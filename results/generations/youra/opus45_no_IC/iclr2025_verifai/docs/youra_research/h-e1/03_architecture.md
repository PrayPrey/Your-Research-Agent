# Architecture: H-E1 (Error Class Independence Verification)

**Type:** EXISTENCE (PoC) | **Gate:** MUST_WORK (Jaccard < 0.30)

Applied: standard-script-per-strategy pattern (no close KB match found; used generic DL eval pipeline conventions)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## File Structure

```
h-e1/code/
  config.py          # fixed experiment config
  data.py             # HumanEval + HumanEval-Verus loading, sample generation
  strategies.py       # grammar / static / SMT strategy implementations
  overlap.py          # Jaccard computation + gate check
  visualize.py         # 3 required figures
  run_experiment.py    # main orchestration script
```

---

## Modules

### config.py

**Dependencies**: none

```python
SEED: int = 42
TEMPERATURE: float = 0.2
N_SAMPLES: int = 10
MODELS: list[str] = ["codellama/CodeLlama-7b-hf", "gpt-4"]
JACCARD_THRESHOLD: float = 0.30
FIGURES_DIR: str = "{hypothesis_folder}/figures/"
RESULTS_DIR: str = "{hypothesis_folder}/results/"
```

### data.py (`code/data.py`)

**Dependencies**: config.py

```python
def load_humaneval_problems() -> dict[str, dict]: ...
def load_verus_task_ids() -> set[str]: ...
def generate_samples(model_name: str, problems: dict, n: int, temperature: float) -> list[dict]: ...
    # returns list of {"task_id": str, "completion": str, "model": str}
```

### strategies.py (`code/strategies.py`)

**Dependencies**: data.py, ast (stdlib), bandit, pylint, z3

```python
def check_syntax(code: str) -> bool: ...
def apply_grammar_constraints(code: str) -> str: ...
def run_static_analysis(code: str) -> list[dict]: ...
def apply_static_feedback(code: str, issues: list[dict]) -> str: ...
def has_formal_spec(task_id: str, verus_ids: set[str]) -> bool: ...
def verify_spec(code: str, task_id: str) -> bool: ...
def smt_guided_repair(code: str, task_id: str) -> str: ...

def run_verification_strategies(samples: list[dict], verus_ids: set[str]) -> dict[str, set[str]]: ...
    # returns {"grammar": set, "static": set, "smt": set}
```

### overlap.py (`code/overlap.py`)

**Dependencies**: strategies.py

```python
def jaccard_index(set_a: set, set_b: set) -> float: ...
def compute_jaccard_overlap(sets: dict[str, set]) -> dict[str, float]: ...
def gate_check(overlaps: dict[str, float], threshold: float) -> bool: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: overlap.py, matplotlib, matplotlib_venn

```python
def plot_jaccard_bar(overlaps: dict[str, float], threshold: float, out_path: str) -> None: ...
def plot_venn(sets: dict[str, set], out_path: str) -> None: ...
def plot_per_model_comparison(overlaps_by_model: dict[str, dict], out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. load data, 2. generate samples per model, 3. run strategies per model,
    # 4. compute overlaps (pooled + per-model), 5. gate check, 6. save results/figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | HumanEval + Verus loading, sample generation for both models | 10 | 3+2+3+2 |
| A-2 | Grammar strategy | Syntax check + grammar-constrained decoding (syncode) | 8 | 2+2+3+1 |
| A-3 | Static analysis strategy | Bandit + Pylint run + feedback regeneration | 8 | 2+2+3+1 |
| A-4 | SMT repair strategy | Z3 spec verification + repair on Verus subset | 9 | 2+3+3+1 |
| A-5 | Overlap analysis | Jaccard computation across 3 pairs + gate check | 5 | 1+2+1+1 |
| A-6 | Visualization | Bar chart, Venn diagram, per-model comparison | 6 | 2+1+1+2 |
| A-7 | Orchestration + run | Wire pipeline end-to-end, save results/figures | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-4], Low(4-8): [A-2, A-3, A-5, A-6, A-7]

---

## Notes

- No base hypothesis / existing codebase — External Dependencies section omitted.
- SMT strategy (A-4) limited to HumanEval-Verus subset (23/164 problems); other strategies run on full 164.
- Samples generated once per model (n=10, temp=0.2, seed=42), reused across all 3 strategies to avoid redundant inference.
