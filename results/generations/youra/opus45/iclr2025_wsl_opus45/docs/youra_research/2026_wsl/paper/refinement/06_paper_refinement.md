# LoRA Adapter Geometric Signatures for Task Similarity Detection

## Abstract

This work investigates whether LoRA adapter geometry encodes task similarity by analyzing the column spaces of learned B matrices under controlled experimental conditions. A total of 40 adapters were trained on 8 tasks spanning reasoning and natural language understanding categories, using identical base model (TinyLlama-1.1B-Chat-v1.0), hyperparameters, and training procedures. The primary finding is that adapters trained on semantically similar tasks exhibit smaller pairwise Grassmann distances than adapters trained on dissimilar tasks (Cohen's d = 0.765, p = 8.63 × 10⁻²⁸). This geometric similarity correlates with FLAN task taxonomy (Spearman ρ = 0.389, p = 1.29 × 10⁻²⁹). Contrary to initial expectations, the clustering signal is distributed uniformly across all transformer layer types (attention and MLP) rather than concentrated in specific layers. A control analysis reveals that within-task variance across random seeds is substantial (ratio = 0.89 relative to within-category variance), indicating that training stochasticity contributes meaningfully to adapter geometry. These findings establish that task-category clustering exists in LoRA adapter weight space under controlled conditions, though practical utility for fine-grained task discrimination may be limited by training variance.

## 1. Introduction

As parameter-efficient fine-tuning methods proliferate, practitioners accumulate collections of LoRA adapters without systematic methods for understanding relationships between them. When selecting an adapter for a new task, current practice relies on metadata tags and manual curation rather than analysis of the adapters themselves. This work investigates whether LoRA adapter weight spaces contain geometric structure that reflects task similarity.

LoRA (Low-Rank Adaptation) constrains weight updates to a low-rank subspace via the decomposition ΔW = BA, where B ∈ ℝ^(d×r) and A ∈ ℝ^(r×k). The column space of the B matrix defines the output transformation subspace. If semantically similar tasks require similar functional transformations, their B matrices may span similar subspaces. This hypothesis has not been rigorously validated under controlled experimental conditions.

Previous attempts to analyze LoRA adapter geometry used public adapter collections with uncontrolled provenance—different base model checkpoints, quantization levels, LoRA configurations, and training hyperparameters. These uncontrolled variables confound any geometric signal with experimental artifacts. One prior experiment using 8 public HuggingFace adapters observed a large effect size (Cohen's d = 0.91) but insufficient statistical power (p = 0.127) due to the small sample size.

This work addresses these limitations by training adapters in-house under controlled conditions. A single base model checkpoint is fine-tuned with identical LoRA configuration and training hyperparameters across all tasks. The only variable that changes is the training task. This approach, adapted from the Model Zoo methodology for full neural network populations, isolates task-specific geometric structure from experimental confounds.

The contributions of this work are:

1. An existence proof demonstrating that within-category LoRA adapters exhibit smaller Grassmann distances than between-category adapters under controlled conditions (Cohen's d = 0.765, p = 8.63 × 10⁻²⁸).

2. Validation that geometric similarity correlates with semantic similarity as defined by FLAN task taxonomy (Spearman ρ = 0.389, p = 1.29 × 10⁻²⁹).

3. A negative finding that task-category clustering is distributed uniformly across all transformer layer types, with no layer type exceeding Cohen's d = 0.8.

4. Identification of a limitation: the P3 control analysis shows within-task variance ratio = 0.89, indicating that training stochasticity substantially affects adapter geometry.

This work establishes that geometric structure exists in LoRA adapter weight space but does not claim that Grassmann distance outperforms existing task similarity methods. Comparison to baseline methods such as task embedding similarity is deferred to future work.

## 2. Related Work

### Parameter-Efficient Fine-Tuning

Low-Rank Adaptation (LoRA) introduced the decomposition ΔW = BA to constrain weight updates to a low-rank subspace. Subsequent work has focused on improving LoRA training: DoRA decomposes weights into magnitude and direction components; QLoRA enables efficient fine-tuning of quantized models; AdaLoRA adaptively allocates rank across layers. StelLA employs Stiefel manifold geometry to optimize LoRA training. These methods leverage geometric structure to improve training but do not analyze trained adapters for task similarity.

### Weight-Space Learning

Weight-space learning treats neural network parameters as data points for downstream analysis. The Model Zoo framework introduced controlled populations of neural networks with verified provenance, demonstrating that weight-space representations enable model property prediction, generation, and analysis. This methodology has focused primarily on full neural network models rather than parameter-efficient adapters. The present work adapts this controlled-generation approach specifically for LoRA adapters.

### Geometric Analysis of Representations

Grassmann manifolds provide a natural framework for comparing linear subspaces. Principal angles between subspaces, computed via SVD of inner products between orthonormal bases, yield the Grassmann geodesic distance. This metric has been applied to subspace clustering, domain adaptation, and representation similarity analysis. CKA and SVCCA measure representation similarity across layers and models by comparing activations rather than weights. For LoRA adapters, weight-space analysis requires no inference: geometric signatures can be computed directly from adapter parameters.

FL-TAC clusters similar adapters in federated learning settings, though without controlled provenance verification. The present work provides controlled validation where only the training task varies.

## 3. Method

### Controlled Adapter Generation

Adapters are generated in-house with verified provenance. A single base model checkpoint (TinyLlama-1.1B-Chat-v1.0) is fine-tuned with identical LoRA configuration across all tasks. The LoRA configuration uses rank r = 32, alpha = 64, dropout = 0.05, targeting all attention and MLP projections (q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj).

All adapters are trained with identical hyperparameters: learning rate 2 × 10⁻⁴, batch size 8, 3 epochs, AdamW optimizer, warmup ratio 0.1, and maximum sequence length 512. For each task, 5 adapters are trained with different random seeds (42, 43, 44, 45, 46) to assess within-task variance.

### Grassmann Distance Computation

Given two B matrices B₁, B₂ ∈ ℝ^(d×r), the Grassmann distance is computed as follows:

1. Compute orthonormal bases for the column spaces via SVD
2. Compute principal angles θ₁, ..., θᵣ between the subspaces
3. Grassmann distance: d_G(B₁, B₂) = √(Σⱼ θⱼ²)

This distance is zero when subspaces are identical and maximal when subspaces are orthogonal.

### Statistical Analysis

The main hypothesis is tested using the Mann-Whitney U test comparing within-category vs. between-category distance distributions. Cohen's d is reported as effect size. Spearman rank correlation validates the relationship between geometric distance and semantic similarity. Bootstrap confidence intervals (1000 iterations) are computed for all primary metrics.

## 4. Experimental Setup

### Tasks and Categories

Eight tasks spanning two FLAN categories were selected:

| Category | Tasks |
|----------|-------|
| Reasoning | gsm8k, arc, logiqa, strategyqa |
| NLU | mnli, qqp, sst2, mrpc |

### Adapter Generation

A total of 40 adapters were trained (8 tasks × 5 seeds) on TinyLlama-1.1B-Chat-v1.0. Training was conducted on NVIDIA H100 NVL, taking approximately 2 hours 14 minutes total.

### Evaluation Protocol

For each adapter pair, B matrices were extracted for all 154 layer-module combinations (22 layers × 7 module types). Grassmann distance was computed per layer and aggregated using mean pooling across layers.

### Success Criteria

- RQ1 (Existence): p < 0.05 and Cohen's d > 0.5
- RQ2 (Mechanism): Spearman ρ > 0.3 with p < 0.05
- RQ3 (Layer Analysis): At least one layer type with Cohen's d > 0.8
- P3 (Control): Within-task variance ratio < 0.5

## 5. Results

### RQ1: Existence of Task-Category Clustering

| Metric | Value |
|--------|-------|
| Within-category mean distance | 7.606 |
| Between-category mean distance | 7.795 |
| Mean difference | 0.190 |
| Cohen's d | 0.765 |
| 95% CI for Cohen's d | [0.68, 0.85] |
| p-value (Mann-Whitney U) | 8.63 × 10⁻²⁸ |
| Within-category pairs | 380 |
| Between-category pairs | 400 |

The within-category Grassmann distances are smaller than between-category distances. The effect size (Cohen's d = 0.765) exceeds the threshold of 0.5. The 95% confidence interval for the mean difference [0.155, 0.226] does not include zero.

![Distance Heatmap](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_wsl_opus45_3/docs/youra_research/20260413_wsl/paper/figures/distance_heatmap.png)
*Figure 1: Pairwise Grassmann distance matrix between all 40 LoRA adapters.*

### RQ2: Correlation with Semantic Similarity

| Metric | Value |
|--------|-------|
| Spearman ρ | 0.389 |
| 95% CI | [0.328, 0.450] |
| p-value | 1.29 × 10⁻²⁹ |
| N pairs | 780 |

The positive correlation indicates that adapters for tasks in the same FLAN category have smaller Grassmann distances than adapters for tasks in different categories. The 95% confidence interval excludes zero.

![Scatter Regression](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_wsl_opus45_3/docs/youra_research/20260413_wsl/paper/figures/scatter_regression.png)
*Figure 2: Grassmann distance vs. FLAN taxonomy distance showing positive correlation (ρ = 0.389).*

### RQ3: Layer-Type Analysis

| Layer Type | Cohen's d | 95% CI | p-value |
|------------|-----------|--------|---------|
| down_proj | 0.783 | [0.699, 0.869] | 5.89 × 10⁻²⁶ |
| o_proj | 0.772 | [0.686, 0.862] | 2.52 × 10⁻²⁵ |
| v_proj | 0.760 | [0.673, 0.851] | 1.23 × 10⁻²⁴ |
| k_proj | 0.759 | [0.660, 0.855] | 1.44 × 10⁻²⁴ |
| up_proj | 0.756 | [0.671, 0.844] | 1.95 × 10⁻²⁴ |
| gate_proj | 0.749 | [0.664, 0.836] | 4.96 × 10⁻²⁴ |
| q_proj | 0.745 | [0.649, 0.842] | 8.27 × 10⁻²⁴ |

No layer type exceeds Cohen's d = 0.8. The range across layer types is narrow (0.745 to 0.783). The mean Cohen's d for attention layers (0.759) and MLP layers (0.763) are not significantly different (Mann-Whitney p = 1.0).

![Cohen's d by Layer Type](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_wsl_opus45_3/docs/youra_research/20260413_wsl/paper/figures/cohens_d_by_layer_type.png)
*Figure 3: Cohen's d by layer type showing uniform clustering strength across all layer types.*

### P3 Control: Training Stochasticity

| Metric | Value |
|--------|-------|
| Within-task mean distance | 6.931 |
| Within-cluster mean distance | 7.786 |
| Ratio | 0.890 |
| Threshold | < 0.5 |
| Status | FAIL |

The P3 control criterion is not satisfied. The within-task variance (across different random seeds for the same task) is 89% of the within-cluster variance (across different tasks in the same category). This indicates that training stochasticity contributes substantially to adapter geometry.

### Summary of Results

| Research Question | Criterion | Result | Status |
|-------------------|-----------|--------|--------|
| RQ1: Existence | Cohen's d > 0.5 | d = 0.765 | PASS |
| RQ2: Mechanism | Spearman ρ > 0.3 | ρ = 0.389 | PASS |
| RQ3: Layer Analysis | Cohen's d > 0.8 for any layer | d = 0.783 (max) | FAIL |
| P3: Control | Ratio < 0.5 | Ratio = 0.89 | FAIL |

## 6. Discussion

### Summary of Findings

The existence proof (RQ1) demonstrates that task-category clustering in LoRA adapter geometry is statistically detectable under controlled conditions (Cohen's d = 0.765, p < 10⁻²⁷). The correlation with FLAN taxonomy (RQ2, ρ = 0.389) indicates that the geometric structure reflects semantic relationships between tasks.

The layer-type analysis yielded a negative result: all seven layer types show similar clustering strength (Cohen's d range 0.745–0.783), and no layer type exceeds the 0.8 threshold. Task-relevant geometric information appears to be distributed uniformly across the transformer architecture rather than concentrated in specific layers.

### Limitations

**Training stochasticity.** The P3 control failure (ratio = 0.89) indicates that within-task variance across random seeds is comparable to within-category variance across tasks. This limits the practical utility of geometric signatures for fine-grained task discrimination. The geometric signatures may reflect category-level structure rather than precise task-level fingerprints.

**Single model family.** Experiments use only TinyLlama-1.1B. Generalization to other architectures and larger model scales is not established.

**Coarse taxonomy.** The binary FLAN taxonomy (same category vs. different category) provides only coarse similarity labels. The moderate correlation (ρ = 0.389) may reflect this limitation.

**No baseline comparison.** This work validates the existence of geometric structure but does not compare Grassmann distance to alternative task similarity methods such as task embedding similarity or activation-based metrics.

### Scope Clarification

The findings establish that geometric structure exists and correlates with task taxonomy. The results do not demonstrate that Grassmann distance is superior to or competitive with existing task similarity methods. Such comparison requires future work.

## 7. Conclusion

This work demonstrates that LoRA adapter B matrix column spaces encode task-specific geometric signatures under controlled experimental conditions. Adapters trained on semantically similar tasks exhibit smaller Grassmann distances (Cohen's d = 0.765, p = 8.63 × 10⁻²⁸), and this geometric similarity correlates with FLAN task taxonomy (Spearman ρ = 0.389, p = 1.29 × 10⁻²⁹). The clustering signal is distributed uniformly across all transformer layer types.

A significant limitation is that training stochasticity contributes substantially to adapter geometry (within-task variance ratio = 0.89), which may constrain practical applications requiring fine-grained task discrimination.

Future work should investigate whether longer training reduces within-task variance, replicate findings on larger models, and compare Grassmann distance to alternative task similarity methods.

## References

Dettmers, T., Pagnoni, A., Holtzman, A., and Zettlemoyer, L. QLoRA: Efficient Finetuning of Quantized LLMs. In NeurIPS, 2023.

Edelman, A., Arias, T. A., and Smith, S. T. The Geometry of Algorithms with Orthogonality Constraints. SIAM J. Matrix Anal. Appl., 20(2):303–353, 1998.

Hu, J. E., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., and Chen, W. LoRA: Low-Rank Adaptation of Large Language Models. In ICLR, 2021.

Kornblith, S., Norouzi, M., Lee, H., and Hinton, G. E. Similarity of Neural Network Representations Revisited. In ICML, 2019.

Li, Z., Sajadmanesh, S., Li, J., and Lyu, L. StelLA: Subspace Learning in Low-rank Adaptation using Stiefel Manifold. arXiv:2510.01938, 2025.

Liu, S.-Y., Wang, C.-Y., Yin, H., Molchanov, P., Wang, Y.-C. F., Cheng, K.-T., and Chen, M.-H. DoRA: Weight-Decomposed Low-Rank Adaptation. In ICML, 2024.

Raghu, M., Gilmer, J., Yosinski, J., and Sohl-Dickstein, J. SVCCA: Singular Vector Canonical Correlation Analysis for Deep Learning Dynamics and Interpretability. In NeurIPS, 2017.

Schürholt, K., Taskiran, D., Knyazev, B., Giró-i-Nieto, X., and Borth, D. Model Zoos: A Dataset of Diverse Populations of Neural Network Models. In NeurIPS, 2022.

Zhang, Q., Chen, M., Bukharin, A., He, P., Cheng, Y., Chen, W., and Zhao, T. AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning. In ICLR, 2023.
