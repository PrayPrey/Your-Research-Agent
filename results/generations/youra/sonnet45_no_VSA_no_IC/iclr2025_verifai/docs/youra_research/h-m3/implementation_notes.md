# Implementation Notes: H-M3
# Random Mathlib Tactic Sampling Baseline

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Implementation Level:** 1.5 (Pseudo-code + Concrete specifications)

---

## Core Design

### Prover Architecture

```
┌─────────────────────────────────────────────────┐
│  Random Mathlib Tactic Sampler                  │
│                                                 │
│  ┌──────────────┐    ┌─────────────────────┐  │
│  │ Tactic       │───▶│ Weighted Random     │  │
│  │ Distribution │    │ Sampler             │  │
│  │ (empirical)  │    │ (seeded RNG)        │  │
│  └──────────────┘    └─────────────────────┘  │
│         │                      │               │
│         ▼                      ▼               │
│  ┌──────────────────────────────────────────┐  │
│  │ Proof Search Loop                        │  │
│  │  for i in 1..budget:                     │  │
│  │    tactic ← sample()                     │  │
│  │    result ← apply(tactic, goal)          │  │
│  │    if solved: return proof               │  │
│  │    else: goal ← pickRandom(subgoals)     │  │
│  └──────────────────────────────────────────┘  │
│                      │                         │
│                      ▼                         │
│  ┌──────────────────────────────────────────┐  │
│  │ Lean 4 Compiler (verification)           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Tactic Distribution

### Empirical Weights

**Source:** Composite from LeanDojo (Yang & Song 2023), miniF2F tidy baseline (Han et al. 2021), Structured Hints (arXiv:2601.16172)

```yaml
tactic_distribution:
  # High-frequency tactics (80% cumulative)
  simp: 0.35        # Simplification (most common)
  rfl: 0.15         # Reflexivity (proof closer)
  intro: 0.08       # Hypothesis introduction
  apply: 0.07       # Theorem application
  cases: 0.06       # Case analysis
  
  # Medium-frequency tactics (15% cumulative)
  intros: 0.04      # Multiple intros
  ring: 0.04        # Ring solver
  induction: 0.04   # Induction
  exact: 0.04       # Direct proof term
  norm_num: 0.03    # Numeric normalization
  constructor: 0.03 # Constructor application
  
  # Low-frequency tactics (5% cumulative)
  linarith: 0.02    # Linear arithmetic
  omega: 0.02       # Integer arithmetic
  have: 0.02        # Auxiliary lemma
  calc: 0.01        # Calculational proof
```

**Validation:**
```bash
# Spot-check on 10 random Mathlib files
files=$(find mathlib4/Mathlib -name "*.lean" | shuf -n 10)
for f in $files; do
  grep -oh "by [a-z_]*" $f | head -100
done | sort | uniq -c | sort -rn

# Expected output (±10% variance acceptable):
#   ~350 simp
#   ~150 rfl
#    ~80 intro
#    ...
```

---

## Random Sampler Implementation

### Weighted Sampling Algorithm

```lean
-- Level 1.5 pseudo-code (concrete enough for Phase 3)

import Lean
import Lean.Meta
import Lean.Elab.Tactic

namespace RandomMathlib

-- Tactic distribution (weights must sum to 1.0)
def tacticWeights : List (String × Float) := [
  ("simp", 0.35), ("rfl", 0.15), ("intro", 0.08),
  ("apply", 0.07), ("cases", 0.06), ("intros", 0.04),
  ("ring", 0.04), ("induction", 0.04), ("exact", 0.04),
  ("norm_num", 0.03), ("constructor", 0.03), ("linarith", 0.02),
  ("omega", 0.02), ("have", 0.02), ("calc", 0.01)
]

-- Weighted random tactic selection
def sampleTactic (rng: StdGen) : String × StdGen := do
  let (r, rng') := rng.next  -- Random float in [0, 1)
  
  -- Find tactic via cumulative distribution
  let cumulative := tacticWeights.scanl (fun acc (_, w) => acc + w) 0.0
  let pairs := tacticWeights.zip cumulative.tail
  
  let idx := pairs.findIdx? (fun ((_, w), cum) => r < cum) |>.getD 0
  let tactic := tacticWeights[idx].1
  
  return (tactic, rng')

-- Random goal selection (when tactic creates multiple subgoals)
def pickRandomGoal (goals: List MVarId) (rng: StdGen) : MVarId × StdGen := do
  let (r, rng') := rng.next
  let idx := r % goals.length
  return (goals[idx], rng')

-- Proof search with random Mathlib tactics
def randomProofSearch 
    (goal: MVarId) 
    (budget: Nat := 15) 
    (seed: Nat := 0) 
    : TermElabM (Option Proof × Nat × List String) := do
  
  let mut rng := mkStdGen seed
  let mut currentGoal := goal
  let mut tacticSequence := []
  
  for i in [0:budget] do
    -- Sample tactic
    let (tacticStr, rng') := sampleTactic rng
    rng := rng'
    tacticSequence := tacticSequence.append [tacticStr]
    
    -- Parse tactic string to tactic syntax
    let tacticStx ← parseTactic tacticStr
    
    -- Apply tactic
    try
      let newGoals ← Lean.Elab.Tactic.run currentGoal do
        evalTactic tacticStx
      
      -- Check if solved
      if newGoals.isEmpty then
        return (some proof, i+1, tacticSequence)  -- Success
      
      -- Pick random goal to continue
      let (nextGoal, rng'') := pickRandomGoal newGoals rng
      currentGoal := nextGoal
      rng := rng''
      
    catch e =>
      -- Tactic failed, continue to next iteration
      continue
  
  -- Budget exhausted without solving
  return (none, budget, tacticSequence)

end RandomMathlib
```

---

## Evaluation Harness

### Batch Evaluation Script

```lean
-- evaluate_h_m3.lean

import RandomMathlib
import Minif2f.Test

def evaluateMiniF2F : IO Unit := do
  -- Load miniF2F test problems (244 theorems)
  let problems ← loadMiniF2FTestTheorems
  
  -- Parallel evaluation (8 workers)
  let results ← problems.mapMConcurrent 8 fun (problem, idx) => do
    let seed := idx  -- Deterministic seeding (problem index)
    
    -- Run with timeout
    let startTime ← IO.monoMsNow
    let result ← runWithTimeout 300000 do  -- 300s timeout
      randomProofSearch problem.goal budget:=15 seed:=seed
    let endTime ← IO.monoMsNow
    let wallTime := (endTime - startTime) / 1000.0  -- Convert to seconds
    
    match result with
    | some (proof?, tacticsUsed, tacticSeq) =>
        return {
          problemId := problem.name,
          source := problem.source,
          outcome := if proof?.isSome then "solved" else "budget_exhausted",
          tacticsUsed := tacticsUsed,
          tacticSequence := tacticSeq,
          wallTime := wallTime,
          seed := seed
        }
    | none =>
        return {
          problemId := problem.name,
          source := problem.source,
          outcome := "timeout",
          tacticsUsed := 0,
          tacticSequence := [],
          wallTime := 300.0,
          seed := seed
        }
  
  -- Write per-problem results (JSONL)
  let jsonlPath := "h_m3_results.jsonl"
  let jsonlContent := results.map toJson |>.map toString |>.intersperse "\n" |>.foldl (· ++ ·) ""
  IO.FS.writeFile jsonlPath jsonlContent
  
  -- Aggregate statistics
  let solvedCount := results.filter (·.outcome == "solved") |>.length
  let successRate := solvedCount.toFloat / 244.0
  let (ciLower, ciUpper) := wilsonCI solvedCount 244 0.05
  
  IO.println s!"H-M3 Results:"
  IO.println s!"  Solved: {solvedCount}/244 ({successRate*100:.1f}%)"
  IO.println s!"  95% CI: [{ciLower*100:.1f}%, {ciUpper*100:.1f}%]"
  IO.println s!"  Results written to {jsonlPath}"
```

### Shell Wrapper

```bash
#!/bin/bash
# evaluate_h_m3.sh

set -e

echo "=== H-M3 Evaluation: Random Mathlib Tactic Sampling ==="
echo ""

# Environment
echo "Environment:"
echo "  Lean version: $(lean --version)"
echo "  Workers: 8"
echo "  Timeout: 300s per problem"
echo "  Tactic budget: 15"
echo ""

# Build
echo "Building prover..."
lake build RandomMathlib
lake build Minif2f

# Evaluate
echo "Running evaluation (244 problems)..."
start_time=$(date +%s)

lake env lean --run evaluate_h_m3.lean

end_time=$(date +%s)
elapsed=$((end_time - start_time))

echo ""
echo "Evaluation complete in ${elapsed}s"
echo ""

# Post-process
echo "Running statistical analysis..."
python3 analyze_h_m3.py

echo ""
echo "=== Evaluation Complete ==="
```

---

## Statistical Analysis

### Python Post-Processing

```python
# analyze_h_m3.py

import json
import numpy as np
from scipy.stats import proportions_ztest
from statsmodels.stats.proportion import proportion_confint

# Load H-M3 results
with open('h_m3_results.jsonl') as f:
    results = [json.loads(line) for line in f]

# Aggregate statistics
total = len(results)
solved = sum(1 for r in results if r['outcome'] == 'solved')
success_rate = solved / total

# Confidence interval (Wilson)
ci_lower, ci_upper = proportion_confint(solved, total, alpha=0.05, method='wilson')

# H-E1 baseline (from verification_state.yaml)
lean_auto_solved = 38
lean_auto_total = 244
lean_auto_rate = lean_auto_solved / lean_auto_total

# Delta vs lean-auto
delta = success_rate - lean_auto_rate

# Statistical significance (one-sided z-test)
z, p = proportions_ztest(
    [solved, lean_auto_solved],
    [total, lean_auto_total],
    alternative='larger'
)

# Print results
print(f"H-M3 Results:")
print(f"  Success Rate: {success_rate*100:.1f}% [{ci_lower*100:.1f}%, {ci_upper*100:.1f}%]")
print(f"  Solved: {solved}/{total}")
print(f"")
print(f"Comparison to H-E1 (lean-auto):")
print(f"  H-E1 Baseline: {lean_auto_rate*100:.1f}%")
print(f"  Delta: {delta*100:+.1f} percentage points")
print(f"  Z-statistic: {z:.2f}")
print(f"  P-value: {p:.4f}")
print(f"  Significant (p<0.05): {p < 0.05}")
print(f"")

# Gate evaluation
in_range = 0.18 <= success_rate <= 0.25
delta_in_range = 0.03 <= delta <= 0.10
significant = p < 0.05

print(f"Gate Evaluation (SHOULD_WORK):")
print(f"  Success rate ∈ [18%, 25%]: {in_range} ({'PASS' if in_range else 'FAIL'})")
print(f"  Delta ∈ [3%, 10%]: {delta_in_range} ({'PASS' if delta_in_range else 'FAIL'})")
print(f"  Statistically significant: {significant} ({'PASS' if significant else 'FAIL'})")
print(f"")
print(f"Overall Gate: {'PASS' if (in_range and delta_in_range and significant) else 'FAIL'}")

# Failure mode breakdown
budget_exhausted = sum(1 for r in results if r['outcome'] == 'budget_exhausted')
timeout = sum(1 for r in results if r['outcome'] == 'timeout')
error = sum(1 for r in results if r['outcome'] == 'error')

print(f"")
print(f"Failure Modes:")
print(f"  Budget exhausted: {budget_exhausted} ({budget_exhausted/total*100:.1f}%)")
print(f"  Timeout: {timeout} ({timeout/total*100:.1f}%)")
print(f"  Error: {error} ({error/total*100:.1f}%)")

# Tactic consumption (for solved problems only)
solved_results = [r for r in results if r['outcome'] == 'solved']
if solved_results:
    tactics_used = [r['tacticsUsed'] for r in solved_results]
    print(f"")
    print(f"Tactic Consumption (solved problems):")
    print(f"  Mean: {np.mean(tactics_used):.1f}")
    print(f"  Median: {np.median(tactics_used):.1f}")
    print(f"  Std: {np.std(tactics_used):.1f}")
    print(f"  CV: {np.std(tactics_used)/np.mean(tactics_used):.2f}")

# Stratification (if metadata available)
sources = set(r['source'] for r in results if 'source' in r and r['source'])
if sources:
    print(f"")
    print(f"Stratification by Source:")
    for source in sorted(sources):
        src_results = [r for r in results if r.get('source') == source]
        src_solved = sum(1 for r in src_results if r['outcome'] == 'solved')
        src_rate = src_solved / len(src_results)
        print(f"  {source}: {src_rate*100:.1f}% ({src_solved}/{len(src_results)})")

# Write aggregate YAML
import yaml

aggregate = {
    'h_m3_results': {
        'success_rate': float(success_rate),
        'ci_95': [float(ci_lower), float(ci_upper)],
        'solved_count': int(solved),
        'delta_vs_lean_auto': {
            'value': float(delta),
            'z_statistic': float(z),
            'p_value': float(p),
            'significant': bool(p < 0.05)
        },
        'failure_modes': {
            'budget_exhausted': int(budget_exhausted),
            'timeout': int(timeout),
            'error': int(error)
        }
    }
}

if solved_results:
    aggregate['h_m3_results']['tactic_consumption'] = {
        'mean': float(np.mean(tactics_used)),
        'median': float(np.median(tactics_used)),
        'std': float(np.std(tactics_used)),
        'cv': float(np.std(tactics_used)/np.mean(tactics_used))
    }

with open('h_m3_aggregate.yaml', 'w') as f:
    yaml.dump(aggregate, f, default_flow_style=False)

print(f"")
print(f"Aggregate statistics written to h_m3_aggregate.yaml")
```

---

## Reproducibility

### Deterministic Execution

**RNG Seeding Strategy:**
- **Problem 0** → seed 0
- **Problem 1** → seed 1
- **Problem i** → seed i

**Guarantees:**
- Same tactic sequence for same problem + same seed
- Same goal selection for same subgoal list + same seed
- Exact reproducibility on rerun

### Validation Protocol

```bash
# Run full evaluation
./evaluate_h_m3.sh > run1.log

# Extract solved problem IDs
jq -r 'select(.outcome == "solved") | .problemId' h_m3_results.jsonl | sort > solved1.txt

# Rerun 10% subset (24 problems)
subset=$(head -24 solved1.txt)
for problem in $subset; do
  # Rerun with same seed
  lake env lean --run "randomProofSearch $problem seed:=$(problem_index)"
done > rerun.log

# Compare results (should match exactly)
diff run1.log rerun.log
```

---

## Key Design Decisions

### 1. Weighted vs Uniform Sampling

**Choice:** Weighted sampling from empirical Mathlib distribution

**Rationale:**
- Hypothesis tests "corpus contribution" = human tactic patterns
- Uniform sampling would test "random search" (different hypothesis)
- Weighted distribution matches claim (10% corpus pattern contribution)

### 2. Goal Selection Strategy

**Choice:** Random goal selection (when tactic creates multiple subgoals)

**Rationale:**
- Simplest strategy (no heuristics, no semantic ordering)
- Human proofs use strategic ordering → random underestimates corpus benefit
- Conservative estimate (lower bound on corpus contribution)

### 3. Tactic Budget

**Choice:** 15 evaluations (from H-E1 recommendation)

**Rationale:**
- H-E1 lean-auto: mean=9.2±4.1, median=7.0
- 15 = mean + 1.4σ (covers 90% of lean-auto distribution)
- Fair comparison (random sampler has same budget as lean-auto mean)

### 4. Premise Selection

**Choice:** None (zero-shot)

**Rationale:**
- Matches H-E1 baseline (no premise selection)
- Isolates tactic frequency effect (no retrieval confound)
- Simplest implementation

---

## Limitations

### Acknowledged Confounds

1. **Corpus Bias is Inherent:**
   - Random sampling from human proofs encodes implicit heuristics
   - Tactic frequency ≠ pure randomness
   - Δ conflates frequency + implicit patterns

2. **No Semantic Understanding:**
   - Random sampler has NO goal-awareness
   - Cannot adapt tactics to problem structure
   - Provides lower bound on corpus contribution

3. **Goal Selection is Random:**
   - Human proofs prioritize goals strategically
   - Random selection underestimates corpus benefit
   - Conservative estimate (actual corpus effect may be higher)

### Mitigation Strategies

- **Triangulation:** Use as THIRD baseline (lean-auto | Random | LLM)
- **Transparency:** Report limitations in caveat section
- **Conservative Claims:** Interpret as lower bound, not exact measure

---

## References

- **Tactic Distribution:** LeanDojo (Yang & Song 2023), Structured Hints (arXiv:2601.16172)
- **Weighted Sampling:** Inverse transform method (standard algorithm)
- **Statistical Tests:** Wilson CI (Agresti & Coull 1998), One-proportion z-test
- **miniF2F Infrastructure:** Reuse H-E1 evaluation harness
