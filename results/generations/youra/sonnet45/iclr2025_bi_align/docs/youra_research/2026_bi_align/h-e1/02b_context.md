# H-E1 Context: Linguistic Marker Extraction Feasibility

**Generated:** 2026-03-17
**Source:** Phase 2B Verification Plan (Section 2.2)
**Hypothesis Type:** EXISTENCE
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under HH-RLHF dataset conditions (161K preference pairs), if linguistic agency markers (modal verbs, hedging, alternative-framing) are extracted using standard NLP tools (spaCy, NLTK, regex), then these markers will demonstrate sufficient distributional variance (CV > 0.3) and measurement reliability across all three dataset splits (helpful-base, helpful-online, helpful-RS).

---

## Rationale

This hypothesis validates the fundamental feasibility of the measurement approach. Without sufficient marker variance, correlation analysis with RLHF preference status becomes impossible. Success establishes that agency-relevant linguistic features exist in RLHF data and can be reliably measured computationally.

---

## Variables

**Independent:** None (descriptive study)

**Dependent:**
- modal_verb_frequency (per 100 words)
- hedging_marker_frequency (per 100 words)
- alternative_framing_frequency (per 100 words)

**Controlled:**
- response_length (via normalization)

---

## Success Criteria

**Primary:** Modal verb CV > 0.3 (sufficient variance for correlation tests)

**Secondary:**
- Hedging CV > 0.2 (convergent evidence)
- Alternatives CV > 0.2 (convergent evidence)

**Tertiary:** Extraction precision > 90% on validation subset

---

## Gate Condition

**Type:** MUST_WORK

**Pass Condition:** CV > 0.3, precision > 90%

**If Fail:** STOP - reassess entire hypothesis, markers unmeasurable or tools unreliable → Cannot proceed to mechanism testing (H-M fails) → PIVOT to different linguistic features or ABANDON computational proxy approach

---

## Verification Protocol

1. Download HH-RLHF dataset (3 splits) and extract all response texts (~322K responses from 161K pairs)
2. Implement extraction pipeline: spaCy POS tagging for modals, NLTK lexicon for hedging, regex for alternatives
3. Normalize counts to per-100-words metric and compute distributional statistics (mean, SD, CV) for each marker
4. Manual validation on 100-sample subset to verify extraction precision/recall (target: >90% accuracy)
5. Stratified analysis across splits to confirm measurement consistency

---

## Dataset Specification (from Phase 2B Section 1.3)

**Dataset:** Anthropic HH-RLHF (standard)

**Source:** HuggingFace: Anthropic/hh-rlhf

**Path:** https://huggingface.co/datasets/Anthropic/hh-rlhf

**Details:**
- 161K preference pairs (chosen vs rejected)
- Three splits: helpful-base, helpful-online, helpful-RS
- Conversation context included
- Publicly available, peer-reviewed methodology

**Justification:** Perfect for matched-pair linguistic analysis with cross-validation capability

---

## Model Specification (from Phase 2B Section 1.3)

**Type:** linguistic_analysis

**Model:** N/A - Analysis only

**Details:** This is a measurement study, not a model training study. We extract linguistic features from static text data using NLP tools (spaCy, NLTK, regex).

---

## Key Assumptions

**A1: Proxy Validity**
- Assumption: Linguistic markers in AI responses correlate with human agency preservation
- Evidence: Juanchich 2017 (modal verbs/pronouns indicate autonomy attribution), Biber et al. 1999 (hedging marks epistemic stance)
- If Violated: Markers measure something else (construct validation checks test this)

**A2: Dataset Quality**
- Assumption: HH-RLHF annotations reflect genuine human preferences
- Evidence: Anthropic 2022 dataset paper, widely used in RLHF research
- If Violated: Results don't generalize beyond HH-RLHF

**A3: Matched-Pair Design**
- Assumption: Preference pair structure controls for content
- Evidence: Same conversation context, standard experimental design
- If Violated: Confounds from topic/context differences

**A4: Statistical Power**
- Assumption: N=161K ensures power > 0.99 for d=0.15
- Evidence: Power analysis
- If Violated: False negatives unlikely given massive sample size

---

## Prerequisites

None (foundation hypothesis)

---

## Dependent Hypotheses

**H-M-integrated** (MECHANISM) - requires H-E1 validation before execution

---

## Risk Factors

**R1: Proxy validity failure** (HIGH)
- Mitigation: Convergent validity (Cronbach's α), known-groups, user study fallback

**R2: Annotation artifacts** (MEDIUM)
- Mitigation: Cross-dataset replication, acknowledge limitation

**R3: Content confounds** (HIGH)
- Mitigation: Partial correlation controls, matched-pair verification

---

## Research Gap & Novelty

**Gap:** Bidirectional alignment framework (Shen et al. 2024) lacks computational operationalization for Human→AI dimension. Current RLHF evaluation focuses exclusively on AI-side metrics (helpfulness, harmlessness), with 0% coverage of human agency preservation.

**Novelty:** First computational proxy for Human→AI alignment dimension via linguistic markers.

**Differentiation:**
- vs Shen et al. 2024: They provide conceptual framework; we operationalize computationally
- vs Juanchich 2017: They study human language in psychology; we apply to AI responses in RLHF

---

*Generated from Phase 2B Verification Plan | Schema v3.5*
