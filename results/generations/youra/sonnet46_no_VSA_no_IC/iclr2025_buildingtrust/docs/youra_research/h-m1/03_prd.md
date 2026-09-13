# Product Requirements Document: H-M1
# Partial Spearman Correlation — BBQ Fairness Cross-Split Predictive Validity

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis:** H-M1 (MECHANISM / FULL tier)
**Date:** 2026-08-20
**Author:** Anonymous
**Source:** Phase 2C — 02c_experiment_brief.md

---

## 1. Executive Summary

H-M1 tests whether fairness failures in LLMs encode stable latent statistical biases in model weights that manifest consistently across the BBQ disambiguated/ambiguous context split. The experiment computes partial Spearman ρ between BBQ-Disambig and BBQ-Ambig model rankings, controlling for MMLU capability rank. Using TrustLLM (Huang et al., ICML 2024) evaluation scores for N≥10 overlapping LLMs, the gate condition is: partial ρ > 0.4 AND p < 0.05 (one-tailed Fisher z-test).

**Scope:** Data assembly from published sources, name standardization, partial Spearman ρ computation, one-tailed significance testing, sensitivity analysis (Winogrande control), and visualization. No model training. Pure statistical meta-analysis.

**Prerequisite:** H-E1 PASS — N_common ≥ 10 models with BBQ-Disambig, BBQ-Ambig, and MMLU scores confirmed.

---

## 2. Problem Statement

LLM trustworthiness benchmarks (TrustLLM, BBQ) evaluate models under both informative (disambiguated) and underspecified (ambiguous) context conditions. The hypothesis posits that fairness failures are stable enough across context conditions that a model's performance under one condition predicts its ranking under the other, even after removing general capability differences via MMLU control.

**Gate Condition (MUST_WORK):** partial_rho > 0.4 AND p_value < 0.05 (one-tailed, H1: ρ > 0)
**Failure Mode:** PIVOT — trigger single-source analysis; investigate context dependency of fairness failures.

---

## 3. Stakeholders

- **Primary:** Anonymous (researcher, author)
- **Downstream:** H-M2, H-M3 experiments (depend on H-M1 gate passing for cross-split predictive validity framework)

---

## 4. Functional Requirements

### FR-1: Data Assembly

**FR-1.1 — TrustLLM Score Extraction (PRIMARY)**
- Access TrustLLM evaluation results from `HowieHwong/TrustLLM` GitHub repository
- Extract per-model BBQ-Disambig accuracy: `results/Fairness/**/*.json`, filter `context_condition == "disambig"`
- Extract per-model BBQ-Ambig accuracy/bias score: same JSON files, filter `context_condition == "ambig"`
- Fallback: manual tabulation from TrustLLM paper arXiv 2401.05561, Table 6/7 (fairness section)
- Target model set: ChatGPT, GPT-4, Llama2-7b, Llama2-13b, Llama2-70b, Vicuna-7b, Vicuna-13b, Vicuna-33b, ChatGLM2, Falcon, Mistral-7b, Oasst-12b, Alpaca-13b, ERNIE-3.5, PaLM2

**FR-1.2 — MMLU Score Retrieval (COVARIATE)**
- Load MMLU scores for target model set from TrustLLM paper Table 3 or Open LLM Leaderboard
- Fallback: HuggingFace OpenEvals leaderboard parquet: `hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet`
- Must align model names exactly with BBQ score set

**FR-1.3 — Winogrande Score Retrieval (SENSITIVITY)**
- Load Winogrande scores from Open LLM Leaderboard or TrustLLM paper appendices
- Used as alternative capability proxy for sensitivity analysis

**FR-1.4 — HuggingFace Dataset (SECONDARY)**
- `load_dataset("TrustLLM/TrustLLM-dataset", data_dir="fairness")` — requires gated access agreement
- Use if GitHub JSON extraction fails

### FR-2: Data Preprocessing

**FR-2.1 — Model Name Standardization**
- Implement canonical name mapping: `"llama-2-7b-chat"` → `"Llama2-7b-chat"`, etc.
- Handle all known aliases from TrustLLM, HuggingFace leaderboard, and paper tables
- Log all name mappings applied

**FR-2.2 — N_common Computation**
- Inner join on models with non-null BBQ-Disambig, BBQ-Ambig, and MMLU scores
- Verify N_common ≥ 10 (H-E1 established this; confirm here)
- Log final N_common and list of included models

**FR-2.3 — Metric Scale Reconciliation**
- Audit whether BBQ-Ambig score uses same metric as BBQ-Disambig (accuracy vs. bias rate)
- If different: convert to common scale (accuracy %) before correlation
- Document any scale reconciliation applied

**FR-2.4 — DataFrame Construction**
- Build master DataFrame: columns = [model_name, bbq_disambig, bbq_ambig, mmlu, winogrande]
- Save to `data/h_m1_scores.csv` for reproducibility

### FR-3: Statistical Analysis

**FR-3.1 — Raw Spearman ρ (Baseline)**
- Compute raw Spearman ρ between bbq_disambig and bbq_ambig (no MMLU control)
- Using `scipy.stats.spearmanr`
- Report: ρ_raw, p_raw, N

**FR-3.2 — Partial Spearman ρ (Primary)**
- Compute partial Spearman ρ controlling for MMLU rank
- Using `pingouin.partial_corr(data=df, x='bbq_disambig', y='bbq_ambig', covar=['mmlu'], method='spearman', alternative='greater')`
- Report: partial_rho, p_value, CI95%, N

**FR-3.3 — Gate Evaluation**
- Check: partial_rho > 0.4 AND p_value < 0.05
- Log: `gate_pass = True/False`
- Secondary: verify raw_rho > partial_rho (confirms MMLU explains variance)

**FR-3.4 — Sensitivity Analysis (Winogrande)**
- Repeat partial Spearman ρ with Winogrande as capability proxy
- Report: rho_winogrande, p_winogrande
- Compare to MMLU-controlled result

**FR-3.5 — Mechanism Verification**
- Assert N_common ≥ 10
- Assert -1 ≤ partial_rho ≤ 1
- Assert 0 ≤ p_value ≤ 1
- Log: "Mechanism verified: partial_rho={:.3f}, n={}"

### FR-4: Ablation Variants

**FR-4.1 — No-Control Ablation**
- Raw Spearman ρ without MMLU control (already computed in FR-3.1)
- Demonstrates that controlling for capability reduces (not inflates) correlation

**FR-4.2 — Winogrande-Control Ablation**
- Replaces MMLU with Winogrande as capability control variable
- Tests robustness: result should not be MMLU-specific

**FR-4.3 — N_common Sensitivity Ablation**
- Re-run with conservative N_common (drop models with any score imputed from paper tables vs. leaderboard JSON)
- Ensures result not driven by data quality differences

### FR-5: Visualization

**FR-5.1 — Gate Metrics Bar Chart (MANDATORY)**
- Bar chart: partial_rho (target >0.4) vs raw_rho
- Include 95% CI error bars
- Mark gate threshold (0.4) as horizontal dashed line
- Save: `figures/gate_metrics_comparison.png`

**FR-5.2 — Rank Scatter Plot**
- BBQ-Disambig rank vs BBQ-Ambig rank, labeled with model names
- Overlay partial correlation fit line
- Save: `figures/rank_scatter_bbq.png`

**FR-5.3 — Sensitivity Comparison Chart**
- Bar chart: ρ(MMLU control) vs ρ(Winogrande control)
- Save: `figures/sensitivity_comparison.png`

**FR-5.4 — Score Distribution Box Plots**
- Box plots of BBQ-Disambig and BBQ-Ambig scores across N_common models
- Save: `figures/score_distributions.png`

**FR-5.5 — MMLU vs Fairness Scatter**
- MMLU rank vs BBQ-Disambig rank (motivates capability control)
- Save: `figures/mmlu_vs_fairness.png`

---

## 5. Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed seed = 1 (statistical analysis is deterministic; seed for any random tie-breaking only)
- All data sources documented with version/URL
- Intermediate DataFrames saved to CSV

**NFR-2: Performance**
- Runtime < 5 seconds on any CPU (N ≤ 20 data points, pure pandas/scipy/pingouin)

**NFR-3: Transparency**
- All model name mappings logged
- All data source fallback decisions logged
- N_common computation logged with list of included models

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| partial_rho | > 0.4 | Gate (MUST_WORK) |
| p_value | < 0.05 (one-tailed) | Gate (MUST_WORK) |
| raw_rho > partial_rho | True | Secondary |
| Winogrande ρ ≈ MMLU ρ | Within 0.1 | Tertiary (robustness) |
| N_common | ≥ 10 | Prerequisite |

---

## 7. Dependencies

### 7.1 Python Packages

```
pingouin==0.6.1
scipy>=1.11
pandas>=1.5
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
datasets>=2.14  # HuggingFace (optional)
```

Install: `pip install pingouin scipy pandas numpy matplotlib seaborn`

### 7.2 Data Sources

| Source | Type | Access |
|--------|------|--------|
| HowieHwong/TrustLLM | GitHub repo | Public (clone) |
| TrustLLM paper arXiv 2401.05561 | PDF | Public |
| TrustLLM/TrustLLM-dataset | HuggingFace | Gated (requires agreement) |
| OpenEvals/leaderboard-data | HuggingFace | Public parquet |

### 7.3 Predecessor Outputs

- H-E1 validation result (PASS) — confirms N_common ≥ 10
- H-E1 `data/` folder may contain partially assembled score matrix (reuse if available)
