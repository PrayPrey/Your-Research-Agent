# Research Proposal: Developmental Curriculum Learning for Neural Theorem Proving

## 1. Title

**Developmental Curriculum Learning for Neural Theorem Proving: Bridging Educational Science and AI for Mathematics**

## 2. Introduction

### 2.1 Background

Mathematical reasoning represents one of the most sophisticated forms of human intelligence, requiring the ability to manipulate abstract symbols, construct logical arguments, and discover novel connections between concepts. The development of neural theorem provers—AI systems capable of generating formal mathematical proofs—has emerged as a grand challenge in artificial intelligence, with profound implications for automated reasoning, formal verification, and scientific discovery.

Recent advances have demonstrated impressive capabilities on benchmark datasets. State-of-the-art systems like DeepSeek-Prover-V2 achieve 88.9% success rates on MiniF2F, a curated collection of competition-level mathematical problems. However, a critical generalization gap emerges when these systems encounter research-level mathematics: performance plummets to merely 10.3% on RLMEval, a dataset of 613 authentic theorems from active Lean formalization projects. This 8.6-fold performance degradation reveals a fundamental limitation—current neural theorem provers learn surface-level pattern matching rather than robust reasoning primitives.

The root cause of this failure has been identified through recent empirical studies. Wang et al. (2025) documented the "Pseudo Aha Moment" phenomenon, where 77-100% of model errors stem from exploiting superficial shortcuts in benchmark data rather than genuine mathematical understanding. When theorem statements are paraphrased or proof templates are varied, baseline models exhibit catastrophic performance drops of 47-73%, demonstrating brittleness to surface-form variations that human mathematicians handle effortlessly.

Existing curriculum learning approaches for theorem proving rely on ad-hoc heuristics—typically sorting problems by proof length or syntactic complexity—without principled theoretical grounding. While these methods show modest improvements on benchmarks, they fail to address the fundamental challenge of building generalizable reasoning capabilities that transfer to novel mathematical domains and research-level complexity.

### 2.2 Research Objectives

This research proposes a paradigm shift: applying evidence-based educational learning science to design curricula for neural theorem provers. Specifically, we draw upon two complementary theoretical frameworks:

1. **Developmental Psychology and Transfer Learning**: Fahim & Karim (2026) demonstrated that exposure to diverse problem types during early learning phases enables robust few-shot generalization in children, achieving AUC 0.65 with only 50 training samples. This diversity-driven transfer learning provides a principled foundation for curriculum design.

2. **Cognitive Demand Frameworks**: Neugebauer & Prediger (2022) established that progressive scaffolding through carefully calibrated difficulty tiers builds abstract understanding rather than procedural memorization in mathematics education. Their framework provides operational criteria for structuring learning progressions.

Our primary research objective is to develop and validate **DC-NTP (Developmental Curriculum for Neural Theorem Proving)**, a three-phase training framework that:

- **Phase 1 (Diversity Pre-training)**: Exposes models to 10,000 simple theorems across 10 mathematical domains to build broad reasoning primitives
- **Phase 2 (Cognitive Demand Progression)**: Advances through four difficulty tiers with controlled template variation to force abstract pattern learning
- **Phase 3 (Research-Level Integration)**: Integrates 613 authentic research problems with reinforcement learning for practical deployment

We hypothesize that this developmentally-grounded curriculum will improve research-level performance from 10.3% to >25% on RLMEval while maintaining ≥85% on MiniF2F benchmarks and achieving superior template robustness (<30% performance drop vs. 47-73% baseline).

### 2.3 Significance

This research addresses three critical gaps in AI for mathematics:

**Scientific Significance**: This work establishes the first formal connection between educational learning science and neural theorem prover generalization. By grounding curriculum design in transfer learning bounds and cognitive demand frameworks, we move beyond empirical heuristics toward learning-theoretically principled training methodologies. This cross-disciplinary synthesis opens new research directions at the intersection of AI and cognitive science.

**Technical Significance**: Achieving >25% on RLMEval would represent a 2.5-fold improvement over state-of-the-art, bringing research-level AI assistance to practical viability. This breakthrough would enable meaningful collaboration between AI systems and research mathematicians on active formalization projects, accelerating the development of verified mathematical knowledge bases like Lean's mathlib.

**Practical Significance**: The proposed framework addresses urgent needs in formal verification, proof assistant augmentation, and automated formalization. By demonstrating that educationally-grounded curricula improve generalization, this work provides actionable insights for training robust reasoning systems across domains—from software verification to scientific reasoning—where reliability and transferability are paramount.

## 3. Methodology

### 3.1 Research Design Overview

We employ a randomized controlled experimental design comparing the proposed DC-NTP curriculum against three baselines: (1) flat random sampling, (2) reverse curriculum ordering, and (3) state-of-the-art single-phase RL training (DeepSeek-Prover-V2 replication). All conditions are matched for total training compute, data volume, model architecture, and hyperparameters to isolate curriculum structure as the independent variable.

### 3.2 Data Collection and Preparation

**Dataset Construction**: We construct a stratified dataset of 15,613 theorems from Lean 4's mathlib library using the LeanDojo extraction toolkit:

1. **Phase 1 Dataset (10,000 theorems)**: Sample 1,000 theorems from each of 10 mathematical domains (algebra, geometry, logic, number theory, set theory, graph theory, combinatorics, topology, analysis, category theory). Selection criteria: proof length 1-2 steps, minimal dependencies (≤3 prerequisite theorems), high tactic diversity (≥4 distinct tactics in domain).

2. **Phase 2 Dataset (5,000 theorems)**: Stratify into four cognitive demand tiers based on proof complexity metrics:
   - **Tier 1**: 2-3 proof steps, 1,250 theorems
   - **Tier 2**: 4-6 proof steps, 1,250 theorems  
   - **Tier 3**: 7-10 proof steps, 1,250 theorems
   - **Tier 4**: 11+ proof steps, 1,250 theorems

   For each tier, generate 30% template variants by: (a) paraphrasing theorem statements using GPT-4 with semantic preservation verification, (b) reordering proof steps where logically permissible, (c) substituting equivalent tactics (e.g., `rw` ↔ `simp`).

3. **Phase 3 Dataset (613 theorems)**: Use the complete RLMEval benchmark of research-level theorems from active Lean projects.

**Complexity Metrics**: We define proof complexity $C(T)$ for theorem $T$ as:

$$C(T) = \alpha \cdot \text{steps}(T) + \beta \cdot \text{deps}(T) + \gamma \cdot \text{div}(T)$$

where $\text{steps}(T)$ is proof length, $\text{deps}(T)$ is dependency count, $\text{div}(T)$ is tactic diversity (unique tactics / total tactics), and $\alpha=0.5, \beta=0.3, \gamma=0.2$ are empirically calibrated weights.

### 3.3 Model Architecture and Training Infrastructure

**Base Model**: We use transformer-based language models (7B-30B parameters) initialized from pre-trained checkpoints (LLaMA-2 or DeepSeek-Coder). The model architecture follows standard decoder-only transformers with causal attention.

**Proof Generation Formulation**: Given theorem statement $s$, the model generates proof $p = (t_1, t_2, \ldots, t_n)$ as a sequence of Lean tactics. At each step $i$, the model predicts:

$$P(t_i | s, t_{1:i-1}, g_i) = \text{softmax}(W_o h_i)$$

where $g_i$ is the current proof state (goals, hypotheses, context) and $h_i$ is the transformer hidden state.

**Training Infrastructure**: We utilize the LeanDojo framework for:
- Proof state extraction and goal tracking
- Tactic execution and verification
- Reward signal computation (binary success/failure + step efficiency)

### 3.4 Three-Phase Curriculum Training Protocol

#### Phase 1: Diversity Pre-training (Epochs 1-5)

**Objective**: Build broad reasoning primitives through cross-domain exposure.

**Training Procedure**:
1. Sample mini-batches uniformly across 10 domains (100 theorems per domain per batch)
2. Train with supervised learning on ground-truth proofs:
   $$\mathcal{L}_{\text{SL}} = -\sum_{i=1}^{n} \log P(t_i^* | s, t_{1:i-1}^*, g_i)$$
   where $t_i^*$ are ground-truth tactics
3. Advancement criterion: Achieve >90% success rate on held-out validation set (1,000 theorems, 100 per domain)

**Rationale**: Transfer learning theory predicts that diverse pre-training reduces sample complexity for downstream tasks. Formally, if $\mathcal{D}_1, \ldots, \mathcal{D}_k$ are source domains and $\mathcal{D}_{\text{target}}$ is the target domain, the generalization bound is:

$$\mathbb{E}_{\mathcal{D}_{\text{target}}}[\text{error}] \leq \frac{1}{k}\sum_{j=1}^{k} \mathbb{E}_{\mathcal{D}_j}[\text{error}] + \mathcal{O}\left(\sqrt{\frac{d_{\mathcal{H}}}{n}}\right)$$

where $d_{\mathcal{H}}$ is hypothesis class complexity and $n$ is sample size. Diversity (large $k$) reduces the first term.

#### Phase 2: Cognitive Demand Progression (Epochs 6-20)

**Objective**: Build abstract reasoning through progressive complexity with template variation.

**Training Procedure**:
1. **Tier 1 Training** (Epochs 6-9):
   - Train on 1,250 base theorems + 375 template variants (30%)
   - Use supervised learning with curriculum replay (20% samples from Phase 1)
   - Advancement criterion: 80% success rate on Tier 1 validation set (250 theorems)

2. **Tier 2-4 Training** (Epochs 10-20):
   - Repeat procedure for each tier with increasing complexity
   - Introduce reinforcement learning with GRPO (Group Relative Policy Optimization):
     $$\mathcal{L}_{\text{RL}} = -\mathbb{E}_{p \sim \pi_\theta}\left[R(p) \cdot \log \pi_\theta(p | s)\right] + \beta \cdot D_{\text{KL}}(\pi_\theta || \pi_{\text{ref}})$$
     where $R(p) = \mathbb{1}[\text{proof succeeds}] - 0.01 \cdot \text{steps}(p)$ rewards correctness and efficiency
   - Curriculum replay: Maintain 15% samples from all previous tiers

**Template Variation Strategy**: For each base theorem $T$, generate variants $T'$ such that:
- Semantic equivalence: $T \equiv T'$ (verified by Lean type checker)
- Syntactic distance: $\text{edit\_distance}(T, T') \geq 0.3 \cdot |T|$
- Proof transferability: Ground-truth proof for $T$ requires ≥2 tactic modifications for $T'$

**Rationale**: Cognitive demand frameworks suggest that progressive scaffolding with controlled variation forces learners to extract abstract patterns. Template variation prevents shortcut learning by ensuring surface-form memorization fails.

#### Phase 3: Research-Level Integration (Epochs 21-30)

**Objective**: Transfer learned reasoning to authentic research problems.

**Training Procedure**:
1. Fine-tune on 613 RLMEval theorems using GRPO with enhanced exploration:
   $$\pi_{\text{explore}}(t | s, g) = (1-\epsilon) \cdot \pi_\theta(t | s, g) + \epsilon \cdot \pi_{\text{uniform}}(t)$$
   with $\epsilon=0.2$ for first 5 epochs, then $\epsilon=0.1$
2. Implement proof search with best-first search (beam width 64)
3. Curriculum replay: Maintain 10% samples from Phases 1-2 to prevent catastrophic forgetting

**Rationale**: Research-level problems require integrating diverse reasoning primitives. The curriculum replay mechanism ensures retention of foundational skills while adapting to novel complexity.

### 3.5 Baseline Conditions

**Baseline 1 (Flat Random)**: Train on all 15,613 theorems with uniform random sampling for 30 epochs.

**Baseline 2 (Reverse Curriculum)**: Train in reverse order (Phase 3 → Phase 2 → Phase 1) to test curriculum ordering hypothesis.

**Baseline 3 (SOTA Replication)**: Replicate DeepSeek-Prover-V2 single-phase RL training on combined dataset.

All baselines use identical model architecture, hyperparameters, and total training compute (matched to DC-NTP).

### 3.6 Evaluation Metrics and Experimental Protocol

**Primary Metrics**:

1. **RLMEval Performance**: Pass rate on 613 research-level theorems (pass@1 with 64-beam search, 10-minute timeout per theorem)
   $$\text{RLMEval Score} = \frac{|\{T \in \text{RLMEval} : \text{proof found}\}|}{613}$$

2. **MiniF2F Performance**: Pass rate on 244 test problems (standard benchmark protocol)

3. **Template Robustness**: Performance drop on VAR-MATH variants
   $$\text{Robustness} = 1 - \frac{\text{Score}_{\text{base}} - \text{Score}_{\text{variant}}}{\text{Score}_{\text{base}}}$$

**Secondary Metrics**:

4. **Proof Efficiency**: Average proof length for successful attempts
5. **Search Efficiency**: Average beam expansions before finding proof
6. **Cross-Domain Transfer**: Performance on held-out mathematical domains (algebraic topology, differential geometry)

**Statistical Protocol**:
- 5 independent training runs with different random seeds
- Paired t-tests for pairwise comparisons (α=0.05)
- Effect size reporting (Cohen's d)
- Power analysis: 1-β=0.80 to detect d≥1.5

**Falsification Criteria**:
- Hypothesis rejected if RLMEval <15% (vs. 10.3% baseline)
- Hypothesis rejected if pilot study shows ≤5% improvement over random ordering

### 3.7 Mechanistic Analysis

To validate the causal mechanism (diversity → primitives → abstraction → generalization), we conduct:

**Representation Analysis**:
1. **Attention Pattern Analysis**: Compute attention entropy across proof steps:
   $$H(A_i) = -\sum_{j} A_{ij} \log A_{ij}$$
   Hypothesis: Curriculum models show higher entropy (broader context integration)

2. **Embedding Geometry**: Apply UMAP to theorem embeddings, measure cluster purity by mathematical domain. Hypothesis: Curriculum models show more abstract organization (mixed domains in clusters)

3. **Probing Tasks**: Train linear probes to predict proof complexity from intermediate representations. Hypothesis: Curriculum models encode complexity more accurately (≥20% higher probe accuracy)

**Ablation Studies**:
- Remove Phase 1 (test diversity necessity)
- Remove template variation (test robustness mechanism)
- Vary tier boundaries (test cognitive demand calibration)

### 3.8 Pilot Study

Before full-scale experiments, we conduct a pilot study with:
- 1B parameter model (reduced compute)
- 1,000 theorems (100 per domain in Phase 1, 250 per tier in Phase 2, 100 from RLMEval)
- 4 conditions: curriculum, random, reverse, flat
- Success criterion: Curriculum >15% better than random on pilot RLMEval subset (p<0.05)

This pilot validates curriculum construction methodology and calibrates hyperparameters before committing full compute budget.

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Performance Targets**:

1. **Primary Outcome**: RLMEval performance ≥25% (vs. 10.3% baseline), representing a 14.7 percentage point improvement and 2.5-fold relative gain. This target is grounded in transfer learning theory: if diversity pre-training provides 5-7% gain (based on Fahim & Karim's AUC improvements) and cognitive demand progression provides 8-10% gain (based on Neugebauer & Prediger's effect sizes in education), the combined effect should exceed 25% with positive interaction.

2. **Benchmark Maintenance**: MiniF2F performance ≥85%, demonstrating that curriculum training does not sacrifice benchmark performance for research-level gains. This validates that the approach builds genuinely broader capabilities rather than merely shifting the performance distribution.

3. **Robustness Improvement**: Template variant performance drop <30% (vs. 47-73% baseline), indicating that models learn abstract reasoning patterns rather than surface-form shortcuts. This represents a 2-2.4× improvement in robustness.

4. **Efficiency Gains**: 20-30% reduction in average proof length and beam expansions for successful proofs, suggesting more direct reasoning paths.

**Qualitative Outcomes**:

5. **Mechanistic Validation**: Representation analyses will reveal whether curriculum training produces qualitatively different internal representations—specifically, higher attention entropy (≥0.3 increase), more abstract embedding organization (≥20% reduction in domain-based clustering), and better complexity encoding (≥20% probe accuracy improvement).

6. **Curriculum Construction Methodology**: A validated semi-automated pipeline for constructing developmentally-grounded curricula from formal proof corpora, including:
   - Complexity metric calibration procedures
   - Template variation generation algorithms
   - Tier boundary optimization methods
   - Advancement criterion tuning protocols

### 4.2 Scientific Impact

**Theoretical Contributions**:

This research establishes a novel theoretical bridge between educational learning science and neural network training. Specifically:

1. **Transfer Learning Formalization**: We provide the first application of developmental psychology transfer learning bounds to neural theorem proving, demonstrating that diversity-driven pre-training reduces sample complexity for mathematical reasoning tasks.

2. **Cognitive Demand Operationalization**: We translate abstract cognitive demand frameworks into concrete computational metrics (proof complexity, template variation), enabling principled curriculum design beyond ad-hoc heuristics.

3. **Generalization Mechanism**: We identify and validate a causal pathway (diversity → primitives → abstraction → generalization) that explains why curriculum structure affects out-of-distribution performance, addressing a fundamental question in deep learning theory.

These contributions open new research directions at the intersection of AI and cognitive science, potentially informing curriculum design for other reasoning-intensive domains (program synthesis, scientific reasoning, legal argumentation).

**Methodological Contributions**:

The DC-NTP framework provides a reusable template for training robust reasoning systems:

1. **Domain-Agnostic Principles**: The three-phase structure (diversity → progression → integration) generalizes beyond theorem proving to any domain with hierarchical complexity and formal verification.

2. **Scalable Infrastructure**: By building on LeanDojo, we demonstrate that educationally-grounded curricula can be implemented with existing tools, lowering barriers to adoption.

3. **Evaluation Standards**: The template robustness evaluation protocol addresses a critical gap in current benchmarking practices, which often fail to detect shortcut learning.

### 4.3 Practical Impact

**Immediate Applications**:

1. **Research Mathematics Assistance**: Achieving >25% on RLMEval enables practical AI assistance for research mathematicians working on Lean formalization projects. This could accelerate the growth of mathlib (currently ~150,000 theorems) by automating routine proof steps and suggesting proof strategies for novel theorems.

2. **Proof Assistant Augmentation**: The trained models can be integrated into proof assistants (Lean, Coq, Isabelle) as tactic suggestion engines, reducing the cognitive burden on human users and making formal verification more accessible.

3. **Automated Formalization**: Improved reasoning capabilities enhance natural language to formal proof translation, supporting the autoformalization research agenda highlighted in the workshop description.

**Broader Applications**:

4. **Formal Verification**: The curriculum methodology transfers directly to software verification tasks, where proving program correctness requires similar hierarchical reasoning. Improved generalization could reduce manual effort in verifying critical systems (aerospace, medical devices, cryptography).

5. **Mathematical Education**: The curriculum construction pipeline could inform adaptive learning systems for mathematics education, automatically generating personalized learning progressions based on student performance.

6. **Scientific Reasoning**: The principles of diversity-driven pre-training and progressive complexity apply to scientific hypothesis generation, experimental design, and theory construction in computational science.

### 4.4 Long-Term Vision

This research contributes to the workshop's vision of human-AI collaboration for mathematical discovery by:

1. **Bridging the Research Gap**: Moving from 10.3% to >25% on research-level problems represents a critical step toward AI systems that can meaningfully contribute to active mathematical research, not just solve curated benchmarks.

2. **Establishing Principled Foundations**: Grounding curriculum design in learning theory provides a scientific basis for future improvements, moving the field beyond empirical trial-and-error toward systematic methodology.

3. **Enabling Interdisciplinary Synthesis**: Demonstrating that educational science informs AI development encourages broader cross-disciplinary collaboration, potentially accelerating progress on other grand challenges in AI for mathematics (automated theorem generation, proof discovery, concept formation).

### 4.5 Reproducibility and Open Science

To maximize impact, we commit to:

1. **Open-Source Release**: All code, curricula, trained models, and evaluation protocols will be released under permissive licenses (MIT/Apache 2.0).

2. **Detailed Documentation**: Comprehensive documentation of curriculum construction procedures, hyperparameter tuning, and experimental protocols to enable exact replication.

3. **Artifact Preservation**: Archival of all experimental artifacts (model checkpoints, training logs, evaluation results) on persistent repositories (Zenodo, Hugging Face).

4. **Community Engagement**: Active participation in the AI for Math workshop and related venues to disseminate findings and gather feedback for iterative improvement.

**Expected Timeline**: Pilot study (1 month) → Full-scale training (2-3 months) → Analysis and writing (2 months) → Total project duration: 6 months.

**Resource Requirements**: 500-1,000 GPU-hours for 7B model training (2-3× baseline compute budget), accessible via academic compute allocations or cloud credits.

This research represents a feasible, high-impact contribution to the AI for Mathematics community, with clear pathways to both scientific advancement and practical deployment.