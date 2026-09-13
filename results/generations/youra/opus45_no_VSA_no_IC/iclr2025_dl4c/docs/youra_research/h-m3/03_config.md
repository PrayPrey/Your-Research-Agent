# h-m3 Configuration

**Applied**: Standard scipy/pandas defaults (no KB pattern match for stats-only analysis)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (h-m3 has no existing `code/` dir in active version)
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (single fixed config, no ML training/tuning)

---

## Configuration (Hardcoded Dict)

```python
CONFIG = {
    # Paths
    "input_data": "../h-e1/code/outputs/results.csv",
    "output_dir": "outputs/",
    "figures_dir": "figures/",

    # Thresholds
    "success_threshold": 0.10,        # unanimous_acc - split_acc >= 0.10
    "significance_level": 0.05,       # p-value threshold
    "falsification_threshold": 0.05,  # improvement < 0.05 => falsified

    # Experiment
    "n_judges": 4,
    "random_seed": 42,

    # Visualization
    "figure_format": "png",
    "dpi": 150,
    "style": "seaborn-v0_8-whitegrid",
}
```

## Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-1 | Config module | Single `CONFIG` dict, imported by analyze.py/visualize.py |

---

## CLI Argument Mapping

```bash
python analyze.py \
    --input-data ../h-e1/code/outputs/results.csv \
    --output-dir outputs/ \
    --figures-dir figures/ \
    --success-threshold 0.10 \
    --significance-level 0.05
```

| CLI Flag | Config Key | Default |
|----------|-----------|---------|
| `--input-data` | `input_data` | `../h-e1/code/outputs/results.csv` |
| `--output-dir` | `output_dir` | `outputs/` |
| `--figures-dir` | `figures_dir` | `figures/` |
| `--success-threshold` | `success_threshold` | `0.10` |
| `--significance-level` | `significance_level` | `0.05` |

No other CLI args needed — `n_judges`, `random_seed`, and visualization settings are fixed (PoC-style, no tuning).
