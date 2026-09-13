# Adversarial Review Changelog
**Paper:** Gradient Alignment as Spurious-Minority Detector  
**Review Started:** 2026-08-31

---

## Round 1 Revisions (06_paper.md → 06_paper_r1.md)

**Date:** 2026-08-31  
**Issues addressed:** 5 MAJOR

---

### Change R1-01: [ACC-MAJOR-001] Remove unverified "raw cosine similarity ≈ 0.85" claim

**Section:** 5 (Results) and 3 (Methodology)  
**Original:** "spurious-minority samples appear **more** aligned with the within-batch mean (raw cosine similarity ≈ 0.85) than majority samples"  
**Revised:** Removed unverified numerical claim. Instead, added clarifying language in Section 3 Methodology explaining what ROC-AUC < 0.5 means directionally:

> "ROC-AUC of $a_i$ below 0.5 means minority samples have *lower* conflict scores — equivalently, higher raw cosine similarity with the batch mean — the opposite of the directional hypothesis."

In Section 5 Results, the inversion description now reads:
> "The conflict score $a_i$ (negated cosine similarity) is anti-predictive: minority samples score *lower* on $a_i$ than majority samples, meaning minority samples have *higher* raw cosine similarity with the within-batch mean — the direct opposite of the hypothesis."

**Rationale:** The 0.85 value did not appear in ground truth data. The directional implication is now derived from the ROC-AUC value itself rather than stated as a measured number.

---

### Change R1-02: [BR-MAJOR-001] Add proper standalone figure captions

**Section:** 5 (Results) and Appendix A, B  
**Original:** Figures referenced with single-sentence inline captions only (e.g., "*Figure 1: ROC-AUC vs. training epoch (both datasets). Figure 2: Waterbirds detail. Figure 3: CelebA detail.*")  
**Revised:** All 7 figures (Figures 1–7) now have expanded standalone captions including: what is shown, axis/data description, key observation, and source file reference.

Examples:
- Figure 1 now: "ROC-AUC vs. training epoch for gradient alignment score and per-sample loss, on Waterbirds (solid lines) and CelebA (dashed lines). Alignment ROC-AUC (blue) remains far below loss ROC-AUC (orange) at all epochs. Dotted horizontal line at 0.5 marks chance; alignment falls below chance on Waterbirds throughout training."
- Appendix figures (4–7) similarly expanded.

**Rationale:** Short inline captions prevent reviewers from evaluating figures as standalone artifacts. Expanded captions make each figure interpretable without re-reading the body text.

---

### Change R1-03: [SE-MAJOR-002] Add JTT non-reproduction disclaimer

**Section:** 2 (Related Work), end of Label-Free Debiasing Methods subsection  
**Original:** JTT numbers cited without clarification of scope.  
**Added:** "We note that our contribution is signal existence (ROC-AUC measurement), not downstream task performance, and we do not reproduce JTT or GroupDRO baselines in our experimental setup."

Also updated Section 4 Baselines:
> "We evaluate signal discriminability (ROC-AUC) rather than downstream worst-group accuracy; the latter is only relevant if the signal exists."

**Rationale:** Prevents reviewer confusion about whether JTT 86.7% is directly comparable to our experimental setup.

---

### Change R1-04: [SE-MAJOR-003] Soften "signature of batch contamination" overclaim in Conclusion

**Section:** 7 (Conclusion)  
**Original:** "This inversion is the signature of batch contamination by high-magnitude minority gradients."  
**Revised:** "This inversion is *consistent with* batch contamination by high-magnitude minority gradients."

Also in Section 6 Discussion, added explicit acknowledgment:
> "These alternatives are not ruled out by the current experiments. The batch contamination hypothesis is supported by the prevalence-dependent pattern across datasets, but definitive separation requires additional ablations."

And added to Discussion Path Forward:
> "Whether this correction resolves the inversion remains to be empirically validated."

**Rationale:** Batch contamination is a mechanistic diagnosis based on indirect evidence (prevalence-dependence pattern). Calling it a "signature" implies confirmed causality. Changed to "consistent with" throughout Discussion/Conclusion to accurately reflect the evidential status.

---

### Change R1-05: [SE-MAJOR-004] Change "is required" to "is expected to be required/necessary"

**Sections affected:** Abstract, Introduction (Contribution 3 and body), Discussion (Path Forward), Conclusion  

| Location | Original | Revised |
|----------|----------|---------|
| Abstract | "is required to avoid contamination" | "is expected to be necessary to avoid contamination" |
| Intro contribution 3 | "is required for gradient cosine similarity to retain discriminative power" | "is expected to be necessary for gradient cosine similarity to retain discriminative power" |
| Intro body | "addresses the root cause directly" | "is expected to address the root cause" |
| Discussion | "addresses the root cause" | "is expected to address the root cause" |
| Conclusion | "The correction is principled: two-pass global mean gradient..." | "The natural corrective direction is a two-pass global mean gradient..." |

**Rationale:** The two-pass global mean gradient is a mechanistic prediction — it has not been validated empirically (Limitation L4). "Required" implies empirical proof. "Expected to be necessary" accurately represents the claim as a prediction from the diagnosis.

---

### Minor Issues Collected (Not Auto-Fixed — See human_review_notes.md)

- BR-MINOR-001: Sec 6 heading style alignment with subtitle
- BR-MINOR-002: "partially recovers" imprecision for 0.349 value
- BR-MINOR-003: Table 1 column header notation (fixed in R1: changed to "WB Align", "WB Loss" etc.)
- ACC-MINOR-004: CelebA subsample description (fixed in R1: added "~10% of full 162K dataset")
- BR-MINOR-005: Abstract range clarification (fixed in R1: added "across datasets and epochs")
- SE-MINOR-006: "k ≈ 10" informal estimate note needed

*Note: BR-MINOR-003, ACC-MINOR-004, and BR-MINOR-005 were incidentally fixed during MAJOR edits. Others remain in human_review_notes.md.*

---

### Summary

| Metric | Value |
|--------|-------|
| Issues addressed | 5 MAJOR |
| Issues remaining | 0 FATAL, 0 MAJOR |
| Sections modified | Abstract, Introduction, Related Work, Methodology (Sec 3), Experimental Setup (Sec 4), Results (Sec 5), Discussion (Sec 6), Conclusion (Sec 7), Appendix A/B |
| Word count delta | ~+280 words (figure captions, clarifying sentences) |

---

## Round 2 Revisions (06_paper_r1.md → 06_paper_r2.md)

**Date:** 2026-08-31  
**Issues addressed:** 0 FATAL, 0 MAJOR, 2 MINOR (formatting improvements)

R2 numerical verification confirmed all values. No FATAL or MAJOR issues found.

### Change R2-01: [R2-MINOR-002] Table 1 gap sign convention footnote

**Section:** 5 (Results), Table 1  
**Added:** Footnote to Table 1 gap columns: "*† Gap = Align − Loss; negative values indicate alignment below loss (expected direction of failure).*"  
**Rationale:** Gap values are signed in the table (−0.780) but the text discusses magnitude (0.43–0.78). Footnote clarifies the sign convention without changing any values.

### MINOR Issues Remaining (Human Review)

- R2-MINOR-001: Sec 6 "k potentially large" — informal estimate clarification
- BR-MINOR-001: Sec 6 heading style
- BR-MINOR-002: "partially recovers" imprecision  
- SE-MINOR-006: "k ≈ 10" informal estimate (original removed in R1; note to consider adding informal bound in R2-MINOR-001)

---

## Final Summary

**Total Revisions Made:** 6 (5 MAJOR + 1 MINOR formatting fix in R2)  
**Sections Modified:** Abstract, Introduction (Sections 1, 3), Related Work (Sec 2), Experimental Setup (Sec 4), Results (Sec 5), Discussion (Sec 6), Conclusion (Sec 7), Appendix A/B  
**Word Count Change:** ~5500 (original) → ~5780 (final) (+280 words)

**Review Process:**
- Started: 2026-08-31T12:00:00+00:00
- Completed: 2026-08-31T14:00:00+00:00
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper)
- 065_review_summary.md (review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
