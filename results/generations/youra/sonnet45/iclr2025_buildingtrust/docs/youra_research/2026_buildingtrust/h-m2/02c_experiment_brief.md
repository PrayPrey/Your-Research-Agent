# Experiment Design: H-M2

**Date:** 2026-03-17
**Author:** Anonymous
**Hypothesis Statement:** Under RLHF alignment (PPO vs DPO), DPO produces significantly higher logit delta variance in low-margin regions (bottom quintile) compared to PPO, even after KL divergence control, because DPO's log-odds objective (L_DPO ∝ log σ(β·log ratio)) directly amplifies option-probability differences while PPO's KL penalty globally constrains distributional drift (Xu et al. [2024]).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Tests method-specific variance structure in low-margin regions.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 (MUST_WORK, PASS) — logit deltas confirmed non-isotropic (ratio 2.9–4.6)
**Gate Status:** SHOULD_WORK (continue with warning if failed)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
SHOULD_WORK: DPO variance > PPO variance in Q1 (bottom margin quintile), p < 0.05, KL-controlled.
Failure response: EXPLORE — document as null result for method-specific variance; scope narrows to
P(flip|margin) without method distinction. Does NOT stop pipeline.

---

## Continuation Context

**Previous Hypothesis:** H-M1 (COMPLETED)
**Key Results from H-M1:**
- pair2 (tulu-2-7b DPO): anisotropy ratio 2.8996, p=0.0028 ✅
- pair4 (pythia-6.9b SFT): anisotropy ratio 4.5789, p=0.0047 ✅
- H-E1 cache available at h-e1/cache/ (pair2, pair4 × 3 datasets × base+aligned)
- Broken pairs: pair1 (tulu-2-ppo-7b, 404), pair3 (reciprocate/ppo_hh_pythia-1B, tokenizer error)

### Previous Hypothesis Results (if applicable)
H-M1 proven: Alignment-induced logit deltas are strongly non-isotropic (ratio 2.9–4.6x).
The dominant eigenvalue direction (PC1) captures 2.9–4.6× more variance than remaining axes.
H-M2 builds on this: now tests whether this non-isotropy concentrates specifically in LOW-MARGIN
items AND whether this concentration is method-specific (DPO > PPO/SFT).

**Reused components from H-M1:**
- `compute_logit_delta` from h-m1/code/analysis_anisotropy.py
- H-E1 cache (h-e1/cache/) — no redundant model inference needed
- Full test sets: MMLU 14,042 items, TruthfulQA 817, ARC 1,172

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "DPO PPO logit variance comparison"**
- Domain mismatch: Archon KB contains diffusion model content (HuggingFace diffusers, stable-diffusion)
- No relevant results for LLM alignment logit analysis
- Similarity scores 0.33–0.38 (below relevance threshold)

**Query 2: "RLHF alignment logit delta analysis implementation"**
- Domain mismatch: Results reference LyCORIS, k-diffusion sampling, DPM-solver
- No relevant RLHF alignment analysis found
- Highest similarity: 0.43 (LyCORIS — still irrelevant)

**Query 3: "MCQ benchmark logit stratification quintile analysis"**
- Domain mismatch: Results reference Apple ml-stable-diffusion, CUDA cublas
- No relevant results

**Conclusion:** Archon KB contains diffusion model domain exclusively. No applicable past cases for
LLM alignment logit variance analysis. This is consistent with H-E1 and H-M1 Phase 2C findings.

### Archon Code Examples

**Query 1: "logit delta variance mixed effects model"**
- Domain mismatch: Code examples are diffusion model implementations (LEDITS++, DEIS sampler,
  LogitsProcessor for constrained generation)
- No applicable code patterns for variance stratification by margin quintile

**Applied:** Domain mismatch documented. Experiment design derived from Phase 2B verification
protocol and H-M1 proven implementation patterns.

### Exa GitHub Implementations

**Query 1: "DPO PPO logit delta variance analysis RLHF alignment comparison GitHub"**
- Status: 402 Payment Required — Exa MCP unavailable (consistent with H-E1 and H-M1 runs)

**Query 2: "Xu 2024 DPO distribution shift logit analysis implementation"**
- Status: 402 Payment Required — Exa MCP unavailable

**Applied:** No GitHub implementations retrieved. Experiment design relies on:
1. H-M1 proven implementation (analysis_anisotropy.py — reusable compute_logit_delta)
2. Phase 2B verification protocol (quintile stratification + mixed-effects model)
3. H-E1 cache (avoids redundant inference)
4. Standard scipy.stats/numpy patterns for variance testing

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M2 is an ORIGINAL analysis (not paper reproduction). The analysis pipeline extends H-M1's
proven implementation with:
1. Quintile stratification of items by pre-alignment confidence margin
2. Per-quintile variance computation (DPO vs PPO/SFT)
3. Mixed-effects model for KL-controlled interaction test

**Recommended Implementation Path:**
- Primary: Extend h-m1/code/analysis_anisotropy.py with quintile-variance analysis module
- Fallback: Standalone analysis script using H-E1 cache directly
- Justification: H-M1 code already loads H-E1 cache, computes logit deltas, and manages model
  pairs. Extending it is more efficient than building from scratch.

### Code Analysis (Serena MCP)

*Skipped* — No complex external code requiring Serena analysis. Exa MCP unavailable (402).
Implementation extends proven H-M1 codebase (compute_logit_delta already validated by 45 tests).

---

## Experiment Specification

### Dataset

**Primary Dataset:** MMLU (full test set, all subsets)
- **Type:** standard (real benchmark dataset)
- **Source:** HuggingFace — `cais/mmlu`
- **Size:** 14,042 items (full test split)
- **Subsets:** All 57 subject categories
- **Cache Status:** ✅ Available at h-e1/cache/ (reused from H-E1, H-M1)
- **Hypothesis Fit:** Large N (14,042) enables stable per-quintile variance estimates (~2,800 items/quintile)

**Secondary Dataset:** TruthfulQA
- **Type:** standard
- **Source:** HuggingFace — `truthful_qa`, `generation` config, MC format
- **Size:** 817 items
- **Cache Status:** ✅ Available at h-e1/cache/

**Tertiary Dataset:** ARC-Challenge
- **Type:** standard
- **Source:** HuggingFace — `allenai/ai2_arc`, `ARC-Challenge` config
- **Size:** 1,172 items
- **Cache Status:** ✅ Available at h-e1/cache/

**Synthetic Data Check:** ✅ PASS — All datasets are standard real benchmarks (not synthetic).

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (cache reuse from H-E1)
- Identifier: `cais/mmlu`, `truthful_qa`, `allenai/ai2_arc`
- Code:
```python
# Cache already exists — load from h-e1/cache/
# Cache format: {pair_id}_{dataset}_{split}_logprobs.pkl
# Keys: base_logprobs, aligned_logprobs, margin, flip_indicator, kl_div
cache_path = "h-e1/cache/"
```

**Quintile Stratification:**
- Margin = log-prob(top-1) − log-prob(top-2), z-scored within model pair
- Q1 = bottom 20% (lowest margin = most uncertain items)
- Q2–Q5 = progressively higher margin
- Per-quintile N at MMLU: ~2,800 items (statistically stable for variance estimates)

### Models

#### Baseline Model

**Architecture:** Tulu-2-7B (base model) → paired with tulu-2-dpo-7b (pair2, DPO)
**Architecture:** Pythia-6.9B (base model) → paired with pythia-6.9b + SFT (pair4, SFT)

**pair2 (DPO pair):**
- Base: `allenai/tulu-2-7b` (HuggingFace)
- Aligned: `allenai/tulu-2-dpo-7b` (DPO-aligned)
- Method: DPO
- Cache: h-e1/cache/pair2_*.pkl ✅

**pair4 (SFT pair — used as PPO proxy since PPO pairs broken):**
- Base: `EleutherAI/pythia-6.9b` (HuggingFace)
- Aligned: `EleutherAI/pythia-6.9b-deduped` + SFT finetuned variant
- Method: SFT (closest available to PPO contrast given pair1/pair3 failures)
- Cache: h-e1/cache/pair4_*.pkl ✅

**Note on PPO contrast:** pair1 (tulu-2-ppo-7b, 404) and pair3 (reciprocate/ppo_hh_pythia-1B,
tokenizer error) are broken. The DPO vs SFT contrast (pair2 vs pair4) is the primary comparison.
This is a limitation — document in results. The KL control approach still tests whether
variance differences are method-specific vs magnitude-specific.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers (cache reuse from H-E1)
- Identifier: Cache files already exist (no re-inference needed)
- Code:
```python
import pickle
cache = pickle.load(open("h-e1/cache/pair2_mmlu_test_logprobs.pkl", "rb"))
# cache["base_logprobs"]: np.array (N, 4)  — 4-class MCQ option logprobs
# cache["aligned_logprobs"]: np.array (N, 4)
# cache["margin"]: np.array (N,)  — z-scored confidence margin
# cache["flip_indicator"]: np.array (N,)  — binary flip labels
# cache["kl_div"]: np.array (N,)  — per-item KL divergence
```

#### Proposed Model

**Architecture:** No new model — this is a statistical analysis experiment, not training.
The "proposed model" is the analysis framework: variance stratification by margin quintile.

**Core Mechanism Implementation:**

```python
# Core Mechanism: DPO vs PPO Logit Delta Variance by Margin Quintile
# Based on: H-M1 analysis_anisotropy.py (compute_logit_delta) + Phase 2B protocol
# Purpose: Test if DPO produces higher variance in low-margin regions vs PPO/SFT

import numpy as np
from scipy import stats

def compute_variance_by_quintile(base_logprobs, aligned_logprobs, margin_z, kl_div, n_quintiles=5):
    """
    Args:
        base_logprobs: (N, 4) — base model MCQ option log-probs
        aligned_logprobs: (N, 4) — aligned model MCQ option log-probs
        margin_z: (N,) — z-scored confidence margin (pre-alignment)
        kl_div: (N,) — per-item KL divergence (base || aligned)
        n_quintiles: int — number of margin bins (default 5)
    Returns:
        quintile_variances: (n_quintiles,) — logit delta variance per quintile
        quintile_boundaries: (n_quintiles+1,) — margin thresholds
    """
    delta = aligned_logprobs - base_logprobs  # (N, 4) logit delta
    delta_var = np.var(delta, axis=1)          # (N,) per-item delta variance (4D)

    # Stratify by pre-alignment margin quintile
    boundaries = np.percentile(margin_z, np.linspace(0, 100, n_quintiles + 1))
    quintile_labels = np.digitize(margin_z, boundaries[1:-1])  # 0..n_quintiles-1

    # Per-quintile variance (controlling for KL by residualization)
    quintile_variances = np.zeros(n_quintiles)
    for q in range(n_quintiles):
        mask = (quintile_labels == q)
        delta_var_q = delta_var[mask]
        kl_q = kl_div[mask]
        # Residualize: regress out KL divergence from delta variance
        if len(delta_var_q) > 10:
            slope, intercept = np.polyfit(kl_q, delta_var_q, 1)
            residuals = delta_var_q - (slope * kl_q + intercept)
            quintile_variances[q] = np.var(residuals)
        else:
            quintile_variances[q] = np.var(delta_var_q)

    return quintile_variances, boundaries

def test_method_quintile_interaction(dpo_variances, ppo_variances, n_bootstrap=5000):
    """Test: DPO Q1 variance > PPO Q1 variance (Welch's t + bootstrap CI)"""
    t_stat, p_value = stats.ttest_ind(dpo_variances[:, 0], ppo_variances[:, 0],
                                       equal_var=False)  # Q1 only
    return {"t_stat": t_stat, "p_value": p_value / 2}  # one-tailed
```

### Training Protocol

**Note:** H-M2 is a statistical analysis experiment — no model training is performed.
The "training protocol" governs the analysis pipeline execution.

**From H-M1 (reused for controlled comparison):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Inference seed | 1 | H-M1 optimal |
| Cache source | h-e1/cache/ | H-E1 proven |
| Dataset splits | Full test sets | H-M1 confirmed stable |
| MMLU items | 14,042 | H-E1/H-M1 proven |
| TruthfulQA items | 817 | H-E1/H-M1 proven |
| ARC items | 1,172 | H-E1/H-M1 proven |
| Eigendecomp | numpy.linalg.eigh | H-M1 optimal |

**Analysis Parameters (new for H-M2):**

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Number of quintiles | 5 | Standard quintile analysis; Q1=bottom 20% |
| KL control method | OLS residualization | Remove KL confound before variance test |
| Significance threshold | p < 0.05 | SHOULD_WORK gate criterion |
| Test statistic | Welch's t-test (one-tailed) | DPO Q1 > PPO/SFT Q1 direction test |
| Bootstrap replicates | 5,000 | CI estimation for small pair count (N=2) |
| Min items per quintile | 100 | Stability threshold for variance estimate |

**Seeds:** 1 (fixed, from H-M1)

**Evaluation Mode:** Inference only (no training gradient computation)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| Q1_variance_ratio | DPO Q1 var / PPO Q1 var | Ratio > 1.0 |
| Q1_interaction_p | p-value of DPO vs PPO Q1 difference | p < 0.05 (one-tailed) |
| KL_controlled_interaction | β_method×Q1 survives KL covariate | Significant after residualization |

**Secondary Metrics:**

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| Quintile_trend | Variance ratio (DPO/PPO) across Q1–Q5 | Highest ratio at Q1, decreasing |
| Cross-benchmark consistency | Ratio significant on ≥ 2 of 3 datasets | ≥ 2/3 |
| Effect size (Cohen's d) | Standardized difference in Q1 variances | d > 0.2 (small effect) |

**Success Criteria (Gate: SHOULD_WORK):**
1. **Primary PASS:** DPO Q1 variance > PPO/SFT Q1 variance, p < 0.05, KL-controlled
2. **Secondary PASS:** Effect consistent across ≥ 2 benchmarks
3. **FAIL:** No significant difference (documents as null result, pipeline continues)

**Expected Baseline Performance (from research + H-M1):**
- H-M1 showed variance anisotropy ratio 2.9x (DPO) vs 4.6x (SFT)
- SFT shows HIGHER overall anisotropy than DPO — but H-M2 tests LOW-MARGIN specificity
- Expected: DPO concentrates variance specifically in Q1 (low margin) due to log-odds amplification
- Expected Q1 variance ratio (DPO/SFT): > 1.5 (directional prediction from Xu et al. [2024])

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (variance test, mixed-effects model)
- Library: `scipy.stats` (Welch's t, OLS), `numpy` (variance), `statsmodels` (mixed-effects optional)
- Code:
```python
from scipy import stats
import numpy as np

# Primary test: Welch's t (one-tailed)
t, p = stats.ttest_ind(dpo_q1_variances, ppo_q1_variances, equal_var=False)
p_one_tailed = p / 2  # directional test: DPO > PPO

# Effect size
pooled_std = np.sqrt((np.var(dpo_q1_variances) + np.var(ppo_q1_variances)) / 2)
cohens_d = (np.mean(dpo_q1_variances) - np.mean(ppo_q1_variances)) / pooled_std
```

**Ablation Study:**

| Variant | What It Tests | Why |
|---------|--------------|-----|
| Full model (KL-controlled) | Main effect | Primary SHOULD_WORK test |
| No KL control | Raw variance difference | Tests if KL confounds result |
| Q1 only | Low-margin specificity | Gate criterion |
| Q1–Q5 trend | Gradient of effect across quintiles | Full picture |
| Per-dataset | Generalization check | Cross-benchmark consistency |

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: DPO vs PPO/SFT Q1 variance bar chart with p-value annotation

#### Additional Figures (LLM Autonomous)

**Fig 1:** Logit delta variance by quintile (line chart, DPO vs SFT, Q1–Q5)
- Shows interaction: DPO higher specifically in low-margin regions
- X-axis: Margin quintile (Q1=lowest to Q5=highest)
- Y-axis: KL-residualized logit delta variance

**Fig 2:** KL divergence vs logit delta variance scatter (DPO vs SFT)
- Validates KL control: shows residualization removes confound

**Fig 3:** Per-benchmark Q1 variance comparison (grouped bars, MMLU/TQA/ARC)
- Cross-benchmark consistency

**Fig 4:** Variance ratio (DPO/SFT) by quintile across datasets
- Heat map or line plot

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 cache contains margin + logit data for quintile stratification | TRUE — cache confirmed in H-M1 |
| Mechanism Isolatable | KL residualization toggleable (with/without KL control) | TRUE — analysis parameter |
| Baseline Measurable | DPO and SFT variance computable independently per quintile | TRUE — separate pair analysis |

### Architecture Compatibility Check

This experiment uses cached logit data — no live model inference required.

**Required Components:**
- h-e1/cache/ directory with pair2 and pair4 logprob files
- base_logprobs and aligned_logprobs arrays (N, 4)
- pre-computed margin (z-scored) and kl_div per item

**Incompatible Scenarios:**
- Cache files corrupted or missing → FAIL early with clear error
- < 100 items in any quintile → variance estimate unstable → skip that quintile

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Quintile stratification: Q1 has N={n} items (expected ~2800)" | analysis_variance.py:stratify() |
| Tensor Shape | quintile_variances.shape == (5,) for each pair+dataset | analysis_variance.py:compute_variance_by_quintile() |
| Metric Delta | DPO Q1 variance > SFT Q1 variance (ratio check) | analysis_variance.py:test_method_quintile_interaction() |

**Activation Verification Code (Phase 4 must implement):**
```python
def verify_mechanism_activated(results):
    indicators = {
        "quintile_stratification_ok": all(
            results["quintile_counts"][q] >= 100 for q in range(5)
        ),
        "variance_computed": results["dpo_q1_variance"] > 0,
        "kl_controlled": results.get("kl_residualization_applied", False),
        "test_executed": "p_value" in results
    }
    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Empty Q1 | len(Q1_items) < 100 | FAIL: Insufficient Q1 items for variance |
| NaN variance | np.isnan(quintile_variances).any() | FAIL: Cache data corrupted |
| KL not computed | kl_div missing from cache | WARN: Skip KL control, note limitation |
| p > 0.05 | Primary test not significant | EXPLORE: Document null result (gate SHOULD_WORK) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Quintile stratification + variance computed |
| Effect Measurable | Δ > 0 | DPO Q1 var > SFT Q1 var (ratio > 1) |
| Hypothesis Supported | p < 0.05 (one-tailed Welch's t) | KL-residualized Q1 variance comparison |

---

## PoC Success Check

**Gate Type:** SHOULD_WORK (continue pipeline even on failure)

**PASS Condition:**
1. Code runs without error
2. DPO Q1 variance > PPO/SFT Q1 variance (directional)
3. p < 0.05 (Welch's t, one-tailed, KL-controlled)
4. Consistent on ≥ 2 of 3 benchmarks

**FAIL Condition (documents null, continues):**
1. No significant difference: p ≥ 0.05
2. Or: Direction reversed (SFT Q1 variance > DPO Q1 variance)
3. Document: "H-M2 null result — method-specific Q1 amplification not confirmed"

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Summary:** Archon KB contains diffusion model content exclusively. No relevant LLM alignment
sources found across 3 queries. Domain mismatch documented (consistent with H-E1, H-M1 runs).

| Query | Result | Used For |
|-------|--------|----------|
| "DPO PPO logit variance comparison" | Diffusion model results (similarity 0.33–0.38) | No applicable content |
| "RLHF alignment logit delta analysis implementation" | LyCORIS, k-diffusion (similarity 0.43) | No applicable content |
| "MCQ benchmark logit stratification quintile analysis" | Apple ml-stable-diffusion, CUDA cublas | No applicable content |

### B. GitHub Implementations (Exa)

**Exa MCP Status:** Unavailable (402 Payment Required) — consistent with H-E1 and H-M1 Phase 2C.
No GitHub repositories retrieved. Experiment design relies on:
1. H-M1 proven implementation (h-m1/code/analysis_anisotropy.py)
2. Phase 2B verification protocol (02b_verification_plan.md Section H-M2)
3. Standard scipy/numpy patterns for variance analysis

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — serena_needed = false (no external complex code to analyze).
Implementation extends proven H-M1 codebase (45 tests validated, compute_logit_delta confirmed).

### D. Previous Hypothesis Context

**Source:** H-M1 Phase 4 Validation Report (h-m1/04_validation.md)
**Source:** H-E1 Phase 4 Validation Report (h-e1/04_validation.md)

**Reused Components:**
| Component | Source File | Evidence |
|-----------|-------------|---------|
| `compute_logit_delta` | h-m1/code/analysis_anisotropy.py | 45 tests pass |
| H-E1 logprob cache | h-e1/cache/ | pair2, pair4 × 3 datasets × base+aligned |
| `run_pair_extraction` | h-e1/code/model_runner.py | 14,042+817+1,172 samples confirmed |
| Quintile stratification insight | H-M1 Fig 4 (anisotropy by quintile) | Shows Q1 effect exists in anisotropy |

**Why Reused:** Same model pairs and datasets enable controlled comparison. Only analysis
(quintile variance vs anisotropy ratio) changes between H-M1 and H-M2.

**Key Insight from H-M1 that guides H-M2:**
Fig 4 (anisotropy by quintile) from H-M1 already showed that anisotropy ratio MIGHT vary by
margin quintile. H-M2 directly tests this with the correct metric (variance by quintile, not ratio).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (MMLU+TQA+ARC) | Previous hypothesis | H-E1 Phase 2B plan + confirmed in H-M1 |
| Dataset loading (cache reuse) | Previous hypothesis | H-E1 cache (h-e1/cache/) |
| Model pairs (pair2, pair4) | Previous hypothesis | H-M1 04_validation.md (only working pairs) |
| Quintile stratification protocol | Phase 2B plan | 02b_verification_plan.md §H-M2 |
| KL residualization approach | Phase 2B plan | 02b_verification_plan.md §H-M2 (KL control) |
| Welch's t-test (one-tailed) | Phase 2B plan | 02b_verification_plan.md success criteria |
| Core pseudo-code | H-M1 analysis_anisotropy.py | compute_logit_delta + quintile extension |
| Training protocol (no training) | H-M1 validation | h-m1/04_validation.md (inference only) |
| Evaluation metrics | Phase 2B plan | Success criteria §H-M2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-17T03:30:00Z

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| H-M2 set to IN_PROGRESS | 2026-03-17T03:28:09Z | External loop starting Phase 2C → 3 → 4 |
| Phase 2C started | 2026-03-17T03:30:00Z | Experiment design IN_PROGRESS |
| Archon KB searched | 2026-03-17T03:30:00Z | 3 queries — domain mismatch (diffusion) |
| Exa MCP searched | 2026-03-17T03:30:00Z | 402 unavailable |
| Phase 2C completed | 2026-03-17T03:35:00Z | Level 1.5 specification generated |

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (3 KB queries, 1 code query — domain mismatch), Exa (unavailable 402), Serena (skipped — not needed)*
*All specifications grounded in H-M1 proven implementation and Phase 2B protocol*
*Next Phase: Phase 3 - Implementation Planning*
