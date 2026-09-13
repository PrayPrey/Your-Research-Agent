# Architecture: H-C1 (Condition Test — Prospective Structural Validity)

**Type**: CONDITION — pure statistical validation, no training, single-script scope
**Applied**: sklearn frozen-PCA `transform()` projection + Pearson correlation loading pattern (no KB match — domain mismatch, diffusion-model corpus)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1) for data artifacts only — no code reuse
**Status**: H-E1 code is green-field Python, no shared library to import. H-C1 consumes H-E1 **output artifacts** (JSON/CSV), not H-E1 modules.
**Analyzed Path**: `h-e1/outputs/` (artifact schema, confirmed via `h-e1/03_architecture.md` Section 2)
**Findings**: `h-e1/outputs/h_e1_results.json` contains `pc1_loadings`, `residual_mean`, `residual_std`; `h-e1/outputs/residualized_matrix.csv` is the N x 6 fitted residual matrix. H-C1 code itself is green-field.

---

## 1. Module Structure

Data flow: `data_loader` (H-E1 artifacts + TrustLLM holdout) → `analysis` (model matching + frozen PC1 projection + correlation) → `visualization`, orchestrated by `h_c1_prospective_validity.py`.

### data_loader (`data_loader.py`)

**Dependencies**: pandas, json, requests/datasets (TrustLLM fetch)

```python
def load_h_e1_artifacts(results_path: str, matrix_path: str) -> dict:
    """Returns {pc1_loadings, residual_mean, residual_std, residualized_matrix: pd.DataFrame}"""

def load_trustllm_holdout(cache_path: str = "outputs/trustllm_raw.parquet") -> pd.DataFrame:
    """Returns df with model_id + holdout dimension columns (truthfulness, safety, fairness, robustness)"""

def match_models(h_e1_df: pd.DataFrame, trustllm_df: pd.DataFrame) -> pd.DataFrame:
    """Inner-join on model_id; returns aligned df, logs (n_h_e1, n_trustllm, n_matched)"""
```

### analysis (`analysis.py`)

**Dependencies**: numpy, sklearn.decomposition.PCA, scipy.stats.pearsonr

```python
def rebuild_frozen_pca(pc1_loadings: list[float], residual_mean: list[float],
                        residual_std: list[float]) -> PCA:
    """Reconstructs fitted PCA(n_components=1) object from H-E1 frozen params (no refit)"""

def project_pc1_scores(frozen_pca: PCA, residualized_matrix: np.ndarray) -> np.ndarray:
    """frozen_pca.transform(matrix)[:, 0] -- matched-subset PC1 scores"""

def compute_holdout_loading(pc1_scores: np.ndarray, new_benchmark: np.ndarray) -> dict:
    """Returns {loading, p_value, ci_lower, ci_upper} via pearsonr + Fisher z CI"""

def run_all_holdouts(pc1_scores: np.ndarray, holdout_df: pd.DataFrame,
                      holdout_cols: list[str]) -> dict:
    """Returns {benchmark_name: {loading, p_value, ci_lower, ci_upper}} for each holdout dim"""
```

### visualization (`visualization.py`)

**Dependencies**: matplotlib

```python
def plot_gate_metrics(loadings: dict[str, float], threshold: float, out_path: str) -> None:
    """Mandatory: bar chart, green if >=0.3 else red, horizontal line at threshold"""

def plot_loading_comparison(h_e1_loadings: dict, holdout_loadings: dict, out_path: str) -> None: ...
def plot_pc1_scatter(pc1_scores: np.ndarray, holdout_df: pd.DataFrame, holdout_cols: list[str], out_path: str) -> None: ...
def plot_loading_heatmap(all_loadings: dict, out_path: str) -> None: ...
```

### orchestrator (`h_c1_prospective_validity.py`)

```python
def main() -> dict:
    """Runs full pipeline, writes outputs/h_c1_results.json, returns results dict"""
```

---

## 2. File Organization

```
h-c1/code/
  data_loader.py
  analysis.py
  visualization.py
  h_c1_prospective_validity.py
  requirements.txt
h-c1/outputs/
  h_c1_results.json
  matched_models.csv
h-c1/figures/
  gate_metrics.png
  loading_comparison.png
  pc1_scatter.png
  loading_heatmap.png
```

No `config.py` — holdout benchmark list, PC1 threshold (0.3), and CI method are module-level constants in `analysis.py` (Tier 1 simple validation, no ablation surface).

---

## 3. Error Handling & Validation Checkpoints

| Checkpoint | Location | Failure Mode |
|---|---|---|
| H-E1 artifacts missing/malformed | `data_loader.load_h_e1_artifacts` | raise `FileNotFoundError` / assert required keys present |
| TrustLLM fetch returns 0 rows | `data_loader.load_trustllm_holdout` | raise `RuntimeError` |
| Model matching < 10 overlapping models | `data_loader.match_models` | raise `ValueError` (insufficient N for correlation) |
| Frozen PCA reconstruction shape mismatch | `analysis.rebuild_frozen_pca` | assert `len(pc1_loadings) == 6` |
| Loading computation NaN (zero variance) | `analysis.compute_holdout_loading` | raise `ValueError`, skip that benchmark, log warning |
| Output schema incomplete | `h_c1_prospective_validity.main` | assert all keys (per-benchmark loading/p/CI) present before json.dump |

Logs `(n_h_e1_models, n_trustllm_models, n_matched)` at match step for reproducibility.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loader | Load H-E1 artifacts + fetch TrustLLM holdout | 5 | 2+1+1+1 |
| A-2 | Model matching | Join H-E1/TrustLLM on model_id, log counts | 4 | 1+1+1+1 |
| A-3 | Frozen PCA rebuild + projection | Reconstruct PCA from frozen params, transform matched matrix | 5 | 2+1+1+1 |
| A-4 | Loading computation | Pearson correlation + p-value + Fisher z CI per holdout benchmark | 5 | 1+1+2+1 |
| A-5 | Visualization | 4 plots (gate metrics, comparison, scatter, heatmap) | 4 | 1+1+1+1 |
| A-6 | Orchestration + output | Wire pipeline, write results JSON, pass/fail gate check | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1,A-2,A-3,A-4,A-5,A-6]

---

## External Dependencies (H-E1 Artifacts)

| Artifact | Path | Contents |
|----------|------|----------|
| PC1 params | `h-e1/outputs/h_e1_results.json` | `pc1_loadings`, `residual_mean`, `residual_std` |
| Residual matrix | `h-e1/outputs/residualized_matrix.csv` | N x 6 fitted residuals (model_id indexed) |

**Verified from**: `h-e1/03_architecture.md` Section 2 (File Organization) — not code import, artifact-only dependency.
