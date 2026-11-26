#!/usr/bin/env python3
"""Compare Research I CSV directories without modifying their contents."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import sys


CSV_NAMES = (
    "aspect_summary.csv",
    "aspect_trials.csv",
    "density_summary.csv",
    "density_trials.csv",
    "null_controls.csv",
    "null_summary.csv",
    "null_trials.csv",
    "placement_metrics.csv",
    "start_z_m30.csv",
    "symmetry_metrics.csv",
    "synthetic_metrics.csv",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def classify(value):
    if value == "":
        return "missing", None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return "text", value
    if math.isnan(parsed):
        return "nan", None
    if math.isinf(parsed):
        return ("positive_infinity" if parsed > 0 else "negative_infinity"), None
    return "finite", parsed


def cells_equal(left, right):
    left_kind, left_value = classify(left)
    right_kind, right_value = classify(right)
    if left_kind != right_kind:
        return False
    if left_kind == "finite":
        return left_value == right_value
    if left_kind in {"nan", "positive_infinity", "negative_infinity"}:
        return True
    return left == right


def parse_set(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("set must be LABEL=PATH")
    label, path = value.split("=", 1)
    if not label or not path:
        raise argparse.ArgumentTypeError("set must be LABEL=PATH")
    return label, Path(path)


def compare_file(reference, candidate):
    ref_columns, ref_rows = read_csv(reference)
    columns, rows = read_csv(candidate)
    result = {
        "sha256": sha256(candidate),
        "byte_equal": reference.read_bytes() == candidate.read_bytes(),
        "shape": [len(rows), len(columns)],
        "shape_equal": (len(ref_rows), len(ref_columns)) == (len(rows), len(columns)),
        "headers_equal": ref_columns == columns,
        "rows_equal": False,
        "row_multiset_equal": False,
        "row_order_equal": None,
        "differing_columns": [],
        "rank_changed_columns": [],
        "max_absolute_difference": 0.0,
        "max_relative_difference": 0.0,
        "numeric_statistics_complete": True,
        "finite_numeric_pairs": 0,
        "missing_values": {"reference": 0, "candidate": 0},
        "non_finite_values": {
            "reference": {"nan": 0, "positive_infinity": 0, "negative_infinity": 0},
            "candidate": {"nan": 0, "positive_infinity": 0, "negative_infinity": 0},
        },
    }
    if not result["shape_equal"] or not result["headers_equal"]:
        return result

    ref_row_values = [tuple(row[column] for column in ref_columns) for row in ref_rows]
    row_values = [tuple(row[column] for column in columns) for row in rows]
    result["rows_equal"] = ref_row_values == row_values
    result["row_multiset_equal"] = Counter(ref_row_values) == Counter(row_values)
    if result["row_multiset_equal"]:
        result["row_order_equal"] = result["rows_equal"]

    for column in ref_columns:
        ref_cells = [classify(row[column]) for row in ref_rows]
        cells = [classify(row[column]) for row in rows]
        if any(not cells_equal(left, right) for left, right in zip(
            (row[column] for row in ref_rows), (row[column] for row in rows)
        )):
            result["differing_columns"].append(column)

        for side, parsed_cells in (("reference", ref_cells), ("candidate", cells)):
            for kind, _ in parsed_cells:
                if kind == "missing":
                    result["missing_values"][side] += 1
                elif kind in result["non_finite_values"][side]:
                    result["non_finite_values"][side][kind] += 1

        finite_pairs = [
            (left_value, right_value)
            for (left_kind, left_value), (right_kind, right_value) in zip(ref_cells, cells)
            if left_kind == right_kind == "finite"
        ]
        result["finite_numeric_pairs"] += len(finite_pairs)
        absolute = [abs(left - right) for left, right in finite_pairs]
        relative = [
            abs(left - right) / abs(left)
            for left, right in finite_pairs
            if left != 0
        ]
        result["max_absolute_difference"] = max(
            result["max_absolute_difference"], max(absolute, default=0.0)
        )
        result["max_relative_difference"] = max(
            result["max_relative_difference"], max(relative, default=0.0)
        )
        if all(kind == "finite" for kind, _ in ref_cells + cells):
            ref_values = [value for _, value in ref_cells]
            values = [value for _, value in cells]
            ref_order = sorted(range(len(ref_values)), key=lambda index: (ref_values[index], index))
            order = sorted(range(len(values)), key=lambda index: (values[index], index))
            if ref_order != order:
                result["rank_changed_columns"].append(column)

    non_finite_count = sum(
        count
        for side in result["non_finite_values"].values()
        for count in side.values()
    )
    if non_finite_count:
        result["numeric_statistics_complete"] = False
        result["max_absolute_difference"] = None
        result["max_relative_difference"] = None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", required=True, type=Path)
    parser.add_argument("--set", action="append", type=parse_set, default=[])
    parser.add_argument("--expect-byte-equal", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.set:
        parser.error("at least one --set LABEL=PATH is required")

    missing = []
    for name in CSV_NAMES:
        if not (args.published / name).is_file():
            missing.append(str(args.published / name))
        for label, directory in args.set:
            if not (directory / name).is_file():
                missing.append(f"{label}:{directory / name}")
    if missing:
        print(json.dumps({"error": "missing files", "files": missing}, indent=2))
        return 2

    report = {
        "published": str(args.published),
        "published_hashes": {
            name: sha256(args.published / name) for name in CSV_NAMES
        },
        "sets": {},
    }
    failed = False
    expected = set(args.expect_byte_equal)
    labels = {label for label, _ in args.set}
    unknown = sorted(expected - labels)
    if unknown:
        print(json.dumps({"error": "unknown expected sets", "sets": unknown}, indent=2))
        return 2

    for label, directory in args.set:
        comparisons = {}
        for name in CSV_NAMES:
            comparisons[name] = compare_file(args.published / name, directory / name)
        report["sets"][label] = {"path": str(directory), "files": comparisons}
        if label in expected and not all(item["byte_equal"] for item in comparisons.values()):
            failed = True

    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
