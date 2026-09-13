# Human Review Notes - Round 1

> **Purpose:** Minor issues for human review (NOT auto-fixed by Revision Agent)
> **Generated:** 2026-05-12
> **Source:** Adversarial Review Round 1 (065_review_r1.md)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Style | 4 |
| Clarity | 3 |
| Formatting | 2 |
| Missing Info | 1 |
| **Total** | **10** |

---

## Issues Collected

### Style Issues

**STYLE-01: Abstract Opening Phrasing**
- **Location:** Abstract, line 1 (revised paper)
- **Current:** "Machine learning reproducibility suffers from silent dataset versioning failures"
- **Issue:** Somewhat awkward phrasing—"suffers from" + "failures" is redundant
- **Suggestion:** Consider "Machine learning reproducibility faces silent dataset versioning failures" or "Silent dataset versioning failures undermine machine learning reproducibility"
- **Priority:** LOW
- **Impact:** Minor stylistic improvement, does not affect clarity

---

**STYLE-02: Inconsistent Voice (we vs passive)**
- **Location:** Section 3.1 ("Layer 2: Classification"), line ~88 in original
- **Current:** "We compare the drift score against fixed thresholds"
- **Issue:** Paper alternates between "we" (active) and passive voice inconsistently
- **Examples:**
  - Active: "We compare the drift score" (Section 3.1)
  - Passive: "Fixed thresholds are derived" (Section 3.4)
  - Active: "We freeze weights" (Section 3.2)
- **Suggestion:** Pick one style (active "we" recommended for methods sections) and apply consistently throughout Section 3
- **Priority:** LOW
- **Impact:** Style consistency, easier reading flow

---

**STYLE-03: Excessive Bold Formatting**
- **Location:** Section 5.2, multiple instances in revised paper
- **Current:** "**dual breakdown in detection and precision**", "**systematic mis-calibration**"
- **Issue:** Overuse of bold formatting may distract rather than emphasize
- **Suggestion:** Limit bold to 1-2 key terms per section, use italics for secondary emphasis
- **Priority:** LOW
- **Impact:** Visual clarity, less "shouting" on page

---

**STYLE-04: Conclusion Callback Could Be Stronger**
- **Location:** Section 7, "Callback to introduction hook" paragraph
- **Current:** Callback mentions ImageNet example but doesn't fully mirror opening paragraph's structure
- **Issue:** The introduction opens with specific ImageNet-v2 story; conclusion could mirror this more directly
- **Suggestion:** Consider opening conclusion's callback with "We asked whether statistical drift detection could automate semantic versioning, inspired by ImageNet-v2's 11-14% accuracy drop..."
- **Priority:** LOW
- **Impact:** Narrative cohesion, satisfying structure for readers

---

### Clarity Issues

**CLARITY-01: HuggingFace Revision ID Could Use Real Example**
- **Location:** Section 1 (Introduction), paragraph 2, line ~10 in original
- **Current:** "A researcher encountering version `rev=a3f7b2d`"
- **Issue:** Generic placeholder revision ID—readers unfamiliar with HuggingFace may not recognize this as example
- **Suggestion:** Use actual HuggingFace revision ID from real dataset (e.g., `load_dataset("glue", "mrpc", revision="bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c")`) or add context like "encountering an opaque version identifier such as `rev=a3f7b2d`"
- **Priority:** MEDIUM
- **Impact:** Improves concreteness, helps readers understand real-world scenario

---

**CLARITY-02: Dataset Coverage Numbers Need Clarification**
- **Location:** Section 4.1
- **Current:** Paper says "9 successfully loaded via API" but "14 were classified by the system"
- **Issue:** The 5 additional datasets are mentioned but not clearly explained
- **What's unclear:** Were these 5 loaded via alternative methods? Simulated? Pre-processed offline?
- **Suggestion:** Add 1-2 sentences explaining what "5 additional datasets processed" means (e.g., "5 datasets were preprocessed offline and loaded from cached features" or "5 datasets required manual download and local processing")
- **Priority:** HIGH (affects reproducibility)
- **Impact:** Critical for readers attempting to reproduce experiments

---

**CLARITY-03: SST2 Contradiction Needs Stronger Resolution**
- **Location:** Section 6.2, line ~391 in original
- **Current:** "For SST2, a baseline drift of 0.79 may be normal"
- **Issue:** This statement contradicts the PATCH label assignment—if 0.79 drift is "normal," why is it labeled PATCH?
- **Suggestion:** Rewrite to: "For SST2, if validation set curation differed substantially from training set, a 0.79 drift might reflect curation artifacts rather than performance-relevant distribution shift, which would validate the PATCH label. However, without performance measurement, this remains unresolved."
- **Priority:** MEDIUM
- **Impact:** Logical consistency, prevents reviewer confusion

---

### Formatting Issues

**FORMAT-01: Implementation Details Placement**
- **Location:** Section 3.3, line ~143 in original
- **Current:** "Implemented using `scipy.stats.ks_2samp`"
- **Issue:** Very low-level implementation detail in main methodology section
- **Suggestion:** Move to supplementary materials or footnote, keep main text focused on conceptual approach
- **Priority:** LOW
- **Impact:** Improves main text flow, reduces technical clutter

---

**FORMAT-02: Figure/Table Numbering Consistency**
- **Location:** Throughout paper
- **Current:** Text references "Figure 2" (confusion matrix), "Figure 3" (drift scores), "Figure 4" (per-dataset), but figures are not shown in markdown
- **Issue:** Cannot verify numbering is consistent since figures not embedded
- **Suggestion:** When generating final PDF, verify all "Figure X" and "Table X" references match actual figure positions
- **Priority:** MEDIUM (critical for final submission)
- **Impact:** Professional presentation, prevents reviewer confusion

---

### Missing Information

**MISSING-01: Repository URL Placeholder**
- **Location:** Section 7 (Conclusion), "Data and code availability" paragraph, line ~574 in original
- **Current:** "[REPOSITORY_URL]"
- **Issue:** Placeholder not filled in
- **Action Required:** Replace with actual repository URL before submission (e.g., GitHub, Zenodo, institution repository)
- **Priority:** HIGH (required for submission)
- **Impact:** Essential for reproducibility, ICML requires code/data availability statements

---

## Detailed Context for Each Issue

### STYLE-02 Elaboration: Voice Consistency Examples

**Section 3 voice usage audit:**
- 3.1: "We extract feature representations" (active) ✓
- 3.2: "We freeze weights" (active) ✓
- 3.3: "Implemented using scipy.stats" (passive) ✗
- 3.4: "Fixed thresholds are derived" (passive) ✗
- 3.5: "We selected 15 datasets" (active) ✓

**Recommendation:** Change passive instances to active:
- "Implemented using" → "We implement the KS test using"
- "Fixed thresholds are derived" → "We derive fixed thresholds"

**Rationale:** Active voice in methods sections is standard practice, makes it clear who did what.

---

### CLARITY-02 Elaboration: 14-Dataset Breakdown

**What we know:**
- 9 datasets loaded via standard HuggingFace/torchvision APIs (explicitly listed)
- 5 additional datasets processed somehow (not explained)
- 1 dataset unavailable (ImageNet-v2 or similar requiring manual download)
- Total: 9 + 5 = 14 evaluated, 1 missing = 15 planned

**What needs clarification:**
1. Were the 5 additional datasets:
   - Loaded via alternative APIs (Kaggle, manual download)?
   - Generated synthetically for testing purposes?
   - Cached from previous runs?
2. What are their names/characteristics?
3. Why weren't they loaded via standard APIs?

**Suggested addition to Section 4.1:**
> "The 5 additional datasets were [EXPLAIN: manually downloaded and preprocessed / loaded from institution dataset repository / cached from preliminary experiments]. These datasets included [LIST or CHARACTERIZE: 2 additional GLUE variants, 3 proprietary benchmark splits / diverse NLP tasks / etc.], contributing to the overall sample diversity but limiting reproducibility for external researchers."

---

### CLARITY-03 Elaboration: SST2 Resolution Options

**Current ambiguity:** Paper simultaneously states:
1. SST2 is labeled PATCH (expected low impact)
2. SST2 has 0.79 drift (highest in corpus, 10× MAJOR threshold)
3. "0.79 may be normal for SST2" (Section 6.2)

**Problem:** If 0.79 is normal, PATCH label makes sense. But then drift detection is false positive. If 0.79 is abnormal, PATCH label is wrong. Can't have both.

**Three resolution paths:**

**Option A (Ground Truth Error):**
> "SST2's 0.79 drift score—highest in our corpus—suggests the PATCH label may be incorrect. Without performance-based validation (training a model on SST2-train and measuring accuracy on SST2-validation), we cannot determine whether this represents a false positive (drift detector oversensitive) or a labeling error (should be MAJOR/MINOR). This ambiguity highlights the critical need for performance-based ground truth."

**Option B (Detector False Positive):**
> "SST2's 0.79 drift score likely reflects validation set curation artifacts (e.g., balanced class distribution) rather than performance-relevant distribution shift. If true, this represents a drift detector false positive—statistical drift without semantic impact. Performance measurement is needed to confirm."

**Option C (Uncertainty Acknowledged):**
> "SST2 presents an unresolved case: high drift (0.79) with PATCH label creates three possible interpretations: (1) ground truth error, (2) detector false positive, or (3) dataset-specific baseline misalignment. Only performance-based validation can resolve this ambiguity."

**Recommendation:** Use Option C (acknowledges uncertainty without overstating confidence).

---

## Typography and Grammar Audit

**Note:** Original review listed 10 MINOR issues, with some being typos/grammar. During detailed review of revised paper, no specific typos were found that weren't already addressed. The 10 issues above cover style, clarity, and formatting. If additional typos emerge during human review, add them here.

**Potential typo candidates (to verify during human review):**
1. Section 2.1: Check for "recieve" vs "receive" (not found in revised paper)
2. Section 3.2: Check for "We uses" vs "We use" (not found in revised paper)
3. All instances of "dataset-specific" vs "dataset specific" (hyphenation consistency)
4. All instances of "two-phase" vs "two phase" (hyphenation consistency)

---

## Priority Ranking for Human Review

### Must Fix Before Submission (HIGH Priority)
1. **MISSING-01:** Repository URL placeholder (line 574)
2. **CLARITY-02:** Explain 5 additional datasets (affects reproducibility)
3. **FORMAT-02:** Verify all figure/table numbering when generating PDF

### Should Fix for Quality (MEDIUM Priority)
4. **CLARITY-01:** Use real HuggingFace revision ID example
5. **CLARITY-03:** Resolve SST2 drift/label contradiction more explicitly

### Nice to Have (LOW Priority)
6. **STYLE-01:** Rephrase abstract opening
7. **STYLE-02:** Consistent voice in methods section
8. **STYLE-03:** Reduce bold formatting
9. **STYLE-04:** Strengthen conclusion callback
10. **FORMAT-01:** Move implementation details to supplement

---

## Suggested Review Process

**Step 1: Critical Fixes (30 minutes)**
- Replace [REPOSITORY_URL] placeholder
- Add 2-3 sentences explaining 5 additional datasets in Section 4.1
- Verify figure numbering when generating PDF

**Step 2: Clarity Improvements (20 minutes)**
- Replace `rev=a3f7b2d` with real example
- Rewrite SST2 paragraph in Section 6.2 using Option C resolution

**Step 3: Style Polish (20 minutes)**
- Audit Section 3 for voice consistency, convert passive→active
- Review bold formatting, reduce to 1-2 key terms per section
- Consider abstract opening rephrase

**Step 4: Final Proofread (15 minutes)**
- Check all cross-references (Section X, Table Y, Figure Z)
- Verify all metrics consistent (28.57%, 25%, 25%, 25%)
- Ensure no orphaned references to "9 datasets" or "44.4%" remain

**Total estimated time:** 85 minutes for human review

---

## Not Fixed (By Design)

The following items were intentionally **NOT** fixed to preserve author voice and scientific tone:

1. **Conversational elements preserved:**
   - "Spoiler:" framing in introduction
   - Colloquial phrases like "barely above random chance"
   - Rhetorical questions in introduction

2. **Negative result honesty:**
   - Direct statements like "fails catastrophically" (softened to "fails significantly" but still strong)
   - Transparent limitation discussion

3. **Technical depth:**
   - Mathematical equations in Section 3.3 (KS, MMD formulas)
   - Implementation details (though FORMAT-01 suggests moving some to supplement)

**Rationale:** These elements make the paper engaging and authentic. Over-polishing would make it sterile and less readable.

---

## Cross-Reference Verification Checklist

For human reviewer to verify:

- [ ] All instances of "9 datasets" changed to "14 datasets"
- [ ] All instances of "44.4%" changed to "28.57%"
- [ ] All instances of "16.7%" changed to "25%"
- [ ] All instances of "100% recall" changed to "25% recall"
- [ ] All instances of "28.6% F1" changed to "25% F1"
- [ ] All instances of "-53.3pp" changed to "-45pp" (precision gap)
- [ ] All instances of "-40.6pp" changed to "-56.43pp" (accuracy gap)
- [ ] No instances of "100% false positive rate" remain (outdated claim)
- [ ] No instances of "perfect recall" remain (incorrect)
- [ ] All figure references (Figure 1-4) are correct
- [ ] All table references (Table 1-2) are correct
- [ ] All section cross-references (Section X.Y) are correct
- [ ] Repository URL filled in (currently [REPOSITORY_URL])

---

## Additional Notes for Human Reviewer

### Why These Weren't Auto-Fixed

**Revision Agent protocol:** Minor issues (style, typos, formatting) are collected for human review rather than auto-fixed to:
1. Preserve author's voice and writing style
2. Avoid introducing new errors through automated text manipulation
3. Respect subjective style preferences (some reviewers prefer passive voice, others active)
4. Prevent over-polishing that makes academic writing sterile

### When to Ignore These Suggestions

**Ignore if:**
- Author strongly prefers current phrasing for stylistic reasons
- Journal/venue style guide contradicts suggestions (e.g., requires passive voice)
- Time constraints prevent full polish (prioritize HIGH items only)
- Co-authors disagree on style changes

**Do NOT ignore:**
- MISSING-01 (repository URL) - required for submission
- CLARITY-02 (dataset explanation) - affects reproducibility
- FORMAT-02 (figure numbering) - affects professionalism

---

## Feedback Loop

If human reviewer finds additional issues during review:

**Add to this file:**
1. New typos discovered
2. Inconsistencies not caught by automated revision
3. Additional clarity improvements needed
4. New formatting issues

**Format for additions:**
```markdown
**CATEGORY-##: Brief Title**
- **Location:** Section X, paragraph Y
- **Current:** "..."
- **Issue:** ...
- **Suggestion:** ...
- **Priority:** HIGH/MEDIUM/LOW
```

---

**Human Review Notes Status:** READY FOR REVIEW
**Generated by:** Revision Agent Round 1
**Date:** 2026-05-12
