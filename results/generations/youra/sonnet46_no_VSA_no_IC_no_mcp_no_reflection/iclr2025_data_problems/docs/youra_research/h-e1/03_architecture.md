# Architecture: H-E1 — Corpus Curation Generalization Balance (EXISTENCE PoC)

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Type:** EXISTENCE (PoC)
**Experiment Type:** Evaluation-only pipeline

Applied: Pipeline-Stage-Isolation pattern — each stage writes results to disk before next stage starts, enabling resume-on-failure.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing codebase to analyze. Serena MCP skipped per green-field rule.
**Analyzed Path:** N/A
**Findings:** New implementation from scratch.

---

## File Structure

```
docs/youra_research/h-e1/
├── code/
│   ├── precondition_check.py   # FR-1: checkpoint existence + token count verification
│   ├── evaluator.py            # FR-2/3: lm-eval CLI wrapper for both models
│   ├── metrics.py              # FR-4/5: ratio/delta, bootstrap CI, Cohen's d, pass/fail
│   ├── figures.py              # FR-6: 4 required figures
│   ├── config.py               # single fixed config (model IDs, revisions, paths)
│   └── run.py                  # entry point: orchestrates all stages in order
├── results/
│   ├── pythia-6.9b-300B/       # lm-eval JSON output
│   └── olmo-7b-300B/           # lm-eval JSON output
└── figures/                    # saved figure files
```

---

## Data Flow

```
config.py
    ↓
precondition_check.py  →  verify HF revisions exist + token match <10%
    ↓
evaluator.py           →  run lm_eval CLI for Pythia → results/pythia-6.9b-300B/
                       →  run lm_eval CLI for OLMo   → results/olmo-7b-300B/
    ↓
metrics.py             →  load both results JSONs → compute ratio/delta/bootstrap/Cohen's d → pass/fail
    ↓
figures.py             →  load metrics output → write 4 figures to figures/
```

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies:** none

```python
PYTHIA_ID = "EleutherAI/pythia-6.9b"
PYTHIA_REVISION = "step143000"
PYTHIA_TOKENS = 143_000 * 2_097_152  # ~300B

OLMO_ID = "allenai/OLMo-7B-hf"
OLMO_REVISION = "step149531"         # verify at runtime
OLMO_TOKENS = 149_531 * 2_000_000   # ~300B; ponytail: approximate, precondition_check verifies

TASKS = ["mmlu", "hellaswag", "arc_easy", "arc_challenge"]
FEWSHOT_MAP = {"mmlu": 5, "hellaswag": 0, "arc_easy": 25, "arc_challenge": 25}
TARGET_TOKENS = 300e9
TOKEN_TOLERANCE = 0.10
BOOTSTRAP_N = 1000
SEED = 42
RESULTS_DIR = "results"
FIGURES_DIR = "docs/youra_research/h-e1/figures"
```

---

### PreconditionChecker (`code/precondition_check.py`)

**Dependencies:** config, huggingface_hub

```python
def check_revision_exists(model_id: str, revision: str) -> bool: ...
    # Uses huggingface_hub.list_repo_refs; returns True if revision in branches

def check_token_match(revision: str, tokens_per_step: int) -> bool: ...
    # Parses step number from revision string; checks abs(tokens - TARGET_TOKENS) / TARGET_TOKENS < TOKEN_TOLERANCE

def sanity_eval(model_id: str, revision: str, output_dir: str) -> bool: ...
    # Runs lm_eval with --tasks mmlu_abstract_algebra --limit 50; returns True on success

def run_all_checks() -> None: ...
    # Calls above three functions for both models; raises SystemExit on any failure
```

---

### Evaluator (`code/evaluator.py`)

**Dependencies:** config, subprocess, pathlib

```python
def build_lm_eval_cmd(
    model_id: str,
    revision: str,
    output_dir: str,
    limit: int | None = None
) -> list[str]: ...
    # Returns lm_eval CLI args list with --log_samples and --batch_size auto

def run_evaluation(model_id: str, revision: str, output_dir: str) -> pathlib.Path: ...
    # Checks if output_dir/results.json already exists (skip if so); runs CLI; returns results path
    # ponytail: skip-on-existing-output enables resume; invalidate manually if re-run needed

def load_results(results_path: pathlib.Path) -> dict: ...
    # Returns json.load(results_path)["results"]

def evaluate_both_models() -> tuple[dict, dict]: ...
    # Evaluates Pythia then OLMo; returns (pythia_results, olmo_results)
```

---

### MetricComputer (`code/metrics.py`)

**Dependencies:** config, numpy, scipy.stats

```python
def compute_ratio(results: dict) -> float: ...
    # mean(MMLU subject accs) / hellaswag acc

def compute_arc_delta(results: dict) -> float: ...
    # arc_challenge acc_norm - arc_easy acc

def bootstrap_ratio_diff(
    pythia_results: dict,
    olmo_results: dict,
    n: int = BOOTSTRAP_N,
    seed: int = SEED
) -> dict: ...
    # Returns {mean_diff, ci_95: [lo, hi], p_value (one-sided)}

def cohens_d(bootstrap_diffs: np.ndarray) -> float: ...
    # d = mean(diffs) / std(diffs)

def evaluate_hypothesis(pythia_results: dict, olmo_results: dict) -> dict: ...
    # Returns {
    #   pythia_ratio, olmo_ratio, ratio_diff,
    #   arc_delta_pythia, arc_delta_olmo,
    #   bootstrap: {...}, cohens_d,
    #   primary_pass: bool, secondary_pass: bool,
    #   verdict: "CONFIRMED" | "FAILED"
    # }
```

---

### FigureGenerator (`code/figures.py`)

**Dependencies:** metrics output dict, matplotlib, seaborn, pathlib

```python
def fig_absolute_scores(pythia_results: dict, olmo_results: dict, out_dir: str) -> None: ...
    # FR-6.1: side-by-side bar chart, 4 tasks, saves absolute_scores.png

def fig_ratio_delta(metrics: dict, out_dir: str) -> None: ...
    # FR-6.2: bar chart with 95% CI error bars for ratio and arc_delta, saves ratio_delta.png

def fig_mmlu_heatmap(pythia_results: dict, olmo_results: dict, out_dir: str) -> None: ...
    # FR-6.3: 57×2 heatmap of per-subject MMLU accuracy, saves mmlu_heatmap.png

def fig_bootstrap_dist(metrics: dict, out_dir: str) -> None: ...
    # FR-6.4: histogram of bootstrap diffs, vertical lines at 0 and 0.02, saves bootstrap_dist.png

def generate_all(pythia_results: dict, olmo_results: dict, metrics: dict) -> None: ...
    # Calls all four above; creates out_dir if missing
```

---

### Orchestrator (`code/run.py`)

**Dependencies:** all modules above

```python
def main() -> None: ...
    # 1. run_all_checks()
    # 2. pythia_results, olmo_results = evaluate_both_models()
    # 3. metrics = evaluate_hypothesis(pythia_results, olmo_results)
    # 4. generate_all(pythia_results, olmo_results, metrics)
    # 5. print verdict + save metrics to results/metrics_summary.json

if __name__ == "__main__":
    main()
```

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| lm-eval | ==0.4.3 | Core evaluation framework (CLI) |
| torch | >=2.0.0 | Model inference backend |
| transformers | >=4.40.0 | HuggingFace model loading |
| huggingface_hub | >=0.20.0 | Revision existence checks |
| accelerate | >=0.27.0 | Multi-GPU / device_map support |
| numpy | >=1.24.0 | Bootstrap computation |
| scipy | >=1.11.0 | Stats (used for cohens_d cross-check) |
| matplotlib | >=3.7.0 | Figures |
| seaborn | >=0.12.0 | Heatmap figure |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown | Type |
|----|------|-------------|------------|-----------|------|
| E1 | Project setup | Create directory layout, requirements.txt, config.py with all constants. Verify lm-eval install. | 4 | 1+1+1+1 | setup |
| E2 | Precondition checker | Implement check_revision_exists, check_token_match, sanity_eval, run_all_checks. Covers FR-1.1–1.3. | 8 | 2+2+2+2 | data-pipeline |
| E3 | Evaluator | Implement lm-eval CLI wrapper with skip-on-existing-output resume logic. Covers FR-2 and FR-3. | 9 | 2+2+3+2 | evaluation |
| E4 | Metric computer | Implement ratio, arc_delta, bootstrap CI (n=1000), Cohen's d, pass/fail verdict. Covers FR-4 and FR-5. | 10 | 2+2+4+2 | analysis |
| E5 | Figure generator | Implement all 4 figures (absolute scores, ratio/delta with CI, MMLU heatmap, bootstrap hist). Covers FR-6. | 9 | 2+2+3+2 | visualization |
| E6 | Orchestrator + integration test | Implement run.py main(); add end-to-end smoke test using --limit 50 on both models. | 7 | 1+3+1+2 | setup |

**Distribution**: High(8-10): [E3, E4, E5], Medium(6-9): [E2, E6], Low(4-5): [E1]

**Total Complexity**: 47 points across 6 tasks.
