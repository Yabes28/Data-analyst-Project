-- QUERY ID: SQL-002
-- ANALYSIS ID: AN-001; AN-008; AN-009; AN-011
-- BUSINESS REQUIREMENT: BR-001; BR-002; BR-015; BR-018; BR-021
-- METRIC DEPENDENCIES: MET-001–MET-015
-- MODEL DEPENDENCIES: MODEL-001–MODEL-012
-- GRAIN: Portfolio summary
-- POPULATION: Metric-specific; no global population filter
-- DATE BASIS: order_purchase_timestamp
-- PURPOSE: Recruiter-readable technical KPI output with denominator context.
SELECT * FROM read_csv_auto('{{RESULTS}}/core_metrics.csv') ORDER BY metric_id;

