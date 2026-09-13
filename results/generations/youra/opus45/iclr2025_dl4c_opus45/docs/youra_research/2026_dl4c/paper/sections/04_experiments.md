# Experimental Setup

We design experiments to answer four research questions, each corresponding to a hypothesis in our verification framework:

**RQ1 (H-E1):** Do error type distributions differ significantly between RL-aligned and DPO-aligned code generation models?

**RQ2 (H-M1):** Does RL's binary execution reward concentrate failures in assertion errors as predicted by the zero-reward basin theory?

**RQ3 (H-M2):** Do RL failures execute deeper into the code before failing, reflecting syntactic validity pressure?

**RQ4 (H-M3):** Does the alignment signature persist—or amplify—at fine-grained error taxonomy levels?

## Models

We select models representing the two alignment paradigms under study:

### RL-Aligned: CodeRL

- **Model:** Salesforce/codet5-large-ntp-py (770M parameters)
- **Architecture:** CodeT5-large encoder-decoder [Wang et al., 2021]
- **Alignment Method:** Reinforcement learning with binary execution reward (pass=1, fail=0)
- **Training Data:** APPS benchmark with unit test feedback
- **Key Property:** All non-executing programs receive identical zero reward

### DPO-Aligned: CodeLlama-Instruct

- **Model:** codellama/CodeLlama-7b-Instruct-hf (7B parameters)
- **Architecture:** Llama 2 decoder-only [Touvron et al., 2023]
- **Alignment Method:** Instruction tuning with preference data (no execution feedback during alignment)
- **Training Data:** General instruction-following preferences
- **Key Property:** Optimizes human preference signal without explicit execution validation

**Model Selection Rationale:** We intentionally compare models with different architectures (encoder-decoder vs. decoder-only) and scales (770M vs. 7B). This is a conservative test: if alignment-induced error divergence exists despite these confounds, it represents a robust phenomenon. Future work will address controlled training from identical base models.

## Datasets

We evaluate on the EvalPlus benchmark [Liu et al., 2023], which provides augmented test coverage for detecting subtle semantic errors:

| Dataset | Problems | Test Augmentation | Purpose |
|---------|----------|-------------------|---------|
| HumanEval+ | 164 | 80x original coverage | Diverse function synthesis |
| MBPP+ | 378 | 35x original coverage | Simple function synthesis |
| **Total** | **542** | - | Combined evaluation |

The augmented test coverage is critical: original HumanEval/MBPP tests often have insufficient coverage to detect semantic errors. HumanEval+ and MBPP+ increase the likelihood of assertion failures (code that passes some tests but fails others), which is central to our hypothesis about RL error concentration.

## Generation Protocol

For each model and problem:
- **Samples:** n = 1 per problem (total: 1,084 samples)
- **Temperature:** T = 0.8 (balancing diversity and quality)
- **Top-p:** 0.95 (nucleus sampling)
- **Max tokens:** 512
- **Seed:** 42 (reproducibility)

## Error Classification

We employ a two-tier classification scheme based on execution semantics:

### Coarse Classification (3 categories)

| Category | Definition | Detection |
|----------|------------|-----------|
| Syntax Error | Code fails to parse | SyntaxError, IndentationError |
| Runtime Error | Code parses but fails during execution | NameError, TypeError, ZeroDivisionError, etc. |
| Assertion Error | Code executes completely, wrong output | AssertionError from test assertions |

Classification is automated via Python exception type mapping—no manual annotation required.

### Fine-Grained Classification (19 causes)

We apply the LlmFix taxonomy [Zhang et al., 2024] for detailed analysis:
- **Syntax tier (9 causes):** indentation_error, syntax_error, incomplete_code, missing_colon, unmatched_brackets, invalid_escape, encoding_error, tabs_spaces, other_syntax
- **Runtime tier (7 causes):** name_error, type_error, attribute_error, index_error, value_error, recursion_error, other_runtime
- **Assertion tier (3 causes):** wrong_output, off_by_one, incorrect_algorithm

## Execution Depth Measurement (H-M2)

For the execution depth analysis, we instrument code execution using Python's `sys.settrace()`:

1. Construct full executable code: prompt + model completion
2. Execute with tracing enabled to count unique lines reached
3. Compute: `execution_depth = executed_lines / total_executable_lines`

This measures how far into the code execution proceeds before failure—a direct proxy for syntactic validity pressure.

## Evaluation Metrics

| Hypothesis | Test | Primary Metric | Success Criterion |
|------------|------|----------------|-------------------|
| H-E1 | Chi-square | p-value, Cramér's V | p < 0.05, V > 0.05 |
| H-M1 | Fisher's exact | p-value (one-sided) | p < 0.05, RL > DPO |
| H-M2 | Welch's t-test | p-value, Cohen's d | p < 0.05, d > 0.2 |
| H-M3 | Chi-square | Cramér's V (fine) | V > 0.03 at 19-cause level |

## Baseline Comparison

Since no prior work has examined alignment-induced error distributions, we compare against the null hypothesis: error type distribution is independent of alignment method (no systematic difference). Our chi-square test directly tests this null hypothesis.

## Computational Resources

- **Hardware:** NVIDIA H100 NVL (95GB VRAM)
- **Generation Time:** ~53 minutes (1,084 samples total)
- **Framework:** PyTorch 2.7.1, Transformers 4.45.0
- **Analysis:** scipy 1.11.0 for statistical tests
