# Product Requirements Document: H-M3
# Per-Pair Adversarial Rank Disruption Analysis

**Hypothesis:** H-M3 (MECHANISM — INCREMENTAL on H-M2)
**Date:** 2026-08-20
**Author:** Anonymous
**Phase:** 3 — Implementation Planning
**Input:** 02c_experiment_brief.md

---

## 1. Executive Summary

H-M3 tests whether adversarial benchmark construction disrupts rank stability independently in each adversarial benchmark pair. Specifically: partial Spearman ρ for GLUE→AdvGLUE and ANLI R1→R3 (each MMLU-controlled) are both non-significantly positive (ρ < 0.4 or p ≥ 0.05). This extends H-M2's combined mean analysis into per-pair resolution.

The implementation is a statistical analysis script reusing the H-M1/H-M2 data artifact (`data/model_scores.csv`) and the same pingouin.partial_corr infrastructure. No model training; no new data collection.

---

## 2. Problem Statement

H-M2 showed Δρ = 0.192 (directional support, SHOULD_WORK gate failed). The mechanism hypothesis requires confirming that each adversarial pair individually shows low rank stability — ruling out the possibility that one pair drives the effect while the other does not.

**Research Question:** Does adversarial benchmark construction disrupt rank stability separately in the GLUE→AdvGLUE pair AND in the ANLI R1→R3 pair?

**Gate Condition (SHOULD_WORK):**
- `ρ_AdvGLUE < 0.4 OR p_AdvGLUE ≥ 0.05` AND
- `ρ_ANLI < 0.4 OR p_ANLI ≥ 0.05`

---

## 3. Scope

### In Scope
- Load existing `data/model_scores.csv` (N ≥ 10 overlapping models, columns: model_name, GLUE, AdvGLUE, ANLI_R1, ANLI_R3, MMLU, BBQ_disambig, BBQ_ambig)
- Compute partial Spearman ρ(GLUE, AdvGLUE | MMLU) and ρ(ANLI_R1, ANLI_R3 | MMLU)
- Fisher z one-tailed test vs. threshold ρ = 0.4 for each pair
- Bootstrap 95% CI (1000 resamples) for each ρ
- Rank reversal count (≥ 5 rank position shifts) per adversarial pair
- Required visualizations: gate metrics comparison bar chart + scatter/heatmap figures
- Mechanism activation verification (`verify_mechanism_activated()`)

### Out of Scope
- New model inference or fine-tuning
- New data collection (reuse H-M1/H-M2 CSV)
- Comparison between adversarial pairs (secondary analysis only)
- Hyperparameter search

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | model_scores.csv (H-M1/H-M2 artifact) |
| Type | CSV reuse — no download required |
| Path | `data/model_scores.csv` |
| Acquisition | Already built in H-M1 from TrustLLM leaderboard + AdvGLUE + OOD_NLP tables |
| Size | N ≥ 10 rows (overlapping models), 7–8 columns |
| Columns required | model_name, GLUE, AdvGLUE, ANLI_R1, ANLI_R3, MMLU |
| Optional cols | BBQ_disambig, BBQ_ambig (for reference) |

**Loading Code:**
```python
import pandas as pd
df = pd.read_csv('data/model_scores.csv')
required_cols = ['model_name', 'GLUE', 'AdvGLUE', 'ANLI_R1', 'ANLI_R3', 'MMLU']
df_clean = df.dropna(subset=required_cols)
assert len(df_clean) >= 10, f"Insufficient data: N={len(df_clean)}"
```

**No manual download task needed** — data is pre-existing artifact.

### 4.2 Models (LLMs Under Analysis)

Not trained models — evaluated LLMs in the dataset rows:
- LLaMA-2-7B, LLaMA-2-13B, LLaMA-2-70B, LLaMA-2-Chat variants
- GPT-3.5-Turbo, GPT-4
- Mistral-7B, Mistral-7B-Instruct
- Vicuna-33B, Vicuna-13B, Vicuna-7B
- Falcon-7B, ChatGLM2

---

## 5. Functional Requirements

### FR-01: Data Loading and Validation
- Load `data/model_scores.csv` into pandas DataFrame
- Validate presence of all required columns
- Drop rows with NaN in required columns
- Assert N ≥ 10 for each pair; if N < 10 for a pair, flag as underpowered and document as limitation
- Log shape: `f"DataFrame loaded: {df_clean.shape}"`

### FR-02: Partial Spearman ρ Computation — AdvGLUE Pair
- Compute `ρ_AdvGLUE = partial_corr(GLUE, AdvGLUE | MMLU, method='spearman', alternative='greater')`
- Return: rho, p_asymptotic, CI_lower, CI_upper (1000 bootstrap resamples)
- Library: pingouin ≥ 0.5.0

### FR-03: Partial Spearman ρ Computation — ANLI Pair
- Compute `ρ_ANLI = partial_corr(ANLI_R1, ANLI_R3 | MMLU, method='spearman', alternative='greater')`
- Return: rho, p_asymptotic, CI_lower, CI_upper (1000 bootstrap resamples)
- Same implementation as FR-02 with different column inputs

### FR-04: Fisher z-Test vs. Threshold (ρ = 0.4)
- For each pair: test H0: ρ ≥ 0.4 vs H1: ρ < 0.4
- Formula: `z = (arctanh(ρ) − arctanh(0.4)) / (1/√(N-3))`
- p = `norm.cdf(z)` (one-tailed, lower tail)
- Return: z_stat, p_value, significant (bool: p < 0.05)
- Apply to both ρ_AdvGLUE and ρ_ANLI

### FR-05: Rank Reversal Counting
- For each adversarial pair: compute rank positions (ID and OOD) per model
- Count models with |rank_ID − rank_OOD| ≥ 5
- Report per-pair: reversals_AdvGLUE, reversals_ANLI

### FR-06: Mechanism Activation Verification
- Implement `verify_mechanism_activated(df, results)` returning (all_ok: bool, indicators: dict)
- Checks: data_complete, n_sufficient, advglue_computed, anli_computed, pairs_differ, reversals_counted
- Must run before gate evaluation; log all indicator values

### FR-07: Gate Evaluation
- SHOULD_WORK gate passes if:
  - `(ρ_AdvGLUE < 0.4 OR p_AdvGLUE ≥ 0.05)` AND
  - `(ρ_ANLI < 0.4 OR p_ANLI ≥ 0.05)`
- Log gate result with all metric values

### FR-08: Visualization — Required Figure
- Bar chart: ρ_AdvGLUE and ρ_ANLI vs. ρ_fairness (from H-M1) with 95% CI error bars
- Horizontal threshold line at ρ = 0.4
- Save to: `docs/youra_research/h-m3/figures/gate_metrics_comparison.png`

### FR-09: Visualization — Additional Figures (LLM-Autonomous)
- Scatter: GLUE rank vs. AdvGLUE rank per model (colored by rank shift magnitude)
- Scatter: ANLI_R1 rank vs. ANLI_R3 rank per model
- Heatmap: Model × benchmark pair matrix of rank positions; highlight large shifts
- Summary table visualization: all four ρ values with CI and p-values
- Fisher z distribution plot relative to ρ = 0.4
- Save all to `docs/youra_research/h-m3/figures/`

### FR-10: Results Export
- Save results dict to `docs/youra_research/h-m3/results.json`
- Include: rho_AdvGLUE, p_AdvGLUE, ci_AdvGLUE, rho_ANLI, p_ANLI, ci_ANLI, reversals_AdvGLUE, reversals_ANLI, gate_passed, z_AdvGLUE, z_ANLI

---

## 6. Non-Functional Requirements

### NFR-01: Reproducibility
- Fix random seed: `np.random.seed(42)` before bootstrap
- Record library versions in requirements section

### NFR-02: Small-N Statistical Rigor
- Always supplement asymptotic p-values with bootstrap CI
- Report both; flag if CI crosses 0.4 threshold ambiguously

### NFR-03: Reuse
- `compute_partial_spearman()` function must match H-M1/H-M2 signature for controlled comparison
- Do NOT reimplement what exists — import/copy from H-M1/H-M2 code directory

### NFR-04: Logging
- Log: data load shape, N per pair, each ρ + CI + p, gate evaluation outcome, mechanism indicators

---

## 7. Dependencies

### 7.1 Python Packages
```
pingouin>=0.5.0
scipy>=1.10
numpy>=1.24
pandas>=1.5
matplotlib>=3.7
seaborn>=0.12
```

**Environment setup task:** `pip install pingouin scipy numpy pandas matplotlib seaborn`

### 7.2 Data Artifacts
- `data/model_scores.csv` — from H-M1 implementation (required, not created here)

### 7.3 Code Reuse (H-M1/H-M2)
- `compute_partial_spearman()` function
- `fisher_z_test_vs_threshold()` helper
- Existing DataFrame construction logic

---

## 8. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Code runs without error | 100% | No uncaught exceptions |
| Mechanism activated | All 6 indicators = True | verify_mechanism_activated() |
| Gate: AdvGLUE pair | ρ < 0.4 OR p ≥ 0.05 | fisher_z_test_vs_threshold(ρ_AdvGLUE) |
| Gate: ANLI pair | ρ < 0.4 OR p ≥ 0.05 | fisher_z_test_vs_threshold(ρ_ANLI) |
| Required figure | gate_metrics_comparison.png generated | File exists check |
| Results exported | results.json generated | File exists check |

---

## 9. File Structure

```
docs/youra_research/h-m3/
├── 03_prd.md              (this file)
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── 03_tasks.yaml
├── results.json
└── figures/
    ├── gate_metrics_comparison.png
    ├── rank_scatter_advglue.png
    ├── rank_scatter_anli.png
    ├── rank_reversal_heatmap.png
    ├── correlation_summary_table.png
    └── fisher_z_distribution.png

data/
└── model_scores.csv       (reused from H-M1)
```
