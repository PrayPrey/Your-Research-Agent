# Configuration: H-M2 Experiment

**Hypothesis:** Root Cause Prioritization in Code Debugging
**Date:** 2026-08-28
**Base Hypothesis:** h-m1 (Error Clustering Recognition)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config pattern verified from h-m1/code/config.py
**Config Files Found:** h-m1/code/config.py
**Pattern Used:** Hardcoded dict (EXPERIMENT_CONFIG)

---

## Inherited Configuration (Base Hypothesis)

### Config from H-M1 (Actual Code)

Verified from `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_dl4c/docs/youra_research/h-m1/code/config.py`

```python
# Reused from H-M1 (verified field names):
EXPERIMENT_CONFIG = {
    # Model (unchanged from H-M1)
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,
    
    # Dataset (unchanged - same 50 problems)
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,
    
    # Debugging loop (unchanged)
    "max_iterations": 10,
    
    # Reproducibility (unchanged)
    "random_seed": 1,
}
```

---

## A-1: Baseline Agent Configuration [Complexity: 1, Budget: 3]

**Applied:** Standard sequential debugging (H-M1 baseline pattern)

### Configuration (Python Dict)

```python
BASELINE_CONFIG = {
    # Model (from H-M1)
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,
    "timeout": 60,
    
    # Dataset (from H-M1)
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    
    # Debugging
    "max_iterations": 10,
    "strategy": "sequential",  # Address failures in original order
    
    # Reproducibility
    "random_seed": 1,
    
    # API
    "openai_retry_count": 3,
    "retry_backoff": 2.0,
    
    # Paths
    "cache_dir": "docs/youra_research/h-m1/cache",  # Reuse H-M1 dataset
    "output_dir": "docs/youra_research/h-m2/results/baseline",
}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Sequential iteration | Iterate through failed tests in original order |
| C-1-2 | Fix generation | Generate code fix for current failure (GPT-4) |
| C-1-3 | Impact tracking | Record Δpassing_tests per modification |

---

## A-2: Proposed Agent Configuration [Complexity: 2, Budget: 5]

**Applied:** Root cause prioritization (cluster-based strategy)

### Configuration (Python Dict)

```python
PROPOSED_CONFIG = {
    # Model (from H-M1)
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_tokens": 2048,
    "timeout": 60,
    
    # Dataset (from H-M1)
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    
    # Debugging (NEW: prioritization strategy)
    "max_iterations": 10,
    "strategy": "prioritized",  # Address largest cluster first
    "clustering_method": "error_type",  # From H-M1 validated clustering
    
    # Reproducibility
    "random_seed": 1,
    
    # API
    "openai_retry_count": 3,
    "retry_backoff": 2.0,
    
    # Paths
    "cache_dir": "docs/youra_research/h-m1/cache",  # Reuse H-M1 dataset
    "output_dir": "docs/youra_research/h-m2/results/proposed",
}
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Error clustering | Cluster failed tests by error type (H-M1 mechanism) |
| C-2-2 | Cluster prioritization | Sort clusters by size (descending) |
| C-2-3 | Priority queue | Build fix priority queue (largest cluster first) |
| C-2-4 | Fix generation | Generate code fix for highest priority failure |
| C-2-5 | Impact tracking | Record Δpassing_tests per modification |

---

## A-3: Evaluation Configuration [Complexity: 1, Budget: 4]

**Applied:** Fix-impact-ratio measurement (Archon KB pattern)

### Configuration (Python Dict)

```python
EVALUATION_CONFIG = {
    # Metric thresholds
    "high_impact_threshold": 2,  # Δpassing_tests ≥ 2
    
    # Success criteria (PoC)
    "success_criterion": "directional",  # proposed > baseline
    
    # Visualization
    "save_figures": True,
    "figure_dir": "docs/youra_research/h-m2/figures",
    "figure_formats": ["png"],
    "dpi": 300,
    
    # Outputs
    "results_file": "docs/youra_research/h-m2/results/metrics.json",
    "fix_sequences_file": "docs/youra_research/h-m2/results/fix_sequences.json",
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Impact calculation | Calculate Δpassing_tests for each modification |
| C-3-2 | Proportion metric | Count high-impact fixes (Δ ≥ 2) / total fixes |
| C-3-3 | Comparison | Compare baseline vs proposed proportions |
| C-3-4 | Visualization | Generate bar chart + histograms |

---

## A-4: Dataset Configuration [Complexity: 1, Budget: 2]

**Applied:** H-M1 dataset reuse (cache-first loading)

### Configuration (Python Dict)

```python
DATASET_CONFIG = {
    # Source priority
    "cache_first": True,  # Check H-M1 cache before API fetch
    "h_m1_cache_path": "docs/youra_research/h-m1/cache/problems.json",
    
    # Codeforces API (fallback)
    "api_url": "https://codeforces.com/api/problemset.problems",
    "rate_limit": 10,  # Requests per second
    
    # Filtering (from H-M1)
    "num_problems": 50,
    "rating_min": 1200,
    "rating_max": 1800,
    "solve_count_min": 1000,
    "min_test_cases": 15,
    
    # Test execution
    "test_timeout": 5,  # Seconds per test case
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Cache loading | Load 50 problems from H-M1 cache |
| C-4-2 | API fallback | Fetch from Codeforces API if cache missing |

---

## Self-Validation

- [x] ONE format only (hardcoded dict - consistent with H-M1)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (none needed - all from H-M1 or experiment brief)
- [x] Subtask count within budget (3+5+4+2=14 total)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis config verified from actual code (h-m1/code/config.py)
- [x] Field names match actual implementation (verified: "model", "temperature", etc.)
- [x] Inherited Configuration section included

---

## Notes for Phase 4 Coder

**Copy-paste ready configuration:**
1. Use `BASELINE_CONFIG` for sequential debugging baseline
2. Use `PROPOSED_CONFIG` for root cause prioritization
3. Use `EVALUATION_CONFIG` for metric calculation and visualization
4. Use `DATASET_CONFIG` for dataset loading (H-M1 cache first, API fallback)

**Critical field names verified from H-M1 actual code:**
- `model`, `temperature`, `max_tokens`, `timeout`
- `num_problems`, `rating_min`, `rating_max`, `solve_count_min`
- `max_iterations`, `random_seed`
- `cache_dir`, `output_dir`, `figures_dir`

**New fields for H-M2:**
- `strategy`: "sequential" (baseline) vs "prioritized" (proposed)
- `clustering_method`: "error_type" (from H-M1)
- `high_impact_threshold`: 2 (Δpassing_tests ≥ 2)
- `success_criterion`: "directional" (PoC - no statistical test)

---

*Configuration schema ready for Phase 4 implementation.*
*Total subtasks: 14 (within budget).*
*All configs inherit from validated H-M1 patterns.*
