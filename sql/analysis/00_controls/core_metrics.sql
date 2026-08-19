-- QUERY ID: SQL-001
-- ANALYSIS ID: AN-001; AN-003; AN-008; AN-009; AN-011
-- BUSINESS REQUIREMENT: BR-001; BR-002; BR-005; BR-006; BR-015; BR-017; BR-018; BR-021; BR-022
-- METRIC DEPENDENCIES: MET-001–MET-015
-- MODEL DEPENDENCIES: MODEL-001; MODEL-002; MODEL-003; MODEL-005; MODEL-006; MODEL-010; MODEL-011; MODEL-012
-- GRAIN: Native facts aggregated to portfolio metric grain
-- POPULATION: Metric-specific according to the authoritative metric contract
-- DATE BASIS: order_purchase_timestamp
-- PURPOSE: Calculate the governed core metric set without interpretation.
WITH customer_orders AS (
  SELECT customer_unique_id, count(DISTINCT order_id) order_count
  FROM fact_orders WHERE is_commercially_eligible GROUP BY 1
), values AS (
  SELECT 'MET-001' metric_id, count(DISTINCT order_id)::DOUBLE AS "value", count(DISTINCT order_id)::DOUBLE denominator FROM fact_orders
  UNION ALL SELECT 'MET-002', count(DISTINCT order_id)::DOUBLE, count(DISTINCT order_id)::DOUBLE FROM fact_orders WHERE is_delivered_status
  UNION ALL SELECT 'MET-003', sum(price)::DOUBLE, count(*)::DOUBLE FROM fact_order_items WHERE is_commercially_eligible
  UNION ALL SELECT 'MET-004', sum(price + freight_value)::DOUBLE, count(*)::DOUBLE FROM fact_order_items WHERE is_commercially_eligible
  UNION ALL SELECT 'MET-005', sum(product_gmv)::DOUBLE / NULLIF(count(*),0), count(*)::DOUBLE FROM agg_order_items i JOIN fact_orders o USING(order_id) WHERE o.is_commercially_eligible
  UNION ALL SELECT 'MET-006', count(DISTINCT customer_unique_id)::DOUBLE, count(DISTINCT customer_unique_id)::DOUBLE FROM fact_orders WHERE is_commercially_eligible
  UNION ALL SELECT 'MET-007', count(*) FILTER (WHERE order_count >= 2)::DOUBLE / NULLIF(count(*),0), count(*)::DOUBLE FROM customer_orders
  UNION ALL SELECT 'MET-008', avg(delivery_lead_time_days), count(*)::DOUBLE FROM fact_orders WHERE is_delivery_metric_eligible
  UNION ALL SELECT 'MET-009', count(*) FILTER (WHERE is_late_delivery)::DOUBLE / NULLIF(count(*),0), count(*)::DOUBLE FROM fact_orders WHERE is_delivery_metric_eligible
  UNION ALL SELECT 'MET-010', avg(mean_review_score), count(*)::DOUBLE FROM fact_order_reviews
  UNION ALL SELECT 'MET-011', count(*)::DOUBLE, count(*)::DOUBLE FROM fact_order_items WHERE is_commercially_eligible
  UNION ALL SELECT 'MET-012', sum(freight_value)::DOUBLE, count(*)::DOUBLE FROM fact_order_items WHERE is_commercially_eligible
  UNION ALL SELECT 'MET-013', sum(freight_value)::DOUBLE / NULLIF(sum(price + freight_value),0), sum(price + freight_value)::DOUBLE FROM fact_order_items WHERE is_commercially_eligible
  UNION ALL SELECT 'MET-014', sum(payment_value)::DOUBLE, count(*)::DOUBLE FROM fact_payments
  UNION ALL SELECT 'MET-015', count(*) FILTER (WHERE is_on_time_delivery)::DOUBLE / NULLIF(count(*),0), count(*)::DOUBLE FROM fact_orders WHERE is_delivery_metric_eligible
)
SELECT * FROM values ORDER BY metric_id;
