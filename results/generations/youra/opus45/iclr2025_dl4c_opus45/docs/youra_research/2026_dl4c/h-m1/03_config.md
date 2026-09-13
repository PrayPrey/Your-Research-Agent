# Config: H-M1 Zero-Reward Basin Mechanism Analysis

**Hypothesis**: H-M1 (MECHANISM) - Statistical analysis, no training/GPU
**Date**: 2026-03-24

Applied: pytorch-inductor-dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `h-e1/code/config.py` (read actual implementation)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/20260323_dl4c/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Models
    rl_model_id: str = "Salesforce/codet5-large-ntp-py"
    dpo_model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    # Generation
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    n_samples: int = 1
    seed: int = 42
    # Execution
    timeout: int = 5
    # Paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    # Statistical thresholds
    chi2_p_threshold: float = 0.05
    cramers_v_threshold: float = 0.05
```

**Verified from**: `docs/youra_research/20260323_dl4c/h-e1/code/config.py` (actual implementation)

---

## A-2: Config Module [Complexity: 5, Budget: 2 subtasks]

**Applied**: pytorch-inductor-dataclass pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class HM1Config:
    # H-E1 data paths
    h_e1_code_dir: str = "../../h-e1/code"
    rl_results_path: str = "../../h-e1/code/outputs/rl_execution_results.json"
    dpo_results_path: str = "../../h-e1/code/outputs/dpo_execution_results.json"
    h_e1_experiment_results_path: str = "../../h-e1/code/outputs/experiment_results.json"
    h_e1_metrics_path: str = "../../h-e1/code/outputs/metrics.json"

    # Output paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds
    fisher_p_threshold: float = 0.05
    # Non-standard: one-sided "greater" because mechanism predicts RL > DPO direction
    alternative: str = "greater"

    # Expected counts from H-E1 (for validation; tolerates ±10 difference)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    # Reproducibility
    seed: int = 42


CONFIG = HM1Config()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Write HM1Config dataclass | Implement config.py with all fields above |
| C-2-2 | Validate paths at import | Add `__post_init__` warning if H-E1 output files not found |
