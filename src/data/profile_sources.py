"""Create deterministic Phase 1 file, column, date, and numeric profiles."""

import hashlib
from datetime import datetime, timezone

import pandas as pd

from source_config import DATE_COLUMNS, FILES, NUMERIC_COLUMNS, RAW_DIR, REPORT_DIR


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_raw(table):
    return pd.read_csv(RAW_DIR / FILES[table], dtype="string", keep_default_na=True)


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, inventory, columns, dates, numerics = [], [], [], [], []
    generated_at = datetime.now(timezone.utc).isoformat()

    missing = [name for name in FILES.values() if not (RAW_DIR / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing expected raw files: {missing}")

    for table, filename in FILES.items():
        path = RAW_DIR / filename
        frame = load_raw(table)
        manifest.append({
            "source_file": filename,
            "logical_table": table,
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "readable": True,
            "encoding_used": "utf-8",
            "delimiter": ",",
            "generated_at_utc": generated_at,
        })
        inventory.append({
            "logical_table": table,
            "source_file": filename,
            "row_count": len(frame),
            "column_count": len(frame.columns),
            "duplicate_full_rows": int(frame.duplicated().sum()),
            "columns": " | ".join(frame.columns),
        })

        for column in frame.columns:
            series = frame[column]
            non_null = int(series.notna().sum())
            inferred = "datetime" if column in DATE_COLUMNS.get(table, []) else (
                "numeric" if column in NUMERIC_COLUMNS.get(table, []) else "string"
            )
            columns.append({
                "table": table,
                "column": column,
                "observed_type": "string (raw read)",
                "semantic_inferred_type": inferred,
                "row_count": len(frame),
                "null_count": int(series.isna().sum()),
                "null_percentage": round(float(series.isna().mean() * 100), 6),
                "distinct_count_non_null": int(series.nunique(dropna=True)),
                "sample_values": " | ".join(series.dropna().drop_duplicates().head(3).astype(str)),
            })

        for column in DATE_COLUMNS.get(table, []):
            raw = frame[column]
            parsed = pd.to_datetime(raw, errors="coerce")
            dates.append({
                "table": table,
                "column": column,
                "non_null_raw": int(raw.notna().sum()),
                "parse_failures": int((raw.notna() & parsed.isna()).sum()),
                "min_datetime": parsed.min().isoformat() if parsed.notna().any() else None,
                "max_datetime": parsed.max().isoformat() if parsed.notna().any() else None,
            })

        for column in NUMERIC_COLUMNS.get(table, []):
            raw = frame[column]
            parsed = pd.to_numeric(raw, errors="coerce")
            numerics.append({
                "table": table,
                "column": column,
                "non_null_raw": int(raw.notna().sum()),
                "parse_failures": int((raw.notna() & parsed.isna()).sum()),
                "null_count": int(raw.isna().sum()),
                "zero_count": int((parsed == 0).sum()),
                "negative_count": int((parsed < 0).sum()),
                "minimum": float(parsed.min()) if parsed.notna().any() else None,
                "maximum": float(parsed.max()) if parsed.notna().any() else None,
                "mean": float(parsed.mean()) if parsed.notna().any() else None,
                "median": float(parsed.median()) if parsed.notna().any() else None,
                "p99": float(parsed.quantile(0.99)) if parsed.notna().any() else None,
            })

    pd.DataFrame(manifest).to_csv(REPORT_DIR / "file_manifest.csv", index=False)
    pd.DataFrame(inventory).to_csv(REPORT_DIR / "source_inventory.csv", index=False)
    pd.DataFrame(columns).to_csv(REPORT_DIR / "column_profile.csv", index=False)
    pd.DataFrame(dates).to_csv(REPORT_DIR / "date_profile.csv", index=False)
    pd.DataFrame(numerics).to_csv(REPORT_DIR / "numeric_profile.csv", index=False)
    print(f"Profiled {len(FILES)} files into {REPORT_DIR}")


if __name__ == "__main__":
    main()

