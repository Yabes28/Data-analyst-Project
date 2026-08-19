# Data Quality Specification

**Status:** Draft — executable thresholds pending source profiling.

## Assessment principles

Raw records are never edited or automatically removed. Each observed issue must be quantified, retained in a test result, and classified as one of: **valid business condition**, **source-data limitation**, **data-quality defect**, or **analytical exclusion**. Exclusions require a stated metric/analysis impact.

| ID | Test area | Required test | Initial disposition rule |
|---|---|---|---|
| DQ-001 | File integrity | Expected files, readable CSV structure, checksum, encoding, delimiter. | Block downstream work if structurally unreadable or missing. |
| DQ-002 | Key uniqueness | Duplicate candidate keys for each source. | Investigate; never deduplicate without deterministic rule. |
| DQ-003 | Critical IDs | Null/blank order, customer, product, seller, review, or payment identifiers where required by grain. | Quantify and assess referential impact. |
| DQ-004 | Foreign keys | Unmatched orders/customers/items/products/sellers/payments/reviews/translations. | Preserve and report; exclusion depends on analytical use. |
| DQ-005 | Timestamps | Parse failures, invalid values, and unexpected observation-window bounds. | Preserve raw value; derived time metrics require valid endpoints. |
| DQ-006 | Chronology | Purchase, approval, carrier, delivery, and estimate chronology violations. | Classify case-by-case; exclude only from affected duration metric if justified. |
| DQ-007 | Monetary values | Negative and zero price, freight, and payment values; nonnumeric values. | Zero may be valid; negatives require investigation. |
| DQ-008 | Status | Unexpected, cancelled, unavailable, or inconsistent lifecycle states. | Treat status as business condition unless evidence indicates defect. |
| DQ-009 | Delivery completeness | Missing delivery dates by status and required endpoints for lead time. | Exclude only from delivery-duration denominator; report coverage. |
| DQ-010 | Reviews | Duplicate review IDs, multiple review/order links, missing scores, scores outside validated domain. | Establish canonical review rule before aggregation. |
| DQ-011 | Customer identity | Relationship between order-linked customer ID and stable customer identity. | Block repeat-rate/cohort work until validated. |
| DQ-012 | Categories | Missing source category and unmatched translation. | Retain explicit Unknown/Untranslated group when modeled. |
| DQ-013 | Geolocation | Duplicate postal prefixes, conflicting city/state/coordinates, invalid coordinates. | Do not direct-join until normalized aggregation is specified. |
| DQ-014 | Categorical consistency | Whitespace, casing, spelling, and unexpected domain values. | Normalize only in derived layers with documented mapping. |
| DQ-015 | Join cardinality | Pre/post-join row counts, key multiplicity, and monetary control totals. | Any unexplained multiplication blocks release. |
| DQ-016 | Coverage | Metric-eligible numerator/denominator records and excluded counts. | Publish coverage with affected metrics. |

## Output contract

Phase 2 must produce a machine-readable test summary and a human-readable issue register containing test ID, table/column, observed count/rate, examples that contain no secrets, classification, decision, owner, and downstream impact. Thresholds and accepted exceptions must be approved rather than invented during implementation.

