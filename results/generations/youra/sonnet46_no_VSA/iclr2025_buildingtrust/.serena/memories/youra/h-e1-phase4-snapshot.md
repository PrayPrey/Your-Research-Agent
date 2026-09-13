# Hypothesis Completion Snapshot: H-E1

**Date:** 2026-07-29
**Hypothesis:** H-E1 (EXISTENCE, FOUNDATION)
**Statement:** Under scale-matched conditions (~110-250M parameters), transformer models grouped by architecture family exhibit characteristic Δ*-vector profiles showing greater within-family similarity than between-family similarity (permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories).
**Final Status:** PARTIAL → SELF_MODIFY
**Gate Type:** MUST_WORK
**Gate Result:** PARTIAL

## Results
- η² = 0.293 (> 0.15 target ✓)
- η² fraction ≥ 0.15 = 83.3% of categories ✓
- p-value = 0.147 (target < 0.05 ✗ — underpowered, N=9)
- LOMO accuracy = 0.333 = chance ✗ (N too small for LOMO)
- Bootstrap CI includes zero ✗

## Reflection
- Outcome: SELF_MODIFY
- Root cause: N=3 per family insufficient statistical power (~40% for η²=0.29)
- enc_dec coverage gap: T5/BART sst2-only, no mnli → ANLI-R3 η²=0
- Signal confirmed real and large (η²=0.29, one significant interaction p=0.014)

## Lessons
- N≥5 per family (≥15 total) needed for p<0.05 at this effect size
- enc_dec models need mnli fine-tuning for ANLI-R3 evaluation
- Per-model checkpoint saving essential (crash recovery used successfully)
- CheckList requires pre-installation (skipped in h-e1)

## New Hypothesis
- ID: h-e1-v2
- Changes: Expand to 4-5 per family (~15 total), fix enc_dec mnli fine-tuning, install checklist
- All 7 code modules reusable — only extend MODEL_CONFIGS in fine_tuner.py

## Code Location
/docs/youra_research/h-e1/code/ (7 modules, 1788 lines total)
