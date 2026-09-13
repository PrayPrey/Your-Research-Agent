# Verification Plan: CorrectnessProbe - Single-Pass Factual Correctness Prediction

**Date:** 2026-08-18
**Hypothesis ID:** H-CorrectnessProbe-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the scope of factual QA tasks with objective ground-truth answers,
if we train a linear probe on middle-layer (60% depth) hidden states from a transformer LLM,
then the probe will predict factual correctness with AUROC >= 0.75,
because middle-layer representations encode semantic knowledge before task-specific output formatting compresses this information.

### 1.2 Alternative Hypothesis (H0)
Hidden state probes achieve correctness prediction AUROC no better than output-level
uncertainty measures (token entropy, sequence probability). Middle-layer hidden states
contain no additional correctness signal beyond the output distribution.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA + Natural Questions + TruthfulQA (standard) | Factual QA with objective answers; diverse difficulty levels; TruthfulQA tests hallucination resistance |
| **Model** | Llama-3-8B-Instruct | Open-weights, well-studied, accessible hidden states, representative of modern LLMs |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: trivia_qa, natural_questions, truthful_qa

**Model Details:**
- Type: transformer
- Source: meta-llama/Meta-Llama-3-8B-Instruct

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Token Entropy | ~0.65 AUROC | TriviaQA, Natural Questions |
| Multi-sample Semantic Entropy | ~0.80 AUROC | TriviaQA, Natural Questions |
| Semantic Entropy Probes | 0.85+ correlation with SE | Various QA |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Hidden states accessible via forward hooks | Standard PyTorch/HuggingFace feature | Implementation impossible - not a real risk |
| A2 | Exact-match correctness labels approximate true factual correctness | Standard QA evaluation | Probe learns format matching - mitigate with F1 overlap |
| A3 | Middle-layer representations generalize across QA question types | Transfer learning literature | Probe overfits - test on TruthfulQA, NQ |
| A4 | Linear probe has sufficient capacity | SEP used linear probes successfully | Linear underperforms - test MLP variant |
| A5 | Signal consistent across answer lengths and question difficulties | Requires stratified analysis | Probe only works on easy questions - stratify results |

### 1.6 Research Gap & Novelty

**Key Innovation:** First work to train probes for direct factual correctness prediction rather than uncertainty estimation.

SEP (Kossen, 2024) predicts semantic entropy (an uncertainty measure); we predict ground-truth accuracy. This reframes the problem: instead of "estimate uncertainty, then infer correctness," we go directly to "hidden states → correctness."

**Differentiation:**
- vs SEP: Different training signal (correctness vs SE)
- vs Token entropy: Uses internal hidden states with richer signal
- vs Multi-sample SE: Achieves similar AUROC with single pass (5-20x less compute)

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
**H-E1: Existence of Correctness Signal in Hidden States**

**Statement**: Under factual QA tasks, if we extract middle-layer hidden states from Llama-3-8B, then a trained probe achieves AUROC > 0.60 (better than random), because hidden states encode knowledge representation.

**Rationale**: Establishes that hidden states contain ANY signal predictive of correctness. Without this, the entire mechanism fails. This is the foundation hypothesis.

**Variables** (from Phase 2A):
- Independent: Layer depth (8 levels: 0.125-1.0)
- Dependent: Correctness AUROC
- Controlled: Model (Llama-3-8B), Training data (TriviaQA 95K)

**Verification Protocol**:
1. Generate answers for TriviaQA validation set (17K examples) using greedy decoding
2. Extract hidden states from layer at 60% depth via forward hooks
3. Train linear probe on train split, evaluate AUROC on validation
4. Compare against random baseline (AUROC = 0.50)

**Success Criteria** (PoC: Direction-based):
- Primary: AUROC > 0.60 on validation set
- Secondary: Statistically significant improvement over random (p < 0.05)

**Failure Response**:
- IF fails: ABANDON - hidden states lack correctness signal

**Dependencies**: None

**Source**: Phase 2A SH1, Prediction P1

---
**H-M1: Forward Pass Generates Answer with Extractable Hidden States**

**Statement**: Under standard inference, if we run Llama-3-8B with forward hooks, then hidden states are captured at all layer depths without affecting generation quality, because PyTorch hooks are non-intrusive.

**Rationale**: Validates the technical foundation. Hidden state extraction must not alter model behavior.

**Variables**:
- Independent: Hook presence (with/without hooks)
- Dependent: Generation output identity, inference time overhead
- Controlled: Same input prompts, greedy decoding

**Verification Protocol**:
1. Generate 1000 answers without hooks
2. Generate same 1000 answers with hooks capturing all layers
3. Verify outputs are byte-identical
4. Measure inference time overhead

**Success Criteria**:
- Primary: 100% output identity with/without hooks
- Secondary: Overhead < 10% inference time

**Failure Response**:
- IF fails: PIVOT to gradient-free extraction methods

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---
**H-M2: Middle Layers Encode Semantic Knowledge Representation**

**Statement**: Under factual QA, if we compare probe AUROC across layer depths, then middle layers (50-70% depth) achieve highest AUROC exhibiting inverted-U pattern, because semantic knowledge is encoded before output formatting.

**Rationale**: Tests the core mechanistic claim about WHERE in the model correctness information lives.

**Variables**:
- Independent: Layer depth (8 levels)
- Dependent: Correctness AUROC per layer
- Controlled: Same probe architecture, same training data

**Verification Protocol**:
1. Train separate linear probe at each of 8 layer depths
2. Evaluate each probe on validation set
3. Plot AUROC vs layer depth curve
4. Test for inverted-U pattern (peak at 50-70%)

**Success Criteria**:
- Primary: L_60% AUROC > L_100% AUROC (middle beats final)
- Secondary: L_60% AUROC > L_25% AUROC (middle beats early)

**Failure Response**:
- IF final layer best: PIVOT - correctness in output formatting, not middle layers

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2, Prediction P1

---
**H-M3: Linear Probe Learns Hidden State to Correctness Mapping**

**Statement**: Under supervised training, if we train a linear probe on middle-layer hidden states with correctness labels, then the probe converges with validation AUROC >= 0.70, because the hidden state space is linearly separable for correctness.

**Rationale**: Validates that the correctness signal is extractable with minimal model complexity.

**Variables**:
- Independent: Probe architecture (linear vs 2-layer MLP)
- Dependent: Training convergence, validation AUROC
- Controlled: Same hidden states, same labels

**Verification Protocol**:
1. Train linear probe with SGD on TriviaQA train (95K)
2. Monitor training loss convergence
3. Evaluate validation AUROC
4. If linear fails, train 2-layer MLP as fallback

**Success Criteria**:
- Primary: Training loss converges (not stuck at random)
- Secondary: Validation AUROC >= 0.70

**Failure Response**:
- IF linear fails: TEST MLP variant
- IF both fail: EXPLORE - non-linear extraction needed

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, Assumption A4

---
**H-M4: Probe Outperforms Output-Level Baselines**

**Statement**: Under comparable evaluation, if we compare probe AUROC to token entropy and sequence probability, then the probe exceeds baselines by >= 5 AUROC points, because hidden states encode knowledge confidence distinct from softmax confidence.

**Rationale**: The critical test - hidden states must add value beyond what's in the output distribution.

**Variables**:
- Independent: Method (probe vs token entropy vs seq prob)
- Dependent: Correctness AUROC
- Controlled: Same evaluation set, same model outputs

**Verification Protocol**:
1. Compute token entropy for all validation examples
2. Compute sequence probability for all validation examples
3. Evaluate probe AUROC on same examples
4. Statistical comparison with bootstrap CIs

**Success Criteria**:
- Primary: Probe AUROC - Token Entropy AUROC >= 0.05
- Secondary: Probe AUROC within 0.03 of 5-sample SE (with 5x less compute)

**Failure Response**:
- IF fails: PIVOT - hidden states redundant with output; explore attention patterns

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Predictions P3, P4

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUROC > 0.60 | ABANDON entire hypothesis |
| H-M1 | MUST_WORK | 100% output identity | PIVOT to alternative extraction |
| H-M2 | SHOULD_WORK | Middle > Final layer | Document limitation |
| H-M3 | SHOULD_WORK | AUROC >= 0.70 | Try MLP variant |
| H-M4 | SHOULD_WORK | +5 AUROC vs baseline | Document as incremental gain |

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
| R1 | A1 | H-M1 | Low |
| R2 | A2 | H-E1, H-M3, H-M4 | Medium |
| R3 | A3 | H-M2, H-M4 | Medium |
| R4 | A4 | H-M3 | Medium |
| R5 | A5 | H-M4 | Medium |

### 4.2 Mitigation Strategies

**R1: Hidden State Inaccessibility**
- Prevention: Use standard HuggingFace hooks (proven in SEP)
- Detection: Unit test hook functionality
- Response: N/A - extremely low probability

**R2: Label Quality Issues**
- Prevention: Use established QA benchmarks
- Detection: Manual inspection of 100 examples
- Response: Add F1 overlap and TruthfulQA evaluation

**R3: Overfitting to TriviaQA**
- Prevention: Evaluate on held-out benchmarks (NQ, TruthfulQA)
- Detection: Large train-test AUROC gap
- Response: Report cross-benchmark results honestly

**R4: Linear Probe Insufficient**
- Prevention: Design MLP fallback from start
- Detection: Training fails to converge
- Response: Switch to 2-layer MLP

**R5: Performance Varies by Difficulty**
- Prevention: Plan stratified analysis
- Detection: AUROC varies >0.10 across strata
- Response: Report stratified results, characterize limitations

### 4.3 Risk Summary

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| R1 | Hook inaccessibility | Low | Very Low | Standard API |
| R2 | Label quality | Medium | Medium | Multi-benchmark |
| R3 | Overfitting | Medium | Medium | Cross-benchmark eval |
| R4 | Probe capacity | Medium | Low | MLP fallback |
| R5 | Stratification | Medium | Medium | Report stratified |

Critical: 0 | High: 0 | Medium: 4 | Low: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1-4 - Mechanisms]
    H-M1 ← H-E1 (Forward pass extraction)
         │
         ▼
    H-M2 ← H-M1 (Middle layer superiority)
         │
         ▼
    H-M3 ← H-M2 (Probe learning)
         │
         ▼
    H-M4 ← H-M3 (Baseline comparison)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Length: 5 hypotheses, 6 weeks
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3   │ W4   │ W5   │ W6   │
─────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 1: Foundation
  H-E1           │██████│      │      │      │      │
  [Gate 1]       │      │◆     │      │      │      │
─────────────────┼──────┼──────┼──────┼──────┼──────┤
PHASE 2: Mechanisms
  H-M1           │      │██████│      │      │      │
  H-M2           │      │      │██████│      │      │
  H-M3           │      │      │      │██████│      │
  H-M4           │      │      │      │      │██████│
  [Gate 2]       │      │      │      │      │     ◆│
─────────────────┼──────┼──────┼──────┼──────┼──────┤
═══════════════════════════════════════════════════════════════════
Legend: ██████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

- **Critical Path**: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- **Total Duration**: 6 weeks
- **Slack Available**: 0 weeks (all sequential)
- **Parallelization**: None (strict dependencies)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim**: Middle-layer hidden states encode factual correctness signal that can be extracted with a linear probe, achieving AUROC >= 0.75.

**Supporting Evidence**:
1. SEP paper shows hidden states correlate with semantic entropy (0.85+)
2. Logit lens work demonstrates semantic knowledge in middle layers
3. Linear probes successfully extract high-level concepts from representations

**Strengths**:
- Builds on established hidden state probing literature
- Clear 4-step causal mechanism with testable predictions
- 6 pre-registered predictions with quantitative thresholds

### 6.2 Antithesis (H0-Based)

**Null Hypothesis**: Hidden state probes achieve correctness prediction AUROC no better than output-level uncertainty measures. Middle-layer hidden states contain no additional correctness signal.

**Counter-Arguments**:
1. Token entropy already captures output confidence - hidden states may be redundant
2. SEP predicts uncertainty, not correctness - different signals may not transfer
3. Correctness is binary but hidden states encode continuous uncertainty

**Conditions Under Which H0 Would Be Supported**:
- Probe AUROC <= Token entropy baseline
- No inverted-U pattern (final layer best)
- Probe fails to detect confident-but-wrong cases

### 6.3 Synthesis

**Balanced Assessment**:
The hypothesis H-CorrectnessProbe-v1 presents a testable claim that hidden states encode correctness signal. However, the null hypothesis raises valid concerns about redundancy with output-level signals.

**Resolution Path**:
1. **H-E1** establishes existence before mechanism testing
2. **H-M2** tests the inverted-U prediction to validate middle-layer claim
3. **H-M4** directly compares against baselines - decisive test

**Conditions for Thesis Support**:
- H-E1 and H-M1 pass (MUST_WORK gates)
- Inverted-U pattern observed (H-M2)
- Probe exceeds token entropy by >= 5 AUROC points (H-M4)

**Conditions for Antithesis Support**:
- H-E1 fails (no existence)
- Final layer achieves highest AUROC (H-M2 fails)
- Probe AUROC <= token entropy (H-M4 fails)

**Nuanced Outcome Possibilities**:
1. **Full Support**: All pass → Thesis validated
2. **Partial Support**: Mechanism works but marginal gain → Incremental contribution
3. **No Support**: Foundation fails → Antithesis supported, pivot to new approach

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Signal exists | May be noise | H-E1 test |
| Location | Middle layers optimal | Could be final layer | H-M2 test |
| Magnitude | +5 AUROC over baseline | Marginal at best | H-M4 test |
| Scope | Generalizes to QA | Overfits TriviaQA | Cross-benchmark eval |

**Overall Robustness Score**: Medium-High
**Confidence in Verification Plan**: 0.80

---

## 7. Executive Summary

**Main Hypothesis:** Direct correctness prediction from middle-layer hidden states
- ID: H-CorrectnessProbe-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (from Phase 2A)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 MUST_WORK decision points

**Risk Assessment:** Medium
- Primary concerns: Label quality (R2), Generalization (R3)

**Immediate Action:** Begin Phase 1 with H-E1 existence verification

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-CorrectnessProbe-v1)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 2
- **Tools:** scientificmethod (2x: H-E1 verification, H-M integrated mechanism)

### C. Established Facts (BUILD_ON - Not Re-tested)
- Hidden states correlate with semantic entropy (Kossen et al., 2024)
- Token entropy correlates weakly with correctness (~0.65 AUROC)
- Multi-sample semantic entropy achieves ~0.80 AUROC (Kuhn et al., 2023)
- Middle layers encode semantic knowledge (logit lens work)
