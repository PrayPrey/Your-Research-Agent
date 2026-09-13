# Verification Plan: Calibration Inversion as Behavioral Marker for Bidirectional Task Classification

**Date:** 2026-08-19
**Hypothesis ID:** H-BiDir-Cal-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under existing RLHF benchmarks (TruthfulQA, ETHICS, HHH), if we cluster tasks by calibration inversion patterns (where models show high confidence on incorrect answers), then these clusters will correlate significantly with theoretically-expected bidirectional task features (r > 0.4), because RLHF's reward modeling conflates "correct output" with "user-state-modeling-required output."

### 1.2 Alternative Hypothesis (H0)

There is no significant correlation between calibration inversion clusters and bidirectional task features, OR the correlation with bidirectional features does not exceed correlation with control features (length, topic, format).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Combined RLHF Benchmarks (standard) | These benchmarks evaluate RLHF model behavior with clear correctness labels |
| **Model** | Open RLHF Models | Representative RLHF-trained models with accessible logprobs |

**Dataset Details:**
- Source: TruthfulQA (817 tasks) + ETHICS justice (~500 tasks) + HHH single-turn (~200 tasks)
- Path: Hugging Face datasets / lm-evaluation-harness

**Model Details:**
- Type: instruction-following LLMs
- Source: Llama-2-7B-Chat, Llama-2-13B-Chat, Mistral-7B-Instruct

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Aggregate benchmark accuracy | ~75% on TruthfulQA for top RLHF models | TruthfulQA |
| Topic-stratified evaluation | Varies by topic (~10% variance) | Various |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Calibration scores reliably measurable from model logprobs | Standard technique; logprobs available from open models | Cannot compute inversion metric; need alternative confidence measure |
| A2 | Bidirectional features identifiable from task text alone | Three features defined: user-belief-reference, context-dependent, hedged-answer | Would need human annotation or richer context |
| A3 | Open RLHF models representative of RLHF behavior generally | Llama-2-Chat, Mistral-Instruct use standard RLHF | Findings may not generalize to closed models |
| A4 | Task difficulty estimable via cross-model accuracy | Standard proxy for difficulty | Difficulty confound might not be fully controlled |
| A5 | Bidirectional feature base rate in informative range (20-80%) | To be validated in preliminary analysis | Test becomes uninformative if most/few tasks have features |

### 1.6 Research Gap & Novelty

**Gap:** Existing benchmarks lack directionality classification. Shen et al. 2024 established theoretical bidirectional alignment framework but left task-level classification unsolved.

**Novelty:** First empirical method to classify benchmark tasks by bidirectionality using behavioral signals (calibration inversion patterns). Automated classification without manual annotation.

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

#### H-E1: Calibration Inversion Clusters Exist Systematically

**Type:** EXISTENCE
**Statement:** Under RLHF benchmark evaluation, if we compute calibration scores across all tasks, then tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) will cluster non-randomly (silhouette > 0.3), because systematic model behavior patterns exist.

**Rationale:** Before testing mechanism, we must verify the phenomenon exists. If calibration inversion is randomly distributed, no clustering will emerge and the entire hypothesis fails.

**Variables:**
- Independent: Task calibration scores (model logprobs)
- Dependent: Cluster separability (silhouette score)
- Controlled: Model architecture, evaluation protocol

**Verification Protocol:**
1. Generate model responses with logprobs for all benchmark tasks (~1500 tasks across TruthfulQA, ETHICS, HHH).
2. Compute calibration score per task (sequence-level log probability, length-normalized).
3. Apply k-means clustering (k=3) on calibration scores.
4. Compute silhouette score to validate cluster quality.

**Success Criteria (PoC: Direction-based):**
- Primary: Silhouette score > 0.3
- Secondary: Clusters show distinct calibration profiles

**Failure Response:**
- IF fails: ABANDON - No systematic pattern exists to correlate with features

**Dependencies:** None

**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: RLHF Optimizes for Annotator Approval

**Type:** MECHANISM
**Statement:** Under standard RLHF training, if we analyze the reward signal, then models optimize for annotator approval (not correctness alone), because annotator ratings conflate multiple dimensions.

**Rationale:** First causal step establishing that RLHF reward signal carries conflated information. This is foundational to explaining why calibration inversion occurs.

**Variables:**
- Independent: RLHF training objective
- Dependent: Reward model behavior on correctness vs user-modeling tasks
- Controlled: Model architecture, training data

**Verification Protocol:**
1. Sample tasks that require user-state modeling vs pure factual correctness.
2. Analyze reward model scores (if accessible) or proxy via model confidence.
3. Test if both task types receive similar reward signals.

**Success Criteria (PoC: Direction-based):**
- Primary: Evidence of conflated reward signal
- Secondary: Similar confidence on both task types

**Failure Response:**
- IF fails: PIVOT - Reward models may separate dimensions; alternative mechanism

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Annotator Approval Conflates Correctness with User-State Modeling

**Type:** MECHANISM
**Statement:** Under annotator rating behavior, if annotators rate both "correct output" and "output requiring user-state modeling" high without distinguishing, then the reward model learns a combined signal, because the rating scale doesn't differentiate.

**Rationale:** Tests the conflation hypothesis - that annotator behavior is the source of the reward signal ambiguity.

**Variables:**
- Independent: Annotator rating behavior (proxy via reward model)
- Dependent: Reward model internal representation
- Controlled: Rating interface, task presentation

**Verification Protocol:**
1. Identify tasks with user-state-modeling requirements vs pure correctness.
2. Compare model confidence distributions across task types.
3. Test if high confidence correlates equally with both task types.

**Success Criteria (PoC: Direction-based):**
- Primary: Similar confidence on user-modeling and correctness tasks
- Secondary: No separation in model internal representations

**Failure Response:**
- IF fails: EXPLORE - Conflation may be partial; document scope

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Models Learn Single Reward Signal Missing Bidirectional Nuance

**Type:** MECHANISM
**Statement:** Under single scalar reward training, if models receive one combined signal for correctness and user-modeling, then they miss bidirectional adaptation nuance, because the training objective doesn't distinguish.

**Rationale:** Tests whether the single reward architecture causes the blindspot.

**Variables:**
- Independent: Reward signal dimensionality (single scalar)
- Dependent: Model representation of bidirectional features
- Controlled: Training procedure, model architecture

**Verification Protocol:**
1. Probe model representations for bidirectional feature sensitivity.
2. Compare with representations of non-bidirectional features.
3. Analyze if bidirectional nuance is captured.

**Success Criteria (PoC: Direction-based):**
- Primary: Lower sensitivity to bidirectional features
- Secondary: Evidence of representation conflation

**Failure Response:**
- IF fails: EXPLORE - Models may learn separate representations; scope limitation

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Bidirectional Tasks Show Miscalibrated Confidence

**Type:** MECHANISM
**Statement:** Under the reward conflation mechanism, if tasks require bidirectional adaptation, then models show miscalibrated confidence (high confidence on wrong answers), because the specialized training signal is missing.

**Rationale:** Final causal step connecting the mechanism to the observable phenomenon. This is the key prediction test.

**Variables:**
- Independent: Task bidirectionality score (0-3 feature checklist)
- Dependent: Calibration inversion rate
- Controlled: Task length, topic, format, difficulty

**Verification Protocol:**
1. Score all benchmark tasks on bidirectional feature checklist (3 features).
2. Correlate bidirectional score with calibration cluster membership.
3. Compute partial correlation controlling for confounds (length, topic, format, difficulty).
4. Test effect size (Cohen's d) between inversion and non-inversion tasks.

**Success Criteria (PoC: Direction-based):**
- Primary: r(cluster, bidirectional_features) > 0.4
- Secondary: Cohen's d > 0.3; partial r > 0.3 after controls

**Failure Response:**
- IF fails: ABANDON - Mechanism doesn't explain calibration patterns

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4, Predictions P2-P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Silhouette > 0.3 | STOP: No systematic pattern |
| H-M1 | MUST_WORK | Evidence of conflated reward | PIVOT: Alternative mechanism |
| H-M2 | SHOULD_WORK | Similar confidence across task types | EXPLORE: Partial conflation |
| H-M3 | SHOULD_WORK | Lower bidirectional sensitivity | EXPLORE: Scope limitation |
| H-M4 | SHOULD_WORK | r > 0.4, d > 0.3 | ABANDON: Mechanism fails |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

| Risk ID | Source | Description | Severity | Affected Hypotheses |
|---------|--------|-------------|----------|---------------------|
| R1 | A1 | Calibration scores unreliable/noisy | High | H-E1, H-M4 |
| R2 | A2 | Bidirectional features hard to identify from text | Medium | H-M4 |
| R3 | A3 | Open models not representative | Medium | All |
| R4 | A4 | Difficulty confound not controlled | Medium | H-M4 |
| R5 | A5 | Feature base rate outside informative range | High | H-M4 |

### 4.2 Mitigation Strategies

**R1 (High): Calibration Score Reliability**
- Prevention: Use length-normalized log probabilities; test multiple aggregation methods
- Detection: Check calibration variance across repeated runs
- Response: PIVOT to alternative confidence metrics (entropy, margin)

**R2 (Medium): Feature Identification**
- Prevention: Pre-register three proxy features with objective definitions
- Detection: Inter-rater reliability check on sample
- Response: SCOPE to features with >80% agreement

**R3 (Medium): Model Representativeness**
- Prevention: Use models from multiple organizations (Meta, Mistral)
- Detection: Check pattern consistency across models
- Response: SCOPE findings to open RLHF models

**R4 (Medium): Difficulty Confound**
- Prevention: Stratify analysis by difficulty quartiles
- Detection: Check correlation in each stratum
- Response: Report partial correlations

**R5 (High): Base Rate Problem**
- Prevention: Validate feature base rate in preliminary analysis
- Detection: Check if 20-80% tasks have features
- Response: PIVOT to different feature operationalization

### 4.3 Risk Summary

| Severity | Count | Risks |
|----------|-------|-------|
| Critical | 0 | - |
| High | 2 | R1, R5 |
| Medium | 3 | R2, R3, R4 |
| Low | 0 | - |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 ← H-E1
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    H-M3 ← H-M2
         │
         ▼
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════════════
```

### 5.2 Verification Phases

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Calibration clustering exists | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, no systematic pattern exists.

**Phase 2 - Core Mechanisms** (4 hypotheses)
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | SHOULD_WORK |
| H-M3 | H-M2 | SHOULD_WORK |
| H-M4 | H-M3 | SHOULD_WORK |

→ **Gate 2**: H-M1 must pass. Later failures document limitations.

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2 │ W3   │ W4   │ W5   │ W6   │
──────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 1: Foundation
  H-E1            │██████│      │      │      │      │
  [Gate 1]        │      │ ◆    │      │      │      │
──────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 2: Mechanisms
  H-M1            │      │██████│      │      │      │
  H-M2            │      │      │████  │      │      │
  H-M3            │      │      │      │████  │      │
  H-M4            │      │      │      │      │████  │
  [Gate 2]        │      │      │      │      │    ◆ │
══════════════════════════════════════════════════════
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
**Total Duration:** 6 weeks (2 + 4)
**Slack Available:** 0 weeks (all sequential)

### 5.5 Resource Summary

| Resource | Allocation |
|----------|------------|
| Total Hypotheses | 5 |
| Existence | 1 (H-E1) |
| Mechanism | 4 (H-M1-M4) |
| Verification Phases | 2 |
| Critical Path Length | 6 weeks |

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** RLHF-trained models exhibit systematic calibration inversion on tasks requiring bidirectional adaptation due to reward signal conflation.

**Supporting Evidence:**
1. RLHF training optimizes for annotator approval (Ouyang et al. 2022)
2. Annotators don't distinguish correctness from user-modeling
3. Single scalar reward misses dimensional nuance

**Strengths:**
- Clear causal mechanism with 4 testable steps
- Uses established RLHF training framework
- Testable predictions with quantified thresholds

**Expected Outcomes:**
- P1: Clusters form (silhouette > 0.3)
- P2: Clusters correlate with features (r > 0.4, d > 0.3)
- P3: Correlation survives controls (partial r > 0.3)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant correlation between calibration inversion clusters and bidirectional task features, OR the correlation with bidirectional features does not exceed correlation with control features.

**Counter-Arguments:**
1. Calibration inversion may be random/artifactual
2. Correlation may be driven by confounds (length, topic, format)
3. Bidirectional features may be unmeasurable from text alone

**Potential Failure Points:**
- R1: Calibration unreliable → no clusters
- R5: Feature base rate outside informative range → uninformative test
- R4: Difficulty confound explains all variance

**Conditions Under Which H0 Would Be Supported:**
- Silhouette < 0.2 (no meaningful clustering)
- r(cluster, features) < 0.2 (no meaningful correlation)
- Partial r < 0.15 after confound controls

### 6.3 Synthesis

**Balanced Assessment:**
The hypothesis H-BiDir-Cal-v1 presents a testable claim with clear mechanism. However, the null hypothesis raises valid concerns about reliability and confounds.

**Resolution Path:**
1. **Foundation verification (H-E1):** Establishes existence before mechanism
2. **Sequential mechanism testing (H-M1-4):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- H-E1 and H-M1 pass (MUST_WORK gates)
- P1-P3 predictions confirmed

**Conditions for Antithesis Support:**
- H-E1 fails: No systematic pattern
- H-M4 fails: Mechanism doesn't explain correlation

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Clusters exist | May be artifact | H-E1 test |
| Mechanism | Causal chain valid | Alternative explanations | H-M1-4 tests |
| Scope | Applies to RLHF models | Limited to open models | A3 scope |
| Performance | Outperforms baselines | Marginal improvement | Phase 5 |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** Calibration inversion patterns in RLHF models correlate with bidirectional task features due to reward signal conflation.
- ID: H-BiDir-Cal-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1, Gate 2)

**Risk Assessment:** Medium
- High concerns: Calibration reliability (R1), feature base rate (R5)

**Immediate Action:** Begin Phase 1 with H-E1 (clustering validation)

---

## 8. Conclusions

### 8.1 Key Achievements
- 5 hypotheses across 2 phases
- H0 addressed via dialectical analysis

### 8.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Calibration inversion clusters exist systematically
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: RLHF optimizes for annotator approval
- H-M2: Annotator approval conflates correctness with user-state modeling
- H-M3: Models learn single reward signal missing bidirectional nuance
- H-M4: Bidirectional tasks show miscalibrated confidence
- Gate 2: H-M1 must pass

### 8.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

### 8.4 Open Questions
- What is the exact base rate of bidirectional features in benchmark tasks?
- Do all RLHF variants (DPO, RLAIF) show same calibration patterns?
- Does calibration inversion predict real-world deployment failures?

### 8.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up logprob extraction pipeline

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Reserve buffer for Gate 1 failure pivot

3. **Failure Management:**
   - Document all failures
   - Execute PIVOT strategies per risk mitigation

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-BiDir-Cal-v1)

### B. Established Facts (BUILD_ON)
- Bidirectional alignment framework is theoretically established (Shen et al. 2024)
- RLHF models exhibit miscalibration patterns

### C. Scope Reduction
- 50% scope reduction from Established Facts
- Focus on PROVE_NEW claims only

---

*Generated by Phase 2B Planning Workflow*
*Completed: 2026-08-19*
