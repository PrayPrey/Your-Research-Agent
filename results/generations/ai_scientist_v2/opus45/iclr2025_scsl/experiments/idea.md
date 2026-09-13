## Name

learning_velocity_signatures

## Title

Learning Velocity Signatures: Detecting Spurious Correlations via Differential Feature Learning Dynamics

## Short Hypothesis

We hypothesize that spurious features exhibit a distinct 'learning velocity signature' compared to core features: they are learned faster (higher initial velocity), plateau earlier (earlier velocity decay), and show lower gradient magnitudes post-plateau. By monitoring per-feature or per-neuron learning velocities throughout training, we can automatically detect and flag potential spurious correlations without requiring group labels or prior knowledge of spurious attributes. This approach is uniquely suited to the training-time setting because: (1) it exploits the inherent temporal asymmetry in how different feature types are learned, (2) it requires no external validation data or annotations, and (3) it provides continuous monitoring rather than post-hoc analysis.

## Related Work

SPARE (Yang et al., 2023) identifies spurious correlations early in training by showing examples with spurious features are separable based on model outputs early on. However, SPARE focuses on sample-level identification at a single early checkpoint rather than continuous feature-level monitoring. The 'Hypernym Bias' work (Malashin et al., 2025) studies hierarchical learning dynamics but doesn't connect this to spurious correlations. Work on simplicity bias (Hu et al., 2020; Rende et al., 2024) establishes that simpler features are learned first but doesn't operationalize this for spurious feature detection. Our approach differs by: (1) proposing continuous monitoring of learning velocity throughout training rather than early-stopping analysis, (2) operating at the feature/neuron level rather than sample level, and (3) providing a principled metric (learning velocity divergence) that can be computed without any spurious feature annotations.

## Abstract

Deep neural networks' tendency to exploit spurious correlations stems from their simplicity bias—simpler features are learned before complex ones. We propose Learning Velocity Signatures (LVS), a novel framework that detects spurious correlations by monitoring the differential learning dynamics of features throughout training. Our key insight is that spurious features exhibit a characteristic temporal signature: rapid initial learning followed by early plateau, while core features show slower but sustained learning. We operationalize this through per-neuron 'learning velocity' metrics computed from gradient statistics and activation changes across training. By tracking when different neurons plateau and computing the velocity divergence between fast-learning and slow-learning feature detectors, LVS automatically flags potential spurious correlations without requiring group labels or prior knowledge of spurious attributes. We validate LVS on standard spurious correlation benchmarks (Waterbirds, CelebA, ColoredMNIST) and demonstrate that: (1) neurons detecting spurious features show statistically distinct velocity signatures, (2) these signatures emerge reliably across architectures and datasets, and (3) velocity-based neuron weighting during inference improves worst-group accuracy. LVS provides a lightweight, annotation-free diagnostic tool that can be integrated into standard training pipelines, offering practitioners continuous visibility into potential spurious feature reliance.

## Experiments

**Experiment 1: Characterizing Learning Velocity Signatures**
- Datasets: Waterbirds, CelebA (hair color vs. gender), ColoredMNIST
- Method: Train ResNet-18/50 with standard ERM. For each neuron in the penultimate layer, compute: (a) learning velocity = moving average of |Δactivation|/Δepoch, (b) gradient magnitude over time, (c) epoch of plateau (when velocity drops below threshold)
- Analysis: Using ground-truth spurious/core feature labels (available at test time), verify that neurons responding to spurious features show higher early velocity and earlier plateau
- Metrics: Correlation between neuron plateau time and spurious feature alignment; statistical tests (t-test, KS-test) comparing velocity distributions

**Experiment 2: Unsupervised Spurious Feature Detection**
- Method: Cluster neurons based on their velocity signatures (early-plateau vs. late-plateau) without using any group labels
- Evaluation: Measure alignment between velocity-based clusters and ground-truth spurious/core feature neurons using probing classifiers
- Baselines: Compare to SPARE's early-training sample identification, random neuron selection

**Experiment 3: Velocity-Guided Inference**
- Method: Down-weight neurons with 'spurious signatures' (high early velocity, early plateau) during inference using a simple learned or heuristic weighting
- Evaluation: Worst-group accuracy, average accuracy on Waterbirds, CelebA, ColoredMNIST
- Baselines: ERM, JTT, SPARE, DFR (Deep Feature Reweighting)

**Experiment 4: Robustness Analysis**
- Vary spurious correlation strength (50%, 80%, 95%, 99%)
- Test across architectures: ResNet, ViT-small, MLP-Mixer
- Ablations: Different velocity computation windows, plateau detection thresholds

**Experiment 5: Real-World Application**
- Dataset: CheXpert (medical imaging with known shortcuts like patient positioning)
- Demonstrate LVS can flag potential shortcuts without prior knowledge

## Risk Factors And Limitations

1. **Feature entanglement**: Spurious and core features may be encoded in overlapping neurons, making clean separation difficult. Mitigation: analyze at multiple granularities (neuron, layer, channel).

2. **Velocity signature overlap**: In some cases, simple but legitimate core features might show similar signatures to spurious features. Mitigation: combine velocity with other signals like cross-validation consistency.

3. **Architecture dependence**: Learning dynamics may vary significantly across architectures (CNNs vs. Transformers). Risk that signatures don't transfer. Mitigation: extensive architecture ablations.

4. **Computational overhead**: Tracking per-neuron statistics throughout training adds memory/compute costs. Mitigation: sample checkpoints rather than continuous monitoring; focus on penultimate layer.

5. **Threshold sensitivity**: Plateau detection requires threshold choices that may be dataset-dependent. Mitigation: use relative rankings rather than absolute thresholds.

6. **Limited to detectable shortcuts**: LVS can only detect spurious features that are genuinely simpler/faster to learn; complex spurious correlations may not show distinct signatures.

