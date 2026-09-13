# Research Proposal: Geometric Mergeability Score: A Predictive Metric for Neural Network Model Merging Success

## 1. Introduction

### 1.1 Background

The contemporary deep learning paradigm has been dominated by the "bigger is better" philosophy, where scaling model size and training data has yielded remarkable performance gains across diverse domains. However, this approach is rapidly approaching an inflection point characterized by prohibitive computational costs, environmental concerns, and fundamental limitations in model maintainability. A particularly wasteful aspect of current practice is the complete discarding of deprecated models in favor of training new ones from scratch—a stark contrast to the modular, reusable design principles that have long governed software engineering.

Model merging has emerged as a promising paradigm for addressing these limitations by enabling the combination of independently trained models into unified systems that inherit capabilities from their constituents. Techniques such as Model Soups, Task Arithmetic, and TIES-Merging have demonstrated that models fine-tuned from shared pre-trained bases can often be successfully averaged in parameter space, yielding multi-task models without additional training. This capability is foundational for collaborative, decentralized, and continual deep learning, where practitioners independently develop specialized models that must later be integrated.

However, a critical gap exists in current model merging practice: **the absence of predictive metrics for merge success**. Practitioners currently operate in a trial-and-error mode, attempting merges without knowing beforehand whether the combination will succeed or catastrophically fail. This blind approach wastes computational resources, hinders collaborative development, and prevents the principled construction of modular deep learning systems.

Recent theoretical work on Linear Mode Connectivity (LMC) has established that models fine-tuned from shared pre-trained checkpoints often reside in the same loss basin, enabling successful linear interpolation. The "Landscaping LMC" framework characterizes this phenomenon through the geometry of loss landscapes, identifying barrier height between models as the fundamental determinant of merge success. Complementary work on "Demystifying Mergeability" has identified gradient alignment and subspace overlap as foundational, method-agnostic prerequisites for successful merging. Despite these theoretical advances, no unified, practical metric exists to predict mergeability before attempting the merge.

### 1.2 Research Objectives

This research proposes the **Geometric Mergeability Score (GMS)**, a predictive metric that combines three complementary geometric properties to estimate merge success before execution. Our specific objectives are:

1. **Develop the GMS metric** by integrating gradient alignment ($\alpha$), singular value subspace overlap ($\beta$), and Fisher information distance ($\gamma$) into a unified predictive score.

2. **Validate GMS predictive power** by demonstrating strong correlation ($\rho > 0.7$) with actual merged model performance across diverse model pairs and task families.

3. **Establish component complementarity** by showing that each GMS component contributes independently to predictive power, capturing distinct geometric aspects of mergeability.

4. **Demonstrate threshold generalization** by proving that calibrated thresholds transfer across task domains, enabling practical deployment without per-domain tuning.

### 1.3 Significance

The successful development of GMS would represent a significant advance for modular deep learning with several key impacts:

- **Resource Efficiency**: Pre-screening model pairs would dramatically reduce failed merge attempts, saving computational resources and practitioner time.
- **Collaborative Development**: Teams could assess compatibility of independently developed models before attempting integration, enabling principled collaborative workflows.
- **Theoretical Understanding**: GMS would provide empirical validation of geometric theories of model merging, advancing our understanding of loss landscape structure.
- **Practical Tooling**: A validated GMS implementation would serve as essential infrastructure for emerging model merging ecosystems and collaborative training platforms.

## 2. Methodology

### 2.1 Theoretical Foundation

Our core hypothesis posits that under Linear Mode Connectivity conditions, the success of model merging is determined by the loss barrier height between models in parameter space. GMS estimates this barrier height through three complementary geometric measurements, each capturing a distinct aspect of model compatibility.

**Hypothesis (H-GMS-v1):** Under the condition that two neural network models are fine-tuned from the same pre-trained base with Linear Mode Connectivity, if we compute a Geometric Mergeability Score combining gradient alignment ($\alpha$), singular value subspace overlap ($\beta$), and Fisher information distance ($\gamma$), then models with $\text{GMS} > \tau$ will merge successfully with bounded performance loss $\epsilon$, because GMS quantifies the loss barrier height between models in parameter space.

### 2.2 GMS Component Definitions

#### 2.2.1 Gradient Alignment ($\alpha$)

Gradient alignment measures task compatibility by computing the cosine similarity between gradients of the two models evaluated at the base model parameters:

$$\alpha = \frac{\mathbf{g}_A \cdot \mathbf{g}_B}{\|\mathbf{g}_A\| \|\mathbf{g}_B\|}$$

where $\mathbf{g}_A = \nabla_\theta \mathcal{L}_A(\theta_{\text{base}})$ and $\mathbf{g}_B = \nabla_\theta \mathcal{L}_B(\theta_{\text{base}})$ are gradients computed on validation batches from tasks A and B respectively, evaluated at the shared pre-trained base parameters $\theta_{\text{base}}$.

**Interpretation**: High $\alpha$ values (> 0.5) indicate that the two tasks push parameters in compatible directions, suggesting low interference during merging. Negative values indicate conflicting optimization objectives.

#### 2.2.2 Singular Value Subspace Overlap ($\beta$)

Subspace overlap quantifies shared representational structure by measuring the alignment of top-$k$ singular vectors of the weight update matrices:

$$\beta = \frac{\|U_A^\top U_B\|_F}{\sqrt{k}}$$

where $U_A \in \mathbb{R}^{d \times k}$ and $U_B \in \mathbb{R}^{d \times k}$ contain the top-$k$ left singular vectors of the weight updates $\Delta W_A = W_A - W_{\text{base}}$ and $\Delta W_B = W_B - W_{\text{base}}$ respectively. We use randomized SVD with $k = 50$ for computational efficiency.

**Interpretation**: High $\beta$ values (> 0.7) indicate that task-specific adaptations occupy similar subspaces, enabling averaging without destructive interference. This is grounded in findings that top-$k$ singular vectors capture 99% of task-specific information.

#### 2.2.3 Fisher Information Distance ($\gamma$)

Fisher distance captures parameter importance similarity using the diagonal Fisher-Rao distance:

$$\gamma = \sqrt{\sum_{i} (\theta_A^i - \theta_B^i)^2 \cdot \frac{F_A^i + F_B^i}{2}}$$

where $F_A^i$ and $F_B^i$ are diagonal elements of the empirical Fisher information matrices computed on validation sets:

$$F^i = \mathbb{E}_{x \sim \mathcal{D}} \left[ \left( \frac{\partial \log p(y|x; \theta)}{\partial \theta^i} \right)^2 \right]$$

**Interpretation**: Low $\gamma$ values (< 1.0) indicate that parameter differences are concentrated in regions of low importance, enabling averaging without significant performance degradation.

#### 2.2.4 Unified GMS Computation

The Geometric Mergeability Score combines the three components:

$$\text{GMS} = w_1 \cdot \alpha + w_2 \cdot \beta - w_3 \cdot \gamma_{\text{norm}}$$

where $\gamma_{\text{norm}} = \gamma / \gamma_{\max}$ normalizes Fisher distance to $[0, 1]$, and weights $w_1 = w_2 = w_3 = 1/3$ provide equal contribution by default. The subtraction of $\gamma_{\text{norm}}$ reflects that lower Fisher distance indicates better mergeability.

**GMS Range**: $[-1/3, 1]$ where higher values predict better merge success.

### 2.3 Data Collection

#### 2.3.1 Model Pair Construction

We construct a diverse dataset of model pairs spanning multiple architectures and task families:

**Vision Models (ViT-B/16 base):**
- Task families: Image classification (CIFAR-100, Flowers-102, DTD), Fine-grained recognition (CUB-200, Stanford Cars), Scene understanding (SUN397, Places365)
- Fine-tuning: Both full fine-tuning and LoRA adapters ($r = 16$)
- Pairs: 15 within-family + 15 cross-family = 30 pairs

**Language Models (RoBERTa-base):**
- Task families: Sentiment analysis (SST-2, IMDB, Yelp), NLI (MNLI, SNLI, QNLI), Question answering (SQuAD, TriviaQA)
- Fine-tuning: LoRA adapters ($r = 8$)
- Pairs: 15 within-family + 15 cross-family = 30 pairs

**Total**: 60+ model pairs ensuring statistical power for correlation analysis.

#### 2.3.2 Ground Truth Merge Performance

For each model pair $(M_A, M_B)$, we compute ground truth merge performance using uniform averaging:

$$\theta_{\text{merged}} = 0.5 \cdot \theta_A + 0.5 \cdot \theta_B$$

Merge success is measured as:

$$\text{MergePerf} = \frac{1}{2} \left( \text{Acc}_A(\theta_{\text{merged}}) + \text{Acc}_B(\theta_{\text{merged}}) \right)$$

where $\text{Acc}_A$ and $\text{Acc}_B$ are accuracies on the respective task validation sets.

### 2.4 Experimental Design

#### 2.4.1 Primary Validation (P1: GMS-Performance Correlation)

**Objective**: Validate that GMS correlates strongly with merge performance.

**Procedure**:
1. Compute GMS for all 60+ model pairs
2. Compute ground truth merge performance for all pairs
3. Calculate Spearman rank correlation $\rho$ between GMS and MergePerf
4. Compute bootstrap 95% confidence intervals (10,000 resamples)

**Success Criterion**: $\rho > 0.7$ with $p < 0.05$

**Falsification Criterion**: $\rho < 0.5$ rejects the hypothesis

#### 2.4.2 Component Complementarity Analysis (P2)

**Objective**: Verify that each GMS component contributes independently.

**Procedure**:
1. Compute pairwise Pearson correlations between $\alpha$, $\beta$, and $\gamma$
2. Perform ablation study: compute correlation with MergePerf using:
   - Single components: $\alpha$ only, $\beta$ only, $\gamma$ only
   - Pairwise combinations: $(\alpha, \beta)$, $(\alpha, \gamma)$, $(\beta, \gamma)$
   - Full GMS: $(\alpha, \beta, \gamma)$
3. Compute incremental $R^2$ contribution of each component

**Success Criterion**: Pairwise correlations < 0.7; full GMS outperforms all ablations

**Falsification Criterion**: Pairwise correlation > 0.9 indicates redundancy

#### 2.4.3 Threshold Generalization (P3)

**Objective**: Demonstrate that calibrated thresholds transfer across domains.

**Procedure**:
1. Split task families into calibration (2 families) and test (1 family)
2. On calibration set, find optimal threshold $\tau^*$ maximizing F1-score for binary merge success prediction
3. Apply $\tau^*$ to held-out test family
4. Compute AUC-ROC on test family
5. Repeat with 3-fold cross-validation across family splits

**Success Criterion**: Mean AUC > 0.75 across folds

**Falsification Criterion**: AUC < 0.6 indicates failure to generalize

#### 2.4.4 Baseline Comparisons (SH3)

**Objective**: Demonstrate GMS superiority over simpler alternatives.

**Baselines**:
1. **Random Selection**: Random binary prediction
2. **Parameter Distance**: $\|\theta_A - \theta_B\|_2$
3. **Single Components**: $\alpha$-only, $\beta$-only, $\gamma$-only predictors
4. **Task Similarity**: Cosine similarity of task embeddings (using CLIP)

**Metrics**: Spearman $\rho$, AUC-ROC, precision@k

### 2.5 Evaluation Metrics

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Spearman $\rho$ | Rank correlation between GMS and MergePerf | $\rho > 0.7$ |
| AUC-ROC | Area under ROC curve for binary success prediction | AUC > 0.75 |
| Precision@k | Precision in top-k GMS-ranked pairs | P@5 > 0.8 |
| Component Independence | Max pairwise correlation among $\alpha$, $\beta$, $\gamma$ | $r < 0.7$ |
| Ablation Gap | $\rho_{\text{full}} - \max(\rho_{\text{ablated}})$ | Gap > 0.1 |

### 2.6 Implementation Details

**Computational Requirements**:
- GMS computation: ~1 GPU-hour per model pair (dominated by Fisher estimation)
- Total validation: ~60-80 GPU-hours for full experimental suite

**Efficiency Optimizations**:
- Randomized SVD with $k = 50$ (vs. full SVD)
- Diagonal Fisher approximation (vs. full Fisher matrix)
- Gradient computation on 1024-sample validation batches

**Software**: PyTorch, HuggingFace Transformers, custom GMS library (to be released)

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical foundation and preliminary analysis, we anticipate the following outcomes:

**Primary Outcome (P1)**: GMS will achieve Spearman correlation $\rho \approx 0.75-0.85$ with merged model performance, substantially exceeding the 0.7 threshold. This prediction is grounded in recent findings that gradient alignment and subspace overlap are foundational predictors of merge success.

**Component Analysis (P2)**: We expect each component to contribute uniquely:
- $\alpha$ (gradient alignment): Primary predictor for task compatibility
- $\beta$ (subspace overlap): Critical for detecting representational interference
- $\gamma$ (Fisher distance): Important for identifying parameter importance conflicts

Pairwise correlations are expected to be moderate (0.3-0.6), confirming complementarity.

**Threshold Generalization (P3)**: We anticipate AUC > 0.8 on held-out task families, demonstrating that the geometric properties captured by GMS are domain-agnostic.

### 3.2 Potential Limitations and Mitigations

**Limitation 1**: GMS may underperform for models with fundamentally incompatible tasks.
**Mitigation**: Clearly define scope boundaries; GMS is designed for models with LMC, not arbitrary model pairs.

**Limitation 2**: Equal component weights may not be optimal for all merging methods.
**Mitigation**: Provide learned weight variants for specific methods (Task Arithmetic, TIES-Merging) as extensions.

**Limitation 3**: Diagonal Fisher approximation may miss important parameter interactions.
**Mitigation**: Investigate block-diagonal or low-rank Fisher approximations in future work.

### 3.3 Broader Impact

**For Practitioners**: GMS provides a practical tool for pre-screening model pairs before attempting merges, reducing wasted computation and enabling more efficient collaborative workflows. A practitioner developing a specialized model could query a model registry for compatible models, dramatically accelerating multi-task model development.

**For Collaborative ML**: GMS enables principled decentralized model development where teams can independently train specialized models with confidence that compatible models can be identified and merged. This supports the workshop's vision of modular, collaborative deep learning.

**For Continual Learning**: By predicting which new task models can be successfully merged with existing systems, GMS provides a foundation for continual learning without catastrophic forgetting—models can be selectively merged based on predicted compatibility.

**For Theoretical Understanding**: Empirical validation of GMS would provide strong evidence for geometric theories of model merging, advancing our understanding of loss landscape structure and Linear Mode Connectivity.

### 3.4 Future Directions

1. **Adaptive Weighting**: Learn optimal component weights for specific merging methods
2. **Multi-Model Extension**: Extend GMS to predict success of merging $n > 2$ models
3. **Architecture-Aware GMS**: Incorporate architectural similarity for cross-architecture merging
4. **Online GMS**: Develop streaming variants for continual learning scenarios
5. **Theoretical Bounds**: Derive formal guarantees relating GMS to merge performance bounds

### 3.5 Deliverables

1. **GMS Library**: Open-source PyTorch implementation with efficient computation
2. **Benchmark Dataset**: 60+ model pairs with ground truth merge performance
3. **Empirical Analysis**: Comprehensive validation across vision and language domains
4. **Practitioner Guidelines**: Threshold recommendations and usage documentation

In conclusion, the Geometric Mergeability Score represents a critical step toward principled, predictive model merging—transforming the current trial-and-error approach into a systematic methodology that enables truly modular deep learning systems.