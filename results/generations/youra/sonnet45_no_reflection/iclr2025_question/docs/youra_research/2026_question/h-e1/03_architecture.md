---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
created_at: 2026-05-12
author: architecture-agent
---

# Architecture Design: H-E1 Geometric Uncertainty Correlation

**Applied Patterns**: Minimal EXISTENCE architecture, inference-only pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing code to analyze. Fresh implementation for geometric uncertainty correlation experiment.

---

## Overview

**Hypothesis**: Geometric features (participation ratio, eigenvalue decay, condition number) from Llama-3-8B-Instruct layers 24-31 hidden states correlate with semantic entropy (|ρ| > 0.4) on TruthfulQA questions.

**Architecture Type**: Inference-only correlation analysis (no training)

**Key Components**:
1. Data loading (TruthfulQA)
2. Hidden state extraction (Llama-3-8B-Instruct layers 24-31)
3. Geometric feature computation (PR, α, κ)
4. Semantic entropy computation (K=10 samples, NLI clustering)
5. Correlation analysis (Spearman ρ)

---

## Module Structure

### DataLoader (`data/loader.py`)

**Dependencies**: HuggingFace datasets, transformers

```python
class TruthfulQALoader:
    def __init__(self, split_ratio: float = 0.7, seed: int = 42): ...
    def load_dataset(self) -> Tuple[List[str], List[str]]: ...
    def get_train_questions(self) -> List[str]: ...
    def get_test_questions(self) -> List[str]: ...
```

### HiddenStateExtractor (`models/extractor.py`)

**Dependencies**: transformers, torch

```python
class HiddenStateExtractor:
    def __init__(self, model_name: str, target_layers: List[int], device: str): ...
    def load_model(self) -> None: ...
    def extract_hidden_states(self, questions: List[str], batch_size: int) -> Dict[str, torch.Tensor]: ...
    def get_final_token_states(self, hidden_states: Tuple, input_ids: torch.Tensor) -> List[torch.Tensor]: ...
```

### GeometricFeatures (`metrics/geometric.py`)

**Dependencies**: torch, numpy

```python
class GeometricFeatureComputer:
    def __init__(self, epsilon: float = 1e-12): ...
    def compute_covariance(self, hidden_states: List[torch.Tensor]) -> torch.Tensor: ...
    def compute_eigenvalues(self, cov_matrix: torch.Tensor) -> torch.Tensor: ...
    def compute_participation_ratio(self, eigenvalues: torch.Tensor) -> float: ...
    def compute_eigenvalue_decay(self, eigenvalues: torch.Tensor) -> float: ...
    def compute_condition_number(self, eigenvalues: torch.Tensor) -> float: ...
    def compute_all_features(self, hidden_states: List[torch.Tensor]) -> Dict[str, float]: ...
```

### SemanticEntropy (`metrics/semantic_entropy.py`)

**Dependencies**: transformers, torch, numpy

```python
class SemanticEntropyComputer:
    def __init__(self, model_name: str, nli_model: str, device: str): ...
    def generate_samples(self, questions: List[str], k: int, temperature: float) -> List[List[str]]: ...
    def cluster_generations(self, generations: List[str]) -> List[int]: ...
    def compute_entropy(self, cluster_ids: List[int]) -> float: ...
    def compute_all_entropies(self, questions: List[str], k: int = 10) -> List[float]: ...
```

### CorrelationAnalyzer (`analysis/correlation.py`)

**Dependencies**: scipy, numpy, matplotlib, seaborn

```python
class CorrelationAnalyzer:
    def __init__(self, output_dir: str): ...
    def compute_spearman(self, features: np.ndarray, entropies: np.ndarray) -> Tuple[float, float]: ...
    def bootstrap_ci(self, features: np.ndarray, entropies: np.ndarray, n_resamples: int = 1000) -> Tuple[float, float]: ...
    def plot_scatter(self, features: np.ndarray, entropies: np.ndarray, feature_name: str) -> None: ...
    def plot_distributions(self, features: np.ndarray, entropies: np.ndarray, feature_name: str) -> None: ...
    def plot_correlation_heatmap(self, results: Dict[str, Dict]) -> None: ...
    def generate_report(self, results: Dict[str, Dict]) -> str: ...
```

### MainExperiment (`main.py`)

**Dependencies**: All modules above, argparse, logging

```python
def run_experiment(
    model_name: str,
    nli_model: str,
    target_layers: List[int],
    split_ratio: float,
    k_samples: int,
    temperature: float,
    batch_size: int,
    output_dir: str,
    seed: int
) -> Dict[str, Any]: ...

def evaluate_gate(results: Dict[str, Dict]) -> Tuple[bool, str]: ...

def save_results(results: Dict[str, Any], output_path: str) -> None: ...

if __name__ == "__main__":
    # Parse arguments, run experiment, evaluate gate, save results
    ...
```

### Config (`config.py`)

**Dependencies**: None

```python
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
NLI_MODEL = "microsoft/deberta-v3-base"
TARGET_LAYERS = [24, 25, 26, 27, 28, 29, 30, 31]
SPLIT_RATIO = 0.7
K_SAMPLES = 10
TEMPERATURE = 0.7
BATCH_SIZE = 4
EPSILON = 1e-12
SEED = 42
GATE_THRESHOLD = 0.4
GATE_P_VALUE = 0.001
GATE_CI_LOWER = 0.3
```

---

## File Organization

```
code/
├── config.py                    # Hardcoded configuration
├── main.py                      # Main experiment script
├── data/
│   ├── __init__.py
│   └── loader.py               # TruthfulQA loader
├── models/
│   ├── __init__.py
│   └── extractor.py            # Hidden state extraction
├── metrics/
│   ├── __init__.py
│   ├── geometric.py            # PR, α, κ computation
│   └── semantic_entropy.py     # SE computation
├── analysis/
│   ├── __init__.py
│   └── correlation.py          # Spearman correlation + visualization
└── utils/
    ├── __init__.py
    └── helpers.py              # Numerical stability, device management

outputs/
├── features.csv                # Geometric features per question
├── entropies.csv               # Semantic entropy per question
├── correlation_results.json    # ρ, p-values, CIs
└── figures/
    ├── scatter_pr.png
    ├── scatter_alpha.png
    ├── scatter_kappa.png
    ├── distributions_pr.png
    ├── distributions_alpha.png
    ├── distributions_kappa.png
    └── correlation_heatmap.png
```

---

## Data Flow

1. **Load Data**: TruthfulQA questions → 70/30 split
2. **Extract Hidden States**: Llama-3-8B-Instruct forward pass → layers 24-31 final token
3. **Compute Geometric Features**: Covariance → eigenvalues → PR, α, κ
4. **Compute Semantic Entropy**: K=10 samples → NLI clustering → SE
5. **Correlation Analysis**: Spearman(features, SE) → ρ, p-value, 95% CI
6. **Gate Evaluation**: Check |ρ| > 0.4, p < 0.001, CI excludes 0.3
7. **Generate Report**: Visualizations + 04_validation.md

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup Environment | Install dependencies, verify GPU access, test model loading | 5 | 1+1+2+1 (setup+deps+model+test) |
| A-2 | Data Preparation | Load TruthfulQA, implement 70/30 split, tokenization | 6 | 2+1+2+1 (load+split+tokenize+validate) |
| A-3 | Hidden State Extraction | Implement forward pass with hidden state extraction from layers 24-31 | 9 | 3+2+2+2 (model+extraction+batching+validation) |
| A-4 | Geometric Features | Implement covariance, eigenvalue computation, PR/α/κ metrics | 12 | 4+3+3+2 (covariance+eigenvalues+metrics+stability) |
| A-5 | Semantic Entropy | Implement K=10 sampling, NLI clustering, SE computation | 14 | 4+4+3+3 (generation+nli+clustering+entropy) |
| A-6 | Correlation Analysis | Spearman correlation, bootstrap CI, visualization, gate evaluation | 10 | 3+2+3+2 (correlation+bootstrap+plots+gate) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-4, A-6], Low(4-8): [A-1, A-2]

**Total Complexity**: 56 points (6 tasks)

---

## Implementation Details

### Numerical Stability

**Eigenvalue Computation**:
- Use `torch.linalg.eigvalsh` for symmetric matrices
- float32 precision for covariance/eigenvalue computation
- Add ε=1e-12 to denominators (condition number, participation ratio)

**Covariance Matrix**:
```python
# Stack hidden states: [N*8, 4096]
X = torch.cat(hidden_states, dim=0)
X_centered = X - X.mean(dim=0, keepdim=True)
cov = (X_centered.T @ X_centered) / (X.shape[0] - 1)
```

### Memory Management

**Batch Processing**:
- Batch size: 4 questions (Llama-3-8B-Instruct + DeBERTa on single GPU)
- Clear CUDA cache between batches
- Store features incrementally (CSV append mode)

**Inference Precision**:
- Model loading: float16
- Hidden state storage: float16
- Feature computation: float32

### Reference Implementations

**NerVE Integration** (geometric features):
- Copy participation ratio formula: `(Σλᵢ)² / (Σλᵢ²)`
- Use eigenvalue decay pattern: linear fit on log-spectrum
- Numerical stability patterns from official repo

**Semantic Uncertainty Integration** (SE computation):
- Use DeBERTa-v3-base for NLI clustering
- Sampling: temperature=0.7, nucleus sampling
- Cluster assignment via entailment scores

---

## Success Criteria Mapping

| Gate Criterion | Implementation | Validation |
|----------------|----------------|------------|
| \|ρ\| > 0.4 | `scipy.stats.spearmanr()` on test set (N=245) | Check max(\|ρ_PR\|, \|ρ_α\|, \|ρ_κ\|) > 0.4 |
| p < 0.001 | p-value from Spearman test | Check corresponding p-value |
| 95% CI excludes 0.3 | Bootstrap 1000 resamples | Check CI lower bound > 0.3 or upper < -0.3 |

**Gate Evaluation Logic**:
```python
def evaluate_gate(results):
    for feature in ['pr', 'alpha', 'kappa']:
        rho = abs(results[feature]['rho'])
        p_value = results[feature]['p_value']
        ci_lower, ci_upper = results[feature]['ci_95']
        
        if rho > 0.4 and p_value < 0.001 and (ci_lower > 0.3 or ci_upper < -0.3):
            return True, f"PASS: {feature} achieves gate criteria"
    
    return False, "FAIL: No feature meets gate criteria"
```

---

## Visualization Requirements

**Mandatory Figure** (Gate Metrics):
- Bar chart: Spearman |ρ| for PR, α, κ with threshold line at 0.4

**Additional Figures**:
1. Scatter plots: Each feature vs SE (3 plots)
2. Distribution plots: Feature distributions for high/low SE questions (3 plots)
3. Correlation heatmap: All features vs SE
4. Bootstrap CI plot: ρ with 95% confidence intervals

**Output Location**: `outputs/figures/`

---

## Dependencies

### Python Packages

```txt
torch>=2.0.0
transformers>=4.36.0
datasets>=2.14.0
scipy>=1.11.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Pre-trained Models

- `meta-llama/Meta-Llama-3-8B-Instruct` (HuggingFace)
- `microsoft/deberta-v3-base` (HuggingFace)
- `truthful_qa/generation` (HuggingFace datasets)

### Hardware

- Single GPU (A100 40GB or V100 32GB)
- ~20GB GPU memory for inference
- ~4 hours runtime for full dataset

---

## Risk Mitigations

**Risk 1: GPU OOM**
- Mitigation: Reduce batch size to 2, use gradient checkpointing if needed
- Fallback: Process questions sequentially (batch_size=1)

**Risk 2: Numerical Instability**
- Mitigation: float32 precision, epsilon handling, symmetric eigenvalue solver
- Detection: Check for NaN/Inf in features before correlation

**Risk 3: SE Computation Errors**
- Mitigation: Validate generations (non-empty, decodable)
- Fallback: Skip degenerate cases (all identical generations)

**Risk 4: Low Correlation (Gate FAIL)**
- Mitigation: None (fundamental hypothesis test)
- Outcome: Document results, abandon hypothesis per MUST_WORK gate

---

## Task Dependencies

```
A-1 (Setup) → A-2 (Data) → A-3 (Hidden States) → A-4 (Geometric Features)
                          ↘ A-5 (Semantic Entropy) ↗
                                                   ↓
                                              A-6 (Correlation Analysis)
```

**Critical Path**: A-1 → A-2 → A-3 → A-4 → A-6 (geometric features pipeline)
**Parallel Path**: A-1 → A-2 → A-5 → A-6 (semantic entropy pipeline)

**Execution Strategy**: Implement A-3/A-5 in parallel after A-2, then merge at A-6.

---

*Generated by architecture-agent*
*Date: 2026-05-12*
*Next: Phase 4 - Implementation (03_tasks.yaml generation)*
