# H-C1 Architecture: Scale Attenuation of SFT Source Identity Effect

**Applied**: H-E2 module patterns (train/evaluate/analyze); minimal delta for 7B + η² comparison

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E2)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e2/code/`
**Findings**: H-E2 has `train.py` (TRL SFTTrainer, 1.3B, completion_only_loss), `evaluate.py` (EvalPlus two-step codegen→evaluate, CSV append), `analyze.py` (MixedLM + Holm-Bonferroni + 5 figures). H-C1 is a thin adaptation: MODEL_ID 1.3B→7B, epochs→3 uniform, η² extraction added to analyze.py, new figures.py for scale comparison plots.

---

## System Components

**Training pipeline**
- `data_loader.py` — symlinks/copies H-E2 Arrow datasets; validates token budget parity
- `train.py` — TRL SFTTrainer on DeepSeek-Coder-7B-Base; 4 conditions × 3 seeds = 12 checkpoints

**Eval pipeline**
- `evaluate.py` — EvalPlus two-step (codegen → evaluate) per checkpoint × 2 benchmarks; appends to results.json

**Analysis pipeline**
- `analyze.py` — loads results.json; MixedLM + η² at 7B; compares to H-E2 η² at 1.3B
- `figures.py` — 4 publication figures to `docs/youra_research/h-c1/figures/`

---

## File / Directory Structure

```
experiments/h-c1/
├── data_loader.py          # dataset access from H-E2 Arrow files
├── train.py                # SFT runner (7B, 4 conditions × 3 seeds)
├── evaluate.py             # EvalPlus runner (24 evals: 12 models × 2 benchmarks)
├── analyze.py              # statistical analysis + η² comparison
├── figures.py              # 4 figures → docs/youra_research/h-c1/figures/
├── config.py               # all constants (paths, hparams, seeds)
├── run_all.sh              # orchestration: sequential train → parallel eval → analyze
├── ds_config.json          # DeepSpeed ZeRO-3 config (adapted from H-E2)
└── tests/
    └── test_smoke.py       # smoke tests for all 5 modules
```

**Output artifacts**
```
experiments/h-c1/checkpoints/
    condition_{cond}_seed_{seed}/   # 12 checkpoint dirs (model.safetensors + tokenizer)
experiments/h-c1/results/
    all_results.json                # {condition: {seed: {benchmark: pass@1}}}
    all_results.csv                 # flat CSV for analysis
    statistical_report.txt
docs/youra_research/h-c1/figures/
    eta2_comparison.png             # MANDATORY: η²_7B vs η²_1.3B bar chart
    bar_pass1_by_condition.png      # pass@1 per condition × benchmark at 7B
    strip_per_seed.png              # per-seed pass@1 scatter (variance check)
    scale_attenuation_scatter.png   # x=η²_1.3B, y=η²_7B per benchmark
```

---

## Module Interfaces

### config.py (`experiments/h-c1/config.py`)

**Dependencies**: none

```python
MODEL_ID: str = "deepseek-ai/deepseek-coder-7b-base"
CONDITIONS: list[str] = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS: list[int] = [42, 123, 777]
EPOCHS: int = 3                          # uniform across conditions (7B token budget matched)
H_E2_DATA_DIR: str                       # abs path to h-e2/data/sft_sources/
CHECKPOINT_DIR: str                      # abs path to h-c1/checkpoints/
RESULTS_JSON: str                        # abs path to h-c1/results/all_results.json
RESULTS_CSV: str
FIGURES_DIR: str                         # abs path to docs/youra_research/h-c1/figures/
H_E2_ETA2: dict[str, float]             # {"humaneval": 0.83, "mbpp": ...} from H-E2 report
FIXED_HPARAMS: dict                      # lr=2e-5, cosine, warmup=0.03, bs=4, ga=8, bf16=True
```

---

### data_loader.py (`experiments/h-c1/data_loader.py`)

**Dependencies**: config.py, `datasets` (load_from_disk)

```python
def load_condition_dataset(condition: str) -> Dataset:
    """Load Arrow dataset from H-E2 data dir for given condition."""
    ...

def verify_datasets() -> dict[str, int]:
    """Return {condition: n_examples}; raise if any condition missing."""
    ...
```

---

### train.py (`experiments/h-c1/train.py`)

**Dependencies**: config.py, data_loader.py, transformers, trl

```python
def set_all_seeds(seed: int) -> None: ...

def load_model_and_tokenizer(model_id: str = MODEL_ID) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """bf16, Flash Attention 2, trust_remote_code=True."""
    ...

def run_sft(
    condition: str,
    seed: int,
    smoke: bool = False,
) -> str:
    """Train one run; return checkpoint path. Skips if checkpoint exists."""
    ...

def main() -> None:
    """CLI: --condition --seed [--smoke]"""
    ...
```

CLI args: `--condition {humaneval_only|mbpp_only|leetcode_only|equal_mix} --seed {42|123|777} [--smoke]`

Key delta from H-E2 train.py:
- `MODEL_ID` = `deepseek-ai/deepseek-coder-7b-base`
- `attn_implementation="flash_attention_2"` in `from_pretrained`
- Uniform `num_train_epochs=3` (no per-condition variable epochs)
- `gradient_accumulation_steps=8` (4× H100, effective batch 32)
- No activation verification call (gate is SHOULD_WORK, not MUST_WORK)

---

### evaluate.py (`experiments/h-c1/evaluate.py`)

**Dependencies**: config.py, evalplus, subprocess

```python
def run_evalplus(checkpoint_dir: str, benchmark: str, output_dir: str) -> dict:
    """Two-step: evalplus.codegen → evalplus.evaluate. Returns {stdout, output_path}."""
    ...

def parse_evalplus_output(output_path: str, stdout: str) -> float:
    """Extract pass@1 float from JSON or stdout."""
    ...

def evaluate_checkpoint(
    condition: str,
    seed: int,
    benchmark: str,
    checkpoint_dir: str,
    results_json: str,
) -> float:
    """Run eval; append to results.json atomically. Return pass@1."""
    ...

def main() -> None:
    """CLI: --condition --seed --benchmark --checkpoint_dir [--smoke]"""
    ...
```

Output schema (`all_results.json`):
```json
{
  "humaneval_only": {
    "42": {"humaneval": 0.512, "mbpp": 0.423},
    "123": {...},
    "777": {...}
  },
  ...
}
```

---

### analyze.py (`experiments/h-c1/analyze.py`)

**Dependencies**: config.py, pandas, numpy, statsmodels, scipy

```python
def load_results(results_json: str) -> pd.DataFrame:
    """Flatten nested JSON to long DataFrame: [condition, seed, benchmark, pass1]."""
    ...

def compute_eta_squared_anova(df: pd.DataFrame, benchmark: str) -> float:
    """One-way ANOVA η² = SS_between / SS_total across 4 conditions (aggregate means)."""
    ...

def compare_effect_sizes(
    eta2_7b: dict[str, float],
    eta2_1b: dict[str, float],
) -> dict:
    """Return {benchmark: {eta2_7b, eta2_1b, attenuated: bool}} for gate eval."""
    ...

def fit_mixedlm(df: pd.DataFrame, benchmark: str):
    """MixedLM: pass1 ~ C(source_condition) | seed (random intercept)."""
    ...

def write_report(gate: dict, eta2: dict, report_path: str) -> None: ...

def main() -> None:
    """CLI: --results_json --report_out [--smoke]"""
    ...
```

Gate logic: `SHOULD_WORK` passes if `η²_7B < η²_1.3B` for ≥1 benchmark. Null result documented, does not block pipeline.

---

### figures.py (`experiments/h-c1/figures.py`)

**Dependencies**: config.py, analyze.py, matplotlib, seaborn, pandas

```python
def plot_eta2_comparison(
    eta2_7b: dict[str, float],
    eta2_1b: dict[str, float],
    out_path: str,
) -> None:
    """MANDATORY: grouped bar η²_7B vs η²_1.3B per benchmark."""
    ...

def plot_bar_pass1(df: pd.DataFrame, out_path: str) -> None:
    """pass@1 mean ± std per condition × benchmark at 7B."""
    ...

def plot_strip_per_seed(df: pd.DataFrame, out_path: str) -> None:
    """Per-seed pass@1 strip plot per condition × benchmark."""
    ...

def plot_scale_attenuation_scatter(
    eta2_7b: dict[str, float],
    eta2_1b: dict[str, float],
    out_path: str,
) -> None:
    """x=η²_1.3B, y=η²_7B, diagonal = no attenuation."""
    ...

def generate_all(df: pd.DataFrame, eta2_7b: dict, eta2_1b: dict, figures_dir: str) -> None:
    """Generate and save all 4 figures."""
    ...
```

---

## Data Flow

```
H-E2 Arrow datasets (4 conditions)
    │  data_loader.load_condition_dataset()
    ▼
train.py (per condition × seed, 12 runs)
    │  SFTTrainer → save_model()
    ▼
checkpoints/condition_{cond}_seed_{seed}/
    │  evaluate.run_evalplus()
    ▼
results/all_results.json  ←── 24 (condition×seed×benchmark) pass@1 scores
    │  analyze.load_results() + compute_eta_squared_anova()
    ▼
η²_7B dict  +  H_E2_ETA2 (from config, hardcoded from H-E2 report)
    │  compare_effect_sizes() → gate dict
    │  write_report()
    ▼
results/statistical_report.txt
    │  figures.generate_all()
    ▼
docs/youra_research/h-c1/figures/ (4 PNGs)
```

---

## Parallelization Strategy

**Phase 1 — Training (sequential within GPU budget):**
- 4× H100 needed per run (7B bf16 + ZeRO-3 = ~28GB sharded across 4 GPUs)
- Runs are sequential: one run at a time occupies all 4 GPUs
- Total wall time: 12 runs × ~2h = ~24h

```bash
# run_all.sh inner loop
for condition in humaneval_only mbpp_only leetcode_only equal_mix; do
  for seed in 42 123 777; do
    torchrun --nproc_per_node=4 train.py --condition $condition --seed $seed
  done
done
```

**Phase 2 — Evaluation (parallelizable across GPUs):**
- Each EvalPlus codegen run needs 1 GPU
- Can run up to 4 evals concurrently (one per H100), each on `CUDA_VISIBLE_DEVICES={0,1,2,3}`
- 24 evals / 4 parallel = 6 batches × ~30min = ~3h

```bash
# evaluate.py uses CUDA_VISIBLE_DEVICES=$GPU_ID for codegen
# run_all.sh schedules 4 parallel eval jobs with sem -j4
```

**Phase 3 — Analysis + Figures (CPU-only, minutes):**
- Single-threaded; runs after all results collected

**Sequencing constraint**: All 12 training runs must complete before eval; all 24 evals must complete before analyze.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-E2 datasets | `datasets.load_from_disk(H_E2_DATA_DIR / condition)` | `docs/youra_research/h-e2/data/sft_sources/{condition}/` |
| H-E2 η² reference | hardcoded in `config.H_E2_ETA2` | derived from H-E2 `statistical_report.txt` |

**Verified from**: `docs/youra_research/h-e2/data/sft_sources/` (Arrow files present for all 4 conditions)

H-C1 does **not** import H-E2 Python modules directly — it reuses the serialized datasets and numeric results only.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + data_loader | config.py constants; data_loader.py loads H-E2 Arrow, verifies 4 conditions | 6 | 2+1+1+2 |
| A-2 | train.py | Adapt H-E2 train.py: MODEL_ID→7B, Flash Attn 2, uniform epochs=3, ga=8, no activation check | 10 | 3+2+2+3 |
| A-3 | ds_config.json | ZeRO-3 config for 7B bf16 on 4× H100; offload_optimizer if OOM | 7 | 2+2+1+2 |
| A-4 | evaluate.py | Port H-E2 evaluate.py; switch CSV→JSON output; add GPU-slot arg for parallel eval | 9 | 2+3+2+2 |
| A-5 | analyze.py + η² | Port H-E2 analyze.py; add compute_eta_squared_anova(); compare_effect_sizes() vs H-E2 reference; gate logic | 12 | 3+3+3+3 |
| A-6 | figures.py | 4 figures: eta2_comparison (mandatory), bar_pass1, strip_per_seed, scale_attenuation_scatter | 10 | 2+2+3+3 |
| A-7 | run_all.sh | Orchestration: sequential train loop → parallel eval (sem -j4) → analyze → figures | 8 | 2+3+1+2 |
| A-8 | test_smoke.py | Smoke tests: data_loader (file exists), train (5 steps, tiny dataset), evaluate (evalplus import), analyze (synthetic df), figures (render to /tmp) | 9 | 2+2+2+3 |

**Distribution**: High(10-12): [A-2, A-5, A-6], Medium(7-9): [A-3, A-4, A-7, A-8], Low(4-6): [A-1]

**Total task count**: 8 (within LIGHT tier 15-task budget)
