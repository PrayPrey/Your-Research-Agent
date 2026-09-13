# Adversarial Review - Round 1

**Paper:** MMLU Scale Confounding in Alignment Benchmark Correlations: A Partial Spearman Diagnostic
**Reviewed:** 2026-07-30
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 2 | Minor number inconsistency between section file and compiled paper; Fisher z formula notation issue |
| Engagement | 0 | 0 | Strong engagement throughout |
| Credibility | 0 | 1 | Conclusion drops "to our knowledge" hedge; RLHF N mismatch needs clarification |
| **TOTAL** | **0** | **3** | **MINOR_REVISION** |

**Recommendation:** MINOR_REVISION

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Verification Table

| Metric | Paper Claims | Ground Truth | Match? |
|--------|-------------|--------------|--------|
| N analysis | 296 | 296 | YES |
| N after join (before dropna) | 297 (compiled); 299 (section 4.2) | 297 | DISCREPANCY in section 4.2 |
| raw_rho | 0.732 | 0.7322 | YES (rounded) |
| partial_rho | 0.343 | 0.3432 | YES (rounded) |
| fisher_z | 6.97 / 6.9679 | 6.9679 | YES (both forms used consistently) |
| fisher_z_p | 3.22 × 10⁻¹² | 3.22e-12 | YES |
| reduction_pct | 53% / 53.1% | 53.1% | YES (both forms used) |
| raw_rho_p | 5.83 × 10⁻⁵¹ | 5.83e-51 | YES |
| partial_rho_p | 1.40 × 10⁻⁹ | 1.40e-09 | YES |
| raw_ci | [0.670, 0.780] | [0.670, 0.780] | YES |
| partial_ci | [0.180, 0.492] | [0.180, 0.492] | YES |
| R²(MMLU×TruthfulQA) | 0.493 / 49.3% | 0.4927 | YES (rounded) |
| R²(MMLU×BBQ) | 0.763 / 76.3% | 0.7634 | YES (rounded) |
| rho_mmlu_truthfulqa | 0.702 | 0.7019 | YES (rounded) |
| rho_mmlu_bbq | 0.874 | 0.8737 | YES (rounded) |
| p_mmlu_truthfulqa | 3.15 × 10⁻⁴⁵ | 3.15e-45 | YES |
| p_mmlu_bbq | 5.01 × 10⁻⁹⁴ | 5.01e-94 | YES |
| tier3_k_positive | 146 | 146 | YES |
| tier3_n | 300 | 300 | YES |
| tier3_proportion | 0.487 | 0.487 | YES |
| tier3_binomtest_p | 0.686 | 0.686 | YES |
| rlhf_truthfulqa_improvement | +3.406 pts | 3.406 | YES |
| rlhf_truthfulqa_ci | [+2.589, +4.212] | [2.589, 4.212] | YES |
| rlhf_n_pairs | 321 | 321 | YES |
| n_model_families | 51 | 51 | YES |
| n_families_min3 | 30 | 30 | YES |
| scenario classification | AMBIGUOUS | AMBIGUOUS | YES |
| BBQ proxy disclosure | Acknowledged | Required | YES — disclosed in Abstract, 3.2, 3.7, 4.2, 6.2, 6.3, 7 |

### FATAL Issues - Accuracy

None found.

### MAJOR Issues - Accuracy

**ACC-MAJOR-001: N=299 vs N=297 discrepancy in Section 4.2 (section file)**

In `/sections/04_experiments.md` (Section 4.2), the text reads: "Inner join on `model_name` between the LLM LB v1 CSV (N=500) and a separate BBQ proxy file (N=300), yielding N=299 matched models, reduced to N=296 after removing rows with missing values."

The compiled paper (`06_paper.md`) correctly states N=297 in section 5.1, consistent with ground truth (n_complete: 297). The section file says "N=299" which contradicts ground truth and the compiled paper.

This appears to be a stale value in the section file that was not propagated into the compiled paper. The compiled paper is correct, but the section file has an inconsistent intermediate count. If section files are regenerated, this would re-introduce the error.

**Fix:** Update `/sections/04_experiments.md` Section 4.2 to read "N=297 matched models" to match the validated ground truth and the compiled paper.

**ACC-MAJOR-002: Fisher z formula notation potentially misleading**

In Section 3.1 (both compiled and section file), the Fisher z formula is written:

> z = (z_raw − z_partial) / √(1/(N−3−1) + 1/(N−3−1))

The denominator uses `N−3−1 = N−4` for both terms. For raw Spearman (no covariate), the standard denominator term is `1/(N−3)`, not `1/(N−4)`. The `N−k−3` form (where k=1 covariate) applies to the partial correlation. This may reflect an implementation choice (treating both as partial with k=1 covariates), but the formula as written applies the same covariate correction to the raw rho term, which does not control for any covariate. Readers familiar with the standard Fisher z test will notice this discrepancy.

The underlying computation appears correct (the validated results match), so this is a presentational issue in the formula — but one that a statistician reviewer will flag. The paper should either (a) clarify that the formula is adapted for the raw-vs-partial comparison case with k=1 covariate in the partial, or (b) use the more standard `1/(N−3)` for the raw term and `1/(N−4)` for the partial term with a note on the mixed formula.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Opening hook avoids generic opening? | PASS | Concrete statistic in first sentence: "80% on MMLU...alignment coherence disappears by more than half" — avoids "X is important" trap entirely |
| Problem clear in first 60 seconds? | PASS | First paragraph states problem, method, result, and implication |
| Novelty clear within 2 minutes? | PASS | Contribution (2) explicitly states the Fisher z application as first in this literature |
| Would continue reading after abstract? | YES | Abstract has hook, result, caveat, and call-to-action — well-structured |
| Figure 1 self-explanatory from description? | PARTIAL | "Figure 1: Spearman heatmap for {MMLU, TruthfulQA, BBQ-proxy}" is minimally described in compiled paper; the section file references "[fig_6]" with more context. A reader cannot reconstruct what the heatmap shows without seeing the figure. However, this is standard for blind review submissions — acceptable if actual figure is included. |
| Contribution list compelling or feature dump? | PASS | Four contributions are well-differentiated: empirical magnitude, methodological tool, residual interpretation, RLHF null |
| Attention lost? | N/A | Never lost |
| RLHF pair count clarity (321 vs 300) | MINOR | Two different N values for RLHF analysis (321 base/chat pairs for TruthfulQA improvement; 300 for BBQ sign test). A quick reader might wonder if these should match. Section 2.3 and 5.5 mention both; the distinction is not explained inline |

**Attention Lost At:** N/A — paper maintains engagement throughout. Methodology section is slightly dense but justified.

### FATAL Issues - Engagement

None found.

### MAJOR Issues - Engagement

None found.

### Minor Engagement Notes

- The distinction between N=321 (TruthfulQA RLHF) and N=300 (BBQ sign test) is never explained. A confused reader might assume these should be equal. One sentence clarifying these come from different pipeline iterations would prevent confusion.
- Figure numbering in section files uses placeholder tags (`[fig_6]`, `[fig_14]`) while compiled paper uses sequential numbers (Figure 1, Figure 2, Figure 3, Figure 4). This is a compilation artifact but should be verified before submission.

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

**Claim:** "This is, to our knowledge, the first application of this test in the alignment benchmark evaluation literature."

**Assessment:** CREDIBLE. The hedge "to our knowledge" is appropriately applied. The claim is about a specific combination (Fisher z raw-vs-partial difference test applied as an alignment benchmark diagnostic), not about Fisher z in general or partial correlation in general. The paper correctly positions this against BenchScope (dimensionality, not pairwise directed test) and PCA analyses (global structure, not hypothesis-testable). The claim is well-scoped and appropriately hedged.

**ISSUE:** The Conclusion section (`07_conclusion.md` and `06_paper.md` Section 7) drops the hedge:

> "Our work provides the **first direct application** of the Fisher z raw-vs-partial difference test as a formal statistical diagnostic for this confound..."

The word "first" appears here without "to our knowledge." This is inconsistent with the Introduction which uses the hedge. The Conclusion should match: "the first direct application, to our knowledge, of the Fisher z..." — or the Introduction version should be used verbatim.

### Baseline Fairness Audit

**BBQ proxy disclosure:** The paper is transparent throughout. The abstract calls it "a bias proxy." Section 3.2 explicitly names ARC Challenge and explains why HELM Lite BBQ was unavailable. Section 6.2 names ARC proxy artifact as the "preferred explanation" for the residual partial_rho magnitude. Section 6.3 leads with BBQ proxy as L1 limitation. This is a model example of honest proxy handling.

**No overclaiming on bias avoidance findings:** Every mention of "bias" or "bias avoidance" in the context of results is qualified with "proxy." The Discussion explicitly cautions that partial_rho=0.343 may reflect shared reasoning demands rather than genuine factuality-bias coupling.

### RLHF Null Result Reporting

**Sign test p=0.686, N=300:** Reported appropriately as REFUTED in the prediction outcomes table. The paper frames this as "no evidence" rather than "evidence of no effect" — correct statistical language. The proxy caveat (L4 in Section 6.3) appropriately notes the null may be proxy-driven.

**Minor credibility concern:** Contribution (4) in the Introduction frames this as "Evidence for asymmetric RLHF alignment effects." A null result providing "evidence for" something is slightly aggressive framing. More precisely, the null result is consistent with asymmetric effects but does not confirm them. The body text (Section 5.5, 6.2) is more careful ("suggests potential asymmetry," "hypothesis-generating finding"), but the contribution list header is stronger than the evidence warrants.

### Residual 0.343 Interpretation

The paper handles partial_rho=0.343 well: it acknowledges significance, declines to classify into a scenario, identifies three competing explanations, and names the preferred explanation (ARC proxy artifact). No overclaiming detected.

### AMBIGUOUS Scenario Framing

The AMBIGUOUS outcome is consistently framed as pre-registered and scientifically valid, not spun as positive. The BCa CI spanning the boundary is reported as a limitation of N=296. This is appropriately honest.

### Limitations Section Completeness

| Required Limitation | Present? | Location |
|---------------------|----------|----------|
| bbq_proxy_disclosed | YES | L1 in 6.3; also 3.2, 3.7, 4.2 |
| scenario_ambiguity_disclosed | YES | L2 in 6.3; also 5.4 |
| harmbench_n0_disclosed | YES | L3 in 6.3; also 5.5 |
| rlhf_proxy_caveat_disclosed | YES | L4 in 6.3 |
| observational_cross_sectional_disclosed | YES | L5 in 6.3; also 3.7 |

All five required limitations present and appropriately detailed.

### Hype Language Audit

No hype language detected. The paper uses "decisive" for Fisher z p=3.22×10⁻¹² which is accurate given that magnitude. The phrase "exceptional statistical strength" appears in section 5.6 — this is defensible given p=3.22×10⁻¹² but slightly enthusiastic. No CRED-MAJOR-004 issues.

### RLHF Section 2.3 Background Claim

"Prior iterations of this research pipeline established a confirmed RLHF improvement on TruthfulQA MC2 of +3.406 points (BCa CI [+2.589, +4.212]) across 321 base/chat pairs" — this is properly flagged as coming from prior pipeline iterations, not the current experiment. Ground truth confirms these values. Appropriately sourced.

### FATAL Issues - Credibility

None found.

### MAJOR Issues - Credibility

**CRED-MAJOR-001: "First" claim in Conclusion drops hedge**

Section 7 (Conclusion) states: "Our work provides the first direct application of the Fisher z raw-vs-partial difference test as a formal statistical diagnostic for this confound."

The Introduction's version is: "This is, to our knowledge, the first application of this test in the alignment benchmark evaluation literature."

The Conclusion version drops "to our knowledge" — a hedge that is present and necessary in the Introduction. This inconsistency exposes the paper to reviewer criticism. A reviewer who catches this will flag it as either an overconfident claim in the Conclusion or an inconsistency in scholarly hedging.

**Fix:** Add "to our knowledge" to the Conclusion's first claim, matching the Introduction's language exactly.

---

## Part 4: Human Review Notes

1. **Minor phrasing inconsistency:** Introduction contribution (1) says "49.3% of TruthfulQA variance and 76.3% of BBQ-proxy variance" while abstract says "49% ... and 76%." These are the same numbers rounded differently. Consistent rounding within the abstract is fine, but between abstract and introduction the switch from rounded to precise may confuse readers. Consider standardizing (either always 49%/76% or always 49.3%/76.3%).

2. **Citation note:** `clawrxiv:2603.00394` uses an unusual citation format (not standard arXiv). This will need to be formatted as a proper reference for ICML submission. Ground truth lists it as "partially verified (preprint, no SS match)." Ensure this is formatted consistently with other preprint citations and that "clawrxiv" is a real preprint server rather than a placeholder.

3. **Section 2.4 discrepancy with compiled paper:** The section file for Related Work includes `(Liu et al., 2017; Tu et al., 2024)` but the compiled `06_paper.md` only has `(Liu et al., 2017)`. If Tu et al. 2024 is a real citation, it should appear in the compiled paper and reference list. If it was dropped intentionally, remove it from the section file too.

4. **"Figure 1" description:** In the compiled paper, Section 5.2 says "Figure 1: Spearman heatmap for {MMLU, TruthfulQA, BBQ-proxy} (N=296)." But Section 5.3 refers to "Figure 2" and "Figure 3" — the figure numbering in the compiled paper (Figures 1-4 in Results) should be consistent with whatever actual figures are included.

5. **BBQ description in Related Work (Section 2.1):** The first paragraph in 2.1 describes BBQ as "a question-answering benchmark specifically designed to detect social biases" without the proxy caveat. This is appropriate context for describing the real BBQ benchmark, since the section is reviewing existing work. However, a reader reading quickly might not notice the proxy disclosure comes three sections later. Consider adding a forward reference: "(see Section 3.2 for proxy substitution details)" at first mention in 2.1.

---

## Summary for Revision Agent

### Priority Fix List

**MAJOR (fix before resubmission):**

1. **ACC-MAJOR-001**: Update `/sections/04_experiments.md` Section 4.2: "N=299 matched models" → "N=297 matched models" to match ground truth and compiled paper.

2. **ACC-MAJOR-002**: Clarify Fisher z formula in Section 3.1. Either (a) note that both terms use N−k−3 with k=1 to treat the comparison symmetrically, (b) use separate denominators for raw (N−3) and partial (N−4) with explanation, or (c) add a footnote that the implementation follows the form in [reference] which applies the covariate correction to both terms for the raw-vs-partial comparison.

3. **CRED-MAJOR-001**: Add "to our knowledge" to Conclusion Section 7: "Our work provides the first direct application..." → "Our work provides, to our knowledge, the first direct application..."

**MINOR (clean up before resubmission):**

4. Add one sentence clarifying why TruthfulQA RLHF analysis used N=321 pairs while BBQ sign test used N=300 pairs (different pipeline iterations).

5. Soften Contribution (4) header in Introduction: "Evidence for asymmetric RLHF alignment effects" → "Null result suggesting potential asymmetry in RLHF alignment targets" — aligns with the body text framing.

6. Verify `Tu et al., 2024` citation: present in section file (02_related_work.md) but missing from compiled paper (06_paper.md). Resolve intentionally in one direction.

7. Standardize rounding: 49%/76% vs 49.3%/76.3% within and across sections.

8. Forward-reference BBQ proxy at first mention in Section 2.1.

9. Confirm `clawrxiv:2603.00394` is a real preprint server and format citation consistently.

### What's Working

- **Numerical accuracy is excellent.** Every key statistic in the compiled paper matches ground truth to the specified rounding. This is the result of a well-executed pre-registration and pipeline.

- **BBQ proxy handling is a model of transparency.** The paper acknowledges the ARC proxy substitution in the abstract, methodology, results, discussion, and limitations — it is impossible for a reader to miss this caveat. The preferred explanation for the residual rho (ARC artifact) demonstrates appropriate epistemic humility.

- **Opening hook is strong.** The concrete 80% MMLU example immediately makes the problem intuitive and avoids the generic "alignment is important" trap.

- **AMBIGUOUS outcome handling.** Pre-registering AMBIGUOUS as a valid outcome and then reporting it honestly, including it in the prediction outcome table as PARTIALLY_SUPPORTED, is excellent scientific practice.

- **Null result reported correctly.** The RLHF sign test (p=0.686) is reported as REFUTED without overclaiming. The body text appropriately frames it as hypothesis-generating.

- **All required limitations present.** All five required limitations from the ground truth specification appear in Section 6.3 with appropriate detail.

- **Contribution claims are well-hedged.** The "first application" novelty claim carries "to our knowledge" in the Introduction (fix needed in Conclusion only).
