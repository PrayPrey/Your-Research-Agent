# Introduction

We set out to filter Python training data for code large language models (LLMs) using
doctest execution — a seemingly natural signal of functional correctness. Before training
a single model, we discovered that only 1 in 1,000 Python files in a curated corpus
contains an independently-executable doctest. The `>>>` patterns that Python conventions
encourage appear in 3.1% of files, but 31× fewer survive subprocess execution in a clean
environment. This gap is not a measurement artifact: it is a structural property of
Python library code, which depends on third-party packages unavailable in clean execution environments.

## Motivation

Code LLMs are supervised fine-tuned (SFT) on corpora of Python code drawn from platforms
such as GitHub, producing models evaluated on benchmarks like HumanEval [Chen et al., 2021]
and MBPP [Austin et al., 2021]. These corpora are large but noisy: raw code repositories
contain syntactically invalid files, functionally broken examples, and copy-paste debris.
Training on such data exposes models to malformed patterns, potentially limiting benchmark
performance relative to training on a cleaner, execution-validated subset.

The field has responded to this challenge with heuristic filtering — removing files based
on line length, alphanumeric fraction, and encoding (as in The Stack [Kocetkov et al., 2022]
and StarCoder [Li et al., 2023]). A more principled alternative is *execution-based filtering*:
retain only files that pass a syntax validity gate (`compile()`) or a functional correctness
gate (doctest execution). The appeal of execution-based filtering is that it applies a
ground-truth check — code that does not compile is certainly wrong, and code whose doctests
fail is likely inconsistent with intended behavior.

However, execution-based filtering rests on an untested assumption: that the corpus contains
sufficient executable examples to meet SFT token budget requirements. For the doctest-passing
condition — the strictest functional gate — this assumption is precisely what we examine.

## The Deeper Problem: Pattern ≠ Executability

Python's doctest convention was designed for installed environments. A docstring beginning
with `>>> import numpy as np` is documentation intent, not a self-contained executable
example: it requires `numpy` to be installed in the execution environment. Clean subprocess
execution — without pre-installed third-party packages — will reject the vast majority of
such examples at the import stage.

Prior work did not measure this gap. The Stack paper estimated compile() validity rates
on 10,000 sampled Python files [Kocetkov et al., 2022] but did not characterize doctest
executability. phi-1 [Gunasekar et al., 2023] demonstrated that quality-filtered SFT
data outperforms equal-token-budget unfiltered data, but used GPT-4 curation rather than
execution gates. EffiCoder [Zeng et al., 2024] applied execution-selected SFT samples
for instruction tuning and achieved +13pp HumanEval improvement on Qwen2.5-Coder-7B,
but operated on instruction-response pairs rather than raw corpus code. No prior work
performed a controlled comparison of unfiltered vs. compile-only vs. doctest-passing SFT
filtering on a raw Python corpus at equal token budget.

## Key Insight

Execution filtering for code LLM data quality has two fundamentally different regimes:
(1) *compile-only* (syntax gate), which retains ~60-80% of files and scales to any corpus
size; and (2) *doctest-passing* (functional gate), which collapses to ~0.1% of files in
library-heavy Python corpora — a rate insufficient for SFT at 500M-token budgets.
These are not points on a quality spectrum; they are categorically different strategies
with different corpus-scale feasibility profiles.

This insight motivates the present work: before designing an SFT comparison, we must
measure whether the doctest-passing condition is feasible as a corpus quality gate.

## Contributions

Building on this insight, we make the following contributions:

1. **First empirical characterization of Python doctest executability at corpus scale.**
We conduct a systematic three-phase pilot scan of 10,000 randomly sampled Python files,
measuring the prevalence of `>>>` patterns (Phase A: 3.1%), AST-parseable doctest examples
(Phase B: 2.0%), and independently-executable doctests (Phase C: 0.1%). The 31× gap
from Phase A to Phase C is the primary finding, with import errors as the dominant
failure mode.

2. **Validated multi-phase doctest filtering pipeline.**
We implement and release the Phase A/B/C pipeline — pattern check, AST extraction,
and base64-isolated subprocess execution — which processes 10,000 files in 129.8 seconds
with 4-worker parallelism and passes 28/28 unit tests. The pipeline is production-ready
and reusable for future corpus characterization studies.

3. **Practical recommendation for SFT corpus construction.**
We establish that compile-only filtering is the practical execution-quality gate for
raw Python SFT corpus construction at scale, and that doctest-passing filtering requires
dependency-aware execution infrastructure (pre-installed scientific packages in subprocess
context) to be viable. The equal-token-budget SFT comparison experiment (compile-only vs.
unfiltered, Qwen2.5-Coder-1.5B on HumanEval/MBPP) is designed and pending execution.

We organize the paper as follows: Section 2 reviews related work on code data quality
filtering. Section 3 describes the three-phase filtering methodology. Section 4 presents
the experimental design for both the feasibility scan (H-C1) and the planned SFT comparison
(H-E1). Section 5 reports results. Section 6 discusses findings and limitations. Section 7 concludes.
