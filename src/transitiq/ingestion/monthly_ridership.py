"""Fetch a bounded, original MTA monthly-ridership response for Bronze."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4


SOURCE_ID = "xfre-bxip"
SOURCE_URL = f"https://data.ny.gov/resource/{SOURCE_ID}.json"
SOURCE_METADATA_URL = f"https://data.ny.gov/api/views/{SOURCE_ID}.json"
AGENCIES = ("Subway", "SIR", "LIRR", "MNR")
ROOT = Path(__file__).resolve().parents[3]
BRONZE_ROOT = ROOT / "data" / "raw" / "mta" / "monthly-ridership"
MAX_RESPONSE_BYTES = 2_000_000
MAX_ROWS = 500
PAGE_SIZE = 100


def parse_month(value: str) -> datetime:
    try:
        month = datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise ValueError("Months must use YYYY-MM, for example 2019-01") from exc
    return month


def month_range(start: datetime, end: datetime) -> list[str]:
    if end < start:
        raise ValueError("End month must be on or after start month")
    months = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        months.append(f"{year:04d}-{month:02d}")
        if len(months) > 12:
            raise ValueError("This first ingestion allows at most 12 months per run")
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return months


def next_month(month: datetime) -> str:
    year = month.year + (month.month == 12)
    number = 1 if month.month == 12 else month.month + 1
    return f"{year:04d}-{number:02d}-01T00:00:00"


def fetch_page(url: str) -> tuple[bytes, int]:
    request = Request(url, headers={"User-Agent": "TransitIQ portfolio ingestion/0.1"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=20) as response:
                body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ValueError("API page exceeded the 2 MB safety limit")
                return body, response.status
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"MTA API returned HTTP {exc.code}") from exc
        except (URLError, TimeoutError) as exc:
            if attempt == 2:
                raise RuntimeError(f"Could not reach MTA API: {exc}") from exc
        time.sleep(2**attempt)
    raise AssertionError("Retry loop ended unexpectedly")


def validate_rows(rows: list[object], allowed_months: set[str], seen: set[tuple[str, str]]) -> None:
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"month", "agency", "ridership"}:
            raise ValueError("A source row does not have exactly month, agency, ridership")
        month = row["month"]
        agency = row["agency"]
        ridership = row["ridership"]
        if not isinstance(month, str) or len(month) < 10 or month[:7] not in allowed_months:
            raise ValueError(f"Unexpected source month: {month!r}")
        if month[7:] != "-01T00:00:00.000":
            raise ValueError(f"Source month is not a first-of-month label: {month!r}")
        if agency not in AGENCIES:
            raise ValueError(f"Unexpected agency: {agency!r}")
        try:
            count = Decimal(str(ridership))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid ridership for {agency} {month}") from exc
        if not count.is_finite() or count < 0:
            raise ValueError(f"Missing, negative, or nonfinite ridership for {agency} {month}")
        key = (agency, month[:7])
        if key in seen:
            raise ValueError(f"Duplicate agency-month: {key}")
        seen.add(key)


def source_update_time() -> str:
    body, _ = fetch_page(SOURCE_METADATA_URL)
    try:
        metadata = json.loads(body)
        timestamp = metadata["rowsUpdatedAt"]
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            raise ValueError("Publisher update timestamp is not an integer")
        return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    except (KeyError, TypeError, OverflowError, json.JSONDecodeError) as exc:
        raise ValueError("Could not read the publisher's row update timestamp") from exc


def ingest(start: datetime, end: datetime) -> Path:
    months = month_range(start, end)
    retrieved_at = datetime.now(timezone.utc)
    run_id = retrieved_at.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    target = BRONZE_ROOT / f"source_id={SOURCE_ID}" / f"ingest_date={retrieved_at:%Y-%m-%d}" / f"run_id={run_id}"
    target.parent.mkdir(parents=True, exist_ok=True)

    where = (
        f"month >= '{start:%Y-%m}-01T00:00:00' "
        f"AND month < '{next_month(end)}' "
        "AND agency in ('Subway','SIR','LIRR','MNR')"
    )
    seen: set[tuple[str, str]] = set()
    pages: list[dict[str, object]] = []
    raw_pages: list[bytes] = []
    offset = 0
    while True:
        query = urlencode({
            "$select": "month,agency,ridership",
            "$where": where,
            "$order": "month ASC,agency ASC",
            "$limit": PAGE_SIZE,
            "$offset": offset,
        })
        url = f"{SOURCE_URL}?{query}"
        body, status = fetch_page(url)
        try:
            rows = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("MTA API returned invalid JSON") from exc
        if not isinstance(rows, list):
            raise ValueError("MTA API returned something other than a row array")
        validate_rows(rows, set(months), seen)
        if len(seen) > MAX_ROWS:
            raise ValueError("Extract exceeded the 500-row safety limit")
        raw_pages.append(body)
        pages.append({"page": len(pages) + 1, "http_status": status, "row_count": len(rows)})
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    expected = {(agency, month) for agency in AGENCIES for month in months}
    if seen != expected:
        missing = sorted(expected - seen)
        raise ValueError(f"Source extract is incomplete; missing {missing[:5]}")

    publisher_updated_at = source_update_time()

    work = target.parent / f".partial-{run_id}"
    work.mkdir()
    for number, body in enumerate(raw_pages, start=1):
        filename = "response.json" if len(raw_pages) == 1 else f"response-page-{number:04d}.json"
        (work / filename).write_bytes(body)
        pages[number - 1]["file"] = filename
        pages[number - 1]["bytes"] = len(body)
        pages[number - 1]["sha256"] = hashlib.sha256(body).hexdigest()
    manifest = {
        "source_id": SOURCE_ID,
        "source_url": SOURCE_URL,
        "source_metadata_url": SOURCE_METADATA_URL,
        "source_rows_updated_at_utc": publisher_updated_at,
        "retrieved_at_utc": retrieved_at.isoformat(),
        "run_id": run_id,
        "requested_start_month": months[0],
        "requested_end_month": months[-1],
        "agencies": list(AGENCIES),
        "row_count": len(seen),
        "pages": pages,
        "measure_note": "Published monthly estimates; Subway grouping includes SIR.",
    }
    (work / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    work.rename(target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-month", default="2019-01")
    parser.add_argument("--end-month", default="2019-05")
    parser.add_argument("--upload", action="store_true", help="Upload the completed run to ADLS Bronze")
    args = parser.parse_args()
    try:
        target = ingest(parse_month(args.start_month), parse_month(args.end_month))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"Ingestion failed: {exc}\n")
    print(f"Validated Bronze extract: {target}")
    print((target / "manifest.json").read_text(encoding="utf-8"))
    if args.upload:
        from upload_bronze import upload_run

        try:
            upload_run(target)
        except Exception as exc:
            parser.exit(1, f"Local extract is saved, but Azure upload failed: {exc}\n")


if __name__ == "__main__":
    main()
