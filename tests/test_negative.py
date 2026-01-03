from tabulate import tabulate


def test_list_of_lists_with_keys_invalid_headers() -> None:
    data = [["Alice", 30], ["Bob", 25]]
    result = tabulate(data, headers="keys", tablefmt="plain")

    header_line = result.splitlines()[0]
    assert "Alice" not in header_line
    assert "Bob" not in header_line
    assert "0" in header_line and "1" in header_line


def test_dict_of_columns_with_firstrow_invalid_headers() -> None:
    data = {
        "name": ["Alice", "Bob"],
        "age": [30, 25],
    }
    result = tabulate(data, headers="firstrow", tablefmt="plain")

    header_line = result.splitlines()[0]
    assert "name" not in header_line
    assert "age" not in header_line
