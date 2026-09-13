# Research Proposal: BioConstruct-SC: A Psychometric Framework for Measuring Biological Representation Quality in Single-Cell Foundation Models

## 1. Introduction

### 1.1 Background

The emergence of single-cell foundation models represents a paradigm shift in computational biology. Models such as scGPT, Geneformer, and Universal Cell Embeddings (UCE) have demonstrated remarkable capabilities in extracting representations from high-dimensional single-cell transcriptomic data. These models promise to serve as universal feature extractors that capture the complexity of cellular states, enabling downstream applications ranging from cell type annotation to perturbation response prediction. The ultimate vision—articulated in recent work on AI-powered virtual cells—is to develop universal simulators of cellular function and behavior that can accelerate biological discovery and therapeutic development.

However, a fundamental problem plagues the field: we lack rigorous methods to measure what "meaningful representation" actually means. Current evaluation practices rely on task-specific metrics (accuracy, F1-score, silhouette coefficient) that cannot be compared across models or tasks. This fragmented evaluation landscape creates several critical issues. First, model selection becomes arbitrary, as practitioners cannot determine whether a model that excels at cell type classification will also perform well at trajectory inference. Second, progress measurement is obscured, since improvements on individual benchmarks may not reflect genuine advances in biological understanding. Third, the field cannot distinguish between models that truly capture biological mechanisms versus those that merely memorize dataset-specific patterns.

This evaluation crisis is not unique to biology. Educational and psychological testing faced similar challenges in the early 20th century, leading to the development of psychometric measurement theory. Item Response Theory (IRT), in particular, provides mathematical frameworks for measuring latent traits (such as cognitive ability) from observed response patterns. Over 70+ years, psychometrics has developed rigorous methods for establishing construct validity—the degree to which a test measures what it claims to measure—through convergent, discriminant, and criterion validity evidence.

### 1.2 Research Objectives

This research proposes BioConstruct-SC, a novel framework that adapts psychometric measurement theory to evaluate biological foundation models. Our primary objectives are:

1. **Develop a hierarchical IRT framework** for measuring biological representation quality as latent constructs, enabling fair cross-model comparison on common measurement scales.

2. **Identify and validate biological constructs** underlying foundation model performance through exploratory factor analysis of model-task performance matrices.

3. **Establish construct validity criteria** for biological representations using multi-source ground truth from ENCODE, Reactome, and Perturb-seq databases.

4. **Demonstrate predictive utility** by showing that construct validity scores predict generalization to held-out tasks better than raw performance metrics.

### 1.3 Significance

This research addresses the LMRL workshop's central question: "How can we evaluate the quality and utility of learned representations?" By importing established psychometric methodology, we provide the field with:

- **Operational definitions** of "meaningful representation" grounded in empirical evidence requirements
- **Common measurement scales** enabling fair comparison across architecturally diverse models
- **Construct-level diagnostics** revealing which aspects of biological understanding each model captures
- **Principled model selection criteria** based on validity evidence rather than arbitrary benchmark performance

The framework directly supports the workshop's goal of "developing open-source standardization of datasets and evaluation metrics for benchmarking new methods."

## 2. Methodology

### 2.1 Overview

BioConstruct-SC implements a four-step methodology: (1) exploratory factor analysis to identify biological constructs, (2) hierarchical IRT model specification, (3) ability parameter estimation, and (4) construct validity assessment. Figure 1 illustrates the complete pipeline.

### 2.2 Data Collection

#### 2.2.1 Foundation Model Selection

We will evaluate $n \geq 10$ single-cell foundation models spanning major architecture families:

- **Transformer-based:** scGPT, Geneformer, scBERT
- **Variational Autoencoder-based:** scVI, scANVI, LDVAE
- **Contrastive Learning-based:** UCE, scEMB
- **Hybrid architectures:** CellPLM, scFoundation

For each model, we obtain pre-trained weights from official repositories and extract cell embeddings using standardized preprocessing pipelines.

#### 2.2.2 Task Battery Construction

We construct a calibrated benchmark battery of $T = 80$ tasks spanning anticipated biological constructs:

| Construct Category | Example Tasks | Task Count |
|-------------------|---------------|------------|
| Cell Identity | Cell type classification, lineage prediction | 20 |
| Gene Regulation | GRN inference, TF activity prediction | 20 |
| Perturbation Response | Drug response, CRISPR effect prediction | 20 |
| Developmental Dynamics | Trajectory inference, pseudotime ordering | 20 |

Tasks are drawn from established benchmarks (scIB, BEELINE, Perturb-seq Atlas) and standardized to produce comparable performance metrics.

#### 2.2.3 Ground Truth Assembly

Multi-source biological ground truth is assembled from:

- **ENCODE:** ChIP-seq derived gene regulatory networks (GRNs)
- **Reactome/KEGG:** Curated pathway membership and interactions
- **Perturb-seq Atlas:** Experimentally validated perturbation effects

Consensus ground truth requires agreement from $\geq 2$ of 3 sources.

### 2.3 Step 1: Exploratory Factor Analysis

We construct a model-task performance matrix $\mathbf{P} \in \mathbb{R}^{M \times T}$ where $P_{mt}$ represents model $m$'s performance on task $t$.

#### 2.3.1 Preprocessing

Performance scores are standardized within tasks:
$$z_{mt} = \frac{P_{mt} - \bar{P}_t}{s_t}$$

where $\bar{P}_t$ and $s_t$ are the mean and standard deviation across models for task $t$.

#### 2.3.2 Dimensionality Determination

We apply parallel analysis and the Minimum Average Partial (MAP) criterion to determine the number of factors $K$:

$$\text{MAP}(k) = \frac{1}{T^2} \sum_{i \neq j} r_{ij(k)}^2$$

where $r_{ij(k)}$ is the partial correlation between tasks $i$ and $j$ after extracting $k$ factors.

#### 2.3.3 Factor Extraction

Principal axis factoring with oblimin rotation extracts $K$ factors:
$$\mathbf{Z} = \mathbf{\Lambda} \mathbf{F} + \mathbf{E}$$

where $\mathbf{\Lambda}$ is the factor loading matrix, $\mathbf{F}$ contains factor scores, and $\mathbf{E}$ represents unique variance.

Factor interpretability is assessed by examining loading patterns and mapping to biological construct categories.

### 2.4 Step 2: Hierarchical IRT Model Specification

Based on EFA results, we specify a bifactor IRT model capturing both general biological understanding and construct-specific abilities.

#### 2.4.1 Bifactor Model

For model $m$ on task $t$ belonging to construct $c$, the probability of "success" (performance above threshold) is:

$$P(Y_{mt} = 1 | \theta_m^{(g)}, \theta_m^{(c)}) = \frac{1}{1 + \exp(-[a_t^{(g)} \theta_m^{(g)} + a_t^{(c)} \theta_m^{(c)} - b_t])}$$

where:
- $\theta_m^{(g)}$ is model $m$'s general biological understanding
- $\theta_m^{(c)}$ is model $m$'s ability on construct $c$
- $a_t^{(g)}$ and $a_t^{(c)}$ are discrimination parameters
- $b_t$ is the task difficulty parameter

#### 2.4.2 Graded Response Extension

For continuous performance metrics, we employ a graded response model:

$$P(Y_{mt} \geq k | \boldsymbol{\theta}_m) = \frac{1}{1 + \exp(-[a_t^{(g)} \theta_m^{(g)} + a_t^{(c)} \theta_m^{(c)} - b_{tk}])}$$

where $b_{tk}$ represents the threshold for performance category $k$.

### 2.5 Step 3: Parameter Estimation

#### 2.5.1 Bayesian Estimation

Given the small sample size ($M \approx 10-15$), we employ Bayesian estimation with informative priors:

$$\theta_m^{(g)} \sim \mathcal{N}(0, 1)$$
$$\theta_m^{(c)} \sim \mathcal{N}(0, 1)$$
$$a_t \sim \mathcal{N}^+(1, 0.5)$$
$$b_t \sim \mathcal{N}(0, 2)$$

Posterior distributions are estimated via Markov Chain Monte Carlo (MCMC) using Stan or the mirt package in R.

#### 2.5.2 Convergence Diagnostics

We assess convergence using:
- Gelman-Rubin statistic: $\hat{R} < 1.1$
- Effective sample size: $n_{eff} > 400$
- Posterior predictive checks for model fit

#### 2.5.3 Uncertainty Quantification

Bootstrap resampling (B = 1000) provides confidence intervals for ability estimates:

$$\text{CI}_{95\%}(\theta_m^{(g)}) = [\theta_m^{(g)*}_{(0.025)}, \theta_m^{(g)*}_{(0.975)}]$$

### 2.6 Step 4: Construct Validity Assessment

#### 2.6.1 Convergent Validity

Models should produce similar embeddings for biologically similar cell types across independent datasets. We compute:

$$r_{conv} = \text{corr}(\mathbf{e}_m^{(D_1)}, \mathbf{e}_m^{(D_2)})$$

where $\mathbf{e}_m^{(D_i)}$ represents model $m$'s embeddings for matched cell types in dataset $D_i$.

**Criterion:** $r_{conv} > 0.7$ indicates strong convergent validity.

#### 2.6.2 Discriminant Validity

Embeddings should separate functionally distinct cell types. We compute silhouette scores:

$$s_m = \frac{1}{N} \sum_{i=1}^{N} \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

where $a(i)$ is the mean intra-cluster distance and $b(i)$ is the mean nearest-cluster distance.

**Criterion:** $s_m > 0.3$ indicates adequate discriminant validity.

#### 2.6.3 Criterion Validity

Model predictions should correlate with multi-source biological ground truth:

$$r_{crit} = \text{corr}(\hat{y}_m, y_{consensus})$$

where $y_{consensus}$ requires agreement from $\geq 2$ of 3 ground truth sources.

**Criterion:** $r_{crit} > 0.5$ indicates acceptable criterion validity.

### 2.7 Experimental Validation

#### 2.7.1 Primary Experiment: Validity-Generalization Relationship

**Design:** Split tasks into training (60 tasks) and held-out (20 tasks) sets. Compute construct validity scores using training tasks only. Evaluate generalization on held-out tasks.

**Hypothesis Test:** Models with high validity (meeting all three criteria) will show superior held-out performance compared to models with high training performance but low validity.

**Statistical Test:** Independent samples t-test or Mann-Whitney U, $\alpha = 0.05$

**Expected Effect Size:** Cohen's $d > 0.5$

#### 2.7.2 Secondary Experiment: Model Comparison

**Design:** Compare bifactor IRT model against single-factor model and raw performance aggregation.

**Metrics:**
- Model fit: $\Delta$BIC, $\Delta$AIC (bifactor vs. single-factor)
- Ranking consistency: Spearman correlation between IRT rankings and aggregate rankings
- Information gain: Variance explained by construct-specific factors

**Success Criteria:**
- $\Delta$BIC $> 10$ favoring bifactor model
- Ranking correlation $r > 0.6$ with additional construct-specific information

#### 2.7.3 Evaluation Metrics Summary

| Metric | Purpose | Threshold |
|--------|---------|-----------|
| Factor interpretability | Construct identification | $\geq 3$ tasks loading $> 0.4$ per factor |
| Model fit (RMSEA) | IRT model adequacy | RMSEA $< 0.08$ |
| Convergent validity | Embedding consistency | $r > 0.7$ |
| Discriminant validity | Cell type separation | Silhouette $> 0.3$ |
| Criterion validity | Ground truth alignment | $r > 0.5$ |
| Generalization prediction | Framework utility | Cohen's $d > 0.5$ |

### 2.8 Implementation

All code will be released as an open-source Python package with:
- Standardized task battery with preprocessing scripts
- IRT estimation using `mirt-py` or `pystan`
- Validity assessment modules
- Visualization and reporting tools

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome:** A validated psychometric framework demonstrating that biological representation quality can be measured as latent constructs. We expect to identify 2-4 interpretable biological constructs (e.g., cell identity, gene regulation, perturbation response, developmental dynamics) with distinct model ability profiles.

**Secondary Outcomes:**
1. Empirical evidence that construct validity predicts generalization better than raw performance metrics
2. A calibrated task battery serving as a community benchmark
3. Model rankings on common scales enabling principled model selection
4. Identification of construct-specific strengths and weaknesses across architecture families

### 3.2 Potential Limitations

- **Small sample size:** With only 10-15 models, statistical power is limited. Bayesian estimation and bootstrap uncertainty quantification partially address this.
- **Domain specificity:** Results may not generalize to protein language models or multi-scale models.
- **Ground truth incompleteness:** Biological knowledge is incomplete; criterion validity assessment is bounded by available annotations.

### 3.3 Broader Impact

**For the LMRL Community:** BioConstruct-SC provides the "appropriate methods for evaluating the quality of embeddings" called for in the workshop description. By operationalizing "meaningful representation" through construct validity evidence, we enable principled comparison across the growing landscape of biological foundation models.

**For Foundation Model Development:** Construct-level diagnostics reveal which aspects of biological understanding models capture, guiding architectural improvements and training strategies.

**For Downstream Applications:** Practitioners gain principled model selection criteria based on validity evidence rather than arbitrary benchmark performance, improving reliability of biological discoveries.

**Toward Virtual Cells:** By establishing rigorous evaluation methodology, this work contributes to the foundation needed for "universal simulators of cellular function and behavior"—ensuring that the representations underlying such simulators truly capture biological reality.

### 3.4 Future Directions

This framework establishes foundations for:
- Extension to multi-modal and multi-scale biological representations
- Adaptive testing procedures for efficient model evaluation
- Longitudinal tracking of field progress on common measurement scales
- Integration with active learning for experimental design

By importing the rigor of psychometric measurement theory into biological representation learning, BioConstruct-SC transforms the evaluation of foundation models from an ad hoc collection of benchmarks into a principled measurement science.