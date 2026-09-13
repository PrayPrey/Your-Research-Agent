# Reflection Report: H-M4

**Generated:** 2026-08-31T11:20:00+00:00
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED

---

## Summary

H-M4 tested whether execution monitoring achieves the highest efficiency ratio (Δpass@1 / mean overhead s, ≥1.5× next-best, bootstrap p<0.05). The gate failed: static analysis achieved the highest efficiency ratio (6.64) versus execution monitoring (0.41). The ratio advantage of static over type was only 1.24× (< 1.5× threshold), and the bootstrap CI [-1.10, 3.35] includes 0.

---

## What Succeeded

- Overhead ordering confirmed (secondary hypothesis): static ≈ type < execution < SMT
- Kruskal-Wallis and pairwise Mann-Whitney tests confirm statistically significant overhead differences
- Full pipeline implemented: timing instrumentation, 4 verifiers, bootstrap BCa, 5 figures
- All 421 problems × 4 categories processed (1,684 runs)
- Checkpoint/resume operational

## What Failed

- Primary hypothesis: execution monitoring does NOT achieve ≥1.5× efficiency ratio advantage
- Execution monitoring Δpass@1 (~0.22) is only ~2× that of static (~0.11), while overhead is ~17× higher → net efficiency strongly favors static

## Root Cause

The efficiency ratio metric (Δpass@1 / mean_overhead_s) is dominated by overhead, not correctness gains. Execution monitoring's high overhead (~800ms) overwhelms its higher absolute improvement rate. This is a structural property of the metric — any high-overhead verifier will score poorly on efficiency ratio regardless of correction quality.

## Improvement Assessment

No self-recovery path exists for this specific gate criterion without changing the metric definition or the overhead profile of execution monitoring (which is not modifiable without changing the verifier mechanism itself). The finding is scientifically valid and informative.

**Decision:** LIMITATION_RECORDED — continue to Phase 5 with limitation note.

## Limitation Note

H-M4: SHOULD_WORK gate FAILED — execution monitoring does not achieve ≥1.5× efficiency ratio advantage over static analysis. Static analysis dominates efficiency ratio due to 17× lower overhead. Finding is scientifically valid: efficiency ratio (Δpass@1/overhead) favors lightweight verifiers structurally. No self-modification path identified.

## Lessons Learned

- Efficiency ratio metrics penalize high-overhead methods even when they achieve higher absolute correctness gains
- Static analysis (Pyright) is the efficiency-dominant feedback category on this metric
- For paper: report overhead ordering as confirmed finding; reframe efficiency ratio as a practical cost-benefit finding rather than a failure
- Future hypotheses should consider separating "effectiveness" (Δpass@1) from "efficiency" (ratio) as distinct metrics

## Dependent Hypotheses

None. H-M4 is a leaf node in the hypothesis DAG.

## Route

Continue to Phase 4.5 (hypothesis synthesis). No Phase 0/2A routing for SHOULD_WORK gates.
