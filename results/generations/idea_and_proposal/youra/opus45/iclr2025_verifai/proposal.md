# Research Proposal: Step-Level Verification-Guided Generation for Formal Reasoning in Large Language Models

## 1. Introduction

### 1.1 Background

The intersection of generative artificial intelligence and formal verification represents one of the most promising frontiers in computer science research. Large language models (LLMs) have demonstrated remarkable capabilities in generating code, mathematical proofs, and structured reasoning artifacts. However, these probabilistic systems fundamentally differ from traditional formal methods in their approach to correctness: while formal verification tools provide mathematical guarantees through construction, LLMs generate outputs based on learned statistical patterns without inherent correctness assurances.

In formal reasoning domains such as theorem proving and verified code generation, errors exhibit a particularly problematic characteristic: they compound across sequential reasoning steps. A single incorrect tactic in a proof or an erroneous assertion in a program can invalidate all subsequent reasoning, leading to cascading failures that waste computational resources and produce unusable outputs. Current state-of-the-art approaches predominantly employ claim-level verification, where feedback is provided only after complete generation. This paradigm misses critical opportunities for early error correction and forces models to regenerate entire proofs or programs when errors are detected late in the process.

Recent advances have explored various integration strategies between LLMs and formal methods. Grammar-constrained decoding approaches enforce syntactic validity during generation but lack semantic verification depth. Iterative refinement methods like VERGE achieve significant improvements through post-hoc correction cycles but still operate at the claim level. Meanwhile, systems like Seed-Prover have demonstrated impressive results on theorem proving benchmarks through whole-proof refinement with Lean feedback, achieving near-saturation on miniF2F. However, these approaches do not fully exploit the potential of incremental verification during the generation process itself.

### 1.2 Research Objectives

This research proposes Step-Level Verification-Guided Generation (SL-VGG), a novel framework that integrates incremental formal verification directly into the LLM decoding process. Our primary objectives are:

1. **Develop an efficient step-level verification integration architecture** that provides real-time feedback during generation without prohibitive computational overhead.

2. **Design a structured feedback encoding mechanism** that translates verification signals into representations that effectively condition subsequent token generation.

3. **Establish a dense reward framework for reinforcement learning** that leverages step-level verification signals to improve model training efficiency and final performance.

4. **Empirically validate the hypothesis** that step-level feedback exceeds claim-level approaches by at least 5% verification correctness in compounding-error formal domains.

### 1.3 Research Significance

This research addresses a fundamental challenge in trustworthy AI systems: how to combine the scalability and adaptability of generative AI with the correctness guarantees of formal methods. The significance extends across multiple dimensions:

**Theoretical Contribution:** SL-VGG provides a principled framework for understanding how verification granularity affects error propagation in sequential reasoning tasks, establishing causal mechanisms that explain when and why step-level feedback outperforms alternatives.

**Practical Impact:** By reducing error propagation and regeneration cycles, SL-VGG can significantly improve the efficiency of AI-assisted formal verification workflows, making these tools more accessible to practitioners.

**Methodological Advancement:** The proposed feedback encoding and dense reward mechanisms contribute reusable techniques applicable beyond theorem proving and code generation to any domain with incremental verification support.

## 2. Methodology

### 2.1 System Architecture Overview

SL-VGG consists of three integrated components: (1) an incremental verification module, (2) a feedback encoding layer, and (3) a verification-conditioned decoder. The system operates in a tight loop where each generated step triggers verification, and the resulting feedback conditions subsequent generation.

### 2.2 Incremental Verification Module

The verification module provides real-time validity checking for partial generations. We implement two verification backends:

**Lean 4 Tactic Verification:** For theorem proving, we leverage Lean 4's incremental type checking capabilities. After each tactic $t_i$ is generated, the module attempts to apply it to the current proof state $s_{i-1}$:

$$V_{\text{Lean}}(t_i, s_{i-1}) = \begin{cases} (1, \emptyset, s_i) & \text{if } t_i \text{ succeeds} \\ (0, e, \text{hints}(e)) & \text{if } t_i \text{ fails with error } e \end{cases}$$

where the output tuple contains a validity bit, error information, and either the new proof state or correction hints.

**Z3 SMT Verification:** For verified code generation, we employ Z3's incremental solving mode. Given a program with assertions $A = \{a_1, ..., a_n\}$, after generating assertion $a_i$, we check:

$$V_{\text{Z3}}(a_i, A_{<i}) = \begin{cases} (1, \emptyset, \text{model}) & \text{if } \text{SAT}(A_{<i} \cup \{a_i\}) \\ (0, \text{core}, \text{hints}(\text{core})) & \text{if } \text{UNSAT with core} \end{cases}$$

To ensure efficiency, we implement query caching and incremental solving. The target latency is $<50$ms per verification step, achieved through:
- Maintaining persistent solver instances across steps
- Caching intermediate proof states in Lean 4
- Using push/pop operations in Z3 for incremental constraint management

### 2.3 Feedback Encoding Layer

The verification output is encoded into a structured representation suitable for conditioning the LLM. We define a 3-part feedback signal $F_i$ for step $i$:

$$F_i = (v_i, \mathbf{e}_i, \mathbf{h}_i)$$

where:
- $v_i \in \{0, 1\}$ is the validity bit
- $\mathbf{e}_i \in \mathbb{R}^{d_e}$ is an error type embedding (zero vector if valid)
- $\mathbf{h}_i \in \mathbb{R}^{d_h}$ is a correction hint embedding

The error type embedding is computed by passing the error message through a frozen encoder:

$$\mathbf{e}_i = \text{Encoder}_{\text{error}}(\text{error\_message}_i)$$

Correction hints are generated by a learned hint generator that maps error types to actionable suggestions:

$$\mathbf{h}_i = \text{MLP}_{\text{hint}}(\mathbf{e}_i, \text{context}_i)$$

The complete feedback embedding is:

$$\mathbf{f}_i = \text{LayerNorm}(W_v v_i + W_e \mathbf{e}_i + W_h \mathbf{h}_i)$$

where $W_v, W_e, W_h$ are learned projection matrices.

### 2.4 Verification-Conditioned Decoder

We modify a standard transformer decoder to incorporate verification feedback via cross-attention. Let $\mathbf{H}^{(l)}$ denote the hidden states at layer $l$. We insert verification cross-attention after every $k$ layers:

$$\mathbf{H}^{(l)}_{\text{ver}} = \text{CrossAttn}(\mathbf{H}^{(l)}, \mathbf{F}_{1:i}) + \mathbf{H}^{(l)}$$

where $\mathbf{F}_{1:i} = [\mathbf{f}_1, ..., \mathbf{f}_i]$ is the sequence of feedback embeddings for all previous steps.

The cross-attention mechanism is defined as:

$$\text{CrossAttn}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

with $Q = \mathbf{H}^{(l)}W_Q$, $K = \mathbf{F}_{1:i}W_K$, $V = \mathbf{F}_{1:i}W_V$.

### 2.5 Training Procedure

Training proceeds in two phases:

**Phase 1: Supervised Fine-Tuning (SFT)**

We fine-tune the base LLM on successful proof/code traces with step-level verification annotations. The loss function is:

$$\mathcal{L}_{\text{SFT}} = -\sum_{i=1}^{N} \log P(t_i | t_{<i}, \mathbf{F}_{<i})$$

**Phase 2: Reinforcement Learning with Dense Rewards**

We employ Proximal Policy Optimization (PPO) with step-level rewards derived from verification feedback:

$$r_i = \begin{cases} r_{\text{valid}} & \text{if } v_i = 1 \\ r_{\text{invalid}} + \alpha \cdot \text{sim}(t_{i+1}, \text{hint}_i) & \text{if } v_i = 0 \text{ and recovered} \\ r_{\text{terminal}} & \text{if } v_i = 0 \text{ and not recovered} \end{cases}$$

where $r_{\text{valid}} > 0$, $r_{\text{invalid}} < 0$, $r_{\text{terminal}} \ll 0$, and $\alpha$ weights the recovery bonus based on hint utilization.

The PPO objective is:

$$\mathcal{L}_{\text{PPO}} = \mathbb{E}\left[\min\left(\rho_t A_t, \text{clip}(\rho_t, 1-\epsilon, 1+\epsilon)A_t\right)\right]$$

where $\rho_t = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ and $A_t$ is the advantage computed using step-level rewards.

### 2.6 Data Collection

**Theorem Proving Data:** We utilize LeanDojo to extract tactic-level proof traces from Mathlib4. Each trace includes:
- Initial goal state
- Sequence of tactics with intermediate proof states
- Verification status after each tactic
- Error messages for failed attempts (from proof search logs)

We construct approximately 100,000 training examples with step-level annotations.

**Verified Code Data:** We use the CLEVER benchmark and extend it with Z3 verification traces. Each example includes:
- Natural language specification
- Code with embedded assertions
- Incremental verification results
- SMT solver feedback for failed assertions

### 2.7 Experimental Design

**Baselines:**
1. **Unconstrained LLM:** Standard autoregressive generation without verification
2. **Grammar-Constrained (CRANE-style):** Syntactic constraints during decoding
3. **Claim-Level (VERGE-style):** Post-hoc verification with iterative refinement
4. **Seed-Prover:** State-of-the-art whole-proof refinement

**Benchmarks:**
- **miniF2F-Lean:** 488 formalized mathematical problems (primary benchmark)
- **CLEVER:** Verified code generation benchmark
- **ProofNet:** Additional theorem proving evaluation

**Evaluation Metrics:**

1. **Verification Correctness Rate (VCR):**
$$\text{VCR} = \frac{\text{Number of fully verified outputs}}{\text{Total number of problems}} \times 100\%$$

2. **Error Recovery Rate (ERR):**
$$\text{ERR} = \frac{\text{Recovered generations after initial failure}}{\text{Total initial failures}} \times 100\%$$

3. **Generation Efficiency (GE):**
$$\text{GE} = \frac{\text{Total generation time (SL-VGG)}}{\text{Total generation time (unconstrained)}}$$

4. **Step-Level Accuracy (SLA):**
$$\text{SLA} = \frac{\text{Valid steps generated}}{\text{Total steps generated}} \times 100\%$$

**Statistical Analysis:**

We conduct $n = 25$ independent runs with different random seeds. Statistical significance is assessed using paired t-tests with $\alpha = 0.05$ (one-tailed). We target Cohen's $d = 0.5$ effect size with statistical power $\beta = 0.8$.

**Ablation Studies:**

1. **Feedback Granularity:** Compare step-level vs. every-$k$-steps vs. claim-level
2. **Feedback Components:** Ablate validity bit, error embedding, and hints independently
3. **Cross-Attention Frequency:** Vary insertion frequency of verification cross-attention
4. **Verification Latency:** Artificially vary verification delay to assess efficiency bounds

### 2.8 Implementation Details

- **Base Model:** 7B parameter decoder-only transformer (Llama-2 architecture)
- **Training Infrastructure:** 8× A100 GPUs, approximately 1 week for RL fine-tuning
- **Verification Backends:** Lean 4.3.0, Z3 4.12.0
- **Frameworks:** PyTorch, Hugging Face Transformers, LeanDojo

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Verification Correctness:** We predict SL-VGG will achieve >75% verification correctness on miniF2F-Lean, representing a statistically significant improvement over the current 70% ± 10% state-of-the-art. This improvement stems from early error detection preventing the compounding failures that plague claim-level approaches.

**Error Recovery:** We expect ≥70% error recovery rate compared to ≤50% for claim-level methods. The dense feedback signals enable the model to learn effective correction strategies, reducing the need for complete regeneration.

**Efficiency:** Total generation time should remain <2× the unconstrained baseline. While step-level verification introduces overhead, this is offset by reduced regeneration cycles and earlier termination of invalid proof attempts.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. Verification correctness rate ≤60% (primary failure)
2. Error recovery rate <50% (mechanism failure)
3. Generation time >3× unconstrained baseline (efficiency failure)

These criteria ensure rigorous evaluation and prevent confirmation bias.

### 3.3 Scientific Impact

This research contributes to the theoretical understanding of verification granularity in neural-symbolic systems. The causal mechanism analysis will clarify when step-level feedback provides genuine advantages over alternatives, establishing boundary conditions for the approach's applicability.

### 3.4 Practical Impact

**Formal Verification Workflows:** SL-VGG can significantly accelerate AI-assisted theorem proving and verified code generation, making these tools more practical for real-world software development and mathematical research.

**Trustworthy AI Systems:** By integrating formal guarantees into the generation process, SL-VGG advances the goal of building AI systems whose outputs can be trusted in safety-critical applications.

**Benchmark Contributions:** The step-level annotated datasets created for this research will benefit the broader community working at the intersection of LLMs and formal methods.

### 3.5 Limitations and Future Work

The approach currently depends on verification backends with incremental solving support (Lean 4, Z3). Future work will explore extending to other proof assistants (Coq, Isabelle) and verification tools. Additionally, the computational overhead, while acceptable, motivates research into more efficient verification integration strategies, potentially through learned verification approximations that maintain correctness guarantees.