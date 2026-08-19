# Data Source and Schema Specification

**Status:** Pending source validation  
**Source identifier:** Kaggle `olistbr/brazilian-ecommerce`

## Phase 0 finding

No dataset files were present when the repository was inspected. Exact filenames, columns, types, keys, row counts, and grains must be verified in Phase 1. The items below are expected source assets, not validated facts about local files.

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

## Source entities and grain hypotheses

| Source entity | Expected grain to validate | Candidate logical key to validate | Key risk |
|---|---|---|---|
| customers | One row per order-linked customer record | customer identifier | Distinguish order-level customer ID from stable unique customer ID. |
| geolocation | Potentially multiple rows per postal-code prefix | composite/location fields | High duplication; unsafe as a direct dimension join. |
| order items | One row per order-item sequence | order + item sequence | Multiple products/sellers per order. |
| payments | One row per order payment sequence/type record | order + payment sequence | Multiple rows per order; do not join directly to items for monetary aggregation. |
| reviews | Review records associated with orders | review/order identifiers | Possible duplicate or revised order-review relationships. |
| orders | One row per order | order identifier | Lifecycle status and nullable event timestamps. |
| products | One row per product | product identifier | Missing/untranslated categories. |
| sellers | One row per seller | seller identifier | Geography may require careful enrichment. |
| category translation | One row per source category label | source category label | Translation gaps or duplicates. |

These are hypotheses only. No analytical join is authorized until Phase 1 validates actual columns and Phase 4 approves table grains.

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

