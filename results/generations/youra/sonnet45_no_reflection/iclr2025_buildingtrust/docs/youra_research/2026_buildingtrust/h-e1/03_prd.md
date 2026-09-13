# Product Requirements Document: H-E1 Cross-Dimensional Trustworthiness Effects

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Author:** Anonymous
**Hypothesis:** H-E1 (EXISTENCE)  
**Status:** Draft  

---

## Executive Summary

This PRD defines the requirements for implementing an experiment to validate the existence of cross-dimensional effects in language model trustworthiness. The experiment will fine-tune models on a single trustworthiness dimension and measure correlations across three dimensions (truthfulness, fairness, robustness) to test if interventions create measurable impacts beyond the target dimension.

**Success Criteria:** ≥80% of intervention configurations (12/15) show statistically significant cross-dimensional correlations (|ρ| > 0, p<0.01).

---

## Problem Statement

### Research Question
Do parameter updates targeting a single trustworthiness dimension create detectable effects across other trustworthiness dimensions?

### Current Gap
Existing trustworthiness frameworks (TrustLLM, MultiTrust) evaluate dimensions in isolation. No prior work characterizes how interventions targeting one dimension affect others.

### Hypothesis Statement
Under controlled intervention conditions (fine-tuning on single trustworthiness dimension), if we apply systematic perturbations (N=20 replications with varied hyperparameters/seeds), then we will observe statistically significant cross-dimensional effects (p<0.01) in at least 80% of intervention configurations (12/15 configurations across 3 dimensions × 5 models), because parameter updates reshape internal representations affecting multiple dimensions simultaneously.

---

## Functional Requirements

### FR-1: Dataset Management
**Priority:** P0 (Blocking)

#### FR-1.1: TruthfulQA Dataset
- **Source:** HuggingFace datasets (`truthful_qa`)
- **Variants:** Multiple-choice (MC1, MC2) and generation
- **Statistics:** 817 questions across 38 categories
- **Split:** Validation only (no train split)
- **Implementation:** 
  ```python
  from datasets import load_dataset
  dataset_mc = load_dataset("truthful_qa", "multiple_choice")
  dataset_gen = load_dataset("truthful_qa", "generation")
  ```

#### FR-1.2: BBQ Dataset (Bias Benchmark for QA)
- **Source:** HuggingFace datasets (`heegyu/bbq` or `HiTZ/bbq`)
- **Statistics:** 58,492 questions across 9 demographic categories
- **Categories:** Age, Disability_status, Gender_identity, Nationality, Physical_appearance, Race_ethnicity, Religion, SES, Sexual_orientation
- **Splits:** train (4-shot examples), test (main evaluation)
- **Implementation:**
  ```python
  from datasets import load_dataset
  dataset_bbq = load_dataset("heegyu/bbq")
  # Or load specific category
  dataset_age = load_dataset("HiTZ/bbq", "Age_disambig")
  ```

#### FR-1.3: AdvGLUE Dataset
- **Source:** HuggingFace datasets (`adv_glue` or `AI-Secure/adv_glue`)
- **Tasks:** SST-2, QQP, MNLI, QNLI, RTE with adversarial perturbations
- **Perturbation Types:** Word-level, sentence-level, human-crafted adversarial examples
- **Implementation:**
  ```python
  from datasets import load_dataset
  dataset_sst2 = load_dataset("adv_glue", "adv_sst2")
  dataset_mnli = load_dataset("adv_glue", "adv_mnli")
  ```

### FR-2: Model Management
**Priority:** P0 (Blocking)

#### FR-2.1: Baseline Model (PoC)
- **Model:** Llama-3-8B
- **Source:** HuggingFace Hub (`meta-llama/Meta-Llama-3-8B`)
- **Architecture:** Transformer-based causal LM
- **Parameters:** 8 billion
- **Context Length:** 8K tokens
- **Precision:** bfloat16
- **Implementation:**
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  import torch
  
  model_id = "meta-llama/Meta-Llama-3-8B"
  model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  ```

#### FR-2.2: Full Model Suite (Future Scaling)
- Llama-3-8B (`meta-llama/Meta-Llama-3-8B`)
- Mistral-7B (`mistralai/Mistral-7B-v0.1`)
- Qwen-1.8B (`Qwen/Qwen-1_8B`)
- Mamba-1.4B (`state-spaces/mamba-1.4b`)
- Falcon-40B (`tiiuae/falcon-40b`)

### FR-3: Fine-Tuning Intervention
**Priority:** P0 (Blocking)

#### FR-3.1: LoRA Configuration
- **Method:** Parameter-efficient fine-tuning using PEFT library
- **Rank:** [8, 16, 32] (varied across replicates)
- **Alpha:** Same as rank
- **Target Modules:** ["q_proj", "v_proj"]
- **Dropout:** 0.05
- **Task Type:** CAUSAL_LM
- **Implementation:**
  ```python
  from peft import LoraConfig, get_peft_model
  
  lora_config = LoraConfig(
      r=lora_rank,  # 8, 16, or 32
      lora_alpha=lora_rank,
      target_modules=["q_proj", "v_proj"],
      lora_dropout=0.05,
      bias="none",
      task_type="CAUSAL_LM"
  )
  model = get_peft_model(base_model, lora_config)
  ```

#### FR-3.2: Training Configuration
- **Optimizer:** AdamW (betas=(0.9, 0.999), weight_decay=0.01)
- **Learning Rate:** [1e-5, 5e-5, 1e-4] (varied across replicates)
- **Schedule:** Cosine with warmup (100 warmup steps)
- **Batch Size:** 4 (with gradient accumulation steps=4, effective batch=16)
- **Epochs:** [1, 3, 5] (varied across replicates)
- **Loss Function:** Cross-entropy (standard causal LM loss)
- **Seeds:** Fixed seed=1 for PoC (20 varied seeds for full experiment)

#### FR-3.3: Perturbation Strategy
- Generate 20 configurations by sampling from hyperparameter ranges
- Each replicate uses different (lr, epochs, lora_rank, seed) combination
- Enables correlation measurement across perturbations

### FR-4: Evaluation Metrics
**Priority:** P0 (Blocking)

#### FR-4.1: TruthfulQA Metrics
- **MC1:** Fraction of questions where best answer has highest log-probability
- **MC2:** Normalized total probability assigned to set of true answers
- **Source:** sylinrl/TruthfulQA evaluation protocol

#### FR-4.2: BBQ Metrics
- **Bias Score:** Difference between accuracy on stereotype-aligned vs. stereotype-conflicting examples
- **Disambiguation Accuracy:** Performance on fully informative contexts
- **Source:** BBQ paper (Parrish et al., 2022)

#### FR-4.3: AdvGLUE Metrics
- **Adversarial Accuracy:** Performance on adversarially perturbed examples
- **Per-task Metrics:** SST-2, QQP, MNLI accuracy
- **Source:** AdvGLUE benchmark documentation

#### FR-4.4: Cross-Dimensional Correlation Metric (Primary DV)
- **Metric:** Pearson correlation ρ(ΔDim₁, ΔDim₂) across 20 replicates
- **Statistical Test:** Fisher's z-transformation for p-value
- **Significance Threshold:** p < 0.01
- **Implementation:**
  ```python
  from scipy.stats import pearsonr
  rho, p_value = pearsonr(delta_dim1, delta_dim2)
  ```

### FR-5: Experiment Workflow
**Priority:** P0 (Blocking)

#### FR-5.1: Baseline Measurement
- Load base model (Llama-3-8B)
- Evaluate on TruthfulQA, BBQ, AdvGLUE
- Record baseline scores for all three dimensions

#### FR-5.2: Intervention Loop (N=3 for PoC, N=20 for full)
For each replicate:
1. Initialize model with LoRA adapter (sampled hyperparameters)
2. Fine-tune on target dimension dataset (e.g., TruthfulQA)
3. Evaluate on all three benchmarks
4. Calculate Δscores (post-intervention - baseline)
5. Store (Δtruthfulness, Δfairness, Δrobustness) tuple

#### FR-5.3: Correlation Analysis
- Extract delta scores for each dimension pair
- Compute Pearson correlation ρ for (Truth, Fair), (Truth, Robust), (Fair, Robust)
- Test significance with Fisher's z-transformation
- Count configurations with |ρ| > 0 and p < 0.01

### FR-6: Visualization
**Priority:** P1 (Important)

#### FR-6.1: Required Figures
- **Correlation Heatmap:** 3×3 matrix showing ρ values for all dimension pairs
- **Scatter Plots:** Δ(Dim₁) vs Δ(Dim₂) for each pair with regression line

#### FR-6.2: Additional Figures
- Delta distribution histograms for each dimension
- Intervention effect bar chart (mean Δscore per dimension)
- Significance map (binary heatmap for p<0.01 correlations)

All figures saved to `{hypothesis_folder}/figures/`

---

## Non-Functional Requirements

### NFR-1: Computational Resources
- **GPU:** Single GPU with ≥24GB VRAM (A100 recommended)
- **CUDA:** Set `CUDA_VISIBLE_DEVICES` to single empty GPU
- **Memory:** Gradient checkpointing enabled for memory efficiency

### NFR-2: Reproducibility
- Fixed random seeds for PoC validation
- All hyperparameters logged per replicate
- Model checkpoints saved after each intervention

### NFR-3: Execution Time
- PoC (3 replicates): ~2-4 hours
- Full experiment (20 replicates): ~12-24 hours

### NFR-4: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Unit tests for core functions (correlation computation, evaluation metrics)

---

## Data Specifications

### Input Data
| Dataset | Size | Format | Source |
|---------|------|--------|--------|
| TruthfulQA | 817 questions | JSON | HuggingFace datasets |
| BBQ | 58,492 questions | JSON | HuggingFace datasets |
| AdvGLUE | 5 GLUE tasks | JSON | HuggingFace datasets |

### Output Data
| File | Content | Format |
|------|---------|--------|
| `baseline_scores.json` | Pre-intervention scores | JSON |
| `intervention_results.json` | Per-replicate Δscores | JSON |
| `correlation_analysis.json` | ρ values, p-values | JSON |
| `figures/*.png` | Visualizations | PNG |

---

## Dependencies

### Python Packages
```
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0
datasets>=2.12.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### External Resources
- HuggingFace Hub access (model downloads)
- HuggingFace datasets library (benchmark access)

---

## Success Criteria

### PoC Success (H-E1)
1. Code runs without error
2. Cross-dimensional correlation detection: |ρ| > 0 with measurable effect
3. Intervention effectiveness: Target dimension improves (Δ(Target) > 0)

### Full Hypothesis Success
1. ≥80% configurations (12/15) show |ρ| > 0 with p<0.01 for at least one dimension pair
2. Effect sizes |ρ| > 0.3 (medium correlations)
3. Consistent directionality across models

---

## Out of Scope

- Multi-model evaluation (deferred to full experiment after PoC)
- Mechanistic interpretation of correlations (H-M1, H-M2, H-M3)
- Production deployment or real-time inference
- Full fine-tuning (using LoRA only for efficiency)

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GPU memory overflow | Medium | High | Use gradient checkpointing, single GPU |
| Weak correlations (|ρ| < 0.3) | Medium | High | Increase replicate count, adjust perturbation ranges |
| Evaluation benchmark errors | Low | Medium | Use official evaluation scripts, validate against baselines |
| Long execution time | Medium | Low | Start with PoC (N=3), optimize before full run |

---

## References

### Implementation Sources
1. **TrustLLM Framework:** HowieHwong/TrustLLM (ICML 2024)
2. **TruthfulQA Official:** sylinrl/TruthfulQA
3. **LM Evaluation Harness:** EleutherAI/lm-evaluation-harness
4. **HuggingFace PEFT:** LoRA documentation and examples

### Research Grounding
- TrustLLM paper: Multi-dimensional trustworthiness evaluation (6 dimensions)
- MultiTrust (NeurIPS 2024): No significant correlation across dimensions found
- Understanding LLM Benchmarks: Correlation analysis methodology

---

## Appendix: Expected Baseline Performance

Based on TrustLLM (ICML 2024) and MultiTrust (NeurIPS 2024):
- **TruthfulQA MC2:** 0.30-0.45 for base Llama-3-8B
- **BBQ Bias Score:** 40-60% for base models
- **AdvGLUE:** 60-80% of original GLUE accuracy

---

*This PRD is derived from Phase 2C Experiment Brief (02c_experiment_brief.md) and follows EXISTENCE hypothesis requirements for proof-of-concept validation.*
