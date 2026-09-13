# Configuration: h-e1

**Type:** EXISTENCE (PoC) — single fixed config, no sweeps, no ablations.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: YAML (hardcoded dict, loaded at runtime)

---

## A-1: Attribution Method Comparison [Complexity: PoC, Budget: n/a]

**Applied**: Standard PyTorch / TRAK paper defaults (no KB pattern match; used official repo defaults from experiment brief)

### Configuration (YAML)

```yaml
# config.yaml — h-e1 EXISTENCE PoC

seed: 42

data:
  dataset: CIFAR10
  root: ./data
  num_classes: 10
  train_size: 50000
  test_size: 10000
  # PoC: subsample test set for tractable pairwise scoring (full train set retained)
  eval_subset_size: 1000
  batch_size: 128
  eval_batch_size: 256
  num_workers: 4
  normalize_mean: [0.4914, 0.4822, 0.4465]
  normalize_std: [0.2470, 0.2435, 0.2616]

model:
  arch: resnet18_cifar   # torchvision resnet18, conv1->3x3 stride1, maxpool->Identity
  num_classes: 10
  pretrained: false

training:
  # Only used if no pretrained checkpoint available
  optimizer: sgd
  lr: 0.1
  momentum: 0.9
  weight_decay: 5.0e-4
  lr_schedule: cosine
  epochs: 200
  loss: cross_entropy
  # Non-standard: checkpoints saved at fixed epochs for TracIn (needs multiple checkpoints)
  checkpoint_epochs: [50, 100, 150, 200]

trak:
  # Random projection dimension (TRAK paper default for CIFAR-scale models)
  projection_dim: 2048
  proj_type: rademacher
  task: image_classification
  num_model_ids: 4          # = len(checkpoint_epochs), one per checkpoint

tracin:
  # Uses same checkpoints as TRAK for fair comparison
  checkpoints: ${training.checkpoint_epochs}
  loss_fn: cross_entropy
  # Non-standard: learning rates per checkpoint (TracIn weights by LR at capture time)
  checkpoint_lrs: [0.05, 0.02, 0.005, 0.001]

kronfluence:
  factors_name: ekfac_factors
  scores_name: pairwise_scores
  strategy: ekfac
  # PoC: single-pass factor fitting, no iterative refinement
  covariance_data_partitions: 1
  lambda_data_partitions: 1

evaluation:
  correlation_metrics: [pearson, spearman, kendall]
  distinctness_threshold: 0.9   # from PRD success criteria

paths:
  data_dir: ./data
  checkpoint_dir: ./h-e1/checkpoints
  output_dir: ./h-e1/outputs
  figures_dir: ./h-e1/figures
  correlations_file: ./h-e1/outputs/correlations.json
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Full pipeline config | Single config drives train/load model, run 3 attribution methods, compute correlations, generate figures |

---

## Defaults Justification (non-obvious only)

- `projection_dim: 2048` — TRAK paper default for image classification at CIFAR scale.
- `checkpoint_epochs` / `checkpoint_lrs` — TracIn requires multiple checkpoints with associated LR weighting; shared with TRAK's `num_model_ids` for consistent comparison basis.
- `eval_subset_size: 1000` — meets PRD acceptance criterion (≥1000 test samples) while keeping PoC runtime bounded.
- `covariance_data_partitions/lambda_data_partitions: 1` — Kronfluence default single-partition fitting sufficient for PoC (no distributed factor computation needed).
- All other values are library/torchvision defaults.
