# Experimental Setup

We evaluate the FGO mechanism through a 4-hypothesis verification chain on standard code generation benchmarks. Our experimental design prioritizes mechanism validation over aggregate performance comparison.

## Datasets

We use two standard code generation benchmarks:

**HumanEval** \cite{chen2021humaneval}: 164 hand-crafted Python programming problems with function signatures, docstrings, and unit tests. Problems range from simple string manipulation to algorithmic challenges. We use all 164 problems for evaluation.

**MBPP** \cite{austin2021mbpp}: 500 crowd-sourced Python programming problems designed to assess basic programming ability. Each problem includes a natural language description and three test cases. We use the sanitized subset of 500 problems.

**Rationale**: These benchmarks provide function-level tasks with executable test cases, enabling trace collection during evaluation. They represent the standard evaluation setup for code generation RL \cite{shojaee2023ppocoder,dou2024stepcoder}.

## Model

We use **CodeLlama-7B-Instruct** \cite{roziere2023codellama} as our base model. This model:
- Is widely used in code generation research, enabling comparison with prior work
- Provides instruction-following capabilities for prompt-based generation
- Represents a practical scale for RL fine-tuning (7B parameters)

For mechanism validation, we use CodeLlama-7B as a reference model for trace collection and gradient verification. Full PPO training is deferred to Phase 5 baseline comparison.

## Experimental Conditions

We evaluate three masking conditions to isolate the effect of execution-informed masking:

| Condition | Description |
|-----------|-------------|
| **none** | No masking; standard PPO with uniform gradient |
| **random** | Random masking at matched sparsity (~80%) |
| **trace** | Trace-based FGO masking |

The **random** condition controls for sparsity effects. If FGO improvement stems merely from gradient sparsity rather than execution information, random masking should perform similarly. If trace-based masking outperforms random masking, the execution information is providing value beyond sparsity.

## Evaluation Protocol

**pass@1**: Fraction of problems solved with greedy decoding (temperature=0). This measures the model's best single-attempt performance.

**pass@10**: Fraction of problems solved within 10 samples (temperature=0.8). This measures solution diversity and robustness.

For mechanism validation, we primarily report pass@1 as it provides a cleaner signal of policy quality.

## Gate Criteria

Each hypothesis has explicit pass/fail criteria:

### H-E1: Existence Gate (MUST_WORK)

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Trace coverage | >= 50% | Must capture meaningful execution |
| Signal concentration | > 1.0 | Must concentrate gradients |
| Mask ratio | > 10% | Must mask non-trivial portion |

**Pass condition**: All three criteria satisfied.

### H-M1: Trace Collection Gate (MUST_WORK)

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Trace capture rate | >= 95% | Infrastructure reliability |
| Token classification F1 | >= 70% | Mapping accuracy |
| Overhead | <= 20x | Practical for training |

**Pass condition**: Capture rate >= 95% AND Token F1 >= 70%.

### H-M2: Gradient Exclusion Gate (MUST_WORK)

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Non-executed gradient norm | = 0.0 | Exact exclusion required |
| All verification checks | Pass | Consistent across seeds |

**Pass condition**: All gradient verification checks pass (6/6).

### H-M3: Efficiency Gate (SHOULD_WORK)

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| FGO pass@1 | > Standard pass@1 | Must show improvement |
| Improvement | > 0% | Any positive effect |

**Pass condition**: FGO achieves higher final pass@1 than Standard PPO.

Note: H-M3 is a SHOULD_WORK gate—failure indicates a limitation to document rather than mechanism invalidity.

## Verification Seeds

We run verification across 3 random seeds (42, 123, 456) to assess consistency:
- Trace collection reliability
- Gradient verification robustness
- Performance variance

## Implementation

Experiments are implemented using:
- **TRL library** for PPO training infrastructure
- **Hugging Face Transformers** for model loading
- **RestrictedPython** for sandboxed code execution
- **sys.settrace** for execution trace collection

All code will be released upon publication.
