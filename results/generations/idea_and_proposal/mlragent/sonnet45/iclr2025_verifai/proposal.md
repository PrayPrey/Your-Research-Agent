# Neural-Symbolic Repair: Self-Correcting LLM Code Generation via Iterative Formal Feedback Synthesis

## 1. Introduction

### Background

The rapid advancement of Large Language Models (LLMs) has revolutionized code generation, with tools like GitHub Copilot, ChatGPT, and specialized models demonstrating remarkable capabilities in translating natural language specifications into executable code. However, a critical challenge persists: LLM-generated code frequently contains subtle bugs that evade basic testing yet violate formal specifications or exhibit edge-case failures. These failures can manifest as type inconsistencies, null pointer dereferences, contract violations, or incorrect boundary condition handling—issues that are particularly problematic in safety-critical domains such as embedded systems, automotive software, and financial applications.

While formal verification tools—including static analyzers, symbolic executors, and Satisfiability Modulo Theories (SMT) solvers—excel at detecting such violations, they typically produce low-level, technical error messages designed for expert human developers. These messages often reference abstract syntax tree nodes, constraint violations, or symbolic execution paths that are incomprehensible to LLMs without explicit grounding in the code's semantic structure. Recent studies have shown that directly feeding raw verification outputs to LLMs for self-correction yields limited success, with models struggling to identify the root cause and apply appropriate fixes.

This disconnect represents a fundamental impedance mismatch between two paradigms: the precision-oriented, formal methods community that demands correctness guarantees, and the probabilistic, scale-driven approach of modern generative AI. Bridging this gap requires a translation layer that can convert formal verification feedback into actionable repair guidance that leverages LLMs' natural language understanding and code manipulation capabilities.

### Research Objectives

This research proposes **Neural-Symbolic Repair**, a framework that synthesizes the strengths of formal verification and neural code generation through an iterative feedback loop augmented with intelligent feedback synthesis. The primary objectives are:

1. **Design a Feedback Synthesis Layer**: Develop a specialized component that transforms low-level formal verification outputs into structured, natural language repair prompts containing explanations, counterexamples, and location-specific repair hints.

2. **Implement Multi-Tool Verification Pipeline**: Integrate diverse formal analysis tools (static analyzers, symbolic executors, SMT solvers) to detect different classes of errors and generate comprehensive feedback.

3. **Enable Iterative Self-Correction**: Create an iterative repair mechanism where LLMs consume synthesized feedback to generate progressively refined code versions until verification succeeds or a termination criterion is met.

4. **Establish Evaluation Framework**: Develop benchmarks and metrics to assess repair effectiveness, iteration efficiency, and the quality of synthesized feedback across diverse programming tasks and error types.

### Significance

This research addresses critical needs at the intersection of formal methods and AI-driven code generation:

- **Practical Impact**: Enhances the reliability of LLM-based code generation tools, making them viable for safety-critical applications where correctness guarantees are essential.

- **Theoretical Contribution**: Provides insights into how neural and symbolic approaches can be synergistically combined, advancing our understanding of hybrid AI architectures.

- **Community Resources**: Delivers a curated dataset of verification-guided repairs, enabling future research on learning-based program repair and formal feedback interpretation.

- **Alignment with Workshop Themes**: Directly addresses the VerifAI workshop's focus on integrating formal methods with generative AI, particularly the special theme of enhancing LLM-driven code generation through programming languages and formal methods techniques.

## 2. Methodology

### 2.1 System Architecture

The Neural-Symbolic Repair framework consists of four primary components operating in an iterative loop:

**Component 1: Initial Code Generation Module**
- Input: Natural language specification $S$ and optional context (function signatures, library dependencies)
- Process: Query LLM $\mathcal{M}$ with carefully designed prompts to generate initial code $C_0$
- Output: Candidate code implementation $C_0$

**Component 2: Multi-Tool Formal Verification Module**
- Input: Code $C_i$ at iteration $i$
- Process: Apply verification tools $\mathcal{V} = \{v_1, v_2, ..., v_k\}$ in parallel
  - Static analyzers (e.g., Infer, Clang Static Analyzer) for type safety, null pointer checks
  - Symbolic executors (e.g., KLEE, Symbolic PathFinder) for path exploration
  - SMT solvers (e.g., Z3, CVC5) for contract verification
- Output: Set of verification results $\mathcal{R}_i = \{r_1, r_2, ..., r_m\}$ where each $r_j$ contains error type, location, and raw diagnostic information

**Component 3: Feedback Synthesis Module**
- Input: Verification results $\mathcal{R}_i$, original specification $S$, code $C_i$
- Process: Transform raw verification outputs into structured repair prompts
- Output: Synthesized feedback $F_i$ containing natural language explanations, counterexamples, and repair hints

**Component 4: Iterative Repair Module**
- Input: Code $C_i$, synthesized feedback $F_i$, specification $S$
- Process: Prompt LLM with context-enriched repair request
- Output: Refined code $C_{i+1}$

### 2.2 Feedback Synthesis Layer Design

The feedback synthesis layer is the core innovation of this framework. We propose a two-stage approach:

**Stage 1: Error Categorization and Localization**

For each verification result $r_j \in \mathcal{R}_i$, extract:
- Error type $\tau_j$ (e.g., NullPointerException, ArrayIndexOutOfBounds, ContractViolation)
- Source location $\ell_j$ (file, line number, code span)
- Diagnostic message $d_j$ (raw tool output)

Construct a structured representation:
$$E_j = (\tau_j, \ell_j, d_j, C_i[\ell_j])$$

where $C_i[\ell_j]$ denotes the code snippet at location $\ell_j$.

**Stage 2: Neural Feedback Generation**

Train a smaller, specialized model $\mathcal{F}$ (e.g., fine-tuned T5, CodeT5+, or GPT-3.5) on a dataset of $(E, F)$ pairs where:
- $E$ represents structured error information
- $F$ represents expert-written repair guidance

The synthesis model generates feedback following a template structure:

$$F_i = \mathcal{F}(E_1, E_2, ..., E_m, S, C_i)$$

Each feedback component $f_j$ for error $E_j$ contains:

1. **Natural Language Explanation**: 
   - "The verification tool detected a potential null pointer dereference at line X. This occurs because variable `var` may be null when accessed in the conditional statement."

2. **Concrete Counterexample** (when available from symbolic execution):
   - "Execution trace: Input values [a=0, b=-1] lead to array index -1, violating array bounds."

3. **Repair Hints**:
   - "Consider adding a null check before accessing `var`."
   - "Ensure the index variable is validated against array bounds."
   - "Review the loop termination condition at line Y."

4. **Code Location Markers**:
   - Highlight specific lines and expressions requiring attention

The complete synthesized feedback is formatted as:

```
Verification identified {m} issues in your code:

Issue 1 [{error_type_1}] at line {line_1}:
- Explanation: {explanation_1}
- Counterexample: {counterexample_1}
- Suggestion: {repair_hint_1}
- Code: {code_snippet_1}

[Repeat for each issue...]

Please revise the code to address these issues while maintaining 
the original specification: {S}
```

### 2.3 Training the Feedback Synthesis Model

**Data Collection**:

We will create a training dataset through three strategies:

1. **Automated Pipeline**: Generate code using existing LLMs, run verification tools, collect error outputs. For successful repairs (from LLM self-correction or human intervention), record $(E, F)$ pairs.

2. **Human Annotation**: Recruit expert developers to write repair guidance for verification errors in open-source repositories.

3. **Synthesis from Existing Datasets**: Leverage program repair datasets (e.g., Defects4J, BugsInPy) and augment with verification tool outputs.

Target dataset size: 10,000+ $(E, F)$ pairs covering diverse error types and programming languages (Python, Java, C/C++).

**Training Procedure**:

Fine-tune a pre-trained code-aware language model using supervised learning:

$$\mathcal{L} = -\sum_{(E,F) \in \mathcal{D}} \log P_{\mathcal{F}}(F | E, S, C)$$

Employ techniques such as:
- Curriculum learning: Start with simple error types, progressively introduce complex cases
- Multi-task learning: Joint training on explanation generation, counterexample extraction, and hint synthesis
- Reinforcement learning from repair success: Reward feedback that leads to successful verification in subsequent iterations

### 2.4 Iterative Repair Algorithm

The complete repair process follows this algorithm:

```
Algorithm: Neural-Symbolic Repair
Input: Specification S, LLM M, Verification tools V, Feedback synthesizer F
Output: Verified code C* or failure after max_iterations

1. C_0 ← M.generate(S)
2. iteration ← 0
3. while iteration < max_iterations:
4.     R ← apply_verification(C_iteration, V)
5.     if R indicates all checks passed:
6.         return C_iteration  // Success
7.     F ← synthesize_feedback(R, S, C_iteration)
8.     C_{iteration+1} ← M.repair(C_iteration, F, S)
9.     if C_{iteration+1} == C_iteration:
10.        break  // Convergence detected
11.    iteration ← iteration + 1
12. return FAILURE
```

**Key Design Decisions**:

- **Max Iterations**: Set to 5 based on preliminary experiments showing diminishing returns beyond this point
- **Convergence Detection**: Stop if code remains unchanged between iterations to avoid infinite loops
- **Prompt Engineering**: Use few-shot examples of successful repairs in repair prompts to guide the LLM

### 2.5 Experimental Design

**Dataset Construction**:

1. **Specification-to-Code Benchmark**: Curate 500 programming problems from:
   - LeetCode/CodeForces (algorithmic problems)
   - Real-world GitHub issues with specifications
   - Safety-critical code snippets (automotive, embedded systems)

2. **Error Injection**: For existing correct implementations, systematically inject errors detectable by verification tools to create a controlled testbed.

**Baseline Comparisons**:

- **Raw Feedback**: Directly feed verification tool outputs to LLM without synthesis
- **Simple Translation**: Use rule-based templates to convert errors to natural language
- **Self-Debugging**: LLM attempts repair without external verification feedback
- **Human-in-the-Loop**: Expert developers provide repair guidance (upper bound)

**Evaluation Metrics**:

1. **Repair Success Rate**: 
$$\text{RSR} = \frac{\text{Number of successfully verified codes}}{\text{Total problems}}$$

2. **Average Repair Iterations**:
$$\text{ARI} = \frac{\sum_{i=1}^{n} \text{iterations}_i}{\text{successful repairs}}$$

3. **Fix Quality**: Measure via:
   - Test case pass rate
   - Code similarity to reference solutions (CodeBLEU score)
   - Performance benchmarks (execution time, memory usage)

4. **Feedback Quality**: Human evaluation on:
   - Clarity (1-5 scale)
   - Actionability (1-5 scale)
   - Accuracy of error explanation

5. **Efficiency Metrics**:
   - Time to successful verification
   - Computational cost (API calls, verification tool runtime)

**Ablation Studies**:

- Impact of individual verification tools (static analysis only, symbolic execution only, etc.)
- Effect of feedback components (explanations vs. counterexamples vs. hints)
- Influence of synthesis model size and architecture
- Role of few-shot examples in repair prompts

**Statistical Analysis**:

Apply paired t-tests and Wilcoxon signed-rank tests to assess statistical significance of improvements over baselines (p < 0.05).

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Primary Research Contributions**:

1. **Novel Framework**: A production-ready neural-symbolic repair system demonstrating 40-60% improvement in repair success rates over baseline approaches, particularly for complex error types (contract violations, symbolic execution failures).

2. **Feedback Synthesis Model**: A trained, open-source model capable of translating formal verification outputs into actionable repair guidance, achieving >80% human-rated clarity and actionability scores.

3. **Benchmark Dataset**: A curated collection of 500+ specification-code pairs with annotated verification errors and expert repair guidance, serving as a resource for future research in program repair and formal methods integration.

4. **Empirical Insights**: Comprehensive analysis revealing:
   - Which error types benefit most from synthesized feedback
   - Optimal iteration counts for different problem complexities
   - Effectiveness of different verification tool combinations
   - Limitations of LLM self-correction capabilities

**Quantitative Targets**:

- **Repair Success Rate**: 70-80% on benchmark problems (compared to 30-40% for raw feedback baselines)
- **Iteration Efficiency**: Reduce average iterations from 4-5 to 2-3 through better feedback quality
- **Feedback Synthesis Accuracy**: 85%+ correlation with human expert feedback
- **Code Quality**: Generated code passes 90%+ of test cases and maintains performance within 10% of reference implementations

### Broader Impact

**Advancing Formal Methods Accessibility**:

By making formal verification feedback interpretable to LLMs, this research democratizes access to correctness guarantees traditionally requiring expert knowledge. Developers can leverage powerful verification tools through natural language interfaces, lowering barriers to adoption in industry.

**Enhancing AI Safety and Reliability**:

The framework provides a pathway for deploying LLM-based code generation in safety-critical contexts (medical devices, autonomous vehicles, aerospace) where correctness is non-negotiable. This addresses growing concerns about AI-generated code reliability.

**Bridging Academic Communities**:

This work creates concrete touchpoints between the programming languages, formal methods, and machine learning communities, fostering interdisciplinary collaboration and knowledge transfer.

**Industry Applications**:

- **Developer Tools**: Integration into IDEs and code review platforms to provide verification-aware code suggestions
- **Automated Testing**: Generate test cases guided by symbolic execution counterexamples
- **Legacy Code Modernization**: Apply formal verification to detect issues in existing codebases and automatically generate patches

**Educational Value**:

The synthesized feedback serves as educational material, helping developers understand formal verification concepts through concrete examples in their code.

### Limitations and Future Directions

**Acknowledged Limitations**:

1. **Verification Tool Coverage**: Not all code properties are verifiable with current tools; dynamic behaviors and concurrency remain challenging.

2. **Scalability**: Verification tools may struggle with large codebases; initial focus on function-level verification.

3. **Language Specificity**: Initial implementation targets Python and Java; extending to low-resource languages requires additional effort.

4. **LLM Capabilities**: Inherent limitations in LLM reasoning may prevent repair of deeply flawed designs.

**Future Research Directions**:

- **Learning from Repair Trajectories**: Use successful repair sequences to fine-tune LLMs specifically for verification-guided correction
- **Multi-Agent Collaboration**: Explore specialized LLMs for different error types working in concert
- **Proof-Carrying Code**: Extend to generate formal proofs alongside code
- **Interactive Repair**: Incorporate human feedback when automated repair stalls
- **Cross-Language Transfer**: Investigate whether feedback synthesis models generalize across programming languages

### Alignment with Workshop Goals

This research directly addresses multiple VerifAI workshop themes:

- **Generative AI for Formal Methods**: Demonstrates how LLMs can leverage formal verification tools effectively through intelligent feedback translation
- **Formal Methods for Generative AI**: Integrates verification tools as quality gates for LLM outputs
- **Datasets and Benchmarks**: Contributes a novel benchmark for verification-guided code repair
- **Special Theme (LLMs for Code Generation)**: Exemplifies integration of formal structures (verification tools) with LLM code generation, with potential applications to low-resource languages through transfer learning

The proposal offers both methodological innovation and practical tooling, fostering discussion on the future of trustworthy AI-driven software development. By demonstrating concrete improvements in repair success rates and providing open-source implementations, this work aims to catalyze broader adoption of neural-symbolic approaches in production code generation systems.