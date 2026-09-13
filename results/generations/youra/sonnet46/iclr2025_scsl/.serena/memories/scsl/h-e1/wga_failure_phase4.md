# Hypothesis Completion Snapshot: h-e1 (Phase 4 — WGA Existence Test)

**Date:** 2026-03-16T17:45:00Z
**Hypothesis:** h-e1
**Statement:** SAM optimizer improves WGA by >=10pp over ERM+SGD on Waterbirds/CelebA without group label supervision
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results Summary
- ERM+SGD baseline: 76.60% WGA (±2.93%)
- Best SAM (rho=0.01): 77.51% WGA (+0.90pp) — NOT significant (p_corr=0.83)
- Larger rho values hurt WGA monotonically: rho=0.2 → 38.54% (-38pp)
- GroupDRO (group-supervised): 87.51% (+10.9pp) — confirms dataset works
- n=35 runs (7 conditions × 5 seeds), Waterbirds full test set n=5,794

## Root Causes
1. Flat minima ≠ group-robust minima — SAM's flatness is isotropic, does not discriminate spurious vs core features
2. Dose-response inverted: larger rho = more WGA harm (not help)
3. No group-label-free advantage from flatness regularization

## Cascade Effects
- h-m1, h-m2, h-m3: CASCADE_FAILED

## Proven Infrastructure (reusable for Phase 0 redesign)
- WaterbirdsDataset (data_loader.py), ResNet-50 setup, evaluate.py, GroupDRO train step
- Conda env: youra-h-e1
- Dataset cache: .data_cache/datasets/waterbirds/

## Lessons for Phase 0
- Do NOT pursue SAM/flatness optimizers as group-robustness surrogates
- Promising group-label-free alternatives: JTT, LfF, DFR, CLIP-style pretraining
- GroupDRO strong labeled baseline: +10.9pp confirmed
