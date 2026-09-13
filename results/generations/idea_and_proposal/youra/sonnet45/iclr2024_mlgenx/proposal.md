# Research Proposal: Hierarchical Causal Mediation Framework for Genomics-Guided Drug Response Prediction

## 1. Title

**Hierarchical Causal Mediation Framework for Genomics-Guided Drug Response Prediction: Integrating Mendelian Randomization with Pathway-Constrained Graph Neural Networks**

## 2. Introduction

### 2.1 Background

Drug discovery and development face a critical challenge: approximately 90% of drug candidates fail in clinical trials, with lack of efficacy accounting for over 50% of these failures. This high attrition rate stems fundamentally from our limited mechanistic understanding of why patients respond differently to treatments. While genomics and multi-omics technologies have generated unprecedented volumes of biological data, translating these data into actionable therapeutic insights remains a formidable challenge.

Current approaches to understanding drug response mechanisms fall into two inadequate categories. First, correlational methods such as genome-wide association studies (GWAS) and SHAP-based interpretability provide statistical associations between genetic variants and outcomes but cannot establish causality or trace biological mechanisms. These approaches identify "what" is associated with drug response but not "why" or "how." Second, causal inference methods like standard Mendelian randomization (MR) can establish causality between genetic variants and outcomes but operate at a single biological scale, failing to illuminate the intermediate molecular pathways through which genetic effects propagate.

This gap has profound consequences for precision medicine. Clinicians lack patient-specific mechanistic insights to guide treatment selection. Regulatory agencies require mechanistic evidence for drug approval decisions. Drug developers cannot rationally design combination therapies targeting synergistic pathways. The field needs a framework that simultaneously achieves three objectives: (1) establishes causal validity through rigorous statistical inference, (2) provides biological interpretability by tracing mechanisms across molecular scales, and (3) delivers actionable predictions for clinical decision-making.

### 2.2 Research Objectives

This research proposes a **Hierarchical Causal Mediation Framework (HCMF)** that integrates Mendelian randomization with pathway-constrained graph neural networks to trace causally-validated mechanistic pathways from genetic variants through multi-omics molecular states to patient-specific drug responses. The framework leverages genomic variants as instrumental variables—exploiting the random assignment of alleles at conception to control for confounding—while incorporating biological pathway knowledge to ensure interpretability.

The specific objectives are:

**Objective 1:** Develop a hierarchical causal mediation model that decomposes genetic effects on drug response into pathway-specific mechanisms spanning genotype → transcriptome → proteome → pathway activity → clinical outcome.

**Objective 2:** Design pathway-constrained graph neural network architectures that respect known biological topology while learning data-driven refinements, enabling both mechanistic interpretability and predictive accuracy.

**Objective 3:** Implement counterfactual reasoning algorithms that generate patient-specific intervention predictions, supporting clinical decision-making and combination therapy design.

**Objective 4:** Validate the framework on large-scale pharmacogenomics datasets (1,000 cancer cell lines from GDSC, 500,000 participants from UK Biobank) across multiple drugs, demonstrating superior causal validity, interpretability, and prediction performance compared to existing methods.

### 2.3 Significance

This research addresses a critical gap identified in precision pharmacogenomics: no existing framework connects genetic variants to drug responses through interpretable, causally-validated molecular pathways spanning multiple biological scales. Success would deliver transformative advances across multiple domains:

**Scientific Impact:** The framework establishes theoretical foundations for hierarchical causal mediation in multi-scale biological systems, extending causal inference methodology to handle complex molecular networks with heterogeneous data types.

**Clinical Impact:** Patient-specific pathway identification enables mechanistic treatment selection, moving beyond empirical trial-and-error approaches. Counterfactual predictions support personalized dosing and combination therapy design based on individual molecular profiles.

**Regulatory Impact:** Causally-validated mechanistic evidence strengthens regulatory submissions, potentially accelerating drug approval timelines by providing biological plausibility alongside statistical associations.

**Drug Discovery Impact:** Identification of causal pathway synergies guides rational combination therapy development, while mechanistic insights into drug resistance inform next-generation therapeutic design.

The proposed framework is particularly timely given recent advances in multi-omics profiling technologies, large-scale biobanks with linked genomic and clinical data, and computational methods for causal inference and graph neural networks. By integrating these advances, this research aims to establish a new paradigm for mechanistic precision medicine.

## 3. Methodology

### 3.1 Overall Framework Architecture

The Hierarchical Causal Mediation Framework consists of four integrated layers:

**Layer 1 (Instrumental Variable Foundation):** Mendelian randomization establishes causal effects from genetic variants to drug response, leveraging random allele assignment to control confounding.

**Layer 2 (Pathway-Constrained Graph Neural Networks):** Graph attention networks incorporate biological pathway topology from curated databases (KEGG, Reactome, STRING, Gene Ontology) while learning data-driven refinements.

**Layer 3 (Hierarchical Mediation Analysis):** Multi-scale mediation decomposition quantifies pathway-specific effects across biological scales: genotype → transcriptome → proteome → pathway activity → drug response.

**Layer 4 (Counterfactual Reasoning):** Interventional calculus on the learned causal directed acyclic graph (DAG) generates patient-specific predictions for pathway perturbations.

### 3.2 Data Sources and Preprocessing

**Primary Datasets:**

1. **Genomics of Drug Sensitivity in Cancer (GDSC):** ~1,000 cancer cell lines with whole-genome sequencing, RNA-seq transcriptomics, proteomics (subset), and drug response measurements (IC50, AUC) for >100 compounds.

2. **UK Biobank:** ~500,000 participants with genotyping array data, proteomics measurements (subset via Olink platform), electronic health records, and medication histories.

3. **PharmGKB:** Curated pharmacogenomic variant-drug associations for validation and prior knowledge integration.

**Preprocessing Pipeline:**

- **Genomic variants:** Quality control (call rate >95%, Hardy-Weinberg equilibrium p>10⁻⁶), imputation to 1000 Genomes reference panel, minor allele frequency filtering (MAF >1%), linkage disequilibrium pruning (r² <0.2).

- **Transcriptomics:** TPM normalization, batch correction (ComBat-seq), log-transformation, removal of low-expression genes (mean TPM <1).

- **Proteomics:** Median normalization, missing value imputation (k-nearest neighbors), outlier detection (Tukey's method).

- **Drug response:** Standardization within each drug, outlier removal (>3 SD), binary classification for clinical outcomes (responder/non-responder based on validated thresholds).

### 3.3 Layer 1: Mendelian Randomization for Causal Inference

**Instrumental Variable Selection:**

For each drug, we identify genetic variants serving as instrumental variables (IVs) for multi-omics mediators. Valid IVs must satisfy three assumptions:

1. **Relevance:** Genetic variant strongly associates with the mediator (F-statistic >10)
2. **Independence:** Genetic variant is independent of confounders (ensured by random Mendelian inheritance)
3. **Exclusion restriction:** Genetic variant affects outcome only through the mediator

**Mathematical Formulation:**

Let $G_i$ denote genetic variant dosage (0, 1, 2), $M_i$ the mediator (e.g., gene expression), $Y_i$ the drug response, and $C_i$ confounders. The two-stage least squares (2SLS) estimator:

**Stage 1 (First-stage regression):**
$$M_i = \alpha_0 + \alpha_1 G_i + \alpha_2 C_i + \epsilon_i$$

**Stage 2 (Second-stage regression):**
$$Y_i = \beta_0 + \beta_1 \hat{M}_i + \beta_2 C_i + \nu_i$$

The causal effect estimate is $\hat{\beta}_1$, with standard errors computed via heteroskedasticity-robust methods.

**IV Validity Testing:**

- **F-statistic:** Test instrument strength via $F = \frac{(\text{RSS}_{\text{restricted}} - \text{RSS}_{\text{unrestricted}})/q}{\text{RSS}_{\text{unrestricted}}/(n-k)}$ where $q$ is number of instruments. Threshold: F >10.

- **Sargan test:** Test overidentification restrictions for multiple instruments: $J = n \cdot R^2_{\text{residuals}} \sim \chi^2_{q-1}$. Threshold: p >0.05.

**Sensitivity Analyses:**

To assess robustness to IV assumption violations, we implement:

1. **MR-Egger regression:** Allows directional pleiotropy, intercept term tests for bias
2. **Weighted median estimator:** Robust to 50% invalid instruments
3. **MR-PRESSO:** Detects and corrects for horizontal pleiotropy outliers

Concordance across methods (≥80% agreement) indicates robust causal estimates.

### 3.4 Layer 2: Pathway-Constrained Graph Neural Networks

**Graph Construction:**

We construct a multi-scale biological network $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where:

- **Nodes ($\mathcal{V}$):** Genetic variants, genes (transcripts), proteins, pathways
- **Edges ($\mathcal{E}$):** Variant-gene regulatory links (eQTL databases), protein-protein interactions (STRING), gene-pathway memberships (KEGG, Reactome, GO)

**Graph Attention Network Architecture:**

For node $i$ with feature vector $\mathbf{h}_i^{(l)}$ at layer $l$, the update rule:

$$\mathbf{h}_i^{(l+1)} = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij}^{(l)} \mathbf{W}^{(l)} \mathbf{h}_j^{(l)}\right)$$

where attention coefficients $\alpha_{ij}^{(l)}$ are computed via:

$$\alpha_{ij}^{(l)} = \frac{\exp\left(\text{LeakyReLU}\left(\mathbf{a}^T [\mathbf{W}\mathbf{h}_i \| \mathbf{W}\mathbf{h}_j]\right)\right)}{\sum_{k \in \mathcal{N}(i)} \exp\left(\text{LeakyReLU}\left(\mathbf{a}^T [\mathbf{W}\mathbf{h}_i \| \mathbf{W}\mathbf{h}_k]\right)\right)}$$

**Pathway Constraints:**

To enforce biological interpretability, we introduce pathway-specific attention masks:

$$\alpha_{ij}^{(l)} = \begin{cases} 
\alpha_{ij}^{(l)} & \text{if } (i,j) \in \mathcal{E}_{\text{pathway}} \text{ or } s_{ij} > \tau \\
0 & \text{otherwise}
\end{cases}$$

where $s_{ij}$ is a learned edge score and $\tau$ is a sparsity threshold. This allows data-driven edge discovery while maintaining pathway topology.

**Multi-Head Attention:**

We employ $K=8$ attention heads to capture diverse biological relationships:

$$\mathbf{h}_i^{(l+1)} = \|_{k=1}^K \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij}^{(l,k)} \mathbf{W}^{(l,k)} \mathbf{h}_j^{(l)}\right)$$

**Training Objective:**

The GNN is trained end-to-end with a composite loss function:

$$\mathcal{L} = \mathcal{L}_{\text{prediction}} + \lambda_1 \mathcal{L}_{\text{pathway}} + \lambda_2 \mathcal{L}_{\text{sparsity}}$$

where:
- $\mathcal{L}_{\text{prediction}}$: Cross-entropy (classification) or MSE (regression) for drug response
- $\mathcal{L}_{\text{pathway}}$: Pathway enrichment regularization encouraging known pathway activations
- $\mathcal{L}_{\text{sparsity}}$: L1 penalty on learned edge scores to prevent overfitting

### 3.5 Layer 3: Hierarchical Mediation Analysis

**Multi-Scale Mediation Decomposition:**

We decompose the total genetic effect into pathway-specific mediated effects across biological scales. For a causal chain $G \rightarrow T \rightarrow P \rightarrow W \rightarrow Y$ (genotype → transcriptome → proteome → pathway → outcome):

**Total effect:**
$$\text{TE} = \frac{\partial Y}{\partial G}$$

**Natural direct effect (NDE):**
$$\text{NDE} = \mathbb{E}[Y(G=1, M(G=0)) - Y(G=0, M(G=0))]$$

**Natural indirect effect (NIE) through pathway $p$:**
$$\text{NIE}_p = \mathbb{E}[Y(G=1, M_p(G=1)) - Y(G=1, M_p(G=0))]$$

**Proportion mediated through pathway $p$:**
$$\text{PM}_p = \frac{\text{NIE}_p}{\text{TE}}$$

**Estimation Procedure:**

We implement the mediation formula approach (Pearl, 2001; Imai et al., 2010):

1. Fit mediator model: $M_p = f_M(G, C) + \epsilon_M$
2. Fit outcome model: $Y = f_Y(G, M_p, C) + \epsilon_Y$
3. Compute counterfactual predictions:
   - $\hat{M}_p(G=0)$ and $\hat{M}_p(G=1)$ for each individual
   - $\hat{Y}(G=g, M_p=m)$ for all combinations
4. Average over population to obtain NIE and NDE estimates

**Uncertainty Quantification:**

Bootstrap confidence intervals (1,000 iterations) for mediation effects, accounting for estimation uncertainty in both mediator and outcome models.

### 3.6 Layer 4: Counterfactual Reasoning

**Causal DAG Learning:**

From the trained GNN and mediation analysis, we construct a causal DAG $\mathcal{D} = (\mathcal{V}, \mathcal{E}_{\text{causal}})$ where edges represent validated causal relationships (passing IV tests and mediation significance thresholds).

**Interventional Calculus:**

For a proposed intervention $do(M_p = m^*)$ on pathway $p$, we compute the expected outcome via the truncated factorization:

$$P(Y | do(M_p = m^*)) = \sum_{pa(M_p)} P(Y | M_p = m^*, pa(M_p)) P(pa(M_p))$$

where $pa(M_p)$ denotes parents of $M_p$ in the DAG.

**Patient-Specific Predictions:**

For individual $i$ with observed covariates $\mathbf{x}_i$:

1. Compute baseline prediction: $\hat{Y}_i = f_Y(\mathbf{x}_i)$
2. For each pathway intervention $do(M_p = m_p^*)$:
   - Propagate intervention through DAG using learned GNN
   - Compute counterfactual prediction: $\hat{Y}_i(do(M_p = m_p^*))$
3. Rank interventions by predicted benefit: $\Delta_p = \hat{Y}_i(do(M_p = m_p^*)) - \hat{Y}_i$

**Combination Therapy Design:**

For multi-pathway interventions $do(M_{p_1} = m_1^*, M_{p_2} = m_2^*)$, we assess synergy:

$$\text{Synergy}_{p_1, p_2} = \hat{Y}(do(M_{p_1}, M_{p_2})) - [\hat{Y}(do(M_{p_1})) + \hat{Y}(do(M_{p_2})) - \hat{Y}]$$

Positive synergy indicates super-additive effects, guiding combination therapy selection.

### 3.7 Experimental Design and Validation

**Training-Validation-Test Split:**

- **GDSC:** 60% training, 20% validation, 20% held-out test (stratified by cancer type and drug)
- **UK Biobank:** External validation cohort (no overlap with training)
- **Temporal validation:** PharmGKB data split by publication date (<2020 training, ≥2020 test)

**Cross-Validation Strategy:**

5-fold cross-validation on GDSC training set, with hyperparameter tuning on validation set. Final model evaluation on held-out test sets.

**Baseline Comparisons:**

1. **Direct GWAS:** Standard genome-wide association with Bonferroni correction
2. **SHAP-XGBoost:** Gradient boosting with SHAP interpretability
3. **Standard MR:** Single-scale Mendelian randomization (genotype → outcome)
4. **GSEA + Linear Models:** Gene set enrichment analysis with linear regression

**Evaluation Metrics:**

**Prediction Performance:**
- Classification: AUC-ROC, AUC-PR, F1-score, calibration error (ECE)
- Regression: R², RMSE, mean absolute error

**Causal Validity:**
- IV strength: F-statistic distribution, proportion F >10
- Overidentification: Sargan test p-values, proportion p >0.05
- Sensitivity concordance: Agreement across MR-Egger, weighted median, MR-PRESSO (≥80%)

**Interpretability:**
- Proportion mediated (PM): Percentage of drugs with PM ≥30%
- Pathway enrichment: FDR-corrected p-values for known pharmacogenes
- PharmGKB overlap: Proportion of identified pathways matching curated associations
- Expert evaluation: Oncologist ratings (1-5 scale) of pathway explanations for 100 cases

**Counterfactual Validation:**
- Perturbation agreement: Correlation between predicted and observed effects in CRISPR/RNAi screens (DepMap)
- Combination therapy validation: Agreement with clinical combination trial outcomes (literature)

**Statistical Testing:**

- Paired t-tests for metric comparisons between HCMF and baselines
- Bonferroni correction for multiple comparisons across drugs
- Significance threshold: p <0.05

### 3.8 Implementation Details

**Software and Hardware:**

- **Framework:** PyTorch 2.0 with PyTorch Geometric for GNN implementation
- **Distributed training:** PyTorch Distributed Data Parallel (DDP) across 4×NVIDIA V100 GPUs
- **Causal inference:** R packages (MendelianRandomization, mediation) interfaced via rpy2
- **Pathway databases:** KEGG REST API, Reactome graph database, STRING v11.5, Gene Ontology

**Hyperparameters:**

- GNN layers: 3, hidden dimensions: 256, attention heads: 8
- Learning rate: 0.001 (Adam optimizer), weight decay: 0.0001
- Dropout: 0.3, batch size: 64
- Pathway regularization weight ($\lambda_1$): 0.1, sparsity weight ($\lambda_2$): 0.01
- Training epochs: 100 with early stopping (patience=10)

**Computational Budget:**

- Estimated 200 GPU-hours total (~$500 cloud compute cost)
- Parallelization across 100 drugs: 2 GPU-hours per drug
- Scalability: Embarrassingly parallel, linear scaling to 1,000+ drugs

**Reproducibility:**

- Random seeds fixed across all experiments
- Code and trained models released on GitHub
- Preprocessed data deposited in Zenodo repository
- Detailed hyperparameter logs via Weights & Biases

### 3.9 Sensitivity and Robustness Analyses

**Pathway Database Sensitivity:**

Repeat analysis with four pathway database combinations:
1. KEGG only
2. Reactome only
3. KEGG + Reactome
4. KEGG + Reactome + STRING + GO (full ensemble)

Assess stability of pathway identifications across databases.

**GNN Architecture Sensitivity:**

Compare pathway-constrained GAT against:
1. Standard GAT (no pathway constraints)
2. Graph Convolutional Networks (GCN)
3. GraphSAGE
4. Fully connected neural network (no graph structure)

**IV Selection Sensitivity:**

Vary IV selection thresholds:
1. F-statistic: 5, 10, 20
2. MAF: 0.01, 0.05, 0.10
3. LD pruning: r² <0.1, 0.2, 0.5

**Unmeasured Confounding:**

Simulate unmeasured confounders with varying effect sizes and assess robustness via:
1. E-value calculation (minimum confounder strength to nullify results)
2. Negative control outcomes (outcomes known to be unrelated to drug response)

**Cross-Cohort Generalization:**

Assess transfer learning performance:
1. Train on GDSC cell lines, test on UK Biobank population cohorts
2. Train on one cancer type, test on others
3. Domain adaptation techniques (adversarial training, importance weighting)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes:**

**P1 (Mediation Discovery):** We expect to identify significant pathway-mediated effects (proportion mediated ≥30%) for ≥70% of drugs tested, with pathway enrichment achieving FDR <0.05 and ≥60% overlap with PharmGKB curated associations. This would demonstrate that genetic effects on drug response are substantially mediated through identifiable biological pathways.

**P2 (Prediction Performance):** The framework is expected to achieve drug response prediction AUC ≥0.75 (classification) or R² ≥0.3 (regression) with calibration error <0.1, outperforming ≥3 of 4 baseline methods on at least one primary metric while remaining competitive (within 10%) on others.

**P3 (Causal Validity):** IV validity tests should pass for ≥80% of genetic variants (F-statistic >10) and ≥70% of models (Sargan test p >0.05), with ≥80% concordance across MR sensitivity analyses, establishing robust causal inference.

**P4 (Interpretability):** Expert oncologist ratings of pathway explanations should average ≥4/5 for ≥60% of cases, significantly exceeding SHAP baseline interpretability (p <0.05 in paired comparisons).

**P5 (Counterfactual Validation):** Predicted intervention effects should agree with experimental perturbation data (CRISPR/RNAi screens) in ≥70% of cases, validating the counterfactual reasoning component.

**Secondary Outcomes:**

- **Computational Efficiency:** Complete analysis of 100 drugs within 200 GPU-hours, demonstrating scalability to genome-wide pharmacogenomics
- **Cross-Cohort Generalization:** Maintain ≥80% of in-cohort performance when transferring from GDSC to UK Biobank
- **Novel Pathway Discovery:** Identify ≥10 previously unreported drug-pathway associations validated by literature review
- **Combination Synergy Prediction:** Predict ≥5 synergistic pathway combinations validated by clinical trial data

**Falsification Criteria:**

The hypothesis will be rejected if ≥2 of the following occur:
- F1: Proportion mediated <30% for >50% of drugs
- F2: Pathway enrichment FDR >0.05 or PharmGKB overlap <40%
- F3: Prediction AUC <0.65 or R² <0.15
- F4: IV validity tests fail (F <10 for >30% variants OR Sargan p <0.05 for >40% models)
- F5: Counterfactual predictions agree <50% with perturbation data

### 4.2 Scientific Impact

**Theoretical Contributions:**

This research will establish foundational theory for hierarchical causal mediation in multi-scale biological systems, extending classical mediation analysis to handle:
1. Multiple mediators at different biological scales (transcriptome, proteome, pathways)
2. Network-structured mediators (pathways as graph-based entities)
3. High-dimensional genomic instruments with complex LD structures

The framework formalizes IV validity conditions for multi-omics causal inference, providing guidance for future pharmacogenomics studies.

**Methodological Advances:**

The integration of pathway-constrained graph neural networks with Mendelian randomization represents a novel synthesis of causal inference and deep learning. Key innovations include:
1. Biologically-informed attention mechanisms that balance data-driven learning with prior knowledge
2. Multi-scale mediation decomposition algorithms for network-structured mediators
3. Counterfactual reasoning on learned biological DAGs with uncertainty quantification

These methods are generalizable beyond pharmacogenomics to any domain requiring causal inference in multi-scale systems (e.g., climate science, economics).

**Benchmark Datasets:**

The research will produce standardized benchmark datasets for pharmacogenomics causal inference:
1. Harmonized GDSC multi-omics data with quality-controlled genetic variants
2. UK Biobank pharmacogenomics subset with linked proteomics
3. Curated perturbation validation datasets from DepMap and literature

These resources will accelerate future research by providing common evaluation frameworks.

### 4.3 Clinical and Translational Impact

**Precision Medicine Applications:**

The framework enables patient-specific pathway identification for treatment selection. For a patient with genomic profile $\mathbf{G}_i$, clinicians can:
1. Predict drug response probabilities across multiple therapies
2. Identify causal pathways driving predicted responses
3. Prioritize interventions targeting patient-specific vulnerabilities

This mechanistic approach moves beyond empirical trial-and-error, potentially reducing time to effective treatment and minimizing exposure to ineffective therapies.

**Regulatory Decision Support:**

Regulatory agencies (FDA, EMA) increasingly require mechanistic evidence for drug approvals, particularly for precision medicine indications. The framework provides:
1. Causally-validated biomarker-outcome relationships
2. Mechanistic explanations for subgroup efficacy differences
3. Quantified uncertainty for risk-benefit assessments

This could accelerate approval timelines for targeted therapies with strong mechanistic support.

**Combination Therapy Design:**

Rational combination therapy development requires understanding pathway synergies. The framework identifies:
1. Pathway pairs with super-additive effects (positive synergy)
2. Redundant pathways (negative synergy, avoid combination)
3. Patient subgroups most likely to benefit from combinations

This could reduce the combinatorial explosion in combination trial design, focusing resources on mechanistically-justified combinations.

**Drug Repurposing:**

By identifying causal pathways for existing drugs, the framework suggests repurposing opportunities:
1. Drugs targeting the same causal pathway may treat different diseases
2. Pathway-based similarity metrics identify repurposing candidates
3. Counterfactual predictions estimate repurposing efficacy

### 4.4 Drug Discovery Impact

**Target Identification and Validation:**

The framework addresses the critical bottleneck in target identification by:
1. Prioritizing targets with causal genetic evidence (reducing false positives)
2. Identifying pathway context dependencies (when/where targets are relevant)
3. Predicting on-target efficacy and off-target toxicity via pathway analysis

This could improve the success rate of early-stage drug discovery programs.

**Resistance Mechanism Elucidation:**

By comparing pathway activations between responders and non-responders, the framework identifies:
1. Bypass pathways conferring resistance
2. Genetic variants predisposing to resistance
3. Combination strategies to overcome resistance

This informs next-generation therapeutic design and patient stratification strategies.

**Biomarker Discovery:**

Causally-validated pathway biomarkers are more likely to generalize across populations than correlational biomarkers. The framework identifies:
1. Genetic biomarkers (germline variants) for patient selection
2. Molecular biomarkers (pathway activities) for response monitoring
3. Composite biomarkers integrating multi-omics data

### 4.5 Broader Impacts

**Educational Resources:**

The research will produce educational materials for interdisciplinary training:
1. Tutorial notebooks demonstrating causal inference in genomics
2. Lecture materials on integrating machine learning with causal reasoning
3. Case studies illustrating clinical translation of computational findings

**Open Science Contributions:**

All code, data, and models will be released under permissive licenses:
1. GitHub repository with documented implementation
2. Preprocessed datasets in standardized formats (Zenodo)
3. Trained models via Hugging Face Model Hub
4. Interactive web application for pathway exploration

**Interdisciplinary Collaboration:**

The framework bridges machine learning, genomics, and clinical medicine, fostering collaboration:
1. Joint publications with oncologists, geneticists, and computational scientists
2. Workshops at ML and genomics conferences (NeurIPS, ICML, ASHG, AACR)
3. Industry partnerships for clinical validation and deployment

### 4.6 Timeline and Milestones

**Months 1-3:** Data acquisition, preprocessing, and quality control; IV selection and validation

**Months 4-6:** GNN architecture development, pathway constraint implementation, initial training

**Months 7-9:** Mediation analysis implementation, counterfactual reasoning algorithms, baseline comparisons

**Months 10-12:** External validation (UK Biobank), sensitivity analyses, perturbation validation

**Months 13-15:** Expert evaluation studies, clinical case studies, manuscript preparation

**Months 16-18:** Code release, documentation, web application development, dissemination

**Key Milestones:**
- Month 6: First working prototype with GDSC validation results
- Month 9: Baseline comparisons complete, initial manuscript draft
- Month 12: External validation complete, submission to top-tier venue (Nature Medicine, Cell)
- Month 15: Expert evaluation complete, clinical case studies published
- Month 18: Full code release, web application launch, workshop presentations

### 4.7 Risk Mitigation and Contingency Plans

**Risk 1: IV Assumptions Violated**
- *Mitigation:* Comprehensive sensitivity analyses (MR-Egger, weighted median, MR-PRESSO)
- *Contingency:* If >40% of models fail IV tests, pivot to negative control outcome designs

**Risk 2: Pathway Databases Incomplete**
- *Mitigation:* Ensemble of multiple databases + data-driven edge learning
- *Contingency:* If pathway recall <40%, revert to unsupervised pathway discovery (e.g., non-negative matrix factorization)

**Risk 3: Error Propagation Across Scales**
- *Mitigation:* Bayesian uncertainty quantification, per-stage validation
- *Contingency:* If calibration error >0.2, implement conformal prediction for rigorous uncertainty bounds

**Risk 4: Cross-Cohort Generalization Failure**
- *Mitigation:* Domain adaptation techniques, transfer learning
- *Contingency:* If UK Biobank performance <60% of GDSC, develop cohort-specific models with meta-learning

**Risk 5: Computational Scalability**
- *Mitigation:* Distributed training, dimensionality reduction (PCA on proteomics)
- *Contingency:* If compute exceeds budget, prioritize top 50 drugs by clinical importance

This comprehensive research proposal establishes a rigorous, feasible, and impactful plan to develop and validate a hierarchical causal mediation framework for genomics-guided drug response prediction, with the potential to transform precision pharmacogenomics through causally-grounded, mechanistically-interpretable predictions.