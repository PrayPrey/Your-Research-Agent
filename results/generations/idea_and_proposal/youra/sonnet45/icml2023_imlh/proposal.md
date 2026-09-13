# Research Proposal: Bidirectional Uncertainty Propagation in Hybrid Symbolic-Neural Systems for Safe Clinical Decision Support

## 1. Title

**Bidirectional Uncertainty Propagation in Hybrid Symbolic-Neural Systems for Safe Clinical Decision Support: Integrating Medical Knowledge Graphs with Deep Learning through Variational Inference**

---

## 2. Introduction

### 2.1 Background

The integration of machine learning (ML) into healthcare has accelerated dramatically, with applications spanning diagnostic prediction, treatment recommendation, and patient risk stratification. However, the deployment of ML systems in clinical settings faces critical adoption barriers that stem from fundamental limitations in current approaches. Black-box neural models, while achieving impressive predictive performance on benchmark datasets, fail silently on unfamiliar patients, lack interpretability for clinicians who must justify medical decisions, and cannot meet the multi-stakeholder trust requirements essential for healthcare applications.

Current medical AI systems exhibit three critical gaps that impede clinical adoption:

**Safety Gap**: Neural models trained on historical data perform poorly on out-of-distribution (OOD) patients—those from underrepresented demographic groups, presenting with rare disease combinations, or treated at hospitals with different clinical protocols. Weng et al. (2025) demonstrated that OOD detection can filter patients where model performance degrades significantly, yet existing approaches rely solely on statistical distribution shift detection without leveraging domain knowledge about medical plausibility.

**Interpretability Gap**: Clinicians require explanations that align with clinical reasoning processes to trust AI recommendations. Imrie et al. (2023) identified that different stakeholders—clinicians, patients, and regulators—have distinct interpretability needs: clinicians need causal explanations grounded in medical knowledge, patients need understandable risk communication, and regulators need auditable compliance traces. Current explainable AI (XAI) methods provide either learned patterns (attention mechanisms, saliency maps) or symbolic rules, but not both in a unified framework.

**Uncertainty Quantification Gap**: Medical decision-making inherently involves uncertainty from multiple sources: noisy clinical measurements (aleatoric uncertainty), limited training data (epistemic uncertainty), and incomplete medical knowledge. López et al. (2025) surveyed uncertainty quantification methods for healthcare AI, emphasizing the need for calibrated confidence estimates that align predicted probabilities with actual correctness. However, existing UQ approaches operate on neural models in isolation, without incorporating structured medical knowledge that could inform uncertainty estimates.

Existing research has demonstrated **pairwise integrations** of these components:

- **Knowledge Graphs + Deep Learning** (without UQ): Alawad et al. (2021) showed that integrating UMLS medical knowledge graphs with word embeddings improved cancer phenotyping by 22.5% macro-F1, demonstrating that domain knowledge provides valuable inductive bias for clinical prediction tasks.

- **Hybrid Symbolic-Neural Reasoning** (without UQ): Domingues (2026) developed a hybrid framework combining OWL2 ontologies with SWRL rules, achieving 78% reduction in clinical guideline violations. This work validated that symbolic constraints can align AI predictions with established medical knowledge.

- **Deep Learning + Uncertainty Quantification** (without symbolic knowledge): Abdar et al. (2022) established the need for separating epistemic and aleatoric uncertainty in medical AI, providing practical guidelines for trustworthy clinical decision support through probabilistic modeling.

However, **no existing framework unifies all three components**—symbolic medical knowledge, deep learning, and uncertainty quantification—with bidirectional uncertainty propagation. This creates a critical safety gap: models cannot reliably identify when they are uncertain about predictions, cannot explain predictions through clinical reasoning pathways grounded in medical knowledge, and cannot leverage domain expertise to improve uncertainty calibration.

### 2.2 Research Objectives

This research proposes **BK-DL (Bayesian Knowledge-Deep Learning)**, the first framework integrating medical knowledge graphs (UMLS), graph neural networks, and uncertainty quantification through variational inference with **bidirectional uncertainty flow**. The core innovation is treating medical knowledge graphs as **probabilistic generative models** within a variational inference framework, enabling uncertainty to propagate in both directions:

- **Neural → Symbolic**: Prediction uncertainty from data-driven learning propagates through symbolic reasoning (evidential uncertainty: "how confident is the data-driven prediction?")
- **Symbolic → Neural**: Constraint violations from knowledge graph reasoning inform neural uncertainty estimates (epistemic uncertainty: "does the prediction contradict known medical knowledge?")

**Primary Objective**: Develop and validate a hybrid symbolic-neural framework that improves clinical decision support safety through enhanced out-of-distribution detection (≥8% OOD AUROC improvement) and better uncertainty calibration (≥15% Expected Calibration Error reduction) compared to neural-only and hybrid-without-UQ baselines.

**Secondary Objectives**:

1. **Theoretical Contribution**: Formalize bidirectional uncertainty propagation in hybrid architectures through an extended variational inference objective that incorporates knowledge graph constraints as probabilistic priors.

2. **Methodological Contribution**: Develop novel methods for (a) evidence-graded probabilistic knowledge graph construction from medical literature, (b) disease-specific subgraph sampling for scalable reasoning, (c) hybrid OOD detection combining neural uncertainty signals with symbolic violation detection, and (d) variational inference with knowledge graph constraints.

3. **Practical Contribution**: Demonstrate clinical utility through user studies measuring dual interpretability effectiveness (learned patterns + symbolic reasoning traces) for multi-stakeholder trust, targeting clinician-rated explanation usefulness ≥4.0/5.0 and trust calibration correlation ≥0.75.

### 2.3 Research Significance

This research addresses a critical need in healthcare AI: developing systems that are not only accurate but also **safe, interpretable, and trustworthy** for high-stakes clinical decision-making. The significance spans multiple dimensions:

**Clinical Impact**: By providing calibrated uncertainty estimates and hybrid OOD detection, BK-DL enables clinicians to identify cases requiring additional scrutiny, reducing diagnostic errors and adverse events. Target use cases include sepsis early detection (where delayed treatment increases mortality 7.6% per hour), differential diagnosis for complex cases with overlapping symptoms, and treatment recommendation with automated contraindication checking.

**Theoretical Advancement**: BK-DL establishes the first formal framework for propagating uncertainty **through** symbolic medical knowledge rather than around it. This extends variational inference theory to hybrid architectures, enabling principled decomposition of uncertainty sources (data noise, model limitations, knowledge incompleteness) and providing theoretical foundations for future research in knowledge-intensive AI domains beyond healthcare.

**Methodological Innovation**: The proposed methods for probabilistic knowledge graph construction, hybrid OOD detection, and dual interpretability generation provide reusable components for other medical AI applications. The framework's modular design enables independent validation of each component, facilitating incremental adoption in clinical settings.

**Regulatory and Deployment Pathway**: By providing auditable symbolic reasoning traces alongside learned patterns, BK-DL addresses regulatory requirements for medical AI transparency. The dual interpretability approach supports FDA Software as Medical Device (SaMD) documentation requirements, potentially accelerating clinical deployment timelines.

**Broader Implications**: While focused on healthcare, the framework generalizes to other knowledge-intensive domains (legal reasoning, scientific discovery, engineering design) where domain expertise must be integrated with data-driven learning under uncertainty. Success in medical AI could catalyze adoption of hybrid symbolic-neural approaches across high-stakes decision-making applications.

---

## 3. Methodology

### 3.1 Research Design Overview

The research follows a **comparative effectiveness design** with four phases: (1) probabilistic knowledge graph construction, (2) hybrid model development, (3) quantitative evaluation against baselines, and (4) qualitative user studies for interpretability validation. The methodology integrates theoretical formalization, algorithmic development, and empirical validation to test the core hypothesis that bidirectional uncertainty propagation improves clinical decision support safety and interpretability.

**Datasets**:
- **In-distribution training/testing**: MIMIC-III or MIMIC-IV (Medical Information Mart for Intensive Care), containing de-identified health records from ~40,000 ICU patients with structured clinical data (demographics, vital signs, lab results, diagnoses, medications)
- **Out-of-distribution testing**: eICU Collaborative Research Database (~200,000 patient admissions from multiple hospitals) for distribution shift evaluation
- **Medical knowledge**: UMLS Metathesaurus (2024 release, 4M+ concepts, 14M+ relations), domain-specific OWL2 ontologies (SNOMED CT, ICD-10)

**Clinical Tasks**: Diagnosis prediction (sepsis, acute kidney injury, in-hospital mortality), treatment recommendation (antibiotic selection)

### 3.2 Phase 1: Probabilistic Knowledge Graph Construction

**Objective**: Construct medical knowledge graphs with probabilistic edge weights reflecting uncertainty in medical knowledge, initialized from literature evidence strength.

#### 3.2.1 UMLS Knowledge Graph Extraction

**Step 1: Concept Identification**
- Extract UMLS concepts relevant to target clinical tasks (sepsis, AKI, mortality) using semantic types: Disease or Syndrome (T047), Sign or Symptom (T184), Laboratory Procedure (T059), Pharmacologic Substance (T121)
- Filter concepts by clinical relevance: retain concepts appearing in ≥10 MIMIC-III patient records
- Result: Disease-specific concept sets $\mathcal{C}_{\text{sepsis}}$, $\mathcal{C}_{\text{AKI}}$, $\mathcal{C}_{\text{mortality}}$

**Step 2: Relation Extraction**
- Extract UMLS relations between concepts: "may_treat", "may_cause", "associated_with", "contraindicated_with", "is_a" (hierarchical)
- Construct directed knowledge graph $G = (\mathcal{V}, \mathcal{E})$ where:
  - Nodes $\mathcal{V}$: UMLS concepts (diseases, symptoms, medications, procedures)
  - Edges $\mathcal{E}$: UMLS relations with types $r \in \mathcal{R}$

#### 3.2.2 Evidence-Graded Probabilistic Annotation

**Step 3: Literature Evidence Extraction**
- Parse medical literature abstracts from PubMed (using BioBERT for biomedical NER) to extract evidence grading annotations
- Map evidence levels to probability values using GRADE system:

$$p_{\text{edge}}(e_{ij}) = \begin{cases}
0.95 & \text{Level I: Systematic review/meta-analysis} \\
0.85 & \text{Level II: Randomized controlled trial} \\
0.75 & \text{Level III: Cohort study} \\
0.65 & \text{Level IV: Case-control study} \\
0.55 & \text{Level V: Expert opinion/case report} \\
0.50 & \text{No evidence found (uniform prior)}
\end{cases}$$

**Step 4: Probabilistic Edge Weight Initialization**
- For each edge $e_{ij} \in \mathcal{E}$ (relation from concept $i$ to concept $j$):
  - Initialize weight $w_{ij} = p_{\text{edge}}(e_{ij})$ from literature evidence
  - If multiple evidence sources exist, aggregate via weighted average: $w_{ij} = \frac{\sum_k n_k \cdot p_k}{\sum_k n_k}$ where $n_k$ is sample size of study $k$
  - Mark edges as **learnable parameters** for fine-tuning during training

**Step 5: Disease-Specific Subgraph Sampling**
- For each patient with symptoms/diagnoses $\{c_1, c_2, \ldots, c_m\}$:
  - Perform breadth-first search (BFS) from patient concepts in $G$
  - Extract $k$-hop neighborhood subgraph $G_{\text{patient}} = (\mathcal{V}_{\text{sub}}, \mathcal{E}_{\text{sub}})$ where $k=3$ (covers direct relations + 2 intermediate hops)
  - If $|\mathcal{E}_{\text{sub}}| > N_{\text{max}}$ (e.g., 10,000 edges), rank edges by $w_{ij} \times \text{frequency}_{\text{literature}}$ and retain top-$N_{\text{max}}$
- Result: Patient-specific probabilistic knowledge graph for each clinical case

### 3.3 Phase 2: Hybrid Model Development

**Objective**: Develop BK-DL framework integrating graph neural networks with variational inference for bidirectional uncertainty propagation.

#### 3.3.1 Architecture Overview

The BK-DL model consists of three components:

1. **Patient Encoder**: Encodes structured clinical data (demographics, vital signs, lab results) into feature vector $\mathbf{x} \in \mathbb{R}^d$
2. **Knowledge Graph Encoder**: Graph neural network encoding patient-specific subgraph $G_{\text{patient}}$ with uncertainty-aware Bayesian layers
3. **Variational Inference Module**: Propagates uncertainty bidirectionally between neural and symbolic components

#### 3.3.2 Patient Data Encoding

**Input Representation**:
- Demographics: Age, gender, ethnicity (one-hot encoded)
- Vital signs: Heart rate, blood pressure, temperature, respiratory rate (time-series aggregated via mean, std, min, max over 24-hour window)
- Lab results: Creatinine, white blood cell count, lactate, etc. (normalized to z-scores)
- Medical history: Prior diagnoses (multi-hot encoding of ICD-10 codes)

**Encoder Architecture**:
$$\mathbf{x} = \text{MLP}_{\text{patient}}([\mathbf{x}_{\text{demo}}, \mathbf{x}_{\text{vitals}}, \mathbf{x}_{\text{labs}}, \mathbf{x}_{\text{history}}])$$

where MLP is a 2-layer feedforward network with ReLU activations, output dimension $d=256$.

#### 3.3.3 Graph Neural Network with Bayesian Layers

**GNN Architecture**: Graph Attention Network (GAT) with Bayesian linear layers for epistemic uncertainty quantification.

**Message Passing**:
For each node $v_i \in \mathcal{V}_{\text{sub}}$ in patient subgraph:

$$\mathbf{h}_i^{(l+1)} = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij} \mathbf{W}^{(l)} \mathbf{h}_j^{(l)}\right)$$

where:
- $\mathbf{h}_i^{(l)}$: Node embedding at layer $l$ (initialized with UMLS concept embeddings from BioBERT)
- $\mathbf{W}^{(l)}$: **Bayesian linear layer** with weight distribution $q(\mathbf{W}^{(l)}) = \mathcal{N}(\boldsymbol{\mu}_W, \text{diag}(\boldsymbol{\sigma}_W^2))$
- $\alpha_{ij}$: Attention coefficient computed as:

$$\alpha_{ij} = \frac{\exp(\text{LeakyReLU}(\mathbf{a}^T [\mathbf{W}\mathbf{h}_i \| \mathbf{W}\mathbf{h}_j \| w_{ij}]))}{\sum_{k \in \mathcal{N}(i)} \exp(\text{LeakyReLU}(\mathbf{a}^T [\mathbf{W}\mathbf{h}_i \| \mathbf{W}\mathbf{h}_k \| w_{ik}]))}$$

Note: Attention incorporates probabilistic edge weight $w_{ij}$ to weight relations by evidence strength.

**Graph Readout**:
Aggregate node embeddings to graph-level representation:

$$\mathbf{z}_{\text{graph}} = \text{READOUT}(\{\mathbf{h}_i^{(L)} : v_i \in \mathcal{V}_{\text{sub}}\}) = \frac{1}{|\mathcal{V}_{\text{sub}}|} \sum_{i} \mathbf{h}_i^{(L)}$$

**Combined Representation**:
Concatenate patient features and graph embedding:

$$\mathbf{z} = [\mathbf{x}, \mathbf{z}_{\text{graph}}] \in \mathbb{R}^{2d}$$

#### 3.3.4 Variational Inference Framework

**Probabilistic Model**:

- **Prior** (constrained by knowledge graph): $p(\mathbf{z} | G) = \mathcal{N}(\boldsymbol{\mu}_{\text{KG}}, \boldsymbol{\Sigma}_{\text{KG}})$
  - Mean $\boldsymbol{\mu}_{\text{KG}}$ computed from graph structure (e.g., graph convolution on $G$)
  - Covariance $\boldsymbol{\Sigma}_{\text{KG}}$ reflects uncertainty in knowledge graph (function of edge weight variances)

- **Approximate Posterior** (neural encoder): $q(\mathbf{z} | \mathbf{x}, G) = \mathcal{N}(\boldsymbol{\mu}_{\text{enc}}(\mathbf{x}, G), \boldsymbol{\Sigma}_{\text{enc}}(\mathbf{x}, G))$
  - Encoder outputs mean and log-variance: $\boldsymbol{\mu}_{\text{enc}}, \log \boldsymbol{\sigma}_{\text{enc}}^2 = \text{GNN}(\mathbf{x}, G)$

- **Likelihood**: $p(y | \mathbf{z}, \mathbf{x}, G)$ where $y$ is diagnosis label
  - Decoder: $p(y | \mathbf{z}) = \text{Softmax}(\text{MLP}_{\text{decoder}}(\mathbf{z}))$

**Evidence Lower Bound (ELBO)**:

The training objective maximizes the ELBO:

$$\mathcal{L}_{\text{ELBO}} = \mathbb{E}_{q(\mathbf{z}|\mathbf{x},G)}[\log p(y | \mathbf{z}, \mathbf{x}, G)] - \beta \cdot \text{KL}[q(\mathbf{z}|\mathbf{x},G) \| p(\mathbf{z}|G)] - \lambda \cdot \mathcal{L}_{\text{constraint}}$$

where:

1. **Likelihood term**: Supervised loss on diagnosis prediction (cross-entropy)
2. **KL divergence term**: Regularizes latent space to align with knowledge graph prior, weighted by $\beta$ (annealed from 0 to 1 during training)
3. **Constraint violation term**: Penalizes predictions violating knowledge graph relations

$$\mathcal{L}_{\text{constraint}} = \sum_{(i,j) \in \mathcal{E}_{\text{sub}}} w_{ij} \cdot \mathbb{1}[\text{prediction violates relation } r_{ij}]$$

Example: If KG contains "symptom X → disease Y" with $w_{ij}=0.9$, but model predicts "not disease Y" despite symptom X present, incur penalty $0.9 \times 1$.

**Reparameterization Trick**:
Sample latent variable via:

$$\mathbf{z} = \boldsymbol{\mu}_{\text{enc}} + \boldsymbol{\sigma}_{\text{enc}} \odot \boldsymbol{\epsilon}, \quad \boldsymbol{\epsilon} \sim \mathcal{N}(0, \mathbf{I})$$

This enables backpropagation through stochastic sampling.

#### 3.3.5 Bidirectional Uncertainty Propagation

**Neural → Symbolic (Evidential Uncertainty)**:

When making predictions, sample $M$ latent codes $\{\mathbf{z}_m\}_{m=1}^M$ from $q(\mathbf{z}|\mathbf{x},G)$ and compute prediction distribution:

$$p(y | \mathbf{x}, G) \approx \frac{1}{M} \sum_{m=1}^M p(y | \mathbf{z}_m)$$

**Prediction uncertainty** (entropy):

$$H(y | \mathbf{x}, G) = -\sum_c p(y=c | \mathbf{x}, G) \log p(y=c | \mathbf{x}, G)$$

This uncertainty propagates through symbolic reasoning: when traversing knowledge graph paths to explain predictions, uncertainty accumulates along paths via:

$$\text{Path uncertainty} = 1 - \prod_{e \in \text{path}} w_e$$

**Symbolic → Neural (Epistemic Uncertainty)**:

Knowledge graph constraints inform neural uncertainty estimates. If prediction violates high-confidence KG relations (edges with $w_{ij} > 0.8$), increase epistemic uncertainty:

$$\sigma_{\text{epistemic}}^2 = \sigma_{\text{enc}}^2 + \gamma \sum_{(i,j) \in \text{violations}} w_{ij}$$

where $\gamma$ is a hyperparameter controlling symbolic influence on uncertainty.

### 3.4 Phase 3: Hybrid Out-of-Distribution Detection

**Objective**: Develop OOD detection combining neural uncertainty signals with symbolic constraint violations.

#### 3.4.1 Neural OOD Signals

**Signal 1: Prediction Entropy**

$$s_{\text{entropy}} = H(y | \mathbf{x}, G) = -\sum_c p(y=c | \mathbf{x}, G) \log p(y=c | \mathbf{x}, G)$$

High entropy indicates model uncertainty about prediction.

**Signal 2: Mahalanobis Distance**

Compute distance of latent embedding $\mathbf{z}$ from training distribution:

$$s_{\text{Mahal}} = \sqrt{(\mathbf{z} - \boldsymbol{\mu}_{\text{train}})^T \boldsymbol{\Sigma}_{\text{train}}^{-1} (\mathbf{z} - \boldsymbol{\mu}_{\text{train}})}$$

where $\boldsymbol{\mu}_{\text{train}}, \boldsymbol{\Sigma}_{\text{train}}$ are mean and covariance of training set latent embeddings.

**Signal 3: Epistemic Uncertainty**

Variance of predictions across $M$ samples:

$$s_{\text{epistemic}} = \frac{1}{C} \sum_{c=1}^C \text{Var}_m[p(y=c | \mathbf{z}_m)]$$

#### 3.4.2 Symbolic OOD Signals

**Signal 4: Knowledge Graph Constraint Violations**

Count violations of KG relations by prediction:

$$s_{\text{violation}} = \frac{1}{|\mathcal{E}_{\text{sub}}|} \sum_{(i,j) \in \mathcal{E}_{\text{sub}}} w_{ij} \cdot \mathbb{1}[\text{prediction violates } r_{ij}]$$

Example violations:
- Predicted disease contradicts "symptom X → NOT disease Y" relation
- Recommended treatment contradicts "disease Z → contraindicated with drug W"

**Signal 5: Knowledge Graph Coverage**

Measure how well patient symptoms are covered by KG:

$$s_{\text{coverage}} = 1 - \frac{|\text{patient concepts in } G|}{|\text{total patient concepts}|}$$

Low coverage indicates patient has symptoms/conditions not well-represented in medical knowledge graph.

#### 3.4.3 Hybrid OOD Score

Combine neural and symbolic signals via weighted sum:

$$s_{\text{OOD}} = \alpha_1 s_{\text{entropy}} + \alpha_2 s_{\text{Mahal}} + \alpha_3 s_{\text{epistemic}} + \alpha_4 s_{\text{violation}} + \alpha_5 s_{\text{coverage}}$$

**Weight Learning**:
Learn weights $\{\alpha_i\}$ on validation set by maximizing OOD detection AUROC (separating in-distribution MIMIC-III validation set from out-of-distribution eICU samples).

Use logistic regression:

$$\alpha^* = \arg\max_{\alpha} \text{AUROC}(\{s_{\text{OOD}}(\mathbf{x}_{\text{ID}})\}, \{s_{\text{OOD}}(\mathbf{x}_{\text{OOD}})\})$$

### 3.5 Phase 4: Dual Interpretability Generation

**Objective**: Provide explanations combining learned patterns (neural attention) and symbolic reasoning traces for multi-stakeholder trust.

#### 3.5.1 Neural Explanations (Learned Patterns)

**Attention Visualization**:
Extract attention weights $\{\alpha_{ij}\}$ from GAT layers to identify which knowledge graph relations were most important for prediction.

**Feature Importance**:
Compute gradient-based saliency for patient features:

$$\text{Importance}(\mathbf{x}_i) = \left|\frac{\partial \log p(y | \mathbf{x}, G)}{\partial \mathbf{x}_i}\right|$$

Rank features by importance to show which clinical variables (vital signs, lab results) drove prediction.

#### 3.5.2 Symbolic Explanations (Reasoning Traces)

**Knowledge Graph Path Extraction**:
For predicted diagnosis $\hat{y}$, extract top-$K$ paths in $G_{\text{patient}}$ connecting patient symptoms to $\hat{y}$:

1. Perform BFS from patient symptom nodes to predicted disease node
2. Rank paths by cumulative edge weight: $\text{score}(\text{path}) = \prod_{e \in \text{path}} w_e$
3. Select top-$K=5$ highest-scoring paths

**Natural Language Generation**:
Convert paths to natural language explanations:

Example path: `Symptom: Fever → Relation: may_cause → Condition: Infection → Relation: associated_with → Disease: Sepsis`

Generated explanation: *"Predicted sepsis because patient has fever, which may cause infection (evidence strength: 85%), and infection is associated with sepsis (evidence strength: 90%)."*

#### 3.5.3 Multi-Stakeholder Explanation Formatting

**For Clinicians**:
- **Neural**: Attention heatmap over knowledge graph, feature importance bar chart
- **Symbolic**: Top-5 reasoning paths with evidence strength, guideline compliance check

**For Patients**:
- **Simplified symbolic**: "Your symptoms (fever, high heart rate) match patterns of sepsis based on medical knowledge."
- **Risk communication**: "Model is 78% confident (moderate certainty). Doctor will confirm with additional tests."

**For Regulators**:
- **Audit trail**: Complete reasoning trace with UMLS concept IDs, relation types, evidence sources (PubMed IDs)
- **Constraint violations**: List of any guideline violations flagged by symbolic checker

### 3.6 Experimental Design and Evaluation

#### 3.6.1 Dataset Preparation

**MIMIC-III/IV Preprocessing**:
- **Inclusion criteria**: Adult patients (age ≥18), ICU stay ≥24 hours, complete vital signs and lab results
- **Exclusion criteria**: Missing >30% of clinical variables, readmissions (use only first admission)
- **Sample size**: ~40,000 patients after filtering
- **Train/Val/Test split**: 70% / 15% / 15% (stratified by disease prevalence)

**Task Definitions**:
1. **Sepsis prediction**: Binary classification (sepsis vs. no sepsis) using Sepsis-3 criteria, predict within first 24 hours of ICU admission
2. **Acute Kidney Injury (AKI)**: Multi-class classification (no AKI, Stage 1, Stage 2, Stage 3) using KDIGO criteria
3. **In-hospital mortality**: Binary classification (survived vs. died during hospitalization)

**eICU OOD Dataset**:
- Use eICU patients from hospitals NOT represented in MIMIC-III (different geographic regions, patient demographics)
- Same preprocessing and task definitions for distribution shift evaluation

#### 3.6.2 Baseline Models

**Baseline 1: Neural-only + Monte Carlo Dropout**
- Architecture: MLP encoder (patient features) + standard feedforward classifier
- UQ method: MC Dropout (Gal & Ghahramani 2016) with dropout rate 0.2, 50 forward passes
- No knowledge graph integration

**Baseline 2: Hybrid without UQ (Deterministic)**
- Architecture: GNN encoding UMLS subgraph + patient features
- No Bayesian layers, no variational inference
- Deterministic predictions (single forward pass)

**Baseline 3: Deep Ensemble**
- Ensemble of 5 independently trained neural networks (same architecture as Baseline 1)
- UQ from prediction variance across ensemble members

**Baseline 4: Neural-only + Temperature Scaling**
- Same as Baseline 1 but with post-hoc calibration via temperature scaling on validation set

**BK-DL (Proposed)**:
- Full framework with probabilistic KG, GNN + Bayesian layers, variational inference, hybrid OOD detection

#### 3.6.3 Evaluation Metrics

**Prediction Performance**:
- **Macro-averaged F1 score**: Balances performance across disease classes (important for imbalanced datasets)
- **AUROC**: Area under ROC curve for binary/multi-class classification
- **Precision-Recall AUC**: For imbalanced tasks (e.g., sepsis prevalence ~10%)

**Uncertainty Calibration**:
- **Expected Calibration Error (ECE)**: 

$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$$

where $B_m$ are bins of predictions grouped by confidence, $\text{acc}(B_m)$ is accuracy in bin $m$, $\text{conf}(B_m)$ is average confidence.

- **Brier Score**: Mean squared error between predicted probabilities and true labels

$$\text{Brier} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$

- **Reliability Diagrams**: Plot predicted confidence vs. observed accuracy

**OOD Detection**:
- **OOD AUROC**: Area under ROC curve for separating in-distribution (MIMIC-III test) vs. out-of-distribution (eICU) patients
- **OOD Precision-Recall AUC**: Precision-recall curve for OOD detection
- **False Positive Rate at 95% True Positive Rate (FPR95)**: Commonly used OOD detection metric

**Interpretability** (User Study):
- **Explanation Usefulness**: 5-point Likert scale (1=not useful, 5=very useful), clinician-rated
- **Trust Calibration**: Pearson correlation between model confidence and clinician reliance on prediction
- **Decision Accuracy**: Diagnostic accuracy with vs. without AI assistance
- **Time to Diagnosis**: Time from case presentation to final diagnosis

#### 3.6.4 Statistical Testing

**Prediction Performance**:
- **Test**: Paired t-test (BK-DL vs. each baseline, paired by test patient, $n=5$ random seeds)
- **Significance level**: $\alpha=0.0125$ (Bonferroni correction for 4 comparisons)
- **Effect size**: Cohen's $d$ for practical significance

**Calibration**:
- **Test**: Paired t-test on ECE and Brier score
- **Visualization**: Reliability diagrams with 95% confidence intervals

**OOD Detection**:
- **Test**: DeLong test for comparing ROC curves
- **Significance level**: $\alpha=0.05$

**Interpretability**:
- **Test**: Wilcoxon signed-rank test (non-parametric, for Likert scores)
- **Sample size**: $N=20$ physicians provides 80% power to detect medium effect size (Cohen's $d=0.6$) at $\alpha=0.05$

#### 3.6.5 User Study Protocol

**Participants**: $N=20$ board-certified physicians (internal medicine, critical care, emergency medicine)

**Study Design**: Within-subject randomized controlled trial
- Each physician evaluates 10 diagnosis cases (5 with BK-DL explanations, 5 with neural-only explanations)
- Case order and explanation type randomized
- Single-blind (physicians blinded to which system generated explanations)

**Procedure**:
1. **Training phase**: 30-minute tutorial on interpreting dual explanations (neural attention + symbolic traces)
2. **Evaluation phase**: For each case:
   - Present patient clinical data (demographics, vitals, labs, history)
   - Physician makes initial diagnosis without AI assistance (baseline accuracy)
   - Present AI prediction with explanations (BK-DL or neural-only)
   - Physician revises diagnosis if desired
   - Rate explanation usefulness (1-5 Likert scale)
   - Indicate reliance on AI prediction (0-100% scale)
3. **Post-study interview**: Qualitative feedback on explanation types, trust factors, deployment concerns

**Metrics**:
- **Primary**: Explanation usefulness rating, trust calibration (correlation between model confidence and physician reliance)
- **Secondary**: Diagnostic accuracy improvement (with AI vs. without), time to diagnosis

**IRB Approval**: Study protocol approved by institutional review board, informed consent obtained from all participants

#### 3.6.6 Ablation Studies

**Ablation 1: Probabilistic Edge Weight Initialization**
- Compare: (1) Evidence-graded initialization (proposed), (2) Uniform weights (0.5), (3) Learned from scratch
- Metric: Calibration ECE, prediction F1

**Ablation 2: Subgraph Size ($k$-hop neighborhood)**
- Vary $k \in \{1, 2, 3, 4, 5\}$
- Metrics: Prediction F1, inference time, explanation completeness (qualitative clinician review)

**Ablation 3: Hybrid OOD Score Weighting**
- Grid search $\beta \in \{0.1, 0.3, 0.5, 0.7, 0.9\}$ for neural vs. symbolic weight
- Metric: OOD AUROC on MIMIC-III → eICU transfer

**Ablation 4: Constraint Violation Penalty ($\lambda$)**
- Vary $\lambda \in \{0.01, 0.1, 1.0, 10.0\}$ in ELBO objective
- Metrics: Prediction F1, constraint violation rate, calibration ECE

#### 3.6.7 Sensitivity Analysis

**Stratified Evaluation by Patient Subgroups**:
- **Age**: <40, 40-60, >60 years
- **Gender**: Male, female
- **Disease prevalence**: Common (>5%), rare (<1%)
- **KG coverage**: High (>80% symptoms in UMLS), low (<50%)

**Metrics**: Prediction F1, calibration ECE, OOD detection AUROC for each subgroup

**Fairness Analysis**:
- Measure performance disparities across demographic groups
- Compute equalized odds difference, demographic parity difference
- Identify if hybrid approach reduces or exacerbates biases

### 3.7 Implementation Details

**Software Framework**:
- **Deep learning**: PyTorch 2.0
- **Graph neural networks**: PyTorch Geometric 2.3
- **Variational inference**: Pyro 1.8
- **Medical ontologies**: OWL API 5.1, UMLS API

**Hardware**:
- **Training**: Single NVIDIA A100 GPU (40GB VRAM), 128GB RAM
- **Training time**: ~24-48 hours per task (sepsis, AKI, mortality)
- **Inference**: ~2-5 seconds per patient (acceptable for non-real-time clinical decision support)

**Hyperparameters** (tuned on validation set):
- GNN layers: 3
- Hidden dimension: 256
- Learning rate: 1e-4 (Adam optimizer)
- Batch size: 64
- KL divergence weight $\beta$: Annealed from 0 to 1 over 50 epochs
- Constraint penalty $\lambda$: 0.1
- MC samples for inference: $M=50$

**Reproducibility**:
- Code repository: Public GitHub release with Docker container
- Random seeds: Fixed (42, 123, 456, 789, 2024) for 5 experimental runs
- Hyperparameter logs: Weights & Biases public project

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Quantitative Performance Targets

Based on the hypothesis and preliminary evidence from related work, we expect BK-DL to achieve the following quantitative improvements over baselines:

**Prediction Performance** (Hypothesis P4):
- **F1 Score**: Competitive with or exceeding best baseline (within -2% or better)
  - Expected: Neural-only F1 ≈ 0.82, BK-DL F1 ≥ 0.80 (acceptable trade-off for safety/interpretability gains)
  - Stretch goal: BK-DL F1 ≥ 0.84 (knowledge graph provides generalization benefit)
- **AUROC**: ≥0.85 for sepsis prediction, ≥0.80 for AKI, ≥0.88 for mortality

**Uncertainty Calibration** (Hypothesis P1):
- **ECE Reduction**: ≥15% compared to best neural-only baseline
  - Expected: Neural-only ECE ≈ 0.12, BK-DL ECE ≤ 0.102
  - Mechanism: Symbolic constraints reduce overconfident predictions on edge cases
- **Brier Score**: ≥10% improvement (lower is better)

**OOD Detection** (Hypothesis P2):
- **OOD AUROC Improvement**: ≥8% compared to best neural-only OOD method
  - Expected: Neural-only OOD AUROC ≈ 0.75, BK-DL OOD AUROC ≥ 0.81
  - Mechanism: Symbolic violations capture semantic distribution shift missed by statistical methods
- **FPR95**: <20% (low false alarm rate to avoid alert fatigue)

**Interpretability** (Hypothesis P3):
- **Explanation Usefulness**: ≥4.0/5.0 on Likert scale (clinician-rated)
- **Trust Calibration**: Pearson correlation ≥0.75 between model confidence and clinician reliance
- **Diagnostic Accuracy Improvement**: ≥5% increase in physician diagnostic accuracy when using BK-DL vs. no AI assistance

#### 4.1.2 Qualitative Insights

**Failure Mode Identification**:
Through stratified analysis, we expect to identify specific scenarios where BK-DL underperforms baselines:
- **Very rare diseases** (<0.1% prevalence): Limited training data may outweigh knowledge graph benefit
- **Low KG coverage** (<30% symptoms in UMLS): Symbolic constraints provide minimal value
- **High data abundance** (>10,000 training examples): Neural-only models may achieve sufficient performance without knowledge integration

These insights will inform deployment guidelines: recommend BK-DL for moderate-prevalence diseases (1-10%) with good KG coverage, recommend neural-only for very common diseases with abundant data.

**Clinician Feedback**:
User study interviews expected to reveal:
- Which explanation types (attention vs. symbolic traces) clinicians find most useful for different decision contexts
- Trust factors beyond accuracy (e.g., alignment with clinical guidelines, transparency about uncertainty)
- Deployment barriers (computational cost, integration with EHR workflows, liability concerns)

#### 4.1.3 Theoretical Contributions

**Formalization of Bidirectional Uncertainty Propagation**:
The research will produce:
1. **Extended ELBO objective** incorporating knowledge graph constraints as probabilistic priors
2. **Theoretical analysis** of calibration guarantees under mild assumptions (KG correctness, sufficient training data)
3. **Uncertainty decomposition framework** separating data uncertainty (aleatoric), model uncertainty (epistemic), and knowledge uncertainty (probabilistic edge weights)

**Generalization Beyond Healthcare**:
The framework generalizes to other knowledge-intensive domains:
- **Legal reasoning**: Integrate legal knowledge graphs (case law, statutes) with neural models for legal outcome prediction
- **Scientific discovery**: Combine scientific ontologies (gene-disease relations, chemical reactions) with deep learning for hypothesis generation
- **Engineering design**: Integrate design constraints (physics equations, safety standards) with neural optimization

### 4.2 Clinical Impact

#### 4.2.1 Patient Safety Improvements

**Reduced Diagnostic Errors**:
By flagging OOD cases where model is unreliable, BK-DL enables clinicians to:
- Request additional diagnostic tests for ambiguous cases
- Consult specialists for patients with rare disease combinations
- Avoid premature diagnostic closure (anchoring on incorrect AI prediction)

**Estimated impact**: 10-15% reduction in diagnostic errors for flagged OOD cases (requires prospective clinical trial validation)

**Earlier Sepsis Detection**:
Improved calibration and interpretability may enable earlier sepsis treatment:
- Current median time to sepsis diagnosis: 6-12 hours from symptom onset
- Target: Reduce to 4-8 hours via AI-assisted early detection
- **Mortality reduction**: 7.6% per hour of delayed treatment → potential 15-30% relative mortality reduction

#### 4.2.2 Clinician Workflow Integration

**Decision Support, Not Replacement**:
BK-DL designed as assistive tool, not autonomous decision-maker:
- Provides predictions with uncertainty estimates and explanations
- Clinician retains final decision authority
- Reduces cognitive load by pre-filtering differential diagnoses

**EHR Integration**:
- FHIR-compliant API for real-time data ingestion
- Web dashboard displaying predictions, uncertainty, dual explanations
- Alert system for high-risk predictions or OOD cases

**Training Requirements**:
- 30-minute tutorial on interpreting dual explanations
- Ongoing feedback loop: clinician corrections improve model via continual learning

### 4.3 Regulatory and Deployment Pathway

#### 4.3.1 FDA Approval Strategy

**Classification**: Software as Medical Device (SaMD) - Class II (moderate risk)

**Validation Requirements**:
1. **Retrospective validation**: MIMIC-III/IV (completed in this research)
2. **Prospective pilot study**: N=500 patients, single hospital site, 6-month duration
3. **Multi-site validation**: N=2000 patients, 3 hospitals, 12-month duration

**Documentation**:
- **Transparency report**: Training data characteristics, model architecture, validation results, failure modes
- **Audit trail**: Complete reasoning traces for regulatory review
- **Risk mitigation**: OOD detection protocol, clinician override procedures

**Timeline**: 18-24 months from research completion to FDA clearance (Class II 510(k) pathway)

#### 4.3.2 Deployment Considerations

**Computational Cost**:
- **Training**: One-time cost (~$100 GPU-hours per task)
- **Inference**: 2-5 seconds per patient (acceptable for diagnosis, not real-time alarms)
- **Scalability**: Cloud deployment (AWS SageMaker, Azure ML) for multi-hospital rollout

**Liability and Legal**:
- **Clinician responsibility**: Final decision authority remains with physician
- **AI as "second opinion"**: Similar legal framework to radiologist consultation
- **Malpractice insurance**: Requires coverage for AI-assisted decisions (emerging market)

**Equity and Access**:
- **Bias mitigation**: Fairness analysis across demographic groups, retraining on diverse data
- **Underserved populations**: Prioritize deployment in safety-net hospitals with limited specialist access

### 4.4 Broader Scientific Impact

#### 4.4.1 Advancing Hybrid AI Research

**Benchmark Dataset**:
Release annotated MIMIC-III/IV dataset with:
- Probabilistic knowledge graph annotations
- OOD detection labels (in-distribution vs. eICU)
- Clinician-rated explanation quality scores

**Open-Source Framework**:
Public GitHub repository with modular components:
- Probabilistic KG construction pipeline
- GNN + variational inference architecture
- Hybrid OOD detection module
- Dual interpretability generation

**Expected adoption**: 100+ citations within 2 years, 500+ GitHub stars, integration into medical AI courses

#### 4.4.2 Informing AI Policy and Ethics

**Interpretability Standards**:
Dual interpretability approach (learned + symbolic) may inform regulatory standards for medical AI transparency:
- FDA guidance on explainable AI for SaMD
- European Union AI Act requirements for high-risk applications

**Multi-Stakeholder Trust**:
Framework demonstrates how to address diverse interpretability needs:
- **Clinicians**: Causal explanations aligned with medical reasoning
- **Patients**: Understandable risk communication
- **Regulators**: Auditable compliance traces

**Ethical AI Principles**:
- **Transparency**: Dual explanations provide multiple perspectives on predictions
- **Accountability**: Symbolic traces enable auditing of decision-making process
- **Fairness**: Stratified evaluation identifies and mitigates demographic biases

#### 4.4.3 Cross-Domain Applications

**Legal AI**:
Adapt framework for legal outcome prediction:
- Knowledge graph: Case law citations, statutory relations
- Uncertainty: Precedent strength, jurisdictional variations
- Interpretability: Legal reasoning traces for judges/lawyers

**Scientific Discovery**:
Apply to drug discovery and biomedical research:
- Knowledge graph: Gene-disease relations, protein interactions
- Uncertainty: Experimental evidence strength, publication bias
- Interpretability: Hypothesis generation with mechanistic explanations

**Engineering Design**:
Integrate with computer-aided design (CAD) systems:
- Knowledge graph: Physics constraints, safety standards
- Uncertainty: Material property variations, manufacturing tolerances
- Interpretability: Design rationale for engineers/regulators

### 4.5 Limitations and Future Work

#### 4.5.1 Known Limitations

**Computational Cost**:
- Inference time (2-5 seconds) prohibits real-time applications (ICU alarms, emergency triage)
- **Future work**: Model compression, knowledge distillation to reduce latency

**Knowledge Graph Coverage**:
- UMLS may lack comprehensive relations for very rare diseases or emerging conditions (e.g., novel pathogens)
- **Future work**: Automated KG expansion from medical literature, crowdsourced expert annotations

**Generalization to Unstructured Data**:
- Current framework focuses on structured EHR data; extending to medical imaging requires additional vision encoders
- **Future work**: Multimodal integration (clinical data + imaging + clinical notes)

#### 4.5.2 Future Research Directions

**Continual Learning**:
- Adapt model to distribution shift over time (evolving clinical protocols, new treatments)
- Incorporate clinician feedback for online model updates

**Personalized Medicine**:
- Extend framework to patient-specific knowledge graphs (individual genetic profiles, comorbidities)
- Uncertainty quantification for personalized treatment recommendations

**Causal Inference**:
- Integrate causal discovery methods to learn causal relations from observational data
- Combine learned causal graphs with expert-curated knowledge graphs

**Federated Learning**:
- Enable multi-hospital collaboration without sharing patient data
- Aggregate knowledge graphs and model parameters across institutions

### 4.6 Success Criteria Summary

The research will be considered **successful** if:

1. ✅ **Technical validation**: All four primary predictions (P1-P4) met with statistical significance
   - ECE reduction ≥15% (p<0.0125)
   - OOD AUROC improvement ≥8% (p<0.05)
   - Explanation usefulness ≥4.0/5.0 (p<0.05)
   - F1 score within -2% of best baseline (non-inferiority)

2. ✅ **Clinical validation**: Pilot user study demonstrates practical utility
   - ≥70% of clinicians report willingness to use system in practice
   - Diagnostic accuracy improvement ≥5% with AI assistance
   - Trust calibration correlation ≥0.75

3. ✅ **Scientific contribution**: Publications and open-source release
   - ≥2 peer-reviewed publications (top-tier ML/medical informatics venues)
   - Open-source framework with ≥100 GitHub stars within 1 year
   - Benchmark dataset adopted by ≥3 independent research groups

4. ✅ **Regulatory pathway**: Clear path to clinical deployment
   - FDA pre-submission meeting completed
   - Prospective pilot study protocol approved by IRB
   - Industry partnership for multi-site validation (optional but desirable)

**Partial success scenarios**:
- If P1 (calibration) and P4 (accuracy) hold but P2 (OOD) or P3 (interpretability) fail → Framework technically sound but limited practical benefit; revise interpretability methods or OOD detection approach
- If P2 (OOD) and P3 (interpretability) hold but P1 (calibration) fails → Interpretability benefit exists but core uncertainty mechanism needs revision; explore alternative UQ methods (e.g., conformal prediction)

---

**Conclusion**:

This research proposes BK-DL, the first framework integrating medical knowledge graphs, deep learning, and uncertainty quantification through bidirectional uncertainty propagation. By addressing critical gaps in clinical AI safety, interpretability, and trustworthiness, BK-DL has the potential to accelerate adoption of AI-assisted clinical decision support systems. The comprehensive evaluation plan—combining quantitative benchmarks, ablation studies, and clinician user studies—will rigorously validate the hypothesis that hybrid symbolic-neural systems with uncertainty quantification improve clinical decision-making. Success will advance both theoretical understanding of hybrid AI architectures and practical deployment of safe, interpretable medical AI systems.