# Architecture: H-E1
# LoRA-KV Misalignment Diagnostic Experiment

**Applied**: inference-only diagnostic pattern (PEFT attention extraction + scipy correlation)
**Applied**: GQA head expansion pattern (repeat_interleave for KV→query head alignment)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: docs/youra_research/20260520_scope/h-e1 (directory only, no source files)
**Findings**: New implementation from scratch.

---

## Overview

H-E1 is an inference-only diagnostic. Two pre-trained models (LLaMA-3.1-8B+LoRA and LLaMA-3.1-8B+Locret) are loaded sequentially. Attention scores and CIS scores are extracted per-example, Spearman ρ is computed with GQA expansion, and results + figures are saved.

---

## File Organization

```
h-e1/
├── code/
│   ├── config.py          # Fixed experiment configuration
│   ├── data_loader.py     # GLUE MNLI loading + tokenization
│   ├── lora_extractor.py  # LoRA model load + attention extraction
│   ├── locret_extractor.py# Locret model load + CIS extraction
│   ├── correlate.py       # Spearman ρ computation with GQA handling
│   ├── visualize.py       # Bar chart, heatmap, scatter, histogram
│   └── run_experiment.py  # Orchestration entry point
├── results/
│   └── spearman_correlation_results.json
└── figures/
    ├── mean_rho_bar.png
    ├── layer_head_heatmap.png
    ├── token_scatter.png
    └── rho_histogram.png
```

---

## Module Structure

### Config (`code/config.py`)

**Dependencies**: none

```python
class ExperimentConfig:
    # Dataset
    dataset_id: str = "nyu-mll/glue"
    dataset_config: str = "mnli"
    primary_n: int = 100
    extended_n: int = 500
    borderline_low: float = 0.65
    borderline_high: float = 0.75
    max_seq_len: int = 512
    seed: int = 42

    # LoRA model
    lora_base_model: str = "meta-llama/Meta-Llama-3.1-8B"
    lora_checkpoint: str = "yophis/DRM-Llama-3.1-8B-mnli"
    num_labels: int = 3
    attn_impl: str = "eager"

    # Locret model
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"

    # GQA config
    num_query_heads: int = 32
    num_kv_heads: int = 8
    num_layers: int = 32
    kv_repeat: int = 4  # num_query_heads // num_kv_heads

    # Output
    results_path: str = "h-e1/results/spearman_correlation_results.json"
    figures_dir: str = "h-e1/figures/"
    dtype: str = "float16"
    device_map: str = "auto"
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config

```python
from datasets import Dataset
from transformers import PreTrainedTokenizer

class MNLIDataLoader:
    def __init__(self, config: ExperimentConfig): ...

    def load(self, n: int = None) -> Dataset:
        """Load GLUE MNLI validation_matched, select first n examples."""
        ...

    def tokenize(
        self,
        dataset: Dataset,
        tokenizer: PreTrainedTokenizer
    ) -> Dataset:
        """Tokenize premise+hypothesis pairs, max_length=512, pad/truncate."""
        ...

    def get_batch(
        self,
        dataset: Dataset,
        idx: int
    ) -> dict:
        """Return single-example dict: {input_ids, attention_mask, label}."""
        ...
```

---

### LoRAExtractor (`code/lora_extractor.py`)

**Dependencies**: Config

```python
import torch
from torch import Tensor
from transformers import PreTrainedModel, PreTrainedTokenizer

class LoRAExtractor:
    def __init__(self, config: ExperimentConfig): ...

    def load_model(self) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        """
        Load LLaMA-3.1-8B + LoRA MNLI checkpoint.
        attn_implementation="eager" is mandatory.
        Falls back to LoRA fine-tune if checkpoint incompatible.
        """
        ...

    def extract_attention_scores(
        self,
        model: PreTrainedModel,
        input_ids: Tensor,
        attention_mask: Tensor
    ) -> list[Tensor]:
        """
        Run forward pass with output_attentions=True.
        Returns list of per-layer attention scores, each (num_query_heads, seq_len).
        Aggregation: attn[layer].sum(dim=2).squeeze(0) — sum over query axis.
        """
        ...

    def get_layer_scores(
        self,
        all_layer_scores: list[Tensor],
        layer_idx: int
    ) -> Tensor:
        """Return (num_query_heads, seq_len) for a specific layer."""
        ...
```

---

### LocretExtractor (`code/locret_extractor.py`)

**Dependencies**: Config

```python
import torch
from torch import Tensor
from transformers import PreTrainedModel

class LocretExtractor:
    def __init__(self, config: ExperimentConfig): ...

    def load_model(self) -> PreTrainedModel:
        """
        Load hyx21/Locret-llama-3.1-8B-instruct.
        Uses official Locret loading pattern from huangyuxiang03/Locret.
        """
        ...

    def extract_cis_scores(
        self,
        model: PreTrainedModel,
        input_ids: Tensor,
        attention_mask: Tensor
    ) -> list[Tensor]:
        """
        Run forward pass with output_retaining_scores=True.
        Returns list of per-layer CIS scores, each (num_kv_heads, seq_len).
        CIS = sigma([Q,K,V] @ W1) @ W2 per Locret paper Section 3.3.
        """
        ...

    def get_layer_scores(
        self,
        all_layer_scores: list[Tensor],
        layer_idx: int
    ) -> Tensor:
        """Return (num_kv_heads, seq_len) for a specific layer."""
        ...
```

---

### Correlator (`code/correlate.py`)

**Dependencies**: Config

```python
import numpy as np
from torch import Tensor

class SpearmanCorrelator:
    def __init__(self, config: ExperimentConfig): ...

    def expand_kv_heads(self, cis_scores: Tensor) -> Tensor:
        """
        Expand (num_kv_heads, seq_len) → (num_query_heads, seq_len)
        via repeat_interleave(kv_repeat, dim=0).
        """
        ...

    def compute_per_layer_rho(
        self,
        lora_scores: Tensor,
        cis_scores: Tensor,
        attention_mask: Tensor
    ) -> np.ndarray:
        """
        Compute per-head Spearman ρ for one layer, non-padding tokens only.
        Returns (num_query_heads,) array of ρ values.
        """
        ...

    def compute_example_rho(
        self,
        lora_all_layers: list[Tensor],
        cis_all_layers: list[Tensor],
        attention_mask: Tensor
    ) -> tuple[float, np.ndarray, np.ndarray]:
        """
        Average per-head ρ across all 32 layers for one example.
        Returns: (mean_rho, per_head_rho (32,), per_layer_rho (32, 32))
        """
        ...

    def aggregate_results(
        self,
        per_example_rho: list[float],
        per_example_per_head: list[np.ndarray],
        per_example_per_layer: list[np.ndarray]
    ) -> dict:
        """
        Aggregate across N examples.
        Returns dict: {mean_rho, std_rho, per_head_mean, per_layer_mean, all_example_rhos}
        """
        ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: Config

```python
class ResultVisualizer:
    def __init__(self, config: ExperimentConfig): ...

    def bar_chart(self, mean_rho: float, threshold: float = 0.7) -> None:
        """Bar chart: mean Spearman ρ vs. 0.7 threshold. Saved to figures_dir."""
        ...

    def layer_head_heatmap(self, per_layer_per_head: np.ndarray) -> None:
        """Heatmap (layer × head) of Spearman ρ. Shape (32, 32)."""
        ...

    def token_scatter(
        self,
        lora_scores: np.ndarray,
        cis_scores: np.ndarray,
        tokens: list[str],
        example_idx: int
    ) -> None:
        """Scatter plot of LoRA attn vs. CIS per token for one example."""
        ...

    def rho_histogram(self, per_example_rho: list[float]) -> None:
        """Histogram of per-example mean ρ distribution."""
        ...

    def save_all(
        self,
        results: dict,
        lora_scores_sample: list,
        cis_scores_sample: list,
        tokens_sample: list
    ) -> None:
        """Generate and save all four figures."""
        ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, DataLoader, LoRAExtractor, LocretExtractor, Correlator, Visualizer

```python
import json

def run(config: ExperimentConfig) -> dict:
    """
    Orchestration entry point.
    1. Load data (primary_n=100)
    2. Load LoRA model → extract attention scores per example
    3. Load Locret model → extract CIS scores per example
    4. Compute Spearman ρ per example → aggregate
    5. If borderline: extend to extended_n=500 (+ SST-2, QNLI if needed)
    6. Save results JSON + generate figures
    Returns: results dict with mean_rho, std_rho, pass/fail verdict
    """
    ...

def save_results(results: dict, path: str) -> None:
    """Save results dict to JSON."""
    ...

def check_borderline(mean_rho: float, config: ExperimentConfig) -> bool:
    """Return True if mean_rho in [borderline_low, borderline_high]."""
    ...

if __name__ == "__main__":
    config = ExperimentConfig()
    results = run(config)
    print(f"mean_rho={results['mean_rho']:.4f} | PASS={results['pass']}")
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup & Config | File structure, config.py, requirements, GPU setup | 5 | 1+1+1+2 |
| A-2 | Data Loading | GLUE MNLI load/tokenize/batch, 500 examples | 7 | 2+2+1+2 |
| A-3 | LoRA Model + Attention Extraction | Load PeftModel (eager mode), extract per-layer attention scores with fallback | 14 | 3+4+4+3 |
| A-4 | Locret Model + CIS Extraction | Load Locret checkpoint, extract retaining head CIS scores per layer | 15 | 3+4+5+3 |
| A-5 | Spearman Correlation + GQA Expansion | Per-head ρ with KV head expansion, aggregate across layers + examples | 12 | 3+3+4+2 |
| A-6 | Results + Visualization | Bar chart, heatmap, scatter, histogram; JSON save; borderline extension logic | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-5, A-6], Low(4-8): [A-1, A-2]

---

## Module Dependencies

```
run_experiment.py
  ├── config.py
  ├── data_loader.py  ← config
  ├── lora_extractor.py  ← config
  ├── locret_extractor.py  ← config
  ├── correlate.py  ← config
  └── visualize.py  ← config
```

---

## Critical Implementation Notes

- `attn_implementation="eager"` is non-negotiable for LoRA model — disables FlashAttention
- Sequential model loading (LoRA first, unload, then Locret) to stay within ~16GB VRAM
- GQA expansion: `cis_expanded = cis_scores.repeat_interleave(4, dim=0)` before correlation
- Non-padding token masking required in Spearman computation
- Batch size=1 throughout; no batched inference
- Borderline check: if `mean_rho ∈ [0.65, 0.75]`, extend to 500 examples in same run
- Locret loading relies on official `huangyuxiang03/Locret` pattern (`output_retaining_scores=True`)
