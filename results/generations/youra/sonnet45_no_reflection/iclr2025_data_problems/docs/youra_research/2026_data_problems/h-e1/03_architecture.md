---
name: "Architecture: h-e1 Three-Tier Contamination Detection System"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-11
phase: Phase 3 - Architecture
source: 03_prd.md, 02c_experiment_brief.md
---

# System Architecture: h-e1

**Applied**: Modular detection pipeline pattern (minimal PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing code - PoC implementation with minimal architecture

---

## Module Structure

### DataLoader (`src/data/loader.py`)

**Dependencies**: datasets, torch

```python
class ContaminationDataset:
    def __init__(self, contamination_rate: float, seed: int): ...
    def load_gsm8k(self) -> Dataset: ...
    def load_math(self) -> Dataset: ...
    def paraphrase_samples(self, samples: List[dict], api_key: str) -> List[dict]: ...
    def create_contaminated_mix(self) -> Dataset: ...

def create_dataloader(dataset: Dataset, batch_size: int) -> DataLoader: ...
```

---

### BaseModel (`src/models/model.py`)

**Dependencies**: transformers, torch

```python
class Llama2Model:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf"): ...
    def forward(self, input_ids: Tensor, attention_mask: Tensor) -> Tensor: ...
    def generate(self, input_ids: Tensor, max_length: int) -> Tensor: ...
```

---

### Tier1DataFilter (`src/detectors/tier1.py`)

**Dependencies**: datasketch, datetime

```python
class Tier1DataFilter:
    def __init__(self, benchmark_release_date: str, lsh_bands: int = 20, lsh_rows: int = 5): ...
    def check_temporal_isolation(self, sample_timestamp: str) -> bool: ...
    def check_lsh_fingerprint(self, sample: str) -> bool: ...
    def detect(self, training_data: List[dict]) -> bool: ...
```

---

### Tier2TSGProbes (`src/detectors/tier2.py`)

**Dependencies**: torch, numpy

```python
class Tier2TSGProbes:
    def __init__(self, benchmark_samples: List[dict]): ...
    def extract_tsg_invariants(self, samples: List[dict]) -> List[dict]: ...
    def generate_neighbor_probes(self, samples: List[dict]) -> List[dict]: ...
    def generate_broken_probes(self, samples: List[dict]) -> List[dict]: ...
    def evaluate_probes(self, model: nn.Module, probes: List[dict]) -> float: ...
    def compute_differential_alignment(self, model: nn.Module, training_losses: List[float], clean_std: float) -> bool: ...
```

---

### Tier3GeometricDetection (`src/detectors/tier3.py`)

**Dependencies**: torch, hessian_eigenthings, numpy

```python
class Tier3GeometricDetection:
    def __init__(self, model: nn.Module, benchmark_dataloader: DataLoader): ...
    def compute_gradient_overlap(self) -> float: ...
    def compute_hessian_concentration(self) -> float: ...
    def compute_cka_alignment(self) -> float: ...
    def compute_efficiency_zscore(self, baseline_mean: float, baseline_std: float) -> float: ...
    def detect(self, thresholds: dict) -> bool: ...
```

---

### CombinedDetector (`src/detectors/combined.py`)

**Dependencies**: tier1, tier2, tier3

```python
class CombinedDetector:
    def __init__(self, tier1: Tier1DataFilter, tier2: Tier2TSGProbes, tier3: Tier3GeometricDetection): ...
    def detect_contamination(self, model: nn.Module, training_data: List[dict], clean_baseline_stats: dict) -> dict: ...
```

---

### TrainingLoop (`src/train.py`)

**Dependencies**: transformers, torch, models, data

```python
class ContaminationTrainer:
    def __init__(self, model: nn.Module, train_dataset: Dataset, config: dict): ...
    def train(self) -> dict: ...
    def save_checkpoint(self, epoch: int): ...
    def log_metrics(self, metrics: dict): ...
```

---

### Evaluator (`src/evaluate.py`)

**Dependencies**: detectors, torch, sklearn

```python
class DetectionEvaluator:
    def __init__(self, detector: CombinedDetector): ...
    def evaluate_detection_power(self, models: List[nn.Module], true_labels: List[int]) -> float: ...
    def compute_false_positive_rate(self, clean_models: List[nn.Module]) -> float: ...
    def compute_gsm8k_accuracy(self, model: nn.Module, test_data: Dataset) -> float: ...
    def generate_results_report(self) -> dict: ...
```

---

### Visualizer (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_gate_metrics(detection_power: float, target: float, save_path: str): ...
def plot_per_tier_heatmap(results: dict, save_path: str): ...
def plot_roc_curve(fpr: List[float], tpr: List[float], save_path: str): ...
def plot_accuracy_vs_contamination(results: dict, save_path: str): ...
def plot_geometric_metrics_distribution(metrics: dict, save_path: str): ...
```

---

### Config (`src/config.py`)

**Dependencies**: None

```python
class ExperimentConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    contamination_rates: List[float] = [0.0, 0.01, 0.05]
    n_runs: int = 20
    batch_size: int = 64
    learning_rate: float = 2e-5
    epochs: int = 3
    seed_start: int = 0
    
    tier1_config: dict
    tier2_config: dict
    tier3_config: dict
    
    def to_dict(self) -> dict: ...
    def save_json(self, path: str): ...
```

---

### MainExperiment (`main.py`)

**Dependencies**: all modules

```python
def setup_experiment(config: ExperimentConfig) -> tuple: ...
def run_training_runs(config: ExperimentConfig) -> List[dict]: ...
def run_detection_pipeline(models: List[nn.Module], config: ExperimentConfig) -> dict: ...
def main(): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── loader.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── model.py
│   │   ├── detectors/
│   │   │   ├── __init__.py
│   │   │   ├── tier1.py
│   │   │   ├── tier2.py
│   │   │   ├── tier3.py
│   │   │   └── combined.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── visualize.py
│   │   └── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── results/
│   ├── clean/
│   ├── contam_1pct/
│   └── contam_5pct/
├── figures/
└── checkpoints/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Pipeline Setup | Load datasets, implement EAL paraphrasing, create contaminated mixes | 9 | 3+2+2+2 (module+deps+algo+integ) |
| E-2 | Base Model & Training Infrastructure | Setup Llama-2-7B, implement training loop with logging and checkpointing | 11 | 3+3+2+3 |
| E-3 | Tier 1 Detection Implementation | Temporal isolation + LSH fingerprinting with datasketch | 8 | 2+2+2+2 |
| E-4 | Tier 2 TSG Probes | Generate probe families, track losses, compute differential alignment | 13 | 3+3+4+3 |
| E-5 | Tier 3 Geometric Metrics | Implement 4 geometric metrics (gradient, Hessian, CKA, efficiency) | 16 | 4+4+5+3 |
| E-6 | Combined Detection System | Integrate three tiers with OR logic, threshold calibration | 10 | 2+3+2+3 |
| E-7 | Evaluation & Visualization | Compute detection metrics, generate figures, validation report | 12 | 3+3+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-5], Medium(9-13): [E-1, E-2, E-4, E-6, E-7], Low(4-8): [E-3]

**Total Complexity**: 79 points across 7 Epic tasks

---

## Implementation Notes

### Key Dependencies

```txt
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
datasketch>=1.6.0
hessian-eigenthings>=0.0.1
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
numpy>=1.24.0
```

### Critical Thresholds (From PRD)

- **Tier 2**: Differential alignment Δ > 2σ (clean baseline)
- **Tier 3**: 
  - Gradient overlap > 0.10
  - Hessian concentration > 1.5
  - CKA alignment > 0.15
  - Efficiency Z-score > 2.5
  - Detection: ≥2 of 4 metrics exceed thresholds
- **Combined**: OR logic across all tiers

### Success Gate

- Combined detection power ≥80% for 5% contamination
- False positive rate <5% on clean runs
- At least 2 of 3 tiers show >0% detection power

---

*Generated by Phase 3 Architecture | Hypothesis: h-e1 (EXISTENCE) | Target: 7 Epic tasks, 79 complexity points*
