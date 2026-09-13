# Adversarial Review Summary

**Paper:** Contracts Catch What Tests Miss: Measuring Execution-Based Oracle Strength for LLM-Generated Code
**Review Completed:** 2026-08-03
**Rounds Completed:** 2
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert). All FATAL and MAJOR issues were resolved.

| Severity | R1 Found | R1 Resolved | R2 Found | R2 Resolved | Remaining |
|----------|----------|-------------|----------|-------------|-----------|
| FATAL | 0 | 0 | 0 | 0 | 0 |
| MAJOR | 6 | 6 | 1 | 1 | **0** |

**MINOR Issues (11):** Collected in `065_human_review_notes.md` — NOT auto-fixed.

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Hook premise ("764 tests, still wrong 40%") is arresting; abstract delivers all 4 elements (problem/approach/result/significance) |
| Problem clear by paragraph 2? | PASS | Three-level framing (surface/deeper/gap) is clear and effective |
| Novelty clear by end of Introduction? | PASS | Contributions 1–4 are well-differentiated; CVT oracle isolation design is clearly new |
| Figure 1 self-explanatory? | N/A | Figures not embedded (placeholder references); no assessment possible |
| Hook avoids "X is important"? | PASS | Hook leads with a specific counterintuitive finding, not a generic importance claim |
| Would continue reading? | PASS | Hook payoff clear; sections lead well |
| Attention lost at? | PASS (after fix) | Table 4 framing fixed in R1; structural null finding now clearly pre-labeled |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (0 FATAL, 6 MAJOR)

**Accuracy Checker Findings (2 MAJOR):**

| Issue | Finding | Resolution |
|-------|---------|------------|
| MAJOR-A1 | Contract failure rate 0.997 on CVT inputs: ceiling effect not addressed | Added clarifying paragraph explaining expected near-unity rate; CU mass (0.40) identified as scientifically informative quantity |
| MAJOR-A2 | h-e1 "62.6%" lacked explicit numerator/denominator | Changed to "228/364 tasks (62.6%)" |

**Bored Reviewer Findings (1 MAJOR):**

| Issue | Finding | Resolution |
|-------|---------|------------|
| MAJOR-E1 | Table 4 three ❌ FAIL rows signal experiment failure before prose corrects | Added pre-table note: "❌ FAIL entries indicate structural statistical constraints (n=5 underpowering), not hypothesis failures" |

**Skeptical Expert Findings (3 MAJOR):**

| Issue | Finding | Resolution |
|-------|---------|------------|
| MAJOR-C1 | Two [UNVERIFIED] citations in live reference list | Removed both citations and dependent paragraphs from §2.4 and References |
| MAJOR-C2 | CVT input scope qualifier absent from abstract; hook implies 40% on 764-test inputs | Added "on CVT inputs" qualifier; hook revised to "on the inputs that matter most to contract semantics" |
| MAJOR-C3 | "Model-invariant" language overclaims theoretical universality (5 models, 1 benchmark) | Replaced with "model-consistent across all 5 tested model families" throughout |

### Round 2: Numerical Verification (0 FATAL, 1 MAJOR)

**All arithmetic verified correct.** Full numerical verification table in `065_review_r2.md`.

| Issue | Finding | Resolution |
|-------|---------|------------|
| MAJOR-R2-1 | Oracle gap (Exp A) demonstrated on 3 models; abstract/intro/conclusion claim "5 LLM families" | Scoped oracle gap claims to "3 LLM families (Experiment A)"; adaptive contribution retains "5 tested model families (Experiment B)"; §3.3 LLM Corpus now documents experiment-level coverage |

---

## Sections Modified

| Section | Round 1 Modifications | Round 2 Modifications |
|---------|----------------------|----------------------|
| Abstract | CVT qualifier added; "model-invariant" → "5 tested model families" | "5 LLM families" → "3 LLM families (Experiment A)" |
| §1 Introduction | Hook revised; Contribution 2 scoped; Contribution 3 "model-invariantly" removed | Contribution 2 "3 LLM families" |
| §2.3 Related Work | Added closing sentence on verified citations | — |
| §3.3 LLM Corpus | — | Added Exp A/B model coverage note |
| §5.1 Results | Added ceiling-effect explanation paragraph | "3 model families" in gap consistency sentence |
| §5.4 / Table 4 | Added pre-table structural constraint note | — |
| §5 Summary Table | h-e1 "228/364 tasks (62.6%)" | — |
| §6.1 Discussion | "model-invariant" → "model-consistent" | — |
| §7 Conclusion | Hook and contribution 3 revised | "3 model families (Exp A)" + "5 model families (Exp B)" |
| References | Removed 2 unverified entries | — |

---

## Quality Assessment Post-Review

| Dimension | Pre-Review | Post-Review |
|-----------|------------|-------------|
| Numerical accuracy | ✅ All verified | ✅ All verified |
| Scope accuracy | ❌ "5 families" for 3-model experiment | ✅ Correctly scoped |
| Citation integrity | ❌ 2 unverified citations present | ✅ All citations verified |
| CVT scope disclosure | ⚠️ In limitations only | ✅ In abstract and introduction |
| Novelty language | ⚠️ "Model-invariant" overclaim | ✅ "Model-consistent across 5 tested families" |
| Table 4 framing | ⚠️ Visual ❌ misleads before prose corrects | ✅ Pre-table note added |
| Baseline fairness | ✅ Fair throughout | ✅ Confirmed |
| Limitations disclosure | ✅ L1–L4 complete | ✅ Unchanged |

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Experiment A partial coverage (3/5 models)** — now disclosed accurately; prepared response: "Experiment A demonstrates the oracle-isolation gap on 3 model families spanning open and closed architectures; Experiment B (adaptive PBT) confirms the finding generalizes to all 5 families. Expanding Experiment A to all 5 models is immediate future work."

2. **CVT input selection bias** — disclosed in L1; prepared response: "CVT inputs are the natural evaluation domain for contract-violating behavior — they are the inputs where contracts are designed to be discriminative. The question of whether the 40% gap persists on random inputs is explicitly identified as future work."

3. **n=5 model sample for cross-model analysis** — disclosed in L2; prepared response: "n=5 is a structural constraint; the ΔR²=0.004 null finding is interpretable as a genuine null (model identity adds negligible variance beyond pass@1* and size) without requiring p-significance."

4. **ContractEval-specific scope (L3)** — prepared response: "ContractEval is the only publicly available benchmark with executable Python contracts for LLM-generated code. The oracle isolation design is benchmark-agnostic and replicable on any benchmark with formal contract annotations."

5. **Richness gradient null (L4, ρ=0.136)** — prepared response: "The null gradient is informative: contract presence creates a threshold effect, not a complexity gradient. This is because ContractEval's contracts are precondition-dominated; postcondition-only analysis is a targeted future experiment."

---

## Files Generated

| File | Path | Description |
|------|------|-------------|
| Final Paper | `paper/06_paper_final.md` | Reviewed and revised paper (R1+R2 fixes) |
| Review R1 | `paper/review/065_review_r1.md` | Round 1 adversary report |
| Review R2 | `paper/review/065_review_r2.md` | Round 2 numerical verification report |
| Review Summary | `paper/review/065_review_summary.md` | This file |
| Changelog | `paper/review/065_changelog.md` | Detailed change log |
| Human Review Notes | `paper/review/065_human_review_notes.md` | 11 MINOR issues for human polish |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` | Review state |

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
