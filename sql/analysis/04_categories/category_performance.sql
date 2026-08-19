-- QUERY ID: SQL-005
-- ANALYSIS ID: AN-006
-- BUSINESS REQUIREMENT: BR-009; BR-010; BR-011
-- METRIC DEPENDENCIES: MET-003; MET-005; MET-010; MET-011–MET-013
-- MODEL DEPENDENCIES: MODEL-001; MODEL-002; MODEL-005; MODEL-007
-- GRAIN: Item to category; order outcomes allocated only to distinct category/order pairs
-- POPULATION: Commercial item population; reviewed/delivery subsets disclosed
-- DATE BASIS: parent order_purchase_timestamp
-- PURPOSE: Category scale, contribution, freight, delivery, and review context.
WITH item_category AS (
 SELECT i.order_id,p.approved_display_category category,i.price,i.freight_value
 FROM fact_order_items i JOIN dim_products p USING(product_id) WHERE i.is_commercially_eligible
), commercial AS (
 SELECT category,count(*) item_count,count(DISTINCT order_id) order_count,sum(price) product_gmv,sum(price+freight_value) gross_order_value,sum(freight_value) freight_value
 FROM item_category GROUP BY 1
), order_category AS (SELECT DISTINCT order_id,category FROM item_category), outcomes AS (
 SELECT oc.category,count(*) FILTER(WHERE m.is_delivery_metric_eligible) delivery_denominator,
   count(*) FILTER(WHERE m.is_delivery_metric_eligible AND m.is_late_delivery) late_orders,
   count(*) FILTER(WHERE m.has_review) reviewed_orders,avg(m.mean_review_score) FILTER(WHERE m.has_review) avg_order_review_score
 FROM order_category oc JOIN mart_order_analytics m USING(order_id) GROUP BY 1
), ranked AS (
 SELECT c.*,rank() OVER(ORDER BY product_gmv DESC,category) product_gmv_rank,
  product_gmv/sum(product_gmv) OVER() product_gmv_share,
  sum(product_gmv) OVER(ORDER BY product_gmv DESC,category ROWS UNBOUNDED PRECEDING)/sum(product_gmv) OVER() cumulative_product_gmv_share
 FROM commercial c
)
SELECT r.*,product_gmv/NULLIF(order_count,0) category_value_per_order,freight_value/NULLIF(gross_order_value,0) freight_burden,
 o.delivery_denominator,o.late_orders,o.late_orders::DOUBLE/NULLIF(o.delivery_denominator,0) late_delivery_rate,o.reviewed_orders,o.avg_order_review_score
FROM ranked r LEFT JOIN outcomes o USING(category) ORDER BY product_gmv_rank,category;

