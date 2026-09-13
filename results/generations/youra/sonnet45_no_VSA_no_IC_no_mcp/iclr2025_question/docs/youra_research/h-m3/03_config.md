# Configuration: H-M3 Viability Classification

**Date:** 2026-08-25
**Hypothesis:** H-M3 (MECHANISM)
**Gate:** MUST_WORK

---

## Codebase Analysis (Serena)

**Project Type:** Existing codebase - extending h-m1 and h-m2
**Status:** Reusing validated config pattern from h-m1/h-m2
**Config Files Found:** h-m1/03_config.md, h-m2/03_config.md
**Pattern Used:** Hardcoded dict (consistent with h-m1/h-m2 pattern)

---

## Applied Patterns

**Applied:** Hardcoded dict pattern from h-m1/h-m2 (rule-based classifier, no training)

---

## Data Configuration

```python
DATA_CONFIG = {
    "corpus_path": "../h-m1/data/retrospective_corpus_30.csv",
    
    "required_columns": ["O_10", "O_full", "hypothesis_type", "threshold"],
    
    "stratification": {
        "low": {"min": 0.0, "max": 0.20},
        "mid": {"min": 0.20, "max": 0.80},
        "high": {"min": 0.80, "max": 1.0},
    },
    
    "validation": {
        "check_missing": True,
        "check_numeric": True,
        "check_range": (0.0, 1.0),
    },
}
```

---

## Model Configuration

**Applied:** Validated k from h-m1 (r >= 0.7 prerequisite)

```python
MODEL_CONFIG = {
    "scaling_factor_k": None,  # Loaded from h-m1 validation results at runtime
    "k_source": "../h-m1/04_validation.md",  # Extract k from validation report
    
    "threshold": 0.10,  # Viability threshold from Phase 2B deployment context
    
    "baseline_type": "random",
    "baseline_seed": 42,
    "baseline_probability": 0.50,
}
```

Rationale for non-standard values:
- `threshold=0.10`: Deployment context from Phase 2B (10% overhead acceptable)
- `scaling_factor_k=None`: Runtime load ensures consistency with h-m1 validation

---

## Evaluation Configuration

**Applied:** Standard binomial test from scipy.stats

```python
EVAL_CONFIG = {
    "accuracy_target": 0.80,      # Primary success criterion (24/30 correct)
    "null_hypothesis_p": 0.50,    # Random guessing baseline
    "alpha": 0.05,                # Statistical significance level
    
    "metrics": [
        "accuracy",
        "confusion_matrix",
        "binomial_test",
    ],
    
    "confusion_matrix_labels": ["viable", "non-viable"],
    
    "secondary_targets": {
        "non_viable_filter_rate": 0.60,  # 60%+ predicted non-viable
        "failure_threshold": 0.60,       # Accuracy <= 60% = MUST_WORK gate failure
        "partial_threshold": 0.80,       # 60% < accuracy <= 80% = partial success
    },
}
```

---

## Visualization Configuration

**Applied:** Publication-ready matplotlib defaults (reused from h-m1/h-m2)

```python
VIZ_CONFIG = {
    "figsize": (8, 6),
    "dpi": 300,
    "format": "png",
    "tight_layout": True,
    
    "output_dir": "figures",
    
    "colors": {
        "random_baseline": "#95a5a6",    # gray
        "expert_intuition": "#3498db",   # light blue
        "gate1_actual": "#2ecc71",       # green
        "target_line": "#e74c3c",        # red
        "correct_prediction": "#2ecc71", # green
        "incorrect_prediction": "#e74c3c", # red
    },
    
    "bar": {
        "width": 0.6,
        "alpha": 0.8,
        "edgecolor": "black",
        "linewidth": 1,
    },
    
    "scatter": {
        "marker_size": 100,
        "alpha": 0.7,
        "edgecolor": "black",
        "linewidth": 0.5,
    },
    
    "confusion_matrix": {
        "cmap": "Blues",
        "annot_fontsize": 14,
        "fmt": "d",
    },
    
    "annotations": {
        "fontsize": 12,
        "bbox_style": "round,pad=0.5",
        "bbox_facecolor": "white",
        "bbox_alpha": 0.8,
    },
    
    "filenames": {
        "accuracy_bar": "accuracy_comparison.png",
        "confusion_matrix": "confusion_matrix.png",
        "distribution": "prediction_distribution.png",
        "error_analysis": "error_analysis_scatter.png",
    },
}
```

---

## Statistical Test Parameters

```python
STAT_CONFIG = {
    "binomial_test": {
        "n_total": 30,
        "null_p": 0.50,
        "alternative": "greater",
    },
    
    "accuracy_reference": {
        "random_baseline": 0.50,
        "expert_intuition": 0.65,  # Optional reference from h-e1
        "target": 0.80,
    },
}
```

---

## Usage Example

```python
# Load config
from config import DATA_CONFIG, MODEL_CONFIG, EVAL_CONFIG, VIZ_CONFIG

# Load data
import pandas as pd
corpus_df = pd.read_csv(DATA_CONFIG["corpus_path"])

# Load scaling factor k from h-m1
import re
with open(MODEL_CONFIG["k_source"]) as f:
    validation_text = f.read()
    k_match = re.search(r"k = ([0-9.]+)", validation_text)
    k = float(k_match.group(1))

# Initialize classifier
class Gate1ViabilityClassifier:
    def __init__(self, k, threshold):
        self.k = k
        self.threshold = threshold
    
    def predict(self, O_10):
        O_pred = O_10 * self.k
        return "non-viable" if O_pred > self.threshold else "viable"

classifier = Gate1ViabilityClassifier(k=k, threshold=MODEL_CONFIG["threshold"])

# Evaluate
from sklearn.metrics import accuracy_score, confusion_matrix
from scipy.stats import binom_test

predictions = [classifier.predict(o) for o in corpus_df["O_10"]]
actuals = ["non-viable" if o > MODEL_CONFIG["threshold"] else "viable" 
           for o in corpus_df["O_full"]]

accuracy = accuracy_score(actuals, predictions)
n_correct = int(accuracy * len(actuals))
p_value = binom_test(n_correct, len(actuals), 
                     p=EVAL_CONFIG["null_hypothesis_p"], 
                     alternative="greater")

# Visualize
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize"], dpi=VIZ_CONFIG["dpi"])
plt.savefig(f"{VIZ_CONFIG['output_dir']}/{VIZ_CONFIG['filenames']['accuracy_bar']}", 
            format=VIZ_CONFIG["format"], dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
```

---

**Total Lines:** 186
