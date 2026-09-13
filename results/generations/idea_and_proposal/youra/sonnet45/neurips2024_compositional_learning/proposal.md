# Research Proposal: Schema-Guided Multi-Modal Compositional Transfer for Cross-Domain Generalization

## 1. Title

**Schema-Guided Multi-Modal Compositional Transfer: Universal Operators for Cross-Domain Generalization in Foundation Models**

## 2. Introduction

### 2.1 Background

Compositional learning—the ability to understand and generate complex concepts from simpler building blocks—represents a fundamental capability that distinguishes human cognition from current artificial intelligence systems. While humans effortlessly transfer compositional understanding across domains (e.g., applying the concept of "combination" from "red cup" in vision to "loud sound" in audio), state-of-the-art foundation models struggle with such cross-domain compositional generalization. This limitation severely constrains their adaptability to new modalities and dynamic real-world distributions.

Recent advances have demonstrated remarkable progress in isolated aspects of this challenge. Mirage (Noviello et al., 2025) achieves >99% compositional accuracy on the SCAN benchmark through neuroscience-inspired dual-process models with explicit schemas, validating that structured compositional representations enable systematic generalization. Simultaneously, cross-modal learning approaches like SMSA (Weng et al., 2025) demonstrate that multi-modal semantic distillation can preserve associations across modalities through cross-modal attention mechanisms. However, a critical gap persists: no existing method demonstrates transferable compositional *operators* across fundamentally different modalities such as vision, language, audio, and robotics.

This research addresses a fundamental question at the intersection of compositional learning and foundation model capabilities: **Can abstract composition rules be factorized from modality-specific content to enable zero-shot cross-domain compositional transfer?** Drawing on hierarchical predictive coding from cognitive neuroscience, we hypothesize that compositional learning can be decomposed into domain-invariant schemas (universal operators such as binding, sequential composition, and hierarchical structuring) and modality-specific primitives (adapter-based feature representations).

### 2.2 Research Objectives

The primary objectives of this research are:

1. **Develop a schema-guided compositional transfer framework** that factorizes compositional learning into universal operators and modality-specific primitives, enabling cross-domain generalization without full model retraining.

2. **Empirically validate the existence of universal compositional operators** by demonstrating that schemas learned from vision+language data can transfer to held-out modalities (audio, robotics) with minimal adaptation.

3. **Establish the causal mechanism** linking multi-modal training, operator specialization in attention heads, schema formation, and cross-domain transfer performance.

4. **Quantify transfer efficiency** by measuring compositional performance on novel modality combinations relative to in-domain performance and baseline approaches.

### 2.3 Research Significance

This research makes several significant contributions to compositional learning and foundation model development:

**Theoretical Contribution:** We provide the first framework explicitly factorizing compositional learning into domain-invariant schemas and modality-specific primitives, grounded in hierarchical predictive coding from cognitive neuroscience. This addresses the fundamental question of whether compositional operators are universal or modality-specific—a question with profound implications for understanding both biological and artificial intelligence.

**Methodological Contribution:** We introduce operator-specialized multi-head cross-modal attention with operator-level pooling as a concrete mechanism for learning abstract composition operators from multi-modal demonstrations. The two-stage training procedure (primitive extraction → schema learning → transfer validation) enables modular transfer without end-to-end retraining, offering a practical path toward efficient multi-modal deployment.

**Practical Impact:** Successful validation would enable foundation models to adapt to new modalities with orders of magnitude less data (1K samples vs. full retraining), dramatically reducing computational costs and enabling rapid deployment across diverse applications including robotics, audio processing, and emerging modalities.

**Alignment with Workshop Themes:** This research directly addresses multiple workshop foci: (1) understanding contexts where foundation models excel in compositional generalization, (2) developing transferable compositional learning methods compatible with existing models, (3) investigating the relationship between modularity and compositional generalization, and (4) extending compositional strategies toward continual learning through efficient adaptation mechanisms.

## 3. Methodology

### 3.1 Research Design Overview

We employ a mixed-methods approach combining controlled experiments, causal analysis through systematic ablations, and comparative evaluation against baselines. The research follows a three-phase design:

**Phase 1:** Multi-modal schema learning from vision+language data
**Phase 2:** Held-out modality transfer with frozen schemas
**Phase 3:** Mechanistic analysis and comparative evaluation

### 3.2 Data Collection and Preparation

#### 3.2.1 Training Data Composition

Our multi-modal training dataset comprises approximately 1 million samples designed to provide diverse compositional coverage:

- **COCO Dataset:** 500,000 image-caption pairs providing grounded vision-language compositions
- **Visual Genome:** 100,000 samples with rich scene graphs capturing hierarchical compositional structure
- **SCAN Benchmark:** 20,000 language-only compositional examples for systematic generalization
- **Compositional Augmentation:** 360,000 synthetically generated samples ensuring balanced operator distribution

The compositional augmentation strategy generates samples targeting three operator types:

**Binding Operator (target: 33% of augmented data):**
- Vision: Attribute-object combinations (e.g., "red cup" + "blue cup" → "red plate")
- Language: Adjective-noun bindings with systematic recombination

**Sequential Operator (target: 33% of augmented data):**
- Vision: Action sequences in video frames
- Language: Command compositions ("jump twice" + "turn left" → "jump twice and turn left")

**Hierarchical Operator (target: 34% of augmented data):**
- Vision: Part-whole relationships from scene graphs
- Language: Nested structures ("the cat on the mat in the room")

#### 3.2.2 Held-Out Modality Data

For transfer validation, we prepare two held-out modalities:

**Audio Domain (1,000 training samples, 5,000 test samples):**
- Environmental sound compositions (ESC-50 extended)
- Compositional structure: sound source + acoustic property + temporal pattern
- Example: "loud dog barking twice" → novel combinations of intensity, source, pattern

**Robotics Domain (1,000 training samples, 5,000 test samples):**
- Manipulation task compositions (RLBench subset)
- Compositional structure: object + action + spatial relation
- Example: "grasp red block above blue block" → novel object-action-relation combinations

### 3.3 Model Architecture

#### 3.3.1 Base Foundation Model

We utilize a Transformer encoder-decoder architecture with 350M parameters as the frozen base model. This provides:
- Pre-trained representations across vision and language modalities
- Sufficient capacity for complex compositional patterns
- Compatibility with adapter-based fine-tuning approaches

#### 3.3.2 Schema Network Architecture

The Schema Network implements domain-invariant compositional operators through specialized multi-head cross-modal attention:

$$\text{Schema}(Q, K, V) = \text{Concat}(h_1, ..., h_8)W^O$$

where each attention head $h_i$ is computed as:

$$h_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

**Operator Specialization:** Heads 1-3 specialize for binding, 4-5 for sequential composition, 6-8 for hierarchical structuring through operator-level pooling:

$$\text{OperatorPool}_{\text{type}}(H) = \frac{1}{|S_{\text{type}}|} \sum_{i \in S_{\text{type}}} h_i$$

where $S_{\text{type}}$ denotes the set of heads assigned to operator type (binding/sequential/hierarchical).

The Schema Network comprises approximately 50M parameters (15% overhead on base model), remaining frozen during transfer to held-out modalities.

#### 3.3.3 Modality-Specific Adapters

For each modality, we employ Low-Rank Adaptation (LoRA) with rank 16:

$$h = W_0x + \frac{\alpha}{r}BAx$$

where:
- $W_0$ is the frozen pre-trained weight matrix
- $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ are trainable low-rank matrices
- $r = 16$ (rank), $\alpha$ is a scaling factor
- Parameter overhead: ~28M parameters per modality (8% of base model)

### 3.4 Training Procedure

#### 3.4.1 Stage 1: Primitive Extraction (Vision + Language)

**Objective:** Learn modality-specific feature extractors compatible with compositional schemas

**Training Configuration:**
- Optimizer: AdamW with learning rate $\eta = 3 \times 10^{-4}$
- Batch size: 256 samples
- Epochs: 50
- Loss function: Contrastive loss for vision-language alignment

$$\mathcal{L}_{\text{primitive}} = -\log \frac{\exp(\text{sim}(v_i, l_i)/\tau)}{\sum_{j=1}^N \exp(\text{sim}(v_i, l_j)/\tau)}$$

where $\text{sim}(\cdot, \cdot)$ is cosine similarity, $\tau = 0.07$ is temperature, $v_i$ and $l_i$ are vision and language embeddings.

#### 3.4.2 Stage 2: Schema Learning

**Objective:** Train operator-specialized attention heads on compositional tasks

**Training Configuration:**
- Optimizer: AdamW with learning rate $\eta = 1 \times 10^{-4}$
- Batch size: 128 samples
- Epochs: 100
- Loss function: Compositional prediction loss with operator regularization

$$\mathcal{L}_{\text{schema}} = \mathcal{L}_{\text{task}} + \lambda_{\text{op}} \mathcal{L}_{\text{operator}} + \lambda_{\text{cons}} \mathcal{L}_{\text{consistency}}$$

where:

**Task Loss:** Cross-entropy for compositional prediction
$$\mathcal{L}_{\text{task}} = -\sum_{i=1}^N y_i \log \hat{y}_i$$

**Operator Specialization Loss:** Encourages head-operator correspondence
$$\mathcal{L}_{\text{operator}} = -\sum_{\text{type}} \text{MI}(H_{\text{type}}, O_{\text{type}})$$

where $\text{MI}$ is mutual information between head activations and operator type labels.

**Cross-Modal Consistency Loss:** Enforces similar attention patterns across modalities for same composition type
$$\mathcal{L}_{\text{consistency}} = 1 - \frac{1}{|T|} \sum_{\text{type} \in T} \text{CosSim}(A_{\text{vision}}^{\text{type}}, A_{\text{language}}^{\text{type}})$$

Hyperparameters: $\lambda_{\text{op}} = 0.1$, $\lambda_{\text{cons}} = 0.5$

#### 3.4.3 Stage 3: Held-Out Modality Transfer

**Objective:** Adapt frozen schemas to new modalities with minimal data

**Training Configuration:**
- Frozen: Base model + Schema Network (all 400M parameters)
- Trainable: Modality-specific LoRA adapters only (~28M parameters)
- Training samples: 1,000 per held-out modality
- Optimizer: AdamW with learning rate $\eta = 5 \times 10^{-4}$
- Epochs: 30
- Loss function: Task-specific compositional prediction loss

### 3.5 Experimental Design

#### 3.5.1 Primary Experiments: Cross-Domain Transfer Validation

**Experiment 1: Held-Out Modality Compositional Accuracy**

*Objective:* Test Prediction P1 (transfer accuracy >60% of in-domain performance)

*Procedure:*
1. Train schemas on vision+language data (Stage 1-2)
2. Freeze Schema Network completely
3. Train audio adapters on 1,000 samples
4. Train robotics adapters on 1,000 samples
5. Evaluate on novel combinations in held-out test sets

*Evaluation Metrics:*
- **Novel Combination Success Rate (NCSR):** Percentage of correctly predicted novel primitive combinations not seen during adapter training
- **Transfer Ratio:** $\text{TR} = \frac{\text{NCSR}_{\text{held-out}}}{\text{NCSR}_{\text{in-domain}}} \times 100\%$
- Target: TR > 60% with $p < 0.05$ (one-sample t-test, $n \geq 20$ runs)

*Baselines:*
- From-scratch training on 1,000 samples (no schema transfer)
- Full fine-tuning with unfrozen schemas
- Random schema initialization + adapter training

**Experiment 2: Cross-Modal Consistency Analysis**

*Objective:* Test Prediction P2 (mechanism validation through interpretability)

*Procedure:*
1. Extract attention patterns from Schema Network for vision and language samples with same composition type
2. Compute cosine similarity across modalities for each operator type
3. Calculate mutual information between head activations and operator labels

*Evaluation Metrics:*
- **Cross-Modal Consistency (CMC):** Mean cosine similarity of attention patterns across modalities for same composition type
  $$\text{CMC}_{\text{type}} = \frac{1}{N} \sum_{i=1}^N \text{CosSim}(A_{\text{vision}}^{i}, A_{\text{language}}^{i})$$
  Target: CMC > 0.7 for each operator type

- **Operator Emergence (OE):** Mutual information between head assignment and operator type
  $$\text{OE} = \text{MI}(H, O) = \sum_{h,o} p(h,o) \log \frac{p(h,o)}{p(h)p(o)}$$
  Target: OE > 0.5 bits

**Experiment 3: Transfer Efficiency Scaling**

*Objective:* Test Prediction P3 (data efficiency and robustness)

*Procedure:*
1. Train held-out modality adapters with varying data sizes: 100, 500, 1K, 5K samples
2. Measure transfer accuracy at each data point
3. Compare against predicted scaling curve

*Evaluation Metrics:*
- Transfer accuracy at each data point
- Predicted vs. observed scaling deviation
- Data required to reach 60% threshold

*Expected Scaling:*
- 100 samples: 30-40% transfer ratio
- 500 samples: 50-60% transfer ratio
- 1,000 samples: 60-70% transfer ratio
- 5,000 samples: 75-85% transfer ratio

#### 3.5.2 Mechanistic Analysis: Causal Chain Validation

To validate the 5-step causal mechanism, we conduct systematic ablation studies:

**Ablation A1: Multi-modal Data → Operator Patterns**
- Compare schema learning with single-modality vs. multi-modal training
- Measure operator pattern emergence (mutual information)
- Expected: Multi-modal training increases MI by >0.2 bits

**Ablation A2: Operator Patterns → Domain-Invariant Schemas**
- Remove operator-level pooling and consistency loss
- Measure cross-modal consistency degradation
- Expected: Consistency drops from >0.7 to <0.5

**Ablation A3: Schemas + Primitives → In-Domain Composition**
- Compare schema-based vs. end-to-end training on in-domain tasks
- Measure compositional accuracy on SCAN and CZSL benchmarks
- Expected: Schema-based achieves >95% of end-to-end performance

**Ablation A4: Frozen Schemas + New Adapters → Transfer**
- Compare frozen vs. fine-tuned schemas during held-out modality adaptation
- Measure transfer accuracy and catastrophic forgetting
- Expected: Frozen schemas maintain transfer while fine-tuning degrades in-domain performance

**Ablation A5: Transfer → Novel Combinations**
- Analyze performance breakdown by composition complexity
- Measure accuracy on 1-hop, 2-hop, 3-hop compositions
- Expected: Graceful degradation with complexity

#### 3.5.3 Comparative Evaluation

**Baseline Comparisons:**

1. **Mirage (Noviello et al., 2025):** Single-modality dual-process model
   - Compare SCAN accuracy (language)
   - Evaluate cross-domain transfer capability (expected: none)

2. **HGRL:** Vision-only compositional zero-shot learning
   - Compare MIT-States and UT-Zappos accuracy
   - Evaluate audio/robotics transfer (expected: poor)

3. **SMSA (Weng et al., 2025):** Cross-modal semantic distillation
   - Compare cross-modal association preservation
   - Evaluate compositional structure transfer (expected: limited)

4. **From-Scratch Training:** Domain-specific models on 1K samples
   - Direct comparison of data efficiency
   - Critical baseline for practical value assessment

### 3.6 Evaluation Metrics Summary

| Metric | Formula | Target | Falsification Threshold |
|--------|---------|--------|------------------------|
| Transfer Ratio (TR) | $\frac{\text{NCSR}_{\text{held-out}}}{\text{NCSR}_{\text{in-domain}}} \times 100\%$ | >60% | <40% |
| Cross-Modal Consistency (CMC) | $\frac{1}{N}\sum \text{CosSim}(A_v, A_l)$ | >0.7 | <0.5 |
| Operator Emergence (OE) | $\text{MI}(H, O)$ | >0.5 bits | <0.3 bits |
| Data Efficiency | Accuracy at 1K samples | 60-70% | <50% at 5K |
| Baseline Comparison | TR vs. from-scratch | Significantly higher | ≤ from-scratch |

### 3.7 Statistical Analysis

**Sample Size:** All experiments conducted with $n \geq 20$ independent runs (different random seeds)

**Statistical Tests:**
- One-sample t-test for P1 (TR vs. 60% threshold)
- Paired t-test for baseline comparisons
- Pearson correlation for consistency/MI relationships
- Bonferroni correction for multiple comparisons: $\alpha = 0.05 / k$ where $k$ is number of held-out modalities

**Reporting Standards:**
- Mean ± standard deviation
- 95% confidence intervals
- Effect sizes (Cohen's d)
- p-values with significance levels

### 3.8 Computational Resources

**Hardware:** 8× NVIDIA A100 GPUs (80GB VRAM each)

**Estimated Compute Budget:**
- Stage 1 (Primitive Extraction): 30 GPU-hours
- Stage 2 (Schema Learning): 40 GPU-hours
- Stage 3 (Transfer Experiments): 20 GPU-hours
- Ablations and Analysis: 10 GPU-hours
- **Total:** ~100 GPU-hours (~$1,000 cloud compute cost)

**Software Stack:**
- PyTorch 2.0+ with distributed training
- Hugging Face Transformers for base models
- Custom implementation of Schema Network and operator-level pooling
- Weights & Biases for experiment tracking

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Primary Outcomes

**Outcome 1: Validation of Universal Compositional Operators**

We expect to demonstrate that abstract compositional operators (binding, sequential, hierarchical) learned from vision+language data transfer to held-out modalities (audio, robotics) with >60% of in-domain compositional performance. This would provide the first empirical evidence that compositional operators possess universal structure independent of modality-specific content.

*Success Criteria:* Transfer Ratio >60% with p < 0.05 across both audio and robotics domains

*Alternative Outcome:* If transfer ratio falls below 40%, this would indicate compositional operators are fundamentally modality-specific, requiring revision of the universal operator hypothesis and potentially domain-specific schema architectures.

**Outcome 2: Mechanistic Understanding of Schema Transfer**

Through systematic ablation studies, we expect to validate the 5-step causal chain linking multi-modal training, operator specialization, schema formation, and cross-domain transfer. Specifically:

- Cross-modal consistency >0.7 demonstrating domain-invariant schema representations
- Operator emergence >0.5 bits mutual information confirming attention head specialization
- Ablation studies quantifying the contribution of each mechanism component

*Success Criteria:* All mechanistic predictions (P2) validated with statistical significance

**Outcome 3: Data-Efficient Transfer Protocol**

We expect to establish that schema-guided transfer achieves superior data efficiency compared to from-scratch training, requiring only 1,000 samples to reach 60-70% transfer performance—a level that would require orders of magnitude more data for conventional approaches.

*Success Criteria:* Statistically significant advantage over from-scratch baseline at 1K samples

#### 4.1.2 Secondary Outcomes

- **Operator Taxonomy Refinement:** Analysis may reveal additional operator types beyond binding/sequential/hierarchical or suggest refinements to the taxonomy
- **Scaling Laws:** Characterization of how transfer performance scales with schema capacity, adapter rank, and training data diversity
- **Failure Mode Analysis:** Identification of composition types or modality characteristics where transfer fails, informing future research directions

### 4.2 Scientific Impact

#### 4.2.1 Theoretical Contributions

**Compositional Learning Theory:** This research addresses a fundamental question in compositional learning: whether composition rules are universal or domain-specific. Positive results would establish that abstract compositional structure can be separated from modality-specific content, providing theoretical foundation for cross-domain compositional transfer.

**Foundation Model Understanding:** By demonstrating (or refuting) the existence of universal compositional operators, this work contributes to understanding what foundation models learn and under what conditions they exhibit compositional generalization—directly addressing the workshop's first focus area.

**Neuroscience-AI Bridge:** Validation of hierarchical predictive coding as a mechanism for compositional transfer would strengthen connections between cognitive neuroscience and machine learning, potentially informing both fields.

#### 4.2.2 Methodological Contributions

**Transferable Compositional Learning Methods:** The schema-guided transfer framework provides a concrete, model-agnostic approach for compositional learning across domains—directly addressing the workshop's second focus area. The operator-specialized multi-head attention with operator-level pooling offers a reusable architectural pattern.

**Modularity-Compositionality Relationship:** By explicitly testing whether modular structure (schemas + adapters) guarantees compositional generalization, this research addresses the workshop's third focus area, providing empirical evidence for or against this relationship.

**Evaluation Protocols:** The comprehensive evaluation framework (cross-modal consistency metrics, operator emergence analysis, transfer efficiency curves) provides methodological tools for future compositional learning research.

### 4.3 Practical Impact

#### 4.3.1 Efficient Multi-Modal Deployment

**Reduced Training Costs:** If successful, schema-guided transfer would enable foundation models to adapt to new modalities with 1,000 samples instead of millions, reducing computational costs by 2-3 orders of magnitude. At current cloud GPU prices, this translates to cost reductions from ~$100K to ~$1K per modality.

**Rapid Prototyping:** The ability to transfer compositional capabilities with minimal data would accelerate development cycles for applications in emerging modalities (e.g., haptics, olfaction, novel sensor types).

**Resource-Constrained Deployment:** Organizations without access to massive computational resources could leverage pre-trained schemas to deploy compositional AI in specialized domains.

#### 4.3.2 Application Domains

**Robotics:** Transfer of compositional manipulation skills (object + action + spatial relation) would enable robots to generalize to novel object-action combinations with minimal demonstration data, advancing few-shot robot learning.

**Audio Processing:** Compositional understanding of environmental sounds (source + property + pattern) would improve audio scene understanding, assistive technologies, and acoustic monitoring systems.

**Cross-Lingual Systems:** Extension to low-resource languages could leverage compositional schemas learned from high-resource languages, improving machine translation and cross-lingual transfer.

**Continual Learning:** The modular architecture naturally supports the workshop's fourth focus area—extending to continual learning environments by adding new adapters without catastrophic forgetting of existing schemas.

### 4.4 Broader Impact

#### 4.4.1 Advancing Foundation Model Capabilities

This research contributes to the broader goal of developing foundation models with human-like compositional understanding. Success would demonstrate a concrete path toward models that can:

- Generalize systematically to novel combinations
- Transfer knowledge efficiently across domains
- Adapt to new modalities with minimal supervision
- Maintain interpretable compositional structure

#### 4.4.2 Addressing Workshop Challenges

**Compositional Generalization in Dynamic Distributions:** By enabling efficient adaptation through schema transfer, this work addresses the challenge of compositional learning in frequently changing real-world distributions.

**Model-Agnostic Strategies:** The schema-guided approach is compatible with existing foundation models (demonstrated with 350M parameter Transformer), providing a practical path for integration with current systems.

**Theoretical-Empirical Bridge:** The research combines theoretical grounding (hierarchical predictive coding) with rigorous empirical validation, contributing to both understanding and practical advancement.

### 4.5 Limitations and Future Directions

#### 4.5.1 Known Limitations

**Operator Taxonomy Completeness:** The current taxonomy (binding, sequential, hierarchical) may be incomplete. Future work should investigate additional operator types and domain-specific composition rules.

**Inference Overhead:** The 20% computational overhead from Schema Network may be prohibitive for real-time applications (<50ms latency requirements). Optimization techniques or distillation approaches could address this.

**Modality Scope:** The framework applies to modalities with compositional structure. Unstructured or fundamentally different composition paradigms may require alternative approaches.

**Synthetic Augmentation Quality:** The 360K augmented samples may not capture all real-world compositional nuances. Future work should explore improved augmentation strategies or larger-scale multi-modal datasets.

#### 4.5.2 Future Research Directions

**Continual Schema Learning:** Extending the framework to continuously update schemas as new modalities are encountered, addressing the workshop's fourth focus area more directly.

**Hierarchical Schema Composition:** Investigating whether schemas themselves can be composed hierarchically for more complex compositional patterns.

**Cross-Domain Schema Transfer:** Testing transfer between more distant modality pairs (e.g., audio → robotics) to establish limits of universality.

**Theoretical Analysis:** Developing formal theoretical frameworks for universal compositional operators, potentially drawing on category theory or abstract algebra.

**Real-World Deployment:** Validating the approach on production-scale systems and diverse application domains beyond controlled benchmarks.

### 4.6 Timeline and Deliverables

**Months 1-3:** Data preparation, baseline implementation, Stage 1 training
**Months 4-6:** Schema learning (Stage 2), initial transfer experiments
**Months 7-9:** Comprehensive evaluation, ablation studies, mechanistic analysis
**Months 10-12:** Comparative evaluation, paper writing, code release

**Deliverables:**
- Open-source implementation of schema-guided transfer framework
- Comprehensive benchmark suite for cross-domain compositional evaluation
- Research paper submitted to top-tier venue (NeurIPS, ICML, ICLR)
- Workshop presentation and community engagement
- Public dataset of compositional augmentations

---

**Conclusion:** This research proposal presents a rigorous, theoretically grounded, and empirically testable approach to cross-domain compositional transfer in foundation models. By factorizing compositional learning into universal schemas and modality-specific primitives, we address fundamental questions about the nature of compositional operators while providing practical methods for efficient multi-modal deployment. The comprehensive experimental design, clear falsification criteria, and alignment with workshop themes position this work to make significant contributions to compositional learning research and foundation model development.