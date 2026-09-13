# PRD: H-M1 Cross-Benchmark Transfer Inversion Analysis

**Date:** 2026-08-02
**Hypothesis:** H-M1 (MECHANISM)
**Gate:** SHOULD_WORK
**Budget Tier:** LIGHT (analysis-only, zero new training)

---

## Overview

H-M1 tests whether cross-benchmark transfer is asymmetric: HumanEval-only SFT models outperform MBPP-only on HumanEval+, while MBPP-only outperforms HumanEval-only on MBPP+ (directional rank inversion). This is a zero-training statistical analysis over H-E2 checkpoint evaluation results.

**No new models are trained. No GPU compute is required beyond H-E2 runs already completed.**

---

## Goals

1. Load H-E2 pass@1 results (all source conditions × both benchmarks × available seeds)
2. Check rank inversion per seed for the key HumanEval-only vs MBPP-only pair
3. Report inversion consistency across ≥2/3 valid seeds
4. Generate required figures (2×4 heatmap, per-seed strip, delta bar chart)
5. Output structured result JSON for downstream hypothesis synthesis

---

## Non-Goals

- No new SFT training
- No hyperparameter search
- No evaluation of new models
- No new EvalPlus runs unless MBPP+ results are missing from H-E2 output (fallback only)

---

## Inputs

| Input | Location | Notes |
|-------|----------|-------|
| H-E2 EvalPlus result files | `docs/youra_research/h-e2/results/` | JSON per (condition, seed, benchmark) |
| H-E2 SFT checkpoints | `docs/youra_research/h-e2/checkpoints/` | Only needed if MBPP+ results missing |
| EvalPlus package | pip install evalplus | v0.2.0+ for MBPP+ support |

**Available seeds (from H-E2 state):**
- humaneval_only: seeds 42, 123
- mbpp_only: seeds 42, 777
- leetcode_only: seeds 42, 123, 777
- equal_mix: seed 123

---

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Analysis result | `docs/youra_research/h-m1/h_m1_result.json` | JSON with success/seed_checks |
| 2×4 heatmap | `docs/youra_research/h-m1/figures/heatmap_pass1.png` | PNG, 300dpi |
| Per-seed strip | `docs/youra_research/h-m1/figures/per_seed_inversion.png` | PNG |
| Delta bar chart | `docs/youra_research/h-m1/figures/transfer_delta.png` | PNG |
| Validation report | `docs/youra_research/h-m1/04_validation.md` | Markdown |

---

## Success Criteria

- **PASS:** Full inversion (HE-only > MBPP-only on HumanEval+ AND MBPP-only > HE-only on MBPP+) in ≥2/3 valid seeds
- **PARTIAL:** One direction inverts but not both — report as partial mechanism support
- **FAIL:** No inversion in any seed — log as limitation, SHOULD_WORK gate does not block pipeline

---

## Implementation Budget

| Component | Effort |
|-----------|--------|
| Data loading + inversion check script | 1–2 hours |
| Figure generation | 1 hour |
| Fallback: re-run MBPP+ eval if missing | 2–4 hours GPU (conditional) |
| Validation report | 30 min |

Total: ~4–8 hours (including fallback). No GPU needed if H-E2 MBPP+ results exist.

---

## Risk

| Risk | Mitigation |
|------|-----------|
| MBPP+ results missing from H-E2 | Fallback: re-run `evalplus.evaluate --dataset mbpp` on H-E2 checkpoints |
| Only seed 42 valid for both conditions | Report limitation; inversion check still valid over 1 seed |
| Gate fails | SHOULD_WORK — log, do not block pipeline |
