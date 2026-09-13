# Logic: H-M4 — Step-Matched vs Token-Count-Matched Robustness Check

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M4 (MECHANISM — robustness check extending H-M3)

Applied: scipy.stats pearsonr/spearmanr correlation pattern
Applied: bootstrap resampling CI pattern (numpy random state)
Applied: lm-evaluation-harness simple_evaluate programmatic API pattern
Applied: matplotlib subplot 2-panel scatter pattern

---

## Codebase Analysis (Serena)

**Project Type:** incremental extension of H-M3
**Status:** No H-M4 code/ exists yet; H-M3 code/ also not implemented — green-field
**Analyzed path:** `docs/youra_research/h-m3/03_logic.md` (reference for interface conventions)
**Findings:** H-M3 defines correlation/visualization patterns with numpy float arrays of shape (16,) for 4 benchmarks × 4 model sizes. H-M4 inherits this convention exactly and adds a second condition dimension. No Serena code analysis possible (no source files exist).

---

## B-2: Eval Runner — Step-Matched Condition [Complexity: 12, Budget: 4 subtasks]

### L-2-1: Checkpoint Download + Verification

```python
def verify_checkpoint_pair(
    pile_step: int,
    dedup_step: int,
    condition: str,  # "step_matched" | "token_matched"
    pile_tps: float = 244e9 / 143000,
    dedup_tps: float = 207e9 / 143000,
) -> bool:
    """
    Verify checkpoint pair satisfies expected token ratio.
    Raises AssertionError with diagnostic message on failure.

    Returns: True if verified
    """
    pile_tokens = pile_step * pile_tps
    dedup_tokens = dedup_step * dedup_tps
    token_ratio = pile_tokens / dedup_tokens  # shape: scalar

    if condition == "step_matched":
        # step_matched: same step → Pile has ~15% more tokens
        assert pile_step == dedup_step, (
            f"Step-matched requires equal steps: pile={pile_step}, dedup={dedup_step}"
        )
        assert 1.10 < token_ratio < 1.20, (
            f"Expected token_ratio in [1.10, 1.20] for step_matched, got {token_ratio:.4f}"
        )
        print(f"STEP_MATCHED_VERIFIED: pile=step{pile_step}, dedup=step{dedup_step}, "
              f"token_ratio={token_ratio:.4f}")
    elif condition == "token_matched":
        # token_matched: Pile step chosen so cumulative tokens ≈ dedup tokens
        assert abs(token_ratio - 1.0) < 0.03, (
            f"Expected token_ratio ≈ 1.0 ±3% for token_matched, got {token_ratio:.4f}"
        )
        print(f"TOKEN_MATCHED_VERIFIED: pile=step{pile_step}, dedup=step{dedup_step}, "
              f"token_ratio={token_ratio:.4f}")
    else:
        raise ValueError(f"Unknown condition: {condition!r}")

    return True


def download_checkpoint(
    model_id: str,
    revision: str,
    cache_dir: str,
) -> str:
    """
    Pre-download checkpoint to local cache using huggingface_hub.
    Returns local cache path.

    model_id: e.g. "EleutherAI/pythia-1b"
    revision: e.g. "step143000"
    """
    from huggingface_hub import snapshot_download
    local_path = snapshot_download(
        repo_id=model_id,
        revision=revision,
        cache_dir=cache_dir,
    )
    return local_path
```

**Data shapes:** None (scalar token ratio check; string paths)

---

### L-2-2: lm_eval.simple_evaluate Wrapper

```python
def run_model(
    model_id: str,          # e.g. "EleutherAI/pythia-1b"
    revision: str,          # e.g. "step143000"
    benchmarks: list[str],  # e.g. ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
    num_fewshot: dict[str, int],  # {benchmark: n_shots}
    out_path: str,          # JSON output path
    device: str = "cuda",
    dtype: str = "float16",
    batch_size: int = 1,
) -> dict:
    """
    Run lm-evaluation-harness evaluation for one model checkpoint.
    Saves raw results JSON to out_path.

    Returns: raw results dict with structure:
      {
        "results": {
          benchmark: {
            "acc,none": float,        # for mmlu, winogrande
            "acc_norm,none": float,   # for hellaswag, arc_challenge
          }
        }
      }
    """
    import lm_eval
    results = lm_eval.simple_evaluate(
        model="hf",
        model_args=f"pretrained={model_id},revision={revision},dtype={dtype}",
        tasks=benchmarks,
        num_fewshot=[num_fewshot[b] for b in benchmarks],
        device=device,
        batch_size=batch_size,
    )
    import json, pathlib
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    return results
```

**Data shapes:**
- Input: model_id (str), revision (str)
- Output results dict: `results["results"][benchmark]["acc,none"]` → scalar float

---

### L-2-3: Differential Extraction

```python
ACC_KEYS: dict[str, str] = {
    "mmlu": "acc,none",
    "hellaswag": "acc_norm,none",
    "arc_challenge": "acc_norm,none",
    "winogrande": "acc,none",
}

def extract_accuracy(
    results: dict,
    benchmark: str,
) -> float:
    """Extract scalar accuracy from lm-eval results dict."""
    return results["results"][benchmark][ACC_KEYS[benchmark]]


def compute_differentials(
    pile_results: dict,     # raw lm-eval output for Pile model
    dedup_results: dict,    # raw lm-eval output for dedup-Pile model
    benchmarks: list[str],
) -> dict[str, float]:
    """
    Compute per-benchmark accuracy differential: dedup_acc - pile_acc.

    Returns: {benchmark: float}
      e.g. {"mmlu": -0.021, "hellaswag": -0.015, "arc_challenge": -0.008, "winogrande": 0.003}
    """
    return {
        b: extract_accuracy(dedup_results, b) - extract_accuracy(pile_results, b)
        for b in benchmarks
    }
```

**Data shapes:** Output dict shape: 4 keys → scalar floats

---

### L-2-4: Batch Runner for All Model Sizes

```python
def run_step_matched_condition(
    model_sizes: list[str],     # ["160m", "410m", "1b", "6.9b"]
    benchmarks: list[str],
    num_fewshot: dict[str, int],
    cache_dir: str,
    out_dir: str,               # e.g. "docs/youra_research/h-m4/results/"
    step: int = 143000,
    device: str = "cuda",
    dtype: str = "float16",
) -> dict[str, dict[str, float]]:
    """
    For each model size, evaluate Pile and dedup-Pile at step=143000.
    Verifies checkpoint pairs before evaluation.

    Returns: {
      model_size: {benchmark: differential}  # dedup_acc - pile_acc
    }  shape: {4 sizes: {4 benchmarks: float}}
    """
    import pathlib
    result_dir = pathlib.Path(out_dir)
    differentials = {}

    for size in model_sizes:
        pile_id   = f"EleutherAI/pythia-{size}"
        dedup_id  = f"EleutherAI/pythia-{size}-deduped"
        revision  = f"step{step}"

        # Verify pair before evaluation
        verify_checkpoint_pair(step, step, "step_matched")

        pile_out  = str(result_dir / f"step_matched_{size}_pile.json")
        dedup_out = str(result_dir / f"step_matched_{size}_dedup.json")

        pile_res  = run_model(pile_id,  revision, benchmarks, num_fewshot, pile_out,  device, dtype)
        dedup_res = run_model(dedup_id, revision, benchmarks, num_fewshot, dedup_out, device, dtype)

        differentials[size] = compute_differentials(pile_res, dedup_res, benchmarks)

    return differentials
```

**Data shapes:** Output: `dict[str, dict[str, float]]` — 4 sizes × 4 benchmarks = 16 scalar values total

---

## B-4: Comparative Analysis [Complexity: 11, Budget: 3 subtasks]

### L-4-1: Pearson/Spearman for Both Conditions

```python
import numpy as np
from scipy.stats import pearsonr, spearmanr

def build_vectors(
    differentials: dict[str, dict[str, float]],
    contamination_estimates: dict[str, float],
    model_sizes: list[str],
    benchmarks: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Flatten 4 benchmarks × 4 model sizes into correlation vectors.

    Returns:
      cont_vec:  shape (16,) — contamination estimate repeated per model size
      diff_vec:  shape (16,) — accuracy differential (dedup - pile)

    Order: benchmarks vary fastest (size0_bench0, size0_bench1, ..., size3_bench3)
    """
    cont_vec = np.array([
        contamination_estimates[b]
        for size in model_sizes
        for b in benchmarks
    ])  # shape: (16,)

    diff_vec = np.array([
        differentials[size][b]
        for size in model_sizes
        for b in benchmarks
    ])  # shape: (16,)

    return cont_vec, diff_vec


def compute_correlations(
    cont_vec: np.ndarray,   # shape (16,)
    diff_vec: np.ndarray,   # shape (16,)
) -> dict:
    """
    Returns: {
      "pearson_r": float, "pearson_p": float,
      "spearman_r": float, "spearman_p": float,
      "n": int
    }
    """
    r_p, p_p = pearsonr(cont_vec, diff_vec)
    r_s, p_s = spearmanr(cont_vec, diff_vec)
    return {
        "pearson_r": float(r_p),
        "pearson_p": float(p_p),
        "spearman_r": float(r_s),
        "spearman_p": float(p_s),
        "n": len(cont_vec),
    }


def run_comparison(
    token_matched_diffs: dict[str, dict[str, float]],
    step_matched_diffs: dict[str, dict[str, float]],
    contamination_estimates: dict[str, float],
    model_sizes: list[str],
    benchmarks: list[str],
) -> dict:
    """
    Compute full comparison metrics for both conditions.

    Returns: {
      "token_matched": {pearson_r, pearson_p, spearman_r, spearman_p, n},
      "step_matched":  {pearson_r, pearson_p, spearman_r, spearman_p, n},
      "delta_r":       float,  # r_token - r_step (positive = token_matched stronger)
      "uniform_bias_token": float,  # mean(all token_matched differentials)
      "uniform_bias_step":  float,  # mean(all step_matched differentials)
      "bias_delta":    float,  # bias_step - bias_token (negative = step_matched more negative)
    }
    """
    cont_t, diff_t = build_vectors(token_matched_diffs, contamination_estimates, model_sizes, benchmarks)
    cont_s, diff_s = build_vectors(step_matched_diffs,  contamination_estimates, model_sizes, benchmarks)

    stats_t = compute_correlations(cont_t, diff_t)
    stats_s = compute_correlations(cont_s, diff_s)

    return {
        "token_matched": stats_t,
        "step_matched":  stats_s,
        "delta_r":             stats_t["pearson_r"] - stats_s["pearson_r"],
        "uniform_bias_token":  float(np.mean(diff_t)),
        "uniform_bias_step":   float(np.mean(diff_s)),
        "bias_delta":          float(np.mean(diff_s) - np.mean(diff_t)),
    }
```

**Data shapes:** cont_vec/diff_vec: `(16,)` float64; all correlation outputs: scalar floats

---

### L-4-2: Bootstrap CI Computation

```python
def bootstrap_ci(
    cont_vec: np.ndarray,       # shape (16,)
    diff_vec: np.ndarray,       # shape (16,)
    n_iterations: int = 10000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Compute bootstrap confidence interval for Pearson r.
    Resamples (cont, diff) pairs with replacement.

    Returns: (lower_bound, upper_bound) at ci_level
    """
    rng = np.random.default_rng(seed)
    n = len(cont_vec)
    bootstrapped_r = np.empty(n_iterations, dtype=np.float64)  # shape: (n_iterations,)

    for i in range(n_iterations):
        idx = rng.integers(0, n, size=n)   # shape: (n,)
        r, _ = pearsonr(cont_vec[idx], diff_vec[idx])
        bootstrapped_r[i] = r

    alpha = 1.0 - ci_level
    lower = float(np.percentile(bootstrapped_r, 100 * alpha / 2))
    upper = float(np.percentile(bootstrapped_r, 100 * (1 - alpha / 2)))
    return lower, upper


def compute_all_cis(
    token_matched_diffs: dict,
    step_matched_diffs: dict,
    contamination_estimates: dict,
    model_sizes: list[str],
    benchmarks: list[str],
    n_iterations: int = 10000,
    seed: int = 42,
) -> dict:
    """
    Returns: {
      "ci_token_matched": (lower, upper),
      "ci_step_matched":  (lower, upper),
    }
    """
    cont_t, diff_t = build_vectors(token_matched_diffs, contamination_estimates, model_sizes, benchmarks)
    cont_s, diff_s = build_vectors(step_matched_diffs,  contamination_estimates, model_sizes, benchmarks)

    ci_t = bootstrap_ci(cont_t, diff_t, n_iterations=n_iterations, seed=seed)
    ci_s = bootstrap_ci(cont_s, diff_s, n_iterations=n_iterations, seed=seed)
    return {"ci_token_matched": ci_t, "ci_step_matched": ci_s}
```

**Data shapes:** bootstrapped_r: `(10000,)` float64; CI outputs: tuple of 2 scalars

---

### L-4-3: Gate Verdict + Metrics Export

```python
def determine_gate(
    delta_r: float,        # r_token_matched - r_step_matched
    bias_delta: float,     # uniform_bias_step - uniform_bias_token
    delta_r_threshold: float = 0.05,
    bias_delta_threshold: float = 0.01,
) -> str:
    """
    Returns one of:
      "PASS" — both criteria met (volume confound confirmed)
      "ROBUSTNESS_CONFIRMATION" — no difference (confound negligible)
      "PARTIAL" — one criterion met
    """
    primary_met   = delta_r > 0
    secondary_met = bias_delta < 0

    if abs(delta_r) < delta_r_threshold and abs(bias_delta) < bias_delta_threshold:
        return "ROBUSTNESS_CONFIRMATION"
    if primary_met and secondary_met:
        return "PASS"
    return "PARTIAL"


def export_gate_verdict(
    comparison: dict,
    cis: dict,
    gate_verdict: str,
    out_path: str,
) -> None:
    """
    Writes gate_verdict.json with all metrics.

    Output JSON schema:
    {
      "hypothesis": "h-m4",
      "gate_type": "SHOULD_WORK",
      "gate_verdict": str,
      "token_matched": {pearson_r, pearson_p, spearman_r, spearman_p, ci_lower, ci_upper},
      "step_matched":  {pearson_r, pearson_p, spearman_r, spearman_p, ci_lower, ci_upper},
      "delta_r": float,
      "uniform_bias_token": float,
      "uniform_bias_step": float,
      "bias_delta": float,
    }
    """
    import json, pathlib
    record = {
        "hypothesis": "h-m4",
        "gate_type": "SHOULD_WORK",
        "gate_verdict": gate_verdict,
        "token_matched": {
            **comparison["token_matched"],
            "ci_lower": cis["ci_token_matched"][0],
            "ci_upper": cis["ci_token_matched"][1],
        },
        "step_matched": {
            **comparison["step_matched"],
            "ci_lower": cis["ci_step_matched"][0],
            "ci_upper": cis["ci_step_matched"][1],
        },
        "delta_r":             comparison["delta_r"],
        "uniform_bias_token":  comparison["uniform_bias_token"],
        "uniform_bias_step":   comparison["uniform_bias_step"],
        "bias_delta":          comparison["bias_delta"],
    }
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
```

---

## B-5: Visualization [Complexity: 12, Budget: 4 subtasks]

### L-5-1: fig_01 — Correlation Comparison Bar Chart (MANDATORY)

```python
def plot_correlation_comparison_bar(
    r_token: float,
    r_step: float,
    ci_token: tuple[float, float],   # (lower, upper)
    ci_step: tuple[float, float],    # (lower, upper)
    out_path: str,
    figsize: tuple[int, int] = (6, 5),
) -> None:
    """
    Bar chart: r_token_matched vs r_step_matched with 95% CI error bars.

    Error bar = asymmetric: lower_err = r - ci_lower, upper_err = ci_upper - r
    """
    import matplotlib.pyplot as plt
    import numpy as np

    labels = ["Token-count\nmatched (H-M3)", "Step-matched\n(H-M4)"]
    rs     = [r_token, r_step]
    yerr_lower = [r_token - ci_token[0], r_step - ci_step[0]]
    yerr_upper = [ci_token[1] - r_token,  ci_step[1] - r_step]
    yerr = [yerr_lower, yerr_upper]   # shape: (2, 2)

    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(labels))
    bars = ax.bar(x, rs, yerr=yerr, capsize=6, color=["steelblue", "coral"],
                  ecolor="black", alpha=0.85)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Pearson r (contamination vs accuracy differential)", fontsize=10)
    ax.set_title("H-M4: Correlation Strength by Checkpoint-Matching Method", fontsize=12)
    ax.set_ylim(-0.1, 1.0)

    for bar, r_val in zip(bars, rs):
        ax.text(bar.get_x() + bar.get_width() / 2, r_val + 0.02,
                f"r={r_val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

### L-5-2: fig_02 — Scatter Two-Panel

```python
def plot_scatter_two_panel(
    cont_est: dict[str, float],              # {benchmark: float}
    token_diffs: dict[str, dict[str, float]], # {size: {benchmark: float}}
    step_diffs: dict[str, dict[str, float]],
    r_token: float,
    r_step: float,
    model_sizes: list[str],
    benchmarks: list[str],
    out_path: str,
    figsize: tuple[int, int] = (12, 5),
) -> None:
    """
    2-panel scatter: contamination estimate vs accuracy differential.
    Left panel: token-count-matched; right panel: step-matched.
    Each point = one (benchmark, model_size) pair; regression line + CI band.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import pearsonr

    fig, axes = plt.subplots(1, 2, figsize=figsize, sharey=False)
    titles  = ["Token-count-matched (H-M3)", "Step-matched (H-M4)"]
    diffs_l = [token_diffs, step_diffs]
    rs      = [r_token, r_step]

    MARKERS = ["o", "s", "^", "D"]
    COLORS  = ["steelblue", "darkorange", "green", "purple"]

    for ax, title, diffs, r_val in zip(axes, titles, diffs_l, rs):
        for i, size in enumerate(model_sizes):
            xs = [cont_est[b] for b in benchmarks]
            ys = [diffs[size][b] for b in benchmarks]
            ax.scatter(xs, ys, marker=MARKERS[i], color=COLORS[i],
                       label=f"pythia-{size}", s=60, zorder=3)

        # Regression line
        all_x = np.array([cont_est[b] for s in model_sizes for b in benchmarks])
        all_y = np.array([diffs[s][b]  for s in model_sizes for b in benchmarks])
        m, b_int = np.polyfit(all_x, all_y, 1)
        x_line   = np.linspace(all_x.min(), all_x.max(), 100)
        ax.plot(x_line, m * x_line + b_int, color="black", linewidth=1.5, label="OLS fit")
        ax.axhline(0, color="gray", linewidth=0.7, linestyle="--")
        ax.set_xlabel("Contamination overlap estimate", fontsize=10)
        ax.set_ylabel("Accuracy differential (dedup − Pile)", fontsize=10)
        ax.set_title(f"{title}\nr={r_val:.3f}", fontsize=11)
        ax.legend(fontsize=8, loc="upper right")

    fig.suptitle("H-M4: Contamination vs Accuracy Differential by Matching Method", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

### L-5-3: fig_03 — Per-Benchmark Differential Bar Chart

```python
def plot_differential_bar_chart(
    token_diffs: dict[str, dict[str, float]],
    step_diffs: dict[str, dict[str, float]],
    model_sizes: list[str],
    benchmarks: list[str],
    out_path: str,
    figsize: tuple[int, int] = (14, 6),
) -> None:
    """
    Grouped bar chart: per-benchmark accuracy differentials, side-by-side
    token-matched vs step-matched, across 4 model sizes.

    Layout: x-axis = benchmarks (4 groups), each group has 8 bars
    (4 model sizes × 2 conditions). Color encodes condition; hatch encodes size.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    n_bench   = len(benchmarks)
    n_sizes   = len(model_sizes)
    n_cond    = 2   # token_matched, step_matched
    bar_width = 0.09
    x         = np.arange(n_bench)

    fig, ax = plt.subplots(figsize=figsize)
    COLORS   = ["steelblue", "coral"]
    HATCHES  = ["", "/", "x", "\\"]
    COND_LABELS = ["Token-matched", "Step-matched"]

    for ci, (cond_diffs, cond_label, color) in enumerate(
        zip([token_diffs, step_diffs], COND_LABELS, COLORS)
    ):
        for si, size in enumerate(model_sizes):
            offset = (ci * n_sizes + si - (n_cond * n_sizes - 1) / 2) * bar_width
            vals   = [cond_diffs[size][b] for b in benchmarks]
            ax.bar(x + offset, vals, bar_width, label=f"{cond_label} {size}",
                   color=color, hatch=HATCHES[si], alpha=0.8)

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("_", "\n") for b in benchmarks], fontsize=10)
    ax.set_ylabel("Accuracy differential (dedup − Pile)", fontsize=10)
    ax.set_title("H-M4: Per-Benchmark Differentials by Matching Condition and Model Size", fontsize=11)
    ax.legend(fontsize=7, ncol=4, loc="lower right")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

### L-5-4: fig_04 + fig_05 — Bias Decomposition + Summary Table

```python
def plot_bias_decomposition(
    token_diffs: dict[str, dict[str, float]],
    step_diffs: dict[str, dict[str, float]],
    model_sizes: list[str],
    benchmarks: list[str],
    out_path: str,
    figsize: tuple[int, int] = (8, 5),
) -> None:
    """
    Per model size: stacked/grouped bars showing
    (a) volume bias = mean(step_diff) - mean(token_diff) [uniform downward shift]
    (b) contamination component = mean(token_diff) [H-M3 baseline]
    """
    import matplotlib.pyplot as plt
    import numpy as np

    volume_bias   = []
    cont_baseline = []
    for size in model_sizes:
        mean_token = np.mean([token_diffs[size][b] for b in benchmarks])
        mean_step  = np.mean([step_diffs[size][b]  for b in benchmarks])
        cont_baseline.append(float(mean_token))
        volume_bias.append(float(mean_step - mean_token))

    x = np.arange(len(model_sizes))
    width = 0.35

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x - width/2, cont_baseline, width, label="Contamination component (token-matched mean diff)", color="steelblue", alpha=0.85)
    ax.bar(x + width/2, volume_bias,   width, label="Volume bias (step - token mean diff)", color="coral", alpha=0.85)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([f"pythia-{s}" for s in model_sizes], fontsize=10)
    ax.set_ylabel("Mean accuracy differential", fontsize=10)
    ax.set_title("H-M4: Bias Decomposition by Model Size", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_correlation_summary_table(
    comparison: dict,
    cis: dict,
    out_path: str,
    figsize: tuple[int, int] = (10, 3),
) -> None:
    """
    Renders a matplotlib table with r, ρ, p-values, 95% CI for both conditions + delta_r.
    """
    import matplotlib.pyplot as plt

    tm = comparison["token_matched"]
    sm = comparison["step_matched"]
    rows = [
        ["Token-count-matched (H-M3)",
         f"{tm['pearson_r']:.3f}", f"{tm['pearson_p']:.4f}",
         f"{tm['spearman_r']:.3f}", f"{tm['spearman_p']:.4f}",
         f"[{cis['ci_token_matched'][0]:.3f}, {cis['ci_token_matched'][1]:.3f}]"],
        ["Step-matched (H-M4)",
         f"{sm['pearson_r']:.3f}", f"{sm['pearson_p']:.4f}",
         f"{sm['spearman_r']:.3f}", f"{sm['spearman_p']:.4f}",
         f"[{cis['ci_step_matched'][0]:.3f}, {cis['ci_step_matched'][1]:.3f}]"],
        ["Δ (token − step)",
         f"{comparison['delta_r']:.3f}", "—", "—", "—", "—"],
    ]
    col_labels = ["Condition", "Pearson r", "p (Pearson)", "Spearman ρ", "p (Spearman)", "95% CI (Pearson)"]

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=col_labels, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.8)
    ax.set_title("H-M4: Correlation Summary — Token-count-matched vs Step-matched", fontsize=11, pad=20)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

## External Dependencies API

| Module | Function | Source |
|--------|----------|--------|
| `lm_eval.simple_evaluate` | Programmatic evaluation | EleutherAI/lm-evaluation-harness |
| `scipy.stats.pearsonr(x, y)` | Returns `(r: float, p: float)` | scipy ≥1.10 |
| `scipy.stats.spearmanr(x, y)` | Returns `SpearmanrResult(statistic, pvalue)` | scipy ≥1.10 |
| `numpy.random.default_rng(seed).integers(0, n, size=n)` | Bootstrap resampling | numpy ≥1.24 |
| `huggingface_hub.snapshot_download(repo_id, revision, cache_dir)` | Checkpoint pre-download | huggingface_hub ≥0.19 |
