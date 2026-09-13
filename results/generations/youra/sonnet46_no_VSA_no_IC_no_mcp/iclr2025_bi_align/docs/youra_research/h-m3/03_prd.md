# Product Requirements Document: H-M3
# OLS Regression Slope Significance Test for Calibration-Alignment Divergence Gap

**Hypothesis ID:** H-M3
**Type:** MECHANISM (PoC — INCREMENTAL from H-M2)
**Tier:** FULL (max 30 tasks)
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Status:** Phase 3 — Implementation Planning
**Prerequisite:** H-M2 (VALIDATED, PASS — gap strictly positive at 5/5 high-KL levels, Spearman ρ=1.000, N=10)

---

## 1. Executive Summary

H-M3 formally tests whether the calibration-alignment divergence gap (RM_norm − gold_preference), validated in H-M2, grows linearly with KL optimization budget. Using the 10-observation dataset output by H-M2 (`h_m2_normalized_gap.csv`), the experiment fits an OLS linear regression (`gap ~ β₀ + β₁·KL_budget + ε`) and tests H0: β=0. Success requires β > 0, p < 0.05, and R² > 0.5. A bootstrap CI (n=10,000) supplements the parametric Wald t-test. Pre-computation from H-M2 data (near-perfect monotone growth, ρ=1.000) strongly predicts β ≈ 0.145/nat, R² ≈ 0.98, p << 0.05. No model training required; runtime < 5 seconds.

---

## 2. Problem Statement

H-M2 confirmed that the normalized divergence gap is strictly positive at all high-KL levels and grows monotonically (Spearman ρ=1.000). However, monotone rank correlation does not quantify the *rate* of growth or whether a linear relationship holds. H-M3 tests the MECHANISM formalization: does the calibration-alignment divergence gap increase with a significantly positive linear slope as a function of KL budget? Confirming a positive, significant β establishes that proxy-gold divergence compounds linearly (or super-linearly) with optimization pressure — a key ingredient for the H-BiAlign-v1 scaling law claim. Failure to achieve β > 0, p < 0.05, R² > 0.5 triggers ABANDON of H-BiAlign-v1.

---

## 3. Functional Requirements

### FR-1: Data Ingestion (Reuse H-M2 Output CSV)

- **FR-1.1:** Load `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv`
- **FR-1.2:** Validate required columns: `kl_budget`, `gap`
- **FR-1.3:** Validate N=10 rows with no NaN values
- **FR-1.4:** Sort by `kl_budget` ascending before analysis
- **FR-1.5:** Assert `kl_budget` range: [0.0, 8.0]; assert `gap` range: approx [-0.52, 0.62]
- **FR-1.6:** Extract arrays: `kl_values = df["kl_budget"].values` (shape 10,), `gap_values = df["gap"].values` (shape 10,)

### FR-2: Null Model (Baseline)

- **FR-2.1:** Fit intercept-only OLS: predict `mean(gap)` for all KL levels
- **FR-2.2:** Compute `SS_tot = sum((gap - mean(gap))²)` and `SS_res_null = SS_tot`
- **FR-2.3:** Store `mse_null = SS_res_null / N` — denominator for R² sanity check

### FR-3: OLS Linear Regression (Proposed Model)

- **FR-3.1:** Fit OLS: `gap ~ β₀ + β₁·kl_budget` using `scipy.stats.linregress`
- **FR-3.2:** Extract: `slope (β)`, `intercept (β₀)`, `r_value`, `p_value`, `std_err`
- **FR-3.3:** Compute `r_squared = r_value ** 2`
- **FR-3.4:** Compute `t_stat = slope / std_err`
- **FR-3.5:** Fit statsmodels OLS for full summary and 95% CI: `model = sm.OLS(gap, sm.add_constant(kl)).fit()`
- **FR-3.6:** Extract parametric 95% CI: `ci_parametric = model.conf_int(alpha=0.05)[1]` — (ci_low, ci_high) for slope
- **FR-3.7:** Run `model.summary()` and store text for reporting

### FR-4: Bootstrap Confidence Interval

- **FR-4.1:** Bootstrap with n_boot=10,000 iterations; resample with replacement; seed=42
- **FR-4.2:** For each bootstrap sample: fit `scipy.stats.linregress(kl[s], gap[s])`, store slope
- **FR-4.3:** Compute bootstrap 95% CI: `np.percentile(boot_slopes, [2.5, 97.5])`
- **FR-4.4:** Store `boot_slopes` array (shape 10000,) for histogram visualization
- **FR-4.5:** If both CI bounds > 0 → report strong evidence; if CI straddles 0 → note bootstrap uncertainty

### FR-5: Gate Condition Verification

- **FR-5.1 (Primary Gate 1):** Assert `slope > 0` — positive linear relationship
- **FR-5.2 (Primary Gate 2):** Assert `p_value < 0.05` — Wald t-test significant
- **FR-5.3 (Primary Gate 3):** Assert `r_squared > 0.5` — linear model explains majority of variance
- **FR-5.4:** H-M3 gate PASS condition: FR-5.1 AND FR-5.2 AND FR-5.3 all satisfied
- **FR-5.5:** On FAIL: print diagnostic identifying which condition failed; suggest checking data file path and H-M2 run completion
- **FR-5.6:** Failure response = ABANDON H-BiAlign-v1; route to Phase 0

### FR-6: Mechanism Activation Verification

- **FR-6.1:** Call `verify_mechanism_activated(results)` before gate check
- **FR-6.2:** Verify: `n == 10`, `slope is not NaN`, `0 ≤ p_value ≤ 1`, `0 ≤ r_squared ≤ 1`, `ci_bootstrap is not None`
- **FR-6.3:** Raise `RuntimeError` if any indicator fails — hard stop before gate evaluation

### FR-7: Secondary Analysis (Gao et al. Preliminary Check)

- **FR-7.1:** Attempt to load `docs/youra_research/h-m4/gao_digitized.csv` if file exists (optional)
- **FR-7.2:** If file exists and has columns `kl_budget`, `gap`: run same OLS regression; report slope sign only
- **FR-7.3:** Gate decision based solely on Coste et al. data (H-M2 output); Gao result is informational

### FR-8: Visualization

- **FR-8.1 (Mandatory):** Gate metrics bar chart — β, p_value, R² vs. thresholds (0, 0.05, 0.5)
- **FR-8.2:** Regression scatter plot — scatter (KL, gap) + OLS best-fit line + 95% CI band; annotate β, R², p
- **FR-8.3:** Residuals plot — residuals vs. fitted values; horizontal zero line
- **FR-8.4:** Bootstrap distribution histogram — 10,000 slopes; mark observed β and 95% CI bounds
- **FR-8.5:** Save all figures to `docs/youra_research/h-m3/figures/` (auto-created)

### FR-9: Reporting

- **FR-9.1:** Print structured pass/fail report to stdout with all metrics
- **FR-9.2:** Save results JSON to `docs/youra_research/h-m3/results/h_m3_results.json`
- **FR-9.3:** JSON must include: `slope`, `intercept`, `r_squared`, `p_value`, `std_err`, `t_stat`, `ci_parametric`, `ci_bootstrap`, `n`, `gate_pass`, `gate_reason`, `statsmodels_summary`
- **FR-9.4:** Exit code 0 if gate passes, 1 if gate fails

---

## 4. Data Specification

### 4.1 Primary Dataset: H-M2 Output CSV

| Field | Value |
|-------|-------|
| Name | Coste2023 Calibration-Alignment Divergence Gap (H-M2 validated output) |
| Source | `docs/youra_research/h-m2/results/h_m2_normalized_gap.csv` |
| Type | Local file (no download — produced by H-M2 Phase 4) |
| Acquisition | Auto-accessible — H-M2 PASS output; no manual download |
| N | 10 KL-level observations |
| Columns | `kl_budget` (float, nats), `rm_score` (float), `rm_norm` (float, [0,1]), `gold_preference` (float), `gap` (float = rm_norm − gold_preference) |
| Splits | Single time-series; no train/val/test split |
| Missing values | None (confirmed in H-M2 validation) |

**Loading:**
```python
import pandas as pd
df = pd.read_csv("docs/youra_research/h-m2/results/h_m2_normalized_gap.csv")
kl_values  = df["kl_budget"].values   # shape (10,)
gap_values = df["gap"].values          # shape (10,)
```

**Note:** No manual data acquisition required. H-M2 result file is the sole required input.

### 4.2 Secondary Dataset: Gao et al. (Optional)

| Field | Value |
|-------|-------|
| Name | Gao et al. 2023 RM/Gold proxy data (if digitized) |
| Source | `docs/youra_research/h-m4/gao_digitized.csv` (may not exist yet) |
| Acquisition | Optional: WebPlotDigitizer from arXiv 2210.10760 figures; or check github.com/tlc4418/llm_optimization for raw data |
| Role | Secondary sign-check only; not used for gate decision |

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Fixed seed=42 for bootstrap; OLS is deterministic |
| Dependencies | scipy>=1.10, statsmodels>=0.14, numpy>=1.24, matplotlib>=3.7, pandas>=2.0 |
| Runtime | < 5 seconds (10 OLS fits + 10,000 bootstrap iterations on N=10; no GPU) |
| File organization | All outputs under `docs/youra_research/h-m3/` |
| Python version | ≥3.9 |
| H-M2 dependency | Requires `h-m2/results/h_m2_normalized_gap.csv` to exist; fail early if missing |
| Environment | Reuse youra-h-m2 conda env (Python 3.10, all libs already installed) |

---

## 6. Success Criteria

| Criterion | Target |
|-----------|--------|
| Code runs without error | Required |
| `slope > 0` | PASS (primary gate 1) |
| `p_value < 0.05` | PASS (primary gate 2) |
| `r_squared > 0.5` | PASS (primary gate 3) |
| Mechanism activation verified | Required (verify_mechanism_activated passes) |
| All 4 figures generated | Required |
| Results JSON saved | Required |

**Expected Performance:** slope ≈ 0.145, R² ≈ 0.98, p << 0.001 (based on H-M2 monotone data, ρ=1.000)

**H-M3 Gate:** MUST_WORK — all three conditions required; any failure = ABANDON H-BiAlign-v1

---

## 7. Dependencies

### 7.1 Python Packages

```
scipy>=1.10.0
statsmodels>=0.14.0
numpy>=1.24.0
matplotlib>=3.7.0
pandas>=2.0.0
```

### 7.2 External Repositories (Reference Only)

| Repo | Purpose |
|------|---------|
| scipy/scipy | `stats.linregress` — OLS slope, p-value, R² |
| statsmodels/statsmodels | `OLS.fit()` — full summary, `conf_int()` — 95% CI |
| tlc4418/llm_optimization | Coste et al. companion code — check for raw data as alternative to H-M2 CSV |

### 7.3 Reference Papers

| Paper | arXiv | Role |
|-------|-------|------|
| Coste et al. 2023 | 2310.02743 | Source of primary data (via H-M1/H-M2 digitization pipeline) |
| Gao et al. 2023 | 2210.10760 | Motivation: proxy ∝ √KL; secondary dataset for sign check |

### 7.4 H-M2 Dependency

H-M3 builds directly on H-M2:
- Input: `h-m2/results/h_m2_normalized_gap.csv` (gap time-series, N=10)
- Reuse environment: youra-h-m2 (Python 3.10, all required packages installed)
- Architecture pattern: same `load → analyse → visualize → report → exit` pipeline as H-M2
- Code pattern: mirror H-M2's `src/` module structure with regression-specific analysis layer

---

## 8. Out of Scope

- Neural network training or fine-tuning
- Re-digitization of Coste et al. figures (H-M1/H-M2 already validated)
- Cross-scale replication (reserved for H-M4)
- Non-linear regression models (H-M3 tests linear hypothesis only)
- Secondary dataset (Gao et al.) gate contribution — informational only
- RLHF fine-tuning or RM training

---

Applied: MECHANISM PoC template — extends H-M2 monotone gap confirmation with OLS regression slope significance formalization
Codebase Analysis (Serena): H-M2 code at h-m2/code/src/ fully available; same pipeline pattern reused with regression-specific analysis module
