# Experiment Brief: h-m2 (Transfer Stability Correlates with Objective-Independence)

**Generated:** 2026-08-24  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-e1 (VALIDATED), h-m1 (VALIDATED)

---

## 1. Hypothesis Statement

Under foundation model training, if curation techniques are categorized by their dependence on stage objectives, then objective-independent techniques (deduplication, outlier removal) will show robust transfer (≤1% delta) while objective-dependent techniques (domain mixing, task filters) will show poor transfer (>5% degradation), because optimal configurations for objective-dependent techniques vary with each stage's distinct optimization target.

---

## 2. Research Background

### 2.1 Core Question

Does the objective-dependence of a curation technique predict its transfer stability across training stages?

### 2.2 Key Insight

**Categorization principle:** Techniques that address universal data quality (hygiene) should transfer robustly, while techniques optimized for stage-specific goals (domain balance, task alignment) should degrade when transferred.

### 2.3 Expected Outcome

Clear separation between technique categories:
- **Objective-independent (hygiene):** ≤1% performance delta when transferred
- **Objective-dependent (strategic):** >5% performance degradation when transferred

### 2.4 Implementation Resources

**MCP Status:** Archon, Exa, Serena MCP unavailable  
**Resource basis:** Verification plan specification (02b_verification_plan.md lines 150-178)

**Known implementations:**
- C4 filtering pipeline (deduplication, perplexity-based removal)
- Dolly-15k instruction dataset (standard fine-tuning target)
- lm-evaluation-harness (MMLU, HellaSwag benchmarks)

**Technique implementations:**
- Exact deduplication: MinHash LSH or exact n-gram matching
- Perplexity filtering: Kneser-Ney LM or GPT-2 perplexity scorer
- Domain mixing: Dataset composition ratios (if multi-source available)

---

## 3. Experimental Design

### 3.1 Dataset Specification

#### Pre-training Source: C4 (Colossal Clean Crawled Corpus)
- **Type:** standard
- **Size:** ~800GB web text (training), ~365M documents
- **Preprocessing:** Documented deduplication + perplexity filtering
- **Rationale:** Established filtering pipeline allows threshold extraction

**Thresholds to extract:**
1. Deduplication: n-gram size (e.g., 13-gram), similarity threshold (e.g., 0.8)
2. Perplexity cutoff: e.g., remove samples with perplexity > 1000 (Kneser-Ney 5-gram)
3. Domain mixing: web/news/forums proportions (if documented)

#### Fine-tuning Target: Dolly-15k
- **Type:** standard
- **Size:** 15,015 instruction-response pairs
- **Source:** databricks/databricks-dolly-15k (Hugging Face)
- **Domain:** Open-domain instruction following
- **Rationale:** Standard instruction tuning benchmark, sufficient size for statistical analysis

**Dataset variants (5 conditions):**
1. **Baseline:** No curation (15,015 samples)
2. **Transferred-Independent:** C4 dedup + perplexity thresholds applied
3. **Tuned-Independent:** Stage-optimized dedup + perplexity thresholds
4. **Transferred-Dependent:** C4 domain mixing ratios (if applicable)
5. **Tuned-Dependent:** Dolly-optimized domain/quality filters

**Evaluation datasets:**
- **MMLU:** 14,042 test samples across 57 tasks (reasoning, knowledge)
- **HellaSwag:** 10,042 validation samples (commonsense reasoning)
- **Sample size rationale:** Full standard test sets provide statistical power for detecting 1-5% differences

### 3.2 Model Specification

**Base model:** Llama-2-7B
- **Source:** Meta AI (meta-llama/Llama-2-7b-hf)
- **Pre-training checkpoint:** After C4 pre-training (or closest public checkpoint)
- **Parameters:** 6.7B
- **Context length:** 4096 tokens
- **Rationale:** Mid-size model balances feasibility with meaningful measurement; widely used for transfer studies

**Fine-tuning configuration:**
- Epochs: 3 (standard for instruction tuning)
- Batch size: 8 (effective batch 64 via gradient accumulation)
- Learning rate: 2e-5 (linear warmup 100 steps, cosine decay)
- Max sequence length: 512 tokens
- Optimizer: AdamW (β1=0.9, β2=0.999, ε=1e-8)
- **Fixed across all conditions:** Identical hyperparameters to isolate curation effects

### 3.3 Technique Categorization

#### Objective-Independent (Low-Level Hygiene)
1. **Exact deduplication**
   - **Operation:** Remove duplicate or near-duplicate samples (n-gram overlap or MinHash)
   - **Objective-dependence:** None (duplicate removal improves data efficiency regardless of stage goal)
   - **Transferred threshold:** C4 n-gram size + similarity cutoff
   - **Tuning target:** Maximize validation performance via grid search

2. **Perplexity-based outlier removal**
   - **Operation:** Remove samples with high perplexity under reference LM
   - **Objective-dependence:** None (outlier removal addresses data quality universally)
   - **Transferred threshold:** C4 perplexity cutoff
   - **Tuning target:** Maximize validation performance via grid search

#### Objective-Dependent (High-Level Strategy)
1. **Domain mixing ratios**
   - **Operation:** Balance data sources (web/books/code/scientific) or content types
   - **Objective-dependence:** High (optimal mix varies: pre-training favors diversity, instruction tuning favors alignment)
   - **Transferred configuration:** C4 domain proportions (if documented)
   - **Tuning target:** Optimize instruction quality via held-out validation
   - **Fallback:** If Dolly lacks multi-source variant, use instruction quality filters (length, prompt diversity)

2. **Task-specific filters**
   - **Operation:** Filter samples by task relevance, safety, instruction clarity
   - **Objective-dependence:** High (task definition changes per stage)
   - **Transferred configuration:** C4 content filters (if applicable)
   - **Tuning target:** Instruction quality metrics (prompt diversity, response coherence)

### 3.4 Experimental Conditions

| Condition | Dedup | Perplexity | Domain Mix | Task Filter | Expected Delta |
|-----------|-------|------------|------------|-------------|----------------|
| Baseline | No | No | No | No | Reference |
| Transferred-Indep | C4 threshold | C4 threshold | No | No | ≤1% |
| Tuned-Indep | Dolly-optimized | Dolly-optimized | No | No | ≤1% |
| Transferred-Dep | No | No | C4 ratios | C4 filters | >5% |
| Tuned-Dep | No | No | Dolly-optimized | Dolly-optimized | >5% |

**Comparison pairs:**
- **Objective-independent delta:** |Transferred-Indep - Tuned-Indep| / Tuned-Indep × 100%
- **Objective-dependent delta:** |Transferred-Dep - Tuned-Dep| / Tuned-Dep × 100%
- **Category separation:** Test if independent_delta << dependent_delta

### 3.5 Baseline Configuration

**Reference:** No curation (Baseline condition)

**Comparison targets:**
1. Stage-tuned independent techniques (upper bound for objective-independent)
2. Stage-tuned dependent techniques (upper bound for objective-dependent)

**Performance expectations:**
- Baseline < Transferred < Tuned (for both categories)
- Transferred-Indep ≈ Tuned-Indep (≤1% gap)
- Transferred-Dep << Tuned-Dep (>5% gap)

---

## 4. Metrics and Success Criteria

### 4.1 Primary Metrics

**Performance delta (transfer degradation):**
```
delta = |acc_transferred - acc_tuned| / acc_tuned × 100%
```

**Measured for:**
- MMLU accuracy (57-task average)
- HellaSwag accuracy

**Aggregation:** Average across both benchmarks

### 4.2 Success Criteria (PoC - Direction-based)

✅ **Primary (SHOULD_WORK gate):**
- Objective-independent techniques: delta ≤ 1.0%
- Objective-dependent techniques: delta > 5.0%

✅ **Secondary:**
- Non-overlapping confidence intervals between categories (bootstrap 95% CI)
- Both transferred and tuned conditions > baseline by ≥2% (validates curation benefit)

❌ **Failure modes:**
- Overlapping deltas (no clear categorical separation)
- Objective-independent delta > 5% (hygiene not universal)
- Objective-dependent delta < 1% (strategy surprisingly robust)

### 4.3 Statistical Analysis

**Significance testing:**
1. Bootstrap 95% confidence intervals (10k resamples)
2. Welch's t-test for category separation (independent vs. dependent deltas)
3. Effect size: Cohen's d for delta differences

**Minimum detectable effect:** 1% performance delta (based on MMLU/HellaSwag test set sizes)

---

## 5. Implementation Plan

### 5.1 Data Preparation (Epic 1)

**Task 1.1: Extract C4 thresholds**
- Read C4 documentation (https://huggingface.co/datasets/c4)
- Extract: dedup n-gram size, similarity threshold, perplexity cutoff, domain ratios
- **Deliverable:** `c4_thresholds.yaml`

**Task 1.2: Load Dolly-15k**
- Download: `databricks/databricks-dolly-15k`
- Verify: 15,015 samples, instruction-response format
- Split: train (90%, 13,513 samples), validation (10%, 1,502 samples)
- **Deliverable:** `dolly_splits/` (train.jsonl, val.jsonl)

**Task 1.3: Create baseline dataset**
- No filtering applied
- **Deliverable:** `dolly_baseline/` (train: 13,513, val: 1,502)

**Task 1.4: Apply transferred-independent filters**
- Dedup: C4 n-gram threshold on Dolly train
- Perplexity: C4 cutoff on Dolly train (use GPT-2 or Kneser-Ney LM)
- **Deliverable:** `dolly_transferred_indep/` (expect ~13,000 samples after filtering)

**Task 1.5: Tune independent filters**
- Grid search: dedup similarity ∈ [0.7, 0.8, 0.9, 0.95]
- Grid search: perplexity cutoff ∈ [500, 1000, 1500, 2000]
- Evaluate on validation set (train small probe model or use heuristic)
- **Deliverable:** `dolly_tuned_indep/`, `tuning_logs/independent.yaml`

**Task 1.6: Apply transferred-dependent filters**
- If C4 domain ratios available: resample Dolly by category (if multi-source variant exists)
- Else: apply C4 content filters (if documented)
- **Deliverable:** `dolly_transferred_dep/`

**Task 1.7: Tune dependent filters**
- Optimize instruction quality filters (prompt diversity, length, safety)
- Use validation set metrics (perplexity, diversity)
- **Deliverable:** `dolly_tuned_dep/`, `tuning_logs/dependent.yaml`

### 5.2 Model Training (Epic 2)

**Task 2.1: Setup training environment**
- Install: transformers, accelerate, deepspeed
- Load Llama-2-7B checkpoint
- Configure: 3 epochs, lr=2e-5, batch=8, grad_accum=8
- **Deliverable:** `train_config.yaml`

**Task 2.2: Fine-tune on baseline**
- Train on `dolly_baseline/train.jsonl`
- **Deliverable:** `models/baseline/` checkpoint

**Task 2.3: Fine-tune on transferred-independent**
- Train on `dolly_transferred_indep/train.jsonl`
- **Deliverable:** `models/transferred_indep/` checkpoint

**Task 2.4: Fine-tune on tuned-independent**
- Train on `dolly_tuned_indep/train.jsonl`
- **Deliverable:** `models/tuned_indep/` checkpoint

**Task 2.5: Fine-tune on transferred-dependent**
- Train on `dolly_transferred_dep/train.jsonl`
- **Deliverable:** `models/transferred_dep/` checkpoint

**Task 2.6: Fine-tune on tuned-dependent**
- Train on `dolly_tuned_dep/train.jsonl`
- **Deliverable:** `models/tuned_dep/` checkpoint

### 5.3 Evaluation (Epic 3)

**Task 3.1: Setup lm-evaluation-harness**
- Install: https://github.com/EleutherAI/lm-evaluation-harness
- Configure tasks: MMLU, HellaSwag
- **Deliverable:** `eval_config.yaml`

**Task 3.2: Evaluate all conditions on MMLU**
- Run: 5 models × 57 MMLU tasks (14,042 total samples)
- **Deliverable:** `results/mmlu_scores.csv`

**Task 3.3: Evaluate all conditions on HellaSwag**
- Run: 5 models on 10,042 validation samples
- **Deliverable:** `results/hellaswag_scores.csv`

**Task 3.4: Compute transfer deltas**
- Calculate: |transferred - tuned| / tuned × 100%
- For: objective-independent, objective-dependent
- **Deliverable:** `results/transfer_deltas.csv`

**Task 3.5: Statistical analysis**
- Bootstrap 95% CI (10k resamples)
- Welch's t-test: independent_delta vs. dependent_delta
- Cohen's d effect size
- **Deliverable:** `results/statistical_analysis.yaml`

### 5.4 Validation (Epic 4)

**Task 4.1: Check success criteria**
- Objective-independent delta ≤ 1%? (MMLU, HellaSwag)
- Objective-dependent delta > 5%?
- Non-overlapping CIs?
- **Deliverable:** `results/gate_check.yaml`

**Task 4.2: Generate validation report**
- Summary: hypothesis support, gate status, key findings
- Plots: delta comparison, category separation
- **Deliverable:** `h-m2/04_validation.md`

---

## 6. Resource Requirements

### 6.1 Compute

**Training:**
- 5 fine-tuning runs × 3 epochs × 13k samples
- GPU: 1× A100 (40GB) or 2× RTX 4090
- Time estimate: ~3 hours per run (15 hours total)

**Evaluation:**
- 5 models × (14k MMLU + 10k HellaSwag) samples
- Time estimate: ~5 hours total

**Total GPU hours:** ~20 hours (A100 equivalent)

### 6.2 Storage

- Dolly-15k variants: ~5 × 100MB = 500MB
- Model checkpoints: 5 × 13GB = 65GB
- Evaluation results: <1GB
- **Total:** ~66GB

### 6.3 Data Sources

- C4 documentation: https://huggingface.co/datasets/c4
- Dolly-15k: https://huggingface.co/datasets/databricks/databricks-dolly-15k
- Llama-2-7B: https://huggingface.co/meta-llama/Llama-2-7b-hf
- lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness

---

## 7. Risk Mitigation

### 7.1 Dataset Risks

**Risk:** C4 thresholds not documented precisely
- **Mitigation:** Use reasonable estimates from literature (e.g., perplexity > 1000); primary goal is categorical comparison, not absolute transfer

**Risk:** Dolly lacks multi-source variant for domain mixing test
- **Mitigation:** Fallback to instruction quality filters (prompt diversity, length, safety) as objective-dependent technique

### 7.2 Measurement Risks

**Risk:** MMLU/HellaSwag insensitive to 1-5% differences
- **Mitigation:** Use full test sets (14k, 10k samples) for statistical power; bootstrap CIs detect small effects

**Risk:** Category overlap (deltas not clearly separated)
- **Mitigation:** Test multiple objective-dependent techniques (domain mix + task filters) to increase separation signal

### 7.3 Implementation Risks

**Risk:** Deduplication/perplexity filtering removes excessive samples
- **Mitigation:** Monitor filtered sample counts; ensure ≥10k training samples remain for stable fine-tuning

**Risk:** Stage-tuning overfits to validation set
- **Mitigation:** Use small validation set (10%); report both val and test performance

---

## 8. Deliverables

### 8.1 Code
- `scripts/extract_c4_thresholds.py`
- `scripts/prepare_dolly_variants.py`
- `scripts/train_llama.py`
- `scripts/evaluate_models.py`
- `scripts/compute_deltas.py`

### 8.2 Data
- `c4_thresholds.yaml`
- `dolly_splits/` (train, val)
- `dolly_variants/` (5 conditions)
- `tuning_logs/` (grid search results)

### 8.3 Models
- `models/baseline/`
- `models/transferred_indep/`
- `models/tuned_indep/`
- `models/transferred_dep/`
- `models/tuned_dep/`

### 8.4 Results
- `results/mmlu_scores.csv`
- `results/hellaswag_scores.csv`
- `results/transfer_deltas.csv`
- `results/statistical_analysis.yaml`
- `results/gate_check.yaml`

### 8.5 Reports
- `h-m2/04_validation.md` (hypothesis support, gate status, key findings)

---

## 9. Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Data preparation (Epic 1) | 2 days | C4 documentation, Dolly download |
| Model training (Epic 2) | 2 days | Epic 1 complete |
| Evaluation (Epic 3) | 1 day | Epic 2 complete |
| Validation (Epic 4) | 0.5 days | Epic 3 complete |
| **Total** | **5.5 days** | Sequential |

**Critical path:** Data prep → Training → Evaluation → Validation

---

## 10. Next Steps

**Immediate actions:**
1. Extract C4 filtering thresholds from documentation
2. Download and split Dolly-15k
3. Implement deduplication and perplexity filtering scripts
4. Begin stage-tuning grid search on validation set

**Phase 3 input:**
- This experiment brief (`02c_experiment_brief.md`)
- Hypothesis statement and prerequisites from verification plan
- Success criteria (≤1% independent, >5% dependent deltas)

**Phase 4 validation trigger:**
- All 5 fine-tuning runs complete
- MMLU + HellaSwag evaluation finished
- Transfer deltas computed

---

**Document Status:** Phase 2C Complete  
**Ready for Phase 3:** Yes (implementation planning)  
**Gate Type:** SHOULD_WORK (failure triggers taxonomy refinement)
