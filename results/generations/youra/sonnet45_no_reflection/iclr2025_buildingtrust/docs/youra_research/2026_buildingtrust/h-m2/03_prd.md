# Product Requirements Document: H-M2 Representation Change Validation

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Author:** Anonymous
**Hypothesis:** H-M2 (MECHANISM)  
**Status:** Draft  

---

## Executive Summary

This PRD defines the requirements for implementing an experiment to validate that parameter updates from targeted interventions cause measurable internal representation changes (attention patterns, hidden states) in neural network layers. This experiment validates the second step of the causal chain: parameter updates must change representations for cross-dimensional effects to propagate.

**Success Criteria:** Significant correlation (p<0.05) between representation change magnitude and performance improvement.

**Continuation Context:** This experiment builds directly on h-m1 (COMPLETED, gate PASS), reusing the proven GPT-2 + LoRA configuration. H-M1 validated that interventions improve target dimension (+2.32% on TruthfulQA). H-M2 validates that these improvements occur through representation changes.

---

## Problem Statement

### Research Question
Do parameter updates from fine-tuning on a target dimension (TruthfulQA) cause measurable changes in internal representations (attention patterns, hidden states)?

### Current Gap
H-M1 validated that interventions improve target dimension performance, but did not validate the mechanism: whether improvements occur through representation changes or alternative mechanisms. This is prerequisite for understanding cross-dimensional propagation (H-M3).

### Hypothesis Statement
Under parameter updates from dimension-targeted interventions, if neural network layers are shared across tasks, then internal representations (attention patterns, hidden states, layer activations) change in ways that affect multiple capabilities simultaneously, because weight changes necessarily impact all downstream computations.

---

## Functional Requirements

### FR-1: Dataset Management
**Priority:** P0 (Blocking)

#### FR-1.1: TruthfulQA Dataset (Target Dimension - Inherited from H-M1)
- **Source:** HuggingFace datasets via EleutherAI lm-evaluation-harness
- **Task:** Multiple-choice question answering (truthfulness evaluation)
- **Statistics:** 817 questions, MC2 (multi-true) format
- **Evaluation Set:** Full 817 questions for representation extraction
- **Training Subset:** 100 samples (same as h-m1)
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

**Rationale:** Same dataset as h-m1 for controlled comparison. Representation changes are measured on the same distribution as performance changes.

**Note:** H-M2 uses ONLY TruthfulQA (same as h-m1). No cross-dimensional datasets needed for this mechanism validation.

### FR-2: Model Management
**Priority:** P0 (Blocking)

#### FR-2.1: Baseline Model (Inherited from H-M1)
- **Model:** GPT-2 (124M parameters)
- **Source:** HuggingFace Hub (`openai-community/gpt2`)
- **Architecture:** Transformer-based causal LM
  - Layers: 12
  - Hidden size: 768
  - Attention heads: 12
  - Context length: 1024 tokens
- **Precision:** FP32 (same as h-m1)
- **Loading Method:** TransformerLens HookedTransformer (for activation extraction)
- **Implementation:**
  ```python
  from transformer_lens import HookedTransformer
  
  # Load GPT-2 with TransformerLens for activation extraction
  model = HookedTransformer.from_pretrained("gpt2", device="cuda")
  
  # TransformerLens provides hook points for all layers:
  # - blocks.{i}.hook_resid_pre: residual stream input
  # - blocks.{i}.attn.hook_pattern: attention patterns  
  # - blocks.{i}.hook_resid_post: residual stream output
  ```

**Rationale:** H-M1 used GPT-2 successfully. H-M2 reuses the same model with TransformerLens wrapper for activation extraction capability.

**Difference from H-M1:** H-M1 used standard HuggingFace transformers. H-M2 uses TransformerLens wrapper to enable activation caching without manual hook registration.

### FR-3: Fine-Tuning Intervention (Inherited from H-M1)
**Priority:** P0 (Blocking)

#### FR-3.1: LoRA Configuration (Proven in H-M1)
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

**Source:** H-M1 validation results (gate PASS with these exact parameters)

#### FR-3.2: Training Protocol (Inherited from H-M1)
- **Optimizer:** AdamW (default betas=(0.9, 0.999), eps=1e-8)
- **Learning Rate:** 1e-4
- **Scheduler:** Cosine annealing with warmup (10% of total steps)
- **Batch Size:** 4 per device
- **Gradient Accumulation:** 2 steps (effective batch=8)
- **Epochs:** 3
- **Training Samples:** 100 per replicate
- **Loss Function:** Causal language modeling (next-token prediction)
- **Precision:** FP32
- **Random Seeds:** [42, 43, 44] (3 replicates, same as h-m1)

**Source:** H-M1 validation results (proven sufficient for measurable improvement)

**Rationale:** Exact replication of h-m1 intervention ensures representation changes are measured under identical conditions to performance changes.

### FR-4: Representation Extraction
**Priority:** P0 (Blocking)

#### FR-4.1: Pre-Intervention Activation Extraction
- **Timing:** Before LoRA fine-tuning
- **Method:** TransformerLens `run_with_cache()`
- **Layers to Extract:**
  - **Attention Patterns:** `blocks.{i}.attn.hook_pattern` (12 layers, i=0..11)
    - Shape: (batch, n_heads, seq_len, seq_len)
    - Measures: Attention distribution changes
  - **Hidden States:** `blocks.{i}.hook_resid_post` (12 layers, i=0..11)
    - Shape: (batch, seq_len, d_model)
    - Measures: Residual stream representation changes
- **Total Layers Analyzed:** 24 (12 attention + 12 hidden state)
- **Storage:** Save activations to disk (per replicate)
- **Implementation:**
  ```python
  from transformer_lens import HookedTransformer
  import torch
  
  model = HookedTransformer.from_pretrained("gpt2")
  
  # Extract all activations
  _, cache = model.run_with_cache(eval_tokens)
  
  # Store pre-intervention activations
  pre_activations = {
      f"blocks.{i}.attn.hook_pattern": cache[f"blocks.{i}.attn.hook_pattern"].detach().cpu()
      for i in range(12)
  }
  pre_activations.update({
      f"blocks.{i}.hook_resid_post": cache[f"blocks.{i}.hook_resid_post"].detach().cpu()
      for i in range(12)
  })
  
  torch.save(pre_activations, f"pre_activations_seed{seed}.pt")
  ```

**Rationale:** Baseline representations must be captured before intervention to measure change magnitude.

#### FR-4.2: Post-Intervention Activation Extraction
- **Timing:** After LoRA fine-tuning (3 epochs)
- **Method:** TransformerLens `run_with_cache()` on fine-tuned model
- **Layers:** Same 24 layers as pre-intervention
- **Input Data:** Exact same evaluation tokens as pre-intervention
- **Storage:** Save activations to disk (per replicate)
- **Implementation:**
  ```python
  # After fine-tuning, reload model with LoRA weights
  model_finetuned = HookedTransformer.from_pretrained(
      "gpt2", 
      state_dict=lora_model.state_dict()
  )
  
  # Extract post-intervention activations
  _, cache = model_finetuned.run_with_cache(eval_tokens)
  
  post_activations = {
      f"blocks.{i}.attn.hook_pattern": cache[f"blocks.{i}.attn.hook_pattern"].detach().cpu()
      for i in range(12)
  }
  post_activations.update({
      f"blocks.{i}.hook_resid_post": cache[f"blocks.{i}.hook_resid_post"].detach().cpu()
      for i in range(12)
  })
  
  torch.save(post_activations, f"post_activations_seed{seed}.pt")
  ```

**Rationale:** Post-intervention representations measured on identical inputs enable direct comparison via CKA.

### FR-5: Representation Similarity Analysis
**Priority:** P0 (Blocking)

#### FR-5.1: CKA Similarity Computation
- **Method:** Centered Kernel Alignment (CKA)
- **Library:** pytorch-cka (GPU-accelerated, 44x faster than baseline)
- **Installation:** `pip install pytorch-cka`
- **Formula:** CKA(K, L) = HSIC(K, L) / sqrt(HSIC(K, K) * HSIC(L, L))
- **Range:** [0, 1] where 1.0 = identical, 0.0 = completely different
- **Computation:** Layer-wise CKA between pre and post activations
- **Implementation:**
  ```python
  from cka import cka_score
  import torch
  
  # Load saved activations
  pre_acts = torch.load(f"pre_activations_seed{seed}.pt")
  post_acts = torch.load(f"post_activations_seed{seed}.pt")
  
  cka_scores = {}
  for layer_name in layers_to_analyze:
      # Flatten activations for CKA computation
      pre = pre_acts[layer_name].flatten(1)  # (batch, features)
      post = post_acts[layer_name].flatten(1)
      
      # Compute CKA similarity
      cka = cka_score(pre, post)
      cka_scores[layer_name] = cka.item()
  
  # Save results
  with open(f"cka_scores_seed{seed}.json", "w") as f:
      json.dump(cka_scores, f)
  ```

**Reference:** Kornblith et al. (2019), "Similarity of Neural Network Representations Revisited"

**Rationale:** CKA is invariant to orthogonal transformations and isotropic scaling, making it robust for comparing representations across training stages.

#### FR-5.2: Representation Change Magnitude
- **Metric:** (1 - CKA) per layer
- **Interpretation:** 0.0 = no change, 1.0 = complete change
- **Aggregation:** Per-layer change magnitude across 3 replicates
- **Expected Pattern:** 
  - Higher changes in adapted layers (c_attn modules)
  - Smaller changes in non-adapted layers (downstream propagation)
- **Storage:** CSV file with columns: layer_name, seed, cka_score, change_magnitude

### FR-6: Statistical Correlation Analysis
**Priority:** P0 (Blocking)

#### FR-6.1: Correlation Test
- **Method:** Pearson correlation coefficient
- **Library:** scipy.stats
- **Variables:**
  - X: Representation change magnitude (1 - CKA) per layer
  - Y: Performance improvement from h-m1 (+2.32% TruthfulQA MC2)
- **Null Hypothesis:** No correlation (ρ = 0)
- **Alternative:** Significant correlation exists (ρ ≠ 0)
- **Significance Level:** p < 0.05 (two-tailed)
- **Implementation:**
  ```python
  from scipy.stats import pearsonr
  import numpy as np
  
  # Aggregate across replicates
  rep_changes = [1.0 - cka for cka in cka_scores.values()]
  perf_change = 0.0232  # From h-m1 validation
  
  # Compute correlation
  correlation, p_value = pearsonr(
      rep_changes, 
      [perf_change] * len(rep_changes)
  )
  
  print(f"Correlation: {correlation:.3f}, p-value: {p_value:.3e}")
  ```

**Gate Criteria:**
- **PASS:** p < 0.05 (significant correlation found)
- **FAIL:** p >= 0.05 (document as limitation)

**Note:** Gate type is SHOULD_WORK, so failure does not stop workflow, but documents limitation.

### FR-7: Visualization Generation
**Priority:** P1 (Important)

#### FR-7.1: Required Figure (Gate Metrics)
- **Figure:** Correlation scatter plot
  - X-axis: Layer representation change magnitude
  - Y-axis: Performance improvement (constant across layers for this experiment)
  - Regression line with correlation coefficient and p-value
  - Save to: `{hypothesis_folder}/figures/correlation_scatter.png`

#### FR-7.2: Additional Figures (Autonomous)
1. **CKA Heatmap:**
   - X-axis: Layer index (0-11)
   - Y-axis: Representation type (attention, hidden state)
   - Color: CKA similarity (1.0 = no change, 0.0 = complete change)
   - Save to: `{hypothesis_folder}/figures/cka_heatmap.png`

2. **Representation Change Magnitude Bar Chart:**
   - X-axis: Layer index (0-11)
   - Y-axis: Change magnitude (1 - CKA)
   - Separate bars for attention vs. hidden state
   - Highlight LoRA-adapted layers
   - Save to: `{hypothesis_folder}/figures/change_magnitude.png`

3. **Layer-wise Change Progression:**
   - X-axis: Layer depth (0-11)
   - Y-axis: Representation change magnitude
   - Two lines: attention patterns, hidden states
   - Save to: `{hypothesis_folder}/figures/layer_progression.png`

**Implementation Note:** All figures must be generated programmatically in experiment code.

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** P0 (Blocking)

- **Random Seeds:** [42, 43, 44] (3 replicates, same as h-m1)
- **Deterministic Operations:** Set `torch.manual_seed()`, `np.random.seed()`
- **Version Pinning:** 
  - transformers==4.x (same as h-m1)
  - peft==0.x (same as h-m1)
  - transformer_lens==1.x (new for h-m2)
  - pytorch-cka==0.x (new for h-m2)
- **Environment File:** `requirements.txt` with exact versions

### NFR-2: Computational Resources
**Priority:** P0 (Blocking)

- **GPU:** Single CUDA device (same as h-m1)
- **Memory:** ~8GB VRAM (GPT-2 124M + LoRA + activations)
- **Storage:** ~5GB per replicate (activation caches)
- **Runtime:** ~10-15 minutes per replicate (same as h-m1 + activation extraction)

**GPU Selection:**
```bash
# Check available GPUs
nvidia-smi

# Use single empty GPU
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>
```

### NFR-3: Code Quality
**Priority:** P1 (Important)

- **Modularity:** Separate classes for activation extraction, CKA computation, correlation analysis
- **Logging:** Structured logging with timestamps (print statements acceptable for LIGHT tier)
- **Error Handling:** Try-except blocks for file I/O and GPU operations
- **Documentation:** Docstrings for main classes and functions

### NFR-4: Output Organization
**Priority:** P0 (Blocking)

**File Structure:**
```
h-m2/
├── code/
│   ├── representation_analyzer.py  # Main experiment code
│   ├── requirements.txt            # Dependencies
│   └── run_experiment.sh           # Execution script
├── outputs/
│   ├── pre_activations_seed42.pt   # Pre-intervention activations
│   ├── post_activations_seed42.pt  # Post-intervention activations
│   ├── cka_scores_seed42.json      # CKA similarity scores
│   ├── correlation_results.json    # Correlation analysis results
│   └── logs/                       # Training logs
├── figures/
│   ├── correlation_scatter.png     # Required gate figure
│   ├── cka_heatmap.png            # CKA similarity heatmap
│   ├── change_magnitude.png        # Layer-wise change magnitude
│   └── layer_progression.png       # Change progression across depth
└── 04_validation.md                # Validation report
```

---

## Success Criteria

### Gate Validation (SHOULD_WORK)
**Primary Criterion:** Significant correlation (p<0.05) between representation change magnitude and performance improvement

**Secondary Criterion:** Representation changes detectable in >50% of layers (CKA < 1.0)

### PoC Validation
**Minimum Criteria:**
1. Code runs without error
2. Representation changes detectable (CKA Δ > 0 in any layer)

### Full Validation
**All Criteria:**
1. ✅ Pre-intervention activations extracted for 24 layers
2. ✅ LoRA fine-tuning completed (3 replicates)
3. ✅ Post-intervention activations extracted for 24 layers
4. ✅ CKA similarity computed for all 24 layers
5. ✅ Correlation analysis completed (p-value calculated)
6. ✅ Required figure generated (correlation scatter)
7. ✅ Gate criterion met OR documented as limitation

---

## Dependencies

### Technical Dependencies
- **From H-M1:**
  - GPT-2 model configuration
  - LoRA hyperparameters
  - TruthfulQA dataset
  - Training protocol
  - Random seeds

### Prerequisite Hypotheses
- **H-M1 (MUST_WORK):** COMPLETED, gate PASS
  - Performance improvement validated: +2.32% TruthfulQA MC2
  - Optimal configuration inherited by h-m2

### External Libraries
- **New for H-M2:**
  - transformer_lens (activation extraction)
  - pytorch-cka (CKA computation)
- **Inherited from H-M1:**
  - transformers (model loading)
  - peft (LoRA fine-tuning)
  - lm-eval (TruthfulQA evaluation)
  - scipy (statistical analysis)

---

## Risks and Mitigations

### Risk 1: TransformerLens Compatibility with LoRA
**Likelihood:** Medium  
**Impact:** High  
**Mitigation:** 
- Test TransformerLens → HuggingFace → PEFT conversion pipeline before full experiment
- Fallback: Use manual hook registration (PyTorch standard approach)
- Reference: h-m1 used standard HuggingFace, so conversion path is available

### Risk 2: Activation Storage (Memory)
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Process activations in batches
- Save to disk immediately after extraction
- Free GPU memory after each layer extraction

### Risk 3: No Representation Changes Detected
**Likelihood:** Low (h-m1 validated parameter updates occur)  
**Impact:** Medium (SHOULD_WORK gate allows continuation)  
**Mitigation:**
- Document as limitation in 04_validation.md
- Explore alternative mechanisms (disentangled subnetworks)
- Gate type allows workflow continuation

---

## Appendix: Reference Implementations

### A. TransformerLens (Activation Extraction)
- **Repository:** https://github.com/TransformerLensOrg/TransformerLens
- **Documentation:** https://transformerlensorg.github.io/TransformerLens/
- **Key Features:**
  - `run_with_cache()` - Automatic activation extraction
  - Pre-integrated with HuggingFace models
  - Compatible with PEFT LoRA models

### B. pytorch-cka (Representation Similarity)
- **Repository:** https://github.com/ryusudol/Centered-Kernel-Alignment
- **Installation:** `pip install pytorch-cka`
- **Performance:** 44x faster than baseline CKA implementations
- **Key Features:**
  - GPU-accelerated
  - Built-in visualization
  - HuggingFace model support

### C. H-M1 Validation Results
- **File:** docs/youra_research/20260511_buildingtrust/h-m1/04_validation.md
- **Key Findings:**
  - Model: GPT-2 with LoRA (r=8, alpha=16)
  - Training: 3 epochs, batch=4, lr=1e-4, 100 samples
  - Performance: +2.32% TruthfulQA MC2 (p < 0.001)
  - Gate: PASS

---

**Document Status:** Ready for Phase 3 Implementation Planning  
**Next Phase:** Architecture Design (Step 3)
