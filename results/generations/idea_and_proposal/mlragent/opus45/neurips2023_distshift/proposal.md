# Research Proposal: Adaptive Layer-Selective Fine-tuning for Preserving Foundation Model Robustness

## 1. Introduction

### Background

Foundation models—large-scale pretrained models such as BERT, GPT, and Vision Transformers—have revolutionized machine learning by achieving state-of-the-art performance across diverse tasks. Their success stems from pretraining on massive, heterogeneous datasets that encode rich, generalizable representations. However, when these models are deployed in real-world applications, they frequently encounter distribution shifts: discrepancies between training and deployment data distributions. Such shifts are particularly prevalent in critical domains like healthcare (variations across hospitals and patient demographics), wildlife conservation (seasonal and geographic variations), and autonomous systems (novel environmental conditions).

A well-documented phenomenon is that fine-tuning foundation models on specialized downstream tasks often degrades their inherent distributional robustness—a problem we term "robustness forgetting." While foundation models pretrained on diverse corpora exhibit impressive out-of-distribution (OOD) generalization, adapting them to specific tasks through conventional fine-tuning can overwrite the robust features learned during pretraining, replacing them with task-specific patterns that fail under distribution shift. This degradation poses significant challenges for deploying foundation models in safety-critical applications where robustness is paramount.

Recent work has explored various approaches to address this challenge, including ensemble methods with Bayesian distributional robustness (Pham et al., 2025), causal data augmentation (Bühler et al., 2026), and dual risk minimization strategies (Li et al., 2024). However, these methods often introduce substantial computational overhead or require extensive OOD labeled data, limiting their practical applicability. A fundamental question remains underexplored: **which layers of foundation models are responsible for encoding robust, transferable representations versus task-specific features vulnerable to distribution shifts?**

### Research Objectives

This research aims to develop a principled framework for understanding and exploiting the layer-wise structure of foundation models to preserve distributional robustness during fine-tuning. Our specific objectives are:

1. **Characterize layer-wise contributions to robustness**: Systematically analyze how different transformer layers contribute to in-distribution (ID) performance versus OOD robustness across multiple types of distribution shifts (domain, subpopulation, and temporal).

2. **Develop gradient-based sensitivity metrics**: Design attribution methods that quantify each layer's sensitivity to distribution shifts, enabling principled identification of "robust" versus "task-specific" layers.

3. **Create an adaptive layer-selective fine-tuning algorithm**: Propose an automated method that determines optimal layer freezing patterns using minimal OOD validation data or shift-type metadata, achieving Pareto-optimal trade-offs between ID accuracy and OOD robustness.

### Significance

This research addresses a critical gap in the deployment of foundation models under distribution shift. By providing both theoretical insights into the layer-wise encoding of robustness and practical algorithms for selective fine-tuning, our work will enable practitioners to adapt foundation models to specialized domains without sacrificing the robustness benefits of pretraining. The potential impact spans healthcare (robust clinical models across hospitals), environmental monitoring (models that generalize across geographic regions), and any application where distribution shifts are inevitable but labeled OOD data is scarce.

## 2. Methodology

### 2.1 Problem Formulation

Let $f_\theta$ denote a foundation model with $L$ transformer layers, where $\theta = \{\theta^{(1)}, \theta^{(2)}, \ldots, \theta^{(L)}\}$ represents the parameters of each layer. Given a downstream task with training distribution $P_{train}$ and potential OOD distributions $\{Q_1, Q_2, \ldots, Q_K\}$, our goal is to find a fine-tuning strategy that optimizes:

$$\min_{\theta'} \mathcal{L}_{ID}(f_{\theta'}; P_{train}) + \lambda \sum_{k=1}^{K} \mathcal{L}_{OOD}(f_{\theta'}; Q_k)$$

where $\mathcal{L}_{ID}$ and $\mathcal{L}_{OOD}$ denote the in-distribution and out-of-distribution losses, respectively, and $\lambda$ controls the robustness-accuracy trade-off.

### 2.2 Layer-wise Analysis Framework

#### Phase 1: Systematic Layer Freezing Experiments

We conduct comprehensive experiments by systematically varying which layers are frozen during fine-tuning. For a model with $L$ layers, we define a binary mask $\mathbf{m} = (m_1, m_2, \ldots, m_L) \in \{0, 1\}^L$, where $m_l = 1$ indicates that layer $l$ is frozen (not updated during fine-tuning).

For each mask configuration $\mathbf{m}$, we fine-tune the model and evaluate:

$$\text{ID-Acc}(\mathbf{m}) = \mathbb{E}_{(x,y) \sim P_{test}}[\mathbf{1}(\hat{y} = y)]$$

$$\text{OOD-Acc}_k(\mathbf{m}) = \mathbb{E}_{(x,y) \sim Q_k}[\mathbf{1}(\hat{y} = y)]$$

We systematically explore:
- **Contiguous freezing**: Freeze layers $1$ to $l$ for $l \in \{0, 1, \ldots, L\}$
- **Reverse contiguous freezing**: Freeze layers $l$ to $L$
- **Alternating patterns**: Freeze every $k$-th layer
- **Block-wise freezing**: Freeze specific blocks (e.g., attention vs. feed-forward)

#### Phase 2: Gradient-Based Sensitivity Attribution

We develop a sensitivity metric $S_l$ for each layer $l$ that quantifies its contribution to distribution shift vulnerability. Define the gradient of the loss with respect to layer $l$'s activations:

$$g_l(x) = \nabla_{h^{(l)}} \mathcal{L}(f_\theta(x), y)$$

where $h^{(l)}$ is the hidden representation at layer $l$.

Our **Distribution Shift Sensitivity Score (DSSS)** for layer $l$ is:

$$S_l = \mathbb{E}_{x \sim P}\left[\|g_l(x)\|_2\right] - \mathbb{E}_{x \sim Q}\left[\|g_l(x)\|_2\right] + \alpha \cdot \text{Var}_{x \sim Q}\left[\|g_l(x)\|_2\right]$$

where the first two terms capture the gradient magnitude difference between ID and OOD data, and the variance term captures instability under OOD inputs. Layers with high $|S_l|$ are more sensitive to distribution shifts.

Additionally, we compute the **Feature Drift Score**:

$$D_l = \|\mathbb{E}_{x \sim P}[h^{(l)}(x)] - \mathbb{E}_{x \sim Q}[h^{(l)}(x)]\|_2$$

measuring how much the layer's representations drift under distribution shift.

### 2.3 Adaptive Layer-Selective Fine-tuning Algorithm (ALSF)

Based on insights from Phases 1 and 2, we propose the **Adaptive Layer-Selective Fine-tuning (ALSF)** algorithm:

**Algorithm: ALSF**

**Input**: Pretrained model $f_\theta$, training data $D_{train}$, small OOD validation set $D_{val}^{OOD}$ (or shift-type metadata), budget $B$ for frozen layers

**Step 1: Compute Layer Sensitivity Scores**
1. Fine-tune a probe model for $T_{probe}$ steps on $D_{train}$
2. For each layer $l \in \{1, \ldots, L\}$:
   - Compute $S_l$ using ID samples from $D_{train}$ and OOD samples from $D_{val}^{OOD}$
   - Compute $D_l$ for feature drift estimation

**Step 2: Rank Layers by Robustness Contribution**
$$R_l = \beta_1 \cdot \text{normalize}(S_l) + \beta_2 \cdot \text{normalize}(D_l)$$

where $\beta_1, \beta_2$ are hyperparameters (default: $\beta_1 = 0.7, \beta_2 = 0.3$).

**Step 3: Adaptive Mask Selection**
- If OOD validation data available:
  - Use Bayesian optimization to find optimal mask $\mathbf{m}^*$ maximizing:
  $$\mathcal{J}(\mathbf{m}) = \text{ID-Acc}(\mathbf{m}) + \gamma \cdot \text{OOD-Acc}(\mathbf{m}) \quad \text{s.t.} \sum_l m_l \leq B$$
  
- If only shift-type metadata available:
  - Use pre-computed lookup table mapping shift types to recommended freezing patterns
  - For domain shifts: freeze early layers (1 to $\lfloor L/3 \rfloor$)
  - For subpopulation shifts: freeze middle layers ($\lfloor L/3 \rfloor$ to $\lfloor 2L/3 \rfloor$)
  - For temporal shifts: freeze later layers with lowest $R_l$

**Step 4: Selective Fine-tuning**
Fine-tune $f_\theta$ with mask $\mathbf{m}^*$:
$$\theta'^{(l)} = \begin{cases} \theta^{(l)} & \text{if } m_l = 1 \\ \theta^{(l)} - \eta \nabla_{\theta^{(l)}} \mathcal{L} & \text{if } m_l = 0 \end{cases}$$

**Output**: Fine-tuned model $f_{\theta'}$

### 2.4 Experimental Design

#### Datasets and Benchmarks

We evaluate on established distribution shift benchmarks:

1. **WILDS Benchmark** (Koh et al., 2021):
   - *Camelyon17*: Tumor detection across hospitals (domain shift)
   - *CivilComments*: Toxicity detection across demographic groups (subpopulation shift)
   - *FMoW*: Land use classification across time periods (temporal shift)
   - *iWildCam*: Animal classification across camera traps (domain shift)

2. **DomainBed** (Gulrajani & Lopez-Paz, 2021):
   - PACS, VLCS, OfficeHome, TerraIncognita

3. **Natural Language Understanding**:
   - MNLI with HANS evaluation (syntactic heuristic shift)
   - Amazon Reviews across product categories

#### Foundation Models

We experiment with:
- **Vision**: ViT-B/16, ViT-L/16, CLIP (ViT-based)
- **Language**: BERT-base, BERT-large, RoBERTa, Llama-2-7B

#### Baselines

We compare against:
1. Full fine-tuning (all layers updated)
2. Linear probing (only classifier head)
3. BitFit (bias terms only)
4. LoRA (low-rank adaptation)
5. LP-FT (linear probing then fine-tuning)
6. WiSE-FT (weight-space ensembling)
7. DRM (Dual Risk Minimization, Li et al., 2024)

#### Evaluation Metrics

- **ID Accuracy**: Performance on in-distribution test set
- **OOD Accuracy**: Performance on out-of-distribution test sets
- **Effective Robustness** (Taori et al., 2020): OOD accuracy relative to ID accuracy
- **Pareto Efficiency**: Trade-off curves between ID and OOD performance
- **Computational Cost**: Training time and memory requirements

#### Experimental Protocol

1. **5-fold cross-validation** with different random seeds
2. **Hyperparameter tuning** on validation sets (ID for baselines, mixed ID/OOD for ALSF)
3. **Statistical significance testing** using paired t-tests with Bonferroni correction
4. **Ablation studies** on each component of ALSF

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Empirical Findings on Layer-wise Robustness**:
   - We expect to confirm and extend the hypothesis that early-to-middle layers encode more transferable, robust representations, while later layers capture task-specific patterns. We anticipate discovering nuanced patterns—for instance, attention layers may contribute differently to robustness than feed-forward layers.

2. **Novel Sensitivity Metrics**:
   - The proposed DSSS and Feature Drift metrics will provide interpretable, computationally efficient tools for diagnosing layer vulnerability to distribution shifts without requiring full retraining.

3. **State-of-the-art Robustness-Accuracy Trade-offs**:
   - We expect ALSF to achieve Pareto-optimal performance, improving OOD accuracy by 3-8% over full fine-tuning while maintaining within 1-2% of ID accuracy on WILDS benchmarks. In low-OOD-data regimes (≤100 OOD samples), we anticipate 5-10% improvements over existing methods.

4. **Practical Guidelines**:
   - We will release comprehensive guidelines mapping distribution shift types to recommended layer freezing strategies, enabling practitioners without OOD validation data to make informed decisions.

5. **Open-source Implementation**:
   - A PyTorch/Hugging Face library implementing ALSF with pre-computed sensitivity scores for popular foundation models.

### Broader Impact

**Scientific Impact**: This research bridges the gap between empirical observations of robustness forgetting and mechanistic understanding of how foundation models encode robust features. The layer-wise analysis framework contributes to the interpretability of deep learning models under distribution shift.

**Practical Impact**: Healthcare, environmental monitoring, and autonomous systems will benefit from models that maintain robustness when deployed across diverse populations and conditions. By reducing the need for extensive OOD labeled data, ALSF democratizes robust model adaptation for resource-constrained settings.

**Methodological Impact**: The adaptive fine-tuning paradigm—where fine-tuning decisions are informed by model structure rather than purely data-driven—opens new directions for efficient and robust transfer learning.

### Limitations and Future Work

We acknowledge that our initial investigation focuses on transformer architectures; extending to other foundation model families (e.g., state-space models) remains future work. Additionally, the effectiveness of ALSF may vary with pretraining data composition, warranting investigation into pretraining-aware layer selection strategies.

In conclusion, this research addresses a fundamental challenge in deploying foundation models under distribution shift by providing both theoretical insights and practical algorithms for layer-selective fine-tuning, with significant implications for robust machine learning in critical applications.