# Research Proposal: BioRenorm - Physics-Inspired Renormalization Group Operators for Cross-Scale Drug Response Prediction

## 1. Title

**BioRenorm: Physics-Inspired Renormalization Group Operators for Cross-Scale Drug Response Prediction in Emerging Therapeutic Modalities**

## 2. Introduction

### 2.1 Background

The landscape of drug discovery is rapidly evolving beyond traditional small molecules toward emerging therapeutic modalities including RNA therapeutics (mRNA vaccines, antisense oligonucleotides), cell and gene therapies (CAR-T cells, CRISPR-based interventions), and protein engineering. These modalities operate across multiple biological scales—from molecular interactions at the nanometer scale to cellular responses at the micrometer scale and tissue-level phenotypes at the millimeter scale. However, current artificial intelligence approaches for drug discovery face a critical limitation: they lack principled frameworks for bridging these hierarchical biological scales.

Existing multimodal foundation models in drug discovery typically employ simple concatenation of features from different scales or rely on attention mechanisms that treat cross-scale interactions as generic pattern matching problems. While these approaches have shown promise in single-scale predictions (e.g., molecular property prediction or cellular phenotype classification), they fundamentally struggle with cross-scale prediction tasks such as inferring tissue-level drug responses from molecular features. This limitation necessitates extensive and expensive wet-lab validation at each biological scale, creating bottlenecks in therapeutic development pipelines. For instance, screening a single compound across organoid models can cost $5 million and require 6 months, while CRISPR target prioritization experiments can exceed $1.5 million per campaign.

The core challenge lies in the absence of biologically-meaningful scale-transition mechanisms. Physical systems have long addressed analogous multi-scale problems through renormalization group (RG) theory—a framework from statistical physics that describes how system properties transform across different observation scales. RG theory has successfully explained phenomena ranging from phase transitions in materials to turbulence in fluids by identifying conserved quantities and emergent behaviors at different scales. Recent work has begun exploring RG concepts in deep learning for scale-invariant representations, but no prior work has systematically applied RG theory to biological hierarchies with domain-specific constraints.

### 2.2 Research Objectives

This research proposes **BioRenorm**, a novel multimodal foundation model that incorporates learnable renormalization group operators to discover data-driven scale-transition rules across molecular, cellular, and tissue levels. Our specific objectives are:

1. **Develop a theoretical framework** that formalizes biological scale transitions using RG theory, defining learnable coarse-graining operators $\mathcal{R}_{\theta}$ with biologically-motivated conservation constraints (information preservation, mass balance).

2. **Design and implement pathway-aware RG operators** that leverage biological knowledge graphs (KEGG, Reactome, Gene Ontology) to ensure scale transitions respect known biological pathway structures.

3. **Create a multi-stage training strategy** that addresses data heterogeneity across scales through separate pretraining per scale, pairwise RG operator learning, and end-to-end fine-tuning.

4. **Validate cross-scale prediction capabilities** on PRISM organoid drug screening data, achieving ≥0.7 Pearson correlation for molecular→tissue drug response prediction with ≥10% improvement over hierarchical transformer baselines.

5. **Demonstrate practical utility** for drug discovery applications including in silico screening, CRISPR target prioritization, and RNA therapeutic design, targeting 60-90% cost reduction and 2-5× time acceleration.

### 2.3 Significance

This research addresses a critical gap (Gap 3: Multimodal Foundation Models Bridging Molecular and Cellular Scales) identified in the AI for Drug Discovery landscape. The significance spans three dimensions:

**Theoretical Contribution**: BioRenorm introduces the first formalization of biological scale transitions using RG theory, establishing concepts of biological universality classes (conserved modules across scales), scale-invariant biological features, and emergent complexity in hierarchical biological systems. This framework provides a principled alternative to ad-hoc feature aggregation methods.

**Methodological Innovation**: The integration of (1) learnable RG operators, (2) biological pathway priors, (3) conservation constraints, and (4) skip connections with learnable gating represents a novel architectural paradigm. Unlike existing approaches that treat scales independently or use generic attention mechanisms, BioRenorm explicitly models the physics of scale transitions while incorporating domain knowledge.

**Practical Impact**: For emerging therapeutic modalities, BioRenorm enables:
- **RNA therapeutics**: Predict tissue-level efficacy from UTR/codon sequences, reducing screening costs by 60% ($350K→$150K) and enabling 10× larger candidate exploration (100→1,000 designs).
- **Cell/gene therapies**: Prioritize CRISPR targets by predicting tissue phenotypes from genetic perturbations, reducing validation costs by 85% ($1.5M→$200K) and accelerating timelines by 2.3× (9→4 months).
- **Drug repurposing**: Screen compounds in silico across organoid models, reducing costs by 90% ($5M→$500K) and accelerating discovery by 5× (6→1 month).

Furthermore, the interpretability of RG operators—through pathway alignment analysis—provides mechanistic insights into conserved biological modules (e.g., transcription factor motifs → inflammatory gene expression → tissue inflammation), addressing the black-box criticism of foundation models in drug discovery.

## 3. Methodology

### 3.1 Theoretical Framework: Renormalization Group for Biological Hierarchies

We formalize biological scale transitions using RG theory. Let $\mathbf{x}^{(s)}$ denote the representation at scale $s \in \{\text{molecular}, \text{cellular}, \text{tissue}\}$. A renormalization group operator $\mathcal{R}_{\theta}^{s \to s+1}$ maps representations from scale $s$ to $s+1$:

$$\mathbf{x}^{(s+1)} = \mathcal{R}_{\theta}^{s \to s+1}(\mathbf{x}^{(s)})$$

**Conservation Constraints**: Inspired by physical RG theory, we impose two biologically-motivated constraints:

1. **Information Conservation**: The mutual information between scales should be maximized to prevent information loss during coarse-graining:
$$\mathcal{L}_{\text{info}} = -I(\mathbf{x}^{(s)}; \mathbf{x}^{(s+1)})$$

2. **Mass Balance**: For molecular→cellular transitions involving gene expression, total "mass" (e.g., sum of expression levels) should be approximately conserved:
$$\mathcal{L}_{\text{mass}} = \left|\sum_i x_i^{(s)} - \sum_j x_j^{(s+1)}\right|^2$$

**Pathway-Aware Aggregation**: We structure $\mathcal{R}_{\theta}$ to respect biological pathway hierarchies. Let $\mathcal{P} = \{P_1, P_2, \ldots, P_K\}$ be a set of pathways from KEGG/Reactome, where each pathway $P_k$ contains genes $\{g_1^k, g_2^k, \ldots, g_{n_k}^k\}$. The RG operator first aggregates within pathways:

$$\mathbf{h}_k = \text{PathwayPool}(\{\mathbf{x}_{g_i^k}^{(s)}\}_{i=1}^{n_k}; \theta_{\text{pool}})$$

where PathwayPool is a learnable aggregation function (e.g., attention-weighted sum). Then, pathway representations are transformed to the next scale:

$$\mathbf{x}^{(s+1)} = \text{MLP}_{\theta}([\mathbf{h}_1, \mathbf{h}_2, \ldots, \mathbf{h}_K])$$

### 3.2 BioRenorm Architecture

**Multi-Scale Encoder**: BioRenorm consists of three scale-specific encoders:

1. **Molecular Encoder** $E_{\text{mol}}$: Processes molecular features (SMILES strings, molecular graphs, physicochemical properties) using a graph neural network (GNN) or transformer:
$$\mathbf{x}^{(\text{mol})} = E_{\text{mol}}(\text{SMILES}, \text{MolGraph}; \theta_{\text{mol}})$$

2. **Cellular Encoder** $E_{\text{cell}}$: Processes single-cell RNA-seq data or cell painting features using a transformer or variational autoencoder:
$$\mathbf{x}^{(\text{cell})} = E_{\text{cell}}(\text{scRNA-seq}; \theta_{\text{cell}})$$

3. **Tissue Encoder** $E_{\text{tissue}}$: Processes spatial transcriptomics or histopathology images using a vision transformer or convolutional network:
$$\mathbf{x}^{(\text{tissue})} = E_{\text{tissue}}(\text{SpatialData}; \theta_{\text{tissue}})$$

**RG Operators with Skip Connections**: To prevent error amplification across scales, we introduce skip connections with learnable gating:

$$\mathbf{x}^{(s+1)} = \alpha_s \cdot \mathcal{R}_{\theta}^{s \to s+1}(\mathbf{x}^{(s)}) + (1 - \alpha_s) \cdot \text{Direct}_{\theta}(\mathbf{x}^{(s)})$$

where $\alpha_s = \sigma(\mathbf{w}_s^T \mathbf{x}^{(s)} + b_s)$ is a learnable gating function, and $\text{Direct}_{\theta}$ is a direct projection that bypasses the RG operator.

**Prediction Head**: For drug response prediction, we use a multi-layer perceptron on the tissue-scale representation:

$$\hat{y}_{\text{response}} = \text{MLP}_{\text{pred}}(\mathbf{x}^{(\text{tissue})}; \theta_{\text{pred}})$$

**Total Loss Function**: The training objective combines prediction loss with conservation constraints:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pred}} + \lambda_{\text{info}} \mathcal{L}_{\text{info}} + \lambda_{\text{mass}} \mathcal{L}_{\text{mass}}$$

where $\mathcal{L}_{\text{pred}}$ is mean squared error for regression tasks or cross-entropy for classification, and $\lambda_{\text{info}}, \lambda_{\text{mass}}$ are hyperparameters controlling constraint strength.

### 3.3 Multi-Stage Training Strategy

To address data heterogeneity across scales, we employ a three-stage training protocol:

**Stage 1: Scale-Specific Pretraining**
- **Molecular Scale**: Pretrain $E_{\text{mol}}$ on PubChem (110M compounds) using self-supervised objectives (masked atom prediction, contrastive learning).
- **Cellular Scale**: Pretrain $E_{\text{cell}}$ on scRNA-seq atlases (Human Cell Atlas, Tabula Sapiens; ~10M cells) using masked gene expression prediction.
- **Tissue Scale**: Pretrain $E_{\text{tissue}}$ on TCGA spatial transcriptomics and histopathology images (~10K samples) using contrastive learning.

**Stage 2: Pairwise RG Operator Learning**
- **Molecular→Cellular**: Train $\mathcal{R}_{\theta}^{\text{mol} \to \text{cell}}$ on paired data from Cell Painting assays (~50K compound-cell pairs) with frozen encoders.
- **Cellular→Tissue**: Train $\mathcal{R}_{\theta}^{\text{cell} \to \text{tissue}}$ on spatial transcriptomics data (~5K samples) linking single-cell and tissue representations.

**Stage 3: End-to-End Fine-Tuning**
- Fine-tune the entire BioRenorm model on PRISM organoid drug screening data (~2.25M data points: 4,500 compounds × 500 organoid models) for molecular→tissue drug response prediction.
- Use a learning rate schedule with warm-up (1,000 steps) and cosine decay.
- Apply gradient clipping (max norm = 1.0) to stabilize training across scales.

### 3.4 Data Collection and Preprocessing

**Primary Dataset**: PRISM Repurposing organoid drug screening dataset
- **Size**: 4,500 compounds × 500 organoid models × ~1 drug response metric = 2.25M data points
- **Molecular Features**: SMILES strings, molecular graphs (RDKit), physicochemical descriptors (molecular weight, logP, TPSA)
- **Cellular Features**: Baseline gene expression profiles of organoid models (RNA-seq, ~20K genes)
- **Tissue Features**: Organoid morphology images, spatial gene expression patterns
- **Target Variable**: Drug response (viability, IC50, area under curve)

**Auxiliary Datasets**:
- **Stage 1 Pretraining**: PubChem (molecular), Human Cell Atlas (cellular), TCGA (tissue)
- **Stage 2 Pairwise Training**: Cell Painting (molecular-cellular), 10x Visium spatial transcriptomics (cellular-tissue)

**Preprocessing**:
1. **Molecular**: Canonicalize SMILES, generate molecular graphs with atom/bond features, normalize physicochemical descriptors to zero mean and unit variance.
2. **Cellular**: Log-normalize gene expression counts, select top 5,000 highly variable genes, apply batch correction (Harmony).
3. **Tissue**: Resize images to 224×224, normalize pixel values, extract spatial gene expression matrices.

### 3.5 Experimental Design

**Research Questions**:
1. **RQ1 (Primary)**: Can BioRenorm achieve ≥0.7 Pearson correlation for molecular→tissue drug response prediction?
2. **RQ2**: Does BioRenorm outperform hierarchical transformer and late fusion baselines by ≥10%?
3. **RQ3**: Do skip connections prevent error amplification (degradation <10% vs oracle)?
4. **RQ4**: Do RG operators align with biological pathways (≥30% pathway alignment)?
5. **RQ5**: Does multi-stage training enable data-efficient learning (<10K fully-paired samples)?

**Experimental Arms**:
1. **BioRenorm-Full**: Complete model with RG operators, skip connections, pathway priors, conservation constraints
2. **Hierarchical Transformer**: Swin-style hierarchical transformer without RG operators or pathway priors
3. **Late Fusion**: Concatenate molecular, cellular, tissue features → MLP predictor
4. **Ablations**:
   - BioRenorm-NoSkip: Remove skip connections
   - BioRenorm-NoPathway: Remove pathway-aware pooling
   - BioRenorm-NoConservation: Remove conservation constraints ($\lambda_{\text{info}} = \lambda_{\text{mass}} = 0$)
   - BioRenorm-RGOnly: Remove skip connections and use only RG operators

**Evaluation Protocol**:
- **Data Split**: 5-fold cross-validation with stratification by organoid tissue type
- **Training**: 100 epochs per fold, early stopping with patience=10 on validation loss
- **Hardware**: 64 NVIDIA A100 GPUs (80GB), distributed training with PyTorch DDP
- **Computational Budget**: ~15,000 GPU-hours (~$50K at cloud pricing)

### 3.6 Evaluation Metrics

**Primary Metrics**:
1. **Pearson Correlation** ($r$): Measures linear relationship between predicted and actual drug responses
2. **Spearman Correlation** ($\rho$): Measures rank-order relationship (robust to outliers)

**Secondary Metrics**:
1. **Mean Absolute Error (MAE)**: $\frac{1}{N}\sum_{i=1}^N |y_i - \hat{y}_i|$
2. **Top-K Precision**: Fraction of top-K predicted compounds that are truly effective (K=10, 50, 100)
3. **Pathway Alignment**: Percentage of learned RG operator attention weights that align with known KEGG/Reactome pathway structures (measured via pathway enrichment analysis)
4. **Computational Cost**: Training time (GPU-hours), inference time (ms per sample), model parameters

**Statistical Testing**:
- **Paired t-test** with Bonferroni correction (α=0.01) to compare BioRenorm vs baselines across 5 folds
- **Effect size**: Cohen's d ≥ 0.5 for practical significance
- **Confidence intervals**: 95% CI for correlation coefficients using Fisher's z-transformation

**Success Criteria**:
- **Primary**: $r_{\text{BioRenorm}} \geq 0.7$ AND $(r_{\text{BioRenorm}} - r_{\text{baseline}}) / r_{\text{baseline}} \geq 0.10$ for BOTH baselines
- **Secondary**: Pathway alignment ≥30%, degradation vs oracle <10%, statistical significance (p<0.01, d≥0.5)

**Falsification Criteria** (reject hypothesis if):
- Baseline equivalence: $|r_{\text{BioRenorm}} - r_{\text{baseline}}| \leq 0.05$
- Oracle gap: $(r_{\text{oracle}} - r_{\text{BioRenorm}}) / r_{\text{oracle}} > 0.25$
- Pathway alignment: <10%
- Skip dominance: Skip connections contribute >90% of performance (RG operators ineffective)

### 3.7 Interpretability Analysis

To validate that RG operators discover biologically meaningful scale transitions:

1. **Pathway Enrichment Analysis**: Extract attention weights from PathwayPool operators, perform hypergeometric test to identify enriched KEGG/Reactome pathways (FDR-corrected p<0.05).

2. **Conserved Module Identification**: Cluster genes with similar RG operator transformation patterns across multiple compounds, annotate clusters with Gene Ontology terms.

3. **Case Studies**: For selected compounds (e.g., known NF-κB inhibitors), trace molecular features → pathway activations → cellular phenotypes → tissue responses, validating against literature.

4. **Ablation Analysis**: Systematically remove pathway priors and measure impact on both prediction performance and pathway alignment to quantify the contribution of biological knowledge.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Results**:
1. **Cross-Scale Prediction Performance**: Pearson correlation $r \geq 0.7$ for molecular→tissue drug response prediction, representing ≥10% improvement over hierarchical transformer ($r \approx 0.63$) and ≥15% improvement over late fusion ($r \approx 0.60$).

2. **Robustness**: Skip connections reduce error amplification to <10% degradation compared to oracle models (trained directly on tissue-level features), compared to >25% degradation for models without skip connections.

3. **Interpretability**: ≥30% of learned RG operator attention weights align with known KEGG/Reactome pathway structures (vs <10% for generic attention mechanisms), enabling mechanistic interpretation.

4. **Data Efficiency**: Multi-stage training achieves strong performance with <10K fully-paired molecular-cellular-tissue samples, compared to >50K samples required for end-to-end training from scratch.

5. **Computational Efficiency**: Inference time <100ms per compound-organoid pair on a single GPU, enabling high-throughput in silico screening.

**Qualitative Insights**:
1. **Biological Universality Classes**: Identification of conserved biological modules that exhibit scale-invariant behavior (e.g., inflammatory response pathways that manifest consistently from molecular perturbations to tissue phenotypes).

2. **Emergent Complexity**: Discovery of tissue-level phenotypes that emerge from cellular interactions but are not predictable from molecular features alone, quantifying the information gain at each scale transition.

3. **Failure Mode Characterization**: Systematic analysis of when cross-scale prediction fails (e.g., novel cell types, high noise, adversarial perturbations), informing future model improvements.

### 4.2 Scientific Impact

**Theoretical Contributions**:
1. **RG Framework for Biology**: Establishes renormalization group theory as a principled framework for modeling biological hierarchies, opening new research directions in computational biology and systems biology.

2. **Conservation Laws in Neural Networks**: Demonstrates how physics-inspired conservation constraints (information preservation, mass balance) can improve both performance and interpretability of deep learning models.

3. **Biological Priors in Foundation Models**: Provides a blueprint for integrating structured biological knowledge (pathway databases, gene ontologies) into foundation model architectures beyond simple feature engineering.

**Methodological Contributions**:
1. **Pathway-Aware Operators**: The PathwayPool mechanism can be adapted to other biological hierarchies (protein domains→proteins→complexes, cells→tissues→organs).

2. **Multi-Stage Training for Heterogeneous Data**: The three-stage training strategy addresses a common challenge in biomedical AI where fully-paired multi-scale data is scarce.

3. **Skip Connections for Error Propagation**: The learnable gating mechanism for skip connections provides a general solution for preventing error amplification in hierarchical models.

### 4.3 Practical Impact

**Drug Discovery Applications**:

1. **In Silico Screening**:
   - **Cost Reduction**: 90% ($5M → $500K per screening campaign)
   - **Time Acceleration**: 5× (6 months → 1 month)
   - **Throughput Increase**: Screen 10,000 compounds vs 100 in traditional organoid assays
   - **Use Case**: Repurposing FDA-approved drugs for rare diseases using patient-derived organoids

2. **CRISPR Target Prioritization**:
   - **Cost Reduction**: 85% ($1.5M → $200K per campaign)
   - **Time Acceleration**: 2.3× (9 months → 4 months)
   - **Success Rate**: Increase from 20% to 50% by predicting tissue-level phenotypes before wet-lab validation
   - **Use Case**: Gene therapy development for genetic disorders (e.g., sickle cell disease, muscular dystrophy)

3. **RNA Therapeutic Design**:
   - **Cost Reduction**: 60% ($350K → $150K per design cycle)
   - **Time Acceleration**: 2× (6 months → 3 months)
   - **Candidate Exploration**: 10× increase (100 → 1,000 UTR/codon variants)
   - **Use Case**: Optimizing mRNA vaccine constructs for enhanced translational efficiency and stability

**Broader Applications**:
1. **Personalized Medicine**: Predict patient-specific drug responses using patient-derived organoids, enabling precision oncology and rare disease treatment.

2. **Toxicity Prediction**: Identify compounds with tissue-level toxicity from molecular features, reducing late-stage clinical trial failures.

3. **Combination Therapy Design**: Predict synergistic drug combinations by modeling multi-compound perturbations across scales.

### 4.4 Dissemination and Validation

**Publications**:
1. **Primary Venue**: NeurIPS 2024 AIDrugX Workshop (ML Track + Application Track) for initial results
2. **Follow-Up Venues**: ICLR 2025 (methodological contributions), Nature Machine Intelligence (application-focused results with experimental validation)

**Open Science**:
1. **Code Release**: PyTorch implementation of BioRenorm on GitHub with Apache 2.0 license
2. **Pretrained Models**: Release pretrained encoders and RG operators on Hugging Face Model Hub
3. **Datasets**: Curated and preprocessed PRISM data with standardized splits for reproducibility

**Experimental Validation**:
1. **Wet-Lab Collaboration**: Partner with organoid research groups to validate top-10 predicted compounds in 3 disease models (cancer, inflammatory bowel disease, cystic fibrosis)
2. **Prospective Study**: Conduct prospective in silico screening for COVID-19 therapeutics, comparing predictions to subsequent wet-lab results

**Community Engagement**:
1. **Workshops**: Organize tutorial sessions at ISMB, RECOMB, and ML4H conferences
2. **Industry Partnerships**: Collaborate with pharmaceutical companies (e.g., Moderna, Genentech) to deploy BioRenorm in real-world drug discovery pipelines
3. **Educational Resources**: Develop Jupyter notebooks and video tutorials explaining RG theory for biologists and biological priors for ML researchers

### 4.5 Limitations and Future Directions

**Current Limitations**:
1. **Data Dependency**: Requires large-scale pretraining datasets at each scale (addressed by multi-stage training but still data-intensive)
2. **Pathway Database Coverage**: Limited to well-annotated pathways in KEGG/Reactome (~500 pathways), missing novel or poorly characterized biological processes
3. **Computational Cost**: Pretraining requires ~15,000 GPU-hours, limiting accessibility for smaller research groups

**Future Directions**:
1. **Extension to Additional Modalities**: Incorporate protein structure (AlphaFold predictions), metabolomics, and microbiome data into the multi-scale framework
2. **Active Learning**: Develop acquisition functions to select most informative wet-lab experiments, closing the loop between in silico prediction and experimental validation
3. **Causal RG Operators**: Extend from correlational to causal scale transitions using interventional data (CRISPR screens, drug perturbations)
4. **Federated Learning**: Enable multi-institutional collaboration on BioRenorm training while preserving data privacy (critical for patient-derived organoid data)
5. **Diffusion-Based Alternatives**: Compare RG operators with hierarchical diffusion models for generative cross-scale modeling

This research represents a paradigm shift in AI for drug discovery, moving from scale-agnostic pattern matching to physics-inspired, biologically-grounded multi-scale modeling. By bridging the gap between molecular features and tissue-level phenotypes, BioRenorm has the potential to accelerate therapeutic development for emerging modalities and democratize access to in silico drug screening for rare diseases and personalized medicine.