# Architecture: H-M1 — Attention Entropy Mechanistic Analysis

**Applied**: attention-entropy-mechanistic-analysis pattern
**Applied**: paired-ttest-layer-comparison pattern
**Applied**: longbench-evaluation-protocol pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (h-e1/code/)
**Analyzed Path**: `docs/youra_research/20260504_scope/h-e1/code/`
**Findings**: H-E1 provides H2OEvictionAwareAttention, inject_h2o_wrappers, load_base_model, build_model, LoRAConfig, TrainingConfig, LongAlpacaDataset. No attention extraction, LongBench loading, or statistical analysis modules exist — all new in H-M1.

---

## Overview

H-M1 is an inference-only analysis experiment. No re-training. New code adds:
- LongBench dataset loading (21 tasks, 6 categories)
- Attention weight extraction via `output_attentions=True`
- Per-layer entropy and heavy-hitter concentration computation
- Paired t-test across samples, per layer
- Visualization (line plots, heatmaps, box plots)

H-E1 adapter checkpoints (eviction-aware + sequential baseline) for LLaMA-2-7B and Mistral-7B-v0.1 are loaded directly.

---

## File Organization

- `h-m1/code/config.py` — InferenceConfig, ExperimentConfig dataclasses
- `h-m1/code/data.py` — LongBenchDataLoader
- `h-m1/code/model.py` — load_adapter_model, AttentionAnalysisExtractor
- `h-m1/code/analyze.py` — StatisticalAnalyzer, MetricsAggregator
- `h-m1/code/evaluate.py` — run_inference_condition, collect_layer_metrics
- `h-m1/code/visualize.py` — plot_entropy_per_layer, plot_hh_concentration, plot_pvalue_heatmap, plot_entropy_by_category
- `h-m1/code/run_experiment.py` — main entry point
- `h-m1/code/tests/` — unit tests
- `h-m1/figures/` — saved figures

---

## Module Definitions

### InferenceConfig / ExperimentConfig (`h-m1/code/config.py`)

**Dependencies**: dataclasses, typing

```python
@dataclass
class InferenceConfig:
    model_name: str = ""
    adapter_checkpoint: str = ""
    condition: str = ""           # "eviction-aware" | "baseline"
    kv_budget_ratio: float = 0.5
    heavy_ratio: float = 0.1
    recent_ratio: float = 0.1
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    top_ratio: float = 0.2        # heavy-hitter top-20% threshold
    output_dir: str = ""

@dataclass
class ExperimentConfig:
    experiment_id: str = "h-m1"
    longbench_tasks: List[str] = field(default_factory=list)  # 21 task names
    min_samples_per_category: int = 500
    significance_threshold: float = 0.05
    gate_layer_fraction: float = 0.5    # >=50% layers must pass
    figures_dir: str = "h-m1/figures"
    results_dir: str = "h-m1/results"
    models: List[InferenceConfig] = field(default_factory=list)

def get_experiment_config() -> ExperimentConfig: ...
def validate_config(cfg: ExperimentConfig) -> None: ...
```

---

### LongBenchDataLoader (`h-m1/code/data.py`)

**Dependencies**: datasets, transformers, torch

```python
LONGBENCH_TASKS: List[str]   # 21 task names, module-level constant
LONGBENCH_CATEGORIES: Dict[str, List[str]]  # category -> [task names]

class LongBenchDataLoader:
    def __init__(
        self,
        tokenizer,
        max_seq_length: int = 4096,
        tasks: Optional[List[str]] = None,
    ): ...

    def load_task(self, task_name: str) -> Dataset: ...

    def get_category_samples(
        self,
        category: str,
        min_samples: int = 500,
    ) -> List[dict]: ...
    # Aggregates across tasks in category until >= min_samples

    def tokenize_sample(self, sample: dict, task_name: str) -> dict:
        # Returns: {input_ids, attention_mask, task, category, sample_id}
        # Middle truncation: keep first 1000 + last 3000 tokens
        ...

    def iter_all_samples(self) -> Iterator[dict]: ...
    # Yields tokenized samples across all 21 tasks
```

---

### AttentionAnalysisExtractor (`h-m1/code/model.py`)

**Dependencies**: torch, transformers, peft, h-e1/code/model.py (H2OEvictionAwareAttention, inject_h2o_wrappers, load_base_model)

```python
def load_adapter_model(
    model_name: str,
    adapter_checkpoint: str,
    condition: str,
    kv_budget_ratio: float = 0.5,
    fp16: bool = True,
) -> nn.Module:
    # Loads base model, optionally injects H2O wrappers, applies PEFT adapter
    # condition: "eviction-aware" injects H2O wrappers at inference; "baseline" does not
    ...

class AttentionAnalysisExtractor:
    def __init__(self, model: nn.Module, top_ratio: float = 0.2): ...

    def verify_attention_extraction(
        self, tokenizer, device: str, max_length: int = 512
    ) -> None:
        # Smoke test: checks output_attentions=True shape and softmax normalization
        ...

    def extract_metrics(
        self,
        input_ids: torch.Tensor,       # (1, seq_len)
        attention_mask: torch.Tensor,  # (1, seq_len)
    ) -> Tuple[List[float], List[float]]:
        # Returns: (entropy_per_layer, hh_concentration_per_layer)
        # Each list has length == num_hidden_layers
        ...

    @staticmethod
    def compute_entropy(attn_weights: torch.Tensor) -> float:
        # attn_weights: (B, H, S, S); returns scalar
        ...

    @staticmethod
    def compute_hh_concentration(
        attn_weights: torch.Tensor, top_ratio: float = 0.2
    ) -> float:
        # attn_weights: (B, H, S, S); returns scalar
        ...
```

---

### StatisticalAnalyzer / MetricsAggregator (`h-m1/code/analyze.py`)

**Dependencies**: numpy, scipy.stats, typing

```python
@dataclass
class LayerMetrics:
    layer_idx: int
    baseline_entropy: List[float]        # one value per sample
    proposed_entropy: List[float]
    baseline_hh_concentration: List[float]
    proposed_hh_concentration: List[float]
    n_samples: int

@dataclass
class StatisticalResult:
    layer_idx: int
    entropy_pvalue: float
    entropy_statistic: float
    entropy_mean_diff: float             # proposed - baseline
    hh_pvalue: float
    hh_statistic: float
    hh_mean_diff: float

class MetricsAggregator:
    def __init__(self, num_layers: int): ...

    def add_sample(
        self,
        condition: str,                  # "baseline" | "eviction-aware"
        entropy_per_layer: List[float],
        hh_per_layer: List[float],
        task: str,
        category: str,
    ) -> None: ...

    def get_layer_metrics(self) -> List[LayerMetrics]: ...

    def save(self, path: str) -> None: ...

    @classmethod
    def load(cls, path: str) -> "MetricsAggregator": ...

class StatisticalAnalyzer:
    def run_paired_ttest(
        self, layer_metrics: List[LayerMetrics]
    ) -> List[StatisticalResult]: ...

    def compute_gate_result(
        self,
        results: List[StatisticalResult],
        significance_threshold: float = 0.05,
        gate_fraction: float = 0.5,
    ) -> dict:
        # Returns: {passed: bool, fraction_significant: float, significant_layers: List[int]}
        ...

    def summarize(
        self, results: List[StatisticalResult]
    ) -> dict: ...
```

---

### Evaluation Runner (`h-m1/code/evaluate.py`)

**Dependencies**: torch, config, data, model, analyze

```python
def run_inference_condition(
    extractor: AttentionAnalysisExtractor,
    dataloader: LongBenchDataLoader,
    aggregator: MetricsAggregator,
    condition: str,
    device: str,
    min_samples_per_category: int = 500,
) -> MetricsAggregator:
    # Iterates LongBench samples, calls extractor.extract_metrics, feeds aggregator
    ...

def collect_layer_metrics(
    baseline_cfg: InferenceConfig,
    proposed_cfg: InferenceConfig,
    experiment_cfg: ExperimentConfig,
    device: str,
) -> MetricsAggregator:
    # Loads both adapter models, runs both conditions, returns aggregated metrics
    ...

def run_evaluation(
    experiment_cfg: ExperimentConfig,
    device: str,
) -> dict:
    # Full pipeline: collect metrics -> statistical analysis -> gate check
    # Returns results dict with gate pass/fail
    ...
```

---

### Visualizer (`h-m1/code/visualize.py`)

**Dependencies**: matplotlib, numpy, analyze

```python
def plot_entropy_per_layer(
    results: List[StatisticalResult],
    aggregator: MetricsAggregator,
    model_label: str,
    save_path: str,
) -> None: ...
# Line plot: entropy per layer for both conditions with SE shading; p<0.05 marked

def plot_hh_concentration(
    results: List[StatisticalResult],
    aggregator: MetricsAggregator,
    model_label: str,
    save_path: str,
) -> None: ...
# Line plot: HH concentration per layer; asterisks at significant layers

def plot_pvalue_heatmap(
    results: List[StatisticalResult],
    save_path: str,
) -> None: ...
# Heatmap: layer x metric (-log10 p-value); p=0.05 threshold line

def plot_entropy_by_category(
    aggregator: MetricsAggregator,
    save_path: str,
) -> None: ...
# Box plot: entropy distribution per LongBench category, both conditions

def plot_gate_summary(
    gate_result: dict,
    save_path: str,
) -> None: ...
# Bar chart: % layers with p<0.05; target line at 50%
```

---

### Run Experiment (`h-m1/code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    # Parses args, sets CUDA_VISIBLE_DEVICES, calls run_evaluation, saves results, calls visualizers
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H2OEvictionAwareAttention | `sys.path.insert + from model import H2OEvictionAwareAttention` | `h-e1/code/model.py` |
| inject_h2o_wrappers | `from model import inject_h2o_wrappers` | `h-e1/code/model.py` |
| load_base_model | `from model import load_base_model` | `h-e1/code/model.py` |
| LoRAConfig | `from config import LoRAConfig` | `h-e1/code/config.py` |
| TrainingConfig | `from config import TrainingConfig` | `h-e1/code/config.py` |
| LongAlpacaDataset | `from data import LongAlpacaDataset` | `h-e1/code/data.py` (not reused in H-M1 — LongBench replaces it) |

**Verified from**: `docs/youra_research/20260504_scope/h-e1/code/` (actual implementation)

**Notes on H-E1 code:**
- `load_base_model` uses bfloat16 if supported, else float16 — H-M1 must match
- `inject_h2o_wrappers` replaces LlamaAttention/MistralAttention — H-M1 inference uses same wrappers
- `H2OEvictionAwareAttention.forward` passes through to base_attention when `not self.training` — H-M1 sets model to eval mode; H2O eviction at inference must be handled separately (via past_key_values or separate H2OKVCache)
- Adapter checkpoints saved at `outputs/h-e1/{model}-{condition}/` by H-E1 config

**Critical inference note**: H-E1's H2OEvictionAwareAttention only applies eviction mask during training (`if not self.training: return self.base_attention(...)`). For H-M1 inference-time H2O eviction, `load_adapter_model` must either (a) keep model in train mode for eviction (not recommended) or (b) use a separate H2OKVCache implementation for inference-time KV eviction. The architecture design in `load_adapter_model` must resolve this — recommended approach: use FMInference/H2O `H2OKVCache` for inference-time eviction, applied identically to both conditions.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config Setup | InferenceConfig, ExperimentConfig, get_experiment_config, validate_config | 7 | 1+2+2+2 |
| A-2 | LongBench Data Loader | LongBenchDataLoader with 21 tasks, category aggregation, middle truncation | 13 | 3+3+4+3 |
| A-3 | Adapter Model Loading | load_adapter_model with H2O inference-time eviction (H2OKVCache integration) | 16 | 4+4+4+4 |
| A-4 | Attention Extraction | AttentionAnalysisExtractor: extract_metrics, compute_entropy, compute_hh_concentration, smoke test | 15 | 4+3+4+4 |
| A-5 | Metrics Aggregation | MetricsAggregator: per-sample accumulation, task/category tracking, save/load | 12 | 3+3+3+3 |
| A-6 | Statistical Analysis | StatisticalAnalyzer: paired t-test per layer, gate result computation, summary | 14 | 3+3+4+4 |
| A-7 | Evaluation Runner | run_inference_condition, collect_layer_metrics, run_evaluation pipeline | 15 | 3+4+4+4 |
| A-8 | Visualization | 5 figures: entropy line plot, HH line plot, p-value heatmap, category box plot, gate bar chart | 12 | 3+2+4+3 |
| A-9 | Run Experiment Entry | main(), arg parsing, CUDA setup, full pipeline orchestration, results saving | 9 | 2+2+3+2 |
| A-10 | Unit Tests | Tests for config, data loading, entropy computation, statistical test correctness | 10 | 2+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4, A-6, A-7], Medium(9-13): [A-2, A-5, A-8, A-10], Low(4-8): [A-1, A-9]

**Total Complexity**: 123 across 10 tasks
