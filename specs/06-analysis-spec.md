# Analysis Specification

**Status:** Draft; execution blocked until metrics and model are validated.

| ID | Analysis | Requirements | Primary metrics | Method / expected output |
|---|---|---|---|---|
| AN-001 | Commerce trend and period comparison | BR-001–BR-003 | MET-001–MET-005 | Monthly series, complete-period flags, `LAG`, absolute/percentage change. |
| AN-002 | Geographic demand | BR-004 | MET-001, MET-003, MET-005, MET-006 | Customer-state ranking and share; coverage/unmapped group. |
| AN-003 | Customer frequency and repeat behavior | BR-005–BR-006 | MET-006–MET-007 | Customer-level aggregation and frequency distribution. |
| AN-004 | Cohort retention | BR-007 | MET-006–MET-007 | Acquisition cohort matrix with exposure/right-censoring disclosure. |
| AN-005 | RFM assessment | BR-008 | governed components | Validate usefulness, recency anchor, scoring, and segment stability before publishing. |
| AN-006 | Category portfolio | BR-009–BR-011 | MET-001, MET-003, MET-005, MET-011–MET-013 | Category ranks, mix, freight burden, unknown coverage. |
| AN-007 | Seller concentration/performance | BR-012–BR-014 | MET-003, MET-008–MET-010 | Seller shares/cumulative concentration, minimum sample context, attribution safeguards. |
| AN-008 | Delivery performance | BR-015–BR-017 | MET-008, MET-009, MET-015 | Distribution, lateness, region/category comparisons and excluded-record counts. |
| AN-009 | Review distribution and coverage | BR-018, BR-020 | MET-010 | Score distribution, coverage, grouped comparisons with sample sizes. |
| AN-010 | Delivery–review association | BR-019 | MET-009, MET-010 | On-time vs late comparisons, confidence/uncertainty where appropriate; no causal claim. |
| AN-011 | Payment behavior and reconciliation | BR-021–BR-022 | MET-014 and commerce metrics | Payment type/installment summaries after validation; explain rather than erase differences. |

Every output must state requirement/metric IDs, population, grain, filters, date attribution, missing-data coverage, and limitations. Quantitative findings are prohibited until the analysis is executed and validated.

