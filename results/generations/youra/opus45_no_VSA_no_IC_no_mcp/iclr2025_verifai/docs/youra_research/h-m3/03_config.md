# Configuration: H-M3 (Fix Specificity Inverted-U)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from base code (Serena MCP unavailable — direct file read of `h-e1/code/config.py` used per CRITICAL RULE)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (dict-based `CONFIG` + `OPENAI_API_KEY`)
**Pattern Used**: Hardcoded dict (matches H-E1 base — kept consistent, no dataclass introduced)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE, unchanged)
CONFIG = {
    "models": [
        "codellama/CodeLlama-7b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
        "gpt-4",
    ],
    "openai_models": {"gpt-4"},
    "benchmarks": ["humaneval", "mbpp"],
    "benchmark_datasets": {
        "humaneval": "evalplus/humanevalplus",
        "mbpp": "evalplus/mbppplus",
    },
    "temperature": 0.0,
    "max_new_tokens": 512,
    "batch_size": 1,
    "seed": 42,
    "torch_dtype": "float16",
    "device_map": "auto",
    "max_repair_attempts": 5,
    "prompt_formats": ["structured", "raw"],
    "exec_timeout_sec": 3.0,
    "eval_k": [1],
    "n_workers": 4,
    "openai_max_retries": 5,
    "openai_backoff_base_sec": 2.0,
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
```

**Verified from**: `h-e1/code/config.py` (field names confirmed, no drift vs. spec)

---

## A-8: Config & Integration [Complexity: 7, Budget: 7]

**Applied**: Dict-extension pattern (CONFIG.update) — consistent with H-E1 dict-only config

### Configuration (Hardcoded Dict Extension)

```python
# h-m3/code/config.py
from config_base import CONFIG, OPENAI_API_KEY  # or copy h-e1 CONFIG dict verbatim, then .update()

CONFIG.update({
    # FR-1: Fix specificity levels
    "fix_levels": [0, 1, 2, 3],

    # FR-6: Within-subject repeated measures
    "n_repetitions": 3,
    "level_order_seed": 42,          # Non-standard: separate seed for per-error level-order randomization (independent of model seed=42)

    # FR-4/Data Spec: error instance collection target
    "target_error_instances": 500,
    "repairable_error_types": ["syntax", "type", "runtime", "semantic"],

    # FR-2: repair loop override (H-E1 default max_repair_attempts=5 -> PRD caps at 3 for H-M3)
    "max_repair_attempts_leveled": 3,  # Non-standard: PRD FR-2 specifies max 3 iterations (differs from inherited max_repair_attempts=5)

    # FR-5: statistical model spec (used by analysis.py, not passed to mixedlm directly)
    "quadratic_formula": "success ~ level + I(level**2)",
    "quad_pval_threshold": 0.05,

    # Output paths
    "results_path": "outputs/h-m3_results.json",
    "figures_dir": "outputs/h-m3_figures/",
    "raw_instances_path": "outputs/error_instances.json",

    # Logging
    "log_level": "INFO",
    "log_path": "outputs/h-m3_run.log",
})
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Extend CONFIG dict | Add fix_levels, n_repetitions, level_order_seed, target_error_instances keys |
| C-8-2 | Wire run_poc.py main() | Orchestrate collect_error_instances -> run_level_sweep -> build_results_dataframe -> fit_quadratic_contrast -> check_gate_criteria -> plot_* |
| C-8-3 | Results serialization | Save results.json with per-level/per-model/per-error records + fit_result + gate outcome |
| C-8-4 | Logging setup | Configure log_path/log_level, one line per stage (collection, sweep, analysis, plotting) |

---

## Model-Specific Notes (3 Models)

All 3 models reuse inherited `CONFIG["models"]` list and `CONFIG["openai_models"]` set unchanged from H-E1 — no new per-model config needed:
- `codellama/CodeLlama-7b-Instruct-hf` — HF, `torch_dtype=float16`, `device_map=auto`
- `codellama/CodeLlama-34b-Instruct-hf` — HF, same dtype/device_map (requires A100 40GB per NFR-3)
- `gpt-4` (proxy for gpt-4-turbo per PRD FR-3) — OpenAI API, uses `openai_max_retries`/`openai_backoff_base_sec`

**Non-standard**: PRD FR-3 names `GPT-4-turbo` but inherited `CONFIG["models"]` uses `"gpt-4"` string — keep as-is (matches base H-E1 openai_models set) unless Phase 4 confirms a `gpt-4-turbo` API model string is required; if so, single-line change: `"models": [..., "gpt-4-turbo"]`.

---

## Self-Validation

- [x] ONE format only (hardcoded dict, matches H-E1)
- [x] No ASCII diagrams
- [x] "Applied: X" line included
- [x] Rationale only for non-standard values (level_order_seed, max_repair_attempts_leveled, gpt-4 naming)
- [x] Subtasks within budget (4/4 for A-8)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included with verified base fields
