# Configuration: h-e1 — Contamination Geometry Decomposition Exists

**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-05-13

Applied: Python-dataclass-fixed-config pattern (single seed, no grid search)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — green-field implementation
**Config Files Found**: None - new config design
**Pattern Used**: dataclass + YAML schema

---

## ExperimentConfig (Python Dataclass)

```python
# code/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    """Fixed single-run config for h-e1 EXISTENCE PoC.

    All values are defaults from prior literature or standard practice.
    No grid search — one run to validate geometry stratification exists.
    """

    # --- Reproducibility ---
    seed: int = 42

    # --- N-gram Index ---
    ngram_n: int = 13           # EleutherAI standard (13-gram contamination)
    ngram_buckets: int = 500    # Hash buckets for inverted index sharding

    # --- SBERT Embedding Index ---
    sbert_model: str = "all-MiniLM-L6-v2"
    sbert_batch_size: int = 256

    # --- FAISS ---
    faiss_index_type: str = "IndexFlatIP"  # Inner product (cosine after L2-norm)

    # --- Geometry Stratification ---
    stratum_percentile: float = 75.0  # Top quartile = "high overlap" threshold

    # --- Min-K%++ Detector ---
    minkpp_k: float = 0.20  # 20% of tokens used (zjysteven default)

    # --- Bootstrap CI ---
    bootstrap_n: int = 10_000

    # --- Simulated Contamination (Approach B) ---
    contamination_rate: float = 0.10  # 10% injection rate for Approach B

    # --- Corpora & Benchmarks ---
    corpora: list = field(default_factory=lambda: ["pile", "c4", "redpajama"])
    benchmarks: list = field(default_factory=lambda: ["mmlu", "hellaswag", "gsm8k"])

    # --- Corpus Streaming Limits ---
    # Non-standard: capped to avoid OOM on single GPU node
    pile_max_docs: int = 1_000_000
    c4_max_docs: int = 1_000_000
    redpajama_max_docs: int = 1_000_000

    # --- Model IDs for Min-K%++ / DC-PDD ---
    llama2_7b_id: str = "meta-llama/Llama-2-7b-hf"
    mistral_7b_id: str = "mistralai/Mistral-7B-v0.1"
    pythia_7b_id: str = "EleutherAI/pythia-6.9b"
    pythia_2b_id: str = "EleutherAI/pythia-2.8b"   # DC-PDD reference model

    # --- Output Directories ---
    figures_dir: str = "h-e1/figures/"
    results_dir: str = "h-e1/results/"
    index_dir: str = "h-e1/indices/"

    def validate(self) -> None:
        """Raise ValueError on invalid parameter combinations."""
        assert 0.0 < self.minkpp_k < 1.0, "minkpp_k must be in (0, 1)"
        assert 0.0 < self.stratum_percentile < 100.0, "stratum_percentile must be in (0, 100)"
        assert self.bootstrap_n >= 1000, "bootstrap_n too low for stable CI"
        assert 0.0 < self.contamination_rate < 1.0, "contamination_rate must be in (0, 1)"
        assert self.ngram_n > 0, "ngram_n must be positive"
        for d in [self.figures_dir, self.results_dir, self.index_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)


def get_config() -> ExperimentConfig:
    """Return the single fixed config for this PoC run."""
    cfg = ExperimentConfig()
    cfg.validate()
    return cfg
```

---

## YAML Configuration Schema (`experiment_config.yaml`)

```yaml
# experiment_config.yaml
# h-e1: Contamination Geometry Decomposition — EXISTENCE PoC
# All values match ExperimentConfig dataclass defaults.

experiment:
  seed: 42                        # RNG seed for reproducibility

ngram:
  n: 13                           # Gram size — EleutherAI standard
  buckets: 500                    # Hash buckets for index sharding

sbert:
  model: "all-MiniLM-L6-v2"      # Sentence-BERT model (HuggingFace hub)
  batch_size: 256                 # Embedding batch size (fits single 40GB GPU)

faiss:
  index_type: "IndexFlatIP"       # Flat inner-product; exact search, no quantization

stratification:
  percentile: 75.0                # Top-quartile defines "high overlap" boundary

detectors:
  minkpp_k: 0.20                  # Fraction of lowest-prob tokens for Min-K%++
  dcpdd_ref_model: "EleutherAI/pythia-2.8b"   # Reference model for DC-PDD

evaluation:
  bootstrap_n: 10000              # Bootstrap iterations for 95% CI
  contamination_rate: 0.10        # Injection rate for Approach B simulated sets

corpora:
  names: ["pile", "c4", "redpajama"]
  pile_max_docs: 1000000          # Stream cap to avoid OOM
  c4_max_docs: 1000000
  redpajama_max_docs: 1000000

benchmarks:
  names: ["mmlu", "hellaswag", "gsm8k"]

models:
  llama2_7b: "meta-llama/Llama-2-7b-hf"
  mistral_7b: "mistralai/Mistral-7B-v0.1"
  pythia_7b: "EleutherAI/pythia-6.9b"
  pythia_2b: "EleutherAI/pythia-2.8b"

output:
  figures_dir: "h-e1/figures/"
  results_dir: "h-e1/results/"
  index_dir: "h-e1/indices/"
```

---

## Per-Module Configuration Sections

### DataConfig

```python
@dataclass
class DataConfig:
    corpora: list = field(default_factory=lambda: ["pile", "c4", "redpajama"])
    benchmarks: list = field(default_factory=lambda: ["mmlu", "hellaswag", "gsm8k"])
    pile_max_docs: int = 1_000_000
    c4_max_docs: int = 1_000_000
    redpajama_max_docs: int = 1_000_000
    contamination_rate: float = 0.10
```

### IndexConfig

```python
@dataclass
class IndexConfig:
    ngram_n: int = 13
    ngram_buckets: int = 500
    sbert_model: str = "all-MiniLM-L6-v2"
    sbert_batch_size: int = 256
    faiss_index_type: str = "IndexFlatIP"
    index_dir: str = "h-e1/indices/"
```

### StratificationConfig

```python
@dataclass
class StratificationConfig:
    stratum_percentile: float = 75.0
    # Strata labels produced: "lexical" | "semantic" | "indeterminate"
```

### DetectorConfig

```python
@dataclass
class DetectorConfig:
    minkpp_k: float = 0.20
    llama2_7b_id: str = "meta-llama/Llama-2-7b-hf"
    mistral_7b_id: str = "mistralai/Mistral-7B-v0.1"
    pythia_7b_id: str = "EleutherAI/pythia-6.9b"
    pythia_2b_id: str = "EleutherAI/pythia-2.8b"
```

### EvaluationConfig

```python
@dataclass
class EvaluationConfig:
    bootstrap_n: int = 10_000
    # PoC pass conditions (checked in evaluate.py):
    # recall_lexical > 0.70, recall_semantic > 0.40, indeterminacy_rate < 0.30
    recall_lexical_threshold: float = 0.70
    recall_semantic_threshold: float = 0.40
    indeterminacy_rate_threshold: float = 0.30
```

### OutputConfig

```python
@dataclass
class OutputConfig:
    figures_dir: str = "h-e1/figures/"
    results_dir: str = "h-e1/results/"
    index_dir: str = "h-e1/indices/"
```

---

## Environment Variables

```bash
# Set before running run_experiment.py
export CUDA_VISIBLE_DEVICES=0       # Single GPU — pick lowest-usage device from nvidia-smi
export HF_HOME=/scratch/hf_cache    # HuggingFace model/dataset cache
export TOKENIZERS_PARALLELISM=false # Avoid HF tokenizer fork warnings
```

---

## Subtasks

| ID | Title | Parent Epic | Description |
|----|-------|-------------|-------------|
| C-3-1 | GeometryStratifier config wiring | A-3 | Wire StratificationConfig into GeometryStratifier.__init__; expose stratum_percentile for threshold computation |
| C-3-2 | Stratum label validation | A-3 | Add post-assign assertion that output array contains only ["lexical", "semantic", "indeterminate"]; raise on unknown label |
| C-6-1 | EvaluationConfig PoC gate check | A-6 | Implement check_poc_conditions(cfg: EvaluationConfig, metrics: dict) that compares per-stratum recall/F1 and indeterminacy_rate against thresholds; return pass/fail dict |
