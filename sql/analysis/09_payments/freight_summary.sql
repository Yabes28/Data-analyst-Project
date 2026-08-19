-- QUERY ID: SQL-011
-- ANALYSIS ID: AN-011
-- BUSINESS REQUIREMENT: BR-010; BR-016; BR-021
-- METRIC DEPENDENCIES: MET-012; MET-013
-- MODEL DEPENDENCIES: MODEL-002
-- GRAIN: Commercial item to portfolio
-- POPULATION: Approved commercial item population
-- DATE BASIS: parent order_purchase_timestamp
-- PURPOSE: Preserve recorded freight value and zero-freight context without cost claims.
SELECT count(*) item_count,count(*) FILTER(WHERE freight_value=0) zero_freight_items,
 sum(freight_value) freight_value,sum(price+freight_value) gross_order_value,
 sum(freight_value)/NULLIF(sum(price+freight_value),0) freight_burden
FROM fact_order_items WHERE is_commercially_eligible;
