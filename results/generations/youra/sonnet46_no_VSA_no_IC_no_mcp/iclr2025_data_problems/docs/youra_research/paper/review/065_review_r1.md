# Adversarial Review — Round 1
**Paper:** Deduplication Produces a Contamination-Correction Benchmark Accuracy Signature
**Date:** 2026-08-25
**Round:** R1 — Accuracy, Engagement, Structural Issues
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Summary

| Claim | Ground Truth Value | Source |
|-------|-------------------|--------|
| Pearson r | 0.632 (exact: 0.6323) | h-m3/04_validation.md |
| Pearson p | 0.0086 | h-m3/04_validation.md |
| Spearman ρ | 0.618 (exact: 0.6185) | h-m3/04_validation.md |
| Spearman p | 0.0107 | h-m3/04_validation.md |
| Bootstrap 95% CI | [0.297, 0.858] (exact: [0.2970, 0.8581]) | h-m3/04_validation.md |
| n observations | 16 | h-m3/04_validation.md |
| MMLU t-stat | -5.574 | h-e1/04_validation.md |
| MMLU p | 0.0114 | h-e1/04_validation.md |
| MMLU mean Δ | -0.0071 | h-e1/04_validation.md |
| Δr (token vs step) | +0.093 | h-m4/04_validation.md |
| Pile step used | 99,000 | h-e1/04_validation.md |
| bias_delta | -0.00418 | h-m4/04_validation.md |
| min-k% r | -0.713 (exact: -0.7125) | h-m3/04_validation.md |

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 3 |
| MINOR | collected in human_review_notes |

**Recommendation:** CONTINUE to Round 2 (MAJOR issues require resolution)

---

## PERSONA 1: ACCURACY CHECKER

### Claim Verification Table

| Claim | Paper | Ground Truth | Match | Severity |
|-------|-------|--------------|-------|----------|
| Pearson r = 0.632 | 0.632 | 0.6323 | ✅ (rounded) | — |
| p = 0.0086 | 0.0086 | 0.0086 | ✅ | — |
| Spearman ρ = 0.618 | 0.618 | 0.6185 | ✅ (rounded) | — |
| Bootstrap CI [0.297, 0.858] | [0.297, 0.858] | [0.2970, 0.8581] | ✅ (rounded) | — |
| MMLU t = -5.574, p = 0.0114 | -5.574, 0.0114 | -5.574, 0.0114 | ✅ | — |
| MMLU mean Δ = -0.0071 | -0.0071 | -0.0071 | ✅ | — |
| Δr = +0.093 | +0.093 | +0.093 | ✅ | — |
| Pile step = 99,000 | 99,000 | 99,000 (h-e1) | ✅ | — |
| <0.30% mismatch | <0.30% | 0.30% | ✅ | — |
| 13-gram r = +0.632 vs min-k% r = -0.713 | stated | -0.7125 in h-m3 | ✅ (rounded) | — |
| H-M1 2/4 benchmarks significant | stated | 2/4 confirmed | ✅ | — |
| H-M1 Spearman ρ = 1.0 | stated | 1.0 confirmed | ✅ | — |
| 207B tokens | ~207B | 207_000_000_000 | ✅ | — |
| bias_delta = -0.004 | "-0.004" (Section 5.3) | -0.00418 | ✅ (approx) | — |
| Per-model r: 160M=0.631, 410M=0.799, 1B=0.539, 6.9B=0.856 | stated | 0.6307, 0.7988, 0.5391, 0.8562 | ✅ (rounded) | — |
| n=4 benchmark degrees of freedom | L3 limitation | n=4 unique benchmarks | ✅ disclosed | — |

**MAJOR FINDING (ACC-MAJOR-001): Pile step 99K vs 128K inconsistency across reports**

The paper states "Pile step 99,000" consistently (Methods Section 3, Results Section 5.3). h-e1/04_validation.md confirms step 99,000. However, h-m4/04_validation.md reports "Token-count-matched pair uses Pile step 128000." This appears to be two different checkpoint pair calculations: h-e1 uses step 99K (≈207B tokens, <0.30% mismatch per h-e1 table), while h-m4's implementation notes report step 128K (218.4B actual vs 207B target, within 5.5% tolerance). 

**Critical issue:** The paper claims "<0.30% token volume mismatch" in Section 3. But h-m4/04_validation.md states the token-count-matched pair uses step 128K giving "218.4B actual vs 207B target" — which is 5.5% mismatch, not <0.30%. These cannot both be true for the same checkpoint pair. The paper may be citing h-e1's step 99K figures while H-M4 used a different checkpoint (128K). The paper needs to clarify: which Pile step was actually used for the primary analysis, and is the <0.30% claim accurate?

**Severity: MAJOR** — Directly affects the paper's central methodological claim and confound control argument.

**MINOR FINDING (ACC-MINOR-001): Benchmark mean n=4 correlation not reported in main text**

h-m3/04_validation.md shows that with n=4 (benchmark means), r=0.7761 but p=0.2239 (non-significant). The paper relies on n=16 flattened analysis. While L3 in Limitations acknowledges this, the main Results (Section 5.2) presents n=16 as the primary without early mention that this approach inflates effective df. This is a disclosure adequacy issue, not a numerical error.

---

## PERSONA 2: BORED REVIEWER

### Engagement Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✅ PASS | Opens with concrete puzzle (dedup makes MMLU worse), delivers resolution |
| Problem clear in 1 minute? | ✅ PASS | "What is happening?" paragraph lands well |
| Novelty clear in 2 minutes? | ✅ PASS | Contributions clearly listed |
| Figure 1 self-explanatory? | ⚠️ CONDITIONAL | Figure 1 described as `fig_01_correlation_comparison_bar.png` in Methods (not Introduction) — may confuse reader expecting it in Section 1 |
| Hook avoids "X is important"? | ✅ PASS | Opens with puzzle, not importance claim |
| Would I continue reading? | YES | Strong opening |
| Attention lost at? | Section 5.3 | Token-count matching section introduces "<0.30% mismatch" claim without flagging the h-m4 discrepancy |

**MAJOR FINDING (ENG-MAJOR-001): Figure numbering inconsistency in Results**

Section 5.1 references "Figure 4 (`differential_bar.png`)", "Figure 5 (`scaling_plot.png`)", "Figure 6 (`paired_scatter.png`)". Section 3 (Methods) references "Figure 1 (`fig_01_correlation_comparison_bar.png`)", "Figure 2 (`fig_02_scatter_two_panel.png`)", "Figure 3 (`fig_04_bias_decomposition.png`)". The Figure Reference Summary at the end lists Figure 1 in Methods content and Figure 4 in Results content — this is internally consistent with the reference table but the Results section is likely to confuse readers who expect figures to be numbered sequentially from the first result figure. More critically, Figure 3 in the Methods section refers to `fig_04_bias_decomposition.png` — the filename contains "04" while it's called Figure 3. This creates a mismatch between figure number and filename convention. A reviewer unfamiliar with the internal naming will notice this inconsistency and may flag it.

**Severity: MAJOR** — Will confuse reviewers and likely trigger a revision request.

**MINOR FINDING (ENG-MINOR-001): Section 5.3 "17% relative improvement" framing**

"a 17% relative improvement in contamination signal recovery" — this is Δr=0.093/0.539 ≈ 17.3%, which is mathematically correct but feels like overclaiming relative to the absolute gain of 0.093 correlation points. Whether 0.632 vs 0.539 is "17% better" or just "0.093 higher" is a framing choice; the relative framing is defensible but the absolute is more conservative.

---

## PERSONA 3: SKEPTICAL EXPERT

### Novelty and Methodology Assessment

**MAJOR FINDING (SKP-MAJOR-001): n=16 sample size with only 4 unique benchmark degrees of freedom — framing adequacy**

The paper's primary statistical claim is r=0.632, p=0.0086 across "16 observations." The paper does disclose in Limitation L3: "Only 4 benchmarks (n=4 unique benchmark degrees of freedom); n=16 flattened analysis inflates effective sample size." However, L3 appears in the Discussion section, after the main results are presented with n=16 framing. Worse, h-m3/04_validation.md's Ablation 2 shows that at n=4 (benchmark mean), r=0.776 but p=0.224 — non-significant. A skeptical reviewer will catch this and argue: the actual statistical test that respects independence is non-significant, and the p=0.0086 is derived from treating 4 repeated measurements across model sizes as independent observations.

The paper should either: (a) move the n=4 non-significance result to the main Results section with explicit acknowledgment, or (b) add a principled statistical argument for why the 4×4 flattening preserves independence (e.g., if model-size effects are orthogonal to contamination effects). As currently written, a reviewer has to hunt for this caveat in Limitations.

**This is a significant credibility risk at venues like ICML/NeurIPS.** The result survives statistically as a SHOULD_WORK finding, but the primary reporting mechanism (p=0.0086 with n=16) may be questioned as inflated.

**Severity: MAJOR** — Directly affects primary statistical claim's perceived validity.

**Novelty Assessment:** Legitimate. The contamination-correction framing of deduplication effects and the token-count matching contribution are genuinely novel angles not covered by Lee et al. 2022 or Biderman et al. 2023. No false novelty claims detected.

**Baseline Fairness:** No unfair baselines. The paper doesn't claim outperformance over baselines in the traditional sense; it presents a new analysis framework. Step-matching is a fair comparison target since it's the de-facto prior practice.

**Missing Limitations Check:**
- L1 (H-M2 scale threshold) — disclosed ✅
- L2 (proxy contamination estimates) — disclosed ✅
- L3 (n=4 true dof) — disclosed ✅ but buried
- L4 (H-M4 analytical simulation) — disclosed ✅
- L5 (single model family) — disclosed ✅
- Missing: **No Phase 5 baseline comparison** — the ground truth file explicitly flags this. The paper doesn't mention that Phase 5 baseline comparison was never completed. This is a genuine gap.
- Missing: **BibTeX unverified entry** — "Golchin & Surdeanu (2023). Time Travel in LLMs." Listed as "arXiv preprint" without arXiv ID. Ground truth flags this as unverified.

**MAJOR FINDING (SKP-MAJOR-002): Missing limitation — No Phase 5 baseline comparison**

The pipeline's ground truth file notes: "No Phase 5 baseline comparison — is this limitation noted?" The paper's Discussion (Section 6, Limitations) does not mention that a formal baseline comparison (Phase 5) was not completed. This is a procedural limitation that may affect how the result is contextualized against prior work in a structured way. While the paper does compare to Biderman et al. 2023 informally, the lack of a completed Phase 5 formal comparison should be disclosed.

**Severity: MAJOR** — Missing methodological disclosure.

**MINOR FINDING (SKP-MINOR-001): Golchin & Surdeanu citation incomplete**

Reference "Golchin, S., & Surdeanu, M. (2023). Time Travel in LLMs..." is listed as "arXiv preprint" without an arXiv ID. The paper uses this reference in Related Work. Should be verified and completed with actual arXiv ID.

---

## Summary for Revision Agent

### FATAL Issues (0): None

### MAJOR Issues (3):

1. **ACC-MAJOR-001** — Pile step 99K vs 128K inconsistency
   - Location: Section 3 (Methods), "<0.30% mismatch" claim
   - Fix: Clarify that Pile step 99K was used for all primary analyses (consistent with h-e1), confirm <0.30% applies to step 99K pair. Acknowledge h-m4 implementation note discrepancy (step 128K was an alternative checkpoint exploration) or reconcile explicitly. Add footnote clarifying the checkpoint selection.

2. **ENG-MAJOR-001** — Figure numbering inconsistency (Figure 3 / fig_04_bias_decomposition.png)
   - Location: Section 3 (Methods), Figure Reference Summary
   - Fix: Rename Figure 3 filename reference to `fig_03_bias_decomposition.png` in the text, or renumber to eliminate Methods-to-Results figure numbering confusion. Ensure filenames and figure numbers are consistent throughout.

3. **SKP-MAJOR-001** — n=16 flattening non-significance at n=4 buried in Limitations
   - Location: Section 5.2 (Results), Discussion Limitation L3
   - Fix: Add explicit sentence in Section 5.2 results text: "We note that at n=4 (per-benchmark mean across model sizes), the correlation r=0.776 does not reach significance (p=0.224); our primary n=16 analysis treats model-size replications as additional observations under the assumption that contamination effects are consistent across scale, which is supported by per-model-size correlations all exceeding r=0.5 (Table X)."

4. **SKP-MAJOR-002** — No Phase 5 baseline comparison not disclosed
   - Location: Discussion Section 6, Limitations
   - Fix: Add limitation "L6: No formal Phase 5 baseline comparison was completed. The contamination-correction framework is evaluated against prior literature informally; a structured comparison to methods such as [X] remains for future work."

### MINOR Issues (collected for human review):
- ACC-MINOR-001: n=4 correlation disclosure adequacy (overlap with SKP-MAJOR-001 — addressed by major fix)
- ENG-MINOR-001: "17% relative improvement" framing — consider also stating absolute Δr=+0.093
- SKP-MINOR-001: Golchin & Surdeanu arXiv ID missing

---

## Ground Truth Verification Log

- ✅ All primary numerical claims verified against h-e1, h-m3, h-m4 validation files
- ✅ Pile step 99K confirmed in h-e1/04_validation.md
- ⚠️ h-m4/04_validation.md shows step 128K for its token-count matching — potential discrepancy to investigate in R2
- ✅ H-M2 direction reversal accurately reported
- ✅ H-M1 dry-run 2/4 benchmarks accurately reported
- ✅ Per-model-size correlations match rounded values
- ⚠️ 065_ground_truth.yaml flags "No Phase 5 baseline comparison" — not disclosed in paper
- ⚠️ 065_ground_truth.yaml flags Golchin & Surdeanu unverified BibTeX entry
