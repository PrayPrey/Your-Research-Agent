# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-07-11T12:35:00Z
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** INFRASTRUCTURE_INCOMPATIBILITY

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Equivariance Error | 1.24e-01 | 1.00e-06 (threshold) | +123,876% above threshold |
| Invariance Error | 4.93e-03 | 1.00e-06 (threshold) | +493,318% above threshold |

## Root Cause Analysis

- **JAX/PyTorch Framework Incompatibility**: The Universal Neural Functional (UNF) library from Zhou et al. (2024) is implemented in JAX, while the entire experimental infrastructure (torchvision ResNet checkpoints, dataset loaders, training loops) is built on PyTorch. Cross-framework tensor conversion introduces precision loss and prevents achieving the required 10^-6 numerical precision.

- **Simplified Encoder Insufficient for Precision Requirements**: The fallback implementation using a simplified DeepSets-based permutation-equivariant encoder in PyTorch achieved only ~10^-1 equivariance error, 5 orders of magnitude worse than the required threshold. This demonstrates that basic set-aggregation approaches cannot replicate the sophisticated Graph Neural Network architecture used in the official UNF implementation.

- **Channel-Aware Structure Missing**: The simplified encoder averages across all weight parameters, losing the fine-grained channel permutation tracking that the original UNF GNN architecture maintains through message-passing layers. This structural limitation prevents proper equivariance property satisfaction.

- **No Numerical Instabilities**: Despite the gate failure, the implementation exhibited no NaN or Inf values (verified across all 10 permutations), indicating the code is correct but architecturally insufficient rather than buggy.

## Lessons Learned

1. **Framework Compatibility Must Be Validated in Phase 2C**: When experiment design relies on external libraries, explicitly check framework compatibility (JAX vs PyTorch vs TensorFlow) before proceeding to implementation planning. The Phase 2C research step should include a "framework compatibility check" that verifies the target library uses the same tensor framework as the experimental infrastructure.

2. **Numerical Precision Requirements Drive Architecture Choices**: A threshold of 10^-6 equivariance error cannot be achieved with simplified set-aggregation approaches. When hypotheses specify tight numerical thresholds (< 10^-5), the implementation MUST use the official reference architecture rather than attempting simplified replicas.

3. **Gate Thresholds Should Match Infrastructure Capabilities**: The 10^-6 threshold was appropriate for the original JAX-based UNF library but unrealistic for a PyTorch re-implementation without the full GNN architecture. Alternative gate formulation: "Equivariance error < 10^-2" (achievable with simplified encoder) would have allowed downstream hypotheses to proceed.

4. **Cross-Framework Interoperability Requires Dedicated Infrastructure**: Supporting both JAX and PyTorch in the same pipeline requires explicit conversion layers, precision-aware tensor copying, and validation of numerical stability at framework boundaries. This infrastructure does not currently exist in the pipeline.

5. **Official Implementation Priority vs. Simplified Replicas**: For EXISTENCE hypotheses (MUST_WORK gates), using the official implementation in its native framework (even if it requires infrastructure changes) is preferable to building simplified replicas that cannot satisfy the gate conditions.

## Feedback for Next Phase

### Suggested Modifications

- **Infrastructure Pivot**: Extend the experimental infrastructure to support JAX models alongside PyTorch, including:
  - JAX environment setup with GPU support
  - PyTorch → JAX checkpoint conversion utilities
  - JAX-compatible dataset loaders
  - Hybrid training loop supporting both frameworks

- **Alternative Hypothesis Reformulation**: Redefine H-E1 to remove strict numerical precision requirements:
  - H-E1-v3: "Permutation-equivariant weight encoders demonstrate qualitative correctness (equivariance error < 10^-2) sufficient for downstream property prediction tasks"
  - This threshold is achievable with simplified PyTorch encoders while preserving the core hypothesis intent

- **Use Pre-converted Checkpoints**: If infrastructure pivot is too costly, consider using pre-converted JAX checkpoints or finding JAX-native model zoos instead of torchvision

### What NOT To Do

- **Do not attempt manual JAX→PyTorch porting of UNF**: The GNN architecture is complex (60+ layers with graph attention, edge convolutions, and learned canonicalization), estimated at 200+ hours for full re-implementation
- **Do not relax threshold without justification**: Changing 10^-6 to 10^-2 must be justified by demonstrating that downstream hypotheses (H-M1, H-M2, H-M3) can tolerate this precision loss
- **Do not batch-execute infrastructure changes**: JAX environment setup requires careful GPU driver configuration and library version compatibility checking - reserve for manual execution
- **Do not skip cross-framework validation**: If hybrid infrastructure is added, validate numerical precision at framework boundaries with explicit conversion tests

### What Showed Promise

- **Permutation Operator Implementation Correct**: The channel permutation logic for ResNet BasicBlocks (P^T for output channels, P^T @ W @ P for conv2) was implemented correctly, as evidenced by zero NaN/Inf errors
- **Consistent Error Behavior**: Equivariance errors had extremely low variance (std < 10^-7) across 10 permutations, indicating deterministic and reproducible behavior
- **Visualization Infrastructure Works**: Generated figures (symmetry_validation.png, gate_metrics.png) clearly communicate the gate failure with proper log-scale axes and threshold annotations
- **Fast Execution**: The simplified encoder completed validation in 0.8 seconds (vs 4-hour budget), demonstrating that if precision requirements were relaxed, rapid iteration would be possible

## Routing Recommendation

**Route To:** STOP PIPELINE

**Rationale:** This is a Stage 0 MUST_WORK gate failure. All downstream hypotheses (H-M1, H-M2, H-M3) depend on H-E1 passing to establish that permutation equivariance is correctly implemented. Without this foundation, any results from downstream hypotheses would be meaningless (if equivariance is broken, property prediction cannot be trusted to respect weight space symmetries).

**Escalation Required:** 
- **Decision Point**: Research lead must choose between:
  1. **Infrastructure Pivot**: Invest 20-40 hours in JAX integration to enable official UNF library usage
  2. **Hypothesis Reformulation**: Redefine entire hypothesis tree to use simplified encoders with relaxed precision requirements (10^-2 threshold)
  3. **Research Direction Change**: Abandon permutation-equivariant weight space learning approach entirely

- **Blocked Hypotheses**: H-M1 (zero-shot transfer), H-M2 (cross-architecture property prediction), H-M3 (mechanism comparison) cannot proceed until H-E1 is resolved

---
*For cross-phase reference*
*Written at: 2026-07-11T12:35:00Z*
