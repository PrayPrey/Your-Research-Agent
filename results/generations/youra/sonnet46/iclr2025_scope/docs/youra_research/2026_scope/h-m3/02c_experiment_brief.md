# Experiment Design: h-m3

**Date:** 2026-05-08
**Author:** Anonymous
**Hypothesis Statement:** Layers with higher MLP activation sparsity in LLaMA-3-8B require lower LoRA rank to achieve equivalent fine-tuning quality (Pearson r ≤ -0.4 on sensitive layers for both SST-2 and MNLI), sparsity ranking correlates with AdaLoRA's learned allocation (Kendall's tau ≥ 0.4), and sparsity explains ≥20% unique variance in delta-W spectral decay ratio beyond gradient norm (p < 0.05), because sparse layers operate in lower intrinsic-dimension subspaces requiring less LoRA rank for effective adaptation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 (PASS, ICC=0.9846), H-M2 (PASS, tau_min=0.9597)
**Gate Status:** MUST_WORK (not yet evaluated — H-M3 pending)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (PASS), H-M2 (PASS)

### Gate Condition
MUST_WORK: All three primary criteria must pass:
1. Pearson r ≤ -0.4 on sensitive layers (≥0.5% accuracy drop) for BOTH SST-2 AND MNLI
2. Kendall's tau ≥ 0.4 between sparsity ranking and AdaLoRA's learned allocation
3. Sparsity unique variance ≥ 20% in ΔW spectral decay beyond gradient norm (p < 0.05)

---

## Continuation Context

**This is a continuation experiment (H-M3 depends on H-M1 + H-M2).**

### Previous Hypothesis Results

**H-M1 (PASS):** ICC(3,k)=0.9846 > 0.75; all 6 pairwise Kendall tau ≥ 0.73; sparsity profiles stable across Alpaca, WikiText-103, SST-2 val, MNLI val. Confirms Alpaca is valid task-agnostic calibration source.

**H-M2 (PASS):** CV > 0.48 for all 4 epsilon values; cross-epsilon tau > 0.96 for all 6 pairs. Epsilon=0.01 confirmed as primary. Sparsity rank ordering essentially identical across all epsilon choices.

**Key Inherited Artifacts:**
- Sparsity profiles: Load from `h-m2/experiment_results.json` → `sparsity_profiles["0.01"]`
- Epsilon: 0.01 (primary, validated stable)
- Architecture: LLaMA-3.1-8B with gate_proj hooks (same as h-e1, h-m1, h-m2)
- Local model path: `~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B` (use local_files_only=True)

**Active Risk Mitigations:**
- R6: Analyze SST-2 and MNLI separately throughout; if SST-2 < 5 sensitive layers, apply MNLI-only fallback immediately
- R4: Use joint sensitivity protocol (budget-neutral rank redistribution), not marginal
- R3: Include ΔW spectral decay as concurrent mechanistic check
- R5: Train at r=4, r=8, r=16 to verify spectral decay is not rank-constraint artifact

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: LoRA rank sensitivity per-layer activation sparsity**
- **Result 1**: HuggingFace PEFT LoRA Conceptual Guide (similarity 0.574)
  - Key insight: LoRA's rank r controls intrinsic dimension of weight update; per-layer rank control is supported via `rank_pattern` dict in LoraConfig
  - Dataset: GLUE tasks (SST-2, MNLI, etc.) standard benchmark
  - Implementation: `LoraConfig(rank_pattern={"model.layers.0.mlp": 8, "model.layers.1.mlp": 4, ...})`
  - Used for: rank_pattern API design in sensitivity perturbation experiment

- **Result 2**: HF Papers — AdaLoRA (arxiv 2303.10512, similarity 0.534)
  - Key insight: AdaLoRA uses SVD-based importance scoring per rank triplet; final `rank_pattern` attribute stores per-layer allocation
  - GLUE MNLI performance: 90.76% at 0.3M parameters (budget-matched)
  - Implementation: `peft.AdaLoraConfig` with `rank_pattern` field after training

**Query 2: AdaLoRA adaptive rank allocation**
- **Result 1**: AdaLoRA paper (ICLR 2023) — global competition across all singular values across all layers; top-b triplets by importance score retained
- Key insight: Final `rank_pattern` is extractable from AdaLoRA model via `model.base_model.rank_pattern`; this gives per-layer effective rank allocation for Kendall's tau comparison

**Query 3: GLUE SST-2 MNLI fine-tuning LLaMA LoRA**
- Archon KB not highly specific to LLaMA-3 GLUE; supplemented by Exa findings

**Archon Knowledge Base Summary:**
- LoRA rank_pattern API confirmed for per-layer rank control
- AdaLoRA rank_pattern extraction path identified
- GLUE benchmark performance baselines available (AdaLoRA: SST-2 ~95%, MNLI ~90.76%)

### Archon Code Examples

**Query: LoRA rank sensitivity PyTorch**
- `LoraConfig(r=rank, lora_alpha=rank, target_modules=["q_proj","k_proj","v_proj","o_proj"], rank_pattern={...})` — from HF PEFT documentation
- Pattern: per-layer rank assignment via rank_pattern dict
- Used for: sensitivity perturbation implementation (reduce rank of layer l by Δr=2, increase other layers proportionally)

### Exa GitHub Implementations

**Query 1: AdaLoRA official implementation (QingruZhang/AdaLoRA)**

**Repository 1:** `QingruZhang/AdaLoRA` (ICLR 2023 official)
- **URL:** https://github.com/QingruZhang/AdaLoRA
- **Relevance:** Official AdaLoRA implementation; NLU/ directory has GLUE benchmark examples with DeBERTaV3-base; shows how RankAllocator extracts final per-layer allocation
- **Key Code:**
  ```python
  from loralib import RankAllocator
  rankallocator = RankAllocator(
      model, lora_r=12, target_rank=8,
      init_warmup=500, final_warmup=1500, mask_interval=10,
      total_step=3000, beta1=0.85, beta2=0.85,
  )
  # In training loop:
  (loss + compute_orth_regu(model, regu_weight=0.1)).backward()
  optimizer.step()
  rankallocator.update_and_mask(model, global_step)
  ```
- **Training Config:**
  - Optimizer: AdamW
  - Target rank: 8 (from init_r=12)
  - beta1=0.85, beta2=0.85 (EMA for importance smoothing)
- **Dataset:** GLUE (SST-2, MNLI, CoLA, etc.)
- **Results:** MNLI 90.76% at 0.3M parameters

**Repository 2:** `huggingface/peft` — AdaLoRA integration
- **URL:** https://github.com/huggingface/peft (src/peft/tuners/adalora/)
- **Relevance:** Production implementation; `rank_pattern` field in AdaLoraConfig stores final per-layer allocation
- **Key Config:**
  ```python
  from peft import AdaLoraConfig, get_peft_model
  config = AdaLoraConfig(
      target_r=8, init_r=12,
      tinit=100, tfinal=1500, deltaT=10,
      beta1=0.85, beta2=0.85,
      orth_reg_weight=0.5,
      total_step=None,  # set to total training steps
      target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]
  )
  model = get_peft_model(base_model, config)
  # After training: model.base_model.rank_pattern → dict of per-layer ranks
  ```
- **Used for:** AdaLoRA rank extraction for Kendall's tau comparison

**Query 2: LoRA per-layer rank sensitivity SVD spectral decay**

**Repository 3:** `sockeye44/dorascope` — LoRA/DoRA spectral analysis
- **URL:** https://github.com/sockeye44/dorascope
- **Relevance:** Tracks LoRA adapter spectral metrics across training; computes SV decay rate, effective rank, stable rank per layer
- **Key Metrics:**
  - Spectral decay: `SV decay rate` = log-linear slope of singular values
  - Effective rank: Shannon entropy-based `exp(-Σ pᵢ log pᵢ)` over singular values
  - Rank utilization: effective rank / allocated rank
- **Implementation insight:** Covariance-based SVD via `eigvalsh` on smaller of WᵀW or WWᵀ — 10-100x faster than full SVD
- **Used for:** ΔW spectral decay ratio computation design

**Paper Reference:** Spectral Surgery (arxiv 2603.03995) — defines sensitivity score for singular components:
```
s_k = |g_k| where g_k = tr(U_k V_k^T * G)
G = ∂L/∂ΔW (gradient w.r.t. weight update)
```
Directly applicable to H-M3's ΔW spectral decay ratio computation and gradient norm comparison.

**Paper Reference:** ShapLoRA (arxiv 2601.17921) — shows per-layer rank sensitivity heatmaps for LLaMA-3 8B at layers 8, 16, 24, 32; confirms heterogeneous rank sensitivity across layers in LLaMA-3.

**Serena Analysis Needed:** false — code from Exa results is sufficiently clear for pseudo-code generation.

### 🎯 Implementation Priority Assessment

**This is an original hypothesis (not paper reproduction) — no single "official" implementation to reproduce.**

**Primary implementation path:** Custom implementation using:
1. HF PEFT LoRA + AdaLoRA for reference comparison
2. QingruZhang/AdaLoRA for rank_pattern extraction patterns
3. dorascope spectral analysis patterns for ΔW SVD computation

**Recommended Implementation Path:**
- Primary: Custom PyTorch + HF PEFT (rank_pattern API for per-layer rank manipulation)
- Fallback: Extend AdaLoRA training loop to extract rank allocations for comparison
- Justification: No prior work directly measures joint rank sensitivity per-layer and correlates with activation sparsity; must implement custom sensitivity sweep

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. Key patterns extracted:
- AdaLoRA rank_pattern extraction via `model.base_model.rank_pattern` (dict, layer_name → effective_rank)
- LoRA rank_pattern in LoraConfig for per-layer rank assignment during sensitivity perturbation
- torch.linalg.svd for ΔW spectral analysis; eigvalsh for covariance-based efficiency
- scipy.stats.pearsonr for Pearson r; kendalltau for rank correlation

---

## Experiment Specification

### Dataset

**Primary Datasets:** GLUE SST-2 + GLUE MNLI (full standard splits)
- **Type:** standard (HuggingFace datasets)
- **SST-2:** Binary sentiment classification; train ~67K / val 872 / test 1.8K
- **MNLI:** Natural language inference (3-class); train ~393K / matched val 9815 / mismatched val 9832
- **Calibration input:** Alpaca sparsity profiles from h-m2/experiment_results.json (pre-computed, not re-measured)

**Dataset Policy:** Real established datasets — CONFIRMED (type: standard)

**Dataset Hypothesis Fit:**
- SST-2 and MNLI are the exact datasets from the main H-SparsityLoRA-v1 hypothesis
- Two tasks with different supervision signals test whether the sparsity-rank correlation holds cross-task
- SST-2 may be rank-insensitive (DyLoRA prior; Risk R6) — this is expected and handled by MNLI-only fallback

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `glue` / `sst2`, `glue` / `mnli`
- Code:
  ```python
  from datasets import load_dataset
  sst2 = load_dataset('glue', 'sst2')  # train / validation / test
  mnli = load_dataset('glue', 'mnli')  # train / validation_matched / validation_mismatched
  ```

**Evaluation samples:** Full validation sets (SST-2: 872 samples; MNLI matched: 9815 + mismatched: 9832)

**Preprocessing:**
- Tokenizer: LlamaTokenizer (fast), max_length=512, truncation=True, padding='max_length'
- SST-2: tokenize `sentence`, label in {0=negative, 1=positive}
- MNLI: tokenize `premise` + `hypothesis` (SEP-separated), label in {0=entailment, 1=neutral, 2=contradiction}
- No data augmentation (classification fine-tuning)

### Models

#### Baseline Model

**Architecture:** LLaMA-3.1-8B with uniform LoRA r=16 on all 7 projection types
- **Configuration:**
  - Target modules: q_proj, v_proj, k_proj, o_proj, gate_proj, up_proj, down_proj (all 7)
  - Rank: r=16 (uniform), lora_alpha=16
  - Total parameter budget: r=16 across all layers → reference budget
  - 5 random seeds (42, 43, 44, 45, 46)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers (local cache)
- Identifier: `meta-llama/Llama-3.1-8B` (local snapshot)
- Code:
  ```python
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  model = AutoModelForSequenceClassification.from_pretrained(
      "meta-llama/Llama-3.1-8B",
      local_files_only=True,
      num_labels=2,  # SST-2; 3 for MNLI
      torch_dtype=torch.bfloat16,
  )
  tokenizer = AutoTokenizer.from_pretrained(
      "meta-llama/Llama-3.1-8B", local_files_only=True
  )
  ```

#### Proposed Model

**Architecture:** Same LLaMA-3.1-8B + 3 experimental configurations for sensitivity measurement

**Core Mechanism: Joint Rank Sensitivity Perturbation + Multi-Signal Correlation Analysis**

The experiment has THREE concurrent measurement streams:

**Stream 1: Joint Rank Sensitivity Sweep (32 perturbations × 2 tasks × 5 seeds)**
- For each layer l ∈ {0..31}: reduce rank of layer l by Δr=2, redistribute 2*cost to other 31 layers proportionally
- Fine-tune and record accuracy drop vs. uniform r=16 baseline
- Identify sensitive layers (≥0.5% drop); compute Pearson r vs. sparsity ranking

**Stream 2: AdaLoRA Reference Run (2 tasks × 5 seeds)**
- Train AdaLoRA at 60% budget on SST-2 and MNLI
- Extract final `rank_pattern` per layer; compute Kendall's tau vs. sparsity ranking

**Stream 3: ΔW Spectral Analysis + Multiple Regression**
- Post-training: compute ΔW = B@A for each layer from fine-tuned uniform r=16 model
- SVD: compute spectral decay ratio = sum(top-4 SVs) / Frobenius norm
- Also compute gradient Frobenius norm (stored during training)
- Multiple regression: sparsity + grad_norm → spectral_decay (compute semipartial r² for sparsity)

**Core Mechanism Pseudo-code:**

```python
# Core Mechanism: Joint Rank Sensitivity Measurement + Sparsity Correlation
# Based on: HF PEFT rank_pattern API + AdaLoRA (QingruZhang/AdaLoRA) + dorascope SVD patterns

import torch, numpy as np
from peft import LoraConfig, get_peft_model, AdaLoraConfig
from scipy.stats import pearsonr, kendalltau
from sklearn.linear_model import LinearRegression

# --- Step 1: Load pre-computed sparsity profiles from H-M2 ---
sparsity = load_json("h-m2/experiment_results.json")["sparsity_profiles"]["0.01"]
# sparsity: dict[layer_name → float], 32 entries

# --- Step 2: Fine-tune uniform r=16 reference (5 seeds, 2 tasks) ---
def finetune_uniform(task, seed, r=16):
    config = LoraConfig(r=r, lora_alpha=r, target_modules=TARGET_MODULES)
    model = get_peft_model(load_base_model(), config)
    train(model, task, seed)
    delta_W = {n: p.data.clone() for n, p in model.named_parameters()
               if "lora_B" in n}  # ΔW = B@A computed post-training
    grad_norms = {n: g.norm("fro") for n, g in stored_grads.items()}
    return model, delta_W, grad_norms

# --- Step 3: Per-layer joint sensitivity sweep ---
def measure_joint_sensitivity(task, seed, layer_idx, delta_r=2):
    # Budget-neutral: reduce layer_idx by delta_r, redistribute to others
    rank_pattern = build_joint_rank_pattern(layer_idx, delta_r, r_base=16)
    config = LoraConfig(r=16, rank_pattern=rank_pattern, target_modules=TARGET_MODULES)
    model = get_peft_model(load_base_model(), config)
    acc = finetune_and_eval(model, task, seed)
    baseline_acc = precomputed_baseline[task][seed]
    return baseline_acc - acc  # positive = sensitive (drop)

# --- Step 4: AdaLoRA reference run ---
def run_adalora(task, seed, budget_60pct):
    config = AdaLoraConfig(target_r=budget_60pct, init_r=16,
                           target_modules=TARGET_MODULES,
                           tinit=100, tfinal=1500, deltaT=10)
    model = get_peft_model(load_base_model(), config)
    train_adalora(model, task, seed)
    return model.base_model.rank_pattern  # dict: layer_name → effective_rank

# --- Step 5: Correlation analysis ---
sensitive_mask = sensitivity_drop >= 0.005  # ≥0.5% accuracy drop
pearson_r, p_val = pearsonr(sparsity[sensitive_mask], sensitivity_drop[sensitive_mask])
tau, _ = kendalltau(sparsity_rank, adalora_rank)

# --- Step 6: ΔW spectral decay + multiple regression ---
spectral_decay = {l: svd_top4_ratio(delta_W[l]) for l in layers}
reg = LinearRegression().fit([[sparsity[l], grad_norms[l]] for l in layers],
                              [spectral_decay[l] for l in layers])
unique_var_sparsity = semipartial_r2(sparsity, grad_norms, spectral_decay)
```

### Training Protocol

**Inherited from H-M1/H-M2 validated settings (controlled comparison):**

**Optimizer:** AdamW
- lr=2e-4, weight_decay=0.01, betas=(0.9, 0.999)
- **Source:** Main hypothesis specification (02b_verification_plan.md §1.3)

**Learning Rate Schedule:** Linear warmup + cosine decay
- Warmup ratio: 0.03 (≈ 3% of total steps)
- **Source:** Phase 2A controlled variables

**Batch Size:** 16 (per device, gradient_accumulation_steps=1)
- **Source:** Phase 2A controlled variables

**Epochs:** 3 (both SST-2 and MNLI)
- **Source:** Phase 2A controlled variables

**Loss Function:**
- SST-2: CrossEntropyLoss (binary, 2 classes)
- MNLI: CrossEntropyLoss (3 classes: entailment/neutral/contradiction)

**Seeds:** 5 seeds {42, 43, 44, 45, 46} for sensitivity sweep (average over seeds for stable sensitivity estimate)

**Experimental runs breakdown:**
- Uniform r=16 reference: 2 tasks × 5 seeds = 10 runs
- Joint sensitivity sweep: 32 layers × 2 tasks × 5 seeds = 320 runs (primary bottleneck, ~240 GPU-hrs)
- AdaLoRA reference: 2 tasks × 5 seeds = 10 runs
- Total: ~340 fine-tuning runs

**GPU Configuration:**
- Single GPU (NVIDIA H100 NVL, CUDA_VISIBLE_DEVICES=0)
- bf16 precision (torch.bfloat16)
- Gradient checkpointing if OOM

### Evaluation

**Task-Specific Metrics:**
- SST-2: Accuracy (binary classification)
- MNLI: Accuracy on matched validation set (3-class); also report mismatched accuracy

**Primary Gate Metrics:**
1. `pearson_r_sst2`: Pearson r between sparsity and joint sensitivity on sensitive layers (SST-2)
2. `pearson_r_mnli`: Pearson r between sparsity and joint sensitivity on sensitive layers (MNLI)
3. `kendall_tau_sst2`: Kendall's tau between sparsity ranking and AdaLoRA allocation (SST-2)
4. `kendall_tau_mnli`: Kendall's tau between sparsity ranking and AdaLoRA allocation (MNLI)
5. `unique_var_sparsity`: Semipartial r² for sparsity in multiple regression (ΔW spectral decay)
6. `p_value_sparsity_beta`: Significance of sparsity coefficient in regression

**Success Criteria (MUST_WORK):**
- pearson_r_sst2 ≤ -0.4 AND pearson_r_mnli ≤ -0.4 (both tasks, sensitive layers only)
- kendall_tau_sst2 ≥ 0.4 AND kendall_tau_mnli ≥ 0.4
- unique_var_sparsity ≥ 0.20 AND p_value_sparsity_beta < 0.05

**Risk R6 Fallback (if SST-2 has < 5 sensitive layers):**
- Apply MNLI-only gate: pearson_r_mnli ≤ -0.4 AND kendall_tau_mnli ≥ 0.4 (MNLI only)
- Document SST-2 rank-insensitivity as negative result (consistent with DyLoRA findings)

**Expected Performance (from Phase 2B research):**
- Baseline uniform r=16 SST-2: ~95% accuracy (LoRA standard results)
- Baseline uniform r=16 MNLI: ~90.7% accuracy (AdaLoRA reference)
- AdaLoRA MNLI matched: 90.76% at 0.3M parameters (QingruZhang/AdaLoRA ICLR 2023)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: text_classification (binary SST-2; 3-class MNLI)
- Library: `evaluate` (HuggingFace) + `scipy.stats` + `sklearn.linear_model`
- Code:
  ```python
  import evaluate
  metric = evaluate.load("glue", "sst2")   # or "mnli"
  result = metric.compute(predictions=preds, references=labels)
  # Returns: {"accuracy": float}

  from scipy.stats import pearsonr, kendalltau
  r, p = pearsonr(sparsity_vals, sensitivity_vals)
  tau, _ = kendalltau(sparsity_rank, adalora_rank)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of pearson_r, kendall_tau, unique_var for SST-2 and MNLI vs. gate thresholds

#### Additional Figures (LLM Autonomous)
1. **Scatter plot:** Per-layer sparsity vs. joint rank sensitivity (SST-2, MNLI separately) — highlight sensitive layers (≥0.5% drop); annotate Pearson r and p-value
2. **Heatmap:** 32 × 2 sensitivity matrix (layers × tasks) with sparsity overlay as color gradient
3. **Bar chart:** Per-layer AdaLoRA rank allocation vs. sparsity-predicted allocation (inverse-sparsity-proportional under 60% budget) — Kendall's tau annotated
4. **Scatter plot:** ΔW spectral decay ratio vs. sparsity per layer; color by gradient norm; regression line with 95% CI; semipartial r² annotated
5. **Sensitivity distribution:** Histogram of per-layer accuracy drops (both tasks) with ≥0.5% threshold line

**Output Location:** `h-m3/figures/`

---

## 🔬 Mechanism Verification Protocol

**Mechanism Name:** Sparsity-Rank Sensitivity Correlation (three-stream evidence)

**Pre-conditions:**
- mechanism_exists: true (sparsity profiles available from H-M2; rank sensitivity is measurable via perturbation)
- mechanism_isolatable: true (per-layer rank reduction is budget-neutral; only one layer perturbed at a time)
- baseline_measurable: true (uniform r=16 accuracy measured in 5-seed reference runs)

**Architecture Compatibility:**
- LLaMA-3.1-8B with 32 MLP layers supports per-layer rank_pattern in HF PEFT LoraConfig
- AdaLoRA available in peft >= 0.4.0; rank_pattern extraction via `model.base_model.rank_pattern`
- torch.linalg.svd supports batched SVD for ΔW matrices (d_out × d_in, e.g., 4096×4096)

**Mechanism Activation Indicators:**
- Log: `[SENSITIVITY] Layer {l}: accuracy_drop={drop:.4f}, sensitive={drop>=0.005}`
- Tensor shapes: ΔW per layer has shape (d_out, d_in); top-4 SVs shape (4,)
- Metric delta expected: pearson_r should be negative (-0.4 to -0.8 range based on H-M3 hypothesis)

**Failure Detection:**
- If pearson_r > -0.2 for both tasks: mechanism fails; log and report "No sparsity-sensitivity correlation"
- If < 5 sensitive layers on SST-2: apply R6 fallback, report SST-2 rank-insensitivity
- If all sensitivity drops < 0.5%: increase Δr to 4 and repeat (logged as experiment modification)
- If AdaLoRA rank_pattern all equal (uniform): AdaLoRA failed to learn heterogeneous allocation; flag

**Mechanism Verification Code:**
```python
# Verify mechanism activated (before reporting gate result)
n_sensitive_sst2 = sum(1 for d in sensitivity_sst2 if d >= 0.005)
n_sensitive_mnli = sum(1 for d in sensitivity_mnli if d >= 0.005)
r6_fallback = n_sensitive_sst2 < 5  # Risk R6 triggered

gate_pearson = (pearson_r_mnli <= -0.4) if r6_fallback else (pearson_r_sst2 <= -0.4 and pearson_r_mnli <= -0.4)
gate_tau = (kendall_tau_mnli >= 0.4) if r6_fallback else (kendall_tau_sst2 >= 0.4 and kendall_tau_mnli >= 0.4)
gate_spectral = (unique_var_sparsity >= 0.20) and (p_value_sparsity_beta < 0.05)

gate_pass = gate_pearson and gate_tau and gate_spectral
print(f"[GATE] MUST_WORK: {'PASS' if gate_pass else 'FAIL'}")
print(f"  pearson_r SST-2={pearson_r_sst2:.3f}, MNLI={pearson_r_mnli:.3f} (gate<=−0.4)")
print(f"  kendall_tau SST-2={kendall_tau_sst2:.3f}, MNLI={kendall_tau_mnli:.3f} (gate>=0.4)")
print(f"  unique_var_sparsity={unique_var_sparsity:.3f} (gate>=0.20), p={p_value_sparsity_beta:.4f}")
```

**Hypothesis Support Threshold:** pearson_r ≤ -0.4 AND tau ≥ 0.4 AND unique_var ≥ 0.20
**Hypothesis Support Metric:** All three primary gate criteria simultaneously satisfied

---

## Ablation Studies

**H-M3 is a MECHANISM hypothesis — ablation is built into the 3-stream verification design:**

| Variant | What It Measures |
|---------|-----------------|
| Sensitivity vs. sparsity (Stream 1) | Does sparsity predict which layers are rank-critical? |
| Sensitivity vs. AdaLoRA allocation (Stream 2) | Does sparsity approximate learned adaptive rank without training? |
| Sparsity vs. grad_norm in regression (Stream 3) | Does sparsity add unique information beyond gradient magnitude? |
| SST-2 vs. MNLI separate analysis | Task-conditioned sensitivity (Risk R6 detection) |
| R6 fallback scope | MNLI-only gate if SST-2 rank-insensitive |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** HuggingFace PEFT LoRA Conceptual Guide
- **URL:** https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora
- **Query:** LoRA rank sensitivity per-layer activation sparsity
- **Key Insights:**
  - `rank_pattern` dict in LoraConfig enables per-layer rank assignment
  - Per-layer rank manipulation is production-supported in PEFT
- **Used For:** Rank perturbation protocol design (joint sensitivity sweep)

**Source A.2:** AdaLoRA Paper (ICLR 2023) — HF Papers hf.co/papers/2305.14314
- **Query:** AdaLoRA adaptive rank allocation fine-tuning LLM
- **Key Insights:**
  - Final rank allocation stored in `rank_pattern` after training
  - Budget 0.3M parameters → MNLI 90.76% accuracy
  - Global competition across all singular values for rank budget
- **Used For:** AdaLoRA reference run design; Kendall's tau baseline

### B. GitHub Implementations (Exa)

**Repository B.1:** QingruZhang/AdaLoRA (Official, ICLR 2023)
- **URL:** https://github.com/QingruZhang/AdaLoRA
- **Query:** AdaLoRA adaptive rank allocation implementation GitHub per-layer LoRA
- **Architecture Used:** DeBERTaV3-base on GLUE (NLU/); SVDLinear + RankAllocator pattern
- **Key Code:** `rankallocator.update_and_mask(model, global_step)` — updates importance scores and allocates budget
- **Configuration Extracted:** lora_r=12, target_rank=8, beta1=beta2=0.85, orth_regu=0.1
- **Results:** MNLI 90.76% at 0.3M parameters
- **Used For:** AdaLoRA rank extraction pattern; training loop integration

**Repository B.2:** huggingface/peft — AdaLoraConfig
- **URL:** https://github.com/huggingface/peft/blob/main/src/peft/tuners/adalora/config.py
- **Key Config:**
  ```
  target_r=8, init_r=12, tinit=0, tfinal=0, deltaT=1,
  beta1=0.85, beta2=0.85, orth_reg_weight=0.5
  rank_pattern: Optional[dict] = None  # populated after training
  ```
- **Used For:** AdaLoraConfig setup for LLaMA-3.1-8B on SST-2/MNLI

**Repository B.3:** sockeye44/dorascope — LoRA spectral analysis
- **URL:** https://github.com/sockeye44/dorascope
- **Key Metrics:** SV decay rate (log-linear slope), effective rank, stable rank, rank utilization
- **Key Insight:** Covariance-based SVD (eigvalsh on WᵀW) — 10-100x faster for large matrices
- **Used For:** ΔW spectral decay ratio computation design

### C. Paper References

**Paper C.1:** Spectral Surgery (arxiv 2603.03995) — gradient-based singular component sensitivity
- Sensitivity score: `s_k = |tr(U_k V_k^T * G)|` where G = ∂L/∂ΔW
- Used For: ΔW spectral analysis methodology

**Paper C.2:** ShapLoRA (arxiv 2601.17921) — per-layer rank sensitivity in LLaMA-3 8B
- Shows heterogeneous rank sensitivity across layers 8, 16, 24, 32 of LLaMA-3 8B
- Confirms that rank sensitivity varies significantly across layers — validates H-M3 hypothesis premise

**Paper C.3:** MSPLoRA (arxiv 2503.21838) — SVD analysis of per-layer LoRA components
- Records top-8 singular values of LoRA components per layer during training
- Shows layer-specific components have lower effective rank — supports H-M3 mechanism

### D. Previous Hypothesis Context

**Source D.1:** H-M2 Phase 4 Validation Report (h-m2/04_validation.md)
- **Gate Result:** PASS (all 4 epsilon values pass CV > 0.3; tau_min=0.9597 > 0.7)
- **Reused Components:**
  - Sparsity profiles: `h-m2/experiment_results.json["sparsity_profiles"]["0.01"]` — 32-dim vector
  - measure_layer_sparsity: `h-m2/code/measure_sparsity.py` — reusable
  - data_utils.py: `h-m2/code/data_utils.py` — reusable for GLUE loading
  - Local LLaMA-3.1-8B path: confirmed working with local_files_only=True
- **Why Reused:** Sparsity profiles are the independent variable in H-M3; no re-measurement needed (saves ~1 hour GPU)

**Source D.2:** H-M1 Phase 4 Validation Report (h-m1/04_validation.md)
- **Key Result:** ICC(3,k)=0.9846 — Alpaca-calibrated sparsity is valid across distributions including SST-2 and MNLI validation sets
- **Impact on H-M3:** Justifies using Alpaca-calibrated sparsity as task-agnostic signal for both SST-2 and MNLI sensitivity correlation

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: GLUE SST-2 + MNLI | Phase 2A/2B | verification_state.yaml §main_hypothesis |
| Dataset loading code | Exa / HF docs | load_dataset('glue', 'sst2/mnli') |
| Sparsity profiles (IV) | H-M2 results | D.1: h-m2/experiment_results.json |
| Baseline model: LLaMA-3.1-8B | Phase 2A/2B | D.2: confirmed local cache |
| Uniform r=16 LoRA config | Archon A.1 | PEFT rank_pattern API |
| Per-layer rank perturbation | Archon A.1 | LoraConfig rank_pattern per-layer |
| AdaLoRA reference config | Archon A.2 + B.1 | QingruZhang/AdaLoRA |
| AdaLoRA rank extraction | Exa B.2 | peft AdaLoraConfig.rank_pattern |
| ΔW spectral decay ratio | Exa B.3, C.1 | dorascope + Spectral Surgery |
| Multiple regression method | Paper C.2, C.3 | ShapLoRA + MSPLoRA SVD analysis |
| Pearson r / Kendall tau | H-M1/H-M2 code | scipy.stats (kendalltau variant='b') |
| Training hyperparameters | Phase 2A/2B | controlled variables (lr=2e-4, bs=16, epochs=3) |
| AdaLoRA hyperparameters | Exa B.1 | QingruZhang defaults (beta1=beta2=0.85) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-08T08:39:04Z

### Workflow History for This Hypothesis
- 2026-05-08T08:39:04Z: Hypothesis h-m3 set to IN_PROGRESS (external loop)
- 2026-05-08: Phase 2C experiment design IN_PROGRESS → COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (skipped — code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
