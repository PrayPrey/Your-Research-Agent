# Experiment Brief: Transfer Learning to Held-Out Tests (h-m3)

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** h-m2 (VALIDATED)
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

**Statement:**
Under revealed test failures (50%), if agents learn patterns, then held-out test pass slope > 1.5× baseline because pattern transfer works without error messages.

**Rationale:**
Tests the third link in strategic debugging causal chain — agents must generalize from revealed errors to unseen cases. Strongest evidence of conceptual understanding vs memorization. If agents show measurably higher held-out test pass rate slope compared to random mutation baseline, this validates that pattern learning transfers to unseen test cases without relying on error message information.

**Variables:**
- **Independent:** Agent Architecture (GPT-4+memory vs baselines)
- **Dependent:** Held-Out Test Pass Rate Slope (agent_slope / random_slope)
- **Controlled:** Held-out ratio (50%), test revelation strategy, problem difficulty

---

## 2. Dataset Specification

### 2.1 Dataset Selection

**Name:** Codeforces Competitive Programming Problems (Curated Subset)
**Type:** standard
**Source:** Codeforces.com (publicly available)
**Scope:** 50 problems (Phase 1 validation scale)

**Filtering Criteria:**
- Rating: 1200-1800 (intermediate difficulty)
- Solve count: > 1000 (ensures quality test suites)
- Test cases: 15+ per problem (required for 50% held-out split)

**Split Strategy:**
- 50% revealed tests (agent receives error messages during iteration)
- 50% held-out tests (agent NEVER sees error messages)
- Stratified sampling: ensure revealed/held-out tests have similar difficulty distribution

**Cache Path:** `docs/youra_research/h-m3/data/problems.json`

**Justification:**
- Consistent with h-m1/h-m2 dataset for cross-hypothesis comparison
- High solve count (>1000) ensures quality test suites (verification plan assumption A2)
- 15+ test cases per problem allows meaningful 50% split
- 50% held-out methodology isolates transfer learning signal from information-based improvement (verification plan assumption A3)

**Sample Size:** 50 problems × 15 test cases average = 750 total test executions per iteration

### 2.2 Data Preparation Steps

1. **Problem Curation:**
   - Fetch problems from Codeforces API filtering by rating (1200-1800) and solve count (>1000)
   - Parse problem statement, input/output format, test cases
   - Validate test case count (15+ required)
   - Store in `data/problems.json`

2. **Test Case Split:**
   - For each problem, randomly assign test cases to revealed (50%) or held-out (50%)
   - Ensure at least 7 revealed tests per problem (minimum for pattern learning)
   - Store split indices in `data/test_splits.json`
   - Validation: revealed/held-out test difficulty distributions similar (KS test, p > 0.05)

3. **Baseline Code Generation:**
   - Use GPT-4 (temperature=0.7) to generate initial code for each problem
   - Accept only codes that fail at least 3 revealed tests (ensures debugging task exists)
   - Store baseline codes in `data/baseline_codes/`

4. **Data Validation Checks:**
   - All problems have 15+ test cases
   - All problems have 50% revealed / 50% held-out split
   - Baseline codes exist for all problems
   - No test case overlap between revealed/held-out sets

---

## 3. Model Specification

### 3.1 Model Selection

**Name:** GPT-4 Turbo with Pattern Learning Agent
**Type:** Large Language Model (code generation)
**Pretrained Base:** gpt-4-turbo-2024-04-09

**Architecture Variant:** GPT-4 + memory module
- **Memory Module:** Stores revealed test failure patterns (error type, code region, fix applied)
- **Pattern Extraction:** After each fix, agent summarizes learned pattern (e.g., "off-by-one errors in loop bounds")
- **Transfer Mechanism:** When generating new fix, agent retrieves similar patterns from memory and applies to current code

**Hyperparameters:**
- Temperature: 0.7 (per verification plan)
- Max tokens: 2048 (sufficient for code modifications)
- Top-p: 0.95

**Cache Path:** `docs/youra_research/h-m3/code/agent.py`

**Justification:**
- Memory-augmented GPT-4 is the architecture most likely to demonstrate pattern transfer (verification plan assumption A4)
- h-m1/h-m2 used baseline GPT-4 — h-m3 tests whether memory module enables transfer learning
- Pattern extraction + retrieval is the minimum mechanism needed to test transfer hypothesis

### 3.2 Model Setup

**Implementation File:** `code/agent.py`
**Key Components:**
1. `PatternMemory` class: stores (error_pattern, fix_template) tuples
2. `extract_pattern(error_msg, code, fix)`: extracts reusable pattern from revealed test failures
3. `retrieve_similar_patterns(current_code, current_error)`: retrieves relevant patterns from memory
4. `apply_pattern(pattern, code)`: generates new fix by applying pattern to current code

**No Fine-Tuning Required:** Uses pretrained GPT-4 + prompt engineering for pattern extraction

---

## 4. Baseline Methods

### 4.1 Baseline 1: Random Mutation Baseline

**Description:**
Apply random code mutations (variable renames, expression rewrites, operator changes) without error feedback.

**Implementation:**
- Mutation operators: rename variable, change operator (+/-, </<=), modify constant
- Sample size: 1000 mutations across 50 problems (20 mutations per problem)
- No error message feedback — mutations are blind

**Metric Tracked:**
- Held-out test pass rate slope per iteration
- Expected slope: ~0 (random mutations should not systematically improve held-out tests)

**Justification:**
Null hypothesis — if pattern transfer does not work, agent slope should match random mutation slope.

**Implementation File:** `code/random_baseline.py`

### 4.2 Baseline 2: Revealed-Test-Only Baseline

**Description:**
Fix revealed test failures sequentially without attempting to generalize to held-out tests. Agent receives revealed test error messages and fixes them, but does not attempt pattern extraction or transfer.

**Implementation:**
- Use GPT-4 (no memory module) to fix revealed test failures
- 10 fix iterations per problem
- Sample size: 50 problems × 10 iterations = 500 fix attempts
- Track held-out test pass rate per iteration

**Metric Tracked:**
- Held-out test pass rate slope
- Expected slope: ~0 (fixes target revealed tests only, should not transfer to held-out)

**Justification:**
Controls for information gain from revealed tests — validates that held-out improvement is due to transfer, not revealed test fixes accidentally passing held-out tests.

**Implementation File:** `code/revealed_only_baseline.py`

---

## 5. Experimental Procedure

### 5.1 Procedure Steps

**Phase 1: Data Preparation**
1. Curate 50 Codeforces problems (rating 1200-1800, solve_count > 1000, 15+ test cases)
2. Split test cases into revealed (50%) and held-out (50%)
3. Generate baseline codes (GPT-4, temperature=0.7)
4. Validate: all problems have failing revealed tests

**Phase 2: Agent Execution**
For each problem:
1. Initialize PatternMemory (empty)
2. Iteration 1-10:
   - Run code on revealed tests → get error messages
   - Extract pattern: `extract_pattern(error_msg, code, fix)`
   - Store pattern in PatternMemory
   - Retrieve similar patterns: `retrieve_similar_patterns(current_code, current_error)`
   - Generate fix: `apply_pattern(pattern, code)` + GPT-4 completion
   - Run code on held-out tests → record pass rate (NO error messages shown)
3. Store results: revealed pass rate, held-out pass rate per iteration

**Phase 3: Baseline Execution**
1. Random Mutation Baseline:
   - For each problem, apply 20 random mutations
   - Track held-out test pass rate per mutation
2. Revealed-Test-Only Baseline:
   - For each problem, run 10 fix iterations targeting revealed tests only
   - Track held-out test pass rate per iteration

**Phase 4: Analysis**
1. Fit linear regression: held_out_pass_rate ~ iteration (for agent and baselines)
2. Extract slopes: agent_slope, random_slope, revealed_only_slope
3. Compute slope ratio: agent_slope / random_slope
4. Statistical test: permutation test (1000 samples, p < 0.05)

### 5.2 Iteration Count & Budget

**Iteration Count:** 10 iterations per problem
**Total Samples:**
- Agent: 50 problems × 10 iterations = 500 executions
- Random baseline: 50 problems × 20 mutations = 1000 executions
- Revealed-only baseline: 50 problems × 10 iterations = 500 executions

**Compute Budget:**
- GPT-4 API calls: 500 (agent) + 500 (revealed-only) = 1000 calls
- Token estimate: ~1500 tokens/call × 1000 calls = 1.5M tokens
- Cost estimate: ~$30 (GPT-4 Turbo pricing)

### 5.3 Stopping Criteria

**Early Stopping (Success):**
- If agent_slope > 1.5× random_slope AND p < 0.05 after 30 problems → proceed to full 50 problems for confirmation

**Early Stopping (Failure):**
- If agent_slope ≈ random_slope (ratio < 1.2) AND p > 0.2 after 30 problems → STOP, hypothesis falsified

**Final Evaluation:**
- Requires all 50 problems for statistical power (verification plan assumption A5)

---

## 6. Evaluation Metrics

### 6.1 Primary Metric

**Metric Name:** Held-Out Test Pass Rate Slope Ratio
**Definition:**
```
agent_slope = slope of held_out_pass_rate ~ iteration (agent)
random_slope = slope of held_out_pass_rate ~ iteration (random baseline)
slope_ratio = agent_slope / random_slope
```

**Success Criterion:**
- slope_ratio > 1.5 (agent improves held-out tests 1.5× faster than random)
- p < 0.05 (permutation test, 1000 samples)

**Measurement Method:**
1. For each problem, record held-out test pass rate at iterations 1, 2, ..., 10
2. Fit linear regression: held_out_pass_rate ~ iteration
3. Extract slope (units: percentage points per iteration)
4. Compute mean slope across 50 problems for agent and baselines
5. Permutation test: randomly shuffle agent/random labels 1000 times, compute p-value

**Justification:**
Slope ratio captures rate of held-out test improvement relative to random chance. Ratio > 1.5 indicates meaningful transfer learning (verification plan success criterion).

### 6.2 Secondary Metrics

**Metric 1: Held-Out vs Revealed Pass Rate Improvement**
**Definition:**
```
revealed_slope = slope of revealed_pass_rate ~ iteration
held_out_slope = slope of held_out_pass_rate ~ iteration
transfer_efficiency = held_out_slope / revealed_slope
```
**Success Criterion:** transfer_efficiency > 0.5 (held-out tests improve at least half as fast as revealed tests)
**Justification:** Evidence that fixes targeting revealed tests also transfer to held-out tests

**Metric 2: Pattern Retrieval Accuracy**
**Definition:**
```
For each fix iteration:
  - Count how many retrieved patterns were actually used in the fix
  - pattern_usage_rate = used_patterns / retrieved_patterns
```
**Success Criterion:** pattern_usage_rate > 0.6 (agent uses retrieved patterns in majority of fixes)
**Justification:** Validates that pattern memory is actively contributing to fix generation

**Metric 3: Revealed-Only Baseline Held-Out Slope**
**Definition:** Slope of held_out_pass_rate ~ iteration for revealed-test-only baseline
**Success Criterion:** revealed_only_slope ≈ 0 (no held-out improvement without transfer mechanism)
**Justification:** Control metric — if revealed-only baseline shows high held-out slope, then held-out improvement is due to revealed test fixes accidentally passing held-out tests, not transfer learning

### 6.3 Statistical Tests

**Test 1: Slope Ratio Significance (Primary)**
- **Method:** Permutation test (1000 samples)
- **Null Hypothesis:** agent_slope = random_slope
- **Alternative:** agent_slope > random_slope
- **Significance Level:** p < 0.05

**Test 2: Agent vs Revealed-Only Baseline**
- **Method:** Two-sample t-test on held-out slopes
- **Null Hypothesis:** agent_slope = revealed_only_slope
- **Alternative:** agent_slope > revealed_only_slope
- **Significance Level:** p < 0.05

---

## 7. Success Criteria

### 7.1 Primary Success Criteria (Gate: MUST_WORK)

**Criterion 1 (Primary):**
- At least one architecture shows held_out_slope > 1.5× random_slope
- Permutation test p < 0.05

**Criterion 2 (Secondary):**
- Held-out pass rate increases faster than revealed test pass rate (transfer_efficiency > 0.5)
- Evidence that fixes targeting revealed tests transfer to held-out tests

**Gate Decision:**
- **PASS:** Both criteria met → h-m3 VALIDATED, proceed to hypothesis synthesis
- **FAIL:** Criterion 1 not met → PIVOT, no transfer learning, mechanism not validated beyond information gain

### 7.2 Failure Response Protocol

**If agent_slope ≈ random_slope (ratio < 1.2):**
- **Action:** PIVOT
- **Interpretation:** No transfer learning — held-out improvement is at chance level
- **Next Steps:** Document in reflection, hypothesis falsified

**If agent_slope > random_slope BUT agent_slope ≈ revealed_only_slope:**
- **Action:** PIVOT
- **Interpretation:** Held-out improvement is due to revealed test fixes accidentally passing held-out tests, not pattern transfer
- **Next Steps:** Redesign held-out split strategy (e.g., 70% held-out) or hypothesis falsified

**If p > 0.05:**
- **Action:** PIVOT (if p > 0.2) or EXPLORE (if 0.05 < p < 0.2)
- **Interpretation:** Insufficient statistical power or effect size too small
- **Next Steps:** Increase problem count to 100 (if p < 0.1) or hypothesis falsified

---

## 8. Expected Outcomes

### 8.1 Predicted Results

**Agent (GPT-4 + Pattern Memory):**
- Held-out test pass rate slope: 3-5 percentage points per iteration
- Slope ratio vs random: 1.8-2.5×
- Pattern usage rate: 65-75%

**Random Mutation Baseline:**
- Held-out test pass rate slope: 1-2 percentage points per iteration
- Represents chance-level improvement

**Revealed-Test-Only Baseline:**
- Held-out test pass rate slope: 0-1 percentage points per iteration
- Minimal transfer without pattern extraction mechanism

### 8.2 Alternative Outcomes

**Outcome 1: Strong Transfer (slope_ratio > 2.5)**
- **Interpretation:** Pattern learning is highly effective, transfer works robustly
- **Implication:** Memory module is a key architectural component for strategic debugging

**Outcome 2: Weak Transfer (1.0 < slope_ratio < 1.5)**
- **Interpretation:** Some transfer learning, but below success threshold
- **Implication:** Pattern extraction mechanism needs refinement (e.g., more sophisticated pattern representation)

**Outcome 3: No Transfer (slope_ratio ≈ 1.0)**
- **Interpretation:** Hypothesis falsified — agents do not learn transferable patterns from revealed tests
- **Implication:** Strategic debugging relies on revealed test information only, not generalization

---

## 9. Risk Mitigation

### 9.1 Technical Risks

**Risk 1: Held-Out Split Reveals Information**
- **Description:** Revealed test fixes accidentally pass held-out tests due to shared error types
- **Mitigation:** Use revealed-only baseline to control for this — if baseline shows high held-out slope, split strategy is flawed
- **Fallback:** Increase held-out ratio to 70% to reduce information leakage

**Risk 2: Pattern Memory Overfitting**
- **Description:** Agent memorizes revealed test fixes without learning generalizable patterns
- **Mitigation:** Analyze pattern usage rate — if patterns are not reused across problems, memory is not contributing
- **Fallback:** Add pattern generalization step (e.g., abstract variable names, normalize code structure)

**Risk 3: Insufficient Statistical Power**
- **Description:** 50 problems may not provide enough power to detect slope ratio differences (p < 0.05)
- **Mitigation:** Use permutation test (more sensitive than parametric tests) and check power post-hoc
- **Fallback:** Increase to 100 problems if p < 0.1 but p > 0.05

### 9.2 Data Quality Risks

**Risk 1: Test Case Quality Variance**
- **Description:** Some problems have low-quality test suites (duplicates, weak coverage)
- **Mitigation:** Filter by solve count > 1000 (high-quality problems per verification plan)
- **Fallback:** Manual curation or switch to different benchmark if quality issues persist

**Risk 2: Revealed/Held-Out Difficulty Imbalance**
- **Description:** Held-out tests are systematically easier/harder than revealed tests
- **Mitigation:** Stratified sampling + KS test validation (p > 0.05)
- **Fallback:** Resample test splits until difficulty distributions match

---

## 10. Implementation Notes

### 10.1 File Structure

```
docs/youra_research/h-m3/
├── 02c_experiment_brief.md         # This file
├── data/
│   ├── problems.json                # 50 curated Codeforces problems
│   ├── test_splits.json             # Revealed/held-out test indices
│   ├── baseline_codes/              # Initial GPT-4 generated codes
│   └── validation_checks.json       # Data quality validation results
├── code/
│   ├── agent.py                     # GPT-4 + Pattern Memory agent
│   ├── random_baseline.py           # Random mutation baseline
│   ├── revealed_only_baseline.py    # Revealed-test-only baseline
│   ├── pattern_memory.py            # PatternMemory class
│   ├── experiment_runner.py         # Main experiment orchestrator
│   └── analysis.py                  # Statistical analysis + plots
├── results/
│   ├── agent_results.json           # Per-iteration held-out pass rates
│   ├── baseline_results.json        # Baseline held-out pass rates
│   ├── slope_analysis.json          # Regression slopes + p-values
│   └── plots/                       # Held-out pass rate curves
└── 04_validation.md                 # Final validation report
```

### 10.2 Phase 4 Implementation Guidance

**Critical Implementation Details:**
1. **Test Case Split:** Ensure revealed/held-out split is truly random and stratified by difficulty
2. **Pattern Extraction:** Must extract generalizable patterns (not problem-specific fixes)
3. **No Held-Out Information Leakage:** Agent must NEVER see held-out test error messages
4. **Statistical Power:** Use permutation test (non-parametric, more sensitive)

**Recommended Libraries:**
- `requests` for Codeforces API
- `scipy.stats` for permutation test
- `matplotlib` for held-out pass rate plots
- OpenAI Python SDK for GPT-4 API

**Validation Checkpoints:**
- After data preparation: validate test split quality (KS test)
- After agent execution: validate pattern usage rate > 0
- After baseline execution: validate revealed-only slope ≈ 0
- After analysis: validate p-value computation (permutation test)

---

## 11. Dependencies

**Prerequisite Hypotheses:**
- **h-m2 (VALIDATED):** Root cause prioritization must work before testing transfer learning
  - h-m2 validates that agents can identify and prioritize high-impact fixes
  - h-m3 extends this to test whether fixes transfer to unseen test cases

**Data Dependencies:**
- Codeforces API (public, no auth required)
- GPT-4 Turbo API (OpenAI account required)

**Compute Dependencies:**
- OpenAI API quota: ~1.5M tokens
- Local compute: minimal (statistical analysis only)

---

## 12. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-28 | Initial experiment brief for h-m3 |

---

**Prepared by:** Phase 2C Pipeline
**Status:** READY FOR PHASE 3 (Implementation Planning)
