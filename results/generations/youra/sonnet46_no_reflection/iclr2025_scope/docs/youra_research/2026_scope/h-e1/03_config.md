# Configuration: H-E1
# LoRA-KV Misalignment Diagnostic Experiment

**Hypothesis**: H-E1 | **Type**: EXISTENCE | **Tier**: LIGHT | **Inference-only**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config design
**Pattern Used**: dataclass

Applied: standard inference-only diagnostic config pattern

---

## Full Experiment Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Dataset
    dataset_id: str = "nyu-mll/glue"
    dataset_config: str = "mnli"
    primary_n: int = 100
    extended_n: int = 500
    borderline_low: float = 0.65
    borderline_high: float = 0.75
    # Non-standard: threshold=0.7 is midpoint of borderline band, per H-E1 spec
    misalignment_threshold: float = 0.7
    max_seq_len: int = 512
    seed: int = 42

    # LoRA model
    lora_base_model: str = "meta-llama/Meta-Llama-3.1-8B"
    lora_checkpoint: str = "yophis/DRM-Llama-3.1-8B-mnli"
    num_labels: int = 3
    attn_impl: str = "eager"  # Required for output_attentions=True

    # Locret model
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"

    # GQA config
    num_query_heads: int = 32
    num_kv_heads: int = 8
    num_layers: int = 32
    kv_repeat: int = 4  # num_query_heads // num_kv_heads

    # Correlation
    aggregation_method: str = "mean"  # mean over heads per layer
    spearman_alternative: str = "less"  # one-sided test: rho < threshold

    # Output
    results_path: str = "h-e1/results/spearman_correlation_results.json"
    figures_dir: str = "h-e1/figures/"

    # Runtime
    dtype: str = "float16"
    device_map: str = "auto"
```

---

## A-5: Spearman + GQA Expansion [Complexity: 12, Budget: 1 subtask]

Applied: standard inference-only diagnostic config pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Correlation computation config | Head expansion params, aggregation method, borderline thresholds |

### Key Config Values (A-5)

```python
# GQA expansion
num_query_heads: int = 32
num_kv_heads: int = 8
kv_repeat: int = 4          # torch.repeat_interleave factor for KV→query alignment

# Borderline detection
borderline_low: float = 0.65
borderline_high: float = 0.75
misalignment_threshold: float = 0.7  # mean rho < 0.7 confirms misalignment

# Aggregation
aggregation_method: str = "mean"      # per-layer mean across expanded query heads
spearman_alternative: str = "less"    # one-sided scipy.stats.spearmanr test
```

---

## A-6: Results + Visualization [Complexity: 10, Budget: 1 subtask]

Applied: standard inference-only diagnostic config pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Output paths config | Results JSON schema, figure paths, visualization settings |

### Key Config Values (A-6)

```python
# Output paths
results_path: str = "h-e1/results/spearman_correlation_results.json"
figures_dir: str = "h-e1/figures/"

# Figure filenames (relative to figures_dir)
FIGURE_BAR      = "mean_rho_bar.png"
FIGURE_HEATMAP  = "layer_head_heatmap.png"
FIGURE_SCATTER  = "token_scatter.png"
FIGURE_HISTOGRAM = "rho_histogram.png"

# Visualization settings
fig_dpi: int = 150
fig_format: str = "png"
colormap_heatmap: str = "coolwarm"
```

---

## Results JSON Schema

```json
{
  "hypothesis_id": "H-E1",
  "primary_n": 100,
  "extended_n": 500,
  "seed": 42,
  "misalignment_threshold": 0.7,
  "summary": {
    "mean_spearman_rho": 0.0,
    "std_spearman_rho": 0.0,
    "fraction_below_threshold": 0.0,
    "misalignment_confirmed": false
  },
  "per_layer": [
    {
      "layer": 0,
      "mean_rho": 0.0,
      "std_rho": 0.0,
      "per_head_rho": [0.0]
    }
  ],
  "borderline_examples": [
    {
      "example_idx": 0,
      "mean_rho": 0.0,
      "label": 0
    }
  ],
  "figures": {
    "bar": "h-e1/figures/mean_rho_bar.png",
    "heatmap": "h-e1/figures/layer_head_heatmap.png",
    "scatter": "h-e1/figures/token_scatter.png",
    "histogram": "h-e1/figures/rho_histogram.png"
  }
}
```

---

## YAML Configuration Reference

```yaml
experiment:
  hypothesis_id: H-E1
  seed: 42
  dtype: float16
  device_map: auto

dataset:
  id: nyu-mll/glue
  config: mnli
  primary_n: 100
  extended_n: 500
  max_seq_len: 512
  borderline_low: 0.65
  borderline_high: 0.75
  misalignment_threshold: 0.7

models:
  lora:
    base: meta-llama/Meta-Llama-3.1-8B
    checkpoint: yophis/DRM-Llama-3.1-8B-mnli
    num_labels: 3
    attn_impl: eager
  locret:
    checkpoint: hyx21/Locret-llama-3.1-8B-instruct

gqa:
  num_query_heads: 32
  num_kv_heads: 8
  num_layers: 32
  kv_repeat: 4

correlation:
  aggregation_method: mean
  spearman_alternative: less

output:
  results_path: h-e1/results/spearman_correlation_results.json
  figures_dir: h-e1/figures/
  fig_dpi: 150
  fig_format: png
  colormap_heatmap: coolwarm
```
