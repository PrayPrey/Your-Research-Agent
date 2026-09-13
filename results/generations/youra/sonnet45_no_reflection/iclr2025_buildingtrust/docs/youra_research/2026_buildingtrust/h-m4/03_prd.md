# Product Requirements Document: H-M4 Cross-Architecture Directional Replication

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Author:** Anonymous
**Hypothesis:** H-M4 (MECHANISM)  
**Status:** Draft  

---

## Executive Summary

This PRD defines the requirements for implementing an experiment to validate that correlation direction patterns from targeted interventions replicate consistently across ≥3/5 diverse model families (4 transformer variants + 1 SSM). This experiment validates architectural generalization: if fundamental optimization dynamics are architecture-agnostic, directional replication should occur.

**Success Criteria:** Directional replication ≥3/5 models (60%) for significant intervention × dimension pairs.

**Continuation Context:** This experiment builds directly on h-m3 (COMPLETED, gate PASS with limitation). H-M3 found strong truthfulness-robustness trade-off (r=-0.997, p=0.051) but only tested on GPT-2 (single architecture). H-M4 validates whether this correlation direction generalizes across transformer families and non-transformer architectures (SSM).

---

## Problem Statement

### Research Question
Does the correlation direction (positive/negative) observed in h-m3 replicate consistently across diverse model families (transformers + SSM)?

### Current Gap
H-M3 validated cross-dimensional correlations exist but only tested GPT-2 (124M, single transformer family). Unknown whether correlation patterns are architecture-specific or driven by fundamental optimization dynamics shared across architectures.

### Hypothesis Statement
Under directional correlation patterns from targeted interventions, if fundamental optimization dynamics (gradient descent, backpropagation) are architecture-agnostic, then correlation direction (positive/negative) will replicate consistently across ≥3/5 model families, because core learning mechanisms are shared across transformer, SSM, and other architectures.

---

## Functional Requirements

### FR-1: Dataset Management (Multi-Dimensional Suite - Inherited from H-M3)
**Priority:** P0 (Blocking)

#### FR-1.1: TruthfulQA Dataset (Truthfulness Dimension)
- **Source:** HuggingFace datasets (`truthfulqa/truthful_qa`)
- **Split:** `multiple_choice` (817 questions)
- **Task:** Multiple-choice question answering (truthfulness evaluation)
- **Statistics:** 817 samples
- **Purpose:** Target dimension for LoRA intervention
- **Training Subset:** 500 samples (reusing h-m3 optimal configuration)
- **Evaluation Set:** Full 817 questions
- **Implementation:**
  ```python
  from datasets import load_dataset
  truthfulqa = load_dataset("truthful_qa", "multiple_choice")
  ```

**Rationale:** Same dataset as h-m3 for controlled comparison. Intervention target dimension.

#### FR-1.2: BBQ Dataset (Fairness Dimension)
- **Source:** HuggingFace datasets (`lighteval/bbq_helm`)
- **Split:** all categories, zero-shot evaluation
- **Task:** Bias detection in question answering
- **Statistics:** 1000+ samples across 9 social dimensions
- **Purpose:** Non-target dimension D₂ (fairness/bias)
- **Evaluation Set:** Full test split
- **Implementation:**
  ```python
  from datasets import load_dataset
  bbq = load_dataset("lighteval/bbq_helm", "all", split="test")
  # Can also use lm_eval.tasks.bbq for standardized evaluation
  ```

**Rationale:** Standard fairness benchmark for measuring cross-dimensional effects.

#### FR-1.3: ANLI Round 3 Dataset (Robustness Dimension)
- **Source:** HuggingFace datasets (`facebook/anli`)
- **Split:** `test_r3` (1200 samples)
- **Task:** Natural language inference under adversarial conditions
- **Statistics:** 1200 samples (Round 3 - hardest adversarial examples)
- **Purpose:** Non-target dimension D₃ (adversarial robustness)
- **Evaluation Set:** Full test_r3 split
- **Implementation:**
  ```python
  from datasets import load_dataset
  anli_r3 = load_dataset("anli", split="test_r3")
  ```

**Rationale:** Replaced AdvGLUE with ANLI R3 (better HuggingFace support). Standard adversarial robustness benchmark.

**Sample Size Policy** (addressing experiment scale guidance):
- **TruthfulQA**: Full validation set (817 questions)
- **BBQ**: Full test split (1000+ samples)
- **ANLI R3**: Full test split (1200 samples)
- **No trivial subsets**: All evaluations use standard benchmark splits

### FR-2: Multi-Model Family Management (5 Architectures)
**Priority:** P0 (Blocking)

**NEW REQUIREMENT:** This experiment requires 5 diverse model families (4 transformer variants + 1 SSM) to test cross-architecture generalization.

#### FR-2.1: Model Family 1 - LLaMA 3.2
- **Model:** LLaMA-3.2-1B (1B parameters)
- **Source:** HuggingFace Hub (`meta-llama/Llama-3.2-1B`)
- **Architecture:** Transformer-based decoder (Meta AI)
- **Rationale:** Mainstream transformer architecture, proven performance
- **Implementation:**
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B", device_map="auto")
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
  ```

#### FR-2.2: Model Family 2 - Mistral
- **Model:** Mistral-7B-v0.1 (7B parameters)
- **Source:** HuggingFace Hub (`mistralai/Mistral-7B-v0.1`)
- **Architecture:** Transformer with Grouped Query Attention (GQA) + Sliding Window Attention
- **Rationale:** Optimized transformer variant with architectural innovations
- **Implementation:**
  ```python
  model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", device_map="auto", torch_dtype="auto")
  tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
  ```

#### FR-2.3: Model Family 3 - Qwen
- **Model:** Qwen-1.8B (1.8B parameters)
- **Source:** HuggingFace Hub (`Qwen/Qwen-1.8B`)
- **Architecture:** Transformer-based (Alibaba Cloud)
- **Rationale:** Non-Western architecture family for diversity
- **Implementation:**
  ```python
  model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-1.8B", device_map="auto", trust_remote_code=True)
  tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-1.8B", trust_remote_code=True)
  ```

#### FR-2.4: Model Family 4 - Mamba (SSM - Non-Transformer)
- **Model:** Mamba-1.4B (1.4B parameters)
- **Source:** HuggingFace Hub (`state-spaces/mamba-1.4b`)
- **Architecture:** Structured State Space Model (SSM) - **Non-transformer**
- **Rationale:** Tests generalization to non-transformer architectures (SSM vs. attention mechanism)
- **Implementation:**
  ```python
  # Mamba requires special loading (not standard AutoModel)
  from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
  model = MambaLMHeadModel.from_pretrained("state-spaces/mamba-1.4b", device="cuda")
  ```

**Note:** Mamba requires `mamba-ssm` package installation and has different API from standard transformers.

#### FR-2.5: Model Family 5 - Falcon
- **Model:** Falcon-7B (7B parameters)
- **Source:** HuggingFace Hub (`tiiuae/falcon-7b`)
- **Architecture:** Transformer-based decoder (TII UAE)
- **Rationale:** Open-source transformer trained on diverse multilingual data
- **Implementation:**
  ```python
  model = AutoModelForCausalLM.from_pretrained("tiiuae/falcon-7b", device_map="auto", trust_remote_code=True)
  tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b", trust_remote_code=True)
  ```

**Model Size Range:** 1B-7B parameters (computationally feasible for 5-family comparison)
**Architecture Diversity:** 4 transformer variants (LLaMA, Mistral, Qwen, Falcon) + 1 SSM (Mamba)

### FR-3: LoRA Intervention (Inherited from H-M3 Optimal Configuration)
**Priority:** P0 (Blocking)

**Configuration (from h-m3 optimal):**
- **Method:** LoRA (Low-Rank Adaptation)
- **Rank (r):** 8
- **Alpha (α):** 16
- **Target Modules:** All attention layers (for transformers); equivalent layers for Mamba
- **Trainable Parameters:** ~0.5-2M (depending on model size)

**Training Configuration:**
- **Samples:** 500 (from TruthfulQA)
- **Epochs:** 3
- **Batch Size:** 8 (gradient accumulation for 7B models if needed)
- **Optimizer:** AdamW (lr=2e-4, weight_decay=0.01)
- **Seeds:** 5 per model family (increased from h-m3's 3 for statistical power)

**Total Runs:** 5 families × 5 seeds = 25 intervention experiments

**Implementation:**
```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Adjust per model
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(base_model, lora_config)
```

**Rationale:** Reusing h-m3 optimal configuration ensures controlled comparison. LoRA is architecture-agnostic and works across all 5 model families.

### FR-4: Cross-Dimensional Evaluation Pipeline
**Priority:** P0 (Blocking)

**Evaluation Protocol (per model family, per seed):**

1. **Baseline Evaluation (Pre-Intervention):**
   - TruthfulQA MC1 accuracy
   - BBQ accuracy (ambiguous + disambiguated)
   - ANLI R3 accuracy

2. **LoRA Intervention:** Fine-tune on 500 TruthfulQA samples (3 epochs)

3. **Post-Intervention Evaluation:**
   - Re-evaluate on all 3 benchmarks
   - Compute performance deltas: Δ = post - baseline

4. **Correlation Analysis (per model family):**
   - Compute Pearson correlation between dimension pairs across 5 seeds
   - Classify direction: ρ > 0.3 (positive), ρ < -0.3 (negative), else neutral

**Implementation:**
```python
from scipy.stats import pearsonr

# For each model family
baseline_scores = evaluate_all_dimensions(model)
intervention_results = []

for seed in range(5):
    model_finetuned = apply_lora_intervention(model, target_dim="truthfulness", seed=seed)
    post_scores = evaluate_all_dimensions(model_finetuned)
    deltas = {dim: post_scores[dim] - baseline_scores[dim] for dim in dimensions}
    intervention_results.append(deltas)

# Compute correlations
correlations = compute_pairwise_correlations(intervention_results)
direction = classify_direction(correlations)  # positive/negative/neutral
```

### FR-5: Directional Replication Analysis
**Priority:** P0 (Blocking)

**Gate Criterion:** ≥3/5 model families show same correlation direction for at least one dimension pair.

**Analysis Steps:**

1. **Per-Model Direction Classification:**
   - For each dimension pair (truth-fair, truth-robust, fair-robust)
   - Classify direction per model family based on Pearson ρ

2. **Majority Direction:**
   - For each dimension pair, find most common direction across 5 families

3. **Replication Rate:**
   - Count families matching majority direction
   - Compute: replication_rate = matching_count / 5

4. **Gate Validation:**
   - Check if replication_rate ≥ 0.6 (3/5 threshold)

**Implementation:**
```python
def compute_directional_replication(all_model_results):
    """
    Args:
        all_model_results: {model_family: {dim_pair: direction}}
    
    Returns:
        replication_metrics: {dim_pair: replication_rate}
    """
    replication_metrics = {}
    
    for dim_pair in ["truth-fair", "truth-robust", "fair-robust"]:
        directions = [results[dim_pair] for results in all_model_results.values()]
        majority = max(set(directions), key=directions.count)
        replication_count = directions.count(majority)
        replication_rate = replication_count / len(directions)
        
        replication_metrics[dim_pair] = {
            "majority_direction": majority,
            "replication_rate": replication_rate,
            "gate_pass": replication_rate >= 0.6
        }
    
    return replication_metrics
```

---

## Non-Functional Requirements

### NFR-1: Computational Resources
**Priority:** P0 (Blocking)

**GPU Requirements:**
- Single GPU for 1B models (LLaMA-3.2-1B, Qwen-1.8B, Mamba-1.4B)
- Single GPU (24GB+ VRAM) for 7B models (Mistral-7B, Falcon-7B) with bf16/fp16

**Disk Space:**
- Model checkpoints: ~30GB (5 models × ~6GB each)
- Dataset cache: ~2GB
- Results storage: ~500MB

**Compute Time Estimate (per model family):**
- Baseline eval: 10-30 minutes
- LoRA training × 5 seeds: 2-4 hours
- Post-intervention eval × 5: 50-150 minutes
- **Total per family:** 4-6 hours
- **Total experiment:** 20-30 hours (5 families)

### NFR-2: Reproducibility
**Priority:** P1 (Important)

- Set random seeds for all 5 replications per model
- Log all hyperparameters and model versions
- Save intermediate checkpoints
- Version datasets with HuggingFace cache

### NFR-3: Statistical Rigor
**Priority:** P0 (Blocking)

- **Seeds:** 5 per model family (vs h-m3's 3) for p<0.05 significance
- **Correlation test:** Pearson with p-value reporting
- **Fisher's exact test:** For directional consistency validation
- **ANOVA:** Test intervention type main effect

---

## Success Criteria

### Primary Success Criteria (SHOULD_WORK Gate)
✅ **Gate Pass:** ≥3/5 model families (60%) show same correlation direction for at least one dimension pair

**Measurement:**
- Extract correlation directions per model family
- Compute replication rate per dimension pair
- Pass if any dimension pair achieves ≥60% replication

### Secondary Success Criteria
1. **Statistical Significance:** Pearson correlation p < 0.05 within each replicating model family
2. **ANOVA:** Intervention type shows main effect on correlation patterns (F-test, p<0.05)
3. **Architecture Comparison:** Analyze transformer vs. SSM (Mamba) replication separately

### Expected Baseline Performance (from research)
- **TruthfulQA MC1:** 25-35% (h-m3 GPT-2: 29.4%)
- **BBQ Accuracy:** 30-40% (Llama-3.2-1B: 31.15%)
- **ANLI R3 Accuracy:** 30-40% (h-m3 GPT-2: 34.6%)

---

## Dependencies & Constraints

### External Dependencies
- **HuggingFace Transformers:** Model loading and tokenization
- **HuggingFace Datasets:** Dataset management
- **PEFT (Parameter-Efficient Fine-Tuning):** LoRA implementation
- **mamba-ssm:** Required for Mamba model loading
- **lm-evaluation-harness:** Optional for standardized BBQ evaluation
- **PyTorch:** Deep learning framework
- **scipy:** Statistical analysis (Pearson correlation)

### Prerequisites
- H-M3 completed (gate PASS with limitation) ✅
- GPU access (24GB VRAM recommended for 7B models)
- ~30GB disk space for model checkpoints

### Constraints
- **Model Size:** Limited to 1B-7B range (computational feasibility)
- **Families:** 5 specific families chosen (LLaMA, Mistral, Qwen, Mamba, Falcon)
- **Seeds:** Fixed at 5 per family (25 total runs)
- **Intervention:** LoRA only (no full fine-tuning due to compute constraints)

---

## Out of Scope

- Testing model sizes >7B (compute constraints)
- Testing >5 model families (scope constraint)
- Full fine-tuning (only LoRA)
- Additional trustworthiness dimensions beyond truth/fairness/robustness
- Cross-lingual evaluation (English only)

---

## Risks & Mitigations

### Risk 1: Mamba-Specific Integration Issues
- **Impact:** High - SSM architecture has different API
- **Mitigation:** Use Mamba-specific evaluation wrapper, test separately first
- **Fallback:** Replace with another transformer family if integration fails

### Risk 2: Replication Threshold Sensitivity (3/5 may be too strict/lax)
- **Impact:** Medium - Gate validation ambiguity
- **Mitigation:** Report full distribution (0/5 to 5/5), sensitivity analysis with 2/5 and 4/5 thresholds
- **Documentation:** Transparent reporting regardless of gate result

### Risk 3: Compute Time Overrun (30+ hours)
- **Impact:** Medium - Timeline delay
- **Mitigation:** Parallel execution where possible, prioritize smaller models first
- **Fallback:** Reduce seeds from 5 to 3 if time-critical (accept lower statistical power)

### Risk 4: No Replication Observed (<3/5 families)
- **Impact:** Low - Valid scientific finding
- **Action:** Document architecture-specific effects, analyze patterns (transformer vs SSM)
- **Gate:** SHOULD_WORK allows continuation with limitation documented

---

## Validation Plan

### Unit Testing
- [ ] Dataset loaders work for all 3 benchmarks
- [ ] Model loaders work for all 5 families
- [ ] LoRA application successful across all families
- [ ] Evaluation pipeline produces valid metrics

### Integration Testing
- [ ] End-to-end run for 1 model family (1 seed)
- [ ] Correlation computation produces valid ρ values
- [ ] Direction classification logic correct

### Acceptance Testing
- [ ] All 5 families × 5 seeds = 25 runs complete
- [ ] Replication rate computed per dimension pair
- [ ] Gate criterion checked (≥3/5 threshold)
- [ ] Results saved and reproducible

---

## Appendix

### A. Model Selection Rationale

**LLaMA 3.2:** Industry standard, well-documented  
**Mistral:** Architectural innovations (GQA, sliding window)  
**Qwen:** Non-Western training data diversity  
**Mamba:** Non-transformer architecture (SSM)  
**Falcon:** Open multilingual training corpus  

**Size Justification:** 1B-7B range balances computational feasibility with meaningful model capacity.

### B. Reference Implementations

**TrustLLM** (ICML 2024): Multi-model trustworthiness benchmarking framework  
**TrustEval-toolkit** (ICLR'26): Multi-GPU evaluation for LLM trustworthiness  
**DecodingTrust**: Comprehensive GPT + open LLM evaluation codebase  
**fairness-pruning**: Cross-architecture BBQ evaluation (LLaMA + Salamandra)  

### C. H-M3 Context (Prerequisite)

**Key Finding:** Strong truthfulness-robustness trade-off (r=-0.997, p=0.051)  
**Limitation:** Single architecture (GPT-2 124M) tested  
**Lessons Learned:** Need 5+ seeds for statistical power, LoRA r=8/α=16 optimal  
**H-M4 Goal:** Test if h-m3's correlation direction replicates across architectures  

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Architecture Design (Step 3)
