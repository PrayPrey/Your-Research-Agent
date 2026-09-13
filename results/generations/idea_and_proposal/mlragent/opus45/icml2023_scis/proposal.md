# Research Proposal: Adaptive Spurious Correlation Discovery via Gradient-Based Feature Attribution Disagreement

## 1. Introduction

### Background

Machine learning models deployed in high-stakes domains frequently fail due to their reliance on spurious correlations—statistical associations that hold in training data but do not reflect true causal relationships. These failures manifest across diverse applications: medical imaging systems that detect hospital-specific scanner artifacts rather than disease biomarkers, natural language models that exploit lexical overlap rather than semantic reasoning, and genomic risk predictors that perform poorly on underrepresented populations. Despite achieving impressive benchmark performance, such models exhibit brittleness when confronted with distribution shifts in deployment.

The fundamental challenge is that spurious correlations are often invisible until catastrophic failures occur. Current approaches to addressing this problem fall into two categories: mitigation methods that assume prior knowledge of spurious features, and discovery methods that require expensive group annotations. For instance, Group Distributionally Robust Optimization (GroupDRO) optimizes worst-group performance but requires labeled subgroups, while Invariant Risk Minimization (IRM) needs multiple training environments with known distribution shifts. Recent work on logit correction and evidential alignment has shown promise in reducing spurious correlation reliance without explicit group labels, yet these methods focus on mitigation rather than discovery—they improve robustness without explaining which features are problematic.

The literature reveals a critical gap: there exists no systematic, automated approach for proactively discovering spurious correlations without prior assumptions about their nature or access to group annotations. This gap is particularly problematic because practitioners cannot fix what they cannot see. The recent survey by Ye et al. (2024) emphasizes that spurious correlation discovery remains understudied compared to mitigation, despite being a prerequisite for targeted interventions.

### Research Objectives

This research proposes a novel self-supervised framework—**Attribution Disagreement Analysis (ADA)**—for automatically discovering spurious correlations by exploiting a key insight: spurious features, while statistically predictive, exhibit inconsistent importance across model instances due to their lack of causal grounding. Specifically, our objectives are:

1. **Develop a principled method** for quantifying feature-level attribution variance across diverse model ensembles as a signal for spurious correlation detection.
2. **Create an interpretable clustering framework** that aggregates high-variance features into coherent "spurious hypotheses" suitable for human verification.
3. **Validate the framework** on standard spurious correlation benchmarks and real-world medical imaging datasets, demonstrating practical utility.
4. **Establish connections** between attribution disagreement and causal feature identification, bridging discovery and mitigation paradigms.

### Significance

This work addresses the workshop's central themes by providing a practical diagnostic tool that operates without the restrictive assumptions of existing methods. By enabling automated discovery before deployment, ADA transforms spurious correlation mitigation from a reactive to a proactive endeavor. The framework is particularly valuable for practitioners who lack domain expertise to anticipate specific shortcuts, yet face critical reliability requirements.

## 2. Methodology

### 2.1 Theoretical Foundation

Our approach rests on the hypothesis that spurious features exhibit higher attribution instability than causal features across model instances. Let $f_\theta: \mathcal{X} \rightarrow \mathcal{Y}$ denote a model parameterized by $\theta$, and let $\phi(f_\theta, x)_i$ represent the attribution score for feature $i$ given input $x$. We posit that for a spurious feature $s$ and a causal feature $c$:

$$\text{Var}_\theta[\phi(f_\theta, x)_s] > \text{Var}_\theta[\phi(f_\theta, x)_c]$$

This inequality arises because causal features have consistent predictive relationships with labels across all valid models, while spurious features may be utilized differently depending on initialization, capacity, and training dynamics. Models that happen to exploit a particular shortcut will assign high attribution to the corresponding spurious feature, while others may find alternative predictive pathways.

### 2.2 Framework Architecture

The ADA framework consists of four interconnected stages:

**Stage 1: Diverse Ensemble Construction**

We train an ensemble of $K$ models $\{f_{\theta_1}, f_{\theta_2}, \ldots, f_{\theta_K}\}$ designed to maximize diversity in feature utilization while maintaining comparable predictive performance. Diversity is induced through:

- **Initialization diversity**: Random weight initialization with different seeds
- **Augmentation diversity**: Each model receives a distinct augmentation policy sampled from a predefined augmentation space $\mathcal{A}$
- **Architectural micro-variations**: Small perturbations in layer widths or dropout rates

For model $k$, the training objective is:

$$\theta_k^* = \argmin_\theta \mathcal{L}_{CE}(f_\theta, \mathcal{D}) + \lambda \mathcal{R}(\theta)$$

where $\mathcal{L}_{CE}$ is cross-entropy loss, $\mathcal{D}$ is the training dataset, and $\mathcal{R}(\theta)$ is a regularization term. We set $K \geq 10$ to ensure sufficient statistical power for variance estimation.

**Stage 2: Attribution Computation**

For each model $f_{\theta_k}$ and input $x$, we compute feature attributions using Integrated Gradients (IG), chosen for its axiomatic properties including sensitivity and implementation invariance:

$$\phi(f_{\theta_k}, x)_i = (x_i - x'_i) \times \int_{\alpha=0}^{1} \frac{\partial f_{\theta_k}(x' + \alpha(x - x'))}{\partial x_i} d\alpha$$

where $x'$ is a baseline input (typically zero or dataset mean). For high-dimensional inputs like images, we aggregate pixel-level attributions to semantically meaningful regions using superpixel segmentation (SLIC algorithm) or predefined object detectors.

**Stage 3: Disagreement Quantification**

For each feature dimension $i$ and input $x$, we compute the cross-model attribution variance:

$$V_i(x) = \frac{1}{K-1} \sum_{k=1}^{K} \left(\phi(f_{\theta_k}, x)_i - \bar{\phi}(x)_i\right)^2$$

where $\bar{\phi}(x)_i = \frac{1}{K}\sum_{k=1}^{K} \phi(f_{\theta_k}, x)_i$.

To obtain dataset-level spuriousness scores, we aggregate across samples:

$$S_i = \frac{1}{N} \sum_{n=1}^{N} \frac{V_i(x_n)}{\bar{\phi}(x_n)_i^2 + \epsilon}$$

The normalization by squared mean attribution ensures that high variance is meaningful relative to feature importance, and $\epsilon$ prevents division by zero. Features with $S_i$ exceeding a threshold $\tau$ (determined via held-out validation) are flagged as spurious candidates.

**Stage 4: Spurious Hypothesis Generation**

Raw spurious feature candidates are often numerous and fragmented. We cluster them into interpretable hypotheses using the following procedure:

1. **Feature embedding**: For image data, extract semantic descriptors for each high-variance region using a pretrained vision-language model (e.g., CLIP). For text, use contextualized embeddings from the input encoder.

2. **Hierarchical clustering**: Apply agglomerative clustering with Ward linkage on the embedded features:

$$d(u, v) = \sqrt{\frac{|u||v|}{|u|+|v|}} \|\mathbf{c}_u - \mathbf{c}_v\|_2$$

where $\mathbf{c}_u$ and $\mathbf{c}_v$ are cluster centroids.

3. **Hypothesis labeling**: Generate natural language descriptions for each cluster using the nearest neighbors in the vision-language embedding space, producing interpretable spurious hypotheses like "hospital equipment in image corners" or "negation words in premises."

### 2.3 Experimental Design

**Datasets**: We evaluate ADA on established benchmarks and real-world data:

- *Waterbirds*: Bird species classification with spurious background correlations (water/land)
- *CelebA*: Hair color prediction with spurious gender correlation
- *MultiNLI*: Natural language inference with lexical overlap shortcuts
- *CheXpert*: Chest X-ray classification (real medical imaging with known scanner artifacts)

**Baselines**: We compare against:
- Random feature flagging (control)
- High-activation feature detection (single model)
- TCAV-based concept detection (requires concept supervision)
- Clustering-based methods (Li et al., 2025)

**Evaluation Metrics**:

1. **Discovery precision/recall**: Using ground-truth spurious feature annotations where available, we measure:
   $$\text{Precision} = \frac{|\text{Flagged} \cap \text{Spurious}|}{|\text{Flagged}|}$$
   $$\text{Recall} = \frac{|\text{Flagged} \cap \text{Spurious}|}{|\text{Spurious}|}$$

2. **Downstream robustness improvement**: After discovery, we apply simple mitigation (upweighting samples with low spurious feature activation) and measure worst-group accuracy improvement.

3. **Human evaluation**: Domain experts rate the interpretability and actionability of generated spurious hypotheses on a 5-point Likert scale.

4. **Computational efficiency**: Wall-clock time and GPU memory requirements relative to baselines.

**Ablation Studies**: We systematically vary:
- Ensemble size $K \in \{5, 10, 20, 50\}$
- Diversity mechanisms (initialization only, augmentation only, combined)
- Attribution methods (Integrated Gradients, GradCAM, SHAP)
- Clustering granularity

### 2.4 Implementation Details

Models are implemented in PyTorch with standard architectures (ResNet-50 for images, BERT-base for text). Integrated Gradients are computed with 50 interpolation steps. Ensemble training is parallelized across 8 NVIDIA A100 GPUs. The variance threshold $\tau$ is set at the 90th percentile of feature-level scores on a validation set. All experiments use 5 random seeds with reported mean and standard deviation.

## 3. Expected Outcomes & Impact

### Technical Contributions

We anticipate the following outcomes:

1. **Validated discovery method**: ADA will achieve $\geq$80% recall in identifying known spurious features on benchmarks while maintaining $\geq$60% precision, significantly outperforming unsupervised baselines.

2. **Interpretable diagnostics**: Generated spurious hypotheses will receive mean interpretability ratings $\geq$4.0/5.0 from domain experts, enabling actionable insights without requiring ML expertise.

3. **Robustness cascade**: Simple mitigation strategies informed by ADA discovery will improve worst-group accuracy by 5-15% compared to standard training, demonstrating the value of targeted discovery.

4. **Efficiency analysis**: The framework will operate within 2× the computational budget of single-model training, making it practical for real-world deployment.

### Broader Impact

This research directly addresses the workshop's mission of bridging discovery and deployment. By providing practitioners with automated diagnostic capabilities, ADA democratizes access to spurious correlation analysis, previously requiring deep domain expertise or expensive annotation campaigns. The framework is particularly impactful for:

- **Healthcare**: Enabling radiologists to verify that diagnostic models rely on clinically meaningful features before deployment
- **Fairness auditing**: Surfacing hidden demographic proxies without requiring sensitive attribute labels
- **Scientific discovery**: Distinguishing genuine biomarkers from dataset artifacts in genomics and drug discovery

The interpretable hypothesis generation component addresses the human verification challenge identified in prior literature, transforming raw statistical signals into actionable insights. By connecting attribution disagreement to causal reasoning, this work also advances theoretical understanding of when and why ensemble diversity reveals spurious patterns.

### Limitations and Future Directions

We acknowledge that ADA's effectiveness depends on ensemble diversity successfully capturing feature utilization variation. In cases where all models converge to identical shortcuts, the method may fail to flag spurious correlations. Future work will explore adversarial diversity objectives and connections to causal discovery algorithms that could provide theoretical guarantees. Additionally, extending the framework to temporal and sequential data presents interesting challenges for attribution aggregation.