# Architecture Design Document
## Transfer Learning to Held-Out Tests - h-m3

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis:** h-m3 (MECHANISM)

---

## Codebase Analysis (Serena)

**Base Hypothesis:** h-m2 (Root cause prioritization)

**Existing Code Structure:**
```
h-m2/code/
├── agent.py                 # Mock GPT-4 agent with cluster prioritization
├── experiment_runner.py     # Main execution harness
└── data/
    └── problems.json        # Cached Codeforces problems
```

**Import Patterns from h-m2:**
- Data loading: `json.load()` from `data/problems.json`
- Agent interface: `class Agent` with `fix_problem(problem, tests)` method
- Test execution: `run_tests(code, tests)` returns pass/fail boolean array

**Reusable Components:**
- Dataset loader (Codeforces API wrapper)
- Test execution engine
- Result logging structure

**Applied:** Standard DL experiment template (data → model → train → eval)  
**Applied:** Incremental hypothesis pattern (reuse base infrastructure, add memory module)

---

## System Architecture

### Module Structure

```
h-m3/
├── data/
│   ├── problems.json              # Codeforces problem cache (reuse h-m2)
│   ├── test_splits.json           # Revealed/held-out indices per problem
│   ├── baseline_codes/            # Initial buggy codes
│   │   ├── problem_001.py
│   │   └── ...
│   └── validation_checks.json     # Data quality metrics
│
├── code/
│   ├── pattern_memory.py          # NEW: PatternMemory class
│   ├── agent.py                   # GPT-4 + PatternMemory agent
│   ├── random_baseline.py         # Random mutation baseline
│   ├── revealed_only_baseline.py  # Revealed-test-only baseline
│   ├── experiment_runner.py       # Main orchestrator (adapted from h-m2)
│   └── analysis.py                # Statistical analysis + plots
│
├── results/
│   ├── agent_results.json         # Per-iteration pass rates (agent)
│   ├── baseline_results.json      # Baseline pass rates
│   ├── slope_analysis.json        # Regression slopes, p-values
│   └── plots/
│       ├── held_out_curves.png    # Agent vs baselines
│       └── pattern_usage.png
│
└── 04_validation.md               # Final validation report
```

---

## Module Descriptions

### 1. PatternMemory (`code/pattern_memory.py`)

**Purpose:** Store and retrieve debugging patterns learned from revealed test failures.

**Public API:**
```python
class PatternMemory:
    def store_pattern(error_type: str, code_region: str, fix_template: str) -> None
    def retrieve_similar(current_error: str, current_code: str, top_k: int = 3) -> List[Pattern]
    def get_usage_stats() -> Dict[str, int]  # For pattern usage rate metric
```

**Dependencies:** None (stdlib only)

**Complexity:** LOW (simple dict storage + cosine similarity retrieval)

---

### 2. Agent (`code/agent.py`)

**Purpose:** GPT-4 agent with pattern memory for iterative code fixing.

**Public API:**
```python
class PatternLearningAgent:
    def __init__(memory: PatternMemory, model: str = "gpt-4-turbo-2024-04-09")
    
    def fix_iteration(
        problem: Problem,
        current_code: str,
        revealed_tests: List[Test],
        held_out_tests: List[Test]
    ) -> FixResult
    
    def extract_pattern(error_msg: str, code: str, fix: str) -> Pattern
    def apply_pattern(pattern: Pattern, code: str) -> str
```

**Dependencies:**
- `pattern_memory.PatternMemory`
- `openai` (GPT-4 API)
- Data structures from `h-m2/code/agent.py`

**Complexity:** MEDIUM-HIGH (GPT-4 integration + pattern extraction logic)

---

### 3. Baselines (`code/random_baseline.py`, `code/revealed_only_baseline.py`)

**Purpose:** Control experiments for slope comparison.

**Public API:**
```python
# random_baseline.py
def mutate_code(code: str, mutation_type: str) -> str
def run_random_baseline(problems: List[Problem], n_mutations: int = 20) -> Results

# revealed_only_baseline.py  
def run_revealed_only_baseline(problems: List[Problem], n_iterations: int = 10) -> Results
```

**Dependencies:**
- Data structures from `h-m2/code/`
- `openai` (revealed-only baseline)

**Complexity:** LOW (random_baseline), MEDIUM (revealed_only_baseline)

---

### 4. Experiment Runner (`code/experiment_runner.py`)

**Purpose:** Orchestrate data prep → execution → analysis pipeline.

**Phases:**
1. Data prep: curate problems, split tests, generate baseline codes
2. Agent execution: 50 problems × 10 iterations
3. Baseline execution: random + revealed-only
4. Analysis: slopes, permutation test

**Public API:**
```python
def prepare_data() -> DataPrep
def run_agent_experiment(data: DataPrep) -> AgentResults
def run_baselines(data: DataPrep) -> BaselineResults
def run_analysis(agent_results, baseline_results) -> Analysis
```

**Dependencies:** All code modules

**Complexity:** MEDIUM (orchestration logic + checkpointing)

---

### 5. Analysis (`code/analysis.py`)

**Purpose:** Compute slopes, statistical tests, visualizations.

**Public API:**
```python
def compute_slopes(results: Results) -> Slopes
def permutation_test(agent_slope, random_slope, n_samples=1000) -> float  # p-value
def plot_held_out_curves(agent_results, baseline_results) -> None
def generate_report(analysis: Analysis) -> str  # Markdown report
```

**Dependencies:**
- `scipy.stats` (permutation test, linear regression)
- `matplotlib` (plots)
- `numpy`, `pandas`

**Complexity:** MEDIUM (statistical tests + visualization)

---

## External Dependencies

### Python Packages
| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.0 | GPT-4 API |
| `scipy` | >=1.11 | Statistical tests |
| `matplotlib` | >=3.7 | Visualization |
| `requests` | >=2.31 | Codeforces API |
| `numpy` | >=1.24 | Numerical operations |
| `pandas` | >=2.0 | Data processing |
| `pyyaml` | >=6.0 | Config loading |

### External APIs
- **Codeforces API:** Public, no auth required
- **OpenAI API:** Requires API key in `OPENAI_API_KEY` env var

---

## File Organization

### Data Files
```
data/
├── problems.json              # 50 problem specs with test cases
├── test_splits.json           # {problem_id: {revealed: [idx], held_out: [idx]}}
├── baseline_codes/            # problem_XXX.py files
└── validation_checks.json     # {ks_test_p: 0.12, baseline_fail_rate: 0.85}
```

### Code Files
```
code/
├── pattern_memory.py          # 150 lines (Pattern class + PatternMemory)
├── agent.py                   # 300 lines (PatternLearningAgent + helpers)
├── random_baseline.py         # 100 lines (mutation operators + runner)
├── revealed_only_baseline.py  # 150 lines (GPT-4 revealed-only agent)
├── experiment_runner.py       # 400 lines (orchestration + checkpointing)
└── analysis.py                # 250 lines (slopes, tests, plots)
```

### Result Files
```
results/
├── agent_results.json         # [{problem_id, iteration, revealed_pass, held_out_pass}]
├── baseline_results.json      # {random: [...], revealed_only: [...]}
├── slope_analysis.json        # {agent_slope, random_slope, ratio, p_value, ...}
└── plots/
    ├── held_out_curves.png    # Line plot: held-out pass rate vs iteration
    └── pattern_usage.png      # Bar chart: pattern usage rate over iterations
```

---

## Proposed Tasks (Epic Level)

### Epic 1: Data Preparation Pipeline
**Complexity Score:** 6 (Module=2, Deps=1, Algo=2, Integration=1)
- Curate 50 Codeforces problems (API + filtering)
- Implement 50% revealed / 50% held-out split with stratification
- Generate baseline buggy codes (GPT-4 initial gen)
- Validation: KS test for difficulty distribution

**Estimated Subtasks:** 4

---

### Epic 2: Pattern Memory Module
**Complexity Score:** 10 (Module=3, Deps=2, Algo=4, Integration=1)
- Implement PatternMemory class (store/retrieve)
- Pattern similarity scoring (cosine similarity on embeddings)
- Pattern abstraction (normalize variable names, code structure)
- Usage tracking for pattern_usage_rate metric

**Estimated Subtasks:** 5-6

---

### Epic 3: Agent Implementation (GPT-4 + Memory)
**Complexity Score:** 15 (Module=4, Deps=3, Algo=6, Integration=2)
- PatternLearningAgent class
- extract_pattern() from revealed test errors
- retrieve_similar_patterns() with relevance filtering
- apply_pattern() to generate fixes
- Iterative fixing loop (10 iterations per problem)
- Held-out test execution (NO error message leakage)

**Estimated Subtasks:** 8-10

---

### Epic 4: Baseline Implementations
**Complexity Score:** 8 (Module=2, Deps=1, Algo=3, Integration=2)
- Random mutation baseline (mutation operators + runner)
- Revealed-only baseline (GPT-4 without memory)
- Test execution for held-out pass rate tracking
- Result logging

**Estimated Subtasks:** 4-5

---

### Epic 5: Experiment Orchestration
**Complexity Score:** 12 (Module=3, Deps=4, Algo=3, Integration=2)
- Experiment runner harness
- Phase sequencing (data → agent → baselines → analysis)
- Checkpointing for resumption
- Early stopping logic (p > 0.2 after 30 problems)
- Logging and progress tracking

**Estimated Subtasks:** 6-7

---

### Epic 6: Statistical Analysis & Visualization
**Complexity Score:** 10 (Module=3, Deps=2, Algo=4, Integration=1)
- Linear regression for slope computation (agent, random, revealed-only)
- Permutation test (1000 samples, p-value)
- Transfer efficiency metric (held-out slope / revealed slope)
- Plots: held-out pass rate curves, pattern usage
- Generate 04_validation.md report

**Estimated Subtasks:** 5-6

---

### Epic 7: Environment Setup & Infrastructure
**Complexity Score:** 4 (Module=1, Deps=2, Algo=0, Integration=1)
- Dependencies installation (requirements.txt)
- API key configuration (OpenAI)
- Folder structure creation
- Config file setup

**Estimated Subtasks:** 2

---

## Task Summary

| Epic | Description | Complexity | Est. Subtasks |
|------|-------------|------------|---------------|
| E1 | Data Preparation | 6 | 4 |
| E2 | Pattern Memory | 10 | 5-6 |
| E3 | Agent Implementation | 15 | 8-10 |
| E4 | Baselines | 8 | 4-5 |
| E5 | Orchestration | 12 | 6-7 |
| E6 | Analysis | 10 | 5-6 |
| E7 | Infrastructure | 4 | 2 |

**Total Epics:** 7  
**Complexity Range:** 4-15  
**Total Estimated Subtasks:** 34-40 (within FULL budget of 30-40 after refinement)

---

## Complexity Allocation

| Complexity Level | Epic Count | Total Complexity Points |
|------------------|------------|-------------------------|
| Very High (15+) | 1 (E3) | 15 |
| High (10-14) | 3 (E2, E5, E6) | 32 |
| Medium (6-9) | 2 (E1, E4) | 14 |
| Low (1-5) | 1 (E7) | 4 |

**Total Complexity:** 65 points across 7 Epics

---

## Integration Points

1. **h-m2 → h-m3:**
   - Reuse: Data loader, test execution engine
   - Extend: Add PatternMemory to agent architecture
   - Modify: Agent now tracks revealed vs held-out pass rates separately

2. **Data → Agent:**
   - Data module provides: Problem specs, test splits, baseline codes
   - Agent consumes: Revealed tests (with errors), held-out tests (pass/fail only)

3. **Agent → Analysis:**
   - Agent produces: Per-iteration pass rates (revealed + held-out)
   - Analysis consumes: Results JSON → slopes → statistical tests

4. **Baselines → Analysis:**
   - Baselines produce: Same result format as agent
   - Analysis compares: Agent slope vs random slope (primary metric)

---

## Design Decisions

### Decision 1: Pattern Representation
**Choice:** String-based error type + code region (not embeddings)  
**Rationale:** Simplicity first; upgrade to embeddings only if similarity scoring fails  
**ponytail:** Start with exact string match, add fuzzy matching if needed

### Decision 2: Test Split Stratification
**Choice:** Random split per problem, validate with KS test  
**Rationale:** Simple and provable (KS test p > 0.05)  
**Alternative:** Clustering by test input features (over-engineering for 15+ tests)

### Decision 3: Early Stopping
**Choice:** Check p-value after 30 problems  
**Rationale:** Balance statistical power vs compute cost  
**Risk:** May miss weak effects that need full 50 problems

---

## Quality Assurance

### Code Quality
- Type hints for all public APIs
- Docstrings for classes and functions
- Unit tests for pattern memory (store/retrieve correctness)

### Data Quality
- KS test for revealed/held-out difficulty distribution (p > 0.05)
- Baseline code validation (fails 3+ revealed tests)
- No test case overlap between revealed/held-out

### Reproducibility
- Fixed random seeds (data splits, baseline gen, mutations)
- Logged hyperparameters (temperature=0.7, top-p=0.95)
- Versioned data/code/results

---

## Next Steps

1. **Step 4:** Budget allocation (refine Epic subtask counts to fit 30 total)
2. **Step 5:** Generate Logic document (API signatures, algorithms)
3. **Step 6:** Generate Config document (hyperparameters, settings)
4. **Step 9:** Create 03_tasks.yaml (Epic tasks → detailed subtasks)

---

**Document Status:** Architecture Design Complete  
**Next Phase:** Budget Allocation (Step 4)
