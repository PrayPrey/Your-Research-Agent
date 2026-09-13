# Research Proposal: Cluster-Aware Variational Disagreement (CAVD): Discovering Latent Value Systems from Preference Data via Voting-Based Reward Aggregation

## 1. Introduction

### 1.1 Background

The alignment of artificial intelligence systems with human values has emerged as one of the most critical challenges in contemporary machine learning research. As large language models (LLMs) become increasingly integrated into high-stakes decision-making contexts—from content moderation to healthcare recommendations—ensuring these systems reflect the diverse spectrum of human values becomes paramount. However, current alignment methodologies, predominantly Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO), operate under a fundamental assumption that proves increasingly problematic: they treat annotator disagreement as noise to be eliminated rather than as a valuable signal encoding genuine value diversity.

This reductionist approach creates AI systems that implicitly favor majority perspectives while obscuring the value trade-offs inherent in their decisions. The consequences are twofold: marginalized viewpoints are systematically underrepresented, and the decision-making process lacks the transparency required for meaningful governance oversight. This gap becomes particularly acute as regulatory frameworks such as the EU AI Act mandate governance-auditable AI decisions, requiring organizations to demonstrate how their systems handle value conflicts and whose perspectives they prioritize.

Recent advances in pluralistic alignment have begun addressing these limitations. Variational Preference Learning (VPL) employs variational autoencoders to model user-specific preferences, while Multi-Objective Direct Preference Optimization (MODPO) extends DPO to handle multiple reward objectives simultaneously. ArmoRM demonstrates that multi-head reward architectures can achieve state-of-the-art performance while maintaining interpretability. However, these approaches share a critical limitation: they require explicit annotator labels or metadata to function effectively, creating substantial barriers to scalability and deployment.

### 1.2 Research Objectives

This research proposes Cluster-Aware Variational Disagreement (CAVD), a novel framework that addresses these limitations through three interconnected innovations:

1. **Unsupervised Value Discovery**: Develop a variational inference mechanism capable of discovering latent value clusters from standard pairwise preference data without requiring explicit annotator labels or demographic metadata.

2. **Transparent Reward Aggregation**: Design a differentiable social choice voting mechanism (implementing Borda count and Condorcet methods via Gumbel-Softmax relaxation) that aggregates per-cluster rewards while maintaining complete audit trails.

3. **Governance-Compliant Pluralistic Alignment**: Demonstrate that the discovered value clusters correspond to established moral frameworks and that the aggregation process enables human evaluators to identify which values influenced specific decisions.

### 1.3 Research Significance

The significance of this research extends across multiple dimensions:

**Scientific Contribution**: CAVD bridges the gap between unsupervised representation learning and normative social choice theory, establishing a novel paradigm for pluralistic AI alignment that does not require costly annotator metadata collection.

**Practical Impact**: By enabling governance-auditable pluralistic alignment from standard preference data, CAVD dramatically reduces the barriers to deploying value-aware AI systems, making pluralistic alignment accessible to organizations without extensive annotation infrastructure.

**Regulatory Compliance**: The transparent voting mechanism with full audit trails directly addresses EU AI Act requirements for explainable and auditable AI decision-making, providing a concrete technical pathway to regulatory compliance.

**Theoretical Advancement**: The research tests a fundamental hypothesis about the nature of preference disagreement—whether such disagreements encode coherent moral frameworks rather than mere noise—with implications for how the field conceptualizes and handles annotation diversity.

## 2. Methodology

### 2.1 Theoretical Framework

The core hypothesis underlying CAVD posits that under conditions of standard pairwise preference data with implicit annotator disagreement, variational inference can discover $K$ latent value clusters whose rewards, when aggregated via transparent social choice voting, preserve pluralistic value representation while enabling governance-auditable decisions. This hypothesis rests on the assumption that disagreement patterns in preference data encode latent value structure decomposable into interpretable clusters reflecting distinct moral frameworks.

### 2.2 Data Collection and Preparation

**Primary Dataset**: The PERSONA benchmark serves as the primary data source, comprising 1,586 distinct personas and 317,200 pairwise preference pairs. This dataset provides sufficient scale and diversity for discovering meaningful value clusters while enabling validation against known persona characteristics.

**Validation Framework**: The Moral Foundations Questionnaire (MFQ) provides external validation, measuring five moral foundations: Care/Harm, Fairness/Cheating, Loyalty/Betrayal, Authority/Subversion, and Sanctity/Degradation. For personas with available MFQ annotations, we compute correlations between discovered clusters and MFQ dimensions.

**Data Preprocessing**: Each preference pair $(x, y_w, y_l)$ consists of a prompt $x$, a preferred response $y_w$, and a dispreferred response $y_l$. We encode these using a frozen language model encoder to obtain dense representations suitable for variational inference.

### 2.3 Algorithmic Framework

CAVD operates through a four-stage pipeline, each with precise mathematical formulation:

**Stage 1: Variational Cluster Discovery**

We employ a Variational Autoencoder (VAE) architecture to discover soft cluster assignments from preference data. Given a preference pair $(x, y_w, y_l)$, the encoder $q_\phi$ produces a distribution over $K$ latent value clusters:

$$q_\phi(z | x, y_w, y_l) = \text{Categorical}(\pi_1, \pi_2, ..., \pi_K)$$

where $\pi_k = \text{softmax}(f_\phi(h_{x,y_w,y_l}))_k$ and $h_{x,y_w,y_l}$ is the concatenated representation of the preference triple.

The VAE objective combines reconstruction and regularization:

$$\mathcal{L}_{\text{VAE}} = \mathbb{E}_{q_\phi(z|x,y_w,y_l)}[\log p_\theta(y_w \succ y_l | x, z)] - \beta \cdot D_{KL}(q_\phi(z|x,y_w,y_l) || p(z))$$

where $p(z) = \text{Uniform}(1, K)$ serves as the prior, encouraging balanced cluster utilization.

**Stage 2: Specialized Reward Head Training**

For each discovered cluster $k \in \{1, ..., K\}$, we train a specialized reward head $r_k(x, y)$ that captures the preference patterns characteristic of that value cluster:

$$r_k(x, y) = W_k^T \cdot g(h_{x,y}) + b_k$$

where $g$ is a shared feature extractor and $(W_k, b_k)$ are cluster-specific parameters.

The training objective for each reward head incorporates soft cluster assignments:

$$\mathcal{L}_{\text{reward}} = -\sum_{k=1}^{K} \pi_k \cdot \log \sigma(r_k(x, y_w) - r_k(x, y_l))$$

This formulation ensures each reward head specializes on preferences most strongly associated with its cluster while maintaining differentiability.

**Stage 3: Differentiable Social Choice Voting**

We aggregate per-cluster rewards using differentiable implementations of classical voting mechanisms. For Borda count, each cluster $k$ ranks responses, and scores are aggregated:

$$\text{Borda}(y | x) = \sum_{k=1}^{K} w_k \cdot \text{rank}_k(y | x)$$

where $w_k$ represents the cluster's voting weight (uniform by default, or learned).

For Condorcet aggregation, we compute pairwise victory margins:

$$M(y_i, y_j) = \sum_{k=1}^{K} w_k \cdot \mathbb{1}[r_k(x, y_i) > r_k(x, y_j)]$$

To enable end-to-end training, we apply Gumbel-Softmax relaxation to discrete voting operations:

$$\tilde{v}_k = \text{softmax}\left(\frac{\log(\pi_k) + g_k}{\tau}\right)$$

where $g_k \sim \text{Gumbel}(0, 1)$ and $\tau$ is the temperature parameter (annealed from 1.0 to 0.1 during training).

The final aggregated reward is:

$$R_{\text{CAVD}}(x, y) = \sum_{k=1}^{K} \tilde{v}_k \cdot r_k(x, y)$$

**Stage 4: Policy Training with Audit Trail Generation**

The aggregated reward guides policy optimization via standard RLHF or DPO. Crucially, we maintain complete audit trails recording:

- Soft cluster assignments $\pi_k$ for each decision
- Per-cluster reward values $r_k(x, y)$
- Voting weights and aggregation computations
- Final decision with contribution attribution

The audit trail enables post-hoc analysis of which value clusters influenced specific decisions, supporting governance requirements.

### 2.4 Experimental Design

**Experiment 1: Cluster Interpretability Validation (P1)**

*Objective*: Verify that discovered clusters correlate with established moral frameworks.

*Protocol*: 
1. Train CAVD on PERSONA with $K \in \{3, 5, 7, 10\}$
2. For personas with MFQ annotations, compute cluster assignment centroids
3. Calculate Pearson correlation between cluster assignments and each MFQ dimension
4. Apply Bonferroni correction for multiple comparisons ($\alpha' = 0.01$)

*Success Criterion*: $r > 0.3$ for at least 3 of 5 MFQ foundations with $p < 0.05$

*Sample Size Justification*: For detecting $r = 0.3$ with power $= 0.8$ and $\alpha = 0.05$, minimum $n = 84$ personas required; PERSONA provides 1,586.

**Experiment 2: Preference Preservation Comparison (P2)**

*Objective*: Demonstrate competitive performance against label-requiring baselines.

*Protocol*:
1. Train CAVD, VPL (with labels), MODPO (with labels), and single-reward baseline
2. Evaluate per-cluster preference prediction accuracy on held-out test set
3. Compute accuracy ratio: $\text{CAVD accuracy} / \text{MODPO accuracy}$

*Success Criterion*: Ratio $\geq 0.90$ (CAVD achieves at least 90% of MODPO performance)

*Statistical Analysis*: Paired t-test across 15 random seeds, reporting mean and 95% confidence intervals

**Experiment 3: Governance Auditability Assessment (P3)**

*Objective*: Validate that audit trails enable human identification of value contributions.

*Protocol*:
1. Generate 50 model decisions with complete audit trails
2. Recruit 5 expert evaluators (ethics/ML background)
3. Present decisions with audit trails; evaluators identify which clusters influenced each decision
4. Compute Fleiss' kappa for inter-rater reliability

*Success Criterion*: $\kappa > 0.6$ (substantial agreement)

*Control Condition*: Same task with randomized audit trails to establish baseline agreement

**Experiment 4: Ablation Studies**

*Components Ablated*:
- VAE vs. hard clustering (K-means)
- Borda vs. Condorcet voting
- Gumbel-Softmax vs. straight-through estimator
- Uniform vs. learned voting weights

*Metrics*: Preference accuracy, cluster entropy, MFQ correlation, training stability

### 2.5 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| MFQ Correlation | Pearson $r$ between cluster assignments and MFQ dimensions | $r > 0.3$ for $\geq 3/5$ foundations |
| Per-Cluster Accuracy | Preference prediction accuracy within each cluster | $\geq 90\%$ of MODPO |
| Governance Transparency Score | Fleiss' $\kappa$ for human evaluator agreement | $\kappa > 0.6$ |
| Value Inequity Index | Variance in per-cluster accuracy | $< 0.05$ |
| Cluster Entropy | $-\sum_k \bar{\pi}_k \log \bar{\pi}_k$ | $> 0.5$ (non-degenerate) |

### 2.6 Falsification Criteria

The hypothesis will be rejected if any of the following occur:

1. **Primary Failure**: MFQ correlation $r < 0.15$ for all 5 foundations
2. **Mechanism Failure**: Per-cluster accuracy $< 75\%$ of single-reward baseline
3. **Transparency Failure**: Human evaluator agreement $\kappa < 0.4$
4. **Degenerate Clustering**: $> 80\%$ of samples assigned to single cluster OR entropy $< 0.5$

### 2.7 Implementation Details

**Architecture**: Base LLM fixed to Llama-3-8B; VAE encoder uses 2-layer MLP with 512 hidden units; reward heads share a 3-layer transformer feature extractor.

**Training Configuration**: 40 configurations total (5 seeds × 4 $K$ values × 2 voting rules); batch size 32; learning rate $1 \times 10^{-5}$ with cosine annealing; Gumbel-Softmax temperature annealed from 1.0 to 0.1 over 10 epochs.

**Computational Resources**: Single 80GB A100 GPU; estimated 2-3 days per configuration; total compute approximately 120 GPU-days.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (Cluster Interpretability)**: We anticipate discovering 5 latent value clusters that correlate meaningfully ($r > 0.3$) with at least 3 of the 5 Moral Foundations Questionnaire dimensions. Based on preliminary analysis of preference disagreement patterns, we expect particularly strong correlations with Care/Harm and Fairness/Cheating foundations, which tend to generate the most pronounced disagreements in content moderation and ethical judgment tasks.

**Secondary Outcome (Preference Preservation)**: CAVD is expected to achieve per-cluster preference accuracy within 90-95% of MODPO despite not requiring explicit annotator labels. This outcome would validate the core insight that disagreement patterns encode sufficient information for value-aware preference modeling without metadata.

**Tertiary Outcome (Governance Auditability)**: Human evaluators are expected to achieve substantial agreement ($\kappa > 0.6$) when identifying value cluster contributions from audit trails, demonstrating that the voting-based aggregation mechanism produces genuinely interpretable decisions rather than opaque numerical combinations.

### 3.2 Scientific Impact

**Theoretical Contributions**: This research establishes a novel theoretical bridge between unsupervised representation learning and normative social choice theory. By demonstrating that preference disagreements encode coherent moral frameworks discoverable via variational inference, we challenge the prevailing assumption that annotation disagreement represents noise. This reconceptualization has implications for how the field approaches data collection, annotation protocols, and model training.

**Methodological Innovations**: The differentiable social choice voting mechanism represents a technical contribution applicable beyond pluralistic alignment. The Gumbel-Softmax relaxation of Borda and Condorcet voting enables end-to-end training of systems requiring discrete aggregation decisions, with potential applications in multi-agent systems, ensemble methods, and democratic AI governance.

**Empirical Benchmarks**: The experimental framework establishes rigorous benchmarks for evaluating pluralistic alignment methods, including the novel Governance Transparency Score and Value Inequity Index. These metrics address a critical gap in current evaluation practices, which focus predominantly on aggregate accuracy while ignoring distributional fairness across value groups.

### 3.3 Practical Impact

**Scalability**: By eliminating the requirement for explicit annotator labels, CAVD dramatically reduces the cost and complexity of deploying pluralistic AI systems. Organizations can leverage existing preference datasets without retrofitting expensive metadata collection pipelines.

**Regulatory Compliance**: The audit trail mechanism directly addresses EU AI Act requirements for explainable and auditable AI decision-making. Organizations deploying CAVD-aligned systems can demonstrate precisely how value trade-offs were handled and whose perspectives influenced specific decisions.

**Deployment Readiness**: The approximately 5% inference latency overhead from the voting mechanism represents an acceptable trade-off for governance-critical applications. The modular architecture enables integration with existing RLHF/DPO pipelines with minimal modification.

### 3.4 Broader Societal Impact

**Democratic AI Governance**: CAVD provides a technical foundation for more democratic AI systems that transparently represent diverse value perspectives rather than implicitly favoring majority viewpoints. This aligns with broader societal goals of inclusive technology development.

**Marginalized Voice Representation**: By discovering and explicitly modeling minority value clusters, CAVD addresses systematic underrepresentation in current alignment methods. The Value Inequity Index provides a concrete metric for monitoring and improving representational fairness.

**Interdisciplinary Bridge**: This research demonstrates productive integration of insights from moral philosophy (Moral Foundations Theory), political science (social choice theory), and machine learning (variational inference), modeling the interdisciplinary collaboration essential for responsible AI development.

### 3.5 Limitations and Future Directions

**Current Limitations**: Cluster interpretability depends on post-hoc MFQ correlation, which may not capture all relevant value dimensions. The approach requires diverse annotator pools to generate meaningful disagreement signals and may underperform in low-resource settings with fewer than 10,000 preference pairs.

**Future Research Directions**: 
1. Extending CAVD to handle dynamic value evolution over time
2. Developing interactive interfaces for stakeholder engagement with discovered value clusters
3. Investigating cross-cultural generalization of discovered moral frameworks
4. Exploring integration with constitutional AI approaches for value specification

In conclusion, CAVD represents a significant advance toward governance-compliant pluralistic AI alignment, offering a scalable, transparent, and theoretically grounded approach to discovering and aggregating diverse human values from standard preference data.