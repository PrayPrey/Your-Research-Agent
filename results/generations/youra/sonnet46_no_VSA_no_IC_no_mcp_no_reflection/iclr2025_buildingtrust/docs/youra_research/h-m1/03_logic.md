# H-M1 Logic: Post-hoc Statistical Analysis of H-E1 Benchmark Scores

**Green-field project — designing new APIs**

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 results consumed as data)
**Status**: H-E1 results verified from `h-e1/experiment_results.json` and `h-e1/code/model_pairs.json`
**Analyzed Path**: `docs/youra_research/h-e1/`
**Relevant Symbols**: `experiment_results.json` (model_scores dict), `model_pairs.json` (6-pair registry)

---

## Algorithm Walkthrough

```
Step 1: Load scores
  data = json.load("h-e1/experiment_results.json")
  scores = data["model_scores"]                  # dict of 12 model entries
  pairs  = json.load("h-e1/code/model_pairs.json")  # list of 6 pair dicts

  Fallback (if file missing): embed scores as inline dict in run_hm1.py

Step 2: Compute per-pair deltas for each benchmark
  BENCHMARKS = ["bbq", "winogender_all", "winogrande", "truthfulqa_mc2"]
  for each pair (sft_key, dpo_key):
      delta[bench] = scores[dpo_key][bench] - scores[sft_key][bench]
  # delta arrays shape: [6] per benchmark

Step 3: Count k = number of positive deltas
  k[bench] = sum(d > 0 for d in delta[bench])   # ties (d==0) -> NOT DPO>SFT

Step 4: One-sided binomial test (per benchmark)
  from scipy.stats import binomtest
  result = binomtest(k[bench], n=6, p=0.5, alternative='greater')
  p_value[bench] = result.pvalue

Step 5: Fisher criterion (signal-to-noise, all 4 benchmarks)
  fisher[bench] = mean(delta[bench])**2 / (var(delta[bench]) + 1e-8)

Step 6: Gate check
  gate_pass = (k["bbq"] >= 4) AND (p_value["bbq"] <= 0.125)
  verdict   = "PASS" if gate_pass else "FAIL"
```

---

## Implementation Pseudocode: `run_hm1.py`

```python
# --- Inline fallback data (edit keys to match experiment_results.json) ---
INLINE_SCORES = {
    # key format matches experiment_results.json model_scores keys
    "mistralai-Mistral-7B-Instruct-v0.1":  {"bbq": 0.43, "winogender_all": 0.55, "winogrande": 0.75, "truthfulqa_mc2": 0.5588},
    "HuggingFaceH4-zephyr-7b-alpha":        {"bbq": 0.38, "winogender_all": 0.65, "winogrande": 0.73, "truthfulqa_mc2": 0.5492},
    "teknium-OpenHermes-2.5-Mistral-7B":    {"bbq": 0.45, "winogender_all": 0.71, "winogrande": 0.74, "truthfulqa_mc2": 0.4916},
    "HuggingFaceH4-zephyr-7b-beta":         {"bbq": 0.39, "winogender_all": 0.65, "winogrande": 0.69, "truthfulqa_mc2": 0.5140},
    "allenai-tulu-2-7b":                    {"bbq": 0.45, "winogender_all": 0.63, "winogrande": 0.71, "truthfulqa_mc2": 0.4815},
    "allenai-tulu-2-dpo-7b":                {"bbq": 0.47, "winogender_all": 0.63, "winogrande": 0.71, "truthfulqa_mc2": 0.5782},
    "meta-llama-Llama-2-7b-chat-hf":        {"bbq": 0.42, "winogender_all": 0.66, "winogrande": 0.70, "truthfulqa_mc2": 0.4954},
    "Intel-neural-chat-7b-v3-1":            {"bbq": 0.47, "winogender_all": 0.67, "winogrande": 0.76, "truthfulqa_mc2": 0.5924},
    "openchat-openchat_3.5":                {"bbq": 0.48, "winogender_all": 0.67, "winogrande": 0.77, "truthfulqa_mc2": 0.4469},
    "berkeley-nest-Starling-LM-7B-alpha":   {"bbq": 0.48, "winogender_all": 0.69, "winogrande": 0.77, "truthfulqa_mc2": 0.4373},
    "mistralai-Mistral-7B-Instruct-v0.3":   {"bbq": 0.40, "winogender_all": 0.63, "winogrande": 0.76, "truthfulqa_mc2": 0.5591},
    "Intel-neural-chat-7b-v3-3":            {"bbq": 0.47, "winogender_all": 0.65, "winogrande": 0.73, "truthfulqa_mc2": 0.6382},
}

PAIRS = [
    ("mistralai-Mistral-7B-Instruct-v0.1",  "HuggingFaceH4-zephyr-7b-alpha"),
    ("teknium-OpenHermes-2.5-Mistral-7B",    "HuggingFaceH4-zephyr-7b-beta"),
    ("allenai-tulu-2-7b",                    "allenai-tulu-2-dpo-7b"),
    ("meta-llama-Llama-2-7b-chat-hf",        "Intel-neural-chat-7b-v3-1"),
    ("openchat-openchat_3.5",                "berkeley-nest-Starling-LM-7B-alpha"),
    ("mistralai-Mistral-7B-Instruct-v0.3",   "Intel-neural-chat-7b-v3-3"),
]

BENCHMARKS = ["bbq", "winogender_all", "winogrande", "truthfulqa_mc2"]


def load_scores(results_path: str) -> dict:
    """Load model_scores from H-E1 results JSON, fallback to INLINE_SCORES."""
    try:
        with open(results_path) as f:
            return json.load(f)["model_scores"]
    except (FileNotFoundError, KeyError):
        print("WARNING: H-E1 results not found, using inline fallback.")
        return INLINE_SCORES


def compute_deltas(scores: dict, pairs: list, benchmarks: list) -> dict:
    """delta[bench] -> np.ndarray shape [6]"""
    deltas = {b: [] for b in benchmarks}
    for sft_key, dpo_key in pairs:
        for b in benchmarks:
            d = scores[dpo_key][b] - scores[sft_key][b]
            deltas[b].append(d)
    return {b: np.array(v) for b, v in deltas.items()}


def run_stats(deltas: dict) -> dict:
    """Returns per-benchmark stats dict."""
    results = {}
    for bench, d in deltas.items():            # d shape: [6]
        k = int(np.sum(d > 0))                 # ties excluded
        binom = binomtest(k, n=6, p=0.5, alternative='greater')
        results[bench] = {
            "deltas": d.tolist(),              # [6]
            "k_positive": k,
            "mean_delta": float(np.mean(d)),
            "std_delta": float(np.std(d, ddof=1)),
            "p_value": float(binom.pvalue),
            "fisher": float(np.mean(d)**2 / (np.var(d, ddof=1) + 1e-8)),
        }
    return results


def gate_check(stats: dict, k_thr: int = 4, p_thr: float = 0.125) -> dict:
    """Returns gate verdict dict."""
    k = stats["bbq"]["k_positive"]
    p = stats["bbq"]["p_value"]
    return {
        "k_bbq": k, "p_bbq": p,
        "k_pass": k >= k_thr, "p_pass": p <= p_thr,
        "gate_pass": (k >= k_thr) and (p <= p_thr),
    }


def save_results(stats: dict, gate: dict, out_path: str):
    """Dump stats + gate to JSON."""
    out = {"benchmark_stats": stats, "gate": gate}
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)


def main():
    scores  = load_scores(HE1_RESULTS_PATH)
    deltas  = compute_deltas(scores, PAIRS, BENCHMARKS)
    stats   = run_stats(deltas)
    gate    = gate_check(stats)
    save_results(stats, gate, RESULTS_OUT_PATH)
    make_figures(deltas, stats, gate, FIGURES_DIR)
    print(f"Gate: {'PASS' if gate['gate_pass'] else 'FAIL'}")
    print(f"  k_BBQ={gate['k_bbq']}/6, p_BBQ={gate['p_bbq']:.4f}")
```

---

## Figure Generation Logic

Four figures required (matplotlib, no external plot libs).

### Fig 1: Per-pair delta bar chart (BBQ and WinoGender side-by-side)
```python
# fig1_delta_bars.png
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, bench in zip(axes, ["bbq", "winogender_all"]):
    d = deltas[bench]                          # [6]
    colors = ["tab:blue" if v > 0 else "tab:red" for v in d]
    ax.bar(range(6), d, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(bench); ax.set_xlabel("Pair index")
    ax.set_ylabel("DPO - SFT score")
```

### Fig 2: Scatter plot DPO score vs SFT score (BBQ)
```python
# fig2_scatter_bbq.png  — one point per pair
sft_scores = [scores[s]["bbq"] for s, _ in PAIRS]  # [6]
dpo_scores = [scores[d]["bbq"] for _, d in PAIRS]  # [6]
plt.scatter(sft_scores, dpo_scores)
plt.plot([0.3, 0.6], [0.3, 0.6], "k--")            # diagonal
plt.xlabel("SFT BBQ"); plt.ylabel("DPO BBQ")
```

### Fig 3: Fisher criterion bar chart (all 4 benchmarks)
```python
# fig3_fisher.png
benchmarks = list(stats.keys())
fishers = [stats[b]["fisher"] for b in benchmarks]
plt.bar(benchmarks, fishers)
plt.ylabel("Fisher criterion (mean^2 / var)")
```

### Fig 4: Summary table as heatmap (k and p per benchmark)
```python
# fig4_summary_table.png
# Rows: benchmarks; Cols: k_positive, p_value
# Use plt.table() or imshow on a 4x2 array
data = np.array([[stats[b]["k_positive"], stats[b]["p_value"]] for b in BENCHMARKS])
plt.imshow(data, aspect="auto", cmap="RdYlGn")
plt.xticks([0, 1], ["k_positive", "p_value"])
plt.yticks(range(4), BENCHMARKS)
plt.colorbar()
```

---

## Tensor / Array Shapes

| Variable | Shape | Type |
|----------|-------|------|
| `deltas[bench]` | `[6]` | `np.float64` |
| `sft_scores` / `dpo_scores` | `[6]` | `list[float]` |
| `k_positive` | scalar | `int` |
| `p_value` | scalar | `float` |
| `fisher` | scalar | `float` |

---

## Statistical Interpretation

- **k_BBQ >= 4/6**: majority of pairs show DPO advantage on BBQ (bias QA). Under H0 (p=0.5), P(k>=4|n=6) = 0.344; gate threshold 0.125 tightens this.
- **p_BBQ <= 0.125**: one-sided binomial p-value. Not standard 0.05 — set looser because n=6 is small and exact binomial is discrete (minimum achievable p at k=5 is 0.109, k=6 is 0.016).
- **Fisher criterion**: captures effect size relative to within-pair variance. High fisher = consistent directional effect. Reported per benchmark, not used in gate.
- **WinoGender**: secondary benchmark; reported but not in gate. Corroborates BBQ finding on gender-bias axis.

---

## Edge Cases

| Case | Handling |
|------|----------|
| `delta == 0` (tie) | Counts as NOT DPO>SFT (`d > 0` strict) |
| Missing model key in scores | `KeyError` raised early in `compute_deltas`; fix: check all 12 keys present before proceeding |
| H-E1 results file absent | `load_scores` falls back to `INLINE_SCORES`; logs WARNING |
| All deltas same sign | `var=0`, fisher denominator guarded by `+1e-8` |
