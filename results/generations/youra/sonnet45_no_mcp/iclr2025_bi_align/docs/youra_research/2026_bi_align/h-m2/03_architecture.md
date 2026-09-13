# System Architecture
# Hypothesis: h-m2 - Embedding Space Clustering Analysis

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m2  
**Hypothesis Type:** MECHANISM (Step 2)  
**Architecture Type:** Embedding Analysis with Statistical Testing

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-m1 base code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/h-m1/code/`

**Findings:** h-m1 implements annotation study with data loading, sampling, analysis, and visualization modules. h-m2 adapts data loading infrastructure and extends with embedding extraction, PCA dimensionality reduction, and MANOVA statistical analysis.

**Applied:** KB-Pattern-EmbeddingAnalysis, KB-Pattern-StatisticalTesting

---

## 1. System Overview

### 1.1 Architecture Pattern
**Pattern:** Embedding Extraction → Statistical Analysis → Visualization  
**Components:** Data Loading → Embedding Extraction → PCA Reduction → MANOVA Testing → Visualization

### 1.2 Design Principles
- **Reuse:** Extend h-m1 data loading infrastructure
- **No Training:** Pretrained RoBERTa-base (frozen weights)
- **Statistical Focus:** MANOVA effect size as primary metric
- **Reproducibility:** Fixed seeds, deterministic computation

---

## 2. Module Structure

### Module 1: Data Loading (`src/data/`)

**Dependencies:** HuggingFace datasets

```python
def load_hh_rlhf_harmless(
    dataset_name: str = "Anthropic/hh-rlhf",
    split: str = "train",
    cache_dir: str = None
) -> Dataset:
    """
    Load HH-RLHF harmless subset.
    
    Returns:
        Dataset with fields: prompt, chosen, rejected
    """
    ...

def extract_response_pairs(
    dataset: Dataset,
    max_samples: int = None
) -> Tuple[List[str], List[str]]:
    """
    Extract chosen and rejected response texts.
    
    Returns:
        (chosen_texts, rejected_texts)
    """
    ...
```

### Module 2: Embedding Extraction (`src/embeddings/`)

**Dependencies:** transformers, torch

```python
class RoBERTaEmbeddingExtractor:
    def __init__(self, model_name: str = "roberta-base", device: str = "cuda"):
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = RobertaModel.from_pretrained(model_name)
        self.model.eval()
        self.device = device
        ...
    
    def extract_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        max_length: int = 512
    ) -> np.ndarray:
        """
        Extract CLS embeddings in batches.
        
        Returns:
            (N, 768) embedding matrix
        """
        ...
    
    def extract_embeddings(
        self,
        chosen_texts: List[str],
        rejected_texts: List[str],
        batch_size: int = 32
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract embeddings for both groups.
        
        Returns:
            (chosen_embeddings, rejected_embeddings)
        """
        ...
```

### Module 3: Dimensionality Reduction (`src/analysis/`)

**Dependencies:** scikit-learn

```python
def apply_pca(
    embeddings: np.ndarray,
    n_components: int = 2
) -> Tuple[np.ndarray, PCA]:
    """
    Apply PCA for dimensionality reduction.
    
    Returns:
        (reduced_embeddings, pca_model)
    """
    ...

def compute_variance_explained(
    pca_model: PCA,
    n_components: int = 50
) -> np.ndarray:
    """
    Compute cumulative variance explained.
    
    Returns:
        Cumulative variance array
    """
    ...
```

### Module 4: Statistical Analysis (`src/analysis/`)

**Dependencies:** numpy, scipy

```python
def compute_cohens_d(
    group1: np.ndarray,
    group2: np.ndarray
) -> float:
    """
    Compute Cohen's d effect size.
    
    Formula: (mean1 - mean2) / pooled_std
    
    Returns:
        Effect size d
    """
    ...

def compute_manova_effect_size(
    chosen_embeddings: np.ndarray,
    rejected_embeddings: np.ndarray
) -> Dict[str, float]:
    """
    Compute multivariate effect size.
    
    Returns:
        {
            'cohens_d': float,
            'mean_separation': float,
            'f_statistic': float,
            'p_value': float
        }
    """
    ...

def baseline_random_separation(
    embeddings: np.ndarray,
    n_trials: int = 100,
    seed: int = 42
) -> List[float]:
    """
    Compute baseline effect sizes with random labels.
    
    Returns:
        List of random effect sizes
    """
    ...
```

### Module 5: Visualization (`src/visualization/`)

**Dependencies:** matplotlib, seaborn

```python
def plot_gate_metrics_comparison(
    cohens_d: float,
    baseline_d: float,
    threshold: float,
    output_path: str
) -> None:
    """
    Bar chart: Baseline vs RoBERTa embeddings Cohen's d.
    """
    ...

def plot_pca_scatter(
    chosen_2d: np.ndarray,
    rejected_2d: np.ndarray,
    variance_explained: Tuple[float, float],
    output_path: str
) -> None:
    """
    2D scatter plot of PCA projection.
    """
    ...

def plot_effect_size_distribution(
    per_dimension_d: np.ndarray,
    output_path: str
) -> None:
    """
    Histogram of Cohen's d across embedding dimensions.
    """
    ...

def plot_variance_explained(
    cumulative_variance: np.ndarray,
    output_path: str
) -> None:
    """
    PCA scree plot showing cumulative variance.
    """
    ...

def plot_distance_heatmap(
    chosen_sample: np.ndarray,
    rejected_sample: np.ndarray,
    output_path: str
) -> None:
    """
    Distance matrix heatmap for sample pairs.
    """
    ...
```

### Module 6: Experiment Runner (`src/`)

**Dependencies:** All modules

```python
def run_h_m2_experiment(config: Dict) -> Dict:
    """
    Main experiment orchestration:
    1. Load HH-RLHF harmless subset
    2. Extract RoBERTa embeddings (chosen + rejected)
    3. Save embeddings to disk (checkpoint)
    4. Apply PCA for visualization
    5. Compute MANOVA effect size
    6. Compute random baseline
    7. Generate visualizations
    8. Return gate decision
    """
    ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_hh_rlhf_dataset | `from src.data.loader import load_hh_rlhf_dataset` | `h-m1/code/src/data/loader.py` |

**Verified from:** h-m1/code/ (actual implementation)

**Reuse Strategy:** Adapt h-m1 data loader for full 160K dataset (no sampling needed)

---

## 4. File Organization

```
h-m2/
├── code/
│   ├── src/
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── loader.py              # Dataset loading (adapted from h-m1)
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   └── extractor.py           # RoBERTa embedding extraction NEW
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── pca.py                 # PCA dimensionality reduction NEW
│   │   │   └── manova.py              # Statistical analysis NEW
│   │   ├── visualization/
│   │   │   ├── __init__.py
│   │   │   └── plots.py               # 5 required figures NEW
│   │   ├── main.py                    # Experiment runner
│   │   └── config.yaml                # Configuration
│   ├── data/
│   │   ├── chosen_embeddings.npy      # Saved embeddings (N, 768)
│   │   ├── rejected_embeddings.npy    # Saved embeddings (N, 768)
│   │   └── pca_2d_projection.npy      # PCA projections
│   ├── outputs/
│   │   ├── figures/
│   │   │   ├── gate_metrics.png
│   │   │   ├── pca_scatter.png
│   │   │   ├── effect_size_distribution.png
│   │   │   ├── variance_explained.png
│   │   │   └── distance_heatmap.png
│   │   ├── results.json
│   │   └── report.md
│   ├── tests/
│   │   ├── test_embeddings.py
│   │   ├── test_manova.py
│   │   └── test_pca.py
│   ├── requirements.txt
│   └── README.md
```

---

## 5. Epic Tasks with Complexity Scores

### Epic E-1: Data Loading and Preprocessing
**ID:** E-1  
**Module:** data  
**Complexity Score:** 7/20  
**Breakdown:**
- Module Size: 1 file, ~100 LOC → 2/5
- Dependencies: HuggingFace datasets (reused from h-m1) → 1/5
- Algorithm: Full dataset loading, text extraction → 2/5
- Integration: Interfaces with embedding extractor → 2/5

**Description:** Load full HH-RLHF harmless subset (160K+ pairs) and extract chosen/rejected text pairs.

**Acceptance Criteria:**
- Load complete HH-RLHF dataset from HuggingFace
- Extract text from chosen and rejected response fields
- Validate no missing data
- Return lists of chosen_texts, rejected_texts
- Reproducible with seed=42

---

### Epic E-2: RoBERTa Embedding Extraction
**ID:** E-2  
**Module:** embeddings  
**Complexity Score:** 12/20  
**Breakdown:**
- Module Size: 1 file, ~200 LOC → 3/5
- Dependencies: transformers, torch, GPU management → 3/5
- Algorithm: Batch processing with CLS pooling → 3/5
- Integration: Checkpoint saving, memory management → 3/5

**Description:** Extract 768-dimensional CLS token embeddings using pretrained RoBERTa-base for all 160K+ chosen/rejected pairs.

**Acceptance Criteria:**
- Load RoBERTa-base from HuggingFace
- Batch processing with batch_size=32
- CLS token embedding extraction (first token of last hidden state)
- GPU memory efficient (≤4GB)
- Save embeddings to .npy files
- Progress tracking for long computation
- Reproducible with fixed seed

---

### Epic E-3: PCA Dimensionality Reduction
**ID:** E-3  
**Module:** analysis  
**Complexity Score:** 8/20  
**Breakdown:**
- Module Size: 1 file, ~120 LOC → 2/5
- Dependencies: scikit-learn → 1/5
- Algorithm: PCA transformation, variance calculation → 3/5
- Integration: Processes saved embeddings → 2/5

**Description:** Apply PCA to reduce 768D embeddings to 2D for visualization and compute variance explained statistics.

**Acceptance Criteria:**
- Load saved embeddings from .npy files
- Apply PCA for 2D projection
- Compute variance explained by first 2 PCs
- Generate cumulative variance plot data (first 50 PCs)
- Save PCA projections to disk
- Report % variance explained

---

### Epic E-4: MANOVA Statistical Analysis
**ID:** E-4  
**Module:** analysis  
**Complexity Score:** 10/20  
**Breakdown:**
- Module Size: 1 file, ~150 LOC → 3/5
- Dependencies: numpy, scipy.stats → 1/5
- Algorithm: Cohen's d, MANOVA F-test, random baseline → 4/5
- Integration: Processes embeddings, generates statistics → 2/5

**Description:** Compute MANOVA effect size (Cohen's d) for chosen vs rejected group separation and compare against random baseline.

**Acceptance Criteria:**
- Compute multivariate Cohen's d
- Calculate F-statistic and p-value
- Per-dimension Cohen's d distribution
- Random baseline with 100 trials (random label assignment)
- Confidence intervals for effect size
- Gate decision: d ≥ 0.5 (PASS), d < 0.3 (FAIL)

---

### Epic E-5: Gate Metrics Visualization
**ID:** E-5  
**Module:** visualization  
**Complexity Score:** 6/20  
**Breakdown:**
- Module Size: Part of plots.py, ~40 LOC → 1/5
- Dependencies: matplotlib → 1/5
- Algorithm: Bar chart with threshold line → 2/5
- Integration: Reads MANOVA results → 2/5

**Description:** Generate mandatory gate metrics comparison bar chart showing Cohen's d for random baseline vs RoBERTa embeddings.

**Acceptance Criteria:**
- X-axis: Method (Random Baseline, RoBERTa Embeddings)
- Y-axis: Cohen's d effect size
- Threshold line at d = 0.5 (gate condition)
- Actual values displayed on bars
- Save to outputs/figures/gate_metrics.png

---

### Epic E-6: Additional Visualizations
**ID:** E-6  
**Module:** visualization  
**Complexity Score:** 9/20  
**Breakdown:**
- Module Size: Part of plots.py, ~160 LOC → 3/5
- Dependencies: matplotlib, seaborn → 1/5
- Algorithm: 4 distinct plot types → 3/5
- Integration: Reads embeddings, PCA, MANOVA results → 2/5

**Description:** Generate 4 additional figures: PCA scatter, effect size distribution, variance explained, distance heatmap.

**Acceptance Criteria:**
- PCA 2D scatter: chosen (blue) vs rejected (red)
- Effect size histogram: per-dimension Cohen's d
- Cumulative variance plot: scree plot for first 50 PCs
- Distance heatmap: Euclidean distances for sample pairs
- All saved to outputs/figures/

---

### Epic E-7: Experiment Orchestration
**ID:** E-7  
**Module:** main  
**Complexity Score:** 10/20  
**Breakdown:**
- Module Size: 1 file, ~180 LOC → 3/5
- Dependencies: All modules (E-1 through E-6) → 4/5
- Algorithm: Sequential pipeline with checkpointing → 2/5
- Integration: Coordinates all modules, error handling → 1/5

**Description:** Main experiment runner orchestrating full pipeline from data loading through final report generation.

**Acceptance Criteria:**
- Sequential execution: load → extract → save → analyze → visualize
- Config-driven execution (YAML)
- Checkpoint management (resume from saved embeddings)
- Progress reporting for long operations
- Generates final report.md with results
- Returns gate decision (PASS/FAIL)
- Estimated runtime: 2-3 hours for full dataset

---

## 6. Task Budget Summary

**Hypothesis Type:** MECHANISM  
**Total Epic Tasks:** 7  
**Complexity Distribution:**
- High (10-12): 3 tasks [E-2, E-4, E-7]
- Medium (7-9): 3 tasks [E-1, E-3, E-6]
- Low (6): 1 task [E-5]

**Total Complexity:** 62/140 (7 tasks × 20 max)

---

## 7. Data Flow

```
HH-RLHF Dataset (160K+ pairs)
    ↓
Data Loader (E-1) → chosen_texts, rejected_texts
    ↓
RoBERTa Embedding Extractor (E-2) → chosen_embeddings.npy (N×768), rejected_embeddings.npy (N×768)
    ↓
    ├→ PCA Reduction (E-3) → pca_2d_projection.npy
    │   └→ Variance analysis → cumulative_variance
    │
    └→ MANOVA Analysis (E-4)
        ├→ Cohen's d (proposed)
        ├→ Random baseline Cohen's d
        └→ Gate decision (d ≥ 0.5?)
    ↓
Visualization (E-5, E-6) → 5 figures
    ↓
Experiment Runner (E-7) → report.md, results.json
```

---

## 8. Integration Points

### 8.1 Reused from h-m1
- `src.data.loader.load_hh_rlhf_dataset` - HuggingFace dataset loading

### 8.2 New Components
- `src.embeddings.extractor.RoBERTaEmbeddingExtractor` - Embedding extraction
- `src.analysis.pca.apply_pca` - Dimensionality reduction
- `src.analysis.manova.compute_manova_effect_size` - Statistical testing
- `src.visualization.plots.*` - All visualization functions

### 8.3 External Dependencies
- HuggingFace `transformers` library (RoBERTa-base)
- HuggingFace `datasets` library (HH-RLHF)
- PyTorch for GPU acceleration
- scikit-learn for PCA
- scipy for statistical tests

---

## 9. Mechanism Validation

### Pre-conditions
1. **Mechanism Exists:** Semantic clustering in pretrained embeddings
2. **Baseline Measurable:** Random label assignment (Cohen's d ≈ 0.0)
3. **Improvement Target:** Cohen's d ≥ 0.5 (medium-to-large effect)

### Activation Indicators
- **Embedding Space Structure:** PCA visualization shows distinct clusters
- **Statistical Separation:** MANOVA effect size exceeds random baseline
- **Expected Delta:** d ≥ 0.5 (vs random d ≈ 0.0)

### Success Criteria
- **Primary Gate:** Cohen's d ≥ 0.5 (MANOVA effect size)
- **Secondary:** Visual clustering in PCA 2D projection
- **Baseline Comparison:** d > 0.3 (exceeds random distribution)

### Failure Detection
- **No Structure:** d < 0.3 → random-like, no clustering
- **Weak Effect:** 0.3 ≤ d < 0.5 → marginal structure, EXPLORE alternatives
- **Gate Fail:** d < 0.5 → consider alternative encoders or ABANDON geometric framing

---

## 10. Configuration Management

```yaml
experiment:
  name: "h-m2-embedding-clustering"
  hypothesis_id: "h-m2"
  seed: 42

dataset:
  name: "Anthropic/hh-rlhf"
  split: "train"
  max_samples: null  # Use full dataset (~160K)

embedding:
  model_name: "roberta-base"
  batch_size: 32
  max_length: 512
  device: "cuda"

pca:
  n_components_viz: 2
  n_components_variance: 50

manova:
  baseline_trials: 100

gates:
  primary_threshold: 0.5  # Cohen's d
  secondary_threshold: 0.3  # Random baseline

outputs:
  data_dir: "data/"
  figures_dir: "outputs/figures/"
  results_file: "outputs/results.json"
  report_file: "outputs/report.md"
```

---

## 11. Computational Requirements

### Hardware
- **GPU:** Single NVIDIA GPU with ≥4GB VRAM (Tesla T4, RTX 3060, or better)
- **RAM:** ≥16GB system memory
- **Storage:** ≥10GB free space (dataset + embeddings)

### Runtime Estimates
- Dataset loading: ~5 minutes
- Embedding extraction: ~2-3 hours (160K samples, batch_size=32)
- PCA reduction: ~2 minutes
- Statistical analysis: ~5 minutes
- Visualization: ~1 minute
- **Total:** ~2-3 hours

### GPU Usage
```bash
# Select empty GPU before running
nvidia-smi
export CUDA_VISIBLE_DEVICES=0  # Use single empty GPU
```

---

## 12. Testing Strategy

### 12.1 Unit Tests
- `test_embeddings.py` - Embedding extraction correctness
- `test_manova.py` - Statistical calculations
- `test_pca.py` - PCA transformation

### 12.2 Integration Tests
- Full pipeline with small sample (100 pairs)
- Checkpoint save/load functionality

### 12.3 Validation Tests
- Random baseline verification (d ≈ 0.0)
- PCA variance explained (first 2 PCs capture structure)

---

## 13. Architecture Validation

### 13.1 Complexity Check
✓ Total Epic tasks: 7 (within 6-12 range for MECHANISM)  
✓ All tasks have complexity scores  
✓ Complexity range: 6-12/20 (appropriate for MECHANISM)

### 13.2 Dependency Check
✓ No circular dependencies  
✓ Clear sequential execution path with checkpointing  
✓ All h-m1 dependencies verified from actual code

### 13.3 Mechanism Check
✓ Pretrained embeddings (RoBERTa-base, frozen)  
✓ MANOVA effect size as primary metric  
✓ Random baseline comparison  
✓ No training required (analysis only)

---

**Document Status:** COMPLETE  
**Next Phase:** Logic Design (03_logic.md)  
**Applied Patterns:** KB-Pattern-EmbeddingAnalysis, KB-Pattern-StatisticalTesting  
**Base Hypothesis:** h-m1 (data loading infrastructure reused)
