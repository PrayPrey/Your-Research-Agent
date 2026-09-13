# Logic Specifications: h-e1
# Hypothesis: Dual-Sensitive Task Classification System

**Date:** 2026-03-18
**Hypothesis Type:** EXISTENCE
**Author:** Claude (Logic Agent)
**Budget:** 7 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation - designing new APIs
**Analyzed Path:** N/A (no existing code)
**Relevant Symbols:** None - first hypothesis in pipeline

---

## A-1: Setup Infrastructure [Complexity: 6, Budget: 1]

**Applied:** Standard Python project structure

### API Signatures

```python
# File: src/__init__.py
"""Dual-sensitivity task classification system."""
__version__ = "0.1.0"

# File: config.yaml (YAML configuration)
# See architecture document for structure
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Project structure | Create directory structure, requirements.txt, config.yaml |

---

## A-2: Dataset Loading [Complexity: 7, Budget: 1]

**Applied:** HuggingFace datasets pattern

### API Signatures

```python
# File: src/data/loader.py
from typing import Dict, Optional

class HumanEvalLoader:
    """Load HumanEval tasks from evalplus or human-eval."""

    def __init__(self, use_evalplus: bool = True):
        """Initialize loader. use_evalplus: [True] → evalplus, [False] → human-eval"""
        self.use_evalplus = use_evalplus
        self.problems: Optional[Dict[str, Dict]] = None

    def load_problems(self) -> Dict[str, Dict]:
        """Load all 164 tasks. Returns: {task_id: {prompt, entry_point, test, ...}}"""
        ...

    def get_task(self, task_id: str) -> Dict:
        """Get single task by ID. Returns: {prompt, entry_point, test}"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Dataset loader | Implement evalplus loader with human-eval fallback |

---

## A-3: Code Generation [Complexity: 12, Budget: 2]

**Applied:** HuggingFace transformers generation pattern

### API Signatures

```python
# File: src/models/generator.py
from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class CodeLlamaGenerator:
    """Generate code samples using CodeLlama-7B."""

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        device: str = "auto",
        dtype: torch.dtype = torch.float16
    ):
        """Initialize generator. model_name: [str], device: [auto|cuda|cpu]"""
        self.model_name = model_name
        self.device = device
        self.dtype = dtype
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None

    def load_model(self) -> None:
        """Load model weights. First call may take 2-5 mins."""
        ...

    def generate_samples(
        self,
        prompt: str,
        k: int = 20,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 40,
        max_tokens: int = 256
    ) -> List[str]:
        """Generate K samples. prompt: [str] → [K × str]. Returns list of K completions."""
        ...

    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, L] | Tokenized prompt |
| outputs | [1, L+M] | Generated tokens |

### Pseudo-code

```
1. Tokenize prompt → input_ids [1, L]
2. For i in range(k):
   a. Set seed(seed + i)
   b. outputs = model.generate(input_ids, temperature=T, top_p=P, max_length=256)
   c. completion = tokenizer.decode(outputs[0])
   d. samples.append(completion)
3. Return samples
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model loading | HuggingFace model init with device_map="auto" |
| L-3-2 | Sample generation | K=20 generation loop with seed control |

---

## A-4: Static Verification [Complexity: 9, Budget: 1]

**Applied:** Subprocess timeout pattern

### API Signatures

```python
# File: src/verification/mypy_verifier.py
from typing import List, Tuple
import subprocess
import tempfile

class MypyVerifier:
    """Run mypy --strict on code samples."""

    def __init__(self, timeout: int = 10):
        """Initialize verifier. timeout: [int seconds]"""
        self.timeout = timeout

    def verify(self, code: str) -> Tuple[bool, str]:
        """Verify single sample. code: [str] → (pass: bool, output: str)"""
        ...

    def verify_batch(self, codes: List[str]) -> List[Tuple[bool, str]]:
        """Verify multiple samples. Returns: [(pass, output), ...]"""
        ...
```

### Pseudo-code

```
1. Write code to temp file
2. Run: subprocess.run(["mypy", "--strict", temp_path], timeout=10s)
3. Parse return code: 0 → True, non-zero → False
4. Cleanup temp file
5. Return (pass, output)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Mypy integration | Subprocess wrapper with timeout and error handling |

---

## A-5: Execution Verification [Complexity: 10, Budget: 1]

**Applied:** Subprocess timeout pattern

### API Signatures

```python
# File: src/verification/pytest_verifier.py
from typing import List, Tuple
import subprocess
import tempfile

class PytestVerifier:
    """Run pytest with HumanEval test cases."""

    def __init__(self, timeout: int = 120):
        """Initialize verifier. timeout: [int seconds]"""
        self.timeout = timeout

    def verify(self, code: str, test_code: str) -> Tuple[bool, str]:
        """Verify single sample. Returns: (pass: bool, output: str)"""
        ...

    def verify_batch(
        self,
        codes: List[str],
        tests: List[str]
    ) -> List[Tuple[bool, str]]:
        """Verify multiple samples. Returns: [(pass, output), ...]"""
        ...
```

### Pseudo-code

```
1. Combine code + test_code into single file
2. Run: subprocess.run(["pytest", "-x", temp_path], timeout=120s)
3. Parse return code: 0 → True, non-zero → False
4. Cleanup temp file
5. Return (pass, output)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Pytest integration | Subprocess wrapper with test sandboxing |

---

## A-6: Classification Logic [Complexity: 8, Budget: 1]

**Applied:** Standard numpy statistics pattern

### API Signatures

```python
# File: src/classifier/dual_sensitivity.py
from typing import List, Dict, Tuple
import numpy as np

class DualSensitivityClassifier:
    """Classify tasks as dual-sensitive based on verification results."""

    def __init__(self, k_samples: int = 20, variance_threshold: float = 1.0):
        """Initialize classifier. k_samples: [20], variance_threshold: [1.0]"""
        self.k = k_samples
        self.sd_threshold = variance_threshold

    def classify_task(
        self,
        task_id: str,
        mypy_results: List[bool],
        pytest_results: List[bool]
    ) -> Dict:
        """
        Classify single task.

        Args:
            task_id: Task identifier
            mypy_results: [K × bool] mypy pass/fail
            pytest_results: [K × bool] pytest pass/fail

        Returns:
            {
                "task_id": str,
                "dual_sensitive": bool,
                "mypy_only_fails": int,
                "pytest_only_fails": int,
                "variance": float,
                "qualifies": bool
            }
        """
        ...

    def compute_variance(
        self,
        mypy_results: List[bool],
        pytest_results: List[bool]
    ) -> float:
        """Compute within-task variance. Returns: SD as float"""
        ...

    def count_patterns(
        self,
        mypy_results: List[bool],
        pytest_results: List[bool]
    ) -> Tuple[int, int]:
        """
        Count failure patterns.

        Returns:
            (mypy_fail_pytest_pass_count, mypy_pass_pytest_fail_count)
        """
        ...
```

### Pseudo-code

```
1. Count patterns:
   - mypy_fail_pytest_pass = sum(not m and p for m, p in zip(mypy, pytest))
   - mypy_pass_pytest_fail = sum(m and not p for m, p in zip(mypy, pytest))

2. Check dual-sensitivity:
   - dual_sensitive = (mypy_fail_pytest_pass >= 1) and (mypy_pass_pytest_fail >= 1)

3. Compute variance:
   - numeric_results = [int(m) + int(p) for m, p in zip(mypy, pytest)]
   - variance = np.std(numeric_results)

4. Qualification:
   - qualifies = dual_sensitive and (variance <= threshold)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Classifier logic | Pattern counting + variance computation |

---

## A-7: Gate Validation [Complexity: 6, Budget: 0]

**Applied:** Standard threshold validation

### API Signatures

```python
# File: src/validation/gate.py
from typing import List, Dict

class GateValidator:
    """Validate MUST_WORK gate criteria."""

    def __init__(self, threshold: int = 20):
        """Initialize validator. threshold: [20] minimum qualifying tasks"""
        self.threshold = threshold

    def validate(self, classification_results: List[Dict]) -> Dict:
        """
        Validate gate criteria.

        Args:
            classification_results: List of classification dicts

        Returns:
            {
                "gate_satisfied": bool,
                "qualifying_count": int,
                "threshold_used": float,
                "action": str  # "PASS" | "RETRY_RELAXED" | "FAIL"
            }
        """
        ...

    def apply_risk_mitigation(
        self,
        classification_results: List[Dict]
    ) -> Dict:
        """Apply R1 mitigation: relax SD threshold to 0.2"""
        ...
```

### Pseudo-code

```
1. Count qualifying tasks: N = sum(r["qualifies"] for r in results)
2. If N >= 20: return PASS
3. Else: apply_risk_mitigation()
   a. Recount with SD <= 0.2
   b. If N_relaxed >= 20: return PASS
   c. Else: return FAIL
```

### Subtasks [0/0 used]

No subtasks allocated (complexity absorbed into other tasks).

---

## A-8: Visualization [Complexity: 7, Budget: 0]

**Applied:** Matplotlib standard plotting

### API Signatures

```python
# File: src/visualization/plotter.py
from typing import List, Dict
import matplotlib.pyplot as plt

class ExperimentVisualizer:
    """Generate experiment figures."""

    def __init__(self, output_dir: str):
        """Initialize visualizer. output_dir: [str path]"""
        self.output_dir = output_dir

    def plot_gate_metrics(
        self,
        target: int,
        actual: int,
        passed: bool
    ) -> None:
        """Fig 1: Bar chart comparing target vs actual. Save to output_dir/fig1_gate_metrics.png"""
        ...

    def plot_classification_distribution(
        self,
        results: List[Dict]
    ) -> None:
        """Fig 2: Bar chart of dual-sensitive vs not. Save to fig2_classification.png"""
        ...

    def plot_variance_histogram(
        self,
        results: List[Dict]
    ) -> None:
        """Fig 3: Histogram of SD values. Save to fig3_variance.png"""
        ...

    def plot_dual_sensitivity_patterns(
        self,
        results: List[Dict]
    ) -> None:
        """Fig 4: Scatter plot of failure patterns. Save to fig4_patterns.png"""
        ...
```

### Subtasks [0/0 used]

No subtasks allocated (complexity absorbed into other tasks).

---

## Pipeline Orchestrator

**Applied:** Standard ETL pipeline pattern

### API Signatures

```python
# File: src/main.py
from typing import Dict, List, Any
import yaml

class ClassificationPipeline:
    """Orchestrate end-to-end classification pipeline."""

    def __init__(self, config_path: str):
        """Initialize pipeline. config_path: [str] path to config.yaml"""
        self.config = self._load_config(config_path)
        self.loader = None
        self.generator = None
        self.mypy_verifier = None
        self.pytest_verifier = None
        self.classifier = None
        self.gate_validator = None
        self.visualizer = None

    def run(self) -> Dict:
        """
        Run full pipeline.

        Returns:
            {
                "gate_satisfied": bool,
                "qualifying_count": int,
                "total_tasks": int,
                "figures_generated": List[str]
            }
        """
        ...

    def stage_load_dataset(self) -> Dict[str, Dict]:
        """Stage 1: Load 164 tasks. Returns: {task_id: task_dict}"""
        ...

    def stage_generate_samples(
        self,
        problems: Dict
    ) -> Dict[str, List[str]]:
        """Stage 2: Generate K=20 samples per task. Returns: {task_id: [K × str]}"""
        ...

    def stage_verify_mypy(
        self,
        samples: Dict
    ) -> Dict[str, List[bool]]:
        """Stage 3: Mypy verification. Returns: {task_id: [K × bool]}"""
        ...

    def stage_verify_pytest(
        self,
        samples: Dict,
        problems: Dict
    ) -> Dict[str, List[bool]]:
        """Stage 4: Pytest verification. Returns: {task_id: [K × bool]}"""
        ...

    def stage_classify(
        self,
        mypy_results: Dict,
        pytest_results: Dict
    ) -> List[Dict]:
        """Stage 5: Classification. Returns: [classification_dict, ...]"""
        ...

    def stage_validate_gate(
        self,
        classification_results: List[Dict]
    ) -> Dict:
        """Stage 6: Gate validation. Returns: gate_result_dict"""
        ...

    def save_checkpoint(self, stage: str, data: Any) -> None:
        """Save intermediate results."""
        ...

def main():
    """Entry point."""
    pipeline = ClassificationPipeline("config.yaml")
    results = pipeline.run()
    print(f"Gate status: {'PASSED' if results['gate_satisfied'] else 'FAILED'}")
    print(f"Qualifying tasks: {results['qualifying_count']}/164")
```

### Pseudo-code

```
1. Load config.yaml
2. Initialize all modules
3. For each stage:
   a. Check if checkpoint exists → resume
   b. Execute stage
   c. Save checkpoint
4. Generate visualizations
5. Return gate results
```

---

## Task Allocation Summary

| Task | Budget | Used | Remaining |
|------|--------|------|-----------|
| A-1 | 1 | 1 | 0 |
| A-2 | 1 | 1 | 0 |
| A-3 | 2 | 2 | 0 |
| A-4 | 1 | 1 | 0 |
| A-5 | 1 | 1 | 0 |
| A-6 | 1 | 1 | 0 |
| A-7 | 0 | 0 | 0 |
| A-8 | 0 | 0 | 0 |
| **Total** | **7** | **7** | **0** |

---

## Implementation Notes

### Type Hints
All APIs use Python 3.8+ type hints (`typing` module).

### Error Handling
- **Subprocess timeouts:** Catch `subprocess.TimeoutExpired`, log and continue
- **Model loading:** Retry up to 3 times with 15s delay
- **File I/O:** Use `with` statements for automatic cleanup

### Configuration
All hyperparameters externalized to `config.yaml`:
- Model name, precision, device
- Generation parameters (K, temperature, top_p, top_k)
- Verification timeouts
- Gate thresholds

### Checkpointing
Save after each stage to `checkpoints/`:
- `dataset.json` - Loaded tasks
- `samples.jsonl` - Generated samples
- `mypy_results.json` - Mypy results
- `pytest_results.json` - Pytest results
- `classification.json` - Final classification

---

## Dependencies

### External Packages
```txt
evalplus>=0.2.0
human-eval>=1.0.0
transformers>=4.30.0
torch>=2.0.0
mypy>=1.0.0
pytest>=7.0.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
```

### System Requirements
- Python 3.8+
- CUDA 11.0+ (for GPU)
- GPU: ≥16GB VRAM
- RAM: ≥32GB

---

**Generated by Phase 3 Logic Agent**
**Source:** 03_architecture.md, 03_prd.md
**Next:** Phase 4 - Implementation (Coder Agent)
