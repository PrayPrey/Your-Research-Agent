# Architecture Design: H-E1 Proxy Metric Validation System

**Date:** 2026-07-09  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Author:** Architecture Agent  

---

## Knowledge Base Pattern

Applied: Metric configuration pattern (declarative config with explicit sample sizes, reproducibility controls)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing codebase - implementing proxy metric validation system for code generation

---

## System Overview

**Purpose**: Validate measurement reliability of 3 proxy metrics (CodeBLEU, runtime efficiency, PR-style score) for code generation quality assessment.

**Architecture Pattern**: Pipeline-based measurement system with statistical validation.

**Components**:
- Data: HumanEval dataset + controlled complexity tasks
- Generation: CodeLlama-7B solution generator
- Measurement: 3 proxy metric evaluators
- Analysis: Statistical reliability validators (CV, Cohen's d, Spearman ρ)
- Reporting: Gate validation visualizations

---

## Module Structure

### DataModule (`src/data/dataset.py`)

**Dependencies**: datasets, human_eval

```python
class HumanEvalLoader:
    def __init__(self, problem_count: int = 50, seed: int = 42): ...
    def load_problems(self) -> List[Dict]: ...
    def select_stratified_subset(self) -> List[Dict]: ...

class ControlledTaskGenerator:
    def generate_complexity_tasks(self) -> List[Dict]: ...
    def create_labeled_solutions(self, complexity: str) -> str: ...
```

### SolutionGenerator (`src/generation/generator.py`)

**Dependencies**: transformers, torch

```python
class CodeLlamaGenerator:
    def __init__(self, model_name: str, device: str, dtype: str): ...
    def load_model(self) -> None: ...
    def generate_solutions(self, prompt: str, num_solutions: int) -> List[str]: ...
    def batch_generate(self, problems: List[Dict]) -> Dict[str, List[str]]: ...
```

### ProxyMetrics (`src/metrics/proxies.py`)

**Dependencies**: codebleu, subprocess, scipy

```python
class CodeBLEUMetric:
    def __init__(self, lang: str = "python", weights: Tuple = (0.25, 0.25, 0.25, 0.25)): ...
    def compute(self, reference: str, prediction: str) -> Dict[str, float]: ...
    def batch_compute(self, refs: List[str], preds: List[str]) -> List[Dict]: ...

class RuntimeEfficiencyMetric:
    def __init__(self, tool: str = "perf", event: str = "instructions"): ...
    def count_instructions(self, code: str, test_inputs: List) -> int: ...
    def compute_ratio(self, solution_count: int, reference_count: int) -> float: ...

class PRStyleMetric:
    def __init__(self, implementation: str = "placeholder"): ...
    def compute(self, code: str) -> float: ...
```

### ReliabilityAnalysis (`src/analysis/reliability.py`)

**Dependencies**: numpy, scipy.stats

```python
class ReliabilityValidator:
    def compute_cv(self, measurements: List[float]) -> float: ...
    def compute_cohens_d(self, group1: List[float], group2: List[float]) -> float: ...
    def compute_spearman_rho(self, ranks1: List[float], ranks2: List[float]) -> Tuple[float, float]: ...
    def validate_gate_criteria(self, cv: float, d: float, rho: float) -> bool: ...
```

### Visualization (`src/visualization/plots.py`)

**Dependencies**: matplotlib, seaborn

```python
class GateMetricsPlotter:
    def plot_gate_comparison(self, metrics: Dict, thresholds: Dict) -> Figure: ...
    def plot_cv_distribution(self, cvs: List[float]) -> Figure: ...
    def plot_complexity_separation(self, data: Dict) -> Figure: ...
    def plot_cross_hardware_correlation(self, aws_ranks: List, local_ranks: List) -> Figure: ...
    def save_all_figures(self, output_dir: str) -> None: ...
```

### ExperimentOrchestrator (`src/orchestrator.py`)

**Dependencies**: All above modules

```python
class ExperimentPipeline:
    def __init__(self, config: Dict): ...
    def run_solution_generation(self) -> Dict[str, List[str]]: ...
    def run_metric_measurement(self, solutions: Dict) -> Dict: ...
    def run_reliability_analysis(self, measurements: Dict) -> Dict: ...
    def run_cross_hardware_validation(self) -> Dict: ...
    def generate_report(self) -> None: ...
    def execute(self) -> Dict: ...
```

### Configuration (`config.py`)

**Dependencies**: yaml, pydantic

```python
class DatasetConfig:
    name: str = "HumanEval"
    source: str = "openai/openai_humaneval"
    problem_count: int = 50
    problem_selection_seed: int = 42

class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    dtype: str = "float16"
    device_map: str = "auto"
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    num_solutions_per_problem: int = 10

class MetricConfig:
    codebleu_weights: Tuple = (0.25, 0.25, 0.25, 0.25)
    runtime_tool: str = "perf"
    runtime_event: str = "instructions"
    runtime_repetitions: int = 5
    pr_style_implementation: str = "placeholder"

class ThresholdConfig:
    cv_max: float = 5.0
    cohens_d_min: float = 0.8
    spearman_rho_min: float = 0.8

class ExperimentConfig:
    dataset: DatasetConfig
    model: ModelConfig
    metrics: MetricConfig
    thresholds: ThresholdConfig
    seed: int = 42
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig": ...
    def to_yaml(self, path: str) -> None: ...
```

### Main Entry (`main.py`)

**Dependencies**: orchestrator, config, logging

```python
def setup_logging(log_file: str) -> None: ...
def load_config(config_path: str) -> ExperimentConfig: ...
def main(config_path: str) -> None: ...
```

---

## File Organization

```
h-e1/
├── config.yaml                    # Experiment configuration
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── dataset.py             # HumanEval + controlled tasks
│   ├── generation/
│   │   ├── __init__.py
│   │   └── generator.py           # CodeLlama solution generation
│   ├── metrics/
│   │   ├── __init__.py
│   │   └── proxies.py             # 3 proxy metrics
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── reliability.py         # CV, Cohen's d, Spearman ρ
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py               # Gate metrics figures
│   └── orchestrator.py            # Pipeline controller
├── data/                          # Downloaded datasets (cache)
├── models/                        # Downloaded models (cache)
├── outputs/                       # Results
│   ├── solutions/                 # Generated code
│   ├── measurements/              # Metric values
│   └── figures/                   # Visualizations
└── logs/
    └── experiment.log
```

---

## Data Flow

1. **Load Data** → HumanEvalLoader selects 50 problems
2. **Generate Solutions** → CodeLlamaGenerator creates 10 solutions/problem (500 total)
3. **Measure Proxies** → Each metric measured 5 times/solution (2,500 measurements)
4. **Analyze Reliability** → Compute CV, Cohen's d, Spearman ρ
5. **Validate Gate** → Check thresholds (CV≤5%, d≥0.8, ρ≥0.8)
6. **Generate Report** → Create figures + validation summary

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Setup | Load HumanEval + generate controlled tasks | 8 | 2+2+2+2 (load+stratify+controlled+verify) |
| A-2 | Solution Generation | CodeLlama setup + solution generation | 12 | 3+3+4+2 (model+batch+generation+cache) |
| A-3 | Proxy Metrics | Implement CodeBLEU + runtime + PR-style | 14 | 4+5+3+2 (codebleu+perf+placeholder+integration) |
| A-4 | Reliability Analysis | CV, Cohen's d, Spearman ρ computation | 10 | 3+3+3+1 (cv+cohens+spearman+validation) |
| A-5 | Visualization | Gate metrics + distribution plots | 9 | 3+2+2+2 (gate_plot+cv_hist+separation+scatter) |
| A-6 | Pipeline Integration | Orchestrator + config + main | 11 | 4+3+2+2 (orchestrator+config+logging+entry) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-6], Low(4-8): [A-1, A-5]

**Complexity Scoring**:
- Module_Size (1-5): Lines of code
- Dependencies (1-5): External library complexity
- Algorithm (1-5): Implementation difficulty
- Integration (1-5): Cross-module coordination

---

## Key Design Decisions

**Measurement Stability**: Using CPU instruction count (perf) instead of wall-clock time eliminates I/O/scheduling noise (COFFE 2025).

**Placeholder for PR-Style**: Third proxy is placeholder returning random scores - requires SWE-bench PR data training (out of PoC scope).

**Checkpointing**: Save after each problem's solutions to enable resume on failure.

**Reproducibility**: Fixed seeds (42) + deterministic GPU operations + versioned dependencies.

---

## Success Criteria Mapping

| Criterion | Module | Validation |
|-----------|--------|------------|
| CV ≤ 5% | ReliabilityValidator.compute_cv | Pass if mean CV across all solutions ≤ 5% |
| Cohen's d ≥ 0.8 | ReliabilityValidator.compute_cohens_d | Pass if O(n) vs O(n²) separation ≥ 0.8 |
| Spearman ρ ≥ 0.8 | ReliabilityValidator.compute_spearman_rho | Pass if cross-hardware correlation ≥ 0.8 |

**Gate Pass**: ≥1 proxy passes all 3 criteria → Proceed to H-E2 with validated proxy set

---

## External Dependencies

```txt
# Core ML
torch>=2.1.0
transformers>=4.35.0
accelerate>=0.24.0

# Datasets
datasets>=2.14.0
human-eval>=1.0.0

# Metrics
codebleu>=0.7.0
scipy>=1.11.0
numpy>=1.24.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Configuration
pyyaml>=6.0
pydantic>=2.0.0

# Logging
tqdm>=4.66.0
```

---

## Risk Mitigation

**perf unavailable**: Fallback to wall-clock time with median of 10 runs (documented in NFR-3).

**GPU OOM**: Use fp16 (14GB peak on 16GB GPU) + gradient checkpointing if needed.

**Low measurement stability**: Increase repetitions 5→10, control system load.

---

**Architecture Status**: Ready for Phase 4 Implementation  
**Next Phase**: Phase 4 - PoC Coder (Epic tasks A-1 through A-6)
