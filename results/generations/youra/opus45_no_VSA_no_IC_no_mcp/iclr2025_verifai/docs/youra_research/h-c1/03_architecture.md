# Architecture: h-c1 Format × Model Scale Interaction

Applied: DL module pattern (parser -> formatter -> repair-loop -> evaluate, reused across factorial cells)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-e1 implementation, not specs)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: `errors.py`, `models.py`, `prompts.py`, `repair_loop.py` are already generic over model and format (no h-e1-specific hardcoding) — reusable unmodified. `evaluate.py::run_benchmark` loops single model/format; h-c1 needs a thin orchestration wrapper around it for the 2x3 grid, not a rewrite.

---

## System Components

- `config.py` (h-c1) — factorial grid config, imports h-e1 `CONFIG` for shared constants
- `orchestrate.py` (NEW) — runs `run_benchmark` (h-e1) across 6 cells (2 formats x 3 models x 2 benchmarks), caches to disk
- `errors.py`, `models.py`, `prompts.py`, `repair_loop.py`, `evaluate.py` (REUSED from h-e1, unmodified, imported via path)
- `stats.py` (NEW) — two-way ANOVA, effect sizes, planned contrasts, BH-FDR
- `visualize_interaction.py` (NEW) — interaction plot with 95% CI error bars
- `run_h_c1.py` (NEW) — entrypoint: orchestrate -> stats -> visualize -> validation report

## Data Flow (Multi-Model Runs)

1. `run_h_c1.py` loads `config.py` grid: `{format: [raw, structured]} x {model: [7b,34b,gpt4]} x {benchmark: [humaneval,mbpp]}`
2. For each of 6 (format, model) cells: `orchestrate.run_cell()` calls h-e1's `run_benchmark(model_name, benchmark, use_structured)` for both benchmarks, pools HumanEval+/MBPP+ results per cell
3. Each cell result (list of per-problem `{passed, attempts_used, error_types_seen}`) cached to `outputs/cache/{model}_{format}.json` (skip if exists — resume support)
4. `orchestrate.py` flattens all cells into long-format DataFrame: columns `[problem_id, model, format, passed]`
5. `stats.py` consumes DataFrame -> ANOVA table + simple effects + contrasts -> `outputs/anova_summary.json`
6. `visualize_interaction.py` consumes same DataFrame -> `outputs/figures/h-c1_interaction_plot.png`

## Module Interfaces

### `config.py` (`docs/youra_research/h-c1/code/config.py`)

**Dependencies**: h-e1 `config.CONFIG`

```python
from h_e1.config import CONFIG as BASE_CONFIG  # path-adjusted import, see External Dependencies

CONFIG = {
    **BASE_CONFIG,
    "models": ["codellama/CodeLlama-7b-Instruct-hf",
               "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"],
    "formats": ["raw", "structured"],
    "benchmarks": ["humaneval", "mbpp"],
    "cache_dir": "outputs/cache/",
    "alpha": 0.05,
}
```

### `orchestrate.py` (`docs/youra_research/h-c1/code/orchestrate.py`)

**Dependencies**: h-e1 `evaluate.run_benchmark`, `config.CONFIG`

```python
def run_cell(model: str, use_structured: bool) -> list[dict]: ...
    # calls h-e1 run_benchmark() per benchmark, pools problem-level results
    # returns [{"problem_id": str, "passed": bool}, ...]

def run_all_cells(force: bool = False) -> "pandas.DataFrame": ...
    # iterates 6 cells, uses cache, returns long-format df
    # columns: problem_id, model, format, passed
```

### `stats.py` (`docs/youra_research/h-c1/code/stats.py`)

**Dependencies**: `statsmodels.formula.api`, `scipy.stats`, `orchestrate` output DataFrame

```python
def two_way_anova(df: "pandas.DataFrame") -> "pandas.DataFrame": ...
    # statsmodels OLS: passed ~ C(format)*C(model), Type III SS via anova_lm(typ=3)
    # returns table with F, p, partial eta^2 for format, model, format:model

def simple_effects(df: "pandas.DataFrame") -> dict: ...
    # per model: (structured_rate - raw_rate), Cohen's d, 95% CI via bootstrap or normal approx

def planned_contrasts(df: "pandas.DataFrame") -> dict: ...
    # linear trend contrast on model [-1,0,1] x format [-0.5,0.5]
    # returns {"contrast_estimate": float, "t": float, "p": float}

def bh_fdr(pvals: list[float]) -> list[float]: ...
    # scipy.stats.false_discovery_control or manual BH correction
```

### `visualize_interaction.py` (`docs/youra_research/h-c1/code/visualize_interaction.py`)

**Dependencies**: `matplotlib`, `orchestrate`/`stats` output

```python
def plot_interaction(df: "pandas.DataFrame", simple_effects: dict, out_path: str) -> None: ...
    # x=model (ordered 7B,34B,GPT-4), y=repair_rate, 2 lines (raw/structured), CI error bars
```

### `run_h_c1.py` (`docs/youra_research/h-c1/code/run_h_c1.py`)

```python
def main() -> None: ...
    # df = orchestrate.run_all_cells()
    # anova = stats.two_way_anova(df); effects = stats.simple_effects(df)
    # contrasts = stats.planned_contrasts(df)
    # visualize_interaction.plot_interaction(df, effects, ...)
    # writes outputs/h-c1_anova_summary.json, outputs/h-c1_interaction_analysis.json
```

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| StructuredError / parse_compiler_output | `from errors import StructuredError, parse_compiler_output` | `docs/youra_research/h-e1/code/errors.py` |
| format_structured_prompt / format_raw_prompt | `from prompts import format_structured_prompt, format_raw_prompt` | `docs/youra_research/h-e1/code/prompts.py` |
| load_hf_model / generate_code | `from models import load_hf_model, generate_code` | `docs/youra_research/h-e1/code/models.py` |
| repair_problem | `from repair_loop import repair_problem` | `docs/youra_research/h-e1/code/repair_loop.py` |
| run_benchmark / load_benchmark_problems | `from evaluate import run_benchmark, load_benchmark_problems` | `docs/youra_research/h-e1/code/evaluate.py` |
| BASE CONFIG | `from config import CONFIG as BASE_CONFIG` | `docs/youra_research/h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, all modules confirmed generic — no h-e1-specific coupling to remove)

**Reuse approach**: symlink or add h-e1/code to `sys.path` in h-c1/code (no copy/fork) — ponytail: avoids duplicating 6 files; if h-e1 code later diverges, pin via git submodule or copy at that point.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Path wiring | sys.path setup to import h-e1 code modules from h-c1 | 3 | 1+1+1+0 |
| C-2 | config.py | Build factorial grid config extending h-e1 CONFIG | 3 | 1+1+1+0 |
| C-3 | orchestrate.py | run_cell + run_all_cells with disk caching/resume | 8 | 2+3+2+1 |
| C-4 | Data collection run | Execute all 6 cells (7B/34B/GPT-4 x raw/structured) on full EvalPlus | 10 | 2+3+3+2 |
| C-5 | stats.py: ANOVA | Two-way ANOVA Type III SS via statsmodels | 9 | 2+2+4+1 |
| C-6 | stats.py: effects | Simple effects, Cohen's d, 95% CI, BH-FDR correction | 8 | 2+2+3+1 |
| C-7 | stats.py: contrasts | Planned linear-trend contrast for monotonic ordering test | 7 | 2+2+2+1 |
| C-8 | visualize_interaction.py | Interaction plot with CI error bars | 5 | 1+1+2+1 |
| C-9 | run_h_c1.py + validation | Wire pipeline, write summary JSON, produce 04_validation.md inputs | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-3, C-4, C-5], Low(4-8): [C-1, C-2, C-6, C-7, C-8, C-9]
