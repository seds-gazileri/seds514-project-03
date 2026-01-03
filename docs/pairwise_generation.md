# Step 2 - Pairwise Test Case Generation (allpairspy)

## Tool and settings
- Tool: `allpairspy` (Python, version 2.5.1)
- Generation: `AllPairs` with a custom filter function implementing the constraints in `docs/design_spec.md`
- Output formats: CSV and JSON

## Constraints applied
1. `input_type=list_of_dicts` => `headers!=firstrow`
2. `headers=keys` => `input_type` in `{list_of_dicts, dict_of_columns}`
3. `missingval` in `{question, na}` => `data_mix=includes_none`
4. `showindex=custom_iterable` => `size!=small`
5. `headers=firstrow` => `size!=small`

## Outputs
- Pairwise cases (CSV): `generated_data/pairwise_cases.csv`
- Pairwise cases (JSON): `generated_data/pairwise_cases.json`
- Metrics (JSON): `generated_data/pairwise_metrics.json`

## Metrics
- Theoretical combinations (exhaustive): 2,916
- Generated pairwise tests: 16
- Reduction ratio: 0.0055

## Re-generate
```bash
python3 src/generate_pairwise.py
```
