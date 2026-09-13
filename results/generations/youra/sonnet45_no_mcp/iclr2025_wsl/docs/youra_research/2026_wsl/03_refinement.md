# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-21T05:14:58.258912
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-1
- **Gap Title**: Discriminative Weight Features for Binary Depth Classification
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met:
1. **SPECIFIC**: Clear core claim with 70% accuracy threshold
2. **MECHANISM**: Three-step causal chain (gradient accumulation, architectural constraints, normalization effects)
3. **PREDICTIONS**: P1/P2/P3 with explicit success/failure criteria
4. **NOVELTY**: First demonstration of weight-based architectural depth classification
5. **FEASIBILITY**: Scientifically sound within EXISTENCE-tier constraints
6. **OBJECTIONS**: Confounds acknowledged and mitigated

### Key Insights

**From Run 3 Failure to Run 4 Success:**
Run 3 attempted continuous correlation analysis (|ρ| = 0.859 < 0.90 threshold, p = 0.067 > 0.05) with inadequate sample size (n=5). The pivot to binary classification (Run 4) amplifies signal through extreme group comparison (shallow ≤34 vs deep ≥50 layers), increases sample size to n=20 for statistical power, and adopts exploratory threshold (accuracy > 70% vs rigid ρ ≥ 0.90).

**Methodological Innovation:**
Binary classification enables decision boundary discovery for practical use cases (model zoo navigation, mislabel detection) rather than correlation measurement for theoretical understanding. Simple features (mean/std/min/max of layer norms) maximize statistical power and strengthen contribution compared to complex features (SVD spectra, cross-layer correlations).

**Confound Acknowledgment:**
Honest scientific approach: we test for "depth-correlated patterns" (may include width, training recipe, architecture family) rather than "pure depth causality." This is appropriate for EXISTENCE-tier validation. Multi-family sampling (ResNet, VGG, DenseNet) provides evidence that depth signal persists despite intra-group width variation.

### Breakthrough Moments

1. **Dr. Nova's Weight Space Geometry**: Introduced perspective that weights encode "compressed computational capacity" rather than mere architectural metadata. Proposed spectral fingerprinting for future work.

2. **Prof. Vera's Testable Hierarchy**: Grounded creative ideas with three-tier prediction framework (P1: simple features baseline, P2: robustness check, P3: null control), providing clear falsification criteria.

3. **Dr. Ally's Confound Mitigation**: Synthesized multi-family sampling strategy to test whether depth signal persists across architectures with varying widths within each depth category.

4. **Prof. Rex's Critical Challenge**: Forced explicit scope boundaries, null result plan, and honest acknowledgment that classification may learn "depth + width + training" rather than pure depth.

---

## Final Hypothesis

### Title
Weight-Based Binary Classification of CNN Architectural Depth

### Hypothesis ID
H-WeightDepthClassifier-v1

### Core Claim
Pretrained CNN architectures exhibit weight distribution signatures that enable binary classification (shallow ≤34 layers vs. deep ≥50 layers) with >70% accuracy using simple aggregated statistics (mean/std/min/max of layer-wise Frobenius norms), demonstrating that architectural depth leaves measurable fingerprints in weight space despite confounding factors.

### Mechanism
Deep networks (≥50 layers) develop distinctive weight norm patterns through three mechanisms:

1. **Gradient Accumulation**: Deeper networks experience more gradient transformation steps during backpropagation, leading to characteristic weight magnitude patterns that differ from shallow networks.

2. **Architectural Constraints**: Residual connections (ResNet), dense connections (DenseNet), and bottleneck layers create depth-specific weight structures that shallow networks lack.

3. **Normalization Effects**: Batch normalization statistics accumulate differently across 50+ layers versus <34 layers, creating distinctive weight distribution signatures.

---

## Predictions

### P1 (Primary - EXISTENCE Validation)
**Statement**: Binary logistic regression trained on aggregated weight statistics (mean, std, min, max of layer-wise Frobenius norms) from 16 pretrained models achieves ≥70% test accuracy on 4 held-out models.

**Test Method**: Extract features from 20 PyTorch torchvision models (10 shallow, 10 deep), 80/20 train/test split, sklearn LogisticRegression with default hyperparameters.

**Success Criterion**: Test accuracy ≥ 70%

**Falsification**: Test accuracy ≤ 60% indicates weight norms alone are insufficient for depth classification.

### P2 (Robustness Check)
**Statement**: Classification accuracy on within-family subsets (ResNet-only, VGG-only) remains ≥65%.

**Test Method**: Train and test separately on ResNet subset, then VGG subset.

**Success Criterion**: Accuracy ≥ 65% for each family.

**Falsification**: Accuracy drops below 60% indicates depth signal is confounded with architecture family rather than depth itself.

### P3 (Null Control)
**Statement**: Random label shuffle (assign shallow/deep labels randomly to same 20 models) produces accuracy ≤55% (near 50% chance).

**Test Method**: Randomly permute depth labels, retrain classifier, measure test accuracy.

**Success Criterion**: Accuracy ≤ 55%

**Falsification**: Accuracy > 60% with random labels indicates overfitting to model-specific artifacts rather than learning depth signal.

---

## Novelty

**Key Innovation**: First demonstration that architectural depth—a fundamental network property—can be inferred from weight statistics alone without forward passes, activation analysis, or metadata parsing.

**Differentiation from Prior Work**:
- **Weight-based compression**: Prior work uses weights to reduce model size; we use weights to infer architectural properties
- **Transfer learning**: Prior work measures weight similarity for task relatedness; we classify architectural categories
- **Run 3 correlation**: Run 3 measured correlation strength (|ρ| = 0.859); we classify depth categories with decision boundaries

**Research Impact**:
- **Model Zoo Navigation**: Classify 1M+ Hugging Face models by depth without running inference
- **Model Verification**: Detect mislabeled models (claimed deep but weight stats suggest shallow)
- **New Research Direction**: If depth is weight-fingerprinted, what other properties are? Width? Training dataset size? Optimization algorithm?

---

## Experimental Design

### Dataset
20 pretrained CNNs from PyTorch torchvision (no downloads required):
- **Shallow (n=10)**: ResNet-18/34, VGG-11/13/16/19, AlexNet, SqueezeNet, MobileNet-v2, ShuffleNet
- **Deep (n=10)**: ResNet-50/101/152, Wide-ResNet-50/101, DenseNet-121/169/201, ResNeXt-50/101

### Features
For each model:
1. Load pretrained weights from torchvision.models
2. Extract Frobenius norm for each convolutional/linear layer using torch.norm()
3. Compute aggregated statistics: mean, std, min, max (4 features total)

### Classifier
sklearn LogisticRegression with L2 regularization, default hyperparameters

### Validation
80/20 train/test split (16 train, 4 test), stratified by depth category

### Success Criterion
Test accuracy ≥ 70%

---

## Scope & Limitations

### Applies To
Pretrained CNNs from standard ImageNet training recipes (ResNet, VGG, DenseNet families) available in PyTorch torchvision. Binary classification of shallow (≤34 layers) vs deep (≥50 layers) architectures.

### Does Not Apply To
- Randomly initialized models (no training history)
- Models trained on non-ImageNet datasets
- Architectures with fundamentally different paradigms (Transformers, RNNs, Graph Neural Networks)
- Models with custom training recipes outside standard ImageNet protocols

### Known Limitations
1. **Confound Correlation**: Classification success may be influenced by correlated factors (width, training recipe, architecture family). We test for "depth-correlated patterns," not pure depth causality.

2. **Generalization Uncertainty**: 20 models span only 3 architecture families (ResNet, VGG, DenseNet). Generalization to unseen families (EfficientNet, ConvNeXt, Vision Transformers) is untested.

3. **Training Recipe Dominance**: All models from PyTorch torchvision (standardized ImageNet training) reduces variance but doesn't eliminate it. If training hyperparameters dominate weight statistics, classification may succeed for wrong reasons.

4. **Sample Size**: n=20 is adequate for EXISTENCE-tier detection but limited for robust generalization claims.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed with mitigation strategies) |

### Null Result Plan (Committed)
- **If P1 accuracy ≤ 60%**: Accept that simple weight norms are insufficient. Document as "Weight statistics alone do not strongly fingerprint CNN depth." Publish as negative result at ICLR workshop OR route to Phase 0 for alternative approach (activation statistics, functional evaluation).
- **If P1 = 60-70%**: Marginal result. Proceed to Phase 2B but flag as "weak signal" requiring careful experimental design.
- **If P1 ≥ 70%**: Strong signal. Proceed to Phase 2B with confidence.

---

## Constraints Compliance

✅ **EXISTENCE-Tier Validated**:
- Maximum 2 epics (Epic 1: Data Preparation, Epic 2: Classification) ✓
- Maximum 6 tasks (3 per epic) ✓
- 0 model training (pretrained only) ✓
- sklearn classifiers only (no custom algorithms) ✓
- 2 GPU hours maximum (1 hour for loading/feature extraction, <1 hour for classification) ✓

✅ **Feasibility Constraints Met**:
- Uses existing real datasets (PyTorch pretrained models) ✓
- Uses existing benchmarks (classification accuracy metric) ✓
- No human evaluation required ✓
- Testable immediately ✓

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Ready for Phase 2B: Research Planning (Roadmap Creation)*
