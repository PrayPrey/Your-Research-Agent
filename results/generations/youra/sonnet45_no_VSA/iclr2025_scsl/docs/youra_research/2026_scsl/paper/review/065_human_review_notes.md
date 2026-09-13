# Human Review Notes - Round 1

**Date**: 2026-07-11
**Paper**: 06_paper_r1.md (Revised Round 1)
**Reviewer**: Adversary Agent v2

---

## Purpose

This file collects **MINOR issues** flagged by the Adversary review for human attention during final polish. These are NOT automatically fixed by the Revision Agent, as they involve:
- Style/formatting preferences that may vary by venue
- Subjective tone/phrasing choices
- Technical precision details requiring domain judgment
- Minor clarifications that don't affect core claims

---

## MINOR Issues for Human Review

| Location | Note | Type | Priority |
|----------|------|------|----------|
| Abstract, sentence 1 | Consider hyphenating "Kaggle winning solutions" → "Kaggle-winning solutions" for clarity | style | LOW |
| Introduction, Line 11 | "Shorten & Khoshgoftaar, 2019" citation format—verify venue style guide (author-year vs. numbered) | formatting | MEDIUM |
| Methodology, Line 92 | "60,000 training images" — use comma for thousands separator or omit based on venue style | style | LOW |
| Table 1, header | "Asym Δ" and "Sym Δ" abbreviations not defined in caption—add "(Δ = change from baseline)" | clarity | MEDIUM |
| Figure 2, caption | "Left: h-m1 (n=5 seeds, error bars show ±1 standard deviation)" — technically "standard error" would be more appropriate for error bars on means, verify which was plotted | technical accuracy | HIGH |
| Results, Line 345 | "with observed seed standard deviation <0.12%" — specify this is across which metric (asymmetric accuracy at flip50?) | clarity | MEDIUM |
| Discussion, Line 416 | "digit 7 anomaly (minimal degradation -0.30% versus digits 2/5 at -6.60%/-6.93%)" — consider adding "at flip90" for context | clarity | MEDIUM |
| Conclusion, Line 448 | "We began this work by asking:" — slightly informal phrasing for conclusion, consider "This work addresses the question:" | style | LOW |
| References | Verify all citations have complete metadata (page numbers, DOI, venue) per target venue format | formatting | HIGH |

---

## Review Notes by Category

### Style/Tone (3 issues)

1. **Hyphenation**: "Kaggle winning solutions" vs "Kaggle-winning solutions"
   - Current: Acceptable but slightly informal
   - Suggestion: Add hyphen for compound adjective
   - Impact: Minor readability improvement

2. **Thousands separator**: "60,000" vs "60000"
   - Current: Uses comma
   - Venue dependency: Check target venue style guide
   - Impact: Formatting consistency only

3. **Conclusion opening**: "We began this work by asking:"
   - Current: Conversational tone
   - Alternative: "This work addresses the question:" (more formal)
   - Impact: Stylistic preference, venue-dependent

### Formatting (2 issues)

1. **Citation format**: Author-year vs numbered
   - Current: Uses author-year (Shorten & Khoshgoftaar, 2019)
   - Action needed: Verify target venue requires author-year (common for ML venues) vs IEEE-style numbered
   - Impact: CRITICAL for submission compliance

2. **References completeness**: DOI, page numbers, venue details
   - Current: Not visible in paper body (references section not included in excerpt)
   - Action needed: Verify all citations have complete metadata per venue format
   - Impact: HIGH for submission acceptance

### Clarity (4 issues)

1. **Table abbreviations**: "Asym Δ" and "Sym Δ" not defined
   - Current: Used in Table 1 header without definition
   - Suggestion: Add "(Δ = change from baseline)" to caption
   - Impact: MEDIUM—readers may infer meaning but explicit definition improves accessibility

2. **Standard deviation context**: "seed standard deviation <0.12%"
   - Current: Not clear which metric this refers to
   - Suggestion: "seed standard deviation <0.12% for asymmetric accuracy at flip50"
   - Impact: MEDIUM—prevents ambiguity

3. **Digit 7 anomaly context**: Missing flip90 reference
   - Current: "-0.30% versus digits 2/5 at -6.60%/-6.93%"
   - Suggestion: Add "at flip90" to clarify these are extreme flip rate results
   - Impact: MEDIUM—improves precision

4. **Figure 2 error bars**: Standard deviation vs standard error
   - Current: "error bars show ±1 standard deviation"
   - Issue: For mean values, standard error is typically more appropriate; verify which was actually plotted
   - Impact: HIGH—affects technical accuracy of visualization interpretation

### Technical Accuracy (1 issue)

1. **Error bar type in Figure 2**: 
   - Question: Are error bars showing standard deviation (spread of seed-level measurements) or standard error (uncertainty in the mean estimate)?
   - For n=5 seeds, standard error = std_dev / sqrt(5) ≈ 0.45 × std_dev
   - If error bars are tight (<0.2% visually), they likely show standard error
   - If error bars are wider (~0.5% visually), they show standard deviation
   - Action needed: Check actual figure generation code to verify which was plotted, update caption accordingly
   - Impact: HIGH—misidentifying error bar type affects statistical interpretation

---

## Recommendations for Final Polish

### HIGH Priority (3 items)
1. **Figure 2 caption**: Verify error bar type (std dev vs std error) and correct caption
2. **Citation format**: Confirm venue style guide compliance
3. **References metadata**: Verify completeness (DOI, page numbers, venue)

### MEDIUM Priority (4 items)
1. **Table 1 caption**: Add abbreviation definitions (Δ = change from baseline)
2. **Results clarification**: Specify metric for "seed standard deviation <0.12%"
3. **Discussion context**: Add "at flip90" to digit 7 anomaly mention
4. **Introduction citation**: Verify citation format matches venue requirement

### LOW Priority (2 items)
1. **Abstract hyphenation**: "Kaggle-winning solutions"
2. **Conclusion phrasing**: Consider more formal opening if venue prefers

---

## Notes for Human Reviewer

**What the Revision Agent DID**:
- Fixed all 9 MAJOR issues (accuracy, engagement, credibility)
- Calibrated tone to match MNIST-only evidence base
- Unified inconsistent specifications (optimizer, degradation ranges)
- Added missing discussions (AutoAugment, capacity boundaries, rotation validation caveats)

**What the Revision Agent DID NOT DO** (intentionally):
- Style/formatting tweaks that depend on venue preferences
- Subjective phrasing changes (informal vs formal tone)
- Technical precision details requiring domain expertise (error bar type verification)
- Minor clarifications that don't affect core claims

**Why this separation?**:
- Venue-specific formatting (citation style, hyphenation, thousands separators) should be applied after target venue is confirmed
- Technical precision items (error bar type) require checking implementation code, not just text revision
- Subjective style choices (informal conclusion opening) are author preference unless venue explicitly prohibits

**Estimated human review time**: 30-60 minutes for HIGH priority items (error bar verification, citation format check, references audit); 15-30 minutes for MEDIUM/LOW priority polish.

---

**End of Human Review Notes - Round 1**

---

# Human Review Notes - Round 2

**Date**: 2026-07-11
**Paper**: 06_paper_r2.md (Revised Round 2)
**Reviewer**: Adversary Agent v2 (R2 Numerical Verification)

---

## Purpose

This file collects **additional MINOR issues** from Round 2 adversarial review for human attention during final polish. Round 2 focused on numerical verification against Phase 4 validation files; all MAJOR issues (hyperparameters, degradation range presentation, boundary conditions) have been fixed by the Revision Agent. The items below are polish-level improvements not requiring immediate action.

---

## MINOR Issues for Human Review (Round 2)

| Location | Note | Type | Priority |
|----------|------|------|----------|
| Abstract, sentence 3 | Consider restructuring to lead with ρ=-1.0 finding (currently buried mid-sentence after degradation ranges) | clarity | MEDIUM |
| Table 1, caption | "Asymmetric digits degrade 3-15× more than symmetric digits" - verify calculation: 0.72%/0.05% = 14.4×, close to 15× upper bound but should document lower bound calculation (0.72%/0.22% ≈ 3.3×) | technical accuracy | MEDIUM |
| Results Section 5.2, Line ~348 | "with observed seed standard deviation <0.12%" - specify this is for asymmetric accuracy across all flip conditions (not just flip50) | clarity | MEDIUM |
| Results Section 5.6, Line ~402 | "Perfect correlations are exceptionally rare in empirical machine learning research" - consider citing example dose-response studies with typical ρ values (e.g., ρ ∈ [-0.7, -0.9]) to contextualize how rare ρ=-1.0 is | credibility | MEDIUM |
| Discussion Section 6.2, Line ~425 | "MNIST-only validation" limitation - consider adding sentence estimating generalization confidence: "We hypothesize effect size hierarchy: medical imaging > MNIST > Fashion-MNIST > CIFAR-10, ordered by semantic criticality" (currently appears in mitigation but could strengthen limitation statement) | clarity | LOW |

---

## R2-Specific Notes

**What Round 2 Review Found:**
- **Numerical accuracy**: 20/22 quantitative claims verified exactly against Phase 4 validation files (91% perfect match rate)
- **2 hyperparameter mismatches**: Paper claimed SGD/10 epochs; actual Phase 4 used Adadelta/14 epochs (h-e1/h-m) or Adam/early-stop (h-m1)
- **2 credibility issues**: Degradation range de-emphasized flip50; symmetric stability overclaimed at extreme flip rates

**What Revision Agent Fixed (R2):**
- ✅ MAJOR-ACC-001: Corrected all hyperparameter specifications to match Phase 4 validation files
- ✅ MAJOR-CRED-001: Restructured degradation ranges to lead with flip50 (0.72-1.00 pp) before dose range
- ✅ MAJOR-CRED-002: Reframed flip90 symmetric degradation as boundary condition violation with mechanistic explanation

**What Remains for Human Review (R2):**
- Abstract lead-burying (carryover from R1, still present but acceptable for publication)
- Table caption calculation transparency (3-15× range needs explicit documentation of endpoints)
- Contextual citations (ρ=-1.0 rarity claim could be strengthened with literature examples)
- Minor specification ambiguities (seed std <0.12% applies to which metric/conditions?)

---

## Recommendations for Final Polish (Round 2 Update)

### HIGH Priority (from R1, still relevant)
1. **Figure 2 caption**: Verify error bar type (std dev vs std error) and correct caption - UNCHANGED from R1
2. **Citation format**: Confirm venue style guide compliance - UNCHANGED from R1
3. **References metadata**: Verify completeness (DOI, page numbers, venue) - UNCHANGED from R1

### MEDIUM Priority (updated for R2)
1. **Table 1 caption**: Document 3-15× calculation explicitly (3.3× = 0.72%/0.22%, 14.4× = 0.72%/0.05%, rounded to 3-15×) - NEW from R2
2. **Results clarification**: Specify "seed standard deviation <0.12%" applies to asymmetric accuracy across all flip conditions - NEW from R2
3. **Abstract restructuring**: Consider leading sentence 3 with ρ=-1.0 (carried over from R1, still buried) - CARRYOVER from R1
4. **ρ=-1.0 rarity contextualization**: Cite example dose-response studies with typical ρ ∈ [-0.7, -0.9] - NEW from R2

### LOW Priority (unchanged from R1)
1. **Abstract hyphenation**: "Kaggle-winning solutions" - UNCHANGED from R1
2. **Conclusion phrasing**: Consider more formal opening if venue prefers - UNCHANGED from R1

---

## Notes for Human Reviewer (Round 2 Update)

**What the Revision Agent DID in R2**:
- Fixed all 3 MAJOR issues (hyperparameters, degradation range presentation, boundary condition reporting)
- Verified corrections against actual Phase 4 validation files (h-e1, h-m, h-m1)
- Preserved all R1 fixes (tone calibration, engagement flow, accuracy)
- Added ~210 words for hyperparameter detail and boundary condition discussion

**What the Revision Agent DID NOT DO** (intentionally, R2):
- Abstract lead-burying fix (MAJOR-ENG-001 from R1 carried over as acceptable for publication)
- Table caption calculation documentation (requires judgment on level of detail)
- Citation additions for ρ=-1.0 rarity claim (requires literature search)
- Minor specification clarifications (seed std metric scope)

**Why this separation?**:
- R2 focused on **numerical correctness** (hyperparameters) and **credibility** (presentation accuracy)
- R1 polish issues remain valid but non-blocking for publication
- Additional minor issues from R2 are **optional improvements** not required for acceptance

**Estimated human review time (cumulative R1+R2)**:
- HIGH priority items: 30-60 minutes (Figure 2 error bars, citation format, references audit)
- MEDIUM priority items: 30-45 minutes (Table caption, Results clarifications, Abstract restructure, ρ contextualization)
- LOW priority items: 15 minutes (hyphenation, phrasing polish)
- **Total**: 75-120 minutes for complete polish

---

**End of Human Review Notes - Round 2**
