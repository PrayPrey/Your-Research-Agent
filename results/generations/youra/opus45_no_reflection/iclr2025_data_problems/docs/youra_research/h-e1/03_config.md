# Config: H-E1 (EXISTENCE PoC)

Applied: standard PyTorch defaults (no matching KB config pattern found)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict

## Config (code/config.py)

Single fixed config per PRD — no hyperparameter search (EXISTENCE PoC).

```python
CONFIG = {
    # data
    "dataset": "glue/sst2",
    "noise_rate": 0.05,
    "noise_seed": 42,
    "max_length": 128,

    # models
    "bert_name": "bert-base-uncased",
    "gpt2_name": "gpt2",
    "num_labels": 2,

    # training
    "lr": 2e-5,
    "epochs": 3,
    "batch_size": 32,
    "seeds": [42, 43, 44, 45, 46],

    # attribution
    "methods": ["trak", "ekfac", "tracin"],
    "architectures": ["bert", "gpt2"],

    # stats
    "alpha": 0.05,          # significance threshold
    "min_auc_diff": 0.05,   # 5% required diff
    "min_effect_size": 0.3, # Cohen's d

    # paths
    "checkpoint_dir": "checkpoints/",
    "figures_dir": "figures/",
    "results_path": "results.json",
}
```

## Subtasks

None — budget is 0 subtasks (simple config.py).
