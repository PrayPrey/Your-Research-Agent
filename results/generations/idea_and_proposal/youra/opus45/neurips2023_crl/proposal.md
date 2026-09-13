# Research Proposal: Cross-Modal Causal Asymmetry for Identifiable Representation Learning (CMCA-IRL)

## 1. Introduction

### 1.1 Background

Modern machine learning systems have achieved remarkable performance across diverse tasks by leveraging large-scale models and datasets. However, these systems fundamentally rely on capturing statistical correlations, which limits their ability to perform tasks requiring higher-order cognition such as domain generalization, robustness to adversarial perturbations, and causal reasoning. This limitation has sparked significant interest in integrating causal inference principles into representation learning, giving rise to the emerging field of Causal Representation Learning (CRL).

Traditional causal inference methods assume that causal variables are predefined and directly observable. In contrast, real-world data typically consists of high-dimensional, low-level observations (e.g., RGB pixels, audio waveforms) that are not naturally structured into meaningful causal units. CRL addresses this gap by aiming to learn low-dimensional, high-level causal variables along with their causal relations directly from raw, unstructured data.

A central challenge in CRL is achieving **identifiability**—the guarantee that learned representations correspond to true underlying causal factors up to well-defined equivalence classes. Recent theoretical advances have established that identifiability can be achieved through various mechanisms, including temporal structure, explicit interventions, and multi-view observations. However, explicit interventional data is costly to obtain, and temporal structure is not always available.

Multi-modal learning has emerged as a promising direction, with recent work by Daunhawer et al. (2023) demonstrating that contrastive learning can achieve block-identification of latent factors shared between modalities with distinct generative mechanisms. However, existing approaches typically treat modalities symmetrically, overlooking a fundamental insight: different modalities often have **asymmetric causal relationships** to shared latent factors. For instance, in audio-visual data, visual observations may capture the causes of events while audio captures their effects; in text-image pairs, text may describe high-level semantic causes while images depict their visual manifestations.

### 1.2 Research Objectives

This research proposes **Cross-Modal Causal Asymmetry for Identifiable Representation Learning (CMCA-IRL)**, a novel framework that exploits the natural causal asymmetry between modalities to achieve block-wise identifiability without requiring explicit interventional data or temporal structure.

Our primary objectives are:

1. **Theoretical Foundation**: Establish formal conditions under which cross-modal causal asymmetry provides sufficient constraints for block-wise identifiability, analogous to soft interventions.

2. **Algorithmic Development**: Design modality-specific encoders that preserve and exploit asymmetric causal structure, enabling the recovery of shared latent causal variables.

3. **Empirical Validation**: Demonstrate the effectiveness of CMCA-IRL on both synthetic datasets with controlled causal graphs and real-world multi-modal datasets.

4. **Comparative Analysis**: Quantify the advantage of exploiting causal asymmetry over symmetric multi-view baselines.

### 1.3 Research Significance

This research addresses a fundamental gap in causal representation learning by providing a principled approach to achieve identifiability from naturally paired multi-modal data. The significance of this work is threefold:

**Theoretical Contribution**: We extend the theoretical understanding of identifiability conditions by formalizing how cross-modal causal asymmetry creates implicit constraints equivalent to soft interventions.

**Practical Impact**: By eliminating the need for costly interventional experiments, CMCA-IRL enables identifiable causal representations from abundant naturally paired multi-modal data (audio-visual, text-image, multi-sensor).

**Broader Applications**: Identifiable causal representations support robust generalization, interpretable AI systems, and principled reasoning about interventions and counterfactuals, with applications spanning healthcare, robotics, and scientific discovery.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathbf{Z} = (Z_1, \ldots, Z_d) \in \mathbb{R}^d$ denote the latent causal variables of interest, governed by a structural causal model (SCM) with directed acyclic graph (DAG) $\mathcal{G}$. We observe paired multi-modal data $(\mathbf{X}_A, \mathbf{X}_B)$ generated through modality-specific observation functions:

$$\mathbf{X}_A = g_A(\mathbf{Z}_A) + \boldsymbol{\epsilon}_A, \quad \mathbf{X}_B = g_B(\mathbf{Z}_B) + \boldsymbol{\epsilon}_B$$

where $\mathbf{Z}_A \subseteq \mathbf{Z}$ and $\mathbf{Z}_B \subseteq \mathbf{Z}$ are subsets of latent variables observed by each modality, with shared factors $\mathbf{Z}_S = \mathbf{Z}_A \cap \mathbf{Z}_B$ and modality-specific factors $\mathbf{Z}_A \setminus \mathbf{Z}_S$ and $\mathbf{Z}_B \setminus \mathbf{Z}_S$.

**Definition (Cross-Modal Causal Asymmetry)**: Modalities exhibit causal asymmetry if the subsets $\mathbf{Z}_A$ and $\mathbf{Z}_B$ have different causal roles with respect to the shared factors $\mathbf{Z}_S$. Specifically, if $\mathbf{Z}_A$ contains variables that are causal ancestors of variables in $\mathbf{Z}_B$ within the latent DAG $\mathcal{G}$.

**Asymmetry Score**: We quantify causal asymmetry as:

$$\text{Asymmetry}(\mathbf{Z}_A, \mathbf{Z}_B) = \frac{\text{rank}(\mathbf{J}_A \cap \mathbf{J}_B^c)}{\text{rank}(\mathbf{J}_A \cup \mathbf{J}_B)}$$

where $\mathbf{J}_A = \frac{\partial g_A}{\partial \mathbf{Z}}$ and $\mathbf{J}_B = \frac{\partial g_B}{\partial \mathbf{Z}}$ are the Jacobian matrices of the observation functions.

### 2.2 Theoretical Framework

**Core Hypothesis**: Under cross-modal causal asymmetry, the combined Jacobian constraints from both modalities satisfy the rank conditions required for block-wise identifiability.

**Theorem (Informal)**: Let $(\mathbf{X}_A, \mathbf{X}_B)$ be paired observations from modalities with asymmetric causal relationships to shared latents $\mathbf{Z}_S$. If:
1. Observation functions $g_A, g_B$ are smooth and injective on their respective domains
2. The asymmetry score exceeds a threshold $\tau > 0$
3. The combined Jacobian $[\mathbf{J}_A; \mathbf{J}_B]$ has full column rank on $\mathbf{Z}_S$

Then the shared latent factors $\mathbf{Z}_S$ are block-wise identifiable up to smooth bijection.

The key insight is that asymmetric observation functions create complementary constraints: modality A provides information about "cause" variables while modality B provides information about "effect" variables. Together, these constraints break the symmetries that prevent identification in single-modality settings.

### 2.3 Model Architecture

The CMCA-IRL framework consists of three main components:

**Modality-Specific Encoders**: For each modality $m \in \{A, B\}$, we define an encoder $f_m: \mathcal{X}_m \rightarrow \mathbb{R}^{d_m}$ that maps observations to latent representations:

$$\hat{\mathbf{Z}}_m = f_m(\mathbf{X}_m; \theta_m)$$

The encoders are parameterized as deep neural networks (CNNs for images, transformers for audio/text) with architecture chosen based on modality characteristics.

**Shared Latent Alignment Module**: To identify shared factors, we introduce a cross-modal alignment mechanism:

$$\hat{\mathbf{Z}}_S^A = \Pi_A(\hat{\mathbf{Z}}_A), \quad \hat{\mathbf{Z}}_S^B = \Pi_B(\hat{\mathbf{Z}}_B)$$

where $\Pi_A, \Pi_B$ are learnable projection matrices that extract the shared latent subspace from each modality's representation.

**Causal Structure Preservation Module**: To preserve asymmetric causal structure, we incorporate a structural constraint:

$$\mathcal{L}_{\text{struct}} = \|\mathbf{A} - \text{DAG}(\hat{\mathbf{Z}}_S)\|_F^2 + \lambda_{\text{acyclic}} h(\mathbf{A})$$

where $\mathbf{A}$ is a learnable adjacency matrix, $\text{DAG}(\cdot)$ extracts causal structure from learned representations, and $h(\mathbf{A}) = \text{tr}(e^{\mathbf{A} \circ \mathbf{A}}) - d$ is the acyclicity constraint from NOTEARS.

### 2.4 Training Objective

The complete training objective combines four loss terms:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{align}} + \alpha \mathcal{L}_{\text{recon}} + \beta \mathcal{L}_{\text{struct}} + \gamma \mathcal{L}_{\text{asym}}$$

**Cross-Modal Alignment Loss**: Encourages shared factors to be consistent across modalities:

$$\mathcal{L}_{\text{align}} = -\frac{1}{N}\sum_{i=1}^{N} \log \frac{\exp(\text{sim}(\hat{\mathbf{Z}}_S^{A,i}, \hat{\mathbf{Z}}_S^{B,i})/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\hat{\mathbf{Z}}_S^{A,i}, \hat{\mathbf{Z}}_S^{B,j})/\tau)}$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity and $\tau$ is a temperature parameter.

**Reconstruction Loss**: Ensures representations retain sufficient information:

$$\mathcal{L}_{\text{recon}} = \sum_{m \in \{A,B\}} \|\mathbf{X}_m - \hat{g}_m(\hat{\mathbf{Z}}_m)\|_2^2$$

where $\hat{g}_m$ are decoder networks.

**Asymmetry Regularization Loss**: Encourages modality-specific encoders to capture different aspects of shared latents:

$$\mathcal{L}_{\text{asym}} = -\text{KL}(p(\hat{\mathbf{Z}}_S^A | \mathbf{X}_A) \| p(\hat{\mathbf{Z}}_S^B | \mathbf{X}_B))$$

This term penalizes identical posterior distributions, encouraging complementary information extraction.

### 2.5 Algorithmic Procedure

**Algorithm: CMCA-IRL Training**

```
Input: Paired multi-modal dataset D = {(X_A^i, X_B^i)}_{i=1}^N
Output: Trained encoders f_A, f_B; shared latent representations Z_S

1. Initialize encoders f_A, f_B, decoders g_A, g_B, projections Π_A, Π_B
2. Initialize adjacency matrix A for causal structure
3. For epoch = 1 to max_epochs:
   4. For each mini-batch {(X_A, X_B)} from D:
      5. Encode: Z_A = f_A(X_A), Z_B = f_B(X_B)
      6. Project to shared space: Z_S^A = Π_A(Z_A), Z_S^B = Π_B(Z_B)
      7. Compute alignment loss L_align (contrastive)
      8. Reconstruct: X_A_hat = g_A(Z_A), X_B_hat = g_B(Z_B)
      9. Compute reconstruction loss L_recon
      10. Update causal structure estimate from Z_S
      11. Compute structural loss L_struct with acyclicity constraint
      12. Compute asymmetry loss L_asym
      13. Total loss: L = L_align + α*L_recon + β*L_struct + γ*L_asym
      14. Update parameters via gradient descent
   15. End For
16. End For
17. Return f_A, f_B, Z_S
```

### 2.6 Experimental Design

#### 2.6.1 Synthetic Data Experiments

**Data Generation**: We generate synthetic datasets with controlled causal structure:

1. Sample latent DAG $\mathcal{G}$ with $d = 10$ to $50$ nodes and 2-5 edges per node
2. Generate latent variables $\mathbf{Z}$ following the SCM with linear-Gaussian or nonlinear mechanisms
3. Define asymmetric observation functions:
   - $g_A$: observes "cause" variables (ancestors in $\mathcal{G}$)
   - $g_B$: observes "effect" variables (descendants in $\mathcal{G}$)
4. Generate observations with additive Gaussian noise

**Controlled Variables**:
- Latent dimensionality: $d \in \{10, 20, 30, 50\}$
- Asymmetry degree: varied from 0.0 (symmetric) to 1.0 (fully asymmetric)
- Sample size: $N \in \{1000, 5000, 10000, 50000\}$
- Noise level: $\sigma \in \{0.1, 0.5, 1.0\}$

#### 2.6.2 Real-World Data Experiments

**Datasets**:
1. **AudioSet** (audio-visual): 2M+ video clips with audio, natural causal asymmetry (visual causes → audio effects)
2. **HowTo100M** (instructional videos): 136M video clips with narration, text describes causes while video shows effects
3. **MIMIC-CXR** (medical imaging): chest X-rays with radiology reports, imaging captures physical state while text describes clinical interpretation

#### 2.6.3 Baselines

1. **Symmetric Multi-View ICA**: Standard multi-view approach treating modalities identically
2. **Contrastive Multi-Modal Learning** (Daunhawer et al., 2023): Block-identification without explicit asymmetry modeling
3. **Partial Observability CRL** (Yao et al., 2023): Assumes known observation masks
4. **Single-Modality VAE**: Ablation baseline using only one modality

#### 2.6.4 Evaluation Metrics

**Primary Metric - Mean Correlation Coefficient (MCC)**:

$$\text{MCC} = \frac{1}{d_S} \sum_{i=1}^{d_S} \max_j |\text{corr}(\hat{Z}_{S,i}, Z_{S,j})|$$

computed after optimal permutation matching between learned and ground-truth latents.

**Secondary Metrics**:
- **Structural Hamming Distance (SHD)**: Number of edge additions, deletions, and reversals to transform recovered DAG to ground truth
- **Downstream Task Performance**: Classification/regression accuracy using learned representations
- **Disentanglement Metrics**: DCI disentanglement score, Mutual Information Gap (MIG)

#### 2.6.5 Statistical Analysis

- **Sample Size**: $n \geq 20$ random seeds per configuration
- **Statistical Tests**: One-sample t-test for MCC > 0.85 threshold; paired t-test for baseline comparisons
- **Significance Level**: $\alpha = 0.05$
- **Effect Size**: Cohen's d with 95% confidence intervals
- **Multiple Comparison Correction**: Bonferroni correction for multiple baselines

### 2.7 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

1. **Asymmetry Ablation**: Replace asymmetric observation functions with symmetric ones; expect performance degradation
2. **Shared Factor Ablation**: Vary the proportion of shared vs. modality-specific factors
3. **Causal Structure Ablation**: Remove structural constraint $\mathcal{L}_{\text{struct}}$; assess impact on causal graph recovery
4. **Modality Ablation**: Train with single modality; confirm multi-modal advantage

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1)**: CMCA-IRL will achieve block-wise identifiability with MCC > 0.85 on synthetic datasets with known ground-truth latents and controlled causal asymmetry. Based on prior work achieving MCC ~0.9 for multi-modal contrastive learning with independent latents, we expect comparable or improved performance due to additional structural constraints from causal dependencies.

**Secondary Prediction (P2)**: CMCA-IRL will outperform symmetric multi-view baselines by at least 10% relative improvement in MCC, demonstrating the value of explicitly modeling causal asymmetry.

**Secondary Prediction (P3)**: The learned representations will preserve causal structure with SHD ≤ 3 edges compared to ground-truth causal graphs, enabling valid causal reasoning.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. MCC ≤ 0.70 on synthetic data with known causal asymmetry
2. No significant difference between CMCA-IRL and symmetric baseline (p > 0.10)
3. Ablating causal asymmetry does not degrade performance

### 3.3 Scientific Impact

This research will advance the theoretical foundations of causal representation learning by:

1. **Extending Identifiability Theory**: Formalizing conditions under which cross-modal causal asymmetry enables identification, complementing existing results on interventions and temporal structure

2. **Bridging Multi-Modal and Causal Learning**: Providing a principled framework connecting multi-modal representation learning with causal inference

3. **Enabling New Research Directions**: Opening avenues for exploiting natural causal structure in diverse multi-modal settings

### 3.4 Practical Impact

**Healthcare Applications**: Learning identifiable causal representations from multi-modal medical data (imaging + clinical notes + lab results) can support interpretable diagnosis and treatment planning.

**Robotics**: Multi-sensor robotic systems can leverage causal asymmetry between sensors (e.g., cameras capturing causes, force sensors capturing effects) for robust state estimation.

**Scientific Discovery**: Automated discovery of causal relationships from multi-modal scientific data (e.g., microscopy + spectroscopy) can accelerate hypothesis generation.

### 3.5 Limitations and Future Work

**Limitations**:
- Block-wise identifiability is weaker than component-wise identifiability
- Causal asymmetry assumption may not hold universally
- Computational cost scales with modalities and latent dimensions

**Future Directions**:
- Extension to more than two modalities with complex causal relationships
- Integration with active learning for targeted data collection
- Application to temporal multi-modal data with dynamic causal structure
- Development of practical diagnostics for assessing causal asymmetry in real data

### 3.6 Timeline

- **Months 1-3**: Theoretical development and proof of identifiability conditions
- **Months 4-6**: Implementation and synthetic data experiments
- **Months 7-9**: Real-world dataset experiments and ablation studies
- **Months 10-12**: Analysis, paper writing, and dissemination

This research will contribute a novel perspective on achieving identifiable causal representations by exploiting the natural causal asymmetry present in multi-modal data, advancing both the theoretical foundations and practical applications of causal representation learning.