# Logic Design: H-E1 Proxy Metric Validation System

**Date:** 2026-07-09  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Author:** Logic Agent  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing codebase  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - designing new APIs from scratch

---

## Knowledge Base Patterns Applied

**Applied**: PyTorch design philosophy (usability-first, modular components)  
**Applied**: Metric configuration pattern (declarative config with reproducibility controls)

---

## A-1: Dataset Setup [Complexity: 8, Budget: 2]

**Applied**: Standard PyTorch data loading patterns

### API Signatures

```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Problem:
    """Single problem representation."""
    task_id: str
    prompt: str
    canonical_solution: str
    test: str
    entry_point: str
    complexity: Optional[str] = None  # For controlled tasks

class HumanEvalLoader:
    def __init__(self, problem_count: int = 50, seed: int = 42):
        """Initialize loader. Loads openai_humaneval dataset."""
        ...
    
    def load_problems(self) -> List[Problem]:
        """Load all HumanEval problems. Returns: List[Problem] (164 problems)"""
        ...
    
    def select_stratified_subset(self, problems: List[Problem]) -> List[Problem]:
        """Select stratified subset. problems: [164] -> [50]"""
        ...

class ControlledTaskGenerator:
    def __init__(self, num_tasks: int = 50, seed: int = 42):
        """Initialize generator for synthetic complexity tasks."""
        ...
    
    def generate_complexity_tasks(self) -> List[Problem]:
        """Generate synthetic tasks. Returns: List[Problem] (50 tasks, 3 variants each)"""
        ...
    
    def create_labeled_solutions(self, task_id: str, complexity: str) -> str:
        """Create solution with specific complexity. complexity: ['O(n)', 'O(n log n)', 'O(n^2)']"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HumanEval loader | Load and stratify HumanEval problems |
| L-1-2 | Controlled task generator | Generate labeled complexity tasks |

---

## A-2: Solution Generation [Complexity: 12, Budget: 3]

**Applied**: HuggingFace Transformers generation API

### API Signatures

```python
from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class CodeLlamaGenerator:
    def __init__(
        self, 
        model_name: str = "meta-llama/CodeLlama-7b-Instruct-hf",
        device: str = "cuda",
        dtype: str = "float16"
    ):
        """Initialize CodeLlama model."""
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        ...
    
    def load_model(self) -> None:
        """Load model and tokenizer. Applies device_map='auto'"""
        ...
    
    def generate_solutions(
        self, 
        prompt: str, 
        num_solutions: int = 10,
        temperature: float = 0.8,
        top_p: float = 0.95,
        max_new_tokens: int = 512
    ) -> List[str]:
        """Generate diverse solutions. prompt: str -> List[str] (num_solutions)"""
        ...
    
    def batch_generate(
        self, 
        problems: List[Problem],
        num_solutions: int = 10
    ) -> Dict[str, List[str]]:
        """Batch generate for all problems. Returns: {task_id: [solutions]}"""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model initialization | Load CodeLlama with fp16 |
| L-2-2 | Solution generation | Generate diverse solutions |
| L-2-3 | Checkpointing | Save solutions per problem |

---

## A-3: Proxy Metrics [Complexity: 14, Budget: 4]

**Applied**: CodeBLEU library API + perf subprocess pattern

### API Signatures

```python
from typing import List, Dict, Tuple, Optional
import subprocess
from codebleu import calc_codebleu

class CodeBLEUMetric:
    def __init__(
        self, 
        lang: str = "python",
        weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)
    ):
        """Initialize CodeBLEU metric."""
        ...
    
    def compute(self, reference: str, prediction: str) -> Dict[str, float]:
        """Compute CodeBLEU. Returns: {'codebleu': float, 'ngram_match': float, ...}"""
        ...
    
    def batch_compute(
        self, 
        references: List[str], 
        predictions: List[str],
        repetitions: int = 5
    ) -> List[List[Dict[str, float]]]:
        """Batch compute with repetitions. Returns: [solutions][reps][metrics]"""
        ...

class RuntimeEfficiencyMetric:
    def __init__(
        self, 
        tool: str = "perf",
        event: str = "instructions",
        repetitions: int = 5
    ):
        """Initialize runtime metric."""
        ...
    
    def count_instructions(self, code: str, test_inputs: List) -> int:
        """Count CPU instructions. Returns: instruction count (int)"""
        ...
    
    def compute_ratio(
        self, 
        solution_instructions: int, 
        reference_instructions: int
    ) -> float:
        """Compute efficiency ratio. Returns: reference / max(solution, 1)"""
        ...
    
    def batch_compute(
        self, 
        solutions: List[str],
        references: List[str],
        test_inputs: List[List]
    ) -> List[List[float]]:
        """Batch compute ratios. Returns: [solutions][reps] ratios"""
        ...

class PRStyleMetric:
    def __init__(self, seed: int = 42):
        """Initialize placeholder PR-style metric."""
        ...
    
    def compute(self, code: str) -> float:
        """Compute placeholder score. Returns: random [0.0, 1.0]"""
        ...
    
    def batch_compute(self, codes: List[str], repetitions: int = 5) -> List[List[float]]:
        """Batch compute placeholder. Returns: [solutions][reps] scores"""
        ...
```

### Pseudo-code (perf measurement)

```
1. Write code to temp file
2. Run: perf stat -e instructions python temp_file.py
3. Parse stderr for "instructions" line
4. Extract integer count
5. Return count
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | CodeBLEU wrapper | Integrate codebleu library |
| L-3-2 | perf instrumentation | CPU instruction counting |
| L-3-3 | PR-style placeholder | Deterministic random scores |
| L-3-4 | Batch processing | Parallel metric computation |

---

## A-4: Reliability Analysis [Complexity: 10, Budget: 3]

**Applied**: scipy.stats statistical functions

### API Signatures

```python
from typing import List, Tuple
import numpy as np
from scipy import stats

class ReliabilityValidator:
    def __init__(self):
        """Initialize reliability validator."""
        ...
    
    def compute_cv(self, measurements: List[float]) -> float:
        """Compute coefficient of variation. measurements: [5] -> CV% (float)"""
        ...
    
    def compute_cohens_d(
        self, 
        group1: List[float], 
        group2: List[float]
    ) -> float:
        """Compute Cohen's d effect size. Returns: (mean1 - mean2) / pooled_std"""
        ...
    
    def compute_spearman_rho(
        self, 
        ranks1: List[float], 
        ranks2: List[float]
    ) -> Tuple[float, float]:
        """Compute Spearman rank correlation. Returns: (rho, p_value)"""
        ...
    
    def validate_gate_criteria(
        self,
        cv: float,
        cohens_d: float,
        spearman_rho: float,
        cv_threshold: float = 5.0,
        d_threshold: float = 0.8,
        rho_threshold: float = 0.8
    ) -> bool:
        """Check if metric passes all gate criteria. Returns: True if all pass"""
        ...
```

### Pseudo-code (CV computation)

```
1. For each solution in 500:
   a. Extract 5 repeated measurements
   b. CV = (std / mean) * 100
2. Aggregate: mean_cv = mean(all_cvs)
3. Return mean_cv
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | CV computation | Coefficient of variation across repetitions |
| L-4-2 | Cohen's d | Effect size between complexity classes |
| L-4-3 | Spearman ρ | Cross-hardware rank correlation |

---

## A-5: Visualization [Complexity: 9, Budget: 2]

**Applied**: matplotlib/seaborn plotting patterns

### API Signatures

```python
from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns

class GateMetricsPlotter:
    def __init__(self, style: str = "seaborn-v0_8"):
        """Initialize plotter with style."""
        ...
    
    def plot_gate_comparison(
        self, 
        metrics: Dict[str, Dict[str, float]],
        thresholds: Dict[str, float]
    ) -> Figure:
        """
        Plot gate metrics bar chart.
        metrics: {'CodeBLEU': {'cv': 3.2, 'cohens_d': 0.9, 'rho': 0.85}, ...}
        thresholds: {'cv': 5.0, 'cohens_d': 0.8, 'rho': 0.8}
        Returns: Figure with 3 grouped bars per metric
        """
        ...
    
    def plot_cv_distribution(
        self, 
        cvs: Dict[str, List[float]]
    ) -> Figure:
        """
        Plot CV distributions.
        cvs: {'CodeBLEU': [cv1, cv2, ...], 'Runtime': [...], ...}
        Returns: Figure with 3 subplots
        """
        ...
    
    def plot_complexity_separation(
        self, 
        data: Dict[str, Dict[str, List[float]]]
    ) -> Figure:
        """
        Plot complexity class separation.
        data: {'CodeBLEU': {'O(n)': [vals], 'O(n^2)': [vals]}, ...}
        Returns: Figure with violin plots
        """
        ...
    
    def plot_cross_hardware_correlation(
        self, 
        rankings: Dict[str, Tuple[List[float], List[float]]]
    ) -> Figure:
        """
        Plot cross-hardware scatter.
        rankings: {'CodeBLEU': (aws_ranks, local_ranks), ...}
        Returns: Figure with 3 scatter subplots
        """
        ...
    
    def save_all_figures(self, output_dir: str, figures: List[Figure]) -> None:
        """Save all figures to directory. Format: PNG 300 DPI"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Gate metrics plot | Mandatory bar chart with thresholds |
| L-5-2 | Supporting plots | CV histogram, violin plots, scatter plots |

---

## A-6: Pipeline Integration [Complexity: 11, Budget: 3]

**Applied**: Orchestrator pattern with config management

### API Signatures

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import yaml

@dataclass
class DatasetConfig:
    name: str = "HumanEval"
    source: str = "openai/openai_humaneval"
    problem_count: int = 50
    problem_selection_seed: int = 42

@dataclass
class ModelConfig:
    name: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    dtype: str = "float16"
    device_map: str = "auto"
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    num_solutions_per_problem: int = 10

@dataclass
class MetricConfig:
    codebleu_weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)
    runtime_tool: str = "perf"
    runtime_event: str = "instructions"
    runtime_repetitions: int = 5
    pr_style_implementation: str = "placeholder"

@dataclass
class ThresholdConfig:
    cv_max: float = 5.0
    cohens_d_min: float = 0.8
    spearman_rho_min: float = 0.8

@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    metrics: MetricConfig = field(default_factory=MetricConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    seed: int = 42
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        """Load config from YAML file."""
        ...
    
    def to_yaml(self, path: str) -> None:
        """Save config to YAML file."""
        ...

class ExperimentPipeline:
    def __init__(self, config: ExperimentConfig):
        """Initialize pipeline with config."""
        self.config = config
        self.loader: Optional[HumanEvalLoader] = None
        self.generator: Optional[CodeLlamaGenerator] = None
        self.metrics: Dict[str, Any] = {}
        self.validator: Optional[ReliabilityValidator] = None
        ...
    
    def run_solution_generation(self) -> Dict[str, List[str]]:
        """
        Generate all solutions.
        Returns: {task_id: [solution1, solution2, ...]} (500 total solutions)
        """
        ...
    
    def run_metric_measurement(
        self, 
        solutions: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, List[List[float]]]]:
        """
        Measure all proxies.
        Returns: {task_id: {metric_name: [[rep1, rep2, ...], ...]}}
        """
        ...
    
    def run_reliability_analysis(
        self, 
        measurements: Dict[str, Dict[str, List[List[float]]]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute reliability metrics.
        Returns: {metric_name: {'cv': float, 'cohens_d': float, 'rho': float}}
        """
        ...
    
    def run_cross_hardware_validation(self) -> Dict[str, Tuple[List[float], List[float]]]:
        """
        Validate cross-hardware stability.
        Returns: {metric_name: (platform1_ranks, platform2_ranks)}
        """
        ...
    
    def generate_report(self, results: Dict[str, Any]) -> None:
        """Generate figures and validation summary."""
        ...
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute full pipeline.
        Returns: Complete results dict with gate validation
        """
        ...
```

### Pseudo-code (pipeline execution)

```
1. Load config from YAML
2. Initialize all components (loader, generator, metrics, validator, plotter)
3. Load HumanEval problems (50 stratified)
4. Generate controlled tasks (50 synthetic)
5. Generate solutions (500 HumanEval + 150 controlled = 650 total)
   - Checkpoint after each problem
6. Measure proxies (650 solutions × 5 reps × 3 metrics = 9,750 measurements)
7. Compute reliability (CV, Cohen's d, Spearman ρ for each proxy)
8. Validate gate criteria (check thresholds)
9. Generate figures (4 required plots)
10. Save results + config + figures
11. Return validation report
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Config management | YAML load/save with validation |
| L-6-2 | Pipeline orchestrator | Execute all stages with checkpointing |
| L-6-3 | Entry point | CLI main with logging setup |

---

## Main Entry Point

### API Signatures

```python
import logging
from pathlib import Path

def setup_logging(log_file: str, level: int = logging.INFO) -> None:
    """Configure logging to console and file."""
    ...

def load_config(config_path: str) -> ExperimentConfig:
    """Load experiment config from YAML."""
    ...

def main(config_path: str = "config.yaml") -> None:
    """
    Main entry point.
    1. Setup logging
    2. Load config
    3. Initialize pipeline
    4. Execute pipeline
    5. Print validation results
    """
    ...

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    main(args.config)
```

---

## Tensor/Data Shapes Reference

| Module | Input | Output | Notes |
|--------|-------|--------|-------|
| HumanEvalLoader.load_problems | - | List[Problem] (164) | Full dataset |
| HumanEvalLoader.select_stratified_subset | List[Problem] (164) | List[Problem] (50) | Stratified sampling |
| ControlledTaskGenerator.generate_complexity_tasks | - | List[Problem] (50 × 3 variants) | Synthetic tasks |
| CodeLlamaGenerator.generate_solutions | str | List[str] (10) | Per problem |
| CodeLlamaGenerator.batch_generate | List[Problem] (50) | Dict[str, List[str]] (500 solutions) | Full batch |
| CodeBLEUMetric.compute | (str, str) | Dict[str, float] | Single measurement |
| CodeBLEUMetric.batch_compute | (List[str], List[str]) | List[List[Dict]] (500 × 5) | With repetitions |
| RuntimeEfficiencyMetric.count_instructions | str | int | CPU instruction count |
| RuntimeEfficiencyMetric.batch_compute | (List[str], List[str]) | List[List[float]] (500 × 5) | Efficiency ratios |
| PRStyleMetric.batch_compute | List[str] (500) | List[List[float]] (500 × 5) | Placeholder scores |
| ReliabilityValidator.compute_cv | List[float] (5) | float | Per solution CV |
| ReliabilityValidator.compute_cohens_d | (List[float], List[float]) | float | Between complexity classes |
| ReliabilityValidator.compute_spearman_rho | (List[float], List[float]) | (float, float) | (ρ, p-value) |

---

## Implementation Notes

### Reproducibility

All random operations use fixed seed (42):
- HumanEval problem selection
- CodeLlama generation (seed in config)
- PR-style placeholder scores
- PyTorch deterministic mode enabled

### Checkpointing

Save after each problem's solutions to `{hypothesis_folder}/outputs/solutions/{task_id}.json`:
```json
{
  "task_id": "HumanEval/0",
  "solutions": ["def func()...", "def func()..."],
  "timestamp": "2026-07-09T12:00:00Z",
  "config_hash": "abc123"
}
```

### Error Handling

- Solution generation timeout: 30s per solution
- Metric computation timeout: 10s per measurement
- Invalid solutions: Log and skip, don't crash pipeline
- perf unavailable: Fallback to wall-clock time (documented in results)

### Resource Management

- Model loaded once, kept in memory
- Batch size for generation: 1 (sequential to avoid OOM)
- Multiprocessing for metrics: `num_workers = min(cpu_count(), 8)`
- GPU memory monitoring: Log peak usage

---

## Design Validation

**Task Budget Check**:
- A-1: 2/2 subtasks ✓
- A-2: 3/3 subtasks ✓
- A-3: 4/4 subtasks ✓
- A-4: 3/3 subtasks ✓
- A-5: 2/2 subtasks ✓
- A-6: 3/3 subtasks ✓
- **Total: 17/17 subtasks (Budget: 7 epics, 17 subtasks within complexity estimates)**

**API Completeness**:
- All module signatures defined ✓
- Tensor/data shapes documented ✓
- Pseudo-code for complex algorithms ✓
- External dependencies specified ✓
- Configuration management designed ✓

**Gate Criteria Mapping**:
- CV ≤ 5%: `ReliabilityValidator.compute_cv` → aggregate mean ✓
- Cohen's d ≥ 0.8: `ReliabilityValidator.compute_cohens_d` → O(n) vs O(n²) ✓
- Spearman ρ ≥ 0.8: `ReliabilityValidator.compute_spearman_rho` → cross-hardware ✓

---

**Logic Design Status**: Ready for Phase 4 Implementation  
**Next Phase**: Phase 4 - PoC Coder  
**Estimated LOC**: ~1,200 lines (excluding tests)
