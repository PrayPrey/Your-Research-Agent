# CrossScaleBench: A Unified Benchmarking Framework for Multi-Scale Biological Machine Learning

## 1. Introduction

### Background

Biology and chemistry play fundamental roles in addressing humanity's most pressing challenges, from drug discovery and materials design to climate change mitigation and food security. Machine learning has demonstrated transformative potential in these domains, yet compared to computer vision and natural language processing, biological and chemical ML research faces unique evaluation challenges that hinder both scientific progress and industrial translation.

The core challenge stems from biology's inherently multi-scale nature. Understanding biological systems requires integrating information across multiple organizational levels: from electronic structure and atomic interactions at the quantum scale, to molecular graphs and 3D conformations, to protein sequences and structures, and ultimately to cellular and tissue-level representations. Current ML benchmarks evaluate these scales independently—PubChemQCR provides 3.5 million DFT trajectories for molecular property prediction, ProteinGym offers comprehensive protein function benchmarks, and DeepProtein establishes standardized protein design evaluation. However, this fragmentation creates a critical gap: researchers cannot objectively compare multi-scale approaches that integrate information across biological scales against single-scale specialist models.

This evaluation gap has profound consequences. In drug discovery, predicting how molecular modifications affect protein binding requires understanding molecular→protein transitions. In materials design, relating atomic structure to macroscopic properties demands cross-scale consistency. Yet without standardized metrics for evaluating representation alignment and predictive transfer across scale boundaries, the field cannot answer fundamental questions: Does multi-scale integration provide measurable benefits over single-scale specialists? What architectural designs optimize cross-scale consistency? How much per-scale performance must be sacrificed to achieve cross-scale coherence?

The success of unified benchmarks in transforming computer vision (ImageNet) and natural language processing (GLUE) demonstrates that standardized evaluation frameworks accelerate research by enabling objective comparison, facilitating reproducibility, and providing clear performance indicators for industry adoption. Biology and chemistry ML urgently need analogous infrastructure that respects the field's unique multi-scale structure.

### Research Objectives

This research proposes **CrossScaleBench**, the first unified benchmarking framework treating cross-scale consistency as a first-class evaluation dimension for biological and chemical ML systems. Our primary objectives are:

**Objective 1: Develop Novel Scale-Transition Metrics**
Design and validate three complementary metrics quantifying cross-scale consistency:
- **Centered Kernel Alignment (CKA)** measuring embedding alignment quality between molecular and protein representations
- **Predictive Transfer Score (PTS)** quantifying accuracy retention when molecular features predict protein-level properties
- **End-to-End Consistency Score (EECS)** evaluating correlation between molecular predictions and protein ground truth

**Objective 2: Establish Unified Evaluation Infrastructure**
Integrate existing single-scale benchmarks (PubChemQCR for molecular scale, ProteinGym for protein scale) with ChEMBL's molecular→protein linkage data to create standardized evaluation protocols spanning scale boundaries, including:
- Curated datasets with verified cross-scale ground truth (target: 100K molecule-protein pairs)
- Reference baseline implementations across three model categories (single-scale specialists, naive multi-scale, state-of-the-art multi-scale)
- Standardized data splits, hyperparameter search procedures, and reproducibility protocols

**Objective 3: Deploy Multi-Dimensional Leaderboard**
Create a public evaluation platform with separate rankings for (A) per-scale performance, (B) cross-scale transfer quality, and (C) end-to-end task accuracy, accommodating diverse community priorities while enabling unified comparison.

**Objective 4: Validate Framework Through Empirical Study**
Conduct comprehensive experiments testing three core hypotheses:
- H1: Naive multi-scale models exhibit 20-40% performance drops at scale boundaries
- H2: Architectures with explicit transition mechanisms achieve 15-25% better cross-scale consistency
- H3: Multi-scale models trade 5-15% per-scale performance for cross-scale coherence

### Significance

CrossScaleBench addresses critical gaps at the intersection of ML methodology and biological/chemical applications:

**Scientific Impact:**
- **Enables New Research Questions**: For the first time, researchers can objectively quantify whether multi-scale integration provides net benefits over single-scale specialists, guiding architectural design decisions with empirical evidence rather than intuition.
- **Reveals Performance Trade-offs**: By measuring both per-scale accuracy and cross-scale consistency, the framework exposes fundamental trade-offs between specialization and integration, informing model selection for specific applications.
- **Accelerates Research Efficiency**: Standardized evaluation reduces duplicated effort in reimplementing baselines across fragmented benchmarks, allowing researchers to focus on innovation rather than infrastructure.

**Industrial Translation:**
- **Facilitates Drug Discovery**: Pharmaceutical companies require models that accurately predict protein binding from molecular structure—a quintessential cross-scale task. Clear performance indicators enable evidence-based model selection for high-stakes applications.
- **Supports Materials Design**: Relating molecular composition to material properties demands cross-scale consistency. The framework provides quantitative metrics for evaluating models in materials informatics pipelines.
- **Reduces Adoption Barriers**: Industry practitioners face challenges translating academic ML advances due to inconsistent evaluation standards. Unified benchmarking with standardized leaderboards lowers barriers to adoption.

**Methodological Contribution:**
- **Establishes Cross-Scale Consistency as Evaluation Dimension**: Introduces a novel evaluation paradigm treating scale transitions as explicit targets, complementing existing per-scale metrics.
- **Provides Reusable Infrastructure**: Open-source implementation of metrics, baselines, and evaluation server creates community resource analogous to ImageNet/GLUE for biological ML.
- **Informs Future Benchmark Design**: Demonstrates principles for building multi-scale evaluation frameworks applicable to other scientific domains (e.g., climate modeling, neuroscience).

This research directly addresses the workshop's call for "dataset curation, analysis and benchmarking work highlighting opportunities and pitfalls of current ML applications" while providing infrastructure that will "unlock capabilities previously thought available only through non-ML approaches" by enabling systematic evaluation of multi-scale integration strategies.

## 2. Methodology

### 2.1 Overall Research Design

CrossScaleBench employs a staged development approach with rigorous empirical validation:

**Phase 1 (Months 1-6): Pilot Study & Metric Validation**
- Curate 10,000 molecule-protein pairs from ChEMBL with verified cross-scale linkage
- Implement scale-transition metrics (CKA, PTS, EECS) with reference code
- Validate metric signal strength and correlation with downstream performance
- Conduct preliminary experiments with three baseline model categories

**Phase 2 (Months 7-12): Full Framework Development**
- Scale dataset curation to 100,000 molecule-protein pairs
- Implement comprehensive baseline models and standardized evaluation protocols
- Deploy multi-dimensional leaderboard with evaluation server
- Conduct full experimental validation testing three core hypotheses

**Phase 3 (Months 13-18): Community Deployment & Validation**
- Launch public benchmark at major ML conference workshop (NeurIPS/ICML)
- Organize community competition to drive adoption
- Collect external validation results from independent research groups
- Refine framework based on community feedback

### 2.2 Data Collection and Curation

**2.2.1 Data Sources**

The framework integrates three complementary data sources:

**Molecular Scale: PubChemQCR**
- **Content**: 3.5 million DFT (Density Functional Theory) trajectories covering diverse chemical space
- **Properties**: Quantum mechanical properties (energies, forces, dipole moments), molecular graphs, 3D conformations
- **Usage**: Provides ground truth for molecular-level tasks and molecular representations for cross-scale evaluation
- **Citation**: Fu et al. (2025)

**Protein Scale: ProteinGym**
- **Content**: Comprehensive protein function prediction benchmarks with standardized tasks
- **Properties**: Protein sequences, structures, functional annotations, fitness landscapes
- **Usage**: Provides ground truth for protein-level tasks and protein representations for cross-scale evaluation
- **Citation**: Community standard benchmark

**Cross-Scale Linkage: ChEMBL Database**
- **Content**: ~2 million bioactive compounds with molecular→protein→cellular activity linkage
- **Properties**: Chemical structures (SMILES), target proteins (UniProt IDs), binding affinities, cellular assays
- **Usage**: Provides verified cross-scale ground truth connecting molecular and protein scales
- **Citation**: Gaulton et al. (2023)

**2.2.2 Dataset Curation Protocol**

**Pilot Dataset (10K pairs, Months 1-3):**

1. **Molecular Selection from ChEMBL**:
   - Filter compounds with complete structure information (valid SMILES, 3D conformations available)
   - Require binding affinity measurements (IC50, Ki, or Kd) for at least one protein target
   - Ensure chemical diversity: Tanimoto similarity < 0.7 between any pair using Morgan fingerprints
   - Target distribution: 60% drug-like molecules (Lipinski's rule), 40% diverse chemical space

2. **Protein Target Selection**:
   - Extract UniProt IDs for protein targets with ChEMBL binding data
   - Cross-reference with ProteinGym to ensure protein-level task availability
   - Require experimental structure (PDB) or high-confidence AlphaFold prediction
   - Cover diverse protein families: kinases (30%), GPCRs (25%), ion channels (15%), enzymes (30%)

3. **Cross-Scale Linkage Validation**:
   - Verify molecular→protein linkage completeness: both molecular properties (from PubChemQCR or quantum calculations) and protein properties (from ProteinGym) available
   - Require binding affinity measurements with confidence scores
   - Manual curation of 500 pairs to establish quality baseline
   - Automated validation pipeline for remaining 9,500 pairs

4. **Data Splits**:
   - Training: 70% (7,000 pairs)
   - Validation: 15% (1,500 pairs)
   - Test: 15% (1,500 pairs)
   - Stratified sampling ensuring protein family distribution preserved across splits
   - Molecular scaffold-based splitting to prevent data leakage

**Full Dataset (100K pairs, Months 4-9):**

Scale pilot curation protocol 10x with additional quality controls:
- Automated curation pipeline validated on pilot data
- Expanded protein family coverage (target: 50+ families)
- Increased chemical diversity (target: Tanimoto < 0.6)
- Multiple binding measurements per molecule-protein pair where available (for uncertainty quantification)

### 2.3 Scale-Transition Metrics: Mathematical Formulations

**2.3.1 Centered Kernel Alignment (CKA)**

CKA measures similarity between learned representations across scales by comparing representational geometry.

**Definition**: For molecular embeddings $\mathbf{X} \in \mathbb{R}^{n \times d_m}$ and protein embeddings $\mathbf{Y} \in \mathbb{R}^{n \times d_p}$ from $n$ molecule-protein pairs:

$$\text{CKA}(\mathbf{X}, \mathbf{Y}) = \frac{\text{HSIC}(\mathbf{K}_X, \mathbf{K}_Y)}{\sqrt{\text{HSIC}(\mathbf{K}_X, \mathbf{K}_X) \cdot \text{HSIC}(\mathbf{K}_Y, \mathbf{K}_Y)}}$$

where $\mathbf{K}_X$ and $\mathbf{K}_Y$ are kernel matrices computed using RBF kernel:

$$\mathbf{K}_X[i,j] = \exp\left(-\frac{\|\mathbf{x}_i - \mathbf{x}_j\|^2}{2\sigma^2}\right)$$

and HSIC (Hilbert-Schmidt Independence Criterion) is:

$$\text{HSIC}(\mathbf{K}_X, \mathbf{K}_Y) = \frac{1}{(n-1)^2}\text{tr}(\mathbf{K}_X \mathbf{H} \mathbf{K}_Y \mathbf{H})$$

with centering matrix $\mathbf{H} = \mathbf{I}_n - \frac{1}{n}\mathbf{1}_n\mathbf{1}_n^T$.

**Interpretation**:
- CKA $\in [0, 1]$
- CKA = 1: Perfect alignment (representations capture identical relational structure)
- CKA = 0: No alignment (representations are independent)
- **Threshold**: CKA > 0.7 indicates strong cross-scale alignment

**Implementation Details**:
- Kernel bandwidth $\sigma$ selected via median heuristic: $\sigma = \text{median}(\{\|\mathbf{x}_i - \mathbf{x}_j\|\}_{i \neq j})$
- Computed on validation set to prevent overfitting
- Averaged over 5 random subsamples (1,000 pairs each) for computational efficiency on large datasets

**2.3.2 Predictive Transfer Score (PTS)**

PTS quantifies how well molecular-level representations transfer to protein-level prediction tasks.

**Definition**: For a downstream protein property prediction task $T_{\text{protein}}$:

$$\text{PTS} = 1 - \frac{\mathcal{L}_{\text{transfer}} - \mathcal{L}_{\text{baseline}}}{\mathcal{L}_{\text{baseline}}}$$

where:
- $\mathcal{L}_{\text{baseline}}$: Loss when training protein predictor from scratch on protein representations
- $\mathcal{L}_{\text{transfer}}$: Loss when training protein predictor using frozen molecular embeddings as additional features

**Procedure**:
1. Train molecular encoder $f_m: \mathcal{M} \rightarrow \mathbb{R}^{d_m}$ on molecular tasks
2. Train protein encoder $f_p: \mathcal{P} \rightarrow \mathbb{R}^{d_p}$ on protein tasks
3. **Baseline**: Train protein property predictor $g: \mathbb{R}^{d_p} \rightarrow \mathbb{R}$ using only $f_p(\text{protein})$
4. **Transfer**: Train predictor $g': \mathbb{R}^{d_p + d_m} \rightarrow \mathbb{R}$ using concatenated $[f_p(\text{protein}), f_m(\text{molecule})]$ where molecule is the binding partner from ChEMBL linkage
5. Compute PTS using validation set performance

**Interpretation**:
- PTS = 1.0: Perfect transfer (molecular features fully explain protein properties)
- PTS = 0.0: No transfer benefit
- PTS < 0: Negative transfer (molecular features hurt performance)
- **Threshold**: PTS > 0.8 (≤20% accuracy drop) indicates good predictive transfer

**Tasks for PTS Evaluation**:
- Protein binding affinity prediction (regression, MSE loss)
- Protein function classification (multi-class, cross-entropy loss)
- Protein stability prediction (regression, MSE loss)

**2.3.3 End-to-End Consistency Score (EECS)**

EECS measures correlation between molecular-level predictions and protein-level ground truth across the full pipeline.

**Definition**: For molecule-protein pairs $\{(m_i, p_i)\}_{i=1}^n$ with protein property ground truth $\{y_i\}_{i=1}^n$:

$$\text{EECS} = \text{Pearson}(\{\hat{y}_i^{\text{mol}}\}_{i=1}^n, \{y_i\}_{i=1}^n)$$

where $\hat{y}_i^{\text{mol}} = h(f_m(m_i))$ is the prediction of protein property $y_i$ using only molecular representation $f_m(m_i)$ through learned mapping $h$.

**Procedure**:
1. Train molecular encoder $f_m$ on molecular tasks
2. Train cross-scale predictor $h: \mathbb{R}^{d_m} \rightarrow \mathbb{R}$ mapping molecular embeddings to protein properties using training set
3. Generate predictions $\hat{y}_i^{\text{mol}}$ on test set
4. Compute Pearson correlation with ground truth protein properties $y_i$

**Interpretation**:
- EECS $\in [-1, 1]$
- EECS > 0.6: Strong end-to-end consistency
- EECS < 0.3: Weak consistency (molecular representations insufficient for protein prediction)
- **Threshold**: EECS > 0.6 indicates meaningful cross-scale predictive power

**Statistical Significance**:
- Report 95% confidence intervals via bootstrap (1,000 resamples)
- Test significance: $H_0: \rho = 0$ vs. $H_1: \rho > 0$ using Fisher's z-transformation

### 2.4 Baseline Model Implementations

**2.4.1 Single-Scale Specialists**

**Molecular Specialist**:
- **Architecture**: Graph Isomorphism Network (GIN) implemented in PyTorch Geometric
- **Input**: Molecular graphs with node features (atom type, charge, hybridization) and edge features (bond type, aromaticity)
- **Layers**: 5 GIN layers with hidden dimension 256, batch normalization, ReLU activation
- **Pooling**: Global mean pooling for graph-level representation
- **Training**: Supervised on PubChemQCR molecular property prediction tasks (energy, dipole moment, HOMO-LUMO gap)
- **Hyperparameters**: Learning rate 1e-3, batch size 128, Adam optimizer, 100 epochs with early stopping

**Protein Specialist**:
- **Architecture**: ESM-2 (Evolutionary Scale Modeling) transformer
- **Input**: Protein sequences (amino acid sequences)
- **Model**: ESM-2 650M parameter pretrained model, fine-tuned on ProteinGym tasks
- **Training**: Fine-tuning on protein function prediction, stability prediction, binding site identification
- **Hyperparameters**: Learning rate 1e-5, batch size 32, AdamW optimizer, 50 epochs with early stopping

**2.4.2 Naive Multi-Scale Baseline**

**Architecture**: Feature concatenation approach
- Train molecular specialist $f_m$ and protein specialist $f_p$ independently
- For cross-scale tasks, concatenate embeddings: $\mathbf{z} = [f_m(m), f_p(p)]$
- Train task-specific head $g: \mathbb{R}^{d_m + d_p} \rightarrow \mathbb{R}$ on concatenated features
- **No explicit cross-scale alignment mechanism**

**Training Protocol**:
1. Pretrain $f_m$ on molecular tasks (PubChemQCR)
2. Pretrain $f_p$ on protein tasks (ProteinGym)
3. Freeze encoders, train task head on ChEMBL cross-scale tasks
4. Hyperparameters: Learning rate 1e-3, batch size 64, 50 epochs

**2.4.3 State-of-the-Art Multi-Scale Baseline**

**Architecture**: HoloProt-inspired hierarchical encoding
- **Molecular Encoder**: GIN (as above) producing $\mathbf{h}_m \in \mathbb{R}^{256}$
- **Protein Encoder**: ESM-2 (as above) producing $\mathbf{h}_p \in \mathbb{R}^{1280}$
- **Cross-Scale Attention Module**:

$$\mathbf{h}_m' = \mathbf{h}_m + \text{Attention}(\mathbf{Q}_m, \mathbf{K}_p, \mathbf{V}_p)$$

$$\mathbf{h}_p' = \mathbf{h}_p + \text{Attention}(\mathbf{Q}_p, \mathbf{K}_m, \mathbf{V}_m)$$

where $\mathbf{Q}_m = \mathbf{W}_Q^m \mathbf{h}_m$, $\mathbf{K}_p = \mathbf{W}_K^p \mathbf{h}_p$, $\mathbf{V}_p = \mathbf{W}_V^p \mathbf{h}_p$ (and vice versa)

- **Alignment Loss**: Contrastive loss encouraging aligned molecule-protein pairs:

$$\mathcal{L}_{\text{align}} = -\log \frac{\exp(\text{sim}(\mathbf{h}_m', \mathbf{h}_p') / \tau)}{\sum_{j=1}^B \exp(\text{sim}(\mathbf{h}_m', \mathbf{h}_{p_j}') / \tau)}$$

where $\text{sim}(\mathbf{u}, \mathbf{v}) = \mathbf{u}^T \mathbf{v} / (\|\mathbf{u}\| \|\mathbf{v}\|)$ and $\tau = 0.07$ (temperature)

**Training Protocol**:
1. Pretrain encoders independently (as naive baseline)
2. Joint training with multi-task loss:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{molecular}} + \mathcal{L}_{\text{protein}} + \lambda \mathcal{L}_{\text{align}} + \mathcal{L}_{\text{cross-scale}}$$

where $\lambda = 0.5$ balances alignment and task losses

3. Hyperparameters: Learning rate 5e-4, batch size 64, 100 epochs with cosine annealing

### 2.5 Experimental Design

**2.5.1 Hypothesis Testing Experiments**

**Experiment 1: Multi-Scale Performance Drop (H1)**

**Objective**: Test whether naive multi-scale models exhibit 20-40% performance drops at scale boundaries.

**Procedure**:
1. Train 20 naive multi-scale models with different random seeds
2. Compute CKA, PTS, EECS on test set for each model
3. Compare against single-scale specialist baselines (20 models each)

**Measurements**:
- CKA scores (expected: naive < 0.5)
- PTS scores (expected: >30% accuracy drop, PTS < 0.7)
- Per-scale accuracy on molecular and protein tasks

**Statistical Test**:
- One-way ANOVA comparing three conditions: single-scale specialist, naive multi-scale, SOTA multi-scale
- Post-hoc Tukey HSD for pairwise comparisons
- Significance level: $\alpha = 0.05$
- Effect size: Cohen's $f$ (expected: $f > 0.4$, medium-large effect)
- Power analysis: $n = 20$ models per condition achieves power > 0.8 for $f = 0.4$

**Falsification Criteria**:
- If naive multi-scale achieves CKA ≥ 0.7 without explicit mechanisms, H1 rejected
- If PTS shows ≤20% accuracy drop for naive approaches, H1 rejected

**Experiment 2: Explicit Mechanism Benefit (H2)**

**Objective**: Test whether SOTA multi-scale architectures achieve 15-25% better cross-scale consistency.

**Procedure**:
1. Train 15 paired models (naive vs. SOTA) with identical random seeds
2. Compute CKA, PTS, EECS for each pair
3. Measure improvement: $\Delta = (\text{SOTA} - \text{Naive}) / \text{Naive}$

**Measurements**:
- CKA improvement (expected: SOTA > 0.7, Naive < 0.5, improvement > 40%)
- PTS improvement (expected: SOTA > 0.8, Naive < 0.7, improvement > 15%)
- EECS improvement (expected: SOTA > 0.6, Naive < 0.5, improvement > 20%)

**Statistical Test**:
- Paired t-test (one-tailed) comparing naive vs. SOTA within each seed
- Significance level: $\alpha = 0.05$
- Effect size: Cohen's $d$ (expected: $d > 0.8$, large effect)
- Power analysis: $n = 15$ pairs achieves power > 0.8 for $d = 0.8$

**Falsification Criteria**:
- If SOTA improvement < 10% across all metrics, H2 rejected
- If CKA difference < 0.1, explicit mechanisms provide no measurable benefit

**Experiment 3: Specialist vs. Multi-Scale Trade-off (H3)**

**Objective**: Test whether multi-scale models sacrifice 5-15% per-scale performance for cross-scale consistency.

**Procedure**:
1. Evaluate all models (specialists, naive, SOTA) on per-scale tasks
2. Molecular tasks: PubChemQCR property prediction (MAE for energy, dipole)
3. Protein tasks: ProteinGym function prediction (accuracy, F1)
4. Compare per-scale performance vs. cross-scale consistency

**Measurements**:
- Per-scale accuracy: Molecular MAE, Protein F1
- Cross-scale consistency: CKA, PTS, EECS
- Trade-off quantification: Pareto frontier analysis

**Statistical Test**:
- Two-sample t-test comparing per-scale performance (specialists vs. multi-scale)
- Significance level: $\alpha = 0.05$ (two-tailed)
- Effect size: Cohen's $d$ (expected: $d = 0.5$, medium effect)
- Correlation analysis: Pearson correlation between per-scale accuracy and cross-scale consistency (expected: negative correlation, $r < -0.3$)

**Falsification Criteria**:
- If multi-scale models match specialist performance (difference < 3%), no trade-off exists
- If correlation between per-scale and cross-scale metrics is positive ($r > 0$), trade-off hypothesis rejected

**2.5.2 Metric Validation Experiments**

**Objective**: Validate that scale-transition metrics (CKA, PTS, EECS) correlate with downstream task performance.

**Procedure**:
1. Compute CKA, PTS, EECS for all models on validation set
2. Measure downstream task performance on held-out test tasks:
   - Binding affinity prediction (regression, Pearson $r$)
   - Drug efficacy prediction (classification, AUROC)
   - Protein-ligand interaction prediction (binary classification, F1)
3. Compute correlation between metrics and downstream performance

**Statistical Test**:
- Pearson correlation between each metric (CKA, PTS, EECS) and downstream task performance
- Significance test: $H_0: \rho = 0$ vs. $H_1: \rho > 0$
- Threshold: $r > 0.3$ indicates meaningful predictive validity
- Bootstrap confidence intervals (1,000 resamples)

**Success Criteria**:
- At least 2 of 3 metrics show $r > 0.3$ with downstream performance
- CKA and PTS expected to show strongest correlation ($r > 0.4$)

### 2.6 Evaluation Metrics

**Per-Scale Performance Metrics**:

**Molecular Scale**:
- Mean Absolute Error (MAE) for energy prediction: $\text{MAE} = \frac{1}{n}\sum_{i=1}^n |E_i - \hat{E}_i|$
- MAE for dipole moment prediction
- Classification accuracy for molecular property classification tasks

**Protein Scale**:
- F1 score for protein function classification: $F1 = 2 \cdot \frac{\text{precision} \cdot \text{recall}}{\text{precision} + \text{recall}}$
- Pearson correlation for protein stability prediction
- AUROC for binding site prediction

**Cross-Scale Metrics**:
- CKA (as defined in Section 2.3.1)
- PTS (as defined in Section 2.3.2)
- EECS (as defined in Section 2.3.3)

**End-to-End Task Metrics**:
- Binding affinity prediction: Pearson $r$, Spearman $\rho$, RMSE
- Drug efficacy prediction: AUROC, AUPRC, F1
- Molecular optimization for protein target: Success rate (% molecules with improved binding)

**Computational Efficiency Metrics**:
- Training time (GPU hours)
- Inference time (ms per prediction)
- Memory footprint (GB)
- Parameter count (millions)

### 2.7 Multi-Dimensional Leaderboard Design

**Leaderboard Structure**:

**Dimension A: Per-Scale Performance**
- Separate rankings for molecular tasks and protein tasks
- Allows single-scale specialists to demonstrate superiority at individual scales
- Metrics: Molecular MAE, Protein F1 (primary), plus task-specific metrics

**Dimension B: Cross-Scale Transfer**
- Rankings based on scale-transition metrics
- Highlights models optimized for cross-scale consistency
- Metrics: CKA (30%), PTS (40%), EECS (30%) weighted composite score

**Dimension C: End-to-End Tasks**
- Rankings on practical downstream applications
- Emphasizes real-world performance
- Metrics: Binding affinity Pearson $r$ (50%), Drug efficacy AUROC (30%), Optimization success rate (20%)

**Composite Score** (optional overall ranking):

$$S_{\text{composite}} = 0.3 \cdot S_{\text{per-scale}} + 0.4 \cdot S_{\text{cross-scale}} + 0.3 \cdot S_{\text{end-to-end}}$$

where each component is normalized to [0, 100] scale.

**Submission Requirements**:
- Open-source code with reproducible training scripts
- Model checkpoints and hyperparameter configurations
- Evaluation results on all three dimensions
- Computational cost reporting (GPU hours, memory)

**Evaluation Server**:
- Automated evaluation on held-out test set (refreshed quarterly)
- Prevents overfitting to public test set
- Returns scores within 24 hours
- Limits: 2 submissions per week per team

### 2.8 Reproducibility and Open Science

**Code Release**:
- Reference implementations of all metrics (CKA, PTS, EECS) in PyTorch
- Baseline model implementations (specialists, naive, SOTA)
- Data preprocessing and curation scripts
- Evaluation pipeline with standardized protocols
- Repository: GitHub with MIT license

**Data Release**:
- Curated 100K molecule-protein pairs with cross-scale linkage
- Standardized train/val/test splits with metadata
- Preprocessing code for PubChemQCR, ProteinGym, ChEMBL integration
- Data format: HDF5 for efficient loading, JSON for metadata

**Documentation**:
- Comprehensive tutorial notebooks (Jupyter)
- API documentation for all components
- Benchmark paper with detailed methodology
- Video tutorials for submission process

**Community Engagement**:
- Workshop at NeurIPS/ICML (Month 13)
- Benchmark competition with prizes (sponsored by industry partners)
- Quarterly leaderboard updates and analysis blog posts
- Slack/Discord community for discussions

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Outcome 1: Validated Scale-Transition Metrics**

We expect to demonstrate that CKA, PTS, and EECS provide meaningful, reproducible measurements of cross-scale consistency with the following characteristics:

- **Metric Validity**: Correlation with downstream task performance ($r > 0.3$, $p < 0.05$) for at least 2 of 3 metrics, with CKA and PTS showing strongest correlation ($r > 0.4$)
- **Discriminative Power**: Metrics successfully distinguish between model categories (naive vs. SOTA multi-scale) with large effect sizes (Cohen's $d > 0.8$)
- **Reproducibility**: Metric values stable across random seeds (coefficient of variation < 10%) and consistent across independent implementations

**Outcome 2: Empirical Validation of Multi-Scale Hypotheses**

The comprehensive experimental validation will provide definitive answers to three previously unanswerable questions:

- **H1 Validation**: Naive multi-scale models will exhibit 20-40% performance drops at scale boundaries (CKA < 0.5, PTS < 0.7), confirming that cross-scale integration without explicit mechanisms fails to maintain representational coherence
- **H2 Validation**: SOTA architectures with explicit transition mechanisms (hierarchical attention, alignment losses) will achieve 15-25% better cross-scale consistency (CKA > 0.7, PTS > 0.8), demonstrating measurable benefits of architectural design for multi-scale integration
- **H3 Validation**: Multi-scale models will show 5-15% per-scale performance degradation compared to specialists, revealing fundamental trade-offs between specialization and integration that inform model selection for specific applications

**Outcome 3: Unified Evaluation Infrastructure**

CrossScaleBench will provide the biological and chemical ML community with:

- **Curated Dataset**: 100,000 molecule-protein pairs with verified cross-scale linkage, standardized splits, and comprehensive metadata—the largest multi-scale biological ML benchmark
- **Reference Baselines**: Open-source implementations of single-scale specialists, naive multi-scale, and SOTA multi-scale models with documented hyperparameters and training protocols
- **Evaluation Server**: Automated evaluation platform processing submissions within 24 hours, preventing test set overfitting through quarterly refreshes
- **Multi-Dimensional Leaderboard**: Public rankings across three dimensions (per-scale, cross-scale, end-to-end) accommodating diverse community priorities

**Outcome 4: Community Adoption Indicators**

Based on ImageNet/GLUE precedents, we expect measurable adoption within 18 months:

- **Academic Adoption**: 50+ research groups submitting to leaderboard within 12 months of launch
- **Publication Impact**: 20+ papers citing CrossScaleBench in first year, establishing it as standard evaluation protocol
- **Industry Engagement**: 5+ pharmaceutical/materials companies using framework for internal model selection
- **Educational Use**: Integration into 10+ ML courses as standard benchmark for teaching multi-scale biological ML

### 3.2 Scientific Impact

**Advancing Multi-Scale ML Theory**

CrossScaleBench will establish cross-scale consistency as a fundamental evaluation dimension, analogous to how ImageNet established generalization and GLUE established transfer learning as core ML concepts. This theoretical contribution will:

- **Formalize Scale-Transition Quality**: Provide rigorous mathematical definitions (CKA, PTS, EECS) for measuring representation alignment across biological scales, enabling theoretical analysis of multi-scale architectures
- **Reveal Fundamental Trade-offs**: Empirically demonstrate trade-offs between per-scale optimization and cross-scale consistency, informing theoretical understanding of multi-task learning in hierarchical domains
- **Guide Architecture Design**: Establish design principles for multi-scale biological ML systems (e.g., "explicit alignment mechanisms improve cross-scale consistency by 15-25%"), accelerating architectural innovation

**Enabling New Research Directions**

The framework will unlock research questions currently impossible to address objectively:

- **Optimal Scale Integration Strategies**: Researchers can systematically compare hierarchical attention, graph neural networks with multi-resolution pooling, and transformer-based multi-scale architectures
- **Transfer Learning Across Scales**: Investigate whether pretraining at one scale (e.g., molecular) improves performance at another scale (e.g., protein) more effectively than single-scale pretraining
- **Multi-Fidelity Modeling**: Explore whether combining low-fidelity (fast, approximate) and high-fidelity (slow, accurate) models across scales improves efficiency-accuracy trade-offs

**Accelerating Research Efficiency**

Standardized evaluation will reduce duplicated effort:

- **Baseline Reimplementation**: Researchers currently spend 20-30% of project time reimplementing baselines across fragmented benchmarks. Unified framework reduces this to <5% (using reference implementations)
- **Fair Comparison**: Eliminates inconsistencies from different data splits, hyperparameter choices, and evaluation protocols that currently make cross-paper comparisons unreliable
- **Reproducibility**: Open-source code and standardized protocols increase reproducibility from current ~40% (estimated) to >80% for biological ML research

### 3.3 Industrial Translation Impact

**Drug Discovery Applications**

Pharmaceutical companies will benefit from objective model selection for critical tasks:

- **Molecular Optimization**: Predicting how molecular modifications affect protein binding (a quintessential cross-scale task) with quantified uncertainty via EECS scores
- **Target Identification**: Identifying protein targets for small molecules using models validated on cross-scale consistency metrics
- **ADMET Prediction**: Relating molecular structure to protein-mediated absorption, distribution, metabolism, excretion, and toxicity properties

**Expected Industry Adoption Pathway**:
1. **Months 13-18**: Pilot partnerships with 2-3 pharmaceutical companies for internal validation
2. **Year 2**: Integration into computational chemistry pipelines at 5+ companies
3. **Year 3**: Industry-sponsored benchmark extensions (e.g., ADMET-specific tasks, proprietary molecule-protein pairs)

**Materials Design Applications**

Materials informatics will leverage cross-scale evaluation for:

- **Structure-Property Relationships**: Relating atomic/molecular structure to macroscopic material properties (mechanical strength, conductivity, optical properties)
- **Catalyst Design**: Predicting catalytic activity from molecular structure and protein/enzyme environment
- **Polymer Engineering**: Optimizing monomer composition for desired polymer properties

**Reducing Adoption Barriers**:
- **Clear Performance Indicators**: Industry practitioners can select models based on leaderboard rankings rather than navigating fragmented academic literature
- **Standardized Interfaces**: Unified data formats and APIs reduce integration costs into existing computational pipelines
- **Uncertainty Quantification**: Confidence intervals and statistical significance testing enable risk-aware decision-making for high-stakes applications

### 3.4 Broader Impact on Scientific ML

**Cross-Domain Methodology Transfer**

CrossScaleBench's design principles will inform multi-scale benchmarking in other scientific domains:

- **Climate Modeling**: Evaluating models integrating atmospheric dynamics across spatial scales (local → regional → global)
- **Neuroscience**: Assessing models spanning neural scales (synaptic → cellular → circuit → systems)
- **Astrophysics**: Benchmarking simulations across cosmological scales (stellar → galactic → cosmic web)

**Contribution to Responsible AI**

The framework addresses key responsible AI considerations:

- **Transparency**: Multi-dimensional leaderboard reveals trade-offs (per-scale vs. cross-scale performance), enabling informed model selection rather than optimizing single metrics
- **Reproducibility**: Standardized protocols and open-source code reduce publication bias and increase research reliability
- **Accessibility**: Free, open-source infrastructure democratizes access to state-of-the-art evaluation tools, reducing barriers for researchers at under-resourced institutions

**Educational Impact**

CrossScaleBench will serve as pedagogical resource:

- **Teaching Multi-Scale ML**: Provides concrete examples and hands-on exercises for courses on scientific ML, multi-task learning, and transfer learning
- **Benchmark Competitions**: Student competitions (similar to ImageNet challenges) engage next generation of biological ML researchers
- **Open Science Model**: Demonstrates best practices for building community-driven research infrastructure

### 3.5 Long-Term Vision and Sustainability

**Phase 2 Expansion: Cellular Scale Integration**

Contingent on Phase 1 success, Phase 2 (Months 19-36) will extend framework to cellular scale:

- **Data Integration**: Incorporate cellular assay data from ChEMBL, linking molecular→protein→cellular activity
- **New Metrics**: Develop cellular-scale transition metrics measuring protein→cellular consistency
- **Three-Scale Evaluation**: Enable evaluation of models spanning molecular→protein→cellular scales

**Institutional Partnership Model**

Long-term sustainability requires institutional support:

- **Academic Partnership**: Host infrastructure at university research lab (e.g., MIT, Stanford, Cambridge) providing computational resources and student contributors
- **Industry Sponsorship**: Pharmaceutical/materials companies sponsor benchmark maintenance, competition prizes, and dataset expansion in exchange for early access to results
- **Community Governance**: Establish steering committee (academic + industry representatives) for benchmark evolution decisions

**Estimated Costs**:
- Infrastructure hosting: $10K/year (cloud computing, evaluation server)
- Dataset curation: $30K/year (postdoc effort for quality control, expansion)
- Community management: $20K/year (workshop organization, documentation maintenance)
- **Total**: $60K/year (sustainable via industry sponsorship model)

### 3.6 Success Metrics and Timeline

**12-Month Milestones**:
- Month 6: Pilot study complete, metrics validated ($r > 0.3$ with downstream tasks)
- Month 12: Full framework deployed, 100K dataset released, first leaderboard submissions
- Month 18: Workshop at major conference, 20+ submissions, community adoption demonstrated

**18-Month Success Criteria**:
- **Technical**: All three hypotheses validated with $p < 0.05$, effect sizes as predicted
- **Adoption**: 50+ research groups using framework, 20+ publications citing benchmark
- **Impact**: At least 2 industry partnerships established, framework integrated into 5+ computational pipelines

**Long-Term Impact Indicators (3-5 years)**:
- **Field Transformation**: CrossScaleBench becomes standard evaluation protocol cited in 100+ papers
- **Methodological Influence**: Scale-transition metrics adopted in other scientific ML domains
- **Practical Translation**: Demonstrable impact on drug discovery timelines or materials design efficiency (measured via industry partner case studies)

This research will fundamentally transform how the biological and chemical ML community evaluates multi-scale approaches, providing the standardized infrastructure necessary to accelerate both scientific discovery and industrial translation in life and materials sciences.