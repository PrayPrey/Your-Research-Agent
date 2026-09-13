# Architecture: H-E1 — Frozen-Model Variance Profiling (MBPP)

**Hypothesis:** h-e1 | **Type:** EXISTENCE (PoC) | **Date:** 2026-08-21

Applied: single-script profiling pattern (agentpatterns.ai variance-based RL sample selection)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing codebase to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. Single self-contained profiling script.

---

## Architecture Overview

H-E1 is a **single-script profiling experiment** — no training, no model modules, no abstractions. One file does everything: load data, load model, generate k=8 completions, execute, compute variance, check gate, save results, generate figures.

---

## Module Structure

### ProfileMBPP (`code/profile_mbpp.py`)

**Dependencies:** datasets, transformers, torch, numpy, matplotlib, subprocess, tqdm

```python
# --- Data ---
def load_mbpp_train() -> Dataset: ...
    # returns mbpp["train"], 374 problems

def format_mbpp_prompt(problem: dict) -> str: ...
    # returns instruction-formatted string

# --- Model ---
def load_frozen_model(model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5") \
    -> tuple[AutoModelForCausalLM, AutoTokenizer]: ...
    # bfloat16, device_map="auto", model.eval()

# --- Generation & Execution ---
def generate_one(model, tokenizer, prompt: str, seed: int) -> str: ...
    # temperature=1.0, top_p=0.95, max_new_tokens=512, torch.no_grad()

def execute_and_test(code_str: str, test_cases: list[str]) -> bool: ...
    # subprocess sandbox, timeout=10s, returns returncode == 0

# --- Core Profiling Loop ---
def profile_all_problems(
    model, tokenizer, problems: Dataset,
    k: int = 8, seed: int = 42,
    checkpoint_dir: str = "results/"
) -> dict[int, dict]: ...
    # {task_id: {p_i, variance_i, pass_count, k}}
    # saves checkpoint every 50 problems
    # tqdm progress bar

# --- Analysis ---
def compute_gate(results: dict, threshold_count: int = 50, threshold_var: float = 0.1) \
    -> tuple[bool, dict]: ...
    # returns (gate_passed, metrics)

def select_top50(results: dict) -> list[int]: ...
    # top-50 task_ids by variance_i descending

# --- Output ---
def save_results(results: dict, top50_ids: list[int], gate_result: bool,
                 metrics: dict, path: str) -> None: ...
    # JSON: {task_id: {...}, "top50_ids": [...], "gate_result": bool, "metrics": {...}}

def generate_figures(results: dict, top50_ids: list[int],
                     metrics: dict, fig_dir: str) -> None: ...
    # fig1_gate_metrics.png — bar chart vs thresholds
    # fig2_pass_rate_histogram.png — p_i distribution, shade [0.25, 0.75]
    # fig3_variance_histogram.png — variance_i distribution, vline at 0.1
    # fig4_top50_scatter.png — all 374 (x=rank, y=p_i), top-50 red

# --- Entry Point ---
def main() -> None: ...
    # orchestrates full pipeline, exits 0/1 based on gate

if __name__ == "__main__":
    main()
```

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   └── profile_mbpp.py          # entire experiment — one file
├── results/
│   ├── checkpoint_50.json       # intermediate (every 50 problems)
│   ├── checkpoint_100.json
│   └── mbpp_variance_profile.json  # final output for H-M1
└── figures/
    ├── fig1_gate_metrics.png
    ├── fig2_pass_rate_histogram.png
    ├── fig3_variance_histogram.png
    └── fig4_top50_scatter.png
```

---

## Results JSON Schema

```json
{
  "374": {"p_i": 0.625, "variance_i": 0.234, "pass_count": 5, "k": 8, "rank_by_variance": 3},
  "top50_ids": [374, 101, 22, ...],
  "gate_result": true,
  "metrics": {
    "count_nonzero_variance": 62,
    "threshold_count": 50,
    "mean_p_top50": 0.51,
    "gate_passed": true
  }
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Structure | Create dirs, verify deps (datasets, transformers, torch, tqdm, matplotlib), smoke-test CUDA | 5 | 1+1+1+2 |
| A-2 | Data Loading | `load_mbpp_train()`, `format_mbpp_prompt()`, validate 374 problems | 5 | 1+1+1+2 |
| A-3 | Model Loading | `load_frozen_model()`, bfloat16, device_map=auto, eval() | 6 | 2+1+1+2 |
| A-4 | Generation + Execution | `generate_one()` + `execute_and_test()` sandbox, seed management | 10 | 3+2+3+2 |
| A-5 | Profiling Loop + Checkpoint | `profile_all_problems()` with tqdm, checkpoint every 50, cache clear | 11 | 3+2+3+3 |
| A-6 | Gate + Output + Figures | `compute_gate()`, `select_top50()`, `save_results()`, `generate_figures()` (4 figs), `main()` | 12 | 3+2+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-6], Low(4-8): [A-1, A-2, A-3]

**Total complexity**: 49 | **Task count**: 6 (within LIGHT tier budget of 4-8)

---

## Key Constraints for Phase 4

- Single file: `code/profile_mbpp.py` — no modules, no imports from other local files
- Seed per completion: `torch.manual_seed(42 + problem_idx * 8 + completion_idx)`
- Checkpoint resume: check for existing `checkpoint_N.json` at startup, skip completed problems
- GPU cache: `torch.cuda.empty_cache()` every 50 problems
- Exit code: `sys.exit(0)` on gate pass, `sys.exit(1)` on gate fail
- All paths relative to script location or passed as CLI args
