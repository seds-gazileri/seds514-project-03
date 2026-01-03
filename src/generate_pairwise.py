from __future__ import annotations

import csv
import json
from pathlib import Path

from allpairspy import AllPairs
from importlib import metadata

from pairwise_model import (
    FACTORS,
    FACTOR_NAMES,
    THEORETICAL_COMBINATIONS,
    is_valid,
)


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
        "theoretical_combinations": THEORETICAL_COMBINATIONS,
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
