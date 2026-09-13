# Logic Specification: H-M4 (Scale Transfer Validation)

**Date:** 2026-08-28  
**Prerequisite:** H-M3 optimal threshold p44.5

---

## 1. Core Algorithms

### 1.1 Perplexity Threshold Filtering

```python
def filter_by_perplexity_threshold(
    documents: Iterator[Document],
    perplexity_scores: np.ndarray,  # shape: (N,)
    threshold_percentile: float = 44.5  # From H-M3
) -> Iterator[Document]:
    """
    Filter documents by KenLM perplexity percentile.
    Keep documents with perplexity <= threshold.
    
    Args:
        documents: Stream of Document(text, metadata)
        perplexity_scores: Pre-computed perplexity for each doc
        threshold_percentile: Percentile cutoff (p44.5 = keep bottom 44.5%)
    
    Returns:
        Filtered document stream
    """
    threshold_value = np.percentile(perplexity_scores, threshold_percentile)
    
    for doc, ppl in zip(documents, perplexity_scores):
        if ppl <= threshold_value:
            yield doc
```

### 1.2 Compute-Matched Token Budget

```python
def compute_matched_tokens(
    base_tokens: int,           # 10B for 125M
    base_params: int,           # 125M
    target_params: int,         # 1B
    scaling_exponent: float = 0.5  # Chinchilla-inspired
) -> int:
    """
    Calculate token budget for compute-matched training.
    
    Chinchilla: T_opt ~ C^0.5 / N^0.5
    For fixed compute ratio, scale tokens sublinearly with params.
    
    Returns:
        Token budget for target model
    """
    param_ratio = target_params / base_params  # 8x for 125M->1B
    token_multiplier = param_ratio ** scaling_exponent  # sqrt(8) ≈ 2.83
    return int(base_tokens * token_multiplier)

# Example:
# 125M: 10B tokens
# 1B:   compute_matched_tokens(10B, 125M, 1B) ≈ 28B tokens
# Simplified to 20B in experiment for tractability
```

### 1.3 Scale Transfer Validation Logic

```python
def validate_scale_transfer(
    scores_125m: dict,  # {"optimal": float, "default": float}
    scores_1b: dict,
    optimal_threshold_125m: float = 44.5,
    tolerance: float = 0.20  # ±20%
) -> dict:
    """
    Validate whether optimal threshold transfers across scales.
    
    Success criteria:
    1. Same-sign improvement at both scales
    2. If 1B sweep done: threshold within tolerance
    
    Returns:
        {
            "rankings_preserved": bool,
            "improvement_125m": float,
            "improvement_1b": float,
            "transfer_success": bool
        }
    """
    imp_125m = scores_125m["optimal"] - scores_125m["default"]
    imp_1b = scores_1b["optimal"] - scores_1b["default"]
    
    # Same sign = rankings preserved
    rankings_preserved = (imp_125m > 0) == (imp_1b > 0) and imp_125m != 0
    
    return {
        "rankings_preserved": rankings_preserved,
        "improvement_125m": imp_125m,
        "improvement_1b": imp_1b,
        "transfer_success": rankings_preserved and (imp_125m > 0)
    }
```

### 1.4 Ensemble Score Computation

```python
def compute_ensemble_score(
    benchmark_scores: dict,  # {"hellaswag": 0.52, "arc_easy": 0.58, ...}
    method: str = "mean"     # "mean" or "pc1"
) -> float:
    """
    Aggregate benchmark scores into single metric.
    
    Methods:
    - mean: Simple average (default for PoC)
    - pc1: First principal component (more robust)
    """
    scores = np.array(list(benchmark_scores.values()))  # shape: (4,)
    
    if method == "mean":
        return float(np.mean(scores))
    
    elif method == "pc1":
        # Center scores
        centered = scores - np.mean(scores)
        # For single sample, PC1 ≈ normalized sum
        # With multiple seeds: use sklearn.decomposition.PCA
        return float(np.sum(centered) / np.linalg.norm(centered))
    
    raise ValueError(f"Unknown method: {method}")


def compute_pc1_across_seeds(
    seed_results: list[dict],  # List of benchmark_scores dicts per seed
    benchmarks: list = ["hellaswag", "arc_easy", "piqa", "winogrande"]
) -> tuple[float, float]:
    """
    Compute PC1 ensemble with std across seeds.
    
    Args:
        seed_results: [{"hellaswag": 0.52, ...}, ...] per seed
    
    Returns:
        (mean_pc1, std_pc1)
    """
    # Build matrix: (n_seeds, n_benchmarks)
    X = np.array([[r[b] for b in benchmarks] for r in seed_results])
    
    # Standardize columns
    X_std = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
    
    # Simple PC1: first right singular vector weighted sum
    # For PoC, use mean per seed then aggregate
    seed_scores = X.mean(axis=1)  # shape: (n_seeds,)
    
    return float(np.mean(seed_scores)), float(np.std(seed_scores))
```

---

## 2. Tensor Shapes

### 2.1 Training Pipeline

```
Input:
  documents: Iterator[Document]          # Streaming
  
After tokenization:
  input_ids: (batch, seq_len)            # (512, 1024) for 125M
                                         # (256, 1024) for 1B (memory)
  attention_mask: (batch, seq_len)       # Same shape
  labels: (batch, seq_len)               # Same, shifted internally

Model forward:
  GPT-2 125M:
    embeddings: (batch, seq_len, 768)
    hidden_states: (batch, seq_len, 768) per layer (12 layers)
    logits: (batch, seq_len, 50257)
    
  GPT-2 1B:
    embeddings: (batch, seq_len, 1600)
    hidden_states: (batch, seq_len, 1600) per layer (48 layers)
    logits: (batch, seq_len, 50257)

Loss:
  cross_entropy: scalar
  
Evaluation:
  benchmark_scores: (4,)                 # 4 benchmarks
  ensemble: scalar
```

### 2.2 Data Pipeline

```
Raw corpus:
  N documents, variable length

Perplexity scoring:
  ppl_scores: (N,)                       # float32

After threshold filter (p44.5):
  ~0.445 * N documents retained

Tokenized:
  total_tokens: 10B (125M) / 20B (1B)
  batches: total_tokens / (batch * seq_len)
```

---

## 3. API Signatures

```python
# === Data Pipeline ===

def score_perplexity(
    documents: list[str],
    kenlm_model_path: str
) -> np.ndarray:
    """Returns perplexity scores, shape (N,)"""
    ...

def filter_documents(
    documents: Iterator[Document],
    ppl_scores: np.ndarray,
    threshold_percentile: float
) -> Iterator[Document]:
    """Yields filtered documents"""
    ...

def prepare_dataset(
    filtered_docs: Iterator[Document],
    tokenizer: PreTrainedTokenizer,
    max_length: int = 1024
) -> IterableDataset:
    """Returns streaming dataset for training"""
    ...


# === Training ===

def train_model(
    model: GPT2LMHeadModel,
    train_dataset: IterableDataset,
    config: TrainConfig,
    seed: int
) -> GPT2LMHeadModel:
    """Returns trained model checkpoint path"""
    ...

@dataclass
class TrainConfig:
    learning_rate: float      # 6e-4 (125M) / 2e-4 (1B)
    batch_size: int           # 512K / 2M tokens
    warmup_steps: int = 2000
    weight_decay: float = 0.1
    max_tokens: int           # 10B / 20B
    fp16: bool = True


# === Evaluation ===

def evaluate_model(
    model_path: str,
    tasks: list[str] = ["hellaswag", "arc_easy", "piqa", "winogrande"]
) -> dict[str, float]:
    """Returns {task: accuracy}"""
    ...

def run_scale_experiment(
    optimal_threshold: float,
    default_threshold: float,
    seeds: list[int] = [42, 43, 44]
) -> dict:
    """
    Main experiment entry point.
    
    Returns:
        {
            "125M": {"optimal": {...}, "default": {...}},
            "1B": {"optimal": {...}, "default": {...}},
            "transfer_validated": bool
        }
    """
    ...
```

---

## 4. Statistical Analysis

### 4.1 Paired Comparison Across Scales

```python
def analyze_transfer(
    results_125m: list[dict],  # Per-seed results
    results_1b: list[dict],
    alpha: float = 0.05
) -> dict:
    """
    Statistical analysis of scale transfer.
    
    Tests:
    1. Paired t-test: optimal vs default at each scale
    2. Sign consistency: same direction at both scales
    """
    from scipy import stats
    
    # Extract ensemble scores per seed
    opt_125m = [compute_ensemble_score(r) for r in results_125m["optimal"]]
    def_125m = [compute_ensemble_score(r) for r in results_125m["default"]]
    opt_1b = [compute_ensemble_score(r) for r in results_1b["optimal"]]
    def_1b = [compute_ensemble_score(r) for r in results_1b["default"]]
    
    # Paired t-tests
    t_125m, p_125m = stats.ttest_rel(opt_125m, def_125m)
    t_1b, p_1b = stats.ttest_rel(opt_1b, def_1b)
    
    # Improvements
    imp_125m = np.mean(opt_125m) - np.mean(def_125m)
    imp_1b = np.mean(opt_1b) - np.mean(def_1b)
    
    # Effect sizes (Cohen's d)
    d_125m = imp_125m / np.std(np.array(opt_125m) - np.array(def_125m))
    d_1b = imp_1b / np.std(np.array(opt_1b) - np.array(def_1b))
    
    return {
        "125M": {
            "improvement": imp_125m,
            "t_stat": t_125m,
            "p_value": p_125m,
            "cohens_d": d_125m,
            "significant": p_125m < alpha
        },
        "1B": {
            "improvement": imp_1b,
            "t_stat": t_1b,
            "p_value": p_1b,
            "cohens_d": d_1b,
            "significant": p_1b < alpha
        },
        "transfer": {
            "same_sign": (imp_125m > 0) == (imp_1b > 0),
            "both_positive": imp_125m > 0 and imp_1b > 0
        }
    }
```

### 4.2 Threshold Transfer Metric

```python
def compute_threshold_transfer_error(
    optimal_125m: float,  # p44.5
    optimal_1b: float     # From optional mini-sweep
) -> dict:
    """
    Quantify threshold transfer accuracy.
    Success: |delta| < 20%
    """
    delta = abs(optimal_1b - optimal_125m) / optimal_125m
    
    return {
        "optimal_125m": optimal_125m,
        "optimal_1b": optimal_1b,
        "relative_delta": delta,
        "within_tolerance": delta < 0.20
    }
```

---

## 5. Gate Conditions

```python
SUCCESS_CRITERIA = {
    "primary": "Optimal threshold at 1B within ±20% of 125M optimum",
    "secondary": "CPDR-optimized outperforms defaults at both scales"
}

def check_gate(analysis: dict) -> bool:
    """
    H-M4 passes if:
    1. Same-sign improvement at both scales (secondary)
    2. Both improvements > 0 (optimal beats default)
    """
    return (
        analysis["transfer"]["same_sign"] and
        analysis["transfer"]["both_positive"]
    )
```

---

*Skipped: Factory patterns, abstract interfaces, config file parsing. Add when multi-threshold sweep or 3+ model scales needed.*
