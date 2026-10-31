# TransitIQ

TransitIQ is a staged portfolio project for exploring public MTA rail
data across NYC Subway, Staten Island Railway, LIRR, and Metro-North.

The planned website has five tabs: Operations & Disruptions, Rider &
Ridership Explorer, General Service Overview, Fare Intelligence, and
Ask TransitIQ AI Assistant.

## Project status

**Level 1 foundations are documented; the Phase 4 design review awaits
your confirmation.**

- **Phases 0–2:** Agreed on scope, $0 intended personal spending, and an
  E: workspace; checked the laptop and set up the local environment and Git.
- **Phase 3:** Listed sources by tab and checked small samples. The monthly
  starter has 2019–August 2026 rows for all four services. Other checks
  covered daily/hourly ridership, alerts, reliability, LIRR occupancy,
  selected fares, and station/branch references.
- **Phase 4:** Documented row meanings, relationships, metric formulas,
  missing/estimated values, and Bronze/Silver/Gold roles. The final review
  marks features that still need evidence as conditional or unsupported.

These are design and sample checks. Full-data pipeline validation and the
dashboard have not been built yet.

## Level 1 project documents

- [Confirmed scope and decisions](docs/Level_1_Project_foundations/01_scope_and_decisions.md)
- [Data sources and feature plan by tab](docs/Level_1_Project_foundations/02_data_sources_by_tab.md)
- [Phase 4 metrics and data model](docs/Level_1_Project_foundations/03_metrics_and_data_model.md)
- [Phase 4 final review](docs/Level_1_Project_foundations/04_phase4_final_review.md)

## Planned data flow

Official public MTA data -> ingestion and validation -> Azure Data Lake
Storage Gen2 -> processing and documented metrics -> Azure SQL Database (if eligible)
-> prepared website files -> GitHub Pages.

Azure Data Factory will coordinate an initial small workflow. Azure
SQL and Azure Data Factory require account/eligibility and cost checks
before use. Azure Databricks, forecasting, and the AI assistant are later
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

We will add run instructions as we build the data pipeline and website.

## Basic check

Once Python source files exist, check their syntax with:

`& 'E:\TransitIQ\.venv\Scripts\python.exe' -m compileall -q 'E:\TransitIQ\src'`
