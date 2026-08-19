# Acceptance Criteria

**Status:** Draft. Phase-specific gates are also defined in `tasks/roadmap.md`.

| ID | Acceptance criterion | Evidence required |
|---|---|---|
| AC-001 | Required original files are inventoried and checksummed without committing raw data. | Source manifest and clean Git status for data. |
| AC-002 | Exact source schema, grain, logical keys, and relationships are documented. | Validated data dictionary/schema spec. |
| AC-003 | Data-quality tests cover specified risks and issues receive documented dispositions. | Executed test report and issue register. |
| AC-004 | Each published KPI has a validated contract with exact columns, grain, filters, null logic, and caveats. | Approved metric contract and tests. |
| AC-005 | No join produces unexplained row multiplication or monetary double counting. | Cardinality and pre/post-join reconciliations. |
| AC-006 | Analytical tables have documented grain, keys, lineage, transformation, and use. | Model spec, diagram, build SQL/code. |
| AC-007 | Major analyses trace to requirement and metric IDs and are reproducible. | SQL/notebooks with lineage headers. |
| AC-008 | SQL demonstrates correct, readable analyst-level techniques appropriate to the question. | Reviewed SQL and validation queries. |
| AC-009 | Python outputs rerun from documented dependencies and paths without editing raw inputs. | Successful clean-run record. |
| AC-010 | Dashboard measures and filters reconcile with approved analytical outputs. | Reconciliation workbook/query results. |
| AC-011 | Findings distinguish evidence, interpretation, assumptions, and limitations; no causal overclaiming. | Reviewed findings report. |
| AC-012 | Recommendations cite quantitative evidence and identify an owner/action or testable next step. | Executive summary traceability. |
| AC-013 | Profit/margin terminology is absent unless future validated cost data and an approved spec change support it. | Repository content review. |
| AC-014 | No credentials, secrets, or personal tokens are tracked. | Secret scan/manual review. |
| AC-015 | README is accurate, navigable, and contains no placeholder findings represented as facts. | Final portfolio review. |
| AC-016 | Specifications, code, docs, and dashboard definitions are synchronized; drift is resolved through approval. | Decision log and final audit. |
| AC-017 | Product GMV uses only eligible item `price`, excludes freight/payment value, and is never labeled revenue or profit. | Metric-contract and executable semantic test. |
| AC-018 | Customer metrics use `customer_unique_id`; repeat behavior is labeled observed-window behavior rather than retention. | Metric-contract identity/window tests. |
| AC-019 | Delivery metrics require explicit source endpoints and metric-specific missing/chronology handling. | Eligibility and date-attribution matrices. |
| AC-020 | Late and on-time delivery share one explicit endpoint-complete denominator and complementary equality semantics. | MET-009/MET-015 reconciliation test. |
| AC-021 | Average Review Score follows the approved order-level mean policy and reports review coverage/limitations. | Review-policy and model reconciliation. |
| AC-022 | Item and payment monetary measures never pass through an unsafe fact-to-fact join. | Safe-join tests and independent source controls. |
| AC-023 | Raw geolocation is not directly joined to fact metrics; entity geography semantics are labeled. | Model relationship and row-count tests. |
| AC-024 | Every implemented metric reconciles to an independent native-grain control within its approved tolerance. | Reconciliation results. |
| AC-025 | Facts preserve order, item, payment-sequence, and review-event grains with unique/non-null keys where specified. | MODEL-KEY/ROW tests. |
| AC-026 | Order mart joins only independently aggregated child models and passes monetary fanout regression. | MODEL-FANOUT tests. |
| AC-027 | Stable customer dimension contains one row per `customer_unique_id` and no arbitrary permanent geography. | MODEL-006 validation/schema review. |
| AC-028 | Product left join preserves every product and implements approved missing/untranslated category policy. | MODEL-007 row/key tests. |
| AC-029 | Raw geolocation is absent from the current analytical model. | MODEL-GEO-001. |
| AC-030 | Model rebuild is deterministic and completes with zero hard validation failures. | Two-run build and model validation results. |

## Phase 0 acceptance

Phase 0 is accepted only when the repository foundation exists, the charter/business requirements/metric proposals/acquisition guidance/roadmap are reviewable, all unvalidated claims are labeled, no source data or findings were fabricated, and the owner explicitly approves continuation.
