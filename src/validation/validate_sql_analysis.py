"""Validate Phase 5 metric reconciliation and SQL safety contracts."""
import csv, re, sys
from pathlib import Path
import duckdb

ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'data'/'interim'/'olist_analytics.duckdb'; REPORT=ROOT/'reports'/'sql-analysis'; RESULTS=REPORT/'results'

def rows(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def main():
    con=duckdb.connect(str(DB),read_only=True); core={r['metric_id']:r for r in rows(RESULTS/'core_metrics.csv')}
    controls={
      'MET-001':"select count(distinct order_id)::double from stg_orders",
      'MET-002':"select count(distinct order_id)::double from stg_orders where order_status='delivered'",
      'MET-003':"select sum(i.price)::double from stg_order_items i join stg_orders o using(order_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered')",
      'MET-004':"select sum(i.price+i.freight_value)::double from stg_order_items i join stg_orders o using(order_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered')",
      'MET-005':"select avg(v)::double from (select i.order_id,sum(i.price) v from stg_order_items i join stg_orders o using(order_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered') group by 1)",
      'MET-006':"select count(distinct c.customer_unique_id)::double from stg_orders o join stg_customers c using(customer_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered')",
      'MET-007':"select count(*) filter(where n>=2)::double/nullif(count(*),0) from (select c.customer_unique_id,count(distinct o.order_id)n from stg_orders o join stg_customers c using(customer_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered') group by 1)",
      'MET-008':"select avg(date_diff('microsecond',order_purchase_timestamp,order_delivered_customer_date)/86400000000.0) from stg_orders where order_status='delivered' and order_purchase_timestamp is not null and order_delivered_customer_date>=order_purchase_timestamp",
      'MET-009':"select count(*) filter(where order_delivered_customer_date>order_estimated_delivery_date)::double/nullif(count(*),0) from stg_orders where order_status='delivered' and order_delivered_customer_date>=order_purchase_timestamp and order_estimated_delivery_date is not null",
      'MET-010':"select avg(v) from (select order_id,avg(review_score)v from stg_reviews where review_score between 1 and 5 group by 1)",
      'MET-011':"select count(*)::double from stg_order_items i join stg_orders o using(order_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered')",
      'MET-012':"select sum(i.freight_value)::double from stg_order_items i join stg_orders o using(order_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered')",
      'MET-013':"select sum(i.freight_value)::double/nullif(sum(i.price+i.freight_value),0) from stg_order_items i join stg_orders o using(order_id) where o.order_status in ('approved','invoiced','processing','shipped','delivered')",
      'MET-014':"select sum(payment_value)::double from stg_payments",
      'MET-015':"select count(*) filter(where order_delivered_customer_date<=order_estimated_delivery_date)::double/nullif(count(*),0) from stg_orders where order_status='delivered' and order_delivered_customer_date>=order_purchase_timestamp and order_estimated_delivery_date is not null",
    }
    reconciliation=[]; tests=[]
    def test(tid,name,expected,observed,severity='CRITICAL',notes=''):
      ok=expected==observed if not isinstance(expected,float) else abs(expected-observed)<=1e-9
      tests.append({'test_id':tid,'test_name':name,'expected':expected,'observed':observed,'status':'PASS' if ok else 'FAIL','severity':severity,'notes':notes})
    for mid,sql in controls.items():
      observed=float(core[mid]['value']); control=float(con.execute(sql).fetchone()[0]); tol=0 if mid in {'MET-001','MET-002','MET-006','MET-011'} else .01 if mid in {'MET-003','MET-004','MET-005','MET-012','MET-014'} else 1e-9
      diff=observed-control; status='PASS' if abs(diff)<=tol else 'FAIL'; reconciliation.append({'metric_id':mid,'analytical_result':format(observed,'.15g'),'independent_control':format(control,'.15g'),'difference':format(diff,'.15g'),'tolerance':tol,'status':status,'notes':'Independent staging/native-grain control'})
    test('SQL-METRIC-001','all core metrics reconcile',0,sum(r['status']=='FAIL' for r in reconciliation))
    late=float(core['MET-009']['denominator']); ontime=float(core['MET-015']['denominator']); test('SQL-DENOM-001','MET-009 and MET-015 denominator equality',late,ontime)
    test('SQL-COMP-001','MET-009 and MET-015 complement',1.0,float(core['MET-009']['value'])+float(core['MET-015']['value']))
    sql_files=sorted((ROOT/'sql'/'analysis').rglob('*.sql')); ids=[]
    for p in sql_files:
      text=p.read_text(encoding='utf-8'); m=re.search(r'QUERY ID:\s*(SQL-\d+)',text); ids.append(m.group(1) if m else '')
      test('SQL-META-'+p.stem,'required metadata present',True,all(x in text for x in ['QUERY ID:','ANALYSIS ID:','BUSINESS REQUIREMENT:','METRIC DEPENDENCIES:','MODEL DEPENDENCIES:','GRAIN:','POPULATION:','DATE BASIS:','PURPOSE:']))
      low=text.lower(); test('SQL-GEO-'+p.stem,'raw geolocation absent',False,'geolocation' in low)
      unsafe=bool(re.search(r'fact_order_items\s+(?:as\s+)?\w*\s+join\s+fact_payments|fact_payments\s+(?:as\s+)?\w*\s+join\s+fact_order_items',low))
      test('SQL-SAFE-'+p.stem,'no item-payment fact join',False,unsafe)
    test('SQL-ID-001','query IDs unique and complete',len(sql_files),len(set(ids)-{''}))
    trends=rows(RESULTS/'monthly_trends.csv'); test('SQL-PERIOD-001','partial periods explicitly labeled',True,any(r['period_status']=='PARTIAL_PERIOD' for r in trends))
    test('SQL-PERIOD-002','partial periods lack headline LAG comparison',True,all(not r['previous_total_orders'] for r in trends if r['period_status']=='PARTIAL_PERIOD'))
    test('SQL-PERIOD-003','calendar scaffold contains all 26 observation-window months',26,len(trends))
    test('SQL-PERIOD-004','one no-activity month is explicit',1,sum(r['period_status']=='NO_OBSERVED_ACTIVITY' for r in trends))
    test('SQL-PERIOD-005','no-activity month remains null rather than fabricated zero',True,all(not r['total_orders'] and not r['product_gmv'] for r in trends if r['period_status']=='NO_OBSERVED_ACTIVITY'))
    test('SQL-PERIOD-006','non-complete periods lack headline LAG comparison',True,all(not r['previous_total_orders'] for r in trends if r['period_status']!='COMPLETE_PERIOD'))
    review=rows(RESULTS/'review_delivery_comparison.csv'); test('SQL-REVIEW-001','review comparison has denominators',True,all(int(r['reviewed_order_count'])>0 for r in review))
    model=rows(ROOT/'reports'/'model'/'model-validation-results.csv'); test('SQL-FANOUT-001','Phase 4 fanout tests remain PASS',0,sum(r['status']!='PASS' for r in model if r['test_id'].startswith('MODEL-FANOUT')))
    con.close()
    fields=['metric_id','analytical_result','independent_control','difference','tolerance','status','notes']; REPORT.mkdir(parents=True,exist_ok=True)
    with (REPORT/'core-metric-reconciliation.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(reconciliation)
    with (REPORT/'sql-analysis-validation-results.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(tests[0]));w.writeheader();w.writerows(tests)
    fails=sum(r['status']=='FAIL' for r in reconciliation)+sum(t['status']=='FAIL' for t in tests); print(f'SQL validation: tests={len(tests)} reconciliation={len(reconciliation)} fails={fails}')
    if fails:sys.exit(1)
if __name__=='__main__':main()
