# Phase 6.5 Adversarial Review — Changelog
# Paper: "Capability or Verbosity? Disentangling the Drivers of Length-Debiased Preference in LLM Evaluation"
# Started: 2026-08-04
# Mode: UNATTENDED

---

## Round 1 Changes (Step 03 — Revision R1)

**Source paper**: `06_paper.md`  
**Output paper**: `06_paper_r1.md`  
**Issues addressed**: 3 MAJOR / 0 FATAL

---

### CHANGE R1-001 — Remove Singhal 2023 Unverified Citation

**Issue**: AC-002 (MAJOR)  
**Type**: Reference deletion  
**Location**: References section  
**Original**: `Singhal, P., et al. (2023). How LLMs Interact with Length Bias in RLHF. *arXiv preprint*. [UNVERIFIED — verify before submission]`  
**Revised**: Reference removed entirely  
**Rationale**: Unverified citations risk desk rejection. No in-text citation found for Singhal 2023 that requires keeping it; the line in Section 6.4 about "evaluation reliability" does not directly cite Singhal.  
**Word count delta**: -1 line  

---

### CHANGE R1-002 — FWL Spearman Qualification in Section 3.4

**Issue**: SE-001 (MAJOR)  
**Type**: Methodological clarification  
**Location**: Section 3.4 (now titled "FWL-Inspired Robustness Verification")  
**Original**: "Delta = |ρ_Pingouin − ρ_resid| < 0.02 confirms FWL consistency."  
**Revised**: Added note: "The Frisch-Waugh-Lovell theorem guarantees exact algebraic equality between partial OLS coefficients and residualized OLS estimates (Pearson). For Spearman partial correlation, residualized ranks provide an independent estimator that approximates this principle; convergence within 1.1pp is empirical evidence of robustness, not a theorem guarantee."  
**Rationale**: Sophisticated reviewers know FWL applies to Pearson/OLS only. Without this note, paper's "FWL verification" claim is technically incorrect for Spearman.  
**Word count delta**: +47 words  

---

### CHANGE R1-003 — FWL Qualification in Section 5.3 and RQ3

**Issue**: SE-001 (MAJOR)  
**Type**: Methodological clarification  
**Location**: Section 5.3 heading and text; Section 4 RQ3 description  
**Original heading**: "RQ3: FWL Robustness (H-M2)"  
**Revised heading**: "RQ3: Estimator Robustness via FWL-Inspired Residualization (H-M2)"  
**Original text**: "Two independent estimators converge within 1.1pp (Figure 9), ruling out methodological artifact."  
**Revised text**: Added qualification about Pearson/Spearman distinction while maintaining conclusion that 1.1pp gap rules out artifact.  
**Word count delta**: +30 words  

---

### CHANGE R1-004 — Update Citation Statistics

**Issue**: AC-002, AC-003 (MAJOR follow-on)  
**Type**: Metadata update  
**Location**: Paper Statistics YAML block  
**Original**: total: 10, verified: 7, unverified: 3, verification_rate: 70%  
**Revised**: total: 9, verified: 8, unverified: 1, verification_rate: 89%  
**Rationale**: Singhal removed (-1); Ji 2023 accepted with verification note (+1 to verified tentatively)  

---

## Round 1 MINOR Issues — NOT Fixed (Human Review Only)

See `065_human_review_notes.md` for full list.

| ID | Issue | Deferred to Human |
|----|-------|-------------------|
| AC-001 | Add "bootstrap" qualifier to CI mentions in prose | ✓ |
| AC-004 | "~5×" vs 4.88 precision in abstract | ✓ |
| AC-005 | "~4.9" vs "~5" inconsistency | ✓ |
| BR-001 | Experiments section partially redundant | ✓ |
| BR-002 | Clarify bivariate 0.966 vs Dubois' 0.94 | ✓ |
| SE-002 | VIF interpretation note for Spearman | ✓ |
| SE-003 | Distinguish our bivariate (0.966) from Dubois' (0.94) | ✓ |
| SE-004 | Cite ε² formula for KW | ✓ |
| SE-005 | H-M3 summary table note | ✓ |

---

## Sections Modified (R1)

| Section | Modification |
|---------|-------------|
| 3.4 | Heading + FWL Pearson/Spearman qualification added |
| 4 | RQ3 description updated |
| 5.3 | Heading + FWL qualification added |
| References | Singhal 2023 removed |
| Paper Statistics | Citation counts updated |

---

## Round 2 Changes (Step 06 — Revision R2)

**Source paper**: `06_paper_r1.md`  
**Output paper**: `06_paper_r2.md`  
**Issues addressed**: 1 MAJOR / 0 FATAL

---

### CHANGE R2-001 — Add One-Tailed Qualifier to H-E1 p-value

**Issue**: AC2-001 (MAJOR)  
**Type**: Methodological transparency  
**Location**: Abstract, Introduction (Contribution 1), Section 3.2, Section 5.1 (result box and table), Section 5.3 table  
**Issue**: p = 1.69e-170 is a one-tailed p-value (Pingouin alternative='greater', pre-registered directional hypothesis). Paper did not declare this. H-M2 re-run with default two-tailed produced p = 3.38e-170 (factor of 2), which a reviewer would flag.  
**Fix applied**:  
- Abstract: "p = 1.69e-170, one-tailed"  
- Contribution #1: "p = 1.69e-170 one-tailed, pre-registered directional test"  
- Section 3.2: added `alternative='greater'` to implementation description  
- Section 5.1 box: "(one-tailed)" added  
- Section 5.1 table: "(one-tailed)" added  
- Section 5.3 FWL table: "(one-tailed)" added  
**Word count delta**: ~+15 words  

---

## Round 2 MINOR Issues — NOT Fixed (Human Review Only)

(Added to 065_human_review_notes.md)

| ID | Issue | Deferred to Human |
|----|-------|-------------------|
| AC2-002 | ρ(win_rate, avg_length) ≈ 0.63 inferred from R²=0.433, not directly measured | ✓ |
| AC2-003 | ε²=0.883 rounding non-issue | ✓ |
| SE2-002 | ε² "variance explained" shorthand | ✓ |

---

## Sections Modified (R2)

| Section | Modification |
|---------|-------------|
| Abstract | "(one-tailed)" added to p-value |
| 1 (Intro, Contribution 1) | "(one-tailed, pre-registered)" added |
| 3.2 | `alternative='greater'` added to implementation |
| 5.1 | "(one-tailed)" added to box and table |
| 5.3 | "(one-tailed)" added to FWL table |

---

## Final Summary

**Total Revisions Made**: 9 (4 from R1 + 5 from R2)  
**Sections Modified**: 3.2, 3.4, 4, 5.1, 5.3, References, Paper Statistics (+ Abstract, Intro, Contributions)  
**Word Count Change**: original (~3805) → final (~3860, +55 words)

**Review Process**:
- Started: 2026-08-04
- Completed: 2026-08-04
- Rounds: 2 (R1 + R2)
- Personas Used: accuracy_checker (R1+R2), bored_reviewer (R1), skeptical_expert (R1+R2)

**Files Generated**:
- 06_paper_r1.md (after R1 revision)
- 06_paper_r2.md (after R2 revision → becomes final)
- 065_review_r1.md (R1 adversary report)
- 065_review_r2.md (R2 adversary report)
- 065_review_summary.md (consolidated summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
