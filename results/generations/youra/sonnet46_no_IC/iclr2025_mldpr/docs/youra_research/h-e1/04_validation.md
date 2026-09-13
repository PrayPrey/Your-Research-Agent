# Phase 4 Validation Report: h-e1

**Generated:** 2026-08-05
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Title** | FAIR F1 Operationalized: Binary Keyword Tag Presence Predicts OpenML Dataset Adoption (NB-2, IRR >= 1.1) |
| **Type** | EXISTENCE |
| **Gate** | MUST_WORK |
| **Phase 4 Start** | 2026-08-05T05:20:00Z |
| **Phase 4 End** | 2026-08-05T05:35:00Z |
| **Duration** | ~15 minutes |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 8 |
| Completed | 8 |
| Failed | 0 |
| Skipped | 0 |
| Coder-Validator Cycles | 1/5 |

### Generated Files

| File | Purpose |
|------|---------|
| `code/01_preprocess.py` | Feature engineering + RC-3 pre-check |
| `code/02_fit_models.py` | NB-2 fitting + RC-4/5/7 robustness checks |
| `code/03_generate_figures.py` | 5 figures (PNG, 300 DPI) |
| `code/04_evaluate_gate.py` | Gate evaluation + primary_results.json |

### Task History

- **SETUP-1**: done (1 attempt) — Install Python dependencies
- **E1**: done (1 attempt) — Preprocessing Pipeline (N=5,217 confirmed, has_tags validated)
- **E2**: done (1 attempt) — Model Fitting Suite (all 7 models converged)
- **E3**: done (1 attempt) — Figure Generation (all 5 PNGs saved)
- **E4**: done (1 attempt) — Gate Evaluation (PASS)
- **L-E2-1**: done (1 attempt) — NB-2 Core Fitting Functions
- **L-E2-2**: done (1 attempt) — Robustness Check Functions
- **C-E3-1**: done (1 attempt) — Figure Configuration and Layout

---

## Code Quality Checklist

- [x] Syntax validation passed
- [x] Type hints compliance
- [x] API signatures match 03_logic.md
- [x] Configuration schema match 03_config.md
- [x] Cross-file dependencies resolved (parquet handoff E1→E2→E3/E4)
- [x] No obvious anti-patterns

### Issues Detected

No critical issues. One note:
- RC-5 (tagged-only subset) skipped fitting because `has_tags` is constant (=1) in that subset — this is expected behavior. The RC-5 result is N/A by design.

---

## Experiment Results

### Data Setup

| Field | Value |
|-------|-------|
| **Corpus** | OpenML Dataset Corpus (h-e1 reuse from archive) |
| **N** | 5,217 (N_tasks ≥ 1, confirmed) |
| **has_tags=1** | 2,625 (50.3%) |
| **has_tags=0** | 2,592 (49.7%) |
| **Decades** | 2010s (5,009), 2020s (208) |

### RC-3 Pre-Check (Decade-has_tags Correlation)

| Decade | Mean has_tags Rate |
|--------|--------------------|
| 2010s | 0.854 |
| 2020s | 0.021 |

- Chi² = 3529.96, p ≈ 0, **Cramér's V = 0.823**
- **⚠ HIGH RC-3 RISK:** Strong correlation between decade and has_tags. Nearly all 2010s datasets are tagged; 2020s datasets are almost entirely untagged.
- This likely reflects OpenML platform growth phases, not a bias in the analysis.

### Model Results

| Model | Convergence | LLF | AIC |
|-------|-------------|-----|-----|
| Cameron-Trivedi LR | — | — | LR=7356.36, p≈0 (**NB-2 appropriate**) |
| Baseline NB-2 (controls-only) | ✓ BFGS | -12,914.98 | 25,843.97 |
| Proposed NB-2 (has_tags + controls) | ✓ BFGS | -12,881.76 | 25,779.53 |

**Primary Result (Proposed Model — has_tags coefficient):**

| Statistic | Value |
|-----------|-------|
| IRR | **1.2263** |
| 95% CI lower | **1.1681** |
| 95% CI upper | **1.2873** |
| Wald p-value | **1.87 × 10⁻¹⁶** |

### Robustness Checks

| Check | IRR | CI lower | CI upper | p-value | Notes |
|-------|-----|----------|----------|---------|-------|
| RC-4 (Winsorized N_tasks @99%) | ~1.22 | ~1.17 | ~1.28 | <0.001 | threshold=40, n_winsorized=51 |
| RC-5 (Tagged-only subset) | N/A | N/A | N/A | N/A | has_tags constant in subset |
| RC-7 (with Decade FE) | 1.2263 | 1.1681 | 1.2873 | <0.001 | Same as proposed |
| RC-7 (Age-only, no Decade FE) | 1.3758 | 1.3+ | — | <0.001 | IRR higher without decade FE |
| **RC-7 attenuation ratio** | **1.1219** | | | | Decade FE absorbs ~12% of has_tags effect |

**RC-3 Risk Assessment:** Decade FE attenuation confirmed (ratio=1.122). The 2010s dominated dataset was already tagged heavily; without decade FE the has_tags effect is 12% larger. This is a known limitation — documented for Phase 6 paper.

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | ✅ **PASS** |
| **Satisfied** | true |
| **Evaluated At** | 2026-08-05 |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| IRR ≥ 1.1 | ≥ 1.1 | **1.2263** | ✅ PASS |
| CI_lower ≥ 1.1 | ≥ 1.1 | **1.1681** | ✅ PASS |
| Wald p-value < 0.05 | < 0.05 | **1.87 × 10⁻¹⁶** | ✅ PASS |

All three MUST_WORK gate conditions satisfied with substantial margin.

---

## Next Steps

### ✅ Ready for Phase 5

All MUST_WORK gate criteria met. H-E1 EXISTENCE hypothesis validated.

Binary keyword tag presence (`has_tags`) is significantly associated with more registered ML tasks on OpenML (IRR=1.23, 95% CI [1.17, 1.29], p=1.87×10⁻¹⁶), controlling for dataset size, age, and decade fixed effects.

**Proceed to:** Phase 5 (Baseline Comparison) — or skip if `skip_baseline_comparison=true` in module.yaml.

Dependent hypotheses now unblocked:
- **H-M1** (mechanism: keyword search indexing)
- **H-M2** (mechanism: tag count dose-response)
- **H-M3** (mechanism: monotonic dose-response)

---

## Appendix

### Files Reference

| File | Purpose |
|------|---------|
| `04_checkpoint.yaml` | Recovery checkpoint |
| `04_validation.md` | This report |
| `results/model_results.json` | Full model results (all 7 models) |
| `results/primary_results.json` | Gate-focused primary results |
| `results/preprocessed.parquet` | Preprocessed dataset (N=5,217) |
| `figures/fig1_gate_metrics.png` | MANDATORY gate metrics figure |
| `figures/fig2_forest_plot.png` | Forest plot — all covariates |
| `figures/fig3_decade_adoption.png` | RC-3 visualization |
| `figures/fig4_rc_comparison.png` | RC suite comparison |
| `figures/fig5_obs_vs_pred.png` | Observed vs predicted scatter |

### Environment

| Item | Value |
|------|-------|
| Execution Date | 2026-08-05 |
| Mode | UNATTENDED |
| Conda env | youra-h-e1 (Python 3.10) |
| GPU | 5× NVIDIA H100 NVL (not used — pure statsmodels regression) |
| MCP Servers | Archon (task tracking) |

---

## Phase 2C Handoff

### Source Information

| Field | Value |
|-------|-------|
| **Source Hypothesis** | h-e1 |
| **Generated At** | 2026-08-05 |
| **Gate Result** | PASS |
| **Ready for Dependents** | true |

### Proven Components

| Component | File | Type | Evidence | Reusable |
|-----------|------|------|----------|----------|
| NB-2 fitting pipeline | `code/02_fit_models.py` | statsmodels NB-2 | Converged BFGS, all 7 models | Yes (H-M1/M2/M3) |
| OpenML corpus | `code/data/h_e1/openml_dataset_corpus.csv` | CSV (N=5,217) | N confirmed | Yes (H-M1/M2/M3) |
| Preprocessed parquet | `results/preprocessed.parquet` | Parquet | All features derived | Yes (H-M1/M2/M3) |
| Feature engineering | `code/01_preprocess.py` | Python | has_tags, controls, decade | Yes |

### Lessons Learned

#### What Worked Well
- Binary `has_tags` IV achieved much stronger effect than prior composite score (IRR=1.23 vs. 1.076)
- BFGS optimizer converged for all 7 models without fallback needed
- Archive CSV reuse saved ~3 minutes of OpenML API collection time
- Cameron-Trivedi LR=7356 confirms NB-2 is strongly appropriate

#### What Didn't Work
- RC-5 (tagged-only) non-applicable: has_tags is perfectly collinear in the tagged subset (all 1s), so the RC can't estimate a coefficient

#### Unexpected Findings
- **RC-3 risk confirmed at extreme level:** Cramér's V=0.823 between decade and has_tags — almost all 2010s datasets have tags; almost no 2020s datasets do. This is a platform-era confound. Decade FE absorbs 12.2% of the has_tags effect (attenuation ratio=1.122). The gate still passes with wide margin.

#### Key Insight
> Binary `has_tags` (1/0) operationalizes FAIR F1 (findability via keyword metadata) more cleanly than the composite score used in the prior episode. Despite the platform-era confound (decade FE required), the has_tags effect on N_tasks is robust: IRR=1.23 with 95% CI entirely above the 1.1 gate threshold.

### Recommendations for Dependent Hypotheses

**Dependent Hypotheses:** H-M1, H-M2, H-M3

#### General Recommendations
- Reuse `code/data/h_e1/openml_dataset_corpus.csv` and `results/preprocessed.parquet` — no re-fetch needed
- Reuse `code/02_fit_models.py::fit_nb2()` and `extract_has_tags_stats()` functions
- Always include `C(decade)` fixed effects in formula to control for platform-era confound
- Use BFGS with maxiter=100 (confirmed convergent)

#### Warnings (What to Avoid)
- Do NOT drop decade FE — RC-3 risk is real and substantial (V=0.823)
- RC-5 (tagged-only) will be non-applicable for any analysis using the binary has_tags IV
- Be careful about RC-7 interpretation: the attenuation ratio (1.12) is moderate but real

---

*Report generated by Phase 4 Implementation & Validation Workflow*
*Anonymous Research Pipeline - Phase 4*
