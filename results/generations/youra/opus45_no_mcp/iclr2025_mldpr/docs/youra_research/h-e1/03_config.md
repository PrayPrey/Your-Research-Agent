# Configuration: H-E1

**Type:** EXISTENCE (PoC)
**Format:** Hardcoded dict (single fixed config, no variations)

Applied: standard-cifar-resnet-training-config

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** dict

---

## Configuration (config.py)

```python
CONFIG = {
    "seed": 42,
    "batch_size": 128,
    "epochs": 200,
    "lr": 0.1,
    "momentum": 0.9,
    "weight_decay": 5e-4,
    "lr_milestones": [100, 150],
    "lr_gamma": 0.1,
    "cifar10_norm": ((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    "svhn_norm": ((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970)),
    "num_classes": 10,
    "data_root": "./data",
    "checkpoint_dir": "./checkpoints",
    "figures_dir": "./figures",
    "results_path": "./results.json",
    "svhn_extra_sample_size": 26032,  # matched to SVHN test size (FR "matched for fair comparison")
    "device": "cuda",  # fallback to "cpu" if unavailable (NFR-1 supports CPU)
}
```

All values sourced directly from PRD/experiment brief (SGD/MultiStepLR = ResNet paper defaults for CIFAR; batch_size/epochs = standard practice). No tuning performed (PoC).

- `svhn_norm`: not specified in brief; standard SVHN channel stats used since brief only gave CIFAR-10 norm but requires per-dataset normalization (FR-1.4).
- `svhn_extra_sample_size`: matches SVHN test set size (26,032) per PRD 4.2 "matched to test set size for fair comparison".

## Experiment Settings

- **Seeds:** 1 (`seed=42`) — PoC single run per condition, no multi-seed statistics (Non-Goal in PRD).
- **Conditions:** 2 (`cifar10` high-use, `svhn` low-use) — both trained with identical CONFIG values (only dataset/normalization differ).
- **Gate metrics:** Cohen's d > 0.3, p < 0.05 (computed in stats.py from single gap_high vs gap_low values — PoC uses n=1 per condition per experiment brief; direction check `gap_high > gap_low` is the primary PoC pass condition).

## Subtasks

None — budget is 0, config integrated directly into epic tasks A-1 through A-8 (see 03_architecture.md).
