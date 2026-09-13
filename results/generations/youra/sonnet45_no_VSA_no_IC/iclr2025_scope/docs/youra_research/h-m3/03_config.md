# Configuration for H-M3 Query Complexity Attention Analysis

**Hypothesis**: h-m3  
**Type**: EXISTENCE (PoC)  
**Date**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-e1)  
**Status**: Config verified from h-e1 archived code  
**Config Files Found**: h-e1/code/config.py (dataclass pattern)  
**Pattern Used**: Dataclass (matching h-e1)

---

## Applied Pattern

**Applied**: Dataclass pattern from h-e1, Standard PyTorch defaults

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-e1 Actual Code)

```python
# Verified from: docs/youra_research/_archive/20260820T012415_routing_recovery/h-e1/code/config.py
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-2.8b-hf"
    max_context_length: int = 8192
    
    # Data
    dataset_name: str = "THUDM/LongBench"
    task_name: str = "narrativeqa"
    
    # Reproducibility
    seed: int = 42
    
    # Compute
    device: str = "cpu"
    
    # Evaluation
    eval_samples: int = 10
```

**Note**: H-M3 uses Llama-2-7B (not Mamba) but inherits dataset source and seed pattern.

---

## M1: Entity Classifier [Complexity: 8, Budget: 2]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ComplexityConfig:
    spacy_model: str = "en_core_web_sm"
    simple_word_count_max: int = 10
    simple_entity_density_max: float = 0.3
    min_samples_per_stratum: int = 100
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-1 | spaCy integration | Load NER model, extract entities |
| M1-2 | Density computation + classification | Compute entity_density, apply thresholds |

---

## M2: Attention Extraction Reuse [Complexity: 10, Budget: 0]

**Inherited from h-e1** - No new config needed. Uses h-e1's AttentionCollector with:
- `output_attentions=True`
- `attn_implementation="eager"`
- `target_layer=-1`

---

## M3: Stratification Pipeline [Complexity: 7, Budget: 0]

**No config needed** - Applies ComplexityConfig thresholds from M1.

---

## M4: Concentration Metrics [Complexity: 9, Budget: 0]

**No config needed** - Standard attention aggregation:
- Aggregation: Mean across heads
- Metric: query_attn_mass / total_attn_mass

---

## M5: Statistical Testing [Complexity: 11, Budget: 0]

### Configuration (Python Dataclass)

```python
@dataclass
class StatisticalConfig:
    test_type: str = "two_sample_t_test"
    alternative: str = "greater"  # simple > complex
    alpha: float = 0.05
    bootstrap_samples: int = 1000
    bootstrap_seed: int = 42
```

**Note**: EXISTENCE PoC uses single test, no hyperparameter grid.

---

## M6: Visualization + Report [Complexity: 10, Budget: 0]

**No config needed** - Fixed visualization settings:
- Bar chart with error bars
- 95% confidence intervals
- Output: `h-m3/outputs/results/figures/`

---

## Master Experiment Config

```python
from dataclasses import dataclass, field

@dataclass
class H_M3_Config:
    # Model (from h-e1 pattern, switched to Llama)
    model_id: str = "meta-llama/Llama-2-7b-hf"
    device: str = "cuda"
    output_attentions: bool = True
    attn_implementation: str = "eager"
    
    # Dataset (inherited from h-e1)
    dataset_name: str = "THUDM/LongBench"
    tasks: list[str] = field(default_factory=lambda: ["hotpotqa", "2wikimqa", "musique"])
    total_samples: int = 600
    
    # Complexity classification
    complexity: ComplexityConfig = field(default_factory=ComplexityConfig)
    
    # Statistical testing
    stats: StatisticalConfig = field(default_factory=StatisticalConfig)
    
    # Reproducibility (inherited from h-e1)
    seed: int = 42
    
    # Outputs
    output_dir: str = "h-m3/outputs"
    save_interval: int = 100
```

---

## Validation Rules

```python
VALIDATION_RULES = {
    "model_has_attention": lambda cfg: cfg.output_attentions is True,
    "eager_implementation": lambda cfg: cfg.attn_implementation == "eager",
    "sufficient_samples": lambda cfg: cfg.total_samples >= 600,
    "strata_balanced": lambda cfg: cfg.complexity.min_samples_per_stratum >= 100,
    "seed_fixed": lambda cfg: cfg.seed is not None,
}
```

---

**Config Status**: COMPLETE  
**Subtasks Used**: 2/2  
**Format**: Dataclass (matches h-e1)
