# Architecture Document: h-m1

**Date:** 2026-08-25  
**Author:** Phase 3 Architecture Agent  
**Hypothesis:** h-m1 - MECHANISM hypothesis on specification completeness and test-intent capture  
**Source:** 03_prd.md, 02c_experiment_brief.md  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: h-e1 code analyzed  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Findings**: h-e1 implements complete correlation study with generator, feedback collectors, correlation analysis. Reusable: generator, execution/AI/human feedback, data loader patterns.

---

## Knowledge Base Patterns (Archon)

Applied: Disagreement analysis pipeline, qualitative coding framework, statistical comparison patterns (chi-square contingency test)

---

## System Overview

h-m1 extends h-e1 infrastructure with:
- SWE-bench dataset loader
- Disagreement case extraction (exec/human mismatch)
- Qualitative coding framework
- Statistical comparison across task types

**Reuse Strategy (70%+ from h-e1):**
- CodeGen model wrapper
- Execution/AI feedback collectors
- Data loading pattern
- Basic analysis utilities

**New Components (30%):**
- SWE-bench loader + test harness integration
- Disagreement extractor
- Qualitative coding module
- Chi-square statistical tests

---

## Module Specifications

### 1. Data Loaders

#### `data/loader.py` (REUSE h-e1)

**Dependencies**: datasets, h-e1/code/data/loader.py

```python
@dataclass
class Problem:
    id: str
    prompt: str
    tests: List[str]
    dataset: str

def load_humaneval(n_samples: int = 100) -> List[Problem]: ...
def load_mbpp(n_samples: int = 100, seed: int = 42) -> List[Problem]: ...
```

#### `data/swebench_loader.py` (NEW)

**Dependencies**: datasets

```python
@dataclass
class SWEBenchIssue:
    id: str
    problem_statement: str
    repo: str
    base_commit: str
    patch: str
    test_patch: str

def load_swebench_lite(n_samples: int = 100, seed: int = 42) -> List[SWEBenchIssue]: ...
```

#### `data/load_h_e1_results.py` (NEW)

**Dependencies**: json, pathlib

```python
@dataclass
class H_E1_Sample:
    dataset: str  # "humaneval" | "mbpp"
    id: str
    code: str
    exec: int
    ai: float
    human: float

def load_h_e1_feedback() -> List[H_E1_Sample]: ...
```

---

### 2. Code Generation

#### `models/generator.py` (REUSE h-e1)

**Dependencies**: transformers, torch, h-e1/code/models/generator.py

```python
class CodeGenModel:
    def __init__(self, model_name: str = "Salesforce/codegen-350M-mono"): ...
    def generate(self, prompt: str, temperature: float = 0.8, max_tokens: int = 256) -> str: ...
    def batch_generate(self, prompts: List[str], batch_size: int = 4) -> List[str]: ...
```

#### `models/swebench_generator.py` (NEW)

**Dependencies**: CodeGenModel

```python
class SWEBenchGenerator:
    def __init__(self, base_model: CodeGenModel): ...
    def generate_patch(self, issue: SWEBenchIssue) -> str: ...
    def batch_generate_patches(self, issues: List[SWEBenchIssue]) -> List[str]: ...
```

---

### 3. Feedback Collection

#### `eval/feedback.py` (EXTEND h-e1)

**Dependencies**: subprocess, tempfile, numpy, h-e1/code/eval/feedback.py

```python
def execute_code(code: str, tests: List[str], timeout: int = 5) -> int: ...
def ai_score(prompt: str, code: str) -> float: ...
def simulate_human_ratings(code: str, execution_result: int, seed: int) -> List[float]: ...
def collect_execution_feedback(problems, codes: List[str]) -> List[int]: ...
def collect_ai_feedback(problems, codes: List[str]) -> List[float]: ...
def collect_human_feedback(problems, codes: List[str], exec_results: List[int]) -> List[float]: ...
```

#### `eval/swebench_exec.py` (NEW)

**Dependencies**: subprocess, docker

```python
def execute_swebench_patch(
    issue: SWEBenchIssue,
    patch: str,
    timeout: int = 60
) -> int: ...
    """Apply patch, run tests in Docker container. Returns 1 if pass, 0 if fail."""

def batch_execute_patches(issues: List[SWEBenchIssue], patches: List[str]) -> List[int]: ...
```

---

### 4. Disagreement Analysis (NEW)

#### `analysis/disagreements.py`

**Dependencies**: numpy, pandas

```python
@dataclass
class DisagreementCase:
    sample_id: str
    task_type: str  # "humaneval" | "mbpp" | "swebench"
    exec_result: int
    human_rating: float
    disagreement_type: str  # "exec_pass_human_low" | "exec_fail_human_high"
    code: str
    problem: str

def extract_disagreements(
    samples: List[Sample],
    threshold: float = 3.0
) -> List[DisagreementCase]: ...
    """Extract cases where exec=1 & human<3 OR exec=0 & human>3."""

def export_disagreements(cases: List[DisagreementCase], output_path: str) -> None: ...
```

---

### 5. Qualitative Coding (NEW)

#### `analysis/qualitative_coding.py`

**Dependencies**: json

```python
INTENT_DIMENSIONS = [
    "correctness",
    "edge_cases",
    "readability",
    "efficiency",
    "maintainability",
    "security"
]

@dataclass
class CodedResult:
    sample_id: str
    task_type: str
    disagreement_type: str
    missed_dimensions: List[str]
    notes: str

def load_coding_interface(cases: List[DisagreementCase]) -> None: ...
    """Interactive CLI to manually code disagreement cases."""

def save_coded_results(results: List[CodedResult], output_path: str) -> None: ...
def load_coded_results(input_path: str) -> List[CodedResult]: ...
```

---

### 6. Statistical Analysis (NEW)

#### `analysis/statistical_tests.py`

**Dependencies**: scipy, numpy, pandas

```python
@dataclass
class ChiSquareResult:
    statistic: float
    p_value: float
    dof: int
    observed: np.ndarray
    expected: np.ndarray

@dataclass
class TaskTypeStats:
    task_type: str
    total_disagreements: int
    missed_count: int
    missed_rate: float
    ci_95_lower: float
    ci_95_upper: float

def compute_chi_square(coded_results: List[CodedResult]) -> ChiSquareResult: ...
    """Test if missed dimension rates differ by task type."""

def compute_effect_size(coded_results: List[CodedResult]) -> Dict[str, float]: ...
    """Compute SWE-bench/HumanEval and SWE-bench/MBPP rate ratios."""

def bootstrap_ci(
    coded_results: List[CodedResult],
    task_type: str,
    n_bootstrap: int = 1000
) -> Tuple[float, float]: ...
    """95% CI for missed dimension rate via bootstrap."""

def summarize_by_task_type(coded_results: List[CodedResult]) -> Dict[str, TaskTypeStats]: ...
```

---

### 7. Visualization (NEW)

#### `analysis/visualize.py`

**Dependencies**: matplotlib, seaborn, pandas

```python
def plot_missed_dimensions_comparison(
    stats: Dict[str, TaskTypeStats],
    output_path: str
) -> None: ...
    """Bar chart: % disagreements with missed dimensions by task type."""

def plot_disagreement_type_distribution(
    coded_results: List[CodedResult],
    output_path: str
) -> None: ...
    """Stacked bar chart: exec_pass/human_low vs exec_fail/human_high."""

def plot_intent_dimension_heatmap(
    coded_results: List[CodedResult],
    output_path: str
) -> None: ...
    """Heatmap: intent dimensions × task types."""

def export_qualitative_examples_table(
    coded_results: List[CodedResult],
    n_per_task: int = 3,
    output_path: str
) -> None: ...
    """Markdown table with code snippets."""
```

---

### 8. Orchestration

#### `run_experiment.py` (NEW)

**Dependencies**: All modules above

```python
def main():
    # 1. Load h-e1 results (HumanEval/MBPP)
    # 2. Load SWE-bench dataset
    # 3. Generate SWE-bench patches
    # 4. Collect feedback (exec/ai/human) for SWE-bench
    # 5. Extract disagreement cases (all 3 datasets)
    # 6. Manual qualitative coding
    # 7. Statistical analysis
    # 8. Generate visualizations
    # 9. Export validation report
    ...
```

#### `config.py` (NEW)

**Dependencies**: None

```python
@dataclass
class ExperimentConfig:
    # Paths
    h_e1_results_path: str
    swebench_output_dir: str
    figures_dir: str
    
    # Dataset params
    n_swebench_samples: int = 100
    swebench_seed: int = 42
    
    # Generation params
    model_name: str = "Salesforce/codegen-350M-mono"
    temperature: float = 0.8
    max_tokens: int = 512
    
    # Analysis params
    disagreement_threshold: float = 3.0
    n_bootstrap: int = 1000
    alpha: float = 0.05
    
    # Gate thresholds
    min_effect_size: float = 2.0
    max_p_value: float = 0.05
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| CodeGenModel | `from h_e1.code.models.generator import CodeGenModel` | `h-e1/code/models/generator.py` |
| Problem | `from h_e1.code.data.loader import Problem, load_humaneval, load_mbpp` | `h-e1/code/data/loader.py` |
| Feedback collectors | `from h_e1.code.eval.feedback import execute_code, ai_score, simulate_human_ratings` | `h-e1/code/eval/feedback.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## Data Flow

```
1. h-e1 results → load_h_e1_results() → 100 samples (HumanEval/MBPP) with feedback
2. SWE-bench Lite → load_swebench_lite() → 100 issues
3. Issues → SWEBenchGenerator → 100 patches
4. Patches → execute_swebench_patch() → execution feedback (0/1)
5. Patches → ai_score() → AI scores (0-1)
6. Patches → simulate_human_ratings() → human ratings (0-1)
7. All samples → extract_disagreements() → disagreement cases (~30-50 expected)
8. Cases → load_coding_interface() → manually coded with missed dimensions
9. Coded results → compute_chi_square() → statistical test
10. Coded results → visualize → 4 figures
11. All outputs → 04_validation.md report
```

---

## File Organization

```
h-m1/code/
├── config.py                       # Experiment configuration
├── run_experiment.py               # Main orchestrator
├── data/
│   ├── __init__.py
│   ├── loader.py                   # REUSE h-e1 (HumanEval/MBPP)
│   ├── swebench_loader.py          # NEW (SWE-bench Lite loader)
│   └── load_h_e1_results.py        # NEW (load h-e1 feedback data)
├── models/
│   ├── __init__.py
│   ├── generator.py                # REUSE h-e1 (CodeGen wrapper)
│   └── swebench_generator.py       # NEW (repo-level patch generation)
├── eval/
│   ├── __init__.py
│   ├── feedback.py                 # REUSE h-e1 (exec/AI/human feedback)
│   └── swebench_exec.py            # NEW (SWE-bench test harness)
├── analysis/
│   ├── __init__.py
│   ├── disagreements.py            # NEW (disagreement extraction)
│   ├── qualitative_coding.py       # NEW (manual coding interface)
│   ├── statistical_tests.py        # NEW (chi-square, bootstrap CI)
│   └── visualize.py                # NEW (4 figures)
└── outputs/
    ├── swebench_samples.jsonl
    ├── swebench_feedback.jsonl
    ├── disagreements.csv
    ├── coded_results.json
    └── statistical_results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | h-e1 data integration | Load h-e1 results, standardize format | 6 | 2 (read h-e1 outputs) + 2 (schema mapping) + 2 (validation) |
| M1-2 | SWE-bench infrastructure | Dataset loader + Docker harness setup | 12 | 3 (dataset API) + 5 (Docker integration) + 2 (test exec) + 2 (error handling) |
| M1-3 | SWE-bench generation | Generate 100 patches using CodeGen | 8 | 2 (prompt formatting) + 4 (batch generation) + 2 (save outputs) |
| M1-4 | Feedback collection | Exec/AI/human feedback for SWE-bench | 10 | 4 (exec via Docker) + 2 (AI scoring reuse) + 4 (human rating simulation) |
| M1-5 | Disagreement extraction | Extract cases where exec/human disagree | 7 | 3 (threshold logic) + 2 (filtering) + 2 (export CSV) |
| M1-6 | Qualitative coding | Manual coding interface + results storage | 14 | 4 (CLI interface) + 6 (coding workflow) + 2 (JSON save) + 2 (validation) |
| M1-7 | Statistical analysis | Chi-square test, effect size, bootstrap CI | 11 | 4 (contingency table) + 3 (chi-square) + 2 (effect size) + 2 (bootstrap) |
| M1-8 | Visualization | 4 figures (bar chart, stacked bar, heatmap, examples) | 13 | 3×3 (3 charts) + 4 (examples table) |
| M1-9 | Validation report | 04_validation.md with results + gate decision | 9 | 3 (stats summary) + 4 (qualitative examples) + 2 (gate logic) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M1-6], Medium(9-13): [M1-2, M1-4, M1-7, M1-8, M1-9], Low(4-8): [M1-1, M1-3, M1-5]

---

## Technology Stack

**Core Dependencies:**
- Python 3.10+
- transformers==4.36.0 (CodeGen model)
- datasets==2.16.0 (HuggingFace datasets)
- torch==2.1.0 (model inference)
- scipy==1.11.4 (statistical tests)
- matplotlib==3.8.2, seaborn==0.13.0 (visualization)
- pandas==2.1.4, numpy==1.26.2 (data manipulation)
- docker (SWE-bench test harness)

**Hardware:**
- GPU: 1× A100 40GB
- RAM: 64GB
- Storage: 10GB

---

## Error Handling

**Generation Failures:**
- Log sample_id + error message
- Skip sample, continue batch
- Warn if >10% failure rate

**Test Harness Failures:**
- Docker container errors → mark exec=0
- Timeout (>60s) → mark exec=0
- Log all failures for review

**Insufficient Disagreement Cases:**
- If <10 cases per dataset → lower threshold from 3.0 to 2.5
- If still insufficient → increase SWE-bench samples to 200

**Manual Coding Errors:**
- Validate missed_dimensions against taxonomy
- Reject invalid dimension names
- Allow empty missed_dimensions list (tests captured intent)

---

## Self-Validation

- [x] No ASCII diagrams (used bullet lists)
- [x] Module sections = interface code only
- [x] 9 Epic tasks with complexity scores
- [x] Codebase Analysis section included
- [x] External Dependencies section (h-e1 imports)
- [x] Import paths verified from actual code
- [x] Total length < 500 lines
