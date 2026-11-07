# Phase 8 — First Azure Data Factory pipeline

**Status (November 1, 2026): Confirmed.** A manual, parameterized Copy run landed an official MTA monthly-ridership response in ADLS. The user checked the saved file and found all 20 expected rows.

## What this exercise demonstrates

| Part | Confirmed setup | Role |
| --- | --- | --- |
| Data Factory | `adf-transitiq-dev-3847`, North Central US | Coordinates one manual Copy activity. |
| Public source connection | `ls_mta_public_http`, anonymous HTTPS | Reads the official [MTA monthly ridership API](https://data.ny.gov/d/xfre-bxip). |
| Source dataset | `ds_mta_monthly_jan2019_http`, HTTP Binary | Builds a bounded API URL from `start_month` and `end_month`. |
| Lake connection | `ls_adls_transitiq`, system-assigned managed identity | Uses the factory identity to access ADLS without a storage key. |
| Sink dataset | `ds_adls_bronze_binary`, ADLS Gen2 Binary | Writes the response as `response.json` in the `transitiq` file system. |
| Pipeline | `pl_mta_monthly_jan2019_copy` | Passes month parameters to the source and a unique folder path to the sink. |

The source URL selects `month`, `agency`, and `ridership` for Subway, SIR, LIRR, and MNR. It has a 500-row API limit. The file is copied as raw JSON bytes; ADF does not calculate monthly totals or validate source values in this pilot. The Python Phase 7 process performs the separate validation and writes a manifest.

## Verified flow

```text
MTA public API -> ADF HTTP Binary source -> Copy activity
               -> ADLS Gen2: transitiq/bronze/mta/monthly-ridership/...
```

| Check | Observed result |
| --- | --- |
| First manual pilot | January 2019 response with four rows: LIRR, MNR, SIR, Subway. ADF Monitor showed success. |
| Parameterized test | `start_month=2019-01`, `end_month=2019-05`; ADF Monitor showed success. |
| Saved response | 20 rows: one for each of the four services in every month from January through May 2019. |
| Destination | Private `transitiq` file system, under `bronze/mta/monthly-ridership/source_id=xfre-bxip/ingest_date=2026-11-01/run_id=adf-<pipeline-run-id>/response.json`. |
| Run isolation | The sink folder includes the ADF pipeline run ID, so a new manual run has a separate path. |
| Activity policy | Retry set to 1 and timeout corrected to 10 minutes during setup. |

The first copy attempt failed because the sink tried to use `bronze` as a **file system**. `bronze` is a directory inside the `transitiq` file system. Setting **File system = `transitiq`** and **Directory = the parameterized path beginning with `bronze/`** resolved the permission error; the next run succeeded.

## Meaning and limits

- This proves that ADF can copy a small official source response to the project lake with managed identity, manual execution, and run monitoring.
- The copied monthly values are publisher estimates. The Subway source grouping includes SIR; do not add the separate SIR row to the published Subway total.
- The ADF pilot does not yet create a source-version manifest, apply Silver data quality checks, or schedule automatic runs. The Phase 7 Python ingestion retains that metadata and validation for its own runs.
- Keep runs manual while learning and check Azure credit use after tests. A budget alert warns about spending; it does not stop an ADF run.
