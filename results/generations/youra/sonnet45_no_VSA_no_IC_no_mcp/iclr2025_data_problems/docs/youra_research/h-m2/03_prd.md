# Product Requirements Document: h-m2 Transfer Stability Categorization

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Generated:** 2026-08-24  
**Prerequisites:** h-e1 (VALIDATED), h-m1 (VALIDATED)

---

## 1. Objective

Build a PoC implementation that tests whether curation technique transfer stability correlates with objective-independence. The system will compare objective-independent techniques (deduplication, perplexity filtering) against objective-dependent techniques (domain mixing, task filters) across pre-training → fine-tuning transfer.

**Success Criteria (SHOULD_WORK gate):**
- Objective-independent techniques: transfer delta ≤ 1.0%
- Objective-dependent techniques: transfer delta > 5.0%
- Non-overlapping 95% confidence intervals between categories

---

## 2. Functional Requirements

### 2.1 Data Pipeline

**FR-1: C4 Threshold Extraction**
- Extract documented filtering thresholds from C4 dataset:
  - Deduplication: n-gram size, similarity threshold
  - Perplexity: cutoff value, reference LM
  - Domain mixing: source proportions (if available)
- Output: `c4_thresholds.yaml` with extracted parameters
- Fallback: Use literature defaults if documentation incomplete

**FR-2: Dolly-15k Preprocessing**
- Load `databricks/databricks-dolly-15k` (15,015 samples)
- Split: 90% train (13,513), 10% validation (1,502)
- Verify instruction-response format integrity
- Output: `dolly_splits/train.jsonl`, `dolly_splits/val.jsonl`

**FR-3: Dataset Variant Generation (5 conditions)**

| Condition | Dedup | Perplexity | Domain Mix | Task Filter |
|-----------|-------|------------|------------|-------------|
| Baseline | No | No | No | No |
| Transferred-Indep | C4 threshold | C4 threshold | No | No |
| Tuned-Indep | Dolly-optimized | Dolly-optimized | No | No |
| Transferred-Dep | No | No | C4 ratios | C4 filters |
| Tuned-Dep | No | No | Dolly-optimized | Dolly-optimized |

Each variant outputs to `dolly_variants/<condition>/train.jsonl`

**FR-4: Objective-Independent Filter Implementation**
- **Deduplication:**
  - Algorithm: MinHash LSH or exact n-gram matching
  - Transferred: C4 n-gram size + similarity threshold
  - Tuned: Grid search over similarity ∈ [0.7, 0.8, 0.9, 0.95]
- **Perplexity filtering:**
  - Reference LM: GPT-2 or Kneser-Ney 5-gram
  - Transferred: C4 cutoff
  - Tuned: Grid search over cutoff ∈ [500, 1000, 1500, 2000]
- Validation metric: Held-out validation set performance proxy

**FR-5: Objective-Dependent Filter Implementation**
- **Primary: Domain mixing**
  - If Dolly multi-source variant available: Apply C4 domain ratios
  - Else: Fallback to instruction quality filters (FR-6)
- **Fallback: Task filters**
  - Prompt diversity (n-gram diversity score)
  - Response length filtering
  - Instruction clarity heuristics
- Tuning: Optimize via validation set instruction quality metrics

### 2.2 Model Training

**FR-6: Training Configuration (Fixed Across Conditions)**
- Base model: `meta-llama/Llama-2-7b-hf`
- Epochs: 3
- Batch size: 8 (effective 64 via gradient accumulation steps=8)
- Learning rate: 2e-5 (linear warmup 100 steps, cosine decay)
- Max sequence length: 512 tokens
- Optimizer: AdamW (β1=0.9, β2=0.999, ε=1e-8)
- Framework: Hugging Face Transformers + Accelerate

**FR-7: Fine-Tuning Execution**
- Train 5 separate models (one per dataset condition)
- Checkpoint: Save final epoch model to `models/<condition>/`
- Logging: Track training loss, validation perplexity
- Output: 5 fine-tuned checkpoints (~13GB each)

### 2.3 Evaluation

**FR-8: Benchmark Evaluation**
- Tool: lm-evaluation-harness
- Tasks: MMLU (14,042 test samples, 57 tasks), HellaSwag (10,042 validation samples)
- Run: All 5 models on both benchmarks
- Output: `results/mmlu_scores.csv`, `results/hellaswag_scores.csv`

**FR-9: Transfer Delta Computation**
```
delta = |acc_transferred - acc_tuned| / acc_tuned × 100%
```
- Independent delta: `|Transferred-Indep - Tuned-Indep| / Tuned-Indep × 100%`
- Dependent delta: `|Transferred-Dep - Tuned-Dep| / Tuned-Dep × 100%`
- Aggregate: Average across MMLU + HellaSwag
- Output: `results/transfer_deltas.csv`

**FR-10: Statistical Analysis**
- Bootstrap 95% confidence intervals (10k resamples)
- Welch's t-test: independent_delta vs. dependent_delta
- Cohen's d effect size
- Output: `results/statistical_analysis.yaml`

### 2.4 Validation

**FR-11: Gate Check**
- Primary criteria:
  - Objective-independent delta ≤ 1.0%
  - Objective-dependent delta > 5.0%
- Secondary criteria:
  - Non-overlapping CIs between categories
  - Both transferred and tuned > baseline by ≥2%
- Output: `results/gate_check.yaml` (PASS/FAIL status)

**FR-12: Validation Report**
- Document: `h-m2/04_validation.md`
- Sections: Hypothesis support, gate status, key findings, failure modes
- Visualizations: Delta comparison plots, category separation

---

## 3. Non-Functional Requirements

### 3.1 Performance
- **Training time:** ≤4 hours per model (A100 40GB)
- **Evaluation time:** ≤5 hours total (all models, both benchmarks)
- **Total GPU time:** ≤25 hours

### 3.2 Storage
- Dataset variants: ~500MB
- Model checkpoints: ~65GB (5 models × 13GB)
- Results: <1GB
- **Total:** ~66GB

### 3.3 Reproducibility
- Fixed random seeds for data splits, training, evaluation
- Versioned dependencies (transformers, datasets, lm-evaluation-harness)
- Logged hyperparameters in `train_config.yaml`

### 3.4 PoC Constraints
- **No production deployment:** Code runs locally/on research cluster
- **Minimal UI:** Command-line scripts only
- **No real-time inference:** Batch evaluation only
- **Mock substitute acceptable:** If full fine-tuning infeasible, use smaller model (e.g., GPT-2 355M) or fewer training samples (≥10k)

---

## 4. Out of Scope (PoC Phase)

- Multi-GPU distributed training (single GPU sufficient)
- Hyperparameter optimization beyond grid search
- Additional benchmarks (GLUE, SuperGLUE, etc.)
- Production-grade error handling, logging infrastructure
- Interactive dashboard for results visualization
- Pre-training from scratch (use publicly available checkpoints)

---

## 5. Deliverables

### 5.1 Code
- `scripts/extract_c4_thresholds.py`
- `scripts/prepare_dolly_variants.py`
- `scripts/train_llama.py`
- `scripts/evaluate_models.py`
- `scripts/compute_deltas.py`
- `scripts/statistical_analysis.py`

### 5.2 Data Artifacts
- `c4_thresholds.yaml`
- `dolly_splits/` (train, val)
- `dolly_variants/<condition>/` (5 conditions)
- `tuning_logs/independent.yaml`, `tuning_logs/dependent.yaml`

### 5.3 Model Artifacts
- `models/baseline/`
- `models/transferred_indep/`
- `models/tuned_indep/`
- `models/transferred_dep/`
- `models/tuned_dep/`

### 5.4 Results
- `results/mmlu_scores.csv`
- `results/hellaswag_scores.csv`
- `results/transfer_deltas.csv`
- `results/statistical_analysis.yaml`
- `results/gate_check.yaml`

### 5.5 Documentation
- `h-m2/04_validation.md` (validation report)
- `README.md` (setup, execution instructions)

---

## 6. Success Metrics

| Metric | Target | Priority |
|--------|--------|----------|
| Objective-independent delta | ≤ 1.0% | P0 (SHOULD_WORK gate) |
| Objective-dependent delta | > 5.0% | P0 (SHOULD_WORK gate) |
| CI separation | Non-overlapping | P0 (SHOULD_WORK gate) |
| Curation benefit | Tuned > Baseline by ≥2% | P1 (validates curation utility) |
| Statistical significance | p < 0.05 (Welch's t-test) | P1 |
| Cohen's d | > 0.8 (large effect) | P2 |

---

## 7. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| C4 thresholds undocumented | Medium | Use literature defaults; focus on categorical comparison |
| Dolly lacks multi-source variant | Medium | Fallback to instruction quality filters as objective-dependent technique |
| MMLU/HellaSwag insensitive to small deltas | High | Use full test sets (14k, 10k samples); bootstrap for statistical power |
| Excessive sample removal by filters | Medium | Monitor filtered counts; ensure ≥10k training samples remain |
| Tuning overfits validation set | Low | Use small val set (10%); report both val and test performance |

---

## 8. Dependencies

### 8.1 External Resources
- **Datasets:** C4 documentation, Dolly-15k (Hugging Face)
- **Models:** Llama-2-7B checkpoint (Hugging Face)
- **Tools:** lm-evaluation-harness (GitHub)

### 8.2 Compute
- GPU: 1× A100 40GB (or 2× RTX 4090)
- Storage: 70GB available
- RAM: 64GB recommended

### 8.3 Software
- Python 3.9+
- transformers, datasets, accelerate, deepspeed
- lm-evaluation-harness
- scipy, numpy (for statistical analysis)

---

## 9. Implementation Phases

| Phase | Tasks | Duration |
|-------|-------|----------|
| Data Prep | FR-1 to FR-5 | 2 days |
| Training | FR-6, FR-7 | 2 days |
| Evaluation | FR-8, FR-9, FR-10 | 1 day |
| Validation | FR-11, FR-12 | 0.5 days |
| **Total** | | **5.5 days** |

---

## 10. Acceptance Criteria

**PoC is complete when:**
1. All 5 dataset variants generated with documented filtering steps
2. All 5 fine-tuning runs completed without errors
3. MMLU + HellaSwag evaluation results available for all models
4. Transfer deltas computed with bootstrap CIs
5. Gate check passes OR failure analysis documented
6. 04_validation.md report generated

**Gate passes (SHOULD_WORK) when:**
- Objective-independent delta ≤ 1.0% (both MMLU and HellaSwag)
- Objective-dependent delta > 5.0% (both MMLU and HellaSwag)
- 95% CIs do not overlap between categories

**Gate fails (triggers taxonomy refinement) when:**
- Deltas overlap or reverse (independent > dependent)
- Insufficient statistical separation (p > 0.05)
- Both categories show <1% or >5% deltas (categorical distinction invalid)

---

**Document Version:** 1.0  
**Status:** Phase 3 - Implementation Planning  
**Next Phase:** Phase 4 - Coding & Validation
