# Product Requirements Document: H-E1 Baseline Measurement

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)  
**Date**: 2026-08-20  
**Status**: Phase 3 - Implementation Planning

---

## Executive Summary

Build automated evaluation harness to measure lean-auto (automated theorem prover) success rate on miniF2F Lean 4 benchmark (N=244 test problems). Establishes baseline for comparing LLM-guided theorem proving approaches.

**Success Criteria**: Success rate in 10-25% range, error rate < 5%, tactic count distribution captured.

---

## Problem Statement

Need reproducible baseline measurement of pure automated theorem proving performance on miniF2F to:
1. Validate infrastructure (lean-auto + miniF2F + Mathlib integration)
2. Establish success rate for comparison with H-M1/M2/M3 (LLM-guided approaches)
3. Measure tactic evaluation budget for H-C1 (equalized comparison)

**Gate Type**: MUST_WORK - If baseline fails or success rate outside 5-30% (indicating infrastructure issue), blocks H-M3 and H-C1.

---

## User Stories

### Primary User: Researcher validating automated prover baseline

**US-1**: As a researcher, I want to run lean-auto on all 244 miniF2F test problems with 300s timeout, so I can measure baseline success rate.

**US-2**: As a researcher, I want tactic evaluation counts logged for each solved problem, so I can set fair comparison budgets for LLM approaches.

**US-3**: As a researcher, I want checkpoint-based evaluation with crash recovery, so I don't lose progress if infrastructure fails mid-run.

**US-4**: As a researcher, I want pilot run validation (N=20) before full evaluation, so I can debug setup issues early.

**US-5**: As a researcher, I want statistical analysis (success rate + Wilson CI), so I can report results with confidence intervals.

---

## Functional Requirements

### FR-1: Dataset Loading
- Parse miniF2F Test.lean file (244 theorem statements)
- Extract theorem name, statement, source annotation (AMC/AIME/IMO)
- Validate: All 244 problems loaded, no duplicates

### FR-2: Parallel Evaluation
- Partition 244 problems across 8 worker processes (~30 each)
- Each worker evaluates assigned problems sequentially
- Isolated Lean REPL per problem (no cross-contamination)
- Timeout enforcement: 300s per problem (SIGTERM at 300s, SIGKILL at 310s)

### FR-3: Prover Invocation
- Load lean-auto with configuration:
  - `set_option auto.native true`
  - `set_option auto.smt false` (native mode only for reproducibility)
  - `set_option trace.auto true` (enable trace logging)
- Invoke `auto` tactic on theorem statement
- Capture stdout/stderr (trace logs)
- Record outcome: solved/timeout/error

### FR-4: Tactic Count Extraction
- Parse trace logs for ATP invocation patterns:
  - Primary: `[auto.native] Invoking` count
  - Fallback: `[auto.mono] Instantiating` count
- Log tactic count for each solved problem
- Validate on pilot run (manual check 5 samples)

### FR-5: Checkpointing
- Save progress every 10 problems per worker
- Checkpoint format: JSON with worker_id, completed count, results array
- Recovery: Skip completed problems on restart

### FR-6: Result Aggregation
- Merge results from 8 workers
- Validate: Total 244 problems, no duplicates, no missing data
- Output: CSV (per-problem) + JSON (summary)

### FR-7: Statistical Analysis
- Compute success rate: (solved / total) × 100
- Wilson score 95% confidence interval
- Tactic count statistics: mean, median, std, CV
- Stratification by source (if metadata available)

### FR-8: Quality Gates
- Error rate < 5% (< 12 problems)
- Tactic count captured for ≥80% of solved problems
- Reproducibility: Rerun 10% sample, 100% match (Lean is deterministic)

---

## Non-Functional Requirements

### NFR-1: Performance
- Full evaluation completes in ≤ 3 hours
- Pilot run completes in ≤ 15 minutes
- Worker isolation prevents memory leaks across problems

### NFR-2: Reliability
- Graceful handling of Lean REPL crashes (retry up to 3 times)
- Timeout enforcement at OS level (subprocess, not lean-auto internal)
- Checkpoint recovery: Restart from last checkpoint, not from scratch

### NFR-3: Reproducibility
- Pin versions: Lean 4.15.0, lean-auto git SHA, miniF2F git SHA
- Deterministic evaluation (same problem → same outcome on rerun)
- Archive: Raw logs, trace files, configuration, git SHAs

### NFR-4: Observability
- Per-problem logging: problem_id, outcome, time, tactic_count, trace_path
- Worker progress logging: "Worker 3: 10/30 completed"
- Error logging: Full stack trace for infrastructure failures

### NFR-5: Scalability
- Resource requirements: 64 cores, 128GB RAM, 50GB disk
- Worker count configurable (default 8, supports 1-16)
- Memory per worker: ≤ 16GB

---

## Technical Constraints

### TC-1: Environment
- Lean 4.15.0 (exact version, via elan)
- lean-auto: leanprover-community/lean-auto @ pinned SHA
- miniF2F: google-deepmind/miniF2F @ AlphaProof evaluation version
- Mathlib: Version from miniF2F's lean-toolchain

### TC-2: Dependencies
- Python 3.10+ (evaluation harness)
- Z3 SMT solver (lean-auto backend, though not used in native-only mode)
- Lake (Lean build tool)
- Subprocess module (timeout enforcement)

### TC-3: Data Format
- Input: Lean 4 theorem declarations from Test.lean
- Output: CSV (per-problem results), JSON (summary statistics)
- Logs: Text files (trace logs), JSON (checkpoints)

---

## Out of Scope

### OS-1: Alternative Provers
- Not evaluating: Sledgehammer, E prover, Vampire, manual tactics
- Rationale: H-E1 is lean-auto baseline only

### OS-2: Premise Selection
- Not implementing: Retrieval of relevant lemmas from Mathlib
- Rationale: Zero-shot evaluation (lean-auto uses only local context)

### OS-3: Proof Explanation
- Not generating: Human-readable proof explanations
- Rationale: Only need success/failure classification

### OS-4: Hyperparameter Tuning
- Not optimizing: lean-auto timeout, solver choice, monomorphization depth
- Rationale: Baseline uses default settings

---

## Success Metrics

### Primary Metric
**Success Rate**: 10-25% (hypothesis prediction)
- **Gate Pass**: Rate in [10%, 25%]
- **Gate Warning**: Rate in [5%, 10%) or (25%, 30%] → Revise predictions
- **Gate Fail**: Rate < 5% or > 30% → Infrastructure issue

### Secondary Metrics
- **Error Rate**: < 5% (< 12 errors out of 244)
- **Timeout Rate**: Expected 70-85% (majority of problems unsolved)
- **Tactic Count**: Mean ± Std (target ~10 ± 5 evaluations)
- **Coefficient of Variation**: CV < 100% (variance not excessive)

### Quality Metrics
- **Tactic Count Coverage**: ≥80% of solved problems have tactic count logged
- **Reproducibility**: 100% match on 10% rerun sample
- **Pilot Success**: 2-5 solves out of 20 (10-25%)

---

## Milestones

### M1: Infrastructure Setup (Day 1-2)
- Lean 4.15.0 installed via elan
- miniF2F cloned, Mathlib built
- lean-auto integrated into miniF2F lakefile
- Validation: Simple theorem proves with `auto` tactic

### M2: Harness Implementation (Day 3-4)
- Problem loader (parse Test.lean)
- Worker pool (8 parallel workers)
- Timeout handler (subprocess with SIGTERM/SIGKILL)
- Tactic extractor (trace log parser)
- Result aggregator (merge worker outputs)

### M3: Pilot Run (Day 5)
- Run N=20 sample from validation split
- Validate: 2-5 solves, logs captured, tactic counts extracted
- Quality check: Manual inspection of 5 solved problems
- Decision: Proceed to full run or debug

### M4: Full Evaluation (Day 6)
- Run N=244 problems from test split
- Checkpointing every 10 problems
- Expected duration: 2-3 hours

### M5: Analysis & Report (Day 7)
- Statistical analysis (success rate, CI, tactic stats)
- Quality gate validation
- Summary report generation
- Data archival (logs compressed, results committed)

---

## Risk Assessment

### Risk 1: lean-auto Integration Failure
- **Probability**: Medium
- **Impact**: High (blocks entire experiment)
- **Mitigation**: Pilot run catches integration issues early
- **Contingency**: Use alternative lean-auto fork or manual tactic application

### Risk 2: High Error Rate (> 10%)
- **Probability**: Low
- **Impact**: Medium (degrades baseline quality)
- **Mitigation**: Retry failed problems up to 3 times
- **Contingency**: Report baseline with error bars, flag unreliable

### Risk 3: Tactic Count Extraction Fails
- **Probability**: Medium
- **Impact**: Medium (H-C1 cannot set fair budget)
- **Mitigation**: Fallback to proxy metrics (time, proof size)
- **Contingency**: Use conservative budget estimate (mean + 2σ)

### Risk 4: Timeout Ineffective
- **Probability**: Low
- **Impact**: High (evaluation never completes)
- **Mitigation**: OS-level timeout (subprocess module)
- **Contingency**: Manually kill hung processes, reduce worker count

### Risk 5: Mathlib Build Failure
- **Probability**: Low
- **Impact**: High (cannot load miniF2F)
- **Mitigation**: Use lake cache (`lake exe cache get`)
- **Contingency**: Build from source (adds 30min setup time)

---

## Acceptance Criteria

### AC-1: Completeness
- [x] All 244 problems evaluated
- [x] Per-problem logs captured (outcome, time, tactic_count)
- [x] Summary statistics computed (success rate, CI, tactic stats)

### AC-2: Quality
- [x] Error rate < 5%
- [x] Tactic count coverage ≥ 80% of solved problems
- [x] Reproducibility: 100% match on 10% rerun

### AC-3: Gate Validation
- [x] Success rate in [10%, 25%] → PASS
- [x] OR Success rate in [5%, 30%] with explanation → WARNING
- [x] NOT Success rate < 5% or > 30% → FAIL

### AC-4: Deliverables
- [x] Code: Evaluation harness (Python + Lean scripts)
- [x] Data: results.csv, summary.json, trace logs (compressed)
- [x] Report: 04_validation.md with findings and gate decision
- [x] Reproducibility: Version pins, setup scripts, Dockerfile

---

## Appendix: Related Documents

- **Experiment Brief**: h-e1/02c_experiment_brief.md
- **Evaluation Protocol**: h-e1/evaluation_protocol.md
- **Implementation Notes**: h-e1/implementation_notes.md
- **Dataset Spec**: h-e1/dataset_spec.yaml
- **Archon Task**: b1cf534c-c7ff-48e5-a432-1d260d9ec129

---

**Approved By**: Phase 3 Implementation Planning  
**Next Phase**: Phase 4 - Coding (Coder-Validator Loop)
