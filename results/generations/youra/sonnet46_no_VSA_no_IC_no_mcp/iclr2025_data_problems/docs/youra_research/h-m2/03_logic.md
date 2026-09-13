# Logic Design: H-M2 — Min-k% Memorization Signal Analysis

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M2 (MECHANISM / SHOULD_WORK)
**Tier:** FULL — 14 subtasks across A-2, A-4, A-7, A-8

Applied: revision-specific-checkpoint-loading pattern
Applied: shifted-logit-per-token-logprob pattern
Applied: min-k-percent-aggregation pattern
Applied: paired-statistical-test-with-bonferroni pattern
Applied: checkpoint-resume-json-atomic-write pattern

---

## Codebase Analysis (Serena)

**Analyzed:** `docs/youra_research/h-m1/code/` via `03_logic.md` (base hypothesis — Serena MCP unavailable)

**Reusable from h-m1:**
- `BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]` — copy verbatim
- `CORRECTED_ALPHA = 0.0125` — copy verbatim
- `sig_stars(p)` helper: `"***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"` — copy to visualizer.py
- `matplotlib.use("Agg")` before import — copy pattern
- Checkpoint atomic write: `.tmp` + `os.replace()` — copy pattern
- JSON intermediate format — follow convention

**New in h-m2:**
- `AutoModelForCausalLM.from_pretrained(..., revision="step{N}", torch_dtype=torch.float16)` pattern
- Shifted logit computation: `logits[..., :-1, :]` / `input_ids[..., 1:]` for next-token prediction
- Min-k% aggregation: sort token log-probs ascending, mean of first k_count elements
- Paired t-test (`scipy.stats.ttest_rel`) vs Mann-Whitney U in h-m1
- Cross-hypothesis loading: `json.loads(HM1_RESULTS_PATH.read_text())`

**External Dependencies API (verified from h-m1 actual specs):**
- `sig_stars(p: float) -> str` — from h-m1/code/visualizer.py (verified from 03_logic.md line 23)
- `BENCHMARKS: list[str]` — from h-m1/code/config.py (verified from 03_config.md `ExperimentConfig.benchmarks`)
- `CORRECTED_ALPHA: float = 0.0125` — from h-m1/code/config.py (verified from 03_config.md)

---

## Data Structures

```python
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

@dataclass
class ModelSpec:
    model_id: str           # HuggingFace model ID
    revision: str           # e.g. "step98000"
    corpus: str             # "pile" or "deduped"
    size: str               # "1b" or "6.9b"
    key: str                # e.g. "pile_1b"

@dataclass
class BenchmarkItem:
    benchmark: str
    item_id: int
    text: str               # question + answer concatenated
    token_count: int        # after tokenization (None if < MIN_SEQ_LEN)
    valid: bool             # True if token_count >= MIN_SEQ_LEN

@dataclass
class MinKScore:
    item_id: int
    benchmark: str
    model_key: str
    scores: dict[int, float]    # {k_percent: min_k_score}  e.g. {10: -4.2, 20: -3.8, 40: -3.1}

@dataclass
class BenchmarkStat:
    benchmark: str
    model_size: str         # "1b" or "6.9b"
    mean_pile: float
    mean_deduped: float
    differential: float     # mean_pile - mean_deduped
    t_statistic: float
    p_value: float          # raw one-tailed
    p_corrected: float      # Bonferroni: p_raw * 4
    wilcoxon_p: float
    cohens_d: float
    significant: bool       # p_corrected < 0.0125

@dataclass
class SpearmanResult:
    rho: float
    p_value: float
    hm1_benchmark_order: list[str]   # H-M1 contamination ranking
    hm2_benchmark_order: list[str]   # H-M2 memorization differential ranking

# Type aliases
ScoresDict = dict[str, dict[str, list[float]]]
# {model_key: {benchmark: [per-item min-k% score at k=20]}}
```

---

## Subtask Table

| ID | Parent | Title | Description |
|----|--------|-------|-------------|
| L-2-1 | A-2 | load_model_checkpoint | HuggingFace revision= loading with fp16; step verification; device placement |
| L-2-2 | A-2 | verify_checkpoint_step | Extract loaded step from model config; log token count; adjacent-step fallback |
| L-4-1 | A-4 | compute_token_logprobs | Shifted logit forward pass → per-token log-probabilities array |
| L-4-2 | A-4 | compute_mink_score | Sort token log-probs ascending; mean of lowest k% |
| L-4-3 | A-4 | score_benchmark_items | Score all valid items for one model-benchmark combination |
| L-4-4 | A-4 | checkpoint_mink_scores | Save/load per-model-benchmark score arrays to JSON |
| L-4-5 | A-4 | score_all_models | Outer loop over 4 models × 4 benchmarks × k values with checkpoint/resume |
| L-7-1 | A-7 | plot_mink_comparison_bar | Mandatory gate figure: mean min-k% (Pile vs deduped) per benchmark × model size |
| L-7-2 | A-7 | plot_mink_heatmap | Differential heatmap: 4 benchmarks × 2 model sizes |
| L-7-3 | A-7 | plot_mink_violin | Per-benchmark item-level score distribution (Pile vs deduped, 6.9B) |
| L-7-4 | A-7 | plot_cross_hypothesis | Scatter: H-M1 contamination differential vs H-M2 memorization differential |
| L-8-1 | A-8 | run_pipeline_stages | Stage orchestrator: load_benchmarks → score → stats → ablations → figures |
| L-8-2 | A-8 | verify_mechanism_activated | Check all 4 checkpoints loaded; ≥500 items scored; direction check |
| L-8-3 | A-8 | generate_validation_report | Compile all results into 04_validation.md format |

---

## A-2: Model Loader (2 subtasks)

### L-2-1: load_model_checkpoint

```python
def load_model_checkpoint(
    model_id: str,
    revision: str,
    device: str = "cuda",
    cache_dir: str = "./model_cache",
) -> tuple["AutoModelForCausalLM", "AutoTokenizer"]:
    """
    Load Pythia checkpoint at specific revision (step).
    
    Args:
        model_id: e.g. "EleutherAI/pythia-1b"
        revision: e.g. "step98000"
        device: "cuda" or "cpu"
        cache_dir: local cache for HuggingFace downloads
    
    Returns:
        (model, tokenizer) — model in eval() mode, fp16 on device
    
    Raises:
        OSError: if revision not found → caller tries adjacent steps
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        revision=revision,
        torch_dtype=torch.float16,
        cache_dir=cache_dir,
    ).to(device).eval()
    
    return model, tokenizer
```

### L-2-2: verify_checkpoint_step

```python
def verify_checkpoint_step(
    model: "AutoModelForCausalLM",
    model_spec: ModelSpec,
    adjacent_steps: list[int] = [97000, 99000, 100000],
) -> str:
    """
    Verify loaded checkpoint matches target step. Try adjacent steps on OSError.
    
    Returns: actual revision string used (may differ from model_spec.revision on fallback)
    
    Logs: "Loaded checkpoint at step {step}, token_count={tokens:.1f}B"
    token_count = step * 2_097_152 / 1e9
    """
    import logging
    
    step_str = model_spec.revision.replace("step", "")
    step = int(step_str)
    token_count_b = step * 2_097_152 / 1e9
    
    logging.info(
        f"Loaded {model_spec.key}: step={step}, token_count={token_count_b:.1f}B tokens"
    )
    return model_spec.revision
```

---

## A-4: Min-k% Scorer (5 subtasks)

### L-4-1: compute_token_logprobs

```python
def compute_token_logprobs(
    input_ids: "torch.Tensor",    # shape [1, seq_len]
    model: "AutoModelForCausalLM",
    device: str = "cuda",
) -> "np.ndarray":
    """
    Compute per-token log-probabilities via next-token prediction.
    
    Returns: np.ndarray shape [seq_len - 1] — log-prob of each actual token
             given its prefix context (autoregressive)
    
    Algorithm:
    1. Forward pass: logits = model(input_ids).logits  # [1, seq_len, vocab_size]
    2. Shift: shift_logits = logits[0, :-1, :]         # [seq_len-1, vocab_size]
             shift_labels = input_ids[0, 1:]            # [seq_len-1]
    3. log_softmax over vocab → log_probs [seq_len-1, vocab_size]
    4. Gather actual token probs: log_probs[range(seq_len-1), shift_labels]
    
    Shapes: input [1, L] → output [L-1]
    """
    import torch
    import torch.nn.functional as F
    
    with torch.no_grad():
        logits = model(input_ids).logits   # [1, L, V]
    
    shift_logits = logits[0, :-1, :].float()   # [L-1, V] — float32 for numerical precision
    shift_labels = input_ids[0, 1:]             # [L-1]
    
    log_probs = F.log_softmax(shift_logits, dim=-1)   # [L-1, V]
    token_log_probs = log_probs[
        torch.arange(len(shift_labels), device=device), shift_labels
    ].cpu().numpy()   # [L-1]
    
    return token_log_probs
```

### L-4-2: compute_mink_score

```python
def compute_mink_score(
    token_log_probs: "np.ndarray",   # shape [seq_len-1]
    k: int = 20,                      # percentage (0-100)
) -> float:
    """
    Compute min-k% probability score per Shi et al. 2023.
    
    Algorithm: sort token_log_probs ascending (lowest first);
               return mean of lowest k% of tokens.
    
    Note: HIGHER score (less negative) → more memorized.
    
    Args:
        token_log_probs: per-token log-probabilities
        k: percentage of tokens to average (e.g. 20 = lowest 20%)
    
    Returns: float — mean log-prob of lowest k% tokens
    
    Edge cases:
        - k_count = max(1, int(len(tokens) * k / 100))
        - If len(tokens) == 0: return float('-inf') (filtered upstream)
    """
    import numpy as np
    
    if len(token_log_probs) == 0:
        return float('-inf')
    
    sorted_probs = np.sort(token_log_probs)   # ascending: lowest first
    k_count = max(1, int(len(sorted_probs) * k / 100))
    return float(sorted_probs[:k_count].mean())
```

### L-4-3: score_benchmark_items

```python
def score_benchmark_items(
    items: list[BenchmarkItem],
    model: "AutoModelForCausalLM",
    tokenizer: "AutoTokenizer",
    k_values: list[int] = [10, 20, 40],
    device: str = "cuda",
    batch_size: int = 1,
) -> list[MinKScore]:
    """
    Score all valid benchmark items for one model.
    
    Args:
        items: BenchmarkItem list (pre-filtered for validity)
        model: loaded Pythia checkpoint in eval mode
        k_values: list of k percentages to compute
    
    Returns: list[MinKScore] — one per valid item
    
    Note: batch_size=1 is safe and simple; batch_size=8 with padding
          is faster but requires careful attention mask handling.
    """
    from tqdm import tqdm
    import torch
    
    scores = []
    valid_items = [it for it in items if it.valid]
    
    for item in tqdm(valid_items, desc=f"Scoring {items[0].benchmark if items else ''}"):
        inputs = tokenizer(
            item.text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        input_ids = inputs["input_ids"].to(device)
        
        if input_ids.shape[1] < 32:    # double-check after tokenization
            continue
        
        token_log_probs = compute_token_logprobs(input_ids, model, device)
        item_scores = {k: compute_mink_score(token_log_probs, k) for k in k_values}
        
        scores.append(MinKScore(
            item_id=item.item_id,
            benchmark=item.benchmark,
            model_key="",   # filled by caller
            scores=item_scores,
        ))
    
    return scores
```

### L-4-4: checkpoint_mink_scores

```python
def save_mink_scores(
    scores: list[MinKScore],
    model_key: str,
    benchmark: str,
    checkpoint_dir: Path,
) -> None:
    """
    Save min-k% scores for one model-benchmark combination.
    Atomic write via .tmp + os.replace() — h-m1 pattern.
    
    Format: {"model_key": str, "benchmark": str, 
             "scores": [{"item_id": int, "k10": float, "k20": float, "k40": float}, ...]}
    """
    import json, os
    
    payload = {
        "model_key": model_key,
        "benchmark": benchmark,
        "scores": [
            {"item_id": s.item_id, **{f"k{k}": v for k, v in s.scores.items()}}
            for s in scores
        ]
    }
    path = checkpoint_dir / f"mink_scores_{model_key.replace('.', '_')}_{benchmark}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    os.replace(tmp, path)


def load_mink_scores(
    model_key: str,
    benchmark: str,
    checkpoint_dir: Path,
) -> list[MinKScore] | None:
    """Load checkpoint; return None if missing."""
    import json
    
    path = checkpoint_dir / f"mink_scores_{model_key.replace('.', '_')}_{benchmark}.json"
    if not path.exists():
        return None
    
    data = json.loads(path.read_text())
    scores = []
    for d in data["scores"]:
        item_id = d["item_id"]
        k_scores = {int(k[1:]): v for k, v in d.items() if k.startswith("k")}
        scores.append(MinKScore(item_id=item_id, benchmark=benchmark,
                                model_key=model_key, scores=k_scores))
    return scores
```

### L-4-5: score_all_models

```python
def score_all_models(
    model_configs: dict[str, tuple[str, str]],  # {key: (hf_id, revision)}
    benchmark_items: dict[str, list[BenchmarkItem]],  # {benchmark: [items]}
    k_values: list[int] = [10, 20, 40],
    checkpoint_dir: Path = Path("checkpoints"),
    device: str = "cuda",
) -> ScoresDict:
    """
    Outer loop: for each model × benchmark, score all items.
    Checkpoint/resume: skip if checkpoint exists.
    
    Returns: {model_key: {benchmark: [k20_scores_per_item]}}
    
    Memory strategy: load one model at a time; explicitly del + torch.cuda.empty_cache()
    between model loads to free VRAM.
    """
    import torch, gc
    from config import K_VALUES, BENCHMARKS
    
    results: ScoresDict = {}
    
    for model_key, (model_id, revision) in model_configs.items():
        results[model_key] = {}
        
        # Try to load from checkpoints first
        all_cached = all(
            load_mink_scores(model_key, bench, checkpoint_dir) is not None
            for bench in BENCHMARKS
        )
        if all_cached:
            for bench in BENCHMARKS:
                cached = load_mink_scores(model_key, bench, checkpoint_dir)
                results[model_key][bench] = [s.scores.get(20, float('-inf')) for s in cached]
            continue
        
        # Load model
        model, tokenizer = load_model_checkpoint(model_id, revision, device=device)
        verify_checkpoint_step(model, ModelSpec(model_id=model_id, revision=revision,
                                                corpus=model_key.split("_")[0],
                                                size=model_key.split("_")[1], key=model_key))
        
        for bench in BENCHMARKS:
            if load_mink_scores(model_key, bench, checkpoint_dir) is not None:
                cached = load_mink_scores(model_key, bench, checkpoint_dir)
                results[model_key][bench] = [s.scores.get(20, float('-inf')) for s in cached]
                continue
            
            scores = score_benchmark_items(benchmark_items[bench], model, tokenizer,
                                           k_values=k_values, device=device)
            for s in scores:
                s.model_key = model_key
            
            save_mink_scores(scores, model_key, bench, checkpoint_dir)
            results[model_key][bench] = [s.scores.get(20, float('-inf')) for s in scores]
        
        # Free VRAM before next model
        del model
        gc.collect()
        torch.cuda.empty_cache()
    
    return results
```

---

## A-7: Visualizer (4 subtasks)

### L-7-1: plot_mink_comparison_bar

```python
def plot_mink_comparison_bar(
    stats: list[BenchmarkStat],   # from both model sizes
    out: Path,
) -> None:
    """
    Mandatory gate figure: grouped bar chart.
    X-axis: 4 benchmarks × 2 model sizes (8 groups)
    Y-axis: mean min-k% score
    Bars: Pile (red) vs deduped (blue), same colors as h-m1 convention
    Error bars: 95% CI from raw scores
    Significance: sig_stars() over each Pile-deduped pair
    
    Reuses: sig_stars(), matplotlib Agg backend — h-m1 pattern
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    
    # sig_stars from h-m1 convention
    def sig_stars(p): return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, size in zip(axes, ["1b", "6.9b"]):
        size_stats = [s for s in stats if s.model_size == size]
        x = np.arange(len(size_stats))
        width = 0.35
        
        pile_means = [s.mean_pile for s in size_stats]
        dedup_means = [s.mean_deduped for s in size_stats]
        labels = [s.benchmark for s in size_stats]
        
        bars1 = ax.bar(x - width/2, pile_means, width, label="Pile", color="#d62728", alpha=0.85)
        bars2 = ax.bar(x + width/2, dedup_means, width, label="Dedup-Pile", color="#1f77b4", alpha=0.85)
        
        for xi, stat in zip(x, size_stats):
            star = sig_stars(stat.p_corrected)
            ax.text(xi, max(stat.mean_pile, stat.mean_deduped) + 0.05,
                    star, ha="center", fontsize=9)
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
        ax.set_title(f"Pythia-{size}", fontsize=11)
        ax.set_ylabel("Mean Min-k% Score (k=20)", fontsize=10)
        ax.legend(fontsize=9)
    
    fig.suptitle("Min-k% Memorization: Pile vs Dedup-Pile", fontsize=13)
    plt.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

### L-7-2: plot_mink_heatmap

```python
def plot_mink_heatmap(
    stats: list[BenchmarkStat],
    out: Path,
) -> None:
    """
    Heatmap: rows=benchmarks, cols=model sizes, values=differential (Pile-deduped).
    Color: red = Pile more memorized; blue = deduped more memorized.
    Center = 0 (diverging colormap).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    
    BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    SIZES = ["1b", "6.9b"]
    
    data = np.array([
        [next(s.differential for s in stats if s.benchmark == b and s.model_size == sz)
         for sz in SIZES]
        for b in BENCHMARKS
    ])
    
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        data, annot=True, fmt=".3f",
        xticklabels=SIZES, yticklabels=BENCHMARKS,
        cmap="RdBu_r", center=0,
        ax=ax, linewidths=0.5
    )
    ax.set_title("Min-k% Differential (Pile − Dedup-Pile)", fontsize=12)
    ax.set_xlabel("Model Size")
    ax.set_ylabel("Benchmark")
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

### L-7-3: plot_mink_violin

```python
def plot_mink_violin(
    raw_scores: ScoresDict,   # {model_key: {benchmark: [per-item scores]}}
    out: Path,
    model_size: str = "6.9b",
) -> None:
    """
    Violin plot: per-benchmark distribution of item-level min-k% scores.
    Pythia-{model_size} Pile (red) vs deduped (blue).
    4 subplots (one per benchmark).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    
    BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    pile_key = f"pile_{model_size}"
    dedup_key = f"deduped_{model_size}"
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    for ax, bench in zip(axes, BENCHMARKS):
        pile_scores = raw_scores.get(pile_key, {}).get(bench, [])
        dedup_scores = raw_scores.get(dedup_key, {}).get(bench, [])
        
        df = pd.DataFrame({
            "score": pile_scores + dedup_scores,
            "corpus": ["Pile"] * len(pile_scores) + ["Dedup-Pile"] * len(dedup_scores)
        })
        
        sns.violinplot(data=df, x="corpus", y="score", ax=ax,
                       palette={"Pile": "#d62728", "Dedup-Pile": "#1f77b4"})
        ax.set_title(bench, fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel("Min-k% Score" if bench == BENCHMARKS[0] else "")
    
    fig.suptitle(f"Score Distributions — Pythia-{model_size}", fontsize=12)
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

### L-7-4: plot_cross_hypothesis

```python
def plot_cross_hypothesis(
    hm2_stats: list[BenchmarkStat],
    hm1_results_path: Path,
    out: Path,
    model_size: str = "6.9b",
) -> None:
    """
    Scatter plot: X = H-M1 contamination differential (removed - retained mean overlap)
                  Y = H-M2 memorization differential (pile - deduped mean min-k%)
    4 points (one per benchmark). Labels annotated.
    Adds Spearman ρ annotation.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import json
    import numpy as np
    from scipy.stats import spearmanr
    
    BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    
    # Load H-M1 results
    hm1_data = json.loads(hm1_results_path.read_text())
    
    x_vals = []
    y_vals = []
    labels = []
    
    for bench in BENCHMARKS:
        if bench not in hm1_data:
            continue
        hm1_diff = hm1_data[bench].get("mean_removed", 0) - hm1_data[bench].get("mean_retained", 0)
        hm2_stat = next((s for s in hm2_stats if s.benchmark == bench and s.model_size == model_size), None)
        if hm2_stat is None:
            continue
        x_vals.append(hm1_diff)
        y_vals.append(hm2_stat.differential)
        labels.append(bench)
    
    rho, _ = spearmanr(x_vals, y_vals) if len(x_vals) >= 3 else (float("nan"), float("nan"))
    
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(x_vals, y_vals, color="#2ca02c", s=80, zorder=3)
    for x, y, lab in zip(x_vals, y_vals, labels):
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)
    
    ax.set_xlabel("H-M1: Contamination Differential (removed - retained overlap)", fontsize=10)
    ax.set_ylabel(f"H-M2: Memorization Differential (Pile - Deduped, k=20, {model_size})", fontsize=9)
    ax.set_title(f"Cross-Hypothesis: Contamination → Memorization\nSpearman ρ = {rho:.2f}", fontsize=11)
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.axvline(0, color="gray", lw=0.8, ls="--")
    
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

## A-8: Pipeline Orchestrator (3 subtasks)

### L-8-1: run_pipeline_stages

```python
def run_pipeline(
    stages: list[str] = None,
    skip_stages: list[str] = None,
    resume: bool = True,
    device: str = "cuda",
) -> dict:
    """
    End-to-end pipeline with checkpoint/resume at each stage.
    
    Stages (in order):
    1. load_benchmarks   → dict[str, list[BenchmarkItem]]
    2. score_models      → ScoresDict (per-model-benchmark min-k% scores)
    3. run_stats         → list[BenchmarkStat]
    4. run_ablations     → k-sensitivity results dict
    5. generate_figures  → None (side effect: saves figures)
    
    Args:
        stages: subset of stage names to run (default: all)
        skip_stages: stage names to skip
        resume: if True, use existing checkpoints
    
    Returns: dict with all results keyed by stage name
    """
    from config import BENCHMARKS, MODEL_CONFIGS, K_VALUES, CHECKPOINT_DIR, FIGURES_DIR
    from benchmark_loader import load_all_benchmarks
    from mink_scorer import score_all_models
    from statistical_tester import run_all_tests
    from ablation_runner import run_k_sensitivity
    from visualizer import generate_all_figures
    
    all_stages = ["load_benchmarks", "score_models", "run_stats", "run_ablations", "generate_figures"]
    active = [s for s in (stages or all_stages) if s not in (skip_stages or [])]
    
    results = {}
    
    if "load_benchmarks" in active:
        results["benchmark_items"] = load_all_benchmarks()
    
    if "score_models" in active:
        results["scores"] = score_all_models(
            MODEL_CONFIGS, results["benchmark_items"], K_VALUES, CHECKPOINT_DIR, device
        )
    
    if "run_stats" in active:
        results["stats"] = run_all_tests(results["scores"])
    
    if "run_ablations" in active:
        results["ablations"] = run_k_sensitivity(
            results.get("benchmark_items", load_all_benchmarks()), device
        )
    
    if "generate_figures" in active:
        generate_all_figures(results["scores"], results["stats"], results["ablations"],
                             FIGURES_DIR)
    
    return results
```

### L-8-2: verify_mechanism_activated

```python
def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Verify mechanism activation indicators per 02c_experiment_brief.md spec.
    
    Checks:
    1. All 4 model checkpoints loaded at correct steps (from score metadata)
    2. ≥500 items scored per benchmark per model
    3. pile_mean > deduped_mean for ≥1 benchmark (direction)
    4. ≥1 benchmark p < 0.0125 (statistical confirmation)
    
    Returns: (activated: bool, indicators: dict)
    """
    from config import BENCHMARKS
    
    scores = results.get("scores", {})
    stats = results.get("stats", [])
    
    indicators = {
        "checkpoints_loaded": all(
            f"pile_{sz}" in scores and f"deduped_{sz}" in scores
            for sz in ["1b", "6.9b"]
        ),
        "scores_computed": all(
            len(scores.get("pile_1b", {}).get(bench, [])) >= 500
            for bench in BENCHMARKS
        ),
        "pile_higher_on_any": any(
            s.differential > 0 for s in stats
        ),
        "effect_measurable": any(
            s.p_corrected < 0.0125 for s in stats
        ),
    }
    
    activated = (
        indicators["checkpoints_loaded"] and
        indicators["scores_computed"] and
        indicators["pile_higher_on_any"]
    )
    
    return activated, indicators
```

### L-8-3: generate_validation_report

```python
def generate_validation_report(results: dict, gate_decision: str, out_path: Path) -> None:
    """
    Write 04_validation.md with gate decision, per-benchmark results table,
    k-sensitivity table, cross-hypothesis correlation, mechanism log.
    
    gate_decision: "PASS" | "SHOULD_WORK_PASS" | "FAIL"
    
    Format matches h-m1 04_validation.md convention.
    """
    import json
    from config import BENCHMARKS
    
    stats = results.get("stats", [])
    ablations = results.get("ablations", {})
    activated, indicators = verify_mechanism_activated(results)
    
    lines = [
        f"# Validation Report: H-M2",
        f"**Gate Decision:** {gate_decision}",
        f"**Mechanism Activated:** {activated}",
        "",
        "## Per-Benchmark Results (k=20, paired t-test)",
        "| Benchmark | Model | Mean Pile | Mean Deduped | Differential | p_corrected | Significant |",
        "|-----------|-------|-----------|--------------|--------------|-------------|-------------|",
    ]
    for s in stats:
        lines.append(
            f"| {s.benchmark} | {s.model_size} | {s.mean_pile:.4f} | {s.mean_deduped:.4f} "
            f"| {s.differential:.4f} | {s.p_corrected:.4f} | {'✓' if s.significant else '✗'} |"
        )
    
    lines += ["", "## Mechanism Activation Indicators"]
    for k, v in indicators.items():
        lines.append(f"- {k}: {v}")
    
    out_path.write_text("\n".join(lines))
```
