# TransitIQ

TransitIQ is a staged portfolio project for exploring public MTA rail
data across NYC Subway, Staten Island Railway, LIRR, and Metro-North.

The planned website has five tabs: Operations & Disruptions, Rider &
Ridership Explorer, General Service Overview, Fare Intelligence, and
Ask TransitIQ AI Assistant.

## Project status

**Level 1 foundations and the first Azure ingestion exercises are complete.
Phase 8's parameterized ADF copy landed a checked 20-row sample in ADLS.**

- **Phases 0–2:** Agreed on scope, $0 intended personal spending, and an
  E: workspace; checked the laptop and set up the local environment and Git.
- **Phase 3:** Listed sources by tab and checked small samples. The monthly
  starter has 2019–August 2026 rows for all four services. Other checks
  covered daily/hourly ridership, alerts, reliability, LIRR occupancy,
  selected fares, and station/branch references.
- **Phase 4:** Documented row meanings, relationships, metric formulas,
  missing/estimated values, and Bronze/Silver/Gold roles. The final review
  marks features that still need evidence as conditional or unsupported.

These are design and sample checks. Full historical pipeline validation and
the dashboard have not been built yet.

- **Phase 5:** Verified Azure for Students credit, an allowed region, a budget alert,
  Data Factory V2 availability, and the Azure SQL free-tier offer.
- **Phase 6:** Created the private ADLS Gen2 storage layout and verified an
  identity-based upload and read of a tiny test file.
- **Phase 7:** Built a bounded Python fetch with validation, a source-update
  timestamp, a manifest, and an idempotent ADLS Bronze upload.
- **Phase 8:** Built a manual ADF HTTP-to-ADLS Copy pipeline. A parameterized
  January-May 2019 run succeeded, and all 20 source rows were verified in ADLS.

## Level 1 project documents

- [Confirmed scope and decisions](docs/Level_1_Project_foundations/01_scope_and_decisions.md)
- [Data sources and feature plan by tab](docs/Level_1_Project_foundations/02_data_sources_by_tab.md)
- [Phase 4 metrics and data model](docs/Level_1_Project_foundations/03_metrics_and_data_model.md)
- [Phase 4 final review](docs/Level_1_Project_foundations/04_phase4_final_review.md)

## Level 2 project documents

- [Level 2 Azure ingestion learning guide](docs/Level_2_Azure_ingestion/README.md)
- [ADLS layout and operating rules](docs/Level_2_Azure_ingestion/06_adls_layout.md)
- [First ADF pipeline and verified result](docs/Level_2_Azure_ingestion/08_adf_first_pipeline.md)

## Planned data flow

Official public MTA data -> ingestion and validation -> Azure Data Lake
Storage Gen2 -> processing and documented metrics -> Azure SQL Database (if eligible)
-> prepared website files -> GitHub Pages.

Azure Data Factory has completed a small manual ingestion exercise. Azure SQL
still requires creation under the verified free offer. Azure Databricks,
forecasting, and the AI assistant are later
phases, subject to the project checks described in the scope.

## Folders

- `src/transitiq/`: Python ingestion, processing, and metrics code
- `tests/`: checks for code and data
- `web/`: dashboard website
- `data/samples/`: small approved samples
- `docs/`: project documentation
- `.venv/` and `.cache/`: local environment and caches, excluded from Git

## Local setup

Use Python 3.13, Git, Node.js, and npm. Keep project files in
`E:\TransitIQ`.

From PowerShell:

```powershell
Set-Location -LiteralPath 'E:\TransitIQ'
$env:PIP_CACHE_DIR = 'E:\TransitIQ\.cache\pip'
$env:npm_config_cache = 'E:\TransitIQ\.cache\npm'
$env:TEMP = 'E:\TransitIQ\.cache\tmp'
$env:TMP = 'E:\TransitIQ\.cache\tmp'
& 'E:\TransitIQ\.venv\Scripts\python.exe' --version
```

## Data sources

The first verified source is MTA Monthly Ridership / Traffic Data. Its
2019–August 2026 snapshot has been checked for four rail services. See the
Level 1 source list for links, intended uses, and remaining checks.

## Run the project

The first Phase 7 ingestion fetches January through May 2019 monthly estimates
for Subway, SIR, LIRR, and Metro-North. It uses only the Python standard
library, validates 20 service-month rows, and writes the original API response
and a run manifest under `data/raw/` on E:. The manifest records the publisher's
row update time separately from our retrieval time.

```powershell
& 'E:\TransitIQ\.venv\Scripts\python.exe' 'E:\TransitIQ\src\transitiq\ingestion\monthly_ridership.py' --start-month 2019-01 --end-month 2019-05
```

Add `--upload` to fetch and upload the new run in one command:

```powershell
& 'E:\TransitIQ\.venv\Scripts\python.exe' 'E:\TransitIQ\src\transitiq\ingestion\monthly_ridership.py' --start-month 2019-01 --end-month 2019-05 --upload
```

Each successful fetch receives a new ID and folder. Failed validation does not
publish a completed run. If Azure upload fails, the local run remains available
for retry using the uploader below.

The first end-to-end run on November 1, 2026 validated and uploaded 20 rows
for January–May 2019. The publisher row update time was October 26, 2026;
both timestamps are stored in its manifest. The run ID was
`20261101T162309Z-410100b3`.

To check the Bronze destination without contacting Azure:

```powershell
& 'E:\TransitIQ\.venv\Scripts\python.exe' 'E:\TransitIQ\src\transitiq\ingestion\upload_bronze.py' --latest
```

To upload that run, add `--upload`:

```powershell
& 'E:\TransitIQ\.venv\Scripts\python.exe' 'E:\TransitIQ\src\transitiq\ingestion\upload_bronze.py' --latest --upload
```

The upload opens a browser for the **Azure for Students** sign-in. It uses
Microsoft Entra authentication, not a storage key. It checks each local
response against its manifest checksum, then uploads response files before
the manifest. Repeating the command checks existing remote files and does
not overwrite different content. New uploads use a conditional create and
read back the result. Azure packages are listed in
`requirements-azure.txt`; install them into the E: virtual environment if
setting up a fresh checkout.

## Basic check

Once Python source files exist, check their syntax with:

`& 'E:\TransitIQ\.venv\Scripts\python.exe' -m compileall -q 'E:\TransitIQ\src'`
