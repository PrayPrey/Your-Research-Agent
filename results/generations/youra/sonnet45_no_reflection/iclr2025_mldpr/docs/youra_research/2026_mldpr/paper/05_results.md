# 5. Results

## 5.1 Headline Metrics: Gate Failure

Table 2 summarizes our results against the MUST_WORK gate criteria:

| Metric | Target | Achieved | Gap | Status |
|--------|--------|----------|-----|--------|
| **Accuracy** | 85% | 44.4% | -40.6pp | ❌ FAIL |
| **Precision (MAJOR)** | 70% | 16.7% | -53.3pp | ❌ FAIL |
| **Recall (MAJOR)** | 85% | 100% | +15pp | ✅ PASS |
| **F1 (MAJOR)** | 75% | 28.6% | -46.4pp | ❌ FAIL |

The classifier achieves **44.4% overall accuracy**—barely above the 33% random baseline for 3 classes (MAJOR/MINOR/PATCH). Precision for MAJOR detection is catastrophically low at **16.7%**, missing the 70% target by 53.3 percentage points. Paradoxically, recall is perfect (100%), meaning all true MAJOR changes are detected—but at the cost of massive false positive rate.

**Gate verdict:** ❌ **FAILED**. All three metrics (accuracy, precision, F1) fall far short of targets. The hypothesis that fixed thresholds (7%/2%/0.5%) can reliably classify version severity is empirically refuted.

## 5.2 Confusion Matrix: 100% False Positive Rate on PATCH

Figure 2 shows the confusion matrix:

```
              Predicted
           MAJOR  MINOR  PATCH
Actual:
MAJOR        1      0      0      (1 total)
MINOR        0      3      0      (3 total)
PATCH        5      0      0      (5 total)
```

**Key finding:** All 5 PATCH-labeled datasets (MNIST, SST2, SNLI, CoLA, WNLI) were misclassified as MAJOR. This represents a **100% false positive rate** on PATCH labels—every minor update is flagged as a breaking change.

**Why this matters:** In production, this failure mode would cause "alarm fatigue." If every patch-level documentation fix triggers MAJOR version bump warnings, researchers will learn to ignore the system, defeating its purpose. The perfect PATCH→MAJOR confusion reveals that the 7% threshold is fundamentally mis-calibrated for the tested datasets.

**MINOR classification:** The system correctly classified 3/3 MINOR changes (GLUE MRPC, RTE, QNLI) with drift scores between 0.042-0.057, falling within the 2-7% MINOR range. This suggests the MINOR threshold (2%) may be better calibrated, though the small sample size (3 datasets) limits confidence.

**MAJOR detection:** The system correctly identified the 1 true MAJOR change (MultiNLI matched→mismatched, drift score 0.087). However, it also produced 5 false positives, yielding 16.7% precision (1 true positive / 6 total predictions).

## 5.3 Drift Score Distribution: 20× Variance

Figure 3 plots drift scores across all 9 datasets, color-coded by ground truth label. Key observations:

**PATCH labels show extreme variance:** 
- SNLI: 0.082 (slightly above MAJOR threshold)
- CoLA: 0.089  
- WNLI: 0.085
- SST2: **0.79** (highest drift, 10× above MAJOR threshold)
- MNIST→USPS: 0.597 (cross-dataset artifact)

**MINOR labels cluster tightly:**
- GLUE QNLI: 0.042 (lowest drift overall)
- GLUE MRPC: 0.053
- GLUE RTE: 0.057

**MAJOR label below some PATCH scores:**
- MultiNLI: 0.087 (only slightly above PATCH scores 0.082-0.089)

**20× variance:** The ratio between lowest (QNLI: 0.042) and highest (SST2: 0.79) drift scores is **18.8×**, demonstrating that drift magnitude spans nearly two orders of magnitude across datasets with similar ground truth severity.

**Insight:** This variance falsifies the core hypothesis that drift score magnitude alone determines version severity. A 0.79 drift (SST2, labeled PATCH) is 9× higher than 0.087 drift (MultiNLI, labeled MAJOR), yet the ground truth labels reverse the severity ordering. This suggests that "high drift" is relative to dataset-specific baselines, not an absolute threshold.

## 5.4 Per-Dataset Breakdown

Figure 4 shows classification results for each dataset:

**Correctly classified (4/9, 44.4%):**
- ✅ MultiNLI (MAJOR): drift 0.087 → predicted MAJOR
- ✅ GLUE MRPC (MINOR): drift 0.053 → predicted MINOR
- ✅ GLUE RTE (MINOR): drift 0.057 → predicted MINOR
- ✅ GLUE QNLI (MINOR): drift 0.042 → predicted MINOR

**Misclassified (5/9, 55.6%):**
- ❌ MNIST→USPS (PATCH): drift 0.597 → predicted MAJOR
- ❌ SST2 (PATCH): drift 0.79 → predicted MAJOR  
- ❌ SNLI (PATCH): drift 0.082 → predicted MAJOR
- ❌ CoLA (PATCH): drift 0.089 → predicted MAJOR
- ❌ WNLI (PATCH): drift 0.085 → predicted MAJOR

**Pattern:** The classifier achieves 100% accuracy on MINOR changes (3/3) and 100% accuracy on MAJOR changes (1/1), but **0% accuracy on PATCH changes** (0/5). This is not random error—it is systematic mis-calibration where the MAJOR threshold (7%) is set too low for PATCH-level dataset changes.

## 5.5 Comparison to Random Baseline

A random classifier for 3 classes achieves 33.3% accuracy (1/3 uniform distribution). Our classifier achieves **44.4% accuracy**, only **11.1pp above random**. While statistically better than random, this is far from the 85% target and demonstrates that fixed thresholds provide minimal signal for semantic version classification.

**Precision comparison:** Random classifier would yield ~33% precision for MAJOR detection (1/3 of predictions are MAJOR by chance). Our classifier achieves 16.7% precision, **worse than random** for MAJOR predictions due to systematic over-flagging.

## 5.6 Summary of Findings

1. **Fixed thresholds fail comprehensively:** 44.4% accuracy vs 85% target (-40.6pp gap).

2. **100% false positive rate on PATCH labels:** All 5 PATCH datasets exceed MAJOR threshold, revealing fundamental threshold mis-calibration.

3. **20× drift variance invalidates universal thresholds:** Drift scores range 0.042-0.79 across datasets with similar ground truth labels, demonstrating dataset-specific baselines are required.

4. **Perfect recall but abysmal precision:** System detects all MAJOR changes (100% recall) but produces 5× false positive rate (16.7% precision), making it unusable without manual filtering.

5. **Cross-modality generalization untested:** Only 1 vision dataset (and an invalid one—MNIST→USPS is cross-dataset, not version drift). Cannot claim results generalize beyond NLP benchmarks.

These findings falsify the hypothesis that ImageNet-derived thresholds (7%/2%/0.5%) generalize across datasets. The surprising failure mode (100% PATCH error rate) redirects future research toward adaptive calibration or alternative approaches (Section 6.4).
