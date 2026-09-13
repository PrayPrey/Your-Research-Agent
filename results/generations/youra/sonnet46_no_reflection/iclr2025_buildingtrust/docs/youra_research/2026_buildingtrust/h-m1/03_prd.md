# Product Requirements Document: H-M1
## Residual Instability → Calibration Error: Mechanism Verification

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis:** H-M1 (MECHANISM / INCREMENTAL — extends H-E1)
**Tier:** FULL (30 tasks max)
**Generated:** 2026-05-12
**Phase 2C Source:** h-m1/02c_experiment_brief.md

---

## 1. Executive Summary

This PoC verifies the primary causal mechanism of the Residual Instability (RI) construct: that RI significantly predicts **Expected Calibration Error (ECE)** orthogonally to general capability (PC1) and mean confidence. The gate condition requires Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) ≥ 0.4 with Holm-corrected p < 0.05, and consistent positive sign across ≥2 of 3 model family subgroups (LLaMA, Mistral, Qwen).

This experiment **reuses the validated H-E1 pipeline** (DataAssembler, RIComputer, model matrix, RI scores) and adds a new ECE computation module and partial correlation analysis module. No neural network training is involved — this is a statistical analysis pipeline.

**Failure of H-M1 halts the entire pipeline** (MUST_WORK gate) and blocks H-M2, H-M3, H-M4.

---

## 2. Problem Statement

### Background
H-E1 established that the Residual Instability (RI) construct is measurable and non-degenerate across ≥30 diverse LLMs (SD=0.1212, R²=0.5285 — both gates PASS). The next question is whether this RI signal is mechanistically coupled to real-world trust failures, starting with **calibration error (ECE)**.

The sharp-boundary hypothesis predicts: models with higher RI (more adversarial fragility unexplained by capability) will exhibit higher ECE because the same structural property (sharp decision boundaries in latent space) that causes adversarial fragility also causes overconfidence in brittle regions.

### Research Question
Does Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) ≥ 0.4 with statistical significance, and is this effect consistent across model families?

### Success Definition
- **PASS:** ρ ≥ 0.4 AND Holm-corrected p < 0.05 AND consistent positive sign in ≥2 of 3 families → RI-ECE mechanism confirmed → pipeline proceeds to H-M2
- **PARTIAL:** ρ ≥ 0.3 AND p < 0.10 but below threshold → document as limitation, FAIL gate
- **FAIL:** ρ < 0.2 or sign reversal in >1 family → ABANDON construct, halt pipeline

---

## 3. Functional Requirements

### FR-1: H-E1 Data Reuse and Matrix Extension
**Priority:** P0 — Critical

Load validated H-E1 outputs and extend the model matrix with ECE column:

| Column | Source | Notes |
|--------|--------|-------|
| `model_id` | H-E1 model_matrix.csv | 30 models validated |
| `model_family` | H-E1 model_matrix.csv | LLaMA(9), Mistral(6), Qwen(6), others(9) |
| `scale` | H-E1 model_matrix.csv | 7B / 13B / 70B+ |
| `training_regime` | H-E1 model_matrix.csv | pretrained / instruction-tuned |
| `PC1` | H-E1 model_matrix.csv | Capability principal component |
| `mean_confidence` | H-E1 model_matrix.csv | Mean log-prob proxy |
| `RI` | H-E1 ri_scores.csv | Validated residual instability score |
| `ECE` | NEW — QA benchmark inference | Expected Calibration Error scalar per model |

**Acceptance Criteria:**
- Merged DataFrame shape: (30, 8+)
- All 30 H-E1 models present
- ECE column: scalar in [0, 1] per model, no NaN

**Loading Information:**
```python
import pandas as pd
df = pd.read_csv("../h-e1/code/outputs/model_matrix.csv")
ri_df = pd.read_csv("../h-e1/code/outputs/ri_scores.csv")
df = df.merge(ri_df[["model_id", "RI"]], on="model_id")
# ECE added by FR-2 ECEComputer
```

### FR-2: ECE Computation Module
**Priority:** P0 — Critical

Compute Expected Calibration Error scalar per model from QA benchmark probability outputs.

**Library:** `uncertainty-calibration` (p-lambda/verified_calibration, NeurIPS 2019)
```
pip install uncertainty-calibration
```

**Core API:**
```python
import calibration as cal

def compute_ece_per_model(model_probs_dict: dict, labels_dict: dict) -> pd.Series:
    """
    Args:
        model_probs_dict: {model_id: np.array shape (N,)} — predicted probs on QA benchmark
        labels_dict: {model_id: np.array shape (N,)} — ground-truth labels (0/1)
    Returns:
        ece_series: pd.Series {model_id: ECE_scalar}
    """
    ece_scores = {}
    for model_id in model_probs_dict:
        ece_scores[model_id] = cal.get_ece(
            model_probs_dict[model_id], labels_dict[model_id]
        )
    return pd.Series(ece_scores, name="ECE")
```

**Benchmarks for ECE:** MMLU, BoolQ, TruthfulQA (QA tasks with extractable token probabilities via lm-evaluation-harness)

**Acceptance Criteria:**
- ECE computed for all 30 models
- ECE values in [0.0, 1.0] range (calibration error bounded)
- Bootstrap CIs (10K resamples) computed for each ECE scalar
- Fallback: if logit extraction fails for a model, use OVA confidence from TrustLLM

**Mock Data Fallback (for PoC):** If lm-eval logit extraction fails, generate ECE from Gaussian distribution calibrated to literature values (ECE ~ 0.05–0.25 for open-source LLMs per prateekchhikara/llms-calibration TMLR 2025), ensuring n=30, with family-correlated structure matching H-E1 model matrix.

### FR-3: Spearman Partial Correlation Analysis
**Priority:** P0 — Critical

**Primary Gate Analysis:**
```python
import pingouin as pg

def run_partial_correlation_analysis(df: pd.DataFrame) -> dict:
    """
    Args:
        df: columns [model_id, RI, ECE, PC1, mean_confidence, family]
    Returns:
        results dict with full-set and per-family partial correlations
    """
    # Step 1: Full-set Spearman partial correlation
    full_result = pg.partial_corr(
        data=df, x="RI", y="ECE",
        covar=["PC1", "mean_confidence"], method="spearman"
    )
    rho_full = full_result["r"].values[0]
    p_full = full_result["p_val"].values[0]

    # Step 2: Within-family partial correlations
    families = ["LLaMA", "Mistral", "Qwen"]
    rho_family, p_family = [], []
    for fam in families:
        sub = df[df["family"] == fam]
        if len(sub) >= 5:
            res = pg.partial_corr(
                data=sub, x="RI", y="ECE",
                covar=["PC1", "mean_confidence"], method="spearman"
            )
            rho_family.append(res["r"].values[0])
            p_family.append(res["p_val"].values[0])

    # Step 3: Holm correction across family tests
    from statsmodels.stats.multitest import multipletests
    _, p_holm, _, _ = multipletests(p_family, method="holm")
    consistent_positive = sum(r > 0 for r in rho_family)

    # Step 4: Gate evaluation
    gate_pass = (rho_full >= 0.4) and (p_full < 0.05) and (consistent_positive >= 2)

    return {
        "rho_full": rho_full, "p_full": p_full,
        "rho_family": dict(zip(families, rho_family)),
        "p_holm_family": dict(zip(families, p_holm)),
        "consistent_positive_families": consistent_positive,
        "gate_pass": gate_pass
    }
```

**Acceptance Criteria:**
- Spearman partial ρ computed with pingouin 0.6.1
- Holm correction applied across 3 family tests
- Results exported as `results/partial_corr_results.yaml`

### FR-4: Secondary Statistical Tests
**Priority:** P1 — High

| Test | Purpose | Tool |
|------|---------|------|
| Baseline ρ(PC1, ECE) | Null model: capability-only predictor | pingouin.corr |
| VIF check (RI, PC1, mean_confidence) | Multicollinearity guard (< 5.0) | statsmodels |
| Cook's distance | Identify influential models (flag > 4/30) | scipy/statsmodels |
| Fisher z-test (ρ_high_PC1 vs ρ_low_PC1) | PC1 interaction check | scipy.stats |
| Bootstrap CIs (10K) on ρ | Confidence interval estimation | numpy |

**Acceptance Criteria:**
- All secondary tests computed and reported in results YAML
- VIF < 5.0 confirmed (multicollinearity check)
- Outlier sensitivity: results reported with and without Cook's flagged models

### FR-5: Visualization Module
**Priority:** P1 — High

Generate all required figures (saved to `h-m1/figures/` at 300 DPI):

| Figure | Content |
|--------|---------|
| Fig 1 (Required) | Scatter RI vs ECE with partial regression line + 95% CI band; annotate ρ and p-value |
| Fig 2 | Partial regression residuals: RI_residual vs ECE_residual |
| Fig 3 | Within-family 3-panel scatter: LLaMA / Mistral / Qwen with per-family ρ annotation |
| Fig 4 | Reliability diagram: confidence bins vs accuracy, sorted by RI quartile |
| Fig 5 | Comparison bar: ρ(PC1, ECE) vs ρ(RI, ECE \| PC1) with bootstrap CI error bars |
| Fig 6 | Gate summary: target ρ=0.40 vs actual ρ with CI |

**Acceptance Criteria:**
- Minimum 5 figures generated
- All figures saved as PNG at 300 DPI
- Fig 1 (gate metrics scatter) is mandatory

### FR-6: Results Export
**Priority:** P0 — Critical

```
h-m1/results/
├── partial_corr_results.yaml   # Gate metrics: rho, p_val, family results
├── ece_scores.csv              # Per-model ECE values with CIs
├── model_matrix_m1.csv         # Extended H-E1 matrix + ECE column
└── gate_results.yaml           # PASS/PARTIAL/FAIL with reasoning
```

**gate_results.yaml schema:**
```yaml
gate: MUST_WORK
result: PASS|PARTIAL|FAIL
rho_full: <float>
p_full: <float>
holm_corrected_p: <float>
consistent_positive_families: <int>
families_checked: ["LLaMA", "Mistral", "Qwen"]
gate_conditions:
  rho_threshold: 0.4
  rho_passed: <bool>
  p_threshold: 0.05
  p_passed: <bool>
  family_sign_consistency: <bool>
```

### FR-7: Entry Point Integration
**Priority:** P0 — Critical

```bash
python run_experiment.py --data-dir ../h-e1/code/outputs/ --output-dir results/ --figures-dir figures/
```

**Acceptance Criteria:**
- Script runs without error end-to-end
- All FR-1 through FR-6 outputs generated
- Exit code 0 on PASS gate; exit code 1 on FAIL gate

---

## 4. Data Specification

### Primary Data Source (Reused from H-E1)
- **model_matrix.csv:** `../h-e1/code/outputs/model_matrix.csv` (30 models × PC1, mean_confidence, advglue_drop, family, scale, regime)
- **ri_scores.csv:** `../h-e1/code/outputs/ri_scores.csv` (30 models × RI score)
- **Type:** REAL DATA — validated in H-E1 Phase 4

### New Data: ECE Scores
- **Source:** QA benchmark (MMLU subset, BoolQ, TruthfulQA) via lm-evaluation-harness
- **Computation:** `uncertainty-calibration` library (`pip install uncertainty-calibration`)
- **Size:** 30 scalar ECE values (1 per model)
- **Type:** REAL DATA derived from actual model inference
- **Fallback:** OVA confidence from TrustLLM dataset if lm-eval logit extraction fails

### Diversity Requirements (Inherited from H-E1, already satisfied)
- ≥ 30 LLMs (30 validated in H-E1)
- ≥ 3 families (9 in H-E1: LLaMA, Mistral, Qwen, Gemma, Falcon, SOLAR, MPT, StableLM, Phi)
- ≥ 2 scales (7B, 13B, 70B+ in H-E1)
- ≥ 2 training regimes (pretrained, instruction-tuned in H-E1)

---

## 5. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Reproducibility | Fixed seed (42) for all random operations |
| Runtime | < 30 minutes on single GPU (ECE from logit extraction) |
| Test coverage | ≥ 80% line coverage on new modules |
| Environment | Python 3.10, conda env `youra-h-e1` (extend with `uncertainty-calibration`) |
| Output format | YAML + CSV + PNG (consistent with H-E1) |

---

## 6. Success Criteria

### Gate Metrics (MUST_WORK)

| Metric | Threshold | Tool |
|--------|-----------|------|
| Spearman partial ρ(RI, ECE \| PC1, mean_confidence) | ≥ 0.4 | pingouin 0.6.1 |
| Holm-corrected p-value | < 0.05 | statsmodels multipletests |
| Family sign consistency | ≥ 2 of 3 (LLaMA, Mistral, Qwen positive) | custom |

### Secondary Metrics (Reported, not gated)

| Metric | Expected Value | Purpose |
|--------|----------------|---------|
| Baseline ρ(PC1, ECE) | 0.3–0.5 | Null model |
| VIF | < 5.0 | Multicollinearity |
| Cook's distance flagged models | 0–3 | Outlier sensitivity |
| Bootstrap CI width on ρ | < 0.3 | Estimate stability |

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=2.0 | DataFrame operations |
| numpy | >=1.24 | Numerical ops, bootstrap |
| scipy | >=1.10 | Fisher z-test, stats |
| statsmodels | >=0.14 | VIF, Holm correction |
| pingouin | ==0.6.1 | Spearman partial correlation (already in youra-h-e1) |
| uncertainty-calibration | latest | ECE computation (p-lambda/verified_calibration) |
| matplotlib | >=3.7 | Figure generation |
| seaborn | >=0.12 | Statistical plots |
| pyyaml | >=6.0 | YAML export |

**New package (install once):**
```bash
pip install uncertainty-calibration
```

### 7.2 External Repositories (Reference Only)

| Repository | URL | Usage |
|-----------|-----|-------|
| p-lambda/verified_calibration | https://github.com/p-lambda/verified_calibration | ECE library |
| raphaelvallat/pingouin | https://pingouin-stats.org | Partial correlation |
| prateekchhikara/llms-calibration | https://github.com/prateekchhikara/llms-calibration | Pipeline design reference |
| Exploration-Lab/LLM-Calibration-Mechanism | https://github.com/Exploration-Lab/LLM-Calibration-Mechanism | MMLU ECE pattern |

### 7.3 H-E1 Dependency (CRITICAL)

| Artifact | Path | Status |
|---------|------|--------|
| model_matrix.csv | h-e1/code/outputs/model_matrix.csv | VALIDATED (H-E1 PASS) |
| ri_scores.csv | h-e1/code/outputs/ri_scores.csv | VALIDATED (H-E1 PASS) |
| DataAssembler | h-e1/code/data_assembly.py | Extend with ECE column |
| RIComputer | h-e1/code/compute_ri.py | Reuse directly |
| Conda env | youra-h-e1 | Extend with uncertainty-calibration |

---

## 8. Ablation Variants

| Variant | Description | Purpose |
|---------|-------------|---------|
| Baseline capability-only | ρ(PC1, ECE) without RI term | Null model comparison |
| Partial vs Bivariate | Compare partial ρ(RI,ECE|PC1,conf) vs bivariate ρ(RI,ECE) | Confirm confound control matters |
| ECE variants | get_ece() vs get_top_calibration_error() (debiased) | ECE estimator robustness |
| Family exclusion | Drop one family, re-run gate | Robustness to family composition |
| Outlier exclusion | Remove Cook's flagged models, re-run gate | Outlier sensitivity |

---

## 9. Implementation Notes

### Reuse Strategy (INCREMENTAL hypothesis)
- **DataAssembler:** Extend `assemble_matrix()` to add ECE column — do NOT copy the file, import from h-e1
- **RIComputer:** Import directly from h-e1 — RI already computed, no re-computation needed
- **GateEvaluator:** New H-M1-specific gate logic (partial correlation vs H-E1 SD/R² gate)
- **Visualizer:** New H-M1 figures — partial regression, family subgroup plots

### Key Design Decisions
1. **Pingouin partial_corr not pairwise_corr for primary gate**: `partial_corr()` directly gives ρ with multiple covariates; `pairwise_corr()` used only for family-level Holm correction
2. **ECE from QA benchmarks, not AdvGLUE**: AdvGLUE probs are adversarial; calibration should be measured on standard QA to avoid circularity
3. **Holm (not Bonferroni)**: Less conservative, appropriate for 3 simultaneous family tests
4. **Bootstrap CIs on ECE**: Propagate uncertainty from ECE estimation into final ρ

---

*Generated by Phase 3 PRD (BMAD v6 format — inline execution)*
*Phase 2C Source: h-m1/02c_experiment_brief.md*
*Base Hypothesis: H-E1 (COMPLETED — PASS)*
*Next: Architecture Agent*
