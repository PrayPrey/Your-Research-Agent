# h-c1 Configuration: Mode Profile Stability (Cronbach's Alpha)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (simplified statistical analysis, no NN training)
**Config Files Found**: None - new config
**Pattern Used**: dict

**Applied**: Standard PyTorch/NumPy defaults

## A-1: Alpha Reliability Analysis [Complexity: 1, Budget: 1]

### Configuration (Hardcoded Dict)
```python
CONFIG = {
    "attribution_scores_path": "docs/youra_research/h-m1/code/output/attribution_scores.npz",
    "methods": ["trak", "tracin", "kronfluence"],
    "modes": ["memorization", "feature_transfer", "spurious"],
    "alpha_threshold": 0.8,
    "min_sample_size": 500,
    "output_dir": "docs/youra_research/h-c1/figures",
    "figure_paths": {
        "alpha_by_mode": "docs/youra_research/h-c1/figures/alpha_by_mode.png",
        "alpha_by_method": "docs/youra_research/h-c1/figures/alpha_by_method.png",
    },
    "seed": 42,
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Alpha computation | Load NPZ, compute Cronbach's alpha per (method, mode), plot vs threshold |
