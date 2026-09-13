# Config: h-m2 (Evaluation on low-entropy subset)

**Hypothesis**: On low-entropy subset (H_L < 25th percentile), trajectory metrics achieve AUROC > 0.55 with 95% CI LB > 0.50

**Applied**: Standard sklearn/NumPy evaluation defaults (no KB pattern match — reuses h-e1 dict-config style).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: h-e1 config verified from actual code (`docs/youra_research/h-e1/03_config.md`) — no runnable code/ dir exists yet for h-e1, only spec; field names below match h-e1's `CONFIG` dict spec.
**Config Files Found**: `docs/youra_research/h-e1/03_config.md` (CONFIG dict: seed, target_layers, dataset, figures_dir, etc.)
**Pattern Used**: hardcoded dict (single fixed config — simple evaluation, no variation needed)

---

## A-1: Setup & Evaluation Config [Complexity: 2, Budget: 2]

**Applied**: Bootstrap CI + AUROC defaults matching h-e1 gate thresholds.

### Configuration (Hardcoded Dict)

```python
# code/config.py
CONFIG = {
    "seed": 42,
    "h_e1_features_path": "../h-e1/code/features.npz",  # H_L, NTI, labels from h-e1
    "figures_dir": "figures/",
    "entropy_percentile": 25,      # low-entropy cutoff (H_L < this percentile)
    "n_bootstrap": 1000,
    "confidence_level": 0.95,
    "auroc_threshold": 0.55,       # gate: AUROC must exceed
    "ci_lower_bound_min": 0.50,    # gate: 95% CI LB must exceed
}
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | config.py | Define CONFIG dict above |
| C-1-2 | dirs | Create `CONFIG["figures_dir"]` if not exists |

---

## Notes

- Reuses h-e1's `features.npz` output (H_L, NTI, labels) — no recomputation, per PRD constraint.
- Single global CONFIG dict, no dataclass — evaluation-only script, zero config variation needed.
- If h-e1's actual saved feature file path differs once h-e1 code runs, update `h_e1_features_path` accordingly (h-e1 has no `code/` dir yet, only spec).
