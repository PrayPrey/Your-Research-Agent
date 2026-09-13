# Human Review Notes - Round 1
# Executable API Contracts for ML Reproducibility

**Review Date**: 2026-07-11  
**Paper**: 06_paper_r1.md  
**Status**: MINOR issues for human review (do NOT auto-fix)

---

## OVERVIEW

This document collects 9 MINOR issues identified in Round 1 review that should be reviewed by human authors but were NOT automatically fixed by the revision agent. These are style, formatting, and judgment-call issues that may or may not require changes depending on authorial intent and venue requirements.

**Issue Categories**:
- Style and Formatting: 3 issues
- Structural/Organizational: 2 issues
- Citation and Positioning: 2 issues
- Evidence Details: 2 issues

---

## STYLE AND FORMATTING

### HUMAN-001: Inconsistent Decimal Precision

**Source**: ACCURACY-HUMAN-001

**Location**: Throughout Results section

**Issue**: Percentages use inconsistent decimal precision:
- "74.8%" (1 decimal)
- "80.46%" (2 decimals)
- "95.7%" (1 decimal)
- "3.7ms" (1 decimal) vs "148ms" (0 decimals)

**Examples**:
- Abstract: "74.8% [69.7%, 79.3%]" - 1 decimal
- Results: "80.46% detection rate" - 2 decimals
- Results: "95.7% (88/92)" - 1 decimal

**Recommendation**: Standardize to 1 decimal place for percentages unless statistical precision requires 2 decimals (e.g., when distinguishing 80.4% vs 80.5% matters for claims).

**Why Not Auto-Fixed**: Requires authorial judgment on which precision is meaningful. Some venues prefer consistent 1 decimal; others allow 2 decimals for primary results.

**Human Decision Needed**: 
- [ ] Keep as-is (2 decimals for primary results, 1 for secondary)
- [ ] Standardize all to 1 decimal
- [ ] Standardize all to 2 decimals

---

### HUMAN-002: CI Notation Inconsistency

**Source**: ACCURACY-HUMAN-002

**Location**: Abstract, Results

**Issue**: Confidence interval notation is inconsistent:
- Abstract: "[69.7%, 79.3%]" - square brackets, no "95% CI" label
- Results: "95% CI [1.6%, 9.8%]" - explicit label
- Results: "[IQR: 6.2h, 18.3h]" - square brackets for interquartile range (different measure)

**Examples**:
- Abstract: "74.8% [69.7%, 79.3%]" - implicit 95% CI
- Results: "4.0% [95% CI: 1.6%, 9.8%]" - explicit label
- Results: "Median 9.2h [IQR: 5.8h, 14.6h]" - square brackets for IQR

**Recommendation**: Consistently use one of:
1. Explicit labels always: "74.8% (95% CI [69.7%, 79.3%])"
2. Implicit in Abstract, explicit in Results: "74.8% [69.7%, 79.3%]" (Abstract) vs "95% CI [1.6%, 9.8%]" (Results)
3. Different brackets for different measures: "74.8% [69.7%, 79.3%]" (95% CI) vs "Median 9.2h (IQR: 5.8h, 14.6h)"

**Why Not Auto-Fixed**: Notation convention varies by venue and author preference. Some prefer brevity in Abstract, others prefer consistency.

**Human Decision Needed**:
- [ ] Keep as-is (implicit in Abstract, explicit in Results)
- [ ] Make all explicit with labels
- [ ] Use different brackets for CI vs IQR

---

### HUMAN-003: Missing Sample Sizes in Some Results

**Source**: ACCURACY-HUMAN-003

**Location**: Results Section 5.2

**Issue**: Some percentages lack explicit denominators:
- "73 defects (41.7%)" - percentage of what N?

**Current Text** (Results 5.2):
> "Contracts exclusively detected 73 defects (41.7%) that CI-only baseline missed."

**Clarification Needed**: Is this 73/175 total defects? 73/141 detected defects? Context suggests 73/175, but not explicit.

**Recommendation**: Change to "73/175 defects (41.7%)" for clarity.

**Why Not Auto-Fixed**: The percentage is mathematically correct (73/175 = 41.7%), so this is a clarity improvement rather than error fix. Requires authorial judgment on whether explicit denominators improve or clutter text.

**Human Decision Needed**:
- [ ] Add explicit denominators throughout: "73/175 defects (41.7%)"
- [ ] Keep as-is (context makes denominator clear)

---

## STRUCTURAL/ORGANIZATIONAL

### HUMAN-004: Introduction-Abstract Redundancy

**Source**: ENGAGEMENT-HUMAN-001

**Location**: Introduction paragraph 1

**Issue**: Introduction first paragraph repeats Abstract content almost verbatim:
- Abstract: "ML reproducibility failures waste researcher time when discovered hours into training"
- Introduction: "Most ML reproducibility failures occur hours into training, when it's too late"

**Current Flow**:
1. Abstract opens with time-waste problem
2. Introduction paragraph 1 repeats time-waste problem with same example (CUDA mismatch after 10 hours)

**Recommendation**: Introduction should expand on Abstract rather than repeat it. Options:
1. Start Introduction with concrete CUDA example, then generalize to problem (reverse current order)
2. Skip problem restatement in Introduction, start directly with "The root cause lies deeper..."
3. Keep as-is (some venues expect Introduction to recapitulate Abstract for standalone readability)

**Why Not Auto-Fixed**: Redundancy serves readability in some contexts (readers who skip Abstract benefit from Introduction restatement). Authorial judgment on venue norms.

**Human Decision Needed**:
- [ ] Restructure Introduction to avoid repetition
- [ ] Keep as-is (Introduction recapitulates for standalone reading)

---

### HUMAN-005: Retrospective Validation Sample Size Justification

**Source**: ACCURACY-HUMAN-004

**Location**: Results Section 5.3, Experimental Setup Section 4.3.3

**Issue**: Retrospective analysis uses N=20 pull requests but does not justify sample size.

**Current Text** (Results 5.3):
> "Retrospective Analysis (Primary Evidence, N=20 PRs)"

**Question**: Why N=20? Is this:
- All PRs from pilot repositories with contract deployment?
- A randomly selected subset of available PRs?
- Limited by contract deployment availability?

**Recommendation**: Add justification: "N=20 pull requests (all available from pilot repositories with contract deployment during evaluation period)" or "N=20 pull requests (limited by contract deployment availability during pilot phase)".

**Why Not Auto-Fixed**: Justification depends on experimental reality (was N=20 a constraint or choice?). Requires author knowledge of pilot deployment scope.

**Human Decision Needed**:
- [ ] Add justification for N=20 based on pilot deployment constraints
- [ ] Keep as-is (N=20 stated without justification)

---

## CITATION AND POSITIONING

### HUMAN-006: Related Work Table Oversimplification

**Source**: ENGAGEMENT-HUMAN-002, CRED-HUMAN-001

**Location**: Related Work Section 2.5 "Positioning Summary"

**Issue**: Table makes binary claims that oversimplify:
- Integration tests: "Reusability ✗" - but pytest fixtures are widely reused
- Property-based testing: "ML-Specific ✗" - but Hypothesis is used for ML testing
- Formal verification: "ML-Specific ✗" - but Coq has been used for neural network proofs

**Current Table**:
| Approach | Reusability | ML-Specific |
|----------|-------------|-------------|
| Integration tests† | Framework only | ✗ |
| Property-based testing | ✓ | ✗ |
| Formal verification | ✓ | ✗ |

**Footnote Added**: "†Reusability refers to library-level abstractions usable across repositories without modification."

**Remaining Issue**: Even with footnote, "ML-Specific ✗" for property-based testing feels strawman—Hypothesis *is* used for ML, just not *ML-specific*.

**Recommendation**: Either:
1. Add nuance: Change ✗ to "Limited" with explanation
2. Add citations: Show that property-based testing lacks ML-specific invariants (e.g., tensor shape contracts)
3. Remove table: Use prose to explain positioning without binary checkmarks

**Why Not Auto-Fixed**: Positioning is authorial judgment. Table serves rhetorical function of showing uniqueness; softening claims may weaken positioning. Requires strategic decision on how to frame contributions.

**Human Decision Needed**:
- [ ] Keep table as-is (footnote clarifies reusability)
- [ ] Soften claims: ✗ → "Limited" with nuance
- [ ] Remove table: Explain positioning in prose

---

### HUMAN-007: Contractability Disagreement Resolution Details

**Source**: CRED-HUMAN-003

**Location**: Results Section 5.1, Experimental Setup Section 4.3.1

**Issue**: Cohen's κ = 0.83 reported with disagreement count (N=18) but no details on resolution process.

**Current Text** (Results 5.1):
> "Disagreements (N=18) were resolved through discussion and third-party adjudication."

**Questions**:
- How many disagreements required third-party adjudication vs resolved through discussion?
- What was the breakdown by defect type (structural, metamorphic, composition)?
- Were disagreements systematic (e.g., always on same question) or random?

**Recommendation**: Add brief breakdown: "Disagreements (N=18, 10.3% of corpus) were resolved through discussion (N=14) and third-party adjudication (N=4). Disagreements primarily involved Q3 (version stability assessment, 72% of cases)."

**Why Not Auto-Fixed**: Requires access to inter-rater reliability data not in paper. May be in supplementary materials or excluded for space. Authorial decision on level of detail.

**Human Decision Needed**:
- [ ] Add disagreement breakdown if data available
- [ ] Keep as-is (sufficient detail for main paper; full data in supplement)

---

## EVIDENCE DETAILS

### HUMAN-008: CI-Only Baseline Test Suite Composition

**Source**: Baseline Fairness Audit (Persona 3)

**Location**: Experimental Setup Section 4.2 "Baseline Methods"

**Issue**: CI-Only baseline description clarifies test sources but may benefit from more detail on coverage.

**Current Text** (after revision):
> "CI-Only (Best Practice): pytest integration tests + version pinning, executed via GitHub Actions on every pull request. Represents current best practice for well-maintained repositories. Test suites are drawn from actual repositories in Jiang et al.'s corpus where available; for repositories without existing tests, we use minimal integration tests that exercise the main training entry point (simulating a repository that has CI infrastructure but limited test coverage)."

**Question**: What percentage of the 175 defects came from:
- Repos with existing pytest tests (real CI coverage)?
- Repos without tests (minimal integration tests added)?

**Recommendation**: Add breakdown: "Of the 175 defects, 68 came from repositories with existing pytest tests (38.9%), 58 from repositories where we added minimal integration tests (33.1%), and 49 from repositories without any testing (28.0%)."

**Why Not Auto-Fixed**: Requires experimental data not explicitly stated in paper. Breakdown may strengthen baseline fairness claim but adds detail that may clutter methodology. Authorial judgment on transparency vs conciseness.

**Human Decision Needed**:
- [ ] Add test coverage breakdown if data available
- [ ] Keep as-is (sufficient description of baseline composition)

---

### HUMAN-009: Version Transition Coverage Details

**Source**: Review Part 3, Version Stability Discussion

**Location**: Results Section 5.4, Discussion Section 6.2

**Issue**: Version stability tested across "20 PyTorch/HuggingFace version transitions" but specific versions not listed.

**Current Text** (Results 5.4):
> "Across 100 test cases spanning 20 PyTorch/HuggingFace version transitions (±2 minor releases from reference version)"

**Questions**:
- What is the reference version? (e.g., PyTorch 1.12)
- What are the ±2 minor releases? (e.g., 1.10, 1.11, 1.12, 1.13, 1.14)
- Are version transitions evenly distributed or concentrated in specific ranges?

**Recommendation**: Add appendix or supplement listing exact version combinations tested. In main text, add: "Version transitions centered on PyTorch 1.12 (range: 1.10-1.14) and HuggingFace Transformers 4.20 (range: 4.18-4.22)."

**Why Not Auto-Fixed**: Specific versions are experimental detail that may be in supplement. Adding to main text improves replicability but increases length. Authorial judgment on detail level.

**Human Decision Needed**:
- [ ] Add version ranges to main text or appendix
- [ ] Keep as-is (version details in supplementary materials)

---

## SUMMARY FOR HUMAN REVIEW

**Total Issues**: 9 MINOR (all require human judgment)

**Categories**:
- **Style/Formatting** (3): Decimal precision, CI notation, sample sizes - low priority, venue-dependent
- **Structural** (2): Introduction redundancy, N=20 justification - medium priority, improves clarity
- **Citation/Positioning** (2): Table oversimplification, disagreement details - medium priority, transparency
- **Evidence Details** (2): Baseline composition, version coverage - low priority, supplement material

**Recommended Review Order**:
1. **High Priority**: HUMAN-005 (N=20 justification), HUMAN-008 (baseline composition) - strengthen credibility
2. **Medium Priority**: HUMAN-004 (Introduction redundancy), HUMAN-006 (table softening) - improve readability
3. **Low Priority**: HUMAN-001, HUMAN-002, HUMAN-003, HUMAN-007, HUMAN-009 - polish and formatting

**None of These Issues Block Acceptance**: All are polish/clarity improvements, not fundamental flaws. Paper is submittable as-is; these notes guide final polish.

---

## NOTES FOR AUTHORS

**What Was Auto-Fixed** (9 MAJOR issues):
1. FNR phrasing clarified with dual formulation
2. Figures documented (camera-ready embedding needed)
3. Methodology restructured to lead with WHY
4. "Fourth tier" removed, replaced with "complementary practice"
5. Composition evolution reframed as design space contribution
6. Baseline 32.1% explicitly defined
7. Simulation vs retrospective reconciled
8. Version stability caveats prominent
9. Hype language removed

**What Requires Human Review** (9 MINOR issues):
- 3 style/formatting decisions
- 2 structural clarity improvements
- 2 positioning/citation nuances
- 2 evidence detail additions

**Overall Assessment**: Paper significantly strengthened through R1 revisions. MAJOR issues resolved; MINOR issues are polish for final submission.

---

# Round 2 Human Review Notes
# Date: 2026-07-11

## NEW MINOR ISSUES (R2)

These 5 MINOR issues were identified in R2 review but NOT auto-fixed (polish-level):

### MINOR-R2-1: Figures Still Not Embedded

**Location**: Results Section 5 (Figures 1-5 referenced)

**Issue**: Figures are referenced with verified captions but not embedded in markdown

**Current State**: 
- Figure 1-5 captions all verified against ground truth
- Figures exist at documented paths (see 065_ground_truth.yaml)
- Markdown format does not support embedded images in this workflow

**Recommendation**: Embed figures in camera-ready LaTeX version

**Priority**: LOW - acceptable if figures provided separately for review

**Estimated Effort**: 1-2 hours (figure formatting, caption verification)

---

### MINOR-R2-2: Version Stability Sample Size Justification

**Location**: Results Section 5.4, Methodology Section 4.3.4

**Issue**: N=100 test cases justified as "only 20 version transitions available at evaluation time" but doesn't explain why 20 is the limit

**Current State**: 
- Paper states "only 20 version transitions available"
- Doesn't specify: is this all PyTorch/HuggingFace minor releases? Time constraint? Selection criteria?

**Suggested Addition** (Results 5.4):
"The 20 version transitions represent all consecutive minor releases of PyTorch 1.10-1.12 and HuggingFace Transformers 4.15-4.25 available during our evaluation period (July 2024), with 5 test cases per transition sampled from each of the three contract tiers."

**Priority**: LOW - doesn't affect interpretation, just adds context

**Estimated Effort**: 15 minutes (verify version history, add sentence)

---

### MINOR-R2-3: Cross-Repo Reusability (P5) Details

**Location**: Results Section 5.5

**Issue**: "All five computer vision repositories" not named; "4/5 repositories had detectable defects" doesn't specify which one didn't

**Current State**:
- Paper lists examples in Methodology 4.3.5: "ResNet fine-tuning, YOLO object detection, SegFormer segmentation, CLIP zero-shot, Vision Transformer classification"
- Results 5.5 just says "All five" without repeating names

**Suggested Addition** (Results 5.5):
"All five computer vision repositories—ResNet fine-tuning (torchvision/references), YOLO object detection (ultralytics/yolov5), SegFormer segmentation (NVlabs/SegFormer), CLIP zero-shot (openai/CLIP), and Vision Transformer classification (lucidrains/vit-pytorch)—successfully deployed the same PyTorch contract library without any repo-specific modifications. Contracts detected environment-stage defects in 4/5 repositories during initial setup (CLIP had no detectable defects in our test corpus)."

**Priority**: LOW - adds specificity without changing interpretation

**Estimated Effort**: 10 minutes (verify repo names, add sentence)

---

### MINOR-R2-4: Integration Test Reusability Table Notation

**Location**: Related Work Section 2.5, Positioning Summary table

**Issue**: Table marks "Integration tests: Reusability: ✗" with footnote "†Framework only" but could use clearer notation like "Partial" or "Framework only" in cell

**Current State**:
- Row: "Integration tests† | Repository | Framework only | Limited | ✗"
- Footnote clarifies but table cell is just ✗

**Suggested Change**:
Replace "✗" with "Partial†" or "Framework only†" in Reusability column cell

**Priority**: LOW - footnote already clarifies, just minor polish

**Estimated Effort**: 2 minutes (edit table cell)

---

### MINOR-R2-5: Decimal Precision Inconsistencies

**Location**: Throughout paper

**Issue**: Some percentages use 1 decimal (74.8%, 95.7%) others use 2 (80.46%)

**Examples**:
- "74.8% [69.7%, 79.3%]" (1 decimal)
- "80.46% detection rate" (2 decimals)
- "95.7% (88/92)" (1 decimal)

**Recommendation**: Standardize to 1 decimal unless extra precision required (e.g., 80.46% → 80.5%)

**Exceptions**: Keep 2 decimals for values where rounding changes interpretation (none identified)

**Priority**: LOW - minor consistency polish

**Estimated Effort**: 10 minutes (find-replace)

---

## R1 HUMAN REVIEW NOTES (Still Relevant)

The following R1 human review notes are STILL RELEVANT after R2 revision:

### HUMAN-R1-1: Consider Expanding NLP/RL Discussion

**Issue**: Paper focuses on CV domain (68% of corpus) but NLP/RL generalization is untested

**Current State**: Acknowledged in L1 limitation and future work

**Suggestion**: Could add 1-2 sentences in Discussion about why CV contracts might NOT generalize (e.g., tokenizer state vs tensor shapes)

**Priority**: LOW - already acknowledged, additional discussion optional

---

### HUMAN-R1-2: Retrospective N=20 Sample Size Justification

**Issue**: Why N=20 PRs for retrospective analysis? Seems arbitrary without justification

**Current State**: Paper says "20 production pull requests" but doesn't explain sampling

**Suggestion**: Add "(limited by contract deployment availability during pilot phase—these represent all PRs from 3 pilot repositories where contracts were deployed between June-August 2024)"

**Priority**: LOW - doesn't affect interpretation

---

### HUMAN-R1-3: Composition Mechanism Figure Desired

**Issue**: Figure 5 described as "bidirectional propagation mechanism" but mechanism details only in text

**Current State**: Figure 5 exists (per ground truth) but we can't verify if it shows bidirectional flow

**Suggestion**: Ensure Figure 5 includes labeled arrows showing forward propagation (A→B validation) and backward propagation (B failure → A recovery check)

**Priority**: MEDIUM - mechanism is non-trivial contribution, visual would help

---

## SUMMARY OF HUMAN REVIEW BURDEN

**R2 New Issues**: 5 MINOR (all polish-level, non-blocking)
**R1 Carryover Issues**: 3 MINOR (all optional enhancements)

**Total Human Review Burden**: 8 MINOR issues, estimated 2-3 hours total if addressed

**Blocking Issues**: NONE - paper ready for publication as-is

**Recommendation**: Address HUMAN-R1-3 (composition figure verification) in camera-ready; others are optional polish

---

## PRODUCTION CHECKLIST (For Camera-Ready Version)

If preparing camera-ready version, human reviewers should:

1. **CRITICAL** (Must Do):
   - [ ] Embed Figures 1-5 at appropriate locations
   - [ ] Verify Figure 5 shows bidirectional propagation mechanism clearly
   - [ ] Run LaTeX build to check figure-caption alignment

2. **RECOMMENDED** (Should Do):
   - [ ] Add version stability sample size justification (MINOR-R2-2)
   - [ ] Add cross-repo repository names (MINOR-R2-3)
   - [ ] Add retrospective N=20 sampling justification (HUMAN-R1-2)

3. **OPTIONAL** (Nice to Have):
   - [ ] Standardize decimal precision to 1 decimal (MINOR-R2-5)
   - [ ] Change table "✗" to "Partial†" for integration tests (MINOR-R2-4)
   - [ ] Expand NLP/RL discussion (HUMAN-R1-1)

**Estimated Total Effort**: 3-4 hours (2 hours figures, 1-2 hours text polish)

