# Phase 6.5 Round 1: MINOR Issues Deferred for Human Review
# Date: 2026-07-10
# Paper: 06_paper_r1.md (after R1 revision)

---

## Overview

**Total MINOR Issues**: 6  
**Source**: Round 1 Three-Persona Adversarial Review  
**Status**: Deferred (not fixed in R1 automated revision)  
**Reason**: MINOR issues require human judgment or are cosmetic/low-priority

These issues do NOT block convergence (FATAL=0, MAJOR=0 is sufficient). However, they may improve paper quality if addressed in final polishing.

---

## MINOR-1: Percentage Deviation Arithmetic

**Source**: Accuracy Checker  
**Location**: §4.2 Table 1  
**Severity**: MINOR — Rounding differences (<0.5 percentage points), not material

### Issue

Paper reports deviation percentages with inconsistent rounding:
- **Published**: "Deviation: −95.8% (factual), −98.5% (creative)"
- **Calculated**:
  - Factual: (0.0354 - 0.75) / 0.75 = **-95.28%** (paper says -95.8%, difference 0.52pp)
  - Creative: (0.0103 - 0.75) / 0.75 = **-98.63%** (paper says -98.5%, difference 0.13pp)

### Recommended Fix

**Option 1 (Conservative)**: Round to 1 decimal place consistently:
- Factual: -95.3%
- Creative: -98.6%

**Option 2 (Precise)**: Report to 2 decimal places:
- Factual: -95.28%
- Creative: -98.63%

**Option 3 (Keep as-is)**: Differences are <1 percentage point; not material to findings.

### Human Decision Required

Which rounding convention to use? Option 1 (1 decimal) is most common in academic papers.

**Status in R1**: PARTIALLY FIXED as part of MAJOR-1 (updated to -95.3% and -98.6% in Table 1)

---

## MINOR-2: Gate Criteria Count Inconsistency

**Source**: Accuracy Checker  
**Location**: §3.5, §4.3 Table 2  
**Severity**: MINOR — Does not affect conclusion (gate failed regardless), but confusing

### Issue

**§3.5 (Methodology)** lists **5 gate criteria**:
1. Primary: Δρ_j > 0.15
2. Direction: ρ_creative > ρ_factual
3. Autocorr: Lag-1 > 0.4 (creative), < 0.2 (factual)
4. Reliability: Krippendorff's α > 0.7
5. Significance: p < 0.05, Cohen's d > 0.5

**§4.3 Table 2** lists **7 criteria** (adds significance + effect size as separate rows):
1. Δρ_j > 0.15
2. Direction
3. Autocorr (creative)
4. Autocorr (factual)
5. Krippendorff's α
6. Statistical significance (p < 0.05)
7. Effect size (d > 0.5)

**Gate status**: "FAILED (1/7 criteria met)" in §4.3, but denominator unclear from §3.5.

### Recommended Fix

**Option 1**: Update §3.5 to list 7 criteria explicitly (expand #5 into #5 significance + #6 effect size + #7 power).

**Option 2**: Simplify Table 2 to 5 rows (merge significance + effect size into one "Statistical Tests" row).

**Option 3**: Add clarifying note in §4.3:
> "Gate evaluation expands the 5 methodology criteria into 7 rows for granular tracking (autocorrelation split by domain; statistical tests split by p-value and effect size)."

### Human Decision Required

Which structure is clearer? Option 1 (expand §3.5) ensures consistency. Option 3 (add note) is faster.

**Status in R1**: NOT FIXED (requires human decision on canonical criteria count)

---

## MINOR-3: Conclusion Repeats Introduction (Lazy Writing)

**Source**: Bored Reviewer  
**Location**: §7 Conclusion, Paragraph 1  
**Severity**: MINOR — Annoying but not a blocker

### Issue

Conclusion uses formulaic "We began by asking... We end with..." structure:

**§7 Paragraph 1**:
> "We began by asking whether CCP-based hallucination detection degrades when applied to creative text due to implicit factual-ontology assumptions. We end with a methodological requirement: **validate your measurement before testing your hypothesis**."

**§1 Introduction** has similar backward-looking → forward-looking arc. Feels repetitive.

### Recommended Fix

**Option 1 (Forward-Looking)**: Start conclusion with impact, not recap:
> "Transparent failures accelerate progress. Our replication attempt of CCP exposed a field-wide reproducibility gap: hallucination detection papers optimize for novelty (+0.05 ROC-AUC improvements) over implementation transparency. We propose a shift..."

**Option 2 (Actionable)**: Start with the lesson learned:
> "**Measurement validity precedes hypothesis testing.** When a metric produces values 20-80× outside the inferred range, you cannot distinguish 'hypothesis wrong' from 'measurement broken.' This principle, illustrated by our CCP replication failure, generalizes..."

**Option 3 (Keep as-is)**: Formulaic but clear. Not worth rewriting.

### Human Decision Required

Does the current conclusion structure bother you? If yes, choose Option 1 or 2. If no, keep as-is.

**Status in R1**: NOT FIXED (stylistic preference, low priority)

---

## MINOR-4: Too Many Tables in Section 4 (Reader Fatigue)

**Source**: Bored Reviewer  
**Location**: §4 (Experiments and Results)  
**Severity**: MINOR — Tables are necessary, but presentation could improve

### Issue

**Section 4 contains 4 tables**:
- **Table 1**: Claim-Type Mass Ratio by Domain (§4.2)
- **Table 2**: Gate Criteria vs Observed (§4.3)
- **Table 3**: Mean NLI Class Probabilities by Domain (§4.4)
- **Table 4**: Autocorrelation by Lag (§4.5)

Bored Reviewer: "Four tables in one section. Reviewer's eyes glaze over."

### Recommended Fix

**Option 1 (Merge Tables 1 + 3)**: Both show ρ_j and NLI distributions. Combine into single "Primary Metrics by Domain" table:

| Domain | Median ρ_j | P(entail) | P(neutral) | P(contradict) | N |
|--------|-----------|-----------|------------|--------------|---|
| Factual | 0.0354 | 0.045 | 0.910 | 0.045 | 792 |
| Creative | 0.0103 | 0.017 | 0.967 | 0.016 | 817 |

**Option 2 (Move Table 4 to Appendix)**: Autocorrelation analysis is secondary (hypothesis failed). Move lag-1 through lag-10 breakdown to appendix; keep lag-1 in main text.

**Option 3 (Keep as-is)**: Tables are necessary for transparency. Reader fatigue is subjective.

### Human Decision Required

Does 4 tables in Section 4 feel excessive? If yes, choose Option 1 (merge) or Option 2 (move to appendix). If no, keep as-is.

**Status in R1**: NOT FIXED (presentation preference, low priority)

---

## MINOR-5: Sanity Check Not Cited

**Source**: Skeptical Expert  
**Location**: §4.4 (NLI Distribution Analysis)  
**Severity**: MINOR — Doesn't affect findings, but harms reproducibility

### Issue

**§4.4** mentions sanity check:
> "We tested the NLI model on 20 manually selected TruthfulQA correct/incorrect answer pairs..."

But **no citation** to code or data. Readers cannot verify which 20 examples were used.

### Recommended Fix

Add footnote:
> "We tested the NLI model on 20 manually selected TruthfulQA correct/incorrect answer pairs^‡^..."
>
> ^‡^See `h-e1/code/sanity_checks.ipynb` for manual examples and results.

### Human Decision Required

Does the code file `h-e1/code/sanity_checks.ipynb` exist? If yes, add footnote. If no, create it or remove specificity ("20 manually selected examples").

**Status in R1**: NOT FIXED (requires verification of code file existence)

---

## MINOR-6: p-value Formatting Inconsistency

**Source**: Skeptical Expert  
**Location**: Throughout paper (§4.2, §4.3, tables)  
**Severity**: MINOR — Cosmetic

### Issue

p-values reported with inconsistent precision:
- **Sometimes**: "p = 1.0000" (4 decimal places)
- **Sometimes**: "p = 1.0" (1 decimal place)

### Recommended Fix

**Option 1 (Standard)**: Standardize to 4 decimal places: "p = 1.0000"

**Option 2 (Significant Digits)**: Use 3 decimal places unless p < 0.001:
- p = 1.000
- p < 0.001

**Option 3 (Keep as-is)**: Inconsistency is minor; not worth global search-replace.

### Human Decision Required

Which convention to use? Most statistics journals prefer 3-4 decimal places (Option 1 or 2).

**Status in R1**: NOT FIXED (cosmetic, low priority)

---

## Summary Table

| Issue | Severity | Fix Effort | Impact on Quality | Recommended Action |
|-------|----------|-----------|-------------------|-------------------|
| MINOR-1: Percentage rounding | MINOR | 5 min | Low | ✅ DONE in R1 (part of MAJOR-1) |
| MINOR-2: Gate criteria count | MINOR | 15 min | Medium (clarity) | ⚠️ Human decision: 5 vs 7 criteria |
| MINOR-3: Conclusion formula | MINOR | 30 min | Low (style) | ⏸️ Optional polish |
| MINOR-4: Too many tables | MINOR | 1 hour | Low (presentation) | ⏸️ Optional redesign |
| MINOR-5: Sanity check citation | MINOR | 5 min | Medium (reproducibility) | ⚠️ Check if file exists |
| MINOR-6: p-value formatting | MINOR | 10 min | Low (cosmetic) | ⏸️ Optional polish |

**Priority Ranking**:
1. **MINOR-2** (gate criteria) — Medium clarity impact, requires human decision
2. **MINOR-5** (sanity check citation) — Medium reproducibility impact, quick fix IF file exists
3. **MINOR-1** (percentage rounding) — ✅ Already fixed in R1
4. **MINOR-6** (p-value format) — Low cosmetic impact, optional
5. **MINOR-3** (conclusion structure) — Low stylistic impact, optional
6. **MINOR-4** (table count) — Low presentation impact, optional

---

## Recommended Human Workflow

### Phase 1: Quick Wins (15 minutes)
1. ✅ **MINOR-1**: Already fixed in R1 (check changelog)
2. **MINOR-5**: Check if `h-e1/code/sanity_checks.ipynb` exists
   - If yes → Add footnote in §4.4
   - If no → Remove specificity or create file
3. **MINOR-6**: Search-replace "p = 1.0" → "p = 1.0000" (4 instances)

### Phase 2: Clarity Improvements (30 minutes)
4. **MINOR-2**: Decide canonical gate criteria count
   - Option A: Expand §3.5 to 7 criteria (matches Table 2)
   - Option B: Add clarifying note in §4.3

### Phase 3: Optional Polish (1 hour+)
5. **MINOR-3**: Rewrite conclusion opening (forward-looking instead of backward-looking)
6. **MINOR-4**: Merge Table 1 + Table 3 OR move Table 4 to appendix

---

## Sign-Off

**Human Reviewer**: Please review MINOR issues and decide:
1. Which fixes to apply (recommended: MINOR-2, MINOR-5, MINOR-6)
2. Which to defer (MINOR-3, MINOR-4 are low-priority style/presentation)

**Next Step**: After human decisions, update `06_paper_r1.md` and re-run Round 2 review to verify convergence.

**Date**: 2026-07-10  
**Status**: Awaiting human review
