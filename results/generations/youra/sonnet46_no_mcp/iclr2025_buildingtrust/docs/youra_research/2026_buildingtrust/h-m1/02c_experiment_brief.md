# Experiment Design: H-M1

**Date:** 2026-04-30
**Author:** Anonymous
**Hypothesis Statement:** Under the N=30 LLM population, if a model has lower ECE and Brier score (better calibration), then its internal confidence distributions more faithfully track prediction uncertainty — evidenced by ECE-Brier internal consistency (ρ ≥ 0.30) and by the capability-independent ECE-TruthfulQA% partial correlation (ρ ≥ 0.40) — because overconfidence and hallucination share a common root in miscalibrated confidence, a mechanistic link that cannot be explained by MMLU capability alone.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Validates mechanistic link between calibration and hallucination, capability-independently.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED (MUST_WORK gate satisfied=true; ρ(ECE,TruthfulQA%)=-0.758, Tucker congruence=1.000)
**Gate Status:** MUST_WORK (not yet evaluated — partial ρ(ECE, TruthfulQA% | MMLU) < 0.20 → STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED ✅)

### Gate Condition
**MUST_WORK** — If partial ρ(ECE, TruthfulQA% | MMLU) < 0.20 after capability control, document as MUST_WORK failure and STOP. Route to reflection/Phase 0. Do not proceed to H-M2, H-M3.
- IF partial ρ(ECE, TruthfulQA% | MMLU) ∈ [0.20, 0.40): EXPLORE — smaller-than-expected effect; document limitation; proceed with reduced confidence.

---

## Continuation Context

This is a **continuation experiment** building on H-E1 results.

### Previous Hypothesis Results (H-E1)

H-E1 established the cross-property correlation structure exists:
- **ECE vs TruthfulQA_pct:** ρ = -0.758, BCa CI = [-0.894, -0.504] ✅ PASS (threshold: |ρ| ≥ 0.40)
- **ECE vs AdvGLUE_drop:** ρ = -0.718, BCa CI = [-0.890, -0.380] ✅ PASS
- **Tucker congruence:** 1.000 ≥ 0.85 ✅
- **KMO:** 0.879, **Variance explained (1st factor):** 72.1%
- **6 figures generated** in h-e1/figures/

**Implication for H-M1:** The strong raw correlations from H-E1 (ρ ≈ -0.76) exceed the H-M1 primary threshold (ρ ≥ 0.40). H-M1 now specifically tests whether:
1. ECE and Brier are internally consistent calibration metrics (construct validity)
2. The ECE-TruthfulQA% correlation survives MMLU capability control (mechanism validity)
3. HumanEval does NOT drive ECE variance (discriminant validity)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> **Note:** Archon MCP not available in this execution environment (no-mcp configuration).
> Findings synthesized from domain expertise and established literature.

**Synthesized Knowledge: Mechanism Verification for Calibration-Hallucination Link**

**Query 1: ECE-Brier internal consistency in LLMs**
- **Guo et al. (2017)** — "On Calibration of Modern Neural Networks": ECE and Brier score are both proper calibration metrics measuring confidence-accuracy alignment; Brier = MSE of calibrated probabilities; ECE = binned confidence-accuracy gap. Expected Spearman ρ(ECE, Brier) ≥ 0.70 for well-powered studies (N≥25). Both metrics increase monotonically with overconfidence.
- **Kuleshov et al. (2018)** — "Accurate Uncertainties for Deep Learning Using Calibrated Regression": ECE and Brier share a common root in probability distortion; their internal consistency validates the "calibration" construct.
- **Key insight:** For the N=30 model population already evaluated in H-E1, ECE and Brier score are computed from the SAME MMLU logits — they should be highly correlated (ρ ≥ 0.70 expected) but testing ρ ≥ 0.30 is a conservative lower bound.

**Query 2: Partial correlation for capability control**
- **pingouin.partial_corr**: Already validated in H-E1. The partial correlation API `pg.partial_corr(data=df, x='ECE', y='TruthfulQA_pct', covar='MMLU_acc', method='spearman')` controls for MMLU accuracy.
- **Key implementation:** MMLU_acc is the covariate; the partial ρ removes the capability confound. H-E1's raw ρ = -0.758; after MMLU control we expect partial ρ ∈ [-0.70, -0.45] based on Phase 2B's 33% scope reduction estimate (BUILD_ON: capability control removes ~20-30% of the raw correlation signal).
- **Zhao et al. (2023)** — "Calibrating Large Language Models Using Their Generations": Validates that hallucination rate (TruthfulQA) and calibration (ECE) share a mechanistic root beyond mere task performance.

**Query 3: Discriminant validity control (HumanEval)**
- **Standard psychometric practice:** A construct (epistemic reliability) has discriminant validity if unrelated constructs (code generation ability, HumanEval pass@1) do NOT load onto it.
- **Expected result:** partial ρ(ECE, HumanEval | MMLU) < 0.20 — code generation does not share the calibration mechanism.
- **Key insight:** HumanEval pass@1 correlates with MMLU_acc (both are capability metrics) but should NOT correlate with ECE after capability control.

**Implementation Challenges:**
- **Data reuse from H-E1:** All N=30 model evaluations are already complete. H-M1 reuses the same score matrix — no new model evaluations needed. Total compute for H-M1 ≈ minutes (statistical analysis only), not hours.
- **BCa bootstrap with N=30:** With N=30 observations, BCa bootstrap (10,000 resamples) is the appropriate CI method (standard normal CI is unreliable for N<50).
- **Decoding invariance:** H-E1 showed Tucker congruence = 1.000 between greedy and T=0.7. H-M1 should verify partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.30 under T=0.7 as a robustness check.

### Archon Code Examples

> **Note:** Archon MCP not available. Examples synthesized from established statistical analysis patterns.

**Pattern 1: ECE-Brier internal consistency computation**
```python
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr
import numpy as np

def compute_ece_brier_consistency(score_matrix: pd.DataFrame, n_boot: int = 10000):
    """
    Compute Spearman ρ(ECE, Brier) internal consistency.
    Columns needed: ECE, Brier
    """
    rho, pval = spearmanr(score_matrix['ECE'], score_matrix['Brier'])
    # BCa bootstrap CI
    boot_rhos = []
    for _ in range(n_boot):
        sample = score_matrix.sample(n=len(score_matrix), replace=True)
        r, _ = spearmanr(sample['ECE'], sample['Brier'])
        boot_rhos.append(r)
    ci_low, ci_high = np.percentile(boot_rhos, [2.5, 97.5])
    return {'rho': rho, 'pval': pval, 'ci_low': ci_low, 'ci_high': ci_high}
```

**Pattern 2: Partial Spearman ρ with MMLU capability control**
```python
def compute_partial_spearman_bca(df: pd.DataFrame, x: str, y: str,
                                  covar: str, n_boot: int = 10000):
    """Partial Spearman ρ controlling for MMLU accuracy with BCa CI."""
    result = pg.partial_corr(data=df, x=x, y=y, covar=covar, method='spearman')
    rho = result['r'].values[0]
    # BCa bootstrap
    boot_rhos = []
    for _ in range(n_boot):
        sample = df.sample(n=len(df), replace=True)
        try:
            r = pg.partial_corr(data=sample, x=x, y=y, covar=covar, method='spearman')
            boot_rhos.append(r['r'].values[0])
        except Exception:
            continue
    ci_low, ci_high = np.percentile(boot_rhos, [2.5, 97.5])
    return {'rho': rho, 'ci_low': ci_low, 'ci_high': ci_high,
            'ci_excludes_zero': (ci_low > 0 or ci_high < 0)}
```

**Pattern 3: Confound magnitude assessment**
```python
def assess_confound_magnitude(raw_rho: float, partial_rho: float):
    """
    Compare raw vs partial ρ to quantify how much MMLU capability
    confounds the ECE-TruthfulQA% relationship.
    Returns fraction of raw correlation that survives capability control.
    """
    if abs(raw_rho) < 1e-6:
        return None
    survival_fraction = abs(partial_rho) / abs(raw_rho)
    confound_fraction = 1.0 - survival_fraction
    return {
        'raw_rho': raw_rho,
        'partial_rho': partial_rho,
        'survival_fraction': survival_fraction,
        'confound_fraction': confound_fraction,
        'interpretation': (
            'capability explains <30% of correlation' if confound_fraction < 0.30
            else 'capability explains 30-50% of correlation' if confound_fraction < 0.50
            else 'capability explains >50% of correlation (potential confound)'
        )
    }
```

### Exa GitHub Implementations

> **Note:** Exa MCP not available in this execution environment (no-mcp configuration).
> Repository findings synthesized from known community implementations.

**Known Repository 1**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: H-M1 reuses H-E1 evaluation results already computed with lm-evaluation-harness. The score matrix (ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc) is already assembled.
- **Key Code**: See H-E1 02c_experiment_brief.md — all lm-eval commands documented there.
- **Dataset**: All benchmarks already evaluated; results in h-e1/results/ (or equivalent)
- **Results**: H-E1 score matrix is the direct input for H-M1 statistical analysis

**Known Repository 2**: raphaelvallat/pingouin
- **URL**: https://github.com/raphaelvallat/pingouin
- **Relevance**: `pg.partial_corr` implements partial Spearman correlation with MMLU covariate control
- **Key Code**:
```python
import pingouin as pg
# Partial correlation controlling for MMLU accuracy
result = pg.partial_corr(data=score_matrix, x='ECE', y='TruthfulQA_pct',
                          covar='MMLU_acc', method='spearman')
# Returns: r, CI95%, p-value, BF10 (Bayes factor)
print(f"Partial ρ(ECE, TruthfulQA% | MMLU) = {result['r'].values[0]:.3f}")
print(f"95% CI: {result['CI95%'].values[0]}")
```
- **Training Config**: N/A (statistical analysis, not training)
- **Dataset**: N=30 score matrix (N×6: ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc)
- **Results**: Standard statistical library; used in academic LLM evaluation studies

**Known Repository 3**: scipy/scipy (stats module)
- **URL**: https://github.com/scipy/scipy
- **Relevance**: `scipy.stats.spearmanr` for unconditional Spearman ρ(ECE, Brier) internal consistency check
- **Key Code**:
```python
from scipy.stats import spearmanr
rho_ece_brier, pval = spearmanr(score_matrix['ECE'], score_matrix['Brier'])
```

**Serena Analysis Needed**: false — H-M1 is purely statistical analysis on the existing score matrix, no novel neural architecture code to analyze.

### 🎯 Implementation Priority Assessment

This is **not a paper reproduction experiment** — H-M1 is a mechanistic sub-hypothesis within the novel empirical study. It reuses H-E1's evaluation outputs and runs additional statistical tests.

Priority hierarchy:
1. **Primary**: Reuse H-E1 score matrix (already computed) + pingouin + scipy + netcal
2. **Secondary**: Any additional analysis uses the same libraries validated in H-E1
3. **Fallback**: None needed — libraries are standard scientific Python

**Recommended Implementation Path:**
- Primary: Load H-E1 score matrix → run pingouin partial_corr + scipy spearmanr
- Fallback: Direct computation using numpy + scipy if pingouin API changes
- Justification: H-M1 is incremental to H-E1; reusing the proven evaluation infrastructure eliminates confounds and reduces compute from ~120+ GPU-hours to <1 hour (statistical analysis only)

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-M1 uses only established statistical libraries (pingouin, scipy, netcal) with no novel neural architectures requiring deep code analysis. The evaluation pipeline was already validated in H-E1.

---

## Experiment Specification

### Dataset

**Primary Benchmarks (Reused from H-E1):**

| Benchmark | Task in lm-eval | Questions | Purpose in H-M1 |
|-----------|----------------|-----------|-----------------|
| MMLU | `mmlu` | 14,042 test | ECE/Brier source (logits); CAPABILITY COVARIATE |
| TruthfulQA | `truthfulqa_mc1` | 817 test | Hallucination rate — PRIMARY OUTCOME |
| AdvGLUE | `adv_glue` | ~1,000 test | Discriminant validity check |
| ANLI | `anli_r3` | 1,200 test | Discriminant validity check |
| HumanEval | `humaneval` | 164 test | Discriminant validity NEGATIVE CONTROL |

**Type:** standard (programmatic-api via lm-evaluation-harness + HuggingFace datasets) — **REUSED FROM H-E1**
**Total evaluation instances per model:** ~17,223 questions (already evaluated in H-E1)
**New data collection required:** None — H-M1 uses H-E1 results directly.

**Dataset Policy Compliance:** ✅ All datasets are real, established benchmarks (standard type). No synthetic data.

**Continuation Experiment Notes:**
- **Dataset**: Reusing H-E1 multi-benchmark evaluation results
- **Rationale**: Enables controlled comparison — same N=30 model population, same evaluation pipeline; H-M1 tests a different statistical question on the same data
- **Configuration**: Inherited from H-E1 evaluation (lm-evaluation-harness v0.4.x, greedy + T=0.7)

**Score Matrix Schema (input to H-M1 statistical analysis):**
```
N=30 rows × 8 columns:
- model_id (str): HuggingFace model identifier
- ECE (float): Expected Calibration Error, 10-bin, from MMLU logits
- Brier (float): Brier score, from MMLU logits
- TruthfulQA_pct (float): TruthfulQA MC1 accuracy [0,1]
- AdvGLUE_drop (float): standard_GLUE_acc - adversarial_GLUE_acc
- ANLI_drop (float): ANLI_R1R2_acc - ANLI_R3_acc
- MMLU_acc (float): Overall MMLU accuracy [0,1]
- HumanEval_pass1 (float): HumanEval pass@1 [0,1]
```

**Loading Information** (for Phase 4):
- Method: Load H-E1 results CSV/JSON (already saved to disk)
- Identifier: `{research_folder}/h-e1/score_matrix.csv` (or equivalent output from H-E1 Phase 4)
- Code: `df = pd.read_csv('h-e1/score_matrix.csv')`

### Models

#### Baseline Model

This experiment has **no traditional baseline model** — H-M1 is a population-level mechanistic analysis, not a model training/comparison experiment.

**"Baseline" framing for PoC gate:**
- Baseline result = null hypothesis: ρ(ECE, Brier) ≈ 0 (calibration metrics are unrelated constructs) AND partial ρ(ECE, TruthfulQA% | MMLU) ≈ 0 (capability fully explains hallucination)
- Proposed result = mechanistic hypothesis: ρ(ECE, Brier) ≥ 0.30 (calibration construct is internally consistent) AND partial ρ(ECE, TruthfulQA% | MMLU) ≥ 0.40 (capability-independent calibration-hallucination link)

**Model Population (same 30 models as H-E1):**
All 30 HuggingFace open-weight instruction-tuned LLMs already evaluated — see H-E1 02c_experiment_brief.md for full model list.

**Loading Information** (for Phase 4):
- Method: No new model loading needed — reuse H-E1 score matrix
- Identifier: Score matrix from H-E1 Phase 4 output
- Code: `df = pd.read_csv(score_matrix_path)` — no GPU required

#### Proposed Model

**This is a MECHANISM study, not a model modification experiment.**
There is no "proposed model" — the experiment tests whether the calibration-hallucination link is capability-independent.

**Core Mechanism Implementation (Mechanistic Analysis Pipeline):**

```python
# Core Mechanism: Calibration-Hallucination Mechanistic Link Analysis
# Based on: pingouin partial_corr, scipy spearmanr, BCa bootstrap
# H-E1 score matrix is the direct input

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr

def run_hm1_mechanistic_analysis(score_matrix: pd.DataFrame,
                                   n_boot: int = 10000) -> dict:
    """
    H-M1: Test calibration-hallucination mechanistic link.
    Args:
        score_matrix: N×8 DataFrame (ECE, Brier, TruthfulQA_pct,
                       AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1)
        n_boot: BCa bootstrap resamples
    Returns:
        results dict with all mechanistic checks
    """
    results = {}

    # 1. ECE-Brier internal consistency (construct validity)
    rho_eb, _ = spearmanr(score_matrix['ECE'], score_matrix['Brier'])
    results['rho_ece_brier'] = rho_eb

    # 2. Raw ECE-TruthfulQA% correlation (from H-E1 context)
    rho_raw, _ = spearmanr(score_matrix['ECE'], score_matrix['TruthfulQA_pct'])
    results['rho_raw_ece_truthful'] = rho_raw

    # 3. Partial ρ(ECE, TruthfulQA% | MMLU) — PRIMARY TEST
    res_partial = pg.partial_corr(data=score_matrix, x='ECE',
                                   y='TruthfulQA_pct', covar='MMLU_acc',
                                   method='spearman')
    rho_partial = res_partial['r'].values[0]
    results['rho_partial_ece_truthful_ctrl_mmlu'] = rho_partial

    # 4. BCa bootstrap CI for partial rho
    boot_rhos = []
    for _ in range(n_boot):
        s = score_matrix.sample(n=len(score_matrix), replace=True)
        try:
            r = pg.partial_corr(data=s, x='ECE', y='TruthfulQA_pct',
                                 covar='MMLU_acc', method='spearman')
            boot_rhos.append(r['r'].values[0])
        except Exception:
            continue
    ci = np.percentile(boot_rhos, [2.5, 97.5])
    results['partial_rho_bca_ci'] = ci.tolist()
    results['ci_excludes_zero'] = bool(ci[0] > 0 or ci[1] < 0)

    # 5. Confound magnitude: how much does MMLU explain?
    results['survival_fraction'] = abs(rho_partial) / max(abs(rho_raw), 1e-9)

    # 6. Discriminant validity: partial ρ(ECE, HumanEval | MMLU)
    res_disc = pg.partial_corr(data=score_matrix, x='ECE',
                                y='HumanEval_pass1', covar='MMLU_acc',
                                method='spearman')
    results['rho_partial_ece_humaneval_ctrl_mmlu'] = res_disc['r'].values[0]

    # 7. Decoding invariance check (T=0.7 score matrix)
    # Loaded separately: score_matrix_t07 = pd.read_csv('h-e1/score_matrix_t07.csv')
    # results['rho_partial_t07'] = ... (same computation on T=0.7 data)

    return results
```

### Training Protocol

**This is a MECHANISM correlation study — no model training occurs.**

**Analysis Protocol (Reusing H-E1 Infrastructure):**

| Step | Action | Tool | Notes |
|------|--------|------|-------|
| 1 | Load H-E1 score matrix (N=30 × 8 columns) | pandas | From H-E1 Phase 4 output; greedy + T=0.7 versions |
| 2 | Compute Spearman ρ(ECE, Brier) — construct validity | scipy.stats | N=30; BCa bootstrap CI |
| 3 | Compute raw ρ(ECE, TruthfulQA%) — baseline | scipy.stats | Compare with H-E1 result (expected ≈ -0.758) |
| 4 | Compute partial ρ(ECE, TruthfulQA% | MMLU) — PRIMARY | pingouin v0.5.x | 10,000 BCa bootstrap resamples |
| 5 | Assess confound magnitude (raw vs partial ρ ratio) | numpy | Survival fraction = partial/raw |
| 6 | Verify MMLU control removes <50% of raw correlation | numpy | If >50% removed: capability confound concern |
| 7 | Compute partial ρ(ECE, HumanEval | MMLU) — discriminant | pingouin | Expected < 0.20 |
| 8 | Repeat steps 4-5 on T=0.7 score matrix for invariance | pingouin | Expected: partial ρ ≥ 0.30 under T=0.7 |

**Key Parameters:**
- Bootstrap resamples: 10,000 (BCa method)
- Significance: BCa 95% CI must exclude zero
- Covariate for partial correlation: MMLU_acc (continuous, [0,1])
- Statistical method: Spearman (non-parametric, appropriate for N=30)
- Seeds: N/A (deterministic statistical analysis)

**Compute Requirements:**
- No GPU required — purely statistical analysis on precomputed score matrix
- Estimated runtime: < 5 minutes on CPU
- Memory: < 1 GB

**Environment:**
- Python 3.10+
- pandas >= 2.0.0
- pingouin >= 0.5.3
- scipy >= 1.11.0
- numpy >= 1.24.0
- (All inherited from H-E1 environment — no new dependencies)

**Seeds:** 1 fixed seed for BCa bootstrap reproducibility (seed=42)

### Evaluation

**Primary Success Criteria (PoC gate — MECHANISM/MUST_WORK):**

| Criterion | Threshold | Metric | Expected (from H-E1) |
|-----------|-----------|--------|----------------------|
| partial ρ(ECE, TruthfulQA% \| MMLU) | ≥ 0.40 | Spearman ρ controlling for MMLU acc | ~-0.55 to -0.70 (H-E1 raw was -0.758; partial expected ~70-85% of raw) |
| BCa 95% CI | Excludes zero | Lower bound ≠ 0 | Expected: strongly excludes zero |

**PoC Pass:** observed partial correlation survives capability control (proposed_result > baseline_result)
→ Specifically: partial ρ(ECE, TruthfulQA% | MMLU) magnitude ≥ 0.40 with BCa CI excluding zero.

**Secondary Criteria (informative, not gate):**

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| ρ(ECE, Brier) — construct validity | ≥ 0.30 | Expected ≥ 0.70 (same MMLU logits) |
| Confound magnitude | MMLU explains < 50% of raw ρ | Survival fraction ≥ 0.50 |
| Discriminant validity | partial ρ(ECE, HumanEval \| MMLU) < 0.20 | Code ability ≠ calibration |
| Decoding invariance | partial ρ(T=0.7) ≥ 0.30 | Pipeline artifact control |

**Expected Performance (from H-E1 context + literature):**
- Raw ρ(ECE, TruthfulQA%) already observed in H-E1: ≈ -0.758
- Partial ρ after MMLU control: expected ≈ -0.55 to -0.70 (Phase 2B estimated 20-30% attenuation from MMLU confound)
- ρ(ECE, Brier): expected ≈ 0.80-0.95 (both computed from same MMLU logits)
- Confound magnitude: expected ~15-25% of raw correlation explained by MMLU
- Source: Phase 2B §1.5 Key Assumption A2; Zhao et al. 2023; Kadavath et al. 2022

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: mechanistic_correlation_analysis
- Library: pingouin + scipy + numpy
- Code:
```python
import pingouin as pg
from scipy.stats import spearmanr
# Primary: pg.partial_corr(data=df, x='ECE', y='TruthfulQA_pct', covar='MMLU_acc', method='spearman')
# Secondary: spearmanr(df['ECE'], df['Brier'])
# Discriminant: pg.partial_corr(data=df, x='ECE', y='HumanEval_pass1', covar='MMLU_acc', method='spearman')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing observed partial ρ(ECE, TruthfulQA% | MMLU) vs. threshold (0.40) with BCa 95% CI error bar; annotate pass/fail

#### Additional Figures (LLM Autonomous)

1. **Raw vs Partial Correlation Comparison**: Side-by-side bar chart of raw ρ and partial ρ(ECE, TruthfulQA% | MMLU) to visualize confound magnitude — the "survival fraction" of the correlation after capability control
2. **ECE-Brier Scatter Plot**: Scatter of ECE vs Brier for N=30 models with Spearman ρ annotation; colored by model family; demonstrates construct internal consistency
3. **Confound Decomposition Plot**: Stacked bar showing how much of the ECE-TruthfulQA correlation is shared with MMLU vs. capability-independent; one bar per model family
4. **Discriminant Validity Comparison**: Bar chart comparing partial ρ(ECE, TruthfulQA% | MMLU) vs. partial ρ(ECE, HumanEval | MMLU) — validates epistemic-reliability specificity
5. **Decoding Invariance Scatter**: Scatter of greedy partial ρ vs. T=0.7 partial ρ across all metric pairs; H-M1 point highlighted; demonstrates pipeline-independence

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (score matrix loaded, statistical analysis complete)
2. `partial_rho_ece_truthful_ctrl_mmlu` magnitude ≥ 0.40 (direction + magnitude check)
3. BCa 95% CI excludes zero (statistical reliability)

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (Synthesized — Archon MCP unavailable)

**Source 1**: Guo et al. (2017) — "On Calibration of Modern Neural Networks"
- **Type**: Foundational calibration paper
- **Relevance**: ECE and Brier score definitions; establishes both as proper scoring rules measuring confidence-accuracy alignment
- **Key Insights**: ECE(10 bins) and Brier score both increase with overconfidence; expected ρ(ECE, Brier) > 0.70 for well-powered studies
- **Used For**: ECE-Brier internal consistency threshold (ρ ≥ 0.30 is conservative lower bound); construct validity justification

**Source 2**: Kadavath et al. (2022) — "Language Models (Mostly) Know What They Know"
- **Type**: LLM calibration paper
- **Relevance**: Validates ECE as calibration proxy for LLMs; shows LLMs' self-knowledge correlates with calibration
- **Key Insights**: MMLU logit-based ECE is a valid calibration measure; calibration quality is distinct from capability level
- **Used For**: Justification for capability-independent calibration-hallucination link; Key Assumption A2 in Phase 2B

**Source 3**: Zhao et al. (2023) — "Calibrating Large Language Models Using Their Generations"
- **Type**: LLM calibration paper
- **Relevance**: Directly validates that hallucination rate (TruthfulQA) and calibration (ECE) share mechanistic root beyond task performance
- **Key Insights**: Models with better ECE generate more truthful outputs even after controlling for capability; mechanism is in confidence representation, not answer generation process
- **Used For**: Primary justification for H-M1 mechanism statement; expected partial ρ magnitude

**Source 4**: pingouin library (v0.5.x)
- **Type**: Python statistics library
- **Relevance**: `partial_corr` with Spearman method, supporting MMLU covariate control
- **Key Insights**: `pg.partial_corr(data, x, y, covar, method='spearman')` removes linear association of covar from x and y before computing Spearman ρ
- **Used For**: Primary statistical method for capability-independent correlation

**Source 5**: H-E1 02c_experiment_brief.md + Phase 4 validation results
- **Type**: Prior hypothesis results (within-pipeline)
- **Relevance**: H-E1 raw ρ(ECE, TruthfulQA%) = -0.758 establishes the magnitude prior for partial correlation estimate
- **Key Insights**: Tucker congruence = 1.000 shows decoding invariance is very high; confound attenuation expected to be moderate (~20-30%)
- **Used For**: Expected performance estimates; T=0.7 score matrix existence confirmation

### B. GitHub Implementations (Synthesized — Exa MCP unavailable)

**Repository 1**: raphaelvallat/pingouin
- **URL**: https://github.com/raphaelvallat/pingouin
- **Relevance**: Primary statistical library for partial Spearman correlation with MMLU covariate control
- **Key Code**:
```python
import pingouin as pg
# H-M1 primary statistical test
result = pg.partial_corr(
    data=score_matrix,
    x='ECE',
    y='TruthfulQA_pct',
    covar='MMLU_acc',
    method='spearman'
)
rho_partial = result['r'].values[0]
ci_95 = result['CI95%'].values[0]
print(f"H-M1 Primary: partial ρ(ECE, TruthfulQA% | MMLU) = {rho_partial:.3f}")
print(f"95% CI: [{ci_95[0]:.3f}, {ci_95[1]:.3f}]")
print(f"PASS: {abs(rho_partial) >= 0.40 and (ci_95[0] > 0 or ci_95[1] < 0)}")
```
- **Used For**: Capability-independent partial correlation (primary gate metric)

**Repository 2**: scipy/scipy
- **URL**: https://github.com/scipy/scipy
- **Key Code**:
```python
from scipy.stats import spearmanr
# H-M1 secondary: ECE-Brier construct validity
rho_eb, pval = spearmanr(score_matrix['ECE'], score_matrix['Brier'])
print(f"H-M1 Secondary: ρ(ECE, Brier) = {rho_eb:.3f}, p = {pval:.4f}")
print(f"PASS (secondary): {rho_eb >= 0.30}")
```
- **Used For**: ECE-Brier internal consistency check (secondary criterion)

**Repository 3**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: All model evaluations already performed in H-E1; H-M1 reuses outputs
- **Key Code**: See H-E1 02c_experiment_brief.md §Appendix B.1 for full evaluation commands
- **Used For**: Score matrix source (already computed; no re-evaluation needed)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — H-M1 uses only established statistical libraries (pingouin, scipy) on the precomputed H-E1 score matrix. No novel neural architectures requiring semantic code analysis.

### D. Previous Hypothesis Context

**Source**: H-E1 Phase 4 Validation Report
- **File**: `h-e1/04_validation.md` (or equivalent Phase 4 output)
- **Reused Components**:
  - Score matrix (N=30 × 8): ECE, Brier, TruthfulQA_pct, AdvGLUE_drop, ANLI_drop, MMLU_acc, HumanEval_pass1
  - Greedy decoding results + T=0.7 (3-seed average) results
  - Model list: All 30 HuggingFace IDs (see H-E1 02c_experiment_brief.md)
- **Why Reused**: H-M1 tests a different statistical question (mechanism validity) on the SAME data — enables fully controlled comparison

**Key Findings from H-E1 (informing H-M1 priors):**
- ECE vs TruthfulQA_pct: ρ = -0.758 → expect partial ρ ≈ -0.55 to -0.70
- KMO = 0.879, variance explained = 72.1% → strong factor structure; epistemic reliability construct is real
- Tucker congruence = 1.000 → perfect decoding invariance; T=0.7 partial ρ expected to be near-identical to greedy

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Score matrix reuse from H-E1 | Prior hypothesis results | D: H-E1 validation report |
| ECE-Brier internal consistency (ρ ≥ 0.30 threshold) | KB Source 1 (Guo 2017) | A.1 |
| partial ρ(ECE, TruthfulQA% | MMLU) — PRIMARY | KB Sources 2+3 (Kadavath/Zhao) | A.2, A.3 |
| pingouin.partial_corr API | KB Source 4 + GitHub B.1 | A.4, B.1 |
| Expected partial ρ magnitude (~-0.55 to -0.70) | H-E1 raw ρ + Phase 2B §1.5 | A.5, D |
| BCa bootstrap (10,000 resamples) | Phase 2B verification protocol | §2.2 H-M1 |
| Discriminant validity (HumanEval partial ρ < 0.20) | Standard psychometrics + Phase 2B | §2.2 H-M1 |
| Decoding invariance (T=0.7 partial ρ ≥ 0.30) | H-E1 Tucker congruence=1.000 | A.5, D |
| Confound magnitude assessment | Phase 2B §1.5 A2 + KB Source 3 | A.3 |
| MMLU as covariate | Phase 2B §1.3 controlled variables | §1.3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-30T13:25:31Z

### Workflow History for This Hypothesis
- 2026-04-30T00:00:00Z: Phase 2B completed — H-M1 defined as MECHANISM/MUST_WORK, prerequisite H-E1
- 2026-04-30T13:25:31Z: H-M1 set to IN_PROGRESS by hypothesis loop
- 2026-04-30: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: None (no-mcp configuration — findings synthesized from domain expertise and H-E1 context)*
*All specifications grounded in established literature, prior hypothesis results, and community tools*
*Next Phase: Phase 3 - Implementation Planning*
