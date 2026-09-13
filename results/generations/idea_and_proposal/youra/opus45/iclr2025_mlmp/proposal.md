# Research Proposal: RG-STFM: Renormalization Group-Structured Foundation Models for Cross-Domain Scale Transition Transfer

## 1. Introduction

### 1.1 Background

Multiscale modeling represents one of the most fundamental challenges in computational science. As Paul Dirac noted in 1929, while the underlying physical laws governing systems from atoms to climate are well-established through quantum mechanics and the Standard Model, the computational complexity of applying these laws to realistic systems remains prohibitive. A system of merely 100 atoms already exceeds the exact computational capabilities of modern supercomputers, yet practical scientific problems—from designing fusion reactors to predicting weather patterns—involve vastly larger scales spanning many orders of magnitude in both space and time.

The history of physics is punctuated by breakthrough solutions to scale transition problems: renormalization group theory, density functional theory, and multiscale climate models have each earned Nobel recognition precisely because they enabled tractable computation of previously intractable systems. However, these solutions remain largely domain-specific, requiring deep physical insight and years of development for each new application area.

Recent advances in machine learning have produced physics foundation models such as PhysiX (4.5B parameters) and GPhyT (trained on 1.8TB of simulation data) that achieve impressive results across multiple physical domains. These models learn scale transitions implicitly through massive data and parameters, demonstrating that neural networks can capture complex physical dynamics. However, they do so without leveraging the deep mathematical structure that governs how physics changes across scales—structure that physicists have spent decades uncovering.

Renormalization group (RG) theory provides precisely this mathematical framework. RG theory explains why vastly different physical systems—magnets, fluids, superconductors—exhibit identical scaling behavior near critical points. This phenomenon, known as universality, means that systems sharing the same "universality class" obey identical scaling laws regardless of their microscopic details. The Ising model of magnetism, the liquid-gas critical point, and certain superconducting transitions all belong to the same universality class and share identical critical exponents. This universality has never been systematically embedded into foundation model architectures, representing a critical gap between theoretical physics insights and modern AI capabilities.

### 1.2 Research Objectives

This research proposes RG-STFM (Renormalization Group-Structured Foundation Model), a novel architecture that embeds explicit RG flow structure as interpretable embeddings within a transformer-based foundation model. Our primary objectives are:

1. **Develop an RG Flow Encoder** that captures hierarchical scale structure through RG-aware positional encodings and produces domain-agnostic embeddings organized by universality class.

2. **Demonstrate zero-shot cross-domain transfer** by showing that systems sharing the same RG universality class cluster in embedding space, enabling transfer across physically distinct domains without fine-tuning.

3. **Achieve interpretable scale transitions** where the learned embeddings reveal which physical principles transfer across systems, with quantifiable predictions of critical exponents and universality class membership.

4. **Validate against state-of-the-art baselines** (PhysiX, GPhyT) on The Well benchmark, demonstrating competitive accuracy with superior interpretability and sample efficiency.

### 1.3 Significance

If successful, RG-STFM would bridge the gap between rigorous theoretical physics and modern AI, potentially unlocking principled scale transitions for fusion energy, climate modeling, and materials science. Unlike purely data-driven approaches, RG-STFM would provide interpretable insights into why transfer succeeds, enabling physicists to validate and trust model predictions. The 10x improvement in sample efficiency for new domains would dramatically reduce the computational cost of extending models to new physical systems, accelerating scientific discovery across multiple fields.

## 2. Methodology

### 2.1 Theoretical Foundation

The core hypothesis underlying RG-STFM is that systems sharing the same RG universality class will cluster in embedding space, enabling zero-shot transfer across physically distinct domains. This hypothesis rests on the mathematical structure of RG theory.

Near a critical point, physical observables follow scaling laws characterized by critical exponents. For a system with correlation length $\xi$ and reduced temperature $t = (T - T_c)/T_c$:

$$\xi \sim |t|^{-\nu}$$

where $\nu$ is a critical exponent determined solely by the universality class. Systems in the same universality class share identical values of $\nu$ and other critical exponents ($\alpha$, $\beta$, $\gamma$, $\delta$, $\eta$), regardless of microscopic details.

The RG transformation $\mathcal{R}$ acts on the space of Hamiltonians, coarse-graining microscopic degrees of freedom while preserving long-wavelength physics:

$$\mathcal{R}: H \rightarrow H' = \mathcal{R}(H)$$

Fixed points $H^*$ of this transformation ($\mathcal{R}(H^*) = H^*$) define universality classes, with the flow toward fixed points determining critical behavior.

### 2.2 Architecture Design

**RG Flow Encoder.** The encoder transforms input physical states into RG-structured embeddings through a modified transformer architecture. Given input state $\mathbf{x} \in \mathbb{R}^{N \times d}$ representing a physical system at $N$ spatial points with $d$ features:

$$\mathbf{z} = \text{RGEncoder}(\mathbf{x}) = \text{Transformer}(\mathbf{x} + \mathbf{P}_{RG})$$

where $\mathbf{P}_{RG}$ are RG-aware positional encodings that capture scale hierarchy:

$$\mathbf{P}_{RG}(i, s) = \sin\left(\frac{i}{10000^{2s/d_{model}}}\right) \cdot \log(L_s/L_0)$$

Here $s$ indexes the scale level, $L_s$ is the characteristic length at scale $s$, and $L_0$ is the microscopic cutoff. This encoding explicitly injects scale information into the attention mechanism.

**Scale-Aware Attention.** We modify the standard attention mechanism to respect scale hierarchy:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + \mathbf{M}_{scale}\right)V$$

where $\mathbf{M}_{scale}$ is a scale-coupling mask that encourages information flow from fine to coarse scales, mimicking the RG coarse-graining direction.

**Universality Class Embedding.** The final embedding $\mathbf{z} \in \mathbb{R}^{d_{emb}}$ (with $d_{emb} \in \{64, 128, 256\}$) is designed to cluster by universality class. We decompose:

$$\mathbf{z} = \mathbf{z}_{univ} + \mathbf{z}_{micro}$$

where $\mathbf{z}_{univ}$ captures universal (transferable) features and $\mathbf{z}_{micro}$ captures system-specific details.

### 2.3 Training Procedure

**Phase 1: Multi-Domain Pre-training.** We pre-train on diverse physical systems from PDEBench and The Well benchmark, spanning:
- Fluid dynamics (Navier-Stokes, turbulence)
- Phase transitions (Ising, XY models)
- Wave phenomena (acoustic, electromagnetic)
- Diffusion processes

The pre-training loss combines reconstruction and contrastive objectives:

$$\mathcal{L}_{pretrain} = \mathcal{L}_{recon} + \lambda_{cont}\mathcal{L}_{cont} + \lambda_{exp}\mathcal{L}_{exp}$$

**Reconstruction Loss:** Standard MSE for predicting future states:

$$\mathcal{L}_{recon} = \mathbb{E}\left[\|\hat{\mathbf{x}}_{t+\Delta t} - \mathbf{x}_{t+\Delta t}\|^2\right]$$

**Contrastive Loss:** Clusters embeddings by universality class using InfoNCE:

$$\mathcal{L}_{cont} = -\log\frac{\exp(\mathbf{z}_i \cdot \mathbf{z}_j^+ / \tau)}{\sum_{k}\exp(\mathbf{z}_i \cdot \mathbf{z}_k / \tau)}$$

where $\mathbf{z}_j^+$ is an embedding from the same universality class and $\tau$ is temperature.

**Critical Exponent Loss:** Supervises prediction of known critical exponents:

$$\mathcal{L}_{exp} = \sum_{\alpha \in \{\nu, \beta, \gamma, \eta\}} |\hat{\alpha} - \alpha_{true}|$$

**Phase 2: Universality-Guided Fine-tuning.** For new domains, we leverage universality class predictions to initialize from the nearest cluster centroid, enabling few-shot adaptation.

### 2.4 Data Collection and Preparation

**Training Data Sources:**
1. **PDEBench** (Takamoto et al., 2022): Standardized PDE datasets including Navier-Stokes, diffusion-reaction, and shallow water equations.
2. **The Well Benchmark** (2024): Comprehensive physics foundation model evaluation suite with 21 evaluation points across multiple domains.
3. **Synthetic RG Data:** Generated Ising model configurations at various temperatures and system sizes, with known universality class labels.

**Universality Class Labels:** We assign labels based on:
- Known physics (Ising → 3D Ising class, Navier-Stokes → directed percolation class near turbulent transition)
- Measured critical exponents from simulation
- Heuristic clustering for unlabeled systems

**Data Preprocessing:**
- Normalize to fixed scale separation ratio (100:1 fine-to-coarse)
- Augment with scale transformations preserving universality class
- Split: 70% train, 15% validation, 15% test (held-out domains)

### 2.5 Experimental Design

**Experiment 1: Zero-Shot Transfer Evaluation**

*Setup:* Train on 8 domains from The Well, evaluate zero-shot on 3 held-out domains.

*Metrics:*
- Volume-weighted RMSE (VRMSE): $\text{VRMSE} = \sqrt{\frac{1}{V}\sum_i v_i (y_i - \hat{y}_i)^2}$
- Relative improvement over PhysiX baseline

*Success Criterion:* VRMSE ≤ PhysiX baseline (paired t-test, $p < 0.05$, $n = 25$ runs)

**Experiment 2: Universality Class Prediction**

*Setup:* Evaluate embedding clustering quality and universality class prediction accuracy.

*Metrics:*
- Classification accuracy on held-out systems with known universality class
- Silhouette score for embedding clusters: $s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$

*Success Criterion:* Classification accuracy > 80%, silhouette score > 0.5

**Experiment 3: Critical Exponent Regression**

*Setup:* Predict critical exponents ($\nu$, $\beta$, $\gamma$, $\eta$) from embeddings.

*Metrics:*
- Mean Absolute Error (MAE) vs. known physics values
- Correlation with theoretical predictions

*Success Criterion:* MAE < 0.1 for all exponents

**Experiment 4: Sample Efficiency**

*Setup:* Compare learning curves on new domains.

*Metrics:*
- Number of samples to reach PhysiX performance
- Area under learning curve (AULC)

*Success Criterion:* 10x fewer samples than PhysiX

**Experiment 5: Ablation Studies**

*Components to ablate:*
- RG-aware positional encodings → standard sinusoidal
- Contrastive loss → reconstruction only
- Scale-aware attention → standard attention
- Critical exponent supervision → unsupervised

*Purpose:* Validate causal mechanism by showing each component contributes to performance.

### 2.6 Baseline Comparisons

| Model | Parameters | Training Data | Key Strength |
|-------|------------|---------------|--------------|
| PhysiX | 4.5B | The Well | SOTA accuracy |
| GPhyT | ~1B | 1.8TB custom | Generalization |
| FNO | ~50M | Domain-specific | Efficiency |
| RG-STFM (ours) | ~500M | PDEBench + The Well | Interpretability + Transfer |

### 2.7 Statistical Analysis

All experiments use:
- $n \geq 25$ independent runs with different random seeds
- Paired t-tests with Bonferroni correction ($\alpha = 0.017$ for 3 primary comparisons)
- Effect size reporting (Cohen's $d$, target $d \geq 0.6$)
- 95% confidence intervals for all metrics

**Falsification Criteria:**
1. VRMSE > PhysiX × 1.5 → reject accuracy hypothesis
2. Universality class accuracy < 50% → reject interpretability hypothesis
3. Critical exponent MAE > 0.5 → reject mechanism hypothesis
4. No advantage on any dimension → reject overall hypothesis

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcomes:**
1. **Competitive Accuracy:** RG-STFM achieving VRMSE ≤ PhysiX on The Well benchmark, demonstrating that explicit physics structure does not sacrifice predictive performance.

2. **Superior Interpretability:** >80% accuracy in universality class prediction, with embeddings that cluster meaningfully by physical principles rather than superficial features.

3. **Quantitative Physics Predictions:** Critical exponent regression with MAE < 0.1, providing physically meaningful outputs that can be validated against known theory.

4. **Enhanced Sample Efficiency:** 10x reduction in samples needed for new domains, dramatically reducing the cost of extending to new physical systems.

### 3.2 Scientific Impact

**Bridging Theory and AI:** RG-STFM would demonstrate that embedding rigorous physics principles into neural architectures provides measurable advantages over purely data-driven approaches. This validates the broader program of physics-informed machine learning and provides a template for incorporating other theoretical frameworks.

**Interpretable Scale Transitions:** Unlike black-box models, RG-STFM's embeddings reveal which physical principles transfer across systems. This interpretability is crucial for scientific applications where understanding why a prediction is made is as important as the prediction itself.

**Universality as Inductive Bias:** By demonstrating that universality class structure improves transfer learning, we establish a new paradigm for physics foundation models that leverages decades of theoretical physics insights.

### 3.3 Practical Applications

**Fusion Energy:** Scale transitions in plasma physics could benefit from RG-structured models, potentially accelerating the design of fusion reactors by enabling transfer from simplified models to realistic geometries.

**Climate Modeling:** Turbulent atmospheric dynamics exhibit scale-invariant behavior amenable to RG analysis. RG-STFM could enable more efficient climate simulations by learning transferable representations of turbulent cascades.

**Materials Science:** Phase transitions in materials (superconductivity, magnetism) are natural applications of RG theory. RG-STFM could accelerate materials discovery by transferring knowledge across material classes sharing universality.

### 3.4 Limitations and Future Work

**Scope Limitations:** RG-STFM is most applicable to near-critical systems with scale-invariant behavior. Far-from-equilibrium systems and those without clear scale separation may not benefit from RG structure.

**Future Directions:**
- Extension to non-equilibrium RG for driven systems
- Integration with symbolic regression for discovering new scaling laws
- Application to quantum many-body systems where RG is well-established

### 3.5 Broader Impact

If successful, RG-STFM represents a step toward the workshop's vision of "solving scale transition to solve science." By demonstrating that universal mathematical structures can be embedded in AI systems to enable principled cross-domain transfer, we open the door to AI systems that not only predict but explain physical phenomena across scales—a capability essential for tackling humanity's most pressing scientific challenges.