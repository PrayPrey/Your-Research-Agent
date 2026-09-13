# Research Proposal: Specification Inference from Natural Language for LLM Code Generation Verification

## 1. Introduction

### Background

The proliferation of large language models (LLMs) for code generation has fundamentally transformed software development practices. Tools like GitHub Copilot, CodeWhisperer, and open-source alternatives now assist millions of developers in writing code from natural language descriptions. However, this convenience comes with significant risks: LLM-generated code can contain subtle bugs, security vulnerabilities, and logical errors that appear syntactically correct but fail to satisfy the user's actual intent. Recent work on code hallucinations (Agarwal et al., 2024) has demonstrated that LLMs frequently produce plausible but incorrect code snippets, underscoring the critical need for verification mechanisms.

Formal verification offers mathematically rigorous guarantees about program correctness through techniques such as theorem proving, model checking, and SMT solving. These methods require precise formal specifications—pre-conditions, post-conditions, and invariants—that define expected program behavior. Systems like VeCoGen (Sevenhuijsen et al., 2024) have shown promising results in generating formally verified code when specifications are provided. Similarly, FVEL (Lin et al., 2024) demonstrates that interactive theorem proving can verify LLM-generated code against formal properties.

However, a fundamental gap persists: users describe their requirements in natural language, not formal specifications. This disconnect creates a critical bottleneck where either (1) expensive human experts must manually translate requirements into specifications, or (2) verification is simply skipped, leaving potentially unsafe code unverified. PAT-Agent (Zuo et al., 2025) addresses this for model checking through autoformalization, and SLD-Spec (Chen et al., 2025) enhances specification generation for complex loops, yet neither provides a comprehensive framework for translating arbitrary natural language requirements into verifiable specifications for general code generation.

### Research Objectives

This research proposes **SpecBridge**, a novel two-stage framework that automatically infers formal specifications from natural language requirements and uses these specifications to guide and verify LLM-generated code. Our specific objectives are:

1. **Develop a specification inference model** that translates natural language requirements into formal pre/post-conditions and loop invariants through fine-tuning on curated datasets of verified codebases.

2. **Design a consistency-checking mechanism** that validates generated specifications against natural language intent using diverse test scenario generation and ensemble disagreement detection.

3. **Create an integrated verification pipeline** that combines specification inference, guided code generation, and SMT-based verification with iterative refinement.

4. **Evaluate the framework** on established benchmarks and real-world code generation tasks, measuring specification accuracy, verification success rates, and ambiguity detection capabilities.

### Significance

This research addresses the VerifAI workshop's special theme on LLMs for code generation by bridging the accessibility gap between informal user intent and formal verification. By automating specification inference, we enable practical formal verification for everyday LLM code generation, potentially transforming how developers interact with AI coding assistants. The framework's ambiguity detection mechanism provides an additional safety layer by explicitly identifying underspecified requirements before code generation, reducing the risk of generating code that satisfies an incorrect interpretation of user intent.

## 2. Methodology

### 2.1 System Architecture Overview

SpecBridge consists of four interconnected components: (1) Specification Inference Module, (2) Consistency Checking Module, (3) Guided Code Generation Module, and (4) Verification and Refinement Module. The system processes natural language requirements through a pipeline that produces formally verified code or identifies ambiguities requiring user clarification.

### 2.2 Specification Inference Module

#### Dataset Construction

We construct a training dataset $\mathcal{D} = \{(n_i, s_i, c_i)\}_{i=1}^{N}$ where $n_i$ represents natural language descriptions, $s_i$ represents formal specifications, and $c_i$ represents verified code implementations. Data sources include:

- **Verified codebases**: ACSL-annotated C programs, Dafny programs with specifications, and JML-annotated Java code
- **Theorem prover libraries**: Isabelle/HOL and Coq proof libraries with natural language documentation
- **Synthetic generation**: Using existing verified code to generate natural language descriptions via back-translation

For each specification $s_i$, we represent it as a tuple:
$$s_i = (\text{Pre}_i, \text{Post}_i, \text{Inv}_i, \text{Types}_i)$$
where $\text{Pre}_i$ denotes preconditions, $\text{Post}_i$ denotes postconditions, $\text{Inv}_i$ denotes loop invariants, and $\text{Types}_i$ denotes type constraints.

#### Fine-tuning Approach

We fine-tune a base LLM $\mathcal{M}_{\text{spec}}$ using a multi-task learning objective:

$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{pre}} + \lambda_2 \mathcal{L}_{\text{post}} + \lambda_3 \mathcal{L}_{\text{inv}} + \lambda_4 \mathcal{L}_{\text{type}}$$

where each component loss $\mathcal{L}_k$ is the cross-entropy loss for generating the corresponding specification component. The multi-task formulation enables the model to learn correlations between different specification types.

#### Ensemble Generation

For each natural language input $n$, we generate $K$ diverse specification candidates using temperature sampling:
$$S_{\text{candidates}} = \{\hat{s}_1, \hat{s}_2, ..., \hat{s}_K\} \sim \mathcal{M}_{\text{spec}}(n; \tau)$$
where $\tau$ is a temperature parameter that controls diversity.

### 2.3 Consistency Checking Module

#### Specification Satisfiability Verification

Before proceeding to code generation, we verify that generated specifications are satisfiable using an SMT solver. For a specification $\hat{s} = (\text{Pre}, \text{Post}, \text{Inv}, \text{Types})$, we check:

$$\text{SAT}(\text{Pre} \land \text{Types}) \neq \text{UNSAT}$$

and verify that there exists at least one execution path from precondition to postcondition:

$$\text{SAT}(\text{Pre} \land \text{Trans} \land \text{Post}) \neq \text{UNSAT}$$

where $\text{Trans}$ represents abstract transition constraints inferred from the specification structure.

#### Test Scenario Generation for Intent Validation

We generate diverse test scenarios $T = \{t_1, t_2, ..., t_M\}$ using a separate LLM $\mathcal{M}_{\text{test}}$ prompted with the original natural language requirement:

$$t_j = (\text{input}_j, \text{expected\_output}_j, \text{description}_j)$$

Each test scenario is then checked against the formal specification:
$$\text{Valid}(t_j, \hat{s}) = \text{Pre}(\text{input}_j) \implies \text{Post}(\text{input}_j, \text{expected\_output}_j)$$

#### Ensemble Disagreement Detection

We compute the disagreement score across specification candidates:

$$D(S_{\text{candidates}}) = 1 - \frac{1}{K(K-1)} \sum_{i \neq j} \text{Equiv}(\hat{s}_i, \hat{s}_j)$$

where $\text{Equiv}(\hat{s}_i, \hat{s}_j)$ measures semantic equivalence between specifications using SMT-based equivalence checking:

$$\text{Equiv}(\hat{s}_i, \hat{s}_j) = \begin{cases} 1 & \text{if SAT}((\hat{s}_i \land \neg\hat{s}_j) \lor (\neg\hat{s}_i \land \hat{s}_j)) = \text{UNSAT} \\ 0 & \text{otherwise} \end{cases}$$

When $D(S_{\text{candidates}}) > \theta_D$ (a threshold hyperparameter), the system flags the requirement as ambiguous and generates clarifying questions based on the disagreement points.

### 2.4 Guided Code Generation Module

Once a specification $\hat{s}^*$ is selected (either the highest-confidence candidate or user-approved after clarification), we guide code generation using specification-aware prompting:

$$c = \mathcal{M}_{\text{code}}(n, \hat{s}^*, \text{examples})$$

where $\text{examples}$ are retrieved similar verified implementations. The prompt structure includes:
1. The original natural language requirement
2. The formal specification with explanation
3. Few-shot examples of specification-satisfying code
4. Explicit instructions to respect specification constraints

### 2.5 Verification and Refinement Module

#### SMT-Based Verification

We employ bounded model checking with an SMT solver (Z3) to verify the generated code against specifications. For a function $f$ with specification $\hat{s}^* = (\text{Pre}, \text{Post}, \text{Inv})$, we encode the verification condition:

$$\text{VC}(f, \hat{s}^*) = \forall \vec{x}. \text{Pre}(\vec{x}) \implies \text{Post}(\vec{x}, f(\vec{x}))$$

For loops, we verify partial correctness using Hoare logic:
$$\{\text{Pre} \land \text{Inv}\} \ \text{loop\_body} \ \{\text{Inv}\}$$
$$\{\text{Inv} \land \neg\text{guard}\} \implies \text{Post}$$

#### Iterative Refinement

When verification fails, we implement a counterexample-guided refinement loop similar to PAT-Agent's approach:

1. Extract counterexample $\text{cex}$ from SMT solver
2. Generate diagnostic message explaining the violation
3. Re-prompt code generation with counterexample context:
$$c' = \mathcal{M}_{\text{code}}(n, \hat{s}^*, c, \text{cex}, \text{diagnostic})$$
4. Repeat until verification succeeds or maximum iterations reached

### 2.6 Experimental Design

#### Datasets and Benchmarks

We evaluate SpecBridge on:
- **HumanEval-Spec**: Extended HumanEval with formal specifications (created as part of this work)
- **MBPP-Spec**: Extended MBPP with specifications
- **Code2Inv**: Loop invariant inference benchmark
- **SV-COMP**: Software verification competition benchmarks
- **Real-world Dataset**: Curated GitHub issues with associated pull requests and tests

#### Evaluation Metrics

1. **Specification Accuracy** ($\text{Acc}_{\text{spec}}$): Percentage of generated specifications that are semantically equivalent to ground truth:
$$\text{Acc}_{\text{spec}} = \frac{|\{i : \text{Equiv}(\hat{s}_i, s_i^{\text{gt}})\}|}{N}$$

2. **Verification Success Rate** ($\text{VSR}$): Percentage of generated code that passes formal verification:
$$\text{VSR} = \frac{|\{i : \text{Verify}(c_i, \hat{s}_i) = \text{PASS}\}|}{N}$$

3. **Functional Correctness** ($\text{Pass}@k$): Standard pass@k metric on test cases

4. **Ambiguity Detection Precision/Recall**: Measured against human-annotated ambiguous requirements

5. **End-to-End Latency**: Time from natural language input to verified code output

#### Baselines

We compare against:
- Direct LLM code generation without specifications (GPT-4, Claude, CodeLlama)
- VeCoGen with manually written specifications
- LLM + simple test-based verification
- FVEL for post-hoc verification

#### Ablation Studies

We conduct ablations on:
- Number of specification candidates $K$
- Ensemble disagreement threshold $\theta_D$
- With/without satisfiability pre-checking
- With/without counterexample-guided refinement

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Verification Rates**: We anticipate achieving 60-75% formal verification success on HumanEval-Spec, compared to <30% for unguided generation, based on preliminary experiments and related work results.

2. **Accurate Specification Inference**: Target 70%+ specification accuracy on benchmarks, with clear identification of challenging cases (complex loops, concurrent code).

3. **Effective Ambiguity Detection**: Precision >80% and recall >70% in identifying genuinely ambiguous requirements, reducing downstream errors from misinterpreted intent.

4. **Practical Efficiency**: End-to-end latency under 60 seconds for typical function-level code generation tasks, making the approach viable for interactive development.

5. **Open-Source Artifacts**: Release of the fine-tuned specification inference model, HumanEval-Spec and MBPP-Spec benchmark datasets, and the complete SpecBridge implementation.

### Research Impact

**Bridging Communities**: This work directly addresses the VerifAI workshop's goal of bridging formal methods and generative AI. By automating the specification inference bottleneck, we make formal verification accessible to developers who lack formal methods expertise.

**Advancing Code Generation Safety**: As LLM-generated code becomes ubiquitous, ensuring its correctness becomes critical. SpecBridge provides a practical path toward trustworthy AI-assisted programming.

**Enabling New Workflows**: The ambiguity detection mechanism transforms the developer experience from "generate and hope" to "clarify and verify," promoting more intentional software development practices.

**Foundation for Future Work**: The specification inference model and consistency-checking framework can extend to other domains requiring formal guarantees, including smart contracts, safety-critical systems, and automated theorem proving.

### Limitations and Future Directions

We acknowledge current limitations including reliance on SMT decidability (restricting expressible properties), potential scalability challenges for large codebases, and dependence on training data quality. Future work will explore integration with runtime verification for undecidable properties, hierarchical specification for system-level verification, and active learning approaches to improve specification quality with minimal user feedback.