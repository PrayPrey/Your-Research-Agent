# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-05-12T08:54:00.000000+00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILURE

## Performance Gap

| Metric | Target | Actual | Gap | Status |
|--------|--------|--------|-----|--------|
| Reconstruction Error | <10.0% | 19.18% | +9.18 pp | ❌ FAIL |
| Frozen-K Generalization | <10.0% | 10.31% | +0.31 pp | ❌ FAIL |
| Kernel Robustness | ≥90.0% | 0.00% | -90.0 pp | ❌ FAIL |

## Root Cause Analysis

### 1. **Equivariance Mechanism Complete Failure (CRITICAL)**
- **Evidence**: Kernel robustness 0.00% (target ≥90%)
- **Root Cause**: MSE-based equivariance loss is fundamentally too weak
  - Loss: `L_equiv = MSE(z_original, z_permuted)` under random weight permutations
  - This formulation allows the model to learn permutation-sensitive encodings
  - No hard constraint forcing permutation invariance
- **Impact**: Core hypothesis property (quotient space factorizes permutations) completely violated

### 2. **Insufficient Quotient Space Capacity**
- **Evidence**: Reconstruction error 19.18% (target <10%)
- **Root Cause**: K=32 too small for 1000-dimensional weight vectors
  - Compression ratio: 1000 → 32 (96.8% compression)
  - Real models: 100K+ dimensions would need K >> 32
- **Impact**: Significant information loss prevents accurate reconstruction

### 3. **Architecture Embeddings Prevent Cross-Family Learning**
- **Evidence**: Frozen-K generalization 10.31% on RNN holdout (marginally failing)
- **Root Cause**: Architecture embeddings inject family-specific information
  - Embeddings allow encoder to learn architecture-specific rather than shared representations
  - Defeats purpose of cross-architecture quotient space
- **Impact**: Limited generalization to unseen architecture families

### 4. **Training Instability**
- **Evidence**: Early stopping at epoch 12 of 20 (60% completion)
- **Root Cause**: Conflicting gradients from reconstruction + equivariance losses
  - Reconstruction loss wants to preserve all information
  - Equivariance loss wants to discard permutation information
  - Without careful balancing, these objectives conflict
- **Impact**: Suboptimal convergence, unstable training dynamics

## Lessons Learned

### What Failed Completely

1. **MSE-based equivariance loss is insufficient**
   - Does not enforce hard permutation invariance
   - Model learns permutation-sensitive encodings despite loss term
   - Result: 0.00% kernel robustness (complete failure)

2. **Architecture embeddings contradict cross-architecture goal**
   - Injecting architecture family information prevents shared learning
   - Model specializes per-architecture rather than finding common structure
   - Result: 10.31% frozen-K generalization (marginal failure)

3. **K=32 far too small for weight space compression**
   - 96.8% compression ratio loses critical information
   - Real models (100K+ dims) would need K in hundreds or thousands
   - Result: 19.18% reconstruction error (significant information loss)

4. **Naive loss combination creates conflicting objectives**
   - Reconstruction + equivariance losses fight each other
   - No principled balancing mechanism
   - Result: Early stopping at 60% of planned training

### What Showed Promise

1. **Deep Sets architecture is tractable**
   - Permutation-invariant aggregation (mean pooling) is efficient
   - Computational cost manageable even for large weight vectors
   - Could work with better equivariance constraints

2. **Synthetic data generation approach viable**
   - Simulated ModelZoo-14K dataset enables rapid PoC testing
   - Architecture stratification ensures balanced evaluation
   - Proof-of-concept methodology is sound

3. **Modular implementation enables iteration**
   - Clean separation: data, models, loss, train, evaluate, visualize
   - Easy to swap components (e.g., replace loss function)
   - Code quality high, suitable for refinement

### Implementation vs Hypothesis

**Type**: MECHANISM_FAILURE (not hypothesis invalidation)

**Assessment**: 
- Implementation is functionally complete and correct
- Code properly measures all required metrics
- Static validation passed (architecture, loss, training loop all correct)
- **BUT**: Mechanism design has fundamental flaws

**Core Problem**: Deep Sets + architecture embeddings + MSE equivariance loss is an insufficient combination for learning quotient space representations

**Hypothesis Status**: 
- May still be valid with alternative implementations
- Kernel robustness failure (0.00%) suggests deeper issues than just hyperparameters
- Need fundamentally different equivariance mechanism

## Feedback for Next Phase

### Suggested Modifications (If Retrying H-E1)

1. **Replace equivariance loss with contrastive learning**
   - Use contrastive loss on permutation pairs: push apart (z_orig, z_permuted_wrong), pull together (z_orig, z_permuted_same)
   - Add explicit slot-permutation operators ρ(g)
   - Enforce hard invariance through architecture (not just loss)

2. **Increase K substantially**
   - Test K ∈ {64, 128, 256, 512}
   - Aim for <90% compression (more conservative)
   - Scale K with weight dimensionality

3. **Remove or ablate architecture embeddings**
   - Test pure Deep Sets without architecture conditioning
   - If needed, use architecture info only after encoding (not before)
   - Goal: force encoder to find shared structure

4. **Extend training and improve stability**
   - Full 100 epochs with patience=20 early stopping
   - Better learning rate schedule (warmup + cosine decay)
   - Loss balancing with adaptive weights

### Alternative Approaches (If Modifications Insufficient)

1. **Attention-based slot encoders (Slot Attention)**
   - Replace Deep Sets with Transformer-based set encoder
   - Learnable slot queries with cross-attention
   - Better capacity than mean pooling

2. **Graph Neural Networks for weight encoding**
   - Represent weights as graphs (layers as nodes)
   - Use GNN message passing for equivariant encoding
   - Natural permutation equivariance through graph structure

3. **Per-family encoders with alignment**
   - Train separate quotient spaces for CNN, Transformer, RNN
   - Align spaces using Procrustes or optimal transport
   - Two-stage approach: within-family, then cross-family

4. **Simplify to single architecture family first**
   - Validate existence on homogeneous case (CNN-only or Transformer-only)
   - Prove quotient space works within family
   - Then extend to cross-architecture

### What NOT To Do

1. ❌ **Do not use MSE for equivariance constraints** - proven too weak
2. ❌ **Do not use architecture embeddings before encoding** - defeats cross-architecture goal
3. ❌ **Do not use K < 64 for 1000+ dim weights** - insufficient capacity
4. ❌ **Do not naively combine reconstruction + equivariance losses** - conflicting gradients
5. ❌ **Do not assume 20 epochs sufficient** - need longer training with this complexity
6. ❌ **Do not treat this as hyperparameter issue** - fundamental mechanism failure

### What Showed Promise (Preserve)

1. ✅ **Deep Sets permutation-invariant aggregation** - efficient and sound
2. ✅ **Synthetic data generation methodology** - enables rapid PoC iteration
3. ✅ **Modular code architecture** - clean separation of concerns
4. ✅ **Comprehensive evaluation metrics** - reconstruction, frozen-K, kernel robustness
5. ✅ **Visualization approach** - gate metrics, t-SNE, training curves, error distributions

## Context for Phase 0 Restart

**Why Route to Phase 0?**
- MUST_WORK gate failure with all three metrics failing
- Core mechanism (equivariance) completely broken (0.00% robustness)
- Not just implementation bug - fundamental design issue

**What Should Phase 0 Consider?**

1. **Equivariance Mechanism Design**
   - How to enforce permutation invariance? (contrastive? architectural? both?)
   - Are slot permutations ρ(g) learnable or predefined?
   - Should invariance be hard constraint or soft loss?

2. **Quotient Space Dimensionality**
   - How to choose K? (function of weight dimension? architecture complexity?)
   - Is compression-based K selection viable? (e.g., PCA to determine effective rank)
   - Can K be adaptive per model?

3. **Cross-Architecture Representation**
   - Should architecture family be input to encoder? (current approach failed)
   - Alternative: architecture-agnostic encoder + family-specific decoders?
   - Can we prove shared structure exists before building quotient space?

4. **Success Criteria Validation**
   - Are targets realistic? (reconstruction <10%, robustness ≥90%)
   - Should metrics be architecture-dependent? (easier for CNN than RNN?)
   - Is frozen-K generalization the right cross-architecture test?

**Key Research Question to Address:**
> Given that MSE equivariance loss failed completely (0.00% robustness), what alternative equivariance mechanism has theoretical grounding and empirical evidence for enforcing permutation invariance in neural network weight space?

## Experiment Summary

- **Implementation**: Complete (7 epic tasks, 20 subtasks)
- **Code Quality**: Passed static validation
- **Training**: Early stopped at epoch 12/20
- **Gate Result**: FAIL (all 3 metrics failed)
- **Routing**: Phase 0 (MUST_WORK failure)

**Artifacts**: 
- Code: `h-e1/code/`
- Report: `h-e1/04_validation.md`
- Checkpoint: `h-e1/04_checkpoint.yaml`
- Figures: `h-e1/code/figures/` (gate_metrics.png, training_curves.png, quotient_space_tsne.png, error_distribution.png)

---
*For cross-phase reference*
*Written at: 2026-05-12T08:54:00.000000+00:00*
