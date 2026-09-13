# Phase 6.5 Adversarial Review: Round 1 Findings

**Generated**: 2026-08-25T01:11:10Z  
**Reviewers**: Accuracy Checker, Bored Reviewer, Skeptical Expert  
**Paper**: 06_paper.md

---

## Summary Statistics

| Severity | Count | Action |
|----------|-------|--------|
| FATAL    | 0     | Must fix (blocks publication) |
| MAJOR    | 6     | Must fix (confuses/misleads reader) |
| MINOR    | 5     | Collect for human review (style/polish) |

**Verdict**: No fatal issues. Proceed to Revision R1.

---

## FATAL Issues (0)

None identified.

---

## MAJOR Issues (6)

### M1: Incorrect Standard Deviations (Accuracy Checker)
**Location**: Results Section, line 318  
**Issue**: Paper states "ResNet-18-BN: 1.2032 ± 0.0821, ResNet-18-LN: 0.9532 ± 0.0745"  
**Ground Truth**: h-m1/04_validation.md line 63 reports "BN: 1.2032 ± 0.0808, LN: 0.9532 ± 0.0579"  
**Error**: BN std dev off by 1.6% (0.0821 vs 0.0808), LN std dev off by 28.7% (0.0745 vs 0.0579)  
**Action**: Fix to correct values from h-m1/04_validation.md

### M2: Synthetic Data Not Flagged in Abstract (Skeptical Expert)
**Location**: Abstract  
**Issue**: Abstract claims "9.41pp gap" as fact without disclosing synthetic data limitation until Discussion Section 6  
**Impact**: Reader assumes real dataset validation; may feel misled when reaching Discussion  
**Action**: Add caveat to Abstract (e.g., "proof-of-concept on synthetic data; real validation pending")

### M3: Constant LR Limitation Not Disclosed in Abstract/Conclusion (Skeptical Expert)
**Location**: Abstract line 3, Conclusion line 457  
**Issue**: Both claim "no hyperparameter tuning" without disclosing that constant LR (0.01) is non-standard and may inflate effect  
**Impact**: Reader may assume result generalizes to standard training schedules (warmup, cosine decay)  
**Action**: Add "under constant learning rate" qualifier to Abstract and Conclusion claims

### M4: Group DRO Comparison Mixes Loss Functions (Skeptical Expert)
**Location**: Discussion line 394  
**Issue**: Paper compares LN+ERM to BN+ERM, but positions against BN+GroupDRO (Sagawa 2020) which uses modified loss  
**Impact**: Claim "architectural choice alone vs algorithmic intervention" is misleading (apples-to-oranges)  
**Action**: Clarify that Group DRO uses BN+different-loss, not LN+same-loss; frame as complementary, not competitive

### M5: Abstract Too Long (Bored Reviewer)
**Location**: Abstract  
**Issue**: 250+ words vs ICML 150-word guideline  
**Impact**: Reviewer may skim past key claims; violates venue formatting  
**Action**: Cut to 150 words (remove "More broadly..." sentence, condense mechanism explanation)

### M6: Hook Buried (Bored Reviewer)
**Location**: Abstract first sentence  
**Issue**: Leads with "preferentially learn shortcuts" (vague) instead of "9.41pp gap caused by BN" (quantitative hook)  
**Impact**: Reader doesn't immediately grasp impact; may close PDF after 30 seconds  
**Action**: Lead with gap size: "Batch Normalization amplifies worst-group gaps by 9.41pp vs Layer Normalization..."

---

## MINOR Issues (5) — Deferred to Human Review

### m1: Inconsistent Rounding (Accuracy Checker)
**Location**: Abstract, Introduction, Results (9 occurrences)  
**Issue**: Gradient asymmetry reported as "26%" in Abstract, "26.23%" in Introduction line 18 and Results  
**Impact**: Minor confusion (both technically correct)  
**Recommendation**: Standardize to "26%" throughout (rounded) or "26.23%" (precise), not mixed

### m2: Jargon Before Definition (Bored Reviewer)
**Location**: Abstract  
**Issue**: "spurious correlations" used in sentence 1 without definition  
**Impact**: Non-fairness reviewers may need to Google term  
**Recommendation**: Define inline or rephrase ("statistical shortcuts that fail on minority groups")

### m3: Overwrought First Sentence (Bored Reviewer)
**Location**: Introduction line 1  
**Issue**: "not due to insufficient data, but because of an architectural choice made decades ago" feels dramatic  
**Impact**: Slightly undermines scientific tone  
**Recommendation**: Simplify to "A model achieving 97% average accuracy can fail on 28% of minority groups due to an architectural design choice"

### m4: Organization Paragraph Adds Zero Information (Bored Reviewer)
**Location**: Introduction end  
**Issue**: "Organization. Section 2 discusses..." (60 words)  
**Impact**: Standard boilerplate, wastes space  
**Recommendation**: Cut (readers can see section headings)

### m5: Related Work Citation Gap (Skeptical Expert)
**Location**: Related Work Section 2  
**Issue**: Cites Shen2021 but doesn't cite BatchNorm alternatives surveys (e.g., Brock2021)  
**Impact**: Completeness (not critical)  
**Recommendation**: Add 1-2 normalization survey citations

---

## Verified Correct Claims (Sample)

- ✓ Gap difference "9.41 pp" matches h-e1/04_validation.md line 98
- ✓ p-value "5.43e-05" matches h-e1/04_validation.md line 104
- ✓ Cohen's d "3.94" (RQ1), "4.32" (RQ2) match validation reports
- ✓ Seeds "10/10" reaching 90% matches h-e1/04_validation.md lines 95-96
- ✓ Spearman ρ "1.0000" matches h-c1/04_validation.md line 54
- ✓ Gradient ratio means "1.2032" (BN), "0.9532" (LN) match h-m1/04_validation.md line 63
- ✓ All 16 occurrences of "9.41pp" numerically consistent across sections

---

## Recommendations for Revision R1

**Fix ALL MAJOR issues** (M1-M6):
1. Correct gradient ratio std devs (M1)
2. Flag synthetic data limitation in Abstract (M2)
3. Add "constant LR" qualifier to Abstract/Conclusion (M3)
4. Clarify Group DRO comparison framing (M4)
5. Cut Abstract to 150 words (M5)
6. Lead Abstract with quantitative hook (M6)

**Defer MINOR issues** (m1-m5) to 065_human_review_notes.md:
- Standardize gradient asymmetry rounding
- Define "spurious correlations" in Abstract
- Simplify Introduction first sentence
- Cut organization paragraph
- Add normalization survey citations

**Persuasiveness Check**: After R1 fixes, re-assess Abstract engagement (should pass 2-minute test with shortened hook-first version).

---

**Round 1 Complete**: 2026-08-25T01:11:10Z
