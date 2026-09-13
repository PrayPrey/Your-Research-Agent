# Related Work

## Weight-Space Learning

The treatment of neural network weights as a learnable data modality has emerged as an active research direction. The 2026 Weight Space Learning Survey categorizes this field into understanding, representation, and generation paradigms. Our work falls under *understanding*: decoding behavioral properties from weight inspection.

**Permutation Equivariance.** A fundamental challenge in processing weights is that hidden neurons have no canonical ordering—any permutation of neurons within a layer (with corresponding permutation of adjacent layer connections) yields functionally identical networks. Zhou et al. introduced Neural Functionals (NF-Layers) that respect this symmetry through parameter-sharing schemes. Their characterization theorem proves that NF-Layers capture all permutation-equivariant linear maps. Subsequent work extended this to Universal Neural Functionals capable of processing arbitrary architectures.

**Scalable Representations.** SANE addresses scalability by tokenizing weight subsets sequentially, enabling processing of models too large for monolithic approaches. ProbeGen uses learned deep linear probes with shared generators. Set-based Neural Network Encoding handles mixed-architecture model zoos through logit invariance.

## Property Prediction from Weights

Prior work on property prediction has focused on scalar targets—primarily accuracy and generalization metrics.

**Weight Statistics.** Unterthiner et al. demonstrated that handcrafted weight statistics (layer-wise means, standard deviations, spectral properties) achieve R² ≈ 0.97 for accuracy prediction on the Small CNN Zoo. This established that scalar accuracy is highly predictable from simple features. Our work tests whether this extends to structured behavioral predictions.

**Learned Representations.** SANE achieves R² > 0.9 for accuracy via learned embeddings on MNIST and SVHN variants. Schürholt et al. show that weight-space autoencoders can be trained with combined structural and behavioral losses. Herrmann et al. adapt Deep Weight Space layers for RNNs using "functionalist interrogation"—probing models with inputs to characterize behavior.

**The Gap.** These methods predict *scalar* properties. Class-wise accuracy profiles (10-dimensional vectors for CIFAR-10) represent structured behavioral predictions with cross-class dependencies. Whether the behavioral information captured in scalar predictions extends to structured profiles—and whether behavioral structure transfers to unseen metrics like confusion matrices—remains untested.

## Model Zoos as Data

Model zoos provide the substrate for weight-space learning research. The Small CNN Zoo contains approximately 30,000 CNNs trained on CIFAR-10 with systematic hyperparameter variation. Each model's weights and predictions are stored, enabling post-hoc behavioral analysis.

Unterthiner et al. originally used this zoo to study prediction of model properties. SANE extends to larger model collections. Our work uses a 193-model subset (final-epoch models with complete metadata) to test behavioral variance existence before scaling.

## Behavioral Understanding

The question of what constitutes model "behavior" beyond accuracy connects to interpretability and robustness research.

**Behavioral Loss.** Meynent et al. propose behavioral loss for weight-space autoencoders, showing that structural reconstruction (low MSE) does not guarantee behavioral fidelity. They report 16-20% accuracy drops despite low reconstruction error, motivating explicit behavioral supervision. This supports our premise that behavioral information exists beyond scalar accuracy.

**Failure Mode Analysis.** Work on model debugging examines per-class performance, confusion patterns, and sample-level errors. Our behavioral fingerprinting perspective asks whether these patterns are predictable from weights without inference.

## Positioning

Prior work establishes that (1) weight-space methods achieve high R² for scalar accuracy, and (2) behavioral information beyond accuracy exists in principle. We bridge these by testing whether class-wise behavioral profiles—the structured extension of accuracy prediction—can be extracted from weight features. Our existence result (67.6% residual variance) quantifies the behavioral signal; our mechanism failure (weight statistics R² < baseline) identifies the extraction challenge.
