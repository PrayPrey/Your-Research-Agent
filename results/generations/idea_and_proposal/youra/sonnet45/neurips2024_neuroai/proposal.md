# Research Proposal: Free Energy-Coordinated Neuro-Inspired AI for Efficient Continual Learning

## 1. Title

**Free Energy-Coordinated Neuro-Inspired AI: Unifying Spiking Networks, Predictive Coding, and Symbolic Reasoning for Efficient Continual Learning**

## 2. Introduction

### 2.1 Background

The rapid advancement of artificial intelligence has produced remarkable achievements in domains ranging from natural language processing to computer vision. However, contemporary AI systems face a critical trilemma that limits their practical deployment: they excel at accuracy on specific tasks but struggle simultaneously with (1) computational efficiency for resource-constrained environments, (2) continual learning without catastrophic forgetting when adapting to new tasks, and (3) interpretable decision-making that can be audited and understood by human operators.

Biological brains, in contrast, solve all three challenges simultaneously through coordinated neural mechanisms operating at multiple scales. The human brain consumes approximately 20 watts of power while performing complex cognitive tasks that would require kilowatts in artificial systems. Biological systems continuously learn new skills without erasing previously acquired knowledge, and neural computations can be traced through interpretable hierarchical processing pathways.

The emerging field of NeuroAI seeks to bridge artificial and natural intelligence by incorporating brain-inspired mechanisms into computational systems. Current neuro-inspired approaches have demonstrated promise in addressing individual aspects of the trilemma: spiking neural networks (SNNs) provide event-driven sparse computation for efficiency (Yan et al., 2024; HIRE-SNN, 2021), predictive coding (PC) enables self-supervised learning through hierarchical prediction (Ali et al., 2021), Hebbian plasticity supports local synaptic adaptation without global interference (Limbacher et al., 2023), active inference provides adaptive decision-making frameworks, and neuro-symbolic AI (NSAI) offers interpretable reasoning through symbolic rule extraction (Wan et al., 2024).

However, these mechanisms have been explored largely in isolation, lacking a principled integration framework that could enable synergistic advantages. The fundamental challenge is that these heterogeneous components operate on different computational substrates (discrete spikes vs. continuous activations), optimize different local objectives (sparsity vs. prediction accuracy vs. interpretability), and require different learning rules (local Hebbian updates vs. global backpropagation). Simply combining these mechanisms without coordination risks creating interference rather than synergy.

### 2.2 Research Gap

The critical gap in current NeuroAI research is the absence of a unified theoretical framework that can coordinate heterogeneous bio-inspired mechanisms through a shared optimization objective. While the Free Energy Principle (FEP) from neuroscience provides a candidate unifying theory—positing that biological systems minimize variational free energy to maintain homeostasis and adapt to their environment—its application to integrating multiple artificial neuro-inspired components remains unexplored.

Existing work has demonstrated that individual components can be formulated within free energy frameworks: variational autoencoders minimize the Evidence Lower Bound (ELBO), which is equivalent to variational free energy (Kingma & Welling, 2014); predictive coding emerges from energy minimization in recurrent networks (Ali et al., 2021); and active inference formalizes perception and action as free energy minimization. However, no prior work has attempted to create a unified Free Energy Functional (FEF) that coordinates SNNs, PC, Hebbian plasticity, active inference, and NSAI simultaneously through shared variational optimization.

This research addresses three fundamental questions: (1) Can a unified FEF formulation create a shared optimization landscape that enables coordination between heterogeneous neuro-inspired mechanisms? (2) Does FEF-guided coordination produce synergistic advantages in efficiency, continual learning, and interpretability that exceed single-mechanism approaches? (3) What are the causal mechanisms through which FEF minimization enables multi-dimensional performance improvements?

### 2.3 Research Objectives

The primary objective of this research is to develop and validate a Free Energy-Coordinated Neuro-Inspired AI system (H-FEN) that integrates five bio-inspired mechanisms through a unified Free Energy Functional. Specific objectives include:

**Objective 1 (Theoretical):** Formulate a unified Free Energy Functional $\text{FEF} = \alpha \cdot \text{FE}_{\text{pc}} + \beta \cdot \text{FE}_{\text{snn}} + \gamma \cdot \text{FE}_{\text{hebbian}} + \delta \cdot \text{FE}_{\text{ai}} + \epsilon \cdot \text{FE}_{\text{nsai}}$ that provides a shared optimization objective for heterogeneous components, with mathematically rigorous definitions of each component's free energy contribution.

**Objective 2 (Architectural):** Design a hierarchical neural architecture that implements FEF-guided message passing between SNN, PC, Hebbian, active inference, and NSAI layers, resolving the continuous/discrete representation mismatch through hybrid encoding strategies.

**Objective 3 (Empirical - Efficiency):** Demonstrate that H-FEN achieves >2× computational efficiency (measured as operations per inference) compared to standard artificial neural networks while maintaining accuracy within 2% on MNIST and CIFAR-10 benchmarks.

**Objective 4 (Empirical - Continual Learning):** Validate that H-FEN achieves >90% accuracy retention on previously learned tasks in sequential multi-task learning scenarios, compared to <60% for standard fine-tuning approaches.

**Objective 5 (Empirical - Interpretability):** Establish that H-FEN produces valid symbolic decision traces for >80% of test samples, as measured by trace completeness and domain expert evaluation.

**Objective 6 (Mechanistic):** Verify through ablation studies that the Free Energy Functional is the causal mechanism enabling coordination, demonstrating that removing FEF guidance degrades performance across all three dimensions.

### 2.4 Research Significance

This research has significant implications for both theoretical neuroscience and practical AI systems:

**Theoretical Significance:** This work provides the first empirical validation of the Free Energy Principle as a unifying framework for coordinating heterogeneous neuro-inspired computational mechanisms in artificial systems. By demonstrating that FEF minimization enables synergistic integration, this research extends the explanatory scope of the FEP beyond biological systems and establishes it as a principled design framework for NeuroAI architectures.

**Practical Significance:** The proposed H-FEN system addresses critical deployment challenges for AI in resource-constrained environments. Applications include: (1) **Neuromorphic edge computing**: Efficient continual learning on battery-powered devices (robotics, IoT sensors, mobile health monitors); (2) **Interpretable medical AI**: Diagnostic support systems that provide auditable decision traces for clinical validation; (3) **Lifelong learning robotics**: Autonomous systems that adapt to new tasks without forgetting safety-critical behaviors; (4) **Educational AI**: Tutoring systems that explain reasoning processes in human-understandable terms.

**Methodological Significance:** This research establishes a rigorous experimental framework for evaluating multi-dimensional performance in NeuroAI systems, moving beyond single-metric benchmarks to assess the simultaneous achievement of efficiency, adaptability, and interpretability—a critical step toward practical bio-inspired AI deployment.

## 3. Methodology

### 3.1 Theoretical Framework: Unified Free Energy Functional

#### 3.1.1 Free Energy Functional Formulation

The core theoretical contribution is the unified Free Energy Functional that coordinates five neuro-inspired mechanisms:

$$\text{FEF}(\theta, \phi) = \alpha \cdot \text{FE}_{\text{pc}}(\theta_{\text{pc}}) + \beta \cdot \text{FE}_{\text{snn}}(\theta_{\text{snn}}) + \gamma \cdot \text{FE}_{\text{hebbian}}(\theta_{\text{hebb}}) + \delta \cdot \text{FE}_{\text{ai}}(\phi) + \epsilon \cdot \text{FE}_{\text{nsai}}(\theta_{\text{nsai}})$$

where $\theta = \{\theta_{\text{pc}}, \theta_{\text{snn}}, \theta_{\text{hebb}}, \theta_{\text{nsai}}\}$ represents model parameters and $\phi$ represents variational parameters for active inference. The weighting coefficients $\alpha, \beta, \gamma, \delta, \epsilon \in [0,1]$ with $\alpha + \beta + \gamma + \delta + \epsilon = 1$ are learned during training through meta-optimization.

Each component's free energy is defined as follows:

**Predictive Coding Free Energy:**
$$\text{FE}_{\text{pc}} = \sum_{l=1}^{L} \mathbb{E}_{q(z_l)} \left[ \|\epsilon_l\|^2 \right] + \text{KL}(q(z_l) \| p(z_l))$$

where $\epsilon_l = x_l - \hat{x}_l$ is the prediction error at layer $l$, $z_l$ are latent representations, $q(z_l)$ is the approximate posterior, and $p(z_l)$ is the prior. This formulation follows the variational free energy framework where minimizing prediction errors and KL divergence corresponds to maximizing the evidence lower bound (ELBO).

**Spiking Neural Network Free Energy:**
$$\text{FE}_{\text{snn}} = \lambda_{\text{spike}} \sum_{t=1}^{T} \sum_{i=1}^{N} s_i(t) + \lambda_{\text{mem}} \sum_{i=1}^{N} \|u_i(T) - u_{\text{rest}}\|^2$$

where $s_i(t) \in \{0,1\}$ is the spike indicator for neuron $i$ at time $t$, $u_i(T)$ is the membrane potential at final timestep, $u_{\text{rest}}$ is the resting potential, and $\lambda_{\text{spike}}, \lambda_{\text{mem}}$ are regularization coefficients. The first term penalizes spike count (encouraging sparsity), while the second term encourages membrane potentials to return to rest (energy efficiency).

**Hebbian Plasticity Free Energy:**
$$\text{FE}_{\text{hebbian}} = -\sum_{i,j} w_{ij} \cdot \text{corr}(a_i, a_j) + \lambda_{\text{decay}} \sum_{i,j} w_{ij}^2$$

where $w_{ij}$ is the synaptic weight from neuron $j$ to $i$, $\text{corr}(a_i, a_j)$ is the correlation between pre- and post-synaptic activities, and $\lambda_{\text{decay}}$ controls weight decay. This formulation encourages weights to align with activity correlations (Hebbian principle) while preventing unbounded growth.

**Active Inference Free Energy:**
$$\text{FE}_{\text{ai}} = \mathbb{E}_{q(\mathbf{s}|\mathbf{o})} [\log q(\mathbf{s}|\mathbf{o}) - \log p(\mathbf{o}, \mathbf{s})]$$

where $\mathbf{s}$ represents hidden states, $\mathbf{o}$ represents observations, $q(\mathbf{s}|\mathbf{o})$ is the recognition density, and $p(\mathbf{o}, \mathbf{s})$ is the generative model. This standard active inference formulation balances accuracy (fitting observations) and complexity (staying close to priors).

**Neuro-Symbolic AI Free Energy:**
$$\text{FE}_{\text{nsai}} = -\sum_{r \in \mathcal{R}} \text{conf}(r) \cdot \text{cov}(r) + \lambda_{\text{complex}} |\mathcal{R}|$$

where $\mathcal{R}$ is the set of extracted symbolic rules, $\text{conf}(r)$ is rule confidence, $\text{cov}(r)$ is rule coverage (fraction of samples explained), and $\lambda_{\text{complex}}$ penalizes rule set size. This encourages extracting high-confidence, high-coverage rules while maintaining parsimony.

#### 3.1.2 Hierarchical Message Passing Protocol

FEF minimization is implemented through variational message passing in a hierarchical architecture with three levels:

**Level 1 (Sensory):** SNN layer processes input through event-driven spike encoding
**Level 2 (Predictive):** PC layer generates predictions and computes prediction errors
**Level 3 (Symbolic):** NSAI layer extracts interpretable rules from distributed representations

Message passing occurs through:

**Bottom-up messages (error signals):**
$$\mu_{l \to l+1}^{\uparrow} = \Sigma_l^{-1} \epsilon_l$$

where $\Sigma_l$ is the precision (inverse variance) of prediction errors at layer $l$.

**Top-down messages (predictions):**
$$\mu_{l+1 \to l}^{\downarrow} = g_{l+1}(z_{l+1})$$

where $g_{l+1}$ is the generative function mapping higher-level representations to predictions for lower levels.

**Update rule for layer $l$:**
$$\Delta z_l = -\eta \nabla_{z_l} \text{FEF} = -\eta \left( \alpha \frac{\partial \text{FE}_{\text{pc}}}{\partial z_l} + \beta \frac{\partial \text{FE}_{\text{snn}}}{\partial z_l} + \ldots \right)$$

where $\eta$ is the learning rate. This ensures all components contribute to representation updates through their FEF gradients.

### 3.2 System Architecture

#### 3.2.1 H-FEN Core Architecture

The H-FEN Core integrates three primary mechanisms (SNN, PC, Hebbian) in a three-layer hierarchy:

**Layer 1 (Input):** Leaky Integrate-and-Fire (LIF) SNN layer
- Input encoding: Rate coding for static images, temporal coding for sequential data
- LIF dynamics: $\tau_m \frac{du_i}{dt} = -(u_i - u_{\text{rest}}) + I_i(t)$
- Spike generation: $s_i(t) = \Theta(u_i(t) - \theta_{\text{th}})$ where $\Theta$ is Heaviside function
- Reset: $u_i(t^+) = u_{\text{reset}}$ after spike at $t$
- Dimensions: 784 neurons (MNIST), 3072 neurons (CIFAR-10)
- Timesteps: $T = 10$ (based on efficiency threshold from Yan et al., 2024)

**Layer 2 (Hidden):** Predictive Coding layer with Hebbian plasticity
- Continuous-valued representations: $z_2 \in \mathbb{R}^{512}$
- Prediction: $\hat{z}_1 = W_2 z_2$ where $W_2 \in \mathbb{R}^{d_1 \times 512}$
- Error: $\epsilon_1 = z_1 - \hat{z}_1$ (where $z_1$ is continuous membrane potential from SNN layer)
- Hebbian update: $\Delta W_2 = \eta_{\text{hebb}} (z_2 \epsilon_1^T - \lambda_{\text{decay}} W_2)$

**Layer 3 (Output):** Classification layer with PC prediction
- Dimensions: $z_3 \in \mathbb{R}^{C}$ where $C$ is number of classes
- Prediction: $\hat{z}_2 = W_3 z_3$
- Error: $\epsilon_2 = z_2 - \hat{z}_2$
- Standard gradient update: $\Delta W_3 = -\eta \nabla_{W_3} \text{FEF}$

#### 3.2.2 H-FEN Full Architecture

The full system adds active inference and NSAI components:

**Active Inference Module:** Implements action selection through expected free energy minimization
- Policy evaluation: $\pi^* = \arg\min_{\pi} \mathbb{E}_{q(\mathbf{s}|\pi)} [G(\pi)]$ where $G(\pi)$ is expected free energy
- Integration: Modulates learning rates and attention based on prediction uncertainty

**NSAI Layer:** Extracts symbolic rules from Layer 2 representations
- Rule extraction: Decision tree induction on $z_2$ activations
- Rule format: IF (feature $f_i > \theta_i$) AND ... THEN class $c$
- Pruning: Remove rules with $\text{conf}(r) < 0.7$ or $\text{cov}(r) < 0.05$
- Maximum rules: $|\mathcal{R}| \leq 50$ to maintain interpretability

### 3.3 Training Procedure

#### 3.3.1 Two-Phase Training

**Phase 1: Component Pre-training (Epochs 1-20)**
- Train each component separately to initialize parameters
- SNN: Surrogate gradient descent with fast sigmoid surrogate
- PC: Standard predictive coding updates
- Hebbian: Unsupervised correlation-based learning
- Objective: Ensure each component reaches functional baseline

**Phase 2: FEF Joint Optimization (Epochs 21-100)**
- Minimize unified FEF with learned weighting coefficients
- Meta-optimization: Update $\{\alpha, \beta, \gamma, \delta, \epsilon\}$ every 5 epochs using validation performance
- Gradient computation: Automatic differentiation through FEF
- Optimizer: Adam with $\beta_1=0.9, \beta_2=0.999$, initial learning rate $\eta=0.001$
- Learning rate schedule: Cosine annealing with warm restarts

#### 3.3.2 Continual Learning Protocol

For sequential task learning (Objective 4):

**Task Sequence:** 5 tasks from Split-MNIST or Split-CIFAR-10
- Task 1: Classes 0-1, Task 2: Classes 2-3, ..., Task 5: Classes 8-9

**Training per task:**
- Epochs: 20 per task
- No replay buffer (pure continual learning)
- Hebbian plasticity active: Local updates without global backprop interference
- FEF regularization: Maintain $\text{FEF}(\theta_{\text{new}}) \approx \text{FEF}(\theta_{\text{old}})$ to prevent drift

**Evaluation:**
- After training Task $j$, evaluate on all tasks $1, \ldots, j$
- Compute retention: $R_{i,j} = \frac{\text{Acc}_i^{(j)}}{\text{Acc}_i^{(i)}}$ where $\text{Acc}_i^{(j)}$ is accuracy on Task $i$ after training Task $j$
- Average retention: $\bar{R}_j = \frac{1}{j-1} \sum_{i=1}^{j-1} R_{i,j}$

### 3.4 Experimental Design

#### 3.4.1 Datasets and Benchmarks

**Primary Benchmarks:**
- **MNIST:** 60,000 training, 10,000 test images (28×28 grayscale)
- **CIFAR-10:** 50,000 training, 10,000 test images (32×32 RGB)

**Continual Learning Benchmarks:**
- **Split-MNIST:** 5 tasks, 2 classes each
- **Split-CIFAR-10:** 5 tasks, 2 classes each
- **Permuted-MNIST:** 10 tasks with random pixel permutations

**Small-Data Regime:**
- Subsets with 20, 50, 100 samples per class
- Evaluate few-shot learning capability

#### 3.4.2 Baseline Comparisons

**Baseline 1: Standard ANN**
- Architecture: 3-layer MLP with ReLU activations, same parameter count as H-FEN
- Training: Standard cross-entropy loss with Adam optimizer
- Purpose: Computational efficiency comparison

**Baseline 2: Single-Mechanism Approaches**
- SNN-only: Pure spiking network with surrogate gradient training
- PC-only: Predictive coding network without spikes
- Hebbian-only: Network with only local Hebbian updates
- Purpose: Validate synergistic advantage of integration

**Baseline 3: Non-Unified Multi-Component**
- Separate SNN and PC networks (no FEF coordination)
- Ensemble prediction through voting
- Purpose: Verify FEF as causal coordination mechanism

**Baseline 4: Continual Learning Methods**
- Elastic Weight Consolidation (EWC)
- Progressive Neural Networks
- Experience Replay
- Purpose: Continual learning performance comparison

#### 3.4.3 Evaluation Metrics

**Computational Efficiency (Objective 3):**

$$\text{Efficiency Ratio} = \frac{\text{Operations}_{\text{ANN}}}{\text{Operations}_{\text{H-FEN}}}$$

where operations are counted as:
- Multiply-Accumulate Operations (MACs): $\text{MACs} = \sum_l d_l \times d_{l+1}$ for dense layers
- Additions: Spike accumulations in SNN layer
- Target: Efficiency Ratio > 2.0

**Spike Rate:**
$$\text{Spike Rate} = \frac{1}{N \cdot T} \sum_{i=1}^{N} \sum_{t=1}^{T} s_i(t)$$

Target: Spike Rate < 6.4% (Yan et al., 2024 threshold)

**Continual Learning Performance (Objective 4):**

$$\text{Average Retention} = \frac{1}{K(K-1)/2} \sum_{j=2}^{K} \sum_{i=1}^{j-1} \frac{\text{Acc}_i^{(j)}}{\text{Acc}_i^{(i)}}$$

where $K=5$ tasks. Target: Average Retention > 0.90

**Forgetting Measure:**
$$\text{Forgetting} = \frac{1}{K-1} \sum_{i=1}^{K-1} \left( \max_{j \in \{i, \ldots, K\}} \text{Acc}_i^{(j)} - \text{Acc}_i^{(K)} \right)$$

Target: Forgetting < 0.10

**Interpretability (Objective 5):**

$$\text{Trace Completeness} = \frac{|\{x : \exists r \in \mathcal{R}, r(x) = \text{True}\}|}{|\text{Test Set}|}$$

Target: Trace Completeness > 0.80

**Expert Evaluation Score:**
- Sample 100 random test predictions
- Domain experts rate symbolic traces on 1-5 scale (1=no trace, 5=fully interpretable)
- Target: Mean score > 4.0

**Accuracy:**
- Standard classification accuracy
- Constraint: Accuracy within 2% of baseline ANN

#### 3.4.4 Ablation Studies (Objective 6)

To verify FEF as the causal mechanism, conduct systematic ablations:

**Ablation 1: Remove FEF Coordination**
- Train components independently with separate loss functions
- Compare performance to FEF-coordinated version
- Hypothesis: Performance degrades across all three dimensions

**Ablation 2: Remove Individual Components**
- H-FEN without SNN (continuous activations only)
- H-FEN without PC (no hierarchical prediction)
- H-FEN without Hebbian (global backprop only)
- H-FEN without NSAI (no symbolic layer)
- Hypothesis: Each component contributes to specific performance dimension

**Ablation 3: Vary FEF Weights**
- Test configurations: $\alpha=1, \beta=\gamma=\delta=\epsilon=0$ (PC-only), etc.
- Sweep weight space to find optimal balance
- Hypothesis: Balanced weights outperform single-component emphasis

**Ablation 4: Message Passing Frequency**
- Vary update frequency: Every timestep vs. every 5 timesteps vs. no message passing
- Hypothesis: Message passing overhead has optimal frequency

#### 3.4.5 Statistical Analysis

**Sample Size:**
- Primary experiments: $n=20$ independent runs with different random seeds
- Continual learning: $n=15$ runs (higher variance expected)
- Interpretability: $n=100$ expert-evaluated samples

**Statistical Tests:**

**Efficiency (Prediction P1):**
- Test: Paired t-test (H-FEN vs. ANN on same seeds)
- Hypothesis: One-tailed (H-FEN > ANN)
- Significance: $\alpha = 0.05$
- Effect size: Cohen's $d$
- Report: Mean ± SD (95% CI), $p$-value

**Continual Learning (Prediction P2):**
- Test: Independent t-test (H-FEN retention vs. baseline retention)
- Hypothesis: One-tailed (H-FEN > baseline)
- Significance: $\alpha = 0.05$

**Interpretability (Prediction P3):**
- Test: One-sample t-test (expert scores vs. threshold 4.0)
- Hypothesis: One-tailed (scores > 4.0)
- Significance: $\alpha = 0.05$

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:
1. Efficiency Ratio ≤ 1.5× (>25% below target)
2. Average Retention ≤ 0.75 (>15% below target)
3. Trace Completeness < 0.60 or Expert Score < 3.0
4. Ablation studies show no performance degradation when removing FEF coordination
5. Training fails to converge in >50% of runs

### 3.5 Implementation Details

**Software Framework:**
- PyTorch 2.0+ for automatic differentiation
- snnTorch 0.7+ for SNN components
- Custom PC implementation based on Whittington & Bogacz (2017)
- Scikit-learn for NSAI rule extraction

**Hardware:**
- Training: NVIDIA RTX 3090 GPU (24GB VRAM)
- Neuromorphic deployment (optional): Intel Loihi 2 chip for efficiency validation

**Hyperparameters:**
- Batch size: 128
- SNN timesteps: $T=10$
- LIF time constant: $\tau_m = 20$ms
- Spike threshold: $\theta_{\text{th}} = 1.0$
- Hebbian learning rate: $\eta_{\text{hebb}} = 0.01$
- Weight decay: $\lambda_{\text{decay}} = 0.0001$
- FEF weight initialization: $\alpha=\beta=\gamma=\delta=\epsilon=0.2$

**Reproducibility:**
- Fixed random seeds: 42, 123, 456, ... (20 seeds)
- Version control: Git repository with tagged releases
- Containerization: Docker image with all dependencies
- Code release: Open-source repository upon publication

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Computational Efficiency Gains**

We expect H-FEN to achieve 2.0-2.5× computational efficiency compared to standard ANNs on MNIST and CIFAR-10 benchmarks while maintaining accuracy within 2%. The causal mechanism is the combination of: (1) SNN sparse activations reducing dense matrix operations by ~85% (spike rate <6.4%), (2) PC hierarchical prediction eliminating redundant computation on predictable inputs (~30% reduction), and (3) Hebbian local plasticity removing global backpropagation overhead during continual learning (~40% reduction in gradient computation).

**Quantitative prediction:**
- MNIST: 2.3× efficiency (95% CI: [2.1, 2.5]), accuracy 98.5% vs. 98.7% baseline
- CIFAR-10: 2.1× efficiency (95% CI: [1.9, 2.3]), accuracy 89.2% vs. 90.8% baseline
- Spike rate: 5.8% ± 1.2% (below 6.4% threshold)

**Primary Outcome 2: Continual Learning Without Catastrophic Forgetting**

We expect H-FEN to achieve 92-95% average retention across 5 sequential tasks, compared to 45-60% for standard fine-tuning and 70-80% for EWC. The causal mechanism is Hebbian local plasticity enabling task-specific synaptic consolidation without interfering with previously learned representations, coordinated by FEF global objective preventing drift.

**Quantitative prediction:**
- Split-MNIST: 94% retention (95% CI: [92%, 96%]), forgetting 6%
- Split-CIFAR-10: 91% retention (95% CI: [88%, 94%]), forgetting 9%
- Comparison: EWC 78% retention, Progressive Networks 85% retention (but 5× parameters)

**Primary Outcome 3: Interpretable Decision Traces**

We expect H-FEN to produce valid symbolic traces for 82-88% of test samples with expert evaluation scores of 4.2-4.5 out of 5. The causal mechanism is NSAI layer extracting high-confidence rules from PC layer representations, guided by FEF minimization to select rules that reduce prediction error.

**Quantitative prediction:**
- Trace completeness: 85% (95% CI: [82%, 88%])
- Expert score: 4.3 ± 0.4 (95% CI: [4.2, 4.4])
- Rule set size: 35 ± 8 rules (maintaining parsimony)

**Secondary Outcome 1: FEF as Causal Coordination Mechanism**

Ablation studies will demonstrate that removing FEF coordination degrades performance across all three dimensions:
- Efficiency: 1.4× (vs. 2.3× with FEF) - 39% degradation
- Retention: 78% (vs. 94% with FEF) - 16 percentage points degradation
- Interpretability: 62% (vs. 85% with FEF) - 23 percentage points degradation

This will establish FEF as the causal factor enabling synergistic integration rather than mere correlation.

**Secondary Outcome 2: Optimal FEF Weight Configuration**

Meta-optimization will converge to learned weights approximately:
- $\alpha_{\text{pc}} \approx 0.30$ (predictive coding - highest weight for self-supervision)
- $\beta_{\text{snn}} \approx 0.25$ (spiking efficiency)
- $\gamma_{\text{hebbian}} \approx 0.20$ (continual learning)
- $\delta_{\text{ai}} \approx 0.15$ (active inference - adaptive modulation)
- $\epsilon_{\text{nsai}} \approx 0.10$ (symbolic reasoning - interpretability)

This distribution reflects the relative importance of each mechanism for multi-dimensional performance.

**Secondary Outcome 3: Small-Data Regime Performance**

We expect H-FEN to demonstrate superior few-shot learning compared to standard ANNs:
- 20 samples/class: H-FEN 75% accuracy vs. ANN 58% accuracy
- 50 samples/class: H-FEN 82% accuracy vs. ANN 71% accuracy
- 100 samples/class: H-FEN 88% accuracy vs. ANN 81% accuracy

This validates bio-inspired mechanisms for data-efficient learning.

### 4.2 Scientific Impact

**Theoretical Contributions:**

1. **Unified Free Energy Framework for NeuroAI:** This research establishes the Free Energy Principle as a principled integration framework for heterogeneous neuro-inspired mechanisms, extending FEP from descriptive neuroscience theory to prescriptive AI design methodology. This opens new research directions in using variational principles to coordinate bio-inspired components.

2. **Causal Mechanisms of Bio-Inspired Synergy:** By decomposing the 5-step causal chain from FEF formulation to multi-dimensional performance and validating each link through ablation studies, this work provides mechanistic understanding of how and why bio-inspired integration produces synergistic advantages. This moves NeuroAI beyond empirical "brain-inspired" heuristics toward principled design.

3. **Resolution of Continuous/Discrete Representation Mismatch:** The hybrid encoding strategy (discrete spikes for efficiency, continuous membrane potentials for prediction) provides a general solution for integrating event-driven and continuous neural computations, applicable beyond this specific architecture.

**Methodological Contributions:**

1. **Multi-Dimensional Evaluation Framework:** This research establishes rigorous methodology for evaluating AI systems across efficiency, continual learning, and interpretability simultaneously, moving beyond single-metric benchmarks. The statistical analysis framework (paired tests, effect sizes, falsification criteria) provides a template for future NeuroAI research.

2. **Ablation-Based Causal Verification:** The systematic ablation protocol for verifying FEF as causal mechanism (rather than correlation) sets a higher standard for mechanistic claims in bio-inspired AI research.

### 4.3 Practical Impact

**Neuromorphic Edge Computing:**

H-FEN's 2× efficiency gains enable deployment on resource-constrained devices:
- **Battery-powered robotics:** 2× longer operation time on same battery
- **IoT sensors:** Continual learning from streaming data without cloud connectivity
- **Mobile health monitors:** On-device adaptation to individual patient patterns with interpretable alerts

**Estimated impact:** Enabling neuromorphic AI deployment on devices with <5W power budgets, expanding addressable market from data centers to edge devices (projected 10× market expansion by 2030).

**Interpretable Medical AI:**

NSAI symbolic traces enable clinical validation of AI diagnostic support:
- **Radiology:** "IF lesion_size > 2cm AND irregular_border THEN malignancy_risk=high" - auditable by radiologists
- **Drug interaction screening:** Interpretable rules for contraindication detection
- **Personalized treatment:** Continual learning from patient response with explainable recommendations

**Estimated impact:** Addressing FDA interpretability requirements for AI medical devices, accelerating regulatory approval timelines by 30-50%.

**Lifelong Learning Robotics:**

90% retention enables robots to learn new tasks without forgetting safety-critical behaviors:
- **Manufacturing:** Adapt to new product variants without retraining from scratch
- **Elderly care:** Personalize to individual patient preferences over months/years
- **Autonomous vehicles:** Continual adaptation to new environments while maintaining safety protocols

**Estimated impact:** Reducing robot retraining costs by 70% through continual learning, enabling practical deployment in dynamic environments.

**Educational AI:**

Interpretable decision traces enable pedagogically valuable explanations:
- **Intelligent tutoring:** "You made this error because you forgot to apply the chain rule" - specific, actionable feedback
- **Automated grading:** Transparent rubric application with symbolic justifications
- **Adaptive learning:** Continual personalization with interpretable student models

**Estimated impact:** Improving student learning outcomes by 15-20% through interpretable feedback (based on meta-analyses of explanation effectiveness).

### 4.4 Broader Impacts

**Advancing NeuroAI as Interdisciplinary Field:**

This research demonstrates concrete value of neuroscience-AI collaboration, providing evidence that principled bio-inspired integration outperforms ad-hoc engineering. This strengthens the case for sustained investment in NeuroAI research and training programs bridging neuroscience, cognitive science, and AI.

**Ethical AI Development:**

Interpretability is critical for AI accountability, fairness auditing, and bias detection. By achieving >80% interpretable decision traces, H-FEN contributes to the broader goal of trustworthy AI systems that can be audited, debugged, and aligned with human values.

**Environmental Sustainability:**

2× computational efficiency translates to 50% reduction in energy consumption for AI inference. At scale (billions of daily AI queries), this represents significant carbon footprint reduction. Neuromorphic deployment on specialized hardware (e.g., Loihi) could achieve 10-100× additional efficiency gains.

**Democratization of AI:**

Efficiency and small-data learning enable AI deployment in resource-constrained settings (developing countries, small organizations, individual researchers) without requiring massive compute infrastructure or datasets. This reduces barriers to AI adoption and innovation.

### 4.5 Future Research Directions

**Immediate Extensions:**

1. **Scaling to Large Models:** Investigate FEF coordination in transformer architectures (100M+ parameters) for language tasks
2. **Neuromorphic Hardware Deployment:** Validate efficiency gains on Intel Loihi 2 and other neuromorphic chips
3. **Additional Modalities:** Extend to audio (speech recognition), video (action recognition), and multimodal learning

**Long-Term Directions:**

1. **Biological Validation:** Compare H-FEN representations to neural recordings (fMRI, electrophysiology) to test biological plausibility
2. **Meta-Learning FEF Weights:** Develop algorithms to automatically discover optimal FEF configurations for new tasks
3. **Hierarchical Active Inference:** Extend active inference component to multi-level planning and decision-making
4. **Neuro-Symbolic Reasoning:** Enhance NSAI layer with logical inference capabilities (first-order logic, probabilistic reasoning)

This research establishes a foundation for principled bio-inspired AI integration, with potential to transform how we design, deploy, and understand artificial intelligence systems that approach the efficiency, adaptability, and interpretability of biological brains.