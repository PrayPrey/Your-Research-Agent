# Phase 6.5 Adversarial Review — R1 Changelog

**Paper:** Measuring Structural Efficiency of Policy Movement
**Revision:** R1
**Date:** 2026-05-19
**Source review:** 065_review_r1.md

---

## Issues Addressed

### SKEPT-FATAL-001 (FATAL) — Removed [Jiang et al., 2025] citation
- **Section modified:** Section 2.1 (Related Work)
- **Action:** Removed the sentence "CodeRL+ [Jiang et al., 2025] shows that variable-level execution trajectory rewards outperform binary pass/fail by +4.6% pass@1, suggesting reward granularity affects outcome." from Section 2.1.
- **References section:** Removed the entry "[Jiang et al., 2025] Xue Jiang et al. CodeRL+: Improving Code Generation via Reinforcement with Execution Semantics Alignment. arXiv:2510.18471, 2025."
- **Reason:** arXiv:2510.18471 is dated October 2025, making it impossible to cite in an ICML 2025 paper. The citation was fabricated or temporally impossible.
- **Secondary fix:** Removed mention of "CodeRL+" from Section 4.1 Datasets rationale sentence that referenced it alongside other baselines.
- **Citation count:** Reduced from 20 to 19.

### BORED-MAJOR-001 (MAJOR) — Added framework-scope framing sentence in Introduction
- **Section modified:** Section 1 (Introduction), second paragraph
- **Action:** Added bridge sentence at the end of the paragraph ending "...whether the model has learned to structure programs differently or has merely become more decisive about existing surface patterns.":
  "In this paper, we provide the measurement framework and proof-of-concept validation that makes this structural question answerable — the full-scale comparison awaits the corrected experimental protocol described in Section 6.3."
- **Reason:** Addresses reviewer concern that the paper reads as claiming full empirical results rather than a framework contribution with preliminary findings.

### BORED-MAJOR-002 (MAJOR) — Reframed Contribution 3 bold lead-in
- **Section modified:** Section 1 (Introduction), Contribution 3 bullet
- **Action:** Changed bold lead-in from "A preliminary empirical analysis with a surprising finding." to "A proof-of-concept empirical finding: a raw/proportion dissociation."
- **Body text:** Unchanged.
- **Reason:** The original phrasing "preliminary empirical analysis" undersells the specificity of the finding while "surprising" is editorially weak. The new phrasing names the actual finding (raw/proportion dissociation) and accurately scopes it as proof-of-concept.

### SKEPT-MAJOR-001 (MAJOR) — Added L5 to Limitations
- **Section modified:** Section 6.2 (Limitations), after L4 paragraph
- **Action:** Added new paragraph:
  "**L5: SEP not validated against functional outcomes.** The structural efficiency metric and SEP have not been validated against functional correctness measures (pass@1, ECE, OOD transfer). A high-SEP model might make more structural changes that are wrong. The framework measures *structural activity* of policy movement, not the *correctness* of that movement. Establishing the correlation between SEP and downstream performance is a prerequisite for using structural efficiency as an alignment quality indicator rather than a descriptive diagnostic. This validation is part of the future work outlined in Section 7.2."
- **Reason:** Critical gap — the metric has no validated relationship to functional correctness, which must be disclosed explicitly.

### SKEPT-MAJOR-002 (MAJOR) — Added note after Table 1 about identical GRPO results
- **Section modified:** Section 5.2, immediately after the Mann-Whitney U line, before Figure 4 reference
- **Action:** Added italicized note:
  "*Note:* GRPO-binary and GRPO-error-type produce identical SEP statistics because the h-m1 analysis reused h-e1 checkpoints, and the checkpoint aliasing confound (Section 5.3) caused both conditions to analyze the same aliased checkpoint-100 files. The two reward functions would produce different checkpoints in a corrected run with dedicated full-scale training; the present results cannot distinguish their structural effects."
- **Reason:** Without this note, readers might incorrectly conclude that binary and error-type rewards produce identical structural effects — a misleading empirical claim given the aliasing confound.

---

## Summary

| Issue ID | Severity | Status |
|----------|----------|--------|
| SKEPT-FATAL-001 | FATAL | Fixed |
| BORED-MAJOR-001 | MAJOR | Fixed |
| BORED-MAJOR-002 | MAJOR | Fixed |
| SKEPT-MAJOR-001 | MAJOR | Fixed |
| SKEPT-MAJOR-002 | MAJOR | Fixed |

**Total fixes applied:** 5 (1 FATAL + 4 MAJOR)
**Sections modified:** Section 1 (Introduction), Section 2.1 (Related Work), Section 4.1 (Datasets), Section 5.2 (Results), Section 6.2 (Limitations), References

**MINOR issues:** Collected in 065_human_review_notes.md — NOT fixed in R1.

---

## Round 2 (R2)

**Paper:** Measuring Structural Efficiency of Policy Movement
**Revision:** R2
**Date:** 2026-05-19
**Source review:** 065_review_r2.md

---

### MAJOR-R2-001 (MAJOR) — Added inline data-source labels for raw/proportion dissociation

- **Sections modified:** Section 5.2 (raw/proportion dissociation paragraph), Section 6.1 (Finding 2), Section 5.2 top-of-section note
- **Actions:**
  1. Added a warning note at the top of Section 5.2: "Note: The raw edit distance results reported in Section 5.1 use synthetic h-e1 proof-of-concept data; the SEP results reported in this section use real checkpoints from h-m1 but are underpowered (n_eff≈2 due to checkpoint aliasing, Section 5.3). These experiments address different questions and cannot be directly compared."
  2. In Section 5.2 dissociation paragraph, changed "+250% higher *absolute* semantic AST edit distance" to include "(h-e1 synthetic PoC data, not real training output)" and the SEP near-equality to include "(≈0.237 for both; h-m1 preliminary, n_eff≈2, underpowered)".
  3. In Section 6.1 Finding 2, added "(h-e1 synthetic PoC data, not real training output)" after the +250% claim and "(≈0.237 for both methods; h-m1 preliminary, n_eff≈2)" after the SEP claim.
  4. Added inline note after the proof-of-concept table in Section 5.1: "†Note: The above results are from h-e1 synthetic (hand-crafted) proof-of-concept data... DPO training in h-e1 used stub preference pairs rather than genuine execution-oracle pairs (see Limitation L4 in Section 6.2), which may suppress DPO's structural activity and inflate the apparent raw edit distance advantage."
- **Reason:** The dissociation presented GRPO's +250% raw edit distance (from h-e1, synthetic data) and ≈0.237 SEP near-equality (from h-m1, aliased real data) side-by-side as if comparable. Without inline source labels, readers of Section 5.2 and 6.1 must cross-reference Section 6.2 to understand these are fundamentally different experimental contexts.

---

### MAJOR-R2-002 (MAJOR) — Hedged "previously undocumented" checkpoint aliasing claims

- **Sections modified:** Abstract, Section 1 (Contribution 4), Section 5.3, Section 6.1 (Finding 3)
- **Actions:**
  1. Abstract: Changed "checkpoint aliasing as a previously undescribed confound" → "checkpoint aliasing as a confound not, to our knowledge, previously documented in the RL fine-tuning literature".
  2. Section 1 Contribution 4: Changed "has not been previously documented" → "has not, to our knowledge, been previously documented".
  3. Section 5.3: Changed "a confound that has not been previously documented in the RL fine-tuning literature" → "a confound that has not, to our knowledge, been previously documented in the RL fine-tuning literature".
  4. Section 6.1 Finding 3: Changed "Checkpoint aliasing is a previously undocumented methodological confound" → "Checkpoint aliasing is a confound not, to our knowledge, previously documented in the RL fine-tuning literature".
- **Reason:** The unhedged phrase "previously undocumented" appeared three times without hedging language or a negative citation. The ground truth itself notes the claim "cannot be fully verified without exhaustive literature review." Adding "to our knowledge" qualifies the novelty claim appropriately without weakening the contribution.

---

### MAJOR-R2-003 (MAJOR) — Added implementation note to DPO row in Section 4.3 conditions table

- **Section modified:** Section 4.3 (Alignment Methods table)
- **Action:** Changed DPO reward signal description from:
  "Execution-oracle preference pairs (passing solution preferred over failing)"
  to:
  "Execution-oracle preference pairs (passing solution preferred over failing) [intended design; see L4 in Section 6.2 for actual implementation note]"
- **Reason:** The table described the intended design for DPO, but the actual h-e1 implementation used stub preference pairs (`return None` as rejected completion). The inconsistency between Section 4.3 (intended design) and Section 6.2 L4 (actual implementation) could mislead readers who stop at the Methods section without reading Limitations. The cross-reference resolves the inconsistency without restructuring the table.

---

### R2 Summary

| Issue ID | Severity | Status |
|----------|----------|--------|
| MAJOR-R2-001 | MAJOR | Fixed |
| MAJOR-R2-002 | MAJOR | Fixed |
| MAJOR-R2-003 | MAJOR | Fixed |

**Total fixes applied in R2:** 3 MAJOR (0 FATAL)
**Sections modified:** Abstract, Section 1 (Introduction), Section 4.3 (Alignment Methods), Section 5.1 (Results — PoC table note), Section 5.2 (Results — dissociation paragraph + top note), Section 5.3 (Checkpoint Aliasing), Section 6.1 (Finding 2 and Finding 3)

**MINOR issues from R2:** Collected in 065_human_review_notes.md — NOT fixed in R2.

---

## Final Summary (v2.0)

**Total Revisions Made**: 8 (1 FATAL + 7 MAJOR)
**Sections Modified**: Abstract, Section 1 (Introduction), Section 2.1 (Related Work), Section 4.3 (Alignment Methods), Section 5.1 (Results — PoC table), Section 5.2 (Results — SEP), Section 5.3 (Checkpoint Aliasing), Section 6.1 (Discussion), Section 6.2 (Limitations), References
**Word Count Change**: ~7,200 → ~7,350 (approx. +150 words net, from added notes and L5)

**Review Process**:
- Started: 2026-05-19T12:30:00Z
- Completed: 2026-05-19T14:00:00Z
- Rounds: 2 (R1: Three-Persona; R2: Accuracy+Credibility)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert
- Convergence: FATAL=0, MAJOR=0, persuasiveness_passed=true → CONVERGED after R2

**Files Generated**:
- 06_paper_final.md (final reviewed paper)
- 065_review_summary.md (consolidated review summary)
- 065_human_review_notes.md (7 MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_checkpoint.yaml (state tracking)
- 065_review_r1.md (Round 1 adversary report)
- 065_review_r2.md (Round 2 adversary report)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
