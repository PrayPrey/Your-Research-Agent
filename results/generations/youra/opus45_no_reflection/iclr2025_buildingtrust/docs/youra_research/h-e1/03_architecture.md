# Architecture: H-E1 (EXISTENCE)

Applied: evaluation-only pipeline pattern (no training loop; sequential model eval → aggregate → stats)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch using lm-evaluation-harness + TextAttack as external frameworks

---

## File Organization

```
h-e1/code/
├── config.py          # model list, dataset ids, seeds, thresholds
├── run_eval.py         # per-model MC1 + TextFooler eval loop, saves results.json
├── analyze.py          # correlation stats (Pearson, bootstrap CI, partial r)
└── visualize.py        # required + supporting figures
```

No `model.py`/`train.py` — this is evaluation-only (no model architecture proposed, no training).

---

## Modules

### config.py

```python
MODEL_IDS: list[str]          # 12 HF model ids (see PRD FR-2)
MODEL_FAMILY: dict[str, str]  # model_id -> family name (llama2/llama3/mistral/flan-t5/phi)
MODEL_PARAMS: dict[str, float]  # model_id -> param count (for log(params))
SEED: int = 42
N_BOOTSTRAP: int = 1000
TRUTHFULQA_TASK = "truthfulqa_mc1"
TEXTFOOLER_NUM_EXAMPLES = 1000
BATCH_SIZE = 4
RESULTS_PATH = "results/results.json"
```

### run_eval.py (`code/run_eval.py`)

**Dependencies**: config.py, lm_eval, textattack

```python
def eval_truthfulqa_mc1(model_id: str, batch_size: int) -> float: ...
def eval_textfooler_asr(model_id: str, num_examples: int) -> float: ...
def run_all(model_ids: list[str]) -> dict: ...  # returns {"model":[], "mc1_acc":[], "robustness":[], "log_params":[]}
def save_results(results: dict, path: str) -> None: ...
```

### analyze.py (`code/analyze.py`)

**Dependencies**: results.json (from run_eval.py), scipy, numpy, sklearn

```python
def pearson_correlation(x: list[float], y: list[float]) -> tuple[float, float]: ...
def bootstrap_ci(x: list[float], y: list[float], n_boot: int, seed: int) -> tuple[float, float]: ...
def partial_correlation(x: list[float], y: list[float], control: list[float]) -> tuple[float, float]: ...
def evaluate_hypothesis(results: dict) -> dict: ...  # r, p_value, ci_95, partial_r, partial_p, pass
def save_analysis(analysis: dict, path: str) -> None: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: results.json, analysis.json (from analyze.py), matplotlib

```python
def plot_gate_metrics(results: dict, analysis: dict, out_path: str) -> None: ...      # required: MC1 vs (1-ASR), regression + CI band
def plot_correlation_heatmap(results: dict, out_path: str) -> None: ...
def plot_bootstrap_distribution(bootstrap_rs: list[float], ci: tuple, out_path: str) -> None: ...
def plot_within_family(results: dict, out_path: str) -> None: ...
def plot_partial_correlation(results: dict, out_path: str) -> None: ...
def generate_all_figures(results: dict, analysis: dict, out_dir: str) -> None: ...
```

**Figures** saved to `{hypothesis_folder}/figures/`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup config & data loading | model list, dataset loaders (TruthfulQA, SST-2) | 6 | 2+1+1+2 |
| A-2 | TruthfulQA MC1 evaluation | lm-eval-harness wrapper across 12 models | 10 | 3+3+2+2 |
| A-3 | TextFooler attack evaluation | TextAttack wrapper across 12 models, ASR extraction | 12 | 3+4+3+2 |
| A-4 | Results aggregation | run_eval orchestration, JSON export, GPU memory handling for 70B | 8 | 2+2+2+2 |
| A-5 | Correlation statistics | Pearson r/p, bootstrap CI, partial correlation | 9 | 2+2+3+2 |
| A-6 | Required visualization | gate metrics scatter (MC1 vs 1-ASR, regression, CI band) | 6 | 2+1+2+1 |
| A-7 | Supporting visualizations | heatmap, bootstrap histogram, within-family, partial corr plots | 7 | 3+1+1+2 |
| A-8 | End-to-end run + gate check | full pipeline execution, pass/fail against gate thresholds | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5], Low(4-8): [A-1, A-6, A-7, A-8]

Total: 8 tasks (within LIGHT tier max 15).

---

## Notes

- No training required — all modules are inference/evaluation/analysis only.
- 70B models (M03, M05) require sequential/offloaded processing per NFR-3 fallback; handled in A-4 orchestration, not a separate module.
- ECE and mediation analysis explicitly out of scope (deferred to H-M1/H-M3 per PRD).
