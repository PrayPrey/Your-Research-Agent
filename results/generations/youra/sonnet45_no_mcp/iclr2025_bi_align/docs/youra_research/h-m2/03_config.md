# Configuration Design Document

**Hypothesis:** h-m2  
**Date:** 2026-04-19  
**Author:** Configuration Agent  
**Version:** 1.0  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m1 actual code  
**Config Files Found**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/h-m1/code/config/experiment_config.py`  
**Pattern Used**: dataclass  

---

## Applied Patterns

Applied: Analysis Pipeline Config Pattern, Statistical Testing Config Pattern

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-m1 Actual Code)

The following configs are inherited from h-m1:

```python
# From: h-m1/code/config/experiment_config.py (ACTUAL CODE)
@dataclass
class ModelConfig:
    encoder_name: str = "roberta-base"
    embedding_dim: int = 256
    num_demographic_groups: int = 60
    hidden_dim: int = 768
    projection_hidden_dim: int = 768
    dropout: float = 0.1
    temperature: float = 0.07
```

**Verified from**: h-m1/code/config/experiment_config.py (actual implementation)

---

## h-m2 Configuration Schema

### Key Differences from h-m1

h-m2 is an ANALYSIS experiment testing correlation between embedding similarity and behavioral concordance:
- **No training** (uses frozen h-m1 embeddings) vs h-m1's training experiment
- **CPU-only** (analysis workload) vs h-m1's GPU training
- **Single seed** (42 for sampling) vs h-m1's 3 seeds (1, 42, 123)
- **ETHICS dataset** (behavioral concordance) vs h-m1's OpinionQA (embedding learning)
- **Correlation metrics** (Pearson r, p-value) vs h-m1's clustering metrics (silhouette)

---

## Configuration Implementation

### File: `code/config/analysis_config.py`

```python
"""
Analysis Configuration for h-m2: Embedding Similarity → Behavioral Concordance
Tests: Does embedding similarity predict behavioral concordance on ETHICS?

Design: Pure analysis - no training, uses frozen h-m1 embeddings
Benchmark: ETHICS (5 categories, ~13K test samples)
Primary Metric: Pearson correlation coefficient
"""

from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class H_M1Config:
    """h-m1 checkpoint and embedding configuration"""
    checkpoint_path: str = "../h-m1/checkpoints/contrastive_seed42/best_model.pt"
    embedding_dim: int = 256
    num_demographic_groups: int = 60
    encoder_name: str = "roberta-base"

@dataclass
class ETHICSConfig:
    """ETHICS dataset configuration"""
    dataset_name: str = "hendrycks/ethics"
    cache_dir: str = "../../.data_cache/datasets/huggingface"
    categories: List[str] = field(default_factory=lambda: [
        'deontology', 'virtue', 'justice', 'utilitarianism', 'commonsense'
    ])
    test_split: str = "test"
    max_seq_length: int = 512

@dataclass
class AnalysisConfig:
    """Similarity and concordance analysis configuration"""
    n_user_pairs: int = 1000
    similarity_threshold_high: float = 0.7
    low_bin_max: float = 0.3
    medium_bin_range: Tuple[float, float] = (0.3, 0.7)
    random_seed: int = 42
    n_bootstrap_samples: int = 1000

@dataclass
class GateConfig:
    """Gate criteria for hypothesis validation"""
    target_correlation: float = 0.5
    target_high_sim_concordance: float = 0.65
    min_baseline_diff: float = 0.10
    significance_level: float = 0.05

@dataclass
class OutputConfig:
    """Output paths configuration"""
    figures_dir: str = "../figures"
    results_file: str = "../outputs/experiment_results.json"
    checkpoint_dir: str = "../checkpoints"

@dataclass
class AnalysisExperimentConfig:
    """Top-level analysis experiment configuration"""
    h_m1: H_M1Config = field(default_factory=H_M1Config)
    ethics: ETHICSConfig = field(default_factory=ETHICSConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    experiment_name: str = "h-m2-similarity-concordance-analysis"
    hypothesis_id: str = "h-m2"
    device: str = "cpu"
```

---

## Per-Task Configuration

### C-1: Embedding & Data Loading [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch checkpoint loading pattern

```python
@dataclass
class LoaderConfig:
    """Configuration for embedding and ETHICS data loading (C-1)"""
    h_m1_checkpoint: str = "../h-m1/checkpoints/contrastive_seed42/best_model.pt"
    ethics_dataset: str = "hendrycks/ethics"
    ethics_cache_dir: str = "../../.data_cache/datasets/huggingface"
    tokenizer_name: str = "roberta-base"
    max_length: int = 512
    verify_checkpoint: bool = True
```

**Subtasks** [8/8 used]:
- C-1-1: h-m1 checkpoint loading (2)
- C-1-2: Embedding extraction (2)
- C-1-3: ETHICS dataset loading (2)
- C-1-4: Data verification (2)

---

### C-2: Response Generation [Complexity: 11, Budget: 11]

**Applied**: Embedding-based inference pattern

```python
@dataclass
class ResponseGeneratorConfig:
    """Configuration for user response generation on ETHICS (C-2)"""
    embedding_dim: int = 256
    batch_size: int = 32
    num_workers: int = 2
    deterministic: bool = True
    seed: int = 42
    
    # Response generation uses embedding similarity to scenario embeddings
    similarity_threshold: float = 0.5
```

**Subtasks** [11/11 used]:
- C-2-1: Model initialization for inference (3)
- C-2-2: Scenario embedding computation (2)
- C-2-3: User response generation (3)
- C-2-4: Response validation (3)

---

### C-3: Similarity Analysis [Complexity: 9, Budget: 9]

**Applied**: Stratified sampling pattern

```python
@dataclass
class SimilarityAnalysisConfig:
    """Configuration for embedding similarity analysis (C-3)"""
    distance_metric: str = "cosine"
    n_user_pairs: int = 1000
    
    # Similarity bins for stratified sampling
    low_bin_max: float = 0.3
    medium_bin_min: float = 0.3
    medium_bin_max: float = 0.7
    high_bin_min: float = 0.7
    
    # Ensure balanced sampling
    pairs_per_bin: int = 333
    seed: int = 42
```

**Subtasks** [9/9 used]:
- C-3-1: Pairwise similarity computation (2)
- C-3-2: Similarity matrix creation (2)
- C-3-3: Stratified sampling (3)
- C-3-4: Bin validation (2)

---

### C-4: Concordance Measurement [Complexity: 10, Budget: 10]

**Applied**: Agreement rate computation pattern

```python
@dataclass
class ConcordanceConfig:
    """Configuration for behavioral concordance measurement (C-4)"""
    n_tasks_per_pair: int = 1000
    n_random_pairs: int = 1000
    
    # Concordance computation
    agreement_metric: str = "exact_match"
    
    # Baseline comparison
    compute_random_baseline: bool = True
    random_seed: int = 42
```

**Subtasks** [10/10 used]:
- C-4-1: Pairwise agreement calculation (3)
- C-4-2: Concordance by bin (2)
- C-4-3: Random baseline concordance (3)
- C-4-4: Category-specific concordance (2)

---

### C-5: Correlation & Statistical Tests [Complexity: 12, Budget: 12]

**Applied**: Statistical testing pattern (scipy)

```python
@dataclass
class CorrelationConfig:
    """Configuration for correlation and statistical testing (C-5)"""
    primary_test: str = "pearson"
    secondary_test: str = "spearman"
    significance_level: float = 0.05
    
    # Bootstrap confidence intervals
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    
    # Gate criteria
    target_correlation: float = 0.5
    target_high_sim_concordance: float = 0.65
    min_baseline_diff: float = 0.10
```

**Subtasks** [12/12 used]:
- C-5-1: Pearson correlation (3)
- C-5-2: Spearman correlation (3)
- C-5-3: Bootstrap confidence intervals (4)
- C-5-4: Gate evaluation (2)

---

### C-6: Visualization & Results [Complexity: 9, Budget: 9]

**Applied**: Standard matplotlib visualization pattern

```python
@dataclass
class VisualizationConfig:
    """Configuration for visualization generation (C-6)"""
    figures_dir: str = "../figures"
    save_format: str = "png"
    dpi: int = 300
    
    # Required gate figure
    gate_figure_name: str = "gate_metrics_comparison.png"
    
    # Additional figures
    correlation_scatter: bool = True
    concordance_by_bin: bool = True
    similarity_heatmap: bool = True
```

**Subtasks** [9/9 used]:
- C-6-1: Gate metrics figure (2)
- C-6-2: Correlation scatter plot (2)
- C-6-3: Concordance by bin plot (3)
- C-6-4: Results export (2)

---

## Hyperparameter Justifications

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_user_pairs` | 1000 | Adequate sample size for detecting r > 0.5 (power analysis) |
| `similarity_threshold_high` | 0.7 | High similarity threshold from hypothesis definition |
| `target_correlation` | 0.5 | Gate criterion from PRD (moderate-strong correlation) |
| `target_high_sim_concordance` | 0.65 | Gate criterion from PRD (meaningful behavioral agreement) |
| `min_baseline_diff` | 0.10 | Effect size threshold (10% improvement over random) |
| `significance_level` | 0.05 | Standard statistical significance threshold |
| `random_seed` | 42 | Fixed seed for reproducible sampling |
| `n_bootstrap` | 1000 | Standard for bootstrap confidence intervals |

---

## Environment Setup

### CPU-Only Execution

```bash
#!/bin/bash
# File: setup_environment.sh

# No GPU needed for analysis
export CUDA_VISIBLE_DEVICES=""

# Reproducibility
export PYTHONHASHSEED=42
```

### Dependencies

```
# requirements.txt
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## Execution Commands

### Full Analysis Pipeline

```bash
# Run analysis (CPU-only, no GPU needed)
python run_analysis.py --config config/analysis_config.py
```

### Individual Components

```bash
# Load embeddings only
python run_analysis.py --stage load_embeddings

# Similarity analysis only
python run_analysis.py --stage similarity_analysis

# Full pipeline with verbose output
python run_analysis.py --verbose
```

---

## Configuration Validation

```python
def validate_h_m2_config(config: AnalysisExperimentConfig) -> None:
    """Validate h-m2 specific configuration"""
    
    # Check h-m1 checkpoint exists
    checkpoint_path = Path(config.h_m1.checkpoint_path)
    assert checkpoint_path.exists(), f"h-m1 checkpoint not found: {checkpoint_path}"
    
    # Check sampling parameters
    assert config.analysis.n_user_pairs == 1000, "Sample size must be 1000 pairs"
    
    # Check gate criteria match PRD
    assert config.gate.target_correlation == 0.5, "Gate: Pearson r > 0.5"
    assert config.gate.target_high_sim_concordance == 0.65, "Gate: High-sim concordance > 0.65"
    assert config.gate.significance_level == 0.05, "Gate: p < 0.05"
    
    # Check ETHICS categories
    expected_categories = ['deontology', 'virtue', 'justice', 'utilitarianism', 'commonsense']
    assert config.ethics.categories == expected_categories, "ETHICS must have all 5 categories"
    
    print("✓ h-m2 configuration validated")
```

---

## Key Differences from Training Configs

| Aspect | h-m1 (Training) | h-m2 (Analysis) |
|--------|-----------------|-----------------|
| Config Focus | Training hyperparameters | Analysis parameters |
| GPU Required | Yes (CUDA) | No (CPU) |
| Seeds | 3 seeds [1, 42, 123] | 1 seed [42] |
| Epochs | 15 | N/A (no training) |
| Learning Rate | 2e-5, 1e-4 | N/A (no training) |
| Batch Size | 64 (training) | 32 (inference) |
| Primary Config | TrainingConfig | AnalysisConfig |
| Gate Metric | Silhouette score | Correlation coefficient |
| Checkpoint | Produces checkpoint | Consumes checkpoint |

---

## Summary

**Configuration Format**: Python dataclasses (copy-paste ready)

**Key Features**:
- Inherited h-m1 checkpoint configuration (verified field names)
- Analysis-specific parameters (correlation, concordance)
- Gate criteria embedded in config
- CPU-only execution (no GPU config needed)
- Single seed for reproducibility

**Total Tasks**: 6 tasks (C-1 to C-6)  
**Complexity Budget**: 59/59 (100%)

---

**Status**: Configuration Design Complete
