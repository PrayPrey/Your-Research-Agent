# Research Proposal

## Title
Domain-Guided Concept Bottleneck Layers for Interpretable Foundation Model Fine-Tuning

---

## 1. Introduction

### Background

The rapid advancement of foundation models—large-scale neural networks pre-trained on massive datasets—has revolutionized machine learning across diverse domains including natural language processing, computer vision, and healthcare. Models such as GPT-4, CLIP, and domain-specific variants demonstrate unprecedented capabilities in understanding and generating complex patterns. However, these models operate as "black boxes," making decisions through billions of parameters that defy human comprehension. This opacity poses significant challenges in high-stakes applications where understanding the reasoning behind predictions is not merely desirable but essential for safety, accountability, and regulatory compliance.

The field of interpretable machine learning has historically bifurcated into two distinct paradigms. Classical interpretability methods, designed for tabular and small-scale data, employ inherently transparent models such as decision trees, sparse linear models, and rule-based systems. These approaches guarantee faithful explanations by design but struggle to capture the complex, non-linear relationships present in high-dimensional data like medical images or clinical text. Modern interpretability methods for deep learning, including post-hoc approaches like SHAP, LIME, and attention visualization, provide insights into model behavior but cannot guarantee faithful or complete explanations—they approximate what the model might be doing rather than revealing its true computational process.

Concept Bottleneck Models (CBMs), introduced by Koh et al., represent a promising middle ground by forcing neural networks to first predict human-interpretable concepts before making final predictions. Recent advances have extended CBMs to handle spatial locality (SL-CBM), automatic concept discovery without predefined vocabularies, and text classification (TBM). However, significant gaps remain: existing methods either require extensive manual concept annotation, lack systematic incorporation of domain expertise, or fail to scale to foundation model architectures.

### Research Objectives

This research proposes **Domain-Guided Concept Bottleneck Layers (DG-CBL)**, a novel framework that bridges the gap between foundation model capabilities and inherent interpretability. Our specific objectives are:

1. **Develop automated concept vocabulary extraction** from domain-specific scientific literature and expert ontologies using large language models, eliminating the need for manual concept curation.

2. **Design trainable concept bottleneck layers** that can be inserted into frozen foundation models during fine-tuning, enabling interpretable adaptation without sacrificing pre-trained knowledge.

3. **Create a joint optimization framework** that balances concept prediction accuracy, task performance, and concept sparsity to ensure both interpretability and competitive performance.

4. **Establish rigorous evaluation protocols** for assessing concept faithfulness, intervention effectiveness, and domain expert alignment.

### Significance

This research addresses critical needs identified by the interpretable AI community. First, it provides a systematic approach to incorporating domain knowledge—previously siloed in scientific literature and expert ontologies—directly into model architecture. Second, it offers truthful explanations by design rather than post-hoc approximations, addressing concerns about explanation faithfulness. Third, it enables concept-level interventions that allow domain experts to debug, verify, and correct model behavior at a semantically meaningful level. The framework is particularly significant for healthcare, where regulatory requirements increasingly demand explainable AI systems and where domain expertise is abundant but underutilized in model design.

---

## 2. Methodology

### 2.1 Overview

The DG-CBL framework consists of three main components: (1) automated domain-guided concept extraction, (2) concept bottleneck layer architecture, and (3) joint optimization with interpretability constraints. Figure 1 illustrates the overall architecture.

### 2.2 Domain-Guided Concept Extraction

#### 2.2.1 Literature Mining with LLMs

We employ large language models to automatically extract domain-relevant concept vocabularies from scientific literature. Given a target domain $\mathcal{D}$ (e.g., dermatology, radiology), we collect a corpus of relevant publications $\mathcal{C} = \{d_1, d_2, ..., d_N\}$ from sources such as PubMed, arXiv, and domain-specific databases.

For each document $d_i$, we prompt an LLM to extract concepts using structured prompts:

$$P_{extract}(d_i) = \text{LLM}(\text{"Extract medical concepts relevant to [DOMAIN] from: "} + d_i)$$

The extracted concepts are aggregated and filtered based on frequency and relevance scores:

$$\mathcal{V}_{raw} = \bigcup_{i=1}^{N} P_{extract}(d_i)$$

#### 2.2.2 Ontology Integration

We integrate extracted concepts with existing domain ontologies (e.g., SNOMED-CT for healthcare, Gene Ontology for biology) to ensure semantic validity and hierarchical structure. Let $\mathcal{O}$ denote the ontology graph where nodes represent concepts and edges represent relationships. We align extracted concepts using semantic similarity:

$$\text{align}(c, \mathcal{O}) = \arg\max_{o \in \mathcal{O}} \text{sim}(\text{embed}(c), \text{embed}(o))$$

where $\text{embed}(\cdot)$ produces semantic embeddings using a domain-adapted language model.

#### 2.2.3 Concept Hierarchy Construction

We construct a hierarchical concept vocabulary $\mathcal{V} = \{c_1, c_2, ..., c_K\}$ organized into levels of abstraction:

$$\mathcal{V} = \mathcal{V}_{base} \cup \mathcal{V}_{intermediate} \cup \mathcal{V}_{abstract}$$

where $\mathcal{V}_{base}$ contains fine-grained concepts (e.g., "irregular border"), $\mathcal{V}_{intermediate}$ contains mid-level concepts (e.g., "asymmetric lesion"), and $\mathcal{V}_{abstract}$ contains high-level concepts (e.g., "malignancy indicators").

### 2.3 Concept Bottleneck Layer Architecture

#### 2.3.1 Foundation Model Integration

Let $f_\theta$ denote a pre-trained foundation model with $L$ layers: $f_\theta = f^{(L)} \circ f^{(L-1)} \circ ... \circ f^{(1)}$. We insert concept bottleneck layers at strategic positions $\mathcal{L}_{insert} \subset \{1, 2, ..., L\}$, typically at the transition between the encoder and task-specific heads.

For an input $x$, the intermediate representation at layer $l \in \mathcal{L}_{insert}$ is:

$$h^{(l)} = f^{(l)} \circ ... \circ f^{(1)}(x) \in \mathbb{R}^{d_l}$$

#### 2.3.2 Concept Prediction Module

The concept bottleneck layer maps intermediate representations to concept predictions. We employ a multi-head attention mechanism to capture concept-representation alignment:

$$Q = h^{(l)} W_Q, \quad K = E_c W_K, \quad V = E_c W_V$$

where $E_c \in \mathbb{R}^{K \times d_c}$ contains learnable concept embeddings initialized from text embeddings of concept descriptions.

The attention-based concept scores are computed as:

$$A = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)$$

$$\hat{c} = \sigma(W_{proj}(AV) + b_{proj})$$

where $\hat{c} \in [0, 1]^K$ represents predicted concept activations and $\sigma$ is the sigmoid function.

#### 2.3.3 Concept-to-Prediction Module

The final prediction is made through an interpretable linear layer operating on concept activations:

$$\hat{y} = \text{softmax}(W_y \hat{c} + b_y)$$

where $W_y \in \mathbb{R}^{|\mathcal{Y}| \times K}$ provides direct interpretability—each element $W_y^{(i,j)}$ represents the contribution of concept $c_j$ to class $i$.

### 2.4 Joint Optimization Framework

#### 2.4.1 Loss Function

We jointly optimize three objectives:

**Task Loss**: Standard cross-entropy for the downstream task:
$$\mathcal{L}_{task} = -\sum_{i} y_i \log(\hat{y}_i)$$

**Concept Loss**: Binary cross-entropy for concept prediction (when concept labels are available) or concept consistency loss using pseudo-labels:
$$\mathcal{L}_{concept} = -\sum_{k=1}^{K} \left[ c_k \log(\hat{c}_k) + (1-c_k) \log(1-\hat{c}_k) \right]$$

**Sparsity Loss**: Encouraging sparse concept activations for interpretability:
$$\mathcal{L}_{sparse} = \lambda_1 \|\hat{c}\|_1 + \lambda_2 \|W_y\|_1$$

The total loss is:
$$\mathcal{L}_{total} = \mathcal{L}_{task} + \alpha \mathcal{L}_{concept} + \beta \mathcal{L}_{sparse}$$

where $\alpha$ and $\beta$ are hyperparameters controlling the trade-off.

#### 2.4.2 Training Procedure

1. **Phase 1 - Concept Alignment**: Train concept prediction module with foundation model frozen using $\mathcal{L}_{concept}$.
2. **Phase 2 - Joint Fine-tuning**: Jointly optimize all losses with selective unfreezing of foundation model parameters.
3. **Phase 3 - Sparsification**: Gradually increase sparsity regularization to prune irrelevant concept connections.

### 2.5 Experimental Design

#### 2.5.1 Datasets

We evaluate on three domains:

1. **Healthcare**: MIMIC-CXR (chest X-ray classification), ISIC 2019 (skin lesion diagnosis), and CheXpert (multi-label chest conditions).

2. **Natural Images**: CUB-200-2011 (bird species with attribute annotations) and AwA2 (animals with attributes).

3. **Text Classification**: Medical question answering (PubMedQA) and clinical note classification.

#### 2.5.2 Baselines

- Standard fine-tuning without interpretability constraints
- Post-hoc explanation methods (LIME, SHAP, GradCAM)
- Existing CBM variants (original CBM, Label-free CBM, TBM)
- Prototype-based interpretable models

#### 2.5.3 Evaluation Metrics

**Performance Metrics**:
- Classification accuracy, AUC-ROC, F1-score

**Interpretability Metrics**:
- Concept accuracy: alignment between predicted and ground-truth concepts
- Concept faithfulness: correlation between concept perturbation and prediction change
- Sparsity: average number of active concepts per prediction

**Human Evaluation**:
- Expert agreement: domain experts rate explanation quality on a 5-point Likert scale
- Intervention effectiveness: accuracy improvement after expert concept correction
- Simulatability: human ability to predict model behavior given explanations

#### 2.5.4 Ablation Studies

We conduct ablations on:
- Concept extraction source (literature only vs. ontology-augmented)
- Bottleneck layer insertion positions
- Sparsity regularization strength
- Number of concepts in vocabulary

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Technical Contributions**: We expect DG-CBL to achieve within 2-3% of state-of-the-art task performance while providing fully interpretable concept-based explanations. The automated concept extraction pipeline should reduce manual annotation effort by over 90% compared to traditional CBMs.

2. **Interpretability Quality**: We anticipate concept faithfulness scores exceeding 0.85 (measured by intervention consistency), significantly outperforming post-hoc methods which typically achieve 0.6-0.7 on similar metrics.

3. **Domain Expert Validation**: Through collaboration with medical professionals, we expect expert agreement ratings above 4.0/5.0, demonstrating that extracted concepts align with clinical reasoning.

4. **Open Resources**: We will release: (a) curated concept vocabularies for healthcare domains, (b) pre-trained DG-CBL models for common foundation architectures, and (c) evaluation benchmarks for interpretability assessment.

### Broader Impact

**Scientific Impact**: This work advances the theoretical understanding of how domain knowledge can be systematically incorporated into neural network architectures while maintaining interpretability guarantees. It establishes a new paradigm for "interpretable-by-design" foundation model adaptation.

**Practical Impact**: In healthcare settings, DG-CBL enables clinicians to understand, verify, and correct AI recommendations at a conceptual level meaningful to their expertise. This addresses a critical barrier to clinical AI adoption and supports regulatory compliance requirements for explainable medical AI.

**Societal Impact**: By providing faithful explanations, DG-CBL supports AI auditing and bias detection. Domain experts can identify when models rely on spurious correlations by examining concept activations, enabling systematic debugging of fairness issues.

### Limitations and Future Work

We acknowledge potential limitations: (1) concept vocabularies may be incomplete or biased toward well-documented phenomena in literature, (2) the interpretability-performance trade-off may be more severe in some domains, and (3) evaluation of interpretability remains partially subjective. Future work will address multi-modal concept extraction, continual concept vocabulary expansion, and integration with causal reasoning frameworks.

---

This research proposal presents a comprehensive approach to bridging the gap between foundation model capabilities and inherent interpretability, with rigorous methodology and evaluation designed to advance both the science and practice of interpretable AI.