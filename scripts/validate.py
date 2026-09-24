#!/usr/bin/env python3
"""Validate every dataset in this repository.

Run from the repository root:  python3 scripts/validate.py

Checks, in order:
  1. required files exist
  2. every CSV parses, has a header, a consistent column count and no empty cells
  3. key columns are unique, and rows are not duplicated
  4. percentage ranges run low to high and are numeric
  5. the glossary is alphabetised
  6. units of measure come from a known vocabulary
  7. every dataset is listed in README.md and SOURCES.md
  8. fetched samples carry their provenance columns

Exits non-zero on the first run that finds errors, so it can gate CI.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SAMPLES_DIR = ROOT / "samples"

REQUIRED_FILES = [
    "README.md",
    "SOURCES.md",
    "LICENSE",
    "samples/README.md",
    "scripts/validate.py",
    "scripts/fetch_bls_ppi.py",
    ".github/workflows/validate.yml",
]

# dataset path -> list of columns that must together be unique
KEY_COLUMNS: dict[str, list[str]] = {
    "data/classification/csi-divisions.csv": ["division"],
    "data/cost-codes/starter-cost-code-taxonomy.csv": ["cost_code"],
    "data/glossary/glossary.csv": ["term"],
    "data/measures/earthwork-volume-factors.csv": ["material"],
    "data/measures/unit-conversions.csv": ["category", "from_unit", "to_unit"],
    "data/measures/waste-factors.csv": ["material"],
    "data/metrics/metric-formulas.csv": ["metric"],
    "data/schedule/typical-trade-sequence.csv": ["step"],
    "data/scope/pay-units.csv": ["scope_item"],
    "samples/bls-ppi-construction-materials.csv": ["series_id", "year", "period"],
}

PERCENT_RANGE_FILES = [
    "data/measures/waste-factors.csv",
    "data/measures/earthwork-volume-factors.csv",
]

UNIT_VOCABULARY = {
    "ACRE", "CY", "EA", "HR", "LB", "LF", "LS", "MO", "SF", "SQ", "SY", "TON",
}

SAMPLE_PROVENANCE_COLUMNS = {"source_url", "licence", "fetched_on"}

errors: list[str] = []
stats: list[tuple[str, int]] = []


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def dataset_paths() -> list[Path]:
    return sorted(p for p in list(DATA_DIR.rglob("*.csv")) + list(SAMPLES_DIR.rglob("*.csv")))


def check_required_files() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")


def check_csv_shape() -> None:
    for path in dataset_paths():
        rel = path.relative_to(ROOT).as_posix()
        rows = read_csv(path)
        if not rows:
            errors.append(f"{rel}: no data rows")
            continue
        stats.append((rel, len(rows)))
        width = len(rows[0])
        for index, row in enumerate(rows, start=2):
            if len(row) != width:
                errors.append(f"{rel}: row {index} has {len(row)} columns, expected {width}")
            for column, value in row.items():
                if value is None or value.strip() == "":
                    errors.append(f"{rel}: row {index} has an empty '{column}' cell")
                    break


def check_lf_line_endings() -> None:
    for path in dataset_paths():
        rel = path.relative_to(ROOT).as_posix()
        if b"\r\n" in path.read_bytes():
            errors.append(f"{rel}: contains CRLF line endings; use LF")


def check_keys() -> None:
    for rel, columns in KEY_COLUMNS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"key rule refers to a missing dataset: {rel}")
            continue
        rows = read_csv(path)
        seen: set[tuple[str, ...]] = set()
        for row in rows:
            key = tuple(row.get(column, "") for column in columns)
            if key in seen:
                errors.append(f"{rel}: duplicate key {key!r} on columns {columns}")
            seen.add(key)


def check_percentage_ranges() -> None:
    for rel in PERCENT_RANGE_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        header = list(read_csv(path)[0].keys())
        low_columns = [c for c in header if c.endswith("low_percent")]
        high_columns = [c for c in header if c.endswith("high_percent")]
        for row in read_csv(path):
            for low_column in low_columns:
                high_column = low_column.replace("low_percent", "high_percent")
                if high_column not in row:
                    continue
                label = row.get("material", "row")
                try:
                    low = float(row[low_column])
                    high = float(row[high_column])
                except (TypeError, ValueError):
                    errors.append(f"{rel}: {label}: non-numeric range in {low_column}/{high_column}")
                    continue
                if low > high:
                    errors.append(f"{rel}: {label}: low ({low}) is greater than high ({high})")


def check_glossary_sorted() -> None:
    rel = "data/glossary/glossary.csv"
    path = ROOT / rel
    if not path.exists():
        return
    terms = [row["term"] for row in read_csv(path)]
    if terms != sorted(terms, key=lambda term: term.lower()):
        for index, (actual, expected) in enumerate(zip(terms, sorted(terms, key=lambda t: t.lower()))):
            if actual != expected:
                errors.append(f"{rel}: not alphabetised at row {index + 2}: {actual!r} should be {expected!r}")
                break


def check_units() -> None:
    rel = "data/cost-codes/starter-cost-code-taxonomy.csv"
    path = ROOT / rel
    if not path.exists():
        return
    unknown = {row["unit"] for row in read_csv(path)} - UNIT_VOCABULARY
    if unknown:
        errors.append(f"{rel}: units outside the vocabulary: {sorted(unknown)}")

    scope = ROOT / "data/scope/pay-units.csv"
    if scope.exists():
        unknown_scope = {row["pay_unit"] for row in read_csv(scope)} - UNIT_VOCABULARY
        if unknown_scope:
            errors.append(f"data/scope/pay-units.csv: units outside the vocabulary: {sorted(unknown_scope)}")


def check_readme_counts() -> None:
    """The README table states a row count per dataset; keep it honest."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pattern = re.compile(r"\|\s*\[`([^`]+)`\]\(([^)]+)\)\s*\|\s*(\d+)\s*\|")
    counted = dict(stats)
    for listed_path, link_target, stated in pattern.findall(readme):
        actual = counted.get(listed_path)
        if actual is None:
            continue
        if int(stated) != actual:
            errors.append(
                f"README.md: states {stated} rows for {listed_path} but the file has {actual}"
            )
        if link_target != listed_path:
            errors.append(f"README.md: link text {listed_path} points at {link_target}")


def check_documented() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
    for path in dataset_paths():
        rel = path.relative_to(ROOT).as_posix()
        if rel not in readme:
            errors.append(f"{rel}: not listed in README.md")
        if rel not in sources:
            errors.append(f"{rel}: not listed in SOURCES.md")


def check_sample_provenance() -> None:
    for path in sorted(SAMPLES_DIR.rglob("*.csv")):
        rel = path.relative_to(ROOT).as_posix()
        header = set(read_csv(path)[0].keys())
        missing = SAMPLE_PROVENANCE_COLUMNS - header
        if missing:
            errors.append(f"{rel}: sample is missing provenance columns {sorted(missing)}")


def main() -> int:
    check_required_files()
    check_csv_shape()
    check_lf_line_endings()
    check_keys()
    check_percentage_ranges()
    check_glossary_sorted()
    check_units()
    check_readme_counts()
    check_documented()
    check_sample_provenance()

    if errors:
        print(f"FAIL: {len(errors)} problem(s)\n")
        for error in errors:
            print(f"  - {error}")
        return 1

    total = sum(count for _, count in stats)
    print(f"OK: {len(stats)} datasets, {total} rows")
    for rel, count in stats:
        print(f"  {count:>5}  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
