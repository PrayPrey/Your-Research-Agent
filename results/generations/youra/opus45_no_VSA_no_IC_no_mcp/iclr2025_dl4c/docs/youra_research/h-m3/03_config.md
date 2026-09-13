# Config: h-m3

**Hypothesis:** Targeted edits have higher probability of fixing bugs than global rewrites
**Type:** EXISTENCE (PoC) — single fixed config, no sweeps

Applied: Standard PyTorch/HF experiment-config defaults (Archon KB: no h-m3-specific pattern found; reused h-m2 dataclass config pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2)
**Status**: Config class verified from actual code (read directly; Serena MCP unavailable this run, per architecture note)
**Config Files Found**: `h-m2/code/config.py` (`ExperimentConfig` dataclass)
**Pattern Used**: dataclass (single global `CONFIG` instance)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m2/code/config.py (ACTUAL CODE, verbatim copy into h-m3/code/config.py)
@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.95
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    feedback_types: list[str] = field(default_factory=lambda: ["detailed", "binary"])
    results_path: str = "results.json"
    figures_dir: str = "../figures/"

CONFIG = ExperimentConfig()
```

**Verified from**: `h-m2/code/config.py` (actual implementation).
**h-m3 usage**: `config.py` copied unchanged into `h-m3/code/`. `feedback_types` field exists but h-m3 driver (`run_poc.py`) only uses `"detailed"` — no code change needed, just ignore `"binary"` at call site.

---

## A-3/A-4/A-5: Edit Scope Threshold (Config Addition)

**Applied**: Standard PyTorch defaults; threshold value fixed from PRD FR-5 (no tuning — EXISTENCE PoC)

No new dataclass — single constant added at call sites (`edit_scope_classify.py`, `evaluate.py`), matching architecture's "pure function" design:

```python
THRESHOLD_LINES = 5  # lines_changed <= 5 -> "targeted", else "global" (PRD FR-5 AST threshold; h-m2 code uses difflib line-diff, not tree-sitter, per architecture note)
```

## A-4: PoC Driver Scale

```python
POC_SAMPLES = 50  # per dataset (humaneval, mbpp), matches h-m2 PoC scale
FEEDBACK_TYPE = "detailed"  # single condition only, per architecture (no detailed/binary split)
```

### Subtasks

None — 0 subtask budget (minimal config, reuse h-m2).
