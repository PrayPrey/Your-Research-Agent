# Logic Specification: h-e1 CCP Domain Degradation Experiment

**Date:** 2026-07-09
**Hypothesis:** ρ_j (claim-type mass ratio) degrades by >0.15 when CCP is applied to creative text vs factual text
**Type:** EXISTENCE (Proof-of-Concept)
**Author:** Logic Agent
**Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** Green-field
**Status:** New implementation - no existing code found
**Analyzed Path:** /workspace/TEST_question/docs/youra_research/h-e1
**Relevant Symbols:** None - new implementation from scratch

---

## Knowledge Base Patterns Applied

**Applied:** PyTorch design philosophy - modular components with clear forward() signatures
**Applied:** Batch processing pattern for efficient NLI inference

---

## A-1: Setup Environment [Complexity: 5, Budget: 2]

### API Signatures

```python
# config.py
from pathlib import Path
from typing import Dict, Any
import torch

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"

CONFIG: Dict[str, Any] = {
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

def setup_environment(seed: int = 42) -> None:
    """Initialize random seeds and create directories."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config setup | Define CONFIG dict, paths, thresholds |
| L-1-2 | Seed initialization | Set random seeds (torch, numpy, python) |

---

## A-2: Dataset Loading [Complexity: 6, Budget: 2]

### API Signatures

```python
# data/loader.py
from datasets import load_dataset
from typing import List, Dict
import nltk

class TruthfulQALoader:
    def __init__(self, cache_dir: str):
        """Initialize TruthfulQA loader."""
        self.cache_dir = cache_dir
    
    def load(self) -> List[Dict[str, str]]:
        """Load and format TruthfulQA dataset.
        
        Returns:
            List of dicts with keys: question, best_answer, context
            Length: 817 samples
        """
        ...

class WritingPromptsLoader:
    def __init__(self, cache_dir: str, sample_size: int = 817, seed: int = 42):
        """Initialize WritingPrompts loader with sampling."""
        self.cache_dir = cache_dir
        self.sample_size = sample_size
        self.seed = seed
    
    def load(self) -> List[Dict[str, str]]:
        """Load and subsample WritingPrompts dataset.
        
        Returns:
            List of dicts with keys: prompt, story, context
            Length: ~817 samples
        """
        ...

def decompose_claims(text: str, method: str = "nltk", max_claims: int = 20) -> List[str]:
    """Decompose text into claims using sentence tokenization.
    
    Args:
        text: Input text
        method: Tokenization method (default: nltk)
        max_claims: Maximum claims to extract
    
    Returns:
        List of claim strings (sentences)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dataset | (817,) | List of dicts |
| claims | variable | List[str] per sample |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Dataset loaders | Implement TruthfulQALoader and WritingPromptsLoader classes |
| L-2-2 | Claim decomposition | Implement decompose_claims() with NLTK tokenization |

---

## A-3: NLI Model Integration [Complexity: 8, Budget: 2]

### API Signatures

```python
# models/nli_inference.py
from sentence_transformers import CrossEncoder
import torch
from typing import List, Tuple
import numpy as np

class NLIModel:
    def __init__(
        self, 
        model_name: str = "cross-encoder/nli-deberta-v3-base", 
        device: str = "cuda",
        max_length: int = 512
    ):
        """Initialize NLI model with CrossEncoder.
        
        Args:
            model_name: HuggingFace model ID
            device: cuda or cpu
            max_length: Max sequence length
        """
        self.model = CrossEncoder(model_name, max_length=max_length, device=device)
        self.device = device
    
    def predict(self, pairs: List[Tuple[str, str]], batch_size: int = 16) -> np.ndarray:
        """Run NLI inference on (context, claim) pairs.
        
        Args:
            pairs: List of (context, claim) tuples
            batch_size: Batch size for inference
        
        Returns:
            scores: (N, 3) array with [contradiction, entailment, neutral] scores
        """
        ...
    
    def clear_cache(self) -> None:
        """Clear CUDA cache to prevent OOM."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| pairs | (N,) | List of (str, str) tuples |
| scores | (N, 3) | [contradiction, entailment, neutral] |

### Pseudo-code

```
1. Initialize CrossEncoder with model_name
2. For each batch of pairs:
   a. Run model.predict(batch) -> (batch_size, 3)
   b. Concatenate to full scores array
3. Return full scores (N, 3)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model initialization | Load CrossEncoder with DeBERTa-v3-base |
| L-3-2 | Batch inference | Implement predict() with batching and OOM handling |

---

## A-4: Metrics Implementation [Complexity: 10, Budget: 2]

### API Signatures

```python
# evaluation/metrics.py
import numpy as np
from scipy.stats import pearsonr, wilcoxon
import krippendorff
from typing import Dict, List, Tuple

def compute_rho_j(nli_scores: np.ndarray) -> float:
    """Compute CCP ρ_j metric for a single sample.
    
    Args:
        nli_scores: (N_claims, 3) array [contradiction, entailment, neutral]
    
    Returns:
        rho_j: median((contradict + entail) / total_mass)
    """
    # contradict_mass + entail_mass = nli_scores[:, 0] + nli_scores[:, 1]
    # total_mass = nli_scores.sum(axis=1)
    # rho_j = np.median((contradict_mass + entail_mass) / total_mass)
    ...

def compute_autocorrelation(scores: np.ndarray, max_lag: int = 10) -> List[float]:
    """Compute autocorrelation for lags 1 to max_lag.
    
    Args:
        scores: (N,) array of CCP scores
        max_lag: Maximum lag
    
    Returns:
        autocorr: List of autocorrelation coefficients
    """
    ...

def compute_krippendorff_alpha(decompositions: List[List[str]]) -> float:
    """Compute claim decomposition reliability.
    
    Args:
        decompositions: List of 2 decompositions for same texts
    
    Returns:
        alpha: Krippendorff's alpha coefficient
    """
    ...

def statistical_test(
    factual_rho: np.ndarray, 
    creative_rho: np.ndarray
) -> Dict[str, float]:
    """Run statistical test for ρ_j degradation.
    
    Args:
        factual_rho: (N,) array of factual domain ρ_j values
        creative_rho: (N,) array of creative domain ρ_j values
    
    Returns:
        {
            "delta_rho_j": float,
            "p_value": float,
            "effect_size": float
        }
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| nli_scores | (N_claims, 3) | Per-claim NLI scores |
| factual_rho | (817,) | Per-sample ρ_j (factual) |
| creative_rho | (817,) | Per-sample ρ_j (creative) |
| autocorr | (max_lag,) | Autocorrelation coefficients |

### Pseudo-code

```
compute_rho_j:
1. claim_masses = nli_scores[:, 0] + nli_scores[:, 1]  # contradict + entail
2. total_masses = nli_scores.sum(axis=1)
3. ratios = claim_masses / total_masses
4. rho_j = np.median(ratios)

statistical_test:
1. delta_rho_j = np.median(creative_rho) - np.median(factual_rho)
2. stat, p_value = wilcoxon(creative_rho, factual_rho)
3. effect_size = delta_rho_j / np.std(factual_rho)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | CCP metrics | Implement compute_rho_j() and autocorrelation |
| L-4-2 | Statistical tests | Implement statistical_test() and Krippendorff's alpha |

---

## A-5: Experiment Pipeline [Complexity: 9, Budget: 2]

### API Signatures

```python
# main/experiment.py
import json
import torch
from pathlib import Path
from typing import Dict, List, Tuple
from tqdm import tqdm
import numpy as np

class CCPExperiment:
    def __init__(self, config: Dict):
        """Initialize experiment with config."""
        self.config = config
        self.factual_loader = None
        self.creative_loader = None
        self.nli_model = None
    
    def run(self) -> Dict:
        """Execute full experiment pipeline.
        
        Pipeline:
        1. Load datasets
        2. Process factual domain
        3. Process creative domain
        4. Compute metrics
        5. Generate visualizations
        6. Save results
        
        Returns:
            results: {
                "rho_j_factual": float,
                "rho_j_creative": float,
                "delta_rho_j": float,
                "autocorr_factual": float,
                "autocorr_creative": float,
                "krippendorff_alpha": float,
                "p_value": float,
                "gate_satisfied": bool
            }
        """
        ...
    
    def process_domain(
        self, 
        samples: List[Dict], 
        domain_name: str
    ) -> Tuple[np.ndarray, List]:
        """Process single domain through NLI pipeline.
        
        Args:
            samples: List of dataset samples
            domain_name: "factual" or "creative"
        
        Returns:
            rho_j_values: (N,) array of per-sample ρ_j
            all_nli_scores: List of NLI score arrays
        """
        ...
    
    def check_gate_criteria(self, results: Dict) -> bool:
        """Validate MUST_WORK gate criteria.
        
        Returns:
            satisfied: True if all criteria met
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| samples | (817,) | List of dicts |
| rho_j_values | (817,) | Per-sample ρ_j |
| all_nli_scores | variable | List of (N_claims, 3) arrays |

### Pseudo-code

```
run():
1. Setup environment (seeds, directories)
2. Load datasets (TruthfulQA, WritingPrompts)
3. Initialize NLI model
4. Process factual domain:
   - For each sample: decompose -> NLI -> compute ρ_j
   - Save intermediate results
5. Process creative domain (same)
6. Compute metrics (autocorr, reliability, statistical test)
7. Generate visualizations
8. Check gate criteria
9. Generate validation report

process_domain():
1. For each sample in domain:
   a. Decompose claims
   b. Create (context, claim) pairs
   c. Run NLI inference
   d. Compute per-sample ρ_j
2. Return array of ρ_j values
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Main pipeline | Implement run() method with full execution flow |
| L-5-2 | Domain processing | Implement process_domain() with NLI inference loop |

---

## A-6: Visualization [Complexity: 7, Budget: 2]

### API Signatures

```python
# visualization/plots.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List

def plot_rho_distribution(
    factual_rho: np.ndarray, 
    creative_rho: np.ndarray, 
    save_path: Path
) -> None:
    """Generate violin plot comparing ρ_j distributions.
    
    Args:
        factual_rho: (N,) array of factual ρ_j values
        creative_rho: (N,) array of creative ρ_j values
        save_path: Output file path
    """
    ...

def plot_nli_heatmap(
    factual_scores: np.ndarray, 
    creative_scores: np.ndarray, 
    save_path: Path
) -> None:
    """Generate heatmap of NLI score distributions.
    
    Args:
        factual_scores: (N_factual, 3) array
        creative_scores: (N_creative, 3) array
        save_path: Output file path
    """
    ...

def plot_autocorrelation(
    factual_autocorr: List[float], 
    creative_autocorr: List[float], 
    save_path: Path
) -> None:
    """Generate line plot comparing autocorrelation.
    
    Args:
        factual_autocorr: List of autocorr coefficients
        creative_autocorr: List of autocorr coefficients
        save_path: Output file path
    """
    ...

def plot_sample_scatter(
    factual_rho: np.ndarray, 
    creative_rho: np.ndarray, 
    save_path: Path
) -> None:
    """Generate scatter plot of per-sample ρ_j values.
    
    Args:
        factual_rho: (N,) array
        creative_rho: (N,) array
        save_path: Output file path
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Distribution plots | Implement violin plot and heatmap |
| L-6-2 | Comparison plots | Implement autocorrelation and scatter plots |

---

## A-7: Validation Report [Complexity: 5, Budget: 2]

### API Signatures

```python
# main/experiment.py (extension)

def generate_validation_report(
    results: Dict, 
    figures_dir: Path, 
    output_path: Path
) -> None:
    """Generate 04_validation.md report.
    
    Args:
        results: Metrics dict from run()
        figures_dir: Path to figures directory
        output_path: Path to save report
    
    Report sections:
    1. Executive Summary
    2. Gate Metrics
    3. Statistical Analysis
    4. Visualizations
    5. Limitations
    6. Recommendations
    """
    ...

def update_verification_state(gate_satisfied: bool, results: Dict) -> None:
    """Update verification_state.yaml with gate results."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Report generation | Implement generate_validation_report() with markdown formatting |
| L-7-2 | State update | Implement update_verification_state() with YAML writing |

---

## Summary

**Total Subtasks:** 14/14 used (7 tasks × 2 subtasks each)
**Budget Status:** Exactly at budget limit
**Complexity Distribution:** VeryHigh(0), High(0), Medium(2), Low(5)

**Phase 4 Ready:** All API signatures, tensor shapes, and pseudo-code provided for implementation.

**Key Design Decisions:**
1. CrossEncoder API for DeBERTa-v3-base NLI inference
2. NumPy arrays for metric computation
3. Matplotlib/Seaborn for visualization
4. Modular pipeline with clear separation of concerns
5. Batch processing with OOM handling for GPU efficiency

**Implementation Notes:**
- Use `sentence_transformers.CrossEncoder` for NLI model
- Use `nltk.sent_tokenize` for claim decomposition
- Use `scipy.stats.wilcoxon` for statistical testing
- Save intermediate results to JSON for debugging
- Generate 4 PNG figures in figures/ directory
- Write validation report to 04_validation.md

**External Dependencies:**
- transformers==4.36.0
- sentence-transformers==2.2.2
- torch==2.1.0
- datasets==2.16.0
- nltk==3.8.1
- numpy==1.24.3
- scipy==1.11.4
- krippendorff==0.6.0
- matplotlib==3.8.2
- seaborn==0.13.0

---

**Logic Status:** ✅ COMPLETED
**Next Phase:** Phase 4 - Implementation (Coding Agent)
