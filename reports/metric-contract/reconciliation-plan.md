# Metric Reconciliation Plan

| Metrics | Independent source control | Expected grain | Tolerance / pass condition | Known exception |
|---|---|---|---|---|
| MET-001 | Distinct eligible `orders.order_id` | Order | Exact equality | Child-table absence does not change count. |
| MET-002 | Distinct delivered-status order IDs | Order | Exact equality | Missing actual delivery remains included. |
| MET-003 | Eligible item `SUM(price)` | Item | 0.01 currency unit | No payment join. |
| MET-004 | Eligible item `SUM(price + freight)` | Item | 0.01 | No payment join. |
| MET-005 | MET-003-independent source numerator and distinct eligible item-bearing orders | Order | Numerator 0.01; denominator exact | Itemless orders excluded. |
| MET-006 | Distinct eligible source `customer_unique_id` | Stable customer | Exact equality | Observation-window limitation. |
| MET-007 | Independent eligible distinct-order counts per stable customer | Customer/window | Numerator/denominator exact; numerator ≤ denominator | Unequal exposure disclosed. |
| MET-008 | Eligible order count and sum of source endpoint durations | Order | Count exact; duration `1e-9` day pre-round | Missing endpoints excluded. |
| MET-009 | Independent late numerator and eligible delivered denominator | Order | Exact; `0 ≤ numerator ≤ denominator` | Missing actual delivery excluded. |
| MET-010 | Rebuilt per-order means plus distinct reviewed orders | Order-review aggregate | Denominator exact; mean within floating precision | Analytical order-mean policy. |
| MET-011 | Eligible validated item-key count | Item | Exact equality | Source lines, not proven quantity. |
| MET-012 | Eligible item `SUM(freight_value)` | Item | 0.01 | Zero freight included. |
| MET-013 | Independently reconciled MET-012/MET-004 components | Reporting aggregate | Components 0.01; formula exact pre-round | Zero denominator returns null. |
| MET-014 | Eligible payment-grain `SUM(payment_value)` | Payment sequence | 0.01 | Zero values included; no item join. |
| MET-015 | Shared MET-009 denominator; on-time + late = denominator | Order | Exact counts; unrounded rates total 100% | Equality classified on-time. |

Controls must query native sources independently from the analytical model so they do not share the same error path.

