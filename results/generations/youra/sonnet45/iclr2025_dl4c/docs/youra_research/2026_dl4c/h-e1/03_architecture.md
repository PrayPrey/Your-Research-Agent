# System Architecture: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18
**Author:** Phase 3 Architecture Agent

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** Fresh EXISTENCE hypothesis - minimal PoC architecture only.

---

## Knowledge Base Patterns Applied

Applied: sklearn clustering pipeline pattern (StandardScaler → PCA → KMeans)

---

## Architecture Overview

**Scope:** Standalone evaluation pipeline for alignment method clustering analysis.
**Pattern:** Sequential profiling + batch clustering.
**Infrastructure:** LIGHT tier - hardcoded config, print logging, CSV output.

**File Organization:**
```
h-e1/code/
├── config.py              # Hardcoded configuration
├── data_loader.py         # HumanEval+ dataset loading
├── model_manager.py       # Model loading and inference
├── profiler.py            # Correctness, complexity, efficiency profiling
├── clustering.py          # PCA + k-means + effect size
├── visualizer.py          # 5 figures + gate metrics
└── run_experiment.py      # Entry point
```

---

## Module Specifications

### ConfigModule (`config.py`)

**Dependencies:** None

```python
class ExperimentConfig:
    MODELS: list[tuple[str, str]] = [
        ("codellama/CodeLlama-7b-hf", "baseline"),
        ("codellama/CodeLlama-7b-Python-hf", "execution"),
        # ... 6-8 models total
    ]
    TEMPERATURE: float = 0.8
    TOP_P: float = 0.95
    MAX_TOKENS: int = 512
    NUM_SAMPLES: int = 64
    RANDOM_SEED: int = 42
    TIMEOUT: float = 3.0
    N_WORKERS: int = 4
    K_CLUSTERS: int = 3
    COHENS_D_THRESHOLD: float = 1.5
```

---

### DataModule (`data_loader.py`)

**Dependencies:** evalplus, datasets

```python
class HumanEvalPlusLoader:
    def __init__(self): ...
    def load_dataset(self) -> dict[str, dict]: ...
    def get_problem(self, task_id: str) -> dict: ...
```

---

### ModelModule (`model_manager.py`)

**Dependencies:** transformers, torch, ConfigModule

```python
class ModelManager:
    def __init__(self, config: ExperimentConfig): ...
    def load_model(self, model_name: str) -> tuple: ...
    def unload_model(self) -> None: ...
    def generate_sample(self, prompt: str) -> str: ...
    def generate_batch(self, task: dict, n: int) -> list[str]: ...
```

---

### ProfilerModule (`profiler.py`)

**Dependencies:** radon, lizard, cProfile, tracemalloc, scipy, ModelModule, DataModule

```python
class CodeProfiler:
    def __init__(self, timeout: float = 3.0, n_workers: int = 4): ...
    def profile_correctness(self, samples: list[str], tests: str) -> float: ...
    def profile_complexity(self, samples: list[str]) -> tuple[float, float]: ...
    def profile_efficiency(self, samples: list[str]) -> tuple[float, float]: ...
    def extract_signature(self, task: dict, samples: list[str]) -> dict: ...
```

---

### ClusteringModule (`clustering.py`)

**Dependencies:** sklearn, numpy, scipy, ProfilerModule

```python
class AlignmentClusterer:
    def __init__(self, k: int = 3, random_state: int = 42): ...
    def prepare_features(self, signatures: list[dict]) -> np.ndarray: ...
    def fit_pca(self, X: np.ndarray) -> np.ndarray: ...
    def fit_kmeans(self, X_pca: np.ndarray) -> np.ndarray: ...
    def compute_cohens_d(self, X_pca: np.ndarray, labels: np.ndarray) -> float: ...
    def compute_silhouette(self, X_pca: np.ndarray, labels: np.ndarray) -> float: ...
    def compute_purity(self, labels: np.ndarray, alignment_types: list[str]) -> float: ...
```

---

### VisualizerModule (`visualizer.py`)

**Dependencies:** matplotlib, pandas, scipy, ClusteringModule

```python
class ResultVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_3d_scatter(self, X_pca: np.ndarray, labels: np.ndarray, alignment_types: list[str]) -> None: ...
    def plot_heatmap(self, signatures: list[dict], model_names: list[str]) -> None: ...
    def plot_boxplots(self, signatures: list[dict], alignment_types: list[str]) -> None: ...
    def plot_dendrogram(self, X: np.ndarray, model_names: list[str]) -> None: ...
    def plot_effect_size(self, cohens_d: float, ci_lower: float, ci_upper: float) -> None: ...
    def plot_gate_metrics(self, target: float, actual: float) -> None: ...
```

---

## External Dependencies (Base Hypothesis)

**N/A** - This is a foundation hypothesis with no base code to reuse.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Install evalplus, transformers, profiling packages. Verify GPU access. | 5 | 1+1+1+2 (install+test+verify+smoke) |
| A-2 | Data Loading | Implement HumanEvalPlusLoader. Load 164 problems. Validate structure. | 6 | 2+2+1+1 (loader+validation+test+doc) |
| A-3 | Model Management | Implement ModelManager. Load 6-8 models sequentially. Test generation. | 15 | 4+4+4+3 (loading+generation+sequential+error) |
| A-4 | Profiling Pipeline | Implement CodeProfiler (correctness, complexity, efficiency). Parallel execution. | 16 | 5+4+4+3 (correctness+complexity+efficiency+parallel) |
| A-5 | Clustering Analysis | Implement AlignmentClusterer (PCA, k-means, effect size, metrics). | 13 | 4+3+3+3 (PCA+kmeans+cohens_d+metrics) |
| A-6 | Visualization | Generate 5 figures + gate metrics. Color-blind palette. High-res export. | 11 | 3+3+2+3 (3D+heatmap+boxplot+dendrogram+effect+gate) |
| A-7 | Experiment Orchestration | Implement run_experiment.py. Loop over models, aggregate results, save outputs. | 12 | 3+3+3+3 (loop+aggregation+save+logging) |

**Total Complexity:** 78
**Distribution:** VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-5, A-6, A-7], Low(4-8): [A-1, A-2]

---

## Data Flow

```
1. DataModule loads HumanEval+ (164 tasks)
2. For each model in MODELS:
   a. ModelModule loads model → GPU
   b. For each task:
      - Generate 64 samples (temperature=0.8)
      - ProfilerModule extracts (correctness, complexity, efficiency)
   c. ModelModule unloads model (free GPU memory)
3. ClusteringModule:
   - Flatten signatures → StandardScaler → PCA(3) → KMeans(3)
   - Compute Cohen's d, silhouette, purity
4. VisualizerModule generates 6 figures
5. Save results to CSV + figures to PNG
```

---

## Integration Points

**Input:**
- `02c_experiment_brief.md` (experiment specification)
- `03_prd.md` (functional requirements)

**Output:**
- `04_validation.md` (Phase 4 validation report)
- `h-e1/code/*.py` (implementation files)
- `h-e1/figures/*.png` (6 visualizations)
- `h-e1/results/signatures.csv` (performance signatures)
- `h-e1/results/metrics.csv` (clustering metrics)

**State:**
- `verification_state.yaml` (gate evaluation: Cohen's d > 1.5σ)

---

## Non-Functional Requirements

### Performance
- Sequential model loading (GPU memory constraints)
- Parallel test execution (4 workers)
- Expected runtime: 10-15 GPU-hours (6-8 models × 164 tasks × 64 samples)

### Reproducibility
- Fixed seeds: `random.seed(42)`, `np.random.seed(42)`, `torch.manual_seed(42)`
- Deterministic k-means: `random_state=42`

### Error Handling
- Model loading failures: Skip model, log warning
- Generation timeouts: Skip sample, continue
- Test execution errors: Mark as failed, count in pass@k

### Logging
- Print statements for progress tracking
- CSV output for metrics storage
- No WandB, no structured logging (LIGHT tier)

---

## Validation Checklist

**Pre-execution:**
- [ ] GPU available (≥14GB VRAM)
- [ ] All 6-8 models accessible on HuggingFace
- [ ] Python packages installed (evalplus, transformers, torch, radon, lizard, sklearn, scipy, matplotlib, pandas)

**Post-execution:**
- [ ] All models generated samples successfully
- [ ] Cohen's d computed without error
- [ ] 6 figures saved to `h-e1/figures/`
- [ ] Gate evaluation: Cohen's d > 1.5σ (pass) or < 1.5σ (fail → HALT)

---

**End of Architecture Document**

*Ready for Phase 3 Logic Design (03b_logic.md)*
