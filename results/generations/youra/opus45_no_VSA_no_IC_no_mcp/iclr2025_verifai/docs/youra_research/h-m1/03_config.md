# Config: H-M1 (MECHANISM — PoC)

**Applied**: LLM-as-judge evaluation config pattern (single fixed config, no grid/tuning)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable this session; verified H-E1 `config.py` directly via file read.
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (dict `CONFIG` + `OPENAI_API_KEY`)
**Pattern Used**: Hardcoded dict (matches H-E1 style; no dataclasses in base code)

---

## Inherited Configuration (Base Hypothesis)

H-M1 does not subclass H-E1's `CONFIG` (different domain: judge extraction, not code repair). Only `OPENAI_API_KEY` loading pattern and dict style are reused.

```python
# From: h-e1/code/config.py (ACTUAL CODE, verified)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # reused verbatim
```

`errors.py` (StructuredError, parse_compiler_output) is copied into `h-m1/code/` per architecture — no config fields needed from it.

---

## M-1: Config Module [Complexity: 5, Budget: 0 subtasks]

**Applied**: Hardcoded dict, PoC minimal (single config, no variations, 1 seed implicit via judge determinism)

### Configuration (Hardcoded dict)

```python
# h-m1/code/config.py
import os

CONFIG = {
    "judge_model": "gpt-4",          # or "claude-3-sonnet-20240229"
    "judge_provider": "openai",      # "openai" | "anthropic"
    "temperature": 0.0,              # determinism (NFR-1)
    "max_tokens": 500,
    "fields": ["error_type", "line_number", "message", "context"],
    "min_samples": 500,              # FR-1
    "accuracy_threshold": 0.95,      # gate: mean field accuracy
    "pass_rate_threshold": 0.90,     # gate: sample pass rate
    "max_retries": 5,
    "backoff_base_sec": 2.0,
    "error_pairs_path": "data/error_pairs.json",
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
```

No subtasks — task budget is 0; config.py is a direct copy of the architecture-specified dict.
