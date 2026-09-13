# Research Proposal: Learned Module Selection for Neuro-Symbolic Reasoning: Bridging LLMs and Symbolic Solvers via Adaptive Orchestration

## 1. Introduction

### 1.1 Background

The pursuit of Artificial General Intelligence (AGI) represents one of the most ambitious goals in computer science. While Large Language Models (LLMs) have demonstrated remarkable capabilities across diverse tasks—from natural language understanding to code generation—they exhibit fundamental limitations in multi-step logical reasoning requiring formal verification. These limitations manifest as hallucinations in mathematical proofs, inconsistent logical deductions, and inability to guarantee correctness in constraint satisfaction problems. Such deficiencies represent a critical barrier on the path toward AGI, where reliable reasoning across arbitrary domains is essential.

Symbolic AI systems, including satisfiability solvers (Z3, MiniSAT), theorem provers (Prover9), and answer set programming engines, provide complementary strengths: provable guarantees, systematic search, and formal verification capabilities. However, these systems require precise formal specifications and lack the flexibility and natural language understanding that LLMs provide. The integration of neural and symbolic approaches—neuro-symbolic integration (NSI)—has emerged as a promising paradigm for combining the strengths of both approaches.

Current approaches to NSI face significant challenges. Rule-based dispatch systems, exemplified by SymbolicAI frameworks, use keyword matching and heuristic rules to route problems to appropriate solvers. While simple to implement, these systems cannot adapt to the nuanced characteristics of diverse problems, leading to suboptimal solver selection. Alternatively, architectural fusion approaches attempt to embed symbolic reasoning directly within neural network architectures. However, as Šír (2024) demonstrates, such approaches encounter fundamental computational complexity barriers—static tensor graphs are computationally insufficient for general symbolic integration, limiting their scalability and applicability.

### 1.2 Research Objectives

This research proposes L-MSAL (Learned Module Selection for Augmented LLMs), a novel framework that addresses the limitations of existing NSI approaches through adaptive orchestration. Rather than fusing symbolic reasoning into neural architectures or relying on rigid rule-based dispatch, L-MSAL fine-tunes an LLM to learn optimal module selection while keeping symbolic solvers external. The primary objectives are:

1. **Develop a learned module selection mechanism** that adapts to problem characteristics through supervised fine-tuning on reasoning traces with explicit module selection labels.

2. **Demonstrate superior performance** over rule-based dispatch systems on established reasoning benchmarks (FOLIO, ProofWriter, GSM8K).

3. **Validate the scalability** of the approach with increasing numbers of available symbolic modules.

4. **Establish a practical framework** for neuro-symbolic integration that avoids computational complexity barriers while maintaining symbolic guarantees.

### 1.3 Significance

This research advances AGI development in several critical ways. First, it addresses the fundamental limitation of LLMs in formal reasoning by providing a scalable integration mechanism with symbolic solvers. Second, it bridges the gap between classic symbolic AI approaches and modern neural methods, drawing inspiration from historical AGI attempts while leveraging contemporary deep learning advances. Third, the proposed approach maintains the interpretability and verifiability of symbolic reasoning while benefiting from the flexibility and generalization capabilities of LLMs. Finally, by demonstrating that learned orchestration can outperform rule-based systems without architectural complexity, this work provides a practical pathway for deploying hybrid reasoning systems in real-world applications.

## 2. Methodology

### 2.1 System Architecture

L-MSAL consists of three primary components: (1) a fine-tuned LLM serving as the orchestrator, (2) a module library containing external symbolic solvers, and (3) an integration layer for result synthesis.

**Orchestrator LLM:** We employ Llama-3-8B-Instruct as the base model, fine-tuned using Low-Rank Adaptation (LoRA) with rank $r=16$ and scaling factor $\alpha=32$. The LoRA adaptation modifies the attention weight matrices:

$$W' = W + \frac{\alpha}{r} BA$$

where $W \in \mathbb{R}^{d \times k}$ is the original weight matrix, $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ are the low-rank adaptation matrices.

**Module Library:** The library contains $M$ symbolic solvers: $\mathcal{M} = \{m_1, m_2, ..., m_M\}$. Initial experiments use $M \in \{2, 5, 10\}$, including Z3 (SMT solving), Prover9 (first-order theorem proving), MiniSAT (SAT solving), and ASP solvers (answer set programming).

**Integration Layer:** Results from selected solvers are integrated into natural language responses through template-based synthesis with verification checks.

### 2.2 Training Data Generation

We construct a training dataset $\mathcal{D}$ of approximately 50,000 reasoning traces with explicit module selection labels. Each training instance is a triplet $(p, s, y)$ where $p$ is the problem statement, $s \in \mathcal{M}$ is the optimal module selection, and $y$ is the solution trace.

**Data Sources:**
- FOLIO training split: ~1,000 first-order logic problems
- ProofWriter: ~10,000 logical deduction problems
- GSM8K training split: ~7,500 mathematical reasoning problems
- Synthetic generation: ~31,500 problems from templates

**Labeling Procedure:** For each problem $p$, we execute all available solvers and label the optimal module as:

$$s^* = \arg\max_{m \in \mathcal{M}} \mathbb{1}[\text{correct}(m, p)] \cdot \frac{1}{\text{time}(m, p)}$$

This prioritizes correctness while preferring faster solvers among correct solutions.

### 2.3 Fine-Tuning Procedure

The fine-tuning objective combines module selection accuracy with reasoning quality:

$$\mathcal{L} = \lambda_1 \mathcal{L}_{\text{select}} + \lambda_2 \mathcal{L}_{\text{reason}}$$

where $\lambda_1 = 0.4$ and $\lambda_2 = 0.6$ balance the two objectives.

**Module Selection Loss:** Cross-entropy over module predictions:

$$\mathcal{L}_{\text{select}} = -\sum_{i=1}^{N} \sum_{m \in \mathcal{M}} y_{i,m} \log(\hat{p}_{i,m})$$

where $y_{i,m}$ is the ground-truth label and $\hat{p}_{i,m}$ is the predicted probability for module $m$ on instance $i$.

**Reasoning Loss:** Standard language modeling cross-entropy on solution traces:

$$\mathcal{L}_{\text{reason}} = -\sum_{i=1}^{N} \sum_{t=1}^{T_i} \log P(y_{i,t} | y_{i,<t}, p_i)$$

**Training Configuration:**
- Optimizer: AdamW with learning rate $2 \times 10^{-4}$
- Batch size: 16 with gradient accumulation over 4 steps
- Training epochs: 3
- Hardware: Single NVIDIA A100 (80GB)
- Estimated training time: ~8 GPU-hours

### 2.4 Inference Pipeline

During inference, L-MSAL processes problems through a three-stage pipeline:

**Stage 1 - Problem Analysis and Module Selection:**
Given input problem $p$, the fine-tuned LLM generates module selection probabilities:

$$\hat{p}_m = \text{softmax}(f_\theta(p))_m \quad \forall m \in \mathcal{M}$$

Modules with $\hat{p}_m > \tau$ (threshold $\tau = 0.3$) are selected for execution.

**Stage 2 - Parallel Solver Execution:**
Selected modules execute in parallel via tool-calling APIs:

$$r_m = \text{Execute}(m, \text{Formalize}(p)) \quad \forall m \in \mathcal{S}$$

where $\mathcal{S} \subseteq \mathcal{M}$ is the selected module set and $\text{Formalize}(p)$ converts the natural language problem to solver-compatible format.

**Stage 3 - Result Integration:**
Solver results are aggregated and synthesized into a natural language response:

$$y = \text{Integrate}(p, \{(m, r_m) : m \in \mathcal{S}\})$$

with verification checks ensuring consistency across multiple solver outputs.

### 2.5 Experimental Design

**Benchmarks:**
1. **FOLIO** (First-Order Logic): 1,004 problems testing first-order logical reasoning
2. **ProofWriter** (Logical Deduction): 2,000 problems across 5 depth levels
3. **GSM8K** (Mathematical Reasoning): 1,319 test problems requiring multi-step arithmetic

**Baseline Systems:**
1. **Pure LLM:** Llama-3-8B-Instruct without symbolic augmentation
2. **Rule-based Dispatch (SymbolicAI):** Keyword-matching heuristics for module selection
3. **Random Selection:** Uniform random module selection as lower bound

**Experimental Conditions:**
- Module counts: $M \in \{2, 5, 10\}$
- Runs per condition: $n = 25$ with different random seeds
- Fixed seeds across conditions for paired comparisons

**Evaluation Metrics:**

*Primary Metrics:*
- **Reasoning Accuracy:** $\text{Acc} = \frac{\text{correct answers}}{\text{total problems}} \times 100\%$
- **Module Selection Precision:** $\text{Prec} = \frac{\text{correct selections}}{\text{total selections}} \times 100\%$

*Secondary Metrics:*
- **Inference Latency:** Mean time per problem (ms)
- **GPU Memory Usage:** Peak memory during inference (GB)
- **Solver Utilization:** Fraction of problems routed to each solver

### 2.6 Statistical Analysis

**Primary Hypothesis Test:**
Paired t-test comparing L-MSAL accuracy against rule-based dispatch:

$$t = \frac{\bar{d}}{s_d / \sqrt{n}}$$

where $\bar{d}$ is the mean accuracy difference and $s_d$ is the standard deviation of differences.

**Sample Size Justification:**
For Cohen's $d = 0.5$ (medium effect), $\alpha = 0.05$, power $= 0.8$:

$$n \geq \frac{2(z_{\alpha/2} + z_\beta)^2}{d^2} \approx 25$$

**Multiple Comparison Correction:**
Bonferroni correction for 3 pairwise comparisons: $\alpha_{\text{adj}} = 0.05/3 = 0.0167$

**Effect Size Reporting:**
Cohen's $d$ with 95% confidence intervals for all comparisons.

### 2.7 Ablation Studies

To validate the causal mechanism, we conduct ablations:

1. **Selection Mechanism Ablation:** Compare learned selection vs. random initialization after identical training epochs
2. **Training Data Size:** Evaluate performance with 10K, 25K, and 50K training traces
3. **LoRA Rank Ablation:** Test $r \in \{4, 8, 16, 32\}$ to assess adaptation capacity requirements
4. **Module Count Scaling:** Measure accuracy and latency as $M$ increases from 2 to 10

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcomes:**
We hypothesize that L-MSAL will achieve:
- Reasoning accuracy improvement of $\geq 5$ percentage points over rule-based dispatch (e.g., 78% → 83%) with statistical significance ($p < 0.05$)
- Module selection precision $\geq 80\%$ compared to $< 60\%$ for random baseline
- Cohen's $d \geq 0.5$ (medium effect size) for accuracy comparisons

**Benchmark-Specific Predictions:**
- FOLIO: Largest improvement expected due to direct mapping to first-order logic solvers
- ProofWriter: Moderate improvement with depth-dependent gains
- GSM8K: Improvement primarily on problems requiring constraint verification

**Scalability Outcomes:**
- Accuracy improvement with increasing module count without proportional latency increase
- Inference time $< 10\times$ pure LLM baseline while maintaining accuracy gains

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. $\text{Acc}(\text{L-MSAL}) \leq \text{Acc}(\text{SymbolicAI})$ after full training
2. Module selection precision $< 60\%$ (worse than informed random)
3. $\text{Acc}(\text{L-MSAL}) < \text{Acc}(\text{Pure LLM})$ on any benchmark
4. Inference time $> 10\times$ pure LLM with no accuracy improvement

### 3.3 Scientific Impact

This research contributes to AGI development by:

1. **Demonstrating Scalable NSI:** Providing empirical evidence that learned orchestration can overcome the computational complexity barriers of architectural fusion while maintaining symbolic guarantees.

2. **Bridging Classic and Modern AI:** Showing how insights from symbolic AI can be effectively integrated with LLMs through adaptive mechanisms rather than rigid rules.

3. **Establishing Evaluation Framework:** Creating benchmarks and metrics for assessing neuro-symbolic integration quality beyond simple accuracy measures.

4. **Informing AGI Architecture Design:** Providing evidence for modular, interface-based designs over monolithic architectures in hybrid reasoning systems.

### 3.4 Practical Impact

**Immediate Applications:**
- Educational AI systems requiring verified mathematical reasoning
- Legal and compliance systems needing formal logical verification
- Scientific discovery tools combining natural language understanding with formal proof

**Broader Implications:**
- Reduced computational requirements for deploying hybrid reasoning systems
- Improved interpretability through explicit module selection decisions
- Foundation for extending to additional symbolic reasoning modules

### 3.5 Limitations and Future Work

**Known Limitations:**
- Requires curated training data with module-problem mappings
- May not generalize to entirely novel module types
- Performance depends on solver coverage for problem types
- Single GPU requirement may limit accessibility

**Future Directions:**
- Reinforcement learning for module selection without explicit labels
- Extension to visual and multimodal reasoning with appropriate solvers
- Meta-learning for rapid adaptation to new module types
- Distributed execution for real-time applications

This research represents a significant step toward AGI by demonstrating that the fundamental limitation of LLMs in formal reasoning can be addressed through learned neuro-symbolic integration without sacrificing scalability or practicality.