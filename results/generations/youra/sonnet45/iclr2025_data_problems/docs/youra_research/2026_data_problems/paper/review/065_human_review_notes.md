# Human Review Notes
# Phase 6.5 Adversarial Review — Minor Issues for Human Review

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI. All items below require human judgment.

**Generated:** 2026-03-17T21:00:00Z
**Rounds Completed:** 2

---

## Summary by Category

| Category | Round 1 | Round 2 | Total |
|----------|---------|---------|-------|
| Typography/Formatting | 2 | 2 | 4 |
| Terminology/Consistency | 2 | 2 | 4 |
| Precision/Rounding | 1 | 1 | 2 |
| Verification/Accuracy | 2 | 1 | 3 |
| **TOTAL** | **7** | **6** | **13** |

---

## Round 1 Issues (from R1 adversarial review)

### Typography / Formatting

**HRN-001**
- **Category:** Formatting
- **Location:** Abstract
- **Issue:** `*negatively*` is Markdown asterisk formatting. Verify this renders as proper italics in PDF (LaTeX should use `\textit{negatively}`). In a camera-ready submission, Markdown asterisks will not automatically convert.
- **Suggested fix:** Replace with proper LaTeX `\textit{}` when converting to final format (handled by Phase 6.5.1).

**HRN-002**
- **Category:** Terminology
- **Location:** Table 2.5 heading row
- **Issue:** Table uses "OLL Leaderboard" (abbreviated) while body text uses "Open LLM Leaderboard." Use one abbreviation consistently. "OLLB" or "Open LLM Leaderboard" — pick one and apply throughout.
- **Suggested fix:** Choose "Open LLM Leaderboard" (spelled out) or define "OLLB" as abbreviation at first use.

### Terminology / Consistency

**HRN-003**
- **Category:** Precision
- **Location:** Abstract vs. Introduction vs. Results
- **Issue:** β reported as −3.45 in Abstract and Introduction; −3.4520 in Results (Table 4). This is not an error (both are correct), but the inconsistency creates the impression of selective precision in persuasive vs. empirical sections. Consider adding "approximately" or using consistent precision.
- **Suggested fix:** Use −3.45 consistently throughout with one note "(exact: −3.4520)" in Table 4, or use the full precision uniformly.

**HRN-004**
- **Category:** Precision
- **Location:** Table 1
- **Issue:** n_positive = 158 (Table 1, ground_truth.yaml) vs. "n_positive ≈ 156" (045_validated_hypothesis.md). While 158 is consistent with ground_truth.yaml arithmetic (4,493 − 4,335 = 158), the validated_hypothesis.md says ~156 and 04_validation.md implies 156. A 2-unit discrepancy.
- **Suggested fix:** Verify exact value from h-e1-v2/data/registry.csv. Use the verified count consistently.

### Verification

**HRN-005**
- **Category:** Verification
- **Location:** §2.1
- **Issue:** "a 10% improvement in effective data quality is equivalent to a ~4.5% increase in training tokens" — verify this is a direct numerical result from Subramanyam et al. [2025] using γ_CLM ≈ 0.39, not the authors' own calculation. If authors calculated this, add "(authors' calculation from γ_CLM ≈ 0.39)."
- **Suggested fix:** Add footnote or parenthetical clarifying whether this is a direct quote/result or a derived calculation.

**HRN-006**
- **Category:** Verification / Accuracy
- **Location:** Abstract, References
- **Issue:** "The registry, code, and methodology will be released upon publication" — verify this is true. If data or code has any licensing or institutional constraints, this statement needs to be more specific.
- **Suggested fix:** Confirm release plan. If releasing on HuggingFace/GitHub, consider adding the planned repository URL (or placeholder) at camera-ready.

### Style

**HRN-007**
- **Category:** Style
- **Location:** §1 Introduction, paragraph 2
- **Issue:** "Data quality is widely recognized as a critical determinant of large language model (LLM) performance." — this is a standard "X is important" weak opener that many ICML/NeurIPS writing guides flag. The paper's Introduction paragraph 1 now leads with the finding (fixed in R1), but paragraph 2 reverts to motivation language.
- **Suggested fix:** Consider whether paragraph 2 can be restructured to continue from the finding rather than reset to motivation. Optional — subjective style preference.

---

## Round 2 Issues (from R2 adversarial review)

### Typography / Formatting

**HRN-R2-A**
- **Category:** Formatting
- **Location:** §5.2
- **Issue:** "explains only 42.47% of V2 benchmark variance" in Results vs. "approximately 42% (R² = 0.4247)" in Abstract — both correct, but different precision levels within one document. Minor stylistic inconsistency.
- **Suggested fix:** Acceptable as-is (abstract rounds, results are precise). Optionally add "(R² = 0.4247)" inline in §5.2 for completeness.

**HRN-R2-B**
- **Category:** Formatting
- **Location:** §5.1, §5.2, §5.3
- **Issue:** Figures referenced as inline text "(dropout_funnel.png)" rather than proper LaTeX figure environments with captions, labels, and \ref{} cross-references. This will fail venue formatting requirements for camera-ready.
- **Suggested fix:** Phase 6.5.1 (Overleaf generation) should convert these to proper `\begin{figure}...\end{figure}` environments with `\caption{}` and `\label{}`.

### Terminology / Consistency

**HRN-R2-C**
- **Category:** Clarity
- **Location:** Table 1
- **Issue:** "Targeted family models prioritized | 114" — only 114 of 4,493 were targeted, but 3,749 cards were retrieved. A reader will wonder: if only 114 were targeted, where did the other 3,635 retrieved cards come from? §3.3 explains this (non-targeted models are retrieved after priority families within API budget), but Table 1 has no footnote.
- **Suggested fix:** Add footnote to Table 1: "114 models matched targeted family prefixes and were prioritized for retrieval; remaining cards retrieved within the same API budget window."

**HRN-R2-D**
- **Category:** Consistency
- **Location:** Paper metadata header
- **Issue:** `hypothesis_id: H-DocCuration-v1` contains "v1" while the paper uses Open LLM Leaderboard v2 data. The naming inconsistency (hypothesis designed for v1, executed on v2) could confuse careful referees. This is a provenance note, not a scientific error.
- **Suggested fix:** Add a note in the metadata or §3.2 explaining that H-DocCuration-v1 refers to the hypothesis version identifier, not the leaderboard version. Or note "hypothesis originally designed for v1 leaderboard; executed on v2 due to improved benchmark coverage."

### Verification

**HRN-R2-E**
- **Category:** Precision / Verification
- **Location:** §1 Introduction, §6.1
- **Issue:** "only 3.5% document any pretraining data curation practice" — exact value is 158/4,493 = 3.517%, which rounds correctly to 3.5%. Confirmed accurate. No change needed, but author should verify the exact n_positive count (see HRN-004) before final submission.
- **Suggested fix:** After resolving n_positive discrepancy (HRN-004), confirm this percentage is consistent.

**HRN-R2-F**
- **Category:** Verification
- **Location:** §3.4 (new robustness note from R2)
- **Issue:** "log(doc_score + 1) alternative specification produces qualitatively consistent directional finding (β_log < 0, p < 0.01)" — this was added as a robustness note, but β_log was not computed from actual data. The p < 0.01 threshold is hedged language but has no verified ground truth. Authors should verify this claim before submission.
- **Suggested fix:** Either (a) run the log specification and report the actual β_log and p-value, or (b) change to "We expect log(doc_score + 1) to produce a consistent directional finding given the monotone transformation and the statistical significance of the linear specification" to avoid claiming a result that wasn't computed.

---

## Recommended Priority for Human Review

1. **Fix First (HRN-R2-F):** The log(doc_score+1) claim — either verify empirically or soften language. This is the most substantively important minor issue.
2. **Fix Second (HRN-004):** Verify n_positive exact count from registry.csv.
3. **Fix Third (HRN-R2-C):** Add Table 1 footnote on targeted vs. total retrieval.
4. **Fix Fourth (HRN-005):** Verify Subramanyam γ_CLM calculation attribution.
5. **Consider (HRN-R2-B):** Phase 6.5.1 should handle figure formatting.
6. **Optional (HRN-007):** Style revision to Introduction paragraph 2.

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer experience. All FATAL and MAJOR issues have been addressed in R1 and R2 revisions.*
