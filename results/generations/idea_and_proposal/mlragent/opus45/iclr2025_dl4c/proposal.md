# Research Proposal: Execution-Guided Self-Play for Code Agent Alignment

## 1. Introduction

### Background

The rapid advancement of large language models (LLMs) has transformed the landscape of automated code generation, enabling AI systems to assist developers with increasingly complex programming tasks. From simple function completions to resolving GitHub issues and developing entire software modules, code agents are becoming integral to modern software engineering workflows. However, despite remarkable progress, current code generation agents struggle with complex, multi-step programming tasks that require iterative refinement, debugging, and adaptation based on execution outcomes.

Reinforcement Learning from Human Feedback (RLHF) has emerged as a powerful paradigm for aligning language models with human preferences. While successful in general-purpose language tasks, applying RLHF to code generation faces unique challenges. Obtaining high-quality human feedback for code is expensive, requires domain expertise, and fundamentally cannot scale to the volume of training data needed for robust code agents. Recent work, including CosmoCore (Ravindran, 2025) and crowd-sourced RLHF approaches (Wong & Tan, 2025), has attempted to address these scaling limitations, but the dependency on human annotation remains a significant bottleneck.

A natural alternative to human feedback in the code domain is execution feedback—the rich signals generated when code is actually run. Unlike natural language, code can be objectively evaluated through compilation, test execution, and runtime behavior analysis. However, naively using binary pass/fail signals leads to sparse rewards that cause unstable training dynamics. The recent Process Reward Model approach (Dai et al., 2024) and execution-guided generation methods (Lavon et al., 2025) have begun to explore denser feedback signals, but these approaches lack the continuous self-improvement loop necessary for scalable alignment.

Self-play methods, where an agent learns by interacting with itself, have shown remarkable success in game-playing domains and are now being explored for code generation. The Sol-Ver framework (Lin et al., 2025) and Self-Challenging approach (Zhou et al., 2025) demonstrate the potential of self-play for code, but they do not fully leverage the structured nature of execution feedback to create fine-grained training signals.

### Research Objectives

This research proposes **ExePlay**, a novel self-play framework for code agent alignment that addresses the fundamental challenge of scalable, human-feedback-free training. Our specific objectives are:

1. **Develop a structured execution feedback mechanism** that extracts rich, multi-dimensional signals from code execution, moving beyond binary pass/fail to capture partial correctness, error proximity, and behavioral similarity.

2. **Design a critique generation module** that transforms execution traces into natural language explanations, enabling the model to learn not just from outcomes but from the reasoning about failures.

3. **Create a contrastive alignment algorithm** that constructs weighted preference pairs from self-generated solutions, leveraging execution signal richness for stable training.

4. **Validate the approach** on challenging agentic coding benchmarks including SWE-Bench, demonstrating significant improvements without any human feedback.

### Significance

This research addresses a critical gap in the post-training and alignment landscape for code generation models. By eliminating the dependency on human feedback while providing richer training signals than existing automated methods, ExePlay has the potential to enable continuous, scalable improvement of code agents. The framework contributes to open science practices by relying entirely on automated, reproducible feedback mechanisms, and advances the broader goal of developing agents capable of solving realistic software development tasks.

## 2. Methodology

### 2.1 Overview of the ExePlay Framework

ExePlay operates as a cyclical self-improvement system comprising three interconnected phases: Generation, Critique Generation, and Contrastive Alignment. The framework assumes access to a base code generation model $M_\theta$, a set of programming tasks $\mathcal{T}$ with associated test suites, and an execution environment $\mathcal{E}$.

### 2.2 Phase 1: Generation and Execution Feedback Collection

Given a programming task $t \in \mathcal{T}$ with problem description $d_t$ and test suite $\{(x_i, y_i)\}_{i=1}^n$, the agent generates $K$ candidate solutions:

$$S_t = \{s_1, s_2, ..., s_K\} \sim M_\theta(\cdot | d_t)$$

Each solution $s_j$ is executed in the sandboxed environment $\mathcal{E}$, producing an execution trace $E_j$ that captures:

- **Compilation status**: Whether the code successfully compiles/parses
- **Test results**: For each test case $i$, the tuple $(pass_i, output_i, expected_i, error_i)$
- **Stack traces**: Full error traces for runtime exceptions
- **Coverage information**: Line and branch coverage metrics
- **Runtime behavior**: Execution time, memory usage, and intermediate states

We define the **Structured Execution Feedback (SEF)** as a comprehensive representation:

$$SEF(s_j) = (c_j, \mathbf{r}_j, \mathbf{e}_j, \text{cov}_j, \mathbf{b}_j)$$

where $c_j \in \{0, 1\}$ is compilation status, $\mathbf{r}_j \in \{0, 1\}^n$ is the test result vector, $\mathbf{e}_j$ is the set of error messages, $\text{cov}_j \in [0, 1]$ is coverage ratio, and $\mathbf{b}_j$ captures behavioral features.

### 2.3 Phase 2: Critique Generation

The critique generation module leverages the same base model $M_\theta$ with a specialized critique prompt to analyze execution failures. For each failed solution $s_j$, we construct:

$$\text{critique}_j = M_\theta(\cdot | p_{\text{critique}}, d_t, s_j, SEF(s_j))$$

where $p_{\text{critique}}$ is a carefully designed prompt that instructs the model to:

1. Identify the specific lines causing failures based on stack traces
2. Explain the logical error in natural language
3. Hypothesize the correct behavior
4. Suggest concrete fixes

The critique serves dual purposes: (1) it provides interpretable feedback for the contrastive learning phase, and (2) it can be used for self-repair attempts, generating improved solutions:

$$s_j^{\text{repair}} = M_\theta(\cdot | d_t, s_j, \text{critique}_j)$$

### 2.4 Phase 3: Contrastive Alignment with Execution-Weighted Preferences

The core innovation of ExePlay lies in constructing fine-grained preference pairs weighted by execution signal richness. Unlike binary preference learning, we compute a continuous **Execution Quality Score (EQS)** for each solution:

$$EQS(s_j) = \alpha \cdot \frac{\sum_{i=1}^n r_{j,i}}{n} + \beta \cdot \text{cov}_j + \gamma \cdot \text{ErrorProximity}(s_j) + \delta \cdot \text{BehaviorSim}(s_j, s^*)$$

where:
- The first term measures test pass rate
- $\text{cov}_j$ captures how much of the intended functionality was attempted
- $\text{ErrorProximity}(s_j)$ measures how "close" the errors are to the correct solution (computed via edit distance of error-causing lines to reference solutions or via embedding similarity)
- $\text{BehaviorSim}(s_j, s^*)$ measures similarity in runtime behavior to any successful solution $s^*$

The hyperparameters $\alpha, \beta, \gamma, \delta$ are tuned to balance these components, with default values $\alpha = 0.4, \beta = 0.2, \gamma = 0.2, \delta = 0.2$.

**Preference Pair Construction**: For each task $t$, we construct preference pairs $(s^+, s^-)$ where $EQS(s^+) > EQS(s^-)$. The preference margin is defined as:

$$m(s^+, s^-) = EQS(s^+) - EQS(s^-)$$

**Weighted Direct Preference Optimization**: We adapt DPO to incorporate preference margins:

$$\mathcal{L}_{\text{ExePlay}}(\theta) = -\mathbb{E}_{(s^+, s^-, m)} \left[ w(m) \cdot \log \sigma \left( \beta \left( \log \frac{\pi_\theta(s^+ | d_t)}{\pi_{\text{ref}}(s^+ | d_t)} - \log \frac{\pi_\theta(s^- | d_t)}{\pi_{\text{ref}}(s^- | d_t)} \right) \right) \right]$$

where $w(m) = 1 + \lambda \cdot m$ is a margin-based weight function that emphasizes pairs with larger quality differences, and $\lambda$ is a scaling hyperparameter.

### 2.5 Iterative Self-Play Loop

The complete ExePlay algorithm operates iteratively:

```
Algorithm: ExePlay
Input: Base model M_θ, Task set T, Number of iterations N, Samples per task K
Output: Aligned model M_θ*

for iteration i = 1 to N do:
    D_pref ← ∅  // Preference dataset
    
    for each task t ∈ T do:
        // Phase 1: Generation
        S_t ← Sample K solutions from M_θ given d_t
        
        for each s_j ∈ S_t do:
            Execute s_j and compute SEF(s_j)
            Compute EQS(s_j)
        end for
        
        // Phase 2: Critique Generation
        for each failed s_j do:
            Generate critique_j
            Optionally generate s_j^repair and add to S_t
        end for
        
        // Phase 3: Preference Pair Construction
        for each pair (s_a, s_b) where EQS(s_a) > EQS(s_b) do:
            Add (s_a, s_b, m(s_a, s_b)) to D_pref
        end for
    end for
    
    // Update model
    M_θ ← Optimize L_ExePlay on D_pref
    
    // Curriculum: Add harder tasks based on current performance
    T ← UpdateTaskCurriculum(T, M_θ)
end for

return M_θ* = M_θ
```

### 2.6 Experimental Design

**Datasets and Benchmarks**: We evaluate on:
- **SWE-Bench Lite and Full**: Real-world GitHub issue resolution
- **HumanEval and MBPP**: Standard code generation benchmarks
- **CodeContests**: Competitive programming problems
- **LiveCodeBench**: Contamination-free evaluation set

**Baselines**:
1. Base model without alignment (e.g., CodeLlama, DeepSeek-Coder)
2. Standard RLHF with human preferences
3. RRHF (Yuan et al., 2023)
4. Sol-Ver self-play (Lin et al., 2025)
5. Binary execution feedback RL (pass/fail only)

**Evaluation Metrics**:
- **Pass@k**: Percentage of problems solved within k attempts
- **Resolve Rate**: For SWE-Bench, percentage of issues successfully resolved
- **Test Coverage Improvement**: Average coverage gain over iterations
- **Self-Repair Success Rate**: Percentage of failed solutions successfully repaired via critique

**Implementation Details**: We use DeepSeek-Coder-33B as the base model, implement execution sandboxing using Docker containers, and train using the OpenRLHF framework (2024) with 8×A100 GPUs. Each iteration processes 10,000 tasks with K=8 samples per task.

**Ablation Studies**:
1. Impact of each EQS component
2. Effect of critique generation (with/without)
3. Sensitivity to preference margin weighting
4. Comparison of sampling strategies (temperature, nucleus sampling)

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following results:

1. **Performance Improvements**: We expect ExePlay to achieve 15-25% relative improvement on SWE-Bench resolve rate compared to the base model, and 10-15% improvement over binary execution feedback baselines, demonstrating the value of structured feedback.

2. **Scalable Training Dynamics**: The iterative self-play loop should show consistent improvement across iterations without the instability often observed in sparse-reward RL, as measured by monotonically increasing Pass@1 on held-out evaluation sets.

3. **Effective Self-Repair**: The critique-guided repair mechanism should successfully fix 30-40% of initially failed solutions, providing additional high-quality training signal.

4. **Interpretable Feedback**: Generated critiques should align with ground-truth bug explanations (measured via semantic similarity), demonstrating the model's genuine understanding of execution failures.

### Broader Impact

**Advancing Scalable Alignment**: ExePlay demonstrates a path toward continuously improving code agents without human annotation bottlenecks, contributing to the post-training and alignment research agenda for code.

**Open Science Contribution**: We commit to releasing the complete codebase, trained model checkpoints, and preference datasets, enabling reproducibility and community extensions. The framework's modular design allows researchers to experiment with different execution environments, feedback structures, and alignment algorithms.

**Developer Productivity**: More capable code agents directly translate to improved developer productivity, particularly for complex debugging and issue resolution tasks that currently require significant human effort.

**Responsible AI Considerations**: By grounding training in objective execution feedback rather than potentially biased human preferences, ExePlay may reduce certain alignment risks. However, we acknowledge that execution success does not guarantee safety or adherence to coding standards, and recommend combining ExePlay with complementary safety mechanisms.

### Limitations and Future Directions

The current approach requires executable test suites, limiting applicability to tasks with well-defined specifications. Future work will explore generating synthetic tests and extending to documentation, style, and security alignment. Additionally, scaling to larger models and longer-horizon tasks (e.g., multi-file repository modifications) presents computational and methodological challenges we aim to address in subsequent research.

In conclusion, ExePlay offers a principled, scalable approach to code agent alignment that leverages the unique properties of code—its executability and objective correctness criteria—to enable continuous self-improvement without human feedback dependency.