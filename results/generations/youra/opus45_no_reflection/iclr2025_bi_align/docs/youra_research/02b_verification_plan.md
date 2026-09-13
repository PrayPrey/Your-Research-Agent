# Verification Plan: BiDPO - Bidirectional Direct Preference Optimization

**Date:** 2026-08-18
**Hypothesis ID:** H-BiDPO-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard alignment training conditions (Mistral-7B, HH-RLHF dataset), if we add a length-normalized collaboration score as an auxiliary objective to DPO (L_BiDPO = L_DPO + lambda * L_agency), then models will Pareto-dominate standard DPO on MT-Bench x TruthfulQA frontier, because agency-preserving responses (explanations, uncertainty acknowledgment, engagement) transfer capability to users, improving multi-turn dialogue quality.

### 1.2 Alternative Hypothesis (H0)

Agency signals extracted from response text provide no incremental optimization benefit beyond preference labels. All lambda > 0 configurations perform <= DPO (lambda=0) on both MT-Bench and TruthfulQA benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HH-RLHF (standard) | Contains preference pairs with full response text, enabling collaboration score extraction |
| **Model** | Mistral-7B-Instruct-v0.2 | Standard size for DPO research, TRL-compatible, strong base capability |

**Dataset Details:**
- Source: Anthropic via HuggingFace
- Path: Anthropic/hh-rlhf

**Model Details:**
- Type: instruction-tuned LLM
- Source: mistralai/Mistral-7B-Instruct-v0.2

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Standard DPO | MT-Bench ~6.5, TruthfulQA ~45% | HH-RLHF |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Collaboration score heuristics capture genuine agency-preservation signals | Patterns derived from HCI research on explanation and collaboration | L_agency optimizes for superficial patterns, not agency |
| A2 | Agency signals are sufficiently orthogonal to preference labels | Pre-training correlation check will verify; if >0.7, use orthogonalized score | BiDPO reduces to weighted DPO, no novel contribution |
| A3 | MT-Bench GPT-4 judge evaluates genuine quality, not just style similarity | MT-Bench validated against human preferences in original paper | Improvement reflects GPT-4 aesthetic preferences, not user utility |
| A4 | Mistral-7B results generalize to other model sizes | Standard assumption in DPO literature; not directly tested | Findings limited to 7B scale |
| A5 | HH-RLHF preference patterns remain relevant for current alignment objectives | HH-RLHF widely used in recent DPO research (2023-2024) | Results may not transfer to more recent preference data |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First method to operationalize bidirectional alignment as a training signal using implicit signals from existing preference data.

**Key Innovation:** Length-normalized collaboration score (collab_score_v2) extracts agency-preservation signals without new annotation.

**Differentiation:**
- Standard DPO: Unidirectional (AI-to-human only); BiDPO adds human-to-AI direction
- MODPO/PAMA/GAPO: Multi-objective but focus on helpfulness vs harmlessness; none include agency preservation
- Mitelut et al. 2023: Theoretical argument only; we provide empirical validation via training intervention

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
**H-E1: Agency Signal Existence**

**Statement**: Under HH-RLHF dataset conditions, if we compute collab_score_v2 on response text, then correlation with preference labels will be < 0.7, because agency signals (reasoning traces, uncertainty, engagement) are orthogonal to helpfulness preferences.

**Rationale**: Validates that collaboration score extracts genuinely novel signal not already captured by preference labels. If correlation >= 0.7, the signal is redundant and BiDPO reduces to weighted DPO.

**Variables**:
- Independent: Response text (chosen vs rejected from HH-RLHF)
- Dependent: Pearson correlation between collab_score and preference labels
- Controlled: Length normalization applied, same HH-RLHF split

**Verification Protocol**:
1. Sample 1000 random HH-RLHF pairs
2. Compute collab_score_v2 on both chosen and rejected responses
3. Calculate Pearson correlation with preference labels (chosen=1, rejected=0)
4. Pass if r < 0.7

**Success Criteria** (PoC: Direction-based):
- Primary: Correlation < 0.7 (signal is orthogonal)
- Secondary: Score distribution shows meaningful variance

**Failure Response**:
- IF fails: PIVOT to orthogonalized score or revise heuristics

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1, Section 1.3 Step 1

---
**H-M1: Gradient Pressure Creation**

**Statement**: Under BiDPO training conditions, if L_agency = 1 - collab_score is added to DPO loss, then training will remain stable and loss will decrease, because multi-objective DPO extensions are stable per MODPO literature.

**Rationale**: Tests that the auxiliary loss integrates without destabilizing training. This is the first mechanism step - if training breaks, entire hypothesis fails.

**Variables**:
- Independent: Lambda weight in {0.25, 0.5, 0.75, 1.0}
- Dependent: Training stability (no NaN, loss decreases)
- Controlled: beta=0.1, lr=5e-7, Mistral-7B, HH-RLHF

**Verification Protocol**:
1. Implement BiDPO loss in TRL DPOTrainer fork
2. Run training with lambda=0.5 for 1 epoch on HH-RLHF
3. Monitor loss curves for stability
4. Pass if no NaN and loss decreases

**Success Criteria**:
- Primary: Training completes without NaN
- Secondary: Loss decreases monotonically after warmup

**Failure Response**:
- IF fails: EXPLORE gradient clipping, lower lambda, or loss scaling

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Step 2

---
**H-M2: Agency-Preserving Response Generation**

**Statement**: Under BiDPO training, if L_agency creates gradient pressure, then trained models will generate responses with higher collaboration scores than DPO baseline, because the loss penalizes low-agency responses.

**Rationale**: Tests that the training signal actually influences model behavior in the expected direction.

**Variables**:
- Independent: Training method (BiDPO vs DPO)
- Dependent: Mean collab_score on held-out prompts
- Controlled: Same base model, same evaluation prompts

**Verification Protocol**:
1. Generate responses from BiDPO and DPO models on 500 held-out prompts
2. Compute collab_score_v2 on all responses
3. Compare mean scores between methods
4. Pass if BiDPO mean > DPO mean (p < 0.05)

**Success Criteria**:
- Primary: BiDPO responses have higher collab_score than DPO
- Secondary: Effect is consistent across lambda values

**Failure Response**:
- IF fails: EXPLORE stronger lambda, different heuristics

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Step 2-3

---
**H-M3: Capability Transfer Mechanism**

**Statement**: Under agency-preserving response generation, if BiDPO models generate more collaborative responses, then MT-Bench multi-turn gains will exceed single-turn gains, because capability transfer primarily benefits follow-up dialogue.

**Rationale**: Tests the core theoretical claim that agency preservation improves user capability, which manifests most strongly in multi-turn settings.

**Variables**:
- Independent: Training method (BiDPO vs DPO)
- Dependent: Relative improvement on MT-Bench (multi-turn) vs TruthfulQA (single-turn)
- Controlled: Same evaluation protocol, GPT-4 judge settings

**Verification Protocol**:
1. Evaluate BiDPO and DPO on MT-Bench (8 categories, multi-turn)
2. Evaluate both on TruthfulQA MC1 (single-turn factual)
3. Calculate relative improvement: (BiDPO - DPO) / DPO for both
4. Pass if MT-Bench relative gain > TruthfulQA relative gain

**Success Criteria**:
- Primary: MT-Bench improvement exceeds TruthfulQA improvement
- Secondary: Effect consistent across 3 seeds

**Failure Response**:
- IF fails: Document as limitation (effect may be uniform across turn types)

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Step 3, Prediction P2

---
**H-M4: Benchmark Performance Improvement**

**Statement**: Under full BiDPO training, if the causal mechanism operates correctly, then BiDPO (lambda=0.5) will achieve MT-Bench >= DPO + 0.3 points, because agency-preserving responses improve multi-turn dialogue quality.

**Rationale**: Tests the primary prediction that BiDPO outperforms DPO on the main benchmark.

**Variables**:
- Independent: Lambda weight (0.0 vs 0.5)
- Dependent: MT-Bench score (GPT-4 judge, 1-10 scale)
- Controlled: Model (Mistral-7B), data (HH-RLHF), 3 random seeds

**Verification Protocol**:
1. Train BiDPO with lambda=0.5 for 3 seeds
2. Train DPO baseline (lambda=0.0) for 3 seeds
3. Evaluate all checkpoints on MT-Bench
4. Pass if mean(BiDPO) >= mean(DPO) + 0.3

**Success Criteria**:
- Primary: MT-Bench improvement >= 0.3 points
- Secondary: Pareto-dominant lambda exists (improves both MT-Bench AND TruthfulQA)

**Failure Response**:
- IF fails: ABANDON if all lambda degrade both metrics; PIVOT if partial improvement

**Dependencies**: H-M3

**Source**: Phase 2A Prediction P1, P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (Existence)
   │
   ▼
H-M1 (Gradient Pressure)
   │
   ▼
H-M2 (Response Generation)
   │
   ▼
H-M3 (Capability Transfer)
   │
   ▼
H-M4 (Benchmark Performance)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Correlation < 0.7 | STOP, use orthogonalized score |
| H-M1 | MUST_WORK | Training stable, loss decreases | STOP, debug training |
| H-M2 | SHOULD_WORK | BiDPO collab_score > DPO | Document limitation |
| H-M3 | SHOULD_WORK | Multi-turn > single-turn improvement | Document limitation |
| H-M4 | SHOULD_WORK | MT-Bench >= DPO + 0.3 | Partial success possible |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Heuristic captures style not agency | A1 | H-E1, H-M2 | High |
| R2: Signal redundant with preferences | A2 | H-E1 | Critical |
| R3: GPT-4 judge circularity | A3 | H-M3, H-M4 | Medium |
| R4: Scale-specific results | A4 | All | Low |
| R5: Dataset drift | A5 | All | Low |

### 4.2 Mitigation Strategies

**R1 (Heuristic validity):**
- Prevention: Length normalization applied
- Detection: Qualitative inspection of high/low scoring responses
- Response: Revise heuristics if pattern artifacts detected

**R2 (Signal redundancy):**
- Prevention: Pre-training correlation check (H-E1)
- Detection: r >= 0.7 triggers alert
- Response: PIVOT to orthogonalized score

**R3 (GPT-4 circularity):**
- Prevention: TruthfulQA as non-LLM-judge control
- Detection: Divergence between MT-Bench and TruthfulQA trends
- Response: Report both metrics, acknowledge limitation

**R4/R5 (Generalization):**
- Acknowledged as limitations in scope
- Future work: Test on other model sizes, recent preference data

---

## 5. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1-4 - Mechanisms]
    H-M1 ← H-E1 (Gradient Pressure)
         │
         ▼
    H-M2 ← H-M1 (Response Generation)
         │
         ▼
    H-M3 ← H-M2 (Capability Transfer)
         │
         ▼
    H-M4 ← H-M3 (Benchmark Performance)

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════════════
```

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2 │ W3-4 │ W5 │ W6 │ W7 │
──────────────────┼──────┼──────┼────┼────┼────┤
PHASE 1: Foundation
  H-E1            │██████│      │    │    │    │
  [Gate 1]        │      │◆     │    │    │    │
──────────────────┼──────┼──────┼────┼────┼────┤
PHASE 2: Mechanisms
  H-M1            │      │██████│    │    │    │
  H-M2            │      │      │████│    │    │
  H-M3            │      │      │    │████│    │
  H-M4            │      │      │    │    │████│
  [Gate 2]        │      │      │    │    │   ◆│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** BiDPO with agency-preserving auxiliary objective outperforms standard DPO on alignment benchmarks.

**Supporting Evidence:**
1. DPO provides closed-form preference optimization (Rafailov 2023, 10K+ citations)
2. Multi-objective DPO is stable per MODPO literature
3. Agency-preserving responses transfer capability (theoretical grounding from Mitelut et al.)

**Strengths:**
- Builds on established DPO foundation
- No new annotation required
- Clear testable predictions

### 6.2 Antithesis (H0)

**Null Hypothesis:** Agency signals provide no incremental optimization benefit beyond preference labels.

**Counter-Arguments:**
1. Collaboration score may capture verbosity/style artifacts
2. Signal may be redundant if correlation > 0.7
3. GPT-4 judge may prefer collaborative style due to its training

**Conditions for H0 Support:**
- All lambda > 0 perform <= DPO on both benchmarks
- Correlation check fails (r >= 0.7)

### 6.3 Synthesis

The verification plan resolves this dialectic through:

1. **Pre-training validation (H-E1):** Tests signal orthogonality before expensive training
2. **Sequential mechanism testing (H-M1-4):** Each step has falsification criteria
3. **Dual-benchmark evaluation:** MT-Bench + TruthfulQA controls for judge bias
4. **Gate conditions:** Allow early detection of antithesis support

**Outcome Possibilities:**
- **Full Support:** All gates pass → Thesis validated
- **Partial Support:** Some H-M fail → Refined thesis with limitations
- **No Support:** H-E1 or H-M1 fail → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Agency signal exists | May be artifact | H-E1 correlation check |
| Mechanism | Causal chain valid | Alternative explanations | H-M1-4 sequential tests |
| Performance | Outperforms baseline | Marginal improvement | Phase 5 comparison |

**Overall Robustness:** High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** BiDPO adds agency-preserving auxiliary objective to DPO for Pareto-dominant alignment
- ID: H-BiDPO-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (75% scope reduction from Phase 2A)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (H-E1, H-M1 are MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: Heuristic validity (R1), signal redundancy (R2)
- Mitigations in place: Length normalization, pre-training correlation check

**Immediate Action:** Begin Phase 1 with H-E1 (correlation check on 1000 HH-RLHF samples)

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-BiDPO-v1)
- **Scope Reduction:** 75% (3 BUILD_ON claims, 1 PROVE_NEW claim)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 5
- **Tools:** scientificmethod (2x hypothesis, 2x experiment), structuredargumentation (3x dialectical)

### C. Established Facts (BUILD_ON - Not Re-Verified)
1. DPO provides closed-form preference optimization without reward model
2. Multi-objective DPO is stable (MODPO demonstrates margin-based extensions work)
3. Intent-aligned AI may deplete human agency (Mitelut et al. 2023)
