# Architecture: H-E1 — Difficulty-Tier Sample Size Viability Check

**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK gate)
**Type:** FOUNDATION (green-field, no base hypothesis)
**Tier:** LIGHT (EXISTENCE PoC → 3-5 Epic tasks)
**Date:** 2026-03-18

Applied: modular-pipeline (generate → evaluate → analyze → visualize)
Applied: argparse-only config (LIGHT tier, no WandB, no YAML)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze (Serena returned no active project error; glob confirms only .md files exist in h-e1/)
**Analyzed Path:** `docs/youra_research/20260316_verifia/h-e1/`
**Findings:** New implementation from scratch. Only documentation files present (02b_context.md, 02c_experiment_brief.md, 03_prd.md).

---

## File Structure

```
h-e1/code/src/h_e1/
  generate_solutions.py   — model loading + k=5 solution generation
  evaluate_solutions.py   — EvalPlus correctness oracle
  analyze_tiers.py        — pass@1 computation + tier assignment + gate check
  visualize.py            — 4 required figures
  run_experiment.py       — main entry point (argparse CLI)

h-e1/results/
  solutions_{model}.jsonl
  correctness_{model}.json
  pass_at_1_{model}.json
  tier_statistics.csv

h-e1/figures/
  tier_sizes_bar.png
  pass_at_1_distribution.png
  tier_size_heatmap.png
  coverage_rate.png
```

---

## Module Definitions

### SolutionGenerator (`h-e1/code/src/h_e1/generate_solutions.py`)

**Dependencies:** transformers, torch, evalplus.data

```python
MODEL_IDS = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]
GENERATION_CONFIG = dict(
    temperature=0.8, top_p=0.95, max_new_tokens=512, do_sample=True
)
SEED = 42
K = 5

def load_model_and_tokenizer(model_id: str) -> tuple: ...
    # Returns (model, tokenizer) with float16, device_map="auto"

def generate_solutions(
    model,
    tokenizer,
    problems: dict,
    k: int = K,
    seed: int = SEED,
) -> dict:
    # Returns {task_id: [str × k]}

def save_solutions(solutions: dict, output_path: str) -> None:
    # Saves JSONL: {task_id, solutions: [str × 5]}

def load_existing_solutions(path: str) -> dict | None:
    # Returns loaded dict or None if file absent (reuse check)

def main(args) -> None:
    # argparse entry: --model_id, --output_dir, --smoke_test (5 problems only)
```

---

### CorrectnessEvaluator (`h-e1/code/src/h_e1/evaluate_solutions.py`)

**Dependencies:** evalplus.data, evalplus.eval, json

```python
EVALPLUS_PARAMS = dict(
    max_as_limit=30,
    max_data_limit=30,
    max_stack_limit=10,
    min_time_limit=1,
    gt_time_limit_factor=4.0,
)

def load_problems(benchmark: str) -> dict:
    # benchmark in {"humaneval", "mbpp"}
    # Returns problem dict from get_human_eval_plus() or get_mbpp_plus()

def evaluate_solution(
    dataset: str,
    problem: dict,
    solution: str,
) -> bool:
    # Returns passed = (base_status=="pass") and (plus_status=="pass")

def evaluate_model_solutions(
    solutions: dict,
    problems_he: dict,
    problems_mbpp: dict,
) -> dict:
    # Returns {task_id: [bool × k]}

def compute_coverage_rate(correctness: dict, total_problems: int) -> float: ...

def save_correctness(correctness: dict, output_path: str) -> None:
    # Saves JSON: {task_id: [bool × k]}

def main(args) -> None:
    # argparse entry: --solutions_path, --output_dir
```

---

### TierAnalyzer (`h-e1/code/src/h_e1/analyze_tiers.py`)

**Dependencies:** numpy, pandas, json

```python
HARD_THRESHOLD = 0.0
EASY_THRESHOLD = 0.6
MIN_N = 20

def compute_pass_at_1(correctness: dict, k: int = 5) -> dict:
    # Returns {task_id: float} in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}

def assign_tiers(
    pass_at_1: dict,
    hard_thresh: float = HARD_THRESHOLD,
    easy_thresh: float = EASY_THRESHOLD,
) -> dict:
    # Returns {task_id: "hard"|"easy"|"medium"}

def count_tiers(tiers: dict, problem_ids_he: list, problem_ids_mbpp: list) -> dict:
    # Returns {benchmark: {tier: count}} for "humaneval" and "mbpp"

def evaluate_gate(
    tier_counts: dict,
    model_names: list,
    all_tier_counts: dict,
    min_n: int = MIN_N,
) -> dict:
    # Returns {gate_pass: bool, models_passing: int, benchmark_passing: str|None,
    #          n_hard_per: dict, n_easy_per: dict}

def verify_tier_mechanism_activated(
    tier_results: dict,
    coverage_rate: float,
) -> tuple[bool, dict]:
    # Asserts n_hard > 0, n_easy > 0, coverage >= 0.95

def relax_and_retry(
    correctness_all: dict,
    relaxed_hard_thresh: float = 0.2,
) -> dict:
    # Recomputes with hard_thresh=0.2; returns new gate result dict

def save_tier_statistics(stats: list[dict], output_path: str) -> None:
    # CSV: model, benchmark, n_hard, n_easy, n_medium, n_total, coverage_rate, gate_pass

def save_pass_at_1(pass_at_1: dict, output_path: str) -> None:
    # JSON: {task_id: float} per model

def compute_cross_model_overlap(tiers_per_model: dict) -> dict:
    # Jaccard similarity of hard-tier sets across model pairs (prep for H-M2)

def main(args) -> None:
    # argparse entry: --results_dir, --output_dir, --hard_threshold, --easy_threshold
```

---

### Visualizer (`h-e1/code/src/h_e1/visualize.py`)

**Dependencies:** matplotlib, pandas, numpy

```python
def plot_tier_sizes_bar(
    tier_stats: list[dict],
    min_n: int = 20,
    output_path: str = "h-e1/figures/tier_sizes_bar.png",
) -> None:
    # Bar chart: n_hard and n_easy per (model, benchmark) vs threshold n=20

def plot_pass_at_1_distribution(
    pass_at_1_per_model: dict,
    output_path: str = "h-e1/figures/pass_at_1_distribution.png",
) -> None:
    # 6-point histogram per model per benchmark

def plot_tier_size_heatmap(
    tier_stats: list[dict],
    output_path: str = "h-e1/figures/tier_size_heatmap.png",
) -> None:
    # Matrix (model × benchmark) → (n_hard, n_easy)

def plot_coverage_rate(
    coverage_per_model: dict,
    output_path: str = "h-e1/figures/coverage_rate.png",
) -> None:
    # Bar chart: coverage fraction per model

def main(args) -> None:
    # argparse entry: --results_dir, --figures_dir
```

---

### ExperimentRunner (`h-e1/code/src/h_e1/run_experiment.py`)

**Dependencies:** generate_solutions, evaluate_solutions, analyze_tiers, visualize

```python
def parse_args() -> argparse.Namespace:
    # --output_dir, --smoke_test, --skip_generation, --gpu_id, --hard_threshold

def run_pipeline(args) -> dict:
    # Orchestrates: generate → evaluate → analyze → visualize
    # Returns final gate result dict

def print_summary(gate_result: dict) -> None:
    # Prints gate PASS/FAIL with n_hard/n_easy counts per (model, benchmark)

if __name__ == "__main__":
    args = parse_args()
    result = run_pipeline(args)
    print_summary(result)
    sys.exit(0 if result["gate_pass"] else 1)
```

---

## Data Flow

- `run_experiment.py` → calls `generate_solutions.main()` per model → `results/solutions_{model}.jsonl`
- `run_experiment.py` → calls `evaluate_solutions.main()` per model → `results/correctness_{model}.json`
- `run_experiment.py` → calls `analyze_tiers.main()` → `results/pass_at_1_{model}.json`, `results/tier_statistics.csv`
- `run_experiment.py` → calls `visualize.main()` → `figures/*.png`
- Gate failure path: `analyze_tiers.relax_and_retry()` with hard_thresh=0.2; if still fails → sys.exit(1)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data Loading | Project structure, requirements.txt, EvalPlus dataset loading, smoke test harness | 8 | 2+1+2+3 |
| A-2 | Solution Generation | HuggingFace model loading (3 models), k=5 generation loop, JSONL save/reuse logic | 14 | 3+3+4+4 |
| A-3 | EvalPlus Evaluation | check_correctness() integration, correctness labeling, coverage tracking | 12 | 3+2+4+3 |
| A-4 | Tier Analysis & Gate | pass@1 computation, tier assignment, gate evaluation, threshold relaxation, CSV output | 13 | 3+2+4+4 |
| A-5 | Visualization & Report | 4 required figures, cross-model Jaccard overlap, run_experiment.py orchestration | 10 | 2+2+3+3 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-5], Low(4-8): [A-1]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| evalplus | >=0.3.0 | Dataset loading + correctness oracle |
| transformers | >=4.35 | HuggingFace model loading/generation |
| torch | >=2.0 | GPU inference (float16) |
| numpy | >=1.24 | pass@1 computation, tier counting |
| pandas | >=2.0 | tier_statistics CSV |
| matplotlib | >=3.7 | 4 required figures |

**CUDA:** Single GPU via `CUDA_VISIBLE_DEVICES=<empty_gpu>`, float16 + device_map="auto"
**Seed:** 42 fixed for all generation

---

## Validation Checklist

- [ ] No ASCII diagrams — confirmed
- [ ] No KB search logs (only "Applied: X") — confirmed
- [ ] Module sections = interface code only — confirmed
- [ ] Epic tasks: 5 (EXISTENCE PoC range 3-5) with complexity scores — confirmed
- [ ] Codebase Analysis (Serena) section included — confirmed
- [ ] Green-field: no base hypothesis to verify — confirmed
