# Product Requirements Document: Fix-Impact-Ratio Measurement System

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Generated:** 2026-08-28  
**Phase:** 3 — Implementation Planning

---

## Executive Summary

This PRD defines the requirements for implementing a system to measure fix-impact-ratio in strategic debugging agents. The system evaluates whether agents can achieve fix-impact-ratio > 2.0 (vs baseline ~1.0) on Codeforces competitive programming problems with 15+ test cases. Success demonstrates that strategic debugging (root cause identification + error clustering) exists and can be measured.

**Primary Goal:** Validate h-e1 by demonstrating at least one agent architecture achieves fix-impact-ratio > 2.0 with statistical significance (p < 0.05, Cohen's d > 0.5).

**Deliverables:**
1. Codeforces dataset curation pipeline (200 problems, 15+ test cases each)
2. Three baseline implementations (Random Sampling, Sequential Trial-and-Error, Zero-Shot)
3. Three agent implementations (GPT-4 Baseline, Memory Module, Explicit Prompting)
4. Metrics computation framework (fix-impact-ratio, pass rate, convergence)
5. Statistical analysis pipeline (Mann-Whitney U, Cohen's d, Pearson r)
6. Validation report with visualizations

---

## Problem Statement

### Background

Current debugging research focuses on single-point bug localization. Strategic debugging—where agents cluster errors by root cause and apply multi-test fixes—has not been rigorously measured. Fix-impact-ratio (tests fixed per modification) provides a quantitative metric for strategic debugging efficiency.

### Success Criteria

**MUST_WORK Gate Criteria:**
- ✅ At least one agent achieves fix-impact-ratio > 2.0 (mean across 50 problems)
- ✅ Baseline methods achieve ratio ≈ 1.0 (validating metric sensitivity)
- ✅ Statistical significance: p < 0.05 (Mann-Whitney U test, agent vs baseline)
- ✅ Effect size: Cohen's d > 0.5 (medium or larger)

**Failure Criteria:**
- ❌ No agent exceeds ratio 2.0
- ❌ p ≥ 0.05 (no significant difference from baseline)
- ❌ d < 0.2 (negligible effect size)

### Constraints

- **Sample Size:** Minimum 50 problems (Phase 1), target 200 problems (full dataset)
- **Test Case Requirement:** All problems must have ≥15 test cases
- **Model Access:** GPT-4 Turbo via OpenAI API
- **Timeline:** 14 days (2 weeks)
- **Compute:** Code execution sandbox (Docker or subprocess with timeout)

---

## Functional Requirements

### FR1: Dataset Curation Pipeline

**Description:** Fetch, filter, and validate Codeforces problems to create curated dataset.

**Inputs:**
- Codeforces API or CodeContests dataset (Kaggle/HuggingFace)

**Outputs:**
- `data/codeforces_curated/problems.json` with schema:
  ```json
  {
    "problem_id": "string",
    "statement": "string",
    "solution": "string (ground truth code)",
    "test_cases": [
      {"input": "string", "expected_output": "string"}
    ],
    "metadata": {
      "rating": "int",
      "solve_count": "int",
      "test_case_count": "int"
    }
  }
  ```

**Processing Steps:**
1. Fetch problems from source
2. Filter: rating ∈ [1200, 1800] AND solve_count > 1000 AND test_case_count ≥ 15
3. Extract: problem statement, ground truth solution, test inputs/outputs
4. Validate: run ground truth solution, verify 100% test pass
5. Save: JSON format to cache directory

**Acceptance Criteria:**
- ✅ All problems have ≥15 test cases
- ✅ Ground truth solutions pass 100% of test cases
- ✅ No duplicate problem_ids
- ✅ Manual inspection of 10 random problems confirms quality

---

### FR2: Baseline Implementation — Random Sampling

**Description:** Sample from GPT-4 output distribution without error feedback.

**Algorithm:**
1. Generate N=10 solutions with temperature=0.7
2. Run each solution against all test cases
3. Select solution with highest test pass rate
4. Track: modifications=N, tests_fixed=max(pass_count) - initial_pass_count

**Expected Behavior:**
- Fix-impact-ratio ≈ 1.0 (random fixes do not cluster by root cause)
- No iterative refinement

**Acceptance Criteria:**
- ✅ Runs on 50 problems
- ✅ Outputs fix-impact-ratio per problem
- ✅ Saves results to `results/h-e1/baseline_random.json`

---

### FR3: Baseline Implementation — Sequential Trial-and-Error

**Description:** Address test failures one-by-one in order without clustering.

**Algorithm:**
1. Generate initial solution
2. Run against all test cases
3. For each failing test (in order):
   - Prompt GPT-4: "Fix the code to pass test {i}: input={x}, expected={y}, got={z}"
   - Apply fix
   - Track: Δpassing_tests per modification
4. Repeat until 100% pass or max 10 iterations

**Expected Behavior:**
- Fix-impact-ratio ≈ 1.0 (one fix per test, no multi-test resolution)
- Iterative but not strategic

**Acceptance Criteria:**
- ✅ Runs on 50 problems
- ✅ Outputs fix-impact-ratio per problem
- ✅ Saves results to `results/h-e1/baseline_sequential.json`

---

### FR4: Baseline Implementation — Zero-Shot Code Generation

**Description:** Single-attempt code generation without debugging.

**Algorithm:**
1. Prompt GPT-4 with problem statement only (no test feedback)
2. Run solution against all test cases
3. Record pass rate (no modifications)

**Expected Behavior:**
- Fix-impact-ratio = N/A (no debugging iterations)
- Measures initial solution quality

**Acceptance Criteria:**
- ✅ Runs on 50 problems
- ✅ Outputs initial pass rate per problem
- ✅ Saves results to `results/h-e1/baseline_zeroshot.json`

---

### FR5: Agent Implementation — GPT-4 Baseline (Standard Prompting)

**Description:** GPT-4 with standard debugging prompt, no explicit clustering.

**Prompt Template:**
```
Fix the code to pass all test cases.
Problem: {statement}
Current code: {code}
Failing tests: {failures}
```

**Algorithm:**
1. Generate initial solution
2. Run against all test cases
3. If failures, pass failing tests to prompt
4. Generate fix
5. Track: Δpassing_tests per modification
6. Repeat until 100% pass or max 10 iterations

**Expected Behavior:**
- Fix-impact-ratio ≈ 1.2-1.5 (some implicit clustering via context window)

**Acceptance Criteria:**
- ✅ Runs on 50 problems
- ✅ Outputs fix-impact-ratio per problem
- ✅ Saves results to `results/h-e1/agent_baseline.json`

---

### FR6: Agent Implementation — GPT-4 + Memory Module

**Description:** GPT-4 with external memory storing past error patterns and fixes.

**Memory Schema:**
```python
{
  "error_signature": str,  # e.g., "IndexError at line 10"
  "fixes_attempted": List[str],
  "outcome": str  # "success" | "failure"
}
```

**Prompt Template:**
```
Review past errors and fixes from memory:
{memory}

Fix the code to pass all test cases.
Problem: {statement}
Current code: {code}
Failing tests: {failures}
```

**Algorithm:**
1. Initialize empty memory dict
2. Generate initial solution
3. On failure:
   - Extract error signatures from failing tests
   - Query memory for similar errors
   - Pass memory context to prompt
   - Generate fix
   - Update memory with outcome
4. Track: Δpassing_tests per modification
5. Repeat until 100% pass or max 10 iterations

**Expected Behavior:**
- Fix-impact-ratio ≈ 1.5-2.5 (memory enables pattern recognition)

**Acceptance Criteria:**
- ✅ Runs on 50 problems
- ✅ Outputs fix-impact-ratio per problem
- ✅ Saves results to `results/h-e1/agent_memory.json`
- ✅ Memory populated with error patterns

---

### FR7: Agent Implementation — GPT-4 + Explicit Error Analysis Prompt

**Description:** GPT-4 prompted to explicitly cluster errors before fixing.

**Prompt Template:**
```
Step 1: Group failing tests by root cause. Identify common error patterns.
Step 2: Prioritize the highest-impact fix (affects most tests).
Step 3: Apply the fix to resolve all tests in the prioritized cluster.

Problem: {statement}
Current code: {code}
Failing tests (with inputs/outputs): {failures}
```

**Algorithm:**
1. Generate initial solution
2. On failure:
   - Pass explicit clustering instruction to prompt
   - Request structured output: {clusters: [{root_cause, affected_tests, fix}]}
   - Apply highest-impact fix first
   - Track: Δpassing_tests per modification
3. Repeat until 100% pass or max 10 iterations

**Expected Behavior:**
- Fix-impact-ratio ≈ 2.0-3.0 (explicit clustering enforces strategic debugging)

**Acceptance Criteria:**
- ✅ Runs on 50 problems
- ✅ Outputs fix-impact-ratio per problem
- ✅ Saves results to `results/h-e1/agent_explicit.json`
- ✅ Agent outputs structured clustering analysis

---

### FR8: Metrics Computation Framework

**Description:** Compute fix-impact-ratio and secondary metrics per problem.

**Primary Metric:**
```python
fix_impact_ratio = sum(Δpassing_tests_per_modification) / total_modifications
```

**Secondary Metrics:**
- `final_pass_rate = (tests_passed / total_tests) × 100`
- `iterations_to_convergence = min(iter where pass_rate[iter] == pass_rate[iter+1])`
- `high_impact_fix_proportion = count(Δtests ≥ 2) / total_modifications`

**Aggregation:**
- Mean, std dev, median across all problems
- Per-agent distributions

**Acceptance Criteria:**
- ✅ Computes all metrics for each experiment run
- ✅ Saves aggregated results to JSON
- ✅ Handles edge cases (zero modifications, 100% initial pass)

---

### FR9: Statistical Analysis Pipeline

**Description:** Perform hypothesis tests comparing agents to baselines.

**Tests:**
1. **Mann-Whitney U Test** (agent vs baseline fix-impact-ratio)
   - Null hypothesis: no difference in median ratios
   - Alternative: agent median > baseline median
   - Significance: p < 0.05 (one-tailed)

2. **Cohen's d Effect Size**
   ```python
   d = (mean_agent - mean_baseline) / pooled_std
   ```
   - Small: d=0.2, Medium: d=0.5, Large: d=0.8
   - Minimum acceptable: d > 0.5

3. **Pearson Correlation** (fix-impact-ratio vs final_pass_rate)
   - Expected: r > 0.5 (strategic debugging improves solution quality)

**Acceptance Criteria:**
- ✅ Outputs p-value, effect size, correlation for all comparisons
- ✅ Includes confidence intervals
- ✅ Saves statistical summary to `results/h-e1/statistics.json`

---

### FR10: Validation Report Generation

**Description:** Generate validation report summarizing results and gate status.

**Report Structure:**
1. **Executive Summary:** Gate status (PASS/FAIL), key findings
2. **Dataset Overview:** Problem count, test case statistics
3. **Baseline Results:** Fix-impact-ratio distributions, pass rates
4. **Agent Results:** Fix-impact-ratio distributions, pass rates
5. **Statistical Tests:** p-values, effect sizes, correlations
6. **Visualizations:**
   - Fix-impact-ratio distributions (histograms)
   - Agent vs Baseline scatter plots
   - Convergence curves (pass rate over iterations)
7. **Gate Assessment:** Detailed verification against success criteria

**Output File:** `results/h-e1/04_validation.md`

**Acceptance Criteria:**
- ✅ All sections present
- ✅ Visualizations saved to `results/h-e1/figures/`
- ✅ Clear PASS/FAIL determination
- ✅ Recommendations for next steps

---

## Non-Functional Requirements

### NFR1: Performance

- Dataset curation: < 3 hours for 200 problems
- Single experiment run (50 problems): < 6 hours (GPT-4 API latency)
- Metrics computation: < 5 minutes

### NFR2: Reliability

- Ground truth validation: 100% test pass rate required
- Code execution sandbox: timeout after 10 seconds per test
- API error handling: retry with exponential backoff (max 3 retries)

### NFR3: Reproducibility

- Fixed random seeds for GPT-4 sampling (where applicable)
- Cached dataset (no re-fetch between runs)
- Logged prompts and responses for debugging

### NFR4: Scalability

- Support dataset expansion to 500+ problems without code changes
- Parallel execution of experiments (multi-processing over problems)

---

## Dependencies

### External Dependencies

- **OpenAI API:** GPT-4 Turbo access (required for all agents)
- **Codeforces API:** Problem fetching (fallback: CodeContests dataset)
- **Python Libraries:** `numpy`, `scipy`, `pandas`, `matplotlib`, `requests`

### Internal Dependencies

- **Code Execution Sandbox:** Docker or `subprocess` with timeout
- **Dataset Cache:** `data/codeforces_curated/` directory
- **Results Storage:** `results/h-e1/` directory

---

## Risk Mitigation

### Risk 1: Test Case Quality Issues

**Mitigation:**
- Filter by solve_count > 1000 (validated by community)
- Manual spot-check 10 random problems
- Fallback: CodeContests dataset (pre-curated by DeepMind)

### Risk 2: API Rate Limits

**Mitigation:**
- Cache agent responses (avoid redundant calls)
- Run experiments in batches with delays
- Fallback: Reduce problem set to 30 if budget constrained

### Risk 3: Low Statistical Power

**Mitigation:**
- Verification plan validated n=50 sufficient for p<0.05
- Monitor initial results: if p=0.05-0.10, increase to 100 problems
- Effect size threshold (d > 0.5) provides additional validation

---

## Implementation Plan

### Phase 1: Dataset Preparation (3 days)

- **Day 1:** Fetch Codeforces problems via API/CodeContests
- **Day 2:** Filter and validate (solve_count > 1000, rating 1200-1800, test_cases ≥ 15)
- **Day 3:** Verify ground truth solutions, cache dataset

### Phase 2: Baseline Experiments (4 days)

- **Day 4-5:** Implement and run Baseline 1 (Random Sampling) on 50 problems
- **Day 6-7:** Implement and run Baseline 2 (Sequential Trial-and-Error) on 50 problems
- Compute baseline fix-impact-ratio distributions

### Phase 3: Agent Experiments (5 days)

- **Day 8-9:** Agent A (GPT-4 Baseline) on 50 problems
- **Day 10-11:** Agent B (GPT-4 + Memory) on 50 problems
- **Day 12:** Agent C (GPT-4 + Explicit Prompt) on 50 problems

### Phase 4: Analysis & Reporting (2 days)

- **Day 13:** Statistical tests (Mann-Whitney U, Cohen's d, correlations)
- **Day 14:** Generate validation report with visualizations

**Total Duration:** 14 days (2 weeks)

---

## Success Metrics

### Gate Verification Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Max agent fix-impact-ratio | > 2.0 | Mean across 50 problems |
| Baseline fix-impact-ratio | ≈ 1.0 | Validates metric sensitivity |
| Statistical significance | p < 0.05 | Mann-Whitney U test |
| Effect size | d > 0.5 | Cohen's d (medium+) |

### Quality Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Dataset size | 200 problems | Statistical power |
| Test cases per problem | ≥ 15 | Hypothesis constraint |
| Ground truth validation | 100% pass | Data quality |
| Correlation (ratio vs pass rate) | r > 0.5 | Metric validity |

---

## Appendix

### A1: Dataset Schema

```json
{
  "problem_id": "string (e.g., 'cf_1234A')",
  "statement": "string (problem description)",
  "solution": "string (ground truth code)",
  "test_cases": [
    {
      "input": "string",
      "expected_output": "string"
    }
  ],
  "metadata": {
    "rating": "int (1200-1800)",
    "solve_count": "int (>1000)",
    "test_case_count": "int (≥15)"
  }
}
```

### A2: Results Schema

```json
{
  "experiment_name": "string (e.g., 'agent_explicit')",
  "problem_results": [
    {
      "problem_id": "string",
      "fix_impact_ratio": "float",
      "final_pass_rate": "float (0-100)",
      "iterations_to_convergence": "int",
      "high_impact_fix_proportion": "float (0-1)",
      "modifications": [
        {
          "iteration": "int",
          "tests_fixed": "int",
          "code_diff": "string"
        }
      ]
    }
  ],
  "aggregated_metrics": {
    "mean_fix_impact_ratio": "float",
    "std_fix_impact_ratio": "float",
    "median_fix_impact_ratio": "float",
    "mean_pass_rate": "float",
    "mean_iterations": "float"
  }
}
```

### A3: Prompt Templates

See FR5-FR7 for agent-specific prompt templates.

---

**End of PRD**
