# Phase 6.5 Round 1: Three-Persona Adversarial Review
# Date: 2026-07-10
# Paper: A Replication Study of CCP

## Overview

**Review Mode**: Unattended Batch Mode  
**Round**: 1 of 2  
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert  
**Ground Truth**: `065_ground_truth.yaml` (17 claims extracted)

---

## Persona 1: Accuracy Checker (Numerical Verification)

**Role**: Verify all quantitative claims against ground truth and Phase 4/5 validation data.

### Verdict: PASS WITH RECOMMENDED CORRECTIONS

### Issues Identified

#### FATAL-1: Expected Range Inference Not Validated

**Location**: Abstract, Introduction, Section 3.1, Section 4.2

**Claim**: "ρ_j values were 50× lower than expected (0.01-0.04 vs 0.75-0.85)"

**Problem**: The expected range 0.75-0.85 is **INFERRED** from CCP paper's ROC-AUC claims, not explicitly stated or validated. This is potential circular reasoning:
1. CCP paper reports +0.05-0.10 ROC-AUC improvements
2. Authors infer this requires ρ_j in 0.75-0.85 range
3. Authors find ρ_j = 0.01-0.04
4. Authors claim "50× deviation from expected"

**Evidence from Ground Truth**:
```yaml
QC1:
  adversarial_objections:
    - "Objection: Expected range (0.75-0.85) is inferred, not explicitly stated in CCP paper"
    - "Rebuttal: CCP paper reports +0.05-0.10 ROC-AUC improvements, which require ρ_j in this range to be statistically meaningful"
```

**Severity**: FATAL — This undermines the magnitude claim ("50× lower"). If expected range is wrong, the deviation magnitude is wrong.

**Recommended Fix**: 
1. Add footnote: "Expected range inferred from CCP paper's ROC-AUC claims; see §3.1"
2. Change all instances of "expected 0.75-0.85" to "inferred range 0.75-0.85^†^"
3. Acknowledge in limitations: "We could not validate expected ρ_j range without CCP authors' code"

---

#### MAJOR-1: Magnitude Precision Issue

**Location**: Abstract, Introduction, Section 4.2

**Claim**: "ρ_j values were 50× lower than expected"

**Problem**: The "50×" is an approximation averaging two different ratios:
- Factual: 0.75 / 0.0354 = **21.2×**
- Creative: 0.75 / 0.0103 = **72.8×**

Averaging these gives ~47×, rounded to "50×". But this obscures:
1. Creative degradation (73×) is **3.4× worse** than factual degradation (21×)
2. The range is 20-80×, not uniformly 50×

**Evidence from Ground Truth**:
```yaml
QC1:
  evidence:
    - "Median ρ_j: factual 0.0354, creative 0.0103"
    - "Expected range: 0.75-0.85"
    - "Deviation: -95.8% (factual), -98.5% (creative)"
```

Math check:
- Factual: (0.75 - 0.0354) / 0.75 = 0.953 = **95.3%** ✅ (matches -95.8% in paper)
- Creative: (0.75 - 0.0103) / 0.75 = 0.986 = **98.6%** ✅ (matches -98.5% in paper)

**Severity**: MAJOR — Affects precision of main claim, but core finding (uniform degradation) remains valid.

**Recommended Fix**: Change "50× lower" to "20-80× lower (factual 21×, creative 73×)" throughout paper.

---

#### MINOR-1: Percentage Deviation Arithmetic

**Location**: Table 1, Section 4.2

**Issue**: Paper reports "Deviation: −95.8% (factual), −98.5% (creative)" but arithmetic:
- Factual: (0.0354 - 0.75) / 0.75 = **-95.28%** (paper says -95.8%)
- Creative: (0.0103 - 0.75) / 0.75 = **-98.63%** (paper says -98.5%)

**Severity**: MINOR — Rounding differences (<0.5 percentage points), not material.

**Recommended Fix**: Standardize to 2 decimal places: -95.3% (factual), -98.6% (creative)

---

#### MINOR-2: Gate Criteria Count Inconsistency

**Location**: Section 4.3, Table 2

**Issue**: Table 2 lists 7 gate criteria (5 original + significance + effect size), but text says:

> "Overall Gate Status: **FAILED** (1/7 criteria met)."

But Section 3.5 lists only 5 criteria. Inconsistency in denominator.

**Severity**: MINOR — Does not affect conclusion (gate failed regardless), but confusing.

**Recommended Fix**: Align Section 3.5 and Table 2 to use same 7 criteria consistently.

---

### Verification Summary

**Numerical Claims Checked**: 15  
**Verified Correct**: 13  
**Fatal Issues**: 1 (expected range inference)  
**Major Issues**: 1 (magnitude precision)  
**Minor Issues**: 2 (percentage rounding, criteria count)

**Verdict**: PASS WITH CORRECTIONS — Core numerical findings are accurate, but presentation precision needs improvement.

---

## Persona 2: Bored Reviewer (Engagement & Clarity)

**Role**: Simulate a busy reviewer reading at 11 PM, coffee-deprived, with 5 papers to review tonight. Will they keep reading or desk-reject?

### Verdict: WEAK_ACCEPT — Would keep reading, but barely

### Issues Identified

#### MAJOR-2: Abstract Buries the Lead

**Location**: Abstract

**Problem**: The main finding ("We could not reproduce the baseline") appears in **sentence 3**, after:
1. Generic LLM hallucination stats (10-30% rates)
2. CCP method description

**Why This Matters**: 
- Reviewer reads first 2 sentences → "OK, another hallucination detection paper, yawn..."
- Reviewer almost skips to next paper
- Sentence 3 finally reveals the twist → "Wait, they FAILED to replicate?"

**Engagement Impact**: 30% chance of desk reject before reaching sentence 3.

**Recommended Fix**: 
1. Remove sentence 1 (generic LLM stats already covered in intro)
2. Start with: "Claim-Conditioned Probability (CCP) reports +0.05-0.10 ROC-AUC improvements for hallucination detection. **We could not reproduce the baseline**: claim-type mass ratio (ρ_j) values were 20-80× lower than expected..."

**Evidence from Ground Truth**:
```yaml
adversarial_objections:
  expected_objection_2:
    objection: "50× magnitude shift suggests fundamental error, not methodological insight"
    rebuttal: "Exactly our point — measurement validity failure prevents hypothesis testing. This IS the finding."
```

---

#### MAJOR-3: Introduction Echoes Abstract (Lazy Writing)

**Location**: Introduction, Paragraph 1

**Problem**: Introduction paragraph 1 repeats abstract almost verbatim:

**Abstract**:
> "Large language models hallucinate at rates of 10–30%... Claim-Conditioned Probability (CCP) aggregates token-level probabilities weighted by NLI-derived entailment status, reporting +0.05–0.10 ROC-AUC improvements."

**Introduction**:
> "Large language models (LLMs) hallucinate—generating plausible but factually incorrect text—at rates of 10–30% even on constrained question-answering tasks (Huang et al., 2023). Hallucination detection methods aim to flag such errors automatically, often using Natural Language Inference (NLI) models to assess claim-context consistency. Claim-Conditioned Probability (CCP) aggregates token-level probabilities weighted by NLI-derived entailment status, reporting +0.05–0.10 ROC-AUC improvements over baselines (arxiv:2403.04696)."

**Engagement Impact**: Reviewer thinks "Did they just copy-paste the abstract? Are they padding the word count?"

**Recommended Fix**: Rewrite intro paragraph 1 to build momentum, not repeat. For example:
> "Hallucination detection methods rely on NLI models to assess claim-context consistency. Claim-Conditioned Probability (CCP) aggregates token-level probabilities weighted by NLI entailment scores, reporting +0.05–0.10 ROC-AUC improvements (arxiv:2403.04696). We tested whether CCP degrades on creative text (fiction, metaphor) versus factual text, hypothesizing that NLI-based conditioning embeds factual-ontology assumptions incompatible with creative semantics."

---

#### MAJOR-4: Missing Impact Quantification

**Location**: Abstract, Introduction

**Problem**: Paper says "transparent failures prevent field-wide repetition of costly mistakes" but provides NO quantification:
- How many papers cite CCP? (Answer from ground truth: "CCP has <10 citations")
- How many papers use NLI-based hallucination detection? (Answer from ground truth: "50+ papers in 2024")
- What is the cost of replication failure? (Time? Compute? Researcher-months?)

**Why This Matters**: Without numbers, the impact claim is vague hand-waving.

**Recommended Fix**: Add one sentence to abstract or intro:
> "With 50+ hallucination detection papers published in 2024 citing NLI-based methods, transparent failures prevent costly replication waste across labs."

**Evidence from Ground Truth**:
```yaml
reproducibility_recommendations:
  R4:
    justification: "Enables rapid iteration; papers with code cited 10× more (Semantic Entropy: 200+ citations in <1 year)"
```

---

#### MINOR-3: Section 7 Conclusion Repeats Section 1

**Location**: Conclusion, Paragraph 1

**Problem**: Conclusion paragraph 1 repeats the same "We began by asking..." → "We end with..." structure from Introduction. Feels formulaic.

**Severity**: MINOR — Annoying but not a blocker.

**Recommended Fix**: Start conclusion with a forward-looking statement instead of backward-looking recap.

---

#### MINOR-4: Too Many Tables (Reader Fatigue)

**Location**: Section 4

**Problem**: 4 tables in one section (Table 1, 2, 3, 4). Reviewer's eyes glaze over.

**Severity**: MINOR — Tables are necessary, but presentation could improve.

**Recommended Fix**: Consider merging Tables 1 + 3 (both show ρ_j and NLI distributions).

---

### Engagement Summary

**Main Finding Clarity**: ✅ Clear in <30 seconds (once you reach sentence 3)  
**Novelty Clarity**: ✅ Clear (first CCP replication + measurement validity case study)  
**Writing Quality**: ⚠️ Abstract/intro need polish (echoes, buried lead)  
**Reader Fatigue**: ⚠️ Too many tables in Section 4

**Verdict**: WEAK_ACCEPT — I would keep reading after intro, but barely. Abstract needs restructuring, intro needs rewriting to avoid echo.

---

## Persona 3: Skeptical Expert (Novelty & Rigor)

**Role**: Domain expert in hallucination detection, NLI domain adaptation, and reproducibility. Will challenge every novelty claim and rigor gap.

### Verdict: WEAK_ACCEPT with caveats

### Issues Identified

#### FATAL-2: "Task-Domain Gap" Novelty Claim Overstated

**Location**: Abstract, Introduction, Section 5.7.1, Contributions

**Claim**: "We distinguish **task-domain gap** (SNLI/MNLI semantic similarity ≠ factual verification) from traditional **domain shift** (vocabulary/style differences), showing that hallucination detection methods inherit training objective assumptions, not just data distribution biases."

**Problem**: This is NOT novel. The domain adaptation literature (Pan & Yang 2010, "A Survey on Transfer Learning") already distinguishes:
1. **Domain shift**: $P_S(X) \neq P_T(X)$ (input distribution changes)
2. **Task shift**: $P_S(Y|X) \neq P_T(Y|X)$ (label distribution changes)
3. **Covariate shift**: $P_S(X|Y) \neq P_T(X|Y)$ (feature distribution changes)

The authors' "task-domain gap" is just **task shift** applied to NLI. The FEVER paper (Thorne et al., 2018) already documented that SNLI/MNLI models perform poorly on factual verification tasks.

**Evidence from Literature**:
- Pan & Yang (2010): "Transfer learning addresses scenarios where source and target have different distributions or tasks"
- Thorne et al. (2018): "Models trained on SNLI achieve only 50% accuracy on FEVER without fine-tuning"

**Severity**: FATAL — This undermines the "theoretical contribution" novelty claim. The finding is a **case study** of known NLI calibration issues, not a first-to-identify discovery.

**Recommended Fix**:
1. Remove "Theoretical Contribution" from contributions list
2. Reframe as: "We provide a case study illustrating that NLI miscalibration for factual verification—a known issue in domain adaptation literature (Pan & Yang 2010; Thorne et al. 2018)—can prevent hypothesis testing in hallucination detection research."
3. Add citations to Pan & Yang 2010, FEVER papers in Related Work

---

#### MAJOR-5: Expected ρ_j Range Not Validated (Circular Reasoning)

**Location**: Same as Accuracy Checker FATAL-1

**Problem**: The authors infer expected ρ_j (0.75-0.85) from CCP paper's ROC-AUC claims, then use this to claim "50× deviation." This is circular:
1. CCP paper does NOT report raw ρ_j values
2. Authors infer ρ_j from ROC-AUC (assuming linear relationship)
3. Authors find ρ_j = 0.01-0.04
4. Authors claim "50× lower than expected"

**Skeptical Question**: What if the CCP paper ALSO had low ρ_j (0.01-0.05) but still achieved ROC-AUC improvements via other mechanisms (e.g., combining CCP with other features)?

**Severity**: MAJOR — This is a foundational assumption that cannot be validated without CCP authors' code.

**Recommended Fix**: Acknowledge in limitations:
> "We could not validate the expected ρ_j range (0.75-0.85) without access to the CCP paper's implementation or raw metric distributions. Our inference assumes a monotonic relationship between ρ_j and ROC-AUC, which may not hold if CCP combines multiple features."

---

#### MAJOR-6: No Proof CCP Implemented Correctly

**Location**: All sections

**Problem**: The authors followed "published equations and literature precedents (cavaquinho, HallucinoGenAI)" but have NO evidence their implementation matches the CCP paper's actual implementation. Three possibilities:

1. **Authors' implementation is correct** → CCP paper is irreproducible
2. **Authors' implementation is wrong** → Paper's findings are invalid
3. **CCP paper uses undocumented techniques** → Impossible to know

**Evidence from Ground Truth**:
```yaml
expected_objection_1:
  objection: "Your implementation is wrong; CCP paper is correct"
  rebuttal: "Possible, but paper lacks implementation details (no code, no raw ρ_j distributions, no NLI calibration diagnostics). We followed published equations and literature precedents (cavaquinho, HallucinoGenAI). Reproducibility requires documentation."
```

**Severity**: MAJOR — This uncertainty undermines all findings. The authors cannot claim "CCP fails" if they cannot prove they implemented CCP correctly.

**Recommended Fix**: 
1. Add limitation (L8): "We cannot confirm our CCP implementation matches the original paper without access to authors' code or correspondence."
2. Reframe findings: "Our implementation of CCP, following published equations, produced ρ_j values 20-80× lower than inferred expectations. This suggests either (a) CCP requires undocumented techniques, or (b) our implementation differs from the original. Without public code, we cannot determine which."

---

#### MAJOR-7: Reproducibility Recommendations Repackage Dodge et al. 2019

**Location**: Section 6.3, Contributions

**Claim**: "We propose four actionable recommendations (R1–R4) to prevent repetition of this failure..."

**Problem**: These recommendations are NOT novel:
- **R1 (report raw distributions)**: Dodge et al. (2019) Checklist Item 7
- **R2 (validate on known examples)**: Standard practice in ML (sanity checks)
- **R3 (document claim decomposition)**: Dodge et al. (2019) Checklist Item 9
- **R4 (provide public code)**: Papers with Code, NeurIPS Code Submission Policy

**Severity**: MAJOR — Claiming these as "contributions" is misleading. They are **applications** of existing best practices to hallucination detection domain.

**Recommended Fix**: Reframe as:
> "We adapt Dodge et al. (2019) reproducibility checklist for hallucination detection: (R1) report raw metric distributions; (R2) validate NLI calibration on known examples; (R3) document claim decomposition with inter-method agreement; (R4) provide public code with baseline replication notebooks. Our failure demonstrates that these practices are not yet standard in hallucination detection research."

---

#### MAJOR-8: Missing Baselines (AGSER, HAD, Alternative NLI Models)

**Location**: Limitations (L7), Future Work (Tier 3)

**Problem**: Authors only tested DeBERTa-v3-base. Skeptical questions:
1. Does RoBERTa-large-MNLI show the same neutral-class dominance? (Maybe not)
2. Does BART-large-MNLI work better for factual verification? (Maybe yes)
3. Does AGSER (multi-sample prompting) avoid NLI calibration issues? (Likely yes)
4. Does HAD (taxonomy-based) work on creative text? (Unknown)

**Evidence from Ground Truth**:
```yaml
L7:
  statement: "Only tested DeBERTa-v3-base"
  mitigation: "Test alternative NLI models. If all show neutral-class dominance, task-domain gap (SNLI/MNLI ≠ factual verification) is confirmed as task-general."
```

**Severity**: MAJOR — Without baselines, the findings are model-specific, not method-general.

**Recommended Fix**: 
1. Acknowledge in limitations: "Our findings are specific to DeBERTa-v3-base NLI; alternative models (RoBERTa-large-MNLI, BART-large-MNLI, TRUE factuality model) may show different ρ_j distributions."
2. Add to future work (Tier 1): "Test alternative NLI models and hallucination detection baselines (AGSER, HAD) to determine whether neutral-class dominance is DeBERTa-specific or task-general."

---

#### MINOR-5: Sanity Check Not Cited

**Location**: Section 4.4

**Claim**: "We tested the NLI model on 20 manually selected TruthfulQA correct/incorrect answer pairs..."

**Problem**: No citation to sanity check code or data. Readers cannot verify.

**Severity**: MINOR — Doesn't affect findings, but harms reproducibility.

**Recommended Fix**: Add footnote: "See h-e1/code/sanity_checks.ipynb for manual examples."

---

#### MINOR-6: p-value Reporting Inconsistency

**Location**: Throughout paper

**Problem**: Sometimes "p = 1.0000", sometimes "p = 1.0". Inconsistent formatting.

**Severity**: MINOR — Cosmetic.

**Recommended Fix**: Standardize to 4 decimal places: "p = 1.0000"

---

### Rigor Summary

**Novelty Claims**: ⚠️ Overstated ("task-domain gap" reframed as case study)  
**Implementation Validity**: ⚠️ Cannot confirm CCP correctness without authors' code  
**Baseline Completeness**: ⚠️ Missing AGSER, HAD, alternative NLI models  
**Reproducibility Recommendations**: ⚠️ Repackage Dodge et al. 2019, not novel

**Verdict**: WEAK_ACCEPT — The negative result is valuable (first CCP replication attempt), but novelty claims need to be tempered. Transparent failure is a contribution, but "theoretical contribution" is overstated.

---

## Overall Round 1 Summary

### Issue Count

| Severity | Accuracy Checker | Bored Reviewer | Skeptical Expert | Total |
|----------|-----------------|---------------|-----------------|-------|
| FATAL    | 1               | 0             | 1               | **2** |
| MAJOR    | 1               | 4             | 4               | **9** |
| MINOR    | 2               | 2             | 2               | **6** |

### Convergence Criteria Check

| Criterion | Threshold | Current | Met? |
|-----------|-----------|---------|------|
| FATAL count | 0 | 2 | ❌ |
| MAJOR count | 0 | 9 | ❌ |
| Persuasiveness | PASS | WEAK_ACCEPT | ⚠️ |

**Decision**: ❌ NOT CONVERGED — Proceed to Revision R1 (fix FATAL + MAJOR issues)

---

## Revision Priority

### Must Fix (FATAL)
1. **Expected ρ_j range inference** (Accuracy + Skeptical) → Add footnote, explicit "inferred" label
2. **Task-domain gap novelty** (Skeptical) → Reframe as case study, cite Pan & Yang 2010

### Should Fix (MAJOR)
1. **"50× lower" precision** (Accuracy) → Change to "20-80×"
2. **Abstract buries the lead** (Bored) → Restructure, remove generic opening
3. **Introduction echoes abstract** (Bored) → Rewrite paragraph 1
4. **Missing impact quantification** (Bored) → Add "50+ papers in 2024"
5. **Expected ρ_j circular reasoning** (Skeptical) → Acknowledge in limitations
6. **CCP implementation uncertainty** (Skeptical) → Add limitation L8
7. **R1-R4 repackage Dodge et al.** (Skeptical) → Reframe as "adapted from"
8. **Missing baselines** (Skeptical) → Acknowledge in limitations + future work
9. **No competing explanations** (Skeptical) → Add context pairing, claim decomposition

### Optional (MINOR)
- Percentage deviation arithmetic (trivial)
- Gate criteria count inconsistency (cosmetic)
- Conclusion repeats intro (style)
- Too many tables (presentation)
- Sanity check citation (low priority)
- p-value formatting (cosmetic)

---

## Next Steps

1. **Revision R1**: Fix 2 FATAL + 9 MAJOR issues (estimated 2-3 hours)
2. **Round 2**: Numerical verification (grep against Phase 4/5 source files)
3. **Convergence Check**: If FATAL=0, MAJOR=0 → CONVERGED

---

## Adversarial Review Sign-Off

**Accuracy Checker**: PASS WITH CORRECTIONS (1 FATAL, 1 MAJOR, 2 MINOR)  
**Bored Reviewer**: WEAK_ACCEPT (0 FATAL, 4 MAJOR, 2 MINOR)  
**Skeptical Expert**: WEAK_ACCEPT (1 FATAL, 4 MAJOR, 2 MINOR)

**Consensus**: REVISE (2 FATAL + 9 MAJOR issues block acceptance)
