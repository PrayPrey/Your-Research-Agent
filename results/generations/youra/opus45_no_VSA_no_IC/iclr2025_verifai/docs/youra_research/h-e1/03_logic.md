# Logic: H-E1 (Static Analysis Tool Coverage Validation)

**Type**: EXISTENCE (PoC) | **Budget**: 2 subtasks (A-7, A-2 only)

Applied: subprocess.run(timeout=) + try/except (KB low-relevance; stdlib standard practice)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Dataset Loading [Complexity: 9, Budget: 2 subtasks]

**Applied**: HuggingFace `datasets.load_dataset` standard loader pattern

### API Signatures

```python
from dataclasses import dataclass

@dataclass
class Sample:
    task_id: str
    source: str  # "humaneval" | "mbpp"
    code: str    # canonical solution, standalone .py source

def load_humaneval() -> list[Sample]:
    """Load 164 samples from openai/human-eval via datasets."""
    ...

def load_mbpp() -> list[Sample]:
    """Load 500 samples (task_ids 11-510) from mbpp HF test split."""
    ...

def validate_syntax(sample: Sample) -> bool:
    """ast.parse(sample.code); True if no SyntaxError."""
    ...

def load_all_samples() -> list[Sample]:
    """Combine humaneval+mbpp, filter invalid syntax, assert len==664."""
    ...
```

### Pseudo-code

```
load_humaneval:
  ds = datasets.load_dataset("openai_humaneval")["test"]
  for row in ds: yield Sample(row["task_id"], "humaneval", row["prompt"] + row["canonical_solution"])

load_mbpp:
  ds = datasets.load_dataset("mbpp")["test"]  # task_ids 11-510
  for row in ds: yield Sample(str(row["task_id"]), "mbpp", row["code"])

load_all_samples:
  samples = load_humaneval() + load_mbpp()
  valid = [s for s in samples if validate_syntax(s)]
  assert len(valid) == 664, f"expected 664, got {len(valid)}"
  return valid
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | HF dataset loaders | `load_humaneval`, `load_mbpp` — fetch + map rows to `Sample` |
| L-A2-2 | Combine + validate | `load_all_samples` — merge, `ast.parse` filter, assert count==664 |

---

## A-7: Run Loop & Aggregation [Complexity: 10, Budget: 2 subtasks]

**Applied**: tempfile.NamedTemporaryFile for isolated per-sample files; dict aggregation

### API Signatures

```python
from pathlib import Path

def write_temp_file(sample: Sample) -> str:
    """Write sample.code to UTF-8 temp .py file. Returns file path (str)."""
    ...

def process_sample(sample: Sample) -> dict:
    """Run pylint/mypy/radon on sample. Returns per-sample record dict."""
    # returns: {"task_id": str, "source": str,
    #           "pylint": ToolResult, "mypy": ToolResult, "radon": ToolResult}
    ...

def aggregate(records: list[dict]) -> dict:
    """Compute per-tool valid rates + overall pass. Returns summary dict."""
    # returns: {"pylint_rate": float, "mypy_rate": float, "radon_rate": float,
    #           "min_valid_rate": float, "pass": bool, "n": int}
    ...

def main() -> None:
    """Load samples, process all, aggregate, write 3 result JSON files."""
    ...
```

### Tensor/Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| records | list[dict], len=664 | one dict per sample |
| ToolResult | {success: bool, metric: float\|int\|None, error: str\|None} | from sa_tools.py |

### Pseudo-code

```
process_sample(sample):
  path = write_temp_file(sample)
  try:
    return {
      "task_id": sample.task_id, "source": sample.source,
      "pylint": run_sa_tool("pylint", path, config.TIMEOUT_SEC),
      "mypy":   run_sa_tool("mypy", path, config.TIMEOUT_SEC),
      "radon":  run_sa_tool("radon", path, config.TIMEOUT_SEC),
    }
  finally:
    os.remove(path)

aggregate(records):
  n = len(records)
  rates = {}
  for tool in ["pylint", "mypy", "radon"]:
    rates[tool] = sum(r[tool].success for r in records) / n
  min_rate = min(rates.values())
  return {**{f"{t}_rate": r for t, r in rates.items()},
          "min_valid_rate": min_rate, "pass": min_rate >= 0.95, "n": n}

main():
  samples = load_all_samples()                      # 664
  records = [process_sample(s) for s in samples]
  summary = aggregate(records)
  failures = [r for r in records if not all(r[t].success for t in ["pylint","mypy","radon"])]
  write_json("results/h_e1_coverage.json", records)
  write_json("results/h_e1_summary.json", summary)
  write_json("results/h_e1_failures.json", failures)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A7-1 | Per-sample processing | `write_temp_file`, `process_sample` — temp file + 3 tool dispatch |
| L-A7-2 | Aggregate + main | `aggregate`, `main` — valid rates, pass check, 3 JSON outputs |

---

## Non-Allocated Tasks (Reference Only — Signatures from Architecture)

A-1, A-3, A-4, A-5, A-6, A-8 are low-complexity (≤7); signatures already fully specified in `03_architecture.md` module interfaces (config.py, dataset.py `validate_syntax`, sa_tools.py `run_pylint`/`run_mypy`/`run_radon`/`run_sa_tool`). No additional logic design required within this budget.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] Applied line present per task
- [x] Docstrings ≤ 2 lines
- [x] Tensor/data shapes in comments/table
- [x] Pseudo-code only for non-trivial algorithms (aggregation, main loop)
- [x] Subtasks: 2/2 for A-2, 2/2 for A-7 (budget respected)
- [x] Codebase Analysis (Serena) section included
- [x] Length < 600 lines
