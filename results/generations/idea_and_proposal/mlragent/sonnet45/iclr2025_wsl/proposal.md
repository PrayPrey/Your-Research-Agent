# Research Proposal: Permutation-Invariant Weight Fingerprinting for Neural Network Provenance and Integrity Verification

## 1. Title

**Permutation-Invariant Weight Fingerprinting for Neural Network Provenance and Integrity Verification**

## 2. Introduction

### Background

The democratization of machine learning has led to an unprecedented proliferation of pre-trained neural network models. Platforms like Hugging Face currently host over one million publicly available models, creating a rich ecosystem for model sharing and reuse. However, this rapid growth has introduced critical challenges in model governance, intellectual property protection, and security. Unlike traditional digital artifacts that can be verified through cryptographic hashing, neural network weights present unique challenges due to their inherent symmetries and geometric properties.

A fundamental challenge in treating neural network weights as a data modality is the existence of weight space symmetries. Two neural networks can be functionally identical—producing exactly the same outputs for all inputs—while having vastly different weight configurations. These symmetries arise from several sources: permutation invariance (neurons within a layer can be arbitrarily reordered), scaling symmetries (weights can be rescaled across adjacent layers), and sign flips in certain activation functions. Traditional fingerprinting methods that treat weights as flat vectors fail catastrophically in the presence of these symmetries, as a simple neuron permutation would produce an entirely different hash despite unchanged functionality.

This fundamental mismatch between the geometric structure of weight space and existing verification methods has created a security and governance gap. Model creators cannot reliably prove ownership, model users cannot verify provenance, and malicious actors can introduce backdoors or unauthorized modifications that evade detection. Furthermore, the computational cost of identifying duplicate or derivative models in large repositories becomes prohibitive without geometry-aware fingerprinting methods.

### Research Objectives

This research proposes a novel framework for **permutation-invariant weight fingerprinting** that respects the geometric structure of neural network weight spaces while enabling robust model verification. Our primary objectives are:

1. **Develop a permutation-equivariant architecture** that processes neural network weights as structured graph data, naturally handling the inherent symmetries of weight spaces through message-passing operations.

2. **Design a contrastive learning framework** that learns canonical embeddings of neural networks, where functionally equivalent models (related by symmetry transformations) map to similar fingerprints, while distinct or maliciously modified models produce dissimilar embeddings.

3. **Create a comprehensive evaluation framework** for model fingerprinting across three critical applications: provenance tracking, integrity verification, and duplicate detection.

4. **Establish theoretical foundations** for understanding the expressivity and invariance properties of weight space fingerprinting systems.

### Significance

This research addresses several pressing needs in the machine learning ecosystem:

**Security and Trust**: As neural networks increasingly mediate critical decisions in healthcare, finance, and autonomous systems, verifying model integrity becomes paramount. Our approach enables detection of weight-space backdoors and adversarial modifications that evade input-space defenses.

**Intellectual Property Protection**: Model creators invest significant computational resources in training. Geometry-aware fingerprinting enables robust provenance tracking and detection of unauthorized derivatives, even when models are fine-tuned or partially modified.

**Repository Management**: With millions of models available, identifying duplicates and understanding model lineage becomes computationally prohibitive. Our method enables efficient similarity search in weight space, facilitating better model discovery and reducing redundancy.

**Scientific Contribution**: This work bridges multiple research areas—weight space learning, graph neural networks, and model security—while establishing neural network weights as a first-class data modality with its own geometric structure and processing requirements.

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{M}$ denote the space of neural networks with a given architecture. For a network $f_\theta \in \mathcal{M}$ with weights $\theta$, we seek to learn a fingerprinting function $\phi: \mathcal{M} \rightarrow \mathbb{R}^d$ that produces a $d$-dimensional embedding satisfying:

1. **Permutation Invariance**: For any permutation $\pi$ in the symmetry group $G$ of the architecture, $\phi(f_{\pi(\theta)}) \approx \phi(f_\theta)$.

2. **Discriminative Power**: For functionally distinct networks $f_{\theta_1}$ and $f_{\theta_2}$, $\|\phi(f_{\theta_1}) - \phi(f_{\theta_2})\|_2$ should be large.

3. **Robustness**: Small benign perturbations (e.g., continued training) should produce small changes in the fingerprint, while malicious modifications (e.g., backdoor injection) should produce detectable changes.

### 3.2 Graph Representation of Neural Networks

We represent a neural network as a directed acyclic graph $G = (V, E)$ where:

- **Nodes** $V$ represent neurons, with node features $\mathbf{h}_v \in \mathbb{R}^{d_n}$ encoding neuron-level statistics (e.g., bias values, aggregated incoming/outgoing weight statistics).

- **Edges** $E$ represent connections between neurons, with edge features $\mathbf{e}_{uv} \in \mathbb{R}^{d_e}$ encoding weight values and derived statistics.

For a fully connected layer with weight matrix $\mathbf{W} \in \mathbb{R}^{n_{out} \times n_{in}}$ and bias $\mathbf{b} \in \mathbb{R}^{n_{out}}$, we construct:

$$\mathbf{h}_v = [\mathbf{b}_v, \|\mathbf{W}_{v,:}\|_2, \text{mean}(\mathbf{W}_{v,:}), \text{std}(\mathbf{W}_{v,:})]$$

$$\mathbf{e}_{uv} = [\mathbf{W}_{vu}, \text{sign}(\mathbf{W}_{vu}), |\mathbf{W}_{vu}|]$$

This representation naturally extends to convolutional layers by treating each filter as a node and encoding kernel weights as edge features.

### 3.3 Permutation-Equivariant Fingerprinting Architecture

Our fingerprinting system consists of three components:

#### 3.3.1 Local Feature Extraction

We employ a Graph Neural Network (GNN) with message-passing layers to extract permutation-equivariant features:

$$\mathbf{m}_{v}^{(t)} = \text{AGGREGATE}\left(\left\{\mathbf{e}_{uv} \oplus \mathbf{h}_u^{(t-1)} : u \in \mathcal{N}(v)\right\}\right)$$

$$\mathbf{h}_v^{(t)} = \text{UPDATE}\left(\mathbf{h}_v^{(t-1)}, \mathbf{m}_v^{(t)}\right)$$

where $\oplus$ denotes concatenation, $\mathcal{N}(v)$ are neighbors of node $v$, and AGGREGATE uses permutation-invariant functions (e.g., sum, max, mean). Specifically:

$$\text{AGGREGATE}(\{\mathbf{x}_i\}) = \text{MLP}_{\text{agg}}\left(\sum_i \mathbf{x}_i \oplus \max_i \mathbf{x}_i \oplus \text{mean}_i \mathbf{x}_i\right)$$

$$\text{UPDATE}(\mathbf{h}, \mathbf{m}) = \text{LayerNorm}(\mathbf{h} + \text{MLP}_{\text{update}}(\mathbf{h} \oplus \mathbf{m}))$$

We apply $L=6$ message-passing layers to capture multi-hop dependencies in the network architecture.

#### 3.3.2 Global Pooling and Fingerprint Generation

To obtain a fixed-size fingerprint invariant to node ordering, we apply hierarchical pooling:

$$\mathbf{z}_{\text{global}} = \text{POOL}\left(\left\{\mathbf{h}_v^{(L)} : v \in V\right\}\right)$$

We use a combination of multiple pooling operations to capture diverse graph properties:

$$\mathbf{z}_{\text{global}} = \left[\sum_{v \in V} \mathbf{h}_v^{(L)} \oplus \max_{v \in V} \mathbf{h}_v^{(L)} \oplus \text{SAG-Pool}(\{\mathbf{h}_v^{(L)}\})\right]$$

where SAG-Pool is a self-attention graph pooling mechanism:

$$\mathbf{z}_{\text{SAG}} = \sum_{v \in V} \sigma\left(\text{MLP}_{\text{att}}(\mathbf{h}_v^{(L)})\right) \cdot \mathbf{h}_v^{(L)}$$

The final fingerprint is generated through a projection head:

$$\phi(f_\theta) = \text{MLP}_{\text{proj}}(\mathbf{z}_{\text{global}}) \in \mathbb{R}^d$$

with $d=256$ dimensions, followed by $\ell_2$ normalization.

### 3.4 Contrastive Learning Framework

We train the fingerprinting system using a supervised contrastive loss that explicitly incorporates weight space symmetries:

#### 3.4.1 Data Augmentation via Symmetry Transformations

For each model $f_\theta$, we generate positive pairs through symmetry-preserving transformations:

1. **Random permutations**: Apply random neuron permutations within layers
2. **Scaling transformations**: Apply complementary scaling across layer boundaries
3. **Continued training**: Brief fine-tuning on related tasks (≤5% parameter change)

Negative examples include:

1. **Different base models**: Models trained with different initializations or architectures
2. **Malicious modifications**: Models with injected backdoors or adversarial perturbations
3. **Hard negatives**: Models from the same family but fine-tuned on different tasks

#### 3.4.2 Loss Function

We employ a triplet loss with online hard negative mining:

$$\mathcal{L}_{\text{triplet}} = \sum_{i=1}^{N} \max\left(0, \|\phi(f_{\theta_i}) - \phi(f_{\theta_i^+})\|_2^2 - \|\phi(f_{\theta_i}) - \phi(f_{\theta_i^-})\|_2^2 + \alpha\right)$$

where $f_{\theta_i^+}$ is a symmetry-transformed version of $f_{\theta_i}$, $f_{\theta_i^-}$ is a hard negative, and $\alpha=0.5$ is the margin.

Additionally, we incorporate a supervised contrastive loss for models with known provenance labels:

$$\mathcal{L}_{\text{sup}} = -\sum_{i=1}^{N} \frac{1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(\phi(f_{\theta_i}) \cdot \phi(f_{\theta_p}) / \tau)}{\sum_{a \in A(i)} \exp(\phi(f_{\theta_i}) \cdot \phi(f_{\theta_a}) / \tau)}$$

where $P(i)$ is the set of positive pairs (same provenance), $A(i)$ is all examples except $i$, and $\tau=0.1$ is the temperature parameter.

The total loss is:

$$\mathcal{L} = \mathcal{L}_{\text{triplet}} + \lambda \mathcal{L}_{\text{sup}}$$

with $\lambda=0.5$.

### 3.5 Data Collection and Experimental Design

#### 3.5.1 Datasets

We construct three complementary datasets:

**Dataset 1: Controlled Model Zoo**
- Train 10,000 models across 5 architectures (ResNet, VGG, MobileNet, Vision Transformer, BERT variants)
- For each base architecture, generate 2,000 variants through:
  - Different random initializations (500)
  - Different training datasets (CIFAR-10, CIFAR-100, ImageNet subsets) (500)
  - Different hyperparameters (learning rate, batch size, optimizer) (500)
  - Fine-tuned versions (500)

**Dataset 2: Symmetry Test Set**
- For 1,000 base models, generate 50 symmetry-transformed variants each through:
  - Random permutations (20)
  - Scaling transformations (10)
  - Combined transformations (10)
  - Continued training for 1-10 epochs (10)

**Dataset 3: Backdoor Detection Set**
- Create 2,000 backdoored models using established attack methods:
  - BadNets (500)
  - Trojan attacks (500)
  - Clean-label backdoors (500)
  - Blend attacks (500)
- Each with varying trigger sizes and target classes

#### 3.5.2 Training Protocol

1. **Preprocessing**: Convert all models to graph representation, computing node and edge features
2. **Batching**: Group graphs of similar sizes to enable efficient batching (batch size = 32)
3. **Optimization**: Train using AdamW optimizer with learning rate $10^{-4}$, weight decay $10^{-5}$
4. **Schedule**: Cosine annealing learning rate schedule over 100 epochs
5. **Hardware**: 4×A100 GPUs with distributed data parallel training

#### 3.5.3 Evaluation Metrics

**Provenance Tracking**:
- **Retrieval Accuracy**: Top-k accuracy for identifying the correct base model from which a derivative was fine-tuned (k=1, 5, 10)
- **Lineage Recovery**: F1-score for reconstructing model family trees

**Integrity Verification**:
- **Backdoor Detection AUROC**: Area under ROC curve for distinguishing clean vs. backdoored models
- **Modification Detection**: True positive rate at 1% false positive rate for detecting unauthorized changes

**Duplicate Detection**:
- **Symmetry Invariance Score**: Mean pairwise distance between fingerprints of symmetry-transformed variants (should be ≈0)
- **Discriminative Power**: Mean pairwise distance between fingerprints of functionally distinct models (should be large)
- **Search Efficiency**: Query time for finding duplicates in a repository of 100K models

**Robustness**:
- **Benign Perturbation Robustness**: Fingerprint stability under continued training (Δ<0.1)
- **Malicious Perturbation Sensitivity**: Fingerprint change under backdoor injection (Δ>0.5)

### 3.6 Baseline Comparisons

We compare against:

1. **Naive Weight Hashing**: Cryptographic hash of flattened weights
2. **Weight Statistics**: Fingerprints based on layer-wise weight statistics (mean, std, skewness)
3. **Model2Vec**: Existing weight embedding methods treating weights as sequences
4. **Function-Based Fingerprinting**: Watermarking through input-output behaviors
5. **Neuron Embedding**: Recent permutation-invariant neuron representation methods

### 3.7 Theoretical Analysis

We provide theoretical guarantees on:

1. **Expressivity**: Prove that our GNN architecture is at least as expressive as the 2-WL test in distinguishing non-isomorphic neural network graphs
2. **Invariance**: Formally verify that the fingerprinting function is invariant to the symmetry group of the architecture
3. **Stability**: Establish Lipschitz continuity bounds relating weight space perturbations to fingerprint distances

## 4. Expected Outcomes & Impact

### Expected Outcomes

**Technical Achievements**:

1. **High-Accuracy Model Identification**: We expect to achieve >95% top-1 accuracy in identifying base models from fine-tuned derivatives, even when models have undergone substantial adaptation (up to 20% parameter change).

2. **Robust Backdoor Detection**: The system should achieve AUROC >0.95 for detecting backdoored models across diverse attack methods, outperforming input-space detection methods that are attack-specific.

3. **Perfect Symmetry Invariance**: Fingerprints of symmetry-transformed variants should have cosine similarity >0.99, demonstrating true geometric understanding of weight space.

4. **Efficient Repository Search**: Enable sub-second duplicate detection queries in repositories of 100K+ models through approximate nearest neighbor search in the learned embedding space.

5. **Theoretical Guarantees**: Formal proofs of expressivity bounds and invariance properties, establishing foundations for weight space fingerprinting.

**Deliverables**:

1. **Open-Source Implementation**: A PyTorch-based library for model fingerprinting with pre-trained fingerprinting networks for common architectures
2. **Model Zoo Dataset**: A curated dataset of 10,000+ models with provenance labels and symmetry variants for benchmarking
3. **Evaluation Suite**: Comprehensive benchmarks for assessing fingerprinting methods across multiple criteria
4. **Theoretical Framework**: Mathematical characterization of weight space geometry relevant to fingerprinting

### Impact

**Immediate Impact**:

**Enhanced Model Security**: Our fingerprinting system enables model repositories to automatically detect malicious modifications, protecting users from backdoored models. This is particularly critical as models are increasingly deployed in security-sensitive applications.

**Intellectual Property Protection**: Model creators can cryptographically sign their fingerprints, enabling verifiable proof of ownership even when models are distributed and modified. This encourages open sharing while protecting creators' rights.

**Repository Efficiency**: Automatic duplicate detection reduces storage redundancy and helps users discover existing solutions before training new models, reducing computational waste.

**Long-Term Impact**:

**Establishing Weight Space as a Modality**: This work demonstrates that neural network weights can be processed as structured data with their own geometry, paving the way for other weight space learning applications (model merging, architecture search, meta-learning).

**Foundation for Model Governance**: As AI regulation evolves, our methods provide technical infrastructure for model provenance tracking, essential for compliance with proposed AI audit requirements.

**Cross-Domain Applications**: The principles developed here extend beyond supervised learning to other weight-based artifacts like neural radiance fields (NeRFs), implicit neural representations (INRs), and generative models, enabling provenance tracking in 3D vision and scientific computing.

**Interdisciplinary Connections**: This work bridges graph neural networks, model security, and weight space learning, fostering collaboration between communities that have developed largely independently.

**Broader Implications**:

By treating weight space symmetries as a fundamental property to be respected rather than an obstacle to be overcome, this research shifts the paradigm for how we analyze and process neural networks. Just as translation invariance is fundamental to image processing via CNNs, and permutation invariance is fundamental to set and graph processing, this work establishes symmetry-awareness as fundamental to weight space processing. This conceptual contribution will influence future research in model merging, neural architecture search, continual learning, and other emerging areas where neural network weights themselves become objects of computation.

The successful completion of this research will establish neural network fingerprinting as a solved problem for common architectures, enabling the trustworthy model ecosystem necessary for the continued democratization of machine learning. Furthermore, it will provide the methodological foundation for treating weight spaces as a first-class data modality, opening new research directions in meta-learning, model synthesis, and automated machine learning.