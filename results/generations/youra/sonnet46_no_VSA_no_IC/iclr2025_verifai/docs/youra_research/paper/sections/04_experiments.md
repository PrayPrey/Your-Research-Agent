# 4. Experimental Setup

We design experiments to answer the following research questions:

**RQ1:** Is the 134-problem GPT-4o-mini EvalPlus failure set fully recoverable from
the h-e1 Run 2 archive, enabling reproducible repair experiments without new baseline
API calls?

**RQ2 (Pre-registered):** Does specification-aligned repair (Condition C) achieve
statistically significantly higher round-1 pass@1 than blind reprompting (Condition B)
on the 128-task working set, as measured by one-tailed McNemar's test (α=0.05)?

**RQ3 (Pre-registered, Exploratory):** Is specification-aligned repair differentially
effective by problem type — specifically, does the HumanEval+ fix rate exceed the
MBPP+ fix rate under Condition C?

RQ1 is the focus of this paper. RQ2 and RQ3 are pre-registered predictions for the
mechanism experiment phase (h-m1, h-m2, h-c1), reported here for transparency.

## 4.1 Dataset

**EvalPlus failure subset (h-e1 Run 2 archive).** The experimental dataset consists
of 134 GPT-4o-mini code generation failures from the h-e1 Run 2 evaluation:

| Benchmark | Failures | % of total |
|-----------|----------|------------|
| HumanEval+ | 34 | 25.4% |
| MBPP+ | 100 | 74.6% |
| **Total** | **134** | **100%** |

These failures represent GPT-4o-mini's natural round-0 failure distribution on EvalPlus
(79.3% pass rate on HumanEval+, 73.5% on MBPP+). All 134 failures are semantic/
algorithmic errors: static analysis (ruff+mypy) fires on at most 32.4% of HumanEval+
failures and 16.0% of MBPP+ failures, confirming that syntactic repair oracles are
insufficient for this population.

**Why EvalPlus.** EvalPlus augments HumanEval and MBPP with 80× more test cases,
making it a substantially stricter evaluation than base benchmarks. Problems that
pass round-0 on EvalPlus represent genuine algorithmic capability; failures are
semantic divergences that require targeted repair signal, not syntactic correction.

**Working set.** Six tasks (HumanEval/143, Mbpp/725, Mbpp/726, Mbpp/765, Mbpp/805,
Mbpp/809) have empty `plus_fail_tests` fields in the archive, preventing Condition C
prompt construction from stored data. These tasks require either fresh EvalPlus
evaluation runs or exclusion. We use the 128-task working set (95.5% recovery rate)
for mechanism experiments. This exclusion is principled and pre-registered.

## 4.2 Baselines

| Condition | Method | Description | Rationale |
|-----------|--------|-------------|-----------|
| A (Baseline) | h-e1 Run 2 results | Round-0 GPT-4o-mini, no repair | Establishes failure population |
| B (Blind reprompt) | Self-Refine [Madaan et al., 2023] | Original prompt + "Please try again" | Placebo control — isolates re-exposure |
| C (Spec-aligned) | This work | Specification triple | Tests semantic gap description oracle |

**Condition A** is the h-e1 Run 2 ground truth — all 128 working-set problems failed
round-0 by definition. No new API calls are required.

**Condition B** isolates the value of mere re-exposure (re-sampling at temperature
> 0) from the value of specification context. Without this control, any improvement
under Condition C could be attributed to stochastic re-sampling rather than the
structured information in the triple.

## 4.3 Evaluation Metrics

**Primary metric: round-1 pass@1** — binary fix indicator per problem. A problem is
fixed if the repaired code passes *all* EvalPlus augmented test cases (not just the
prompted failing test). This strict criterion prevents solutions that address only the
shown counterexample while failing other tests.

**Secondary metrics:**
- *Fix rate*: proportion of 128 working-set problems fixed under each condition (C
  threshold: ≥ 15%, aligned with FeedbackEval baseline of 21.1pp average fix rate)
- *Token efficiency ratio*: fix rate per 1000 additional input tokens vs. Condition A
  (quantifies the cost-benefit of the triple vs. blind re-exposure)

**Statistical significance:** One-tailed McNemar's test at α=0.05. Yates' continuity
correction if any cell count < 5. Fallback to Fisher's exact test if discordant pairs
< 25.

## 4.4 Implementation Details

**Model.** GPT-4o-mini (OpenAI API). Same model used in h-e1 Run 2, enabling direct
comparison with round-0 baseline.

**Hyperparameters (pre-registered):**
- Temperature: 0.2 (non-zero to avoid greedy fixed-point suppression of Condition B)
- Seed: 42 (reproducibility)
- Repair rounds: 1 (single-turn only)

**Test selection.** `plus_input[0]` — first test case in EvalPlus's deterministic
ordering. Pre-registered; no cherry-picking of failing tests.

**Evaluation oracle.** EvalPlus augmented test suite (all tests must pass for fix = 1).
Same oracle used in round-0 evaluation.

**Infrastructure.** Verification script: `verify_h_e1_v2.py` (~80 lines, CPU-only,
~2s runtime). Mechanism experiments: `scipy.stats.mcnemar()` for statistical testing.
EvalPlus version: 0.3.1.

**Estimated cost.** Condition B: 128 API calls (~$0.025). Condition C: 128 API calls
(~$0.025). Total mechanism experiment cost: ~$0.05. Condition A reuses existing data
at zero cost.

**Hardware.** Existence verification run on 5× NVIDIA H100 NVL server (CPU-only;
GPUs not used). Mechanism experiments require only API access and EvalPlus evaluation.
