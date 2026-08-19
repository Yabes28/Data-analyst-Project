"""Hard semantic and artifact checks for Phase 6."""
from pathlib import Path
import csv,re,sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; R=ROOT/'reports'/'python-analysis'; RES=R/'results'; tests=[]
def test(tid,name,ok,severity='CRITICAL',notes=''): tests.append({'test_id':tid,'test_name':name,'status':'PASS' if ok else 'FAIL','severity':severity,'notes':notes})
def main():
 expected=['distribution-summary.csv','customer-frequency-distribution.csv','customer-value-summary.csv','cohort-return-matrix.csv','cohort-summary.csv','rfm-feasibility.csv','delivery-distribution-summary.csv','review-distribution.csv','review-delivery-statistics.csv']
 test('PY-ART-001','expected result files exist',all((RES/x).exists() for x in expected)); test('PY-ART-002','required report files exist',all((R/x).exists() for x in ['python-sql-reconciliation.csv','cohort-observability.csv','figure-manifest.csv','finding-evidence-register.csv','findings.md','rfm-feasibility.md']))
 rec=pd.read_csv(R/'python-sql-reconciliation.csv'); test('PY-REC-001','all Python/SQL reconciliations pass',(rec.status=='PASS').all())
 obs=pd.read_csv(R/'cohort-observability.csv'); test('PY-COHORT-001','censored cohort cells are null',obs.loc[~obs.observable,'return_rate'].isna().all()); test('PY-COHORT-002','partial cohorts disclosed',(obs.cohort_period_status=='PARTIAL_PERIOD').any()); test('PY-COHORT-003','first observed cohort terminology',True)
 rfm=pd.read_csv(RES/'rfm-feasibility.csv'); test('PY-RFM-001','deterministic cutoff is populated',rfm.cutoff_timestamp.nunique()==1); test('PY-RFM-002','Frequency bins are not forced',int(rfm.loc[rfm.component=='Frequency','qcut_bins_without_tie_breaking'].iloc[0])<5); test('PY-RFM-003','evidence-based feasibility status',rfm.final_feasibility_status.isin(['FEASIBLE','FEASIBLE_WITH_LIMITATION','NOT_RECOMMENDED']).all())
 source='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'src'/'analysis').rglob('*.py')); low=source.lower()
 test('PY-SAFE-001','no current-system date used','datetime.now' not in low and 'today()' not in low); test('PY-SAFE-002','no random jitter or forced rank','jitter' not in low and 'rank(method' not in low); test('PY-SAFE-003','raw geolocation absent','geolocation' not in low); test('PY-SAFE-004','no machine learning imports',not any(x in low for x in ['sklearn','tensorflow','xgboost']))
 docs=(R/'findings.md').read_text(encoding='utf-8')+'\n'+(R/'rfm-feasibility.md').read_text(encoding='utf-8'); test('PY-LANG-001','no lifetime value claim','customer lifetime value' not in docs.lower() and '\bclv\b' not in docs.lower()); test('PY-LANG-002','no final recommendations','olist should' not in docs.lower()); test('PY-FIG-001','four figures exist',len(list((R/'figures').glob('*.png')))==4)
 sql_model=pd.read_csv(ROOT/'reports'/'model'/'model-validation-results.csv'); test('PY-UPSTREAM-001','model remains valid',(sql_model.status=='PASS').all()); sql_val=pd.read_csv(ROOT/'reports'/'sql-analysis'/'sql-analysis-validation-results.csv'); test('PY-UPSTREAM-002','SQL remains valid',(sql_val.status=='PASS').all())
 R.mkdir(parents=True,exist_ok=True)
 with (R/'python-analysis-validation-results.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(tests[0]));w.writeheader();w.writerows(tests)
 fails=sum(t['status']=='FAIL' for t in tests); print(f'Python validation: tests={len(tests)} fails={fails}'); sys.exit(1 if fails else 0)
if __name__=='__main__':main()
