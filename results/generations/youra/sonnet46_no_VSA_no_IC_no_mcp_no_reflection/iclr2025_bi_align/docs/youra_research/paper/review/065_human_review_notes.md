# Human Review Notes: R1 MINOR Issues

**Round**: R1
**Paper**: 06_paper_r1.md (revised)
**Date**: 2026-08-31

These issues were identified in adversarial review R1 as MINOR. They have NOT been auto-fixed in the revised paper. A human author should evaluate each before submission.

---

## MINOR-1: All references marked [UNVERIFIED]

**Source**: ACC-MINOR-1
**Location**: References section; all 13 citations.
**Issue**: Every citation carries [UNVERIFIED]. Authorship, year, venue, and titles have not been confirmed against Semantic Scholar or equivalent. If any citation is incorrect, the paper may cite non-existent or misattributed work.
**Action required**: Run each reference through Semantic Scholar (scholar.google.com or semanticscholar.org). Confirm author list, year, title, and venue. Remove [UNVERIFIED] tags once confirmed. Pay special attention to Shen et al. (2024) — the closest prior work — and Dell'Acqua et al. (2023), which motivates the effect size threshold.
**Priority**: HIGH before submission.

---

## MINOR-2: Paper title length

**Source**: ENG-MINOR (Bored Reviewer)
**Location**: Title / front matter.
**Issue**: "Do Better AI Models Make Us Intellectually Lazier? A Negative Result on Bidirectional Alignment Asymmetry in Large-Scale Interaction Logs" is 19 words — at the upper length limit for ICML. A shorter subtitle may improve scanability.
**Suggested options** (for human judgment):
- "Do Better AI Models Make Us Lazier? Testing Bidirectional Alignment Asymmetry at Scale"
- "Negative Result on Bidirectional Alignment Asymmetry: Prompt Length Trends in 1M AI Interaction Logs"
**Action required**: Author judgment. No change auto-applied.

---

## MINOR-3: Appendix A.2 sensitivity analysis asserted but data not shown

**Source**: ENG-MINOR (Bored Reviewer)
**Location**: Appendix A.2.
**Issue**: A.2 states the τ = +0.744 result is "robust to these variations (tested but not reported)." A reviewer may ask for the supporting numbers. As written, robustness is asserted without evidence.
**Action required**: Either (a) add a table in A.2 showing τ values under ≥30 and ≥100 user/bin floors, or (b) remove the robustness claim from A.2 and limit it to describing what the floor affects. Option (a) strengthens the paper; option (b) avoids the reviewer follow-up question.

---

## MINOR-4: Section 3.5 module filenames in main text

**Source**: ENG-MINOR (Bored Reviewer)
**Location**: Section 3.5 Implementation.
**Issue**: Listing seven Python module filenames in the methodology section reads as implementation detail rather than scientific content. May signal "filler" to reviewers.
**Action required**: Move the filename list to a footnote or a "Code availability" statement at the end of Section 3.5 (e.g., "Code available at [URL]; modules: data_loader.py, cohort_builder.py, [etc.]"). The paragraph text can retain the high-level description of pipeline components without filenames.

---

## MINOR-5: IP-hash user proxy noise not quantified

**Source**: EXP-L2 (Skeptical Expert)
**Location**: Section 6.3, L5 (added in R1 revision).
**Issue**: The limitation is now stated qualitatively. A skeptical reviewer may ask for an estimate of the noise magnitude — e.g., what fraction of the cohort might be misidentified due to NAT/VPN churn.
**Action required**: If feasible, add a rough estimate: (a) count IPs that appear in ≥2 consecutive months then drop for ≥1 month (VPN churn proxy), or (b) cite literature on IP-hash user proxy noise from prior WildChat or web log studies. If unfeasible, leave as-is — the limitation is now stated.

---

## MINOR-6: WildChat platform scope — explicit generalizability statement

**Source**: EXP-L3 (Skeptical Expert)
**Location**: Section 6.3, L6 (added in R1 revision); Abstract.
**Issue**: The paper now states L6 (ChatGPT-only scope) in limitations but the abstract does not mention this restriction. A reader may take the finding as generalizable to all AI platforms.
**Action required**: Consider adding a one-clause qualifier to the abstract: "in ChatGPT interaction logs" or "in WildChat returning users" in the key finding sentence. Example: "...returning users compose progressively longer, more elaborate prompts over the observation period (in WildChat-1M, a ChatGPT interaction log)." Small change, may improve precision.

---

## MINOR-7: No multiple comparison correction for h-e1 vs. h-e1-v2

**Source**: EXP-L4 (Skeptical Expert)
**Location**: Section 5.6 Internal Replication; Section 5.3.
**Issue**: Two experiment rounds test the same proxy on overlapping data (h-e1: τ = +0.564, p = 0.007; h-e1-v2: τ = +0.744, p = 0.0005). Reporting the stronger result without Bonferroni or similar adjustment inflates the nominal p-value. The paper frames this as "internal replication," which is partially correct — but the framing may not satisfy a statistical reviewer.
**Action required**: Options: (a) apply Bonferroni correction (multiply p by 2; 0.0005 → 0.001, still highly significant — easy win), or (b) add a sentence noting that both results independently exceed α = 0.05/2 = 0.025, making the conclusion robust to a two-test correction. Option (b) is one sentence and sufficient.

---

## MINOR-8: 4.6× growth — cohort-mean vs. individual growth (partially addressed)

**Source**: EXP-OC2 (Skeptical Expert)
**Location**: Section 5.3.
**Issue**: The R1 revision added "cohort-level mean growth (individual trajectories not measured)" qualification to the 4.6× figure. However, the abstract still references the finding without this qualifier ("returning users compose progressively longer... prompts"). A careful reader may still interpret the abstract as an individual-level claim.
**Action required**: Consider adding a brief qualifier in the abstract: "at the cohort level" or "in cohort-aggregate measures." Example: "returning users compose progressively longer, more elaborate prompts over the observation period (cohort-level aggregate)." Low priority — the abstract is already qualified by "returning users" which implies cohort framing.

---

## MINOR-9: Section 3.2 date range mismatch (partially addressed)

**Source**: ACC-MINOR-2
**Location**: Section 3.1 (R1 revision added parenthetical here; original issue was in 3.2).
**Issue**: The R1 revision added a parenthetical in Section 3.1 noting the effective window difference. Original Section 3.2 still states the ≥3 monthly bin filter without repeating the range clarification.
**Action required**: Verify that the parenthetical in Section 3.1 is sufficient for reader clarity. If a reviewer still finds the mismatch confusing, add one sentence at the end of Section 3.2: "The effective analysis window (April 2023–April 2024) is narrower than the planned extraction range due to the cohort-size floor applied in step 5."

---

*End of R1 human review notes. 9 MINOR issues deferred. All 8 MAJOR issues fixed in 06_paper_r1.md.*

---

# Human Review Notes: R2 MINOR Issues

**Round**: R2
**Paper**: 06_paper_r2.md (revised)
**Date**: 2026-08-31

These issues were identified in adversarial review R2 as MINOR. They have NOT been auto-fixed in the revised paper. A human author should evaluate each before submission.

---

## R2-MINOR-1: Uncorrected Mann-Kendall p-value not reported

**Source**: R2 Signal-Performance Gap Analysis
**Location**: Section 5.3; Table 1.
**Issue**: The paper reports the Hamed-Rao-corrected p = 0.0005 but not the uncorrected p-value. Given ACF lag-1 = 0.634 (high autocorrelation), the Hamed-Rao correction inflates the variance of the S statistic (making the test more conservative — i.e., the uncorrected p-value would be even more significant). Reporting both values would let readers assess the magnitude of the autocorrelation correction and demonstrate the result holds before correction.
**Action required**: Consider adding a parenthetical in Section 5.3: "(uncorrected p = [value])" after the Hamed-Rao p = 0.0005. Requires re-running standard Mann-Kendall on the same data to obtain uncorrected p.
**Priority**: LOW — the corrected value is what matters statistically; uncorrected adds context.

---

## R2-MINOR-2: tiktoken cl100k_base tokenization choice unjustified

**Source**: R2 Missing Limitations Check (L8)
**Location**: Section 3.3 Behavioral Proxy Computation.
**Issue**: The paper uses tiktoken cl100k_base without explaining why this tokenizer was chosen. cl100k_base is the tokenizer for GPT-3.5-turbo and GPT-4 (the model family underlying WildChat). A reviewer from a non-OpenAI background may question whether the tokenization is appropriate or biased.
**Action required**: Add one sentence to Section 3.3: "cl100k_base is appropriate here because WildChat logs are GPT-3.5-turbo and GPT-4 interactions, for which cl100k_base is the native tokenizer." Low-effort, pre-empts a common reviewer question.
**Priority**: LOW — the choice is correct; documentation is the only gap.

---

## R2-MINOR-3: Calendar-month binning edge effects unacknowledged

**Source**: R2 Missing Limitations Check (L9)
**Location**: Section 3.2 Returning-User Cohort Construction.
**Issue**: The pipeline bins by calendar month. Conversations near month boundaries (e.g., March 31 vs. April 1) fall into different bins. For a 13-bin monthly time series this is standard practice and unlikely to create directional bias. However, if WildChat data collection had systematic upload batches near month boundaries, this could create artificial jumps. The paper does not acknowledge this.
**Action required**: Optional one-line note in Section 3.2 or Appendix A.2: "Calendar-month binning is standard for monthly time series; boundary effects are unlikely to introduce directional bias over a 13-month window." If unfeasible, omit — the risk is low.
**Priority**: VERY LOW — standard practice.

---

## R2-MINOR-4: Appendix A.3 approximate values could cite exact source

**Source**: R2 Numerical Verification Table
**Location**: Appendix A.3.
**Issue**: A.3 presents cohort size and token mean values with "~" (approximate) qualifiers and notes "Full monthly data in `results/wildchat_monthly.csv`." A reviewer who checks the appendix may prefer exact values at least for the endpoints (April 2023, April 2024). The tilde qualifiers throughout create a slightly informal impression.
**Action required**: If `results/wildchat_monthly.csv` is accessible, replace approximate endpoint values in A.3 with exact figures and remove tilde qualifiers for those rows. Intermediate rows (2023-07, 2023-10, 2024-01) may retain approximate values if exact data is unavailable at the time of writing.
**Priority**: LOW.

---

## R2-MINOR-5: Section 5.6 "replicates and strengthens" language (now partially fixed)

**Source**: R2 Numerical Verification Table; R2-M1 fix
**Location**: Section 5.6 Internal Replication.
**Issue**: R2 revision added methodological variant language to Section 5.6 and Appendix A.1. The phrase "replicates and strengthens" was retained in Section 5.6 ("h-e1-v2 replicates and strengthens h-e1"). A strict reader may still object that "replicates" implies identical methodology. The revised Section 5.6 now adds methodological variant context, but the opening phrase remains.
**Action required**: Consider changing "replicates and strengthens" to "corroborates with a methodological variant" or "directionally replicates (methodological variant)" for precision. Small wording change only.
**Priority**: LOW — the new context added in R2 largely resolves the concern.

---

*End of R2 human review notes. 5 MINOR issues deferred. All 4 MAJOR issues fixed in 06_paper_r2.md.*
