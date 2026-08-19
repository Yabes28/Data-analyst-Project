# Analysis Specification

**Status:** Phase 5 approved SQL-analysis specification. Metric formulas remain governed by `specs/04-metric-contract.md`.

| ID | Business question / rationale | BR | MET | MODEL | Calculation / reporting grain | Population and date basis | SQL method / output | DQ dependencies / limitations | Validation |
|---|---|---|---|---|---|---|---|---|---|
| AN-001 | How do governed commerce KPIs and comparable monthly periods change? | BR-001–BR-003 | MET-001–MET-005 | MODEL-001/002/009/010/012 | Order/item → portfolio and month | Metric-specific; purchase month; boundary months labeled | Conditional aggregation, `LAG`; core metrics and monthly trends | DQ-005/008/016/018; incomplete boundaries | Native-fact controls; completeness tests |
| AN-002 | How does observed demand vary by customer state? | BR-004 | MET-001/003/005/006 | MODEL-001/002/010/012 | Order/customer → customer state | Metric-specific; purchase timestamp | State aggregation, rank/share | DQ-011/014/018; order-associated geography | Independent totals and denominator checks |
| AN-003 | What purchase-frequency behavior is observed within the window? | BR-005–BR-006 | MET-006/007 | MODEL-001/006 | Stable customer → frequency group | Commercial population; full observed purchase window | Customer CTE, distribution, repeat grouping | DQ-011/018; not retention/lifetime | Distinct `customer_unique_id` reconciliation |
| AN-004 | Cohort retention | BR-007 | MET-006/007 | MODEL-001/006 | Acquisition cohort | Deferred to Phase 6 | Python-supported cohort assessment | Right censoring requires dedicated treatment | Deferred |
| AN-005 | RFM assessment | BR-008 | Governed components | MODEL-001/002 | Stable customer | Deferred to Phase 6 | Python stability assessment | Recency anchor and scoring not yet approved | Deferred |
| AN-006 | Which categories drive mix, concentration, freight burden, and experience? | BR-009–BR-011 | MET-003/005/011–013/010 | MODEL-002/005/007 | Item/order → category | Commercial items; reviewed/delivery subsets disclosed; purchase date | CTEs, rank, cumulative share | DQ-010/012/016; multi-category orders prevent portfolio AOV attribution | Native item totals and visible denominators |
| AN-007 | How concentrated is seller activity and how do seller outcomes compare with volume context? | BR-012–BR-014 | MET-003/008–010 | MODEL-001/002/005/008 | Item/order-seller | Commercial items; seller-attributable single-seller orders for order outcomes | CTEs, rank, cumulative share; denominator-aware comparison | Multi-seller outcomes excluded from seller outcome rates | Native item reconciliation; denominators exposed |
| AN-008 | What are delivery outcomes overall and by month/category/state? | BR-015–BR-017 | MET-008/009/015 | MODEL-001/012 | Endpoint-eligible delivered order | Approved endpoint population; purchase cohort date | Conditional aggregation and distribution summary | DQ-006/009; no imputation; tail-sensitive mean | Late + on-time = denominator |
| AN-009 | What is review coverage and score distribution? | BR-018/020 | MET-010 | MODEL-004/005/012 | Review events → reviewed order | All reviewed orders; purchase timestamp | Distribution and grouped averages | DQ-010/016; approved order mean | Reviewed-order count and score domain |
| AN-010 | Are late deliveries associated with lower review scores? | BR-019 | MET-009/010 | MODEL-001/005/012 | Endpoint-eligible reviewed order | Same delivery endpoint population, split late/on-time | Conditional aggregation; low score = order-level mean `<= 2` | Observational only; reviewed subset | Mutually exclusive groups and denominators |
| AN-011 | What payment and freight patterns are recorded? | BR-021–BR-022 | MET-012–014 | MODEL-002/003/011 | Payment sequence/order and item | Approved metric-specific populations; purchase timestamp | Independent aggregation, distributions, ratios | DQ-007/015/016; payment is not revenue, freight is not cost | Native-fact reconciliation; no item-payment join |

## Output rules

- Full precision is retained in calculation outputs; presentation text may round currency to two decimals, rates to two percentage points, and scores/days to two decimals.
- Every rate or average preserves its denominator. Ratios use `NULLIF(denominator, 0)`.
- A calendar scaffold preserves every month in the purchase window. Months with no purchases are `NO_OBSERVED_ACTIVITY` with NULL measures; observed months are `COMPLETE_PERIOD` only when purchases span calendar day 1 through month end and otherwise `PARTIAL_PERIOD`. MoM/YoY comparisons require calendar-aligned complete periods and cannot bridge gaps.
- Category trend selection uses the five categories with the highest full-window eligible Product GMV, determined before trend inspection.
- Seller commercial concentration includes all sellers. Seller delivery/review comparisons use seller-attributable single-seller orders and expose denominators; no best/worst label or arbitrary stability threshold is used.
- Low review score in AN-010 means an order-level mean review score `<= 2`. This transparent threshold aligns with the two lowest points of the source 1–5 scale and is not a causal classification.
- Findings may describe observed associations but cannot contain final recommendations.
