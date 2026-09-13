# Adversarial Review Summary

**Paper:** When Consistency Is Not Uncertainty: Sampling-Based Hallucination Detection Fails Under Systematic Confabulation in Instruction-Tuned LLMs
**Review Completed:** 2026-08-31T07:45:00+00:00
**Rounds Completed:** 2 (R1 + R2)
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | — | 0 |
| MAJOR | 3 | 3 | 0 |

**MINOR Issues:** 9 items collected in `065_human_review_notes.md` (NOT auto-fixed)

All quantitative claims verified against `h-e1/04_validation.md` and `paper/065_ground_truth.yaml` with **0 discrepancies found**.

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Leads with concrete setup and specific AUROC number |
| Problem clear by paragraph 2? | PASS | Opening paragraph hook (perfect detector / AUROC=0.49) is excellent |
| Novelty clear by page 1? | PASS (after R1 fix) | [CITATION NEEDED] placeholder removed; claims hedged appropriately |
| Figure 1 self-explanatory? | PASS (after R1 fix) | Figure numbering conflict resolved; Figure 1 = AUROC bar chart |
| Hook avoids "X is important"? | PASS | Hook is specific and counterintuitive, not generic importance claim |
| Would continue reading? | YES | |
| Attention lost at? | Nowhere (after R1 fix) | Section 4 redundancy with Section 3 resolved |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings:**
| Category | Issues Found | Resolved |
|----------|--------------|----------|
| Figure numbering conflict | 1 MAJOR | ✅ Fixed |
| Novelty overclaim / placeholder | 1 MAJOR | ✅ Fixed |
| Temperature citation concern | 1 MINOR | Human review |

**Bored Reviewer Findings:**
| Category | Issues Found | Resolved |
|----------|--------------|----------|
| Section 4 redundancy | 1 MAJOR | ✅ Fixed |
| Abstract length | 1 MINOR | Human review |
| "Confidently consistent" term | 1 MINOR | Human review |
| Discussion organization | 1 MINOR | Human review |

**Skeptical Expert Findings:**
| Category | Issues Found | Resolved |
|----------|--------------|----------|
| "Systematic confabulation" term attribution | 1 MINOR | Human review |
| Missing bootstrap CIs | 1 MINOR | Human review |
| N=10 sensitivity analysis | 1 MINOR | Human review |

**Key Issues Addressed in R1:**
1. **MAJOR-AC-001** (Figure numbering): Two figures both labeled "Figure 1." Fixed by reassigning `smc_nli_distribution.png` to Figure 3 in Section 3, keeping `auroc_comparison.png` as Figure 1 throughout. Final assignment: Fig1=AUROC bars, Fig2=ROC curves, Fig3=SMC distribution, Fig4=NLI vs Embed scatter.
2. **MAJOR-AC-002** ([CITATION NEEDED] placeholder): Removed `[CITATION NEEDED: any paper discussing RLHF effects on UQ]` text. Replaced with hedged claim citing Ouyang et al. 2022 and Bai et al. 2022 for RLHF output effects, noting downstream UQ implication is not systematically investigated. "First direct empirical evidence" → "To our knowledge, the first direct empirical evidence in the context of hallucination detection."
3. **MAJOR-BR-001** (Section 4 redundancy): Removed ~180 words of duplicated methodology from Section 4. Section 4 now contains only: four nested questions (Q1-Q4), hardware spec, evaluation protocol, baselines. Forward-references Section 3 for full methodology details.

### Round 2: Numerical Verification

**Accuracy Checker — Numerical Verification:**
- All 20+ quantitative values verified against ground truth: 0 discrepancies
- Mathematical checks: C(10,2)=45 ✅, 45,000=1000×45 ✅, 10,000=1000×10 ✅
- Gap calculation: 0.6299-0.6236=0.0063 rounds to 0.006 ✅
- Mechanism range: 0.9853-0.3875=0.5978 ✅

**Skeptical Expert — Credibility:**
- C1-C4 contributions verified as internally consistent and supported
- Baseline fairness: appropriate — random classifier is correct comparison; no cross-task unfairness
- No baseline numbers disputed

**R2 Issues (MINOR only, 2 items):**
- MINOR-R2-001: AUROC SE claim "< 0.02" slightly optimistic (≈ 0.022)
- MINOR-R2-002: Temperature citation concern (persists from R1 MINOR)

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | No changes |
| Introduction | No changes |
| Related Work | [CITATION NEEDED] removed; "first" → "to our knowledge, first in context of hallucination detection"; positioning paragraph rewritten |
| Methodology | Figure 3 reference corrected (was erroneously labeled Figure 1) |
| Experimental Setup | Removed ~180 words duplicating Section 3; kept Q1-Q4 structure, hardware, eval protocol |
| Results | Figure refs confirmed correct (Figure 1, 2, 3, 4 all present, no conflicts) |
| Discussion | No changes |
| Conclusion | No changes |

---

## Quality Improvements

- **Logical Consistency:** Improved — figure numbering conflict eliminated
- **Numerical Accuracy:** Unchanged — all values were already correct
- **Novelty Claims:** Refined — appropriately hedged, placeholder removed
- **Baseline Comparison:** Unchanged — no issues found
- **Persuasiveness:** Improved — figure conflict and placeholder were the two main engagement blockers
- **Paper Length:** Reduced — ~180 words removed from Section 4

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Temperature validation**: If SelfCheckGPT actually uses T=1.0, the design rationale for T=0.7 loses its citation support. Prepare: "We use T=0.7 within the sampling range of prior work; at T=0.7 the model still generates diverse samples (std=0.3388 confirms this) while matching practical deployment settings."

2. **Single model scope**: Reviewers will ask about other RLHF models. Prepared response: "Limitation L1 explicitly acknowledges this. The regime characterization experiment on other models is future work. The framework we provide (measure per-label SMC gap before deployment) applies to any model."

3. **HaluEval label validity (QLC4)**: Reviewers may argue AUROC failure is just label noise, not regime. Prepared response: "Section 6 explicitly argues this is secondary — the mean score analysis (both labels produce 0.62 consistency) is label-independent. With any binary labeling, both groups produce identical consistency — there is no signal to detect."

4. **N=10 sufficiency**: Reviewers may ask if N=20 would show signal. Prepared response: "The regime analysis shows mean SMC-NLI differs by 0.006 (<<1 SD). No N will distinguish distributions with means 0.006 apart given std=0.34 — the effect size is essentially zero."

5. **"Systematic confabulation" terminology**: Reviewers may push back on the term. Prepared response: "The regime concept is the contribution; the term is descriptive. We acknowledge 'confabulation' appears in adjacent literature and use it here in the specific RLHF-output-consistency sense."
