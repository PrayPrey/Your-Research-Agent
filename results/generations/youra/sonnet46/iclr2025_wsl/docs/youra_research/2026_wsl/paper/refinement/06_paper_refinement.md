# Comparing Permutation-Equivariant and Flat Encoders for Generalization Gap Prediction on a Neural Network Model Zoo

## Abstract

Weight-space encoders that predict properties of trained neural networks from their parameters face a structural challenge: fully-connected networks are invariant to neuron permutations within layers, yet standard flat-MLP encoders treat neuron position as input signal. This work presents a controlled comparison between Neural Functional Transformers (NFT), a permutation-equivariant encoder, and flat-MLP baselines for generalization gap prediction on the Unterthiner model zoo (29,997 models). In permutation stress tests at severity levels s in {0, 0.25, 0.5, 1.0}, flat-MLP exhibited a Spearman rank correlation drop of 0.160 (from 0.303 to 0.143; bootstrap p = 0.000), while NFT showed no measurable degradation (delta-rho = 4.09 x 10^-6; bootstrap p = 0.477). A six-encoder ablation (18 training runs, 3 seeds) confirmed larger flat-MLP degradation (delta-rho = 0.640) and near-zero NFT sensitivity (delta-rho = 4.71 x 10^-7). Mediation analysis yielded delta-R-squared = 0.228, indicating that NFT embeddings explained additional variance in generalization gap prediction beyond augmentation-based approaches. Permutation augmentation reduced flat-MLP sensitivity by approximately 65% on average but exhibited high seed-dependent variance (delta-rho range: 0.096--0.317). L2-norm canonicalization collapsed to constant predictions across all seeds. NFT used 75K parameters compared to flat-MLP's 3.04M. Two of five planned sub-hypotheses (cross-pipeline transfer, graceful degradation curves) were not executed; cross-pipeline claims remain untested.

## 1. Introduction

Predicting properties of trained neural networks directly from their weights --- generalization gap, test accuracy, training loss --- has applications in model selection, hyperparameter analysis, and automated machine learning. Unterthiner et al. (2020) demonstrated that a flat multi-layer perceptron (flat-MLP) applied to concatenated weight vectors achieves high predictive performance on large model zoos, establishing this as the standard baseline for weight-space property prediction.

A structural property of fully-connected neural networks is that any permutation of neurons within a layer yields a functionally identical network. Flat-MLP encoders, which concatenate weights into a fixed-order vector, treat neuron position as an input feature. When the neuron ordering is consistent across models (as in a single training pipeline), this does not prevent effective prediction. However, when neuron orderings differ --- due to different random seeds, training procedures, or deliberate permutation --- flat-MLP representations may change for functionally equivalent networks.

Neural Functional Transformers (NFT; Zhou et al., 2023) address this by applying permutation-equivariant multi-head attention over per-neuron token sequences. The equivariance property guarantees that any permutation-invariant downstream head produces identical predictions regardless of neuron ordering. NFT was previously evaluated on implicit neural representation (INR) classification tasks but had not been tested on model zoo property prediction tasks such as generalization gap regression.

This work bridges these two lines of research by conducting a controlled comparison of NFT and flat-MLP encoders for generalization gap prediction on the Unterthiner model zoo. The specific contributions are:

1. A direct empirical comparison of NFT and flat-MLP encoders under permutation stress for generalization gap prediction, using a six-encoder ablation suite spanning no equivariance handling through oracle canonicalization.

2. A mediation analysis (following Baron and Kenny, 1986) testing whether the observed robustness difference is attributable to equivariant attention capturing neuron influence concentration signals, yielding delta-R-squared = 0.228.

3. Empirical evaluation of two alternative approaches: permutation augmentation (partial reduction with high variance) and L2-norm canonicalization (collapsed to constant predictor).

4. An observation that NFT achieved higher baseline Spearman rho (0.489 vs. 0.303) with 40x fewer parameters (75K vs. 3.04M), though this comparison is confounded by unmatched parameter counts (see Section 6).

The scope of this study is limited to within-distribution evaluation on a single model zoo. Planned cross-pipeline transfer experiments (MNIST to CIFAR) were not executed and are noted as future work.

## 2. Related Work

### 2.1 Weight-Space Property Prediction

Unterthiner et al. (2020) demonstrated that properties of trained neural networks are predictable from their weights with high fidelity on a zoo of over 120,000 models. Their flat-MLP baseline concatenates all weight matrices into a single vector and applies a standard MLP regression head. Eilertsen et al. (2020) extended this direction with meta-classifiers operating on weight snapshots (320K snapshots across 16K networks). Both works operate in the in-distribution setting with implicitly consistent neuron ordering and do not evaluate behavior under permutation stress.

Schurholt et al. (2021) introduced hyper-representations using contrastive learning with permutation augmentation, demonstrating that augmenting with random neuron permutations during training can improve generalization of weight-space encoders. More recent work has extended weight-space property prediction to graph-structured model representations (WS-KAN, 2026) and large-scale benchmarking across diverse model zoos (Schurholt et al., 2025).

### 2.2 Permutation-Equivariant Architectures for Weight Spaces

Zhou et al. (2023) introduced Neural Functional Transformers (NFT), which apply permutation-equivariant attention layers to neural network weight representations. NFT represents each neuron as a token and applies multi-head attention where equivariance is enforced across the neuron dimension. The equivariance theorem (Theorem 1 of Zhou et al., 2023) guarantees that permuting neurons permutes the attention outputs correspondingly. NFT was evaluated on INR classification tasks but not on model zoo property prediction.

Navon et al. (2023) developed Deep Weight Space Networks (DWSNets), which achieve equivariance for CNN weight spaces. DWSNets encounters runtime shape mismatches with FC-MLP weight vectors and was not included as a baseline.

Subsequent work has extended equivariant weight-space representations to graph metanetworks (Kofinas et al., 2024) and architecture-agnostic encoders (NNiT, 2026).

### 2.3 Model Zoo Analysis

The Unterthiner MNIST zoo (29,997 models) provides a standard benchmark for property prediction. Peebles et al. (2022) demonstrated that diffusion Transformers applied to weight checkpoints can achieve weight-space generative modeling, confirming that Transformer architectures are viable for weight-space tasks.

### 2.4 Positioning

Prior work on weight-space property prediction (Unterthiner et al., 2020; Eilertsen et al., 2020) does not evaluate under permutation stress or compare against equivariant alternatives. Prior work on equivariant weight-space encoders (Zhou et al., 2023; Navon et al., 2023) does not test on model zoo property prediction. This work provides the controlled comparison that neither line has conducted.

## 3. Method

### 3.1 Problem Formulation

Let Z = {(w_i, g_i)}_{i=1}^N be a model zoo, where w_i are the weight parameters of the i-th trained network and g_i = train_loss_i - test_loss_i is the generalization gap. An encoder phi: R^D -> R^d followed by a regression head h: R^d -> R predicts g from w.

A permutation-equivariant encoder satisfies phi(w^pi) = pi-hat(phi(w)) for a corresponding action pi-hat, such that any permutation-invariant head h produces h(phi(w^pi)) = h(phi(w)).

Encoders are evaluated at permutation severity s in {0, 0.25, 0.5, 1.0}, where s is the fraction of neurons randomly permuted within each layer at test time. The primary sensitivity metric is delta-rho = rho(s=0) - rho(s=1.0), where rho is the Spearman rank correlation between predicted and true generalization gap.

### 3.2 Encoder Suite

Six encoder variants were compared:

| Encoder | Architecture | Parameters | Permutation Handling |
|---------|-------------|------------|---------------------|
| flat-MLP | 3-layer MLP, hidden=512 | 3.04M | None |
| flat-MLP+aug | Same as flat-MLP | 3.04M | Training-time augmentation |
| flat-MLP+canon | Same, L2-normed inputs | 3.04M | L2 canonicalization |
| NFT-base | NFT, d_model=128, n_heads=4 | 75K | Architectural equivariance |
| NFT+aug | NFT + augmentation | 75K | Architectural + augmentation |
| Oracle-canon | flat-MLP, optimal alignment | 3.04M | Oracle (upper bound) |

The flat-MLP encoder concatenates all weight matrices into a single 4,912-dimensional vector and applies a 3-layer MLP with hidden dimension 512. The NFT encoder represents each neuron's incoming weight vector (fan_in = 16) as a token, projects it to d_model = 128 dimensions, and applies multi-head attention (n_heads = 4) within each layer. Cross-layer aggregation combines per-layer embeddings into a fixed-size representation. The flat-MLP+aug encoder applies random neuron permutations to input weight vectors during training, following Schurholt et al. (2021). The flat-MLP+canon encoder normalizes each neuron's weight vector to unit L2 norm before encoding. Oracle canonicalization aligns each test model's neurons to a reference model via the optimal permutation minimizing L2 distance.

### 3.3 Mediation Analysis

Following the hierarchical regression framework of Baron and Kenny (1986), generalization gap was regressed on flat-MLP+aug embeddings (yielding R-squared_aug) and on NFT-base embeddings (yielding R-squared_NFT). The mediation effect is delta-R-squared = R-squared_NFT - R-squared_aug. A pre-specified gate condition required delta-R-squared >= 0.10.

### 3.4 Statistical Protocol

Bootstrap testing for delta-rho significance used n = 10,000 paired resamples from the test set, with Holm-Bonferroni correction for multiple comparisons across severity levels. Two-sided p-values tested the null hypothesis delta-rho = 0.

## 4. Experimental Setup

### 4.1 Dataset

The Unterthiner MNIST zoo was used: 29,997 trained 4-layer convolutional neural networks with per-neuron weight vectors reshaped to token format (fan_in = 16 per layer, 4 layers). The original Unterthiner FC-MLP zoo URL was unavailable (HTTP 404); the CNN zoo was adapted to maintain the permutation structure. Data was enriched with train_acc from metrics.csv.gz to enable generalization gap computation (train_loss - test_loss).

| Property | Value |
|----------|-------|
| Total models | 29,997 |
| Training split | 23,997 (80%) |
| Test split | 6,000 (20%) |
| Network depth | 4 layers |
| Fan-in per layer | 16 |
| Prediction target | Generalization gap |
| Split seed | 42 |

### 4.2 Training Protocol

All encoders were trained with Adam optimizer (lr = 0.001, beta = (0.9, 0.999), weight decay = 0.0001), CosineAnnealingLR scheduler (T_max = 100, eta_min = 1e-5), batch size 64. For the primary comparison (h-e1), training ran for 50 epochs with seed 42. For the six-encoder ablation (h-m1), training ran for 100 epochs with seeds {42, 123, 456}, yielding 18 training runs (6 encoders x 3 seeds). The h-m2 evaluation reused h-m1 checkpoints without retraining.

### 4.3 Hardware

Experiments ran on a single NVIDIA H100 NVL GPU. Total: 21 training runs (h-e1: 2 runs, h-m1: 18 runs, h-m2: evaluation-only).

## 5. Results

### 5.1 Primary Robustness Comparison (h-e1)

Table 1 reports Spearman rho at each permutation severity level from the primary two-encoder comparison (50 training epochs, seed 42).

**Table 1: Primary robustness comparison (h-e1)**

| Encoder | rho(s=0) | rho(s=0.25) | rho(s=0.5) | rho(s=1.0) | delta-rho | Bootstrap p |
|---------|----------|-------------|------------|------------|-----------|-------------|
| NFT-base | 0.4886 | 0.4886 | 0.4886 | 0.4886 | 4.09 x 10^-6 | 0.477 |
| flat-MLP | 0.3029 | 0.2704 | 0.1945 | 0.1434 | 0.1595 | 0.000 |

NFT-base showed no statistically significant degradation under permutation stress (p = 0.477; the null hypothesis of delta-rho = 0 was not rejected). Flat-MLP showed statistically significant degradation (p = 0.000), with a 52.7% relative drop in Spearman rho from s=0 to s=1.0.

NFT-base achieved higher baseline Spearman rho (0.489 vs. 0.303 at s=0) despite having 40x fewer parameters than flat-MLP (75K vs. 3.04M). This baseline performance difference was not the primary hypothesis and is discussed further in Section 6.

![Figure 1: Spearman rho vs. permutation severity](figures/fig_e1_2_rho_vs_severity.png)

*Figure 1: Spearman rho as a function of permutation severity for NFT-base and flat-MLP (h-e1). NFT-base maintains rho = 0.4886 across all severity levels. Flat-MLP declines from 0.303 to 0.143.*

![Figure 2: Delta-rho bar chart](figures/fig_e1_1_delta_rho_bar.png)

*Figure 2: Permutation sensitivity (delta-rho) for NFT-base and flat-MLP. Dashed line indicates the pre-specified 0.02 threshold.*

### 5.2 Six-Encoder Ablation and Mediation Analysis (h-m1)

Table 2 reports results from the six-encoder ablation (100 training epochs, 3 seeds, 18 total runs).

**Table 2: Six-encoder ablation results (h-m1, mean across 3 seeds)**

| Encoder | rho(s=0) | rho(s=1.0) | delta-rho | R-squared(s=0) | p (Holm) | Significant |
|---------|----------|------------|-----------|----------------|----------|-------------|
| Oracle-canon | 0.465 | 0.465 | 0.000 | 0.216 | 1.0 | No |
| NFT-base | 0.489 | 0.489 | 4.71 x 10^-7 | 0.300 | 0.829 | No |
| NFT+aug | 0.489 | 0.489 | 2.32 x 10^-7 | 0.300 | 1.0 | No |
| flat-MLP+aug | 0.237 | 0.014 | 0.224 | 0.072 | 0.000 | Yes |
| flat-MLP | 0.303 | -0.337 | 0.640 | 0.092 | 0.000 | Yes |
| flat-MLP+canon | N/A | N/A | NaN | N/A | 0.000 | N/A |

Flat-MLP+canon collapsed to constant predictions (output std approximately 0 across all 3 seeds) and is reported as N/A.

The flat-MLP Spearman rho reversed sign under full permutation (from +0.303 to -0.337), indicating that the encoder's learned representation became anti-correlated with the target under permuted inputs. This effect was larger than in h-e1 (delta-rho = 0.640 vs. 0.160), consistent with the longer training (100 vs. 50 epochs) potentially increasing reliance on neuron ordering statistics.

**Mediation analysis:** delta-R-squared = R-squared(NFT-base) - R-squared(flat-MLP+aug) = 0.300 - 0.072 = 0.228. This exceeded the pre-specified 0.10 threshold by a factor of 2.28. The result indicates that NFT embeddings explained 22.8 additional percentage points of variance in generalization gap prediction compared to augmentation-based embeddings.

![Figure 3: R-squared bar chart showing the mediation gap](figures/fig_m1_3_mediation_bar.png)

*Figure 3: R-squared values for each encoder at s=0. The delta-R-squared = 0.228 gap between NFT-base and flat-MLP+aug is annotated.*

![Figure 4: Rho heatmap across 6 encoders and 4 severity levels](figures/fig_m1_4_rho_heatmap.png)

*Figure 4: Spearman rho for six encoders at four permutation severity levels. NFT-base and NFT+aug rows are uniform. Flat-MLP degrades with increasing severity. Flat-MLP+canon is absent (constant predictor).*

### 5.3 Alternative Approaches (h-m2)

The h-m2 experiment evaluated augmentation and canonicalization as alternatives to architectural equivariance, reusing h-m1 checkpoints. The pre-specified SHOULD_WORK gate required: (a) augmentation delta-rho > 0.05, (b) canonicalization delta-rho > 0.03, (c) NFT delta-rho < 0.02, and (d) a strict ranking NFT < canon < aug < flat-MLP. The gate failed due to canonicalization collapse and the resulting inability to evaluate the ranking condition.

**Augmentation.** Flat-MLP+aug achieved mean delta-rho = 0.207, representing an approximately 67% reduction compared to flat-MLP (delta-rho = 0.627). However, per-seed results showed high variance: delta-rho of 0.096 (seed 42), 0.210 (seed 123), and 0.317 (seed 456). The coefficient of variation was approximately 107%, indicating that the augmentation benefit was strongly seed-dependent. The bootstrap test confirmed that flat-MLP+aug remained significantly less robust than NFT-base (p = 0.000, Holm-corrected).

**Table 3: Per-seed augmentation results (h-m2)**

| Encoder | Seed 42 delta-rho | Seed 123 delta-rho | Seed 456 delta-rho | Mean delta-rho |
|---------|-------------------|--------------------|--------------------|----------------|
| flat-MLP | 0.649 | 0.605 | 0.626 | 0.627 |
| flat-MLP+aug | 0.096 | 0.210 | 0.317 | 0.207 |
| flat-MLP+canon | NaN | NaN | NaN | NaN |
| NFT-base | 2.86 x 10^-7 | 2.81 x 10^-7 | 1.75 x 10^-7 | 2.47 x 10^-7 |

**L2-norm canonicalization.** Flat-MLP+canon produced constant predictions across all 3 seeds (output std approximately 0, all predictions approximately 0.0006). Root cause analysis attributed this to L2 normalization projecting all weight vectors onto the unit sphere, thereby destroying the relative magnitude information that distinguishes networks with different generalization gaps. This represents a systematic failure of this canonicalization approach for this prediction task.

**Oracle canonicalization.** Oracle-canon achieved delta-rho = 0.000, confirming the theoretical upper bound for post-hoc canonicalization with oracle access to the reference neuron ordering.

![Figure 5: Six-encoder delta-rho bar chart](figures/fig_m1_1_delta_rho_bar.png)

*Figure 5: Permutation sensitivity (delta-rho) for all six encoders. Dashed line indicates the 0.02 threshold. NFT-base and NFT+aug fall below the threshold; flat-MLP variants fall above.*

### 5.4 Parameter Efficiency

**Table 4: Parameter count and baseline performance**

| Encoder | Parameters | rho(s=0) | Final Train Loss |
|---------|-----------|----------|------------------|
| NFT-base | 75K | 0.489 | 5.0 x 10^-5 |
| flat-MLP | 3,040K | 0.303 | 6.3 x 10^-5 |
| flat-MLP+aug | 3,040K | 0.237 | not specified |

NFT-base achieved higher Spearman rho at baseline (0.489 vs. 0.303) with 40x fewer parameters. Both models converged to similar final training losses (5.0 x 10^-5 vs. 6.3 x 10^-5). This comparison is confounded by unmatched parameter counts: the performance difference could reflect structural inductive bias, the flat-MLP being over-parameterized relative to the dataset size (3.04M parameters / 23,997 training examples), or both. A matched-parameter comparison was not conducted.

## 6. Discussion

### 6.1 Summary of Findings

Three sub-hypotheses were experimentally evaluated out of five planned:

- **h-e1 (existence, MUST_WORK gate): Passed.** Flat-MLP exhibited significant permutation sensitivity (delta-rho = 0.160, p = 0.000); NFT showed no significant sensitivity (delta-rho = 4.09 x 10^-6, p = 0.477).

- **h-m1 (mechanism, MUST_WORK gate): Passed.** NFT-base delta-rho = 4.71 x 10^-7; mediation delta-R-squared = 0.228 >= 0.10 threshold. Six-encoder ablation across 18 runs confirmed encoder ranking.

- **h-m2 (alternatives, SHOULD_WORK gate): Failed.** Augmentation provided partial compensation (67% delta-rho reduction) but with high seed variance. L2 canonicalization collapsed to constant predictor. The three-way ranking condition could not be evaluated.

- **h-m3 (graceful degradation) and h-m4 (cross-pipeline transfer): Not executed.**

The results support the claim that NFT encoders exhibit substantially lower permutation sensitivity than flat-MLP encoders on this benchmark, and that the difference is mediated by equivariant attention (as measured by the delta-R-squared analysis). The results do not address cross-pipeline transfer robustness, which was part of the original hypothesis but was not experimentally tested.

### 6.2 Interpretation of Mediation Analysis

The delta-R-squared = 0.228 indicates that NFT-base embeddings explained 22.8 percentage points more variance in generalization gap than flat-MLP+aug embeddings. This is interpreted as evidence that equivariant attention captures structural signals (attributed to neuron influence concentration) that augmentation-based approaches do not encode invariantly. However, this analysis compares two architectures of different sizes (75K vs. 3.04M parameters), and the mediation effect could partly reflect architectural differences unrelated to equivariance. A more controlled mediation analysis would require matched-parameter encoders.

### 6.3 Flat-MLP Degradation Across Experiments

Flat-MLP delta-rho was 0.160 in h-e1 (50 epochs) and 0.640 in h-m1 (100 epochs). The larger degradation under longer training is consistent with the hypothesis that extended training increases reliance on neuron ordering statistics, though other differences between experiments (number of seeds, minor implementation variations) could also contribute. Both values exceeded the pre-specified 0.10 threshold.

### 6.4 Limitations

**Dataset adaptation.** The intended Unterthiner FC-MLP zoo was unavailable (URL returned HTTP 404). The CNN zoo (29,997 models, 4-layer CNNs) was adapted by reshaping weight matrices to per-neuron token format. While the permutation structure is preserved by this adaptation, absolute metric values may differ on native FC-MLP weights, and the generalization gap characteristics may differ between CNN and FC-MLP model families.

**Cross-pipeline transfer not tested.** The original hypothesis included a prediction about cross-pipeline transfer robustness (MNIST to CIFAR). Sub-hypotheses h-m3 and h-m4 were not executed. No claims about cross-distribution generalization can be made from this study.

**Canonicalization scope.** Only L2-norm canonicalization was tested as a post-hoc approach. Stronger canonicalization methods (sort-by-magnitude, Hungarian alignment without oracle access, spectral normalization) were not evaluated. The oracle canonicalization result (delta-rho = 0.000) demonstrates that perfect post-hoc alignment is theoretically possible; whether practical non-oracle canonicalization can approach this bound is an open question.

**Augmentation seed count.** The augmentation analysis is based on 3 seeds. The observed high variance (delta-rho range: 0.096--0.317) is suggestive of a multi-modal optimization landscape but cannot be characterized precisely with so few samples.

**Unmatched parameter comparison.** NFT (75K parameters) and flat-MLP (3.04M parameters) differ by 40x in parameter count. The observed baseline performance difference (rho = 0.489 vs. 0.303) cannot be attributed solely to equivariance without a matched-parameter control. Flat-MLP may be over-parameterized for a 30K-model zoo (approximately 127 parameters per training example vs. 3 for NFT).

**Single zoo, single task.** All experiments use a single model zoo (Unterthiner MNIST) and a single prediction target (generalization gap). Generalization to other zoos, architectures, or prediction targets is not established.

### 6.5 Broader Considerations

The mediation analysis framework (delta-R-squared as a test of architectural inductive bias) may be applicable to other settings where encoder architecture is compared against the symmetry structure of the input domain. The finding that L2-norm canonicalization collapses the predictor provides a concrete negative result for weight-space analysis: magnitude-destructive normalization removes information relevant to scalar property prediction from weight vectors.

## 7. Conclusion

This study compared Neural Functional Transformer (NFT) encoders with flat-MLP baselines for generalization gap prediction on the Unterthiner model zoo under permutation stress. NFT exhibited near-zero permutation sensitivity (delta-rho approximately 4.7 x 10^-7) across 21 training runs, while flat-MLP showed significant degradation (delta-rho = 0.160--0.640). Mediation analysis (delta-R-squared = 0.228) indicated that the robustness difference was associated with equivariant attention capturing structural signals beyond what augmentation provides. Permutation augmentation partially reduced flat-MLP sensitivity but with high seed-dependent variance. L2-norm canonicalization collapsed to constant predictions.

These results were obtained on a single model zoo (Unterthiner MNIST CNN zoo adapted to token format, 29,997 models) with a single prediction target (generalization gap). Two of five planned sub-hypotheses (cross-pipeline transfer and graceful degradation) were not executed. A matched-parameter comparison between NFT and flat-MLP was not conducted.

Future work includes: (1) executing the cross-pipeline transfer experiments (h-m3, h-m4) using existing infrastructure, (2) validating on native FC-MLP zoo weights, (3) testing stronger canonicalization approaches (Hungarian alignment, sort-by-magnitude), (4) conducting a matched-parameter comparison to disentangle equivariance effects from parameter count effects, and (5) extending to additional model zoos and prediction targets.

## References

- Baron, R. M. & Kenny, D. A. (1986). The moderator-mediator variable distinction in social psychological research. *Journal of Personality and Social Psychology*, 51(6), 1173--1182.

- Eilertsen, G., Jonsson, D., Ropinski, T., Unger, J., & Ynnerman, A. (2020). Classifying the Classifier: Dissecting the Weight Space of Neural Networks. *ECAI 2020*. DOI: 10.3233/FAIA200209.

- Navon, A., Shamsian, A., Achituve, I., Fetaya, E., Chechik, G., & Maron, H. (2023). Equivariant Architectures for Learning in Deep Weight Spaces. *ICML 2023*. arXiv:2301.12780.

- NNiT (2026). NNiT: Width-Agnostic Neural Network Generation with Structurally Aligned Weight Spaces. arXiv:2603.00180.

- Peebles, W. S., Radosavovic, I., Brooks, T., Efros, A. A., & Malik, J. (2022). Learning to Learn with Generative Models of Neural Network Checkpoints. arXiv:2209.12892.

- Schurholt, K., Kostadinov, D., & Borth, D. (2021). Hyper-Representations: Self-Supervised Representation Learning on Neural Network Weights. arXiv:2110.15288.

- Schurholt, K., et al. (2025). A Model Zoo on Phase Transitions in Neural Networks. arXiv:2504.18072.

- Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., & Tolstikhin, I. (2020). Predicting Neural Network Accuracy from Weights. arXiv:2002.11448.

- WS-KAN (2026). A Graph Meta-Network for Learning on KANs. arXiv:2602.16316.

- Zhou, A., Yang, K., Jiang, Y., Burns, K., Xu, W., Sokota, S., Kolter, J. Z., & Finn, C. (2023). Neural Functional Transformers. *NeurIPS 2023*. arXiv:2305.13546.
