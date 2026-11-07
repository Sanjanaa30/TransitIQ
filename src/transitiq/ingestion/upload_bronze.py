"""Upload one validated local monthly-ridership run to ADLS Bronze."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BRONZE_ROOT = ROOT / "data" / "raw" / "mta" / "monthly-ridership"
DEFAULT_ACCOUNT = "transitiqdl20263847"
DEFAULT_FILE_SYSTEM = "transitiq"
MAX_TOTAL_BYTES = 2_000_000


def latest_run() -> Path:
    candidates = sorted(BRONZE_ROOT.glob("source_id=xfre-bxip/ingest_date=*/run_id=*/manifest.json"))
    if not candidates:
        raise ValueError("No completed local Bronze run found; run monthly_ridership.py first")
    return candidates[-1].parent


def read_run(run_folder: Path) -> tuple[dict, list[tuple[str, bytes]]]:
    folder = run_folder.resolve(strict=True)
    if not folder.is_relative_to(BRONZE_ROOT.resolve(strict=True)):
        raise ValueError("Run folder must be inside E:\\TransitIQ\\data\\raw\\mta\\monthly-ridership")
    if not folder.name.startswith("run_id=") or not folder.parent.name.startswith("ingest_date="):
        raise ValueError("Run folder does not match the confirmed Bronze layout")
    manifest_bytes = (folder / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("source_id") != "xfre-bxip" or manifest.get("run_id") != folder.name.removeprefix("run_id="):
        raise ValueError("Manifest source ID or run ID does not match its folder")
    if manifest.get("retrieved_at_utc", "")[:10] != folder.parent.name.removeprefix("ingest_date="):
        raise ValueError("Manifest UTC ingestion date does not match its folder")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("Manifest has no response pages")
    files: list[tuple[str, bytes]] = []
    total_bytes = 0
    total_rows = 0
    seen_names: set[str] = set()
    for page in pages:
        name = page.get("file") if isinstance(page, dict) else None
        if not isinstance(name, str) or not (name == "response.json" or name.startswith("response-page-")):
            raise ValueError("Manifest has an unexpected response filename")
        if name in seen_names or Path(name).name != name or not name.endswith(".json"):
            raise ValueError("Manifest has a duplicate or unsafe response filename")
        seen_names.add(name)
        body = (folder / name).read_bytes()
        if len(body) != page.get("bytes") or hashlib.sha256(body).hexdigest() != page.get("sha256"):
            raise ValueError(f"Local response does not match its checksum: {name}")
        if page.get("http_status") != 200 or not isinstance(page.get("row_count"), int):
            raise ValueError(f"Manifest records an unsuccessful or invalid response: {name}")
        total_rows += page["row_count"]
        total_bytes += len(body)
        files.append((name, body))
    if total_rows != manifest.get("row_count") or total_bytes > MAX_TOTAL_BYTES:
        raise ValueError("Run row count or 2 MB upload limit failed")
    files.append(("manifest.json", manifest_bytes))
    return manifest, files


def upload(account: str, file_system: str, remote_dir: str, files: list[tuple[str, bytes]]) -> None:
    from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
    from azure.identity import InteractiveBrowserCredential
    from azure.storage.filedatalake import DataLakeServiceClient

    # No storage account key or connection string is used. The token stays in memory.
    with InteractiveBrowserCredential() as credential:
        service = DataLakeServiceClient(
            account_url=f"https://{account}.dfs.core.windows.net",
            credential=credential,
        )
        file_system_client = service.get_file_system_client(file_system)
        segments = remote_dir.split("/")
        for index in range(1, len(segments) + 1):
            directory = file_system_client.get_directory_client("/".join(segments[:index]))
            try:
                directory.create_directory()
            except ResourceExistsError:
                pass
        for name, body in files:
            remote_file = file_system_client.get_file_client(f"{remote_dir}/{name}")
            try:
                existing = remote_file.download_file().readall()
            except ResourceNotFoundError:
                existing = None
            if existing is not None:
                if existing != body:
                    raise ValueError(f"Remote file differs; upload stopped: {name}")
                print(f"Already present and identical: {name}")
                continue
            # ADLS upload_data(overwrite=False) appends to an existing file.
            # Create only when absent, then read back the exact bytes.
            remote_file.upload_data(body, overwrite=True, if_none_match="*")
            if remote_file.download_file().readall() != body:
                raise ValueError(f"Remote verification failed: {name}")
            print(f"Uploaded: {name} ({len(body)} bytes)")


def upload_run(folder: Path, account: str = DEFAULT_ACCOUNT, file_system: str = DEFAULT_FILE_SYSTEM) -> None:
    manifest, files = read_run(folder)
    relative = folder.resolve().relative_to(BRONZE_ROOT.resolve())
    remote_dir = f"bronze/mta/monthly-ridership/{relative.as_posix()}"
    print(f"Local run: {folder.resolve()}")
    print(f"Validated rows: {manifest['row_count']}")
    print(f"ADLS destination: {file_system}@{account}/{remote_dir}")
    print("Files: " + ", ".join(name for name, _ in files))
    upload(account, file_system, remote_dir, files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--latest", action="store_true", help="Use the newest completed local run")
    choice.add_argument("--run-folder", type=Path, help="Use this exact local run folder")
    parser.add_argument("--upload", action="store_true", help="Open a student sign-in and upload to Azure")
    parser.add_argument("--account", default=DEFAULT_ACCOUNT)
    parser.add_argument("--file-system", default=DEFAULT_FILE_SYSTEM)
    args = parser.parse_args()
    try:
        folder = latest_run() if args.latest else args.run_folder
        if args.upload:
            upload_run(folder, args.account, args.file_system)
        else:
            manifest, files = read_run(folder)
            relative = folder.resolve().relative_to(BRONZE_ROOT.resolve())
            remote_dir = f"bronze/mta/monthly-ridership/{relative.as_posix()}"
            print(f"Local run: {folder.resolve()}")
            print(f"Validated rows: {manifest['row_count']}")
            print(f"ADLS destination: {args.file_system}@{args.account}/{remote_dir}")
            print("Files: " + ", ".join(name for name, _ in files))
            print("Dry run only. Add --upload to sign in and write to ADLS.")
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Bronze upload stopped: {exc}\n")


if __name__ == "__main__":
    main()
