# Adversarial Review — Round 2

**Paper:** Contracts Catch What Tests Miss: Measuring Execution-Based Oracle Strength for LLM-Generated Code
**Reviewed:** 2026-08-03
**Round:** R2 — Numerical Verification & Credibility

---

## Executive Summary (R2)

| Category | FATAL | MAJOR |
|----------|-------|-------|
| Mathematical validity | 0 | 0 |
| Baseline fairness | 0 | 0 |
| Signal-performance consistency | 0 | 0 |
| Model coverage claims | 0 | **1** |
| R1 fix verification | 0 | 0 |
| **TOTAL** | **0** | **1** |

**R2 Recommendation:** One MAJOR issue — the paper claims the oracle-isolation gap (primary RQ1 result) holds "across 5 model families" but Experiment A data covers only 3 models (10,432/18,200 triples completed). The adaptive PBT contribution (Experiment B) correctly spans 5 model families. Fix requires scoping oracle gap claims to 3 models and adaptive claims to 5 models. All arithmetic, statistics, and baseline comparisons verified correct.

---

## R2 Numerical Verification Table

| Check | Claim | Verified Value | Status |
|-------|-------|---------------|--------|
| Gap arithmetic | 0.9967 − 0.5955 = 0.4012 | 0.4012 | ✅ |
| CU mass vs gap | Both reported; gap=0.4012, CU=0.4023 (distinct measures) | Both in ground truth | ✅ |
| "4× threshold" | 0.4012 / 0.10 = 4.012 | 4.012 | ✅ |
| "8× threshold" | 0.4023 / 0.05 = 8.046 | 8.046 | ✅ |
| Per-model range | 0.1033 − 0.0993 = 0.004 | ground truth [0.0993, 0.1033] | ✅ |
| "~10pp" adaptive contribution | 0.0999 ≈ 10pp | 0.0999 | ✅ |
| Task counts | 117 + 247 = 364 | verified | ✅ |
| 95% CI oracle gap rounding | [0.358, 0.445] vs [0.3576, 0.4451] | acceptable rounding | ✅ |
| Wilcoxon p primary | 5.88e-38 | ground truth 5.88e-38 | ✅ |
| Adaptive Wilcoxon p | 2.64e-22 | ground truth 2.64e-22 | ✅ |
| Spearman ρ | 0.136, p = 5.30e-03 | ground truth confirmed | ✅ |
| Kendall τ | 0.40, p = 0.4833 | ground truth confirmed | ✅ |
| ΔR² | 0.0044 | ground truth confirmed | ✅ |
| Cross-model gap | 0.0069 | ground truth confirmed | ✅ |
| HumanEval+ / MBPP+ gaps | 0.520 / 0.345 | ground truth confirmed | ✅ |
| n_triples Exp A | 10,432 | h-m1/04_validation.md: 3 models × 364 tasks | ✅ |
| n_triples Exp B | 17,226 | 94.6% of 18,200 | ✅ |
| CU mass internal consistency | 99.7% contract × 40.4% diff-pass ≈ 40.3% ≈ CU 0.4023 | consistent | ✅ |
| h-e1 "228/364 = 62.6%" | 228/364 = 0.6264 | correct | ✅ |
| **Exp A model count** | **"5 LLM families" (abstract/intro)** | **h-m1: 3 models completed** | ❌ MISMATCH |
| h-e1 max-gap 0.471 | 0.471 | not in ground truth YAML | ⚠️ unverifiable |

---

## FATAL Issues — R2

None.

---

## MAJOR Issues — R2

### MAJOR-R2-1: Oracle-Isolation Gap (Experiment A) Demonstrated on 3 Models, Claimed Across 5

**Location:** Abstract, Introduction, Section 3.1, Section 4.1, Conclusion

**Finding:** The paper's Experiment A (h-m1), which establishes the core oracle-isolation gap of 0.4012, completed execution on **3 model families only** (Claude-3-Haiku, CodeLlama-13B, CodeLlama-34B — 10,432 triples out of 18,200 planned). GPT-4o-mini and DeepSeek-Coder-V2-Lite are listed as model families but are not present in the Experiment A per-model stratification table. Experiment B (adaptive PBT, h-m3) does span all 5 model families (17,226/18,200 triples, 5-model per-model table confirmed).

**Evidence from h-m1/04_validation.md:**
- "Work items: 18,200 (5 models × 364 tasks × 10 programs)"
- "Completed: 10,432 items (3 models × 364 tasks fully covered)"
- Per-model table: only claude-3-haiku-20240307, CodeLlama-13b-Instruct, CodeLlama-34b-Instruct

**Specific overclaims:**
1. Abstract: "Across 364 HumanEval+/MBPP+ tasks and **5 LLM families**, we find an oracle-isolation gap of 0.40" → should be "3 LLM families" for the gap finding
2. Abstract: "consistently across **all 5 tested model families**" → this applies to adaptive contribution (Exp B), but the sentence structure places it adjacent to the gap finding, creating ambiguity
3. Introduction: "10,432 evaluation triples, the contract oracle detects 40% more failures...across 364 ContractEval tasks, **5 model families**" → should be 3 model families
4. Section 5.1: The model stratification correctly lists 3 models, but the paragraph header "across model families" and the surrounding "5 model families" framing conflict

**Why not FATAL:** The oracle-isolation gap result itself (0.4012, all arithmetic, statistics) is valid and verified on the 3 completed models. The underlying claim that the gap exceeds threshold is fully supported. The gap is also likely stable across all 5 models given the model-consistency finding in Experiment B, but this extrapolation is not the same as having measured it.

**Required fix:**
1. Abstract: "3 LLM families" for the gap clause; "5 tested model families" for adaptive contribution clause
2. Introduction: "10,432 evaluation triples across 3 model families" for Experiment A; add "(Experiment B spans 5 model families and 17,226 triples)"
3. Section 3.1/LLM Corpus: Add a note that 3 of 5 model families completed Experiment A; all 5 completed Experiment B
4. Section 5.1 closing: Prefix with "Among the three fully-completed model families in Experiment A..." — the individual values (Claude 0.401, CL-13B 0.401, CL-34B 0.411) are correct

---

## Human Review Notes — R2 (MINOR)

| Location | Note | Type |
|----------|------|------|
| Sec 5 summary table | h-e1 max-gap 0.471 not verifiable from ground truth YAML; either add to GT or soften to "up to ~0.47" | clarity |
| Sec 5.2 | "257/354 tasks" denominator 354 never explained; 10 tasks excluded from Exp B; add one clause | clarity |
| h-m1 validation | CodeLlama-34b shows N=317 tasks in per-model table (not 364) — inconsistent with "3 models × 364" claim in validation summary; paper should note this | clarity |
| R1 fixes | All 6 R1 MAJOR fixes verified correct — no introduced errors | — |

---

## Summary for Revision Agent R2

**One MAJOR fix required (MAJOR-R2-1):**

Scope the oracle-isolation gap claims accurately:
- Abstract gap sentence: "3 LLM families" not 5
- Abstract adaptive sentence: keep "all 5 tested model families"
- Introduction: "3 model families, and 10,432 evaluation triples (Experiment A); adaptive contribution spans 5 model families across 17,226 triples (Experiment B)"
- Section 3.1 LLM Corpus: Note that Experiments A completed 3 of 5 model families
- Section 5.1: Prefix the model gap table with "Among the three model families completing Experiment A..."

**Three MINOR improvements (optional, for human review):**
- Explain 354 vs 364 denominator in Experiment B results
- Note CodeLlama-34b's 317/364 task coverage
- Soften h-e1 max-gap 0.471 if unverifiable
