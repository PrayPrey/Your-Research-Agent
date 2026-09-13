# Product Requirements Document: H-M3
# Random Mathlib Tactic Sampling Baseline

**Hypothesis ID:** h-m3  
**Date:** 2026-08-20  
**Status:** Phase 3 Implementation Planning  
**Gate:** SHOULD_WORK  
**Prerequisites:** H-E1 COMPLETED (lean-auto baseline established)

---

## Executive Summary

Build random Mathlib tactic sampler that validates corpus contribution claim (10% of main hypothesis gap) by achieving 18-25% success on miniF2F test set (Δ=3-10pp above lean-auto 15.6%). Reuses H-E1 infrastructure for evaluation.

---

## Objectives

### Primary Goal
Implement weighted random tactic sampler from empirical Mathlib distribution that:
- Achieves 18-25% success on miniF2F (244 problems)
- Outperforms lean-auto by 3-10 percentage points
- Validates corpus pattern matching contribution claim

### Secondary Goals
- Establish third baseline for triangulation (lean-auto | Random | LLM)
- Measure tactic consumption distribution
- Stratify results by problem source (AMC/AIME/IMO)

---

## Success Metrics

### Primary Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Success Rate | [18%, 25%] | problems_solved / 244 |
| Δ vs lean-auto | [3%, 10%] pp | H-M3 rate - H-E1 rate |
| Statistical Significance | p < 0.05 | One-proportion z-test |

### Secondary Metrics
- **Tactic consumption**: Mean evaluations per solved problem (target: ~10)
- **Solve time**: Wall-clock seconds (infrastructure validation)
- **Failure modes**: Breakdown of budget_exhausted, timeout, error

---

## Functional Requirements

### FR1: Tactic Distribution
**Description:** Empirical weighted distribution from Mathlib corpus  
**Rationale:** Tests human tactic frequency patterns (corpus contribution)  
**Specification:**
- 15 tactics with empirical weights summing to 1.0
- Top tactics: simp (35%), rfl (15%), intro (8%), apply (7%)
- Source: LeanDojo + Structured Hints literature

### FR2: Weighted Random Sampler
**Description:** Sample tactics from weighted distribution  
**Algorithm:**
```lean
def sampleTactic (rng: StdGen) : String × StdGen :=
  cumulative_distribution ← compute_from_weights
  random_value ← rng.next
  tactic ← inverse_transform_sample(cumulative, random_value)
  return (tactic, updated_rng)
```
**Properties:**
- Deterministic seeding (problem_index → seed)
- Reproducible on rerun

### FR3: Proof Search Loop
**Description:** Apply random tactics until budget exhausted or proof found  
**Specification:**
- **Budget:** 15 evaluations (from H-E1 recommendation)
- **Goal selection:** Random (when tactic creates multiple subgoals)
- **Timeout:** 300s per problem
- **Termination:** Success OR budget exhausted OR timeout

### FR4: Evaluation Harness
**Description:** Batch evaluation on miniF2F test set  
**Infrastructure:** Reuse H-E1 setup
**Configuration:**
- 244 problems (miniF2F test split)
- 8 parallel workers
- Deterministic seeding per problem
- Per-problem JSONL logging

### FR5: Statistical Analysis
**Description:** Compare H-M3 vs H-E1 with statistical tests  
**Analysis:**
- Success rate + Wilson 95% CI
- One-sided z-test (H-M3 > H-E1)
- Stratification by problem source (optional)

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Deterministic RNG seeding (problem index)
- Exact rerun validation (10% subset match)
- Version pinning (Lean 4.15.0, mathlib cache)

### NFR2: Performance
- Evaluation runtime: <3h wall-clock (8 workers)
- Per-problem timeout: 300s
- Memory: 16GB per worker

### NFR3: Logging
- Per-problem JSONL (problem_id, outcome, tactics_used, tactic_sequence, wall_time)
- Aggregate YAML (success_rate, CI, delta, failure modes)
- Console progress reporting

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│  Random Mathlib Tactic Sampler              │
│                                             │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │ Tactic       │───▶│ Weighted RNG     │  │
│  │ Weights      │    │ Sampler          │  │
│  └──────────────┘    └──────────────────┘  │
│         │                      │            │
│         ▼                      ▼            │
│  ┌─────────────────────────────────────┐   │
│  │ Proof Search (budget=15)            │   │
│  │  for i in 1..15:                    │   │
│  │    tactic ← sample()                │   │
│  │    result ← apply(tactic, goal)     │   │
│  │    if solved: return proof          │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Evaluation Harness (H-E1 Infrastructure)   │
│  - miniF2F test (244 problems)              │
│  - Parallel workers (8)                     │
│  - Timeout (300s)                           │
│  - JSONL logging                            │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Statistical Analysis (Python)              │
│  - Wilson CI                                │
│  - One-proportion z-test                    │
│  - Stratification                           │
└─────────────────────────────────────────────┘
```

### Key Files
- `random_mathlib_sampler.lean` — Tactic sampler + proof search
- `evaluate_h_m3.lean` — Batch evaluation entry point
- `evaluate_h_m3.sh` — Shell wrapper (build + run + analyze)
- `analyze_h_m3.py` — Statistical post-processing
- `tactic_distribution.yaml` — Empirical weights

---

## Data Requirements

### Input Data
**Source:** miniF2F Lean 4 test set (google-deepmind/miniF2F)  
**Size:** 244 problems  
**Preprocessing:** None (reuse H-E1 setup)  
**Splits:** Test only (no validation needed)

### Output Data
**Per-problem results** (`h_m3_results.jsonl`):
```json
{
  "problemId": "minif2f_test_001",
  "source": "AMC",
  "outcome": "solved",
  "tacticsUsed": 8,
  "tacticSequence": ["simp", "intro", "rfl", ...],
  "wallTime": 12.3,
  "seed": 0
}
```

**Aggregate statistics** (`h_m3_aggregate.yaml`):
```yaml
h_m3_results:
  success_rate: 0.20
  ci_95: [0.153, 0.255]
  solved_count: 49
  delta_vs_lean_auto:
    value: 0.044
    z_statistic: 2.13
    p_value: 0.017
    significant: true
```

---

## Dependencies & Infrastructure

### Reused from H-E1
- miniF2F repository (cloned, built, mathlib cached)
- Lean 4.15.0 toolchain
- Parallel evaluation harness (8 workers, 300s timeout)
- JSONL logging format

### New Dependencies
- Python 3.10+ (scipy, statsmodels, numpy)
- Random number generator (Lean StdGen)
- Tactic distribution weights (empirical from literature)

---

## Comparison Baseline

### H-E1 Results
- **Success rate:** 15.6% [11.5%, 20.3%]
- **Solved count:** 38/244
- **Tactic count:** mean=9.2±4.1, median=7.0

### Statistical Test
- **Null hypothesis:** H-M3 success rate = H-E1 success rate (15.6%)
- **Alternative:** H-M3 > H-E1 (one-sided)
- **Test:** One-proportion z-test
- **Significance:** α = 0.05

---

## Falsification Criteria

### REJECT Hypothesis IF:
1. Success rate < 15% (no corpus benefit)
2. Success rate > 30% (corpus contribution >> predicted)
3. Δ not statistically significant (p > 0.05)

### PASS Hypothesis IF:
1. Success rate ∈ [18%, 25%]
2. Δ ∈ [3%, 10%] percentage points
3. p < 0.05 (statistically significant)

---

## Risks & Mitigations

### Risk 1: Corpus Bias Acknowledged
**Probability:** 60%  
**Impact:** Random sampling from human proofs ≠ uniform distribution  
**Mitigation:** Use as third baseline for triangulation; acknowledge in caveats

### Risk 2: Variance from Randomness
**Probability:** 40%  
**Impact:** High variance in solve paths  
**Mitigation:** Deterministic seeding, rerun validation, report CI

### Risk 3: Budget Sensitivity
**Probability:** 30%  
**Impact:** 15-evaluation budget may be suboptimal  
**Mitigation:** Budget from H-E1 measurement (mean=9.2, recommend=15)

---

## Timeline

**Total Duration:** 4 days

**Breakdown:**
- **Day 1:** Tactic distribution extraction + validation (4h)
- **Day 2:** Random sampler implementation (6h)
- **Day 3:** Evaluation run (2.5h wall-clock)
- **Day 4:** Statistical analysis + report (4h)

**Parallel Work:** Can run alongside H-M1, H-M2 (independent)

---

## Deliverables

### Code Artifacts
1. `random_mathlib_sampler.lean` (tactic distribution + proof search)
2. `evaluate_h_m3.lean` (batch evaluation)
3. `evaluate_h_m3.sh` (shell wrapper)
4. `analyze_h_m3.py` (statistical analysis)
5. `tactic_distribution.yaml` (empirical weights)

### Data Artifacts
1. `h_m3_results.jsonl` (per-problem results)
2. `h_m3_aggregate.yaml` (aggregate statistics)
3. `h_m3_stratification.csv` (by source, optional)

### Documentation
1. `04_validation.md` (Phase 4 validation report)
2. `implementation_notes.md` (rationale)
3. `comparison_analysis.ipynb` (visualization)

---

## Acceptance Criteria

### Minimum Viable Product
- ✅ Random sampler produces proofs for ≥18% of miniF2F
- ✅ Δ vs lean-auto ≥ 3 percentage points
- ✅ Statistical significance p < 0.05
- ✅ Deterministic reproducibility (10% subset match)

### Quality Gates
- Error rate < 5%
- Infrastructure stable (no crashes)
- Results logged in JSONL + YAML

---

## Out of Scope

### Explicitly NOT Included
- ❌ Premise selection (zero-shot only)
- ❌ Goal prioritization (random selection)
- ❌ Tactic arguments (default arguments only)
- ❌ Multi-tactic sequences (single tactic per evaluation)
- ❌ Adaptive sampling (fixed distribution)

---

## References

### Primary Sources
- **miniF2F Benchmark:** Zheng et al. (2021) - arXiv:2109.00110
- **lean-auto Prover:** Qian et al. (2025) - leanprover-community/lean-auto
- **Tidy Baseline:** Han et al. (2021 PACT) - Section 4.2.1

### Implementation Guides
- **LeanDojo:** Yang & Song (2023) - Tactic statistics
- **Structured Hints:** arXiv:2601.16172 - Tactic skeleton schedules
- **Mathlib4:** leanprover-community/mathlib4

### Prior Work
- **H-E1 Results:** verification_state.yaml
- **Phase 2C Design:** 02c_experiment_brief.md

---

**PRD Complete — Ready for Architecture & Logic Design**
