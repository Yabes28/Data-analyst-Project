# Decision Log

| Date | ID | Decision | Rationale | Impact |
|---|---|---|---|---|
| 2026-08-19 | DEC-001 | Use `specs/` as the single source of truth and require explicit phase approval. | Prevent implementation from silently defining business logic. | Work is gated by roadmap phases. |
| 2026-08-19 | DEC-002 | Exclude profit and margin analysis from scope. | The expected source lacks validated cost-of-goods information. | Use GMV/value, volume, freight, delivery, and experience metrics instead. |
| 2026-08-19 | DEC-003 | Keep items, payments, and reviews at separate facts unless safely pre-aggregated. | Their potentially multi-row order relationships can multiply measures. | Phase 4 must prove join cardinality and reconciliation. |
| 2026-08-19 | DEC-004 | Defer dependency pinning and database choice until source validation. | Phase 0 has no source data and should not pre-empt the model/tool decision. | `requirements.txt` is provisional. |
| 2026-08-19 | DEC-005 | Record Phase 0 as explicitly approved and stop Phase 1 at the acquisition gate. | The nine original Olist CSV files are absent, Kaggle CLI is unavailable, and source evidence cannot be fabricated. | Phase 1 remains incomplete until the user places the original files in `data/raw/`. |
