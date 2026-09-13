# Research Proposal: Shapley-Weighted Direct Preference Optimization for Fair LLM Alignment

## 1. Introduction

### 1.1 Background

Large language models (LLMs) have achieved remarkable capabilities through preference-based learning, particularly via Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO). These methods leverage human preference data to align model outputs with human values and intentions, enabling sophisticated dialogue systems, content generation, and decision support tools. However, a critical challenge has emerged: LLMs aligned through preference learning often exhibit systematic demographic disparities, performing substantially better for majority groups whose preferences dominate training datasets.

This disparity arises from a fundamental imbalance in preference data collection. When certain demographic groups contribute more preference annotations—whether due to sampling bias, accessibility differences, or historical data collection practices—the resulting aligned models disproportionately reflect those groups' preferences. Empirical studies using the HELM framework have documented significant fairness gaps, with Gini coefficients measuring demographic disparity ranging from 0.58 to 0.73 across different model architectures, indicating substantial inequality in model performance across demographic groups.

Current approaches to addressing fairness in preference-based learning rely primarily on ad-hoc constraints, post-hoc adjustments, or robust optimization techniques. Methods such as FARO (Fairness-Aware Reward Optimization) impose explicit fairness constraints during training, while GRPO (Group-Robust Preference Optimization) employs distributionally robust optimization to improve worst-group performance. However, these approaches lack principled theoretical justification for their fairness mechanisms, often requiring manual tuning of fairness-accuracy tradeoff parameters without clear guidance on appropriate values.

### 1.2 Research Motivation

Cooperative game theory offers a principled solution through Shapley values—a unique attribution method that satisfies four fundamental fairness axioms: efficiency (total contribution equals total value), symmetry (equal contributors receive equal attribution), null-player (non-contributors receive zero attribution), and additivity (contributions across games sum appropriately). These axioms provide mathematical guarantees for fair contribution-based representation that ad-hoc fairness constraints cannot match.

The intersection of social choice theory and preference-based learning presents a compelling opportunity. By computing Shapley values for each demographic group's contribution to reward model accuracy, we can identify underrepresented groups whose preferences are inadequately captured and systematically amplify their influence during training. This approach transforms fairness from an external constraint into an intrinsic property of the learning objective.

### 1.3 Research Objectives

This research proposes Shapley-Weighted Direct Preference Optimization (SW-DPO), a novel method that integrates Shapley value-based fairness attribution into the DPO training framework. Our primary objectives are:

1. **Develop SW-DPO**: Design and implement a gradient-based Shapley approximation method that efficiently computes demographic group contributions during DPO training.

2. **Validate Fairness Improvement**: Demonstrate that SW-DPO reduces demographic disparity (measured by Gini coefficient) by at least 20% compared to standard DPO while maintaining at least 95% of baseline alignment accuracy.

3. **Establish Causal Mechanism**: Verify that the Shapley value-based weighting mechanism is the actual cause of fairness improvements through systematic ablation studies.

4. **Compare Against Baselines**: Evaluate SW-DPO against existing fairness approaches (FARO, GRPO) to establish its practical value in the fairness-accuracy tradeoff.

### 1.4 Significance

This research bridges cooperative game theory with preference-based LLM alignment, providing the first axiomatically-grounded approach to fair preference learning. Beyond LLMs, the methodology extends to recommender systems, robotics, and any domain where group fairness in preference aggregation is desired. By grounding fairness in mathematical axioms rather than ad-hoc constraints, SW-DPO offers principled guidance for practitioners seeking to build equitable AI systems.

## 2. Methodology

### 2.1 Problem Formulation

Consider a preference dataset $\mathcal{D} = \{(x_i, y_i^w, y_i^l)\}_{i=1}^N$ where $x_i$ is an input prompt, $y_i^w$ is the preferred response, and $y_i^l$ is the dispreferred response. Each preference pair is associated with a demographic group $g \in \mathcal{G}$, where $\mathcal{G}$ represents the set of demographic categories (e.g., age, gender, ethnicity, or their intersections).

Standard DPO optimizes the policy $\pi_\theta$ using the loss function:

$$\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y^w, y^l) \sim \mathcal{D}} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y^w|x)}{\pi_{\text{ref}}(y^w|x)} - \beta \log \frac{\pi_\theta(y^l|x)}{\pi_{\text{ref}}(y^l|x)} \right) \right]$$

where $\sigma$ is the sigmoid function, $\beta$ is a temperature parameter, and $\pi_{\text{ref}}$ is the reference policy.

The key limitation is that this formulation treats all preference pairs equally, regardless of demographic group representation, leading to models that disproportionately reflect majority group preferences.

### 2.2 Shapley Value Computation for Demographic Groups

We define a cooperative game $(N, v)$ where $N = \mathcal{G}$ is the set of demographic groups and $v: 2^N \rightarrow \mathbb{R}$ is the characteristic function measuring reward model accuracy when trained on subsets of groups.

The Shapley value for group $g$ is:

$$\phi_g = \sum_{S \subseteq N \setminus \{g\}} \frac{|S|!(|N|-|S|-1)!}{|N|!} \left[ v(S \cup \{g\}) - v(S) \right]$$

This measures group $g$'s marginal contribution to reward model accuracy across all possible coalitions.

**Gradient-Based Approximation**: Exact Shapley computation is exponential in $|N|$. We employ gradient-based approximation using Monte Carlo sampling:

$$\hat{\phi}_g = \frac{1}{M} \sum_{m=1}^M \left[ v(S_m \cup \{g\}) - v(S_m) \right]$$

where $S_m$ is sampled uniformly from $2^{N \setminus \{g\}}$ and $M$ is the number of Monte Carlo samples (we use $M = 100$).

The characteristic function $v(S)$ is computed as the validation accuracy of a reward model trained only on preference data from groups in $S$:

$$v(S) = \text{Accuracy}\left( r_\theta^{(S)}, \mathcal{D}_{\text{val}} \right)$$

where $r_\theta^{(S)}$ is trained on $\mathcal{D}_S = \{(x_i, y_i^w, y_i^l) : g_i \in S\}$.

### 2.3 SW-DPO Loss Function

We define inverse-proportional weights based on Shapley values to amplify underrepresented groups:

$$w_g = \frac{1/\phi_g}{\sum_{g' \in \mathcal{G}} 1/\phi_{g'}}$$

Groups with lower Shapley contributions (indicating underrepresentation) receive higher weights. The SW-DPO loss becomes:

$$\mathcal{L}_{\text{SW-DPO}}(\theta) = -\sum_{g \in \mathcal{G}} w_g \cdot \mathbb{E}_{(x, y^w, y^l) \sim \mathcal{D}_g} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y^w|x)}{\pi_{\text{ref}}(y^w|x)} - \beta \log \frac{\pi_\theta(y^l|x)}{\pi_{\text{ref}}(y^l|x)} \right) \right]$$

### 2.4 Algorithm

**Algorithm 1: Shapley-Weighted DPO Training**

```
Input: Preference dataset D with demographic labels, reference policy π_ref, 
       demographic groups G, update frequency T_update, Monte Carlo samples M
Output: Aligned policy π_θ

1. Initialize policy π_θ from π_ref
2. Initialize Shapley weights w_g = 1/|G| for all g ∈ G
3. For epoch e = 1 to E:
4.     If e mod T_update == 0:
5.         For each group g ∈ G:
6.             φ_g ← 0
7.             For m = 1 to M:
8.                 Sample S_m uniformly from 2^(G\{g})
9.                 Train reward model r^(S_m) on D_{S_m}
10.                Train reward model r^(S_m∪{g}) on D_{S_m∪{g}}
11.                φ_g ← φ_g + [v(S_m∪{g}) - v(S_m)] / M
12.            End For
13.        End For
14.        Compute weights: w_g ← (1/φ_g) / Σ_{g'}(1/φ_{g'})
15.    End If
16.    For each batch B:
17.        Compute L_SW-DPO using current weights w_g
18.        Update θ via gradient descent
19.    End For
20. End For
21. Return π_θ
```

### 2.5 Hierarchical Grouping for Intersectionality

To address intersectional fairness while avoiding combinatorial explosion, we employ hierarchical grouping. For $K$ demographic attributes each with $L$ levels, naive intersection yields $L^K$ groups. We limit to $\leq 64$ groups using:

1. **Primary grouping**: Single attributes (e.g., age, gender, ethnicity)
2. **Secondary grouping**: Pairwise intersections for attributes with significant interaction effects (detected via statistical testing)
3. **Pruning**: Remove groups with $<1000$ preference pairs

### 2.6 Experimental Design

**Datasets**:
- **Anthropic HH-RLHF**: Human preference data with partial demographic metadata
- **Synthetic Augmentation**: For controlled experiments, we augment datasets with synthetic demographic labels following documented demographic distributions

**Models**:
- Base model: LLaMA-2-7B
- Training framework: TRL DPOTrainer with custom SW-DPO loss

**Baselines**:
1. **Standard DPO**: Unweighted baseline
2. **FARO**: Constraint-based fairness approach
3. **GRPO**: Group-robust preference optimization
4. **Uniform Reweighting**: Equal weights per group (ablation)

**Experimental Configurations**:
- 5 random seeds × 4 demographic configurations = 20 runs per method
- Demographic configurations vary group imbalance ratios (1:2, 1:4, 1:8, 1:16)

### 2.7 Evaluation Metrics

**Primary Metric - Demographic Disparity**:
$$\text{Gini} = \frac{\sum_{i=1}^{|G|} \sum_{j=1}^{|G|} |a_i - a_j|}{2|G| \sum_{i=1}^{|G|} a_i}$$

where $a_i$ is the reward model accuracy for group $i$.

**Secondary Metrics**:
- **Overall Alignment Accuracy**: Win-rate on held-out preference pairs
- **Worst-Group Accuracy**: Minimum accuracy across all groups
- **Computational Overhead**: $(T_{\text{SW-DPO}} - T_{\text{DPO}}) / T_{\text{DPO}}$

### 2.8 Statistical Analysis

**Hypothesis Testing**:
- Paired t-test comparing SW-DPO vs. DPO (same random seeds)
- Significance level: $\alpha = 0.05$ with Bonferroni correction ($\alpha_{\text{adj}} = 0.017$)
- Effect size: Cohen's $d \geq 0.5$ (medium effect)

**Success Criteria**:
- P1: Gini(SW-DPO) / Gini(DPO) $\leq 0.80$ (≥20% reduction)
- P2: Accuracy(SW-DPO) / Accuracy(DPO) $\geq 0.95$
- P3: Computational overhead $\leq 20\%$

**Falsification Criteria**:
- Gini reduction $< 10\%$
- Accuracy drop $> 10\%$
- Uniform Shapley weights across groups (mechanism failure)

### 2.9 Ablation Studies

To verify the causal mechanism:
1. **Shapley vs. Random Weights**: Replace Shapley weights with random weights
2. **Shapley vs. Frequency Weights**: Replace with inverse frequency weights
3. **Update Frequency**: Vary $T_{\text{update}} \in \{1, 5, 10, 20\}$ epochs
4. **Monte Carlo Samples**: Vary $M \in \{10, 50, 100, 200\}$

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence from related work, we anticipate:

1. **Fairness Improvement**: SW-DPO will achieve Gini coefficient reduction of 20-30% compared to standard DPO, with statistical significance ($p < 0.05$, Cohen's $d > 0.5$). This prediction is grounded in evidence from federated learning settings where Shapley-based fairness mechanisms achieved similar improvements.

2. **Maintained Alignment Quality**: Overall alignment accuracy will remain within 5% of the DPO baseline, demonstrating that fairness improvements do not require substantial accuracy sacrifices. The Shapley axioms ensure efficient redistribution of training signal rather than degradation.

3. **Computational Feasibility**: Gradient-based Shapley approximation will add $\leq 20\%$ computational overhead, making SW-DPO practical for real-world deployment. Amortized computation through periodic updates ($T_{\text{update}} = 5$ epochs) will minimize runtime impact.

4. **Mechanism Validation**: Ablation studies will confirm that Shapley-based weights outperform both random and frequency-based alternatives, validating the causal mechanism.

### 3.2 Theoretical Contributions

This research provides:

1. **Axiomatic Foundation for Fair Preference Learning**: The first integration of Shapley value fairness axioms into LLM alignment, offering principled justification for fairness mechanisms.

2. **Efficient Shapley Approximation for Preference Data**: Novel gradient-based approximation techniques adapted for preference learning settings.

3. **Hierarchical Intersectionality Framework**: Practical approach to handling intersectional demographic groups without combinatorial explosion.

### 3.3 Practical Impact

**For LLM Practitioners**: SW-DPO provides a drop-in replacement for standard DPO training that automatically addresses demographic disparities without manual fairness constraint tuning.

**For Recommender Systems**: The methodology extends directly to collaborative filtering settings where user group fairness is critical.

**For Robotics and Control**: Preference-based robot learning can incorporate SW-DPO to ensure equitable performance across user populations.

**For Policy and Governance**: Axiomatically-grounded fairness provides clearer justification for regulatory compliance and ethical AI deployment.

### 3.4 Limitations and Future Work

**Current Limitations**:
- Requires demographic labels during training (not inference)
- Hierarchical grouping design requires domain expertise
- Does not address fairness in generated content, only preference learning

**Future Directions**:
- Unsupervised demographic discovery for unlabeled datasets
- Extension to continuous demographic attributes
- Integration with content-level fairness constraints
- Theoretical analysis of fairness-accuracy Pareto frontier

### 3.5 Broader Impact

By establishing principled foundations for fair preference learning, this research contributes to the broader goal of developing AI systems that serve all populations equitably. The axiomatic grounding in cooperative game theory provides a framework for reasoning about fairness that transcends specific applications, offering a template for principled fairness integration across machine learning domains.