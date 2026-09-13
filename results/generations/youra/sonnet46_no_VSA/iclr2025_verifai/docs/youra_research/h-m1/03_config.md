# H-M1 Configuration

Oracle isolation experiment — CPU-only evaluation, no LLM inference.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: Config classes verified from h-e1/code/config.py
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Configuration Schema

```python
# h-m1/code/config.py
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class ExperimentConfig:
    # --- Dataset ---
    contracteval_jsonl: str = ""          # path to ContractEval.jsonl (set at runtime)
    evalplus_split: str = "test"          # evalplus dataset split
    n_tasks: int = 364                    # total tasks in ContractEval HumanEval+/MBPP+ subset
    n_static_inputs: int = 764            # base_input + plus_input per task (EvalPlus)
    task_id_overlap_min: float = 0.90    # abort if ContractEval/EvalPlus overlap < 90%
    quarantine_threshold: int = 1        # exclude task if >= 1 contract failure on reference impl

    # --- H-E1 program corpus ---
    he1_corpus_dir: str = ""             # path to h-e1/code/data/samples/ (set at runtime)
    models: list = field(default_factory=lambda: [
        "gpt-4o-mini",
        "claude-3-haiku-20240307",
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
    ])
    # Subdirectory names inside he1_corpus_dir for each model
    model_subdirs: dict = field(default_factory=lambda: {
        "gpt-4o-mini":                                 "gpt-4o-mini",
        "claude-3-haiku-20240307":                     "claude-3-haiku-20240307",
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct": "deepseek-ai__DeepSeek-Coder-V2-Lite-Instruct",
        "codellama/CodeLlama-13b-Instruct-hf":         "codellama__CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf":         "codellama__CodeLlama-34b-Instruct-hf",
    })

    # --- Execution ---
    exec_timeout: float = 5.0            # seconds per (program, input) execution
    n_workers: int = 0                   # multiprocessing workers; 0 = cpu_count()
    seed: int = 42

    # --- Soundness pre-check (Hypothesis/icontract-hypothesis) ---
    soundness_budget: int = 100_000      # Hypothesis examples per task
    soundness_seed: int = 42
    soundness_wall_clock_limit: int = 7200  # 2h in seconds

    # --- Statistical analysis ---
    n_bootstrap: int = 10_000
    ci_percentiles: tuple = (2.5, 97.5)  # 95% CI
    wilcoxon_alpha: float = 0.01         # after Holm correction
    holm_method: str = "holm"            # statsmodels multipletests method string

    # --- Success thresholds ---
    gap_threshold: float = 0.10          # oracle gap >= 0.10 to consider meaningful
    contract_unique_mass_min: float = 0.05   # contract-unique failure mass >= 0.05
    contract_unique_ci_lower: float = 0.03   # CI lower bound for unique mass

    # --- Output ---
    results_dir: str = "results"
    figures_dir: str = "figures"
    outputs_dir: str = "outputs"
    results_json: str = "oracle_isolation_results.json"
    results_csv: str = "oracle_isolation_results.csv"
    results_md: str = "oracle_isolation_summary.md"
    quarantine_log: str = "quarantined_tasks.json"
    soundness_log: str = "soundness_precheck.jsonl"

    # --- Pilot mode ---
    pilot: bool = False                  # if True, run on 10 random tasks only
    pilot_n_tasks: int = 10
    pilot_seed: int = 42                 # random.seed for pilot task sampling
```

---

## Runtime Config Factory

```python
def default_config() -> ExperimentConfig:
    base = Path(__file__).parent
    archive_root = (
        base.parent.parent.parent
        / "_archive/20260803T121822_routing_recovery"
        / ".data_cache/datasets/ContractEval/data/ContractEval"
    )
    he1_samples = (
        base.parent.parent
        / "h-e1/code/data/samples"
    )

    cfg = ExperimentConfig()
    cfg.contracteval_jsonl = os.environ.get(
        "CONTRACTEVAL_JSONL",
        str(archive_root / "ContractEval.jsonl"),
    )
    cfg.he1_corpus_dir = os.environ.get(
        "HE1_CORPUS_DIR",
        str(he1_samples),
    )
    cfg.results_dir = str(base / "results")
    cfg.figures_dir = str(base.parent / "figures")
    cfg.outputs_dir = str(base / "outputs")
    return cfg
```

---

## Environment Variables

| Variable | Overrides | Example |
|---|---|---|
| `CONTRACTEVAL_JSONL` | `contracteval_jsonl` | `/data/ContractEval.jsonl` |
| `HE1_CORPUS_DIR` | `he1_corpus_dir` | `/data/h-e1/samples/` |

---

## Validation Logic

Run at startup before any experiment work:

```python
import multiprocessing
from pathlib import Path


def validate_config(cfg: ExperimentConfig) -> None:
    errors = []

    # Paths
    if not Path(cfg.contracteval_jsonl).exists():
        errors.append(f"contracteval_jsonl not found: {cfg.contracteval_jsonl}")
    if not Path(cfg.he1_corpus_dir).is_dir():
        errors.append(f"he1_corpus_dir not found: {cfg.he1_corpus_dir}")
    for model, subdir in cfg.model_subdirs.items():
        p = Path(cfg.he1_corpus_dir) / subdir
        if not p.exists():
            errors.append(f"Missing H-E1 output dir for {model}: {p}")

    # Parameter ranges
    if not (0.0 < cfg.task_id_overlap_min <= 1.0):
        errors.append("task_id_overlap_min must be in (0, 1]")
    if cfg.exec_timeout <= 0:
        errors.append("exec_timeout must be > 0")
    if cfg.n_bootstrap < 1000:
        errors.append("n_bootstrap < 1000 is too low for stable CIs")
    if not (0.0 < cfg.wilcoxon_alpha < 1.0):
        errors.append("wilcoxon_alpha out of range")
    if cfg.n_workers < 0:
        errors.append("n_workers must be >= 0")

    if errors:
        raise ValueError("Config validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    # Resolve workers
    if cfg.n_workers == 0:
        cfg.n_workers = multiprocessing.cpu_count()
```

---

## Pilot vs Full Run

```python
# Full run (default)
cfg = default_config()

# Pilot: 10 random tasks
cfg = default_config()
cfg.pilot = True
```

When `cfg.pilot is True`, the runner samples `pilot_n_tasks` task IDs using `random.seed(pilot_seed)` before execution. All other parameters remain identical.

---

## Concrete Instantiation Example

```python
cfg = ExperimentConfig(
    contracteval_jsonl="/data/ContractEval/ContractEval.jsonl",
    evalplus_split="test",
    n_tasks=364,
    n_static_inputs=764,
    task_id_overlap_min=0.90,
    quarantine_threshold=1,
    he1_corpus_dir="/home/user/h-e1/code/data/samples",
    models=[
        "gpt-4o-mini",
        "claude-3-haiku-20240307",
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
    ],
    exec_timeout=5.0,
    n_workers=0,          # resolved to cpu_count() at validate_config()
    seed=42,
    soundness_budget=100_000,
    soundness_seed=42,
    soundness_wall_clock_limit=7200,
    n_bootstrap=10_000,
    ci_percentiles=(2.5, 97.5),
    wilcoxon_alpha=0.01,
    holm_method="holm",
    gap_threshold=0.10,
    contract_unique_mass_min=0.05,
    contract_unique_ci_lower=0.03,
    results_dir="results",
    figures_dir="figures",
    outputs_dir="outputs",
    results_json="oracle_isolation_results.json",
    results_csv="oracle_isolation_results.csv",
    results_md="oracle_isolation_summary.md",
    quarantine_log="quarantined_tasks.json",
    soundness_log="soundness_precheck.jsonl",
    pilot=False,
    pilot_n_tasks=10,
    pilot_seed=42,
)
```

---

## Dependency Requirements

Python >= 3.10

```
# requirements.txt (h-m1)
evalplus>=0.3.0
icontract>=2.6.6
icontract-hypothesis>=1.1.7
hypothesis>=6.100.0
scipy>=1.10.0
statsmodels>=0.14.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
tqdm>=4.65.0
```

Note: No torch, no transformers. CPU-only. LLM inference not required — H-E1 program corpus is consumed as pre-generated JSONL files.
