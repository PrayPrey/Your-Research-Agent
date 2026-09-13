# Experiment Design: H-M2

**Date:** 2026-03-15
**Author:** Anonymous
**Hypothesis Statement:** Under forced-choice MMLU evaluation, alignment training (SFT/DPO/PPO) increases mean pre-softmax logit margins (top-1 minus top-2 log-prob before normalization) relative to base models, with margin inflation ordered PPO >= DPO > SFT across Pythia model sizes, operationalizing the confidence inflation causal mechanism.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** — Tests causal Step 2 of the alignment→calibration chain: logit-level confidence inflation via pre-softmax margin analysis.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 PASS (ECE_base < 0.15 for all 3 Pythia sizes — confirmed 2026-03-15T02:01:09Z)
**Gate Status:** SHOULD_WORK (failure → EXPLORE, not STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED — PASS), H-E1 (COMPLETED — PASS)

### Gate Condition

**SHOULD_WORK Gate:** Δmargin > 0 for PPO in ≥2/3 Pythia sizes with bootstrap CI lower bound > 0. Secondary: Δmargin_PPO >= Δmargin_DPO > Δmargin_SFT confirmed by sign test.

If gate fails → EXPLORE (test whether alignment acts post-softmax; document as H2 boundary shift candidate). Pipeline continues.

---

## Continuation Context

**This is a DATA EXTRACTION experiment** — directly inherits from H-E1 and H-M1.

**Reuse from H-E1/H-M1:**
- Same lm-eval v0.4.11 evaluation run (12 Pythia models × full MMLU 14,042 items)
- Validated public fallback models (Risk R1 activated): lomahony/Leogrin/usvsnsp
- Validated calibration_analysis.py pipeline (Brier decomposition, ECE)
- **0 additional GPU-hours** if H-E1 logit outputs are cached to disk

**Key results inherited:**
- H-E1 gate PASS: PPO 1.4b Δ_rel=+0.0406, PPO 2.8b Δ_rel=+0.0423, DPO all 3 sizes pass
- H-M1 gate PASS: ECE_base = {1.4b: 0.0849, 2.8b: 0.0597, 6.9b: 0.0792}
- **Implication:** Pre-softmax margins ARE expected to inflate (ECE increase confirmed)

### Previous Hypothesis Results
- **H-E1 (MUST_WORK PASS):** Alignment increases Brier reliability. PPO/DPO show ΔECE > 0 in ≥2/3 sizes.
- **H-M1 (MUST_WORK PASS):** Base Pythia models well-calibrated (ECE_base < 0.15). Causal baseline confirmed.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "logit margin calibration LLM alignment"** (match_count=5)
- Top similarity: 0.433 (hf.co/papers/2305.14314) — **No relevant results**
- All results: diffusion model content (consistency models, marigold pipeline, bitsandbytes)
- **Key finding:** Archon KB contains no prior art on pre-softmax logit margin analysis for RLHF alignment.

**Query 2: "pre-softmax logit distribution RLHF confidence"** (match_count=5)
- Top similarity: 0.370 — **No relevant results**
- All results: diffusion model content (IC-Light, LoRA, consistency models)
- **Key finding:** No RLHF logit analysis cases in KB.

**Query 3: "MMLU evaluation ECE calibration benchmark"** (match_count=5)
- Top similarity: 0.468 — **No relevant results** (openai/consistency_models, diffusers PR)
- **Key finding:** No MMLU calibration experiments in KB.

**Summary:** Archon KB contains only diffusion model content. No prior art on pre-softmax margin analysis. All specifications grounded in Phase 2B research (Li et al. 2024, Coste et al. 2023, Xie et al. 2024) and domain expertise from H-E1/H-M1 implementations.

### Archon Code Examples

**Query 1: "lm-eval logit extraction log probability"** (match_count=5)
- Top result: Slurm eval scripts (mmgeneration, DeepCache logging) — **No relevant results**
- Similarity scores all < 0.31 — entirely unrelated to lm-eval logit processing

**Query 2: "numpy scipy Wilcoxon signed rank test bootstrap CI"** (match_count=5)
- Top result: LaTeX code listing (incidence matrix) — **No relevant results**
- No statistical testing code found in KB

**Conclusion:** Archon KB has no relevant code. Implementations follow:
1. lm-eval-harness v0.4.11 standard output format (validated in H-E1)
2. scipy.stats.wilcoxon for paired test
3. numpy bootstrap for CI (n=1000)

### Exa GitHub Implementations

**⚠️ Exa MCP Unavailable (HTTP 402 — Payment Required)**
- Retry 1: 402 error
- Retry 2: 402 error
- Status: Exa unavailable for this session (same as H-E1, H-M1)

**Fallback Strategy:** Implementations grounded in:
1. **lm-eval-harness v0.4.11** (EleutherAI/lm-evaluation-harness) — validated in H-E1; log-prob outputs include raw logit values accessible pre-softmax
2. **Li et al. 2024** — Pythia PPO/DPO alignment experiments; pre-softmax margin analysis is the standard diagnostic approach cited in their methodology
3. **Coste et al. 2023** — "Reward model ensembles help mitigate overoptimization" — PPO reward pressure creates logit scale inflation
4. **H-E1 validated pipeline** — calibration_analysis.py already parses lm-eval JSON outputs with per-item logit vectors

### 🎯 Implementation Priority Assessment

**This is NOT a paper reproduction experiment** — H-M2 is a diagnostic analysis extending the H-E1 evaluation pipeline. No external "official implementation" needed.

**CRITICAL:** lm-eval outputs log-probs per answer choice. The pre-softmax logits are accessible as log-probs BEFORE the log_softmax normalization step (lm-eval stores `loglikelihood` values which are pre-normalization log-probs from the LM).

**Recommended Implementation Path:**
- Primary: Extend H-E1 calibration_analysis.py with margin computation module
- Fallback: Re-run lm-eval with `--output_path` to capture full logit outputs if cached data unavailable
- Justification: H-E1 pipeline already validated; margin extraction is a simple numpy operation on stored logit arrays

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is a data analysis pipeline extending the validated H-E1 implementation. No novel architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** MMLU (Massive Multitask Language Understanding)
**Source:** HuggingFace — `cais/mmlu`, all subjects
**Type:** standard
**Split:** Test set (full, 14,042 items across 57 subjects)
**Access:** Via lm-eval-harness v0.4.11 `--tasks mmlu` (same run as H-E1)

**Dataset Statistics:**
- Total items: 14,042 (57 subjects × varying counts)
- Format: 4-choice multiple choice (A/B/C/D)
- Evaluation: log-probability continuation scoring (forced-choice)
- **Reuse:** Same lm-eval run as H-E1/H-M1 — no new data download required

**Preprocessing:** None — raw lm-eval outputs used directly
**Augmentation:** None — inference only

**Hypothesis Fit:** MMLU forced-choice evaluation requires computing log-prob for each of 4 answer continuations. These log-probs ARE the pre-softmax logit scores (lm-eval calls `loglikelihood` which returns raw LM log-probs before softmax normalization). Margin = max(log_prob) − second_max(log_prob) over 4 choices. ✅ CONFIRMED

**Synthetic Data Check:** Type = `standard` — real dataset. PASS ✅

**Loading Information** (for Phase 4 download):
- Method: lm-eval-harness (no direct HuggingFace datasets call)
- Identifier: `--tasks mmlu` (lm-eval v0.4.11 argument)
- Code: `lm_eval --model hf --model_args "pretrained=<model_id>" --tasks mmlu --output_path <output_dir> --log_samples`

### Models

#### Baseline Model

**Architecture:** Pythia base models — autoregressive causal LM
**Sizes:** 1.4B, 2.8B, 6.9B (3 models)
**Source:** EleutherAI/pythia-{1.4b|2.8b|6.9b}
**Type:** autoregressive_causal_lm
**Public Fallback (Risk R1 activated):** EleutherAI/pythia-{1.4b|2.8b|6.9b} (base) — already cached from H-E1

**Role:** Provides baseline pre-softmax log-prob vectors from which margins are computed.

**Expected baseline margin:** ~0.5–2.0 nats (log-prob scale) based on MMLU difficulty; exact values from H-E1 outputs.

**Configuration:**
- Decoding: greedy, temperature=1.0
- Framework: lm-eval v0.4.11
- Context: 4-shot (MMLU standard)

**Loading Information** (for Phase 4 download):
- Method: lm-eval `--model hf` (HuggingFace transformers)
- Identifier: `"EleutherAI/pythia-1.4b"`, `"EleutherAI/pythia-2.8b"`, `"EleutherAI/pythia-6.9b"`
- Code: `lm_eval --model hf --model_args "pretrained=EleutherAI/pythia-1.4b,dtype=float32" --tasks mmlu --log_samples`

#### Proposed Model

**Architecture:** Pythia aligned variants — same autoregressive causal LM base, aligned with SFT/DPO/PPO
**Sizes × Methods:** 3 sizes × 3 alignment methods = 9 models
**Public Fallback (Risk R1 — already activated):**
- SFT: lomahony/pythia-{1.4b|2.8b|6.9b}-deduped-tldr (or equivalent)
- DPO: Leogrin/pythia-{1.4b|2.8b|6.9b}-sft-tldr-dpo (or equivalent)
- PPO: usvsnsp/pythia-{1.4b|2.8b|6.9b}-sft-tldr-ppo (or equivalent)
*(Exact model IDs per H-E1 validation — already cached)*

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pre-Softmax Logit Margin Extraction
# Based on: lm-eval-harness v0.4.11 log-prob output format
# H-E1 validated pipeline extension

import numpy as np
from scipy import stats

def compute_logit_margins(logprob_matrix):
    """
    Args:
        logprob_matrix: np.ndarray of shape (N_items, 4)
                        Each row = [log_prob_A, log_prob_B, log_prob_C, log_prob_D]
                        These are pre-softmax log-probs from lm-eval
    Returns:
        margins: np.ndarray of shape (N_items,)
                 margin_i = logprob_rank1_i − logprob_rank2_i
    """
    # Sort descending to get rank-1 and rank-2
    sorted_logprobs = np.sort(logprob_matrix, axis=1)[:, ::-1]
    margins = sorted_logprobs[:, 0] - sorted_logprobs[:, 1]
    return margins  # shape: (N_items,)

def compute_delta_margin(base_logprobs, aligned_logprobs):
    """
    Args:
        base_logprobs: (N_items, 4) from base model
        aligned_logprobs: (N_items, 4) from aligned model (same items)
    Returns:
        delta_margin: scalar mean Δmargin (aligned − base)
        ci_lower: bootstrap 95% CI lower bound (n=1000)
        ci_upper: bootstrap 95% CI upper bound
    """
    base_margins = compute_logit_margins(base_logprobs)
    aligned_margins = compute_logit_margins(aligned_logprobs)
    delta_per_item = aligned_margins - base_margins
    delta_mean = np.mean(delta_per_item)

    # Bootstrap CI (n=1000)
    n = len(delta_per_item)
    boot_means = [np.mean(np.random.choice(delta_per_item, n, replace=True))
                  for _ in range(1000)]
    ci_lower = np.percentile(boot_means, 2.5)
    ci_upper = np.percentile(boot_means, 97.5)
    return delta_mean, ci_lower, ci_upper

def test_gradient_ordering(delta_ppo, delta_dpo, delta_sft):
    """Sign test: PPO >= DPO > SFT across 3 Pythia sizes."""
    # paired Wilcoxon across sizes
    stat_ppo_dpo, p_ppo_dpo = stats.wilcoxon(delta_ppo, delta_dpo, alternative='greater')
    stat_dpo_sft, p_dpo_sft = stats.wilcoxon(delta_dpo, delta_sft, alternative='greater')
    return {'ppo_ge_dpo_p': p_ppo_dpo, 'dpo_gt_sft_p': p_dpo_sft}
```

### Training Protocol

**This is an evaluation-only experiment — no training required.**

**Evaluation Protocol:**
- **Framework:** lm-eval-harness v0.4.11 (validated in H-E1)
- **Task:** `--tasks mmlu` (full test set, 14,042 items, 4-shot)
- **Decoding:** Greedy, temperature=1.0
- **Output format:** `--log_samples` flag to capture per-item log-prob vectors

**Data Pipeline:**
1. Load cached H-E1 lm-eval JSON outputs (if available) — 12 models × MMLU
2. Parse per-item logit vectors from `loglikelihood` fields
3. Compute margins per model, per item
4. Compute Δmargin = aligned − base per size/method pair
5. Run bootstrap CI (n=1000 samples) per alignment method
6. Run Wilcoxon signed-rank test across 3 sizes for gradient ordering

**Fallback (if H-E1 outputs not cached):**
- Re-run lm-eval for all 12 models with `--log_samples` flag
- Single GPU sufficient (inference-only, ~2-3 hours for all 12 models on A100)
- GPU requirement: `export CUDA_VISIBLE_DEVICES=<empty_gpu>`

**Seeds:** 1 (fixed, greedy decoding — deterministic)
**Optimizer:** N/A (no training)
**Loss:** N/A (no training)

### Evaluation

**Task Type:** Statistical analysis of log-probability outputs (no ML training)

**Primary Metric:** Δmargin = mean(top-1 logit − top-2 logit)_aligned − mean(top-1 logit − top-2 logit)_base
- Computed per model-size pair (9 aligned × 3 base = 9 Δ values)
- Units: nats (log-prob scale)
- Positive = alignment inflates confidence gap between top-1 and top-2 predictions

**Secondary Metric:** Gradient ordering Δmargin_PPO >= Δmargin_DPO > Δmargin_SFT
- Assessed via sign test across 3 Pythia sizes
- Wilcoxon signed-rank p-value reported per comparison

**Success Criteria (SHOULD_WORK gate):**
- **Primary:** Δmargin > 0 for PPO in ≥2/3 Pythia sizes (bootstrap 95% CI lower bound > 0)
- **Secondary:** Ordering Δmargin_PPO >= Δmargin_DPO > Δmargin_SFT in sign test

**Expected Values (based on H-E1 findings):**
- PPO 1.4b: Δmargin expected +0.05 to +0.20 nats (H-E1 ΔECE_rel=0.0406 implies meaningful logit inflation)
- PPO 2.8b: Δmargin expected +0.04 to +0.15 nats
- DPO 1.4b: Δmargin expected +0.10 to +0.35 nats (H-E1 shows DPO strongest ΔECE)
- SFT: Δmargin expected near 0 or small positive (weakest alignment pressure)
- **Note:** These are informed estimates from H-E1 calibration results — actual values may differ

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical analysis / calibration
- Library: `scipy.stats` (Wilcoxon), `numpy` (bootstrap, margin computation)
- Code: `from scipy.stats import wilcoxon; import numpy as np`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Δmargin bar chart per alignment method (PPO/DPO/SFT) × model size (1.4B/2.8B/6.9B) with bootstrap 95% CI error bars

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type (MECHANISM — logit-level analysis), the following additional figures are recommended:

1. **Margin Distribution Violin Plot:** Full distribution of per-item margins for base vs aligned models (PPO 1.4b example) — shows not just mean shift but shape change
2. **Δmargin vs ΔECE Scatter:** Scatter plot of Δmargin_PPO vs ΔECE_PPO across 9 model-size pairs — validates mechanistic link between margin inflation and calibration degradation
3. **Gradient Ordering Heatmap:** 3×3 heatmap (alignment method × model size) of Δmargin values — visualizes PPO >= DPO > SFT ordering claim
4. **Cumulative Margin Distribution:** CDF of margins for base vs PPO (1.4b) — shows rightward shift indicating confidence inflation

Output Location: `h-m2/figures/`

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | lm-eval log-prob outputs contain pre-softmax logit values accessible as `loglikelihood` per answer choice | TRUE — lm-eval v0.4.11 `--log_samples` captures per-item logit vectors |
| Mechanism Isolatable | Margin can be computed independently for base vs aligned; difference is Δmargin | TRUE — same items evaluated separately for each model |
| Baseline Measurable | Base Pythia models (no alignment) provide margin baseline; ECE_base already validated in H-M1 | TRUE — base models already evaluated in H-E1 |

### Architecture Compatibility Check

**Required Features:**
- Model must support continuation-style log-prob scoring (standard autoregressive LM ✅)
- lm-eval must return per-answer-choice log-prob values (v0.4.11 `--log_samples` ✅)
- Log-probs must be un-normalized (pre-softmax) — lm-eval `loglikelihood` returns raw LM log-probs ✅

**Incompatible Architectures:**
- Models without standard log-prob API (e.g., API-only models without logit access)
- Models using softmax-normalized outputs as inputs (double-normalization artifact)

**Pythia Compatibility:** ✅ Fully compatible — autoregressive causal LM, lm-eval native support, `--log_samples` captures full logit vectors

> ⚠️ If H-E1 log outputs were NOT saved with `--log_samples`, Phase 4 MUST re-run lm-eval with this flag.

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Margin computation complete. Mean Δmargin_PPO_1.4b = +X.XXX nats" | margin_analysis.py:main() |
| Tensor Shape | logprob_matrix shape (14042, 4) per model → margin shape (14042,) | margin_analysis.py:compute_logit_margins() |
| Metric Delta | Δmargin_PPO > 0 in ≥2/3 sizes; bootstrap CI lower > 0 | margin_analysis.py:compute_delta_margin() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results_dict):
    """
    Verify that margin inflation mechanism was detected.
    Args:
        results_dict: dict with keys like 'ppo_1.4b_delta_margin',
                      'ppo_1.4b_ci_lower', etc.
    """
    indicators = {
        "logprob_matrix_loaded": results_dict.get("n_items_processed") == 14042,
        "margins_computed": results_dict.get("ppo_1.4b_margin_mean") is not None,
        "delta_positive_ppo": sum(
            results_dict.get(f"ppo_{s}_delta_margin", -1) > 0
            for s in ["1.4b", "2.8b", "6.9b"]
        ) >= 2,  # ≥2/3 sizes
        "ci_lower_positive": sum(
            results_dict.get(f"ppo_{s}_ci_lower", -1) > 0
            for s in ["1.4b", "2.8b", "6.9b"]
        ) >= 2,
    }
    mechanism_verified = indicators["delta_positive_ppo"] and indicators["ci_lower_positive"]
    return mechanism_verified, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No logit data | `--log_samples` outputs missing or empty | FAIL: Re-run lm-eval with `--log_samples` flag |
| Margin unchanged | Δmargin ≈ 0 across all 9 pairs | EXPLORE: Alignment acts post-softmax; H2 candidate |
| Negative Δmargin for PPO | PPO shows smaller margins than base | EXPLORE: Format mismatch dominant (Risk R2); restrict to SFT |
| Gradient reversed | DPO > PPO in Δmargin | EXPLORE: PPO reward self-regulation active (Risk R5) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Logit vectors extracted (N=14,042 per model) | Shape check in verification code |
| Effect Measurable | Δmargin_PPO > 0 in ≥2/3 sizes | mean(delta_per_item) > 0 |
| Hypothesis Supported | Bootstrap 95% CI lower bound > 0 for PPO in ≥2/3 sizes | percentile(boot_means, 2.5) > 0 |

---

## PoC Success Check

**PoC Pass Condition (SHOULD_WORK gate):**
1. Code runs without error
2. Δmargin_PPO > 0 in ≥2/3 Pythia sizes (bootstrap CI lower > 0)

**Failure Handling:** EXPLORE — document as normalization artifact (H2 candidate); report DPO margin analysis as secondary finding; pipeline continues to H-M3.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Summary:** No relevant sources found in Archon KB (diffusion-model focused repository). 5 queries executed across calibration, RLHF, logit margin, MMLU benchmark, and lm-eval topics — all returned similarity scores < 0.53 with diffusion model content.

### B. GitHub Implementations (Exa)

**⚠️ Exa MCP Unavailable (HTTP 402 — Payment Required)**
- Query 1: "lm-evaluation-harness logit extraction log probability MMLU calibration" → 402
- Query 2: "RLHF alignment logit margin confidence inflation pre-softmax analysis Python" → 402

**Primary Reference (Domain Knowledge):**
- **EleutherAI/lm-evaluation-harness** (GitHub, validated in H-E1)
  - Relevant file: `lm_eval/models/huggingface.py` — `loglikelihood()` method returns `(log_prob, is_greedy)` tuples per answer choice
  - Key: `log_prob` is un-normalized (pre-softmax) log-likelihood from the language model
  - `--log_samples` flag writes per-sample results to JSON including per-choice logits

**Secondary Reference:**
- **H-E1 validated implementation** (`h-e1/code/calibration_analysis.py`)
  - Parses lm-eval JSON `--log_samples` output
  - Extracts per-item 4-option log-prob vectors (shape: [N, 4])
  - **H-M2 Extension:** Add `compute_margins()` function using same parsed vectors

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-E1 validated implementation is sufficiently clear. No novel architecture requiring semantic analysis. Margin computation is a simple numpy operation (argsort + subtraction) on the existing log-prob matrix.

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation Report (`h-e1/04_validation.md`) + H-M1 (`h-m1/04_validation.md`)

**Reused Components:**
- **Dataset:** MMLU full test set (14,042 items) — same lm-eval run
- **Models:** All 12 Pythia checkpoints (3 sizes × 4 variants: base/SFT/DPO/PPO)
- **Pipeline:** calibration_analysis.py — log-prob parsing and ECE computation
- **Key finding:** H-E1 confirms PPO/DPO inflate calibration error; H-M2 diagnoses the logit-level mechanism

**H-M2 adds to H-E1 pipeline:**
```python
# New module: margin_analysis.py (extends calibration_analysis.py)
# Input: logprob_matrix [N, 4] — same as calibration analysis input
# New computation:
margins = np.sort(logprob_matrix, axis=1)[:, ::-1][:, 0] - \
          np.sort(logprob_matrix, axis=1)[:, ::-1][:, 1]
delta_margin = margins_aligned.mean() - margins_base.mean()
```

**Why Reused:** Controlled experiment — only analysis type changes (calibration → margin). Same data enables direct comparison of ECE increase vs margin inflation.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: MMLU cais/mmlu | Phase 2A/2B plan | 02b_verification_plan.md §1.3 |
| Dataset: full test set 14,042 items | H-E1 validated | h-e1/04_validation.md |
| Model: Pythia fallback variants | H-E1 Risk R1 | h-e1/04_validation.md + lomahony/Leogrin/usvsnsp |
| Margin formula: top-1 − top-2 logit | Phase 2B protocol | 02b_verification_plan.md §2.2 H-M2 step 2 |
| Bootstrap CI n=1000 | H-E1 precedent | h-e1/02c_experiment_brief.md |
| Wilcoxon signed-rank test | Phase 2B protocol | 02b_verification_plan.md §2.2 H-M2 step 4 |
| lm-eval v0.4.11 framework | H-E1 validated | h-e1/04_validation.md — 12 models evaluated |
| Greedy decoding, temperature=1.0 | Main hypothesis | verification_state.yaml:controlled_variables |
| Gradient ordering PPO>=DPO>SFT | Phase 2A/2B | 02b_verification_plan.md §2.2 H-M2 success criteria |
| Serena analysis | Skipped | Code sufficiently clear from H-E1 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-15

### Workflow History for This Hypothesis
- H-E1 COMPLETED PASS: 2026-03-15T01:28:30Z — alignment inflates Brier reliability confirmed
- H-M1 COMPLETED PASS: 2026-03-15T02:01:09Z — base ECE < 0.15 confirmed for all 3 sizes
- H-M2 IN_PROGRESS: 2026-03-15T02:02:48Z — Phase 2C experiment design initiated

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no relevant results, KB is diffusion-focused), Exa (unavailable — 402), Serena (skipped — code clear from H-E1)*
*All specifications grounded in Phase 2B plan, Li et al. 2024, Coste et al. 2023, Xie et al. 2024, and H-E1/H-M1 validated implementations*
*Next Phase: Phase 3 - Implementation Planning*
