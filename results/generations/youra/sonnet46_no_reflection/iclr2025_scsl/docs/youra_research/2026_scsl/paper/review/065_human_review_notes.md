# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI (except those resolved in-round as part of cleanup).

**Generated**: 2026-05-20T07:15:00
**Rounds Completed**: 2 (R1, R2)

---

## Summary by Category

| Category | Total Found | Fixed In-Round | Deferred for Human Review |
|----------|-------------|----------------|--------------------------|
| Typo | 0 | 0 | 0 |
| Grammar | 0 | 0 | 0 |
| Style | 2 | 1 | 1 |
| Clarity | 8 | 5 | 3 |
| Formatting | 3 | 2 | 1 |
| **Total** | **13** | **8** | **5** |

---

## Issues Fixed In-Round (R1/R2 cleanup — already applied to 06_paper_final.md)

These were addressed during revision as part of MINOR cleanup:

| ID | Type | Location | Issue | Status |
|----|------|----------|-------|--------|
| MINOR-001 | Formatting | YAML frontmatter | Pipeline metadata fields (hypothesis_id, generated_by) | FIXED in R1 |
| MINOR-002 | Formatting | Appendix | Pipeline statistics block (word counts, pipeline_version, narrative_coherence) | FIXED in R1 |
| MINOR-003 | Formatting | References | [UNVERIFIED] tags on three citations | FIXED in R1 |
| MINOR-004 | Clarity | Section 6.3 L4 | "Gate failure" pipeline-internal language | FIXED in R1 |
| MINOR-005 | Clarity | Section 3.3 table | CelebA spurious attribute mislabeled as "Biological sex" (should be "Hair color") | FIXED in R1 |
| MINOR-R2-003 | Style | Section 7 | GSB acronym without parenthetical on first mention | FIXED in R2 |
| MINOR-R2-004 | Clarity | Section 5.2/5.3 | Figure paths as placeholders | NOTED — verify before submission |
| MINOR-R2-005 | Formatting | Section 3.3 | Table column alignment per ICML 2025 style | NOTED — verify before submission |

---

## Deferred Issues for Human Review

These issues remain in `06_paper_final.md` and require human judgment before submission.

---

### MINOR-006 — Clarity
**Location**: Section 5.1  
**Issue**: Purity gap precision inconsistency.

The text states: "CelebA purity (0.456) is only 0.016 above the random baseline (0.440)"

Actual values: purity=0.4557, random purity=0.4395, gap=0.0162.

The gap is computed from rounded values (0.456 − 0.440 = 0.016) rather than unrounded values (0.4557 − 0.4395 = 0.0162). Numerically inconsequential, but technically inconsistent precision.

**Suggested fix**: Either report the unrounded gap ("0.0162") or add a note: "computed from rounded values."

---

### MINOR-007 — Clarity
**Location**: Sections 2.1 and 2.2  
**Issue**: LFR vs DFR naming may confuse readers.

Section 2.1 introduces DFR ("Deep Feature Reweighting") as retraining "only the last linear layer." Section 2.2 introduces LFR ("Last-Layer Feature Reweighting") with a similar description. The similar names and similar mechanisms may confuse readers unfamiliar with both methods.

R1 revision added one sentence distinguishing LFR and DFR. A reviewer may still flag this as unclear if they encounter Section 2.2 before Section 2.1 (e.g., when reading related work selectively).

**Suggested fix**: Add a brief parenthetical to the LFR mention: "(not to be confused with DFR — LFR uses training-loss-based resampling, not group-labeled retraining)."

---

### MINOR-008 — Style
**Location**: Section 1, contributions list  
**Issue**: Contribution items lack section cross-references.

C1 through C4 do not include "(see Section X)" pointers. A reviewer scanning the paper structure after reading the contributions will have to search for where each contribution is demonstrated.

**Suggested fix**: Add cross-references:
- C1: "(see Sections 3–5)"
- C2: "(see Section 5.1, Table 1)"  
- C3: "(see Section 6.2)"
- C4: "(see Section 5.5)"

---

### MINOR-R2-001 — Clarity
**Location**: Section 4.2  
**Issue**: Random baseline description ambiguous.

"randomly shuffled cluster assignments (preserving cluster sizes)" — it is not immediately clear whether "preserving cluster sizes" means the shuffled assignment maintains the same number of samples per cluster as the original k-means assignment, or maintains the original group sizes. The former is standard practice; the latter would be unusual.

**Suggested fix**: Clarify: "randomly shuffled cluster assignments (same cluster sizes as k-means output, shuffled across samples)."

---

### MINOR-R2-002 — Clarity
**Location**: Section 3.4  
**Issue**: Probe epoch not distinguished from training epoch in implementation table.

The implementation table lists "Probe epoch | 5" separately from training, but the table does not make clear that epoch 5 is the only checkpoint saved and that training stops at epoch 5 (not that training continues and epoch 5 is one of many checkpoints).

**Suggested fix**: Add footnote to table: "Training terminates at epoch 5; no later checkpoints are used."

---

## Recommended Priority for Human Review

1. **Fix First**: MINOR-006 (purity gap precision — Section 5.1, high visibility number claim)
2. **Fix Second**: MINOR-008 (contribution cross-references — improves reviewer navigability)
3. **Consider**: MINOR-007 (LFR/DFR distinction — low risk but cleaner)
4. **Consider**: MINOR-R2-001 (random baseline clarification — methodological clarity)
5. **Optional**: MINOR-R2-002 (probe epoch footnote — minor but technically precise)

---

*Note: These issues do not block paper acceptance but improve overall quality. All FATAL and MAJOR issues have been resolved in the adversarial review process.*
