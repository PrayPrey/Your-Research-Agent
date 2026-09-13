# 6. Discussion

## 6.1 Why Fixed Thresholds Fail: Root Cause Analysis

### Root Cause 1: Dataset-Specific Drift Baselines Required

The 20× variance in drift scores (0.042 to 0.79) across datasets with similar ground truth labels reveals that **drift magnitude is relative, not absolute**. Consider:

- **SST2 (PATCH):** Train→validation split, same corpus, expected to be low-drift. Yet drift score = 0.79, far exceeding the 0.07 MAJOR threshold.
- **GLUE QNLI (MINOR):** Train→validation split, similar construction to SST2. Drift score = 0.042, 18× lower.

Both datasets are GLUE benchmarks with train/validation splits from the same source, yet one scores 0.79 and the other 0.042. This suggests that **"high drift" means different things for different datasets**. For SST2, a baseline drift of 0.79 may be normal (validation set possibly curated differently), while for QNLI, 0.042 represents expected variation.

**Implication:** Fixed universal thresholds (7%/2%/0.5%) assume drift scores are comparable across datasets—like assuming 100°C is universally "hot" regardless of whether you're measuring air or molten metal. Instead, each dataset requires calibrated baselines: "SST2 drift >0.8 is MAJOR" while "QNLI drift >0.05 is MAJOR."

### Root Cause 2: Frozen Feature Extractors Insufficiently Sensitive

We used frozen pre-trained models (ResNet-50, BERT-base) optimized for transfer learning, which prioritizes **robustness** to distribution shifts. A model that generalizes well across domains (the goal of transfer learning) will by design produce similar embeddings for different data distributions—exactly the opposite of what drift detection requires.

**Example:** BERT-base trained on Wikipedia generalizes to legal text, medical text, and social media—producing meaningful embeddings despite domain shift. When we use these embeddings to detect drift between SST2 train/validation, the model's robustness may suppress subtle distributional differences, requiring larger actual shifts to register as measurable drift.

**Why PATCH datasets scored high:** If frozen extractors are insufficiently sensitive, even minor dataset changes may produce exaggerated drift scores relative to the underlying performance impact. SST2 (PATCH) showing 0.79 drift suggests the feature space is noisy or the validation set has curation artifacts that don't reflect actual performance degradation.

**Alternative approach:** Train drift-specialized feature extractors using contrastive learning on synthetic distribution shifts, optimizing for **sensitivity** rather than robustness. Recent work on contrastive drift detection [Gui et al., 2021] demonstrates this improves calibration.

### Root Cause 3: Cross-Modality Mis-Calibration

The 7%/2%/0.5% thresholds derive from ImageNet-v2 literature (Recht et al., 2019: 11-14% performance drop). Scaling this to ~7% drift assumes:
1. PCA compression causes ~50% sensitivity loss
2. Performance drops correlate linearly with drift scores  
3. ImageNet characteristics (large-scale, high-resolution images, 1000 classes) generalize to GLUE benchmarks (small-scale, text, 2-10 classes)

**Evidence of mis-calibration:** All 8 NLP datasets show different drift characteristics than expected from ImageNet:
- NLP drift scores span 0.04-0.79 (20× range)
- ImageNet-derived 7% threshold falls in the middle of this range, not at the tail
- PATCH-labeled NLP datasets systematically exceed MAJOR threshold

**Hypothesis:** Text embeddings (768-dim BERT) vs image embeddings (2048-dim ResNet) may have fundamentally different drift magnitude distributions. NLP datasets with smaller vocabularies and discrete token spaces may naturally exhibit higher measured drift than continuous image pixel distributions.

**Implication:** Cross-modality thresholds cannot be transferred without extensive calibration. At minimum, separate thresholds for vision and NLP are required; ideally, per-dataset or per-family (e.g., GLUE-wide) baselines.

## 6.2 Unexpected Finding: SST2 PATCH with 0.79 Drift

SST2 (Stanford Sentiment Treebank) train→validation scored **0.79 drift**, the highest in our corpus, yet is labeled PATCH (expected low impact). Three competing explanations:

**Hypothesis 1: Ground truth label error.** SST2 validation may actually represent a MINOR or MAJOR shift due to curation differences. Without measuring actual model performance degradation (train on SST2-train, test on SST2-validation), we cannot verify the PATCH label is correct.

**Hypothesis 2: Validation set curation artifacts.** SST2 validation may have been curated differently (e.g., balanced class distribution, filtered edge cases) in ways that increase statistical drift without affecting performance. This would make it a false positive for version severity.

**Hypothesis 3: Feature extractor noise.** BERT-base embeddings for short sentences (SST2 is movie reviews, often 10-30 tokens) may be less stable than for longer documents, amplifying spurious drift.

**Evidence needed:** Train a sentiment classifier on SST2-train, measure accuracy on SST2-validation. If accuracy drop is <2% → confirms PATCH label, exposes drift detection false positive. If drop is >5% → ground truth label should be MINOR/MAJOR, vindicating the drift detector.

**Implication:** Ground truth validation via performance measurement is critical. Literature-derived labels are insufficient for evaluating drift-based semantic versioning.

## 6.3 Limitations and Scope Boundaries

### Limitation 1: Ground Truth Labels Not Performance-Validated

We assigned MAJOR/MINOR/PATCH labels based on documented dataset changes (literature descriptions, curator intent) rather than measuring actual model performance degradation. This means:

- **If ground truth is noisy:** Our 44.4% accuracy may underestimate method performance—some "misclassifications" may actually be correct.
- **If ground truth is accurate:** The method genuinely fails to capture performance-relevant drift.

**Why acceptable for this paper:** Our goal is to test whether fixed thresholds generalize. Even if ground truth has errors, the 100% PATCH misclassification rate and 20× drift variance demonstrate threshold failure. Performance validation would strengthen future work but doesn't change the negative result.

**Mitigation:** Future work should train reference models on v_old, measure accuracy on v_new, use performance drops as ground truth (e.g., >5% drop = MAJOR, 2-5% = MINOR, <2% = PATCH).

### Limitation 2: Dataset Coverage Incomplete (9/15)

We successfully loaded 9 of 15 planned datasets (60% coverage), missing:
- **Vision:** 3 of 4 datasets (ImageNet-v2, CIFAR-10.1, Fashion-MNIST)  
- **NLP:** 3 of 11 datasets (QQP, SQuAD, MS-MARCO)

**Impact:** Cannot claim results generalize to computer vision (only 1 vision example, and it's invalid—MNIST→USPS is cross-dataset, not version drift). Our findings apply to NLP benchmarks (8/9 datasets) but vision generalization is untested.

**Why acceptable:** The hypothesis failed decisively on 9 datasets (44.4% accuracy, -53pp gap). Adding 6 more datasets is unlikely to reverse this trend—achieving 85% accuracy on all 15 would require perfect 15/15 classification on the missing 6 datasets, implausible given 4/9 on tested ones.

**Mitigation:** Future work should manually download ImageNet-v2 and CIFAR-10.1 (require registration) to test cross-modality generalization.

### Limitation 3: MNIST Cross-Dataset Shift Contaminates Results

MNIST→USPS/EMNIST (drift 0.597) is **domain adaptation** (different digit sources), not version drift within MNIST. This invalidates the data point—it tests whether frozen ResNet-50 detects domain shift (it does) rather than version-level drift.

**Impact:** Removing MNIST reduces sample to 8 datasets (all NLP). Recalculated accuracy: 4/8 = 50%, still far below 85% target. Precision: 1/5 = 20% (MAJOR detection), still far below 70% target. Conclusion unchanged.

**Why included:** We include MNIST for transparency but note it should be interpreted separately. It demonstrates that drift detection **works** for large domain shifts, but this doesn't help with semantic versioning where changes are more subtle.

**Mitigation:** Exclude MNIST from primary analysis or relabel as "domain shift control" rather than PATCH.

### Limitation 4: Frozen Feature Extractors May Under-Detect Drift

Transfer learning models are optimized for **robustness** (generalize well despite distribution shift), potentially making them insensitive to version-level changes. This is a design choice trade-off:

- **Advantage:** Off-the-shelf models, no training required, computationally cheap  
- **Disadvantage:** May lack sensitivity for subtle shifts

**Impact:** Even with current "under-sensitive" features, drift scores span 0.04-0.79 (20× range). Improving sensitivity might change score magnitudes but won't fix the threshold generalization problem—we'd still need per-dataset calibration.

**Why acceptable:** The failure mode is threshold mis-calibration (100% PATCH error), not missed detections (100% recall). More sensitive features might produce different score magnitudes, but the relative ordering (SST2 >> QNLI) would likely persist, still requiring dataset-specific thresholds.

**Mitigation:** Train drift-specialized feature extractors using contrastive learning on synthetic shifts (future work).

## 6.4 Path Forward: Three Alternative Approaches

Our negative result falsifies fixed-threshold semantic versioning but suggests three viable alternatives:

### Approach 1: Adaptive Per-Dataset Calibration

**Idea:** Start with cold-start thresholds (7%/2%/0.5%) for new datasets, then refine thresholds as more version transitions are observed. For example:
- After 5 version transitions: Use percentile-based thresholds (e.g., 75th percentile = MAJOR)  
- After 20 transitions: Fit distribution model to drift scores, set thresholds at 2σ/1σ/0.5σ

**Advantage:** Addresses dataset-specific baseline issue (Root Cause 1).

**Challenge:** Requires multiple version transitions per dataset to calibrate. New datasets face cold-start problem.

**Validation needed:** Collect 5+ version transitions per dataset, test convergence.

### Approach 2: Supervised Classification from Labeled Version Pairs

**Idea:** Treat semantic versioning as a supervised learning problem. Collect 100+ labeled version pairs (with measured performance degradation), train a classifier (Random Forest, XGBoost, neural network) on features = [drift_score, dataset_size, feature_dim, domain, ...].

**Advantage:** Learns decision boundaries rather than assuming fixed thresholds. Can incorporate dataset metadata (size, domain) to capture context.

**Challenge:** Requires labeled training data (expensive to collect). May not generalize to unseen dataset types.

**Validation needed:** Cross-dataset evaluation (train on GLUE, test on SQuAD).

### Approach 3: Performance-Based Ground Truth

**Idea:** Replace statistical drift with actual model performance degradation. For each version pair:
1. Train reference model on v_old  
2. Measure accuracy on v_old vs v_new
3. If drop >5% → MAJOR, 2-5% → MINOR, <2% → PATCH

**Advantage:** Directly measures what matters (performance impact), bypassing drift score calibration issues.

**Challenge:** Computationally expensive (requires training models per version pair). Requires task-specific model architecture and hyperparameters.

**Validation needed:** Test on datasets with documented performance drops (ImageNet-v2, CIFAR-10.1).

## 6.5 Implications for Reproducibility Research

Our negative result has broader implications:

**Automated reproducibility tools are harder than they appear.** The intuition that "statistical drift → semantic version" seems obvious, yet fails in practice. This suggests that reproducibility interventions require extensive empirical validation, not just conceptual plausibility.

**Dataset versioning needs human-in-the-loop.** Fully automated semantic versioning may be infeasible. Hybrid systems (automated detection + manual review for borderline cases) may be more practical.

**Performance measurement is unavoidable.** Statistical proxies (drift scores) are insufficient. Ground truth must come from actual model performance degradation, requiring computational investment.

**Universal standards are elusive.** Just as software semantic versioning requires human judgment ("is this breaking?"), dataset versioning may resist full automation. Tools can assist (flag potential breaking changes) but cannot replace expert assessment.
