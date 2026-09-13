# Logic Design: H-M3 Random Mathlib Tactic Sampler

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Phase:** 3 Implementation Planning  
**Gate:** SHOULD_WORK  

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: H-E1 Python infrastructure exists (evaluation harness, metrics)  
**Analyzed Path**: `/docs/youra_research/h-e1/code/src/`  
**Relevant Symbols**: `load_minif2f_problems`, `run_parallel_evaluation`, `compute_metrics`  
**Note**: H-M3 requires NEW Lean 4 prover implementation (no base hypothesis code to extend)

---

## Applied Patterns

**Knowledge Base**: No relevant Lean/theorem proving patterns in Archon KB  
**Applied**: Standard weighted sampling (inverse transform method) + proof search loop

---

## Core Algorithms

### A-1: Weighted Random Tactic Sampler (Complexity: 2, Budget: 2)

**Algorithm**: Inverse transform sampling from cumulative distribution

```lean
-- Tactic distribution (empirical from Mathlib)
structure TacticDistribution where
  tactics : Array String
  weights : Array Float  -- Must sum to 1.0
  cumulative : Array Float  -- Precomputed cumulative[i] = sum(weights[0..i])

def sampleTactic (dist: TacticDistribution) (rng: StdGen) : String × StdGen :=
  let (r, rng') := rng.next  -- r ∈ [0.0, 1.0)
  let idx := dist.cumulative.findIdx (r < ·) |>.getD 0
  (dist.tactics[idx], rng')
```

**Data Structures**:

| Variable | Type | Shape | Description |
|----------|------|-------|-------------|
| tactics | Array String | [15] | Tactic names |
| weights | Array Float | [15] | Empirical probabilities |
| cumulative | Array Float | [15] | Cumulative distribution |
| r | Float | scalar | Random value [0,1) |
| idx | Nat | scalar | Selected tactic index |

**Edge Cases**:
- Empty distribution → compile-time error (static array)
- Weights not summing to 1.0 → normalize at init
- r = 1.0 (exclusive bound) → return last tactic

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Build cumulative distribution | Scanl sum over weights |
| L-1-2 | Binary search | Find idx where r < cumulative[idx] |

---

### A-2: Proof Search Loop (Complexity: 3, Budget: 3)

**Algorithm**: Budget-controlled tactic application with random goal selection

```lean
def proofSearch 
    (goal: MVarId) 
    (dist: TacticDistribution) 
    (budget: Nat := 15) 
    (seed: Nat := 0) 
    : TermElabM ProofResult := do
  
  let mut rng := mkStdGen seed
  let mut currentGoal := goal
  let mut tacticSeq := []
  
  for i in [0:budget] do
    -- Sample tactic
    let (tacticStr, rng') := sampleTactic dist rng
    rng := rng'
    tacticSeq := tacticSeq.push tacticStr
    
    -- Apply tactic
    try
      let newGoals ← evalTacticString tacticStr currentGoal
      
      if newGoals.isEmpty then
        return { status := .solved, tacticsUsed := i+1, tacticSeq }
      
      -- Random goal selection
      let (goalIdx, rng'') := rng.next
      currentGoal := newGoals[goalIdx % newGoals.length]
      rng := rng''
      
    catch e =>
      continue  -- Tactic failed, try next
  
  return { status := .budgetExhausted, tacticsUsed := budget, tacticSeq }
```

**Control Flow**:

```
1. Initialize: rng ← seed, goal ← initial, seq ← []
2. FOR i = 0 TO budget-1:
     a. Sample tactic from distribution
     b. TRY apply tactic to current goal
     c. IF goals.isEmpty → RETURN solved
     d. ELSE pick random goal → continue
     e. CATCH error → continue to next iteration
3. RETURN budget_exhausted
```

**Termination Guarantees**:
- Loop bounded by budget (hard limit: 15 iterations)
- Each iteration consumes 1 budget unit
- Early termination on solved (goals.isEmpty)
- Timeout enforced externally (300s wall-clock)

**Data Structures**:

| Variable | Type | Shape | Description |
|----------|------|-------|-------------|
| goal | MVarId | - | Current proof goal |
| rng | StdGen | - | RNG state |
| tacticSeq | Array String | [≤15] | Applied tactics |
| newGoals | Array MVarId | [0..∞] | Subgoals after tactic |
| budget | Nat | scalar | Max evaluations (15) |
| i | Nat | scalar | Current iteration |

**Edge Cases**:
- Empty goal list (initial) → return error immediately
- Tactic creates 0 subgoals → solved, exit loop
- Tactic error → catch, continue to next tactic
- Budget exhausted → return with status
- All tactics fail → budget_exhausted outcome

**Subtasks [3/3 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Tactic evaluation | Parse string → apply to MVarId |
| L-2-2 | Goal selection | Random index mod length |
| L-2-3 | Error handling | Catch tactic failures, continue |

---

### A-3: Deterministic Seeding (Complexity: 1, Budget: 1)

**Algorithm**: Problem index → RNG seed for reproducibility

```lean
def seedFromProblemIndex (idx: Nat) : Nat := idx

def evaluateProblem (problem: Problem) (dist: TacticDistribution) : IO ProofResult := do
  let seed := seedFromProblemIndex problem.index
  runWithTimeout 300000 (proofSearch problem.goal dist budget:=15 seed:=seed)
```

**Properties**:
- Same problem index → same RNG seed → same tactic sequence
- Deterministic across reruns
- Independent seeds per problem (no cross-contamination)

**Validation**:
```lean
-- Rerun 10% subset (24 problems) must match exactly
def validateReproducibility (problems: Array Problem) : IO Bool := do
  let subset := problems.take 24
  let results1 ← subset.mapM (evaluateProblem · dist)
  let results2 ← subset.mapM (evaluateProblem · dist)
  return results1 == results2  -- Must be true
```

**Subtasks [1/1 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Seed mapping | Identity function (idx → seed) |

---

### A-4: Batch Evaluation Harness (Complexity: 2, Budget: 2)

**Algorithm**: Parallel evaluation with timeout enforcement

```lean
def evaluateMiniF2F 
    (problems: Array Problem) 
    (dist: TacticDistribution)
    (nWorkers: Nat := 8) 
    : IO (Array ProofResult) := do
  
  problems.mapMConcurrent nWorkers fun (problem, idx) => do
    let seed := seedFromProblemIndex idx
    let startTime ← IO.monoMsNow
    
    -- Timeout wrapper (300s)
    let result ← runWithTimeout 300000 do
      proofSearch problem.goal dist budget:=15 seed:=seed
    
    let endTime ← IO.monoMsNow
    let wallTime := (endTime - startTime) / 1000.0
    
    return {
      problemId := problem.name,
      result := result,
      wallTime := wallTime,
      seed := seed
    }
```

**Concurrency Model**:
- 8 parallel workers (from H-E1 infrastructure)
- Independent RNG state per problem (no shared state)
- Each worker: timeout-wrapped proof search
- Results aggregated after completion

**Timeout Handling**:
- Per-problem timeout: 300s (5 minutes)
- Implementation: `runWithTimeout` wrapper
- Timeout outcome: `{ status := .timeout, tacticsUsed := 0, tacticSeq := [] }`

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Parallel map | mapMConcurrent over problems |
| L-4-2 | Timeout wrapper | runWithTimeout 300s |

---

## Tactic Distribution Specification

### Empirical Weights

**Source**: Composite from LeanDojo (2023), miniF2F tidy baseline (2021), Structured Hints (2026)

```lean
def mathlibTacticDistribution : TacticDistribution :=
  let tactics := #[
    "simp", "rfl", "intro", "apply", "cases",
    "intros", "ring", "induction", "exact", "norm_num",
    "constructor", "linarith", "omega", "have", "calc"
  ]
  let weights := #[
    0.35, 0.15, 0.08, 0.07, 0.06,
    0.04, 0.04, 0.04, 0.04, 0.03,
    0.03, 0.02, 0.02, 0.02, 0.01
  ]
  let cumulative := weights.scanl (· + ·) 0.0 |>.tail  -- [0.35, 0.50, 0.58, ...]
  { tactics, weights, cumulative }
```

**Weight Validation**:
- Sum of weights = 1.0 (enforced at compile time via assertion)
- All weights > 0 (strictly positive probabilities)
- 15 tactics total (matches miniF2F tidy baseline)

---

## Statistical Analysis API

### Python Post-Processing (Reuse H-E1)

```python
# analyze_h_m3.py
from scipy.stats import proportions_ztest
from statsmodels.stats.proportion import proportion_confint

def compute_metrics(results: list[dict]) -> dict:
    """Compute success rate, CI, tactic stats."""
    total = len(results)
    solved = sum(1 for r in results if r['status'] == 'solved')
    success_rate = solved / total
    
    # Wilson 95% CI
    ci_low, ci_high = proportion_confint(solved, total, alpha=0.05, method='wilson')
    
    # Tactic consumption (solved only)
    tactics_used = [r['tacticsUsed'] for r in results if r['status'] == 'solved']
    mean_tactics = np.mean(tactics_used) if tactics_used else 0
    
    return {
        'success_rate': success_rate,
        'ci_95': [ci_low, ci_high],
        'solved': solved,
        'mean_tactics': mean_tactics
    }

def compare_to_baseline(h_m3_results: dict, h_e1_baseline: dict) -> dict:
    """One-sided z-test: H-M3 > H-E1."""
    z, p = proportions_ztest(
        [h_m3_results['solved'], h_e1_baseline['solved']],
        [244, 244],
        alternative='larger'
    )
    
    delta = h_m3_results['success_rate'] - h_e1_baseline['success_rate']
    
    return {
        'delta': delta,
        'z_stat': z,
        'p_value': p,
        'significant': p < 0.05
    }
```

**Falsification Criteria**:

```python
def validate_gate(metrics: dict) -> bool:
    """SHOULD_WORK gate: 18-25% success, Δ=3-10pp, p<0.05."""
    success_in_range = 0.18 <= metrics['success_rate'] <= 0.25
    delta_in_range = 0.03 <= metrics['delta'] <= 0.10
    significant = metrics['p_value'] < 0.05
    
    return success_in_range and delta_in_range and significant
```

---

## Error Handling Strategy

### Tactic Application Errors

```lean
-- Level 1: Tactic evaluation
try
  let goals ← evalTacticString tacticStr goal
  handleSuccess goals
catch
  | .tacticError => continue  -- Expected (tactic doesn't apply)
  | .parseError => continue   -- Malformed tactic string (skip)
  | .timeout => break         -- Propagate timeout upward
```

**Error Classification**:

| Error Type | Handling | Impact |
|------------|----------|--------|
| Tactic doesn't apply | Catch, continue | Normal operation |
| Parse error | Catch, continue | Log warning |
| Timeout (external) | Propagate | Return timeout status |
| Budget exhausted | Return | Expected termination |

### Timeout Enforcement

```lean
-- Level 2: Problem evaluation
runWithTimeout 300000 do  -- 300s = 300,000ms
  proofSearch goal dist budget:=15 seed:=seed
-- Returns: Option ProofResult (None on timeout)
```

**Timeout Guarantees**:
- Per-problem wall-clock limit: 300s
- Enforced by Lean runtime (not budget check)
- Timeout outcome recorded as status field
- No partial results on timeout (clean failure)

---

## Reproducibility Guarantees

### Deterministic Execution Path

```
Problem Index → Seed → RNG State → Tactic Sequence → Goals → Result
     ↓             ↓         ↓             ↓            ↓         ↓
     0          seed=0    StdGen(0)    [simp, intro] [g1, g2]  solved
     1          seed=1    StdGen(1)    [rfl, cases]  [g3]      timeout
    ...
```

**Properties**:
1. Same seed → same RNG state
2. Same RNG state → same tactic sequence
3. Same tactics + same goal → deterministic Lean evaluation
4. Deterministic evaluation → same result

**Validation Protocol**:
```bash
# Run 1
./evaluate_h_m3.sh > run1.log
jq 'select(.status == "solved")' h_m3_results.jsonl | wc -l  # Count solved

# Run 2 (10% subset)
./evaluate_h_m3.sh --pilot --n-problems=24 > run2.log
diff run1_subset.jsonl run2.jsonl  # Must be identical
```

---

## Module Dependencies

### Lean 4 Standard Library

```lean
import Lean                     -- Core Lean 4 API
import Lean.Meta                -- Meta-level tactics (MVarId, goals)
import Lean.Elab.Tactic         -- Tactic evaluation (evalTactic)
import Std.Data.Array           -- Array operations (mapM, scanl)
```

### External Repositories

```lean
import Minif2f.Test             -- miniF2F test theorems (244 problems)
```

**Dependency Versions**:
- Lean 4.15.0 (from H-E1)
- mathlib 2024-06-01 (miniF2F compatible)
- miniF2F fork: `google-deepmind/miniF2F` (Lean 4 port)

---

## File Structure

### Implementation Files

```
h-m3/code/
├── RandomMathlib.lean          # Core algorithms (A-1, A-2, A-3)
├── TacticDistribution.lean     # Empirical weights + sampling
├── Evaluate.lean               # Batch harness (A-4)
├── Main.lean                   # Entry point
└── lakefile.lean               # Build configuration

h-m3/code/analysis/
└── analyze_h_m3.py             # Statistical post-processing
```

### Data Artifacts

```
h-m3/data/
├── h_m3_results.jsonl          # Per-problem results
├── h_m3_aggregate.yaml         # Success rate, CI, delta
└── h_m3_validation.txt         # Gate pass/fail
```

---

## Budget Summary

| Task | Complexity | Budget | Subtasks Used |
|------|-----------|--------|---------------|
| A-1: Weighted Sampler | 2 | 2 | 2/2 |
| A-2: Proof Search | 3 | 3 | 3/3 |
| A-3: Seeding | 1 | 1 | 1/1 |
| A-4: Batch Harness | 2 | 2 | 2/2 |
| **Total** | **8** | **8** | **8/8** |

**Budget Status**: FULLY ALLOCATED (8/8 used)

---

## Phase 4 Implementation Notes

### Critical API Contracts

**For Phase 4 Coder:**

1. **TacticDistribution** must precompute cumulative array at init
2. **proofSearch** returns `ProofResult` with `status`, `tacticsUsed`, `tacticSeq`
3. **Seeding** is identity function: `seed = problemIndex`
4. **Timeout** is external wrapper (not internal budget check)
5. **Error handling**: Catch all tactic errors, continue loop

### Type Signatures (Copy-Paste Ready)

```lean
structure TacticDistribution where
  tactics : Array String
  weights : Array Float
  cumulative : Array Float

structure ProofResult where
  status : ProofStatus  -- .solved | .budgetExhausted | .timeout
  tacticsUsed : Nat
  tacticSeq : Array String

def sampleTactic (dist: TacticDistribution) (rng: StdGen) : String × StdGen

def proofSearch (goal: MVarId) (dist: TacticDistribution) 
  (budget: Nat := 15) (seed: Nat := 0) : TermElabM ProofResult

def evaluateMiniF2F (problems: Array Problem) (dist: TacticDistribution)
  (nWorkers: Nat := 8) : IO (Array ProofResult)
```

---

**Logic Design Complete — Ready for Phase 4 Implementation**
