# Research Proposal: Inhibitory Error-Gated Hebbian Plasticity for Backpropagation-Free Spiking Neural Networks

## 1. Title

**Inhibitory Error-Gated Hebbian Plasticity (IEGH-HP): A Biologically-Plausible Learning Framework for Energy-Efficient Spiking Neural Networks with Continual Learning Capabilities**

---

## 2. Introduction

### 2.1 Background

The remarkable success of artificial neural networks (ANNs) over the past decade has transformed numerous domains, from natural language processing to computer vision. However, this progress has come at substantial computational and energy costs. Training large-scale models requires extensive GPU resources and consumes significant energy, raising concerns about sustainability and limiting deployment in resource-constrained environments. In contrast, biological neural systems achieve remarkable computational efficiency, with the human brain consuming approximately 20 watts while performing complex cognitive tasks that remain challenging for artificial systems.

Spiking neural networks (SNNs) represent a promising bridge between artificial and biological intelligence. Unlike traditional ANNs that communicate through continuous activation values, SNNs process information through discrete spike events, mimicking the temporal dynamics of biological neurons. This event-driven computation offers inherent energy efficiency, particularly when implemented on neuromorphic hardware such as Intel's Loihi chip or IBM's TrueNorth. However, training SNNs remains a fundamental challenge. The discrete, non-differentiable nature of spike generation precludes direct application of backpropagation, the workhorse algorithm of deep learning.

Current approaches to SNN training primarily rely on surrogate gradient methods, which approximate the derivative of the spike function during the backward pass. While effective, these methods inherit the biological implausibility of backpropagation: they require symmetric weight transport, separate forward and backward phases, and global error propagation—mechanisms absent in biological neural circuits. Furthermore, backpropagation through time (BPTT) for temporal sequences incurs substantial memory and computational overhead, negating much of the efficiency advantage that SNNs promise.

Neuroscience offers compelling alternatives. Biological neural circuits solve the credit assignment problem through local learning rules modulated by global neuromodulatory signals. Inhibitory interneurons play crucial roles in computing prediction errors, maintaining excitatory-inhibitory (E/I) balance, and gating synaptic plasticity. Recent theoretical work has demonstrated that cortical circuits, particularly layer 2/3 neurons, compute uncertainty-modulated prediction errors (UPE) through interactions between excitatory principal neurons and inhibitory interneurons. These local error signals, combined with neuromodulatory broadcasts (e.g., dopamine signaling reward prediction errors), enable effective learning without explicit gradient computation.

### 2.2 Research Objectives

This research proposes **Inhibitory Error-Gated Hebbian Plasticity (IEGH-HP)**, a novel learning framework for SNNs that eliminates the need for backpropagation by leveraging biologically-inspired mechanisms. Our primary objectives are:

1. **Develop a four-component learning mechanism** comprising: (a) prediction encoding via excitatory spike patterns, (b) local error computation through inhibitory interneurons, (c) error-gated Hebbian weight updates, and (d) global neuromodulator scaling based on task-level feedback.

2. **Demonstrate competitive classification performance** within 10% accuracy of surrogate gradient baselines on standard benchmarks (MNIST, CIFAR-10, Spiking Heidelberg Digits).

3. **Achieve significant computational efficiency gains** with 30-50% reduction in synaptic operations compared to backpropagation-based training.

4. **Enable continual learning capabilities** with less than 5% catastrophic forgetting on sequential task learning scenarios.

### 2.3 Significance

This research addresses fundamental challenges at the intersection of neuroscience and artificial intelligence. By developing biologically-plausible learning rules that achieve competitive performance, we contribute to:

- **Neuromorphic Computing**: IEGH-HP is designed for direct implementation on neuromorphic hardware, enabling energy-efficient edge AI applications.
- **Theoretical Neuroscience**: Validating computational models of inhibitory error computation provides insights into biological credit assignment mechanisms.
- **Sustainable AI**: Reducing computational requirements for SNN training aligns with growing concerns about AI's environmental impact.
- **Continual Learning**: The homeostatic mechanisms in IEGH-HP naturally support learning without catastrophic forgetting, a critical capability for real-world deployment.

---

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Network Architecture

We propose a feedforward SNN architecture augmented with lateral inhibitory connections. Each layer $l$ contains two neuron populations:

- **Excitatory Principal Neurons ($E^l$)**: Leaky Integrate-and-Fire (LIF) neurons that encode predictions and propagate information forward.
- **Inhibitory Error Neurons ($I^l$)**: LIF neurons that compute local prediction errors through subtractive inhibition.

The membrane potential dynamics for excitatory neurons follow:

$$\tau_m \frac{dV_E^l}{dt} = -(V_E^l - V_{rest}) + R_m \cdot I_{syn}^l - I_{inh}^l$$

where $\tau_m$ is the membrane time constant, $V_{rest}$ is the resting potential, $R_m$ is the membrane resistance, $I_{syn}^l$ is the synaptic input current, and $I_{inh}^l$ is the inhibitory current from error neurons.

#### 3.1.2 Four-Step Learning Mechanism

**Step 1: Prediction Encoding**

Excitatory neurons encode predictions through their spike patterns. The spike train $S_E^l(t)$ represents the network's prediction at layer $l$:

$$S_E^l(t) = \Theta(V_E^l(t) - V_{th})$$

where $\Theta(\cdot)$ is the Heaviside step function and $V_{th}$ is the firing threshold.

**Step 2: Error Computation**

Inhibitory error neurons compute prediction mismatch through subtractive inhibition. The error signal $e^l(t)$ is computed as:

$$e^l(t) = \sigma\left(\sum_j w_{EI}^l \cdot S_E^l(t) - \sum_k w_{II}^l \cdot S_I^l(t) - \theta_{err}\right)$$

where $w_{EI}^l$ are excitatory-to-inhibitory weights, $w_{II}^l$ are inhibitory-to-inhibitory weights, $\theta_{err}$ is the error threshold, and $\sigma(\cdot)$ is a sigmoid activation ensuring bounded error signals.

**Step 3: Error-Gated Hebbian Plasticity**

Weight updates follow a gated Hebbian rule where the error signal modulates plasticity:

$$\Delta w_{ij}^l = \eta \cdot \text{pre}_j(t) \cdot \text{post}_i(t) \cdot g(e^l(t))$$

where $\eta$ is the learning rate, $\text{pre}_j(t)$ and $\text{post}_i(t)$ are pre- and post-synaptic spike traces, and $g(\cdot)$ is the error gating function:

$$g(e^l(t)) = \begin{cases} e^l(t) & \text{if } e^l(t) > \theta_{gate} \\ 0 & \text{otherwise} \end{cases}$$

The spike traces are computed using exponential filtering:

$$\tau_{trace} \frac{d\text{trace}(t)}{dt} = -\text{trace}(t) + S(t)$$

**Step 4: Neuromodulator Broadcast**

A global neuromodulator signal $M(t)$ scales all weight updates based on task-level feedback:

$$M(t) = \alpha \cdot \mathcal{L}(t) + (1-\alpha) \cdot M(t-1)$$

where $\mathcal{L}(t)$ is the task loss (e.g., cross-entropy) and $\alpha$ is a smoothing parameter. The final weight update becomes:

$$\Delta w_{ij}^l = \eta \cdot M(t) \cdot \text{pre}_j(t) \cdot \text{post}_i(t) \cdot g(e^l(t))$$

#### 3.1.3 Homeostatic Inhibitory Plasticity

To maintain E/I balance throughout training, we implement homeostatic plasticity for inhibitory synapses:

$$\Delta w_{EI}^l = \eta_{homeo} \cdot (r_E^l - r_{target}) \cdot S_E^l(t)$$

where $r_E^l$ is the running average firing rate of excitatory neurons, $r_{target}$ is the target firing rate, and $\eta_{homeo}$ is the homeostatic learning rate.

### 3.2 Implementation Details

#### 3.2.1 Software Framework

We implement IEGH-HP using snnTorch, a PyTorch-based framework for SNNs. Custom layers are developed for:

1. **LateralInhibitoryLayer**: Implements excitatory-inhibitory connectivity with configurable connection patterns.
2. **ErrorGatingModule**: Computes error signals and applies gating to Hebbian updates.
3. **NeuromodulatorModule**: Maintains global neuromodulator state and broadcasts scaling signals.

#### 3.2.2 Network Configurations

| Parameter | MNIST | CIFAR-10 | SHD |
|-----------|-------|----------|-----|
| Input Encoding | Rate coding | Rate coding | Direct spike input |
| Hidden Layers | 2 | 3 | 2 |
| Neurons per Layer | 256 | 512 | 256 |
| Time Steps | 25 | 50 | 100 |
| E/I Ratio | 4:1 | 4:1 | 4:1 |

### 3.3 Experimental Design

#### 3.3.1 Datasets

1. **MNIST**: 60,000 training / 10,000 test images of handwritten digits (28×28 pixels).
2. **CIFAR-10**: 50,000 training / 10,000 test natural images (32×32×3 pixels).
3. **Spiking Heidelberg Digits (SHD)**: 8,156 training / 2,264 test spoken digit recordings encoded as spike trains.

#### 3.3.2 Baseline Methods

1. **Surrogate Gradient SNN (SG-SNN)**: Standard BPTT with fast sigmoid surrogate gradient.
2. **STDP-based SNN**: Spike-timing-dependent plasticity without error gating.
3. **Random Feedback Alignment SNN**: Backpropagation with random feedback weights.

All baselines use identical network architectures to ensure fair comparison.

#### 3.3.3 Evaluation Metrics

**Primary Metrics:**
- **Classification Accuracy**: Test accuracy (%) averaged over 5 random seeds.
- **Accuracy Gap**: $\Delta_{acc} = \text{Acc}_{baseline} - \text{Acc}_{IEGH-HP}$

**Secondary Metrics:**
- **Synaptic Operations (SOPs)**: Total spike-weighted synaptic operations per inference:
$$\text{SOPs} = \sum_{l} \sum_{t} \sum_{i,j} S_j^{l-1}(t) \cdot |w_{ij}^l|$$

- **Energy Efficiency Ratio**: $\text{EER} = \frac{\text{SOPs}_{baseline}}{\text{SOPs}_{IEGH-HP}}$

- **Backward Transfer (Continual Learning)**:
$$\text{BWT} = \frac{1}{T-1} \sum_{i=1}^{T-1} (R_{T,i} - R_{i,i})$$
where $R_{j,i}$ is accuracy on task $i$ after training on task $j$.

#### 3.3.4 Ablation Studies

To verify the causal mechanism, we conduct systematic ablations:

| Ablation | Modification | Tests |
|----------|--------------|-------|
| A1: No Error Gating | Set $g(e^l(t)) = 1$ | Necessity of error computation |
| A2: No Neuromodulator | Set $M(t) = 1$ | Necessity of global modulation |
| A3: No Homeostasis | Disable $\Delta w_{EI}^l$ | Necessity of E/I balance |
| A4: Random Inhibition | Randomize $w_{EI}^l$ | Specificity of inhibitory structure |

#### 3.3.5 Continual Learning Protocol

We evaluate continual learning using Split-MNIST (5 tasks, 2 digits each) and Split-CIFAR-10 (5 tasks, 2 classes each):

1. Train sequentially on tasks $T_1, T_2, ..., T_5$
2. After each task, evaluate on all previous tasks
3. Compare against: (a) naive fine-tuning, (b) Elastic Weight Consolidation (EWC), (c) replay-based methods

#### 3.3.6 Statistical Analysis

- **Sample Size**: 15 runs per condition (5 seeds × 3 hyperparameter configurations)
- **Statistical Tests**: Paired t-tests with Bonferroni correction for multiple comparisons
- **Significance Level**: $\alpha = 0.05$
- **Effect Size**: Cohen's d with 95% confidence intervals
- **Reporting**: Mean ± standard deviation, p-values, effect sizes

### 3.4 Hyperparameter Optimization

Key hyperparameters are tuned using Bayesian optimization with Tree-structured Parzen Estimators (TPE):

| Hyperparameter | Search Range | Default |
|----------------|--------------|---------|
| Learning rate $\eta$ | [1e-4, 1e-2] | 1e-3 |
| Error threshold $\theta_{err}$ | [0.1, 0.5] | 0.3 |
| Gate threshold $\theta_{gate}$ | [0.1, 0.5] | 0.2 |
| Neuromodulator scale $\alpha$ | [0.01, 1.0] | 0.1 |
| Homeostatic rate $\eta_{homeo}$ | [1e-3, 1e-1] | 0.01 |
| Trace time constant $\tau_{trace}$ | [5, 50] ms | 20 ms |

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcomes:**

Based on our theoretical analysis and preliminary evidence from related work, we predict:

| Dataset | Baseline Accuracy | IEGH-HP Target | Expected Gap |
|---------|-------------------|----------------|--------------|
| MNIST | 98.5% ± 0.3% | 94-96% | 3-5% |
| CIFAR-10 | 78% ± 1.5% | 70-75% | 5-8% |
| SHD | 85% ± 2% | 78-82% | 5-7% |

**Energy Efficiency:**
We expect 30-50% reduction in synaptic operations during training due to elimination of the backward pass. Inference efficiency should be comparable to baseline SNNs.

**Continual Learning:**
IEGH-HP with homeostatic plasticity should achieve backward transfer (BWT) > -5%, compared to BWT < -30% for naive fine-tuning.

**Ablation Predictions:**
- Removing error gating (A1): >15% accuracy drop
- Removing neuromodulator (A2): >10% accuracy drop, unstable convergence
- Removing homeostasis (A3): Training instability in >50% of runs
- Random inhibition (A4): >20% accuracy drop

### 4.2 Potential Challenges and Mitigations

1. **Training Instability**: If E/I balance is difficult to maintain, we will implement adaptive homeostatic rates that increase when firing rates deviate significantly from targets.

2. **Accuracy Gap Exceeds 10%**: If the primary prediction fails, we will explore hybrid approaches combining IEGH-HP with sparse backpropagation for the final layer only.

3. **Hyperparameter Sensitivity**: Extensive sensitivity analysis will identify robust operating regimes; we will provide guidelines for hyperparameter selection.

### 4.3 Scientific Impact

**Contributions to NeuroAI:**
- Validates computational models of inhibitory error computation in artificial systems
- Demonstrates that biologically-plausible learning rules can achieve competitive performance
- Provides a framework for integrating neuroscience insights into machine learning algorithms

**Contributions to Neuromorphic Computing:**
- Enables efficient on-chip learning without backpropagation
- Reduces memory requirements by eliminating gradient storage
- Supports continual learning for adaptive edge AI systems

**Contributions to Theoretical Understanding:**
- Clarifies the role of inhibitory interneurons in credit assignment
- Establishes connections between Hebbian plasticity and gradient-based learning
- Provides testable predictions for neuroscience experiments

### 4.4 Broader Impact

**Sustainability**: By reducing computational requirements for SNN training, IEGH-HP contributes to more sustainable AI development practices.

**Accessibility**: Efficient training algorithms enable deployment of intelligent systems on resource-constrained devices, democratizing access to AI capabilities.

**Neuroscience Translation**: The computational framework provides a testbed for neuroscience hypotheses, potentially accelerating understanding of biological learning mechanisms.

### 4.5 Future Directions

1. **Hardware Implementation**: Deploy IEGH-HP on Intel Loihi 2 to validate energy efficiency claims in neuromorphic hardware.

2. **Scaling Studies**: Investigate performance on larger datasets (ImageNet) and deeper architectures.

3. **Multi-modal Learning**: Extend IEGH-HP to handle multi-modal inputs (vision + audio) with cross-modal error computation.

4. **Theoretical Analysis**: Develop formal convergence guarantees and connections to gradient descent.

---

**Conclusion**: This research proposal presents IEGH-HP, a novel biologically-plausible learning framework for SNNs that leverages inhibitory error neurons and neuromodulator-gated Hebbian plasticity. By eliminating backpropagation while maintaining competitive performance, IEGH-HP addresses fundamental challenges in neuromorphic computing and advances our understanding of biological credit assignment mechanisms. The proposed methodology provides rigorous experimental validation with clear success criteria, positioning this work to make significant contributions to the emerging field of NeuroAI.