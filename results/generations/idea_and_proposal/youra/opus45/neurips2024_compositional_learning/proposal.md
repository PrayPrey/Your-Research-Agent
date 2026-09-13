# Research Proposal: Universal Composition Functor for Cross-Domain Compositional Generalization via Functorial Constraints on Foundation Model Primitives

## 1. Introduction

### 1.1 Background

Compositional learning represents one of the most fundamental challenges in artificial intelligence, inspired by the remarkable human ability to understand and generate infinitely complex ideas from a finite set of simpler concepts. This capacity for systematic composition—understanding "purple elephant" after learning "purple" and "elephant" separately—underlies human language acquisition, visual reasoning, and abstract thought. Despite significant advances in deep learning, achieving robust compositional generalization remains elusive for modern AI systems, particularly when confronting novel combinations of learned primitives in dynamic, real-world environments.

Recent research has demonstrated both the promise and limitations of current approaches. Lake and Baroni's Meta-Learning for Compositionality (MLC) achieves near-perfect performance (~99%) on benchmarks like SCAN and COGS, demonstrating that human-like systematicity is achievable through appropriate training regimes. However, these methods require domain-specific training and fail to transfer across domains without retraining, severely limiting their practical deployment in multi-domain environments. Similarly, vision-language models like TripletCLIP show promising compositional capabilities within their training domains but struggle with cross-domain transfer.

The fundamental tension in compositional learning lies between achieving high within-domain accuracy and enabling cross-domain generalization. Current methods optimize for one at the expense of the other: domain-specific approaches achieve excellent performance but lack transferability, while domain-agnostic methods sacrifice accuracy for generality. This gap represents a critical barrier to deploying compositional AI systems in real-world applications where domains shift dynamically and retraining is impractical.

### 1.2 Research Objectives

This research proposes to develop and validate a **Universal Composition Functor (UCF)**—a novel architecture that bridges the gap between within-domain compositional accuracy and cross-domain transfer. Our primary objectives are:

1. **Design a functorial composition mechanism** that enforces algebraic structure preservation across domains through category-theoretic constraints, enabling learned composition rules to transfer universally.

2. **Achieve dual performance targets**: ≥95% in-domain compositional accuracy (matching state-of-the-art domain-specific methods) AND ≥80% zero-shot cross-domain transfer (representing a 2x improvement over existing approaches).

3. **Empirically validate the causal mechanism** through systematic ablation studies, demonstrating that functorial constraints—not merely shared primitives—drive cross-domain generalization.

4. **Establish the first empirically validated universal composition method** bridging NLP, vision, and multimodal domains within a single unified framework.

### 1.3 Significance

This research addresses a critical gap identified in the compositional learning community: the absence of methods achieving both high compositional accuracy and cross-domain transfer. Success would have profound implications:

**Scientific Impact**: Validating category-theoretic constraints as a practical mechanism for compositional generalization would bridge theoretical frameworks (Gavranovic, 2024) with empirical machine learning, opening new research directions in algebraically-constrained neural networks.

**Practical Impact**: A universal composition method would enable deployment of compositional AI systems in dynamic, multi-domain environments without costly domain-specific retraining, with applications spanning machine translation, visual reasoning, robotics, and multimodal AI assistants.

**Methodological Impact**: The proposed functorial regularization framework provides a principled, model-agnostic approach compatible with existing foundation models, offering a transferable methodology across diverse research domains.

## 2. Methodology

### 2.1 Overall Architecture

The Universal Composition Functor (UCF) consists of three integrated components operating on frozen foundation model representations:

**Component 1: Primitive Extraction Module**
Frozen foundation models (CLIP ViT-L/14 for vision, T5-base for language) extract domain-specific primitives. For an input $x$ from domain $d$, we obtain:

$$p_d = \text{Encoder}_d(x) \in \mathbb{R}^{768}$$

where primitives represent compositionally meaningful units (objects, attributes, relations for vision; concepts, predicates, arguments for language).

**Component 2: Shared Primitive Space Alignment**
Learned projection networks $\phi_d$ map domain-specific primitives to a shared space:

$$\tilde{p} = \phi_d(p_d) \in \mathbb{R}^{768}$$

Alignment is enforced through concept anchor loss:

$$\mathcal{L}_{\text{align}} = \sum_{c \in \mathcal{C}} \sum_{d} \|\phi_d(p_d^c) - a_c\|^2$$

where $\mathcal{C}$ is a vocabulary of shared concept anchors $a_c$ representing domain-invariant semantic concepts.

**Component 3: Universal Composition Functor**
A transformer-based module $F$ composes aligned primitives:

$$F: (\tilde{p}_1, \tilde{p}_2) \rightarrow \tilde{p}_{1 \circ 2}$$

The functor is implemented as a 4-layer transformer with 512 hidden dimensions and 8 attention heads, taking concatenated primitive pairs as input and producing composed representations.

### 2.2 Functorial Regularization

The core innovation is the functorial constraint enforcing that composition operations preserve algebraic structure. For primitives $p_1, p_2$ and their composition $p_1 \circ p_2$, we enforce:

$$\mathcal{L}_{\text{functor}} = \|F(p_1 \circ p_2) - F(p_1) \otimes F(p_2)\|^2$$

where $\otimes$ represents a learned bilinear composition operator in the output space. This constraint ensures that the functor preserves compositional relationships: composing then mapping equals mapping then composing.

The bilinear operator is parameterized as:

$$F(p_1) \otimes F(p_2) = W_{\otimes}[F(p_1); F(p_2)] + b_{\otimes}$$

where $W_{\otimes} \in \mathbb{R}^{768 \times 1536}$ and $b_{\otimes} \in \mathbb{R}^{768}$ are learned parameters.

### 2.3 Training Objective

The complete training objective combines three losses:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{comp}} + \lambda_{\text{align}}\mathcal{L}_{\text{align}} + \lambda_{\text{functor}}\mathcal{L}_{\text{functor}}$$

**Contrastive Composition Loss** ($\mathcal{L}_{\text{comp}}$):
Self-supervised learning of composition through contrastive objectives:

$$\mathcal{L}_{\text{comp}} = -\log \frac{\exp(\text{sim}(F(p_1, p_2), p_{1 \circ 2})/\tau)}{\sum_{n \in \mathcal{N}} \exp(\text{sim}(F(p_1, p_2), p_n)/\tau)}$$

where $\mathcal{N}$ contains negative samples (incorrect compositions), $\text{sim}(\cdot)$ is cosine similarity, and $\tau = 0.07$ is the temperature.

**Hyperparameters**: $\lambda_{\text{align}} = 0.1$, $\lambda_{\text{functor}} \in [0.01, 0.5]$ (tuned via validation).

### 2.4 Data Collection and Preprocessing

**Training Domains**:

1. **NLP Domain (SCAN)**: Synthetic command-action pairs with systematic generalization splits. Primitives extracted via T5 encoder from command tokens.

2. **NLP Domain (COGS)**: Semantic parsing with lexical generalization. Primitives represent predicates and arguments.

3. **Vision Domain (MIT-States)**: Attribute-object compositions (e.g., "sliced apple"). CLIP extracts attribute and object primitives from images.

4. **Multimodal Domain (RefCOCO)**: Referring expression comprehension. Used exclusively for held-out cross-domain evaluation.

**Composition-Decomposition Pair Generation**:
- SCAN/COGS: Grammar-based decomposition of commands into primitive operations
- MIT-States: Scene graph parsing to extract (attribute, object) pairs
- Automatic mining with quality filtering (confidence threshold > 0.8)

**Data Splits**:
- Training: 70% of SCAN, COGS, MIT-States
- Validation: 15% for hyperparameter tuning
- In-domain Test: 15% with novel compositions
- Cross-domain Test: Full RefCOCO (zero-shot)

### 2.5 Experimental Design

**Experiment 1: In-Domain Compositional Generalization**

*Objective*: Validate UCF achieves ≥95% accuracy on standard compositional benchmarks.

*Setup*:
- Train UCF on SCAN (add jump split), COGS (lexical generalization)
- Compare against: MLC, Standard Transformer, LSTM baselines
- Metrics: Exact match accuracy on novel compositions

*Statistical Design*:
- 25 independent runs with different random seeds
- Paired t-test for significance (α = 0.05)
- Report: Mean ± Std Dev, 95% CI, Cohen's d

**Experiment 2: Cross-Domain Transfer**

*Objective*: Demonstrate ≥80% zero-shot transfer to held-out domains.

*Setup*:
- Train UCF on NLP (SCAN, COGS) + Vision (MIT-States)
- Test zero-shot on RefCOCO without fine-tuning
- Compare against: Domain-specific methods trained on same data, then evaluated on RefCOCO

*Metrics*:
- Cross-domain accuracy
- Transfer efficiency = (held-out accuracy) / (in-domain accuracy)
- Target: Transfer efficiency ≥ 2x baseline methods

**Experiment 3: Functorial Constraint Ablation**

*Objective*: Verify functorial constraints causally contribute to generalization.

*Setup*:
- UCF with $\lambda_{\text{functor}} = 0$ (ablated)
- UCF with $\lambda_{\text{functor}} \in \{0.01, 0.05, 0.1, 0.2, 0.5\}$
- Measure: Novel composition accuracy, cross-domain transfer

*Success Criterion*: $\lambda_{\text{functor}} > 0$ outperforms $\lambda_{\text{functor}} = 0$ by ≥5% (p < 0.05)

**Experiment 4: Mechanism Decomposition**

*Objective*: Validate each step of the causal mechanism.

*Setup*:
- H-M1 (Primitive Quality): Measure primitive compositionality via linear probing
- H-M2 (Alignment Quality): Measure cross-domain primitive similarity for shared concepts
- H-M3 (Functor Effectiveness): Measure composition consistency across domains

*Metrics*:
- Primitive compositionality score (linear separability of compositions)
- Cross-domain alignment correlation
- Composition consistency: $\|F_d(p_1, p_2) - F_{d'}(p_1, p_2)\|$ for same concepts across domains

### 2.6 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| In-Domain Accuracy | Exact match on novel compositions within training domains | ≥95% |
| Cross-Domain Accuracy | Exact match on held-out domain (RefCOCO) | ≥80% |
| Transfer Efficiency | Cross-domain / In-domain accuracy ratio | ≥2x baselines |
| Functorial Improvement | Accuracy gain from $\lambda_{\text{functor}} > 0$ | ≥5% |
| Composition Consistency | Cross-domain functor output similarity | >0.9 cosine |

### 2.7 Falsification Criteria

The hypothesis will be **rejected** if:
1. In-domain accuracy ≤85% (>15% below SOTA)
2. $\lambda_{\text{functor}}$ ablation shows no significant difference (p > 0.1)
3. Cross-domain accuracy ≤60% OR transfer efficiency ≤1.0x
4. Domain-specific methods outperform UCF on ALL metrics

### 2.8 Implementation Details

**Computational Resources**:
- Training: 4× NVIDIA A100 GPUs, ~48 hours per full training run
- Inference: Single GPU, <200ms per composition

**Software Stack**:
- PyTorch 2.0 with mixed-precision training
- HuggingFace Transformers for foundation models
- Custom functorial regularization module

**Reproducibility**:
- Fixed random seeds across all experiments
- Public code release with configuration files
- Detailed hyperparameter documentation

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcomes**:

1. **In-Domain Performance**: We expect UCF to achieve 95-97% accuracy on SCAN and COGS compositional splits, within 3-5% of MLC's 99% performance. This slight gap is acceptable given UCF's additional cross-domain transfer capability.

2. **Cross-Domain Transfer**: We anticipate 80-85% zero-shot accuracy on RefCOCO, representing approximately 2x improvement over domain-specific baselines (~40% when applied cross-domain without fine-tuning).

3. **Functorial Constraint Validation**: Ablation studies should demonstrate 5-10% accuracy improvement from functorial regularization, with optimal $\lambda_{\text{functor}}$ around 0.1-0.2.

**Secondary Outcomes**:

4. **Mechanism Insights**: We expect to identify which aspects of compositional structure transfer most readily across domains (likely attribute-object compositions) versus those requiring domain-specific adaptation (complex relational compositions).

5. **Scaling Analysis**: Preliminary analysis of how UCF performance scales with primitive vocabulary size and functor capacity.

### 3.2 Scientific Impact

**Theoretical Contributions**:
- First empirical validation of category-theoretic constraints for compositional generalization
- Evidence for universal compositional structure across NLP and vision domains
- Framework connecting algebraic structure preservation to neural network generalization

**Methodological Contributions**:
- Functorial regularization as a general technique for structure-preserving learning
- Multi-domain training protocol for compositional generalization
- Evaluation framework for cross-domain compositional transfer

### 3.3 Practical Impact

**Near-Term Applications**:
- Multimodal AI assistants capable of compositional reasoning across text and images
- Cross-lingual transfer for low-resource language understanding
- Robotic systems that generalize manipulation skills to novel object combinations

**Long-Term Vision**:
- Foundation for continual compositional learning in dynamic environments
- Building block for artificial general intelligence with human-like systematicity
- Enabling compositional reasoning in domains beyond current foundation model coverage

### 3.4 Limitations and Future Directions

**Known Limitations**:
- Concept anchor vocabulary may not cover all primitive types
- Single functor assumption may be restrictive for highly diverse composition types
- Computational overhead compared to domain-specific methods

**Future Research Directions**:
1. Extension to continual learning with dynamic primitive vocabularies
2. Hierarchical functors for multi-level compositional structure
3. Application to reinforcement learning for compositional skill transfer
4. Theoretical analysis of functorial constraint convergence properties

### 3.5 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Phase 1 | Months 1-3 | Implementation, data preparation, baseline reproduction |
| Phase 2 | Months 4-6 | UCF training, in-domain evaluation |
| Phase 3 | Months 7-9 | Cross-domain experiments, ablation studies |
| Phase 4 | Months 10-12 | Analysis, paper writing, code release |

This research represents a significant step toward universal compositional learning, bridging the gap between domain-specific excellence and cross-domain generalization that has long challenged the field.