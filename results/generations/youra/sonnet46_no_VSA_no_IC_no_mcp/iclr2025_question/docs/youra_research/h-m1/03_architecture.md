---
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: "2026-08-25"
author: yoon303@ust.ac.kr
base_hypothesis: H-E1
---

# Architecture: H-M1 — Paraphrase Token Entropy Variance Analysis

Applied: analysis-on-cached-outputs, fallback-rerun-pattern, cluster-variance-decomposition

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-E1)
**Status**: patterns found from base code (direct file reads)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- H-E1 code is flat (5 files): `data.py`, `compute_te.py`, `compute_se.py`, `evaluate.py`, `run.py`
- NLI model used: `cross-encoder/nli-deberta-v3-large` (not `deberta-large-mnli` as spec states — trust code)
- Results saved as `.npy` + `.json` to `docs/youra_research/h-e1/results/`; cluster assignments are NOT individually persisted as a separate file — they are recomputed by `compute_se.py` via `compute_se_scores()` at runtime
- Per-sample logprobs not saved to disk — `te_scores.npy` saves scalar TE per question, not per-sample TE; implies H-M1 needs per-sample TE recomputed from h-e2-v2 cache (`samples_map[qid]["te_score"]` is scalar) or from Llama-2-7B re-inference
- `data.py:load_h_e2v2_samples()` + `get_pilot_questions()` are the data entry points

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_h_e2v2_samples | `from h_e1_code.data import load_h_e2v2_samples` | `h-e1/code/data.py` |
| get_pilot_questions | `from h_e1_code.data import get_pilot_questions` | `h-e1/code/data.py` |
| load_nli_model | `from h_e1_code.compute_se import load_nli_model` | `h-e1/code/compute_se.py` |
| compute_se_scores | `from h_e1_code.compute_se import compute_se_scores` | `h-e1/code/compute_se.py` |
| load_llama / compute_te_scores | `from h_e1_code.compute_te import load_llama, compute_te_scores` | `h-e1/code/compute_te.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Critical note**: H-E1 saves per-question scalar TE (`te_scores.npy`) and per-question scalar SE (`se_scores.npy`). It does NOT save per-sample TE or cluster assignments to disk. H-M1 needs per-sample TE values and cluster assignments. These must be recomputed:
- Per-sample TE: rerun `compute_te_scores` with per-sample output, OR use `samples_map[qid]["te_score"]` if h-e2-v2 stores them per sample
- Cluster assignments: rerun `compute_se_scores` capturing intermediate cluster dicts

---

## File Organization

```
docs/youra_research/h-m1/code/
  cache_loader.py     # load H-E1 outputs; recompute per-sample TE + clusters if missing
  analysis.py         # intra/inter-cluster variance computation + eligibility filter
  evaluate.py         # verify_mechanism_activated(), secondary metrics, results save
  visualize.py        # all figures → h-m1/figures/
  run.py              # orchestrator: cache_loader → analysis → evaluate → visualize

docs/youra_research/h-m1/results/   # h_m1_results.json, h_m1_summary.json, experiment.log
docs/youra_research/h-m1/figures/   # all PNGs
```

---

## Module Structure

### CacheLoader (`code/cache_loader.py`)

**Dependencies**: h-e1 data.py, h-e1 compute_te.py, h-e1 compute_se.py

```python
def load_or_recompute(
    he1_results_dir: str,        # "docs/youra_research/h-e1/results/"
    he1_code_dir: str,           # "docs/youra_research/h-e1/code/"
    samples_path: str | None,    # h-e2-v2 JSONL path; None = auto-detect
    n: int = 98,
    seed: int = 42,
    nli_model_id: str = "cross-encoder/nli-deberta-v3-large",
    nli_device: int = 0,
) -> dict:
    """
    Returns:
      {
        "questions": list[dict],               # 98 question records
        "samples_map": dict,                   # qid -> h-e2-v2 record
        "per_sample_te": dict[str, list[float]],  # qid -> [te_0..te_9]
        "cluster_assignments": dict[str, dict[int, int]],  # qid -> {sample_idx: cluster_id}
        "correctness": list[int],
        "se_scores": list[float],
      }
    """
    ...

def _check_he1_cache(he1_results_dir: str) -> dict:
    """Check which files exist: te_scores.npy, se_scores.npy, correctness.npy, results.json."""
    ...
```

### Analysis (`code/analysis.py`)

**Dependencies**: numpy, collections.defaultdict

```python
def filter_eligible_questions(
    questions: list[dict],
    cluster_assignments: dict[str, dict[int, int]],
) -> list[str]:
    """Return question IDs with ≥1 NLI cluster containing ≥2 samples."""
    ...

def compute_intra_cluster_variance(
    cluster_assignments: dict[int, int],  # {sample_idx: cluster_id}
    per_sample_te: list[float],           # [te_0..te_9]
) -> float | None:
    """Mean variance across multi-member clusters; None if no pairs."""
    ...

def compute_inter_cluster_variance(
    cluster_assignments: dict[int, int],
    per_sample_te: list[float],
) -> float | None:
    """Variance across cluster means (between-cluster control)."""
    ...

def run_analysis(
    questions: list[dict],
    cluster_assignments: dict[str, dict[int, int]],
    per_sample_te: dict[str, list[float]],
    se_scores: list[float],
) -> list[dict]:
    """
    Per-question result dicts:
      {qid, n_clusters, n_multi_member_clusters, mean_intra_var,
       inter_var, has_paraphrase, se_score, high_uncertainty}
    """
    ...
```

### Evaluate (`code/evaluate.py`)

**Dependencies**: numpy, scipy.stats, json, logging

```python
def verify_mechanism_activated(results: list[dict]) -> tuple[bool, dict]:
    """
    Primary gate: mean_intra_cluster_variance > 0.1 nats on ≥15/20 eligible questions.
    Returns (primary_pass, indicators_dict).
    """
    ...

def compute_secondary_metrics(results: list[dict]) -> dict:
    """NLI clustering accuracy proxy, threshold sensitivity table, high/low SE stratum comparison."""
    ...

def save_results(
    results: list[dict],
    indicators: dict,
    secondary: dict,
    primary_pass: bool,
    out_dir: str,
) -> None:
    """Writes h_m1_results.json, h_m1_summary.json."""
    ...
```

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_all(
    results: list[dict],
    indicators: dict,
    figures_dir: str,
) -> None:
    """
    Generates:
      fig1_gate_bar.png          — mean intra-cluster var vs 0.1 nats threshold (MANDATORY)
      fig2_violin_intra_var.png  — per-question variance distribution
      fig3_scatter_size_var.png  — cluster size vs TE variance
      fig4_nli_heatmap.png       — pairwise entailment matrix (3 representative questions)
      fig5_threshold_sensitivity.png — fraction passing at {0.05, 0.1, 0.2, 0.5} nats
    """
    ...
```

### Run (`code/run.py`)

**Dependencies**: cache_loader, analysis, evaluate, visualize, argparse, logging

```python
CONFIG = {
    "he1_results_dir": "docs/youra_research/h-e1/results/",
    "he1_code_dir": "docs/youra_research/h-e1/code/",
    "nli_model_id": "cross-encoder/nli-deberta-v3-large",
    "nli_device": 0,
    "n": 98,
    "seed": 42,
    "out_dir": "docs/youra_research/h-m1/results/",
    "figures_dir": "docs/youra_research/h-m1/figures/",
    "intra_var_threshold": 0.1,
    "min_passing_questions": 15,
    "min_eligible_questions": 20,
}

def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & cache probe | Create project structure; implement `_check_he1_cache()` to detect which H-E1 outputs exist; determine whether per-sample TE and cluster assignments need recomputation | 7 | 2+1+2+2 |
| A-2 | Per-sample TE recomputation | Implement `load_or_recompute()` path that re-runs `compute_te_scores` in per-sample mode (or extracts from h-e2-v2 cache) and re-runs `compute_se_scores` capturing cluster assignment dicts | 14 | 3+4+4+3 |
| A-3 | Eligibility filter | Implement `filter_eligible_questions()` identifying questions with ≥1 multi-member NLI cluster; assert ≥20 eligible; log count | 6 | 1+1+2+2 |
| A-4 | Variance computation | Implement `compute_intra_cluster_variance()` and `compute_inter_cluster_variance()`; run `run_analysis()` over all 98 questions; attach SE stratum flag | 9 | 2+2+3+2 |
| A-5 | Gate verification | Implement `verify_mechanism_activated()` with primary gate (≥15/20 at 0.1 nats), secondary metrics, threshold sensitivity table; `save_results()` | 10 | 2+2+3+3 |
| A-6 | Visualization | Implement all 5 figures in `plot_all()`; mandatory gate bar chart + 4 diagnostic plots | 9 | 2+2+2+3 |
| A-7 | Orchestration & smoke test | Wire `run.py`; add `--smoke-test` (N=5); add `--skip-recompute` flag to load cached per-sample data; write `__main__` self-check asserting no crash | 8 | 2+2+2+2 |

**Distribution**: High(14-17): [A-2], Medium(9-13): [A-4, A-5, A-6], Low(4-8): [A-1, A-3, A-7]

---

## Design Notes

**Per-sample TE gap**: H-E1 `te_scores.npy` stores one scalar per question (not per sample). H-M1 needs 10 scalars per question. A-2 must either: (a) check if h-e2-v2 JSONL stores per-sample logprobs and compute TE from those, or (b) re-run Llama-2-7B inference. Check path (a) first — zero GPU cost.

**Cluster assignment gap**: `compute_se_scores()` in H-E1 returns `(se_scores, avg_clusters)` — it does not return the raw cluster dicts. A-2 must modify or wrap `compute_se_scores` to also return `{qid: {sample_idx: cluster_id}}`.

**NLI model**: Actual H-E1 code uses `cross-encoder/nli-deberta-v3-large` (not `deberta-large-mnli`). Use same model for consistency.
