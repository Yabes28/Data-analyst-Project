# Safe Join Contract

1. Orders to customers is safe by `customer_id` at one order-associated customer record per order. Stable customer analysis groups by `customer_unique_id` afterward.
2. Orders to order items is 1:M. Item measures stay at `order_id + order_item_id` until deliberately pre-aggregated.
3. Orders to payments is 1:M. Payment measures stay at `order_id + payment_sequential` or are independently pre-aggregated.
4. Never join item rows to payment rows and then aggregate price, freight, or payment value.
5. Review rows are aggregated to one order-level mean for MET-010 while retaining event count/coverage; no row-selection deduplication.
6. Raw geolocation is never directly joined to customer, seller, order, item, payment, or review facts.
7. Product category translation uses a left join. Missing/untranslated categories remain explicit.
8. Order-level outcomes must not be attributed to an individual seller in multi-seller orders without a separately approved allocation rule.
9. Every implementation join records pre/post row counts, distinct keys, unmatched keys, and monetary source controls.

These are Phase 4 modeling constraints, not a model implementation.

