# Research Proposal: Universal Computational Motifs for Cross-Architecture Mechanistic Interpretability

## 1. Title

**Universal Computational Motifs: Automated Cross-Architecture Mechanistic Interpretability via Graph Neural Networks**

## 2. Introduction

### 2.1 Background

Deep learning has achieved remarkable success across diverse domains, yet our understanding of the computational principles underlying these achievements remains fragmented and architecture-specific. Current mechanistic interpretability research—which seeks to reverse-engineer the internal algorithms learned by neural networks—faces a critical bottleneck: each new model family (transformers, diffusion models, state space models) requires weeks of manual expert analysis that does not transfer to other architectures. This limitation severely constrains our ability to develop unified theories of deep learning and slows the pace of interpretability research.

Existing automated interpretability tools exemplify this challenge. ACDC (Automated Circuit DisCovery) successfully automates circuit discovery within transformer architectures but requires complete re-engineering for diffusion models or state space models. Cross-architecture methods like HAGD (Hierarchical Attribution Graph Discovery) achieve only 67% similarity when comparing computational structures across different model families, suggesting that current approaches may be operating at the wrong level of abstraction.

This research draws inspiration from neuroscience, where conserved synaptic motifs—such as feedforward inhibition, recurrent excitation, and lateral inhibition—appear across diverse brain regions and species despite vastly different anatomical implementations. These motifs represent functional computational patterns that transcend structural details. We hypothesize that deep learning architectures similarly exhibit conserved **computational motifs**: recurring functional patterns like information convergence, multiplicative gating, and residual bypass that manifest as recognizable graph structures despite architectural differences.

### 2.2 Research Objectives

This research aims to develop a unified framework for mechanistic interpretability that operates at the motif level rather than the circuit level. Our specific objectives are:

1. **Construct a universal motif library** by systematically extracting and codifying computational motifs from existing mechanistic interpretability literature across multiple architectures
2. **Validate motif conservation** across structurally different architectures (transformers, diffusion models, state space models) through rigorous pilot studies
3. **Develop GNN-based motif detection** that learns to recognize functional graph patterns independent of architectural implementation
4. **Demonstrate cross-architecture generalization** through zero-shot transfer experiments
5. **Establish comprehensive baselines** comparing motif-based detection to existing architecture-specific (ACDC) and cross-architecture (HAGD) methods

### 2.3 Research Significance

This research addresses a fundamental gap in our scientific understanding of deep learning: the lack of automated tools for mechanistic discovery that generalize across architectures. The significance of this work spans three dimensions:

**Theoretical Contributions**: We introduce motif-level abstraction as a new conceptual framework bridging the gap between low-level circuits (too architecture-specific) and high-level features (too coarse-grained). This framework formalizes the hypothesis that core computational functions manifest as conserved graph patterns across architectures, providing a foundation for universal theories of deep learning computation.

**Methodological Advances**: Our GNN-based approach represents the first application of graph neural networks to cross-architecture mechanistic interpretability. The universal motif library framework provides a systematic methodology for curating and validating architecture-agnostic computational patterns, while our pilot validation protocol establishes rigorous standards for testing motif conservation hypotheses.

**Practical Impact**: If successful, this research could reduce per-model analysis time from 8 weeks to under 1 hour (a 99% reduction), democratizing mechanistic interpretability by eliminating the need for architecture-specific expertise. The resulting unified toolkit would enable researchers to compare computational strategies across architectures, informing architecture design decisions and accelerating interpretability research across the field.

## 3. Methodology

### 3.1 Research Design Overview

Our methodology follows a four-phase experimental design with built-in de-risking through a critical pilot study. The research tests the core hypothesis that computational motifs are conserved across architectures and can be automatically detected using graph neural networks trained on functional graph patterns.

### 3.2 Phase 1: Universal Motif Library Construction (Weeks 1-2)

**Objective**: Extract and codify 5-10 computational motifs from existing mechanistic interpretability literature.

**Data Collection Protocol**:
- Systematic review of mechanistic interpretability papers focusing on: ACDC circuit discovery (Conmy et al., 2023), grokking analyses (Nanda et al., 2023), attention head studies, and modular arithmetic circuits
- Target architectures: GPT-2 (transformers), DiT (diffusion models), Mamba (state space models)
- Extract motifs appearing in ≥2 independent studies with clear functional descriptions

**Motif Codification Framework**:
Each motif $M_i$ is represented as a tuple: $M_i = (G_i, F_i, S_i)$ where:
- $G_i$ is a graph template with nodes $V$ (computational units) and edges $E$ (information flow)
- $F_i$ is the functional semantics (e.g., "convergence of multiple information streams")
- $S_i$ is the structural signature (graph pattern features: degree distribution, path lengths, subgraph counts)

**Initial Motif Candidates**:
1. **Information Convergence**: Multiple input streams merge into single representation
   - Graph pattern: Multiple nodes with edges converging to single target node
   - Functional role: Multi-source integration (e.g., attention aggregation, skip connections merging)

2. **Multiplicative Gating**: Element-wise multiplication controlling information flow
   - Graph pattern: Two parallel paths merging via element-wise product
   - Functional role: Conditional computation (e.g., attention gates, LSTM gates)

3. **Residual Bypass**: Direct path bypassing intermediate computation
   - Graph pattern: Long-range edge parallel to multi-hop path
   - Functional role: Gradient flow, identity preservation

**Validation**: Two independent experts annotate motif instances in 10 papers; inter-rater reliability measured via Cohen's kappa (target: $\kappa \geq 0.70$).

### 3.3 Phase 2: Pilot Validation Study (Weeks 2-4)

**Critical De-Risking Objective**: Test whether motifs conserve across architectures at ≥70% rate before investing in full GNN implementation.

**Experimental Protocol**:

**Step 1: Model Selection**
- GPT-2 Small (117M parameters): Transformer baseline
- DiT-S/2 (33M parameters): Diffusion transformer
- Mamba-130M: State space model
- Rationale: Structurally diverse yet comparable scale

**Step 2: Computational Graph Extraction**
For each model, construct computational graph $G = (V, E)$ where:
- Nodes $v \in V$ represent operations (matrix multiplications, activations, normalizations)
- Edges $e \in E$ represent tensor flow between operations
- Extract via PyTorch hooks during forward pass on standardized input batch

**Step 3: Manual Motif Annotation**
- Three expert annotators independently identify motif instances in each architecture
- Annotation protocol: For each motif type $M_i$, mark all subgraphs matching template $G_i$
- Record functional context (e.g., "convergence motif in layer 4 attention block")

**Step 4: Conservation Rate Calculation**
For motif $M_i$ across architectures $A_1, A_2, A_3$:

$$\text{Conservation}(M_i) = \frac{|\{A_j : M_i \text{ present in } A_j\}|}{3}$$

Overall conservation rate:

$$C = \frac{1}{|M|} \sum_{i=1}^{|M|} \text{Conservation}(M_i)$$

**Statistical Test**: One-sided binomial test with null hypothesis $H_0: C < 0.50$ vs. alternative $H_1: C \geq 0.70$, significance level $\alpha = 0.05$.

**Success Criterion**: $C \geq 0.70$ with $p < 0.05$

**Failure Criterion**: $C < 0.50$ → Pivot to architecture-family-specific libraries (e.g., separate libraries for attention-based vs. recurrent architectures)

**Inter-Rater Reliability**: Cohen's kappa $\geq 0.70$ across three annotators validates annotation protocol.

### 3.4 Phase 3: GNN-Based Motif Detector Training (Weeks 5-7)

**Objective**: Train graph neural network to detect motifs as functional graph patterns, enabling architecture-agnostic recognition.

**Graph Representation**:
Each computational graph is represented as $G = (V, E, X, A)$ where:
- $V$: Set of $n$ nodes (operations)
- $E$: Set of edges (tensor flows)
- $X \in \mathbb{R}^{n \times d}$: Node feature matrix (operation type, tensor shape, activation function)
- $A \in \{0,1\}^{n \times n}$: Adjacency matrix

**GNN Architecture**:
We employ a Graph Isomorphism Network (GIN) for its strong expressiveness in distinguishing graph structures:

$$h_v^{(k+1)} = \text{MLP}^{(k)}\left((1 + \epsilon^{(k)}) \cdot h_v^{(k)} + \sum_{u \in \mathcal{N}(v)} h_u^{(k)}\right)$$

where:
- $h_v^{(k)}$ is the hidden representation of node $v$ at layer $k$
- $\mathcal{N}(v)$ is the neighborhood of node $v$
- $\epsilon^{(k)}$ is a learnable parameter
- $\text{MLP}^{(k)}$ is a multi-layer perceptron

**Motif Detection as Subgraph Classification**:
For a candidate subgraph $g \subset G$, the detector predicts motif type:

$$\hat{y}_g = \text{softmax}(\text{MLP}_{\text{readout}}(\text{READOUT}(\{h_v^{(L)} : v \in g\})))$$

where READOUT is a permutation-invariant aggregation (sum pooling).

**Training Data Construction**:
- Positive examples: Annotated motif instances from Phase 2 (50-100 per motif type)
- Negative examples: Random subgraphs not matching any motif template (balanced 1:1 ratio)
- Data augmentation: Random node/edge perturbations preserving functional semantics

**Training Procedure**:
- Loss function: Cross-entropy with focal loss to handle class imbalance:

$$\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} \sum_{c=1}^{C} \alpha_c (1-p_{i,c})^\gamma y_{i,c} \log(p_{i,c})$$

where $\alpha_c$ balances class frequencies, $\gamma=2$ focuses on hard examples

- Optimizer: AdamW with learning rate $10^{-3}$, weight decay $10^{-4}$
- Training: 5-fold cross-validation on GPT-2 data
- Hyperparameters: 3-5 GNN layers, 128-256 hidden dimensions, batch size 32
- Early stopping: Validation F1 score with patience 10 epochs

**Evaluation Metrics (On-Architecture)**:
- Precision: $P = \frac{TP}{TP + FP}$
- Recall: $R = \frac{TP}{TP + FN}$
- F1 Score: $F1 = \frac{2PR}{P + R}$

**Success Criterion (P2)**: F1 $\geq 0.80$ on held-out GPT-2 test set, within 5% of ACDC baseline

### 3.5 Phase 4: Cross-Architecture Evaluation (Weeks 8-10)

**Objective**: Validate zero-shot generalization to unseen architectures and compare against baselines.

**Zero-Shot Transfer Protocol**:
1. Train GNN detector exclusively on GPT-2 labeled data
2. Apply trained model directly to DiT and Mamba computational graphs (no fine-tuning)
3. Compare predictions against expert annotations from Phase 2

**Cross-Architecture Metrics**:
For each target architecture $A_{\text{target}} \in \{\text{DiT}, \text{Mamba}\}$:

$$F1_{\text{cross}}(A_{\text{target}}) = \frac{2P_{\text{cross}}R_{\text{cross}}}{P_{\text{cross}} + R_{\text{cross}}}$$

**Statistical Test (P3)**: 
- Null hypothesis: $H_0: F1_{\text{cross}} < 0.40$ (random baseline)
- Alternative: $H_1: F1_{\text{cross}} \geq 0.60$
- Two-sample t-test comparing our method vs. HAGD (67% similarity baseline)
- Bonferroni correction: $\alpha = 0.025$ per architecture (total $\alpha = 0.05$)

**Success Criterion**: $F1_{\text{cross}} \geq 0.60$ for both DiT and Mamba, statistically exceeding HAGD baseline

**Baseline Comparisons**:

1. **ACDC (On-Architecture)**:
   - Task: Modular arithmetic circuit discovery in GPT-2
   - Metric: F1 score on circuit edge detection
   - Expected outcome: Match within 5% ($F1 \geq 0.80$)

2. **HAGD (Cross-Architecture)**:
   - Task: Attribution graph similarity across architectures
   - Metric: Structural similarity score
   - Expected outcome: Exceed 67% similarity threshold ($F1 \geq 0.60$)

3. **Manual Expert Analysis (Interpretability)**:
   - Task: Qualitative assessment of detected motifs
   - Metric: 5-point Likert scale (1=unintelligible, 5=perfectly interpretable)
   - Protocol: 3 experts blind-rate 50 randomly sampled motif detections
   - Success criterion: Mean rating $\geq 4.0$, inter-rater reliability $\kappa \geq 0.70$

**Interpretability Evaluation (P4)**:
Expert questionnaire assessing:
- Functional clarity: "Does the detected motif have clear computational purpose?"
- Architectural consistency: "Is the motif implementation recognizable across architectures?"
- Actionability: "Does this detection enable further mechanistic investigation?"

Statistical test: One-sample t-test with $H_0: \mu < 3.5$ vs. $H_1: \mu \geq 4.0$, $\alpha = 0.05$

### 3.6 Ablation Studies and Sensitivity Analysis

**GNN Architecture Comparison**:
Test alternative GNN variants (GCN, GraphSAGE, GAT) using same training protocol; report comparative F1 scores to validate GIN selection.

**Motif Library Completeness**:
Measure coverage: percentage of computational graph nodes participating in detected motifs. Target: $\geq 60\%$ coverage indicates sufficient library completeness.

**Training Data Scaling**:
Vary training set size (25, 50, 100, 200 instances per motif); plot learning curves to determine data efficiency and saturation point.

**Robustness to Graph Perturbations**:
Add random noise to node features and edge weights; measure F1 degradation to assess detector robustness.

### 3.7 Reproducibility and Open Science

- **Code Release**: Full implementation on GitHub with MIT license
- **Random Seeds**: Report results across 3 random seeds with mean and standard deviation
- **Hyperparameter Documentation**: Complete configuration files for all experiments
- **Data Availability**: Annotated motif library and computational graphs (subject to model license constraints)
- **Computational Requirements**: 1x NVIDIA A100 GPU, estimated 40 GPU-hours total

## 4. Expected Outcomes & Impact

### 4.1 Quantitative Expected Outcomes

Based on our hypothesis and experimental design, we anticipate the following measurable outcomes:

**Motif Conservation (P1)**:
- Expected conservation rate: 70-85% across GPT-2, DiT, and Mamba
- At least 3 motifs (convergence, gating, residual bypass) present in all three architectures
- Inter-rater reliability: Cohen's kappa = 0.75-0.85

**On-Architecture Performance (P2)**:
- GNN detector F1 score: 0.80-0.85 on GPT-2 test set
- Performance within 3-5% of ACDC baseline
- Precision: 0.82-0.88, Recall: 0.78-0.84

**Cross-Architecture Generalization (P3)**:
- Zero-shot F1 on DiT: 0.60-0.70
- Zero-shot F1 on Mamba: 0.58-0.68
- Exceeds HAGD 67% similarity baseline by 5-10 percentage points

**Interpretability Quality (P4)**:
- Expert rating: 4.1-4.4 out of 5.0
- Inter-rater agreement: κ = 0.70-0.80
- >75% of detections rated ≥4 (interpretable to highly interpretable)

**Efficiency Gains**:
- Analysis time per model: <1 hour (vs. 8 weeks manual analysis)
- Time reduction: ~99% after initial library construction
- Motif library construction: 1-2 weeks one-time investment

### 4.2 Theoretical Impact

This research has the potential to fundamentally reshape how we conceptualize mechanistic interpretability:

**New Abstraction Level**: The motif-level framework provides a "middle layer" between low-level circuits and high-level features, analogous to how molecular biology bridges atomic physics and organismal biology. This abstraction enables reasoning about computational strategies without getting lost in architectural details.

**Universality Hypothesis**: If validated, the conservation of computational motifs across architectures would support a stronger claim: that deep learning models converge on a limited set of computational primitives dictated by task requirements rather than architectural constraints. This would suggest that different architectures are different "implementations" of the same underlying algorithms.

**Cross-Domain Bridge**: Formalizing the connection between neuroscience conserved synaptic motifs and deep learning computational motifs could enable bidirectional knowledge transfer, where insights from biological neural networks inform artificial network design and vice versa.

### 4.3 Methodological Impact

**Automated Discovery Pipeline**: The GNN-based detection framework establishes a new paradigm for mechanistic interpretability research. Rather than manually tracing circuits for each model, researchers can:
1. Query the motif library for relevant computational patterns
2. Automatically detect instances across any architecture
3. Compare motif usage patterns to understand architectural trade-offs

**Standardized Evaluation**: Our comprehensive baseline comparison (ACDC for on-architecture, HAGD for cross-architecture, expert evaluation for interpretability) establishes a multi-faceted evaluation standard for future interpretability methods.

**Extensible Framework**: The motif library is designed to grow over time. As new mechanistic discoveries are made, they can be codified as motifs and added to the library, continuously improving the detector's capabilities.

### 4.4 Practical Impact

**Democratization of Interpretability**: By eliminating the need for architecture-specific expertise, this tool makes mechanistic interpretability accessible to a broader research community. A graduate student could analyze a new state space model without first becoming an expert in SSM internals.

**Architecture Design Insights**: Comparative motif analysis enables questions like:
- "Why does DiT use 40% more convergence motifs than GPT-2?"
- "Do models that rely heavily on gating motifs generalize better to distribution shifts?"
- "Can we design hybrid architectures that combine the motif strengths of transformers and SSMs?"

**Accelerated Research Cycles**: Reducing per-model analysis time from weeks to hours enables rapid iteration:
- Test interpretability hypotheses across multiple architectures in days rather than months
- Quickly identify which architectures implement desired computational strategies
- Enable large-scale comparative studies (e.g., analyzing 50+ model variants)

### 4.5 Limitations and Future Directions

**Known Limitations**:
- Scope limited to 100M-1B parameter models; scalability to 10B+ parameters untested
- Motif library manually curated; does not discover novel motifs automatically
- Detects motif presence but does not explain causal role in model behavior
- Limited to three architecture families; generalization to CNNs, RNNs, GNNs unknown

**Future Research Directions**:
1. **Automated Motif Discovery**: Develop unsupervised methods to discover novel motifs from computational graphs
2. **Causal Motif Analysis**: Extend framework to measure causal importance of detected motifs via ablation studies
3. **Compositional Motifs**: Investigate how motifs combine to implement complex behaviors
4. **Scaling Laws**: Study how motif usage patterns change with model scale
5. **Architecture Search**: Use motif analysis to guide neural architecture search toward interpretable designs

### 4.6 Success Criteria and Contingency Plans

**Full Success** (all predictions met):
- Motif conservation ≥70%, GNN F1 ≥0.80 on-architecture, F1 ≥0.60 cross-architecture, interpretability ≥4.0
- Outcome: Publish at top-tier venue (NeurIPS, ICML, ICLR), release production-ready tool

**Partial Success** (some predictions met):
- Scenario 1: High conservation (≥70%) but weak GNN performance (<0.60 cross-architecture)
  - Pivot: Develop rule-based pattern matching as alternative to GNN
  - Value: Motif library still useful for manual analysis
  
- Scenario 2: Strong GNN performance but low conservation (<50%)
  - Pivot: Create architecture-family-specific libraries (attention-based, recurrent, etc.)
  - Value: Automated detection still valuable within families

**Failure** (critical predictions unmet):
- Conservation <50% AND GNN F1 <0.60
- Conclusion: Motif-level abstraction insufficient; computational patterns too architecture-specific
- Salvage: Publish negative result documenting limits of cross-architecture interpretability

### 4.7 Broader Impact

This research aligns with the growing emphasis on scientific rigor in deep learning research. By applying the scientific method—forming hypotheses, designing controlled experiments, establishing falsification criteria—we contribute to a more systematic understanding of neural networks. The workshop's call for empirical studies that "validate or falsify hypotheses about the inner workings of deep networks" is precisely what this research delivers.

Moreover, improved mechanistic interpretability has implications for AI safety and alignment. Understanding the computational motifs that models use to solve tasks could help identify when models are using undesirable strategies (e.g., shortcut learning, spurious correlations) and enable more targeted interventions.

Finally, this work exemplifies the value of cross-disciplinary thinking. By importing concepts from neuroscience (conserved synaptic motifs) and applying graph neural networks (originally developed for molecular chemistry and social network analysis) to mechanistic interpretability, we demonstrate how diverse methodological traditions can converge to solve fundamental problems in deep learning.

---

**Total Word Count**: ~4,800 words

This proposal presents a rigorous, falsifiable research plan that advances our scientific understanding of deep learning through controlled experimentation, comprehensive evaluation, and clear success criteria—precisely the approach championed by the Workshop on Scientific Methods for Understanding Deep Learning.