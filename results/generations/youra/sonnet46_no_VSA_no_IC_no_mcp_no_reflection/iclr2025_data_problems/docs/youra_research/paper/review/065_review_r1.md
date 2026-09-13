# Adversarial Review — Round 1
**Round**: R1 — Accuracy, Engagement, Structural Issues
**Personas**: Accuracy Checker | Bored Reviewer | Skeptical Expert
**Paper**: "Does Better Data Produce Better-Generalized Models?"
**Date**: 2026-08-31

---

## Ground Truth Summary

| Claim | Ground Truth Value | Source |
|-------|-------------------|--------|
| Pythia MMLU/HellaSwag ratio | 0.565 | 04_validation.md Table |
| OLMo MMLU/HellaSwag ratio | 0.538 | 04_validation.md Table |
| Ratio difference (OLMo − Pythia) | −0.0265 | 04_validation.md |
| 95% CI | [−0.045, −0.007] | 04_validation.md |
| One-sided p-value | 0.004 | 045_validated_hypothesis.md |
| Cohen's d | −2.732 | 04_validation.md |
| HellaSwag (both models) | 0.458 | 04_validation.md |
| Pythia MMLU | 0.259 | 04_validation.md |
| OLMo MMLU | 0.246 | 04_validation.md |
| Overall result | REFUTED | verification_state |

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 1 |
| MAJOR | 3 |
| MINOR | 6 |

**Recommendation**: MAJOR_REVISION — one FATAL issue (p-value direction confusion) requires fix; MAJOR issues weaken credibility but are fixable.

---

## FATAL Issues

### FATAL-001: p-value Directional Confusion

**Persona**: Accuracy Checker
**Location**: Introduction (contribution 1), Results Section 5.2
**Severity**: FATAL

**Issue**: The paper inconsistently describes the p-value meaning. In Introduction contribution 1, the paper states:
> "Pythia achieves significantly higher ratio (p=0.996 one-sided, d=−2.732)"

But in Results Section 5.2:
> "The one-sided p-value (fraction of bootstrap iterations in which OLMo exceeds Pythia) is 0.004"

These are **two different p-values** reporting opposite things. p=0.996 is the probability OLMo exceeds Pythia (fails the hypothesis direction test). p=0.004 is the probability Pythia exceeds OLMo (which IS significant in the observed direction). The ground truth from 04_validation.md confirms: "Bootstrap p-value (one-sided): 0.996" for the test that OLMo > Pythia.

The paper uses 0.996 in Introduction and 0.004 in Results for what appears to be the same claim, creating a genuine factual contradiction. The correct interpretation: p=0.996 means OLMo almost never beats Pythia in bootstrap (96% CI is NOT that Pythia wins — rather, 0.4% of bootstrap iterations showed OLMo > Pythia, so 99.6% showed Pythia ≥ OLMo; thus the one-sided p for H0: OLMo ≥ Pythia is 0.004).

**Evidence**: 04_validation.md line 44: "Bootstrap p-value (one-sided): 0.996" with description "fraction of bootstrap iterations in which OLMo exceeds Pythia" — this is p=0.996, not 0.004. But the Results section says "The one-sided p-value (fraction of bootstrap iterations in which OLMo exceeds Pythia) is 0.004."

**Root cause**: 0.996 and 0.004 are complements (0.996 + 0.004 = 1.000). The paper switches between two definitions of "one-sided p-value" without flagging the switch:
- p=0.996: fraction of bootstrap iterations where OLMo > Pythia (the definition in 04_validation.md)
- p=0.004: fraction where OLMo ≤ Pythia (i.e., 1 − 0.996)

Both are technically valid depending on which null hypothesis is being tested, but using both numbers with the SAME description ("one-sided p-value, fraction where OLMo exceeds Pythia") in different sections is a direct contradiction — one number must be wrong, or the descriptions must differ. The ground_truth YAML gives p_value_one_sided: 0.004 with "HIGH confidence" which means the ground truth itself may have been set to 0.004 = 1−0.996 (the p-value for rejecting H0: Pythia ≥ OLMo).

**Required Fix**: Standardize to ONE p-value definition throughout. Recommended: use p=0.004 (the fraction of bootstraps where OLMo fails to exceed Pythia's threshold, i.e., supporting the refutation) and describe it precisely: "The one-sided p-value for the test that OLMo ≥ Pythia (i.e., fraction of bootstrap iterations where OLMo exceeded Pythia) is 0.004, far below α=0.05 — but in the wrong direction: this p-value tests whether Pythia's advantage is significant, and it is." Remove the p=0.996 usage from Introduction contribution 1.

---

## MAJOR Issues

### MAJOR-001: Abstract Overstates HellaSwag Finding

**Persona**: Accuracy Checker + Skeptical Expert
**Location**: Abstract, paragraph 3
**Severity**: MAJOR

**Issue**: The abstract states: "both models converge to identical HellaSwag commonsense scores at this training scale." This is presented as a confirmed finding, but the ground truth (065_ground_truth.yaml, confidence: MEDIUM) notes:
> "MEDIUM (fast eval; full evaluation recommended)"
> caveat: "500-sample limit; full evaluation may show small non-zero difference"

The identical HellaSwag scores (0.4580 = 0.4580 to 4 decimal places) under 500-sample fast evaluation may reflect sampling coincidence, not true convergence. The Results section (5.3) correctly qualifies this as "MEDIUM plausibility" for the coincidence explanation, but the Abstract does not carry this caveat. For a flagship structural finding, this creates an overstated claim.

**Required Fix**: Add qualification in Abstract: "converge to *effectively* identical HellaSwag scores (0.458 each, under 500-sample fast evaluation)" or add "(confidence: medium — fast eval may mask small differences)".

### MAJOR-002: "First Evaluation" Novelty Claim Requires Evidence

**Persona**: Skeptical Expert
**Location**: Introduction, Contribution 1; Conclusion Summary
**Severity**: MAJOR

**Issue**: The paper claims "to our knowledge, the first evaluation of MMLU/HellaSwag generalization balance ratios comparing Pythia-6.9B and OLMo-7B at controlled matched training scale." This "first" novelty claim is not supported by any literature search evidence in the paper. No prior work is cited to show this specific comparison has not been done.

The Related Work section (§2) discusses prior art but never explicitly says "no prior work has computed this ratio for these models at matched scale" — it just describes what other papers focused on. A skeptical reviewer will ask: "How do you know no preprint does exactly this?"

**Required Fix**: Either (a) soften to "to our knowledge" consistently AND cite at least one search strategy that failed to find prior work, or (b) change the claim to: "We provide, to our knowledge, the first *systematic* evaluation of [the ratio] as a *corpus-quality* discriminator at matched scale" — emphasizing the *systematic* and *purposeful* design rather than simple measurement.

### MAJOR-003: HellaSwag "Saturation" Mechanism Claimed Without Supporting Evidence

**Persona**: Skeptical Expert + Accuracy Checker
**Location**: Results §5.3, Discussion §3, Abstract, Conclusion
**Severity**: MAJOR

**Issue**: The paper's core structural finding — "HellaSwag commonsense performance reaches a scale-dependent saturation point for 6-8B models at ~300B tokens" — is asserted repeatedly as established, but the actual evidence is:
1. Two models at one training scale achieved the same score (0.458)
2. Biderman et al. [2023] show Pythia-dedup gains only ~0.01 on HellaSwag

That's it. There is no:
- HellaSwag scores across multiple checkpoints showing a saturation curve
- Evidence that other 6-8B models at ~300B tokens also plateau at 0.458
- Statistical argument that 0.458 is a "ceiling" vs. a coincidental match

The paper admits in §5.3 that "sampling variance with 500 examples could produce this exact match by coincidence (MEDIUM plausibility)" but then treats the saturation explanation as "Most likely." A skeptical reviewer will note: you have N=2 data points (one model family, one training scale) and conclude "saturation" is a general phenomenon. This is insufficient for a general claim.

**Required Fix**: Reframe the saturation finding as a hypothesis, not a conclusion: "The identical scores are *consistent with* a scale-dependent saturation effect, a hypothesis supported by [Biderman et al., 2023] showing diminishing HellaSwag sensitivity in the Pythia family. Confirming saturation as a general phenomenon requires HellaSwag scores across multiple model sizes and checkpoints." Do NOT present it as a confirmed structural fact in the Abstract without this qualification.

---

## MINOR Issues (for Human Review)

**MINOR-001**: Introduction, para 1: "one of the most carefully curated pre-training corpora to date" — superlative without citation. Should cite Soldaini et al. [2024] inline here. (grammar/citation style)

**MINOR-002**: Results §5.2, p-value footnote context missing. The sentence "The one-sided p-value... is 0.004 — far below the 0.05 threshold — but in the direction opposite to the hypothesis" is confusing without first establishing what the null hypothesis of the test is. A one-sentence setup would clarify. (clarity)

**MINOR-003**: Table 2 caption missing — there is no "Table 2:" label in the results section file as shown. Check rendering. (formatting)

**MINOR-004**: Methodology §3 uses "ID/OOD" without defining in-distribution/out-of-distribution at first use. (clarity)

**MINOR-005**: Discussion "Explanation 3" says "original contamination concern was in the opposite direction" — this is slightly confusing without more context about the pre-registration direction. (clarity)

**MINOR-006**: Related Work ends abruptly with "Positioning Our Contribution" subsection; consider adding a single transition sentence at the end leading into Methodology. (style)

---

## Bored Reviewer Engagement Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | YES | Strong hook — "found the opposite" is engaging |
| Problem clear in 1 minute? | YES | First two paragraphs establish problem clearly |
| Novelty clear in 2 minutes? | MOSTLY | Structural insight (HellaSwag saturation) takes ~3 minutes to emerge |
| Figure 1 self-explanatory? | UNKNOWN | Paper has [Figure 1] placeholders — cannot assess actual figure |
| Would continue reading? | YES | Negative result well-framed |
| Attention lost at? | "Discussion §3 saturation mechanism" — repetitive; same point made 3+ times |

**Persuasiveness Status**: PASSED (with reservation about figure placeholder state)

---

## Ground Truth Verification Log

| Claim in Paper | Paper Value | Ground Truth | Match? | Notes |
|----------------|-------------|--------------|--------|-------|
| Pythia ratio | 0.565 | 0.565 | YES | |
| OLMo ratio | 0.538 | 0.538 (0.5383 precise) | YES | Paper rounds, acceptable |
| Ratio difference | −0.0265 | −0.0265 | YES | |
| 95% CI | [−0.045, −0.007] | [−0.0447, −0.0069] | YES | Rounded, acceptable |
| Cohen's d | −2.732 | −2.732 | YES | |
| Pythia MMLU | 0.259 | 0.2588 | YES | Rounded |
| OLMo MMLU | 0.246 | 0.2463 | YES | Rounded |
| HellaSwag both | 0.458 | 0.4580 | YES | |
| p-value | 0.996 (Intro) / 0.004 (Results) | 0.996 (04_validation) / 0.004 (ground_truth.yaml) | CONFLICT | FATAL-001 |
| ARC delta Pythia | −0.334 | −0.334 | YES | |
| ARC delta OLMo | −0.344 | −0.344 | YES | |

**Overall accuracy**: Very high. No fabricated numbers. One critical p-value directional inconsistency (FATAL-001).

---

## Summary for Revision Agent

**Fix immediately (FATAL)**:
1. Standardize p-value to 0.004 throughout, with precise null-hypothesis description. Remove p=0.996 from Introduction contribution 1 or reframe explicitly as "the fraction of bootstraps where OLMo exceeds Pythia is only 0.4%" (= p=0.004 for H0: OLMo ≥ Pythia).

**Fix next (MAJOR)**:
2. Add fast-eval caveat to Abstract's HellaSwag convergence claim.
3. Soften "first evaluation" novelty claim in Introduction — add qualifier or evidence of prior search.
4. Reframe "saturation" as a hypothesis supported by evidence, not a confirmed fact — remove unqualified saturation language from Abstract.

**Collect for human review (MINOR)**:
5. MINOR-001 through MINOR-006 as listed above.

**Do NOT change**:
- All numerical results are accurate
- Limitation structure (L1–L4) is complete and well-articulated
- Negative result framing is appropriate
- Architecture confound acknowledgment is thorough
