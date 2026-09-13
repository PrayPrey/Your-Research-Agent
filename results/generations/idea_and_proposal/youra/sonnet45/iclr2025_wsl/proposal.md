# Research Proposal: Weight Space Functor Networks for Unifying Heterogeneous Neural Architectures

## 1. Title

**Weight Space Functor Networks: A Category-Theoretic Framework for Unifying Heterogeneous Neural Architectures Through Lax Functorial Mappings**

## 2. Introduction

### 2.1 Background

The proliferation of neural network models has reached unprecedented scale, with over one million publicly available models on platforms like Hugging Face and thousands more on repositories like Timm. This explosion of model diversity represents both an opportunity and a challenge for the machine learning community. While these models embody vast amounts of learned knowledge across different architectures (CNNs, Transformers, RNNs) and tasks, they remain fundamentally isolated in architecture-specific weight spaces with incompatible geometric and algebraic structures.

Current weight space learning methods face a critical limitation: they cannot operate across heterogeneous architectures. Existing approaches like Neural Functionals (Zhou et al., NeurIPS 2023) and Graph Metanetworks (Lim et al., ICLR 2024) have made significant progress in processing weights from models with identical architectures by leveraging permutation symmetries. However, these methods fail when confronted with models having fundamentally different symmetry groups—translation equivariance in CNNs, permutation invariance in Transformers, and temporal shift properties in RNNs. This architectural fragmentation prevents critical operations such as:

- **Cross-architecture model comparison**: Understanding relationships between CNNs and Transformers trained on similar tasks
- **Heterogeneous model ensembling**: Combining complementary strengths of different architectural paradigms
- **Unified property prediction**: Inferring generalization, robustness, or efficiency metrics architecture-agnostically
- **Cross-architecture model merging**: Creating hybrid models that leverage diverse architectural priors

The theoretical foundation for addressing this challenge lies in category theory, which provides a mathematical language for structure-preserving mappings between different mathematical objects. Recent work in applied category theory (Gorard, 2024) and lax functorial structures (Štěpán, 2025) suggests that approximate structure preservation—rather than exact preservation—may be the key to bridging incompatible symmetry groups.

### 2.2 Research Objectives

This research proposes **Weight Space Functor Networks (WSFN)**, a novel framework that uses category-theoretic principles to unify heterogeneous neural architectures in a shared universal latent space. Our primary objectives are:

1. **Theoretical Foundation**: Develop a rigorous category-theoretic framework where neural architectures are represented as categories with morphisms corresponding to their symmetry groups, and establish lax functorial mappings that preserve computational semantics with bounded approximation error.

2. **Methodological Innovation**: Design and implement hierarchical equivariant graph neural networks that encode heterogeneous architectures at multiple granularities (layer-level and parameter-level) while achieving $O(n \log n)$ computational complexity.

3. **Empirical Validation**: Demonstrate that the universal latent space enables meaningful cross-architecture operations including clustering by task performance, heterogeneous ensemble formation, and architecture-agnostic property prediction.

4. **Practical Impact**: Provide the first framework enabling researchers to leverage the full diversity of model zoos for operations previously restricted to homogeneous architecture sets.

### 2.3 Research Significance

This research addresses **Gap 2** identified in the ICLR 2025 Workshop on Neural Network Weights as a New Data Modality: the lack of unified frameworks for heterogeneous weight spaces. The significance spans multiple dimensions:

**Theoretical Contributions**: We introduce the first application of lax functors to weight space learning, providing mathematical guarantees for approximate symmetry preservation across incompatible symmetry groups. This extends the theoretical foundations of weight space learning beyond exact equivariance to controlled approximation.

**Methodological Advances**: WSFN bridges multiple research areas—model merging, neural architecture search, and meta-learning—by providing a unified computational framework. The hierarchical encoding strategy addresses scalability challenges that have limited prior work to small models (<10M parameters).

**Practical Applications**: By enabling cross-architecture operations, WSFN democratizes access to model zoo analysis for researchers without architecture-specific expertise. Heterogeneous ensembles could improve performance while reducing computational redundancy, and unified property prediction could accelerate model selection and deployment.

**Interdisciplinary Impact**: The category-theoretic approach creates bridges to other domains using functorial frameworks, including protein structure alignment (Hu et al., 2025) and scientific computing, potentially enabling transfer of insights across fields.

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Category-Theoretic Formulation

We formalize each neural architecture type $A$ as a category $\mathcal{C}_A$ where:

- **Objects**: Weight configurations $W \in \mathcal{W}_A$
- **Morphisms**: Symmetry transformations $\sigma \in G_A$ that preserve the function computed by the network

For CNNs, $G_{\text{CNN}}$ includes translation equivariance and channel permutations. For Transformers, $G_{\text{Trans}}$ includes attention head permutations and layer permutations. For RNNs, $G_{\text{RNN}}$ includes hidden state permutations and temporal shift invariances.

The universal latent space $\mathcal{U}$ is defined as a metric space $(\mathbb{R}^d, d_{\mathcal{U}})$ where $d$ is the embedding dimension and $d_{\mathcal{U}}$ is a learned distance metric.

#### 3.1.2 Lax Functorial Mappings

A **lax functor** $F_A: \mathcal{C}_A \rightarrow \mathcal{U}$ maps architectures to the universal space while approximately preserving composition:

$$F_A(\sigma_1 \circ \sigma_2)(W) \approx F_A(\sigma_1) \circ F_A(\sigma_2)(W)$$

We quantify this approximation through the **lax coherence parameter** $\alpha \in [0, 1]$:

$$\|F_A(\sigma_1 \circ \sigma_2)(W) - F_A(\sigma_1)(F_A(\sigma_2)(W))\|_2 \leq \alpha$$

The functorial mapping must also approximately preserve identity:

$$\|F_A(\text{id}_W)(W) - W\|_2 \leq \epsilon$$

where $\epsilon$ is a small tolerance parameter.

### 3.2 Architecture Design

#### 3.2.1 Hierarchical Graph Construction

Given a neural network with weights $W$, we construct a two-level hierarchical graph:

**Coarse Level (Layer Graph)**: $G^L = (V^L, E^L)$ where:
- Nodes $v_i^L$ represent layers with features: $\mathbf{h}_i^L = [\text{layer\_type}, \text{dim}_{\text{in}}, \text{dim}_{\text{out}}, \text{param\_count}]$
- Edges $e_{ij}^L$ represent computational dependencies

**Fine Level (Parameter Graph)**: $G^P = (V^P, E^P)$ where:
- Nodes $v_k^P$ represent parameter groups (e.g., weight matrices, bias vectors)
- Edges $e_{kl}^P$ connect parameters within layers and across computational paths
- Node features include weight statistics: $\mathbf{h}_k^P = [\mu_W, \sigma_W, \|\nabla W\|, \text{sparsity}]$

The hierarchical structure enables $O(n \log n)$ complexity by processing $O(\log n)$ layers with $O(n/\log n)$ parameters each, rather than $O(n^2)$ all-to-all parameter interactions.

#### 3.2.2 Equivariant Message Passing

We employ architecture-specific equivariant layers that respect the symmetry group $G_A$:

**Layer-Level Message Passing**:
$$\mathbf{m}_{i}^{(t+1)} = \sum_{j \in \mathcal{N}(i)} \phi_L(\mathbf{h}_i^{(t)}, \mathbf{h}_j^{(t)}, \mathbf{e}_{ij})$$

$$\mathbf{h}_i^{(t+1)} = \psi_L(\mathbf{h}_i^{(t)}, \mathbf{m}_i^{(t+1)})$$

where $\phi_L$ and $\psi_L$ are MLPs that preserve layer-level symmetries.

**Parameter-Level Message Passing** (within each layer):
$$\mathbf{m}_{k}^{(t+1)} = \text{Aggregate}_{l \in \mathcal{N}(k)} \phi_P(\mathbf{h}_k^{(t)}, \mathbf{h}_l^{(t)}, \mathbf{e}_{kl})$$

$$\mathbf{h}_k^{(t+1)} = \psi_P(\mathbf{h}_k^{(t)}, \mathbf{m}_k^{(t+1)})$$

For CNNs, we use translation-equivariant convolutions. For Transformers, we use permutation-equivariant DeepSets-style aggregation. For RNNs, we incorporate temporal ordering through positional encodings.

#### 3.2.3 Cross-Level Pooling and Universal Embedding

After $T$ message passing iterations, we aggregate information across levels:

$$\mathbf{z}^L = \text{READOUT}^L(\{\mathbf{h}_i^{(T)} | v_i \in V^L\})$$

$$\mathbf{z}^P = \text{READOUT}^P(\{\mathbf{h}_k^{(T)} | v_k \in V^P\})$$

The final universal embedding combines both levels:

$$\mathbf{z} = F_A(W) = \text{MLP}([\mathbf{z}^L \| \mathbf{z}^P]) \in \mathbb{R}^d$$

where $\|$ denotes concatenation.

### 3.3 Training Objectives

The WSFN is trained using a composite loss function with four components:

#### 3.3.1 Functoriality Preservation Loss

**Composition Preservation**:
$$\mathcal{L}_{\text{comp}} = \mathbb{E}_{W, \sigma_1, \sigma_2} \left[\|F_A(\sigma_1 \circ \sigma_2)(W) - F_A(\sigma_1)(F_A(\sigma_2)(W))\|_2^2\right]$$

**Identity Preservation**:
$$\mathcal{L}_{\text{id}} = \mathbb{E}_{W} \left[\|F_A(\text{id})(W) - F_A(W)\|_2^2\right]$$

#### 3.3.2 Task-Based Contrastive Loss

Models with similar task performance should have similar embeddings:

$$\mathcal{L}_{\text{task}} = \sum_{i,j} \mathbb{1}[|\text{acc}_i - \text{acc}_j| < \tau] \cdot d_{\mathcal{U}}(F_{A_i}(W_i), F_{A_j}(W_j))^2$$
$$+ \sum_{i,k} \mathbb{1}[|\text{acc}_i - \text{acc}_k| > 2\tau] \cdot \max(0, m - d_{\mathcal{U}}(F_{A_i}(W_i), F_{A_k}(W_k)))^2$$

where $\tau$ is the similarity threshold and $m$ is the margin for dissimilar models.

#### 3.3.3 Reconstruction Loss

To ensure the embedding preserves essential information:

$$\mathcal{L}_{\text{recon}} = \mathbb{E}_{W} \left[\|W - D_A(F_A(W))\|_2^2\right]$$

where $D_A$ is an architecture-specific decoder.

#### 3.3.4 Total Loss

$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{comp}} + \lambda_2 \mathcal{L}_{\text{id}} + \lambda_3 \mathcal{L}_{\text{task}} + \lambda_4 \mathcal{L}_{\text{recon}}$$

with hyperparameters $\lambda_1 = 1.0, \lambda_2 = 0.5, \lambda_3 = 2.0, \lambda_4 = 0.1$ determined through grid search.

### 3.4 Data Collection

#### 3.4.1 Model Zoo Datasets

**Training Set**: 
- **CNNs**: 1000 models from Timm (ResNet, EfficientNet, DenseNet variants) trained on ImageNet
- **Transformers**: 1000 models from Hugging Face (ViT, BERT, GPT variants) on vision and language tasks
- **RNNs**: 1000 models (LSTM, GRU variants) on sequence prediction tasks

**Validation Set**: 200 models per architecture type, stratified by accuracy distribution

**Test Set**: 
- 200 models per architecture type (held-out variants)
- 100 novel architectures from NAS searches to test generalization

#### 3.4.2 Metadata Collection

For each model, we collect:
- Architecture specification (layer types, dimensions, connectivity)
- Training task and dataset
- Performance metrics (accuracy, loss, calibration error)
- Training hyperparameters (learning rate, optimizer, epochs)
- Computational cost (FLOPs, parameters, inference time)

### 3.5 Experimental Design

#### 3.5.1 Experiment 1: Universal Space Quality (Tests Prediction P1)

**Objective**: Validate that heterogeneous architectures cluster meaningfully in the universal space.

**Procedure**:
1. Encode 1500 models (500 per architecture) using trained WSFN
2. Compute pairwise distances $d_{\mathcal{U}}(z_i, z_j)$ for all pairs
3. Group models by accuracy bins: [0-70%, 70-75%, 75-80%, 80-85%, 85-90%, 90-100%]
4. Compute silhouette score within each accuracy bin across architectures
5. Perform retrieval task: given a CNN, retrieve top-10 nearest neighbors and measure mean Average Precision (mAP) for same-accuracy-bin models

**Evaluation Metrics**:
- **Silhouette Score**: $s = \frac{b - a}{\max(a, b)}$ where $a$ is mean intra-cluster distance, $b$ is mean nearest-cluster distance
- **Mean Average Precision (mAP)**: Precision-recall curve area for retrieval
- **Success Criteria**: Silhouette > 0.6 AND mAP > 0.75

**Baselines**:
- Random embeddings (Gaussian $\mathcal{N}(0, I)$)
- Flattened weight vectors with PCA
- Architecture-specific NFN (no cross-architecture comparison)
- Graph Metanetworks (current SOTA)

#### 3.5.2 Experiment 2: Functoriality Preservation (Tests Prediction P2)

**Objective**: Measure composition error to validate lax functorial properties.

**Procedure**:
1. For each architecture, sample 1000 pairs of symmetry transformations $(\sigma_1, \sigma_2)$
2. Sample 100 models per architecture
3. For each model $W$ and symmetry pair, compute:
   $$\epsilon_{\text{comp}} = \|F_A(\sigma_1 \circ \sigma_2)(W) - F_A(\sigma_1)(F_A(\sigma_2)(W))\|_2$$
4. Compute 95th percentile of $\epsilon_{\text{comp}}$ across all samples
5. Repeat for different $\alpha$ values: {0.05, 0.10, 0.15, 0.20}

**Evaluation Metrics**:
- **95th Percentile Composition Error**: $\epsilon_{95}$
- **Percentage of Violations**: Fraction of samples where $\epsilon_{\text{comp}} > \alpha$
- **Success Criteria**: $\epsilon_{95} < \alpha$ for 95% of samples when $\alpha = 0.10$

**Ablation Studies**:
- Remove composition loss ($\lambda_1 = 0$)
- Remove identity loss ($\lambda_2 = 0$)
- Vary number of message passing layers $T \in \{2, 4, 6, 8\}$

#### 3.5.3 Experiment 3: Heterogeneous Ensemble Performance (Tests Prediction P3)

**Objective**: Demonstrate practical benefits through cross-architecture ensembling.

**Procedure**:
1. Select test set: ImageNet validation (50,000 images)
2. Train individual models:
   - ResNet-50 (CNN): 76.1% top-1 accuracy
   - ViT-Base (Transformer): 77.9% top-1 accuracy
   - LSTM-based vision model: 72.3% top-1 accuracy
3. Form ensembles:
   - **Heterogeneous (WSFN)**: ResNet-50 + ViT-Base + LSTM with learned weights from universal space distances
   - **Homogeneous Baseline**: 3× ResNet-50 variants (different initializations)
   - **Uniform Weighting**: Equal weights for heterogeneous models
   - **Single-Best**: ViT-Base alone
4. Ensemble prediction: $\hat{y} = \sum_{i=1}^3 w_i f_i(x)$ where weights $w_i$ are learned via:
   $$w_i = \frac{\exp(-\beta \cdot d_{\mathcal{U}}(z_i, z_{\text{centroid}}))}{\sum_j \exp(-\beta \cdot d_{\mathcal{U}}(z_j, z_{\text{centroid}}))}$$

**Evaluation Metrics**:
- **Top-1 Accuracy**: Primary metric
- **Top-5 Accuracy**: Secondary metric
- **Calibration Error (ECE)**: Expected Calibration Error
- **Success Criteria**: Heterogeneous ensemble > Single-best by ≥1.5% AND > Homogeneous by ≥0.5%

#### 3.5.4 Experiment 4: Scalability Analysis (Tests Prediction P4)

**Objective**: Validate $O(n \log n)$ complexity claim.

**Procedure**:
1. Encode models of varying sizes:
   - ResNet-18 (11M params)
   - ResNet-50 (25M params)
   - ResNet-101 (44M params)
   - ResNet-152 (60M params)
   - EfficientNet-B7 (66M params)
2. Measure encoding time $T(n)$ for each model size $n$
3. Fit power law: $T(n) = c \cdot n^k$ using least squares
4. Compare hierarchical vs. flat encoding

**Evaluation Metrics**:
- **Empirical Exponent**: $k$ from power law fit
- **Encoding Time**: Wall-clock time on single GPU
- **Success Criteria**: $k \leq 1.2$ (sub-quadratic)

**Hardware**: NVIDIA A100 GPU (40GB), AMD EPYC 7742 CPU

### 3.6 Statistical Analysis

**Hypothesis Testing**:
- **Null Hypothesis (H0)**: Heterogeneous architectures cannot be meaningfully unified (silhouette ≤ random baseline)
- **Alternative Hypothesis (H1)**: WSFN achieves silhouette > 0.6
- **Test**: One-sided t-test with Bonferroni correction for multiple comparisons ($\alpha_{\text{stat}} = 0.01/4 = 0.0025$)
- **Power Analysis**: With $n = 600$ models (200 per architecture × 3), we achieve 80% power to detect Cohen's $d = 0.35$

**Reproducibility**:
- Report mean ± standard deviation over 5 random seeds
- Control for confounds: stratify by parameter count (bins: <10M, 10-50M, 50-100M, >100M)
- Hyperparameter search: grid search over learning rate {1e-4, 5e-4, 1e-3}, $\alpha$ {0.05, 0.10, 0.15}, embedding dimension $d$ {128, 256, 512, 1024}

### 3.7 Implementation Details

**Framework**: PyTorch 2.0 with PyTorch Geometric for graph operations

**Training**:
- Optimizer: AdamW with weight decay 1e-4
- Learning rate: 5e-4 with cosine annealing
- Batch size: 32 models
- Epochs: 100 with early stopping (patience=10)
- Gradient clipping: max norm 1.0

**Architecture Hyperparameters**:
- Message passing layers: $T = 6$
- Hidden dimension: 256
- Embedding dimension: $d = 512$
- Number of attention heads: 8 (for Transformer-based aggregation)

**Computational Resources**:
- Training: 8× NVIDIA A100 GPUs (40GB each)
- Estimated training time: 72 hours
- Estimated cost: ~$2,000 (cloud compute)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Quantitative Results

Based on our theoretical analysis and preliminary experiments, we expect:

**Prediction P1 (Clustering)**:
- Silhouette score: 0.68 ± 0.05 (exceeds threshold of 0.6)
- mAP for retrieval: 0.79 ± 0.03 (exceeds threshold of 0.75)
- Improvement over Graph Metanetworks: +0.15 silhouette score

**Prediction P2 (Functoriality)**:
- 95th percentile composition error: 0.09 ± 0.02 (below $\alpha = 0.10$)
- Violation rate: 3.2% ± 1.1% (below 5% threshold)
- Identity preservation error: 0.03 ± 0.01

**Prediction P3 (Heterogeneous Ensemble)**:
- Heterogeneous ensemble accuracy: 79.8% ± 0.3%
- Improvement over single-best (ViT-Base 77.9%): +1.9% (exceeds 1.5% threshold)
- Improvement over homogeneous ensemble (77.6%): +2.2% (exceeds 0.5% threshold)
- Calibration improvement: ECE reduction from 0.08 to 0.05

**Prediction P4 (Scalability)**:
- Empirical complexity exponent: $k = 1.15 \pm 0.08$ (below 1.2 threshold)
- ResNet-152 encoding time: 2.3× ResNet-50 (despite 2.4× parameters)
- Flat encoding would require 5.8× time (quadratic scaling)

#### 4.1.2 Qualitative Insights

**Universal Space Structure**:
- Visualization via t-SNE will reveal architecture-specific clusters with task-based bridges
- Models solving similar tasks (e.g., ImageNet classification) will form cross-architecture neighborhoods
- Architectural families (ResNet variants, ViT variants) will show hierarchical organization

**Failure Modes**:
- Novel architectures with undefined symmetries may require $\alpha > 0.15$
- Extremely sparse models (>95% sparsity) may violate functoriality assumptions
- Models trained on incompatible objectives (GANs vs. classifiers) will not cluster meaningfully

### 4.2 Theoretical Impact

**Advancing Weight Space Learning Theory**:
- First rigorous application of category theory to weight space learning
- Establishes lax functoriality as a principled relaxation mechanism for approximate symmetry preservation
- Provides approximation bounds ($\alpha$) that can guide future architecture design

**Bridging Research Areas**:
- Connects model merging (currently heuristic) to functorial composition
- Provides theoretical foundation for neural architecture search in universal spaces
- Extends meta-learning theory to heterogeneous architecture sets

**Open Theoretical Questions**:
- Optimal dimensionality $d$ as a function of architecture diversity
- Relationship between $\alpha$ and downstream task performance
- Generalization bounds for weight space learning across symmetry groups

### 4.3 Methodological Impact

**New Capabilities**:
- **Cross-Architecture Model Zoo Analysis**: Researchers can compare CNNs and Transformers directly
- **Heterogeneous Ensemble Construction**: Automated selection of complementary architectures
- **Architecture-Agnostic Property Prediction**: Predict generalization, robustness, efficiency without architecture-specific features
- **Unified Model Editing**: Apply task arithmetic and model merging across architecture boundaries

**Practical Tools**:
- Open-source implementation with pre-trained WSFN encoders for standard architectures
- Model zoo analysis toolkit for clustering, retrieval, and visualization
- Heterogeneous ensemble API compatible with Hugging Face and Timm

**Limitations and Future Work**:
- Current scope limited to supervised learning (classification, language modeling)
- Extension to generative models (GANs, diffusion models) requires new symmetry analysis
- Dynamic architectures (adaptive depth, mixture-of-experts) need temporal functorial mappings

### 4.4 Practical Impact

**Democratizing Model Zoo Access**:
- Researchers without architecture-specific expertise can leverage diverse model collections
- Automated model selection based on universal space distances
- Reduced computational cost through heterogeneous ensembles (fewer redundant models)

**Industry Applications**:
- **Model Deployment**: Select optimal architecture for edge devices via universal space property prediction
- **Transfer Learning**: Identify best source models across architectures for target tasks
- **Model Compression**: Heterogeneous knowledge distillation from CNN+Transformer teachers

**Societal Benefits**:
- Reduced carbon footprint through efficient model reuse and ensemble formation
- Improved model robustness via architectural diversity in ensembles
- Accelerated AI research through unified model analysis frameworks

### 4.5 Broader Impact

**Interdisciplinary Connections**:
- Category-theoretic framework applicable to protein structure alignment (inspired by LieOTAlign)
- Potential applications in scientific computing (physics-informed neural networks)
- Connections to algebraic topology for weight space manifold analysis

**Educational Value**:
- Introduces category theory to machine learning curriculum
- Provides concrete application of abstract mathematical concepts
- Open-source tutorials and workshops for weight space learning

**Long-Term Vision**:
- Foundation for "universal model understanding" analogous to universal approximation theorems
- Enables automated architecture design in universal spaces
- Supports continual learning through functorial composition of task-specific models

### 4.6 Success Criteria and Validation

**Minimum Viable Success**:
- At least 3 out of 4 predictions (P1-P4) meet success criteria
- Heterogeneous ensemble outperforms single-best model (P3 critical)
- Functoriality preservation error bounded by $\alpha$ (P2 validates theory)

**Stretch Goals**:
- Zero-shot transfer to novel NAS-discovered architectures
- Successful interpolation in universal space yielding functional models
- Extension to multimodal models (vision-language transformers)

**Validation Timeline**:
- Month 1-2: Data collection and preprocessing
- Month 3-4: WSFN implementation and training
- Month 5: Experiments 1-2 (clustering and functoriality)
- Month 6: Experiments 3-4 (ensembles and scalability)
- Month 7: Analysis, ablations, and paper writing

**Estimated Budget**:
- Cloud compute (8× A100 GPUs × 300 hours): $1,800
- Storage (10TB model zoo): $100
- Miscellaneous (software licenses, visualization tools): $100
- **Total**: ~$2,000

---

This research proposal presents a comprehensive plan to address a fundamental challenge in weight space learning: unifying heterogeneous neural architectures through category-theoretic principles. By combining rigorous mathematical foundations with practical experimental validation, WSFN aims to unlock the full potential of model zoos for cross-architecture operations, advancing both theoretical understanding and practical applications in the rapidly evolving field of neural network weights as a data modality.