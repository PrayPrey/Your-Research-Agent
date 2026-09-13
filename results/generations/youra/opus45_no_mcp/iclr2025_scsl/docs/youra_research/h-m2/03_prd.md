# Product Requirements Document: H-M2 Post-Crystallization Feature Commitment

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis:** H-M2 - Post-crystallization, classifier commits to spurious features and does not revert
**Type:** MECHANISM
**Budget Tier:** FULL (≤30 tasks)

---

## 1. Executive Summary

This PRD defines requirements for testing the irreversibility hypothesis: once crystallization occurs (H-E1) and gradient starvation sets in (H-M1), does the classifier permanently commit to spurious features? We use linear probes to measure spurious vs core feature reliance across training epochs post-crystallization.

### Success Criteria
- Spurious probe accuracy does NOT decrease post-crystallization (commitment confirmed)
- Core probe accuracy remains suppressed (<85% at final epoch)
- No late reversal observed in feature probe dynamics

---

## 2. Problem Statement

H-M1 established gradient starvation as the mechanism driving crystallization. H-M2 tests whether this commitment is permanent: does the classifier remain locked to spurious features, or can it recover?

### Connection to Prerequisites
- **H-E1 Output:** Crystallization timing via d²WGA/dt² peak
- **H-M1 Output:** Gradient starvation inflection confirmed
- **H-M2 Input:** Use H-M1 checkpoints post-crystallization for probe analysis
- **H-M2 Goal:** Prove irreversibility of spurious feature commitment

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load Waterbirds dataset from WILDS benchmark
- Full test set: ~5,794 samples for probe evaluation
- Validation set: 1,199 samples for probe training (balanced subset)
- Provide group annotations: metadata[:,0] = bird type, metadata[:,1] = background (if available)
- Track spurious label (background) and core label (bird type) separately

### FR-2: Checkpoint Loading
- Load H-M1 checkpoints from crystallization epoch onward
- Crystallization epoch identified from H-E1/H-M1 outputs
- Load checkpoints: epoch_{crystallization} to epoch_{final}
- Use same ResNet-50 architecture as H-M1

### FR-3: Feature Extraction
- Register forward hook on avgpool layer (penultimate)
- Extract 2048-dim features for each sample
- Cache features per checkpoint to avoid redundant forward passes

### FR-4: Linear Probe Training
- Train spurious feature probe: predicts background (land/water) from features
- Train core feature probe: predicts bird type (landbird/waterbird) from features
- Use SGD optimizer, lr=0.01, 100 iterations per probe
- Reinitialize probes for each checkpoint (fresh training)

### FR-5: Temporal Probe Analysis
- Track spurious_acc(t), core_acc(t) for t ≥ crystallization_epoch
- Compute probe accuracy on held-out test split
- Store history for commitment analysis

### FR-6: Commitment Detection
- Check if spurious probe accuracy is monotonically non-decreasing (±2% noise margin)
- Check if core probe accuracy remains suppressed (<85%)
- Report commitment status: {committed: bool, core_suppressed: bool}

### FR-7: Visualization
- **Required:** Gate metrics comparison - spurious vs core probe accuracy over epochs
- Temporal probe accuracy plot with crystallization vertical line
- Optional: Commitment heatmap by group

### FR-8: WGA Integration (Reuse from H-M1)
- Import checkpoint loading utilities from H-M1
- Use crystallization_epoch from H-E1/H-M1 detection results

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

### Label Definitions
| Label | Meaning | Probe Target |
|-------|---------|--------------|
| Core | Bird type (landbird=0, waterbird=1) | core_probe |
| Spurious | Background (land=0, water=1) | spurious_probe |

### Group Mapping
| Group ID | Bird Type | Background | Role |
|----------|-----------|------------|------|
| 0 | Landbird | Land | Majority |
| 1 | Landbird | Water | Minority |
| 2 | Waterbird | Land | Minority |
| 3 | Waterbird | Water | Majority |

---

## 5. Model Specification

### Analysis Model: ResNet-50 (from H-M1 checkpoints)
| Attribute | Value |
|-----------|-------|
| Architecture | ResNet-50 |
| Pretrained | ImageNet (then trained on Waterbirds) |
| Checkpoint Source | h-m1/code/checkpoints/epoch_*.pt |
| Final Layer | Linear(2048, 2) |
| Feature Layer | avgpool (2048-dim) |

### Linear Probes
| Probe | Input | Output | Purpose |
|-------|-------|--------|---------|
| spurious_probe | features [N, 2048] | logits [N, 2] | Predict background |
| core_probe | features [N, 2048] | logits [N, 2] | Predict bird type |

### Core Mechanism: FeatureProbeAnalyzer
```python
class FeatureProbeAnalyzer:
    """Tracks linear probe accuracy on spurious vs core features
    across training epochs post-crystallization."""
    
    def __init__(self, model, crystallization_epoch, hidden_dim=2048):
        self.model = model
        self.crystallization_epoch = crystallization_epoch
        self.spurious_probe = nn.Linear(hidden_dim, 2)
        self.core_probe = nn.Linear(hidden_dim, 2)
        self.spurious_acc_history = []
        self.core_acc_history = []
    
    def extract_features(self, dataloader) -> Tuple[Tensor, Tensor, Tensor]:
        """Returns (features, spurious_labels, core_labels)."""
        ...
    
    def train_probes(self, features, spurious_labels, core_labels) -> None:
        """Train both probes from scratch."""
        ...
    
    def evaluate_probes(self, features, spurious_labels, core_labels) -> Tuple[float, float]:
        """Returns (spurious_acc, core_acc)."""
        ...
    
    def check_commitment(self) -> dict:
        """Returns {'committed': bool, 'core_suppressed': bool}."""
        ...
```

---

## 6. Evaluation Metrics

### Primary Metrics
| Metric | Description | Target |
|--------|-------------|--------|
| Spurious Probe Accuracy | Linear probe accuracy on background | Track trend |
| Core Probe Accuracy | Linear probe accuracy on bird type | Track trend |
| Commitment Score | final_spurious ≥ initial_spurious - 0.02 | True |

### Gate Condition (MUST_WORK)
- **Pass:** Spurious probe accuracy does NOT decrease by >2% post-crystallization
- **Secondary Pass:** Core probe accuracy remains <85% at final epoch
- **Fail:** Spurious accuracy decreases significantly → EXPLORE late reversal

### Success Criteria
```
IF spurious_acc[final] >= spurious_acc[crystallization] - 0.02:
    IF core_acc[final] < 0.85:
        PASS (Full commitment confirmed)
    ELSE:
        PASS with note (Commitment confirmed, core features recovered)
ELSE:
    FAIL → EXPLORE late reversal possibility
```

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.10.0
torchvision>=0.11.0
wilds>=2.0.0
numpy>=1.21.0
matplotlib>=3.4.0
tqdm>=4.62.0
pyyaml>=5.4.0
```

### 7.2 Reference Implementations
| Repository | Usage |
|------------|-------|
| p-lambda/wilds | Dataset loading |
| PolinaKirichenko/deep_feature_reweighting | Linear probe methodology |
| h-m1/code/ | Checkpoint loading, crystallization epoch |

### 7.3 Literature References
| Paper | Relevance |
|-------|-----------|
| Kirichenko et al. (2023) | Last-layer retraining, linear probe methodology |
| Sagawa et al. (2020) | Waterbirds benchmark, group definitions |
| Alain & Bengio (2017) | Linear probing methodology foundation |

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic feature extraction (torch.no_grad)
- Probe training: deterministic SGD (no momentum variance)

### NFR-2: Compute
- Single GPU inference only (no training of main model)
- Feature extraction: ~10 min per checkpoint (5794 test samples)
- Total analysis time: ~2-3 hours (probe training fast)

### NFR-3: Code Reuse
- Import checkpoint utilities from H-M1
- Reuse data loading from H-M1 (get_loaders)
- Extend, don't duplicate, existing infrastructure

---

## 9. Out of Scope

- Training new models (analysis only on H-M1 checkpoints)
- Multi-seed statistical runs (MECHANISM PoC, single seed)
- CelebA dataset (Waterbirds sufficient)
- Intervention experiments (observation only)
- Feature retraining or recovery attempts

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Probe training noisy | Unstable accuracy | Multiple iterations (100), epoch averaging |
| Checkpoint missing | Incomplete timeline | Verify all checkpoints exist before analysis |
| Spurious/core label ambiguity | Wrong probe targets | Use metadata columns consistently |
| Late recovery observed | Hypothesis fail | Report as finding, explore reversal mechanism |

---

## 11. Test Plan

### Unit Tests
- Feature extraction hook registration
- Probe training convergence (loss decreases)
- Accuracy computation correctness

### Integration Tests
- Full checkpoint loading pipeline
- Feature caching across checkpoints
- Figure generation pipeline

### Validation Tests
- Gate criteria: spurious_acc stable, core_acc suppressed
- Probe accuracy reasonable (>50% on respective tasks)

---

*Generated for Phase 3 Implementation Planning*
*Hypothesis Type: MECHANISM | Budget Tier: FULL*
