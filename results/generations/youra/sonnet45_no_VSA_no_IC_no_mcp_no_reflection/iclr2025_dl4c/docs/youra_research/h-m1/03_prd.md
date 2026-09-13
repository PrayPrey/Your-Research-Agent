# Product Requirements Document: h-m1 Error Clustering Analyzer

**Date:** 2026-08-28  
**Hypothesis:** Under multi-test failures, if agents identify root causes, then test failures are grouped by shared error sources because conceptual understanding enables pattern recognition.  
**Phase 2C Source:** 02c_experiment_brief.md  
**Gate:** MUST_WORK (clustering coefficient > 0.3, p < 0.05 vs random)

---

## 1. Executive Summary

Build evaluation framework measuring whether code debugging agents cluster fixes by error type (syntax/runtime/logic/edge-case). Core claim: conceptual understanding → pattern recognition → grouped error handling vs random trial-and-error.

**Success Criteria:** Clustering coefficient > 0.3 AND p < 0.05 vs random permutation baseline.

**Failure Consequence:** PIVOT - mechanism not validated, agents don't group errors by root cause.

---

## 2. System Architecture

### 2.1 Components

```
┌─────────────────────────────────────────────────┐
│ Main Evaluation Loop                            │
│  ├─ Problem Loader (Codeforces API)            │
│  ├─ Agent Debugging Session                     │
│  │   ├─ GPT-4 Turbo Baseline (temp=0.7)        │
│  │   ├─ Multi-test execution (15+ cases)       │
│  │   └─ Fix sequence tracking                  │
│  ├─ Error Annotation (human 2-3 annotators)    │
│  └─ Clustering Analysis                         │
│      ├─ Clustering coefficient                 │
│      ├─ Permutation test (p-value)             │
│      └─ Inter-annotator kappa > 0.7            │
└─────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. Fetch 50 Codeforces problems (rating 1200-1800, solve_count > 1000, test_cases ≥ 15)
2. Run debugging session: agent generates code → test → fix → repeat (max 10 iterations)
3. Track fix sequence: which test failures addressed in what order
4. Human annotate error types: syntax/runtime/logic/edge-case (2-3 annotators, kappa > 0.7)
5. Compute clustering coefficient: observed consecutive same-type / expected random
6. Permutation test: p-value vs 1000 random shuffles
7. Generate figures: coefficient bar chart, fix sequence heatmap, error distribution

---

## 3. Functional Requirements

### FR1: Problem Curation
- Fetch Codeforces problems via API
- Filter: solve_count > 1000, rating 1200-1800
- Verify test case count ≥ 15 per problem (via scraping if API lacks field)
- Output: 50 problems × metadata (problem_id, test_cases, rating)

### FR2: Multi-Test Debugging Loop
- Generate initial solution (GPT-4 Turbo, temp=0.7)
- Execute all test cases (subprocess isolation)
- Present failing tests to agent
- Agent returns fixed code
- Track: iteration, passing count delta, failing test IDs
- Terminate: all pass OR max 10 iterations

### FR3: Error Annotation
- Manual labeling UI: annotators see test failure (input/output/error)
- Taxonomy: syntax, runtime, logic, edge_case
- Multi-annotator workflow (2-3 labels per failure)
- Compute Cohen's kappa (require > 0.7)
- Resolve conflicts: majority vote or 3rd annotator

### FR4: Clustering Measurement
- Input: fix_sequence (list of test IDs), error_labels (dict)
- Compute observed consecutive same-type rate
- Expected random = 1 / num_unique_error_types
- Clustering coefficient = observed / expected
- Permutation test: shuffle fix_sequence 1000 times, compute p-value

### FR5: Visualization
- **Gate metric chart**: Clustering coefficient agent vs random (bar chart)
- **Error distribution**: Histogram of error types (750 test failures)
- **Fix sequence heatmap**: Time (iteration) × error type
- **Inter-annotator agreement**: Confusion matrix (kappa validation)
- Save to `h-m1/figures/` as PNG

---

## 4. Non-Functional Requirements

### NFR1: Reproducibility
- Fixed seed = 1
- GPT-4 model version: `gpt-4-turbo-2024-04-09`
- Annotation guidelines documented (with examples)

### NFR2: Performance
- API rate limits: max 10 req/min to Codeforces
- Test execution timeout: 5s per test case
- Annotation: 750 labels (50 problems × 15 tests) → ~3-5 hours per annotator

### NFR3: Data Quality
- Reject problems with < 15 test cases
- Reject annotations with kappa < 0.7 (re-annotate or filter problems)
- Verify agent completes ≥ 5 iterations per problem (else discard problem)

### NFR4: Error Handling
- API failures → retry 3x with exponential backoff
- Test execution crash → log error, mark test as "execution_failed"
- Agent timeout → abort iteration, use last valid code

---

## 5. Success Metrics

| Metric | Threshold | Source |
|--------|-----------|--------|
| Clustering coefficient (agent) | > 0.3 | Phase 2B Section 2.2 |
| p-value (vs random) | < 0.05 | Phase 2B Section 2.2 |
| Cohen's kappa (annotators) | > 0.7 | 02c_experiment_brief.md |
| Sample size | 50 problems | 02c_experiment_brief.md |
| Test cases per problem | ≥ 15 | 02c_experiment_brief.md |

**PoC Success:** Code runs without error AND clustering_agent > clustering_random.

---

## 6. Out of Scope

- Agent architecture variations (memory module, prompting) → future work
- Fix-impact-ratio analysis → covered by prerequisite h-e1
- Automated error annotation (ML-based) → requires reliable ground truth first
- Real-time debugging UI → batch evaluation only

---

## 7. Dependencies

### External APIs
- OpenAI API (GPT-4 Turbo)
- Codeforces API (problem metadata)
- Codeforces scraping (test cases, if not in API)

### Python Libraries
- `openai>=1.0.0` (agent inference)
- `requests` (API calls)
- `numpy`, `scipy` (statistics, permutation test)
- `sklearn` (Cohen's kappa)
- `matplotlib`, `seaborn` (figures)
- `subprocess` (test execution isolation)

### Data
- Codeforces problems (public, no auth required)
- Human annotators (2-3 researchers with coding expertise)

---

## 8. Assumptions & Constraints

### Assumptions
- Codeforces API stable, rate limits acceptable
- GPT-4 Turbo API accessible (no quota exhaustion)
- Annotators have programming background (can classify syntax vs logic errors)
- 50 problems sufficient for p < 0.05 with clustering coefficient ~ 0.3-0.5

### Constraints
- Budget: ~500 API calls (50 problems × ~10 iterations/problem)
- Timeline: Annotation bottleneck (~5 hours per annotator for 750 labels)
- Gate: MUST_WORK → if fails, hypothesis PIVOTS

---

## 9. Acceptance Criteria

**Phase 4 Implementation Complete When:**
1. Code executes 50 problems end-to-end without crash
2. All 750 test failures annotated (kappa > 0.7 verified)
3. Clustering coefficient + p-value computed for agent vs random
4. All 4 required figures generated and saved
5. Gate evaluation logic: `assert clustering_agent > 0.3 and p_value < 0.05`

**Validation Report (04_validation.md) Must Include:**
- Clustering coefficient (agent vs random) with p-value
- Cohen's kappa (annotator agreement)
- Sample size breakdown (problems × iterations × test failures)
- Gate decision: PASS/PIVOT with justification

---

## 10. Appendix: Error Taxonomy

### Syntax Errors
- Missing brackets, colons, semicolons
- Indentation errors
- Undefined variable references

### Runtime Errors
- Division by zero
- Index out of bounds
- Type mismatches (int + str)
- Null pointer / None access

### Logic Errors
- Incorrect algorithm (wrong sorting, search)
- Off-by-one errors
- Edge case mishandling (empty list, single element)

### Edge Case Failures
- Large input overflow
- Boundary conditions (min/max values)
- Special inputs (negative, zero)

**Annotation Guideline:** If test failure shows exception → runtime or syntax. If wrong output (no exception) → logic or edge case. Consult examples in annotation manual.

---

*Next Phase: Phase 4 - Implementation (Coder + Validator agents)*
