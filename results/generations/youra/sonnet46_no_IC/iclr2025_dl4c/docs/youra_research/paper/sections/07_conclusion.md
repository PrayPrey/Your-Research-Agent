# Conclusion

We set out to filter Python SFT training data using doctest execution — a functional
quality gate that tests whether code behaves as documented. We found that only 1 in 1,000
Python files in a curated corpus contains an independently-executable doctest. The `>>>`
prompt in Python code is documentation intent, not executable reality: Python library code
depends on third-party packages that clean subprocess environments do not provide.

This finding is not incidental. The 31× gap between pattern prevalence (3.1%) and executable
rate (0.1%) is architecturally determined — import isolation in clean subprocesses rejects
~95% of AST-parseable doctests at the ModuleNotFoundError stage. The resulting token pool
(0.004M tokens) is 125,000× below the 500M-token SFT budget. Doctest-passing filtering is
structurally infeasible for raw Python corpus SFT without dependency-aware execution
infrastructure.

We contribute the first empirical characterization of this gap at corpus scale, validated
with 28/28 unit tests across a three-phase filtering pipeline (pattern → AST → subprocess)
that processes 10,000 files in 129.8 seconds with 4-worker parallelism. The pipeline is
released as open-source and is directly reusable for corpus characterization studies.

The practical implication is clear: compile() is the appropriate primary execution-quality
gate for raw Python SFT corpus construction. It applies to all syntactically testable Python
files, retains ~60-80% of corpus content, and requires no dependency management infrastructure.
Whether compile-only SFT filtering improves HumanEval pass@1 and MBPP pass@1 over equal-
token-budget unfiltered training remains the primary open question, addressed by the designed
but pending H-E1 experiment.

Measuring feasibility before committing to an experiment design is a small methodological
investment that prevents large experimental waste. We encourage practitioners building code
LLM data pipelines to characterize their execution-gate feasibility at corpus scale before
designing the SFT experiment around it.
