# Product Requirements Document: H-M3 Cross-Dimensional Correlation Analysis

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Author:** Anonymous
**Hypothesis:** H-M3 (MECHANISM)  
**Status:** Draft  

---

## Executive Summary

This PRD defines the requirements for implementing an experiment to validate that representation changes from targeted interventions cause correlated performance shifts across non-targeted trustworthiness dimensions. This experiment validates the third step of the causal chain: representation changes must propagate to measurable cross-dimensional effects.

**Success Criteria:** Non-random correlation structure between target dimension changes and non-target dimension changes (differs from control baseline at p<0.05).

**Continuation Context:** This experiment builds directly on h-m2 (COMPLETED, gate PASS), extending from single-dimension to multi-dimensional evaluation. H-M2 validated that interventions cause representation changes across all 24 layers. H-M3 validates that these representation changes translate to correlated performance shifts across multiple trustworthiness dimensions.

---

## Problem Statement

### Research Question
Do representation changes from fine-tuning on a target dimension (truthfulness) cause correlated performance shifts in non-targeted dimensions (fairness, robustness)?

### Current Gap
H-M2 validated that interventions cause representation changes, but correlation with performance was non-significant (r=0.150, p=0.28) when using aggregate single-dimension metrics. This experiment extends to multi-dimensional evaluation to test whether correlation structure exists when measuring across multiple trustworthiness dimensions simultaneously.

### Hypothesis Statement
Under representation changes from targeted interventions, if internal states affect multiple downstream capabilities, then performance on non-targeted dimensions D₂/D₃ shifts in correlated fashion, because prior multi-task learning work shows task interference from shared representations.

---

## Functional Requirements

### FR-1: Dataset Management (Multi-Dimensional Suite)
**Priority:** P0 (Blocking)

#### FR-1.1: TruthfulQA Dataset (Target Dimension - Inherited from H-M1/H-M2)
- **Source:** HuggingFace datasets (`truthfulqa/truthful_qa`)
- **Task:** Multiple-choice question answering (truthfulness evaluation)
- **Statistics:** 817 questions, 38 categories
- **Purpose:** Target dimension for intervention
- **Training Subset:** 500 samples (increased from h-m2's 100 for better coverage)
- **Evaluation Set:** Full 817 questions
- **Split:** Validation only (no train split)
- **Implementation:**
  ```python
  from datasets import load_dataset
  truthfulqa = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
  # Fields: type, category, question, best_answer, correct_answers, incorrect_answers, source
  ```

**Rationale:** Same dataset as h-m1/h-m2 for controlled comparison. Increased training size from 100→500 for more robust representation changes (lesson from h-m2).

#### FR-1.2: BBQ Dataset (Non-Target Dimension - Fairness/Bias)
- **Source:** HuggingFace datasets (`lighteval/bbq_helm`)
- **Task:** Bias detection in question answering
- **Statistics:** Multiple subsets across 9 social dimensions
- **Purpose:** Non-target dimension D₂ (fairness/bias)
- **Evaluation Set:** Full test split (500+ samples minimum)
- **Split:** Test only
- **Implementation:**
  ```python
  from datasets import load_dataset
  bbq = load_dataset("lighteval/bbq_helm", "all", split="test")
  # Fields: context, question, choices, gold_index
  ```

**Rationale:** Standard fairness benchmark for measuring bias in QA systems. Non-targeted dimension to measure cross-dimensional correlation.

#### FR-1.3: AdvGLUE Dataset (Non-Target Dimension - Robustness)
- **Source:** Official AdvGLUE benchmark (https://adversarialglue.github.io/)
- **Task:** Adversarial robustness evaluation across 5 GLUE tasks
- **Statistics:** 500-1000+ samples per task
- **Purpose:** Non-target dimension D₃ (adversarial robustness)
- **Evaluation Set:** Per benchmark specification
- **Attack Types:** Word-level, sentence-level, human-crafted adversarial examples
- **Implementation:**
  ```python
  # Custom loader based on official benchmark
  # Download from https://adversarialglue.github.io/
  # Implement evaluation wrapper for model inference
  ```

**Rationale:** Standard adversarial robustness benchmark. Completes 3-dimensional trustworthiness evaluation suite.

**Sample Size Policy** (addressing experiment scale guidance):
- **TruthfulQA**: Full validation set (817 questions) - statistically meaningful
- **BBQ**: Full test split (minimum 500+ samples)
- **AdvGLUE**: Standard benchmark splits (500-1000+ samples per task)
- **No trivial subsets**: All evaluations use standard benchmark splits

### FR-2: Model Management (Inherited from H-M1/H-M2)
**Priority:** P0 (Blocking)

#### FR-2.1: Baseline Model
- **Model:** GPT-2 (124M parameters)
- **Source:** HuggingFace Hub (`openai-community/gpt2`)
- **Architecture:** Transformer-based causal LM
  - Layers: 12
  - Hidden size: 768
  - Attention heads: 12
  - Context length: 1024 tokens
- **Precision:** FP32
- **Loading Method:** TransformerLens HookedTransformer (for activation extraction, inherited from h-m2)
- **Implementation:**
  ```python
  from transformer_lens import HookedTransformer
  
  # Load GPT-2 with TransformerLens for activation extraction
  model = HookedTransformer.from_pretrained("gpt2", device="cuda")
  ```

**Rationale:** H-M1 and H-M2 used GPT-2 successfully. H-M3 reuses the same model for controlled comparison (only evaluation scope changes).

**Continuation Justification:** Same base model ensures only evaluation scope changes from h-m2 (single-dimension → multi-dimensional). This is scientifically correct for testing causal chain Step 3.

### FR-3: Fine-Tuning Intervention (Inherited from H-M1/H-M2)
**Priority:** P0 (Blocking)

#### FR-3.1: LoRA Configuration (Proven in H-M1, Validated in H-M2)
- **Method:** Parameter-efficient fine-tuning using PEFT library
- **Rank:** 8
- **Alpha:** 16
- **Target Modules:** ["c_attn"] (GPT-2 attention modules)
- **Dropout:** 0.1
- **Bias:** none
- **Task Type:** CAUSAL_LM
- **Trainable Parameters:** 294,912 / 124,734,720 (0.24%)
- **Implementation:**
  ```python
  from peft import LoraConfig, get_peft_model
  
  lora_config = LoraConfig(
      r=8,
      lora_alpha=16,
      target_modules=["c_attn"],
      lora_dropout=0.1,
      bias="none",
      task_type="CAUSAL_LM"
  )
  
  model = get_peft_model(base_model, lora_config)
  ```

**Source:** H-M1 validation results, H-M2 validated representation changes

#### FR-3.2: Training Protocol (Inherited from H-M2 with Increased Sample Size)
- **Optimizer:** AdamW (betas=(0.9, 0.999), weight_decay=0.01)
- **Learning Rate:** 5e-5
- **Scheduler:** Constant (no decay)
- **Batch Size:** 4 per device
- **Gradient Accumulation:** 2 steps (effective batch=8)
- **Epochs:** 3
- **Training Samples:** 500 per replicate (increased from h-m2's 100)
- **Training Dataset:** TruthfulQA (target dimension only)
- **Loss Function:** Cross-entropy (causal language modeling)
- **Precision:** FP32
- **Random Seeds:** [42, 43, 44] (3 replicates for statistical robustness)

**Source:** H-M2 training protocol with increased sample size (100→500) for better representation coverage

**Rationale:** Exact replication of h-m2 intervention with increased training size ensures controlled comparison. Lessons from h-m2: larger sample needed for robust representation changes.

### FR-4: Multi-Dimensional Evaluation
**Priority:** P0 (Blocking)

#### FR-4.1: Pre-Intervention Baseline Evaluation
- **Timing:** Before LoRA fine-tuning
- **Dimensions:** All 3 dimensions evaluated simultaneously
- **Method:** 
  - TruthfulQA: MC1 accuracy (% truthful)
  - BBQ: Accuracy on bias detection
  - AdvGLUE: Robustness score (accuracy on adversarial examples)
- **Storage:** Baseline scores per dimension, per seed
- **Implementation:**
  ```python
  baseline_scores = {
      'truthfulness': evaluate_truthfulqa(base_model, truthfulqa_dataset),
      'fairness': evaluate_bbq(base_model, bbq_dataset),
      'robustness': evaluate_advglue(base_model, advglue_dataset)
  }
  ```

**Rationale:** Baseline measurements on all 3 dimensions before intervention enable Δ computation for correlation analysis.

#### FR-4.2: Post-Intervention Multi-Dimensional Evaluation
- **Timing:** After LoRA fine-tuning (3 epochs on TruthfulQA)
- **Dimensions:** All 3 dimensions re-evaluated
- **Input:** Same evaluation datasets as pre-intervention
- **Storage:** Post-intervention scores per dimension, per seed
- **Implementation:**
  ```python
  post_scores = {
      'truthfulness': evaluate_truthfulqa(finetuned_model, truthfulqa_dataset),
      'fairness': evaluate_bbq(finetuned_model, bbq_dataset),
      'robustness': evaluate_advglue(finetuned_model, advglue_dataset)
  }
  
  # Compute deltas
  deltas = {
      dim: post_scores[dim] - baseline_scores[dim]
      for dim in ['truthfulness', 'fairness', 'robustness']
  }
  ```

**Rationale:** Post-intervention evaluation on identical inputs enables direct Δ comparison for correlation analysis.

### FR-5: Representation Analysis (Inherited from H-M2)
**Priority:** P0 (Blocking)

#### FR-5.1: CKA Similarity Computation (Reuse H-M2 Pipeline)
- **Method:** Centered Kernel Alignment (CKA)
- **Library:** pytorch-cka
- **Layers:** 24 layers (12 attention + 12 residual)
  - Attention: `blocks.{i}.attn.hook_pattern` (i=0..11)
  - Hidden: `blocks.{i}.hook_resid_post` (i=0..11)
- **Formula:** CKA(K, L) = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))
- **Range:** [0, 1] where 1.0 = identical, 0.0 = completely different
- **Implementation:** Reuse h-m2 code
  ```python
  from cka import cka_score
  
  # Load saved activations from h-m2 pipeline
  pre_acts = torch.load(f"pre_activations_seed{seed}.pt")
  post_acts = torch.load(f"post_activations_seed{seed}.pt")
  
  cka_scores = {}
  for layer_name in layers_to_analyze:
      pre = pre_acts[layer_name].flatten(1)
      post = post_acts[layer_name].flatten(1)
      cka = cka_score(pre, post)
      cka_scores[layer_name] = cka.item()
  ```

**Source:** H-M2 validated TransformerLens + CKA pipeline

**Rationale:** Proven mechanism from h-m2. Reusing same analysis ensures consistency and controlled comparison.

### FR-6: Cross-Dimensional Correlation Analysis
**Priority:** P0 (Blocking)

#### FR-6.1: Per-Dimension Correlation Test
- **Method:** Pearson correlation coefficient
- **Library:** scipy.stats
- **Variables:**
  - X: Δ(Truthfulness) - change in target dimension
  - Y₁: Δ(Fairness) - change in non-target dimension 1
  - Y₂: Δ(Robustness) - change in non-target dimension 2
- **Correlations to Compute:**
  1. Δ(Truthfulness) vs. Δ(Fairness)
  2. Δ(Truthfulness) vs. Δ(Robustness)
  3. Δ(Fairness) vs. Δ(Robustness) (exploratory)
- **Null Hypothesis:** No correlation (ρ = 0)
- **Alternative:** Non-zero correlation exists (ρ ≠ 0)
- **Significance Level:** p < 0.05 (two-tailed)
- **Implementation:**
  ```python
  from scipy.stats import pearsonr
  
  # Correlations between dimension pairs
  r_fair, p_fair = pearsonr(
      deltas_across_seeds['truthfulness'],
      deltas_across_seeds['fairness']
  )
  
  r_robust, p_robust = pearsonr(
      deltas_across_seeds['truthfulness'],
      deltas_across_seeds['robustness']
  )
  
  print(f"Truthfulness-Fairness: r={r_fair:.3f}, p={p_fair:.3e}")
  print(f"Truthfulness-Robustness: r={r_robust:.3f}, p={p_robust:.3e}")
  ```

**Gate Criteria:**
- **PASS:** At least one dimension pair shows p < 0.05 (non-random correlation)
- **Strong PASS:** |ρ| > 0.2 with p < 0.05 (small-to-medium effect size)
- **PARTIAL:** Code runs but all correlations random (document as limitation)

**Note:** Gate type is SHOULD_WORK, so weak/random correlations still allow continuation to h-m4 with documented limitations.

#### FR-6.2: Layer-Wise Correlation Analysis
- **Method:** For each layer, correlate representation change with dimension-specific performance
- **Purpose:** Identify which layers most influence which dimensions
- **Variables:**
  - X: Representation change magnitude per layer (1 - CKA)
  - Y: Dimension-specific Δ performance
- **Output:** Correlation matrix (24 layers × 3 dimensions)
- **Implementation:**
  ```python
  layer_correlations = {}
  for layer_name in cka_scores.keys():
      rep_change = 1.0 - cka_scores[layer_name]
      layer_corrs = {}
      for dim in ['truthfulness', 'fairness', 'robustness']:
          r, p = pearsonr([rep_change], [deltas[dim]])
          layer_corrs[dim] = {'r': r, 'p': p}
      layer_correlations[layer_name] = layer_corrs
  ```

**Rationale:** Layer-wise analysis identifies dimension-specific representation patterns (exploratory analysis for paper discussion).

#### FR-6.3: Random Baseline Comparison
- **Method:** Permutation test
- **Purpose:** Verify correlation is non-random (differs from control)
- **Implementation:**
  1. Randomly permute dimension deltas
  2. Compute correlation with permuted values
  3. Repeat 1000 times to generate null distribution
  4. Compare observed correlation to null distribution
- **Statistical Test:** p-value = proportion of permuted correlations ≥ observed
- **Code:**
  ```python
  import numpy as np
  
  # Observed correlation
  r_obs, _ = pearsonr(deltas['truthfulness'], deltas['fairness'])
  
  # Permutation test
  null_dist = []
  for _ in range(1000):
      permuted = np.random.permutation(deltas['fairness'])
      r_null, _ = pearsonr(deltas['truthfulness'], permuted)
      null_dist.append(r_null)
  
  # Compare to null
  p_perm = np.mean(np.abs(null_dist) >= np.abs(r_obs))
  print(f"Permutation p-value: {p_perm:.3e}")
  ```

**Gate Criteria:** p_perm < 0.05 (differs from random baseline)

**Rationale:** Addresses hypothesis requirement "differs from control baseline at p<0.05".

### FR-7: Visualization Generation
**Priority:** P1 (Important)

#### FR-7.1: Required Figure (Gate Metrics)
- **Figure 1:** Correlation scatter plots
  - Panel A: Δ(Truthfulness) vs. Δ(Fairness)
  - Panel B: Δ(Truthfulness) vs. Δ(Robustness)
  - Each with regression line, correlation coefficient, p-value
  - 3 points per panel (one per seed)
  - Save to: `{hypothesis_folder}/figures/dimension_correlations.png`

#### FR-7.2: Additional Figures (Autonomous)
- **Figure 2:** Correlation matrix heatmap (24 layers × 3 dimensions)
- **Figure 3:** Layer progression - CKA change magnitude by layer depth
- **Figure 4:** Dimension performance - bar chart (pre/post across all 3 dimensions)
- **Figure 5:** Statistical significance heatmap (p-values for layer-dimension correlations)

**Rationale:** Phase 4 Coder MUST include figure generation logic. All figures saved to `{hypothesis_folder}/figures/`.

### FR-8: Code Reuse from H-M2
**Priority:** P0 (Blocking)

#### FR-8.1: Reuse H-M2 Validated Code
- **Source:** `h-m2/code/` directory
- **Components to Reuse:**
  1. `transformer_lens_wrapper.py` - activation extraction
  2. `representation_analyzer.py` - pre/post comparison
  3. `similarity.py` - CKA computation
  4. Training loop (LoRA fine-tuning)
- **Required Extensions:**
  1. Multi-dimensional evaluation (add BBQ, AdvGLUE loaders)
  2. Correlation analysis (scipy.stats integration)
  3. Cross-dimensional plotting

**Rationale:** H-M2 code is proven and validated. Extension (not rewrite) ensures controlled comparison.

**Known Bug to Fix:** Device mismatch in `transformer_lens_wrapper.py:convert_peft_to_hooked()` (documented in h-m2 validation report).

---

## Non-Functional Requirements

### NFR-1: Performance
- **Training Time:** ≤2 hours per replicate (3 replicates = 6 hours total for training)
- **Evaluation Time:** ≤1 hour per dimension per replicate (9 evaluations = 9 hours)
- **Total Runtime:** ≤15 hours for complete experiment (3 seeds × 5 hours)
- **GPU Memory:** ≤16GB per GPU (GPT-2 124M fits on single GPU)

### NFR-2: Reproducibility
- **Random Seeds:** Fixed seeds [42, 43, 44] for all operations
- **Deterministic Mode:** `torch.use_deterministic_algorithms(True)` where possible
- **Version Pinning:** All dependencies pinned in requirements.txt
- **Checkpoint Saving:** Save model checkpoints after training for replication

### NFR-3: Code Quality
- **Documentation:** Docstrings for all functions
- **Type Hints:** Python type hints throughout
- **Logging:** Structured logging (INFO level minimum)
- **Error Handling:** Try-except blocks for I/O operations
- **Testing:** Unit tests for data loaders and evaluation functions

### NFR-4: Resource Management
- **GPU Usage:** Single GPU per experiment (set CUDA_VISIBLE_DEVICES)
- **Disk Space:** ~10GB for model checkpoints + activations
- **Memory Cleanup:** Explicit `torch.cuda.empty_cache()` after training

---

## Success Criteria

### Primary Success Criteria (Gate Requirements)
1. **Code Execution:** All 3 dimensions evaluate without errors
2. **Correlation Analysis:** Statistical tests complete successfully
3. **Non-Random Structure:** At least one dimension pair shows p < 0.05
4. **Permutation Test:** Observed correlation differs from null (p_perm < 0.05)

### Secondary Success Criteria (Strong Evidence)
1. **Effect Size:** |ρ| > 0.2 for at least one dimension pair
2. **Multiple Correlations:** ≥2 dimension pairs significant
3. **Consistency:** Correlation direction consistent across 3 seeds
4. **Layer Patterns:** Layer-wise analysis identifies dimension-specific patterns

### SHOULD_WORK Gate Behavior
- **PASS:** Primary criteria met (non-random correlation found)
- **PARTIAL:** Code runs but correlations random (document limitation, proceed to h-m4)
- **FAIL:** Code execution errors or prerequisites not met

**Scientific Value:** Null results (random correlations) still valuable - demonstrates dimension independence, informs theoretical understanding.

---

## Dependencies

### Python Libraries
- `torch >= 2.0.0` - PyTorch for deep learning
- `transformers >= 4.30.0` - HuggingFace transformers
- `peft >= 0.4.0` - Parameter-efficient fine-tuning (LoRA)
- `datasets >= 2.12.0` - HuggingFace datasets
- `transformer-lens >= 1.0.0` - Activation extraction (validated in h-m2)
- `pytorch-cka >= 0.1.0` - CKA similarity computation
- `scipy >= 1.10.0` - Statistical tests (pearsonr, permutation)
- `numpy >= 1.24.0` - Numerical operations
- `matplotlib >= 3.7.0` - Plotting
- `seaborn >= 0.12.0` - Statistical visualization
- `pandas >= 2.0.0` - Data manipulation

### External Resources
- GPT-2 model weights (HuggingFace Hub)
- TruthfulQA dataset (HuggingFace datasets)
- BBQ dataset (HuggingFace datasets)
- AdvGLUE benchmark (download from official website)

### Infrastructure
- CUDA-compatible GPU (NVIDIA, ≥16GB VRAM)
- ~10GB disk space for checkpoints and activations
- Internet connection for dataset/model downloads

---

## Out of Scope

### Explicitly NOT Included
1. **Model Scaling:** Only GPT-2 (124M) - no multi-model families (reserved for h-m4)
2. **Additional Dimensions:** Only 3 dimensions (truthfulness, fairness, robustness)
3. **Alternative Interventions:** Only LoRA fine-tuning (same as h-m1/h-m2)
4. **Cross-Architecture:** Only GPT-2 transformer (h-m4 addresses architecture replication)
5. **Hyperparameter Search:** Fixed hyperparameters from h-m1/h-m2
6. **Baseline Comparison:** No comparison to h-m1 baselines (reserved for Phase 5)

### Deferred to Future Hypotheses
- **h-m4:** Multi-architecture replication (≥3/5 model families)
- **Phase 5:** Baseline comparison and statistical validation

---

## Risk Assessment

### Technical Risks

**Risk 1: AdvGLUE Integration Complexity**
- **Probability:** Medium
- **Impact:** High (blocks D₃ evaluation)
- **Mitigation:** 
  - Download benchmark early in implementation
  - Implement custom evaluation wrapper
  - Fallback: Use proxy robustness metric if official benchmark unavailable

**Risk 2: Weak Correlations (Random Structure)**
- **Probability:** Medium (h-m2 showed r=0.150, p=0.28)
- **Impact:** Low (SHOULD_WORK gate allows continuation)
- **Mitigation:**
  - Increase training sample size (100→500)
  - Use per-dimension correlation instead of aggregate
  - Document null result as scientific finding

**Risk 3: Device Mismatch Bug from H-M2**
- **Probability:** High (known bug from h-m2)
- **Impact:** Medium (causes runtime errors)
- **Mitigation:**
  - Fix device handling in `transformer_lens_wrapper.py`
  - Add explicit `.to(device)` calls
  - Test early in Phase 4

**Risk 4: Multi-Dimensional Evaluation Overhead**
- **Probability:** Low
- **Impact:** Medium (extends runtime)
- **Mitigation:**
  - Parallelize dimension evaluations where possible
  - Use batched inference
  - Budget 15 hours total (acceptable for research)

### Scientific Risks

**Risk 5: Correlation Direction Inconsistency Across Seeds**
- **Probability:** Medium
- **Impact:** Medium (weakens evidence)
- **Mitigation:**
  - Use 3 seeds for statistical robustness
  - Report per-seed results in addition to aggregate
  - Document inconsistency as limitation if occurs

---

## Validation Plan

### Phase 4 Validation Criteria
1. **Data Loading:** All 3 datasets load successfully
2. **Training:** LoRA fine-tuning completes for all 3 seeds
3. **Evaluation:** Multi-dimensional evaluation produces valid scores
4. **Representation:** CKA computation completes for all 24 layers
5. **Correlation:** Statistical tests produce valid p-values
6. **Permutation:** Null distribution generated successfully
7. **Visualization:** All required figures generated and saved

### Gate Validation (04_validation.md)
- **Primary:** At least one p < 0.05 (non-random correlation)
- **Secondary:** |ρ| > 0.2 (effect size)
- **Permutation:** p_perm < 0.05 (differs from random baseline)

---

## Appendix A: Reference Implementations

### A.1 H-M2 Validated Code (PRIMARY)
- **Source:** `h-m2/code/` directory
- **Components:** TransformerLens wrapper, CKA analysis, LoRA training
- **Status:** Validated in Phase 4 (PASS)
- **Use Case:** Foundation for h-m3 extension

### A.2 LibMTL Framework
- **URL:** https://github.com/median-research-group/LibMTL
- **Relevance:** Multi-task evaluation patterns
- **Use Case:** Structure for tracking multiple dimensions

### A.3 TruthfulQA Official
- **URL:** https://github.com/sylinrl/TruthfulQA
- **Use Case:** Dataset loading and evaluation metrics

### A.4 BBQ Benchmark
- **URL:** https://huggingface.co/datasets/lighteval/bbq_helm
- **Use Case:** Fairness dimension evaluation

### A.5 AdvGLUE Benchmark
- **URL:** https://adversarialglue.github.io/
- **Use Case:** Robustness dimension evaluation

---

## Appendix B: Changes from H-M2

### Key Differences
1. **Evaluation Scope:** Single-dimension → Multi-dimensional (3 dimensions)
2. **Training Sample:** 100 → 500 (better coverage)
3. **Correlation Analysis:** Aggregate → Per-dimension
4. **Statistical Test:** Simple correlation → Correlation + permutation test
5. **Datasets:** TruthfulQA only → TruthfulQA + BBQ + AdvGLUE

### Unchanged (Controlled Comparison)
1. **Model:** GPT-2 (124M)
2. **Intervention:** LoRA (r=8, α=16, c_attn)
3. **Training Protocol:** 3 epochs, AdamW, 5e-5 LR
4. **Representation Analysis:** TransformerLens + CKA
5. **Seeds:** [42, 43, 44]

---

*End of PRD v1.0*
