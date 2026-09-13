# Research Proposal: Clinical Concept Graphs for Interpretable Disease Progression Modeling

## 1. Introduction

### Background

The integration of machine learning (ML) into healthcare has accelerated dramatically over the past decade, with applications ranging from diagnostic imaging to risk prediction and treatment optimization. Despite remarkable advances in predictive accuracy, the predominant use of black-box models—such as deep neural networks and ensemble methods—has created a significant barrier to clinical adoption. Physicians are often reluctant to trust predictions they cannot understand, particularly when patient safety is at stake. This interpretability gap represents one of the most pressing challenges in medical artificial intelligence.

Current approaches to model interpretability in healthcare largely rely on post-hoc explanation methods such as SHAP values, LIME, or attention visualization. While these techniques provide some insight into model behavior, they often fail to align with clinical reasoning processes. Physicians do not reason about individual feature contributions in isolation; rather, they synthesize information through interconnected clinical concepts, recognizing temporal patterns and leveraging established medical knowledge to form diagnostic and prognostic assessments. For instance, a clinician evaluating cardiovascular risk naturally considers how elevated creatinine levels suggest kidney dysfunction, which in turn increases cardiovascular risk through well-established pathophysiological mechanisms.

Disease progression modeling presents particular challenges for interpretability. Predicting how a patient's condition will evolve over time requires understanding complex temporal dynamics, recognizing patterns across multiple clinical variables, and integrating domain knowledge about disease mechanisms. Existing approaches, such as recurrent neural networks or transformer-based models, can achieve strong predictive performance but provide limited insight into the reasoning behind their predictions.

### Research Objectives

This research proposes to develop **Clinical Concept Graphs (CCG)**, a novel framework for interpretable disease progression modeling that explicitly represents and reasons over clinically meaningful concepts and their relationships. Our specific objectives are:

1. To design a systematic methodology for constructing patient-specific dynamic clinical concept graphs from electronic health record (EHR) data, incorporating both data-driven patterns and established medical knowledge from ontologies and knowledge bases.

2. To develop an attention-based graph neural network architecture that performs reasoning over clinical concept graphs while producing interpretable reasoning chains aligned with clinical thinking.

3. To implement built-in uncertainty quantification mechanisms that reflect confidence in both graph structure and predictions.

4. To validate the framework on real-world disease progression tasks, evaluating both predictive performance and interpretability through clinician assessments.

### Significance

This research addresses a critical need in healthcare AI by providing predictions accompanied by transparent reasoning paths expressed in clinical terminology. Unlike post-hoc explanations that approximate model behavior, our approach ensures that interpretability is inherent to the model's reasoning process. The expected benefits include enhanced physician trust, identification of novel clinical insights, early detection of opportunities for intervention, and ultimately, improved patient outcomes through more informed clinical decision-making.

## 2. Methodology

### 2.1 Overview

Our framework consists of four integrated components: (1) Clinical Concept Extraction and Mapping, (2) Dynamic Graph Construction, (3) Graph Reasoning Network, and (4) Interpretation Generation. We describe each component in detail below.

### 2.2 Clinical Concept Extraction and Mapping

**Data Sources:** We utilize longitudinal EHR data including diagnoses, laboratory values, medications, vital signs, procedures, and clinical notes. Let $\mathcal{D} = \{D_1, D_2, \ldots, D_N\}$ represent the dataset of $N$ patients, where each patient $D_i$ contains time-stamped clinical events $\{(e_{i,1}, t_{i,1}), (e_{i,2}, t_{i,2}), \ldots\}$.

**Concept Extraction:** We employ a multi-modal extraction pipeline:
- Structured data (diagnoses, labs, medications) are directly mapped to standardized concepts
- Unstructured clinical notes are processed using named entity recognition (NER) models fine-tuned on medical corpora (e.g., MedCAT, cTAKES)

**Ontology Mapping:** Extracted concepts are mapped to standardized medical ontologies:
- Diagnoses → ICD-10 and SNOMED-CT
- Medications → RxNorm
- Laboratory values → LOINC

Let $\mathcal{C} = \{c_1, c_2, \ldots, c_M\}$ denote the set of $M$ unique clinical concepts in our vocabulary, with each concept $c_j$ associated with its ontology identifiers and semantic type (symptom, diagnosis, medication, lab value, etc.).

### 2.3 Dynamic Graph Construction

For each patient $i$ at time point $t$, we construct a temporal clinical concept graph $G_i^t = (V_i^t, E_i^t, X_i^t, R_i^t)$.

**Node Construction:** The node set $V_i^t$ contains clinical concepts active within a specified time window $[t-\tau, t]$. Each node $v_j \in V_i^t$ represents a clinical concept with feature vector:

$$x_j = [e_j^{ont} \| e_j^{val} \| e_j^{temp}]$$

where $e_j^{ont}$ is the ontology embedding from pre-trained medical concept embeddings, $e_j^{val}$ encodes the concept's value (e.g., normalized lab value, medication dosage), and $e_j^{temp}$ represents temporal features (recency, frequency, trend).

**Edge Construction:** We construct edges from three sources:

1. *Knowledge-Based Edges:* Extracted from medical knowledge bases including:
   - UMLS Metathesaurus relationships
   - DrugBank for drug-disease and drug-drug interactions
   - Clinical practice guidelines

2. *Data-Driven Edges:* Learned from co-occurrence patterns and temporal associations in the training data using mutual information:

$$MI(c_j, c_k) = \sum_{c_j, c_k} p(c_j, c_k) \log \frac{p(c_j, c_k)}{p(c_j)p(c_k)}$$

3. *Temporal Edges:* Connect concepts across time steps to capture disease evolution patterns.

Each edge $e_{jk} \in E_i^t$ is associated with a relation type $r_{jk} \in \mathcal{R}$ (e.g., "causes," "treats," "indicates," "precedes") and confidence score $\omega_{jk}$.

### 2.4 Graph Reasoning Network Architecture

We propose a **Clinical Concept Reasoning Network (CCRN)** that performs multi-hop reasoning over the clinical concept graph.

**Input Encoding:** Node features are first projected into a shared embedding space:

$$h_j^{(0)} = W_{type(j)} x_j + b_{type(j)}$$

where $W_{type(j)}$ and $b_{type(j)}$ are type-specific parameters.

**Relational Graph Attention Layers:** We employ $L$ layers of relational graph attention to propagate information:

$$h_j^{(l+1)} = \sigma\left(\sum_{k \in \mathcal{N}(j)} \sum_{r \in \mathcal{R}_{jk}} \alpha_{jk}^{(l,r)} W_r^{(l)} h_k^{(l)}\right)$$

where $\mathcal{N}(j)$ denotes neighbors of node $j$, and attention coefficients are computed as:

$$\alpha_{jk}^{(l,r)} = \frac{\exp\left(a_r^T [W_q h_j^{(l)} \| W_k h_k^{(l)} \| e_r]\right)}{\sum_{k' \in \mathcal{N}(j)} \sum_{r' \in \mathcal{R}_{jk'}} \exp\left(a_{r'}^T [W_q h_j^{(l)} \| W_k h_{k'}^{(l)} \| e_{r'}]\right)}$$

**Reasoning Path Extraction:** We implement a differentiable path extraction mechanism that identifies important reasoning chains. For each prediction, we compute path importance scores:

$$s(p) = \prod_{(j,r,k) \in p} \alpha_{jk}^{r} \cdot \omega_{jk}$$

where $p$ represents a path through the graph, and top-$K$ paths are retained as explanations.

**Prediction Head:** The final graph representation is obtained through hierarchical pooling:

$$h_G = \text{ReadOut}\left(\{h_j^{(L)} | v_j \in V\}\right)$$

Disease progression predictions are made using:

$$\hat{y} = \text{MLP}(h_G)$$

### 2.5 Uncertainty Quantification

We incorporate uncertainty quantification at two levels:

**Structural Uncertainty:** Reflects confidence in graph construction:

$$u_{struct} = 1 - \frac{1}{|E|}\sum_{e_{jk} \in E} \omega_{jk}$$

**Predictive Uncertainty:** Implemented via Monte Carlo Dropout:

$$u_{pred} = \text{Var}\left[\hat{y}^{(s)}\right]_{s=1}^{S}$$

where $S$ forward passes with dropout provide predictive variance.

### 2.6 Training Procedure

**Loss Function:** We optimize a multi-task objective:

$$\mathcal{L} = \mathcal{L}_{pred} + \lambda_1 \mathcal{L}_{path} + \lambda_2 \mathcal{L}_{reg}$$

where $\mathcal{L}_{pred}$ is the prediction loss (cross-entropy for classification, MSE for regression), $\mathcal{L}_{path}$ encourages path diversity and knowledge alignment, and $\mathcal{L}_{reg}$ provides regularization.

**Knowledge Alignment Loss:** We encourage discovered reasoning paths to align with established medical knowledge:

$$\mathcal{L}_{path} = -\sum_{p \in \mathcal{P}_{known}} \log P(p | G)$$

### 2.7 Experimental Design

**Datasets:** We will evaluate on:
1. MIMIC-IV: ICU patient data for mortality and readmission prediction
2. eICU Collaborative Research Database: Multi-center ICU data for external validation
3. UK Biobank: Large-scale cohort for chronic disease progression (diabetes, cardiovascular disease)

**Baselines:** We compare against:
- Traditional ML: XGBoost, Random Forest with feature importance
- Deep learning: LSTM, Transformer-based models
- Existing GNN approaches: GRAM, GAMENet, MOTGNN
- Post-hoc explanation methods: SHAP, attention-based explanations

**Evaluation Metrics:**

*Predictive Performance:*
- AUROC and AUPRC for classification tasks
- Mean Absolute Error for time-to-event prediction
- Calibration metrics (Expected Calibration Error)

*Interpretability Evaluation:*
- Clinician assessment surveys (5-point Likert scale for clarity, clinical relevance, actionability)
- Path validity rate: percentage of reasoning paths confirmed by medical literature
- Faithfulness metrics: correlation between path importance and prediction sensitivity

*Robustness:*
- Performance on out-of-distribution samples
- Stability of explanations across similar patients

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Technical Contributions:**
   - A novel graph construction methodology that systematically integrates EHR data with medical ontologies
   - An interpretable GNN architecture producing clinically meaningful reasoning chains
   - A comprehensive uncertainty quantification framework for healthcare predictions

2. **Empirical Results:**
   - Competitive predictive performance with state-of-the-art black-box models (target: within 2% AUROC)
   - Significantly improved interpretability scores in clinician evaluations (target: >80% of explanations rated as clinically meaningful)
   - High path validity rates (target: >70% alignment with established medical knowledge)

3. **Clinical Insights:**
   - Discovery of novel clinical concept associations that may inform future research
   - Identification of patient subgroups with distinct progression patterns

### Impact

**Clinical Practice:** By providing transparent reasoning chains, our framework enables physicians to understand and verify ML predictions, facilitating clinical adoption. Interpretable predictions can guide early interventions and personalized treatment strategies.

**Healthcare AI Research:** This work advances the field by demonstrating that interpretability need not come at the cost of predictive accuracy. The framework provides a template for developing inherently interpretable models in other healthcare domains.

**Patient Outcomes:** Ultimately, trustworthy and actionable ML predictions can improve patient care by enabling timely interventions based on understood risk factors, potentially reducing adverse outcomes and healthcare costs.

**Broader Implications:** The principles developed here—embedding domain knowledge, reasoning in domain-appropriate terms, and providing structured explanations—can extend beyond healthcare to other high-stakes AI applications requiring interpretability and trust.