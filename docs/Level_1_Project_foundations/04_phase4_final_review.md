# TransitIQ — Phase 4 final review

**Status (2026-10-31): Ready for the user's design review.** This reviews definitions and source fit. It does not claim that the pipelines or dashboard metrics have passed full-data validation.

Read this in order: [01 — scope and decisions](01_scope_and_decisions.md) says what we agreed to build; [02 — sources by tab](02_data_sources_by_tab.md) identifies the source for each feature; [03 — metrics and data model](03_metrics_and_data_model.md) defines row grains, relationships, calculations and safeguards. This file checks whether those definitions support the first four analytics tabs.

## 1. Phase 4 completion checklist

| Subphase | Review finding | Design status |
| --- | --- | --- |
| 4.1 — One-row meaning | Monthly service-month, daily mode-day, hourly mode-complex-hour-payment-fare, alert update/thread/event candidates, published OTP groups, LIRR trip/stop occupancy, fare-table entries, and current station/branch records are described in 03. | **Defined for selected sources.** Candidate keys and full-period coverage still need pipeline checks. |
| 4.2 — References | Service labels, physical station versus complex, railroad `(railroad, code)`, branch crosswalk need, and month/day/local-hour rules are described. | **Defined with coverage limits.** Current Metro-North station reference omits West-of-Hudson stations; passenger-branch count remains conditional. |
| 4.3 — Events and revisions | Modern `(agency, event_id)` with revisions and legacy `(agency, status_id)` alert threads have separate relationships. | **Modelled as candidates.** Neither source yet supports an unconditional 2019–2026 distinct-disruption series. |
| 4.4 — Formulas and denominators | Monthly growth/recovery, observed-day averages, hourly entry shares, service-specific OTP, occupancy and checked fare lookups have calculation rules. Other metrics are explicitly conditional or unsupported below. | **Defined for initial metrics; gates recorded for the rest.** |
| 4.5 — Value states | Published estimate, actual zero, missing, later forecast, possible projection and unsupported are distinct. Estimated LIRR stop loads have their own quality state. | **Defined.** Never replace missing with zero or label a forecast as observed. |
| 4.6 — Bronze/Silver/Gold | Each selected family has raw preservation, checked/typed transformation and publishable-output responsibilities in 03. | **Designed.** Delta Lake and Databricks remain later implementation choices. |

**Review conclusion:** Phase 4 has a workable *design* for the first dashboard if the conditional and unsupported features below are hidden or labelled exactly as stated. Source validation during ingestion is still required before any metric is published. The user has not yet signed off this final review.

## 2. Tab 1 — Operations & Disruptions

| Planned output | Phase 4 decision | What can appear in the first dashboard |
| --- | --- | --- |
| Alert/disruption trend and total | An alert row is an update, not a disruption. Modern event IDs and legacy thread IDs need wider grouping checks. The 2019/2020 source change must be shown rather than silently merged. | **Alert records/updates**, labelled with source and date coverage. **Total Disruptions** waits for validated distinct events. |
| Planned versus unplanned, cause, average/longest duration, peak-hour disruptions | Status text can change within an event; cause is not yet a verified structured field; the last observed update need not be resolution. Peak overlap also needs a trusted event interval. | **Conditional; hide** these cards and breakdowns until classification and start/end rules pass reviewed examples. |
| Most affected line/branch and affected-station map | One event can affect several lines. Alert-to-route and station-to-map joins require validation and a documented counting rule. | **Conditional.** Never sum line counts and call them distinct service events. |
| Current reliability/OTP, best/worst line, reliability trend | Use each service's published OTP at its own line/territory and month grain. Subway terminal OTP differs from rider-journey performance; Metro-North has territory totals, not a checked whole-network total. | **Initial candidate after source quality checks.** Label it **latest published** month and exact measure, not live status or a cross-service score. |
| Estimated passengers affected, normalized disruption rate, weather association | The selected sources do not yet provide a verified affected-passenger measure, matched historical scheduled-trip denominator or matched weather analysis. | **Conditional/optional; hide** until their numerator, denominator, geography and time alignment are validated. |

SIR has no verified separate alert label in the checked samples. Missing SIR alert evidence is **not** zero SIR disruptions. Tab 1 can still show the separately published SIR OTP trend.

## 3. Tab 2 — Rider & Ridership Explorer

| Planned output | Phase 4 decision | What can appear in the first dashboard |
| --- | --- | --- |
| Total ridership, year-over-year growth, 2019 recovery and monthly trend | Use the **monthly published estimate** for complete-month selections. Compare the same months and service scope; the published Subway grouping includes SIR. | **Defined; validate refreshed source before publication.** Label Subway scope; never add its total to the separate SIR estimate. |
| Arbitrary-date total, average daily, busiest day, weekday/weekend trend and weekend share | Use **daily estimates** from March 2020 onward. Divide by eligible non-null days and show coverage. A partial-date total is labelled `Estimated ridership over observed days`, not the published monthly total. | **Initial candidate after quality checks.** SIR comparisons including its 32 older blank weekend days remain conditional or use a stated complete-date subset. |
| Peak share, busiest hour, busiest station, latest station demand | The hourly source measures estimated fare entries at **station complexes**, not unique passengers or line boardings. Peak share uses the confirmed entry-analysis clock windows and the same observed-hour denominator. | **Initial candidate for measured Subway complexes.** SIR views must say **St George/Tompkinsville fare-control locations only**; no all-SIR station ranking. Say **latest published**, never live count. |
| LIRR highest-occupancy trip/stop, maximum rate and trips over 80% | Trip maxima and onboard stop loads have different grains. Rank only supported measured trips/stops and separate fully reported, estimated and unavailable loads. | **Initial candidate after key/coverage/quality checks.** A crowded onboard stop is not a high-boarding station. Stop-level history begins 2024; trip-level begins July 2022. |
| Metro-North peak/off-peak ridership, LIRR peak/off-peak system ridership | Selected monthly/daily railroad ridership lacks hour or an eligible peak split. OTP and LIRR onboard occupancy cannot supply a system ridership split. | **Unsupported by selected sources; hide.** Calendar weekday/weekend ridership is available from daily data. |
| Unusual demand changes and 1–3-hour forecasts | An anomaly threshold and evaluation rule are not yet defined; forecasting belongs to the later ML phase. | **Not in first dashboard.** Later ML begins with supported Subway complex-hour entries; SIR-wide forecasts are unsupported. |

## 4. Tab 3 — General Service Overview

| Planned card or highlight | Phase 4 decision | What can appear in the first dashboard |
| --- | --- | --- |
| Total, average daily, year-over-year growth, recovery versus 2019 | Reuse Tab 2's exact source, time grain, unit and coverage rule. | **Initial candidates.** A 2026 comparison uses matching 2019 months, never full-year 2019 against partial-year 2026. |
| Number of stations and network map | Current reference gives **472 distinct Subway station IDs** and **21 SIR station IDs**. LIRR has **126 listed station codes**; the **112 Metro-North codes omit West-of-Hudson** stations. | Show only a **reference-date-labelled, accurately scoped** count/map. Do not label 112 a complete Metro-North network total. |
| Number of lines/branches | Station `branch` labels and the 20 rail-map records include non-passenger groupings; their codes do not directly match every metric source. | **Conditional; hide** the networkwide count until each service's passenger-line definition and crosswalk are approved. |
| Latest reliability, reliability trend and line/branch highlights | Reuse Tab 1's service-specific official measure and reporting month. Metro-North East/West territory rows are separate; the selected source lacks a checked 2019 Metro-North OTP baseline. | **Initial candidates after source checks**, with explicit service/territory and measure labels. |
| Total disruptions | Reuse Tab 1's event rule. | **Conditional.** If grouping fails, show a separately labelled alert-record count instead. |
| Subway busiest line and Wait Assessment; SIR-wide busiest station and Mean Distance Between Failures | Complex entries cannot identify a busiest line; Wait Assessment and SIR failure-distance have no selected source; checked SIR entries cover two locations only. | **Unsupported by selected sources; hide** these highlights. Subway Customer Journey Time Performance is a separate selected metric. |
| LIRR occupancy and Metro-North late-train highlights | LIRR trip/stop coverage and load quality must be shown. Metro-North trains over 15 minutes late are countable where a unique territory-month exists; August 2026 has conflicting values. The average-delay field's unit is unverified. | **Conditional.** Hide August 2026 Metro-North reliability values and average-delay card until resolved. |

## 5. Tab 4 — Fare Intelligence

| Planned output | Phase 4 decision | What can appear in the first dashboard |
| --- | --- | --- |
| Subway/SIR total fare entries, OMNY and MetroCard, adoption rate, fare-category shares, top entry location | Sum eligible hourly `ridership` estimates at measured complexes; transfers are already included. OMNY share uses OMNY ÷ (OMNY + MetroCard) within the same dates/mode/locations. Category labels must be checked across releases. | **Initial candidate for Subway; measured-location-only candidate for SIR.** Label entries as estimated, not unique riders or fare revenue. Hide categories not supported for a selected service/date. |
| Current LIRR/Metro-North station-pair fare, peak/off-peak one-way, premium, weekly/monthly and zone | Use a checked station-zone pair, applicable official table section and ticket rule. Peak premium is subtraction only when both fares apply; an intermediate one-way fare may have no peak premium. | **Only checked station pairs and ticket types** may appear. A missing printed effective date remains missing; show source/access date. West-of-Hudson pairs remain conditional. |
| Break-even trips and recommended ticket | Requires dated trip frequency, mixed peak/off-peak prices, validity period, eligibility, discounts and exceptions. | **Conditional; hide** until those assumptions and rules are tested. |
| Historical 2019–2026 fare lookup | A current table does not establish historical prices. | **Not in first dashboard.** Hide the analytics year/date filter on the current fare calculator; show its own fare-table version. |

## 6. Filter and normalization rules shared by the tabs

| Source grain | Filters it can support | Filters it cannot create |
| --- | --- | --- |
| Monthly service estimate | Service, complete month, year | Day, weekday/weekend, hour, station, peak share |
| Daily mode estimate | Service, travel date, weekday/weekend | Hour, station, peak share |
| Hourly complex entry | Subway or measured SIR mode, date/hour, confirmed entry-analysis period, measured complex, payment/fare category | Unique passengers, line boardings, all SIR stations, live count |
| Published OTP or journey metric | Its published month, line/branch/territory and source period | Arbitrary day/hour or a different source's period definition |
| LIRR occupancy | Supported trip, stop, branch, service date and scheduled time where validated | Station boardings or systemwide peak ridership |
| Current railroad fare table | Covered railroad, origin/destination, zone, ticket type and applicable current fare version | Automatic historical price from a 2019–2026 dashboard date filter |

Every Gold metric will carry its **source, unit, service/geography, coverage dates, calculation rule, eligible row count or denominator, and refresh/extraction date**. Raw row count is not ridership, distinct disruptions or trains. Missing values are not zero. Cross-service OTP percentages are not a single comparable reliability score. A forecast or projection is never presented as an observed value.

## 7. Sign-off decision

The Phase 4 **data-model design** is ready to confirm with these boundaries: the first dashboard may use validated monthly/daily ridership, supported hourly entries, service-specific published reliability, alert-record fallback, quality-labelled LIRR occupancy and checked current fare pairs. Conditional and unsupported cards above stay hidden until their evidence gates pass. Full-period source quality, joins, publisher revisions and clock-change behavior are checked during pipeline construction, not assumed complete from the small Phase 4 samples.

**User confirmation pending:** accept this metric/status matrix as the Phase 4 design baseline, or identify a card whose status should change. No bulk source download, Azure resource or website deployment is part of this review.
