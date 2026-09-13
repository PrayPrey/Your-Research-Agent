# Config: H-M2 (Scale-Ensemble Outperformance)

**Applied**: Standard PyTorch/stdlib dataclass config (no closer KB match for McNemar/ensemble config pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: `h-e1/code/` glob returned no files — H-E1 has no reusable Python modules, only data artifacts (`results.csv`, `contingency.csv`). Serena symbol search not applicable (no code to introspect); confirmed via `Glob` on `h-e1/code/*config*` (empty result).
**Config Files Found**: None — new config design
**Pattern Used**: dataclass (green-field for H-M2; H-E1 contributes data paths only, not config schema)

---

## A-1..A-9: Full Task Set [Complexity: Low-Medium, Budget: 0 subtasks]

Single low-complexity task set (all tasks Low/Medium per architecture distribution) — no subtask breakdown required.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field


@dataclass
class EnsembleConfig:
    judges: tuple[str, ...] = ("7b", "70b", "proprietary")
    he1_results_path: str = "../h-e1/code/results.csv"
    he1_contingency_path: str = "../h-e1/code/contingency.csv"
    n_expected_problems: int = 164

    # Statistical thresholds
    p_value_threshold: float = 0.05
    improvement_target: float = 0.03  # 3% accuracy improvement (success criterion)
    improvement_partial: float = 0.02  # 2% (partial success floor)

    # Baselines
    codebertscore_baseline: float = 0.58

    # Ablation exclusion for AB3 (2-tier subset)
    ab3_exclude_judge: str = "7b"

    # Reproducibility (AB4 random baseline only; primary ensemble is seed-free)
    seed: int = 42

    # Output paths
    comparison_csv_path: str = "comparison.csv"
    mcnemar_results_json_path: str = "mcnemar_results.json"
    figures_dir: str = "figures/"
```

### Subtasks [0/0 used]

No subtask breakdown — budget allocated is 0; all tasks (A-1 through A-9) proceed directly per architecture's Epic Tasks table.
