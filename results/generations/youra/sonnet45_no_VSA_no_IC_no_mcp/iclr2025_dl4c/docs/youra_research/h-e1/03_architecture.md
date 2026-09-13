# Architecture Design: h-e1

**Date:** 2026-08-25
**Hypothesis:** h-e1 (EXISTENCE)
**Type:** PoC - Minimal correlation measurement infrastructure
**PRD:** 03_prd.md

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing code - baseline correlation measurement pipeline

---

## Applied Patterns (Archon KB)

Applied: Statistical experiment pipeline (data → compute → analyze → visualize)

---

## System Overview

Correlation measurement infrastructure to validate that execution, AI, and human feedback show measurable correlations (not noise) across three code generation tasks.

**Purpose:** EXISTENCE validation - does correlation structure exist?

**Not included (per PoC rules):**
- Real human annotation (simulated only)
- Model training/fine-tuning
- Advanced reward models
- Ablation studies

---

## Module Structure

### 1. DatasetManager (`data_loader.py`)

**Dependencies:** datasets, numpy

```python
def load_humaneval(n: int = 100) -> List[Dict[str, Any]]:
    """Load first n HumanEval problems."""
    ...

def load_mbpp(n: int = 100, seed: int = 42) -> List[Dict[str, Any]]:
    """Randomly sample n MBPP problems."""
    ...

def load_swe_bench(n: int = 100, seed: int = 42) -> List[Dict[str, Any]]:
    """Randomly sample n SWE-bench issues."""
    ...
```

**Output format:** `List[{"id": str, "prompt": str, "tests": List[str]}]`

---

### 2. CodeGenerator (`generator.py`)

**Dependencies:** transformers, torch

```python
class CodeGenModel:
    def __init__(self, model_name: str = "Salesforce/codegen-16B-mono"): ...
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate single code sample."""
        ...
    
    def batch_generate(self, prompts: List[str], batch_size: int = 8) -> List[str]:
        """Generate multiple samples efficiently."""
        ...
```

**Default params:** temperature=0.8, top_p=0.95, max_tokens=512

---

### 3. FeedbackCollectors (`feedback.py`)

**Dependencies:** subprocess, transformers

```python
def execute_code(code: str, tests: List[str], timeout: int = 5) -> int:
    """Run tests, return 1 if pass, 0 if fail."""
    ...

def ai_score(prompt: str, code: str, model: str = "gpt-3.5-turbo") -> float:
    """Score code quality in [0, 1]."""
    ...

def simulate_human_ratings(code: str, exec_result: int, num_raters: int = 3) -> List[float]:
    """Simulate raters: base=exec_result, noise=±0.2 uniform."""
    ...

def compute_inter_rater_reliability(ratings: np.ndarray) -> float:
    """Cohen's kappa across all samples."""
    ...
```

---

### 4. CorrelationAnalyzer (`analysis.py`)

**Dependencies:** scipy, numpy

```python
def compute_pairwise_correlations(exec: np.ndarray, ai: np.ndarray, human: np.ndarray) -> Dict[str, Tuple[float, float]]:
    """Return {pair: (r, p)} for all 3 combinations."""
    ...

def bootstrap_ci(data1: np.ndarray, data2: np.ndarray, n_iter: int = 1000) -> Tuple[float, float]:
    """95% CI for Pearson r."""
    ...

def evaluate_gate(correlations: Dict, kappa: float) -> bool:
    """Check p<0.05 for all correlations and kappa>0.6."""
    ...
```

---

### 5. Visualizer (`visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
def plot_correlation_matrix(corr_data: np.ndarray, dataset_name: str, output_dir: Path): ...

def plot_scatter(x: np.ndarray, y: np.ndarray, labels: Tuple[str, str], output_path: Path): ...

def plot_distributions(exec: np.ndarray, ai: np.ndarray, human: np.ndarray, output_dir: Path): ...

def plot_bootstrap_ci(correlations: Dict, cis: Dict, output_path: Path): ...
```

---

### 6. MainRunner (`run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    # Load datasets
    datasets = {
        "humaneval": load_humaneval(100),
        "mbpp": load_mbpp(100, seed=42),
        "swe_bench": load_swe_bench(100, seed=42)
    }
    
    # Generate code
    generator = CodeGenModel()
    samples = {name: generator.batch_generate([d["prompt"] for d in data])
               for name, data in datasets.items()}
    
    # Collect feedback
    feedback = {}
    for name, data in datasets.items():
        exec_fb = [execute_code(s, d["tests"]) for s, d in zip(samples[name], data)]
        ai_fb = [ai_score(d["prompt"], s) for d, s in zip(data, samples[name])]
        human_fb = [np.mean(simulate_human_ratings(s, e)) for s, e in zip(samples[name], exec_fb)]
        feedback[name] = {"exec": exec_fb, "ai": ai_fb, "human": human_fb}
    
    # Analyze correlations
    results = {}
    for name, fb in feedback.items():
        results[name] = compute_pairwise_correlations(fb["exec"], fb["ai"], fb["human"])
    
    # Visualize
    for name in datasets:
        plot_correlation_matrix(results[name], name, figures_dir)
        plot_scatter(feedback[name]["exec"], feedback[name]["human"], 
                    ("Execution", "Human"), figures_dir / f"scatter_{name}.png")
    
    # Gate evaluation
    gate_pass = all(evaluate_gate(results[name], kappa) for name in datasets)
    write_validation_report(results, gate_pass)
```

---

## Data Flow

```
Dataset Loaders → [problems with prompts and tests]
                         ↓
Code Generator → [300 generated code samples]
                         ↓
Feedback Collectors → [exec_fb, ai_fb, human_fb] (900 values total)
                         ↓
Correlation Analyzer → [9 correlation stats + CIs]
                         ↓
                  ├→ Visualizer → [18 PNG figures]
                  └→ Gate Evaluator → [04_validation.md]
```

---

## Interface Contracts

### Dataset Output Schema
```python
{
    "id": str,           # Problem identifier
    "prompt": str,       # Code generation prompt
    "tests": List[str]   # Test cases (executable Python)
}
```

### Feedback Arrays
```python
exec_feedback: np.ndarray[int]    # Shape (100,), values {0, 1}
ai_feedback: np.ndarray[float]    # Shape (100,), values [0, 1]
human_feedback: np.ndarray[float] # Shape (100,), values [0, 1]
```

### Correlation Results
```python
{
    "exec_human": (r: float, p: float),
    "ai_human": (r: float, p: float),
    "exec_ai": (r: float, p: float)
}
```

### Gate Output
```python
{
    "pass": bool,
    "correlations": Dict[str, Dict[str, Tuple[float, float]]],  # dataset → pair → (r, p)
    "kappa": float,
    "failure_reason": Optional[str]
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Dataset Setup | Implement all 3 loaders with sampling logic | 8 | Module(2) + Deps(1) + Algo(3) + Integration(2) |
| E2 | Code Generation | CodeGen model wrapper with batching | 10 | Module(3) + Deps(2) + Algo(2) + Integration(3) |
| E3 | Feedback Collection | Execute tests, AI scoring, human simulation | 14 | Module(4) + Deps(3) + Algo(4) + Integration(3) |
| E4 | Statistical Analysis | Correlations, bootstrap CIs, gate logic | 12 | Module(3) + Deps(2) + Algo(4) + Integration(3) |
| E5 | Visualization | All plots (matrices, scatters, distributions) | 9 | Module(3) + Deps(2) + Algo(2) + Integration(2) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [E3], Medium(9-13): [E2, E4, E5], Low(4-8): [E1]

---

## Technology Stack

**Core Libraries:**
- `transformers==4.30.0` - CodeGen model
- `datasets==2.12.0` - HumanEval, MBPP
- `scipy==1.10.0` - pearsonr, statistical tests
- `scikit-learn==1.2.0` - cohen_kappa_score
- `numpy==1.24.0` - numerical ops
- `matplotlib==3.7.0` + `seaborn==0.12.0` - visualization
- `torch==2.0.0` - model inference

**Execution:**
- Python 3.10+
- 1x A100 40GB GPU
- ~2-4 hours runtime

---

## File Structure

```
h-e1/code/
├── data_loader.py      # Dataset loading (E1)
├── generator.py        # Code generation (E2)
├── feedback.py         # Feedback collection (E3)
├── analysis.py         # Statistical analysis (E4)
├── visualize.py        # Plotting (E5)
├── run_experiment.py   # Main orchestrator
└── config.yaml         # Hyperparameters

h-e1/outputs/
├── samples.jsonl       # Cached generated code
└── feedback.jsonl      # Raw feedback values

h-e1/figures/           # Auto-generated plots (18 files)
```

---

## Error Handling Strategy

**Dataset loading failures:** Retry with exponential backoff (max 3 attempts)
**GPU OOM:** Fallback to CodeGen-2B-mono (7x smaller)
**Execution timeouts:** Mark as fail, log error, continue
**Missing dependencies:** Fail fast with clear error message

---

## Validation Checks

**Self-checks before Phase 4:**
- [ ] 5 Epic tasks (PoC scope)
- [ ] Module interfaces = code signatures only
- [ ] No ASCII diagrams in data flow
- [ ] Total length <500 lines
- [ ] Green-field project noted in Serena section

---

**Next Phase:** Phase 4 - Task breakdown and implementation
