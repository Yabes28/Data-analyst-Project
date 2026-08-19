# Analytical Model Specification

**Status:** Candidate design only; creation is not authorized before source inspection.

## Modeling decision to evaluate

A lightweight star-style model is likely useful because measures exist at order, item, payment, and review grains. Phase 4 must justify the final design using validated keys/cardinalities. The core safeguard is that facts remain separate and are combined only through conformed dimensions or pre-aggregated one-row-per-order bridges.

| ID | Candidate table | Proposed grain | Candidate logical key | Sources | Proposed transformation / use | Status |
|---|---|---|---|---|---|---|
| MODEL-001 | `fact_orders` | One row per order | order ID | orders, customers; safe order aggregates | Lifecycle fields and order-level item/payment summaries created independently before joining. Executive/order/delivery analysis. | Pending Validation |
| MODEL-002 | `fact_order_items` | One row per validated order-item sequence | order ID + item sequence | order items | Preserve item price, freight, product, seller. Product/category/seller commerce. | Pending Validation |
| MODEL-003 | `fact_payments` or `agg_order_payments` | One payment record or one order aggregate, explicitly chosen | order + payment sequence or order | payments | Retain payment detail or aggregate before order join. Payment behavior. | Pending Validation |
| MODEL-004 | `fact_order_reviews` | One canonical review record per approved grain | pending review rule | reviews | Resolve duplicate/revision semantics; retain coverage. Experience analysis. | Pending Validation |
| MODEL-005 | `dim_customers` | One row per stable customer identity | stable customer ID | customers | Separate stable identity from order-linked customer reference; geography attributes subject to SCD assumptions. | Pending Validation |
| MODEL-006 | `dim_products` | One row per product | product ID | products, category translation | Preserve unknown/untranslated category labels. | Pending Validation |
| MODEL-007 | `dim_sellers` | One row per seller | seller ID | sellers | Seller attributes; geography enrichment only after safe normalization. | Pending Validation |
| MODEL-008 | `dim_date` | One row per calendar date | date | generated from validated observation window | Calendar attributes and complete-period flags. | Pending Validation |
| MODEL-009 | `dim_geography` | Approved normalized geographic grain | pending | geolocation plus entity location fields | Use deterministic aggregation/mapping; never raw many-row postal join. | Pending Validation |

## Mandatory join rules

1. Profile and document both sides of every join before implementation.
2. Never directly join multi-row items to multi-row payments and aggregate money.
3. Never attach an order-level review to every item and then average without weighting/duplication analysis.
4. Multi-seller orders require an explicit allocation rule before seller-level order metrics.
5. Store metric eligibility flags/counts where they improve auditability.
6. Validate row counts, distinct keys, unmatched keys, and monetary totals after every material join.

## Phase 4 deliverables

Approved grain/key/source/transformation/use for every table; relationship/cardinality diagram; column-level mappings; date-role strategy; Power BI relationship direction; incremental/rebuild method; and reconciliation tests.

