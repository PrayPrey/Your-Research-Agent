# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: gap1
- **Gap Title**: Scalable SMT-Guided Feedback Loop for LLM Code Refinement
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met at exchange 15 - clear hypothesis with testable predictions, scoped to typed languages, mechanism well-defined, objections addressed

### Key Insights
- **Decoupling contributions**: Separating incremental SMT verification (H1, testable now) from neural constraint extraction (H2, future work) enabled immediate feasibility
- **Typed language scoping**: Constraining to statically-typed languages (Rust, typed Python with Pydantic) resolves static analysis reliability concerns
- **Repair locality**: Program repair literature establishes that 80%+ of repairs modify 1-3 lines, ensuring small invalidation cones for speedup
- **Conservative dependency analysis**: Over-approximation strategy maintains soundness while achieving practical speedup

### Breakthrough Moments
- **Exchange 3**: Dr. Sage identified two conflated contributions (assertion generation vs incremental verification), leading to focus on H1
- **Exchange 9**: Dr. Sage recommended decoupling neural extraction (H2) from incremental SMT (H1), enabling immediate testing of H1
- **Exchange 10**: Prof. Pax confirmed technical feasibility with existing tools (Z3, Prusti, Pyre)
- **Exchange 11**: Dr. Ally synthesized complete hypothesis with 3 testable predictions and clear mechanism

---

## Final Hypothesis

### Title
Incremental SMT Verification for LLM Code Repair

### Core Claim
Under iterative LLM code repair workflows in statically-typed languages, if incremental SMT verification is used (re-verifying only modified functions + dependencies), then verification time reduces by 2-5x compared to batch re-verification, because unchanged code portions skip redundant constraint checking.

### Mechanism
**Causal Chain (3 steps)**:
1. **Typed code → constraint extraction**: LLM generates typed code (Rust, typed Python) → static analyzer (Prusti, Pyre) extracts SMT constraints from type signatures and annotations
2. **Incremental SMT identifies invalidation**: Z3 uses dependency analysis to determine which constraints invalidate after code modification
3. **Selective re-verification → speedup**: Only modified functions + dependency cone re-verified → unchanged code skipped → wall-clock time reduced

**Key Tension**: Speedup magnitude depends on repair locality vs dependency spread. LLM code may have broader dependencies than human code, limiting speedup.

---

## Predictions

### P1 (Primary): Wall-Clock Speedup
**Statement**: Incremental SMT verification achieves 2-5x wall-clock speedup vs batch on repair workflows

**Test Method**: Generate 100 programs (10-50 LOC) in typed Python with Pydantic, induce 1-2 errors per program, LLM repairs, measure batch vs incremental verification time

**Success Criterion**: Median speedup ≥ 2x, 75th percentile ≥ 3x

**Falsification**: Median speedup < 1.5x indicates no practical benefit

### P2: Speedup Scaling
**Statement**: Speedup increases with codebase size (larger programs → higher % unchanged code)

**Test Method**: Stratify programs by LOC (10-50, 50-100, 100-500), measure speedup in each bin

**Success Criterion**: Positive correlation (100 LOC = 2x, 500 LOC ≥ 5x)

**Falsification**: No correlation or negative correlation

### P3: Soundness Guarantee
**Statement**: Conservative dependency analysis maintains soundness (zero false negatives)

**Test Method**: Seed verification errors in dependency-connected code, check if incremental approach catches all errors

**Success Criterion**: 100% error detection

**Falsification**: Any missed errors indicate unsound verification

---

## Novelty

**Preserved Novelty**: First application of incremental SMT verification to neural code generation repair workflows

**Key Innovation**: Combining established techniques (incremental SMT + typed LLM code) in new configuration to solve LLM verification scalability bottleneck

**Differentiation from Prior Work**:
- **Angelix, Prophet** (SMT-guided repair for human code) → We scale to LLM-generated full programs with typed constraints
- **AlphaCode, CodeT5** (neural code generation) → We add SMT-based correctness guarantees
- **Prusti, Pyre** (static analyzers for typed languages) → We integrate with LLM repair loop + incremental SMT

---

## Experimental Design

**Dataset**: HumanEval extended with Pydantic type annotations (100 programs, 10-50 LOC)

**Models**: GPT-4 or Claude Sonnet 3.5 (code generation LLMs)

**Baselines**:
1. Batch SMT verification (re-verify entire program on each iteration using Z3)
2. No verification (test-suite-only validation)

**Measurement Plan**:
1. Generate typed Python code using LLM
2. Induce 1-2 type/logic errors per program
3. LLM repairs errors based on static analysis feedback
4. Measure verification time: (A) batch re-verification, (B) incremental re-verification
5. Compute speedup factor = time(batch) / time(incremental)

---

## Limitations

### Scope Boundaries
**Applies to**:
- Statically-typed languages (Rust, typed Python with Pydantic)
- Iterative repair workflows (not general generation from scratch)
- Programs 10-500 LOC
- Code modifications touching 1-3 functions per iteration

**Does NOT apply to**:
- Dynamic languages without type annotations (JavaScript, Ruby)
- Full program generation from scratch
- Code using heavy dynamic features (eval, exec, reflection, metaprogramming)
- Massive refactorings restructuring entire codebase

### Known Limitations
1. **Cold start problem** (Exchange 12): First iteration sees no speedup - mitigated by cross-program constraint caching (P4 future work)
2. **Dependency spread** (Exchange 4): If modifications touch 50-70% of code, speedup minimal
3. **Static analysis incompleteness**: Constraints may be incomplete (sound but not complete verification)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Converged at exchange 15 after scoping to typed languages and decoupling H1 (incremental SMT) from H2 (neural extraction) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Cold start problem (mitigated by P4 caching), dependency graph accuracy (mitigated by conservative over-approximation) |

---

## Phase 2B Readiness

**Status**: READY

**SH1 (Existence)**: Typed LLM code with extractable constraints must exist (static analyzers work on type annotations)

**SH2 (Mechanism)**: Incremental SMT re-verification skips unchanged code → reduced verification time

**SH3 (Comparison)**: Compare against batch SMT (baseline 1) and test-only validation (baseline 2)

**Open Questions**:
- What is actual iteration count distribution for LLM repair in practice? (affects cold start impact)
- Can cross-program constraint caching (P4) further improve first-iteration speedup?
- Does embedding-based retrieval cache (H2 future work) provide additional speedup?

---

*Phase 2A Complete - Ready for Phase 2B Research Planning*
