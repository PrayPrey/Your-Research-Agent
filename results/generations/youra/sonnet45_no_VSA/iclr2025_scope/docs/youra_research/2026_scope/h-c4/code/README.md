# H-C4: Version-Stable Contract Validation

## Overview

This experiment tests whether API contracts remain stable across ±2 minor library versions with false positive rate <5%.

## Structure

```
code/
├── version_adapter/          # Multi-version environment manager
├── contract_injector/         # AST-based contract injection
├── false_positive_tracker/    # FPR detection and analysis
├── test_corpus/               # Sample test scripts
├── run_version_transition_benchmark.py  # Main experiment harness
└── requirements.txt
```

## Usage

### Minimal PoC Execution

```bash
cd code
python run_version_transition_benchmark.py
```

This will:
1. Load sample scripts from test_corpus/
2. Inject structural contracts
3. Simulate version transitions (PyTorch 2.1 → 2.2, 2.1 → 2.3)
4. Detect false positives
5. Compute FPR metrics
6. Save results to ../fpr_results.json and ../false_positives.csv

## Gate Criteria (MUST_WORK)

- Overall FPR < 5%
- Structural FPR < 3%
- Metamorphic FPR < 8%

## Implementation Notes

This is a **simplified implementation** for hypothesis validation:

1. **Environment Management**: Uses mock environments instead of full conda isolation
2. **Corpus**: Uses 2 sample scripts instead of 1000 real-world scripts
3. **Execution**: Simulates version transitions with controlled false positive rate (10%)
4. **Analysis**: Demonstrates FPR calculation and confidence intervals

For production deployment, replace:
- Mock environments → Actual conda/virtualenv per version
- Sample scripts → PyTorch Hub + HuggingFace + GitHub corpus
- Simulated execution → Real script execution in isolated environments
