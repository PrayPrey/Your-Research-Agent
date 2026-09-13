# Research Proposal: Active Learning with Uncertainty-Guided Perturbation Selection for Efficient Gene Function Discovery

## 1. Introduction

### Background

Understanding gene function and identifying therapeutic targets remain fundamental challenges in modern biomedical research. Perturbation biology, particularly CRISPR-based genetic screens coupled with single-cell transcriptomics (Perturb-seq), has emerged as a powerful approach for systematically interrogating gene function at scale. These experiments enable researchers to observe the transcriptional consequences of knocking out or modifying specific genes, providing crucial insights into gene regulatory networks and potential drug targets. However, the combinatorial space of possible perturbations is vast—the human genome contains approximately 20,000 protein-coding genes, and when considering combinations, genetic backgrounds, and cellular contexts, the experimental space becomes prohibitively expensive to explore exhaustively.

Current experimental design strategies in perturbation biology often rely on random selection, literature-based prioritization, or simple heuristics that fail to account for the complex, context-dependent nature of gene interactions. This inefficiency represents a critical bottleneck in drug discovery, where the cost of a single large-scale Perturb-seq experiment can exceed hundreds of thousands of dollars. Moreover, the failure to identify optimal targets early in the discovery process contributes to the high attrition rates observed in clinical trials.

Recent advances in foundation models for genomics have demonstrated remarkable capabilities in learning representations from large-scale biological data. Simultaneously, Bayesian deep learning methods have matured to provide principled uncertainty quantification in complex prediction tasks. The convergence of these technologies presents an unprecedented opportunity to develop intelligent experimental design strategies that can dramatically improve the efficiency of gene function discovery.

### Research Objectives

This research proposes to develop an uncertainty-aware active learning framework that integrates genomic foundation models with Bayesian deep learning to guide the iterative selection of perturbation experiments. Our specific objectives are:

1. To develop a neural ensemble architecture that leverages pre-trained genomic foundation models for predicting transcriptional outcomes of genetic perturbations while providing calibrated uncertainty estimates.

2. To design novel acquisition functions that decompose predictive uncertainty into epistemic and aleatoric components, enabling intelligent prioritization of experiments that maximize information gain.

3. To incorporate diversity-promoting mechanisms that balance exploration of uncertain genomic regions with exploitation of promising therapeutic target candidates.

4. To validate the framework on large-scale Perturb-seq datasets and demonstrate its applicability to real-world drug discovery pipelines.

### Significance

This research addresses a critical gap at the intersection of machine learning and genomics with direct implications for drug discovery. By reducing the number of experiments required to achieve comprehensive gene function understanding by 2-3x, our approach could save millions of dollars in experimental costs while accelerating the identification of novel therapeutic targets. Furthermore, the principled uncertainty quantification framework will provide researchers with actionable confidence estimates, enabling more informed decision-making in target prioritization. The proposed methodology is broadly applicable across perturbation modalities, cellular contexts, and disease areas, positioning it as a foundational tool for modern genomics research.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{G} = \{g_1, g_2, ..., g_N\}$ denote the set of $N$ genes under consideration for perturbation. For each perturbation $g_i$, the experimental outcome is a high-dimensional transcriptional response vector $\mathbf{y}_i \in \mathbb{R}^M$, where $M$ represents the number of measured genes. We define the labeled dataset at iteration $t$ as $\mathcal{D}_t = \{(g_i, \mathbf{y}_i)\}_{i=1}^{n_t}$, where $n_t$ denotes the number of perturbations experimentally characterized by iteration $t$. The goal is to develop a selection strategy $\pi: \mathcal{G} \setminus \mathcal{D}_t \rightarrow g^*$ that identifies the next perturbation $g^*$ to experimentally characterize, maximizing cumulative information gain while minimizing the total number of experiments.

### 2.2 Model Architecture

#### Foundation Model Integration

We build upon pre-trained genomic foundation models (e.g., scGPT, Geneformer) to leverage learned representations of gene-gene relationships. For each gene $g_i$, we extract a foundation model embedding $\mathbf{h}_i = f_\theta(g_i) \in \mathbb{R}^d$, where $f_\theta$ represents the pre-trained encoder. These embeddings capture rich biological context including gene regulatory relationships, pathway memberships, and expression patterns across cellular contexts.

#### Ensemble Prediction Network

We construct an ensemble of $K$ neural networks $\{p_{\phi_k}(\mathbf{y}|g)\}_{k=1}^K$ to predict transcriptional outcomes from gene embeddings. Each network $k$ consists of:

$$\mathbf{z}_k = \text{MLP}_k(\mathbf{h}_i; \phi_k)$$
$$p_{\phi_k}(\mathbf{y}|g_i) = \mathcal{N}(\boldsymbol{\mu}_k(\mathbf{z}_k), \text{diag}(\boldsymbol{\sigma}_k^2(\mathbf{z}_k)))$$

where $\boldsymbol{\mu}_k$ and $\boldsymbol{\sigma}_k^2$ are output heads predicting the mean and variance of the Gaussian likelihood. The networks are trained with diverse initializations and dropout configurations to promote ensemble diversity.

The training objective for each network combines negative log-likelihood with a regularization term:

$$\mathcal{L}_k(\phi_k) = -\sum_{(g_i, \mathbf{y}_i) \in \mathcal{D}_t} \log p_{\phi_k}(\mathbf{y}_i|g_i) + \lambda \|\phi_k\|_2^2$$

### 2.3 Uncertainty Decomposition

We decompose total predictive uncertainty into epistemic (model) and aleatoric (data) components following established Bayesian principles.

**Total Predictive Uncertainty**: For a gene $g$ with ensemble predictions, the total variance is:

$$\text{Var}[\mathbf{y}|g] = \underbrace{\frac{1}{K}\sum_{k=1}^K \boldsymbol{\sigma}_k^2(g)}_{\text{Aleatoric}} + \underbrace{\frac{1}{K}\sum_{k=1}^K (\boldsymbol{\mu}_k(g) - \bar{\boldsymbol{\mu}}(g))^2}_{\text{Epistemic}}$$

where $\bar{\boldsymbol{\mu}}(g) = \frac{1}{K}\sum_{k=1}^K \boldsymbol{\mu}_k(g)$ is the ensemble mean prediction.

**Epistemic Uncertainty Score**: We compute a scalar epistemic uncertainty score for each gene:

$$u_{\text{epistemic}}(g) = \frac{1}{M}\sum_{j=1}^M \frac{1}{K}\sum_{k=1}^K (\mu_{k,j}(g) - \bar{\mu}_j(g))^2$$

This score quantifies disagreement among ensemble members and identifies genes where additional data would most reduce model uncertainty.

### 2.4 Diversity-Promoting Acquisition Function

To balance uncertainty-driven exploration with strategic exploitation, we propose a composite acquisition function incorporating three components:

**Information Gain Component**: Prioritizes genes with high epistemic uncertainty:

$$a_{\text{info}}(g) = u_{\text{epistemic}}(g)$$

**Target Relevance Component**: Incorporates prior knowledge about target relevance using a relevance scoring function $r(g)$ based on pathway annotations, disease associations, or druggability scores:

$$a_{\text{relevance}}(g) = r(g) \cdot \|\bar{\boldsymbol{\mu}}(g) - \mathbf{y}_{\text{control}}\|_2$$

where $\mathbf{y}_{\text{control}}$ represents the control (unperturbed) expression profile.

**Diversity Component**: Promotes coverage of the gene embedding space using determinantal point processes (DPP). For a candidate batch $\mathcal{B}$:

$$a_{\text{diversity}}(\mathcal{B}) = \det(\mathbf{L}_\mathcal{B})$$

where $\mathbf{L}_\mathcal{B}$ is the kernel matrix with entries $L_{ij} = \mathbf{h}_i^\top \mathbf{h}_j \cdot \sqrt{a_{\text{info}}(g_i) \cdot a_{\text{info}}(g_j)}$.

**Composite Acquisition Function**: The final batch selection optimizes:

$$\mathcal{B}^* = \arg\max_{\mathcal{B} \subset \mathcal{G} \setminus \mathcal{D}_t, |\mathcal{B}|=b} \left[\alpha \sum_{g \in \mathcal{B}} a_{\text{info}}(g) + \beta \sum_{g \in \mathcal{B}} a_{\text{relevance}}(g) + \gamma \log \det(\mathbf{L}_\mathcal{B})\right]$$

where $\alpha, \beta, \gamma$ are hyperparameters controlling the trade-off between exploration, exploitation, and diversity, and $b$ is the batch size.

### 2.5 Active Learning Algorithm

The complete active learning procedure is summarized as follows:

**Algorithm: Uncertainty-Guided Perturbation Selection**

1. **Input**: Initial labeled dataset $\mathcal{D}_0$, gene set $\mathcal{G}$, budget $T$, batch size $b$
2. **Initialize**: Train ensemble $\{p_{\phi_k}\}_{k=1}^K$ on $\mathcal{D}_0$
3. **For** $t = 1, 2, ..., T/b$:
   - Compute epistemic uncertainty $u_{\text{epistemic}}(g)$ for all $g \in \mathcal{G} \setminus \mathcal{D}_{t-1}$
   - Compute relevance scores $a_{\text{relevance}}(g)$
   - Select batch $\mathcal{B}^*$ using greedy submodular maximization of composite acquisition function
   - Perform experiments: Obtain $\{(g, \mathbf{y}_g)\}_{g \in \mathcal{B}^*}$
   - Update dataset: $\mathcal{D}_t = \mathcal{D}_{t-1} \cup \{(g, \mathbf{y}_g)\}_{g \in \mathcal{B}^*}$
   - Retrain ensemble on $\mathcal{D}_t$
4. **Output**: Final model and labeled dataset $\mathcal{D}_T$

### 2.6 Data Collection and Experimental Design

**Datasets**: We will utilize publicly available large-scale Perturb-seq datasets:
- **Replogle et al. (2022)**: Genome-wide CRISPR screen in K562 cells (~10,000 perturbations)
- **Norman et al. (2019)**: Combinatorial CRISPR screen (~300 perturbations)
- **Dixit et al. (2016)**: Initial Perturb-seq dataset (~100 perturbations)

**Experimental Validation Protocol**:

1. **Simulated Active Learning**: We partition datasets into training (10%), pool (70%), and test (20%) sets. The active learning algorithm iteratively selects batches from the pool, simulating experimental acquisition.

2. **Evaluation Metrics**:
   - **Prediction Performance**: Mean squared error (MSE) and Pearson correlation on held-out test perturbations
   - **Sample Efficiency**: Area under the learning curve (AULC) measuring performance vs. number of experiments
   - **Uncertainty Calibration**: Expected calibration error (ECE) for uncertainty estimates
   - **Target Identification**: Precision@k for identifying essential genes and known drug targets

3. **Baselines**:
   - Random selection
   - Uncertainty sampling (standard)
   - Graph-based selection (Panagopoulos et al., 2025)
   - Coreset selection
   - Maximum entropy sampling

4. **Ablation Studies**: We will systematically evaluate the contribution of each component (epistemic uncertainty, relevance scoring, diversity promotion) through ablation experiments.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Sample Efficiency**: We anticipate achieving 2-3x reduction in the number of perturbation experiments required to reach equivalent prediction accuracy compared to random selection baselines. Specifically, we expect to match the performance of random selection at 100% data using only 30-50% of experiments.

2. **Calibrated Uncertainty Estimates**: The ensemble framework will provide well-calibrated uncertainty estimates with expected calibration error (ECE) below 0.05, enabling researchers to make informed decisions about prediction reliability.

3. **Enhanced Target Identification**: We expect significant improvement in identifying high-value therapeutic targets, measured by 20-30% improvement in Precision@50 for essential gene identification compared to non-uncertainty-guided approaches.

4. **Open-Source Framework**: We will release a comprehensive software package including pre-trained models, acquisition functions, and integration with standard genomics workflows.

### Scientific Impact

This research will advance the field of machine learning for genomics by:

1. **Establishing Best Practices**: Providing a rigorous framework for uncertainty quantification in genomic prediction tasks, addressing a key challenge identified in the literature.

2. **Bridging Computational and Experimental Biology**: Creating a practical pipeline that directly interfaces with experimental workflows, facilitating adoption by biology laboratories.

3. **Enabling New Discoveries**: By making perturbation screens more efficient, enabling researchers to explore previously intractable experimental spaces and accelerate the discovery of novel gene functions and therapeutic targets.

### Broader Impact

The proposed framework has direct applications in drug discovery pipelines, potentially reducing the time and cost of target identification by enabling more strategic experimental designs. This is particularly relevant for rare diseases and precision medicine applications where experimental resources are limited. Furthermore, the uncertainty quantification methodology is transferable to other domains of experimental biology, including protein engineering, synthetic biology, and drug screening campaigns.

In conclusion, this research addresses a critical need at the intersection of machine learning and genomics, with the potential to fundamentally transform how perturbation experiments are designed and executed in modern biomedical research.