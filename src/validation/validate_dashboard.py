"""Validate the Phase 7 Power BI implementation package without fabricating DAX execution."""
from pathlib import Path
import csv,sys
import duckdb,pandas as pd
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'data'/'processed'/'powerbi'; R=ROOT/'reports'/'dashboard'; tests=[]; exports=[]
def test(tid,name,ok,severity='CRITICAL',notes=''): tests.append({'test_id':tid,'test_name':name,'status':'PASS' if ok else 'FAIL','severity':severity,'notes':notes})
def main():
 manifest=pd.read_csv(R/'powerbi-data-manifest.csv'); test('DASH-EXP-001','eleven governed exports registered',len(manifest)==11); test('DASH-EXP-002','all export files exist',all((ROOT/p).exists() for p in manifest.output_file))
 con=duckdb.connect(); keys={'bi_orders':'order_id','bi_order_items':'order_id,order_item_id','bi_payments':'order_id,payment_sequential','bi_order_reviews':'order_id','dim_date':'date','dim_customer_identity':'customer_unique_id','bi_monthly_trends':'year_month','bi_category_performance':'category','bi_customer_state':'customer_state','bi_customer_frequency':'frequency_group','bi_delivery_review':'delivery_outcome'}
 for _,m in manifest.iterrows():
  name=m.table_name; path=(ROOT/m.output_file).as_posix(); key=keys[name]; rows=con.execute(f"select count(*) from read_csv_auto('{path}')").fetchone()[0]; distinct=con.execute(f"select count(*) from (select distinct {key} from read_csv_auto('{path}'))").fetchone()[0]
  status='PASS' if rows==int(m.rows) and rows==distinct else 'FAIL'; exports.append({'test_id':f'DASH-EXPORT-{name}','table_name':name,'expected_rows':int(m.rows),'observed_rows':rows,'key':key,'distinct_keys':distinct,'hash':m['hash'],'status':status,'notes':'Deterministic governed export'})
 con.close(); test('DASH-EXP-003','all export grains and keys validate',all(x['status']=='PASS' for x in exports))
 dax=pd.read_csv(R/'dax-measure-catalog.csv'); test('DASH-DAX-001','DAX catalog covers MET-001 through MET-015',dax.metric_id.nunique()==15); test('DASH-DAX-002','DAX execution honestly remains pending',(dax.execution_status=='PENDING_POWER_BI_EXECUTION').all())
 rel=pd.read_csv(R/'powerbi-relationships.csv'); test('DASH-REL-001','relationships are single direction',(rel.cross_filter_direction=='single').all()); test('DASH-REL-002','no item-payment relationship',not any(('item' in a and 'payment' in b) or ('payment' in a and 'item' in b) for a,b in zip(rel.from_table,rel.to_table)))
 visuals=pd.read_csv(R/'visual-catalog.csv'); test('DASH-VIS-001','visual IDs are unique',len(visuals)==visuals.visual_id.nunique()); test('DASH-VIS-002','all visuals have business questions',visuals.business_question.notna().all())
 test('DASH-RFM-001','no RFM measure segmentation page or slicer',not dax.display_name.str.contains('RFM',case=False).any() and not visuals.visual_type.str.contains('segment|quadrant',case=False,regex=True).any())
 test('DASH-TERM-001','governed display names contain no forbidden KPI terms',not dax.display_name.str.contains('Revenue|Profit|Margin|CLV|Lifetime Value|Retention Rate',case=False,regex=True).any())
 test('DASH-GEO-001','raw geolocation is not exported',not manifest.table_name.str.contains('geolocation',case=False).any())
 months=pd.read_csv(OUT/'bi_monthly_trends.csv'); counts=months.period_status.value_counts().to_dict(); nov=months[months.year_month.astype(str).str.startswith('2016-11')].iloc[0]
 test('DASH-PERIOD-001','26-month scaffold preserved',len(months)==26); test('DASH-PERIOD-002','period classifications preserved',counts=={'COMPLETE_PERIOD':19,'PARTIAL_PERIOD':6,'NO_OBSERVED_ACTIVITY':1}); test('DASH-PERIOD-003','November 2016 remains null no-activity',nov.period_status=='NO_OBSERVED_ACTIVITY' and pd.isna(nov.total_orders))
 test('DASH-FILE-001','no fabricated PBIX exists',not any((ROOT/'dashboard').glob('*.pbix'))); test('DASH-FILE-002','no fabricated dashboard screenshots exist',not any((ROOT/'reports'/'dashboard').glob('*.png')))
 with (R/'powerbi-export-validation.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(exports[0]));w.writeheader();w.writerows(exports)
 with (R/'dashboard-validation-results.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(tests[0]));w.writeheader();w.writerows(tests)
 fails=sum(t['status']=='FAIL' for t in tests)+sum(x['status']=='FAIL' for x in exports); print(f'Dashboard validation: governance={len(tests)} exports={len(exports)} fails={fails}'); sys.exit(1 if fails else 0)
if __name__=='__main__':main()
