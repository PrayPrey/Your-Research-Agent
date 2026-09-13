# H-E1 Configuration

**Scope**: PoC (existence) — single fixed config, no ablation grid.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing h-e1 config in current run; archived h-e1 configs found but belong to a different hypothesis (gpt2-medium/LongBench) — not reused.
**Config Files Found**: None (new)
**Pattern Used**: YAML (loaded into a dict at runtime)

**Applied**: Standard HF/sklearn defaults (no KB pattern match required for PoC config).

## Config Schema (YAML)

```yaml
# config.yaml
model:
  name: "bert-base-uncased"
  layer: -1               # last hidden layer
  max_length: 512

dataset:
  name: "super_glue"
  tasks: ["boolq", "cb", "copa", "multirc", "record", "rte", "wic", "wsc"]
  split: "validation"

clustering:
  method: "kmeans"
  n_clusters: 8
  random_state: 42
  n_init: 10               # sklearn default

experiment:
  seed: 42
  batch_size: 16
  device: "cuda"
  output_dir: "h-e1/results/"
```

## Defaults (Python dict, PoC — single fixed config)

```python
CONFIG = {
    "model_name": "bert-base-uncased",
    "layer": -1,
    "max_length": 512,
    "dataset_name": "super_glue",
    "tasks": ["boolq", "cb", "copa", "multirc", "record", "rte", "wic", "wsc"],
    "split": "validation",
    "n_clusters": 8,
    "random_state": 42,
    "n_init": 10,
    "seed": 42,
    "batch_size": 16,
    "device": "cuda",
    "output_dir": "h-e1/results/",
}
```

## Hyperparameter Ranges (ablation reference only — not run in PoC)

| Param | PoC value | Ablation range |
|---|---|---|
| `n_clusters` | 8 | 4, 8, 16, 32 |
| `layer` | -1 | -1, -4, 6 (mid), 0 (embed) |
| `max_length` | 512 | 128, 256, 512 |
| `random_state` | 42 | N/A (single seed for PoC) |
