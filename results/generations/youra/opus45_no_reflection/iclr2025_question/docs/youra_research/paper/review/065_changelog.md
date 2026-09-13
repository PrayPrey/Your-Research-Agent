# Phase 6.5 Changelog

**Paper:** Probing Hidden States for Factual Correctness Prediction in LLMs  
**Review Period:** 2026-08-18

---

## Round 1 Changes

### R1-001: Clarify 0.885 vs 0.852 AUROC values (MAJOR)

**Location:** Section 5.1 Results

**Before:**
```
**Existence.** The probe achieves **AUROC = 0.885**, far exceeding the 0.60 threshold.

**Layer sweep.** The inverted-U pattern is confirmed:
[table with L15 = 0.852]
```

**After:**
```
**Existence.** The probe achieves **AUROC = 0.885** on full-scale evaluation (9,500 train / 1,700 val samples), far exceeding the 0.60 threshold.

**Layer sweep.** We conduct a preliminary layer sweep on a reduced sample (500 train / 200 val) to identify optimal extraction depth. The inverted-U pattern is confirmed:
[table]
...
The final probe trained on full data achieves 0.885 AUROC, improving over the layer sweep due to increased training data.
```

**Rationale:** Paper conflated two different experiments with different sample sizes. Clarification prevents reader confusion about apparent inconsistency.

---

## Round 2 Changes

### R2-001: Correct L11 AUROC (MINOR)

**Location:** Section 5.1, Layer sweep table

**Change:** 0.798 → 0.818

**Source:** h-m2/04_validation.md shows 0.8177

### R2-002: Correct L23 AUROC (MINOR)

**Location:** Section 5.1, Layer sweep table

**Change:** 0.791 → 0.785

**Source:** h-m2/04_validation.md shows 0.7854

### R2-003: Correct L27 AUROC (MINOR)

**Location:** Section 5.1, Layer sweep table

**Change:** 0.778 → 0.758

**Source:** h-m2/04_validation.md shows 0.7584

### R2-004: Update confidence intervals

**Location:** Section 5.1, Layer sweep table

**Change:** Adjusted CIs to match corrected AUROC values

---

## Summary Statistics

| Change Type | Count |
|-------------|-------|
| MAJOR fixes | 1 |
| MINOR corrections | 4 |
| Total edits | 5 |

---

## Verification

All changes verified against:
- `065_ground_truth.yaml`
- `h-e1/04_validation.md`
- `h-m2/04_validation.md`
- `h-m3/04_validation.md`
- `h-m4/04_validation.md`

---

*Generated: 2026-08-18*
