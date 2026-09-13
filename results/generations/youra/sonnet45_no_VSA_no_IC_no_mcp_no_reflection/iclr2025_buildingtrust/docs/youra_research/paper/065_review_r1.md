# Adversarial Review Round 1
**Date:** 2026-08-28  
**Round:** 1  
**Reviewers:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## PERSONA 1: Accuracy Checker
**Role:** Verify quantitative claims against ground truth

### Findings

#### FATAL-A1: Incorrect stratified correlation value
**Location:** paper/sections/05_results.md line 34 (Small stratum table)  
**Claim:** "Small (<1B) | 6 | r=0.994, p=2.6e-05"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "small_stratum: TrustfulQA_AdvBench: {r: 0.994, p: '2.64e-05'}"  
**Issue:** p-value formatting inconsistency — paper shows "2.6e-05" but ground truth specifies "2.64e-05"  
**Severity:** FATAL (numerical precision error)  
**Fix:** Change "p=2.6e-05" → "p=2.64e-05"

#### FATAL-A2: Incorrect p-value formatting in stratified table
**Location:** paper/sections/05_results.md line 35  
**Claim:** "r=0.989, p=8.1e-05"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '8.12e-05'"  
**Issue:** Missing last digit in p-value  
**Severity:** FATAL  
**Fix:** Change "p=8.1e-05" → "p=8.12e-05"

#### FATAL-A3: Incorrect p-value formatting (Medium stratum)
**Location:** paper/sections/05_results.md line 36  
**Claim:** "Medium (1-10B) | 9 | r=0.998, p=1.5e-09"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '1.47e-09'"  
**Issue:** Rounding error — "1.5e-09" instead of "1.47e-09"  
**Severity:** FATAL  
**Fix:** Change "p=1.5e-09" → "p=1.47e-09"

#### FATAL-A4: Incorrect p-value (Medium stratum, row 2)
**Location:** paper/sections/05_results.md line 36  
**Claim:** "r=0.995, p=1.3e-08"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '1.31e-08'"  
**Issue:** Missing precision digit  
**Severity:** FATAL  
**Fix:** Change "p=1.3e-08" → "p=1.31e-08"

#### FATAL-A5: Incorrect p-value (Medium stratum, row 3)
**Location:** paper/sections/05_results.md line 36  
**Claim:** "r=0.997, p=4.4e-09"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '4.37e-09'"  
**Issue:** Rounding error  
**Severity:** FATAL  
**Fix:** Change "p=4.4e-09" → "p=4.37e-09"

#### FATAL-A6: Incorrect p-value (Large stratum, row 1)
**Location:** paper/sections/05_results.md line 37  
**Claim:** "Large (>10B) | 5 | r=0.997, p=2.4e-04"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '2.39e-04'"  
**Issue:** Rounding error  
**Severity:** FATAL  
**Fix:** Change "p=2.4e-04" → "p=2.39e-04"

#### FATAL-A7: Incorrect p-value (Large stratum, row 2)
**Location:** paper/sections/05_results.md line 37  
**Claim:** "r=0.991, p=1.0e-03"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '1.01e-03'"  
**Issue:** Missing precision digit  
**Severity:** FATAL  
**Fix:** Change "p=1.0e-03" → "p=1.01e-03"

#### FATAL-A8: Incorrect p-value (Large stratum, row 3)
**Location:** paper/sections/05_results.md line 37  
**Claim:** "r=0.994, p=4.6e-04"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '4.58e-04'"  
**Issue:** Rounding error  
**Severity:** FATAL  
**Fix:** Change "p=4.6e-04" → "p=4.58e-04"

#### MAJOR-A9: Missing last digit in Small stratum row 3
**Location:** paper/sections/05_results.md line 34  
**Claim:** "r=0.986, p=1.5e-04"  
**Ground Truth:** 065_ground_truth.yaml Q3 → "p: '1.45e-04'"  
**Issue:** Truncation error  
**Severity:** MAJOR  
**Fix:** Change "p=1.5e-04" → "p=1.45e-04"

#### PASS-A10: Main correlation table accurate
**Location:** paper/sections/05_results.md lines 9-13 (main correlation table)  
**Verified:** All values match 065_ground_truth.yaml Q1  
- TrustfulQA ↔ AdvBench: r=0.998, p=1.11e-23 ✓  
- TrustfulQA ↔ BOLD: r=0.993, p=1.35e-17 ✓  
- AdvBench ↔ BOLD: r=0.996, p=9.96e-20 ✓

#### PASS-A11: Clustering metrics accurate
**Location:** paper/sections/05_results.md lines 44-49  
**Verified:** Matches 065_ground_truth.yaml Q4, Q5, Q6  
- Silhouette = 0.274 ✓  
- Bootstrap = 100.0% ✓  
- Cophenetic = 0.693 ✓

#### PASS-A12: Confidence adjustment accurate
**Location:** paper/sections/05_results.md lines 126-129  
**Verified:** Matches 065_ground_truth.yaml Q7  
- Revised confidence 0.85 → 0.40 ✓  
- P1: +0.40 ✓  
- P2: -0.45 ✓  
- P3: -0.40 ✓

---

## PERSONA 2: Bored Reviewer
**Role:** Check engagement — abstract compelling? novelty clear in 2 min?

### Findings

#### MAJOR-B1: Abstract buries lead
**Location:** paper/sections/00_abstract.md lines 1-3  
**Issue:** First sentence is 35 words describing the assumption before revealing the finding. Reader doesn't know "why care" until sentence 2.  
**Severity:** MAJOR (engagement)  
**Fix:** Open with finding: "Trustworthiness benchmarks (TrustfulQA, AdvBench, BOLD) correlate at r > 0.99 across 20 LLMs — near-perfect coupling that challenges the independent dimensions paradigm underlying multi-dimensional evaluation."  
**Current:** "Multi-dimensional trustworthiness evaluation treats reliability, robustness, and fairness as independent properties..."  
**Revised:** "Trustworthiness benchmarks exhibit near-perfect correlations (r > 0.99, p < 1e-17) across 20 LLMs, challenging the independent dimensions assumption..."

#### MAJOR-B2: Novelty claim unclear in first 2 minutes
**Location:** paper/sections/01_introduction.md lines 14-22 (contribution list)  
**Issue:** Contribution 1 starts "First large-scale empirical evidence..." — unclear what makes this "first" vs. prior HELM/BIG-bench work.  
**Severity:** MAJOR (novelty not established quickly)  
**Fix:** Add one sentence before contribution list: "Prior work (HELM, BIG-bench) aggregates scores without testing correlation structure — our analysis reveals near-redundancy invisible to aggregation-only approaches."

#### MINOR-B3: Competing explanations section too late
**Location:** paper/sections/05_results.md line 83 (Section 5.3)  
**Issue:** "Why r > 0.99?" is the most interesting question, but it appears in Results section 5.3 after clustering details. Reader may lose interest before reaching it.  
**Severity:** MINOR (structure)  
**Suggestion:** Move competing explanations teaser to Introduction (after line 10): "This coupling admits two explanations: unified construct (benchmarks measure the same thing) or insufficient resolution (3 benchmarks cannot distinguish dimensions). We test these via 10-benchmark future work."

#### PASS-B4: Introduction hook works
**Location:** paper/sections/01_introduction.md lines 1-6  
**Verified:** Opening sentence ("Models achieving 95%+ accuracy... can fail across multiple dimensions at r > 0.99") is concrete and surprising ✓

---

## PERSONA 3: Skeptical Expert
**Role:** Challenge novelty claims, baseline fairness, missing limitations

### Findings

#### MAJOR-S1: HELM baseline comparison missing quantitative claim
**Location:** paper/sections/02_related_work.md lines 27-31  
**Claim:** "HELM aggregates 50+ benchmarks... without testing whether failures correlate"  
**Issue:** Did you verify HELM paper doesn't report correlations? If HELM reports inter-benchmark correlations anywhere (appendix, supplementary), this claim is wrong.  
**Severity:** MAJOR (novelty claim at risk)  
**Fix Required:** Add footnote: "We searched HELM paper (Liang et al. 2022) and supplementary materials — no correlation analysis reported. HELM reports per-benchmark scores but not cross-benchmark correlation structure."

#### MAJOR-S2: Missing limitation — model family confound not controlled
**Location:** paper/sections/06_discussion.md lines 75-82 (Section 6.4 Confounds)  
**Claim:** "Model Family (Partially Controlled): Dataset includes 7+ model families..."  
**Issue:** "Partially controlled" is weasel language. You did NOT stratify by family — you just claim diversity. If GPT-4, Claude, LLaMA correlate because they all use RLHF, your r > 0.99 could be training method artifact, not fundamental property.  
**Severity:** MAJOR (validity threat)  
**Fix:** Add to Limitations section: "L6: Model Family Confound — UNCONTROLLED. Dataset includes 7+ families but no family-stratified analysis. If training methods (RLHF, DPO) create correlated failure patterns, r > 0.99 may reflect shared training paradigms rather than fundamental coupling."

#### MAJOR-S3: 3-benchmark design justified only in hindsight
**Location:** paper/sections/03_methodology.md lines 63-66  
**Claim:** "3-benchmark evaluation imposes clustering constraints... but provides sufficient power for correlation analysis"  
**Issue:** This is post-hoc rationalization. Your hypothesis predicted 2-5 clusters — you knew k≥3 requires n≥3. Why not start with 5 benchmarks?  
**Severity:** MAJOR (methodological honesty)  
**Fix:** Add honest admission: "In hindsight, 3-benchmark design was insufficient for taxonomy validation (k≥3 requires n≥3). We prioritized data availability (20 models × 3 benchmarks with public scores) over clustering robustness — a tradeoff that succeeded for correlation analysis but failed for taxonomy."

#### MINOR-S4: "First large-scale" claim overstated
**Location:** paper/sections/01_introduction.md line 16  
**Claim:** "First large-scale empirical evidence..."  
**Issue:** n=20 models × 3 benchmarks = 60 observations. Is this "large-scale"? HELM evaluates 50+ benchmarks × 30+ models.  
**Severity:** MINOR (claim inflation)  
**Fix:** Remove "large-scale" → "First empirical evidence..." OR qualify: "First cross-benchmark correlation analysis (20 models, 3 dimensions)..."

#### MINOR-S5: Dual-use section feels tacked on
**Location:** paper/sections/06_discussion.md lines 93-99 (Section 6.6 Broader Impact, Dual-Use)  
**Issue:** "understanding coupling structure could inform adversarial attacks" — this is generic boilerplate. If you can't name a concrete dual-use risk, delete it.  
**Severity:** MINOR (filler)  
**Suggestion:** Delete Dual-Use paragraph OR make concrete: "Adversaries could exploit coupling — if attacking TrustfulQA transfers to AdvBench at r=0.998, one adversarial training dataset could compromise multiple benchmarks simultaneously."

#### PASS-S6: Negative results honestly reported
**Location:** paper/sections/06_discussion.md lines 101-109 (Section 6.7)  
**Verified:** "What went wrong" section admits 3-benchmark design flaw and r > 0.99 unexpectedly strong ✓

#### PASS-S7: Future work falsifiable
**Location:** paper/sections/07_conclusion.md lines 487-496  
**Verified:** FW1 specifies exact predictions (r > 0.99 persists → H1, r < 0.7 → H2) ✓

---

## Summary

**FATAL Issues:** 8 (all p-value precision errors in stratified table)  
**MAJOR Issues:** 6 (abstract lead, novelty unclear, HELM verification, family confound, design justification, "large-scale" claim)  
**MINOR Issues:** 3 (competing explanations placement, dual-use filler, model count)

**Total Issues:** 17  
**Blocking Issues (FATAL + MAJOR):** 14

**Gate Decision:** REVISION REQUIRED — fix all FATAL issues (numerical accuracy), address all MAJOR issues (engagement, novelty, validity threats).

**Persuasiveness Check:**  
- Abstract compelling? ❌ (buries lead)  
- Novelty clear in 2 min? ⚠️ (HELM baseline unclear, "first" claim needs support)  
- Limitations honest? ✅ (negative results transparent, but missing family confound)

**Next Step:** Proceed to Step 03 (Revision R1)
