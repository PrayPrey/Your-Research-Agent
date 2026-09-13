# Configuration Specification: h-e1 - Retrieval-Quality Corpus Filtering

**Date:** 2026-07-12  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Config Designer:** configuration-agent  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - no existing config patterns  
**Config Files Found:** None - new config design  
**Pattern Used:** Hardcoded dict (PoC simplicity)  

---

## Knowledge Base Integration

**Applied:** Standard PyTorch/HuggingFace defaults for DL experiments

---

## Configuration Philosophy

**PoC Strategy:** Single fixed configuration to test "does retrieval-quality filtering work?"
- No hyperparameter grid (EXISTENCE hypothesis)
- No ablation configs
- Fixed seed=42
- Default values from referenced papers (DPR, DataComp-LM, FastText)

---

## A-1: Data Acquisition (Complexity: 10, Budget: 2)

### Configuration

```python
DATA_CONFIG = {
    "seed": 42,
    "beir": {
        "dataset": "nq",
        "split": "test",
        "url": "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nq.zip"
    },
    "common_crawl": {
        "snapshot": "CC-MAIN-2024-10",
        "sample_size": 100000,
        "timeout": 3600
    },
    "preprocessing": {
        "min_length": 50,
        "max_length": 500,
        "language": "en",
        "dedup_threshold": 0.9
    },
    "tokenizer": {
        "model_name": "facebook/dpr-ctx_encoder-single-nq-base",
        "max_length": 512,
        "truncation": True
    },
    "output_paths": {
        "beir_data": "data/beir/nq/",
        "cc_raw": "data/common_crawl/raw/",
        "cc_preprocessed": "data/common_crawl/preprocessed/"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | BEIR NQ download | Download test split via beir package |
| C-1-2 | CC sampling + preprocessing | Sample 100K docs, HTML extraction, dedup, filter |

---

## A-2: Baseline Corpus (Complexity: 9, Budget: 2)

### Configuration

```python
BASELINE_CONFIG = {
    "perplexity": {
        "model_name": "gpt2",
        "batch_size": 16,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    },
    "corpus": {
        "target_size": 1000000,
        "selection_method": "lowest_perplexity"
    },
    "indexing": {
        "encoder": "facebook/dpr-ctx_encoder-single-nq-base",
        "batch_size": 64,
        "embedding_dim": 768,
        "index_type": "IndexFlatIP"
    },
    "output_paths": {
        "perplexity_scores": "data/baseline/perplexity_scores.npy",
        "corpus": "data/baseline/corpus_1M.jsonl",
        "faiss_index": "data/baseline/corpus.index"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Perplexity computation | GPT-2 perplexity for all 100K docs |
| C-2-2 | Corpus selection + FAISS indexing | Select top 1M, encode with DPR, index |

---

## A-3: Classifier Training (Complexity: 11, Budget: 2)

### Configuration

```python
CLASSIFIER_CONFIG = {
    "training_data": {
        "positive_threshold": 2,
        "negative_threshold": 0,
        "oversample_ratio": 2,
        "target_samples_per_class": 10000,
        "validation_split": 0.2
    },
    "fasttext": {
        "dim": 100,
        "lr": 0.1,
        "epoch": 25,
        "wordNgrams": 2,
        "loss": "softmax",
        "thread": 4
    },
    "validation": {
        "min_accuracy": 0.7
    },
    "output_paths": {
        "training_data": "data/classifier/training.txt",
        "validation_data": "data/classifier/validation.txt",
        "model": "models/retrieval_quality_classifier.bin"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Stratified data extraction | Extract high/low BEIR relevance docs with oversampling |
| C-3-2 | FastText training | Train supervised model, validate >0.7 accuracy |

---

## A-4: Proposed Corpus (Complexity: 8, Budget: 2)

### Configuration

```python
PROPOSED_CONFIG = {
    "classifier": {
        "model_path": "models/retrieval_quality_classifier.bin"
    },
    "corpus": {
        "target_size": 1000000,
        "selection_method": "highest_quality_score"
    },
    "indexing": {
        "encoder": "facebook/dpr-ctx_encoder-single-nq-base",
        "batch_size": 64,
        "embedding_dim": 768,
        "index_type": "IndexFlatIP"
    },
    "output_paths": {
        "quality_scores": "data/proposed/quality_scores.npy",
        "corpus": "data/proposed/corpus_1M.jsonl",
        "faiss_index": "data/proposed/corpus.index"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Quality score prediction | Apply classifier to all 100K docs |
| C-4-2 | Corpus selection + FAISS indexing | Select top 1M by quality, encode, index |

---

## A-5: Retrieval Evaluation (Complexity: 12, Budget: 2)

### Configuration

```python
EVALUATION_CONFIG = {
    "dpr": {
        "question_encoder": "facebook/dpr-question_encoder-single-nq-base",
        "context_encoder": "facebook/dpr-ctx_encoder-single-nq-base",
        "batch_size": 32,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    },
    "retrieval": {
        "k": 10,
        "similarity": "cosine"
    },
    "metrics": {
        "recall_at_k": 10,
        "gate_threshold": 0.03
    },
    "output_paths": {
        "baseline_results": "results/baseline_recall.json",
        "proposed_results": "results/proposed_recall.json",
        "comparison": "results/recall_comparison.json"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | DPR retrieval | Encode queries, retrieve top-10 for both corpora |
| C-5-2 | Recall@10 computation | Compute metrics, compare with gate threshold |

---

## A-6: Visualization (Complexity: 8, Budget: 2)

### Configuration

```python
VISUALIZATION_CONFIG = {
    "figures": {
        "dpi": 300,
        "formats": ["png", "pdf"],
        "style": "seaborn-v0_8-paper"
    },
    "figure_1_recall_comparison": {
        "figsize": (8, 6),
        "title": "Recall@10: Perplexity vs Retrieval-Quality Filtering",
        "gate_threshold": 0.03,
        "colors": ["#1f77b4", "#ff7f0e"]
    },
    "figure_2_quality_distribution": {
        "figsize": (10, 6),
        "bins": 50,
        "title": "FastText Quality Score Distribution"
    },
    "figure_3_corpus_statistics": {
        "figsize": (10, 8),
        "metrics": ["entity_density", "ttr", "avg_length", "perplexity"]
    },
    "figure_4_query_performance": {
        "figsize": (8, 8),
        "alpha": 0.5,
        "title": "Per-Query Recall@10 Comparison"
    },
    "output_paths": {
        "figures_dir": "figures/"
    }
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Core figures (1-2) | Recall comparison + quality distribution |
| C-6-2 | Analysis figures (3-4) | Corpus statistics + per-query scatter |

---

## Master Configuration

**Usage:** Import in `run_experiment.py` for unified config access

```python
MASTER_CONFIG = {
    "experiment": {
        "hypothesis_id": "h-e1",
        "type": "EXISTENCE",
        "seed": 42,
        "description": "Retrieval-quality corpus filtering validation"
    },
    "data": DATA_CONFIG,
    "baseline": BASELINE_CONFIG,
    "classifier": CLASSIFIER_CONFIG,
    "proposed": PROPOSED_CONFIG,
    "evaluation": EVALUATION_CONFIG,
    "visualization": VISUALIZATION_CONFIG
}
```

---

## Environment Requirements

```python
ENVIRONMENT = {
    "python": ">=3.8",
    "cuda": "optional (CPU fallback supported)",
    "disk_space_gb": 10,
    "ram_gb": 16
}

DEPENDENCIES = {
    "transformers": ">=4.30.0",
    "beir": ">=1.0.0",
    "fasttext": ">=0.9.2",
    "faiss-cpu": ">=1.7.0",
    "warcio": ">=1.7.0",
    "torch": ">=2.0.0",
    "numpy": ">=1.23.0",
    "matplotlib": ">=3.7.0",
    "seaborn": ">=0.12.0"
}
```

---

## Configuration Usage Pattern

**In implementation code:**

```python
# Example: code/data_loader.py
from config.master_config import MASTER_CONFIG

class BEIRLoader:
    def __init__(self):
        self.config = MASTER_CONFIG["data"]["beir"]
        self.dataset = self.config["dataset"]
        self.split = self.config["split"]
        
    def load(self):
        return beir.util.download_and_unzip(
            url=self.config["url"],
            out_dir=MASTER_CONFIG["data"]["output_paths"]["beir_data"]
        )
```

---

## Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] Rationale omitted (all standard defaults)
- [x] Subtask count: 2 per task (within budget)
- [x] Total length: ~330 lines (< 400)
- [x] "Codebase Analysis (Serena)" section included
- [x] PoC-appropriate (no hyperparameter grid)
- [x] All paths relative to project root
- [x] Device auto-detection (cuda/cpu)

---

**Config Version:** 1.0  
**Status:** Complete  
**Total Subtasks:** 12 (2 × 6 tasks)  
**Total Lines:** 335
