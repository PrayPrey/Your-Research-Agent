# Config: H-M1 — Attention Entropy Mechanistic Analysis

Applied: inference-config-dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual h-e1/code/config.py
**Config Files Found**: `h-e1/code/config.py` — LoRAConfig, TrainingConfig, get_all_configs, validate_config
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-e1/code/config.py)

```python
# From: docs/youra_research/20260504_scope/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])

@dataclass
class TrainingConfig:
    model_name: str = ""
    condition: str = ""
    output_dir: str = ""
    max_seq_length: int = 32768
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 16
    num_train_epochs: int = 1
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    seed: int = 42
    kv_budget_ratio: float = 0.5
    fp16: bool = True
    bf16: bool = False
    dataloader_num_workers: int = 4
    save_strategy: str = "no"
    logging_steps: int = 10
    report_to: str = "none"
    run_name: Optional[str] = None
    lora: LoRAConfig = field(default_factory=LoRAConfig)
```

**Verified from**: `docs/youra_research/20260504_scope/h-e1/code/config.py` (actual implementation)

**Usage in H-M1**: LoRAConfig is reused for loading adapter checkpoints only. TrainingConfig is referenced for adapter checkpoint paths (`outputs/h-e1/{model}-{condition}/`). No training is performed.

---

## H-M1 New Configurations

### Full config.py

```python
import os
from dataclasses import dataclass, field
from typing import List, Optional

os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")

LONGBENCH_TASKS: List[str] = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique",
    "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_count", "passage_retrieval_en", "passage_retrieval_zh",
    "lcc", "repobench-p",
]

LONGBENCH_CATEGORIES = {
    "single-doc-qa":    ["narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh"],
    "multi-doc-qa":     ["hotpotqa", "2wikimqa", "musique", "dureader"],
    "summarization":    ["gov_report", "qmsum", "multi_news", "vcsum"],
    "few-shot":         ["trec", "triviaqa", "samsum", "lsht"],
    "synthetic":        ["passage_count", "passage_retrieval_en", "passage_retrieval_zh"],
    "code":             ["lcc", "repobench-p"],
}


@dataclass
class InferenceConfig:
    model_name: str = ""
    adapter_checkpoint: str = ""
    condition: str = ""                  # "eviction-aware" | "baseline"
    kv_budget_ratio: float = 0.5
    heavy_ratio: float = 0.1
    recent_ratio: float = 0.1
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    top_ratio: float = 0.2               # heavy-hitter top-20% threshold
    output_dir: str = ""


@dataclass
class ExperimentConfig:
    experiment_id: str = "h-m1"
    longbench_tasks: List[str] = field(default_factory=lambda: LONGBENCH_TASKS)
    min_samples_per_category: int = 500
    significance_threshold: float = 0.05
    gate_layer_fraction: float = 0.5     # >=50% layers must pass
    figures_dir: str = "h-m1/figures"
    results_dir: str = "h-m1/results"
    models: List[InferenceConfig] = field(default_factory=list)


def get_experiment_config() -> ExperimentConfig:
    BASE_ADAPTER = "outputs/h-e1"
    models = [
        InferenceConfig(
            model_name="meta-llama/Llama-2-7b-hf",
            adapter_checkpoint=f"{BASE_ADAPTER}/llama2-7b-baseline",
            condition="baseline",
            output_dir="h-m1/results/llama2-7b-baseline",
        ),
        InferenceConfig(
            model_name="meta-llama/Llama-2-7b-hf",
            adapter_checkpoint=f"{BASE_ADAPTER}/llama2-7b-eviction-aware",
            condition="eviction-aware",
            output_dir="h-m1/results/llama2-7b-eviction-aware",
        ),
        InferenceConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            adapter_checkpoint=f"{BASE_ADAPTER}/mistral-7b-baseline",
            condition="baseline",
            output_dir="h-m1/results/mistral-7b-baseline",
        ),
        InferenceConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            adapter_checkpoint=f"{BASE_ADAPTER}/mistral-7b-eviction-aware",
            condition="eviction-aware",
            output_dir="h-m1/results/mistral-7b-eviction-aware",
        ),
    ]
    return ExperimentConfig(models=models)


def validate_config(cfg: ExperimentConfig) -> None:
    assert cfg.significance_threshold > 0.0, "significance_threshold must be > 0"
    assert 0.0 < cfg.gate_layer_fraction <= 1.0, "gate_layer_fraction must be in (0, 1]"
    assert len(cfg.longbench_tasks) > 0, "longbench_tasks must not be empty"
    for m in cfg.models:
        assert m.model_name != "", "model_name must be set"
        assert m.condition in ("baseline", "eviction-aware"), \
            f"condition must be 'baseline' or 'eviction-aware', got: {m.condition}"
        assert 0.0 < m.kv_budget_ratio < 1.0, \
            f"kv_budget_ratio must be in (0, 1), got: {m.kv_budget_ratio}"
        assert 0.0 < m.top_ratio <= 1.0, \
            f"top_ratio must be in (0, 1], got: {m.top_ratio}"
        os.makedirs(m.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.results_dir, exist_ok=True)
```

---

## A-2: LongBench Data Loader [Complexity: 13, Budget: 2 subtasks]

Applied: inference-config-dataclass pattern

**Config fields used**: `ExperimentConfig.longbench_tasks`, `ExperimentConfig.min_samples_per_category`, `InferenceConfig.max_seq_length`

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Task Loading | load_task per task name via HuggingFace datasets; category mapping via LONGBENCH_CATEGORIES |
| C-2-2 | Tokenization + Truncation | tokenize_sample with middle truncation: keep first 1000 + last 3000 tokens up to max_seq_length=4096 |

---

## A-5: Metrics Aggregation [Complexity: 12, Budget: 1 subtask]

Applied: inference-config-dataclass pattern

**Config fields used**: `ExperimentConfig.significance_threshold`, `ExperimentConfig.gate_layer_fraction`

**Data classes used in analyze.py** (not config.py — no hyperparameters to tune):

```python
@dataclass
class LayerMetrics:
    layer_idx: int
    baseline_entropy: List[float]
    proposed_entropy: List[float]
    baseline_hh_concentration: List[float]
    proposed_hh_concentration: List[float]
    n_samples: int

@dataclass
class StatisticalResult:
    layer_idx: int
    entropy_pvalue: float
    entropy_statistic: float
    entropy_mean_diff: float
    hh_pvalue: float
    hh_statistic: float
    hh_mean_diff: float
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Aggregator + Serialization | MetricsAggregator.add_sample, get_layer_metrics, save/load (JSON or pickle) |

---

## A-8: Visualization [Complexity: 12, Budget: 1 subtask]

Applied: inference-config-dataclass pattern

**Config fields used**: `ExperimentConfig.figures_dir`, `ExperimentConfig.significance_threshold`

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Five Figures | plot_entropy_per_layer, plot_hh_concentration, plot_pvalue_heatmap, plot_entropy_by_category, plot_gate_summary — all save to figures_dir |
