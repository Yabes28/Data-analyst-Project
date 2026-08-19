# Analytical Model Specification

**Status:** Phase 4 approved implementation specification

| ID | Table | Grain / key | Sources | Purpose / metrics | DQ and reconciliation |
|---|---|---|---|---|---|
| MODEL-001 | `fact_orders` | One row/order; `order_id` | orders + customers | Lifecycle, stable identity, order geography, delivery flags; MET-001/002/006–010/015 | Exact source order count/key; DQ-005/008/009/011/016/018 |
| MODEL-002 | `fact_order_items` | One row/order item; `order_id, order_item_id` | items + order status | Native item money and commercial flag; MET-003–005/011–013 | Exact source grain/sums; DQ-007/008/015/016 |
| MODEL-003 | `fact_payments` | One row/payment sequence; `order_id, payment_sequential` | payments + purchase date/status | Independent recorded payments; MET-014 | Exact source grain/value; never item join |
| MODEL-004 | `fact_review_events` | One source review row | reviews | Preserve ambiguous events | Exact source row count; DQ-002/010 |
| MODEL-005 | `fact_order_reviews` | One row/reviewed order; `order_id` | MODEL-004 | Order mean/min/max/count/variation; MET-010 | One row/order; weighted policy prohibited |
| MODEL-006 | `dim_customer_identity` | One row/stable identity; `customer_unique_id` | customers | Stable customer key only; MET-006/007 | Exact distinct identity count; no permanent geography |
| MODEL-007 | `dim_products` | One row/product; `product_id` | products LEFT JOIN translation | Category fallback/status and product attributes | Preserve all products; DQ-012 |
| MODEL-008 | `dim_sellers` | One row/seller; `seller_id` | sellers | Seller-owned geography | Exact source key; no raw geolocation |
| MODEL-009 | `dim_date` | One row/calendar date; `date` | generated source date bounds | Standard calendar roles | Unique contiguous dates; no fiscal assumptions |
| MODEL-010 | `agg_order_items` | One row/item-bearing order | MODEL-002 | Independent item count/GMV/freight/gross/product/seller aggregates | Reconcile to item fact |
| MODEL-011 | `agg_order_payments` | One row/payment-bearing order | MODEL-003 | Independent payment aggregates | Reconcile to payment fact |
| MODEL-012 | `mart_order_analytics` | One row/order; `order_id` | MODEL-001 LEFT JOIN MODEL-010/011/005 | Recruiter-readable SQL/Python/Power BI convenience layer | Only independently aggregated children; exact order count; native facts authoritative |

## Decisions

- DuckDB 1.4.5 is the embedded engine. The rebuildable database is `data/interim/olist_analytics.duckdb` and is Git-ignored.
- Raw geolocation normalization is deferred: current state/city analysis is supported by order-associated customer and seller fields. No raw geolocation join exists.
- Customer geography stays on `fact_orders`; `dim_customer_identity` contains no arbitrarily selected home location.
- The order mart is justified for safe consumption, but never replaces native facts for reconciliation.
- Staging casts types and preserves rows/values. No anomaly correction, deduplication, or imputation occurs.

## Flag contract

`is_commercially_eligible` implements the approved five-status population. `is_delivered_status` reflects status only. `has_delivery_endpoints`, `is_delivery_metric_eligible`, `is_late_delivery`, and `is_on_time_delivery` implement MET-008/009/015 endpoints. `has_items`, `has_payment`, and `has_review` are source-coverage flags.

