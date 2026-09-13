# Configuration: H-E1 — ContractEval Contract-Strength Gap

Applied: sequential-pipeline dataclass pattern (fixed single config, EXISTENCE PoC)
Applied: YAML-backed dataclass pattern (Stability-AI/generative-models config style)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config design
**Pattern Used**: dataclass (single fixed config, no variations)

---

## Main Configuration (`h-e1/code/config.py`)

```python
from dataclasses import dataclass, field


@dataclass
class Config:
    # Data paths
    contracteval_dir: str = "./ContractEval/data"
    samples_dir: str = "data/samples"
    results_dir: str = "results"
    figures_dir: str = "figures"

    # Models (5 fixed LLMs)
    models: list[str] = field(default_factory=lambda: [
        "gpt-4o-mini",
        "claude-3-haiku-20240307",
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
    ])

    # Oracle soundness pre-check
    oracle_budget: int = 100_000
    oracle_timeout: int = 30       # seconds per task; total wall-clock ~2h

    # PBT contract checking
    pbt_budget: int = 5_000
    pbt_seed: int = 42
    pbt_timeout: int = 60          # seconds per check

    # Code generation
    n_samples: int = 10
    temperature: float = 0.8

    # Metrics
    n_bootstrap: int = 10_000
    gate_threshold: float = 0.01   # CI_lower > 0.01 → PASS

    # Rerun control flags
    skip_generation: bool = False  # True: use cached samples_dir
    skip_oracle: bool = False      # True: use cached oracle_precheck.jsonl
    skip_pbt: bool = False         # True: use cached pbt_results_*.jsonl


CFG = Config()  # single global instance for direct import
```

---

## YAML Config Schema

```yaml
# config.yaml — mirrors Config dataclass for reference/override
data:
  contracteval_dir: "./ContractEval/data"
  samples_dir: "data/samples"
  results_dir: "results"
  figures_dir: "figures"

models:
  - "gpt-4o-mini"
  - "claude-3-haiku-20240307"
  - "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
  - "codellama/CodeLlama-13b-Instruct-hf"
  - "codellama/CodeLlama-34b-Instruct-hf"

oracle:
  budget: 100000
  timeout: 30

pbt:
  budget: 5000
  seed: 42
  timeout: 60

generation:
  n_samples: 10
  temperature: 0.8

metrics:
  n_bootstrap: 10000
  gate_threshold: 0.01

flags:
  skip_generation: false
  skip_oracle: false
  skip_pbt: false
```

---

## A-7: Orchestration — Wiring + E2E Test [Complexity: 10, Budget: 2 subtasks]

Applied: skip-flag rerun pattern (partial pipeline re-execution via boolean guards)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Pipeline Wiring Spec | Step order, skip-flag logic, exit code convention |
| C-7-2 | E2E Smoke Test Spec | Small-scale smoke: 5 tasks, 1 model, n=2, budget=100 |

---

## C-7-1: Pipeline Wiring Spec

`run_experiment.py` executes steps sequentially. Each step guarded by a skip flag that checks for cached output before running.

```python
def main(cfg: Config = Config()) -> None:
    # Step 1: Load dataset (always runs — fast)
    tasks = load_contracteval(cfg.contracteval_dir)
    z3_ids = get_z3_tractable_ids(tasks)

    # Step 2: Oracle soundness pre-check
    oracle_cache = Path(cfg.results_dir) / "oracle_precheck.jsonl"
    if cfg.skip_oracle and oracle_cache.exists():
        valid_ids, quarantined_ids = _load_oracle_cache(oracle_cache)
    else:
        valid_ids, quarantined_ids = run_soundness_precheck(
            tasks,
            budget=cfg.oracle_budget,
            seed=cfg.pbt_seed,
            results_path=str(oracle_cache),
        )

    # Step 3: Per-model generation + contract checking
    all_pbt_results = []
    for model in cfg.models:
        model_slug = model.replace("/", "_")

        # Step 3a: Code generation
        for dataset in ("humaneval", "mbpp"):
            samples_path = Path(cfg.samples_dir) / model_slug / f"{dataset}.jsonl"
            if cfg.skip_generation and samples_path.exists():
                filtered_path = _cached_filtered_path(samples_path)
            else:
                raw_path = generate_samples(
                    model, dataset, str(samples_path.parent),
                    n=cfg.n_samples, temperature=cfg.temperature,
                )
                filtered_path = run_evalplus_filter(raw_path, dataset)

            passing = load_passing_samples(filtered_path)

            # Step 3b: PBT contract checking
            pbt_cache = Path(cfg.results_dir) / f"pbt_results_{model_slug}_{dataset}.jsonl"
            if cfg.skip_pbt and pbt_cache.exists():
                results = _load_jsonl(pbt_cache)
            else:
                results = run_contract_checking(
                    tasks, passing, model, valid_ids,
                    budget=cfg.pbt_budget,
                    seed=cfg.pbt_seed,
                    timeout=cfg.pbt_timeout,
                    results_path=str(pbt_cache),
                )
            all_pbt_results.extend(results)

    # Step 4: Aggregate metrics
    metrics = aggregate_metrics(all_pbt_results, z3_ids)

    # Step 5: Save results
    summary_path = Path(cfg.results_dir) / "summary.json"
    summary_path.write_text(json.dumps(metrics, indent=2))
    _write_summary_report(metrics, Path(cfg.results_dir) / "summary_report.md")

    # Step 6: Figures
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    plot_gap_vs_baseline(metrics["mean_gap"], metrics["ci_lower"], metrics["ci_upper"],
                         f"{cfg.figures_dir}/gap_vs_baseline.png")
    plot_per_model_boxplot(all_pbt_results, f"{cfg.figures_dir}/per_model_gap.png")
    plot_per_task_histogram(compute_per_task_gap(all_pbt_results),
                            f"{cfg.figures_dir}/per_task_histogram.png")
    plot_cumulative_gap(compute_per_task_gap(all_pbt_results),
                        f"{cfg.figures_dir}/cumulative_gap.png")
    plot_soundness_summary(valid_ids, quarantined_ids,
                           f"{cfg.figures_dir}/soundness_summary.png")

    # Exit convention: 0 = gate passed, 1 = gate failed (CI_lower <= threshold)
    gate = metrics.get("gate_passed", False)
    print(f"GATE: {'PASS' if gate else 'FAIL'} — mean_gap={metrics['mean_gap']:.4f} "
          f"CI=[{metrics['ci_lower']:.4f}, {metrics['ci_upper']:.4f}]")
    sys.exit(0 if gate else 1)
```

**Exit codes**: `0` = gate passed (CI_lower > 0.01), `1` = gate failed.

**Partial rerun examples**:
```bash
# Regenerate only figures (samples + PBT cached)
python run_experiment.py --skip_generation --skip_oracle --skip_pbt

# Redo PBT only (generation cached)
python run_experiment.py --skip_generation --skip_oracle
```

---

## C-7-2: E2E Smoke Test Spec

Smoke config runs the full pipeline at minimal scale to confirm wiring before the full 24h run.

```python
SMOKE_CONFIG = Config(
    contracteval_dir="./ContractEval/data",
    samples_dir="data/smoke_samples",
    results_dir="results/smoke",
    figures_dir="figures/smoke",
    models=["gpt-4o-mini"],          # 1 model only
    oracle_budget=500,               # fast oracle check
    pbt_budget=100,                  # fast PBT
    pbt_seed=42,
    pbt_timeout=10,
    n_samples=2,                     # 2 samples per task
    temperature=0.8,
    n_bootstrap=100,                 # fast bootstrap
    gate_threshold=0.01,
    skip_generation=False,
    skip_oracle=False,
    skip_pbt=False,
)

# In run_experiment.py, add:
SMOKE_TASK_LIMIT = 5  # subset first 5 tasks for smoke
```

Smoke invocation (add `--smoke` flag to `main()`):
```python
if args.smoke:
    cfg = SMOKE_CONFIG
    tasks = dict(list(tasks.items())[:5])  # slice after load_contracteval
```

**Expected smoke outputs** (all must exist, content is secondary):
- `results/smoke/oracle_precheck.jsonl` — 5 entries, quarantined ≤ 1
- `results/smoke/pbt_results_gpt-4o-mini_humaneval.jsonl` — entries present
- `results/smoke/summary.json` — JSON parseable, keys: mean_gap, ci_lower, ci_upper, gate_passed
- `figures/smoke/gap_vs_baseline.png` — file exists, size > 0
- Exit code 0 or 1 (either is acceptable for smoke — just no crash)

**Smoke runtime target**: < 3 minutes on any machine with API access.
