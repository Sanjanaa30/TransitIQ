# TransitIQ

TransitIQ is a staged portfolio project for exploring public MTA rail
data across NYC Subway, Staten Island Railway, LIRR, and Metro-North.

The planned website has five tabs: Operations & Disruptions, Rider &
Ridership Explorer, General Service Overview, Fare Intelligence, and
Ask TransitIQ AI Assistant.

## Project status

Project foundations are in progress. Data pipelines and the website
will be added in later phases.

## Scope and decisions

- [Project scope](docs/scope.md)
- [Decision log](docs/decisions.md)

## Planned data flow

Official public MTA data -> ingestion and validation -> Azure Data Lake
Storage Gen2 -> processing and documented metrics -> Azure SQL Database
-> prepared website files -> GitHub Pages.

Azure Data Factory will coordinate an initial small workflow. Azure
Databricks, forecasting, and the AI assistant are later phases, subject
to the project checks described in the scope.

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

We will choose and document the first official MTA dataset in Phase 3.

## Run the project

We will add run instructions as we build the data pipeline and website.

## Basic check

Once Python source files exist, check their syntax with:

`& 'E:\TransitIQ\.venv\Scripts\python.exe' -m compileall -q 'E:\TransitIQ\src'`