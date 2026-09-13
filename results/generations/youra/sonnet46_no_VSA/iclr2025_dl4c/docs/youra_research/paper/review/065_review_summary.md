# Adversarial Review Summary

**Paper**: What Does Code SFT Actually Teach? Source Identity Governs Benchmark Performance via Distributional Alignment  
**Review Completed**: 2026-08-03  
**Rounds Completed**: 2  
**Final Status**: CONVERGED  
**Persuasiveness Check**: PASSED  

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 2 | 2 | **0** |
| MAJOR | 3 | 3 | **0** |

**MINOR Issues**: 5 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Counterintuitive finding + specific numbers in first sentence |
| Problem clear by paragraph 2? | PASS | Clear "train on X → test on X" assumption stated and challenged |
| Novelty clear by page 1? | PASS | Four contributions listed explicitly |
| Figure 1 self-explanatory? | LIKELY PASS | Caption adequate; dual-encoder matrices are standard format |
| Hook avoids "X is important"? | PASS | Opens with concrete finding, not motivation statement |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (R1)

**Accuracy Checker Findings**:

| Category | Issues Found |
|----------|--------------|
| Wrong number in Introduction body | FATAL-001: 32.6% → correct is 35.0% |
| Inconsistent number in contribution bullet | FATAL-002: 35.9% → correct is 35.0% |
| Per-seed values wrong in Table 1 | MAJOR-001: LeetCode seeds 3.1/3.1/3.1 → actual 0/0/9.1% |
| Per-seed values swapped in Table 1 | MAJOR-002: Equal-mix seed 42/123 transposed |

**Bored Reviewer Findings**:

| Category | Issues Found |
|----------|--------------|
| Hook quality | PASS — strong counterintuitive hook |
| Engagement | Would continue reading; minor concern at Table 1 LeetCode row |
| Overclaim | MINOR: "substantially exceeds" claim lacks citation |

**Skeptical Expert Findings**:

| Category | Issues Found |
|----------|--------------|
| LeetCode training failure unaddressed | MAJOR-003: 0% on 2/3 seeds not explained as potential confound |
| Novelty | FAIR — clear differentiation from GRAPE |
| Baseline fairness | FAIR — within-model ablation |

**Key Issues Addressed in R1**:
1. FATAL-001: Corrected 32.6% → 35.0% throughout Introduction; corrected derived gap 29.6pp → 31.9pp throughout paper
2. FATAL-002: Corrected 35.9% → 35.0% in contributions bullet
3. MAJOR-001: Corrected LeetCode Table 1 per-seed values to 0.0%, 0.0%, 9.1%
4. MAJOR-002: Corrected Equal-mix Table 1 seed_42↔seed_123 swap
5. MAJOR-003: Added LeetCode training convergence limitation to Section 6.4

### Round 2: Numerical Verification (R2)

**Accuracy Checker + Serena/File Verification**:

All numerical claims cross-verified against raw result files:
- h-e2/results/all_results.csv: all condition means verified ✓
- h-m1/results/h_m1_result.json: MBPP+ cross-benchmark values verified ✓
- h-m2/results/rank_comparison_table.csv: Spearman ρ, p-value verified ✓
- h-e1/experiment_results.json: CodeBERT similarity matrix verified ✓
- h-c1/results/results.json: 7B scale results, η² values verified ✓

One notation inconsistency found and fixed:
- MINOR-R2-001 (treated as MAJOR for clarity): "0.055pp vs 0.319pp" → "5.5pp vs 31.9pp" in Section 5.4

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Frontmatter | Added review metadata |
| Abstract | "29.6pp" → "31.9pp" |
| Introduction | "32.6%" → "35.0%", gap "29.6pp" → "31.9pp", "35.9%" → "35.0%", "dwarfs" → "substantially exceeds", "29.6pp" → "31.9pp" in contribution bullet |
| Results (Table 1) | LeetCode per-seed corrected; Equal-mix per-seed seeds 42/123 swapped back |
| Results (Section 5.4 note) | "0.055pp vs 0.319pp" → "5.5pp vs 31.9pp" |
| Discussion (Section 6.4) | New limitation paragraph on LeetCode training convergence |
| Conclusion | "29.6pp" → "31.9pp" |

---

## Quality Improvements

- **Logical Consistency**: Improved — single coherent number (35.0%) for HE-only 1.3B mean throughout
- **Numerical Accuracy**: Improved — all 22 checked claims verified against raw data; 5 corrected
- **Novelty Claims**: Unchanged — claims were accurate
- **Baseline Comparison**: Unchanged — within-model ablation is fair by design
- **Persuasiveness**: Unchanged (already strong)
- **Hook Quality**: Unchanged (already strong)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **n=4 fragility**: Spearman p=0.042 is the minimum achievable with n=4 conditions — marginal significance.
   - *Prepared response*: Acknowledged in Section 6.4; dual-encoder concordance (MiniLM ρ=0.8) provides additional evidence beyond the marginal p-value.

2. **LeetCode near-zero performance**: May be training failure, not source identity.
   - *Prepared response*: Acknowledged in Section 6.4 (added in R1). Training convergence not separately verified; explicitly noted as limitation.

3. **MBPP+ evaluation incomplete**: Full 4-condition MBPP+ not available.
   - *Prepared response*: Acknowledged in Section 6.4. 24 checkpoints preserved for re-evaluation.

4. **"Substantially exceeds architectural improvements" claim**: Lacks citation.
   - *Prepared response*: This is a MINOR note; add citation to a code SFT survey or soften the language.

5. **Unverified citation**: Zhang 2026 (DomainPilot arXiv:2607.22769) not indexed in Semantic Scholar as of 2026-08-03.
   - *Prepared response*: Noted in paper as [UNVERIFIED]; re-verify after August 2026 indexing.
