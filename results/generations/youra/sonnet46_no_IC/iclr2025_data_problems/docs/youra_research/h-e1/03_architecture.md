# Architecture: H-E1 — Scale-Dependent Optimal Curation (Existence Test)

**Applied**: Standard pipeline pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior hypothesis code to reuse. All modules are original.

---

## Overview

EXISTENCE hypothesis. Minimal pipeline: curate 12 corpus variants, train 72 models, evaluate 720 checkpoints, run ANOVA, visualize.

**Root**: `docs/youra_research/h-e1/code/`

---

## File Structure

- `code/curate.py` — PPL filtering + MinHash dedup via NeMo-Curator
- `code/preprocess.py` — NeoX binary format conversion + contamination removal
- `code/train.py` — GPT-NeoX run launcher (72 runs)
- `code/evaluate.py` — lm-eval harness batch runner (720 checkpoint evals)
- `code/analyze.py` — 2-way ANOVA + ANCOVA + gate check
- `code/visualize.py` — all required figures
- `code/config.py` — single fixed config (all hyperparams + paths)
- `code/orchestrate.py` — top-level pipeline runner

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
PPL_THRESHOLDS: list[int] = [20, 35, 50]
DEDUP_JACCARD: list[float] = [0.7, 0.9]
CORPORA: list[str] = ["dolma", "fineweb"]
SCALES: list[int] = [70, 160]
SEEDS: list[int] = [1, 2, 3]
TOTAL_TOKENS: int = 50_000_000_000
CHECKPOINT_INTERVAL_TOKENS: int = 5_000_000_000
BATCH_SIZE_TOKENS: int = 2_000_000
TRAIN_STEPS: int = 25_000

CORPUS_ROOT: str        # base dir for curated corpora
CHECKPOINT_ROOT: str    # base dir for model checkpoints
EVAL_ROOT: str          # base dir for lm-eval outputs
RESULTS_CSV: str        # "results/h-e1/results.csv"
FIGURES_DIR: str        # "docs/youra_research/h-e1/figures/"

MINHASH_PARAMS: dict    # {0.7: {num_buckets:20, hashes_per_bucket:13}, 0.9: {...8...}}
GPT2_PPL_MODEL: str = "gpt2"
NEOX_TOKENIZER: str     # path to 20B_tokenizer.json
NEOX_REPO: str          # path to cloned gpt-neox repo

PYTHIA_CONFIGS: dict    # {70: {...}, 160: {...}} hyperparams per scale
```

---

### DataCurator (`code/curate.py`)

**Dependencies**: Config, nemo_curator, transformers, datasets

```python
def score_and_filter_ppl(
    dataset_iter,
    ppl_threshold: int,
    output_path: str,
    batch_size: int = 64,
) -> dict: ...
# Returns: {"retained": int, "total": int, "output_path": str}

def apply_minhash_dedup(
    input_path: str,
    jaccard_threshold: float,
    output_path: str,
    cache_dir: str,
) -> dict: ...
# Returns: {"retained": int, "total": int, "output_path": str}

def curate_all_variants(
    corpus_name: str,          # "dolma" | "fineweb"
    base_stream,               # HF streaming dataset
    output_root: str,
) -> list[dict]: ...
# Returns list of variant metadata dicts (condition, path, token_count)

def get_corpus_stream(corpus_name: str): ...
# Returns HuggingFace streaming dataset for dolma or fineweb
```

---

### Preprocessor (`code/preprocess.py`)

**Dependencies**: Config, subprocess, pathlib

```python
def convert_to_neox_binary(
    jsonl_path: str,
    output_prefix: str,
    tokenizer_path: str,
    neox_repo: str,
) -> str: ...
# Calls tools/preprocess_data.py, returns .bin/.idx prefix path

def run_decontaminator(
    corpus_path: str,
    benchmark_test_sets: list[str],
    output_path: str,
) -> float: ...
# Returns contamination_rate (CR) for ANCOVA covariate

def preprocess_all_variants(
    variant_metadata: list[dict],
    neox_repo: str,
) -> list[dict]: ...
# Adds "binary_prefix" and "contamination_rate" to each variant dict
```

---

### Trainer (`code/train.py`)

**Dependencies**: Config, subprocess, pathlib, yaml

```python
def build_neox_config(
    scale: int,              # 70 | 160
    binary_prefix: str,
    seed: int,
    checkpoint_dir: str,
    base_config_path: str,
) -> str: ...
# Returns path to written YAML config file

def launch_neox_run(
    neox_config_path: str,
    neox_repo: str,
) -> int: ...
# Runs subprocess, returns exit code

def run_all_training(
    variant_metadata: list[dict],
) -> list[dict]: ...
# Iterates 12 variants × 2 scales × 3 seeds = 72 runs
# Returns list of run records: {variant, scale, seed, checkpoint_dir, status}

def list_checkpoints(checkpoint_dir: str) -> list[str]: ...
# Returns sorted list of 10 HF-format checkpoint paths per run

def convert_checkpoint_to_hf(
    neox_checkpoint: str,
    output_dir: str,
    neox_repo: str,
) -> str: ...
# Calls tools/convert_to_hf.py, returns HF model dir
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config, subprocess, json, pathlib

```python
def run_lm_eval(
    model_path: str,
    output_path: str,
    tasks: list[str] = ["mmlu", "hellaswag"],
    num_fewshot: int = 4,
) -> dict: ...
# Returns {"mmlu_4shot": float, "hellaswag_0shot": float}

def parse_lm_eval_output(output_dir: str) -> dict: ...
# Parses lm-eval JSON output, returns metric dict

def evaluate_all_checkpoints(
    run_records: list[dict],
    eval_root: str,
) -> list[dict]: ...
# 72 runs × 10 checkpoints = 720 evaluations
# Returns list of result dicts with all condition columns

def save_results(
    results: list[dict],
    csv_path: str,
    parquet_path: str,
) -> None: ...
```

---

### Analyzer (`code/analyze.py`)

**Dependencies**: Config, pandas, scipy, statsmodels, numpy

```python
def load_results(csv_path: str) -> "pd.DataFrame": ...

def compute_partial_eta2(
    anova_table: "pd.DataFrame",
    effect_name: str,
) -> float: ...

def run_ancova_interaction(
    df: "pd.DataFrame",
    dv: str = "mmlu_4shot",
) -> dict: ...
# Returns: {"interaction_p": float, "interaction_eta2": float, "anova_table": DataFrame}

def check_direction(df: "pd.DataFrame") -> dict: ...
# Returns: {"tau_star_70m": int, "tau_star_160m": int, "direction_confirmed": bool}

def run_secondary_analyses(df: "pd.DataFrame") -> dict: ...
# Levene's test + Scale×Dedup ANOVA + post-hoc pairwise

def gate_check(analysis_results: dict) -> dict: ...
# Returns: {"passed": bool, "reason": str}

def run_full_analysis(csv_path: str) -> dict: ...
# Top-level: loads data, runs all tests, prints gate result
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: Config, pandas, matplotlib, seaborn, pathlib

```python
def plot_bar_factorial(
    df: "pd.DataFrame",
    output_dir: str,
) -> None: ...
# MMLU + HellaSwag by Scale × PPL-threshold, error bars over seeds

def plot_interaction(
    df: "pd.DataFrame",
    output_dir: str,
) -> None: ...
# Line plot: score vs τ, separate lines per scale

def plot_dedup_interaction(
    df: "pd.DataFrame",
    output_dir: str,
) -> None: ...
# Dedup effect (J=0.7 vs J=0.9) by scale

def plot_fineweb_replication(
    df: "pd.DataFrame",
    output_dir: str,
) -> None: ...
# Side-by-side Dolma vs FineWeb interaction plots

def plot_corpus_size_heatmap(
    variant_metadata: list[dict],
    output_dir: str,
) -> None: ...
# Token count per filter condition

def plot_contamination_table(
    variant_metadata: list[dict],
    output_dir: str,
) -> None: ...

def generate_all_figures(
    df: "pd.DataFrame",
    variant_metadata: list[dict],
    output_dir: str,
) -> None: ...
```

---

### Orchestrator (`code/orchestrate.py`)

**Dependencies**: all modules above

```python
def run_pipeline(
    stage: str = "all",   # "curate"|"preprocess"|"train"|"evaluate"|"analyze"|"visualize"|"all"
    resume: bool = True,
) -> None: ...
# Entry point. Calls stages in order, writes checkpoint metadata to JSON between stages.

def load_stage_state(state_file: str) -> dict: ...
def save_stage_state(state: dict, state_file: str) -> None: ...

if __name__ == "__main__":
    import argparse
    # python orchestrate.py --stage all --resume
```

---

## Data Flow

- `curate.py` → JSONL variant dirs (12 variants × 2 corpora)
- `preprocess.py` → NeoX .bin/.idx files + contamination rates
- `train.py` → 72 checkpoint dirs (converted to HF format)
- `evaluate.py` → `results/h-e1/results.csv` (720 rows)
- `analyze.py` → gate check result + printed report
- `visualize.py` → `docs/youra_research/h-e1/figures/` (6 figures)

---

## External Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `nemo_curator` | GPU MinHash + fuzzy dedup | `pip install nemo-curator>=0.3.0` |
| `gpt-neox` | Pythia training + conversion | `git clone EleutherAI/gpt-neox` |
| `lm-eval` | MMLU + HellaSwag eval | `pip install lm-eval>=0.4.0` |
| `llm-decontaminator` | Contamination rate | `git clone lm-sys/llm-decontaminator` |
| `statsmodels` | ANOVA + ANCOVA | `pip install statsmodels>=0.14.0` |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Orchestrator | Fixed config, stage runner, state file | 6 | 2+1+1+2 |
| A-2 | Corpus Curation | PPL filter + MinHash dedup for 12 variants × 2 corpora | 17 | 4+4+5+4 |
| A-3 | Preprocessing | NeoX binary conversion + decontamination for all variants | 13 | 3+3+4+3 |
| A-4 | Training | NeoX config gen + 72-run launcher + HF conversion | 16 | 4+4+4+4 |
| A-5 | Evaluation | lm-eval batch runner over 720 checkpoint-condition pairs | 14 | 3+3+4+4 |
| A-6 | Analysis + Gate | ANCOVA, direction check, gate pass/fail | 12 | 3+3+4+2 |
| A-7 | Visualization | 6 required figures + save to figures/ | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-4, A-5], Medium(9-13): [A-3, A-6, A-7], Low(4-8): [A-1]
