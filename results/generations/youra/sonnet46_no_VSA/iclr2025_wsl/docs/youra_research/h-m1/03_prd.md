# Product Requirements Document: H-M1
# Causal Attribution — Encoder Architecture Determines OrbitVar (≥4 OOM)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (Causal Step 1)
**Date:** 2026-08-03
**Author:** Anonymous
**Source:** 02c_experiment_brief.md
**Prerequisite:** H-E1 (VALIDATED — C2=1.002e-14, C3=8.905e-08, CISE=0.010333)

---

## 1. Executive Summary

H-M1 establishes the first causal link in the H-InvEnc-v1 chain: encoder architectural design (invariant vs non-invariant) causally determines OrbitVar by ≥ 4 orders of magnitude. The experiment reuses all H-E1 infrastructure, adding only CISE (C1) re-measurement under matched conditions, OrbitVar ratio computation, Wilcoxon signed-rank statistical tests, and the anti-confound gate (no order statistics in DeepSets φ). H-E1 C2/C3 OrbitVar values are loaded directly from saved results — no re-measurement. New code estimated < 80 lines.

---

## 2. Problem Statement

H-E1 demonstrated C2 and C3 achieve OrbitVar < 1e-6. H-M1 asks: is this difference **causally attributable** to encoder architecture? The causal argument requires (a) matched experimental conditions across all three encoders, (b) ruling out alternative confounders (order-statistics trick, permutation implementation differences), and (c) quantifying the gap as ≥ 4 orders of magnitude via ratio statistics.

**Gate Condition (MUST_WORK):** OrbitVar(C1) / OrbitVar(C2) > 1e4 AND OrbitVar(C1) / OrbitVar(C3) > 1e4, with Wilcoxon p < 0.001 on paired log10(OrbitVar) values.

---

## 3. Functional Requirements

### FR-1: Load H-E1 Prerequisite Results
- Load per-model OrbitVar arrays from `h-e1/results/orbit_var_results.json` (or equivalent saved H-E1 outputs)
- Extract: `orbit_vars_C2` [N_MODELS], `orbit_vars_C3` [N_MODELS]
- Verify loaded values match known means: C2 ≈ 1.002e-14, C3 ≈ 8.905e-08
- **Reuse H-E1 infrastructure:** `data_loader.py`, `permutation.py`, `encoder_c2.py`, `encoder_c3.py` via import from `../h-e1/code/`

### FR-2: CISE (C1) Re-measurement Under Matched Conditions
- Reuse sh1 `CISEEncoder` implementation
- Use exact same 100 models, same K=50 functional S_16³ permutations, same permutation code as H-E1
- Decision gate: if sh1 functional audit (||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6) was confirmed in H-E1, reuse CISE = 0.010333 as BUILD_ON; otherwise re-measure
- Consistency check: if re-measured, verify within 20% of 0.010333

### FR-3: OrbitVar Ratio Computation
- Per-model ratios: `ratios_C1_C2[i] = orbit_vars_C1[i] / (orbit_vars_C2[i] + EPS)` (EPS = 1e-30)
- Per-model ratios: `ratios_C1_C3[i] = orbit_vars_C1[i] / (orbit_vars_C3[i] + EPS)`
- Aggregate statistics: mean, median, geometric mean for each ratio
- Log10 orders-of-magnitude: `log10(mean_C1 / (mean_C2 + EPS))` and `log10(mean_C1 / (mean_C3 + EPS))`

### FR-4: Statistical Significance (Wilcoxon Signed-Rank)
- Paired Wilcoxon on log10-transformed per-model OrbitVar values
- Test: C1 > C2 (log scale), C1 > C3 (log scale), alternative='greater'
- Report: statistic, p-value for each test
- Gate: p < 0.001 for both tests

### FR-5: Anti-Confound Gate (No Order Statistics in φ)
- Unit test: run DeepSetsChannelEncoder on shuffled channel order → assert output identical (max diff < 1e-6)
- Code inspection: assert 'sort', 'argsort', 'topk' NOT in source of encoder_c2.phi
- Report: PASS/FAIL with max_diff value

### FR-6: Causal Attribution Summary
- Print matched-conditions confirmation (same 100 models, same K=50 perms, same perm code)
- Print OrbitVar table: C1/C2/C3 means, OOM columns, gate PASS/FAIL per row
- Save results to `h-m1/results/orbit_var_ratios.json`
- Save summary to `h-m1/results/h_m1_summary.csv`

### FR-7: Visualization
- **Figure 1:** Violin + scatter plot of log10(OrbitVar) per encoder (C1, C2, C3); annotate mean
- **Figure 2:** Histogram of per-model log10(C1/C2) and log10(C1/C3); vertical line at log10(1e4)=4
- **Figure 3:** Summary table (Encoder | Mean OrbitVar | OOM vs C1 | Gate)
- Save to `h-m1/figures/`

### FR-8: Gate Check Output
- Print: `Gate MUST_WORK: C1/C2 > 1e4: PASS/FAIL`
- Print: `Gate MUST_WORK: C1/C3 > 1e4: PASS/FAIL`
- Print: `Anti-confound gate: PASS/FAIL`
- Exit code 0 on PASS, 1 on FAIL

---

## 4. Data Specification

### Primary Dataset
| Field | Value |
|-------|-------|
| Name | ModelZooDataset CIFAR10-GS |
| Source | Zenodo DOI 10.5281/zenodo.6620868 |
| File | `dataset_cifar_small_hyp_rand.pt` |
| Size | 100 CNN models with CIFAR-10 test accuracy labels |
| Architecture | 3-conv (C=16), 1-dense, AdaptiveAvgPool2d |
| Access | **Reuse from H-E1** — already downloaded to `data/dataset_cifar_small_hyp_rand.pt` |
| Download | NOT required — reuse H-E1 data |

### H-E1 Prerequisite Files (Load Directly)
| File | Source | Purpose |
|------|--------|---------|
| `h-e1/results/orbit_var_results.json` | H-E1 output | orbit_vars_C2, orbit_vars_C3 per-model arrays |
| `data/dataset_cifar_small_hyp_rand.pt` | H-E1 download | 100 CNN models (if CISE re-measurement needed) |
| `data/index_dict.json` | H-E1 download | Weight index mapping |

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed = 1 (same as H-E1) for any permutation re-sampling
- Deterministic encoder forward passes

### NFR-2: Numerical Precision
- OrbitVar ratios computed in float64
- EPS = 1e-30 for division-by-zero guard

### NFR-3: Performance
- If CISE re-measurement: ~10-20 min CPU (100 models × 50 perms)
- If BUILD_ON reuse: < 5 min total
- Memory: < 2 GB

### NFR-4: Code Quality
- Single entry point: `python run_experiment.py`
- Imports from H-E1 code directory (`../h-e1/code/`) — no code duplication
- All 100 models must complete before reporting

---

## 6. Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| OrbitVar(C1) / OrbitVar(C2) > 1e4 | > 10,000× (~1e12 expected) | MUST_WORK |
| OrbitVar(C1) / OrbitVar(C3) > 1e4 | > 10,000× (~1e5 expected) | MUST_WORK |
| Wilcoxon C1 > C2 p-value | < 0.001 | MUST_WORK |
| Wilcoxon C1 > C3 p-value | < 0.001 | MUST_WORK |
| Anti-confound gate | No order stats in φ; max diff < 1e-6 | Secondary |
| CISE re-measurement consistency | Within 20% of 0.010333 | Secondary |
| Per-model ratios C1/C2 > 1e4 | > 99% of models | Secondary |
| Per-model ratios C1/C3 > 1e3 | > 95% of models | Secondary |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12.0        # already installed (H-E1)
numpy>=1.21.0        # already installed (H-E1)
scipy>=1.7.0         # already installed (H-E1) — Wilcoxon
matplotlib>=3.5.0    # already installed (H-E1)
```
No new packages required — all dependencies satisfied by H-E1 environment.

### 7.2 H-E1 Code Reuse (INCREMENTAL)
| Module | Import Path | What's Reused |
|--------|-------------|---------------|
| data_loader | `../h-e1/code/data_loader` | load_dataset, reconstruct_state_dict |
| permutation | `../h-e1/code/permutation` | sample_functional_permutations, apply_permutation |
| encoder_c2 | `../h-e1/code/encoder_c2` | DeepSetsChannelEncoder |
| encoder_c3 | `../h-e1/code/encoder_c3` | build_nfn_encoder, encode |

### 7.3 Pre-established Baselines (BUILD_ON)
- CISE OrbitVar = 0.010333 (sh1 PASS — may reuse if audit confirmed)
- C2 per-model OrbitVars = from H-E1 results JSON
- C3 per-model OrbitVars = from H-E1 results JSON

---

## 8. Out of Scope

- Re-implementing any H-E1 encoder (C2, C3)
- Re-running H-E1 OrbitVar measurement for C2/C3
- Training new models
- New encoder architectures beyond C1/C2/C3
- GPU optimization

---

## 9. Assumptions and Risks

| Assumption | Risk | Mitigation |
|------------|------|------------|
| H-E1 results JSON saved per-model arrays | Low | H-E1 validation passed; check file exists before run |
| sh1 CISE implementation available | Low | Fallback: re-implement CISE from H-E1 experiment brief spec |
| C3 ratio exactly exceeds 1e4 (5.1 OOM margin) | Low | Document exact ratio; PASS if ≥ 4 OOM |
| Anti-confound gate reveals order statistics | Very Low | Fix C2 implementation if triggered |

---

*stepsCompleted: [executive_summary, problem_statement, functional_requirements, data_specification, nfr, success_criteria, dependencies]*
