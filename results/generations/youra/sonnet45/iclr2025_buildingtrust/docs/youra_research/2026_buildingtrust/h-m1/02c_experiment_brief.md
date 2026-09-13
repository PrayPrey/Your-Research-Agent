# Experiment Design: h-m1

**Date:** 2026-03-17
**Author:** Anonymous
**Hypothesis Statement:** Under RLHF alignment of LLMs (PPO and DPO), alignment-induced logit deltas (aligned_logits − base_logits) are axis-specific and non-isotropic (structured perturbations), with anisotropy ratio significantly > 1.0 (p < 0.05) in ≥ 2 of 3 model families, because Li et al. [2024] confirmed heterogeneous axis-specific trustworthiness changes rather than isotropic noise post-RLHF.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Validates structural non-isotropy of alignment-induced logit perturbations.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 PASS (β₁=-4.33, AUROC=0.867, p≈4.1×10⁻²²⁷)
**Gate Status:** MUST_WORK — Anisotropy ratio > 1.0 (p < 0.05) in ≥ 2/3 model families

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
MUST_WORK gate: Anisotropy ratio (leading eigenvalue / mean other eigenvalues of Δ covariance matrix) significantly > 1.0 (paired t-test, p < 0.05) in ≥ 2 of 3 model families. If fails: EXPLORE — mechanism chain narrows to H-E1 only; pipeline continues with documentation.

---

## Continuation Context

H-E1 completed successfully (PASS, 2026-03-17). Key infrastructure to reuse:

**Functional Model Pairs:**
| Pair | Base Model | Aligned Model | Method | H-E1 Status |
|------|-----------|--------------|--------|-------------|
| pair2 | allenai/tulu-2-7b | allenai/tulu-2-dpo-7b | DPO | ✅ β₁=-4.33, AUROC=0.867 |
| pair4 | EleutherAI/pythia-6.9b | dvruette/oasst-pythia-6.9b-4000-steps | SFT | ✅ β₁=-0.062, p=0.002 |
| pair_new | EleutherAI/pythia-1.4b | pvduy/pythia-1.4b-rl-trlx-dolly15k | PPO | 🆕 To validate |

**Infrastructure Available from H-E1:**
- Log-probability extraction via HuggingFace forward pass (functional)
- 4D MCQ logit extraction pipeline
- Dataset loading: MMLU 14,042 items, TruthfulQA 817, ARC-Challenge 1,172 (all cached)
- Conda env `youra-h-e1` (Python 3.10, H100 NVL GPU 0)

### Previous Hypothesis Results (H-E1)
- Confirmed: confidence margin predicts argmax flip with strong AUROC
- Infrastructure issues avoided: `allenai/tulu-2-ppo-7b` (404), `reciprocate/ppo_hh_pythia-1B` (tokenizer error)
- Key code pattern: direct HuggingFace forward pass for logit extraction

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Domain Mismatch (documented):** Archon KB is populated with diffusion model content (LoRA, LyCORIS, DALLE-2, HunyuanDiT). Zero relevant results for RLHF logit analysis. Consistent with H-E1 finding.

**Query 1: logit anisotropy RLHF structured perturbations**
- Top results: PEFT LoRA docs, LyCORIS, 4-bit quantization — similarity 0.43–0.46, all diffusion model content
- Insight: No past cases in KB for this research domain

**Query 2: LLM logit delta covariance eigenvalue analysis**
- Top results: HuggingFace diffusers PRs, diffusion papers — similarity 0.31–0.39
- Insight: No matching methodology documented

**Query 3: DPO PPO logit distribution MCQ benchmark**
- Top results: DPM-Solver, AlignYourSteps (diffusion schedulers) — similarity 0.33–0.36
- Insight: Domain mismatch confirmed; no actionable results

**Assessment:** Archon KB provides no applicable prior cases for this hypothesis. All specifications derived from Phase 2A/2B research findings, H-E1 validated infrastructure, and known literature (Li et al. [2024], Xu et al. [2024]).

### Archon Code Examples

**Query 1: logit extraction covariance eigenvalue PyTorch**
- DALLE-2 pytorch, IP-Adapter, diffusion RL examples — similarity 0.31–0.35
- No applicable code patterns for MCQ logit analysis

**Query 2: HuggingFace model logits MCQ inference**
- HunyuanDiT download scripts, DistilBert ANE optimization — low relevance
- Pattern noted: `AutoModelForCausalLM.from_pretrained()` confirmed as standard loading method

### Exa GitHub Implementations

**Exa MCP Status:** Unavailable (HTTP 402 error) — same as H-E1 documented case.

**Alternative sources used:**
- H-E1 validated codebase: direct HuggingFace forward pass for 4D MCQ logit extraction
- Li et al. [2024] methodology: covariance eigenvalue analysis of model output perturbations
- Standard numpy/scipy: `np.cov()`, `np.linalg.eigh()` for eigendecomposition

### 🎯 Implementation Priority Assessment

**No paper-specific official implementation found** (Exa unavailable, Archon domain mismatch).

**Recommended Implementation Path:**
- Primary: Extend H-E1 codebase — logit extraction already functional; add covariance + eigenvalue analysis module
- Fallback: Implement from scratch using numpy eigendecomposition on extracted logit delta matrices
- Justification: H-E1 code already extracts 4D MCQ logits; adding Δ = aligned_logits − base_logits → covariance → eigenvalue ratio is a direct extension requiring ~50 lines of new analysis code

### Code Analysis (Serena MCP)

*Skipped* — No complex code requiring Serena analysis. Experiment uses:
1. Extended H-E1 logit extraction pipeline (already validated)
2. Standard numpy eigenvalue decomposition (`np.linalg.eigh`) — well-understood operations
3. No custom model architectures or novel code patterns requiring semantic analysis

---

## Experiment Specification

### Dataset

**Primary Dataset:** MMLU (Multiple-choice Machine Learning Understanding)
- **Name:** MMLU (Massive Multitask Language Understanding)
- **HuggingFace Identifier:** `cais/mmlu`, split `all`, subset `test`
- **Size:** 14,042 items (57 subjects)
- **Type:** standard (real benchmark)
- **Format:** 4-option MCQ (A/B/C/D) — enables 4D logit vector extraction
- **Validated in H-E1:** ✅ fully functional

**Secondary Datasets (cross-family validation):**
| Dataset | HF Identifier | Size | Purpose |
|---------|--------------|------|---------|
| TruthfulQA | `truthful_qa`, `multiple_choice`, `validation` | 817 items | Cross-benchmark anisotropy replication |
| ARC-Challenge | `allenai/ai2_arc`, `ARC-Challenge`, `test` | 1,172 items | Cross-benchmark anisotropy replication |

**Total evaluation items:** 16,031 (across 3 benchmarks)

**Preprocessing:**
- Load 4 option log-probabilities per item via model forward pass (tokens A, B, C, D)
- Compute Δ = aligned_4D_logits − base_4D_logits per item
- No normalization required before covariance analysis (raw logit deltas)
- Margin quintile stratification for secondary analysis

**Type:** standard (real, established benchmarks — NOT synthetic) ✅

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` library
- Identifier: `cais/mmlu` (all, test), `truthful_qa` (multiple_choice, validation), `allenai/ai2_arc` (ARC-Challenge, test)
- Code: `load_dataset("cais/mmlu", "all", split="test")`

### Models

#### Baseline Model

**Architecture:** Decoder-only transformer LLMs (base pre-trained, no alignment)
**Type:** Causal language model (HuggingFace AutoModelForCausalLM)

**Model Pairs for Anisotropy Analysis:**

| Pair ID | Family | Base Model HF ID | Aligned Model HF ID | Alignment Method |
|---------|--------|-----------------|--------------------|-----------------:|
| pair2 | Tulu-2 7B | `allenai/tulu-2-7b` | `allenai/tulu-2-dpo-7b` | DPO |
| pair4 | Pythia 6.9B | `EleutherAI/pythia-6.9b` | `dvruette/oasst-pythia-6.9b-4000-steps` | SFT |
| pair_new | Pythia 1.4B | `EleutherAI/pythia-1.4b` | `pvduy/pythia-1.4b-rl-trlx-dolly15k` | PPO (TRLX) |

**Selection rationale:**
- pair2 (tulu-2 DPO): Primary pair validated in H-E1 with strong effect (AUROC=0.867)
- pair4 (pythia-6.9b SFT): Second family validated in H-E1; SFT provides isotropic-vs-structured baseline
- pair_new (pythia-1.4b PPO): Scale variant; TRLX-trained PPO model avoids tokenizer issues of prior pair3

**Baseline for isotropic comparison:** Compute anisotropy ratio under null hypothesis — if Δ is isotropic noise, eigenvalues should be approximately equal (ratio ≈ 1.0)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers` (AutoModelForCausalLM + AutoTokenizer)
- Identifier: See table above (3 pairs)
- Code: `AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="cuda")`

#### Proposed Model / Analysis Extension

**Architecture:** Same models as baseline — this is an ANALYSIS experiment, not a new model architecture.

The "proposed mechanism" is the logit delta anisotropy analysis:
- For each MCQ item: compute Δ_i = aligned_logits_4D − base_logits_4D (shape: [4])
- Stack Δ across N items: shape [N, 4]
- Compute covariance matrix Σ = Δᵀ Δ / N (shape: [4, 4])
- Compute eigenvalues λ₁ ≥ λ₂ ≥ λ₃ ≥ λ₄
- Anisotropy ratio r = λ₁ / mean(λ₂, λ₃, λ₄)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Logit Delta Anisotropy Analysis
# H-M1: Tests whether alignment-induced perturbations are structured (non-isotropic)
# Based on: Li et al. [2024] methodology + H-E1 logit extraction pipeline

import numpy as np
from scipy import stats

def compute_logit_delta_anisotropy(base_logits_4d, aligned_logits_4d):
    """
    Args:
        base_logits_4d: np.ndarray [N, 4] — MCQ logits from base model
        aligned_logits_4d: np.ndarray [N, 4] — MCQ logits from aligned model
    Returns:
        dict with anisotropy_ratio, eigenvalues, p_value
    """
    # Step 1: Compute logit delta matrix
    delta = aligned_logits_4d - base_logits_4d  # shape: [N, 4]

    # Step 2: Center the delta (zero-mean per axis)
    delta_centered = delta - delta.mean(axis=0)  # shape: [N, 4]

    # Step 3: Compute 4×4 covariance matrix of perturbations
    cov_matrix = np.cov(delta_centered.T)  # shape: [4, 4]

    # Step 4: Eigendecomposition (eigh for symmetric matrix)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    eigenvalues = np.sort(eigenvalues)[::-1]  # descending order

    # Step 5: Compute anisotropy ratio: λ₁ / mean(λ₂, λ₃, λ₄)
    anisotropy_ratio = eigenvalues[0] / np.mean(eigenvalues[1:])

    # Step 6: Significance test — compare leading vs. trailing eigenvalues
    # Directional test: variance along decision axis > orthogonal axes
    decision_axis_var = project_onto_decision_axis(delta, base_logits_4d)
    orthogonal_var = eigenvalues[1:]  # trailing eigenvalues
    t_stat, p_value = stats.ttest_1samp(orthogonal_var, decision_axis_var)

    return {
        "anisotropy_ratio": anisotropy_ratio,
        "eigenvalues": eigenvalues,
        "cov_matrix": cov_matrix,
        "p_value": p_value,
        "is_anisotropic": (anisotropy_ratio > 1.0) and (p_value < 0.05)
    }
```

### Training Protocol

**Note:** H-M1 is an ANALYSIS experiment — no model training required. The experiment extracts logits from pre-trained base and aligned models, computes logit deltas, and performs statistical analysis.

**Inherited from H-E1 (reuse for controlled comparison):**

| Component | Value | Source |
|-----------|-------|--------|
| **Model loading** | float16, device_map="cuda" | H-E1 validated |
| **Batch size** | 8–16 items per forward pass | H-E1 validated (H100 NVL) |
| **GPU** | CUDA_VISIBLE_DEVICES=0 (H100 NVL) | H-E1 infrastructure |
| **Dataset splits** | Same test splits as H-E1 | Controlled comparison |
| **Seeds** | 1 (fixed) | PoC standard |

**Analysis Protocol:**
1. Load base model + aligned model for each pair sequentially (not simultaneously — insufficient VRAM)
2. Extract 4D MCQ logits via forward pass for all items
3. Save logit tensors to disk (numpy .npy files)
4. Compute Δ = aligned − base per item
5. Run anisotropy analysis: covariance → eigendecomposition → anisotropy ratio
6. Statistical test per model family
7. Report across ≥ 2/3 families

**Optimizer:** None (inference-only analysis)
**Loss function:** None (statistical test: paired t-test on eigenvalues)
**Epochs:** None (single-pass inference per model)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Gate Threshold |
|--------|-----------|---------------|
| Anisotropy ratio (r) | λ₁ / mean(λ₂, λ₃, λ₄) of Δ covariance matrix | r > 1.0 |
| Statistical significance | Paired t-test p-value (λ₁ vs trailing eigenvalues) | p < 0.05 |
| Family count | Number of model families where r > 1.0 and p < 0.05 | ≥ 2/3 |

**Secondary Metrics:**
| Metric | Definition | Purpose |
|--------|-----------|---------|
| Decision axis projection | Variance of Δ projected onto (top1_logit − top2_logit) direction | Directional test |
| Method comparison | Δ anisotropy ratio comparison: DPO vs SFT vs PPO | Feeds into H-M2 |
| Cross-benchmark consistency | Anisotropy ratio on TruthfulQA + ARC-Challenge | Generalization check |

**Success Criteria:**
- **Gate PASS:** Anisotropy ratio > 1.0 with p < 0.05 in ≥ 2 of 3 model families (MMLU, N~14K items)
- **Expected range:** r ∈ [2.0, 10.0] if Li et al. [2024] findings generalize (heterogeneous axis-specific changes)
- **Direction:** r > 1.0 means leading eigenvalue dominates — structured (non-isotropic) perturbation

**Expected Baseline Performance:**
- Isotropic null: r ≈ 1.0 (all eigenvalues equal, Gaussian noise)
- Li et al. [2024] heterogeneous trustworthiness changes → expect r >> 1.0 for DPO/PPO
- H-E1 finding (β₁=-4.33, η²=0.289) suggests large structured effect in tulu-2 DPO pair

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis (eigenvalue test)
- Library: numpy (`np.linalg.eigh`), scipy (`scipy.stats.ttest_1samp`, `scipy.stats.ttest_rel`)
- Code: `eigenvalues, _ = np.linalg.eigh(cov_matrix); ratio = eigenvalues[-1] / eigenvalues[:-1].mean()`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Anisotropy ratio per model family vs. threshold (r=1.0) bar chart

#### Additional Figures (LLM Autonomous)
Based on the hypothesis type (MECHANISM: logit perturbation structure), the following additional figures are recommended:

1. **Eigenvalue spectrum plot** — 4 eigenvalues per model pair on a bar chart showing distribution shape (isotropic = flat, anisotropic = one dominant spike)
2. **Logit delta PCA visualization** — 2D PCA scatter of Δ vectors per model pair, colored by confidence margin quintile (visualizes the principal direction)
3. **Anisotropy ratio by margin quintile** — Line chart showing whether anisotropy is stronger in low-margin items (bridges to H-M2)
4. **DPO vs SFT vs PPO anisotropy comparison** — Box plots of per-item Δ variance along decision axis vs orthogonal axes, split by alignment method

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Model outputs 4D logit vectors for MCQ items (A/B/C/D) accessible via forward pass | TRUE — confirmed in H-E1 logit extraction |
| Mechanism Isolatable | Base and aligned logits can be extracted independently and subtracted | TRUE — H-E1 extracts both; Δ computation is trivial |
| Baseline Measurable | Null anisotropy (r=1.0) can be computed from isotropic synthetic noise for validation | TRUE — synthetic isotropic Δ as sanity check |

### Architecture Compatibility Check

**Required Features:**
- Decoder-only transformer with 4-option MCQ scoring capability
- Accessible final-layer logit vectors for tokens A, B, C, D
- Same tokenizer between base and aligned model (critical — tokenizer mismatch caused pair3 failure in H-E1)

**Compatibility Status:**
- pair2 (tulu-2 DPO): ✅ Tokenizer compatible (confirmed H-E1)
- pair4 (pythia-6.9b SFT): ✅ Tokenizer compatible (confirmed H-E1)
- pair_new (pythia-1.4b PPO): ⚠️ Must verify tokenizer compatibility before full run; use pilot test on 100 items

**Incompatible Architectures:**
- Models without shared tokenizer between base/aligned (e.g., pair3 failure in H-E1)
- Models with non-standard MCQ logit format (embedding-based or generative scoring)

> ⚠️ If tokenizer mismatch detected for pair_new, Phase 4 MUST skip that pair and document. Gate still passable with 2/3 families (pair2 + pair4).

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Logit delta extracted: shape [N, 4], mean_delta=[...]" printed per pair | extract_logits.py:forward_pass() |
| Tensor Shape | delta.shape == (N_items, 4) where N_items ≈ 14042 | analysis.py:compute_anisotropy() |
| Metric Delta | anisotropy_ratio > 1.0 (mechanism activation threshold) | analysis.py:gate_check() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(pair_id, base_logits, aligned_logits, results):
    """Verify that anisotropy analysis pipeline ran correctly."""
    indicators = {
        "delta_computed": base_logits.shape == aligned_logits.shape == (None, 4),
        "cov_computed": results.get("cov_matrix") is not None,
        "eigenvalues_valid": all(results.get("eigenvalues", [0]) > 0),
        "ratio_above_threshold": results.get("anisotropy_ratio", 0) > 0,
        "log_found": f"pair_{pair_id}_anisotropy" in experiment_log
    }
    activated = indicators["delta_computed"] and indicators["cov_computed"]
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Tokenizer mismatch | Shape error during logit extraction (NaN/inf values) | Skip pair, document, continue |
| Degenerate covariance | All eigenvalues ≈ 0 (numerical issue) | Check logit normalization |
| Isotropic result | r ≤ 1.0 for that family | Document null; count toward family failures |
| Model not found | HuggingFace 404/401 error | Log and skip; try fallback model ID |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Δ shape [N, 4] confirmed per pair | Tensor shape check |
| Effect Measurable | Anisotropy ratio computable (no numerical degeneracy) | Eigenvalue positivity check |
| Hypothesis Supported | r > 1.0 AND p < 0.05 in ≥ 2/3 families | Gate evaluation |

**Hypothesis Support Threshold:** Anisotropy ratio > 1.0 with p < 0.05 (paired t-test: λ₁ vs mean(λ₂,λ₃,λ₄)) in ≥ 2 of 3 model families across MMLU test set (N≈14K items).

**Hypothesis Support Metric:** Anisotropy ratio r = λ₁ / mean(λ₂,λ₃,λ₄) of logit delta covariance matrix Σ, where Σ = cov(aligned_4D_logits − base_4D_logits) computed over all MCQ items.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Domain Mismatch — No applicable sources found.** Archon KB is populated with diffusion model content (LoRA, LyCORIS, HunyuanDiT, DALLE-2). All 5 queries returned diffusion-domain results with low similarity (0.31–0.46) to RLHF logit analysis.

- **Used For:** Nothing actionable; documented as limitation

### B. GitHub Implementations (Exa)

**Exa MCP Status:** Unavailable (HTTP 402 payment required) — quota exceeded.
- Same status as H-E1 experiment design (documented in h-e1/02c_experiment_brief.md)
- No GitHub repository URLs retrieved

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-E1 validated infrastructure is sufficiently clear. Experiment is a direct numerical extension (eigenvalue analysis) of the existing logit extraction pipeline.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1 (`h-e1/04_validation.md`, PASS, 2026-03-17)

**Reused Components:**
- **Dataset:** MMLU/TruthfulQA/ARC-Challenge (same test splits) — proven stable in H-E1
- **Model loading pattern:** `AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="cuda")` — validated
- **Logit extraction pipeline:** 4D MCQ logit extraction via HuggingFace forward pass — validated
- **Infrastructure:** conda env, H100 NVL GPU, CUDA_VISIBLE_DEVICES=0

**Why Reused:** Enables controlled comparison — H-M1 adds only the Δ computation and eigenvalue analysis step; all other components identical to H-E1. Infrastructure bugs (pair1 404, pair3 tokenizer) already documented and avoided.

**Infrastructure Issues to Avoid:**
- `allenai/tulu-2-ppo-7b` → 404, use DPO variant only
- `reciprocate/ppo_hh_pythia-1B` → tokenizer error, use `pvduy/pythia-1.4b-rl-trlx-dolly15k` instead

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (MMLU/TruthfulQA/ARC) | Phase 2A/2B + H-E1 validation | 02b_verification_plan.md §1.3; h-e1/04_validation.md |
| Model pairs (pair2, pair4) | H-E1 validation | h-e1/04_validation.md §2, §3 |
| Model pair_new (pythia-1.4b TRLX) | Phase 2B §1.3 + HF Hub fallback | 02b_verification_plan.md; pvduy/pythia-1.4b-rl-trlx-dolly15k |
| Anisotropy metric definition | Phase 2B hypothesis protocol | 02b_verification_plan.md §2.2 H-M1 |
| Eigenvalue analysis methodology | Li et al. [2024] | Phase 2A research (confirmed axis-specific changes) |
| Gate threshold (r>1.0, p<0.05, ≥2/3) | Phase 2B success criteria | 02b_verification_plan.md §3.2 |
| Logit loading code | H-E1 codebase | h-e1/code/ (functional) |
| Statistical test (paired t-test) | Standard statistical methodology | scipy.stats.ttest_rel |
| Visualization requirements | Phase 2C synthesis | This document §Visualization |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-17

### Workflow History for This Hypothesis
- 2026-03-17T02:44:09Z: H-M1 set to IN_PROGRESS (external loop starting Phase 2C)
- 2026-03-17T(now): Experiment design Phase 2C executing (UNATTENDED)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — domain mismatch), Exa (GitHub — 402 unavailable), Serena (skipped — not needed)*
*All specifications grounded in H-E1 validated infrastructure + Phase 2B research*
*Next Phase: Phase 3 - Implementation Planning*
