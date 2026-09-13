# Configuration: h-c1 (CONDITION — Format × Model Scale Interaction)

**Applied**: h-e1 hardcoded-dict pattern, extended with 2×3 factorial grid + statistical settings

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, VALIDATED)
**Status**: config classes verified from base code (`docs/youra_research/h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` — single `CONFIG` dict + `OPENAI_API_KEY` env read
**Pattern Used**: hardcoded dict (kept consistent with h-e1; NOT switching to dataclass)

h-e1's `CONFIG` already defines `models`, `openai_models`, `benchmark_datasets`, `temperature=0.0`,
`max_new_tokens`, `prompt_formats`, `max_repair_attempts`, `exec_timeout_sec`, `eval_k`, `n_workers`,
`openai_max_retries/backoff`, `results_path`, `figures_dir`. h-c1 reuses these field names verbatim
and adds only what's new: full test-set sizes, `max_iterations` naming for repair budget per PRD,
and a `stats` block for the two-way ANOVA.

---

## A-1 to A-N: Shared Experiment Config (2×3 Factorial)

### Configuration (`code/config.py`)

```python
import os

CONFIG = {
    # Models (3 scales — factor: model_scale)
    "models": [
        "codellama/CodeLlama-7b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
        "gpt-4",
    ],
    "openai_models": {"gpt-4"},  # routed to OpenAI backend

    # Benchmarks — full EvalPlus test sets (PRD scope: 164 + 378, not PoC subset)
    "benchmarks": ["humaneval", "mbpp"],
    "benchmark_datasets": {
        "humaneval": "evalplus/humanevalplus",
        "mbpp": "evalplus/mbppplus",
    },

    # Format (2 levels — factor: format)
    "prompt_formats": ["structured", "raw"],

    # Inference (reproducibility — same as h-e1)
    "temperature": 0.0,
    "max_new_tokens": 1024,   # widened from h-e1's 512 for larger/harder full-set problems
    "batch_size": 1,
    "seed": 42,

    # HF model loading (7B/34B only; gpt-4 uses OpenAI API)
    "torch_dtype": "float16",
    "device_map": "auto",

    # Repair loop
    "max_iterations": 3,     # PRD-specified repair budget (vs h-e1's max_repair_attempts=5)
    "exec_timeout_sec": 3.0,
    "eval_k": [1],
    "n_workers": 4,

    # OpenAI retry + rate limiting (TR-3: API rate limiting for GPT-4)
    "openai_max_retries": 5,
    "openai_backoff_base_sec": 2.0,
    "openai_rate_limit_rps": 2.0,  # new: throttle GPT-4 calls across 542 problems x 2 formats

    # Statistical analysis (TR-2: new module, not present in h-e1)
    "stats": {
        "alpha": 0.05,
        "correction_method": "fdr_bh",   # Benjamini-Hochberg, per PRD TR-2
        "anova_ss_type": 3,              # Type III SS, handles unequal cell sizes (US-2)
        "effect_size": "eta_squared",
        "contrast_effect_size": "cohens_d",
        "ci_level": 0.95,
        "planned_contrasts": "monotonic_ordering",  # 7B > 34B > GPT-4 (Secondary Goal 1)
    },

    # Caching (Risk: API costs — cache aggressively)
    "cache_dir": "outputs/cache/",
    "cache_enabled": True,

    # Output
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}

# Environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # required for gpt-4 calls
```

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Reuse h-e1 error parser/prompts/models | No new config; import as-is |
| C-2 | Multi-model orchestration | `models` x `prompt_formats` x `benchmarks` grid, `openai_rate_limit_rps` |
| C-3 | Result caching | `cache_dir`, `cache_enabled`, keyed by (model, format, problem_id) |
| C-4 | Two-way ANOVA module | `stats.alpha`, `stats.anova_ss_type`, `stats.effect_size` |
| C-5 | Planned contrasts / effect sizes | `stats.contrast_effect_size`, `stats.ci_level`, `stats.planned_contrasts` |
| C-6 | Multiple comparison correction | `stats.correction_method` (BH-FDR) |
| C-7 | Interaction visualization | `figures_dir` (reuses h-e1 visualize.py conventions, no new tunables) |

---

## Inherited Configuration (Base Hypothesis: h-e1)

Reused verbatim from `h-e1/code/config.py` (verified from actual code, not spec):
`models`, `openai_models`, `benchmarks`, `benchmark_datasets`, `temperature`, `batch_size`, `seed`,
`torch_dtype`, `device_map`, `prompt_formats`, `exec_timeout_sec`, `eval_k`, `n_workers`,
`openai_max_retries`, `openai_backoff_base_sec`, `OPENAI_API_KEY` env pattern.

Renamed/changed for h-c1 per PRD: `max_repair_attempts` (5) → `max_iterations` (3);
`max_new_tokens` 512 → 1024. `results_path`/`figures_dir` moved under `outputs/` to avoid
collision with h-e1's run artifacts.

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes (for gpt-4) | OpenAI client auth, same as h-e1 |

No new env vars or `.env` layer — single `os.environ.get` read, consistent with h-e1.
