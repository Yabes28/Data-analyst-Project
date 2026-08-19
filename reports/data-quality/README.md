# Phase 2 Data Quality Assessment

**Status:** Complete — awaiting explicit Phase 2 approval  
**Raw data integrity:** PASS  
**Scope:** Classification and proposed future treatment only. No source rows were changed, cleaned, imputed, deduplicated, or excluded; no business analysis was performed.

## Reproduce

```powershell
python src/validation/validate_raw_integrity.py
python src/validation/validate_data_quality.py
```

Known conditions return `WARN` or `INFO`; only validator/integrity failures are hard failures. The structured evidence is in `data-quality-test-results.csv`, and the governed issue list is `data-quality-issue-register.csv`.

## Executive data-quality summary

- 18 Data Quality specification requirements are defined (`DQ-001` through `DQ-018`).
- 15 active issues/conditions are represented in `data-quality-issue-register.csv`.
- Classifications: 4 `ANALYTICAL_MODELING_CONDITION`, 4 `SOURCE_DATA_LIMITATION`, 4 `UNRESOLVED`, 2 `ANALYTICAL_EXCLUSION_CANDIDATE`, and 1 `VALID_BUSINESS_CONDITION`.
- Severities: 1 CRITICAL, 8 HIGH, 5 MEDIUM, and 1 LOW.
- Tests: 16 PASS, 12 WARN, and 4 INFO.

### Specification-to-register reconciliation

The difference between 18 specification IDs and 15 active register rows is intentional. The specification contains both issue requirements and preventive/integrity controls:

| Specification ID | Register status | Reason |
|---|---|---|
| DQ-001 | Intentionally not an active issue row | Raw-integrity control passed: all nine files match the Phase 1 manifest. It remains a CRITICAL hard gate in `data-quality-test-results.csv`. |
| DQ-003 | Intentionally not an active issue row | Critical-identifier control passed with zero null critical identifiers. It remains an executable hard control. |
| DQ-004 | Intentionally not an active issue row | Core foreign-key control passed with zero child orphans. Optional relationship absence and reference coverage gaps are active issues under DQ-012, DQ-013, and DQ-016. |
| DQ-002 and DQ-005–DQ-018 | Active issue rows | Each maps one-to-one to the same ID in `data-quality-issue-register.csv`. |

No IDs are reserved, merged, retired, or renumbered. DQ-001, DQ-003, and DQ-004 are informational/preventive specification requirements with passing executable results; converting successful controls into active issues would misrepresent the evidence. Classification and severity totals apply only to the 15 active register rows.

## Critical technical risk

### DQ-015 — item/payment fanout

A direct item-to-payment join on `order_id` creates `I_o × P_o` rows. There are 9,802 multi-item orders, 2,936 multi-payment orders, and 275 with both. The unsafe join produces 117,601 rows and increases the item-price control by 4.544% and payment-value control by 28.157%. This is analytically CRITICAL, not a source-row defect.

Permanent choice: `DEFERRED_TO_PHASE_4`. Safe candidates are separate fact tables, item pre-aggregation to order grain, and payment pre-aggregation to order grain.

## Semantic risks

### Customer identity

`customer_id → order_id` is 1:1 at the order-associated customer-record grain. `customer_unique_id → orders` is potentially 1:M across multiple customer records. There are 99,441 unique `customer_id`, 96,096 stable identities, 2,997 identities with multiple records, and a maximum of 17 records per identity. This is an analytical modeling condition, not duplicate customer data.

### Ambiguous review relationships

There are 98,410 unique review IDs. 789 review IDs span multiple orders and retain the same score and recorded timestamps across those mappings; 547 orders have multiple distinct review IDs, including 202 with score variation. Maximum rows per order is three and there are no exact duplicate rows. With no revision/version field, the behavior remains `UNRESOLVED`; no first/latest/average/deduplication policy is approved.

### Status eligibility and missingness

Eight source statuses have different timestamp and child-table coverage. Missing carrier/customer-delivery timestamps are mostly structural for incomplete lifecycle states, while delivered orders include 14 missing approval timestamps, two missing carrier timestamps, and eight missing customer-delivery timestamps. Six non-delivered orders contain a customer-delivery timestamp. Every metric-population decision is `PENDING_PHASE_3`.

Optional review text is structurally absent for 88.34% of titles and 58.70% of messages; this does not invalidate review scores but limits later text coverage.

### Observation window and timezone

Purchases are bounded from 2016-09-04 21:15:19 through 2018-10-17 17:30:18. Boundary completeness is not guaranteed. Late entrants have less opportunity to repurchase, and recency depends on the dataset endpoint. Phase 6 must disclose censoring/exposure; no retention, cohort, or RFM work was performed.

Timestamps contain no timezone metadata. They remain source-naive; hour-of-day or timezone-sensitive interpretation requires additional justification.

## Temporal assessment

- Purchase after approval: 0.
- Purchase after customer delivery: 0.
- Approval after carrier handoff: 1,359 (1.36664%); median violation 17.17 hours, maximum 4,109.26 hours.
- Carrier handoff after customer delivery: 23 (0.023129%); median violation 39.86 hours, maximum 386.31 hours.
- Customer delivery after estimate: 7,827. This is potential late delivery, a valid business condition—not a chronology defect.

The two unexpected sequence patterns are unresolved and are potential metric-specific exclusion candidates; timestamps were not corrected.

### Shipping-limit dates in 2020

Four item rows across three orders have 2020 shipping-limit timestamps. All involve one seller; purchase-to-limit differences are approximately 1,052–1,056 days. The orders were purchased in 2017 and have canceled, shipped, and delivered statuses. The pattern is small and concentrated but cannot be explained from source evidence, so it remains `UNRESOLVED` and preserved.

## Geolocation assessment

Raw geolocation is a source-observation table, not a ZIP dimension:

- 1,000,163 rows; 261,831 exact repeats.
- 19,015 ZIP prefixes: 1,043 single-row and 17,972 multi-row prefixes.
- Maximum 1,146 observations per prefix.
- 8,556 multi-city and eight multi-state prefixes.
- 278 customer rows and seven seller rows lack ZIP coverage.

Normalization candidates for Phase 4:

| Candidate | Advantages | Disadvantages / caveat | Deterministic? | Multiplication risk after normalization |
|---|---|---|---|---|
| Median latitude/longitude per ZIP | Robust to extreme coordinates; simple | May not correspond to a real observation; needs label rule | Yes | None at one row/ZIP |
| Mean/centroid coordinates | Familiar and uses all observations | Sensitive to extreme coordinates and dispersed prefixes | Yes | None at one row/ZIP |
| Modal city/state plus deterministic coordinate rule | Interpretable labels | Requires explicit tie-break; mode can hide genuine boundary variation | Yes with tie-break | None at one row/ZIP |
| Separate normalized geographic reference with quality flags | Preserves conflicts/coverage transparently | More modeling/documentation effort | Yes | None if key uniqueness enforced |

Final decision: `DEFERRED_TO_PHASE_4`.

## Product categories

610 products, representing 1,603 item rows, have no Portuguese category. Two source categories lack English mappings, affecting 13 products and 24 item rows. Later display options include an explicit `Unknown`, retaining the Portuguese value, or an explicit untranslated label; Phase 2 implements none of them.

## Monetary fields

- `price`: no nulls, zeros, negatives, or parse failures; range 0.85–6,735.
- `freight_value`: 383 zeros, no nulls/negatives; range 0–409.68.
- `payment_value`: nine zeros, no nulls/negatives; range 0–13,664.08.
- Zero payments consist of six voucher records and three `not_defined` records across delivered, shipped, and canceled orders.

Zeros and large values remain preserved. They are not automatically invalid or outliers requiring removal.

## Data that must not be used naively

- Do not join item and payment rows directly before aggregating their measures.
- Do not join raw geolocation rows to customers, sellers, orders, or items.
- Do not treat `customer_id` as a stable cross-order identity.
- Do not arbitrarily select or deduplicate review rows.
- Do not apply one undocumented status population across all metrics.
- Do not treat all nulls as equivalent or all late deliveries as chronology defects.

## Decisions deferred

- Phase 3: metric populations, date attribution, delivery endpoint rules, zero-value handling, customer observation window, and review-score metric policy.
- Phase 4: item/payment fact design, geolocation normalization, category display/modeling, and possibly canonical review modeling.
- Phase 6: customer censoring methodology and any cohort/RFM feasibility decision.
