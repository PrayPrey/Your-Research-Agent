# Phase 6.5 Changelog

**Date:** 2026-08-02
**Rounds:** 2 (R1 adversary + R2 numerical verification)

---

## Change 1: Table 1 p-values corrected (FATAL → FIXED)

**File:** `paper/06_paper.md`, `paper/sections/05_results.md`

**Before:**
```
| adv_qqp | 0.354 | ~0.12 | ✓ |
| adv_qnli | 0.350 | ~0.12 | ✓ |
| adv_sst2 | 0.274 | ~0.15 | ✓ |
| adv_mnli | 0.189 | ~0.20 | ✓ |
```

**After:**
```
| adv_qqp | 0.354 | 0.265 | ✓ |
| adv_qnli | 0.350 | 0.295 | ✓ |
| adv_sst2 | 0.274 | 0.360 | ✓ |
| adv_mnli | 0.189 | 0.695 | ✓ |
```

**Source:** `h-e1/results/stats_results.json` → `permutation_manova.cat_p_values`

---

## Change 2: Pillai's trace equivalence claim corrected (FATAL → FIXED)

**File:** `paper/sections/03_methodology.md`, `paper/06_paper.md`

**Before:**
> Test statistic: Pillai's trace (≡ η² in three-group case)

**After:**
> Test statistic: Pillai's trace; effect size: η² = SS_between/SS_total. In the balanced three-group case, Pillai's trace and η² are monotonically related (both bounded [0,1]) but not identical — we report η² throughout for interpretability, with Pillai's trace as the basis for the permutation p-value.

---

## Change 3: Section 5.2b added (MAJOR → FIXED, then revised in R2)

**File:** `paper/sections/05_results.md`, `paper/06_paper.md`

**Added section:**
> Mixed-effects model reached convergence. However, at N=9, severely underdetermined: most interaction terms show p≈1.0 or NaN due to collinearity/separation. encoder×adv_mnli p=0.014 consistent with MANOVA direction but should not be read as independent confirmation given model degeneracy. Reinforces N≥15 requirement.

---

## Change 4: CheckList absence explained (MAJOR → FIXED)

**File:** `paper/sections/04_experiments.md`, `paper/06_paper.md`

**Added note to Section 4.1 Datasets:**
> CheckList (Ribeiro et al., 2020) was included in the original design but not evaluated in this experiment due to a missing package installation; it is included in the h-e1-v2 design.

---

## Change 5: Related work citation consistency

**File:** `paper/06_paper_final.md`

Standardized references to use `Zhao et al. (2023)` and `Zeng et al. (2021)` consistently with `02_related_work.md` and `01_introduction.md` (the sections use updated citations from the section files, which differ slightly from the original `06_paper.md`). The final paper uses the section files as authoritative.

---

## Not changed (numerical claims verified correct)

- η²=0.293 ✓
- Cohen's f²≈0.41 ✓
- 83% (5/6 categories) ✓
- adv_rte η²=0.592, p=0.075 ✓
- LOMO=0.333 ✓
- N=9 → ~40% power ✓
- N≥15 for 80% power ✓
- 7 modules, 1,788 lines ✓
- All required limitations present ✓
