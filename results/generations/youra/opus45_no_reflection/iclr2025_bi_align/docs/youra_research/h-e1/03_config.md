# Configuration: H-E1 (EXISTENCE / PoC)

**Hypothesis:** Collaboration score extracts agency signals orthogonal to preference labels
**Type:** EXISTENCE - statistical analysis, no training

Applied: No relevant KB pattern found (searched "experiment config patterns"); standard fixed-dict PoC config used.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dict (fixed, single config, no dataclass needed for PoC)

---

## config.py

Single fixed config file (`config.py`), no CLI args, no variations — this is an EXISTENCE PoC.

```python
CONFIG = {
    # Experiment
    "seed": 42,
    "sample_size": 1000,

    # Dataset
    "dataset_name": "Anthropic/hh-rlhf",
    "dataset_subset": "helpful-base",

    # Paths
    "figures_dir": "figures/",
    "results_path": "results.json",

    # Thresholds (gate conditions)
    "correlation_threshold": 0.7,   # gate_passed = abs(correlation) < 0.7
    "p_value_threshold": 0.05,
}
```

No subtasks (0 budget) — config is a single flat dict consumed directly by `data.py`, `analysis.py`, `visualize.py`, `run_experiment.py`.

---

## Self-Validation

- [x] ONE format only (dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] 0 subtasks (within budget)
- [x] Codebase Analysis (Serena) section included
