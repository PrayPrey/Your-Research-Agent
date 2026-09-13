# Research Proposal: Dual-Plasticity Alignment Networks: Steering Representational Alignment Through Dynamic Sparse Training

## 1. Introduction

### 1.1 Background

Both natural and artificial intelligent systems construct internal representations of the world that enable reasoning, decision-making, and communication. A fundamental question spanning machine learning, neuroscience, and cognitive science concerns how these representations can be meaningfully compared and aligned across different systems. Despite extensive research, the field lacks principled methods for systematically controlling representational alignment—the degree to which different systems encode similar information in similar ways.

Recent advances have established reliable metrics for measuring representational similarity, with Centered Kernel Alignment (CKA) emerging as a prominent tool for comparing neural network representations. Murphy et al. (2024) demonstrated that debiased CKA provides reliable alignment measurement even in low-data regimes, while Muttenthaler et al. (2022) showed that training objective modifications can improve alignment between artificial neural networks and human similarity judgments. However, these approaches primarily operate through loss function modifications, offering limited controllability over the alignment process.

Simultaneously, dynamic sparse training has emerged as a powerful paradigm for reshaping neural network topology during training. Methods such as RigL (Evci et al., 2019) and Top-KAST (Jayakumar et al., 2021) demonstrate that networks can maintain or improve task performance while dynamically modifying their connectivity structure. These techniques operate through iterative grow-prune cycles that selectively strengthen important connections while removing less useful ones. Crucially, the importance scoring mechanisms in these frameworks are modular and can be customized—yet this flexibility has never been leveraged to target representational alignment.

### 1.2 Research Gap

The intersection of dynamic sparse training and representational alignment remains unexplored. Current alignment improvement methods rely on auxiliary loss terms that provide indirect pressure toward alignment but offer no structural intervention mechanism. Researchers lack tools to systematically increase or decrease alignment between systems, limiting our ability to study the causal relationship between network structure and representational similarity. This gap is particularly significant given the Re-Align workshop's central question: "How can we systematically increase (or decrease) representational alignment among biological and artificial systems?"

### 1.3 Research Objectives

This research proposes **Dual-Plasticity Alignment Networks (DPAN)**, a novel framework that integrates alignment signals into dynamic sparse training decisions. Our primary objectives are:

1. **Demonstrate existence**: Establish that alignment-weighted dynamic sparse training produces measurable alignment improvements (>10% debiased CKA increase) compared to standard training.

2. **Validate mechanism**: Confirm that the proposed four-step causal chain (alignment computation → importance scoring → structural modification → alignment improvement) operates as designed.

3. **Enable controllability**: Provide a tunable parameter α that enables systematic exploration of the task-alignment trade-off, producing a monotonic Pareto front.

### 1.4 Significance

This research addresses multiple open questions in representational alignment:

- **Structural intervention**: DPAN provides the first framework for controlling alignment through network topology rather than loss functions, offering a fundamentally new intervention mechanism.

- **Controllability**: The α parameter enables researchers to systematically dial alignment up or down, facilitating studies of alignment's effects on downstream behaviors.

- **Mechanistic insight**: By examining which connections are strengthened versus pruned, DPAN provides interpretable evidence about which computational pathways promote alignment.

- **Practical applications**: Controllable alignment has implications for building AI systems that better match human cognition, with potential benefits for human-AI interaction, interpretability, and value alignment.

## 2. Methodology

### 2.1 Framework Overview

Dual-Plasticity Alignment Networks operate through iterative cycles that reshape network topology based on both task performance and alignment with target representations. The framework integrates with existing dynamic sparse training methods by introducing alignment-aware importance scoring.

### 2.2 Alignment Signal Computation

Every $K$ epochs, we compute layer-wise debiased CKA between model representations and target representations. Following Murphy et al. (2024), we use mean-centered representations to eliminate bias:

$$\text{CKA}_{\text{debiased}}(X, Y) = \frac{\text{HSIC}(\tilde{X}, \tilde{Y})}{\sqrt{\text{HSIC}(\tilde{X}, \tilde{X}) \cdot \text{HSIC}(\tilde{Y}, \tilde{Y})}}$$

where $\tilde{X} = X - \bar{X}$ and $\tilde{Y} = Y - \bar{Y}$ are mean-centered representations, and HSIC denotes the Hilbert-Schmidt Independence Criterion:

$$\text{HSIC}(X, Y) = \frac{1}{(n-1)^2} \text{tr}(K_X H K_Y H)$$

with $K_X$, $K_Y$ being kernel matrices and $H = I - \frac{1}{n}\mathbf{1}\mathbf{1}^T$ the centering matrix.

For target representations, we use human similarity judgments from the THINGS dataset (odd-one-out triplet comparisons) converted to representational dissimilarity matrices, or fMRI responses from the Natural Scenes Dataset (NSD).

### 2.3 Alignment-Weighted Importance Scoring

For each connection $w_{ij}$ between neurons $i$ and $j$, we compute an importance score combining task relevance and alignment contribution:

$$S_{ij} = \alpha \cdot T_{ij} + (1 - \alpha) \cdot A_{ij}$$

where:
- $\alpha \in [0, 1]$ is the tunable task-alignment trade-off parameter
- $T_{ij}$ is the task importance, computed as the gradient magnitude: $T_{ij} = |w_{ij} \cdot \nabla_{w_{ij}} \mathcal{L}_{\text{task}}|$
- $A_{ij}$ is the alignment correlation, measuring how much the connection contributes to alignment

The alignment correlation $A_{ij}$ is computed by measuring the correlation between connection activation patterns and alignment-promoting directions:

$$A_{ij} = \text{corr}\left(a_i \cdot a_j, \frac{\partial \text{CKA}_{\text{debiased}}}{\partial h_l}\right)$$

where $a_i$, $a_j$ are neuron activations and $h_l$ is the layer representation.

### 2.4 Grow-Prune Operations

**Pruning**: At each restructuring cycle (every $K$ epochs), we remove the bottom $p\%$ of connections ranked by importance score $S_{ij}$:

$$\mathcal{W}_{\text{prune}} = \{w_{ij} : S_{ij} < \text{percentile}(S, p)\}$$

**Growth**: We add new connections between neuron pairs with high alignment potential. Growth candidates are scored by:

$$G_{ij} = (1 - \alpha) \cdot \hat{A}_{ij} + \alpha \cdot \hat{T}_{ij}$$

where $\hat{A}_{ij}$ and $\hat{T}_{ij}$ are estimated importance scores for potential connections, computed using gradient-based estimation following Top-KAST:

$$\hat{T}_{ij} = \left|\frac{\partial \mathcal{L}_{\text{task}}}{\partial w_{ij}}\right|_{w_{ij}=0}$$

The top $g\%$ of candidate connections are added, where typically $g \leq p$ to maintain or reduce sparsity.

### 2.5 Complete Algorithm

**Algorithm: Dual-Plasticity Alignment Network Training**

```
Input: Model M, Dataset D, Target representations R_target, 
       α (trade-off), K (alignment frequency), p (prune rate), g (grow rate)
Output: Trained model with alignment-shaped topology

1. Initialize model M with random sparse connectivity
2. For epoch e = 1 to E:
   a. Standard training step: update weights via SGD on task loss
   b. If e mod K == 0:  # Restructuring cycle
      i.   Compute layer-wise debiased CKA with R_target
      ii.  For each connection w_ij:
           - Compute task importance T_ij
           - Compute alignment correlation A_ij
           - Compute combined score S_ij = α·T_ij + (1-α)·A_ij
      iii. Prune: Remove bottom p% connections by S_ij
      iv.  Score growth candidates G_ij for zero connections
      v.   Grow: Add top g% candidates by G_ij
      vi.  Re-initialize new connection weights (small random values)
3. Return trained model M
```

### 2.6 Experimental Design

#### 2.6.1 Datasets and Models

**Development Phase:**
- Model: ResNet-18
- Dataset: CIFAR-10 (50K training, 10K test images)
- Target representations: THINGS human similarity judgments (subset of 100 categories overlapping with CIFAR)

**Scaling Phase:**
- Model: ResNet-50
- Dataset: ImageNet-1K (1.2M training, 50K validation images)
- Target representations: THINGS full dataset (1,854 object concepts) and NSD fMRI data (8 subjects, ~10K images each)

#### 2.6.2 Baselines

1. **Standard Training**: Dense ResNet trained with cross-entropy loss only
2. **Standard Sparse Training**: RigL/Top-KAST with task-only importance scoring (α=1.0)
3. **Loss-Based Alignment**: Muttenthaler et al. (2022) approach using auxiliary alignment loss
4. **Random Sparse**: Random grow-prune decisions (ablation control)

#### 2.6.3 Hyperparameter Settings

| Parameter | Development | Scaling |
|-----------|-------------|---------|
| α (trade-off) | {0.0, 0.25, 0.5, 0.75, 1.0} | {0.0, 0.25, 0.5, 0.75, 1.0} |
| K (alignment frequency) | {5, 10, 20} epochs | {5, 10, 20} epochs |
| p (prune rate) | {10%, 20%, 30%} | 20% |
| g (grow rate) | {10%, 20%, 30%} | 20% |
| Sparsity level | 80%, 90% | 80%, 90% |
| Training epochs | 200 | 90 |
| Batch size | 128 | 256 |
| Learning rate | 0.1 (cosine decay) | 0.1 (cosine decay) |

#### 2.6.4 Evaluation Metrics

**Primary Metrics:**
- **Alignment (CKA)**: Debiased CKA between model representations and target representations, computed at multiple layers
- **Task Accuracy**: Top-1 classification accuracy on validation set

**Secondary Metrics:**
- **Controllability**: Correlation between α and alignment (expected >0.8)
- **Pareto Efficiency**: Area under the task-alignment Pareto front
- **Mechanism Validation**: Statistical difference in alignment correlation between pruned vs. retained connections

#### 2.6.5 Statistical Analysis

- **Sample size**: n=20 independent runs per condition (different random seeds)
- **Primary test**: Paired t-test comparing DPAN (α=0.5) vs. standard training
- **Effect size**: Cohen's d with 95% confidence intervals
- **Significance threshold**: p < 0.05 (one-tailed for improvement hypothesis)
- **Multiple comparison correction**: Bonferroni correction for secondary predictions

#### 2.6.6 Ablation Studies

1. **Importance scoring ablation**: Compare full scoring vs. task-only vs. alignment-only
2. **Frequency ablation**: Vary K to assess alignment computation frequency effects
3. **Debiased vs. biased CKA**: Verify necessity of debiasing
4. **Layer-wise analysis**: Examine which layers show strongest alignment effects

### 2.7 Falsification Criteria

The hypothesis will be rejected if any of the following occur:
1. Alignment improvement ≤2% (within noise range)
2. No statistical difference in alignment correlation between pruned and retained connections (p > 0.05)
3. Non-monotonic relationship between α and alignment (correlation < 0.5)
4. Task accuracy drops >5% below standard training baseline

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1)**: We predict that DPAN with α=0.5 will achieve >10% improvement in debiased CKA compared to standard training, while maintaining task accuracy within 2% of baseline. This prediction is grounded in evidence that (a) loss-based alignment methods achieve 5-15% improvements (Muttenthaler et al., 2022), and (b) structural interventions provide more direct control than loss modifications.

**Secondary Outcomes:**
- **P2 (Controllability)**: Varying α from 0 to 1 will produce a monotonic Pareto front, with correlation >0.8 between α and alignment metrics.
- **P3 (Mechanism Validation)**: Pruned connections will show statistically lower alignment correlation than retained connections (p < 0.01), confirming the causal mechanism.

### 3.2 Scientific Impact

**Advancing Alignment Measurement**: This work will provide empirical evidence about which network structures promote alignment, informing future metric development. The layer-wise analysis will reveal whether alignment is localized or distributed across network depth.

**Understanding Computational Strategies**: By examining which connections are alignment-promoting, we gain insight into whether aligned representations reflect shared computational strategies between biological and artificial systems.

**Methodological Contribution**: DPAN establishes a new paradigm for alignment research—structural intervention—complementing existing loss-based approaches. The framework is modular and can incorporate future alignment metrics as they are developed.

### 3.3 Practical Applications

**Human-AI Interaction**: Systems with controllable alignment could be tuned to match human expectations more closely, potentially improving usability and trust.

**Interpretability**: The explicit connection between network structure and alignment provides a new avenue for understanding what neural networks learn and why.

**Value Alignment**: While representational alignment is distinct from value alignment, understanding how to control the former may inform approaches to the latter.

### 3.4 Limitations and Future Directions

**Current Limitations:**
- Requires pre-defined target representations (not applicable to unsupervised settings)
- Computational overhead (~10-15% additional training time)
- Validated only on vision models; extension to language models requires different alignment metrics

**Future Directions:**
- Extension to transformer architectures and language models
- Self-supervised alignment targets derived from behavioral data
- Real-time adaptation mechanisms for online alignment adjustment
- Investigation of alignment's causal effects on downstream behavioral alignment

### 3.5 Broader Implications

This research directly addresses the Re-Align workshop's central question about systematic intervention on alignment. By providing the first structural approach to controllable alignment, DPAN opens new research directions for understanding when and why intelligent systems learn aligned representations. The ability to dial alignment up or down enables controlled experiments on alignment's downstream effects—on behavioral alignment, generalization, and potentially value alignment—advancing our understanding of the relationship between representational similarity and functional similarity across intelligent systems.

The framework also has implications for the positive and negative consequences of alignment modification. By enabling systematic study of alignment's effects, researchers can better understand potential risks of misaligned AI systems and develop principled approaches to building systems that appropriately match human cognition where beneficial while maintaining distinct capabilities where advantageous.