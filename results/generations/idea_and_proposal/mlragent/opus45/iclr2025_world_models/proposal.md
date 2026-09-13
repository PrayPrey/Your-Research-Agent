# Research Proposal: Causal State-Space Models for Compositional World Understanding

## 1. Introduction

### Background

World models have emerged as a fundamental paradigm in artificial intelligence, enabling agents to understand, predict, and interact with complex environments. These models have evolved from simple recurrent neural networks capturing low-level physical dynamics to sophisticated systems capable of generating realistic, high-dimensional simulations of the real world. Recent advances, exemplified by systems like Sora and Genie, demonstrate the remarkable capacity of modern world models to synthesize complex visual environments. However, despite these achievements in pattern recognition and generation, current world models exhibit a critical limitation: they struggle with compositional generalization—the ability to understand and predict outcomes for novel combinations of previously learned concepts.

Consider a world model trained on scenarios involving balls rolling down inclines and cubes being pushed across surfaces. While such a model may accurately predict each scenario individually, it often fails when asked to predict how a cube would behave on an incline—a novel combination of known concepts. This limitation stems from a fundamental architectural shortcoming: existing models tend to entangle causal mechanisms with spurious correlations present in training data, learning "what typically happens together" rather than "what causes what."

State-space models (SSMs) have recently gained prominence as efficient backbones for temporal modeling, offering superior computational efficiency for long-range dependencies compared to transformers and traditional RNNs. Models like Mamba and S4 have demonstrated impressive performance across sequence modeling tasks. However, these architectures treat state dimensions as monolithic vectors without explicit causal structure, leading to representations where independent mechanisms become intertwined and brittle under distribution shift.

### Research Objectives

This research proposes **Causal State-Space Models (C-SSM)**, a novel architecture that augments state-space models with learned causal graphs over latent state dimensions. Our primary objectives are:

1. **Develop a principled framework** for discovering causal structure among latent state variables using interventional data from environment interactions.

2. **Design a modular state transition mechanism** that factorizes dynamics according to discovered causal dependencies, enabling independent mechanism updates.

3. **Demonstrate improved compositional generalization** on established benchmarks measuring prediction accuracy for novel concept combinations.

4. **Provide interpretable state representations** that align with ground-truth causal factors in controlled environments.

### Significance

This research addresses a fundamental gap between pattern recognition and genuine understanding in world models. By enabling models to discover and exploit modular causal mechanisms, C-SSM offers several transformative benefits:

- **Robust Generalization**: Models can transfer knowledge to out-of-distribution scenarios by recombining learned causal mechanisms.
- **Sample Efficiency**: Learning independent mechanisms reduces the combinatorial explosion of training data needed for comprehensive coverage.
- **Interpretability**: Explicit causal structure provides human-understandable explanations of model predictions.
- **Foundation for Planning**: Causal world models support counterfactual reasoning essential for robust decision-making.

This work bridges two critical research directions—causality and scalable sequence modeling—offering a principled path toward world models that truly understand, rather than merely memorize, environment dynamics.

## 2. Methodology

### 2.1 Problem Formulation

We consider a world model that observes sequences of high-dimensional observations $\mathbf{o}_t \in \mathcal{O}$ (e.g., images) and actions $\mathbf{a}_t \in \mathcal{A}$, and aims to learn a latent state representation $\mathbf{z}_t \in \mathbb{R}^d$ that captures the underlying dynamics. We assume the true data-generating process follows a structural causal model (SCM) where state dimensions have sparse causal dependencies captured by a directed acyclic graph (DAG) $\mathcal{G}$.

**Assumption 1 (Modular Dynamics)**: The true dynamics factorize according to causal parents:
$$p(\mathbf{z}_{t+1} | \mathbf{z}_t, \mathbf{a}_t) = \prod_{i=1}^{d} p(z_{t+1}^{(i)} | \mathbf{z}_t^{\text{Pa}(i)}, \mathbf{a}_t)$$
where $\text{Pa}(i)$ denotes the parent set of variable $i$ in $\mathcal{G}$.

**Assumption 2 (Independent Mechanisms)**: Each conditional distribution $p(z_{t+1}^{(i)} | \mathbf{z}_t^{\text{Pa}(i)}, \mathbf{a}_t)$ can change independently across environments without affecting other mechanisms.

### 2.2 Architecture Overview

C-SSM consists of four interconnected components:

1. **Encoder** $q_\phi(\mathbf{z}_t | \mathbf{o}_t)$: Maps observations to latent states
2. **Causal Discovery Module**: Learns the causal graph $\mathcal{G}$ over state dimensions
3. **Modular SSM Dynamics**: State transitions factorized by $\mathcal{G}$
4. **Decoder** $p_\psi(\mathbf{o}_t | \mathbf{z}_t)$: Reconstructs observations from latent states

### 2.3 Causal Discovery Phase

We employ a differentiable approach to structure learning that identifies causal relationships using interventional data. The key insight is that actions in interactive environments serve as natural interventions, breaking spurious correlations while preserving causal dependencies.

**Adjacency Matrix Parameterization**: We represent the causal graph using a continuous adjacency matrix $\mathbf{A} \in [0,1]^{d \times d}$, parameterized through a sigmoid transformation of learnable parameters $\mathbf{W}$:
$$A_{ij} = \sigma(W_{ij})$$

**Acyclicity Constraint**: To ensure the learned graph is a valid DAG, we incorporate the NOTEARS acyclicity constraint:
$$h(\mathbf{A}) = \text{tr}(e^{\mathbf{A} \circ \mathbf{A}}) - d = 0$$

**Interventional Score Matching**: Using action-induced interventions, we maximize the likelihood of observed state transitions while encouraging sparsity:
$$\mathcal{L}_{\text{causal}} = \mathbb{E}_{(\mathbf{z}_t, \mathbf{a}_t, \mathbf{z}_{t+1}) \sim \mathcal{D}} \left[ \sum_{i=1}^{d} \log p(z_{t+1}^{(i)} | \mathbf{A}_{:,i} \odot \mathbf{z}_t, \mathbf{a}_t) \right] - \lambda_1 \|\mathbf{A}\|_1$$

where $\mathbf{A}_{:,i}$ represents the $i$-th column of $\mathbf{A}$, acting as a soft mask over parent variables.

**Multi-Environment Identification**: Following recent identifiability results, we leverage data from multiple environments where mechanisms change independently. For environments $e \in \{1, ..., E\}$, we encourage shared causal structure but allow mechanism-specific parameters:
$$\mathcal{L}_{\text{multi}} = \sum_{e=1}^{E} \mathcal{L}_{\text{causal}}^{(e)} + \lambda_2 \sum_{e \neq e'} \|\mathbf{A}^{(e)} - \mathbf{A}^{(e')}\|_F^2$$

### 2.4 Modular Dynamics Phase

Once the causal structure is discovered, we factorize the SSM's state transition according to $\mathcal{G}$.

**Standard SSM Formulation**: A discrete SSM with hidden state $\mathbf{h}_t$ evolves as:
$$\mathbf{h}_{t+1} = \bar{\mathbf{A}} \mathbf{h}_t + \bar{\mathbf{B}} \mathbf{x}_t$$
$$\mathbf{y}_t = \mathbf{C} \mathbf{h}_t$$

**Causal Factorization**: We decompose the state transition matrix $\bar{\mathbf{A}}$ into modular components guided by the learned adjacency matrix:
$$\bar{\mathbf{A}}_{\text{causal}} = \mathbf{A}_{\text{graph}} \odot \bar{\mathbf{A}}_{\text{base}}$$

where $\mathbf{A}_{\text{graph}}$ is a binarized (or soft-thresholded) version of the learned causal adjacency matrix, enforcing that state dimension $i$ only depends on its causal parents.

**Independent Mechanism Networks**: For each state dimension $i$, we define a small neural network $f_{\theta_i}$ that computes the update based only on parent states:
$$z_{t+1}^{(i)} = f_{\theta_i}(\{z_t^{(j)} : A_{ji} > \tau\}, \mathbf{a}_t) + \epsilon_i$$

where $\tau$ is a sparsity threshold and $\epsilon_i \sim \mathcal{N}(0, \sigma_i^2)$ is independent noise.

### 2.5 Complete Training Objective

The full C-SSM training objective combines reconstruction, causal discovery, and regularization:

$$\mathcal{L}_{\text{total}} = \underbrace{\mathbb{E}[\|\mathbf{o}_t - \hat{\mathbf{o}}_t\|^2]}_{\text{reconstruction}} + \underbrace{\beta \cdot D_{KL}(q_\phi(\mathbf{z}_t | \mathbf{o}_t) \| p(\mathbf{z}_t))}_{\text{regularization}} + \underbrace{\gamma \cdot \mathcal{L}_{\text{causal}}}_{\text{causal structure}} + \underbrace{\mu \cdot h(\mathbf{A})^2}_{\text{acyclicity}}$$

Training proceeds in two alternating phases:
1. **Phase 1**: Fix dynamics, update causal structure (every $K$ steps)
2. **Phase 2**: Fix causal structure, update dynamics and encoder/decoder

### 2.6 Experimental Design

**Datasets and Benchmarks**:

1. **PHYRE** (Physical Reasoning): A benchmark requiring physical reasoning about object interactions. We evaluate on within-template (interpolation) and cross-template (compositional) generalization.

2. **CausalWorld**: A robotic manipulation benchmark with explicit causal factors. We test transfer across novel object shapes, sizes, and physical properties.

3. **dSprites-Physics**: We extend dSprites with physics simulation, creating sequences where objects with different visual properties interact under consistent physical laws.

4. **Shapes3D-Dynamics**: A novel benchmark we construct by adding temporal dynamics to Shapes3D, enabling controlled evaluation of compositional generalization.

**Baselines**:

- **Standard SSM** (Mamba, S4): Without causal structure
- **DreamerV3**: State-of-the-art model-based RL world model
- **SlotSSM**: Object-centric SSM without explicit causality
- **CITRIS**: Causal representation learning without SSM backbone
- **CausalVAE**: Causal discovery in static settings

**Evaluation Metrics**:

1. **Prediction Accuracy**: MSE and LPIPS for future frame prediction
2. **Compositional Generalization Score (CGS)**: 
$$\text{CGS} = \frac{\text{Accuracy}_{\text{novel combinations}}}{\text{Accuracy}_{\text{seen combinations}}}$$

3. **Causal Discovery Metrics**: Structural Hamming Distance (SHD) and Area Under ROC Curve (AUROC) against ground-truth graphs (where available)

4. **Disentanglement Scores**: DCI, MIG, and SAP scores measuring alignment with true factors

5. **Zero-shot Transfer Performance**: Accuracy on entirely new environments sharing causal mechanisms

**Implementation Details**:

- Latent dimension $d = 64$ with 8-16 discovered causal factors
- Mamba backbone with hidden dimension 256
- Training: Adam optimizer, learning rate $3 \times 10^{-4}$, batch size 64
- Hyperparameters: $\beta = 0.1$, $\gamma = 1.0$, $\mu = 10.0$ (annealed)
- Training epochs: 500 with early stopping on validation loss

## 3. Expected Outcomes & Impact

### Expected Results

1. **Improved Compositional Generalization**: We expect C-SSM to achieve CGS scores of 0.85-0.95 on PHYRE and CausalWorld, compared to 0.5-0.7 for standard SSMs and 0.6-0.8 for existing causal methods, demonstrating substantial improvement in handling novel concept combinations.

2. **Accurate Causal Discovery**: On benchmarks with known ground-truth structure, we anticipate SHD improvements of 30-50% over non-interventional baselines, validating that action-based interventions enable reliable causal identification.

3. **Interpretable Representations**: Qualitative analysis should reveal that learned latent dimensions correspond to interpretable physical quantities (position, velocity, mass, friction), with DCI scores exceeding 0.7.

4. **Sample Efficiency**: Learning modular mechanisms should reduce training data requirements by 40-60% for achieving comparable performance on downstream tasks.

### Broader Impact

**Scientific Contributions**:
- A novel theoretical framework connecting state-space models with causal representation learning
- Practical algorithms for discovering causal structure from sequential interventional data
- New benchmarks for evaluating compositional generalization in world models

**Applications**:
- **Robotics**: More robust manipulation policies that transfer across object types
- **Healthcare**: Medical simulators that correctly model independent physiological mechanisms
- **Scientific Discovery**: World models that discover modular causal laws from experimental data
- **Embodied AI**: Agents that generalize physical intuitions to novel scenarios

**Limitations and Future Work**:
This initial work assumes discrete actions as interventions; extending to continuous action spaces and partial observability remains future work. Additionally, scaling to very high-dimensional causal graphs (hundreds of variables) will require more efficient structure learning algorithms.

By bridging causality research with scalable sequence modeling, C-SSM represents a principled step toward world models that genuinely understand environment dynamics, enabling safer, more reliable AI systems capable of robust reasoning in our complex, compositional world.