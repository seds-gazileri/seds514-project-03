from __future__ import annotations

import csv
import json
from pathlib import Path

from allpairspy import AllPairs
from importlib import metadata


FACTOR_NAMES = [
    "input_type",
    "headers",
    "tablefmt",
    "showindex",
    "missingval",
    "data_mix",
    "size",
]

FACTORS = [
    ["list_of_lists", "list_of_dicts", "dict_of_columns"],
    ["explicit_list", "firstrow", "keys"],
    ["plain", "github", "grid", "psql"],
    ["always", "never", "custom_iterable"],
    ["default", "question", "na"],
    ["all_strings", "ints_floats", "includes_none"],
    ["small", "medium", "wide_text"],
]


def is_valid(row: list[str | None]) -> bool:
    """Filter invalid combinations based on design_spec constraints."""
    values = dict(zip(FACTOR_NAMES, row))

    def defined(*keys: str) -> bool:
        return all(values.get(key) is not None for key in keys)

    # Constraint 1: list_of_dicts cannot use firstrow headers
    if defined("input_type", "headers"):
        if values["input_type"] == "list_of_dicts" and values["headers"] == "firstrow":
            return False

        # Constraint 2: keys headers require dict-like input
        if values["headers"] == "keys" and values["input_type"] not in (
            "list_of_dicts",
            "dict_of_columns",
        ):
            return False

    # Constraint 3: missingval only meaningful with None data
    if defined("missingval", "data_mix"):
        if values["missingval"] in ("question", "na") and values["data_mix"] != "includes_none":
            return False

    # Constraint 4: custom_iterable index requires medium or wide tables
    if defined("showindex", "size"):
        if values["showindex"] == "custom_iterable" and values["size"] == "small":
            return False

    # Constraint 5: firstrow requires medium or wide tables
    if defined("headers", "size"):
        if values["headers"] == "firstrow" and values["size"] == "small":
            return False

    return True


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "generated_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    pairs = list(AllPairs(FACTORS, filter_func=is_valid))
    rows = [dict(zip(FACTOR_NAMES, row)) for row in pairs]

    csv_path = output_dir / "pairwise_cases.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FACTOR_NAMES)
        writer.writeheader()
        writer.writerows(rows)

    json_path = output_dir / "pairwise_cases.json"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    metrics = {
        "tool": "allpairspy",
        "tool_version": metadata.version("allpairspy"),
        "generated_count": len(rows),
        "theoretical_combinations": 3 * 3 * 4 * 3 * 3 * 3 * 3,
    }
    metrics["reduction_ratio"] = round(
        metrics["generated_count"] / metrics["theoretical_combinations"],
        4,
    )

    metrics_path = output_dir / "pairwise_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Wrote {len(rows)} cases to {csv_path}")
    print(f"Metrics: {metrics_path}")


if __name__ == "__main__":
    main()
