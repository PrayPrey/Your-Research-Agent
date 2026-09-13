# Config: H-E1 (Behavioral Information Exists Beyond Accuracy)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT

Applied: fixed-constants-dict (statistical-analysis-pipeline, single-run PoC, no hyperparameter search)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, no existing code/base hypothesis
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (module-level constants in `config.py`)

---

## Config (Hardcoded Dict / Module Constants)

Single fixed config — no variations, no grid, 1 seed. Matches architecture's `config.py`.

```python
# config.py
CONFIG = {
    "seed": 42,
    "n_classes": 10,
    "residual_ratio_threshold": 0.05,  # gate: PASS if residual_ratio > this

    # Data
    "data_url": "https://zenodo.org/records/6620869/files/dataset_cifar_small_hyp_rand.pt",
    "data_path": "./data/dataset_cifar_small_hyp_rand.pt",
    "cifar_root": "./data",

    # Output
    "figures_dir": "./figures",
    "results_path": "./results.json",
    "figure_dpi": 300,
}
```

**Non-standard**: `residual_ratio_threshold=0.05` is the PRD-mandated gate criterion (FR-5/Section 6), not a tunable hyperparameter.

No epochs/batch_size/lr — this is a statistical analysis on frozen pre-trained model predictions, no training involved.

---

## A-1..A-8: Data Loading through Reporting [Complexity: 4-8 each, Budget: LIGHT]

**Applied**: Single shared `CONFIG` dict imported by all modules (`data.py`, `analysis.py`, `visualize.py`, `run.py`).

All tasks (A-1 through A-8) consume `CONFIG` directly — no per-task config variants. Function signatures already fully specified in `03_architecture.md`; no additional config schema needed beyond the dict above.

### Subtasks
Subtask breakdown and counts are owned by architecture.md's Epic Tasks table (A-1..A-8, complexity 4-8, breakdown column). No config-specific subtask splits required — this dict is consumed as-is by all 8 tasks.

---

## Notes

- EXISTENCE hypothesis: omitted hyperparameter grids, ablations, multiple configs — single fixed run is sufficient to test residual_ratio > 0.05.
- 1 seed (42) per NFR-2 (reproducibility).
- No YAML — dict kept in `config.py` per architecture spec, directly importable by all modules.
