# Research Proposal: Causal Probing for Representational Alignment: Beyond Correlational Metrics

## 1. Introduction

### Background

The study of representational alignment—understanding when and how different intelligent systems develop similar internal representations—has emerged as a critical interdisciplinary research frontier spanning machine learning, neuroscience, and cognitive science. Both biological and artificial systems construct internal representations of the world that guide reasoning, decision-making, and communication. Comparing these representations offers profound insights into the computational principles underlying intelligence and provides practical tools for building AI systems that better align with human cognition.

Current approaches to measuring representational alignment predominantly rely on correlational metrics such as Representational Similarity Analysis (RSA), Centered Kernel Alignment (CKA), and linear predictivity measures. These methods compare the geometric structure of representational spaces across systems, quantifying similarity based on how stimuli cluster, distances between representations, or the extent to which one system's representations can linearly predict another's. While valuable, these approaches face a fundamental limitation: they capture *observational* similarity without revealing whether representations play *functionally equivalent computational roles* in downstream processing.

Recent literature highlights several critical challenges with existing metrics. Kapoor et al. (2025) demonstrated that significant representational alignment can emerge early in training, driven by shared input statistics and architectural biases rather than task-specific computational strategies. Wu et al. (2025) showed that different metrics vary substantially in their discriminative power across model families, raising questions about which aspects of alignment they truly capture. Furthermore, Ciernik et al. (2024) found that the consistency of representational similarity across datasets depends heavily on training objectives, suggesting that geometric alignment may not reflect stable computational properties.

These findings underscore a fundamental gap: two systems may exhibit high correlational similarity in their representations yet utilize these representations entirely differently for downstream tasks. This disconnect limits our ability to determine whether observed alignment indicates genuinely shared computational strategies or merely coincidental geometric similarity.

### Research Objectives

This proposal introduces **Causal Alignment Probing (CAP)**, a novel framework for measuring representational alignment through interventional rather than observational analysis. The core hypothesis is that *true computational alignment* should manifest not only in similar representational geometry but also in similar patterns of sensitivity to targeted interventions—if representations serve equivalent functional roles, perturbing them should produce comparable effects on downstream behavior.

The primary objectives of this research are:

1. To develop a principled methodology for assessing representational alignment based on causal influence profiles rather than geometric similarity alone.
2. To establish formal criteria distinguishing superficial geometric similarity from genuine computational alignment.
3. To identify which representational dimensions are functionally critical across different systems.
4. To provide actionable insights for increasing meaningful alignment between artificial and biological systems.

### Significance

This research addresses a central question of the Re-Align workshop: *To what extent does representational alignment indicate shared computational strategies among biological and artificial systems?* By shifting from correlational to causal metrics, CAP offers a principled answer to when geometric alignment reflects shared computation versus coincidental similarity. This has implications for developing more robust and generalizable alignment measures, understanding the computational basis of intelligence across systems, and designing interventions to systematically increase meaningful alignment.

## 2. Methodology

### 2.1 Conceptual Framework

The CAP framework is grounded in the principle that representations functionally critical to computation should, when perturbed, produce measurable and consistent effects on downstream behavior. We define **causal alignment** as the degree to which two systems exhibit similar behavioral sensitivity profiles in response to matched interventions on their representations.

Formally, let $\mathbf{r}_A(x) \in \mathbb{R}^{d_A}$ and $\mathbf{r}_B(x) \in \mathbb{R}^{d_B}$ denote the representations of stimulus $x$ in systems $A$ and $B$, respectively. Traditional metrics compute alignment as some function of the similarity between $\{\mathbf{r}_A(x_i)\}$ and $\{\mathbf{r}_B(x_i)\}$ across a stimulus set. In contrast, CAP measures alignment through the similarity of *intervention response functions*.

### 2.2 Intervention Design

We propose a systematic intervention taxonomy with three categories of perturbations applied to representations:

**Type 1: Ablation Interventions**
For each system, we identify principal components or learned feature directions and ablate specific dimensions:
$$\mathbf{r}'(x) = \mathbf{r}(x) - \sum_{j \in S} \langle \mathbf{r}(x), \mathbf{v}_j \rangle \mathbf{v}_j$$
where $S$ is the set of ablated dimensions and $\{\mathbf{v}_j\}$ are orthonormal basis vectors.

**Type 2: Rotation Interventions**
Apply random or structured rotations to subspaces of the representation:
$$\mathbf{r}'(x) = \mathbf{R}_\theta \mathbf{r}(x)$$
where $\mathbf{R}_\theta$ is a rotation matrix parameterized by angle $\theta$ in specified planes.

**Type 3: Noise Injection Interventions**
Add calibrated noise to specific representational dimensions:
$$\mathbf{r}'(x) = \mathbf{r}(x) + \sigma \cdot \mathbf{M} \odot \boldsymbol{\epsilon}$$
where $\boldsymbol{\epsilon} \sim \mathcal{N}(0, \mathbf{I})$, $\sigma$ controls noise magnitude, and $\mathbf{M}$ is a binary mask selecting targeted dimensions.

To enable cross-system comparison when $d_A \neq d_B$, we first establish a correspondence mapping using soft alignment techniques. Specifically, we compute an optimal transport mapping $\mathbf{T}^*$ between the two representation spaces that minimizes:
$$\mathbf{T}^* = \arg\min_{\mathbf{T}} \sum_{i,j} \mathbf{T}_{ij} \cdot c(\mathbf{r}_A(x_i), \mathbf{r}_B(x_j)) + \lambda \cdot H(\mathbf{T})$$
where $c(\cdot, \cdot)$ is a cost function (e.g., cosine distance) and $H(\mathbf{T})$ is an entropy regularizer.

### 2.3 Behavioral Sensitivity Mapping

For each intervention type $\tau$ and intensity level $\alpha$, we measure the behavioral impact through a sensitivity function. Let $f_A(\cdot)$ and $f_B(\cdot)$ denote the downstream task functions of systems $A$ and $B$. The behavioral sensitivity is:

$$\Delta_{A}^{(\tau, \alpha)}(x) = d\left(f_A(\mathbf{r}_A(x)), f_A(\mathbf{r}'_{A,\tau,\alpha}(x))\right)$$

where $d(\cdot, \cdot)$ is an appropriate distance metric for the task output (e.g., cross-entropy for classification, MSE for regression).

We construct a **Causal Influence Profile (CIP)** for each system as the vector:
$$\mathbf{CIP}_A = \left[\mathbb{E}_x[\Delta_A^{(\tau_1, \alpha_1)}(x)], \ldots, \mathbb{E}_x[\Delta_A^{(\tau_n, \alpha_m)}(x)]\right]$$

This profile captures how the system's behavior depends on different aspects of its representations across intervention types and intensities.

### 2.4 Causal Alignment Score

The **Causal Alignment Score (CAS)** between systems $A$ and $B$ is defined as the similarity between their causal influence profiles:

$$\text{CAS}(A, B) = \frac{\mathbf{CIP}_A \cdot \mathbf{CIP}_B}{\|\mathbf{CIP}_A\| \cdot \|\mathbf{CIP}_B\|}$$

To capture finer-grained alignment, we also compute **dimension-specific causal alignment**. For each representational dimension $j$ (after alignment via optimal transport), we compute:

$$\text{CAS}_j(A, B) = \text{corr}\left(\Delta_{A,j}^{(\cdot)}(x), \Delta_{B,j}^{(\cdot)}(x)\right)$$

across all interventions targeting dimension $j$. This reveals which specific representational dimensions exhibit functional correspondence.

### 2.5 Experimental Design

**Datasets and Stimuli:**
We will use three experimental domains:
1. **Vision**: ImageNet validation set (50K images) and the Natural Scenes Dataset (NSD) with human fMRI responses
2. **Language**: The BLiMP benchmark and GPT-generated sentence pairs with controlled semantic variations
3. **Cross-modal**: COCO captions with matched image-text pairs

**Systems Under Comparison:**
- *Artificial-Artificial*: Vision transformers (ViT, DeiT, CLIP-ViT) and CNNs (ResNet, EfficientNet) at matched layers
- *Artificial-Biological*: Deep networks compared against human fMRI responses from NSD (visual cortex ROIs: V1-V4, LOC, PPA, FFA)
- *Language Models*: GPT-2, LLaMA, and BERT representations compared to human behavioral similarity judgments

**Baseline Metrics:**
We compare CAP against established correlational metrics:
- Representational Similarity Analysis (RSA)
- Centered Kernel Alignment (CKA)
- Linear predictivity (ridge regression $R^2$)
- Procrustes distance

**Evaluation Protocol:**

*Experiment 1: Discriminative Power*
Following Wu et al. (2025), we assess whether CAS better discriminates between model families than correlational metrics. We compute within-family versus between-family alignment scores and measure discriminability via ROC-AUC.

*Experiment 2: Predictive Validity*
We test whether CAS predicts transfer learning performance better than correlational metrics. If causal alignment reflects shared computation, high CAS should predict successful knowledge transfer between systems.

*Experiment 3: Robustness Analysis*
We evaluate CAS stability across:
- Distribution shifts (ImageNet-C corruptions)
- Stimulus set variations (random subsampling)
- Intervention parameter variations (sensitivity analysis)

*Experiment 4: Biological Correspondence*
We measure CAS between neural network layers and human visual cortex regions, testing whether causal alignment reveals hierarchical correspondence more accurately than correlational metrics.

**Statistical Analysis:**
All comparisons will use permutation tests (10,000 iterations) to establish significance. Effect sizes will be reported via Cohen's d. Multiple comparison corrections (Bonferroni) will be applied across analyses.

### 2.6 Algorithmic Implementation

```
Algorithm: Causal Alignment Probing (CAP)
Input: Systems A, B; Stimulus set X; Intervention types T; Task functions f_A, f_B
Output: Causal Alignment Score CAS(A, B)

1. Extract representations: R_A = {r_A(x) : x ∈ X}, R_B = {r_B(x) : x ∈ X}
2. Compute alignment mapping T* via optimal transport
3. For each intervention type τ ∈ T:
   For each intensity α ∈ {0.1, 0.25, 0.5, 0.75, 1.0}:
     For each stimulus x ∈ X:
       a. Apply intervention: r'_A = Intervene(r_A(x), τ, α)
       b. Apply matched intervention: r'_B = Intervene(r_B(x), τ, α, T*)
       c. Compute Δ_A(x) = d(f_A(r_A(x)), f_A(r'_A))
       d. Compute Δ_B(x) = d(f_B(r_B(x)), f_B(r'_B))
4. Aggregate into CIP_A, CIP_B
5. Compute CAS = cosine_similarity(CIP_A, CIP_B)
Return CAS
```

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Methodological Contribution**: A validated framework (CAP) for measuring representational alignment through causal analysis, with open-source implementation and benchmarks.

2. **Empirical Findings**: We anticipate discovering that:
   - Correlational and causal alignment often diverge, with some system pairs showing high geometric similarity but low functional correspondence
   - Causal alignment emerges later in training than geometric alignment, reflecting task-specific computational adaptation
   - Specific representational dimensions consistently show high causal alignment across system pairs, suggesting universal computational features

3. **Theoretical Insights**: A taxonomy of alignment types—distinguishing "geometric alignment" (similar structure) from "causal alignment" (similar function)—with formal criteria for each.

4. **Practical Tools**: Actionable recommendations for increasing meaningful alignment in AI systems, based on identifying which representational properties are causally relevant to desired behaviors.

### Broader Impact

This research directly addresses core questions of the Re-Align workshop. By providing metrics that distinguish superficial from functional alignment, CAP advances our understanding of when shared representations indicate shared computational strategies. This has implications for:

- **Neuroscience**: More principled comparisons between artificial and biological visual systems
- **AI Safety**: Better metrics for ensuring AI systems align with human reasoning processes, not just outputs
- **Transfer Learning**: Predicting which representations will support effective knowledge transfer

The interventional approach also provides a bridge between representational and behavioral alignment, offering insights into how geometric alignment relates to value alignment and beyond. By participating in the workshop hackathon, we will contribute CAP as a tool for the community, facilitating comparative analyses and promoting reproducibility in alignment research.

### Limitations and Future Directions

CAP requires access to intermediate representations and the ability to intervene on them, limiting applicability to black-box systems. Future work will explore approximation methods using input-space perturbations that induce targeted representational changes. Additionally, extending CAP to temporal dynamics—measuring alignment in sequential processing—represents a promising direction for understanding computational correspondence in recurrent and autoregressive systems.