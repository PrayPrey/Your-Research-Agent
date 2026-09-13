# Architecture: H-M2 (Mechanism Test — Instruction-Tuning Effect on BSI & PC1,residual)

**Type**: MECHANISM
**Applied**: Paired-difference statistical test pattern (scipy.stats.ttest_rel + Wilcoxon + Cohen's d), reused from H-E1's OLS-residualization → PCA pattern for PC1 scoring.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 referenced, but its `code/` directory does not exist on disk yet — only `03_architecture.md` spec is present)
**Status**: No actual H-E1 implementation files found at `h-e1/code/`; only the architecture spec exists. Per rule (trust actual code over spec), since no code exists, H-M2 re-implements the residualization/PCA pipeline directly from the H-E1 spec (Section "analysis.py") rather than importing unverifiable code.
**Analyzed Path**: `h-e1/code/` (searched, empty — 0 files)
**Findings**: Green-field for H-M2 code; reuse is by algorithm/spec only (`residualize`, `fit_pca` signatures from `h-e1/03_architecture.md`), not by import.

---

## 1. Module Structure

Data flow: `model_pairs` (config) → `bsi_evaluator` + `pc1_scorer` (parallel) → `paired_analysis` → `run_experiment.py` (orchestrator)

### model_pairs (`data/model_pairs.yaml`)

Static config, not code — 16 rows of `{family, base_model, instruct_model, params}`.

### bsi_evaluator (`src/bsi_evaluator.py`)

**Dependencies**: transformers, torch, datasets

```python
def load_paws(cache_dir: str) -> pd.DataFrame:
    """Concat PAWS-Wiki test + PAWS-QQP dev, columns: sentence1, sentence2, paraphrase_label"""

def paraphrase_prompt(pair: str, s1: str, s2: str) -> str: ...

def classify_pair(model, tokenizer, s1: str, s2: str, few_shot: bool = False) -> int:
    """Returns 0/1 prediction via greedy decode, temperature=0"""

def compute_bsi(model, tokenizer, paws_df: pd.DataFrame, paraphrase_fn, few_shot: bool = False) -> float:
    """BSI = mean agreement(pred(original), pred(paraphrased)) over all rows"""

def evaluate_model_bsi(model_id: str, few_shot: bool = False) -> dict:
    """Loads model, returns {model_id, bsi, n_pairs}"""
```

### pc1_scorer (`src/pc1_scorer.py`)

**Dependencies**: pandas, numpy, statsmodels, sklearn.decomposition.PCA (reuses H-E1 `residualize`/`fit_pca` algorithm)

```python
BENCHMARKS = ["truthfulqa", "mmlu", "advglue", "bbh", "gsm8k", "winogrande"]

def load_benchmark_scores(model_ids: list[str]) -> pd.DataFrame:
    """From Open LLM Leaderboard API, columns: model_id, log_params, release_date, *BENCHMARKS"""

def residualize(Y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Same as H-E1: OLS residuals per benchmark column"""

def compute_pc1(df: pd.DataFrame) -> pd.Series:
    """Returns PC1,residual score indexed by model_id"""
```

### paired_analysis (`src/paired_analysis.py`)

**Dependencies**: scipy.stats, numpy

```python
def paired_deltas(base_vals: np.ndarray, instruct_vals: np.ndarray) -> np.ndarray: ...

def run_paired_ttest(base_vals: np.ndarray, instruct_vals: np.ndarray) -> dict:
    """Returns {t_stat, p_value, mean_delta, cohens_d}"""

def run_wilcoxon(base_vals: np.ndarray, instruct_vals: np.ndarray) -> dict:
    """Returns {stat, p_value}"""

def delta_correlation(delta_bsi: np.ndarray, delta_pc1: np.ndarray) -> dict:
    """Returns {pearson_r, p_value}"""
```

### run_experiment (`src/run_experiment.py`)

```python
def main() -> dict:
    """Loads model_pairs.yaml, runs BSI+PC1 for all 32 models (base+instruct few_shot=True for base),
    runs paired_analysis, writes results/*.csv and results/statistical_results.json"""
```

---

## 2. File Organization

```
h-m2/
  data/
    paws_wiki_test.json
    paws_qqp_dev.json
    model_pairs.yaml
  src/
    bsi_evaluator.py
    pc1_scorer.py
    paired_analysis.py
    run_experiment.py
  results/
    bsi_scores.csv
    pc1_scores.csv
    statistical_results.json
  requirements.txt
```

No separate `config.py` — model list lives in `model_pairs.yaml`; benchmark list and seed (42) are module constants in `pc1_scorer.py`.

---

## 3. Error Handling & Validation Checkpoints

| Checkpoint | Location | Failure Mode |
|---|---|---|
| Model fails to load (OOM/missing) | `bsi_evaluator.evaluate_model_bsi` | log + skip pair, exclude from N=16 |
| PAWS file missing | `bsi_evaluator.load_paws` | raise `FileNotFoundError` |
| Benchmark score missing for model | `pc1_scorer.load_benchmark_scores` | raise `ValueError`, list missing models |
| N < 16 pairs after failures | `run_experiment.main` | log warning, proceed with reduced N, note in results |
| ttest_rel on N<2 | `paired_analysis.run_paired_ttest` | raise `ValueError` |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Model pairs config | Write model_pairs.yaml (16 pairs) | 3 | 1+1+1+0 |
| B-2 | PAWS data loader | Load/merge PAWS-Wiki + PAWS-QQP | 5 | 2+1+1+1 |
| B-3 | BSI evaluator | Paraphrase classify + agreement scoring, zero/few-shot | 9 | 3+2+2+2 |
| B-4 | PC1 scorer | Load benchmark scores, residualize, PCA (reuse H-E1 algorithm) | 7 | 2+2+2+1 |
| B-5 | Paired statistical tests | ttest_rel, Wilcoxon, Cohen's d | 5 | 2+1+1+1 |
| B-6 | Delta correlation | Pearson r between Δ_BSI and Δ_PC1 | 3 | 1+1+1+0 |
| B-7 | Few-shot ablation | 3-shot base vs zero-shot instruct comparison | 6 | 2+1+2+1 |
| B-8 | Orchestration | Wire full pipeline across 32 models, write CSV/JSON outputs | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-3, B-4, B-8], Low(4-8): [B-1, B-2, B-5, B-6, B-7]

---

## External Dependencies (Base Hypothesis)

H-E1's `code/` directory does not exist on disk (Serena search returned 0 files). No import path can be verified. `pc1_scorer.py` therefore **re-implements** the `residualize`/`fit_pca` algorithm following the interface documented in `h-e1/03_architecture.md` rather than importing unverifiable modules. If H-E1 code is added later, replace `pc1_scorer.residualize`/`compute_pc1` bodies with imports from `h-e1/code/analysis.py`.
