# Research Proposal: Hierarchical Ontology-Structured Concept Bottleneck Models for Scientifically Interpretable Predictions

## 1. Introduction

### 1.1 Background

The rapid advancement of machine learning (ML) has produced models with remarkable predictive capabilities across diverse scientific domains, from climate modeling to drug discovery. However, these models often function as "black boxes," providing accurate predictions without offering insights into their reasoning processes. This opacity poses significant challenges for scientific applications, where understanding *why* a model makes certain predictions is often as valuable as the predictions themselves. Scientists require not merely accurate forecasts but interpretable explanations that can generate new hypotheses, validate existing theories, and ultimately advance human knowledge.

Explainable Artificial Intelligence (XAI) has emerged as a critical research area addressing this challenge. Among XAI approaches, Concept Bottleneck Models (CBMs) represent a particularly promising paradigm for scientific applications. CBMs introduce an intermediate layer of human-interpretable concepts between input features and final predictions, enabling users to understand model decisions through familiar semantic constructs. Recent advances, particularly Label-Free CBM, have demonstrated that concept bottleneck layers can be constructed without explicit concept annotations by leveraging large vision-language models like CLIP to align learned features with textual concept descriptions.

Despite these advances, existing CBM approaches suffer from a fundamental limitation: they employ flat, general-purpose concept sets that fail to capture the hierarchical structure inherent in scientific knowledge organization. Scientists do not reason with unstructured concept lists; rather, they organize domain knowledge through formal ontologies that encode taxonomic relationships (is-a), compositional relationships (part-of), and other semantic structures. For instance, climate scientists reason about atmospheric phenomena through hierarchical classifications—from broad categories like "precipitation events" to specific types like "convective rainfall" or "orographic precipitation." Similarly, biomedical researchers navigate the Gene Ontology's hierarchical structure when interpreting molecular functions and biological processes.

This structural mismatch between flat concept bottlenecks and hierarchical scientific knowledge organization represents a critical gap limiting CBMs' utility for scientific knowledge discovery. When model explanations do not align with how scientists cognitively structure domain knowledge, the explanations become difficult to interpret, validate, and integrate into existing scientific frameworks.

### 1.2 Research Objectives

This research proposes **Hierarchical Ontology-Structured Concept Bottleneck Models (HOS-CBM)**, a novel architecture that organizes concept bottleneck layers according to domain ontology hierarchies, creating multi-resolution concept representations that mirror scientific reasoning patterns. Our primary objectives are:

1. **Develop a principled method** for integrating formal ontology structures (encoded in OWL format) into concept bottleneck architectures, preserving hierarchical relationships through multi-level concept embeddings.

2. **Design and implement** a training framework that aligns learned features to concepts at multiple hierarchy levels while enforcing ontology consistency constraints.

3. **Empirically validate** that ontology-structured concept organization improves domain expert-assessed interpretability compared to flat concept baselines while maintaining competitive prediction accuracy.

4. **Demonstrate applicability** to climate science applications using the ERA5 dataset and ENVO (Environment Ontology), establishing a template for other scientific domains.

### 1.3 Research Significance

This research addresses the XAI4Science workshop's core mission of using model understanding to discover new scientific knowledge. By aligning model architectures with established scientific knowledge structures, HOS-CBM offers several significant contributions:

**Theoretical Significance:** HOS-CBM provides a principled framework for incorporating structured domain knowledge into neural network architectures, bridging the gap between symbolic knowledge representation (ontologies) and sub-symbolic learning (deep neural networks).

**Practical Significance:** For climate scientists, healthcare researchers, and materials scientists, HOS-CBM offers explanations structured according to familiar ontological frameworks, facilitating hypothesis generation and validation.

**Methodological Significance:** The proposed evaluation framework, combining automated consistency metrics with expert interpretability assessments, establishes rigorous standards for evaluating scientifically meaningful XAI.

---

## 2. Methodology

### 2.1 Overview

HOS-CBM consists of three main components: (1) ontology parsing and hierarchical embedding generation, (2) multi-resolution concept bottleneck architecture, and (3) ontology-constrained training. We detail each component below.

### 2.2 Ontology Parsing and Hierarchical Embedding Generation

**Step 1: Ontology Structure Extraction**

Given a domain ontology $\mathcal{O}$ in OWL format, we extract the hierarchical concept structure. Let $\mathcal{C} = \{c_1, c_2, ..., c_N\}$ denote the set of concepts, and let $\mathcal{R} \subseteq \mathcal{C} \times \mathcal{C}$ denote the set of hierarchical relations (is-a, part-of). We organize concepts into $L$ hierarchy levels:

$$\mathcal{C} = \mathcal{C}^{(1)} \cup \mathcal{C}^{(2)} \cup ... \cup \mathcal{C}^{(L)}$$

where $\mathcal{C}^{(1)}$ contains the most general (root-level) concepts and $\mathcal{C}^{(L)}$ contains the most specific (leaf-level) concepts. For the ENVO ontology, we target $L \in \{3, 4, 5\}$ levels with approximately 100-1000 total concepts.

**Step 2: Concept Embedding Generation**

We employ OWL2Vec+ to generate concept embeddings that preserve ontological structure. For each concept $c_i$, OWL2Vec+ produces an embedding $\mathbf{e}_i \in \mathbb{R}^d$ by:

1. Extracting structural walks through the ontology graph
2. Incorporating lexical information from concept labels and definitions
3. Training a Word2Vec-style model on the combined corpus

The resulting embeddings satisfy the property that semantically related concepts (according to ontology structure) have higher cosine similarity:

$$\text{sim}(\mathbf{e}_i, \mathbf{e}_j) > \text{sim}(\mathbf{e}_i, \mathbf{e}_k) \quad \text{if } (c_i, c_j) \in \mathcal{R} \text{ and } (c_i, c_k) \notin \mathcal{R}$$

**Step 3: Hierarchical Embedding Organization**

We organize concept embeddings into level-specific embedding matrices:

$$\mathbf{E}^{(\ell)} = [\mathbf{e}_1^{(\ell)}, \mathbf{e}_2^{(\ell)}, ..., \mathbf{e}_{n_\ell}^{(\ell)}]^\top \in \mathbb{R}^{n_\ell \times d}$$

where $n_\ell = |\mathcal{C}^{(\ell)}|$ is the number of concepts at level $\ell$.

### 2.3 Multi-Resolution Concept Bottleneck Architecture

**Feature Extraction**

Given an input $\mathbf{x}$ (e.g., climate data grid), a backbone network $f_\theta$ (ResNet-50) extracts features:

$$\mathbf{h} = f_\theta(\mathbf{x}) \in \mathbb{R}^{d_h}$$

**Hierarchical Concept Projection**

For each hierarchy level $\ell \in \{1, ..., L\}$, we project features to concept space using level-specific projection heads:

$$\mathbf{z}^{(\ell)} = g_\phi^{(\ell)}(\mathbf{h}) \in \mathbb{R}^d$$

where $g_\phi^{(\ell)}$ is a two-layer MLP with ReLU activation.

**Concept Activation Computation**

Concept activations at each level are computed via cosine similarity with concept embeddings:

$$a_i^{(\ell)} = \sigma\left(\tau \cdot \frac{\mathbf{z}^{(\ell)} \cdot \mathbf{e}_i^{(\ell)}}{\|\mathbf{z}^{(\ell)}\| \|\mathbf{e}_i^{(\ell)}\|}\right)$$

where $\sigma$ is the sigmoid function and $\tau$ is a learnable temperature parameter. The full concept activation vector at level $\ell$ is:

$$\mathbf{a}^{(\ell)} = [a_1^{(\ell)}, a_2^{(\ell)}, ..., a_{n_\ell}^{(\ell)}]^\top \in \mathbb{R}^{n_\ell}$$

**Multi-Resolution Bottleneck**

The complete bottleneck representation concatenates activations across all levels:

$$\mathbf{a} = [\mathbf{a}^{(1)}; \mathbf{a}^{(2)}; ...; \mathbf{a}^{(L)}] \in \mathbb{R}^{\sum_\ell n_\ell}$$

**Prediction Head**

A linear classifier produces final predictions:

$$\hat{y} = \text{softmax}(\mathbf{W}_y \mathbf{a} + \mathbf{b}_y)$$

### 2.4 Ontology-Constrained Training

**Loss Function**

The total training loss combines four components:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pred}} + \lambda_1 \mathcal{L}_{\text{align}} + \lambda_2 \mathcal{L}_{\text{consist}} + \lambda_3 \mathcal{L}_{\text{sparse}}$$

**Prediction Loss:** Standard cross-entropy for classification:

$$\mathcal{L}_{\text{pred}} = -\sum_{k} y_k \log \hat{y}_k$$

**Hierarchical Alignment Loss:** Contrastive loss ensuring features align with appropriate concept embeddings at each level:

$$\mathcal{L}_{\text{align}} = \sum_{\ell=1}^{L} \mathcal{L}_{\text{InfoNCE}}^{(\ell)}(\mathbf{z}^{(\ell)}, \mathbf{E}^{(\ell)})$$

where InfoNCE encourages high similarity between projected features and relevant concept embeddings while pushing apart irrelevant concepts.

**Ontology Consistency Loss:** Enforces the constraint that parent concept activations must be at least as high as their children:

$$\mathcal{L}_{\text{consist}} = \sum_{(c_p, c_c) \in \mathcal{R}} \max(0, a_c - a_p + \epsilon)$$

where $c_p$ is a parent concept, $c_c$ is a child concept, and $\epsilon$ is a small margin. This ensures taxonomic coherence: if "convective precipitation" is active, "precipitation" must also be active.

**Sparsity Loss:** Encourages interpretable sparse activations:

$$\mathcal{L}_{\text{sparse}} = \sum_{\ell} \|\mathbf{a}^{(\ell)}\|_1$$

### 2.5 Data Collection and Experimental Setup

**Primary Dataset: ERA5 Climate Data**

- **Source:** ECMWF ERA5 reanalysis dataset
- **Variables:** Temperature, precipitation, wind, pressure at multiple levels
- **Spatial resolution:** 0.25° × 0.25° grid
- **Temporal coverage:** 2010-2020 for training, 2021 for testing
- **Task:** Climate event classification (e.g., extreme weather event types)

**Ontology: ENVO (Environment Ontology)**

- **Source:** OBO Foundry
- **Relevant branches:** Atmospheric phenomena, precipitation types, climate zones
- **Hierarchy depth:** 4-5 levels
- **Concept count:** ~500 relevant concepts after filtering

**Baselines:**

1. **Label-Free CBM:** Flat concept bottleneck using CLIP-derived concepts
2. **Flat-CBM:** Ontology concepts without hierarchical structure
3. **Standard ResNet-50:** Black-box baseline without concept bottleneck

**Implementation Details:**

- Backbone: ResNet-50 pretrained on ImageNet
- Optimizer: AdamW with learning rate $10^{-4}$
- Batch size: 64
- Training epochs: 100 with early stopping
- Hardware: 2× NVIDIA A100 GPUs
- Random seeds: 5 runs per configuration

### 2.6 Evaluation Metrics

**Prediction Performance:**
- Classification accuracy
- Macro F1-score
- Area under ROC curve (AUC)

**Interpretability Metrics:**

*Automated Metrics:*
- **Ontology Consistency Score (OCS):** Percentage of samples where parent ≥ max(child) constraint holds:

$$\text{OCS} = \frac{1}{|\mathcal{D}|} \sum_{\mathbf{x} \in \mathcal{D}} \mathbb{1}\left[\forall (c_p, c_c) \in \mathcal{R}: a_p(\mathbf{x}) \geq a_c(\mathbf{x})\right]$$

- **Concept Activation Sparsity:** Average L0 norm of concept activations

*Expert Evaluation:*
- **Protocol:** 3-5 climate science domain experts rate explanations
- **Scale:** 5-point Likert scale assessing:
  - Concept relevance to prediction
  - Alignment with domain knowledge
  - Usefulness for scientific reasoning
- **Sample size:** 30 evaluations per condition (power analysis: Cohen's d = 0.6, power = 0.8, α = 0.05)

**Statistical Analysis:**
- Independent samples t-test comparing HOS-CBM vs. baselines
- Report: Mean difference, 95% confidence intervals, Cohen's d effect size, p-values
- Significance threshold: p < 0.05

### 2.7 Falsification Criteria

The hypothesis will be **rejected** if any of the following occur:

1. **Primary Failure:** Expert interpretability rating for HOS-CBM ≤ Label-Free CBM baseline (p > 0.05)
2. **Mechanism Failure:** Ontology Consistency Score < 70%
3. **Accuracy Collapse:** HOS-CBM accuracy drops > 10% below Label-Free CBM baseline

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1 - Interpretability Improvement):**
We expect HOS-CBM to achieve significantly higher expert interpretability ratings than Label-Free CBM, with a target mean rating ≥ 3.5/5.0 and effect size Cohen's d > 0.5. This improvement stems from the alignment between hierarchical concept organization and scientists' cognitive structures for domain knowledge.

**Secondary Outcomes:**

*P2 - Ontology Consistency:* We anticipate concept activations will respect taxonomic constraints in ≥ 90% of test samples, demonstrating that the ontology consistency loss successfully enforces hierarchical coherence.

*P3 - Multi-Resolution Utility:* Coarse-level concepts (L1) will provide high-level categorizations useful for initial understanding, while fine-level concepts (L3+) will offer specific details enabling deeper scientific analysis. This multi-resolution structure will enable scientists to "zoom in" on explanations as needed.

*P4 - Competitive Accuracy:* HOS-CBM will maintain prediction accuracy within 5% of black-box baselines and within 10% of Label-Free CBM, demonstrating that interpretability gains do not require substantial accuracy sacrifices.

### 3.2 Scientific Impact

**Advancing XAI Theory:**
HOS-CBM establishes ontology-guided architecture as a principled approach for scientifically meaningful XAI. By demonstrating that structured domain knowledge can be effectively integrated into neural network architectures, this work bridges symbolic AI (knowledge representation) and connectionist AI (deep learning), contributing to the broader neuro-symbolic AI research agenda.

**Enabling Scientific Discovery:**
For climate scientists, HOS-CBM offers explanations structured according to the ENVO ontology, facilitating:
- Hypothesis generation about relationships between atmospheric phenomena
- Validation of existing climate classification schemes
- Identification of novel patterns that may warrant new ontology concepts

**Template for Other Domains:**
The methodology generalizes to any domain with formal ontologies:
- **Healthcare:** Gene Ontology, Disease Ontology, Human Phenotype Ontology
- **Materials Science:** ChEBI (chemical entities), Materials Ontology
- **Biology:** Cell Ontology, Protein Ontology

### 3.3 Broader Impact

**Responsible AI Deployment:**
By providing scientifically meaningful explanations, HOS-CBM supports responsible deployment of ML models in high-stakes scientific applications. Scientists can validate model reasoning against established domain knowledge, identifying potential failure modes before deployment.

**Democratizing Scientific AI:**
Ontology-structured explanations lower the barrier for domain experts (who may not be ML specialists) to engage with and critique model predictions, fostering productive human-AI collaboration in scientific research.

**Limitations and Future Work:**
We acknowledge that HOS-CBM requires domains with established formal ontologies, limiting immediate applicability to emerging fields. Future work will explore methods for semi-automatic ontology construction from scientific literature and extension to domains with less formalized knowledge structures.

---

## 4. Conclusion

This proposal presents HOS-CBM, a novel approach to interpretable machine learning that aligns concept bottleneck architectures with hierarchical scientific ontologies. By organizing concept representations according to established domain knowledge structures, HOS-CBM promises to deliver explanations that are not merely human-understandable but scientifically meaningful—structured in ways that mirror expert reasoning and facilitate knowledge discovery. Through rigorous empirical evaluation combining automated metrics and expert assessments, we will establish whether ontology-guided architecture represents a principled path toward XAI systems that genuinely advance scientific understanding.