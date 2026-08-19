# Phase 6 Python Analysis

Run `python src/analysis/run_python_analysis.py` after the approved DuckDB model and Phase 5 SQL outputs exist.

The pipeline reconciles nine governed metrics, produces distribution diagnostics without removing extremes, builds a stable-customer frame, creates censoring-aware observed cohorts, evaluates rather than assumes RFM feasibility, and generates four curated figures. Raw CSVs and raw geolocation are not used.

## Methodological decisions

- Customer identity: `customer_unique_id`.
- Customer dates: first/last eligible purchases observed inside the source window—not lifetime history.
- Cohort anchor: Observed First-Purchase Cohort month.
- Cohort headline population: complete-period cohort months. Partial cohorts remain visible.
- Censoring: target partial, no-activity, or unavailable months are NULL with a reason—not zero.
- RFM cutoff: maximum eligible purchase timestamp, `2018-09-03 09:06:57`.
- RFM result: `NOT_RECOMMENDED`; Frequency=1 for 96.96% and five-bin quantiles collapse without artificial tie-breaking. No segmentation was created.
- Governed means remain unchanged; medians and percentiles are diagnostic statistics.
- Findings are descriptive and contain no final recommendations.
