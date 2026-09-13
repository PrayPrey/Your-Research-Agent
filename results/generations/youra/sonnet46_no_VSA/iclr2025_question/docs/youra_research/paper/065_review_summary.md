# Phase 6.5 Adversarial Review Summary

**Generated:** 2026-08-03
**Pipeline Position:** Phase 6 → [Phase 6.5] → Phase 6.5.1
**Rounds completed:** 2

---

## Review Outcome

**Status:** CONVERGED (Round 2)
**FATAL issues fixed:** 1 (numerical discrepancy — see below)
**MAJOR issues fixed:** 6
**MINOR issues collected:** 5 (see 065_human_review_notes.md)

---

## Critical Finding (FATAL — R2)

**The actual experiment results (`experiment_results.json`) differ substantially from the values reported in `04_validation.md` and `065_ground_truth.yaml`.**

| Metric | 04_validation.md (stale) | experiment_results.json (authoritative) |
|--------|--------------------------|----------------------------------------|
| N | 300 (claimed "PoC") | **2500** (actual run) |
| Pearson \|r\| | 0.049 (0.0493) | **0.026** (0.02602) |
| Spearman ρ | -0.081 (-0.0815) | **-0.026** (-0.02623) |
| Partial R²(SE) | 0.0101 | **0.0005** |
| LRT p-value | 0.1504 | **0.442** |
| LRT chi² | 3.789 | **1.632** |
| SE variance | 0.133 | **0.100** |
| min_logprob mean | -2.415 | **-2.435** |
| Correctness rate | 34.3% (103/300) | **34.8% (870/2500)** |

**Root cause:** `04_validation.md` was authored before the actual experiment ran (or reflects an earlier different run). The `experiment_results.json` is the authoritative output from the actual code execution. The narrative framing ("N=300 PoC smoke test") was entirely fictional — the actual run used N=2500.

**Narrative consequence:** The paper's framing as a "PoC" with claims "pending N=2500" was incorrect. The paper now accurately reports N=2500 results. The partial R² null result (0.0005 vs target 0.02) at N=2500 is a **genuine well-powered null**, not an underpowering artifact. This changes the paper's scientific message: SE and min_logprob are near-orthogonal but do NOT improve correctness prediction in conditional logistic regression on TriviaQA at this scale.

---

## R1 MAJOR Issues Fixed

1. **Abstract** — Added the "20× lower than first-token signals" contrast and the partial R² null result.
2. **Introduction para 1** — Added the null result finding to the opening (novelty now clear in first paragraph).
3. **Introduction para 4 (gap)** — Restructured to emphasize both independence AND conditional predictive null as contributions.
4. **Contribution 3** — Reframed from "power boundary characterization" to "conditional predictive null result at full scale."
5. **Table 5.2** — Removed misleading "95% CI" column; replaced with "Direction / Significance" columns and deferred to stats.json for exact values.
6. **Section 1 para 3** — Added caveat that min_logprob AUROC 0.825 is from prior pipeline runs, not replicated in this experiment.

---

## R2 Numerical Corrections (all metrics updated)

All numerical values in `06_paper.md` and all section files corrected to match `experiment_results.json`. Key changes:
- Pearson |r|: 0.049 → 0.026
- Spearman ρ: -0.081 → -0.026
- Partial R²: 0.0101 → 0.0005
- LRT p: 0.1504 → 0.442
- SE variance: 0.133 → 0.100
- min_logprob mean: -2.415 → -2.435
- Correctness: 34.3% (103/300) → 34.8% (870/2500)
- N: 300 (PoC) → 2500 (full evaluation)
- RQ2 status: PARTIALLY CONFIRMED → NOT CONFIRMED (genuine null at N=2500)

---

## Persuasiveness Assessment

**Abstract:** Opens with the near-zero correlation and immediately contrasts with Gabriel 2026's first-token r=0.54–0.76. The null result for partial R² is stated honestly. Compelling hook for practitioners concerned about ensemble redundancy.

**Novelty:** Clear — direct measurement of SE vs min_logprob independence at N=2500, plus honest reporting of a well-powered null for conditional predictive contribution.

**Limitations:** Honest and complete. Scope is short-answer factual QA, single seed, no ensemble AUROC. The null result itself is a limitation and a finding simultaneously.

**Overall:** Paper reports an important negative result (genuine null for partial R²) alongside a positive result (near-orthogonality). This is more valuable than a fabricated "PoC pending" framing. Persuasiveness: **PASS**.

---

## Verified Against Ground Truth

| Claim | Authoritative Source | Verified |
|-------|---------------------|----------|
| \|r\|=0.026 | experiment_results.json: abs_pearson_r=0.02602 | ✓ |
| ρ=-0.026 | experiment_results.json: spearman_rho=-0.02623 | ✓ |
| Partial R²=0.0005 | experiment_results.json: partial_r2_se=0.0005119 | ✓ |
| LRT p=0.442 | experiment_results.json: lrt_p=0.4422 | ✓ |
| LRT chi²=1.632 | experiment_results.json: lrt_chi2=1.6320 | ✓ |
| SE var=0.100 | experiment_results.json: se_variance=0.09978 | ✓ |
| min_logprob mean=-2.435 | experiment_results.json: min_logprob_mean=-2.435 | ✓ |
| Correctness 34.8% | experiment_results.json: correctness_rate=0.348 | ✓ |
| N=2500 | experiment_results.json: n_samples=2500 | ✓ |
