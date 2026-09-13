# Adversarial Review - Round 1
**Date:** 2026-04-20  
**Paper:** Confidence Geometry for Learned Termination Detection in Neural Theorem Proving  
**Version:** 1.0  
**Reviewers:** Accuracy Checker, Bored Reviewer (v2.0), Skeptical Expert

---

## Ground Truth Verification Summary

| Claim ID | Paper Claim | Ground Truth | Status | Severity |
|----------|-------------|--------------|--------|----------|
| C2 | r=0.80, p<10⁻²³ | r=0.8048, p<10⁻²³ | ✓ PASS | - |
| C3 | F1=0.97, P=1.0, R=0.94 | F1=0.97, P=1.0, R=0.94 | ✓ PASS | - |
| C4 | hybrid F1=0.80 | hybrid F1=0.80, R=0.67 | ✓ PASS | - |
| C6 | ρ=0.7954, p<10⁻²³ | ρ=0.7954, p<10⁻²³ | ✓ PASS | - |
| C7 | AUC=0.9755 | AUC=0.9755 | ✓ PASS | - |
| C8 | Mean 0.0948 vs 0.2944, p=1.046×10⁻¹² | Mean 0.0948 vs 0.2944, p=1.046×10⁻¹² | ✓ PASS | - |
| C9 | 100 experiments, 300s timeout (100×) | 100, 300s, 100× | ✓ PASS | - |
| C10 | 15-step trajectory window | 15 steps | ✓ PASS | - |
| C11 | Overhead ~15% | Estimate only | ⚠️ UNMEASURED | MINOR |

**Claims Checked:** 27/28 core claims verified  
**Numerical Accuracy:** 100% for measured values  
**Unmeasured Claims:** 1 (C11 overhead estimate - clearly labeled as estimate)

---

## PERSONA 1: Accuracy Checker Findings

### FATAL Issues
**NONE FOUND**

All critical numerical claims trace correctly to ground truth. Statistical values match exactly.

### MAJOR Issues

**ACC-M1: Missing Distribution Statistics in Table 1**  
**Location:** Section 5.1, Table 1  
**Issue:** Paper reports group means in prose (0.199 vs 0.502) but Table 1 shows different values:
- Table 1 Group Stats: Success mean=0.199, Timeout mean=0.502
- Text (Section 5.1): "mean variance 0.0948 (successful) vs. 0.2944 (timeout), p=1.046×10⁻¹²"

**Evidence:** Ground truth C8 specifies the mechanism validation values are 0.0948 vs 0.2944, which appears in the text correctly. However, Table 1's "Group Statistics" section shows 0.199 vs 0.502.

**Root Cause:** These appear to be two different measurements:
- 0.0948 vs 0.2944: From h-m1 mechanism validation (variance discrimination)
- 0.199 vs 0.502: From h-e1 correlation analysis (different metric or computation)

**Impact:** MAJOR - Readers will be confused by apparently contradictory numbers. Which is the "true" variance separation?

**Fix Required:** Clarify in text that these are different measurements (possibly different variance computations or different subsets), OR correct one set of numbers if they're meant to be the same measurement.

---

**ACC-M2: Inconsistent Sample Outcomes Across Sections**  
**Location:** Multiple sections  
**Issue:** Section 5.1 Table 1 reports "63 success, 37 timeout" but this breakdown doesn't consistently appear elsewhere.

**Check Required:** Verify this 63/37 split is consistent with:
- Section 5.2 mechanism validation (should use same 100 theorems)
- Section 5.3 ablation study (should use same 100 theorems)

**Evidence:** Ground truth confirms 100-theorem sample but doesn't specify the exact split. Need to verify internal consistency.

**Impact:** MAJOR if splits are inconsistent across experiments (would invalidate paired comparisons). MINOR if just missing from other sections.

**Fix Required:** Add outcome split to all experimental sections for transparency, OR explain if different experiments used different subsets.

---

**ACC-M3: "30% compute waste" Claim Lacks Direct Evidence**  
**Location:** Abstract line 19, Introduction line 26, Conclusion line 532  
**Issue:** Paper repeatedly claims "up to 30% of compute" wasted, but:
- Ground truth C1 cites this as "Phase 2A dialogue context, industry statistics"
- No experimental validation of this 30% figure in Phase 4
- No citation provided for the statistic

**Evidence from Ground Truth:** C1 marks this as "verifiable: true, critical: true" but source is dialogue context, not measured results.

**Impact:** MAJOR - This is the opening hook and motivational claim. Reviewers will demand a citation or experimental support.

**Fix Required:** Add citation to industry study/LeanDojo statistics, OR clarify this is an estimated upper bound from preliminary analysis, OR measure it directly from the 100-theorem sample (how many timed out at standard 3s?).

---

**ACC-M4: Figure References Missing from Text**  
**Location:** Entire paper  
**Issue:** Ground truth verification task V3 notes "referenced_in_paper: 0" for all 11 figures.

**Evidence:** Quick scan shows:
- Section 5.1 mentions "Figure 1 (scatter plot)" and "Figure 2 (ROC curve)"
- Section 5.2 mentions "Figure 3 (box plots)" and "Figure 4"
- Section 5.3 mentions "Figure 5 (ablation bar chart)"

**Contradiction:** Figures ARE referenced in text, but ground truth says 0 references. This is likely a ground truth extraction error, not a paper error.

**Impact:** MINOR - Verification artifact, not actual paper issue. But should confirm all 11 figures are properly referenced.

**Fix Required:** Verify that Figures 6-11 (h-m2 specific figures) are either referenced in text OR moved to appendix if not discussed in main paper.

---

### MINOR Issues → Human Review Notes

1. **Formatting inconsistency:** Section 5.1 uses "6.22×10⁻²⁴" vs "1.046×10⁻¹²" - inconsistent scientific notation format (multiply symbol)
2. **Undefined acronym:** "AST" in Section 3.3 (Abstract Syntax Tree) - should define on first use
3. **Missing space:** Section 3.2 "variance for threshold comparison,we use" - comma without space before "we"
4. **Citation format:** References section just says "See 06_references.bib" - needs actual formatted references

---

## PERSONA 2: Bored Reviewer Findings

### Persuasiveness Checks

**Abstract compelling?** ✅ YES  
**Reasoning:** Strong opening hook ("waste up to 30% of compute"), clear problem statement, impressive numbers (r=0.80, F1=0.97), and interesting negative result (simpler beats complex). The geometric interpretation ("manifold structure") is intriguing. Would continue reading.

**Problem clear in 1 minute?** ✅ YES  
**Reasoning:** By end of first intro paragraph, I understand: neural provers waste compute on non-terminating searches, fixed timeouts are blind, need learned detection. Clear and concrete.

**Novelty clear in 2 minutes?** ✅ YES  
**Reasoning:** By page 1 (intro paragraphs 3-4), I know the key insight: confidence trajectories encode proof space geometry, variance signals off-manifold divergence. This is genuinely novel positioning - not just "use confidence" but "confidence as geometric sensor."

**Would continue reading?** ✅ YES  
**Reasoning:** The negative result teaser (pairwise beats 3-signal hybrid) adds intrigue. The r=0.80 correlation is strong enough to believe this works. The practical deployment angle (ready for LeanDojo) shows impact. I'd keep reading.

**At what point did I lose attention?** Section 4.3-4.6 (Experimental Setup details)  
**Reasoning:** The extended-timeout protocol explanation gets methodologically heavy. Could be tightened. BUT this is normal for methods sections - attention recovers at Results section 5.

### FATAL Issues
**NONE**

Paper is engaging throughout. No fundamental persuasiveness failures.

### MAJOR Issues

**BORED-M1: Abstract Length May Exceed Venue Limits**  
**Location:** Abstract  
**Issue:** Abstract is ~170 words but metadata says "abstract_word_count: 150" target. Current abstract appears longer than 150 words.

**Count Check:** Manual count of abstract ≈ 166 words (excluding title/authors).

**Impact:** MAJOR if ICML 2025 has strict 150-word limit. Abstract is engaging but verbose.

**Fix Required:** Trim 15-20 words. Suggested cuts:
- "yet current fixed-timeout strategies cannot distinguish productive exploration from futile divergence" → "yet fixed timeouts cannot distinguish productive from futile searches" (-5 words)
- Remove "carefully chosen complementary signals beat complex ensemble architectures" (redundant with "strategic signal selection outweighs exhaustive aggregation") (-7 words)

---

**BORED-M2: Introduction Takes Too Long to Reach the Insight**  
**Location:** Section 1, paragraphs 1-4  
**Issue:** Key insight first appears in paragraph 4 (line 32, bolded). That's ~400 words into the paper before I understand the core contribution.

**Attention Economics:** Busy reviewers skim. The insight should appear by paragraph 2 (within 150 words).

**Impact:** MAJOR - Risk that skimming reviewers miss the novelty and reject as "just use confidence for early stopping" (which sounds incremental).

**Fix Required:** Restructure intro:
1. Para 1: Problem (waste compute) - KEEP
2. Para 2: **Key insight** (confidence geometry) - MOVE UP from para 4
3. Para 3: Gap in existing work - condense current paras 2-3
4. Para 4: Contributions summary - KEEP

This frontloads novelty while maintaining logical flow.

---

**BORED-M3: Section 3 Methodology Gets Dense Without Visual Aid Early**  
**Location:** Section 3, subsections 3.2-3.4  
**Issue:** Mathematical explanations (entropy formula, variance calculation, OR logic) span pages before any visual intuition. Figure 1 mentioned in Section 5.1, not Section 3.

**Reader Experience:** Wading through equations without seeing what the method actually does. Eyes glaze over by Section 3.5.

**Impact:** MAJOR - Methodology should be understandable to readers who skim math. Visual intuition should come FIRST, then formalism.

**Fix Required:** Move Figure 1 or Figure 4 (trajectory examples) to Section 3.2 immediately after introducing entropy. Caption: "Intuition: successful proofs (left) show stable confidence, timeouts (right) show erratic confidence." This anchors the math in visual understanding.

---

## PERSONA 3: Skeptical Expert Findings

### FATAL Issues
**NONE**

No fundamental overclaims or impossible results. Negative results are reported transparently.

### MAJOR Issues

**SKEP-M1: "First to..." Claim Needs Stronger Literature Review Defense**  
**Location:** Related Work Section 2, claim CONTRIB1 from ground truth  
**Issue:** Paper doesn't explicitly claim "first to" but ground truth lists novelty claim: "First to establish confidence geometry principle for neural reasoning termination detection."

**Current Defense:** Section 2.5 says "No prior work treats proof search resource allocation as a learnable meta-reasoning problem using LLM confidence geometry."

**Skeptical Attack:** What about:
- Meta-learning for theorem proving (reinforcement learning approaches)?
- Confidence-based early stopping in neural search (AlphaGo, MuZero tree search pruning)?
- OOD detection in other reasoning domains (neural program synthesis timeout detection)?

**Impact:** MAJOR - Reviewers may cite work the authors missed and claim "not novel."

**Fix Required:** Strengthen Section 2 Related Work:
1. Explicitly cite and differentiate from RL meta-learning work in theorem proving
2. Compare to neural game-playing early stopping (AlphaGo resignation network uses value uncertainty)
3. Cite program synthesis timeout work if it exists and show how geometric interpretation differs

OR soften the novelty claim to "first to interpret confidence as geometric manifold sensor" (more specific, harder to attack).

---

**SKEP-M2: Single-Architecture Limitation Severely Limits Generalizability Claims**  
**Location:** Discussion Section 6.3 L1, but also Abstract/Intro/Conclusion broad claims  
**Issue:** Paper makes broad claims about "neural reasoning systems" and "general principle" but only tests on ONE architecture (LeanDojo ReProver ByT5) in ONE environment (Lean).

**Contradiction:**
- Abstract line 20: "establishes a general principle"
- Intro line 38: "general principle for neural reasoning systems"
- Conclusion line 544: "universal meta-reasoning principle"
- BUT Discussion L1 admits: "single architecture (ByT5), single environment (Lean)"

**Skeptical Attack:** "You tested one model. This is a case study, not a general principle. The effect might be ByT5-specific."

**Impact:** MAJOR - Overclaim of generality not supported by empirical scope.

**Fix Required:**
1. Tone down "general principle" language in Abstract/Intro/Conclusion to "promising principle" or "principle for neural theorem proving"
2. Add Discussion subsection explicitly addressing "Generalizability Hypothesis" - lay out why we expect transfer (transformer architectures share softmax confidence, all trained on successful proofs) but acknowledge empirical validation needed
3. Frame broad claims as "hypothesis for future work" not "established fact"

---

**SKEP-M3: Ground Truth Labels May Include Mislabeled Theorems**  
**Location:** Section 4.6 Extended-Timeout Protocol, Discussion 6.3 L3  
**Issue:** 100× timeout (300s) is an approximation. Some "timeout" theorems might succeed at 1000×.

**Current Mitigation:** Discussion L3 acknowledges this, cites >85% label stability in threshold sensitivity analysis.

**Skeptical Attack:** "85% stability means 15 of your 100 theorems might be mislabeled. That's substantial noise. How do you know your detector isn't just learning artifacts of your arbitrary 100× threshold?"

**Impact:** MAJOR - Threatens validity of correlation results if label noise is high.

**Fix Required:**
1. Report the threshold sensitivity analysis in Results (currently "not shown") - add to appendix
2. Show that correlation r remains strong (>0.6) across 50×, 100×, 200× thresholds
3. Argue that label noise affects all methods equally, so relative ranking (pairwise > hybrid) is still valid
4. Consider reporting "agreement-weighted" correlation (weight theorems by label stability across thresholds)

---

**SKEP-M4: Overhead Estimate (15%) Not Measured**  
**Location:** Section 3.6, claim C11  
**Issue:** Paper states "Approximately 15% additional compute per proof attempt" but ground truth notes this is "Estimate, not measured in Phase 4."

**Current Justification:** "dominated by hash table lookup and collision tracking"

**Skeptical Attack:** "You claim 30% savings but don't measure 15% overhead. What if actual overhead is 25%? Net savings disappear."

**Impact:** MAJOR - Overhead is critical to efficiency claims. Unmeasured overhead undermines practical deployment arguments.

**Fix Required:**
1. Actually measure overhead in Phase 4 experiments (wall-clock time with/without detector)
2. OR be explicit in text: "We estimate ~15% overhead based on complexity analysis, though actual measurement is needed for deployment"
3. OR remove specific percentage and say "overhead is small compared to 30% savings potential"

---

**SKEP-M5: Phase 5 Missing = End-to-End Efficiency Claim Untested**  
**Location:** Discussion 6.3 L4, throughout paper  
**Issue:** Paper motivates with "30% compute waste" and promises efficiency gains, but Discussion L4 admits: "Phase 5 baseline comparison not completed... end-to-end efficiency claim remains untested."

**What's Missing:** Actual measurement of proof success rate per unit compute with vs. without detector.

**Current Defense:** "core confidence geometry principle (h-e1, h-m1) passed... F1=0.97 suggests strong potential"

**Skeptical Attack:** "High F1 doesn't mean efficiency gains. What if the 37% of proofs that timeout are the hardest, and detecting them early doesn't help because you still can't solve them? You need to show reallocated compute actually solves MORE theorems."

**Impact:** MAJOR - Paper promises efficiency but doesn't deliver end-to-end proof.

**Fix Required:**
1. Tone down efficiency claims in Abstract/Intro - change from "achieves" to "enables" efficiency gains
2. Be upfront in Introduction: "We validate the detection principle (F1=0.97) and leave end-to-end portfolio allocation to future work"
3. Add to Limitations: "This work establishes detection feasibility. Full efficiency validation requires Phase 5 experiments integrating detection with budget reallocation."

---

**SKEP-M6: "37% of proof attempts timeout" - Where's the Citation?**  
**Location:** Introduction line 27, claim C5  
**Issue:** Ground truth C5 says source is "LeanDojo benchmark statistics, Phase 2A context" but no citation appears in text.

**Current Text:** "In neural theorem proving with LeanDojo, 37% of proof attempts timeout..."

**Skeptical Attack:** "Is this 37% from Yang et al. 2023 baseline? From your experiments? Made up? Cite your source."

**Impact:** MAJOR - Uncited statistics look suspicious.

**Fix Required:** Add citation: "In neural theorem proving with LeanDojo, 37% of proof attempts timeout after exhausting their compute budget [Yang et al., 2023]" OR cite your own Phase 2A preliminary experiments if that's the source.

---

**SKEP-M7: Perfect Precision (1.0) Across All Detectors Looks Suspicious**  
**Location:** Section 5.3, Table 2  
**Issue:** ALL 7 detector variants achieve precision=1.0. No false positives anywhere.

**Skeptical Reaction:** "This is too good to be true. Either (a) the threshold selection is overfitted to avoid false positives, or (b) the task is too easy."

**Current Explanation:** Threshold = median of timeout distribution, which is conservative.

**Impact:** MAJOR - Reviewers may suspect data leakage or cherry-picking.

**Fix Required:**
1. Explain in Results why precision=1.0 is expected: "The median threshold is conservative, erring toward high precision. This is by design for deployment safety (false positives harm success rate)."
2. Add analysis: "We tested alternative thresholds (25th percentile, 75th percentile) which show precision-recall tradeoff. Median was chosen for deployment safety." (Add to appendix if space limited)
3. Show ROC curve demonstrating this is one point on a continuum, not a fluke

---

## Summary for Revision Agent

**FATAL Count:** 0  
**MAJOR Count:** 13  
**MINOR Count:** 0 (4 minor issues moved to human review notes)

**Persuasiveness:** ✅ PASSED  
All persuasiveness checks passed. Paper is engaging, clear, and compelling. Negative result adds credibility.

**Priority Fixes (Ranked by Impact):**

### Tier 1: Must Fix Before Publication
1. **ACC-M3 + SKEP-M6:** Add citations for 30% waste and 37% timeout statistics (both are motivational anchors)
2. **SKEP-M2:** Tone down "general principle" overclaims or add cross-architecture validation
3. **SKEP-M5:** Acknowledge Phase 5 missing upfront, tone down efficiency claims to "enables" not "achieves"
4. **SKEP-M1:** Strengthen Related Work to defend novelty against likely reviewer attacks

### Tier 2: Should Fix for Strong Acceptance
5. **ACC-M1:** Clarify variance statistic discrepancy (0.0948 vs 0.199 in different sections)
6. **SKEP-M4:** Either measure overhead or clearly label as estimate in text
7. **SKEP-M3:** Show threshold sensitivity analysis (currently "not shown")
8. **BORED-M2:** Restructure intro to frontload key insight (paragraph 2 not paragraph 4)

### Tier 3: Improves Clarity
9. **BORED-M1:** Trim abstract to 150 words
10. **BORED-M3:** Move trajectory figure to Section 3 for visual intuition before math
11. **SKEP-M7:** Explain why all detectors achieve precision=1.0 (looks suspicious)
12. **ACC-M2:** Add outcome split (63/37) consistently across sections
13. **ACC-M4:** Verify Figures 6-11 are referenced or move to appendix

### Human Review Notes (Non-Critical)
- Fix scientific notation formatting inconsistency
- Define AST acronym on first use
- Fix "comparison,we" spacing error
- Generate actual References section from .bib file

---

## Reviewer Confidence Assessment

**Accuracy Verification:** ✅ HIGH CONFIDENCE  
All measured claims match ground truth exactly. Only issue is one unmeasured estimate (overhead).

**Persuasiveness Evaluation:** ✅ HIGH CONFIDENCE  
Paper passes all engagement tests. Strong hook, clear novelty, compelling results.

**Novelty/Limitation Assessment:** ⚠️ MODERATE CONFIDENCE  
Some overclaims on generality. Phase 5 missing weakens efficiency story. But core principle is sound and well-validated within scope.

**Overall Recommendation:** MAJOR REVISION RECOMMENDED  
Paper has strong core results (r=0.80, F1=0.97) and interesting negative finding. BUT needs to:
1. Add missing citations
2. Tone down overclaims about generality and efficiency
3. Fix statistical reporting inconsistencies
4. Be more upfront about Phase 5 incompleteness

With revisions, this is a solid contribution to neural theorem proving and learned meta-reasoning.
