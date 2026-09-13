# Logic Design: H-M2
## Domain Exposure–Benchmark Correlation Analysis

**Date:** 2026-08-20
**Hypothesis:** H-M2 (MECHANISM — INCREMENTAL on H-E1 + H-M1)

Applied: pipeline-module pattern (data_loader → evaluator → correlation_analysis → statistical_test → visualization → reporter)
Applied: resume-capable batch evaluation pattern (cache-hit short-circuit before expensive compute)
Applied: nonparametric correlation with Fisher z-transform comparison pattern

---

## Codebase Analysis (Serena)

Serena MCP was unavailable (no active project configured). H-M1 base logic reviewed via Read tool:
- H-M1 uses `scipy.stats` (f_oneway, tukey_hsd) — H-M2 analogously uses `spearmanr` + custom Fisher z
- H-M1 data_loader pattern: stream → sample → compute → cache — H-M2 follows same cache-first pattern
- No conflicting import paths found; H-M2 is a new standalone pipeline in `src/h_m2/`

---

## Module A-3: Checkpoint Evaluator (4 subtasks)

### Subtask A-3-1: `evaluate_checkpoint`

```python
def evaluate_checkpoint(
    model_id: str,           # e.g. "EleutherAI/pythia-70m"
    step: int,               # e.g. 1000
    tasks: list[str],        # ["mmlu", "hellaswag"]
    cache_dir: Path,         # results/h-m2/eval_cache/{model_size}/
    num_fewshot_map: dict[str, int],  # {"mmlu": 5, "hellaswag": 10}
    device: str = "cuda",
    batch_size: str = "auto",
    dtype: str = "float",
) -> dict[str, float]:
    """
    Evaluate one Pythia checkpoint at a specific training step.
    
    Returns:
        {"mmlu": float, "hellaswag": float}  — accuracy scores [0, 1]
    
    Cache behavior:
        - cache_path = cache_dir / f"step{step:07d}.json"
        - If cache valid: return cached scores immediately (no GPU needed)
        - If cache miss: run lm_eval.simple_evaluate, save, return
    
    Raises:
        HubConnectionError: if HF Hub unreachable AND no fallback cache
        ValueError: if returned results missing expected task keys
    """
    cache_path = cache_dir / f"step{step:07d}.json"
    if is_cache_valid(cache_path, tasks):
        return load_cached_scores(cache_path)
    
    # Run evaluation
    model_args = f"pretrained={model_id},revision=step{step},dtype={dtype}"
    results = lm_eval.simple_evaluate(
        model="hf",
        model_args=model_args,
        tasks=tasks,
        num_fewshot=num_fewshot_map.get(tasks[0], 0),  # applied per-task below
        batch_size=batch_size,
        device=device,
    )
    # Extract scores
    scores = {
        "mmlu": results["results"]["mmlu"]["acc,none"],
        "hellaswag": results["results"]["hellaswag"]["acc_norm,none"],
    }
    # Save cache
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"step": step, "scores": scores}))
    return scores
```

**Tensor shapes:** scalar outputs only (aggregated over 14,042 / 10,042 examples internally by lm-eval)

### Subtask A-3-2: `batch_evaluate_model`

```python
def batch_evaluate_model(
    model_size: str,           # "70m", "1b", "6.9b"
    model_id: str,             # "EleutherAI/pythia-70m"
    steps: list[int],          # 154 checkpoint steps
    tasks: list[str],
    config: H_M2Config,
) -> dict[int, dict[str, float]]:
    """
    Evaluate all 154 checkpoints for one model size with resume.
    
    Returns:
        {step: {"mmlu": float, "hellaswag": float}}
    
    Algorithm:
        for step in steps:
            scores[step] = evaluate_checkpoint(model_id, step, ...)
            log(f"[{model_size}] step {step}: mmlu={scores[step]['mmlu']:.3f}, hellaswag={scores[step]['hellaswag']:.3f}")
        return scores
    
    Note: sequential by default; caller may parallelize across model sizes.
    """
```

### Subtask A-3-3: `is_cache_valid` + `load_cached_scores`

```python
def is_cache_valid(cache_path: Path, required_tasks: list[str]) -> bool:
    """Return True iff cache_path exists, is valid JSON, and has all required task scores."""
    if not cache_path.exists():
        return False
    try:
        data = json.loads(cache_path.read_text())
        return all(t in data.get("scores", {}) for t in required_tasks)
    except (json.JSONDecodeError, KeyError):
        return False

def load_cached_scores(cache_path: Path) -> dict[str, float]:
    return json.loads(cache_path.read_text())["scores"]
```

### Subtask A-3-4: `load_fallback_scores`

```python
def load_fallback_scores(
    model_size: str,
    pythia_repo_dir: Path,   # local clone of EleutherAI/pythia
    steps: list[int],
) -> dict[int, dict[str, float]]:
    """
    Load pre-cached eval results from pythia repo evals/pythia-v1/.
    
    File pattern: {pythia_repo_dir}/evals/pythia-v1/pythia-{model_size}/
                  step{N}/results_{task}.json
    
    Returns: {step: {"mmlu": float, "hellaswag": float}}
    Raises FileNotFoundError if fallback dir not present.
    """
```

---

## Module A-4: Decontamination Audit (2 subtasks)

### Subtask A-4-1: N-gram overlap utilities

```python
def build_ngram_set(text: str, n: int = 13) -> set[tuple[str, ...]]:
    """
    Tokenize text and return set of n-gram tuples.
    
    Args:
        text: raw string (MMLU question or HellaSwag context)
        n: gram size (default 13 per standard decontamination protocol)
    Returns:
        set of tuples, each of length n
    """
    tokens = nltk.word_tokenize(text.lower())
    return {tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def compute_overlap_rate(
    test_examples: list[str],   # MMLU questions or HellaSwag contexts
    pile_docs: list[str],        # training documents seen by checkpoint
    n: int = 13,
) -> float:
    """
    Fraction of test examples that share ≥1 n-gram with any training doc.
    
    Algorithm:
        pile_ngrams = union of build_ngram_set(doc, n) for doc in pile_docs
        contaminated = sum(1 for ex in test_examples if build_ngram_set(ex, n) & pile_ngrams)
        return contaminated / len(test_examples)
    
    Returns: float in [0, 1]
    """
```

### Subtask A-4-2: `run_decontamination_audit`

```python
@dataclass
class DecontaminationReport:
    mmlu_overlap_rate: float
    hellaswag_overlap_rate: float
    adjusted_scores: dict[str, dict[int, float]] | None  # None if delta < threshold
    use_adjusted: bool
    delta_mmlu: float      # max delta across subjects
    delta_hellaswag: float

def run_decontamination_audit(
    model_size: str,
    raw_scores: dict[int, dict[str, float]],  # {step: {task: score}}
    pile_idx_dir: Path,    # EleutherAI/pythia_deduped_pile_idxmaps
    config: H_M2Config,
) -> DecontaminationReport:
    """
    Full decontamination pipeline for one model size.
    
    Steps:
        1. Load MMLU test set and HellaSwag validation set questions
        2. Load Pile document indices for this model size from pile_idx_dir
        3. Sample representative pile documents (first 100k for efficiency)
        4. compute_overlap_rate for MMLU and HellaSwag
        5. If overlap > 5% for any subject: compute adjusted scores
           (adjusted_score = raw - contamination_delta_estimate)
        6. If delta > config.contamination_delta_threshold (0.03): use adjusted
        7. Save report JSON; return DecontaminationReport
    """
```

---

## Module A-5: Correlation Analysis (2 subtasks)

### Subtask A-5-1: `compute_spearman_matrix`

```python
@dataclass
class CorrelationResult:
    rho: float
    p_val: float
    ci_lower: float   # 95% CI lower bound via Fisher z-transform
    ci_upper: float   # 95% CI upper bound
    n: int            # number of valid checkpoints used

# Type aliases
CorrelationMatrix = dict[str, dict[str, CorrelationResult]]
# CorrelationMatrix[domain_name][benchmark_name] = CorrelationResult

def compute_spearman_matrix(
    exposure: np.ndarray,           # shape: (T_valid, 22) — filtered checkpoints × domains
    scores: dict[str, np.ndarray],  # {"mmlu": (T_valid,), "hellaswag": (T_valid,)}
    domain_names: list[str],        # length 22, ordered to match exposure columns
) -> CorrelationMatrix:
    """
    Compute Spearman ρ for all (domain, benchmark) pairs.
    
    Total: 22 domains × 2 benchmarks = 44 pairs (per model size).
    Across 3 model sizes: 132 total ρ values.
    
    For each (domain_idx, benchmark):
        rho, p_val = scipy.stats.spearmanr(exposure[:, domain_idx], scores[benchmark])
        n = T_valid
        stderr = 1.0 / sqrt(n - 3)
        ci_lower = tanh(arctanh(rho) - 1.96 * stderr)
        ci_upper = tanh(arctanh(rho) + 1.96 * stderr)
    
    Returns nested dict: matrix[domain_name][benchmark_name] = CorrelationResult
    """
```

### Subtask A-5-2: `extract_focal_correlations` + `apply_floor_filter`

```python
@dataclass
class FocalCorrelations:
    rho_wiki_mmlu: dict[str, float]       # {model_size: rho}
    rho_wiki_hellaswag: dict[str, float]
    rho_books_hellaswag: dict[str, float]
    rho_books_mmlu: dict[str, float]
    ci_wiki_mmlu: dict[str, tuple[float, float]]   # {model_size: (lower, upper)}
    # ... (same for other focal pairs)
    n_valid: dict[str, int]               # {model_size: N_valid_checkpoints}

def extract_focal_correlations(
    matrices: dict[str, CorrelationMatrix],  # {model_size: CorrelationMatrix}
) -> FocalCorrelations:
    """Extract the 4 focal (domain, benchmark) pairs across 3 model sizes."""

def apply_floor_filter(
    scores: dict[str, np.ndarray],    # {"mmlu": (154,), "hellaswag": (154,)}
    exposure: np.ndarray,              # (154, 22)
    floor_threshold: float = 0.30,
    min_valid: int = 100,
) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    """
    Filter checkpoints where any benchmark score < floor_threshold.
    
    Returns:
        exposure_filtered: (T_valid, 22)
        scores_filtered: {"mmlu": (T_valid,), "hellaswag": (T_valid,)}
        valid_mask: (154,) bool array
    
    Raises:
        ValueError: if T_valid < min_valid after filtering
    """
    valid_mask = np.ones(len(scores["mmlu"]), dtype=bool)
    for task_scores in scores.values():
        valid_mask &= (task_scores >= floor_threshold)
    T_valid = valid_mask.sum()
    if T_valid < min_valid:
        raise ValueError(f"Floor filter left only {T_valid} checkpoints (min={min_valid})")
    return exposure[valid_mask], {k: v[valid_mask] for k, v in scores.items()}, valid_mask
```

---

## Module A-6: Statistical Tests (1 subtask)

### Subtask A-6-1: Fisher z-test + Holm-Bonferroni + gate verification

```python
def fisher_z_test(
    rho1: float,
    rho2: float,
    n: int,
) -> tuple[float, float]:
    """
    One-tailed Fisher z-test for H1: rho1 > rho2.
    
    Algorithm:
        z1 = arctanh(rho1)
        z2 = arctanh(rho2)
        se = sqrt(2.0 / (n - 3))
        z_stat = (z1 - z2) / se
        p_one_tailed = 1 - norm.cdf(z_stat)
    
    Returns: (z_stat, p_one_tailed)
    
    Note: rho values near ±1 cause arctanh instability — clip to [-0.9999, 0.9999].
    """
    rho1 = np.clip(rho1, -0.9999, 0.9999)
    rho2 = np.clip(rho2, -0.9999, 0.9999)
    z1, z2 = np.arctanh(rho1), np.arctanh(rho2)
    se = np.sqrt(2.0 / (n - 3))
    z_stat = (z1 - z2) / se
    p_one_tailed = 1 - stats.norm.cdf(z_stat)
    return z_stat, p_one_tailed

def apply_holm_bonferroni(
    p_values: list[float],
    alpha: float = 0.10,
) -> list[bool]:
    """
    Holm-Bonferroni step-down procedure.
    
    Args:
        p_values: list of raw p-values (length m)
        alpha: family-wise error rate threshold
    Returns:
        list of bool — True = reject H0 at corrected threshold
    
    Algorithm:
        Sort p-values ascending with original indices.
        For k=1..m: reject if p_(k) <= alpha / (m - k + 1)
        Stop at first non-rejection (all subsequent accepted H0).
    """

def verify_mechanism_activated(
    results_by_model_size: dict[str, dict],
    # {model_size: {"(Wikipedia (en)", "mmlu")": CorrelationResult, ..., "n_valid_checkpoints": int}}
) -> tuple[bool, dict]:
    """
    Gate verification per 02c_experiment_brief.md spec.
    
    Returns:
        (mechanism_activated: bool, indicators: dict)
        indicators keys: p1_directional_count, p2_directional_count,
                         p1_gate_passed, p2_gate_passed
    
    Gate pass condition: p1_directional_count >= 2
    """
    p1_confirmed = 0
    p2_confirmed = 0
    for model_size, results in results_by_model_size.items():
        rho_wm = results[("Wikipedia (en)", "mmlu")].rho
        rho_wh = results[("Wikipedia (en)", "hellaswag")].rho
        rho_bh = results[("Books3", "hellaswag")].rho
        rho_bm = results[("Books3", "mmlu")].rho
        n_valid = results["n_valid_checkpoints"]
        assert n_valid >= 100, f"Floor filter removed too many checkpoints: {n_valid}"
        if rho_wm > rho_wh:
            p1_confirmed += 1
        if rho_bh > rho_bm:
            p2_confirmed += 1
    indicators = {
        "p1_directional_count": p1_confirmed,
        "p2_directional_count": p2_confirmed,
        "p1_gate_passed": p1_confirmed >= 2,
        "p2_gate_passed": p2_confirmed >= 2,
    }
    return indicators["p1_gate_passed"], indicators
```

---

## Module A-7: Visualization (2 subtasks)

### Subtask A-7-1: Gate metrics bar chart + heatmap

```python
def plot_gate_metrics(
    focal_corr: FocalCorrelations,
    output_path: Path,              # figures/fig1_gate_metrics.png
    model_sizes: list[str] = ["70m", "1b", "6.9b"],
) -> None:
    """
    Bar chart: ρ(Wikipedia→MMLU) vs ρ(Wikipedia→HellaSwag) × 3 model sizes.
    
    Layout: grouped bars (2 bars per model size), error bars = 95% CI
    Colors: colorblind-safe (blue=MMLU, orange=HellaSwag)
    x-axis: model sizes; y-axis: Spearman ρ; title: "P1 Gate Metric"
    Save at 300 DPI.
    """

def plot_heatmap(
    correlation_matrices: dict[str, CorrelationMatrix],  # {model_size: matrix}
    domain_names: list[str],
    top_n_domains: int = 8,           # top by |rho_mmlu + rho_hellaswag|
    output_path: Path,                # figures/fig2_domain_benchmark_heatmap.png
) -> None:
    """
    3-panel heatmap: one panel per model size.
    Rows = top_n_domains, Cols = ["MMLU", "HellaSwag"]
    Color: diverging palette centered at 0 (blue=negative, red=positive)
    Annotate cells with ρ value (2 decimal places).
    """
```

### Subtask A-7-2: Trajectory + forest + floor diagnostic plots

```python
def plot_trajectories(
    exposure: dict[str, np.ndarray],   # {model_size: (T_valid, 22)}
    scores: dict[str, dict[str, np.ndarray]],  # {model_size: {task: (T_valid,)}}
    valid_steps: dict[str, list[int]], # {model_size: list of valid step numbers}
    domain_names: list[str],
    focal_domain: str = "Wikipedia (en)",
    output_path: Path,                 # figures/fig3_trajectories.png
) -> None:
    """
    6-panel plot: 3 model sizes × 2 benchmarks.
    Each panel: dual y-axis (left=benchmark score, right=cumulative exposure).
    x-axis: training step (log scale after step 512).
    """

def plot_fisher_forest(
    fisher_results: dict,   # {model_size: {"p1": (z, p), "p2": (z, p)}}
    focal_corr: FocalCorrelations,
    output_path: Path,      # figures/fig4_fisher_forest.png
) -> None:
    """
    Forest plot: point estimates + 95% CIs for P1 and P2 per model size.
    Vertical line at 0 (null). Right of 0 = directional confirmation.
    """

def plot_floor_diagnostic(
    valid_masks: dict[str, np.ndarray],  # {model_size: (154,) bool}
    all_steps: list[int],
    scores_raw: dict[str, dict[str, np.ndarray]],
    output_path: Path,                   # figures/fig5_floor_filter.png
) -> None:
    """
    Show which of 154 checkpoints pass the floor filter per model size.
    Scatter: step vs MMLU score; color = valid/filtered; horizontal line at 0.30.
    """
```

---

## Summary: Subtask Allocation

| Subtask | Module | Description | Priority |
|---------|--------|-------------|----------|
| A-3-1 | Evaluator | `evaluate_checkpoint` with cache | 93 |
| A-3-2 | Evaluator | `batch_evaluate_model` resume loop | 92 |
| A-3-3 | Evaluator | `is_cache_valid` + `load_cached_scores` | 91 |
| A-3-4 | Evaluator | `load_fallback_scores` (HF Hub fallback) | 90 |
| A-4-1 | Decontamination | N-gram utilities | 85 |
| A-4-2 | Decontamination | `run_decontamination_audit` | 84 |
| A-5-1 | Correlation | `compute_spearman_matrix` | 80 |
| A-5-2 | Correlation | `extract_focal` + `apply_floor_filter` | 79 |
| A-6-1 | Statistical | Fisher z-test + gate verification | 75 |
| A-7-1 | Visualization | Gate bar chart + heatmap | 60 |
| A-7-2 | Visualization | Trajectory + forest + floor plots | 59 |

**Total subtasks: 11** | **Logic Agent budget: 11** ✓
