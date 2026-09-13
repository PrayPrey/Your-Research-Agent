# Product Requirements Document: H-M2
## DPO vs PPO/SFT Logit Delta Variance in Low-Margin Regions — Method-Specific Quintile Analysis

**Hypothesis ID:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-M1 infrastructure)
**Date:** 2026-03-17
**Author:** Anonymous
**Phase 2C Source:** h-m2/02c_experiment_brief.md
**Base Hypothesis:** H-M1 (COMPLETED, gate PASS — anisotropy ratio 2.9–4.6x confirmed)
**Tier:** FULL (max 30 tasks)
**Gate:** SHOULD_WORK (continues pipeline even on null result)

---

## 1. Executive Summary

This experiment tests whether DPO alignment produces significantly higher logit delta variance specifically in low-margin (bottom quintile) items compared to PPO/SFT alignment, after controlling for KL divergence. It is a pure statistical analysis pipeline — no model inference required. The H-E1 cache (h-e1/cache/) provides all pre-computed logits, margins, and KL divergences.

**Scientific Claim:** DPO's log-odds objective (L_DPO ∝ log σ(β·log ratio)) amplifies option-probability differences more directly in low-confidence regions than PPO's KL-penalized gradient (Xu et al. [2024]), producing higher per-item logit delta variance in Q1 (bottom margin quintile).

**Key Reuse:** H-M1's `compute_logit_delta` function (45 tests validated) + H-E1 cache (no re-inference needed). Only ~60–80 lines of new quintile variance analysis code required.

---

## 2. Problem Statement

H-M1 confirmed that alignment-induced logit deltas are non-isotropic (anisotropy ratio 2.9–4.6x). H-M2 now tests whether this non-isotropy concentrates specifically in low-margin items and whether this concentration is method-specific: DPO more concentrated in Q1 than SFT/PPO.

**Scientific Question:** Does DPO produce significantly higher logit delta variance in the bottom margin quintile compared to PPO/SFT, after KL divergence control?

**Theoretical Basis:** Xu et al. [2024] — DPO's log-odds objective directly amplifies existing option-probability differences; PPO's KL penalty globally constrains distributional drift, spreading variance more uniformly. In low-margin items (where top-1 and top-2 probabilities are nearly equal), this DPO amplification effect should be most pronounced.

**Limitations (Documented):** PPO pairs (pair1: tulu-2-ppo-7b 404 error, pair3: pythia-1B tokenizer error) are unavailable. Primary comparison is DPO (pair2) vs SFT (pair4) — a weaker but valid proxy for the DPO vs PPO distinction.

---

## 3. Goals and Non-Goals

### Goals
- Stratify MCQ items into 5 quintiles by pre-alignment confidence margin (z-scored)
- Compute KL-residualized logit delta variance per quintile for pair2 (DPO) and pair4 (SFT)
- Test: DPO Q1 variance > SFT Q1 variance (Welch's t, one-tailed, p < 0.05)
- Assess cross-benchmark consistency (≥ 2 of 3 datasets)
- Produce Q1–Q5 trend visualization showing Q1 specificity
- Document as null result if not significant (pipeline continues)

### Non-Goals
- No model inference (all logits are cached from H-E1)
- No model training
- No comparison with H-M1 anisotropy ratio directly
- No PPO true pairs (documented limitation)
- No hyperparameter search

---

## 4. Functional Requirements

### FR-1: Cache Loading
- **FR-1.1:** Load H-E1 cache files: `h-e1/cache/pair2_{dataset}_test_logprobs.pkl` for pair2 (DPO, tulu-2-7b) and pair4 (SFT, pythia-6.9b)
- **FR-1.2:** Extract arrays: `base_logprobs` (N, 4), `aligned_logprobs` (N, 4), `margin` (N,), `flip_indicator` (N,), `kl_div` (N,)
- **FR-1.3:** Validate cache integrity: check for NaN values, verify shape (N, 4) for logprobs, (N,) for margin/kl
- **FR-1.4:** Fail early with clear error if cache missing or corrupted
- **FR-1.5:** Datasets: MMLU (N=14,042), TruthfulQA (N=817), ARC-Challenge (N=1,172)

### FR-2: Quintile Stratification
- **FR-2.1:** Z-score margin within each dataset-pair combination: `margin_z = scipy.stats.zscore(margin)`
- **FR-2.2:** Compute quintile boundaries: `boundaries = np.percentile(margin_z, [0, 20, 40, 60, 80, 100])`
- **FR-2.3:** Assign items to quintiles 0–4: `quintile_labels = np.digitize(margin_z, boundaries[1:-1])`
- **FR-2.4:** Verify minimum N per quintile ≥ 100; log count per quintile; skip quintile if < 100 items
- **FR-2.5:** Expected per-quintile N at MMLU: ~2,808 items (stable for variance estimation)

### FR-3: KL-Residualized Variance Computation
- **FR-3.1:** Compute per-item 4D logit delta: `delta = aligned_logprobs - base_logprobs` shape (N, 4)
- **FR-3.2:** Compute per-item scalar delta variance: `delta_var = np.var(delta, axis=1)` shape (N,)
- **FR-3.3:** For each quintile q: extract `delta_var_q` and `kl_q` for items in quintile q
- **FR-3.4:** KL residualization via OLS: fit `delta_var_q ~ kl_q`, compute residuals `delta_var_q - (slope * kl_q + intercept)`
- **FR-3.5:** If quintile has < 10 items for OLS: use raw `delta_var_q` without residualization (log warning)
- **FR-3.6:** Per-quintile variance: `quintile_variances[q] = np.var(residuals)`
- **FR-3.7:** Output shape: `quintile_variances` (5,) per pair per dataset

### FR-4: Statistical Testing
- **FR-4.1:** Primary test — Welch's t-test (one-tailed): DPO Q1 variance > SFT Q1 variance
  - `t_stat, p_two = scipy.stats.ttest_ind(dpo_q1_residuals, sft_q1_residuals, equal_var=False)`
  - `p_one_tailed = p_two / 2` (directional: DPO > SFT)
- **FR-4.2:** Effect size — Cohen's d: `cohens_d = (mean(dpo_q1_residuals) - mean(sft_q1_residuals)) / pooled_std`
- **FR-4.3:** Variance ratio: `q1_variance_ratio = quintile_variances_dpo[0] / quintile_variances_sft[0]`
- **FR-4.4:** Cross-benchmark gate: significant (p < 0.05 one-tailed) on ≥ 2 of 3 datasets
- **FR-4.5:** Bootstrap CI (5,000 replicates) for variance ratio confidence interval
- **FR-4.6:** Report per-dataset: t_stat, p_one_tailed, cohens_d, q1_variance_ratio, bootstrap CI

### FR-5: Ablation Variants
- **FR-5.1:** Full model (KL-controlled): primary SHOULD_WORK test (FR-3 + FR-4)
- **FR-5.2:** No KL control: raw delta_var used without residualization — tests if KL confounds result
- **FR-5.3:** Q1-only analysis: primary gate criterion (Welch's t on Q1 residuals only)
- **FR-5.4:** Q1–Q5 trend: compute variance ratio (DPO/SFT) for all quintiles to show Q1 specificity
- **FR-5.5:** Per-dataset analysis: separate results for MMLU, TruthfulQA, ARC-Challenge

### FR-6: Mechanism Verification
- **FR-6.1:** Implement `verify_mechanism_activated(results)` checking:
  - `quintile_stratification_ok`: all quintile counts ≥ 100
  - `variance_computed`: dpo_q1_variance > 0 and sft_q1_variance > 0
  - `kl_controlled`: kl_residualization_applied == True
  - `test_executed`: "p_value" in results
- **FR-6.2:** Log quintile counts at INFO level: "Quintile stratification: Q1 has N={n} items (expected ~2800)"
- **FR-6.3:** Log tensor shapes: "delta shape: ({N}, 4), quintile_variances shape: (5,)"
- **FR-6.4:** Run isotropic sanity check: variance across quintiles for synthetic Gaussian Δ (expected: flat trend)

### FR-7: Visualization (Mandatory)
- **FR-7.1 (Gate Metric):** Bar chart — DPO vs SFT Q1 variance (KL-residualized) with p-value annotation per dataset
- **FR-7.2:** Quintile trend line chart: DPO vs SFT variance ratio Q1→Q5 across all 3 datasets
- **FR-7.3:** KL divergence scatter: delta_var vs kl_div colored by quintile (validates residualization)
- **FR-7.4:** Per-benchmark Q1 variance: grouped bar (MMLU/TQA/ARC × DPO/SFT) with error bars
- **FR-7.5:** Variance ratio heat map or line plot: DPO/SFT ratio across Q1–Q5 × dataset
- **FR-7.6:** All figures saved to `h-m2/figures/` as both `.pdf` and `.png`

---

## 5. Data Specification

### Cache Source (H-E1, No Re-inference)

| Cache File | Pair | Dataset | N items |
|-----------|------|---------|---------|
| `h-e1/cache/pair2_mmlu_test_logprobs.pkl` | DPO (tulu-2-7b) | MMLU | 14,042 |
| `h-e1/cache/pair2_truthfulqa_test_logprobs.pkl` | DPO (tulu-2-7b) | TruthfulQA | 817 |
| `h-e1/cache/pair2_arc_test_logprobs.pkl` | DPO (tulu-2-7b) | ARC-Challenge | 1,172 |
| `h-e1/cache/pair4_mmlu_test_logprobs.pkl` | SFT (pythia-6.9b) | MMLU | 14,042 |
| `h-e1/cache/pair4_truthfulqa_test_logprobs.pkl` | SFT (pythia-6.9b) | TruthfulQA | 817 |
| `h-e1/cache/pair4_arc_test_logprobs.pkl` | SFT (pythia-6.9b) | ARC-Challenge | 1,172 |

**Cache Format:**
```python
cache = pickle.load(open(cache_path, "rb"))
# cache["base_logprobs"]: np.array (N, 4) — 4-class MCQ option log-probs (base model)
# cache["aligned_logprobs"]: np.array (N, 4) — 4-class MCQ option log-probs (aligned model)
# cache["margin"]: np.array (N,) — z-scored confidence margin (pre-alignment)
# cache["flip_indicator"]: np.array (N,) — binary argmax flip labels
# cache["kl_div"]: np.array (N,) — per-item KL divergence (base || aligned)
```

### Dataset Properties

| Dataset | N | Quintile N (expected) | Min acceptable per quintile |
|---------|---|----------------------|---------------------------|
| MMLU | 14,042 | ~2,808 | 100 |
| TruthfulQA | 817 | ~163 | 100 |
| ARC-Challenge | 1,172 | ~234 | 100 |

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- No GPU required — pure numpy/scipy statistical analysis
- Expected runtime: < 2 minutes total (no inference)
- Memory footprint: ~500MB for all 6 cache files loaded simultaneously

### NFR-2: Reproducibility
- Fixed seed: 1 (consistent with H-E1/H-M1)
- Bootstrap CI: `np.random.seed(1)` before bootstrap loop
- All results saved to `h-m2/experiment_results.json`

### NFR-3: Error Handling
- Cache file missing → FAIL with message: "Cache file {path} not found. Run H-E1 Phase 4 first."
- kl_div missing from cache → WARN + skip KL control: "kl_div not in cache — skipping KL residualization"
- Quintile < 100 items → WARN + skip that quintile: "Q{q} has only {n} items — skipping variance estimate"
- NaN in delta → FAIL: "NaN values in logit delta — cache may be corrupted"
- p ≥ 0.05 → NOT a code error; gate SHOULD_WORK → document null result and continue

### NFR-4: Infrastructure Reuse
- Conda environment: `youra-h-e1` (Python 3.10, H100 NVL)
- Import `compute_logit_delta` from `h-m1/code/analysis_anisotropy.py` if available; else reimplement inline
- No new model downloads required

---

## 7. Evaluation Metrics & Success Criteria

### Primary Metrics (Gate: SHOULD_WORK)

| Metric | Definition | Success Threshold |
|--------|-----------|-------------------|
| Q1 variance ratio | DPO Q1 var / SFT Q1 var (KL-residualized) | Ratio > 1.0 (directional) |
| Q1 interaction p-value | Welch's t one-tailed p | p < 0.05 |
| KL-controlled interaction | Residualized test | Significant after KL removal |
| Cross-benchmark | Significant on ≥ datasets | ≥ 2 of 3 benchmarks |

### Gate Evaluation

| Result | Condition | Action |
|--------|-----------|--------|
| **PASS** | DPO Q1 var > SFT Q1 var, p < 0.05 (one-tailed), KL-controlled, ≥ 2/3 benchmarks | Continue → H-M3 |
| **FAIL** | p ≥ 0.05 OR direction reversed | Document null result → Continue → H-M3 |

### Secondary Metrics

| Metric | Definition | Purpose |
|--------|-----------|---------|
| Quintile trend slope | Variance ratio decrease from Q1→Q5 | Q1 specificity of DPO effect |
| Cohen's d | Standardized Q1 variance difference | Effect size estimation |
| Bootstrap 95% CI | Confidence interval on Q1 variance ratio | Uncertainty quantification |
| No-KL-control comparison | Raw vs residualized result | KL confound assessment |

### Expected Performance
- H-M1 showed DPO anisotropy ratio 2.9x vs SFT 4.6x (overall); H-M2 tests Q1-specifically
- Expected Q1 variance ratio (DPO/SFT): > 1.5 (from Xu et al. [2024] theoretical prediction)
- Cross-benchmark consistency expected on MMLU + ARC at minimum

---

## 8. Dependencies

### 8.1 Python Packages
```
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
statsmodels>=0.14.0  # Optional — for mixed-effects model
pyyaml>=6.0
tqdm>=4.65.0
```

### 8.2 Infrastructure Dependencies
- **H-E1 cache:** `h-e1/cache/` — 6 pickle files (pair2 × 3 datasets + pair4 × 3 datasets)
- **H-M1 code:** `h-m1/code/analysis_anisotropy.py` — `compute_logit_delta` function (optional import)
- **Conda environment:** `youra-h-e1` (Python 3.10, already installed from H-E1/H-M1)
- **No GPU required** for analysis phase

### 8.3 Theoretical References
- Xu et al. [2024]: DPO distribution shift — log-odds amplification in low-margin regions
- H-M1 proven implementation: anisotropy analysis codebase as starting point

---

## 9. Ablation Variants Summary

| Variant | Description | FR Reference |
|---------|-------------|-------------|
| KL-controlled (primary) | OLS residualization of KL before variance test | FR-3, FR-4 |
| No KL control | Raw delta_var without residualization | FR-5.2 |
| Q1 only | Gate criterion — bottom 20% margin items | FR-5.3 |
| Q1–Q5 trend | Full quintile spectrum shows Q1 specificity | FR-5.4 |
| Per-dataset | MMLU / TruthfulQA / ARC separate analysis | FR-5.5 |
| Isotropic sanity | Gaussian Δ control — expects flat quintile trend | FR-6.4 |

---

## 10. Output Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Experiment results | `h-m2/experiment_results.json` | All metrics per pair/dataset + gate evaluation |
| Quintile variance data | `h-m2/cache/quintile_variances_{pair}_{dataset}.npy` | Per-quintile variances |
| Figures | `h-m2/figures/` | 5 required plots |
| Validation report | `h-m2/04_validation.md` | Phase 4 output |
| Checkpoint | `h-m2/04_checkpoint.yaml` | Phase 4 progress tracking |

---

## 11. Phase 4 Coder Notes

**CRITICAL Implementation Rules:**
1. No GPU needed — all data is pre-cached; analysis is pure numpy/scipy
2. Load both pair2 and pair4 caches simultaneously (small enough: ~300MB each)
3. Z-score margin WITHIN each dataset-pair combination (don't share z-score across datasets)
4. One-tailed Welch's t-test: `p_one = p_two / 2` — directional hypothesis (DPO > SFT)
5. Bootstrap CI: resample from `dpo_q1_residuals` and `sft_q1_residuals` arrays (not from quintile boundaries)
6. Gate SHOULD_WORK: p ≥ 0.05 is NOT a code error — write result to JSON and continue
7. Visualize Q1–Q5 trend to show whether DPO effect is Q1-specific or uniform

**Code Starting Point:**
- New file: `h-m2/code/analysis_variance.py` (extends H-M1 patterns)
- Import from `h-m1/code/analysis_anisotropy.py`: `compute_logit_delta` (already validated)
- Main entry: `h-m2/code/run_analysis.py`

**Key Functions to Implement:**
- `load_h_e1_cache(pair_id, dataset)` → base_logprobs, aligned_logprobs, margin_z, kl_div
- `compute_variance_by_quintile(base_logprobs, aligned_logprobs, margin_z, kl_div, n_quintiles=5)` → (5,) variances
- `test_method_quintile_interaction(dpo_variances, sft_variances)` → t_stat, p_one_tailed, cohens_d
- `verify_mechanism_activated(results)` → (bool, dict)

---

*Generated by Phase 3 Step 2 (PRD) — UNATTENDED mode*
*BMAD PRD workflow not installed; generated from Phase 2C experiment brief directly*
*Base hypothesis H-M1 infrastructure reused per INCREMENTAL design*
*Phase 2C source: h-m2/02c_experiment_brief.md verified (COMPLETED 2026-03-17T03:35:00Z)*
