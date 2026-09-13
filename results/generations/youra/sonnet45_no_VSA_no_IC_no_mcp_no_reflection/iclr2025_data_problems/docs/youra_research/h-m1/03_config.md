# Configuration Specification
# Hypothesis H-M1: Data Curation Causally Increases Information Density

**Version**: 1.0
**Created**: 2026-08-28
**Hypothesis ID**: h-m1
**Type**: MECHANISM (extending h-e1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code
**Config Files Found**: h-e1/code/config.py (hardcoded dict)
**Pattern Used**: Dataclass (MECHANISM hypothesis standard)

---

## Applied Patterns

Applied: Dataclass config with nested modules (standard PyTorch training pattern)
Applied: Fractional factorial experimental design (9 conditions from 3^3 grid)

---

## Inherited Configuration (Base Hypothesis)

### Config from H-E1 (Actual Code)

H-E1 used hardcoded dict format. Key values verified from actual implementation:

```python
# From: h-e1/code/config.py (ACTUAL CODE)
H_E1_CONFIG = {
    "dataset_name": "allenai/c4",
    "dataset_split": "en",
    "subset_size_gb": 10,
    "seed": 42,
    "device": "cuda",
    "perplexity_model": "gpt2",
    "ngram_size": 13
}
```

**Reused for H-M1**: dataset source, seed, device, perplexity model for filtering
**Changed for H-M1**: subset_size_gb (10 → 50), added training hyperparameters

---

## Configuration (Python Dataclass)

```python
# config.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DatasetConfig:
    name: str = "allenai/c4"
    split: str = "en"
    subset_size_gb: int = 50
    num_conditions: int = 9
    cache_dir: str = "data/curated/"
    
@dataclass
class DeduplicationConfig:
    method: str = "minhash_lsh"
    num_perm: int = 128
    jaccard_threshold: float = 0.8
    
@dataclass
class FilteringConfig:
    model_name: str = "gpt2"
    batch_size: int = 128
    levels: Dict[int, str] = None
    
    def __post_init__(self):
        if self.levels is None:
            self.levels = {
                0: None,
                1: "median",
                2: "top25"
            }

@dataclass
class DomainMixConfig:
    strategies: Dict[int, str] = None
    
    def __post_init__(self):
        if self.strategies is None:
            self.strategies = {
                0: "uniform",
                1: "quality_weighted"
            }

@dataclass
class CurationCondition:
    name: str
    dedup_ratio: float
    filter_level: int
    domain_mix: int

@dataclass
class CurationConfig:
    dedup: DeduplicationConfig = None
    filtering: FilteringConfig = None
    domain_mix: DomainMixConfig = None
    conditions: List[CurationCondition] = None
    
    def __post_init__(self):
        if self.dedup is None:
            self.dedup = DeduplicationConfig()
        if self.filtering is None:
            self.filtering = FilteringConfig()
        if self.domain_mix is None:
            self.domain_mix = DomainMixConfig()
        if self.conditions is None:
            self.conditions = [
                CurationCondition("baseline", 0.0, 0, 0),
                CurationCondition("dedup_low", 0.5, 0, 0),
                CurationCondition("dedup_high", 0.95, 0, 0),
                CurationCondition("filter_med", 0.0, 1, 0),
                CurationCondition("filter_high", 0.0, 2, 0),
                CurationCondition("mix_only", 0.0, 0, 1),
                CurationCondition("dedup_filter", 0.95, 2, 0),
                CurationCondition("dedup_mix", 0.95, 0, 1),
                CurationCondition("full_curation", 0.95, 2, 1)
            ]

@dataclass
class TrainingConfig:
    model_name: str = "gpt2"
    batch_size: int = 256
    micro_batch_size: int = 32
    gradient_accumulation_steps: int = 8
    learning_rate: float = 6e-4
    warmup_steps: int = 2000
    total_steps: int = 50000
    optimizer: str = "adamw"
    adam_beta1: float = 0.9
    adam_beta2: float = 0.95
    adam_eps: float = 1e-8
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    dropout: float = 0.1
    seed: int = 42
    log_interval: int = 100
    checkpoint_interval: int = 5000
    device: str = "cuda"
    output_dir: str = "results/checkpoints/"

@dataclass
class DensityMetricsConfig:
    compute_entropy: bool = True
    compute_fisher: bool = True
    log_interval: int = 100
    vocab_size: int = 50257

@dataclass
class EvaluationConfig:
    entropy_reduction_threshold: float = 0.20
    fisher_increase_threshold: float = 0.15
    monotonicity_required: bool = True
    output_dir: str = "results/"
    plots_dir: str = "results/plots/"

@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = None
    curation: CurationConfig = None
    training: TrainingConfig = None
    density_metrics: DensityMetricsConfig = None
    evaluation: EvaluationConfig = None
    
    def __post_init__(self):
        if self.dataset is None:
            self.dataset = DatasetConfig()
        if self.curation is None:
            self.curation = CurationConfig()
        if self.training is None:
            self.training = TrainingConfig()
        if self.density_metrics is None:
            self.density_metrics = DensityMetricsConfig()
        if self.evaluation is None:
            self.evaluation = EvaluationConfig()

CONFIG = ExperimentConfig()
```

---

## Rationale (Non-Standard Values Only)

**num_perm=128**: MinHash LSH standard (datasketch default)
**jaccard_threshold=0.8**: Common dedup threshold in literature (Lee et al. 2021)
**subset_size_gb=50**: 5x larger than h-e1 to provide sufficient training tokens (10B tokens)
**gradient_accumulation_steps=8**: Achieves 256 effective batch size on single V100 (32 micro-batch)

---

## Epic Tasks with Subtask Allocation

### M-1: Curation Infrastructure [Complexity: 14, Budget: 1/7]

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | MinHash LSH implementation | Integrate datasketch for deduplication |

**Config**: `CurationConfig.dedup`, `DeduplicationConfig`

---

### M-2: Density Analyzer [Complexity: 11, Budget: 1/7]

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | Entropy + Fisher hooks | Implement forward/backward metric computation |

**Config**: `DensityMetricsConfig`, `TrainingConfig.log_interval`

---

### M-3: Dataset Generation [Complexity: 9, Budget: 1/7]

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | Generate 9 curated subsets | Apply conditions and save to disk |

**Config**: `DatasetConfig`, `CurationConfig.conditions`

---

### M-4: Training Pipeline [Complexity: 12, Budget: 2/7]

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | GPT-2 training loop | Standard AdamW optimizer with metric logging |
| M-4-2 | Checkpointing | Save model every 5000 steps |

**Config**: `TrainingConfig`

---

### M-5: Condition Execution [Complexity: 10, Budget: 1/7]

| ID | Subtask | Description |
|----|---------|-------------|
| M-5-1 | Orchestrate 9 conditions | Sequential or parallel execution |

**Config**: `ExperimentConfig` (top-level orchestration)

---

### M-6: Gate Evaluation [Complexity: 13, Budget: 1/7]

| ID | Subtask | Description |
|----|---------|-------------|
| M-6-1 | Compute gate metrics | Entropy reduction, Fisher increase, monotonicity |

**Config**: `EvaluationConfig`

---

## Gate Decision Logic

```python
# Embedded in evaluate.py
def check_gate(metrics_log: pd.DataFrame, config: EvaluationConfig) -> str:
    baseline = metrics_log[metrics_log['condition'] == 'baseline'].iloc[-1]
    full_curation = metrics_log[metrics_log['condition'] == 'full_curation'].iloc[-1]
    
    entropy_reduction = (baseline['entropy'] - full_curation['entropy']) / baseline['entropy']
    fisher_increase = (full_curation['fisher_trace'] - baseline['fisher_trace']) / baseline['fisher_trace']
    
    dedup_conditions = ['baseline', 'dedup_low', 'dedup_high']
    dedup_entropies = [metrics_log[metrics_log['condition'] == c].iloc[-1]['entropy'] for c in dedup_conditions]
    dedup_monotonic = all(dedup_entropies[i] >= dedup_entropies[i+1] for i in range(len(dedup_entropies)-1))
    
    filter_conditions = ['baseline', 'filter_med', 'filter_high']
    filter_entropies = [metrics_log[metrics_log['condition'] == c].iloc[-1]['entropy'] for c in filter_conditions]
    filter_monotonic = all(filter_entropies[i] >= filter_entropies[i+1] for i in range(len(filter_entropies)-1))
    
    mix_conditions = ['baseline', 'mix_only']
    mix_entropies = [metrics_log[metrics_log['condition'] == c].iloc[-1]['entropy'] for c in mix_conditions]
    mix_monotonic = mix_entropies[0] >= mix_entropies[1]
    
    monotonicity = dedup_monotonic and filter_monotonic and mix_monotonic
    
    if (entropy_reduction > config.entropy_reduction_threshold and 
        fisher_increase > config.fisher_increase_threshold and 
        (monotonicity or not config.monotonicity_required)):
        return "PASS"
    elif entropy_reduction > 0.10 or fisher_increase > 0.10:
        return "PARTIAL"
    else:
        return "FAIL"
```

---

**END OF CONFIG**
