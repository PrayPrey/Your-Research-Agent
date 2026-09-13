---
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: "2026-08-25"
author: yoon303@ust.ac.kr
base_hypothesis: H-E1
---

# Logic Design: H-M1 — Paraphrase Token Entropy Variance Analysis

Applied: analysis-on-cached-outputs, fallback-rerun-pattern, variance-decomposition, per-sample-recompute-wrapper

---

## Codebase Analysis (Serena)

**Analyzed**: `docs/youra_research/h-e1/code/` (direct file reads)

### Functions Found (Actual Code)

| Function | File | Signature |
|----------|------|-----------|
| `load_llama` | `compute_te.py:8` | `(model_id="meta-llama/Llama-2-7b-hf", hf_token=None) -> (model, tokenizer)` |
| `compute_single_te` | `compute_te.py:23` | `(question_text: str, model, tokenizer, max_new_tokens=50) -> float` |
| `compute_te_scores` | `compute_te.py:53` | `(questions: list, model, tokenizer) -> list[float]` — **one scalar per question** |
| `load_nli_model` | `compute_se.py:7` | `(model_id="cross-encoder/nli-deberta-v3-large", device=0) -> pipeline` |
| `get_semantic_ids` | `compute_se.py:71` | `(strings_list: list, nli_pipeline) -> list[int]` — cluster id per sample |
| `compute_se_scores` | `compute_se.py:124` | `(questions, samples_map, nli_pipeline) -> (list[float], float)` — returns `(se_scores, avg_clusters)` only; **does NOT return cluster dicts** |
| `load_h_e2v2_samples` | `data.py` | `() -> (questions, samples_map)` |
| `get_pilot_questions` | `data.py` | `(samples_map, n=98, seed=42) -> list[dict]` |

### Critical Gaps for H-M1

1. **`compute_te_scores` returns per-question scalar** — H-M1 needs per-sample TE (10 scalars/question). Must write `compute_per_sample_te()` wrapper.
2. **`compute_se_scores` does not return cluster assignments dict** — H-M1 needs `{sample_idx: cluster_id}` per question. Must write `compute_cluster_assignments()` wrapper around `get_semantic_ids`.
3. **NLI model**: actual code uses `cross-encoder/nli-deberta-v3-large` — not `deberta-large-mnli` as stated in spec. Use actual model.
4. **H-E1 results**: `te_scores.npy` = one float/question; `se_scores.npy` = one float/question; no per-sample outputs saved to disk.

---

## External Dependencies API

All signatures verified from `docs/youra_research/h-e1/code/` actual implementation.

### From `h-e1/code/data.py`

```python
def load_h_e2v2_samples() -> tuple[list[dict], dict]:
    """
    Returns:
      questions: list of question dicts with keys:
        - "question_id": str
        - "question": str
        - "answer": list[str]  (gold answers)
      samples_map: dict[question_id -> {
        "samples": list[str],   # K generated text answers
        "log_probs": list[float],  # per-sample log-prob (scalar)
      }]
    NOTE: log_probs are per-sample sequence log-probs, NOT per-token.
    """

def get_pilot_questions(
    samples_map: dict,
    n: int = 98,
    seed: int = 42,
) -> list[dict]:
    """Subsample n questions from samples_map keys. Returns list of question dicts."""
```

### From `h-e1/code/compute_te.py`

```python
def load_llama(
    model_id: str = "meta-llama/Llama-2-7b-hf",
    hf_token: str = None,             # fallback: os.environ["HF_TOKEN"]
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load Llama-2-7B float16 with device_map=auto."""

def compute_single_te(
    question_text: str,
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    max_new_tokens: int = 50,
) -> float:
    """
    Greedy decode with output_scores=True.
    Computes mean per-token Shannon entropy over generated tokens.
    Returns scalar float (nats).
    NOTE: uses greedy decode (do_sample=False) — not stochastic samples.
    """

def compute_te_scores(
    questions: list[dict],            # list with "question" key
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
) -> list[float]:
    """Returns list[float] len=N — ONE scalar TE per question (greedy)."""
```

### From `h-e1/code/compute_se.py`

```python
def load_nli_model(
    model_id: str = "cross-encoder/nli-deberta-v3-large",  # ACTUAL model from code
    device: int = 0,
) -> pipeline:
    """Returns HuggingFace zero-shot-classification pipeline."""

def get_semantic_ids(
    strings_list: list[str],     # K sample texts for one question
    nli_pipeline,
) -> list[int]:
    """
    Bidirectional NLI entailment clustering (Kuhn et al. 2023).
    Returns cluster_ids: list[int] len=K — one cluster id per sample.
    Threshold: entailment_score > 0.5 for both directions.
    """

def compute_se_scores(
    questions: list[dict],
    samples_map: dict,
    nli_pipeline,
) -> tuple[list[float], float]:
    """
    Returns (se_scores: list[float], avg_clusters: float).
    Does NOT return cluster_assignments — wrapping required for H-M1.
    """
```

---

## Module API Specifications

### Module 1: `cache_loader.py`

```python
def load_or_recompute(
    he1_results_dir: str,
    he1_code_dir: str,
    samples_path: str | None = None,
    n: int = 98,
    seed: int = 42,
    nli_model_id: str = "cross-encoder/nli-deberta-v3-large",
    nli_device: int = 0,
) -> dict:
    """
    Returns dict with keys:
      "questions":           list[dict]                          # 98 question records
      "samples_map":         dict[str, dict]                     # qid -> {samples, log_probs}
      "per_sample_te":       dict[str, list[float]]             # qid -> [te_0..te_K-1]
      "cluster_assignments": dict[str, dict[int, int]]          # qid -> {sample_idx: cluster_id}
      "correctness":         list[int]                           # binary EM per question
      "se_scores":           list[float]                         # SE per question

    Logic:
      1. Load questions + samples_map via load_h_e2v2_samples() + get_pilot_questions()
      2. Load se_scores from he1_results_dir/se_scores.npy if exists
      3. Call compute_per_sample_te() — extracts from samples_map log_probs (fast path)
      4. Call compute_cluster_assignments() — re-runs get_semantic_ids per question
      5. Load correctness from he1_results_dir/correctness.npy
    """

def _check_he1_cache(he1_results_dir: str) -> dict[str, bool]:
    """
    Returns dict of which npy/json files exist:
      {"te_scores": bool, "se_scores": bool, "correctness": bool, "results_json": bool}
    """

def compute_per_sample_te(
    questions: list[dict],
    samples_map: dict,
    model=None,
    tokenizer=None,
) -> dict[str, list[float]]:
    """
    Fast path: compute TE for each of the K samples per question using compute_single_te.
    samples_map[qid]["samples"] provides the K text strings.
    Falls back to Llama inference only if model is provided and samples need TE.

    Returns: dict[qid -> list[float]] len=K per question.

    Pseudo-code:
      per_sample_te = {}
      for q in questions:
          qid = q["question_id"]
          sample_texts = samples_map[qid]["samples"]  # list[str] len K
          if model is not None:
              tes = [compute_single_te(s, model, tokenizer) for s in sample_texts]
          else:
              # Approximate: use sequence log_probs as proxy (normalized by length)
              log_probs = samples_map[qid]["log_probs"]  # per-sample scalar
              # NOTE: log_probs from H-E1 are sequence-level, not token-level entropy
              # For TE proxy: negate and normalize; real TE needs Llama re-inference
              tes = [-lp / max(len(s.split()), 1) for s, lp in
                     zip(sample_texts, log_probs)]
          per_sample_te[qid] = tes
      return per_sample_te
    """

def compute_cluster_assignments(
    questions: list[dict],
    samples_map: dict,
    nli_pipeline,
) -> dict[str, dict[int, int]]:
    """
    Wraps get_semantic_ids per question.
    Returns: dict[qid -> {sample_idx: cluster_id}]

    Pseudo-code:
      assignments = {}
      for q in questions:
          qid = q["question_id"]
          samples = samples_map[qid]["samples"]
          cluster_ids = get_semantic_ids(samples, nli_pipeline)  # list[int] len K
          assignments[qid] = {i: cid for i, cid in enumerate(cluster_ids)}
      return assignments
    """
```

### Module 2: `analysis.py`

#### Subtask L-4-1: `filter_eligible_questions`

```python
def filter_eligible_questions(
    questions: list[dict],
    cluster_assignments: dict[str, dict[int, int]],
    min_cluster_size: int = 2,
) -> list[str]:
    """
    Return question IDs where ≥1 NLI cluster has ≥min_cluster_size members.
    Asserts len(result) >= 20 (expected from avg_clusters=7.31, K=10).

    Shapes: cluster_assignments[qid] = {sample_idx: cluster_id}
            output: list[str] of eligible qids

    Pseudo-code:
      eligible = []
      for q in questions:
          qid = q["question_id"]
          clusters = cluster_assignments[qid]
          cluster_sizes = Counter(clusters.values())
          if any(size >= min_cluster_size for size in cluster_sizes.values()):
              eligible.append(qid)
      assert len(eligible) >= 20, f"Only {len(eligible)} eligible; check NLI clustering"
      return eligible
    """
```

#### Subtask L-4-2: `compute_intra_cluster_variance` + `compute_inter_cluster_variance`

```python
def compute_intra_cluster_variance(
    cluster_assignments: dict[int, int],   # {sample_idx: cluster_id} for one question
    per_sample_te: list[float],            # [te_0..te_K-1] for one question
    min_cluster_size: int = 2,
) -> float | None:
    """
    Mean variance across multi-member clusters.
    Returns None if no cluster has ≥2 members.

    Shapes: input scalars; output scalar (nats²)

    Pseudo-code:
      cluster_groups = defaultdict(list)
      for idx, cid in cluster_assignments.items():
          cluster_groups[cid].append(per_sample_te[idx])
      variances = [np.var(members) for members in cluster_groups.values()
                   if len(members) >= min_cluster_size]
      return float(np.mean(variances)) if variances else None
    """

def compute_inter_cluster_variance(
    cluster_assignments: dict[int, int],
    per_sample_te: list[float],
) -> float | None:
    """
    Variance across cluster means (between-cluster control).
    Expected to be > intra-cluster variance for correct vs incorrect questions.

    Pseudo-code:
      cluster_groups = defaultdict(list)
      for idx, cid in cluster_assignments.items():
          cluster_groups[cid].append(per_sample_te[idx])
      cluster_means = [np.mean(m) for m in cluster_groups.values()]
      return float(np.var(cluster_means)) if len(cluster_means) > 1 else None
    """

def run_analysis(
    questions: list[dict],
    cluster_assignments: dict[str, dict[int, int]],
    per_sample_te: dict[str, list[float]],
    se_scores: list[float],
) -> list[dict]:
    """
    Per-question analysis. Returns list of result dicts.

    Output dict per question:
      {
        "qid": str,
        "n_clusters": int,
        "n_multi_member_clusters": int,
        "mean_intra_var": float | None,
        "inter_var": float | None,
        "has_paraphrase": bool,
        "se_score": float,
        "high_uncertainty": bool,   # se_score > median(se_scores)
        "per_sample_te": list[float],
      }
    """
```

### Module 3: `evaluate.py`

#### Subtask L-5-1: `verify_mechanism_activated`

```python
def verify_mechanism_activated(
    results: list[dict],
    intra_var_threshold: float = 0.1,
    min_passing: int = 15,
    min_eligible: int = 20,
) -> tuple[bool, dict]:
    """
    Primary gate: mean_intra_var > intra_var_threshold on ≥min_passing eligible questions.

    Pseudo-code:
      eligible = [r for r in results if r["has_paraphrase"]]
      assert len(eligible) >= min_eligible
      passing = [r for r in eligible
                 if r["mean_intra_var"] is not None
                 and r["mean_intra_var"] > intra_var_threshold]
      primary_pass = len(passing) >= min_passing
      indicators = {
          "n_eligible_questions": len(eligible),
          "n_passing_primary_threshold": len(passing),
          "primary_criterion_met": primary_pass,
          "mean_variance_overall": np.mean([r["mean_intra_var"] for r in eligible
                                            if r["mean_intra_var"] is not None]),
          "fraction_passing": len(passing) / len(eligible),
      }
      print(f"[H-M1] eligible={len(eligible)}, passing={len(passing)}, "
            f"mean_var={indicators['mean_variance_overall']:.4f} nats")
      return primary_pass, indicators
    """

def compute_secondary_metrics(
    results: list[dict],
    variance_thresholds: list[float] = (0.05, 0.1, 0.2, 0.5),
) -> dict:
    """
    Returns:
      {
        "threshold_sensitivity": {t: fraction_passing for t in variance_thresholds},
        "high_uncertainty_mean_var": float,   # mean intra_var for high-SE questions
        "low_uncertainty_mean_var": float,    # mean intra_var for low-SE questions
        "inter_gt_intra_fraction": float,     # fraction where inter_var > intra_var
      }
    """

def save_results(
    results: list[dict],
    indicators: dict,
    secondary: dict,
    primary_pass: bool,
    out_dir: str,
) -> None:
    """
    Writes:
      {out_dir}/h_m1_results.json   — per-question list
      {out_dir}/h_m1_summary.json   — indicators + secondary + verdict
    """
```

#### Subtask L-5-2: `compute_secondary_metrics` (threshold sensitivity)

See signature above. Threshold sensitivity table iterates `variance_thresholds` and computes fraction of eligible questions passing each threshold. Used for Figure 5.

### Module 4: `visualize.py`

```python
def plot_all(
    results: list[dict],
    indicators: dict,
    secondary: dict,
    figures_dir: str,
    threshold: float = 0.1,
    dpi: int = 150,
) -> None:
    """
    Generates 5 figures to figures_dir/.

    fig1_gate_bar.png:
      Bar chart: mean intra-cluster TE variance vs 0.1 nats threshold line.
      X: eligible questions sorted by mean_intra_var.
      Y: mean_intra_var (nats²). Red dashed line at threshold=0.1.
      MANDATORY.

    fig2_violin_intra_var.png:
      Violin plot of per-question mean_intra_var distribution across eligible questions.
      Overlay: threshold line, median marker.

    fig3_scatter_size_var.png:
      X: n_multi_member_clusters, Y: mean_intra_var.
      Shows whether variance grows with cluster size.

    fig4_nli_heatmap.png:
      3 representative questions (low-SE, high-SE, borderline).
      For each: heatmap of NLI pairwise entailment scores (K×K matrix).
      Uses seaborn.heatmap.

    fig5_threshold_sensitivity.png:
      X: variance_thresholds [0.05, 0.1, 0.2, 0.5].
      Y: fraction of eligible questions passing.
      Bar chart from secondary["threshold_sensitivity"].
    """
```

### Module 5: `run.py`

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
    "variance_thresholds": [0.05, 0.1, 0.2, 0.5],
}

def main(cfg: dict = CONFIG, smoke_test: bool = False, skip_recompute: bool = False) -> None:
    """
    Orchestrates:
      1. load_or_recompute(cfg) -> data
      2. run_analysis(data) -> results
      3. verify_mechanism_activated(results) -> (primary_pass, indicators)
      4. compute_secondary_metrics(results) -> secondary
      5. save_results(...)
      6. plot_all(...)
      7. Log verdict to experiment.log

    --smoke-test: runs on first 5 questions only
    --skip-recompute: loads cached per-sample TE from results/ if present
    """

if __name__ == "__main__":
    # Self-check: smoke test on 5 questions, assert no crash
    import sys
    smoke = "--smoke-test" in sys.argv
    main(smoke_test=smoke)
    print("[H-M1 self-check] PASS — no crash")
```

---

## Subtask Breakdown

### Epic A-2: Per-sample TE Recomputation (4 subtasks)

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | `_check_he1_cache()` | Probe h-e1/results/ for existing npy files; log what's available |
| L-2-2 | `compute_per_sample_te()` | Re-run compute_single_te on K sample texts per question; fast path uses existing sample texts from samples_map |
| L-2-3 | `compute_cluster_assignments()` | Wrap get_semantic_ids per question; return {qid: {sample_idx: cluster_id}} |
| L-2-4 | `load_or_recompute()` orchestrator | Wire cache check → per-sample TE → cluster assignments → return unified data dict |

### Epic A-4: Variance Computation (2 subtasks)

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | `filter_eligible_questions()` + `run_analysis()` | Eligibility filter + per-question variance computation loop |
| L-4-2 | `compute_intra_cluster_variance()` + `compute_inter_cluster_variance()` | Core variance functions with multi-member cluster filtering |

---

## Data Flow

```
H-E1 results/
  samples_map (JSONL)    ──→ compute_per_sample_te()  ──→ per_sample_te dict
  samples_map (JSONL)    ──→ compute_cluster_assignments() ──→ cluster_assignments dict
  se_scores.npy          ──→ se_scores list
  correctness.npy        ──→ correctness list
                                    ↓
                          filter_eligible_questions()
                                    ↓
                          run_analysis() per question
                                    ↓
                    verify_mechanism_activated() ──→ (primary_pass, indicators)
                    compute_secondary_metrics()  ──→ secondary
                                    ↓
                    save_results() + plot_all()
```

## Expected Data Shapes

| Variable | Shape/Type | Notes |
|----------|-----------|-------|
| `per_sample_te[qid]` | `list[float]` len K=10 | Mean per-token TE, one per sample |
| `cluster_assignments[qid]` | `dict[int, int]` len K=10 | sample_idx → cluster_id |
| `results` | `list[dict]` len 98 | Per-question analysis output |
| `eligible` | `list[str]` len ~20-30 | Filtered question IDs |
| `mean_intra_var` | `float | None` | nats² per question; None if no pairs |
| `inter_var` | `float | None` | nats² between-cluster control |
