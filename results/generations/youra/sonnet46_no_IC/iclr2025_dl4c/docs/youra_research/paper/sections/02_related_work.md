# Related Work

Understanding why prior work did not measure the doctest feasibility gap requires examining
how code LLM data curation evolved — from heuristic rules to quality-filtered corpora. We
organize this review around the key comparison points that motivate our approach.

## Code LLM Benchmarks and Evaluation

HumanEval [Chen et al., 2021] established the pass@k metric for code generation evaluation,
using 164 hand-written Python programming problems with unit tests. MBPP [Austin et al., 2021]
provided a complementary benchmark of 974 Python programming tasks ranging from simple to
challenging. Both benchmarks evaluate functional correctness via execution, making them the
canonical measure of SFT data quality effects in our study. We evaluate HumanEval pass@1
and MBPP pass@1 (greedy decoding) for direct comparability with prior work.

## Heuristic-Only Corpus Filtering

StarCoder [Li et al., 2023] and StarCoder 2 [Lozhkov et al., 2024] established the standard
pipeline for open-source code corpus construction from The Stack [Kocetkov et al., 2022]:
near-deduplication, PII redaction, and heuristic quality filtering (line length, alphanumeric
fraction, encoding, XML/HTML ratio). These filters remove obvious junk but do not apply
execution-based quality signals. StarCoder achieves 40% HumanEval pass@1 at 15.5B parameters
— a strong but heuristically-filtered baseline.

Contemporaneously, cristinaimprota et al. [2025] conducted an SFT study on The Stack Python
using function-level pairs (docstring + implementation), finding that data composition
affects HumanEval performance. However, their filtering pipeline is heuristic-only: no
execution gate is applied to verify that the implementations are syntactically or functionally
valid. This is precisely the gap our work addresses.

**Limitation:** Heuristic filtering cannot distinguish syntactically valid from invalid code,
nor functionally correct from incorrect code. Execution-based filtering provides ground-truth
quality signals that heuristic rules approximate.

## Quality Curation via Language Models

phi-1 [Gunasekar et al., 2023] demonstrated that 7B quality tokens curated by GPT-4 yield
50.6% HumanEval pass@1 at 1.3B parameters — a landmark result showing quality > quantity
at equal token budget. phi-1.5 [Li et al., 2023] extended this to reasoning tasks. The
phi line establishes the conceptual foundation for our equal-token-budget comparison design.

However, phi-1's curation is not reproducible or scalable for open-source use: it requires
GPT-4 API access and proprietary educational quality scoring. Our approach uses deterministic,
open-source execution gates (compile() and doctest execution) that scale to 12.96M+ files
without external API costs.

**Limitation:** GPT-4-based quality curation is not a reproducible, open-source pipeline.
Execution-based gates provide reproducible, cost-free quality signals.

## Execution-Based Data Selection

EffiCoder [Zeng et al., 2024] is the closest prior work: it applies execution-based sample
selection to instruction-tuning data (prompt-solution pairs), achieving Qwen2.5-Coder-7B
44.8% → 57.7% HumanEval pass@1 (+13pp). EffiCoder's selection criterion is execution
pass rate on the solution's test cases — a strong functional signal.

However, EffiCoder operates on *instruction-tuning pairs* (prompt + labeled test cases),
not *raw corpus code*. Instruction pairs are curated and labeled; raw corpus code from
The Stack is unlabeled and contains no test cases. The doctest mechanism offers a functional
gate for raw corpus code (each file's doctests serve as its tests), but this requires
measuring whether enough executable doctests exist in the corpus — which EffiCoder does
not address.

OpenCodeInstruct [2025] provides a large-scale instruction-tuning dataset with execution
feedback and quality filtering, achieving significant HumanEval/MBPP improvement across
1B/3B/7B models. Token Cleaning [2025] applies token-level influence filtering to SFT data,
confirming data quality > quantity for SFT. These works operate in the instruction-tuning
regime, not raw corpus SFT.

**Limitation:** Execution-selected SFT samples require labeled test cases or instruction
pairs. Raw corpus execution filtering (our setting) must use intrinsic execution signals
(compile() validity, doctest execution), and the feasibility of these signals at corpus
scale has not been characterized.

## Corpus Scale Characterization

The Stack paper [Kocetkov et al., 2022] applied `py_compile` on 10,000 sampled Python
files to estimate the proportion of syntactically valid code — the direct methodological
precedent for our Phase A/B/C pipeline. StarCoder 2's OpenCoder [Huang et al., 2024]
validated SFT triples using compiler checks but did not ablate against an unfiltered
baseline at equal token budget.

**Our Position:** We extend The Stack's 10,000-file methodology to the full three-phase
doctest filtering funnel (pattern → AST → subprocess execution), providing the first
corpus-scale characterization of the pattern-to-executable gap. Unlike prior corpus studies,
we explicitly measure feasibility before committing to the SFT experiment design — a step
that reveals the doctest condition's structural infeasibility.

## Summary of Gap

| Prior Work | Data Type | Execution Gate | Equal Budget | Feasibility Measured |
|------------|-----------|---------------|--------------|---------------------|
| StarCoder [Li et al., 2023] | Raw corpus | Heuristic only | — | No |
| phi-1 [Gunasekar et al., 2023] | GPT-4 curated | No | Yes | No |
| EffiCoder [Zeng et al., 2024] | Instruction pairs | Execution pass rate | No | No |
| cristinaimprota [2025] | The Stack Python | Heuristic only | Partial | No |
| **This work** | **Raw corpus** | **compile() + doctest** | **Yes (H-E1 planned)** | **Yes (H-C1)** |

No prior work performs: (1) a controlled comparison of unfiltered vs. compile-only vs.
doctest-passing SFT filtering at equal token budget on a raw Python corpus, or (2) a
corpus-scale measurement of doctest executability to verify feasibility before designing
the experiment. We address both gaps.
