# Data Source and Schema Specification

**Status:** Phase 1 source validation complete  
**Source identifier:** Kaggle `olistbr/brazilian-ecommerce`

## Phase 0 finding

No dataset files were present when the repository was inspected. Exact filenames, columns, types, keys, row counts, and grains must be verified in Phase 1. The items below are expected source assets, not validated facts about local files.

## Phase 1 evidence

All nine expected files were acquired manually and validated as readable UTF-8 comma-separated files on 2026-08-19. SHA-256 hashes, sizes, row/column counts, complete schemas, profiles, key tests, and relationship tests are stored under `reports/source-validation/`. The validated data dictionary is `docs/data-dictionary.md`.

## Expected original CSV files

- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

Do not rename or manually edit original CSVs in `data/raw/`. Record checksums, sizes, row counts, encoding, delimiter, and acquisition date after download.

## Safe acquisition procedure

1. Open the Kaggle dataset page for `olistbr/brazilian-ecommerce` and accept any current Kaggle terms.
2. Download the archive manually, or install/configure the official Kaggle CLI outside the repository.
3. For CLI use, store credentials only in Kaggle's user-level configuration location or environment variables. Never place `kaggle.json`, usernames, keys, or tokens in this repository.
4. Run from the repository root after the CLI is available:

   ```powershell
   kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
   ```

5. Confirm that only original source files exist in `data/raw/`; do not commit them.
6. Run the Phase 1 inventory and checksum procedure before any transformations.

If automated access is unavailable, use Kaggle's browser download and extract the original CSV files into `data/raw/`.

## Validated source entities and grains

| Source entity | Confirmed grain | Validated logical key | Key risk |
|---|---|---|---|
| customers | One order-associated customer record | `customer_id` | `customer_unique_id` is the validated stable customer grouping identity. |
| geolocation | One observed coordinate/city/state record for a ZIP prefix | None; tested combinations are non-unique | High duplication; unsafe as a direct dimension join. |
| order items | One sequential item line within an order | `order_id + order_item_id` | Multiple products/sellers per order. |
| payments | One payment sequence record within an order | `order_id + payment_sequential` | Multiple rows per order; do not join directly to items for monetary aggregation. |
| reviews | One source review event row linking review and order | None approved; both IDs repeat | Multiple review/order relationships have no explicit revision indicator. |
| orders | One order | `order_id` | Lifecycle status and nullable event timestamps. |
| products | One product | `product_id` | Missing/untranslated categories. |
| sellers | One seller | `seller_id` | Geography requires normalization or omission. |
| category translation | One Portuguese category label mapping | `product_category_name` | Two product category values are unmatched. |

These source grains are validated. Analytical table design and canonical review/geolocation rules remain Phase 4 decisions.

## Customer identity semantics

Observed relationships validate `customer_id` as an order-associated customer record identifier: it is unique in customers and each value links to exactly one order. `customer_unique_id` is the stable cross-order identity: 2,997 values map to multiple `customer_id` records, with a maximum of 17. Future repeat/cohort/RFM analysis must use `customer_unique_id`, subject to approved status and observation-window rules.

## Publication attribution

The Kaggle dataset page identifies the license as CC BY-NC-SA 4.0 and describes the data as anonymized commercial data. Recheck the live license at publication time and include Olist/Kaggle attribution and required license/adaptation notices.

## Required Phase 1 validations

| ID | Requirement |
|---|---|
| DATA-001 | Verify presence, exact filename, size, checksum, encoding, delimiter, row count, and column names for every source file. |
| DATA-002 | Infer then explicitly assign data types; preserve raw strings during initial inspection. |
| DATA-003 | Validate candidate primary/logical keys and duplicate counts. |
| DATA-004 | Validate foreign-key coverage among orders, customers, items, products, sellers, payments, reviews, and translations. |
| DATA-005 | Confirm customer identifier semantics before customer-level aggregation. |
| DATA-006 | Confirm timestamp meaning, timezone assumptions, minimum/maximum dates, and dataset observation window. |
| DATA-007 | Profile status values and lifecycle timestamp completeness by status. |
| DATA-008 | Determine a safe geolocation normalization/deduplication strategy before joining. |
| DATA-009 | Record source licensing/attribution requirements for portfolio publication. |
