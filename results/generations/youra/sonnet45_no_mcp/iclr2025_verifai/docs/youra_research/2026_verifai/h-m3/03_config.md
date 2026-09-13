# Configuration Design: h-m3

**Date:** 2026-04-20  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Hybrid Signal Combination)  
**Config Designer:** Configuration Agent  
**Budget:** 4 subtasks  
**Base Hypothesis:** h-m2 (COMPLETED, PASSED)

Applied: Configuration inheritance pattern - reuse h-m2 settings with symbolic signal and ablation extensions

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** h-m2 config verified from actual code  
**Config Files Found:** h-m2/code/config.py  
**Pattern Used:** Hardcoded dict (EXPERIMENT_CONFIG)

---

## Inherited Configuration (Base Hypothesis)

### Config Schema (From Actual h-m2 Code)

Verified from: `/h-m2/code/config.py`

```python
# From h-m2/code/config.py (ACTUAL CODE - VERIFIED)
EXPERIMENT_CONFIG = {
    # Dataset
    "repo_url": "https://github.com/leanprover-community/mathlib",
    "commit_hash": "d88406ff7d5d41304c2f94222ac7852ecb4c38f2",
    "sample_size": 100,
    "random_seed": 42,
    
    # Experiment execution
    "timeout_seconds": 300,
    "confidence_window": 15,
    
    # Gate condition
    "gate_type": "variance_comparison",
    "significance_level": 0.05,
    
    # Output paths
    "results_dir": "./results",
    "figures_dir": "./figures",
    
    # Logging
    "log_level": "INFO",
    "progress_interval": 10,
}

VISUALIZATION_CONFIG = {
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    "figsize": (10, 6),
    "colors": {
        "success": "#2ecc71",
        "timeout": "#e74c3c",
        "target": "#3498db",
    },
}
```

**Reuse Level:** 100% - All experimental settings inherited

---

## H-M3 Specific Configuration

### E1: Environment Setup [Complexity: 5, Budget: 5/30]

**Applied:** Standard PyTorch environment setup

```python
# h-m3/code/config.py

# INHERITED: All h-m2 experiment settings
from pathlib import Path

# Base hypothesis path configuration
H_M2_PATH = Path(__file__).parent.parent.parent / "h-m2" / "code"

ENVIRONMENT_CONFIG = {
    "h_m2_code_path": str(H_M2_PATH),
    "python_path_prepend": True,
    "output_base_dir": "h-m3",
}
```

**Subtasks:** [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E1-1 | Create directory structure | signals/, detectors/, evaluation/, visualization/ |
| E1-2 | Configure h-m2 imports | Add h-m2/code to sys.path |
| E1-3 | Verify dependencies | sklearn, scipy, numpy |
| E1-4 | Create output directories | results/, figures/ |
| E1-5 | Environment validation | Test h-m2 module imports |

---

### E2: Implement Symbolic Signal Extraction [Complexity: 12, Budget: 12/30]

**Applied:** Signal extraction pattern - default thresholds from research

```python
SYMBOLIC_SIGNAL_CONFIG = {
    # State collision detection
    "state_hash_method": "frozenset",  # hash(frozenset(state.pp.items()))
    "collision_threshold": 2,  # Min collisions for divergence alert
    
    # Exponential growth detection
    "growth_window": 10,  # Window size for trend fitting
    "growth_threshold": 0.5,  # Min exponential rate for alert
    "growth_method": "log_linear_regression",
    
    # Edge case handling
    "min_states_for_growth": 5,  # Min states to fit exponential
    "fallback_on_fit_failure": True,  # Use state size variance if fit fails
}
```

**Subtasks:** [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E2-1 | Implement collision counting | Use SearchTree.get_collision_count() |
| E2-2 | Implement exponential fitting | numpy polyfit on log-transformed sizes |
| E2-3 | Extract proof state sizes | Parse LeanDojo state.goals |
| E2-4 | Handle edge cases | Empty states, single state, fit failures |
| E2-5 | Integration test | Test on h-m2 results |

---

### E3: Implement Hybrid Termination Detector [Complexity: 14, Budget: 14/30]

**Applied:** Voting-based ensemble pattern - k-of-n threshold

```python
HYBRID_DETECTOR_CONFIG = {
    # Voting configuration
    "voting_k": 2,  # At least 2 of 3 signals must trigger
    "voting_n": 3,  # Total number of signals
    
    # Signal thresholds (data-driven from timeout group)
    "thresholds": {
        "variance": 0.25,  # From h-m1 (median of timeout group)
        "collisions": 2,  # To be selected from h-m3 timeout data
        "growth": 0.5,  # To be selected from h-m3 timeout data
        "backtrack": 0.3,  # To be selected from h-m2 timeout data
    },
    
    # Individual alert logic
    "confidence_alert": "variance > threshold",
    "symbolic_alert": "collisions > threshold OR growth > threshold",
    "search_alert": "backtrack_freq > threshold",
}
```

**Subtasks:** [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E3-1 | Implement signal extraction | Extract all 3 signal types |
| E3-2 | Implement voting logic | k-of-3 threshold voting |
| E3-3 | Implement confidence checker | Variance > threshold |
| E3-4 | Implement symbolic checker | Collisions OR growth > threshold |
| E3-5 | Implement search checker | Backtrack frequency > threshold |
| E3-6 | Calculate backtrack frequency | From SearchTree |
| E3-7 | Integration testing | Test voting with mock signals |

---

### E4: Implement Threshold Selection [Complexity: 8, Budget: 8/30]

**Applied:** Data-driven threshold selection - median strategy

```python
THRESHOLD_SELECTION_CONFIG = {
    # Selection strategy
    "strategy": "median",  # Median of timeout group
    "fallback_strategy": "h_m1_reference",  # Use h-m1 values if timeout group small
    
    # Reference thresholds (from h-m1)
    "reference_thresholds": {
        "variance": 0.25,  # Validated in h-m1
    },
    
    # Validation
    "min_timeout_samples": 5,  # Min samples required for threshold selection
    "validate_against_success_group": True,  # Ensure threshold separates groups
}
```

**Subtasks:** [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E4-1 | Implement median calculation | Per signal type |
| E4-2 | Load h-m1 reference | Variance threshold 0.25 |
| E4-3 | Handle edge cases | Empty timeout group fallback |
| E4-4 | Validate thresholds | Test on h-m2 results |
| E4-5 | Document values | Save to results/thresholds.txt |

---

### E5: Implement Ablation Framework [Complexity: 16, Budget: 16/30]

**Applied:** Ablation study pattern - systematic model comparison

```python
ABLATION_CONFIG = {
    # Model variants (7 total)
    "models": {
        "confidence_only": {"signals": ["variance"]},
        "symbolic_only": {"signals": ["collisions", "growth"]},
        "search_only": {"signals": ["backtrack"]},
        "conf_symb": {"signals": ["variance", "collisions", "growth"], "voting_k": 1},
        "conf_search": {"signals": ["variance", "backtrack"], "voting_k": 1},
        "symb_search": {"signals": ["collisions", "growth", "backtrack"], "voting_k": 1},
        "hybrid_all": {"signals": ["variance", "collisions", "growth", "backtrack"], "voting_k": 2},
    },
    
    # Evaluation metrics
    "metrics": ["precision", "recall", "f1", "accuracy"],
    "correlation_metrics": ["pearson_r", "spearman_rho"],
    
    # Gate condition
    "gate_type": "hybrid_outperforms_all_single",
    "gate_metric": "f1",
}
```

**Subtasks:** [16/16 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E5-1 | Create model factory | Generate 7 detector variants |
| E5-2 | Implement confidence-only | Variance threshold |
| E5-3 | Implement symbolic-only | Collisions OR growth |
| E5-4 | Implement search-only | Backtrack frequency |
| E5-5 | Implement conf+symb | OR combination |
| E5-6 | Implement conf+search | OR combination |
| E5-7 | Implement symb+search | OR combination |
| E5-8 | Implement hybrid all | k=2 voting |
| E5-9 | Implement evaluation loop | Run all on dataset |
| E5-10 | Compute metrics | Precision, recall, F1 |
| E5-11 | Test each variant | Individual validation |

---

### E6: Implement Ablation Visualization [Complexity: 13, Budget: 13/30]

**Applied:** Research visualization pattern - publication-ready plots

```python
VISUALIZATION_CONFIG = {
    # Mandatory plot (GATE requirement)
    "ablation_comparison_bar": {
        "enabled": True,  # MANDATORY
        "metric": "f1",
        "title": "Ablation Study: F1 Scores Across 7 Models",
        "xlabel": "Model Variant",
        "ylabel": "F1 Score",
        "figsize": (12, 6),
        "bar_colors": ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22"],
        "show_values": True,
    },
    
    # Additional plots
    "signal_distributions": {
        "enabled": True,
        "plot_type": "boxplot",
        "title": "Signal Distributions by Outcome",
        "figsize": (14, 6),
    },
    
    "correlation_scatter": {
        "enabled": True,
        "n_subplots": 4,  # One per signal
        "figsize": (12, 10),
    },
    
    "voting_analysis": {
        "enabled": True,
        "plot_type": "bar",
        "title": "Voting Pattern Analysis",
        "figsize": (10, 6),
    },
    
    "confusion_matrices": {
        "enabled": True,
        "grid_layout": (2, 4),  # 7 models + 1 empty
        "figsize": (16, 8),
    },
    
    # Output settings
    "output_dir": "h-m3/figures",
    "dpi": 300,
    "format": "png",
}
```

**Subtasks:** [13/13 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E6-1 | Implement ablation bar chart | F1 comparison (MANDATORY) |
| E6-2 | Implement signal distributions | Box plots by outcome |
| E6-3 | Implement correlation scatter | 4 subplots per signal |
| E6-4 | Implement voting analysis | Voting pattern bars |
| E6-5 | Implement confusion matrices | Grid of 7 models |

---

### E7: Main Experiment Script [Complexity: 15, Budget: 15/30]

**Applied:** Experiment orchestration pattern - modular pipeline

```python
EXPERIMENT_CONFIG = {
    # Data sources
    "h_m1_results_path": "../h-m1/results/experiment_results.pkl",
    "h_m2_results_path": "../h-m2/results/experiment_results.pkl",
    "reuse_h_m2_results": True,  # Efficiency: reuse tree tracking
    
    # Experiment execution
    "sample_size": 100,  # Same as h-m1, h-m2
    "random_seed": 42,  # Same as h-m1, h-m2
    "timeout_seconds": 300,  # Same as h-m1, h-m2
    
    # Pipeline stages
    "stages": {
        "load_data": True,
        "extract_signals": True,
        "select_thresholds": True,
        "run_ablation": True,
        "compute_metrics": True,
        "generate_visualizations": True,
        "evaluate_gate": True,
    },
    
    # Output
    "results_dir": "h-m3/results",
    "figures_dir": "h-m3/figures",
    "results_file": "h_m3_results.json",
    "signals_file": "signals_data.csv",
    "thresholds_file": "thresholds.txt",
    
    # Gate evaluation
    "gate_condition": "hybrid_f1 > all_single_f1s",
    "gate_type": "SHOULD_WORK",
}
```

**Subtasks:** [15/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E7-1 | Load h-m1 results | Ground truth labels |
| E7-2 | Load/run tree tracking | Reuse h-m2 or re-run |
| E7-3 | Extract all signals | 3 signal types per theorem |
| E7-4 | Select thresholds | Median from timeout group |
| E7-5 | Run ablation | 7 models on 100 theorems |
| E7-6 | Compute metrics | F1, precision, recall, correlation |
| E7-7 | Generate visualizations | All 5 plot types |
| E7-8 | Save results | JSON output |
| E7-9 | Evaluate gate | Hybrid vs single models |

---

### E8: Results Interpretation [Complexity: 6, Budget: 6/30]

**Applied:** Research documentation pattern - reproducible results

```python
DOCUMENTATION_CONFIG = {
    "readme_sections": [
        "experiment_overview",
        "threshold_selection_strategy",
        "ablation_design_rationale",
        "result_interpretation_guide",
        "signal_combination_rationale",
        "usage_instructions",
    ],
    
    "include_examples": True,
    "include_troubleshooting": True,
    "include_gate_interpretation": True,
}
```

**Subtasks:** [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| E8-1 | Create README template | Document structure |
| E8-2 | Document thresholds | Selection strategy |
| E8-3 | Explain ablation design | 7-model rationale |
| E8-4 | Result interpretation | Gate pass/fail guide |
| E8-5 | Signal combination rationale | Why 3 signals |
| E8-6 | Usage instructions | How to run experiment |

---

## Complete Configuration (h-m3/code/config.py)

```python
# Configuration for h-m3 Experiment
# Date: 2026-04-20
# Hypothesis: MECHANISM - Hybrid Signal Combination
# Base: h-m2 (COMPLETED, PASSED)

from pathlib import Path

# Base hypothesis path
H_M2_PATH = Path(__file__).parent.parent.parent / "h-m2" / "code"

# INHERITED from h-m2 (100% reuse)
EXPERIMENT_CONFIG = {
    # Dataset (inherited)
    "repo_url": "https://github.com/leanprover-community/mathlib",
    "commit_hash": "d88406ff7d5d41304c2f94222ac7852ecb4c38f2",
    "sample_size": 100,
    "random_seed": 42,
    
    # Execution (inherited)
    "timeout_seconds": 300,
    "confidence_window": 15,
    
    # H-M3 specific: data sources
    "h_m1_results_path": "../h-m1/results/experiment_results.pkl",
    "h_m2_results_path": "../h-m2/results/experiment_results.pkl",
    "reuse_h_m2_results": True,
    
    # Output paths (h-m3)
    "results_dir": "./h-m3/results",
    "figures_dir": "./h-m3/figures",
    "results_file": "h_m3_results.json",
    "signals_file": "signals_data.csv",
    "thresholds_file": "thresholds.txt",
    
    # Logging
    "log_level": "INFO",
    "progress_interval": 10,
}

# H-M3 NEW: Symbolic signal extraction
SYMBOLIC_SIGNAL_CONFIG = {
    "state_hash_method": "frozenset",
    "collision_threshold": 2,
    "growth_window": 10,
    "growth_threshold": 0.5,
    "growth_method": "log_linear_regression",
    "min_states_for_growth": 5,
    "fallback_on_fit_failure": True,
}

# H-M3 NEW: Hybrid detector voting
HYBRID_DETECTOR_CONFIG = {
    "voting_k": 2,
    "voting_n": 3,
    "thresholds": {
        "variance": 0.25,  # From h-m1
        "collisions": 2,  # To be selected from data
        "growth": 0.5,  # To be selected from data
        "backtrack": 0.3,  # To be selected from data
    },
    "confidence_alert": "variance > threshold",
    "symbolic_alert": "collisions > threshold OR growth > threshold",
    "search_alert": "backtrack_freq > threshold",
}

# H-M3 NEW: Threshold selection
THRESHOLD_SELECTION_CONFIG = {
    "strategy": "median",
    "fallback_strategy": "h_m1_reference",
    "reference_thresholds": {
        "variance": 0.25,
    },
    "min_timeout_samples": 5,
    "validate_against_success_group": True,
}

# H-M3 NEW: Ablation framework
ABLATION_CONFIG = {
    "models": {
        "confidence_only": {"signals": ["variance"]},
        "symbolic_only": {"signals": ["collisions", "growth"]},
        "search_only": {"signals": ["backtrack"]},
        "conf_symb": {"signals": ["variance", "collisions", "growth"], "voting_k": 1},
        "conf_search": {"signals": ["variance", "backtrack"], "voting_k": 1},
        "symb_search": {"signals": ["collisions", "growth", "backtrack"], "voting_k": 1},
        "hybrid_all": {"signals": ["variance", "collisions", "growth", "backtrack"], "voting_k": 2},
    },
    "metrics": ["precision", "recall", "f1", "accuracy"],
    "correlation_metrics": ["pearson_r", "spearman_rho"],
    "gate_type": "hybrid_outperforms_all_single",
    "gate_metric": "f1",
}

# H-M3 NEW: Visualization
VISUALIZATION_CONFIG = {
    "ablation_comparison_bar": {
        "enabled": True,  # MANDATORY
        "metric": "f1",
        "title": "Ablation Study: F1 Scores Across 7 Models",
        "xlabel": "Model Variant",
        "ylabel": "F1 Score",
        "figsize": (12, 6),
        "bar_colors": ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22"],
        "show_values": True,
    },
    "signal_distributions": {
        "enabled": True,
        "plot_type": "boxplot",
        "title": "Signal Distributions by Outcome",
        "figsize": (14, 6),
    },
    "correlation_scatter": {
        "enabled": True,
        "n_subplots": 4,
        "figsize": (12, 10),
    },
    "voting_analysis": {
        "enabled": True,
        "plot_type": "bar",
        "title": "Voting Pattern Analysis",
        "figsize": (10, 6),
    },
    "confusion_matrices": {
        "enabled": True,
        "grid_layout": (2, 4),
        "figsize": (16, 8),
    },
    "output_dir": "./h-m3/figures",
    "dpi": 300,
    "format": "png",
}

# Environment setup
ENVIRONMENT_CONFIG = {
    "h_m2_code_path": str(H_M2_PATH),
    "python_path_prepend": True,
    "output_base_dir": "h-m3",
}
```

---

## Task Summary

| Epic ID | Name | Complexity | Budget Used | Status |
|---------|------|------------|-------------|--------|
| E1 | Environment Setup | 5 | 5/5 | Configured |
| E2 | Symbolic Signal Extraction | 12 | 12/12 | Configured |
| E3 | Hybrid Termination Detector | 14 | 14/14 | Configured |
| E4 | Threshold Selection | 8 | 8/8 | Configured |
| E5 | Ablation Framework | 16 | 16/16 | Configured |
| E6 | Ablation Visualization | 13 | 13/13 | Configured |
| E7 | Main Experiment Script | 15 | 15/15 | Configured |
| E8 | Results Interpretation | 6 | 6/6 | Configured |

**Total Budget:** 89/89 used (100% allocated)

---

## Configuration Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] Codebase Analysis section included
- [x] Field names verified from actual h-m2 code
- [x] Default values match base config
- [x] Inherited Configuration section included
- [x] Subtask count within budget (89/89)
- [x] Total length < 400 lines
- [x] Applied: patterns noted (1 line each)
- [x] Rationale only for non-standard values

---

## Notes

**Configuration Philosophy:** Maximize h-m2 reuse (100% experiment settings). Add only h-m3-specific configs for symbolic signals, voting logic, and ablation framework.

**Threshold Strategy:** Use median of timeout group (data-driven, no hyperparameter search). PoC-level approach - future work can optimize.

**Ablation Design:** 7 models (3 single + 3 pairwise + 1 hybrid) enable systematic evaluation of signal combination hypothesis.

**Gate Condition:** Strict test - hybrid must outperform ALL single-signal models (F1 metric).
