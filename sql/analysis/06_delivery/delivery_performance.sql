-- QUERY ID: SQL-007
-- ANALYSIS ID: AN-008
-- BUSINESS REQUIREMENT: BR-015; BR-016; BR-017
-- METRIC DEPENDENCIES: MET-008; MET-009; MET-015
-- MODEL DEPENDENCIES: MODEL-001; MODEL-012
-- GRAIN: Endpoint-eligible delivered order to portfolio
-- POPULATION: is_delivery_metric_eligible
-- DATE BASIS: purchase-cohort attribution
-- PURPOSE: Delivery distribution and complementary rates with explicit denominator.
SELECT count(*) delivery_denominator,avg(delivery_lead_time_days) average_delivery_lead_time_days,
 median(delivery_lead_time_days) median_delivery_lead_time_days,
 quantile_cont(delivery_lead_time_days,0.9) p90_delivery_lead_time_days,
 count(*) FILTER(WHERE is_late_delivery) late_orders,
 count(*) FILTER(WHERE is_on_time_delivery) on_time_orders,
 count(*) FILTER(WHERE is_late_delivery)::DOUBLE/NULLIF(count(*),0) late_delivery_rate,
 count(*) FILTER(WHERE is_on_time_delivery)::DOUBLE/NULLIF(count(*),0) on_time_delivery_rate
FROM fact_orders WHERE is_delivery_metric_eligible;

