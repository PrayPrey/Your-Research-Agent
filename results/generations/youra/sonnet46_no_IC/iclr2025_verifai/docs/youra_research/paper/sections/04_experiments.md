# Experimental Setup

## Research Questions

Our experimental design addresses three research questions:

**RQ1:** Does execution test feedback achieve significantly larger pass@1 improvement than pylint/mypy static analysis at fixed token budget B=1000 on HumanEval and MBPP? *(Tests P1: the primary feedback type ranking claim)*

**RQ2:** What fraction of HumanEval baseline failures does pylint/mypy detect, and which flag categories dominate? *(Tests P2: the mechanistic coverage analysis)*

**RQ3:** Does the execution advantage vary by benchmark, and does pylint repair harm some benchmarks while helping others? *(Tests the task-complexity moderation hypothesis)*

## Datasets

We evaluate on two standard Python code generation benchmarks:

**HumanEval** [Chen et al., 2021]: 164 hand-crafted programming problems designed to test algorithmic reasoning. Problems involve data structure manipulation, string processing, mathematical computation, and algorithm implementation. Baseline pass@1 for Llama 3.1 8B Instruct: 61.0% (64/164 failures). We choose HumanEval because it tests *algorithmic* problems — the failure mode we hypothesize is poorly addressed by style-focused static analysis.

**MBPP** [Austin et al., 2021]: 378 Python programming problems (EvalPlus format, assertion field) covering function-completion tasks with clear specifications. Baseline pass@1: 33.1% (253/378 failures). MBPP problems are generally simpler than HumanEval, enabling us to test whether task complexity moderates the feedback advantage (RQ3).

| Dataset | # Problems | Failure Rate | Problem Type |
|---------|-----------|-------------|--------------|
| HumanEval | 164 | 39% (64/164) | Algorithmic reasoning |
| MBPP | 378 | 67% (253/378) | Function completion |

## Conditions

| Condition | Description | Token Budget |
|-----------|-------------|-------------|
| No-feedback | Single greedy pass, no repair | B=1000 (initial gen only) |
| Pylint/mypy repair | Iterative repair with pylint + mypy output | B=1000 total |
| Execution feedback repair | Iterative repair with test execution output | B=1000 total |

All conditions use Llama 3.1 8B Instruct with greedy decoding (temperature=0, seed=42).

## Implementation Details

**Pylint/mypy integration.** We run `pylint --output-format=text` with default rule configuration and `mypy` in strict mode. Output is parsed and formatted as structured feedback within the prompt. Coverage analysis (RQ2) runs pylint/mypy on all 64 HumanEval failures and records flags by category.

**Execution infrastructure.** Test execution uses a sandboxed subprocess with a 15-second timeout per execution call. For HumanEval, we use the official EvalPlus test suite. For MBPP, we use the assertion-based test suite from the EvalPlus MBPP format.

**Token budget enforcement.** A repair manager tracks cumulative output tokens per problem. A new repair round is initiated only if remaining budget exceeds 50 tokens. Rounds are capped at max\_tokens=512 per generation call.

**Resume capability.** Results are written incrementally to JSONL files with task-id deduplication, allowing resume from checkpoint on interruption. All 542 problems (164 + 378) completed successfully.

## Evaluation Metrics

**Primary:** Pass@1 improvement delta Δ = pass@1(condition) − pass@1(no-feedback baseline), measured across all problems. A positive Δ indicates the condition improves over not repairing; a negative Δ indicates regression.

**Statistical test:** McNemar's test on the paired 2×2 contingency table (condition-passes × condition-fails) for each benchmark. Significance threshold α=0.05.

**Mechanism metric:** Pylint coverage fraction (total and E+W only) over HumanEval baseline failures. Bootstrap 95% CI with 10,000 samples, seed=42.

**Secondary:** Per-round pass@1 trajectory (rounds 0–3) to characterize budget saturation.
