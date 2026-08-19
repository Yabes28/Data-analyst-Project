-- QUERY ID: SQL-003
-- ANALYSIS ID: AN-001
-- BUSINESS REQUIREMENT: BR-001; BR-002; BR-003
-- METRIC DEPENDENCIES: MET-001; MET-003; MET-005; MET-006; MET-009; MET-015
-- MODEL DEPENDENCIES: MODEL-001; MODEL-010; MODEL-012
-- GRAIN: Order to calendar month
-- POPULATION: Metric-specific monthly populations
-- DATE BASIS: order_purchase_timestamp month
-- PURPOSE: Comparable monthly trends with explicit boundary completeness and LAG.
WITH calendar_months AS (
 SELECT DISTINCT date_trunc('month',date)::DATE year_month
 FROM dim_date
 WHERE date BETWEEN (SELECT min(order_purchase_timestamp)::DATE FROM fact_orders)
                    AND (SELECT max(order_purchase_timestamp)::DATE FROM fact_orders)
), monthly AS (
 SELECT date_trunc('month',order_purchase_timestamp)::DATE year_month,
   min(order_purchase_timestamp::DATE) observed_first_date, max(order_purchase_timestamp::DATE) observed_last_date,
   date_diff('day',min(order_purchase_timestamp::DATE),max(order_purchase_timestamp::DATE))+1 days_represented,
   count(*) total_orders,
   sum(product_gmv) FILTER(WHERE is_commercially_eligible AND has_items) product_gmv,
   sum(product_gmv) FILTER(WHERE is_commercially_eligible AND has_items)/NULLIF(count(*) FILTER(WHERE is_commercially_eligible AND has_items),0) aov_product_gmv,
   count(DISTINCT customer_unique_id) FILTER(WHERE is_commercially_eligible) observed_unique_customers,
   count(*) FILTER(WHERE is_delivery_metric_eligible AND is_late_delivery) late_orders,
   count(*) FILTER(WHERE is_delivery_metric_eligible) delivery_denominator
 FROM mart_order_analytics GROUP BY 1
), labeled AS (
 SELECT c.year_month,m.* EXCLUDE(year_month),
   CASE WHEN m.total_orders IS NULL THEN 'NO_OBSERVED_ACTIVITY'
        WHEN m.observed_first_date=c.year_month AND m.observed_last_date=last_day(c.year_month) THEN 'COMPLETE_PERIOD'
        ELSE 'PARTIAL_PERIOD' END period_status
 FROM calendar_months c LEFT JOIN monthly m USING(year_month)
), windowed AS (
 SELECT *, lag(period_status) OVER(ORDER BY year_month) previous_period_status,
   lag(total_orders) OVER(ORDER BY year_month) previous_total_orders,
   lag(product_gmv) OVER(ORDER BY year_month) previous_product_gmv,
   lag(period_status,12) OVER(ORDER BY year_month) prior_year_period_status,
   lag(total_orders,12) OVER(ORDER BY year_month) prior_year_total_orders,
   lag(product_gmv,12) OVER(ORDER BY year_month) prior_year_product_gmv
 FROM labeled
)
SELECT year_month,observed_first_date,observed_last_date,days_represented,total_orders,product_gmv,aov_product_gmv,
 observed_unique_customers,late_orders,delivery_denominator,period_status,
 CASE WHEN period_status='COMPLETE_PERIOD' AND previous_period_status='COMPLETE_PERIOD' THEN previous_total_orders END previous_total_orders,
 CASE WHEN period_status='COMPLETE_PERIOD' AND previous_period_status='COMPLETE_PERIOD' THEN total_orders-previous_total_orders END order_absolute_change,
 CASE WHEN period_status='COMPLETE_PERIOD' AND previous_period_status='COMPLETE_PERIOD' THEN (total_orders-previous_total_orders)::DOUBLE/NULLIF(previous_total_orders,0) END order_pct_change,
 CASE WHEN period_status='COMPLETE_PERIOD' AND previous_period_status='COMPLETE_PERIOD' THEN previous_product_gmv END previous_product_gmv,
 CASE WHEN period_status='COMPLETE_PERIOD' AND previous_period_status='COMPLETE_PERIOD' THEN product_gmv-previous_product_gmv END product_gmv_absolute_change,
 CASE WHEN period_status='COMPLETE_PERIOD' AND previous_period_status='COMPLETE_PERIOD' THEN (product_gmv-previous_product_gmv)/NULLIF(previous_product_gmv,0) END product_gmv_pct_change,
 CASE WHEN period_status='COMPLETE_PERIOD' AND prior_year_period_status='COMPLETE_PERIOD' THEN prior_year_total_orders END prior_year_total_orders,
 CASE WHEN period_status='COMPLETE_PERIOD' AND prior_year_period_status='COMPLETE_PERIOD' THEN (total_orders-prior_year_total_orders)::DOUBLE/NULLIF(prior_year_total_orders,0) END order_yoy_pct_change,
 CASE WHEN period_status='COMPLETE_PERIOD' AND prior_year_period_status='COMPLETE_PERIOD' THEN prior_year_product_gmv END prior_year_product_gmv,
 CASE WHEN period_status='COMPLETE_PERIOD' AND prior_year_period_status='COMPLETE_PERIOD' THEN (product_gmv-prior_year_product_gmv)/NULLIF(prior_year_product_gmv,0) END product_gmv_yoy_pct_change,
 late_orders::DOUBLE/NULLIF(delivery_denominator,0) late_delivery_rate,
 1-late_orders::DOUBLE/NULLIF(delivery_denominator,0) on_time_delivery_rate
FROM windowed ORDER BY year_month;
