# 7. Conclusion

We tested whether fixed statistical thresholds derived from ImageNet literature (7%/2%/0.5% drift for MAJOR/MINOR/PATCH classification) could automate semantic versioning for ML datasets. Our experiments on 9 real dataset pairs falsify this hypothesis: the system achieves only 44.4% accuracy (vs 85% target) with 16.7% precision (vs 70% target) for MAJOR change detection.

The most striking failure mode is the **100% false positive rate on PATCH-level changes**—all 5 datasets labeled as minor updates exceeded the MAJOR threshold, misclassified as breaking changes. This reveals that drift magnitude is dataset-relative, not absolute: SST2 (PATCH) scored 0.79 drift while MultiNLI (MAJOR) scored only 0.087, yet the severity ordering is reversed in ground truth labels. The 20× variance in drift scores (0.042 to 0.79) across datasets with similar severity demonstrates that universal thresholds cannot exist without per-dataset calibration.

**Scientific contribution:** This paper provides the first empirical evidence that ImageNet-derived thresholds fail to generalize to NLP benchmarks, with quantitative measurement of the failure magnitude (−53.3pp precision gap, 20× drift variance). While negative results are less celebrated than breakthroughs, rigorous falsification redirects research effort away from dead ends. Our finding that fixed thresholds produce random-level classification (44.4% vs 33% baseline) should dissuade future attempts at universal threshold-based semantic versioning.

**Why the hypothesis failed:** Three root causes conspire against fixed thresholds:

1. **Dataset-specific baselines required:** "High drift" means 0.05 for QNLI but 0.8 for SST2. Without calibrated baselines, thresholds are arbitrary.

2. **Frozen feature extractor robustness:** Pre-trained models optimized for transfer learning (BERT-base, ResNet-50) are too robust to detect subtle version-level shifts, requiring drift-specialized feature extractors.

3. **Cross-modality mis-calibration:** ImageNet characteristics (large-scale, 2048-dim embeddings, continuous pixel distributions) do not transfer to GLUE benchmarks (small-scale, 768-dim text embeddings, discrete token spaces).

**Path forward:** We propose three alternatives, each addressing specific failure modes:

- **Adaptive calibration:** Start with cold-start thresholds, refine per-dataset after ≥5 version transitions using percentile-based or distribution-fitted thresholds. Addresses dataset-specific baseline issue but requires multiple transitions for calibration.

- **Supervised classification:** Train classifiers (Random Forest, XGBoost) on 100+ labeled version pairs with features = [drift_score, dataset_size, domain, ...]. Learns decision boundaries rather than assuming fixed thresholds but requires expensive labeled data collection.

- **Performance-based ground truth:** Replace statistical drift with measured model performance degradation (train on v_old, test on v_new, threshold accuracy drops). Directly captures what matters but computationally expensive and task-specific.

We recommend **hybrid approaches** combining automated drift detection (flag potential breaking changes) with human review (final severity assignment), acknowledging that full automation may be elusive.

**Limitations recap:** Our ground truth labels derive from literature rather than measured performance (limitation for PoC stage, critical for future work). Dataset coverage is incomplete (9/15, missing vision datasets for cross-modality validation). MNIST result is invalid (cross-dataset shift, not version drift). These limitations do not change the negative result—the -53pp precision gap is decisive—but bound the scope of claims to NLP benchmarks.

**Broader impact:** This work contributes to ML reproducibility research by demonstrating that intuitive solutions (statistical drift thresholds) can fail in non-obvious ways (100% FP rate on minor changes). Reproducibility tools require extensive empirical validation, not just conceptual plausibility. Our negative result saves future researchers from pursuing fixed-threshold approaches and provides quantitative evidence to justify more sophisticated alternatives.

**Callback to introduction hook:** We opened by asking, "What if we could automatically classify version changes as 'breaking' vs 'minor' using statistical drift detection?" The answer: not with fixed thresholds. Dataset versioning faces the same challenge as software semantic versioning—"breaking change" requires human judgment about impact, resisting full automation. But unlike software's syntactic changes (API signatures), datasets involve statistical shifts that vary by domain, making automation even harder. Our 100% PATCH misclassification rate quantifies this difficulty.

**Final takeaway:** Automated semantic dataset versioning is harder than anticipated. Statistical drift alone cannot determine version severity without extensive per-dataset calibration or supervised learning. However, our failure mode analysis provides actionable insights—drift detection works (100% recall), threshold generalization fails (16.7% precision)—guiding future systems toward hybrid automation rather than universal thresholds.

---

**Data and code availability:** Experiment code, feature extraction pipelines, and results are available at [REPOSITORY_URL]. Datasets are accessible via HuggingFace (GLUE, SNLI, MultiNLI) and torchvision (MNIST, USPS/EMNIST), except those requiring manual download (ImageNet-v2, CIFAR-10.1).

**Acknowledgments:** We thank the HuggingFace and TorchVision teams for dataset infrastructure, and reviewers for constructive feedback on framing negative results.
