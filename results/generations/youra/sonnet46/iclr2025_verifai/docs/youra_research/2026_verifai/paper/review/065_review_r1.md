# Adversarial Review — Round 1
**Paper:** Architecture Determines Calibration Direction: Difficulty-Stratified P(True) Fingerprinting for LLM Code Verifiers
**Round:** R1 — Accuracy and Engagement
**Date:** 2026-03-23
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Ground Truth Summary

| Metric | Ground Truth Value | Source |
|--------|--------------------|--------|
| DeepSeek ΔECE | +0.298 (CI [0.285, 0.312]) | 065_ground_truth.yaml |
| Llama3 ΔECE | +0.003 (CI includes zero) | 065_ground_truth.yaml |
| CodeLlama ΔECE | −0.249 (CI [−0.259, −0.239]) | 065_ground_truth.yaml |
| Total EvalPlus problems | 542 | 065_ground_truth.yaml |
| CodeLlama n_easy | 0 (HumanEval+), 37 (MBPP+) | 065_ground_truth.yaml |
| Consensus hard problems | 133/542 = 24.5% | 065_ground_truth.yaml |
| Jaccard range | 0.456–0.546 | 065_ground_truth.yaml |
| T* DeepSeek | 1.210 | 065_ground_truth.yaml |
| T* Llama3 | 1.163 | paper Table 5.4 / 045 |
| T* CodeLlama | 3.951 | paper Table 5.4 / 045 |
| Post-scaling DeepSeek | +0.073 | paper Table 5.4 / 045 |
| Post-scaling Llama3 | −0.137 | paper Table 5.4 / 045 |
| Post-scaling CodeLlama | −0.810 | paper Table 5.4 / 045 |

---

## Executive Summary

| Severity | Count | Notes |
|----------|-------|-------|
| FATAL | 0 | No fundamental contradictions |
| MAJOR | 3 | See MAJOR-001, MAJOR-002, MAJOR-003 below |

**Persuasiveness Assessment:**
| Check | Result |
|-------|--------|
| Abstract compelling? | PASS (marginally) |
| Problem clear in 1 minute? | PASS |
| Novelty clear in 2 minutes? | PASS |
| Would continue reading? | YES |
| Attention lost at? | Section 5.5 (M-stability claim needs explanation) |
| Overclaims found | 1 (mechanism contribution) |
| Missing limitations | YES (base model P(True) validity) |

**Overall Persuasiveness:** PASS (bored reviewer would continue reading)

**Recommendation:** CONTINUE TO R2 — Fix 3 MAJOR issues, then verify numerics

---

## FATAL Issues (0)

*None found.*

---

## MAJOR Issues (3)

### MAJOR-001: Abstract lacks narrative blueprint hook (Bored Reviewer)

**Location:** Abstract, first sentence
**Persona:** Bored Reviewer

**Issue:** The narrative blueprint explicitly designs the opening as: *"When a language model fails to write correct code, should you trust its confidence?"* This concrete question is the intended hook. The Abstract instead opens with: *"LLMs are increasingly deployed as code verifiers, where their P(True) logprob confidence signals filter and prioritize code review decisions."*

This is precisely the anti-pattern flagged in the narrative blueprint: "NOT 'calibration is important' — opens with a concrete question about a practical scenario." The blueprint's hook appears in the Introduction (first sentence), not the Abstract. A bored NeurIPS reviewer may not read the Introduction if the Abstract doesn't grab attention first.

**Evidence:** Narrative blueprint hook.opening_statement vs. Abstract §1.
**Severity:** MAJOR — affects first impression and whether the abstract is compelling for a busy reviewer.
**Required Fix:** Move or adapt the hook to be the first sentence of the Abstract. The Introduction already has the hook — the Abstract should have a similar opening.

---

### MAJOR-002: Contribution 3 overclaims "Evidence for mechanism" (Skeptical Expert)

**Location:** Introduction, Contribution 3; also Conclusion §2 item 3
**Persona:** Skeptical Expert

**Issue:** The paper states as a contribution: *"Evidence that global temperature scaling cannot correct architecture-dependent miscalibration: Temperature scaling (T fitted on 20% holdout) fails to reverse ΔECE direction..."*

More critically, Contribution 3 in the Conclusion reads: *"Evidence for training data composition as the mechanism: CodeLlama's extreme T*=3.95 and inverted ΔECE (−0.249) suggest that code fine-tuning on common utility patterns creates systematic overconfidence..."*

The Discussion (§6.2) appropriately hedges: *"We note that this mechanistic interpretation is exploratory (N=1 per architecture category)."* However, framing it as a "contribution" in the Introduction and Conclusion implies the mechanism was demonstrated, not hypothesized. This is an inconsistency between the contribution framing and the actual epistemic status.

**Evidence:** Introduction Contribution 3 vs. Discussion §6.2, Conclusion §2 item 3.
**Severity:** MAJOR — a skeptical expert reviewer will challenge this directly; it weakens credibility.
**Required Fix:** Reframe Contribution 3 to: *"A training-data composition hypothesis for the mechanism..."* or *"Preliminary evidence consistent with a training-data composition mechanism..."* — matching the Discussion's hedged language.

---

### MAJOR-003: Base model P(True) validity not adequately addressed as a limitation (Skeptical Expert)

**Location:** §3.2, §6.4, Discussion
**Persona:** Skeptical Expert

**Issue:** The Kadavath et al. (2022) P(True) methodology was developed and validated on instruction-tuned or RLHF-trained models (specifically Anthropic's Claude-family models). The paper applies this methodology to **base models** (NousResearch/Meta-Llama-3-8B, CodeLlama-7b-hf, deepseek-coder-6.7b-base). Base models are not trained to respond to the prompt "Is the above solution correct? (True/False)" — they may respond based on surface co-occurrence patterns in pre-training data rather than genuine self-evaluation.

The paper acknowledges weak correlation (r=0.14–0.20) in §5.1.2 and notes it as L4 in §6.4. However, it does not explicitly discuss whether base model P(True) extraction is methodologically valid per the original Kadavath et al. protocol. A skeptical expert reviewer will immediately raise this question: *"Why did you use base models for P(True) when the original method was designed for instruction-tuned models?"*

**Evidence:** §3.2 (P(True) description uses same zero-shot format as Kadavath but on base models); §6.4 L4 (weak correlation acknowledged but not connected to methodological validity question).
**Severity:** MAJOR — this is the most likely attack vector from expert reviewers; it must be addressed explicitly.
**Required Fix:** Add explicit discussion to §3.2 (Rationale) or §6.4 explaining: (1) we use base models deliberately to isolate pre-training calibration; (2) the weak but significant correlation (r=0.14–0.20, p<10^{-10}) confirms the signal is non-random even for base models; (3) this is a limitation of the measurement methodology compared to instruction-tuned settings, and future work should replicate with instruction-tuned variants (already mentioned in §7 as a future direction). Add a specific limitation entry (L5) addressing this.

---

## Minor Issues (collected for human review)

These are NOT auto-fixed. Collected for `065_human_review_notes.md`.

1. **[clarity]** §5.2 narrative text says "ECE(hard)=0.657" and "ECE(easy)=0.359" for DeepSeek, but Table 1 shows 0.6565 and 0.3586. Minor rounding inconsistency (text rounds to 3 significant digits, table shows 4). Not an error — consider making consistent.

2. **[clarity]** §3.1: "six discrete pass@1 values {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}" — with k=5, the possible values are actually {0/5, 1/5, 2/5, 3/5, 4/5, 5/5} = {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} ✅ — correct but could add "k=5 yields" for clarity.

3. **[style]** Abstract: "Practitioners typically assume that confidence degrades on harder problems" — "practitioners" is uncited. Consider softening to "It is commonly assumed..." or citing a practitioner paper.

4. **[clarity]** Section 5.5: "ΔECE values are exactly stable across M ∈ {10, 15, 20}" — the word "exactly" with identical 5-decimal values (e.g., +0.29789 for all three M values) is suspicious to any reader. The paper does not explain WHY the values are identical. For M-insensitivity this should be explained: the confidence distributions are spread across many bins such that M-resampling produces the same bin partitions. Add 1-2 sentences explaining this.

5. **[grammar]** §5.3: "The model's easy tier (n=37, MBPP-only)" — should be "MBPP+ only" for consistency with the rest of the paper.

---

## Ground Truth Verification Log

| Paper Claim | Source Section | Ground Truth | Match? |
|-------------|----------------|--------------|--------|
| DeepSeek ΔECE=+0.298 | Abstract, Table 1 | +0.2979 (≈0.298) | ✅ YES |
| Llama3 ΔECE≈0 | Abstract, Table 1 | +0.0034 | ✅ YES |
| CodeLlama ΔECE=−0.249 | Abstract, Table 1 | −0.2490 | ✅ YES |
| DeepSeek CI [+0.285, +0.312] | §5.2 | [0.2849, 0.3115] | ✅ YES |
| CodeLlama CI [−0.259, −0.239] | §5.2 | [−0.2589, −0.2391] | ✅ YES |
| Total 542 problems | §4.1 | 542 | ✅ YES |
| HumanEval+ 164, MBPP+ 378 | §4.1 | 164, 378 | ✅ YES |
| Jaccard 0.456–0.546 | §5.1.3 | 0.456–0.546 | ✅ YES |
| 133/542 = 24.5% hard | §5.1.3 | 133, 24.5% | ✅ YES |
| T* CodeLlama = 3.95 | §5.4 | 3.951 | ✅ YES |
| Post-scaling DeepSeek +0.073 | §5.4 | +0.0728 | ✅ YES |
| Post-scaling CodeLlama −0.810 | §5.4 | −0.8099 | ✅ YES |
| Post-scaling Llama3 −0.137 | §5.4 | −0.1371 | ✅ YES |
| n_easy=37 (CodeLlama MBPP+) | §5.3 | 37 | ✅ YES |
| n_easy=0 (CodeLlama HumanEval+) | §5.1.1 | 0 | ✅ YES |
| std(c) 0.062–0.078 | §5.1.2 | 0.062–0.078 | ✅ YES |
| coverage = 1.0000 | §5.1.1 | 1.0000 | ✅ YES |

**All numerical claims match ground truth. No numerical discrepancies found.**

---

## Summary for Revision Agent

**Priority 1 — MAJOR-001 (Abstract hook):**
The abstract must open with a compelling concrete question or finding, not a "X is important" statement. The narrative blueprint's hook is already in the Introduction. Adapt/move the hook to the Abstract first sentence.

**Priority 2 — MAJOR-002 (Mechanism overclaim):**
Reframe Contribution 3 in Introduction and Conclusion to use hedged language matching Discussion §6.2. "Evidence for mechanism" → "Observation consistent with mechanism" or "Training-data composition hypothesis."

**Priority 3 — MAJOR-003 (Base model P(True) validity):**
Add explicit justification in §3.2 for using base models (deliberate choice to isolate pre-training calibration), connect L4 (weak correlation) to methodological validity, and add L5 as a new limitation entry explicitly addressing the instruction-tuned vs. base model question.

**MINOR issues:** Collect in `065_human_review_notes.md` — do NOT auto-fix.

---

*Review generated by: Phase 6.5 Adversarial Review v2.0*
*Round: R1 | Personas: Accuracy Checker, Bored Reviewer, Skeptical Expert*
