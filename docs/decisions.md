# TransitIQ — Decision log

## Why do we need this file?

As we build TransitIQ, we may change a tool, feature, calculation, or cost plan. This file records what we decided and why, so we can understand those choices later.

The full project scope is in `docs/scope.md`. This file records decisions that confirm or change that scope.

## How will we make a decision?

For each important choice, we will:
1. Describe the choice.
2. Check the evidence, such as available data, account access, or cost.
3. Agree on what to do.
4. Record the decision here with its date and effect on the project.

A question we have not answered yet is open, not a confirmed decision.

## What does each status mean?
- Proposed: We are considering it.
- Confirmed: We have agreed to use it.
- Replaced: A newer decision has taken its place.

If a decision changes, we will add a new entry and mark the old one Replaced. This keeps the history clear.

## 2026-10-18 — Phase 0 project scope

- Status: Confirmed.
- Decision: Use the services, five website tabs, time period, build stages, cost limit, and E: drive plan written in docs/scope.md.
- Reason: We need one agreed starting point before setting up tools or working with data.
- Effect: This guides future work. It does not create Azure resources or charges.
- Replaces: None

## Questions we will decide in later phases

These are not decided yet:
- Which small MTA dataset will be used for the first complete pipeline?
- Which planned metrics do the public datasets actually support?
- Can your Azure account use the Azure SQL Database free offer?
- Can Azure Databricks be used within the zero-spending limit?
- What hosting and document-search setup will the AI assistant use?

We will answer each question in the phase where we have enough evidence, then add a decision entry.