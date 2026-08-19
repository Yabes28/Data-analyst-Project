-- QUERY ID: SQL-009
-- ANALYSIS ID: AN-002; AN-008; AN-009
-- BUSINESS REQUIREMENT: BR-004; BR-015; BR-016; BR-020
-- METRIC DEPENDENCIES: MET-001; MET-003; MET-005; MET-006; MET-008–MET-010
-- MODEL DEPENDENCIES: MODEL-001; MODEL-012
-- GRAIN: Order to order-associated Customer State
-- POPULATION: Metric-specific; denominators disclosed
-- DATE BASIS: order_purchase_timestamp
-- PURPOSE: Demand and service outcomes by explicitly labeled Customer State.
SELECT customer_state,count(*) total_orders,
 count(*) FILTER(WHERE is_commercially_eligible) commercial_orders,
 count(DISTINCT customer_unique_id) FILTER(WHERE is_commercially_eligible) observed_unique_customers,
 sum(product_gmv) FILTER(WHERE is_commercially_eligible AND has_items) product_gmv,
 sum(product_gmv) FILTER(WHERE is_commercially_eligible AND has_items)/NULLIF(count(*) FILTER(WHERE is_commercially_eligible AND has_items),0) aov_product_gmv,
 count(*) FILTER(WHERE is_delivery_metric_eligible) delivery_denominator,
 avg(delivery_lead_time_days) FILTER(WHERE is_delivery_metric_eligible) average_delivery_lead_time_days,
 count(*) FILTER(WHERE is_delivery_metric_eligible AND is_late_delivery) late_orders,
 count(*) FILTER(WHERE is_delivery_metric_eligible AND is_late_delivery)::DOUBLE/NULLIF(count(*) FILTER(WHERE is_delivery_metric_eligible),0) late_delivery_rate,
 count(*) FILTER(WHERE has_review) reviewed_orders,avg(mean_review_score) FILTER(WHERE has_review) average_order_level_review_score
FROM mart_order_analytics GROUP BY 1 ORDER BY product_gmv DESC NULLS LAST,customer_state;

