-- QUERY ID: SQL-006
-- ANALYSIS ID: AN-007
-- BUSINESS REQUIREMENT: BR-012; BR-013; BR-014
-- METRIC DEPENDENCIES: MET-003; MET-008–MET-010; MET-011
-- MODEL DEPENDENCIES: MODEL-001; MODEL-002; MODEL-005; MODEL-008
-- GRAIN: Item to seller; order outcomes limited to single-seller commercial orders
-- POPULATION: Commercial items; seller-attributable order outcomes only
-- DATE BASIS: parent order_purchase_timestamp
-- PURPOSE: Seller concentration and denominator-aware outcomes without best/worst labels.
WITH commercial AS (
 SELECT seller_id,count(*) item_count,count(DISTINCT order_id) order_count,sum(price) product_gmv FROM fact_order_items WHERE is_commercially_eligible GROUP BY 1
), single_seller_orders AS (
 SELECT order_id,min(seller_id) seller_id FROM fact_order_items WHERE is_commercially_eligible GROUP BY 1 HAVING count(DISTINCT seller_id)=1
), outcomes AS (
 SELECT s.seller_id,count(*) attributable_orders,count(*) FILTER(WHERE m.is_delivery_metric_eligible) delivery_denominator,
  count(*) FILTER(WHERE m.is_delivery_metric_eligible AND m.is_late_delivery) late_orders,
  count(*) FILTER(WHERE m.has_review) reviewed_orders,avg(m.mean_review_score) FILTER(WHERE m.has_review) avg_order_review_score
 FROM single_seller_orders s JOIN mart_order_analytics m USING(order_id) GROUP BY 1
), ranked AS (
 SELECT c.*,rank() OVER(ORDER BY product_gmv DESC,seller_id) product_gmv_rank,
 product_gmv/sum(product_gmv) OVER() product_gmv_share,
 sum(product_gmv) OVER(ORDER BY product_gmv DESC,seller_id ROWS UNBOUNDED PRECEDING)/sum(product_gmv) OVER() cumulative_product_gmv_share
 FROM commercial c
)
SELECT r.*,d.seller_state,o.attributable_orders,o.delivery_denominator,o.late_orders,
 o.late_orders::DOUBLE/NULLIF(o.delivery_denominator,0) late_delivery_rate,o.reviewed_orders,o.avg_order_review_score
FROM ranked r JOIN dim_sellers d USING(seller_id) LEFT JOIN outcomes o USING(seller_id) ORDER BY product_gmv_rank,seller_id;

