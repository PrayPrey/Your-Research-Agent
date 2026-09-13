# Research Proposal: Causal Perturbation Modeling for Biologically Meaningful Representation Learning

## 1. Title

**Causal Perturbation Modeling for Biologically Meaningful Representation Learning: A Multi-Scale Framework for Interpretable Biological Foundation Models**

## 2. Introduction

### 2.1 Background

The rapid advancement of biological foundation models has been driven by the availability of large-scale datasets spanning genomics, proteomics, and cellular imaging. Models such as those trained on JUMP-CP, RxRx3, and Human Cell Atlas data have demonstrated impressive performance on reconstruction and prediction tasks. However, a critical limitation persists: these models primarily capture correlational patterns rather than causal mechanisms underlying biological processes. This distinction becomes particularly problematic when models are deployed for drug discovery, virtual cell simulation, or predicting responses to novel perturbations—scenarios where understanding causal relationships is paramount.

Current representation learning approaches in biology typically optimize objectives such as masked autoencoding, contrastive learning, or next-token prediction. While these methods excel at capturing statistical regularities in data, they often fail to encode the intervention-response relationships that govern cellular behavior. For instance, a model trained to reconstruct cell morphology images may learn to associate certain visual features with drug treatments without understanding the causal pathway through which the drug produces those effects. This limitation manifests as poor generalization to unseen perturbations, inability to predict combinatorial interventions, and lack of interpretability in terms of biological mechanisms.

The field of causal representation learning has made significant theoretical progress, establishing conditions under which causal factors can be identified from observational and interventional data. However, these advances have seen limited application to biological foundation models, where the complexity of multi-scale interactions—from molecular binding to phenotypic outcomes—presents unique challenges and opportunities.

### 2.2 Research Objectives

This research proposes a novel framework for learning biologically meaningful representations by explicitly incorporating perturbation modeling and causal reasoning into the pre-training process. Our primary objectives are:

1. **Develop a causal perturbation modeling framework** that integrates perturbation prediction, counterfactual reasoning, and multi-scale consistency constraints into foundation model pre-training.

2. **Create perturbation-aware architectures** that can disentangle causal factors underlying cellular responses while maintaining computational efficiency for large-scale datasets.

3. **Establish comprehensive evaluation protocols** that assess both causal validity (perturbation prediction, pathway recovery) and practical utility (downstream task performance, cross-dataset generalization).

4. **Demonstrate superior generalization** to novel perturbations, combinatorial interventions, and cross-dataset transfer compared to reconstruction-based baselines.

### 2.3 Research Significance

This research addresses a fundamental gap in biological representation learning by bridging causal inference and deep learning. The significance of this work spans multiple dimensions:

**Scientific Impact**: By encoding causal mechanisms, the learned representations will provide interpretable insights into biological pathways, enabling researchers to generate testable hypotheses about cellular responses to perturbations. This addresses the LMRL workshop's core question of what constitutes "meaningful" representations.

**Practical Applications**: For drug discovery, models that understand causal mechanisms can more reliably predict off-target effects, drug combinations, and patient-specific responses. For virtual cell simulation, causal representations enable accurate in-silico experimentation with novel interventions.

**Methodological Contributions**: The framework establishes a new paradigm for biological foundation models, demonstrating how domain knowledge about perturbations can be systematically incorporated into self-supervised learning objectives. This approach is generalizable across modalities (genomics, imaging, proteomics) and scales (molecular to organismal).

**Benchmarking and Standardization**: By developing rigorous evaluation protocols for causal validity, this work contributes to the LMRL community's goal of establishing standardized metrics for assessing representation quality beyond traditional downstream task performance.

## 3. Methodology

### 3.1 Data Collection and Preparation

#### 3.1.1 Primary Datasets

We will utilize three complementary large-scale perturbation datasets:

**JUMP-CP (Joint Undertaking in Morphological Profiling - Cell Painting)**: Contains over 100,000 chemical and genetic perturbations with high-content imaging across multiple cell lines. We will use the Cell Painting features (1,783 morphological features) and raw images.

**Perturb-seq**: Single-cell RNA sequencing data with CRISPR-based genetic perturbations, providing transcriptomic profiles for thousands of gene knockdowns across multiple cell types.

**L1000**: Gene expression profiles for ~40,000 chemical perturbations, enabling cross-modal validation.

#### 3.1.2 Data Preprocessing

For each dataset, we will:
- Normalize features using robust scaling to handle batch effects
- Filter perturbations with sufficient replicates (minimum 3) for reliable effect estimation
- Create train/validation/test splits ensuring perturbation-level separation (80/10/10)
- Construct held-out sets for: (a) unseen perturbations, (b) unseen combinations, (c) cross-dataset transfer

### 3.2 Causal Perturbation Modeling Framework

#### 3.2.1 Theoretical Foundation

Let $\mathbf{x} \in \mathbb{R}^d$ represent a biological observation (e.g., cell image, gene expression profile), and $\mathbf{z} \in \mathbb{R}^k$ represent the underlying causal factors. We model perturbations as interventions $do(Z_i = z_i')$ that modify specific causal factors.

Our framework assumes a structural causal model:
$$\mathbf{z} = f(\mathbf{u}, \epsilon_z)$$
$$\mathbf{x} = g(\mathbf{z}, \epsilon_x)$$

where $\mathbf{u}$ represents perturbation variables, $f$ captures the causal mechanism by which perturbations affect latent factors, and $g$ is the observation function.

#### 3.2.2 Architecture Design

We propose a **Causal Perturbation Encoder (CPE)** with three key components:

**Base Encoder** $E_\theta$: Maps observations to representations
$$\mathbf{h} = E_\theta(\mathbf{x})$$

For imaging data, we use a Vision Transformer (ViT) backbone; for gene expression, a transformer encoder with gene-wise embeddings.

**Perturbation Disentanglement Module**: Decomposes representations into perturbation-sensitive and invariant components:
$$\mathbf{h} = [\mathbf{h}^{inv}, \mathbf{h}^{pert}]$$

where $\mathbf{h}^{inv}$ captures cell-intrinsic properties and $\mathbf{h}^{pert}$ captures perturbation effects.

**Causal Prediction Head**: Predicts perturbation effects and counterfactuals:
$$\hat{\mathbf{u}} = P_\phi(\mathbf{h}^{pert})$$
$$\hat{\mathbf{x}}_{cf} = D_\psi(\mathbf{h}^{inv}, \mathbf{h}'^{pert})$$

### 3.3 Training Objectives

Our multi-objective training combines three complementary losses:

#### 3.3.1 Perturbation Prediction Loss

$$\mathcal{L}_{pert} = \mathbb{E}_{(\mathbf{x}, \mathbf{u})} \left[ \ell(P_\phi(E_\theta(\mathbf{x})^{pert}), \mathbf{u}) \right]$$

where $\ell$ is cross-entropy for discrete perturbations (gene knockdowns) or contrastive loss for continuous perturbations (drug concentrations).

#### 3.3.2 Counterfactual Consistency Loss

For paired samples $(\mathbf{x}_i, \mathbf{u}_i)$ and $(\mathbf{x}_j, \mathbf{u}_j)$ from the same cell state:

$$\mathcal{L}_{cf} = \mathbb{E} \left[ \|\mathbf{h}_i^{inv} - \mathbf{h}_j^{inv}\|_2^2 + \lambda_{swap} \|\mathbf{x}_j - D_\psi(\mathbf{h}_i^{inv}, \mathbf{h}_j^{pert})\|_2^2 \right]$$

This encourages disentanglement by enforcing that swapping perturbation components reconstructs the target observation.

#### 3.3.3 Multi-Scale Consistency Loss

To align molecular and phenotypic effects, we introduce a cross-modal consistency constraint:

$$\mathcal{L}_{scale} = \mathbb{E}_{(\mathbf{x}^{img}, \mathbf{x}^{expr}, \mathbf{u})} \left[ \|E_\theta^{img}(\mathbf{x}^{img})^{pert} - E_\theta^{expr}(\mathbf{x}^{expr})^{pert}\|_2^2 \right]$$

for matched image-expression pairs under the same perturbation.

#### 3.3.4 Combined Objective

$$\mathcal{L}_{total} = \mathcal{L}_{pert} + \alpha \mathcal{L}_{cf} + \beta \mathcal{L}_{scale} + \gamma \mathcal{L}_{recon}$$

where $\mathcal{L}_{recon}$ is a standard reconstruction loss (masked autoencoding) to maintain representation quality, and $\alpha, \beta, \gamma$ are hyperparameters.

### 3.4 Experimental Design

#### 3.4.1 Training Protocol

**Phase 1: Single-Modal Pre-training** (4 weeks on 8 A100 GPUs)
- Train separate encoders on JUMP-CP (imaging) and Perturb-seq (expression)
- Batch size: 256, Learning rate: 1e-4 with cosine decay
- Optimize $\mathcal{L}_{pert} + \alpha \mathcal{L}_{cf} + \gamma \mathcal{L}_{recon}$

**Phase 2: Multi-Modal Alignment** (2 weeks)
- Fine-tune on matched image-expression pairs
- Add $\mathcal{L}_{scale}$ to align modalities
- Smaller learning rate: 1e-5

**Phase 3: Downstream Adaptation** (1 week per task)
- Freeze encoder, train task-specific heads
- Evaluate on diverse downstream tasks

#### 3.4.2 Baseline Comparisons

We will compare against:
1. **Masked Autoencoder (MAE)**: Standard reconstruction-based pre-training
2. **Contrastive Learning**: SimCLR-style approach with perturbation augmentations
3. **Supervised Perturbation Prediction**: Direct classification without disentanglement
4. **Existing Foundation Models**: scGPT (for expression), CellViT (for imaging)

### 3.5 Evaluation Metrics

#### 3.5.1 Causal Validity Metrics

**Perturbation Prediction Accuracy**: Classification accuracy for held-out perturbations
$$\text{Acc}_{pert} = \frac{1}{N} \sum_{i=1}^N \mathbb{1}[\arg\max P_\phi(\mathbf{h}_i^{pert}) = \mathbf{u}_i]$$

**Pathway Recovery Score**: Ability to cluster perturbations by known biological pathways using adjusted Rand index (ARI) on perturbation embeddings.

**Counterfactual Prediction Error**: For test samples with known perturbation swaps:
$$\text{CPE} = \mathbb{E}\left[\|\mathbf{x}_{true}(\mathbf{u}') - \hat{\mathbf{x}}_{cf}(\mathbf{u}')\|_2\right]$$

**Disentanglement Score**: Mutual Information Gap (MIG) measuring how well individual latent dimensions correspond to perturbation factors.

#### 3.5.2 Generalization Metrics

**Unseen Perturbation Transfer**: Performance on perturbations excluded from training
- Zero-shot prediction accuracy
- Few-shot adaptation efficiency (1, 5, 10 examples)

**Combinatorial Perturbation Prediction**: For double knockdowns or drug combinations:
$$\text{Combo-R}^2 = 1 - \frac{\sum(\mathbf{x}_{combo} - \hat{\mathbf{x}}_{combo})^2}{\sum(\mathbf{x}_{combo} - \bar{\mathbf{x}})^2}$$

**Cross-Dataset Transfer**: Train on JUMP-CP, evaluate on L1000 and vice versa
- Spearman correlation of predicted vs. observed effects
- Top-k retrieval accuracy for similar perturbations

#### 3.5.3 Downstream Task Performance

**Drug-Target Prediction**: Binary classification of compound-target interactions (AUC-ROC)

**Toxicity Prediction**: Multi-class classification on Tox21 benchmark (Balanced Accuracy)

**Cell Type Classification**: Transfer to cell type identification tasks (F1-score)

**Gene Function Prediction**: GO term prediction from perturbation profiles (AUPRC)

### 3.6 Ablation Studies

To validate our design choices, we will conduct systematic ablations:

1. **Objective Components**: Remove $\mathcal{L}_{cf}$, $\mathcal{L}_{scale}$, or $\mathcal{L}_{pert}$ individually
2. **Architecture Variants**: Test without disentanglement module, different backbone sizes
3. **Data Scale**: Train on 10%, 25%, 50%, 100% of data to assess sample efficiency
4. **Perturbation Types**: Evaluate on genetic vs. chemical perturbations separately

### 3.7 Interpretability Analysis

**Attention Visualization**: Analyze which cellular regions/genes the model attends to for specific perturbations

**Latent Space Analysis**: 
- t-SNE/UMAP visualization of perturbation embeddings colored by pathway
- Linear probing to identify which dimensions encode specific biological properties

**Causal Graph Recovery**: Use learned representations to infer gene regulatory networks, compare against ground truth from databases (STRING, KEGG)

**Mechanistic Validation**: For selected perturbations, generate counterfactual predictions and validate against held-out experimental data or literature

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes**:

1. **Superior Perturbation Prediction**: We expect 15-25% improvement in held-out perturbation prediction accuracy compared to reconstruction-based baselines, demonstrating that causal objectives enhance representation quality.

2. **Enhanced Generalization**: Anticipate 30-40% better performance on combinatorial perturbations and cross-dataset transfer, validating that causal representations capture transferable mechanisms.

3. **Interpretable Pathway Recovery**: Achieve ARI > 0.7 for clustering perturbations by biological pathways, compared to ARI < 0.5 for baselines, showing biological meaningfulness.

4. **Competitive Downstream Performance**: Maintain within 5% of state-of-the-art on standard benchmarks while excelling on perturbation-related tasks, proving we don't sacrifice general utility.

**Secondary Outcomes**:

5. **Disentangled Representations**: MIG scores > 0.6 indicating successful separation of perturbation effects from cell-intrinsic properties.

6. **Sample Efficiency**: Demonstrate 2-3x better few-shot learning on novel perturbations, valuable for expensive experimental settings.

7. **Multi-Scale Alignment**: Achieve Spearman correlation > 0.75 between image and expression perturbation embeddings, enabling cross-modal reasoning.

### 4.2 Scientific Impact

**Advancing Causal Representation Learning in Biology**: This work establishes a concrete framework for incorporating causal reasoning into biological foundation models, moving beyond correlational pattern recognition. The theoretical contributions around multi-scale causal consistency and perturbation disentanglement will inform future model development.

**Mechanistic Understanding**: By learning representations that encode causal pathways, this research enables biologists to generate mechanistic hypotheses about cellular responses. The interpretability analyses will reveal how perturbations propagate through biological systems, potentially uncovering novel pathway interactions.

**Benchmark Establishment**: The comprehensive evaluation protocol, including causal validity metrics and cross-dataset transfer tasks, will provide the community with standardized methods for assessing biological meaningfulness—directly addressing LMRL workshop objectives.

### 4.3 Practical Impact

**Drug Discovery**: Pharmaceutical companies can use these models to:
- Predict off-target effects of novel compounds more reliably
- Design combination therapies by simulating multi-drug perturbations
- Identify patient subgroups likely to respond to specific treatments

**Virtual Cell Simulation**: The causal representations enable more accurate in-silico experimentation, reducing the need for costly wet-lab validation. Researchers can test thousands of perturbations computationally before selecting candidates for experimental validation.

**Precision Medicine**: By understanding causal mechanisms underlying disease perturbations, clinicians can better predict individual patient responses and design personalized interventions.

### 4.4 Broader Impact

**Open Science**: We will release:
- Pre-trained model weights and code on GitHub
- Standardized evaluation benchmarks for perturbation prediction
- Interactive visualization tools for exploring learned representations

**Community Building**: This work bridges machine learning and biology communities, demonstrating how domain knowledge (perturbations as interventions) can enhance foundation models. We anticipate this will inspire similar approaches in other scientific domains.

**Educational Value**: The framework provides a concrete example of applying causal inference to real-world problems, valuable for teaching advanced ML courses at the intersection of causality and biology.

**Ethical Considerations**: While improved perturbation prediction has tremendous positive potential, we acknowledge risks around dual-use (e.g., designing harmful biological agents). We will engage with biosecurity experts and include responsible use guidelines in our releases.

### 4.5 Future Directions

This research opens several promising avenues:

**Temporal Dynamics**: Extending the framework to model time-series perturbation responses, capturing dynamic causal processes.

**Active Learning**: Using causal uncertainty estimates to guide experimental design, selecting maximally informative perturbations to test.

**Causal Discovery**: Leveraging learned representations to infer complete causal graphs of biological systems, going beyond perturbation prediction to mechanism discovery.

**Multi-Organism Transfer**: Testing whether causal representations learned in model organisms (yeast, C. elegans) transfer to human cells, enabling cross-species biological insights.

In conclusion, this research addresses a critical gap in biological foundation models by incorporating causal reasoning through perturbation modeling. By learning representations that encode intervention-response relationships rather than mere correlations, we enable more reliable generalization, interpretable insights, and practical applications in drug discovery and virtual cell simulation. This work directly contributes to the LMRL workshop's mission of defining and learning truly meaningful representations of life.