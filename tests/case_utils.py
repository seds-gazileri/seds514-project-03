from __future__ import annotations

import json
from pathlib import Path

FACTOR_ORDER = [
    "input_type",
    "headers",
    "tablefmt",
    "showindex",
    "missingval",
    "data_mix",
    "size",
]

SIZE_DIMENSIONS = {
    "small": (2, 2),
    "medium": (5, 4),
    "wide_text": (3, 3),
}


def build_headers(size: str) -> list[str]:
    if size == "small":
        return ["ColA", "ColB"]
    if size == "medium":
        return ["Name", "Age", "City", "Role"]
    return [
        "VeryLongHeaderColumnOne_XXXXXXXXXXXXXXXXXXXX",
        "VeryLongHeaderColumnTwo_XXXXXXXXXXXXXXXXXXXX",
        "VeryLongHeaderColumnThree_XXXXXXXXXXXXXXXXXX",
    ]


def build_rows(rows: int, cols: int, data_mix: str, size: str) -> list[list[object]]:
    def string_cell(r: int, c: int) -> str:
        if size == "wide_text":
            return f"long_text_{r}_{c}_" + ("x" * 40)
        return f"S{r}{c}"

    result: list[list[object]] = []
    for r in range(rows):
        row: list[object] = []
        for c in range(cols):
            if data_mix == "all_strings":
                value: object = string_cell(r, c)
            elif data_mix == "ints_floats":
                value = (r * 10 + c) if c % 2 == 0 else (r + c / 10.0)
            else:
                value = string_cell(r, c)
            row.append(value)
        result.append(row)

    if data_mix == "includes_none":
        result[0][0] = None
        if rows > 1 and cols > 1:
            result[1][1] = None

    return result


def to_input_type(input_type: str, headers: list[str], rows: list[list[object]]):
    if input_type == "list_of_lists":
        return rows
    if input_type == "list_of_dicts":
        return [dict(zip(headers, row)) for row in rows]
    return {header: [row[i] for row in rows] for i, header in enumerate(headers)}


def build_case(case: dict[str, str]):
    size = case["size"]
    rows_count, cols_count = SIZE_DIMENSIONS[size]
    headers = build_headers(size)
    rows = build_rows(rows_count, cols_count, case["data_mix"], size)

    headers_mode = case["headers"]
    input_type = case["input_type"]

    if headers_mode == "firstrow":
        data = [headers] + rows
        headers_param = "firstrow"
        expected_headers = headers
    elif headers_mode == "explicit_list":
        data = to_input_type(input_type, headers, rows)
        if input_type == "list_of_dicts":
            headers_param = {header: header for header in headers}
        else:
            headers_param = headers
        expected_headers = headers
    else:
        data = to_input_type(input_type, headers, rows)
        headers_param = "keys"
        expected_headers = headers

    data_rows_count = rows_count

    showindex = case["showindex"]
    if showindex == "custom_iterable":
        custom_labels = [f"row_{i}" for i in range(data_rows_count)]
        showindex_param = custom_labels
    else:
        custom_labels = []
        showindex_param = showindex

    missingval = case["missingval"]
    missingval_param = None
    if missingval == "question":
        missingval_param = "?"
    elif missingval == "na":
        missingval_param = "NA"

    return (
        data,
        headers_param,
        expected_headers,
        showindex_param,
        custom_labels,
        missingval_param,
    )


def case_id(case: dict[str, str]) -> str:
    return "|".join(f"{key}={case[key]}" for key in FACTOR_ORDER)


def load_cases(path: Path) -> list[dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))
