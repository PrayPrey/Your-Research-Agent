# Verification Plan: Length-Dependent Distillation Objectives for Transformer-to-Mamba Conversion

**Date:** 2026-08-18
**Hypothesis ID:** H-LenDistill-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the setting of distilling a pretrained Transformer (Phi-1.5) into a Mamba-based architecture (Phi-Mamba) for long-context NLU tasks, if we compare token-level distillation objectives (CAB-style Q/K→C/B alignment) versus matrix-level objectives (MOHAWK-style attention map matching), then token-level objectives achieve superior F1 retention at extrapolated sequence lengths (≥16K) while matrix-level objectives achieve comparable or better performance at in-distribution lengths (≤4K), because token-level representations capture the functional structure of attention that generalizes to unseen lengths, whereas matrix-level objectives overfit to specific attention values that degrade under length extrapolation.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in F1 retention between token-level and matrix-level distillation objectives across sequence lengths (4K, 16K, 32K). The interaction term (Objective Type × Sequence Length) is not statistically significant at p<0.05.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench (standard) | Standard long-context NLU benchmark with single-doc QA tasks supporting 4K-32K evaluation |
| **Model** | Phi-Mamba | Standard target architecture from MOHAWK with modifications enabling fair objective comparison |

**Dataset Details:**
- Source: THUDM/LongBench (HuggingFace)
- Path: huggingface:THUDM/LongBench

**Model Details:**
- Type: Modified Mamba-2 (SSM)
- Source: goombalab/phi-mamba + wph6/CAB (custom integration)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Phi-1.5 Teacher | 100% (reference) | Various NLU benchmarks |
| MOHAWK Phi-Mamba | ~85% of Phi-1.5 | Various NLU benchmarks (2K length) |
| Random Init Mamba | Control | Training from scratch |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Phi-1.5 attention at 32K is not fully degenerate | LMs often extrapolate to 2-4x training length | Both methods fail equally; hypothesis vacuously true |
| A2 | Phi-Mamba can faithfully learn attention patterns | MOHAWK demonstrates success at 2K | Architecture is bottleneck, not objective |
| A3 | 1.5B tokens per condition is sufficient | CAB uses 200M-4B; MOHAWK uses 3B | Results show noise rather than true differences |
| A4 | LongBench generalizes to other long-context tasks | Standard benchmark used across prior work | Conclusions limited to single-doc QA |
| A5 | Fair comparison using same training setup | Both use same Phi-Mamba and C4 | Implementation confounds may affect results |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First controlled comparison of distillation objective types (matrix vs token-level) across sequence lengths for Transformer-to-Mamba conversion.

**Key Innovation:** Unified framework testing whether optimal distillation objective depends on target sequence length, with length-generalization framing.

**Differentiation:**
- MOHAWK: Validates matrix-level at single length; we compare across lengths
- CAB: Validates token-level; we test against matrix-level under controlled conditions
- Hybrid Analysis: Compares architectures; we compare distillation objectives

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | pending |
| H-M2 | Mechanism | MUST_WORK | H-M1 | pending |
| H-M3 | Mechanism | MUST_WORK | H-M2 | pending |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Unified Framework Existence**

**Statement**: Under the setting of Transformer-to-Mamba distillation, if both matrix-level and token-level objectives are implemented in a unified Phi-Mamba framework, then controlled comparison of their effects on F1 retention is possible, because the same target architecture eliminates confounds from architectural differences.

**Rationale**: This validates feasibility before investing in full experiments. MOHAWK and CAB use different codebases; we need unified implementation for fair comparison.

**Variables**:
- Independent: Distillation objective type (matrix-level vs token-level)
- Dependent: Implementation success (both trainable in same framework)
- Controlled: Target architecture (Phi-Mamba), source model (Phi-1.5)

**Verification Protocol**:
1. Fork MOHAWK codebase and integrate CAB-style token-level alignment
2. Verify both objectives compute gradients correctly on small batch
3. Train 100M token smoke test for each objective
4. Confirm loss decreases and no NaN/divergence

**Success Criteria (PoC)**:
- Primary: Both objectives train without errors for 100M tokens
- Secondary: Loss curves show expected learning behavior

**Failure Response**: IF fails: PIVOT to using separate codebases with matched hyperparameters

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1

---
**H-M1: Training Distribution Bound**

**Statement**: Under the condition that Phi-1.5 was trained on 2048-length sequences, if we evaluate attention patterns at 16K-32K, then attention exhibits extrapolation artifacts (high entropy, sparse patterns), because the model has never seen such lengths during training.

**Rationale**: This tests the first causal step - whether long sequences are truly out-of-distribution for the teacher. If attention is structured at 32K, the length extrapolation premise is weakened.

**Variables**:
- Independent: Sequence length (2K, 4K, 8K, 16K, 32K)
- Dependent: Attention entropy, pattern structure metrics
- Controlled: Input text domain (C4 samples)

**Verification Protocol**:
1. Sample 500 documents from C4 validation at each length
2. Extract attention patterns from Phi-1.5 middle layers
3. Compute attention entropy and sparsity metrics
4. Plot entropy vs length, identify inflection point

**Success Criteria (PoC)**:
- Primary: Attention entropy increases significantly beyond 4K
- Secondary: Sparsity patterns emerge at 16K+ (top-k concentration)

**Failure Response**: IF fails (attention remains structured): EXPLORE whether structured 32K attention still degrades during distillation

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---
**H-M2: Representation Robustness**

**Statement**: Under token-level distillation (CAB-style Q/K→C/B alignment), if we compare hidden representations at 4K vs 16K vs 32K, then token-level representations remain stable across lengths, because Q/K projections encode local attention intent that is length-invariant.

**Rationale**: This tests whether token-level representations are actually more robust to length extrapolation than full attention maps, validating the mechanism claim.

**Variables**:
- Independent: Sequence length (4K, 16K, 32K), distillation type
- Dependent: Hidden state drift (L2 distance student vs teacher)
- Controlled: Layer selection (middle layers), alignment method

**Verification Protocol**:
1. Train token-level distilled model at each length (500M tokens)
2. Extract per-layer hidden states on LongBench samples
3. Compute L2 drift between student and teacher outputs
4. Compare drift slopes: token-level vs matrix-level

**Success Criteria (PoC)**:
- Primary: Token-level drift slope < matrix-level drift slope
- Secondary: Drift remains bounded at 32K for token-level

**Failure Response**: IF fails: EXPLORE whether drift correlates with downstream F1

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---
**H-M3: Objective-Task Match**

**Statement**: Under the full distillation setup with 1.5B tokens per condition, if we evaluate F1 retention on LongBench at 4K/16K/32K, then token-level achieves superior retention at ≥16K while matrix-level matches at ≤4K, because token-level alignment transfers robust local representations while matrix-level captures noise at extrapolated lengths.

**Rationale**: This is the main experimental test combining the mechanism steps into the final prediction. Success here validates the complete hypothesis.

**Variables**:
- Independent: Distillation objective × Sequence length (2×3 factorial)
- Dependent: F1 retention ratio (student F1 / teacher F1)
- Controlled: Training budget (1.5B tokens), architecture, data

**Verification Protocol**:
1. Train 6 models: 2 objectives × 3 lengths (1.5B tokens each)
2. Evaluate each on LongBench single-doc QA at matching length
3. Compute F1 retention ratios
4. Run 2×3 ANOVA with interaction term
5. Test predictions P1 (4K), P2 (16K), P3 (32K)

**Success Criteria (PoC)**:
- Primary: Interaction term (Objective × Length) significant at p<0.05
- Secondary: P2 and P3 effect sizes match predictions (≥3 and ≥5 F1 points)

**Failure Response**: IF fails: Document as negative result, analyze where mechanism breaks

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---

## 3. Risk Analysis

### 3.1 Risk Identification

| ID | Risk | Source | Severity | Description |
|----|------|--------|----------|-------------|
| R1 | Degenerate Attention | A1 | High | Phi-1.5 attention at 32K may be fully degenerate (no signal) |
| R2 | Architecture Bottleneck | A2 | Medium | Phi-Mamba may not faithfully learn attention patterns |
| R3 | Training Budget Insufficient | A3 | Medium | 1.5B tokens may not reach convergence |
| R4 | Benchmark Limitation | A4 | Low | LongBench single-doc QA may not generalize |
| R5 | Implementation Confounds | A5 | Medium | Different objective implementations may have hidden differences |

### 3.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-M1, H-M2, H-M3 | Invalidates length extrapolation premise |
| R2 | H-E1, H-M2 | Architecture becomes bottleneck instead of objective |
| R3 | H-M1, H-M2, H-M3 | Results show noise, not true differences |
| R4 | H-M3 | Conclusions limited to single-doc QA |
| R5 | All | Confounds may explain differences instead of objectives |

### 3.3 Mitigation Strategies

**R1: Degenerate Attention (High)**
- **Prevention**: Pre-experiment attention entropy check at 4K/16K/32K
- **Detection**: Measure attention entropy before training starts
- **Response**: If entropy is uniform at 32K, reduce max length to 16K
- **Early Warning**: Entropy > 0.9 at 32K indicates degeneration

**R2: Architecture Bottleneck (Medium)**
- **Prevention**: Verify MOHAWK published results reproduce at 2K
- **Detection**: Compare our H-E1 baseline to published numbers
- **Response**: If architecture limits, document as architecture paper contribution
- **Early Warning**: H-E1 fails to match published MOHAWK performance

**R3: Training Budget Insufficient (Medium)**
- **Prevention**: Monitor loss curves for convergence
- **Detection**: Loss still decreasing at 1.5B token mark
- **Response**: Extend training to 2B-3B tokens if needed
- **Early Warning**: Loss plateaus not reached by 1B tokens

**R4: Benchmark Limitation (Low)**
- **Prevention**: Include secondary metrics (perplexity, hidden drift)
- **Detection**: F1 trends don't match perplexity trends
- **Response**: Document as limitation, recommend follow-up study
- **Early Warning**: High variance in F1 across task types

**R5: Implementation Confounds (Medium)**
- **Prevention**: Minimize code differences, same hyperparameters
- **Detection**: Ablation study varying learning rate, batch size
- **Response**: Document confounds, recommend controlled replication
- **Early Warning**: Large sensitivity to hyperparameters

### 3.4 Risk Summary

| ID | Risk | Severity | Likelihood | Priority | Mitigation |
|----|------|----------|------------|----------|------------|
| R1 | Degenerate Attention | High | Medium | **Critical** | Pre-experiment entropy check |
| R2 | Architecture Bottleneck | Medium | Low | Medium | Reproduce MOHAWK baseline |
| R3 | Training Budget | Medium | Medium | Medium | Monitor convergence, extend if needed |
| R4 | Benchmark Limitation | Low | Low | Low | Include secondary metrics |
| R5 | Implementation Confounds | Medium | Medium | Medium | Minimal code differences |

**Critical Risks: 1** | **High: 0** | **Medium: 3** | **Low: 1**

---

## 4. Execution

### 4.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Unified Framework Existence  │
    │  Gate: MUST_WORK                    │
    └─────────────────┬───────────────────┘
                      │
                      ▼
[Level 1 - Mechanism Step 1]
    ┌─────────────────────────────────────┐
    │  H-M1: Training Distribution Bound  │
    │  Gate: MUST_WORK                    │
    └─────────────────┬───────────────────┘
                      │
                      ▼
[Level 2 - Mechanism Step 2]
    ┌─────────────────────────────────────┐
    │  H-M2: Representation Robustness    │
    │  Gate: MUST_WORK                    │
    └─────────────────┬───────────────────┘
                      │
                      ▼
[Level 3 - Mechanism Step 3]
    ┌─────────────────────────────────────┐
    │  H-M3: Objective-Task Match         │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 | Parallelization: None (sequential)
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|------------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism |
| 2 | H-M2 | H-M1 | MUST_WORK | Mechanism |
| 3 | H-M3 | H-M2 | MUST_WORK | Mechanism |

### 4.3 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Both objectives train without errors | STOP: Reassess architecture |
| H-M1 | MUST_WORK | Attention entropy increases with length | PIVOT: Reduce max length to 16K |
| H-M2 | MUST_WORK | Token drift slope < matrix drift slope | EXPLORE: Check if drift correlates with F1 |
| H-M3 | MUST_WORK | Interaction term significant at p<0.05 | Document as negative result |

### 4.4 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses, 5 Weeks Total
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2    │ W3-4    │ W5      │
──────────────────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation   │         │         │         │
  H-E1 (Framework)    │ ████████│         │         │
  [Gate 1]            │        ◆│         │         │
──────────────────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms   │         │         │         │
  H-M1 (Distribution) │         │ ████████│         │
  H-M2 (Robustness)   │         │     ████│         │
  H-M3 (Match)        │         │         │ ████    │
  [Gate 2]            │         │         │    ◆    │
══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 4.5 Critical Path Analysis

**Critical Path**: H-E1 → H-M1 → H-M2 → H-M3

**Total Duration**: 5 weeks
- H-E1: 2 weeks (framework setup, smoke tests)
- H-M1: 1.5 weeks (attention entropy analysis)
- H-M2: 1 week (drift measurement, 500M token training)
- H-M3: 2.5 weeks (full 6-condition training, statistical analysis)

**Note**: H-M1/H-M2 can overlap partially with H-M3 setup. Compressed to 5 weeks total.

**Slack**: 0 weeks (all hypotheses on critical path)

### 4.6 Resource Summary

| Resource | Allocation | Notes |
|----------|------------|-------|
| GPU Hours | ~4 weeks × 8 A100s | 9B tokens total across 6 conditions |
| Storage | ~500GB | Model checkpoints, attention logs |
| Compute Budget | 1.5B tokens/condition | 6 conditions total |
| Evaluation | LongBench single-doc QA | Full test set (~2K samples) |

### 4.7 Execution Order

1. **Week 1-2**: H-E1 - Implement unified framework, verify both objectives train
2. **Week 2**: Gate 1 - Both objectives converge? → Proceed / Reassess
3. **Week 3**: H-M1 - Attention entropy analysis at 4K/16K/32K
4. **Week 3-4**: H-M2 - Train 500M token models, measure drift
5. **Week 4-5**: H-M3 - Train full 6-condition experiment (1.5B each)
6. **Week 5**: Gate 2 - Run ANOVA, evaluate predictions P1-P3
7. **Final**: Document results, proceed to Phase 5 baseline comparison

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim**: Token-level distillation objectives achieve superior F1 retention at extrapolated sequence lengths (≥16K) because they capture functional attention structure that generalizes to unseen lengths.

**Supporting Evidence**:
1. CAB's design explicitly avoids O(L²) attention map materialization
2. Token-level Q/K projections encode local attention intent
3. MOHAWK's matrix alignment explicitly optimizes attention map matching (includes noise)

**Strengths**:
- Clear causal mechanism with 3 testable steps
- Builds on established work (MOHAWK, CAB)
- Predictions specify quantitative effect sizes (2, 3, 5 F1 points)

**Expected Outcomes**:
- P1: At 4K, matrix ≥ token (within 2 F1 points)
- P2: At 16K, token > matrix by ≥3 F1 points
- P3: At 32K, token > matrix by ≥5 F1 points

### 5.2 Antithesis

**Null Hypothesis (H0)**: There is no significant difference in F1 retention between token-level and matrix-level distillation objectives across sequence lengths. The interaction term (Objective Type × Sequence Length) is not statistically significant at p<0.05.

**Counter-Arguments**:
1. Attention maps may contain structured signal even at 32K if Phi-1.5 extrapolates well
2. Matrix-level objectives might capture richer global patterns than token-level
3. Both methods may hit the same Phi-Mamba architecture ceiling

**Potential Failure Points**:
- R1: Phi-1.5 attention fully degenerate at 32K (both methods fail)
- R2: Phi-Mamba architecture is the bottleneck
- R3: Training budget insufficient for reliable comparison

**Conditions Under Which H0 Supported**:
- Interaction term (Objective × Length) not significant at p<0.05
- P2 and P3 effect sizes below thresholds
- Hidden state drift slopes not significantly different

### 5.3 Synthesis

**Balanced Assessment**:
The hypothesis H-LenDistill-v1 presents a testable claim about length-dependent distillation objectives. The null hypothesis raises valid concerns about attention extrapolation quality and architecture limitations.

**Resolution Path**:
1. **H-E1 (Foundation)**: Validates both objectives implementable before mechanism testing
2. **H-M1 (Distribution Bound)**: Tests prerequisite - attention degradation at long lengths
3. **H-M2 (Representation)**: Tests mechanism - drift comparison between objectives
4. **H-M3 (Match)**: Tests prediction - full factorial with statistical analysis

**Conditions for Thesis Support**:
- All MUST_WORK gates pass
- Interaction term significant at p<0.05
- P2 and P3 effect sizes achieved

**Conditions for Antithesis Support**:
- H-E1 fails (implementation infeasible)
- H-M1 fails (attention structured at 32K - no extrapolation problem)
- Interaction term not significant

**Nuanced Outcomes**:
1. **Full Support**: All pass → Token-level superior at long lengths
2. **Partial Support**: H-M3 shows smaller effect sizes → Refinement needed
3. **No Support**: H-M1 shows no attention degradation → Premise invalid

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Both objectives implementable | Implementation details may differ | H-E1 smoke test |
| Mechanism | Attention degrades at long lengths | May extrapolate well | H-M1 entropy analysis |
| Transfer | Token-level more robust | May capture less information | H-M2 drift comparison |
| Performance | Significant interaction effect | No effect or reverse | H-M3 2×3 ANOVA |

**Overall Robustness Score**: High
- Clear falsification criteria
- Sequential gate structure allows early failure detection
- Quantified predictions enable precise statistical testing

**Confidence in Verification Plan**: 0.80

---

## 6. Summary

### 6.1 Executive Summary

**Main Hypothesis**: Token-level distillation objectives achieve superior F1 retention at extrapolated sequence lengths
- ID: H-LenDistill-v1, Confidence: 0.80

**Verification Structure**:
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 5 weeks
- Critical Gates: 4 decision points (all MUST_WORK)

**Risk Assessment**: Medium
- Primary concerns: Degenerate attention at 32K (R1), training budget (R3)

**Immediate Action**: Begin Phase 1 with H-E1 (unified framework implementation)

### 6.2 Final Summary

**Verification Execution Order**:

**Phase 1: Foundation** (2 weeks)
- H-E1: Unified framework implementation and smoke test
- Gate 1: Both objectives train without errors

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Attention entropy analysis across lengths
- H-M2: Hidden state drift comparison
- H-M3: Full 2×3 factorial experiment (1.5B tokens/condition)
- Gate 2: Statistical significance at p<0.05

### 6.3 Conclusions

**Key Achievements**:
- 4 hypotheses generated across 2 phases
- H0 addressed: No significant difference in F1 retention
- 40% scope reduction from Established Facts (BUILD_ON claims skipped)

**Critical Decision Points**:
1. Gate 1: H-E1 must pass → FAIL: Reassess architecture
2. Gate 2: H-M1 must pass → FAIL: Reduce max length or document as negative result

**Open Questions** (from Phase 2A):
- Exact crossover point in 8K-16K range
- Whether hybrid objectives outperform pure approaches
- Generalization to other source models (Llama, Mistral)

**Recommendations**:
1. Start Phase 1 immediately with H-E1 implementation
2. Run pre-experiment attention entropy check before H-M training
3. Reserve compute buffer for potential training extension

### 6.4 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml
- Main Hypothesis ID: H-LenDistill-v1

**B. MCP Tool Usage**
- scientificmethod: 2 calls (hypothesis, experiment stages)
- Total MCP calls: 2

**C. Compute Requirements**
- 9B tokens total (6 conditions × 1.5B)
- ~4 weeks on 8×A100 GPUs

---

## 7. State & Tasks

### 7.1 Verification State

**Status**: Generated
**File**: `verification_state.yaml`
**Schema**: v2.0

| Field | Value |
|-------|-------|
| Total Hypotheses | 4 |
| Ready | 1 (H-E1) |
| Blocked | 3 (H-M1, H-M2, H-M3) |
| Current Phase | Phase 2C |
| Next Hypothesis | H-E1 |

### 7.2 Pipeline Tasks

| Task | Status | ID |
|------|--------|-----|
| Phase 2B - Planning | done | 286b4c0b-3c1d-4045-904f-3a887095ce36 |
| Phase 2C - Experiment | doing | 8560f238-9f91-4eaf-bfd3-c0a797be0add |

### 7.3 Hypothesis Tasks

| Hypothesis | Type | Task ID |
|------------|------|---------|
| H-E1 | EXISTENCE | 6ce038b6-7c3c-4c04-b9cc-a949008307f7 |
| H-M1 | MECHANISM | 314efd47-cca5-469d-b73b-2ac46a15c245 |
| H-M2 | MECHANISM | c6a0ba8f-4094-4879-bf0a-b5bd5237f83a |
| H-M3 | MECHANISM | abafda43-ee51-4921-8208-d95bd38c73b4 |

---
