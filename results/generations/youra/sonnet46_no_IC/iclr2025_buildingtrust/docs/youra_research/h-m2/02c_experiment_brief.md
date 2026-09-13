# Experiment Design: H-M2
## RLHF Representation Rigidity Reduces Adversarial Robustness

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under the TrustLLM 16-model setting, if RLHF-induced conservative refusal patterns create representation-level rigidity that is brittle to adversarial perturbations, then ρ_partial(safety, robustness) < -0.4 (p < 0.0033), and RLHF Chat variants should score EQUAL OR LOWER on adversarial robustness compared to size-matched base models, because the same pattern-matching representations that avoid harmful outputs via conservative prediction are brittle to adversarial input perturbations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 ✅ PASS (ρ_partial(safety, ethics) = 0.841, 3/3 LLaMA-2 pairs positive)
**Gate Status:** SHOULD_WORK (failure = EXPLORE, not STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (Step 2 of 3-step RLHF causal chain)
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
**SHOULD_WORK gate:** ρ_partial(safety, robustness) < -0.4 AND p < 0.0033; AND ≥2/3 LLaMA-2 within-family Δ_robustness ≤ 0.

**Failure handling:** If primary fails → EXPLORE (report positive correlation as null finding; pipeline continues). Gate violation does NOT stop workflow.

---

## Continuation Context

**Previous Hypothesis:** H-M1 (RLHF Co-Optimizes Safety and Ethics)
**Key Results:**
- ρ_partial(safety, machine_ethics) = 0.841 (positive cluster confirmed)
- 3/3 LLaMA-2 within-family pairs: Δ_safety > 0 AND Δ_ethics > 0
- Dataset cache: `h-e1/code/TrustLLM/results/*.json` (all 16×6 scores)
- Conda env: youra-h-m1, Python 3.10, scipy 1.11.0

**Continuation strategy:** Reuse h-e1/experiment_results_phase3.json (contains full 16×6 rho_partial matrix AND per-model per-dimension raw scores). Extract robustness column. LLaMA-2 7B/13B/70B base+Chat scores already loaded. Only new component: optional Pythia lm-eval-harness robustness scores.

### Previous Hypothesis Results (H-M1)
| Scale | Δ_safety | Δ_ethics | Both Positive |
|-------|----------|----------|---------------|
| 7B    | +0.626   | +0.464   | ✅            |
| 13B   | +0.652   | +0.422   | ✅            |
| 70B   | +0.638   | +0.386   | ✅            |

Note: ρ_partial(safety, robustness) is already pre-computed in H-E1 results (h-e1/experiment_results_phase3.json). Primary gate check requires only loading this value.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "RLHF safety robustness tradeoff adversarial"**
- Top result: HuggingFace PEFT/LoRA (similarity 0.449) — not relevant
- Key insight: Archon KB is diffusion/vision-focused; **no relevant results for LLM statistical analysis**
- Used for: Confirming no prior implementation cases in KB

**Query 2: "LLM trustworthiness partial Spearman correlation analysis"**
- Top result: OpenReview paper (similarity 0.321) — not relevant
- Key insight: **No relevant knowledge base content** for this domain
- Used for: Confirming KB gap, directing research to Exa

**Query 3: "adversarial robustness benchmark evaluation LLM"**
- Top result: hf.co/papers/2305.14314 (similarity 0.497) — unrelated PEFT paper
- Key insight: KB consistently returns diffusion/NLP unrelated content at low similarity
- **Overall Archon finding:** Archon KB provides no relevant guidance; primary sources are Exa (TrustLLM toolkit) and continuation from H-E1/H-M1

### Archon Code Examples

**Query: "Spearman correlation scipy statistical analysis"**
- Top result: hojonathanho/diffusion (similarity 0.309) — diffusion install script
- Key insight: **No relevant code examples**; rely on scipy/pingouin documentation from Exa

### Exa GitHub Implementations

**Repository 1: HowieHwong/TrustLLM** (⭐ 628, ICML 2024)
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Relevance:** Official TrustLLM toolkit — provides robustness evaluation pipeline and published results JSON
- **Key Code:**
  ```python
  from trustllm import run_robustness
  robustness_results = run_robustness(
      advglue_path="path_to_advglue_data.json",        # AdvGLUE: 912 samples
      advinstruction_path="path_to_advinstruction_data.json",
      ood_detection_path="path_to_ood_detection_data.json",
      ood_generalization_path="path_to_ood_generalization_data.json"
  )
  ```
- **Robustness subsections:** Natural Noise (AdvGLUE: 912 samples, AdvInstruction) + OOD (detection + generalization)
- **Results location:** `results/*.json` per-model per-dimension (already cached from H-E1)
- **Metrics:** ASR (↓), RS (↑) for adversarial tasks; RtA (↑) for OOD detection; Micro F1 (↑) for OOD generalization
- **Key insight for H-M2:** Robustness = composite of 4 sub-tasks aggregated to single dimension score

**Repository 2: raphaelvallat/pingouin** (partial_corr implementation)
- **URL:** https://github.com/raphaelvallat/pingouin/blob/main/src/pingouin/correlation.py
- **Relevance:** Production-quality partial Spearman via rank→covariance method
- **Key Code:**
  ```python
  import pingouin as pg
  # Partial Spearman via rank transformation + inverse covariance
  result = pg.partial_corr(data=df, x='safety', y='robustness',
                           covar=['log_params', 'is_RLHF'],
                           method='spearman')
  # Returns: r, CI95%, p-val, dof, power
  ```
- **Method:** Convert to ranks (like R cov()), compute partial corr via inverse covariance matrix — significantly faster than OLS residualization, results validated against ppcor R package
- **Used for:** Validation check against H-E1 OLS method

**Repository 3: scipy.stats (spearmanr + residualization)**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
- **Key Code:**
  ```python
  from scipy import stats
  from sklearn.linear_model import LinearRegression
  import numpy as np
  
  # OLS residualization (established in H-E1, reuse exact pattern)
  def partial_spearman_ols(x, y, Z):
      """Partial Spearman via OLS residualization on Z covariates."""
      def residualize(v, Z):
          reg = LinearRegression().fit(Z, v)
          return v - reg.predict(Z)
      x_res = residualize(x, Z)
      y_res = residualize(y, Z)
      rho, pval = stats.spearmanr(x_res, y_res)
      return rho, pval
  ```
- **Notes:** scipy docs warn: p-value only accurate for n > 500; with n=16 use t-distribution (df=n-2-k=13) — same as H-E1 implementation
- **Used for:** Core statistical method (continuity with H-E1)

**Source: Vennemeyer et al. 2026 — "Objective Matters: Fine-Tuning Objectives Shape Safety, Robustness, and Persona Drift"**
- **URL:** https://arxiv.org/html/2601.12639v1
- **Relevance:** Direct empirical evidence that preference-based fine-tuning (RLHF/DPO) "tightly couples capability gains to increased adversarial vulnerability" at larger training budgets
- **Key finding:** "supervised and preference-based tuning tightly couple capability gains to increased adversarial vulnerability and persona drift, while objectives that constrain learning signals substantially mitigate both"
- **Used for:** Theoretical grounding of H-M2 mechanism (RLHF → vulnerability trade-off)

**Serena Analysis Needed:** false — pure statistical analysis, same pattern as H-E1/H-M1

### 🎯 Implementation Priority Assessment

H-M2 is a **statistical analysis hypothesis** — no neural model implementation required. Implementation priority hierarchy:
1. **Primary:** Reuse h-e1/experiment_results_phase3.json (pre-computed ρ_partial matrix + per-model raw scores) — ZERO additional data download
2. **Secondary:** Optional Pythia lm-eval-harness scores (AdvGLUE/ANLI) — requires running `lm_eval` for Pythia 70M–12B if not already available
3. **Fallback:** TrustLLM leaderboard robustness scores (manually extracted table if JSON unavailable)

**Recommended Implementation Path:**
- Primary: Load `h-e1/experiment_results_phase3.json` → extract robustness column → compute Δ_robustness for LLaMA-2 family → verify ρ_partial(safety, robustness) already in matrix
- Fallback: Re-extract from `h-e1/code/TrustLLM/results/*.json` using same data pipeline as H-E1
- Justification: All primary data already cached from H-E1 execution; H-M2 is a targeted column-extraction + sign-test, not a new data collection task

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is pure statistical analysis (scipy OLS + spearmanr) identical in pattern to H-E1/H-M1 already validated implementations.

---

## Experiment Specification

### Dataset

**Name:** TrustLLM Published Score Tables (16-model × 6-dimension)
**Type:** standard (real published benchmark, ICML 2024)
**Source:** HowieHwong/TrustLLM GitHub — results/*.json (per-model per-dimension scores)
**Cache Path:** `h-e1/experiment_results_phase3.json` (primary), `h-e1/code/TrustLLM/results/*.json` (raw)
**Verified:** true (reused from H-E1 and H-M1)

**Focus for H-M2:** Adversarial robustness dimension column extraction from 16×6 score matrix

**Robustness Subsections (4 tasks aggregated):**
| Sub-task | Dataset | N Samples | Metric |
|----------|---------|-----------|--------|
| Natural Noise (AdvGLUE) | AdvGLUE | 912 | ASR (↓), RS (↑) |
| Natural Noise (AdvInstruction) | AdvInstruction | variable | Embedding similarity (↑) |
| OOD Detection | Custom | variable | RtA (↑) |
| OOD Generalization | Custom | variable | Micro F1 (↑) |

**Total models:** 16 (including LLaMA-2 7B/13B/70B base + Chat variants)
**LLaMA-2 family (within-family comparison):**
- llama_2_7b (base) vs llama_2_7b_chat (RLHF)
- llama_2_13b (base) vs llama_2_13b_chat (RLHF)
- llama_2_70b (base) vs llama_2_70b_chat (RLHF)

**Preprocessing:** None required — scores are pre-computed composite scores per dimension, already normalized [0,1].
**Splits:** N/A — full 16-model set used (n=16, df=13 for t-test on Spearman ρ)

**Optional Pythia Control Dataset:**
- **Name:** Pythia scaling series lm-eval-harness results (adversarial robustness proxy)
- **Type:** programmatic-api (EleutherAI/lm-evaluation-harness)
- **Models:** pythia-70m, pythia-160m, pythia-410m, pythia-1b, pythia-1.4b, pythia-2.8b, pythia-6.9b, pythia-12b (8 checkpoints)
- **Task:** AdvGLUE (ANLI/adversarial NLI subset)
- **Purpose:** Verify ρ(safety_proxy, robustness) near zero for RLHF=False series (scale only)
- **If unavailable:** Skip Pythia; note as limitation; primary gate unaffected

**Loading Information:**
- Method: JSON file load (cached) + optional lm-eval-harness API
- Identifier: `h-e1/experiment_results_phase3.json` (primary)
- Code:
  ```python
  import json
  with open("../h-e1/experiment_results_phase3.json") as f:
      h_e1_results = json.load(f)
  
  # Extract: rho_partial matrix + per-model raw scores
  rho_matrix = h_e1_results["rho_partial_matrix"]   # 6×6 dict
  model_scores = h_e1_results["model_scores"]         # {model_name: {dim: score}}
  # robustness column: model_scores[m]["robustness"] for m in model_scores
  ```

### Models

#### Baseline Model

**Architecture:** No neural model — statistical comparator
**Configuration:** Full 16-model TrustLLM set with RLHF binary annotation
**Source:** TrustLLM 16 models (all pre-evaluated, scores in h-e1/experiment_results_phase3.json)

**Model metadata required:**
```python
model_metadata = {
    "llama_2_7b":        {"log_params": 6.845, "is_RLHF": 0},  # base
    "llama_2_7b_chat":   {"log_params": 6.845, "is_RLHF": 1},  # RLHF
    "llama_2_13b":       {"log_params": 7.114, "is_RLHF": 0},
    "llama_2_13b_chat":  {"log_params": 7.114, "is_RLHF": 1},
    "llama_2_70b":       {"log_params": 7.845, "is_RLHF": 0},
    "llama_2_70b_chat":  {"log_params": 7.845, "is_RLHF": 1},
    # + 10 additional TrustLLM models (from H-E1 annotations)
}
```

**Loading Information:**
- Method: JSON load from H-E1 cache
- Identifier: `h-e1/experiment_results_phase3.json`
- Code: See Dataset section above

#### Proposed Model

**Architecture:** Mechanism under test — RLHF representation rigidity hypothesis

**Core Mechanism Implementation:**

```python
# Core Mechanism: RLHF Safety-Robustness Anti-Correlation Analysis
# Based on: H-E1 OLS residualization pattern + scipy.stats + pingouin validation

import json, numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

def compute_partial_spearman(scores, dim_x, dim_y, covariates):
    """
    Partial Spearman via OLS residualization (continuity with H-E1).
    Args:
        scores: dict {model_name: {dim: float}}
        dim_x, dim_y: dimension names (e.g., 'safety', 'robustness')
        covariates: list of covariate names ['log_params', 'is_RLHF']
    Returns: (rho_partial, p_value)
    """
    models = sorted(scores.keys())
    x = np.array([scores[m][dim_x] for m in models])
    y = np.array([scores[m][dim_y] for m in models])
    Z = np.column_stack([[scores[m][c] for m in models] for c in covariates])
    
    def residualize(v, Z):
        reg = LinearRegression(fit_intercept=True).fit(Z, v)
        return v - reg.predict(Z)
    
    x_res, y_res = residualize(x, Z), residualize(y, Z)
    rho, _ = stats.spearmanr(x_res, y_res)
    # t-distribution p-value (df=n-2-k, k=2 covariates)
    n, k = len(models), Z.shape[1]
    t_stat = rho * np.sqrt((n - 2 - k) / (1 - rho**2))
    p_val = 2 * stats.t.sf(abs(t_stat), df=n-2-k)
    return rho, p_val

def compute_within_family_delta(scores, base_model, chat_model, dim):
    """Signed difference: Chat - Base for given dimension."""
    return scores[chat_model][dim] - scores[base_model][dim]

# Integration: Load H-E1 results → extract robustness column → run analysis
```

### Training Protocol

**Note:** H-M2 is a pure statistical analysis hypothesis. There is no gradient-based training. The "training protocol" specifies the statistical analysis pipeline.

**Statistical Analysis Protocol:**

**Step 1: Data Loading (reuse from H-E1)**
- Load `h-e1/experiment_results_phase3.json`
- Extract: model_scores (16×6 matrix), model_metadata (log_params, is_RLHF annotations)
- Verify: rho_partial(safety, robustness) already in matrix (primary gate check = direct lookup)

**Step 2: Primary Gate — ρ_partial(safety, robustness)**
- Read pre-computed ρ_partial from H-E1 matrix
- If value available: gate check = (rho < -0.4 AND p < 0.0033)
- If value missing or need recomputation: run `compute_partial_spearman(model_scores, 'safety', 'robustness', ['log_params', 'is_RLHF'])`
- **Expected value from H-E1 data:** H-E1 silhouette=0.614 for k=2 clusters with safety-robustness anti-correlation implied; exact value TBD from matrix extraction

**Step 3: Secondary Gate — Within-Family Δ_robustness Sign Test**
- Compute for LLaMA-2 7B, 13B, 70B: Δ_robustness = Chat_robustness − Base_robustness
- Count pairs with Δ_robustness ≤ 0 (RLHF does NOT improve robustness)
- Gate: ≥ 2/3 pairs have Δ_robustness ≤ 0
- Report: exact Δ values, direction, sign consistency

**Step 4: Pythia Control (Optional)**
- Load Pythia 70M–12B lm-eval-harness AdvGLUE scores (if available from h-e1 cache or re-run)
- Compute ρ(robustness_proxy, scale) for Pythia series (RLHF=False, scale only)
- Expected: near-zero correlation (confirming RLHF, not scale, drives anti-correlation in TrustLLM)
- If unavailable: skip, note as limitation

**Step 5: Visualization**
- Bar chart: Δ_robustness per LLaMA-2 scale (3 pairs, grouped)
- Heatmap: 6×6 rho_partial matrix with safety-robustness cell highlighted
- Scatter: safety vs robustness scores, color by RLHF status, with partial regression lines
- (Optional) Pythia ρ comparison: TrustLLM RLHF vs Pythia scale-only

**Seeds:** 1 (deterministic statistical analysis — no randomness)
**Runtime:** < 5 seconds (pure numpy/scipy, no GPU required)
**Environment:** Reuse youra-h-m1 conda env (Python 3.10, scipy 1.11.0, sklearn, numpy, pandas)

### Evaluation

**Primary Gate (SHOULD_WORK):**
| Check | Threshold | Result Source |
|-------|-----------|---------------|
| ρ_partial(safety, robustness) | < -0.4 | H-E1 rho_partial matrix (direct read) |
| p-value (Bonferroni-corrected) | < 0.0033 | t-distribution df=13 |

**Secondary Gate:**
| Check | Threshold | Result Source |
|-------|-----------|---------------|
| LLaMA-2 pairs Δ_robustness ≤ 0 | ≥ 2/3 pairs | Within-family delta computation |

**Success Criteria:**
- PASS: Both primary AND secondary satisfied
- PARTIAL_PASS: Primary satisfied, secondary fails (or vice versa) — document and continue
- FAIL/EXPLORE: Primary fails (ρ_partial > 0 or p > 0.0033) — report as null finding, continue pipeline (SHOULD_WORK gate)

**Expected Baseline Performance (from TrustLLM paper and H-E1 silhouette evidence):**
- ρ_partial(safety, robustness) expected to be negative (implied by 2-cluster silhouette=0.614 in H-E1 — safety and robustness in different clusters)
- H-E1 finding: "Robustness uncorrelated with other dims — consistent with H-M2 prediction" (from verification_state.yaml)
- Δ_robustness: TrustLLM paper notes "some LLMs, such as Llama2, may be overly calibrated towards exhibiting trustworthiness, to the extent that they compromise their utility" — consistent with robustness penalty
- Source: Sun et al. 2024 (TrustLLM ICML), arxiv 2401.05561

**Metrics Loading Information:**
- Task Type: statistical analysis (correlation + sign test)
- Library: scipy.stats (spearmanr, t-distribution), numpy, pandas
- Code:
  ```python
  from scipy import stats
  import numpy as np
  # p-value for partial Spearman (n=16, k=2 covariates, df=13):
  # t_stat = rho * sqrt(df / (1 - rho^2)); p = 2 * t.sf(|t_stat|, df=13)
  # Bonferroni threshold: alpha = 0.05 / 15 = 0.0033
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing ρ_partial(safety, robustness) vs -0.4 threshold; secondary gate Δ_robustness bars for 3 LLaMA-2 scales vs 0 threshold

#### Additional Figures (LLM Autonomous)
Based on mechanism verification and H-M2 structure:

1. **Within-Family Δ_robustness Grouped Bar Chart** (3 scales × 2 conditions): safety delta vs robustness delta side-by-side for LLaMA-2 7B/13B/70B — shows directional divergence (both-positive for safety, ≤0 for robustness)
2. **6×6 ρ_partial Heatmap** (reuse from H-E1 figures, add safety-robustness highlight): Compare safety-ethics (positive) vs safety-robustness (negative) cells
3. **Safety vs Robustness Scatter** (16 models, color by RLHF): Shows separation + partial regression trend
4. **Cluster Motivation Plot**: 2D projection showing RLHF-sensitive (safety, ethics) vs RLHF-insensitive (robustness, ...) cluster

> Phase 4 Coder MUST include figure generation logic. All figures → `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Mechanism Exists Check:**
- `mechanism_exists`: True — the safety-robustness tradeoff is observable in pre-computed H-E1 rho_partial matrix; mechanism verification = checking sign and magnitude of ρ_partial(safety, robustness)

**Mechanism Isolatable:**
- `mechanism_isolatable`: True — OLS residualization removes scale (log_params) and RLHF status confounds; within-LLaMA-2 comparison controls architecture and pretraining; Pythia control isolates scale-only effect

**Baseline Measurable:**
- `baseline_measurable`: True — H-E1 uncontrolled Spearman (without OLS) serves as baseline for comparison; within-family comparison directly contrasts RLHF vs base at same scale

**Architecture Compatibility:**
- Statistical analysis pipeline is fully compatible — no architecture change required. Re-uses exact same code structure as H-E1 (OLS residualization + scipy spearmanr).

**Mechanism Log Message:**
- `mechanism_log_message`: "ρ_partial(safety, robustness) = {value:.4f} (expected < -0.4)"
- "LLaMA-2 Δ_robustness: 7B={d7:.3f}, 13B={d13:.3f}, 70B={d70:.3f} (expected ≤0 for ≥2/3)"

**Tensor Shape Change:** N/A (no tensor operations — scalar statistics only)

**Metric Delta Expected:**
- `metric_delta_expected`: ρ_partial(safety, robustness) ∈ (-0.9, -0.4) — strongly negative; Δ_robustness ≤ 0 for ≥2/3 LLaMA-2 pairs

**Mechanism Verification Code:**
```python
# Verification: Check mechanism activation
rho_sr, p_sr = compute_partial_spearman(model_scores, 'safety', 'robustness',
                                         ['log_params', 'is_RLHF'])
primary_pass = (rho_sr < -0.4) and (p_sr < 0.0033)

llama2_pairs = [
    ('llama_2_7b', 'llama_2_7b_chat'),
    ('llama_2_13b', 'llama_2_13b_chat'),
    ('llama_2_70b', 'llama_2_70b_chat'),
]
deltas_robustness = [compute_within_family_delta(model_scores, b, c, 'robustness')
                     for b, c in llama2_pairs]
n_nonpositive = sum(d <= 0 for d in deltas_robustness)
secondary_pass = (n_nonpositive >= 2)

print(f"ρ_partial(safety,robustness) = {rho_sr:.4f}, p={p_sr:.4e}")
print(f"Primary gate: {'PASS' if primary_pass else 'FAIL/EXPLORE'}")
print(f"Δ_robustness (7B,13B,70B): {[f'{d:.3f}' for d in deltas_robustness]}")
print(f"Secondary gate: {'PASS' if secondary_pass else 'FAIL'} ({n_nonpositive}/3 ≤0)")
```

**Hypothesis Support Threshold:**
- `hypothesis_support_threshold`: ρ_partial < -0.4 (primary); ≥2/3 Δ_robustness ≤ 0 (secondary)
- SHOULD_WORK: failure → EXPLORE path, pipeline continues

**Hypothesis Support Metric:**
- `hypothesis_support_metric`: partial_spearman_rho(safety, robustness) + binomial_sign_test(Δ_robustness ≤ 0)

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ρ_partial(safety, robustness) < -0.4 AND p < 0.0033 (SHOULD_WORK — not mandatory)
3. ≥2/3 LLaMA-2 within-family pairs show Δ_robustness ≤ 0

**SHOULD_WORK gate note:** Even if primary gate fails, the experiment is "successful" as a scientific finding — a positive ρ_partial would itself be a publishable null finding (contradicting the RLHF rigidity mechanism hypothesis).

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1: Query "RLHF safety robustness tradeoff adversarial"**
- **Type:** Knowledge base search
- **Result:** HuggingFace PEFT/LoRA docs (similarity 0.449) — not relevant
- **Key Insights:** Archon KB is diffusion/vision-domain; no LLM trustworthiness content
- **Used For:** Confirming KB gap; directing research to Exa

**Source 2: Query "LLM trustworthiness partial Spearman correlation analysis"**
- **Result:** Unrelated papers (similarity 0.321)
- **Used For:** KB gap confirmation

**Source 3: Query "adversarial robustness benchmark evaluation LLM"**
- **Result:** Unrelated PEFT paper (similarity 0.497)
- **Used For:** KB gap confirmation

**Code Source: Query "Spearman correlation scipy statistical analysis"**
- **Result:** diffusion pip install script (similarity 0.309) — not relevant
- **Used For:** Confirming no code examples; scipy/pingouin docs used instead

### B. GitHub Implementations (Exa)

**Repository 1: HowieHwong/TrustLLM** (⭐ 628, ICML 2024)
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Query Used:** "TrustLLM HowieHwong adversarial robustness evaluation RLHF safety tradeoff GitHub"
- **Relevance:** Official benchmark — provides robustness evaluation pipeline + published per-model scores
- **Key Code:**
  ```python
  # TrustLLM robustness evaluation pipeline
  from trustllm import run_robustness
  robustness_results = run_robustness(
      advglue_path="path_to_advglue_data.json",      # AdvGLUE: 912 adversarial samples
      advinstruction_path="path_to_advinstruction.json",
      ood_detection_path="path_to_ood_detection.json",
      ood_generalization_path="path_to_ood_generalization.json"
  )
  ```
- **Configuration Extracted:** Dataset file temperature=0.0 (classification), AdvGLUE 912 samples
- **Their Results:** Published in leaderboard at trustllmbenchmark.github.io
- **Used For:** Dataset specification (robustness subsections); loading code for Phase 4

**Repository 2: raphaelvallat/pingouin (partial_corr)**
- **URL:** https://github.com/raphaelvallat/pingouin/blob/main/src/pingouin/correlation.py
- **Query Used:** "scipy spearmanr OLS residualization partial correlation numpy within-family comparison GitHub"
- **Relevance:** Production partial Spearman implementation validated against R ppcor
- **Key Code:**
  ```python
  import pingouin as pg
  result = pg.partial_corr(data=df, x='safety', y='robustness',
                           covar=['log_params', 'is_RLHF'], method='spearman')
  # Method: rank transform → inverse covariance matrix (faster than OLS residualization)
  ```
- **Used For:** Validation cross-check of OLS residualization method (both methods should agree)

**Repository 3: rscgh/individual_function_predictions (residualize function)**
- **URL:** https://github.com/rscgh/individual_function_predictions/blob/main/lib/stats.py
- **Relevance:** Compact `residualize(data, confound)` implementation (same OLS pattern as H-E1)
- **Key Code:**
  ```python
  def residualize(data, confound, **kwargs):
      reg = LinearRegression(**kwargs).fit(confound.reshape(-1,1), data.reshape(-1,1))
      return data - reg.predict(confound.reshape(-1,1)).ravel()
  ```
- **Used For:** OLS residualization pattern (continuity with H-E1 implementation)

**Repository 4: tigramite/independence_tests/parcorr.py**
- **URL:** https://github.com/jakobrunge/tigramite/blob/master/tigramite/independence_tests/parcorr.py
- **Relevance:** Reference ParCorr class implementation — confirms OLS residualization is standard method
- **Used For:** Confirming implementation pattern; Spearman extension via rank-transform pre-processing

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. Statistical analysis (scipy OLS + spearmanr) is identical in pattern to H-E1/H-M1 already validated code.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1 (`h-m1/04_validation.md`)
- **Reused Components:**
  - Dataset: TrustLLM 16×6 score matrix (h-e1/experiment_results_phase3.json) — proven stable
  - Model annotations: log_params, is_RLHF per model — reused exactly
  - OLS residualization code: same function, different dimension pair (safety,robustness instead of safety,ethics)
  - Conda env: youra-h-m1, Python 3.10, scipy 1.11.0 — reuse directly
  - LLaMA-2 within-family structure: same 3 pairs (7B/13B/70B), same delta computation
- **Why Reused:** Enables controlled experiment — only the dimension under analysis (robustness vs ethics) changes; all data, annotations, and code structure remain identical

**Source:** Phase 4 Validation Report — H-E1 (`h-e1/04_validation.md`)
- **Critical finding:** ρ_partial(safety, robustness) is already computed in `h-e1/experiment_results_phase3.json`
- **Key note:** "8/15 partial Spearman pairs significant (|rho|>0.5, p<0.0033 Bonferroni)" — robustness was one of the 15 pairs analyzed; its value against safety is already in the matrix

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TrustLLM 16×6) | Previous experiment | H-E1 h-e1/experiment_results_phase3.json |
| Robustness subsections (AdvGLUE 912) | GitHub | HowieHwong/TrustLLM README |
| OLS residualization method | GitHub | rscgh/stats.py + tigramite/parcorr.py |
| partial_spearman implementation | GitHub + scipy docs | pingouin + scipy.stats |
| Model annotations (log_params, is_RLHF) | Previous experiment | H-E1 annotations (reused) |
| RLHF-robustness tradeoff mechanism | Literature | Vennemeyer et al. 2026 (arXiv 2601.12639) |
| TrustLLM findings on robustness | Literature | Sun et al. 2024 TrustLLM ICML (arXiv 2401.05561) |
| Within-family delta protocol | Previous experiment | H-M1 04_validation.md |
| t-distribution p-value formula (df=13) | scipy docs | scipy.stats docs |
| Bonferroni α=0.0033 | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04T12:00:00Z

### Workflow History for This Hypothesis
- 2026-08-04T07:12:11Z: h-m2 set to IN_PROGRESS (hypothesis loop)
- 2026-08-04: Phase 2C experiment design started
- 2026-08-04: 02b_context.md JIT-generated from 02b_verification_plan.md
- 2026-08-04: Archon KB searched (3 KB + 1 code query) — low relevance (diffusion KB)
- 2026-08-04: Exa searched (2 queries) — primary: TrustLLM toolkit + scipy/pingouin docs + Vennemeyer 2026
- 2026-08-04: Serena skipped (code sufficiently clear)
- 2026-08-04: Dataset confirmed (standard, real — TrustLLM, ICML 2024)
- 2026-08-04: Experiment specification synthesized
- 2026-08-04: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (KB × 3 + Code × 1 — low relevance), Exa (GitHub × 2 + Web × 2), Serena (skipped)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
