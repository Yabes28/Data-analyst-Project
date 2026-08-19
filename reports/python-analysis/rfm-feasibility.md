# RFM Feasibility Assessment

**Final status: NOT_RECOMMENDED**

Recency is days from the last observed eligible purchase to the deterministic maximum eligible purchase timestamp, `2018-09-03 09:06:57`. Frequency is eligible commercial order count by `customer_unique_id`. Monetary is Observed Customer Product GMV, not lifetime value.

Frequency equals one for 96.96% of customers. Five-bin `qcut` without artificial tie-breaking collapses Frequency bins, so classic balanced RFM scoring is not defensible. Recency and Monetary vary, but the bounded history, partial final month, and unknown purchases outside the source window can alter classification. No segmentation was created.

This conclusion does not show that customer differentiation is impossible; it shows that classic three-component quantile RFM is not recommended for this observation window.
