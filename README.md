# Olist E-Commerce Performance & Customer Experience Analytics

> **Status: In development — Phase 1 source validation complete, awaiting approval.** No business analysis, findings, recommendations, or dashboard claims are published yet.

An end-to-end, specification-driven analytics portfolio project using the **Brazilian E-Commerce Public Dataset by Olist**. The project is designed to demonstrate defensible business analysis, relational data modeling, data-quality assessment, SQL, Python, and Power BI delivery without overstating what the source data can support.

## Business purpose

The case study will evaluate commerce performance, customer behavior, product/category performance, seller performance, delivery operations, and customer experience. It will translate business questions into traceable requirements and governed metric definitions before implementation.

This is not a profitability analysis. The public Olist dataset does not provide validated product cost-of-goods data, so gross profit, net profit, and profit margin are out of scope.

## Current scope

Completed foundation and source-validation work includes:

- the project charter and business requirements;
- data-source, grain, quality, metric, model, analysis, dashboard, and acceptance specifications;
- repository conventions and a phased roadmap;
- safe acquisition instructions for the original Kaggle files;
- reproducible file/schema/key/relationship/grain validation and metric-feasibility assessment.

Data-quality classification and analytical implementation begin only after explicit approval of their roadmap phases.

## Planned workflow

`Business context → Requirements → Source validation → Data quality → Metric validation → Analytical model → SQL/Python analysis → Power BI → Findings → Reconciliation → Portfolio case study`

## Data source

- Dataset: Brazilian E-Commerce Public Dataset by Olist
- Kaggle owner: `olistbr`
- Dataset slug: `brazilian-ecommerce`
- Identifier: `olistbr/brazilian-ecommerce`

The source CSV files are not committed. See [the source specification](specs/02-data-source-and-schema-spec.md) for expected files and safe acquisition steps.

## Repository navigation

- `specs/` — governing requirements and contracts
- `tasks/roadmap.md` — controlled phases and exit criteria
- `sql/` — future staging, marts, analysis, and validation SQL
- `src/` — future reproducible transformation and validation code
- `notebooks/` — future profiling and exploratory analysis
- `dashboard/` — future Power BI artifacts and documentation
- `reports/` — future figures, findings, and executive summary
- `docs/` — methodology, decisions, and validated data dictionary

## Environment snapshot

At Phase 0 inspection: Python 3.9, pandas, NumPy, Matplotlib, Jupyter, Git, Node.js, and VS Code were available. Kaggle CLI, DuckDB CLI/library, SQLite CLI, and SQLAlchemy were not detected. `requirements.txt` will be finalized after the Phase 1 tool choice; no installation is required for Phase 0.

## Governance

Read `AGENTS.md` before contributing. Specifications are authoritative; raw data is immutable; every major output must trace to a requirement ID; and findings must be supported by executed analysis.
