"""Validate Phase 1 relationship cardinalities, orphans, and item/payment fanout."""

import json
import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
sys.path.insert(0, str(DATA_DIR))
from source_config import FILES, RAW_DIR, RELATIONSHIPS, REPORT_DIR  # noqa: E402


def load(table, columns=None):
    return pd.read_csv(RAW_DIR / FILES[table], dtype="string", usecols=columns)


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cache = {table: load(table) for table in FILES}
    rows = []
    for parent_name, child_name, parent_key, child_key in RELATIONSHIPS:
        parent = cache[parent_name]
        child = cache[child_name]
        parent_keys = set(parent[parent_key].dropna())
        child_keys = set(child[child_key].dropna())
        parent_unique = not parent[parent_key].duplicated().any()
        child_counts = child[child_key].value_counts()
        max_children = int(child_counts.max()) if len(child_counts) else 0
        rows.append({
            "parent_table": parent_name,
            "child_table": child_name,
            "join": f"{parent_key} = {child_key}",
            "parent_key_unique": parent_unique,
            "child_key_unique": not child[child_key].duplicated().any(),
            "observed_cardinality": ("1:1" if parent_unique and max_children <= 1 else "1:M") if parent_unique else "M:M-risk",
            "unmatched_child_distinct_keys": len(child_keys - parent_keys),
            "unmatched_child_rows": int((~child[child_key].isin(parent_keys) & child[child_key].notna()).sum()),
            "unmatched_parent_distinct_keys": len(parent_keys - child_keys),
            "max_child_rows_per_parent_key": max_children,
            "fanout_risk": max_children > 1 or not parent_unique,
        })
    pd.DataFrame(rows).to_csv(REPORT_DIR / "relationship_validation.csv", index=False)

    geo = cache["geolocation"]
    geo_zips = set(geo["geolocation_zip_code_prefix"].dropna())
    customer_zips = cache["customers"]["customer_zip_code_prefix"]
    seller_zips = cache["sellers"]["seller_zip_code_prefix"]
    postal_coverage = {
        "geolocation_zip_key_unique": not geo["geolocation_zip_code_prefix"].duplicated().any(),
        "customer_rows_without_geolocation_zip_match": int((~customer_zips.isin(geo_zips) & customer_zips.notna()).sum()),
        "customer_distinct_zips_without_match": len(set(customer_zips.dropna()) - geo_zips),
        "seller_rows_without_geolocation_zip_match": int((~seller_zips.isin(geo_zips) & seller_zips.notna()).sum()),
        "seller_distinct_zips_without_match": len(set(seller_zips.dropna()) - geo_zips),
        "raw_join_warning": "geolocation_zip_code_prefix is non-unique; joining raw geolocation to customers or sellers multiplies entity rows.",
    }
    (REPORT_DIR / "postal_coverage.json").write_text(json.dumps(postal_coverage, indent=2), encoding="utf-8")

    items = cache["order_items"][["order_id", "price", "freight_value"]].copy()
    payments = cache["payments"][["order_id", "payment_value"]].copy()
    for col in ["price", "freight_value"]:
        items[col] = pd.to_numeric(items[col], errors="coerce")
    payments["payment_value"] = pd.to_numeric(payments["payment_value"], errors="coerce")

    item_counts = items.groupby("order_id").size().rename("item_rows")
    payment_counts = payments.groupby("order_id").size().rename("payment_rows")
    overlap = pd.concat([item_counts, payment_counts], axis=1).dropna().astype(int)
    overlap["naive_join_rows"] = overlap.item_rows * overlap.payment_rows
    overlap["extra_rows_vs_items"] = overlap.naive_join_rows - overlap.item_rows
    overlap["extra_rows_vs_payments"] = overlap.naive_join_rows - overlap.payment_rows

    naive = items.merge(payments, on="order_id", how="inner")
    fanout = {
        "orders_in_both_facts": len(overlap),
        "orders_with_multiple_items": int((overlap.item_rows > 1).sum()),
        "orders_with_multiple_payments": int((overlap.payment_rows > 1).sum()),
        "orders_with_multiple_items_and_payments": int(((overlap.item_rows > 1) & (overlap.payment_rows > 1)).sum()),
        "expected_naive_join_rows_sum_item_x_payment": int(overlap.naive_join_rows.sum()),
        "observed_naive_join_rows": len(naive),
        "original_item_rows_for_overlapping_orders": int(overlap.item_rows.sum()),
        "original_payment_rows_for_overlapping_orders": int(overlap.payment_rows.sum()),
        "safe_item_price_sum": float(items[items.order_id.isin(overlap.index)].price.sum()),
        "naive_join_item_price_sum": float(naive.price.sum()),
        "safe_freight_sum": float(items[items.order_id.isin(overlap.index)].freight_value.sum()),
        "naive_join_freight_sum": float(naive.freight_value.sum()),
        "safe_payment_sum": float(payments[payments.order_id.isin(overlap.index)].payment_value.sum()),
        "naive_join_payment_sum": float(naive.payment_value.sum()),
        "mathematical_rule": "For order o, a direct item-payment join creates I_o * P_o rows; each item repeats P_o times and each payment repeats I_o times.",
        "safe_options_for_phase_4": [
            "Keep order_items and payments as separate fact tables.",
            "Aggregate each fact independently to one row per order before joining.",
            "Use order as a conformed dimension/bridge and compute measures within their native fact grain.",
        ],
    }
    (REPORT_DIR / "fanout_validation.json").write_text(json.dumps(fanout, indent=2), encoding="utf-8")
    overlap.reset_index().to_csv(REPORT_DIR / "order_item_payment_multiplicity.csv", index=False)
    print(f"Validated relationships and fanout into {REPORT_DIR}")


if __name__ == "__main__":
    main()
