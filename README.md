# SEDS 514 Project 3: Pairwise Test Design on python-tabulate

## Project Overview
This project applies pairwise testing (2-way combinatorial interaction testing) to the
[python-tabulate](https://github.com/astanin/python-tabulate) library.

## Project Structure
```
seds514-project-03/
├── docs/                    # Design specification and reports
│   └── design_spec.md       # Factors, levels, and constraints
├── generated_data/          # Pairwise test cases (CSV/JSON)
├── src/                     # Source modules for test generation
├── tests/                   # pytest test suite
│   ├── test_pairwise.py     # Pairwise-generated tests
│   └── test_baseline.py     # Random baseline tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation
```bash
# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tabulate --cov-report=html

# Run only pairwise tests
pytest tests/test_pairwise.py -v

# Run only baseline tests
pytest tests/test_baseline.py -v
```

## Project Deliverables
1. Design spec (docs/design_spec.md)
2. Pairwise test set (generated_data/)
3. pytest test suite (tests/)
4. Evaluation report (docs/evaluation_report.md)
