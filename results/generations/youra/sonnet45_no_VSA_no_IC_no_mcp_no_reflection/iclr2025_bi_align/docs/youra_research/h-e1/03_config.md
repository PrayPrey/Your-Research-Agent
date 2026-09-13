# Configuration: H-E1
# Preference Entropy Measurement (EXISTENCE PoC)

**Date:** 2026-08-28  
**Author:** yoon303@etri.re.kr  
**Hypothesis:** Base models produce outputs with preference entropy H_base >= 1.8 nats  
**Type:** EXISTENCE (PoC)  
**Gate:** MUST_WORK

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict

---

## Knowledge Base Patterns Applied

Applied: Minimal EXISTENCE config (hardcoded constants, no hyperparameter tuning)

---

## E1: Dataset Setup (Complexity: 6, Budget: 6)

Applied: Standard HuggingFace datasets defaults

### Configuration (Hardcoded Dict)

```python
DATASET_CONFIG = {
    "dataset_name": "Anthropic/hh-rlhf",
    "split": "train",
    "sample_size": 100,
    "random_seed": 1,
    "cache_dir": None  # Uses HF default ~/.cache/huggingface/datasets
}
```

### Subtasks (4/6 used)

| ID | Subtask | Description |
|----|---------|-------------|
| E1-1 | Install datasets lib | Add datasets>=2.0.0 to requirements.txt |
| E1-2 | Implement load_dataset() | Load Anthropic-HH using HF datasets |
| E1-3 | Implement sample_prompts() | Sample 100 prompts with seed=1 |
| E1-4 | Verify sampling | Assert exactly 100 prompts returned |

---

## E2: Entropy Computation (Complexity: 8, Budget: 8)

Applied: scipy.stats.entropy with natural log base (standard Shannon entropy)

### Configuration (Hardcoded Dict)

```python
ENTROPY_CONFIG = {
    "min_comparisons": 5,  # Filter prompts with <5 examples
    "entropy_base": "e",   # Natural log for nats (np.e)
    "max_entropy_nats": 0.693,  # ln(2) for binary choices
    "min_entropy_nats": 0.0
}
```

### Subtasks (4/8 used)

| ID | Subtask | Description |
|----|---------|-------------|
| E2-1 | Implement aggregate_preferences() | Group comparisons by prompt, count chosen/rejected |
| E2-2 | Implement compute_entropy() | Use scipy.stats.entropy with base=np.e |
| E2-3 | Handle edge cases | Return None for <5 comparisons, filter zero probs |
| E2-4 | Implement analyze_dataset() | Main loop over sampled prompts |

---

## E3: Metrics & Validation (Complexity: 5, Budget: 5)

Applied: Standard statistical metrics (success rate, variance, range)

### Configuration (Hardcoded Dict)

```python
VALIDATION_CONFIG = {
    "min_success_rate": 0.95,  # Gate threshold: 95%
    "min_variance": 0.0,       # Variance > 0 (not constant)
    "expected_mean_entropy": 0.4  # Expected mean > 0.4 nats
}
```

### Subtasks (3/5 used)

| ID | Subtask | Description |
|----|---------|-------------|
| E3-1 | Implement compute_metrics() | Calculate success rate, variance, range, mean |
| E3-2 | Add validation checks | Assert range [0, 0.693], variance > 0 |
| E3-3 | Calculate mean entropy | np.mean(entropy_values) |

---

## E4: Visualization & Output (Complexity: 7, Budget: 7)

Applied: matplotlib defaults with minimal styling

### Configuration (Hardcoded Dict)

```python
OUTPUT_CONFIG = {
    "output_dir": "h-e1",
    "results_file": "h-e1_results.json",
    "figures_dir": "figures",
    "figure_dpi": 100,
    "figure_format": "png",
    "histogram_bins": 20
}

FIGURE_TITLES = {
    "gate_metrics": "H-E1 Gate Metrics: Target vs Actual",
    "histogram": "Entropy Distribution (n=100 prompts)",
    "scatter": "Entropy vs Prompt Index",
    "pie": "Computation Success Rate"
}
```

### Subtasks (6/7 used)

| ID | Subtask | Description |
|----|---------|-------------|
| E4-1 | Gate metrics bar chart | Target vs actual for success_rate, variance, range |
| E4-2 | Entropy histogram | 20 bins, x=nats, y=frequency |
| E4-3 | Entropy scatter plot | x=prompt index, y=entropy |
| E4-4 | Success pie chart | Computed vs failed |
| E4-5 | Implement save_results() | Save to JSON with metadata |
| E4-6 | Create figures/ directory | os.makedirs if not exists |

---

## Dependencies Configuration

```python
# requirements.txt
DEPENDENCIES = {
    "scipy": ">=1.7.0",
    "numpy": ">=1.21.0",
    "datasets": ">=2.0.0",
    "matplotlib": ">=3.5.0"
}
```

---

## Gate Validation Thresholds

```python
GATE_THRESHOLDS = {
    "success_rate": 0.95,        # >=95% prompts with valid entropy
    "min_variance": 0.0,         # Variance > 0
    "entropy_min": 0.0,          # All values in [0, ln(2)]
    "entropy_max": 0.693147      # ln(2) = 0.693147 nats
}
```

---

## Complete Config Module (Copy-Paste Ready)

```python
"""Configuration for H-E1 Preference Entropy Measurement."""

import numpy as np

# Dataset configuration
DATASET_CONFIG = {
    "dataset_name": "Anthropic/hh-rlhf",
    "split": "train",
    "sample_size": 100,
    "random_seed": 1,
    "cache_dir": None
}

# Entropy computation configuration
ENTROPY_CONFIG = {
    "min_comparisons": 5,
    "entropy_base": np.e,
    "max_entropy_nats": np.log(2),  # 0.693147
    "min_entropy_nats": 0.0
}

# Validation thresholds
VALIDATION_CONFIG = {
    "min_success_rate": 0.95,
    "min_variance": 0.0,
    "expected_mean_entropy": 0.4
}

# Output configuration
OUTPUT_CONFIG = {
    "output_dir": "h-e1",
    "results_file": "h-e1_results.json",
    "figures_dir": "figures",
    "figure_dpi": 100,
    "figure_format": "png",
    "histogram_bins": 20
}

# Figure titles
FIGURE_TITLES = {
    "gate_metrics": "H-E1 Gate Metrics: Target vs Actual",
    "histogram": "Entropy Distribution (n=100 prompts)",
    "scatter": "Entropy vs Prompt Index",
    "pie": "Computation Success Rate"
}

# Gate thresholds (MUST_WORK conditions)
GATE_THRESHOLDS = {
    "success_rate": 0.95,
    "min_variance": 0.0,
    "entropy_min": 0.0,
    "entropy_max": 0.693147
}
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict - no dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale omitted (all standard values)
- [x] Subtask counts within budgets (E1:4/6, E2:4/8, E3:3/5, E4:6/7)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project noted
- [x] EXISTENCE PoC: single fixed config, no hyperparameter variations
- [x] Ready-to-copy-paste config module included

---

*Config designed for EXISTENCE PoC - minimal settings to test "does it work?"*  
*Next Phase: Phase 4 - Implementation (Coder)*
