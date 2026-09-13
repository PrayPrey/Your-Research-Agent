# Research Proposal: Entropic Alignment Score for Cross-Modal Representation Alignment

## 1. Title

**Entropic Alignment Score: An Information-Theoretic Metric for Quantifying and Optimizing Cross-Modal Representation Alignment in Vision-Language Models**

---

## 2. Introduction

### 2.1 Background

The convergence of representations across different neural models has emerged as one of the most intriguing phenomena in both artificial intelligence and neuroscience. Recent theoretical advances, particularly the Platonic Representation Hypothesis (PRH) proposed by Huh et al. (2024), suggest that diverse neural networks trained on similar data tend to converge toward a shared statistical structure—a "Platonic" representation of reality. This convergence appears to be driven by fundamental properties of learning dynamics rather than architectural choices alone.

Complementing this theoretical framework, Neural Thermodynamics (Ziyin et al., 2025) provides a mechanistic explanation for this convergence. The theory demonstrates that stochastic gradient descent (SGD) generates entropic forces through its discrete-time updates and inherent stochasticity. These forces systematically break continuous parameter symmetries, driving representations toward thermodynamically favorable configurations that happen to align across different models and modalities.

In the domain of multimodal learning, vision-language models such as CLIP, BLIP, and ALIGN have demonstrated remarkable capabilities in aligning visual and textual representations. These models learn joint embedding spaces where semantically related images and texts are positioned nearby, enabling powerful cross-modal retrieval and understanding. The success of these models provides empirical evidence for the theoretical predictions of PRH and Neural Thermodynamics.

However, a significant gap exists between theoretical understanding and practical measurement. Current metrics for assessing representation alignment—primarily Centered Kernel Alignment (CKA) and Representational Similarity Analysis (RSA)—measure correlation-based similarity rather than information-theoretic alignment. CKA computes the normalized Hilbert-Schmidt Independence Criterion between representation matrices, while RSA correlates pairwise distance matrices. While useful, these metrics do not directly capture the mutual information or predictive relationships between modalities that theory suggests should emerge from entropic convergence.

### 2.2 Research Objectives

This research proposes the **Entropic Alignment Score (EAS)**, a novel information-theoretic metric designed to bridge the gap between theoretical understanding of representation convergence and practical measurement of cross-modal alignment. Our primary objectives are:

1. **Develop and validate EAS** as a theoretically-grounded metric that directly measures how much one modality's embeddings reduce uncertainty about another's, operationalizing the predictions of PRH and Neural Thermodynamics.

2. **Demonstrate superior predictive validity** by showing that EAS correlates more strongly with downstream cross-modal retrieval performance than existing correlation-based metrics (CKA, RSA).

3. **Explore EAS as a training objective** to determine whether optimizing for information-theoretic alignment during training improves multimodal model performance.

### 2.3 Research Significance

This research addresses a critical need in the multimodal learning community. As vision-language models become increasingly central to AI applications—from image search to visual question answering—having principled metrics for measuring and optimizing cross-modal alignment becomes essential. The significance of this work spans multiple dimensions:

**Theoretical Contribution:** EAS provides the first direct operationalization of PRH's entropic convergence predictions, enabling empirical testing of theoretical claims about representation alignment.

**Practical Utility:** A metric that better predicts downstream performance enables more efficient model selection, architecture search, and training monitoring without requiring expensive task-specific evaluation.

**Training Advancement:** If EAS proves effective as a training objective, it could provide a new approach to improving multimodal alignment that is grounded in information theory rather than heuristic contrastive losses.

**Cross-Disciplinary Impact:** By connecting information-theoretic concepts with practical multimodal learning, this work facilitates dialogue between theoretical machine learning, neuroscience, and applied AI research.

---

## 3. Methodology

### 3.1 Entropic Alignment Score: Formal Definition

We define the Entropic Alignment Score (EAS) as a normalized measure of conditional entropy reduction between two modalities. Given embeddings $X$ from modality 1 (e.g., images) and $Y$ from modality 2 (e.g., text), EAS is defined as:

$$\text{EAS}(X, Y) = 1 - \frac{H(X|Y)}{H(X)}$$

where $H(X)$ is the marginal entropy of modality $X$ and $H(X|Y)$ is the conditional entropy of $X$ given $Y$. This formulation has several desirable properties:

- **Range:** EAS $\in [0, 1]$, where 0 indicates no alignment (Y provides no information about X) and 1 indicates perfect alignment (Y completely determines X).
- **Information-theoretic grounding:** EAS directly measures the fraction of uncertainty in X that is resolved by knowing Y.
- **Symmetry consideration:** We compute both $\text{EAS}(X, Y)$ and $\text{EAS}(Y, X)$, reporting the geometric mean as the symmetric EAS.

The symmetric EAS is computed as:

$$\text{EAS}_{\text{sym}}(X, Y) = \sqrt{\text{EAS}(X, Y) \cdot \text{EAS}(Y, X)}$$

### 3.2 Entropy Estimation via Variational Bounds

Direct entropy estimation in high-dimensional spaces (1024-d embeddings) is computationally intractable. We employ variational bounds based on the InfoNCE framework, which provides a tractable lower bound on mutual information:

$$I(X; Y) \geq \mathbb{E}\left[\frac{1}{N}\sum_{i=1}^{N} \log \frac{e^{f(x_i, y_i)}}{\frac{1}{N}\sum_{j=1}^{N} e^{f(x_i, y_j)}}\right]$$

where $f(x, y)$ is a critic function parameterized by a neural network. Since $I(X; Y) = H(X) - H(X|Y)$, we can derive:

$$H(X|Y) \leq H(X) - \hat{I}_{\text{InfoNCE}}(X; Y)$$

For marginal entropy estimation, we employ the MINE (Mutual Information Neural Estimation) framework with a reference distribution. Specifically, we estimate $H(X)$ using:

$$H(X) \approx -\mathbb{E}_{p(x)}[\log p(x)] \approx \mathbb{E}_{p(x)}[T(x)] - \log \mathbb{E}_{q(x)}[e^{T(x)}]$$

where $T(x)$ is a neural network and $q(x)$ is a reference distribution (standard Gaussian).

### 3.3 Entropy Estimator Architecture

We implement the entropy estimator using an ensemble of 5 MINE networks to reduce variance:

**Critic Network Architecture:**
- Input: Concatenated embeddings $[x; y] \in \mathbb{R}^{2048}$ (for 1024-d embeddings per modality)
- Layer 1: Linear(2048, 1024) → LayerNorm → ReLU → Dropout(0.1)
- Layer 2: Linear(1024, 512) → LayerNorm → ReLU → Dropout(0.1)
- Layer 3: Linear(512, 1)
- Output: Scalar critic value $f(x, y)$

**Training Configuration:**
- Optimizer: Adam with learning rate $10^{-4}$
- Batch size: 512 paired samples
- Training steps: 10,000 per model evaluation
- Ensemble: 5 networks with different random seeds
- Final estimate: Mean of ensemble predictions with standard error

**Entropy Estimation Algorithm:**

```
Algorithm 1: EAS Computation
Input: Image embeddings X ∈ R^{n×d}, Text embeddings Y ∈ R^{n×d}
Output: EAS_sym(X, Y)

1. Initialize ensemble of K=5 critic networks {f_k}
2. For each critic f_k:
   a. For t = 1 to T=10000:
      - Sample batch B of n=512 paired (x_i, y_i)
      - Compute InfoNCE loss: L = -mean(log(softmax(f_k(x_i, y_j))))
      - Update f_k via Adam
   b. Estimate I_k(X;Y) using trained f_k on held-out data
3. Compute I(X;Y) = mean({I_k})
4. Estimate H(X) using MINE with Gaussian reference
5. Compute EAS(X,Y) = 1 - (H(X) - I(X;Y))/H(X)
6. Repeat steps 2-5 for EAS(Y,X)
7. Return EAS_sym = sqrt(EAS(X,Y) * EAS(Y,X))
```

### 3.4 Data Collection and Model Selection

**Vision-Language Models (n ≥ 15):**

| Model Family | Variants | Embedding Dim |
|--------------|----------|---------------|
| CLIP | ViT-B/32, ViT-B/16, ViT-L/14, ViT-L/14@336px | 512-768 |
| OpenCLIP | ViT-B/32, ViT-L/14, ViT-H/14, ViT-G/14 | 512-1024 |
| BLIP | Base, Large | 768 |
| BLIP-2 | ViT-G OPT, ViT-G FlanT5 | 768-1408 |
| ALIGN | Base | 640 |
| SigLIP | ViT-B/16, ViT-L/16 | 768-1024 |

**Evaluation Datasets:**
- **COCO Captions:** 330K image-caption pairs; 5K test set for retrieval evaluation
- **Flickr30k:** 31K images with 5 captions each; 1K test set for retrieval evaluation

**Embedding Extraction:**
For each model, we extract embeddings from the final projection layer (after any normalization) for both image and text encoders. Embeddings are L2-normalized before EAS computation.

### 3.5 Experimental Design

**Experiment 1: EAS-Retrieval Correlation (Primary Hypothesis P1)**

*Objective:* Validate that EAS correlates with cross-modal retrieval performance.

*Procedure:*
1. For each of 15+ models, extract embeddings on COCO and Flickr30k test sets
2. Compute EAS using the ensemble estimator (Section 3.3)
3. Evaluate retrieval performance: R@1, R@5, R@10 for both image→text and text→image
4. Compute Pearson correlation between EAS and retrieval metrics

*Statistical Analysis:*
- Primary metric: Pearson correlation coefficient $r$ with 95% CI via Fisher z-transformation
- Success criterion: $r > 0.7$ with $p < 0.05$ (one-tailed)
- Sample size justification: With $n=15$ models, power = 0.8 to detect $r = 0.7$ at $\alpha = 0.05$

**Experiment 2: Comparative Analysis with CKA/RSA (Prediction P2)**

*Objective:* Demonstrate EAS outperforms existing metrics in predicting retrieval performance.

*Procedure:*
1. For the same 15+ models, compute CKA and RSA between image and text embeddings
2. CKA computation: $\text{CKA}(X, Y) = \frac{\|Y^TX\|_F^2}{\|X^TX\|_F \|Y^TY\|_F}$
3. RSA computation: Spearman correlation between pairwise distance matrices
4. Compute correlations of each metric with R@1

*Statistical Analysis:*
- Williams' test for comparing dependent correlations (same samples)
- Success criterion: $r_{\text{EAS}} > r_{\text{CKA}}$ AND $r_{\text{EAS}} > r_{\text{RSA}}$ with $p < 0.05$
- Bonferroni correction for multiple comparisons

**Experiment 3: EAS as Training Objective (Prediction P3)**

*Objective:* Evaluate whether EAS can improve multimodal alignment when used as auxiliary loss.

*Procedure:*
1. Train CLIP-style models from scratch on CC3M dataset (3M image-text pairs)
2. Baseline: Standard InfoNCE contrastive loss
3. Treatment: InfoNCE + $\lambda \cdot \mathcal{L}_{\text{EAS}}$ where $\mathcal{L}_{\text{EAS}} = -\text{EAS}(X, Y)$
4. Hyperparameter search: $\lambda \in \{0.01, 0.1, 0.5, 1.0\}$
5. Evaluate on COCO and Flickr30k retrieval

*Training Configuration:*
- Architecture: ViT-B/32 image encoder, Transformer text encoder
- Batch size: 4096 (distributed across 8 GPUs)
- Training steps: 100K
- 5 random seeds per condition

*Statistical Analysis:*
- Two-sample t-test comparing R@1 between baseline and best treatment
- Success criterion: R@1 improvement > 1.0 percentage points with $p < 0.05$

### 3.6 Evaluation Metrics

| Metric | Description | Computation |
|--------|-------------|-------------|
| R@1 | Recall at rank 1 | Fraction of queries where correct match is top-ranked |
| R@5 | Recall at rank 5 | Fraction of queries where correct match is in top 5 |
| R@10 | Recall at rank 10 | Fraction of queries where correct match is in top 10 |
| EAS | Entropic Alignment Score | $1 - H(X|Y)/H(X)$ via InfoNCE estimation |
| CKA | Centered Kernel Alignment | Normalized HSIC between representation matrices |
| RSA | Representational Similarity Analysis | Spearman correlation of distance matrices |

### 3.7 Ablation Studies

1. **Ensemble Size:** Vary number of MINE networks (1, 3, 5, 10) to assess variance-bias tradeoff
2. **Embedding Dimensionality:** Test EAS reliability across 256-d, 512-d, 768-d, 1024-d embeddings
3. **Sample Size:** Evaluate EAS stability with 1K, 5K, 10K, 50K samples
4. **Estimator Architecture:** Compare 2-layer, 3-layer, 4-layer critic networks

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome (P1 - EAS-Retrieval Correlation):**
We expect to observe a strong positive correlation ($r > 0.7$) between EAS and cross-modal retrieval performance across the evaluated vision-language models. This would validate EAS as a meaningful measure of cross-modal alignment that captures information relevant to downstream task performance. Based on the theoretical grounding in PRH and Neural Thermodynamics, we anticipate that models exhibiting lower conditional entropy between modalities will consistently achieve higher retrieval accuracy.

**Secondary Outcome (P2 - Comparative Superiority):**
We predict EAS will demonstrate stronger correlation with retrieval performance than both CKA and RSA. While CKA and RSA capture geometric similarity between representation spaces, they do not directly measure the predictive relationship between modalities. EAS, by quantifying conditional entropy reduction, should capture alignment information that correlation-based metrics miss—particularly in cases where representations are aligned in information content but not in geometric structure.

**Tertiary Outcome (P3 - Training Objective):**
We expect that incorporating EAS as an auxiliary training objective will yield modest but significant improvements in cross-modal alignment (>1% R@1 improvement). This would demonstrate the practical utility of information-theoretic alignment beyond measurement, suggesting a new direction for multimodal training objectives.

**Potential Negative Results:**
If EAS fails to correlate with retrieval performance ($r \leq 0.5$), this would suggest that either (a) entropy estimation in high-dimensional spaces is insufficiently reliable, (b) the theoretical predictions of PRH do not translate to measurable conditional entropy reduction, or (c) retrieval performance depends on factors beyond information-theoretic alignment. Such negative results would still be valuable in refining our understanding of representation alignment.

### 4.2 Scientific Impact

**Bridging Theory and Practice:**
This research provides the first direct empirical test of PRH and Neural Thermodynamics predictions in the context of multimodal learning. By operationalizing "entropic convergence" as measurable conditional entropy reduction, we enable the theoretical framework to make falsifiable predictions about real-world models.

**Advancing Alignment Metrics:**
If successful, EAS would establish information-theoretic measurement as superior to correlation-based approaches for assessing cross-modal alignment. This could shift the field toward more principled evaluation of multimodal representations.

**Understanding Multimodal Learning:**
The relationship between EAS and model characteristics (scale, architecture, training data) will provide insights into what factors drive cross-modal alignment, informing future model design.

### 4.3 Practical Applications

**Model Selection and Evaluation:**
EAS provides a task-agnostic metric for comparing multimodal models, enabling practitioners to select models based on alignment quality without expensive downstream evaluation.

**Training Monitoring:**
EAS can serve as a training diagnostic, identifying when cross-modal alignment plateaus or degrades during training.

**Architecture Search:**
By providing a differentiable alignment objective, EAS enables gradient-based architecture search for multimodal models.

**Model Merging and Stitching:**
Understanding information-theoretic alignment facilitates techniques for combining or transferring components between multimodal models.

### 4.4 Broader Impact

This research contributes to the broader goal of understanding why and how neural networks learn similar representations. By providing tools to measure and optimize cross-modal alignment, we advance toward unified multimodal AI systems that more faithfully represent the shared structure of reality across sensory modalities.

The cross-disciplinary nature of this work—connecting information theory, statistical mechanics (via Neural Thermodynamics), and practical machine learning—exemplifies the productive exchange between theoretical and applied AI research. We anticipate this work will stimulate further investigation into the thermodynamic principles underlying representation learning, potentially leading to more principled and efficient training methods.

**Limitations and Ethical Considerations:**
The computational overhead of ensemble entropy estimation (~10% additional training time) may limit applicability in resource-constrained settings. Additionally, while EAS measures alignment, it does not assess the quality or fairness of the underlying representations—aligned representations could still encode biases present in training data. Future work should investigate the relationship between information-theoretic alignment and representation fairness.

---

**Word Count:** ~2,150 words