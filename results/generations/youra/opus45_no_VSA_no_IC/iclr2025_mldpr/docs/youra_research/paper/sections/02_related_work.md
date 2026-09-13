# Related Work

## Generalization Gap in Deep Learning

The disconnect between benchmark and deployment performance has been extensively documented. Recht et al. (2019) created ImageNetV2 by replicating the original data collection process and found that all tested classifiers experienced 11-14% accuracy drops, suggesting systematic issues with how benchmark evaluation predicts real-world performance. Subsequent work extended these findings to CIFAR-10 (3-15% gap) and demonstrated that gaps persist across architectures and training procedures.

These studies measure gaps through evaluation metrics but do not identify model-internal signals that might predict or explain such gaps. Our work addresses this limitation by examining whether representations themselves encode benchmark-specific patterns that could serve as diagnostic markers.

## Underspecification and Shortcut Learning

D'Amour et al. (2020) formalized underspecification as a fundamental challenge: multiple models can achieve equivalent training performance while exhibiting different behaviors under distribution shift. This framework explains why benchmark parity does not guarantee deployment equivalence but does not provide mechanisms for detecting underspecification before deployment.

Wang et al. (2025) showed that ImageNet-trained CNNs learn frequency shortcuts, preferring texture over shape information. This work identifies a specific class of spurious features but focuses on the frequency domain rather than benchmark-specific encoding. Our benchmark fingerprint framework generalizes this analysis, asking whether fine-tuning creates detectable signatures regardless of the specific spurious mechanism.

Hermann et al. (2020) explored "dataset bias" in the context of visual question answering, showing that models exploit statistical regularities in benchmark construction. Our methodology extends this analysis to representation space, using linear probing to detect benchmark-specific encoding directly.

## Linear Probing for Representation Analysis

Linear probing has become a standard tool for understanding what information neural network representations encode (Alain & Bengio, 2017; Kornblith et al., 2019). The assumption is that if information is linearly separable in representation space, it is "explicitly" encoded by the network. We apply this methodology to detect benchmark identity from fine-tuned representations — if a linear classifier can predict training benchmark origin, the model has encoded benchmark-specific features.

## Benchmark Concentration and Dataset Reuse

Koch et al. (2021) documented increasing concentration in ML research, with a small number of benchmarks dominating evaluation. They showed that popular benchmarks exhibit systematic patterns in paper usage and citation. Our work complements this meta-scientific analysis by examining what benchmark concentration does to model representations: if narrow training creates fingerprints, concentrated benchmark usage may systematically bias the field's understanding of model capabilities.

## Our Positioning

Prior work establishes that: (1) generalization gaps exist and are systematic; (2) underspecification causes deployment divergence; (3) shortcuts can be domain-specific; (4) benchmark concentration is increasing. We contribute a novel representation-level perspective: measuring benchmark fingerprints directly in model representations using linear probing. Our negative finding — that BFS does not correlate with gap — suggests that the mechanism linking fingerprints to generalization failure is more complex than simple spurious feature encoding, opening new research directions.
