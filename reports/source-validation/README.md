# Phase 1 Source Validation Report

**Status:** Complete  
**Scope:** Source acquisition, schema, grain, key, relationship, and feasibility validation only. No business analysis was performed.  
**Evidence date:** 2026-08-19

Machine-readable evidence in this directory is regenerated with:

```powershell
python src/data/profile_sources.py
python src/validation/validate_keys.py
python src/validation/validate_relationships.py
```

The scripts use repository-relative paths, read raw CSVs without writing to them, and place outputs here.

## Source inventory and confirmed grains

| Table | File | Rows | Columns | Confirmed grain | Validated key | Duplicate behavior | Safe analytical role |
|---|---|---:|---:|---|---|---|---|
| customers | `olist_customers_dataset.csv` | 99,441 | 5 | One order-associated customer record | `customer_id` unique/non-null | No full-row or key duplicates | Join to orders 1:1 by `customer_id`; use `customer_unique_id` for stable person-level grouping. |
| geolocation | `olist_geolocation_dataset.csv` | 1,000,163 | 5 | One observed coordinate/city/state record for a ZIP prefix; repeated observations allowed | No tested source key is unique | 261,831 exact duplicate rows; 17,972 ZIP prefixes have multiple rows | Profile/normalize before any entity join; never direct-join raw rows to customers/sellers. |
| order_items | `olist_order_items_dataset.csv` | 112,650 | 7 | One sequential item line within an order | `order_id + order_item_id` unique/non-null | No full-row/key duplicates | Item/product/seller monetary fact at line grain. |
| payments | `olist_order_payments_dataset.csv` | 103,886 | 5 | One payment sequence record within an order | `order_id + payment_sequential` unique/non-null | No full-row/key duplicates | Payment fact; aggregate independently before any order-level combination with items. |
| reviews | `olist_order_reviews_dataset.csv` | 99,224 | 7 | One review event row linking a review ID and order ID | No unique single-column key; no approved canonical key | 789 review IDs and 547 order IDs occur in multiple rows; no exact full-row duplicates | Preserve events; canonical order-review rule must be approved before MET-010. |
| orders | `olist_orders_dataset.csv` | 99,441 | 8 | One order | `order_id` unique/non-null | No full-row/key duplicates | Order lifecycle fact and parent of items/payments/reviews. |
| products | `olist_products_dataset.csv` | 32,951 | 9 | One product | `product_id` unique/non-null | No full-row/key duplicates | Product attributes/dimension source. |
| sellers | `olist_sellers_dataset.csv` | 3,095 | 4 | One seller | `seller_id` unique/non-null | No full-row/key duplicates | Seller attributes/dimension source. |
| category_translation | `product_category_name_translation.csv` | 71 | 2 | One Portuguese category label and English label mapping | `product_category_name` unique/non-null | No full-row/key duplicates | Optional category label enrichment; unmatched categories must remain visible. |

The file sizes and SHA-256 values are in `file_manifest.csv`; complete column names are in `source_inventory.csv`.

## Relationship and cardinality validation

| Parent → child | Observed cardinality | Orphan child rows | Parent keys without child | Maximum child rows | Implication |
|---|---|---:|---:|---:|---|
| customers → orders (`customer_id`) | 1:1 | 0 | 0 | 1 | The order-associated `customer_id` is not a repeat-customer identity. |
| orders → order_items (`order_id`) | 1:M | 0 | 775 | 21 | Some orders have no item row; status/eligibility requires later disposition. |
| orders → payments (`order_id`) | 1:M | 0 | 1 | 29 | Payment values multiply if joined to item rows. |
| orders → reviews (`order_id`) | 1:M | 0 | 768 | 3 | Review scores/coverage require a canonical rule or event-grain reporting. |
| products → order_items (`product_id`) | 1:M | 0 | 0 | 527 | All item product keys match. |
| sellers → order_items (`seller_id`) | 1:M | 0 | 0 | 2,033 | All item seller keys match. |
| category translation → products (category) | 1:M with unmatched children | 13 product rows | 0 used mappings absent | 3,029 | Two source category values lack translations. |

`relationship_validation.csv` contains the machine-readable results. Parent-without-child counts are coverage facts, not automatic defects.

## Customer identity (DATA-005 / DQ-011)

- `customer_id` is unique in customers and is linked to exactly one order; no `customer_id` maps to multiple `customer_unique_id` values.
- `customer_unique_id` has 96,096 distinct values across 99,441 customer records.
- 2,997 `customer_unique_id` values map to multiple `customer_id` values; the maximum is 17.

Conclusion: the observed relational structure validates `customer_id` as an order-associated customer record identifier and `customer_unique_id` as the stable cross-order customer identity for future customer-level analysis. Eligibility rules and observation-window bias remain Phase 3/6 concerns.

## Item/payment fanout (DQ-015)

For an order with `I` item rows and `P` payment rows, a direct join produces `I × P` rows. Each item measure repeats `P` times and each payment measure repeats `I` times.

- 98,665 orders appear in both facts.
- 9,802 have multiple item rows; 2,936 have multiple payment rows; 275 have both.
- The direct join creates 117,601 rows versus 112,647 item rows and 103,056 payment rows for the overlapping orders.
- Demonstration totals: item price changes from 13,591,508.73 at native item grain to 14,209,115.34 after the naïve join; payment value changes from 15,846,280.17 at native payment grain to 20,308,134.71.

These are validation controls, not business KPIs. Phase 4 must either keep separate facts or aggregate both independently to order grain before joining. Arbitrary deduplication is prohibited.

## Order status and timestamps (DATA-006–DATA-007)

| Status | Orders | Share | Approved timestamp | Carrier timestamp | Customer-delivery timestamp |
|---|---:|---:|---:|---:|---:|
| delivered | 96,478 | 97.0203% | 96,464 | 96,476 | 96,470 |
| shipped | 1,107 | 1.1132% | 1,107 | 1,107 | 0 |
| canceled | 625 | 0.6285% | 484 | 75 | 6 |
| unavailable | 609 | 0.6124% | 609 | 0 | 0 |
| invoiced | 314 | 0.3158% | 314 | 0 | 0 |
| processing | 301 | 0.3027% | 301 | 0 | 0 |
| created | 5 | 0.0050% | 0 | 0 | 0 |
| approved | 2 | 0.0020% | 2 | 0 | 0 |

All non-null configured timestamps parsed successfully. The observed purchase window is 2016-09-04 21:15:19 through 2018-10-17 17:30:18; the estimated-delivery window extends to 2018-11-12.

Chronology controls found no purchase-after-approval or purchase-after-customer-delivery records. They found 1,359 approval-after-carrier timestamps, 23 carrier-after-customer-delivery timestamps, eight delivered-status orders missing customer delivery, and six non-delivered-status orders with a customer-delivery timestamp. These require Phase 2 classification; no rows were deleted. Timestamp timezone is not supplied by the files and remains unknown.

## Reviews (DQ-010)

- 99,224 rows, 98,410 distinct `review_id` values, and 98,673 distinct `order_id` values.
- 789 review IDs link to multiple orders; 547 orders contain multiple distinct review IDs; maximum multiplicity is three.
- There are no exact duplicate full rows, no null review scores/timestamps, and no answer-before-creation timestamps.
- Scores parse as numeric and range from 1 to 5.
- Comment titles are 88.34% null and messages are 58.70% null; these optional-text nulls do not invalidate the score.

The source does not contain an explicit revision/version indicator. Phase 1 therefore cannot prove whether repeated relationships are revisions, reuse, or another source behavior. No deduplication rule is approved.

## Geolocation (DATA-008 / DQ-013)

- 1,000,163 rows cover 19,015 ZIP prefixes.
- 17,972 prefixes have multiple rows; maximum rows per prefix is 1,146.
- 8,556 prefixes map to multiple city strings, eight to multiple states, and 17,781 to multiple coordinate pairs.
- 278 customer rows (157 distinct prefixes) and seven seller rows (seven prefixes) have no geolocation match.
- Observed coordinates extend beyond plausible Brazil bounds; these are investigation flags, not automatic removal rules.

Phase 4 options: aggregate coordinates deterministically by ZIP prefix (for example, median latitude/longitude plus explicit city/state conflict rules), select a deterministic modal city/state with tie-breaking, or omit coordinate enrichment and retain customer/seller city/state. The raw geolocation table must never be joined directly to facts.

## Categories (DQ-012)

- Products contain 73 non-null Portuguese category values; translation contains 71 unique mappings.
- 610 products have a missing category.
- `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos` are untranslated, affecting 13 product rows in total.
- No translation value is unused by the products table.

Missing/untranslated values must remain explicit; no translation was fabricated.

## Monetary and numeric validation (DQ-007)

| Field | Null | Zero | Negative | Minimum | Maximum | Phase 1 interpretation |
|---|---:|---:|---:|---:|---:|---|
| `order_items.price` | 0 | 0 | 0 | 0.85 | 6,735.00 | Calculable at item grain; extreme values need contextual Phase 2 review, not automatic exclusion. |
| `order_items.freight_value` | 0 | 383 | 0 | 0.00 | 409.68 | Zero is an observed condition requiring classification. |
| `payments.payment_value` | 0 | 9 | 0 | 0.00 | 13,664.08 | Payment fact is calculable; zero values require classification. |
| `payments.payment_installments` | 0 | 2 | 0 | 0 | 24 | Zero installments require interpretation against payment type. |

No configured numeric field produced parse failures. Product dimensional measurements include two null rows and four zero weights; these remain unchanged.

## Source license and attribution (DATA-009)

The Kaggle dataset page identifies the dataset as the Brazilian E-Commerce Public Dataset by Olist, describes it as anonymized commercial data, and lists the license as **CC BY-NC-SA 4.0**. Portfolio publication must attribute Olist/Kaggle, remain non-commercial unless separately authorized, identify adaptations, and apply compatible share-alike terms where required. License interpretation should be rechecked at publication time.

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Phase 2 handoff

Phase 2 should classify—not automatically remove—the chronology exceptions, missing lifecycle dates by status, orders without items/payments/reviews, repeated review relationships, geolocation conflicts/out-of-range coordinates, missing/untranslated categories, zero monetary/installment values, and product-dimension nulls/zeros. Thresholds and analytical exclusions require documented approval.

