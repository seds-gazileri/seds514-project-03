# Pairwise Test Design Specification

## SEDS 514 - Software Testing - Project 3

### System Under Test

**python-tabulate** (https://github.com/astanin/python-tabulate)
A Python library that pretty-prints tabular data in various formats.

---

## 1. Factors and Levels

### Factor 1: Input Table Type (input_type)

The structure of the input data passed to `tabulate()`.

| Level ID | Level Name      | Description                                    | Example                                              |
| -------- | --------------- | ---------------------------------------------- | ---------------------------------------------------- |
| IT1      | list_of_lists   | List containing sublists as rows               | `[["a", 1], ["b", 2]]`                               |
| IT2      | list_of_dicts   | List containing dictionaries (keys as headers) | `[{"name": "a", "val": 1}, {"name": "b", "val": 2}]` |
| IT3      | dict_of_columns | Dictionary where keys are column names         | `{"name": ["a", "b"], "val": [1, 2]}`                |

### Factor 2: Headers Mode (headers)

How column headers are specified.

| Level ID | Level Name    | Description                                      |
| -------- | ------------- | ------------------------------------------------ |
| HM1      | explicit_list | Headers provided as explicit list                |
| HM2      | firstrow      | First row of data used as headers (`"firstrow"`) |
| HM3      | keys          | Use dictionary keys as headers (`"keys"`)        |

### Factor 3: Table Format (tablefmt)

The output format of the table.

| Level ID | Level Name | Description                             |
| -------- | ---------- | --------------------------------------- |
| TF1      | plain      | No borders, simple whitespace alignment |
| TF2      | github     | GitHub-flavored markdown table          |
| TF3      | grid       | ASCII grid with box-drawing characters  |
| TF4      | psql       | PostgreSQL-style table format           |

### Factor 4: Row Indices (showindex)

Whether to display row indices/numbers.

| Level ID | Level Name      | Description                                     |
| -------- | --------------- | ----------------------------------------------- |
| SI1      | always          | Always show index (`showindex="always"`)        |
| SI2      | never           | Never show index (`showindex="never"` or False) |
| SI3      | custom_iterable | Custom row labels (e.g., `["r0", "r1", ...]`)   |

### Factor 5: Missing Value Handling (missingval)

How `None` or missing values are displayed.

| Level ID | Level Name | Description                     |
| -------- | ---------- | ------------------------------- |
| MV1      | default    | Default behavior (empty string) |
| MV2      | question   | Display "?" for missing values  |
| MV3      | na         | Display "NA" for missing values |

### Factor 6: Data Mix (data_mix)

The types of data contained in the table cells.

| Level ID | Level Name    | Description                                    |
| -------- | ------------- | ---------------------------------------------- |
| DM1      | all_strings   | All cell values are strings                    |
| DM2      | ints_floats   | Mix of integers and floating-point numbers     |
| DM3      | includes_none | Data contains None values (to test missingval) |

### Factor 7: Row/Column Size (size)

The dimensions and content characteristics of the table.

| Level ID | Level Name | Description                            |
| -------- | ---------- | -------------------------------------- |
| SZ1      | small      | 2 rows x 2 columns                     |
| SZ2      | medium     | 5 rows x 4 columns                     |
| SZ3      | wide_text  | Contains long strings (50+ characters) |

---

## 2. Factor Summary Table

| Factor # | Factor Name   | Code       | # Levels | Level Values                                  |
| -------- | ------------- | ---------- | -------- | --------------------------------------------- |
| 1        | Input Type    | input_type | 3        | list_of_lists, list_of_dicts, dict_of_columns |
| 2        | Headers Mode  | headers    | 3        | explicit_list, firstrow, keys                 |
| 3        | Table Format  | tablefmt   | 4        | plain, github, grid, psql                     |
| 4        | Show Index    | showindex  | 3        | always, never, custom_iterable                |
| 5        | Missing Value | missingval | 3        | default, question, na                         |
| 6        | Data Mix      | data_mix   | 3        | all_strings, ints_floats, includes_none       |
| 7        | Size          | size       | 3        | small, medium, wide_text                      |

**Total theoretical combinations (exhaustive):** 3 x 3 x 4 x 3 x 3 x 3 x 3 = **2,916 test cases**

---

## 3. Pairwise Model (7 Factors)

This model captures the 7 factors and their levels in a compact, machine-readable format.

```
model:
  input_type: [list_of_lists, list_of_dicts, dict_of_columns]
  headers: [explicit_list, firstrow, keys]
  tablefmt: [plain, github, grid, psql]
  showindex: [always, never, custom_iterable]
  missingval: [default, question, na]
  data_mix: [all_strings, ints_floats, includes_none]
  size: [small, medium, wide_text]
```

---

## 4. Constraints

The following constraints must be enforced during test generation to avoid invalid or meaningless test combinations.

### Constraint 1: headers="firstrow" invalid with list_of_dicts

**Rule:** IF `input_type = list_of_dicts` THEN `headers != firstrow`

**Rationale:** When input is a list of dictionaries, the dictionary keys naturally serve as headers. Using `"firstrow"` would incorrectly treat the first dictionary's values as headers, which is semantically incorrect and produces unexpected output.

**Example - Invalid Combination:**

```python
from tabulate import tabulate

# list_of_dicts input
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]

# INVALID: Using firstrow with list_of_dicts
result = tabulate(data, headers="firstrow")
# This treats "Alice" and 30 as headers, which is semantically wrong
# Output:
# Alice      30
# -------  ----
# Bob        25
```

**Example - Valid Alternative:**

```python
# VALID: Use "keys" instead to get proper headers
result = tabulate(data, headers="keys")
# Output:
# name      age
# ------  -----
# Alice      30
# Bob        25
```

---

### Constraint 2: headers="keys" requires dict-like input

**Rule:** IF `headers = keys` THEN `input_type IN {list_of_dicts, dict_of_columns}`

**Rationale:** The `"keys"` header mode extracts headers from dictionary keys. This only makes sense for dict-based input types. Using `"keys"` with `list_of_lists` would raise an error or produce incorrect output.

**Example - Invalid Combination:**

```python
from tabulate import tabulate

# list_of_lists input (no dictionary keys available)
data = [
    ["Alice", 30],
    ["Bob", 25]
]

# INVALID: Using keys with list_of_lists
result = tabulate(data, headers="keys")
# Lists don't have .keys() method - produces unexpected output
# The output may show column indices or empty headers
```

**Example - Valid Combinations:**

```python
# VALID: list_of_dicts with headers="keys"
data_dicts = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]
result = tabulate(data_dicts, headers="keys")
# Output:
# name      age
# ------  -----
# Alice      30
# Bob        25

# VALID: dict_of_columns with headers="keys"
data_cols = {
    "name": ["Alice", "Bob"],
    "age": [30, 25]
}
result = tabulate(data_cols, headers="keys")
# Output:
# name      age
# ------  -----
# Alice      30
# Bob        25
```

---

### Constraint 3: missingval only meaningful with None data

**Rule:** IF `missingval IN {question, na}` THEN `data_mix = includes_none`

**Rationale:** Testing custom missing value representations (`"?"` or `"NA"`) only makes sense when the data actually contains `None` values. Otherwise, the missingval parameter has no observable effect.

**Example - Meaningless Combination:**

```python
from tabulate import tabulate

# Data with NO None values
data = [
    ["Alice", 30],
    ["Bob", 25]
]

# MEANINGLESS: missingval="?" has no effect
result = tabulate(data, headers=["Name", "Age"], missingval="?")
# Output (same as without missingval):
# Name      Age
# ------  -----
# Alice      30
# Bob        25
# The "?" never appears because there are no missing values
```

**Example - Meaningful Combination:**

```python
# Data WITH None values
data = [
    ["Alice", 30],
    ["Bob", None],      # None value here
    [None, 25]          # None value here
]

# MEANINGFUL: missingval="?" replaces None
result = tabulate(data, headers=["Name", "Age"], missingval="?")
# Output:
# Name      Age
# ------  -----
# Alice      30
# Bob         ?
# ?          25

# MEANINGFUL: missingval="NA" replaces None
result = tabulate(data, headers=["Name", "Age"], missingval="NA")
# Output:
# Name      Age
# ------  -----
# Alice      30
# Bob        NA
# NA         25
```

---

### Constraint 4: custom_iterable index requires sufficient rows

**Rule:** IF `showindex = custom_iterable` THEN `size != small`

**Rationale:** Custom index iterables (like `["r0", "r1", "r2", ...]`) need enough rows to demonstrate the feature meaningfully. A 2x2 table is too small to properly test custom indexing behavior.

**Example - Inadequate Testing (Small Table):**

```python
from tabulate import tabulate

# Small 2x2 table
data = [
    ["Alice", 30],
    ["Bob", 25]
]

# Only 2 custom indices - minimal testing
result = tabulate(data, headers=["Name", "Age"], showindex=["r0", "r1"])
# Output:
#       Name      Age
# --  ------  -----
# r0  Alice      30
# r1  Bob        25
# Hard to verify proper index alignment with only 2 rows
```

**Example - Adequate Testing (Medium Table):**

```python
# Medium 5x4 table
data = [
    ["Alice", 30, "NYC", "Engineer"],
    ["Bob", 25, "LA", "Designer"],
    ["Carol", 35, "Chicago", "Manager"],
    ["David", 28, "Boston", "Analyst"],
    ["Eve", 32, "Seattle", "Developer"]
]

# 5 custom indices - better coverage
custom_index = ["row_a", "row_b", "row_c", "row_d", "row_e"]
result = tabulate(data, headers=["Name", "Age", "City", "Role"], showindex=custom_index)
# Output:
#         Name      Age  City      Role
# -----  ------  -----  --------  ---------
# row_a  Alice      30  NYC       Engineer
# row_b  Bob        25  LA        Designer
# row_c  Carol      35  Chicago   Manager
# row_d  David      28  Boston    Analyst
# row_e  Eve        32  Seattle   Developer
# Better demonstrates custom indexing across multiple rows
```

---

### Constraint 5: firstrow headers require extra data row

**Rule:** IF `headers = firstrow` THEN `size != small`

**Rationale:** When using `"firstrow"`, the first row becomes headers, leaving only 1 data row in a 2x2 table. This edge case may not adequately test the feature and could cause issues with index alignment.

**Example - Inadequate Testing (Small Table):**

```python
from tabulate import tabulate

# Small 2x2 table
data = [
    ["Name", "Age"],     # This becomes the header
    ["Alice", 30]        # Only 1 data row remains!
]

result = tabulate(data, headers="firstrow")
# Output:
# Name      Age
# ------  -----
# Alice      30
# Only 1 data row - cannot test multi-row scenarios
```

**Example - Adequate Testing (Medium Table):**

```python
# Medium table with firstrow as headers
data = [
    ["Name", "Age", "City", "Role"],     # Header row
    ["Alice", 30, "NYC", "Engineer"],
    ["Bob", 25, "LA", "Designer"],
    ["Carol", 35, "Chicago", "Manager"],
    ["David", 28, "Boston", "Analyst"]   # 4 data rows remain
]

result = tabulate(data, headers="firstrow")
# Output:
# Name      Age  City      Role
# ------  -----  --------  ---------
# Alice      30  NYC       Engineer
# Bob        25  LA        Designer
# Carol      35  Chicago   Manager
# David      28  Boston    Analyst
# 4 data rows allow proper testing of alignment and formatting
```

---

### Constraint 6: dict_of_columns with firstrow is invalid (Negative Test)

**Rule:** IF `input_type = dict_of_columns` AND `headers = firstrow` THEN **NEGATIVE TEST**

**Rationale:** Dict of columns input where keys are column names doesn't support `"firstrow"` semantically. This combination should either raise an exception or produce unexpected output. Marked as a negative test case.

**Example - Invalid Combination (Negative Test):**

```python
from tabulate import tabulate

# dict_of_columns - keys ARE the column names
data = {
    "name": ["Alice", "Bob", "Carol"],
    "age": [30, 25, 35]
}

# INVALID: firstrow makes no sense here
result = tabulate(data, headers="firstrow")
# Problematic: The first "row" would be ("Alice", 30)
# But dict keys should be the headers, not the first values
# Output may be confusing/incorrect:
# Alice      30
# -------  ----
# Bob        25
# Carol      35
# This loses "name" and "age" as headers entirely!
```

**Example - Valid Alternative:**

```python
# VALID: Use "keys" to properly extract column names
result = tabulate(data, headers="keys")
# Output:
# name      age
# ------  -----
# Alice      30
# Bob        25
# Carol      35
# Headers correctly come from dictionary keys
```

**Negative Test Assertion:**

```python
def test_dict_of_columns_with_firstrow_negative():
    """Verify that dict_of_columns with firstrow produces unexpected output."""
    data = {
        "name": ["Alice", "Bob"],
        "age": [30, 25]
    }
    result = tabulate(data, headers="firstrow")

    # Assert that proper column names are NOT in headers
    # (This is the "negative" behavior we're documenting)
    assert "name" not in result.split('\n')[0]
    assert "age" not in result.split('\n')[0]
```

---

## 5. Constraint Summary (PICT Format)

For use with Microsoft PICT or similar tools:

```
# Factors
input_type: list_of_lists, list_of_dicts, dict_of_columns
headers: explicit_list, firstrow, keys
tablefmt: plain, github, grid, psql
showindex: always, never, custom_iterable
missingval: default, question, na
data_mix: all_strings, ints_floats, includes_none
size: small, medium, wide_text

# Constraints
IF [input_type] = "list_of_dicts" THEN [headers] <> "firstrow";
IF [headers] = "keys" THEN [input_type] IN {"list_of_dicts", "dict_of_columns"};
IF [missingval] IN {"question", "na"} THEN [data_mix] = "includes_none";
IF [showindex] = "custom_iterable" THEN [size] <> "small";
IF [headers] = "firstrow" THEN [size] <> "small";
```

---

## 6. Negative Test Cases

The following combinations are expected to raise exceptions or produce error conditions:

| ID  | Combination                                  | Expected Behavior           |
| --- | -------------------------------------------- | --------------------------- |
| N1  | input_type=dict_of_columns, headers=firstrow | Unexpected/invalid output   |
| N2  | input_type=list_of_lists, headers=keys       | TypeError or invalid output |

These will be tested separately to verify proper error handling.

---

## 7. Test Oracles

For each generated test case, we will assert at least two of the following:

1. **Non-empty output with headers:** When headers are enabled (explicit_list, firstrow, or keys), verify the output contains the expected header labels.

2. **Format markers present:** Each table format has distinctive markers:

   - `plain`: No special markers, whitespace-separated
   - `github`: Contains `|` and `-` characters in header separator
   - `grid`: Contains `+`, `-`, and `|` characters
   - `psql`: Contains `+`, `-`, and `|` with specific pattern

3. **Index column present:** When `showindex="always"` or custom_iterable, verify the output includes the index column (first column contains numeric indices or custom labels).

4. **Missing value substitution:** When `data_mix=includes_none` and `missingval="?"` or `"NA"`, verify the output contains the specified placeholder at positions where None values exist.

---

## Document Information

- **Course:** SEDS 514 Software Testing
- **Project:** Project 3 - Pairwise Test Design
- **Target System:** python-tabulate
- **Date:** December 2024
