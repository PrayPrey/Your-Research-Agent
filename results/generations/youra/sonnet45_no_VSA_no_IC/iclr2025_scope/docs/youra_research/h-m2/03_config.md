# Configuration Specification — H-M2

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Generated**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m1  
**Config Files Found**: `docs/youra_research/h-m1/code/cache_policy.py`, `docs/youra_research/h-m1/code/retrieval.py`  
**Pattern Used**: dataclass

**Applied**: PyTorch research experiment pattern (dataclass configs with fixed defaults)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From H-M1 Actual Code)

```python
# From: docs/youra_research/h-m1/code/cache_policy.py (ACTUAL CODE)
@dataclass
class ProvenanceCacheConfig:
    cache_budget_ratio: float = 0.25
    top_k_passages: int = 5
    high_rel_count: int = 3
    tier_allocation_high: float = 0.5
    tier_allocation_low: float = 0.5
```

**Verified from**: `docs/youra_research/h-m1/code/cache_policy.py`

---

## H-M2 Configurations

### ProvenanceCache-Full (Diversity-Aware)

```python
@dataclass
class DiversityConfig:
    enabled: bool = True
    lambda_param: float = 0.5
    metric: str = "embedding_cosine"

@dataclass
class ProvenanceCacheDiversityConfig:
    cache_budget_ratio: float = 0.25
    tier_allocation_query: float = 0.10
    tier_allocation_high: float = 0.60
    tier_allocation_low: float = 0.30
    diversity: DiversityConfig = field(default_factory=DiversityConfig)
```

**Changes from H-M1**:
- Split tier allocation into query/high/low (was binary high/low)
- Added diversity config nested dataclass
- Removed `top_k_passages`, `high_rel_count` (derived from tier budgets)

---

### ProvenanceCache-RelevanceOnly (Ablation Baseline)

```python
@dataclass
class ProvenanceCacheRelevanceConfig:
    cache_budget_ratio: float = 0.25
    tier_allocation_query: float = 0.10
    tier_allocation_high: float = 0.60
    tier_allocation_low: float = 0.30
```

**Note**: No diversity scorer, pure relevance ranking within tiers.

---

### Model Configuration

```python
@dataclass
class ModelConfig:
    name: str = "meta-llama/Llama-2-7b-hf"
    precision: str = "fp16"
    max_new_tokens: int = 32
    temperature: float = 0.0
    top_p: float = 1.0
    device: str = "cuda"
```

---

### Retriever Configuration

```python
@dataclass
class RetrieverConfig:
    name: str = "sentence-transformers/contriever-base-msmarco"
    embedding_dim: int = 768
    top_k: int = 10
    chunk_size: int = 512
    chunk_overlap: int = 128
```

---

### Dataset Configuration

```python
@dataclass
class DatasetConfig:
    name: str = "hotpotqa"
    split: str = "dev"
    question_type: str = "bridge"
    data_path: str = "data/hotpot_dev_distractor_v1.json"
    cache_dir: str = "data/cache"
    embeddings_cache_path: str = "data/passage_embeddings_cache.pkl"
```

---

### Evaluation Configuration

```python
@dataclass
class EvaluationConfig:
    metrics: List[str] = field(default_factory=lambda: ["f1", "em", "diversity_coverage", "redundancy_rate"])
    statistical_test: str = "paired_t_test"
    alpha: float = 0.05
    checkpoint_interval: int = 1000
    redundancy_threshold: float = 0.8
```

---

## Ablation Study Configurations

### Lambda Sweep

```python
@dataclass
class LambdaSweepConfig:
    lambda_values: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.7, 0.9])
    base_config: ProvenanceCacheDiversityConfig = field(default_factory=ProvenanceCacheDiversityConfig)
```

**Grid**: 4 runs (λ ∈ {0.3, 0.5, 0.7, 0.9})

---

### Diversity Metric Sweep

```python
@dataclass
class DiversityMetricSweepConfig:
    metrics: List[str] = field(default_factory=lambda: ["embedding_cosine", "entity_jaccard", "lexical_jaccard"])
    base_config: ProvenanceCacheDiversityConfig = field(default_factory=ProvenanceCacheDiversityConfig)
```

**Grid**: 3 runs (embedding cosine, entity overlap, lexical overlap)

---

### Tier Budget Sweep

```python
@dataclass
class TierBudgetSweepConfig:
    allocations: List[Tuple[float, float, float]] = field(default_factory=lambda: [
        (0.10, 0.50, 0.40),  # Balanced
        (0.10, 0.60, 0.30),  # Current (default)
        (0.10, 0.70, 0.20)   # Relevance-heavy
    ])
    base_config: ProvenanceCacheDiversityConfig = field(default_factory=ProvenanceCacheDiversityConfig)
```

**Grid**: 3 runs (tier allocation variants, query budget fixed at 10%)

---

## Experiment Configuration

```python
@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m2"
    seed: int = 42
    output_dir: str = "outputs/h-m2"
    cache_policy: str = "provenance_diversity"  # or "provenance_relevance"
    model: ModelConfig = field(default_factory=ModelConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    cache_config: Union[ProvenanceCacheDiversityConfig, ProvenanceCacheRelevanceConfig] = field(
        default_factory=ProvenanceCacheDiversityConfig
    )
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
```

---

## Validation Rules

### Budget Constraints
```python
def validate_tier_allocation(query: float, high: float, low: float) -> None:
    assert abs(query + high + low - 1.0) < 1e-6, "Tier allocation must sum to 1.0"
    assert 0 < query < 0.2, "Query tier should be 5-20% of budget"
    assert high > low, "High-relevance tier should exceed low-relevance tier"
```

### Lambda Constraints
```python
def validate_lambda(lambda_param: float) -> None:
    assert 0.0 <= lambda_param <= 1.0, "Lambda must be in [0, 1]"
```

### Diversity Metric Validation
```python
def validate_diversity_metric(metric: str) -> None:
    valid_metrics = {"embedding_cosine", "entity_jaccard", "lexical_jaccard"}
    assert metric in valid_metrics, f"Metric must be one of {valid_metrics}"
```

---

## Default Instantiation Examples

### Diversity-Aware Experiment
```python
from dataclasses import dataclass, field
from typing import List, Tuple, Union

diversity_config = ProvenanceCacheDiversityConfig()
model_config = ModelConfig()
retriever_config = RetrieverConfig()
dataset_config = DatasetConfig()
eval_config = EvaluationConfig()

experiment = ExperimentConfig(
    cache_policy="provenance_diversity",
    cache_config=diversity_config
)
```

### Relevance-Only Experiment
```python
relevance_config = ProvenanceCacheRelevanceConfig()
experiment = ExperimentConfig(
    cache_policy="provenance_relevance",
    cache_config=relevance_config
)
```

### Lambda Ablation
```python
lambda_sweep = LambdaSweepConfig()
for lambda_val in lambda_sweep.lambda_values:
    config = ProvenanceCacheDiversityConfig()
    config.diversity.lambda_param = lambda_val
    # Run experiment with config
```

---

## File Paths

**Config modules**: `h-m2/src/configs.py`  
**Usage examples**: See `h-m2/src/run_experiment.py`

---

**Document Status**: READY FOR IMPLEMENTATION  
**Next Phase**: Phase 4 (Implementation)
