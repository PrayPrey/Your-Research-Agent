# Verification Plan: Linguistic Agency Markers in RLHF Evaluation

**Date:** 2026-03-17
**Hypothesis ID:** H-AgencyRLHF-v1
**Confidence:** 0.75
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under RLHF evaluation conditions (HH-RLHF dataset with 161K human preference pairs), if computational linguistic markers operationalizing human agency preservation (modal verbs, hedging language, alternative-framing phrases) are extracted from chosen vs rejected responses, then these markers will demonstrate (1) sufficient distributional variance (CV > 0.3), (2) systematic directional association with RLHF preference status (paired t-test p < 0.05, Cohen's d ≥ 0.15), (3) internal consistency as a construct (Cronbach's α > 0.7), and (4) cross-dataset replication across at least 2 of 3 HH-RLHF splits, because RLHF optimization prioritizes efficient task resolution over option presentation, reducing autonomy-preserving linguistic features in chosen responses.

### 1.2 Alternative Hypothesis (H0)

There is no systematic difference in linguistic agency marker frequencies (modal verbs, hedging, alternative-framing) between RLHF-chosen and RLHF-rejected responses when controlling for response length, conversation turn, and topic category.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic HH-RLHF (standard) | Contains 161K preference pairs (chosen vs rejected) with conversation context - perfect for matched-pair linguistic analysis. Three splits (base, online, RS) enable cross-validation. Publicly available, peer-reviewed methodology, widely used in alignment research. |
| **Model** | N/A - Analysis only | This is a measurement study, not a model training study. We extract linguistic features from static text data. |

**Dataset Details:**
- Source: HuggingFace: Anthropic/hh-rlhf
- Path: https://huggingface.co/datasets/Anthropic/hh-rlhf

**Model Details:**
- Type: linguistic_analysis
- Source: No model training - pure NLP feature extraction from existing text

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard RLHF evaluation (helpfulness, harmlessness, honesty metrics) | Measures AI-side properties only | AlpacaEval, MT-Bench, HH-RLHF annotations |

**Why Insufficient:** No metrics for human-side effects (agency preservation, critical thinking capacity) - misses bidirectional dimension

**Best Baseline Performance:** 0% coverage of Human→AI alignment dimension (no existing metrics for agency preservation)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Linguistic markers in AI responses correlate with human agency preservation (proxy validity) | Juanchich 2017 (modal verbs/pronouns indicate autonomy attribution), Biber et al. 1999 (hedging marks epistemic stance), behavioral economics choice architecture literature | Markers measure something else (e.g., response quality, politeness) - construct validation checks test this |
| A2 | HH-RLHF annotations reflect genuine human preferences, not annotation artifacts | Anthropic 2022 dataset paper, peer-reviewed methodology, widely used in RLHF research | Results don't generalize beyond HH-RLHF dataset - acknowledged limitation |
| A3 | Preference pair structure controls for content (matched-pair design validity) | Same conversation context, only differ in chosen/rejected status - standard experimental design | Confounds from topic/context differences - mitigated by within-pair comparison |
| A4 | Statistical power sufficient for small effects (N=161K ensures power > 0.99 for d=0.15) | Power analysis: N=161K pairs, paired design, effect size d=0.15, α=0.05 → power > 0.99 | False negatives unlikely given massive sample size |
| A5 | English linguistic patterns generalize across HH-RLHF conversation types (helpful-base, online, RS) | All three splits use same language (English), same domain (helpfulness), same annotation protocol | Results limited to specific RLHF training procedure - cross-validation tests this |

### 1.6 Research Gap & Novelty

**Gap:** Bidirectional alignment framework (Shen et al. 2024) lacks computational operationalization for Human→AI dimension. Current RLHF evaluation focuses exclusively on AI-side metrics (helpfulness, harmlessness), with 0% coverage of human agency preservation.

**Novelty:** First computational proxy for Human→AI alignment dimension. Bridges three established domains (bidirectional framework + linguistic markers + RLHF evaluation) in novel integration. Zero prior work applies linguistic markers to RLHF agency measurement.

**Differentiation:**
- vs Shen et al. 2024: They provide conceptual framework; we operationalize computationally
- vs Shapira et al. 2026: They explain sycophancy mechanism; we measure via linguistic proxies
- vs Juanchich 2017: They study human language in psychology; we apply to AI responses in RLHF
- vs Constitutional AI: They automate harmlessness; we do it for agency (orthogonal dimension)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M-integrated | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Linguistic Marker Extraction Feasibility

**Type:** EXISTENCE

**Statement:** Under HH-RLHF dataset conditions (161K preference pairs), if linguistic agency markers (modal verbs, hedging, alternative-framing) are extracted using standard NLP tools (spaCy, NLTK, regex), then these markers will demonstrate sufficient distributional variance (CV > 0.3) and measurement reliability across all three dataset splits (helpful-base, helpful-online, helpful-RS).

**Rationale:** This hypothesis validates the fundamental feasibility of the measurement approach. Without sufficient marker variance, correlation analysis with RLHF preference status becomes impossible. Success establishes that agency-relevant linguistic features exist in RLHF data and can be reliably measured computationally.

**Variables:**
- Independent: None (descriptive study)
- Dependent: modal_verb_frequency, hedging_marker_frequency, alternative_framing_frequency (all per 100 words)
- Controlled: response_length (via normalization)

**Success Criteria:**
- Primary: Modal verb CV > 0.3 (sufficient variance for correlation tests)
- Secondary: Hedging CV > 0.2, alternatives CV > 0.2 (convergent evidence)
- Tertiary: Extraction precision > 90% on validation subset

**Gate:**
- Type: MUST_WORK
- If Fail: STOP - reassess entire hypothesis, markers unmeasurable or tools unreliable → Cannot proceed to mechanism testing (H-M fails) → PIVOT to different linguistic features or ABANDON computational proxy approach

**Prerequisites:** None (foundation)

**Verification Protocol:**
1. Download HH-RLHF dataset (3 splits) and extract all response texts (~322K responses from 161K pairs).
2. Implement extraction pipeline: spaCy POS tagging for modals, NLTK lexicon for hedging, regex for alternatives.
3. Normalize counts to per-100-words metric and compute distributional statistics (mean, SD, CV) for each marker.
4. Manual validation on 100-sample subset to verify extraction precision/recall (target: >90% accuracy).
5. Stratified analysis across splits to confirm measurement consistency.

**Source:** Phase 2A Section 5 (SH1: sh1_existence)

---

#### H-M-integrated: RLHF-Linguistic Marker Causal Mechanism

**Type:** MECHANISM

**Statement:** Under HH-RLHF evaluation conditions, if linguistic agency markers are extracted from 161K chosen-rejected response pairs, then chosen responses will exhibit systematically lower marker frequencies (modal verbs, hedging, alternatives) with small-to-medium effect (Cohen's d ≥ 0.15, p < 0.05, chosen < rejected), internal consistency across markers (Cronbach's α > 0.7), and cross-dataset replication (2/3 splits), because the 4-step causal chain (RLHF optimization → efficiency preference → directness priority → reduced markers) operates as theorized.

**Rationale:** This integrated hypothesis tests the full causal mechanism linking RLHF optimization to linguistic manifestations of agency preservation. It validates the core theoretical claim that RLHF's preference for efficient task resolution systematically reduces autonomy-preserving language. Success provides the first computational operationalization of Human→AI alignment dimension (bidirectional framework). Includes construct validation (Cronbach's α) and robustness checks (cross-split replication).

**Variables:**
- Independent: RLHF_preference_status (chosen=1, rejected=0)
- Dependent (Primary): modal_verb_frequency (per 100 words, chosen vs rejected)
- Dependent (Secondary): hedging_marker_frequency, alternative_framing_frequency
- Controlled: response_length (via normalization + paired design), conversation_turn (partial correlation), topic_category (stratified analysis)

**Success Criteria:**
- Primary (P1): Modal verb frequency chosen < rejected, p < 0.05, Cohen's d ≥ 0.15
- Secondary (P2): Internal consistency Cronbach's α > 0.7 (convergent validity across markers)
- Tertiary (P3): Replication in at least 2 of 3 splits (p < 0.05, d ≥ 0.15)

**Gate:**
- Type: MUST_WORK
- If Fail: Mechanism doesn't operate as theorized OR proxy validity invalid → PIVOT to direct user studies for agency measurement OR EXPLORE alternative linguistic markers OR ABANDON computational proxy approach entirely

**Prerequisites:** H-E1 (requires validated marker extraction)

**Verification Protocol:**
1. Extract markers from all chosen and rejected responses using H-E1 validated pipeline (161K pairs).
2. Conduct paired t-test on modal verb frequency (within-pair differences, test if mean < 0).
3. Calculate Cohen's d effect size for paired samples (mean difference / SD of differences).
4. Compute Cronbach's alpha across three marker types to test internal consistency as construct.
5. Partial correlation analysis to control for response length, conversation turn, topic category.
6. Cross-validation: repeat paired t-test separately for each split (helpful-base, helpful-online, helpful-RS).
7. Visualize results: forest plot of effect sizes by split, density plots of marker distributions by preference status.

**Source:** Phase 2A Sections 1.3 (Causal Mechanism 4-step chain), 1.6 (Predictions P1-P3), 5 (SH2: sh2_mechanism)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M-integrated
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | CV > 0.3, precision > 90% | STOP - reassess entire hypothesis |
| H-M-integrated | MUST_WORK | p < 0.05, d ≥ 0.15, α > 0.7, 2/3 splits pass | PIVOT to alternatives OR ABANDON |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanism | H-M-integrated | 1 week |

**Total Duration:** 3 weeks

---

## 4. Risk Analysis

### 4.1 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Proxy validity failure | A1 | HIGH | H-E1, H-M-integrated | Convergent validity (Cronbach's α), known-groups, user study fallback |
| R2 | Annotation artifacts | A2 | MEDIUM | H-M-integrated | Cross-dataset replication (Stanford SHP), acknowledge limitation |
| R3 | Content confounds | A3 | HIGH | H-M-integrated | Partial correlation controls, propensity matching, matched-pair verification |
| R4 | Insufficient power | A4 | MEDIUM | H-M-integrated | Pool splits if needed, report CIs, d=0.10 fallback threshold |
| R5 | Generalization failure | A5 | MEDIUM | H-M-integrated (P3) | 2/3 threshold, heterogeneity analysis, boundary investigation |

**Critical Risks:** 0
**High Risks:** 2 (R1: proxy validity, R3: content confounds)
**Medium Risks:** 3 (R2, R4, R5)
**Low Risks:** 0

### 4.2 Mitigation Strategies

**R1: Proxy Validity Failure (HIGH)**
- Prevention: Build convergent validity into design (Cronbach's α across markers, known-groups discrimination)
- Detection: Check if markers show inconsistent directions, compute inter-marker correlations
- Response: PIVOT to small user study (N=100) validation, or SCOPE to "linguistic pattern analysis"
- Early Warning: Cronbach's α < 0.7, markers uncorrelated

**R3: Content Confound Leakage (HIGH)**
- Prevention: Partial correlation controls (length, turn, topic), verify matched pairs
- Detection: Check chosen-rejected differences on control variables (should be minimal)
- Response: PIVOT to propensity score matching, or SCOPE to "association" not "causal effect"
- Early Warning: Chosen responses systematically longer/shorter, effect disappears with length control

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 2 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1: Linguistic Marker Extraction Feasibility
    │ Gate: MUST_WORK (CV > 0.3, precision > 90%)
    │ If FAIL → STOP (markers unmeasurable)
    │
    ▼
[Level 1 - Core Mechanism]
    H-M-integrated: RLHF-Linguistic Marker Causal Mechanism
    │ Gate: MUST_WORK (p < 0.05, d ≥ 0.15, α > 0.7, 2/3 splits)
    │ Prerequisites: H-E1
    │ If FAIL → PIVOT or ABANDON
    │
    ▼
[Terminal - PoC Complete]
    ✓ Bidirectional alignment operationalization validated

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated (sequential)
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 2 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3      │
─────────────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │
  [Gate 1]       │        ◆│         │
─────────────────┼─────────┼─────────┤
PHASE 2: Mechanism
  H-M-integrated │         │ ████    │
  [Gate 2]       │         │        ◆│
─────────────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 3 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Claim:** RLHF-chosen responses exhibit systematically lower linguistic agency markers than rejected responses, providing first computational operationalization of Human→AI alignment dimension via the 4-step causal mechanism.

**Strengths:**
- Grounded in established theory from 3 domains (RLHF, linguistics, behavioral economics)
- Clear 4-step causal chain with falsifiers at each step
- Massive sample size (N=161K) ensures statistical power
- Built-in construct validation (Cronbach's alpha, cross-validation)
- First computational proxy for Human→AI alignment dimension
- Scalable without human annotation

**Weaknesses:**
- Proxy validity assumption (A1) - markers may measure politeness not agency
- HH-RLHF-specific findings may not generalize
- No direct user study validation of proxy
- Small effect size threshold (d=0.15) may be noise
- English-only limits cross-lingual applicability

### 6.2 Antithesis (H0)

**Claim:** No systematic difference in linguistic agency markers between chosen/rejected responses. Observed patterns reflect confounds (politeness, quality, length) rather than agency preservation.

**Counter-Arguments:**
- Proxy validity unverified in RLHF context
- Multiple unmeasured confounds (user expertise, task complexity)
- HH-RLHF annotations may reflect protocol artifacts
- Small effect size (d=0.15) within measurement noise
- Cross-domain transfer (psychology→AI) questionable

**Strengths:**
- Identifies critical proxy validity assumption
- Highlights unmeasured confounds
- Questions cross-domain transfer validity
- Conservative null appropriate for novel claim

**Weaknesses:**
- Doesn't explain why markers would correlate if pure noise
- Ignores convergent validity design
- Assumes confounds dominate despite matched-pair design
- No alternative explanation for expected patterns

### 6.3 Synthesis

**Resolution:** The verification plan resolves the thesis-antithesis dialectic through sequential hypothesis testing with built-in construct validation, allowing empirical adjudication between competing interpretations while acknowledging proxy validity as testable assumption rather than fatal flaw.

**Balanced Assessment:**
The hypothesis H-AgencyRLHF-v1 presents a testable claim grounded in three domains. However, the null hypothesis raises valid concerns regarding proxy validity and confounds. The verification plan addresses this through:

1. **Foundation verification (H-E1):** Establishes marker existence/variance before testing mechanism
2. **Construct validation:** Cronbach's α tests if markers measure same construct
3. **Gate conditions:** Allow early detection of null hypothesis support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass
- Effect size meaningful (d≥0.15) with high internal consistency (α>0.7)
- Cross-validation succeeds (2/3 splits)

**Conditions for Antithesis Support:**
- H-E1 fails (CV<0.3) - markers lack variance
- H-M fails critical tests (p>0.05, d<0.15)
- Construct invalid (α<0.7)
- No cross-split replication

**Nuanced Outcomes:**
- **Full Support:** All hypotheses pass → Thesis validated, computational proxy approach proven
- **Partial Support:** Some tests fail → Refined thesis with boundary conditions identified
- **Null Support:** Critical gates fail → Antithesis validated, proxy approach invalid, direct user studies required

**Value Regardless of Outcome:** Thesis validates scalable computational approach; Antithesis identifies limits requiring direct validation.

---

## 7. Executive Summary

**Main Hypothesis:** Linguistic agency markers in RLHF responses operationalize Human→AI alignment dimension
- ID: H-AgencyRLHF-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A-driven)
- Sub-Hypotheses: 2 total (H-E1: Existence, H-M-integrated: Mechanism)
- Phases: 2 phases over 3 weeks
- Critical Gates: 2 MUST_WORK decision points

**Risk Assessment:** HIGH (2 high-severity risks: R1 proxy validity, R3 content confounds)
- Primary mitigation: Convergent validity (Cronbach's α, cross-validation, matched-pair design)

**Immediate Action:** Begin Phase 1 with H-E1 marker extraction validation

**Next Steps:**
1. Run Phase 2C for h-e1 to generate detailed experiment brief
2. Phase 3 creates implementation plans (PRD, Architecture, Logic, Config)
3. Phase 4 implements and validates hypotheses with gate checks

---

*Generated by YouRA Phase 2B Planning v7.7.0 | 2026-03-17*
