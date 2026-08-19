-- QUERY ID: SQL-004
-- ANALYSIS ID: AN-003
-- BUSINESS REQUIREMENT: BR-005; BR-006
-- METRIC DEPENDENCIES: MET-006; MET-007; MET-003; MET-005
-- MODEL DEPENDENCIES: MODEL-001; MODEL-006; MODEL-012
-- GRAIN: Stable customer to observed frequency group
-- POPULATION: Commercial orders in the full observed window
-- DATE BASIS: order_purchase_timestamp
-- PURPOSE: Describe observed purchase frequency without retention claims.
WITH customers AS (
 SELECT customer_unique_id, count(DISTINCT order_id) eligible_order_count,
   sum(product_gmv) FILTER(WHERE has_items) product_gmv,
   count(*) FILTER(WHERE has_items) item_bearing_order_count
 FROM mart_order_analytics WHERE is_commercially_eligible GROUP BY 1
)
SELECT CASE WHEN eligible_order_count=1 THEN '1 order' WHEN eligible_order_count=2 THEN '2 orders' WHEN eligible_order_count BETWEEN 3 AND 5 THEN '3-5 orders' ELSE '6+ orders' END frequency_group,
 count(*) observed_customers, sum(eligible_order_count) eligible_orders, sum(product_gmv) product_gmv,
 sum(product_gmv)/NULLIF(sum(item_bearing_order_count),0) frequency_group_aov,
 min(eligible_order_count) min_orders, max(eligible_order_count) max_orders
FROM customers GROUP BY 1 ORDER BY min_orders;
