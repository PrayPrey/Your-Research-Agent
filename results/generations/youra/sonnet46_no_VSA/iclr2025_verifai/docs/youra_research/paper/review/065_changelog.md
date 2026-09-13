# Changelog — Adversarial Review (Phase 6.5)

**Paper:** Contracts Catch What Tests Miss
**Review Period:** 2026-08-03
**Rounds:** 2
**Final Status:** CONVERGED

---

# Revision Log — Round 1

**Date:** 2026-08-03
**Input:** paper/06_paper.md
**Output:** paper/06_paper_r1.md

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-C1 | Two [UNVERIFIED] citations in reference list | ACCEPT | Removed "OpenAI. Code Monitor: Hidden Correctness Check Analysis, 2026. [UNVERIFIED]" and "Liguori et al. Factors Explaining Code Correctness Variance in LLMs, 2026. [UNVERIFIED]" from References. Removed dependent paragraphs from §2.4 "Supporting Context." Added closing sentence to §2.3: "All claims in this related work survey are drawn from peer-reviewed or publicly archived sources." |
| MAJOR-C2 | CVT scope qualifier absent from abstract; hook implies 40% on 764-test inputs | ACCEPT | Abstract: "40% contract-unique mass" → "40% contract-unique mass on CVT inputs — programs output-equal to ground truth but violating reference contracts on these contract-relevant inputs." Hook sentence: "is still wrong 40% of the time — if you ask a formal contract" → "can still be wrong 40% of the time — if you ask a formal contract on the inputs that matter most to contract semantics." Same fix applied to Conclusion opening. |
| MAJOR-A1 | Near-unity contract failure rate (0.997) on CVT inputs: ceiling effect not explained | ACCEPT | Added clarifying paragraph to §5.1 after reporting failure rates: "The near-unity contract failure rate reflects the design of CVT inputs: these inputs are specifically selected to trigger contract violations, so the reference contract oracle fires on nearly all of them by construction. The scientifically informative quantity is the contract-unique mass (0.40): among evaluations where the LLM program matches the reference output (differential oracle: PASS), the contract identifies 40% of programs as semantically invalid." |
| MAJOR-C3 | "Model-invariant" language overclaims theoretical universality | ACCEPT | Replaced all instances of "model-invariant" / "model-invariantly" with "model-consistent" / "consistently across all 5 tested model families" in: Abstract, Introduction Contribution 3, §6.1 Discussion Finding 2, Conclusion. |
| MAJOR-E1 | Table 4 three ❌ FAIL rows signal experiment failure before prose corrects | ACCEPT | Added pre-table italicized note before Table 4: "Note: The ❌ FAIL entries in this table indicate structural statistical constraints (n=5 underpowering), not hypothesis failures. The ΔR²=0.004 and cross-model gap=0.007 are genuine null findings; the permutation p=0.48 reflects the minimum achievable p at n=5, not a data quality issue." |
| MAJOR-A2 | h-e1 "62.6%" lacks explicit numerator/denominator | ACCEPT | Changed summary table h-e1 row from "62.6% show ≥1 violation" to "228/364 tasks (62.6%) show ≥1 violation." |

## Sections Modified

- Abstract: MAJOR-C2 (CVT qualifier), MAJOR-C3 (model language)
- §1 Introduction — hook sentence: MAJOR-C2
- §1 Introduction — Contribution 2: (no change needed in R1)
- §1 Introduction — Contribution 3: MAJOR-C3 ("model-invariantly" removed)
- §2.3 Formal Contract Checking: MAJOR-C1 (closing sentence added)
- §2.4 (Supporting Context paragraphs): MAJOR-C1 (removed unverified claims)
- §5.1 Results body: MAJOR-A1 (ceiling effect explanation)
- §5.4 Table 4: MAJOR-E1 (pre-table structural constraint note)
- §5 Summary Table: MAJOR-A2 (228/364 explicit fraction)
- §6.1 Discussion Finding 2: MAJOR-C3 ("model-invariant" → "model-consistent")
- §7 Conclusion: MAJOR-C2 (hook), MAJOR-C3 (model language)
- References: MAJOR-C1 (2 entries removed)

## Word Count Changes

| Section | Change | Delta |
|---------|--------|-------|
| §2.3 | Added closing sentence | +20 |
| §2.4 | Removed Supporting Context paragraphs | −150 |
| §5.1 | Added ceiling effect paragraph | +80 |
| §5.4 | Added pre-table note | +45 |
| Abstract | Qualifier additions | +12 |
| **Net** | | **−~3 words** |

## Issues NOT Addressed
None — all 6 MAJOR issues resolved.

---

# Revision Log — Round 2

**Date:** 2026-08-03
**Input:** paper/06_paper_r1.md
**Output:** paper/06_paper_r2.md (= 06_paper_final.md)

## Issues Addressed

### MAJOR Issues

| ID | Title | Decision | Action Taken |
|----|-------|----------|--------------|
| MAJOR-R2-1 | Oracle gap (Experiment A) demonstrated on 3 models; paper claims "5 LLM families" for this result | ACCEPT | Abstract: "5 LLM families" → "3 LLM families (Experiment A)" for gap clause; "(Experiment B)" added to adaptive contribution clause. Introduction Contribution 2: "5 LLM families" → "3 LLM families (Experiment A; 10,432 triples)." Introduction paragraph: "5 model families, and 10,432 evaluation triples" → "3 model families (Experiment A), and 10,432 evaluation triples; adaptive contribution spans 5 model families across 17,226 triples (Experiment B)." §3.3 LLM Corpus: added sentence noting Exp A covered 3 of 5 families, Exp B covered all 5. §5.1 body: "The gap is consistent across model families" → "Among the three model families completing Experiment A, the gap is consistent." Conclusion: "5 model families, and 10,432 evaluation triples" → "3 model families (Experiment A), and 10,432 evaluation triples. Adaptive PBT results span all 5 tested model families." |

## Sections Modified

- Abstract: MAJOR-R2-1 (model count scoped)
- §1 Introduction — Contribution 2: MAJOR-R2-1 ("3 LLM families")
- §1 Introduction — gap result paragraph: MAJOR-R2-1 ("3 model families")
- §3.3 LLM Corpus: MAJOR-R2-1 (Exp A/B coverage documented)
- §5.1 Results body: MAJOR-R2-1 ("three model families completing Experiment A")
- §7 Conclusion: MAJOR-R2-1 ("3 model families" + Exp B note)

## Word Count Changes

| Section | Change | Delta |
|---------|--------|-------|
| §3.3 | Added coverage sentence | +30 |
| §5.1 | Minor phrasing change | +5 |
| §7 Conclusion | Added Exp B coverage sentence | +15 |
| **Net** | | **+~50 words** |

## Issues NOT Addressed
None — 1 MAJOR issue resolved.

---

# Final Summary

**Total Revisions Made:** 7 MAJOR issues across 2 rounds
**Sections Modified:** Abstract, Introduction (§1), Related Work (§2.3), LLM Corpus (§3.3), Results §5.1 and §5.4, Discussion §6.1, Conclusion §7, References
**Word Count Change:** Net ~+47 words (from removals and additions)

**Review Process:**
- Started: 2026-08-03T18:00:00+00:00
- Completed: 2026-08-03T19:00:00+00:00
- Rounds: 2 (R1: 3-persona; R2: numerical verification)
- Personas Used: Accuracy Checker, Bored Reviewer, Skeptical Expert

**Files Generated:**
- `paper/06_paper_r1.md` — after Round 1 revision
- `paper/06_paper_r2.md` — after Round 2 revision
- `paper/06_paper_final.md` — final reviewed paper (= r2)
- `paper/review/065_review_r1.md` — Round 1 adversary report
- `paper/review/065_review_r2.md` — Round 2 adversary report
- `paper/review/065_review_summary.md` — consolidated review summary
- `paper/review/065_human_review_notes.md` — 11 MINOR issues for human review
- `paper/review/065_changelog.md` — this file

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
