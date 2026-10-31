# TransitIQ — Level 1 project scope and decisions

**Status (2026-10-31):** Phases 0–2 are set up, Phase 3 has a source catalog and small source checks, and the [Phase 4 design review](04_phase4_final_review.md) is ready for user sign-off. This file records agreed scope and decisions. A planned feature is not a completed feature.

## 1. What we are building

TransitIQ is a public portfolio website about MTA rail service. We will build a trustworthy data pipeline and dashboard first, then add forecasting, then an evidence-based AI assistant.

The four services are **NYC Subway**, **Staten Island Railway (SIR)**, **Long Island Rail Road (LIRR)** and **Metro-North Railroad**. They do not all publish the same measurements, so a feature appears for a service only when its source and calculation are verified.

| Website tab | What a visitor will use it for | Delivery decision |
| --- | --- | --- |
| 1. Operations & Disruptions | Explore service alerts, disruptions and reliability | First dashboard, with conditional metrics hidden until verified |
| 2. Rider & Ridership Explorer | Explore demand, busy periods and supported train occupancy | First dashboard; forecasting added later |
| 3. General Service Overview | See one service's main ridership, network and reliability measures together | First dashboard; reuse checked metrics from Tabs 1 and 2 |
| 4. Fare Intelligence | Explore Subway/SIR fare **entries** or calculate selected current railroad fares | First dashboard; show only verified fare rules and coverage |
| 5. Ask TransitIQ AI Assistant | Ask cited questions about MTA history, dashboard data and forecasts | Later AI phase; accessible from other tabs when built |

## 2. What the first version includes

The first version will ingest **small, selected official public MTA data**, check it, document each metric, and publish the four analytics tabs. The website will read **prepared data files** on GitHub Pages. Opening a chart will not start a paid data-processing job or query Azure SQL.

The agreed data engineering plan is:

```text
Official MTA source → bounded Python ingestion and validation
→ Azure Data Lake Storage Gen2 → documented processing and Gold metrics
→ Azure SQL Database, only if its free offer applies
→ prepared website files → GitHub Pages
```

Azure Data Factory is planned to coordinate a **small initial workflow**, after account, eligibility and cost checks. These are architecture decisions, **not claims that Azure resources have already been created**. A Bronze/Silver/Gold design starts with clear raw, cleaned and presentation data responsibilities. Azure Databricks, PySpark and Delta Lake come later if access and the zero-spending constraint allow them.

| Part of the agreed stack | Planned tool and role |
| --- | --- |
| Data collection and checks | Python for bounded API requests, validation and small samples |
| Azure practice | ADLS Gen2 storage, a small Azure Data Factory workflow, and curated Azure SQL tables **only if the account's free offer is confirmed** |
| Dashboard | React, TypeScript and Vite; Tailwind CSS for styling; Apache ECharts for charts |
| Public data and hosting | Prepared JSON files on GitHub Pages, with GitHub Actions for lightweight checks and deployment |
| Later advanced processing | Azure Databricks, PySpark and Delta Lake if access and cost checks pass |
| Later forecasting and AI | scikit-learn, XGBoost and MLflow; then an assistant backed by approved documents and validated project outputs |

## 3. What waits for evidence or a later phase

| Category | Agreed rule |
| --- | --- |
| Conditional dashboard features | SIR station-level demand, distinct alert-derived incidents, disruption cause/duration, affected-station maps, passenger-demand exposure, rates per scheduled trip, fare-ticket recommendations and historical fare prices appear only after their data and method are checked. |
| Later forecasting | Start with a supported Subway station-complex entry forecast using baseline methods, scikit-learn, XGBoost and MLflow. Evaluate with time-ordered data and label forecasts as forecasts. The checked hourly source measures only two SIR fare-control locations, so a forecast for every SIR station is unsupported by that source. |
| Later AI | Use individually approved MTA/Transit Museum history documents, validated Gold metrics and model outputs. Answers cite sources and dates, disclose gaps, and obey usage limits. Do not send personal information, secrets, credentials or internal MTA data to a model. |

An unsupported feature is hidden or clearly explained. **Missing is never shown as zero.** Subway, SIR, LIRR and Metro-North metrics are not ranked against each other when their definitions differ.

**Counting and normalization rule:** before showing a total, rate or percentage, define what one source row represents, what is being counted, the eligible observations, and the denominator. Use the same service, time period and geography on both sides of a comparison. There is **no single normalization factor** that works for every source: an alert update, a distinct incident, a train trip, a station entry and an onboard passenger load are different units.

## 4. Which dates we analyze

The **target analytical period** is **2019 through the latest data published in 2026**, with 2019 used as a pre-pandemic comparison when the measures match. Each source has its own actual start, end and refresh date. An incomplete 2026 period must be compared with the **same months** of another year, not a full year.

The AI history collection may include approved documents about events **before 2019**. Historical documents have a different purpose from the dashboard's numerical time series.

Our **first verified starter source** is [MTA Monthly Ridership / Traffic Data](https://data.ny.gov/d/xfre-bxip). For the four selected service labels, the user checked **January 2019–August 2026**: 12 months in each full year 2019–2025, eight months in 2026, **368 service-month rows**, no missing months, and zero blank, nonnumeric or negative ridership values. This verifies the checked source snapshot, not future revisions. Some published estimates have decimals and must retain their precision. The source's Subway grouping includes SIR; we will not add a separate SIR row to that Subway total. Later small checks also examined daily ridership, hourly ridership and service alerts; their limits are recorded in the [source list](02_data_sources_by_tab.md) and [Phase 4 model](03_metrics_and_data_model.md).

## 5. Cost and computer boundaries

| Constraint | Confirmed decision or observation |
| --- | --- |
| Personal spending | **$0 intended.** Check student credit, service eligibility, spending protection and possible charges before creating Azure resources. A paid upgrade requires a separate decision. |
| Local storage | Keep project files, Python environment, dependencies and supported caches under `E:\TransitIQ`. Keep only small approved samples locally; do not download entire 2019–2026 source datasets. |
| Laptop check | Phase 1 found **82.4 GB free on E:**, **43.8 GB free on C:** and **7.7 GB RAM**. Python 3.13.3, Git, VS Code, Node.js and npm were already installed. Windows and installed tools can still use some C: space for their own settings or temporary files. |
| Workspace check | `E:\TransitIQ\.venv` exists. Project folders, README, ignore rules, a configuration template and E: cache folders exist. The local Git repository has an `origin` remote; this check does not establish whether the GitHub repository is public. |

## 6. Decisions confirmed so far

These entries combine the former decision log with decisions verified after Phase 0. “Confirmed” means the plan or observation is agreed; it does **not** mean every future feature is implemented.

| Date | Decision | Why | Effect |
| --- | --- | --- | --- |
| 2026-10-18 | Cover four rail services and the five tabs above, building four analytics tabs before forecasting and AI | The project can be delivered in understandable stages | Later features do not block the first dashboard |
| 2026-10-18 | Target 2019–latest published 2026 for analytics; permit earlier approved documents for AI history | 2019 is the intended pre-pandemic reference | Show actual source dates and match periods in comparisons |
| 2026-10-18 | Keep intended personal spending at $0 and project work on E: | Budget and disk-space constraints | Check Azure eligibility/cost before provisioning; use small local samples |
| 2026-10-18 | Reuse installed Python, Git, VS Code, Node.js and npm; use an E: virtual environment and supported caches | Phase 1 inspection found usable tools | Local project setup is ready without new tool installation |
| 2026-10-18 | Use [monthly ridership `xfre-bxip`](https://data.ny.gov/d/xfre-bxip) as the first complete pipeline source | It has a clear service-month grain and small size | First pipeline can demonstrate ingestion, checks, metrics and published data |
| 2026-10-18 | Treat monthly data through **August 2026** as the verified snapshot for the four service labels | The user checked samples, every month and all 368 numeric values | The 2019–August 2026 monthly span can be used as the starter, subject to refresh/revision checks |
| 2026-10-18 | Use source-specific counting and denominators for every metric | The available sources measure different things and have different coverage | Phase 4 must define numerator, denominator, unit and eligible row count before a chart is published |
| 2026-10-31 | Treat blank daily ridership as missing and report the count of usable days | The checked daily source has blank values, including 33 SIR rows and one Subway row | Daily averages and busiest-day claims must state their observed-day coverage |
| 2026-10-31 | Limit SIR hourly station claims to measured fare-control locations | The checked April 2019, 2025 and 2026 hourly samples showed St George and Tompkinsville only | Do not claim all SIR stations are ranked or forecast from this source |
| 2026-10-31 | Keep alert records, modern events and legacy alert threads as separate counts | One modern event had 15 revisions; one legacy `status_id` had 13 different-content rows sharing a timestamp | Distinct disruptions, cause and duration stay conditional; do not count raw rows as incidents |
| 2026-10-31 | Include [Subway Customer Journey-Focused Metrics](https://data.ny.gov/d/r7qk-6tcy) in the selected reliability family | The user requested the rider-focused measure alongside on-time performance | Check it in Phase 4 and present its estimated passenger measures separately from train-terminal OTP; Wait Assessment still needs its own source |
| 2026-10-31 | Withhold unresolved August 2026 Metro-North Service Reliability values | The source has two conflicting East rows and two conflicting West rows for that month | Do not select, sum or average them for a dashboard until provenance establishes an authoritative value |
| 2026-10-31 | Use a separate entry-analysis peak for Subway and measured SIR fare entries: weekdays 7–10 a.m. and 4–7 p.m.; weekends 10 a.m.–6 p.m. | The hourly source has local payment hours but no published peak label; these clock windows follow MTA Subway Wait Assessment and were accepted by the user | Label the result as our analysis window; preserve each source's own OTP, customer-journey and railroad fare peak rules. No added paid service or local storage is required |

## 7. Level 1 progress and the next boundary

| Phase | What has been done |
| --- | --- |
| Phase 0 — boundaries | Services, tabs, stages, dates, trust rules, $0 spending intention and E: plan agreed |
| Phase 1 — laptop | Disk space, RAM, installed tools and cache locations inspected |
| Phase 2 — workspace | E: folders and virtual environment, Git repository, remote, README, ignore rules and configuration template created |
| Phase 3 — sources | Candidate sources and gaps mapped by tab. Monthly starter checked; small daily, hourly, alert, reliability and occupancy samples checked. Selected railroad fare tables, policy rules and station zones checked. Current station/branch references and calendar field meanings received initial checks; full source coverage remains to be tested during pipeline construction |
| Phase 4 — metrics and model | The [final design review](04_phase4_final_review.md) covers all four analytics tabs and is **awaiting user sign-off**. Monthly/daily/hourly, alerts, reliability, occupancy, selected fares and reference rules are documented. Conditional cards are gated; source-wide quality, some reliability units and clock-change behavior still need pipeline validation |

The [Phase 4 final review](04_phase4_final_review.md) is the decision point for this level. Data checks completed so far support modeling decisions; they are not a built pipeline or finished website. Source behavior on clock-change dates, full-network counts, Azure SQL free eligibility, Azure Data Factory/Databricks cost, conditional metrics and the AI hosting design still require their scheduled checks. Record any later change as **date → decision → reason → effect on scope or cost**.
