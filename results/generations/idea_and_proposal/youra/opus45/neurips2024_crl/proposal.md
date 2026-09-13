# Research Proposal: T-CausalVAE: Leveraging Temporal Consistency for Identifiable Causal Representation Learning in Video

## 1. Introduction

### 1.1 Background

Deep generative models have achieved remarkable success in learning rich representations from complex, high-dimensional data such as images, videos, and text. Models like Variational Autoencoders (VAEs), Generative Adversarial Networks (GANs), and diffusion models excel at capturing intricate statistical dependencies within data distributions. However, these models fundamentally learn correlational patterns rather than causal relationships, making them susceptible to spurious correlations and limiting their interpretability, robustness, and trustworthiness in critical applications.

Causal representation learning (CRL) has emerged as a promising paradigm to address these limitations by seeking to discover latent causal variables and their structural relationships from observational data. Unlike traditional representation learning that focuses on statistical sufficiency, CRL aims to recover representations that reflect the underlying data-generating process, enabling more robust generalization, interpretable reasoning, and principled counterfactual inference. Recent theoretical advances have established identifiability conditions under which latent causal variables can be uniquely recovered, typically requiring interventional data, auxiliary variables, or strong distributional assumptions such as non-Gaussianity.

Despite these advances, a significant gap remains between theoretical identifiability results and practical applicability. Most existing CRL methods require access to interventional data or explicit supervision signals that are rarely available in real-world scenarios. This limitation severely restricts the deployment of CRL techniques to controlled experimental settings, leaving vast amounts of observational data—particularly video data—underutilized for causal discovery.

Video data presents a unique and largely untapped opportunity for causal representation learning. Unlike static images, video sequences inherently encode temporal structure: consecutive frames capture the same underlying scene with shared latent causal variables evolving over time. This temporal structure provides natural multi-view observations of the latent space, where each frame serves as a different "view" of the same causal system. Crucially, the temporal ordering of frames introduces asymmetric constraints that could potentially substitute for interventional data in establishing causal directions—causes must precede their effects in time.

### 1.2 Research Objectives

This research proposes T-CausalVAE (Temporal-Causal Variational Autoencoder), a novel framework that exploits the temporal structure inherent in video data to achieve identifiable causal representation learning without requiring interventional data. Our primary objectives are:

1. **Develop a theoretically grounded framework** that leverages temporal consistency across consecutive video frames to identify shared latent causal structure, using temporal ordering as a natural source of causal direction information.

2. **Design and implement T-CausalVAE**, a variational autoencoder architecture that integrates temporal consistency constraints with differentiable DAG learning (NOTEARS-style) for explicit causal graph discovery from video data.

3. **Establish empirical validation** through comprehensive experiments on synthetic video benchmarks with known ground-truth causal structures, demonstrating significant improvements in causal structure recovery (measured by Structural Hamming Distance) and latent variable identification (measured by Mean Correlation Coefficient).

4. **Demonstrate practical applicability** through counterfactual video synthesis, showing that the learned causal representations enable meaningful interventional reasoning on video data.

### 1.3 Significance

This research addresses a fundamental challenge in causal representation learning: achieving identifiability from purely observational data without interventions. By demonstrating that temporal structure in video can substitute for interventional signals, T-CausalVAE would significantly expand the applicability of CRL methods to the vast domain of video data. The expected contributions include:

- **Theoretical contribution**: Establishing conditions under which temporal multi-view structure enables causal identifiability, bridging recent multi-view CRL theory with practical video applications.
- **Methodological contribution**: A novel VAE architecture combining temporal consistency constraints with differentiable causal discovery, providing both generative capabilities and explicit causal graph learning.
- **Practical contribution**: Enabling causal discovery and counterfactual reasoning on observational video data, with applications in robotics (understanding action-effect relationships), medical imaging (temporal disease progression), and autonomous systems (causal scene understanding).

## 2. Methodology

### 2.1 Problem Formulation

We consider video data as a sequence of frames $\{x_1, x_2, \ldots, x_T\}$ where each frame $x_t \in \mathbb{R}^{H \times W \times C}$ is a high-dimensional observation generated from a lower-dimensional latent causal system. We assume the following data-generating process:

$$x_t = g(z_t, \epsilon_t)$$

where $z_t \in \mathbb{R}^d$ represents the latent causal variables at time $t$, $g: \mathbb{R}^d \times \mathbb{R}^m \rightarrow \mathbb{R}^{H \times W \times C}$ is an injective mixing function, and $\epsilon_t$ represents independent observation noise.

The latent causal variables follow a structural causal model (SCM):

$$z_t^{(i)} = f_i(z_t^{\text{pa}(i)}, z_{t-1}^{\text{pa}_{\text{temp}}(i)}, u_t^{(i)})$$

where $\text{pa}(i)$ denotes the contemporaneous parents of variable $i$ within the same frame, $\text{pa}_{\text{temp}}(i)$ denotes temporal parents from the previous frame, and $u_t^{(i)}$ represents exogenous noise.

**Key Assumptions:**

1. **Shared Causal Skeleton**: The contemporaneous causal structure (DAG) $\mathcal{G}$ remains constant across consecutive frames.
2. **Independent Observation Noise**: $\epsilon_t \perp \epsilon_{t'}$ for $t \neq t'$.
3. **DAG Structure**: The contemporaneous causal graph $\mathcal{G}$ is a directed acyclic graph.
4. **Temporal Causal Direction**: Causal influence flows forward in time; $z_{t-1}$ can influence $z_t$ but not vice versa.

### 2.2 T-CausalVAE Architecture

T-CausalVAE processes pairs of consecutive frames $(x_t, x_{t+1})$ through a unified variational framework with three key components:

#### 2.2.1 Temporal Encoder

The encoder $q_\phi(z_t, z_{t+1} | x_t, x_{t+1})$ maps frame pairs to latent distributions. We use a shared convolutional backbone followed by frame-specific heads:

$$h_t = \text{CNN}_\phi(x_t), \quad h_{t+1} = \text{CNN}_\phi(x_{t+1})$$

$$\mu_t, \sigma_t = \text{MLP}_\phi^{(t)}([h_t; h_{t+1}]), \quad \mu_{t+1}, \sigma_{t+1} = \text{MLP}_\phi^{(t+1)}([h_t; h_{t+1}])$$

where $[;]$ denotes concatenation. The joint encoding allows information sharing between frames, enabling the model to leverage temporal consistency.

#### 2.2.2 Causal Layer with DAG Learning

Following the causal VAE paradigm, we introduce a causal layer that transforms independent exogenous variables $\hat{z}$ into causally structured latents $z$:

$$z = (I - A^\top)^{-1} \hat{z}$$

where $A \in \mathbb{R}^{d \times d}$ is the weighted adjacency matrix of the causal graph. To ensure $A$ represents a valid DAG, we incorporate the NOTEARS differentiable acyclicity constraint:

$$h(A) = \text{tr}(e^{A \circ A}) - d = 0$$

where $\circ$ denotes element-wise product. This constraint equals zero if and only if $A$ is acyclic.

#### 2.2.3 Temporal Consistency Module

To enforce shared causal structure across frames, we introduce a temporal consistency loss that penalizes deviations in the causal relationships:

$$\mathcal{L}_{\text{temp}} = \|z_{t+1} - (I - A^\top)^{-1} \cdot \text{MLP}_\psi(z_t)\|_2^2 + \lambda_{\text{smooth}} \|z_{t+1} - z_t\|_2^2$$

The first term ensures that the transition from $z_t$ to $z_{t+1}$ respects the learned causal structure, while the second term encourages smooth latent trajectories.

#### 2.2.4 Decoder

The decoder $p_\theta(x_t | z_t)$ reconstructs frames from latent variables using a transposed convolutional network:

$$\hat{x}_t = \text{DeconvNet}_\theta(z_t)$$

### 2.3 Training Objective

The complete training objective combines the standard VAE ELBO with causal structure learning and temporal consistency:

$$\mathcal{L} = \mathcal{L}_{\text{ELBO}} + \lambda_{\text{DAG}} \cdot h(A)^2 + \lambda_{\text{sparse}} \|A\|_1 + \lambda_{\text{temp}} \cdot \mathcal{L}_{\text{temp}}$$

where:

$$\mathcal{L}_{\text{ELBO}} = -\mathbb{E}_{q_\phi}[\log p_\theta(x_t | z_t) + \log p_\theta(x_{t+1} | z_{t+1})] + \text{KL}(q_\phi(z_t, z_{t+1} | x_t, x_{t+1}) \| p(z_t, z_{t+1}))$$

The hyperparameters $\lambda_{\text{DAG}}$, $\lambda_{\text{sparse}}$, and $\lambda_{\text{temp}}$ control the relative importance of acyclicity, sparsity, and temporal consistency respectively.

### 2.4 Experimental Design

#### 2.4.1 Datasets

**Synthetic Benchmarks (Primary Evaluation):**
- **Temporal Causal3DIdent**: We extend the Causal3DIdent benchmark to video by rendering sequences of 3D scenes with known latent causal structure (object position, rotation, color, lighting) evolving according to a predefined SCM.
- **MPI3D-Video**: Semi-synthetic video sequences derived from MPI3D with controlled causal relationships between factors.

**Real-World Data (Qualitative Evaluation):**
- **Something-Something V2**: Real videos of human-object interactions for qualitative assessment of learned representations.
- **Kinetics-400 subset**: Action recognition videos for generalization testing.

#### 2.4.2 Baselines

1. **Standard VAE**: Vanilla VAE without causal structure learning
2. **β-VAE**: Disentangled VAE with increased KL penalty
3. **CausalVAE** (Yang et al., 2021): Single-frame causal VAE with supervised labels
4. **iVAE** (Khemakhem et al., 2020): Identifiable VAE with auxiliary variables
5. **CITRIS** (Lippe et al., 2022): Causal identifiability from temporal sequences with interventions
6. **Multi-view CRL** (Yao et al., 2023): Contrastive learning approach for multi-view CRL

#### 2.4.3 Evaluation Metrics

**Causal Structure Recovery:**
- **Structural Hamming Distance (SHD)**: Number of edge additions, deletions, and reversals needed to transform the learned graph into the ground-truth graph.
- **Structural Intervention Distance (SID)**: Measures interventional distribution differences implied by graph discrepancies.

**Latent Variable Recovery:**
- **Mean Correlation Coefficient (MCC)**: Average absolute correlation between learned and true latent variables after optimal permutation matching.
- **R² Score**: Coefficient of determination for linear regression from learned to true latents.

**Generative Quality:**
- **Reconstruction FID**: Fréchet Inception Distance between original and reconstructed frames.
- **Counterfactual FID**: FID between generated counterfactual frames and ground-truth interventional outcomes.

#### 2.4.4 Experimental Protocol

**Experiment 1 (SH1 - Existence):** Evaluate whether T-CausalVAE achieves significantly lower SHD than single-frame baselines.
- Protocol: Train all models on Temporal Causal3DIdent with $d=10$ latent variables.
- Statistical test: Paired t-test with $\alpha = 0.05$ (one-tailed), $n \geq 25$ runs.
- Success criterion: SHD reduction $\geq 20\%$ vs. best baseline.

**Experiment 2 (SH2 - Mechanism):** Ablation study to verify the contribution of each component.
- Ablations: (a) Remove temporal consistency loss, (b) Remove DAG constraint, (c) Remove both.
- Analysis: Compare SHD and MCC across ablation conditions.

**Experiment 3 (SH3 - Comparison):** Compare with state-of-the-art multi-view CRL methods.
- Protocol: Evaluate on shared benchmarks with Yao et al. (2023).
- Additional metric: Assess generative capability (counterfactual synthesis) which contrastive methods lack.

**Experiment 4 (Scalability):** Test performance across varying latent dimensions ($d \in \{5, 10, 15, 20\}$) and temporal gaps (1-10 frames).

### 2.5 Implementation Details

- **Architecture**: ResNet-18 encoder backbone, 4-layer MLP for causal layer, symmetric decoder.
- **Optimization**: Adam optimizer with learning rate $10^{-4}$, batch size 32 frame pairs.
- **Hyperparameters**: $\lambda_{\text{DAG}} = 1.0$ (annealed), $\lambda_{\text{sparse}} = 0.1$, $\lambda_{\text{temp}} = 0.5$.
- **Training**: 100 epochs with early stopping based on validation ELBO.
- **Compute**: NVIDIA A100 GPUs, estimated 24-48 hours per full training run.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and the supporting theoretical foundations from multi-view CRL literature, we anticipate the following outcomes:

**Primary Outcome (P1):** T-CausalVAE will achieve SHD reduction of at least 20% compared to single-frame baselines on synthetic video benchmarks. We expect SHD values in the range of 3-5 (out of maximum $d^2 = 100$) compared to baseline SHD of 6-10.

**Secondary Outcomes:**
- **P2:** MCC exceeding 0.7 for latent variable recovery, demonstrating that temporal consistency enables identification of individual causal factors.
- **P3:** Counterfactual FID within 1.5× of reconstruction FID, indicating that learned causal structure supports meaningful interventional reasoning.

**Ablation Insights:** We expect the ablation study to reveal that both temporal consistency and DAG constraints are necessary—removing either component should significantly degrade performance, validating our proposed mechanism.

### 3.2 Potential Challenges and Mitigation

1. **Computational Cost**: The NOTEARS constraint involves matrix exponential computation. Mitigation: Use efficient approximations and GPU-accelerated implementations.

2. **Hyperparameter Sensitivity**: Multiple loss terms require careful balancing. Mitigation: Systematic hyperparameter search with validation-based selection.

3. **Ground-Truth Availability**: Real videos lack ground-truth causal graphs. Mitigation: Primary evaluation on synthetic data; qualitative assessment on real videos.

### 3.3 Broader Impact

**Scientific Impact:** This research bridges the gap between theoretical CRL identifiability results and practical video applications, demonstrating that temporal structure can substitute for interventional data. This opens new research directions in exploiting natural data structure for causal discovery.

**Practical Applications:**
- **Robotics**: Understanding causal relationships between actions and outcomes from demonstration videos.
- **Medical Imaging**: Discovering causal factors in disease progression from longitudinal imaging data.
- **Autonomous Systems**: Building causally-aware world models for robust decision-making.

**Limitations and Ethical Considerations:** The method assumes stable causal structure across frames, which may not hold in all scenarios. Applications in sensitive domains (medical, legal) require careful validation. The interpretability benefits should not be overstated—learned causal graphs require domain expert validation before deployment.

### 3.4 Future Directions

Success of T-CausalVAE would motivate several extensions:
1. Scaling to longer temporal dependencies and more complex causal structures.
2. Extension to multi-modal data (video + audio, video + text).
3. Integration with large-scale video foundation models for causal video understanding.
4. Theoretical analysis establishing formal identifiability guarantees under temporal consistency assumptions.

In conclusion, T-CausalVAE represents a principled approach to leveraging the natural temporal structure in video data for causal representation learning, with the potential to significantly advance both the theoretical understanding and practical applicability of CRL methods.