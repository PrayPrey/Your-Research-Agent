# Product Requirements Document: h-m3 Implementation

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Implementation Tier:** PoC  
**Budget:** Minimal  
**Generated:** 2026-08-24

---

## 1. Objective

Quantify the quality-speed trade-off when using early-stage vs. late-stage embeddings for k-center greedy subset selection in instruction fine-tuning, validating that:
1. Late-stage (task-aligned) embeddings achieve ≥2% higher performance than early-stage at k=5,000
2. Early-stage embeddings are ≥3× faster than late-stage
3. Late-stage embeddings at k=10,000 remain within 1% of full-dataset baseline

---

## 2. System Architecture

### 2.1 Components

**A. Dataset Preparation Module**
- **Input:** Dolly-15k raw dataset (Hugging Face)
- **Output:** Train split (15,015 samples) formatted for embedding
- **Format:** `{"instruction": str, "response": str, "context": str}`
- **Storage:** `data/dolly_15k/raw/`

**B. Embedding Generation Module**
- **Input:** Formatted Dolly-15k samples
- **Models:**
  - Early: `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
  - Mid: `sentence-transformers/all-mpnet-base-v2` (768-dim)
  - Late: `hkunlp/instructor-large` (768-dim, task instruction: "Represent the instruction-response pair for diversity-based selection:")
- **Output:** 3 embedding matrices (15,015 × d_embed) saved as `.npy`
- **Storage:** `data/embeddings/{early,mid,late}_embeddings.npy`
- **Timing:** Record embedding compute time per model

**C. Subset Selection Module**
- **Input:** Embedding matrix, target size k
- **Algorithm:** k-center greedy (iterative farthest-point sampling)
  - Distance metric: Cosine
  - Initialization: Random seed (configurable for reproducibility)
  - Objective: Maximize min distance to nearest selected sample
- **Output:** Selected indices array (length k)
- **Storage:** `data/subsets/{stage}_k{size}_indices.npy`
- **Configurations:** 9 combinations (3 stages × 3 sizes: k=2000, 5000, 10000)
- **Timing:** Record selection compute time per configuration

**D. Fine-tuning Module**
- **Input:** Llama-2-7B base checkpoint + subset dataset
- **Training:**
  - Framework: Hugging Face Trainer
  - Epochs: 3
  - Batch size: 8 (gradient accumulation to effective batch 64)
  - Learning rate: 2e-5 (linear warmup 100 steps, cosine decay)
  - Max sequence length: 512
  - Optimizer: AdamW (β1=0.9, β2=0.999, ε=1e-8)
  - Mixed precision: bfloat16
- **Output:** 10 fine-tuned checkpoints (9 subsets + baseline)
- **Storage:** `models/{condition}/` (condition ∈ {baseline, early_k2000, ..., late_k10000})

**E. Evaluation Module**
- **Input:** Fine-tuned checkpoint
- **Benchmarks:**
  - MMLU: 14,042 test samples (5-shot)
  - HellaSwag: 10,042 validation samples (10-shot)
- **Framework:** lm-evaluation-harness 0.4+
- **Output:** JSON results per model
- **Storage:** `results/{condition}.json`

**F. Analysis Module**
- **Input:** All evaluation results + timing logs
- **Computations:**
  1. Stage-mismatch penalty: (Late_perf - Early_perf) / Late_perf × 100% at k=5,000
  2. Quality bound: |Late_k10000 - Baseline| / Baseline × 100%
  3. Compute cost ratio: Late_time / Early_time
  4. Pareto frontier: Plot performance vs. curation cost
- **Output:** Metrics table, plots (PNG), validation report
- **Storage:** `results/analysis/`

### 2.2 Data Flow

```
Dolly-15k (HF) 
  → Dataset Prep → formatted_dataset (15,015 samples)
  → Embedding Gen → {early,mid,late}_embeddings.npy
  → Subset Selection → 9 × indices arrays
  → Fine-tuning → 10 × Llama-2-7B checkpoints (9 subsets + baseline)
  → Evaluation → 10 × {MMLU, HellaSwag} results
  → Analysis → metrics table + plots + 04_validation.md
```

### 2.3 Configuration Management

**Global config (`config/experiment_config.yaml`):**
```yaml
dataset:
  name: databricks/databricks-dolly-15k
  split: train
  cache_dir: data/dolly_15k

embedding_models:
  early:
    model_id: sentence-transformers/all-MiniLM-L6-v2
    dimension: 384
  mid:
    model_id: sentence-transformers/all-mpnet-base-v2
    dimension: 768
  late:
    model_id: hkunlp/instructor-large
    dimension: 768
    task_instruction: "Represent the instruction-response pair for diversity-based selection:"

subset_sizes: [2000, 5000, 10000]

base_model:
  model_id: meta-llama/Llama-2-7b-hf
  cache_dir: models/llama2_base

training:
  num_train_epochs: 3
  per_device_train_batch_size: 8
  gradient_accumulation_steps: 8
  learning_rate: 2.0e-5
  warmup_steps: 100
  lr_scheduler_type: cosine
  max_seq_length: 512
  bf16: true
  output_dir: models/

evaluation:
  tasks: [mmlu, hellaswag]
  num_fewshot:
    mmlu: 5
    hellaswag: 10
  batch_size: 8
  device: cuda:0

random_seed: 42
```

---

## 3. Functional Requirements

### FR1: Dataset Preparation
- **FR1.1:** Download Dolly-15k from Hugging Face
- **FR1.2:** Verify dataset integrity (15,015 samples)
- **FR1.3:** Format samples as concatenated "instruction + response" text
- **FR1.4:** Save formatted dataset to disk cache

### FR2: Embedding Generation
- **FR2.1:** Load 3 embedding models (early/mid/late) from sentence-transformers
- **FR2.2:** Encode full Dolly-15k dataset with each model
- **FR2.3:** Save embedding matrices as `.npy` files
- **FR2.4:** Log compute time per model (wall-clock seconds)

### FR3: Subset Selection
- **FR3.1:** Implement k-center greedy algorithm
  - Initialize with random seed sample
  - Iteratively select farthest point in cosine distance
  - Track minimum distances efficiently (O(nk) time)
- **FR3.2:** Run selection for 9 configurations (3 stages × 3 sizes)
- **FR3.3:** Save selected indices to disk
- **FR3.4:** Log selection time per configuration

### FR4: Fine-tuning
- **FR4.1:** Load Llama-2-7B base model
- **FR4.2:** Train on 10 configurations:
  - 1× baseline (full 15,015 samples)
  - 9× subsets (early/mid/late × k=2000/5000/10000)
- **FR4.3:** Use identical hyperparameters across all runs
- **FR4.4:** Save each checkpoint to separate directory
- **FR4.5:** Log training time per configuration

### FR5: Evaluation
- **FR5.1:** Run lm-evaluation-harness on MMLU + HellaSwag
- **FR5.2:** Use standard few-shot settings (5-shot MMLU, 10-shot HellaSwag)
- **FR5.3:** Save results as JSON per model
- **FR5.4:** Extract accuracy metrics programmatically

### FR6: Analysis
- **FR6.1:** Compute stage-mismatch penalty at k=5,000
- **FR6.2:** Compute quality bound for late_k10000 vs. baseline
- **FR6.3:** Compute compute cost ratio (late / early)
- **FR6.4:** Generate Pareto frontier plot (performance vs. cost)
- **FR6.5:** Generate convergence curves (performance vs. k)
- **FR6.6:** Output validation report with pass/fail verdict

---

## 4. Non-Functional Requirements

### NFR1: Performance
- **NFR1.1:** Embedding generation ≤10 minutes per model (A100 40GB)
- **NFR1.2:** k-center greedy ≤5 minutes per configuration
- **NFR1.3:** Fine-tuning ≤2 hours per configuration (10 configs → 20 hours total)
- **NFR1.4:** Evaluation ≤30 minutes per model (10 models → 5 hours total)

### NFR2: Resource Constraints
- **NFR2.1:** GPU memory ≤40GB (single A100)
- **NFR2.2:** System RAM ≤64GB
- **NFR2.3:** Disk storage ≤500GB (models + data + checkpoints)

### NFR3: Reproducibility
- **NFR3.1:** Fixed random seeds (data split, model init, k-center init)
- **NFR3.2:** Version-pinned dependencies (requirements.txt)
- **NFR3.3:** Logged hyperparameters in config files
- **NFR3.4:** Timestamped outputs with git commit hash

### NFR4: Code Quality (PoC Standards)
- **NFR4.1:** Single script per module (no abstraction layers)
- **NFR4.2:** Minimal error handling (fail-fast on exceptions)
- **NFR4.3:** Print-based logging (no complex logging framework)
- **NFR4.4:** In-script docstrings for non-obvious operations

---

## 5. Success Criteria (SHOULD_WORK Gate)

### Primary Criteria
1. **Trade-off exists:** Late-stage embeddings achieve ≥2% higher aggregate performance than early-stage at k=5,000
   - **Metric:** (Late_MMLU - Early_MMLU) / Late_MMLU ≥ 0.02 at k=5,000
   
2. **Speed advantage:** Early-stage embedding ≥3× faster than late-stage
   - **Metric:** Time_late / Time_early ≥ 3.0
   
3. **Quality bound:** Late-stage at k=10,000 within 1% of baseline
   - **Metric:** |Late_k10000_MMLU - Baseline_MMLU| / Baseline_MMLU ≤ 0.01

### Secondary Criteria
1. **Pareto frontier identified:** Plot clearly shows trade-off curve
2. **Convergence behavior:** Performance increases monotonically with k
3. **Diversity metrics:** Late-stage subsets show higher avg pairwise distance than early-stage

### Failure Action
If primary criteria not met → route to EXPLORE with diagnostic:
- Criterion 1 fails: Embedding quality gap insufficient for k-center greedy
- Criterion 2 fails: Hardware differences or implementation inefficiency
- Criterion 3 fails: Late-stage embeddings degrade quality (contradicts hypothesis)

---

## 6. Constraints and Assumptions

### Constraints
- **C1:** Single GPU (no distributed training)
- **C2:** PoC mode (no multi-seed statistical tests for all conditions)
- **C3:** Public datasets only (Dolly-15k, MMLU, HellaSwag)
- **C4:** Pre-trained models only (no custom embedding training)

### Assumptions
- **A1:** k-center greedy is sensitive to embedding quality (validated in h-m2 context)
- **A2:** Instructor embeddings encode task-relevant structure better than MiniLM
- **A3:** 15k samples sufficient to measure 1-2% performance differences (validated in h-e1, h-m1)
- **A4:** Fine-tuning hyperparameters are robust across subset sizes (standard practice)

---

## 7. Out of Scope (PoC)

1. **Multi-seed robustness testing** — Production: n=5 seeds per condition
2. **Approximate k-center algorithms** — Production: Compare exact vs. CoreSets/FPS-batch
3. **Multi-stage pipeline testing** — Production: Test on pre-train → fine-tune → RLHF
4. **Embedding quality deep-dive** — Production: Analyze subset diversity, coverage metrics
5. **Alternative selection algorithms** — Production: Compare k-center vs. k-means clustering, herding

---

## 8. Dependencies

### Software
- Python 3.10+
- PyTorch 2.1+
- transformers 4.36+
- sentence-transformers 2.3+
- datasets 2.16+
- lm-evaluation-harness 0.4.1+
- numpy 1.24+
- scipy 1.11+
- matplotlib 3.8+ (plotting)

### Hardware
- 1× NVIDIA A100 40GB (or 2× V100 32GB)
- 64GB system RAM
- 500GB SSD storage

### Data
- Dolly-15k (~50MB) — Auto-download via Hugging Face
- Llama-2-7B (~13GB) — Requires meta-llama access approval
- MMLU/HellaSwag eval sets (~100MB) — Auto-download via lm-eval

### Prerequisite Validation
- h-e1 (VALIDATED) — Confirms 1% measurement precision
- h-m1 (VALIDATED) — Validates curation parameter sensitivity
- h-m2 (VALIDATED) — Demonstrates objective-dependence mechanism

---

## 9. Risks and Mitigations

### R1: Llama-2 access approval delay
- **Impact:** Cannot run fine-tuning
- **Mitigation:** Use GPT-2 (1.5B) as fallback base model
- **Likelihood:** Low (meta-llama access typically approved within 24h)

### R2: Embedding compute time underestimated
- **Impact:** Late-stage embeddings take >10 min
- **Mitigation:** Batch processing with GPU, pre-compute and cache
- **Likelihood:** Medium (Instructor-large is larger than MiniLM)

### R3: k-center greedy OOM on large k
- **Impact:** Cannot select k=10,000 subsets
- **Mitigation:** Chunked distance computation, approximate algorithm fallback
- **Likelihood:** Low (15k dataset fits in memory)

### R4: Fine-tuning crashes due to OOM
- **Impact:** Cannot train on full baseline
- **Mitigation:** Reduce batch size or use gradient checkpointing
- **Likelihood:** Low (Llama-2-7B + batch 8 fits in 40GB)

### R5: MMLU/HellaSwag performance too noisy
- **Impact:** Cannot detect 2% differences
- **Mitigation:** Use aggregate metric (MMLU + HellaSwag) / 2, validated in h-e1
- **Likelihood:** Low (h-e1/h-m1 demonstrated 1% sensitivity)

---

## 10. Deliverables

### Code Artifacts
1. `scripts/01_prepare_dataset.py` — Load and format Dolly-15k
2. `scripts/02_generate_embeddings.py` — Embed corpus with 3 models
3. `scripts/03_k_center_greedy.py` — Subset selection
4. `scripts/04_finetune_llama.py` — Train Llama-2-7B on subsets
5. `scripts/05_evaluate_models.sh` — lm-eval wrapper script
6. `scripts/06_analyze_results.py` — Metrics extraction + plotting
7. `config/experiment_config.yaml` — Centralized configuration
8. `requirements.txt` — Pinned dependencies

### Data Artifacts
1. `data/dolly_15k/` — Cached dataset
2. `data/embeddings/` — 3 embedding matrices (.npy)
3. `data/subsets/` — 9 selected indices arrays
4. `models/` — 10 fine-tuned checkpoints
5. `results/` — 10 lm-eval JSON outputs

### Analysis Artifacts
1. `results/analysis/metrics_table.csv` — Performance + cost matrix
2. `results/analysis/pareto_frontier.png` — Quality vs. cost plot
3. `results/analysis/convergence_curves.png` — Performance vs. k
4. `results/analysis/stage_mismatch_penalty.png` — Delta across conditions

### Documentation
1. `04_validation.md` — Full experimental results, pass/fail verdict, interpretation

---

## 11. Execution Timeline (PoC)

| Phase | Tasks | Duration | Dependencies |
|-------|-------|----------|--------------|
| Setup | Install dependencies, download base model | 1 hour | None |
| Data prep | Load Dolly-15k, format samples | 30 min | Setup |
| Embedding | Generate 3 embedding sets | 30 min | Data prep |
| Selection | Run k-center greedy (9 configs) | 1 hour | Embedding |
| Fine-tuning | Train 10 models (parallel if multi-GPU) | 20 hours | Selection |
| Evaluation | Run lm-eval on 10 models | 5 hours | Fine-tuning |
| Analysis | Compute metrics, generate plots | 2 hours | Evaluation |
| Documentation | Write 04_validation.md | 2 hours | Analysis |
| **Total** | | **32 hours** | Sequential (3-4 days wall-clock) |

**Critical path:** Fine-tuning (parallelizable across GPUs if available)

---

## 12. Validation Checklist

- [ ] Dolly-15k loaded and verified (15,015 samples)
- [ ] 3 embedding matrices generated and saved
- [ ] 9 subset selections completed (indices saved)
- [ ] Baseline + 9 subset fine-tuning runs completed
- [ ] All 10 models evaluated on MMLU + HellaSwag
- [ ] Stage-mismatch penalty computed (≥2% at k=5000)
- [ ] Compute cost ratio verified (≥3×)
- [ ] Quality bound verified (≤1% at k=10000)
- [ ] Pareto frontier plot generated
- [ ] 04_validation.md written with pass/fail verdict

---

**END OF PRD**
