# Architecture: h-e1 SMT Constraint Extraction

**Date:** 2026-08-28
**Hypothesis:** H-E1 (EXISTENCE - PoC)
**Author:** Phase 3 Architecture Agent

Applied: Static analysis pipeline pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing code to analyze

---

## System Overview

Pipeline: HumanEval → Pydantic Extension → LLM Generation → Pyre Analysis → Z3 Validation → Metrics → Figures

**Goal:** Validate ≥90% extraction success rate for SMT constraints from LLM-generated typed Python.

---

## Module Structure

### DatasetExtender (`data/extend_humaneval.py`)

**Dependencies:** HuggingFace datasets, Pydantic

```python
class DatasetExtender:
    def load_humaneval(self) -> list: ...
    def add_pydantic_annotations(self, problem: dict) -> dict: ...
    def save_extended_dataset(self, problems: list, output_dir: str): ...
```

### LLMGenerator (`src/llm_generator.py`)

**Dependencies:** Anthropic API

```python
class LLMGenerator:
    def __init__(self, api_key: str, model: str, temperature: float): ...
    def generate_code(self, prompt: str) -> str: ...
    def batch_generate(self, prompts: list, output_dir: str) -> list: ...
```

### PyreExtractor (`src/pyre_extractor.py`)

**Dependencies:** pyre-check

```python
class PyreExtractor:
    def extract_constraints(self, python_file: str) -> list: ...
    def parse_pyre_output(self, json_output: dict) -> list: ...
    def batch_extract(self, code_files: list, output_dir: str) -> dict: ...
```

### Z3Validator (`src/z3_validator.py`)

**Dependencies:** z3-solver

```python
class Z3Validator:
    def check_satisfiability(self, constraint: dict) -> bool: ...
    def compute_quality_rate(self, constraints: list) -> float: ...
```

### MetricsEngine (`src/metrics.py`)

**Dependencies:** PyreExtractor, Z3Validator

```python
class MetricsEngine:
    def compute_extraction_rate(self, results: dict) -> float: ...
    def compute_quality_rate(self, constraints: list) -> float: ...
    def evaluate_gate(self, extraction_rate: float, threshold: float) -> str: ...
    def save_metrics(self, metrics: dict, output_path: str): ...
```

### Visualizer (`src/visualize.py`)

**Dependencies:** matplotlib, pandas

```python
class Visualizer:
    def plot_gate_metrics(self, metrics: dict, output_path: str): ...
    def plot_success_by_complexity(self, results: list, output_path: str): ...
    def plot_constraint_distribution(self, constraints: list, output_path: str): ...
    def render_failure_table(self, failures: list, output_path: str): ...
```

### Pipeline (`src/pipeline.py`)

**Dependencies:** All above modules

```python
class ExperimentPipeline:
    def __init__(self, config: dict): ...
    def run_full_pipeline(self): ...
    def run_stage(self, stage_name: str): ...
```

---

## File Structure

```
h-e1/
  data/
    extend_humaneval.py          # DatasetExtender
    humaneval_pydantic/          # Extended dataset output
      problem_*.json
  src/
    llm_generator.py             # LLMGenerator
    pyre_extractor.py            # PyreExtractor
    z3_validator.py              # Z3Validator
    metrics.py                   # MetricsEngine
    visualize.py                 # Visualizer
    pipeline.py                  # ExperimentPipeline
    config.py                    # Configuration
  outputs/
    generated_code/              # LLM outputs
      program_*.py
    constraints/                 # Pyre extraction results
      program_*.json
    metrics.json                 # Final metrics
  figures/
    gate_metrics.png             # Mandatory
    success_by_complexity.png
    constraint_types.png
    failure_modes.png
```

---

## Data Flow

1. **DatasetExtender** loads HumanEval, adds Pydantic annotations → `data/humaneval_pydantic/`
2. **LLMGenerator** reads extended prompts → Claude API → `outputs/generated_code/`
3. **PyreExtractor** runs `pyre analyze` on each file → `outputs/constraints/`
4. **Z3Validator** checks constraint satisfiability → quality metrics
5. **MetricsEngine** computes extraction rate + quality rate → `outputs/metrics.json`
6. **Visualizer** generates 4 figures → `figures/`

---

## Integration Points

**External APIs:**
- Anthropic API (`claude-sonnet-3-5-20240620`)
  - Rate limit: 10 req/min
  - Config: temperature=0.2, max_tokens=512

**External Tools:**
- Pyre: `pyre analyze --output-format json`
- Z3: Python API (`z3-solver`)

**External Datasets:**
- HuggingFace: `load_dataset("openai_humaneval")`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Extension | Load HumanEval, add Pydantic annotations, save 100 extended problems | 8 | setup(2) + annotation(4) + validation(2) |
| A-2 | LLM Code Generation | Configure Anthropic API, batch generate 100 programs, handle retries | 9 | api_client(3) + batch_loop(3) + error_handling(3) |
| A-3 | Constraint Extraction | Integrate Pyre, parse JSON output, batch process 100 files | 10 | pyre_integration(4) + json_parsing(3) + batch(3) |
| A-4 | Constraint Validation | Z3 satisfiability checks, compute quality rate | 7 | z3_integration(3) + sat_check(2) + metrics(2) |
| A-5 | Metrics & Visualization | Compute extraction/quality rates, generate 4 figures, save outputs | 11 | metrics_logic(4) + 4_plots(4) + file_io(3) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5], Low(4-8): [A-1, A-4]

---

## Configuration

### config.py

```python
CONFIG = {
    "llm": {
        "model": "claude-sonnet-3-5-20240620",
        "temperature": 0.2,
        "max_tokens": 512,
        "rate_limit_rpm": 10
    },
    "dataset": {
        "source": "openai_humaneval",
        "subset_size": 100
    },
    "pyre": {
        "output_format": "json"
    },
    "thresholds": {
        "extraction_success": 90.0,
        "constraint_quality": 80.0
    },
    "paths": {
        "data": "data/humaneval_pydantic",
        "outputs": "outputs",
        "figures": "figures"
    }
}
```

---

## Validation Checkpoints

- After A-1: 100 JSON files in `data/humaneval_pydantic/`
- After A-2: 100 Python files in `outputs/generated_code/`
- After A-3: 100 JSON files in `outputs/constraints/`
- After A-5: `metrics.json` exists with gate_result field

---

## Success Criteria

**PoC Pass:**
1. Code executes without fatal errors
2. `extraction_success_rate >= 90.0`
3. `constraint_quality_rate > 80.0`
4. 4 figures generated

**Gate Result:** PASS/FAIL → determines pivot to neural extraction

---

## Notes

- No training loop (static analysis experiment)
- Single-pass generation (temperature=0.2 for determinism)
- Z3 validation is secondary metric (not gate condition)
- All outputs timestamped for reproducibility
