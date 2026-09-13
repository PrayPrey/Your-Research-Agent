# Logic: H-M1 (MECHANISM)

Applied: no KB match for KS test (diffusion-only results, ignored) — scipy.stats standard implementation used.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual h-e1 code (not spec — signatures differ from 02c_experiment_brief.md pseudo-code).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `data.py::load_truthfulqa_mc`, `data.py::assign_clusters`, `model.py::load_model_and_tokenizer`, `model.py::score_choices`, `model.py::predict`

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/data.py (ACTUAL CODE)
def load_truthfulqa_mc() -> "Dataset":
    """Loads TruthfulQA MC split merged with category from generation split."""

def assign_clusters(dataset: "Dataset") -> "Dataset":
    """Adds cluster_id column (1-7) via CATEGORY_TO_CLUSTER substring match; default 7."""

# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
def load_model_and_tokenizer(model_id: str, device: str) -> tuple:
    """Returns (model, tokenizer)."""

def score_choices(model, tokenizer, question: str, choices: list[str], device) -> list[float]:
    """Returns per-choice log-likelihood scores, len == len(choices)."""

def predict(
    question: str,
    choices: list[str],
    correct_idx: int,
    model,
    tokenizer,
    device,
    cluster_id: int,
) -> dict:
    """Runs score_choices + softmax. Returns:
    {confidence: float, correct: bool, cluster_id: int, predicted_idx: int, correct_idx: int}
    """
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation via Serena)

**Note**: `predict()` positional order is `(question, choices, correct_idx, model, tokenizer, device, cluster_id)` — the experiment brief's pseudo-code (`logits_by_cluster`-based) does NOT match. Call `predict()` per-question as shown below, not via raw logits dict.

---

## M-1/M-2/M-3: Data + Inference Wiring (train.py)

```python
def run_inference(dataset, model, tokenizer, device) -> list[dict]:
    """Iterate dataset rows, call predict() per question. Returns list of predict() dicts."""
    records = []
    for ex in dataset:
        choices = ex["mc1_targets"]["choices"]          # list[str], len K
        correct_idx = ex["mc1_targets"]["labels"].index(1)
        record = predict(
            ex["question"], choices, correct_idx,
            model, tokenizer, device, ex["cluster_id"],
        )
        records.append(record)
    return records
```

Note: `mc1_targets` field names per TruthfulQA HF schema (`choices: list[str]`, `labels: list[int]` one-hot). Verify against actual dataset schema at runtime; adjust key names if HF dataset version differs — not verifiable via Serena (external dataset).

### Cluster validation (M-2)

```python
def validate_min_cluster_size(dataset, min_size: int = 100) -> None:
    """Raise ValueError if any of 7 clusters has < min_size examples."""
    from collections import Counter
    counts = Counter(dataset["cluster_id"])
    missing = [c for c in range(1, 8) if counts.get(c, 0) < min_size]
    if missing:
        raise ValueError(f"Clusters below min_size={min_size}: {missing}")
```

---

## M-4: KS Test Module (ks_analysis.py)

```python
def extract_cluster_confidences(records: list[dict]) -> dict[int, "np.ndarray"]:
    """Group confidence values by cluster_id. records from run_inference()."""
    from collections import defaultdict
    import numpy as np
    grouped = defaultdict(list)
    for r in records:
        grouped[r["cluster_id"]].append(r["confidence"])
    return {c: np.array(v) for c, v in grouped.items()}


def pairwise_ks_tests(cluster_confidences: dict[int, "np.ndarray"]) -> dict[tuple[int, int], dict]:
    """ks_2samp for all C(7,2)=21 pairs. Returns {(c1,c2): {statistic, pvalue}}."""
    from itertools import combinations
    from scipy.stats import ks_2samp
    cluster_ids = sorted(cluster_confidences.keys())
    results = {}
    for c1, c2 in combinations(cluster_ids, 2):
        stat, pvalue = ks_2samp(cluster_confidences[c1], cluster_confidences[c2], alternative="two-sided")
        results[(c1, c2)] = {"statistic": float(stat), "pvalue": float(pvalue)}
    return results


def evaluate_gate_condition(ks_results: dict) -> tuple[bool, int, int]:
    """Pass if >=11 of 21 pairs have p < 0.05. Returns (gate_passed, significant_count, total_pairs)."""
    total = len(ks_results)  # 21
    significant = sum(1 for r in ks_results.values() if r["pvalue"] < 0.05)
    return significant >= 11, significant, total


def cluster_mean_std(cluster_confidences: dict[int, "np.ndarray"]) -> dict[int, dict]:
    """Per-cluster mean/std. Also compute range = max(mean) - min(mean) for secondary metric."""
    import numpy as np
    stats = {c: {"mean": float(np.mean(v)), "std": float(np.std(v)), "n": len(v)}
              for c, v in cluster_confidences.items()}
    means = [s["mean"] for s in stats.values()]
    stats["_range"] = max(means) - min(means)
    return stats
```

### Pseudo-code: pairwise KS loop (non-trivial part = pair indexing)

```
cluster_ids = sorted(keys)                 # [1..7]
for (c1, c2) in combinations(cluster_ids, 2):   # 21 pairs
    D, p = ks_2samp(conf[c1], conf[c2])
    results[(c1,c2)] = {D, p}
gate_pass = count(p < 0.05 for results) >= 11
```

---

## M-6/M-7: Visualization (train.py)

```python
def plot_ks_heatmap(ks_results: dict, cluster_ids: list[int], path: str) -> None:
    """7x7 symmetric p-value heatmap, diagonal=NaN, annotate significant cells (p<0.05)."""

def plot_confidence_histograms(cluster_confidences: dict[int, "np.ndarray"], path: str) -> None:
    """7 overlaid histograms, alpha=0.5, legend=cluster names."""

def plot_confidence_boxplot(cluster_confidences: dict[int, "np.ndarray"], path: str) -> None:
    """Box plot, x=cluster, y=confidence."""

def plot_cdf_comparison(cluster_confidences: dict[int, "np.ndarray"], path: str) -> None:
    """Empirical CDF per cluster via np.sort + np.arange(1,n+1)/n, one line per cluster."""
```

Tensor/array shapes:

| Variable | Shape/Type | Note |
|----------|------------|------|
| cluster_confidences[c] | np.ndarray [n_c] | n_c ~100-150 |
| ks_results | dict, 21 keys | key=(c1,c2) tuple |
| pvalue_matrix (heatmap) | [7,7] | symmetric, diag=NaN |

---

## M-8/M-9: Results + Entry Point (train.py)

```python
def save_results_json(results: dict, path: str) -> None:
    """json.dump({gate_passed, significant_count, total_pairs, ks_results, cluster_stats}, indent=2)."""

def save_validation_md(gate_pass: bool, results: dict, path: str) -> None:
    """Write 04_validation.md: gate decision, stats table, figure links."""

def main():
    """
    1. dataset = load_truthfulqa_mc(); dataset = assign_clusters(dataset)
    2. validate_min_cluster_size(dataset, MIN_CLUSTER_SIZE)
    3. model, tok = load_model_and_tokenizer(MODEL_ID, device)
    4. records = run_inference(dataset, model, tok, device)
    5. cluster_conf = extract_cluster_confidences(records)
    6. ks_results = pairwise_ks_tests(cluster_conf)
    7. gate_pass, sig, total = evaluate_gate_condition(ks_results)
    8. stats = cluster_mean_std(cluster_conf)
    9. plot_ks_heatmap / histograms / boxplot / cdf -> FIGURES_DIR
    10. save_results_json(...); save_validation_md(gate_pass, ..., VALIDATION_MD)
    """
```

---

## Self-Check
- No ASCII diagrams; KB search logged as 1 line.
- Docstrings <=2 lines.
- Tensor/array shapes in comments/table.
- Codebase Analysis (Serena) section included, base_hypothesis scenario, mandatory call done.
- Signature mismatch (predict() arg order vs brief pseudo-code) explicitly flagged.
- Total length ~180 lines, within budget.
