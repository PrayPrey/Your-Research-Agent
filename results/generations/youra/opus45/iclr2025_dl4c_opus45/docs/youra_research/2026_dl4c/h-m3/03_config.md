# Config: H-M3 - LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis

**Hypothesis:** DPO preference optimization concentrates failures in execution errors at fine-grained LlmFix 19-cause level (Cramér's V > 0.03)
**Type:** MECHANISM | **Gate:** SHOULD_WORK

Applied: dataclass-with-os-path-resolution (from h-m2 pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 + h-m2)
**Status**: Config classes verified from actual code
**Config Files Found**: `h-e1/code/config.py` (ExperimentConfig), `h-m2/code/config.py` (HM2Config)
**Pattern Used**: dataclass with os.path absolute path resolution (h-m2 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
@dataclass
class ExperimentConfig:
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    chi2_p_threshold: float = 0.05
    cramers_v_threshold: float = 0.05
    seed: int = 42

# From: h-m2/code/config.py (ACTUAL CODE - verified)
@dataclass
class HM2Config:
    # Uses os.path.join(__file__) pattern for absolute paths
    # __post_init__ normalizes all paths to absolute
    h_e1_experiment_results_path: str = ...  # ../h-e1/code/outputs/experiment_results.json
    h_e1_metrics_path: str = ...             # ../h-e1/code/outputs/metrics.json
    output_dir: str = ...                    # absolute via os.path
    figures_dir: str = ...                   # absolute via os.path
    t_test_p_threshold: float = 0.05
    random_seed: int = 42
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530
```

**Verified from**: `docs/youra_research/20260323_dl4c/h-e1/code/config.py` and `h-m2/code/config.py`

---

## A-1: Environment & Config [Complexity: 6, Budget: 4 subtasks]

**Applied**: Standard dataclass pattern with os.path absolute resolution (from h-m2 verified code)

### Configuration (Python Dataclass)

```python
"""Configuration for H-M3: LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis."""

from dataclasses import dataclass
import os


@dataclass
class ExperimentConfig:
    """Single fixed configuration for H-M3 MECHANISM hypothesis.

    H-M3 tests whether DPO failure concentration in execution errors
    persists at fine-grained LlmFix 19-cause taxonomy level (Cramér's V > 0.03).
    No GPU required - analysis is pure string parsing + statistics.
    """

    # H-E1 data paths (relative to h-m3/code/, resolved to absolute in __post_init__)
    he1_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "experiment_results.json"
    )
    he1_metrics_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "metrics.json"
    )

    # Output paths
    output_dir: str = os.path.join(os.path.dirname(__file__), "outputs")
    figures_dir: str = os.path.join(os.path.dirname(__file__), "figures")

    # Statistical thresholds (H-M3 SHOULD_WORK gate criteria)
    chi2_p_threshold: float = 0.05
    cramers_v_threshold_fine: float = 0.03    # Non-standard: fine-grained gate (lower than coarse)
    cramers_v_threshold_coarse: float = 0.05  # Coarse validation vs H-E1 (V~0.21 expected)

    # Pseudocount for sparse contingency cells (Laplace smoothing, standard 0.5)
    pseudocount: float = 0.5

    # Expected failure counts from H-E1 (for data integrity validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    # Reproducibility
    seed: int = 42

    def __post_init__(self):
        """Normalize all paths to absolute."""
        self.he1_results_path = os.path.abspath(self.he1_results_path)
        self.he1_metrics_path = os.path.abspath(self.he1_metrics_path)
        self.output_dir = os.path.abspath(self.output_dir)
        self.figures_dir = os.path.abspath(self.figures_dir)


CONFIG = ExperimentConfig()
```

### LlmFix Taxonomy Constants

```python
# From: LlmFix paper arXiv:2409.00676 - 19-cause taxonomy
# Used in: code/classifier.py

from typing import Dict, List

LLMFIX_TAXONOMY: Dict[str, List[str]] = {
    "syntax": [
        "indentation_error",
        "syntax_error",
        "missing_import",
    ],
    "runtime": [
        "name_error",
        "type_error",
        "attribute_error",
        "index_error",
        "key_error",
        "value_error",
        "zero_division",
        "recursion_error",
        "timeout",
        "memory_error",
    ],
    "assertion": [
        "wrong_output",
        "partial_output",
        "missing_output",
        "wrong_type",
        "off_by_one",
        "boundary_error",
    ],
}

# Flat list of all 19 fine-grained causes (ordering: syntax → runtime → assertion)
ALL_FINE_CAUSES: List[str] = [
    cause for causes in LLMFIX_TAXONOMY.values() for cause in causes
]
# len(ALL_FINE_CAUSES) == 19

# Coarse category ordering (matches contingency table columns)
COARSE_CATEGORIES: List[str] = ["syntax", "runtime", "assertion"]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Create project structure | Create h-m3/code/ dirs: outputs/, figures/ |
| C-1-2 | Write config.py | ExperimentConfig dataclass + LLMFIX_TAXONOMY constants |
| C-1-3 | Verify H-E1 paths | Assert he1_results_path and he1_metrics_path exist at runtime |
| C-1-4 | Write requirements.txt | scipy, numpy, matplotlib, seaborn, pandas |

---

## Notes on Non-Standard Values

- `cramers_v_threshold_fine: float = 0.03` — Fine-grained gate is 0.03 (not standard 0.05) because effect size dilutes at 19-cause level vs 3-tier; 0.03 is the H-M3 SHOULD_WORK gate criterion from Phase 2C
- `pseudocount: float = 0.5` — Laplace-style smoothing for 2x19 sparse contingency table; 0.5 is standard half-count pseudocount
- `cramers_v_threshold_coarse: float = 0.05` — Separate threshold for coarse validation (H-E1 yielded V=0.2147, so 0.05 is conservative sanity check)
