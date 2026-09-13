# Product Requirements Document (PRD)
# Hypothesis: h-e1 - SVAD Drift Detection Classifier

**Version:** 1.0  
**Date:** 2026-05-12  
**Author:** Anonymous
**Hypothesis Type:** EXISTENCE (FOUNDATION)  
**Gate Type:** MUST_WORK  

---

## Executive Summary

This PRD defines the implementation requirements for hypothesis h-e1, which validates the foundational assumption of the SVAD (Semantic Dataset Versioning with Adaptive Drift-Based Deprecation) system: that automated statistical drift detection can reliably classify dataset version changes as MAJOR/MINOR/PATCH.

**Core Objective:** Implement and validate a drift detection system that applies KS test + MMD on PCA-reduced features to classify 15 documented dataset version transitions, achieving ≥85% overall accuracy with ≥70% precision and ≥85% recall on MAJOR change detection.

**Success Criteria:**
- Precision ≥70% for MAJOR changes
- Recall ≥85% for MAJOR changes  
- Overall accuracy ≥85% across all change types
- Code runs without error on all 15 dataset pairs

---

## Problem Statement

### Background

Current ML dataset versioning practices rely on manual categorization and snapshot-based approaches (DVC, HuggingFace), leading to:
- Silent reproducibility failures when datasets change
- Inconsistent version categorization (60-70% accuracy estimated)
- No automated detection of breaking changes

### Hypothesis Statement

Under ML dataset version change contexts, if SVAD drift detection (KS test + MMD on PCA-reduced features with cold-start thresholds 7%/2%/0.5%) is applied to 15 datasets with documented version histories, then it will correctly classify ≥85% of version changes as MAJOR/MINOR/PATCH with precision ≥70% and recall ≥85%, because statistical drift tests can reliably detect distribution shifts that cause performance degradation.

### Research Question

Can automated statistical drift detection replace manual categorization of dataset version changes while maintaining high classification accuracy?

---

## Functional Requirements

### FR-1: Dataset Acquisition and Preprocessing

**FR-1.1: Multi-Dataset Corpus Loading**
- Load 15 dataset pairs with documented version histories:
  - Vision: ImageNet→ImageNet-v2, CIFAR-10→CIFAR-10.1, MNIST, Fashion-MNIST
  - NLP: GLUE tasks (MRPC, RTE, etc.), SQuAD, MS-MARCO
- Use standard libraries: torchvision.datasets, HuggingFace datasets
- Handle special cases: ImageNet requires manual download, CIFAR-10.1 from official repo

**FR-1.2: Ground Truth Label Creation**
- Create ground truth labels (MAJOR/MINOR/PATCH) for each version transition
- Base labels on documented performance degradation from literature:
  - MAJOR: ≥5% performance drop (e.g., ImageNet→ImageNet-v2: 5-15% drop)
  - MINOR: 1-5% performance drop
  - PATCH: <1% performance drop
- Store labels in structured format (CSV or JSON) for evaluation

**FR-1.3: Data Preprocessing Pipeline**
- **Vision datasets:**
  - Resize to model input size (224×224 for ResNet-50)
  - Normalize with ImageNet statistics (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- **NLP datasets:**
  - Tokenize with pre-trained tokenizers (BertTokenizer for BERT-based models)
  - Pad/truncate to max_length=512
- No data augmentation (use clean data for drift detection)

### FR-2: Feature Extraction

**FR-2.1: Pre-trained Model Loading**
- **Vision models:**
  - ResNet-50: Load weights from torchvision.models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
  - Remove classification head (only use feature extraction layers)
- **NLP models:**
  - BERT-base: Load from transformers.AutoModel.from_pretrained("bert-base-uncased")
  - Extract [CLS] token embeddings or pooled output
- Freeze all model weights (no training/fine-tuning)

**FR-2.2: Feature Extraction Pipeline**
- Extract features from v_old (reference distribution)
- Extract features from v_new (test distribution)
- Feature dimensions: 512-2048 before PCA reduction
- Batch size: 256 for efficient processing
- Use evaluation mode (no gradient computation)

### FR-3: Drift Detection System

**FR-3.1: SVAD Drift Classifier Implementation**
- Implement SVADDriftClassifier class based on TorchDrift library patterns
- Components:
  - PCA dimensionality reduction (n_components=2)
  - KS test detector (Kolmogorov-Smirnov two-sample test)
  - MMD detector (Maximum Mean Discrepancy with Gaussian RBF kernel)
- Cold-start thresholds:
  - MAJOR: 7% drift score
  - MINOR: 2% drift score
  - PATCH: 0.5% drift score

**FR-3.2: Statistical Test Configuration**
- **KS Test:**
  - Apply on PCA-reduced features (2 dimensions)
  - Use Bonferroni correction for multiple comparisons
  - Return maximum statistic across all features
- **MMD Test:**
  - Gaussian RBF kernel with median heuristic for bandwidth
  - Bootstrap permutations: 1000 for p-value computation
  - Works on PCA-reduced features

**FR-3.3: Classification Logic**
- Fit classifier on v_old features (reference distribution)
- Compute drift scores (KS + MMD) on v_new features
- Classify using max(ks_score, mmd_score):
  - If max_score ≥ 0.07 → MAJOR
  - Else if max_score ≥ 0.02 → MINOR
  - Else → PATCH
- Return classification label + drift scores

### FR-4: Evaluation System

**FR-4.1: Metrics Computation**
- Precision (MAJOR changes): TP / (TP + FP)
- Recall (MAJOR changes): TP / (TP + FN)
- F1 Score (MAJOR changes): Harmonic mean of precision and recall
- Overall Accuracy: Correct classifications / Total
- Per-class accuracy for MINOR and PATCH

**FR-4.2: Confusion Matrix Generation**
- 3×3 confusion matrix (MAJOR/MINOR/PATCH true vs predicted)
- Visualize as heatmap with seaborn

**FR-4.3: Per-Dataset Performance Analysis**
- Compute accuracy breakdown by dataset
- Compare vision vs NLP performance
- Identify failure cases for analysis

### FR-5: Visualization

**FR-5.1: Required Figure - Gate Metrics Comparison**
- Bar chart comparing achieved vs target metrics:
  - Precision: achieved vs 70% target
  - Recall: achieved vs 85% target
  - F1: achieved vs 75% target (implied)
  - Accuracy: achieved vs 85% target
- Save to {hypothesis_folder}/figures/gate_metrics.png

**FR-5.2: Additional Visualizations (Autonomous)**
- Confusion matrix heatmap
- Drift score distribution histograms (KS and MMD per version type)
- Per-dataset performance bar chart
- Threshold sensitivity line plot (performance vs threshold values)
- KS vs MMD scatter plot (colored by version label)
- All figures saved to {hypothesis_folder}/figures/

### FR-6: Experiment Execution and Reporting

**FR-6.1: Main Experiment Loop**
- For each of 15 dataset pairs:
  1. Load v_old and v_new
  2. Extract features using frozen models
  3. Fit SVAD classifier on v_old
  4. Classify v_old→v_new transition
  5. Compare against ground truth
  6. Store results
- Aggregate metrics across all dataset pairs

**FR-6.2: Results Reporting**
- Generate summary table: dataset pair, true label, predicted label, KS score, MMD score
- Compute aggregate metrics
- Generate all required visualizations
- Save results to {hypothesis_folder}/04_results.json

**FR-6.3: Validation Report**
- Check PoC pass condition: precision ≥70% AND recall ≥85%
- Log validation status (PASS/FAIL) with metrics
- If FAIL: Log failure reason and drift scores for analysis

---

## Non-Functional Requirements

### NFR-1: Performance

- Feature extraction: <5 minutes per dataset (batch processing)
- Drift detection: <10 seconds per version pair
- Total experiment runtime: <2 hours (15 dataset pairs)

### NFR-2: Reproducibility

- Fixed random seed (seed=42) for PCA and bootstrapping
- Deterministic order of dataset processing
- Log all hyperparameters and threshold values
- Save random states for reproducibility

### NFR-3: Code Quality

- Modular design: separate classes for data loading, feature extraction, drift detection, evaluation
- Type hints for all function signatures
- Docstrings for all public methods
- Clear variable naming (no single-letter variables except loop indices)

### NFR-4: Error Handling

- Handle missing datasets gracefully (skip and log warning)
- Validate feature dimensions before PCA
- Check for NaN/Inf in drift scores
- Retry dataset downloads on network failure (max 3 retries)

### NFR-5: Logging

- Print progress for each dataset pair (1/15, 2/15, ...)
- Log drift scores and classification for each pair
- Save experiment log to {hypothesis_folder}/experiment.log
- Track CUDA memory usage for GPU monitoring

---

## Data Specifications

### Input Data

**Dataset Sources:**
- torchvision.datasets: CIFAR-10, MNIST, Fashion-MNIST
- HuggingFace datasets: GLUE (glue/mrpc, glue/rte), SQuAD (squad), MS-MARCO
- Manual download: ImageNet-1K (requires registration)
- External repos: CIFAR-10.1 (https://github.com/modestyachts/CIFAR-10.1)

**Data Format:**
- Vision: PIL Image → Tensor (C, H, W)
- NLP: Raw text → Tokenized IDs (max_length=512)

**Expected Sample Sizes:**
- Vision datasets: 10K-50K test samples per version
- NLP datasets: 1K-10K validation samples per version
- Use full standard test sets (no arbitrary subsets)

### Output Data

**Results JSON Schema:**
```json
{
  "hypothesis_id": "h-e1",
  "dataset_results": [
    {
      "dataset_pair": "CIFAR-10 → CIFAR-10.1",
      "true_label": "MAJOR",
      "predicted_label": "MAJOR",
      "ks_score": 0.085,
      "mmd_score": 0.092,
      "classification_correct": true
    }
  ],
  "aggregate_metrics": {
    "precision": 0.75,
    "recall": 0.88,
    "f1": 0.81,
    "accuracy": 0.87
  },
  "validation": {
    "poc_pass": true,
    "gate_satisfied": true
  }
}
```

**Figures Output:**
- Format: PNG (300 DPI)
- Location: {hypothesis_folder}/figures/
- Naming: gate_metrics.png, confusion_matrix.png, drift_scores.png, etc.

---

## Dependencies

### Python Libraries

**Core Dependencies:**
- torch>=2.0.0 (PyTorch framework)
- torchvision>=0.15.0 (Vision models and datasets)
- transformers>=4.30.0 (NLP models)
- datasets>=2.12.0 (HuggingFace datasets)
- torchdrift>=0.3.0 (Drift detection library)
- scikit-learn>=1.2.0 (PCA, metrics)
- scipy>=1.10.0 (KS test)
- numpy>=1.24.0
- pandas>=2.0.0 (Results tabulation)

**Visualization:**
- matplotlib>=3.7.0
- seaborn>=0.12.0

**Utilities:**
- pyyaml>=6.0 (Config loading)
- tqdm>=4.65.0 (Progress bars)

### System Requirements

- Python 3.9+
- CUDA 11.7+ (for GPU acceleration)
- GPU with ≥8GB VRAM (for ResNet-50 feature extraction)
- 50GB disk space (for datasets)

### External Data

- ImageNet-1K: Manual download from https://www.image-net.org/
- CIFAR-10.1: Clone from https://github.com/modestyachts/CIFAR-10.1
- All other datasets: Auto-download via torchvision/HuggingFace

---

## Success Criteria

### Primary Success Criteria (Gate Validation)

1. **Precision ≥70%** for MAJOR change detection
2. **Recall ≥85%** for MAJOR change detection
3. **Overall Accuracy ≥85%** across all change types

### Secondary Success Criteria

1. Code runs without error on all 15 dataset pairs
2. Drift scores computed successfully for all transitions
3. All required visualizations generated
4. Results reproducible with fixed seed

### PoC Pass Condition

- Precision ≥70% **AND** Recall ≥85% (no statistical test required for EXISTENCE PoC)
- Direction of improvement over baseline (random: 33%, manual: 60-70%)

---

## Implementation Notes

### TorchDrift Integration

Use TorchDrift library as reference implementation:
- `torchdrift.detectors.KSDriftDetector` for KS test
- `torchdrift.detectors.KernelMMDDriftDetector` for MMD test
- `torchdrift.reducers.pca.PCAReducer` for dimensionality reduction

If TorchDrift unavailable, implement from scratch using:
- `scipy.stats.ks_2samp` for KS test
- Custom MMD implementation following Gretton et al. 2012

### Ground Truth Label Assignment

Literature-based label assignment:
- ImageNet→ImageNet-v2: MAJOR (11.7% drop, Recht et al. 2019)
- CIFAR-10→CIFAR-10.1: MAJOR (5-6% drop, Recht et al. 2019)
- GLUE task updates: Varies by task (consult HuggingFace docs)
- Create ground_truth_labels.json with justification references

### Cold-Start Threshold Rationale

Thresholds (7%/2%/0.5%) are hypothesis-defined constants:
- MAJOR: 7% drift → Breaking change requiring MAJOR version bump
- MINOR: 2% drift → Backward-compatible change requiring MINOR bump
- PATCH: 0.5% drift → Negligible change requiring PATCH bump

These will be evaluated in H-M2 (adaptive threshold hypothesis).

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| TorchDrift library incompatibility | High | Fallback to scipy + custom MMD |
| ImageNet download failure | Medium | Use subset or skip with warning |
| Memory overflow on large datasets | Medium | Batch processing + gradient checkpointing |
| Label assignment subjectivity | High | Use literature-cited performance drops |

### Validation Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low recall (<85%) | Gate failure | Tune thresholds or add features |
| Low precision (<70%) | Gate failure | Refine classification logic |
| Dataset-specific failures | Partial gate | Analyze failure modes per domain |

---

## Appendix: Reference Materials

### Implementation References

1. **TorchDrift Library:** https://github.com/torchdrift/torchdrift
   - KS test implementation with Bonferroni correction
   - MMD implementation with Gaussian RBF kernel
   - PCA reduction patterns

2. **Rabanser et al. 2019:** "Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift" (NeurIPS 2019)
   - Benchmark drift detection methods
   - KS test + MMD evaluation on ImageNet

3. **Recht et al. 2019:** "Do ImageNet Classifiers Generalize to ImageNet?" (ICML 2019)
   - ImageNet→ImageNet-v2 performance degradation (11.7% drop)
   - Ground truth label justification

4. **SciPy KS Test:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html
   - Standard two-sample KS test implementation

### Phase 2C Source

This PRD is derived from:
- File: `/home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_mldpr_sonnet45_no_reflection_3/docs/youra_research/20260512_mldpr/h-e1/02c_experiment_brief.md`
- Specification Level: 1.5 (Concrete + Pseudo-code)

---

**Document Status:** APPROVED FOR IMPLEMENTATION  
**Next Phase:** Phase 3 - Architecture Design (Step 3)
