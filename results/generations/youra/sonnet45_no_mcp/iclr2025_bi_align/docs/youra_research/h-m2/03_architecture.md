# System Architecture Document

**Hypothesis:** h-m2  
**Date:** 2026-04-19  
**Author:** Architecture Agent  
**Version:** 1.0  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Analyzed h-m1 actual code structure  
**Analyzed Path**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/h-m1/code/`  
**Findings**: h-m1 implements contrastive opinion encoder with demographic clustering. h-m2 is analysis-only (no training) - loads frozen embeddings from h-m1 checkpoint and tests correlation between embedding similarity and behavioral concordance on ETHICS benchmark.

**Applied**: Behavioral Similarity Embeddings (ICLR 2021), Data-Centric RLHF Similarity Analysis (2024)

---

## 1. Architecture Overview

**Design Principle**: Pure analysis pipeline - no model training, only correlation measurement.

**Key Characteristics**:
- No training (uses frozen h-m1 embeddings)
- CPU-only execution (analysis workload)
- Single execution (no multi-seed needed for correlation)
- ETHICS benchmark for behavioral concordance

**Pipeline**:
1. Load h-m1 embeddings (frozen)
2. Load ETHICS test set
3. Compute embedding similarity matrix
4. Generate simulated user responses
5. Measure concordance for user pairs
6. Compute correlation coefficient

**Success Criteria**: Pearson r > 0.5, p < 0.05, high-similarity concordance > 0.65

---

## 2. Module Structure

### 2.1 Embedding Loader (`loaders/embedding_loader.py`)

**Dependencies**: torch, h-m1 checkpoint

```python
class EmbeddingLoader:
    def __init__(self, checkpoint_path: str): ...
    def load_h_m1_embeddings(self) -> Tuple[Tensor, dict]: ...
    def verify_checkpoint(self) -> bool: ...
```

---

### 2.2 ETHICS Data Module (`data/ethics_loader.py`)

**Dependencies**: datasets, transformers

```python
class ETHICSDataset(Dataset):
    def __init__(self, tokenizer, split='test', cache_dir=None): ...
    def _load_ethics(self): ...
    def __getitem__(self, idx) -> dict: ...

def get_ethics_dataloader(config, tokenizer) -> DataLoader: ...
```

---

### 2.3 Response Generator (`analysis/response_generator.py`)

**Dependencies**: torch, h-m1 model

```python
class UserResponseGenerator:
    def __init__(self, embeddings: Tensor, model, tokenizer): ...
    def generate_responses(self, ethics_dataset) -> Tensor: ...
    def _predict_from_embedding(self, embedding, scenario) -> int: ...
```

---

### 2.4 Similarity Analysis (`analysis/similarity.py`)

**Dependencies**: torch, numpy

```python
def compute_similarity_matrix(embeddings: Tensor) -> Tensor: ...
def sample_user_pairs_stratified(similarity_matrix, n_samples=1000) -> dict: ...
def get_similarity_bins(similarity_values, thresholds) -> List[str]: ...
```

---

### 2.5 Concordance Measurement (`analysis/concordance.py`)

**Dependencies**: numpy, torch

```python
def measure_concordance(user_pairs, responses: Tensor) -> Tensor: ...
def concordance_by_bin(similarity_values, concordance_values, bins) -> dict: ...
def random_baseline_concordance(responses, n_pairs=1000) -> float: ...
```

---

### 2.6 Correlation Analysis (`analysis/correlation.py`)

**Dependencies**: scipy, numpy

```python
def compute_pearson_correlation(similarity, concordance) -> Tuple[float, float]: ...
def compute_spearman_correlation(similarity, concordance) -> Tuple[float, float]: ...
def bootstrap_confidence_interval(similarity, concordance, n_bootstrap=1000) -> Tuple[float, float]: ...
def evaluate_gate_criteria(results: dict, config) -> dict: ...
```

---

### 2.7 Visualization (`eval/visualizations.py`)

**Dependencies**: matplotlib, seaborn

```python
def plot_gate_metrics(results: dict, config, save_path): ...
def plot_correlation_scatter(similarity, concordance, save_path): ...
def plot_concordance_by_bin(results: dict, save_path): ...
def plot_similarity_heatmap(similarity_matrix, sampled_pairs, save_path): ...
```

---

### 2.8 Configuration (`config/analysis_config.py`)

```python
@dataclass
class H_M1Config:
    checkpoint_path: str = "../h-m1/checkpoints/contrastive_seed42/best_model.pt"
    embedding_dim: int = 256
    num_demographic_groups: int = 60

@dataclass
class ETHICSConfig:
    dataset_name: str = "hendrycks/ethics"
    cache_dir: str = "../../.data_cache/datasets/huggingface"
    categories: List[str] = field(default_factory=lambda: ['deontology', 'virtue', 'justice', 'utilitarianism', 'commonsense'])

@dataclass
class AnalysisConfig:
    n_user_pairs: int = 1000
    similarity_threshold: float = 0.7
    low_bin_max: float = 0.3
    medium_bin_range: Tuple[float, float] = (0.3, 0.7)
    random_seed: int = 42

@dataclass
class GateConfig:
    target_correlation: float = 0.5
    target_high_sim_concordance: float = 0.65
    min_baseline_diff: float = 0.10
    significance_level: float = 0.05
```

---

### 2.9 Main Execution (`run_analysis.py`)

```python
def load_h_m1_artifacts(config) -> Tuple[Tensor, Model]: ...
def load_ethics_data(config, tokenizer) -> Dataset: ...
def generate_user_responses(embeddings, model, ethics_data) -> Tensor: ...
def run_similarity_analysis(embeddings, responses, config) -> dict: ...
def evaluate_correlation(results, config) -> dict: ...
def generate_visualizations(results, config): ...
def main(): ...
```

---

## 3. External Dependencies (Base Hypothesis)

### Module Paths from h-m1

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ContrastiveModel | `sys.path.append('../h-m1/code'); from models.contrastive_model import DemographicContrastiveOpinionEncoder` | `h-m1/code/models/contrastive_model.py` |
| Config | Load checkpoint metadata | `h-m1/checkpoints/contrastive_seed42/best_model.pt` |

**Verified from**: `h-m1/code/` actual implementation

**Reuse Pattern**:
- Load h-m1 checkpoint to get frozen embeddings
- Reuse model architecture for response generation (inference only)
- No code imports - just checkpoint loading

---

## 4. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Embedding & Data Loading | Load h-m1 checkpoint, ETHICS dataset | 8 | 2+2+2+2 |
| C-2 | Response Generation | Generate user responses on ETHICS using embeddings | 11 | 3+2+3+3 |
| C-3 | Similarity Analysis | Compute similarity matrix, stratified sampling | 9 | 2+2+3+2 |
| C-4 | Concordance Measurement | Measure agreement rates for user pairs | 10 | 3+2+3+2 |
| C-5 | Correlation & Statistical Tests | Pearson/Spearman correlation, gate evaluation | 12 | 3+3+4+2 |
| C-6 | Visualization & Results | Generate figures, save results | 9 | 2+2+3+2 |

**Total Epic Tasks**: 6  
**Complexity Distribution**:
- High (14-17): 0 tasks
- Medium (9-13): 6 tasks (C-1, C-2, C-3, C-4, C-5, C-6)

---

## 5. Task Breakdown Details

### Epic C-1: Embedding & Data Loading
**Complexity**: 8/20 (Low-Medium)  
**Module_Size(2) + Dependencies(2) + Algorithm(2) + Integration(2)**

**Components**:
- Load h-m1 checkpoint (best_model.pt from seed 42)
- Extract user embeddings from checkpoint
- Load ETHICS dataset (5 categories, test split)
- Verify embedding dimension matches h-m1 (256-d)

**Files**: 
- `loaders/embedding_loader.py` (~80 lines)
- `data/ethics_loader.py` (~120 lines)

**Acceptance**:
- h-m1 embeddings loaded: (N_users, 256)
- ETHICS test set: ~13,000 examples
- All 5 categories present

---

### Epic C-2: Response Generation
**Complexity**: 11/20 (Medium)  
**Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(3)**

**Components**:
- Initialize h-m1 model for inference (frozen)
- Generate user responses on ETHICS scenarios
- Use embedding-based prediction (similarity to scenario embeddings)
- Ensure all users respond to same task subset

**Files**: `analysis/response_generator.py` (~150 lines)

**Acceptance**:
- Response matrix: (N_users, N_tasks) with binary values
- Same tasks for all users (concordance measurement requirement)
- Deterministic generation (seed=42)

---

### Epic C-3: Similarity Analysis
**Complexity**: 9/20 (Medium)  
**Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)**

**Components**:
- Compute pairwise cosine similarity (N_users × N_users)
- Stratified sampling: low/medium/high bins
- Sample 1000 user pairs (333 per bin)
- Store similarity values for correlation

**Files**: `analysis/similarity.py` (~120 lines)

**Acceptance**:
- Similarity matrix computed
- 1000 user pairs sampled (stratified)
- Bins balanced: ~333 pairs each

---

### Epic C-4: Concordance Measurement
**Complexity**: 10/20 (Medium)  
**Module_Size(3) + Dependencies(2) + Algorithm(3) + Integration(2)**

**Components**:
- Agreement rate calculation for each pair
- Concordance by similarity bin (low/med/high)
- Random baseline concordance (shuffled pairs)
- Category-specific concordance (per ETHICS domain)

**Files**: `analysis/concordance.py` (~130 lines)

**Acceptance**:
- Concordance values: (1000,) array aligned with similarity
- Mean concordance per bin computed
- Random baseline: ~0.50 (chance level)

---

### Epic C-5: Correlation & Statistical Tests
**Complexity**: 12/20 (Medium)  
**Module_Size(3) + Dependencies(3) + Algorithm(4) + Integration(2)**

**Components**:
- Pearson correlation coefficient (primary metric)
- Spearman rank correlation (robustness check)
- Statistical significance test (p-value)
- Bootstrap confidence intervals
- Gate criteria evaluation (all 4 criteria)

**Files**: `analysis/correlation.py` (~180 lines)

**Acceptance**:
- Pearson r computed with p-value
- Gate result: PASS/FAIL
- All 4 gate criteria evaluated
- 95% confidence intervals

---

### Epic C-6: Visualization & Results
**Complexity**: 9/20 (Medium)  
**Module_Size(2) + Dependencies(2) + Algorithm(3) + Integration(2)**

**Components**:
- Gate metrics figure (required)
- Correlation scatter plot with regression line
- Concordance by bin box plot
- Similarity heatmap with sampled pairs
- Results JSON export

**Files**: 
- `eval/visualizations.py` (~200 lines)
- `run_analysis.py` (results export, ~50 lines)

**Acceptance**:
- gate_metrics_comparison.png generated
- 3 additional figures saved
- experiment_results.json with all metrics

---

## 6. Data Flow

```
h-m1 Checkpoint (../h-m1/checkpoints/contrastive_seed42/best_model.pt)
    ↓
User Embeddings (N_users, 256)
    ↓
    ├──→ Similarity Matrix (N × N)
    │        ↓
    │    Stratified Sampling (1000 pairs)
    │
    └──→ Response Generator
             ↓
         ETHICS Responses (N_users, N_tasks)
             ↓
         Concordance Measurement
             ↓
         Concordance Values (1000,)
             ↓
             └───────┬───────────┘
                     ↓
         Correlation Analysis (Pearson r, p-value)
                     ↓
         Gate Evaluation + Visualizations
```

---

## 7. Configuration Schema

```yaml
# analysis_config.yaml
h_m1:
  checkpoint_path: "../h-m1/checkpoints/contrastive_seed42/best_model.pt"
  embedding_dim: 256
  num_demographic_groups: 60
  encoder_name: "roberta-base"

ethics:
  dataset_name: "hendrycks/ethics"
  cache_dir: "../../.data_cache/datasets/huggingface"
  categories: ['deontology', 'virtue', 'justice', 'utilitarianism', 'commonsense']
  test_split_size: 13000

analysis:
  n_user_pairs: 1000
  similarity_threshold: 0.7
  low_bin_max: 0.3
  medium_bin_range: [0.3, 0.7]
  random_seed: 42

gate:
  target_correlation: 0.5
  target_high_sim_concordance: 0.65
  min_baseline_diff: 0.10
  significance_level: 0.05

output:
  figures_dir: "../figures"
  results_file: "../outputs/experiment_results.json"
```

---

## 8. Technology Stack

**Core**:
- PyTorch 2.0+ (embedding manipulation, model loading)
- Transformers 4.30+ (RoBERTa tokenizer, model inference)
- Datasets 2.12+ (ETHICS loading)

**Analysis**:
- scipy (pearsonr, spearmanr)
- numpy (array operations)
- scikit-learn (optional: additional metrics)

**Visualization**:
- matplotlib, seaborn

**Hardware**:
- CPU-only (no GPU needed)
- ~4GB RAM for embeddings + similarity matrix
- ~5-10 minutes execution time

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| h-m1 checkpoint missing | Verify path before analysis, fallback to other seeds |
| ETHICS download failure | Retry logic (3 attempts, 15s delay), offline cache |
| Insufficient user diversity | Check similarity distribution spans [0, 1] |
| Low sample size (1000 pairs) | Adequate for r > 0.5 detection, can increase to 2000 |
| Response generation instability | Use frozen h-m1 model, deterministic seed |

---

## 10. Testing Strategy

**Unit Tests**:
- Similarity matrix symmetry and range [0, 1]
- Concordance calculation correctness (toy data)
- Stratified sampling balance check

**Integration Tests**:
- End-to-end analysis with small dataset (100 users)
- Checkpoint loading with mock file
- Correlation computation with known data

**Validation**:
- Random baseline concordance ≈ 0.50
- Similarity distribution covers all bins
- All figures generated without errors

---

## 11. Execution Differences from h-m1

| Aspect | h-m1 | h-m2 |
|--------|------|------|
| Training | Yes (15 epochs, 3 seeds) | No (analysis only) |
| GPU Required | Yes | No (CPU sufficient) |
| Seeds | 3 seeds (1, 42, 123) | 1 seed (42 for sampling) |
| Dataset | OpinionQA | ETHICS |
| Output Metric | Silhouette score | Correlation coefficient |
| Execution Time | ~3-5 hours | ~5-10 minutes |
| Checkpoint | Produces checkpoint | Consumes checkpoint |

---

## 12. Deliverables Checklist

- [x] Module structure defined (9 modules)
- [x] 6 Epic tasks with complexity scores
- [x] Data flow documented
- [x] Configuration schema defined
- [x] Technology stack selected
- [x] Risk mitigation strategies
- [x] Testing strategy outlined
- [x] External dependencies from h-m1 documented
- [x] Codebase analysis completed

---

**Status**: Ready for Logic & Configuration Design (Phase 3 Steps 4-5)
