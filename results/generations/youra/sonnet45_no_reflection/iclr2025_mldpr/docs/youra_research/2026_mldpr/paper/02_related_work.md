# 2. Related Work

## 2.1 Dataset Versioning Tools

**DVC (Data Version Control)** [Kuprieiev et al., 2020] provides Git-like versioning for datasets, treating each version as a snapshot with a unique hash. While DVC excels at tracking "what changed," it does not capture "how much impact" the change has—a 1-line metadata correction and a complete dataset redistribution receive identical treatment. Researchers must manually inspect changelogs to assess whether a version update requires model retraining, creating opportunities for silent failures when changelogs are incomplete or ignored.

**HuggingFace Datasets** [Lhoest et al., 2021] uses revision IDs (Git commit SHAs) to version datasets, enabling exact reproducibility via pinning (e.g., `load_dataset("glue", revision="a3f7b2d")`). However, like DVC, revisions are opaque identifiers without semantic meaning. The library provides no automated mechanism to classify whether revision `a3f7b2d` represents a breaking change, leaving impact assessment to human judgment.

**MLflow Model Registry** [Zaharia et al., 2018] tracks model lineage including dataset versions used for training, enabling "which models used which data" queries. While valuable for dependency tracking, MLflow does not detect when dataset updates invalidate existing models—it records relationships but does not flag drift.

**Our focus:** We extend these systems' version tracking with automated severity classification (MAJOR/MINOR/PATCH) to make version impact explicit rather than implicit. Unlike snapshot-based approaches, we test whether statistical drift detection can automate the "breaking change" determination that currently requires manual inspection.

## 2.2 Distribution Shift Detection

**Statistical tests** for distribution comparison are well-established. The **Kolmogorov-Smirnov (KS) test** [Massey, 1951] compares univariate distributions via maximum distance between empirical CDFs, with O(n log n) computational complexity. **Maximum Mean Discrepancy (MMD)** [Gretton et al., 2012] measures multivariate distribution distance in a reproducing kernel Hilbert space, offering superior sensitivity to high-dimensional shifts but requiring careful kernel selection.

**Rabanser et al. [2019]** ("Failing Loudly") benchmarked drift detection methods on synthetic shifts, finding no single metric dominates across all shift types. Critically, they note that threshold selection is context-dependent—what constitutes "significant drift" varies by application. This finding foreshadows our core challenge: determining universal thresholds for semantic versioning.

**González-Cebrián et al. [2024]** proposed using PCA + autoencoders for dataset versioning, detecting drift to trigger version bumps. However, their system flags that drift occurred without classifying severity (is this a MAJOR breaking change or a PATCH tweak?). Our work extends drift detection to semantic classification.

**TorchDrift** [Schröder et al., 2021] implements KS and MMD tests in PyTorch with built-in feature extraction. While TorchDrift provides p-values for hypothesis testing ("is drift statistically significant?"), it does not map drift magnitudes to semantic version labels—the gap we address.

## 2.3 Semantic Versioning in Software Engineering

**Semantic versioning (SemVer)** [Preston-Werner, 2013] uses MAJOR.MINOR.PATCH format to communicate API compatibility:
- **MAJOR:** Breaking changes requiring consumer updates
- **MINOR:** Backward-compatible feature additions  
- **PATCH:** Backward-compatible bug fixes

SemVer's success in package managers (NPM, PyPI) demonstrates the value of explicit version semantics. When a package bumps MAJOR version, downstream consumers receive clear signals to review compatibility. NPM deprecation warnings reduce package usage by ~60% within 6 months [Decan et al., 2018], showing that automated notifications drive behavior change.

**Key difference for datasets:** Software breaking changes are syntactic (function signatures, API contracts), while dataset breaking changes are statistical (distribution shifts causing performance degradation). This means dataset semantic versioning requires empirical measurement rather than static analysis. Our hypothesis tests whether statistical drift magnitude can serve as a reliable proxy for version severity.

## 2.4 Dataset Evolution and Performance Degradation

**Recht et al. [2019]** documented 10-15% accuracy drops when ImageNet classifiers trained on the original dataset were tested on ImageNet-v2, a carefully reproduced test set. Subsequent analysis [Kornblith et al., 2019] attributed this gap to distribution shift rather than dataset construction flaws—the model simply generalized poorly to the new data distribution.

**CIFAR-10.1** [Recht et al., 2018] and **WILDS** [Koh et al., 2021] similarly demonstrate that minor dataset curation differences produce measurable performance impacts. These findings validate the problem we address (dataset evolution affects reproducibility) while highlighting the challenge: if expert-curated datasets show subtle shifts, automated detection must be highly sensitive.

**Our contribution:** While prior work documents that dataset drift causes performance degradation, we are the first to systematically test whether drift magnitude can be thresholded to classify version severity. Our negative result (100% false positive rate on PATCH labels) quantifies the limits of this approach.

## 2.5 Positioning Our Work

| Method | Semantic Versioning | Automated Detection | Tested Datasets | Reported Accuracy |
|--------|---------------------|---------------------|-----------------|-------------------|
| DVC | ❌ (snapshots only) | ❌ (manual) | N/A | N/A |
| HuggingFace | ❌ (revision IDs) | ❌ (manual) | N/A | N/A |
| González-Cebrián et al. | ❌ (flags drift, no severity) | ✅ (PCA+autoencoder) | 3 | N/A (classification not tested) |
| TorchDrift | ❌ (p-values only) | ✅ (KS+MMD) | Synthetic | N/A (threshold-based classification not goal) |
| **Ours (SVAD)** | ✅ (MAJOR/MINOR/PATCH) | ✅ (KS+MMD+thresholds) | 9 real datasets | 44.4% (failed) |

We are the first to attempt automated MAJOR/MINOR/PATCH classification for datasets using statistical drift. Our negative result—44.4% accuracy with 16.7% precision—provides empirical evidence that fixed thresholds fail and redirects future work toward adaptive or supervised approaches.
