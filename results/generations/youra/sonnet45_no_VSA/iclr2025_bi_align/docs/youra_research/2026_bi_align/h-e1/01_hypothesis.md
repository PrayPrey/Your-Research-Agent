# Phase 2A: Hypothesis Definition
## H-E1: Segment-level MSI from 3-iteration sampling

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Generated**: 2026-07-10T16:00:00Z  
**Status**: IN_VERIFICATION

---

## 1. Hypothesis Statement

**Full Statement**: 
3-iteration stratified sampling (1st iteration, post-optimizer.step, P50/P75/P95/P99 length bins) predicts 10-iteration segment peak memory with ≤10% median relative error for CNNs, ≤15% for transformers.

**Short Form**:
Lightweight 3-iteration profiling + stratified sampling achieves <10-15% error vs 10-iteration ground truth for memory prediction.

---

## 2. Motivation & Context

### 2.1 Research Gap

From Phase 1 targeted research (`01_targeted_research.md`):
- **P1 Gap 2**: No lightweight sample-based profiling implementation
- **H-E1 Failure lesson**: Full dataset loading caused WildChat OOM (>10min timeout, 27GB streaming)
- **Need**: Validate that lightweight profiling (3 iterations) is accurate before scaling to full training

### 2.2 Prior Art Limitations

**VeritasEst (baseline)**:
- Uses 2-iteration optimizer state stabilization
- Does NOT address activation memory variance in transformers
- No stratified sampling for variable-length sequences

**pytorch_memlab**:
- Requires FULL training run (not lightweight)
- Cannot handle streaming datasets efficiently

### 2.3 Why This Hypothesis Matters

**Critical Path Position**:
- Foundation for dual-axis framework (MSI calculation)
- Blocks h-m1 (orthogonality analysis) if failed
- Validates that lightweight profiling is practical for real-world use

**Falsification Risk**:
If median error >15%, lightweight profiling is insufficient → must use full training runs (defeats purpose of lightweight approach)

---

## 3. Hypothesis Type: EXISTENCE

**Definition**: Validates that a measurement or phenomenon can be reliably observed.

**For h-e1**: Tests whether segment-level memory can be accurately predicted from 3 iterations (existence of accurate lightweight profiling method).

**Success Gate**: MUST_WORK
- If fails: Blocks downstream hypotheses h-m1, h-m2
- Contingency: Extend to 5-iteration or add confidence intervals

---

## 4. Variables & Dependencies

### 4.1 Independent Variables
- **Profiling iterations**: 3 (lightweight) vs 10 (ground truth)
- **Sampling strategy**: Stratified (P50/P75/P95/P99) vs uniform
- **Architecture type**: CNN vs Transformer
- **Optimizer**: Adam, AdamW, SGD

### 4.2 Dependent Variable
- **Relative error**: |predicted_memory - ground_truth_memory| / ground_truth_memory

### 4.3 Control Variables
- Dataset splits (standard test sets)
- Batch size (fixed per model)
- Hardware (A100 40GB)
- Memory measurement method (torch.cuda.memory_stats)

### 4.4 Confounds to Address
- **Length variance**: Stratified sampling for transformers
- **Optimizer workspace**: Post-optimizer.step measurement
- **Allocator fragmentation**: Segment-level (not tensor-level) tracking

---

## 5. Predicted Outcomes

### 5.1 Success Scenario (H1 supported)
- Median relative error ≤10% for CNNs
- Median relative error ≤15% for transformers
- P95 error ≤25% across all models
- Statistically significant improvement over 2-iteration baseline (p<0.05)

**Interpretation**: Lightweight profiling is accurate → proceed to h-m1

### 5.2 Failure Scenario (H0 not rejected)
- Median relative error >15%
- P95 error >30%

**Interpretation**: 3 iterations insufficient → contingency actions:
1. Extend to 5-iteration sampling
2. Add confidence intervals (±20% tolerance)
3. Architecture-specific calibration

### 5.3 Partial Success
- CNNs pass (≤10%) but transformers fail (>15%)

**Interpretation**: Stratified sampling insufficient for activation variance → revise binning strategy or increase samples per bin

---

## 6. Testability & Falsification

### 6.1 Falsification Criteria
- **Quantitative threshold**: Median error >15% across 48 configs
- **Statistical test**: Wilcoxon signed-rank test, p<0.05
- **Practical threshold**: P95 >30% (too high for production use)

### 6.2 Evidence Required
- Ground truth memory values (10-iteration profiling)
- Predicted memory values (3-iteration + stratified)
- Error distribution across 16 architectures × 3 optimizers

### 6.3 Timeline
- Data collection: 50 GPU-hours (ground truth) + 3 GPU-hours (lightweight)
- Analysis: 1 day
- Total: ~3 days end-to-end

---

## 7. Connection to Research Question

**Original Research Question** (from Phase 1):
How can we predict memory requirements for deep learning training without full dataset profiling?

**H-E1 Contribution**:
- Validates that 3-iteration sampling is accurate (existence proof)
- Establishes error bounds for lightweight profiling
- Enables MSI calculation for downstream routing hypotheses

**Dependency Chain**:
- H-E1 (this) → H-M1 (orthogonality) → H-M2 (quadrant coverage) → Phase 5 baseline comparison

---

## 8. Key Assumptions

1. **Optimizer state stabilizes by iteration 2** (from VeritasEst)
2. **Segment-level tracking captures allocator fragmentation** (PyTorch BFC allocator)
3. **Stratified sampling covers activation variance** (from length distribution)
4. **10-iteration profiling is "ground truth"** (validated by VeritasEst as stable)

**Risk**: If any assumption fails, hypothesis interpretation changes.

---

## 9. Next Steps

**Phase 2B** (Verification Planning):
- Design statistical tests (Wilcoxon signed-rank)
- Specify dataset requirements (CIFAR-10, ImageNet-1K, WMT-14)
- Define ablations (2-iteration baseline)
- Plan confound checks (optimizer, length variance)

**Phase 2C** (Experiment Design):
- Detailed experimental protocol
- Implementation search (Archon KB, Exa)
- Compute requirements
- Risk mitigation

---

## 10. References

### 10.1 Prior Work
- VeritasEst: 2-iteration optimizer state stabilization
- Dagdoug 2026: Sampling theory (no DL application)
- PyTorch CUDA Allocator: BFC fragmentation patterns

### 10.2 Research Context
- Phase 1 targeted research: `/docs/youra_research/01_targeted_research.md`
- H-E1 failure case: WildChat OOM from full dataset loading

---

**Document Status**: COMPLETE  
**Next Phase**: 2B (Verification Planning)  
**Estimated Duration**: Phase 2A→2B: 1 day
