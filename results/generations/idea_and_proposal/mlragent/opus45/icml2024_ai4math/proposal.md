# Research Proposal: Bidirectional Consistency Training for Autoformalization via Round-Trip Translation

## 1. Introduction

### Background

Autoformalization—the automated translation of natural language mathematics into machine-verifiable formal proofs—represents a critical frontier in artificial intelligence for mathematics. The ability to automatically convert the vast corpus of informal mathematical knowledge into formal specifications would revolutionize theorem proving, enable large-scale verification of mathematical results, and dramatically accelerate the development of formal mathematics libraries. Conversely, auto-informalization—translating formal proofs back into natural language—serves the equally important goal of making formal mathematics accessible to human mathematicians and learners.

Despite significant advances driven by large language models (LLMs), autoformalization remains fundamentally challenging. Current approaches face three interconnected problems. First, the scarcity of parallel corpora pairing natural language proofs with their formal counterparts severely limits supervised training. Second, semantic drift during translation causes formalized statements to diverge from the original mathematical meaning, often in subtle ways that are difficult to detect automatically. Third, the absence of reliable, automated evaluation metrics makes it challenging to assess translation quality and guide model improvement.

Recent work has begun addressing these challenges through various mechanisms. Li et al. (2024) introduced symbolic equivalence and semantic consistency scoring to select among multiple autoformalization candidates. Chen et al. (2025) proposed ReForm, which integrates semantic consistency evaluation with iterative self-correction. Huang et al. (2025) developed FormaRL, a reinforcement learning framework using Lean compiler feedback as reward signals. However, these approaches largely treat autoformalization and auto-informalization as separate tasks, missing the opportunity to leverage their inherent duality for mutual improvement.

### Research Objectives

This research proposes a novel **Bidirectional Consistency Training (BiCT)** framework that jointly optimizes autoformalization and auto-informalization through round-trip translation consistency. Our specific objectives are:

1. **Develop a cycle-consistency training framework** that uses round-trip translation fidelity as a self-supervised training signal, reducing dependence on scarce parallel data.

2. **Integrate formal verification constraints** from proof assistants (Lean 4, Coq) as hard constraints during training, ensuring syntactic correctness and logical validity.

3. **Design a learned semantic equivalence module** that captures mathematical meaning preservation beyond surface-level textual similarity.

4. **Establish new evaluation metrics** based on round-trip fidelity that correlate with human judgments of translation quality.

### Significance

This research addresses fundamental challenges in AI for mathematics with broad implications. By creating self-supervised training signals through bidirectional consistency, we can potentially unlock the vast reservoir of unpaired mathematical text for training. The framework provides interpretable natural language explanations of formal proofs as a byproduct, bridging the gap between formal verification and human understanding. Success in this endeavor would significantly reduce the human effort required to build formal mathematics libraries while advancing our understanding of how to encode mathematical semantics in neural systems.

## 2. Methodology

### 2.1 Framework Overview

The BiCT framework consists of four integrated components: (1) paired encoder-decoder models for bidirectional translation, (2) a cycle-consistency loss measuring round-trip fidelity, (3) formal verification integration providing hard constraints, and (4) a learned semantic equivalence classifier. Figure 1 illustrates the overall architecture.

### 2.2 Bidirectional Translation Models

We employ two transformer-based sequence-to-sequence models:

- **Formalizer** $\mathcal{F}_\theta$: Maps natural language mathematical statements $N$ to formal specifications $F$
- **Informalizer** $\mathcal{I}_\phi$: Maps formal specifications $F$ to natural language statements $N$

Both models are initialized from pretrained LLMs (e.g., DeepSeek-Prover or Llama-3) and fine-tuned jointly. For a natural language statement $N$, the forward cycle produces:

$$F = \mathcal{F}_\theta(N), \quad N' = \mathcal{I}_\phi(F)$$

Similarly, for a formal statement $F$, the backward cycle yields:

$$N = \mathcal{I}_\phi(F), \quad F' = \mathcal{F}_\theta(N)$$

### 2.3 Cycle-Consistency Loss

The core innovation is a multi-component cycle-consistency loss that enforces semantic preservation through round-trip translation.

**Semantic Similarity Loss**: We measure the semantic similarity between original and reconstructed statements using a learned embedding function $E(\cdot)$:

$$\mathcal{L}_{sem}^{N \to N'} = 1 - \cos(E(N), E(N'))$$

$$\mathcal{L}_{sem}^{F \to F'} = 1 - \cos(E_f(F), E_f(F'))$$

where $E$ operates on natural language and $E_f$ on formal language. We initialize these encoders from mathematical language models and fine-tune them as part of the training.

**Reconstruction Loss**: For cases with available parallel data, we include a direct reconstruction term:

$$\mathcal{L}_{rec} = -\log P_\theta(F^* | N) - \log P_\phi(N^* | F)$$

where $(N^*, F^*)$ are ground-truth pairs.

**Equivalence Classification Loss**: We train a binary classifier $C_\psi$ to predict whether two statements are semantically equivalent:

$$\mathcal{L}_{equiv} = -\mathbb{E}[\log C_\psi(N, N')] - \mathbb{E}[\log C_\psi(F, F')]$$

The total cycle-consistency loss combines these components:

$$\mathcal{L}_{cycle} = \lambda_1 \mathcal{L}_{sem} + \lambda_2 \mathcal{L}_{rec} + \lambda_3 \mathcal{L}_{equiv}$$

### 2.4 Formal Verification Integration

A critical component is the integration of proof assistants as hard constraints. For any formalization $F = \mathcal{F}_\theta(N)$, we require:

$$\text{TypeCheck}(F) = \text{True}$$

This is implemented through a verification reward in a reinforcement learning framework. Following the GRPO algorithm used in FormaRL, we define the reward function:

$$R(F | N) = \begin{cases} 
r_{base} + r_{semantic}(N, \mathcal{I}_\phi(F)) & \text{if TypeCheck}(F) = \text{True} \\
r_{penalty} & \text{otherwise}
\end{cases}$$

where $r_{semantic}(N, N') = \cos(E(N), E(N'))$ measures round-trip semantic consistency.

The policy gradient update for the formalizer becomes:

$$\nabla_\theta J = \mathbb{E}_{F \sim \mathcal{F}_\theta(\cdot|N)}[(R(F|N) - b) \nabla_\theta \log P_\theta(F|N)]$$

where $b$ is a baseline computed as the average reward.

### 2.5 Semantic Equivalence Classifier

The semantic equivalence classifier $C_\psi$ is trained on multiple sources of equivalence data:

1. **Theorem-level paraphrases**: Mathematical statements with known equivalence from textbook variations
2. **Formal equivalence**: Statements proven equivalent by automated theorem provers
3. **Synthetic negatives**: Statements with subtle semantic modifications

The classifier uses a cross-encoder architecture:

$$C_\psi(S_1, S_2) = \sigma(\text{MLP}([\text{CLS}]_{S_1 \oplus S_2}))$$

where $S_1 \oplus S_2$ denotes concatenation with a separator token.

### 2.6 Training Procedure

**Stage 1: Warm-up** (Supervised)
- Train $\mathcal{F}_\theta$ and $\mathcal{I}_\phi$ on available parallel data using $\mathcal{L}_{rec}$
- Train $C_\psi$ on curated equivalence dataset

**Stage 2: Cycle-Consistency Training** (Self-supervised)
- Alternate between forward cycles (N → F → N') and backward cycles (F → N → F')
- Apply $\mathcal{L}_{cycle}$ with formal verification filtering
- Use curriculum learning: start with simpler mathematical statements

**Stage 3: Reinforcement Learning Refinement**
- Fine-tune using policy gradients with verification rewards
- Incorporate human feedback on sample translations (optional)

### 2.7 Data Collection and Preparation

**Parallel Data Sources**:
- ProofNet dataset (Lean formalizations with informal statements)
- MiniF2F benchmark (competition problems in multiple formal languages)
- Mathlib documentation (Lean 4 library with docstrings)

**Unpaired Data Sources**:
- ArXiv mathematics papers (natural language)
- Mathlib, Archive of Formal Proofs (formal)
- Mathematics StackExchange (natural language proofs)

**Data Preprocessing**:
- Extract statement-proof pairs from LaTeX sources
- Normalize notation and terminology
- Filter by complexity (token count, nesting depth)

### 2.8 Experimental Design

**Benchmarks**:
1. **MiniF2F**: Standard autoformalization benchmark with competition problems
2. **ProofNet**: Undergraduate-level mathematics in Lean
3. **MATH-AF**: Newly curated test set from diverse mathematical domains

**Baselines**:
- LLM prompting (GPT-4, Claude, DeepSeek-Prover)
- ReForm (Chen et al., 2025)
- FormaRL (Huang et al., 2025)
- Supervised fine-tuning without cycle consistency

**Evaluation Metrics**:

1. **Type-Check Success Rate (TCSR)**: Percentage of formalizations that pass the proof assistant's type checker

2. **Semantic Equivalence Score (SES)**: Percentage judged semantically equivalent by $C_\psi$

3. **Round-Trip Fidelity (RTF)**: 
$$\text{RTF} = \frac{1}{|D|}\sum_{N \in D} \cos(E(N), E(\mathcal{I}_\phi(\mathcal{F}_\theta(N))))$$

4. **Bidirectional Equivalence (BEq)**: Following Liu et al. (2025), using automated theorem provers to verify logical equivalence

5. **Human Evaluation**: Expert mathematicians rate translation quality on a 5-point scale for accuracy, completeness, and naturalness

**Ablation Studies**:
- Effect of each loss component ($\mathcal{L}_{sem}$, $\mathcal{L}_{rec}$, $\mathcal{L}_{equiv}$)
- Impact of formal verification constraints
- Contribution of unpaired data through cycle training
- Comparison of different semantic embedding models

**Statistical Analysis**:
- Report mean and standard deviation over 5 random seeds
- Conduct paired t-tests for significance (p < 0.05)
- Analyze performance stratified by mathematical domain and complexity

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Autoformalization Accuracy**: We anticipate achieving 15-25% relative improvement in TCSR over state-of-the-art baselines on MiniF2F, with larger gains on complex multi-step proofs where semantic drift accumulates.

2. **Effective Use of Unpaired Data**: The cycle-consistency framework should enable training on 10× more data than purely supervised approaches, demonstrating that unpaired mathematical text provides meaningful training signal.

3. **New Evaluation Metrics**: Round-Trip Fidelity (RTF) will be validated against human judgments, establishing its utility as an automated evaluation metric with expected correlation > 0.75 with human ratings.

4. **High-Quality Auto-informalization**: As a byproduct, the trained informalizer will generate natural language explanations of formal proofs that are rated as clear and accurate by human evaluators.

5. **Released Resources**: We will release trained models, the semantic equivalence classifier, evaluation scripts, and the curated test set to facilitate future research.

### Broader Impact

**For Formal Mathematics**: By reducing the barrier to formalization, this work could accelerate the growth of formal mathematics libraries like Mathlib, making machine-verified mathematics more accessible to working mathematicians.

**For Mathematics Education**: Automated translation between formal and informal mathematics enables new educational tools that help students understand both the precision of formal systems and the intuition behind informal arguments.

**For Software Verification**: Techniques developed here transfer directly to formal specification of software requirements, where the gap between natural language specifications and formal contracts poses similar challenges.

**For AI Research**: The bidirectional consistency framework introduces a general paradigm for training translation systems between languages with different structural properties, applicable beyond mathematics to code generation, logical reasoning, and scientific knowledge representation.

### Limitations and Future Work

We acknowledge that our approach may struggle with highly context-dependent statements requiring background knowledge not present in the immediate input. Future work will integrate retrieval-augmented generation to address this. Additionally, while formal verification ensures syntactic correctness, logical validity of proofs (not just statements) requires deeper integration with theorem provers, which we leave to subsequent research.

In conclusion, this research proposes a principled framework for jointly improving autoformalization and auto-informalization through bidirectional consistency training, addressing key challenges in data scarcity, semantic preservation, and evaluation methodology that currently limit progress in AI for mathematics.