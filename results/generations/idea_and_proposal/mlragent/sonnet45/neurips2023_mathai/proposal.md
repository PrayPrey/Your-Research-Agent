# Title

Adaptive Curriculum Learning for Mathematical Reasoning via Proof Complexity Measures: A Formal Framework for Progressive LLM Training

# Introduction

## Background

Mathematical reasoning represents one of the most challenging frontiers in artificial intelligence research. While recent large language models (LLMs) have demonstrated remarkable capabilities in various domains, their performance on mathematical reasoning tasks remains inconsistent and brittle. These models often succeed on superficially complex problems while failing on structurally simpler ones that require deeper logical reasoning chains. This paradoxical behavior reveals a fundamental gap in how current training methodologies address the hierarchical and compositional nature of mathematical knowledge.

Traditional approaches to training LLMs for mathematical reasoning typically treat all problems uniformly, disregarding the substantial differences in logical depth, proof complexity, and prerequisite knowledge required for solving different problems. This one-size-fits-all approach mirrors teaching calculus and basic arithmetic with the same pedagogical strategy—an approach that would clearly fail in human education. The mathematical education literature has long recognized that effective learning requires carefully sequenced curricula that build foundational concepts before advancing to more complex material, yet this principle has been largely absent from LLM training paradigms.

Recent work in curriculum learning for LLMs has begun to address this gap, with studies such as Progressive Mastery (Wu et al., 2025) and AdaRFT (Shi et al., 2025) demonstrating that adaptive difficulty sequencing can improve model performance. However, these approaches typically rely on superficial difficulty metrics (e.g., problem length, numerical complexity) rather than fundamental measures of logical structure and proof complexity. The field lacks a principled framework grounded in formal proof theory that can accurately characterize the intrinsic difficulty of mathematical reasoning tasks.

## Research Objectives

This research proposes to develop and validate a comprehensive curriculum learning framework for mathematical reasoning that leverages formal proof-theoretic complexity measures extracted from proof assistants such as Lean, Coq, and Isabelle. Our primary objectives are:

1. **Formalize proof complexity metrics**: Develop a suite of computational measures capturing proof depth, lemma dependency structures, concept prerequisite graphs, and logical inference complexity that can be automatically extracted from formal proofs.

2. **Design adaptive curriculum algorithms**: Create dynamic curriculum learning algorithms that sequence training examples based on these formal complexity measures, with real-time adaptation based on model performance across specific reasoning capabilities.

3. **Implement interleaved reinforcement mechanisms**: Develop strategies for periodically revisiting simpler problems with newly learned concepts to prevent catastrophic forgetting and strengthen conceptual connections across difficulty levels.

4. **Validate empirically**: Demonstrate that this approach yields superior multi-step reasoning capabilities, better generalization across difficulty levels, and improved sample efficiency compared to baseline training approaches.

## Significance

This research addresses critical challenges at the intersection of artificial intelligence and mathematical reasoning with implications spanning multiple domains:

**Theoretical contributions**: By grounding curriculum design in formal proof theory, this work bridges the gap between computational learning theory and automated theorem proving, providing a mathematically rigorous framework for characterizing reasoning difficulty.

**Practical applications**: Improved mathematical reasoning capabilities in LLMs would enable advances in software verification, automated discovery in mathematics and sciences, intelligent tutoring systems, and AI-assisted engineering design.

**Educational implications**: Understanding how structured curricula affect machine learning could inform human mathematics education, particularly in resource-constrained environments where AI tutoring systems might play an increasingly important role.

**Benchmark development**: The proof complexity metrics developed in this research could establish new standards for evaluating mathematical reasoning capabilities, addressing the workshop's emphasis on measuring mathematical reasoning in the LLM era.

# Methodology

## Data Collection and Preparation

### Formal Proof Corpus Construction

We will construct a comprehensive dataset of formal mathematical proofs from three primary sources:

1. **Lean MathLib**: The mathematical library for the Lean theorem prover, containing over 100,000 theorems spanning undergraduate and graduate mathematics
2. **Coq Standard Library and Mathematical Components**: Formal developments in constructive mathematics and algebra
3. **Archive of Formal Proofs (AFP)**: Isabelle/HOL proof archive containing diverse mathematical content

For each proof in our corpus, we will extract:
- Complete proof trees with all intermediate steps
- Dependency graphs showing which lemmas, definitions, and axioms are invoked
- Type signatures and formal statements of all theorems
- Natural language problem statements (where available) or auto-generated descriptions

### Informal Problem Dataset

To enable training and evaluation on informal mathematical problems, we will utilize:
- GSM8K and MATH datasets (arithmetic and competition mathematics)
- MMLU mathematics subset (standardized test problems)
- Lean informal-to-formal translation pairs from existing repositories
- Custom-created problems at varying difficulty levels with human annotations

## Proof Complexity Formalization

### Core Complexity Metrics

We define a multi-dimensional complexity measure $\mathcal{C}(P)$ for a proof $P$, comprising:

**1. Proof Depth** ($d(P)$): The length of the longest inference chain from axioms to conclusion:
$$d(P) = \max_{c \in \text{conclusions}(P)} \text{dist}(\text{axioms}, c)$$

**2. Proof Width** ($w(P)$): The maximum number of premises used in any single inference step:
$$w(P) = \max_{s \in \text{steps}(P)} |\text{premises}(s)|$$

**3. Lemma Complexity** ($\ell(P)$): A weighted count of lemma applications, with weights based on lemma difficulty:
$$\ell(P) = \sum_{L \in \text{lemmas}(P)} \alpha^{d(L)} \cdot (1 + \ell(L))$$
where $\alpha \in (0,1)$ is a decay factor and lemma difficulty is recursively defined.

**4. Concept Dependency Score** ($\kappa(P)$): Measures the breadth of prerequisite mathematical concepts:
$$\kappa(P) = |\text{concepts}(P)| + \beta \sum_{c_1, c_2 \in \text{concepts}(P)} \text{dist}_{\mathcal{G}}(c_1, c_2)$$
where $\text{dist}_{\mathcal{G}}$ is the graph distance in a predefined mathematical concept hierarchy $\mathcal{G}$, and $\beta$ balances breadth and diversity.

**5. Abstraction Level** ($\alpha(P)$): Quantifies the use of abstract mathematical structures (groups, topological spaces, etc.) versus concrete objects:
$$\alpha(P) = \frac{\sum_{t \in \text{types}(P)} \text{abstraction}(t)}{|\text{types}(P)|}$$

The composite complexity measure is:
$$\mathcal{C}(P) = \mathbf{w}^T [d(P), w(P), \ell(P), \kappa(P), \alpha(P)]^T$$
where $\mathbf{w}$ is a weight vector learned through meta-learning (described below).

### Complexity Extraction Pipeline

We implement an automated pipeline:

1. **Parse formal proofs**: Use proof assistant APIs to extract proof terms and tactics
2. **Build dependency graphs**: Construct directed acyclic graphs representing logical dependencies
3. **Compute base metrics**: Calculate $d(P)$, $w(P)$, $\ell(P)$, $\kappa(P)$, $\alpha(P)$ via graph algorithms
4. **Learn complexity weights**: Use human difficulty ratings (when available) or model performance data to learn $\mathbf{w}$ via regression

## Adaptive Curriculum Learning Algorithm

### Curriculum Sequencing Strategy

Our curriculum learning framework operates in stages with adaptive transitions:

**Stage 1: Foundation Building (Epochs 1-T₁)**
- Focus on problems with $\mathcal{C}(P) < \theta_1$ (low complexity)
- Emphasize single-step inferences and basic lemma applications
- Training objective: maximize accuracy on fundamental reasoning patterns

**Stage 2: Structured Progression (Epochs T₁-T₂)**
- Gradually increase complexity threshold: $\theta(t) = \theta_1 + (\theta_2 - \theta_1) \cdot \frac{t - T_1}{T_2 - T_1}$
- Introduce problems requiring multi-step reasoning
- Training objective: standard next-token prediction with complexity-weighted sampling

**Stage 3: Advanced Integration (Epochs T₂-T₃)**
- Full complexity range with emphasis on challenging problems
- Interleaved rehearsal of foundational concepts
- Training objective: policy optimization with reasoning-specific rewards

### Adaptive Difficulty Adjustment

We implement a performance-monitoring system that adjusts curriculum pacing:

$$\theta_{t+1} = \theta_t + \eta \cdot \text{sign}(\text{acc}_{\text{val}}(t) - \text{acc}_{\text{target}}) \cdot |\text{acc}_{\text{val}}(t) - \text{acc}_{\text{target}}|^\gamma$$

where:
- $\text{acc}_{\text{val}}(t)$ is validation accuracy at step $t$
- $\text{acc}_{\text{target}}$ is the target accuracy threshold for progression
- $\eta$ is the learning rate for difficulty adjustment
- $\gamma$ controls adjustment sensitivity

### Interleaved Skill Reinforcement

To prevent catastrophic forgetting, we implement periodic rehearsal:

**Rehearsal Sampling Strategy**: At each training step, with probability $p_{\text{rehearse}}$, sample a problem from earlier complexity levels weighted by:
$$p(P) \propto \exp\left(-\lambda \cdot \text{recency}(P)\right) \cdot \mathbb{I}[\mathcal{C}(P) < \theta_{\text{current}} - \delta]$$

where $\text{recency}(P)$ measures how recently the problem type was seen, and $\delta$ ensures sufficient complexity gap.

**Concept Connection Mechanism**: When introducing a new complex problem, we identify prerequisite concepts and explicitly sample related simpler problems:
$$\mathcal{R}(P_{\text{new}}) = \{P \in \mathcal{D}_{\text{seen}} : |\text{concepts}(P) \cap \text{concepts}(P_{\text{new}})| \geq k\}$$

Sample problems from $\mathcal{R}(P_{\text{new}})$ before and after presenting $P_{\text{new}}$.

## Model Architecture and Training

### Base Model Selection

We will experiment with:
- LLaMA-3 (8B and 70B parameters)
- DeepSeek-Math (specialized for mathematical reasoning)
- Custom Transformer variants with architectural modifications for multi-step reasoning

### Training Procedure

**Phase 1: Supervised Fine-tuning with Curriculum**
1. Initialize from pretrained checkpoint
2. Apply curriculum sequencing as described above
3. Loss function: standard cross-entropy with complexity-aware weighting
$$\mathcal{L}_{\text{SFT}} = \mathbb{E}_{P \sim \mathcal{D}(\theta_t)} \left[ w(\mathcal{C}(P)) \cdot \mathcal{L}_{\text{CE}}(P) \right]$$

**Phase 2: Reinforcement Learning Fine-tuning**
Apply policy gradient methods with reasoning-specific rewards:
$$R(P, \hat{P}) = \mathbb{I}[\text{correct}(\hat{P})] + \lambda_1 \cdot \text{step\_efficiency}(\hat{P}) + \lambda_2 \cdot \text{clarity}(\hat{P})$$

where:
- $\text{step\_efficiency}$ rewards shorter proofs
- $\text{clarity}$ rewards interpretable intermediate steps (scored by auxiliary model)

**Phase 3: Interleaved Rehearsal and Consolidation**
Alternate between:
- Training on frontier complexity level
- Rehearsal batches from earlier levels
- Mixed batches connecting concepts across levels

## Experimental Design

### Baseline Comparisons

We will compare against:
1. **Uniform sampling**: Standard fine-tuning without curriculum
2. **Length-based curriculum**: Sorting by solution length
3. **Random curriculum**: Random difficulty ordering
4. **Fixed difficulty curriculum**: Predetermined static ordering
5. **AdaRFT** (Shi et al., 2025): Current state-of-the-art adaptive curriculum
6. **Progressive Mastery** (Wu et al., 2025): Guided prompting curriculum

### Evaluation Benchmarks

**In-distribution evaluation**:
- MATH dataset (stratified by difficulty level)
- GSM8K
- Custom test set with formal proof complexity annotations

**Out-of-distribution evaluation**:
- Unseen complexity combinations (high depth + low width vs. low depth + high width)
- Cross-domain transfer (algebra → geometry)
- Novel theorem proving tasks in Lean

**Process-level evaluation**:
- Intermediate step correctness
- Proof structure quality (evaluated by formal verification when possible)
- Reasoning transparency (human evaluation)

### Evaluation Metrics

1. **Accuracy**: Standard correctness on final answers
2. **Complexity-stratified accuracy**: Performance binned by $\mathcal{C}(P)$ quantiles
3. **Sample efficiency**: Learning curves (accuracy vs. training examples)
4. **Generalization gap**: Performance difference between seen and unseen complexity profiles
5. **Catastrophic forgetting measure**: 
$$\text{CF} = \frac{1}{K}\sum_{i=1}^K \max(0, \text{acc}_{\text{early}}^{(i)} - \text{acc}_{\text{final}}^{(i)})$$
where $\text{acc}_{\text{early}}^{(i)}$ is accuracy on complexity level $i$ when it was the training focus, and $\text{acc}_{\text{final}}^{(i)}$ is final accuracy on that level.

### Ablation Studies

To isolate the contribution of each component:
1. Individual complexity metrics (remove each from $\mathcal{C}(P)$)
2. Adaptive vs. fixed curriculum pacing
3. Rehearsal frequency and strategy variations
4. Different weight learning methods for $\mathbf{w}$
5. Impact of formal proof grounding vs. heuristic difficulty estimates

### Computational Requirements

- **Training**: 4-8 A100 GPUs per model variant
- **Duration**: Estimated 2-4 weeks per full training run
- **Iterations**: 20+ experimental configurations
- **Total compute**: Approximately 10,000-15,000 GPU-hours

# Expected Outcomes & Impact

## Expected Outcomes

### Primary Outcomes

1. **Performance improvements**: We anticipate 10-20% absolute accuracy gains on challenging mathematical reasoning benchmarks (MATH level 4-5 problems) compared to uniform training baselines, with particular strength on multi-step problems requiring deep logical chains.

2. **Enhanced sample efficiency**: The curriculum approach should achieve target performance levels with 30-50% fewer training examples, as the model learns more effectively from appropriately sequenced data.

3. **Superior generalization**: Models trained with proof-complexity curricula should demonstrate better transfer to unseen complexity profiles and problem types, with reduced performance degradation on out-of-distribution evaluations.

4. **Reduced catastrophic forgetting**: The interleaved rehearsal mechanism should maintain performance on simpler problems (CF < 0.05) while learning advanced concepts, outperforming sequential training approaches.

### Secondary Outcomes

5. **Interpretable complexity framework**: The proof complexity metrics will provide a quantitative, interpretable basis for characterizing mathematical problem difficulty, valuable for benchmark design and educational applications.

6. **Insights into reasoning progression**: Analysis of learning curves across complexity dimensions will reveal which aspects of mathematical reasoning are most challenging for current architectures, informing future model design.

7. **Formal-informal alignment**: By grounding informal problem difficulty in formal proof complexity, we bridge symbolic AI and neural approaches, potentially enabling hybrid reasoning systems.

## Scientific Impact

### Advancing AI Mathematical Reasoning

This research directly addresses the workshop's central question: "To what extent can machine learning models comprehend mathematics?" By establishing that structured, complexity-aware training significantly improves reasoning capabilities, we provide evidence that current architectural limitations can be partially overcome through better training methodology. The proof-theoretic grounding offers a principled answer to "what does it mean for an LLM to understand mathematics?"—at minimum, it should master concepts in an order respecting their logical dependencies.

### Benchmark and Evaluation Contributions

The proof complexity framework addresses the workshop theme of "Measuring mathematical reasoning" by providing:
- Automated difficulty metrics independent of model performance
- Fine-grained evaluation along multiple complexity dimensions
- A basis for creating balanced, comprehensive evaluation suites

This could influence how the community designs future mathematical reasoning benchmarks, moving beyond simple accuracy to complexity-stratified evaluation.

### Bridging Human and Machine Learning

Our curriculum approach draws explicit inspiration from mathematics education research, contributing to the "Humans vs. machines" dialogue. Comparative analysis of human learning trajectories and optimal machine curricula could reveal:
- Universal principles of mathematical concept acquisition
- Fundamental differences in how humans and LLMs represent mathematical knowledge
- Opportunities for human-AI collaborative learning

## Practical Impact

### Educational Applications

The research has immediate implications for AI-assisted mathematics education:

1. **Adaptive tutoring systems**: The complexity metrics and curriculum algorithms can be adapted to personalize problem sequencing for individual students, particularly valuable in resource-limited educational contexts.

2. **Automatic problem generation**: Understanding complexity structure enables generating problems at precisely calibrated difficulty levels for formative assessment.

3. **Teacher support tools**: Providing educators with automated difficulty analysis to inform curriculum design and identify student struggles.

### Software Verification and Formal Methods

Improved mathematical reasoning capabilities directly benefit:
- Automated theorem proving for software verification
- Bug detection in critical systems
- Formal specification development

Models trained with our approach should be more reliable when applied to verification tasks requiring complex multi-step logical reasoning.

### Scientific Discovery

Enhanced mathematical reasoning enables AI systems to:
- Assist in conjecture generation and theorem discovery
- Explore vast proof spaces more effectively
- Serve as collaborative tools for mathematical researchers

## Long-term Vision

This research establishes foundations for several future directions:

1. **Hierarchical curriculum learning**: Extending beyond mathematics to other domains with clear conceptual hierarchies (physics, programming, legal reasoning)

2. **Meta-learning curricula**: Developing algorithms that automatically discover optimal curricula for new domains without manual complexity metric design

3. **Hybrid neurosymbolic systems**: Integrating formal proof assistants directly into LLM training loops, enabling real-time verification and formal feedback

4. **Continual learning frameworks**: Applying the interleaved rehearsal mechanisms to lifelong learning scenarios where models continuously acquire new mathematical knowledge

## Addressing Workshop Themes

This proposal directly engages with multiple workshop focus areas:

- **Measuring mathematical reasoning**: Novel complexity-based evaluation framework
- **New capabilities**: Moving beyond current techniques through principled curriculum design  
- **Education**: Direct applications to adaptive tutoring and personalized learning
- **Applications**: Enabling advances in verification, scientific discovery, and mathematical research
- **Humans vs. machines**: Comparative analysis of learning progressions

By providing both theoretical frameworks and practical algorithms, this research contributes to the workshop's goal of fostering "lively and constructive dialogue" across the diverse stakeholder groups interested in AI and mathematical reasoning.

## Limitations and Future Work

We acknowledge several limitations:

1. **Formalization bottleneck**: Not all mathematical problems have formal proofs; we will develop heuristic complexity estimators for informal problems based on learned mappings from formal examples.

2. **Computational cost**: Formal proof extraction and complexity computation are expensive; optimization and caching strategies will be essential.

3. **Domain specificity**: Initial focus on mathematical reasoning may limit immediate transfer to other domains; cross-domain validation is needed.

Future work will address these limitations while extending the framework to multi-modal mathematical reasoning (diagrams, symbolic manipulation) and exploring theoretical connections to computational learning theory.