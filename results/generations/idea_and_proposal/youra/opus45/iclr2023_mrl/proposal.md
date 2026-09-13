# Research Proposal: Efficient Information-Theoretic Shapley Decomposition for Interpretable Multimodal Contribution Analysis

## 1. Introduction

### 1.1 Background

Multimodal machine learning has emerged as a transformative paradigm, enabling systems to learn from diverse data sources such as vision, language, audio, and sensor data. The fundamental premise is that different perceptual modalities can inform and complement each other, grounding abstract phenomena in more robust and generalizable representations. Recent advances in multimodal models—from vision-language transformers to audio-visual speech recognition systems—have demonstrated remarkable capabilities across domains including sentiment analysis, visual question answering, and autonomous navigation.

However, despite these empirical successes, a critical gap persists in our understanding of *how* different modalities contribute to learned representations. Current attribution methods, including attention weights and gradient-based approaches, provide limited insight into the nature of modality interactions. Specifically, these methods cannot distinguish whether modalities provide unique information unavailable from other sources, share redundant content that could be obtained from any single modality, or create emergent synergistic effects that arise only from their combination. This interpretability gap has practical consequences: practitioners struggle to diagnose issues such as modality collapse (where one modality dominates learning), cannot systematically optimize modality combinations, and lack principled metrics for understanding cross-modal interactions.

The challenge is fundamentally information-theoretic. When a multimodal model processes visual and textual inputs to predict sentiment, the final representation encodes information from both sources. But what portion of this information is uniquely visual? What is shared between modalities? What emerges only from their interaction? Answering these questions requires moving beyond simple attribution scores toward a principled decomposition framework.

### 1.2 Research Objectives

This research proposes **Efficient Information-Theoretic Shapley Decomposition (E-ITSD)**, a novel framework that combines permutation-sampled Shapley values with Partial Information Decomposition (PID) to provide interpretable metrics quantifying each modality's unique contribution, shared redundancy, and emergent synergy. Our specific objectives are:

1. **Develop a mathematically principled decomposition framework** that satisfies axiomatic fairness guarantees (efficiency, symmetry, null player properties) while providing interpretable contribution types.

2. **Design efficient computational methods** using learned null embeddings for valid counterfactual ablation and permutation sampling for tractable Shapley approximation.

3. **Validate the framework empirically** on established multimodal benchmarks, demonstrating both mathematical validity and practical diagnostic utility.

4. **Establish connections between E-ITSD metrics and model behavior**, showing that synergy scores correlate with cross-modal attention and that unique contribution dominance detects modality collapse.

### 1.3 Significance

This research addresses fundamental questions in multimodal representation learning identified by the research community: How do we identify useful properties of multimodal representations? How do different modalities contribute to the semantics of learned representations? What are the representation benefits of multimodal observations versus single modalities?

E-ITSD provides actionable diagnostics for multimodal model development. By decomposing contributions into unique, redundant, and synergistic components, practitioners can identify when modalities are underutilized (low unique contribution), when fusion is ineffective (high redundancy, low synergy), and when models exhibit unhealthy modality dominance. Beyond practical utility, E-ITSD offers theoretical insights into the information-theoretic structure of multimodal representations, advancing our understanding of cross-modal interactions.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Shapley Values for Modality Attribution

Let $\mathcal{M} = \{1, 2, \ldots, M\}$ denote the set of modalities and $v: 2^{\mathcal{M}} \rightarrow \mathbb{R}$ be a value function measuring model output (e.g., prediction confidence, representation quality) for any subset of modalities. The Shapley value for modality $i$ is:

$$\phi_i(v) = \sum_{S \subseteq \mathcal{M} \setminus \{i\}} \frac{|S|!(M - |S| - 1)!}{M!} \left[ v(S \cup \{i\}) - v(S) \right]$$

This formulation satisfies four axiomatic properties: **Efficiency** ($\sum_{i} \phi_i = v(\mathcal{M}) - v(\emptyset)$), **Symmetry** (interchangeable modalities receive equal attribution), **Null Player** (non-contributing modalities receive zero attribution), and **Linearity** (additivity across value functions).

#### 2.1.2 Partial Information Decomposition

While Shapley values quantify *how much* each modality contributes, they do not reveal *how* modalities contribute. Partial Information Decomposition (PID) addresses this by decomposing the mutual information $I(X_1, X_2; Y)$ between source variables $(X_1, X_2)$ and target $Y$ into:

$$I(X_1, X_2; Y) = \text{Uniq}(X_1) + \text{Uniq}(X_2) + \text{Red}(X_1, X_2) + \text{Syn}(X_1, X_2)$$

where $\text{Uniq}(X_i)$ is information uniquely provided by modality $i$, $\text{Red}$ is redundant information available from either modality, and $\text{Syn}$ is synergistic information emerging only from their combination.

We adopt the $I_{\text{broja}}$ measure (Bertschinger et al., 2014), which defines redundancy as the maximum information that can be extracted from either source individually:

$$\text{Red}(X_1, X_2) = \max_{Q \in \Delta_P} I_Q(X_1; Y)$$

where $\Delta_P$ is the set of distributions preserving marginals $P(X_1, Y)$ and $P(X_2, Y)$.

#### 2.1.3 E-ITSD Integration

E-ITSD integrates Shapley attribution with PID decomposition through a three-step causal mechanism:

**Step 1: Learned Null Ablation.** For each modality $i$, we learn a null embedding $\mathbf{e}_i^{\text{null}}$ that represents modality absence while maintaining in-distribution model behavior:

$$\mathbf{e}_i^{\text{null}} = \arg\min_{\mathbf{e}} \mathbb{E}_{x \sim \mathcal{D}} \left[ D_{\text{KL}}\left( f(x) \| f(x_{-i} \oplus \mathbf{e}) \right) + \lambda \|\mathbf{e}\|^2 \right]$$

where $f$ is the model, $x_{-i}$ denotes input with modality $i$ removed, and $\oplus$ denotes embedding substitution.

**Step 2: Permutation-Based Shapley Computation.** We approximate Shapley values using permutation sampling:

$$\hat{\phi}_i = \frac{1}{K} \sum_{k=1}^{K} \left[ v(S_{\pi_k}^i \cup \{i\}) - v(S_{\pi_k}^i) \right]$$

where $\pi_k$ is a random permutation and $S_{\pi_k}^i$ is the set of modalities preceding $i$ in permutation $\pi_k$. We use $K = 500$ samples based on convergence analysis.

**Step 3: PID Decomposition.** For each pair of modalities $(i, j)$, we compute PID components using the Shapley marginals as input distributions. The unique contribution of modality $i$ is:

$$U_i = \phi_i - \text{Red}(i, j) - \frac{1}{2}\text{Syn}(i, j)$$

For $M > 2$ modalities, we extend using the multivariate PID framework, computing pairwise decompositions and aggregating via weighted averaging.

### 2.2 Data Collection

We validate E-ITSD on established MultiBench benchmark datasets:

1. **CMU-MOSEI** (Multimodal Opinion Sentiment and Emotion Intensity): 23,453 video clips with language, visual, and acoustic modalities for sentiment analysis. This dataset tests E-ITSD on 3-modality fusion with continuous sentiment targets.

2. **AV-MNIST** (Audio-Visual MNIST): Paired audio and image data for digit classification. This controlled setting enables precise validation of decomposition properties with 2 modalities.

3. **MM-IMDb** (Multimodal IMDb): Movie plot summaries (text) and posters (image) for genre classification. This tests E-ITSD on vision-language fusion with multi-label targets.

4. **MOSI** (Multimodal Opinion Sentiment Intensity): Subset of CMU-MOSEI for focused sentiment analysis, enabling comparison with prior work.

For each dataset, we use standard train/validation/test splits and pre-trained multimodal models (late fusion and cross-attention architectures) to ensure reproducibility.

### 2.3 Algorithmic Implementation

**Algorithm 1: E-ITSD Computation**

```
Input: Multimodal model f, input sample x, modalities M, samples K
Output: Unique, Redundancy, Synergy scores for each modality

1. Learn null embeddings:
   For each i ∈ M:
     e_i^null ← optimize Eq. (3) using gradient descent
     
2. Compute Shapley values:
   Initialize φ[i] ← 0 for all i
   For k = 1 to K:
     π ← random_permutation(M)
     For i in π:
       S ← modalities preceding i in π
       x_S ← ablate_modalities(x, M \ S, null_embeddings)
       x_S∪i ← ablate_modalities(x, M \ (S ∪ {i}), null_embeddings)
       φ[i] ← φ[i] + (v(f(x_S∪i)) - v(f(x_S))) / K
       
3. Compute PID decomposition:
   For each pair (i, j) ∈ M × M:
     Compute I_broja redundancy Red(i,j)
     Compute synergy Syn(i,j) = I(i,j;Y) - φ[i] - φ[j] + Red(i,j)
     
4. Aggregate scores:
   For each i ∈ M:
     Unique[i] ← φ[i] - Σ_j Red(i,j)/(M-1) - Σ_j Syn(i,j)/(2(M-1))
     Redundancy[i] ← Σ_j Red(i,j) / (M-1)
     Synergy[i] ← Σ_j Syn(i,j) / (M-1)
     
Return Unique, Redundancy, Synergy
```

### 2.4 Experimental Design

#### 2.4.1 Experiment 1: Decomposition Validity (Primary)

**Objective:** Verify that E-ITSD produces mathematically valid decompositions.

**Protocol:** For each dataset and 100 randomly sampled test instances, compute E-ITSD scores with 20 different random seeds. Measure:
- Decomposition sum error: $|\text{Unique}_i + \text{Red}_i + \text{Syn}_i - \phi_i| / |\phi_i|$
- Coefficient of variation (CV) across runs

**Success Criteria:** Sum error < 5%, CV < 10%

#### 2.4.2 Experiment 2: Convergence Analysis

**Objective:** Validate that permutation sampling converges with 500 samples.

**Protocol:** Compute Shapley values with $K \in \{50, 100, 200, 500, 1000, 2000\}$ samples. Plot convergence curves and measure variance reduction.

**Success Criteria:** CV < 5% at $K = 500$

#### 2.4.3 Experiment 3: Null Embedding Validation

**Objective:** Verify that learned null embeddings produce valid counterfactuals.

**Protocol:** Compare three ablation strategies: (a) zero ablation, (b) mean embedding, (c) learned null token. Measure distribution shift via KL divergence between original and ablated model outputs.

**Success Criteria:** Learned null produces lowest KL divergence

#### 2.4.4 Experiment 4: Interpretability Correlation

**Objective:** Validate that E-ITSD synergy scores correlate with cross-modal attention.

**Protocol:** On CMU-MOSEI with cross-attention models, extract attention weights between modality pairs. Compute Spearman correlation between synergy scores and attention weights.

**Success Criteria:** Spearman $\rho > 0.5$, $p < 0.05$

#### 2.4.5 Experiment 5: Modality Collapse Detection

**Objective:** Demonstrate E-ITSD's diagnostic utility for detecting modality dominance.

**Protocol:** Train models with artificially induced modality collapse (by reducing one modality's learning rate). Measure whether E-ITSD unique contribution scores detect dominance (threshold: Unique > 0.7 × Total). Validate against single-modality ablation performance.

**Success Criteria:** Detection accuracy > 90%

#### 2.4.6 Experiment 6: Comparison with Baselines

**Objective:** Compare E-ITSD against existing attribution methods.

**Baselines:**
- MM-SHAP (Shapley without PID)
- Attention-based attribution
- Gradient-based attribution (Integrated Gradients)
- SHAPE scores

**Metrics:**
- Faithfulness: correlation between attribution and ablation performance drop
- Stability: consistency across similar inputs
- Interpretability: user study with ML practitioners (n=20)

### 2.5 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Decomposition Error | $\|U + R + S - \phi\| / \|\phi\|$ | < 5% |
| Coefficient of Variation | $\sigma / \mu$ across runs | < 10% |
| Spearman Correlation | Rank correlation with attention | > 0.5 |
| Detection Accuracy | Correct modality collapse identification | > 90% |
| Faithfulness | Correlation with ablation performance | > 0.7 |

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome:** A validated E-ITSD framework that produces mathematically valid decompositions of modality contributions into unique, redundant, and synergistic components. We expect decomposition sum errors below 5% and coefficient of variation below 10% across all tested datasets and architectures.

**Secondary Outcomes:**

1. **Interpretability Insights:** We anticipate synergy scores will correlate significantly ($\rho > 0.5$) with cross-modal attention weights, providing empirical validation that E-ITSD captures meaningful cross-modal interactions.

2. **Diagnostic Utility:** E-ITSD will successfully detect modality collapse with >90% accuracy, providing practitioners with actionable diagnostics for model development.

3. **Comparative Advantages:** E-ITSD will demonstrate superior interpretability compared to existing methods, particularly in distinguishing redundant from synergistic contributions—a distinction unavailable from standard Shapley or attention-based methods.

4. **Computational Efficiency:** The permutation sampling approach will achieve stable estimates with 500 samples, making E-ITSD practical for models with 2-5 modalities.

### 3.2 Theoretical Contributions

E-ITSD advances multimodal representation learning theory by:

1. **Formalizing modality interaction types:** The unique/redundant/synergistic decomposition provides a principled vocabulary for discussing modality contributions, moving beyond vague notions of "complementarity."

2. **Connecting game theory and information theory:** By integrating Shapley values (fair attribution) with PID (information decomposition), E-ITSD bridges two foundational frameworks in a novel way.

3. **Establishing interpretability benchmarks:** The validation experiments establish quantitative criteria for evaluating multimodal attribution methods.

### 3.3 Practical Impact

**For Researchers:** E-ITSD provides tools for understanding multimodal representations, enabling systematic investigation of questions such as: Which modality combinations produce synergistic effects? How does fusion architecture affect information sharing?

**For Practitioners:** E-ITSD offers diagnostics for model development:
- Detecting modality collapse before deployment
- Identifying underutilized modalities
- Optimizing modality combinations for specific tasks

**For the Field:** By providing interpretable metrics, E-ITSD supports the broader goal of trustworthy AI, enabling stakeholders to understand how multimodal systems process information.

### 3.4 Limitations and Future Work

**Computational Constraints:** E-ITSD's complexity scales with modality count, limiting applicability to models with many modalities. Future work could explore hierarchical decomposition for scalability.

**PID Measure Sensitivity:** Results may depend on PID measure choice. We use $I_{\text{broja}}$ but acknowledge alternatives (e.g., $I_{\text{min}}$, $I_{\text{ccs}}$) may be preferable in some domains.

**Post-hoc Analysis:** E-ITSD operates post-training and cannot directly guide training. Future work could integrate E-ITSD objectives into training losses to promote desirable contribution patterns.

### 3.5 Conclusion

E-ITSD addresses a fundamental gap in multimodal machine learning: understanding how different modalities contribute to learned representations. By combining Shapley values with Partial Information Decomposition, E-ITSD provides interpretable metrics that distinguish unique, redundant, and synergistic contributions. Our comprehensive experimental design validates both mathematical properties and practical utility, establishing E-ITSD as a principled framework for multimodal interpretability. This work advances the field's understanding of modality interactions while providing actionable tools for model development and diagnosis.