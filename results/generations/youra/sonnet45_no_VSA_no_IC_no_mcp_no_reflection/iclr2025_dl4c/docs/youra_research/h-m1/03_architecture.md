# Architecture Specification: h-m1 Error Clustering Analyzer

**Date:** 2026-08-28  
**Hypothesis:** h-m1 (multi-test error clustering)  
**Gate:** MUST_WORK (clustering coefficient > 0.3, p < 0.05)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** Reference pattern from h-e1 (dataclass models, subprocess execution, result tracking)

---

## System Overview

**Components:**
- Data loader (Codeforces API + scraper)
- Debugging loop (GPT-4 agent + test executor)
- Annotation interface (human labeling workflow)
- Clustering analyzer (coefficient + permutation test)
- Visualization generator (figures for gate evaluation)

**Flow:** Load problems → Run agent debugging → Annotate errors → Compute clustering → Generate figures

---

## Module Breakdown

### 1. DataLoader (`src/data_loader.py`)

**Dependencies:** requests, json

```python
@dataclass
class TestCase:
    case_id: int
    input_data: str
    expected_output: str

@dataclass
class Problem:
    problem_id: str
    title: str
    rating: int
    solve_count: int
    test_cases: List[TestCase]

class CodeforcesLoader:
    def __init__(self, api_base_url: str, rate_limit: float): ...
    def fetch_problems(self, min_rating: int, max_rating: int, min_solves: int, limit: int) -> List[Problem]: ...
    def scrape_test_cases(self, problem_id: str) -> List[TestCase]: ...
    def save_dataset(self, problems: List[Problem], path: Path): ...
    def load_dataset(self, path: Path) -> List[Problem]: ...
```

---

### 2. DebugAgent (`src/debug_agent.py`)

**Dependencies:** openai, subprocess, dataclasses

```python
@dataclass
class TestExecution:
    case_id: int
    passed: bool
    actual_output: str
    error_message: str

@dataclass
class DebugIteration:
    iteration: int
    code: str
    test_results: List[TestExecution]
    passing_count: int
    failing_test_ids: List[int]

@dataclass
class DebugSession:
    problem_id: str
    iterations: List[DebugIteration]
    fix_sequence: List[int]  # Order of test IDs fixed

class GPT4DebugAgent:
    def __init__(self, model: str, temperature: float, api_key: str): ...
    def generate_initial_solution(self, problem: Problem) -> str: ...
    def fix_code(self, problem: Problem, failing_tests: List[TestExecution], current_code: str) -> str: ...

class TestExecutor:
    def __init__(self, timeout: float): ...
    def run_tests(self, code: str, test_cases: List[TestCase]) -> List[TestExecution]: ...
```

---

### 3. DebugLoop (`src/debug_loop.py`)

**Dependencies:** debug_agent, data_loader

```python
class DebugLoopRunner:
    def __init__(self, agent: GPT4DebugAgent, executor: TestExecutor, max_iterations: int): ...
    def run_session(self, problem: Problem) -> DebugSession: ...
    def track_fix_sequence(self, iterations: List[DebugIteration]) -> List[int]: ...
    def save_session(self, session: DebugSession, path: Path): ...
```

---

### 4. Annotator (`src/annotator.py`)

**Dependencies:** json, dataclasses

```python
@dataclass
class ErrorAnnotation:
    case_id: int
    problem_id: str
    error_type: str  # syntax | runtime | logic | edge_case
    annotator_id: str

@dataclass
class AnnotationSet:
    problem_id: str
    annotations: List[ErrorAnnotation]

class AnnotationManager:
    def __init__(self, output_dir: Path): ...
    def create_annotation_task(self, session: DebugSession, problem: Problem) -> dict: ...
    def load_annotations(self, path: Path) -> List[AnnotationSet]: ...
    def compute_kappa(self, annotations: List[AnnotationSet]) -> float: ...
    def resolve_conflicts(self, annotations: List[AnnotationSet]) -> dict: ...  # case_id -> error_type
```

---

### 5. ClusteringAnalyzer (`src/clustering_analyzer.py`)

**Dependencies:** numpy, scipy

```python
class ClusteringAnalyzer:
    def __init__(self, seed: int): ...
    def compute_clustering_coefficient(self, fix_sequence: List[int], error_labels: dict) -> float: ...
    def permutation_test(self, fix_sequence: List[int], error_labels: dict, n_permutations: int) -> float: ...
    def analyze_session(self, session: DebugSession, error_labels: dict) -> dict: ...  # {coeff, p_value, observed, expected}
```

---

### 6. Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class FigureGenerator:
    def __init__(self, output_dir: Path): ...
    def plot_clustering_comparison(self, agent_coeff: float, random_coeff: float, p_value: float) -> Path: ...
    def plot_error_distribution(self, error_labels: dict) -> Path: ...
    def plot_fix_sequence_heatmap(self, sessions: List[DebugSession], error_labels: dict) -> Path: ...
    def plot_annotator_agreement(self, annotations: List[AnnotationSet], kappa: float) -> Path: ...
```

---

### 7. Experiment Runner (`run_experiment.py`)

**Dependencies:** All modules above

```python
def main():
    # Load data
    loader = CodeforcesLoader(...)
    problems = loader.fetch_problems(min_rating=1200, max_rating=1800, min_solves=1000, limit=50)
    
    # Run debugging sessions
    agent = GPT4DebugAgent(model="gpt-4-turbo-2024-04-09", temperature=0.7, api_key=...)
    executor = TestExecutor(timeout=5.0)
    runner = DebugLoopRunner(agent, executor, max_iterations=10)
    
    sessions = [runner.run_session(p) for p in problems]
    
    # Annotation (manual step)
    annotator = AnnotationManager(output_dir=Path("data/annotations"))
    for session in sessions:
        task = annotator.create_annotation_task(session, problem)
        # Save task for human annotators
    
    # Load annotations and analyze
    annotations = annotator.load_annotations(Path("data/annotations/annotated.json"))
    kappa = annotator.compute_kappa(annotations)
    assert kappa > 0.7, f"Inter-annotator agreement too low: {kappa:.3f}"
    
    error_labels = annotator.resolve_conflicts(annotations)
    
    # Clustering analysis
    analyzer = ClusteringAnalyzer(seed=1)
    results = [analyzer.analyze_session(s, error_labels) for s in sessions]
    
    agent_coeff = np.mean([r['coeff'] for r in results])
    p_value = np.mean([r['p_value'] for r in results])
    
    # Generate figures
    visualizer = FigureGenerator(output_dir=Path("figures"))
    visualizer.plot_clustering_comparison(agent_coeff, random_coeff=1/4, p_value=p_value)
    visualizer.plot_error_distribution(error_labels)
    visualizer.plot_fix_sequence_heatmap(sessions, error_labels)
    visualizer.plot_annotator_agreement(annotations, kappa)
    
    # Gate evaluation
    gate_pass = agent_coeff > 0.3 and p_value < 0.05
    print(f"Gate: {'PASS' if gate_pass else 'PIVOT'} (coeff={agent_coeff:.3f}, p={p_value:.4f})")
```

---

## Data Flow

**End-to-End Pipeline:**
1. `CodeforcesLoader.fetch_problems()` → List[Problem] (50 problems, 15+ tests each)
2. `DebugLoopRunner.run_session()` → DebugSession (fix sequence tracked)
3. `AnnotationManager.create_annotation_task()` → JSON task file (human annotators label)
4. `AnnotationManager.load_annotations()` → AnnotationSet (2-3 labels per test failure)
5. `AnnotationManager.compute_kappa()` → float (validate agreement > 0.7)
6. `AnnotationManager.resolve_conflicts()` → dict (case_id → error_type)
7. `ClusteringAnalyzer.analyze_session()` → dict (coeff, p_value)
8. `FigureGenerator.plot_*()` → PNG files (figures/)

---

## Interface Contracts

### Input/Output Specifications

**DataLoader:**
- Input: Codeforces API endpoint, rating range, solve count threshold
- Output: `List[Problem]` (50 problems × 15+ test cases)

**DebugAgent:**
- Input: Problem statement, failing test executions, current code
- Output: Fixed code (string)

**DebugLoop:**
- Input: Problem, agent, executor, max_iterations
- Output: DebugSession (iterations, fix_sequence)

**Annotator:**
- Input: DebugSession (test failures)
- Output: AnnotationSet (error_type labels), Cohen's kappa

**ClusteringAnalyzer:**
- Input: fix_sequence (List[int]), error_labels (dict)
- Output: {coeff: float, p_value: float, observed: float, expected: float}

**Visualizer:**
- Input: Clustering results, error labels, annotation data
- Output: PNG files (4 figures)

---

## File Structure

```
experiments/h-m1/
├── run_experiment.py          # Main entry point
├── src/
│   ├── data_loader.py         # Codeforces API + scraper
│   ├── debug_agent.py         # GPT-4 agent + test executor
│   ├── debug_loop.py          # Multi-iteration debugging session
│   ├── annotator.py           # Human annotation workflow
│   ├── clustering_analyzer.py # Clustering coefficient + permutation test
│   └── visualizer.py          # Figure generation
├── data/
│   ├── problems.json          # Fetched problems (50)
│   ├── sessions/              # Debugging sessions (50 JSON files)
│   └── annotations/           # Human annotations (JSON)
├── figures/                   # Output visualizations
│   ├── clustering_comparison.png
│   ├── error_distribution.png
│   ├── fix_sequence_heatmap.png
│   └── annotator_agreement.png
└── config.py                  # Experiment config (seed, API keys, thresholds)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Data pipeline | Codeforces loader + scraper (API rate limits, test case parsing) | 12 | 3+3+3+3 (API, scraper, validation, save/load) |
| M-2 | Debug agent | GPT-4 interface + subprocess executor (timeout, error capture) | 14 | 4+4+3+3 (agent, executor, retry logic, session tracking) |
| M-3 | Debug loop | Multi-iteration runner (fix sequence tracking, termination) | 10 | 3+3+2+2 (runner, sequence tracking, save, tests) |
| M-4 | Annotation system | Task generation + conflict resolution (kappa computation) | 11 | 3+3+3+2 (task gen, loader, kappa, resolve) |
| M-5 | Clustering metrics | Coefficient + permutation test (1000 shuffles) | 13 | 4+4+3+2 (coeff, permutation, stats, validation) |
| M-6 | Visualization | 4 figure types (clustering, distribution, heatmap, kappa) | 10 | 3+2+3+2 (clustering, distribution, heatmap, kappa) |
| M-7 | Integration | End-to-end runner + gate evaluation (logging, error handling) | 8 | 3+2+2+1 (runner, gate logic, logging, tests) |

**Distribution:**  
- VeryHigh (18-20): []  
- High (14-17): [M-2]  
- Medium (9-13): [M-1, M-3, M-4, M-5, M-6]  
- Low (4-8): [M-7]

**Total:** 7 epic tasks, 78 complexity points

---

## Design Decisions

### Key Choices

1. **Subprocess isolation for test execution**: Prevents code crashes from killing agent process
2. **Human annotation bottleneck**: No automated labeling in PoC (requires reliable ground truth first)
3. **Permutation test for p-value**: Non-parametric method (no distribution assumptions)
4. **Cohen's kappa threshold (0.7)**: Standard inter-annotator agreement cutoff
5. **Max 10 iterations**: Balance between exploration and API cost

### Trade-offs

- **Manual annotation** → 3-5 hours per annotator → bottleneck BUT higher quality than auto-labeling
- **API rate limits (10 req/min)** → ~5 min to fetch 50 problems → acceptable for batch evaluation
- **Fixed GPT-4 model** → reproducibility BUT may not reflect latest model performance

### Error Handling

- Codeforces API failure → retry 3x with exponential backoff (2s, 4s, 8s)
- Test execution timeout (5s) → log error, mark as "execution_failed"
- Agent timeout → abort iteration, use last valid code
- Kappa < 0.7 → log warning, flag for re-annotation or problem discard

---

## Validation Checklist

### Implementation Complete When:
- [ ] 50 problems loaded (rating 1200-1800, 15+ tests each)
- [ ] All debugging sessions run (10 iterations or convergence)
- [ ] 750 test failures annotated (2-3 labels each)
- [ ] Kappa > 0.7 verified
- [ ] Clustering coefficient + p-value computed
- [ ] 4 figures generated and saved
- [ ] Gate logic executes: `assert coeff > 0.3 and p < 0.05`

### Output Artifacts:
- `data/problems.json` (50 problems)
- `data/sessions/*.json` (50 session files)
- `data/annotations/annotated.json` (human labels)
- `figures/*.png` (4 figures)
- `04_validation.md` (gate decision report)

---

## Dependencies

### External APIs
- OpenAI API (GPT-4 Turbo): `openai>=1.0.0`
- Codeforces API: `requests`

### Python Libraries
```
openai>=1.0.0
requests>=2.31.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0  # Cohen's kappa
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Runtime
- Python 3.10+
- Environment variables: `OPENAI_API_KEY`

---

## Assumptions

1. Codeforces API stable (rate limits: 10 req/min)
2. GPT-4 Turbo API accessible (no quota exhaustion)
3. Annotators have programming expertise (can distinguish syntax vs logic errors)
4. 50 problems sufficient for p < 0.05 (power analysis assumes medium effect size)
5. Test execution deterministic (same input → same output)

---

*Next Phase: Phase 4 Implementation*
