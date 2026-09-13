# Configuration Document: h-m2

**Date:** 2026-08-24
**Hypothesis:** Context-aware successor graphs capture task-specific replacement paths via usage-pattern inference, providing more relevant recommendations than linear version-based succession with ≥ 70% context inference accuracy
**Phase:** 3 - Implementation Planning
**Author:** Phase 3 Planning

---

## Configuration Schema

### Experiment Configuration

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class DatasetConfig:
    """Dataset collection configuration."""
    hf_api_endpoint: str = "https://huggingface.co/api/datasets"
    pwc_api_endpoint: str = "https://paperswithcode.com/api/v1/datasets"
    validation_dataset_size: int = 500
    train_test_split: float = 0.7
    random_seed: int = 42

@dataclass
class ContextInferenceConfig:
    """Context inference parameters."""
    pattern_confidence: float = 0.85
    fallback_context: str = "unknown"
    patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        'classification': ['sklearn', 'xgboost', 'lightgbm'],
        'pretraining': ['transformers', 'torchvision.models'],
        'robustness': ['foolbox', 'cleverhans']
    })

@dataclass
class GraphConstructionConfig:
    """Graph construction parameters."""
    edge_precision_threshold: float = 0.6
    citation_patterns: List[str] = field(default_factory=lambda: [
        r"improved version of (.+)",
        r"extends (.+) for (.+) task",
        r"successor to (.+)"
    ])

@dataclass
class EvaluationConfig:
    """Evaluation metric thresholds."""
    context_accuracy_threshold: float = 0.7
    override_rate_threshold: float = 0.5
    edge_precision_threshold: float = 0.6
    statistical_alpha: float = 0.05

@dataclass
class ExperimentConfig:
    """Master experiment configuration."""
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    context_inference: ContextInferenceConfig = field(default_factory=ContextInferenceConfig)
    graph_construction: GraphConstructionConfig = field(default_factory=GraphConstructionConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    output_dir: str = "results"
```

---

## YAML Configuration Example

```yaml
experiment:
  hypothesis_id: h-m2
  hypothesis_type: MECHANISM
  
dataset:
  hf_api_endpoint: "https://huggingface.co/api/datasets"
  pwc_api_endpoint: "https://paperswithcode.com/api/v1/datasets"
  validation_dataset_size: 500
  train_test_split: 0.7
  random_seed: 42

context_inference:
  pattern_confidence: 0.85
  fallback_context: "unknown"
  patterns:
    classification: ["sklearn", "xgboost", "lightgbm"]
    pretraining: ["transformers", "torchvision.models"]
    robustness: ["foolbox", "cleverhans"]

graph_construction:
  edge_precision_threshold: 0.6
  citation_patterns:
    - "improved version of (.+)"
    - "extends (.+) for (.+) task"
    - "successor to (.+)"

evaluation:
  context_accuracy_threshold: 0.7
  override_rate_threshold: 0.5
  edge_precision_threshold: 0.6
  statistical_alpha: 0.05

output:
  results_dir: "results"
  figures_dir: "results/figures"
  metrics_file: "results/metrics.json"
```

---

## Hyperparameter Defaults

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `validation_dataset_size` | 500 | [100, 1000] | Number of labeled validation samples |
| `train_test_split` | 0.7 | [0.6, 0.8] | Proportion of data for training |
| `pattern_confidence` | 0.85 | [0.5, 1.0] | Fixed confidence for pattern matches |
| `edge_precision_threshold` | 0.6 | [0.5, 0.9] | Minimum precision for auto-inferred edges |
| `context_accuracy_threshold` | 0.7 | N/A | Gate threshold (not tunable) |
| `override_rate_threshold` | 0.5 | N/A | Gate threshold (not tunable) |

---

## Dependencies

```python
# requirements.txt
networkx>=2.8
requests>=2.28
scikit-learn>=1.0
matplotlib>=3.5
```

---

## Subtasks

### Dataset Configuration (2)
1. Implement DatasetConfig dataclass with API endpoints
2. Implement validation dataset split configuration

### Context Inference Configuration (2)
1. Implement ContextInferenceConfig with pattern dictionary
2. Add pattern confidence and fallback settings

### Graph Construction Configuration (2)
1. Implement GraphConstructionConfig with citation regex patterns
2. Add edge precision threshold configuration

### Evaluation Configuration (2)
1. Implement EvaluationConfig with all gate thresholds
2. Add statistical test alpha parameter

### Master Configuration (2)
1. Implement ExperimentConfig dataclass aggregating all configs
2. Add YAML serialization/deserialization support

Total: 10 subtasks
