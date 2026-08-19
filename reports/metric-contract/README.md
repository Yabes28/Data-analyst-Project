# Phase 3 Metric Contract

**Status:** Complete — awaiting explicit Phase 3 approval  
**Metrics:** 15 final contracts: 6 APPROVED, 9 APPROVED_WITH_LIMITATION, 0 BLOCKED.  
**Scope:** Semantic rules and validation only; no KPI results or analytical datasets were produced.

## Governed decisions

- Total Orders includes all statuses; Delivered Status Orders is separate.
- MET-001 uses every order status. MET-003–MET-007 and MET-011–MET-013 use the narrower approved commercial population. These populations are not interchangeable and must not share an implicit global filter.
- Commercial item/customer metrics use approved, invoiced, processing, shipped, and delivered orders.
- Product GMV is item `price` only and excludes freight/payment value.
- AOV uses order-level Product GMV divided by eligible item-bearing commercial orders.
- Customer metrics use `customer_unique_id`; repeat rate is explicitly observed-window behavior, not retention.
- Delivery metrics require delivered status and valid endpoints; purchase cohort is the primary date basis.
- Review score uses an order-level mean of all associated source review rows, followed by an unweighted average across reviewed orders.
- Recorded Payment Value stays at payment-sequence grain and is never substituted for Product GMV.

## Expected test warning

- **Test ID:** `MCT-050`
- **Impacted metric:** MET-010, Average Order-Level Review Score
- **Expected status:** `WARN`
- **Reason:** The order-level mean policy is a defensible analytical construction that gives each reviewed order equal weight, but the source provides no canonical revision/version semantics for ambiguous repeated review relationships. The warning preserves this limitation; it does not indicate contract failure.

All other 51 metric-contract tests are expected to return `PASS`.
- Raw geolocation joins and item/payment fact-to-fact joins are prohibited.

## Artifacts

- `metric-decision-register.csv` — complete machine-readable contract.
- `status-population-matrix.csv` — 120 metric/status decisions.
- `date-attribution-matrix.csv` — primary date and fallback policy.
- `metric-grain-matrix.csv` — Phase 4 grain and pre-aggregation requirements.
- `traceability-matrix.csv` — requirement/DQ/model/analysis/acceptance lineage.
- `metric-contract-test-results.csv` — semantic contract validation results.
- Supporting policy documents in this directory.

Reproduce structural contract tests with:

```powershell
python src/validation/validate_metric_contract.py
```

The test emits no business KPI values.
