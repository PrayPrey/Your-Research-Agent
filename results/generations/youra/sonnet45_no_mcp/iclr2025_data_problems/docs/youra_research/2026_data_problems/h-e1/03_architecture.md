# System Architecture: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC - Minimal Validation)  
**Date:** 2026-04-15  
**Architecture Tier:** Minimal (hardcoded config, print+CSV logging, smoke tests)

Applied: **EXISTENCE PoC Pattern** - Minimal structure for "does it work?" validation

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - no existing code to analyze  
**Analyzed Path:** N/A  
**Findings:** MCP unavailable in test environment. Fresh implementation using standard PyTorch + Transformers patterns.

---

## Architecture Overview

**Purpose:** Validate diversity-ranked curriculum scheduling improves foundation model performance vs. static baseline.

**Core Components:**
1. Data preparation (domain filtering, diversity scoring, tokenization)
2. Baseline model (GPT-2 style, static domain mixing)
3. Proposed curriculum scheduler (diversity-ranked temporal ordering)
4. Training loop (4 conditions × 2 scales × 5 seeds)
5. Evaluation harness (MMLU, Big-Bench, domain benchmarks)

**File Structure (Minimal PoC):**
```
h-e1/code/
├── data/
│   ├── prepare_pile.py          # Download, filter, precompute diversity
│   └── curriculum_loader.py      # Dynamic domain sampling
├── models/
│   └── model.py                  # GPT-2 baseline + shared architecture
├── train.py                      # Main training loop (all 4 conditions)
├── evaluate.py                   # Benchmark evaluation + metrics
├── config.py                     # Hardcoded hyperparameters
└── utils.py                      # Logging, checkpointing, PR/CKA
```

---

## Module Specifications

### 1. Data Preparation (`data/prepare_pile.py`)

**Dependencies:** datasets, transformers, numpy

```python
def download_pile_subset(target_domains: list[str], tokens_per_domain: int) -> dict:
    """Download and filter The Pile to 6 target domains."""
    ...

def compute_diversity_scores(domain_corpus: dict) -> dict[str, float]:
    """Compute composite diversity: vocab entropy + syntactic complexity + semantic spread."""
    ...

def preprocess_and_tokenize(corpus: dict, tokenizer, seq_length: int) -> dict:
    """Apply GPT-2 BPE tokenization, deduplication, quality filtering."""
    ...

def create_splits(tokenized_data: dict, train_ratio: float) -> tuple:
    """Split into train (95B tokens) and validation (5B tokens)."""
    ...
```

---

### 2. Curriculum Data Loader (`data/curriculum_loader.py`)

**Dependencies:** torch, numpy

```python
class CurriculumDataLoader:
    def __init__(self, 
                 domain_data: dict,
                 diversity_scores: dict[str, float],
                 condition: str,
                 batch_size: int,
                 total_steps: int): ...
    
    def get_domain_weights(self, training_progress: float) -> dict[str, float]:
        """Compute Gaussian-weighted domain sampling based on condition."""
        ...
    
    def sample_batch(self, step: int) -> torch.Tensor:
        """Sample batch according to curriculum schedule."""
        ...
```

**Conditions:**
- `static`: Uniform 16.67% per domain
- `diversity_ranked`: High→Low (Gaussian peaks at domain_rank/6)
- `reversed`: Low→High (inverted Gaussian)
- `shuffled`: Random order per epoch

---

### 3. Model Architecture (`models/model.py`)

**Dependencies:** torch, transformers

```python
class GPT2Config:
    """Configuration for 1B and 7B scales."""
    def __init__(self, scale: str): ...
    
    # 1B: n_layer=24, n_head=16, n_embd=1536
    # 7B: n_layer=32, n_head=32, n_embd=4096

class GPT2Model(nn.Module):
    """Standard GPT-2 architecture (decoder-only transformer)."""
    def __init__(self, config: GPT2Config): ...
    
    def forward(self, input_ids: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """Autoregressive language modeling forward pass."""
        ...
```

---

### 4. Training Loop (`train.py`)

**Dependencies:** torch, transformers, argparse

```python
def setup_experiment(condition: str, scale: str, seed: int) -> tuple:
    """Initialize model, optimizer, data loader, checkpointing."""
    ...

def train_step(model, batch, optimizer, scaler) -> float:
    """Single training step with BFloat16 mixed precision."""
    ...

def train(config: Config) -> dict:
    """
    Main training loop:
    - Load curriculum data loader based on condition
    - Train for total_steps with dynamic domain weights
    - Save checkpoints at [10%, 25%, 50%, 75%, 100%]
    - Log validation perplexity every 1000 steps
    """
    ...

def run_all_experiments():
    """
    Orchestrate full experiment matrix:
    - 4 conditions × 2 scales × 5 seeds = 40 runs
    - Sequential execution (single GPU per run)
    """
    ...
```

---

### 5. Evaluation (`evaluate.py`)

**Dependencies:** lm_eval, torch, scipy, numpy

```python
def evaluate_benchmarks(model, tokenizer, tasks: list[str]) -> dict:
    """Run lm-evaluation-harness on MMLU, Big-Bench, domain tasks."""
    ...

def compute_composite_score(benchmark_results: dict) -> float:
    """Aggregate MMLU + Big-Bench + domain tasks into single metric."""
    ...

def compute_participation_ratio(model, probe_data: torch.Tensor) -> float:
    """
    Gradient geometry analysis:
    - Compute gradient covariance on fixed probe dataset
    - Calculate PR = (Σλ)² / Σ(λ²)
    """
    ...

def compute_cka_similarity(model_early, model_final, dataloader) -> np.ndarray:
    """Layer-wise CKA between 25% and 100% checkpoints."""
    ...

def statistical_test(diversity_ranked: list, static: list) -> tuple:
    """Paired t-test with Bonferroni correction (4 comparisons)."""
    ...
```

---

### 6. Configuration (`config.py`)

**Dependencies:** None

```python
class Config:
    """Hardcoded hyperparameters for EXISTENCE PoC."""
    
    # Data
    TARGET_DOMAINS = ["Pile-CC", "StackExchange", "Wikipedia (en)", 
                      "ArXiv", "Github", "PubMed Central"]
    TOKENS_PER_DOMAIN = 16_700_000_000  # 16.7B
    SEQ_LENGTH = 2048
    
    # Model scales
    SCALE_1B = {"n_layer": 24, "n_head": 16, "n_embd": 1536}
    SCALE_7B = {"n_layer": 32, "n_head": 32, "n_embd": 4096}
    
    # Training
    TOTAL_STEPS = {"1B": 100_000, "7B": 150_000}
    BATCH_SIZE = {"1B": 512, "7B": 1024}
    LR = {"1B": 3e-4, "7B": 1.5e-4}
    WARMUP_STEPS = 2000
    GRAD_CLIP = 1.0
    
    # Curriculum
    GAUSSIAN_WIDTH = 0.3
    MIN_WEIGHT = 0.05
    
    # Evaluation
    CHECKPOINT_STEPS = [0.1, 0.25, 0.5, 0.75, 1.0]  # Progress fractions
    EVAL_TASKS = ["mmlu", "bigbench_hard", "hellaswag", 
                  "winogrande", "humaneval", "mbpp", "scienceqa"]
    
    # Experiment matrix
    CONDITIONS = ["static", "diversity_ranked", "reversed", "shuffled"]
    SCALES = ["1B", "7B"]
    SEEDS = [42, 43, 44, 45, 46]
```

---

### 7. Utilities (`utils.py`)

**Dependencies:** torch, matplotlib, pandas

```python
def setup_logging(output_dir: str) -> None:
    """Initialize CSV logging for training metrics."""
    ...

def save_checkpoint(model, optimizer, step: int, path: str) -> None:
    """Save model checkpoint with metadata."""
    ...

def load_checkpoint(path: str) -> tuple:
    """Load model checkpoint for evaluation."""
    ...

def plot_domain_schedule(condition: str, diversity_scores: dict) -> None:
    """Generate domain sampling schedule line plot."""
    ...

def plot_performance_comparison(results: dict) -> None:
    """Generate mandatory bar chart: 4 conditions × 2 scales with error bars."""
    ...

def plot_training_curves(metrics: dict) -> None:
    """Validation perplexity vs. training steps."""
    ...

def plot_participation_ratio(pr_data: dict) -> None:
    """PR evolution over checkpoints."""
    ...

def plot_cka_heatmap(cka_matrix: np.ndarray) -> None:
    """CKA similarity heatmap."""
    ...
```

---

## Data Flow

**Training Pipeline:**
1. `prepare_pile.py` → Download 6 domains, compute diversity scores → Save tokenized data
2. `train.py` → Load curriculum data loader → Train with dynamic weights → Save checkpoints
3. `evaluate.py` → Load checkpoints → Run benchmarks → Compute PR/CKA → Generate figures

**Curriculum Scheduling:**
```
training_progress (0.0→1.0) → get_domain_weights() → {domain: weight}
                                                     ↓
                              sample_batch() ← WeightedRandomSampler
                                                     ↓
                                              model.forward()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Preparation | Download Pile subset, compute diversity, tokenize | 12 | Module(3) + Deps(3) + Algo(3) + Integrate(3) |
| E-2 | Curriculum Loader | Implement dynamic domain scheduling for 4 conditions | 14 | Module(3) + Deps(2) + Algo(5) + Integrate(4) |
| E-3 | Model + Training | GPT-2 model, training loop, checkpointing | 16 | Module(4) + Deps(4) + Algo(4) + Integrate(4) |
| E-4 | Evaluation Harness | Benchmarks, PR/CKA, statistical tests | 15 | Module(4) + Deps(3) + Algo(4) + Integrate(4) |
| E-5 | Experiment Orchestration | Run 40 experiments, generate visualizations | 11 | Module(2) + Deps(2) + Algo(3) + Integrate(4) |

**Distribution:**  
VeryHigh(18-20): []  
High(14-17): [E-2, E-3, E-4]  
Medium(9-13): [E-1, E-5]  
Low(4-8): []

**Total Complexity:** 68 (avg 13.6 per task)

---

## Task Breakdown Details

### E-1: Data Preparation (12)
- **Module Size (3):** 4 functions, ~200 lines total
- **Dependencies (3):** Hugging Face datasets, transformers tokenizer, numpy
- **Algorithm (3):** Diversity computation (vocab entropy + syntactic + semantic), MinHash dedup
- **Integration (3):** Save to disk format compatible with DataLoader

**Subtasks:**
1. Download and filter The Pile to 6 domains
2. Compute diversity scores (vocab entropy, syntactic complexity, semantic spread)
3. Tokenize with GPT-2 BPE, apply deduplication and quality filtering
4. Create train/val splits and save to disk

---

### E-2: Curriculum Loader (14)
- **Module Size (3):** CurriculumDataLoader class, ~150 lines
- **Dependencies (2):** torch.utils.data, numpy
- **Algorithm (5):** Gaussian weighting function, 4 condition variants, weighted sampling
- **Integration (4):** Interface with 4 conditions, dynamic weight updates per step

**Subtasks:**
1. Implement Gaussian weight computation for diversity-ranked condition
2. Implement reversed and shuffled variants
3. Create weighted batch sampler with per-step updates
4. Validate token exposure matches baseline (16.7B per domain)

---

### E-3: Model + Training (16)
- **Module Size (4):** GPT2Model class, train loop, optimizer setup, ~300 lines
- **Dependencies (4):** torch, transformers, BFloat16 scaler, distributed (if multi-GPU)
- **Algorithm (4):** Transformer forward/backward, AdamW with cosine decay, grad clipping
- **Integration (4):** Checkpoint saving at 5 progress points, curriculum loader integration

**Subtasks:**
1. Implement GPT-2 architecture for 1B and 7B scales
2. Setup AdamW optimizer with cosine learning rate schedule
3. Implement training loop with BFloat16 mixed precision
4. Add checkpointing at [10%, 25%, 50%, 75%, 100%]
5. Integrate curriculum data loader

---

### E-4: Evaluation Harness (15)
- **Module Size (4):** 5 evaluation functions, ~250 lines
- **Dependencies (3):** lm-evaluation-harness, scipy, torch-cka
- **Algorithm (4):** PR computation (eigenvalue analysis), CKA (kernel alignment), t-test
- **Integration (4):** Load checkpoints, run multiple benchmarks, statistical testing

**Subtasks:**
1. Integrate lm-evaluation-harness for MMLU, Big-Bench, domain tasks
2. Implement Participation Ratio computation
3. Implement CKA similarity measurement
4. Implement statistical testing with Bonferroni correction
5. Generate all required figures

---

### E-5: Experiment Orchestration (11)
- **Module Size (2):** Main script, orchestration logic, ~100 lines
- **Dependencies (2):** argparse, subprocess (or sequential calls)
- **Algorithm (3):** Nested loop over conditions/scales/seeds, GPU assignment
- **Integration (4):** Coordinate 40 runs, aggregate results, final visualization

**Subtasks:**
1. Implement experiment matrix launcher (4 × 2 × 5 = 40 runs)
2. Setup GPU selection and CUDA_VISIBLE_DEVICES management
3. Aggregate results across seeds for statistical analysis
4. Generate final performance comparison figure (mandatory)

---

## Infrastructure Notes

**Compute Requirements:**
- **1B scale:** 8×A100 GPUs, ~3 days per run, 100K steps
- **7B scale:** 16×A100 GPUs, ~10 days per run, 150K steps
- **Total:** ~40 runs (4 conditions × 2 scales × 5 seeds)

**Storage:**
- Tokenized data: ~100GB (6 domains × 16.7B tokens)
- Checkpoints: ~5GB (1B), ~30GB (7B) per checkpoint × 5 checkpoints × 40 runs = ~6TB total

**Logging:**
- Training metrics: CSV files (step, loss, perplexity, lr)
- Evaluation results: JSON files per checkpoint
- Figures: PNG files in `{hypothesis_folder}/figures/`

---

## Success Criteria Mapping

**Gate Condition (MUST_WORK):**
1. Diversity-ranked > Static by ≥2.0% at 1B (p<0.05) → Verified in `evaluate.py::statistical_test()`
2. Diversity-ranked > Static by ≥0.5% at 7B (p<0.05) → Verified in `evaluate.py::statistical_test()`

**Implementation Validation:**
- All 40 runs complete without errors
- Total token exposure per domain = 16.7B (verified in curriculum loader)
- Checkpoints saved at required progress points
- Mandatory figure generated (4 conditions × 2 scales bar chart)

---

## Open Risks

**Technical Risks:**
1. **GPU OOM:** 7B model may exceed 80GB A100 memory → Apply gradient checkpointing
2. **Training instability:** Large batch sizes may cause divergence → Monitor loss, reduce LR if needed
3. **Diversity score validity:** Precomputed scores may not reflect true diversity → Validate with manual inspection

**Experimental Risks:**
1. **Insufficient improvement:** Effect size < 2.0% (1B) or < 0.5% (7B) → Gate violation, stop pipeline
2. **High variance:** n=5 seeds may be insufficient for p<0.05 → Consider increasing to n=10 if borderline
3. **Evaluation bias:** MMLU/Big-Bench may not capture domain-specific improvements → Add domain benchmarks

---

## Dependencies Summary

**External Libraries:**
- PyTorch (≥2.0)
- Transformers (≥4.30)
- Datasets (Hugging Face)
- lm-evaluation-harness
- scipy, numpy, matplotlib, pandas
- torch-cka (optional, can implement custom)

**Hardware:**
- 8×A100 (40GB or 80GB) for 1B
- 16×A100 (80GB) for 7B
- ~6TB storage for checkpoints

**Datasets:**
- The Pile (EleutherAI/pile-uncopyrighted)
- MMLU, Big-Bench (via lm-evaluation-harness)

---

## Next Steps for Phase 4

1. **E-1:** Setup data pipeline, download Pile subset, compute diversity scores
2. **E-2:** Implement curriculum data loader with 4 condition variants
3. **E-3:** Implement GPT-2 model and training loop
4. **E-4:** Integrate evaluation harness and metrics
5. **E-5:** Run full experiment matrix and generate visualizations

**Critical Path:** E-1 → E-2 → E-3 → E-4 → E-5 (sequential dependencies)

---

**Architecture Version:** 1.0  
**Generated:** 2026-04-15  
**Next Phase:** Phase 4 (Implementation)
