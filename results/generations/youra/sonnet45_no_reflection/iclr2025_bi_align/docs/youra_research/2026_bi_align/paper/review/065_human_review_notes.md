# Human Review Notes (Minor Issues)

**Generated:** Round 1 Adversarial Review  
**Date:** 2026-05-11  
**Status:** NOT AUTO-FIXED (requires human review and decision)

---

## Instructions for Human Reviewer

This document lists 12 MINOR issues identified by the Devil's Advocate review that were **NOT automatically fixed** per v2.0 protocol. Each issue includes:
- Location in paper
- Type (clarity/tone/formatting/verification)
- Specific suggestion
- Rationale

**Review each issue and decide:**
1. **Accept suggestion:** Make the change manually
2. **Reject suggestion:** Issue not worth addressing
3. **Modify suggestion:** Adjust the proposed fix

---

## Terminology Precision Issues (3 issues)

### MINOR-1: "Validated Infrastructure" Overstates Maturity

**Location:** Abstract, Introduction (line 21-22), Section 5.5 (line 383)

**Current text:** "Validated infrastructure", "Infrastructure validated, ready for empirical testing"

**Type:** clarity

**Issue:** "Validated" implies higher confidence than Ground Truth documents (MEDIUM confidence, no real API calls executed). Could mislead readers about maturity level.

**Suggestion:** Change to:
- "Infrastructure implementation complete and datasets verified, pending API execution"
- "Infrastructure code validated and datasets verified, pending API-based empirical testing"

**Rationale:** More accurately reflects actual state—code validated via mock data detection/correction, datasets verified via loading checks, but no API calls executed.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-2: "Sample Verified" Overstates Verification Scope

**Location:** Section 5.2, Table 2 (MMLU and HumanEval datasets)

**Current text:** "Sample Verified" with specific MMLU question quoted and HumanEval problem quoted

**Type:** clarity

**Issue:** "Sample verified" could mislead readers into thinking sample questions were evaluated through the full system (API calls executed). Verification appears to be dataset loading only.

**Suggestion:** Change to:
- "Sample dataset question loaded successfully" OR
- "Dataset loading verified with sample inspection"

**Rationale:** Clarifies verification scope is dataset integrity (correct loading) not system execution (API evaluation).

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-3: "Frozen Weights" Qualifier Needed

**Location:** Sections 3.1, 4.2, 6.1 (multiple occurrences)

**Current text:** "Claude 3 Opus with frozen pretrained weights"

**Type:** clarity

**Issue:** Paper states "frozen weights" as fact, but Ground Truth shows A1 (Capability Invariance) is UNVERIFIED. API-based models don't expose weight freezing control—this is inferred from Constitutional AI architecture.

**Suggestion:** Change to:
- "Claude 3 Opus (policy-layer modulation via system prompts, base capability assumed frozen per Constitutional AI architecture—testable via h-e1 ICC validation)"

**Rationale:** Makes explicit this is architectural assumption requiring h-e1 validation, not verified fact.

**Note:** This was partially addressed in MAJOR-3 fix. Review remaining occurrences for consistency.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

## Tone and Framing Issues (2 issues)

### MINOR-4: "Why Acceptable" Framing Sounds Defensive

**Location:** Discussion Section 6.2 (lines 422, 432, 442—Limitation 1, 2, 3 subsections)

**Current text:** Each limitation followed by "Why Acceptable" subsection

**Type:** tone

**Issue:** "Why Acceptable" framing minimizes limitations rather than transparently presenting them. Could be perceived as defensive advocacy.

**Suggestion:** Change subsection header to:
- "Rationale and Mitigation"

**Rationale:** Removes defensive tone while preserving justification content. Emphasizes mitigation strategies over acceptability argument.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-5: Automation Bias Generalization Confidence in Related Work

**Location:** Section 2.2 Automation Bias and Trust (lines 40-46)

**Current text:** Related Work presents automation bias generalization confidently, but Discussion 6.2 acknowledges A3 is unverified

**Type:** clarity

**Issue:** Inconsistency between Related Work tone (confident) and Discussion tone (uncertain about generalization).

**Suggestion:** Strengthen Related Work Section 2.2 to note uncertainty explicitly:
- "Whether automation bias mechanisms generalize from static traditional automation to dynamic AI collaboration remains an open empirical question (tested via our h-m3 mediation protocol)."

**Rationale:** Aligns Related Work tone with Discussion's honest acknowledgment of uncertainty.

**Note:** This was addressed in MAJOR fixes (Related Work Section 2.2 enhanced). Verify sufficient or needs further emphasis.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

## Structural and Formatting Issues (4 issues)

### MINOR-6: Abstract Length Exceeds Guideline

**Location:** Abstract (lines 1-3 in original, entire abstract in revised)

**Current length:** ~180 words (ICML guideline: ~150 words)

**Type:** formatting

**Issue:** Abstract slightly exceeds typical ICML length guideline. Could be trimmed for conciseness.

**Suggestion:** Reduce to ~150 words by condensing technical details:
- "statistical invariance checks (ICC > 0.95, ANOVA p > 0.05)" → "statistical invariance validation"
- Combine infrastructure and status sentences for brevity

**Rationale:** Meets venue formatting expectations while preserving key content.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-7: Venue Positioning Unclear

**Location:** N/A in paper text, submission metadata

**Type:** clarity

**Issue:** ICML main conference expects empirical contributions. This paper is methodological/infrastructure. Ground Truth suggests workshop/systems track more appropriate.

**Suggestion:** Add footnote or acknowledgment section positioning paper for:
- ICML Workshop Track
- ICML Systems Track
- OR submit to venue where methodological contributions are primary (e.g., CHI "Tools & Methods", FAccT)

**Rationale:** Sets appropriate reviewer expectations and increases acceptance likelihood.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-8: Section 4 Reads Like Proposal Filler

**Location:** Section 4 Experimental Design (lines 168-274)

**Current structure:** Detailed protocols for experiments that won't be executed (h-e1 through h-m4)

**Type:** clarity

**Issue:** To some readers, detailed protocols for non-executed experiments feel like proposal filler. Could be streamlined.

**Suggestion:** Two options:
1. **Condense Section 4** to high-level protocol summaries (move details to Appendix)
2. **Reposition as "Planned Protocols" appendix** with brief Section 4 summary in main text

**Rationale:** Acknowledges methodological contribution focus while reducing "proposal feel" for readers expecting empirical paper.

**Reviewer Decision:** [ ] Accept Option 1  [ ] Accept Option 2  [ ] Reject

---

### MINOR-9: Tables 3-4 Dense Without Narrative Scaffolding

**Location:** Section 5.3 Verification Protocol Design (Tables 3-4, lines 337-358)

**Current structure:** Dependency structure table and falsification criteria table with limited narrative explanation

**Type:** clarity

**Issue:** Tables are dense data without narrative bridges explaining how to read them and what patterns matter.

**Suggestion:** Add narrative paragraphs:
- Before Table 3: "The hypothesis chain follows strict dependency logic. Each row represents a testable sub-hypothesis with pre-specified success criteria. The 'If Fail' column determines routing: ABORT means fundamental redesign needed, MODIFY means pursue alternative mechanisms."
- Before Table 4: "Each assumption has explicit falsifiers—observable outcomes that would invalidate the assumption. The 'Consequence' column shows why each assumption matters for interpretability."

**Rationale:** Helps readers understand table structure and significance without requiring dense reading.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

## Content Gaps (3 issues)

### MINOR-10: Missing Visual (Figure 1)

**Location:** Methodology Section 3.4 (line 149 mentions "Figure 1 (planned)" but not generated)

**Type:** clarity

**Issue:** Architectural diagram mentioned but not included. Would significantly help reader comprehension of policy-layer separation concept.

**Suggestion:** Generate Figure 1 showing:
- Base model (frozen) vs. Policy layer (modulated)
- λ parameter input → System prompts → Model output
- ACE operationalization via policy-layer manipulation
- Visual separation between capability (base) and compliance (policy)

**Rationale:** Complex architectural concept benefits from visual representation. Referenced in text but missing.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-11: Novelty Positioning Delayed in Introduction

**Location:** Introduction (line 24 clarifies "methodological contribution" but comes late)

**Type:** clarity

**Issue:** Readers may expect empirical paper based on title/abstract. Methodological positioning appears late in Introduction (after contributions enumeration).

**Suggestion:** Add clarifying sentence earlier, after "Key insight" paragraph (line 15):
- "This architectural approach enables a methodological contribution: the first measurement framework for bidirectional alignment in AI safety contexts, not empirical findings about coupling dynamics."

**Rationale:** Sets reader expectations early, reducing risk of disappointment when reaching "experiments not executed" disclosure.

**Note:** This was partially addressed in revision via new paragraph after "Key insight". Review if sufficient or needs earlier positioning.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-12: Citation Verification Pending

**Location:** All citations (25 total, all marked [UNVERIFIED] per Ground Truth)

**Type:** verification

**Issue:** All 25 citations are unverified placeholders. Must verify via Semantic Scholar MCP before submission.

**Suggestion:** Before final submission:
1. Use Semantic Scholar MCP to verify each citation
2. Update citation metadata (authors, year, title, venue)
3. Remove [UNVERIFIED] markers
4. Ensure DOI/URL links are functional

**Rationale:** Ground Truth line 174 action required—citations must be verified for publication-ready manuscript.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

## Summary for Human Reviewer

**Total MINOR Issues:** 12
- **Terminology precision:** 3 issues
- **Tone/framing:** 2 issues
- **Structural/formatting:** 4 issues
- **Content gaps:** 3 issues

**Recommended Action Priority:**
1. **HIGH PRIORITY (affects submission readiness):**
   - MINOR-12: Citation verification (required before submission)
   - MINOR-7: Venue positioning (affects submission strategy)
   - MINOR-10: Figure 1 generation (referenced but missing)

2. **MEDIUM PRIORITY (improves clarity):**
   - MINOR-1, 2, 3: Terminology precision (validates paper maturity accurately)
   - MINOR-4: Tone adjustment (removes defensive framing)
   - MINOR-9: Table scaffolding (helps reader comprehension)

3. **LOW PRIORITY (polish):**
   - MINOR-6: Abstract length (minor formatting issue)
   - MINOR-8: Section 4 structure (preference-based)
   - MINOR-5, 11: Consistency checks (mostly addressed in MAJOR fixes)

**Estimated Review Time:** 1-2 hours for human reviewer to make decisions and implement accepted changes.

---

## Round 2 Minor Issues

**Generated:** Round 2 Adversarial Review  
**Date:** 2026-05-11  
**Status:** NOT AUTO-FIXED (requires human review and decision)

---

### MINOR-R2-1: Abstract Length Over ICML Guideline

**Location:** Abstract

**Type:** formatting

**Current length:** ~220 words (ICML guideline: ~150 words)

**Issue:** R1 abstract revision improved content significantly but didn't reduce length. Still exceeds typical ICML guideline by ~70 words.

**Suggestion:** Trim to ~170 words by condensing technical details:
- Current: "AI Compliance Elasticity (ACE) via policy-layer parameter manipulation (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}) and Human Oversight Retention (HOR) via signal detection d' on seeded within-distribution errors"
- Compressed: "AI Compliance Elasticity (ACE) via policy-layer parameter manipulation and Human Oversight Retention (HOR) via signal detection d'"
- Savings: ~35 words

**Rationale:** Content is strong, length overage acceptable for methodological paper, but technically violates guideline. Consider condensing for journal submission.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-R2-2: Terminology Inconsistency in Section 3.4

**Location:** Methodology Section 3.4 "Infrastructure Implementation"

**Type:** clarity

**Issue:** Section 3.4 uses "policy-layer parameter λ" but system prompt implementation uses "system prompts" terminology. Some inconsistency between "policy-layer modulation" and "system prompt modulation" throughout paper.

**Current examples:**
- Section 3.1: "policy-layer modulation via system prompts"
- Section 3.4: "APIModelClient wraps Claude 3 Opus API with policy-layer parameter λ, mapping λ values to system prompts"
- Some places say "policy-layer" alone, others "system prompt" alone

**Suggestion:** Unify terminology consistently:
- Option 1: Always use "policy-layer modulation via system prompts" (full phrase)
- Option 2: Use "policy-layer modulation" for conceptual discussion, "system prompt implementation" for technical details

**Rationale:** Improves clarity by maintaining consistent terminology. Readers shouldn't wonder if "policy-layer" and "system prompt" refer to different mechanisms.

**Reviewer Decision:** [ ] Accept Option 1  [ ] Accept Option 2  [ ] Reject  [ ] Modify

---

### MINOR-R2-3: Section 2.5 List Formatting

**Location:** Related Work Section 2.5 "Positioning: The Gap We Address"

**Type:** formatting

**Issue:** The 5-item novelty list uses narrative style (full sentences) instead of concise bullet points with bold lead-ins, making it harder to scan quickly.

**Current format:**
"We are the first to:
1. Operationalize alignment-oversight coupling specifically via capability-invariant policy-layer manipulation in AI safety contexts
2. Leverage architectural separation (Constitutional AI policy layer) to enable testable capability invariance
3. Apply signal detection d' to measure oversight degradation in AI collaboration contexts
4. Design experimental protocols with explicit falsification criteria (ICC > 0.95 gate for prerequisite validity)
5. Integrate automation bias mechanisms (Bayesian trust calibration) into AI alignment evaluation"

**Suggestion:** Add bold phrases for scannability:
"We are the first to:
1. **Capability-invariant manipulation:** Operationalize alignment-oversight coupling via policy-layer manipulation in AI safety contexts
2. **Architectural separation:** Leverage Constitutional AI policy layer to enable testable capability invariance
3. **Signal detection measurement:** Apply d' to measure oversight degradation in AI collaboration contexts
4. **Falsification criteria:** Design experimental protocols with explicit success thresholds (ICC > 0.95 gate)
5. **Automation bias integration:** Integrate Bayesian trust calibration mechanisms into AI alignment evaluation"

**Rationale:** Bold lead-ins help readers quickly scan the 5 novelty dimensions without reading full sentences. Common pattern in academic papers for multi-item contribution lists.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

### MINOR-R2-4: Limitation 4 Heading Inconsistency

**Location:** Discussion Section 6.2 Limitations

**Type:** formatting

**Issue:** R1 changelog says "Changed 'Why Acceptable' → 'Rationale and Mitigation'" but checking paper text shows Limitation 4 uses different structure than Limitations 1-3.

**Current structure:**
- **Limitation 1:** Has "**Rationale and Mitigation:**" subsection ✓
- **Limitation 2:** Has "**Rationale and Mitigation:**" subsection ✓
- **Limitation 3:** Has "**Rationale and Mitigation:**" subsection ✓
- **Limitation 4:** Has "**Why This Matters**" and "**Mitigation:**" subsections (not "Rationale and Mitigation") ⚠️

**Suggestion:** Change Limitation 4 to match structure:
- Combine "**Why This Matters**" content into "**Rationale and Mitigation:**" subsection for consistency with Limitations 1-3

**Rationale:** Consistent subsection structure improves readability and makes parallel structure clearer. All four limitations should follow same formatting pattern.

**Reviewer Decision:** [ ] Accept  [ ] Reject  [ ] Modify

---

## Summary for Human Reviewer

**Total Round 2 MINOR Issues:** 4
- **Formatting:** 3 issues (abstract length, list formatting, heading consistency)
- **Clarity:** 1 issue (terminology inconsistency)

**Recommended Action Priority:**
1. **MEDIUM PRIORITY (improves polish):**
   - MINOR-R2-2: Terminology consistency (affects clarity throughout paper)
   - MINOR-R2-3: Section 2.5 formatting (improves scannability of key contribution list)

2. **LOW PRIORITY (minor polish):**
   - MINOR-R2-1: Abstract length (content strong, guideline overage acceptable)
   - MINOR-R2-4: Limitation 4 heading (formatting consistency preference)

**Estimated Review Time:** 15-30 minutes for human reviewer to make decisions and implement accepted changes.

**Notes:**
- These issues are cosmetic/polish improvements, not correctness problems
- All MAJOR R2 issues have been addressed in 06_paper_r2.md
- Paper is ready for convergence check after these minor polish decisions (if any) are made
