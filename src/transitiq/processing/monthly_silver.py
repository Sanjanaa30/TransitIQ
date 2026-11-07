"""Turn one validated MTA monthly-ridership Bronze run into local Silver rows.

Silver stores decimal values as text in JSON Lines so their exact published
precision survives JSON readers that would otherwise use binary floats.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SILVER_ROOT = ROOT / "data" / "silver" / "mta" / "monthly-ridership"
SOURCE_ID = "xfre-bxip"
SERVICE_MAP = {
    "Subway": ("subway", "NYC Subway (published grouping includes SIR)"),
    "SIR": ("sir", "Staten Island Railway"),
    "LIRR": ("lirr", "Long Island Rail Road"),
    "MNR": ("mnr", "Metro-North Railroad"),
}


def transform(bronze_dir: Path) -> Path:
    manifest_path = bronze_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("source_id") != SOURCE_ID:
        raise ValueError("This job accepts only MTA source xfre-bxip")
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or bronze_dir.name != f"run_id={run_id}":
        raise ValueError("Bronze folder and manifest run IDs disagree")

    records = []
    keys = set()
    for page in manifest["pages"]:
        name = page["file"]
        if Path(name).name != name or not name.endswith(".json"):
            raise ValueError("Unsafe Bronze page filename")
        raw = (bronze_dir / name).read_bytes()
        if len(raw) != page["bytes"] or hashlib.sha256(raw).hexdigest() != page["sha256"]:
            raise ValueError(f"Bronze page checksum or size changed: {name}")
        rows = json.loads(raw)
        if not isinstance(rows, list) or len(rows) != page["row_count"]:
            raise ValueError(f"Bronze page row count changed: {name}")
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"month", "agency", "ridership"}:
                raise ValueError("Unexpected monthly source fields")
            agency = row["agency"]
            if agency not in SERVICE_MAP:
                raise ValueError(f"Unknown agency: {agency!r}")
            raw_month = row["month"]
            if not isinstance(raw_month, str):
                raise ValueError("Month must be text in the Bronze response")
            try:
                month = datetime.strptime(raw_month, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError as exc:
                raise ValueError(f"Invalid month: {raw_month!r}") from exc
            if month.day != 1 or month.hour or month.minute or month.second or month.microsecond:
                raise ValueError(f"Month is not a first-of-month label: {raw_month!r}")
            try:
                value = Decimal(str(row["ridership"]))
            except (InvalidOperation, TypeError) as exc:
                raise ValueError(f"Invalid ridership: {row['ridership']!r}") from exc
            if not value.is_finite() or value < 0:
                raise ValueError(f"Missing, negative, or nonfinite ridership: {row['ridership']!r}")
            service_id, service_name = SERVICE_MAP[agency]
            month_start = month.strftime("%Y-%m-%d")
            key = (service_id, month_start)
            if key in keys:
                raise ValueError(f"Duplicate service-month: {key}")
            keys.add(key)
            records.append({
                "month_start": month_start,
                "year": month.year,
                "month_number": month.month,
                "service_id": service_id,
                "service_name": service_name,
                "source_agency": agency,
                "ridership_estimate": str(row["ridership"]),
                "value_state": "published_estimate",
                "source_id": SOURCE_ID,
                "bronze_run_id": run_id,
            })

    if len(records) != manifest["row_count"]:
        raise ValueError("Total Bronze and Silver row counts disagree")
    records.sort(key=lambda r: (r["month_start"], r["service_id"]))
    target = SILVER_ROOT / f"run_id={run_id}"
    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records)
    silver_manifest = {
        "source_id": SOURCE_ID,
        "source_url": manifest["source_url"],
        "source_rows_updated_at_utc": manifest["source_rows_updated_at_utc"],
        "retrieved_at_utc": manifest["retrieved_at_utc"],
        "bronze_run_id": run_id,
        "row_count": len(records),
        "record_file": "records.jsonl",
        "ridership_estimate_type": "decimal encoded as JSON string",
        "value_state": "published_estimate",
        "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }
    manifest_body = json.dumps(silver_manifest, indent=2) + "\n"
    if target.exists():
        if ((target / "records.jsonl").read_text(encoding="utf-8") == body
                and (target / "manifest.json").read_text(encoding="utf-8") == manifest_body):
            return target
        raise FileExistsError(f"Silver run exists with different content: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    work = target.parent / f".partial-{run_id}"
    work.mkdir(exist_ok=False)
    try:
        (work / "records.jsonl").write_text(body, encoding="utf-8")
        (work / "manifest.json").write_text(manifest_body, encoding="utf-8")
        work.rename(target)
    except Exception:
        for item in work.iterdir():
            item.unlink()
        work.rmdir()
        raise
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bronze-run", type=Path, required=True)
    args = parser.parse_args()
    try:
        target = transform(args.bronze_run)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Silver transformation failed: {exc}\n")
    print(f"Silver run: {target}")
    print((target / "manifest.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
