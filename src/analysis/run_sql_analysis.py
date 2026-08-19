"""Run the governed Phase 5 SQL analysis and export compact evidence artifacts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "interim" / "olist_analytics.duckdb"
REPORT = ROOT / "reports" / "sql-analysis"
RESULTS = REPORT / "results"

QUERIES = [
    ("SQL-001", "AN-001;AN-003;AN-008;AN-009;AN-011", "BR-001;BR-002;BR-005;BR-006;BR-015;BR-017;BR-018;BR-021;BR-022", "MET-001–MET-015", "MODEL-001;MODEL-002;MODEL-003;MODEL-005;MODEL-006;MODEL-010;MODEL-011;MODEL-012", "sql/analysis/00_controls/core_metrics.sql", "Calculate the approved core metric set", "native metric grain", "portfolio", "metric-specific", "order_purchase_timestamp", "core_metric_reconciliation", "core_metrics.csv"),
    ("SQL-002", "AN-001;AN-008;AN-009;AN-011", "BR-001;BR-002;BR-015;BR-018;BR-021", "MET-001–MET-015", "MODEL-001–MODEL-012", "sql/analysis/01_executive/executive_summary.sql", "Provide an executive metric result table", "portfolio", "portfolio", "metric-specific", "order_purchase_timestamp", "core_metric_reconciliation", "executive_summary.csv"),
    ("SQL-003", "AN-001", "BR-001;BR-002;BR-003", "MET-001;MET-003;MET-005;MET-006;MET-009;MET-015", "MODEL-001;MODEL-010;MODEL-012", "sql/analysis/02_trends/monthly_trends.sql", "How do comparable monthly metrics change?", "order", "month", "metric-specific", "purchase month", "period_completeness", "monthly_trends.csv"),
    ("SQL-004", "AN-003", "BR-005;BR-006", "MET-003;MET-005;MET-006;MET-007", "MODEL-001;MODEL-006;MODEL-012", "sql/analysis/03_customers/customer_frequency.sql", "What observed purchase frequencies occur?", "stable customer", "frequency group", "commercial", "purchase window", "customer_identity", "customer_frequency.csv"),
    ("SQL-005", "AN-006", "BR-009;BR-010;BR-011", "MET-003;MET-005;MET-010;MET-011–MET-013", "MODEL-001;MODEL-002;MODEL-005;MODEL-007", "sql/analysis/04_categories/category_performance.sql", "How do categories contribute and perform?", "item/order-category", "category", "metric-specific", "purchase timestamp", "item_reconciliation", "category_performance.csv"),
    ("SQL-006", "AN-007", "BR-012;BR-013;BR-014", "MET-003;MET-008–MET-011", "MODEL-001;MODEL-002;MODEL-005;MODEL-008", "sql/analysis/05_sellers/seller_performance.sql", "How concentrated is seller activity?", "item/order-seller", "seller", "commercial/single-seller outcomes", "purchase timestamp", "item_reconciliation", "seller_performance.csv"),
    ("SQL-007", "AN-008", "BR-015;BR-016;BR-017", "MET-008;MET-009;MET-015", "MODEL-001;MODEL-012", "sql/analysis/06_delivery/delivery_performance.sql", "What are endpoint-qualified delivery outcomes?", "order", "portfolio", "delivery eligible", "purchase cohort", "delivery_denominator", "delivery_performance.csv"),
    ("SQL-008", "AN-009;AN-010", "BR-018;BR-019;BR-020", "MET-009;MET-010;MET-015", "MODEL-001;MODEL-005;MODEL-012", "sql/analysis/07_customer_experience/review_delivery_comparison.sql", "Are late deliveries associated with review scores?", "order", "delivery outcome", "delivery eligible reviewed subset", "purchase timestamp", "review_policy", "review_delivery_comparison.csv"),
    ("SQL-009", "AN-002;AN-008;AN-009", "BR-004;BR-015;BR-016;BR-020", "MET-001;MET-003;MET-005;MET-006;MET-008–MET-010", "MODEL-001;MODEL-012", "sql/analysis/08_geography/customer_state_performance.sql", "How do customer-state demand and service vary?", "order", "Customer State", "metric-specific", "purchase timestamp", "state_totals", "customer_state_performance.csv"),
    ("SQL-010", "AN-011", "BR-021;BR-022", "MET-014", "MODEL-003;MODEL-011", "sql/analysis/09_payments/payment_summary.sql", "What payment behavior is recorded?", "payment sequence", "payment type", "payment bearing", "purchase timestamp", "payment_reconciliation", "payment_summary.csv"),
    ("SQL-011", "AN-011", "BR-010;BR-016;BR-021", "MET-012;MET-013", "MODEL-002", "sql/analysis/09_payments/freight_summary.sql", "What freight value and burden are recorded?", "item", "portfolio", "commercial items", "purchase timestamp", "freight_reconciliation", "freight_summary.csv"),
    ("SQL-012", "AN-006", "BR-003;BR-009;BR-011", "MET-003;MET-011", "MODEL-002;MODEL-007", "sql/analysis/04_categories/category_monthly_trends.sql", "How do predetermined major categories vary monthly?", "item", "month/category", "top-five full-window categories", "purchase month", "category_totals", "category_monthly_trends.csv"),
    ("SQL-013", "AN-009", "BR-018", "MET-010", "MODEL-004;MODEL-005", "sql/analysis/07_customer_experience/review_score_distribution.sql", "How are order-level mean review scores distributed?", "reviewed order", "score", "all reviewed orders", "purchase attribution/full window", "review_policy", "review_score_distribution.csv"),
]

METADATA = {
 "MET-001": ("Total Orders", "orders", "all statuses", "APPROVED", "Includes canceled/unavailable orders."),
 "MET-002": ("Delivered Status Orders", "orders", "delivered status", "APPROVED", "Status metric; does not require delivery timestamp."),
 "MET-003": ("Product GMV", "BRL", "commercial item population", "APPROVED_WITH_LIMITATION", "Excludes freight; not revenue or profit."),
 "MET-004": ("Gross Order Value", "BRL", "commercial item population", "APPROVED_WITH_LIMITATION", "Product price plus recorded freight; not revenue."),
 "MET-005": ("Average Order Value (Product GMV)", "BRL/order", "item-bearing commercial orders", "APPROVED_WITH_LIMITATION", "Freight excluded."),
 "MET-006": ("Observed Unique Customers", "customers", "commercial population", "APPROVED_WITH_LIMITATION", "Bounded observation window."),
 "MET-007": ("Observed Repeat Customer Rate", "ratio", "commercial customers in observed window", "APPROVED_WITH_LIMITATION", "Not retention or lifetime behavior."),
 "MET-008": ("Average Delivery Lead Time", "days", "endpoint-complete delivered orders", "APPROVED", "Timezone-naive; mean is tail-sensitive."),
 "MET-009": ("Late Delivery Rate", "ratio", "endpoint-complete delivered orders", "APPROVED", "Actual delivery later than estimate."),
 "MET-010": ("Average Order-Level Review Score", "score", "all reviewed orders", "APPROVED_WITH_LIMITATION", "Order means; repeated-review semantics unavailable."),
 "MET-011": ("Item Volume", "item lines", "commercial item population", "APPROVED", "Item lines are source sequence records."),
 "MET-012": ("Freight Value", "BRL", "commercial item population", "APPROVED_WITH_LIMITATION", "Recorded freight is not validated logistics cost."),
 "MET-013": ("Freight Burden", "ratio", "commercial item population", "APPROVED_WITH_LIMITATION", "Weighted aggregate ratio."),
 "MET-014": ("Recorded Payment Value", "BRL", "all payment rows/statuses", "APPROVED_WITH_LIMITATION", "Not revenue, cash received, or net sales."),
 "MET-015": ("On-time Delivery Rate", "ratio", "same denominator as MET-009", "APPROVED", "Actual delivery on/before estimate."),
}

def export(con, sql_path, output):
    sql = (ROOT / sql_path).read_text(encoding="utf-8").replace("{{RESULTS}}", RESULTS.as_posix().replace("'", "''")).strip().rstrip(";")
    con.execute(f"COPY ({sql}) TO '{output.as_posix()}' (HEADER, DELIMITER ',')")

def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--rebuild-model",action="store_true"); args=parser.parse_args()
    if args.rebuild_model or not DB.exists(): subprocess.run([sys.executable,str(ROOT/"src/data/build_analytical_model.py")],check=True,cwd=ROOT)
    REPORT.mkdir(parents=True,exist_ok=True); RESULTS.mkdir(parents=True,exist_ok=True)
    con=duckdb.connect(str(DB),read_only=True)
    required={"fact_orders","fact_order_items","fact_payments","fact_order_reviews","dim_products","dim_sellers","mart_order_analytics"}
    observed={r[0] for r in con.execute("select table_name from information_schema.tables").fetchall()}
    if required-observed: raise RuntimeError(f"Missing models: {sorted(required-observed)}")
    for q in QUERIES:
        output=RESULTS/q[-1]; export(con,q[5],output)
        if q[0]=="SQL-001":
            raw=read_csv(output); enriched=[]
            for row in raw:
                name,unit,pop,status,note=METADATA[row["metric_id"]]
                enriched.append({"metric_id":row["metric_id"],"metric_name":name,"value":row["value"],"unit":unit,"population":pop,"denominator":row["denominator"],"date_basis":"order_purchase_timestamp","metric_status":status,"limitation_note":note,"reconciliation_status":"PENDING"})
            write_csv(output,enriched,list(enriched[0]))
    con.close()
    subprocess.run([sys.executable,str(ROOT/"src/validation/validate_sql_analysis.py")],check=True,cwd=ROOT)
    core=read_csv(RESULTS/"core_metrics.csv"); rec={r["metric_id"]:r for r in read_csv(REPORT/"core-metric-reconciliation.csv")}
    for r in core: r["reconciliation_status"]=rec[r["metric_id"]]["status"]
    write_csv(RESULTS/"core_metrics.csv",core,list(core[0])); write_csv(RESULTS/"executive_summary.csv",core,list(core[0])); write_csv(REPORT/"core-metric-results.csv",core,list(core[0]))
    write_csv(REPORT/"query-index.csv",[
      dict(zip(["query_id","analysis_id","business_requirement_ids","metric_ids","model_ids","sql_file","business_question","calculation_grain","reporting_grain","population_rule","date_rule","validation_query","output_file"],q),status="COMPLETE",notes="Deterministic aggregated export") for q in QUERIES
    ],["query_id","analysis_id","business_requirement_ids","metric_ids","model_ids","sql_file","business_question","calculation_grain","reporting_grain","population_rule","date_rule","validation_query","output_file","status","notes"])
    create_evidence()
    hashes=[]
    for p in sorted(RESULTS.glob("*.csv")):
        hashes.append({"file":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"row_count":sum(1 for _ in p.open(encoding="utf-8"))-1})
    write_csv(REPORT/"result-manifest.csv",hashes,["file","sha256","row_count"])
    print(f"SQL analysis complete: queries={len(QUERIES)} outputs={len(hashes)}")

def create_evidence():
    core={r["metric_id"]:r for r in read_csv(RESULTS/"core_metrics.csv")}
    trends=read_csv(RESULTS/"monthly_trends.csv"); complete=[r for r in trends if r["period_status"]=="COMPLETE_PERIOD"]
    customers=read_csv(RESULTS/"customer_frequency.csv"); cats=read_csv(RESULTS/"category_performance.csv")
    sellers=read_csv(RESULTS/"seller_performance.csv"); delivery=read_csv(RESULTS/"delivery_performance.csv")[0]
    reviews={r["delivery_outcome"]:r for r in read_csv(RESULTS/"review_delivery_comparison.csv")}
    states=read_csv(RESULTS/"customer_state_performance.csv"); payments=read_csv(RESULTS/"payment_summary.csv")
    peak=max(complete,key=lambda r:float(r["product_gmv"])); one=next(r for r in customers if r["frequency_group"]=="1 order")
    total_customers=sum(int(r["observed_customers"]) for r in customers); topcat=cats[0]; top5=sum(float(r["product_gmv"]) for r in cats[:5])/sum(float(r["product_gmv"]) for r in cats)
    topseller=sellers[0]; top10=sum(float(r["product_gmv"]) for r in sellers[:10])/sum(float(r["product_gmv"]) for r in sellers)
    late=reviews["LATE"]; ontime=reviews["ON_TIME"]; topstate=states[0]; pay=payments[0]
    finding_data=[
      ("FIND-001","AN-001","SQL-003","When did complete-month Product GMV peak?",f"Among calendar-complete months, {peak['year_month']} had the highest observed Product GMV at BRL {float(peak['product_gmv']):,.2f}.","MET-003","MET-001","commercial item population",peak["total_orders"],peak["year_month"],f"Product GMV={peak['product_gmv']}","monthly_trends.csv","Boundary months excluded; descriptive observation window.","SUPPORTED"),
      ("FIND-002","AN-003","SQL-004","How prevalent was observed repeat purchasing?",f"{int(one['observed_customers']):,} of {total_customers:,} commercial customers placed exactly one eligible order; the governed observed repeat rate was {float(core['MET-007']['value'])*100:.2f}%.","MET-007","MET-006","commercial customers in observed window",total_customers,"2016-09-04 to 2018-10-17",f"one-order customers={one['observed_customers']}; repeat rate={core['MET-007']['value']}","customer_frequency.csv","Not retention or lifetime behavior; unequal exposure.","SUPPORTED_WITH_LIMITATION"),
      ("FIND-003","AN-006","SQL-005","How concentrated was category Product GMV?",f"{topcat['category']} ranked first by eligible Product GMV at BRL {float(topcat['product_gmv']):,.2f}; the top five categories represented {top5*100:.2f}% of eligible Product GMV.","MET-003","MET-011","commercial item population",topcat["item_count"],"full observed window",f"top category={topcat['product_gmv']}; top-5 share={top5}","category_performance.csv","Category outcomes have metric-specific denominators.","SUPPORTED"),
      ("FIND-004","AN-007","SQL-006","How concentrated was seller Product GMV?",f"The leading seller represented {float(topseller['product_gmv_share'])*100:.2f}% of eligible Product GMV, while the top ten represented {top10*100:.2f}%.","MET-003","MET-011","commercial item population",topseller["item_count"],"full observed window",f"top seller share={topseller['product_gmv_share']}; top-10 share={top10}","seller_performance.csv","Concentration does not establish dependency or market power; no best/worst claim.","SUPPORTED_WITH_LIMITATION"),
      ("FIND-005","AN-008","SQL-007","What were observed delivery outcomes?",f"Across {int(delivery['delivery_denominator']):,} endpoint-qualified delivered orders, average lead time was {float(delivery['average_delivery_lead_time_days']):.2f} days and {float(delivery['late_delivery_rate'])*100:.2f}% arrived after estimate.","MET-008","MET-009;MET-015","endpoint-complete delivered orders",delivery["delivery_denominator"],"full purchase-cohort window",f"mean days={delivery['average_delivery_lead_time_days']}; late rate={delivery['late_delivery_rate']}","delivery_performance.csv","Timezone-naive timestamps; mean is tail-sensitive.","SUPPORTED"),
      ("FIND-006","AN-010","SQL-008","Are late deliveries associated with review scores?",f"Reviewed late orders averaged {float(late['average_order_level_review_score']):.2f}, versus {float(ontime['average_order_level_review_score']):.2f} for reviewed on-time orders, an observed difference of {float(late['average_order_level_review_score'])-float(ontime['average_order_level_review_score']):.2f} points.","MET-010","MET-009", "endpoint-qualified delivered orders with reviewed subsets",f"late eligible={late['order_count']}; late reviewed={late['reviewed_order_count']}; on-time eligible={ontime['order_count']}; on-time reviewed={ontime['reviewed_order_count']}","full purchase-cohort window",f"late eligible={late['order_count']}; late reviewed={late['reviewed_order_count']}; late mean={late['average_order_level_review_score']}; on-time eligible={ontime['order_count']}; on-time reviewed={ontime['reviewed_order_count']}; on-time mean={ontime['average_order_level_review_score']}","review_delivery_comparison.csv","Observed association; does not establish causality.","SUPPORTED_WITH_LIMITATION"),
      ("FIND-007","AN-002","SQL-009","Which Customer State had the largest observed commercial value?",f"Customer State {topstate['customer_state']} had the largest eligible Product GMV at BRL {float(topstate['product_gmv']):,.2f}, across {int(topstate['commercial_orders']):,} commercial orders.","MET-003","MET-006","commercial orders by order-associated Customer State",topstate["commercial_orders"],"full observed window",f"Product GMV={topstate['product_gmv']}; customers={topstate['observed_unique_customers']}","customer_state_performance.csv","Order-associated geography is not permanent customer residence.","SUPPORTED_WITH_LIMITATION"),
      ("FIND-008","AN-011","SQL-010","Which recorded payment type dominated value?",f"{pay['payment_type']} represented {float(pay['recorded_payment_value_share'])*100:.2f}% of Recorded Payment Value across {int(pay['payment_record_count']):,} payment records.","MET-014","MET-001","all payment rows/statuses",pay["payment_record_count"],"full observed window",f"recorded value={pay['recorded_payment_value']}; share={pay['recorded_payment_value_share']}","payment_summary.csv","Recorded Payment Value is not revenue, cash received, or net sales.","SUPPORTED_WITH_LIMITATION"),
    ]
    fields=["finding_id","analysis_id","query_id","business_question","finding_statement","primary_metric","supporting_metric","population","denominator","period","numerical_evidence","output_file","limitation","status"]
    rows=[dict(zip(fields,x),sql_file=next(q[5] for q in QUERIES if q[0]==x[2]),confidence_note="Validated descriptive result") for x in finding_data]
    out_fields=["finding_id","analysis_id","query_id","business_question","finding_statement","primary_metric","supporting_metric","population","denominator","period","numerical_evidence","sql_file","output_file","limitation","confidence_note","status"]
    write_csv(REPORT/"finding-evidence-register.csv",rows,out_fields)
    query_lookup={q[0]:q for q in QUERIES}
    trace=[]
    for r in rows:
      q=query_lookup[r["query_id"]]
      trace.append({"business_requirement_ids":q[2],"metric_ids":q[3],"model_ids":q[4],"analysis_id":r["analysis_id"],"query_id":r["query_id"],"result_file":r["output_file"],"finding_id":r["finding_id"],"finding_status":r["status"]})
    write_csv(REPORT/"traceability-matrix.csv",trace,list(trace[0]))
    sections={"Executive Performance":["FIND-001"],"Customers":["FIND-002"],"Categories":["FIND-003"],"Sellers":["FIND-004"],"Delivery":["FIND-005"],"Customer Experience":["FIND-006"],"Geography":["FIND-007"],"Payments/Freight":["FIND-008"]}
    lookup={r["finding_id"]:r for r in rows}; lines=["# Phase 5 SQL Findings","","These are validated descriptive SQL findings, not final recommendations.",""]
    for section,ids in sections.items():
      lines += [f"## {section}",""]
      for fid in ids:
        r=lookup[fid]; lines += [f"### {fid}","",f"**Finding:** {r['finding_statement']}","",f"**Evidence:** {r['numerical_evidence']}","",f"**Population:** {r['population']} (denominator: {r['denominator']}).","",f"**Period:** {r['period']}","",f"**Interpretation:** The data supports this descriptive pattern.","",f"**Limitation:** {r['limitation']}","",f"**Traceability:** {r['analysis_id']} / {r['query_id']} / {r['primary_metric']}; SQL: `{r['sql_file']}`.",""]
    (REPORT/"findings.md").write_text("\n".join(lines),encoding="utf-8")
    coverage=[]
    mapping={"BR-001":("AN-001","SQL-001;SQL-003","FIND-001"),"BR-002":("AN-001","SQL-001;SQL-003","FIND-001"),"BR-003":("AN-001","SQL-003","FIND-001"),"BR-004":("AN-002","SQL-009","FIND-007"),"BR-005":("AN-003","SQL-001;SQL-004","FIND-002"),"BR-006":("AN-003","SQL-004","FIND-002"),"BR-007":("AN-004","",""),"BR-008":("AN-005","",""),"BR-009":("AN-006","SQL-005","FIND-003"),"BR-010":("AN-006;AN-011","SQL-005;SQL-011","FIND-003"),"BR-011":("AN-006","SQL-005","FIND-003"),"BR-012":("AN-007","SQL-006","FIND-004"),"BR-013":("AN-007","SQL-006","FIND-004"),"BR-014":("AN-007","SQL-006","FIND-004"),"BR-015":("AN-008","SQL-007","FIND-005"),"BR-016":("AN-002;AN-006;AN-008","SQL-005;SQL-007;SQL-009;SQL-011","FIND-005;FIND-007"),"BR-017":("AN-008","SQL-007","FIND-005"),"BR-018":("AN-009","SQL-001;SQL-008","FIND-006"),"BR-019":("AN-010","SQL-008","FIND-006"),"BR-020":("AN-006;AN-007;AN-009","SQL-005;SQL-006;SQL-008;SQL-009","FIND-003;FIND-006;FIND-007"),"BR-021":("AN-011","SQL-001;SQL-010;SQL-011","FIND-008"),"BR-022":("AN-001–AN-011","SQL-001–SQL-011","FIND-001–FIND-008")}
    for br,(an,q,f) in mapping.items():
      deferred=br in {"BR-007","BR-008"}; coverage.append({"business_requirement_id":br,"analysis_id":an,"query_id":q,"status":"DEFERRED" if deferred else "ANSWERED","evidence_output":"" if deferred else "reports/sql-analysis/results/","finding_id":f,"limitation":"Cohort/RFM governed in Phase 6" if deferred else "See evidence register","future_phase_dependency":"Phase 6" if deferred else "None"})
    write_csv(REPORT/"business-question-coverage.csv",coverage,list(coverage[0]))

if __name__ == "__main__": main()
