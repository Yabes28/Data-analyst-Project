-- QUERY ID: SQL-010
-- ANALYSIS ID: AN-011
-- BUSINESS REQUIREMENT: BR-021; BR-022
-- METRIC DEPENDENCIES: MET-014
-- MODEL DEPENDENCIES: MODEL-003; MODEL-011
-- GRAIN: Payment sequence to payment type
-- POPULATION: All statuses with payment rows
-- DATE BASIS: parent order_purchase_timestamp
-- PURPOSE: Describe recorded payment behavior independently of item facts.
SELECT payment_type,count(*) payment_record_count,count(DISTINCT order_id) payment_bearing_orders,
 sum(payment_value) recorded_payment_value,avg(payment_value) average_recorded_payment_value,
 avg(payment_installments) average_installments,max(payment_installments) maximum_installments,
 sum(payment_value)/NULLIF(sum(sum(payment_value)) OVER(),0) recorded_payment_value_share
FROM fact_payments GROUP BY 1 ORDER BY recorded_payment_value DESC,payment_type;

