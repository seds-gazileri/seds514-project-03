from pathlib import Path

import pytest
from tabulate import tabulate

from tests.case_utils import build_case, case_id, load_cases


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = PROJECT_ROOT / "generated_data" / "baseline_cases.json"

CASES = load_cases(CASES_PATH)


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_baseline_cases(case: dict[str, str]) -> None:
    (
        data,
        headers_param,
        expected_headers,
        showindex_param,
        custom_labels,
        missingval_param,
    ) = build_case(case)

    kwargs = {
        "headers": headers_param,
        "tablefmt": case["tablefmt"],
        "showindex": showindex_param,
    }
    if missingval_param is not None:
        kwargs["missingval"] = missingval_param

    output = tabulate(data, **kwargs)
    assert output.strip()

    oracle_count = 1

    for header in expected_headers:
        assert header in output
    oracle_count += 1

    tablefmt = case["tablefmt"]
    lines = output.splitlines()
    if tablefmt == "github":
        assert lines and lines[0].lstrip().startswith("|")
        assert len(lines) > 1 and "-" in lines[1]
        oracle_count += 1
    elif tablefmt in {"grid", "psql"}:
        assert lines and lines[0].startswith("+") and "-" in lines[0]
        assert "|" in output
        oracle_count += 1

    if custom_labels:
        for label in custom_labels:
            assert label in output
        oracle_count += 1

    if case["data_mix"] == "includes_none" and case["missingval"] in {"question", "na"}:
        placeholder = "?" if case["missingval"] == "question" else "NA"
        assert placeholder in output
        oracle_count += 1

    assert oracle_count >= 2
