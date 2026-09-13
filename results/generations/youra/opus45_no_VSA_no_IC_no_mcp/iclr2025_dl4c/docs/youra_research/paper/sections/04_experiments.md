# Experimental Setup

We design experiments to test each step of the hypothesized causal chain, from counterfactual information extraction through targeted editing to fix success.

## Research Questions

Our experiments address four questions, each mapping to a specific claim:

**RQ1 (H-M1):** Do execution traces contain extractable counterfactual information?  
*Tests:* Whether error traces provide the localization information our theory predicts.

**RQ2 (H-M2):** Does detailed feedback enable targeted edits compared to binary feedback?  
*Tests:* Whether information granularity affects model editing behavior.

**RQ3 (H-M3):** Do targeted edits achieve higher fix rates than global rewrites?  
*Tests:* Whether the predicted mechanism (targeting → success) holds empirically.

**RQ4 (H-C1):** Does execution advantage increase with task complexity?  
*Tests:* Whether complex tasks benefit more from precise localization.

## Datasets

We evaluate on two standard code generation benchmarks with complementary characteristics:

| Dataset | Problems | Language | Complexity | Why Chosen |
|---------|----------|----------|------------|------------|
| HumanEval | 164 | Python | Lower | Standard function-level benchmark; enables comparison with prior work |
| MBPP | 500 | Python | Higher | More complex problems; tests complexity interaction hypothesis |

**HumanEval** [Chen et al., 2021] provides function-level code completion tasks with doctests. We use the standard 164-problem split. Test cases are deterministic, enabling clean execution feedback collection.

**MBPP** [Austin et al., 2021] contains more complex programming problems with multi-step reasoning. We use this to test whether execution advantage increases with task complexity (RQ4).

## Feedback Conditions

We compare four feedback conditions:

| Condition | Information Content | Purpose |
|-----------|---------------------|---------|
| **Execution-Detailed** | Line number, error type, expected/actual values | Full localization |
| **Execution-Binary** | Pass/fail only | Ablates localization |
| **AI-Critic** | LLM-generated critique | Tests AI approximation |
| **Random** | Shuffled feedback | Controls for feedback presence |

The random condition provides a critical control: if AI-critic performs at random level, the critic provides no useful signal. If AI-critic exceeds random but underperforms execution, we can quantify the localization gap.

## Model and Training

**Base Model:** CodeLlama-7B-Instruct (Meta, 2023)  
We select this model for three reasons: (1) open-source, enabling reproducibility; (2) instruction-tuned for code editing; (3) representative of widely-deployed 7B code LLMs.

**Refinement Protocol:**
- Iterations: k=3
- Temperature: 0.2 (low variance for reproducibility)
- Max tokens: 512 per generation
- Timeout: 10s per execution

**AI-Critic:** CodeLlama-7B-Instruct as critic (same model, different prompt). This controls for model capability—any execution advantage cannot be attributed to using a stronger critic.

## Evaluation Metrics

**Primary:**
- **pass@1:** Proportion of problems solved after k=3 refinement iterations. Computed per condition.

**Mechanism Metrics:**
- **CF-score:** Counterfactual information score (0-1) per trace. Measures line number, error type, expected/actual value presence.
- **Edit scope:** Classified as Targeted (≤5 lines), Local (6-15 lines), or Global (>15 lines).
- **Fix rate by scope:** Success rate conditioned on edit scope.

**Statistical Testing:**
- Paired t-test for within-condition comparisons
- Bonferroni correction for multiple comparisons
- Effect size reported as Cohen's d

## Implementation Details

**Execution Sandbox:**
- Docker containers with Python 3.10
- pytest with captured stdout/stderr
- 10-second timeout per execution
- 512MB memory limit

**Trace Parsing:**
- Regex extraction of line numbers, error types
- Template-based conversion to natural language
- CF-score computed as weighted sum of present elements

**Edit Analysis:**
- Line-level diff (difflib)
- AST-based change localization
- Automatic scope classification

**Compute:**
- Hardware: 1× NVIDIA A100 (40GB)
- Inference time: ~0.5s per generation
- Total experiment runtime: ~48 hours

All experiments use fixed random seeds for reproducibility. Code and data will be released upon publication.
