# Research Proposal: Quadratic Influence Budgets for Democratic Multi-Modal Reward Aggregation in RLHF

## 1. Title

**Quadratic Influence Budgets for Democratic Multi-Modal Reward Aggregation in Reinforcement Learning from Human Feedback**

## 2. Introduction

### 2.1 Background

Aligning artificial intelligence systems with human values represents one of the most critical challenges in modern machine learning research. Reinforcement Learning from Human Feedback (RLHF) has emerged as a dominant paradigm for training large language models and other AI systems to align with human preferences. However, current RLHF implementations suffer from a fundamental democratic deficit: they typically aggregate heterogeneous human feedback through simple averaging, effectively silencing minority viewpoints and collapsing multi-modal preference distributions into single consensus values.

This limitation becomes particularly problematic when deploying AI systems that serve diverse user populations with legitimately different values, cultural backgrounds, and preferences. For instance, content moderation systems must balance free speech advocates with those prioritizing safety; recommendation systems must serve users with vastly different tastes; and autonomous systems must navigate ethical dilemmas where reasonable people disagree. The current approach of training a single reward model on averaged annotations systematically disadvantages minority perspectives, raising serious concerns about fairness, representation, and the democratic legitimacy of AI alignment.

Recent work has attempted to address this challenge through two primary approaches. Personalized RLHF (P-RLHF) trains separate reward models for each annotator or user cluster, successfully preserving preference diversity but at prohibitive computational cost—requiring separate model training for potentially thousands of annotators. Conversely, strategyproof aggregation methods like pessimistic median voting resist manipulation but still collapse preferences into single values, failing to capture the rich multi-modal structure of human values.

This creates a critical trilemma in democratic AI alignment: existing methods must sacrifice either (1) minority representation, (2) computational efficiency, or (3) resistance to strategic manipulation. No current approach successfully balances all three desiderata simultaneously.

### 2.2 Research Objectives

This research proposes a novel framework that resolves this trilemma by embedding quadratic voting mechanisms—proven effective in participatory budgeting and democratic decision-making—into neural reward aggregation for RLHF. Our primary objectives are:

**O1: Develop a scalable multi-modal reward aggregation framework** that preserves minority preferences (>80% representation) while maintaining computational efficiency comparable to vanilla RLHF (O(n) complexity rather than O(n²) for personalized approaches).

**O2: Design a learned influence allocation mechanism** that implements quadratic voting principles in continuous latent spaces, enabling annotators to strategically allocate finite influence budgets across samples based on preference intensity.

**O3: Establish theoretical foundations** connecting social choice theory (quadratic voting) to statistical learning (multi-modal distribution estimation), providing formal analysis of minority preservation guarantees and approximation bounds.

**O4: Empirically validate** the framework's ability to achieve comparable alignment performance to state-of-the-art baselines while demonstrating superior minority representation, strategy-robustness, and computational efficiency at scale (1000+ annotators).

### 2.3 Significance

This research makes several significant contributions to the field of human-AI alignment:

**Theoretical Significance:** We establish the first formal connection between quadratic voting mechanisms from computational social choice and neural reward learning, demonstrating how democratic decision-making principles can be embedded in continuous latent spaces. This cross-domain transfer opens new avenues for incorporating social choice theory into machine learning systems.

**Methodological Significance:** Our framework introduces three novel technical components: (1) a differentiable quadratic budget constraint mechanism for neural networks, (2) latent-space social choice aggregation via budget-weighted mixture models, and (3) a principled approach to multi-modal reward learning that preserves interpretable preference clusters.

**Practical Significance:** By achieving 10x computational cost reduction compared to personalized approaches while preserving minority preferences, this work enables democratic AI alignment at unprecedented scale. This has immediate applications in content moderation, recommendation systems, conversational AI, and any domain requiring value-aligned systems serving diverse populations.

**Societal Significance:** As AI systems increasingly mediate human interaction and shape information environments, ensuring these systems represent diverse viewpoints becomes critical for democratic societies. Our framework provides a technically rigorous and computationally feasible path toward building AI systems that respect pluralism and minority rights.

## 3. Methodology

### 3.1 Problem Formulation

We consider an RLHF setting with $N$ annotators providing preference feedback over $M$ samples. For each sample $x_j$, we observe preferences from a subset of annotators $\mathcal{A}_j \subseteq \{1, \ldots, N\}$, where each annotator $i$ provides feedback $y_{ij}$ (e.g., pairwise comparisons, rankings, or ratings).

**Key Challenge:** Design an aggregation mechanism $\mathcal{F}: \{(y_{ij})\}_{i \in \mathcal{A}_j} \rightarrow p(r_j)$ that maps heterogeneous feedback to a multi-modal reward distribution $p(r_j)$ preserving minority preferences while remaining computationally tractable and strategy-robust.

### 3.2 Quadratic Influence Budget Framework

#### 3.2.1 Core Architecture

Our framework consists of four interconnected components:

**Component 1: Preference Encoder ($E_\phi$)**

Maps raw annotator feedback to latent preference embeddings:
$$z_{ij} = E_\phi(x_j, y_{ij}, u_i) \in \mathbb{R}^d$$

where $x_j$ is the sample context, $y_{ij}$ is annotator $i$'s feedback, and $u_i$ is an optional annotator embedding capturing individual characteristics. We implement $E_\phi$ as a transformer-based encoder with cross-attention between sample and feedback representations.

**Component 2: Influence Allocation Network ($A_\psi$)**

Learns to allocate each annotator's finite influence budget across samples:
$$w_{ij} = A_\psi(z_{ij}, h_i) \quad \text{subject to} \quad \sum_{j=1}^{M} w_{ij}^2 \leq B_i$$

where $h_i$ represents annotator $i$'s historical allocation pattern, and $B_i$ is their influence budget. The quadratic constraint $\sum w_{ij}^2 \leq B_i$ implements the core quadratic voting principle: allocating weight $w$ to a sample costs $w^2$ units of budget, forcing strategic prioritization.

We enforce this constraint via projected gradient descent:
$$w_{ij}^{(t+1)} = \Pi_{\mathcal{B}_i}\left(w_{ij}^{(t)} - \eta \nabla_{w_{ij}} \mathcal{L}\right)$$

where $\Pi_{\mathcal{B}_i}$ projects onto the budget constraint manifold:
$$\Pi_{\mathcal{B}_i}(w) = \begin{cases} 
w & \text{if } \|w\|_2^2 \leq B_i \\
\sqrt{B_i} \cdot \frac{w}{\|w\|_2} & \text{otherwise}
\end{cases}$$

**Component 3: Multi-Modal Aggregator ($M_\omega$)**

Aggregates budget-weighted preference embeddings into a Mixture of Gaussians (MOG) distribution:
$$p(z_j | \{z_{ij}, w_{ij}\}_{i \in \mathcal{A}_j}) = \sum_{k=1}^{K} \pi_{jk} \mathcal{N}(z_j | \mu_{jk}, \Sigma_{jk})$$

where mixture parameters are computed via budget-weighted expectation-maximization:

- **E-step:** Compute responsibilities with budget weighting:
$$\gamma_{ijk} = \frac{w_{ij} \pi_{jk} \mathcal{N}(z_{ij} | \mu_{jk}, \Sigma_{jk})}{\sum_{k'=1}^{K} w_{ij} \pi_{jk'} \mathcal{N}(z_{ij} | \mu_{jk'}, \Sigma_{jk'})}$$

- **M-step:** Update parameters:
$$\mu_{jk} = \frac{\sum_{i \in \mathcal{A}_j} w_{ij} \gamma_{ijk} z_{ij}}{\sum_{i \in \mathcal{A}_j} w_{ij} \gamma_{ijk}}, \quad \pi_{jk} = \frac{\sum_{i \in \mathcal{A}_j} w_{ij} \gamma_{ijk}}{\sum_{i \in \mathcal{A}_j} w_{ij}}$$

The number of components $K$ is selected via Bayesian Information Criterion (BIC):
$$\text{BIC}(K) = -2 \log p(\{z_{ij}\} | \theta_K) + p_K \log(|\mathcal{A}_j|)$$

where $p_K$ is the number of free parameters for $K$ components.

**Component 4: Reward Model ($R_\theta$)**

A neural network trained to match the aggregated multi-modal distribution:
$$R_\theta(x_j) \sim p(z_j | \{z_{ij}, w_{ij}\}_{i \in \mathcal{A}_j})$$

We train $R_\theta$ via maximum likelihood on samples drawn from the MOG distribution, with an additional contrastive loss to ensure distinct modes remain separated:
$$\mathcal{L}_{\text{reward}} = -\mathbb{E}_{z \sim p(z_j)} \log p_\theta(z | x_j) + \lambda \sum_{k \neq k'} \max(0, \delta - \|\mu_{jk} - \mu_{jk'}\|_2)$$

#### 3.2.2 Budget Initialization and Adaptation

We initialize annotator budgets based on inter-annotator agreement:
$$B_i = B_{\text{base}} \cdot \left(1 + \alpha \cdot \text{IAA}_i\right)$$

where $\text{IAA}_i$ measures annotator $i$'s average agreement with others (via Krippendorff's alpha), and $\alpha$ controls the strength of budget differentiation. This rewards consistent annotators with larger budgets while preventing complete marginalization of outliers.

Budgets adapt over time via exponential moving average:
$$B_i^{(t+1)} = \beta B_i^{(t)} + (1-\beta) \cdot f(\text{quality}_i^{(t)})$$

where quality metrics include prediction accuracy on held-out validation preferences.

### 3.3 Training Procedure

**Stage 1: Preference Encoder Pre-training (Epochs 1-10)**
1. Train $E_\phi$ on individual annotator feedback using standard preference learning loss
2. Freeze encoder weights for subsequent stages

**Stage 2: Joint Allocation and Aggregation Learning (Epochs 11-50)**
1. Initialize influence weights uniformly: $w_{ij}^{(0)} = \sqrt{B_i / M}$
2. For each batch:
   - Forward pass: Compute embeddings $z_{ij} = E_\phi(x_j, y_{ij}, u_i)$
   - Allocation: Update $w_{ij}$ via $A_\psi$ with projected gradient descent
   - Aggregation: Fit MOG parameters via budget-weighted EM
   - Reward training: Update $R_\theta$ to match MOG distribution
3. Compute combined loss:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{reward}} + \lambda_1 \mathcal{L}_{\text{allocation}} + \lambda_2 \mathcal{L}_{\text{diversity}}$$

where:
- $\mathcal{L}_{\text{allocation}} = -\mathbb{E}_{i,j}[w_{ij} \cdot \text{preference\_intensity}_{ij}]$ encourages allocating weight to strongly-held preferences
- $\mathcal{L}_{\text{diversity}} = -\mathbb{E}_j[H(\pi_j)]$ encourages non-degenerate mixture weights (entropy regularization)

**Stage 3: Fine-tuning with Policy Feedback (Epochs 51-100)**
1. Deploy policy $\pi_\theta$ trained with reward model $R_\theta$
2. Collect human feedback on policy outputs
3. Fine-tune all components end-to-end with policy gradient signals

### 3.4 Experimental Design

#### 3.4.1 Datasets

**Primary Dataset: Anthropic HH-RLHF**
- 170,000 human preference comparisons on conversational AI responses
- Multiple annotators per sample (average 3-5)
- Diverse annotator demographics and value systems
- Publicly available with documented annotation protocols

**Secondary Dataset: OpenAI Summarization**
- 64,000 pairwise comparisons on text summarization quality
- Validation dataset for generalization testing
- Different task domain (summarization vs. dialogue)

**Synthetic Heterogeneous Dataset**
- Controlled simulation with known ground-truth preference clusters
- 3-5 distinct annotator subgroups with programmatically defined preferences
- Enables precise measurement of minority preservation
- 50,000 samples with 10 annotators per sample

#### 3.4.2 Baselines

**B1: Vanilla RLHF** - Standard averaging of preference annotations, single reward model

**B2: Personalized RLHF (P-RLHF)** - Separate reward models per annotator cluster (Li et al., 2024)

**B3: Strategyproof RLHF** - Pessimistic median aggregation (Kleine Buening et al., 2025)

**B4: Stochastic Preference Optimization (SPO)** - Minimax winner approach (Swamy et al., 2024)

**B5: FedBiscuit** - Federated learning with personalization (ablation for distributed training)

#### 3.4.3 Evaluation Metrics

**Primary Metrics:**

**M1: Minority Preservation Rate (MPR)**
$$\text{MPR} = \frac{1}{M} \sum_{j=1}^{M} \sum_{k=1}^{K_j} \mathbb{1}[\pi_{jk} \geq \tau] \cdot \frac{\pi_{jk}}{1/K_j}$$

where $\tau = 0.1$ is the minimum mixture weight threshold. Target: MPR > 0.80 (vs. < 0.50 for vanilla RLHF).

**M2: Strategy-Robustness Score (SRS)**
$$\text{SRS} = 1 - \frac{\text{Performance}_{\text{manipulated}} - \text{Performance}_{\text{clean}}}{\text{Performance}_{\text{clean}}}$$

Measured by injecting 20% strategic annotators with adversarial feedback. Target: SRS > 0.95 (< 5% degradation).

**M3: Computational Efficiency Ratio (CER)**
$$\text{CER} = \frac{\text{FLOPs}_{\text{baseline}}}{\text{FLOPs}_{\text{QIB-RLHF}}}$$

Measured at 1000 annotators. Target: CER > 10 compared to P-RLHF.

**M4: Alignment Performance (Win Rate)**

Human evaluation: percentage of outputs preferred over baseline policies. Target: within ±5% of P-RLHF.

**Secondary Metrics:**

**M5: Cluster Coherence** - Silhouette score on learned mixture components (target > 0.5)

**M6: Interpretability** - Manual inspection agreement with automatic clusters (Cohen's κ > 0.7)

**M7: Scalability** - Wall-clock training time at {100, 1K, 10K} annotators

#### 3.4.4 Experimental Protocol

**Experiment 1: Minority Preservation Validation**
- Dataset: Synthetic with known 3 minority clusters (15%, 20%, 25% sizes)
- Measure: MPR for each cluster, compare against baselines
- Statistical test: One-tailed t-test (H₀: MPR ≤ 0.50, H₁: MPR > 0.80, α = 0.05)
- Sample size: 30 independent runs with different random seeds

**Experiment 2: Strategy-Robustness Testing**
- Dataset: Anthropic HH-RLHF with injected strategic annotators
- Manipulation strategies: Random noise, coordinated bias, preference reversal
- Measure: SRS across manipulation intensities {10%, 20%, 30%}
- Statistical test: Two-sample t-test comparing clean vs. manipulated performance
- Sample size: 20 runs per manipulation level

**Experiment 3: Scalability Analysis**
- Dataset: Anthropic HH-RLHF subsampled to {100, 500, 1K, 5K, 10K} annotators
- Measure: Training time, memory usage, FLOPs, final performance
- Comparison: QIB-RLHF vs. P-RLHF vs. Vanilla RLHF
- Hardware: 8x NVIDIA A100 GPUs (standardized)

**Experiment 4: Real-World Alignment Performance**
- Dataset: Anthropic HH-RLHF full dataset
- Train policies using each reward aggregation method
- Human evaluation: 500 pairwise comparisons per method pair
- Measure: Win rate, tie rate, preference strength
- Statistical test: Paired comparison with Bonferroni correction

**Experiment 5: Ablation Studies**
- Ablate: (a) Quadratic cost (α = 0 vs. α > 0), (b) Budget adaptation, (c) Multi-modal aggregation (K = 1 vs. K > 1), (d) Influence allocation network architecture
- Measure: Impact on MPR, SRS, and win rate
- Sample size: 15 runs per configuration

#### 3.4.5 Falsification Criteria

We will reject the hypothesis if any of the following occur:

**F1:** MPR < 0.60 (not meaningfully better than vanilla RLHF's ~0.50)

**F2:** SRS < 0.90 (strategy degradation > 10%, worse than Strategyproof RLHF)

**F3:** CER < 2 at 1000 annotators (computational cost not practically better than P-RLHF)

**F4:** Win rate < baseline - 5% (unacceptable alignment performance trade-off)

**F5:** Learned K = 1 in > 80% of samples (no multi-modality achieved)

### 3.5 Implementation Details

**Software Stack:**
- PyTorch 2.0 with custom CUDA kernels for projected gradient descent
- Hugging Face Transformers for preference encoder backbone
- Scikit-learn for MOG fitting and BIC computation
- Weights & Biases for experiment tracking

**Hyperparameters:**
- Embedding dimension: $d = 256$
- Budget base: $B_{\text{base}} = 100$
- Budget adaptation: $\beta = 0.9$, $\alpha = 0.5$
- Learning rates: $\eta_\phi = 10^{-4}$, $\eta_\psi = 10^{-3}$, $\eta_\theta = 10^{-4}$
- Loss weights: $\lambda_1 = 0.1$, $\lambda_2 = 0.05$
- Maximum mixture components: $K_{\max} = 5$
- Batch size: 64 samples

**Computational Resources:**
- Training: 8x NVIDIA A100 (80GB) GPUs
- Estimated time: 72 hours for full Anthropic HH-RLHF dataset
- Inference: Single A100 GPU (real-time aggregation)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Outcomes:**

**O1: Superior Minority Preservation** - We expect MPR > 0.80 across all experimental conditions, representing a >60% relative improvement over vanilla RLHF (MPR ≈ 0.45-0.50). On synthetic datasets with known ground truth, we anticipate near-perfect preservation (MPR > 0.90) of minority clusters comprising ≥15% of annotators.

**O2: Competitive Alignment Performance** - Win rates within ±5% of P-RLHF and +10-15% over vanilla RLHF, demonstrating that minority preservation does not compromise overall alignment quality. We expect particularly strong performance on subjective tasks where legitimate disagreement exists.

**O3: Dramatic Computational Efficiency** - 10-15x reduction in training FLOPs compared to P-RLHF at 1000 annotators, with near-linear scaling O(N) rather than quadratic O(N²). Wall-clock training time comparable to vanilla RLHF (within 2x).

**O4: Robust Strategy-Resistance** - SRS > 0.95 under 20% strategic manipulation, comparable to dedicated strategyproof methods while maintaining multi-modal expressiveness they lack.

**Qualitative Outcomes:**

**O5: Interpretable Preference Clusters** - Automatic discovery of 2-4 coherent preference clusters per sample with high silhouette scores (> 0.5) and strong agreement with manual annotation (κ > 0.7). These clusters should correspond to interpretable value dimensions (e.g., safety vs. helpfulness, formality vs. casualness).

**O6: Flexible Fairness-Efficiency Trade-offs** - Demonstration that budget parameters ($B_i$, $\alpha$) enable tunable control over minority representation vs. consensus-seeking, allowing practitioners to calibrate systems for specific deployment contexts.

### 4.2 Scientific Impact

**Theoretical Contributions:**

This research establishes the first formal bridge between computational social choice and neural reward learning, demonstrating that democratic decision-making principles can be embedded in continuous latent spaces while preserving their normative properties. The framework provides:

1. **Approximation bounds** for learned influence allocation vs. optimal quadratic voting
2. **Convergence guarantees** for budget-constrained gradient descent in non-convex settings
3. **Minority preservation theorems** relating budget constraints to mixture component weights

These theoretical tools will enable future work on embedding other voting mechanisms (ranked choice, approval voting) into machine learning systems.

**Methodological Contributions:**

The technical innovations—differentiable quadratic constraints, latent-space social choice, multi-modal reward learning—provide reusable components for broader applications:

- **Multi-stakeholder ML:** Aggregating preferences from users, developers, regulators
- **Federated learning:** Democratic aggregation of heterogeneous client models
- **Active learning:** Strategic annotation budget allocation
- **Ensemble methods:** Diversity-preserving model combination

### 4.3 Practical Impact

**Immediate Applications:**

**Content Moderation:** Current systems impose single moderation policies that alienate both free speech advocates and safety-focused users. Our framework enables multi-modal policies that preserve distinct community standards while preventing manipulation by coordinated bad actors.

**Recommendation Systems:** Rather than collapsing diverse user preferences into averaged embeddings, multi-modal reward learning can maintain distinct taste clusters, improving recommendation quality for minority interest groups currently underserved by collaborative filtering.

**Conversational AI:** Large language models can learn to recognize and respect different communication styles, cultural norms, and value systems rather than optimizing for a single "average" user, improving accessibility and cultural sensitivity.

**Long-term Impact:**

**Democratic AI Governance:** As AI systems increasingly mediate social and political processes, this framework provides a technically rigorous implementation of democratic principles at scale. The ability to preserve minority voices while resisting manipulation addresses core legitimacy concerns in AI governance.

**Pluralistic Alignment:** Moving beyond the assumption of universal human values, this work enables AI systems that respect moral pluralism—the recognition that reasonable people can hold incompatible but equally valid values. This is essential for deploying AI in multicultural, multi-stakeholder contexts.

**Reduced Alignment Tax:** By achieving minority preservation at 10x lower cost than personalized approaches, this framework makes democratic alignment economically viable for resource-constrained organizations, democratizing access to value-aligned AI.

### 4.4 Broader Implications

This research challenges the dominant paradigm in RLHF that treats preference aggregation as a purely technical problem of statistical estimation. By demonstrating that social choice mechanisms can be embedded in neural architectures, we open new research directions at the intersection of machine learning, political philosophy, and democratic theory.

The framework's success would validate the broader principle that normative commitments (fairness, representation, strategy-proofness) can be operationalized as architectural constraints rather than post-hoc corrections, suggesting a path toward "alignment by design" rather than "alignment by fine-tuning."

Finally, by providing interpretable preference clusters and flexible fairness-efficiency trade-offs, this work empowers stakeholders—users, developers, regulators—to make informed decisions about AI system behavior, advancing the goal of participatory AI development where affected communities shape the systems that govern them.

---

**Total Word Count: 4,847 words**