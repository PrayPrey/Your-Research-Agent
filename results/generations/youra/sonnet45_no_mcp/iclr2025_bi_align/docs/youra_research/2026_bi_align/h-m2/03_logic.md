# Logic Design & Implementation Details
# Hypothesis: h-m2 - Embedding Space Clustering Analysis

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m2  
**Hypothesis Type:** MECHANISM  
**Focus:** API Signatures, Tensor Shapes, Statistical Analysis

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m1 base code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/h-m1/code/`  
**Relevant Symbols:** load_hh_rlhf_dataset, stratified_sample

**Applied:** KB-Pattern-EmbeddingAnalysis, KB-Pattern-StatisticalTesting

---

## E-1: Data Loading and Preprocessing [Complexity: 7, Budget: 1]

**Applied:** Reuse h-m1 data loading infrastructure

### API Signatures

```python
def load_hh_rlhf_harmless(
    dataset_name: str = "Anthropic/hh-rlhf",
    split: str = "train",
    cache_dir: str = None
) -> Dataset:
    """Load full HH-RLHF dataset. Returns: HF Dataset with ~160K pairs"""
    ...

def extract_response_pairs(
    dataset: Dataset,
    max_samples: int = None
) -> Tuple[List[str], List[str]]:
    """Extract chosen and rejected texts. Returns: (chosen_texts, rejected_texts)"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| dataset | (N,) | HF Dataset, N~160K |
| chosen_texts | (N,) | List of strings |
| rejected_texts | (N,) | List of strings |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-1 | TextExtraction | Extract text fields from chosen/rejected |

---

## E-2: RoBERTa Embedding Extraction [Complexity: 12, Budget: 2]

**Applied:** PyTorch batch inference pattern

### API Signatures

```python
class RoBERTaEmbeddingExtractor:
    def __init__(self, model_name: str = "roberta-base", device: str = "cuda"):
        """Initialize RoBERTa-base model (frozen)."""
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.model = RobertaModel.from_pretrained(model_name)
        self.model.eval()
        self.device = device
    
    def extract_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        max_length: int = 512
    ) -> np.ndarray:
        """Extract CLS embeddings in batches. texts: List[N] -> [N, 768]"""
        ...
    
    def extract_embeddings(
        self,
        chosen_texts: List[str],
        rejected_texts: List[str],
        batch_size: int = 32
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract embeddings for both groups. Returns: ([N, 768], [N, 768])"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| texts | List[N] | Input strings |
| input_ids | [B, 512] | Tokenized batch |
| last_hidden_state | [B, 512, 768] | RoBERTa output |
| cls_embedding | [B, 768] | First token (CLS) |
| embeddings | [N, 768] | All samples |

### Pseudo-code

```
1. Load RoBERTa-base pretrained model (frozen)
2. For each batch of texts:
   a. Tokenize: tokenizer(texts, max_length=512, truncation=True)
   b. Forward pass: model(**inputs)
   c. Extract CLS: outputs.last_hidden_state[:, 0, :]  # [B, 768]
   d. Store to list
3. Stack all batches: np.vstack(embeddings)
4. Save to disk: np.save("chosen_embeddings.npy", chosen_emb)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | BatchProcessing | Implement memory-efficient batching |
| L-E2-2 | CheckpointSaving | Save embeddings to .npy files |

---

## E-3: PCA Dimensionality Reduction [Complexity: 8, Budget: 1]

**Applied:** scikit-learn PCA pattern

### API Signatures

```python
def apply_pca(
    embeddings: np.ndarray,
    n_components: int = 2
) -> Tuple[np.ndarray, PCA]:
    """Apply PCA. embeddings: [N, 768] -> ([N, 2], pca_model)"""
    ...

def compute_variance_explained(
    pca_model: PCA,
    n_components: int = 50
) -> np.ndarray:
    """Cumulative variance. Returns: [n_components]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [N, 768] | Input |
| reduced | [N, 2] | 2D projection |
| variance | [50] | Cumulative variance |

### Pseudo-code

```
1. Combine chosen + rejected: all_emb = np.vstack([chosen, rejected])
2. Fit PCA: pca = PCA(n_components=2).fit(all_emb)
3. Transform: chosen_2d = pca.transform(chosen_emb)
4. Compute variance: cumsum = np.cumsum(pca.explained_variance_ratio_[:50])
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | VarianceAnalysis | Compute variance explained for 50 PCs |

---

## E-4: MANOVA Statistical Analysis [Complexity: 10, Budget: 2]

**Applied:** Cohen's d effect size calculation

### API Signatures

```python
def compute_cohens_d(
    group1: np.ndarray,
    group2: np.ndarray
) -> float:
    """Cohen's d. group1: [N1, D], group2: [N2, D] -> float"""
    ...

def compute_manova_effect_size(
    chosen_embeddings: np.ndarray,
    rejected_embeddings: np.ndarray
) -> Dict[str, float]:
    """Multivariate effect size. Returns: {cohens_d, mean_separation, f_statistic, p_value}"""
    ...

def baseline_random_separation(
    embeddings: np.ndarray,
    n_trials: int = 100,
    seed: int = 42
) -> List[float]:
    """Random baseline. embeddings: [N, D] -> List[n_trials]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| chosen_embeddings | [N, 768] | Group 1 |
| rejected_embeddings | [N, 768] | Group 2 |
| mean_diff | [768] | Per-dimension difference |
| pooled_std | [768] | Pooled standard deviation |

### Pseudo-code

```
1. Compute multivariate Cohen's d:
   mean_diff = np.mean(chosen_emb, axis=0) - np.mean(rejected_emb, axis=0)
   pooled_std = np.sqrt((np.var(chosen_emb, axis=0) + np.var(rejected_emb, axis=0)) / 2)
   cohens_d = np.linalg.norm(mean_diff) / np.linalg.norm(pooled_std)

2. F-statistic (MANOVA):
   from scipy.stats import f_oneway
   f_stat, p_value = f_oneway(chosen_emb.flatten(), rejected_emb.flatten())

3. Random baseline:
   all_emb = np.vstack([chosen, rejected])
   for trial in range(100):
       labels = np.random.permutation([0]*N + [1]*N)
       group1 = all_emb[labels == 0]
       group2 = all_emb[labels == 1]
       d_random = compute_cohens_d(group1, group2)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | MANOVATest | Implement F-statistic calculation |
| L-E4-2 | RandomBaseline | 100 trials with random labels |

---

## E-5: Gate Metrics Visualization [Complexity: 6, Budget: 1]

**Applied:** Standard matplotlib bar chart

### API Signatures

```python
def plot_gate_metrics_comparison(
    cohens_d: float,
    baseline_d: float,
    threshold: float,
    output_path: str
) -> None:
    """Bar chart: baseline vs proposed. Saves to output_path"""
    ...
```

### Pseudo-code

```
1. Create bar chart:
   methods = ["Random Baseline", "RoBERTa Embeddings"]
   values = [baseline_d, cohens_d]
2. Add threshold line at d = 0.5
3. Annotate bars with actual values
4. Save to outputs/figures/gate_metrics.png
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | GateFigure | Create required gate metrics figure |

---

## E-6: Additional Visualizations [Complexity: 9, Budget: 1]

**Applied:** matplotlib/seaborn plot patterns

### API Signatures

```python
def plot_pca_scatter(
    chosen_2d: np.ndarray,
    rejected_2d: np.ndarray,
    variance_explained: Tuple[float, float],
    output_path: str
) -> None:
    """2D scatter. chosen_2d: [N, 2], rejected_2d: [N, 2]"""
    ...

def plot_effect_size_distribution(
    per_dimension_d: np.ndarray,
    output_path: str
) -> None:
    """Histogram. per_dimension_d: [768]"""
    ...

def plot_variance_explained(
    cumulative_variance: np.ndarray,
    output_path: str
) -> None:
    """Scree plot. cumulative_variance: [50]"""
    ...

def plot_distance_heatmap(
    chosen_sample: np.ndarray,
    rejected_sample: np.ndarray,
    output_path: str
) -> None:
    """Distance heatmap. Sample 100 pairs for visualization"""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E6-1 | MultiPlot | Generate 4 additional figures |

---

## E-7: Experiment Orchestration [Complexity: 10, Budget: 0]

**Applied:** Sequential pipeline with checkpointing

### API Signatures

```python
def run_h_m2_experiment(config: Dict) -> Dict:
    """
    Main orchestration.
    
    Returns:
        {
            "cohens_d": float,
            "baseline_d": float,
            "p_value": float,
            "gate_decision": str  # "PASS" | "FAIL"
        }
    """
    ...
```

### Pseudo-code

```
1. Load data:
   dataset = load_hh_rlhf_harmless()
   chosen_texts, rejected_texts = extract_response_pairs(dataset)

2. Extract embeddings:
   extractor = RoBERTaEmbeddingExtractor()
   chosen_emb, rejected_emb = extractor.extract_embeddings(chosen_texts, rejected_texts)
   np.save("data/chosen_embeddings.npy", chosen_emb)
   np.save("data/rejected_embeddings.npy", rejected_emb)

3. PCA reduction:
   chosen_2d, pca = apply_pca(chosen_emb, n_components=2)
   rejected_2d = pca.transform(rejected_emb)
   variance = compute_variance_explained(pca, 50)

4. Statistical analysis:
   results = compute_manova_effect_size(chosen_emb, rejected_emb)
   baseline_ds = baseline_random_separation(np.vstack([chosen_emb, rejected_emb]))
   baseline_d = np.mean(baseline_ds)

5. Gate decision:
   if results['cohens_d'] >= 0.5:
       gate = "PASS"
   elif results['cohens_d'] >= 0.3:
       gate = "EXPLORE"
   else:
       gate = "FAIL"

6. Visualizations:
   plot_gate_metrics_comparison(results['cohens_d'], baseline_d, 0.5, "gate_metrics.png")
   plot_pca_scatter(chosen_2d, rejected_2d, variance[:2], "pca_scatter.png")
   plot_effect_size_distribution(per_dim_d, "effect_size_dist.png")
   plot_variance_explained(variance, "variance_explained.png")
   plot_distance_heatmap(chosen_emb[:100], rejected_emb[:100], "distance_heatmap.png")

7. Write report:
   save_results(results, "outputs/results.json")
   generate_report(results, gate, "outputs/report.md")
```

### Subtasks [0/0 used]

No subtasks - orchestration logic only.

---

## External Dependencies API (Base Hypothesis)

The following APIs are called from h-m1 base hypothesis. Signatures verified from actual implementation:

```python
# From: h-m1/code/src/data/loader.py (ACTUAL CODE)
def load_hh_rlhf_dataset(
    dataset_name: str = "Anthropic/hh-rlhf",
    subset: str = None,
    split: str = "train",
    cache_dir: str = None
) -> Dataset:
    """Load HH-RLHF dataset. Returns: HF Dataset"""
    ...
```

**Verified from:** h-m1/code/ (actual implementation)

**Adaptation Strategy:**
- E-1: Reuse load_hh_rlhf_dataset, extend with extract_response_pairs for both chosen/rejected fields

---

## Data Flow Summary

```
HH-RLHF Dataset (160K+ pairs)
    ↓
[E-1] load_hh_rlhf_harmless → chosen_texts, rejected_texts
    ↓
[E-2] RoBERTaEmbeddingExtractor.extract_embeddings
    ├→ chosen_embeddings.npy [N, 768]
    └→ rejected_embeddings.npy [N, 768]
    ↓
    ├→ [E-3] apply_pca → chosen_2d [N, 2], rejected_2d [N, 2]
    │   └→ compute_variance_explained → variance [50]
    │
    └→ [E-4] compute_manova_effect_size
        ├→ cohens_d (proposed)
        ├→ baseline_random_separation → baseline_d
        └→ gate_decision (d ≥ 0.5?)
    ↓
[E-5] plot_gate_metrics_comparison → gate_metrics.png
[E-6] plot_pca_scatter, plot_effect_size_distribution, etc. → 4 figures
    ↓
[E-7] run_h_m2_experiment → report.md, results.json
```

---

## Configuration Schema

```yaml
experiment:
  name: "h-m2-embedding-clustering"
  hypothesis_id: "h-m2"
  seed: 42

dataset:
  name: "Anthropic/hh-rlhf"
  split: "train"
  max_samples: null  # Full dataset

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
  secondary_threshold: 0.3

outputs:
  data_dir: "data/"
  figures_dir: "outputs/figures/"
  results_file: "outputs/results.json"
  report_file: "outputs/report.md"
```

---

## Error Handling

### GPU Memory Overflow
```python
# In extract_batch():
try:
    outputs = self.model(**inputs)
except RuntimeError as e:
    if "out of memory" in str(e):
        # Reduce batch size and retry
        return self.extract_batch(texts, batch_size=batch_size//2, max_length=max_length)
    raise
```

### Dataset Size Mismatch
```python
# In extract_response_pairs():
assert len(chosen_texts) == len(rejected_texts), \
    f"Mismatch: {len(chosen_texts)} chosen vs {len(rejected_texts)} rejected"
```

---

## Testing Guidance

### Unit Tests

**test_embeddings.py:**
```python
def test_cls_extraction():
    extractor = RoBERTaEmbeddingExtractor()
    emb = extractor.extract_batch(["test sentence"], batch_size=1)
    assert emb.shape == (1, 768)

def test_batch_consistency():
    texts = ["text1", "text2"]
    emb1 = extractor.extract_batch(texts, batch_size=1)
    emb2 = extractor.extract_batch(texts, batch_size=2)
    np.testing.assert_allclose(emb1, emb2, rtol=1e-5)
```

**test_manova.py:**
```python
def test_cohens_d_identical():
    group1 = np.random.randn(100, 10)
    d = compute_cohens_d(group1, group1)
    assert d < 0.01  # Nearly zero for identical groups

def test_random_baseline():
    embeddings = np.random.randn(1000, 768)
    baseline_ds = baseline_random_separation(embeddings, n_trials=10)
    assert np.mean(baseline_ds) < 0.1  # Random labels → d ≈ 0
```

**test_pca.py:**
```python
def test_pca_variance():
    embeddings = np.random.randn(500, 768)
    reduced, pca = apply_pca(embeddings, n_components=2)
    assert reduced.shape == (500, 2)
    assert len(pca.explained_variance_ratio_) == 768
```

---

## Subtask Budget Summary

| Epic | Complexity | Subtasks Used | Subtasks IDs |
|------|------------|---------------|--------------|
| E-1  | 7          | 1             | L-E1-1 |
| E-2  | 12         | 2             | L-E2-1, L-E2-2 |
| E-3  | 8          | 1             | L-E3-1 |
| E-4  | 10         | 2             | L-E4-1, L-E4-2 |
| E-5  | 6          | 1             | L-E5-1 |
| E-6  | 9          | 1             | L-E6-1 |
| E-7  | 10         | 0             | - |
| **Total** | **62** | **8** | **8/8 budget used** |

---

**Document Status:** COMPLETE  
**Next Phase:** Configuration Design (03_config.md)  
**Applied Patterns:** KB-Pattern-EmbeddingAnalysis, KB-Pattern-StatisticalTesting  
**Base Hypothesis:** h-m1 (data loading infrastructure reused)
