"""Hard Phase 2 integrity gate against the Phase 1 SHA-256 manifest."""

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "reports" / "source-validation" / "file_manifest.csv"


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate():
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        expected = {row["source_file"]: row["sha256"] for row in csv.DictReader(handle)}
    actual = {path.name: path for path in RAW.glob("*.csv")}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(name for name in expected if name in actual and hash_file(actual[name]) != expected[name])
    return missing, extra, changed


if __name__ == "__main__":
    missing, extra, changed = validate()
    print(f"missing={missing}; extra={extra}; changed={changed}")
    sys.exit(1 if missing or extra or changed else 0)

