# Dashboard Specification

**Status:** Planning only — no finished dashboard in Phase 0.

## Audience and goal

Provide executives and commercial/operations teams with a concise, consistent view of commerce activity and customer experience, plus drill paths for investigation. The dashboard is descriptive and diagnostic, not a profit report or causal model.

| ID | View | Decision questions | Planned content | Traceability |
|---|---|---|---|---|
| DASH-001 | Executive Overview | How are demand and value changing, and where are they concentrated? | Total/delivered orders, Product GMV, AOV, unique customers, monthly trends, category and state summaries. | BR-001–BR-004, BR-021–BR-022 |
| DASH-002 | Customer & Commercial Performance | Who buys repeatedly, and which categories/sellers drive scale? | Repeat behavior, cohort/RFM only if valid, category mix, seller concentration/performance. | BR-005–BR-014 |
| DASH-003 | Delivery & Customer Experience | Where is fulfillment friction observed and how does it align with reviews? | Lead-time distribution, late rate, freight burden, review distribution, geographic/category/seller comparisons, late-vs-review association. | BR-015–BR-020 |

## Interaction and design requirements

| ID | Requirement |
|---|---|
| DASH-004 | Use metric-contract names and tooltips containing definitions, filters, and caveats. |
| DASH-005 | Provide only validated slicers, likely date, order status, customer state, category, and seller; prevent misleading cross-filter behavior. |
| DASH-006 | Display source observation window, last refresh, eligibility/coverage, and complete-period warnings. |
| DASH-007 | Use a clear KPI-to-trend-to-breakdown hierarchy, restrained color, accessible contrast, and consistent number formats. |
| DASH-008 | Avoid pie-chart clutter, redundant visuals, decorative gauges, and unsupported target thresholds. |
| DASH-009 | Validate Power BI relationships and DAX measures against SQL/Python control totals. |
| DASH-010 | Label associations as observational and make exclusions/limitations discoverable. |

Final visual selection, layout, targets, and DAX are pending validated data and actual analytical findings.

