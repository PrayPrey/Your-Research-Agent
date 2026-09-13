# System Architecture: h-m1
# Hypothesis: Static Analysis Cascade Routing Mechanism

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (System Architect)
**Applied:** DL experiment minimal architecture pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-e1 implementation (monolithic single-file structure)
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-e1/code/
**Findings:** H-e1 uses monolithic run_experiment.py with integrated classes. Will follow same pattern for consistency. No modular src/ structure - all components in single script.

---

## System Overview

MECHANISM hypothesis validating cascade feedback routing. Extends h-e1 by adding sequential static-first feedback mechanism.

**Pipeline Stages:**
1. Task loading (reuse N=35 from h-e1)
2. Code generation (K=20 samples, CodeLlama-7B)
3. **Cascade routing** (mypy FIRST → pytest conditional)
4. Baseline comparison (aggregation routing)
5. Error detection rate calculation

**Success Criterion:** Mypy error detection rate ≥30%

---

## Module Structure

### DatasetLoader (`code/run_experiment.py` - HumanEvalLoader class)

**Dependencies:** evalplus, human_eval

```python
class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True): ...
    def load_problems(self) -> Dict[str, Dict]: ...
    def load_qualified_tasks(self, h_e1_validation_path: str) -> List[str]: ...
```

---

### CodeGenerator (`code/run_experiment.py` - CodeLlamaGenerator class)

**Dependencies:** transformers, torch

```python
class CodeLlamaGenerator:
    def __init__(self, config: ExperimentConfig): ...
    def load_model(self) -> None: ...
    def generate_samples(self, prompt: str, k: int = 20) -> List[str]: ...
    def set_seed(self, seed: int) -> None: ...
```

---

### MypyVerifier (`code/run_experiment.py` - MypyVerifier class)

**Dependencies:** subprocess, tempfile

```python
class MypyVerifier:
    def __init__(self, timeout: int = 10): ...
    def verify(self, code: str) -> Dict[str, any]: ...
    def parse_errors(self, output: str) -> List[Dict]: ...
```

---

### PytestVerifier (`code/run_experiment.py` - PytestVerifier class)

**Dependencies:** subprocess, tempfile, evalplus

```python
class PytestVerifier:
    def __init__(self, timeout: int = 120): ...
    def verify(self, code: str, test_code: str, entry_point: str) -> Dict[str, any]: ...
    def parse_failures(self, output: str) -> List[str]: ...
```

---

### StaticAnalysisFeedbackRouter (`code/run_experiment.py` - core mechanism)

**Dependencies:** MypyVerifier, PytestVerifier, CodeLlamaGenerator

```python
class StaticAnalysisFeedbackRouter:
    def __init__(self, generator: CodeLlamaGenerator, max_retries: int = 5): ...
    def generate_with_feedback(self, task_prompt: str, task_id: str, test_code: str) -> Dict: ...
    def format_mypy_feedback(self, errors: List[Dict]) -> str: ...
    def format_pytest_feedback(self, failures: List[str]) -> str: ...
```

---

### AggregationFeedbackRouter (`code/run_experiment.py` - baseline)

**Dependencies:** MypyVerifier, PytestVerifier, CodeLlamaGenerator

```python
class AggregationFeedbackRouter:
    def __init__(self, generator: CodeLlamaGenerator, max_retries: int = 5): ...
    def generate_with_feedback(self, task_prompt: str, task_id: str, test_code: str) -> Dict: ...
    def format_aggregated_feedback(self, mypy_errors: List, pytest_failures: List) -> str: ...
```

---

### ErrorDetectionAnalyzer (`code/run_experiment.py`)

**Dependencies:** numpy

```python
class ErrorDetectionAnalyzer:
    def __init__(self, threshold: float = 30.0): ...
    def calculate_detection_rate(self, results: List[Dict]) -> Dict: ...
    def compute_per_task_rates(self, results: List[Dict]) -> List[float]: ...
    def validate_gate(self, overall_rate: float) -> bool: ...
```

---

### ExperimentVisualizer (`code/run_experiment.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class ExperimentVisualizer:
    def __init__(self, output_dir: Path): ...
    def plot_gate_metrics(self, target: float, actual: float, passed: bool) -> None: ...
    def plot_error_detection_breakdown(self, results: List[Dict]) -> None: ...
    def plot_iteration_comparison(self, cascade_results: List, aggregation_results: List) -> None: ...
    def plot_execution_cost(self, cascade_results: List, aggregation_results: List) -> None: ...
    def plot_task_heatmap(self, results: List[Dict]) -> None: ...
```

---

### Pipeline Orchestrator (`code/run_experiment.py` - main)

**Dependencies:** All classes above

```python
class CascadeRoutingPipeline:
    def __init__(self, config: ExperimentConfig): ...
    def run(self) -> Dict: ...
    def stage_load_qualified_tasks(self) -> List[str]: ...
    def stage_cascade_evaluation(self, tasks: List[str]) -> List[Dict]: ...
    def stage_aggregation_baseline(self, tasks: List[str]) -> List[Dict]: ...
    def stage_analyze_detection_rate(self, cascade_results: List) -> Dict: ...
    def stage_generate_visualizations(self, cascade_results: List, aggregation_results: List) -> None: ...
    def stage_validate_gate(self, metrics: Dict) -> Dict: ...
    def save_results(self, results: Dict, path: Path) -> None: ...

def main():
    config = ExperimentConfig()
    pipeline = CascadeRoutingPipeline(config)
    results = pipeline.run()
    print(f"Gate status: {results['gate_satisfied']}")
```

---

### Configuration (`code/run_experiment.py` - ExperimentConfig dataclass)

**Dependencies:** dataclasses, pathlib

```python
@dataclass
class ExperimentConfig:
    model_name: str = "codellama/CodeLlama-7b-hf"
    k_samples: int = 20
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    variance_threshold: float = 1.0
    max_retries: int = 5
    target_detection_rate: float = 30.0
    seed: int = 42
    device: str = "auto"
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-E1 Actual Code)

| Module | Import Pattern | File Location |
|--------|----------------|---------------|
| HumanEvalLoader | Reimplemented (no import) | h-e1/code/run_experiment.py (lines 50-78) |
| CodeLlamaGenerator | Reimplemented (no import) | h-e1/code/run_experiment.py (lines 80-120) |
| MypyVerifier | Reimplemented (no import) | h-e1/code/run_experiment.py (lines 140-180) |
| PytestVerifier | Reimplemented (no import) | h-e1/code/run_experiment.py (lines 182-220) |

**Note:** H-e1 uses monolithic single-file structure. No modular imports needed. Follow same pattern for h-m1.

**H-e1 Data Reuse:**
- Qualified task list: Parse from `../h-e1/04_validation.md`
- Optional samples: Load from `../h-e1/outputs/samples.jsonl` if exists

---

## File Organization

```
h-m1/
├── code/
│   ├── run_experiment.py            # Monolithic main script (all classes)
│   ├── config.py                    # Configuration constants (optional)
│   ├── requirements.txt             # Dependencies
│   └── README.md                    # Setup instructions
├── outputs/
│   ├── cascade_results.jsonl        # Cascade routing results
│   ├── aggregation_results.jsonl    # Baseline results
│   ├── detection_metrics.json       # Error detection analysis
│   └── experiment.log               # Execution log
├── figures/
│   ├── gate_metrics.png             # Target vs actual detection rate
│   ├── error_breakdown.png          # Error type distribution
│   ├── iteration_comparison.png     # Cascade vs aggregation
│   ├── execution_cost.png           # Time savings analysis
│   └── task_heatmap.png             # Dual-sensitivity patterns
└── 04_validation.md                 # Gate validation report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup infrastructure | Project structure, requirements, GPU config | 5 | Module(1)+Dep(1)+Algo(1)+Integ(2) |
| M-2 | Qualified task loader | Parse h-e1 validation results (N=35) | 7 | Module(2)+Dep(2)+Algo(1)+Integ(2) |
| M-3 | Cascade feedback router | Mypy-first sequential routing implementation | 14 | Module(4)+Dep(3)+Algo(4)+Integ(3) |
| M-4 | Aggregation baseline | Both-source feedback routing | 10 | Module(3)+Dep(2)+Algo(2)+Integ(3) |
| M-5 | Mypy integration | Static analysis with error parsing | 8 | Module(2)+Dep(2)+Algo(2)+Integ(2) |
| M-6 | Pytest integration | Execution testing with timeout handling | 9 | Module(2)+Dep(2)+Algo(2)+Integ(3) |
| M-7 | Detection rate analysis | Calculate metrics, validate gate (≥30%) | 11 | Module(3)+Dep(2)+Algo(3)+Integ(3) |
| M-8 | Visualization | 5 figures (gate, breakdown, comparison, cost, heatmap) | 9 | Module(2)+Dep(3)+Algo(1)+Integ(3) |

**Complexity Distribution:**
- Low(4-8): M-1, M-2, M-5
- Medium(9-13): M-4, M-6, M-7, M-8
- High(14-17): M-3
- VeryHigh(18-20): None

**Total Complexity:** 73 points (MEDIUM budget for MECHANISM)

---

## Dependencies

### External Packages
- `evalplus` - HumanEval+ dataset
- `human-eval` - Fallback dataset
- `transformers` - CodeLlama-7B
- `torch` - GPU inference
- `mypy` - Static analysis
- `pytest` - Test execution
- `numpy` - Metrics computation
- `matplotlib` - Visualization
- `seaborn` - Enhanced plots

### System Requirements
- Python 3.10+
- CUDA 11.0+
- GPU: ≥16GB VRAM (same as h-e1)
- RAM: ≥32GB

---

## Checkpoint Strategy

**Intermediate Checkpoints:**
1. `outputs/qualified_tasks.json` - N=35 task list
2. `outputs/cascade_results.jsonl` - Cascade routing (progressive)
3. `outputs/aggregation_results.jsonl` - Aggregation baseline (progressive)
4. `outputs/detection_metrics.json` - Analysis results

**Resume Logic:** Check for partial results and skip completed tasks.

---

## Risk Mitigation

### R1: Detection rate <30% (MUST_WORK failure)
- **Action:** Pilot on N=5 tasks first
- **Early stop:** If <20%, document and PIVOT

### R2: GPU OOM during feedback loops
- **Action:** Batch size=1, clear cache between iterations
- **Implementation:** torch.cuda.empty_cache() per loop

### R3: Mypy/Pytest timeouts
- **Action:** Mark as timeout, continue evaluation
- **Tracking:** Log timeout rate separately

---

## Success Criteria

**MUST_WORK Gate:**
1. Mypy error detection rate ≥30%
2. All N=35 tasks evaluated
3. Cascade vs aggregation comparison complete

**Expected Output:**
- Detection rate: 30-40% (nominal)
- Runtime: 8-12 hours (feedback loops add overhead)
- 5 figures generated

---

## Implementation Notes

### Phase 4 Hints
1. **Reuse h-e1 patterns:** Same monolithic structure, similar class design
2. **Feedback formatting:** Keep mypy/pytest messages concise (token limits)
3. **Early validation:** Run pilot on 5 tasks before full evaluation
4. **Checkpoint frequently:** Save after each task completion

### Key Differences from H-E1
- **No classification:** Focus on feedback routing, not task qualification
- **Iterative loops:** Up to 5 retries per sample (vs h-e1's single-pass)
- **Dual routers:** Cascade + aggregation for comparison
- **Token tracking:** Monitor prompt growth across iterations

---

**Generated by Phase 3 Architecture Agent**
**Source:** 03_prd.md, 02c_experiment_brief.md, h-e1/03_architecture.md
**Next:** Phase 4 - Implementation (Coder Agent)
