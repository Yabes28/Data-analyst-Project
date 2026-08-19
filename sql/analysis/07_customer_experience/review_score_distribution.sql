-- QUERY ID: SQL-013
-- ANALYSIS ID: AN-009
-- BUSINESS REQUIREMENT: BR-018
-- METRIC DEPENDENCIES: MET-010
-- MODEL DEPENDENCIES: MODEL-004; MODEL-005
-- GRAIN: Reviewed order grouped by order-level mean score
-- POPULATION: All reviewed orders
-- DATE BASIS: Parent order_purchase_timestamp for KPI attribution; distribution is full-window
-- PURPOSE: Disclose order-level review-score distribution and denominator.
SELECT mean_review_score order_level_mean_review_score,count(*) reviewed_order_count,
 count(*)::DOUBLE/sum(count(*)) OVER() reviewed_order_share
FROM fact_order_reviews GROUP BY 1 ORDER BY order_level_mean_review_score;
