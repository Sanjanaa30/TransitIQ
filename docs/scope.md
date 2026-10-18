# TransitIQ — Project scope

## Status: Phase 0 review

## What are we building?

TransitIQ is a public website for exploring MTA rail service, ridership, disruptions, and fares. We will build it in stages: first the data and dashboard, then forecasting, then the AI assistant.

## Which services will the website cover?

The project covers four services:
1. NYC Subway
2. Staten Island Railway (SIR)
3. Long Island Rail Road (LIRR)
4. Metro-North Railroad

Each service has different public data. A chart or number will appear only when the data supports it.

## What will visitors see?

The completed website will have five tabs:
1. Operations & Disruptions — service problems and reliability
2. Rider & Ridership Explorer — passenger demand and busy periods
3. General Service Overview — a summary of the selected service
4. Fare Intelligence — fare usage for Subway/SIR and a fare calculator for LIRR/Metro-North
5. Ask TransitIQ AI Assistant — answers supported by approved sources

We will build the first four analytics tabs before the AI assistant. Once built, the assistant will also open from the other tabs.

## What years will we study?

- The target period for charts and analysis is 2019 through the latest published data in 2026.
- We will check the actual dates available in each source. Some sources may start later or have gaps. We will show those limits on the website. We will use comparable 2019 data as a pre-pandemic reference, and we will not treat an incomplete 2026 as a full year.
- The AI assistant may use approved historical documents about events before 2019. That history collection has a different time purpose from the dashboard data.

## How will data reach the website?

The first data flow will be:

```
Official public MTA data → Python checks → Azure Data Lake Storage Gen2 → processing and documented metrics → Azure SQL Database → prepared website files → GitHub Pages
```
- Azure Data Factory will coordinate a small initial workflow. We will use Azure SQL Database only if we confirm that its free offer applies to your account.
- The public website will read prepared files. A visitor opening a chart will not start an Azure pipeline or query Azure SQL.

## What must we verify before showing a number?
- Every important number needs a clear meaning, unit, source, and data date. We must know whether it is an observed value, estimate, forecast, missing value, or unsupported value.
- Some planned features need extra proof before we display them. Examples include SIR station demand, estimated passengers affected by a disruption, disruption rates per scheduled trip, affected-station maps, and historical fare calculations. If the necessary data is missing or unclear, we will explain the limit or leave out that feature. Missing does not mean zero.

## What comes after the first dashboard?

After the first public version, we plan to add:
- Azure Databricks, PySpark, and Delta Lake to build and demonstrate the more advanced data pipeline, if account access and cost permit.
- Forecasting using baseline models, scikit-learn, XGBoost, and MLflow.
- Ask TransitIQ using approved MTA data and history documents, with citations, usage limits, and a protected backend.

These are part of the complete project. They do not need to be finished before the first dashboard goes online.

## What are the cost and laptop limits?

Your intended personal spending is $0. Before creating any Azure resource, we will check student credit, service eligibility, spending protection, and possible charges. Upgrading to paid billing requires a separate decision. Project files, Python environments, dependencies, and supported caches will go under `E:\TransitIQ`. We will keep only small data samples locally. We will also check which small Windows or tool files may still use `C:Drive`.

## What decisions are still open?

We still need to verify:
- The best small dataset for the first complete pipeline.
- Which conditional metrics the real data supports.
- Whether your account can use the Azure SQL Database free offer.
- Whether Azure Databricks fits the zero-spending limit.
- The exact hosting and document-search setup for the AI assistant.

We will record each answer or change in docs\decisions.md with its date, reason, and effect on the project. 

The flow in one line: 
```
decide the scope → verify sources → build a small Azure data pipeline → publish trustworthy dashboard data → add advanced processing → add forecasting → add the AI assistant.
```
Record answers and changes in docs/decisions.md.