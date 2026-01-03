from __future__ import annotations

import csv
import json
import random
from itertools import combinations, product
from pathlib import Path

from pairwise_model import FACTORS, FACTOR_NAMES, THEORETICAL_COMBINATIONS, is_valid


def generate_baseline_cases(count: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    seen: set[tuple[str, ...]] = set()
    cases: list[dict[str, str]] = []
    attempts = 0
    max_attempts = count * 500

    while len(cases) < count and attempts < max_attempts:
        attempts += 1
        row = [rng.choice(levels) for levels in FACTORS]
        if not is_valid(row):
            continue
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)
        cases.append(dict(zip(FACTOR_NAMES, row)))

    if len(cases) < count:
        raise RuntimeError("Unable to generate enough unique baseline cases.")

    return cases


def enumerate_valid_combinations() -> list[tuple[str, ...]]:
    valid = []
    for row in product(*FACTORS):
        if is_valid(list(row)):
            valid.append(tuple(row))
    return valid


def pairwise_coverage(cases: list[dict[str, str]], all_valid_pairs: set[tuple[int, str, int, str]]):
    covered: set[tuple[int, str, int, str]] = set()
    for case in cases:
        values = [case[name] for name in FACTOR_NAMES]
        for i, j in combinations(range(len(values)), 2):
            covered.add((i, values[i], j, values[j]))
    return len(covered), len(all_valid_pairs)


def compute_valid_pairs(valid_combos: list[tuple[str, ...]]):
    valid_pairs: set[tuple[int, str, int, str]] = set()
    for combo in valid_combos:
        for i, j in combinations(range(len(combo)), 2):
            valid_pairs.add((i, combo[i], j, combo[j]))
    return valid_pairs


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "generated_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    pairwise_cases = json.loads((output_dir / "pairwise_cases.json").read_text(encoding="utf-8"))
    baseline_count = len(pairwise_cases)

    seed = 51403
    baseline_cases = generate_baseline_cases(baseline_count, seed)

    baseline_csv = output_dir / "baseline_cases.csv"
    with baseline_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FACTOR_NAMES)
        writer.writeheader()
        writer.writerows(baseline_cases)

    baseline_json = output_dir / "baseline_cases.json"
    baseline_json.write_text(json.dumps(baseline_cases, indent=2), encoding="utf-8")

    valid_combos = enumerate_valid_combinations()
    valid_pairs = compute_valid_pairs(valid_combos)

    pairwise_covered, total_pairs = pairwise_coverage(pairwise_cases, valid_pairs)
    baseline_covered, _ = pairwise_coverage(baseline_cases, valid_pairs)

    metrics = {
        "baseline_count": baseline_count,
        "baseline_seed": seed,
        "theoretical_combinations": THEORETICAL_COMBINATIONS,
        "valid_combinations": len(valid_combos),
        "pairwise_total_pairs": total_pairs,
        "pairwise_covered_pairs": pairwise_covered,
        "pairwise_coverage_ratio": round(pairwise_covered / total_pairs, 4),
        "baseline_covered_pairs": baseline_covered,
        "baseline_coverage_ratio": round(baseline_covered / total_pairs, 4),
    }

    metrics_path = output_dir / "baseline_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Wrote baseline cases to {baseline_csv}")
    print(f"Wrote baseline metrics to {metrics_path}")


if __name__ == "__main__":
    main()
