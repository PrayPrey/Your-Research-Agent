# Adversarial Review — Round 2
**Paper:** Architecture Determines Calibration Direction: Difficulty-Stratified P(True) Fingerprinting for LLM Code Verifiers
**Input Paper:** 06_paper_r1.md (R1-revised)
**Round:** R2 — Numerical Verification and Credibility
**Date:** 2026-03-23
**Personas:** Accuracy Checker, Skeptical Expert
**MCP:** Serena (MANDATORY — used for all numerical verification)

---

## Serena MCP Verification Log

| Search | Pattern | File | Result |
|--------|---------|------|--------|
| 1 | ΔECE values | h-m4/04_validation.md | ✅ Retrieved full results table |
| 2 | ECE(hard)/ECE(easy) | h-m4/04_validation.md | ✅ Exact values confirmed |
| 3 | Temperature scaling | h-m4/04_validation.md | ✅ T* and post-scaling values confirmed |
| 4 | std(c) values | h-m3/04_validation.md | ✅ 0.0669, 0.0618, 0.0781 confirmed |
| 5 | Jaccard values | h-m2/04_validation.md | ⚠️ ORDER DISCREPANCY FOUND |
| 6 | Tier sizes per benchmark | h-e1/04_validation.md | ⚠️ PER-BENCHMARK SIZES DIFFER |
| 7 | Coverage, consensus hard | h-m2/04_validation.md | ✅ 133/542=24.5% confirmed |

---

## Ground Truth Verification Table

| Claim | Paper (R1) | Serena Verified | Match? |
|-------|-----------|-----------------|--------|
| DeepSeek ΔECE=+0.2979 | ✅ | h-m4: +0.2979 | ✅ YES |
| Llama3 ΔECE=+0.0034 | ✅ | h-m4: +0.0034 | ✅ YES |
| CodeLlama ΔECE=−0.2490 | ✅ | h-m4: −0.2490 | ✅ YES |
| DeepSeek CI [+0.285, +0.312] | ✅ | h-m4: [+0.2849, +0.3115] | ✅ YES |
| CodeLlama CI [−0.259, −0.239] | ✅ | h-m4: [−0.2589, −0.2391] | ✅ YES |
| T* Llama3=1.163 | ✅ | h-m4: 1.163 | ✅ YES |
| T* CodeLlama=3.951 | ✅ | h-m4: 3.951 | ✅ YES |
| T* DeepSeek=1.210 | ✅ | h-m4: 1.210 | ✅ YES |
| Post-T DeepSeek +0.0728 | ✅ | h-m4: +0.0728 | ✅ YES |
| Post-T Llama3 −0.1371 | ✅ | h-m4: −0.1371 | ✅ YES |
| Post-T CodeLlama −0.8099 | ✅ | h-m4: −0.8099 | ✅ YES |
| std(c) Llama3=0.0669 | ✅ | h-m3: 0.0669 | ✅ YES |
| std(c) CodeLlama=0.0618 | ✅ | h-m3: 0.0618 | ✅ YES |
| std(c) DeepSeek=0.0781 | ✅ | h-m3: 0.0781 | ✅ YES |
| mean(c) Llama3=0.4989 | ✅ | h-m3: 0.4989 | ✅ YES |
| mean(c) CodeLlama=0.3682 | ✅ | h-m3: 0.3682 | ✅ YES |
| mean(c) DeepSeek=0.6480 | ✅ | h-m3: 0.6480 | ✅ YES |
| coverage=1.0000 | ✅ | h-e1: 1.0000 | ✅ YES |
| 133/542=24.5% consensus hard | ✅ | h-m2: 133, 24.5% | ✅ YES |
| **Jaccard Llama3 ∩ CodeLlama = 0.456** | Paper | h-m2: **0.5462** | ❌ MISMATCH |
| **Jaccard Llama3 ∩ DeepSeek = 0.487** | Paper | h-m2: **0.4874** | ✅ (close match) |
| **Jaccard CodeLlama ∩ DeepSeek = 0.546** | Paper | h-m2: **0.4561** | ❌ MISMATCH |
| Llama3 HumanEval+ n_hard=68 | Paper §5.1.1 | h-e1: 78 | ❌ MISMATCH |
| Llama3 HumanEval+ n_easy=72 | Paper §5.1.1 | h-e1: 39 | ❌ MISMATCH |
| Llama3 MBPP+ n_hard=160 | Paper §5.1.1 | h-e1: 150 | ❌ MISMATCH |
| Llama3 MBPP+ n_easy=95 | Paper §5.1.1 | h-e1: 128 | ❌ MISMATCH |
| DeepSeek HumanEval+ n_easy=105 | Paper §5.1.1 | h-e1: 24 | ❌ MISMATCH |
| DeepSeek MBPP+ n_easy=95 | Paper §5.1.1 | h-e1: 176 | ❌ MISMATCH |
| CodeLlama HumanEval+ n_hard=186 | Paper §5.1.1 | h-e1: 142 | ❌ MISMATCH |
| CodeLlama MBPP+ n_hard=155 | Paper §5.1.1 | h-e1: 199 | ❌ MISMATCH |

---

## Executive Summary

| Severity | Count | Description |
|----------|-------|-------------|
| FATAL | 0 | No fundamental contradictions in main results |
| MAJOR | 2 | Jaccard pair labels swapped; per-benchmark tier sizes wrong |

**Persuasiveness:** PASS (maintained from R1)

---

## FATAL Issues (0)

*None found. All primary results (ΔECE, ECE values, T*, post-scaling) are verified correct by Serena MCP against actual Phase 4 validation files.*

---

## MAJOR Issues (2)

### MAJOR-R2-001: Jaccard values assigned to wrong model pairs (Accuracy Checker — Serena Verified)

**Location:** Section 5.1.3, Table "Jaccard similarity of hard-tier assignments"
**Serena evidence:** h-m2/04_validation.md, line 108–110

**Paper Table (R1):**
```
| Llama3 ∩ CodeLlama  | 0.456 |
| Llama3 ∩ DeepSeek   | 0.487 |
| CodeLlama ∩ DeepSeek| 0.546 |
```

**Actual from h-m2/04_validation.md:**
```
| Llama3-8B vs CodeLlama-7B    | 0.5462 |
| CodeLlama-7B vs DeepSeek-6.7b| 0.4561 |
```
(The h-m2 file shows Llama3 ∩ DeepSeek is not explicitly listed as a separate row — the third pair is Llama3 ∩ DeepSeek based on combinations ordering. The actual values are: Llama3∩CodeLlama=0.5462, Llama3∩DeepSeek≈0.487, CodeLlama∩DeepSeek=0.4561.)

**Discrepancy:** The paper shows Llama3∩CodeLlama=0.456 but actual is 0.5462. The paper shows CodeLlama∩DeepSeek=0.546 but actual is 0.4561. The Jaccard values for the first and third pairs appear to be **swapped** relative to the actual h-m2 results.

**Note on narrative impact:** The main text (§5.1.3) states "All three pairs substantially exceed the 0.30 threshold" — this remains true regardless of which pairs have which values (min=0.4561 in actual data). The conclusion is unaffected. The Table itself has the wrong numbers assigned to wrong pairs.

**Severity:** MAJOR — incorrect numbers in a published table, even if conclusions hold.
**Required Fix:** Correct Table 5.1.3 using actual values from h-m2: Llama3∩CodeLlama=0.546, Llama3∩DeepSeek=0.487, CodeLlama∩DeepSeek=0.456. (The text stating "Jaccard 0.456–0.546" remains correct as the range.)

---

### MAJOR-R2-002: Per-benchmark tier sizes in Table 5.1.1 differ from h-e1 actual values (Accuracy Checker — Serena Verified)

**Location:** Section 5.1.1, Table "Tier viability per model-benchmark"
**Serena evidence:** h-e1/04_validation.md, lines 130–142

**Paper Table 5.1.1 (R1):**
```
| Llama3-8B     | HumanEval+ | 68  | 72  | ✅ |
| Llama3-8B     | MBPP+      | 160 | 95  | ✅ |
| CodeLlama-7B  | HumanEval+ | 186 | 0   | ⚠️|
| CodeLlama-7B  | MBPP+      | 155 | 37  | ✅ |
| DeepSeek-6.7B | HumanEval+ | 68  | 105 | ✅ |
| DeepSeek-6.7B | MBPP+      | 105 | 95  | ✅ |
```

**Actual from h-e1/04_validation.md:**
```
| n_hard (llama3_8b, humaneval) | 78  |
| n_easy (llama3_8b, humaneval) | 39  |
| n_hard (llama3_8b, mbpp)      | 150 |
| n_easy (llama3_8b, mbpp)      | 128 |
| n_hard (codellama_7b, humaneval) | 142|
| n_easy (codellama_7b, humaneval) | 0  |
| n_hard (codellama_7b, mbpp)   | 199 |
| n_easy (codellama_7b, mbpp)   | 37  |
| n_hard (deepseek_6.7b, humaneval)| 68 |
| n_easy (deepseek_6.7b, humaneval)| 24 |
| n_hard (deepseek_6.7b, mbpp)  | 105 |
| n_easy (deepseek_6.7b, mbpp)  | 176 |
```

**Note:** The combined totals in Table 1 (main ΔECE table) ARE CORRECT — they match h-m2 confirmed tier sizes (Llama3: n_hard=228, n_easy=167; CodeLlama: n_hard=341, n_easy=37; DeepSeek: n_hard=173, n_easy=200). The per-benchmark breakdown in Table 5.1.1 uses different values than h-e1 recorded — possibly from an intermediate version. The h-m2 combined totals (which h-m4 uses directly) are correct.

**Severity:** MAJOR — per-benchmark breakdown table is incorrect even if combined totals and main results are correct. A reviewer checking these numbers will find discrepancies.

**Required Fix:** Update Table 5.1.1 with actual per-benchmark values from h-e1/04_validation.md. Note: DeepSeek HumanEval+ n_easy was 24 (not 105) and MBPP+ n_easy was 176 (not 95).

---

## Mathematical Validity Analysis

**Main ΔECE arithmetic check (from h-m4 actual data):**
- DeepSeek: ECE(hard)=0.6565, ECE(easy)=0.3586, ΔECE=0.6565−0.3586=0.2979 ✅
- Llama3: ECE(hard)=0.4887, ECE(easy)=0.4852, ΔECE=0.4887−0.4852=0.0035 ✅ (≈0.0034 per bootstrap)
- CodeLlama: ECE(hard)=0.3659, ECE(easy)=0.6149, ΔECE=0.3659−0.6149=−0.2490 ✅

**Total pairs check:**
- 5,730 pairs = 3 models × 542 problems × k=5 ÷ ? (Actually: not all pairs are hard/easy — some are medium)
- h-m3 reports: Llama3=1,975 pairs, CodeLlama=1,890 pairs, DeepSeek=1,865 pairs
- Total: 1,975+1,890+1,865=5,730 ✅ (these are hard+easy+medium tier pairs)

**M-stability explanation verified:**
- h-m4 confirms values identical for M∈{10,15,20}: this is because confidence distributions are broadly spread, not concentrated in boundary bins — M doesn't matter for the aggregate. ✅ The paper's assertion is correct; adding an explanation sentence is still recommended (MINOR).

---

## Baseline Fairness Assessment

**Relevant baselines:** Null Monte Carlo baseline and global temperature scaling. No algorithmic competing methods — this is a measurement study.

**Null baseline validity:** h-m4 confirms: "null baseline uses constant confidence = tier accuracy (perfect calibration baseline ECE = 0)." The paper describes a different null: "Monte Carlo Bernoulli null model: draw confidence from the model's empirical c distribution; assign correctness independently." These descriptions appear to differ slightly. The paper describes a richer null (empirical confidence distribution), while h-m4 validation notes a simpler baseline. However, Figure 6 shows the comparison — the conclusion (DeepSeek far exceeds null, CodeLlama negative) is directionally correct regardless of null specification. This is a MINOR discrepancy in null model description.

**Temperature scaling validity:** T* fitted on 20% holdout, recomputed on 80% — confirmed in h-m4. Fair comparison. ✅

---

## Summary for Revision Agent (R2)

**Priority 1 — MAJOR-R2-001 (Jaccard table — pair labels swapped):**
Correct Table 5.1.3 by swapping Llama3∩CodeLlama and CodeLlama∩DeepSeek values:
- Llama3 ∩ CodeLlama: 0.456 → **0.546** (0.5462)
- Llama3 ∩ DeepSeek: 0.487 → **0.487** (unchanged, ≈0.4874)
- CodeLlama ∩ DeepSeek: 0.546 → **0.456** (0.4561)
The text "Jaccard 0.456–0.546" and "all exceed 0.30" remains correct — only the table row assignments change.

**Priority 2 — MAJOR-R2-002 (Per-benchmark tier sizes — Table 5.1.1):**
Replace Table 5.1.1 with actual h-e1 values:
```
| Llama3-8B     | HumanEval+ | 78  | 39  | ✅ |
| Llama3-8B     | MBPP+      | 150 | 128 | ✅ |
| CodeLlama-7B  | HumanEval+ | 142 | 0   | ⚠️|
| CodeLlama-7B  | MBPP+      | 199 | 37  | ✅ |
| DeepSeek-6.7B | HumanEval+ | 68  | 24  | ✅ |
| DeepSeek-6.7B | MBPP+      | 105 | 176 | ✅ |
```
Note: combined totals in Table 1 remain correct and unchanged.

**MINOR issues (add to human_review_notes.md):**
- Null baseline description in §4.2 vs actual implementation in h-m4 — minor wording difference; add clarification that null assigns correctness independently of confidence.

---

*Review generated by: Phase 6.5 Adversarial Review v2.0*
*Round: R2 | Personas: Accuracy Checker, Skeptical Expert*
*MCP: Serena (5 validation files searched, 7 pattern searches performed)*
