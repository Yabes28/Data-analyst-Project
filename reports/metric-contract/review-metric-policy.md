# Review Metric Policy

## Decision

MET-010, **Average Order-Level Review Score**, uses **Policy B: order-level mean review score**. Preserve all source review rows; calculate a mean score per `order_id`; then calculate an unweighted mean across reviewed orders. Status is `APPROVED_WITH_LIMITATION`.

## Alternatives considered

- Review-event average was rejected as the primary KPI because orders with multiple rows receive greater weight.
- Single-record selection was rejected because no revision/version flag supports first/latest/highest selection.
- Order-level mean gives every reviewed order equal weight and preserves all associated scores, but it is an analytical construction rather than a source canonical record.

All statuses may contribute when a matched valid score exists. Unreviewed orders are excluded from the score denominator and review coverage must be disclosed. The primary reporting date is parent order purchase date; review creation date may support a secondary event view only.
