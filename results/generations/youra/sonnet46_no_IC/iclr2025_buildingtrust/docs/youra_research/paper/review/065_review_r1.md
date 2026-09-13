# Adversarial Review - Round 1

**Paper:** Trustworthiness Dimensions in LLMs Are Not Independent: A Partial Correlation Structure Driven by RLHF
**Reviewed:** 2026-08-04
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 2 | Citation year mismatch + incomplete reference |
| Engagement | 0 | 0 | Solid hook, clear contributions |
| Credibility | 0 | 2 | "First" overclaim unverifiable; df inconsistency |
| **TOTAL** | **0** | **4** | |

**Recommendation:** MAJOR_REVISION

---

## Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | Match? |
|-------|------------|--------------|--------|
| Significant pairs | 8/15 | 8/15 | ✓ |
| Safety–privacy ρ | 0.971, p=8.77e-09 | 0.971, p=8.77e-09 | ✓ |
| Fairness–privacy ρ | 0.912, p=2.41e-06 | 0.912, p=2.41e-06 | ✓ |
| Privacy–Machine_Ethics ρ | 0.859, p=1.64e-05 | 0.859, p=1.64e-05 | ✓ |
| Safety–Machine_Ethics ρ | 0.841, p=3.22e-05 | 0.841, p=3.22e-05 | ✓ |
| Fairness–Machine_Ethics ρ | 0.821, p=7.12e-05 | 0.821, p=7.12e-05 | ✓ |
| Truthfulness–Fairness ρ | 0.734, p=9.84e-04 | 0.734, p=9.84e-04 | ✓ |
| Truthfulness–Safety ρ | 0.698, p=2.31e-03 | 0.698, p=2.31e-03 | ✓ |
| Robustness–Truthfulness ρ | 0.612, p=1.17e-02 | 0.612, p=1.17e-02 | ✓ |
| Safety–Robustness ρ | −0.188, p=0.519 | −0.188, p=0.519 | ✓ |
| Silhouette (Ward k=2) | 0.637 | 0.637 | ✓ |
| Silhouette (Average k=2) | 0.637 | 0.637 | ✓ |
| Silhouette (Complete k=2) | 0.637 | 0.637 | ✓ |
| Silhouette (Ward k=3) | 0.500 | 0.500 | ✓ |
| Bootstrap mean frequency | 0.917 | 0.917 | ✓ |
| Privacy–Safety edge freq | 1.000 | 1.000 | ✓ |
| Fairness–Truthfulness edge freq | 1.000 | 1.000 | ✓ |
| Fairness–Privacy edge freq | 0.956 | 0.956 | ✓ |
| Robustness–Truthfulness edge freq | 0.941 | 0.941 | ✓ |
| Machine_Ethics–Privacy edge freq | 0.688 | 0.688 | ✓ |
| VIF(log10_params) | 3.37 | 3.37 | ✓ |
| VIF(is_RLHF) | 3.37 | 3.37 | ✓ |
| Δ_safety (7B pair) | +0.626 | +0.626 | ✓ |
| Δ_ethics (7B pair) | +0.464 | +0.464 | ✓ |
| Δ_safety (13B pair) | +0.652 | +0.652 | ✓ |
| Δ_ethics (13B pair) | +0.422 | +0.422 | ✓ |
| Δ_safety (70B pair) | +0.638 | +0.638 | ✓ |
| Δ_ethics (70B pair) | +0.386 | +0.386 | ✓ |
| Average Δ_safety | +0.63 avg | 0.639 mean | ✓ (rounded correctly) |
| Average Δ_ethics | +0.42 avg | 0.424 mean | ✓ (rounded correctly) |
| Scale-only ρ(safety, robustness) | −0.771, p=0.0008 | −0.771, p=0.0008 | ✓ |
| Bonferroni α | 0.0033 | 0.0033 | ✓ |
| Bootstrap n | 1000 resamples of 14/16 | 1000 resamples of 14/16 | ✓ |
| Tumminello citation in text (Sec 3.4) | "Tumminello, 2007" | Reference entry is 2005 | ✗ MISMATCH |
| Minimum eval set | {truthfulness, fairness, privacy} | {truthfulness, fairness, privacy} | ✓ |
| df in Algorithm 1 | df=14 | df should be 12 (16−2 covariates−2) | ✗ INCONSISTENCY |

---

## Part 1: Accuracy Check (Persona 1)

### MAJOR-ACC-1: Citation Year Mismatch — Tumminello 2007 vs 2005

**Evidence:** In-text citations (Section 3.4, Section 2.3, and Contribution 4 in Introduction) read "Tumminello, 2007" and "Tumminello et al., 2007." The reference list entry is:

> Tumminello, M., Aste, T., Di Matteo, T., & Mantegna, R. N. (2005). A Tool for Filtering Information in Complex Systems. *PNAS, 102*(30), 10421–10426.

The published paper (PNAS 102(30), 10421–10426) was received in 2005. Citing it as "2007" is factually incorrect and will trigger immediate red flags from any reviewer familiar with the MST-finance literature. This is either a wrong year in the reference or wrong year in all in-text citations. Fix: standardize all in-text references to "Tumminello et al., 2005" to match the reference list entry.

**Severity: MAJOR** — any reviewer in the network analysis or finance-physics community will notice this immediately and question the paper's literature due diligence.

---

### MAJOR-ACC-2: Degrees of Freedom Inconsistency in Algorithm 1

**Evidence:** Algorithm 1 (Section 3.2) states:
```
p_value ← 2 * scipy.stats.t.sf(|t_stat|, df=14)
```

With n=16 models and 2 OLS covariates (log10_params, is_RLHF), OLS residualization consumes 2 degrees of freedom. The partial correlation t-test should use df = n − 2 − 2 = 12, not df = 14.

The ground truth file lists `degrees_of_freedom: 14` — but this appears to record the raw df (n−2=14 for a simple Spearman), not the partial df after residualization. The Section 6.2 limitation explicitly states "df=12" ("partial correlation tests have df=12"), creating an internal contradiction between the algorithm pseudocode (df=14) and the Discussion section (df=12).

If df=14 was actually used in computation, p-values are anti-conservative (too small) and significance claims could be overstated. If df=12 was used correctly, the pseudocode must be corrected.

**Severity: MAJOR** — this is a methodological accuracy issue that affects the validity of all 8 significance claims if the wrong df was applied.

---

### Confirmed Accurate (no issues)

All 15 pairwise ρ values and p-values in Table 1 match the ground truth exactly. Table 2 delta values match to 3 decimal places. Table 3 silhouette scores match. Table 4 MST edge frequencies match. VIF values match. Bootstrap parameters match. Abstract statistics match the Results section. The H-M2 scale-only ablation (ρ=−0.771, p=0.0008) is correctly described as "scale-only control" removing only log_params, which matches the ground truth description.

---

### Minor Accuracy Notes (for human review)

- **Li et al. 2025 reference:** Listed as "[ICLR 2025 Oral — full citation pending verification]" — this is an incomplete citation and should not appear in a submitted paper. The paper acknowledges the incompleteness in brackets but leaves it unfixed.
- **Wang et al. 2025 (arXiv:2509.03871):** September 2025 arXiv ID cited as an active reference. Current knowledge cutoff is August 2025, so this reference cannot be verified. The paper treats it as an established reference. Reviewers may flag this as a citation to a future/unverifiable preprint.
- **Liang et al. 2022 vs 2023:** HELM is listed as "Liang et al., 2022" in the Introduction but the reference entry shows "(2023). Transactions on Machine Learning Research." In-text year should be 2023 to match the published TMLR version.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Question | Verdict |
|----------|---------|
| Would I continue after the abstract? | Yes — hook is concrete, promise is specific (50% compression) |
| Is the problem clear in 1 minute? | Yes — independence assumption challenged in paragraph 1 |
| Is novelty clear by end of Introduction? | Yes — 4 contributions explicitly listed |
| Is Figure 1 self-explanatory from caption? | Yes — caption clearly describes raw vs partial heatmap comparison |
| At what point do I lose attention? | Section 4 (Experimental Setup) reads as boilerplate; Sections 4.1–4.5 could be compressed |
| Does opening avoid generic "X is important" framing? | Yes — opens with a direct empirical challenge, not "trustworthiness is important" |
| Are contributions clearly listed? | Yes — numbered 1–4, specific, tied to experiments |

### Engagement Observations (no FATAL/MAJOR issues)

The abstract is strong and self-contained. The counterintuitive finding (privacy is RLHF-sensitive) is surfaced early. The practical payoff (50% evaluation compression) is quantified. The structure is logical.

One moderate engagement concern: Section 4 (Experimental Setup, ~450 words) partially duplicates Section 3 (Methodology). A busy reviewer scanning for methods details will encounter redundancy between Section 3.1 (Data) and Section 4.2 (Dataset and Models), and between Section 3.4 (MST) and Section 4.3 (Baselines). This structural redundancy is not a MAJOR issue but risks losing reviewer attention before reaching the results.

---

## Part 3: Credibility Check (Persona 3)

### MAJOR-CRED-1: "First Systematic" Novelty Claim is Unverifiable and Potentially False

**Claim (Introduction, Contribution 1, Conclusion):** "First systematic partial Spearman correlation analysis of LLM trustworthiness"

**Problem:** The word "first" is not substantiated. The paper provides no search methodology, no citation of prior work that was checked and found not to perform this analysis. The Related Work section argues the gap exists (TrustLLM doesn't compute it, Liu et al. list it as future work), but absence of evidence in 3–4 cited papers is not evidence of absence across the broader literature.

Partial correlation analyses of benchmark score matrices are a known technique. The paper does not demonstrate it has searched NLP benchmark methodology literature, psychometric literature on test dimensionality, or applied ML evaluation literature for similar analyses. The claim "we compute the full 6×6 partial Spearman correlation matrix… not previously reported" (Section 2.5) is more defensible than "first systematic analysis."

A skeptical reviewer will ask: "How do you know no one has done this? Did you search?" Without documentation of a comprehensive literature search, "first" is an overclaim.

**Recommended fix:** Replace "First systematic" with "A systematic" or "The first — to our knowledge — systematic analysis of…" following standard hedging convention.

**Severity: MAJOR** — "first" claims without documented search methodology routinely draw reviewer criticism and area chair flags.

---

### MAJOR-CRED-2: Epoch AI Capability Baseline Comparison is Methodologically Inequivalent

**Claim (Section 2.3, Section 4.3):** The paper uses "Epoch AI capability baseline (median ρ=0.73)" as a comparison point, implying the trustworthiness correlations (up to ρ=0.971) exceed capability benchmark redundancy.

**Problem:** The comparison is not apples-to-apples:
1. The Epoch AI study reports *raw* Spearman correlations across capability benchmarks; the paper's ρ=0.971 is a *partial* Spearman after confound removal. Partial correlations structurally exceed raw correlations when the confound is suppressing the estimate. The paper even states this explicitly for safety-privacy: raw ρ=0.73 → partial ρ=0.971. Comparing the paper's partial correlations to Epoch AI's raw correlations makes the trustworthiness correlations appear more distinctive than they may be.
2. The baseline measures different constructs (capability benchmarks vs. trustworthiness dimensions) across different model sets (Epoch AI's 17 benchmarks vs. TrustLLM's 6 dimensions).

The paper uses this comparison rhetorically to imply "trustworthiness dimensions are more correlated than capability benchmarks" — but this conclusion does not follow from the methodologically inequivalent comparison.

**Severity: MAJOR** — this is the kind of baseline mismatch that skeptical reviewers flag as potential cherry-picking or misleading framing.

---

### Credibility Observations (MINOR / no automatic fix needed)

**"Overclaiming tone" assessment:** The paper is generally well-calibrated. The Discussion honestly acknowledges: n=16 power limitations, the directional null for safety-robustness, RLHF mechanism is proposed not proven, machine_ethics MST ambiguity, and TrustLLM-specific operationalization. The within-family sign test p=0.125 is correctly reported as "minimum achievable for n=3" rather than being claimed as significant.

**Limitations completeness:** Section 6.2 is substantive and honest. One gap: the paper does not acknowledge that the OLS residualization approach for partial Spearman, while sound, is an approximation — the exact partial Spearman has different theoretical properties than rank-correlating OLS residuals. This is a known methodological subtlety that a methodologically sophisticated reviewer might raise. It does not invalidate the analysis but should be acknowledged.

**Section 2.5 positioning table:** The table is fair. It accurately represents what each prior work provides and what is missing. The framing "we do not compete with these evaluation frameworks — we analyze the data they provide" is appropriate and will defuse potential turf-defense reviewers.

**Contribution list assessment:** Contributions 1–4 are specific and tied to experimental results. The "robustness isolation principle" label in Contribution 2 is slightly grandiose for what is a clustering result that happened to isolate one dimension — but within acceptable range.

---

## Part 4: Human Review Notes

These are MINOR issues for human judgment. Not auto-fixable.

1. **Liang et al. 2022/2023:** Introduction cites "Liang et al., 2022" but reference is TMLR 2023. Minor year inconsistency — pick one and be consistent. TMLR date is the authoritative publication year.

2. **Li et al. 2025 incomplete citation:** "[ICLR 2025 Oral — full citation pending verification]" must be resolved before submission. Either find the full citation or remove the reference. An incomplete citation in square brackets is unprofessional in a submitted paper.

3. **Wang et al. 2025 (arXiv:2509.03871):** September 2025 arXiv paper cited in a paper dated August 2026. The content of this reference (Section 2.2: "reasoning LLMs show worse safety and privacy than standard models at equivalent scale") is not central to the paper's claims. If unverifiable, consider replacing with an established citation or removing.

4. **Section 4 redundancy with Section 3:** Sections 4.1 and 4.2 largely repeat Section 3.1–3.5. Consider merging or cross-referencing rather than restating. This is a space concern for the 8-page ICML format.

5. **Figure 3 caption vs Figure 10 caption:** Caption for Figure 3 says "Average-linkage hierarchical clustering dendrogram" but caption for Figure 10 says "Ward-linkage dendrogram." Both claim to show the 2-cluster structure. The paper should clarify which dendrogram is the primary visualization and ensure they are not redundant figures.

6. **"91.7% bootstrap stability" in abstract vs "mean per-edge frequency 0.917":** These are the same number, but readers skimming may not immediately recognize 91.7% = 0.917. The abstract uses percentage, the Results section uses decimal. This is consistent but might briefly confuse readers.

7. **Contribution 2 in Introduction mentions "negative safety-to-robustness deltas"** — this should be "negative robustness deltas after RLHF" (i.e., RLHF decreases robustness, not that safety negatively affects robustness). The phrasing "safety-to-robustness deltas" is ambiguous.

---

## Summary for Revision Agent

### Priority 1: MAJOR issues requiring fixes before resubmission

1. **[MAJOR-ACC-1] Tumminello year mismatch:** Change all in-text citations from "Tumminello, 2007" / "Tumminello et al., 2007" to "Tumminello et al., 2005" to match the reference list (PNAS 2005). Affects: Section 2.3, Section 3.4, Contribution 4 in Introduction.

2. **[MAJOR-ACC-2] df inconsistency in Algorithm 1:** Algorithm 1 shows `df=14` but Section 6.2 states "df=12." Determine which was actually used in computation. If df=12 is correct (n=16, 2 covariates), update Algorithm 1 to show `df=12`. If df=14 was used, restate Section 6.2 accordingly and recompute p-values. This must be verified against the actual code.

3. **[MAJOR-CRED-1] "First" novelty claim:** Replace "First systematic partial Spearman correlation analysis" with "The first, to our knowledge, systematic partial Spearman correlation analysis" in all three locations (Introduction contributions, Section 2.5, Conclusion).

4. **[MAJOR-CRED-2] Epoch AI baseline comparison:** Add a caveat sentence in Section 2.3 or 4.3 explicitly noting the comparison is between partial correlations (this paper) and raw Spearman correlations (Epoch AI) and that this methodological difference must be kept in mind when comparing magnitudes. Do not remove the baseline — it provides useful context — but flag the inequivalence.

### Priority 2: MINOR issues (human review)

5. Complete the Li et al. 2025 citation or remove.
6. Resolve Liang et al. 2022 vs 2023 date.
7. Assess Wang et al. 2025 arXiv:2509.03871 verifiability.
8. Review Algorithm 1 df against actual experiment code to determine the authoritative value.
