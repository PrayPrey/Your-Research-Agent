# Configuration Specification: h-e1

**Date:** 2026-08-25
**Author:** Configuration Agent
**Hypothesis:** h-e1 (EXISTENCE - SciBERT Citation Classification)
**Source:** 02c_experiment_brief.md, 03_prd.md

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Dataclass pattern found in experiments/h-e1/src/config/
**Config Files Found:** experiment_config.py (dataclass with nested configs)
**Pattern Used:** dataclass (standard for this project)

---

## Configuration Schema

EXISTENCE hypothesis - single fixed config (PoC validation only).

```python
# config.py - SciBERT Citation Classification Config

from dataclasses import dataclass

@dataclass
class DataCollectionConfig:
    """ArXiv and Semantic Scholar API parameters."""
    arxiv_query: str = "benchmark OR dataset evaluation"
    max_results: int = 200
    date_range_start: int = 2015
    date_range_end: int = 2024
    citation_threshold: int = 50
    sample_size_min: int = 100
    sample_size_max: int = 200
    random_seed: int = 42

@dataclass
class ModelConfig:
    """SciBERT model configuration."""
    model_name: str = "allenai/scibert_scivocab_uncased"
    num_labels: int = 2
    max_sequence_length: int = 512
    truncation: bool = True
    padding: bool = True

@dataclass
class TrainingConfig:
    """Fine-tuning hyperparameters."""
    optimizer: str = "adamw"
    learning_rate: float = 2e-5
    batch_size: int = 16
    epochs: int = 5
    early_stopping_patience: int = 2
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    random_seed: int = 42

@dataclass
class EvaluationConfig:
    """Evaluation and gating thresholds."""
    train_val_split: float = 0.8
    precision_threshold: float = 0.85
    kappa_threshold: float = 0.80
    target_recall: float = 0.70
    target_f1: float = 0.75

@dataclass
class EnvironmentConfig:
    """Runtime environment."""
    python_version: str = ">=3.8"
    pytorch_version: str = ">=1.10"
    transformers_version: str = ">=4.20"
    scikit_learn_version: str = ">=1.0"
    device: str = "cuda"  # Use cuda if available else cpu

@dataclass
class ExperimentConfig:
    """Root configuration for h-e1 experiment."""
    hypothesis_id: str = "h-e1"
    experiment_name: str = "scibert_citation_classification"
    output_dir: str = "docs/youra_research/h-e1"
    
    data_collection: DataCollectionConfig = None
    model: ModelConfig = None
    training: TrainingConfig = None
    evaluation: EvaluationConfig = None
    environment: EnvironmentConfig = None
    
    def __post_init__(self):
        if self.data_collection is None:
            self.data_collection = DataCollectionConfig()
        if self.model is None:
            self.model = ModelConfig()
        if self.training is None:
            self.training = TrainingConfig()
        if self.evaluation is None:
            self.evaluation = EvaluationConfig()
        if self.environment is None:
            self.environment = EnvironmentConfig()
```

---

## Configuration Rationale

### Data Collection Config

**All values from 02c_experiment_brief.md Section "Dataset":**
- `arxiv_query`: Exact query string specified in brief
- `max_results=200`: Buffer for filtering (target 50-100 after citation filter)
- `date_range`: 2015-2024 per hypothesis scope
- `citation_threshold=50`: Hypothesis constraint (≥50 citations)
- `sample_size`: 100-200 citations per manual annotation protocol
- `random_seed=42`: BERT community standard, ensures reproducibility

### Model Config

**All values from 02c_experiment_brief.md Section "Models - Baseline Model":**
- `model_name`: SciBERT pre-trained checkpoint from HuggingFace
- `num_labels=2`: Binary classification (validation claim vs other)
- `max_sequence_length=512`: BERT max sequence length
- `truncation/padding`: Standard BERT preprocessing

### Training Config

**All values from 02c_experiment_brief.md Section "Training Protocol":**
- `optimizer="adamw"`: BERT best practice (Devlin et al. 2019)
- `learning_rate=2e-5`: BERT fine-tuning standard
- `batch_size=16`: Standard for BERT with small datasets
- `epochs=5`: Max epochs (early stopping prevents overfitting)
- `early_stopping_patience=2`: Stop if no improvement for 2 epochs
- `warmup_ratio=0.1`: 10% of total steps (BERT protocol)
- `weight_decay=0.01`: AdamW standard

### Evaluation Config

**All values from 02c_experiment_brief.md Section "Evaluation":**
- `train_val_split=0.8`: 80/20 split specified in brief
- `precision_threshold=0.85`: PRIMARY gate metric from Phase 2B
- `kappa_threshold=0.80`: SECONDARY gate metric from Phase 2B
- `target_recall=0.70`: Secondary metric from brief
- `target_f1=0.75`: Secondary metric from brief

### Environment Config

**All values from 02c_experiment_brief.md and 03_prd.md TC-1:**
- Version constraints match technical constraints section
- `device="cuda"`: Prefer GPU, fallback to CPU handled at runtime

---

## Usage Example (Phase 4 Coder)

```python
# Initialize config
config = ExperimentConfig()

# Access nested configs
print(config.model.model_name)  # "allenai/scibert_scivocab_uncased"
print(config.training.learning_rate)  # 2e-5
print(config.evaluation.precision_threshold)  # 0.85

# Use in training
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained(config.model.model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    config.model.model_name,
    num_labels=config.model.num_labels
)

# Training args
training_args = TrainingArguments(
    output_dir=config.output_dir,
    learning_rate=config.training.learning_rate,
    per_device_train_batch_size=config.training.batch_size,
    num_train_epochs=config.training.epochs,
    weight_decay=config.training.weight_decay,
    warmup_ratio=config.training.warmup_ratio,
    seed=config.training.random_seed
)
```

---

## Validation Checklist

- [x] ONE format only (Dataclass - consistent with existing codebase)
- [x] No ASCII diagrams
- [x] Codebase Analysis section included
- [x] All values traced to 02c_experiment_brief.md or 03_prd.md
- [x] Rationale only for traceability (all from specs)
- [x] Total length < 400 lines
- [x] EXISTENCE config: Single fixed config, no variations
- [x] Copy-paste ready Python code

---

**Document Status:** FINAL
**Next Phase:** Phase 4 - Implementation
**Dependencies:** transformers>=4.20, torch>=1.10, sklearn>=1.0, arxiv, semanticscholar
