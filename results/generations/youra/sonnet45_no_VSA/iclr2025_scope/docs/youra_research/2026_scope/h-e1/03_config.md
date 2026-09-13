# Configuration Schemas: h-e1
# API Contract Validation Framework

**Date:** 2026-07-11  
**Hypothesis:** h-e1 (EXISTENCE)  
**Type:** PoC - Research Tool Validation  
**Total Subtask Budget:** 3 (E-6: 2, E-4: 1)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Foundation hypothesis - new configuration design  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict (PoC simplicity)

---

## Knowledge Base Patterns Applied

**Applied:** Research experiment configuration pattern (minimal hardcoded defaults for PoC validation)

---

## E-4: Retrospective Coding [Complexity: 10, Budget: 1 subtask]

**Applied:** Standard research protocol defaults from scikit-learn and scipy

### Configuration (Hardcoded Dict)

```python
RETROSPECTIVE_CODING_CONFIG = {
    # Reproducibility
    "random_seed": 42,
    
    # 2-Coder Protocol
    "num_coders": 2,
    "kappa_threshold": 0.7,
    
    # 3-Question Filter
    "questions": [
        "documented_invariant_exists",
        "evaluable_within_timeout",
        "version_stable"
    ],
    
    # Timeout Enforcement
    "validation_timeout": 10,  # seconds
    
    # Version Stability Range
    "pytorch_versions": ["1.11", "1.12", "1.13"],
    
    # Confidence Interval
    "confidence_level": 0.95,
    "ci_method": "wilson"  # Wilson score method via scipy.stats.proportion_confint
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Implement 2-coder protocol with kappa calculation | Load defects with random_seed=42, apply 3Q filter, compute Cohen's kappa using sklearn.metrics |

---

## E-6: Visualization [Complexity: 11, Budget: 2 subtasks]

**Applied:** Matplotlib research publication defaults

### Configuration (Hardcoded Dict)

```python
VISUALIZATION_CONFIG = {
    # Output Settings
    "output_dir": "figures",
    "format": "png",
    "dpi": 300,
    
    # Figure Sizing (Publication-Ready)
    "figure_sizes": {
        "gate_metrics": (10, 6),
        "defect_distribution": (8, 8),
        "execution_time": (10, 6),
        "version_stability": (10, 6),
        "kappa_heatmap": (6, 6)
    },
    
    # Color Scheme
    "colors": {
        "pass_threshold": "#2ecc71",  # Green
        "fail_threshold": "#e74c3c",  # Red
        "structural": "#3498db",       # Blue
        "metamorphic": "#f39c12",      # Orange
        "composition": "#9b59b6",      # Purple
        "overall": "#34495e"            # Dark gray
    },
    
    # Gate Metrics (Mandatory Figure)
    "gate_threshold": 0.40,  # 40% contractability threshold
    "show_ci_bars": True,
    "threshold_line_style": "--",
    "threshold_line_color": "#e74c3c",
    
    # Font Sizes
    "font_sizes": {
        "title": 14,
        "axis_label": 12,
        "tick_label": 10,
        "legend": 10
    },
    
    # Figure Filenames
    "filenames": {
        "gate_metrics": "gate_metrics_comparison.png",
        "defect_distribution": "defect_distribution.png",
        "execution_time": "execution_time_histogram.png",
        "version_stability": "version_stability.png",
        "kappa_heatmap": "kappa_heatmap.png"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Implement mandatory gate metrics chart | Bar chart with 40% threshold line, 95% CI error bars, saved as PNG |
| C-6-2 | Implement optional visualizations | 4 additional figures (defect distribution pie, execution histogram, version stability line, kappa heatmap) |

---

## Shared Global Configuration

```python
GLOBAL_CONFIG = {
    # Defect Corpus
    "corpus_url": "https://github.com/wenxin-jiang/emse-cvreengineering-artifact",
    "defect_types": ["structural", "metamorphic", "composition"],
    
    # Gate Evaluation
    "gate_conditions": {
        "min_contractability_rate": 0.40,
        "min_kappa": 0.7,
        "max_execution_time": 10  # seconds
    },
    
    # Baseline Comparisons
    "baselines": {
        "no_ci": 0.0,
        "ci_only": 0.175  # 15-20% from Wolter et al. 2025
    }
}
```

---

## Usage Example

```python
# In run_experiment.py
from config import RETROSPECTIVE_CODING_CONFIG, VISUALIZATION_CONFIG, GLOBAL_CONFIG

# Retrospective Coding
coder = RetrospectiveCoder(
    defects=defects,
    random_seed=RETROSPECTIVE_CODING_CONFIG["random_seed"]
)
kappa = coder.calculate_kappa(coder1_labels, coder2_labels)
assert kappa >= RETROSPECTIVE_CODING_CONFIG["kappa_threshold"], "Kappa too low"

# Visualization
viz = Visualizer(output_dir=VISUALIZATION_CONFIG["output_dir"])
viz.plot_gate_metrics(
    metrics=metrics,
    threshold=VISUALIZATION_CONFIG["gate_threshold"],
    figsize=VISUALIZATION_CONFIG["figure_sizes"]["gate_metrics"],
    colors=VISUALIZATION_CONFIG["colors"]
)

# Gate Evaluation
gate_pass = (
    metrics.overall_rate >= GLOBAL_CONFIG["gate_conditions"]["min_contractability_rate"]
    and metrics.kappa >= GLOBAL_CONFIG["gate_conditions"]["min_kappa"]
)
print(f"Gate Status: {'PASS' if gate_pass else 'FAIL'}")
```

---

## Rationale for Non-Standard Values

**pytorch_versions: ["1.11", "1.12", "1.13"]**
- Chosen to test ±2 minor releases as per FR-7 version stability requirement
- Covers representative range from late 2021 to mid-2022 PyTorch evolution

**ci_method: "wilson"**
- Wilson score method provides accurate confidence intervals for proportions
- More robust than normal approximation for moderate sample sizes (348 defects)

**baselines.ci_only: 0.175**
- Midpoint of 15-20% range from Wolter et al. 2025 literature
- Represents typical integration test coverage in ML repositories

---

## Self-Validation Checks

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (3/3 used)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project status documented

---

**End of Configuration Document**

*Ready for Phase 4 - Code generation using these config schemas*
