# Governed DAX Measures

Create a dedicated `_Measures` table and add the following measures. The metric contract remains authoritative.

```DAX
-- DAX-001 / MET-001
Total Orders = DISTINCTCOUNT(bi_orders[order_id])

-- DAX-002 / MET-002
Delivered Status Orders = CALCULATE(DISTINCTCOUNT(bi_orders[order_id]), bi_orders[order_status] = "delivered")

-- DAX-003 / MET-003
Product GMV = CALCULATE(SUM(bi_order_items[price]), bi_order_items[is_commercially_eligible] = TRUE())

-- DAX-004 / MET-004
Gross Order Value = CALCULATE(SUMX(bi_order_items, bi_order_items[price] + bi_order_items[freight_value]), bi_order_items[is_commercially_eligible] = TRUE())

-- DAX-005 / MET-005
Average Order Value (Product GMV) = CALCULATE(AVERAGE(bi_orders[product_gmv]), bi_orders[is_commercially_eligible] = TRUE(), bi_orders[has_items] = TRUE())

-- DAX-006 / MET-006
Observed Unique Customers = CALCULATE(DISTINCTCOUNT(bi_orders[customer_unique_id]), bi_orders[is_commercially_eligible] = TRUE())

-- DAX-007 / MET-007
Observed Repeat Customer Rate =
VAR CustomerOrders =
    GROUPBY(FILTER(bi_orders, bi_orders[is_commercially_eligible] = TRUE()), bi_orders[customer_unique_id], "EligibleOrders", COUNTX(CURRENTGROUP(), bi_orders[order_id]))
RETURN DIVIDE(COUNTROWS(FILTER(CustomerOrders, [EligibleOrders] >= 2)), COUNTROWS(CustomerOrders))

-- DAX-008 / MET-008
Average Delivery Lead Time = CALCULATE(AVERAGE(bi_orders[delivery_lead_time_days]), bi_orders[is_delivery_metric_eligible] = TRUE())

-- DAX-009 / MET-009
Late Delivery Rate =
DIVIDE(CALCULATE(COUNTROWS(bi_orders), bi_orders[is_delivery_metric_eligible] = TRUE(), bi_orders[is_late_delivery] = TRUE()), CALCULATE(COUNTROWS(bi_orders), bi_orders[is_delivery_metric_eligible] = TRUE(), NOT ISBLANK(bi_orders[is_late_delivery])))

-- DAX-010 / MET-010
Average Order-Level Review Score = AVERAGE(bi_order_reviews[mean_review_score])

-- DAX-011 / MET-011
Item Volume = CALCULATE(COUNTROWS(bi_order_items), bi_order_items[is_commercially_eligible] = TRUE())

-- DAX-012 / MET-012
Freight Value = CALCULATE(SUM(bi_order_items[freight_value]), bi_order_items[is_commercially_eligible] = TRUE())

-- DAX-013 / MET-013
Freight Burden =
VAR Freight = CALCULATE(SUM(bi_order_items[freight_value]), bi_order_items[is_commercially_eligible] = TRUE())
VAR Gross = CALCULATE(SUMX(bi_order_items, bi_order_items[price] + bi_order_items[freight_value]), bi_order_items[is_commercially_eligible] = TRUE())
RETURN DIVIDE(Freight, Gross)

-- DAX-014 / MET-014
Recorded Payment Value = SUM(bi_payments[payment_value])

-- DAX-015 / MET-015
On-time Delivery Rate =
DIVIDE(CALCULATE(COUNTROWS(bi_orders), bi_orders[is_delivery_metric_eligible] = TRUE(), bi_orders[is_on_time_delivery] = TRUE()), CALCULATE(COUNTROWS(bi_orders), bi_orders[is_delivery_metric_eligible] = TRUE(), NOT ISBLANK(bi_orders[is_on_time_delivery])))
```

MET-009 and MET-015 must return the same denominator. Execute all measures in an unfiltered validation page before accepting the report.

