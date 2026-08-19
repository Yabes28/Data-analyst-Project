"""Observed-first-purchase cohort analysis with explicit calendar censoring."""
import numpy as np
import pandas as pd

def build(order_presence, month_status):
    x=order_presence.copy(); x["activity_month"]=x.order_purchase_timestamp.dt.to_period("M").dt.to_timestamp()
    first=x.groupby("customer_unique_id").activity_month.min().rename("cohort_month"); x=x.join(first,on="customer_unique_id")
    x["month_index"]=(x.activity_month.dt.year-x.cohort_month.dt.year)*12+x.activity_month.dt.month-x.cohort_month.dt.month
    presence=x.drop_duplicates(["customer_unique_id","cohort_month","month_index"])
    sizes=presence[presence.month_index==0].groupby("cohort_month").customer_unique_id.nunique().rename("cohort_size")
    counts=presence.groupby(["cohort_month","month_index"]).customer_unique_id.nunique().rename("observed_return_customers")
    status=dict(zip(pd.to_datetime(month_status.year_month),month_status.period_status)); rows=[]
    max_index=int(x.month_index.max())
    for cohort_month,size in sizes.items():
      cohort_status=status.get(cohort_month,"PARTIAL_PERIOD")
      for idx in range(max_index+1):
        target=cohort_month+pd.DateOffset(months=idx); target_status=status.get(target)
        observable=(idx==0) or target_status=="COMPLETE_PERIOD"
        n=int(counts.get((cohort_month,idx),0)) if observable else np.nan
        rows.append({"cohort_month":cohort_month,"cohort_period_status":cohort_status,"month_index":idx,"cohort_size":int(size),"observed_return_customers":n,"return_rate":n/size if observable else np.nan,"observable":observable,"censoring_reason":"" if observable else ("TARGET_PARTIAL_PERIOD" if target_status=="PARTIAL_PERIOD" else "TARGET_NOT_OBSERVED_OR_NO_ACTIVITY")})
    obs=pd.DataFrame(rows); matrix=obs.pivot(index="cohort_month",columns="month_index",values="return_rate").reset_index()
    summary=[]
    for cohort,row in obs.groupby("cohort_month"):
      d={"cohort_month":cohort,"cohort_period_status":row.cohort_period_status.iloc[0],"cohort_size":row.cohort_size.iloc[0]}
      for k in (1,2,3):
        cell=row[row.month_index==k]; d[f"month_{k}_return_rate"]=cell.return_rate.iloc[0] if len(cell) else np.nan; d[f"month_{k}_observable"]=bool(cell.observable.iloc[0]) if len(cell) else False
      summary.append(d)
    return obs,matrix,pd.DataFrame(summary)

