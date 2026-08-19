# Phase 5 SQL Findings

These are validated descriptive SQL findings, not final recommendations.

## Executive Performance

### FIND-001

**Finding:** Among calendar-complete months, 2017-11-01 had the highest observed Product GMV at BRL 1,003,862.14.

**Evidence:** Product GMV=1003862.14

**Population:** commercial item population (denominator: 7544).

**Period:** 2017-11-01

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Boundary months excluded; descriptive observation window.

**Traceability:** AN-001 / SQL-003 / MET-003; SQL: `sql/analysis/02_trends/monthly_trends.sql`.

## Customers

### FIND-002

**Finding:** 92,099 of 94,986 commercial customers placed exactly one eligible order; the governed observed repeat rate was 3.04%.

**Evidence:** one-order customers=92099; repeat rate=0.030393952793043185

**Population:** commercial customers in observed window (denominator: 94986).

**Period:** 2016-09-04 to 2018-10-17

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Not retention or lifetime behavior; unequal exposure.

**Traceability:** AN-003 / SQL-004 / MET-007; SQL: `sql/analysis/03_customers/customer_frequency.sql`.

## Categories

### FIND-003

**Finding:** health_beauty ranked first by eligible Product GMV at BRL 1,255,695.13; the top five categories represented 39.82% of eligible Product GMV.

**Evidence:** top category=1255695.13; top-5 share=0.3982323812328105

**Population:** commercial item population (denominator: 9634).

**Period:** full observed window

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Category outcomes have metric-specific denominators.

**Traceability:** AN-006 / SQL-005 / MET-003; SQL: `sql/analysis/04_categories/category_performance.sql`.

## Sellers

### FIND-004

**Finding:** The leading seller represented 1.70% of eligible Product GMV, while the top ten represented 13.20%.

**Evidence:** top seller share=0.016987610966709737; top-10 share=0.13203773137687191

**Population:** commercial item population (denominator: 1155).

**Period:** full observed window

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Concentration does not establish dependency or market power; no best/worst claim.

**Traceability:** AN-007 / SQL-006 / MET-003; SQL: `sql/analysis/05_sellers/seller_performance.sql`.

## Delivery

### FIND-005

**Finding:** Across 96,470 endpoint-qualified delivered orders, average lead time was 12.56 days and 8.11% arrived after estimate.

**Evidence:** mean days=12.558217098052024; late rate=0.08112366538820359

**Population:** endpoint-complete delivered orders (denominator: 96470).

**Period:** full purchase-cohort window

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Timezone-naive timestamps; mean is tail-sensitive.

**Traceability:** AN-008 / SQL-007 / MET-008; SQL: `sql/analysis/06_delivery/delivery_performance.sql`.

## Customer Experience

### FIND-006

**Finding:** Reviewed late orders averaged 2.57, versus 4.29 for reviewed on-time orders, an observed difference of -1.73 points.

**Evidence:** late eligible=7826; late reviewed=7661; late mean=2.566505678109907; on-time eligible=88644; on-time reviewed=88163; on-time mean=4.294292012144172

**Population:** endpoint-qualified delivered orders with reviewed subsets (denominator: late eligible=7826; late reviewed=7661; on-time eligible=88644; on-time reviewed=88163).

**Period:** full purchase-cohort window

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Observed association; does not establish causality.

**Traceability:** AN-010 / SQL-008 / MET-010; SQL: `sql/analysis/07_customer_experience/review_delivery_comparison.sql`.

## Geography

### FIND-007

**Finding:** Customer State SP had the largest eligible Product GMV at BRL 5,163,867.22, across 41,126 commercial orders.

**Evidence:** Product GMV=5163867.22; customers=39748

**Population:** commercial orders by order-associated Customer State (denominator: 41126).

**Period:** full observed window

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Order-associated geography is not permanent customer residence.

**Traceability:** AN-002 / SQL-009 / MET-003; SQL: `sql/analysis/08_geography/customer_state_performance.sql`.

## Payments/Freight

### FIND-008

**Finding:** credit_card represented 78.34% of Recorded Payment Value across 76,795 payment records.

**Evidence:** recorded value=12542084.19; share=0.7834458352834915

**Population:** all payment rows/statuses (denominator: 76795).

**Period:** full observed window

**Interpretation:** The data supports this descriptive pattern.

**Limitation:** Recorded Payment Value is not revenue, cash received, or net sales.

**Traceability:** AN-011 / SQL-010 / MET-014; SQL: `sql/analysis/09_payments/payment_summary.sql`.
