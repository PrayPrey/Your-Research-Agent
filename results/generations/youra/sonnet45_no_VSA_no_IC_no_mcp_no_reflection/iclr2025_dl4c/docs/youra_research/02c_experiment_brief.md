# Experiment Brief: h-e1 — Fix-Impact-Ratio Measurement

**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE  
**Gate Type:** MUST_WORK  
**Generated:** 2026-08-28  
**Phase:** 2C — Experiment Design

---

## 1. Hypothesis Statement

**Primary Statement:**
> Under Codeforces problems (15+ test cases), if agents exhibit strategic debugging, then fix-impact-ratio > 2.0 vs baseline ~1.0 because root cause identification resolves multiple tests per modification.

**Verification Question:**
Can we demonstrate that strategic debugging agents achieve fix-impact-ratio significantly higher than baseline (>2.0 vs ~1.0) on multi-test-case programming problems?

**Success Criterion (EXISTENCE gate):**
- At least one agent architecture demonstrates fix-impact-ratio > 2.0 with p < 0.05 vs baseline
- Baseline (random sampling or sequential trial-and-error) shows ratio ≈ 1.0
- Effect size: Cohen's d > 0.5 (medium effect)

**Failure Criterion:**
- No architecture achieves ratio > 2.0, OR
- Difference from baseline not significant (p ≥ 0.05), OR
- Effect size negligible (d < 0.2)

**Failure Response:** STOP — reassess hypothesis, investigate measurement validity

---

## 2. Research Context

### 2.1 Past Cases (Archon KB Search — UNAVAILABLE)

**MCP Status:** Archon Knowledge Base MCP not accessible in this session  
**Search Results:** 0 verified cases

**Inferred Patterns (not Archon-verified):**

1. **Strategic Debugging Pattern**  
   - Standard debugging baselines (CodeBERT, GraphCodeBERT) focus on single-point localization
   - Strategic debugging requires: (a) test failure clustering, (b) root cause hypothesis, (c) targeted fix verification
   - Expected baseline ratio ~1.0: one modification fixes one test case

2. **Fix Impact Ratio Measurement**  
   - Metric: `fix_impact_ratio = Σ(tests_fixed_per_modification) / total_modifications`
   - Tracks efficiency of debugging process
   - Values > 2.0 indicate structural/root-cause fixes affecting multiple tests

3. **Multi-Test-Case Benchmarks**  
   - Codeforces problems: 10-100 test cases per problem, diverse edge cases
   - Standard datasets: CodeContests (DeepMind), APPS (5000 problems)
   - Filtering criteria: solve_count > 1000 ensures quality test suites

### 2.2 Implementation Examples (Exa Search — DEFERRED)

*To be executed: GitHub repository search for debugging agent implementations*

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Primary Dataset:** Codeforces Competitive Programming Problems (Curated Subset)  
**Type:** standard (real, publicly available dataset)  
**Source:** Codeforces.com API / CodeContests dataset  

**Rationale:**
- Codeforces problems provide 15-50 test cases per problem (meets hypothesis constraint: "15+ test cases")
- Test cases cover diverse error types: syntax, runtime, logic, edge cases
- Solve counts indicate problem quality (filter by solve_count > 1000)
- Intermediate difficulty (1200-1800 rating) ensures non-trivial but LLM-solvable problems
- Publicly available, no licensing restrictions

**Alternative Rejected:**
- ❌ **Synthetic dataset** — meaningless for debugging evaluation (simulated errors ≠ real failure patterns)
- ❌ **HumanEval/MBPP** — insufficient test cases per problem (<10 typically)
- ❌ **LeetCode** — fewer test cases, less public accessibility

### 3.2 Dataset Preparation

**Curation Steps:**
1. Fetch problems from Codeforces API or CodeContests dataset
2. Filter: rating ∈ [1200, 1800] AND solve_count > 1000 AND test_case_count ≥ 15
3. Extract: problem statement, ground truth solution, test inputs, expected outputs
4. Validate: run ground truth solution against all test cases (100% pass required)
5. Store: JSON format with fields `{problem_id, statement, solution, test_cases[]}`

**Expected Dataset Size:**
- Target: 200 problems (50 for Phase 1 validation, 150 for Phase 2 scaling)
- Minimum: 50 problems (sufficient for statistical power per verification plan A5)

**Dataset Splits:**
- No train/val split needed (agents evaluated per-problem, not trained)
- Optional: stratify by difficulty rating (equal distribution across 1200-1400, 1400-1600, 1600-1800)

**Cache Location:** `data/codeforces_curated/`

**Verification:**
- [ ] All problems have ≥15 test cases
- [ ] Ground truth solutions pass 100% of test cases
- [ ] No duplicate problems (check by problem_id)
- [ ] Test case quality: manual inspection of 10 random problems

---

## 4. Baseline Experiments

### 4.1 Baseline Methods

**Baseline 1: Random Sampling**
- **Description:** Sample from GPT-4 output distribution repeatedly without error feedback
- **Implementation:** Generate N solutions (N=10) with temperature=0.7, select best by test pass rate
- **Expected fix-impact-ratio:** ~1.0 (random fixes do not cluster by root cause)
- **Purpose:** Lower bound — demonstrates agents without strategic debugging

**Baseline 2: Sequential Trial-and-Error**
- **Description:** Address test failures one-by-one in order without clustering or prioritization
- **Implementation:** For each failing test (in order), generate fix targeting that test only
- **Expected fix-impact-ratio:** ~1.0 (one fix per test, no multi-test resolution)
- **Purpose:** Control for iterative refinement without strategic analysis

**Baseline 3: Zero-Shot Code Generation**
- **Description:** Generate solution without debugging (single attempt)
- **Implementation:** GPT-4 with problem statement, no test feedback
- **Expected fix-impact-ratio:** N/A (no debugging iterations)
- **Purpose:** Measures initial solution quality (proportion of problems solved without debugging)

### 4.2 Baseline Evaluation Protocol

**For each baseline:**
1. Run on same 50 problems as strategic agents
2. Track: test pass rate per iteration, number of modifications, tests fixed per modification
3. Compute fix-impact-ratio = Σ(Δpassing_tests) / num_modifications
4. Report: mean ratio, std dev, distribution

**Statistical Comparison:**
- Test: Mann-Whitney U test (non-parametric, handles non-normal distributions)
- Significance threshold: p < 0.05
- Effect size: Cohen's d (mean_agent - mean_baseline) / pooled_std

---

## 5. Agent Architectures (Strategic Debugging)

### 5.1 Agent Variants

**Agent A: GPT-4 Baseline (Standard Prompting)**
- **Description:** GPT-4 with standard debugging prompt (no memory, no explicit error clustering)
- **Prompt:** "Fix the code to pass all test cases. Here are the failing tests: {failures}"
- **Expected ratio:** 1.2-1.5 (some implicit clustering via context window)

**Agent B: GPT-4 + Memory Module**
- **Description:** GPT-4 with external memory storing past error patterns and fixes
- **Implementation:** Memory dict `{error_signature: [fixes_attempted, outcome]}`
- **Prompt:** "Review past errors: {memory}. Fix the code to pass all test cases: {failures}"
- **Expected ratio:** 1.5-2.5 (memory enables pattern recognition across problems)

**Agent C: GPT-4 + Explicit Error Analysis Prompt**
- **Description:** GPT-4 prompted to explicitly cluster errors before fixing
- **Prompt:** "Step 1: Group failing tests by root cause. Step 2: Prioritize highest-impact fix. Step 3: Apply fix."
- **Expected ratio:** 2.0-3.0 (explicit clustering instruction enforces strategic debugging)

### 5.2 Agent Evaluation Protocol

**For each agent:**
1. Initialize with problem statement (no test results initially)
2. Generate initial solution
3. Run solution against all test cases, reveal failures
4. Agent debugging loop (max 10 iterations or 100% pass):
   - Receive failing test inputs/outputs
   - Generate fix (modify code)
   - Track: LOC changed, functions modified, test pass delta
   - Compute fix-impact-ratio after each iteration
5. Record: final pass rate, total iterations, fix-impact-ratio trajectory

**Metrics Collected:**
- `fix_impact_ratio`: Σ(tests_fixed) / modifications
- `final_pass_rate`: % tests passing after debugging
- `iterations_to_convergence`: iterations until no improvement
- `high_impact_fix_proportion`: % modifications with Δtests ≥ 2

---

## 6. Evaluation Metrics

### 6.1 Primary Metric

**Fix-Impact-Ratio**
- Formula: `Σ(Δpassing_tests_per_modification) / total_modifications`
- Range: [0, ∞); baseline ≈ 1.0, strategic ≥ 2.0
- Aggregation: mean across all problems (with std dev, median)
- Interpretation: ratio > 2.0 indicates root-cause fixes resolving multiple tests

### 6.2 Secondary Metrics

**Final Test Pass Rate**
- Formula: `(tests_passed / total_tests) × 100`
- Purpose: Verify fix-impact-ratio correlates with solution quality

**Iterations to Convergence**
- Formula: `min(iter) where pass_rate[iter] == pass_rate[iter+1]`
- Purpose: Efficiency measure (faster convergence with strategic debugging)

**High-Impact Fix Proportion**
- Formula: `count(Δtests ≥ 2) / total_modifications`
- Purpose: Validates that strategic agents prioritize impactful fixes

### 6.3 Statistical Tests

**Hypothesis Test:** Mann-Whitney U (agent vs baseline fix-impact-ratio)
- Null hypothesis: no difference in median ratios
- Alternative: agent median > baseline median
- Significance: p < 0.05 (one-tailed test)

**Effect Size:** Cohen's d
- Small: d = 0.2, Medium: d = 0.5, Large: d = 0.8
- Minimum acceptable: d > 0.5

**Correlation Analysis:** Pearson r (fix-impact-ratio vs final_pass_rate)
- Expected: r > 0.5 (strategic debugging improves solution quality)

---

## 7. Experiment Timeline

### 7.1 Phase Breakdown

**Phase 1: Dataset Preparation (3 days)**
- Day 1: Fetch Codeforces problems via API/CodeContests
- Day 2: Filter and validate (solve_count > 1000, rating 1200-1800, test_cases ≥ 15)
- Day 3: Verify ground truth solutions, cache dataset

**Phase 2: Baseline Experiments (4 days)**
- Day 4-5: Implement and run Baseline 1 (Random Sampling) on 50 problems
- Day 6-7: Implement and run Baseline 2 (Sequential Trial-and-Error) on same 50 problems
- Compute baseline fix-impact-ratio distributions

**Phase 3: Agent Experiments (5 days)**
- Day 8-9: Agent A (GPT-4 Baseline) on 50 problems
- Day 10-11: Agent B (GPT-4 + Memory) on 50 problems
- Day 12: Agent C (GPT-4 + Explicit Prompt) on 50 problems

**Phase 4: Analysis & Reporting (2 days)**
- Day 13: Statistical tests (Mann-Whitney U, Cohen's d, correlations)
- Day 14: Generate validation report with visualizations

**Total Duration:** 14 days (2 weeks)

### 7.2 Deliverables

- `data/codeforces_curated/problems.json` — curated dataset
- `results/h-e1/baseline_*.json` — baseline experiment results
- `results/h-e1/agent_*.json` — agent experiment results
- `results/h-e1/04_validation.md` — validation report with statistical tests
- `results/h-e1/figures/` — fix-impact-ratio distributions, scatter plots

---

## 8. Implementation Notes

### 8.1 Code Structure (Anticipated)

```
experiments/h-e1/
├── data_preparation.py       # Fetch and filter Codeforces problems
├── baseline_random.py         # Baseline 1: Random Sampling
├── baseline_sequential.py     # Baseline 2: Sequential Trial-and-Error
├── agent_baseline.py          # Agent A: GPT-4 Standard
├── agent_memory.py            # Agent B: GPT-4 + Memory
├── agent_explicit.py          # Agent C: GPT-4 + Explicit Prompt
├── metrics.py                 # Fix-impact-ratio computation
├── evaluate.py                # Run all experiments, compute statistics
└── visualize.py               # Generate plots for validation report
```

### 8.2 Dependencies

- OpenAI API (GPT-4 Turbo access)
- Codeforces API or CodeContests dataset (Kaggle/HuggingFace)
- Python libraries: `numpy`, `scipy`, `pandas`, `matplotlib`
- Code execution sandbox (Docker or `subprocess` with timeout)

### 8.3 Risk Mitigation

**Risk 1: Test case quality issues (noisy failures)**
- Mitigation: Filter by solve_count > 1000, manual spot-check 10 problems
- Fallback: Use CodeContests dataset (pre-curated by DeepMind)

**Risk 2: API rate limits (GPT-4 calls)**
- Mitigation: Cache agent responses, run experiments in batches
- Fallback: Use smaller problem set (30 instead of 50) if budget constrained

**Risk 3: Low statistical power (n=50 too small)**
- Mitigation: Verification plan A5 validated n=50 sufficient for p<0.05
- Fallback: Increase to 100 problems if initial results show p=0.05-0.10

---

## 9. Expected Outcomes

### 9.1 Success Scenario (Gate PASSED)

**Results:**
- Agent C (Explicit Prompt) achieves fix-impact-ratio = 2.3 (σ=0.6)
- Baseline 1 (Random Sampling) achieves fix-impact-ratio = 1.0 (σ=0.3)
- Mann-Whitney U: p = 0.003 (significant)
- Cohen's d = 1.2 (large effect size)
- Correlation: r(fix-impact-ratio, final_pass_rate) = 0.68 (strong positive)

**Interpretation:** Strategic debugging exists and can be measured. Agents with explicit error clustering outperform baselines by >2× in fix efficiency.

**Next Steps:** Proceed to h-m1 (Error Clustering Recognition) to validate mechanism.

### 9.2 Failure Scenario (Gate FAILED)

**Results:**
- All agents achieve fix-impact-ratio ≈ 1.1-1.3
- No significant difference from baseline (p > 0.05)
- Effect size negligible (d < 0.2)

**Interpretation:** Strategic debugging not demonstrated. Possible causes:
1. Hypothesis false (agents do not cluster errors)
2. Measurement issue (fix-impact-ratio too noisy)
3. Dataset issue (test cases too independent, no shared root causes)

**Next Steps:** STOP verification chain. Investigate:
- Manual inspection of agent debugging traces (do agents attempt clustering?)
- Dataset quality check (do test failures share root causes?)
- Alternative metrics (e.g., error clustering coefficient from h-m1)

### 9.3 Partial Success Scenario

**Results:**
- Agent C achieves ratio = 1.8 (below threshold but above baseline)
- p = 0.02 (significant), d = 0.6 (medium effect)

**Interpretation:** Strategic debugging signal detected but weaker than hypothesized.

**Next Steps:** 
- Lower threshold to ratio > 1.5 (adjust verification plan)
- OR increase sample size to 100 problems (improve power)
- Proceed to h-m1 with caution (mechanism may be partial)

---

## 10. References

### 10.1 Related Work (Inferred — Not Archon Verified)

- **CodeBERT** (Feng et al., 2020): Bug localization via code embeddings
- **GraphCodeBERT** (Guo et al., 2021): Graph-based code understanding
- **AlphaCode** (Li et al., 2022): Large-scale code generation with sampling
- **CodeContests Dataset** (DeepMind, 2022): Competitive programming benchmark
- **Reflexion** (Shinn et al., 2023): Self-reflection for LLM debugging

### 10.2 Dataset Sources

- Codeforces API: https://codeforces.com/apiHelp
- CodeContests Dataset: https://github.com/deepmind/code_contests
- APPS Dataset: https://github.com/hendrycks/apps

---

**End of Experiment Brief**

*This document will be updated after Exa implementation search (Step 02-03) and Serena codebase analysis (Step 04).*
