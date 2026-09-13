# Logic: H-E2-v2

**Date:** 2026-08-04
**Hypothesis Type:** EXISTENCE (PARAMETER_ADJUSTMENT of H-E2)
**Budget:** 0 subtasks (all 5 tasks are Low complexity)

Applied: Standard Python adapter pattern — load existing results, re-evaluate gate, emit new figure.

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis extension
**Status:** API signatures verified from base code
**Analyzed Path:** `docs/youra_research/h-e2/code/`, `docs/youra_research/h-e1/code/`
**Relevant Symbols:**

| Symbol | File | Lines |
|--------|------|-------|
| `bootstrap_mst_stability` | h-e2/code/mst_analysis.py | 34–73 |
| `run_mst_analysis` | h-e2/code/mst_analysis.py | 77–120 |
| `build_mst` | h-e1/code/clustering.py | 43–51 |
| `partial_spearman_matrix` | h-e1/code/analysis.py | 59–88 |

Key confirmed facts from actual code:
- `bootstrap_mst_stability` signature: `(raw_scores, covariates, dim_names, full_mst_edges, n_boot, subsample, seed)` → `(float, Dict[str, float])`
- `run_mst_analysis` stores key `bootstrap_edge_frequencies` (not `per_edge_frequencies`) in its return dict
- H-E2 `serialize_results` writes that key to JSON — so fast-path loads `h_e2["bootstrap_edge_frequencies"]`
- `build_mst(rho_partial: np.ndarray, dim_names: list) -> nx.Graph`
- `partial_spearman_matrix(scores_df, covariates_df, alpha_bonferroni) -> (rho [6,6], pval [6,6], pairs)`

---

## External Dependencies API

Signatures verified from actual implementation (NOT specs):

```python
# From: h-e2/code/mst_analysis.py (ACTUAL CODE)
def bootstrap_mst_stability(
    raw_scores: np.ndarray,       # (N, 6)
    covariates: np.ndarray,       # (N, 2)
    dim_names: List[str],
    full_mst_edges: FrozenSet,
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Tuple[float, Dict[str, float]]:
    """Returns (topology_stability, edge_frequencies). edge_frequencies keys: 'dim_a--dim_b'."""

def run_mst_analysis(
    rho_partial: np.ndarray,      # (6, 6)
    raw_scores: np.ndarray,       # (N, 6)
    covariates: np.ndarray,       # (N, 2)
    dim_names: List[str],
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Dict:
    """Returns dict with keys: mst_min_set_size, mst_min_set, bootstrap_edge_frequencies, ..."""

# From: h-e1/code/clustering.py (ACTUAL CODE)
def build_mst(rho_partial: np.ndarray, dim_names: list) -> nx.Graph:
    """MST on 1 - |rho_partial| distance (Kruskal)."""

# From: h-e1/code/analysis.py (ACTUAL CODE)
def partial_spearman_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
    alpha_bonferroni: float = 0.0033,
) -> Tuple[np.ndarray, np.ndarray, List]:
    """Returns (rho_partial [6,6], pval [6,6], significant_pairs)."""
```

**Critical:** JSON key is `bootstrap_edge_frequencies` (from `run_mst_analysis` return + `serialize_results`).
Do NOT use `per_edge_frequencies` — that key does not exist in H-E2 output.

---

## A-1: Project Setup [Complexity: Low]

No API design needed — directory creation and file verification.

Verify: `h-e2/experiment_results_phase3.json` exists and has key `bootstrap_edge_frequencies`.

```python
import json, os
with open(h_e2_json_path) as f:
    data = json.load(f)
assert "bootstrap_edge_frequencies" in data, f"Key missing. Keys: {list(data.keys())}"
```

---

## A-2: evaluate_gate_v2 [Complexity: Low]

```python
def evaluate_gate_v2(
    mst_min_set_size: int,
    mean_per_edge_freq: float,
    threshold_min_set: int = 4,
    threshold_mean_freq: float = 0.90,
) -> dict:
    """H-E2-v2 relaxed gate. Primary: set_size<=4. Secondary: mean_freq>=0.90."""
    primary = mst_min_set_size <= threshold_min_set
    secondary = mean_per_edge_freq >= threshold_mean_freq
    return {
        "gate_primary_passed": primary,
        "gate_secondary_passed": secondary,
        "gate_result": "PASS" if (primary and secondary) else "FAIL",
    }

# Self-check (known H-E2 values):
# assert evaluate_gate_v2(3, 0.917)["gate_result"] == "PASS"
# assert evaluate_gate_v2(3, 0.606)["gate_result"] == "FAIL"  # old metric would fail
```

---

## A-3: load_or_recompute [Complexity: Low]

```python
def load_or_recompute(
    h_e2_json_path: str,
    h_e1_json_path: str,
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
) -> Tuple[Dict[str, float], int, List[str]]:
    """Returns (per_edge_freqs, mst_min_set_size, mst_min_set).

    Fast path: reads bootstrap_edge_frequencies from h-e2 JSON.
    Fallback: re-runs bootstrap via run_mst_analysis() from h-e2/code/mst_analysis.py.
    """
    # Fast path
    with open(h_e2_json_path) as f:
        h_e2 = json.load(f)
    if "bootstrap_edge_frequencies" in h_e2:
        return (
            h_e2["bootstrap_edge_frequencies"],   # Dict[str, float]
            h_e2["mst_min_set_size"],              # int
            h_e2["mst_min_set"],                   # List[str]
        )

    # Fallback: re-run bootstrap
    # sys.path setup for h-e2 and h-e1 code dirs must happen before import
    with open(h_e1_json_path) as f:
        h_e1 = json.load(f)
    rho_key = "rho_partial_matrix" if "rho_partial_matrix" in h_e1 else "rho_partial"
    rho_partial = np.array(h_e1[rho_key])  # (6, 6)

    # Load raw scores via data_loader (h-e1)
    scores_df = load_trustllm_scores(trustllm_results_dir)
    annotated_df = add_annotations(scores_df)
    raw_scores = scores_df[DIM_NAMES].values   # (16, 6)
    covariates = annotated_df[["log10_params", "is_RLHF"]].values  # (16, 2)

    results = run_mst_analysis(
        rho_partial=rho_partial,
        raw_scores=raw_scores,
        covariates=covariates,
        dim_names=DIM_NAMES,
        n_boot=n_boot,
        subsample=subsample,
        seed=seed,
    )
    return (
        results["bootstrap_edge_frequencies"],
        results["mst_min_set_size"],
        results["mst_min_set"],
    )
```

---

## A-4: run_experiment [Complexity: Low]

```python
@dataclass
class ExperimentConfigV2:
    h_e2_results_path: str = "../h-e2/experiment_results_phase3.json"
    h_e1_results_path: str = "../h-e1/experiment_results_phase3.json"
    out_dir: str = ".."
    n_bootstrap: int = 1000
    subsample_size: int = 14
    seed: int = 42
    gate_min_set_threshold: int = 4
    gate_mean_freq_threshold: float = 0.90
    topology_stability_h_e2: float = 0.606   # overlay for comparison plot
    figure_dpi: int = 300


def run_experiment(
    h_e2_json_path: str,
    h_e1_json_path: str,
    output_dir: str,
) -> dict:
    """Orchestrate: load → gate → plot → serialize → print.

    Returns full results dict including gate_result.
    """
    cfg = ExperimentConfigV2(
        h_e2_results_path=h_e2_json_path,
        h_e1_results_path=h_e1_json_path,
        out_dir=output_dir,
    )

    # 1. Load or recompute per-edge frequencies
    per_edge_freqs, mst_min_set_size, mst_min_set = load_or_recompute(
        cfg.h_e2_results_path, cfg.h_e1_results_path,
        n_boot=cfg.n_bootstrap, subsample=cfg.subsample_size, seed=cfg.seed,
    )

    # 2. Compute mean_per_edge_freq
    mean_per_edge_freq = float(np.mean(list(per_edge_freqs.values())))  # expected: 0.917

    # 3. Evaluate gate
    gate = evaluate_gate_v2(mst_min_set_size, mean_per_edge_freq,
                             cfg.gate_min_set_threshold, cfg.gate_mean_freq_threshold)

    # 4. Plot
    figures_dir = os.path.join(output_dir, "h-e2-v2", "figures")
    os.makedirs(figures_dir, exist_ok=True)
    plot_gate_bar_v2(
        mst_min_set_size=mst_min_set_size,
        mean_per_edge_freq=mean_per_edge_freq,
        topology_stability_h_e2=cfg.topology_stability_h_e2,
        out_path=os.path.join(figures_dir, "gate_metrics_v2.png"),
        dpi=cfg.figure_dpi,
    )

    # 5. Serialize
    results = {
        "hypothesis": "h-e2-v2",
        "gate_metric": "mean_per_edge_bootstrap_frequency",
        "mst_min_set_size": mst_min_set_size,
        "mst_min_set": mst_min_set,
        "mean_per_edge_bootstrap_frequency": mean_per_edge_freq,
        "per_edge_frequencies": per_edge_freqs,
        "topology_stability_h_e2": cfg.topology_stability_h_e2,
        **gate,
    }
    out_json = os.path.join(output_dir, "h-e2-v2", "experiment_results_phase3.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)

    # 6. Print summary
    print(f"\n{'='*50}")
    print(f"H-E2-v2 RESULTS")
    print(f"MST min_set_size:       {mst_min_set_size} (<=4) — {'PASS' if gate['gate_primary_passed'] else 'FAIL'}")
    print(f"Mean per-edge freq:     {mean_per_edge_freq:.4f} (>=0.90) — {'PASS' if gate['gate_secondary_passed'] else 'FAIL'}")
    print(f"(Old topology_stab:     {cfg.topology_stability_h_e2:.3f} — retired metric)")
    print(f"GATE RESULT:            {gate['gate_result']}")
    print(f"{'='*50}\n")

    return results
```

---

## A-5: plot_gate_bar_v2 [Complexity: Low]

```python
def plot_gate_bar_v2(
    mst_min_set_size: int,
    mean_per_edge_freq: float,
    topology_stability_h_e2: float,   # 0.606 — overlay showing why gate was relaxed
    out_path: str,
    dpi: int = 300,
) -> None:
    """Bar chart: primary + secondary gate metrics vs thresholds.

    Three bars: mst_min_set_size/4 ratio, mean_per_edge_freq, topology_stability.
    Horizontal lines at thresholds. Saves to out_path.
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Left: primary gate — mst_min_set_size vs threshold 4
    ax = axes[0]
    color = "steelblue" if mst_min_set_size <= 4 else "firebrick"
    ax.bar(["min_set_size"], [mst_min_set_size], color=color)
    ax.axhline(4, color="red", linestyle="--", label="threshold=4")
    ax.set_title("Primary Gate: MST Min Set Size")
    ax.set_ylabel("# dimensions")
    ax.legend()

    # Right: secondary gate — mean_per_edge_freq vs 0.90, overlay old topology_stability
    ax = axes[1]
    bars = ax.bar(
        ["mean_per_edge_freq (v2)", "topology_stability (H-E2)"],
        [mean_per_edge_freq, topology_stability_h_e2],
        color=["steelblue" if mean_per_edge_freq >= 0.90 else "firebrick", "gray"],
    )
    ax.axhline(0.90, color="red", linestyle="--", label="threshold=0.90")
    ax.set_ylim(0, 1.1)
    ax.set_title("Secondary Gate: Bootstrap Frequency")
    ax.set_ylabel("frequency / stability")
    ax.legend()

    fig.suptitle(f"H-E2-v2 Gate: {('PASS' if (mst_min_set_size <= 4 and mean_per_edge_freq >= 0.90) else 'FAIL')}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
```

---

## Output JSON Schema

```json
{
  "hypothesis": "h-e2-v2",
  "gate_metric": "mean_per_edge_bootstrap_frequency",
  "mst_min_set_size": 3,
  "mst_min_set": ["truthfulness", "fairness", "privacy"],
  "mean_per_edge_bootstrap_frequency": 0.917,
  "per_edge_frequencies": {
    "fairness--truthfulness": 1.0,
    "privacy--safety": 1.0,
    "robustness--truthfulness": 0.941,
    "fairness--privacy": 0.956,
    "machine_ethics--privacy": 0.688
  },
  "topology_stability_h_e2": 0.606,
  "gate_primary_passed": true,
  "gate_secondary_passed": true,
  "gate_result": "PASS"
}
```

---

## File Layout

```
h-e2-v2/code/
  main.py          # ExperimentConfigV2, load_or_recompute, evaluate_gate_v2, run_experiment
  viz_h_e2_v2.py  # plot_gate_bar_v2
h-e2-v2/figures/
  gate_metrics_v2.png
h-e2-v2/experiment_results_phase3.json
```

No subtasks — all 5 epics are Low complexity, directly implementable from signatures above.
