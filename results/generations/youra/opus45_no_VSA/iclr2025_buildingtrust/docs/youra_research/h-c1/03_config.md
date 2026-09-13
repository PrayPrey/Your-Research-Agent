# H-C1 Configuration

## Codebase Analysis (Serena)

**Project Type**: green-field (statistical validation task, no prior H-C1 code)
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict

**Note**: H-E1 outputs are read as data inputs only (JSON/CSV), not as config classes to inherit — H-C1 does not extend H-E1's PCA/training config.

---

## A-1: Prospective Structural Validity Test [Complexity: 1, Budget: 1]

**Applied**: Standard bootstrap CI defaults (no KB pattern needed — pure stats, no training)

### Configuration (Hardcoded Dict)

```python
CONFIG = {
    # Inputs from H-E1
    "h_e1_results_path": "h-e1/outputs/h_e1_results.json",
    "h_e1_residualized_matrix_path": "h-e1/outputs/residualized_matrix.csv",

    # TrustLLM holdout data
    "trustllm_repo": "https://github.com/HowieHwong/TrustLLM",
    "holdout_dimensions": ["truthfulness", "safety", "fairness", "robustness"],

    # Outputs
    "output_dir": "h-c1/outputs/",
    "figures_dir": "h-c1/figures/",

    # Validation thresholds
    "loading_threshold": 0.3,
    "min_successful_benchmarks": 2,

    # Bootstrap
    "n_bootstrap": 1000,
    "confidence_level": 0.95,
    "random_seed": 42,
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Loading validation | Project TrustLLM holdout benchmarks onto frozen PC1, bootstrap CI, check against `loading_threshold` with `min_successful_benchmarks` |
