---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Formal Specification Alignment for LLM Code Repair on EvalPlus"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-22
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Bridging formal specification alignment with LLM code repair — replacing the falsified static analysis oracle (ruff+mypy) with formal specification signals derived from EvalPlus problem docstrings and test structure, to drive round-1 repair for GPT-4o-mini on HumanEval+/MBPP+. Reuses the clean experimental infrastructure proven functional in h-e1 Run 2. Takes a NEW angle: instead of raw execution error messages, uses docstring-grounded specification alignment to guide repair — a more formal-methods-aligned oracle closer to the VerifAI workshop theme.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode — Attempt 8)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

This workshop explores the intersection of scale-driven generative AI and correctness-focused formal verification principles. Formal analysis tools (theorem provers, SAT/SMT solvers, static analyzers, execution monitors) have demonstrated success in software correctness but face scaling challenges. LLMs offer scalability but are probabilistic rather than correct-by-construction. The special theme focuses on LLMs for code generation and how formal methods from PL/verification communities can enhance LLM-driven code generation. Source Type: Workshop CFP / Structured Input (ICLR 2025 VerifAI Workshop). Retrying after h-e1 MUST_WORK FAIL — SA oracle conceptually falsified at full scale. Multiple previous brainstorm attempts (7 archived sessions) have refined the direction toward execution-based feedback repair.

---

## Lessons from Previous Attempts

### Attempt History

**h-e1 Run 1 (Infrastructure Failure):**
- Hypothesis: ruff+mypy fires on ≥70% of failed HumanEval+/MBPP+ problems for ≥2 of 3 model scales
- Why it failed: GATE_MIN_SCALES=2 not met — local vllm infrastructure failure, only 1 scale ran (n=10 debug)
- Lesson: Infrastructure fragility, not conceptual failure; SA oracle was initially promising (88.9% on n=10 debug)

**h-e1 Run 2 (Conceptual Failure — Decisive):**
- Hypothesis: ruff+mypy fires on ≥50% of GPT-4o-mini round-0 failures on HumanEval+/MBPP+ (n=538)
- Results: HumanEval+ fire rate = **32.4%** (34 failures, 11 SA fired), MBPP+ fire rate = **16.0%** (100 failures, 16 SA fired)
- Why it failed: EvalPlus failures are **semantic errors** (wrong algorithm, wrong edge-case handling), NOT syntactic or type errors. ruff detects only lint/style violations; mypy is nearly useless (0–3% fire rate).
- Root cause: The fundamental assumption that static analysis correlates with functional correctness is falsified

**Previous Brainstorm Iterations (20260822T050417 → 20260822T162103):**
- 6 previous ROUTE_TO_0 sessions all converged on "execution-based feedback repair" as the next direction
- The consistent recommendation: use EvalPlus test failure messages (raw error output) as repair oracle
- This direction has been proposed repeatedly but has not yet been validated — it may have failed in Phase 2A/2B/2C/3/4 or was never attempted due to architectural issues
- NEW ANGLE NEEDED: pivot from "raw execution error messages" → "specification-aligned repair context"

### What Showed Promise
- GPT-4o-mini achieves round-0 pass rates of 79.3% on HumanEval+ and 73.5% on MBPP+ — meaningful failure sets remain
- **Failure set is reusable**: 34 HE+ failures + 100 MBPP+ failures available without new API calls
- The experimental setup (EvalPlus + OpenAI API + subprocess oracle + McNemar statistics) is clean and reusable
- VerifAI CFP explicitly mentions "execution monitoring" and "formal structures" (context-free grammars, static analyzers, SMT-guided repair) as tools for LLM code generation
- The three-condition McNemar design (A=baseline, B=blind-reprompt, C=oracle-guided repair) is statistically sound

### How THIS Direction Avoids Those Pitfalls

**New angle: Specification-aligned repair context vs. raw error messages**

- **Previous angle**: Provide raw EvalPlus error traceback to GPT-4o-mini for repair (execution-feedback repair)
  - Risk: Raw error messages may be cryptic or misleading; the LLM may not interpret them correctly
  - This angle has been proposed 6 times but may have failed at hypothesis level due to insufficient differentiation from simple re-prompting

- **THIS angle**: Extract the formal specification from the EvalPlus problem docstring + visible test cases, construct a "specification alignment context" (what the function SHOULD do, what the test expects, what the code actually returned), and inject this structured specification-aligned feedback into the repair prompt
  - Grounded in VerifAI theme: formal specification as a verification signal
  - More actionable than raw tracebacks (tells the LLM the semantic gap, not just the syntax of failure)
  - Differentiates from blind re-prompting more sharply than raw error messages alone
  - Uses EXISTING EvalPlus structure (docstrings + test cases are already in the benchmark)
  - No new data, no new benchmarks, no human annotation required

---

## Session Plan

ROUTE_TO_0 Auto-Fill — extracted from Workshop CFP + failure context from Serena Memory (h-e1 Run 1 + Run 2 + 6 previous brainstorm archives).

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Research direction informed by:
1. Failure memory (Run 1): h-e1 GATE_MIN_SCALES=2 infrastructure failure — SA oracle functional but scale incomplete
2. Failure memory (Run 2): SA oracle fires on only 16–32% of EvalPlus failures — conceptual failure confirmed
3. Snapshot (Run 2): Failure set (34 HE+ + 100 MBPP+) reusable; execution-based feedback explicitly recommended
4. 6 previous brainstorm archives: All converged on raw execution feedback — new angle needed to avoid repeating same hypothesis
5. Workshop CFP: VerifAI special theme emphasizes formal specification, execution monitoring, and docstring-based program analysis as formal tools
6. New angle synthesis: Specification alignment context (docstring + test expectation + actual output) as repair oracle — more formally grounded than raw error message

---

## Research Question Development

### Initial Question

Does injecting a specification-alignment context (derived from EvalPlus problem docstring + failing test input/expected output) into the repair prompt produce greater pass@1 improvement than blind re-prompting or raw-error-message repair for GPT-4o-mini on HumanEval+/MBPP+?

### Refined Question

Does specification-aligned repair feedback — a structured prompt injection containing (1) the problem docstring's formal intent, (2) the failing test's input/expected-output pair, and (3) the actual incorrect output — produce a statistically significant pass@1 improvement over both blind re-prompting (no error context) and raw-error repair (EvalPlus traceback only) for GPT-4o-mini on the 134 failing problems from h-e1 Run 2 (34 HE+ + 100 MBPP+), as measured by one-tailed McNemar's test (α=0.05)?

### Detailed Sub-Questions

1. Does specification-aligned repair (round-1 with docstring intent + test input/expected + actual output) achieve statistically significant pass@1 improvement over blind re-prompting (round-1 with "try again") on the 134 h-e1 Run 2 failures, per one-tailed McNemar p<0.05?
2. Does specification-aligned repair outperform raw-error-message repair (round-1 with EvalPlus traceback only) on the same 134 failures — i.e., does the structured specification context add value beyond the error traceback alone?
3. Is there a problem-type or difficulty pattern where specification-aligned repair is most/least effective (HumanEval+ algorithmic problems vs. MBPP+ functional tasks, easy vs. hard by pass@1 baseline)?
4. What fraction of specification-aligned repairs succeed (fix rate on the 134-problem failure set), and how does it compare to the near-zero fix rate expected from SA feedback (h-e1 Run 2)?
5. How much does the specification alignment context cost in additional tokens per repair call, and what is the token efficiency ratio (fix rate per additional 1000 tokens) compared to blind re-prompting?

---

## Reference Papers

Not provided - will discover in Phase 1

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 VerifAI Workshop) — significance pre-validated. The question directly addresses the workshop's intersection themes: (1) formal methods for generative AI (docstring specifications as formal intent), (2) AI as verifiers (the specification-alignment context acts as a verifier that describes the semantic gap), and (3) special theme on LLMs for code generation with formal structures. The contrast is sharp and novel: SA gives no signal (h-e1 Run 2 proved this at 16–32%), raw error messages give syntactic context, but specification-aligned context gives SEMANTIC context (what the function should do vs. what it did). A positive result advances the formal methods + LLM code generation literature with a concrete, deployable feedback mechanism. A negative result (specification alignment fails too) would challenge the assumption that richer formal context helps LLMs self-repair and redirect toward architectural changes (bigger model, multi-round repair). The failure set from h-e1 Run 2 (134 problems) is already available — no new round-0 API calls needed.

### Feasibility Check

All sub-questions testable immediately:
- **HumanEval+** (evalplus, 164 problems — round-0 GPT-4o-mini outputs + pass/fail labels from h-e1 Run 2 already available)
- **MBPP+** (evalplus, 374 problems — same)
- **Failure set**: 34 HE+ + 100 MBPP+ failures with EvalPlus error messages already generated in h-e1 Run 2
- **Specification context extraction**: EvalPlus problem docstrings + test inputs/expected outputs are available in the benchmark (no new data needed)
- **GPT-4o-mini** via OpenAI API (OPENAI_API_KEY — only round-1 repair calls needed for 134 failures × 3 conditions)
- **Three conditions**: (A) round-0 baseline (from h-e1 Run 2, no new calls), (B) blind re-prompting (new round-1, no context), (C) specification-aligned repair (new round-1, structured context)
- **statsmodels McNemar** (pip-installable, already used in h-e1)
- **MANDATORY FEASIBILITY CONSTRAINTS**: fully satisfied — no new benchmarks, no human annotation, no synthetic data, no future data, uses existing EvalPlus benchmark and h-e1 Run 2 results

---

## Phase 1 Input Package

<phase1-input>

### research_question
Does specification-aligned repair feedback — a structured prompt injection containing (1) the problem docstring's formal intent, (2) the failing test's input/expected-output pair, and (3) the model's actual incorrect output — produce a statistically significant pass@1 improvement over both blind re-prompting (no error context) and raw-error repair (EvalPlus traceback only) for GPT-4o-mini on the 134 failing problems from h-e1 Run 2 (34 HE+ + 100 MBPP+), as measured by one-tailed McNemar's test (α=0.05)? Specifically: does the structured specification context provide a more actionable formal signal than either the absence of context or raw execution tracebacks, thereby confirming that semantic gap description — not mere additional sampling or syntactic error reporting — drives LLM code repair improvement?

### detailed_question
1. Does specification-aligned repair (round-1 with docstring intent + failing test input/expected output + actual model output) achieve statistically significant pass@1 improvement over blind re-prompting on the 134 h-e1 Run 2 failures, per one-tailed McNemar p<0.05?
2. Does specification-aligned repair statistically outperform raw-error repair (round-1 with only EvalPlus error traceback) on the same 134 failures — isolating the value of structured specification context beyond error syntax?
3. Is there a problem-type or difficulty pattern where specification-aligned repair is most/least effective (HumanEval+ algorithmic vs. MBPP+ functional, easy vs. hard by pass@1 baseline from h-e1 Run 2)?
4. What is the overall fix rate on the 134-problem failure set under specification-aligned repair, compared to the near-zero expected rate from SA feedback (h-e1 Run 2: SA fired on only 16–32% of failures)?
5. What is the token efficiency ratio (fix rate per 1000 additional tokens) of specification-aligned repair vs. blind re-prompting, computed on the n=134 failure set?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

- h-e1 Run 2 decisively falsified the SA oracle: ruff+mypy fires on only 16–32% of EvalPlus failures — semantic errors dominate, not syntactic
- 6 previous ROUTE_TO_0 brainstorm sessions all proposed "raw execution error messages" as the next oracle — this direction needs a fresh angle after repeated failures
- The VerifAI CFP explicitly frames docstring-based formal intent and execution monitoring as formal verification tools — specification alignment is a natural formal-methods angle
- Specification-aligned context (docstring intent + failing test input/expected + actual output) provides SEMANTIC gap description, not just syntactic error reporting — this is the key differentiator from raw error messages
- The experimental infrastructure is fully reusable: 134 failures with error messages + EvalPlus docstrings/tests already available, only round-1 API calls needed (3 conditions × 134 problems)
- Three-condition design (A=round-0, B=blind-reprompt, C=spec-aligned-repair) with McNemar isolates the informational value of specification context vs. raw error vs. no context

### Techniques Used

ROUTE_TO_0 Auto-Fill — Failure context recovery from Serena Memory (h-e1 Run 1 + Run 2) + analysis of 6 previous brainstorm archives + Workshop CFP extraction + specification-alignment angle synthesis

### Areas for Further Exploration

- Multi-round specification-aligned repair (round-2, round-3 with updated specification context if round-1 fails) — future work if round-1 gate passes
- SMT-guided repair as complement: Z3 counterexamples as additional formal oracle alongside specification context
- Comparison across model scales (GPT-4o vs GPT-4o-mini) for specification-aligned repair signal sensitivity
- Low-resource programming language code generation with formal scaffolding (VerifAI CFP angle)
- Theorem-prover integration for specification extraction (Lean/Coq docstring formalization) — future work beyond feasibility constraints

---

## Next Steps

Proceed to Phase 1 - Targeted Research: /phase1-targeted

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 — Failure Recovery, Attempt 8)*
*Previous attempt: h-e1 Run 2 MUST_WORK FAIL — SA oracle conceptually falsified (16–32% fire rate on semantic errors)*
*Previous brainstorm direction (×6): Raw execution error messages as repair oracle*
*New angle: Specification-aligned repair context (docstring intent + test input/expected + actual output) — semantic gap description as formal oracle*
*Ready for: Phase 1 - Targeted Research*
