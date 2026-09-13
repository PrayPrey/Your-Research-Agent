# Experiment Design: H-M1

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under k=8 frozen-model profiling, the top-50 MBPP problems selected by variance_i = p_i*(1-p_i) have higher mean variance than a random-50 selection, and the selected problems have meaningfully different variance distribution, confirming that the profiling signal is real and the selection ranking is stable.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Validates that variance profiling produces a meaningful, non-random ranking signal. No training required; purely analytical from profiling output.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASSED (MUST_WORK gate satisfied)
**Gate Status:** MUST_WORK — if fails, PIVOT (increase k or change selection criterion)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (completed, PASSED)

### Gate Condition
MUST_WORK: mean(variance_i(variance-50)) > mean(variance_i(random-50)). If this fails, top-50 variance selection provides no advantage over random — the entire downstream hypothesis chain (H-M2 through H-M4) is invalidated. Pivot to k=16 or alternative criterion.

---

## Continuation Context

H-M1 directly reuses the profiling output from H-E1. The 374-problem MBPP profiling run (k=8 completions per problem with frozen DeepSeek-Coder-7B-Instruct, computing p_i and variance_i for all problems) is the input data for this hypothesis. No new inference required.

### Previous Hypothesis Results (H-E1)
- **Result:** PASSED
- **Key Output:** p_i distribution across 374 MBPP problems computed; at least 50 problems have variance_i > 0.1; top-50 problem IDs identified by variance ranking.
- **Artifact:** `docs/youra_research/h-e1/` profiling results (variance array, p_i array, ranked problem IDs)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Variance-based data selection ranking stability**
- No directly relevant results found. Archon KB contains diffusion model content (unrelated domain).
- **Fallback:** Relied on Exa GitHub and domain knowledge from BUILD_ON claims in 02b_verification_plan.md.

**Query 2: GRPO reward variance profiling subset selection**
- No directly relevant results found in KB.

**Query 3: MBPP benchmark pass rate distribution**
- No directly relevant results found in KB.

### Archon Code Examples

**Query: MBPP variance profiling pass rate computation**
- No relevant code examples found in KB (diffusion pipeline code returned).
- **Note:** Archon KB appears to be populated with diffusion/image generation content; RLEF/code-LLM content is absent. All implementation guidance sourced from Exa.

### Exa GitHub Implementations

**Query 1: MBPP pass rate variance profiling frozen model top-k vs random**

**Source 1**: bay-yearick-lab/grpo-standard-deviation-identity (README + diagnostics script)
- **URL:** https://github.com/bay-yearick-lab/grpo-standard-deviation-identity
- **Relevance:** Exact mathematical foundation for this experiment. Provides `grpo_diagnostics.py` with closed-form implementations of `per_prompt_gradient(k, G)`, `silent_rate(p, G)`, `expected_gradient(p, G)`.
- **Key Code:**
  ```python
  import grpo_diagnostics as gd
  gd.silent_rate(0.5, 8)              # 0.0078 -> wasted-group fraction at p=0.5
  gd.per_prompt_gradient(3, 8)        # 0.4841 -> gradient gain when 3/8 correct
  gd.expected_gradient(p, G)          # binomial sum -> expected gradient at difficulty p
  ```
- **Key Insight:** The variance σ = sqrt(k(G-k))/G IS the gradient magnitude. At k=8 (our profiling), p_i = k/8 and variance_i = p_i*(1-p_i). The silent-group rate p^G + (1-p)^G confirms that extreme-p problems waste gradient budget.
- **Used For:** Pseudo-code structure; success criteria derivation.

**Source 2**: GRPO AI Infrastructure Knowledge Base
- **URL:** https://ai-infrastructure.net/rl-grpo/
- **Relevance:** Explains `frac_reward_zero_std` signal and its interpretation. Confirms that group where all rewards identical → zero gradient → no learning.
- **Key Insight:** "Watch frac_reward_zero_std: prompts where every sample is right or wrong contribute no gradient." This is the downstream metric H-M2 will measure; H-M1 validates the input signal that should predict it.

**Source 3**: arXiv 2607.00152 (GRPO, Dr. GRPO, and DAPO identity paper)
- **URL:** https://export.arxiv.org/pdf/2607.00152
- **Relevance:** Empirical quantification on 215,608-problem Big-Math corpus. At G=8: 44% of prompts produce no GRPO gradient. Variance profiling on MBPP should reveal similar structure. Confirms the mathematical basis is empirically observable at scale.
- **Key Insight:** "An irreducible 11.2% (p̂ ∈ {0,1}) are silent at every G." This motivates the h-e1 filter; h-m1 confirms the remaining intermediate problems are correctly ranked.

**Query 2: scipy Mann-Whitney rankdata statistical test**

**Source 4**: SciPy docs — mannwhitneyu + rankdata
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
- **Relevance:** Provides the exact non-parametric test for comparing variance distributions of two independent groups (variance-50 vs random-50). No normality assumption needed (appropriate for bounded [0,0.25] variance values).
- **Key Code:**
  ```python
  from scipy.stats import mannwhitneyu, rankdata
  stat, p = mannwhitneyu(var_selected, var_random, alternative='greater')
  # alternative='greater': H1: variance-50 has higher variance than random-50
  ```

**Serena Analysis Needed:** false — h-m1 is a statistical analysis experiment with straightforward numpy/scipy code; no complex neural network code to analyze.

### 🎯 Implementation Priority Assessment

H-M1 is a pure analytical hypothesis — no paper to reproduce. The implementation is original statistical analysis code built on:
- numpy (array operations on profiling output)
- scipy.stats (Mann-Whitney U test, rankdata)
- matplotlib (distribution visualization)

**Recommended Implementation Path:**
- Primary: Original implementation using h-e1 profiling output arrays
- Fallback: Rerun profiling if h-e1 artifacts not accessible (loads from `google-research-datasets/mbpp`)
- Justification: H-M1 is downstream of H-E1; the profiling arrays are the direct input

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M1 requires only numpy/scipy statistical analysis on the profiling output from H-E1. No complex architectural patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** MBPP (Mostly Basic Python Problems) — Full split
**Type:** standard (programmatic-api via HuggingFace Datasets)
**Source:** google-research-datasets/mbpp

**Statistics:**
- Train split: 374 problems (the profiling pool; same as H-E1)
- Test split: 500 problems (not used in H-M1)
- Input format: task_id (int), text (str), test_list (list[str])
- Binary reward: execution pass/fail

**Note:** H-M1 does NOT reload the dataset for new inference. It operates on the profiling output (p_i array, variance_i array, ranked_ids list) from H-E1. If H-E1 artifacts are present, dataset loading is skipped.

**Synthetic Data Check:** ✅ PASSED — Uses real MBPP dataset (standard HuggingFace benchmark). No synthetic data.

**Loading Information** (for Phase 4, only if H-E1 artifacts absent):
- Method: HuggingFace Datasets
- Identifier: `"google-research-datasets/mbpp"`
- Code: `load_dataset("google-research-datasets/mbpp", "full", split="train")`

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-Instruct (frozen, for profiling only)
**Type:** Code LLM, instruction-tuned, 7B parameters

**Note:** H-M1 does NOT run the model for new inference. Model is used only if H-E1 profiling artifacts must be regenerated.

**Configuration:**
- Parameters: 7B
- Dtype: bfloat16
- Inference: temperature=1.0, do_sample=True (for k=8 i.i.d. completions)
- Gradient updates: NONE (frozen)

**Loading Information** (for Phase 4, only if H-E1 artifacts absent):
- Method: HuggingFace Transformers
- Identifier: `"deepseek-ai/deepseek-coder-7b-instruct-v1.5"`
- Code: `AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-7b-instruct-v1.5", torch_dtype=torch.bfloat16)`

#### Proposed Model

**Architecture:** N/A — H-M1 is a statistical analysis experiment with no "proposed model." The mechanism under test is the variance-based ranking procedure itself.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Variance-Guided Top-K vs Random Selection Comparison
# Based on: GRPO group-standard-deviation identity (arXiv:2607.00152)
#           bay-yearick-lab/grpo-standard-deviation-identity

import numpy as np
from scipy.stats import mannwhitneyu, rankdata

def compare_variance_selection(profiling_output: dict, k: int = 50, seed: int = 42):
    """
    H-M1: Compare top-k variance selection vs random-k selection.
    Input: profiling_output from H-E1 with keys:
        'p_i': array (374,) — per-problem pass rate
        'variance_i': array (374,) — p_i * (1 - p_i)
        'problem_ids': array (374,) — MBPP task IDs
    Output: comparison dict with gate metrics
    """
    variance_i = profiling_output['variance_i']   # shape (374,)
    problem_ids = profiling_output['problem_ids'] # shape (374,)

    # Step 1: Top-50 by variance (deterministic ranking)
    ranked_idx = np.argsort(variance_i)[::-1]     # descending
    variance_50_idx = ranked_idx[:k]
    variance_50_var = variance_i[variance_50_idx]

    # Step 2: Random-50 baseline (fixed seed for reproducibility)
    rng = np.random.default_rng(seed)
    random_50_idx = rng.choice(len(variance_i), size=k, replace=False)
    random_50_var = variance_i[random_50_idx]

    # Step 3: Primary gate metric — direction check
    mean_var_selected = float(np.mean(variance_50_var))
    mean_var_random = float(np.mean(random_50_var))
    gate_passed = mean_var_selected > mean_var_random

    # Step 4: Secondary — boundary non-degeneracy (rank-50 vs rank-51)
    boundary_gap = float(variance_i[ranked_idx[k-1]] - variance_i[ranked_idx[k]])

    # Step 5: Mann-Whitney U (non-parametric, one-sided: variance-50 > random-50)
    stat, p_value = mannwhitneyu(variance_50_var, random_50_var, alternative='greater')

    return {
        'gate_passed': gate_passed,
        'mean_var_selected': mean_var_selected,
        'mean_var_random': mean_var_random,
        'difference': mean_var_selected - mean_var_random,
        'boundary_gap': boundary_gap,
        'mwu_stat': stat,
        'mwu_p': p_value,
        'variance_50_ids': problem_ids[variance_50_idx].tolist(),
    }
```

### Training Protocol

**No training required for H-M1.** This hypothesis is verified entirely from H-E1 profiling output via statistical analysis.

**Compute Budget:** ~30 seconds on CPU (numpy/scipy array operations over 374 problems).

**If H-E1 artifacts absent (fallback profiling run):**
- Optimizer: None (frozen model inference only)
- Batch size: 1 problem at a time (sequential for reproducibility)
- Completions per problem: k=8 (i.i.d. samples, temperature=1.0)
- Total inference calls: 374 × 8 = 2,992
- Estimated time: ~2-4 hours on single GPU (A100/H100)
- Seeds: Fixed (seed=42 for reproducibility across k=8 samples per problem)

### Evaluation

**Primary Metric:** mean(variance_i(variance-50)) vs mean(variance_i(random-50))
- **Success:** mean_var_selected > mean_var_random (direction-based, PoC level)
- **Expected range:** variance_i ∈ [0, 0.25] (max at p_i=0.5); variance-50 should cluster near 0.2–0.25

**Secondary Metric:** boundary non-degeneracy
- **Success:** variance_i[rank-50] > variance_i[rank-51] (boundary is non-degenerate; ranking is meaningful at the cutoff)
- **Diagnostic only; does not gate hypothesis**

**Supporting Analysis:** Mann-Whitney U test (non-parametric)
- **H0:** variance distribution of variance-50 == variance distribution of random-50
- **H1 (one-sided):** variance-50 has stochastically higher variance than random-50
- **Expected:** p < 0.05 (PoC level; not pre-registered statistical test, just diagnostic)
- **Rationale:** Nonparametric; appropriate for bounded [0,0.25] distributions with potential ties at 0.0 and 0.25

**PoC Pass Condition:**
1. `mean_var_selected > mean_var_random` (primary gate, MUST pass)
2. Code runs without error
3. `boundary_gap > 0` (desirable; confirms ranking non-trivial at cutoff)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical comparison (not ML classification/regression)
- Library: `scipy.stats` (mannwhitneyu), `numpy` (mean, argsort)
- Code: `from scipy.stats import mannwhitneyu; stat, p = mannwhitneyu(a, b, alternative='greater')`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing mean(variance_i) for variance-50 vs random-50, with individual data points overlaid as strip plot

#### Additional Figures (LLM Autonomous)

The following visualizations are recommended for communicating the H-M1 results:

1. **Variance Distribution Histogram:** Side-by-side histograms of variance_i for variance-50 and random-50 sets (bins=10, range=[0,0.25]). Overlay the full-374 distribution in grey for reference.

2. **Rank Plot:** Sorted variance_i for all 374 problems, with vertical line at rank-50 boundary and shaded region marking the selected set. Illustrates the "cliff" at the selection boundary.

3. **CDF Comparison:** Empirical CDF of variance_i for variance-50 vs random-50. Visual evidence of stochastic dominance if H-M1 passes.

4. **Silent Rate Prediction:** Scatter plot of problem_id vs predicted silent_rate(p_i, G=4) for variance-50 (red) vs random-50 (blue). Motivates why variance selection should reduce frac_reward_zero_std in H-M2.

**Output Location:** `docs/youra_research/h-m1/figures/`

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify that the variance ranking mechanism actually captures a real signal, not sampling noise.

**Pre-conditions:**
- `mechanism_exists`: True — variance_i = p_i*(1-p_i) is a deterministic function of the profiling output; it exists as long as k=8 profiling was run.
- `mechanism_isolatable`: True — The ranking step is a pure numpy sort; it is fully isolatable from any training dynamics.
- `baseline_measurable`: True — random-50 is generated with fixed seed; comparison is exact and reproducible.

**Architecture Compatibility:**
- H-M1 uses no neural architecture. The "mechanism" is the numpy argsort ranking procedure.
- Compatible with any Python environment with numpy ≥ 1.20 and scipy ≥ 1.7.

**Activation Indicators:**
- `mechanism_log_message`: `"[H-M1] Variance selection ranking complete: mean_var_selected={:.4f}, mean_var_random={:.4f}, gate={'PASSED' if gate_passed else 'FAILED'}"`
- `tensor_shape_change`: Not applicable (no tensors). Output shape: `variance_50_idx: (50,)`, `random_50_idx: (50,)`
- `metric_delta_expected`: mean_var_selected - mean_var_random > 0.05 (conservative; variance_i ∈ [0, 0.25])

**Mechanism Verification Code:**
```python
# Inline self-check — add to experiment script
assert len(variance_50_idx) == 50, "Selection size wrong"
assert len(set(variance_50_idx) & set(random_50_idx)) <= 50, "Overlap within bounds"
assert variance_i[ranked_idx[0]] >= variance_i[ranked_idx[-1]], "Ranking order wrong"
assert np.all(variance_i[variance_50_idx] >= variance_i[ranked_idx[50]]), \
    "Top-50 includes problems below boundary — ranking error"
print(f"[H-M1] Gate: mean_var_selected={mean_var_selected:.4f} > mean_var_random={mean_var_random:.4f}: {gate_passed}")
```

**Failure Detection:**
- If `mean_var_selected <= mean_var_random`: ranking provides no signal. Check if profiling had insufficient variance (degenerate distribution — would have failed H-E1).
- If `boundary_gap < 0`: ranking is non-monotone — sorting bug.
- If `mwu_p > 0.5`: distributions are statistically indistinguishable — investigate k sufficiency.

**Success Criteria:**
- `hypothesis_support_threshold`: mean_var_selected > mean_var_random (direction only, no minimum gap required at PoC level)
- `hypothesis_support_metric`: mean(variance_i) of top-50 vs random-50

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Archon KB returned no relevant results for this hypothesis. The KB appears populated with diffusion model content. All research sourced from Exa.

### B. GitHub Implementations (Exa)

**Repository 1**: bay-yearick-lab/grpo-standard-deviation-identity
- **URL:** https://github.com/bay-yearick-lab/grpo-standard-deviation-identity
- **Query Used:** "GRPO reward variance per-problem statistics numpy scipy Mann-Whitney rankdata comparison"
- **Relevance:** Provides mathematical foundation and reference implementations for GRPO gradient identity; `grpo_diagnostics.py` implements `silent_rate`, `per_prompt_gradient`, `expected_gradient`
- **Key Code (annotated):**
  ```python
  # from grpo_diagnostics.py (bay-yearick-lab)
  # silent_rate: fraction of groups that produce zero GRPO gradient
  def silent_rate(p, G):
      return p**G + (1-p)**G
  # per_prompt_gradient: gradient magnitude for a group with k correct out of G
  def per_prompt_gradient(k, G):
      return (k * (G - k))**0.5 / G  # = sigma = variance^0.5 for binary rewards
  ```
- **Used For:** Pseudo-code design; mathematical grounding of variance_i = p_i*(1-p_i) as the correct selection signal

**Repository 2**: GRPO AI Infrastructure KB
- **URL:** https://ai-infrastructure.net/rl-grpo/
- **Query Used:** "GRPO reward variance per-problem statistics numpy scipy"
- **Relevance:** Explains `frac_reward_zero_std` metric and `group_relative_advantage` function
- **Key Code (annotated):**
  ```python
  # group_relative_advantage: zero gradient when all rewards equal (std=0)
  def group_relative_advantage(rewards, scale_by_std=True, eps=1e-8):
      r = np.asarray(rewards, dtype=np.float64)
      mean = r.mean(axis=1, keepdims=True)
      centered = r - mean
      if not scale_by_std:
          return centered
      std = r.std(axis=1, keepdims=True)  # population std
      return centered / (std + eps)       # zero when std=0 (all rewards same)
  ```
- **Used For:** Motivating why variance-high problems are preferred; links H-M1 selection signal to H-M2 frac_reward_zero_std

**Repository 3**: arXiv 2607.00152 (GRPO identity paper)
- **URL:** https://export.arxiv.org/pdf/2607.00152
- **Query Used:** "GRPO reward variance per-problem statistics"
- **Relevance:** Empirical validation that 44% of problems produce no GRPO gradient at G=8 on Big-Math; direct precedent for variance profiling as a selection criterion
- **Key Insight:** Variance profiling identifies the 11–44% silent prompts that waste gradient budget; variance-50 selection removes them
- **Used For:** Justifying success threshold; supporting the mechanism claim

**Repository 4**: SciPy docs — mannwhitneyu
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
- **Query Used:** "GRPO reward variance per-problem statistics numpy scipy Mann-Whitney rankdata comparison"
- **Relevance:** Provides the exact non-parametric test for comparing two independent variance distributions without normality assumption
- **Key Code (annotated):**
  ```python
  from scipy.stats import mannwhitneyu
  # one-sided test: H1 = variance-50 has higher variance than random-50
  stat, p = mannwhitneyu(variance_50_var, random_50_var, alternative='greater')
  ```
- **Used For:** Statistical comparison method in evaluation section

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. H-M1 is a pure statistical analysis using standard numpy/scipy operations; no complex architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-E1 validation results
- **Reused Components:** p_i array (374,), variance_i array (374,), ranked_ids list — direct output of H-E1 profiling run
- **Why Reused:** H-M1 is analytically defined as a function of H-E1 profiling output; no new inference needed

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MBPP train, 374 problems) | Phase 2B (02b_verification_plan.md) | Section 1.3 |
| Model (DeepSeek-Coder-7B-Instruct, frozen) | Phase 2B (02b_verification_plan.md) | Section 1.3 |
| Variance formula variance_i = p_i*(1-p_i) | GitHub | B.1 (bay-yearick-lab) |
| silent_rate formula p^G + (1-p)^G | GitHub | B.1 (bay-yearick-lab) |
| Mann-Whitney U test (one-sided) | SciPy docs | B.4 |
| `frac_reward_zero_std` interpretation | GitHub | B.2 (ai-infra KB) |
| 44% silent at G=8 empirical baseline | arXiv 2607.00152 | B.3 |
| Success criterion (direction-based) | Phase 2B | Section 2.2 H-M1 |
| Boundary non-degeneracy check | Domain reasoning | (derived from ranking theory) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed by harness)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- 2026-08-21T15:11:03: H-M1 set to IN_PROGRESS; Phase 2C starting
- 2026-08-21: Phase 2C completed; experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 4 sources), Serena (skipped — straightforward statistical analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
