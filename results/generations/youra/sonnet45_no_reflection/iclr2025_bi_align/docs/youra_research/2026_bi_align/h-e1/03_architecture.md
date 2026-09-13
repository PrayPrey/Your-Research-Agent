---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3 - Architecture Design
generated: 2026-05-11
status: COMPLETE
---

# System Architecture: h-e1
## Policy-Layer Capability Decoupling Validation

**Version:** 1.0  
**Date:** 2026-05-11  
**Infrastructure:** LIGHT (Minimal - PoC Architecture)

**Applied Patterns:** Standard ML evaluation pipeline pattern (API-based inference + statistical analysis)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field
**Status**: Green-field - no existing code to analyze
**Analyzed Path**: N/A (no prior hypothesis code)
**Findings**: New implementation from scratch. This is the first hypothesis (h-e1) with no prerequisites.

---

## Architecture Overview

This is an EXISTENCE hypothesis (PoC validation). The architecture follows a minimal evaluation pipeline:

1. **Data Loading**: MMLU + HumanEval from standard sources
2. **Model Interface**: API-based LLM access (Claude/GPT-4)
3. **Policy Modulation**: System prompt compliance level variation
4. **Evaluation**: Accuracy measurement across λ conditions
5. **Statistical Analysis**: ICC, ANOVA, Cohen's f gate metrics
6. **Reporting**: Results + visualizations

**Design Principle**: Single-file modules with hardcoded configs (LIGHT tier).

---

## Module Structure

### 1. DataLoader (`data/loader.py`)

**Dependencies**: datasets, pandas

```python
class MMLULoader:
    def __init__(self): ...
    def load_dataset(self) -> dict: ...
    def get_few_shot_examples(self, subject: str, n: int = 4) -> list: ...
    def format_question(self, item: dict) -> str: ...

class HumanEvalLoader:
    def __init__(self): ...
    def load_dataset(self) -> dict: ...
    def format_problem(self, task_id: str) -> str: ...
```

### 2. ModelInterface (`models/api_client.py`)

**Dependencies**: anthropic OR openai, os

```python
class APIModelClient:
    def __init__(self, model_name: str, api_key: str): ...
    def generate(self, prompt: str, system_prompt: str, temperature: float = 0.0) -> str: ...
    def batch_generate(self, prompts: list, system_prompt: str) -> list: ...

class PolicyLayer:
    COMPLIANCE_PROMPTS: dict = {...}
    
    @staticmethod
    def get_system_prompt(lambda_value: float) -> str: ...
```

### 3. Evaluator (`evaluation/evaluator.py`)

**Dependencies**: ModelInterface, DataLoader

```python
class MMLUEvaluator:
    def __init__(self, model_client: APIModelClient, data_loader: MMLULoader): ...
    def evaluate(self, lambda_value: float) -> pd.DataFrame: ...
    def compute_accuracy(self, results: pd.DataFrame) -> float: ...

class HumanEvalEvaluator:
    def __init__(self, model_client: APIModelClient, data_loader: HumanEvalLoader): ...
    def evaluate(self, lambda_value: float) -> pd.DataFrame: ...
    def execute_tests(self, completions: list) -> list: ...
    def compute_pass_at_k(self, results: pd.DataFrame, k: int = 1) -> float: ...
```

### 4. StatisticalAnalyzer (`analysis/statistics.py`)

**Dependencies**: pingouin, scipy, numpy, pandas

```python
class GateAnalyzer:
    def __init__(self, results_df: pd.DataFrame): ...
    def compute_icc(self) -> tuple: ...
    def compute_anova(self) -> tuple: ...
    def compute_cohens_f(self, f_stat: float, df1: int, df2: int) -> float: ...
    def validate_gate(self) -> dict: ...
```

### 5. Visualizer (`visualization/plotter.py`)

**Dependencies**: matplotlib, seaborn, pandas

```python
class ResultsVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, metrics: dict, save_path: str): ...
    def plot_capability_consistency(self, results_df: pd.DataFrame, save_path: str): ...
    def plot_subject_heatmap(self, results_df: pd.DataFrame, save_path: str): ...
    def plot_distributions(self, results_df: pd.DataFrame, save_path: str): ...
```

### 6. Main Pipeline (`main.py`)

**Dependencies**: All modules above

```python
def setup_environment() -> dict: ...
def run_experiment(lambda_values: list) -> pd.DataFrame: ...
def analyze_results(results_df: pd.DataFrame) -> dict: ...
def generate_report(metrics: dict, results_df: pd.DataFrame, output_path: str): ...

def main():
    lambda_values = [0.2, 0.4, 0.6, 0.8, 1.0]
    results = run_experiment(lambda_values)
    metrics = analyze_results(results)
    generate_report(metrics, results, "04_validation.md")
```

---

## File Organization

```
docs/youra_research/20260511_bi_align/h-e1/
├── code/
│   ├── data/
│   │   └── loader.py                # MMLU + HumanEval data loading
│   ├── models/
│   │   └── api_client.py            # API interface + policy layer
│   ├── evaluation/
│   │   └── evaluator.py             # Accuracy measurement
│   ├── analysis/
│   │   └── statistics.py            # ICC, ANOVA, Cohen's f
│   ├── visualization/
│   │   └── plotter.py               # Figure generation
│   └── main.py                      # Experiment orchestration
├── results/
│   ├── mmlu_raw_results.csv
│   ├── humaneval_raw_results.csv
│   └── statistics_summary.json
├── figures/
│   ├── gate_metrics.png
│   ├── capability_consistency.png
│   ├── subject_heatmap.png
│   └── accuracy_distributions.png
└── config.py                        # Hardcoded constants
```

---

## Configuration Schema

**File**: `config.py` (hardcoded constants)

```python
# API Configuration
MODEL_NAME = "claude-3-opus-20240229"  # or "gpt-4-0613"
API_PROVIDER = "anthropic"  # or "openai"
TEMPERATURE = 0.0

# Compliance Levels
LAMBDA_VALUES = [0.2, 0.4, 0.6, 0.8, 1.0]

# Dataset Configuration
MMLU_DATASET = "cais/mmlu"
MMLU_SPLIT = "test"
FEW_SHOT_N = 4

HUMANEVAL_REPO = "git+https://github.com/openai/human-eval.git"

# Gate Thresholds
ICC_THRESHOLD = 0.95
ANOVA_PVALUE_THRESHOLD = 0.05
COHENS_F_THRESHOLD = 0.10

# Output Paths
OUTPUT_DIR = "docs/youra_research/20260511_bi_align/h-e1"
RESULTS_DIR = f"{OUTPUT_DIR}/results"
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
```

---

## Data Flow

1. **Input**: MMLU dataset (14k questions), HumanEval (164 problems)
2. **Processing**: For each λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}:
   - Apply system prompt with compliance level
   - Generate API responses
   - Compute accuracy metrics
3. **Aggregation**: Long-format DataFrame with columns [lambda, item_id, accuracy]
4. **Analysis**: Compute ICC, ANOVA, Cohen's f
5. **Output**: Validation report + 4 figures

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Implement MMLU + HumanEval loading with standard format | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-2 | API Client | Build API wrapper with policy-layer system prompts | 9 | Module(3) + Deps(2) + Algo(2) + Integ(2) |
| A-3 | Evaluation Engine | MMLU/HumanEval evaluators with accuracy computation | 11 | Module(3) + Deps(2) + Algo(4) + Integ(2) |
| A-4 | Statistical Analysis | ICC, ANOVA, Cohen's f with gate validation | 12 | Module(2) + Deps(3) + Algo(5) + Integ(2) |
| A-5 | Visualization | Generate 4 required figures (gate metrics, consistency, heatmap, distributions) | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| A-6 | Orchestration | Main pipeline with error handling and validation report generation | 9 | Module(2) + Deps(2) + Algo(2) + Integ(3) |

**Complexity Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5, A-6], Low(4-8): [A-1]

**Total Complexity**: 59 (Average: 9.8 per task)

---

## Dependencies

### External Libraries
- `anthropic` or `openai` - API clients
- `datasets` - HuggingFace MMLU loading
- `human-eval` - HumanEval benchmark (pip install from GitHub)
- `pingouin` - ICC computation
- `scipy` - ANOVA and effect sizes
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `matplotlib`, `seaborn` - Visualization

### Installation
```bash
pip install anthropic openai datasets pingouin scipy pandas numpy matplotlib seaborn
pip install git+https://github.com/openai/human-eval.git
```

---

## Error Handling Strategy

1. **API Failures**: Retry up to 3 times with 15-second delay
2. **Dataset Loading**: Fail fast with clear error message
3. **Statistical Computation**: Validate input shapes before analysis
4. **Progress Saving**: Checkpoint after each λ evaluation

---

## Testing Strategy

**Smoke Test Only** (LIGHT tier):
- Verify API connection
- Load sample from MMLU (1 subject)
- Load sample from HumanEval (5 problems)
- Run single λ condition
- Check output file generation

---

## Validation Criteria

**Code Readiness**:
- [ ] All 6 modules implemented with interfaces above
- [ ] Main pipeline runs end-to-end
- [ ] Outputs saved to correct paths

**Experiment Success**:
- [ ] ICC > 0.95
- [ ] ANOVA p > 0.05
- [ ] Cohen's f < 0.10
- [ ] All 4 figures generated

---

**Document Status**: COMPLETE  
**Next Phase**: Logic Design (03_logic.md)
