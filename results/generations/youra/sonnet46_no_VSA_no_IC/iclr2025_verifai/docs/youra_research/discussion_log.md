# Phase 2A Discussion Log
## Research Gap: 3-Condition McNemar Comparison of Specification-Aligned vs. Blind Reprompting vs. Raw-Error Repair on EvalPlus

**Date:** 2026-08-22
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)
**Gap ID:** Gap-1
**Gap Title:** No Direct Empirical Comparison of Specification-Aligned vs. Blind Reprompting vs. Raw-Error Repair on EvalPlus Semantic Failure Set

---

### Previous Failure / Routing Context

**Hypothesis h-e1 (Run 2) — FAILED — ROUTED_TO_PHASE_0**

| Memory File | Status | Failure Type |
|-------------|--------|-------------|
| failure_h-e1_run2.md | FAIL | MUST_WORK_FAIL |
| snapshot_h-e1_20260822.md | FAILED | ROUTED_TO_PHASE_0 |

**Root Cause:** Hypothesis h-e1 assumed ruff+mypy static analysis (SA) oracle fires on ≥50% of GPT-4o-mini round-0 failures on EvalPlus. Actual fire rates: 32.4% HE+, 16.0% MBPP+. EvalPlus failures are **semantic errors** (wrong algorithm, wrong edge-case), not syntactic — SA cannot detect them.

**Prohibited Directions:**
- Do NOT use ruff/mypy or any SA tool as a proxy for functional correctness
- Do NOT assume SA fire rate correlates with repair opportunity

**Validated Assets:**
- h-e1 Run 2 failure set: 34 HE+ + 100 MBPP+ = 134 problems (reusable)
- EvalPlus infrastructure (subprocess oracle) is clean and reusable
- GPT-4o-mini round-0 pass rates: 79.3% HE+, 73.5% MBPP+

**New Direction:** Replace SA oracle with execution-based feedback using structured specification context (docstring formal intent + failing test input/expected output + actual model output).

---

### Research Gap Briefing

**Primary Question:** Does specification-aligned repair feedback (docstring intent + failing test input/expected output + actual model output) produce statistically significant pass@1 improvement over blind re-prompting and raw-error repair for GPT-4o-mini on the 134 h-e1 Run 2 failures, measured by one-tailed McNemar's test (α=0.05)?

**Three Conditions:**
- **Condition A (Baseline):** Round-0 pass/fail result (h-e1 Run 2 data — already collected)
- **Condition B (Blind Reprompt):** Round-1 with no error context — "try again"
- **Condition C (Spec-Aligned):** Round-1 with docstring formal intent + failing test input/expected output + actual model output

**Key Literature:**
- Haeri & Ghelichi 2026 (arXiv:2607.06636): +38pp with spec grounding
- Dai, Liu et al. 2025 (arXiv:2504.06939): Removing docstrings = severe degradation
- Iscan 2026 (arXiv:2606.31511): McNemar validated, content matters not re-exposure
- Kong, Xie et al. 2024 (arXiv:2403.01971): Contrastive I/O pairs > raw error

**Feasibility Constraints:**
- Must use existing EvalPlus benchmark (no new benchmarks)
- Must use existing 134-problem failure set (no synthetic data)
- No human evaluation (automated McNemar)
- 268 new API calls (134 × 2 conditions) — fully feasible

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The convergence of h-e1's failure with the specification grounding literature opens a genuinely exciting angle. We're not just proposing another "give the LLM feedback" study — we're proposing a *formal semantic gap description* as the repair oracle. The key novelty here is the triple structure: docstring formal intent (what the problem *asks*), failing test input/expected output (the *gap* between specification and behavior), and actual model output (the *deviation*). This triple gives the LLM precisely what a human programmer uses when debugging: the intent, the expected behavior, and the observed behavior.

What's genuinely new is the *isolation* from h-e1's failure. Prior work (Self-Refine, FeedbackEval) compares feedback vs. no-feedback. We're doing something more surgical: (A) no repair context, (B) naive re-exposure ("try again"), (C) structured specification context. The B vs. C comparison is the key novelty — it tests whether *semantic gap description* drives repair, not merely *additional sampling* or *syntactic error information*. Iscan 2026's placebo-controlled design directly validates this approach, showing content matters, not exposure.

Three creative angles: (1) Could the docstring's *formal type constraints* (input/output types from the test pair) serve as a lightweight type specification? (2) Is there a problem-complexity interaction — does spec-aligned repair help most on algorithmically complex problems (HE+)? (3) Could we treat the failing test as a *counterexample* in the CEGIS sense?

**Key Points:**
- Core novelty: B vs. C comparison isolates semantic gap description vs. mere re-sampling
- Docstring + failing test pair = formal semantic gap description
- CEGIS analogy: counterexample-guided synthesis from concrete failure
- Problem-complexity interaction hypothesis worth exploring

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises the right structural point about the B vs. C comparison, but I want to stress-test the falsifiability of this design. The one-tailed McNemar's test (α=0.05) on n=134 is the right statistical choice — paired, non-parametric, appropriate for binary pass/fail outcomes.

Power analysis: McNemar requires sufficient *discordant pairs*. With n=134 and expected fix rates of 15–40% (Phase 1 literature), we expect roughly 20–54 repairs under C and ~10–20 under B. That yields enough discordant pairs for McNemar with p<0.05 at 80% power — power is adequate.

Null hypothesis: H₀ = "the probability of being fixed by C but not B equals the probability of being fixed by B but not C." One-tailed H₁ = P(fixed by C, not B) > P(fixed by B, not C). Direction is pre-specified, appropriate given strong prior from literature (Haeri 2026: +38pp; FeedbackEval: docstring removal = severe degradation).

Critical: the experiment is *replication-controlled* by using the existing 134-problem failure set. No randomness in problem selection. We should use temperature=0.2 seed=42 to allow some stochasticity while maintaining reproducibility.

**Key Points:**
- McNemar power adequate: n=134, expected 20–54 discordant pairs
- Null hypothesis precisely stated; pre-specified direction appropriate
- Temperature=0.2 seed=42 recommended for reproducibility + stochasticity
- Replication-controlled by fixed failure set

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both Dr. Nova and Prof. Vera have identified the right scientific core. Let me assess impact.

*Practical significance*: The 134-problem failure set represents the exact failure mode of GPT-4o-mini on EvalPlus — semantic algorithmic errors. A positive result (C > B, C > A, p<0.05) would establish structured specification context as the actionable oracle for production LLM code repair loops. EvalPlus has 2073 citations — large impact surface.

*Theoretical significance*: Confirming B vs. C would provide the first empirical evidence that *semantic gap description* (not mere error exposure or syntactic feedback) is the causal driver of LLM code repair improvement. The *negative result* is equally significant: if C fails to outperform B, it challenges the generalization of Haeri 2026 (+38pp) to the specific EvalPlus semantic failure mode, redirecting toward architectural changes (multi-round repair, self-consistency sampling, retrieval-augmented repair).

Research impact: High regardless of direction. The 3-condition design on a well-characterized failure set is a methodologically clean contribution.

**Key Points:**
- Positive result: establishes spec-aligned oracle for production repair loops (EvalPlus 2073 citations)
- Negative result: equally significant — redirects from oracle enrichment to architectural changes
- First empirical isolation of semantic gap description as causal driver
- Methodologically clean: paired design on fixed failure set

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me flag concrete implementation requirements.

**Oracle extraction:** EvalPlus's `get_human_eval_plus()` returns `problem["prompt"]` (docstring), `problem["plus_input"]` (augmented test inputs), and `canonical_solution`. Condition C prompt triple: (1) `problem["prompt"]`, (2) one failing `plus_input` test case + expected output, (3) model's actual incorrect output. All three components are natively available — no new infrastructure.

**API calls:** 134 × 2 conditions = 268 new API calls to GPT-4o-mini. Cost ~$0.05. Time with conservative batching: ~5–10 minutes.

**McNemar test:** `scipy.stats.mcnemar()` — one line of code on a 2×2 contingency table: [fixed by both, fixed by C not B, fixed by B not C, fixed by neither].

**Gap to flag:** Exact Condition C prompt template (XML tags, separators, explicit labels) could affect results — must be pre-registered before Phase 3.

**Key Points:**
- All oracle components natively in EvalPlus — zero new infrastructure
- 268 API calls, ~$0.05 cost, <10 minutes runtime
- McNemar is one scipy call on a 2×2 table
- Exact Condition C prompt template must be pre-registered before Phase 3

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Synthesizing all perspectives into the core hypothesis:

**Core Hypothesis:** Under GPT-4o-mini on the 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+): if the repair prompt includes structured specification context — (1) problem docstring's formal intent, (2) failing test's input/expected-output pair, (3) model's actual incorrect output — then round-1 pass@1 will be significantly higher than both blind reprompting (Condition B) and round-0 baseline (Condition A), measured by one-tailed McNemar's test (α=0.05, temperature=0.2 seed=42), because the structured triple provides a *formal semantic gap description* — the minimum information required for targeted algorithmic repair.

**Mechanism:** Model uses docstring to re-anchor on intended algorithm; test input/expected output to identify the specific behavioral gap; its own incorrect output to detect where reasoning diverged from specification. This triple creates a *grounded counterexample* — a concrete specification violation the model can reason from.

**Key Points:**
- Under-If-Then-Because structure fully specified
- Mechanism: grounded counterexample = docstring anchor + behavioral gap + deviation detection
- Pre-specified direction from strong literature prior (Haeri +38pp, Iscan validated McNemar)
- Isolates semantic gap description specifically on EvalPlus failure set

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Three objections before this is ready for Phase 2B.

**Objection 1 — Temperature and Condition B performance:** At temperature=0, GPT-4o-mini may produce *identical output* for Condition B (pure greedy fixed-point). This could artificially suppress B's performance. **Mitigation:** Dr. Ally's temperature=0.2 seed=42 recommendation resolves this.

**Objection 2 — Failing test selection:** Multiple failing tests per problem in h-e1 Run 2 results. Which failing test case goes into Condition C prompt? **Mitigation:** Use the *first* failing test case from EvalPlus's deterministic test ordering. Pre-specified.

**Objection 3 — Fix definition:** "Fixed" = passes ALL EvalPlus test cases after round-1 repair, not just the prompted test. Must be explicit to avoid overcounting partial fixes.

**Key Points:**
- Temperature=0.2 seed=42 for both conditions (not temperature=0)
- Failing test selection: first failing test (deterministic, pre-specified)
- Fix definition: must pass ALL EvalPlus tests, not just the prompted one
- McNemar with Yates' continuity correction if any cell count < 5

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The B vs. C comparison on EvalPlus's own semantic failure set is a novel controlled ablation not present in the literature. The CEGIS-grounded interpretation of the failing test as a formal counterexample adds theoretical depth. The pivot from h-e1's SA approach to semantic gap description represents a principled, literature-motivated redesign.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** One-tailed McNemar's test on n=134 with pre-specified direction is rigorous and well-powered. The null hypothesis is precisely stated. Temperature=0.2 seed=42 and first-failing-test selection are both pre-specifiable, making the experiment fully pre-registerable. All falsification conditions are clear.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Both positive and negative results carry significance. Positive: establishes spec-aligned oracle for production repair loops in EvalPlus's widely-cited framework. Negative: redirects community from oracle enrichment toward architectural changes. The 3-condition paired design is a methodologically clean contribution.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All oracle components are natively available in EvalPlus. 268 API calls at ~$0.05 total. McNemar test is a single scipy call. No new benchmarks, no human evaluation, no synthetic data. The h-e1 Run 2 failure set is fully reusable. Implementation is straightforward Python.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a clean, well-specified hypothesis: specification-aligned repair — providing GPT-4o-mini with a structured triple of (docstring formal intent, failing test input/expected output, actual model output) — will produce statistically significant pass@1 improvement over blind reprompting on the 134 h-e1 Run 2 EvalPlus failures, as measured by one-tailed McNemar's test at α=0.05 with temperature=0.2 seed=42.

The core mechanism is grounded counterexample reasoning: the model uses the docstring to re-anchor on the intended algorithm, the test pair to identify the behavioral gap, and its own output to detect the deviation. This triple is the minimum information needed for targeted algorithmic repair — not syntax checking, not style linting, but formal semantic gap description.

The hypothesis is directly motivated by the h-e1 failure (SA oracle falsified) and supported by five convergent literature sources (Haeri +38pp, FeedbackEval docstring-critical, Iscan McNemar validated, ContrastRepair I/O pairs > raw error, DUALFIX spec > execution). The experiment requires only 268 new API calls on the existing failure set. Three testable predictions: (P1) C > A McNemar p<0.05, (P2) C > B McNemar p<0.05, (P3) stratified analysis by HE+ vs. MBPP+ and difficulty.

All six convergence criteria are met. Hypothesis is ready for Phase 2B verification protocol.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Temperature selection (0.2 seed=42) must be explicitly pre-registered before Phase 3 API calls
- First-failing-test selection rule must be implemented deterministically (EvalPlus test ordering)
- Fix definition (all tests, not just prompted test) must be enforced in evaluation code
- **Mitigation Strategy:** Pre-register all three implementation choices as an experiment protocol document in Phase 2B before any API calls are made. McNemar with Yates' continuity correction if any cell count < 5.
