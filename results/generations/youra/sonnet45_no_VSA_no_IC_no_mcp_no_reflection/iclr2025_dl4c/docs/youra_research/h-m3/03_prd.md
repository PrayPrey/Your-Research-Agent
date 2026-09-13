# Product Requirements Document (PRD)
## Transfer Learning to Held-Out Tests - h-m3

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis:** h-m3 (MECHANISM)  
**Status:** Implementation Ready

---

## Executive Summary

### Purpose
Implement experimental validation of transfer learning in code debugging: test whether agents learn generalizable patterns from revealed test failures that transfer to held-out tests without error message feedback.

### Core Hypothesis
Under revealed test failures (50%), if agents learn patterns, then held-out test pass slope > 1.5× baseline because pattern transfer works without error messages.

### Success Criteria
- Primary: Held-out test pass rate slope ratio (agent/random) > 1.5, p < 0.05
- Secondary: Transfer efficiency (held-out slope / revealed slope) > 0.5
- Control: Revealed-only baseline held-out slope ≈ 0

---

## Problem Statement

### Research Question
Can code generation agents learn transferable debugging patterns from partial test feedback that generalize to unseen test cases?

### Validation Gap
h-m2 validated root cause prioritization under full error visibility. h-m3 tests the stronger claim: pattern learning enables held-out test improvement without error messages, demonstrating genuine conceptual understanding vs memorization.

### Impact
Evidence of transfer learning validates strategic debugging's third causal link: pattern extraction → generalization → held-out test improvement.

---

## Functional Requirements

### FR1: Dataset Preparation
**ID:** FR1  
**Priority:** P0 (Blocker)

**Description:**
Curate 50 Codeforces problems with stratified 50% revealed / 50% held-out test splits.

**Acceptance Criteria:**
- 50 problems, rating 1200-1800, solve_count > 1000
- Each problem has 15+ test cases
- Test split: 50% revealed (agent sees errors), 50% held-out (no error feedback)
- Stratified sampling: revealed/held-out difficulty distributions similar (KS test p > 0.05)
- Baseline codes fail at least 3 revealed tests per problem
- Data files: `data/problems.json`, `data/test_splits.json`, `data/baseline_codes/`

---

### FR2: Agent Implementation (GPT-4 + Pattern Memory)
**ID:** FR2  
**Priority:** P0 (Blocker)

**Description:**
Implement GPT-4 agent with pattern memory module for extracting and transferring debugging patterns.

**Components:**
1. **PatternMemory** class: stores (error_pattern, fix_template) tuples
2. **extract_pattern()**: summarizes error type, code region, fix from revealed test failures
3. **retrieve_similar_patterns()**: fetches relevant patterns for current code/error
4. **apply_pattern()**: generates new fix by applying pattern to code

**Acceptance Criteria:**
- Agent runs 10 iterations per problem
- Each iteration: run revealed tests → extract pattern → retrieve similar → generate fix → run held-out tests
- Pattern usage rate > 60% (patterns actually used in fixes)
- Held-out tests NEVER reveal error messages to agent
- Output: `results/agent_results.json` (per-iteration pass rates)

**File:** `code/agent.py`

---

### FR3: Baseline 1 - Random Mutation
**ID:** FR3  
**Priority:** P0 (Blocker)

**Description:**
Blind random code mutations without error feedback.

**Mutation Operators:**
- Variable rename
- Operator change (+/-, </<=)
- Constant modification

**Acceptance Criteria:**
- 20 mutations per problem (1000 total mutations across 50 problems)
- No error message feedback
- Track held-out test pass rate per mutation
- Expected slope ≈ 0 (null hypothesis)
- Output: `results/baseline_results.json`

**File:** `code/random_baseline.py`

---

### FR4: Baseline 2 - Revealed-Test-Only
**ID:** FR4  
**Priority:** P0 (Blocker)

**Description:**
GPT-4 (no memory) fixing revealed tests sequentially without pattern extraction.

**Acceptance Criteria:**
- 10 fix iterations per problem (500 total)
- Agent receives revealed test errors, generates fixes
- NO pattern extraction/memory
- Track held-out test pass rate per iteration
- Expected held-out slope ≈ 0 (fixes don't transfer)
- Output: `results/baseline_results.json`

**File:** `code/revealed_only_baseline.py`

---

### FR5: Experiment Execution Pipeline
**ID:** FR5  
**Priority:** P0 (Blocker)

**Description:**
Orchestrate data prep → agent execution → baseline execution → analysis.

**Phases:**
1. Data prep: curate problems, split tests, generate baseline codes
2. Agent execution: 50 problems × 10 iterations
3. Baseline 1 execution: 50 problems × 20 mutations
4. Baseline 2 execution: 50 problems × 10 iterations
5. Statistical analysis: regression slopes, permutation test

**Acceptance Criteria:**
- Sequential execution with checkpoints
- Early stopping: if agent_slope ≈ random_slope after 30 problems (p > 0.2) → STOP
- Validation: all outputs exist, data quality checks pass
- Execution log saved

**File:** `code/experiment_runner.py`

---

### FR6: Statistical Analysis
**ID:** FR6  
**Priority:** P0 (Blocker)

**Description:**
Compute slope ratios, statistical tests, and visualization.

**Metrics:**
1. Primary: slope_ratio = agent_slope / random_slope
2. Secondary: transfer_efficiency = held_out_slope / revealed_slope
3. Control: revealed_only baseline held-out slope
4. Pattern usage rate

**Statistical Tests:**
- Permutation test: agent_slope vs random_slope (1000 samples, p < 0.05)
- Two-sample t-test: agent_slope vs revealed_only_slope

**Acceptance Criteria:**
- Regression slopes computed for agent, random, revealed-only
- Permutation test p-value < 0.05 for success
- Plots: held-out pass rate curves (agent vs baselines)
- Output: `results/slope_analysis.json`, `results/plots/`

**File:** `code/analysis.py`

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Random seeds fixed for test splits, baseline code generation, mutations
- All hyperparameters logged (temperature=0.7, top-p=0.95)
- Data/code/results versioned

### NFR2: Performance
- Total runtime budget: ~1.5M GPT-4 tokens (~$30)
- Execution time: <4 hours on standard machine
- Early stopping enabled

### NFR3: Data Quality
- Test split validation: KS test p > 0.05
- Baseline code validation: fails 3+ revealed tests
- No test case overlap between revealed/held-out

---

## Data Requirements

### Input Data
| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| Codeforces Problems | Codeforces API | 50 problems | JSON |
| Test Cases | Codeforces | 15+ per problem | JSON (inputs/outputs) |
| Problem Statements | Codeforces | 50 | Markdown/HTML |

### Preprocessing
1. Filter by rating (1200-1800), solve_count (>1000), test count (15+)
2. Parse problem statements, input/output formats
3. Random 50% revealed / 50% held-out split per problem
4. Generate baseline codes (GPT-4, temp=0.7)
5. Validate: baseline fails 3+ revealed tests

### Output Data
| File | Content | Size Estimate |
|------|---------|---------------|
| `data/problems.json` | 50 problem specs | ~500 KB |
| `data/test_splits.json` | Revealed/held-out indices | ~50 KB |
| `data/baseline_codes/` | Initial buggy codes | ~250 KB |
| `results/agent_results.json` | Per-iteration pass rates | ~200 KB |
| `results/baseline_results.json` | Baseline pass rates | ~200 KB |
| `results/slope_analysis.json` | Slopes, p-values | ~20 KB |

---

## Dependencies

### External APIs
- **Codeforces API:** Problem fetching (public, no auth)
- **OpenAI API:** GPT-4 Turbo (requires API key, ~1.5M tokens)

### Python Libraries
- `requests`: Codeforces API calls
- `scipy.stats`: Permutation test, KS test
- `matplotlib`: Visualization
- `openai`: GPT-4 API
- `pyyaml`: Config loading
- `numpy`, `pandas`: Data processing

### Compute Resources
- CPU: Standard (no GPU needed)
- Memory: 8GB (for code execution)
- Storage: 2GB (data + results)

---

## Success Criteria & Validation

### Primary Success (Gate: MUST_WORK)
- ✅ slope_ratio > 1.5 (agent_slope / random_slope)
- ✅ Permutation test p < 0.05
- ✅ Transfer efficiency > 0.5 (held-out improves at least half as fast as revealed)

### Secondary Validation
- ✅ Pattern usage rate > 60% (memory actively contributes)
- ✅ Revealed-only baseline held-out slope ≈ 0 (control check)

### Failure Scenarios
| Scenario | Result | Action |
|----------|--------|--------|
| slope_ratio < 1.2 | PIVOT | No transfer learning, hypothesis falsified |
| agent_slope ≈ revealed_only_slope | PIVOT | Held-out improvement from revealed fixes, not transfer |
| p > 0.05 | EXPLORE/PIVOT | Increase to 100 problems if 0.05 < p < 0.1, else falsified |

---

## Timeline & Milestones

### Implementation Phases
| Phase | Deliverable | Est. Tasks |
|-------|-------------|------------|
| Data Prep | `data/` folder populated | 3-4 tasks |
| Environment Setup | Dependencies installed, APIs configured | 1-2 tasks |
| Agent Implementation | `code/agent.py`, `code/pattern_memory.py` | 8-12 tasks |
| Baseline Implementation | `code/random_baseline.py`, `code/revealed_only_baseline.py` | 4-6 tasks |
| Execution Pipeline | `code/experiment_runner.py` | 4-6 tasks |
| Analysis | `code/analysis.py`, plots | 3-5 tasks |

**Total Task Budget:** 23-35 tasks (target: 30 for FULL tier)

---

## Risks & Mitigation

### Risk 1: Information Leakage
**Risk:** Revealed test fixes accidentally pass held-out tests (shared error types)  
**Mitigation:** Revealed-only baseline controls for this; if baseline shows high held-out slope, split strategy is flawed  
**Fallback:** Increase held-out ratio to 70%

### Risk 2: Pattern Memory Overfitting
**Risk:** Agent memorizes revealed fixes without generalizing  
**Mitigation:** Pattern usage rate metric; if patterns not reused, memory not contributing  
**Fallback:** Add pattern abstraction (normalize variable names, code structure)

### Risk 3: Insufficient Statistical Power
**Risk:** 50 problems insufficient for p < 0.05  
**Mitigation:** Permutation test (more sensitive); early stopping if p < 0.1 after 30 problems  
**Fallback:** Increase to 100 problems

---

## Open Questions

1. **Pattern representation granularity:** Should patterns be error-type-only or include code-structure features?
2. **Transfer mechanism validation:** How to verify patterns are genuinely used vs post-hoc retrieval?
3. **Baseline strength:** Is revealed-only baseline sufficient to rule out accidental transfer?

---

## Appendix

### Hypothesis Lineage
- **h-m1:** Error cluster density → high-impact fixes (VALIDATED)
- **h-m2:** Root cause prioritization → 2+ test improvements (VALIDATED)
- **h-m3:** Pattern learning → held-out test transfer (THIS HYPOTHESIS)

### Related Work
- Few-shot learning in code generation
- Transfer learning in debugging
- Meta-learning for code repair

---

**Document Status:** Implementation Ready  
**Next Phase:** Architecture Design (Step 3)
