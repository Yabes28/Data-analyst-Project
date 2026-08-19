# Geography Policy

- Customer-demand/customer metrics use `customer_city` and `customer_state` from the order-associated customer record.
- Seller metrics use `seller_city` and `seller_state` from the seller source.
- Customer and seller geography must not be mixed or generically labeled “region” without identifying the entity.
- Raw geolocation observations must not be joined directly to facts or dimensions because ZIP prefixes are non-unique.
- Latitude/longitude analysis is dependent on a deterministic normalized geographic reference in Phase 4.
- Missing geographic values/coverage remain explicit and must not be silently dropped.

This policy avoids geolocation fanout while Phase 4 evaluates normalization.

