"""Observation-window-bounded customer diagnostics."""
import pandas as pd

def frequency_distribution(customers):
    x=customers.copy(); x["frequency_group"]=x.eligible_order_count.map(lambda n:str(n) if n<5 else "5+")
    out=x.groupby("frequency_group",sort=False).agg(observed_customers=("customer_unique_id","nunique"),eligible_orders=("eligible_order_count","sum"),observed_product_gmv=("observed_customer_product_gmv","sum")).reset_index()
    order={"1":1,"2":2,"3":3,"4":4,"5+":5}; out["sort_order"]=out.frequency_group.map(order)
    out["customer_share"]=out.observed_customers/out.observed_customers.sum(); out["product_gmv_share"]=out.observed_product_gmv/out.observed_product_gmv.sum()
    return out.sort_values("sort_order").drop(columns="sort_order")

def value_summary(customers):
    s=customers.observed_customer_product_gmv.dropna(); total=s.sum(); ordered=s.sort_values(ascending=False)
    return pd.DataFrame([{"observed_customers":len(s),"mean":s.mean(),"median":s.median(),"p75":s.quantile(.75),"p90":s.quantile(.9),"p95":s.quantile(.95),"p99":s.quantile(.99),"maximum":s.max(),"skewness":s.skew(),"top_1pct_share":ordered.head(max(1,int(len(s)*.01))).sum()/total,"top_10pct_share":ordered.head(max(1,int(len(s)*.10))).sum()/total}])

