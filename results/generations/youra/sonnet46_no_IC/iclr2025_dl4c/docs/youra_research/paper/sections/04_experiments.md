# Experimental Setup

We design two experimental components: (1) the H-C1 feasibility scan, which characterizes
doctest executability in a Python corpus, and (2) the H-E1 SFT comparison, which measures
the effect of compile-only filtering on HumanEval and MBPP pass@1 (pending execution).

## Experimental Questions

Our experiments are organized around three questions that directly test our claims:

**EQ1 (Feasibility):** Is doctest-passing filtering feasible as a Python SFT corpus quality
gate at 500M-token scale? We test this via H-C1: a three-phase pilot scan of 10,000 Python
files measuring doctest prevalence and token pool at each filtering phase.

**EQ2 (Root Cause):** What failure mode causes Phase A→C attrition? We analyze Phase C
error types across files that passed Phase B (AST-parseable) but failed subprocess execution,
testing the import isolation hypothesis against stale documentation and other alternatives.

**EQ3 (SFT Quality, Pending):** Does compile-only filtering improve HumanEval/MBPP pass@1
at equal token budget? We design H-E1 for this comparison (pending execution); we report
the design here for transparency and reproducibility.

## H-C1: Doctest Feasibility Scan

### Dataset

We scan `codeparrot/codeparrot-clean-valid` as a proxy for `bigcode/the-stack-dedup`
(access-gated). The corpus is Python-only, HuggingFace-compatible, and uses the same
`content` field schema as The Stack. We apply The Stack quality pre-filters (avg line length
≤ 100, max line length ≤ 1,000, alphanumeric fraction ≥ 0.25) before sampling.

**Sample:** 10,000 randomly sampled Python files (reservoir sampling, `seed=42`), consistent
with The Stack paper's methodology [Kocetkov et al., 2022].

### Metrics

- `doctest_pattern_rate`: Fraction of sampled files with ≥1 `>>>` substring (Phase A)
- `doctest_ast_rate`: Fraction with ≥1 AST-parseable doctest example (Phase B)
- `doctest_executable_rate`: Fraction with ≥1 passing subprocess-executed doctest (Phase C)
- `estimated_token_pool_M`: Extrapolated token pool for executable-doctest files at corpus scale
- `error_type_distribution`: Breakdown of Phase C failure modes

**Success Threshold (from verification plan):**
- PASS: `doctest_executable_rate` ≥ 3.0% (proceed to 3-condition H-E1)
- SCOPE: 1.0–3.0% (reduce token budget)
- PIVOT: < 1.0% (2-condition H-E1 with compile-only only)

### Implementation Details

The three-phase pipeline (`run_scan.py`, `scanner.py`, `data_loader.py`) is implemented
using Python stdlib (`ast`, `doctest`, `subprocess`, `concurrent.futures`) plus HuggingFace
`datasets` for streaming. Phase C uses `ProcessPoolExecutor` with 4 workers and a 5-second
per-file timeout. Source code is base64-encoded before subprocess embedding to eliminate
shell quoting errors.

**Unit test coverage:** 28/28 tests pass, covering all three phases, error classification,
token estimation, and gate evaluation logic.

## H-E1: SFT Quality Comparison (Design)

### Dataset

**Source:** `codeparrot/codeparrot-clean-valid` (or `bigcode/the-stack-dedup` pending access).
**Conditions:**
- **Condition A (Unfiltered):** Random subsample at equal token budget
- **Condition B (Compile-only):** Files passing `compile(source, "<string>", "exec")`

Both conditions use the same quality pre-filters (H-C1 configuration) before applying the
execution gate.

**Token Budget:** 500M tokens per condition (equal budget design). This isolates the quality
effect of compile-only filtering from data quantity effects.

### Model

**Primary:** Qwen2.5-Coder-1.5B [Hui et al., 2024] — a publicly available code LLM at
the 1B scale, comparable to phi-1 (1.3B) [Gunasekar et al., 2023] in terms of scale sensitivity.

**Training Configuration:**
- Optimizer: AdamW, lr=2e-5, batch size=32, 3 epochs, seed=42
- SFT format: next-token prediction on raw code (no instruction template)
- Hardware: single GPU (expected: 40-80GB VRAM)

### Evaluation

**Benchmarks:** HumanEval [Chen et al., 2021] (164 tasks) and MBPP [Austin et al., 2021]
(374 tasks), both evaluated with `lm-evaluation-harness` [Eval Harness, 2021].

**Metric:** pass@1 with greedy decoding (temperature=0). Greedy decoding eliminates
sampling variance, making results reproducible without multiple runs.

**Gate:** MUST_WORK — compile-only filtered ≥ unfiltered by ≥ 2pp HumanEval pass@1.

### Baselines

| Baseline | Rationale |
|----------|-----------|
| Unfiltered subsample (equal token budget) | Primary control; isolates quality effect from quantity |
| Qwen2.5-Coder-1.5B (no SFT) | Establishes base model performance |

The equal-token-budget unfiltered baseline is the correct control for measuring quality
effects: it ensures observed performance differences reflect data quality rather than
regularization from reduced training data volume.

## Fairness and Reproducibility

**Reproducibility:** Fixed seed (42), deterministic reservoir sampling, greedy evaluation.
**Equal budget:** Both SFT conditions receive identical token counts; the compile-only
condition samples more files (slightly higher density) but the same total tokens.
**No cherry-picking:** All evaluation results on HumanEval and MBPP are reported; no
benchmark selection post-hoc.
