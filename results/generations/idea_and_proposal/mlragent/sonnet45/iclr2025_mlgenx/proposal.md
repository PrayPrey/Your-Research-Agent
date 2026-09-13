# Research Proposal: Causal Gene Circuit Discovery via Differentiable Perturbation Masks and Counterfactual Reasoning

## 1. Title

**Causal Gene Circuit Discovery via Differentiable Perturbation Masks and Counterfactual Reasoning: A Unified Framework for Efficient Therapeutic Target Identification**

## 2. Introduction

### 2.1 Background

Understanding the causal mechanisms underlying gene regulatory networks (GRNs) represents one of the fundamental challenges in modern genomics and drug discovery. While high-throughput sequencing technologies have generated unprecedented volumes of gene expression data, our ability to extract causal relationships from these observations remains limited. This limitation stems from the fundamental challenge of distinguishing correlation from causation in observational data, where confounding factors, feedback loops, and complex regulatory dynamics obscure true causal relationships.

Current approaches to causal discovery in genomics fall into two broad categories. First, purely observational methods leverage correlation structures in single-cell RNA sequencing (scRNA-seq) data to infer regulatory relationships. While computationally efficient and applicable to large datasets, these methods struggle to establish directionality and causality, often producing networks with high false-positive rates. Second, perturbation-based approaches, including CRISPR screens (Perturb-seq, CROP-seq) and pharmacological interventions, provide gold-standard causal evidence by directly manipulating gene expression. However, these experiments are prohibitively expensive, labor-intensive, and can typically only interrogate a limited subset of the perturbation space due to combinatorial explosion.

Recent advances in neural causal discovery, as demonstrated by DiscoGen and PerturbODE, have shown promise in learning causal structures from genomics data. These methods employ deep learning architectures to model gene regulatory dynamics and can incorporate both observational and interventional data. However, significant gaps remain: (1) existing methods lack robust mechanisms for counterfactual reasoning under unseen perturbations, (2) they do not systematically integrate active learning to guide experimental design, and (3) uncertainty quantification in predicted causal relationships remains underdeveloped.

### 2.2 Research Objectives

This research proposes a unified framework that addresses these limitations through three primary objectives:

1. **Develop a differentiable causal discovery architecture** that learns sparse, interpretable gene regulatory circuits by integrating observational scRNA-seq data with sparse perturbation experiments through structured graph neural networks with learnable adjacency matrices.

2. **Implement counterfactual prediction capabilities** that enable the model to predict gene expression profiles under hypothetical interventions, validated against held-out perturbation screens, thereby extending causal inference beyond observed perturbations.

3. **Design an active learning strategy** that recommends optimal next-best perturbation experiments to maximally reduce uncertainty in the causal graph structure, reducing experimental costs while improving network recovery accuracy.

### 2.3 Significance

This research addresses critical needs in both machine learning and genomics. From a methodological perspective, it advances causal representation learning by combining differentiable graph learning, counterfactual reasoning, and active experimental design in a principled framework. For genomics and drug discovery, it promises to:

- **Accelerate target identification** by reducing the number of perturbation experiments needed to establish high-confidence causal relationships by an estimated 50%
- **Improve therapeutic target prioritization** through uncertainty-aware predictions that quantify confidence in proposed interventions
- **Enable rational experimental design** by systematically identifying the most informative perturbations to perform next
- **Bridge the gap** between observational genomics studies and mechanistic understanding required for successful drug development

The framework directly addresses the workshop's focus areas including causal representation learning, perturbation biology, active learning in genomics, and uncertainty quantification, while contributing to the broader goal of integrating machine learning with genomics for drug discovery.

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{G} = (V, E)$ represent a gene regulatory network where $V = \{g_1, ..., g_n\}$ denotes $n$ genes and $E \subseteq V \times V$ represents directed regulatory relationships. We assume access to two types of data:

1. **Observational data**: $\mathcal{D}_{obs} = \{x^{(i)}\}_{i=1}^{N_{obs}}$ where $x^{(i)} \in \mathbb{R}^n$ represents gene expression profiles from $N_{obs}$ cells
2. **Perturbational data**: $\mathcal{D}_{pert} = \{(p^{(j)}, x^{(j)})\}_{j=1}^{N_{pert}}$ where $p^{(j)} \in \{0,1\}^n$ is a perturbation mask indicating which genes are perturbed and $x^{(j)}$ is the resulting expression profile

Our goal is to learn the causal adjacency matrix $A \in \{0,1\}^{n \times n}$ where $A_{ij} = 1$ indicates that gene $g_i$ causally regulates gene $g_j$, while minimizing the number of perturbation experiments required.

### 3.2 Differentiable Perturbation Mask Architecture

#### 3.2.1 Graph Neural Network with Learnable Adjacency

We propose a continuous relaxation of the discrete adjacency matrix through a learnable weight matrix $W \in \mathbb{R}^{n \times n}$. The soft adjacency matrix is obtained via:

$$A_{soft} = \sigma(W) \odot M_{acyclic}$$

where $\sigma(\cdot)$ is the sigmoid function and $M_{acyclic}$ is a mask enforcing acyclicity. To ensure the learned graph is a directed acyclic graph (DAG), we employ the differentiable acyclicity constraint:

$$h(A_{soft}) = \text{tr}(e^{A_{soft} \odot A_{soft}}) - n = 0$$

This constraint, introduced in NOTEARS, penalizes cycles by ensuring the matrix exponential's trace equals the dimension.

#### 3.2.2 Gene Expression Propagation Model

Given the soft adjacency matrix, we model gene expression dynamics using a graph convolutional architecture:

$$h^{(l+1)} = \phi\left(A_{soft}^T h^{(l)} W^{(l)} + b^{(l)}\right)$$

where $h^{(0)} = x$ is the input expression, $W^{(l)}$ are layer-specific parameters, and $\phi(\cdot)$ is a non-linear activation (ELU). For perturbation data, we modify the propagation:

$$h^{(l+1)}_{pert} = \phi\left(A_{soft}^T (h^{(l)} \odot (1-p) + p \odot z_{pert}) W^{(l)} + b^{(l)}\right)$$

where $z_{pert}$ represents the intervention value (typically 0 for knockouts or learned embeddings for overexpression).

#### 3.2.3 Structured Sparsity Regularization

To encourage sparse, interpretable networks, we employ a combination of L1 and group sparsity penalties:

$$\mathcal{L}_{sparse} = \lambda_1 \|A_{soft}\|_1 + \lambda_2 \sum_{i=1}^n \sqrt{\sum_{j=1}^n A_{soft,ij}^2}$$

The first term encourages overall sparsity while the second (group Lasso) encourages genes to have few regulators.

### 3.3 Counterfactual Prediction Module

#### 3.3.1 Structural Causal Model Formulation

We frame gene expression as a structural causal model where each gene's expression is determined by:

$$x_j = f_j(\text{pa}(g_j), u_j)$$

where $\text{pa}(g_j)$ are the parents of gene $g_j$ in the causal graph, $f_j$ is a potentially non-linear function learned by the network, and $u_j$ represents unobserved confounders.

For a counterfactual intervention $\text{do}(g_k = v)$, we predict the resulting expression profile by:

1. **Abduction**: Infer the latent variables $u$ from observed data $x$
2. **Action**: Modify the graph by removing incoming edges to $g_k$ and fixing $x_k = v$
3. **Prediction**: Propagate the intervention through the modified graph

#### 3.3.2 Variational Inference for Unobserved Confounders

We model unobserved confounders through a variational autoencoder:

$$q_\phi(u|x) = \mathcal{N}(u; \mu_\phi(x), \Sigma_\phi(x))$$

The counterfactual prediction for intervention $\text{do}(g_k = v)$ is computed as:

$$\hat{x}_{CF} = \mathbb{E}_{u \sim q_\phi(u|x_{obs})}\left[f_\theta(u, x_k=v, A_{soft})\right]$$

where $f_\theta$ is the forward propagation through the GNN with modified adjacency.

#### 3.3.3 Counterfactual Loss

We train the counterfactual module using held-out perturbation data:

$$\mathcal{L}_{CF} = \sum_{(p,x) \in \mathcal{D}_{pert}^{val}} \|\hat{x}_{CF}(p) - x\|_2^2$$

### 3.4 Active Learning for Optimal Experimental Design

#### 3.4.1 Uncertainty Quantification via Bayesian Neural Networks

We employ Monte Carlo dropout to approximate Bayesian uncertainty in both the adjacency matrix and predictions:

$$\text{Var}(A_{ij}) \approx \frac{1}{T}\sum_{t=1}^T (A_{soft}^{(t)}_{ij} - \bar{A}_{ij})^2$$

where $A_{soft}^{(t)}$ is obtained from forward passes with different dropout masks.

Additionally, we maintain an ensemble of $K$ models trained with different initializations to capture epistemic uncertainty:

$$\text{Unc}(A_{ij}) = \frac{1}{K}\sum_{k=1}^K \text{Var}_k(A_{ij}) + \text{Var}\left(\{\mathbb{E}_k[A_{ij}]\}_{k=1}^K\right)$$

#### 3.4.2 Acquisition Function for Perturbation Selection

We design an acquisition function that balances information gain about the causal structure with experimental feasibility:

$$\alpha(p) = \underbrace{\mathbb{E}_{A \sim q(A|D)}[H(X|p, A)] - H(X|p, \mathcal{D})}_{\text{Expected Information Gain}} - \underbrace{\lambda_{cost} \cdot c(p)}_{\text{Experimental Cost}}$$

where $H(\cdot)$ is entropy, and $c(p)$ is the cost of perturbation $p$ (e.g., number of simultaneously perturbed genes).

For computational tractability, we approximate this using:

$$\alpha(p) \approx \sum_{i,j} \text{Unc}(A_{ij}) \cdot |\frac{\partial A_{ij}}{\partial x}|_{x=\hat{x}_{CF}(p)} - \lambda_{cost} \|p\|_0$$

This prioritizes perturbations that affect edges with high uncertainty and have strong influence on the network structure.

#### 3.4.3 Active Learning Algorithm

The complete active learning loop:

**Algorithm 1: Active Causal Discovery**
```
Input: Initial observational data D_obs, budget B, batch size b
Initialize: Train model on D_obs → θ_0
for iteration t = 1 to B/b do:
    1. Compute uncertainty Unc(A_ij) for all edges
    2. Evaluate acquisition function α(p) for candidate perturbations
    3. Select top-b perturbations: P_t = argmax_P |P|=b Σ_{p∈P} α(p)
    4. Perform experiments and obtain D_new
    5. Update dataset: D ← D ∪ D_new
    6. Retrain model: θ_t ← optimize(D, θ_{t-1})
    7. Update counterfactual predictions and uncertainty estimates
end
Output: Causal adjacency matrix A, uncertainty estimates
```

### 3.5 Training Procedure

The complete objective function combines multiple losses:

$$\mathcal{L}_{total} = \mathcal{L}_{recon} + \beta \mathcal{L}_{CF} + \lambda_{dag} h(A_{soft})^2 + \mathcal{L}_{sparse} + \mathcal{L}_{KL}$$

where:
- $\mathcal{L}_{recon} = \sum_{x \in \mathcal{D}_{obs}} \|f_\theta(x, A_{soft}) - x\|_2^2$ is the reconstruction loss
- $\mathcal{L}_{CF}$ is the counterfactual prediction loss
- $\mathcal{L}_{KL}$ is the KL divergence for the variational inference of confounders

We employ a two-stage training strategy:
1. **Stage 1**: Pre-train on observational data with heavy DAG constraint ($\lambda_{dag} = 1.0$)
2. **Stage 2**: Fine-tune with perturbation data, gradually reducing $\lambda_{dag}$ while increasing $\beta$

### 3.6 Data Collection and Experimental Setup

#### 3.6.1 Datasets

We will validate our approach on three benchmark datasets:

1. **Perturb-seq (Dixit et al.)**: ~200,000 single cells with ~2,800 genes, covering perturbations of 24 transcription factors
2. **CROP-seq (Datlinger et al.)**: Single-cell perturbation screens with known ground-truth regulatory relationships
3. **Synthetic Networks**: Simulated GRNs using GeneNetWeaver with varying network sizes (100-1000 genes) and known ground truth

#### 3.6.2 Evaluation Metrics

We will evaluate our method using:

1. **Causal Discovery Accuracy**:
   - AUROC and AUPRC for edge prediction
   - Structural Hamming Distance (SHD) to ground truth
   - F1 score for predicted edges

2. **Counterfactual Prediction**:
   - Mean Squared Error (MSE) on held-out perturbations
   - Pearson correlation between predicted and actual expression changes
   - Cell-type-specific prediction accuracy

3. **Active Learning Efficiency**:
   - Number of perturbations needed to reach target accuracy (e.g., F1 > 0.8)
   - Information gain per experiment
   - Comparison against random selection and uncertainty sampling baselines

4. **Uncertainty Calibration**:
   - Expected Calibration Error (ECE)
   - Correlation between predicted uncertainty and prediction error

#### 3.6.3 Baseline Comparisons

We will compare against:
- **Classical methods**: PC algorithm, GES, GIES
- **Recent neural methods**: DiscoGen, PerturbODE
- **Active learning baselines**: Random selection, maximum entropy, Expected Model Change
- **Counterfactual baselines**: CausalGAN, Deep Structural Causal Models

#### 3.6.4 Ablation Studies

To assess the contribution of each component:
1. Model without counterfactual module
2. Model without active learning
3. Different sparsity regularization schemes
4. Impact of DAG constraint strength
5. Ensemble size effect on uncertainty quantification

### 3.7 Implementation Details

- **Framework**: PyTorch with PyTorch Geometric for graph operations
- **Architecture**: 3-layer GNN with 128 hidden units, ELU activation, dropout rate 0.1
- **Optimization**: Adam optimizer with learning rate 1e-3, cosine annealing schedule
- **Hardware**: Training on NVIDIA A100 GPUs with mixed precision
- **Reproducibility**: All experiments with 5 random seeds, code released on GitHub

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

This research is expected to yield several significant outcomes:

**1. Methodological Contributions:**
- A novel neural architecture that seamlessly integrates observational and perturbational genomics data for causal discovery
- Theoretical guarantees on identifiability conditions under which the causal graph can be uniquely recovered
- Scalable algorithms for counterfactual reasoning in high-dimensional gene expression spaces
- Active learning strategies specifically designed for experimental design in perturbation biology

**2. Quantitative Performance Targets:**
- **50% reduction** in perturbation experiments needed to achieve equivalent causal discovery accuracy compared to random experimental design
- **AUROC > 0.85** for edge prediction on benchmark datasets with sparse perturbation coverage (<10% of possible perturbations)
- **Pearson r > 0.80** for counterfactual predictions on held-out perturbations
- **Expected Calibration Error < 0.1** for uncertainty estimates

**3. Biological Insights:**
- Recovery of known regulatory relationships in well-characterized pathways (e.g., p53, NF-κB signaling)
- Prediction of novel regulatory connections validated through orthogonal experimental techniques
- Cell-type-specific causal networks revealing context-dependent regulatory mechanisms
- Prioritized lists of therapeutic targets with quantified intervention uncertainty

### 4.2 Scientific Impact

**For Machine Learning Research:**
- Advances the field of causal representation learning by demonstrating how differentiable programming, counterfactual reasoning, and active learning can be unified in a principled framework
- Provides new benchmarks for evaluating causal discovery methods in high-dimensional, biological settings
- Contributes to the theoretical understanding of identifiability in causal discovery from mixed observational-interventional data
- Opens new research directions in uncertainty-aware experimental design for scientific discovery

**For Genomics and Drug Discovery:**
- **Accelerated target identification**: Reducing experimental costs by 50% translates to millions of dollars saved and months shortened in early-stage drug discovery pipelines
- **Improved success rates**: Higher confidence causal relationships should reduce clinical trial failures due to invalid target hypotheses
- **Rational combination therapy design**: Counterfactual predictions enable systematic exploration of multi-target interventions
- **Personalized medicine**: Cell-type and patient-specific causal networks can inform precision therapy selection

**For Experimental Biology:**
- Provides experimentalists with interpretable, uncertainty-quantified recommendations for which perturbations to perform next
- Enables systematic exploration of combinatorial perturbation spaces that are intractable with brute-force screening
- Facilitates hypothesis generation by predicting consequences of interventions before expensive experiments
- Bridges computational predictions with wet-lab validation through active learning cycles

### 4.3 Broader Impacts

**Reproducibility and Open Science:**
All code, trained models, and processed datasets will be released under open-source licenses. We will provide detailed documentation, tutorials, and Jupyter notebooks to enable researchers without deep machine learning expertise to apply our methods.

**Education and Training:**
This research will train graduate students at the intersection of machine learning and biology, addressing the critical shortage of researchers with interdisciplinary expertise. Course materials developed from this work will be shared with the community.

**Ethical Considerations:**
We acknowledge potential concerns about AI-driven biological discovery:
- **Dual-use concerns**: Gene regulatory knowledge could potentially be misused; we will engage with biosafety experts and follow responsible disclosure practices
- **Validation requirements**: We emphasize that computational predictions must be experimentally validated before clinical application
- **Equity**: We commit to making methods accessible to researchers in resource-limited settings through efficient implementations and cloud-based tools

**Clinical Translation:**
While this research focuses on basic methodology, we anticipate long-term clinical impact through:
- Identification of novel therapeutic targets for diseases with unmet medical needs
- Repurposing existing drugs based on predicted regulatory mechanisms
- Stratification of patients based on causal network architectures for precision medicine

### 4.4 Future Directions

This research establishes a foundation for several promising extensions:

1. **Multi-modal integration**: Extending the framework to incorporate protein expression, chromatin accessibility, and spatial transcriptomics data
2. **Temporal dynamics**: Modeling time-series perturbation responses to infer dynamic causal relationships
3. **Transfer learning**: Leveraging causal structures learned in model organisms to accelerate discovery in human systems
4. **Combinatorial perturbations**: Scaling counterfactual prediction to multi-gene interventions and drug combinations
5. **Foundation models**: Pre-training on large-scale perturbation atlases to create general-purpose causal reasoning engines for genomics

By addressing the fundamental challenge of causal discovery in genomics through a principled integration of differentiable programming, counterfactual reasoning, and active learning, this research promises to accelerate the path from genomic observations to therapeutic interventions, ultimately improving human health.