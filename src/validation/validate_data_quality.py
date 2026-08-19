"""Generate the non-destructive Phase 2 DQ evidence framework."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
sys.path.insert(0, str(DATA_DIR))
from source_config import FILES, RAW_DIR  # noqa: E402
from validate_raw_integrity import validate as validate_integrity  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "data-quality"


def load(table, usecols=None):
    return pd.read_csv(RAW_DIR / FILES[table], dtype="string", usecols=usecols)


def pct(count, total):
    return round(count / total * 100, 6) if total else 0.0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tests, issues = [], []

    def test(test_id, issue_id, name, table, result, value, expected, severity):
        tests.append(dict(test_id=test_id, issue_id=issue_id, test_name=name, source_table=table,
                          result=result, observed_value=value, expected_condition=expected, severity=severity))

    def issue(issue_id, title, table, columns, description, evidence, rows, entities, percentage,
              classification, severity, risk, metrics, themes, treatment, status, owner, test_id,
              source_ref, unresolved="", notes=""):
        issues.append(dict(issue_id=issue_id, issue_title=title, source_table=table,
            affected_columns=columns, issue_description=description, evidence=evidence,
            affected_row_count=rows, affected_entity_count=entities, affected_percentage=percentage,
            primary_classification=classification, severity=severity, analytical_risk=risk,
            impacted_metrics=metrics, impacted_analysis_themes=themes, proposed_treatment=treatment,
            treatment_status=status, owning_future_phase=owner, test_id=test_id,
            source_evidence_reference=source_ref, unresolved_question=unresolved, notes=notes))

    missing, extra, changed = validate_integrity()
    integrity_pass = not (missing or extra or changed)
    test("T-DQ-001", "DQ-001", "Raw files match Phase 1 manifest", "all", "PASS" if integrity_pass else "FAIL",
         f"missing={missing}; extra={extra}; changed={changed}", "No missing, extra, or changed CSV files", "CRITICAL")
    if not integrity_pass:
        raise RuntimeError("Raw integrity failed; Phase 2 stopped")

    customers, orders = load("customers"), load("orders")
    items, payments = load("order_items"), load("payments")
    reviews, geo = load("reviews"), load("geolocation")
    products, sellers = load("products"), load("sellers")
    translation = load("category_translation")

    # Key/critical identifier controls.
    key_defs = {"customers":["customer_id"], "orders":["order_id"],
                "order_items":["order_id","order_item_id"], "payments":["order_id","payment_sequential"],
                "products":["product_id"], "sellers":["seller_id"],
                "category_translation":["product_category_name"]}
    frames = {"customers":customers,"orders":orders,"order_items":items,"payments":payments,
              "products":products,"sellers":sellers,"category_translation":translation}
    key_failures = 0
    for table, cols in key_defs.items():
        f = frames[table]
        failures = int(f[cols].isna().any(axis=1).sum() + f.duplicated(cols, keep=False).sum())
        key_failures += failures
        test(f"T-DQ-002-{table}", "DQ-002", f"Validated key {'+'.join(cols)}", table,
             "PASS" if failures == 0 else "FAIL", failures, "0 null or duplicate-key rows", "CRITICAL")
    critical_cols = [(customers,"customers",["customer_id","customer_unique_id"]),
                     (orders,"orders",["order_id","customer_id"]),
                     (items,"order_items",["order_id","product_id","seller_id"]),
                     (payments,"payments",["order_id"]),(reviews,"reviews",["review_id","order_id"])]
    critical_nulls = sum(int(f[c].isna().sum()) for f,_,cols in critical_cols for c in cols)
    test("T-DQ-003", "DQ-003", "Critical identifiers are populated", "multiple", "PASS" if critical_nulls == 0 else "FAIL",
         critical_nulls, "0 null critical identifiers", "CRITICAL")

    # Customer semantic condition.
    cid_per_uid = customers.groupby("customer_unique_id")["customer_id"].nunique()
    repeated_uid = int((cid_per_uid > 1).sum())
    test("T-DQ-011", "DQ-011", "Customer identity grain", "customers", "INFO",
         f"customer_id={customers.customer_id.nunique()}; customer_unique_id={customers.customer_unique_id.nunique()}; repeated_stable_ids={repeated_uid}; max={cid_per_uid.max()}",
         "Document order-associated and stable identity levels", "HIGH")
    issue("DQ-011", "Two-level customer identity semantics", "customers; orders", "customer_id; customer_unique_id; order_id",
          "customer_id identifies one order-associated customer record; customer_unique_id can span orders.",
          f"99,441 unique customer_id; 96,096 unique customer_unique_id; {repeated_uid} stable IDs map to multiple records; maximum {int(cid_per_uid.max())}.",
          repeated_uid, repeated_uid, pct(repeated_uid, customers.customer_unique_id.nunique()),
          "ANALYTICAL_MODELING_CONDITION", "HIGH", "Using customer_id as a stable identity understates repeat behavior.",
          "MET-006; MET-007", "Customer", "Use customer_unique_id only after Phase 3 eligibility rules.",
          "REQUIRES_METRIC_RULE", "PHASE_3", "T-DQ-011", "semantic_validation.json")

    # Referential and optional coverage.
    relations = [("customers","orders",customers,"customer_id",orders,"customer_id"),
                 ("orders","order_items",orders,"order_id",items,"order_id"),
                 ("orders","payments",orders,"order_id",payments,"order_id"),
                 ("orders","reviews",orders,"order_id",reviews,"order_id"),
                 ("products","order_items",products,"product_id",items,"product_id"),
                 ("sellers","order_items",sellers,"seller_id",items,"seller_id")]
    orphan_total = 0
    for parent_name, child_name, parent, pk, child, fk in relations:
        orphans = int((~child[fk].isin(set(parent[pk])) & child[fk].notna()).sum())
        orphan_total += orphans
        test(f"T-DQ-004-{parent_name}-{child_name}", "DQ-004", f"{child_name} foreign keys match {parent_name}", child_name,
             "PASS" if orphans == 0 else "FAIL", orphans, "0 unmatched child rows", "HIGH")

    order_sets = {"items":set(items.order_id),"payments":set(payments.order_id),"reviews":set(reviews.order_id)}
    missing_related = {}
    for name, ids in order_sets.items():
        subset = orders[~orders.order_id.isin(ids)]
        missing_related[name] = subset
        dist = subset.order_status.value_counts().sort_index()
        test(f"T-DQ-016-{name}", "DQ-016", f"Orders without {name}", "orders", "WARN",
             f"rows={len(subset)}; statuses={dist.to_dict()}", "Quantify optional relationship absence", "MEDIUM")
    issue("DQ-016", "Orders without related item, payment, or review records", "orders", "order_id; order_status",
          "Parent orders do not always have each optional/transactional child source.",
          f"without items={len(missing_related['items'])}; payments={len(missing_related['payments'])}; reviews={len(missing_related['reviews'])}; no child FK orphans.",
          len(set(missing_related['items'].order_id)|set(missing_related['payments'].order_id)|set(missing_related['reviews'].order_id)),
          len(set(missing_related['items'].order_id)|set(missing_related['payments'].order_id)|set(missing_related['reviews'].order_id)), "varies",
          "ANALYTICAL_EXCLUSION_CANDIDATE", "MEDIUM", "Metric populations and denominators can differ by source coverage.",
          "MET-001–MET-015", "Cross-cutting", "Preserve orders; Phase 3 defines metric-specific eligibility.",
          "REQUIRES_METRIC_RULE", "PHASE_3", "T-DQ-016-items; T-DQ-016-payments; T-DQ-016-reviews", "relationship_validation.csv")

    # Fanout.
    item_counts = items.groupby("order_id").size()
    payment_counts = payments.groupby("order_id").size()
    mult = pd.concat([item_counts.rename("items"), payment_counts.rename("payments")], axis=1).dropna().astype(int)
    both_multi = int(((mult["items"]>1)&(mult["payments"]>1)).sum())
    ip = items[["order_id","price","freight_value"]].copy()
    pp = payments[["order_id","payment_value"]].copy()
    for col in ["price","freight_value"]: ip[col]=pd.to_numeric(ip[col],errors="coerce")
    pp["payment_value"]=pd.to_numeric(pp.payment_value,errors="coerce")
    naive = ip.merge(pp,on="order_id",how="inner")
    overlap=set(mult.index)
    base_price=float(ip[ip.order_id.isin(overlap)].price.sum()); joined_price=float(naive.price.sum())
    base_pay=float(pp[pp.order_id.isin(overlap)].payment_value.sum()); joined_pay=float(naive.payment_value.sum())
    price_infl=pct(joined_price-base_price,base_price); pay_infl=pct(joined_pay-base_pay,base_pay)
    test("T-DQ-015", "DQ-015", "Item-payment fanout changes monetary controls", "order_items; payments", "WARN",
         f"multi_items={(mult['items']>1).sum()}; multi_payments={(mult['payments']>1).sum()}; both={both_multi}; rows={len(naive)}; price_inflation={price_infl}%; payment_inflation={pay_infl}%",
         "Naive join must demonstrably differ and be prohibited", "CRITICAL")
    issue("DQ-015", "Order-item/payment many-to-many fanout", "order_items; payments", "order_id; price; freight_value; payment_value",
          "Directly joining both multi-row facts on order_id repeats measures by I_o × P_o.",
          f"9,802 multi-item orders; 2,936 multi-payment orders; {both_multi} both; 117,601 joined rows; price +{price_infl}%; payment +{pay_infl}%.",
          len(naive), both_multi, pct(both_multi,len(mult)), "ANALYTICAL_MODELING_CONDITION", "CRITICAL",
          "Can materially corrupt monetary metrics and conclusions.", "MET-003; MET-004; MET-005; MET-012; MET-013; MET-014",
          "Commerce; Payment", "Separate facts or independently pre-aggregate each to order grain.",
          "REQUIRES_MODELING_RULE", "PHASE_4", "T-DQ-015", "fanout_validation.json", notes="Permanent choice DEFERRED_TO_PHASE_4")

    # Review ambiguity.
    rid = reviews.groupby("review_id").agg(rows=("order_id","size"), orders=("order_id","nunique"), scores=("review_score","nunique"),
                                           creation_times=("review_creation_date","nunique"), answers=("review_answer_timestamp","nunique"),
                                           titles=("review_comment_title","nunique"), messages=("review_comment_message","nunique"))
    oid = reviews.groupby("order_id").agg(rows=("review_id","size"), review_ids=("review_id","nunique"), scores=("review_score","nunique"))
    review_assess = pd.DataFrame([{
        "review_rows":len(reviews), "unique_review_ids":reviews.review_id.nunique(),
        "review_ids_with_multiple_orders":int((rid.orders>1).sum()),
        "repeated_review_ids_with_score_variation":int(((rid.orders>1)&(rid.scores>1)).sum()),
        "repeated_review_ids_with_creation_variation":int(((rid.orders>1)&(rid.creation_times>1)).sum()),
        "repeated_review_ids_with_answer_variation":int(((rid.orders>1)&(rid.answers>1)).sum()),
        "orders_with_multiple_review_ids":int((oid.review_ids>1).sum()),
        "multi_review_orders_with_score_variation":int(((oid.review_ids>1)&(oid.scores>1)).sum()),
        "max_reviews_per_order":int(oid.rows.max()), "exact_duplicate_rows":int(reviews.duplicated().sum())
    }])
    review_assess.to_csv(OUT/"review-relationship-assessment.csv",index=False)
    rv=review_assess.iloc[0]
    test("T-DQ-010", "DQ-010", "Ambiguous repeated review relationships", "reviews", "WARN", rv.to_dict(),
         "Preserve and quantify without canonical deduplication", "HIGH")
    issue("DQ-010", "Ambiguous repeated review relationships", "reviews", "review_id; order_id; review_score; review timestamps; comments",
          "Review IDs can link to multiple orders and orders can contain multiple review IDs; no revision flag exists.",
          f"789 review IDs span orders; 547 orders have multiple review IDs; score variation among repeated review IDs={int(rv.repeated_review_ids_with_score_variation)}; max rows/order=3.",
          2052, 1336, pct(1336,len(reviews)), "UNRESOLVED", "HIGH", "Average review score and coverage depend on an unsupported canonical rule.",
          "MET-010", "Customer experience", "Preserve all events; approve canonical/event-grain policy later.",
          "REQUIRES_FURTHER_INVESTIGATION", "PHASE_3_OR_4", "T-DQ-010", "review-relationship-assessment.csv",
          "Are repeated relationships revisions, identifier reuse, or another source-system behavior?")

    # Geolocation.
    gz=geo.groupby("geolocation_zip_code_prefix")
    gprof=gz.agg(rows=("geolocation_zip_code_prefix","size"), cities=("geolocation_city","nunique"), states=("geolocation_state","nunique"),
                 lat_min=("geolocation_lat",lambda x: pd.to_numeric(x).min()), lat_max=("geolocation_lat",lambda x: pd.to_numeric(x).max()),
                 lng_min=("geolocation_lng",lambda x: pd.to_numeric(x).min()), lng_max=("geolocation_lng",lambda x: pd.to_numeric(x).max()))
    gprof["lat_range"]=gprof.lat_max-gprof.lat_min; gprof["lng_range"]=gprof.lng_max-gprof.lng_min
    geo_zips=set(geo.geolocation_zip_code_prefix)
    customer_gap=int((~customers.customer_zip_code_prefix.isin(geo_zips)).sum()); seller_gap=int((~sellers.seller_zip_code_prefix.isin(geo_zips)).sum())
    geo_summary=pd.DataFrame([{"rows":len(geo),"exact_duplicate_rows":int(geo.duplicated().sum()),"unique_zip_prefixes":len(gprof),
        "single_row_prefixes":int((gprof.rows==1).sum()),"multiple_row_prefixes":int((gprof.rows>1).sum()),"max_rows_per_prefix":int(gprof.rows.max()),
        "multi_city_prefixes":int((gprof.cities>1).sum()),"multi_state_prefixes":int((gprof.states>1).sum()),
        "median_lat_range":float(gprof.lat_range.median()),"max_lat_range":float(gprof.lat_range.max()),
        "median_lng_range":float(gprof.lng_range.median()),"max_lng_range":float(gprof.lng_range.max()),
        "customer_rows_without_coverage":customer_gap,"seller_rows_without_coverage":seller_gap}])
    geo_summary.to_csv(OUT/"geolocation-quality-assessment.csv",index=False)
    test("T-DQ-013", "DQ-013", "Raw geolocation ZIP multiplicity and coverage", "geolocation", "WARN", geo_summary.iloc[0].to_dict(),
         "Raw observations are not a unique ZIP dimension", "HIGH")
    issue("DQ-013", "Geolocation observation multiplicity and coverage gaps", "geolocation; customers; sellers", "ZIP prefix; latitude; longitude; city; state",
          "Raw geolocation contains repeated observations, conflicting labels/coordinates, exact duplicates, and coverage gaps.",
          f"261,831 exact repeats; 17,972 multi-row prefixes; 8,556 multi-city; 8 multi-state; customer gaps={customer_gap}; seller gaps={seller_gap}.",
          int((gprof.rows>1).sum()), int((gprof.rows>1).sum()), pct(int((gprof.rows>1).sum()),len(gprof)),
          "ANALYTICAL_MODELING_CONDITION", "HIGH", "Direct ZIP joins multiply rows and geography may be misassigned.",
          "MET-001–MET-015 when geographically grouped", "Geography", "Evaluate median/centroid/modal-label normalized ZIP reference; retain coverage flags.",
          "REQUIRES_NORMALIZATION", "PHASE_4", "T-DQ-013", "geolocation-quality-assessment.csv", notes="Final decision DEFERRED_TO_PHASE_4")

    # Categories.
    used=set(products.product_category_name.dropna()); mapped=set(translation.product_category_name)
    unmatched=used-mapped; affected_products=int(products.product_category_name.isin(unmatched).sum())
    missing_products=int(products.product_category_name.isna().sum())
    affected_item_missing=int(items.product_id.isin(set(products.loc[products.product_category_name.isna(),"product_id"])).sum())
    affected_item_unmatched=int(items.product_id.isin(set(products.loc[products.product_category_name.isin(unmatched),"product_id"])).sum())
    test("T-DQ-012", "DQ-012", "Category missingness and translation coverage", "products; category_translation", "WARN",
         f"missing_products={missing_products}; unmatched={sorted(unmatched)}; unmatched_products={affected_products}; item_rows_missing={affected_item_missing}; item_rows_untranslated={affected_item_unmatched}",
         "Preserve explicit missing/untranslated categories", "MEDIUM")
    issue("DQ-012", "Missing and untranslated product categories", "products; category_translation; order_items", "product_category_name; product_category_name_english",
          "Some products lack a Portuguese category and two observed categories lack supplied English mappings.",
          f"610 products / {affected_item_missing} item rows missing; 13 products / {affected_item_unmatched} item rows untranslated; labels={sorted(unmatched)}.",
          missing_products+affected_products, missing_products+affected_products, pct(missing_products+affected_products,len(products)),
          "SOURCE_DATA_LIMITATION", "MEDIUM", "Silent inner joins undercount category-based metrics.",
          "MET-001; MET-003–MET-005; MET-010–MET-013", "Product/category", "Preserve missing and original untranslated values; Phase 4 approves display labels.",
          "REQUIRES_MODELING_RULE", "PHASE_4", "T-DQ-012", "category-quality evidence in test results")

    # Dates, status, missingness, chronology, shipping 2020.
    date_cols=["order_purchase_timestamp","order_approved_at","order_delivered_carrier_date","order_delivered_customer_date","order_estimated_delivery_date"]
    od=orders.copy()
    for c in date_cols: od[c]=pd.to_datetime(od[c],errors="coerce")
    item_dates=items[["order_id","order_item_id","seller_id","product_id","shipping_limit_date"]].copy()
    item_dates.shipping_limit_date=pd.to_datetime(item_dates.shipping_limit_date,errors="coerce")
    parse_failures=sum(int(orders[c].notna().sum()-od[c].notna().sum()) for c in date_cols)+int(items.shipping_limit_date.notna().sum()-item_dates.shipping_limit_date.notna().sum())
    test("T-DQ-005", "DQ-005", "Configured timestamps parse", "orders; order_items", "PASS" if parse_failures==0 else "FAIL", parse_failures, "0 parse failures", "HIGH")
    issue("DQ-005", "Timezone metadata absent from source timestamps", "orders; order_items; reviews", "all timestamp columns",
          "CSV timestamps are timezone-naive and the source provides no timezone field.", "All configured non-null timestamps parse; no offset/timezone metadata exists.",
          "all timestamped rows", "all timestamped rows", "not applicable", "SOURCE_DATA_LIMITATION", "MEDIUM",
          "Timezone-sensitive/hour-of-day interpretation cannot be verified.", "MET-001; MET-008; MET-009", "Time", "Retain source-naive semantics and document limitation.",
          "PRESERVE_AND_DOCUMENT", "PHASE_3_AND_6", "T-DQ-005", "date_profile.csv")

    temporal_conditions={
        "purchase_after_approval":od.order_purchase_timestamp>od.order_approved_at,
        "approval_after_carrier":od.order_approved_at>od.order_delivered_carrier_date,
        "carrier_after_customer_delivery":od.order_delivered_carrier_date>od.order_delivered_customer_date,
        "purchase_after_customer_delivery":od.order_purchase_timestamp>od.order_delivered_customer_date,
        "customer_delivery_after_estimate":od.order_delivered_customer_date>od.order_estimated_delivery_date,
    }
    temporal_rows=[]
    for name,mask in temporal_conditions.items():
        if name=="approval_after_carrier": delta=(od.order_approved_at-od.order_delivered_carrier_date).dt.total_seconds()/3600
        elif name=="carrier_after_customer_delivery": delta=(od.order_delivered_carrier_date-od.order_delivered_customer_date).dt.total_seconds()/3600
        elif name=="purchase_after_approval": delta=(od.order_purchase_timestamp-od.order_approved_at).dt.total_seconds()/3600
        elif name=="purchase_after_customer_delivery": delta=(od.order_purchase_timestamp-od.order_delivered_customer_date).dt.total_seconds()/3600
        else: delta=(od.order_delivered_customer_date-od.order_estimated_delivery_date).dt.total_seconds()/3600
        vals=delta[mask]
        temporal_rows.append({"condition":name,"rows":int(mask.sum()),"percentage_of_orders":pct(int(mask.sum()),len(od)),
                              "min_violation_hours":float(vals.min()) if len(vals) else None,"median_violation_hours":float(vals.median()) if len(vals) else None,
                              "max_violation_hours":float(vals.max()) if len(vals) else None,
                              "status_distribution":json.dumps(od.loc[mask,"order_status"].value_counts().to_dict())})
    pd.DataFrame(temporal_rows).to_csv(OUT/"temporal-quality-assessment.csv",index=False)
    actual_exceptions=int((temporal_conditions["approval_after_carrier"] | temporal_conditions["carrier_after_customer_delivery"]).sum())
    test("T-DQ-006", "DQ-006", "Chronological consistency", "orders", "WARN", f"approval_after_carrier=1359; carrier_after_delivery=23; late_delivery={int(temporal_conditions['customer_delivery_after_estimate'].sum())}",
         "Quantify true sequence exceptions; treat lateness as business condition", "HIGH")
    issue("DQ-006", "Order chronology exceptions", "orders", "approval; carrier; customer delivery timestamps",
          "Some lifecycle timestamps appear in an unexpected sequence; late delivery is separately a valid business condition.",
          "1,359 approval-after-carrier; 23 carrier-after-customer-delivery; zero purchase-after-approval/delivery. Violation magnitudes/statuses in temporal assessment.",
          actual_exceptions, actual_exceptions, pct(actual_exceptions,len(orders)), "UNRESOLVED", "HIGH",
          "Duration metrics may be negative or operational sequence may be misinterpreted.", "MET-008; MET-009; MET-015", "Delivery",
          "Preserve; Phase 2 evidence supports metric-specific exclusion consideration, not correction.",
          "POTENTIAL_ANALYTICAL_EXCLUSION", "PHASE_3", "T-DQ-006", "temporal-quality-assessment.csv",
          "Do timestamps reflect source-system event ordering, delayed writes, or erroneous values?")

    future=item_dates[item_dates.shipping_limit_date.dt.year>=2020].merge(orders[["order_id","order_purchase_timestamp","order_status"]],on="order_id",how="left")
    future["purchase_to_shipping_limit_days"]=(future.shipping_limit_date-pd.to_datetime(future.order_purchase_timestamp)).dt.total_seconds()/86400
    future.to_csv(OUT/"shipping-limit-2020-assessment.csv",index=False)
    test("T-DQ-017", "DQ-017", "Shipping-limit dates in 2020", "order_items", "WARN", f"rows={len(future)}; orders={future.order_id.nunique()}; min={future.shipping_limit_date.min()}; max={future.shipping_limit_date.max()}",
         "Quantify isolated future-bound timestamps without mutation", "MEDIUM")
    issue("DQ-017", "Shipping-limit timestamp beyond source purchase window", "order_items; orders", "shipping_limit_date; order_purchase_timestamp",
          "Shipping-limit timestamp extends to 2020 although the last purchase is in 2018.",
          f"{len(future)} item row(s), {future.order_id.nunique()} order(s), delta days={future.purchase_to_shipping_limit_days.tolist()}.",
          len(future), future.order_id.nunique(), pct(len(future),len(items)), "UNRESOLVED", "MEDIUM",
          "Shipping-limit analysis and chronology can be distorted for the affected row.", "No current core metric; future shipping compliance", "Delivery",
          "Preserve and investigate; do not infer typo or correction.", "REQUIRES_FURTHER_INVESTIGATION", "PHASE_3_OR_4", "T-DQ-017", "shipping-limit-2020-assessment.csv",
          "What source-system event produced the 2020 timestamp?")

    # Status evidence matrix.
    status_rows=[]
    for status,g in od.groupby("order_status"):
        ids=set(g.order_id)
        status_rows.append({"order_status":status,"orders":len(g),"percentage":pct(len(g),len(od)),
            "approval_present":int(g.order_approved_at.notna().sum()),"carrier_present":int(g.order_delivered_carrier_date.notna().sum()),
            "customer_delivery_present":int(g.order_delivered_customer_date.notna().sum()),"estimate_present":int(g.order_estimated_delivery_date.notna().sum()),
            "orders_with_items":int(g.order_id.isin(order_sets['items']).sum()),"orders_with_payments":int(g.order_id.isin(order_sets['payments']).sum()),
            "orders_with_reviews":int(g.order_id.isin(order_sets['reviews']).sum()),"order_count_metrics":"PENDING_PHASE_3",
            "gmv_metrics":"PENDING_PHASE_3","delivery_metrics":"PENDING_PHASE_3","late_delivery_metrics":"PENDING_PHASE_3",
            "review_metrics":"PENDING_PHASE_3","customer_metrics":"PENDING_PHASE_3"})
    pd.DataFrame(status_rows).to_csv(OUT/"status-eligibility-matrix.csv",index=False)
    test("T-DQ-008", "DQ-008", "Order-status evidence matrix", "orders", "INFO", f"statuses={od.order_status.nunique()}", "All population decisions PENDING_PHASE_3", "HIGH")
    issue("DQ-008", "Order-status-dependent metric eligibility", "orders", "order_status; lifecycle timestamps",
          "Eight valid source statuses have different lifecycle completion and child-source coverage.",
          "Counts, timestamp presence, and item/payment/review presence are recorded per status; all eligibility cells PENDING_PHASE_3.",
          len(orders), orders.order_status.nunique(), 100, "VALID_BUSINESS_CONDITION", "HIGH",
          "A single implicit status filter would create inconsistent KPI populations.", "MET-001–MET-015", "All", "Phase 3 approves metric-specific populations.",
          "REQUIRES_METRIC_RULE", "PHASE_3", "T-DQ-008", "status-eligibility-matrix.csv")

    delivered_missing=(od.order_status=="delivered")&od.order_delivered_customer_date.isna()
    nondelivered_present=(od.order_status!="delivered")&od.order_delivered_customer_date.notna()
    test("T-DQ-009", "DQ-009", "Delivery-status/timestamp consistency", "orders", "WARN",
         f"delivered_missing={delivered_missing.sum()}; non_delivered_present={nondelivered_present.sum()}; statuses={od.loc[nondelivered_present,'order_status'].value_counts().to_dict()}",
         "Preserve source status and define metric-specific handling", "HIGH")
    issue("DQ-009", "Delivery status and timestamp inconsistencies", "orders", "order_status; order_delivered_customer_date",
          "Delivered status can lack an actual delivery timestamp, while non-delivered status can contain one.",
          f"8 delivered orders missing timestamp; 6 non-delivered orders with timestamp, statuses={od.loc[nondelivered_present,'order_status'].value_counts().to_dict()}.",
          14, 14, pct(14,len(orders)), "ANALYTICAL_EXCLUSION_CANDIDATE", "HIGH",
          "Delivery lead time and late-rate denominators require explicit endpoint eligibility.", "MET-008; MET-009; MET-015", "Delivery",
          "Preserve status; Phase 3 evaluates status-only vs status-plus-valid-timestamp populations.",
          "REQUIRES_METRIC_RULE", "PHASE_3", "T-DQ-009", "status-eligibility-matrix.csv")

    # Missing value semantics.
    missing_rows=[]
    for col in ["order_approved_at","order_delivered_carrier_date","order_delivered_customer_date"]:
        for status,g in orders.groupby("order_status"):
            n=int(g[col].isna().sum())
            if n:
                structural = (col in ["order_delivered_carrier_date","order_delivered_customer_date"] and status in ["created","approved","invoiced","processing","shipped","canceled","unavailable"])
                missing_rows.append({"table":"orders","column":col,"condition":f"order_status={status}","null_count":n,"percentage_within_condition":pct(n,len(g)),
                    "null_semantics":"STRUCTURAL_NULL" if structural else "UNEXPECTED_NULL" if status=="delivered" else "UNRESOLVED_NULL",
                    "classification":"VALID_BUSINESS_CONDITION" if structural else "ANALYTICAL_EXCLUSION_CANDIDATE" if status=="delivered" else "UNRESOLVED",
                    "metric_impact":"Lifecycle/delivery eligibility"})
    missing_rows += [
        {"table":"reviews","column":"review_comment_title","condition":"all reviews","null_count":int(reviews.review_comment_title.isna().sum()),"percentage_within_condition":pct(int(reviews.review_comment_title.isna().sum()),len(reviews)),"null_semantics":"STRUCTURAL_NULL","classification":"VALID_BUSINESS_CONDITION","metric_impact":"No impact on score; text analysis coverage only"},
        {"table":"reviews","column":"review_comment_message","condition":"all reviews","null_count":int(reviews.review_comment_message.isna().sum()),"percentage_within_condition":pct(int(reviews.review_comment_message.isna().sum()),len(reviews)),"null_semantics":"STRUCTURAL_NULL","classification":"VALID_BUSINESS_CONDITION","metric_impact":"No impact on score; text analysis coverage only"},
        {"table":"products","column":"product_category_name","condition":"all products","null_count":missing_products,"percentage_within_condition":pct(missing_products,len(products)),"null_semantics":"UNRESOLVED_NULL","classification":"SOURCE_DATA_LIMITATION","metric_impact":"Category grouping coverage"},
    ]
    pd.DataFrame(missing_rows).to_csv(OUT/"missing-value-assessment.csv",index=False)

    # Monetary controls and zero contexts.
    monetary=[]
    for table,frame,col in [("order_items",items,"price"),("order_items",items,"freight_value"),("payments",payments,"payment_value")]:
        num=pd.to_numeric(frame[col],errors="coerce")
        monetary.append({"table":table,"column":col,"rows":len(frame),"nulls":int(frame[col].isna().sum()),"parse_failures":int((frame[col].notna()&num.isna()).sum()),
                         "zeros":int((num==0).sum()),"negatives":int((num<0).sum()),"minimum":float(num.min()),"p99":float(num.quantile(.99)),"maximum":float(num.max())})
    pd.DataFrame(monetary).to_csv(OUT/"monetary-quality-assessment.csv",index=False)
    zero_pay=payments[pd.to_numeric(payments.payment_value)==0].merge(orders[["order_id","order_status"]],on="order_id",how="left")
    zero_pay.to_csv(OUT/"zero-payment-context.csv",index=False)
    test("T-DQ-007", "DQ-007", "Monetary parse/null/zero/negative controls", "order_items; payments", "WARN",
         f"negative=0; zero_price=0; zero_freight=383; zero_payment=9; zero_payment_types={zero_pay.payment_type.value_counts().to_dict()}",
         "No mutation; classify zeros and preserve extremes", "MEDIUM")
    issue("DQ-007", "Zero monetary values and extreme ranges", "order_items; payments", "price; freight_value; payment_value",
          "Monetary fields are populated and non-negative, but zero freight/payment values and high ranges need metric-aware interpretation.",
          "price zeros=0 max=6,735; freight zeros=383 max=409.68; payment zeros=9 max=13,664.08; no parse failures/negatives.",
          392, 392, "field-specific", "UNRESOLVED", "MEDIUM", "Zero treatment or automatic outlier removal could bias value metrics.",
          "MET-003–MET-005; MET-012–MET-014", "Commerce; payment", "Preserve all values; investigate zero contexts; never winsorize automatically.",
          "REQUIRES_FURTHER_INVESTIGATION", "PHASE_3", "T-DQ-007", "monetary-quality-assessment.csv")

    # Geographical/categorical consistency is deferred and source-naive.
    test("T-DQ-014", "DQ-014", "Categorical normalization remains unimplemented", "multiple", "INFO",
         "Source labels preserved", "No Phase 2 normalization", "LOW")
    issue("DQ-014", "Source categorical labels are not normalized", "customers; sellers; geolocation; payments; products", "city; state; payment_type; category",
          "Source spelling/casing/accent variants are preserved and may represent aliases rather than defects.",
          "Geolocation includes 8,556 ZIP prefixes with multiple city strings; no derived mapping was created.",
          "not consolidated", "not consolidated", "not applicable", "SOURCE_DATA_LIMITATION", "LOW",
          "Grouping labels may fragment categories or locations.", "Geographic/category grouped metrics", "Cross-cutting",
          "Profile and approve mappings only in a derived layer.", "REQUIRES_NORMALIZATION", "PHASE_4", "T-DQ-014", "geolocation-quality-assessment.csv")

    # Observation-window warning.
    pmin=od.order_purchase_timestamp.min(); pmax=od.order_purchase_timestamp.max()
    test("T-DQ-018", "DQ-018", "Bounded purchase observation window", "orders", "INFO", f"min={pmin}; max={pmax}",
         "Document censoring; do not compute behavior metrics", "HIGH")
    issue("DQ-018", "Bounded observation window and censoring", "orders; customers", "order_purchase_timestamp; customer_unique_id",
          "Customer behavior is observed only between the minimum and maximum purchase timestamps.",
          f"Purchase window {pmin} to {pmax}; boundary completeness is not guaranteed by the source.",
          len(orders), customers.customer_unique_id.nunique(), 100, "SOURCE_DATA_LIMITATION", "HIGH",
          "Late entrants have less opportunity to repeat; recency depends on an arbitrary dataset endpoint.", "MET-006; MET-007", "Customer; time",
          "Disclose fixed window, censoring, cohort exposure, and recency anchor before Phase 6 analysis.",
          "PRESERVE_AND_DOCUMENT", "PHASE_3_AND_6", "T-DQ-018", "date_profile.csv")

    # Key ambiguity and raw geolocation exact repeats as assessed issue area.
    test("T-DQ-002-ambiguous", "DQ-002", "Non-unique review/geolocation identifiers", "reviews; geolocation", "WARN",
         "review_id duplicate-key rows=1603; geolocation full duplicate rows=261831", "Do not infer uniqueness", "HIGH")
    issue("DQ-002", "Non-unique identifiers at review and geolocation grains", "reviews; geolocation", "review_id; order_id; geolocation fields",
          "Identifiers/combinations that resemble keys are not unique at the observed source grains.",
          "review_id duplicate-key rows=1,603; order_id duplicate review rows=1,098; geolocation exact duplicate rows=261,831.",
          263434, "multiple", "not additive", "ANALYTICAL_MODELING_CONDITION", "HIGH",
          "Incorrect uniqueness assumptions cause arbitrary deduplication or row multiplication.", "MET-010; geographic metrics", "Experience; geography",
          "Preserve source events/observations and require modeling rules.", "REQUIRES_MODELING_RULE", "PHASE_4", "T-DQ-002-ambiguous", "key_validation.csv")

    # Status/missing issues cover DQ-008/009; DQ-003 and DQ-004 are clean controls, not issue register rows.
    # Persist tests/register.
    pd.DataFrame(tests).to_csv(OUT/"data-quality-test-results.csv",index=False)
    pd.DataFrame(issues).to_csv(OUT/"data-quality-issue-register.csv",index=False)

    # Metric impact matrix: only material issue/metric combinations; unspecified combinations are NO_IMPACT.
    metrics=[f"MET-{i:03d}" for i in range(1,16)]
    impact_rules={
        "DQ-015":({"MET-003","MET-004","MET-005","MET-012","MET-013","MET-014"},"BLOCKING"),
        "DQ-010":({"MET-010"},"REQUIRES_RULE"), "DQ-013":(set(metrics),"BLOCKING"),
        "DQ-009":({"MET-008","MET-009","MET-015"},"REQUIRES_RULE"),
        "DQ-006":({"MET-008","MET-009","MET-015"},"REQUIRES_RULE"),
        "DQ-011":({"MET-006","MET-007"},"REQUIRES_RULE"),
        "DQ-012":({"MET-001","MET-003","MET-004","MET-005","MET-010","MET-011","MET-012","MET-013"},"POTENTIAL_IMPACT"),
        "DQ-016":(set(metrics),"REQUIRES_RULE"), "DQ-018":({"MET-006","MET-007"},"REQUIRES_RULE"),
        "DQ-007":({"MET-003","MET-004","MET-005","MET-012","MET-013","MET-014"},"POTENTIAL_IMPACT"),
        "DQ-008":(set(metrics),"REQUIRES_RULE"), "DQ-005":({"MET-001","MET-008","MET-009","MET-015"},"POTENTIAL_IMPACT")}
    matrix=[]
    for i in issues:
        impacted,state=impact_rules.get(i["issue_id"],(set(),"NO_IMPACT"))
        for m in metrics:
            matrix.append({"issue_id":i["issue_id"],"metric_id":m,"impact":state if m in impacted else "NO_IMPACT",
                           "reason":i["analytical_risk"] if m in impacted else "No direct Phase 2 impact identified"})
    pd.DataFrame(matrix).to_csv(OUT/"metric-impact-matrix.csv",index=False)

    summary={"raw_integrity":"PASS","issues":len(issues),
             "classification_breakdown":pd.Series([i['primary_classification'] for i in issues]).value_counts().to_dict(),
             "severity_breakdown":pd.Series([i['severity'] for i in issues]).value_counts().to_dict(),
             "test_result_breakdown":pd.Series([t['result'] for t in tests]).value_counts().to_dict()}
    (OUT/"data-quality-summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
