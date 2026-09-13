# Introduction

Combining formal verification strategies for LLM code generation appears straightforward—stack grammar constraints, static analysis, and SMT-guided repair for multiplicative gains. But our experiments reveal a critical prerequisite that prior work has overlooked: detection is model-agnostic, while repair is not. A completion model given static analysis feedback increased security issues by 600%, not decreased them.

This matters for practitioners deploying verification pipelines in production. Teams investing in multi-stage verification infrastructure may see code quality *degrade* if model capability is not matched to each stage's requirements. The stakes are high: verification pipelines promise to catch errors that slip past human review, but a misconfigured pipeline can introduce more vulnerabilities than it prevents.

## The Problem

At the surface level, the problem is well-known: LLM-generated code contains syntax errors, security vulnerabilities, and specification violations. Different verification strategies—grammar-constrained decoding, static analysis, SMT-guided repair—target different error types.

However, a deeper problem emerges when we consider combining these strategies. Each has been studied in isolation: grammar constraints reduce compilation errors by over 50% (Mündler et al., 2025), static analysis feedback reduces security issues from 40% to 13% (Blyth et al., 2025), and SMT-guided pipelines achieve 75-82% pass@1 on contract synthesis (Lim et al., 2025). But no unified comparison exists across all three strategies on identical benchmarks with consistent metrics.

This leaves a critical gap: we do not know whether error classes are truly independent (enabling multiplicative gains) or overlapping (yielding diminishing returns). Without this knowledge, practitioners cannot predict combined pipeline effectiveness.

## Our Insight

We address this gap by measuring error class independence directly. Our key insight is twofold:

**Error classes targeted by grammar constraints, static analysis, and SMT verification are largely independent** (mean Jaccard index 0.0752, well below the 0.30 threshold). This validates the theoretical foundation for layered verification pipelines.

**However, translating detection into repair requires instruction-tuned models.** When we tested static analysis feedback loops with a completion model (StarCoder2-3b), security issues increased from 1 to 7 across 8 prompts. The model treated feedback as context to complete, not instructions to repair.

This distinction—detection is model-agnostic, repair is model-capability-dependent—explains why prior work reported success while our initial experiments failed, and identifies a critical prerequisite for practitioners.

## Contributions

Building on this insight, we make the following contributions:

1. **Error-class-independence framework.** We provide the first quantitative measurement of independence between grammar, semantic, and specification error classes, using Jaccard indices on improvement sets across 164 HumanEval problems.

2. **Model capability prerequisite identification.** We identify that feedback-based verification stages require instruction-tuned models; pure completion models may degrade output quality.

3. **Partial pipeline validation.** We demonstrate that grammar-constrained decoding reduces syntax errors by 40%, validating the first stage of the layered verification pipeline.

The remainder of this paper is organized as follows. Section 2 reviews related work on verification strategies for code generation. Section 3 describes our methodology for measuring error class independence. Section 4 presents experimental setup, Section 5 reports results, and Section 6 discusses implications and limitations. Section 7 concludes with future directions.
