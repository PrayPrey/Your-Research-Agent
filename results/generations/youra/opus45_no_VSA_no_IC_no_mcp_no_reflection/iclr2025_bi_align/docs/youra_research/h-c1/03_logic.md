# Logic: H-C1 (CONDITION)

**Hypothesis:** Explicit constraint training (IFEval) transfers to implicit safety constraints (TruthfulQA/BBQ), ≥2pp improvement

Applied: lm-eval-harness-HFLM-simple_evaluate-pattern
Applied: gate-comparison-pattern (max(baselines) + threshold, reused from H-M2)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2, VALIDATED)
**Status**: API signatures verified from base code (not spec). H-M2's `03_architecture.md` guessed checkpoint path `checkpoints/{variant}_*` and results file `ifeval_results.json` — **both wrong**. Actual code (`train_variants.py`, `evaluate.py`) confirms different paths below.
**Analyzed Path**: `h-m2/code/train_variants.py`, `h-m2/code/evaluate.py`, `h-m2/code/config.py`
**Relevant Symbols**: `run_variant` (checkpoint save location), `evaluate_all`/`__main__` (results file), `VARIANTS` (variant names)

**Corrections vs. spec**:
| Item | Spec assumed | Actual (verified) |
|------|-------------|-------------------|
| B1 checkpoint | `checkpoints/b1` | `meta-llama/Meta-Llama-3-8B-Instruct` (base model id string, `run_variant` returns `cfg.model.base_model_id` when `variant.train=False`) |
| B2/B3/T1-T4 checkpoint | `checkpoints/{variant}_{desc}` | `outputs/{VARIANT_NAME}/final` (e.g. `outputs/T2/final`), from `variant_dir = output_dir / variant.name`, `ckpt_path = variant_dir / "final"` |
| IFEval results file | `outputs/ifeval_results.json` | `outputs/eval_results.json`, dict keyed by variant name (`"T1"`, `"T2"`, ...) with `strict_accuracy` / `loose_accuracy` floats |

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m2/code/train_variants.py + h-m2/code/evaluate.py (ACTUAL CODE)
# No functions are called directly — H-C1 only reads checkpoint dirs and JSON output.

# Checkpoint dir contract (HF from_pretrained compatible, saved via trainer.save_pretrained):
#   B1  -> "meta-llama/Meta-Llama-3-8B-Instruct"   (HF hub, not local)
#   B2  -> "../h-m2/code/outputs/B2/final"
#   B3  -> "../h-m2/code/outputs/B3/final"
#   T1  -> "../h-m2/code/outputs/T1/final"
#   T2  -> "../h-m2/code/outputs/T2/final"
#   T3  -> "../h-m2/code/outputs/T3/final"
#   T4  -> "../h-m2/code/outputs/T4/final"

# IFEval results JSON contract (../h-m2/code/outputs/eval_results.json):
# dict[str, dict] keyed by variant name -> {"strict_accuracy": float, "loose_accuracy": float, "total": int, "per_constraint_type": dict}
```

**Verified from**: `h-m2/code/train_variants.py` (`run_variant`), `h-m2/code/evaluate.py` (`__main__` output path), `h-m2/code/outputs/eval_results.json` (actual file content)

---

## A-1: Config + Model Loading + Sequential Eval Orchestration [Complexity: High, Budget: subtasks below]

**Applied**: HFLM simple_evaluate pattern (unified eval loop across model configs)

### API Signatures

```python
# config.py
MODELS: dict[str, str] = {
    "B1": "meta-llama/Meta-Llama-3-8B-Instruct",
    "B2": "../h-m2/code/outputs/B2/final",
    "B3": "../h-m2/code/outputs/B3/final",
    "T1": "../h-m2/code/outputs/T1/final",
    "T2": "../h-m2/code/outputs/T2/final",
    "T3": "../h-m2/code/outputs/T3/final",
    "T4": "../h-m2/code/outputs/T4/final",
}
TASKS: list[str] = ["truthfulqa_mc1", "truthfulqa_mc2", "bbq"]
IFEVAL_RESULTS_PATH = "../h-m2/code/outputs/eval_results.json"
RESULTS_DIR = "results"
SEED = 42

# evaluate_safety.py
def check_checkpoints(models: dict[str, str]) -> dict[str, bool]:
    """Fail-fast: AutoModelForCausalLM.from_pretrained(path, low_cpu_mem_usage=True) load-check per model, no forward pass."""
    ...

def evaluate_model(model_name: str, checkpoint: str, tasks: list[str] = TASKS) -> dict:
    """lm_eval.simple_evaluate(model=HFLM(pretrained=checkpoint), tasks=tasks,
    batch_size='auto:4', random_seed=SEED). Returns
    {'model': str, 'truthfulqa_mc1': float, 'truthfulqa_mc2': float, 'bbq': float, 'raw': dict}."""
    ...

def evaluate_all(models: dict[str, str] = MODELS) -> dict[str, dict]:
    """Sequential loop over 7 models; del model; torch.cuda.empty_cache() between loads.
    Writes results/safety_results.json. Returns {model_name: evaluate_model(...)}."""
    ...
```

### Pseudo-code (checkpoint validation + sequential eval — non-trivial due to fail-fast + memory reset)

```
1. for name, path in MODELS.items():
     try: AutoModelForCausalLM.from_pretrained(path, low_cpu_mem_usage=True)  # load-only, then del
     except Exception as e: raise RuntimeError(f"{name} checkpoint invalid: {e}")  # fail-fast before any eval runs
2. results = {}
3. for name, path in MODELS.items():
     hflm = HFLM(pretrained=path, batch_size="auto:4")
     out = lm_eval.simple_evaluate(model=hflm, tasks=TASKS, random_seed=SEED)
     results[name] = extract_metrics(out)  # pull acc from out['results'][task]
     del hflm; torch.cuda.empty_cache()
4. json.dump(results, "results/safety_results.json")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Config + checkpoint validation | `config.py` MODELS/TASKS registry; `check_checkpoints` fail-fast load test for all 7 paths |
| L-1-2 | evaluate_model + evaluate_all | HFLM wiring for truthfulqa_mc1/mc2/bbq; sequential loop with GPU memory cleanup; JSON persistence |

---

## A-2: Gate + Correlation + Report [Complexity: High, Budget: covered under A-1's 2-subtask allocation — implement inline, no separate subtask]

**Applied**: gate-comparison-pattern (max(baselines) + threshold, reused from H-M2 `compute_gate`)

### API Signatures

```python
# analyze_transfer.py
def compute_gate(safety_results: dict[str, dict], threshold_pp: float = 0.02) -> dict:
    """max(B1,B2,B3) per metric (truthfulqa_mc1, bbq); for each Ti in T1-T4 check
    delta >= threshold_pp on truthfulqa_mc1 OR bbq. Returns
    {'max_truthful': float, 'max_bbq': float, 'deltas': dict[str, dict], 'gate_passed': bool, 'best_ti': str|None}."""
    ...

def load_ifeval_results(path: str = IFEVAL_RESULTS_PATH) -> dict[str, float]:
    """Loads eval_results.json, returns {variant: strict_accuracy} for T1-T4."""
    ...

def analyze_transfer(safety_results: dict, ifeval_deltas: dict[str, float]) -> dict:
    """scipy.stats.pearsonr across T1-T4 pairs: (ifeval_delta_i, truthfulqa_delta_i) and
    (ifeval_delta_i, bbq_delta_i). Returns
    {'correlation_truthfulqa': {'r': float, 'p': float}, 'correlation_bbq': {'r': float, 'p': float}}."""
    ...

# report.py
def render_validation_report(safety_results: dict, gate: dict, correlation: dict, out_path: str) -> None:
    """Writes 04_validation.md: per-model metrics table, gate PASS/FAIL, correlation section,
    per-category breakdown if gate failed."""
    ...

def per_category_breakdown(safety_results: dict) -> "pandas.DataFrame":
    """Only invoked when gate['gate_passed'] is False (FR-6)."""
    ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| safety_results | `dict[str, dict]` | 7 keys (B1-B3,T1-T4) x {truthfulqa_mc1, truthfulqa_mc2, bbq} floats |
| ifeval_deltas | `dict[str, float]` | 4 keys (T1-T4), `strict_accuracy - max(B1,B2,B3 strict_accuracy)` |
| correlation | `dict` | 2 keys, each `{'r': float, 'p': float}` |

### Pseudo-code

```
1. max_truthful = max(safety_results[b]['truthfulqa_mc1'] for b in ['B1','B2','B3'])
2. max_bbq      = max(safety_results[b]['bbq'] for b in ['B1','B2','B3'])
3. for t in ['T1','T2','T3','T4']:
     deltas[t] = {'truthful': safety_results[t]['truthfulqa_mc1'] - max_truthful,
                  'bbq': safety_results[t]['bbq'] - max_bbq}
4. gate_passed = any(d['truthful'] >= 0.02 or d['bbq'] >= 0.02 for d in deltas.values())
5. ifeval = load_ifeval_results()  # {T1..T4: strict_accuracy}
   max_ifeval_baseline = max(ifeval.get(b, ifeval[min(ifeval)]) for b in ['B1','B2','B3'] if b in ifeval)
   ifeval_deltas[t] = ifeval[t] - max_ifeval_baseline
6. r_truthful, p_truthful = pearsonr([ifeval_deltas[t] for t in T1-T4], [deltas[t]['truthful'] for t in T1-T4])
7. r_bbq, p_bbq = pearsonr([ifeval_deltas[t] for t in T1-T4], [deltas[t]['bbq'] for t in T1-T4])
```

**Note**: this module has no dedicated subtask slot (budget=2, both consumed by A-1); implement as part of L-1-2 delivery or treat as immediate follow-on with same signatures — no additional subtask decomposition needed given low complexity of arithmetic/pearsonr logic.
