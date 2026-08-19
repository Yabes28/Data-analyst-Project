# Manual Power BI Validation Checklist

Power BI Desktop execution is pending. Do not change `PENDING_POWER_BI_EXECUTION` to PASS until each item is verified in the actual report.

## Metric reconciliation

Create an unfiltered validation page containing MET-001–MET-015. Copy actual values into `dax-reconciliation.csv`, calculate differences, and compare with its tolerance. Confirm MET-009 and MET-015 use the same denominator and sum to 100% before display rounding.

## Model

- [ ] Six specified relationships exist, are active, and filter one direction only.
- [ ] `dim_date` is marked as the date table using `date`.
- [ ] No item-payment, raw-geolocation, bidirectional, or many-to-many relationship exists.
- [ ] Category and seller aggregate tables remain disconnected reporting outputs unless a documented safe relationship is added.

## Pages and interactions

- [ ] Five pages exist with the names in `page-layout-spec.md`.
- [ ] KPI cards use exact governed names and tooltips.
- [ ] Date filtering uses purchase date.
- [ ] November 2016 appears as `NO_OBSERVED_ACTIVITY`; its value is blank, not zero.
- [ ] Partial-period markers and tooltips are visible.
- [ ] Category selections do not filter payment visuals or invalid order metrics.
- [ ] Seller concentration uses all commercial seller items; outcome visuals disclose the 1.30% multi-seller exclusion.
- [ ] Rates and averages expose denominators.
- [ ] Delivery/review text says “observed association” and does not imply causality.
- [ ] No RFM segment, score, page, slicer, or customer label exists.

## UX and portfolio review

- [ ] Titles, axes, units, legends, and sorting match the visual catalog.
- [ ] Theme and semantic late/on-time colors are consistent.
- [ ] Page density remains readable at 100% zoom.
- [ ] Methodology panel includes all required limitations.
- [ ] Screenshots are captured only from the verified real report.
