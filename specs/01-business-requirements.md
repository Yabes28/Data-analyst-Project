# Business Requirements

**Status:** Draft — validate feasibility after source inspection.  
**Traceability:** Each implemented analysis must cite one or more IDs below.

## Commerce performance

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-001 | Measure order volume and delivered-order volume over a validated time grain. | Monitor demand and fulfillment throughput. | Must |
| BR-002 | Measure product GMV, gross order value, and average order value using governed definitions. | Evaluate commercial scale without implying profit. | Must |
| BR-003 | Compare monthly trends and period-over-period change only across complete, comparable periods. | Identify growth, decline, and seasonality signals. | Must |
| BR-004 | Compare demand and value by customer geography where geography quality supports it. | Identify market concentration and service needs. | Should |

## Customers

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-005 | Count unique customers using the validated stable customer identifier. | Establish customer reach. | Must |
| BR-006 | Measure repeat purchase behavior and purchase-frequency distribution. | Understand retention opportunity. | Must |
| BR-007 | Evaluate acquisition cohorts and repeat behavior when observation-window bias can be disclosed. | Compare customer development over time. | Should |
| BR-008 | Evaluate RFM-style segmentation only if recency anchor, eligible orders, and segment rules are defensible. | Prioritize customer engagement hypotheses. | Could |

## Products and categories

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-009 | Rank categories by product GMV, order volume, item volume, and average order value. | Identify commercial mix and concentration. | Must |
| BR-010 | Compare category freight burden and review outcomes using grain-safe aggregates. | Surface high-friction categories. | Should |
| BR-011 | Preserve unmapped/unknown categories rather than silently dropping them. | Make coverage limitations visible. | Must |

## Sellers

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-012 | Measure seller concentration by product GMV and fulfilled item/order volume. | Understand seller dependency. | Must |
| BR-013 | Compare seller commercial scale, delivery outcomes, and review outcomes with minimum-volume context. | Identify monitoring and enablement candidates. | Should |
| BR-014 | Avoid attributing order-level outcomes to an individual seller when an order contains multiple sellers unless allocation is specified. | Prevent misleading seller comparisons. | Must |

## Delivery and logistics

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-015 | Measure delivery lead time and late delivery rate for eligible delivered orders. | Monitor fulfillment performance. | Must |
| BR-016 | Compare delivery and freight outcomes by geography, category, and seller where attribution is valid. | Locate operational friction. | Should |
| BR-017 | Separate cancelled/unavailable/incomplete orders from delivered-order service metrics and report exclusions. | Maintain interpretable denominators. | Must |

## Customer experience

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-018 | Describe review-score distribution and average review score with coverage disclosed. | Monitor reported customer experience. | Must |
| BR-019 | Test whether late delivery is associated with lower review scores without causal language. | Identify an operational relationship worth action/testing. | Must |
| BR-020 | Compare experience across category, seller, and geography with coverage and sample-size safeguards. | Prioritize investigation. | Should |

## Cross-cutting

| ID | Requirement | Intended decision use | Priority |
|---|---|---|---|
| BR-021 | Reconcile major metrics to source-level control totals and document exclusions. | Establish trust. | Must |
| BR-022 | Make definitions, filters, grain, null handling, limitations, and requirement lineage visible. | Enable reproducibility and review. | Must |

