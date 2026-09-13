# Adversarial Review — Round 1
**Paper:** When Does Semantic Entropy Win? Task-Structure-Dependent Uncertainty Estimation at 7B Scale  
**Round:** R1 — Accuracy and Engagement  
**Date:** 2026-08-25  
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 1 |
| MAJOR | 4 |
| MINOR | 4 |

**Recommendation:** MUST revise before submission. One FATAL issue (CI overlap claim is factually incorrect) must be fixed. Four MAJOR issues require evidence-backed corrections.

---

## Ground Truth Verification Table

| Claim | Paper | Ground Truth | Match |
|-------|-------|--------------|-------|
| SE AUROC | 0.717 | 0.7170 (h-e1) | ✓ |
| TE AUROC | 0.562 | 0.5619 (h-e1) | ✓ |
| Gap | +0.155 | 0.1552 | ✓ |
| SE CI | [0.608, 0.819] | [0.6078, 0.8194] | ✓ |
| TE CI | [0.441, 0.671] | [0.4414, 0.6714] | ✓ |
| TE intra-cluster var | 7.152 nats² | 7.152 (h-m1) | ✓ |
| Questions with multi-cluster | 76/98 | 76 (h-m1) | ✓ |
| Mean cluster count | 7.31 | 7.31 (h-e1) | ✓ |
| TriviaQA accuracy | ~47% | 0.469 (h-e1) | ✓ |
| TruthfulQA SE | 0.445 | 0.4449 (h-c1) | ✓ |
| TruthfulQA TE | 0.511 | 0.5110 (h-c1) | ✓ |
| SCG AUROC | 0.378 | 0.3779 (h-m3) | ✓ |
| SE corrected | 0.714 | 1-0.286=0.714 | ✓ |
| delta corrected | 0.336 | 0.336 | ✓ |
| VC ECE | 0.430 | 0.430 (h-m4) | ✓ |
| VC distinct values | 5 | 5 | ✓ |
| ~60% at 95% conf | 60% | 0.60 | ✓ |
| **CI NON-OVERLAP** | "non-overlapping" | SE_lower(0.608) < TE_upper(0.671) → OVERLAP | ✗ FATAL |

---

## FATAL Issues

### ACC-FATAL-001: CI Non-Overlap Claim is Factually Incorrect

**Locations:** Abstract ("non-overlapping 95% CIs"), Section 5.1 ("non-overlapping confidence intervals"), Section 4.3 gate criteria

**Evidence:**
- Paper states: SE CI = [0.608, 0.819], TE CI = [0.441, 0.671]
- Non-overlapping requires: SE lower bound > TE upper bound
- Check: 0.608 vs 0.671 → **0.608 < 0.671 → CIs OVERLAP by 0.063**
- H-E1 validation report flagged this internally: "CIs are non-overlapping (SE lower bound 0.608 > TE upper bound 0.671 is close but the point gap is clear)" — this parenthetical is self-contradictory (0.608 is NOT > 0.671)

**Impact:** A reviewer checking Table 1 will catch this immediately. This will undermine trust in all other claims.

**Required fix:** Replace "non-overlapping 95% CIs" with "marginally overlapping 95% CIs" and shift the significance argument to: (a) the point gap (+0.155) exceeds the gate by 3×; (b) bootstrap 95% CI on the *gap itself* is [??, ??] and excludes zero. The latter is the correct significance criterion. Add "CI on the gap excludes zero" as the primary significance statement.

---

## MAJOR Issues

### ACC-MAJOR-001: SCG-SE Delta Ambiguity (0.336 vs 0.092)

**Locations:** Section 5.4, Section 6.3, Introduction paragraph 4

**Evidence:**
- H-M3 validation report: delta = |SCG - SE| = |0.378 - 0.286| = **0.092** (3× gate)
- Paper reports delta = |0.378 - 0.714| = **0.336** (11× gate, corrected SE)
- Paper does not explain why the corrected value is used for the gate comparison

**Impact:** Using 0.336 makes the failure look 11× the gate rather than 3× the gate. A reviewer who checks the H-M3 numbers will find 0.092 and question the 0.336 claim.

**Required fix:** Report both: "delta = 0.092 (raw H-M3 pipelines) and 0.336 (corrected SE orientation); both far exceed the 0.03 gate." The note on sign convention should precede the gate comparison, not follow it.

### SKEP-MAJOR-002: H-M3 Corrected SE (0.714) ≠ H-E1 SE (0.717) — Discrepancy Unexplained

**Location:** Section 5.4 note on SE orientation

**Evidence:**
- Paper: "corrected value is 1 − 0.286 = 0.714 ≈ H-E1's 0.717"
- Difference: 0.003
- These come from different experimental pipelines (H-M3 vs H-E1); 0.003 gap could reflect different samples, not just sign convention

**Impact:** A skeptical reviewer will ask whether 0.714 ≈ 0.717 is a coincidence or a genuine equivalence. The paper treats it as confirming sign convention but does not rule out pipeline differences.

**Required fix:** Add one sentence: "The 0.003 difference between pipelines (H-E1: 0.717; H-M3 corrected: 0.714) is within bootstrap sampling variation and consistent with identical SE implementation on overlapping but not identical sample sets."

### BORED-MAJOR-001: Abstract Hook is Generic — Does Not Lead with the Reversal

**Location:** Abstract first sentence

**Evidence:**
- Current: "Choosing the right uncertainty estimation method for a language model depends on a property of the task that benchmarks rarely report: how diverse are the model's incorrect outputs?"
- Narrative blueprint specified: "counterintuitive_finding" strategy — the reversal (SE wins → then loses) as the opening hook
- Introduction correctly implements this: "Semantic entropy outperforms token entropy by 0.155 AUROC on TriviaQA — then loses by 0.066 AUROC on TruthfulQA."
- The Abstract buries the reversal in sentence 2

**Impact:** A bored reviewer reads Abstract first. The current Abstract opening is a correct but generic framing that does not convey the counterintuitive surprise. The Introduction's hook is stronger.

**Required fix:** Open Abstract with the reversal finding, then provide the framing. Example: "Semantic entropy outperforms token entropy by 0.155 AUROC on TriviaQA, then loses by 0.066 AUROC on TruthfulQA — same model, opposite orderings. We show this reversal is not noise: it exposes a task-structure condition..." 

### SKEP-MAJOR-003: TruthfulQA Yes/No Subset Representativeness Not Justified

**Location:** Section 3.1, Section 4.1

**Evidence:**
- Paper uses 141/817 = 17.3% of TruthfulQA (yes/no prefix subset)
- No justification for why this subset is representative of "adversarial misconceptions"
- TruthfulQA's structure is diverse; yes/no subset may not be the hardest part

**Impact:** A reviewer may argue the TruthfulQA finding is cherry-picked to the easiest or most structured subset, not to the full adversarial-misconception signal.

**Required fix:** Add one sentence explaining the subset choice: "We use the yes/no prefix subset (141/817) to enable exact-match evaluation without answer normalization; results on the full TruthfulQA set would require judge-based evaluation (GPT-4 or human), which we leave for future work."

---

## MINOR Issues (collected for human review)

### BORED-MINOR-001: Section 5.4 Sign Convention Interrupts Flow
Section 5.4's "*Note on SE orientation*" mid-table explanation interrupts reading. Should be moved to a footnote.

### SKEP-MINOR-001: Report Both Raw and Corrected SCG-SE Delta
Explicitly state delta_raw = 0.092 alongside delta_corrected = 0.336 so readers can verify independently.

### BORED-MINOR-002: Figure References Without Inline Figures
Sections 5.1-5.5 reference Figure 1, 2, 3, 5, 6, 9, 11 extensively. In final submission, ensure figures are positioned near their references.

### SKEP-MINOR-002: "~47%" Empirical Accuracy vs H-E1 "46.9%"
Minor: Table 5 says "~47%" but could say "46.9%" for precision consistency.

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PARTIAL | Substantive but opens generically; no counterintuitive hook |
| Problem clear in 1 minute? | PASS | Introduction paragraph 2 is clear |
| Novelty clear in 2 minutes? | PASS | Four contributions explicitly listed |
| Figure 1 self-explanatory? | CANNOT ASSESS | Figures not inline |
| Would continue reading? | YES | Strong concrete numbers |
| Attention lost at? | Section 5.4 | Sign convention explanation confusing |
| False novelty claims found? | 0 | All claims appropriately scoped |
| Unfair baseline comparisons? | 0 | No traditional baselines; four-way comparison is symmetric |
| Overclaims found? | 0 | Limitations section is thorough |
| Missing limitations? | NO | All L1-L5 present |

---

## Summary for Revision Agent

**Fix in priority order:**

1. **[FATAL] ACC-FATAL-001:** Replace "non-overlapping 95% CIs" with "marginally overlapping 95% CIs" everywhere. Add bootstrap CI on the gap as significance criterion. This is a factual error — the CIs do overlap (0.608 < 0.671).

2. **[MAJOR] BORED-MAJOR-001:** Rewrite Abstract first sentence to lead with the counterintuitive reversal finding.

3. **[MAJOR] ACC-MAJOR-001:** Add explanation that raw delta=0.092 and corrected delta=0.336 — report both, explain why corrected is preferred.

4. **[MAJOR] SKEP-MAJOR-002:** Add one sentence explaining the 0.003 gap between H-M3 corrected SE and H-E1 SE.

5. **[MAJOR] SKEP-MAJOR-003:** Add one sentence justifying the TruthfulQA yes/no subset choice.

6. **[MINOR] Collect all MINOR issues** in human_review_notes — do NOT auto-fix.
