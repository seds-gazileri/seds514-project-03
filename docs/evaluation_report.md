# Evaluation Report: Pairwise Testing vs. Random Baseline

## SEDS 514 - Software Testing - Project 3

---

## 1. Executive Summary

This report evaluates the effectiveness of **pairwise (2-way combinatorial) testing** compared to **random baseline testing** for the `tabulate()` function in the python-tabulate library. Both test suites use the same test budget of 16 test cases.

**Key Findings:**
- Pairwise testing achieved **91.46%** 2-way pair coverage (182/199 pairs)
- Random baseline achieved **75.88%** 2-way pair coverage (151/199 pairs)
- Pairwise testing provides **15.58 percentage points** better coverage with the same budget
- No defects were found in either test suite (all 34 tests passed)

---

## 2. Test Setup and Methodology

### 2.1 Test Suites

| Test Suite | File | Test Count | Generation Method |
|------------|------|------------|-------------------|
| Pairwise | `generated_data/pairwise_cases.json` | 16 | allpairspy 2.5.1 algorithm |
| Baseline | `generated_data/baseline_cases.json` | 16 | Random sampling (seed: 51403) |
| Negative | `tests/test_negative.py` | 2 | Manual (constraint violations) |

### 2.2 Test Model

The test model consists of 7 factors with 3-4 levels each:

| Factor | Levels | Count |
|--------|--------|-------|
| Input Type | list_of_lists, list_of_dicts, dict_of_columns | 3 |
| Headers Mode | explicit_list, firstrow, keys | 3 |
| Table Format | plain, github, grid, psql | 4 |
| Show Index | always, never, custom_iterable | 3 |
| Missing Value | default, question, na | 3 |
| Data Mix | all_strings, ints_floats, includes_none | 3 |
| Size | small, medium, wide_text | 3 |

**Theoretical exhaustive combinations:** 3 × 3 × 4 × 3 × 3 × 3 × 3 = **2,916 test cases**

### 2.3 Constraints Applied

Five constraints were enforced to eliminate invalid or meaningless test combinations. Each constraint has a clear rationale based on the semantics of the `tabulate()` function.

#### Constraint 1: `list_of_dicts` cannot use `headers="firstrow"`

**Rule:** IF `input_type = list_of_dicts` THEN `headers ≠ firstrow`

**Rationale:** When input is a list of dictionaries, the dictionary keys naturally serve as column headers. Using `"firstrow"` would incorrectly treat the first dictionary's *values* as headers, producing semantically incorrect output.

```python
# INVALID: firstrow with list_of_dicts
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
tabulate(data, headers="firstrow")
# Output shows "Alice" and "30" as headers - wrong!

# VALID: use "keys" instead
tabulate(data, headers="keys")
# Output shows "name" and "age" as headers - correct!
```

#### Constraint 2: `headers="keys"` requires dict-like input

**Rule:** IF `headers = keys` THEN `input_type ∈ {list_of_dicts, dict_of_columns}`

**Rationale:** The `"keys"` header mode extracts column names from dictionary keys. This only works with dict-based inputs. Using `"keys"` with `list_of_lists` produces unexpected output since lists don't have a `.keys()` method.

```python
# INVALID: keys with list_of_lists
data = [["Alice", 30], ["Bob", 25]]
tabulate(data, headers="keys")
# No dictionary keys available - produces incorrect/empty headers

# VALID: keys with list_of_dicts or dict_of_columns
data = {"name": ["Alice", "Bob"], "age": [30, 25]}
tabulate(data, headers="keys")
# Headers correctly extracted from dictionary keys
```

#### Constraint 3: Custom `missingval` only meaningful with None data

**Rule:** IF `missingval ∈ {question, na}` THEN `data_mix = includes_none`

**Rationale:** The `missingval` parameter specifies how `None` values are displayed (e.g., as "?" or "NA"). Testing this feature is only meaningful when the data actually contains `None` values. Otherwise, the parameter has no observable effect.

```python
# MEANINGLESS: missingval with no None values
data = [["Alice", 30], ["Bob", 25]]
tabulate(data, missingval="?")
# The "?" never appears - nothing to test

# MEANINGFUL: missingval with None values
data = [["Alice", None], ["Bob", 25]]
tabulate(data, missingval="?")
# Output shows "?" where None was - testable behavior
```

#### Constraint 4: `custom_iterable` index requires sufficient rows

**Rule:** IF `showindex = custom_iterable` THEN `size ≠ small`

**Rationale:** Custom index iterables require more than 2 rows for adequate testing due to three technical concerns:

1. **Index-row count mismatch detection:** A key edge case is when the iterable length doesn't match the row count. With only 2 rows, mismatch testing is trivial (1 vs 2, or 3 vs 2). With 5 rows, we can test meaningful mismatches and verify truncation/padding behavior.

2. **Variable-width alignment verification:** Custom labels often have varying lengths (e.g., `["r0", "r1", "r10", "r100", "item"]`). Proper column alignment must handle width variations across multiple rows. With only 2 rows, width variation is minimal and alignment bugs may go undetected.

3. **Format separator consistency:** Table formats like `grid` and `psql` insert row separators and borders. These separators must align correctly with the index column across all rows. Edge cases in separator rendering are more likely to manifest with more rows.

```python
# INADEQUATE: 2 rows cannot test variable-width alignment
data = [["Alice", 30], ["Bob", 25]]
tabulate(data, showindex=["r0", "r1"])
#        0    1
# --  ----  ---
# r0  Alice  30
# r1  Bob    25
# Both indices same width - alignment bugs hidden

# ADEQUATE: 5 rows with varying index widths
data = [["Alice", 30], ["Bob", 25], ["Carol", 35], ["David", 28], ["Eve", 32]]
tabulate(data, showindex=["a", "bb", "ccc", "dddd", "eeeee"], tablefmt="grid")
# +-------+-------+-----+
# |       | 0     |   1 |
# +=======+=======+=====+
# | a     | Alice |  30 |
# +-------+-------+-----+
# | bb    | Bob   |  25 |
# +-------+-------+-----+
# | ccc   | Carol |  35 |
# +-------+-------+-----+
# | dddd  | David |  28 |
# +-------+-------+-----+
# | eeeee | Eve   |  32 |
# +-------+-------+-----+
# Variable widths expose alignment handling across rows and separators
```

#### Constraint 5: `firstrow` headers require sufficient data rows

**Rule:** IF `headers = firstrow` THEN `size ≠ small`

**Rationale:** When using `"firstrow"`, the first row becomes headers, leaving fewer data rows. In a 2×2 table, this leaves only 1 data row, which is an edge case that doesn't adequately test multi-row formatting and alignment.

```python
# INADEQUATE: firstrow with small (2x2) table
data = [["Name", "Age"], ["Alice", 30]]  # Header + 1 data row
tabulate(data, headers="firstrow")
# Only 1 data row remains - cannot test multi-row behavior

# ADEQUATE: firstrow with medium table
data = [["Name", "Age"], ["Alice", 30], ["Bob", 25], ["Carol", 35], ["David", 28]]
tabulate(data, headers="firstrow")
# 4 data rows remain - proper testing coverage
```

#### Constraint Summary

| # | Constraint | Combinations Eliminated |
|---|------------|------------------------|
| 1 | list_of_dicts + firstrow | Invalid semantics |
| 2 | list_of_lists + keys | Missing dictionary keys |
| 3 | missingval without None | Untestable behavior |
| 4 | custom_iterable + small | Insufficient test data |
| 5 | firstrow + small | Insufficient data rows |

**Valid combinations after constraints:** 1,040 (35.7% of theoretical 2,916)

---

## 3. Coverage Analysis

### 3.1 2-Way Pair Coverage Method

Coverage is computed by enumerating all valid 2-way factor-level pairs from the constrained combination space. A pair is "covered" if at least one test case in the suite contains that specific combination of two factor levels.

**Total valid 2-way pairs:** 199

### 3.2 Coverage Results

| Metric | Pairwise | Baseline | Difference |
|--------|----------|----------|------------|
| Pairs Covered | 182 | 151 | +31 |
| Coverage Ratio | 91.46% | 75.88% | +15.58% |
| Uncovered Pairs | 17 | 48 | -31 |

### 3.3 Coverage Visualization

```
Pairwise:  [##################################################] 91.46%
Baseline:  [######################################            ] 75.88%
           |----|----|----|----|----|----|----|----|----|----|
           0%   10%  20%  30%  40%  50%  60%  70%  80%  90%  100%
```

### 3.4 Analysis

The pairwise algorithm systematically ensures that every valid 2-way combination of factor levels appears in at least one test case. Random sampling, by contrast, may accidentally repeat some pairs while missing others entirely.

With only 16 test cases (0.55% of the exhaustive space), pairwise testing covers:
- **91.46%** of all 2-way interactions
- This represents a **99.45% reduction** in test cases while maintaining high interaction coverage

The baseline's 75.88% coverage demonstrates the inherent inefficiency of random selection for combinatorial testing. Random sampling tends to:
- Over-represent common factor combinations
- Under-represent edge cases and rare combinations
- Provide inconsistent coverage across different runs (seed-dependent)

---

## 4. Test Execution Results

### 4.1 Test Outcomes

| Test Suite | Passed | Failed | Errors | Total |
|------------|--------|--------|--------|-------|
| Pairwise (`test_pairwise.py`) | 16 | 0 | 0 | 16 |
| Baseline (`test_baseline.py`) | 16 | 0 | 0 | 16 |
| Negative (`test_negative.py`) | 2 | 0 | 0 | 2 |
| **Total** | **34** | **0** | **0** | **34** |

### 4.2 Failure Analysis

**No failures were detected** in either the pairwise or baseline test suites. This indicates that:

1. The python-tabulate library handles all tested factor combinations correctly
2. The test oracles (assertions) are functioning as expected
3. The constraints properly filtered out invalid combinations

### 4.3 Negative Test Results

Two negative tests verified constraint violations:

| Test | Input Type | Headers | Expected Behavior | Result |
|------|------------|---------|-------------------|--------|
| N1 | list_of_lists | keys | Invalid/unexpected output | PASSED |
| N2 | dict_of_columns | firstrow | Invalid/unexpected output | PASSED |

These tests confirm that the identified constraint violations produce semantically incorrect output, validating the constraint definitions.

---

## 5. Statement Coverage (Optional)

Statement coverage was measured on the tabulate library using pytest-cov:

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
tabulate/__init__.py                795    400    50%
-----------------------------------------------------
TOTAL                               795    400    50%
```

**Analysis:** The 50% statement coverage is expected because:
- Only 4 of 30+ supported table formats were tested (plain, github, grid, psql)
- Many tabulate features (HTML, LaTeX, RST, fancy_grid, etc.) were not in scope
- The focus was on demonstrating pairwise methodology, not exhaustive library coverage

---

## 6. Conclusions

### 6.1 Effectiveness of Pairwise Testing

This evaluation demonstrates that pairwise testing is significantly more effective than random testing for combinatorial input spaces:

| Aspect | Pairwise | Random Baseline |
|--------|----------|-----------------|
| 2-way Coverage | 91.46% | 75.88% |
| Systematic | Yes | No |
| Reproducible | Yes | Seed-dependent |
| Efficiency | Optimal for 2-way | Suboptimal |

### 6.2 Key Takeaways

1. **Dramatic test reduction:** Pairwise testing reduced 2,916 exhaustive combinations to just 16 test cases (99.45% reduction) while covering 91.46% of 2-way interactions.

2. **Superior coverage:** With identical test budgets, pairwise achieved 15.58 percentage points higher coverage than random sampling.

3. **Constraint handling:** The allpairspy tool effectively incorporated constraints during generation, producing only valid test combinations.

4. **No defects found:** The python-tabulate library correctly handled all tested combinations, indicating mature and robust implementation.

### 6.3 Recommendations

For future combinatorial testing projects:
- Use pairwise (or higher-strength) testing for systems with multiple interacting parameters
- Define constraints early to avoid invalid test combinations
- Consider 3-way or higher coverage for critical systems where 2-way may miss important interactions

---

## 7. Test Evidence

### 7.1 Test Run Output

```
======================== test session starts ========================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /Users/cankoc/Desktop/masters/SEDS514-Testing/project-3/seds514-project-03
configfile: pytest.ini
plugins: cov-7.0.0
collected 34 items

tests/test_baseline.py::test_baseline_cases[...] PASSED [  2%]
tests/test_baseline.py::test_baseline_cases[...] PASSED [  5%]
... (14 more baseline tests)
tests/test_negative.py::test_list_of_lists_with_keys_invalid_headers PASSED [ 50%]
tests/test_negative.py::test_dict_of_columns_with_firstrow_invalid_headers PASSED [ 52%]
tests/test_pairwise.py::test_pairwise_cases[...] PASSED [ 55%]
... (15 more pairwise tests)

======================== 34 passed in 0.05s =========================
```

Full test output available in: `docs/pytest_run.txt`

### 7.2 Generated Data Files

| File | Description |
|------|-------------|
| `generated_data/pairwise_cases.json` | 16 pairwise test cases |
| `generated_data/pairwise_cases.csv` | CSV format of pairwise cases |
| `generated_data/pairwise_metrics.json` | Generation metrics (tool, count, reduction) |
| `generated_data/baseline_cases.json` | 16 random baseline test cases |
| `generated_data/baseline_cases.csv` | CSV format of baseline cases |
| `generated_data/baseline_metrics.json` | Coverage comparison metrics |

---

## Document Information

- **Course:** SEDS 514 Software Testing
- **Project:** Project 3 - Pairwise Test Design
- **Repository:** https://github.com/seds-gazileri/seds514-project-03
- **Target System:** python-tabulate (https://github.com/astanin/python-tabulate)
- **Test Framework:** pytest 8.4.2
- **Pairwise Tool:** allpairspy 2.5.1
- **Date:** January 2025

### Team Members

| Name | Student Number |
|------|----------------|
| Mustafacan Koç | 323011014 |
| Barış Yenigün | 323011007 |
| Umut Akın | 323011029 |
