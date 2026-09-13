# System Architecture: h-e1
# Hypothesis: Dual-Sensitive Task Classification System

**Date:** 2026-03-18
**Hypothesis Type:** EXISTENCE
**Author:** Claude (System Architect)
**Applied:** DL experiment minimal architecture pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing code to analyze. First hypothesis in pipeline.

---

## System Overview

EXISTENCE hypothesis for dual-sensitive task classification. No training - classification only.

**Pipeline Stages:**
1. Dataset loading (HumanEval)
2. Code generation (K=20 samples per task)
3. Static verification (mypy --strict)
4. Execution verification (pytest)
5. Dual-sensitivity classification

**Success Criterion:** N ≥ 20 dual-sensitive tasks with SD ≤ 1.0

---

## Module Structure

### DatasetLoader (`src/data/loader.py`)

**Dependencies:** evalplus, human_eval

```python
class HumanEvalLoader:
    def __init__(self, use_evalplus: bool = True): ...
    def load_problems(self) -> Dict[str, Dict]: ...
    def get_task(self, task_id: str) -> Dict: ...
```

---

### CodeGenerator (`src/models/generator.py`)

**Dependencies:** transformers, torch

```python
class CodeLlamaGenerator:
    def __init__(self, model_name: str = "codellama/CodeLlama-7b-hf", device: str = "auto"): ...
    def load_model(self) -> None: ...
    def generate_samples(self, prompt: str, k: int = 20) -> List[str]: ...
    def set_seed(self, seed: int) -> None: ...
```

---

### StaticVerifier (`src/verification/mypy_verifier.py`)

**Dependencies:** subprocess, tempfile

```python
class MypyVerifier:
    def __init__(self, timeout: int = 10): ...
    def verify(self, code: str) -> bool: ...
    def verify_batch(self, codes: List[str]) -> List[bool]: ...
```

---

### ExecutionVerifier (`src/verification/pytest_verifier.py`)

**Dependencies:** subprocess, tempfile

```python
class PytestVerifier:
    def __init__(self, timeout: int = 120): ...
    def verify(self, code: str, test_code: str) -> bool: ...
    def verify_batch(self, codes: List[str], tests: List[str]) -> List[bool]: ...
```

---

### DualSensitivityClassifier (`src/classifier/dual_sensitivity.py`)

**Dependencies:** numpy

```python
class DualSensitivityClassifier:
    def __init__(self, k_samples: int = 20, variance_threshold: float = 1.0): ...
    def classify_task(self, task_id: str, mypy_results: List[bool], pytest_results: List[bool]) -> Dict: ...
    def compute_variance(self, mypy_results: List[bool], pytest_results: List[bool]) -> float: ...
    def count_patterns(self, mypy_results: List[bool], pytest_results: List[bool]) -> Tuple[int, int]: ...
```

---

### GateValidator (`src/validation/gate.py`)

**Dependencies:** None

```python
class GateValidator:
    def __init__(self, threshold: int = 20): ...
    def validate(self, classification_results: List[Dict]) -> Dict: ...
    def apply_risk_mitigation(self, classification_results: List[Dict]) -> Dict: ...
```

---

### Visualizer (`src/visualization/plotter.py`)

**Dependencies:** matplotlib, numpy

```python
class ExperimentVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, target: int, actual: int, passed: bool) -> None: ...
    def plot_classification_distribution(self, results: List[Dict]) -> None: ...
    def plot_variance_histogram(self, results: List[Dict]) -> None: ...
    def plot_dual_sensitivity_patterns(self, results: List[Dict]) -> None: ...
```

---

### Pipeline Orchestrator (`src/main.py`)

**Dependencies:** All modules above

```python
class ClassificationPipeline:
    def __init__(self, config_path: str): ...
    def run(self) -> Dict: ...
    def stage_load_dataset(self) -> Dict[str, Dict]: ...
    def stage_generate_samples(self, problems: Dict) -> Dict[str, List[str]]: ...
    def stage_verify_mypy(self, samples: Dict) -> Dict[str, List[bool]]: ...
    def stage_verify_pytest(self, samples: Dict, problems: Dict) -> Dict[str, List[bool]]: ...
    def stage_classify(self, mypy_results: Dict, pytest_results: Dict) -> List[Dict]: ...
    def stage_validate_gate(self, classification_results: List[Dict]) -> Dict: ...
    def save_checkpoint(self, stage: str, data: Any) -> None: ...

def main():
    pipeline = ClassificationPipeline("config.yaml")
    results = pipeline.run()
    print(f"Gate status: {results['gate_satisfied']}")
```

---

### Configuration (`config.yaml`)

**Dependencies:** None

```python
# File structure (YAML)
model:
  name: "codellama/CodeLlama-7b-hf"
  precision: "fp16"
  device: "auto"

generation:
  k_samples: 20
  temperature: 0.8
  top_p: 0.95
  top_k: 40
  max_tokens: 256
  seed: 1

classification:
  variance_threshold: 1.0
  relaxed_threshold: 0.2

verification:
  mypy_timeout: 10
  pytest_timeout: 120

gate:
  min_qualifying_tasks: 20

paths:
  output_dir: "./results"
  figures_dir: "./figures"
  checkpoint_dir: "./checkpoints"
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data/
│   │   │   └── loader.py           # HumanEval dataset loading
│   │   ├── models/
│   │   │   └── generator.py        # CodeLlama-7B generation
│   │   ├── verification/
│   │   │   ├── mypy_verifier.py    # Static analysis
│   │   │   └── pytest_verifier.py  # Execution testing
│   │   ├── classifier/
│   │   │   └── dual_sensitivity.py # Task classification
│   │   ├── validation/
│   │   │   └── gate.py             # MUST_WORK gate logic
│   │   ├── visualization/
│   │   │   └── plotter.py          # Figure generation
│   │   └── main.py                 # Pipeline orchestration
│   ├── config.yaml                 # Configuration
│   ├── requirements.txt            # Dependencies
│   └── README.md                   # Setup instructions
├── results/
│   ├── samples.jsonl               # Generated code samples
│   ├── mypy_results.json           # Mypy verification
│   ├── pytest_results.json         # Pytest verification
│   └── classification.json         # Final classification
├── checkpoints/                    # Intermediate results
├── figures/                        # Visualization outputs
└── 04_validation.md                # Gate results

```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup infrastructure | Project structure, config, requirements | 6 | Module(2)+Dep(1)+Algo(1)+Integ(2) |
| A-2 | Dataset loading | HumanEval loader with evalplus fallback | 7 | Module(2)+Dep(2)+Algo(1)+Integ(2) |
| A-3 | Code generation | CodeLlama-7B K=20 sample generation | 12 | Module(3)+Dep(3)+Algo(3)+Integ(3) |
| A-4 | Static verification | Mypy --strict integration with timeout | 9 | Module(2)+Dep(2)+Algo(2)+Integ(3) |
| A-5 | Execution verification | Pytest integration with sandboxing | 10 | Module(3)+Dep(2)+Algo(2)+Integ(3) |
| A-6 | Classification logic | Dual-sensitivity classifier + variance | 8 | Module(2)+Dep(1)+Algo(3)+Integ(2) |
| A-7 | Gate validation | MUST_WORK gate with risk mitigation | 6 | Module(2)+Dep(1)+Algo(1)+Integ(2) |
| A-8 | Visualization | 4 figures + gate metrics plot | 7 | Module(2)+Dep(2)+Algo(1)+Integ(2) |

**Complexity Distribution:**
- Low(4-8): A-1, A-2, A-6, A-7, A-8
- Medium(9-13): A-4, A-5
- High(14-17): None
- VeryHigh(18-20): A-3

**Total Complexity:** 65 points (LIGHT budget - acceptable for EXISTENCE)

---

## Dependencies

### External Packages
- `evalplus` - HumanEval+ dataset
- `human-eval` - Fallback dataset
- `transformers` - CodeLlama-7B
- `torch` - GPU inference
- `mypy` - Static analysis
- `pytest` - Test execution
- `numpy` - Variance computation
- `matplotlib` - Visualization
- `pyyaml` - Configuration

### System Requirements
- Python 3.8+
- CUDA 11.0+
- GPU: ≥16GB VRAM
- RAM: ≥32GB

---

## Checkpoint Strategy

**Intermediate Checkpoints:**
1. `checkpoints/dataset.json` - Loaded tasks
2. `checkpoints/samples.jsonl` - Generated samples
3. `checkpoints/mypy_results.json` - Mypy verification
4. `checkpoints/pytest_results.json` - Pytest verification
5. `checkpoints/classification.json` - Final classification

**Resume Logic:** Pipeline checks for existing checkpoints before each stage.

---

## Risk Mitigation

### R1: N < 20 with SD ≤ 1.0
- **Action:** Relax variance threshold to 0.2
- **Implementation:** `GateValidator.apply_risk_mitigation()`

### R2: GPU OOM during generation
- **Action:** Reduce batch size to 1
- **Implementation:** Sequential generation in `CodeLlamaGenerator`

### R3: Mypy/Pytest timeout
- **Action:** Mark as "timeout" and continue
- **Implementation:** Timeout handling in verifiers

---

## Success Criteria

**MUST_WORK Gate:**
1. N ≥ 20 dual-sensitive tasks
2. Median SD ≤ 1.0
3. All 164 tasks processed

**Expected Output:**
- N = 30-50 qualifying tasks (nominal)
- Runtime: 6-11 hours on single GPU
- 4 figures generated

---

## Implementation Notes

### Phase 4 Hints
1. **Modular testing:** Test each module independently before integration
2. **Checkpoint early:** Save after each pipeline stage
3. **Timeout handling:** Critical for mypy/pytest reliability
4. **GPU selection:** Use `CUDA_VISIBLE_DEVICES` for single GPU

### Known Constraints
- EXISTENCE hypothesis: Minimal infrastructure only
- No baseline comparison (deferred to Phase 5)
- No training code (classification only)
- Single GPU sufficient

---

**Generated by Phase 3 Architecture Agent**
**Source:** 03_prd.md, 02c_experiment_brief.md
**Next:** Phase 4 - Implementation (Coder Agent)
