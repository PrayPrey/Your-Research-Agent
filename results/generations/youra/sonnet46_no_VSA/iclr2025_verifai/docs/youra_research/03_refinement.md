# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-03T13:00:00+00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: No Execution-Based Contract-Strength Measurement Across LLM Families on ContractEval
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Convergence**: Exchange 15 (min=15, max=20)

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- EvalPlus's published static test inputs (764/task) can be reused for oracle isolation without new data generation — the decisive experimental design insight
- The "contract-unique failure" category (output-equal-to-gt but contract-failing) is the primary scientific signal, separating oracle strength from mere fuzzing amplification
- h-e1's confirmed violations (7.42% on tractable subset) serve as the validated lower bound and precedent for the new experiment
- Hypothesis filter rate per task must be reported explicitly — complex pre-conditions may limit effective sampling for some tasks

### Breakthrough Moments
- **Exchange 9 (Prof. Pax)**: Identifying EvalPlus static inputs as the oracle isolation substrate — zero new data generation needed
- **Exchange 12 (Prof. Rex)**: Classifying violations into contract-unique vs. redundant — the diagnostic that distinguishes semantic oracle strength from brute-force fuzzing
- **Exchange 13 (Dr. Ally)**: Connecting contract-unique violations back to h-e1's 27 confirmed violations as empirical precedent

---

## Final Hypothesis

### Title
Execution-Based Contract Strength Gap: A Cross-Model Measurement Study on ContractEval

### Hypothesis ID
H-ContractStrength-v2

### Core Claim (Under-If-Then-Because)
Under ContractEval's 364 HumanEval+/MBPP+ tasks, if LLM-generated programs that pass all unit tests are evaluated via Hypothesis PBT with icontract-hypothesis strategy inference, then (a) the mean contract-failure rate exceeds EvalPlus matched-input differential-oracle failure rate by ≥10% absolute (with ≥5% from contract-unique violations), (b) model rankings on contract-satisfaction differ from pass@1⋆ with Kendall τ ≤ 0.6, and (c) contract-strength gap varies by ≥10% absolute between best/worst model families, because contracts encode universal properties (relational invariants, quantified conditions) that finite test suites cannot exhaustively check.

### Null Hypothesis
Execution-based contract checking provides no statistically significant signal beyond EvalPlus dense differential testing: mean oracle-isolation gap ≤ 2%, Kendall τ ≥ 0.8 with pass@1⋆, contract-satisfaction rate explained by pass@1⋆ + model size (R² ≥ 0.85).

### Mechanism
LLM-generated code satisfies finite test cases via pattern completion on training-distribution inputs. ContractEval contracts encode universal properties (relational invariants, quantified conditions over all valid inputs) unreachable by finite test suites. Hypothesis PBT explores beyond test coverage via adaptive search guided by pre-conditions (icontract-hypothesis), finding inputs where the LLM implementation violates the universal property despite matching ground truth on provided tests.

---

## Predictions

### P1 — Oracle Strength (PRIMARY)
- **Statement**: Mean contract-failure rate on EvalPlus static inputs ≥10% above differential oracle failure rate, with ≥5% from contract-unique violations (output-equal but contract-failing)
- **Test**: Experiment A — re-evaluate EvalPlus 764-test inputs under contract oracle; Wilcoxon signed-rank test, Holm correction
- **Success Criterion**: Mean gap ≥ 0.10, Wilcoxon p < 0.01; contract-unique mass ≥ 0.05 (bootstrap 95% CI lower bound > 0.03)
- **Falsifier**: Mean gap ≤ 0.02 or p > 0.05 after correction

### P2 — Ranking Orthogonality
- **Statement**: Kendall τ ≤ 0.6 between contract-satisfaction and HUMANEVAL+ pass@1⋆ rankings; ΔR² ≥ 0.10 in regression controlling for pass@1⋆
- **Test**: Experiment B — per-model contract-satisfaction rates; Kendall τ permutation test; partial F-test for regression
- **Success Criterion**: τ ≤ 0.6 (permutation p < 0.05) AND ΔR² ≥ 0.10
- **Falsifier**: τ ≥ 0.8 OR ΔR² < 0.05

### P3 — Cross-Model Variation
- **Statement**: ≥10% absolute gap between best/worst model families on contract-strength gap, beyond pass@k differences
- **Test**: Mixed-effects model controlling for task difficulty and pass@k; model family coefficient significance test
- **Success Criterion**: Range ≥ 0.10, model family p < 0.05 controlling for pass@k
- **Falsifier**: Range < 0.05 or non-significant after pass@k control

---

## Novelty

### What's New
First execution-based (not SMT) cross-model contract-strength gap measurement on ContractEval. Oracle isolation experiment using EvalPlus published inputs — cleanly separates oracle strength from adaptive search without new data.

### How It Differs from Prior Work
| Prior Work | Limitation | Our Addition |
|------------|-----------|--------------|
| ContractEval (Lim et al. 2025) | SMT only, 25.82% tractable, 5 open models | Execution-based, 100% tractable, 5 models incl. closed |
| Bose 2025 (PBT on MBPP/HumanEval) | 2 models, no oracle isolation | 5 models, oracle isolation experiment |
| EvalPlus (Liu et al. 2023) | Differential oracle only, no contracts | Contract oracle, oracle isolation |
| h-e1 (Z3 approach) | 25.82% tractable, failed gate | 100% tractable by construction |

---

## Experimental Design

### Oracle Soundness Pre-Check
Run Hypothesis (100k examples, 2h wall-clock) against ContractEval reference implementations. Quarantine tasks with violations (expected: ~0%). Required before any model evaluation.

### Experiment A — Oracle Isolation (Zero New Data)
Load EvalPlus published 764-test-per-task inputs. Evaluate test-passing LLM programs under (1) differential oracle (ground-truth equality) and (2) ContractEval contract oracle. Classify failures into contract-unique vs. redundant. Tests P1.

### Experiment B — Adaptive Hypothesis PBT
For each (model, task, program), run Hypothesis with icontract-hypothesis strategy inference: 5,000 max examples, fixed RNG seed, 60s wall-clock. Report violation rate, filter rate, effective sample size. Tests P2, P3.

### Models
- GPT-4o-mini (closed, evalplus OpenAI backend)
- Claude-3-haiku (closed, evalplus Anthropic backend)
- DeepSeek-Coder-V2-Lite 16B (open, vLLM)
- CodeLlama-13B (open, HuggingFace)
- CodeLlama-34B (open, HuggingFace)

### Budget
- Implementation: ~10-12 working days
- API cost: ~$50-100 for closed models (5 models × 364 tasks × 10 samples)
- Local compute: GPU for open models

---

## Limitations

- Hypothesis coverage is probabilistic — cannot guarantee complete contract-space exploration
- icontract-hypothesis may fail for complex pre-conditions (reported per task)
- Results generalize to algorithmic tasks; may not extend to SWE-bench-style software engineering tasks
- Cross-model comparison is observational — cannot attribute gaps to training decisions
- EvalPlus inputs optimized for differential mismatches, not contract failures — may under-sample contract-unique states

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-ContractStrength-v2 |
| **Discussion Convergence** | Exchange 15 of 15 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Addressed by design (dual-experiment, pre-registration, AST stratification) |
| **Phase 2B Ready** | Yes |

---

*Phase 2A-Dialogue complete. Produces 03_refinement.yaml (primary Phase 2B input), 02_synthesis.yaml, 01_round_table/final_opinions.yaml, discussion_log.md.*
