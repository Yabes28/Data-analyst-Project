# Portfolio Case Study Specification

**Status:** Draft structure; content is gated by completed analysis.

## Intended narrative

`Business Context → Analytical Requirements → Data Understanding → Data Quality → Metric Definitions → Data Modeling → SQL/Python Analysis → Dashboard → Findings → Recommendations → Limitations → Validation`

## Required sections

1. Executive summary with only validated outcomes.
2. Stakeholders, decisions, scope, and explicit non-profitability boundary.
3. Source attribution, observation window, entities, grains, and relationship diagram.
4. Material data-quality issues, dispositions, exclusions, and coverage.
5. Selected metric definitions and safeguards against double counting.
6. Analytical model and reproducible workflow.
7. Selected SQL/Python techniques tied to business questions.
8. Dashboard preview and navigation.
9. Quantified findings with requirement/metric lineage.
10. Evidence-linked recommendations and testable next actions.
11. Limitations, observational wording, and unresolved questions.
12. Validation/reconciliation evidence and rerun instructions.

## Publication rules

- Do not publish findings, numbers, screenshots, or recommendations before execution and validation.
- Distinguish fact, analytical interpretation, assumption, and proposed action.
- Do not expose credentials or unnecessary row-level personal/location data.
- Use concise visuals with accessible captions and explain why each matters.
- Keep the landing README scannable; link detailed methodology rather than duplicating it.
- Cite the dataset and respect verified license/attribution terms.

## Traceability standard

Each major finding must cite an `AN-*` analysis and `MET-*` metric; each recommendation must cite the finding/value supporting it. Limitations must name the affected metric or conclusion.

