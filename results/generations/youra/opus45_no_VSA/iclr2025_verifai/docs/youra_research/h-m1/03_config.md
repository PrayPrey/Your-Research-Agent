# Config: H-M1 (ΔPass₁₂ Trajectory Analysis)

**Applied**: No relevant KB pattern found (similarity <0.43, DL-training patterns don't fit post-hoc stats pipeline) — standard dataclass with fixed paths per PRD.

---

## Codebase Analysis (Serena)

**Project Type**: green-field (h-m1/code/ does not exist yet) + base_hypothesis data contract (h-e1)
**Status**: Verified h-e1's actual `config.py` — h-m1 does NOT import or extend it (data contract only, per architecture doc). h-m1 introduces its own independent `AnalysisConfig`.
**Config Files Found**: `h-e1/code/config.py` (`ExperimentConfig` dataclass, read-only reference — not inherited)
**Pattern Used**: dataclass

**Note on field naming**: h-e1 uses `alpha: float = 0.05` for its bootstrap CI significance level. H-m1 reuses the same `alpha` name/value for McNemar's test significance threshold — consistent convention, not code inheritance (h-e1 module code is never imported).

---

## M-1: Config + Data Loading [Complexity: 6]

**Applied**: fixed-config dataclass, no CLI/env overrides (single fixed analysis run per PRD NFR-2 reproducibility)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class AnalysisConfig:
    logs_path: str = "../h-e1/code/results/h-e1_iteration_logs.jsonl"
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    conditions: tuple[str, str] = ("static_first", "exec_first")
    iterations: tuple[int, ...] = (1, 2, 3)
    alpha: float = 0.05
    required_fields: tuple[str, ...] = ("problem_id", "condition", "iteration", "passed")
```

No subtasks allocated (budget: 0) — config is a single fixed dataclass, no variants.

---

## Full Config Path Contract

| Field | Value | Source |
|-------|-------|--------|
| `logs_path` | `../h-e1/code/results/h-e1_iteration_logs.jsonl` | PRD FR-1 |
| `results_dir` | `results/` | PRD Output Artifacts |
| `figures_dir` | `figures/` | PRD FR-5 |
| `conditions` | `("static_first", "exec_first")` | PRD FR-2 |
| `iterations` | `(1, 2, 3)` | PRD FR-2 |
| `alpha` | `0.05` | PRD Success Criteria (McNemar p<0.05) |

No hyperparameters to tune — this is a deterministic post-hoc statistical analysis (NFR-2: byte-identical results, no random sampling, no seed needed).
