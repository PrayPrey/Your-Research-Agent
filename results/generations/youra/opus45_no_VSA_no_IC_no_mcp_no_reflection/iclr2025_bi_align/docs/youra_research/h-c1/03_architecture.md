# Architecture: H-C1 (CONDITION)

**Hypothesis:** Explicit constraint training (IFEval) transfers to implicit safety constraints (TruthfulQA/BBQ), ≥2pp improvement

Applied: lm-eval-harness-standard-evaluation-pattern (unified HFLM eval across model configs)
Applied: gate-comparison-pattern (max(baselines) + threshold, reused from H-M2)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m2, VALIDATED) — checkpoints only, no code reuse
**Status:** No h-c1 code exists yet (green-field for this hypothesis's own modules). Base hypothesis h-m2 provides trained checkpoints (B1-B3, T1-T4) referenced by path only — this experiment is inference/eval only, does not import h-m2 training code.
**Analyzed Path:** `h-m2/code/` (checkpoint directory layout only)
**Findings:** `h-m2/code/train_variants.py` `run_all()` saves checkpoints to `h-m2/code/checkpoints/{variant}_*`. No reward/training modules needed here — H-C1 only loads final checkpoints via HuggingFace `from_pretrained` + `lm-evaluation-harness`. IFEval results consumed from `h-m2/code/evaluate.py` output (JSON with `strict_accuracy` per variant) for correlation analysis (FR-5).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Resource | Path | Notes |
|----------|------|-------|
| B1-B3, T1-T4 checkpoints | `../h-m2/code/checkpoints/{b1,b2,b3,t1_alpha0.2_beta0.8,...}` | Loaded via `transformers.AutoModelForCausalLM.from_pretrained` |
| IFEval per-variant results | `../h-m2/code/outputs/ifeval_results.json` (or equivalent evaluate_all output) | Contains `strict_accuracy` per variant, used for FR-5 correlation |

**Verified from**: `h-m2/03_architecture.md` File Structure section (no `code/` directory present yet to inspect directly; path convention taken from `train_variants.py`/`evaluate.py` module contracts)

---

## File Structure

```
h-c1/code/
├── config.py            # MODELS registry (7 checkpoint paths), TASKS list
├── evaluate_safety.py    # lm-eval-harness runner: TruthfulQA + BBQ per model
├── analyze_transfer.py     # Gate check + IFEval correlation (scipy.pearsonr)
└── report.py                # Renders 04_validation.md from results JSON
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
MODELS: dict[str, str] = {
    "B1": "meta-llama/Meta-Llama-3-8B-Instruct",
    "B2": "../h-m2/code/checkpoints/b2_helpfulness_only",
    "B3": "../h-m2/code/checkpoints/b3_quality_only",
    "T1": "../h-m2/code/checkpoints/t1_alpha0.2_beta0.8",
    "T2": "../h-m2/code/checkpoints/t2_alpha0.4_beta0.6",
    "T3": "../h-m2/code/checkpoints/t3_alpha0.6_beta0.4",
    "T4": "../h-m2/code/checkpoints/t4_alpha0.8_beta0.2",
}
TASKS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
IFEVAL_RESULTS_PATH = "../h-m2/code/outputs/ifeval_results.json"
```

### Evaluate Safety (`evaluate_safety.py`)

**Dependencies**: config, lm_eval (HFLM, evaluator)

```python
def evaluate_model(model_name: str, checkpoint: str) -> dict:
    """HFLM(pretrained=checkpoint) -> evaluator.simple_evaluate(tasks=TASKS,
    batch_size='auto:4'). Returns {'model', 'truthfulqa_mc1', 'truthfulqa_mc2', 'bbq'}."""
    ...

def evaluate_all(models: dict[str, str]) -> dict[str, dict]:
    """Sequential eval over 7 models (memory-safe), writes results/safety_results.json."""
    ...
```

### Analyze Transfer (`analyze_transfer.py`)

**Dependencies**: config.IFEVAL_RESULTS_PATH, scipy.stats.pearsonr

```python
def compute_gate(safety_results: dict[str, dict]) -> dict:
    """max(B1,B2,B3) per metric; for each Ti check delta >= 0.02 on truthfulqa_mc1
    OR bbq. Returns {'max_truthful': float, 'max_bbq': float, 'deltas': dict,
    'gate_passed': bool, 'best_ti': str | None}."""
    ...

def analyze_transfer(safety_results: dict, ifeval_results: dict) -> dict:
    """Pearson r/p between IFEval delta and TruthfulQA/BBQ delta across T1-T4.
    Returns {'correlation_truthfulqa': {'r','p'}, 'correlation_bbq': {'r','p'}}."""
    ...
```

### Report (`report.py`)

**Dependencies**: analyze_transfer outputs, safety_results

```python
def render_validation_report(safety_results: dict, gate: dict, correlation: dict, out_path: str) -> None:
    """Writes 04_validation.md: per-model metrics table, gate PASS/FAIL, correlation
    section, per-category breakdown if gate failed."""
    ...

def per_category_breakdown(safety_results: dict) -> "pandas.DataFrame":
    """Only invoked on gate failure per Failure Analysis Protocol (FR-6)."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Config registry | `config.py`: MODELS dict (7 checkpoint paths), TASKS, IFEval results path | 3 | 1+1+1+0 |
| E-2 | Checkpoint validation | Verify all 7 checkpoints load via `from_pretrained` before eval loop (fail-fast) | 5 | 1+2+1+1 |
| E-3 | TruthfulQA eval | `evaluate_model` wired to `truthfulqa_mc1`/`truthfulqa_mc2` via lm-eval-harness HFLM | 8 | 2+3+2+1 |
| E-4 | BBQ eval | Extend `evaluate_model` for `bbq` task (58k examples, longer runtime, batch tuning) | 9 | 2+3+2+2 |
| E-5 | Sequential eval orchestration | `evaluate_all`: loop 7 models, memory cleanup between loads, JSON persistence | 7 | 2+2+1+2 |
| E-6 | Gate computation | `compute_gate`: max(baselines), ≥2pp delta check on TruthfulQA OR BBQ | 5 | 1+2+1+1 |
| E-7 | Transfer correlation | `analyze_transfer`: load H-M2 IFEval results, Pearson r/p vs TruthfulQA/BBQ deltas | 7 | 2+2+2+1 |
| E-8 | Validation report | `render_validation_report`: 04_validation.md generation with tables + gate + correlation | 6 | 2+1+1+2 |
| E-9 | Failure-path breakdown | `per_category_breakdown`: conditional per-category analysis if gate fails | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E-4], Low(4-8): [E-1, E-2, E-3, E-5, E-6, E-7, E-8, E-9]
