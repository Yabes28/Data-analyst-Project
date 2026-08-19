"""Evidence-first RFM feasibility testing without forced segmentation."""
import pandas as pd

def assess(customers, cutoff):
    r=(cutoff-customers.observed_last_purchase_timestamp).dt.total_seconds()/86400
    f=customers.eligible_order_count.astype(int); m=customers.observed_customer_product_gmv
    rows=[]
    for name,s in [("Recency",r),("Frequency",f),("Monetary",m)]:
      s=s.dropna(); qs=s.quantile([0,.2,.4,.6,.8,1]).tolist(); unique_bounds=len(set(qs));
      try: bins=pd.qcut(s,5,duplicates="drop").cat.categories.size
      except ValueError: bins=0
      rows.append({"component":name,"count":len(s),"unique_values":s.nunique(),"minimum":s.min(),"p20":s.quantile(.2),"p40":s.quantile(.4),"median":s.median(),"p60":s.quantile(.6),"p80":s.quantile(.8),"maximum":s.max(),"skewness":s.skew(),"unique_quantile_boundaries":unique_bounds,"qcut_bins_without_tie_breaking":bins,"assessment":"INSUFFICIENT_VARIATION" if name=="Frequency" and bins<5 else "USEFUL_VARIATION"})
    freq_one=(f==1).mean(); status="NOT_RECOMMENDED" if freq_one>.9 else "FEASIBLE_WITH_LIMITATION"
    return pd.DataFrame(rows),status,freq_one
