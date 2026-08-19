# Power BI Page Layout Specification

Use a 16:9 canvas, 24 px outer margin, aligned 12-column grid, and persistent page navigation.

## Page 1 — Executive Overview

**Objective:** Communicate governed portfolio scale and service context quickly.

- Top: six cards — Total Orders, Product GMV, AOV, Observed Unique Customers, Late Delivery Rate, Average Order-Level Review Score.
- Middle: monthly Product GMV/order combo chart with period-status markers; Top-5 category Product GMV bar.
- Bottom: Customer State Product GMV bar; late/on-time 100% stacked bar; approved finding callout.
- Slicers: date/year and Customer State. Category only filters compatible commercial visuals.
- Notes: 26-month scaffold; partial/no-activity legend; no global commercial filter.

## Page 2 — Commercial & Category Performance

- Top: Product GMV, Item Volume, Freight Value, Freight Burden cards.
- Middle: Top-10 category Product GMV bar; cumulative category contribution line.
- Bottom: category freight burden with gross-value denominator; seller cumulative Product GMV contribution.
- Slicers: date and category for native item visuals. Aggregate category visuals use their documented full-window context.
- Notes: concentration includes every commercial seller item; no best/worst outcome ranking.

## Page 3 — Customer & Geography

- Top: Observed Unique Customers and Observed Repeat Customer Rate cards; observation-window note.
- Middle: customer frequency distribution; Customer State Product GMV bar.
- Bottom: observed customer value concentration callout; Customer State delivery/review detail table.
- Slicers: date and Customer State.
- Notes: no retention, loyalty, CLV, permanent residence, raw coordinates, or RFM segments.

## Page 4 — Delivery & Customer Experience

- Top: Average Delivery Lead Time, Late Delivery Rate, On-time Delivery Rate, Average Order-Level Review Score.
- Middle: late/on-time share; order-level review distribution.
- Bottom: review score by delivery outcome with four denominators; Phase 6 delivery-distribution figure.
- Slicers: date, Customer State, Delivery Outcome where compatible.
- Notes: association is descriptive and non-causal; median/percentiles are diagnostics.

## Page 5 — Analytical Deep Dive

- Top: observed cohort heatmap and its censoring note.
- Middle: customer-frequency figure; RFM `NOT_RECOMMENDED` methodology card.
- Bottom: fanout prevention technical callout and governed-methodology panel.
- Slicers: none for static evidence.
- Notes: static figures are supporting evidence, not interactive substitutes.

