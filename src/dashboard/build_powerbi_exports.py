"""Build deterministic governed CSV exports for manual Power BI implementation."""
from pathlib import Path
import csv,hashlib,subprocess,sys
import duckdb
ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'data'/'interim'/'olist_analytics.duckdb'; OUT=ROOT/'data'/'processed'/'powerbi'; REPORT=ROOT/'reports'/'dashboard'
EXPORTS={
'bi_orders':("MODEL-012","one row per order","order_id","MET-001;MET-002;MET-005–MET-010;MET-015","select *,order_purchase_timestamp::date purchase_date from mart_order_analytics order by order_id"),
'bi_order_items':("MODEL-002;MODEL-007;MODEL-008","one row per order item","order_id + order_item_id","MET-003;MET-004;MET-011–MET-013","select i.*,i.order_purchase_timestamp::date purchase_date,p.approved_display_category,p.category_translation_status,s.seller_state from fact_order_items i left join dim_products p using(product_id) left join dim_sellers s using(seller_id) order by order_id,order_item_id"),
'bi_payments':("MODEL-003","one row per payment sequence","order_id + payment_sequential","MET-014","select *,order_purchase_timestamp::date purchase_date from fact_payments order by order_id,payment_sequential"),
'bi_order_reviews':("MODEL-005","one row per reviewed order","order_id","MET-010","select * from fact_order_reviews order by order_id"),
'dim_date':("MODEL-009","one row per date","date","MET-001–MET-015","select * from dim_date order by date"),
'dim_customer_identity':("MODEL-006","one row per observed stable customer","customer_unique_id","MET-006;MET-007","select * from dim_customer_identity order by customer_unique_id"),
'bi_monthly_trends':("SQL-003","one row per calendar month","year_month","MET-001;MET-003;MET-005;MET-006;MET-009;MET-015","select * from read_csv_auto('"+(ROOT/'reports/sql-analysis/results/monthly_trends.csv').as_posix()+"') order by year_month"),
'bi_category_performance':("SQL-005","one row per category","category","MET-003;MET-010–MET-013","select * from read_csv_auto('"+(ROOT/'reports/sql-analysis/results/category_performance.csv').as_posix()+"') order by product_gmv_rank,category"),
'bi_customer_state':("SQL-009","one row per Customer State","customer_state","MET-001;MET-003;MET-005;MET-006;MET-008–MET-010","select * from read_csv_auto('"+(ROOT/'reports/sql-analysis/results/customer_state_performance.csv').as_posix()+"') order by product_gmv desc nulls last,customer_state"),
'bi_customer_frequency':("PYFIND-002","one row per observed frequency group","frequency_group","MET-006;MET-007","select * from read_csv_auto('"+(ROOT/'reports/python-analysis/results/customer-frequency-distribution.csv').as_posix()+"') order by try_cast(replace(frequency_group,'+','') as int)"),
'bi_delivery_review':("SQL-008","one row per delivery outcome","delivery_outcome","MET-009;MET-010;MET-015","select * from read_csv_auto('"+(ROOT/'reports/sql-analysis/results/review_delivery_comparison.csv').as_posix()+"') order by delivery_outcome")}
def main():
 OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True); con=duckdb.connect(str(DB),read_only=True); manifest=[]
 for name,(model,grain,key,mets,sql) in EXPORTS.items():
  path=OUT/f'{name}.csv'; con.execute(f"copy ({sql}) to '{path.as_posix()}' (header,delimiter ',')"); rows=con.execute(f'select count(*) from ({sql})').fetchone()[0]
  manifest.append({'table_name':name,'source_model':model,'model_id':model if model.startswith('MODEL') else 'reporting output','grain':grain,'rows':rows,'primary_key':key,'output_file':path.relative_to(ROOT).as_posix(),'generated_at_or_build_version':'Phase 7 deterministic build v1','hash':hashlib.sha256(path.read_bytes()).hexdigest(),'supported_metrics':mets,'notes':'Rebuildable; do not edit manually'})
 con.close()
 with (REPORT/'powerbi-data-manifest.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
 subprocess.run([sys.executable,str(ROOT/'src/validation/validate_dashboard.py')],check=True,cwd=ROOT); print(f'Power BI exports complete: tables={len(manifest)}')
if __name__=='__main__':main()
