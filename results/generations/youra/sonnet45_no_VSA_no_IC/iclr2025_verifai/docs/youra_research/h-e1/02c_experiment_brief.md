# Experiment Design: H-E1

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Pure automated prover (lean-auto) achieves 10-25% baseline success on miniF2F Lean 4 subset
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE (Phase 2C)
**Prerequisites Satisfied:** N/A (first hypothesis, no prerequisites)
**Gate Status:** MUST_WORK (foundation for all comparisons)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (independent measurement)

### Gate Condition
**MUST_WORK** — If lean-auto baseline cannot be established (fail, timeout >80%, or success rate outside 5-30% range indicating infrastructure issue), then:
- Block H-M3 (needs lean-auto baseline for Δ comparison)
- Block H-C1 (needs tactic count measurement)
- STOP workflow for investigation

---

## Continuation Context

**Not Applicable** — H-E1 is the first hypothesis in execution order.

### Previous Hypothesis Results (if applicable)
None

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**No relevant results** — Archon KB does not contain Lean/theorem proving domain content. All implementation guidance from Exa GitHub search.

### Archon Code Examples

**No relevant results** — Archon KB focused on ML/DL libraries, not formal mathematics.

### Exa GitHub Implementations

**Repository 1**: leanprover-community/lean-auto (⭐164)
- **URL**: https://github.com/leanprover-community/lean-auto
- **Relevance**: Official lean-auto implementation (automated theorem prover interface for Lean 4)
- **Key Features**:
  - Interface between Lean 4 and automated theorem provers (SMT, TPTP)
  - Monomorphization from dependent type theory to higher-order logic
  - Proof reconstruction via Duper (superposition prover)
  - Active development, Apache 2.0 license
- **Installation**:
  ```bash
  # Add to lakefile.lean
  require auto from git "https://github.com/leanprover-community/lean-auto"
  
  # In Lean file
  import Auto.Tactic
  set_option auto.smt true  -- Enable SMT mode
  set_option auto.smt.solver.name "z3"
  ```
- **Usage**:
  ```lean
  theorem example_name : statement := by auto
  ```
- **Configuration Options**:
  - `auto.smt`: Enable SMT solver (default: false)
  - `auto.native`: Enable native prover (default: false)  
  - `auto.smt.timeout`: Timeout in seconds

**Repository 2**: google-deepmind/miniF2F (⭐14)
- **URL**: https://github.com/google-deepmind/miniF2F
- **Relevance**: Official miniF2F Lean 4 fork (AlphaProof evaluation benchmark)
- **Key Features**:
  - 500 theorem declarations (244 test + 256 validation, 12 variants excluded → 488 base problems)
  - Corrected formalizations vs original OpenAI version
  - Natural language docstrings from AoPS/MATH dataset
  - All problems import Mathlib
- **Installation**:
  ```bash
  git clone https://github.com/google-deepmind/miniF2F
  cd miniF2F
  lake exe cache get
  lake build
  ```
- **Dataset Structure**:
  - `Minif2f/Test.lean`: 244 test theorems
  - `Minif2f/Valid.lean`: 244 validation theorems (12 variants excluded)
  - Each theorem: `theorem <name> : <statement> := by sorry`

**Repository 3**: yangky11/miniF2F-lean4 (⭐75)
- **URL**: https://github.com/yangky11/miniF2F-lean4
- **Relevance**: Alternative Lean 4 port (older, less maintained)
- **Note**: Google DeepMind fork is preferred (used by AlphaProof)

**Repository 4**: namin/LeanDisco (TestBench_SMTAuto.lean)
- **URL**: https://github.com/namin/LeanDisco
- **Relevance**: Benchmark infrastructure for evaluating lean-auto on miniF2F
- **Key Code**: Automated prover evaluation loop
  ```lean
  set_option auto.smt true
  set_option auto.smt.trust true
  set_option auto.smt.solver.name "z3"
  set_option auto.smt.timeout 2
  
  def attemptAutoProofSMT (name : Name) (type : Expr) : TermElabM Bool := do
    let mvar ← mkFreshExprMVar type
    let goal := mvar.mvarId!
    try
      let remainingGoals ← Tactic.run goal do
        evalTactic (← `(tactic| auto))
      if remainingGoals.isEmpty then
        IO.println s!"✓ PROVED by auto (SMT): {name}"
        return true
    catch e => return false
  ```

### 🎯 Implementation Priority Assessment

**No paper reproduction** — This is a baseline measurement experiment, not reproducing a specific paper method.

**Recommended Implementation Path:**
- **Primary**: lean-auto (leanprover-community/lean-auto) + miniF2F (google-deepmind/miniF2F)
- **Fallback**: Manual tactic application (rfl, simp, ring, decide) if lean-auto unavailable
- **Justification**: 
  - lean-auto is the standard automated prover for Lean 4
  - google-deepmind/miniF2F is the AlphaProof evaluation version (most authoritative)
  - Combination provides reproducible baseline for H-E1

### Code Analysis (Serena MCP)

**Not performed** — Theorem proving infrastructure code is clear from documentation. Serena analysis not needed.

---

## Experiment Specification

### Dataset

**Name**: miniF2F Lean 4 Benchmark
**Source**: google-deepmind/miniF2F (AlphaProof evaluation version)
**Type**: Standard (formal mathematics olympiad problems)
**Size**: 488 base problems (244 test + 244 validation, excluding 12 variants)
**Splits**: 
- Test: 244 theorems (held-out evaluation)
- Validation: 244 theorems (hyperparameter tuning)

**Problem Domains**:
- AMC (American Mathematics Competitions)
- AIME (American Invitational Mathematics Examination)
- IMO (International Mathematical Olympiad)
- High-school and undergraduate mathematics

**Formalization Quality**:
- Corrected vs OpenAI original (fewer misformalizations)
- Natural language docstrings from AoPS/MATH dataset
- All statements import Mathlib (Lean 4 standard library)

**For This Experiment (H-E1)**:
- **Subset**: Use problems where N ≥ 50 (pilot: start with validation split N=20, then scale to N ≥ 50 from test split)
- **Selection Criteria**: All solvable problems (no filtering by difficulty)
- **Expected Size**: 50-100 problems (depends on subset definition)

**Loading Information** (for Phase 4 download):
- Method: Git clone + Lake build
- Identifier: google-deepmind/miniF2F @ main branch
- Code:
  ```bash
  git clone https://github.com/google-deepmind/miniF2F
  cd miniF2F
  lake exe cache get  # Download Mathlib cache
  lake build           # Compile all theorems
  ```

### Models

#### Baseline Prover

**Name**: lean-auto (Automated Theorem Prover Interface)
**Source**: leanprover-community/lean-auto
**Type**: Automated theorem prover for Lean 4 (hammer-style automation)
**License**: Apache 2.0

**Architecture**:
- Monomorphization: Dependent type theory → Higher-order logic
- Backend Solvers: SMT (Z3, CVC5), TPTP (Zipperposition)
- Proof Reconstruction: Duper (superposition prover in Lean)

**Configuration for H-E1 Baseline**:
- Solver: Z3 (SMT)
- Mode: `auto.smt` (with proof reconstruction disabled for speed)
- Timeout: 300s per problem
- Tactic budget: 10 tactic evaluations (measured from this run, feeds into H-C1)

**Loading Information** (for Phase 4 download):
- Method: Lake dependency in lakefile.lean
- Identifier: leanprover-community/lean-auto @ latest release
- Code:
  ```lean
  -- In lakefile.lean
  require auto from git "https://github.com/leanprover-community/lean-auto"
  
  -- In experiment file
  import Auto.Tactic
  
  set_option auto.smt true
  set_option auto.smt.solver.name "z3"
  set_option auto.smt.timeout 300
  ```

#### Proposed Prover

**For H-E1 (EXISTENCE hypothesis):** Same as baseline — this IS the baseline measurement.

**Purpose**: Establish lean-auto success rate (predicted 10-25%) for comparison with:
- H-M1, H-M2: LLM-guided provers (LeanCopilot)
- H-M3: Random Mathlib corpus sampling

### Training Protocol

**Not Applicable** — Theorem proving has no training phase.

**Evaluation Protocol** (replaces training):

**Prover Configuration**:
- Solver: Z3 (SMT backend via lean-auto)
- Timeout: 300 seconds per problem
- Memory limit: System default
- Parallelization: Sequential (one problem at a time)

**Tactic Budget Measurement**:
- Log tactic evaluation count per problem
- Compute mean ± std across all solved problems
- **Purpose**: Establishes fair comparison metric for H-C1 (tactic budget equalization)
- **Output**: Mean tactic count (target: ~10 evaluations as Phase 2B prediction)

**Pilot Protocol** (Phase 4 Step 1):
- N=20 problems from validation split
- Verify lean-auto/miniF2F/Mathlib compatibility
- Check: No environment errors, Z3 connection works, timeout handling correct
- If pilot fails: Debug setup before full run

**Full Evaluation** (Phase 4 Step 2):
- N ≥ 50 problems from test split
- Run each problem with lean-auto + timeout
- Record: solved/unsolved, tactic count (if solved), timeout/error type (if failed)

### Evaluation

**Primary Metric**: Success Rate (%)
- **Formula**: (# solved problems) / (# total problems) × 100
- **Gate Target**: 10-25% (from Phase 2B hypothesis statement)
- **PoC Success**: Any rate in 10-25% range

**Secondary Metrics**:
- **Tactic Count** (per solved problem): Mean ± Std
  - Used by H-C1 to set LLM tactic budget
- **Timeout Rate** (%): (# timeout) / (# total) × 100
- **Error Rate** (%): (# errors) / (# total) × 100

**Logging Requirements**:
```python
# Per-problem log
{
  "theorem_name": str,
  "status": "solved" | "timeout" | "error",
  "tactics_used": int | null,  # null if not solved
  "time_seconds": float,
  "error_type": str | null
}
```

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Automated theorem proving (success/failure classification)
- Library: Custom (Lean 4 metaprogramming + Python logging)
- Code:
  ```python
  # Python evaluation script
  import json
  
  def compute_metrics(results: list[dict]) -> dict:
      total = len(results)
      solved = sum(1 for r in results if r["status"] == "solved")
      timeout = sum(1 for r in results if r["status"] == "timeout")
      errors = sum(1 for r in results if r["status"] == "error")
      
      tactic_counts = [r["tactics_used"] for r in results if r["tactics_used"] is not None]
      
      return {
          "success_rate_pct": 100 * solved / total,
          "timeout_rate_pct": 100 * timeout / total,
          "error_rate_pct": 100 * errors / total,
          "mean_tactics": np.mean(tactic_counts) if tactic_counts else None,
          "std_tactics": np.std(tactic_counts) if tactic_counts else None,
          "total_problems": total,
          "solved_problems": solved
      }
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target range (10-25%) vs actual success rate
  - Bar chart: [Target Min | Target Max | Actual]
  - Color: Green if in range, Red if outside

#### Additional Figures (LLM Autonomous)
- **Problem-level Results**: Heatmap showing solved/timeout/error per problem
- **Tactic Count Distribution**: Histogram of tactic counts for solved problems
- **Time vs Tactic Count**: Scatter plot showing relationship

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Primary References

**lean-auto (Automated Prover)**
- Repository: https://github.com/leanprover-community/lean-auto
- Paper: https://arxiv.org/abs/2505.14929 (Lean-auto: An Interface between Lean 4 and Automated Theorem Provers)
- Stars: 164
- License: Apache 2.0
- Installation: `require auto from git "https://github.com/leanprover-community/lean-auto"`

**miniF2F Lean 4 (Benchmark)**
- Repository: https://github.com/google-deepmind/miniF2F
- Paper: https://arxiv.org/abs/2109.00110 (MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics)
- Stars: 14 (AlphaProof evaluation version)
- License: Apache 2.0
- Installation: `git clone + lake build`

### Secondary References

**LeanDisco Benchmarking Infrastructure**
- Repository: https://github.com/namin/LeanDisco (TestBench_SMTAuto.lean)
- Purpose: Automated prover evaluation loop example
- Code pattern: TermElabM-based proof attempt with timeout handling

**miniF2F-v2 (Corrected Benchmark)**
- Repository: https://github.com/roozbeh-yz/miniF2F_v2
- Paper: https://arxiv.org/abs/2511.03108 (miniF2F-Lean Revisited)
- Note: Fixes 16 unprovable statements in original; consider for future work

**VERITAS (MCTS Prover)**
- Repository: https://github.com/manishacharya60/veritas
- Baseline Results: Best-of-1 Claude: 29.5% on miniF2F (244 problems)
- Note: Shows LLM-guided baseline for comparison in H-M1/H-M2

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate in ```state block)
**Date:** 2026-08-20T04:00:00Z

### Workflow History for This Hypothesis
- 2026-08-20T03:44:54Z: H-E1 set to IN_PROGRESS (hypothesis loop start)
- 2026-08-20T03:52:00Z: Experiment design (Phase 2C) completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
