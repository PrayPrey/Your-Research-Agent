# 3. Methodology

## 3.1 Overview

Building on the observation that static analysis fails on 68-84% of EvalPlus semantic
failures, we design a specification-aligned repair oracle that provides the minimum
information necessary for targeted algorithmic repair. The design follows directly from
the insight that three orthogonal components are needed: intent anchoring (docstring),
behavioral gap specification (I/O counterexample), and deviation detection (actual
incorrect output). We call this the *specification triple*.

The methodology has two phases: (1) an existence verification phase that establishes
the data infrastructure for reproducible repair experiments, and (2) a pre-registered
mechanism comparison phase that tests whether the triple outperforms blind reprompting.
This paper reports the existence phase; the mechanism phase is pre-registered and
awaits execution.

## 3.2 The Specification Triple (Condition C)

**Rationale.** The triple design is motivated by three converging mechanisms, each
supported by independent literature:

1. *Docstring re-anchoring* (Step 1): Including the problem docstring's formal intent
   prevents the model from regenerating the same incorrect solution by re-anchoring
   it on the intended algorithm. Haeri & Ghelichi [2026] identify spec grounding as
   the primary driver of +38pp improvement; FeedbackEval [Dai et al., 2025] shows
   severe degradation when docstrings are removed.

2. *I/O counterexample* (Step 2): The failing test's input/expected-output pair
   provides a concrete behavioral gap — a CEGIS-style counterexample [Clarke et al.,
   2003] that specifies exactly where the model's behavior diverges from the
   specification. ContrastRepair [Kong et al., 2024] demonstrates that contrastive
   I/O pairs outperform single failure messages for bug fixing (143/337 vs. 124 bugs).

3. *Deviation detection* (Step 3): The model's actual incorrect output enables it to
   compare its behavior to the expected output and identify the specific algorithmic
   error (off-by-one, wrong base case, incorrect edge case handling). Iscan [2026]
   confirms that content — including actual output — drives repair improvement
   (code+facts +18pp, p=0.00042), not mere re-exposure.

**Why the triple is necessary.** Each component addresses a distinct failure mechanism.
Docstring alone provides intent but no diagnostic. The I/O pair alone provides a
target but no goal specification. The actual output alone provides a symptom but no
intended behavior. Only the triple provides the full semantic gap description: intent
→ expected behavior → actual behavior.

**Prompt construction.** The Condition C repair prompt is structured as:

```
[Original problem prompt]

--- Specification Context ---
DOCSTRING (formal intent): [problem docstring]

FAILING TEST:
  Input: [plus_input[0] from EvalPlus]
  Expected output: [plus_output[0] from EvalPlus]

ACTUAL MODEL OUTPUT:
  [stored incorrect solution from solutions_cache.jsonl]
--- End Specification Context ---

Please repair the solution so that it passes all test cases.
```

This prompt format is pre-registered before any mechanism experiment API calls.

## 3.3 Experimental Conditions

| Condition | Description | Prompt | API Calls |
|-----------|-------------|--------|-----------|
| A (Baseline) | Round-0 GPT-4o-mini output | None (existing h-e1 data) | 0 |
| B (Blind reprompt) | Original prompt + "Please try again" | No error context | 128 |
| C (Spec-aligned repair) | Original prompt + specification triple | Docstring + I/O + actual output | 128 |

**Condition A** uses h-e1 Run 2 pass/fail results directly — no new API calls. All 128
working-set problems failed in round-0 by definition.

**Condition B** prompt: `[problem prompt]\n\nThe above solution is incorrect. Please try again.`

**Rationale for Condition B.** Self-Refine [Madaan et al., 2023] establishes that
blind reprompting improves over baseline. Including Condition B as a placebo control
isolates the value of specification context over mere re-exposure, following the
placebo-controlled design of Iscan [2026].

## 3.4 Data Infrastructure

**Source.** The 134-problem failure set is drawn from the h-e1 Run 2 archive:

```
docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/
├── humaneval_samples_eval_results.json  # 34 HumanEval+ failures
├── mbpp_samples_eval_results.json       # 100 MBPP+ failures
└── solutions_cache.jsonl               # 542 entries (GPT-4o-mini outputs)
```

**Verification (h-e1-v2).** We verify four conditions before any repair API calls
(Figure 2):

- **C1**: 134 failure IDs confirmed (34 HE+ + 100 MBPP+) — existence of failure set
- **C2**: 134/134 failure task IDs have stored GPT-4o-mini solutions in `solutions_cache.jsonl`
- **C3**: All 134 IDs accessible via `get_human_eval_plus()` / `get_mbpp_plus()` EvalPlus API
- **C4**: Deterministic test selection confirmed — sample task `HumanEval/10` has 780
  `plus_input` test cases; `plus_input[0]` is deterministically accessible

This verification establishes that Condition C prompts can be constructed for 128 of
134 tasks without new baseline API calls. Six tasks (HumanEval/143, Mbpp/725, 726,
765, 805, 809) have empty `plus_fail_tests` in the archive and are excluded from
Conditions B/C, yielding the 128-task working set.

**Test selection.** For each task in the 128-task working set, the counterexample for
Condition C is `plus_input[0]` — the first test case in EvalPlus's deterministic
ordering. This selection is pre-registered and reproducible across experimental runs.

## 3.5 Statistical Design

**Primary test (h-m1, P1).** One-tailed McNemar's test on the 2×2 contingency table
of Condition B vs. Condition C fix outcomes across 128 problems:

|  | Fixed by C | Not fixed by C |
|--|------------|----------------|
| **Fixed by B** | — | b |
| **Not fixed by B** | c | — |

Success criterion: one-tailed p < 0.05 (direction: C > B). Yates' continuity
correction applied if any cell count < 5.

**Secondary test (h-m2, P2).** One-tailed McNemar's test for Condition C vs.
Condition A. Since all Condition A outcomes are fail (by definition of the working
set), this reduces to: fix rate under C ≥ 15% (threshold from FeedbackEval baseline:
21.1pp average fix rate) with McNemar p < 0.05 vs. the all-fail baseline.

**Exploratory analysis (h-c1, P3).** Stratified fix rates by benchmark type (34 HE+
vs. 100 MBPP+) with Fisher's exact test. Directional comparison only; statistical
significance not required for this exploratory prediction.

**Fallback.** If discordant pairs b + c < 25, Fisher's exact test on the full 2×2
table replaces McNemar (pre-planned fallback, following Iscan [2026]).

**Model and hyperparameters.** GPT-4o-mini, temperature=0.2, seed=42 (pre-registered).
Temperature > 0 avoids greedy fixed-point suppression of Condition B; seed=42 ensures
reproducibility.

## 3.6 Implementation

The existence verification is implemented as a single-script architecture
(`verify_h_e1_v2.py`, ~80 lines) with four verification functions corresponding to
C1-C4. Five pytest integration tests cover all conditions. The script runs in ~2
seconds (CPU-only, no model inference). All code is available in the project repository.

For the mechanism experiments (h-m1, h-m2), the implementation will reuse the proven
components from h-e1-v2: `_check_c1_failure_ids` for failure ID loading,
`_check_c2_stored_solutions` for solution retrieval, and `_check_c3_evalplus_api`
for augmented test access.
