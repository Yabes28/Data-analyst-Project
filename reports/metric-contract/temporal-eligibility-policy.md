# Temporal Eligibility Policy

- Interpret timestamps exactly as source-provided timezone-naive values; perform no conversion.
- Primary KPI reporting date is `order_purchase_timestamp`; no fallback event date is allowed.
- MET-008 requires purchase and actual customer-delivery timestamps with delivery not earlier than purchase.
- MET-009/MET-015 additionally require estimated delivery; equality is on-time.
- Missing endpoints cause metric-specific ineligibility and coverage disclosure, never global row deletion or imputation.
- Approval-after-carrier and carrier-after-customer-delivery exceptions do not affect metrics whose formulas do not use those endpoints.
- Late delivery is a valid operational condition, not a timestamp defect.
- The four 2020 `shipping_limit_date` rows have `NO_IMPACT_ON_CURRENT_CORE_METRICS`; preserve them for future SLA policy.
- Boundary periods must be tested for completeness before Phase 5/6 trend interpretation.

