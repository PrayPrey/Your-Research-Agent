# Adversarial Review - Round 2

**Paper:** Near-Orthogonal Uncertainty Signals: Empirical Independence of Semantic Entropy and Minimum Log-Probability for LLM Hallucination Detection
**Reviewed:** 2026-08-03
**Round:** R2 — Verification and Credibility
**Ground Truth Source:** `experiment_results.json` (N=2500, confirmed as primary experimental record)

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR | Status |
|----------|-------|-------|-------|--------|
| Accuracy Verification | 0 | 1 | 2 | Numbers match ground truth |
| Credibility / Overclaims | 0 | 3 | 2 | Several claims need tightening |
| Gate Outcome Representation | 1 | 0 | 0 | CRITICAL misrepresentation |
| Missing Limitations | 0 | 1 | 1 | |
| Unverified Citations | 0 | 1 | 0 | |
| **TOTAL** | **1** | **6** | **5** | MAJOR_REVISION |

**Recommendation:** MAJOR_REVISION — one fatal issue (gate outcome misrepresentation), six major issues that must be addressed. Paper is salvageable with targeted fixes. The core numbers are now correct and verified; the problem is narrative/interpretive framing, not data integrity.

---

## Part 1: Accuracy Verification (Accuracy Checker)

### 1.1 Primary Numbers vs. experiment_results.json

All primary metrics match the ground truth file exactly (within rounding):

| Metric | Paper Reports | experiment_results.json | Match? |
|--------|--------------|------------------------|--------|
| N prompts | 2500, seed=42 | n_prompts=2500 | YES |
| Pearson \|r\|(SE, min_logprob) | 0.026 | abs_pearson_r=0.02602 | YES |
| Spearman ρ(SE, judge) | −0.026 | spearman_rho=−0.02623 | YES |
| Partial R²(SE) | 0.0005 | partial_r2_se=0.0005119 | YES |
| LRT p-value | p=0.442 | lrt_p=0.4422 | YES |
| LRT chi² | 1.632 (Section 5.2) | lrt_chi2=1.6320 | YES |
| SE variance | 0.100 | se_variance=0.09978 | YES (rounded) |
| min_logprob mean | −2.435 | min_logprob_mean=−2.4351 | YES |
| Correctness rate | 34.8% (870/2500) | correctness_rate=0.348 | YES |
| Fraction degenerate | 0.000 | not in JSON; consistent | OK |

**Verdict:** All numbers are accurately transcribed from the N=2500 experimental run. The R1 fatal accuracy issues are resolved.

### 1.2 Spearman ρ Rounding Note

The paper rounds Spearman ρ(SE, judge) = −0.026, which matches the JSON value of −0.02623. The paper also rounds Pearson |r|(SE, min_logprob) = 0.026 from 0.02602. These are rounded to the same displayed value (0.026) but from slightly different underlying numbers (0.02623 vs 0.02602). The paper explicitly addresses this coincidence in the abstract and Section 5.3 — the explanation is adequate and accurate.

**MINOR-A1:** The paper says "the same rounded magnitude" in Section 5.3, but a precise reader would note that both round to 0.026 only when truncated to 3 decimal places. The abstract explanation is clear; the Section 5.3 language could more precisely say "both round to 0.026 at 3 significant figures." Low priority fix.

### 1.3 SE Variance Precision

The paper reports "SE variance = 0.100" (3 sig figs) against the actual value of 0.09978. This rounds correctly. No issue.

---

## Part 2: Credibility Check (Skeptical Expert)

### 2.1 FATAL: Gate Outcome Misrepresentation (FATAL-C1)

**This is the most serious remaining issue.**

The `experiment_results.json` gate result is unambiguous:

```json
"gate_result": {
  "gate_pass": false,
  "decision": "EXPLORE_N10",
  "reason": "abs(r)=0.026 or partial_r2=0.0005 marginal — retry N=10"
}
```

The gate **did not pass**. The pre-registered decision was `EXPLORE_N10` — scale to N=10 samples per prompt and retry. The paper, however, frames the partial R² result as a "well-powered null result" and a "genuine null" throughout:

- Abstract: "a well-powered null result that bounds the achievable gain from linear ensembles"
- Section 5.2: "a well-powered result at the full intended evaluation scale"
- Discussion 6.1: "The partial R²=0.0005 at N=2500 (LRT p=0.442) is a result obtained at the full intended evaluation scale... We therefore characterize this as a well-powered null"
- Summary Table 5.5 (RQ2): "NOT CONFIRMED" — this part is correct, but the framing is not

The gate reason says "marginal — retry N=10." This means the system did not conclude that the null is established; it concluded the experiment is marginal and needs more data (N=10 samples). Calling this a "well-powered null result" directly contradicts the pipeline's own gate decision.

**Why this matters scientifically:** A "well-powered null" is a strong claim — it means the experiment had sufficient power to detect the pre-registered effect size and found nothing. But the gate's EXPLORE_N10 decision indicates the pipeline itself considers the result marginal and inconclusive, not powered. Either:
(a) The power analysis referenced in Discussion 6.1 ("N=2500 provides >0.99 power") is correct and the gate decision logic is overly conservative, OR
(b) The gate is correct and the paper overclaims null status.

The paper never acknowledges or reconciles the gate's EXPLORE_N10 decision. A reviewer who checks the pipeline artifacts will find this immediately.

**Required fix:** Add a sentence in Section 5.2 and Discussion 6.1 acknowledging that the pre-registered gate outcome was `EXPLORE_N10` (not gate-pass), and explain why the paper nevertheless characterizes it as a powered null (e.g., "the gate's EXPLORE_N10 flag indicates the pipeline recommends extending to N=10 samples to reduce marginal uncertainty; however, a standard power analysis [cite] at N=2500 with 34.8% prevalence gives >0.99 power to detect partial R²≥0.02, justifying our characterization of the result as a powered null for the pre-registered threshold"). Do not hide the gate outcome — disclose it.

### 2.2 MAJOR: "Well-Powered" Power Analysis Unverified (MAJOR-C1)

The paper claims (Discussion 6.1): "Under a standard power analysis for logistic regression with a binary outcome at 34.8% prevalence, N=2500 provides >0.99 power to detect the pre-registered effect size of partial R²≥0.02."

This claim is not sourced, not computed in the paper, not referenced, and not reproducible. No formula, software, or citation is given. The claim is load-bearing — it is the entire basis for calling the null result "well-powered" and distinguishing it from an underpowered null.

**Required fix:** Either (a) add a brief power calculation in the Appendix (even a one-liner using the pwr package or statsmodels, or cite a formula), or (b) soften the language from "provides >0.99 power" to "is expected to be well-powered to detect partial R²≥0.02, given N=2500 and 34.8% prevalence [cite power analysis method]." Without verification, this claim is unsubstantiated.

### 2.3 MAJOR: min_logprob AUROC ~0.825 — Source Not Properly Cited (MAJOR-C2)

The paper states in Section 2.2 and 4.3: "min_logprob achieves AUROC ~0.825 on TriviaQA dev with Llama-3.1-8B" / "prior baseline AUROC ~0.825 on TriviaQA dev."

The R1 review noted this comes from "h-m1 limitation record (prior pipeline experiment)." It is cited in the paper as: "Min_logprob has been empirically shown to achieve AUROC ~0.825 on TriviaQA dev with Llama-3.1-8B." The current paper provides no citation for this specific number — the sentence just asserts it in Section 2.2 with no citation, and the Baselines section (4.3) labels it "prior baseline AUROC ~0.825" also with no citation.

This is a factual claim that cannot be verified from the References list. The references include Malinin and Gales (2021) but that paper does not report this specific value. The number appears to come from an internal prior run (h-m1), which is unpublished and uncitable.

**Required fix:** Either (a) cite the specific pipeline artifact or prior paper where 0.825 was established, (b) add a footnote: "AUROC of ~0.825 was measured in a prior pipeline run (h-m1) under identical experimental conditions," or (c) remove the specific number and say "strong single-pass baseline" without quantifying it. Option (b) is recommended — it's honest and transparent.

### 2.4 MAJOR: Ensemble Framing Tension (MAJOR-C3)

Section 6.1 states: "This finding establishes a necessary precondition for ensemble benefit." The Abstract says it "empirically justifies combining SE and min_logprob."

However, the same section immediately notes: "the signals are empirically orthogonal yet carry redundant correctness-predictive information in the linear logistic regression setting." This is self-contradictory: if the signals carry redundant correctness-predictive information (partial R²=0.0005), then independence alone does not justify ensemble combination — it only shows the signals don't overlap, not that they add up. The abstract phrasing "empirically justifies combining" goes beyond what the data shows.

**Required fix:** The abstract phrasing "empirically justifies combining SE and min_logprob" should be changed to "establishes the statistical independence precondition for combining SE and min_logprob, while showing that linear combinations yield no measurable gain on this benchmark." The current abstract slightly overclaims relative to the careful Discussion 6.1 language.

### 2.5 MAJOR: Raghuvanshi et al. (2025) Verification Status (MAJOR-C4)

The Appendix A statistics note: "Citations: 12 total (9 verified via Semantic Scholar, 2 partial, 1 unverified/removed)." This suggests the previously flagged [UNVERIFIED] citation was removed.

However, in Section 2.2 the paper still includes: "Raghuvanshi et al. (2025) combine token log-probability, NLI, and SE signals into a hybrid scoring system achieving AUC 0.818 on SQuAD2.0..." — and this citation appears in the References section as an uncited reference (it is NOT in the References list at the end of the paper). The References section ends with Xiong et al. (2023) and does not include Raghuvanshi et al.

**This is a citation without a corresponding reference entry.** The paper cites "Raghuvanshi et al. (2025)" in body text but no matching reference appears in the References list. A reviewer will flag this immediately as a missing reference.

**Required fix:** Either (a) add the full Raghuvanshi et al. (2025) reference with verified bibliographic details, or (b) remove the in-text citation and the associated claim from Section 2.2. If unverified, option (b) is safer.

### 2.6 MINOR: Gabriel (2026) is a 2026 paper cited in a 2026 paper (MINOR-C1)

Gabriel (2026): "The First Token Knows: Single-Decode Confidence for Hallucination Detection. arXiv:2605.05166." This cites an arXiv preprint from 2026 (arxiv ID 2605.xxxxx = May 2026). The paper's date is 2026-08-03. This citation is plausible for an August 2026 paper, but the specific value "r = 0.54–0.76" cited from it is load-bearing (it's the direct comparison point for the main finding). If this paper cannot be independently verified, the comparison is unsubstantiated.

**Recommendation:** Flag in revision notes that Gabriel (2026) should be verified accessible before submission. Low priority given the paper's date.

### 2.7 MINOR: Duplicate Limitation Entry (MINOR-C2)

Section 6.2 (Limitations) contains two nearly identical items:

> "**Ensemble AUROC not measured; linear null predicts limited linear gain.** Ensemble AUROC is not evaluated in this work."
> 
> "**Ensemble AUROC not measured.** ΔAUROC ≥ 0.025 on TriviaQA and cross-model transfer to Qwen-2.5-7B on TruthfulQA are not evaluated."

These two bullet points say essentially the same thing. The first sub-bullet is redundant with the second. This looks like a merge artifact from revision.

**Required fix:** Merge into a single limitation paragraph.

---

## Part 3: Human Review Notes (MINOR)

**MINOR-H1: Section 4.3 lists "SE_N5 (standalone)" as a baseline but never reports its standalone AUROC.** The paper compares SE and min_logprob for independence, but readers expecting a standalone AUROC for SE_N5 to contextualize the independence result will find none. This is not a flaw — the paper's scope is independence, not standalone AUROC — but the Baselines section should explicitly say "standalone SE AUROC is not the focus and is not reported here." The note currently in 4.3 ("Note: Ensemble AUROC is not evaluated") covers ensemble but not standalone SE AUROC.

**MINOR-H2: The Contribution #4** ("End-to-end reproducible pipeline: A checkpoint-aware, GPU-efficient implementation ready to scale directly to full N=2500 evaluation") is awkward given that N=2500 is the actual experiment scale — scaling to it is the experiment, not a future capability. This should be reworded to describe what the pipeline does (not what it "scales to").

---

## Summary for Revision Agent

### Priority Fix List (ordered by severity)

**FATAL (1):**
1. **FATAL-C1:** Disclose the gate outcome `EXPLORE_N10` from `experiment_results.json` in the paper. The current framing ("well-powered null result") contradicts the pipeline's own gate decision without explanation. Add one paragraph in Section 5.2 or Discussion 6.1 that: (a) reports the gate outcome honestly, (b) explains the power analysis rationale for nevertheless characterizing the result as a powered null, and (c) notes that h-e1-v2 will address the gate's recommendation (N=10 samples).

**MAJOR (6):**
2. **MAJOR-C1:** Add a verifiable power calculation or citation for the ">0.99 power at N=2500" claim (Discussion 6.1). Even a one-line formula reference suffices.
3. **MAJOR-C4:** Fix the Raghuvanshi et al. (2025) missing reference — it is cited in body text but absent from the References list. Either add the full reference or remove the citation.
4. **MAJOR-C2:** Source the min_logprob AUROC ~0.825 baseline (Section 2.2, 4.3) — cite the internal prior run (h-m1) as a pipeline artifact or remove the specific number.
5. **MAJOR-C3:** Soften "empirically justifies combining" in the abstract to "establishes the independence precondition for combining... while showing linear combinations yield no measurable gain."
6. **MINOR-C2:** Merge the two duplicate "Ensemble AUROC not measured" limitation bullets in Section 6.2.
7. **MAJOR-C1 (continued):** The Contribution #4 wording in Section 1 ("ready to scale directly to full N=2500 evaluation") is outdated — N=2500 is the completed run, not a future scale target.

**MINOR (3):**
8. MINOR-A1: Precision of "same rounded magnitude" language in Section 5.3.
9. MINOR-H1: Clarify that standalone SE AUROC is intentionally out of scope in Section 4.3.
10. MINOR-H2: Verify Gabriel (2026) arXiv:2605.05166 is accessible.

---

### Final Assessment

The R1 accuracy fixes are confirmed — all numbers now match `experiment_results.json`. The paper is scientifically honest about the partial R² null result, and the cross-model judge design is properly validated. The main remaining issue is that the paper reports a gate outcome as "well-powered null" without disclosing that the pre-registered gate itself said `EXPLORE_N10` (gate_pass: false). This must be addressed before submission. With the fatal gate issue resolved and the six major issues tightened, this paper reaches **CONDITIONAL_ACCEPT** status.
