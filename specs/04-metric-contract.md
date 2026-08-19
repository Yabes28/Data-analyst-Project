# Metric Contract

**Status:** Phase 3 final — authoritative for downstream modeling and analysis  
**Scope:** MET-001 through MET-015. Changes require SDD approval.

## Global analytical policies

- Source timestamps remain timezone-naive; no timezone conversion or fallback dates are allowed.
- The primary reporting date for every current core metric is `order_purchase_timestamp`. Delivery/review event-date views may be secondary analyses but cannot redefine the KPI.
- Commercial population means statuses `approved`, `invoiced`, `processing`, `shipped`, and `delivered`. `created`, `canceled`, and `unavailable` remain in MET-001 but are excluded from lifecycle-active commercial value/item/customer metrics.
- Missing values are handled only at the affected metric grain; no global row deletion or imputation is permitted.
- Monetary zero is not null. Zero freight/payment values are preserved and disclosed.
- Product category grouping retains all records: missing Portuguese category displays `Unknown Category`; untranslated categories retain the Portuguese label with an `Untranslated` indicator. No English translation is fabricated.
- Customer geography uses customer city/state; seller geography uses seller city/state. Raw geolocation is prohibited until Phase 4 normalization.
- `shipping_limit_date` is not required by MET-001–MET-015; the four 2020 rows have `NO_IMPACT_ON_CURRENT_CORE_METRICS`.
- Item and payment facts must never be joined directly before aggregating monetary measures at their native grains.
- Purchase observation window is 2016-09-04 21:15:19 through 2018-10-17 17:30:18. Boundary completeness is not assumed.
- **Population non-interchangeability:** MET-001 includes all order statuses. MET-003–MET-007 and MET-011–MET-013 use the narrower approved commercial population. These populations answer different questions and must never be substituted, compared as if denominator-equivalent, or implemented through one global order filter.

## Status summary

| Metric | Approved name | Final status | Primary calculation grain | Population summary |
|---|---|---|---|---|
| MET-001 | Total Orders | APPROVED | Order | All statuses |
| MET-002 | Delivered Status Orders | APPROVED | Order | `delivered` status |
| MET-003 | Product GMV | APPROVED_WITH_LIMITATION | Order item | Commercial population |
| MET-004 | Gross Order Value | APPROVED_WITH_LIMITATION | Order item | Commercial population |
| MET-005 | Average Order Value (Product GMV) | APPROVED_WITH_LIMITATION | Order after item aggregation | Item-bearing commercial orders |
| MET-006 | Observed Unique Customers | APPROVED_WITH_LIMITATION | Stable customer | Commercial population |
| MET-007 | Observed Repeat Customer Rate | APPROVED_WITH_LIMITATION | Stable customer/window | Commercial population |
| MET-008 | Average Delivery Lead Time | APPROVED | Order | Endpoint-complete delivered orders |
| MET-009 | Late Delivery Rate | APPROVED | Order | Endpoint-complete delivered orders |
| MET-010 | Average Order-Level Review Score | APPROVED_WITH_LIMITATION | Review events → order | All reviewed orders |
| MET-011 | Item Volume | APPROVED | Order item | Commercial population |
| MET-012 | Freight Value | APPROVED_WITH_LIMITATION | Order item | Commercial population |
| MET-013 | Freight Burden | APPROVED_WITH_LIMITATION | Aggregated item population | Commercial population |
| MET-014 | Recorded Payment Value | APPROVED_WITH_LIMITATION | Payment sequence | All statuses with payment rows |
| MET-015 | On-time Delivery Rate | APPROVED | Order | Same denominator as MET-009 |

## MET-001 — Total Orders

- **Purpose/definition:** Count distinct source orders placed in the reporting period, regardless of lifecycle outcome.
- **Formula/numerator:** `COUNT(DISTINCT orders.order_id)`; no denominator.
- **Sources/grain/key:** orders; order grain; `order_id`.
- **Population:** all eight statuses. Orders without items/payments/reviews remain included.
- **Date:** `order_purchase_timestamp`; no fallback.
- **Null/zero/repeats:** order ID/date required; source key must remain unique; zero not applicable.
- **DQ/geography/category:** DQ-001/003/005/008/016. Geography/category grouping must obey global policies.
- **Reconciliation/acceptance:** exact distinct-order equality to identically filtered source orders; column/key/date/population tests pass.
- **Format/terminology:** whole number, `#,##0`; “Total Orders,” never “Delivered Orders.”
- **Limitation/status:** Includes canceled/unavailable/incomplete orders by design. **APPROVED**.

## MET-002 — Delivered Status Orders

- **Purpose/definition:** Count distinct orders whose source status equals `delivered`.
- **Formula:** `COUNT(DISTINCT order_id WHERE order_status='delivered')`.
- **Sources/grain/key:** orders; order; `order_id`.
- **Population:** delivered status only. Actual-delivery timestamp is not required because this is a status metric.
- **Date/nulls:** purchase timestamp; order/status/date required; no fallback.
- **DQ:** DQ-003/008/009. Eight status-delivered orders without actual timestamp remain counted.
- **Reconciliation:** exact distinct delivered-status order count from orders.
- **Format/terminology:** whole number; “Delivered Status Orders,” not “Delivery-Complete Orders.”
- **Limitation/status:** Does not certify endpoint completeness. **APPROVED**.

## MET-003 — Product GMV

- **Purpose/definition:** Item selling-price value for lifecycle-active commercial orders; freight excluded.
- **Formula/numerator:** `SUM(order_items.price)`; no denominator.
- **Sources/columns:** orders (`order_id`, status, purchase timestamp); items (`order_id`, `order_item_id`, `price`).
- **Grain/key:** native item grain; `order_id + order_item_id`.
- **Population:** commercial statuses; exclude created/canceled/unavailable; require item row.
- **Null/zero/repeats:** price/key/date required; no imputation; zero price would be retained and warned; item key unique.
- **DQ/policies:** DQ-007/008/012/015/016; category/geography global rules; never pass through payment join.
- **Reconciliation:** independent eligible source `price` sum; tolerance 0.01 currency unit.
- **Format/terminology:** source currency, two decimals; “Product GMV.” Explicitly not revenue, recognized revenue, net sales, cash received, or profit.
- **Limitation/status:** Refunds, returns, costs, and recognition events are unavailable. **APPROVED_WITH_LIMITATION**.

## MET-004 — Gross Order Value

- **Definition/formula:** Sum of `price + freight_value` over the MET-003 item population.
- **Numerator/denominator:** `SUM(price + freight_value)`; none.
- **Sources/grain/population/date/key:** same as MET-003; item grain; purchase date.
- **Null/zero:** both components required; zero freight included.
- **DQ/safe path:** DQ-007/008/015/016; independent item fact only.
- **Reconciliation:** item-source component sum, tolerance 0.01.
- **Format/terminology:** source currency; “Gross Order Value,” not payment value, revenue, or profit.
- **Limitation/status:** Same refund/recognition limitation as Product GMV. **APPROVED_WITH_LIMITATION**.

## MET-005 — Average Order Value (Product GMV)

- **Definition:** Mean order-level Product GMV among eligible commercial orders represented by at least one eligible item.
- **Formula:** `SUM(order-level Product GMV) / COUNT(DISTINCT eligible item-bearing order_id)`.
- **Sources/grain:** items independently aggregated to order, then reporting group; order key.
- **Population/date:** MET-003 statuses; purchase date; itemless orders excluded only here and coverage disclosed.
- **Null/zero:** valid item price required; zero-value eligible order would remain; zero denominator returns null/NA.
- **DQ/safe path:** DQ-007/008/015/016; item-to-order pre-aggregation mandatory.
- **Reconciliation:** numerator to MET-003 source control, denominator to independent distinct eligible item-bearing order control.
- **Format/terminology:** source currency, two decimals; freight exclusion shown in name/tooltip.
- **Limitation/status:** Not average payment or revenue. **APPROVED_WITH_LIMITATION**.

## MET-006 — Observed Unique Customers

- **Definition/formula:** Distinct stable customers with at least one commercial-population order in the reporting period; `COUNT(DISTINCT customer_unique_id)`.
- **Sources/key/grain:** orders joined 1:1 to customers by `customer_id`; calculate at `customer_unique_id` grain.
- **Population/date:** commercial statuses; purchase timestamp.
- **Null/repeats:** stable ID/order/date required; multiple `customer_id` records per stable identity collapse only through distinct stable ID.
- **DQ:** DQ-005/008/011/016/018; customer geography only.
- **Reconciliation:** independent distinct `customer_unique_id` after eligible source join; exact equality.
- **Format/terminology:** whole number; controlled display name “Observed Unique Customers.”
- **Limitation/status:** Not all historical or lifetime customers; censoring applies. **APPROVED_WITH_LIMITATION**.

## MET-007 — Observed Repeat Customer Rate

- **Definition:** Share of stable customers with at least two distinct eligible orders in the declared observation window among stable customers with at least one.
- **Numerator:** distinct `customer_unique_id` with `COUNT(DISTINCT eligible order_id) >= 2`.
- **Denominator:** distinct `customer_unique_id` with at least one eligible order in the same window.
- **Sources/grain/key:** orders/customers; stable customer over fixed window; `customer_unique_id`.
- **Population/date:** commercial statuses; purchase timestamp; identical window for numerator/denominator.
- **Null/zero:** IDs/dates required; zero denominator returns null/NA.
- **DQ:** DQ-008/011/016/018; no cohort/RFM implementation here.
- **Reconciliation:** rebuild customer-level distinct-order counts; numerator ≤ denominator; exact counts.
- **Format/terminology:** percentage, one decimal by default; “Observed Repeat Customer Rate,” never retention or lifetime repeat rate.
- **Limitation/status:** Unequal customer exposure and right-censoring are unadjusted and mandatory disclosures. **APPROVED_WITH_LIMITATION**.

## MET-008 — Average Delivery Lead Time

- **Definition:** Mean elapsed fractional days from purchase to actual customer delivery.
- **Formula:** `AVG(order_delivered_customer_date - order_purchase_timestamp)` in days.
- **Numerator/denominator:** sum eligible durations / eligible order count.
- **Population:** status delivered; both endpoints present; delivery ≥ purchase. Eight missing-actual orders excluded only here.
- **Date/grain/key:** purchase-cohort attribution; order grain; `order_id`.
- **Null/zero/chronology:** no endpoint imputation; zero-day valid; negative duration metric-ineligible and warned. Approval/carrier reversals do not affect endpoints.
- **DQ:** DQ-005/006/008/009/016.
- **Reconciliation:** independently recompute eligible count and total duration; exact count, `1e-9` day pre-round tolerance.
- **Format:** days, two decimals; median may be a diagnostic only.
- **Limitation/status:** Mean is tail-sensitive; timestamps timezone-naive. **APPROVED**.

## MET-009 — Late Delivery Rate

- **Definition:** Share of endpoint-complete delivered orders with actual delivery later than estimate.
- **Numerator:** count where `actual_delivery > estimated_delivery`.
- **Denominator:** delivered orders with valid purchase, actual, and estimate timestamps and actual ≥ purchase.
- **Population/date/grain:** delivered; purchase cohort; order.
- **Null/zero/equality:** missing endpoints excluded/disclosed; zero denominator null/NA; equality is on-time.
- **DQ:** DQ-005/006/008/009/016. Lateness is a business outcome, not a DQ defect.
- **Reconciliation:** exact source numerator/denominator; `0 ≤ numerator ≤ denominator`.
- **Format/terminology:** percentage, one decimal; “Late Delivery Rate.”
- **Limitation/status:** Measures estimate adherence, not causal service quality. **APPROVED**.

## MET-010 — Average Order-Level Review Score

- **Definition:** Unweighted mean of order-level mean review scores, so each reviewed order contributes equal portfolio weight.
- **Formula:** first `AVG(review_score)` per `order_id` over all matched source review rows, then `AVG(order_level_mean)`.
- **Numerator/denominator:** sum order-level means / distinct reviewed orders.
- **Population:** all statuses with ≥1 matched review and valid score 1–5.
- **Date/grain/key:** parent purchase date; review events → order → reporting group; preserve every source review row.
- **Null/repeats:** invalid/null score excluded/disclosed; unreviewed orders excluded and coverage disclosed; no first/latest/highest selection.
- **DQ:** DQ-002/008/010/016; review-date view secondary only.
- **Reconciliation:** independently reproduce per-order means, verify one aggregate row per order and exact denominator.
- **Format:** score, two decimals, valid displayed range 1–5.
- **Limitation/status:** The order mean is an analytical construction; canonical revision semantics are unavailable. **APPROVED_WITH_LIMITATION**.

## MET-011 — Item Volume

- **Definition/formula:** Count validated item keys for commercial-population orders: `COUNT(order_id + order_item_id)`.
- **Sources/grain/population/date:** items/order; item grain; commercial statuses; purchase date.
- **Null/repeats:** key required and unique; zero not applicable.
- **DQ/reconciliation:** DQ-002/003/008/016; exact eligible source item-key count.
- **Format/terminology:** whole number; “Item Lines” may be used in technical tooltips because source lacks a separate quantity field.
- **Limitation/status:** Item lines are not independently proven physical unit quantities. **APPROVED**.

## MET-012 — Freight Value

- **Definition/formula:** Sum recorded `freight_value` over MET-003 item population.
- **Sources/grain/population/date:** items/order; item grain; commercial statuses; purchase date.
- **Null/zero:** valid numeric required; 383 zero freight rows retained.
- **DQ/safe path:** DQ-007/008/015/016; item fact only.
- **Reconciliation:** independent eligible item freight sum; tolerance 0.01.
- **Format/terminology:** source currency; “Freight Value,” not carrier cost.
- **Limitation/status:** Source value is not validated logistics cost or profit impact. **APPROVED_WITH_LIMITATION**.

## MET-013 — Freight Burden

- **Definition/formula:** `SUM(freight_value) / SUM(price + freight_value)` over identical MET-003 population.
- **Grain:** aggregate item components before division; never average row-level ratios.
- **Population/date/key:** commercial item population; purchase date; validated item key.
- **Null/zero:** components required; zero freight included; zero denominator returns null/NA.
- **DQ:** DQ-007/008/015/016.
- **Reconciliation:** numerator and denominator independently reconcile to MET-012 and MET-004 source controls.
- **Format/terminology:** percentage, one decimal; “Freight Burden.”
- **Limitation/status:** Recorded freight value is not economic cost. **APPROVED_WITH_LIMITATION**.

## MET-014 — Recorded Payment Value

- **Definition:** Sum source payment-sequence values independently of item values.
- **Formula:** `SUM(order_payments.payment_value)`; no denominator.
- **Sources/grain/key:** payments plus orders for purchase date/status; payment sequence; `order_id + payment_sequential`.
- **Population:** all statuses with payment rows; missing-payment orders absent and coverage disclosed.
- **Date/null/zero:** purchase date; valid key/value/date; nine zero values retained and warned.
- **DQ/safe path:** DQ-007/008/015/016; never aggregate through item join.
- **Reconciliation:** independent payment-grain sum under identical order/date filter; tolerance 0.01.
- **Format/terminology:** source currency; controlled name “Recorded Payment Value.” Never describe it as Product GMV, revenue, recognized revenue, cash received, net sales, or net of refunds/chargebacks.
- **Limitation/status:** Settlement/refund/chargeback metadata is unavailable. **APPROVED_WITH_LIMITATION**.

## MET-015 — On-time Delivery Rate

- **Definition:** Share of the exact MET-009 denominator delivered on or before estimate.
- **Numerator/formula:** count where `actual_delivery <= estimated_delivery`; denominator identical to MET-009.
- **Sources/grain/population/date:** orders; order; endpoint-complete delivered; purchase cohort.
- **Null/zero:** same as MET-009; zero denominator null/NA.
- **DQ:** DQ-005/006/008/009/016.
- **Reconciliation:** on-time numerator + late numerator = shared denominator; unrounded rates sum to 100%.
- **Format/terminology:** percentage, one decimal; “On-time Delivery Rate.”
- **Limitation/status:** Complement only under identical population; not causal. **APPROVED**.

## Contract change control

The machine-readable implementation contract is `reports/metric-contract/metric-decision-register.csv`. If it conflicts with this specification, stop and resolve the specification through approval before implementation. No profitability metric is authorized.
