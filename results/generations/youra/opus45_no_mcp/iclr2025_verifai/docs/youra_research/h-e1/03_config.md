# Config: H-E1 (Existence of Orthogonal Error Classes)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT | **Gate:** Mean Jaccard < 0.3

Applied: single fixed config, no hyperparameter search (EXISTENCE hypothesis)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (Archon/Serena MCP unavailable per experiment brief)
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1..A-8: Full Pipeline Config [Complexity: 5+9+8+8+4+7+3+6, Budget: total]

**Applied**: analysis-pipeline config pattern (single dataclass, no tuning)

### Configuration (Python Dataclass)

```python
# code/config.py
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Reproducibility
    seed: int = 42

    # Dataset
    dataset_names: tuple[str, ...] = ("humaneval_plus", "mbpp_plus")  # 563 problems total

    # LLM generation
    model_name: str = "gpt-3.5-turbo"        # fallback: "codellama/CodeLlama-7b-Instruct-hf"
    temperature: float = 0.0                  # deterministic single sample
    max_tokens: int = 512
    top_p: float = 1.0
    num_samples_per_problem: int = 1

    # Static analysis
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30

    # Execution analysis (evalplus)
    exec_timeout_sec: int = 10                # per-testcase timeout

    # Gate thresholds
    jaccard_gate: float = 0.3                 # PASS if mean_jaccard < 0.3
    non_overlap_gate: float = 0.7             # secondary: PASS if non_overlapping_pct > 0.7

    # Output paths
    output_dir: str = "results/"
    figures_dir: str = "figures/"
    results_file: str = "results/results.json"


CONFIG = ExperimentConfig()
```

### Static Analysis Tool Settings

```python
# code/static_analysis.py — subprocess invocation settings (not tunable, fixed defaults)
PYLINT_CMD = ["pylint", "--output-format=json", "--disable=C,R", "-"]
# Non-standard: disable convention(C)/refactor(R) checks — keep only error/warning codes
# relevant to correctness, avoid noise from style-only findings

MYPY_CMD = ["mypy", "--no-error-summary", "--ignore-missing-imports", "-"]
```

### Subtasks [8/8 used — matches architecture Epic Tasks A-1..A-8]

| ID | Subtask | Description |
|----|---------|--------------|
| A-1 | Dataset loading | `get_human_eval_plus()` + `get_mbpp_plus()` → 563 problems |
| A-2 | Code generation | Call LLM per problem with `CONFIG` generation params, seeded |
| A-3 | Static analysis pipeline | Run `PYLINT_CMD`/`MYPY_CMD`, extract `{tool}:{code}` error sets |
| A-4 | Execution analysis pipeline | Run evalplus tests, extract failure-type set (`exec:wrong_answer` etc.) |
| A-5 | Jaccard + categorization | `compute_jaccard`, `categorize` per problem |
| A-6 | Pipeline orchestration | Wire all steps over 563 problems, write `results_file` |
| A-7 | Gate evaluation | Compare `mean_jaccard` vs `jaccard_gate`, `non_overlapping_pct` vs `non_overlap_gate` |
| A-8 | Visualization suite | 4 figures + gate bar chart to `figures_dir` |

---

## Evaluation Thresholds

| Metric | Threshold | Role |
|--------|-----------|------|
| Mean Jaccard similarity | < 0.3 | GATE (MUST_WORK) |
| Non-overlapping % | > 0.7 | Secondary (report only) |

No training hyperparameters — analysis-only experiment (no train/val loop, no optimizer/LR).
