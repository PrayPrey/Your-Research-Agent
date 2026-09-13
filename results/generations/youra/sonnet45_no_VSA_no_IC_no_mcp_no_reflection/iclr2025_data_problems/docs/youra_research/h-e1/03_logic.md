# Logic Design
# Hypothesis H-E1: Data Quality Metrics Correlation Study

**Version**: 1.0  
**Created**: 2026-08-28  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing code  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - designing from scratch

---

## Knowledge Base Patterns Applied

Applied: Standard PyTorch data processing pipeline  
Applied: Statistical analysis with scipy patterns

---

## L-1: C4 Subset Sampling [Complexity: 8, Budget: 1]

Applied: HuggingFace datasets streaming pattern

### API Signatures

```python
from typing import List, Dict
from datasets import load_dataset

class C4SubsetSampler:
    def __init__(self, output_dir: str, subset_size_gb: int = 10):
        """Initialize sampler. subset_size_gb: target size in GB."""
        ...
    
    def sample_subset(self, dimension: str, level: str, seed: int = 42) -> str:
        """Sample single subset. Returns: path to JSONL file."""
        # dimension: 'dedup' | 'diversity' | 'perplexity' | 'efficiency'
        # level: 'low' | 'medium' | 'high'
        ...
    
    def generate_all_subsets(self) -> List[str]:
        """Generate all 12 subsets. Returns: list of file paths."""
        ...

def apply_dedup(texts: List[str], ratio: float, ngram_size: int = 13) -> List[str]:
    """Remove duplicates. ratio: 0.0 (none) to 0.95 (aggressive)."""
    ...

def apply_domain_filter(texts: List[str], urls: List[str], diversity: str) -> List[str]:
    """Filter by domain. diversity: 'single' | 'multi' | 'full'."""
    ...

def apply_perplexity_filter(texts: List[str], threshold: str) -> List[str]:
    """Remove high perplexity. threshold: 'none' | 'top30' | 'top60'."""
    ...

def apply_token_cleaning(texts: List[str], level: str) -> List[str]:
    """Clean markup/stopwords. level: 'none' | 'markdown' | 'aggressive'."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Stream and transform | Download C4 stream, apply filters, save JSONL |

---

## L-2: Quality Metrics Computation [Complexity: 9, Budget: 1]

Applied: Batch processing with transformers

### API Signatures

```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

class QualityMetricsComputer:
    def __init__(self, model_name: str = "gpt2", device: str = "cuda"):
        """Load GPT-2 for perplexity."""
        ...
    
    def compute_dedup_ratio(self, texts: List[str], ngram_size: int = 13) -> float:
        """Returns: 1 - (unique_ngrams / total_ngrams)."""
        ...
    
    def compute_domain_diversity(self, urls: List[str]) -> float:
        """HHI-based diversity. Returns: 1 - HHI."""
        ...
    
    def compute_perplexity(self, texts: List[str], batch_size: int = 128) -> float:
        """Batched GPT-2 perplexity. Returns: mean perplexity."""
        ...
    
    def compute_token_efficiency(self, texts: List[str]) -> float:
        """Returns: semantic_tokens / total_tokens."""
        ...
    
    def compute_all(self, subset_path: str) -> Dict[str, float]:
        """Compute all 4 metrics. Returns: {'dedup': ..., 'diversity': ..., ...}"""
        ...
```

### Tensor Shapes

```python
# Perplexity computation
inputs = tokenizer(texts, ...)  # input_ids: [B, L], attention_mask: [B, L]
outputs = model(**inputs, labels=inputs["input_ids"])  # loss: scalar
perplexity = torch.exp(outputs.loss)  # scalar
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Batch metrics | Compute Q(D) components for all 12 subsets |

---

## L-3: Information Density Computation [Complexity: 10, Budget: 1]

Applied: SentenceTransformers embedding pattern

### API Signatures

```python
from sentence_transformers import SentenceTransformer
import numpy as np
import zlib

class InformationDensityComputer:
    def __init__(self, embedder_name: str = "all-MiniLM-L6-v2"):
        """Load sentence embedder."""
        ...
    
    def compute_token_entropy(self, texts: List[str]) -> float:
        """Unigram/bigram/trigram Shannon entropy. Returns: normalized H(X)."""
        ...
    
    def compute_ngram_redundancy(self, texts: List[str]) -> float:
        """LZ77 compression ratio. Returns: 1 - (compressed / original)."""
        ...
    
    def compute_semantic_diversity(self, texts: List[str], sample_size: int = 1000) -> float:
        """Pairwise embedding diversity. Returns: mean(1 - cosine_sim)."""
        ...
    
    def compute_combined_density(self, texts: List[str]) -> float:
        """Aggregate density score. Returns: (entropy + (1-redundancy) + diversity) / 3."""
        ...
```

### Tensor Shapes

```python
# Semantic diversity computation
embeddings = embedder.encode(texts[:sample_size])  # [N, 384] for MiniLM
pairwise_sim = cosine_similarity(embeddings)  # [N, N]
diversity = 1 - pairwise_sim.mean()  # scalar
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Density metrics | Compute entropy, redundancy, semantic diversity for 12 subsets |

---

## L-4: Correlation Analysis [Complexity: 11, Budget: 1]

Applied: scipy.stats correlation patterns

### API Signatures

```python
from scipy.stats import pearsonr, spearmanr
import pandas as pd
import numpy as np

def compute_pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Returns: (r, p_value)."""
    return pearsonr(x, y)

def compute_spearman(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Returns: (rho, p_value)."""
    return spearmanr(x, y)

def correlate_all_components(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Correlate Q(D) components with info_density.
    
    Args:
        metrics_df: DataFrame with columns ['dedup', 'diversity', 'perplexity', 
                    'efficiency', 'info_density'], 12 rows
    
    Returns:
        results_df: columns ['component', 'pearson_r', 'pearson_p', 
                    'spearman_rho', 'spearman_p']
    """
    ...

def save_results(results: pd.DataFrame, path: str):
    """Save correlation results to CSV."""
    ...
```

### Pseudo-code

```
1. Load metrics_results.csv (12 rows × 8 columns)
2. For each Q(D) component:
   - x = metrics_df[component].values  # [12]
   - y = metrics_df['info_density'].values  # [12]
   - r, p = pearsonr(x, y)
   - rho, p_s = spearmanr(x, y)
   - Store in results table
3. Check gate: count components where r > 0.5 and p < 0.01
4. Return PASS (≥4), PARTIAL (≥2), or FAIL (<2)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Statistical tests | Pearson/Spearman correlations, gate decision logic |

---

## Visualization API (Optional - No Budget Allocated)

**Note**: Visualization is low complexity, included in Epic tasks without subtask allocation.

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_scatter(x: np.ndarray, y: np.ndarray, title: str, save_path: str):
    """Scatter plot with regression line. x, y: [N]."""
    ...

def add_regression_line(ax, x: np.ndarray, y: np.ndarray):
    """Add OLS line + 95% CI shading."""
    ...

def generate_all_plots(metrics_df: pd.DataFrame, output_dir: str):
    """Generate 4 scatter PNGs."""
    ...
```

---

## Main Pipeline

```python
def main():
    """Full experiment pipeline."""
    import yaml
    
    # Load config
    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)
    
    # 1. Generate subsets (2 GPU-hours)
    sampler = C4SubsetSampler(output_dir='data/subsets', subset_size_gb=10)
    subset_paths = sampler.generate_all_subsets()
    
    # 2. Compute quality metrics (4 GPU-hours)
    qm_computer = QualityMetricsComputer(model_name='gpt2', device='cuda')
    quality_metrics = [qm_computer.compute_all(path) for path in subset_paths]
    
    # 3. Compute information density (2 GPU-hours)
    id_computer = InformationDensityComputer(embedder_name='all-MiniLM-L6-v2')
    density_scores = [id_computer.compute_combined_density(load_texts(path)) 
                      for path in subset_paths]
    
    # 4. Build metrics DataFrame
    metrics_df = pd.DataFrame(quality_metrics)
    metrics_df['info_density'] = density_scores
    metrics_df.to_csv('results/metrics_results.csv', index=False)
    
    # 5. Correlation analysis (CPU-only)
    correlation_results = correlate_all_components(metrics_df)
    save_results(correlation_results, 'results/correlation_results.csv')
    
    # 6. Visualization
    generate_all_plots(metrics_df, output_dir='results/plots/')
    
    # 7. Gate decision
    passing = (correlation_results['pearson_r'] > 0.5) & (correlation_results['pearson_p'] < 0.01)
    gate = 'PASS' if passing.sum() >= 4 else ('PARTIAL' if passing.sum() >= 2 else 'FAIL')
    print(f"Gate Decision: {gate}")
```

---

## Budget Summary

| Task | Complexity | Budget Used | Remaining |
|------|------------|-------------|-----------|
| L-1: C4 Sampling | 8 | 1 | 3 |
| L-2: Quality Metrics | 9 | 1 | 2 |
| L-3: Info Density | 10 | 1 | 1 |
| L-4: Correlation | 11 | 1 | 0 |
| **Total** | - | **4** | **0** |

---

## Data Structures

```python
# Subset metadata (YAML)
subset_metadata = {
    'c4_dedup_low.jsonl': {
        'dimension': 'dedup',
        'level': 'low',
        'transformations': {'dedup_ratio': 0.0},
        'size_gb': 10.0
    },
    # ... 11 more entries
}

# Metrics results (CSV)
# columns: subset_name, dedup, diversity, perplexity, efficiency, 
#          token_entropy, ngram_redundancy, semantic_diversity, info_density
# 12 rows, one per subset

# Correlation results (CSV)
# columns: component, pearson_r, pearson_p, spearman_rho, spearman_p
# 4 rows (dedup, diversity, perplexity, efficiency)
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count = 4 (within budget)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project status confirmed
- [x] EXISTENCE hypothesis: minimal PoC APIs only

---

**END OF LOGIC DESIGN**
