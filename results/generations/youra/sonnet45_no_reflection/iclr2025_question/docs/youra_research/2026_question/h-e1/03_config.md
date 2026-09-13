---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
created_at: 2026-05-12
author: configuration-agent
---

# Configuration Design: H-E1 Geometric Uncertainty Correlation

**Applied**: Hardcoded constants pattern (LIGHT tier, PoC experiment)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - no existing config to analyze
**Config Files Found**: None - new config design
**Pattern Used**: Hardcoded dict (minimal infrastructure)

---

## A-6: Correlation Analysis (Complexity: 10, Budget: 2)

**Applied**: Standard scipy defaults for statistical testing

### Configuration (Hardcoded Dict)

```python
# analysis/config.py
CORRELATION_CONFIG = {
    "method": "spearman",              # Spearman rank correlation
    "n_bootstrap": 1000,               # Bootstrap resamples for CI
    "confidence_level": 0.95,          # 95% confidence interval
    "gate_rho_threshold": 0.4,         # |ρ| > 0.4 required
    "gate_p_threshold": 0.001,         # p < 0.001 required
    "gate_ci_threshold": 0.3,          # CI must exclude 0.3
}

VISUALIZATION_CONFIG = {
    "figure_size": (10, 6),
    "dpi": 300,
    "scatter_alpha": 0.6,
    "output_dir": "outputs/figures",
    "format": "png",
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Statistical Tests | Spearman correlation, bootstrap CI computation |
| C-6-2 | Visualizations | Scatter plots, distributions, heatmap generation |

---

## A-3: Hidden State Extraction (Complexity: 9, Budget: 1)

**Applied**: Standard HuggingFace transformers defaults

### Configuration (Hardcoded Dict)

```python
# models/config.py
EXTRACTION_CONFIG = {
    "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
    "target_layers": [24, 25, 26, 27, 28, 29, 30, 31],
    "output_hidden_states": True,
    "device": "cuda",
    "dtype": "float16",                # Inference precision
    "batch_size": 4,
    "position": "final_token",         # Extract from final token position
}
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Model Loading | Load Llama-3-8B-Instruct with hidden state extraction |

---

## Global Experiment Configuration

### Main Experiment Settings

```python
# config.py (root level)
EXPERIMENT_CONFIG = {
    # Model settings
    "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
    "nli_model": "microsoft/deberta-v3-base",
    "target_layers": [24, 25, 26, 27, 28, 29, 30, 31],
    
    # Data settings
    "split_ratio": 0.7,                # 70% train, 30% test
    "seed": 42,
    
    # Semantic entropy settings
    "k_samples": 10,                   # Number of generations
    "temperature": 0.7,                # Sampling temperature
    
    # Batch processing
    "batch_size": 4,
    
    # Numerical stability
    "epsilon": 1e-12,                  # For condition number, PR denominators
    
    # Output paths
    "output_dir": "outputs",
    "figures_dir": "outputs/figures",
}
```

### Geometric Features Configuration

```python
# metrics/config.py
GEOMETRIC_CONFIG = {
    "epsilon": 1e-12,                  # Numerical stability
    "compute_precision": "float32",    # For covariance/eigenvalue computation
    "eigenvalue_method": "eigvalsh",   # Symmetric matrix solver
}

# Feature-specific defaults (no hyperparameter tuning for EXISTENCE)
FEATURE_PARAMS = {
    "participation_ratio": {
        "formula": "(sum(λ))² / sum(λ²)",
    },
    "eigenvalue_decay": {
        "fit_method": "linear",        # Linear regression on log-spectrum
    },
    "condition_number": {
        "formula": "λ_max / (λ_min + ε)",
    },
}
```

### Semantic Entropy Configuration

```python
# metrics/semantic_config.py
SEMANTIC_ENTROPY_CONFIG = {
    "k_samples": 10,
    "temperature": 0.7,
    "nli_model": "microsoft/deberta-v3-base",
    "clustering_threshold": 0.5,       # NLI entailment threshold
    "device": "cuda",
}
```

### Gate Evaluation Configuration

```python
# evaluation/config.py
GATE_CONFIG = {
    "must_work": True,
    "criteria": {
        "min_rho": 0.4,                # |ρ| > 0.4
        "max_p_value": 0.001,          # p < 0.001
        "ci_exclusion": 0.3,           # 95% CI excludes 0.3
    },
    "features": ["pr", "alpha", "kappa"],
}
```

---

## Usage Pattern

### Command Line Interface (Minimal)

```python
# main.py
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="H-E1 Geometric Uncertainty Correlation")
    parser.add_argument("--output_dir", default="outputs", help="Output directory")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--gpu", type=int, default=0, help="GPU device ID")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Override defaults if provided
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    
    EXPERIMENT_CONFIG["output_dir"] = args.output_dir
    EXPERIMENT_CONFIG["batch_size"] = args.batch_size
    EXPERIMENT_CONFIG["seed"] = args.seed
    
    # Run experiment with hardcoded configs
    results = run_experiment(EXPERIMENT_CONFIG)
```

---

## Rationale for Non-Standard Values

**Target Layers [24-31]**: Research hypothesis targets final 25% of Llama-3-8B (32 total layers) where semantic processing occurs.

**K=10 samples**: Standard from Semantic Uncertainty paper for epistemic uncertainty quantification.

**Temperature 0.7**: NLI model default from microsoft/deberta-v3-base, balances diversity and coherence.

**Epsilon 1e-12**: Numerical stability for eigenvalue ratios, prevents division by zero in degenerate cases.

---

## Configuration Validation

### Required Checks

```python
# utils/validation.py
def validate_config():
    """Validate configuration before experiment run."""
    assert len(EXPERIMENT_CONFIG["target_layers"]) == 8, "Must extract 8 layers"
    assert all(24 <= l <= 31 for l in EXPERIMENT_CONFIG["target_layers"]), "Layers must be 24-31"
    assert EXPERIMENT_CONFIG["split_ratio"] == 0.7, "Fixed 70/30 split required"
    assert EXPERIMENT_CONFIG["k_samples"] == 10, "K=10 required for SE computation"
    assert GATE_CONFIG["criteria"]["min_rho"] == 0.4, "Gate threshold |ρ| > 0.4"
    print("✓ Configuration validated")
```

---

## File Organization

```
code/
├── config.py                        # Global experiment config
├── models/
│   └── config.py                   # Model loading config
├── metrics/
│   ├── config.py                   # Geometric features config
│   └── semantic_config.py          # Semantic entropy config
├── analysis/
│   └── config.py                   # Correlation & visualization config
├── evaluation/
│   └── config.py                   # Gate evaluation config
└── utils/
    └── validation.py               # Config validation
```

---

*Generated by configuration-agent*
*Date: 2026-05-12*
*Next: Phase 4 - Implementation*
