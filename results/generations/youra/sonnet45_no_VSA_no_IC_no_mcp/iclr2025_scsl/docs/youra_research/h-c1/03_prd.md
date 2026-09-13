# Phase 3: Product Requirements Document (PRD)

**Hypothesis ID**: h-c1  
**Generated**: 2026-08-25  
**Gate Type**: SHOULD_WORK  
**Prerequisites**: h-e1 (VALIDATED)

---

## 1. Executive Summary

### Objective
Validate that architectural rankings by worst-group gap at 90% average accuracy generalize across datasets (Waterbirds → CelebA) with Spearman rank correlation ρ > 0.8.

### Success Criteria
- **Primary**: Spearman ρ > 0.8 (p < 0.05) between Waterbirds and CelebA rankings
- **Secondary**: No rank reversals in top-2 positions
- **Failure**: ρ < 0.6 OR top-2 rank reversal

### Deliverables
1. CelebA data loading pipeline (group-balanced evaluation)
2. Training-to-threshold orchestration (early stop at 90% avg acc)
3. Ranking computation module (mean gaps → rank vectors)
4. Correlation analysis suite (Spearman, Kendall, p-values)
5. Validation report (04_validation.md) with correlation results

---

## 2. System Architecture

### 2.1 High-Level Pipeline

```
┌─────────────┐
│ Dataset     │  Waterbirds (h-e1) + CelebA (new)
│ Preparation │  → Group-labeled splits
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Training    │  Train each arch to 90% avg acc
│ Loop        │  → Record worst-group gap at threshold
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Ranking     │  Aggregate gaps → rank vectors
│ Computation │  → [Waterbirds ranks, CelebA ranks]
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Correlation │  Spearman ρ, Kendall τ, p-values
│ Analysis    │  → Validation report
└─────────────┘
```

### 2.2 Module Decomposition

```
h-c1/
├── data/
│   ├── waterbirds_loader.py  # REUSE from h-e1
│   ├── celeba_loader.py       # NEW
│   └── group_metrics.py       # REUSE from h-e1
├── models/
│   ├── resnet_bn.py           # REUSE from h-e1
│   ├── resnet_ln.py           # REUSE from h-e1
│   └── model_factory.py       # REUSE from h-e1
├── training/
│   ├── train_to_threshold.py  # NEW (early stop logic)
│   └── trainer_utils.py        # REUSE from h-e1
├── analysis/
│   ├── compute_rankings.py     # NEW
│   └── correlation_stats.py    # NEW
├── experiments/
│   ├── run_waterbirds.sh       # MODIFIED from h-e1
│   └── run_celeba.sh           # NEW
└── validate.py                 # NEW (orchestration + report generation)
```

---

## 3. Functional Requirements

### FR-1: CelebA Data Loading
**Priority**: P0  
**Owner**: Data Pipeline

**Requirements**:
1. Load CelebA dataset with standard splits (162,770 train / 19,867 val / 19,962 test)
2. Extract Blond Hair attribute as binary label
3. Extract Gender attribute as spurious feature
4. Construct 4 groups: (blond-male, blond-female, not-blond-male, not-blond-female)
5. Verify 95% spurious correlation in training set
6. Apply preprocessing: center crop 178×178 → resize 224×224 → ImageNet normalization
7. Apply augmentation: random horizontal flip (training only)

**Acceptance Criteria**:
- Test set returns exactly 19,962 images with group labels
- Group distribution matches expected CelebA statistics
- Preprocessing matches Waterbirds preprocessing (224×224, ImageNet norms)

**Reuse Strategy**:
- Copy group evaluation logic from `h-e1/data/group_metrics.py`
- Follow Waterbirds loader structure for consistency

---

### FR-2: Training to Threshold
**Priority**: P0  
**Owner**: Training Loop

**Requirements**:
1. Train each architecture from scratch (He init)
2. Log average accuracy and worst-group gap every epoch
3. Detect first epoch where `avg_acc ≥ 0.90`
4. Record worst-group gap at that epoch
5. Save checkpoint (optional, for post-analysis)
6. Early stop after threshold reached (no over-training)

**Hyperparameters (from h-e1)**:
- Optimizer: SGD (momentum=0.9, lr=0.01, weight_decay=1e-4)
- Batch size: 64
- Loss: Cross-entropy
- Max epochs: 100

**Acceptance Criteria**:
- All 10 seeds reach 90% avg acc within 100 epochs (per architecture)
- Gap recorded at correct threshold epoch (not final epoch)
- Logs contain columns: `[epoch, avg_acc, worst_group_gap, threshold_reached]`

**Reuse Strategy**:
- Extend `h-e1/training/trainer_utils.py` with early-stop callback
- Reuse optimizer/scheduler setup from h-e1

---

### FR-3: Ranking Computation
**Priority**: P0  
**Owner**: Analysis Module

**Requirements**:
1. Input: Dictionary of `{architecture: [gap_seed0, gap_seed1, ..., gap_seed9]}`
2. Compute mean gap per architecture
3. Rank architectures from best (rank 1) to worst (rank N)
   - Lower gap = better = lower rank number
4. Output: Rank vector (e.g., `[2, 1]` for BN=rank2, LN=rank1)

**Acceptance Criteria**:
- Ranking is deterministic (ties broken by architecture name, alphabetical)
- Unit test: `{BN: [0.2], LN: [0.1]}` → `[2, 1]`

---

### FR-4: Correlation Analysis
**Priority**: P0  
**Owner**: Analysis Module

**Requirements**:
1. Input: Two rank vectors (Waterbirds, CelebA)
2. Compute Spearman rank correlation ρ
3. Compute p-value for ρ
4. Compute Kendall's tau (alternative metric)
5. Detect rank reversals (count architectures with reversed positions)

**Metrics**:
- Spearman ρ (primary): `scipy.stats.spearmanr`
- Kendall's tau (secondary): `scipy.stats.kendalltau`
- Rank reversal count: `sum(sign(waterbirds_rank - celeba_rank) flips)`

**Acceptance Criteria**:
- ρ ∈ [-1, 1], p-value reported
- Unit test: Perfect correlation `([1,2], [1,2])` → ρ=1.0, p≈0
- Unit test: Perfect anti-correlation `([1,2], [2,1])` → ρ=-1.0

---

### FR-5: Validation Report
**Priority**: P0  
**Owner**: Orchestration Script

**Requirements**:
1. Generate `04_validation.md` with:
   - Hypothesis statement
   - Experimental setup (architectures, datasets, seeds)
   - Results table: mean gaps per architecture per dataset
   - Ranking table: Waterbirds ranks vs CelebA ranks
   - Correlation metrics: Spearman ρ, Kendall's τ, p-values
   - Gate decision: PASSED (ρ > 0.8) or FAILED (ρ < 0.6)
2. Include ablation results (if applicable):
   - A1: 2-arch vs 4-arch correlation strength
   - A3: Spearman vs Kendall comparison

**Acceptance Criteria**:
- Report follows h-e1 validation format
- Gate decision is deterministic from ρ threshold
- All random seeds documented (reproducibility)

---

## 4. Non-Functional Requirements

### NFR-1: Code Reuse
**Requirement**: Maximize reuse from h-e1 validated codebase.

**Reuse Targets**:
- Waterbirds data loader (100% reuse)
- ResNet-BN, ResNet-LN models (100% reuse)
- Group evaluation metrics (100% reuse)
- Training utilities (90% reuse, add early-stop logic)

**New Code Only For**:
- CelebA data loader
- Ranking computation
- Correlation statistics

---

### NFR-2: Computational Budget
**Requirement**: Complete PoC within 100 GPU-hours (single V100).

**Budget Breakdown**:
- Waterbirds: 2 architectures × 10 seeds × ~30 epochs = 30 GPU-hours
- CelebA: 2 architectures × 10 seeds × ~20 epochs = 53 GPU-hours
- Buffer: 17 GPU-hours for re-runs

**Optimization**:
- Reuse Waterbirds results from h-e1 if available (save 30 GPU-hours)
- Early stop exactly at 90% threshold (no over-training)

---

### NFR-3: Reproducibility
**Requirement**: All results must be reproducible with fixed seeds.

**Implementation**:
- Seed all RNGs: `torch.manual_seed(seed)`, `np.random.seed(seed)`
- Log all hyperparameters in experiment config files
- Save checkpoints at threshold epoch (optional, for verification)

---

### NFR-4: Extensibility
**Requirement**: Support adding architectures from h-m2 without refactoring.

**Design**:
- Model factory pattern (add CBAM, ViT via config)
- Ranking module accepts variable-length architecture lists
- Correlation analysis handles 2-4 architectures

---

## 5. Data Requirements

### DR-1: Waterbirds Dataset
**Source**: h-e1 validation (already cached)  
**Format**: PyTorch DataLoader with group labels  
**Size**: 5794 test images  
**Status**: VALIDATED in h-e1

---

### DR-2: CelebA Dataset
**Source**: http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html  
**Format**: Images + `list_attr_celeba.txt` (attribute labels)  
**Size**: 202,599 images (162,770 train / 19,867 val / 19,962 test)  
**Required Attributes**: Blond_Hair, Male  
**Download**: `torchvision.datasets.CelebA` or manual download  
**Cache Path**: `./data/celeba/`

**Validation Checks**:
- Verify test set size = 19,962
- Verify group balance matches literature (e.g., blond-male is minority)
- Verify spurious correlation ≥ 95% in training set

---

## 6. Testing Strategy

### Unit Tests
1. **CelebA Loader**:
   - Test group assignment (4 groups constructed correctly)
   - Test preprocessing (output shape 224×224×3)
   - Test augmentation toggle (flip on train, off on val/test)

2. **Ranking Module**:
   - Test deterministic ranking (alphabetical tie-breaking)
   - Test mean aggregation across seeds
   - Test edge case: single architecture (rank=1)

3. **Correlation Module**:
   - Test perfect correlation (ρ=1.0)
   - Test anti-correlation (ρ=-1.0)
   - Test p-value computation (non-zero for small samples)

### Integration Tests
1. **End-to-End (E2E)**:
   - Run 1 architecture × 1 seed on CelebA (smoke test)
   - Verify training reaches 90% avg acc
   - Verify gap recorded at correct epoch
   - Verify ranking computation produces valid rank

2. **Reuse Validation**:
   - Run Waterbirds with h-c1 code → compare gaps with h-e1 results
   - Tolerance: ±0.5 pp difference (seed variance)

---

## 7. Risks and Mitigations

### Risk 1: CelebA Download Failure
**Likelihood**: Medium  
**Impact**: High (blocks entire experiment)  
**Mitigation**:
- Use `torchvision.datasets.CelebA` with automatic download
- Fallback: Manual download from official site
- Test download in isolation before full experiment

---

### Risk 2: CelebA Training Instability
**Likelihood**: Medium  
**Impact**: Medium (some seeds may not reach 90% avg acc)  
**Mitigation**:
- Increase max epochs from 100 to 150 if needed
- Flag seeds that fail to converge in validation report
- Require ≥8/10 seeds succeed per architecture

---

### Risk 3: Ranking Ties
**Likelihood**: Low  
**Impact**: Low (Spearman handles ties, but ambiguous interpretation)  
**Mitigation**:
- Use mean gaps across 10 seeds to reduce tie probability
- Fallback: Kendall's tau (more robust to ties)
- Document any ties in validation report

---

### Risk 4: Insufficient Architecture Diversity
**Likelihood**: High (h-m2 may not complete)  
**Impact**: Medium (only 2 architectures → limited correlation test)  
**Mitigation**:
- Proceed with BN + LN only (minimum viable test)
- Flag results as "limited test, need h-m2 for full validation"
- Defer to Phase 4.5 synthesis for multi-hypothesis analysis

---

## 8. Implementation Budget (Archon Estimate)

### Tier: 1 (Moderate Complexity)
- **Reason**: New dataset (CelebA), new analysis modules (ranking, correlation), but high h-e1 reuse

### Estimated Lines of Code (LoC):
- CelebA loader: ~150 LoC
- Training-to-threshold logic: ~100 LoC (extend h-e1 trainer)
- Ranking computation: ~80 LoC
- Correlation analysis: ~100 LoC
- Validation script: ~150 LoC
- **Total new/modified**: ~580 LoC

### Estimated Development Time:
- Data pipeline: 2-3 hours
- Training extension: 1-2 hours
- Analysis modules: 2-3 hours
- Integration + testing: 3-4 hours
- **Total**: 8-12 hours (Tier 1)

### Token Budget:
- **Low estimate**: 350k tokens (minimal debugging)
- **High estimate**: 450k tokens (CelebA setup issues, ranking edge cases)

---

## 9. Acceptance Criteria (Gate: SHOULD_WORK)

### PASSED
1. Spearman ρ > 0.8 with p < 0.05
2. All seeds (≥8/10) reach 90% avg acc on both datasets
3. No rank reversals in top-2 positions
4. Validation report generated with deterministic gate decision

### FAILED
1. Spearman ρ < 0.6 (signatures do not generalize)
2. Top-2 rank reversal (e.g., BN best on Waterbirds, worst on CelebA)
3. CelebA data loading failures (group imbalance)

### UNCERTAIN (Defer to Phase 4.5)
1. 0.6 ≤ ρ ≤ 0.8 (moderate correlation, need more architectures)
2. Only 1 architecture converges on CelebA (insufficient data)

---

## 10. Dependencies

### Upstream (Prerequisites)
- **h-e1**: VALIDATED
  - Waterbirds data loader
  - ResNet-BN, ResNet-LN models
  - Training hyperparameters
  - Group evaluation metrics

### Downstream (Enables)
- **h-c2**: Requires CelebA baseline rankings from h-c1
- **Phase 4.5**: Synthesis across h-c1, h-c2, h-c3 (correlation family)

### Optional (Parallel)
- **h-m2**: If completed, enables 4-architecture test (BN, LN, CBAM, ViT)
- Otherwise: Proceed with 2-architecture minimal test

---

## 11. Open Questions (for Phase 4)

1. **CelebA hyperparameter tuning**: Do we need different lr/batch-size for CelebA vs Waterbirds?
   - **Default**: Use h-e1 hyperparameters (lr=0.01, batch=64) without tuning
   - **Rationale**: Control for training recipe, only vary dataset

2. **Checkpoint saving**: Do we need full model checkpoints or just gap logs?
   - **Default**: Logs only (saves storage)
   - **Optional**: Save checkpoints for post-analysis (e.g., saliency maps)

3. **Ablation scope**: Run all 3 ablations (A1, A2, A3) or just A1?
   - **Default**: Run A1 (2-arch vs 4-arch) if h-m2 completes
   - **Defer**: A2, A3 to Phase 5 if budget allows

---

## 12. References

- **h-e1 Validation Report**: `docs/youra_research/h-e1/04_validation.md`
- **Phase 2C Experiment Brief**: `docs/youra_research/h-c1/02c_experiment_brief.md`
- **Waterbirds Dataset**: Sagawa et al. 2020, https://github.com/kohpangwei/group_DRO
- **CelebA Dataset**: Liu et al. 2015, http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html
- **Spearman Correlation**: `scipy.stats.spearmanr` documentation

---

## 13. Sign-Off

**PRD Status**: READY FOR ARCHITECTURE DESIGN  
**Next Phase**: Phase 3 Architecture (03_architecture.md)  
**Estimated Effort**: Tier 1, 350-450k tokens, 8-12 dev hours
