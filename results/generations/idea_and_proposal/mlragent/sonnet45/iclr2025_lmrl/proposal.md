# Research Proposal: Hierarchical Perturbation Encoders for Learning Scale-Bridging Representations from Multi-Level Biological Interventions

## 1. Title

**Hierarchical Perturbation Encoders: Learning Scale-Bridging Representations from Multi-Level Biological Interventions**

## 2. Introduction

### 2.1 Background

The emerging field of representation learning for biological data has witnessed remarkable progress with the development of foundation models trained on large-scale genomic, proteomic, and cellular datasets. However, a critical gap remains in our ability to model and predict how biological perturbations—such as gene knockouts, drug treatments, or environmental changes—propagate across multiple scales of biological organization. Current approaches typically focus on single-scale perturbation analysis: genetic perturbation models examine transcriptomic changes, chemical perturbation models analyze cellular morphology, and phenotypic models correlate outcomes with exposures. This fragmented view fails to capture the fundamental reality that biological systems operate through hierarchical causality, where molecular interventions cascade through cellular states to manifest as tissue-level and organism-level phenotypes.

Understanding these cross-scale causal relationships is essential for transformative applications in precision medicine and drug discovery. For instance, predicting how a novel small molecule will affect patient outcomes requires tracing its effects from molecular target engagement, through pathway perturbations and cellular state changes, to tissue-level responses. Conversely, reverse-engineering the molecular mechanisms underlying observed phenotypic changes could reveal new therapeutic targets. Despite the critical importance of this problem, existing representation learning frameworks lack the architectural components and training methodologies necessary to bridge these biological scales.

Recent work in multi-modal biological representation learning has made progress in integrating different data types within single scales (e.g., CHMR's integration of molecular structures with cellular responses) and in capturing hierarchical relationships within specific domains (e.g., HIPPO's hierarchical protein interaction prediction). However, these approaches do not explicitly model perturbation effects across the full biological hierarchy from molecules to phenotypes, nor do they provide mechanisms for cross-scale causal inference.

### 2.2 Research Objectives

This research proposes **Hierarchical Perturbation Encoders (HPE)**, a novel framework for learning scale-bridging representations that explicitly model how biological perturbations propagate across molecular, cellular, and phenotypic scales. Our specific objectives are:

1. **Develop a unified multi-scale perturbation knowledge graph** that integrates heterogeneous perturbation data across genetic, chemical, and environmental interventions with their measured effects at molecular, cellular, and phenotypic levels.

2. **Design hierarchical encoder architectures** that learn perturbation representations capturing both scale-specific effects and cross-scale causal relationships through structured inductive biases.

3. **Formulate novel hierarchical contrastive learning objectives** that align perturbations based on their effects across multiple scales while maintaining the hierarchical structure of biological causality.

4. **Establish comprehensive cross-scale evaluation benchmarks** including zero-shot prediction tasks, causal pathway discovery, and practical drug design applications.

5. **Demonstrate practical utility** through case studies in predicting cellular responses from genetic interventions, inferring molecular mechanisms from phenotypic observations, and designing multi-target therapeutic strategies.

### 2.3 Significance

This research addresses a fundamental challenge in computational biology: bridging the representation gap between molecular interventions and organism-level outcomes. The proposed framework will enable:

- **Predictive drug discovery**: Rational design of therapeutics by predicting organism-level efficacy and safety from molecular properties
- **Mechanism discovery**: Identifying causal pathways connecting molecular targets to phenotypic outcomes
- **Precision medicine**: Predicting patient-specific responses to interventions based on molecular profiles
- **Virtual cell modeling**: Contributing foundational components toward comprehensive simulation of multi-scale cellular responses

Beyond immediate applications, HPE will provide the AI-biology community with open-source tools, benchmarks, and evaluation frameworks for multi-scale representation learning, advancing standardization in this rapidly evolving field.

## 3. Methodology

### 3.1 Data Collection and Multi-Scale Perturbation Graph Construction

#### 3.1.1 Data Sources

We will integrate publicly available datasets spanning multiple biological scales:

**Molecular Scale:**
- Genetic perturbations: Perturb-seq data from the Human Cell Atlas, CRISPR knockout/knockdown screens
- Transcriptomic responses: Gene Expression Omnibus (GEO), LINCS L1000 gene expression profiles
- Proteomic changes: Mass spectrometry data from ProteomeXchange

**Cellular Scale:**
- Morphological perturbations: Cell Painting data from JUMP-CP consortium, RxRx3 image datasets
- Single-cell states: scRNA-seq data from CellxGene, flow cytometry profiles
- Spatial organization: Spatial transcriptomics from 10x Visium, CODEX imaging

**Phenotypic Scale:**
- Disease associations: ClinVar, GWAS catalog, disease ontology databases
- Drug response data: GDSC, CCLE drug sensitivity screens
- Clinical outcomes: Published clinical trial data, UK Biobank

#### 3.1.2 Knowledge Graph Construction

We construct a heterogeneous multi-scale perturbation knowledge graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{R})$ where:

$$\mathcal{V} = \mathcal{V}_p \cup \mathcal{V}_m \cup \mathcal{V}_c \cup \mathcal{V}_{\phi}$$

represents nodes for perturbations ($\mathcal{V}_p$), molecular effects ($\mathcal{V}_m$), cellular effects ($\mathcal{V}_c$), and phenotypic outcomes ($\mathcal{V}_{\phi}$).

Edges $\mathcal{E}$ encode relationships with types $\mathcal{R}$ including:
- **Within-scale**: "co-regulated", "structurally-similar", "pathway-member"
- **Cross-scale**: "induces", "modulates", "manifests-as"
- **Hierarchical**: "parent-of", "upscale-effect", "downscale-mechanism"

Each node $v \in \mathcal{V}$ is associated with raw feature vectors:
- Perturbations: molecular fingerprints, sequence embeddings, environmental parameters
- Effects: gene expression vectors, morphological features, phenotypic measurements

### 3.2 Hierarchical Encoder Architecture

#### 3.2.1 Scale-Specific Encoders

We design specialized encoders for each biological scale:

**Molecular Encoder** $f_m: \mathbb{R}^{d_m} \rightarrow \mathbb{R}^{h}$:
For genetic perturbations, we use transformer-based sequence encoders. For chemical perturbations, we employ graph neural networks on molecular graphs:

$$\mathbf{h}_m^{(l+1)} = \text{GNN}^{(l)}(\mathbf{h}_m^{(l)}, \mathcal{A}_m) = \sigma\left(\sum_{j \in \mathcal{N}(i)} \mathbf{W}^{(l)} \mathbf{h}_j^{(l)}\right)$$

where $\mathcal{A}_m$ represents molecular connectivity and $\mathcal{N}(i)$ are neighboring atoms.

**Cellular Encoder** $f_c: \mathbb{R}^{d_c} \rightarrow \mathbb{R}^{h}$:
For morphological data, we use Vision Transformers (ViT) adapted for multi-channel microscopy images. For single-cell data, we employ scGPT-style transformer architectures:

$$\mathbf{h}_c = \text{ViT}(\mathbf{I}_{\text{cell}}) + \text{Transformer}(\mathbf{x}_{\text{sc}})$$

**Phenotypic Encoder** $f_{\phi}: \mathbb{R}^{d_\phi} \rightarrow \mathbb{R}^{h}$:
For phenotypic data, we use structured encoders incorporating ontology information:

$$\mathbf{h}_{\phi} = \text{MLP}(\mathbf{x}_{\phi}) + \text{GCN}(\mathbf{x}_{\phi}, \mathcal{A}_{\text{ontology}})$$

#### 3.2.2 Hierarchical Cross-Scale Attention

To capture cross-scale dependencies, we introduce hierarchical cross-attention modules that allow information flow between scales:

$$\mathbf{h}_s^{\text{cross}} = \text{CrossAttn}(\mathbf{Q}_s, \mathbf{K}_{s'}, \mathbf{V}_{s'})$$

where $s, s' \in \{m, c, \phi\}$ represent different scales, and:

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$

We implement bidirectional cross-scale attention with learned scale-compatibility weights $\alpha_{s \rightarrow s'}$ to modulate information flow based on biological plausibility.

#### 3.2.3 Perturbation Representation

The final perturbation representation combines scale-specific and cross-scale features:

$$\mathbf{z}_p = \text{Aggregate}\left(\{\mathbf{h}_m, \mathbf{h}_c, \mathbf{h}_{\phi}, \mathbf{h}_m^{\text{cross}}, \mathbf{h}_c^{\text{cross}}, \mathbf{h}_{\phi}^{\text{cross}}\}\right)$$

We use learnable hierarchical pooling that preserves scale structure:

$$\mathbf{z}_p = \mathbf{W}_{\phi}(\mathbf{h}_{\phi} + \mathbf{W}_c(\mathbf{h}_c + \mathbf{W}_m \mathbf{h}_m))$$

### 3.3 Hierarchical Contrastive Learning Framework

#### 3.3.1 Multi-Scale Contrastive Objectives

We formulate a hierarchical contrastive loss that aligns perturbations based on their effects across scales:

**Scale-Specific Contrastive Loss**: For each scale $s \in \{m, c, \phi\}$:

$$\mathcal{L}_s = -\log \frac{\exp(\text{sim}(\mathbf{z}_i^s, \mathbf{z}_j^s)/\tau)}{\sum_{k=1}^N \exp(\text{sim}(\mathbf{z}_i^s, \mathbf{z}_k^s)/\tau)}$$

where $(i,j)$ are perturbations with similar effects at scale $s$, and $\text{sim}(\cdot, \cdot)$ is cosine similarity.

**Cross-Scale Alignment Loss**: To align effects across scales:

$$\mathcal{L}_{\text{align}} = \sum_{s < s'} \|\mathbf{z}_i^s - \mathbf{z}_i^{s'}\|_2^2$$

for perturbations where effects propagate from scale $s$ to $s'$.

**Hierarchical Triplet Loss**: To preserve causal hierarchy:

$$\mathcal{L}_{\text{hierarchy}} = \sum_{(a,p,n)} \max(0, \text{sim}(\mathbf{z}_a, \mathbf{z}_n) - \text{sim}(\mathbf{z}_a, \mathbf{z}_p) + \gamma \cdot d_h(a,p))$$

where $d_h(a,p)$ is the hierarchical distance between anchor $a$ and positive $p$ in the biological scale hierarchy, and $\gamma$ is a margin that increases with hierarchical distance.

#### 3.3.2 Causal Consistency Regularization

To enforce biologically plausible causal relationships, we introduce a causal consistency term:

$$\mathcal{L}_{\text{causal}} = \mathbb{E}_{p \sim \mathcal{P}} \left[\left\|\mathbf{z}_p^{\phi} - g(\mathbf{z}_p^c)\right\|_2^2 + \left\|\mathbf{z}_p^c - g(\mathbf{z}_p^m)\right\|_2^2\right]$$

where $g(\cdot)$ are learned propagation functions modeling how effects cascade upward through scales.

#### 3.3.3 Total Training Objective

The complete loss function combines all components:

$$\mathcal{L}_{\text{total}} = \sum_{s} \lambda_s \mathcal{L}_s + \lambda_{\text{align}} \mathcal{L}_{\text{align}} + \lambda_{\text{hier}} \mathcal{L}_{\text{hierarchy}} + \lambda_{\text{causal}} \mathcal{L}_{\text{causal}}$$

with hyperparameters $\{\lambda_s, \lambda_{\text{align}}, \lambda_{\text{hier}}, \lambda_{\text{causal}}\}$ controlling the relative importance of each component.

### 3.4 Experimental Design and Evaluation

#### 3.4.1 Cross-Scale Transfer Tasks

**Task 1: Molecular → Phenotype Prediction**
- Given: Novel genetic perturbation (e.g., CRISPR knockout)
- Predict: Cellular morphology changes and disease-relevant phenotypes
- Evaluation: Pearson correlation, rank correlation for continuous outcomes; AUROC for disease associations

**Task 2: Phenotype → Mechanism Inference**
- Given: Observed phenotypic change (e.g., disease state)
- Predict: Molecular pathways and specific gene/protein targets involved
- Evaluation: Precision@K, pathway enrichment analysis, validation against literature

**Task 3: Multi-Target Intervention Design**
- Given: Desired phenotypic outcome
- Generate: Combination of molecular interventions across scales
- Evaluation: In silico validation using virtual cell models, comparison with known multi-target drugs

#### 3.4.2 Zero-Shot Generalization

To assess generalization, we design held-out test scenarios:
- **Novel perturbations**: Compounds/genes not seen during training
- **Novel scales**: Predict effects at scales with limited training data
- **Novel contexts**: Different cell types, species, or disease contexts

Evaluation metrics:
- Transfer accuracy: $\frac{1}{N}\sum_{i=1}^N \mathbb{1}[\text{rank}(\text{true}_i) \leq k]$
- Cross-scale consistency: Measuring if predicted effects maintain biological plausibility across scales

#### 3.4.3 Interpretability Analysis

**Attention Map Visualization**: Extract cross-scale attention weights to identify which molecular features drive cellular and phenotypic changes:

$$\mathbf{A}_{m \rightarrow \phi} = \text{softmax}\left(\frac{\mathbf{Q}_{\phi}\mathbf{K}_m^T}{\sqrt{d_k}}\right)$$

**Pathway Attribution**: Use integrated gradients to attribute phenotypic predictions to specific molecular pathways.

**Counterfactual Analysis**: Generate minimal perturbation sets that flip predicted outcomes, revealing critical causal nodes.

#### 3.4.4 Baseline Comparisons

We compare against:
- **Single-scale models**: Separate models for molecular, cellular, and phenotypic prediction
- **Concatenation baselines**: Simple concatenation of scale-specific features
- **Existing multi-modal models**: CHMR, bidirectional hierarchical protein models
- **Graph-based methods**: Standard GNN architectures on the perturbation knowledge graph

#### 3.4.5 Implementation Details

- **Framework**: PyTorch with PyG (PyTorch Geometric) for graph operations
- **Training**: Distributed training on 8× A100 GPUs
- **Optimization**: AdamW optimizer with learning rate warmup and cosine annealing
- **Batch construction**: Stratified sampling ensuring each batch contains perturbations with multi-scale annotations
- **Computational budget**: ~500 GPU hours for full training

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Scientific Contributions:**

1. **Novel Architecture**: A hierarchical encoder framework that explicitly models cross-scale perturbation effects, advancing multi-modal representation learning for biology beyond current state-of-the-art.

2. **Training Methodology**: Hierarchical contrastive learning objectives that preserve biological causal structure, providing a template for future multi-scale biological modeling.

3. **Benchmark Suite**: Comprehensive evaluation framework for cross-scale perturbation prediction, including curated test sets, evaluation protocols, and baseline implementations released as open-source tools.

4. **Mechanistic Insights**: Interpretable attention maps and causal attribution methods revealing how specific molecular interventions propagate to cellular and phenotypic outcomes, validated against known biological pathways.

**Quantitative Targets:**

- **Zero-shot prediction accuracy**: ≥0.75 Spearman correlation for predicting cellular responses from novel molecular perturbations
- **Mechanism inference**: ≥0.6 Precision@10 for identifying correct molecular pathways from phenotypic observations
- **Cross-scale consistency**: ≥0.8 correlation between predicted effects at adjacent biological scales
- **Generalization**: ≤15% performance degradation when transferring to held-out cell types or contexts

### 4.2 Practical Impact

**Drug Discovery Applications:**

The framework will enable:
- **Target identification**: Reverse-engineering molecular targets from desired phenotypic outcomes, reducing early-stage drug discovery costs
- **Polypharmacology design**: Rational design of multi-target drugs by predicting synergistic molecular interventions
- **Safety prediction**: Early identification of potential adverse effects by tracing molecular perturbations to organism-level phenotypes

**Precision Medicine:**

- **Response prediction**: Patient-specific prediction of therapeutic responses based on molecular profiles
- **Mechanism-based stratification**: Identifying patient subgroups based on shared molecular-to-phenotype causal pathways
- **Repurposing opportunities**: Discovering new indications for existing drugs by analyzing cross-scale effect patterns

### 4.3 Community Impact

**Open Science Contributions:**

1. **Code Release**: Full implementation released on GitHub with documentation and tutorials
2. **Pre-trained Models**: Publicly available model checkpoints trained on integrated multi-scale datasets
3. **Benchmark Platform**: Interactive leaderboard for community evaluation of cross-scale prediction methods
4. **Dataset Integration**: Standardized preprocessing pipelines for major perturbation databases

**Educational Resources:**

- Workshop materials and tutorials for LMRL and related venues
- Jupyter notebooks demonstrating use cases from basic prediction to drug design applications
- Documentation of best practices for multi-scale biological representation learning

### 4.4 Future Directions

This research establishes foundational components for several exciting future directions:

**Virtual Cell Modeling**: Integration with spatiotemporal dynamics models to predict time-resolved multi-scale perturbation responses, contributing to comprehensive virtual cell simulators.

**Causal Discovery**: Extension to automatic discovery of causal relationships from observational multi-scale data, reducing reliance on experimental perturbation data.

**Active Learning**: Integration with experimental design algorithms to optimally select perturbations for maximal information gain about cross-scale causal mechanisms.

**Multi-Organism Transfer**: Extending representations to enable cross-species transfer, leveraging evolutionary conservation of biological mechanisms.

**Clinical Translation**: Prospective validation in clinical settings, working toward regulatory-approved models for therapeutic decision support.

### 4.5 Societal Considerations

While this research promises significant benefits, we acknowledge important considerations:

**Ethical Use**: Predictive models of biological interventions must be deployed responsibly, with careful consideration of unintended consequences and dual-use concerns.

**Accessibility**: We commit to open-source release to ensure broad access, particularly for resource-limited research environments.

**Validation Requirements**: Clinical applications will require extensive validation and regulatory approval; our work provides foundational technology requiring further development for clinical deployment.

**Transparency**: Model interpretability components will be prioritized to enable scientific scrutiny and build trust in predictions.

---

**Conclusion**: Hierarchical Perturbation Encoders represent a significant step toward comprehensive modeling of multi-scale biological causality. By learning representations that bridge molecular interventions with organism-level outcomes, this research addresses a critical gap in computational biology and provides practical tools for drug discovery and precision medicine. The proposed framework, evaluation benchmarks, and open-source contributions will advance the field of biological representation learning and catalyze further research in multi-scale modeling of life.