# Phase 2C: Experiment Brief
# Hypothesis H-E1: lean-auto Baseline Measurement

**Generated**: 2026-08-20  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK (foundation for all comparisons)  
**Archon Task ID**: b1cf534c-c7ff-48e5-a432-1d260d9ec129

---

## Executive Summary

Measure pure automated theorem prover (lean-auto) baseline success rate on miniF2F Lean 4 subset to establish foundation for mechanistic comparison. Target: 10-25% success rate, full test set evaluation (N=244 problems).

**Key Design Decision**: Use complete miniF2F-Lean4 test set (244 problems) with standard 300s timeout to match established baselines in literature and avoid statistically meaningless small-sample evaluations.

---

## 1. Research Question

**Primary**: What is lean-auto's baseline success rate on miniF2F Lean 4 olympiad-level formal mathematics problems?

**Secondary**: 
- What is the tactic evaluation count distribution per problem?
- What is the time-to-solution distribution for solved problems?
- Are there difficulty strata (AMC/AIME/IMO) performance differences?

---

## 2. Hypothesis Statement

**H-E1**: Pure automated prover (lean-auto) achieves 10-25% baseline success on miniF2F Lean 4 subset

**Predicted Outcome**: 15% ± 5% success rate (37 ± 12 problems solved out of 244)

**Falsification Criteria**:
- IF success < 10% (< 24 problems): Baseline too weak for meaningful comparison
- IF success > 25% (> 61 problems): Revise predicted LLM gap estimate

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Name**: miniF2F Lean 4 Test Set  
**Type**: standard  
**Source**: google-deepmind/miniF2F fork (Lean 4 port)  
**Repository**: https://github.com/google-deepmind/miniF2F  
**Version**: AlphaProof evaluation version (fully verified, no misformalizations)

**Sample Size**: 244 problems (full test set)

**Rationale for Full Test Set**:
1. **Statistical Power**: Full set (N=244) provides sufficient power to detect 10-25% success rate with 95% confidence intervals ±3-4%
2. **Literature Alignment**: Matches evaluation protocol from lean-auto paper (Mathlib4 evaluation), miniF2F-v2 studies, and AlphaProof benchmark
3. **Avoids Synthetic Data**: Real olympiad problems (AMC, AIME, IMO sources) vs synthetic/simulated datasets
4. **Standard Benchmark**: Widely-used baseline in automated theorem proving literature (2021-2026)

### 3.2 Dataset Characteristics

**Problem Sources**:
- AMC (American Mathematics Competition): ~30% problems
- AIME (American Invitational Mathematics Exam): ~40% problems  
- IMO (International Mathematical Olympiad): ~30% problems

**Difficulty Distribution**:
- AMC: High-school level, often informal language hints
- AIME: Advanced high-school, moderate proof depth
- IMO: Olympiad level, complex multi-step proofs

**Formal Properties**:
- All problems verified against Lean 4.15.0+ kernel
- All statements provable (16 unprovable statements from v1 fixed in current version)
- Natural language docstrings included for context
- Full mathlib imports available

### 3.3 Data Splits

**Test Set Only**: 244 problems (held-out evaluation)

**Validation Set**: Available (244 problems) but not used in this experiment (reserved for ablation studies H-M1, H-M2, H-M3)

**Rationale**: Existence baseline requires test set only; mechanism studies will use validation set to avoid contamination.

### 3.4 Preprocessing Requirements

**Infrastructure Setup**:
1. Clone google-deepmind/miniF2F repository
2. Checkout AlphaProof evaluation version (post-v2 corrections)
3. Verify Lean 4 toolchain compatibility (v4.15.0+)
4. Build mathlib dependencies (lake build)

**Problem Loading**:
- Parse `Minif2f/Test.lean` for theorem statements
- Extract 244 theorem names and formal statements
- No premise selection (use only statements, no imported theorems as hints)

**Excluded Problems**: None (all 244 problems included)

**Stratification Metadata** (optional, for secondary analysis):
- Problem source (AMC/AIME/IMO) extracted from filename or docstring
- Proof depth (tactic count) measured post-hoc from lean-auto logs
- Timeout status (solved vs timeout vs error)

---

## 4. Baseline Configuration

### 4.1 Tool Configuration

**Prover**: lean-auto v1.0+ (leanprover-community/lean-auto)  
**Lean Version**: 4.15.0 (matches miniF2F compatibility)  
**ATP Backend**: Default configuration (auto tactic)

**lean-auto Settings**:
```lean
set_option auto.smt false      -- No SMT solver (pure ATP only)
set_option auto.tptp false     -- No TPTP solver (baseline measurement)
set_option auto.native true    -- Use Duper for proof reconstruction
```

**Premise Selection**: None (zero-shot, no imported theorems as hints)

**Rationale**: Measure pure automated prover baseline without LLM guidance, premise selection, or manual hints.

### 4.2 Resource Constraints

**Timeout**: 300s per problem  
**Tactic Budget**: Unlimited (measured, not constrained)  
**Memory**: 16GB per worker  
**CPU**: 8 cores per worker  
**Parallelization**: 8 concurrent workers (total 64 cores)

**Rationale**: 300s timeout matches lean-auto Mathlib4 evaluation (10s per theorem) scaled for harder olympiad problems. Literature uses 300s-600s for miniF2F evaluations.

### 4.3 Success Criteria

**Solved**: lean-auto produces verified proof within 300s timeout  
**Timeout**: No proof found within 300s  
**Error**: Type-checking failure, ATP crash, or infrastructure error

**Proof Verification**: All proofs checked by Lean 4 kernel (no admitted lemmas)

---

## 5. Measurement Protocol

### 5.1 Execution Pipeline

```
For each problem P in miniF2F test set (N=244):
  1. Load theorem statement from Test.lean
  2. Create isolated Lean environment (no cross-contamination)
  3. Invoke lean-auto tactic with 300s timeout
  4. Log outcome: {solved, timeout, error}
  5. If solved:
     - Record wall-clock time
     - Extract tactic evaluation count from ATP logs
     - Verify proof with Lean kernel
  6. If timeout/error:
     - Record failure mode
```

**Parallelization**: 8 workers × 30 problems each (244 total, 1 worker handles 34)

**Estimated Runtime**: 
- Best case: 244 problems × 300s ÷ 8 workers = 2.5 hours
- Worst case (all timeout): 244 × 300s ÷ 8 = 2.5 hours
- Expected (15% solve early): ~2 hours

### 5.2 Logging Requirements

**Per-Problem Log**:
- Problem ID (miniF2F test set index)
- Problem source (AMC/AIME/IMO, if available)
- Outcome (solved/timeout/error)
- Wall-clock time (seconds)
- Tactic evaluation count (from lean-auto debug logs)
- Proof term size (characters, if solved)
- ATP backend used (Duper/Z3/CVC5/Zipperposition)

**Aggregate Log**:
- Success rate (% solved)
- Mean/median solve time (for solved problems)
- Mean/median tactic count (for solved problems)
- Timeout distribution (300s ceiling effects)
- Error rate and failure modes

### 5.3 Instrumentation

**lean-auto Logging**:
```lean
set_option trace.auto true       -- Enable debug traces
set_option trace.auto.mono true  -- Log monomorphization steps
```

**Tactic Count Extraction**:
- Parse lean-auto trace logs for ATP solver invocations
- Count tactic evaluation calls (not just final proof tactics)
- Measure search depth (not just proof term depth)

**Alternative Fallback** (if trace logs insufficient):
- Use wall-clock time as proxy (timeout = 10 tactic budget equivalent)
- Measure proof term size (lines of generated proof script)

---

## 6. Expected Outcomes

### 6.1 Primary Metric

**Success Rate**: 15% ± 5% (predicted range: 10-25%)

**Distribution**:
- Solved: 37 problems (15% of 244)
- Timeout: 200 problems (82%)
- Error: 7 problems (3%)

**Confidence Interval**: 95% CI for 15% success at N=244 is ±4.5% (10.5%-19.5%)

### 6.2 Secondary Metrics

**Tactic Evaluation Count**:
- Mean: 8-12 evaluations per solved problem
- Median: 6-10 evaluations
- Range: 1-50 evaluations
- Use for H-C1 (tactic budget equalization)

**Solve Time Distribution**:
- Fast solves (< 10s): 20% of solved problems
- Medium solves (10-60s): 50% of solved problems
- Slow solves (60-300s): 30% of solved problems

**Stratification by Source** (if metadata available):
- AMC: 18-22% success (easier, more NL hints)
- AIME: 12-16% success (moderate difficulty)
- IMO: 8-12% success (hardest, minimal hints)

### 6.3 Failure Mode Analysis

**Expected Timeout Patterns**:
- Deep proofs (> 10 tactics): 90% timeout rate
- Proofs requiring NL hint understanding: 95% timeout rate
- Proofs with large search space: 85% timeout rate

**Error Sources**:
- Type-checking failures: 1-2%
- ATP crashes: 1-2%
- Infrastructure timeouts: < 1%

---

## 7. Comparison Baselines

### 7.1 Literature Baselines

**lean-auto on Mathlib4** (from paper):
- 36.6% success rate with Duper backend
- 10s timeout per theorem
- Ideal premise selection (human proof theorems provided)

**Adjustment for miniF2F**:
- Harder problems (olympiad vs library theorems)
- No premise selection (zero-shot)
- Longer timeout (300s vs 10s)
- Expected: 15% vs 36.6% (0.41× harder task)

**Other Tools on miniF2F** (from literature):
- Aesop: 31.6% on Mathlib4 (not miniF2F-specific baseline)
- Simp_all: ~25% on Mathlib4
- Rfl: ~5% on simple goals

**Expected Ranking**: Rfl < lean-auto < Simp_all < Aesop (for miniF2F)

### 7.2 Internal Consistency Checks

**Pilot Run** (N=20 problems, pre-experiment validation):
- Run lean-auto on 20 random miniF2F problems
- Verify infrastructure (no crashes, logs captured)
- Sanity check: 2-5 solves expected (10-25% of 20)

**Cross-Validation**:
- Compare lean-auto results with published miniF2F-v2 baselines
- Expected correlation: r > 0.7 with Deepseek-Prover-V2 solve sets (different tools, same hard problems)

---

## 8. Statistical Analysis Plan

### 8.1 Primary Analysis

**Success Rate Estimation**:
- Point estimate: # solved / 244
- 95% CI: Wilson score interval (better for proportions near boundaries)
- Report: 15% [10.5%, 19.5%] (example)

**Hypothesis Test**:
- H0: Success rate = 15%
- H1: Success rate ≠ 15%
- α = 0.05, two-tailed binomial test
- Reject H0 if p < 0.05

### 8.2 Secondary Analyses

**Tactic Count Distribution**:
- Mean ± SD (for H-C1 budget setting)
- Median [IQR] (robust to outliers)
- Coefficient of variation (CV = SD/Mean)
- Use median if CV > 50% (high variance)

**Stratification by Source** (if metadata available):
- Chi-square test for AMC vs AIME vs IMO success rates
- Bonferroni correction for multiple comparisons (α = 0.05/3 = 0.017)
- Report effect size: odds ratio AMC/IMO

**Solve Time Analysis**:
- Kaplan-Meier curve (survival analysis, 300s censoring)
- Median time-to-solution with 95% CI
- Identify fast-solve vs hard-solve clusters

### 8.3 Sensitivity Analysis

**Timeout Variation**:
- Rerun subset (N=50) with 600s timeout
- Check if success rate increases (ceiling effect diagnosis)
- If 600s success ≫ 300s success: timeout too aggressive

**Premise Selection Ablation** (exploratory):
- Rerun subset (N=50) with ideal premise selection (human proof theorems)
- Compare with zero-shot baseline
- Expected: 2-3× improvement with premises (literature analog)

---

## 9. Data Management

### 9.1 Data Storage

**Raw Logs**: `/data/h-e1/raw_logs/`
- Per-problem logs: `problem_<id>_log.txt`
- ATP traces: `problem_<id>_trace.json`
- Proof terms: `problem_<id>_proof.lean` (if solved)

**Aggregated Results**: `/data/h-e1/results.csv`

| problem_id | source | outcome | time_s | tactic_count | proof_size | atp_backend |
|------------|--------|---------|--------|--------------|------------|-------------|
| test_001   | AMC    | solved  | 12.3   | 8            | 156        | Duper       |
| test_002   | AIME   | timeout | 300.0  | -            | -          | -           |

**Summary Statistics**: `/data/h-e1/summary.json`
```json
{
  "success_rate": 0.15,
  "ci_95": [0.105, 0.195],
  "solved_count": 37,
  "timeout_count": 200,
  "error_count": 7,
  "mean_tactic_count": 9.2,
  "median_tactic_count": 7.0,
  "tactic_count_cv": 0.48
}
```

### 9.2 Version Control

**Code**: Git repository with experiment harness  
**Data**: DVC for large log files  
**Results**: Committed to repo (small CSV/JSON)

**Reproducibility Requirements**:
- Lean version: 4.15.0 (pinned)
- lean-auto version: git SHA or release tag
- miniF2F version: git SHA (AlphaProof fork)
- Random seed: Not applicable (deterministic evaluation)

---

## 10. Risk Assessment

### 10.1 Technical Risks

**R1: Infrastructure Failures**
- **Probability**: 20%
- **Impact**: Medium (delay 1-2 days)
- **Mitigation**: Pilot run on N=20, checkpoint every 50 problems
- **Fallback**: Rerun failed problems individually

**R2: lean-auto Compatibility Issues**
- **Probability**: 30%
- **Impact**: High (blocks entire experiment)
- **Mitigation**: Test lean-auto on 5 miniF2F problems before full run
- **Fallback**: Use alternative ATP (Aesop) if lean-auto incompatible

**R3: Timeout Too Aggressive**
- **Probability**: 40%
- **Impact**: Low (expected behavior, measured in sensitivity analysis)
- **Mitigation**: Run 600s timeout on subset to diagnose
- **Accepted Risk**: 300s is literature standard, comparable to baselines

### 10.2 Statistical Risks

**R4: Success Rate Outside 10-25% Range**
- **Probability**: 30%
- **Impact**: Medium (requires hypothesis revision)
- **Mitigation**: Report actual rate, revise H-M1/H-M2/H-M3 predictions
- **Decision Rule**: 
  - If < 10%: Flag weak baseline, consider alternative comparison
  - If > 25%: Revise LLM gap estimate, tighten mechanistic claims

**R5: High Tactic Count Variance (CV > 100%)**
- **Probability**: 50%
- **Impact**: Medium (affects H-C1 budget setting)
- **Mitigation**: Use median instead of mean for budget
- **Fallback**: Report variance as caveat in H-C1 fairness metric

### 10.3 Data Quality Risks

**R6: Missing Stratification Metadata**
- **Probability**: 60%
- **Impact**: Low (aggregate results still valid)
- **Mitigation**: Extract source from filenames/docstrings
- **Fallback**: Report aggregate results only, skip stratification

**R7: ATP Backend Inconsistency**
- **Probability**: 20%
- **Impact**: Low (measured post-hoc)
- **Mitigation**: Log which ATP backend solved each problem
- **Analysis**: Report backend distribution (Duper vs Z3 vs CVC5)

---

## 11. Timeline

### 11.1 Implementation (5 days)

**Day 1-2**: Infrastructure Setup
- Clone miniF2F, build mathlib
- Install lean-auto, verify compatibility
- Pilot run on N=20 problems

**Day 3**: Experiment Harness
- Parallelize 8 workers
- Implement logging and checkpointing
- Test on N=50 problems

**Day 4**: Full Evaluation
- Run all 244 problems (2.5 hours)
- Monitor for errors, restart failed workers
- Verify all logs captured

**Day 5**: Data Analysis
- Aggregate results, compute statistics
- Generate summary.json and results.csv
- Plot distributions (success rate, solve time, tactic count)

### 11.2 Reporting (2 days)

**Day 6**: Results Write-Up
- Draft experimental report
- Include plots and tables
- Document failure modes

**Day 7**: Review and Finalize
- Peer review of methodology
- Verify reproducibility checklist
- Commit data and code

**Total**: 7 days (1 week)

---

## 12. Success Criteria

### 12.1 Experiment Completion

- [ ] All 244 problems evaluated (no missing data)
- [ ] Success rate measured with 95% CI
- [ ] Tactic count distribution captured
- [ ] Failure modes documented

### 12.2 Quality Gates

- [ ] Error rate < 5% (infrastructure stability)
- [ ] Pilot run validates infrastructure (N=20, 2-5 solves)
- [ ] Results reproducible (rerun 10% subset, 100% match)
- [ ] Logs capture all required metadata

### 12.3 Hypothesis Validation

- [ ] Success rate in 10-25% range (baseline foundation valid)
- [ ] Tactic count CV < 100% (budget setting feasible for H-C1)
- [ ] No systematic bias (stratification analysis, if metadata available)

**Gate Decision**:
- **PASS** if success rate 10-25%, error < 5%, tactic count CV < 100%
- **REVISE** if success rate outside range (update H-M1/M2/M3 predictions)
- **FAIL** if error > 10% or infrastructure unstable (fix before proceeding)

---

## 13. Integration with Broader Pipeline

### 13.1 Dependencies

**Upstream** (Phase 2B): Verification plan complete, hypothesis h-e1 ready

**Downstream** (Phase 3-4):
- **H-C1**: Tactic budget setting (uses mean/median from this experiment)
- **H-M3**: Random Mathlib baseline comparison (uses h-e1 success rate)
- **Phase 5**: LLM vs lean-auto comparison (uses h-e1 as baseline)

### 13.2 Outputs for Phase 3

**Experiment Specification** (this document):
- Dataset: miniF2F Lean 4 test set (N=244)
- Configuration: lean-auto, 300s timeout, zero-shot
- Metrics: success rate, tactic count, solve time

**Data Products**:
- results.csv (per-problem outcomes)
- summary.json (aggregate statistics)
- Raw logs (for debugging and reanalysis)

**Key Findings for PRD**:
- Baseline success rate: 15% [10.5%, 19.5%] (example)
- Mean tactic count: 9.2 ± 4.4 (for H-C1 budget)
- Failure modes: timeout dominant (82%), deep proofs hardest

---

## 14. References

### 14.1 Literature

1. **lean-auto Paper**: Qian et al. (2025), "Lean-Auto: An Interface Between Lean 4 and Automated Theorem Provers" - 36.6% success on Mathlib4 with ideal premises
2. **miniF2F Benchmark**: Zheng et al. (2021), "MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics" - 244 test problems, AMC/AIME/IMO sources
3. **miniF2F-v2 Corrections**: Roozbeh et al. (2026), "miniF2F-Lean Revisited" - Fixed 16 unprovable statements, verified all formal/informal alignment
4. **AlphaProof Evaluation**: DeepMind (2024), google-deepmind/miniF2F fork - Used for AlphaProof benchmark, fully verified Lean 4 port
5. **Automated Theorem Proving Baselines**: 
   - Deepseek-Prover-V2: 69% on miniF2F-v2 (with premise selection)
   - Goedel-Prover-V2: 62% on miniF2F-v2c
   - Kimina-Prover-Distill: 58% on miniF2F-v2

### 14.2 Datasets

- **miniF2F Repository**: https://github.com/google-deepmind/miniF2F
- **Lean 4 Port**: AlphaProof evaluation version (post-v2 corrections)
- **Problem Count**: 244 test + 244 validation
- **Formal Verification**: Lean 4.15.0+, mathlib compatible

### 14.3 Tools

- **lean-auto**: https://github.com/leanprover-community/lean-auto
- **Lean 4**: leanprover/lean4 v4.15.0
- **Duper**: https://github.com/leanprover-community/duper (proof reconstruction)
- **ATP Backends**: Z3, CVC5, Zipperposition (optional, not used in baseline)

---

## Appendix A: Experiment Configuration File

```yaml
# h-e1_config.yaml
experiment:
  id: h-e1
  name: "lean-auto Baseline Measurement"
  hypothesis: "Pure automated prover achieves 10-25% success on miniF2F Lean 4"
  
dataset:
  name: miniF2F-Lean4-Test
  source: google-deepmind/miniF2F
  version: alphaproof-eval
  split: test
  size: 244
  
prover:
  tool: lean-auto
  version: ">=1.0"
  lean_version: "4.15.0"
  options:
    auto.smt: false
    auto.tptp: false
    auto.native: true
    trace.auto: true
    
resources:
  timeout: 300  # seconds
  memory: 16384  # MB
  workers: 8
  
logging:
  raw_logs: /data/h-e1/raw_logs/
  results: /data/h-e1/results.csv
  summary: /data/h-e1/summary.json
  
metrics:
  primary: success_rate
  secondary:
    - tactic_count
    - solve_time
    - failure_modes
```

---

**Phase 2C Experiment Brief Complete**  
**Status**: READY for Phase 3 (Implementation Planning)  
**Next Step**: Generate PRD and Architecture specification for evaluation harness
