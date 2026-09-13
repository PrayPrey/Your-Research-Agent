# PERTURB-FM: A Multimodal Foundation Model Integrating Genetic Perturbations and Phenotypic Responses for Personalized Cell Therapy Design

## 1. Introduction

### Background

Cell and gene therapies represent a paradigm shift in modern medicine, offering unprecedented opportunities to treat previously incurable diseases through direct manipulation of cellular mechanisms. Recent FDA approvals of CAR-T cell therapies and CRISPR-based treatments have validated this therapeutic modality's potential. However, these therapies face critical challenges: unpredictable patient responses, variable efficacy across populations, off-target effects, and extremely high development costs exceeding $500 million per therapy. The fundamental issue lies in our limited ability to predict how genetic modifications will manifest as cellular phenotypes in diverse patient contexts.

Traditional computational approaches to cell therapy design focus on single-modality analyses—genomic sequence prediction, transcriptomic profiling, or phenotypic screening—in isolation. This reductionist approach fails to capture the complex, multiscale biological processes that determine therapeutic outcomes. Recent advances in foundation models (FMs) for biological sequences have demonstrated remarkable capabilities in protein structure prediction and molecular generation, yet these models rarely integrate the critical perturbation-response relationships that govern therapeutic interventions.

The emergence of large-scale perturbation datasets presents a unique opportunity. Technologies like Perturb-seq, CRISPR screens, and single-cell multi-omics platforms now generate massive datasets linking genetic perturbations to cellular responses. Simultaneously, clinical databases accumulate patient-specific genomic profiles alongside treatment outcomes. However, these data remain siloed and underutilized for predictive modeling. Recent works like CRADLE-VAE and the Central Dogma Transformer have begun addressing perturbation modeling and multi-omics integration, but lack comprehensive frameworks for personalized cell therapy optimization.

### Research Objectives

This research proposes PERTURB-FM, a multimodal foundation model designed to:

1. **Integrate multimodal perturbation data** spanning genetic modifications (CRISPR edits, viral vector designs), patient profiles (genomic/transcriptomic), and cellular responses (single-cell transcriptomics, phenotypes, clinical outcomes)

2. **Develop a unified architecture** with modality-specific encoders and cross-attention mechanisms that capture complex perturbation-response relationships across biological scales

3. **Enable personalized predictions** of optimal genetic modifications for patient-specific cell therapies while identifying potential safety concerns

4. **Establish active learning frameworks** for iterative model refinement through experimental validation loops

5. **Provide mechanistic interpretability** through attention visualization and retrieval-augmented generation to support clinical decision-making

### Significance

PERTURB-FM addresses critical gaps at the intersection of AI and cell therapy development. By creating a unified model that bridges perturbation design with patient-specific responses, this research will:

- **Accelerate therapeutic development**: Reduce experimental iterations required for cell therapy optimization from years to months
- **Improve patient outcomes**: Enable precise patient stratification and personalized therapy design based on predicted responses
- **Reduce development costs**: Minimize failed clinical trials through better pre-clinical prediction of efficacy and safety
- **Advance foundational AI methods**: Contribute novel architectures for multimodal biological data integration and perturbation modeling
- **Enable clinical translation**: Provide interpretable predictions that clinicians can trust and act upon

This work directly addresses the workshop's focus on bridging FMs with drug discovery applications, specifically targeting cell and gene therapies through multimodal perturbation modeling with biological readouts.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

**Dataset Sources:**

1. **Perturbation Datasets**:
   - Perturb-seq data from CRISPR screens (>500,000 perturbation-response pairs)
   - CRISPRi/a screens from public repositories (ENCODE, Cistrome)
   - Optical Pooled Screening (OPS) data linking genotype to phenotype
   - Clinical trial data for approved cell therapies (CAR-T outcomes, gene therapy responses)

2. **Patient-Specific Data**:
   - The Cancer Genome Atlas (TCGA) for patient genomic/transcriptomic profiles
   - UK Biobank for population-level genetic variation
   - Single-cell RNA-seq datasets from Human Cell Atlas

3. **Therapeutic Design Data**:
   - Viral vector sequences and design parameters
   - CRISPR guide RNA sequences with on/off-target scores
   - CAR-T construct designs with clinical outcomes

**Data Preprocessing Pipeline**:

For each modality, we implement specialized preprocessing:

- **Genomic sequences**: Tokenization using byte-pair encoding (BPE) with vocabulary size 8,192, capturing k-mer patterns (k=3-6)
- **Transcriptomic profiles**: Log-normalization, highly variable gene selection (top 5,000 genes), batch effect correction using Harmony
- **Phenotypic data**: Standardized morphological features extraction using CellProfiler, temporal dynamics encoding
- **Clinical outcomes**: Structured encoding of response metrics (complete response, partial response, progression-free survival)

### 2.2 Model Architecture

PERTURB-FM consists of three primary components:

**2.2.1 Modality-Specific Encoders**

For each input modality $m \in \{genetic, transcriptomic, phenotypic, clinical\}$, we define encoder $E_m$:

$$\mathbf{h}_m = E_m(\mathbf{x}_m; \theta_m)$$

where $\mathbf{x}_m$ is raw input and $\mathbf{h}_m \in \mathbb{R}^{d_{model}}$ is the encoded representation.

- **Genetic Perturbation Encoder**: Transformer encoder with rotary position embeddings for variable-length sequences (CRISPR guides, viral vectors)
  
$$E_{genetic}(\mathbf{x}) = \text{TransformerEncoder}(\text{Embed}(\mathbf{x}), L=12, d=768, h=12)$$

- **Transcriptomic Encoder**: Graph neural network treating gene co-expression as edges, followed by set transformer for permutation invariance

$$E_{transcriptomic}(\mathbf{x}) = \text{SetTransformer}(\text{GNN}(\mathbf{x}, \mathbf{A}_{coexp}))$$

- **Phenotypic Encoder**: Vision transformer for microscopy images, CNN for extracted morphological features

$$E_{phenotypic}(\mathbf{x}) = \text{ViT}(\mathbf{x}_{image}) \oplus \text{MLP}(\mathbf{x}_{features})$$

**2.2.2 Cross-Modal Fusion Module**

Inspired by the Central Dogma Transformer's directional attention, we implement cross-attention between perturbation inputs and cellular responses:

$$\mathbf{h}_{fusion} = \text{CrossAttention}(Q=\mathbf{h}_{response}, K=\mathbf{h}_{perturbation}, V=\mathbf{h}_{perturbation})$$

where attention weights $\alpha_{ij}$ capture perturbation-response relationships:

$$\alpha_{ij} = \frac{\exp(\mathbf{q}_i^T \mathbf{k}_j / \sqrt{d_k})}{\sum_j \exp(\mathbf{q}_i^T \mathbf{k}_j / \sqrt{d_k})}$$

We incorporate learnable modality embeddings $\mathbf{e}_m$ to distinguish information sources:

$$\mathbf{h}_m' = \mathbf{h}_m + \mathbf{e}_m$$

**2.2.3 Perturbation-Response Predictor**

The unified representation feeds into task-specific heads:

$$\mathbf{z}_{unified} = \text{TransformerDecoder}([\mathbf{h}_{genetic}', \mathbf{h}_{transcriptomic}', \mathbf{h}_{phenotypic}'])$$

For transcriptomic response prediction:

$$\hat{\mathbf{y}}_{transcript} = \text{MLP}_{transcript}(\mathbf{z}_{unified}) \in \mathbb{R}^{|G|}$$

For phenotypic outcome prediction:

$$\hat{\mathbf{y}}_{phenotype} = \text{MLP}_{phenotype}(\mathbf{z}_{unified}) \in \mathbb{R}^{d_{pheno}}$$

For clinical outcome prediction (classification):

$$P(y_{clinical} = c | \mathbf{z}) = \text{softmax}(\mathbf{W}_c \mathbf{z}_{unified} + \mathbf{b}_c)$$

### 2.3 Training Strategy

**2.3.1 Pre-training Objectives**

We employ multi-task pre-training with weighted loss:

$$\mathcal{L}_{pretrain} = \lambda_1 \mathcal{L}_{reconstruction} + \lambda_2 \mathcal{L}_{contrastive} + \lambda_3 \mathcal{L}_{prediction}$$

1. **Reconstruction Loss**: Masked modeling for each modality

$$\mathcal{L}_{reconstruction} = \sum_m \mathbb{E}_{\mathbf{x}_m} [||\mathbf{x}_m - \hat{\mathbf{x}}_m||^2]$$

where 15% of tokens/features are masked randomly.

2. **Contrastive Loss**: Align perturbations with similar cellular responses

$$\mathcal{L}_{contrastive} = -\log \frac{\exp(\text{sim}(\mathbf{h}_i, \mathbf{h}_i^+)/\tau)}{\sum_{j} \exp(\text{sim}(\mathbf{h}_i, \mathbf{h}_j)/\tau)}$$

3. **Prediction Loss**: Direct perturbation-response prediction

$$\mathcal{L}_{prediction} = \text{MSE}(\hat{\mathbf{y}}_{response}, \mathbf{y}_{response}) + \text{CrossEntropy}(\hat{y}_{clinical}, y_{clinical})$$

**2.3.2 Fine-tuning with Lab Feedback**

Implement active learning loop:

1. Model predicts high-uncertainty perturbations using ensemble disagreement:

$$\text{Uncertainty}(\mathbf{x}) = \frac{1}{N} \sum_{i=1}^N ||\hat{\mathbf{y}}_i - \bar{\mathbf{y}}||^2$$

2. Experimentalists validate top-K uncertain predictions in vitro
3. New validated data added to training set
4. Model fine-tuned with prioritized experience replay

Fine-tuning loss incorporates epistemic uncertainty:

$$\mathcal{L}_{finetune} = \mathcal{L}_{prediction} + \beta \mathcal{L}_{uncertainty}$$

where $\mathcal{L}_{uncertainty}$ is negative log-likelihood under learned uncertainty estimates.

### 2.4 Interpretability Mechanisms

**Attention Visualization**: Extract attention weights from cross-modal fusion to identify which genetic perturbations drive specific phenotypic changes.

**Retrieval-Augmented Generation (RAG)**: For each prediction, retrieve k-nearest perturbation examples from training data using learned embeddings:

$$\text{Retrieved}(\mathbf{x}) = \text{TopK}(\{\mathbf{x}_i\}_{i=1}^N, \text{sim}(\mathbf{h}(\mathbf{x}), \mathbf{h}(\mathbf{x}_i)))$$

**Counterfactual Analysis**: Following CRADLE-VAE, generate counterfactual perturbations by intervening on latent representations:

$$\mathbf{x}_{cf} = \text{Decoder}(\text{do}(\mathbf{z}_{perturbation} = \mathbf{z}'))$$

### 2.5 Experimental Design

**Validation Tasks**:

1. **Perturbation Response Prediction**: Predict single-cell transcriptomic profiles from genetic perturbations (held-out test set)
   - Metric: Pearson correlation between predicted and measured gene expression profiles

2. **Patient Stratification**: Classify patients into responder/non-responder groups for CAR-T therapy
   - Metrics: AUROC, AUPRC, calibration error

3. **Therapy Optimization**: Recommend optimal CRISPR edits for maximizing therapeutic efficacy
   - Metric: Success rate in prospective validation experiments

4. **Safety Prediction**: Identify off-target effects and adverse events
   - Metrics: Precision@K for predicted off-target sites, adverse event prediction accuracy

**Baseline Comparisons**:
- Single-modality models (genomic-only, transcriptomic-only)
- CRADLE-VAE for perturbation modeling
- Central Dogma Transformer for multi-omics integration
- Scgen for perturbation response prediction
- Standard CRISPR design tools (CHOPCHOP, Benchling)

**Ablation Studies**:
- Impact of each modality (remove genetic, transcriptomic, phenotypic inputs)
- Effect of cross-attention vs. simple concatenation
- Contribution of active learning loops
- Pre-training vs. training from scratch

**Computational Infrastructure**:
- Pre-training: 128 A100 GPUs for 2 weeks
- Model size: ~1.5B parameters
- Inference: Real-time predictions (<1 second per query)

## 3. Expected Outcomes & Impact

### Expected Outcomes

**1. Technical Achievements**:

- A pre-trained foundation model (PERTURB-FM) with state-of-the-art performance on perturbation response prediction, achieving >0.85 Pearson correlation on held-out transcriptomic predictions (15-20% improvement over existing methods)
- Patient stratification accuracy >0.90 AUROC for CAR-T therapy response prediction
- Successful prospective validation of ≥20 AI-designed cell therapy constructs in laboratory experiments
- Open-source release of model weights, code, and curated multimodal training datasets

**2. Scientific Insights**:

- Quantitative understanding of perturbation-response relationships across different cell types and genetic contexts
- Identification of universal vs. patient-specific determinants of therapy efficacy through interpretability analyses
- Discovery of novel genetic modifications that enhance therapeutic efficacy while minimizing off-target effects
- Validated framework for integrating clinical feedback into foundation model refinement

**3. Methodological Contributions**:

- Novel architecture for multimodal biological data integration with directional perturbation-response modeling
- Active learning protocols for efficient experimental validation of AI predictions
- Interpretability methods tailored for clinical decision support in cell therapy design
- Benchmark datasets and evaluation protocols for perturbation modeling research

### Impact

**Immediate Impact (1-2 years)**:

- **Accelerated Research**: Reduce cell therapy optimization cycles from 6-12 months to 2-3 months by prioritizing high-probability successful designs
- **Cost Reduction**: Decrease experimental costs by 40-60% through computational pre-screening of perturbations
- **Academic Advancement**: Publication in top-tier venues (Nature Biotechnology, Cell, NeurIPS), establishing new standard for perturbation modeling
- **Resource Availability**: Public release of PERTURB-FM will democratize access to advanced cell therapy design tools for academic laboratories

**Medium-term Impact (3-5 years)**:

- **Clinical Translation**: Integration of PERTURB-FM into pre-clinical development pipelines at biotech companies and academic medical centers
- **Personalized Medicine**: Enable routine patient stratification and therapy customization based on genomic profiles
- **Regulatory Acceptance**: Validation data supporting AI-designed therapies in IND applications, establishing precedent for AI-guided therapy design
- **Expanded Applications**: Extension to other therapeutic modalities (RNA therapeutics, gene therapy vectors, engineered T-cell receptors)

**Long-term Impact (5+ years)**:

- **Paradigm Shift**: Establish AI-guided design as standard practice in cell and gene therapy development, similar to computational drug design in small molecules
- **Improved Patient Outcomes**: Measurable improvements in therapy efficacy rates (target: 10-15% increase in complete response rates) and reduction in adverse events (target: 20-30% reduction in severe complications)
- **Healthcare Economics**: Reduce overall cost of cell therapies through improved success rates and reduced development times, improving accessibility
- **Foundation for Future Innovation**: PERTURB-FM architecture serves as template for next-generation multimodal foundation models in biomedicine

**Broader Scientific Impact**:

This research advances multiple frontiers simultaneously: (1) **AI methodology** through novel multimodal learning architectures and active learning frameworks; (2) **Systems biology** through quantitative perturbation-response models at unprecedented scale; (3) **Precision medicine** through patient-specific therapy optimization; and (4) **Clinical practice** through interpretable AI tools that augment human decision-making.

The project exemplifies the workshop's vision of bridging foundational models with emerging drug modalities. By demonstrating that large-scale multimodal models can meaningfully improve cell therapy outcomes, this work will catalyze broader adoption of AI throughout drug discovery and development pipelines. The interpretability mechanisms and active learning frameworks developed here will be transferable to other therapeutic modalities, amplifying impact beyond cell therapies.

Ultimately, PERTURB-FM represents a step toward "AI-native" therapeutic development—where computational prediction and experimental validation form a seamless, iterative cycle that dramatically accelerates the translation of biological insights into life-saving medicines.