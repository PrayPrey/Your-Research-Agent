# Human Review Notes

> Purpose: Minor issues from adversarial review (Round 1) for human review. NOT auto-fixed in 06_paper_r1.md.

**Date**: 2026-08-26
**Rounds**: R1

---

## Summary by Category

| Category | Count |
|----------|-------|
| Grammar | 1 |
| Style | 2 |
| Clarity | 3 |
| Formatting | 2 |
| Minor factual note | 1 |
| **Total** | **9** |

---

## Round 1 Issues

### Grammar

1. **Section 5.2, caveat sentence** — "we attribute this likely to digitization idealization" is awkward. Should be "we attribute this most likely to digitization idealization" or "this is most likely attributable to digitization idealization." *(Note: the R1 paper already changed "likely" to "most likely" in this caveat as part of the incidental edit pass — verify this landed correctly in the final PDF.)*

---

### Style

2. **Introduction bold headers** — The bold-header pattern ("The surface problem," "The deeper problem," "The gap we address") is effective narratively but atypical for ICML format. Verify this pattern is compliant with ICML 2025 author instructions before camera-ready submission.

3. **Section 4.3 Implementation Details** — The mention of "dataclass configuration, flat `src/` layout, and `sys.exit(0/1)` gate result" is implementation-speak that is meaningless to a paper reviewer and reads as padding. Consider trimming to just the key hyperparameters (bootstrap N, seed, CI level) or removing the structural details entirely.

---

### Clarity

4. **Section 3.5 step list** — The original bullet list made the step count ambiguous during proofreading, which contributed to the Step 5/Step 4 error (MAJOR-2). The R1 revision converts this to a numbered list; verify the numbered list renders correctly in the LaTeX build and that no downstream section references (e.g., "Steps 2–3" in the Figure 1 caption) need updating.

5. **Section 6.1, Finding 2** — The parenthetical "(n=2 datasets; further replication required to establish universality)" was added as the MAJOR-3 fix. A skeptical expert may also note that the two datasets are not fully independent at the paradigm level (both use PPO-based RLHF from human preference annotations). Consider adding a sentence explicitly scoping the replication's independence: e.g., "both datasets use PPO-based RLHF; replication across DPO or constitutional AI paradigms remains future work."

6. **Introduction, ICLR 2025 survey claim** — Section 1 ("The gap we address") presents the ICLR 2025 Workshop finding ("synthesized 400 papers and found...") without a caveat that this is an external qualitative finding not independently verified by this paper. Consider adding "(qualitative finding from the workshop survey, not independently verified in this work)" at first mention to pre-empt a reviewer who might interpret it as a result of this paper. This is consistent with L3 in Section 6.3 but should be flagged at first use.

---

### Formatting

7. **Gao bootstrap CI negative sign** — Section 5.5 table shows "−0.020" in the Bootstrap 95% CI cell. Verify this renders as a proper mathematical minus sign in LaTeX (use `$-0.020$` in math mode) rather than an en-dash or typographic minus that may display incorrectly in some PDF viewers.

8. **References venue formatting** — The references section uses inconsistent venue formatting: some entries italicize the venue (*NeurIPS 2022*, *ICML 2023*), some use plain text (*DeepMind Blog*), and one entry (ICLR 2025 Workshop) has no venue field at all. Standardize to a single style before camera-ready submission — either all venues italicized or all plain, following ICML 2025 bibliography style guidelines.

---

### Minor Factual Note

9. **Datasets independence caveat (missing limitation)** — The adversarial review noted that the two datasets are not fully paradigm-independent: both use PPO-based RLHF trained on human preference annotations, and Gao et al. was published contemporaneously and may share experimental design influences with Coste et al. True paradigm-level independence would require comparison across DPO, constitutional AI, or RLAIF settings. The paper's replication claim is accurate as stated (different model family, different scale, different task distribution), but adding a short acknowledgment of this scope limitation in Section 6.3 would pre-empt a skeptical expert's objection. This is distinct from L1–L4 already listed and could be added as L5.

---

## Round 2 Issues (4 new)

### Style

1. **HRN-R2-2: Gao p-value rounding inconsistency** — Abstract states "p = 0.003"; Section 5.5 table states "0.0025". Both are correct roundings of 2.515e-03. If an editor asks for consistency, update abstract to "p = 0.003" (acceptable for space) or add a footnote clarifying both refer to the same value. Current state is acceptable but cosmetically inconsistent.

2. **HRN-R2-3: Gao bootstrap CI lower bound precision** — Paper reports "−0.020"; validation file shows −0.0203. Both are correct rounding. Given that the overlap with zero is the primary concern, reporting "−0.0203" (matching the validation file exactly) would be slightly more precise and easier to verify. Optional fix.

### Clarity

3. **HRN-R2-4: Piecewise linear regression preemption for Gao** — Section 7 (Future Directions) item (b) mentions piecewise linear regression as a follow-up. A skeptical reviewer on Gao's R² = 0.701 may ask "why not fit piecewise now?" Adding one sentence to Section 5.5 noting that a piecewise model (breakpoint at ~3.5 nats) would better fit the Gao trajectory but that the linear model is used for cross-dataset comparability would preempt this objection. The argument is valid and defensible.

### Minor factual note

4. **HRN-R2-1 (MAJOR addressed)**: The DW=0.411 disclosure gap was the MAJOR-R2-1 issue and has been fixed in 06_paper_r2.md as limitation L5. No further action needed unless a reviewer asks for a formal Newey-West or GLS robustness check — in which case, the response is that the bootstrap CI already provides the autocorrelation-robust inference path and the point estimate β is unbiased.
