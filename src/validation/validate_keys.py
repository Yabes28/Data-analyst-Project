"""Validate Phase 1 candidate keys and source-specific semantic risks."""

import json
import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
sys.path.insert(0, str(DATA_DIR))
from source_config import CANDIDATE_KEYS, FILES, RAW_DIR, REPORT_DIR  # noqa: E402


def load(table, columns=None):
    return pd.read_csv(RAW_DIR / FILES[table], dtype="string", usecols=columns)


def key_result(table, frame, key):
    null_rows = int(frame[list(key)].isna().any(axis=1).sum())
    duplicate_rows = int(frame.duplicated(list(key), keep=False).sum())
    return {
        "table": table,
        "candidate_key": " + ".join(key),
        "row_count": len(frame),
        "distinct_key_count": int(frame[list(key)].drop_duplicates().shape[0]),
        "null_key_rows": null_rows,
        "duplicate_key_rows": duplicate_rows,
        "is_unique_and_non_null": null_rows == 0 and duplicate_rows == 0,
    }


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    cache = {}
    for table, keys in CANDIDATE_KEYS.items():
        cache[table] = load(table)
        for key in keys:
            results.append(key_result(table, cache[table], key))
    pd.DataFrame(results).to_csv(REPORT_DIR / "key_validation.csv", index=False)

    customers = cache["customers"]
    orders = cache["orders"]
    reviews = cache["reviews"]
    geo = cache["geolocation"]
    products = cache["products"]
    translation = cache["category_translation"]

    cid_per_unique = customers.groupby("customer_unique_id")["customer_id"].nunique()
    unique_per_cid = customers.groupby("customer_id")["customer_unique_id"].nunique()
    orders_per_cid = orders.groupby("customer_id")["order_id"].nunique()

    review_id_counts = reviews["review_id"].value_counts()
    review_order_counts = reviews["order_id"].value_counts()
    duplicate_review_ids = set(review_id_counts[review_id_counts > 1].index)
    duplicate_order_ids = set(review_order_counts[review_order_counts > 1].index)
    duplicate_review_rows = reviews[
        reviews["review_id"].isin(duplicate_review_ids) | reviews["order_id"].isin(duplicate_order_ids)
    ].copy()
    duplicate_review_rows.to_csv(REPORT_DIR / "review_duplicate_records.csv", index=False)

    review_id_order_counts = reviews.groupby("review_id")["order_id"].nunique()
    order_review_id_counts = reviews.groupby("order_id")["review_id"].nunique()
    review_dates = reviews[["review_creation_date", "review_answer_timestamp"]].copy()
    review_dates["review_creation_date"] = pd.to_datetime(review_dates["review_creation_date"], errors="coerce")
    review_dates["review_answer_timestamp"] = pd.to_datetime(review_dates["review_answer_timestamp"], errors="coerce")

    geo_by_zip = geo.groupby("geolocation_zip_code_prefix").agg(
        rows=("geolocation_zip_code_prefix", "size"),
        cities=("geolocation_city", "nunique"),
        states=("geolocation_state", "nunique"),
        coordinates=("geolocation_lat", lambda s: 0),
    )
    coord_counts = geo.groupby("geolocation_zip_code_prefix").apply(
        lambda g: g[["geolocation_lat", "geolocation_lng"]].drop_duplicates().shape[0]
    )
    geo_by_zip["coordinates"] = coord_counts
    geo_by_zip.reset_index().to_csv(REPORT_DIR / "geolocation_zip_profile.csv", index=False)

    product_categories = set(products["product_category_name"].dropna())
    translated_categories = set(translation["product_category_name"].dropna())

    status = orders.groupby("order_status", dropna=False).agg(
        order_count=("order_id", "size"),
        purchase_present=("order_purchase_timestamp", "count"),
        approved_present=("order_approved_at", "count"),
        carrier_present=("order_delivered_carrier_date", "count"),
        customer_delivery_present=("order_delivered_customer_date", "count"),
        estimate_present=("order_estimated_delivery_date", "count"),
    ).reset_index()
    status["percentage"] = status["order_count"] / len(orders) * 100
    status.to_csv(REPORT_DIR / "order_status_profile.csv", index=False)

    date_cols = [
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
    dt = orders[["order_id", "order_status"] + date_cols].copy()
    for col in date_cols:
        dt[col] = pd.to_datetime(dt[col], errors="coerce")
    chronology = {
        "purchase_after_approval": int((dt.order_purchase_timestamp > dt.order_approved_at).sum()),
        "approval_after_carrier": int((dt.order_approved_at > dt.order_delivered_carrier_date).sum()),
        "carrier_after_customer_delivery": int((dt.order_delivered_carrier_date > dt.order_delivered_customer_date).sum()),
        "purchase_after_customer_delivery": int((dt.order_purchase_timestamp > dt.order_delivered_customer_date).sum()),
        "delivered_status_missing_customer_delivery": int(((dt.order_status == "delivered") & dt.order_delivered_customer_date.isna()).sum()),
        "non_delivered_with_customer_delivery": int(((dt.order_status != "delivered") & dt.order_delivered_customer_date.notna()).sum()),
    }

    summary = {
        "customer_identity": {
            "customer_rows": len(customers),
            "distinct_customer_id": int(customers.customer_id.nunique()),
            "distinct_customer_unique_id": int(customers.customer_unique_id.nunique()),
            "customer_unique_ids_with_multiple_customer_ids": int((cid_per_unique > 1).sum()),
            "max_customer_ids_per_unique_id": int(cid_per_unique.max()),
            "customer_ids_mapping_to_multiple_unique_ids": int((unique_per_cid > 1).sum()),
            "customer_ids_linked_to_multiple_orders": int((orders_per_cid > 1).sum()),
            "max_orders_per_customer_id": int(orders_per_cid.max()),
        },
        "reviews": {
            "rows": len(reviews),
            "distinct_review_id": int(reviews.review_id.nunique()),
            "distinct_order_id": int(reviews.order_id.nunique()),
            "review_ids_with_multiple_rows": int((review_id_counts > 1).sum()),
            "orders_with_multiple_review_rows": int((review_order_counts > 1).sum()),
            "max_rows_per_review_id": int(review_id_counts.max()),
            "max_review_rows_per_order": int(review_order_counts.max()),
            "review_ids_linked_to_multiple_orders": int((review_id_order_counts > 1).sum()),
            "orders_with_multiple_distinct_review_ids": int((order_review_id_counts > 1).sum()),
            "exact_duplicate_full_rows": int(reviews.duplicated().sum()),
            "answer_before_creation": int((review_dates.review_answer_timestamp < review_dates.review_creation_date).sum()),
        },
        "geolocation": {
            "rows": len(geo),
            "distinct_zip_prefixes": int(geo.geolocation_zip_code_prefix.nunique()),
            "duplicate_full_rows": int(geo.duplicated().sum()),
            "zip_prefixes_with_multiple_rows": int((geo_by_zip.rows > 1).sum()),
            "max_rows_per_zip_prefix": int(geo_by_zip.rows.max()),
            "zip_prefixes_with_multiple_cities": int((geo_by_zip.cities > 1).sum()),
            "zip_prefixes_with_multiple_states": int((geo_by_zip.states > 1).sum()),
            "zip_prefixes_with_multiple_coordinates": int((geo_by_zip.coordinates > 1).sum()),
        },
        "categories": {
            "products_missing_category": int(products.product_category_name.isna().sum()),
            "distinct_product_categories": len(product_categories),
            "translation_rows": len(translation),
            "unmatched_product_category_values": sorted(product_categories - translated_categories),
            "translation_values_not_used_by_products": sorted(translated_categories - product_categories),
        },
        "chronology": chronology,
    }
    (REPORT_DIR / "semantic_validation.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Validated keys and source semantics into {REPORT_DIR}")


if __name__ == "__main__":
    main()
