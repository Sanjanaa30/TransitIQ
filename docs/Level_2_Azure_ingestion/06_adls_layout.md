# Phase 6 — ADLS layout and operating rules

**Status (2026-10-31): Confirmed.** Storage account, file system, folders, and a small upload/read test are verified. The naming, metadata, and retention rules below were reviewed by the user and will guide the Phase 7 ingestion code.

## What exists

| Item | Verified setup | Why it is here |
|---|---|---|
| Subscription | Azure for Students | Project credit is used; no intended personal spending. |
| Region | North Central US | Allowed by this subscription's deployment policy. |
| Resource group | `rg-transitiq-dev` | Groups the project resources. |
| Storage account | `transitiqdl20263847` | Standard, locally redundant (LRS), Hot, with hierarchical namespace enabled. |
| File system/container | `transitiq` | Private project data lake. |
| Access | Student account has Storage Blob Data Contributor; account-key and anonymous access are disabled | Identity-based read and write access. |
| Recovery | Blob and container soft delete for 7 days | Short accidental-deletion recovery window; retained data still uses storage. |
| Cost alert | Monthly $5 Azure budget alert | Warning about credit use; it does not stop usage. |
| Test | Tiny text file uploaded to `ops/` and read in the portal | Confirms the student's data-plane read and write access. |

## What each folder means

| Folder | Contents | First use |
|---|---|---|
| `bronze/` | Original bounded responses from official sources, kept exactly as retrieved. | Phase 7 monthly ridership ingestion. |
| `silver/` | Typed and validated records with source labels and quality flags. | First transformation pipeline. |
| `gold/` | Checked measures and small dashboard-ready outputs. | First monthly ridership dashboard example. |
| `quarantine/` | Rejected or ambiguous records with a reason; never silently discarded. | When a validation rule fails. |
| `ops/` | Small run manifests and operational test files. | Phase 6 access test and Phase 7 run tracking. |

These are ordinary ADLS directories. Bronze/Silver/Gold describe data preparation stages; the directories are not Delta Lake tables yet.

## File paths and names

Use lowercase source slugs, the official dataset ID, UTC extraction dates, and a unique run ID. A run ID keeps reruns separate. Do not create one file per source row.

```text
bronze/mta/monthly-ridership/source_id=xfre-bxip/ingest_date=YYYY-MM-DD/run_id=<run-id>/response.json
bronze/mta/monthly-ridership/source_id=xfre-bxip/ingest_date=YYYY-MM-DD/run_id=<run-id>/manifest.json
silver/mta/monthly-ridership/run_id=<run-id>/records.<format>
gold/ridership/monthly/run_id=<run-id>/metrics.<format>
quarantine/mta/monthly-ridership/run_id=<run-id>/rejected.<format>
ops/ingestion-runs/<run-id>.json
```

The `ingest_date` is the **date we collected the extract**, not the month of each ridership row. The source rows retain their own `month` values. The format for Silver and Gold will be chosen when those stages are built. The first source is [MTA Monthly Ridership / Traffic Data](https://data.ny.gov/d/xfre-bxip), which has one published estimate per service-month.

If an extract needs multiple API pages, Bronze keeps each original response as `response-page-0001.json`, `response-page-0002.json`, and so on. The manifest lists each page's row count, size, and checksum.

## Run metadata

For each Bronze extract, store a small `manifest.json` beside the response. It should record: `source_id`, `source_url`, `retrieved_at_utc`, `run_id`, requested date/service filters, HTTP status, response file size, row count, and a SHA-256 checksum. Never put API tokens, account keys, credentials, or personal information in the manifest. If a request fails, the run record should say why and should not claim a successful extract.

## Retention and cost rules

1. Keep the first bounded Bronze extract so the first pipeline can be reproduced. Write new runs to new paths rather than overwriting the original response.
2. Keep only the selected small project extracts in ADLS. Do not download or store every proposed source at once.
3. Keep Silver, Gold, quarantine, and operational files only when they support the current build or an investigated failure. Review their size before adding a lifecycle rule.
4. Use the existing Hot/LRS configuration for the small active dataset. Check credit and budget alerts after uploads or repeated runs.
5. The Phase 6 smoke-test blob may be deleted after review. With 7-day soft delete, deletion does not immediately remove its stored bytes.
6. Publish only approved small samples to Git; do not publish lake extracts or run manifests containing account details.

## Next phase

Phase 6 is complete. Phase 7 will implement these rules for the monthly ridership source and verify that a rerun does not overwrite or duplicate the intended extract.
