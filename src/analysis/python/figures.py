"""Curated deterministic Phase 6 figures."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def _save(fig,path): fig.tight_layout(); fig.savefig(path,dpi=160,bbox_inches="tight"); plt.close(fig)
def customer_frequency(df,path):
 fig,ax=plt.subplots(figsize=(7,4)); ax.bar(df.frequency_group,df.customer_share*100,color="#2878B5"); ax.set(title="Observed Customer Purchase Frequency",xlabel="Eligible orders observed per customer",ylabel="Customers (%)"); ax.text(.99,.96,"Commercial population; bounded observation window",transform=ax.transAxes,ha="right",va="top",fontsize=8); _save(fig,path)
def cohort_heatmap(matrix,path):
 data=matrix.set_index("cohort_month").iloc[:,:7].to_numpy(float); fig,ax=plt.subplots(figsize=(8,6)); cmap=plt.get_cmap("Blues").copy(); cmap.set_bad("#D9D9D9"); im=ax.imshow(np.ma.masked_invalid(data),aspect="auto",vmin=0,vmax=max(.05,np.nanmax(data[:,1:])),cmap=cmap); ax.set(title="Observed Cohort Return Rates (Complete-Period Cohorts)",xlabel="Month index",ylabel="Observed first-purchase cohort"); ax.set_yticks(range(len(matrix))); ax.set_yticklabels(matrix.cohort_month.dt.strftime('%Y-%m')); ax.set_xticks(range(data.shape[1])); fig.colorbar(im,ax=ax,label="Observed return rate"); _save(fig,path)
def delivery_hist(series,path):
 fig,ax=plt.subplots(figsize=(7,4)); ax.hist(series,bins=60,color="#2878B5"); ax.set(title="Delivery Lead-Time Distribution",xlabel="Purchase-to-delivery days",ylabel="Endpoint-qualified delivered orders"); ax.text(.99,.96,"Original values retained; governed mean unchanged",transform=ax.transAxes,ha="right",va="top",fontsize=8); _save(fig,path)
def review_compare(df,path):
 pivot=df.pivot(index="mean_review_score",columns="delivery_outcome",values="order_share").fillna(0); fig,ax=plt.subplots(figsize=(7,4)); pivot.plot(kind="bar",ax=ax,color=["#D9534F","#2878B5"]); ax.set(title="Order-Level Review Scores by Delivery Outcome",xlabel="Order-level mean review score",ylabel="Reviewed orders within outcome (%)"); ax.legend(title="Delivery outcome"); _save(fig,path)
