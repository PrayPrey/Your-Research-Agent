# Research Proposal: Capability Readiness Probes: Predicting Emergent Abilities in Foundation Models via Circuit-Specific Activation Monitoring

## 1. Introduction

### 1.1 Background

Foundation models (FMs) have fundamentally transformed machine learning, demonstrating remarkable capabilities across language, vision, speech, and multimodal domains. Models such as GPT-4, LLaMA, and PaLM exhibit sophisticated behaviors including in-context learning, multi-step reasoning, and chain-of-thought problem solving. However, one of the most puzzling aspects of these models is the phenomenon of emergent capabilities—abilities that appear suddenly and unpredictably during training, often manifesting only after models reach certain scales or training durations.

Current understanding of capability emergence remains largely phenomenological. Researchers have documented that capabilities such as arithmetic reasoning, in-context learning, and factual recall appear to "emerge" at specific training checkpoints, transitioning from near-random performance to competent execution over relatively few training steps. This unpredictability presents significant challenges for both efficient model development and safety monitoring. Training large foundation models requires substantial computational resources, and the inability to anticipate when capabilities will emerge forces practitioners to rely on extensive post-hoc evaluation rather than informed training decisions.

Recent advances in mechanistic interpretability have begun to illuminate the internal computational structures underlying specific capabilities. Olsson et al. (2022) demonstrated that in-context learning corresponds to the development of "induction heads"—specific attention patterns that implement copying and pattern-matching operations. Similarly, research has identified circuits responsible for arithmetic operations, factual retrieval, and other capabilities. These findings suggest that capabilities do not emerge from nowhere but rather reflect the maturation of identifiable computational circuits within the model architecture.

Despite these mechanistic insights, a significant gap exists between understanding *what* circuits underlie capabilities and *predicting when* those capabilities will emerge during training. Current prediction methods, such as the loss-threshold approaches described by Du et al. (2024), rely on aggregate metrics that detect emergence only after it has occurred. This reactive approach limits the practical utility of emergence prediction for training optimization and safety monitoring.

### 1.2 Research Objectives

This research proposes **Capability Readiness Probes (CRPs)**—a novel framework that leverages circuit-specific activation patterns to predict capability emergence before it manifests on behavioral benchmarks. Our central hypothesis is:

> Under controlled training conditions with intermediate checkpoints available, if lightweight linear probes are trained on circuit-specific activation patterns (attention head coherence for in-context learning, MLP activation geometry for arithmetic, key-value patterns for factual recall), then capability emergence can be predicted earlier than loss-threshold methods by directly monitoring the maturation of known capability-relevant circuits during training, because specific computational circuits responsible for capabilities mature at trackable rates before behavioral manifestation on benchmarks.

Our specific objectives are:

1. **Develop and validate CRPs** that can distinguish pre-emergence from post-emergence model states with high accuracy (AUC > 0.8) using circuit-specific activation features.

2. **Quantify prediction lead time** by measuring the training steps between probe threshold crossing and benchmark emergence, targeting >5% of total training duration.

3. **Establish generalization scope** by testing CRPs across multiple capabilities (in-context learning, arithmetic, factual recall) and model families (Pythia, OLMo).

4. **Compare against baselines** to demonstrate practical improvement over existing loss-threshold prediction methods.

### 1.3 Significance

This research addresses a critical gap in foundation model understanding with both theoretical and practical implications. Theoretically, successful CRPs would provide empirical validation of circuit-capability correspondence theories, demonstrating that mechanistic interpretability findings can be operationalized for predictive purposes. Practically, earlier prediction of capability emergence would enable more efficient training decisions—potentially allowing practitioners to adjust learning rates, data mixtures, or training objectives based on circuit maturation signals rather than waiting for benchmark performance changes.

From a safety perspective, the ability to predict capability emergence before behavioral manifestation is particularly valuable. Dangerous capabilities could potentially be detected and addressed proactively rather than discovered through post-hoc evaluation. This aligns with the workshop's emphasis on understanding FMs to mitigate undesirable behaviors and improve alignment.

## 2. Methodology

### 2.1 Data Collection and Model Selection

**Model Families:** We will utilize two publicly available model families with extensive intermediate checkpoints:

- **Pythia Suite** (EleutherAI): Models ranging from 125M to 7B parameters, with 143 checkpoints per model saved throughout training on The Pile dataset.
- **OLMo Suite** (AI2): Models from 1B to 7B parameters with intermediate checkpoints, trained on the Dolma dataset.

These model families provide the temporal resolution necessary for tracking circuit maturation and enable cross-family generalization testing.

**Target Capabilities:** We focus on three capabilities with varying levels of mechanistic understanding:

1. **In-Context Learning (ICL):** Best-understood mechanistically; induction heads identified as causal circuits (Olsson et al., 2022). Serves as positive control.

2. **Basic Arithmetic:** Emerging mechanistic understanding; involves specific MLP layers and attention patterns for digit manipulation.

3. **Factual Recall:** Less mechanistically characterized; hypothesized to involve key-value memory patterns in middle layers.

**Benchmark Datasets:** For each capability, we will use established evaluation benchmarks:
- ICL: Few-shot classification tasks (e.g., SST-2, AG News with varying shot counts)
- Arithmetic: Grade-school math problems (GSM8K subset), basic addition/multiplication
- Factual Recall: LAMA probes, TriviaQA factual questions

### 2.2 Circuit-Specific Feature Extraction

We employ TransformerLens and custom extraction pipelines to obtain circuit-specific activation patterns from each checkpoint.

**For In-Context Learning (Induction Head Coherence):**

We compute induction head scores following Olsson et al. (2022). For each attention head $h$ in layer $l$, we measure the attention pattern's alignment with the induction pattern on repeated token sequences:

$$\text{InductionScore}_{l,h} = \frac{1}{|S|} \sum_{s \in S} \text{Attn}_{l,h}(s_t, s_{t-k})$$

where $S$ is a set of sequences containing repeated tokens, $s_t$ is the current token position, and $s_{t-k}$ is the position of the previous occurrence of the same token. We aggregate scores across identified induction heads to form a coherence vector $\mathbf{c}_{\text{ICL}} \in \mathbb{R}^{H}$ where $H$ is the number of candidate induction heads.

**For Arithmetic (MLP Activation Geometry):**

We extract MLP activations from layers identified as relevant for numerical processing. For input sequences containing arithmetic expressions, we compute:

$$\mathbf{a}_{\text{arith}} = \text{concat}\left[\text{MLP}_l(\mathbf{h}_l)\right]_{l \in L_{\text{arith}}}$$

where $L_{\text{arith}}$ is the set of arithmetic-relevant layers (identified through preliminary ablation studies). We then compute geometric features including activation magnitude, sparsity, and principal component projections:

$$\mathbf{f}_{\text{arith}} = \left[\|\mathbf{a}\|_2, \|\mathbf{a}\|_0 / d, \mathbf{a}^\top \mathbf{v}_1, \ldots, \mathbf{a}^\top \mathbf{v}_k\right]$$

where $\mathbf{v}_1, \ldots, \mathbf{v}_k$ are principal components computed from post-emergence checkpoints.

**For Factual Recall (Key-Value Patterns):**

We analyze attention patterns in middle layers during factual queries, computing:

$$\text{KVScore}_{l,h} = \text{cos}(\mathbf{k}_{l,h}^{\text{subject}}, \mathbf{v}_{l,h}^{\text{object}})$$

where keys at subject token positions are compared with values at object positions for known factual associations. The feature vector $\mathbf{f}_{\text{recall}}$ aggregates these scores across relevant heads.

### 2.3 Probe Architecture and Training

**Probe Design:** We employ lightweight linear probes to maintain interpretability and minimize overfitting risk:

$$p(\text{emerged} | \mathbf{f}) = \sigma(\mathbf{w}^\top \mathbf{f} + b)$$

where $\mathbf{f}$ is the circuit-specific feature vector, $\mathbf{w}$ are learned weights, $b$ is a bias term, and $\sigma$ is the sigmoid function.

**Training Procedure:**

1. **Label Assignment:** For each checkpoint $t$, we evaluate benchmark performance $P_t$. A checkpoint is labeled as "post-emergence" if $P_t > P_{\text{random}} + 2\sigma_{\text{random}}$, where $\sigma_{\text{random}}$ is the standard deviation of random baseline performance.

2. **Feature Extraction:** Extract circuit-specific features $\mathbf{f}_t$ from each checkpoint.

3. **Probe Training:** Train probes using binary cross-entropy loss with L2 regularization:

$$\mathcal{L} = -\sum_t \left[y_t \log p_t + (1-y_t)\log(1-p_t)\right] + \lambda \|\mathbf{w}\|_2^2$$

4. **Cross-Validation:** Use 5-fold cross-validation across checkpoints, ensuring temporal ordering is respected (no future leakage).

### 2.4 Prediction Lead Time Measurement

**Lead Time Definition:** For each capability and model, we define:

$$\text{LeadTime} = t_{\text{loss}} - t_{\text{probe}}$$

where $t_{\text{loss}}$ is the checkpoint at which loss-threshold methods (Du et al., 2024) predict emergence, and $t_{\text{probe}}$ is the checkpoint at which probe confidence first exceeds 0.8.

**Loss-Threshold Baseline:** Following Du et al. (2024), we implement the loss-threshold method that predicts emergence when validation loss crosses capability-specific thresholds derived from scaling law extrapolations.

**Normalized Lead Time:** To enable comparison across models with different training durations:

$$\text{NormalizedLeadTime} = \frac{t_{\text{loss}} - t_{\text{probe}}}{T_{\text{total}}} \times 100\%$$

where $T_{\text{total}}$ is the total number of training steps.

### 2.5 Experimental Design

**Experiment 1: Probe Validation (SH1)**
- *Objective:* Establish that CRPs can distinguish pre/post-emergence states
- *Design:* Train probes for each capability × model combination
- *Metrics:* AUC, precision, recall, F1 on held-out checkpoints
- *Success Criterion:* AUC > 0.8 for majority of combinations

**Experiment 2: Lead Time Quantification (SH3)**
- *Objective:* Measure prediction advantage over loss-threshold methods
- *Design:* Compare $t_{\text{probe}}$ vs $t_{\text{loss}}$ across all combinations
- *Metrics:* Lead time (steps), normalized lead time (%)
- *Statistical Test:* Wilcoxon signed-rank test, $\alpha = 0.05$
- *Success Criterion:* Mean normalized lead time > 5%, $p < 0.05$

**Experiment 3: Mechanism Validation (SH2)**
- *Objective:* Verify causal mechanism through monotonic confidence increase
- *Design:* Track probe confidence trajectories across training
- *Metrics:* Spearman correlation between checkpoint index and probe confidence
- *Success Criterion:* $\rho > 0.7$ for post-emergence trajectory

**Experiment 4: Cross-Model Transfer**
- *Objective:* Test generalization across model families
- *Design:* Train probes on Pythia, evaluate on OLMo (and vice versa)
- *Metrics:* Transfer AUC, fine-tuning efficiency
- *Success Criterion:* Transfer AUC > 0.7 with ≤10% fine-tuning data

### 2.6 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Probe AUC | Area under ROC curve for emergence classification | > 0.8 |
| Lead Time | Steps between probe and loss-threshold prediction | > 0 |
| Normalized Lead Time | Lead time as percentage of training duration | > 5% |
| Transfer AUC | AUC when applying probe to different model family | > 0.7 |
| Confidence Correlation | Spearman $\rho$ between training progress and probe confidence | > 0.7 |

### 2.7 Falsification Criteria

The hypothesis will be rejected if:
1. **Primary Failure:** Lead time ≤ 0 in >50% of capability × model combinations
2. **Mechanism Failure:** Probe AUC ≤ 0.65 on held-out checkpoints
3. **Generalization Failure:** Probes succeed only for ICL but fail for arithmetic and factual recall

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and supporting evidence from mechanistic interpretability literature, we anticipate the following outcomes:

**Primary Outcomes:**
1. CRPs will achieve AUC > 0.8 for in-context learning prediction, with slightly lower but still significant performance (AUC > 0.75) for arithmetic and factual recall due to less complete mechanistic characterization.

2. Mean normalized lead time will exceed 5% of training duration, with ICL showing the largest lead times (potentially 8-12%) due to the clear temporal separation between induction head formation and benchmark performance improvement documented by Olsson et al. (2022).

3. Probe confidence will show monotonic increase during the emergence transition period, validating the hypothesized causal mechanism of circuit maturation preceding behavioral manifestation.

**Secondary Outcomes:**
1. Cross-model transfer will succeed with moderate fine-tuning, suggesting that circuit maturation signatures share common features across architectures trained on similar data distributions.

2. Analysis of probe weights will reveal which specific circuit features are most predictive, providing interpretable insights into the emergence process.

### 3.2 Theoretical Impact

This research will contribute to the theoretical understanding of foundation models in several ways:

**Validation of Circuit-Capability Correspondence:** Successful CRPs would provide strong empirical evidence that mechanistic interpretability findings (e.g., induction heads for ICL) reflect genuine causal relationships rather than mere correlations. The ability to predict emergence from circuit features implies that circuits are not just associated with capabilities but are constitutive of them.

**Temporal Dynamics of Emergence:** By quantifying the lead time between circuit maturation and behavioral manifestation, this work will illuminate the temporal structure of emergence. This addresses a key gap in current understanding—we know capabilities emerge, but not the precise dynamics of how internal representations translate to external behavior.

**Generalization of Mechanistic Findings:** Testing across multiple capabilities will establish the scope of circuit-based prediction. If probes succeed for ICL but fail for other capabilities, this would suggest that current mechanistic understanding is capability-specific rather than reflecting general principles.

### 3.3 Practical Impact

**Training Efficiency:** Earlier prediction of capability emergence enables more informed training decisions. Practitioners could adjust hyperparameters, data mixtures, or compute allocation based on circuit maturation signals rather than waiting for benchmark evaluations. For expensive training runs, even a 5% lead time could translate to significant resource savings.

**Safety Monitoring:** The ability to predict capability emergence before behavioral manifestation is particularly valuable for safety-critical capabilities. Dangerous capabilities (e.g., deception, manipulation) could potentially be detected during training before they become fully functional, enabling proactive interventions.

**Interpretability Tools:** The CRP framework transforms mechanistic interpretability findings into practical monitoring tools. This bridges the gap between academic interpretability research and applied ML engineering, demonstrating concrete utility for mechanistic insights.

### 3.4 Limitations and Future Directions

**Current Limitations:**
- Requires prior mechanistic work to identify target circuits; novel capabilities without known circuits cannot be monitored
- Prediction granularity limited by checkpoint frequency
- Linear probes may miss complex nonlinear signatures of emergence

**Future Extensions:**
- Develop methods to discover capability-relevant circuits automatically, removing dependence on prior mechanistic analysis
- Extend to real-time monitoring during training rather than checkpoint-based evaluation
- Apply CRPs to safety-relevant capabilities such as deception or sycophancy
- Investigate whether CRPs can guide interventions to accelerate or suppress specific capability emergence

### 3.5 Broader Significance

This research exemplifies the workshop's goal of developing rigorous understanding of foundation models through careful experimentation. By operationalizing mechanistic interpretability findings for predictive purposes, we demonstrate that theoretical insights can yield practical tools. The CRP framework represents a step toward the broader goal of making foundation model training more predictable, efficient, and safe—addressing the fundamental challenge that "understanding of FMs lags far behind their extraordinary performance."

Success in this research would establish a new paradigm for foundation model monitoring: rather than treating models as black boxes evaluated only through behavioral benchmarks, we can leverage internal computational structure to anticipate and understand capability development. This shift from reactive to proactive understanding is essential as foundation models become increasingly powerful and widely deployed.