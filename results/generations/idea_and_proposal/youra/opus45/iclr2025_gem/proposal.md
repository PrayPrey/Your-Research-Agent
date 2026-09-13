# Research Proposal: SE(3)-Equivariant Feedback Adapters for Sample-Efficient Protein Design

## 1. Title

**SE(3)-Equivariant Feedback Adapters for Sample-Efficient Protein Design: Bridging Computational Generation and Experimental Validation Through Geometric-Preserving Conditioning**

---

## 2. Introduction

### 2.1 Background

Protein engineering represents one of the most promising frontiers in biotechnology, with applications spanning therapeutic development, industrial enzyme design, and environmental remediation. Recent advances in generative machine learning have produced remarkable tools for protein design, including diffusion-based models such as RFdiffusion and flow-matching approaches like FrameFlow. These models leverage the geometric principles underlying protein structure—particularly SE(3) equivariance, which ensures that predictions remain consistent under rotations and translations in three-dimensional space—to generate novel protein structures with unprecedented diversity and quality.

Despite impressive in-silico performance on computational benchmarks, a critical disconnect persists between computational predictions and experimental outcomes. Current protein generative models achieve wet-lab success rates of only 5-20%, meaning that the vast majority of computationally designed proteins fail when synthesized and tested experimentally. This gap creates substantial inefficiencies: each experimental validation cycle requires weeks of laboratory work and thousands of dollars in resources, yet most designs fail to exhibit desired functional properties such as binding affinity, expression levels, or thermostability.

The fundamental challenge lies in the inability of current generative models to incorporate experimental feedback effectively. Existing approaches either ignore experimental outcomes entirely—treating each generation round as independent—or require expensive full model retraining when new experimental data becomes available. Neither approach is practical for iterative protein engineering campaigns where rapid adaptation to experimental results is essential.

Recent work has demonstrated the potential of feedback integration in protein design. Calvanese et al. (2025) showed that incorporating experimental outcomes through likelihood-based reintegration improved success rates from 6.7% to 63.7% in antibody design. Similarly, the ProSpero framework demonstrated that frozen generative models combined with learnable surrogate functions can achieve high fitness scores without model retraining. These findings suggest that experimental feedback contains learnable patterns that can guide generation toward validated design regions—if we can inject this feedback without disrupting the geometric symmetries essential to protein structure prediction.

### 2.2 Research Objectives

This research proposes **Equivariant Feedback Adapters (EFA)**—lightweight SE(3)-equivariant modules that inject experimental feedback into frozen protein generative models. Our primary objectives are:

1. **Develop a mathematically principled architecture** for encoding experimental outcomes (success/failure, binding affinity, expression levels) as scalar invariants that can modulate equivariant feature representations without breaking SE(3) symmetry.

2. **Demonstrate sample-efficient learning** from limited experimental data (50-100 design-outcome pairs) using contrastive learning and prototype-based conditioning strategies.

3. **Validate the approach experimentally** across multiple protein engineering targets, achieving ≥2x improvement in wet-lab success rates compared to unconditional generation.

4. **Establish theoretical and empirical guarantees** for SE(3) equivariance preservation, ensuring that the geometric properties essential to protein structure are maintained throughout the conditioning process.

### 2.3 Significance

This research addresses a critical bottleneck in translating computational protein design to real-world applications. By enabling rapid, sample-efficient iteration between computation and experiment, EFA has the potential to:

- **Reduce experimental costs** by 50% or more through improved first-round success rates
- **Accelerate therapeutic development** by shortening design-build-test cycles from months to weeks
- **Democratize protein engineering** by making iterative design accessible to laboratories without extensive computational infrastructure for model retraining
- **Advance fundamental understanding** of how experimental feedback can be integrated into geometric deep learning frameworks

The approach is particularly relevant to the GEM workshop's mission of bridging computational and experimental perspectives in biomolecular design, as it directly addresses the disconnect between in-silico benchmark performance and wet-lab outcomes.

---

## 3. Methodology

### 3.1 Overview

The EFA framework consists of three core components: (1) an experimental feedback encoder that transforms heterogeneous experimental outcomes into scalar invariant representations, (2) SE(3)-equivariant adapter layers that inject these representations into frozen generative models at Invariant Point Attention (IPA) modules, and (3) a contrastive learning objective that enables sample-efficient training from limited experimental data.

### 3.2 Experimental Feedback Encoding

We encode experimental outcomes as scalar invariants to ensure compatibility with SE(3)-equivariant architectures. Given an experimental outcome $o_i$ for design $i$, we construct a feedback vector $\mathbf{f}_i \in \mathbb{R}^d$ as follows:

**Binary outcomes** (success/failure) are encoded directly:
$$f_i^{\text{binary}} = \mathbb{1}[\text{design } i \text{ successful}]$$

**Continuous metrics** (binding affinity $K_d$, expression level $E$, thermostability $\Delta T_m$) are normalized to $[0, 1]$:
$$f_i^{\text{affinity}} = \sigma\left(\frac{\log K_d - \mu_{K_d}}{\sigma_{K_d}}\right)$$

where $\sigma(\cdot)$ is the sigmoid function and $\mu_{K_d}, \sigma_{K_d}$ are dataset statistics.

The complete feedback encoding is:
$$\mathbf{f}_i = \text{MLP}_{\text{encode}}\left([f_i^{\text{binary}}, f_i^{\text{affinity}}, f_i^{\text{expression}}, f_i^{\text{stability}}]\right) \in \mathbb{R}^d$$

where $d \in \{16, 32, 64, 128\}$ is a hyperparameter controlling the dimensionality of the feedback representation.

### 3.3 SE(3)-Equivariant Adapter Architecture

The key insight enabling equivariance-preserving conditioning is that **scalar quantities are invariant under SE(3) transformations**. We exploit this property by injecting feedback through scalar-mediated modulation of equivariant features.

Given a frozen protein generative model $G$ with Invariant Point Attention layers, let $\mathbf{h}_l^{(s)} \in \mathbb{R}^{n \times c}$ denote the scalar features and $\mathbf{h}_l^{(v)} \in \mathbb{R}^{n \times c \times 3}$ denote the vector features at layer $l$, where $n$ is the number of residues and $c$ is the channel dimension.

The EFA adapter at layer $l$ computes modulation coefficients:
$$\boldsymbol{\alpha}_l = \text{MLP}_l^{\alpha}(\mathbf{f}) \in \mathbb{R}^c, \quad \boldsymbol{\beta}_l = \text{MLP}_l^{\beta}(\mathbf{f}) \in \mathbb{R}^c$$

These coefficients modulate both scalar and vector features:
$$\tilde{\mathbf{h}}_l^{(s)} = \boldsymbol{\alpha}_l \odot \mathbf{h}_l^{(s)} + \boldsymbol{\beta}_l$$
$$\tilde{\mathbf{h}}_l^{(v)} = \boldsymbol{\alpha}_l \odot \mathbf{h}_l^{(v)}$$

where $\odot$ denotes element-wise multiplication broadcast across residues (and spatial dimensions for vectors).

**Theorem (Equivariance Preservation):** If $G$ is SE(3)-equivariant and $\boldsymbol{\alpha}_l, \boldsymbol{\beta}_l$ are scalar functions of scalar inputs $\mathbf{f}$, then the adapted model $\tilde{G}$ remains SE(3)-equivariant.

*Proof sketch:* Under rotation $R \in SO(3)$ and translation $\mathbf{t} \in \mathbb{R}^3$, scalar features transform as $\mathbf{h}^{(s)} \mapsto \mathbf{h}^{(s)}$ (invariant) and vector features transform as $\mathbf{h}^{(v)} \mapsto R\mathbf{h}^{(v)}$. Since $\boldsymbol{\alpha}_l, \boldsymbol{\beta}_l$ are scalars, the modulated features satisfy:
$$R(\boldsymbol{\alpha}_l \odot \mathbf{h}^{(v)}) = \boldsymbol{\alpha}_l \odot (R\mathbf{h}^{(v)})$$
preserving equivariance. $\square$

### 3.4 Contrastive Learning Objective

To enable sample-efficient learning from limited experimental data, we employ a contrastive learning framework that learns to discriminate between successful and failed designs.

Given a dataset $\mathcal{D} = \{(x_i, o_i)\}_{i=1}^N$ of design-outcome pairs, we construct positive pairs $(x_i^+, x_j^+)$ from successful designs and negative pairs $(x_i^+, x_k^-)$ between successful and failed designs.

The contrastive loss is:
$$\mathcal{L}_{\text{contrast}} = -\mathbb{E}\left[\log \frac{\exp(\text{sim}(\mathbf{z}_i^+, \mathbf{z}_j^+) / \tau)}{\sum_{k} \exp(\text{sim}(\mathbf{z}_i^+, \mathbf{z}_k) / \tau)}\right]$$

where $\mathbf{z}_i = \text{Encoder}(x_i)$ is the latent representation, $\text{sim}(\cdot, \cdot)$ is cosine similarity, and $\tau$ is a temperature parameter.

Additionally, we employ **prototype-based conditioning** to capture diverse success modes:
$$\mathbf{p}_k = \frac{1}{|\mathcal{C}_k|} \sum_{i \in \mathcal{C}_k} \mathbf{z}_i^+, \quad k = 1, \ldots, K$$

where $\mathcal{C}_k$ are clusters of successful designs obtained via k-means clustering with $K \in \{5, 10\}$ prototypes.

The complete training objective is:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{contrast}} + \lambda \mathcal{L}_{\text{prototype}}$$

where $\mathcal{L}_{\text{prototype}}$ encourages generated designs to align with successful prototypes.

### 3.5 Experimental Design

#### 3.5.1 Datasets and Protein Targets

We validate EFA across three protein engineering tasks with available experimental data:

1. **PD-L1 Binders:** Therapeutic antibody design targeting the PD-1/PD-L1 immune checkpoint. Success metric: binding affinity $K_d < 10$ nM.

2. **GFP Variants:** Fluorescent protein engineering for improved brightness. Success metric: fluorescence intensity > 1.5× wild-type.

3. **GB1 Fitness Landscape:** Protein G B1 domain stability optimization. Success metric: fitness score in top 20% of measured variants.

For each target, we use existing experimental datasets (50-100 design-outcome pairs) for EFA training and reserve held-out designs for validation.

#### 3.5.2 Baselines

We compare EFA against four baselines:

1. **Unconditional Generation:** Standard RFdiffusion/FrameFlow without feedback conditioning.

2. **Likelihood Reintegration:** The approach of Calvanese et al. (2025) that modifies sampling probabilities based on experimental outcomes.

3. **Full Fine-tuning:** Retraining the generative model on successful designs only.

4. **LoRA Adaptation:** Low-rank adaptation of the generative model without equivariance constraints.

#### 3.5.3 Evaluation Metrics

**Primary Metrics:**
- **Wet-lab Success Rate:** Percentage of generated designs passing functional assays
- **Sample Efficiency:** Number of experimental rounds to achieve 50% success rate

**Secondary Metrics:**
- **SE(3) Equivariance Error:** $\epsilon = \frac{1}{N}\sum_i \|G(Rx_i + \mathbf{t}) - RG(x_i) - \mathbf{t}\|_2$, target: $\epsilon < 1\%$
- **Design Diversity:** Sequence identity (<50%) and structural RMSD (>2Å) from training data
- **Computational Efficiency:** Training time and GPU memory requirements

#### 3.5.4 Statistical Analysis

For wet-lab success rate comparison, we use a two-proportion z-test:
$$z = \frac{\hat{p}_{\text{EFA}} - \hat{p}_{\text{baseline}}}{\sqrt{\hat{p}(1-\hat{p})(1/n_1 + 1/n_2)}}$$

with Bonferroni correction for multiple comparisons. We require $n \geq 50$ designs per condition to achieve 80% power at $\alpha = 0.05$ for detecting a 2× improvement.

#### 3.5.5 Ablation Studies

We conduct ablations to validate the causal mechanism:

1. **Injection Depth:** Compare 1, 2, 3, 4 IPA layers for adapter placement
2. **Scalar Dimensionality:** Compare $d \in \{16, 32, 64, 128\}$
3. **Feedback Type:** Binary-only vs. continuous metrics vs. combined
4. **Learning Strategy:** Contrastive-only vs. prototype-only vs. combined

### 3.6 Implementation Details

EFA adapters are implemented in PyTorch with approximately 0.5-2M trainable parameters (compared to >100M in the frozen base model). Training uses AdamW optimizer with learning rate $10^{-4}$, batch size 16, and early stopping based on validation loss. Expected training time is 2-4 hours on a single A100 GPU.

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome (P1):** We expect EFA-conditioned generation to achieve wet-lab success rates of 20-40%, representing a ≥2× improvement over the 5-20% baseline of unconditional generation. This prediction is supported by the strong performance of feedback integration in related work (Calvanese et al. achieving 63.7% from 6.7% baseline).

**Secondary Outcomes:**
- **P2:** SE(3) equivariance error will remain below 1%, confirming that scalar injection preserves geometric symmetries
- **P3:** EFA will achieve 50% cumulative success rate within 2-3 experimental rounds, compared to 5-6 rounds for unconditional generation with selection
- **P4:** Cold-start performance using in-silico predictor feedback will exceed random baseline by >20%

**Potential Negative Results:** If the hypothesis is falsified (success rate ratio ≤1.2×), this would indicate that either: (a) experimental feedback cannot be meaningfully encoded as scalar invariants, (b) 50-100 samples are insufficient for contrastive learning, or (c) the base generative model's latent space is not amenable to steering through adapter conditioning. Each failure mode would provide valuable insights for future research directions.

### 4.2 Scientific Impact

This research contributes to multiple areas:

1. **Geometric Deep Learning:** Establishes theoretical and empirical foundations for conditioning equivariant models through scalar injection, with potential applications beyond protein design to molecular generation and materials science.

2. **Protein Engineering:** Provides a practical framework for integrating experimental feedback into computational design workflows, addressing a critical bottleneck in the field.

3. **Sample-Efficient Learning:** Demonstrates that contrastive learning on small experimental datasets (50-100 samples) can effectively guide generative models, relevant to many scientific domains with limited labeled data.

### 4.3 Practical Impact

**For Experimentalists:** EFA enables rapid iteration between computation and experiment without requiring ML expertise for model retraining. Laboratories can simply provide experimental outcomes and receive improved designs within hours.

**For Computationalists:** The adapter framework provides a modular approach to incorporating domain-specific feedback into pre-trained models, applicable to diverse protein engineering tasks.

**For Industry:** Reduced experimental costs (estimated 50% reduction in synthesis and testing expenses) and accelerated development timelines could significantly impact therapeutic protein development, industrial enzyme engineering, and synthetic biology applications.

### 4.4 Broader Implications

By bridging the gap between computational predictions and experimental outcomes, this research contributes to the broader goal of making machine learning genuinely useful for biological discovery. The EFA framework exemplifies the type of experimentally-grounded ML development that the GEM workshop seeks to promote, with potential for direct translation to wet-lab practice.

The modular, sample-efficient nature of EFA also addresses equity concerns in computational biology: laboratories without extensive computational resources can benefit from state-of-the-art generative models while incorporating their unique experimental insights. This democratization of advanced protein design tools could accelerate progress across the field.

---

**Word Count:** ~2,150 words