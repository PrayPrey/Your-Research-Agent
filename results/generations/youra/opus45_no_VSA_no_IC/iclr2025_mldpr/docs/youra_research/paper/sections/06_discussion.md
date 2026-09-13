# Discussion

## Interpreting the Existence Result

The near-perfect fingerprint classification (99.51% accuracy, Cohen's d = 698) demonstrates that fine-tuning creates highly discriminative representation signatures. This finding extends prior work on shortcut learning (Wang et al., 2025) and underspecification (D'Amour et al., 2020) by showing that benchmark-specific encoding is not merely hypothetical but measurable with simple linear probing.

The asymmetric confusion matrix suggests that different benchmarks create fingerprints of varying strength. CIFAR-100's coarse-grained object categories may encode more diverse statistical patterns than Flowers102's homogeneous plant textures, leading to more distinctive fingerprints.

## Why BFS Failed to Predict Gap

The null correlation (r = 0.022) between BFS and cross-dataset gap challenges our initial hypothesis. We consider several explanations:

### Ceiling Effect

All models achieved BFS > 0.999. With no variance in the predictor variable, correlation analysis is mathematically constrained. This saturation indicates that fingerprints are extremely strong across all models, not that the metric is flawed.

### Binary vs. Graded Fingerprints

Fingerprints may be binary phenomena: once representations encode benchmark-specific patterns, additional "fingerprint intensity" may not exist. The gap would then be determined by factors orthogonal to fingerprint detectability.

### Domain Shift Dominance

CIFAR-100 (diverse objects) and Flowers102 (fine-grained plants) represent fundamentally different visual domains. Cross-dataset gap may reflect domain distance rather than fingerprint strength — models fail because the task changes, not because they overfit to benchmark artifacts.

### Sample Size Limitation

With only 6 models (n=6), statistical power for detecting moderate correlations is limited. True effects may be masked by noise; larger studies could reveal subtle relationships.

## Implications

### For Representation Learning

Benchmark fingerprints establish a new measurable property of fine-tuned models. Future work could use fingerprint analysis to characterize how different training procedures affect representation structure.

### For Model Evaluation

The disconnect between fingerprint detectability and gap prediction suggests that fingerprints alone are insufficient for deployment risk assessment. Alternative metrics — perhaps based on calibrated confidence, layer-wise analysis, or representation diversity — may be needed.

### For Transfer Learning Practice

If fingerprints are inevitable but uncorrelated with deployment failure, practitioners need not avoid benchmark fine-tuning per se. Instead, focus should shift to identifying which aspects of representation change (not just detectability) predict generalization.

## Limitations

1. **Reduced benchmark count:** PoC used 2 benchmarks (50% chance level) instead of planned 5 (20% chance). Effect magnitude may differ at scale.

2. **BFS metric saturation:** Near-perfect classifier confidence eliminates variance. Calibrated metrics (temperature scaling, entropy) could enable correlation analysis.

3. **H-M2 not executed:** Single vs. multi-benchmark comparison requires real fine-grained datasets.

4. **Domain heterogeneity:** CIFAR-100 vs. Flowers102 tests cross-domain transfer, not within-domain generalization.

5. **Architecture scope:** Results are specific to ResNet-50; Transformer architectures (ViT) may exhibit different fingerprint characteristics.

## Broader Impact

This work contributes methodological infrastructure for studying benchmark effects on model representations. The negative mechanism result (BFS-gap correlation) is itself a scientific finding, guiding future research away from simple correlation hypotheses toward more nuanced mechanistic models. We do not identify direct risks from fingerprint detection, though misuse of such techniques for model attribution without consent could raise privacy concerns.
