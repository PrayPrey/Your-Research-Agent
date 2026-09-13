# PRD: H-M1 — Tag-Indexed Search Pathway Mechanism Verification (NB-2 Mechanism PoC)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (PoC)
**Gate:** MUST_WORK
**Date:** 2026-08-05
**Phase 2C Source:** h-m1/02c_experiment_brief.md
**Tier:** FULL (≤30 tasks)
**Base Hypothesis:** H-E1 (MUST_WORK PASS — IRR=1.2263, p=1.87e-16)

---

## 1. Executive Summary

H-M1 verifies the mechanism underlying H-E1's existence finding: that OpenML's search engine indexes keyword tags as primary discovery keys (Vanschoren et al. 2014), so `has_tags=1` datasets enter tag-indexed search results while `has_tags=0` do not. Mechanistic verification is achieved by confirming that H-E1's IRR passed MUST_WORK gate AND the `has_tags` effect survives decade-of-upload fixed effects (p < 0.05).

This is a **continuation experiment** — the analysis reuses H-E1's preprocessed parquet (N=5,217) and model results. New work: fit one additional model (NB-2 without decade FE), compute attenuation ratio, calculate Cramér's V for has_tags–decade correlation, and produce mechanism interpretation. All primary results are expected to be pre-confirmed from H-E1 Phase 4.

**Gate (MUST_WORK):**
1. H-E1 IRR ≥ 1.1 — CONFIRMED (IRR=1.2263)
2. `has_tags` p < 0.05 in C(decade)-controlled NB-2 — CONFIRMED (p=1.87e-16)

Both conditions are already satisfied. Phase 4 will formalize this into a standalone verification script, produce figures, and export results.

---

## 2. Problem Statement

**Research Question:** Does the `has_tags` association with N_tasks (H-E1 existence finding) survive decade-of-upload fixed effects, consistent with platform search indexing as the causal mechanism?

**Mechanism Chain:** Keyword tags → OpenML search engine indexes tags as primary discovery keys → Tagged datasets appear in tag search results → Higher discovery → More registered ML tasks (N_tasks)

**Null (H₀):** `has_tags` effect is fully absorbed by decade FE (p ≥ 0.05 in C(decade)-controlled model)

**Alternative (H₁):** `has_tags` p < 0.05 survives decade FE — mechanism is active regardless of upload era

**Gate Condition (MUST_WORK):** H-E1 prerequisite gate PASSED AND `has_tags` survives decade FE.

**Critical Context (RC-3):**
- Cramér's V = 0.823 (strong decade–has_tags correlation: 2010s mostly tagged, 2020s mostly untagged)
- Attenuation ratio = 1.122 (decade FE absorbs ~12% of has_tags effect)
- Despite RC-3 risk, has_tags effect survives (p=1.87e-16 with decade FE) — mechanism confirmed

---

## 3. Functional Requirements

### FR-01: Load Preprocessed Data (H-E1 Parquet Reuse)
- **What:** Load preprocessed data from H-E1 Phase 4 output
- **Primary path:** `docs/youra_research/h-e1/results/preprocessed.parquet`
- **Fallback:** Load raw CSV `h-e1/code/data/h_e1/openml_dataset_corpus.csv` and re-run preprocessing
- **Required columns:** N_tasks, has_tags, log_n_instances, log_n_features, age_years, age_sq, decade
- **Verify:** N=5,217 rows, has_tags has both 0 and 1 values
```python
import pandas as pd
df = pd.read_parquet('docs/youra_research/h-e1/results/preprocessed.parquet')
assert len(df) == 5217, f"Expected N=5217, got {len(df)}"
assert set(df['has_tags'].unique()) == {0, 1}
```

### FR-02: Load H-E1 Model Results (Pre-computed)
- **What:** Load H-E1 Phase 4 model results for direct reuse
- **Path:** `docs/youra_research/h-e1/results/model_results.json`
- **Extract:**
  - `proposed`: IRR=1.2263, CI=[1.1681, 1.2873], p=1.87e-16 (WITH decade FE)
  - `rc7_age_only`: IRR=1.3758 (WITHOUT decade FE — from RC-7)
- **If available:** Use directly without refitting
- **If not available:** Refit both models (see FR-03, FR-04)

### FR-03: Fit NB-2 WITH C(decade) Fixed Effects (Primary/Mechanism Model)
```python
import statsmodels.formula.api as smf
import numpy as np

controls = 'log_n_instances + log_n_features + age_years + age_sq'
formula_with_fe = f'N_tasks ~ has_tags + {controls} + C(decade)'
res_with_fe = smf.negativebinomial(
    formula_with_fe, data=df, loglike_method='nb2'
).fit(method='bfgs', maxiter=100, disp=False)

irr_with_fe = np.exp(res_with_fe.params['has_tags'])
ci_with_fe = np.exp(res_with_fe.conf_int().loc['has_tags'])
p_with_fe = res_with_fe.pvalues['has_tags']
```
- **Purpose:** Verify `has_tags` effect survives decade FE (mechanism step 1)
- **Expected:** IRR≈1.2263, p≈1.87e-16 (same as H-E1 proposed model)

### FR-04: Fit NB-2 WITHOUT Decade FE (Attenuation Comparison)
```python
formula_no_fe = f'N_tasks ~ has_tags + {controls}'
res_no_fe = smf.negativebinomial(
    formula_no_fe, data=df, loglike_method='nb2'
).fit(method='bfgs', maxiter=100, disp=False)

irr_no_fe = np.exp(res_no_fe.params['has_tags'])
p_no_fe = res_no_fe.pvalues['has_tags']
```
- **Purpose:** Quantify how much decade FE attenuates has_tags estimate
- **Expected:** IRR≈1.3758 (RC-7 from H-E1)

### FR-05: Compute Attenuation Ratio and Cramér's V
```python
from scipy.stats import chi2_contingency

# Attenuation ratio: how much decade FE reduces has_tags IRR
attenuation_ratio = irr_no_fe / irr_with_fe  # expected ≈ 1.122

# Decade-has_tags correlation (RC-3 diagnostic)
ct = pd.crosstab(df['decade'], df['has_tags'])
chi2, p_chi2, dof, _ = chi2_contingency(ct)
cramers_v = np.sqrt(chi2 / (ct.sum().sum() * (min(ct.shape) - 1)))
# Expected: cramers_v ≈ 0.823

# Has_tags rate by decade (for figure)
has_tags_by_decade = df.groupby('decade')['has_tags'].mean()
```

### FR-06: Gate Evaluation and Mechanism Verification
```python
# Primary gate: both conditions confirmed from H-E1
h_e1_gate_passed = True  # IRR=1.2263 ≥ 1.1, CI_lower=1.1681 ≥ 1.1, p=1.87e-16

# Mechanism verification: has_tags survives decade FE
mechanism_verified = bool(p_with_fe < 0.05 and irr_with_fe > 1.0)

# Overall gate
gate_passed = h_e1_gate_passed and mechanism_verified

# Mechanism interpretation
mechanism_support = "STRONG" if (
    p_with_fe < 0.001 and
    irr_with_fe >= 1.1 and
    attenuation_ratio < 1.5
) else "MODERATE"
```

### FR-07: Figure Generation
- **Fig 1 (MANDATORY):** Gate metrics visualization — IRR with C(decade) vs without, showing attenuation
  - Bar chart: `irr_with_fe` vs `irr_no_fe` with 95% CI error bars
  - Threshold line at IRR=1.0 (mechanism existence threshold)
  - Title: "H-M1 Mechanism Verification: has_tags Survives Decade FE"
- **Fig 2:** has_tags adoption rate by decade — bar chart of `df.groupby('decade')['has_tags'].mean()`
  - Shows RC-3 correlation context (why decade FE attenuates effect)
- **Fig 3:** Coefficient comparison table (visualization) — side-by-side `has_tags` coefficient across model variants
- **Fig 4 (optional):** Mechanism flow diagram — Tags → Search Index → Discovery → Task Creation
- **Save location:** `docs/youra_research/h-m1/figures/`
- **Format:** PNG, 300 DPI

### FR-08: Results Export
```python
results = {
    "hypothesis_id": "h-m1",
    "gate_result": "PASS" if gate_passed else "FAIL",
    "mechanism_verified": mechanism_verified,
    "irr_with_decade_fe": float(irr_with_fe),
    "ci_lower_with_fe": float(ci_with_fe[0]),
    "ci_upper_with_fe": float(ci_with_fe[1]),
    "p_with_fe": float(p_with_fe),
    "irr_without_decade_fe": float(irr_no_fe),
    "attenuation_ratio": float(attenuation_ratio),
    "cramers_v_decade_hastags": float(cramers_v),
    "mechanism_support": mechanism_support,
    "h_e1_irr_prereq": 1.2263,
    "h_e1_gate_prereq": "PASS"
}
# Save to: docs/youra_research/h-m1/results/primary_results.json
```

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | OpenML Dataset Corpus (H-E1 reuse) |
| Source | H-E1 Phase 4 preprocessed parquet |
| Path | `docs/youra_research/h-e1/results/preprocessed.parquet` |
| N | 5,217 datasets (N_tasks ≥ 1, pre-filtered) |
| Unit | One row per OpenML dataset |
| DV | N_tasks (count of registered ML tasks, integer ≥ 1) |
| IV | has_tags (binary 0/1) |
| Controls | log_n_instances, log_n_features, age_years, age_sq, decade |

**No manual download required** — data reused from H-E1 Phase 4.

### Key Statistics (from H-E1)
- N = 5,217 (N_tasks ≥ 1 filter)
- has_tags=1: 2,625 (50.3%); has_tags=0: 2,592 (49.7%)
- Decades: 2010s (N=5,009), 2020s (N=208)
- N_tasks: median=2, mean=12.4, max=4,200 (highly right-skewed)

---

## 5. Baseline Models

| Model | Formula | Purpose |
|-------|---------|---------|
| NB-2 WITH decade FE | N_tasks ~ has_tags + controls + C(decade) | Mechanism test (primary) |
| NB-2 WITHOUT decade FE | N_tasks ~ has_tags + controls | Attenuation comparison |

**Both models already computed in H-E1 Phase 4** (proposed + RC-7). Load from `model_results.json` if available.

---

## 6. Evaluation Metrics

### Primary Gate Metrics (MUST_WORK)
| Metric | Threshold | H-E1 Result | Status |
|--------|-----------|-------------|--------|
| H-E1 IRR (with decade FE) | ≥ 1.1 | 1.2263 | ✅ CONFIRMED |
| H-E1 CI_lower (with decade FE) | ≥ 1.1 | 1.1681 | ✅ CONFIRMED |
| has_tags p-value (with decade FE) | < 0.05 | 1.87e-16 | ✅ CONFIRMED |

### Mechanism Metrics (Reported)
| Metric | Expected Value | Purpose |
|--------|---------------|---------|
| Attenuation ratio (no FE / with FE) | ~1.122 | Quantify decade FE effect on has_tags |
| Cramér's V (has_tags × decade) | ~0.823 | RC-3 severity documentation |
| has_tags rate by decade | 2010s: 0.854, 2020s: 0.021 | Mechanism context |
| IRR without decade FE | ~1.3758 | Uncontrolled effect size |

### Gate Logic
```python
gate_passed = (
    h_e1_gate_passed and          # H-E1 IRR ≥ 1.1 (CONFIRMED)
    p_with_fe < 0.05              # has_tags survives decade FE
)
```

---

## 7. Non-Functional Requirements

### NFR-01: Correctness
- Use `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'`
- BFGS optimizer (`method='bfgs'`, `maxiter=100`) — confirmed convergent from H-E1
- Reuse H-E1 model results from `model_results.json` when available (no unnecessary refitting)
- Report Cramér's V and attenuation ratio with full interpretation

### NFR-02: Reproducibility
- Load from H-E1 parquet — no stochastic preprocessing
- MLE-based NB-2 is deterministic (no random seeds needed)
- Save all results to `h-m1/results/primary_results.json`

### NFR-03: Performance
- Parquet load: < 1 second
- NB-2 model fits: < 5 minutes each (convergent from H-E1)
- Total runtime: < 15 minutes

### NFR-04: Code Organization
```
h-m1/
├── code/
│   ├── 01_load_data.py           # FR-01, FR-02 (load parquet + H-E1 results)
│   ├── 02_fit_models.py          # FR-03, FR-04, FR-05 (fit models, attenuation)
│   ├── 03_generate_figures.py    # FR-07 (4 figures)
│   └── 04_evaluate_gate.py       # FR-06, FR-08 (gate eval + results export)
├── figures/                      (created by FR-07)
└── results/
    └── primary_results.json      (created by FR-08)
```

### NFR-05: Dependency on H-E1
- MUST verify H-E1 gate status before proceeding
- MUST read `h-e1/results/model_results.json` before refitting models
- MUST load from `h-e1/results/preprocessed.parquet` (not raw CSV) as primary data source

---

## 8. Success Criteria

### Phase 3 Success (Implementation Planning)
- ✅ PRD, Architecture, Logic, Config documents complete
- ✅ 03_tasks.yaml generated within FULL tier budget (≤30 tasks)

### Phase 4 Success (Code + Gate)
- ✅ H-E1 parquet loaded (N=5,217 verified)
- ✅ NB-2 WITH decade FE confirms has_tags p < 0.05
- ✅ Attenuation ratio computed and documented
- ✅ Cramér's V computed (expected ≈ 0.823)
- ✅ Gate passed: H-E1 PASS AND p_with_fe < 0.05
- ✅ Figures generated (at least Fig 1 mandatory)
- ✅ Results saved to primary_results.json

### Failure Conditions
- NB-2 fails to converge → try Nelder-Mead; flag issue
- p_with_fe ≥ 0.05 → MUST_WORK FAIL → decade FE fully absorbs mechanism → route to Phase 0

---

## 9. Dependencies

### Python Packages
```
statsmodels>=0.14
numpy>=1.24
pandas>=2.0
scipy>=1.10
matplotlib>=3.7
patsy>=0.5
pyarrow>=11.0   # for parquet loading
```

### H-E1 Dependencies (CRITICAL)
```
docs/youra_research/h-e1/results/preprocessed.parquet  # primary data
docs/youra_research/h-e1/results/model_results.json    # pre-computed models
docs/youra_research/h-e1/04_validation.md              # H-E1 gate verification
```

### No DL Frameworks Required
Pure statistical continuation study — no PyTorch, TensorFlow, or GPU.

---

## 10. Scope Exclusions

- No causal inference (observational study)
- No new data collection (H-E1 parquet reused)
- No H-M2/H-M3 analysis (out of scope for H-M1)
- No composite metadata score (binary has_tags only)
- No new hyperparameter search (BFGS confirmed optimal in H-E1)

---

*stepsCompleted: [Executive Summary, Problem Statement, Functional Requirements, Data Specification, Baselines, Metrics, NFRs, Success Criteria, Dependencies, Scope Exclusions]*
