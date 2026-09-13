# Product Requirements Document: H-M1 Target Dimension Improvement Validation

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Author:** Anonymous
**Hypothesis:** H-M1 (MECHANISM)  
**Status:** Draft  

---

## Executive Summary

This PRD defines the requirements for implementing an experiment to validate that targeted interventions (fine-tuning on TruthfulQA) measurably improve performance on the target dimension. This experiment validates the first step of the causal chain: parameter updates must actually affect the target dimension for cross-dimensional effects to occur.

**Success Criteria:** Mean Δ(Target) > 0 with p<0.05 across replicates.

**Continuation Context:** This experiment builds directly on h-e1 (COMPLETED, gate PASS), reusing the proven GPT-2 + LoRA configuration but focusing solely on target dimension improvement rather than cross-dimensional correlations.

---

## Problem Statement

### Research Question
Do parameter updates from fine-tuning on a target dimension (TruthfulQA) actually improve performance on that dimension?

### Current Gap
H-E1 validated that cross-dimensional effects exist, but did not validate the mechanism's first step: that interventions actually improve the target dimension. This is prerequisite for the causal chain (H-M1 → H-M2 → H-M3 → H-M4).

### Hypothesis Statement
Under targeted intervention (e.g., fine-tuning on TruthfulQA), if gradient descent updates model parameters, then performance on target dimension D₁ improves measurably, because standard fine-tuning mechanics reshape weight distributions to minimize loss on training data.

---

## Functional Requirements

### FR-1: Dataset Management
**Priority:** P0 (Blocking)

#### FR-1.1: TruthfulQA Dataset (Target Dimension)
- **Source:** HuggingFace datasets via EleutherAI lm-evaluation-harness
- **Task:** Multiple-choice question answering (truthfulness evaluation)
- **Statistics:** 817 questions, MC2 (multi-true) format
- **Baseline Performance:** GPT-3 175B achieves MC2=0.33
- **Split:** Validation only (no train split)
- **Implementation:**
  ```python
  from lm_eval import evaluator
  results = evaluator.simple_evaluate(
      model="hf-causal",
      model_args="pretrained=<model_path>",
      tasks=["truthfulqa_mc2"],
      num_fewshot=0
  )
  ```

**Note:** H-M1 uses ONLY TruthfulQA (target dimension). BBQ and AdvGLUE are NOT used in this experiment (those were for H-E1's cross-dimensional analysis).

### FR-2: Model Management
**Priority:** P0 (Blocking)

#### FR-2.1: Baseline Model
- **Model:** GPT-2 (124M parameters)
- **Source:** HuggingFace Hub (`openai-community/gpt2`)
- **Architecture:** Transformer-based causal LM (12 layers, 768 hidden, 12 heads)
- **Context Length:** 1024 tokens
- **Precision:** FP16 (mixed precision training)
- **Rationale:** Continuation from h-e1 for controlled comparison
- **Implementation:**
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  model = AutoModelForCausalLM.from_pretrained("openai-community/gpt2")
  tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2")
  ```

**Note:** Original plan was Llama-3-8B, but h-e1 used GPT-2 (no authentication required). H-M1 reuses GPT-2 for controlled comparison.

### FR-3: Fine-Tuning Intervention
**Priority:** P0 (Blocking)

#### FR-3.1: LoRA Configuration (Inherited from h-e1)
- **Method:** Parameter-efficient fine-tuning using PEFT library
- **Rank:** 8 (proven in h-e1)
- **Alpha:** 16 (adjusted from h-e1's alpha=8 based on PEFT documentation)
- **Target Modules:** ["c_attn"] (GPT-2 attention modules)
- **Dropout:** 0.1
- **Bias:** none
- **Task Type:** CAUSAL_LM
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

#### FR-3.2: Training Configuration (Inherited from h-e1)
- **Optimizer:** AdamW (betas=(0.9, 0.999), eps=1e-8)
- **Learning Rate:** 1e-4
- **Schedule:** Cosine annealing (Lightning AI experiments showed improvement over constant)
- **Batch Size:** 4 per device
- **Epochs:** 3 (proven sufficient in h-e1)
- **Precision:** FP16 (mixed precision)
- **Loss Function:** Causal language modeling (next-token prediction)
- **Seeds:** [42, 43, 44] (3 replicates for statistical significance)

**Rationale:** Reuse h-e1's proven configuration for controlled comparison. Only difference is focus (target dimension improvement vs cross-dimensional effects).

### FR-4: Evaluation Metrics
**Priority:** P0 (Blocking)

#### FR-4.1: Primary Metric (Dependent Variable)
- **Metric:** Δ(Target) = TruthfulQA MC2 (post-intervention) - TruthfulQA MC2 (pre-intervention)
- **Measurement:** Paired difference scores for each replicate
- **Statistical Test:** Paired t-test (H₀: μ(Δ) = 0)
- **Significance Threshold:** p < 0.05 (two-tailed)
- **Expected Baseline:** GPT-2 (124M) ≈ 0.40-0.50 MC2 (estimated from GPT-3 baseline)
- **Expected Improvement:** +5-10% MC2 score (based on Lightning AI LoRA experiments)

#### FR-4.2: Secondary Check
- **Metric:** Directional consistency (% replicates with Δ > 0)
- **Threshold:** ≥70% of replicates show positive improvement
- **Purpose:** Verify improvement direction is consistent

#### FR-4.3: TruthfulQA MC2 Metric Details
- **Definition:** Normalized total probability assigned to set of true answers
- **Source:** sylinrl/TruthfulQA official benchmark
- **Evaluation Library:** EleutherAI lm-evaluation-harness v0.4.*

### FR-5: Experiment Workflow
**Priority:** P0 (Blocking)

#### FR-5.1: Pre-Intervention Evaluation
1. Load base GPT-2 model
2. Evaluate on TruthfulQA MC2 using lm-eval harness
3. Record baseline score (single measurement, no fine-tuning)
4. Store as `pre_score`

#### FR-5.2: Intervention Loop (N=3 replicates)
For each seed in [42, 43, 44]:
1. Initialize GPT-2 with LoRA adapter (r=8, alpha=16)
2. Fine-tune on TruthfulQA training data (3 epochs, lr=1e-4)
3. Evaluate fine-tuned model on TruthfulQA MC2
4. Record post-intervention score as `post_score`
5. Calculate Δ(Target) = post_score - pre_score
6. Store (seed, pre_score, post_score, Δ) tuple

#### FR-5.3: Statistical Analysis
1. Extract Δ(Target) scores for all 3 replicates
2. Compute mean(Δ) and std(Δ)
3. Perform paired t-test: t-statistic, p-value
4. Check significance: p < 0.05
5. Check directional consistency: count(Δ > 0) / 3 ≥ 0.70

**Gate Evaluation:**
- **PASS:** Mean Δ(Target) > 0 AND p < 0.05
- **FAIL:** Either condition not met → PIVOT to alternative interventions

### FR-6: Visualization
**Priority:** P1 (Important)

#### FR-6.1: Required Figures
- **Gate Metrics Comparison:** Target vs actual metrics bar chart (mandatory)

#### FR-6.2: Additional Figures (Recommended)
1. **Pre/Post TruthfulQA Scores:** Bar chart with error bars
   - X-axis: [Baseline (Pre), Fine-tuned (Post)]
   - Y-axis: TruthfulQA MC2 Score
   - Error bars: Standard deviation across 3 replicates

2. **Individual Replicate Improvements:** Scatter plot
   - X-axis: Replicate ID (1, 2, 3)
   - Y-axis: Δ(Target) score
   - Horizontal line: Δ=0 (no improvement threshold)

3. **Training Loss Curve:** Line plot
   - X-axis: Training steps
   - Y-axis: Loss
   - Shows convergence behavior across epochs

**Output Location:** All figures saved to `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR-1: Resource Constraints
**Priority:** P0 (Blocking)

- **GPU:** Single GPU (select empty GPU via `nvidia-smi`)
- **Memory:** ~8-12 GB VRAM (GPT-2 124M + LoRA adapters)
- **Environment Variable:** Set `CUDA_VISIBLE_DEVICES=<gpu_id>` before training
- **Storage:** ~2 GB for model checkpoints + datasets

### NFR-2: Reproducibility
**Priority:** P0 (Blocking)

- **Fixed Seeds:** [42, 43, 44] for deterministic behavior
- **Configuration Logging:** Save all hyperparameters to YAML
- **Checkpoint Saving:** Store model checkpoints at epoch boundaries
- **Results Tracking:** Log all metrics to structured files

### NFR-3: Code Quality
**Priority:** P1 (Important)

- **Libraries:** HuggingFace Transformers, PEFT, lm-evaluation-harness
- **Error Handling:** Graceful handling of OOM, dataset download failures
- **Documentation:** Inline comments for key implementation decisions
- **Modularity:** Separate data loading, training, evaluation components

---

## Dependencies

### External Dependencies
1. **h-e1 (Prerequisite):** COMPLETED, gate PASS
   - Provides: Proven GPT-2 + LoRA configuration
   - Location: `docs/youra_research/20260511_buildingtrust/h-e1/`
   - Key Files: 03_prd.md, 03_architecture.md, 04_validation.md

2. **Python Libraries:**
   - transformers (HuggingFace)
   - peft (LoRA implementation)
   - lm-evaluation-harness (TruthfulQA evaluation)
   - torch (PyTorch backend)
   - scipy (statistical tests)
   - matplotlib/seaborn (visualization)

3. **Datasets:**
   - TruthfulQA (via lm-eval harness)

4. **Models:**
   - GPT-2 (openai-community/gpt2)

### Internal Dependencies
- Phase 2C experiment brief (02c_experiment_brief.md)
- verification_state.yaml (gate tracking)

---

## Success Criteria

### Experiment Success (PoC Pass Condition)
1. **Code Execution:** Runs without error (all 3 replicates complete)
2. **Gate Validation:** Mean Δ(Target) > 0 with p<0.05

### Gate Conditions
- **Type:** MUST_WORK
- **Threshold:** Mean Δ(Target) > 0 with p<0.05
- **Fail Action:** PIVOT - explore alternative intervention approaches
- **Interpretation:** If interventions don't improve target dimension, entire cross-dimensional mechanism premise breaks (blocks h-m2, h-m3, h-m4)

### Deliverables
1. Working Python experiment code
2. 04_validation.md with results and gate evaluation
3. Visualization figures (3 plots minimum)
4. Updated verification_state.yaml with gate result

---

## Out of Scope

The following are explicitly OUT OF SCOPE for H-M1:

1. **Cross-Dimensional Analysis:** BBQ, AdvGLUE evaluation (covered in h-e1)
2. **Multiple Models:** Only GPT-2 (model diversity in h-e1)
3. **Large-Scale Replication:** 3 replicates (not 20) for PoC
4. **Ablation Studies:** Fixed LoRA configuration (no hyperparameter sweep)
5. **Representation Analysis:** Internal layer activations (deferred to h-m2)

---

## Timeline and Phases

**Implementation Phase:** Phase 4 (Coding & PoC Validation)
- Estimated Duration: 2 weeks (from Phase 2B roadmap)
- Parallel: Can run independently of other hypotheses (prerequisite h-e1 already complete)

**Validation Phase:** Phase 4 (gate evaluation)
- Statistical significance test
- Gate decision: PASS → proceed to h-m2 | FAIL → PIVOT

---

## Risk Assessment

### High Risk Items
1. **TruthfulQA Training Data:**
   - Issue: No official train split (validation-only benchmark)
   - Mitigation: Use GPT-2's general language modeling training (implicit TruthfulQA improvement)
   - Alternative: Fine-tune on related datasets (e.g., SQuAD for factual correctness)

2. **Small Sample Size:**
   - Issue: 3 replicates may have low statistical power
   - Mitigation: Use paired t-test (higher power than unpaired)
   - Fallback: If borderline significance, increase to N=5-10 replicates

### Medium Risk Items
1. **Baseline Performance Uncertainty:**
   - Issue: GPT-2 TruthfulQA baseline unknown (estimated from GPT-3)
   - Mitigation: Measure actual GPT-2 baseline in pre-intervention step
   
2. **Improvement Magnitude:**
   - Issue: Expected +5-10% improvement may be smaller for GPT-2
   - Mitigation: Focus on statistical significance (p<0.05) not absolute magnitude

---

## Appendix

### A. Comparison with h-e1

| Aspect | h-e1 (EXISTENCE) | h-m1 (MECHANISM) |
|--------|------------------|------------------|
| **Focus** | Cross-dimensional correlations | Target dimension improvement |
| **Datasets** | TruthfulQA + BBQ + AdvGLUE | TruthfulQA only |
| **Primary Metric** | Pearson ρ across dimension pairs | Δ(Target) improvement |
| **Statistical Test** | Fisher's z-transformation | Paired t-test |
| **Gate Threshold** | ≥80% configs with |ρ|>0, p<0.01 | Mean Δ>0, p<0.05 |
| **Replicates** | 3 (PoC) | 3 (PoC) |
| **Model** | GPT-2 (124M) | GPT-2 (124M) |
| **LoRA Config** | r=8, alpha=8 | r=8, alpha=16 |

### B. Phase 2C Completeness Checklist

**From 02c_experiment_brief.md:**
- ✅ Dataset: TruthfulQA specified (FR-1.1)
- ✅ Model: GPT-2 specified (FR-2.1)
- ✅ Training: LoRA config, hyperparameters specified (FR-3)
- ✅ Evaluation: Δ(Target) metric, t-test specified (FR-4)
- ✅ Visualization: 3 required figures specified (FR-6)
- ✅ Gate: MUST_WORK threshold specified (Success Criteria)
- ✅ Prerequisites: h-e1 validation confirmed (Dependencies)

**No missing items from Phase 2C.**

### C. Key Implementation References

**Source 1:** PEFT LoRA Documentation
- URL: https://huggingface.co/docs/peft/conceptual_guides/adapter
- Used for: LoRA configuration (FR-3.1)

**Source 2:** Lightning AI LoRA Insights
- URL: https://lightning.ai/pages/community/lora-insights
- Used for: Optimizer selection (AdamW + cosine), expected improvement (+5-10%)

**Source 3:** sylinrl/TruthfulQA
- URL: https://github.com/sylinrl/TruthfulQA
- Used for: Dataset specification, baseline performance

**Source 4:** Meta PyTorch torchtune
- URL: https://meta-pytorch.org/torchtune
- Used for: LoRA fine-tuning patterns, EleutherAI harness integration

---

*Generated by Phase 3 Step 2 - PRD Generation*  
*Next: Phase 3 Step 3 - Architecture Design*
