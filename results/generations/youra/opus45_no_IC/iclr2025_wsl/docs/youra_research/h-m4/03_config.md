# Config: H-M4 (MECHANISM)

**Hypothesis:** At N=1K, MLP probe invariance < 0.5
**Format:** Hardcoded dict (all tasks Low complexity, 0 subtask budget)

Applied: No DL-config KB pattern found relevant (KB returned unrelated diffusion-model docs) — standard AdamW/MSE hyperparameters from PRD FR-2/FR-3, consistent with H-M3 defaults.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: No config/dataclass files exist in `h-m3/code/` (glob for `*config*.py` returned none) — H-M3 uses inline constants, not a config module. No config classes to inherit field names from.
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (matches repo convention of inline constants; single dict avoids introducing a new pattern for a 9-task Low-complexity hypothesis)

---

## CONFIG (`h-m4/code/config.py`)

```python
CONFIG = {
    # Population (data_gen.py)
    "n_models": 1200,
    "n_train": 1000,
    "n_test": 200,
    "hidden_dims": (32, 32),
    "input_dim": 32,
    "output_dim": 10,
    "population_seed": 0,      # base_seed for model generation
    "split_seed": 42,          # train/test split seed

    # Training (train_mlp.py)
    "lr": 1e-3,
    "epochs": 50,
    "batch_size": 32,
    "optimizer": "AdamW",
    "loss": "MSE",
    "train_seeds": list(range(10)),  # 10 seeds, PRD NFR-1

    # Probe invariance (probe_invariance.py)
    "num_permutations": 10,

    # NFN control (nfn_control.py) — optional, graceful skip if unavailable
    "nfn_enabled": True,

    # Gate thresholds (run_experiment.py)
    "mlp_invariance_threshold": 0.5,   # pass if mean_invariance < this
    "nfn_invariance_threshold": 0.95,  # pass if nfn mean_invariance > this

    # Paths
    "figures_dir": "h-m4/figures/",
    "results_path": "h-m4/results.json",
}
```

No per-task subtask breakdown — all R-1..R-9 are Low complexity (budget: 0 subtasks).
