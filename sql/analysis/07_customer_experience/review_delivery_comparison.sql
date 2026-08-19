-- QUERY ID: SQL-008
-- ANALYSIS ID: AN-009; AN-010
-- BUSINESS REQUIREMENT: BR-018; BR-019; BR-020
-- METRIC DEPENDENCIES: MET-009; MET-010; MET-015
-- MODEL DEPENDENCIES: MODEL-001; MODEL-005; MODEL-012
-- GRAIN: Endpoint-eligible order, grouped by delivery outcome
-- POPULATION: Endpoint-eligible delivered orders; review metrics use reviewed subset
-- DATE BASIS: parent order_purchase_timestamp
-- PURPOSE: Test observational late/on-time review association; low score means order mean <=2.
SELECT CASE WHEN is_late_delivery THEN 'LATE' ELSE 'ON_TIME' END delivery_outcome,
 count(*) order_count,count(*) FILTER(WHERE has_review) reviewed_order_count,
 avg(mean_review_score) FILTER(WHERE has_review) average_order_level_review_score,
 count(*) FILTER(WHERE has_review AND mean_review_score<=2) low_score_reviewed_orders,
 count(*) FILTER(WHERE has_review AND mean_review_score<=2)::DOUBLE/NULLIF(count(*) FILTER(WHERE has_review),0) low_score_rate
FROM mart_order_analytics
WHERE is_delivery_metric_eligible AND is_late_delivery IS NOT NULL
GROUP BY 1 ORDER BY delivery_outcome;
