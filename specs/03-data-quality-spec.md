# Data Quality Specification

**Status:** Phase 2 evidence complete — treatments proposed but not implemented.

## Assessment principles

Raw records are never edited or automatically removed. Every registered condition uses exactly one controlled primary classification: `VALID_BUSINESS_CONDITION`, `SOURCE_DATA_LIMITATION`, `DATA_QUALITY_DEFECT`, `ANALYTICAL_MODELING_CONDITION`, `ANALYTICAL_EXCLUSION_CANDIDATE`, or `UNRESOLVED`. Phase 2 treatment states propose later handling but do not implement it.

| ID | Risk/test | Observed evidence | Primary classification | Severity | Proposed handling | Owner |
|---|---|---|---|---|---|---|
| DQ-001 | File integrity | Nine hashes match Phase 1; no missing/extra CSVs. | Control passed; no registered issue | CRITICAL control | Hard fail on change. | Every phase |
| DQ-002 | Candidate-key assumptions | Validated entity keys pass; review/geolocation apparent keys are non-unique. | ANALYTICAL_MODELING_CONDITION | HIGH | Preserve source grains; require model rules. | Phase 4 |
| DQ-003 | Critical IDs | Zero null critical IDs in tested sources. | Control passed; no registered issue | CRITICAL control | Hard fail if introduced. | Every phase |
| DQ-004 | Foreign keys | Zero child orphans across six core relationships. | Control passed; optional/reference gaps handled under DQ-012/013/016 | HIGH control | Retain relationship tests. | Phase 4/9 |
| DQ-005 | Timestamp parsing/timezone | Zero parse failures; no timezone metadata. | SOURCE_DATA_LIMITATION | MEDIUM | Preserve source-naive timestamps and disclose. | Phase 3/6 |
| DQ-006 | Chronology | 1,359 approval-after-carrier; 23 carrier-after-delivery; late delivery separated as business condition. | UNRESOLVED | HIGH | Potential metric-specific exclusion; no correction. | Phase 3 |
| DQ-007 | Monetary values | No nulls/negatives/parse failures; 383 zero freight and nine zero payments. | UNRESOLVED | MEDIUM | Preserve; approve metric rules after context review. | Phase 3 |
| DQ-008 | Status | Eight lifecycle states with different timestamps/child coverage. | VALID_BUSINESS_CONDITION | HIGH | Metric eligibility `PENDING_PHASE_3`. | Phase 3 |
| DQ-009 | Delivery completeness | Eight delivered orders lack customer delivery; six non-delivered orders contain it. | ANALYTICAL_EXCLUSION_CANDIDATE | HIGH | Require valid endpoint/status population rule. | Phase 3 |
| DQ-010 | Reviews | 789 review IDs span orders; 547 orders have multiple review IDs; no revision field. | UNRESOLVED | HIGH | Preserve events; canonical rule not approved. | Phase 3/4 |
| DQ-011 | Customer identity | 99,441 customer records; 96,096 stable IDs; 2,997 stable IDs repeat; max 17. | ANALYTICAL_MODELING_CONDITION | HIGH | Use `customer_unique_id` subject to metric rules. | Phase 3 |
| DQ-012 | Categories | 610 missing categories; two untranslated values; affected item coverage quantified. | SOURCE_DATA_LIMITATION | MEDIUM | Preserve missing/original values; model display rule later. | Phase 4 |
| DQ-013 | Geolocation | 17,972 multi-row ZIPs; label/coordinate conflicts and coverage gaps. | ANALYTICAL_MODELING_CONDITION | HIGH | Normalize deterministically; final choice deferred. | Phase 4 |
| DQ-014 | Categorical consistency | Source labels preserved; geographic label variation measured. | SOURCE_DATA_LIMITATION | LOW | Normalize only in derived layer with mapping. | Phase 4 |
| DQ-015 | Item/payment fanout | Unsafe join inflates item-price control 4.544% and payment control 28.157%. | ANALYTICAL_MODELING_CONDITION | CRITICAL | Separate/pre-aggregate facts; `DEFERRED_TO_PHASE_4`. | Phase 4 |
| DQ-016 | Related-source coverage | 775 orders lack items, one lacks payments, 768 lack reviews; no child orphans. | ANALYTICAL_EXCLUSION_CANDIDATE | MEDIUM | Metric-specific eligibility; preserve parent orders. | Phase 3 |
| DQ-017 | 2020 shipping-limit values | Four item rows, three 2017 orders, one seller, ~1,052–1,056 day deltas. | UNRESOLVED | MEDIUM | Preserve and investigate; no inferred correction. | Phase 3/4 |
| DQ-018 | Observation-window censoring | Purchases bounded 2016-09-04 to 2018-10-17; boundary completeness unknown. | SOURCE_DATA_LIMITATION | HIGH | Disclose window/exposure and fix recency anchor later. | Phase 3/6 |

## Output contract

Phase 2 evidence is stored under `reports/data-quality/`. `data-quality-issue-register.csv` is authoritative for classifications/treatment states; `data-quality-test-results.csv` records PASS/WARN/INFO results; and `metric-impact-matrix.csv` links issues to proposed metrics. No Phase 3 population rule or Phase 4 model decision is approved by this specification.
