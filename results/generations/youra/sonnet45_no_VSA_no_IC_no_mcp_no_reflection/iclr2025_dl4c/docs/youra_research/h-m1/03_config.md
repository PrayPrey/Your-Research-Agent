# Configuration Schema: h-m1 Error Clustering Analyzer

**Hypothesis:** h-m1 (MUST_WORK gate)  
**Gate:** Clustering coefficient > 0.3 AND p < 0.05  
**Project Type:** Green-field (no base hypothesis)  
**Config Format:** Hardcoded dict (copy-paste ready)

---

## Experiment Configuration

```python
# h-m1/code/config.py
EXPERIMENT_CONFIG = {
    # Model
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,
    "timeout": 60,
    
    # Dataset
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,
    
    # Debugging loop
    "max_iterations": 10,
    "test_timeout": 5,
    
    # Annotation
    "min_annotators": 2,
    "kappa_threshold": 0.7,
    "error_types": ["syntax", "runtime", "logic", "edge_case"],
    
    # Metrics
    "clustering_threshold": 0.3,
    "p_value_threshold": 0.05,
    "num_permutations": 1000,
    
    # Reproducibility
    "random_seed": 1,
    
    # API
    "codeforces_rate_limit": 10,  # req/min
    "openai_retry_count": 3,
    "retry_backoff": 2.0,
    
    # Paths
    "output_dir": "docs/youra_research/h-m1/results",
    "figures_dir": "docs/youra_research/h-m1/figures",
    "cache_dir": "docs/youra_research/h-m1/cache",
    "annotations_path": "docs/youra_research/h-m1/annotations.json",
}
```

---

## Validation Rules

```python
# h-m1/code/config.py (continued)
def validate_config(config: dict) -> None:
    """Validate experiment configuration."""
    assert config["model"].startswith("gpt-4"), "Must use GPT-4"
    assert 0 <= config["temperature"] <= 1, "Temperature in [0, 1]"
    assert config["num_problems"] >= 50, "Need 50+ problems"
    assert config["min_test_cases"] >= 15, "Need 15+ test cases"
    assert config["kappa_threshold"] >= 0.7, "Kappa must be ≥ 0.7"
    assert config["clustering_threshold"] == 0.3, "Gate threshold fixed"
    assert config["p_value_threshold"] == 0.05, "Gate threshold fixed"
    assert config["random_seed"] == 1, "Reproducibility: seed=1"
```

---

## Usage

```python
# h-m1/code/main.py
from config import EXPERIMENT_CONFIG, validate_config

validate_config(EXPERIMENT_CONFIG)

# Direct access
model = EXPERIMENT_CONFIG["model"]
num_problems = EXPERIMENT_CONFIG["num_problems"]
```

---

## Gate Evaluation

```python
# h-m1/code/evaluation.py
def evaluate_gate(clustering_coef: float, p_value: float) -> bool:
    """MUST_WORK gate check."""
    threshold_c = EXPERIMENT_CONFIG["clustering_threshold"]
    threshold_p = EXPERIMENT_CONFIG["p_value_threshold"]
    
    passed = clustering_coef > threshold_c and p_value < threshold_p
    print(f"Gate: {'PASS' if passed else 'PIVOT'}")
    print(f"  Clustering: {clustering_coef:.3f} (> {threshold_c})")
    print(f"  p-value: {p_value:.4f} (< {threshold_p})")
    
    return passed
```

---

## Notes

- Values from PRD Section 1-5 (model, dataset, metrics)
- No hyperparameter grid (PoC uses fixed defaults)
- Paths relative to project root
- Gate thresholds non-configurable (MUST_WORK requirements)
