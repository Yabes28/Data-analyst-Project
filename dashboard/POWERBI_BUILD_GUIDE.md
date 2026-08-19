# Power BI Desktop Build Guide

## 1. Rebuild governed inputs

From the repository root run:

```bash
python src/data/build_analytical_model.py
python src/analysis/run_sql_analysis.py
python src/analysis/run_python_analysis.py
python src/dashboard/build_powerbi_exports.py
```

All import files will be regenerated under `data/processed/powerbi/`. Never edit them manually.

## 2. Import tables

Open Power BI Desktop and import the eleven CSV files listed in `reports/dashboard/powerbi-data-manifest.csv`. Set IDs and labels to Text; monetary columns to Fixed decimal number; timestamps to Date/Time; flags to True/False; `purchase_date` and `dim_date[date]` to Date.

## 3. Configure the model

Create exactly the six active single-direction relationships in `powerbi-relationships.csv`. Mark `dim_date` as the date table. The monthly relationship uses first-of-month `year_month` values so governed Year/Date selections can filter the scaffolded series. Do not relate items to payments, import raw geolocation, enable bidirectional filtering, or connect other aggregate reporting outputs merely for convenience.

## 4. Create measures

Create a `_Measures` table and add DAX-001–DAX-015 from `reports/dashboard/dax-measures.md`. Apply formats from the catalog. DAX is an implementation of the metric contract, not a new definition.

## 5. Validate before designing

Create a temporary validation page with all 15 measures and no filters. Complete `dax-reconciliation.csv` and the metric section of `powerbi-validation-checklist.md`. Stop if any value exceeds tolerance.

## 6. Apply theme and build pages

Import `dashboard/theme.json`. Create the five pages from `page-layout-spec.md` and visuals from `visual-catalog.csv`. Use the documented visual titles, sorting, populations, denominator tooltips, and finding callouts.

## 7. Add slicers and interactions

Use Date/Year and page-appropriate Customer State, Category, Seller State, or Delivery Outcome slicers. Disable category interactions with payment and incompatible order-level visuals. Do not add a report-level commercial-status filter because MET-001 and other populations differ.

## 8. Preserve temporal semantics

Use `bi_monthly_trends` for the executive monthly visual so all 26 months remain present. Style complete, partial, and no-activity periods distinctly. Never replace the November 2016 blank with zero and never bridge it in MoM/YoY text.

## 9. Add methodology and static evidence

Add concise tooltip/help content from `metric-tooltips.csv`. On Page 5 import only the approved Phase 6 cohort heatmap; Page 4 may use the delivery-distribution figure. Label both as static supporting evidence. Include the RFM non-adoption and fanout callouts, but no RFM segments.

## 10. Final verification and delivery

Complete every manual checklist item, save the real `.pbix` under `dashboard/`, refresh twice, reconfirm 15/15 measures, and then capture screenshots from the rendered report. Until those steps pass, Phase 7 remains implementation-package complete with the Desktop build pending.
