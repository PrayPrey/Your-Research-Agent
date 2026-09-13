# Phase 2B: Verification Plan
## H-DualAccessibility-v1 - Dual-Axis Dataset Accessibility Profiler

**Generated**: 2026-07-10T17:03:10Z  
**Pipeline Project**: `969e983e-0a40-4910-bedf-4c70577c6f04`  
**Main Hypothesis**: Lightweight dual-failure-mode predictor combining segment-level MSI (memory stress) with GPU-normalized SAT (throughput variance) achieves ≥20% macro-F1 improvement over VeritasEst-only + timing baseline via orthogonal dual-axis 4-quadrant routing.

---

## Executive Summary

This verification plan decomposes the main hypothesis into **4 sub-hypotheses** (H-E1, H-E2, H-M1, H-M2) plus Phase 5 baseline comparison (H-C1). The critical path validates:
1. **Existence** (H-E1/E2): MSI and SAT can be measured accurately from lightweight profiling
2. **Mechanism** (H-M1/M2): Orthogonality enables 4-quadrant diagnostic routing
3. **Comparative** (Phase 5): Dual-axis achieves ≥20% macro-F1 improvement

**Timeline**: 12 weeks (3 months) | **Critical Path**: H-E1 → H-M1 → H-M2 → Phase 5 (10 weeks)  
**Risk Level**: Moderate (30% orthogonality failure risk, mitigated by contingency thresholds)

---

## Sub-Hypotheses Breakdown

### H-E1: Segment-level MSI from 3-iteration sampling
**Type**: EXISTENCE | **Gate**: MUST_WORK | **Status**: READY  
**Archon Task**: `302fe353-3274-4ac0-ad1b-bab7242aace5`

**Statement**: 3-iteration stratified sampling (1st iteration, post-optimizer.step, P50/P75/P95/P99 length bins) predicts 10-iteration segment peak memory with ≤10% median relative error for CNNs, ≤15% for transformers.

**Rationale**: VeritasEst demonstrated 2-iteration optimizer state stabilization; stratified sampling addresses M_act variance via length quantiles. Segment-level simulation (BFC allocator) is non-negotiable for memory prediction (tensor sums fail under Adam optimizer).

**Success Criteria**:
- Median error ≤10% for CNNs (validated on 8 architectures)
- Median error ≤15% for transformers (contingency threshold)
- 95th percentile error ≤25% across all models
- Validation across 48 configs (16 models × 5 optimizers × 3 datasets with varying length distributions)

**Falsification**: If median >15% or P95 >30%, stratified sampling is insufficient → extend to 5-iteration or add confidence intervals.

**Prerequisites**: None (can start immediately)

**Estimated Duration**: 3 weeks (Tier 2 complexity)

**Risks**:
- Allocator simulation generalization to transformers (30% probability) → Contingency: ≤15% acceptable
- Gradient accumulation edge cases (20% probability) → Scope to validated architectures

---

### H-E2: GPU-normalized SAT measures throughput variance
**Type**: EXISTENCE | **Gate**: MUST_WORK | **Status**: READY  
**Archon Task**: `088881a9-a0f3-4af9-9723-93ae24919a0e`

**Statement**: GPU-normalized SAT (P95/Median batch time × GPU utilization fraction) causally predicts ≥15% epoch-time degradation with ≥80% precision when GPU utilization <90%.

**Rationale**: High batch time variance under high GPU utilization indicates data loading bottlenecks (GPU idle). Low utilization indicates non-accessibility system noise. GPU normalization isolates accessibility-related variance.

**Success Criteria**:
- Precision ≥80% for predicting ≥15% epoch-time degradation
- Recall ≥70% (acceptable false negatives for conservative prediction)
- Synthetic jitter falsification: injecting dataloader sleep() increases SAT only when GPU utilization drops (validates causal link)

**Falsification**: If high SAT (>1.5) does not predict degradation with ≥80% precision, SAT is contaminated by non-accessibility variance → Multi-source decomposition needed.

**Prerequisites**: None (can run parallel with H-E1)

**Estimated Duration**: 2 weeks (Tier 2 complexity)

**Risks**:
- System-level noise contamination (30% probability) → Mitigation: Multi-source decomposition (NVML + CUDA events + dataloader queue depth)
- GPU utilization metric reliability (20% probability) → Validate across diverse hardware configs

---

### H-M1: Statistical orthogonality of MSI and SAT
**Type**: MECHANISM | **Gate**: MUST_WORK | **Status**: NOT_STARTED  
**Archon Task**: `538d2be4-8903-4409-9fd9-483e9a10050a`

**Statement**: Pearson correlation between segment-accurate MSI and epoch-time degradation is <0.3 across natural workloads (48 configs: 16 models × 5 optimizers × 3 datasets), demonstrating statistical independence of memory and throughput failure modes.

**Rationale**: H-E3 failure demonstrated orthogonality empirically (WildChat OOM without throughput variance, PersonaChat stable despite lower SAT). Statistical validation confirms axes measure independent bottlenecks.

**Success Criteria**:
- |r| < 0.3 under natural workloads (fixed-length + long-tail length distributions)
- Contingency: |r| = 0.3-0.5 acceptable IF mitigation strategies remain distinct (batch reduction ≠ data loading optimization)
- Synthetic jitter increases correlation (validates SAT measures data loading, not memory)

**Falsification**: If r > 0.5 under natural workloads, axes are NOT orthogonal → Reframe as unified accessibility score with multi-factor decomposition.

**Prerequisites**: H-E1 (segment-accurate MSI), H-E2 (validated SAT)

**Estimated Duration**: 1 week (Tier 1 - reuses H-E1/E2 data)

**Risks**:
- Fundamental orthogonality assumption failure (30% probability) → HIGH IMPACT, but mitigated by contingency threshold and fallback to unified score

---

### H-M2: Four-quadrant diagnostic routing
**Type**: MECHANISM | **Gate**: SHOULD_WORK | **Status**: NOT_STARTED  
**Archon Task**: `d5d50c0d-8856-4c4e-88d9-c6509393a4d6`

**Statement**: 4-quadrant routing (Safe, OOM-risk, Throughput-risk, Dual-risk) based on MSI and SAT thresholds provides actionable mitigation strategies (batch size reduction for OOM, data loading optimization for throughput, both for dual-risk).

**Rationale**: H-E1 WildChat case demonstrated need for dual mitigation (OOM → reduce batch to 8, timeout → pre-download). Single-axis predictors provide failure yes/no but not diagnostic WHY.

**Success Criteria**:
- Clear quadrant boundaries via threshold tuning (e.g., MSI=0.7, SAT=1.5)
- Mitigation strategies validated: OOM-risk cases resolve via batch reduction, Throughput-risk cases resolve via data optimization
- Actionability: practitioners can apply recommendations without deep expertise

**Falsification**: If quadrant routing does not reduce false-safe misclassifications by ≥20% compared to binary prediction, complexity is unjustified → Simplify to 2-class (Safe/Unsafe).

**Prerequisites**: H-E1, H-E2, H-M1 (orthogonality confirms independent axes)

**Estimated Duration**: 2 weeks (Tier 2 complexity)

**Risks**:
- Threshold generalization across workloads (40% probability) → Mitigation: Architecture-specific calibration acceptable
- Test set imbalance (25% probability) → Deliberate failure experiments (5 OOM-only, 5 Dual-risk)

---

## Phase 5: H-C1 Baseline Comparison (DETERMINES_SUCCESS)

**Statement**: Dual-axis routing achieves ≥20% macro-F1 improvement over VeritasEst-only + 20-batch timing baseline on 4-class accessibility classification (80-sample test set: 20 Safe, 20 OOM-risk, 20 Throughput-risk, 20 Dual-risk) with statistical significance p<0.05.

**Gate Type**: DETERMINES_SUCCESS (main hypothesis validation)  
**Archon Task**: `9bf23b58-d946-4fb5-b836-d211fc5aba0f`

**Baselines**:
1. **VeritasEst-only + 20-batch timing**: CPU-based segment simulation for OOM prediction + empirical epoch-time extrapolation for throughput risk
2. **Single-regression unified**: Train single regressor predicting both OOM probability and epoch-time slowdown from profiled features
3. **Dual-axis routing (proposed)**: Independent MSI and SAT classifiers with 4-quadrant decision boundaries

**Success Criteria**:
- Primary: Macro-F1(dual-axis) - Macro-F1(baseline) ≥ 0.20 with p<0.05 (bootstrap test)
- Contingency: ≥ 0.15 acceptable for Tier-2 venue (MLSys, CoLM)
- Falsification: If improvement <0.10, simplify to single-regression

**Prerequisites**: All MUST_WORK gates passed (H-E1, H-E2, H-M1)

**Estimated Duration**: 4 weeks (Tier 3 complexity)

---

## Dependency Graph (DAG)

```
h-e1 (READY) ────┐
                  ├──→ h-m1 (NOT_STARTED) ──┐
h-e2 (READY) ────┘                           ├──→ h-m2 (NOT_STARTED) ──→ Phase 5 (H-C1)
                                             │
                                             └──→ (parallel path)
```

**Execution Waves**:
1. **Wave 1** (Week 1-3): H-E1, H-E2 in parallel (both READY)
2. **Wave 2** (Week 4): H-M1 (after Wave 1 completes)
3. **Wave 3** (Week 5-6): H-M2 (after H-M1)
4. **Phase 5** (Week 7-10): Baseline comparison (after all MUST_WORK gates pass)

**Critical Path**: H-E1 (3 weeks) → H-M1 (1 week) → H-M2 (2 weeks) → Phase 5 (4 weeks) = **10 weeks**

**Parallel Opportunities**: H-E2 runs concurrently with H-E1 (saves 2 weeks vs sequential)

---

## Risk Analysis Summary

| Hypothesis | Risk Type | Probability | Impact | Mitigation |
|------------|-----------|-------------|--------|------------|
| H-E1 | Allocator generalization | 30% | Medium | Contingency threshold ≤15% for transformers |
| H-E2 | SAT noise contamination | 30% | Medium | Multi-source decomposition (NVML + CUDA events) |
| H-M1 | Orthogonality failure | 30% | **HIGH** | Contingency r<0.5 + fallback to unified score |
| H-M2 | Threshold tuning | 40% | Low | Architecture-specific calibration acceptable |
| Phase 5 | Test set imbalance | 25% | Medium | Deliberate failure experiments (5+5) |

**Highest Risk**: H-M1 orthogonality assumption failure (30% probability, HIGH impact) → Invalidates dual-axis framework, but mitigated by contingency acceptance r=0.3-0.5 and demonstrated distinct mitigation strategies.

---

## Timeline & Resource Estimate

**Total Duration**: 12 weeks (3 months)  
**Critical Path**: 10 weeks (H-E1 → H-M1 → H-M2 → Phase 5)

**Compute Budget** (from Phase 2A synthesis):
- ~650 GPU-hours across all experiments
- Estimated cost: $700 (assuming $1/GPU-hour cloud pricing)

**Researcher Effort**:
- Phase 2C (Experiment Design): 1 week per hypothesis = 4 weeks
- Phase 3 (Implementation Planning): 1-2 weeks per hypothesis = 6 weeks
- Phase 4 (Coding & Validation): 3 weeks (H-E1) + 2 weeks (H-E2) + 1 week (H-M1) + 2 weeks (H-M2) = 8 weeks
- Phase 5 (Baseline Comparison): 4 weeks
- **Total**: ~22 weeks (5.5 months) including planning and implementation

---

## Dialectical Analysis: Thesis-Antithesis-Synthesis

**Thesis**: Dual-axis framework is necessary because OOM and throughput are orthogonal failure modes requiring independent prediction and mitigation strategies.

**Antithesis**: A simpler unified score (single regression) could capture both failure modes without dual-axis complexity. Why add geometric framework overhead?

**Synthesis**: The ≥20% macro-F1 improvement bar empirically adjudicates this tension. If dual-axis routing achieves the improvement, complexity is justified by diagnostic value (actionable mitigation: batch reduction vs data optimization vs both). If improvement <15%, simplify to single-regression. Contingency thresholds (≥15% for Tier-2 venue) provide venue-flexible resolution.

**Counter-Synthesis Stress Test**:
- **Skeptic**: "Even if orthogonality holds (r<0.3), what if thresholds are workload-dependent? MSI=0.7 might be OOM-risk for transformers but Safe for CNNs."
- **Response**: Architecture-specific calibration is acceptable refinement (Phase 6 discussion). Initial validation scoped to "validated architectures"; MoE/Flash Attention explicitly excluded. Threshold generalization tested via 8 transformer + 8 CNN diversity.

---

## Key Assumptions & Contingencies

From Phase 2A refinement (Section 1.4):

| ID | Assumption | Consequence if Violated | Contingency |
|----|------------|-------------------------|-------------|
| A1 | 3-iteration sampling generalizes within ≤10% error | MSI unreliable | Extend to 5-iteration or add confidence intervals |
| A2 | OOM and throughput orthogonal (\|r\|<0.3) | Dual-axis collapses | Reframe as unified score with multi-factor analysis |
| A3 | GPU-normalized SAT isolates accessibility variance | False positives | Multi-source decomposition (CUDA events, queue depth) |
| A4 | Ground truth labels obtainable via 10-iteration traces | Test set contamination | Use held-out datasets unseen during development |
| A5 | BFC allocator generalizes to transformers | Transformer MSI >15% error | Architecture-specific calibration, scope to validated architectures |

---

## Next Steps (Phase 2C)

For each sub-hypothesis (H-E1, H-E2, H-M1, H-M2):
1. Generate detailed experiment specification (Level 1.5 brief)
2. MCP-powered implementation search for segment simulator, SAT instrumentation, correlation analysis
3. Validation protocol design with success/failure thresholds
4. Transition to Phase 3 for PRD/Architecture generation

**First Target**: H-E1 (READY status, no prerequisites)

---

## Appendix: Archon Task Mapping

**Pipeline Project**: `969e983e-0a40-4910-bedf-4c70577c6f04`

**Pipeline Phase Tasks**:
- Phase 0: `4520ecb4-383d-44d5-9800-bd7fab1f67a1` (done)
- Phase 1: `6b731d6b-04df-431c-855c-f55bce5561ae` (done)
- Phase 2A: `14db7984-7f3d-43bd-9fac-28dc586801e4` (done)
- Phase 2B: `157b61f9-2d0d-4a4d-a44d-cceff48ce8f5` (doing)
- Phase 2C: `b4eb551b-1b85-48c8-8ba5-e061c242803b` (todo)
- Phase 3: `bfe38ab8-e37c-4499-8924-c96132f99535` (todo)
- Phase 4: `e8f2faa9-9efe-4f9e-b7cb-73e55cc53e63` (todo)
- Phase 5: `9bf23b58-d946-4fb5-b836-d211fc5aba0f` (todo)
- Phase 6: `28988b81-724d-4350-87a9-8055a589704b` (todo)

**Hypothesis Parent Tasks**:
- H-E1: `302fe353-3274-4ac0-ad1b-bab7242aace5` (feature: h-e1)
- H-E2: `088881a9-a0f3-4af9-9723-93ae24919a0e` (feature: h-e2)
- H-M1: `538d2be4-8903-4409-9fd9-483e9a10050a` (feature: h-m1)
- H-M2: `d5d50c0d-8856-4c4e-88d9-c6509393a4d6` (feature: h-m2)
