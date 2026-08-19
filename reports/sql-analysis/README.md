# Phase 5 SQL Business Analysis

Phase 5 uses DuckDB 1.4.5 and 13 governed SQL queries to calculate MET-001 through MET-015 and answer approved business requirements. Run `python src/analysis/run_sql_analysis.py --rebuild-model`.

The runner validates required models, executes queries deterministically, exports compact results, reconciles core metrics, regenerates evidence, and fails on hard controls. SQL uses native-grain facts or independently aggregated order models; item and payment facts are never joined.

## Scope and safeguards

- AN-001–AN-003 and AN-006–AN-011 are complete. AN-004 cohort retention and AN-005 RFM are deferred to Phase 6.
- `query-index.csv` maps BR → MET → MODEL → AN → SQL → result; the evidence register extends the chain to findings.
- All metrics use approved populations and purchase-date attribution. Rates and averages retain denominators.
- The 26-month purchase window is calendar-scaffolded: 19 months are `COMPLETE_PERIOD`, six are `PARTIAL_PERIOD`, and 2016-11 is `NO_OBSERVED_ACTIVITY`. The no-activity month retains NULL measures rather than fabricated zeros. MoM/YoY values require both calendar-aligned periods to be complete, so comparisons cannot bridge a missing month.
- Customer frequency uses `customer_unique_id` and observed-window language.
- Category trends use the predetermined top five categories by full-window eligible Product GMV.
- Seller Product GMV/concentration uses every commercially eligible item and seller. Delivery/review outcomes separately use single-seller commercial orders, visible denominators, and no best/worst label. This outcome-attribution rule excludes 1,277 of 98,199 commercial item-bearing orders (1.30%); it is not a universal seller filter.
- Review comparisons use the approved order mean. Low score means order-level mean `<= 2`; findings are observational, not causal.
- Product GMV excludes freight; Recorded Payment Value stays independent; raw geolocation is not referenced.

## Validation

- Raw integrity: PASS (9 hashes unchanged)
- Model validation: PASS (25/25)
- Fanout regression: PASS (3/3)
- Core metric reconciliation: PASS (15/15)
- SQL validation: PASS (51/51)
- Two-run reproducibility: PASS (13/13 result hashes identical)

Findings are descriptive evidence only. Final recommendations remain reserved for Phase 8.
