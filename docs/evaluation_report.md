# Step 4 - Evaluation Report (Pairwise vs. Baseline)

## Setup
- Pairwise set: `generated_data/pairwise_cases.json` (16 tests)
- Baseline set: `generated_data/baseline_cases.json` (16 tests, seed 51403)
- Constraints: same filter as `src/pairwise_model.py`

## Coverage Method
Coverage is computed over all valid 2-way factor pairs derived from the full, constrained space.
- Valid combinations (after constraints): 1,040
- Valid 2-way pairs: 199

## Results
- Pairwise coverage: 182 / 199 = 0.9146
- Baseline coverage: 151 / 199 = 0.7588
- Failures found: none in either suite (all tests passed)

## Notes
- The baseline uses random sampling without replacement to match the same test budget.
- Pairwise coverage is higher than the baseline, as expected for 2-way interaction testing.
