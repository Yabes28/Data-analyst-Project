-- QUERY ID: SQL-012
-- ANALYSIS ID: AN-006
-- BUSINESS REQUIREMENT: BR-003; BR-009; BR-011
-- METRIC DEPENDENCIES: MET-003; MET-011
-- MODEL DEPENDENCIES: MODEL-002; MODEL-007
-- GRAIN: Commercial item to month/category
-- POPULATION: Top five categories by full-window eligible Product GMV
-- DATE BASIS: parent order_purchase_timestamp month
-- PURPOSE: Compare predetermined major-category trends without story-driven selection.
WITH top_categories AS (
 SELECT p.approved_display_category category
 FROM fact_order_items i JOIN dim_products p USING(product_id)
 WHERE i.is_commercially_eligible GROUP BY 1 ORDER BY sum(i.price) DESC,category LIMIT 5
), monthly AS (
 SELECT date_trunc('month',i.order_purchase_timestamp)::DATE year_month,p.approved_display_category category,
   count(*) item_count,count(DISTINCT i.order_id) order_count,sum(i.price) product_gmv
 FROM fact_order_items i JOIN dim_products p USING(product_id) JOIN top_categories t ON p.approved_display_category=t.category
 WHERE i.is_commercially_eligible GROUP BY 1,2
)
SELECT *,lag(product_gmv) OVER(PARTITION BY category ORDER BY year_month) previous_product_gmv,
 (product_gmv-lag(product_gmv) OVER(PARTITION BY category ORDER BY year_month))/NULLIF(lag(product_gmv) OVER(PARTITION BY category ORDER BY year_month),0) product_gmv_pct_change
FROM monthly ORDER BY category,year_month;

