"""Idempotent DuckDB analytical-model build and hard reconciliation gate."""
from pathlib import Path
import csv, sys
import duckdb

ROOT=Path(__file__).resolve().parents[2]; RAW=ROOT/'data'/'raw'; DB=ROOT/'data'/'interim'/'olist_analytics.duckdb'; OUT=ROOT/'reports'/'model'
sys.path.insert(0,str(ROOT/'src'/'validation'))
from validate_raw_integrity import validate

def run_sql(con,path):
    sql=path.read_text(encoding='utf-8').replace('{{RAW}}',RAW.as_posix().replace("'","''"))
    con.execute(sql)
def q(con,sql): return con.execute(sql).fetchone()[0]
def main():
    missing,extra,changed=validate()
    if missing or extra or changed: raise RuntimeError(f'Raw integrity failed: {missing=} {extra=} {changed=}')
    OUT.mkdir(parents=True,exist_ok=True); DB.parent.mkdir(parents=True,exist_ok=True)
    con=duckdb.connect(str(DB)); run_sql(con,ROOT/'sql'/'staging'/'create_staging.sql'); run_sql(con,ROOT/'sql'/'marts'/'create_analytical_model.sql')
    tests=[]
    def test(tid,mid,name,expected,observed,severity='CRITICAL',mets=''):
        status='PASS' if str(expected)==str(observed) else 'FAIL'; tests.append([tid,mid,name,expected,observed,status,severity,mets,''])
    pairs=[('MODEL-001','fact_orders','order_id'),('MODEL-002','fact_order_items','order_id,order_item_id'),('MODEL-003','fact_payments','order_id,payment_sequential'),('MODEL-005','fact_order_reviews','order_id'),('MODEL-006','dim_customer_identity','customer_unique_id'),('MODEL-007','dim_products','product_id'),('MODEL-008','dim_sellers','seller_id'),('MODEL-009','dim_date','date'),('MODEL-010','agg_order_items','order_id'),('MODEL-011','agg_order_payments','order_id'),('MODEL-012','mart_order_analytics','order_id')]
    for n,(mid,table,key) in enumerate(pairs,1):
        dup=q(con,f'SELECT count(*)-count(DISTINCT ({key})) FROM {table}') if ',' not in key else q(con,f'SELECT count(*)-(SELECT count(*) FROM (SELECT DISTINCT {key} FROM {table})) FROM {table}')
        test(f'MODEL-KEY-{n:03d}',mid,f'{table} key uniqueness',0,dup,mets='MET-001–MET-015')
    controls=[
      ('MODEL-ROW-001','MODEL-001','fact_orders rows',q(con,'select count(*) from stg_orders'),q(con,'select count(*) from fact_orders')),
      ('MODEL-ROW-002','MODEL-002','item rows',q(con,'select count(*) from stg_order_items'),q(con,'select count(*) from fact_order_items')),
      ('MODEL-ROW-003','MODEL-003','payment rows',q(con,'select count(*) from stg_payments'),q(con,'select count(*) from fact_payments')),
      ('MODEL-ROW-004','MODEL-004','review event rows',q(con,'select count(*) from stg_reviews'),q(con,'select count(*) from fact_review_events')),
      ('MODEL-ROW-005','MODEL-007','product rows',q(con,'select count(*) from stg_products'),q(con,'select count(*) from dim_products')),
      ('MODEL-ROW-006','MODEL-008','seller rows',q(con,'select count(*) from stg_sellers'),q(con,'select count(*) from dim_sellers')),
      ('MODEL-ROW-007','MODEL-012','mart order rows',q(con,'select count(*) from fact_orders'),q(con,'select count(*) from mart_order_analytics')),
      ('MODEL-MONEY-001','MODEL-002','item price reconciliation',q(con,'select sum(price) from stg_order_items'),q(con,'select sum(price) from fact_order_items')),
      ('MODEL-MONEY-002','MODEL-002','freight reconciliation',q(con,'select sum(freight_value) from stg_order_items'),q(con,'select sum(freight_value) from fact_order_items')),
      ('MODEL-MONEY-003','MODEL-003','payment reconciliation',q(con,'select sum(payment_value) from stg_payments'),q(con,'select sum(payment_value) from fact_payments')),
      ('MODEL-FANOUT-001','MODEL-012','mart does not inflate order rows',q(con,'select count(*) from fact_orders'),q(con,'select count(*) from mart_order_analytics')),
      ('MODEL-FANOUT-002','MODEL-010','mart item aggregate reconciles',q(con,'select sum(product_gmv) from agg_order_items'),q(con,'select sum(product_gmv) from mart_order_analytics')),
      ('MODEL-FANOUT-003','MODEL-011','mart payment aggregate reconciles',q(con,'select sum(recorded_payment_value) from agg_order_payments'),q(con,'select sum(recorded_payment_value) from mart_order_analytics'))]
    for row in controls: test(*row,mets='MET-001–MET-015')
    test('MODEL-GEO-001','MODEL-001','raw geolocation is not a model dependency',0,q(con,"select count(*) from information_schema.tables where table_name like '%geolocation%'"),mets='geographic views')
    header=['test_id','model_id','test_name','expected','observed','status','severity','related_MET_ids','notes']
    with (OUT/'model-validation-results.csv').open('w',newline='',encoding='utf-8') as f: csv.writer(f).writerows([header]+tests)
    models=['fact_orders','fact_order_items','fact_payments','fact_review_events','fact_order_reviews','dim_customer_identity','dim_products','dim_sellers','dim_date','agg_order_items','agg_order_payments','mart_order_analytics']
    with (OUT/'model-row-counts.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['model_name','row_count']); [w.writerow([m,q(con,f'select count(*) from {m}')]) for m in models]
    limited={'MET-003','MET-004','MET-005','MET-006','MET-007','MET-010','MET-012','MET-013','MET-014'}
    support={
      'MET-001':'MODEL-001;MODEL-009;MODEL-012','MET-002':'MODEL-001;MODEL-012','MET-003':'MODEL-002;MODEL-007;MODEL-010;MODEL-012',
      'MET-004':'MODEL-002;MODEL-010;MODEL-012','MET-005':'MODEL-002;MODEL-010;MODEL-012','MET-006':'MODEL-001;MODEL-006;MODEL-012',
      'MET-007':'MODEL-001;MODEL-006','MET-008':'MODEL-001;MODEL-012','MET-009':'MODEL-001;MODEL-012','MET-010':'MODEL-004;MODEL-005;MODEL-012',
      'MET-011':'MODEL-002;MODEL-010','MET-012':'MODEL-002;MODEL-010;MODEL-012','MET-013':'MODEL-002;MODEL-010;MODEL-012',
      'MET-014':'MODEL-003;MODEL-011;MODEL-012','MET-015':'MODEL-001;MODEL-012'}
    with (OUT/'metric-model-support.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['metric_id','support_status','supporting_models','notes'])
        for i in range(1,16):
            mid=f'MET-{i:03d}'; w.writerow([mid,'SUPPORTED_WITH_LIMITATION' if mid in limited else 'SUPPORTED',support[mid],'Inherits Phase 3 semantic status; model fields/grain available'])
    trace_path=ROOT/'reports'/'metric-contract'/'traceability-matrix.csv'
    with trace_path.open(encoding='utf-8',newline='') as f: trace_rows=list(csv.DictReader(f))
    for row in trace_rows: row['future_model_ids']=support[row['metric_id']]
    with trace_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=trace_rows[0].keys()); w.writeheader(); w.writerows(trace_rows)
    con.close()
    fails=sum(r[5]=='FAIL' for r in tests); print(f'DuckDB {duckdb.__version__}; tests={len(tests)} fails={fails}; database={DB}')
    if fails: sys.exit(1)
if __name__=='__main__': main()
