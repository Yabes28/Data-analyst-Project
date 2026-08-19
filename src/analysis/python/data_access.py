"""Governed DuckDB data access for Phase 6."""
from pathlib import Path
import duckdb

def connect(db: Path): return duckdb.connect(str(db), read_only=True)

def query(con, sql): return con.execute(sql).df()

def customer_frame(con):
    return query(con,"""SELECT customer_unique_id,min(order_purchase_timestamp) observed_first_purchase_timestamp,
      max(order_purchase_timestamp) observed_last_purchase_timestamp,count(DISTINCT order_id) eligible_order_count,
      sum(product_gmv) FILTER(WHERE has_items) observed_customer_product_gmv,
      sum(product_gmv) FILTER(WHERE has_items)/nullif(count(*) FILTER(WHERE has_items),0) average_order_product_gmv,
      date_diff('day',min(order_purchase_timestamp),max(order_purchase_timestamp)) observed_purchase_span_days,
      count(DISTINCT order_id)>=2 observed_repeat_flag
      FROM mart_order_analytics WHERE is_commercially_eligible GROUP BY customer_unique_id ORDER BY customer_unique_id""")

def eligible_orders(con):
    return query(con,"""SELECT order_id,customer_unique_id,order_purchase_timestamp,product_gmv,item_count,freight_value,
      gross_order_value,freight_value/nullif(gross_order_value,0) freight_burden
      FROM mart_order_analytics WHERE is_commercially_eligible AND has_items ORDER BY order_id""")
