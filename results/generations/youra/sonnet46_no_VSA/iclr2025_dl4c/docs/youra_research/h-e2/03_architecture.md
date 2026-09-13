# Architecture: H-E2 — SFT Training Source Ablation

**Applied: minimal-script DL experiment pattern (LIGHT tier)**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Serena `get_symbols_overview` confirmed no src/ or code/ directory exists.

---

## File Structure

```
docs/youra_research/h-e2/
├── code/
│   ├── prepare_data.py      # data pipeline (dedup, format, token-equalize)
│   ├── train.py             # SFT training (TRL SFTTrainer + DeepSpeed ZeRO-3)
│   ├── evaluate.py          # EvalPlus runner + result collection
│   ├── analyze.py           # statsmodels MixedLM + Holm-Bonferroni + plots
│   └── run_all.sh           # orchestration shell script
├── ds_zero3_config.json     # DeepSpeed ZeRO-3 config (fixed)
├── figures/                 # output figures (PNG)
├── data/sft_sources/        # processed HF Datasets (arrow)
├── checkpoints/             # SFT model checkpoints
└── results/                 # JSON + CSV + statistical_report.txt
```

---

## Modules

### DataPipeline (`code/prepare_data.py`)

**Dependencies**: datasets, sentence-transformers, evalplus, numpy

```python
UNIFORM_TEMPLATE: str = "# Complete the following Python function:\n{docstring}\n{function_signature}"
CONDITIONS: list[str] = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
DEDUP_THRESHOLD: float = 0.95
TARGET_PROBLEMS: int = 164  # limited by HumanEval-only post-dedup

def load_source(condition: str) -> Dataset: ...
def embed_texts(texts: list[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray: ...
def dedup_against_eval(dataset: Dataset, threshold: float = DEDUP_THRESHOLD) -> Dataset: ...
def format_example(ex: dict) -> dict: ...  # returns {"text": prompt + solution}
def repeat_to_token_budget(dataset: Dataset, target_tokens: int, tokenizer) -> Dataset: ...
def build_sft_dataset(condition: str) -> Dataset: ...
def main() -> None: ...  # argparse: --condition, --output_dir; smoke: --smoke

if __name__ == "__main__":
    main()
```

---

### Trainer (`code/train.py`)

**Dependencies**: transformers, trl, accelerate, deepspeed, datasets

```python
FIXED_HPARAMS: dict = {
    "learning_rate": 2e-5,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.05,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "bf16": True,
    "completion_only_loss": True,
    "max_length": 2048,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.95,
}
EPOCHS_PER_CONDITION: dict[str, int] = {
    "humaneval_only": 6,
    "mbpp_only": 3,
    "leetcode_only": 1,
    "equal_mix": 2,
}
BASE_HUMANEVAL: float = 0.15
BASE_MBPP: float = 0.45

def load_model_and_tokenizer(model_id: str = "deepseek-ai/deepseek-coder-1.3b-base"): ...
def run_sft(condition: str, seed: int, data_dir: str, output_dir: str) -> None: ...
def verify_sft_activation(pass1_humaneval: float, pass1_mbpp: float, condition: str) -> bool: ...
def main() -> None: ...  # argparse: --condition, --seed, --data_dir, --output_dir; --smoke

if __name__ == "__main__":
    main()
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: subprocess, json, csv, pathlib, argparse

```python
BENCHMARKS: list[str] = ["humaneval", "mbpp"]

def run_evalplus(checkpoint_dir: str, benchmark: str) -> dict: ...
    # calls: python -m evalplus.evaluate --model {checkpoint_dir} --dataset {benchmark}
    #        --backend hf --greedy
    # returns parsed JSON with pass@1

def parse_evalplus_output(json_path: str) -> float: ...  # extracts pass@1

def collect_result(
    condition: str, seed: int, benchmark: str, pass1: float, results_csv: str
) -> None: ...  # appends row to CSV

def main() -> None: ...
    # argparse: --condition, --seed, --benchmark, --checkpoint_dir, --results_csv
    # --smoke: runs with --dataset humaneval on a single task

if __name__ == "__main__":
    main()
```

---

### Analyzer (`code/analyze.py`)

**Dependencies**: pandas, statsmodels, scipy, matplotlib, seaborn, numpy

```python
FIGURES_DIR: str = "docs/youra_research/h-e2/figures"
BENCHMARKS: list[str] = ["humaneval", "mbpp"]

def load_results(results_csv: str) -> pd.DataFrame: ...

def fit_mixedlm(df: pd.DataFrame, benchmark: str) -> MixedLMResultsWrapper: ...
    # formula: "pass1 ~ C(source_condition) + solution_length"
    # groups: df["problem_id"]

def holm_bonferroni(pvalues: list[float]) -> list[float]: ...

def pairwise_contrasts(model_result, conditions: list[str]) -> pd.DataFrame: ...
    # returns DataFrame with columns: pair, contrast_pp, p_raw, p_adjusted

def evaluate_gate(contrasts_df: pd.DataFrame, model_result) -> str: ...
    # returns "PASS" or "FAIL" with reasoning

def plot_bar_chart(df: pd.DataFrame, output_path: str) -> None: ...
    # pass@1 per condition per benchmark, error bars = std across seeds

def plot_transfer_matrix(df: pd.DataFrame, output_path: str) -> None: ...
    # 4×2 heatmap: training source × benchmark, cell = mean pass@1

def plot_strip(df: pd.DataFrame, output_path: str) -> None: ...
    # per-seed pass@1 per condition per benchmark

def plot_forest(contrasts_df: pd.DataFrame, output_path: str) -> None: ...
    # pairwise contrasts with 95% CI and Holm-Bonferroni p-values

def plot_token_budget(token_counts: dict, output_path: str) -> None: ...

def main() -> None: ...
    # argparse: --results_csv, --report_out, --figures_dir
    # smoke: fit on synthetic 5-row DataFrame

if __name__ == "__main__":
    main()
```

---

### Orchestrator (`code/run_all.sh`)

**Dependencies**: bash, accelerate

```bash
#!/usr/bin/env bash
# Usage: bash run_all.sh [--smoke]
# Runs: prepare_data (4 conditions) → train (12 runs) → evaluate (24 runs) → analyze
#
# Each train run:
#   accelerate launch --config_file accelerate_config.yaml \
#       --deepspeed_config_file ../ds_zero3_config.json \
#       train.py --condition $CONDITION --seed $SEED
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load 3 HF sources, dedup via all-MiniLM-L6-v2, subsample to 164, format with uniform template, repeat to token budget, save to arrow | 14 | 3+3+4+4 |
| A-2 | SFT Training Script | TRL SFTTrainer + DeepSpeed ZeRO-3, bf16, completion_only_loss, variable epochs per condition, 3 seeds, checkpoint save | 15 | 3+4+4+4 |
| A-3 | Evaluation Runner | EvalPlus CLI subprocess per checkpoint×benchmark, parse JSON pass@1, append to CSV, smoke test | 10 | 2+2+3+3 |
| A-4 | Statistical Analysis | statsmodels MixedLM fit per benchmark, Holm-Bonferroni on 6 pairwise contrasts, gate evaluation, text report | 13 | 3+3+4+3 |
| A-5 | Visualization | Bar chart (mandatory) + transfer matrix heatmap + strip plots + forest plot + token budget bar | 9 | 3+2+2+2 |
| A-6 | Orchestration & Smoke Tests | run_all.sh wiring all stages, per-script smoke test (--smoke flag, 1 step), DeepSpeed config JSON | 8 | 2+2+2+2 |

**Distribution**: High(14-17): [A-1, A-2], Medium(9-13): [A-3, A-4, A-5], Low(4-8): [A-6]

---

## DeepSpeed Config (`code/../ds_zero3_config.json`)

Fixed ZeRO-3 config alongside checkpoints — standard DeepSeek-Coder official template with `bf16.enabled: true`, `zero_optimization.stage: 3`, `allgather_bucket_size: 2e8`, `reduce_bucket_size: 2e8`.

---

## Artifact Paths

| Artifact | Path |
|----------|------|
| Processed datasets | `docs/youra_research/h-e2/data/sft_sources/{condition}/` |
| Checkpoints | `docs/youra_research/h-e2/checkpoints/condition_{cond}_seed_{seed}/` |
| EvalPlus JSON | `docs/youra_research/h-e2/results/{condition}_{seed}_{benchmark}.json` |
| Aggregated CSV | `docs/youra_research/h-e2/results/all_results.csv` |
| Statistical report | `docs/youra_research/h-e2/results/statistical_report.txt` |
| Figures | `docs/youra_research/h-e2/figures/` |
