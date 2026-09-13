# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-04T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1
- **Gap Title**: No Controlled Comparison of Execution-Filtered SFT Data (Compile-Only vs Compile+Test) at Equal Token Budget
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Recursive Entry**: v7 (ROUTED_TO_PHASE_2A from Phase 4 H-E1)

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15 (min_exchanges = 15, natural convergence at threshold)

**Convergence Reason**: All 6 convergence criteria PASS at Exchange 15; all 6 personas participated with genuine disagreement and refinement

### Key Insights
- Prof. Rex's exec() attack (Exchange 6) forced the design toward doctest extraction — `exec()` on function definitions ≈ `compile()`, making the two-tier design nearly identical without doctests
- Dr. Ally's single-corpus solution (Exchange 5) solved the corpus format confound: all three conditions from The Stack Python avoids conflating filtering level with data format
- The mechanism-agnostic framing (Prof. Rex, Exchange 12) strengthened the hypothesis by not committing to an unverifiable mechanism at Phase 2A
- Prof. Pax confirmed token budget feasibility at 5% doctest prevalence (Exchange 15): ~5.6B tokens available from The Stack Python → sufficient at 500M-1B SFT budget

### Breakthrough Moments
1. **Exchange 5 (Dr. Ally)**: Three-tier exec filter from single corpus eliminates corpus confound without subprocess — key design breakthrough
2. **Exchange 6 (Prof. Rex)**: `exec()` on function definitions ≈ `compile()` — forced doctest solution as genuine functional gate
3. **Exchange 7 (Dr. Nova)**: Doctest extraction from The Stack Python as functional execution gate — creative resolution
4. **Exchange 12 (Prof. Rex)**: Mechanism-agnostic framing accepted — makes hypothesis robust without sacrificing precision

---

## Final Hypothesis

### Title
**Exec-FilteredSFT**: Execution-Filtered SFT Data from Raw Corpus Improves Code LLM Performance at Equal Token Budget

### Hypothesis ID
H-ExecFilteredSFT-v1

### Core Claim
Under equal token budget from The Stack Python corpus (SFT stage, Python language, Qwen2.5-Coder-1.5B primary / 7B secondary), if training data is execution-filtered (compile-only via `compile()` AST check, or doctest-passing via `compile()` + `doctest` module execution), then HumanEval pass@1 and MBPP pass@1 improve over unfiltered-subset SFT of equal token count, because execution filtering retains syntactically and functionally consistent training examples, reducing exposure to malformed patterns and improving distributional alignment with benchmark-style correct code.

**H0 (Null)**: No significant difference in HumanEval pass@1 or MBPP pass@1 between execution-filtered SFT and unfiltered SFT at equal token budget from The Stack Python.

### Mechanism (Mechanism-Agnostic)
Execution filtering selects syntactically/functionally valid programs → SFT on filtered corpus reduces exposure to malformed patterns → reduced invalid pattern exposure improves model distributional alignment with benchmark-style correct code → higher HumanEval/MBPP pass@1.

The specific pathway is one of three candidate mechanisms (noise reduction, distribution shift, coverage concentration) — mechanism disambiguation deferred to Phase 2B intermediate metrics.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | compile+test-filtered SFT outperforms unfiltered SFT on HumanEval pass@1 (Qwen2.5-Coder-1.5B) | ΔHumanEval ≥ 2pp absolute AND paired bootstrap p < 0.05 | ΔHumanEval < 2pp OR p > 0.05 |
| **P2** (secondary) | Filtering strictness ordering: compile+test ≥ compile-only ≥ unfiltered on HumanEval | Ordering holds across all three conditions | Any ordering violation |
| **P3** (confound check) | Doctest stratum not systematically better: compile-only-doctest-subset ≈ compile-only-full within 1pp | |ΔP3| ≤ 1pp on HumanEval | ΔP3 > 1pp (stratum selection dominates) |

---

## Novelty

**What's new:** No prior work (a) applies execution filtering to raw corpus SFT, (b) controls equal token budget, (c) compares compile-only vs. compile+test within single corpus, (d) includes stratum confound check.

**Differentiation from prior work:**
- **phi-1**: GPT-4 oracle (opaque, expensive) vs. this study's objective execution gates (model-agnostic, reproducible)
- **EffiCoder**: Inference-time execution selection on instruction data vs. training-time corpus filtering on raw Stack Python
- **StarCoder/cristinaimprota**: Heuristic filters (no execution gate) vs. compile/doctest execution testing
- **OpenCodeInstruct**: Instruction-tuning format vs. raw corpus SFT

---

## Experimental Design

**Corpus:** The Stack Python (bigcode/the-stack-dedup, Python subset)

**Models:** Qwen2.5-Coder-1.5B (primary), Qwen2.5-Coder-7B (secondary)

**Four conditions (from single corpus, equal token budget N):**
1. Unfiltered: random subsample to N tokens
2. Compile-only: `compile(code, '<string>', 'exec')` gate → subsample to N tokens
3. Doctest-passing: compile + `doctest` module execution → subsample to N tokens
4. Compile-only-doctest-subset: compile gate on doctest-bearing files only → subsample to N tokens (P3 confound check)

**Evaluation:** HumanEval pass@1 + MBPP pass@1 via lm-evaluation-harness; paired bootstrap (n=1000) for P1 significance

**Pilot required:** 10k Stack Python files → measure doctest prevalence. If <3%: compile+test condition infeasible; run compile-only as primary (P1/P2 still answerable).

---

## Limitations

- Doctest prevalence estimated (5-10%) but not empirically verified — pilot required
- Doctest-bearing stratum may be biased toward library/teaching code
- 7B model result is secondary/exploratory — primary hypothesis on 1.5B only
- Mechanism (noise reduction vs. distribution shift vs. coverage concentration) not distinguished by P1/P2
- Scope limited to Python, The Stack, Qwen2.5-Coder family

---

## H-E1 Failure Mode Avoidance

| H-E1 Failure Mode | Avoidance Strategy in H-ExecFilteredSFT |
|-------------------|------------------------------------------|
| APPS harness subprocess isolation | No subprocess — all filtering via `compile()` and `doctest` module in-process |
| APPS interview-level difficulty (11.6% compile rate) | The Stack Python: open-source code with diverse difficulty; much higher compile rates expected |
| Joint compile+test signal window constraint (0/200) | No joint window gate — each condition is an independent data stratum |
| RL execution feedback loop | SFT data filtering only — no RL, no reward model, no PPO |

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Natural convergence at Exchange 15 (minimum threshold) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Doctest prevalence pilot (pre-experiment); mechanism disambiguation (Phase 2B) |

---

*Phase: 2A - Hypothesis Generation via Self-Play Dialogue*
*Architecture: Self-Play Loop, Claude-only, IC-ablation (no external orchestrator)*
*Next Step: Phase 2B — Sub-hypothesis decomposition and verification planning*
