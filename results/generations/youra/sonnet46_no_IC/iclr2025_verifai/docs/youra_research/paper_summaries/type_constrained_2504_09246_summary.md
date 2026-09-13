# Type-Constrained Code Generation with Language Models

## Key Metadata
- **Authors:** Mündler et al.
- **Year:** 2025
- **Venue:** PLDI 2025 (arXiv 2504.09246)
- **Core Contribution:** Introduces type-constrained decoding for LLMs — uses Python type system as a hard constraint during inference to eliminate type errors, reducing compilation errors by >50% on HumanEval/MBPP.

## Section Summaries

### Abstract
Type-constrained code generation integrates Python's type system directly into LLM token generation via constrained decoding. At each decoding step, only tokens that remain type-consistent with the partially generated code are permitted. This reduces compilation/type errors by more than 50% on HumanEval and MBPP benchmarks across multiple model families, with no fine-tuning required.

### Introduction & Motivation
LLMs frequently generate code with type errors that cause compilation or runtime failures. Prior approaches using execution feedback require completed code to be executed before errors are discovered. Type-constrained decoding shifts error prevention to inference time: the type system is used as an oracle that prunes invalid continuations at each step, reducing downstream repair burden.

### Methodology
The approach uses an incremental type checker to maintain type state during generation. At each decoding step: (1) the partial code is type-checked; (2) the vocabulary is filtered to retain only tokens whose addition keeps the program type-consistent; (3) sampling proceeds from the filtered distribution. Implementation: Python/Rust hybrid (Rust for speed); integrated with HuggingFace generation. Key equations: uses type inference rules from PEP 484 / mypy semantics. No training required — decoding-time modification only.

Models tested: multiple families including 7B-30B parameter models. No systematic scale ablation reported (e.g., no 7B vs 70B same-family comparison measuring feedback delta vs. baseline).

### Experiments & Results
| Metric | Result |
|---|---|
| Compilation error reduction | >50% on HumanEval/MBPP |
| pass@1 improvement | Positive (magnitude varies by model) |
| Benchmarks | HumanEval, MBPP |
| Model families | Multiple (7B-30B range) |

No comparison to execution-based iterative repair or pylint/mypy semantic feedback in the same experimental setup. Baselines: unconstrained generation only.

### Discussion & Conclusion
Type-constrained decoding is complementary to, not a replacement for, execution feedback. The authors note that type errors are a subset of all code errors; logic errors and algorithmic errors are not caught by type constraints alone. Future work could combine type-constrained generation with execution-based repair.

## Key Contributions
- First systematic type-constrained decoding for Python code generation
- >50% compilation error reduction on HumanEval/MBPP without fine-tuning
- Multi-model family evaluation
- Open-source implementation (eth-sri/type-constrained-code-generation)

## Potential Relevance
Provides the type-constrained decoding condition for the Gap 3 head-to-head comparison. The eth-sri/type-constrained-code-generation repository (99 stars, Python/Rust) provides a ready implementation that can be run on HumanEval/MBPP alongside execution-feedback repair and pylint/mypy feedback. Critical missing piece: no comparison to other feedback types at iso-compute, which is exactly what Gap 3 targets.
