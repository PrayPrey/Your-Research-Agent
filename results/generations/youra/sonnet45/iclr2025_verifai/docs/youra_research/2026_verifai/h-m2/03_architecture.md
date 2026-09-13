# System Architecture: h-m2
# Hypothesis: Sequential vs Aggregation Feedback Presentation

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (System Architect)
**Applied:** Iterative feedback loop pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-m1 implementation (monolithic single-file structure)
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-m1/code/
**Findings:** H-m1 uses monolithic run_experiment.py with integrated classes. Will follow same pattern for consistency. No modular src/ structure - all components in single script.

---

## System Overview

MECHANISM hypothesis validating feedback presentation impact. Extends h-m1 by comparing single-source sequential vs simultaneous aggregation feedback routing.

**Pipeline Stages:**
1. Task loading (reuse N=20 from h-e1 qualified tasks)
2. Code generation (CodeLlama-7B, iterative refinement)
3. **Sequential mode** (mypy OR pytest per iteration)
4. **Aggregation mode** (mypy + pytest concatenated)
5. Iterations-to-solution comparison

**Success Criterion:** Sequential mode shows μ_seq < μ_agg (directional)

---

## Module Structure

### DatasetLoader (`code/run_experiment.py` - HumanEvalLoader class)

**Dependencies:** evalplus, human_eval

```python
class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True): ...
    def load_problems(self) -> Dict[str, Dict]: ...
    def load_qualified_tasks(self, h_e1_validation_path: str) -> List[str]: ...
    def get_task_tests(self, task_id: str) -> str: ...
```

---

### CodeGenerator (`code/run_experiment.py` - CodeLlamaGenerator class)

**Dependencies:** transformers, torch

```python
class CodeLlamaGenerator:
    def __init__(self, config: ExperimentConfig): ...
    def load_model(self) -> None: ...
    def generate_initial(self, prompt: str) -> str: ...
    def refine_with_feedback(self, code: str, feedback: str, prompt: str) -> str: ...
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
    def format_feedback(self, errors: List[Dict]) -> str: ...
```

---

### PytestVerifier (`code/run_experiment.py` - PytestVerifier class)

**Dependencies:** subprocess, tempfile, evalplus

```python
class PytestVerifier:
    def __init__(self, timeout: int = 120): ...
    def verify(self, code: str, test_code: str, entry_point: str) -> Dict[str, any]: ...
    def parse_failures(self, output: str) -> List[str]: ...
    def format_feedback(self, failures: List[str]) -> str: ...
```

---

### SequentialFeedbackRouter (`code/run_experiment.py` - core mechanism)

**Dependencies:** MypyVerifier, PytestVerifier, CodeLlamaGenerator

```python
class SequentialFeedbackRouter:
    def __init__(self, generator: CodeLlamaGenerator, mypy: MypyVerifier, pytest: PytestVerifier, max_iter: int = 10): ...
    def generate_with_feedback(self, task_prompt: str, task_id: str, test_code: str, entry_point: str) -> Dict: ...
    def _should_present_mypy(self, mypy_result: Dict) -> bool: ...
    def _should_present_pytest(self, mypy_result: Dict, pytest_result: Dict) -> bool: ...
    def log_iteration(self, iteration: int, source: str, feedback: str) -> None: ...
```

---

### AggregationFeedbackRouter (`code/run_experiment.py` - baseline)

**Dependencies:** MypyVerifier, PytestVerifier, CodeLlamaGenerator

```python
class AggregationFeedbackRouter:
    def __init__(self, generator: CodeLlamaGenerator, mypy: MypyVerifier, pytest: PytestVerifier, max_iter: int = 10): ...
    def generate_with_feedback(self, task_prompt: str, task_id: str, test_code: str, entry_point: str) -> Dict: ...
    def _concatenate_feedback(self, mypy_result: Dict, pytest_result: Dict) -> str: ...
    def log_iteration(self, iteration: int, feedback: str) -> None: ...
```

---

### MechanismVerifier (`code/run_experiment.py`)

**Dependencies:** None

```python
class MechanismVerifier:
    def __init__(self): ...
    def verify_sequential_mode(self, experiment_log: List[Dict]) -> Tuple[bool, str]: ...
    def verify_aggregation_mode(self, experiment_log: List[Dict]) -> Tuple[bool, str]: ...
    def count_feedback_sources(self, feedback_text: str) -> int: ...
    def verify_task_parity(self, seq_tasks: List[str], agg_tasks: List[str]) -> bool: ...
```

---

### MetricsAnalyzer (`code/run_experiment.py`)

**Dependencies:** numpy

```python
class MetricsAnalyzer:
    def __init__(self): ...
    def compute_iterations_to_solution(self, results: List[Dict]) -> Dict: ...
    def compute_success_rate(self, results: List[Dict]) -> float: ...
    def compute_token_efficiency(self, results: List[Dict]) -> Dict: ...
    def validate_gate(self, seq_mean: float, agg_mean: float) -> Dict: ...
```

---

### ExperimentVisualizer (`code/run_experiment.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class ExperimentVisualizer:
    def __init__(self, output_dir: Path): ...
    def plot_gate_metrics(self, seq_mean: float, agg_mean: float, passed: bool) -> None: ...
    def plot_iteration_distribution(self, seq_results: List, agg_results: List) -> None: ...
    def plot_convergence_curves(self, seq_results: List, agg_results: List) -> None: ...
    def plot_per_task_comparison(self, seq_results: List, agg_results: List) -> None: ...
    def plot_token_efficiency(self, seq_metrics: Dict, agg_metrics: Dict) -> None: ...
```

---

### Pipeline Orchestrator (`code/run_experiment.py` - main)

**Dependencies:** All classes above

```python
class FeedbackPresentationPipeline:
    def __init__(self, config: ExperimentConfig): ...
    def run(self) -> Dict: ...
    def stage_load_qualified_tasks(self) -> List[str]: ...
    def stage_sequential_evaluation(self, tasks: List[str]) -> List[Dict]: ...
    def stage_aggregation_evaluation(self, tasks: List[str]) -> List[Dict]: ...
    def stage_verify_mechanism(self, seq_results: List, agg_results: List) -> Dict: ...
    def stage_compute_metrics(self, seq_results: List, agg_results: List) -> Dict: ...
    def stage_validate_gate(self, metrics: Dict) -> Dict: ...
    def stage_generate_visualizations(self, seq_results: List, agg_results: List, metrics: Dict) -> None: ...
    def save_results(self, results: Dict, path: Path) -> None: ...

def main():
    config = ExperimentConfig()
    pipeline = FeedbackPresentationPipeline(config)
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
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40
    max_length: int = 256
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    max_iterations: int = 10
    n_tasks: int = 20
    seed: int = 42
    device: str = "auto"
    h_e1_validation_path: str = "../h-e1/04_validation.md"
    output_dir: Path = Path("./outputs")
    figures_dir: Path = Path("./figures")
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-M1 Actual Code)

| Module | Import Pattern | File Location |
|--------|----------------|---------------|
| HumanEvalLoader | Reimplemented (no import) | h-m1/code/run_experiment.py (lines 50-78) |
| CodeLlamaGenerator | Reimplemented (no import) | h-m1/code/run_experiment.py (lines 80-124) |
| MypyVerifier | Reimplemented (no import) | h-m1/code/run_experiment.py (lines 126-160) |
| PytestVerifier | Reimplemented (no import) | h-m1/code/run_experiment.py (lines 161-200) |

**Note:** H-m1 uses monolithic single-file structure. No modular imports needed. Follow same pattern for h-m2.

**H-E1 Data Reuse:**
- Qualified task list: Parse from `../h-e1/04_validation.md` (first 20 of 35 qualified tasks)
- No sample reuse needed (fresh generation per condition)

---

## File Organization

```
h-m2/
├── code/
│   ├── run_experiment.py            # Monolithic main script (all classes)
│   ├── requirements.txt             # Dependencies
│   └── README.md                    # Setup instructions
├── outputs/
│   ├── sequential_results.jsonl     # Sequential mode results
│   ├── aggregation_results.jsonl    # Aggregation mode results
│   ├── metrics.json                 # Comparative metrics
│   ├── mechanism_verification.json  # Verification results
│   └── experiment.log               # Execution log
├── figures/
│   ├── gate_metrics.png             # Sequential vs aggregation comparison
│   ├── iteration_distribution.png   # Box plots
│   ├── convergence_curves.png       # Cumulative success rates
│   ├── per_task_comparison.png      # Scatter plot
│   └── token_efficiency.png         # Token usage comparison
└── 04_validation.md                 # Gate validation report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Setup infrastructure | Project structure, requirements, GPU config | 5 | Module(1)+Dep(1)+Algo(1)+Integ(2) |
| M2-2 | Qualified task loader | Parse h-e1 validation results (first N=20) | 6 | Module(2)+Dep(1)+Algo(1)+Integ(2) |
| M2-3 | Sequential feedback router | Single-source per iteration routing | 15 | Module(4)+Dep(3)+Algo(5)+Integ(3) |
| M2-4 | Aggregation feedback router | Concatenated multi-source routing | 12 | Module(3)+Dep(2)+Algo(4)+Integ(3) |
| M2-5 | LLM refinement loop | Iterative generation with feedback | 13 | Module(3)+Dep(3)+Algo(4)+Integ(3) |
| M2-6 | Mechanism verification | Verify routing logic operates correctly | 9 | Module(2)+Dep(2)+Algo(3)+Integ(2) |
| M2-7 | Metrics computation | Iterations-to-solution, success rate, tokens | 10 | Module(2)+Dep(2)+Algo(3)+Integ(3) |
| M2-8 | Gate validation | Compare μ_seq < μ_agg, validate SHOULD_WORK | 8 | Module(2)+Dep(1)+Algo(3)+Integ(2) |
| M2-9 | Visualization | 5 figures (gate, distribution, convergence, scatter, tokens) | 10 | Module(2)+Dep(3)+Algo(2)+Integ(3) |

**Complexity Distribution:**
- Low(4-8): M2-1, M2-2, M2-8
- Medium(9-13): M2-4, M2-5, M2-6, M2-7, M2-9
- High(14-17): M2-3
- VeryHigh(18-20): None

**Total Complexity:** 88 points (MEDIUM-HIGH budget for MECHANISM)

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
- GPU: ≥16GB VRAM (same as h-m1)
- RAM: ≥32GB

---

## Checkpoint Strategy

**Intermediate Checkpoints:**
1. `outputs/qualified_tasks.json` - N=20 task list
2. `outputs/sequential_results.jsonl` - Sequential mode (progressive)
3. `outputs/aggregation_results.jsonl` - Aggregation mode (progressive)
4. `outputs/metrics.json` - Analysis results

**Resume Logic:** Check for partial results and skip completed tasks.

---

## Risk Mitigation

### R1: Sequential mode worse than aggregation (SHOULD_WORK acceptable failure)
- **Action:** Document findings, EXPLORE alternative explanation
- **Acceptable:** SHOULD_WORK gate allows failure → continue pipeline

### R2: GPU OOM during iterative loops
- **Action:** Batch size=1, clear cache between iterations
- **Implementation:** torch.cuda.empty_cache() per loop

### R3: Mypy/Pytest timeouts
- **Action:** Mark as timeout, continue with next iteration
- **Tracking:** Log timeout rate separately

### R4: Non-deterministic results
- **Action:** Fixed seed (42), temperature control (0.8)
- **Validation:** Re-run subset to check variance (<5%)

---

## Success Criteria

**SHOULD_WORK Gate:**
1. Sequential mode shows μ_seq < μ_agg (directional)
2. All N=20 tasks evaluated in both conditions
3. Mechanism verification passes (routing logic operates correctly)

**Expected Output:**
- Mean iterations (sequential): 4-6 (exploratory estimate)
- Mean iterations (aggregation): 5-8 (exploratory estimate)
- Runtime: 4-8 hours (iterative refinement adds overhead)
- 5 figures generated

**If FAIL:** Acceptable under SHOULD_WORK gate → EXPLORE alternative explanation (LLMs may internally normalize feedback regardless of presentation)

---

## Implementation Notes

### Phase 4 Hints
1. **Reuse h-m1 patterns:** Same monolithic structure, similar class design
2. **Feedback formatting:** Keep mypy/pytest messages concise for LLM token limits
3. **Logging granularity:** Capture full conversation history per (task, condition) pair
4. **Early validation:** Run pilot on 3 tasks before full evaluation
5. **Checkpoint frequently:** Save after each task completion

### Key Differences from H-M1
- **Iterative refinement:** Up to 10 iterations per task (vs h-m1's single-pass)
- **Dual routers:** Sequential + aggregation for controlled comparison
- **Conversation tracking:** Log full feedback history per iteration
- **Token tracking:** Monitor prompt growth across refinement cycles

### Mechanism Verification Protocol
- Check 1: Sequential mode never presents multiple sources simultaneously
- Check 2: Aggregation mode always presents all available sources when errors exist
- Check 3: Same task set tested in both conditions
- Implementation: Run `MechanismVerifier.verify_*` after each condition completes

---

**Generated by Phase 3 Architecture Agent**
**Source:** 03_prd.md, 02c_experiment_brief.md, h-m1/03_architecture.md, h-m1/code/run_experiment.py
**Next:** Phase 4 - Implementation (Coder Agent)
