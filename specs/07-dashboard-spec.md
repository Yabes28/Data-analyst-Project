# Dashboard Specification

**Status:** Phase 7 implementation package specification; Power BI Desktop build pending.

**Audience:** Recruiters, hiring managers, business managers, BI/data analyst interviewers, and technical reviewers.

| ID | Objective / page | MET / findings | Source and population | Visual / interaction | Limitation and acceptance |
|---|---|---|---|---|---|
| DASH-001 | Executive Overview: summarize governed performance | MET-001/003/005/006/009/010; FIND-001/005 | Metric-specific; purchase date | Six KPI cards; monthly orders/GMV; category and Customer State bars; delivery share | No global population filter; KPI tooltips and partial-period legend required |
| DASH-002 | Commercial & Category Performance | MET-003/011–013; FIND-003/004 | Commercial items; category/seller aggregates | Top-10 category bar, cumulative contribution line, freight burden, seller concentration | Unknown/untranslated retained; concentration uses all seller items |
| DASH-003 | Customer & Geography | MET-006/007; FIND-002/007; PYFIND-002/003 | Stable customers; order-associated Customer State | KPI cards, frequency bars, Customer State bar, value-concentration callout | Observed-window language; no CLV/loyalty/retention claim |
| DASH-004 | Delivery & Customer Experience | MET-008–010/015; FIND-005/006; PYFIND-006/007 | Endpoint-qualified orders; reviewed subset | KPI cards, delivery share, review distribution, outcome comparison, diagnostic lead-time figure | Denominators visible; association explicitly non-causal |
| DASH-005 | Analytical Deep Dive | PYFIND-001/004/005 | Approved Python outputs | Observed cohort heatmap, distribution figure, RFM-method note, fanout callout | Censored cells blank; no RFM segmentation; methodology not KPI |
| DASH-006 | Governed metric tooltips | MET-001–015 | Metric-specific | Report-page tooltip/info panel | Exact definition, population, date, caveat, MET ID |
| DASH-007 | Calendar continuity | MET-001/003 | `dim_date`; purchase date | 26-month scaffold; period-status legend and tooltip | 19 complete, 6 partial, 1 no activity; November 2016 retained |
| DASH-008 | Date filtering | MET-001–015 | Primary purchase date | `dim_date[date]` active single-direction filter | Secondary dates prohibited unless separately documented |
| DASH-009 | Category interactions | MET-003/011–013 | Item/category or governed category aggregate | Category selection filters item-compatible visuals only | Disable interaction with payment and unrelated order-level visuals |
| DASH-010 | Seller semantics | MET-003/008–010 | All commercial seller items vs single-seller outcome subset | Separate concentration and outcome sections/tooltips | 1,277 multi-seller orders excluded only from outcomes |
| DASH-011 | Geography semantics | MET-003/006/008–010 | Customer State / Seller State explicitly labeled | State bars; no coordinate map | Raw geolocation prohibited; no permanent customer-residence claim |
| DASH-012 | Payment isolation | MET-014; FIND-008 | Payment fact | Optional payment-type visual with isolated interaction | Recorded Payment Value is not revenue and never joins items directly |
| DASH-013 | Visual denominator disclosure | MET-007–010/013/015 | Applicable metric grain | Tooltip, subtitle, or supporting count | Naked rate/average visuals fail acceptance |
| DASH-014 | Design and accessibility | All | All pages | Restrained theme, grid, whitespace, accessible contrast | No 3D, gauges, decorative gradients, or unsupported targets |
| DASH-015 | Runtime reconciliation | MET-001–015 | SQL controls vs executed DAX | Manual checklist until Desktop is available | Cannot pass until 15 DAX values are executed and entered |

## Interaction policy

- Date, Customer State, Category, and page-appropriate Delivery Outcome are the primary slicers.
- Relationships are single-direction from dimensions/order to child facts. No bidirectional or many-to-many relationship is authorized.
- Category/seller aggregate visuals are display tables and must not cross-filter incompatible payment or customer-state tables.
- MET-001 retains all statuses; commercial, delivery, review, and payment measures apply their own populations inside DAX.

## Visual semantics

- Neutral commercial metrics use blue; on-time uses teal; late/warning uses orange-red; censored/no-activity uses gray.
- Partial periods use dashed/outlined markers and explicit tooltips. `NO_OBSERVED_ACTIVITY` remains blank/NA, not fabricated zero.
- Currency displays as BRL, counts as integers, percentages to 1–2 decimals, days/scores to two decimals.
- No RFM page, score, slicer, or segment is permitted.
