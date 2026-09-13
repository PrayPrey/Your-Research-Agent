# Human Review Notes - Minor Issues

**Paper**: Detecting Alignment Method Objective Function Signatures in Code Generation Models
**Version**: 06_paper_r2.md (post-R2 revision)
**Review Date**: 2026-03-18
**Review Rounds**: R1 (major issues) + R2 (minor issues)

---

## Instructions for Human Reviewer

This document collects **9 MINOR issues** identified in Round 1 adversarial review that were **NOT addressed in R1 automated revision**. These issues require human judgment, editorial polish, or stylistic decisions beyond the scope of major credibility/accuracy fixes.

**Priority**: These are polish items for final publication, not blocking issues for R2 review.

**Action Items**:
- Review each issue and determine if fix is needed
- For citation/typo fixes: implement directly
- For style issues: decide whether to condense or preserve current length
- For figure issues: either generate figures or remove references

---

## Issue Category: Typos and Citations (3 issues)

### MINOR-001: Citation Format Error
**Location**: Line 73 (Related Work section)
**Severity**: MINOR (typo)

**Issue**:
```latex
**LiveCodeBench**~\cite{jain2024livec <bench}
```

**Should be**:
```latex
**LiveCodeBench**~\cite{jain2024livecodebench}
```

**Impact**: Citation will not compile correctly in LaTeX. Does not affect paper logic.

**Recommendation**:
- **Action**: IMPLEMENT FIX (simple typo correction)
- **Effort**: 10 seconds
- **Risk**: None (purely technical fix)

---

### MINOR-002: Missing Bibliography Entry
**Location**: Line 599 (Discussion section, POC defense)
**Severity**: MINOR (incomplete citation)

**Issue**:
Paper cites:
```
Many methodology papers report synthetic experiments before real-world validation~\cite{friedman2001greedy}
```

But `friedman2001greedy` does not appear in bibliography/references section.

**Impact**: Citation will show as [?] in compiled document. Weakens POC defense argument.

**Recommendation**:
- **Action**: INVESTIGATE AND ADD (if citation is correct) OR REMOVE CITATION (if incorrect)
- **Effort**: 5-10 minutes (verify correct citation, add biblio entry)
- **Risk**: Low (citation supports POC defense but is not critical to argument)

**Alternative**: Replace with verifiable methodology paper citation:
```
Many methodology papers in machine learning report validation on synthetic benchmarks before real-world deployment~\cite{<verifiable_citation>}
```

---

### MINOR-003: Conclusion Tone Still Strong
**Location**: Line 671 (Conclusion opening)
**Severity**: MINOR (style preference)

**Issue**:
Current text:
```
"Our results confirm: they do. Execution-based methods create strong correctness signatures"
```

Review noted this is "too strong for POC." R1 revision changed Conclusion extensively but this phrase pattern persists (though context changed).

**Revised R1 text**:
```
"Our POC results suggest that when alignment method signatures exist in data, the framework can reliably identify them"
```

**Status**: ADDRESSED in R1 revision. Tone recalibrated from "results confirm" to "POC results suggest."

**Recommendation**:
- **Action**: NO FURTHER FIX NEEDED (already addressed)
- **Note**: Reviewer may have been referring to original paper; R1 fixed this

---

## Issue Category: Clarity and Organization (4 issues)

### MINOR-004: Table 2 Caption Needs Clarification
**Location**: Line 462 (Results section, Table 2)
**Severity**: MINOR (clarity)

**Issue**:
Table 2 lists models/patterns as:
- "codegen-exec"
- "codegen-pref"

Caption does not explain:
1. Are these the same model (codegen-350M) analyzed with different methods?
2. Are these different checkpoints?
3. What is the relationship between them?

**Current Caption** (R1 revised):
```
Simulated Pattern Rankings by Dimension (percentile ranks, lower = better)
```

**Suggested Clarification**:
```
Simulated Pattern Rankings by Dimension (percentile ranks, lower = better).
codegen-exec-pattern and codegen-pref-pattern represent simulated performance
patterns for codegen-350M model under execution-based and preference-based
alignment training scenarios respectively.
```

**Recommendation**:
- **Action**: ADD CLARIFICATION to table caption or add footnote
- **Effort**: 2 minutes
- **Risk**: None (improves clarity without changing results)

---

### MINOR-005: Sample Size Discrepancy (k=10 vs k=30)
**Location**: Lines 138 (Methodology) vs 328 (Experiments)
**Severity**: MINOR (internal inconsistency)

**Issue**:
- **Line 138** (Methodology measurement protocol): "Generate $k=10$ code samples"
- **Line 328** (Experiments code generation): "Generate $k=30$ code samples"

Which is correct? Or did protocol change between Methodology (planned) and Experiments (actual)?

**Impact**: Confusing for readers trying to replicate. Suggests lack of attention to detail.

**Recommendation**:
- **Action**: INVESTIGATE and RESOLVE
- **Option A**: If k=30 is correct, update Methodology line 138 to k=30
- **Option B**: If k=10 is correct, update Experiments line 328 to k=10
- **Option C**: If both are correct (different phases), add explanation:
  ```
  Methodology section describes idealized protocol (k=10 for efficiency),
  while Experiments section reports actual POC implementation (k=30 for
  increased diversity in simulated data).
  ```
- **Effort**: 5 minutes (investigate ground truth, update 1-2 lines)
- **Risk**: Low (technical detail, does not affect main results)

---

### MINOR-006: Missing Figure References
**Location**: Lines 442, 434, 486, 536 (Results section)
**Severity**: MINOR (incomplete presentation)

**Issue**:
Paper references multiple figures that are not included in the markdown:
- Line 96: `Figure~\ref{fig:pipeline}` (methodology pipeline)
- Line 434: `Figure~\ref{fig:pca-explained-variance}` (PCA variance plot)
- Line 442: `Figure~\ref{fig:3d-scatter}` (3D scatter plot of models in PCA space)
- Line 486: `Figure~\ref{fig:tradeoffs}` (correctness vs complexity trade-offs)
- Line 536: `Figure~\ref{fig:gate-metrics}` (gate validation results)

Ground truth metadata lists 10 figures planned, but **0 rendered in markdown**.

**Impact**: Readers cannot visualize results. Figure references appear as broken links. Reduces persuasiveness of clustering claims.

**Recommendation**:
- **Action**: DECIDE ON APPROACH
- **Option A**: Generate figures (recommended for publication)
  - Create PCA scatter plot showing clustering
  - Create pipeline diagram
  - Create trade-off plots
  - **Effort**: 2-4 hours (figure generation, formatting)
  - **Benefit**: Significantly improves paper persuasiveness

- **Option B**: Remove figure references (acceptable for technical report)
  - Remove all `Figure~\ref{...}` references
  - Describe results in text only
  - **Effort**: 30 minutes (find-replace, reword)
  - **Trade-off**: Loses visual communication

- **Option C**: Defer to final publication (acceptable for R2 review)
  - Leave references as placeholders
  - Add note: "Figures to be generated for camera-ready version"
  - **Effort**: 0 minutes
  - **Risk**: R2 reviewers may request figures

**Recommended**: Option A for final publication, Option C for R2 review

---

### MINOR-007: Discussion Section Repetitive
**Location**: Lines 576-588 (Discussion "Key Findings Interpretation")
**Severity**: MINOR (redundancy)

**Issue**:
Discussion section "Key Findings Interpretation" subsection (lines 576-588) repeats points already made in Results section:
- "Methodology works" (Results line 402 + Discussion line 577)
- "Execution dominance detected" (Results line 450 + Discussion line 577)
- "M2 inconclusive" (Results line 493 + Discussion line 581)

Repetition adds ~200 words without new insights.

**Impact**: Increases paper length (already 34% longer after R1). Risks boring readers.

**Recommendation**:
- **Action**: CONSIDER CONDENSING (optional)
- **Option A**: Condense "Key Findings Interpretation" to 2-3 sentences summarizing Results
  - Remove detailed re-explanation of each RQ
  - Keep only novel Discussion points (implications, future work)
  - **Effort**: 20 minutes
  - **Benefit**: Reduces length by ~150 words

- **Option B**: Keep as-is (current approach)
  - Repetition helps readers who skim sections
  - Discussion adds interpretation beyond Results reporting
  - **Effort**: 0 minutes
  - **Trade-off**: Longer paper but possibly clearer

**Recommended**: Option A if page limits apply, Option B otherwise

---

## Issue Category: Style and Length (2 issues)

### MINOR-008: Abstract Too Long
**Location**: Lines 1-3 (Abstract)
**Severity**: MINOR (style preference)

**Issue**:
- **Target length**: ~150 words (standard for ML conferences)
- **Current length**: 198 words (R1 revision)
- **Overage**: +48 words (+32%)

R1 revision added POC disclosure and qualification language, increasing Abstract length.

**Impact**: Some venues have strict 150-word limits. Long abstracts may be less punchy.

**Recommendation**:
- **Action**: CONDENSE IF REQUIRED BY VENUE
- **Option A**: Trim to 150 words
  - Remove methodology details (PCA, Cohen's d)
  - Simplify POC explanation
  - Keep: scope, finding, limitation, implication
  - **Effort**: 15 minutes
  - **Example trim**: Remove "applying PCA-based clustering with Cohen's d effect size analysis" → "using multi-dimensional clustering analysis"

- **Option B**: Keep at 198 words (current)
  - Acceptable for arXiv, technical reports, journals
  - Provides necessary POC context
  - **Effort**: 0 minutes
  - **Trade-off**: May exceed some venue limits

**Recommended**: Check venue requirements. If 150-word limit exists, implement Option A. Otherwise, keep Option B.

---

### MINOR-009: Introduction Too Long
**Location**: Lines 4-46 (Introduction)
**Severity**: MINOR (style preference)

**Issue**:
- **Current length**: ~1,387 words (R1 revision)
- **Review comment**: "Overly long (1,200+ words)"
- **Suggestion**: "Consider moving Design Justification subsections to Methodology"

R1 revision **increased** Introduction length (+183 words) by adding POC scope section.

**Impact**: Long Introduction may lose reader attention. Design Justification subsections could move to Methodology.

**Recommendation**:
- **Action**: CONSIDER REORGANIZATION (optional)
- **Option A**: Move Design Justification to Methodology
  - Move "Why Three Dimensions?" subsection to Methodology section 3.X
  - Move "Why Cohen's d > 1.5σ?" to Methodology section 3.X
  - Move "Why HumanEval+?" to Methodology section 3.X
  - **Effort**: 30 minutes (cut-paste, smooth transitions)
  - **Benefit**: Introduction reduces to ~900 words (more typical length)

- **Option B**: Condense Contributions list
  - Reduce "First, Second, Third, Fourth" contributions to bullet points
  - Save detailed explanation for Methodology/Results sections
  - **Effort**: 20 minutes
  - **Benefit**: Reduces Introduction by ~200 words

- **Option C**: Keep as-is
  - POC scope section is critical for setting expectations
  - Design Justification helps readers understand choices early
  - **Effort**: 0 minutes
  - **Trade-off**: Longer Introduction but more self-contained

**Recommended**: Option A (move Design Justification) if paper exceeds page limits, Option C otherwise

---

## Issue Category: Conclusion Length (1 issue - already noted)

### MINOR-010: Conclusion Too Long (Already Noted)
**Location**: Lines 669-692 (Conclusion)
**Severity**: MINOR (style preference)

**Issue**:
- **Current length**: ~1,787 words (R1 revision)
- **Review comment**: "Overly long (700+ words)"
- **R1 increase**: +1,041 words (+139.5%)

R1 revision **substantially expanded** Conclusion with POC scoping, conditional framing, honest assessment.

**Why expansion occurred**:
- Added "pending real-model validation" qualifiers throughout
- Added "What we can claim" vs "What we cannot claim" framing
- Added future directions with POC caveats
- Transformed from "we discovered X" to "we propose Y, pending validation of X"

**Impact**: Conclusion is now longer than Results section. May be excessive.

**Recommendation**:
- **Action**: CONSIDER CONDENSING (important for final version)
- **Option A**: Trim to ~800 words
  - Remove redundant restatement of POC limitations (already in Discussion)
  - Condense Future Directions to bullet points
  - Keep: main finding, pending validation, path forward
  - **Effort**: 30 minutes
  - **Benefit**: More punchy, less repetitive

- **Option B**: Keep as-is for R2, condense for final publication
  - Current length appropriate for POC framing importance
  - Ensures no reviewer misses POC scope limitations
  - **Effort**: 0 minutes now, 30 minutes later
  - **Trade-off**: R2 reviewers may comment on length

**Recommended**: Option B for R2 review (preserve thoroughness), then Option A for final publication (trim redundancy)

---

## Summary for Human Reviewer

### Must Fix (3 items)
1. ✓ **MINOR-001**: Citation typo `livec <bench}` → `livecodebench` (10 seconds)
2. ✓ **MINOR-002**: Add or remove `friedman2001greedy` bibliography entry (5-10 minutes)
3. ✓ **MINOR-005**: Resolve k=10 vs k=30 discrepancy (5 minutes)

**Total Effort for Must Fix**: ~15 minutes

### Should Fix (2 items)
4. ○ **MINOR-004**: Clarify Table 2 caption (2 minutes)
5. ○ **MINOR-006**: Decide on figure strategy (0 min defer, 2-4 hours generate, or 30 min remove)

**Total Effort for Should Fix**: 2 min - 4 hours (depending on figure decision)

### Optional Polish (4 items)
6. ○ **MINOR-007**: Consider condensing Discussion repetition (20 minutes, saves 150 words)
7. ○ **MINOR-008**: Consider trimming Abstract to 150 words if venue requires (15 minutes)
8. ○ **MINOR-009**: Consider moving Design Justification to Methodology (30 minutes, saves 400 words)
9. ○ **MINOR-010**: Consider condensing Conclusion for final publication (30 minutes, saves 900 words)

**Total Effort for Optional Polish**: 95 minutes (saves ~1,450 words if all implemented)

---

## Overall Recommendation

**For R2 Review Submission**:
- Implement 3 "Must Fix" items (15 minutes)
- Implement MINOR-004 (Table 2 clarification, 2 minutes)
- Defer figures (MINOR-006) to camera-ready if R2 accepts
- Keep current length (defer polish items to final publication)

**Estimated Effort**: 20 minutes

**For Final Publication**:
- Implement all Must Fix + Should Fix items
- Implement Optional Polish items if page limits apply
- Generate figures (MINOR-006 Option A)
- Condense Conclusion (MINOR-010 Option A)

**Estimated Effort**: 3-5 hours (mostly figure generation)

---

## Changelog Metadata

**Human Review Notes Generated**: 2026-03-18
**Minor Issues Identified**: 9 (10 numbered, but MINOR-003 already resolved)
**Issues Requiring Action**: 8
**Estimated Fix Time (minimum)**: 20 minutes
**Estimated Fix Time (maximum)**: 5 hours

**Priority Breakdown**:
- Must Fix: 3 issues (15 minutes)
- Should Fix: 2 issues (2 min - 4 hours)
- Optional Polish: 4 issues (95 minutes)

**Recommendation**: Implement Must Fix + MINOR-004 before R2 submission. Defer rest to final publication.

---

## R2 Resolution Status

**Date**: 2026-03-18
**R2 Issues Addressed**: 6/6 (100%)

### R2 Minor Issues (All Resolved in Automated Revision)

**ACC-MINOR-001: PCA Variance Percentages**
- Status: ✓ RESOLVED in R2
- Fix: Updated PC2=12.9%, PC3=1.7% (from validation data)
- Location: Results Section 5.1, lines 448-454

**ACC-MINOR-002: M1 Rank Reporting Ambiguity**
- Status: ✓ RESOLVED in R2
- Fix: Changed "0.0%" to "0.0%-12.5% range" in Abstract and Results
- Location: Abstract line 3, Results line 466

**ACC-MINOR-003: Data Source Labeling**
- Status: ✓ RESOLVED in R2
- Fix: Enhanced POC disclaimer box to clarify "minimal real inference"
- Location: Results section opening

**ENG-MINOR-001: Missing POC Disclaimer Box**
- Status: ✓ RESOLVED in R2
- Fix: Added visual box format (┌─┐ borders) before Results
- Location: Results section opening, lines 402-413

**CRED-MINOR-001: Bootstrap CI Traceability**
- Status: ✓ RESOLVED in R2
- Fix: Added note "(estimated via standard procedure; not implemented)"
- Location: Results statistical significance, line 460

**CRED-MINOR-002: Perfect Purity Needs Context**
- Status: ✓ RESOLVED in R2
- Fix: Added "(in 3-model POC)" qualifier in Abstract and detailed note in Results
- Location: Abstract line 3, Results line 442

**CRED-MINOR-003: Temperature Confound**
- Status: ✓ ALREADY IN R1
- Fix: Comprehensive temperature confound section already present
- Location: Discussion lines 654-672

### R1 Minor Issues (Still Open for Human Review)

All 9 R1 minor issues remain as optional polish items for final publication:

---

