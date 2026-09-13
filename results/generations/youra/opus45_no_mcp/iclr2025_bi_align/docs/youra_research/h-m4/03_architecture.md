# Architecture: H-M4 (Bidirectional Tasks Show Miscalibrated Confidence)

**Type:** MECHANISM (FULL tier) | **Applied:** point-biserial + partial correlation via residualization (scipy/sklearn pattern)

Analysis-only experiment. No training, no GPU. Extends H-E1 outputs with feature scoring + correlation.

---

## Codebase Analysis

**Project Type:** base_hypothesis (H-E1)
**Status:** Live H-E1 code found at `docs/youra_research/h-e1/code/` (config.py, data.py, inference.py, calibration.py, clustering.py, visualize.py, run_experiment.py). Multiple stale `_archive/*/h-e1/` copies exist and were ignored.
**Analyzed Path:** `docs/youra_research/h-e1/code/data.py`, `docs/youra_research/h-e1/code/outputs/results.json`
**Findings:**
- `results.json["per_task"]` entries contain `task_id, correct_logprob_norm, max_wrong_logprob_norm, inversion_score, is_inverted, cluster_label` — **NO task text and NO task_metadata key**. PRD/brief assumption of a `task_metadata` field is WRONG (spec vs. implementation mismatch). Task text must be re-loaded from source datasets via `h-e1/code/data.py` loaders, joined on `task_id`.
- Actual H-E1 datasets are **TruthfulQA (`tqa_i`), MMLU moral_scenarios (`mmlu_i`), Anthropic HH-RLHF (`hh_i`)** — NOT "TruthfulQA/ETHICS/HHH" as PRD FR-1/FR-3 states. Architecture below uses actual dataset names for `topic` one-hot and difficulty confound.
- `results.json["aggregate"]` gives `n_tasks_per_cluster=[1519,693]`, `cluster_centers` (cluster 1 = higher inversion_score = "inverted" cluster).
- No cross-model per-model breakdown in results.json beyond `models_evaluated` list — FR-5 (cross-model validation) requires re-deriving per-model calibration or is satisfied via aggregate consistency notes only (single cluster_label used; treat FR-5 as best-effort using available fields, no re-inference).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Task loaders | `from h_e1.data import load_truthfulqa, load_mmlu_moral, load_anthropic_hh` | `h-e1/code/data.py` |
| H-E1 results | JSON load (no import) | `h-e1/code/outputs/results.json` |

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation, not h-e1/03_architecture.md spec)

---

## Module Structure

### data_loader.py (`code/data_loader.py`)

**Dependencies:** h-e1/data.py (sys.path insert), json

```python
def load_e1_results(path: str = "../h-e1/code/outputs/results.json") -> dict: ...
def load_task_texts() -> dict[str, str]:  # task_id -> question text, via h-e1 loaders
def build_dataset(e1_results: dict, task_texts: dict) -> "pd.DataFrame":
    # columns: task_id, question, source_dataset, cluster_label, inversion_score, is_inverted
```

### features.py (`code/features.py`)

**Dependencies:** none (stdlib string matching)

```python
def score_bidirectional_features(task_text: str) -> dict:
    # {"user_belief_reference": 0/1, "context_dependent": 0/1, "hedged_answer": 0/1, "total": 0-3}
def score_all(df: "pd.DataFrame") -> "pd.DataFrame":  # adds feature columns + total
```

### confounds.py (`code/confounds.py`)

**Dependencies:** sklearn.preprocessing (OneHotEncoder)

```python
def extract_length(texts: list[str]) -> "np.ndarray": ...
def extract_topic_onehot(source_dataset: list[str]) -> "np.ndarray": ...
def extract_format_onehot(texts: list[str]) -> "np.ndarray":  # MC vs open-ended heuristic
def extract_difficulty(df: "pd.DataFrame") -> "np.ndarray":  # from correct_logprob_norm/max_wrong_logprob_norm gap
def build_confound_matrix(df: "pd.DataFrame") -> "np.ndarray":  # concat all confounds
```

### correlation.py (`code/correlation.py`)

**Dependencies:** scipy.stats, sklearn.linear_model.LinearRegression, numpy

```python
def compute_correlations(cluster_labels: "np.ndarray", scores: "np.ndarray", confound_matrix: "np.ndarray") -> dict:
    # {point_biserial_r, point_biserial_p, cohens_d, partial_r, partial_p}
def check_gate(metrics: dict) -> bool:
    # (r>0.4) or (d>0.3 and partial_r>0.3)
```

### cross_model.py (`code/cross_model.py`)

**Dependencies:** correlation.py

```python
def per_model_consistency(df: "pd.DataFrame", models: list[str]) -> dict:
    # reruns compute_correlations if per-model cluster data available; else reports aggregate-only note
```

### visualize.py (`code/visualize.py`)

**Dependencies:** matplotlib

```python
def plot_gate_metrics(metrics: dict, out_path: str) -> None: ...  # required
def plot_score_by_cluster(df, out_path: str) -> None: ...          # optional violin
def plot_feature_breakdown(df, out_path: str) -> None: ...         # optional stacked bar
def plot_scatter(df, out_path: str) -> None: ...                   # optional
```

### h_m4_experiment.py (`code/h_m4_experiment.py`) — entrypoint

**Dependencies:** all modules above

```python
def main() -> None:
    # load -> score features -> build confounds -> compute_correlations -> gate check
    # -> cross_model consistency -> save outputs/results.json -> generate figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load H-E1 results.json + rejoin task text via h-e1/data.py loaders (task_id prefix match) | 10 | 3+3+2+2 |
| A-2 | Feature scoring | Implement 3 keyword-based bidirectional features + total score | 6 | 2+1+2+1 |
| A-3 | Confound extraction | Length, topic one-hot, format one-hot, difficulty from logprob gap | 9 | 3+2+2+2 |
| A-4 | Correlation analysis | Point-biserial r, Cohen's d, partial correlation via residualization | 11 | 3+3+3+2 |
| A-5 | Gate check | Threshold logic (r>0.4) or (d>0.3 and partial_r>0.3), save metrics | 4 | 1+1+1+1 |
| A-6 | Cross-model consistency | Repeat/report correlation per model where feasible from available fields | 8 | 3+2+2+1 |
| A-7 | Required visualization | Gate metrics bar chart (r, d, partial_r vs thresholds) | 5 | 2+1+1+1 |
| A-8 | Optional visualizations | Violin plot, feature breakdown stacked bar, scatter plot | 7 | 3+1+2+1 |
| A-9 | Results serialization | Save all metrics + intermediate scores to outputs/results.json, seed=42 | 5 | 2+1+1+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-3, A-4, A-6], Low(4-8): [A-2, A-5, A-7, A-8, A-9]
