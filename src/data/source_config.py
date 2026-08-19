"""Central Phase 1 source metadata. No transformation logic belongs here."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "source-validation"

FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

DATE_COLUMNS = {
    "order_items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
}

NUMERIC_COLUMNS = {
    "customers": ["customer_zip_code_prefix"],
    "geolocation": ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"],
    "order_items": ["order_item_id", "price", "freight_value"],
    "payments": ["payment_sequential", "payment_installments", "payment_value"],
    "reviews": ["review_score"],
    "products": [
        "product_name_lenght", "product_description_lenght", "product_photos_qty",
        "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm",
    ],
    "sellers": ["seller_zip_code_prefix"],
}

CANDIDATE_KEYS = {
    "customers": [("customer_id",)],
    "geolocation": [
        ("geolocation_zip_code_prefix",),
        ("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"),
    ],
    "order_items": [("order_id", "order_item_id")],
    "payments": [("order_id", "payment_sequential")],
    "reviews": [("review_id",), ("order_id",)],
    "orders": [("order_id",)],
    "products": [("product_id",)],
    "sellers": [("seller_id",)],
    "category_translation": [("product_category_name",)],
}

RELATIONSHIPS = [
    ("customers", "orders", "customer_id", "customer_id"),
    ("orders", "order_items", "order_id", "order_id"),
    ("orders", "payments", "order_id", "order_id"),
    ("orders", "reviews", "order_id", "order_id"),
    ("products", "order_items", "product_id", "product_id"),
    ("sellers", "order_items", "seller_id", "seller_id"),
    ("category_translation", "products", "product_category_name", "product_category_name"),
]

