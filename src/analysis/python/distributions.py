"""Reusable descriptive distribution summaries; no anomaly removal."""
import pandas as pd

def summarize(name, series, population, kind="Diagnostic Statistic"):
    s=pd.to_numeric(series,errors="coerce"); valid=s.dropna(); q=valid.quantile([.25,.5,.75,.9,.95,.99])
    return {"variable":name,"statistic_type":kind,"population":population,"count":len(valid),"missing_count":int(s.isna().sum()),
      "zero_count":int((valid==0).sum()),"mean":valid.mean(),"median":q.loc[.5],"std":valid.std(),"minimum":valid.min(),
      "p25":q.loc[.25],"p75":q.loc[.75],"p90":q.loc[.9],"p95":q.loc[.95],"p99":q.loc[.99],"maximum":valid.max(),"skewness":valid.skew()}

def table(series_map): return pd.DataFrame([summarize(*args) for args in series_map])

