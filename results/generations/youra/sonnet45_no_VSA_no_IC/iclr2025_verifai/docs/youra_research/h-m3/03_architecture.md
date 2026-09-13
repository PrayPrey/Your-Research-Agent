# Architecture Design: H-M3
# Random Mathlib Tactic Sampler

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Phase:** 3 Implementation Planning  
**Type:** MECHANISM (corpus contribution test)

**Applied Patterns:** Weighted RNG sampling, deterministic seeding

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation (no existing proof search to analyze)  
**Analyzed Path:** H-E1 mock test data reviewed  
**Findings:** Reuse H-E1 evaluation infrastructure (miniF2F loader, timeout harness). New prover implementation required.

---

## System Overview

Random tactic sampler testing corpus contribution hypothesis (18-25% success target, Δ=3-10pp vs lean-auto 15.6%).

**Components:**
- `TacticSampler` - Weighted RNG from empirical Mathlib distribution
- `ProofSearch` - Budget-controlled loop (15 evaluations)
- `EvaluationHarness` - Parallel workers, timeout, JSONL logging (reuse H-E1)
- `StatisticalAnalysis` - Wilson CI, z-test comparison

---

## Module Specifications

### TacticSampler (`src/random_sampler.lean`)

**Dependencies:** Lean.StdGen

```lean
namespace RandomMathlib

structure TacticDistribution where
  weights : List (String × Float)  -- Must sum to 1.0

def defaultDistribution : TacticDistribution :=
  { weights := [
      ("simp", 0.35), ("rfl", 0.15), ("intro", 0.08),
      ("apply", 0.07), ("cases", 0.06), ("intros", 0.04),
      ("ring", 0.04), ("induction", 0.04), ("exact", 0.04),
      ("norm_num", 0.03), ("constructor", 0.03), ("linarith", 0.02),
      ("omega", 0.02), ("have", 0.02), ("calc", 0.01)
    ] }

def sampleTactic (dist: TacticDistribution) (rng: StdGen) : String × StdGen

def pickRandomGoal (goals: List MVarId) (rng: StdGen) : MVarId × StdGen

end RandomMathlib
```

---

### ProofSearch (`src/proof_search.lean`)

**Dependencies:** TacticSampler, Lean.Elab.Tactic

```lean
namespace RandomMathlib

structure SearchConfig where
  budget : Nat := 15
  timeout : Nat := 300000  -- milliseconds
  seed : Nat := 0

structure SearchResult where
  proof : Option Proof
  tacticsUsed : Nat
  tacticSequence : List String
  wallTime : Float

def randomProofSearch 
    (goal: MVarId) 
    (config: SearchConfig) 
    : TermElabM SearchResult

end RandomMathlib
```

---

### EvaluationHarness (`src/evaluate.lean`)

**Dependencies:** ProofSearch, Minif2f.Test (H-E1 infrastructure)

```lean
namespace Evaluation

structure ProblemResult where
  problemId : String
  source : String
  outcome : String  -- "solved" | "budget_exhausted" | "timeout" | "error"
  tacticsUsed : Nat
  tacticSequence : List String
  wallTime : Float
  seed : Nat

def evaluateMiniF2F : IO Unit

def writeResultsJSONL (results: List ProblemResult) (path: String) : IO Unit

def wilsonCI (successes: Nat) (total: Nat) (alpha: Float := 0.05) 
    : Float × Float

end Evaluation
```

---

### StatisticalAnalysis (`scripts/analyze_h_m3.py`)

**Dependencies:** scipy, statsmodels, numpy

```python
import json
import numpy as np
from scipy.stats import proportions_ztest
from statsmodels.stats.proportion import proportion_confint

def load_results(jsonl_path: str) -> list[dict]:
    ...

def compute_aggregate_stats(results: list[dict]) -> dict:
    ...

def compare_to_baseline(
    h_m3_solved: int, 
    h_e1_solved: int, 
    total: int = 244
) -> dict:
    ...

def stratify_by_source(results: list[dict]) -> dict:
    ...

def write_aggregate_yaml(stats: dict, path: str):
    ...
```

---

## Data Flow

```
Problem Batch (244)
  └─> Parallel Workers (8)
      └─> For each problem:
          ├─> Seed RNG (problem index)
          ├─> randomProofSearch (budget=15, timeout=300s)
          │   └─> Loop (15 iterations):
          │       ├─> sampleTactic(rng) → tactic_str
          │       ├─> applyTactic(goal) → new_goals
          │       ├─> if empty: SUCCESS
          │       └─> else: pickRandomGoal(new_goals, rng)
          └─> Log result (JSONL)
  └─> Aggregate statistics
      ├─> Success rate + Wilson CI
      ├─> Z-test vs H-E1 baseline
      └─> Failure mode breakdown
```

---

## File Structure

```
h-m3/code/
├── src/
│   ├── random_sampler.lean       # TacticSampler module
│   ├── proof_search.lean         # ProofSearch module
│   └── evaluate.lean              # EvaluationHarness
├── scripts/
│   ├── analyze_h_m3.py            # Statistical post-processing
│   └── evaluate_h_m3.sh           # Shell wrapper (build + run)
├── config/
│   └── tactic_distribution.yaml   # Empirical weights
├── lakefile.lean                  # Lean 4 build config
└── README.md                      # Quick start guide
```

---

## External Dependencies (H-E1 Infrastructure)

### Module Paths (Reused from H-E1)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Minif2f.Test | `import Minif2f.Test` | `h-e1/miniF2F-lean4/Test.lean` (external repo) |
| Timeout Utils | `Lean.runWithTimeout` | Lean stdlib |
| JSONL Logging | Custom (replicate from H-E1) | `src/evaluate.lean` |

**Note:** miniF2F repository already cloned and built in H-E1. Reuse mathlib cache.

---

## Error Handling

### Tactic Application Failures

```lean
try
  let goals' ← evalTacticString tacticStr goal
  if goals'.isEmpty then return (some proof)
  else goal := pickRandomGoal goals' rng
catch e =>
  -- Log failure, continue to next tactic
  continue
```

### Timeout Handling

```lean
match ← runWithTimeout config.timeout (randomProofSearch goal config) with
| some result => return result
| none => return { outcome := "timeout", ... }
```

### Worker Crash Recovery

```lean
-- Parallel evaluation with failure isolation
results ← problems.mapMConcurrent 8 fun problem =>
  try
    evaluateProblem problem
  catch e =>
    return { outcome := "error", errorMsg := e.toString }
```

---

## Reproducibility Strategy

### Deterministic Seeding

**Problem Index → RNG Seed Mapping:**
```lean
def evaluateProblem (problem: Problem) (idx: Nat) : IO ProblemResult := do
  let seed := idx  -- Direct mapping
  let rng := mkStdGen seed
  let config := { budget := 15, timeout := 300000, seed }
  randomProofSearch problem.goal config
```

**Guarantees:**
- Same seed → same tactic sequence
- Same tactic sequence → same proof (deterministic compiler)
- Rerun on any subset reproduces exact results

### Validation Protocol

```bash
# Full run
./evaluate_h_m3.sh > run1.log

# Extract solved IDs
jq -r 'select(.outcome == "solved") | .problemId' h_m3_results.jsonl | sort > solved1.txt

# Rerun 10% subset (24 problems)
head -24 solved1.txt | while read id; do
  lake env lean --run "evaluateSingle $id"
done > rerun.log

# Verify exact match
diff run1.log rerun.log  # Should be empty
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Tactic Distribution Validation | Extract/validate weights from literature, spot-check Mathlib | 6 | Module(2) + Data(1) + Algo(2) + Integration(1) |
| A-2 | TacticSampler Implementation | Weighted RNG, cumulative distribution sampling | 8 | Module(2) + Deps(1) + Algo(3) + Integration(2) |
| A-3 | ProofSearch Loop | Budget control, goal selection, termination logic | 10 | Module(3) + Deps(2) + Algo(3) + Integration(2) |
| A-4 | Evaluation Harness | Parallel workers, timeout, JSONL logging (reuse H-E1) | 9 | Module(2) + Deps(2) + Algo(2) + Integration(3) |
| A-5 | Statistical Analysis | Python post-processing, z-test, stratification | 7 | Module(2) + Deps(1) + Algo(2) + Integration(2) |
| A-6 | Reproducibility Validation | Deterministic seeding test, rerun verification | 5 | Module(1) + Deps(1) + Algo(1) + Integration(2) |

**Total Complexity:** 45  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-2, A-5, A-6]

---

## Design Decisions

### Weighted vs Uniform Sampling

**Choice:** Weighted (empirical Mathlib distribution)  
**Rationale:** Tests corpus contribution claim. Uniform would test pure random search (different hypothesis).

### Goal Selection

**Choice:** Random  
**Rationale:** Simplest strategy. Human proofs use semantic ordering, so random provides conservative lower bound on corpus benefit.

### Tactic Budget

**Choice:** 15 evaluations  
**Rationale:** H-E1 measured mean=9.2±4.1. Budget of 15 = mean + 1.4σ (covers 90% of lean-auto distribution).

### Premise Selection

**Choice:** None (zero-shot)  
**Rationale:** Matches H-E1 baseline. Isolates tactic frequency effect without retrieval confound.

---

## Implementation Constraints

### Performance Targets

- **Total runtime:** <3h wall-clock (244 problems, 8 workers, 300s timeout)
- **Per-problem timeout:** 300s (matches H-E1)
- **Memory:** 16GB per worker

### Quality Gates

- **Error rate:** <5% (infrastructure stable from H-E1)
- **Reproducibility:** 100% match on 10% rerun subset
- **Statistical power:** n=244 gives ±6.3% CI at 20% success rate

---

## Validation Criteria

### PASS Conditions (SHOULD_WORK Gate)

1. Success rate ∈ [18%, 25%]
2. Δ vs lean-auto ∈ [3%, 10%] percentage points
3. p < 0.05 (one-sided z-test)

### FAIL Conditions

1. Success rate < 15% (no corpus benefit)
2. Success rate > 30% (corpus contribution >> predicted)
3. p ≥ 0.05 (not statistically significant)

---

## Deliverables

### Code Artifacts
- `src/random_sampler.lean` (TacticSampler)
- `src/proof_search.lean` (ProofSearch)
- `src/evaluate.lean` (EvaluationHarness)
- `scripts/analyze_h_m3.py` (StatisticalAnalysis)
- `scripts/evaluate_h_m3.sh` (Shell wrapper)
- `config/tactic_distribution.yaml` (Empirical weights)

### Data Artifacts
- `h_m3_results.jsonl` (244 per-problem results)
- `h_m3_aggregate.yaml` (Success rate, CI, Δ, p-value)
- `h_m3_stratification.csv` (Optional: by AMC/AIME/IMO)

### Documentation
- `04_validation.md` (Phase 4 validation report)
- `comparison_analysis.ipynb` (Visualization)

---

## Timeline

**Total Duration:** 4 days

| Day | Tasks | Hours |
|-----|-------|-------|
| 1 | A-1 (tactic distribution) | 4h |
| 2 | A-2, A-3 (sampler + search) | 6h |
| 3 | A-4, A-6 (evaluation + validation) | 6h |
| 4 | A-5 (statistical analysis) | 4h |

**Parallel Work:** Independent of H-M1, H-M2 (can run concurrently)

---

**Architecture Complete — Ready for Phase 4 Implementation**
