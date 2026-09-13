# Verification Plan: Bidirectional Formality Accommodation in Human-AI Dialogue

**Date:** 2026-08-10
**Hypothesis ID:** H-BiAcc-v1
**Confidence:** 0.75
**Total Hypotheses:** 5
**Mode:** Incremental (Phase 2A Available)
**Scope Reduction:** 60% (BUILD_ON claims excluded)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under multi-turn human-AI conversation settings (LMSYS-Chat-1M, ≥2 turns per side),
if AI and human formality levels converge in early turns (accommodation),
then conversation length increases (engagement),
because accommodation signals attentiveness and understanding, motivating continuation.

### 1.2 Alternative Hypothesis (H0)

There is no significant correlation between early formality accommodation and
conversation length in LMSYS-Chat-1M conversations (all |r| < 0.10).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LMSYS-Chat-1M (standard) | 1M real human-AI conversations with 25+ LLMs; multi-turn; diverse topics |
| **Model** | DeBERTa Formality Ranker | 87.8% accuracy on formality classification; continuous output for delta computation |

**Dataset Details:**
- Source: HuggingFace: lmsys/lmsys-chat-1m
- Path: https://huggingface.co/datasets/lmsys/lmsys-chat-1m

**Model Details:**
- Type: classification
- Source: HuggingFace: s-nlp/deberta-large-formality-ranker

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Chen et al. (2026) - Bidirectional accommodation measurement | Showed accommodation exists; no outcome correlation reported | WildChat (1,319 GPT-4o conversations) |
| Niederhoffer & Pennebaker (2002) - Linguistic style matching | r ~ 0.3 for style matching predicting relationship quality | Human-human conversations |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Formality accommodation generalizes from human-human to human-AI settings | Chen et al. (2026) showed accommodation exists in human-AI; generalization to outcomes untested | Hypothesis fails; accommodation may exist but not predict outcomes in human-AI |
| A2 | DeBERTa formality scores are valid proxies for perceived formality | 87.8% accuracy on formality classification task; standard in NLP | Measurement noise reduces effect sizes; may need alternative operationalization |
| A3 | Conversation length is a meaningful proxy for engagement/success | Common proxy in dialogue research; longer = more engagement (all else equal) | Length may reflect verbosity or user patience, not engagement; need alternative DV |
| A4 | Early turns (1-2) capture accommodation intent before topic complexity dominates | Chen et al. found model accommodation front-loaded in turn 1 | Need to expand window to turns 1-3 or use full-conversation measure (but circularity risk) |
| A5 | LMSYS-Chat-1M conversations are representative of real human-AI interaction | 1M conversations, 210K unique IPs, diverse topics; standard dataset | Results may not generalize to other platforms or user populations |

### 1.6 Research Gap & Novelty

**Gap:** Prior work (Chen et al. 2026) showed accommodation EXISTS in human-AI dialogue but did not test whether accommodation PREDICTS outcomes.

**Novelty:**
- First test of accommodation→outcome link in human-AI (not just existence)
- Bidirectional decomposition with directional predictions (AI→H vs H→AI)
- 25+ LLM cross-comparison at unprecedented scale

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Accommodation Patterns Detectable in LMSYS-Chat-1M

**Type:** EXISTENCE
**Statement:** Under LMSYS-Chat-1M multi-turn conversations (≥2 turns per side), if we apply DeBERTa formality scoring, then formality accommodation patterns are measurable with coverage ≥50% and observed deltas < shuffled baseline, because multi-turn dialogue inherently involves mutual adaptation.

**Rationale:**
This is the precondition test. If accommodation cannot be detected in the dataset, the main hypothesis is untestable. We must verify adequate coverage and that observed accommodation exceeds random chance.

**Variables:**
- Independent: Turn formality scores (DeBERTa output)
- Dependent: Accommodation detectability (coverage %, delta vs shuffled)
- Controlled: Turn count threshold (≥2 per side)

**Verification Protocol:**
1. Download LMSYS-Chat-1M and filter to ≥2 turns per participant side
2. Apply DeBERTa formality scorer to all turns; compute coverage percentage
3. Calculate |formality(AI_2) - formality(Human_1)| for observed pairs
4. Generate shuffled baseline by randomizing turn pairings
5. Compare observed vs shuffled using Cohen's d

**Success Criteria (PoC: Direction-based):**
- Primary: Coverage ≥ 50% of conversations meet turn threshold
- Secondary: Cohen's d > 0.3 (observed < shuffled)

**Failure Response:**
- IF fails: PIVOT to alternative dataset (WildChat) or relax turn threshold

**Dependencies:** None

**Source:** Phase 2A SH1 (sh1_existence)

---

#### H-M1: Human Initial Formality Captured

**Type:** MECHANISM
**Statement:** Under LMSYS-Chat-1M conversations, if a human sends an initial message, then DeBERTa assigns a formality score with non-trivial variance (SD > 0.1), because users exhibit diverse communication styles.

**Rationale:**
This is the first causal step. If all human messages have the same formality, there's nothing to accommodate. We need variance in the input to test accommodation.

**Variables:**
- Independent: Human turn 1 text
- Dependent: Formality score and variance
- Controlled: Language (English only)

**Verification Protocol:**
1. Sample 10,000 random first human turns from dataset
2. Score each with DeBERTa formality model
3. Calculate mean, SD, and distribution shape
4. Verify SD > 0.1 (non-trivial variance)

**Success Criteria (PoC: Direction-based):**
- Primary: SD(formality_human_1) > 0.1
- Secondary: Distribution not bimodal (suggests meaningful continuous scale)

**Failure Response:**
- IF fails: EXPLORE alternative formality measures or categorical binning

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: AI Formality Response Varies

**Type:** MECHANISM
**Statement:** Under multi-turn conversations, if an AI responds to a human message, then AI formality varies as a function of human formality (correlation |r| > 0.1), because LLMs adapt their style to conversational context.

**Rationale:**
Tests whether AI actually accommodates. If AI formality is constant regardless of human input, there's no accommodation to measure effects of.

**Variables:**
- Independent: Human turn 1 formality
- Dependent: AI turn 1 formality
- Controlled: Model ID (stratified analysis)

**Verification Protocol:**
1. For each conversation, extract (formality_human_1, formality_AI_1) pair
2. Calculate Pearson correlation across all conversations
3. Stratify by model ID to check cross-model consistency
4. Test significance with N > 100,000

**Success Criteria (PoC: Direction-based):**
- Primary: |r(formality_human_1, formality_AI_1)| > 0.1, p < 0.001
- Secondary: Consistent direction across majority of models

**Failure Response:**
- IF fails: EXPLORE per-model analysis (some models may not accommodate)

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Lower Delta Signals Accommodation

**Type:** MECHANISM
**Statement:** Under conversations where AI formality delta is small, if we measure perceived attentiveness proxies, then attentiveness indicators correlate with small deltas, because accommodation signals engagement per Communication Accommodation Theory.

**Rationale:**
This step links the observed accommodation (low delta) to the theoretical mechanism (attentiveness). Without this, correlation with length could be spurious.

**Variables:**
- Independent: |formality(AI_2) - formality(Human_1)|
- Dependent: Continuation probability (proxy for perceived attentiveness)
- Controlled: Conversation length at measurement point

**Verification Protocol:**
1. Split conversations into accommodation terciles by delta
2. Calculate continuation rate (proportion reaching turn 3+) per tercile
3. Test monotonic relationship: low delta → higher continuation
4. Control for initial human message length as potential confound

**Success Criteria (PoC: Direction-based):**
- Primary: Lowest delta tercile has highest continuation rate
- Secondary: Monotonic trend across terciles

**Failure Response:**
- IF fails: PIVOT to alternative proxies (response time, thumbs up/down if available)

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Accommodation Predicts Conversation Length

**Type:** MECHANISM
**Statement:** Under LMSYS-Chat-1M multi-turn conversations, if early accommodation (low |formality_delta|) is observed, then conversation length increases, because accommodation signals attentiveness and understanding, motivating continuation.

**Rationale:**
This is the main prediction. All prior steps build to this: does accommodation actually predict the outcome we care about?

**Variables:**
- Independent: AI→Human accommodation (|formality(AI_2) - formality(Human_1)|)
- Dependent: Conversation length (total turn pairs)
- Controlled: Model ID, initial formality level

**Verification Protocol:**
1. Compute early accommodation delta for all qualifying conversations
2. Correlate with total conversation length
3. Apply partial correlation controlling for model ID and initial formality
4. Test bidirectional: repeat for Human→AI direction
5. Compare effect sizes and signs for AI→H vs H→AI

**Success Criteria (PoC: Direction-based):**
- Primary: r(AI→H_delta, length) < -0.15 (negative = smaller delta = longer; p < 0.001, N > 100,000)
- Secondary: AI→H and H→AI effects distinguishable (|Δr| > 0.10 or different signs)

**Failure Response:**
- IF fails: Document as negative result; explore moderators (model type, topic)

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4 + Primary Prediction P1

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Coverage ≥50%, d > 0.3 | STOP: Reassess dataset/hypothesis |
| H-M1 | MUST_WORK | SD > 0.1 | PIVOT: Alternative formality measure |
| H-M2 | SHOULD_WORK | \|r\| > 0.1 | EXPLORE: Per-model analysis |
| H-M3 | SHOULD_WORK | Monotonic tercile trend | PIVOT: Alternative proxies |
| H-M4 | SHOULD_WORK | r < -0.15, p < 0.001 | Document negative result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Human-AI accommodation differs from human-human | A1 | H-M3, H-M4 | High |
| R2: DeBERTa noise obscures effects | A2 | H-M1, H-M2, H-M3, H-M4 | Medium |
| R3: Length is poor engagement proxy | A3 | H-M4 | Medium |
| R4: Early turns insufficient | A4 | H-M3, H-M4 | Medium |
| R5: Dataset not representative | A5 | All | Low |

### 4.2 Mitigation Strategies

**R1 (High): Human-AI Generalization Risk**
- Prevention: Review Chen et al. (2026) evidence carefully before proceeding
- Detection: Compare effect sizes to Niederhoffer & Pennebaker (2002) r ~ 0.3
- Response: If effects much weaker, document as domain difference finding

**R2 (Medium): Measurement Noise**
- Prevention: Use well-validated DeBERTa model with 87.8% accuracy
- Detection: Check score distributions for anomalies
- Response: PIVOT to alternative models (RoBERTa formality) if needed

**R3 (Medium): Length Proxy Validity**
- Prevention: Acknowledge limitation upfront
- Detection: Check for length ceiling effects in data
- Response: EXPLORE alternative DVs if available (ratings, repeats)

**R4 (Medium): Early Turn Window**
- Prevention: Base on Chen et al. finding of front-loaded accommodation
- Detection: Check accommodation signal at turns 1-2 vs 1-3
- Response: Expand window if signal too weak

**R5 (Low): Dataset Representativeness**
- Prevention: LMSYS is standard; 1M conversations, 210K IPs
- Detection: Compare to WildChat patterns if available
- Response: Acknowledge as limitation in paper

### 4.3 Risk Summary

| Severity | Count | Hypotheses Affected |
|----------|-------|---------------------|
| High | 1 | H-M3, H-M4 |
| Medium | 3 | All H-M |
| Low | 1 | All |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1-4 - Mechanisms]
    H-M1 ← H-E1 (Human formality variance)
         │
         ▼
    H-M2 ← H-M1 (AI formality response)
         │
         ▼
    H-M3 ← H-M2 (Delta signals attentiveness)
         │
         ▼
    H-M4 ← H-M3 (Accommodation predicts length)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3      │ W4      │ W5      │ W6
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation │         │         │         │         │
  H-E1              │ ████████│         │         │         │
  [Gate 1]          │        ◆│         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms │         │         │         │         │
  H-M1              │         │ ████    │         │         │
  H-M2              │         │         │ ████    │         │
  H-M3              │         │         │         │ ████    │
  H-M4              │         │         │         │         │ ████
  [Gate 2]          │         │         │         │         │    ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

- **Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- **Total Duration:** 6 weeks (2 + 4)
- **Slack Available:** 0 weeks (all sequential)
- **Parallelization:** None possible in this hypothesis chain

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Early bidirectional formality accommodation predicts conversation continuation in human-AI dialogue.

**Supporting Evidence:**
1. Communication Accommodation Theory (Giles, 1973) establishes theoretical basis
2. Niederhoffer & Pennebaker (2002) showed r ~ 0.3 in human-human settings
3. Chen et al. (2026) demonstrated accommodation exists in human-AI

**Strengths:**
- Grounded in established sociolinguistic theory
- Clear 4-step causal chain with testable intermediate steps
- Large-scale dataset (1M conversations) enables robust statistical tests

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant correlation between early formality accommodation and conversation length (all |r| < 0.10).

**Counter-Arguments:**
1. Human-AI differs from human-human; users may not care about AI accommodation
2. Length may reflect task complexity, not engagement (confound)
3. DeBERTa may not capture perceptually-relevant formality differences

**Conditions Under Which H0 Would Be Supported:**
- H-E1 fails: Accommodation not measurable in dataset
- H-M2 fails: AI formality constant regardless of human input
- H-M4 fails: r ≥ -0.10 or p ≥ 0.05

### 6.3 Synthesis

The verification plan addresses this dialectic through:

1. **Foundation verification (H-E1):** Establishes accommodation is detectable before testing effects
2. **Sequential mechanism testing (H-M1-4):** Tests each causal step independently
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- H-M4 achieves r < -0.15, p < 0.001
- Effect size comparable to human-human benchmarks

**Conditions for Antithesis Support:**
- H-E1 fails: Accommodation not measurable
- H-M1 or H-M2 fails: Mechanism preconditions not met
- H-M4 r ≥ -0.10: Effect too small to be meaningful

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** H-M4 shows r ~ -0.12 → Effect exists but weaker than human-human
3. **Directional Discovery:** AI→H and H→AI have opposite signs → Novel finding
4. **No Support:** H-E1 or H-M1 fail → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Accommodation detectable | May be measurement artifact | H-E1 shuffled baseline |
| Mechanism | 4-step causal chain | Alternative explanations exist | H-M1-4 sequential tests |
| Effect Size | r < -0.15 | May be too small for practical significance | Compare to human-human r ~ 0.3 |
| Generalization | LMSYS representative | Platform-specific effects | Acknowledge as limitation |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** Early bidirectional formality accommodation predicts conversation length in LMSYS-Chat-1M
- ID: H-BiAcc-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available, 60% scope reduction)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (MUST_WORK: H-E1, H-M1)

**Risk Assessment:** Medium
- Primary concerns: Human-AI generalization (R1), measurement noise (R2)

**Immediate Action:** Begin Phase 1 with H-E1 (dataset coverage and accommodation detectability)

### Key Achievements

- 5 hypotheses across 2 phases defined with clear verification protocols
- H0 explicitly addressed: r < 0.10 = null supported
- Scope reduced 60% by building on established facts (accommodation exists, tools validated)

### Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Verify accommodation patterns detectable in LMSYS-Chat-1M
- Gate 1: MUST PASS (≥50% coverage, d > 0.3)

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Human formality variance (SD > 0.1)
- H-M2: AI formality response correlation (|r| > 0.1)
- H-M3: Delta signals attentiveness (monotonic tercile)
- H-M4: Accommodation predicts length (r < -0.15)
- Gate 2: H-M1 must pass; later failures = documented limitations

### Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis or dataset
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL (H-M1) → Execute PIVOT response
   - OPTIONAL FAIL (H-M2-4) → Document limitation, continue

### Open Questions

- What is the actual turn-count distribution in LMSYS-Chat-1M? (precondition test)
- Do different model families show different accommodation patterns?
- Can user intent be inferred from conversation metadata to control the confound?

### Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (dataset download, filtering, coverage check)
   - Set up DeBERTa formality scoring infrastructure

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Reserve 1-2 weeks buffer for PIVOT strategies if needed

3. **Failure Management:**
   - Document all failures with specific metrics
   - Execute PIVOT/EXPLORE strategies per hypothesis specs

---

## Appendices

### A. Phase 2A Reference

- **Source:** 03_refinement.yaml (H-BiAcc-v1)
- **Workflow:** phase2a-dialogue
- **Convergence:** All 6 criteria met at Exchange 16

### B. MCP Tool Usage Summary

- **Total MCP calls:** 1 (scientificmethod for hypothesis verification)
- **Mode:** Incremental (reduced from 10-14 comprehensive)

### C. Established Facts (BUILD_ON - Not Re-Verified)

1. Bidirectional accommodation exists in human-AI conversations (Chen et al. 2026)
2. LMSYS-Chat-1M contains 1M+ real conversations with 25+ LLMs (Zheng et al. 2023)
3. DeBERTa formality detection achieves 87.8% accuracy (s-nlp model)

---

*Generated by Phase 2B Planning Workflow*
*Next: Phase 2C Experiment Design (/phase2c-experiment-design or /hypothesis-next)*
