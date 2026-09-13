# Related Work

Our work builds on and extends three lines of research: benchmark generalization studies, underspecification in machine learning, and texture bias analysis.

## Benchmark Generalization Studies

Recht et al. (2019) provided the first systematic evidence that ImageNet classifiers do not generalize to ImageNet-like test sets. By creating ImageNetV2 with a carefully matched distribution, they demonstrated consistent 10-15% accuracy drops across 70+ models—a finding that challenged assumptions about benchmark reliability. Subsequent work extended this analysis to CIFAR-10 with the CINIC-10 dataset (Darlow et al., 2018), finding similar generalization gaps. However, these studies examine individual datasets in isolation without connecting generalization failure to dataset popularity or the broader ML ecosystem's optimization patterns.

Engstrom et al. (2020) and Taori et al. (2020) further documented "effective robustness" differences across model families, showing that ImageNet accuracy improvements do not uniformly translate to out-of-distribution performance. Our work extends this line by proposing that *popularity itself* is a predictor of generalization failure—not merely an artifact of individual dataset characteristics.

## Underspecification and Benchmark Overfitting

D'Amour et al. (2020) introduced the underspecification framework, demonstrating that models achieving identical benchmark performance can exhibit dramatically different behavior under distribution shift. Their theoretical analysis explains *why* benchmark performance fails to predict deployment success: the optimization surface admits many equivalent solutions, and benchmarks do not constrain which one the model learns. This provides theoretical grounding for our hypothesis: if popular benchmarks receive more optimization pressure, models may converge to increasingly benchmark-specific solutions.

The benchmark co-evolution concept also relates to Goodhart's Law in ML (Thomas & Uminsky, 2022)—when a measure becomes a target, it ceases to be a good measure. We operationalize this concern by measuring the actual research investment differential between high-use and low-use datasets.

## Texture Bias and Feature Learning

Geirhos et al. (2019) demonstrated that ImageNet-trained CNNs rely heavily on texture rather than shape, contrary to human perception. Hermann et al. (2020) traced this bias to training data statistics, suggesting that benchmark-specific artifacts shape learned representations. We hypothesized that intensive optimization on popular benchmarks might amplify texture bias as a mechanism for the co-evolution effect.

However, our experiments contradict this expectation at CIFAR scale: ResNet-18 shows *lower* texture bias (0.126) than VGG-11 (0.161). This suggests that architectural innovations (skip connections, batch normalization) may counteract texture exploitation, and that ImageNet-scale findings do not directly transfer to 32×32 image classification. Our negative result narrows the mechanism search: the co-evolution effect, while real, operates through pathways other than texture bias.

## Dataset Documentation and Ecosystem Analysis

Gebru et al. (2021) proposed Datasheets for Datasets to standardize documentation, addressing concerns about unexamined data practices. While their work focuses on documentation quality, our study examines dataset *usage* patterns—specifically, how uneven research attention across the benchmark ecosystem correlates with generalization outcomes. These perspectives are complementary: both highlight that benchmark selection and maintenance practices deserve more scrutiny than they currently receive.
