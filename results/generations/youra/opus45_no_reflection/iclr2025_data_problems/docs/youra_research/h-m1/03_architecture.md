# Architecture: H-M1

**Hypothesis:** Attention pattern structure differs between encoder (bidirectional) and decoder (causal)
**Type:** MECHANISM | **Tier:** FULL

Applied: HuggingFace `output_attentions=True` unified extraction pattern (BertViz-style)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code. h-e1 (`docs/youra_research/h-e1/`) has no `code/` directory to reference; H-M1 uses pretrained models directly, no training/base code reuse needed.
**Analyzed Path:** N/A
**Findings:** New implementation from scratch.

---

## Module Structure

### data_loader (`data_loader.py`)

**Dependencies:** datasets, transformers

```python
def load_sst2_validation() -> list[str]: ...  # 872 texts from glue/sst2 validation
def tokenize_batch(tokenizer, texts: list[str], max_length: int = 128) -> dict: ...
```

### models (`models.py`)

**Dependencies:** transformers, torch

```python
def load_bert() -> tuple[AutoModel, AutoTokenizer]: ...  # bert-base-uncased, output_attentions=True
def load_gpt2() -> tuple[AutoModel, AutoTokenizer]: ...  # gpt2, pad_token=eos_token, output_attentions=True
```

### attention_extraction (`attention_extraction.py`)

**Dependencies:** models, data_loader, torch

```python
def extract_attentions(model, tokenizer, texts: list[str], max_length: int = 128) -> list[tuple]:
    """Returns list of per-sample attention tuples: (layers, batch, heads, seq, seq)."""
    ...
```

### sparsity_metrics (`sparsity_metrics.py`)

**Dependencies:** torch, numpy

```python
def upper_triangle_sparsity(attn_matrix: Tensor, threshold: float = 1e-6) -> float: ...
def compute_attention_sparsity(attention_weights: list) -> dict: ...  # overall/upper sparsity, is_causal
def per_layer_sparsity(attention_weights: list, num_layers: int = 12) -> list[float]: ...
def attention_entropy(attn_matrix: Tensor) -> Tensor: ...  # per-head entropy
def aggregate_across_samples(per_sample_metrics: list[dict]) -> dict: ...  # mean/std
```

### verify (`verify.py`)

**Dependencies:** sparsity_metrics

```python
def verify_attention_structure(bert_metrics: dict, gpt2_metrics: dict) -> dict:
    """sparsity_difference, bert_is_causal, gpt2_is_causal, pass/fail gate."""
    ...
```

### visualize (`visualize.py`)

**Dependencies:** matplotlib, seaborn, sparsity_metrics

```python
def plot_gate_comparison(bert_metrics: dict, gpt2_metrics: dict, out_path: str) -> None: ...  # required
def plot_attention_heatmaps(bert_attn: Tensor, gpt2_attn: Tensor, tokens_bert, tokens_gpt2, out_path: str) -> None: ...
def plot_layerwise_sparsity(bert_layers: list[float], gpt2_layers: list[float], out_path: str) -> None: ...
def plot_entropy_histogram(bert_entropy: Tensor, gpt2_entropy: Tensor, out_path: str) -> None: ...
```

### run_experiment (`run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> None:
    """Load data -> load models -> extract attentions (both) -> compute metrics
    -> verify gate -> generate figures -> save results.json + report.md"""
    ...
```

---

## File Organization

```
h-m1/code/
  data_loader.py
  models.py
  attention_extraction.py
  sparsity_metrics.py
  verify.py
  visualize.py
  run_experiment.py
  results.json
  report.md
figures/
  gate_comparison.png
  attention_heatmaps.png
  layerwise_sparsity.png
  entropy_histogram.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | SST-2 via HF datasets, tokenize per-model | 6 | 2+1+1+2 |
| A-2 | Model loading | Load BERT + GPT-2 with output_attentions | 5 | 1+2+1+1 |
| A-3 | Attention extraction | Forward pass loop, 872 samples, batch=1 | 9 | 3+2+2+2 |
| A-4 | Sparsity metrics core | upper_triangle_sparsity, overall sparsity, is_causal | 8 | 2+1+3+2 |
| A-5 | Per-layer + entropy metrics | 12-layer breakdown, per-head entropy | 7 | 2+2+2+1 |
| A-6 | Statistical aggregation | Mean/std across 872 samples, both models | 6 | 2+2+1+1 |
| A-7 | Gate verification | Compare vs thresholds (<0.10 / >0.99), pass/fail | 4 | 1+1+1+1 |
| A-8 | Required visualization | Bar chart BERT vs GPT-2 gate metric | 4 | 1+1+1+1 |
| A-9 | Additional visualizations | Heatmaps, layer-wise line plot, entropy histogram | 8 | 3+1+2+2 |
| A-10 | Results reporting | JSON metrics + Markdown summary report | 5 | 1+1+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7, A-8, A-9, A-10]
