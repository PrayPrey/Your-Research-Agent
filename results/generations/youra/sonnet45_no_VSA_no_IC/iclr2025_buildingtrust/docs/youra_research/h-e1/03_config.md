# Configuration: H-E1

**Date:** 2026-08-19
**Hypothesis:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair
**Type:** EXISTENCE (PoC)

Applied: Minimal config pattern (single dict, no dataclass for PoC)

---

## Configuration Schema

### config.py

```python
CONFIG = {
    "models": {
        "gpt-4": {
            "model": "gpt-4",
            "temperature": 0.0,
            "max_tokens": 512,
            "seed": 42
        },
        "claude-3-sonnet": {
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.0,
            "max_tokens": 512,
            "seed": 42
        },
        "llama-3-70b": {
            "model": "meta-llama/Llama-3-70b",
            "temperature": 0.0,
            "max_tokens": 512,
            "seed": 42
        }
    },
    "dataset": {
        "name": "thu-ml/MultiTrust",
        "samples": 500,
        "seed": 42,
        "dimensions": ["truthfulness", "robustness", "fairness", "safety", "privacy"]
    },
    "statistical": {
        "phi_threshold": 0.3,
        "p_threshold": 0.01
    },
    "api": {
        "batch_size": 10,
        "retry_max": 3,
        "retry_delay": 5
    },
    "paths": {
        "data": "data/multitrust/",
        "results": "results/",
        "figures": "figures/",
        "logs": "logs/"
    }
}
```

---

## Hyperparameters

### Model Settings

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| temperature | 0.0 | Deterministic outputs for reproducibility |
| max_tokens | 512 | Sufficient for trustworthiness evaluation |
| seed | 42 | Fixed random seed |

### Statistical Thresholds

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| phi_threshold | 0.3 | Medium effect size (Cohen's standard) |
| p_threshold | 0.01 | Statistical significance (99% confidence) |

### Dataset Settings

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| samples | 500 | Per Phase 2B specification, sufficient for chi-square validity |
| dimensions | 5 | MultiTrust coverage (truthfulness, robustness, fairness, safety, privacy) |

### API Settings

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| batch_size | 10 | Rate limit compliance |
| retry_max | 3 | Handle transient failures |
| retry_delay | 5 | Exponential backoff base (seconds) |

---

## Environment Variables

```bash
# API Keys (required)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TOGETHER_API_KEY="..."

# Paths (optional, defaults in CONFIG)
export DATA_DIR="data/"
export RESULTS_DIR="results/"
```

---

## Dependencies Version Pinning

```
# requirements.txt
scipy>=1.11.0
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
huggingface-hub>=0.16.0
openai>=1.0.0
anthropic>=0.3.0
together>=0.2.0
```

---

## Notes

EXISTENCE PoC - minimal infrastructure. Single config dict in config.py, no YAML file or dataclass needed. All settings hardcoded for reproducibility. No hyperparameter tuning (statistical analysis, not learned model).
