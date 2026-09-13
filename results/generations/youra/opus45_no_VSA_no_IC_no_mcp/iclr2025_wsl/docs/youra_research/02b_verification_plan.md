# Verification Plan: Locality Bias in Weight-Space Architectures

**Date:** 2026-08-28
**Hypothesis ID:** H-LocalityBias-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under model property prediction tasks on standard benchmarks (TrojAI, ModelZoo), if different permutation-equivariant architectures (DWS, NFT) are applied, then property-type-dependent performance differences emerge, because explicit locality inductive bias (DWS) improves fine-grained pattern detection while global attention (NFT) improves holistic property aggregation.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in model property prediction performance between DWS and NFT architectures across property types (backdoor, accuracy).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TrojAI + ModelZoo (standard) | TrojAI provides large-scale backdoor labels; ModelZoo provides accuracy labels |
| **Model** | NFT, DWS, MLP-Baseline | Direct test of locality vs attention inductive biases |

**Dataset Details:**
- Source: TrojAI benchmark (NIST), ModelZoo datasets
- Path: trojai.nist.gov, github model zoo repositories

**Model Details:**
- Type: weight-space processors
- Source: Public implementations from original papers

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Flattened MLP | ~0.70 AUC on backdoor (estimated) | TrojAI |
| Weight Statistics (Unterthiner) | Moderate accuracy prediction | ModelZoo |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Backdoor triggers manifest as spatially localized weight anomalies | TrojAI benchmark design; backdoors typically affect specific layers | Locality advantage disappears; DWS may not outperform on backdoor |
| A2 | Model accuracy depends on holistic weight statistics | Accuracy emerges from full network behavior, not individual weights | NFT advantage on accuracy prediction disappears |
| A3 | Dataset size is sufficient for effect detection | TrojAI has thousands of models; ModelZoo smaller but usable with effect size derivation | Underpowered experiment; cannot reject null hypothesis |
| A4 | Matched parameters control for capacity confound | Standard practice in architecture comparison studies | Observed differences may reflect capacity, not inductive bias |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic comparison of equivariant architectures on model property prediction

**Key Innovation:** Property-type-dependent architecture selection guidance based on inductive bias analysis

**Differentiation:**
- NFT (Zhou 2024): Evaluated on INR tasks; we evaluate on property prediction
- DWS (Navon 2023): Evaluated on weight editing; we evaluate on classification/regression
- Unterthiner (2020): Statistics baseline; we compare with learned equivariant methods

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | READY |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | READY |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | READY |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Locality Inductive Bias Difference Exists**

**Statement**: Under model property prediction tasks, if DWS and NFT architectures process the same model weights, then measurable differences in internal representations emerge because DWS uses explicit locality via equivariant layers while NFT uses global attention.

**Rationale**: Before testing performance claims, we must verify that the architectures actually process information differently. This validates the fundamental premise that locality vs. global attention creates distinct computational behaviors.

**Variables**:
- Independent: Architecture type (DWS, NFT)
- Dependent: Representation similarity metrics (attention patterns, activation statistics)
- Controlled: Input model weights, parameter count

**Verification Protocol**:
1. Extract intermediate representations from both architectures on same inputs.
2. Compute attention entropy (NFT) and receptive field analysis (DWS).
3. Compare representation statistics to confirm differential processing.

**Success Criteria** (PoC: Direction-based):
- Primary: Attention entropy differs significantly between architectures
- Secondary: DWS shows more localized activation patterns than NFT

**Failure Response**:
- IF fails: ABANDON (core premise invalid)

**Dependencies**: None

**Source**: Phase 2A SH1, established_facts.claims[3]

---
**H-M1: Architecture Encodes Different Inductive Biases**

**Statement**: Under equivalent parameter budgets, if DWS and NFT are trained on the same data, then DWS exhibits weight-space locality constraints while NFT exhibits global aggregation patterns because of their fundamental architectural designs.

**Rationale**: This mechanistic step establishes that architectural differences translate to measurable behavioral differences during training, not just at inference.

**Variables**:
- Independent: Architecture type
- Dependent: Weight update patterns, gradient flow characteristics
- Controlled: Training procedure, learning rate, epochs

**Verification Protocol**:
1. Train both architectures with identical setup on TrojAI subset.
2. Track gradient norms per layer and weight update magnitudes.
3. Analyze attention pattern evolution (NFT) vs. equivariant operation locality (DWS).

**Success Criteria** (PoC: Direction-based):
- Primary: Weight update patterns show architecture-specific signatures
- Secondary: NFT attention becomes more distributed over training

**Failure Response**:
- IF fails: PIVOT to alternative mechanism explanation

**Dependencies**: H-E1

**Source**: Phase 2A causal_mechanism.steps[0]

---
**H-M2: Locality Bias Reduces Sample Complexity for Local Patterns**

**Statement**: Under limited training data conditions, if backdoor detection requires identifying localized weight anomalies, then DWS achieves higher AUC than NFT because locality bias reduces the search space for pattern detection.

**Rationale**: This tests the sample efficiency claim — that inductive bias provides an advantage when data is limited, analogous to CNN vs. ViT findings in vision.

**Variables**:
- Independent: Architecture type, training set size
- Dependent: Backdoor detection AUC
- Controlled: Evaluation set, backdoor types

**Verification Protocol**:
1. Train DWS and NFT on 25%, 50%, 100% of TrojAI training data.
2. Evaluate AUC on held-out test set for each condition.
3. Compare learning curves (AUC vs. training size) between architectures.

**Success Criteria** (PoC: Direction-based):
- Primary: DWS > NFT AUC on backdoor detection, especially at smaller data sizes
- Secondary: Gap narrows with more data (NFT catches up)

**Failure Response**:
- IF fails: EXPLORE whether effect appears at different data scales

**Dependencies**: H-M1

**Source**: Phase 2A causal_mechanism.steps[1]

---
**H-M3: Task-Dependent Optimal Bias Manifests as Performance Difference**

**Statement**: Under full training data conditions, if backdoor detection favors locality and accuracy prediction favors global aggregation, then DWS outperforms NFT on backdoor while NFT outperforms DWS on accuracy because each task aligns with the respective inductive bias.

**Rationale**: The final mechanism step validates that performance differences are task-dependent, not universal. This tests the interaction effect between architecture and property type.

**Variables**:
- Independent: Architecture type, property type (backdoor, accuracy)
- Dependent: Task-specific metrics (AUC for backdoor, RMSE for accuracy)
- Controlled: Parameter count, training procedure

**Verification Protocol**:
1. Train both architectures on full TrojAI and ModelZoo datasets.
2. Evaluate backdoor AUC (TrojAI) and accuracy RMSE (ModelZoo).
3. Test for interaction effect: architecture × property type.

**Success Criteria** (PoC: Direction-based):
- Primary: Significant interaction effect (crossover pattern)
- Secondary: Both architectures outperform MLP baseline on at least one task

**Failure Response**:
- IF fails: EXPLORE whether effect exists at different model zoo compositions

**Dependencies**: H-M2

**Source**: Phase 2A causal_mechanism.steps[2], predictions P1, P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Representation differences detected | ABANDON hypothesis |
| H-M1 | MUST_WORK | Architecture-specific training signatures | PIVOT mechanism |
| H-M2 | SHOULD_WORK | DWS > NFT on backdoor detection | EXPLORE alternatives |
| H-M3 | SHOULD_WORK | Interaction effect significant | Document limitation |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Foundation | H-E1 | 1-2 days |
| Mechanism Core | H-M1 | 2-3 days |
| Sample Efficiency | H-M2 | 3-4 days |
| Task Interaction | H-M3 | 3-4 days |

**Total Duration:** 9-13 days

---

## 4. Risk Analysis

### 4.1 Risk Identification

**R1: Backdoor Triggers Not Localized**
- Source: A1 (Backdoor triggers manifest as spatially localized weight anomalies)
- Description: If backdoors affect distributed weight patterns rather than localized anomalies, DWS locality advantage disappears
- Severity: High
- Likelihood: Low (TrojAI benchmark design supports assumption)

**R2: Accuracy Not Holistic**
- Source: A2 (Model accuracy depends on holistic weight statistics)
- Description: If accuracy can be predicted from local weight features, NFT advantage on accuracy prediction disappears
- Severity: Medium
- Likelihood: Low (theoretical basis is sound)

**R3: Dataset Size Insufficient**
- Source: A3 (Dataset size is sufficient for effect detection)
- Description: Underpowered experiment prevents null hypothesis rejection; effect may exist but not detected
- Severity: High
- Likelihood: Medium (ModelZoo smaller than TrojAI)

**R4: Capacity Confound**
- Source: A4 (Matched parameters control for capacity confound)
- Description: Observed differences may reflect parameter efficiency rather than inductive bias
- Severity: Medium
- Likelihood: Low (standard control procedure)

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-M2, H-M3 | High |
| R2 | A2 | H-M3 | Medium |
| R3 | A3 | All (H-E1, H-M1-3) | High |
| R4 | A4 | H-E1, H-M1 | Medium |

### 4.3 Mitigation Strategies

**R1 Mitigation (Backdoor Triggers Not Localized):**
- Prevention: Analyze TrojAI trigger patterns before experiment; verify locality assumption
- Detection: Check attention maps and weight change distributions in preliminary runs
- Response: If triggers are distributed, pivot to testing "pattern complexity" hypothesis instead of locality

**R2 Mitigation (Accuracy Not Holistic):**
- Prevention: Literature review of accuracy prediction approaches; verify holistic assumption
- Detection: Run feature importance analysis on baseline predictions
- Response: If local features suffice, document as finding; adjust hypothesis to "aggregation style" rather than "scope"

**R3 Mitigation (Dataset Size Insufficient):**
- Prevention: Power analysis before full experiment; derive minimum detectable effect size
- Detection: Monitor confidence intervals during training; compute effect sizes early
- Response: If underpowered, augment with additional model zoo rounds or reduce to existence-only claim

**R4 Mitigation (Capacity Confound):**
- Prevention: Match total parameters within 5%; report exact counts
- Detection: Compare parameter efficiency curves
- Response: If capacity confound suspected, add parameter-matched ablation study

### 4.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Backdoor not localized | A1 | High | H-M2, H-M3 | Verify trigger patterns |
| R2 | Accuracy not holistic | A2 | Medium | H-M3 | Feature importance check |
| R3 | Dataset insufficient | A3 | High | All | Power analysis |
| R4 | Capacity confound | A4 | Medium | H-E1, H-M1 | Parameter matching |

**Risk Distribution:** Critical: 0, High: 2, Medium: 2, Low: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3-4    │ W5      │ W6      │
────────────────────┼─────────┼─────────┼─────────┼─────────┼
PHASE 1: Foundation │         │         │         │         │
  H-E1              │ ████████│         │         │         │
  [Gate 1]          │        ◆│         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼
PHASE 2: Mechanisms │         │         │         │         │
  H-M1              │         │ ████████│         │         │
  H-M2              │         │         │ ████    │         │
  H-M3              │         │         │         │ ████    │
  [Gate 2]          │         │         │         │        ◆│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Total Duration:** 5 weeks
- Formula: 2 (H-E1) + 3 (H-M1, H-M2, H-M3) = 5 weeks

**Slack Available:** 0 weeks (all sequential)

**Gate Decision Points:**
- Gate 1 (W2): H-E1 must pass → proceed to mechanisms
- Gate 2 (W6): Mechanisms complete → summarize findings

### 5.5 Resource Summary

**Total Hypotheses:** 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0

**Verification Phases:** 2
1. Foundation (H-E1)
2. Mechanisms (H-M1, H-M2, H-M3)

**Total Duration:** 5 weeks
**Critical Path Length:** 5 weeks
**Execution Mode:** Sequential chain

### 5.6 Execution Order

1. **Week 1-2**: Execute H-E1 (Foundation) - Verify representation differences exist
2. **Gate 1**: If H-E1 passes → proceed to mechanisms
3. **Week 3-4**: Execute H-M1 - Verify architecture encodes different biases
4. **Week 5**: Execute H-M2 - Test sample efficiency claim
5. **Week 6**: Execute H-M3 - Validate task-dependent performance
6. **Gate 2**: Summarize mechanism findings
7. **Final**: Verification complete → Phase 5 baseline comparison

---

## 6. Dialectical Analysis

### 6.1 Overview

This dialectical analysis evaluates the hypothesis H-LocalityBias-v1 by considering both the thesis (main claim) and antithesis (null hypothesis), then synthesizing a balanced verification approach.

### 6.2 Thesis Statement

**Core Claim:** Under model property prediction tasks on standard benchmarks (TrojAI, ModelZoo), if different permutation-equivariant architectures (DWS, NFT) are applied, then property-type-dependent performance differences emerge, because explicit locality inductive bias (DWS) improves fine-grained pattern detection while global attention (NFT) improves holistic property aggregation.

**Supporting Evidence:**
1. DWS uses equivariant layers preserving weight locality (Navon 2023)
2. NFT flattens weights to tokens with full attention (Zhou 2024)
3. Analogous locality advantages observed in CNN vs ViT literature

**Strengths:**
- Grounded in published architectural analysis
- Clear causal mechanism with testable predictions
- Well-defined task-dependent success criteria

**Expected Outcomes:**
- DWS AUC > NFT AUC on backdoor detection (>1.5 baseline std)
- NFT RMSE < DWS RMSE on accuracy prediction (>1.5 baseline std)
- Both equivariant methods outperform MLP baseline

### 6.3 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in model property prediction performance between DWS and NFT architectures across property types (backdoor, accuracy).

**Counter-Arguments:**
1. NFT's attention mechanism may learn locality from data, eliminating DWS advantage
2. Backdoor triggers might not be as localized as assumed (distributed patterns)
3. ModelZoo dataset may be too small for reliable effect detection

**Potential Failure Points:**
- R1: Backdoor patterns are distributed, not localized
- R3: Underpowered experiment masks true effects
- R4: Capacity differences confound inductive bias effects

**Conditions Under Which H0 Would Be Supported:**
- NFT AUC >= DWS AUC on backdoor detection
- DWS RMSE <= NFT RMSE on accuracy prediction
- No significant interaction effect between architecture and property type

### 6.4 Synthesis

**Balanced Assessment:**

The hypothesis H-LocalityBias-v1 presents a testable claim grounded in architectural analysis from published work. However, the null hypothesis raises valid concerns about whether attention can learn locality and whether dataset characteristics align with assumptions.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes representation differences exist before testing performance claims
2. **Sequential mechanism testing (H-M1-3):** Tests causal chain step-by-step with intermediate validation
3. **Gate conditions:** Allow early detection of H0 support (ABANDON at H-E1 failure, PIVOT at H-M1 failure)

**Conditions for Thesis Support:**
- H-E1 and H-M1 gates pass (MUST_WORK)
- Significant interaction effect: architecture × property type
- DWS > NFT on backdoor AND NFT > DWS on accuracy

**Conditions for Antithesis Support:**
- H-E1 fails (no measurable representation differences)
- No interaction effect (both architectures perform similarly across tasks)
- Performance differences explained by capacity, not inductive bias

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, property-type guidance established
2. **Partial Support:** H-E1/H-M1 pass but H-M3 fails → Mechanisms differ but performance impact unclear
3. **No Support:** H-E1 fails → Fundamental premise invalid, abandon hypothesis

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Locality bias exists | May be learnable | H-E1 representation test |
| Mechanism | Locality helps local patterns | Attention can learn locality | H-M2 sample efficiency test |
| Task-Dependence | Crossover effect expected | No interaction | H-M3 interaction test |
| Performance | Better than baselines | Marginal improvement | Phase 5 baseline comparison |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

**Rationale:** Strong theoretical grounding and clear falsification criteria, but some reliance on assumed task characteristics (backdoor locality, accuracy holism) that could be violated.

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Locality inductive bias in DWS vs global attention in NFT leads to task-dependent performance differences on model property prediction.
- ID: H-LocalityBias-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: Foundation, Gate 2: Mechanisms)

**Risk Assessment:** Medium
- Primary concerns: Dataset size (R3), backdoor locality assumption (R1)

**Immediate Action:** Begin Phase 1 with H-E1 representation difference verification

### 7.2 Final Summary

**Key Achievements:**
- 4 hypotheses across 2 phases with clear execution order
- H0 addressed: "No significant performance difference between DWS and NFT"
- Scope reduction: 60% from Established Facts (BUILD_ON claims skipped)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Verify locality inductive bias difference exists
- Gate 1: MUST PASS → else ABANDON

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Architecture encodes different inductive biases
- H-M2: Locality bias reduces sample complexity for local patterns
- H-M3: Task-dependent optimal bias manifests as performance difference
- Gate 2: H-M1 must pass → else PIVOT mechanism

### 7.3 Conclusions

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess entire hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute PIVOT to alternative mechanism
   - H-M2/H-M3 FAIL → Document limitation, continue

**Open Questions:**
- Exact effect sizes on specific TrojAI rounds
- Whether attention visualization confirms global vs local processing
- Sensitivity to model architecture subgroups within benchmarks

**Recommendations:**

1. **Immediate Actions:** Start Phase 1 with H-E1; set up representation extraction infrastructure
2. **Resource Allocation:** Allocate 5 weeks for critical path; reserve 2-week buffer
3. **Failure Management:** Document all failures; execute PIVOT strategies per risk mitigation

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-LocalityBias-v1)
- Schema: v10.0.0

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (ablation mode)
- Skipped: scientificmethod, structuredargumentation

---

## 8. State Files

### 8.1 Verification State Status

✅ verification_state.yaml: Generated (ABLATION MODE: restated in state block)
- 4 sub-hypotheses defined (H-E1, H-M1, H-M2, H-M3)
- All hypotheses initialized with proper status (READY/NOT_STARTED based on prerequisites)
- Gate conditions defined (MUST_WORK for H-E1/H-M1, SHOULD_WORK for H-M2/H-M3)

### 8.2 Pipeline Tasks Updated

- Phase 2B: done
- Phase 2C: doing (ready for experiment design)

### 8.3 Hypothesis Tasks Created

| Task | Hypothesis | Type | Status |
|------|-----------|------|--------|
| Hypothesis h-e1 | H-E1 | EXISTENCE | todo |
| Hypothesis h-m1 | H-M1 | MECHANISM | todo |
| Hypothesis h-m2 | H-M2 | MECHANISM | todo |
| Hypothesis h-m3 | H-M3 | MECHANISM | todo |

---

## Phase 2B Complete

**Generated:** 2026-08-28
**Status:** Complete
**Next:** Phase 2C Experiment Design
