# Adversarial Review - Round 1

**Paper:** When Adversarial Examples Improve Calibration: Construction-Method-Dependent Calibration Degradation in Open-Weight LLMs
**Reviewed:** 2026-08-25
**Reviewer:** Adversary Agent v2 (Three-Persona)
**Round:** R1 - Accuracy, Engagement, and Credibility

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 1 | NEEDS_WORK |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 3 | NEEDS_WORK |
| **TOTAL** | **0** | **5** | **NEEDS_WORK** |

**Recommendation:** MINOR_REVISION — No fatal issues. All major issues are fixable with targeted edits. Core research is sound; presentation needs adjustment.

---

## Ground Truth Verification Summary

All 18 numerical claims in the paper were checked against `065_ground_truth.yaml`. **Zero discrepancies found.** All values match ground truth within stated rounding conventions.

| Metric | Paper | Ground Truth | Match? |
|--------|-------|-------------|--------|
| AdvGLUE MNLI ΔECE | +0.071 | 0.0705 | ✓ |
| ANLI R1 ΔECE | −0.041 | −0.0405 | ✓ |
| ANLI R2 ΔECE | −0.014 | −0.0136 | ✓ |
| ANLI R3 ΔECE | +0.024 | 0.0244 | ✓ |
| AdvGLUE QQP ΔECE | −0.029 | −0.0294 | ✓ |
| RLHF ANLI R1 ΔΔECE | +0.115 | 0.1149 | ✓ |
| RLHF ANLI R2 ΔΔECE | +0.147 | 0.1474 | ✓ |
| RLHF ANLI R3 ΔΔECE | +0.043 | 0.0425 | ✓ |
| RLHF AdvGLUE ΔΔECE | −0.026 | −0.0256 | ✓ |
| ANLI moderation rate | 100% (3/3) | 1.0000 | ✓ |
| Label preservation | 1.000 all splits | 1.000 | ✓ |
| Clean MNLI ECE | 0.279 | 0.2792 | ✓ |
| AdvGLUE ECE(adv) | 0.350 | 0.3497 | ✓ |
| Mean conf. wrong preds | 0.616 | 0.616 | ✓ |
| n(AdvGLUE MNLI) | 121 | 121 | ✓ |
| n(ANLI R1-R3) | 200 each | 200 | ✓ |
| n(AdvGLUE QQP) | 78 | 78 | ✓ |
| Bin-count ECE stability | 0.3497 (10/15/20) | verified stable | ✓ |

---

## Part 1: Accuracy Check (Persona 1 — Accuracy Checker)

### FATAL Issues — Accuracy
*None.*

### MAJOR Issues — Accuracy

#### MAJOR-ACC-001: ANLI R2 ΔΔECE framing is technically correct but misleading

**Location:** Section 5.4, Table 3, Results paragraph "Finding 1"

**Issue:** The paper states: *"The largest effect is on ANLI R2: ΔΔECE = +0.147, meaning the base model shows 14.7 percentage points more calibration degradation than the chat model on this split."*

However, ΔECE(base) for ANLI R2 = +0.002 (effectively zero — no meaningful calibration change in the base model). The large ΔΔECE is driven almost entirely by the chat model's dramatic calibration improvement (ΔECE(chat) = −0.146), not by base model degradation. Saying the base model "shows 14.7 percentage points more calibration degradation" implies the base model degrades, which it does not (it's essentially unchanged from clean).

**Evidence from ground truth:**
- ΔECE(base) ANLI R2: +0.002 (actual: 0.0017 ≈ 0)
- ΔECE(chat) ANLI R2: −0.146 (actual: −0.1458)
- ΔΔECE = 0.0017 − (−0.1458) = 0.1474 ≈ +0.147

**Impact:** A careful reviewer will notice ΔECE(base)=+0.002 and ask: "If the base model shows near-zero change, is this really 'moderation of base model degradation,' or just 'chat model shows large improvement'?" The framing could be attacked as misleading.

**Required Fix:** Clarify that for ANLI R2, the ΔΔECE reflects primarily the chat model's calibration improvement, not base model degradation. E.g., "RLHF moderation on ANLI R2 reflects primarily the chat model's substantial calibration improvement (ΔECE(chat) = −0.146) relative to the base model's near-zero ECE change (+0.002). The RLHF-aligned model is substantially better calibrated under these conditions regardless of the comparison framing."

---

## Part 2: Engagement Check (Persona 2 — Bored Reviewer)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PARTIAL | Hook buried; finding appears after scene-setting |
| Problem clear in 1 min? | ✓ | Clear by §"The Problem" in Introduction |
| Novelty clear in 2 min? | ✓ | Four contributions stated explicitly |
| Figure 1 self-explanatory? | UNKNOWN | Not verifiable from text; figure referenced as external file |
| Would continue reading? | ✓ | Introduction hook (ANLI paradox) is strong |

**Attention Lost At:** Abstract, sentence 1 (before reaching the finding)

### FATAL Issues — Engagement
*None.*

### MAJOR Issues — Engagement

#### MAJOR-ENG-001: Abstract buries the counterintuitive hook

**Location:** Abstract (first paragraph)

**Issue:** The Abstract opens with: *"Adversarial NLP benchmarks are widely used to stress-test large language models, but accuracy robustness tells only half the story..."*

This is a generic problem-framing sentence. The paper's actual hook — that adversarial benchmarks can *improve* calibration, contrary to expectation — appears only in the middle of the abstract (sentence 4-5) and more powerfully in the Introduction's opening paragraph. The bored reviewer skimming abstracts will not get to it.

The Introduction opens much more compellingly: *"...we found that the model's Expected Calibration Error decreased relative to its performance on clean MultiNLI."* This specific, concrete, counterintuitive finding is what makes the paper interesting. It should appear within the first 2 sentences of the abstract.

**Impact:** A reviewer reading abstracts in a conference stack may not continue to the Introduction, missing the compelling hook entirely.

**Suggested Fix:** Restructure abstract opening to lead with the finding. Example:

> "When we evaluated an open-weight LLM on adversarial NLP benchmarks, we found a counterintuitive result: model-in-the-loop adversarial examples (ANLI R1) *improved* calibration (ΔECE = −0.041), while human-adversarial examples (AdvGLUE MNLI) degraded it (ΔECE = +0.071). Calibration robustness under adversarial conditions is not universal — it depends on *how* adversarial examples were constructed."

Then follow with methodology and broader findings.

---

## Part 3: Credibility Check (Persona 3 — Skeptical Expert)

### Novelty Claims Audit

| Claim | Location | Legitimate? | Notes |
|-------|----------|-------------|-------|
| "First measurement of logit-based ECE on adversarial NLP benchmarks" | Contribution 1, Abstract | PLAUSIBLE | 17 citations unverified; gap real per related work survey |
| "First documented benchmark-type × RLHF calibration interaction" | Contribution 3 | PLAUSIBLE | Post-hoc finding, honestly acknowledged in L4 |
| Framework "predicts when and how adversarial perturbation will degrade" | Abstract conclusion | OVERCLAIM | Single-model, 5 cells; see MAJOR-CRED-002 |

### FATAL Issues — Credibility
*None.*

### MAJOR Issues — Credibility

#### MAJOR-CRED-001: Contribution 4 (JSONL caching) is an engineering practice, not a research contribution

**Location:** Section 1 Contributions list, item (4); Section 3.5

**Issue:** Contribution 4 reads: *"Methodological contribution: JSONL cache reuse for efficient post-hoc calibration analysis."* This is described as one of four paper contributions. However, caching model output logits for multiple downstream analyses is a standard data engineering practice in NLP research — not a methodological research contribution.

A skeptical reviewer will read this and think:
1. "Why is caching listed alongside ECE measurement, conditional structure, and RLHF interaction?"
2. "This is padding the contributions list."
3. "If this is a contribution, the other contributions must not be strong enough to stand on three."

**Impact:** Dilutes the strength of the genuine contributions (1–3). Risk of reviewer discounting all contributions as oversold.

**Required Fix:** Remove from numbered contributions. Retain the description in Section 3.5 as an implementation/replicability detail. Condense to three contributions. Optionally fold into Contribution 1 as: "...using a JSONL caching strategy that enables multiple downstream analyses without repeated inference."

#### MAJOR-CRED-002: Abstract/Introduction make stronger universality claims than single-model scope supports

**Location:** Abstract final sentence; Introduction §Contributions; Conclusion §Summary

**Issue:** The abstract states: *"These findings establish adversarial calibration measurement as a distinct research problem from adversarial accuracy robustness, and provide a conditional framework — construction method × task type × RLHF alignment — for predicting when and how adversarial perturbation will degrade model reliability signals in deployment."*

Problems:
1. "Establish" is strong for a single-model pilot (Llama-2-7b-hf, 5 cells).
2. "Provide a conditional framework for predicting" implies generalizability. With 1 model × 5 cells, this is a hypothesis, not a validated predictive framework.
3. H-M2 gate FAILED (conf_wrong ≥ 0.70 not met; actual = 0.616) and H-M3 gate FAILED (ΔECE > 0.05 in ≥60% of cells; actual = 1/5 = 20%). These failures indicate the pipeline's own pre-specified quantitative criteria were not met — but the abstract language does not reflect this.

A reviewer who reads "provides a conditional framework for predicting" and then reads the Discussion limitations ("L1: single-model evaluation...statistically underpowered for the universal threshold claim") will note the gap between abstract promise and actual scope.

**Required Fix:**
- Change "establish" → "motivate" or "provide initial evidence for"
- Change "provides a conditional framework for predicting" → "motivates a conditional framework for understanding"
- Add a brief pilot-study scope qualifier: "within a single-model pilot study (Llama-2-7b-hf)"

#### MAJOR-CRED-003: Failed sub-hypothesis predictions not disclosed — creates impression of unqualified success

**Location:** Discussion §Limitations; Section 5.3 (RQ3)

**Issue:** The paper's pipeline pre-specified two quantitative predictions that were not met:

1. **H-M2 (confidence-accuracy decoupling):** Gate criterion was conf_wrong ≥ 0.70 on adversarial cells. Actual mean conf_wrong = 0.616. Gate: FAIL.
   - The paper reports 0.616 in Section 5.3 but frames it as: *"smaller than the ≥0.70 threshold originally hypothesized, suggesting that calibration degradation in NLP adversarial settings is more subtle than in vision-domain analogues."*
   - This is a reasonable framing, but does not explicitly say "this prediction failed."

2. **H-M3 (ΔECE threshold):** Gate criterion was ΔECE > 0.05 in ≥60% of cells. Actual: 1/5 cells (AdvGLUE MNLI only) = 20%. Gate: FAIL.
   - The paper does not explicitly mention this gate failure. It reports the ANLI gradient (which includes cells with small negative ΔECE) but does not say "only 1 of 5 cells exceeded our pre-specified ΔECE threshold."

A skeptical reviewer who checks: "Did they achieve what they set out to do?" will find that two of the pipeline's quantitative predictions were not met. Not disclosing this explicitly risks the appearance of cherry-picking the reporting to emphasize the successful cells.

**Required Fix:**
- Add a sentence in Discussion §Limitations: "We note that two of our pre-specified quantitative predictions were not met at their original thresholds: H-M2 (mean confidence on wrong adversarial predictions ≥ 0.70; actual = 0.616) and H-M3 (ΔECE > 0.05 in ≥60% of cells; actual = 20%, 1/5 cells). These results indicate that adversarial calibration degradation in LLMs is smaller in magnitude than originally hypothesized based on vision-domain analogues. The conditional structure we report remains valid at observed magnitudes."
- This converts a potential reviewer attack into a self-aware acknowledged limitation.

---

## Part 4: Human Review Notes

> Minor issues for human review during final polish. NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract, sentence 2 | "a model can become less accurate yet better calibrated, or maintain accuracy while losing confidence reliability" — hyphenation of "confidence reliability" is unusual; consider "confidence-accuracy reliability" | style |
| Section 3.3 | "ΔΔECE (delta-delta ECE)" — capitalization inconsistent (lowercase delta in some places, uppercase in others) | style |
| Section 5.4, Table 3 | Checkmark ✓ and ✗ symbols may not render in all PDF viewers; ensure LaTeX equivalents are used | formatting |
| Section 5.4 | "Llama-2-7b-chat" used without the "-hf" suffix in some places (e.g., Table 3 header says "7b pair") | clarity |
| Introduction §"The Gap" | Bold formatting for gap statement is inconsistent with the rest of the paper's formatting style | formatting |
| Section 6, L1 | "P1 (≥60% of model × task cells show ΔECE > 0.05)" — this is a forward reference without earlier introduction of P1 notation | clarity |
| References section | 17 citations listed, 0 verified (per frontmatter note) — placeholder "[UNVERIFIED-NO-MCP]" comment visible in frontmatter; must be removed in final version | formatting |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-CRED-001:** Remove JSONL caching from numbered contributions; demote to methodology detail. MUST FIX (dilutes contribution list).
2. **MAJOR-CRED-002:** Soften "establish" and "provides a conditional framework for predicting" in abstract; add pilot-study scope qualifier. MUST FIX (overclaims scope).
3. **MAJOR-CRED-003:** Add explicit disclosure of H-M2 and H-M3 gate failures in Discussion §Limitations. MUST FIX (credibility and transparency).
4. **MAJOR-ENG-001:** Restructure abstract to lead with counterintuitive finding (ANLI improves calibration) rather than scene-setting. SHOULD FIX (engagement).
5. **MAJOR-ACC-001:** Clarify ANLI R2 ΔΔECE framing — the signal is driven by chat improvement, not base degradation. SHOULD FIX (accuracy of framing).

### Key Concerns

- Three major credibility fixes needed but all are straightforward textual corrections — no data changes required.
- The paper's scientific core is strong and all numbers check out perfectly. Issues are presentational.
- Citation verification (17 citations, 0 verified) is a blocking requirement for the final paper but outside this review's scope.

### What's Working

- All numerical claims are accurate and internally consistent (ground truth check: 0 discrepancies).
- Introduction hook (ANLI paradox) is excellent — the strongest part of the paper.
- Limitations section (L1-L4) is unusually honest and thorough for the scope.
- Conditional structure (construction method × task type × RLHF) is clearly explained and supported by the data.
- JSONL caching methodology is genuinely useful even if overstated as a "contribution."
- Table 3 RLHF results are clean and the interaction finding is novel and interesting.
