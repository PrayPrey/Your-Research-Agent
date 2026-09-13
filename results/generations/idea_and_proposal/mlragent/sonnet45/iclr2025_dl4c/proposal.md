# Self-Evolving Code Agents through Counterfactual Execution Feedback

## 1. Introduction

### Background

The rapid advancement of Large Language Models (LLMs) has catalyzed significant progress in automated code generation, with applications ranging from code completion to solving complex programming tasks. However, despite impressive capabilities demonstrated by models such as GPT-4, Claude, and specialized code models like CodeGen, current code generation agents face fundamental limitations when confronting realistic, multi-step programming challenges such as those encountered in GitHub issue resolution and software development workflows.

A critical gap in existing approaches lies in how agents learn from execution failures. While recent work has begun incorporating execution feedback into code generation pipelines (Lavon et al., 2025), most systems treat execution results as binary signals (pass/fail) without deeply analyzing *why* failures occur or systematically exploring alternative solution paths. This limitation becomes particularly acute in complex scenarios requiring iterative debugging, architectural reasoning, and understanding of subtle semantic requirements—tasks that remain challenging even for state-of-the-art models on benchmarks like SWE-bench.

The concept of counterfactual reasoning—exploring "what if" scenarios by considering alternative decisions and their consequences—has shown promise in improving LLMs' causal reasoning capabilities (Vashishtha et al., 2025). However, this approach has not been systematically applied to the code generation domain, where execution traces provide rich, concrete feedback about program behavior. Similarly, while contrastive learning has proven effective for code representation learning (Zhang et al., 2024) and evaluation (Ghoummaid et al., 2025), it has not been leveraged to create learning signals that explicitly contrast failed code with counterfactual successful variants.

### Research Objectives

This research proposes a novel framework called **Self-Evolving Code Agents through Counterfactual Execution Feedback (SECACE)**, which aims to:

1. **Develop automated counterfactual generation mechanisms** that identify critical decision points in failed code executions and systematically generate minimal modifications that lead to successful outcomes.

2. **Design contrastive alignment methods** that enable code generation agents to learn from (failure, counterfactual success) pairs, explicitly teaching agents what should change to transform failing code into working solutions.

3. **Create interpretable learning signals** that go beyond simple reward functions by providing structured explanations of why certain code modifications lead to success.

4. **Validate the framework** on realistic programming benchmarks, particularly SWE-bench and GitHub issue resolution tasks, demonstrating improved success rates and reduced iteration counts.

### Significance

This research addresses multiple critical challenges identified in the DL4C workshop's call for papers:

- **Agentic Methods for Programming Tasks**: By enabling agents to learn from their execution failures systematically, SECACE enhances their capability to solve realistic GitHub issues through improved self-correction mechanisms.

- **Post-training and Alignment for Code**: The proposed contrastive alignment approach represents a novel method for learning from execution feedback, providing interpretable signals that explicitly guide model improvement.

- **Benchmarking and Evaluation for Code**: The framework contributes execution-based evaluation methodologies that assess not just whether code works, but how agents learn to fix failing code.

The expected impact includes advancing autonomous software development capabilities, reducing the gap between current AI coding assistants and fully autonomous programming agents, and providing insights into how execution feedback can be structured for effective learning.

## 2. Methodology

### Overview

The SECACE framework consists of four main components: (1) Execution Trace Analysis, (2) Counterfactual Code Generation, (3) Contrastive Alignment Training, and (4) Agent Deployment with Self-Evolution. Figure 1 illustrates the overall architecture.

### 2.1 Execution Trace Analysis

When a code generation agent produces code $C_0$ for a given task specification $T$ and the code fails during execution, we capture a detailed execution trace $E = \{s_1, s_2, ..., s_n\}$ where each $s_i$ represents a program state including variable values, control flow, and stack information.

**Critical Decision Point Identification**: We define critical decision points as program locations where alternative implementations could potentially lead to different execution outcomes. Formally, a location $l_i$ in code $C_0$ is a critical decision point if:

$$\text{CDP}(l_i) = \mathbb{I}[\exists C' : \text{diff}(C_0, C', l_i) \land \text{outcome}(C') \neq \text{outcome}(C_0)]$$

where $\text{diff}(C_0, C', l_i)$ indicates that $C'$ differs from $C_0$ primarily at location $l_i$, and $\text{outcome}(C)$ returns the execution result.

To identify these points efficiently without exhaustive search, we employ:

1. **Static Analysis**: Use program slicing to identify code segments that influence failure points (e.g., assertions, exceptions, error returns).

2. **Dynamic Analysis**: Analyze execution traces to find:
   - Branching points where conditions evaluate in ways that lead toward failure
   - Variable assignments whose values propagate to failure locations
   - Function calls that return unexpected values

3. **LLM-Guided Localization**: Prompt a frozen base model to identify suspicious code locations given the task specification, generated code, and error messages:

$$l_{\text{candidates}} = \text{LLM}_{\text{base}}(\text{"Identify suspicious code locations"}, T, C_0, \text{error})$$

### 2.2 Counterfactual Code Generation

For each identified critical decision point $l_i$, we generate counterfactual code variants through a multi-strategy approach:

**Strategy 1: Targeted Mutations**

We define a set of mutation operators $\mathcal{M} = \{m_1, m_2, ..., m_k\}$ that make minimal, semantically-motivated changes:

- **Condition Flip**: Modify conditional expressions (e.g., `<` to `<=`, `and` to `or`)
- **Boundary Adjustment**: Modify loop bounds and array indices
- **API Substitution**: Replace API calls with semantically similar alternatives
- **Type Conversion**: Add or modify type casting operations

For each mutation operator $m_j$ and location $l_i$:

$$C_{i,j}^{\text{mut}} = m_j(C_0, l_i)$$

**Strategy 2: LLM-Guided Modification**

Leverage a code-specialized LLM to generate targeted modifications:

$$C_i^{\text{llm}} = \text{LLM}_{\text{code}}(\text{prompt}(T, C_0, l_i, E, \text{error}))$$

where the prompt instructs the model to make minimal changes at location $l_i$ to potentially fix the error, providing execution context.

**Strategy 3: Hybrid Approach**

Combine mutation-based exploration with LLM refinement:

$$C_i^{\text{hybrid}} = \text{LLM}_{\text{code}}(\text{"Refine this mutation"}, C_{i,j}^{\text{mut}}, T, \text{error})$$

**Counterfactual Validation**: Execute all generated variants and construct a counterfactual dataset:

$$\mathcal{D}_{\text{CF}} = \{(C_0, C_i^{\text{success}}, l_i, T, E) : \text{outcome}(C_i^{\text{success}}) = \text{pass}\}$$

where $C_i^{\text{success}}$ represents counterfactual code that passes the tests.

### 2.3 Contrastive Alignment Training

We design a multi-objective training approach that combines contrastive learning with preference optimization.

**Contrastive Representation Learning**: Following insights from code representation learning (Zhang et al., 2024), we first train a representation encoder $f_\theta$ that maps code to embeddings where counterfactual successes are close to each other and far from failures:

$$\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(f_\theta(C_0), f_\theta(C_i^{\text{success}}))/\tau)}{\sum_{C_j \in \mathcal{B}} \exp(\text{sim}(f_\theta(C_0), f_\theta(C_j))/\tau)}$$

where $\tau$ is a temperature parameter, $\text{sim}$ is cosine similarity, and $\mathcal{B}$ includes both failures and successes.

**Contrastive Preference Optimization**: We adapt Direct Preference Optimization (DPO) for code generation by treating counterfactual successes as preferred outputs:

$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(C_0, C^{\text{success}}, T) \sim \mathcal{D}_{\text{CF}}} \left[\log \sigma \left(\beta \log \frac{\pi_\theta(C^{\text{success}}|T)}{\pi_{\text{ref}}(C^{\text{success}}|T)} - \beta \log \frac{\pi_\theta(C_0|T)}{\pi_{\text{ref}}(C_0|T)}\right)\right]$$

where $\pi_\theta$ is the policy being trained, $\pi_{\text{ref}}$ is a reference model, and $\beta$ controls the divergence from the reference.

**Location-Aware Training**: To emphasize learning at critical decision points, we introduce location-weighted loss:

$$\mathcal{L}_{\text{location}} = -\sum_{t=1}^{|C^{\text{success}}|} w_t \log \pi_\theta(c_t^{\text{success}} | T, c_{<t}^{\text{success}})$$

where $w_t = \alpha$ if token $c_t$ is at or near a critical decision point $l_i$, and $w_t = 1$ otherwise, with $\alpha > 1$.

**Total Training Objective**:

$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{DPO}} + \lambda_2 \mathcal{L}_{\text{location}} + \lambda_3 \mathcal{L}_{\text{contrast}}$$

### 2.4 Agent Deployment with Self-Evolution

During deployment, the trained agent operates in an iterative loop:

1. **Generate Code**: Given task $T$, generate initial code $C_0 = \pi_\theta(\cdot|T)$
2. **Execute and Collect Feedback**: Run $C_0$ and collect execution trace $E$
3. **Self-Correction**: If execution fails:
   - Identify critical decision points using learned representations
   - Generate counterfactual modifications using trained policy
   - Select best modification based on learned preferences
4. **Update Memory**: Store successful (failure → success) transitions for continual learning

**Continual Self-Evolution**: Periodically update the model using newly collected counterfactual pairs:

$$\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}_{\text{total}}(\mathcal{D}_{\text{CF}}^{\text{new}})$$

### 2.5 Data Collection

**Training Data**: 
- **Base Dataset**: Collect 100K programming problems from diverse sources (HumanEval, MBPP, CodeContests, LeetCode)
- **Execution Traces**: Instrument Python and Java execution environments to capture detailed traces
- **Counterfactual Generation**: For each problem, generate initial solutions using base LLMs (CodeGen, StarCoder), execute to identify failures, and apply counterfactual generation pipeline
- **Target**: Create dataset of 500K (failure, counterfactual success, execution trace) tuples

**Evaluation Benchmarks**:
- **SWE-bench**: 2,294 real GitHub issues from Python repositories
- **SWE-bench Lite**: 300 curated instances for faster iteration
- **Custom GitHub Issue Dataset**: Collect 500 new issues from popular repositories with varying difficulty

### 2.6 Experimental Design

**Baseline Comparisons**:
1. **GPT-4 + Simple Retry**: Standard approach with error message feedback
2. **CodeGen + Execution Feedback**: Using binary pass/fail signals
3. **Reflexion**: Self-reflection based debugging approach
4. **LEVER**: Learning from execution verification

**Ablation Studies**:
- Effect of each counterfactual generation strategy
- Impact of contrastive learning component
- Contribution of location-aware training
- Value of continual self-evolution

**Evaluation Metrics**:
1. **Success Rate**: Percentage of problems solved within $k$ attempts ($k \in \{1, 3, 5, 10\}$)
2. **Iteration Efficiency**: Average number of iterations to reach solution
3. **Code Quality**: Measure efficiency (runtime, memory) and style consistency of generated solutions
4. **Counterfactual Quality**: 
   - Minimality: Edit distance between failed and counterfactual code
   - Diversity: Number of distinct counterfactuals generated
   - Success rate: Percentage of counterfactuals that fix the failure

5. **Human Evaluation**: Expert programmers rate solution quality, debugging reasoning, and code maintainability

**Implementation Details**:
- Base Model: CodeLlama-13B or StarCoder-15B
- Training: 8x A100 GPUs, mixed precision training
- Hyperparameters: $\lambda_1=1.0, \lambda_2=0.5, \lambda_3=0.3, \alpha=2.0, \beta=0.1, \tau=0.07$
- Optimization: AdamW with learning rate $5 \times 10^{-6}$, cosine schedule
- Counterfactual Generation: Timeout of 30s per variant execution

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Primary Outcomes**:

1. **Improved Success Rates**: We expect SECACE to achieve 15-25% relative improvement over baseline methods on SWE-bench, with particularly strong gains on complex issues requiring multiple debugging iterations. Based on current state-of-the-art performance (~12-15% on full SWE-bench), we target 17-20% success rate.

2. **Reduced Iteration Counts**: The explicit learning from counterfactual pairs should reduce average iterations to solution by 30-40%, as agents learn to anticipate common failure modes and their fixes.

3. **High-Quality Counterfactual Dataset**: The automated counterfactual generation pipeline will produce a large-scale dataset of ~500K (failure, success) pairs with execution traces, providing a valuable resource for the community.

4. **Interpretable Debugging Traces**: The framework will generate human-interpretable explanations of what changed between failed and successful code, offering insights into the debugging process.

**Secondary Outcomes**:

1. **Generalization Across Languages**: While primarily evaluated on Python, the approach should generalize to other languages (Java, JavaScript) with minimal adaptation.

2. **Transfer to Related Tasks**: The learned representations and counterfactual reasoning capabilities should transfer to related tasks like program repair and code review.

3. **Continual Learning Capabilities**: The self-evolution mechanism should enable agents to improve over deployment time as they encounter new failure patterns.

### Scientific Impact

**Theoretical Contributions**:

1. **Formalization of Counterfactual Learning for Code**: This work provides a rigorous framework for applying counterfactual reasoning to code generation, connecting program analysis, execution semantics, and machine learning.

2. **Novel Alignment Paradigm**: The contrastive preference optimization approach represents a new way to leverage execution feedback for model alignment, moving beyond simple reward signals to structured contrastive examples.

3. **Understanding of Critical Decision Points**: The research will provide insights into what constitutes critical decisions in code generation and how to identify them efficiently.

**Practical Impact**:

1. **Enhanced Autonomous Coding Agents**: The framework directly addresses limitations in current AI coding assistants, bringing us closer to fully autonomous software development capabilities.

2. **Improved Developer Productivity**: By reducing debugging iterations and providing interpretable corrections, SECACE can significantly enhance developer productivity when working with AI coding tools.

3. **Open Science Contribution**: All code, models, and the counterfactual dataset will be released openly, fostering reproducibility and enabling further research. This aligns with the workshop's emphasis on responsible AI and open science practices.

4. **Industry Applications**: The approach can be integrated into existing code generation products (GitHub Copilot, Amazon CodeWhisperer, etc.) to improve their debugging and self-correction capabilities.

### Broader Impact

**Advancing AI Safety in Code Generation**: By making code agents' learning processes more interpretable through counterfactual explanations, this work contributes to safer deployment of autonomous coding systems. The explicit contrast between failing and successful code provides transparency about what the agent learned.

**Educational Applications**: The counterfactual pairs and debugging traces could serve as educational resources for teaching programming, showing common mistakes and their corrections in context.

**Limitations and Risks**: We acknowledge potential limitations including computational costs of execution-based counterfactual generation, possibility of generating insecure code variants during exploration, and challenges in extending to domains beyond well-specified programming tasks. The research plan includes careful analysis of these limitations and development of mitigation strategies.

### Future Directions

This research opens several promising directions:

1. **Multi-Agent Counterfactual Collaboration**: Extending the framework to multiple agents that generate diverse counterfactuals collaboratively.

2. **Counterfactual Synthesis for Testing**: Using the counterfactual generation mechanism to create comprehensive test suites.

3. **Integration with Formal Methods**: Combining counterfactual execution feedback with formal verification to provide correctness guarantees.

4. **Human-in-the-Loop Refinement**: Incorporating human feedback to guide counterfactual generation toward more meaningful scenarios.

In conclusion, Self-Evolving Code Agents through Counterfactual Execution Feedback represents a significant step toward more capable, interpretable, and autonomous programming agents. By systematically learning from execution failures through counterfactual reasoning, this framework addresses critical challenges in current code generation systems and provides a foundation for future advances in AI-assisted software development.