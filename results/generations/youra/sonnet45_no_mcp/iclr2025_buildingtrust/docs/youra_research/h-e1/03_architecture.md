# Architecture Design: h-e1

**Hypothesis:** Dimensional Separability in Trustworthiness Benchmarks  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-04-14  
**Applied Patterns:** Minimal evaluation pipeline, statistical analysis module

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing code - fresh EXISTENCE (PoC) experiment

---

## Executive Summary

EXISTENCE hypothesis architecture for validating dimensional separability through rank correlation analysis. Minimal structure: benchmark evaluators + statistical analyzer + visualization generator. No training infrastructure needed (evaluation-only).

**Key Design Decisions:**
- Single-file benchmark evaluators (no abstraction overhead for PoC)
- Hardcoded model list (8 models specified in PRD)
- Sequential evaluation (no parallel processing for simplicity)
- CSV output for results (no database)

---

## Module Structure

### BenchmarkEvaluator (`src/evaluators.py`)

**Dependencies**: transformers, datasets, textattack

```python
class TruthfulQAEvaluator:
    def __init__(self): ...
    def evaluate(self, model, tokenizer) -> float: ...

class BOLDEvaluator:
    def __init__(self): ...
    def evaluate(self, model, tokenizer) -> float: ...

class HaluEvalEvaluator:
    def __init__(self): ...
    def evaluate(self, model, tokenizer) -> float: ...

class TextAttackEvaluator:
    def __init__(self): ...
    def evaluate(self, model, tokenizer) -> float: ...
    def apply_perturbations(self, texts: list) -> list: ...
```

---

### RankCorrelationAnalyzer (`src/analysis.py`)

**Dependencies**: scipy, numpy

```python
class RankCorrelationAnalyzer:
    def __init__(self, dimensions: list): ...
    def compute_rankings(self, scores: dict) -> dict: ...
    def compute_kendall_tau(self, baseline_ranks: list, stressed_ranks: list) -> tuple: ...
    def compute_asymmetry(self, delta_taus: dict) -> tuple: ...
    def validate_gate(self, asymmetry: dict, variance: float) -> bool: ...
```

---

### Visualizer (`src/visualizer.py`)

**Dependencies**: matplotlib, seaborn

```python
class ResultVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, target: dict, actual: dict) -> None: ...
    def plot_correlation_heatmap(self, tau_values: dict) -> None: ...
    def plot_asymmetry_bars(self, asymmetry: dict, threshold: float) -> None: ...
    def plot_rank_shifts(self, baseline_ranks: dict, stressed_ranks: dict) -> None: ...
    def plot_variance_distribution(self, delta_taus: list) -> None: ...
```

---

### MainPipeline (`src/main.py`)

**Dependencies**: All above modules

```python
def load_models(model_names: list) -> dict: ...
def run_baseline_evaluation(models: dict, evaluators: dict) -> dict: ...
def run_stressed_evaluation(models: dict, evaluators: dict, perturbations: dict) -> dict: ...
def save_results(results: dict, filepath: str) -> None: ...
def main(): ...
```

---

### Configuration (`src/config.py`)

**Dependencies**: None

```python
MODEL_NAMES: list
BENCHMARKS: list
DIMENSIONS: dict
GATE_THRESHOLDS: dict
OUTPUT_PATHS: dict
RANDOM_SEED: int
```

---

## File Organization

```
docs/youra_research/20260414_buildingtrust/h-e1/
├── code/
│   └── src/
│       ├── config.py          # Hardcoded configuration
│       ├── evaluators.py      # 4 benchmark evaluators
│       ├── analysis.py        # Rank correlation + gate validation
│       ├── visualizer.py      # 5 figures generation
│       └── main.py            # Orchestration pipeline
├── data/                      # Auto-downloaded by HuggingFace
├── results/                   # CSV outputs
│   ├── baseline_scores.csv
│   ├── stressed_scores.csv
│   ├── rankings.csv
│   └── statistics.csv
├── figures/                   # Generated visualizations
│   ├── gate_metrics.png
│   ├── correlation_heatmap.png
│   ├── asymmetry_bars.png
│   ├── rank_shifts.png
│   └── variance_distribution.png
└── 04_validation.md           # Generated report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Environment Setup | Install dependencies, configure GPU, verify model access | 5 | 1+1+2+1 (config+deps+gpu+verify) |
| E2 | Benchmark Evaluators | Implement 4 evaluators (TruthfulQA, BOLD, HaluEval, TextAttack) | 14 | 4+3+4+3 (module+deps+algo+integration) |
| E3 | Baseline Evaluation | Load 8 models, run baseline evaluation, save scores | 9 | 2+2+3+2 (load+eval+save+rankings) |
| E4 | Stress Testing | Apply TextAttack perturbations, re-evaluate models | 11 | 3+2+4+2 (perturb+eval+correctness+integration) |
| E5 | Statistical Analysis | Kendall's tau, asymmetry, variance, gate validation | 10 | 2+2+4+2 (tau+asymmetry+gate+significance) |
| E6 | Visualization | Generate 5 required figures | 7 | 1+1+3+2 (setup+plots+styling+save) |

**Total Complexity**: 56 (6 tasks)

**Distribution**:
- VeryHigh(18-20): []
- High(14-17): [E2]
- Medium(9-13): [E3, E4, E5]
- Low(4-8): [E1, E6]

---

## Dependencies

**External Libraries:**
- torch >= 2.0.0
- transformers >= 4.30.0
- datasets >= 2.10.0
- textattack >= 0.3.0
- scipy >= 1.10.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- pandas >= 2.0.0
- tqdm >= 4.65.0

**Hardware:**
- Single GPU (16GB+ VRAM recommended)
- Selected via `export CUDA_VISIBLE_DEVICES=<gpu_id>`

---

## Data Flow

1. **Model Loading**: HuggingFace → 8 pre-trained models → Memory
2. **Baseline Evaluation**: Models → 4 Evaluators → Scores → Rankings
3. **Perturbation**: TextAttack → Perturbed Inputs → Cache
4. **Stressed Evaluation**: Models → 4 Evaluators (perturbed) → Scores → Rankings
5. **Analysis**: Rankings → RankCorrelationAnalyzer → Kendall's τ, Δτ, Asymmetry
6. **Gate Validation**: Asymmetry + Variance → Gate Check → PASS/FAIL
7. **Visualization**: Results → Visualizer → 5 Figures
8. **Reporting**: All Results → 04_validation.md

---

## Success Validation

**Gate Criteria:**
- Primary: |Δτ| ≥ 0.2 in ≥2 dimension pairs (p < 0.01)
- Secondary: Variance(Δτ) > 0.02

**Output Artifacts:**
- ✓ baseline_scores.csv
- ✓ stressed_scores.csv
- ✓ rankings.csv
- ✓ statistics.csv
- ✓ 5 figures (gate_metrics, correlation_heatmap, asymmetry_bars, rank_shifts, variance_distribution)
- ✓ 04_validation.md

---

**Document Status**: Complete  
**Next Phase**: Phase 4 (Implementation)  
**Estimated LOC**: ~800 lines total
