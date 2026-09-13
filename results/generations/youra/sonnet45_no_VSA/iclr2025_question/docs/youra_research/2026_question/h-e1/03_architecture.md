# System Architecture: h-e1 CCP Domain Degradation Experiment

**Date:** 2026-07-09
**Hypothesis:** ρ_j (claim-type mass ratio) degrades by >0.15 when CCP is applied to creative text vs factual text
**Type:** EXISTENCE (Proof-of-Concept)
**Author:** Architecture Agent

Applied: Standard PoC experiment pattern (minimal modules, baseline + proposed comparison)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** This h-e1 hypothesis folder will contain new CCP domain degradation experiment code. Previous h-e1 code in `/code/h-e1/` implements a different hypothesis (KLE vs SE) and is not reused.

---

## System Overview

Minimal PoC architecture for measuring CCP ρ_j metric degradation across factual (TruthfulQA) and creative (WritingPrompts) domains.

**Core Pipeline:**
1. Load datasets → 2. Decompose claims → 3. Run NLI inference → 4. Compute ρ_j → 5. Statistical analysis → 6. Generate report

**Modules:**
- `data_loader.py` - Dataset loading and preprocessing
- `nli_inference.py` - DeBERTa NLI model wrapper
- `metrics.py` - ρ_j computation and secondary metrics
- `visualization.py` - Figure generation
- `experiment.py` - Main pipeline orchestrator
- `config.py` - Configuration and paths

---

## Module Specifications

### DataLoader (`data/loader.py`)

**Dependencies:** None (uses HuggingFace datasets directly)

```python
from datasets import load_dataset
from typing import List, Dict

class TruthfulQALoader:
    def __init__(self, cache_dir: str):
        ...
    
    def load(self) -> List[Dict[str, str]]:
        """Returns: [{"question": str, "best_answer": str, "context": str}, ...]"""
        ...

class WritingPromptsLoader:
    def __init__(self, cache_dir: str, sample_size: int, seed: int):
        ...
    
    def load(self) -> List[Dict[str, str]]:
        """Returns: [{"prompt": str, "story": str, "context": str}, ...]"""
        ...

def decompose_claims(text: str, method: str = "nltk") -> List[str]:
    """Tokenize text into claims (sentences)."""
    ...
```

---

### NLIInference (`models/nli_inference.py`)

**Dependencies:** DataLoader (for claim decomposition)

```python
from sentence_transformers import CrossEncoder
import torch
from typing import List, Tuple
import numpy as np

class NLIModel:
    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base", device: str = "cuda"):
        ...
    
    def predict(self, pairs: List[Tuple[str, str]], batch_size: int = 16) -> np.ndarray:
        """
        Args:
            pairs: [(context, claim), ...]
        Returns:
            scores: (N, 3) array [contradiction, entailment, neutral]
        """
        ...
    
    def clear_cache(self):
        """Clear CUDA cache to prevent OOM."""
        ...
```

---

### Metrics (`evaluation/metrics.py`)

**Dependencies:** NLIInference

```python
import numpy as np
from scipy.stats import pearsonr, wilcoxon
import krippendorff
from typing import Dict, List, Tuple

def compute_rho_j(nli_scores: np.ndarray) -> float:
    """
    Args:
        nli_scores: (N_claims, 3) array [contradiction, entailment, neutral]
    Returns:
        rho_j: median((contradict + entail) / total_mass)
    """
    ...

def compute_autocorrelation(scores: np.ndarray, max_lag: int = 10) -> List[float]:
    """Lag-1 to lag-N autocorrelation of CCP scores."""
    ...

def compute_krippendorff_alpha(decompositions: List[List[str]]) -> float:
    """Claim decomposition reliability."""
    ...

def statistical_test(factual_rho: np.ndarray, creative_rho: np.ndarray) -> Dict[str, float]:
    """
    Returns:
        {"delta_rho_j": float, "p_value": float, "effect_size": float}
    """
    ...
```

---

### Visualization (`visualization/plots.py`)

**Dependencies:** Metrics

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def plot_rho_distribution(factual_rho: np.ndarray, creative_rho: np.ndarray, save_path: Path):
    """Violin plot comparing ρ_j distributions."""
    ...

def plot_nli_heatmap(factual_scores: np.ndarray, creative_scores: np.ndarray, save_path: Path):
    """Heatmap of NLI score distributions."""
    ...

def plot_autocorrelation(factual_autocorr: List[float], creative_autocorr: List[float], save_path: Path):
    """Line plot comparing autocorrelation."""
    ...

def plot_sample_scatter(factual_rho: np.ndarray, creative_rho: np.ndarray, save_path: Path):
    """Scatter plot of per-sample ρ_j values."""
    ...
```

---

### Experiment (`main/experiment.py`)

**Dependencies:** DataLoader, NLIInference, Metrics, Visualization

```python
import json
import torch
from pathlib import Path
from typing import Dict
from tqdm import tqdm

class CCPExperiment:
    def __init__(self, config: Dict):
        ...
    
    def run(self) -> Dict:
        """
        Pipeline:
        1. Load datasets
        2. Process factual domain
        3. Process creative domain
        4. Compute metrics
        5. Generate visualizations
        6. Save results
        
        Returns:
            results: {"rho_j_factual": float, "rho_j_creative": float, "delta_rho_j": float, ...}
        """
        ...
    
    def process_domain(self, samples: List[Dict], domain_name: str) -> Tuple[np.ndarray, List]:
        """Process single domain through NLI pipeline."""
        ...
    
    def check_gate_criteria(self, results: Dict) -> bool:
        """Validate MUST_WORK gate criteria."""
        ...
```

---

### Config (`config.py`)

**Dependencies:** None

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

for d in [CACHE_DIR, RESULTS_DIR, FIGURES_DIR]:
    d.mkdir(exist_ok=True)

CONFIG = {
    "random_seed": 42,
    "dataset": {
        "truthfulqa": {"name": "truthfulqa/truthful_qa", "subset": "generation"},
        "writingprompts": {"name": "euclaise/writingprompts", "sample_size": 817},
        "cache_dir": str(CACHE_DIR / "datasets")
    },
    "nli_model": {
        "name": "cross-encoder/nli-deberta-v3-base",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "batch_size": 16,
        "max_length": 512
    },
    "claim_decomposition": {
        "method": "nltk",
        "max_claims": 20
    },
    "output": {
        "intermediate": str(RESULTS_DIR / "sample_rho_j.json"),
        "metrics": str(RESULTS_DIR / "metrics_summary.json"),
        "validation_report": str(BASE_DIR.parent / "04_validation.md")
    },
    "gate_thresholds": {
        "delta_rho_j": 0.15,
        "autocorr_creative": 0.4,
        "autocorr_factual": 0.2,
        "krippendorff_alpha": 0.7
    }
}
```

---

## File Structure

```
docs/youra_research/h-e1/
├── code/
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── nli_inference.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── metrics.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py
│   ├── main/
│   │   ├── __init__.py
│   │   └── experiment.py
│   ├── config.py
│   ├── run.py
│   └── requirements.txt
├── cache/
│   ├── datasets/
│   └── models/
├── results/
│   ├── sample_rho_j.json
│   └── metrics_summary.json
├── figures/
│   ├── rho_j_distribution.png
│   ├── nli_distribution_heatmap.png
│   ├── autocorrelation_comparison.png
│   └── sample_rho_j_scatter.png
└── 04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup Environment | Project structure, dependencies, config | 5 | Module(2) + Deps(1) + Algo(1) + Integ(1) |
| A-2 | Dataset Loading | Implement TruthfulQA and WritingPrompts loaders | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |
| A-3 | NLI Model Integration | DeBERTa model wrapper with batching | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-4 | Metrics Implementation | ρ_j, autocorrelation, reliability | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Experiment Pipeline | Main orchestration and processing | 9 | Module(3) + Deps(2) + Algo(2) + Integ(2) |
| A-6 | Visualization | Four required plots | 7 | Module(2) + Deps(2) + Algo(2) + Integ(1) |
| A-7 | Validation Report | Gate check and report generation | 5 | Module(2) + Deps(1) + Algo(1) + Integ(1) |

**Total Complexity:** 50
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5], Low(4-8): [A-1, A-2, A-3, A-6, A-7]

---

## Data Flow

```
TruthfulQA (817) ──┐
                    ├──> Claim Decomposition ──> NLI Pairs ──> DeBERTa ──> ρ_j(factual)
WritingPrompts(817)─┘                                                   └─> ρ_j(creative)
                                                                             │
                                                                             v
                                                                        Δρ_j = creative - factual
                                                                             │
                                                                             v
                                                                        Statistical Test
                                                                             │
                                                                             v
                                                                        Gate Decision
```

---

## Design Decisions

**Minimal PoC Scope:**
- Single NLI model (no ablation)
- Fixed hyperparameters (no tuning)
- Standard metric computation (no optimization)

**Pre-trained Only:**
- DeBERTa-v3-base frozen weights
- No fine-tuning required
- Reduces complexity from 65+ to 50

**Batch Processing:**
- NLI inference in batches of 16
- Dynamic batch reduction on OOM
- Prevents memory issues

---

## Dependencies

**Core:**
```
transformers==4.36.0
sentence-transformers==2.2.2
torch==2.1.0
datasets==2.16.0
```

**Processing:**
```
nltk==3.8.1
numpy==1.24.3
scipy==1.11.4
krippendorff==0.6.0
```

**Visualization:**
```
matplotlib==3.8.2
seaborn==0.13.0
```

**Utilities:**
```
pyyaml==6.0.1
tqdm==4.66.1
```

---

## Execution Flow

1. **Initialization** (config.py)
   - Set random seeds
   - Create directories
   - Load configuration

2. **Data Loading** (data/loader.py)
   - Load TruthfulQA validation (817 samples)
   - Load WritingPrompts (subsample 817)
   - Log dataset statistics

3. **NLI Setup** (models/nli_inference.py)
   - Load DeBERTa-v3-base
   - Configure batch processing
   - Pre-flight GPU check

4. **Domain Processing** (main/experiment.py)
   - For each domain:
     - Decompose claims (NLTK)
     - Create (context, claim) pairs
     - Run NLI inference
     - Compute per-sample ρ_j
     - Save intermediate results

5. **Metric Computation** (evaluation/metrics.py)
   - Aggregate domain ρ_j
   - Compute Δρ_j
   - Calculate autocorrelation
   - Measure reliability (α)
   - Statistical tests

6. **Visualization** (visualization/plots.py)
   - Generate 4 required figures
   - Save to figures/

7. **Validation** (main/experiment.py)
   - Check gate criteria
   - Generate 04_validation.md
   - Update verification_state.yaml

---

## Error Handling

**GPU Memory:**
- Start batch_size=16
- Reduce to 8 on OOM
- Clear cache between domains

**Missing Data:**
- Log and skip null entries
- Don't crash pipeline
- Report skipped count

**NLI Failures:**
- Retry 3 times
- Log failed samples
- Continue with remaining

---

## Reproducibility

**Fixed Seeds:**
- Python: 42
- NumPy: 42
- PyTorch: 42

**Deterministic:**
```python
torch.use_deterministic_algorithms(True)
torch.backends.cudnn.deterministic = True
```

**Versioning:**
- All dependencies pinned
- Save experiment config to YAML
- Log hardware specs

---

## Success Criteria (MUST_WORK Gate)

1. ✅ Code executes without errors
2. ✅ ρ_j(creative) > ρ_j(factual)
3. ✅ Δρ_j > 0.15
4. ✅ Lag-1 autocorr(creative) > 0.4
5. ✅ Lag-1 autocorr(factual) < 0.2
6. ✅ Krippendorff's α > 0.7

---

**Architecture Status:** ✅ COMPLETED
**Next Phase:** Phase 4 - Implementation
**Estimated LOC:** ~800 lines (excluding dependencies)
