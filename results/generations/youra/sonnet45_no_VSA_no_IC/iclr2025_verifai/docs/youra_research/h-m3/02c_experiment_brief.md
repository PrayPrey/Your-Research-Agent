# Experiment Design: H-M3

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Random Mathlib tactic sampling achieves 18-25% success (Δ=5% above lean-auto, tests 10% corpus contribution)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests corpus contribution claim via controlled comparison.

---

## Workflow Status

**Verification State:** ACTIVE (Phase 2C)
**Prerequisites Satisfied:** H-E1 COMPLETED (lean-auto baseline = 15.6% [11.5%, 20.3%])
**Gate Status:** SHOULD_WORK (control baseline for triangulation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** [H-E1] (lean-auto baseline established)

### Gate Condition
**SHOULD_WORK** — If random Mathlib sampling performs outside [15%, 30%] range:
- **Below 15%**: Random sampling ≤ lean-auto → corpus bias rejected (corpus doesn't help)
- **Above 30%**: Random sampling >> predicted → corpus contribution underestimated (claim invalid)
- **Pass criteria**: 18-25% (Δ=3-10 percentage points above lean-auto 15.6%)

**Falsification Logic:**
- IF Random < 15% OR Random > 30%, THEN reject 10% contribution claim
- Purpose: Third baseline for triangulation (lean-auto | Random Mathlib | LLM)

---

## Continuation Context

### Previous Hypothesis Results

**H-E1: lean-auto Baseline (COMPLETED)**
- **Success Rate**: 15.6% [11.5%, 20.3%] (38/244 problems)
- **Tactic Count**: mean=9.2±4.1, median=7.0
- **Error Rate**: 10.7% (26/244) due to Lean 3→4 porting issues
- **Infrastructure**: lean-auto + google-deepmind/miniF2F validated

**Key Carryover:**
- miniF2F test set (244 problems) established
- Evaluation harness validated (parallel workers, timeout=300s)
- Tactic budget baseline measured: recommend 15 evaluations for H-C1
- Infrastructure ready for reuse

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**No relevant results** — Archon KB lacks Lean/theorem proving content. All implementation from Exa search.

### Archon Code Examples

**No relevant results** — KB focused on ML/DL, not formal mathematics.

### Exa GitHub Implementations

**Repository 1**: leanprover-community/mathlib4
- **URL**: https://github.com/leanprover-community/mathlib4
- **Relevance**: Source of tactic distribution for random sampling
- **Key Features**:
  - 1M+ lines of formalized mathematics (Lean 4)
  - Standard tactic library (simp, ring, linarith, omega, norm_num, etc.)
  - Tactic usage statistics extractable via GitHub search or corpus analysis
- **Tactic Frequency (empirical from research papers)**:
  - `simp`: ~35% of all tactic applications
  - `rfl`: ~15%
  - `intro`/`intros`: ~12%
  - `cases`/`induction`: ~10%
  - `ring`/`linarith`/`omega`: ~8%
  - `apply`: ~7%
  - Other: ~13%

**Repository 2**: VERITAS (arXiv:2606.19399)
- **URL**: https://www.emergentmind.com/papers/2606.19399
- **Relevance**: Best-of-N sampling baseline for Lean 4 theorem proving
- **Key Implementation**:
  ```lean
  -- Phase 1: Best-of-N flat sampling
  for i in 1..N do
    tactic ← sampleFromDistribution(tactics, weights)
    result ← applyTactic(tactic, goal)
    if result.success then return proof
  ```
- **Findings**: Best-of-5 achieves 36.9% on miniF2F (with LLM, not random)
- **Relevance**: Random sampling control should be significantly lower

**Repository 3**: miniF2F tidy baseline (arXiv:2109.00110)
- **URL**: https://openreview.net/pdf?id=9ZPegFuFTFv (Section 4.2.1)
- **Relevance**: Original miniF2F baseline using fixed tactic list
- **Key Implementation**:
  - Tactic list L = [rfl, simp, ring, decide, intro, constructor, ...]
  - High-level tactics HL = [nlinarith, linarith, ring_nf, norm_num]
  - Best-first search with priority queue
  - Result: 18% on miniF2F-test (i_max=8, deterministic)
- **Note**: This is NOT random sampling (fixed sequence), but provides reference point

**Repository 4**: Structured Hints for Lean (arXiv:2601.16172)
- **URL**: https://arxiv.org/html/2601.16172v1
- **Relevance**: Fixed tactic skeleton schedule (15 skeletons × 8 hints)
- **Key Tactics Used**:
  ```
  [empty, simp, intro, constructor, cases, induction, apply, 
   ring, linarith, omega, norm_num, aesop, field_simp, 
   ring_nf, nlinarith]
  ```
- **Finding**: 21.7% pass@16 with structural guidance (vs 15.2% baseline)
- **Relevance**: Random sampling from this set provides corpus-based control

### 🎯 Implementation Priority Assessment

**No paper reproduction** — This is a novel control baseline, not reproducing a specific method.

**Recommended Implementation Path:**
1. **Extract Mathlib tactic distribution** from empirical corpus analysis OR use standard tactic frequency from literature
2. **Random sampler**: Sample tactics from weighted distribution, apply to goal until budget exhausted
3. **Evaluation**: Same miniF2F infrastructure as H-E1 (reuse harness)

**Design Decision:**
- **Weighted sampling** (reflects human corpus) vs **Uniform sampling** (pure random)
- **Choice**: Weighted sampling from empirical Mathlib distribution (matches hypothesis claim)
- **Justification**: Tests "corpus contribution" = human tactic patterns, not uniform random

### Code Analysis (Serena MCP)

**Not performed** — Implementation is straightforward random sampler. Serena not needed.

---

## Experiment Specification

### Objective

Test whether **random tactic sampling from Mathlib distribution** achieves 18-25% success on miniF2F, demonstrating 3-10 percentage point improvement over lean-auto (15.6%) attributable to corpus pattern matching.

### Research Question

**RQ-M3**: Does sampling tactics from human-written Mathlib corpus distribution (without semantic guidance) outperform deterministic automated prover (lean-auto) due to corpus bias alone?

### Hypothesis (Mechanistic)

**Main Claim**: Random Mathlib tactic sampling achieves **20% success** (midpoint of [18%, 25%])

**Predicted Effect Size**:
- Random Mathlib: 20% (predicted)
- lean-auto (H-E1): 15.6% (measured)
- **Δ = 4.4 percentage points** (within [3%, 10%] range)

**Contribution Attribution**:
- Δ represents "corpus contribution" = human tactic frequency patterns (no semantic understanding)
- Tests the 10% contribution claim from main hypothesis (Δ=50% → 10% = 5 percentage points)

---

## Experimental Design

### Dataset

**Reuse H-E1 Infrastructure:**
- **Name**: miniF2F Lean 4 Test Set
- **Source**: google-deepmind/miniF2F (AlphaProof evaluation version)
- **Size**: 244 problems (test split)
- **Splits**: Test only (no validation needed for baseline)
- **Problem Sources**: AMC (~73), AIME (~98), IMO (~73)

**Preprocessing**: None (reuse H-E1 setup)

### Baseline Configuration

**Prover**: Random Mathlib Tactic Sampler (custom implementation)

**Tactic Distribution** (weighted sampling):
```yaml
tactic_distribution:
  simp: 0.35
  rfl: 0.15
  intro: 0.08
  intros: 0.04
  cases: 0.06
  induction: 0.04
  ring: 0.04
  linarith: 0.02
  omega: 0.02
  norm_num: 0.03
  apply: 0.07
  constructor: 0.03
  exact: 0.04
  have: 0.02
  calc: 0.01
```

**Sampling Algorithm**:
```lean
-- Pseudo-code (Level 1.5 specification)
def randomMathlibProver (goal: Goal, budget: Nat) : Option Proof :=
  for i in 1..budget do
    tactic ← sampleWeighted(tacticDistribution)
    result ← tryApply(tactic, goal)
    match result with
    | Success newGoals =>
        if newGoals.isEmpty then
          return some proof
        else
          goal ← pickRandom(newGoals)  -- Random goal selection
    | Failure => continue
  return none
```

**Configuration**:
- **Tactic budget**: 15 evaluations (from H-E1 recommendation)
- **Goal selection**: Random (if tactic creates multiple subgoals)
- **Premise selection**: None (zero-shot, like H-E1)
- **Timeout**: 300s per problem (same as H-E1)

### Comparison Baseline

**Control**: H-E1 lean-auto results
- Success rate: 15.6% [11.5%, 20.3%]
- Tactic budget: mean=9.2±4.1 (well within 15 budget for Random)

---

## Evaluation Protocol

### Metrics

**Primary**:
- **Success Rate**: problems_solved / 244
- **Target Range**: [18%, 25%] (predicted: 20%)
- **Δ vs lean-auto**: [3%, 10%] percentage points

**Secondary**:
- **Tactic consumption**: Average evaluations used per solved problem
- **Solve time**: Wall-clock seconds (for infrastructure validation)
- **Failure modes**: timeout, error, budget_exhausted

### Statistical Analysis

**Confidence Interval**: 95% Wilson score interval
- Sample size: 244 problems
- Expected solves: 49 ± 8 (20% ± 3%)

**Comparison Test**:
- H0: Random success rate = lean-auto success rate (15.6%)
- H1: Random success rate > lean-auto (one-sided test)
- **Test**: One-proportion z-test
- **Significance**: α = 0.05

**Stratification** (optional if metadata available):
- By source (AMC/AIME/IMO): Test if corpus bias varies by competition
- Prediction: Uniform effect (corpus patterns are domain-agnostic)

### Falsification Criteria

**REJECT hypothesis IF**:
1. Random success rate < 15% (no corpus benefit)
2. Random success rate > 30% (corpus contribution >> predicted)
3. Δ vs lean-auto not statistically significant (p > 0.05)

**PASS criteria**:
- Random success rate ∈ [18%, 25%]
- Δ ∈ [3%, 10%] percentage points
- p < 0.05 (one-sided z-test)

---

## Implementation Plan (Level 1.5)

### Phase 1: Tactic Distribution Extraction

**Option A: Corpus Analysis** (if time permits)
```bash
# Extract tactic usage from Mathlib4
git clone https://github.com/leanprover-community/mathlib4
cd mathlib4
grep -roh "by [a-z_]*" . | sort | uniq -c | sort -rn > tactic_freq.txt
# Compute empirical distribution from frequency counts
```

**Option B: Literature-Based** (faster, recommended)
- Use empirical distribution from prior research papers
- Validate against spot-check of Mathlib files
- **Distribution**: See "Tactic Distribution" section above

### Phase 2: Random Sampler Implementation

**File**: `random_mathlib_sampler.lean`

```lean
-- Level 1.5 pseudo-code
import Lean
import Minif2f.Test

-- Tactic distribution (empirical weights)
def tacticWeights : List (String × Float) := [
  ("simp", 0.35), ("rfl", 0.15), ("intro", 0.08),
  ("intros", 0.04), ("cases", 0.06), ("induction", 0.04),
  ("ring", 0.04), ("linarith", 0.02), ("omega", 0.02),
  ("norm_num", 0.03), ("apply", 0.07), ("constructor", 0.03),
  ("exact", 0.04), ("have", 0.02), ("calc", 0.01)
]

-- Weighted random sampling
def sampleTactic (rng: StdGen) : String × StdGen :=
  let (r, rng') := rng.next
  let cumulative := tacticWeights.scanl (·.2 + ·.2) 0.0
  let idx := cumulative.findIdx? (r.toFloat / Float.maxValue < ·) |>.getD 0
  (tacticWeights[idx].1, rng')

-- Proof search
def randomProofSearch (goal: MVarId) (budget: Nat) (rng: StdGen) : 
    TermElabM (Option Proof × Nat) := do
  for i in [0:budget] do
    let (tactic, rng') := sampleTactic rng
    try
      let goals' ← evalTacticString tactic goal
      if goals'.isEmpty then
        return (some proof, i+1)  -- Success, return tactic count
      else
        goal ← pickRandomGoal goals' rng'  -- Random goal selection
        rng := rng'
    catch _ => continue
  return (none, budget)  -- Exhausted budget

-- Evaluation harness (reuse H-E1 infrastructure)
def evaluateMinif2f : IO Unit := do
  let problems ← loadMinif2fTest  -- 244 problems
  let results ← problems.mapM fun p => do
    let rng := mkStdGen p.seed
    let (proof?, tactics_used) ← runWithTimeout 300000 
      (randomProofSearch p.goal 15 rng)
    return { problem := p, success := proof?.isSome, 
             tactics_used, wall_time }
  
  -- Aggregate statistics
  let success_rate := results.filter (·.success) |>.length / 244
  let ci_95 := wilsonCI success_rate 244
  IO.println s!"Success: {success_rate*100:.1f}% {ci_95}"
```

### Phase 3: Evaluation

**Reuse H-E1 Infrastructure**:
- Parallel workers: 8 (same as H-E1)
- Timeout: 300s per problem
- Logging: Per-problem results + aggregate statistics

**Reproducibility**:
- **Deterministic seeding**: Use problem index as RNG seed
- **Rerun validation**: 10% subset (24 problems) should match exactly

### Phase 4: Statistical Comparison

```python
# Post-processing analysis
from scipy.stats import proportions_ztest

# H-E1 baseline
lean_auto_success = 38  # from H-E1
lean_auto_n = 244

# H-M3 results
random_success = ?  # From experiment
random_n = 244

# One-sided z-test (Random > lean-auto)
z, p = proportions_ztest(
    [random_success, lean_auto_success],
    [random_n, lean_auto_n],
    alternative='larger'
)

print(f"Δ = {(random_success/244 - lean_auto_success/244)*100:.1f} pp")
print(f"p-value = {p:.4f}")
print(f"Significant: {p < 0.05}")

# Stratification (if metadata available)
for source in ['AMC', 'AIME', 'IMO']:
    random_src = results[results.source == source].success.sum()
    lean_auto_src = h_e1_results[h_e1_results.source == source].success.sum()
    print(f"{source}: Random={random_src/n_src:.1%}, lean-auto={lean_auto_src/n_src:.1%}")
```

---

## Expected Results

### Primary Outcomes

**Predicted Success Rate**: 20% (49/244 problems)
- **95% CI**: [15.3%, 25.5%] (Wilson interval)
- **Δ vs lean-auto**: 4.4 percentage points
- **Statistical significance**: p < 0.05 (one-sided z-test)

### Secondary Outcomes

**Tactic Consumption**:
- Mean: ~10 evaluations per solved problem (within 15 budget)
- Variance: High (random sampling → path variance)

**Failure Modes**:
- Budget exhausted: ~60% (tactic sampling inefficient vs semantic prover)
- Timeout: ~35% (similar to H-E1)
- Error: <5% (infrastructure stable from H-E1)

### Stratification Hypothesis

**By Source** (if metadata available):
- **AMC**: 22% (easier problems, tactic sampling effective)
- **AIME**: 19% (moderate)
- **IMO**: 18% (harder, less benefit from random tactics)

**Interpretation**: Corpus bias slightly favors easier problems (AMC) where standard tactics suffice.

---

## Success Criteria

### Gate Pass Conditions

**SHOULD_WORK gate satisfied IF**:
1. ✅ Random success rate ∈ [18%, 25%]
2. ✅ Δ ∈ [3%, 10%] percentage points above lean-auto
3. ✅ p < 0.05 (statistically significant improvement)

**Outcome**:
- **PASS**: Corpus contribution validated at ~5% (10% of 50% gap claim)
- **Route to**: H-C1, H-M1, H-M2 (independent hypotheses)

### Gate Fail Conditions

**IF Random < 15%** (no corpus benefit):
- **Interpretation**: Mathlib corpus distribution does NOT improve over deterministic prover
- **Action**: Reject 10% corpus contribution claim, revise main hypothesis
- **Impact**: Main hypothesis mechanism attribution revised (60% NL + 30% depth + 0% corpus)

**IF Random > 30%** (excessive benefit):
- **Interpretation**: Corpus contribution >> 10% predicted
- **Action**: Re-estimate mechanism contributions, corpus may explain larger gap
- **Impact**: Main hypothesis claim (60%/30%/10% split) invalid

---

## Risk Assessment

### Risk 1: Corpus Bias Acknowledged
- **Probability**: 60%
- **Description**: Random sampling from human proofs ≠ uniform distribution (inherent bias)
- **Mitigation**: 
  - Use as THIRD baseline for triangulation (lean-auto | Random | LLM)
  - Acknowledge limitation in caveat section
  - Corpus bias is EXPECTED (tests human pattern contribution)

### Risk 2: Variance from Randomness
- **Probability**: 40%
- **Description**: Random sampling → high variance in solve paths
- **Mitigation**:
  - Deterministic seeding (problem index → RNG seed)
  - Rerun validation (10% subset match check)
  - Report confidence intervals (Wilson 95% CI)

### Risk 3: Budget Sensitivity
- **Probability**: 30%
- **Description**: 15-evaluation budget may be too low/high
- **Mitigation**:
  - Budget chosen from H-E1 measurement (mean=9.2, recommend=15)
  - Ablation study (optional): Test budget ∈ {10, 15, 20}
  - Report tactic consumption per solved problem

---

## Limitations & Caveats

### Acknowledged Limitations

1. **Corpus Bias is Inherent**:
   - Random sampling from Mathlib ≠ pure random tactics
   - Human-written proofs encode domain knowledge in tactic frequency
   - **Implication**: 5% gap (vs lean-auto) conflates corpus frequency + implicit heuristics

2. **No Semantic Understanding**:
   - Random sampler has NO goal-awareness (unlike LLM)
   - Provides lower bound on corpus contribution (frequency alone)
   - **Implication**: True corpus contribution may be higher (frequency + heuristics)

3. **Tactic Distribution Approximation**:
   - Empirical distribution from literature (not exact Mathlib corpus)
   - Spot-check validation recommended
   - **Implication**: Results sensitive to distribution accuracy (±2 percentage points)

4. **Goal Selection is Random**:
   - When tactic creates multiple subgoals, pick random (not strategic)
   - Human proofs use semantic ordering
   - **Implication**: Underestimates corpus contribution (no goal prioritization)

### Interpretation Guidance

**IF H-M3 PASSES (18-25% range)**:
- Corpus frequency patterns contribute ~5 percentage points
- Supports main hypothesis 10% corpus contribution claim
- **Triangulation validated**: lean-auto < Random Mathlib < LLM

**IF H-M3 FAILS (outside range)**:
- Below 15%: Corpus frequency alone insufficient (semantic understanding dominates)
- Above 30%: Corpus contribution underestimated (revise main hypothesis)

---

## Timeline Estimation

**Total Duration**: 4 days

**Breakdown**:
- Day 1: Tactic distribution extraction + validation (4h)
- Day 2: Random sampler implementation (6h)
- Day 3: Evaluation run on miniF2F (244 problems @ 300s → 20h wall-clock, 8 workers → 2.5h)
- Day 4: Statistical analysis + report (4h)

**Prerequisites**: H-E1 COMPLETED (infrastructure ready)

**Parallel Work**: Can run alongside H-M1, H-M2 (independent hypotheses)

---

## Deliverables

### Code Artifacts
1. `random_mathlib_sampler.lean` (tactic distribution + proof search)
2. `evaluate_h_m3.sh` (evaluation harness script)
3. `tactic_distribution.yaml` (empirical weights)

### Data Artifacts
1. `h_m3_results.jsonl` (per-problem results)
2. `h_m3_aggregate.yaml` (success rate, CI, Δ vs lean-auto)
3. `h_m3_stratification.csv` (by source, if metadata available)

### Documentation
1. `04_validation.md` (Phase 4 validation report)
2. `implementation_notes.md` (tactic distribution rationale)
3. `comparison_analysis.ipynb` (statistical tests, visualization)

---

## References

### Primary Sources
- **miniF2F Benchmark**: Zheng et al. (2021) - https://arxiv.org/abs/2109.00110
- **lean-auto Prover**: Qian et al. (2025) - https://github.com/leanprover-community/lean-auto
- **Tidy Baseline**: Han et al. (2021, PACT paper) - Section 4.2.1

### Implementation Guides
- **VERITAS**: arXiv:2606.19399 (Best-of-N sampling)
- **Structured Hints**: arXiv:2601.16172 (Tactic skeleton schedules)
- **Mathlib4**: https://github.com/leanprover-community/mathlib4

### Prior Work
- **H-E1 Results**: lean-auto baseline 15.6% [11.5%, 20.3%] (from verification_state.yaml)
- **Phase 2B Plan**: 02b_verification_plan.md (H-M3 specification)

---

## Appendix: Tactic Distribution Validation

### Empirical Distribution (Literature)

Source: Composite from LeanDojo (2023), miniF2F tidy baseline (2021), Structured Hints (2026)

| Tactic | Weight | Rationale |
|--------|--------|-----------|
| `simp` | 0.35 | Most common simplifier (35% of all tactics) |
| `rfl` | 0.15 | Reflexivity (common proof closer) |
| `intro`/`intros` | 0.12 | Hypothesis introduction (ubiquitous) |
| `cases`/`induction` | 0.10 | Case analysis (structural tactics) |
| `ring`/`linarith`/`omega` | 0.08 | Automation for algebra/arithmetic |
| `apply` | 0.07 | Theorem application (frequent) |
| `norm_num` | 0.03 | Numeric normalization |
| `constructor` | 0.03 | Constructor application |
| `exact` | 0.04 | Direct proof term |
| `have`/`calc` | 0.03 | Auxiliary lemmas / calculational proofs |

**Validation Method**:
```bash
# Spot-check on 10 random Mathlib files
files=$(find mathlib4/Mathlib -name "*.lean" | shuf -n 10)
for f in $files; do
  grep -oh "by [a-z_]*" $f | head -100
done | sort | uniq -c | sort -rn
# Compare to literature distribution (expect ±10% variance)
```

---

**Phase 2C Complete for H-M3**
**Next Phase**: Phase 3 Implementation Planning (auto-triggered by harness)
