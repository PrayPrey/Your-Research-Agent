# System Architecture: h-m3
# Hypothesis: Conditional Execution Gating Token Efficiency

**Date:** 2026-03-18
**Hypothesis Type:** MECHANISM
**Author:** Claude (System Architect)
**Applied:** DL experiment minimal architecture pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-m1 infrastructure (monolithic single-file structure)
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_verifai/docs/youra_research/20260318_verifai/h-m1/code/
**Findings:** H-m1 uses monolithic run_experiment.py with integrated classes (HumanEvalLoader, CodeLlamaGenerator, MypyVerifier, PytestVerifier). Will reuse these components and add new feedback routers (CascadeRouter, AggregationRouter) following same pattern. No modular src/ structure.

---

## System Overview

MECHANISM hypothesis validating token efficiency of conditional execution gating. Extends h-m1 by implementing two feedback routing strategies and comparing tokens-per-successful-task.

**Pipeline Stages:**
1. Task loading (N=20 dual-sensitive from h-e1)
2. CASCADE routing (mypy → if clean → pytest)
3. AGGREGATION routing (mypy + pytest always)
4. Token efficiency comparison
5. Gate validation (≤15% overhead)

**Success Criterion:** `cascade_tokens_per_task / aggregation_tokens_per_task ≤ 1.15`

---

## Module Structure

### DatasetLoader (`code/run_experiment.py` - HumanEvalLoader class)

**Dependencies:** evalplus, human_eval

```python
class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True): ...
    def load_problems(self) -> Dict[str, Dict]: ...
    def load_qualified_task_ids(self, h_e1_validation_path: str) -> List[str]: ...
```

---

### CodeGenerator (`code/run_experiment.py` - CodeLlamaGenerator class)

**Dependencies:** transformers, torch

```python
class CodeLlamaGenerator:
    def __init__(self, config: ExperimentConfig): ...
    def load_model(self) -> None: ...
    def generate(self, prompt: str) -> str: ...
    def count_tokens(self, text: str) -> int: ...
```

---

### MypyVerifier (`code/run_experiment.py` - reused from h-m1)

**Dependencies:** subprocess, tempfile

```python
class MypyVerifier:
    def __init__(self, timeout: int = 10): ...
    def verify(self, code: str) -> Dict[str, any]: ...
    def format_feedback(self, stderr: str) -> str: ...
```

---

### PytestVerifier (`code/run_experiment.py` - reused from h-m1)

**Dependencies:** subprocess, tempfile

```python
class PytestVerifier:
    def __init__(self, timeout: int = 120): ...
    def verify(self, code: str, test_code: str, entry_point: str) -> Dict[str, any]: ...
    def format_feedback(self, output: str) -> str: ...
```

---

### CascadeRouter (`code/run_experiment.py` - NEW core mechanism)

**Dependencies:** CodeLlamaGenerator, MypyVerifier, PytestVerifier

```python
class CascadeRouter:
    def __init__(self, generator: CodeLlamaGenerator, max_iterations: int = 10): ...
    def solve_task(self, task_prompt: str, test_code: str, entry_point: str) -> Dict: ...
    def _iteration_step(self, prompt: str, test_code: str, entry_point: str) -> Tuple[str, str, int, bool]: ...
```

**Returns:**
```python
{
    "code": str,
    "iterations": int,
    "total_tokens": int,
    "mypy_tokens": int,
    "pytest_tokens": int,
    "gating_skipped_count": int,
    "success": bool
}
```

---

### AggregationRouter (`code/run_experiment.py` - NEW baseline)

**Dependencies:** CodeLlamaGenerator, MypyVerifier, PytestVerifier

```python
class AggregationRouter:
    def __init__(self, generator: CodeLlamaGenerator, max_iterations: int = 10): ...
    def solve_task(self, task_prompt: str, test_code: str, entry_point: str) -> Dict: ...
    def _iteration_step(self, prompt: str, test_code: str, entry_point: str) -> Tuple[str, str, int, bool]: ...
```

**Returns:**
```python
{
    "code": str,
    "iterations": int,
    "total_tokens": int,
    "mypy_tokens": int,
    "pytest_tokens": int,
    "success": bool
}
```

---

### TokenEfficiencyAnalyzer (`code/run_experiment.py` - NEW)

**Dependencies:** numpy

```python
class TokenEfficiencyAnalyzer:
    def __init__(self, threshold: float = 1.15): ...
    def compute_tokens_per_task(self, results: List[Dict]) -> Dict: ...
    def compute_efficiency_ratio(self, cascade_metrics: Dict, aggregation_metrics: Dict) -> float: ...
    def compute_secondary_metrics(self, cascade_results: List, aggregation_results: List) -> Dict: ...
    def validate_gate(self, ratio: float) -> bool: ...
```

---

### ExperimentVisualizer (`code/run_experiment.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class ExperimentVisualizer:
    def __init__(self, output_dir: Path): ...
    def plot_gate_metrics(self, target: float, actual: float, passed: bool) -> None: ...
    def plot_token_efficiency_comparison(self, cascade_metrics: Dict, aggregation_metrics: Dict) -> None: ...
    def plot_token_breakdown(self, cascade_results: List, aggregation_results: List) -> None: ...
    def plot_gating_efficiency(self, cascade_results: List) -> None: ...
    def plot_iterations_comparison(self, cascade_results: List, aggregation_results: List) -> None: ...
```

---

### Pipeline Orchestrator (`code/run_experiment.py` - main)

**Dependencies:** All classes above

```python
class TokenEfficiencyPipeline:
    def __init__(self, config: ExperimentConfig): ...
    def run(self) -> Dict: ...
    def stage_load_qualified_tasks(self) -> Dict[str, Dict]: ...
    def stage_cascade_evaluation(self, tasks: Dict) -> List[Dict]: ...
    def stage_aggregation_evaluation(self, tasks: Dict) -> List[Dict]: ...
    def stage_analyze_efficiency(self, cascade_results: List, aggregation_results: List) -> Dict: ...
    def stage_generate_visualizations(self, cascade_results: List, aggregation_results: List, metrics: Dict) -> None: ...
    def stage_validate_gate(self, metrics: Dict) -> Dict: ...
    def save_results(self, results: Dict, path: Path) -> None: ...

def main():
    config = ExperimentConfig()
    pipeline = TokenEfficiencyPipeline(config)
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
    temperature: float = 0.7
    top_p: float = 0.95
    max_new_tokens: int = 512
    max_iterations: int = 10
    token_limit_per_source: int = 1000
    mypy_timeout: int = 10
    pytest_timeout: int = 120
    efficiency_threshold: float = 1.15
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
| MypyVerifier | Reimplemented (no import) | h-m1/code/run_experiment.py (lines 126-159) |
| PytestVerifier | Reimplemented (no import) | h-m1/code/run_experiment.py (lines 161-199) |

**Note:** H-m1 uses monolithic single-file structure. No modular imports. Will copy-paste and modify base classes for h-m3's feedback routing use case.

**H-E1 Data Reuse:**
- Qualified task list (N=20): Parse dual-sensitive task IDs from `../h-e1/04_validation.md`
- Task metadata: Load from evalplus package

---

## File Organization

```
h-m3/
├── code/
│   ├── run_experiment.py            # Monolithic main script (all classes)
│   ├── requirements.txt             # Dependencies
│   └── README.md                    # Setup instructions
├── outputs/
│   ├── cascade_results.jsonl        # CASCADE routing results
│   ├── aggregation_results.jsonl    # AGGREGATION baseline results
│   ├── efficiency_metrics.json      # Token efficiency analysis
│   └── experiment.log               # Execution log
├── figures/
│   ├── gate_metrics.png             # Gate validation (≤1.15 threshold)
│   ├── token_efficiency.png         # CASCADE vs AGGREGATION comparison
│   ├── token_breakdown.png          # Mypy vs pytest token contribution
│   ├── gating_efficiency.png        # % execution skipped in CASCADE
│   └── iterations_comparison.png    # Convergence speed comparison
└── 04_validation.md                 # Gate validation report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| T-1 | Setup infrastructure | Project structure, requirements, GPU config | 5 | Module(1)+Dep(1)+Algo(1)+Integ(2) |
| T-2 | Qualified task loader | Parse h-e1 validation (N=20), load from evalplus | 7 | Module(2)+Dep(2)+Algo(1)+Integ(2) |
| T-3 | Reuse verification components | Copy MypyVerifier, PytestVerifier from h-m1 with feedback formatting | 8 | Module(2)+Dep(2)+Algo(2)+Integ(2) |
| T-4 | CASCADE router implementation | Conditional gating logic (mypy → if clean → pytest) | 15 | Module(4)+Dep(3)+Algo(4)+Integ(4) |
| T-5 | AGGREGATION router implementation | Simultaneous both-source feedback baseline | 12 | Module(3)+Dep(3)+Algo(3)+Integ(3) |
| T-6 | Token counting integration | Tokenizer-based token counting in routers | 7 | Module(2)+Dep(2)+Algo(1)+Integ(2) |
| T-7 | Efficiency metric computation | Tokens-per-task calculation, ratio validation | 10 | Module(3)+Dep(2)+Algo(2)+Integ(3) |
| T-8 | Secondary metrics analysis | Gating efficiency, token breakdown, success rates | 9 | Module(2)+Dep(2)+Algo(2)+Integ(3) |
| T-9 | Visualization generation | 5 figures (gate, comparison, breakdown, gating, iterations) | 10 | Module(2)+Dep(3)+Algo(2)+Integ(3) |
| T-10 | Pipeline orchestration | Integrate all stages, checkpointing, gate validation | 11 | Module(3)+Dep(2)+Algo(2)+Integ(4) |

**Complexity Distribution:**
- Low(4-8): T-1, T-2, T-3, T-6
- Medium(9-13): T-5, T-7, T-8, T-9, T-10
- High(14-17): T-4
- VeryHigh(18-20): None

**Total Complexity:** 94 points (MEDIUM-HIGH budget for MECHANISM with dual routing)

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
1. `outputs/qualified_tasks.json` - N=20 task list from h-e1
2. `outputs/cascade_results.jsonl` - CASCADE routing (progressive save)
3. `outputs/aggregation_results.jsonl` - AGGREGATION baseline (progressive save)
4. `outputs/efficiency_metrics.json` - Analysis results

**Resume Logic:** Check for partial results files and skip completed tasks.

---

## Risk Mitigation

### R1: Efficiency ratio >1.15 (SHOULD_WORK failure)
- **Action:** Document limitation in validation report
- **Follow-up:** Write Serena memory, continue to h-c1

### R2: GPU OOM during iterative feedback loops
- **Action:** Batch size=1, clear cache per iteration
- **Implementation:** torch.cuda.empty_cache() after each generation

### R3: Low success rate (<50% tasks solved)
- **Action:** Increase max_iterations from 10 to 15
- **Early detection:** Pilot on 5 tasks first

### R4: Token counting inconsistency
- **Action:** Unit test tokenizer encode/decode
- **Validation:** Manual spot-check on sample feedback

---

## Success Criteria

**SHOULD_WORK Gate:**
1. `cascade_tokens_per_task / aggregation_tokens_per_task ≤ 1.15`
2. Both routers successfully evaluate all N=20 tasks
3. ≥10 tasks solved per condition (50% minimum success rate)

**Expected Output:**
- Efficiency ratio: 1.05-1.15 (nominal range)
- Gating efficiency: ≥60% iterations skipped in CASCADE
- Runtime: ~2 hours total (N=20 × 2 conditions × ~3 min/task)
- 5 figures generated

---

## Implementation Notes

### Phase 4 Hints
1. **Reuse h-m1 code:** Copy MypyVerifier, PytestVerifier, HumanEvalLoader classes
2. **NEW components:** CascadeRouter, AggregationRouter, TokenEfficiencyAnalyzer
3. **Feedback formatting:** Keep mypy/pytest output concise (token limit 1000/source)
4. **Early validation:** Run pilot on 3 tasks before full evaluation
5. **Checkpoint frequently:** Save results after each task to enable resume

### Key Implementation Details

**CascadeRouter Logic:**
```python
# Iteration step
mypy_result = mypy_verifier.verify(code)
mypy_feedback = format_mypy_feedback(mypy_result)
tokens += count_tokens(mypy_feedback)

if mypy_result["success"]:  # Gate OPEN
    pytest_result = pytest_verifier.verify(code, test_code, entry_point)
    pytest_feedback = format_pytest_feedback(pytest_result)
    tokens += count_tokens(pytest_feedback)
    feedback = pytest_feedback
else:  # Gate CLOSED
    gating_skipped += 1
    feedback = mypy_feedback
```

**AggregationRouter Logic:**
```python
# Iteration step - always run both
mypy_result = mypy_verifier.verify(code)
pytest_result = pytest_verifier.verify(code, test_code, entry_point)

mypy_feedback = format_mypy_feedback(mypy_result)
pytest_feedback = format_pytest_feedback(pytest_result)

combined_feedback = mypy_feedback + "\n\n" + pytest_feedback
tokens += count_tokens(combined_feedback)
```

**Token Counting:**
```python
def count_tokens(self, text: str) -> int:
    return len(self.tokenizer.encode(text))
```

### Key Differences from H-M1
- **Iterative feedback loops:** Up to 10 iterations per task (vs h-m1's single-pass K=20 samples)
- **Token tracking:** Primary metric (vs h-m1's error detection rate)
- **Dual routers:** CASCADE vs AGGREGATION comparison
- **Qualified tasks only:** N=20 dual-sensitive (vs h-m1's full 164 classification)

---

**Generated by Phase 3 Architecture Agent**
**Source:** 03_prd.md, 02c_experiment_brief.md, h-m1/03_architecture.md, h-m1/code/run_experiment.py
**Next:** Phase 4 - Implementation (Coder Agent)
