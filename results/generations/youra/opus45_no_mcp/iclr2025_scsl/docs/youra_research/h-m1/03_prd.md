# Product Requirements Document: H-M1 Gradient Starvation Mechanism

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis:** H-M1 - Feedback loop becomes self-reinforcing at crystallization point due to gradient starvation
**Type:** MECHANISM
**Budget Tier:** FULL (≤30 tasks)

---

## 1. Executive Summary

This PRD defines requirements for testing the gradient starvation mechanism hypothesis. The experiment investigates whether the crystallization phenomenon detected in H-E1 is caused by gradient starvation - where dominant features progressively starve gradient flow to minority features, creating a self-reinforcing feedback loop.

### Success Criteria
- Gradient ratio inflection correlates with WGA crystallization (r > 0.7)
- Inflection occurs before 50% of training (epoch < 50)
- Per-group gradient norms diverge at crystallization point

---

## 2. Problem Statement

H-E1 established that crystallization zones exist as detectable training phases where WGA decline accelerates. This follow-up experiment tests whether gradient starvation (Pezeshki et al., 2021) is the underlying mechanism: as majority-group features dominate early learning, gradient flow to minority-group features diminishes, eventually reaching a point of no return (crystallization).

### Connection to H-E1
- **H-E1 Output:** Crystallization timing via d²WGA/dt² peak
- **H-M1 Input:** Use H-E1 crystallization timing for correlation analysis
- **H-M1 Goal:** Explain WHY crystallization occurs via gradient dynamics

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load Waterbirds dataset from WILDS benchmark
- Full dataset: 11,788 samples (train: 4,795, val: 1,199, test: 5,794)
- Provide group annotations (4 groups: bird × background)
- Track group indices for per-group gradient analysis

### FR-2: Model Training with Gradient Hooks
- Train ResNet-50 with ImageNet pretrained weights
- Register backward hooks on classifier layer (model.fc)
- Capture gradient magnitudes per batch during backward pass
- Use SGD optimizer (momentum=0.9, weight_decay=1e-4)
- Learning rate: 1e-3 with step schedule (milestones: [30, 60], gamma: 0.1)
- Batch size: 128, Epochs: 100

### FR-3: Gradient Tracking
- Compute per-group gradient norms per batch
- Track minority group (group 3) vs majority group (group 0) gradient ratio
- Aggregate epoch-level gradient ratio (mean across batches)
- Store gradient history for analysis

### FR-4: WGA Integration (Reuse from H-E1)
- Import WGA computation from h-e1 implementation
- Compute per-epoch WGA and d²WGA/dt² (5-epoch smoothing)
- Extract crystallization timing (peak epoch)

### FR-5: Correlation Analysis
- Compute gradient ratio inflection epoch (where d(ratio)/dt shows acceleration)
- Calculate Pearson correlation between gradient inflection and WGA peak
- Report correlation coefficient (r) and p-value

### FR-6: Visualization
- **Required:** Gate metrics comparison - gradient inflection vs WGA timing
- Gradient ratio timeline with inflection marked
- WGA vs gradient ratio overlay (dual-axis)
- Per-group gradient norm evolution

---

## 4. Data Specification

### Primary Dataset: Waterbirds
| Attribute | Value |
|-----------|-------|
| Source | WILDS benchmark (p-lambda/wilds) |
| Task | Binary classification (landbird vs waterbird) |
| Spurious Feature | Background (water vs land) |
| Total Samples | 11,788 |
| Train Samples | 4,795 |
| Val Samples | 1,199 |
| Test Samples | 5,794 |
| Classes | 2 |
| Groups | 4 (2 labels × 2 backgrounds) |
| Minority Group Size | ~500+ samples |

### Group Definitions
| Group ID | Label | Background | Role |
|----------|-------|------------|------|
| 0 | Landbird | Land | Majority |
| 1 | Landbird | Water | Minority |
| 2 | Waterbird | Land | Minority |
| 3 | Waterbird | Water | Majority |

---

## 5. Model Specification

### Baseline: ResNet-50 (ERM)
| Attribute | Value |
|-----------|-------|
| Architecture | ResNet-50 |
| Pretrained | ImageNet |
| Final Layer | Linear(2048, 2) |
| Training | Standard ERM |
| Gradient Tracking | None |

### Proposed: ResNet-50 with GradientTracker
| Attribute | Value |
|-----------|-------|
| Architecture | ResNet-50 |
| Pretrained | ImageNet |
| Final Layer | Linear(2048, 2) |
| Training | Standard ERM |
| Gradient Tracking | Backward hooks on model.fc |
| Per-Group Analysis | Gradient norms by group ID |

### Core Mechanism: GradientTracker Class
```python
class GradientTracker:
    """Track gradient magnitudes per group during training."""
    def __init__(self, model, group_indices):
        self.gradient_history = []
        model.fc.register_full_backward_hook(self._gradient_hook)
    
    def _gradient_hook(self, module, grad_input, grad_output):
        self.current_gradients = grad_output[0].detach().clone()
    
    def compute_group_gradient_ratio(self, batch_groups):
        # minority_norm / majority_norm
        pass
```

---

## 6. Evaluation Metrics

### Primary Metrics
| Metric | Description | Target |
|--------|-------------|--------|
| Gradient Ratio (minority/majority) | Relative gradient flow per group | Track over epochs |
| Inflection Epoch | Epoch where gradient ratio accelerates decline | < 50 |
| Correlation (r) | Pearson r between inflection and WGA peak | > 0.7 |

### Gate Condition (MUST_WORK)
- **Pass:** r > 0.7 AND inflection epoch < 50% of training
- **Fail:** r ≤ 0.7 → EXPLORE alternative mechanism (loss landscape analysis)

### Secondary Metrics
| Metric | Description |
|--------|-------------|
| Per-group gradient norms | Track divergence pattern |
| p-value | Statistical significance of correlation |
| WGA at inflection | Worst-group accuracy at inflection point |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.10.0
torchvision>=0.11.0
wilds>=2.0.0
numpy>=1.21.0
scipy>=1.7.0  # For pearsonr
matplotlib>=3.4.0
tqdm>=4.62.0
pyyaml>=5.4.0
```

### 7.2 Reference Implementations
| Repository | Usage |
|------------|-------|
| p-lambda/wilds | Dataset loading |
| kohpangwei/group_DRO | Training protocol reference |
| h-e1/code/ | WGA computation, d²WGA/dt² analysis |

### 7.3 Literature References
| Paper | Relevance |
|-------|-----------|
| Pezeshki et al. (2021) | Gradient starvation mechanism |
| Shah et al. (2020) | Simplicity bias in neural networks |
| Sagawa et al. (2020) | Group DRO, per-group tracking |

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic operations where possible
- Dense checkpointing (every epoch for gradient analysis)

### NFR-2: Compute
- Single GPU training (RTX 3090 or equivalent)
- Training time: ~4 hours (100 epochs on Waterbirds)
- Gradient hook overhead: minimal (~5% slowdown)

### NFR-3: Code Reuse
- Import WGA/crystallization detection from h-e1
- Extend, don't duplicate, existing infrastructure

---

## 9. Out of Scope

- Multi-seed statistical runs (MECHANISM PoC, single seed sufficient)
- CelebA dataset (Waterbirds sufficient for mechanism validation)
- Model intervention or modification (observation only)
- Loss landscape analysis (fallback if gate fails)
- Theoretical proof of gradient starvation

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gradient ratio noisy | Weak correlation | Epoch-level aggregation |
| Batch composition varies | Inconsistent per-group stats | Use validation set for stable groups |
| H-E1 crystallization timing imprecise | False correlation | Use smoothed peak detection |
| Correlation spurious | False positive | Check temporal precedence (gradient leads WGA) |

---

## 11. Test Plan

### Unit Tests
- GradientTracker hook registration
- Per-group gradient norm computation
- Correlation calculation correctness

### Integration Tests
- Full training loop with gradient tracking
- WGA + gradient logging consistency
- Figure generation pipeline

### Validation Tests
- Gate criteria: r > 0.7, inflection < 50%
- Correlation p-value < 0.05

---

*Generated for Phase 3 Implementation Planning*
*Hypothesis Type: MECHANISM | Budget Tier: FULL*
