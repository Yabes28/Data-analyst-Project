# ADR-001 — Local Analytical SQL Engine

**Status:** Accepted recommendation; installation deferred until the approved implementation phase  
**Date:** 2026-08-19

## Context

The project needs analyst-level SQL, window functions, direct interchange with CSV/Parquet and pandas, local reproducibility, and low setup overhead. A server database is unnecessary for this approximately one-million-row public dataset.

## Decision

Recommend **DuckDB**, using the current LTS line when Phase 4/5 begins. Do not install or create a database during Phase 1.

## Rationale

- DuckDB directly queries CSV and Parquet and integrates with pandas, which reduces ingestion ceremony for a portfolio repository.
- It supports the required window functions such as `ROW_NUMBER`, `LAG`, ranks, and windowed aggregates.
- It runs embedded through Python or a single local database file, improving portability and recruiter reproducibility.
- Columnar analytical execution and Parquet support better fit scan/group/window workloads than SQLite's transaction-oriented default use case.

SQLite remains a strong portable embedded database and supports window functions, but its CSV workflow is CLI/import oriented and its storage/execution model is less aligned with the planned analytical marts. A server engine would add unjustified setup and administration.

## Consequences

- Add one small dependency (`duckdb`) when implementation begins and pin an LTS version.
- Keep SQL reasonably standard and document DuckDB-specific syntax.
- Treat generated `.duckdb` and Parquet files as reproducible artifacts excluded from Git unless publication policy later changes.
- Validate types explicitly rather than relying solely on CSV auto-detection.

Official references:

- https://duckdb.org/docs/stable/clients/python/overview
- https://duckdb.org/docs/lts/sql/functions/window_functions
- https://duckdb.org/docs/stable/data/parquet/overview
- https://sqlite.org/windowfunctions.html

