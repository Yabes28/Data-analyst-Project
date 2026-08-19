# Metric Contract

**Contract approval status:** Pending Validation until Phase 3 approves each executable definition. Phase 1 source feasibility is classified separately below.

## Phase 1 feasibility assessment

All proposed metrics are **Partially Validated** for source feasibility: the required source fields exist and their native grains are confirmed, but no metric is fully validated until Phase 3 approves status eligibility, date attribution, null/exclusion rules, and reconciliation controls.

| Metric | Phase 1 status | Required tables / exact source columns | Native grain and remaining risk |
|---|---|---|---|
| MET-001 | Partially Validated | orders: `order_id`, `order_purchase_timestamp`, `order_status` | Order; reporting-period completeness/status policy pending. |
| MET-002 | Partially Validated | orders: `order_id`, `order_status`, purchase timestamp | Order; `delivered` is observed, but eligibility/date attribution pending. |
| MET-003 | Partially Validated | order_items: `order_id`, `order_item_id`, `price`; orders for eligibility | Item line; eligible statuses/refund limitation pending. |
| MET-004 | Partially Validated | order_items: `price`, `freight_value`, item key; orders for eligibility | Item line; null policy is straightforward but status policy pending. |
| MET-005 | Partially Validated | MET-003 fields aggregated to `order_id` | Order after item aggregation; denominator/status policy pending. |
| MET-006 | Partially Validated | customers: `customer_unique_id`, `customer_id`; orders: `order_id`, status/time | Customer; stable identity validated, eligible order population pending. |
| MET-007 | Partially Validated | MET-006 fields | Customer across fixed observation window; eligibility/right-censoring policy pending. |
| MET-008 | Partially Validated | orders: purchase/delivered timestamps, status | Order; chronology exceptions and eligible delivered population pending. |
| MET-009 | Partially Validated | orders: actual/estimated delivery timestamps, status | Order; timestamp-versus-date comparison and exception policy pending. |
| MET-010 | Partially Validated | reviews: `review_id`, `order_id`, `review_score`; orders for context | Review event; canonical handling is blocked by repeated review/order relationships until approved. |
| MET-011 | Partially Validated | order_items: `order_id`, `order_item_id` | Item line; key validated, order eligibility pending. |
| MET-012 | Partially Validated | order_items: `freight_value`, item key | Item line; 383 zeros require classification, status policy pending. |
| MET-013 | Partially Validated | order_items: `price`, `freight_value`, item key | Item aggregation; denominator/eligibility policy pending. |
| MET-014 | Partially Validated | payments: `order_id`, `payment_sequential`, `payment_value` | Payment record; nine zeros and order eligibility pending; item join prohibited. |
| MET-015 | Partially Validated | MET-009 fields | Order; must share MET-009 denominator after Phase 3 approval. |

Common rules: monetary values use source currency as documented by Olist; no FX or inflation adjustment is assumed. Status names and column names below are semantic placeholders until inspected. Distinct order/customer counting occurs only at a validated grain.

| ID | Metric | Business definition | Mathematical definition | Required semantic fields | Grain | Filters / null handling | Caveats | Status |
|---|---|---|---|---|---|---|---|---|
| MET-001 | Total Orders | Distinct orders placed in the reporting period. | `COUNT(DISTINCT order_id)` | order ID, purchase timestamp | Reporting period | Valid ID and timestamp for time trends; all statuses shown or filter disclosed. | Partial periods can distort comparisons. | Pending Validation |
| MET-002 | Delivered Orders | Distinct orders with validated delivered status. | `COUNT(DISTINCT order_id WHERE status='delivered')` | order ID, status | Reporting period | Null/unknown statuses excluded and counted separately. | Status domain must be verified. | Pending Validation |
| MET-003 | Product GMV | Sum of item selling prices, excluding freight. | `SUM(order_item_price)` | order ID, item key, item price | Order item then aggregate as needed | Default eligibility/status policy must be approved; null price excluded and reported. | Not revenue recognition or profit; refunds/returns may be unavailable. | Pending Validation |
| MET-004 | Gross Order Value | Item price plus item-level freight, kept distinct from Product GMV. | `SUM(order_item_price + freight_value)` | item price, freight | Order item then aggregate | Null components handled only after profiling; eligibility disclosed. | Not payment value, revenue, or profit. | Pending Validation |
| MET-005 | Average Order Value | Mean order-level Product GMV for eligible distinct orders. | `SUM(order-level Product GMV) / COUNT(eligible orders)` | fields for MET-003, order ID | Order then reporting group | Orders without eligible items/excluded statuses must be disclosed. | Numerator explicitly excludes freight. | Pending Validation |
| MET-006 | Unique Customers | Count of distinct stable customer identities with eligible orders. | `COUNT(DISTINCT stable_customer_id)` | stable customer ID, order ID | Customer | Identifier semantics and order eligibility required. | Order-linked customer ID must not be assumed stable. | Pending Validation |
| MET-007 | Repeat Customer Rate | Share of eligible customers with at least two eligible distinct orders in the observation window. | `customers(order_count>=2) / customers(order_count>=1)` | stable customer ID, order ID, purchase time/status | Customer | Null stable IDs excluded/reported; fixed observation window disclosed. | Right-censoring and historical coverage bias. | Pending Validation |
| MET-008 | Average Delivery Lead Time | Mean elapsed time from purchase to customer delivery for eligible delivered orders. | `AVG(delivered_at - purchased_at)` | purchase and delivery timestamps, status | Order | Both timestamps valid; delivered eligibility; chronology failures excluded/reported. | Mean should be paired with median/distribution. | Pending Validation |
| MET-009 | Late Delivery Rate | Share of eligible delivered orders delivered after estimated delivery date. | `COUNT(delivered_at > estimated_at) / COUNT(valid delivered_at & estimated_at)` | actual/estimated delivery timestamps, status | Order | Valid timestamps and delivered orders only. | Exact timestamp/date comparison convention must be approved. | Pending Validation |
| MET-010 | Average Review Score | Mean validated review score among canonical eligible reviews. | `AVG(review_score)` | order/review IDs, review score | Canonical review/order | Null/invalid scores excluded/reported; duplicate resolution required. | Review coverage and selection bias must be disclosed. | Pending Validation |
| MET-011 | Item Volume | Count of validated order-item rows. | `COUNT(valid order_item_key)` | order ID, item sequence/key | Order item | Duplicate/invalid item keys excluded only after disposition. | Not order volume. | Pending Validation |
| MET-012 | Freight Value | Sum of item-level freight charges. | `SUM(freight_value)` | freight value, item key | Order item | Null/negative policy pending profiling. | Not logistics cost or profit impact. | Pending Validation |
| MET-013 | Freight Burden | Freight value relative to gross order value. | `SUM(freight) / SUM(item price + freight)` | item price, freight | Aggregated item set | Denominator > 0; weighted ratio, not mean of row ratios. | Alternative denominator requires contract change. | Pending Validation |
| MET-014 | Payment Value | Sum of validated payment records at payment grain. | `SUM(payment_value)` | order ID, payment sequence, value | Payment record then order | Duplicate/payment-status semantics pending. | Must never be multiplied through item joins; may not reconcile to item values. | Pending Validation |
| MET-015 | On-time Delivery Rate | Complement of late delivery among the same eligible records. | `1 - MET-009` | MET-009 fields | Order | Same denominator as MET-009. | Do not compute with a different eligibility set. | Pending Validation |

## Contract approval checklist

For each metric, Phase 3 must replace semantic placeholders with exact fields, approve eligible statuses/date logic, document the reporting date attribution, test null behavior, define aggregation behavior, reconcile a control total, and change status to **Validated** only with evidence.
