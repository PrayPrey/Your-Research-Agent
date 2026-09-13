# Configuration Specification: h-m1 - Stratified Training Mechanism

**Date:** 2026-07-12  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (PoC)  
**Config Designer:** configuration-agent  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from H-E1 code  
**Config Files Found:** `h-e1/code/run_experiment.py` (lines 38-69)  
**Pattern Used:** Hardcoded dict (consistent with base hypothesis)  

---

## Knowledge Base Integration

**Applied:** Standard PyTorch/HuggingFace defaults for DL experiments

---

## Configuration Philosophy

**PoC Strategy:** Single fixed configuration to test "does stratified training enable factual density learning?"
- No hyperparameter grid (MECHANISM hypothesis)
- No ablation configs
- Fixed seed=42
- Default values inherited from H-E1 where applicable

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from H-E1 (verified from `h-e1/code/run_experiment.py`):

```python
# From: h-e1/code/run_experiment.py (lines 38-69)
BASE_CONFIG = {
    "experiment": {
        "hypothesis_id": "h-e1",
        "type": "EXISTENCE",
        "seed": 42,
        "description": "Retrieval-quality corpus filtering validation"
    },
    "data": {
        "beir_dataset": "nq",
        "beir_split": "test",
        "corpus_sample_size": 10000,
        "eval_queries": 500,
    },
    "models": {
        "dpr_model": "facebook/dpr-ctx_encoder-single-nq-base",
        "perplexity_model": "gpt2",
    },
    "classifier": {
        "dim": 100,
        "lr": 0.1,
        "epoch": 25,
        "wordNgrams": 2,
        "train_samples_per_class": 500,
    },
    "evaluation": {
        "k": 10,
        "gate_threshold": 0.03,
        "target_corpus_size": 5000,
    },
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}
```

**Verified from:** `h-e1/code/run_experiment.py` (actual implementation)

---

## M-1: Data Infrastructure (Complexity: 9, Budget: 1)

### Configuration

```python
DATA_CONFIG = {
    "seed": 42,
    "beir": {
        "dataset": "nq",
        "split": "test",
        "url": "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nq.zip"
    },
    "corpus": {
        "sample_size": 100000,
        "target_size": 50000
    },
    "training_data": {
        "samples_per_class": 500,
        "min_length": 50,
        "max_length": 1000
    },
    "perplexity": {
        "model_name": "gpt2",
        "batch_size": 16,
        "max_length": 512,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    },
    "output_paths": {
        "beir_data": "data/beir/nq/",
        "training_examples": "data/training_examples.json",
        "educational_scores": "data/educational_scores.npy",
        "beir_scores": "data/beir_scores.npy"
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | BEIR + perplexity scorer | BEIR loader, training data extraction, educational quality scoring |

---

## M-4: Perplexity Baseline (Complexity: 9, Budget: 1)

### Configuration

```python
BASELINE_CONFIG = {
    "perplexity": {
        "model_name": "gpt2",
        "batch_size": 16,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "max_length": 512,
        "truncation": True
    },
    "selection": {
        "target_size": 50000,
        "method": "lowest_perplexity"
    },
    "output_paths": {
        "perplexity_scores": "outputs/perplexity_scores.npy",
        "baseline_corpus_ids": "outputs/baseline_corpus_ids.json"
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Perplexity scoring + selection | Compute perplexity for 100K docs, select top-50K |

---

## M-7: Visualization (Complexity: 10, Budget: 2)

### Configuration

```python
VISUALIZATION_CONFIG = {
    "figures": {
        "dpi": 300,
        "formats": ["png", "pdf"],
        "output_dir": "figures/",
        "style": "seaborn-v0_8-paper"
    },
    "figure_1_entity_density": {
        "figsize": (8, 6),
        "title": "Named Entity Density Comparison",
        "xlabel": "Method",
        "ylabel": "Entities per 100 tokens",
        "threshold": 1.15,
        "colors": ["#1f77b4", "#ff7f0e"]
    },
    "figure_2_entity_types": {
        "figsize": (10, 6),
        "title": "Entity Type Distribution",
        "types": ["PERSON", "ORG", "GPE", "DATE", "MONEY", "LOC", "PRODUCT"]
    },
    "figure_3_stratification": {
        "figsize": (10, 8),
        "title": "Stratification Effect: Educational vs BEIR Quality",
        "xlabel": "Educational Quality (1/Perplexity)",
        "ylabel": "BEIR Quality (Relevance Score)",
        "alpha": 0.5,
        "highlight_color": "#ff0000"
    },
    "figure_4_doc_stats": {
        "figsize": (10, 6),
        "title": "Document Statistics Comparison",
        "metrics": ["length", "ttr", "entity_diversity"]
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Mandatory figure (entity density) | Bar chart with threshold line |
| C-7-2 | Analysis figures (types, stratification, stats) | 3 additional figures for mechanism validation |

---

## M-8: Integration (Complexity: 9, Budget: 1)

### Configuration

```python
INTEGRATION_CONFIG = {
    "pipeline": {
        "stages": [
            "data_acquisition",
            "extract_training_data",
            "stratified_sampling",
            "train_classifier",
            "baseline_selection",
            "proposed_selection",
            "entity_evaluation",
            "visualization"
        ],
        "checkpoint_dir": "checkpoints/",
        "resume_from_checkpoint": True
    },
    "logging": {
        "level": "INFO",
        "console": True,
        "file": "logs/experiment.log",
        "format": "%(asctime)s - %(levelname)s - %(message)s"
    },
    "error_handling": {
        "max_retries": 3,
        "continue_on_error": False
    },
    "output": {
        "results_file": "outputs/experiment_results.json",
        "summary_file": "outputs/summary.txt"
    }
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Pipeline orchestration | End-to-end execution with checkpointing and logging |

---

## Extended Configuration (Current Hypothesis)

### Complete H-M1 Config

```python
import torch

CONFIG = {
    "experiment": {
        "hypothesis_id": "h-m1",
        "type": "MECHANISM",
        "seed": 42,
        "description": "Stratified training mechanism validation"
    },
    
    # Inherited from H-E1
    "data": {
        "beir_dataset": "nq",
        "beir_split": "test",
        "corpus_sample_size": 100000,
        "eval_queries": 500,
    },
    
    # Inherited from H-E1
    "classifier": {
        "dim": 100,
        "lr": 0.1,
        "epoch": 25,
        "wordNgrams": 2,
        "train_samples_per_class": 500,
    },
    
    # NEW: Stratification parameters
    "stratification": {
        "oversample_ratio": 3.0,
        "educational_metric": "perplexity",
        "beir_metric": "relevance",
        "divergent_threshold_percentile": 50
    },
    
    # Extended from H-E1
    "models": {
        "perplexity_model": "gpt2",
        "ner_model": "en_core_web_sm"
    },
    
    # NEW: Entity evaluation parameters
    "entity_evaluation": {
        "gate_threshold": 1.15,
        "entity_types": ["PERSON", "ORG", "GPE", "DATE", "MONEY", "LOC", "PRODUCT"],
        "batch_size": 1000
    },
    
    # Extended from H-E1
    "evaluation": {
        "target_corpus_size": 50000,
        "baseline_method": "perplexity",
        "proposed_method": "classifier"
    },
    
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    
    # Merge sub-configs
    "data_config": DATA_CONFIG,
    "baseline_config": BASELINE_CONFIG,
    "visualization_config": VISUALIZATION_CONFIG,
    "integration_config": INTEGRATION_CONFIG
}
```

---

## Environment Requirements

```python
ENVIRONMENT = {
    "python": ">=3.8",
    "cuda": "optional (CPU fallback supported)",
    "disk_space_gb": 15,
    "ram_gb": 16
}

DEPENDENCIES = {
    "fasttext": ">=0.9.2",
    "spacy": ">=3.7",
    "en_core_web_sm": ">=3.7",
    "transformers": ">=4.30",
    "beir": ">=1.0",
    "torch": ">=2.0",
    "numpy": ">=1.24",
    "matplotlib": ">=3.7",
    "seaborn": ">=0.12"
}
```

**spaCy Model Installation:**
```bash
python -m spacy download en_core_web_sm
```

---

## Configuration Usage Pattern

**In implementation code:**

```python
# Example: code/config.py
from dataclasses import dataclass
import torch

@dataclass
class ExperimentConfig:
    # Experiment metadata
    hypothesis_id: str = "h-m1"
    seed: int = 42
    
    # Dataset
    beir_dataset: str = "nq"
    beir_split: str = "test"
    corpus_sample_size: int = 100000
    
    # Stratification
    stratification_ratio: float = 3.0
    educational_metric: str = "perplexity"
    beir_metric: str = "relevance"
    
    # Classifier (inherited from H-E1)
    fasttext_dim: int = 100
    fasttext_lr: float = 0.1
    fasttext_epoch: int = 25
    fasttext_ngrams: int = 2
    train_samples_per_class: int = 500
    
    # Evaluation
    target_corpus_size: int = 50000
    gate_threshold: float = 1.15
    
    # Models
    perplexity_model: str = "gpt2"
    ner_model: str = "en_core_web_sm"
    
    # Hardware
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
```

**Alternative: Direct dict usage (matching H-E1 pattern):**

```python
# Example: code/run_experiment.py
from pathlib import Path

# Use CONFIG dict directly (consistent with H-E1)
class StratifiedTrainingExperiment:
    def __init__(self):
        self.config = CONFIG
        self.seed = self.config["experiment"]["seed"]
        
    def run_full_pipeline(self):
        # Stage 1: Data acquisition
        loader = BEIRLoader(
            dataset=self.config["data"]["beir_dataset"],
            split=self.config["data"]["beir_split"]
        )
        ...
```

---

## Rationale for Non-Standard Values

**Stratification ratio = 3.0:**
- Higher than typical oversampling (1.5-2.0)
- Hypothesis requires strong signal amplification for divergent examples
- Based on DataComp-LM's stratification approach

**Gate threshold = 1.15:**
- 15% improvement criterion specified in experiment brief
- Higher than typical 5-10% thresholds due to mechanism validation focus
- Must demonstrate measurable factual density difference

**Corpus sample size = 100K:**
- 10x larger than H-E1 (10K) to ensure sufficient divergent examples
- Needed for stratification to be effective
- Still computationally feasible for PoC

**Target corpus size = 50K:**
- Half of sampled corpus (50% selection rate)
- Ensures meaningful filtering while retaining diversity
- Matched between baseline and proposed for fair comparison

---

## Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values
- [x] Subtask count: 5 total (within budget)
- [x] Total length: ~380 lines (< 400)
- [x] "Codebase Analysis (Serena)" section included
- [x] "Inherited Configuration" section included
- [x] Field names verified from H-E1 actual code
- [x] PoC-appropriate (no hyperparameter grid)
- [x] Device auto-detection (cuda/cpu)

---

**Config Version:** 1.0  
**Status:** Complete  
**Total Subtasks:** 5 (1+1+2+1)  
**Total Lines:** 380
