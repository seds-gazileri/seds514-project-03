from __future__ import annotations

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

THEORETICAL_COMBINATIONS = 3 * 3 * 4 * 3 * 3 * 3 * 3


def is_valid(row: list[str | None]) -> bool:
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
