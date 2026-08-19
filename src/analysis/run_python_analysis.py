"""Deterministic Phase 6 Python analysis pipeline."""
from pathlib import Path
import csv,hashlib,subprocess,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'data'/'interim'/'olist_analytics.duckdb'; REPORT=ROOT/'reports'/'python-analysis'; RESULTS=REPORT/'results'; FIGURES=REPORT/'figures'
sys.path.insert(0,str(Path(__file__).parent/'python'))
from data_access import connect,query,customer_frame,eligible_orders
from distributions import table
from customer_behavior import frequency_distribution,value_summary
from cohort import build as cohort_build
from rfm_feasibility import assess
import figures

def write(df,path): path.parent.mkdir(parents=True,exist_ok=True); df.to_csv(path,index=False,float_format='%.15g')
def main():
 REPORT.mkdir(parents=True,exist_ok=True); RESULTS.mkdir(parents=True,exist_ok=True); FIGURES.mkdir(parents=True,exist_ok=True); con=connect(DB)
 required={'mart_order_analytics','fact_order_items','fact_payments','fact_order_reviews','fact_orders'}; observed={x[0] for x in con.execute('select table_name from information_schema.tables').fetchall()}; assert not required-observed
 sql=pd.read_csv(ROOT/'reports'/'sql-analysis'/'core-metric-results.csv').set_index('metric_id'); rec=[]
 py={
 'MET-003':query(con,'select sum(price)::double v from fact_order_items where is_commercially_eligible').v[0],
 'MET-005':query(con,'select avg(product_gmv)::double v from mart_order_analytics where is_commercially_eligible and has_items').v[0],
 'MET-006':query(con,'select count(distinct customer_unique_id)::double v from fact_orders where is_commercially_eligible').v[0],
 'MET-007':query(con,'select count(*) filter(where n>=2)::double/count(*) v from (select customer_unique_id,count(distinct order_id)n from fact_orders where is_commercially_eligible group by 1)').v[0],
 'MET-008':query(con,'select avg(delivery_lead_time_days) v from fact_orders where is_delivery_metric_eligible').v[0],
 'MET-009':query(con,'select avg(is_late_delivery::int) v from fact_orders where is_delivery_metric_eligible and is_late_delivery is not null').v[0],
 'MET-010':query(con,'select avg(mean_review_score) v from fact_order_reviews').v[0],
 'MET-014':query(con,'select sum(payment_value)::double v from fact_payments').v[0],
 'MET-015':query(con,'select avg(is_on_time_delivery::int) v from fact_orders where is_delivery_metric_eligible and is_on_time_delivery is not null').v[0]}
 for mid,pv in py.items():
  sv=float(sql.loc[mid,'value']); tol=.01 if mid in {'MET-003','MET-005','MET-014'} else 1e-9; diff=pv-sv; rec.append({'metric_id':mid,'sql_value':sv,'python_value':pv,'difference':diff,'tolerance':tol,'status':'PASS' if abs(diff)<=tol else 'FAIL','notes':'Governed model population independently queried'})
 rec=pd.DataFrame(rec); write(rec,REPORT/'python-sql-reconciliation.csv');
 if (rec.status=='FAIL').any(): raise RuntimeError('Python/SQL reconciliation failed')
 customers=customer_frame(con); orders=eligible_orders(con)
 delivery=query(con,'select delivery_lead_time_days from fact_orders where is_delivery_metric_eligible')
 reviews=query(con,'select mean_review_score from fact_order_reviews')
 dist=table([('order_product_gmv',orders.product_gmv,'item-bearing commercial orders'),('order_item_count',orders.item_count,'item-bearing commercial orders'),('order_freight_value',orders.freight_value,'item-bearing commercial orders'),('order_freight_burden',orders.freight_burden,'item-bearing commercial orders'),('delivery_lead_time_days',delivery.delivery_lead_time_days,'endpoint-qualified delivered orders'),('order_level_review_score',reviews.mean_review_score,'all reviewed orders'),('customer_eligible_order_count',customers.eligible_order_count,'observed commercial customers'),('observed_customer_product_gmv',customers.observed_customer_product_gmv,'observed commercial customers')]); write(dist,RESULTS/'distribution-summary.csv')
 freq=frequency_distribution(customers); value=value_summary(customers); write(freq,RESULTS/'customer-frequency-distribution.csv'); write(value,RESULTS/'customer-value-summary.csv')
 presence=query(con,'select distinct customer_unique_id,order_purchase_timestamp from fact_orders where is_commercially_eligible'); presence.order_purchase_timestamp=pd.to_datetime(presence.order_purchase_timestamp)
 month_status=pd.read_csv(ROOT/'reports'/'sql-analysis'/'results'/'monthly_trends.csv',usecols=['year_month','period_status']); obs,matrix,cohort_summary=cohort_build(presence,month_status); write(obs,REPORT/'cohort-observability.csv'); write(matrix,RESULTS/'cohort-return-matrix.csv'); write(cohort_summary,RESULTS/'cohort-summary.csv')
 cutoff=pd.Timestamp(presence.order_purchase_timestamp.max()); rfm,status,f_one=assess(customers,cutoff); rfm['cutoff_timestamp']=cutoff; rfm['final_feasibility_status']=status; rfm['frequency_one_share']=f_one; write(rfm,RESULTS/'rfm-feasibility.csv')
 delivery_summary=dist[dist.variable=='delivery_lead_time_days'].copy(); write(delivery_summary,RESULTS/'delivery-distribution-summary.csv')
 review_dist=query(con,'select mean_review_score,count(*) reviewed_orders,count(*)::double/sum(count(*)) over() order_share from fact_order_reviews group by 1 order by 1'); write(review_dist,RESULTS/'review-distribution.csv')
 review_delivery=query(con,"""select case when is_late_delivery then 'LATE' else 'ON_TIME' end delivery_outcome,mean_review_score,count(*) reviewed_orders from mart_order_analytics where is_delivery_metric_eligible and is_late_delivery is not null and has_review group by 1,2 order by 1,2"""); review_delivery['order_share']=review_delivery.groupby('delivery_outcome').reviewed_orders.transform(lambda x:x/x.sum()); write(review_delivery,RESULTS/'review-delivery-statistics.csv')
 complete=set(pd.to_datetime(month_status.loc[month_status.period_status=='COMPLETE_PERIOD','year_month'])); headline=matrix[matrix.cohort_month.isin(complete)].copy(); figures.customer_frequency(freq,FIGURES/'fig-001-customer-frequency.png'); figures.cohort_heatmap(headline,FIGURES/'fig-002-observed-cohort-heatmap.png'); figures.delivery_hist(delivery.delivery_lead_time_days,FIGURES/'fig-003-delivery-distribution.png'); figures.review_compare(review_delivery.rename(columns={'reviewed_orders':'n'}),FIGURES/'fig-004-review-delivery.png')
 manifest=pd.DataFrame([
 ['FIG-001','AN-003','Observed Customer Purchase Frequency','How concentrated is observed frequency?','MODEL-001;MODEL-012','commercial customers','eligible order count','figures/fig-001-customer-frequency.png','PYFIND-002','Bounded window',True,''],
 ['FIG-002','AN-004','Observed Cohort Return Rates','What repeat activity is observable by cohort?','MODEL-001','complete-period observed first-purchase cohorts','observed cohort return rate','figures/fig-002-observed-cohort-heatmap.png','PYFIND-004','Censored cells masked',True,'Month 0 is construction'],
 ['FIG-003','AN-008','Delivery Lead-Time Distribution','How dispersed are delivery times?','MODEL-001','endpoint-qualified delivered orders','delivery lead time','figures/fig-003-delivery-distribution.png','PYFIND-006','Long values preserved',True,'Diagnostic median does not replace KPI'],
 ['FIG-004','AN-010','Order-Level Review Scores by Delivery Outcome','How do score distributions differ?','MODEL-005;MODEL-012','endpoint-qualified reviewed orders','order-level review score','figures/fig-004-review-delivery.png','PYFIND-007','Association only',True,''] ],columns=['figure_id','analysis_id','title','analytical_question','source_model','population','metric_or_variable','output_file','finding_ids','limitation','portfolio_candidate','notes']); write(manifest,REPORT/'figure-manifest.csv')
 create_reports(dist,freq,value,obs,cohort_summary,rfm,status,cutoff,f_one,review_delivery)
 con.close(); subprocess.run([sys.executable,str(ROOT/'src/validation/validate_python_analysis.py')],check=True,cwd=ROOT)
 files=sorted(list(RESULTS.glob('*.csv'))+[REPORT/'cohort-observability.csv',REPORT/'python-sql-reconciliation.csv',REPORT/'finding-evidence-register.csv',REPORT/'figure-manifest.csv'])
 hashes=pd.DataFrame([{'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'row_count':sum(1 for _ in p.open(encoding='utf-8'))-1} for p in files]); write(hashes,REPORT/'result-manifest.csv'); print(f'Python analysis complete: results={len(files)} figures=4 status={status}')

def create_reports(dist,freq,value,obs,coh,rfm,status,cutoff,f_one,review_delivery):
 d={r.variable:r for _,r in dist.iterrows()}; m1=coh[(coh.cohort_period_status=='COMPLETE_PERIOD')&coh.month_1_observable].month_1_return_rate.mean(); m2=coh[(coh.cohort_period_status=='COMPLETE_PERIOD')&coh.month_2_observable].month_2_return_rate.mean(); m3=coh[(coh.cohort_period_status=='COMPLETE_PERIOD')&coh.month_3_observable].month_3_return_rate.mean();
 late=review_delivery[review_delivery.delivery_outcome=='LATE']; on=review_delivery[review_delivery.delivery_outcome=='ON_TIME']; late_mean=np.average(late.mean_review_score,weights=late.reviewed_orders); on_mean=np.average(on.mean_review_score,weights=on.reviewed_orders)
 fs=[
 ['PYFIND-001','AN-001','MODEL-010','run_python_analysis.py','How skewed is order Product GMV?',f"Order Product GMV was right-skewed: mean BRL {d['order_product_gmv']['mean']:.2f}, median BRL {d['order_product_gmv']['median']:.2f}, P99 BRL {d['order_product_gmv']['p99']:.2f}.",'item-bearing commercial orders',int(d['order_product_gmv']['count']),'mean/median/P99',f"skew={d['order_product_gmv']['skewness']}",'','Extreme values retained','FIND-001','SUPPORTED'],
 ['PYFIND-002','AN-003','MODEL-001;MODEL-012','run_python_analysis.py','What is the full observed frequency distribution?',f"Customers with one eligible order represented {freq.iloc[0].customer_share*100:.2f}% of observed commercial customers; maximum frequency was {int(d['customer_eligible_order_count']['maximum'])}.",'observed commercial customers',int(freq.observed_customers.sum()),'frequency distribution',freq.to_json(orient='records'),'FIG-001','Not lifetime behavior','FIND-002','SUPPORTED_WITH_LIMITATION'],
 ['PYFIND-003','AN-003','MODEL-012','run_python_analysis.py','How concentrated is observed customer Product GMV?',f"Median observed customer Product GMV was BRL {value.iloc[0]['median']:.2f}; the top 10% accounted for {value.iloc[0].top_10pct_share*100:.2f}%.",'observed commercial customers',int(value.iloc[0].observed_customers),'median/top-decile share',f"top1={value.iloc[0].top_1pct_share:.12f}; top10={value.iloc[0].top_10pct_share:.12f}",'','Not lifetime value','FIND-002','SUPPORTED_WITH_LIMITATION'],
 ['PYFIND-004','AN-004','MODEL-001','run_python_analysis.py','What repeat activity is observable after first observed purchase?',f"Across eligible complete-period cohorts with observable follow-up, mean observed return rates were {m1*100:.2f}% at month 1, {m2*100:.2f}% at month 2, and {m3*100:.2f}% at month 3.",'complete-period observed first-purchase cohorts','varies by horizon','mean cohort return rate',f"m1={m1};m2={m2};m3={m3}",'FIG-002','Unweighted cohort mean; right censoring and prior history unknown','','SUPPORTED_WITH_LIMITATION'],
 ['PYFIND-005','AN-005','MODEL-001;MODEL-012','run_python_analysis.py','Is classic RFM informative?',f"Classic RFM was {status}: Frequency equaled one for {f_one*100:.2f}% of customers and could not form five natural quantile bins without tie-breaking.",'observed commercial customers',int(freq.observed_customers.sum()),'qcut feasibility',rfm.to_json(orient='records'),'','Bounded history and partial final month','','SUPPORTED_WITH_LIMITATION'],
 ['PYFIND-006','AN-008','MODEL-001','run_python_analysis.py','How dispersed is delivery lead time?',f"The governed mean was {d['delivery_lead_time_days']['mean']:.2f} days versus a diagnostic median of {d['delivery_lead_time_days']['median']:.2f}; P95 was {d['delivery_lead_time_days']['p95']:.2f} days.",'endpoint-qualified delivered orders',int(d['delivery_lead_time_days']['count']),'mean/median/P95',f"p99={d['delivery_lead_time_days']['p99']};max={d['delivery_lead_time_days']['maximum']}",'FIG-003','Mean KPI unchanged; long observations retained','FIND-005','SUPPORTED'],
 ['PYFIND-007','AN-010','MODEL-005;MODEL-012','run_python_analysis.py','How do review distributions differ by delivery outcome?',f"Late reviewed orders averaged {late_mean:.2f} versus {on_mean:.2f} for on-time reviewed orders; score distributions differ descriptively.",'endpoint-qualified reviewed orders',int(late.reviewed_orders.sum()+on.reviewed_orders.sum()),'weighted order-level mean difference',f"late={late_mean};on_time={on_mean};difference={late_mean-on_mean}",'FIG-004','Observed association; not causal','FIND-006','SUPPORTED_WITH_LIMITATION']]
 cols=['finding_id','analysis_id','source_model','notebook_or_script','business_question','finding_statement','population','denominator','statistic','numerical_evidence','figure_id','limitation','SQL_comparison','status']; fdf=pd.DataFrame(fs,columns=cols); write(fdf,REPORT/'finding-evidence-register.csv')
 lines=['# Phase 6 Python Findings','','Descriptive evidence only; no final recommendations.']
 sections={'Distribution Diagnostics':['PYFIND-001'],'Customer Behavior':['PYFIND-002','PYFIND-003'],'Cohort Analysis':['PYFIND-004'],'RFM Feasibility':['PYFIND-005'],'Delivery Distribution':['PYFIND-006'],'Customer Experience':['PYFIND-007']}; lookup=fdf.set_index('finding_id')
 for sec,ids in sections.items():
  lines += ['',f'## {sec}']
  for fid in ids:
   r=lookup.loc[fid]; lines += ['',f'### {fid}','',f"**Finding:** {r.finding_statement}",'',f"**Evidence:** {r.numerical_evidence}",'',f"**Population:** {r.population} (denominator: {r.denominator}).",'',f"**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.",'',f"**Limitation:** {r.limitation}",'',f"**Traceability:** {r.analysis_id} / {r.source_model}; figure {r.figure_id or 'none'}; SQL comparison {r.SQL_comparison or 'none'}." ]
 (REPORT/'findings.md').write_text('\n'.join(lines),encoding='utf-8')
 (REPORT/'rfm-feasibility.md').write_text(f"""# RFM Feasibility Assessment\n\n**Final status: {status}**\n\nRecency is days from the last observed eligible purchase to the deterministic maximum eligible purchase timestamp, `{cutoff}`. Frequency is eligible commercial order count by `customer_unique_id`. Monetary is Observed Customer Product GMV, not lifetime value.\n\nFrequency equals one for {f_one*100:.2f}% of customers. Five-bin `qcut` without artificial tie-breaking collapses Frequency bins, so classic balanced RFM scoring is not defensible. Recency and Monetary vary, but the bounded history, partial final month, and unknown purchases outside the source window can alter classification. No segmentation was created.\n\nThis conclusion does not show that customer differentiation is impossible; it shows that classic three-component quantile RFM is not recommended for this observation window.\n""",encoding='utf-8')
 coverage=pd.DataFrame([['BR-007','AN-004','ANSWERED','cohort-return-matrix.csv','PYFIND-004','Observed-first-purchase cohorts; censoring explicit'],['BR-008','AN-005','ANSWERED — RFM NOT RECOMMENDED','rfm-feasibility.csv','PYFIND-005','No forced segmentation']],columns=['business_requirement_id','analysis_id','status','evidence_output','finding_id','limitation']); write(coverage,REPORT/'business-question-coverage.csv')
 trace=fdf[['analysis_id','source_model','notebook_or_script','figure_id','finding_id','status']].copy(); trace.insert(0,'business_requirement_ids',['BR-001;BR-002','BR-005;BR-006','BR-005;BR-006','BR-007','BR-008','BR-015;BR-017','BR-019']); trace['result']='reports/python-analysis/results/'; write(trace,REPORT/'traceability-matrix.csv')

if __name__=='__main__': main()
