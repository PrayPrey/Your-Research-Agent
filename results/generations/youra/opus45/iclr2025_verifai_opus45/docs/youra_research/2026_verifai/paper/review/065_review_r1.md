# Phase 6.5 Adversary Review - Round 1

**Paper:** "Less Is More: Error Feedback Granularity for LLM Code Repair"
**Review Date:** 2026-03-30
**Round:** R1 (Accuracy and Engagement)
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Executive Summary

| Severity | Count | Details |
|----------|-------|---------|
| **FATAL** | 0 | No fundamental contradictions found |
| **MAJOR** | 2 | Issues requiring revision before acceptance |
| **MINOR** | 5 | Style/clarity issues for human review |

**Recommendation:** MINOR_REVISION - Paper is technically sound with accurate numbers. Two major issues need addressing.

---

## Ground Truth Verification Summary

### Verified Claims (Paper vs Ground Truth)

| Claim | Paper States | Ground Truth | Status |
|-------|-------------|--------------|--------|
| G0 success rate | 41.8% | 41.8% (127/304) | ✓ MATCH |
| G1 success rate | 40.8% | 40.8% (124/304) | ✓ MATCH |
| G2 success rate | 18.4% | 18.4% (56/304) | ✓ MATCH |
| G3 success rate | 16.8% | 16.8% (51/304) | ✓ MATCH |
| G4 success rate | 22.7% | 22.7% (69/304) | ✓ MATCH |
| ANOVA F-statistic | 23.89 | 23.89 | ✓ MATCH |
| ANOVA p-value | p < 10⁻¹⁸ | 3.5e-19 | ✓ MATCH |
| Effect size (η²) | 0.059 | 0.059 | ✓ MATCH |
| Runtime error prevalence | 60.8% | 60.8% (304/500) | ✓ MATCH |
| G0 vs G3 difference | 25pp | 25.0pp | ✓ MATCH |
| McNemar G0 vs G3 | p < 10⁻²¹ | 5.23e-22 | ✓ MATCH |
| McNemar G3 vs G4 | p < 10⁻⁴ | 4.0e-05 | ✓ MATCH |
| 95% CI for G0 | [36.3%, 47.4%] | [36.3%, 47.4%] | ✓ MATCH |

**Ground Truth Verification Result:** ALL NUMERICAL CLAIMS VERIFIED ✓

---

## Persona 1: Accuracy Checker

### Focus: Numerical accuracy, methodology consistency, claim verification

#### Verified Without Issues:

1. **All quantitative claims match ground truth** - See table above
2. **Statistical tests correctly reported** - ANOVA, McNemar's, Tukey HSD all accurate
3. **Confidence intervals correctly stated** - Wilson score intervals match
4. **Effect size interpretation correct** - η²=0.059 is "medium" per Cohen's guidelines (0.01=small, 0.06=medium, 0.14=large)

#### No FATAL Issues Found

#### No MAJOR Issues from Accuracy Perspective

#### Minor Accuracy Notes:
- Abstract says "p < 10⁻¹⁸" while actual value is 3.5e-19 - this is accurate rounding ✓
- Paper says "25 percentage point gap" - actual is exactly 25.0pp ✓

---

## Persona 2: Bored Reviewer

### Focus: Engagement, clarity, "would I keep reading?"

#### First Impression Test:

| Check | Question | Assessment |
|-------|----------|------------|
| Abstract Compelling? | Would I continue reading after abstract? | **YES** - Counterintuitive result (41% vs 17%) immediately grabs attention |
| Problem Clear in 1 min? | Can I understand the problem quickly? | **YES** - "How much error info should we give LLMs?" is immediately clear |
| Novelty Clear in 2 min? | Do I understand what's new? | **YES** - "First systematic granularity comparison" stated explicitly |
| Figure 1 Self-Explanatory? | Can I understand main figure without text? | **N/A** - No Figure 1 in paper (tables used instead) |

#### Engagement Assessment:

**Would Continue Reading:** YES

**Attention Lost At:** NEVER - The counterintuitive finding maintains engagement throughout

#### MAJOR-ENGAGE-001: Missing Visual Hook

**Issue:** The paper lacks a compelling visual figure (e.g., bar chart of G0-G4 success rates) in the opening. While the paper references figures like "fig_3" and "fig_5" in related materials, the main paper text describes Table 2 rather than showing a striking visual.

**Why MAJOR:** A busy reviewer scanning the paper might miss the dramatic 25pp difference without a visual hook. The two-cluster pattern would be instantly clear in a figure.

**Suggested Fix:** Add a bar chart figure early (after Abstract or in Section 1.2) showing G0/G1 at ~41% vs G2/G3/G4 at ~17-23% with visual emphasis on the gap.

---

## Persona 3: Skeptical Expert

### Focus: Novelty claims, baseline fairness, overclaims, missing limitations

#### Novelty Assessment:

| Contribution Claim | Valid? | Assessment |
|-------------------|--------|------------|
| "First systematic granularity comparison (G0-G4)" | ✓ Valid | Table 1 shows prior work used fixed levels without comparison |
| "Evidence detailed feedback can hurt repair" | ✓ Valid | Quantified with strong statistics |
| "Two-cluster pattern discovery" | ✓ Valid | Novel observation with post-hoc confirmation |
| "Methodological framework" | ✓ Valid | Within-subject design is sound |

**No false novelty claims found.**

#### Baseline Fairness Assessment:

The paper uses G0 (minimal feedback) as baseline and compares Self-Debug (G2-level). This is fair:
- G0 represents "naive retry" - appropriate minimal baseline
- Self-Debug comparison contextualizes results with prior work

**No unfair baseline comparisons found.**

#### Overclaim Assessment:

| Statement | Overclaim? | Assessment |
|-----------|------------|------------|
| "Minimal feedback dramatically outperforms detailed feedback" | No | 25pp gap with p<10⁻²¹ supports "dramatically" |
| "Challenges fundamental assumption" | Borderline | Strong but scoped to 7B scale |
| "Less is more" (title) | No | Accurate for experimental scope |

**Overclaims Found:** 0

#### MAJOR-SCOPE-001: Limitations Section Could Be Stronger on Generalization

**Issue:** While the paper acknowledges limitations (L1-L6), the Discussion (6.4) doesn't sufficiently emphasize that the inverse relationship may not hold for larger models. The paper repeatedly says "at the 7B scale" but the title "Less Is More" and some discussion framing could be read as a general claim.

**Why MAJOR:** A skeptical reviewer might reject the paper for appearing to overclaim. The limitation section is present but could be more prominent.

**Evidence:**
- Title says "Less Is More" without qualifier
- Abstract end says "feedback strategies should be scale-aware" (appropriate)
- But Discussion 6.1 Hypothesis 3 (Model Capacity) is presented as "plausible" without strong caveats

**Suggested Fix:**
1. Add explicit qualifier in title or abstract: "Less Is More *at 7B Scale*" or make the scope crystal clear in abstract's final sentence
2. Strengthen the caveat language in Discussion 6.1: "These findings are specific to the 7B scale and may not generalize to larger models where capacity constraints differ"

#### Missing Limitations Check:

| Potential Limitation | Acknowledged? |
|---------------------|---------------|
| Single model (7B) | ✓ L1 |
| Single benchmark (MBPP) | ✓ L2 |
| Single template (Self-Debug) | ✓ L3 |
| Single repair attempt | ✓ L4 |
| Deterministic generation (T=0) | ✓ L5 |
| Runtime errors only | ✓ L6 |
| No multi-turn repair | ✓ L4 mentions |
| No attention analysis | ✓ 7.2 Future Work |

**Missing Limitations:** None critical - paper is thorough

---

## Persuasiveness Checks Summary (v2.0)

| Check | Result |
|-------|--------|
| abstract_compelling | TRUE |
| problem_clear_in_1_minute | TRUE |
| novelty_clear_in_2_minutes | TRUE |
| figure_1_self_explanatory | N/A (no figure) |
| would_continue_reading | TRUE |
| attention_lost_at | NEVER |
| false_novelty_claims_found | 0 |
| unfair_baseline_comparisons | 0 |
| overclaims_found | 0 |
| missing_limitations | FALSE |

**Persuasiveness Passed:** TRUE (with minor visual enhancement recommended)

---

## FATAL Issues (0)

None found. Paper has no fundamental contradictions or impossible claims.

---

## MAJOR Issues (2)

### MAJOR-ENGAGE-001: Missing Visual Hook

- **Severity:** MAJOR
- **Persona:** Bored Reviewer
- **Location:** Introduction / Results
- **Issue:** No compelling bar chart figure showing the dramatic G0-G4 success rate pattern
- **Evidence:** Paper describes Table 2 but visual impact is lost
- **Impact:** Reduced engagement for scanning reviewers
- **Fix Required:** Add bar chart figure early in paper

### MAJOR-SCOPE-001: Title/Scope Qualifier Needed

- **Severity:** MAJOR
- **Persona:** Skeptical Expert
- **Location:** Title, Abstract, Discussion 6.1
- **Issue:** "Less Is More" title without scale qualifier may appear as overclaim
- **Evidence:** Findings are 7B-specific, but title/framing is absolute
- **Impact:** Risk of rejection for appearing to overclaim
- **Fix Required:** Add "at 7B Scale" qualifier or strengthen scope caveats

---

## MINOR Issues (5) - Collected for Human Review

### MINOR-001: Style - Section Transition
- **Location:** Section 1.3 to Section 2
- **Issue:** Transition sentence "The remainder of this paper proceeds as follows" is formulaic
- **Recommendation:** Consider removing or making more engaging

### MINOR-002: Typo Check
- **Location:** Throughout
- **Issue:** Paper appears clean, no typos found
- **Status:** No action needed

### MINOR-003: Citation Format
- **Location:** References
- **Issue:** Some citations use "arXiv preprint" while others use conference names - inconsistent
- **Recommendation:** Standardize citation format

### MINOR-004: Table Formatting
- **Location:** Table 2, Table 3
- **Issue:** Tables are clear but could benefit from visual hierarchy
- **Recommendation:** Consider bolding key result rows

### MINOR-005: Abstract Length
- **Location:** Abstract
- **Issue:** Abstract is 167 words - within ICML limit but dense
- **Recommendation:** Could be slightly tightened

---

## Cross-Reference Verification Log

| Check | Status |
|-------|--------|
| Abstract claims match Results numbers? | ✓ All verified |
| Methodology (Sec 3) matches Experiments (Sec 4)? | ✓ Consistent |
| Introduction claims match Conclusion? | ✓ Consistent |
| Statistical tests match reported results? | ✓ All verified |
| Confidence intervals correct? | ✓ Verified |
| Hypothesis outcomes correctly stated? | ✓ H-E1 PASS, H-M1 PASS, H-M2 FAIL, H-M3 FAIL - all correct |

---

## Summary for Revision Agent

### Priority 1 (MUST FIX - MAJOR):
1. **Add visual figure** - Bar chart of G0-G4 success rates with clear two-cluster pattern
2. **Add scope qualifier** - Either modify title or strengthen scope language in abstract/discussion

### Priority 2 (SHOULD FIX - MAJOR):
- Strengthen Discussion 6.1 caveat language about scale-specificity

### Priority 3 (COLLECT FOR HUMAN - MINOR):
- 5 minor issues collected in `065_human_review_notes.md`

---

## Round 1 Verdict

| Criterion | Status |
|-----------|--------|
| FATAL issues | 0 |
| MAJOR issues | 2 |
| Ground truth verified | YES |
| Persuasiveness passed | YES |
| Proceed to revision | YES |

**Recommendation:** Proceed to Revision R1 to address the 2 MAJOR issues.

---

*Generated by Phase 6.5 Adversary Review Workflow v2.0*
*Three-Persona Review: Accuracy Checker, Bored Reviewer, Skeptical Expert*
*Round: R1 - Accuracy and Engagement*
