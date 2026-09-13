## Name

training_data_forensics_from_weights

## Title

Weight Forensics: Decoding Training Data Distribution Properties Directly from Neural Network Weights

## Short Hypothesis

Neural network weights implicitly encode rich statistical properties of their training data—including class imbalance, demographic biases, domain characteristics, and distributional shifts—and these properties can be systematically decoded using a learned weight-space model trained on a model zoo. This is the ideal setting because weights are the only artifact universally available after training (unlike gradients, activations, or data), making weight-based forensics uniquely practical for auditing deployed models.

## Related Work

Existing work touches on related but distinct problems: (1) Membership inference attacks (Shokri et al., 2017; Carlini et al., 2022) ask whether a specific sample was in the training set, requiring query access to the model. (2) Model inversion (Fredrikson et al., 2015) reconstructs representative inputs but requires forward-pass access and focuses on individual samples rather than distributional properties. (3) Dataset inference (Maini et al., 2021) verifies dataset ownership but again requires query access. (4) Hyper-representations (Schürholt et al., 2022) and neural functional networks (Zhou et al., 2023) learn weight-space representations for downstream tasks like accuracy prediction or generalization estimation, but do not target training data properties. (5) Model zoos (Schürholt et al., 2022; Ramé et al., 2023) have been used for weight-space learning but not for forensic data auditing. Our proposal is the first to systematically frame and study the problem of decoding *distributional* training data properties (bias, imbalance, domain shift, label noise rates) purely from weights—without any data or query access—and to build a rigorous benchmark for this task.

## Abstract

The proliferation of publicly deployed neural networks raises urgent questions about what these models 'remember' about their training data. While membership inference and model inversion attacks probe individual data points, a more practically important and underexplored question is: can we decode *distributional* properties of training data—such as class imbalance ratios, demographic group representation, domain characteristics, and label noise rates—directly from model weights, without any access to training data or model queries? We propose Weight Forensics, a framework that treats this as a supervised weight-space learning problem. We construct a large-scale model zoo of thousands of small-to-medium networks trained on controlled variants of standard benchmarks (CIFAR-10/100, CelebA, iWildCam) with systematically varied data distribution parameters. Using equivariant weight-space architectures (Neural Functional Networks or graph hypernetworks), we train meta-models to predict these distributional properties from weights alone. We investigate: (1) which distributional properties are most faithfully encoded in weights, (2) how architecture, training duration, and regularization affect decodability, (3) whether forensic signals transfer across architectures and datasets, and (4) the fundamental limits of weight-based data auditing. Beyond scientific interest, this work has direct applications in AI auditing and fairness compliance—regulators could verify training data properties of deployed models without requiring data access. We will release our model zoo, benchmark, and forensic tools to the community.

## Experiments

1. **Model Zoo Construction**: Train 5,000+ small CNNs and MLPs on CIFAR-10, CelebA, and iWildCam with systematically varied: class imbalance ratios (uniform to 100:1), demographic group proportions (for CelebA gender/age), domain mixtures (for iWildCam), and label noise rates (0-40%). Record all ground-truth data distribution parameters as regression/classification targets.

2. **Baseline Forensic Models**: Train weight-space predictors using (a) flattened weight vectors + MLP, (b) weight statistics (mean, variance, kurtosis per layer) + MLP, (c) Neural Functional Networks (NFN) with permutation equivariance, (d) graph hypernetworks treating the network as a computation graph. Evaluate with R² for regression targets and accuracy/AUC for classification targets.

3. **Decodability Analysis**: For each distributional property, measure how prediction accuracy scales with: training set size of the meta-model, model zoo diversity, and the degree of the distributional shift. Use SHAP values on weight statistics to identify which layers/weight patterns are most informative.

4. **Cross-Architecture Transfer**: Train forensic models on ResNet-20 zoo, test on VGG-11 and MobileNet zoos. Measure transfer gap and test whether permutation-equivariant architectures transfer better than non-equivariant baselines.

5. **Fundamental Limits Experiment**: For each property, identify the minimum training set size and minimum magnitude of distributional shift detectable above chance. Plot detection power curves analogous to statistical power analysis.

6. **Real-World Validation**: Download 200+ models from HuggingFace fine-tuned on known datasets with documented class distributions. Test whether forensic models trained on synthetic zoos generalize to these real-world models.

7. **Evaluation Metrics**: R² and MAE for continuous properties (imbalance ratio, noise rate), AUC and F1 for binary properties (domain presence), Spearman correlation for rankings. Compare against naive baselines (predicting mean, predicting from model accuracy alone).

## Risk Factors And Limitations

1. **Weak Signal**: Distributional properties may be too weakly encoded in weights to be reliably decoded, especially after regularization or early stopping washes out subtle imbalance signals. Mitigation: start with strong/obvious imbalances and gradually test subtler ones.
2. **Architecture Dependence**: Forensic models trained on one architecture may not transfer, limiting practical utility. Mitigation: architecture-conditioned meta-models and permutation-equivariant designs.
3. **Model Zoo Scale**: Training thousands of models is compute-intensive. Mitigation: use small models (ResNet-8, small MLPs) on downsampled datasets; total compute is feasible on a lab GPU cluster.
4. **Confounding Factors**: Different hyperparameters (learning rate, weight decay) may produce similar weight patterns to distributional shifts, making forensics unreliable. Mitigation: include hyperparameter variation in the zoo and condition on or marginalize over it.
5. **Overfitting to Zoo**: Meta-models may overfit to specific zoo characteristics. Mitigation: rigorous train/test splits by model family and dataset variant.
6. **Ethical Dual Use**: Forensic tools could be misused to extract sensitive information about training data. Mitigation: frame results around auditing and fairness compliance; discuss limitations that prevent reconstruction of individual data points.

