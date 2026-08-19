# Phase 6 Python Findings

Descriptive evidence only; no final recommendations.

## Distribution Diagnostics

### PYFIND-001

**Finding:** Order Product GMV was right-skewed: mean BRL 137.42, median BRL 86.90, P99 BRL 995.02.

**Evidence:** skew=9.771672967261784

**Population:** item-bearing commercial orders (denominator: 98199).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Extreme values retained

**Traceability:** AN-001 / MODEL-010; figure none; SQL comparison FIND-001.

## Customer Behavior

### PYFIND-002

**Finding:** Customers with one eligible order represented 96.96% of observed commercial customers; maximum frequency was 16.

**Evidence:** [{"frequency_group":"1","observed_customers":92099,"eligible_orders":92099,"observed_product_gmv":12743932.3100000005,"customer_share":0.9696060472,"product_gmv_share":0.9443866797},{"frequency_group":"2","observed_customers":2651,"eligible_orders":5302,"observed_product_gmv":650963.95,"customer_share":0.0279093761,"product_gmv_share":0.0482395597},{"frequency_group":"3","observed_customers":188,"eligible_orders":564,"observed_product_gmv":68111.18,"customer_share":0.001979239,"product_gmv_share":0.005047366},{"frequency_group":"4","observed_customers":29,"eligible_orders":116,"observed_product_gmv":19165.61,"customer_share":0.0003053082,"product_gmv_share":0.0014202639},{"frequency_group":"5+","observed_customers":19,"eligible_orders":121,"observed_product_gmv":12227.69,"customer_share":0.0002000295,"product_gmv_share":0.0009061306}]

**Population:** observed commercial customers (denominator: 94986).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Not lifetime behavior

**Traceability:** AN-003 / MODEL-001;MODEL-012; figure FIG-001; SQL comparison FIND-002.

### PYFIND-003

**Finding:** Median observed customer Product GMV was BRL 89.89; the top 10% accounted for 41.13%.

**Evidence:** top1=0.114407552417; top10=0.411336864596

**Population:** observed commercial customers (denominator: 94983).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Not lifetime value

**Traceability:** AN-003 / MODEL-012; figure none; SQL comparison FIND-002.

## Cohort Analysis

### PYFIND-004

**Finding:** Across eligible complete-period cohorts with observable follow-up, mean observed return rates were 0.49% at month 1, 0.34% at month 2, and 0.26% at month 3.

**Evidence:** m1=0.004877792350508916;m2=0.003369672893086608;m3=0.002610510426217017

**Population:** complete-period observed first-purchase cohorts (denominator: varies by horizon).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Unweighted cohort mean; right censoring and prior history unknown

**Traceability:** AN-004 / MODEL-001; figure FIG-002; SQL comparison none.

## RFM Feasibility

### PYFIND-005

**Finding:** Classic RFM was NOT_RECOMMENDED: Frequency equaled one for 96.96% of customers and could not form five natural quantile bins without tie-breaking.

**Evidence:** [{"component":"Recency","count":94986,"unique_values":94727,"minimum":0.0,"p20":97.4414814815,"p40":181.8409606481,"median":223.7857175926,"p60":272.8502199074,"p80":387.9149074074,"maximum":728.4941898148,"skewness":0.4474421312,"unique_quantile_boundaries":6,"qcut_bins_without_tie_breaking":5,"assessment":"USEFUL_VARIATION","cutoff_timestamp":1535965617,"final_feasibility_status":"NOT_RECOMMENDED","frequency_one_share":0.9696060472},{"component":"Frequency","count":94986,"unique_values":9,"minimum":1.0,"p20":1.0,"p40":1.0,"median":1.0,"p60":1.0,"p80":1.0,"maximum":16.0,"skewness":11.5096543981,"unique_quantile_boundaries":2,"qcut_bins_without_tie_breaking":1,"assessment":"INSUFFICIENT_VARIATION","cutoff_timestamp":1535965617,"final_feasibility_status":"NOT_RECOMMENDED","frequency_one_share":0.9696060472},{"component":"Monetary","count":94983,"unique_values":8242,"minimum":0.85,"p20":39.9,"p40":69.9,"median":89.89,"p60":109.9,"p80":179.9,"maximum":13440.0,"skewness":9.6374944751,"unique_quantile_boundaries":6,"qcut_bins_without_tie_breaking":5,"assessment":"USEFUL_VARIATION","cutoff_timestamp":1535965617,"final_feasibility_status":"NOT_RECOMMENDED","frequency_one_share":0.9696060472}]

**Population:** observed commercial customers (denominator: 94986).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Bounded history and partial final month

**Traceability:** AN-005 / MODEL-001;MODEL-012; figure none; SQL comparison none.

## Delivery Distribution

### PYFIND-006

**Finding:** The governed mean was 12.56 days versus a diagnostic median of 10.22; P95 was 29.27 days.

**Evidence:** p99=46.05026180555554;max=209.6286111111111

**Population:** endpoint-qualified delivered orders (denominator: 96470).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Mean KPI unchanged; long observations retained

**Traceability:** AN-008 / MODEL-001; figure FIG-003; SQL comparison FIND-005.

## Customer Experience

### PYFIND-007

**Finding:** Late reviewed orders averaged 2.57 versus 4.29 for on-time reviewed orders; score distributions differ descriptively.

**Evidence:** late=2.566505678109907;on_time=4.294292012144172;difference=-1.7277863340342652

**Population:** endpoint-qualified reviewed orders (denominator: 95824).

**Interpretation:** This supports a descriptive, observation-window-bounded conclusion.

**Limitation:** Observed association; not causal

**Traceability:** AN-010 / MODEL-005;MODEL-012; figure FIG-004; SQL comparison FIND-006.