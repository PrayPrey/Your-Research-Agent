# Neural-Guided Proof Repair: Learning to Fix Intermediate Step Errors in Automated Theorem Proving

## 1. Introduction

### Background

Mathematical reasoning represents one of the pinnacle achievements of human intelligence, characterized by the ability to construct rigorous logical arguments and discover fundamental truths about abstract structures. In recent years, the artificial intelligence community has made remarkable strides in automated theorem proving (ATP), with systems demonstrating increasing capability in generating formal proofs for mathematical statements. However, a critical bottleneck persists: the accumulation of intermediate step errors that derail proof attempts and severely limit the reliability of current ATP systems.

Unlike human mathematicians who can identify mistakes, backtrack, and apply corrective reasoning, current neural theorem provers often fail silently or propagate errors through subsequent proof steps. When a proof attempt fails, these systems typically restart from scratch rather than diagnosing and repairing the specific errors. This limitation is particularly problematic because proof construction is inherently exploratory—even expert mathematicians make mistakes during proof development and rely heavily on iterative refinement.

Recent work has begun addressing aspects of this challenge. Lyra introduced dual correction mechanisms for tool and conjecture correction, achieving significant improvements on the miniF2F benchmark. APOLLO demonstrated the value of automated error analysis and fixing through collaboration between LLMs and the Lean compiler. ProofBridge integrated iterative proof repair with retrieval-augmented generation, while ProofNet++ employed self-correction mechanisms within a neuro-symbolic framework. However, these approaches primarily focus on surface-level syntactic corrections or rely on expensive sampling-based strategies rather than learning systematic repair patterns from proof development histories.

### Research Objectives

This research proposes a comprehensive neural-guided proof repair framework that addresses intermediate step errors through three key innovations:

1. **Intelligent Error Localization**: Develop a multi-modal classifier that identifies erroneous proof steps by analyzing proof state inconsistencies, type-checking failures, semantic drift from proof goals, and learned patterns from historical proof corrections.

2. **Context-Aware Repair Generation**: Design a transformer-based repair model that generates targeted corrections by learning from large-scale proof edit histories, capturing both local tactical repairs and global strategic adjustments.

3. **Verification-in-the-Loop Learning**: Integrate formal verification as both a validation mechanism and a source of self-supervised learning signals, enabling continuous improvement of repair strategies.

### Significance

This research has profound implications for multiple dimensions of AI-assisted mathematical reasoning:

**Reliability Enhancement**: By systematically addressing intermediate errors rather than abandoning failed proof attempts, the proposed framework will significantly improve proof success rates and reduce the computational cost of theorem proving.

**Human-AI Collaboration**: The error localization and repair suggestions will provide interpretable feedback to human mathematicians, facilitating more effective collaboration between human intuition and machine computation.

**Cross-Domain Impact**: The techniques developed for proof repair generalize naturally to software verification and formal code generation, where identifying and correcting errors in formal specifications is equally critical.

**Knowledge Discovery**: The learned repair patterns will illuminate common proof pathologies and successful correction strategies, potentially revealing insights about mathematical reasoning itself.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

#### Proof Corpus Construction

We will construct a comprehensive dataset from multiple sources:

**Interactive Proof Development Histories**: Extract complete edit histories from formal proof assistants including Lean 4, Coq, and Isabelle/HOL. These repositories contain invaluable information about how proofs evolve from initial attempts to completed proofs, capturing both successful and failed intermediate states.

**Synthetic Error Injection**: Systematically generate synthetic errors by:
- Applying incorrect tactics at intermediate steps
- Introducing type mismatches through term substitution
- Creating goal-hypothesis inconsistencies
- Mutating proof terms while preserving syntactic validity

**Human Annotation**: Collect expert annotations for a subset of 5,000 proof failures, where experienced theorem proving practitioners identify error locations and suggest repair strategies.

#### Data Representation

Each training instance will be represented as:
$$\mathcal{D} = \{(P_i, e_i, R_i, v_i)\}_{i=1}^N$$

where:
- $P_i$ represents a proof attempt with partial proof state
- $e_i$ denotes the error location (step index)
- $R_i$ is the repair action or corrected proof segment
- $v_i$ is the verification outcome (binary)

The proof state at step $t$ is formalized as:
$$S_t = (\Gamma_t, G_t, T_{1:t}, H_t)$$

where $\Gamma_t$ is the local context, $G_t$ is the current goal, $T_{1:t}$ is the tactic sequence applied so far, and $H_t$ is the hypothesis set.

### 2.2 Error Localization Module

#### Architecture

The error localization module employs a hierarchical architecture combining:

**Step-Level Encoder**: A graph neural network (GNN) that processes each proof step as a node, with edges representing logical dependencies. Each step is encoded as:
$$\mathbf{h}_t^{(0)} = \text{Embed}(S_t) = [\mathbf{e}_\Gamma; \mathbf{e}_G; \mathbf{e}_T; \mathbf{e}_H]$$

where $\mathbf{e}_\Gamma, \mathbf{e}_G, \mathbf{e}_T, \mathbf{e}_H$ are learned embeddings of the context, goal, tactic, and hypotheses respectively.

**Multi-Head Attention Mechanism**: Apply graph attention to propagate information across proof steps:
$$\mathbf{h}_t^{(l+1)} = \text{MultiHead}\left(\sum_{s \in \mathcal{N}(t)} \alpha_{ts} \mathbf{W}^{(l)} \mathbf{h}_s^{(l)}\right)$$

where $\mathcal{N}(t)$ represents steps that step $t$ depends on, and $\alpha_{ts}$ are learned attention weights.

**Error Scoring**: For each step $t$, compute an error probability:
$$p_{\text{error}}(t) = \sigma(\mathbf{w}^\top \mathbf{h}_t^{(L)} + b)$$

where $\sigma$ is the sigmoid function and $L$ is the number of GNN layers.

#### Training Objective

The error localization module is trained with a combination of:

**Cross-Entropy Loss** for binary error classification:
$$\mathcal{L}_{\text{CE}} = -\sum_{t=1}^{|P|} \left[y_t \log p_{\text{error}}(t) + (1-y_t) \log(1-p_{\text{error}}(t))\right]$$

**Ranking Loss** to prioritize earlier errors:
$$\mathcal{L}_{\text{rank}} = \sum_{t_e < t_c} \max(0, \gamma + p_{\text{error}}(t_c) - p_{\text{error}}(t_e))$$

where $t_e$ is an error step, $t_c$ is a correct step that follows, and $\gamma$ is a margin hyperparameter.

### 2.3 Repair Strategy Generator

#### Model Architecture

The repair generator is based on a transformer encoder-decoder architecture with domain-specific modifications:

**Input Representation**: For an identified error at step $t^*$, construct input sequence:
$$X = [\text{CLS}; S_{t^*-k:t^*}; \text{SEP}; \text{ERROR}; \text{SEP}; S_{t^*+1:t^*+k'}]$$

This provides $k$ steps of context before the error and $k'$ steps after, along with error indication.

**Proof-Aware Attention**: Implement custom attention masks that respect proof structure dependencies:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}} + M_{\text{proof}}\right)V$$

where $M_{\text{proof}}$ is a learned mask encoding logical dependencies.

**Decoder with Tactic Vocabulary**: The decoder generates repairs using a hierarchical vocabulary:
1. High-level repair strategy (e.g., "strengthen hypothesis", "change tactic", "insert lemma")
2. Specific tactics or terms from the formal proof language

#### Training Strategy

**Supervised Learning Phase**: Train on collected proof edits:
$$\mathcal{L}_{\text{repair}} = -\log P(R | P, e; \theta)$$

**Reinforcement Learning Phase**: Fine-tune using policy gradient methods where the reward $r$ is determined by verification success:
$$\mathcal{L}_{\text{RL}} = -\mathbb{E}_{R \sim \pi_\theta}[r(R, P, e) \log \pi_\theta(R | P, e)]$$

The reward function incorporates:
- Verification success: $r_{\text{verify}} \in \{-1, +10\}$
- Minimal edit distance: $r_{\text{edit}} = -\alpha \cdot d_{\text{edit}}(R, P)$
- Proof length penalty: $r_{\text{length}} = -\beta \cdot |R|$

Total reward: $r = r_{\text{verify}} + r_{\text{edit}} + r_{\text{length}}$

### 2.4 Verification-in-the-Loop Integration

#### Formal Verification Interface

Integrate with proof assistant kernels (Lean, Coq) through:

**Type Checking**: Every generated repair $R$ is submitted for type checking:
$$\text{TypeCheck}(R, \Gamma_t) \rightarrow \{\text{valid}, \text{invalid}\}$$

**Proof State Validation**: Ensure repaired proof advances toward the goal:
$$\text{ValidateProgress}(S_t, S_{t+1}) = \text{distance}(S_t.G, \text{goal}) > \text{distance}(S_{t+1}.G, \text{goal})$$

#### Self-Supervised Learning Loop

Use verification outcomes to generate additional training data:

1. **Success Case Mining**: When a repair succeeds, store $(P, e, R, 1)$ as positive example
2. **Failure Analysis**: When repair fails, extract error messages and update error patterns
3. **Counterfactual Generation**: For successful repairs, generate near-miss alternatives as negative examples

This creates a continuous learning cycle:
$$\mathcal{D}_{t+1} = \mathcal{D}_t \cup \{(P, e, R, v) : v = \text{Verify}(R, P, e)\}$$

### 2.5 Experimental Design

#### Benchmarks and Baselines

**Datasets**:
- miniF2F: 488 formalized problems from mathematics competitions
- Lean mathlib: Real-world mathematical library with 150K+ theorems
- CoqGym: 71K human-written proofs from Coq projects
- Custom benchmark: 1000 deliberately incomplete proofs requiring repair

**Baseline Methods**:
1. Beam search without repair (current standard)
2. Lyra (tool and conjecture correction)
3. APOLLO (automated error fixing)
4. ProofBridge (iterative repair with retrieval)
5. Random repair selection
6. Template-based repair heuristics

#### Evaluation Metrics

**Success Rate Improvement**:
$$\text{Improvement} = \frac{\text{Proofs}_{\text{with\_repair}} - \text{Proofs}_{\text{baseline}}}{\text{Proofs}_{\text{baseline}}} \times 100\%$$

**Error Localization Accuracy**:
- Precision@k: Fraction of top-k predictions that include actual error
- Mean Average Precision (MAP) across all proof attempts

**Repair Quality**:
- Verification success rate: Percentage of repairs that type-check
- Edit distance: Average number of modifications from original
- Proof efficiency: Final proof length compared to human-written proofs

**Computational Efficiency**:
- Time to successful proof (compared to restart-based approaches)
- Number of repair iterations required
- Token consumption for LLM-based components

#### Ablation Studies

Systematically evaluate components:
1. Error localization only vs. full pipeline
2. Impact of proof context window size ($k$ and $k'$)
3. Supervised learning vs. RL fine-tuning
4. Different verification integration strategies
5. Effect of synthetic data augmentation

#### Statistical Analysis

Perform significance testing using:
- Paired t-tests for comparing success rates on same problem sets
- Bootstrap confidence intervals (10,000 samples) for metric stability
- Cohen's d for effect size measurement

## 3. Expected Outcomes & Impact

### Expected Research Outcomes

**Quantitative Improvements**: Based on preliminary experiments and literature analysis, we anticipate:
- 15-25% improvement in proof success rates on miniF2F benchmark over current state-of-the-art
- 80%+ precision@5 for error localization on annotated test set
- 60%+ repair verification success rate, representing 3-4× improvement over random repair selection
- 40% reduction in computational cost (measured in LLM tokens or proof search time) compared to restart-based approaches

**Novel Methodological Contributions**:

1. **First comprehensive error taxonomy for ATP**: Systematic categorization of proof step errors derived from analysis of 100K+ proof attempts, including:
   - Tactical errors (wrong tactic selection)
   - Semantic drift (proof diverging from goal)
   - Incompleteness (missing intermediate lemmas)
   - Type mismatches (term-level errors)

2. **Learned repair patterns**: A repository of repair strategies extracted from successful corrections, providing interpretable insights into proof debugging processes.

3. **Benchmark for proof repair**: A curated dataset of 1000 incomplete proofs with expert annotations, establishing standardized evaluation for future research.

### Scientific Impact

**Advancing AI for Mathematics**: This research directly addresses one of the workshop's core themes—relieving intermediate step errors in theorem proving. By enabling systems to learn from mistakes rather than failing silently, we move closer to robust, deployable ATP systems that can genuinely assist mathematicians.

**Cross-Pollination with Formal Verification**: The proof repair techniques translate directly to software verification, where identifying and correcting errors in formal specifications of code is equally critical. Our framework can be adapted to repair:
- Incorrect program invariants
- Flawed security protocol specifications  
- Buggy compiler optimizations with formal correctness proofs

**Neurosymbolic Reasoning Insights**: The integration of neural learning with symbolic verification provides a template for neurosymbolic systems more broadly, demonstrating how formal methods can guide and validate neural predictions.

### Practical Applications

**Educational Tools**: The error localization module can provide real-time feedback to students learning formal theorem proving, identifying exactly where their proof attempts go wrong and suggesting corrections—a significant enhancement over current proof assistants that simply reject invalid proofs.

**Accelerating Formalization Projects**: Large-scale formalization efforts (e.g., formalizing undergraduate mathematics curriculum) would benefit enormously from automated repair, reducing the tedious debugging phase that currently consumes significant expert time.

**Industry Adoption of Formal Methods**: By making formal verification more robust and user-friendly, this research lowers barriers to adoption in safety-critical industries (aerospace, medical devices, financial systems) where provably correct software is essential.

### Long-Term Vision

This research represents a step toward **collaborative theorem proving** where AI systems serve as intelligent assistants that:
- Catch and correct errors in real-time during proof development
- Suggest alternative proof strategies when current approaches stall
- Learn organizational preferences and proof styles from human collaborators

Ultimately, we envision proof repair capabilities as a fundamental component of next-generation proof assistants, analogous to how modern IDEs provide intelligent code completion and error correction for programming. This would transform formal mathematics from a niche discipline requiring extensive training into a more accessible tool for rigorous reasoning across scientific disciplines.

### Broader Implications

**Trustworthy AI**: As AI systems are deployed in high-stakes decision-making, the ability to formally verify their behavior becomes critical. This research contributes to the foundational capability of automatically repairing formal specifications, enhancing our ability to build provably safe AI systems.

**Scientific Discovery**: By making theorem proving more reliable and efficient, we accelerate the pace at which new mathematical results can be discovered and verified, potentially enabling AI systems to contribute meaningfully to mathematical knowledge creation.

**Democratization of Formal Methods**: Lowering the expertise barrier for formal verification through intelligent error repair could bring rigorous formal methods to broader communities of software developers, scientists, and engineers who currently find formal tools too difficult to use effectively.

In conclusion, this research on neural-guided proof repair addresses a critical bottleneck in automated theorem proving while establishing methodological foundations that extend to formal verification, code generation, and neurosymbolic reasoning more broadly. By teaching AI systems to learn from mistakes rather than simply avoiding them, we move toward more robust, reliable, and practically useful AI assistants for mathematical reasoning.