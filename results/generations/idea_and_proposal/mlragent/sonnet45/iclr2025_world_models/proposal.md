# Research Proposal: Causal Disentanglement in World Models via Interventional Self-Supervised Learning

## 1. Title

**Causally Disentangled World Models through Self-Supervised Interventional Learning: Bridging Pattern Recognition and Causal Reasoning for Robust Prediction and Planning**

## 2. Introduction

### 2.1 Background

World models have emerged as a foundational paradigm for enabling intelligent agents to understand, predict, and interact with complex environments. Initially conceptualized for modeling low-level physical interactions through recurrent neural networks, world models have evolved to encompass sophisticated applications including video generation (e.g., Sora, Genie), robotics, and embodied AI. Despite remarkable advances in pattern recognition and predictive accuracy, contemporary world models predominantly capture statistical correlations rather than underlying causal mechanisms. This fundamental limitation severely restricts their ability to generalize to out-of-distribution (OOD) scenarios, perform counterfactual reasoning, and provide interpretable explanations—capabilities essential for high-stakes domains such as healthcare, autonomous systems, and scientific discovery.

The challenge of learning causal representations from observational data has been extensively studied in causal inference and representation learning communities. Traditional approaches require expensive labeled intervention data or strong assumptions about the data-generating process. Recent work on causal disentanglement (e.g., SCADI, DCVAE, ICM-VAE) has demonstrated promising directions for discovering latent causal factors, but these methods either rely on supervised labels or struggle with identifiability guarantees. Furthermore, the integration of causal reasoning into large-scale world models for sequential decision-making and environment simulation remains largely unexplored.

### 2.2 Research Objectives

This research proposes a novel framework for learning causally disentangled world models through self-supervised interventional learning. Our specific objectives are:

1. **Develop an automated intervention generation mechanism** that identifies and perturbs potential causal variables in observational data without human annotation, enabling scalable causal discovery.

2. **Design a causal consistency learning framework** that enforces structural constraints derived from causal graph theory while maintaining compatibility with modern world model architectures (Transformers, SSMs).

3. **Establish multi-scale temporal verification mechanisms** to distinguish genuine causal relationships from spurious correlations across different prediction horizons.

4. **Validate the framework's effectiveness** on distribution shifts, counterfactual prediction, and interpretability metrics across diverse domains including robotics control, healthcare prediction, and physical simulation.

### 2.3 Significance

This research addresses critical gaps at the intersection of world modeling and causal representation learning:

- **Theoretical Contribution**: Provides a principled framework for identifiable causal disentanglement in sequential settings without paired intervention-observation data, extending existing theoretical guarantees to temporal domains.

- **Practical Impact**: Enables world models to make reliable predictions under novel conditions and interventions, crucial for safe deployment in robotics, medical decision support, and autonomous systems where understanding causality is paramount.

- **Methodological Innovation**: Introduces self-supervised techniques for causal discovery that scale to high-dimensional observations (images, videos) while maintaining interpretability through learned causal structures.

- **Broad Applicability**: The framework is designed to be architecture-agnostic and applicable across diverse domains highlighted in the workshop scope, from embodied AI to scientific modeling.

## 3. Methodology

### 3.1 Problem Formulation

We formulate the causally disentangled world model learning problem in a partially observable Markov decision process (POMDP) setting. Let $\mathcal{O}_t$ denote high-dimensional observations (e.g., images) at time $t$, $\mathcal{A}_t$ denote actions, and $\mathbf{z}_t \in \mathbb{R}^d$ represent the latent causal factors. We assume observations are generated from a structural causal model (SCM):

$$\mathbf{z}_t = f(\mathbf{z}_{t-1}, \mathbf{a}_{t-1}, \boldsymbol{\epsilon}_t)$$

$$\mathcal{O}_t = g(\mathbf{z}_t, \boldsymbol{\eta}_t)$$

where $f$ represents causal transition dynamics, $g$ is the observation function, and $\boldsymbol{\epsilon}_t, \boldsymbol{\eta}_t$ are exogenous noise variables. Each component $z_t^i$ should correspond to a distinct causal factor, and the causal graph structure $\mathcal{G}$ encodes dependencies among these factors.

**Objective**: Learn an encoder $E: \mathcal{O}_t \rightarrow \mathbf{z}_t$, a transition model $T: \mathbf{z}_t \times \mathbf{a}_t \rightarrow \mathbf{z}_{t+1}$, and a decoder $D: \mathbf{z}_t \rightarrow \hat{\mathcal{O}}_t$ such that:
1. Latent factors are causally disentangled (satisfy independence of mechanisms)
2. The model supports accurate counterfactual predictions
3. The learned representations generalize to distribution shifts

### 3.2 Automated Intervention Generation

#### 3.2.1 Causal Variable Identification

We employ a multi-head attention mechanism to identify potential causal variables from observations. Define an attention-based saliency map:

$$S_t = \text{Softmax}\left(\frac{Q_t K_t^T}{\sqrt{d_k}}\right) V_t$$

where $Q_t, K_t, V_t$ are queries, keys, and values derived from encoded observations. We then cluster attention patterns across temporal windows to identify candidate causal variables:

$$C_t = \text{Cluster}(\{S_{t-\tau:t}\}_{\tau=1}^{T_{\text{window}}}, k)$$

where $k$ is the number of hypothesized causal factors.

#### 3.2.2 Learnable Intervention Operators

For each identified cluster $c \in C_t$, we define a learnable intervention operator $\mathcal{I}_{\theta_c}$ that applies soft interventions:

$$\tilde{\mathbf{z}}_t^c = \mathbf{z}_t \odot (1 - m_c) + \mathcal{I}_{\theta_c}(\mathbf{z}_t) \odot m_c$$

where $m_c \in \{0,1\}^d$ is a binary mask indicating which latent dimensions are intervened upon, and $\odot$ denotes element-wise multiplication. The intervention function is parameterized as:

$$\mathcal{I}_{\theta_c}(\mathbf{z}_t) = \mu_c + \sigma_c \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

where $\mu_c, \sigma_c$ are learned parameters representing the intervention distribution for causal factor $c$.

### 3.3 Causal Consistency Loss Framework

#### 3.3.1 Structural Causal Model Penalty

We enforce consistency with causal graph constraints through a sparsity-inducing regularizer on the learned transition dynamics. Define the adjacency matrix $A \in \{0,1\}^{d \times d}$ where $A_{ij} = 1$ indicates a causal edge from $z_j$ to $z_i$. The transition model is factorized as:

$$T(\mathbf{z}_t, \mathbf{a}_t)_i = h_{\theta_i}(\{\mathbf{z}_t^j : A_{ij}=1\}, \mathbf{a}_t)$$

We learn $A$ jointly with the transition parameters using a continuous relaxation:

$$\mathcal{L}_{\text{DAG}} = \text{tr}(e^{W \odot W}) - d$$

where $W \in \mathbb{R}^{d \times d}$ is a continuous adjacency weight matrix, and the constraint enforces acyclicity (DAG structure).

#### 3.3.2 Interventional Consistency Loss

Under intervention on factor $c$, only descendants in the causal graph should change. We formalize this through an interventional prediction loss:

$$\mathcal{L}_{\text{int}} = \mathbb{E}_{c \sim \text{Uniform}(C)} \left[ \left\| T(\tilde{\mathbf{z}}_t^c, \mathbf{a}_t) - \text{do}(T(\mathbf{z}_t, \mathbf{a}_t), c) \right\|_2^2 \right]$$

where $\text{do}(T(\mathbf{z}_t, \mathbf{a}_t), c)$ represents the prediction under the intervention, computed by:

$$\text{do}(T(\mathbf{z}_t, \mathbf{a}_t), c)_i = \begin{cases} 
\mathcal{I}_{\theta_c}(\mathbf{z}_t)_i & \text{if } i = c \\
h_{\theta_i}(\mathbf{z}_t^{\text{pa}(i)}, \mathbf{a}_t) & \text{if } i \in \text{desc}(c) \\
\mathbf{z}_{t+1}^i & \text{otherwise}
\end{cases}$$

#### 3.3.3 Contrastive Causal Learning

To enhance disentanglement, we employ a contrastive loss that encourages interventions on different causal factors to produce distinguishable predictions:

$$\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(\tilde{\mathbf{z}}_{t+1}^c, \mathbf{z}_{t+1}^{c,\text{true}})/\tau)}{\sum_{c'} \exp(\text{sim}(\tilde{\mathbf{z}}_{t+1}^c, \mathbf{z}_{t+1}^{c'})/\tau)}$$

where $\text{sim}(\cdot, \cdot)$ is cosine similarity and $\tau$ is a temperature parameter.

### 3.4 Multi-Scale Temporal Verification

To distinguish correlation from causation, we validate causal relationships across multiple prediction horizons:

$$\mathcal{L}_{\text{temporal}} = \sum_{h=1}^{H} \lambda_h \left\| \mathbf{z}_{t+h}^{\text{pred}} - \mathbf{z}_{t+h}^{\text{true}} \right\|_2^2$$

where $\mathbf{z}_{t+h}^{\text{pred}} = T^h(\mathbf{z}_t, \{\mathbf{a}_{t:t+h-1}\})$ is the $h$-step rollout prediction, and $\lambda_h$ weights different horizons. Spurious correlations typically fail to maintain consistency at longer horizons.

Additionally, we introduce a temporal causal discovery module that identifies time-lagged causal relationships:

$$\mathcal{L}_{\text{lag}} = \mathbb{E}_{k \sim [1, K]} \left[ D_{KL}\left( p(\mathbf{z}_{t+k}|\text{do}(\mathbf{z}_t^c)) \| p(\mathbf{z}_{t+k}|\mathbf{z}_t) \right) \right]$$

This quantifies how interventions propagate through time, revealing causal time scales.

### 3.5 Overall Training Objective

The complete training objective combines reconstruction, causal structure learning, and disentanglement:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{recon}} + \alpha \mathcal{L}_{\text{DAG}} + \beta \mathcal{L}_{\text{int}} + \gamma \mathcal{L}_{\text{contrast}} + \delta \mathcal{L}_{\text{temporal}} + \eta \mathcal{L}_{\text{lag}}$$

where:
- $\mathcal{L}_{\text{recon}} = \mathbb{E}[\|\mathcal{O}_t - D(E(\mathcal{O}_t))\|_2^2]$ is the reconstruction loss
- $\alpha, \beta, \gamma, \delta, \eta$ are hyperparameters balancing different objectives

### 3.6 Architecture Design

We implement the framework using a hybrid architecture:

1. **Encoder**: Vision Transformer (ViT) or convolutional backbone for $E$
2. **Latent Dynamics**: Either Transformer with causal masking or State-Space Model (S4/Mamba) for $T$
3. **Decoder**: Transposed convolutions or diffusion-based generator for $D$
4. **Causal Graph Learner**: Neural relational inference module with Gumbel-Softmax for discrete structure learning

### 3.7 Experimental Design

#### 3.7.1 Datasets

**Synthetic Environments**:
- **Causal3DIdent**: 3D scenes with known causal factors (position, color, shape, lighting)
- **CausalWorld**: Robotic manipulation with known causal structure

**Real-World Benchmarks**:
- **CLEVRER**: Video prediction with causal reasoning questions
- **RoboNet**: Real robot interaction dataset for visuomotor control
- **MIMIC-III**: Healthcare trajectories for treatment effect estimation

#### 3.7.2 Baselines

We compare against:
- Standard world models: DreamerV3, IRIS, TWM
- Causal representation methods: SCADI, DCVAE, ICM-VAE
- Disentanglement baselines: β-VAE, Factor-VAE

#### 3.7.3 Evaluation Metrics

**Disentanglement Quality**:
- **MIG (Mutual Information Gap)**: Measures mutual information between latent codes and ground-truth factors
- **SAP Score**: Assesses whether each latent dimension captures a single generative factor
- **DCI Disentanglement**: Evaluates disentanglement, completeness, and informativeness

**Causal Discovery Accuracy**:
- **SHD (Structural Hamming Distance)**: Distance between learned and true causal graphs
- **SID (Structural Intervention Distance)**: Measures difference in interventional distributions

**Prediction Performance**:
- **RMSE** on multi-step predictions under natural rollouts
- **Counterfactual accuracy**: Error on counterfactual queries with known interventions
- **OOD Generalization**: Performance on held-out environments with distribution shifts

**Interpretability**:
- **Causal mechanism alignment**: Correlation between learned factors and domain-specific causal variables (where available)
- **Human evaluation**: For qualitative assessment of learned causal explanations

#### 3.7.4 Ablation Studies

We conduct systematic ablations to assess:
1. Impact of each loss component ($\mathcal{L}_{\text{DAG}}, \mathcal{L}_{\text{int}}, \mathcal{L}_{\text{contrast}}, \mathcal{L}_{\text{temporal}}$)
2. Effect of intervention operator design (hard vs. soft interventions)
3. Sensitivity to number of causal factors $k$
4. Architecture choices (Transformer vs. SSM for dynamics)
5. Multi-scale temporal verification horizons

#### 3.7.5 Experimental Protocol

**Training**: 
- Use Adam optimizer with learning rate $10^{-4}$
- Train for 500K environment steps with batch size 64
- Anneal causal loss weights over first 100K steps
- Apply curriculum learning: start with short horizons, gradually increase

**Evaluation**:
- Report metrics on test sets with 3 random seeds
- Conduct intervention experiments: apply known perturbations, measure prediction accuracy
- Test zero-shot transfer to new environments with shifted distributions
- Visualize learned causal graphs and latent traversals

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Theoretical Contributions**:
1. **Identifiability Guarantees**: We expect to establish sufficient conditions under which our self-supervised interventional framework provably recovers ground-truth causal structures, extending existing identifiability results to temporal settings.

2. **Sample Complexity Analysis**: Characterization of how many diverse observational sequences are required for accurate causal discovery as a function of causal graph complexity and observation dimensionality.

**Empirical Results**:
1. **Superior Disentanglement**: Anticipated 15-25% improvement in MIG and SAP scores compared to β-VAE baselines on synthetic benchmarks, approaching supervised methods like DCVAE without requiring intervention labels.

2. **Enhanced OOD Generalization**: Expected 30-40% reduction in prediction error on distribution shift scenarios (e.g., novel object combinations, lighting changes) compared to standard world models.

3. **Counterfactual Accuracy**: Predicted 50-60% improvement in answering counterfactual queries on CLEVRER compared to correlation-based baselines.

4. **Interpretable Causal Graphs**: Learned graph structures that achieve SHD < 5 on synthetic benchmarks with known ground truth, and qualitatively meaningful structures on real-world domains validated by domain experts.

**Practical Capabilities**:
1. **Safe Robotic Control**: Demonstration of a robotic manipulation system that can predict intervention outcomes (e.g., "what happens if I push object A instead of B?") with 80%+ accuracy, enabling safer exploration strategies.

2. **Medical Decision Support**: A healthcare prediction model that provides causal explanations for treatment recommendations with interpretability validated by clinicians.

3. **Scientific Discovery**: Application to physics simulation data showing the framework can rediscover known physical laws (gravity, friction) from observations.

### 4.2 Broader Impact

**For the Research Community**:
- **New Research Direction**: Establishes causal disentanglement as a fundamental capability for world models, inspiring follow-up work on causal planning, hierarchical causal structures, and multi-agent causal reasoning.
- **Open-Source Toolkit**: We will release a comprehensive library implementing our framework with multiple architecture backends, facilitating reproducibility and adoption.
- **Benchmark Contribution**: Introduction of new evaluation protocols for assessing causal reasoning in world models, addressing gaps in current benchmarks.

**For Applications**:
- **Embodied AI & Robotics**: Enables robots to understand "why" actions lead to outcomes, facilitating better transfer learning, safer exploration, and human-interpretable behavior.
- **Healthcare**: Provides clinicians with causal explanations for AI-recommended treatments, addressing the black-box problem in medical AI and supporting personalized medicine.
- **Scientific Modeling**: Accelerates discovery in physics, chemistry, and biology by automatically identifying causal mechanisms from experimental data, reducing hypothesis space for scientists.
- **Autonomous Systems**: Improves safety-critical decision-making in self-driving vehicles and drones by enabling reasoning about "what would happen if..." scenarios.

**Societal Considerations**:
- **Trustworthy AI**: By providing causal explanations, the framework addresses interpretability and accountability challenges crucial for AI governance and regulation.
- **Bias Mitigation**: Causal understanding helps identify and intervene on spurious correlations that may encode societal biases, supporting fairness in AI systems.
- **Potential Risks**: We acknowledge that improved world models could be misused for deceptive simulations or manipulation. We commit to responsible disclosure and will engage with AI safety communities.

**Alignment with Workshop Themes**:
This research directly addresses multiple workshop challenges:
1. **Understanding World Rules**: Through explicit causal graph learning and mechanism discovery
2. **Training & Evaluation**: Via novel self-supervised objectives and comprehensive metrics
3. **Scaling Across Modalities**: Architecture-agnostic design compatible with vision, language, and control
4. **General Domain Applications**: Validated across robotics, healthcare, and scientific domains

In conclusion, this research bridges the gap between statistical world models and causal reasoning, providing a principled framework for building intelligent systems that not only predict the future but understand why events occur. The self-supervised interventional learning paradigm offers a scalable path toward causally-aware AI systems essential for safe, interpretable, and robust real-world deployment.