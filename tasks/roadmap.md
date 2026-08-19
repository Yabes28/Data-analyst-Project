# Controlled Project Roadmap

Only the approved phase may be executed. Specifications must precede implementation, and each phase requires explicit exit evidence.

## Phase 0 — Specification & repository foundation

**Work:** Inspect repository/tooling; establish structure, governance, charter, requirements, initial contracts/specifications, acquisition guidance, and roadmap.  
**Exit criteria:** Phase 0 files exist; unvalidated items are labeled; no fabricated data/findings; owner reviews and explicitly approves Phase 0.  
**Status:** Approved and complete — owner approval received 2026-08-19.

## Phase 1 — Dataset acquisition and source validation

**Work:** Acquire original Olist files safely; create source manifest/checksums; inspect exact schemas, types, keys, grains, date range, statuses, relationships, and license.  
**Exit criteria:** DATA-001–DATA-009 evidenced; every expected/missing file accounted for; source grains and customer identity semantics documented; no analytical transformations started; spec changes approved.
**Status:** Blocked — the nine expected original CSV files are not present in `data/raw/`. Awaiting user-provided Kaggle download; no source validation has been claimed.

## Phase 2 — Data profiling & data quality assessment

**Work:** Build reproducible profiling and DQ tests; classify anomalies; propose exclusions without silently applying them.  
**Exit criteria:** DQ-001–DQ-016 executed where applicable; issue register has counts, rates, dispositions, and impacts; critical blockers resolved or explicitly accepted.

## Phase 3 — Metric contract validation

**Work:** Replace semantic placeholders with exact fields; approve populations, date logic, aggregation, null behavior, and caveats; test metrics on source data.  
**Exit criteria:** Each used metric is marked Validated with test evidence and approved definitions; rejected/deferred metrics documented; control totals recorded.

## Phase 4 — Analytical data modeling

**Work:** Justify and implement the lightweight dimensional model; create grain-safe staging/marts and lineage.  
**Exit criteria:** MODEL requirements approved; table grains/keys/lineage documented; joins pass cardinality, referential, row-count, and monetary reconciliation tests.

## Phase 5 — SQL analysis

**Work:** Execute traceable business analyses using readable CTEs, joins, date logic, windows, rankings, cohorts, and validation queries where appropriate.  
**Exit criteria:** Approved `AN-*` SQL runs reproducibly; outputs cite requirements/metrics; complete-period and coverage rules are applied; peer-style correctness review completed.

## Phase 6 — Python EDA & customer analysis

**Work:** Perform distributions, statistical summaries, visual EDA, customer frequency/cohorts, and RFM only if justified; move reusable logic from notebooks into modules.  
**Exit criteria:** Notebooks run in order from documented environment; figures are reproducible; SQL/Python shared metrics reconcile; observational limitations are stated.

## Phase 7 — Power BI analytical dataset & dashboard

**Work:** Prepare governed datasets/model, implement validated DAX, and build the three specified views.  
**Exit criteria:** DASH-001–DASH-010 satisfied; relationship/filter behavior tested; KPI totals reconcile; usability/accessibility review complete; no unsupported visual claim.

## Phase 8 — Findings & business recommendations

**Work:** Synthesize quantified insights; distinguish evidence from interpretation; create practical recommendations linked to evidence.  
**Exit criteria:** Every finding traces to executed analysis/metric; every recommendation cites a value and identifies a decision/action/test; limitations and non-causal language reviewed.

## Phase 9 — Validation & reconciliation

**Work:** Run end-to-end rerun, control totals, cross-tool reconciliation, acceptance checks, and specification-drift audit.  
**Exit criteria:** AC-001–AC-016 evidenced or exceptions approved; clean-run record produced; unexplained variances and spec drift equal zero.

## Phase 10 — Portfolio README & final case study

**Work:** Publish polished landing page, methodology, selected code/visuals, dashboard preview, results, recommendations, limitations, navigation, and rerun instructions.  
**Exit criteria:** All claims trace to validated evidence; source attribution/license verified; secret/data review passed; recruiter and technical-review checklists completed.
