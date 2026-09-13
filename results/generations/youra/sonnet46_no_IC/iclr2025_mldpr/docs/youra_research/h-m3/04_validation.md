# Phase 4 Validation Report: H-M3

**Hypothesis ID:** H-M3  
**Gate Type:** SHOULD_WORK  
**Gate Result:** INFORMATIVE_NEGATIVE  
**Date:** 2026-08-05  
**Phase:** 4 (PoC Implementation & Validation)

---

## 1. Executive Summary

H-M3 tested whether the categorical tag count dose-response (bins: 0, 1-2, 3-5, 6+) is **monotonically** ordered AND statistically distinguishable at adjacent contrast boundaries (Bonferroni α=0.0167) on the full OpenML corpus (N=5,217).

**Result: INFORMATIVE_NEGATIVE**

- **Monotonic ordering: CONFIRMED** — IRR(1-2)=1.1267 < IRR(3-5)=1.1277 < IRR(6+)=1.2861 (all vs reference "0")
- **Adjacent contrasts: 1/3 passing** — only the 3-5 vs 6+ contrast is significant at Bonferroni threshold (p=5.54e-10); 0→1-2 and 1-2→3-5 transitions are not distinguishable
- **Gate condition (≥2/3 adjacent contrasts p<0.0167):** NOT MET → INFORMATIVE_NEGATIVE

This is a scientifically valid outcome per the SHOULD_WORK gate design. The binary dose-response (H-E1: IRR=1.2263) and continuous log-linear dose-response (H-M2: IRR_P2=1.5332) remain the primary evidence for the Discovery→Task Creation mechanism. H-M3's informative negative shows that the specific categorical bin boundaries (0, 1-2, 3-5, 6+) do not create equally distinguishable adjacent steps — the transition to high tag counts (6+) is the dominant distinguishing factor.

---

## 2. Experiment Results

### 2.1 Corpus Statistics

| Metric | Value |
|--------|-------|
| Total N | 5,217 |
| Bin "0" (no tags) | 2,592 (49.7%) |
| Bin "1-2" | 73 (1.4%) |
| Bin "3-5" | 710 (13.6%) |
| Bin "6+" | 1,842 (35.3%) |

> **Note:** Bin "1-2" has only N=73, substantially smaller than other bins. This small sample partially explains the weak 0→1-2 contrast (bonf_p=0.272).

### 2.2 CT Overdispersion Test

| Test | Value |
|------|-------|
| CT LR Statistic | 7,509.42 |
| p-value | 0.00 (effectively 0) |
| NB-2 Appropriate | YES (LR >> 3.84) |

### 2.3 Categorical NB-2 Primary Model

**Formula:** `N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq + C(decade)`  
**Reference category:** "0" (no tags)

| Category | IRR | 95% CI Lower | 95% CI Upper | p-value |
|----------|-----|-------------|-------------|---------|
| "0" (reference) | 1.0000 | — | — | — |
| "1-2" | **1.1267** | 1.0025 | 1.2664 | 4.54e-02 |
| "3-5" | **1.1277** | 1.0669 | 1.1919 | 2.10e-05 |
| "6+" | **1.2861** | 1.2230 | 1.3524 | 1.12e-22 |

### 2.4 Monotonicity Check

- IRR(1-2) = 1.1267 > 1.0 ✓
- IRR(1-2) = 1.1267 < IRR(3-5) = 1.1277 ✓ (margin: +0.0010)
- IRR(3-5) = 1.1277 < IRR(6+) = 1.2861 ✓
- **Monotonic: TRUE** (strict ordering confirmed, though 1-2 vs 3-5 margin is very small: 0.001)

### 2.5 Adjacent Contrast Testing (Bonferroni α=0.0167)

| Contrast | Bonferroni p-value | Result |
|----------|-------------------|--------|
| 0 vs 1-2 | 0.2721 | FAIL |
| 1-2 vs 3-5 | 1.0000 | FAIL |
| 3-5 vs 6+ | 5.54e-10 | **PASS** |

**Passing: 1/3** — Gate condition (≥2/3) NOT MET.

### 2.6 Gate Evaluation

| Criterion | Required | Actual | Status |
|-----------|----------|--------|--------|
| Monotonic IRR ordering | IRR(1-2) < IRR(3-5) < IRR(6+), all > 1 | TRUE | ✓ MET |
| Adjacent contrasts significant | ≥2/3 p < 0.0167 | 1/3 | ✗ NOT MET |
| **GATE RESULT** | PASS | **INFORMATIVE_NEGATIVE** | — |

### 2.7 Robustness Checks

**RC-6 (Decade × Category Interaction):**
- AIC = 25,743.84 vs primary 25,739.41 (interaction model worse → main effects sufficient)

**RC-7 (No Decade FE — Attenuation):**
- IRR(1-2) without FE: 1.263 (attenuation ratio: 1.121)
- IRR(3-5) without FE: 1.294 (attenuation ratio: 1.147)
- IRR(6+) without FE: 1.431 (attenuation ratio: 1.114)
- Mean attenuation ~11% — comparable to H-M1 result (12.2%), confirming decade FE absorbs ~11% of categorical tag effect.

---

## 3. Scientific Interpretation

**Why INFORMATIVE_NEGATIVE is scientifically valid:**

1. **Bin "1-2" sparsity (N=73):** With only 73 datasets in the 1-2 bin vs 2,592 in bin "0", the 0→1-2 contrast has insufficient power for Bonferroni-corrected significance. This is a data distribution issue, not a mechanism failure.

2. **Near-identical IRR(1-2) ≈ IRR(3-5):** The 1.1267 vs 1.1277 gap is essentially zero (Δ=0.001), confirming that the categorical boundary between 1-2 and 3-5 tags does not create a meaningfully different discovery effect — both small-tag subsets behave similarly.

3. **The dominant effect is at 6+ tags:** IRR(6+)=1.286 is robustly distinct from all lower categories (p=1.12e-22). Datasets with 6+ tags have the highest discovery advantage.

4. **Mechanism chain status:** H-E1 (binary: IRR=1.23, MUST_WORK PASS) → H-M1 (mechanism: decade-robust, MUST_WORK PASS) → H-M2 (continuous log-linear: IRR_P2=1.53, SHOULD_WORK PASS) → H-M3 (categorical: informative negative). The chain shows the tag effect is real and dose-responsive in continuous form, but the specific categorical binning does not produce equally-spaced dose steps.

**Scientific constraint added:**
> The Discovery→Task Creation mechanism operates more as a **threshold effect** (0 vs ≥1 tag: H-E1) plus a **high-count amplification** (6+ tags: H-M3 bin "6+") than as a uniformly graded categorical dose-response across all four bins.

---

## 4. Outputs Generated

| Output | Path | Status |
|--------|------|--------|
| Preprocessed data | `h-m3/results/preprocessed_m3.parquet` | ✓ |
| Model results | `h-m3/results/model_results.json` | ✓ |
| Primary results | `h-m3/results/primary_results.json` | ✓ |
| Fig 1: IRR bar chart | `h-m3/figures/fig1_irr_bar_chart.png` | ✓ |
| Fig 2: Dose-response | `h-m3/figures/fig2_dose_response.png` | ✓ |
| Fig 3: Category distribution | `h-m3/figures/fig3_category_distribution.png` | ✓ |
| Fig 4: Contrast forest plot | `h-m3/figures/fig4_contrast_forest.png` | ✓ |
| Fig 5: Attenuation comparison | `h-m3/figures/fig5_attenuation.png` | ✓ |

---

## 5. Gate Decision and Pipeline Routing

**Gate Type:** SHOULD_WORK  
**Result:** INFORMATIVE_NEGATIVE  
**Routing:** Per SHOULD_WORK gate protocol — no re-routing to Phase 0 or Phase 2A. Continue pipeline.

The informative negative is documented with the scientific constraint above. The H-E1→H-M1→H-M2 mechanism chain provides sufficient evidence for the Discovery→Task Creation mechanism. H-M3's negative adds nuance: the dose-response is not uniformly categorical but concentrated at the 6+ tag threshold.

**Next phase:** Phase 4.5 (Hypothesis Synthesis) — all 4 sub-hypotheses in the chain now have outcomes.

---

## 6. Checkpoint Reference

- **Checkpoint file:** `h-m3/04_checkpoint.yaml`
- **Tasks completed:** 17/17 (all tasks from 03_tasks.yaml)
- **Coder-Validator cycles:** 1
- **Experiment status:** completed
- **Gate result:** INFORMATIVE_NEGATIVE

---

*Report generated: 2026-08-05 by Phase 4 Workflow (UNATTENDED mode)*
