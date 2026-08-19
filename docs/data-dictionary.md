# Source Data Dictionary

**Status:** Phase 1 source-validated  
**Evidence:** `reports/source-validation/column_profile.csv` and original CSV headers  
**Typing convention:** Raw files are initially read as strings. “Int/decimal/datetime” below means conversion was tested with zero parse failures for non-null values; timestamps contain no timezone metadata.

## Customers — 99,441 rows

Grain: one order-associated customer record. Key: `customer_id` (unique, non-null).

| Column | Observed semantic type | Nullable | Key role | Evidence-backed meaning / caveat |
|---|---|---:|---|---|
| `customer_id` | string | No | PK; FK from orders | Order-associated customer record ID; each value links to one order, so it is not the stable repeat-customer identity. |
| `customer_unique_id` | string | No | Stable customer grouping key | Cross-order customer identity supported by repeated mappings to different `customer_id` values. Eligibility/window rules remain separate. |
| `customer_zip_code_prefix` | integer-like | No | Geographic reference | ZIP-code prefix; 157 distinct values have no raw geolocation match. Preserve leading-prefix semantics when modeling. |
| `customer_city` | string | No | Attribute | Source city label; spelling/normalization not yet classified. |
| `customer_state` | string | No | Attribute | Source state abbreviation/domain; categorical consistency is Phase 2. |

## Geolocation — 1,000,163 rows

Grain: one observed coordinate/city/state record for a ZIP prefix. No tested unique key; raw source is not a ZIP dimension.

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `geolocation_zip_code_prefix` | integer-like | No | Repeating lookup field | 19,015 values; 17,972 repeat, up to 1,146 rows. |
| `geolocation_lat` | decimal | No | Attribute | Latitude observation; extreme values require Phase 2 classification. |
| `geolocation_lng` | decimal | No | Attribute | Longitude observation; extreme values require Phase 2 classification. |
| `geolocation_city` | string | No | Attribute | City observation; 8,556 ZIP prefixes have multiple city strings. |
| `geolocation_state` | string | No | Attribute | State observation; eight ZIP prefixes span multiple states. |

## Order items — 112,650 rows

Grain: one sequential item line within an order. Key: `order_id + order_item_id` (unique, non-null).

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `order_id` | string | No | Composite PK; FK to orders | Parent order; repeats for multi-item orders. |
| `order_item_id` | integer | No | Composite PK | Sequential line identifier within order; observed 1–21. |
| `product_id` | string | No | FK to products | All values match a product. |
| `seller_id` | string | No | FK to sellers | All values match a seller. |
| `shipping_limit_date` | datetime | No | Lifecycle attribute | Seller shipping-limit timestamp according to dataset semantics; observed range extends to 2020 and requires Phase 2 investigation. |
| `price` | decimal | No | Measure | Item selling price; excludes freight; range 0.85–6,735.00. Not cost, profit, or recognized revenue. |
| `freight_value` | decimal | No | Measure | Item-line freight charged/value; 383 zeros; range 0–409.68. Not validated logistics cost. |

## Payments — 103,886 rows

Grain: one payment sequence record within an order. Key: `order_id + payment_sequential` (unique, non-null).

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `order_id` | string | No | Composite PK; FK to orders | Parent order; repeats when an order has multiple payment records. |
| `payment_sequential` | integer | No | Composite PK | Payment sequence within order; observed 1–29. |
| `payment_type` | string | No | Attribute | Source payment-method category; domain profiling belongs to Phase 2. |
| `payment_installments` | integer | No | Attribute | Installment count; observed 0–24, including two zero values requiring classification. |
| `payment_value` | decimal | No | Measure | Payment-record value; nine zeros; range 0–13,664.08. Must not be aggregated after an item-grain join. |

## Reviews — 99,224 rows

Grain: one source review event row linking a review ID and order. Neither `review_id` nor `order_id` is unique; no canonical key is approved.

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `review_id` | string | No | Repeating identifier | 98,410 distinct; 789 IDs link to multiple orders. |
| `order_id` | string | No | FK to orders | 98,673 distinct; 547 orders have multiple distinct review IDs. |
| `review_score` | integer | No | Measure | Score domain observed as 1–5. Canonical aggregation remains unresolved. |
| `review_comment_title` | string | Yes | Optional attribute | 87,656 nulls (88.34%). Text is anonymized per dataset documentation. |
| `review_comment_message` | string | Yes | Optional attribute | 58,247 nulls (58.70%). Text is anonymized per dataset documentation. |
| `review_creation_date` | datetime | No | Event timestamp | Observed 2016-10-02 through 2018-08-31. |
| `review_answer_timestamp` | datetime | No | Event timestamp | Observed 2016-10-07 through 2018-10-29; no answer-before-creation records. |

## Orders — 99,441 rows

Grain: one order. Key: `order_id` (unique, non-null).

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `order_id` | string | No | PK; parent of items/payments/reviews | Stable order identifier. |
| `customer_id` | string | No | FK to customers | 1:1 relationship to order-associated customer records. |
| `order_status` | string | No | Lifecycle attribute | Eight observed values: approved, canceled, created, delivered, invoiced, processing, shipped, unavailable. Final metric eligibility is Phase 3. |
| `order_purchase_timestamp` | datetime | No | Event timestamp | Order placement timestamp; observed 2016-09-04 to 2018-10-17. |
| `order_approved_at` | datetime | Yes | Event timestamp | Approval timestamp; 160 nulls. |
| `order_delivered_carrier_date` | datetime | Yes | Event timestamp | Carrier handoff timestamp; 1,783 nulls. |
| `order_delivered_customer_date` | datetime | Yes | Event timestamp | Customer delivery timestamp; 2,965 nulls. Eight delivered orders lack it; six non-delivered orders contain it. |
| `order_estimated_delivery_date` | datetime | No | Estimate timestamp | Promised/estimated customer delivery date; observed through 2018-11-12. |

## Products — 32,951 rows

Grain: one product. Key: `product_id` (unique, non-null). Source preserves misspelled `lenght` column names.

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `product_id` | string | No | PK; FK from items | Product identifier. |
| `product_category_name` | string | Yes | FK-like translation field | Portuguese category label; 610 nulls and two values lack translations. |
| `product_name_lenght` | integer | Yes | Attribute | Product-name character length; 610 nulls. Meaning follows published column naming; spelling retained. |
| `product_description_lenght` | integer | Yes | Attribute | Product-description character length; 610 nulls. |
| `product_photos_qty` | integer | Yes | Attribute | Photo count; 610 nulls. |
| `product_weight_g` | decimal/integer-like | Yes | Attribute | Weight in grams; two nulls and four zeros. |
| `product_length_cm` | decimal/integer-like | Yes | Attribute | Length in centimeters; two nulls. |
| `product_height_cm` | decimal/integer-like | Yes | Attribute | Height in centimeters; two nulls. |
| `product_width_cm` | decimal/integer-like | Yes | Attribute | Width in centimeters; two nulls. |

## Sellers — 3,095 rows

Grain: one seller. Key: `seller_id` (unique, non-null).

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `seller_id` | string | No | PK; FK from items | Seller identifier. |
| `seller_zip_code_prefix` | integer-like | No | Geographic reference | Seven values have no raw geolocation match. |
| `seller_city` | string | No | Attribute | Source city label; categorical consistency pending Phase 2. |
| `seller_state` | string | No | Attribute | Source state abbreviation/domain. |

## Product category translation — 71 rows

Grain: one Portuguese-to-English category mapping. Key: `product_category_name` (unique, non-null).

| Column | Type | Nullable | Key role | Meaning / caveat |
|---|---|---:|---|---|
| `product_category_name` | string | No | PK; referenced by products | Portuguese category label. Does not cover `pc_gamer` or `portateis_cozinha_e_preparadores_de_alimentos`. |
| `product_category_name_english` | string | No | Attribute | Supplied English label; no translation was fabricated for missing mappings. |

