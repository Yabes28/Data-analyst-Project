# Repository Instructions

This repository uses specification-driven data analysis. Before changing code, SQL, models, dashboards, documentation, or findings, read the relevant files in `specs/` and the current phase in `tasks/roadmap.md`.

## Non-negotiable rules

1. Treat `specs/` as the single source of truth.
2. Preserve files in `data/raw/` unchanged; transformations must be deterministic and reproducible.
3. Never fabricate data, findings, metrics, source columns, or validation results.
4. Never substitute synthetic data when the Olist source files are unavailable.
5. Do not make causal claims from observational associations without causal evidence.
6. State and respect the grain of every source and analytical table before joining.
7. Prevent many-to-many multiplication and monetary double counting, especially between order items, payments, and reviews.
8. Use metric definitions from `specs/04-metric-contract.md` consistently.
9. Document assumptions, exclusions, limitations, and material decisions.
10. Run proportionate validation after every transformation and reconcile major outputs to their sources.
11. Change only the requested scope and current approved roadmap phase.
12. If implementation conflicts with a specification, stop, report the drift and impact, propose a spec change, and wait for approval.
13. Keep code, documentation, specifications, tests, and dashboard definitions synchronized.
14. Reference requirement IDs in major analytical outputs and commits where practical.

## Working conventions

- Raw data and credentials must never be committed.
- Prefer readable SQL and small, testable Python modules over notebook-only logic.
- Notebooks are for profiling, exploration, and presentation; reusable transformations belong in `src/` or `sql/`.
- Do not describe revenue-like measures as profit. Product GMV excludes freight unless the metric contract is explicitly amended.
- Classify anomalies before excluding them: valid business condition, source limitation, data-quality defect, or analytical exclusion.

