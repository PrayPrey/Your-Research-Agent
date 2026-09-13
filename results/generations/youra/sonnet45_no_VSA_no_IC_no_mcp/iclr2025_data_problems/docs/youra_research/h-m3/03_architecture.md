# Architecture: h-m3 - Embedding-Stage Quality-Speed Trade-off

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-24  
**Author:** Phase 3 Architecture Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - embedding-based subset selection (no prior k-center greedy code)  
**Analyzed Path**: N/A  
**Findings**: Reuse h-e1 training patterns, h-m1 threshold sweep utilities. New embedding generation + k-center greedy implementation.

**Applied Patterns**: Archon KB - k-center greedy diversity selection, multi-stage embedding comparison, Pareto frontier analysis

---

## System Overview

**Pipeline:** Dolly-15k → 3 Embedding Models → k-center Greedy (9 subsets) → 10 LLaMA Fine-Tuning Runs → Dual Eval → Trade-off Analysis

**Execution Model:** Sequential pipeline (single GPU, fixed hyperparameters)

**Components:**
- DatasetLoader (NEW): Load Dolly-15k from HuggingFace
- EmbeddingGenerator (NEW): Generate early/mid/late embeddings
- KCenterGreedy (NEW): Diversity-based subset selection
- TrainingOrchestrator (REUSED h-e1): LLaMA-2-7B fine-tuning wrapper
- EvaluationRunner (REUSED h-m2): lm-eval harness wrapper
- TradeoffAnalyzer (NEW): Compute stage-mismatch penalty, Pareto frontier

**Data Flow:**
```
Dolly-15k → Embed(early/mid/late) → k-center(k=2k/5k/10k) → 9 subsets + baseline → 10 training runs → MMLU/HellaSwag → Trade-off plots
```

---

## Module Interfaces

### DatasetLoader (`code/load_data.py`)

**Dependencies:** datasets

```python
from datasets import load_dataset

def load_dolly_15k() -> dict:
    """Load train split (15,015 samples). Return {'instruction': str, 'response': str, 'context': str}[]."""
    ...

def format_for_embedding(sample: dict) -> str:
    """Concatenate 'instruction + response' (context ignored)."""
    ...
```

---

### EmbeddingGenerator (`code/embed_corpus.py`)

**Dependencies:** sentence_transformers, numpy

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model_id: str, device: str = "cuda"): ...
    
    def encode_batch(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Return (N, d_embed) array."""
        ...
    
    def save_embeddings(self, embeddings: np.ndarray, output_path: str): ...
    
    @staticmethod
    def load_embeddings(path: str) -> np.ndarray: ...

def generate_all_embeddings(dolly_data: list[dict], output_dir: str) -> dict:
    """Generate early/mid/late embeddings. Return {stage: path}."""
    ...
```

---

### KCenterGreedy (`code/k_center_greedy.py`)

**Dependencies:** numpy, scipy

```python
from scipy.spatial.distance import cdist
import numpy as np

class KCenterGreedy:
    def __init__(self, embeddings: np.ndarray, seed: int = 42): ...
    
    def select_subset(self, k: int) -> np.ndarray:
        """Iterative farthest-point sampling. Return indices (k,)."""
        ...
    
    def compute_diversity(self, indices: np.ndarray) -> float:
        """Average pairwise cosine distance in selected subset."""
        ...

def select_all_subsets(
    embedding_paths: dict,
    sizes: list[int],
    output_dir: str
) -> dict:
    """Run k-center for 3 stages × 3 sizes. Return {stage_kSize: indices_path}."""
    ...
```

---

### TrainingOrchestrator (`code/train.py`)

**Dependencies:** transformers, h-e1 patterns

```python
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

def train_llama(
    train_data: list[dict],
    output_dir: str,
    model_id: str = "meta-llama/Llama-2-7b-hf",
    epochs: int = 3,
    batch_size: int = 8,
    lr: float = 2e-5,
    seed: int = 42
) -> dict:
    """Fixed hyperparameters. Return {train_loss: float}."""
    ...

def train_all_conditions(subset_indices: dict, dolly_data: list[dict]) -> dict:
    """Train 10 models (9 subsets + baseline). Return {condition: checkpoint_path}."""
    ...
```

---

### EvaluationRunner (`code/evaluate.py`)

**Dependencies:** lm_eval, pandas

```python
import subprocess
import json

def run_lm_eval(
    model_path: str,
    tasks: list[str] = ["mmlu", "hellaswag"],
    batch_size: int = 8
) -> dict:
    """Shell wrapper for lm-evaluation-harness. Return {task: acc}."""
    ...

def evaluate_all_models(checkpoints: dict, output_path: str = "results/scores.csv") -> pd.DataFrame:
    """Run MMLU + HellaSwag on 10 models. Return DataFrame."""
    ...
```

---

### TradeoffAnalyzer (`code/analyze.py`)

**Dependencies:** pandas, numpy, matplotlib

```python
import pandas as pd
import matplotlib.pyplot as plt

class TradeoffAnalyzer:
    def __init__(self, scores_df: pd.DataFrame, timing_logs: dict): ...
    
    def compute_stage_mismatch_penalty(self, k: int = 5000) -> float:
        """(late_perf - early_perf) / late_perf × 100% at k=5000."""
        ...
    
    def compute_quality_bound(self, stage: str = "late", k: int = 10000) -> float:
        """|stage_kK - baseline| / baseline × 100%."""
        ...
    
    def compute_cost_ratio(self) -> float:
        """late_time / early_time."""
        ...
    
    def plot_pareto_frontier(self, output_path: str = "results/pareto.png"): ...
    
    def plot_convergence_curves(self, output_path: str = "results/convergence.png"): ...
    
    def generate_metrics_table(self, output_path: str = "results/metrics.csv"): ...
```

---

## External Dependencies (Base Hypotheses)

### Module Reuse Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| prepare_instruction_dataset | `from h_e1.code.train import prepare_instruction_dataset` | `docs/youra_research/h-e1/code/train.py` |

**Note**: Minimal reuse - only training data formatting patterns.

---

## File Organization

```
h-m3/code/
├── load_data.py                   # DatasetLoader
├── embed_corpus.py                # EmbeddingGenerator
├── k_center_greedy.py             # KCenterGreedy
├── train.py                       # TrainingOrchestrator
├── evaluate.py                    # EvaluationRunner
├── analyze.py                     # TradeoffAnalyzer
├── config.py                      # Fixed hyperparameters
└── run_experiment.py              # Main pipeline

h-m3/data/
├── dolly_15k/                     # Cached dataset
├── embeddings/                    # early/mid/late .npy files (15015 × d_embed)
├── subsets/                       # 9 × indices .npy files
└── timing_logs.yaml               # Embedding + selection times

h-m3/models/                       # 10 × 13GB checkpoints
├── baseline/
├── early_k2000/
├── early_k5000/
├── early_k10000/
├── mid_k2000/
├── mid_k5000/
├── mid_k10000/
├── late_k2000/
├── late_k5000/
└── late_k10000/

h-m3/results/
├── scores.csv                     # 10 models × {MMLU, HellaSwag}
├── metrics.csv                    # Stage-mismatch penalty, quality bound, cost ratio
├── pareto.png                     # Performance vs. compute cost
├── convergence.png                # Performance vs. k
└── gate_check.yaml                # PASS/FAIL decision
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Embedding Pipeline | Load Dolly → generate 3 embedding sets → save .npy | 8 | 1+4+3 (Load:1, Embed:4, Save:3) |
| A-2 | Subset Selection | k-center greedy for 9 configs → save indices | 11 | 5+4+2 (Algorithm:5, 9 runs:4, Timing:2) |
| A-3 | Training Pipeline | 10 fine-tuning runs → checkpoints | 12 | 3+6+3 (Setup:3, Training:6, Monitor:3) |
| A-4 | Evaluation + Analysis | MMLU/HellaSwag → trade-off metrics → plots | 14 | 4+5+3+2 (Eval:4, Metrics:5, Plots:3, Gate:2) |

**Distribution**: High(14-17): [A-4], Medium(9-13): [A-2, A-3], Low(4-8): [A-1]

**Total Complexity**: 45 (PoC range for MECHANISM)

---

## Epic Task Breakdown

### A-1: Embedding Pipeline (Complexity: 8)

**Objective:** Generate 3 embedding matrices for full Dolly-15k corpus

**Dependencies:** HuggingFace datasets, sentence-transformers

**Subtasks:**
1. **Load Dolly** (1): Download train split, verify 15,015 samples
2. **Generate embeddings** (4): Encode with MiniLM (384d), MPNet (768d), Instructor (768d), log timing
3. **Save outputs** (3): Write .npy files, verify shapes, log checksums

**Deliverables:**
- `data/dolly_15k/train.jsonl`
- `data/embeddings/early_embeddings.npy` (15015, 384)
- `data/embeddings/mid_embeddings.npy` (15015, 768)
- `data/embeddings/late_embeddings.npy` (15015, 768)
- `data/timing_logs.yaml` (embed_early: X sec, embed_mid: Y sec, embed_late: Z sec)

**Validation:**
- All embeddings shape (15015, d)
- Early time <10 sec, late time <100 sec
- Embeddings unit-normalized (cosine distance ready)

---

### A-2: Subset Selection (Complexity: 11)

**Objective:** Run k-center greedy on 3 embeddings × 3 sizes = 9 configurations

**Dependencies:** A-1 complete, scipy

**Subtasks:**
1. **Implement k-center greedy** (5): Iterative farthest-point, cosine distance, random seed init
2. **Run 9 selections** (4): early/mid/late × k=2000/5000/10000, log timing
3. **Compute diversity** (2): Average pairwise distances, save stats

**Deliverables:**
- `code/k_center_greedy.py` (KCenterGreedy class)
- `data/subsets/early_k2000_indices.npy` (2000,)
- `data/subsets/early_k5000_indices.npy` (5000,)
- ... (9 total files)
- `data/timing_logs.yaml` (selection_early_k2000: X sec, ...)

**Validation:**
- All indices in [0, 15014]
- Selection times <5 min per config
- Diversity increases with k (larger subsets → lower avg distance)

---

### A-3: Training Pipeline (Complexity: 12)

**Objective:** Fine-tune 10 LLaMA-2-7B models with identical hyperparameters

**Dependencies:** A-2 complete, transformers, GPU

**Subtasks:**
1. **Setup training** (3): Load base model, configure TrainingArguments, test single run
2. **Train 10 models** (6): Sequential fine-tuning (3 epochs × 10 conditions), validation logging
3. **Monitor** (3): Track loss curves, verify convergence, log GPU usage

**Deliverables:**
- `code/config.py` (epochs=3, lr=2e-5, batch=8, seed=42)
- `models/baseline/pytorch_model.bin` (13GB)
- `models/early_k2000/pytorch_model.bin` (13GB)
- ... (10 total checkpoints)
- `models/{condition}/training_log.json` (train_loss per epoch)

**Validation:**
- All 10 models complete 3 epochs
- Validation loss decreases for all conditions
- Total GPU time <25 hours
- Checkpoints loadable by transformers

---

### A-4: Evaluation + Analysis (Complexity: 14)

**Objective:** Benchmark → compute trade-offs → generate gate check

**Dependencies:** A-3 complete, lm-eval, matplotlib

**Subtasks:**
1. **Run evaluation** (4): MMLU (14k samples × 10 models), HellaSwag (10k × 10 models), aggregate
2. **Compute metrics** (5): Stage-mismatch penalty at k=5000, quality bound at k=10000, cost ratio, Pareto points
3. **Generate plots** (3): Pareto frontier, convergence curves, delta heatmap
4. **Gate check** (2): Verify primary criteria (≥2% penalty, ≥3× speedup, ≤1% quality bound)

**Deliverables:**
- `results/scores.csv` (columns: condition, mmlu_acc, hellaswag_acc)
- `results/metrics.csv` (stage_mismatch_penalty, quality_bound, cost_ratio)
- `results/pareto.png` (scatter: cost vs. performance)
- `results/convergence.png` (line: k vs. accuracy, 3 stages)
- `results/gate_check.yaml` (status: PASS/FAIL, criteria: {penalty: ✓, speedup: ✓, quality: ✓})

**Validation:**
- MMLU scores in [40%, 50%] (sanity check)
- HellaSwag scores in [55%, 65%]
- Stage-mismatch penalty: late > early at k=5000
- Gate PASS: all 3 primary criteria met

---

## PoC Constraints & Fallbacks

**GPU unavailable:**
- Use GPT-2 1.5B instead of LLaMA-2-7B (reduces training time, maintains trade-off structure)
- Reduce k sizes: 1000/3000/7000 (still tests convergence)

**Embedding timeout:**
- Use smaller embedding models: MiniLM-L3 (early), MPNet-small (mid), Instructor-base (late)
- Batch size tuning to fit GPU memory

**k-center greedy too slow:**
- Approximate k-center: sample 10k random points, run greedy on subset, expand to full dataset
- Fallback: random sampling (control condition for diversity baseline)

**lm-eval crashes:**
- Run MMLU only (14k samples sufficient for 2% detection)
- Reduce few-shot: 0-shot instead of 5-shot MMLU

---

## Acceptance Criteria

**PoC complete when:**
1. All 3 embedding files generated (early/mid/late)
2. All 9 subset selections complete
3. All 10 fine-tuning runs complete
4. MMLU + HellaSwag scores for 10 models
5. Trade-off metrics computed
6. Gate check report generated

**Gate passes (SHOULD_WORK) when:**
- Stage-mismatch penalty ≥ 2.0% at k=5000 (late - early)
- Compute cost ratio ≥ 3.0× (late / early)
- Quality bound ≤ 1.0% (|late_k10000 - baseline|)

**Gate fails (route to EXPLORE) when:**
- No measurable trade-off (delta <1%)
- Embeddings produce similar subsets (diversity indistinguishable)
- Late-stage degrades quality (>1% worse than early at k=10000)

---

## Implementation Notes

**Reproducibility:**
- Fixed seeds: k-center init (42), training (42)
- Pin versions: sentence-transformers==2.3.0, transformers==4.36.0, lm-eval==0.4.1
- Log all timing (wall-clock seconds)

**Storage optimization:**
- Keep only final checkpoints (delete intermediate epochs)
- Compress embeddings: float16 instead of float32 (halves storage)

**Execution order:**
1. Load Dolly + generate embeddings (30 min)
2. Run k-center greedy (1 hour)
3. Train 10 models (20 hours)
4. Evaluate (5 hours)
5. Analysis + plots (30 min)

**Total timeline:** 2 days with single GPU

---

**Document Status:** Phase 3 Complete  
**Next Phase:** Phase 4 - Coding & Validation  
**Estimated LoC:** ~600 (all new - no complex abstractions)
