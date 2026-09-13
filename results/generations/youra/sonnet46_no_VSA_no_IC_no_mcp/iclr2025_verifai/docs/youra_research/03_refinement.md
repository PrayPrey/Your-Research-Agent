# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-26T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: Gap-1
- **Gap Title**: No Systematic Empirical Comparison of Formal Constraint Types on LLM Code Correctness
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10
- **Hypothesis ID**: H-StaticRepair-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Advocate), Prof. Rex (Critic)

**Total Exchanges**: 10

**Convergence Reason**: All 6 convergence criteria met at Exchange 10 — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS all satisfied.

### Key Insights

1. Decoding-time constraints (grammar/type logit masking) and post-hoc repair loops are fundamentally different intervention architectures — conflating them confounds the experiment. Focus on repair loops is the correct choice.
2. LLM-generated Z3 constraints (rather than manually encoded specs) make the experiment tractable while adding novelty — but require pre-validation against EvalPlus test cases.
3. mypy in permissive mode (`--ignore-missing-imports --no-strict-optional`) reduces false positives on dynamically-typed benchmark code.
4. MBPP+ (378 problems) is more statistically powerful than HumanEval+ (164) for detecting 1% absolute improvements — designate as primary benchmark.
5. Negative result (mypy adds no value over execution-only) is equally publishable for VerifAI — the gap is in the controlled comparison, not the expected direction.

### Breakthrough Moments

- **Exchange 2** (Prof. Vera): Separating decoding-time constraints from repair-loop architectures resolved the design confusion — this single decision focused the entire experiment.
- **Exchange 4** (Prof. Pax): LLM-generated Z3 specs make the SMT condition feasible without 40h of manual spec writing.
- **Exchange 6** (Prof. Rex): Pre-registration of Z3 subset criteria and spec pre-validation addressed the Z3 confound.
- **Exchange 7** (Dr. Nova): Curated-subset Z3 design preserves formal-methods contribution for VerifAI without contaminating the primary comparison.

---

## Final Hypothesis

### Title
**Static Analysis Feedback in LLM Code Repair Loops (H-StaticRepair-v1)**

### Core Claim
Under Python code generation on HumanEval+ and MBPP+ benchmarks, if repair loops are augmented with static analysis feedback (mypy type checking) in addition to execution-based feedback, then pass@1 after up to k=5 repair rounds increases beyond the execution-only baseline, because mypy provides error-type-specific correction signal (type mismatch location and expected type) that narrows the LLM's next-attempt distribution toward type-correct solutions.

**Null hypothesis H₀**: There is no significant difference in pass@1 (averaged over k=1..5 repair rounds) between execution+mypy repair and execution-only repair on HumanEval+ and MBPP+.

### Mechanism

1. Initial LLM generation produces code with type errors (~20-30% of failures based on EvalPlus analysis).
2. mypy feedback identifies type mismatch location and expected type — structurally richer than execution pass/fail binary signal.
3. LLM conditioned on mypy error generates repair with lower probability mass on type-incorrect tokens.
4. Effect accumulates across k=1..5 repair rounds, producing measurable pass@1 improvement.

---

## Predictions

| ID | Prediction | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | execution+mypy pass@1 > execution-only on MBPP+ and HumanEval+ | p < 0.05 on MBPP+; ≥ 1% absolute improvement | p ≥ 0.05 on both benchmarks |
| **P2** (secondary) | execution+mypy+Z3 pass@1 > execution+mypy on curated ~50-problem arithmetic subset | Positive directional delta (not significance-gated) | Z3 condition equal or worse than mypy-only |
| **P3** (mechanism) | mypy error count decreases monotonically across repair rounds 1..5 | Monotone decrease in mean mypy errors per round | Error count flat or increasing (LLM ignores mypy) |

---

## Novelty

**Primary novelty**: First controlled comparison of static analysis (mypy) as an explicit, distinct feedback channel in LLM code repair loops on HumanEval+/MBPP+.

**Differentiation**:
- vs. Self-Debug (Chen et al. 2023): execution-only baseline → this work adds mypy and isolates its contribution
- vs. Reflexion (Shinn et al. 2023): LLM-generated verbal reflection → this work uses structured static analysis output
- vs. Outlines/Guidance: decoding-time grammar constraints → different architecture entirely (repair loop vs. inference constraint)
- vs. SWE-agent (Yang et al. 2024): bash execution without static analysis as distinct channel → this work makes the channel explicit

---

## Experimental Design

**Benchmarks**: MBPP+ (378 problems, primary), HumanEval+ (164 problems, secondary), HumanEval arithmetic subset (~50 problems, Z3 analysis only)

**Model**: GPT-4o-mini (temperature=0.8 initial, 0.0 repair; 3 seeds)

**Conditions**:
1. No-repair baseline (direct generation)
2. Execution-only repair — Self-Debug (k=5 rounds)
3. Execution+mypy repair — primary treatment (k=5 rounds)
4. Execution+mypy+Z3 repair — secondary treatment, curated subset only

**Cost**: ~7,400 LLM calls = $10-15 at GPT-4o-mini pricing

**Timeline**: ~3.5 weeks solo researcher

---

## Limitations

- GPT-4o-mini only — generalization to other models requires replication
- HumanEval+ (164 problems) may be underpowered for 1% effect detection — MBPP+ is primary
- Z3 analysis restricted to ~50-problem subset — not representative of full benchmark
- Phase 1 data quality 63/100 (MCP unavailable) — arXiv IDs need manual verification before paper download
- SWE-bench excluded (too expensive for workshop scope)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-StaticRepair-v1 |
| **Discussion Convergence** | 10 exchanges; all 6 criteria met |
| **Clarity Verified** | Yes |
| **Primary Benchmark** | MBPP+ (power); HumanEval+ (secondary) |
| **Z3 Scope** | Curated ~50-problem subset only |
| **Remaining Blocking Objections** | None |
| **Mitigated Concerns** | Z3 spec confound, mypy false positives, HumanEval+ power |
| **Phase 2B Ready** | YES |
