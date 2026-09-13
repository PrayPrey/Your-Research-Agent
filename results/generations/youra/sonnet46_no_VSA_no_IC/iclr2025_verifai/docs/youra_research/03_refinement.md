# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-22T00:00:00+00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: Gap-1
- **Gap Title**: No Direct Empirical Comparison of Specification-Aligned vs. Blind Reprompting vs. Raw-Error Repair on EvalPlus Semantic Failure Set
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 6

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 6

**Convergence Reason**: All 6 convergence criteria met at Exchange 6 (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- h-e1's SA oracle failure (ruff+mypy fires on 16-32% only) directly motivates the pivot to structured specification context as the repair oracle
- EvalPlus provides all three oracle components natively (docstring, augmented tests, canonical solution) — zero new infrastructure
- The (docstring + failing test I/O + actual output) triple maps to a CEGIS counterexample, giving the mechanism theoretical grounding
- McNemar's test is validated by Iscan 2026's placebo-controlled design — appropriate for content vs. exposure comparison
- n=134 provides adequate power for McNemar at realistic fix rates (15-40%)

### Breakthrough Moments
- **Prof. Pax** identified that all oracle components are natively in EvalPlus — no new data collection required
- **Prof. Rex** flagged the greedy fixed-point problem with temperature=0, leading to the temperature=0.2 seed=42 pre-registration
- **Dr. Nova's** CEGIS analogy gave the mechanism theoretical grounding beyond "more information is better"

---

## Final Hypothesis

### Title
Specification-Aligned Repair: Structured Semantic Gap Description as Oracle for EvalPlus Code Repair

### Hypothesis ID
H-SpecRepair-v1

### Core Claim
Under GPT-4o-mini on the 134 h-e1 Run 2 EvalPlus failures (34 HumanEval+ + 100 MBPP+), if the repair prompt includes structured specification context — (1) problem docstring's formal intent, (2) failing test's input/expected-output pair, and (3) model's actual incorrect output (Condition C: spec-aligned repair) — then round-1 pass@1 will be significantly higher than blind reprompting without error context (Condition B) and the round-0 baseline (Condition A), measured by one-tailed McNemar's test (α=0.05, temperature=0.2 seed=42), because the structured triple provides a formal semantic gap description — the minimum information required for targeted algorithmic repair.

### Mechanism
The triple creates a formal semantic gap description operating through three complementary steps:
1. **Docstring re-anchoring**: The problem docstring's formal intent prevents re-generation of the same incorrect algorithm by giving the model the intended specification
2. **Behavioral gap identification**: The failing test's input/expected-output pair provides a CEGIS-style counterexample — a concrete specification violation the model can reason from
3. **Deviation detection**: The model's actual incorrect output enables the model to compare its reasoning to expected behavior and identify where it diverged

---

## Predictions

| ID | Statement | Success Criterion | Primary |
|----|-----------|-------------------|---------|
| P1 | Spec-aligned repair (C) statistically outperforms blind reprompting (B) | McNemar one-tailed p < 0.05 for C vs. B | ✅ Yes |
| P2 | Spec-aligned repair (C) statistically outperforms round-0 baseline (A) | McNemar one-tailed p < 0.05 for C vs. A; fix rate ≥ 15% | No |
| P3 | HE+ fix rate > MBPP+ fix rate (complexity interaction) | Directional; Fisher's exact for subgroups | No |

---

## Novelty

**What's new:** First 3-condition McNemar ablation (baseline / blind reprompt / spec-aligned) on EvalPlus's own semantic failure set. The B vs. C comparison directly tests whether semantic gap description (not mere re-exposure) drives LLM code repair improvement.

**How it differs:**
- Haeri & Ghelichi 2026: spec grounding vs. ungrounded, no B vs. C isolation, not EvalPlus
- FeedbackEval 2025: typed feedback comparison, no EvalPlus native oracle, no h-e1 failure set
- Self-Refine 2023: feedback vs. no-feedback, no explicit blind reprompt baseline
- Iscan 2026: validates McNemar design, not code-specific on EvalPlus

---

## Experimental Design

| Element | Specification |
|---------|--------------|
| **Model** | GPT-4o-mini (OpenAI API) |
| **Temperature** | 0.2, seed=42 (pre-registered) |
| **Dataset** | EvalPlus HE+ + MBPP+ — h-e1 Run 2 failure subset (n=134) |
| **Condition A** | Round-0 baseline (h-e1 Run 2 results — no new API calls) |
| **Condition B** | Blind reprompt: problem prompt + "Please try again." |
| **Condition C** | Spec-aligned: docstring + first failing test I/O + actual model output |
| **Failing test selection** | First failing test from EvalPlus deterministic ordering (pre-registered) |
| **Fix definition** | Passes ALL EvalPlus augmented tests (not just prompted test) |
| **Statistical test** | One-tailed McNemar's test (Yates' correction if any cell < 5) |
| **API calls** | 268 new calls (134 × 2 conditions) |
| **Cost** | ~$0.05 |
| **Runtime** | <10 minutes |

---

## Limitations

- Results specific to GPT-4o-mini — generalization to other models not tested
- Results specific to EvalPlus (HE+ + MBPP+) — other benchmarks not covered
- Single-turn repair only — multi-round repair not addressed
- Component ablation (which part of the triple matters most) deferred to Phase 5
- n=34 for HE+ subgroup limits stratified analysis power

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 6 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Pre-registration items only (addressed in Phase 2B) |

**Pre-registration items for Phase 2B:**
1. Exact Condition C prompt template format (XML tags, section labels, ordering)
2. Temperature=0.2 seed=42 confirmed as API call parameters
3. McNemar Yates' correction rule (if any cell count < 5, apply correction)

---

*Phase 2A Complete — Ready for Phase 2B*
