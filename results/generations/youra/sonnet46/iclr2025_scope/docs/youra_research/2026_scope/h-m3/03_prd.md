# Product Requirements Document (PRD)
# H-M3: Sparsity-Rank Sensitivity Correlation

**Generated:** 2026-05-08  
**Phase:** 3 - Implementation Planning  
**Hypothesis:** H-M3 (MECHANISM)  
**Status:** Draft  
**Source:** h-m3/02c_experiment_brief.md  

---

## stepsCompleted
- [x] Executive Summary
- [x] Problem Statement
- [x] Functional Requirements
- [x] Non-Functional Requirements
- [x] Data Specification
- [x] Success Criteria
- [x] Dependencies

---

## 1. Executive Summary

This PRD specifies the implementation of a three-stream empirical study to verify the MECHANISM hypothesis H-M3: **Layers with higher MLP activation sparsity in LLaMA-3-8B require lower LoRA rank to achieve equivalent fine-tuning quality.** Specifically:

1. **Stream 1 (Joint Rank Sensitivity):** Pearson r ≤ -0.4 on sensitive layers (≥0.5% accuracy drop) for BOTH SST-2 AND MNLI between sparsity and rank sensitivity
2. **Stream 2 (AdaLoRA Correlation):** Kendall's tau ≥ 0.4 between sparsity ranking and AdaLoRA's learned allocation
3. **Stream 3 (Spectral Variance):** Sparsity explains ≥20% unique variance in ΔW spectral decay ratio beyond gradient norm (p < 0.05)

This experiment builds on confirmed results from H-M1 (ICC=0.9846, sparsity stable across distributions) and H-M2 (CV > 0.48 across all epsilon values, tau_min=0.9597). Sparsity profiles are inherited from H-M2 results (epsilon=0.01).

---

## 2. Problem Statement

### 2.1 Research Question

Do sparse MLP layers in LLaMA-3-8B require less LoRA rank for effective fine-tuning? If so, sparsity can serve as a zero-cost proxy for adaptive rank allocation — eliminating the expensive AdaLoRA training overhead.

### 2.2 Hypothesis H-M3 (MECHANISM Type)

> "Layers with higher MLP activation sparsity in LLaMA-3-8B require lower LoRA rank to achieve equivalent fine-tuning quality (Pearson r ≤ -0.4 on sensitive layers for both SST-2 and MNLI), sparsity ranking correlates with AdaLoRA's learned allocation (Kendall's tau ≥ 0.4), and sparsity explains ≥20% unique variance in delta-W spectral decay ratio beyond gradient norm (p < 0.05), because sparse layers operate in lower intrinsic-dimension subspaces requiring less LoRA rank for effective adaptation."

### 2.3 Gate Condition (MUST_WORK)

All three primary criteria must be satisfied simultaneously:
1. pearson_r_sst2 ≤ -0.4 AND pearson_r_mnli ≤ -0.4
2. kendall_tau_sst2 ≥ 0.4 AND kendall_tau_mnli ≥ 0.4
3. unique_var_sparsity ≥ 0.20 AND p_value_sparsity_beta < 0.05

**Risk R6 Fallback:** If SST-2 has < 5 sensitive layers → apply MNLI-only gate (pearson_r_mnli ≤ -0.4 AND kendall_tau_mnli ≥ 0.4)

### 2.4 Context

H-M3 is an INCREMENTAL hypothesis requiring:
- **H-M1 (PASS):** Sparsity profiles stable across distributions — justifies using Alpaca-calibrated sparsity for SST-2/MNLI
- **H-M2 (PASS):** Epsilon=0.01 confirmed as optimal; sparsity profiles inherited directly from `h-m2/experiment_results.json`

---

## 3. Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load sparsity profiles from `h-m2/experiment_results.json["sparsity_profiles"]["0.01"]` (32 float values, one per LLaMA MLP layer) — NO re-measurement
- **FR-1.2:** Load GLUE SST-2 dataset (train ~67K, val 872 samples) using HuggingFace `datasets` library
- **FR-1.3:** Load GLUE MNLI dataset (train ~393K, matched val 9815, mismatched val 9832) using HuggingFace `datasets`
- **FR-1.4:** Tokenize with LlamaTokenizer: max_length=512, truncation=True, padding='max_length'
- **FR-1.5:** SST-2: tokenize `sentence` field, labels {0=negative, 1=positive}
- **FR-1.6:** MNLI: tokenize `premise` + `hypothesis` (SEP-separated), labels {0=entailment, 1=neutral, 2=contradiction}

### FR-2: Baseline Uniform LoRA Training (Stream 1 Reference)
- **FR-2.1:** Train LLaMA-3.1-8B with uniform LoRA r=16 on SST-2 and MNLI (both tasks, 5 seeds each = 10 runs)
- **FR-2.2:** LoRA config: target_modules=["q_proj","v_proj","k_proj","o_proj","gate_proj","up_proj","down_proj"], r=16, lora_alpha=16
- **FR-2.3:** AdamW optimizer: lr=2e-4, weight_decay=0.01, betas=(0.9, 0.999)
- **FR-2.4:** Linear warmup + cosine decay schedule: warmup_ratio=0.03
- **FR-2.5:** Batch size 16, 3 epochs, bfloat16 precision
- **FR-2.6:** Store per-seed validation accuracy as `baseline_acc[task][seed]`
- **FR-2.7:** Store gradient Frobenius norms per MLP layer during training (for Stream 3)
- **FR-2.8:** Compute ΔW = B@A for each layer post-training (for Stream 3 spectral analysis)

### FR-3: Joint Rank Sensitivity Sweep (Stream 1 Primary)
- **FR-3.1:** For each of 32 LLaMA MLP layers (l ∈ {0..31}): reduce rank of layer l by Δr=2, redistribute 2×cost proportionally to remaining 31 layers (budget-neutral)
- **FR-3.2:** Build `rank_pattern` dict using HF PEFT LoraConfig API for each perturbation
- **FR-3.3:** Fine-tune perturbed model on SST-2 and MNLI (5 seeds each) → 32×2×5=320 training runs
- **FR-3.4:** Record `accuracy_drop[l][task]` = baseline_acc[task] − perturbed_acc[l][task]
- **FR-3.5:** Identify sensitive layers: `is_sensitive[l][task] = (accuracy_drop[l][task] >= 0.005)`
- **FR-3.6:** If all drops < 0.5%: increase Δr to 4 and repeat (logged as experiment modification)
- **FR-3.7:** Compute Pearson r between sparsity values and accuracy drops on sensitive layers per task

### FR-4: AdaLoRA Reference Run (Stream 2)
- **FR-4.1:** Train AdaLoRA at 60% parameter budget on SST-2 and MNLI (5 seeds each = 10 runs)
- **FR-4.2:** AdaLoraConfig: target_r=9 (≈60% of r=16), init_r=16, target_modules=same 7 proj types, tinit=100, tfinal=1500, deltaT=10, beta1=0.85, beta2=0.85, orth_reg_weight=0.5
- **FR-4.3:** Extract `rank_pattern` from trained model: `model.base_model.rank_pattern` → dict[layer_name → effective_rank]
- **FR-4.4:** Compute Kendall's tau (variant='b') between sparsity ranking (ascending sparsity = rank 1 = highest sparsity) and AdaLoRA allocation (descending rank = rank 1 = highest allocated rank)
- **FR-4.5:** Flag if all AdaLoRA allocations equal (uniform) — indicates AdaLoRA failed to learn heterogeneous allocation

### FR-5: ΔW Spectral Decay + Multiple Regression (Stream 3)
- **FR-5.1:** Post-training: compute ΔW = B@A for each MLP layer from uniform r=16 models (from FR-2.8)
- **FR-5.2:** SVD: compute spectral decay ratio = sum(top-4 singular values) / Frobenius norm for each layer
- **FR-5.3:** Use covariance-based SVD (eigvalsh on WᵀW or WWᵀ — smaller dimension) for efficiency
- **FR-5.4:** Multiple regression: [sparsity, grad_norm] → spectral_decay_ratio
- **FR-5.5:** Compute semipartial r² for sparsity coefficient (unique variance beyond gradient norm)
- **FR-5.6:** Report p-value for sparsity coefficient in regression

### FR-6: Correlation Analysis
- **FR-6.1:** Stream 1: Pearson r (scipy.stats.pearsonr) on sensitive layers only per task
- **FR-6.2:** Stream 2: Kendall's tau (scipy.stats.kendalltau, variant='b') across all 32 layers per task
- **FR-6.3:** Stream 3: Semipartial r² via sklearn + scipy regression
- **FR-6.4:** Report SST-2 and MNLI separately; detect and apply R6 fallback if SST-2 < 5 sensitive layers
- **FR-6.5:** Gate evaluation: determine PASS/FAIL per gate condition and overall

### FR-7: Visualization
- **FR-7.1:** Gate metrics comparison bar chart (mandatory): pearson_r, kendall_tau, unique_var vs. thresholds for both tasks
- **FR-7.2:** Scatter plots: per-layer sparsity vs. joint rank sensitivity (SST-2 and MNLI separately); highlight sensitive layers; annotate Pearson r and p-value
- **FR-7.3:** Sensitivity heatmap: 32×2 matrix (layers × tasks) with sparsity overlay
- **FR-7.4:** Bar chart: per-layer AdaLoRA allocation vs. inverse-sparsity-proportional prediction; Kendall's tau annotated
- **FR-7.5:** Scatter plot: ΔW spectral decay vs. sparsity; regression line with 95% CI; semipartial r² annotated
- **FR-7.6:** Histogram: per-layer accuracy drops with ≥0.5% threshold line
- **FR-7.7:** Output directory: `h-m3/figures/`

### FR-8: Results Logging and Reporting
- **FR-8.1:** Log mechanism activation indicators: `[SENSITIVITY] Layer {l}: accuracy_drop={drop:.4f}, sensitive={drop>=0.005}`
- **FR-8.2:** Save all results to `h-m3/experiment_results.json`
- **FR-8.3:** Print gate evaluation summary to stdout with all metric values and PASS/FAIL status
- **FR-8.4:** Generate Phase 4 validation report (`04_validation.md`)

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Source | Train | Validation | Test |
|---------|--------|-------|------------|------|
| GLUE SST-2 | HuggingFace `datasets` (auto-download) | ~67K | 872 | 1.8K |
| GLUE MNLI | HuggingFace `datasets` (auto-download) | ~393K | 9815 (matched) + 9832 (mismatched) | — |

**Loading Code:**
```python
from datasets import load_dataset
sst2 = load_dataset('glue', 'sst2')
mnli = load_dataset('glue', 'mnli')
```

**Auto-download:** Both datasets auto-download via HuggingFace `datasets` library. **No manual download task required.**

### 4.2 Inherited Data

| Artifact | Source | Format |
|----------|--------|--------|
| Sparsity profiles (ε=0.01) | `h-m2/experiment_results.json["sparsity_profiles"]["0.01"]` | dict[layer_name → float], 32 entries |
| LLaMA-3.1-8B model | Local cache: `~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B` | local_files_only=True |

### 4.3 Preprocessing

- Tokenizer: LlamaTokenizer (fast), max_length=512, truncation=True, padding='max_length'
- SST-2: tokenize `sentence` field
- MNLI: tokenize `premise` + `hypothesis` concatenated with tokenizer SEP token

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **NFR-1:** Single GPU only (CUDA_VISIBLE_DEVICES=<lowest-memory-GPU>)
- **NFR-2:** bfloat16 precision (torch.bfloat16) for all training runs
- **NFR-3:** Gradient checkpointing if OOM
- **NFR-4:** Covariance-based SVD (eigvalsh on smaller dimension) for ΔW spectral analysis — 10-100× faster than full SVD

### 5.2 Reproducibility
- **NFR-5:** All 5 seeds (42, 43, 44, 45, 46) for each experimental configuration
- **NFR-6:** local_files_only=True for model loading (no network access required)
- **NFR-7:** All random states set at experiment start: `torch.manual_seed(seed)`, `np.random.seed(seed)`

### 5.3 Code Quality
- **NFR-8:** Reuse components from h-m2/code/ where possible (data_utils.py, measure_sparsity.py)
- **NFR-9:** All scripts runnable from `h-m3/code/` directory
- **NFR-10:** pytest-compatible tests in `h-m3/code/tests/`

---

## 6. Success Criteria

### 6.1 Primary Gate Metrics (MUST_WORK)

| Metric | Threshold | Stream |
|--------|-----------|--------|
| pearson_r_sst2 | ≤ -0.4 | 1 |
| pearson_r_mnli | ≤ -0.4 | 1 |
| kendall_tau_sst2 | ≥ 0.4 | 2 |
| kendall_tau_mnli | ≥ 0.4 | 2 |
| unique_var_sparsity | ≥ 0.20 | 3 |
| p_value_sparsity_beta | < 0.05 | 3 |

**PASS:** All 6 metrics satisfied simultaneously

### 6.2 R6 Fallback Conditions

If SST-2 < 5 sensitive layers (accuracy_drop ≥ 0.5%):
- **Modified gate:** pearson_r_mnli ≤ -0.4 AND kendall_tau_mnli ≥ 0.4 (MNLI only)
- Document SST-2 rank-insensitivity as negative result

### 6.3 Baseline Performance Targets

| Model/Config | SST-2 | MNLI matched |
|---|---|---|
| Uniform LoRA r=16 (reference) | ~95% | ~90.7% |
| AdaLoRA 60% budget | — | ~90.76% (QingruZhang reference) |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.40.0
peft>=0.10.0          # For LoraConfig rank_pattern API + AdaLoraConfig
datasets>=2.18.0
evaluate>=0.4.0
scipy>=1.10.0          # pearsonr, kendalltau
scikit-learn>=1.3.0    # LinearRegression for semipartial r²
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
accelerate>=0.27.0
tqdm>=4.65.0
pyyaml>=6.0
```

### 7.2 External Reference Repositories (for reference only, not cloned)

| Repository | Purpose |
|-----------|---------|
| QingruZhang/AdaLoRA | AdaLoRA training loop patterns, rank_pattern extraction |
| sockeye44/dorascope | ΔW spectral analysis patterns (covariance-based SVD) |
| huggingface/peft | AdaLoraConfig and LoraConfig with rank_pattern API |

### 7.3 Inherited Code Components

| File | Source | Reuse |
|------|--------|-------|
| `data_utils.py` | `h-m2/code/data_utils.py` | GLUE loading + tokenization |
| `measure_sparsity.py` | `h-m2/code/measure_sparsity.py` | Sparsity loading only (no re-measurement) |

### 7.4 External Data (Pre-computed)

| Artifact | Path | Description |
|----------|------|-------------|
| Sparsity profiles | `h-m2/experiment_results.json` | 32-dim sparsity vector, epsilon=0.01 |
| LLaMA-3.1-8B | `~/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B` | Local model cache |

---

## 8. Risk Mitigations

| Risk ID | Description | Mitigation |
|---------|-------------|------------|
| R6 | SST-2 may be rank-insensitive (< 5 sensitive layers) | Apply MNLI-only gate; document as negative result |
| R4 | Marginal vs. joint rank sensitivity confound | Use budget-neutral joint perturbation (not marginal) |
| R3 | Spurious Pearson r | Include ΔW spectral decay as concurrent mechanistic check |
| R5 | Spectral decay as rank-constraint artifact | Train at r=4, r=8, r=16 for spectral verification |

---

## 9. Experiment Scale

**Total training runs:**
- Uniform r=16 reference: 2 tasks × 5 seeds = **10 runs**
- Joint sensitivity sweep: 32 layers × 2 tasks × 5 seeds = **320 runs** (~240 GPU-hrs estimated)
- AdaLoRA reference: 2 tasks × 5 seeds = **10 runs**
- **Total: ~340 fine-tuning runs**

**Evaluation samples:** Full validation sets (SST-2: 872; MNLI matched: 9,815; MNLI mismatched: 9,832)

---

*PRD generated from Phase 2C experiment brief (h-m3/02c_experiment_brief.md)*  
*Phase 3 Implementation Planning — UNATTENDED mode*
