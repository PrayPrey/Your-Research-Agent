# Logic: H-M3 Adaptive PBT Contribution Experiment

Applied: Standard Python / scipy / icontract-hypothesis patterns (Archon KB had no domain match)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3 extends H-M1)
**Status**: API signatures verified from actual H-M1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/statistical_analysis.py`
**Relevant Symbols**:
- `bootstrap_ci(values: list, n_bootstrap: int = 10_000, seed: int = 42) -> tuple`
- `wilcoxon_holm(per_task_gaps: list) -> tuple` — returns `(stat, p_raw, p_corrected)`
- `load_contracteval(jsonl_path: Optional[str] = None) -> dict`
- `load_h1_corpus(h1_samples_dir: Optional[str] = None) -> dict`
- `verify_task_overlap(ce_ids: set, ep_ids: set, threshold: float = 0.90) -> tuple`
- `_save(fig, path: str) -> None`

---

## External Dependencies API

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-m1/code/statistical_analysis.py (ACTUAL CODE)
def bootstrap_ci(values: list, n_bootstrap: int = 10_000, seed: int = 42) -> tuple:
    """95% bootstrap CI on mean. Returns (ci_lower, ci_upper)."""

def wilcoxon_holm(per_task_gaps: list) -> tuple:
    """Wilcoxon signed-rank + Holm. Returns (stat, p_raw, p_corrected).
    Uses alternative="greater" internally. Accepts list of gap floats."""

# From: docs/youra_research/h-m1/code/data_loader.py (ACTUAL CODE)
def load_contracteval(jsonl_path: Optional[str] = None) -> dict:
    """Returns {task_id: task_dict}."""

def load_h1_corpus(h1_samples_dir: Optional[str] = None) -> dict:
    """Returns {model: {task_id: [code_str, ...]}}."""

def verify_task_overlap(ce_ids: set, ep_ids: set, threshold: float = 0.90) -> tuple:
    """Returns (matched_ids, unmatched_ids). Raises if overlap < threshold."""

# From: docs/youra_research/h-m1/code/visualization.py (ACTUAL CODE)
def _save(fig, path: str) -> None:
    """Saves fig to path, creating parent dirs."""
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, not spec)

---

## A-3: Experiment B Runner — Single Triple [Complexity: 15, Budget: 4 subtasks]

### API Signatures

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TripleResult:
    task_id: str
    model: str
    program_idx: int
    adaptive_failure_rate: float  # n_failures / n_valid; 0.0 if n_valid == 0
    n_valid: int                  # examples not rejected by @require filter
    n_failures: int               # @ensure violations detected
    filter_rate: float            # 1.0 - (n_valid / budget)
    error: Optional[str]          # None on success; exception class name on error

def run_triple(
    llm_code: str,
    contracteval_task: dict,
    task_id: str,
    model: str,
    program_idx: int,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
) -> TripleResult: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Contract decorator wrapping | Exec `llm_code`; attach `@require`/`@ensure` from `contracteval_task` |
| L-3-2 | icontract_hypothesis integration | Calling convention, error handling, violation counting |
| L-3-3 | SIGALRM timeout guard | Exact implementation, non-POSIX fallback |
| L-3-4 | TripleResult construction + error state | Dataclass population including all error paths |

---

### L-3-1: Contract Decorator Wrapping

```python
import inspect, icontract

def _arg_sig(fn: callable) -> str:
    """Comma-joined arg names for lambda construction."""
    return ", ".join(inspect.signature(fn).parameters)

def _wrap_with_contracts(llm_code: str, contracteval_task: dict) -> callable:
    """Exec llm_code; attach @require/@ensure from task dict. Returns wrapped fn."""
    entry_point = contracteval_task["entry_point"]
    ns: dict = {}
    exec(llm_code, ns)
    fn = ns[entry_point]

    for pre_str in contracteval_task.get("requires", []):
        condition = eval(f"lambda {_arg_sig(fn)}: {pre_str}", ns)
        fn = icontract.require(condition)(fn)

    for post_str in contracteval_task.get("ensures", []):
        condition = eval(f"lambda result, {_arg_sig(fn)}: {post_str}", ns)
        fn = icontract.ensure(condition)(fn)

    return fn
```

**Pseudo-code**:
```
1. exec(llm_code) into fresh namespace ns
2. fn = ns[entry_point]
3. for pre_str in task["requires"]:  fn = icontract.require(eval_lambda)(fn)
4. for post_str in task["ensures"]:  fn = icontract.ensure(eval_lambda)(fn)
5. return fn
```

---

### L-3-2: icontract_hypothesis Integration

```python
from icontract_hypothesis import test_with_inferred_strategy, StrategyInferenceError
from hypothesis import given, settings, HealthCheck
import icontract

def _run_pbt(wrapped_fn: callable, budget: int, seed: int) -> tuple[int, int]:
    """Run icontract_hypothesis. Returns (n_valid, n_failures).
    ponytail: counter via closure; n_valid approximated as budget - filtered count.
    """
    counter = {"valid": 0, "failures": 0}
    original_fn = wrapped_fn

    def counting_wrapper(*args, **kwargs):
        counter["valid"] += 1
        try:
            return original_fn(*args, **kwargs)
        except icontract.ViolationError:
            counter["failures"] += 1
            raise

    counting_wrapper.__name__ = original_fn.__name__
    import functools
    functools.update_wrapper(counting_wrapper, original_fn)

    try:
        test_with_inferred_strategy(
            counting_wrapper,
            settings=settings(
                max_examples=budget,
                seed=seed,
                deadline=None,
                suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
            ),
        )
    except icontract.ViolationError:
        pass  # expected; already counted

    return counter["valid"], counter["failures"]
```

**Error handling**:

| Exception | Action |
|-----------|--------|
| `icontract.ViolationError` | count as failure, continue |
| `icontract_hypothesis.StrategyInferenceError` | propagate to `run_triple`; sets `error="StrategyInferenceError"` |
| `TimeoutError` (SIGALRM) | propagate to `run_triple`; sets `error="TimeoutError"` |
| Any other `Exception` | propagate to `run_triple`; sets `error=type(e).__name__` |

---

### L-3-3: SIGALRM Timeout Guard

```python
import signal, platform

def _timeout_handler(signum, frame):
    raise TimeoutError("triple timeout")

class _Timeout:
    """Context manager: SIGALRM on POSIX, threading.Timer fallback on Windows."""
    def __init__(self, secs: int):
        self.secs = secs
        self._posix = platform.system() != "Windows"

    def __enter__(self):
        if self._posix:
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(self.secs)
        else:
            import threading
            self._timer = threading.Timer(self.secs, self._raise_timeout)
            self._timer.start()
        return self

    def _raise_timeout(self):
        import ctypes
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(threading.main_thread().ident),
            ctypes.py_object(TimeoutError),
        )

    def __exit__(self, *_):
        if self._posix:
            signal.alarm(0)
        else:
            self._timer.cancel()
# ponytail: Windows fallback is best-effort; upgrade to subprocess isolation if C-ext hangs
```

---

### L-3-4: TripleResult Construction + Error State

```python
def run_triple(
    llm_code: str,
    contracteval_task: dict,
    task_id: str,
    model: str,
    program_idx: int,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
) -> TripleResult:
    n_valid, n_failures, error = 0, 0, None
    try:
        with _Timeout(timeout_secs):
            wrapped = _wrap_with_contracts(llm_code, contracteval_task)
            n_valid, n_failures = _run_pbt(wrapped, budget, rng_seed)
    except TimeoutError:
        error = "TimeoutError"
    except Exception as e:
        error = type(e).__name__

    filter_rate = 1.0 - (n_valid / budget) if budget > 0 else 1.0
    adaptive_failure_rate = n_failures / n_valid if n_valid > 0 else 0.0

    return TripleResult(
        task_id=task_id,
        model=model,
        program_idx=program_idx,
        adaptive_failure_rate=adaptive_failure_rate,
        n_valid=n_valid,
        n_failures=n_failures,
        filter_rate=filter_rate,
        error=error,
    )
```

---

## A-6: Adaptive Contribution Computation [Complexity: 14, Budget: 4 subtasks]

### API Signatures

```python
from dataclasses import dataclass

@dataclass
class ContributionStats:
    mean_adaptive_gap: float
    wilcoxon_stat: float
    wilcoxon_p_raw: float
    wilcoxon_p_holm: float
    ci_lower: float
    ci_upper: float
    fraction_tasks_gt_threshold: float  # tasks where mean_gap > 0.03
    by_model: dict      # {model: {"mean_gap": float, "n_triples": int}}
    by_task_type: dict  # {"humaneval": {"mean_gap": float}, "mbpp": {"mean_gap": float}}
    gate_passed: bool
    n_paired_triples: int

def join_exp_a_b(
    exp_a: list[dict],
    exp_b: list[dict],
    excluded_tasks: list[str],
) -> tuple[list[float], list[float], list[dict]]:
    """Inner join on (task_id, model, program_idx). Returns (a_rates, b_rates, paired_records)."""

def compute_adaptive_contribution(
    exp_a_rates: list[float],
    exp_b_rates: list[float],
    paired_records: list[dict],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ContributionStats: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | join_exp_a_b | Inner join on (task_id, model, program_idx), skip errored triples |
| L-6-2 | Wilcoxon + Holm | Primary test + per-model sub-tests with joint Holm correction |
| L-6-3 | Bootstrap CI | Reuse H-M1 bootstrap_ci on gap list |
| L-6-4 | Per-model sub-analyses + ContributionStats population | Full dataclass assembly |

---

### L-6-1: join_exp_a_b

```python
def join_exp_a_b(
    exp_a: list[dict],
    exp_b: list[dict],
    excluded_tasks: list[str],
) -> tuple[list[float], list[float], list[dict]]:
    excluded = set(excluded_tasks)
    a_index = {
        (r["task_id"], r["model"], r["program_idx"]): r["static_failure_rate"]
        for r in exp_a
        if r["task_id"] not in excluded
    }
    a_rates, b_rates, paired = [], [], []
    for r in exp_b:
        if r["task_id"] in excluded:
            continue
        if r.get("error") is not None:
            continue  # skip errored triples from matching
        key = (r["task_id"], r["model"], r["program_idx"])
        if key not in a_index:
            continue
        a_rate = a_index[key]
        b_rate = r["adaptive_failure_rate"]
        a_rates.append(a_rate)
        b_rates.append(b_rate)
        paired.append({
            "task_id": r["task_id"],
            "model": r["model"],
            "program_idx": r["program_idx"],
            "static_failure_rate": a_rate,
            "adaptive_failure_rate": b_rate,
            "adaptive_gap": b_rate - a_rate,
            "task_type": r.get("task_type", "unknown"),
        })
    return a_rates, b_rates, paired
```

---

### L-6-2: Wilcoxon + Holm

```python
# Primary test — reuse H-M1 wilcoxon_holm directly:
gaps = [b - a for a, b in zip(exp_a_rates, exp_b_rates)]
stat, p_raw, p_holm = wilcoxon_holm(gaps)
# wilcoxon_holm(per_task_gaps: list) uses alternative="greater" internally (verified)

# Per-model sub-tests (5 models, joint Holm correction):
from scipy.stats import wilcoxon as scipy_wilcoxon
from statsmodels.stats.multitest import multipletests

def _per_model_wilcoxon(paired_records: list[dict]) -> dict:
    """Returns {model: {"stat", "p_raw", "p_holm", "mean_gap"}}."""
    model_gaps: dict[str, list[float]] = {}
    for r in paired_records:
        model_gaps.setdefault(r["model"], []).append(r["adaptive_gap"])

    models = list(model_gaps.keys())
    raw_ps, stats_vals, means = [], [], []
    for m in models:
        g = model_gaps[m]
        nonzero = [x for x in g if x != 0.0]
        if len(nonzero) < 2:
            stats_vals.append(0.0); raw_ps.append(1.0)
        else:
            try:
                s, p = scipy_wilcoxon(g, alternative="greater")
                stats_vals.append(float(s)); raw_ps.append(float(p))
            except Exception:
                stats_vals.append(0.0); raw_ps.append(1.0)
        means.append(float(np.mean(g)))

    _, holm_ps, _, _ = multipletests(raw_ps, method="holm")
    return {
        m: {"stat": stats_vals[i], "p_raw": raw_ps[i], "p_holm": float(holm_ps[i]), "mean_gap": means[i]}
        for i, m in enumerate(models)
    }
```

---

### L-6-3: Bootstrap CI

```python
# Direct reuse — verified signature from actual h-m1 code:
# bootstrap_ci(values: list, n_bootstrap: int = 10_000, seed: int = 42) -> tuple[float, float]

gaps = [r["adaptive_gap"] for r in paired_records]
ci_lower, ci_upper = bootstrap_ci(gaps, n_bootstrap=n_bootstrap, seed=seed)
# Returns (2.5th percentile, 97.5th percentile) of bootstrap means distribution
```

---

### L-6-4: ContributionStats Population

```python
def compute_adaptive_contribution(
    exp_a_rates: list[float],
    exp_b_rates: list[float],
    paired_records: list[dict],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ContributionStats:
    import numpy as np

    gaps = [b - a for a, b in zip(exp_a_rates, exp_b_rates)]
    mean_gap = float(np.mean(gaps)) if gaps else 0.0
    stat, p_raw, p_holm = wilcoxon_holm(gaps)
    ci_lower, ci_upper = bootstrap_ci(gaps, n_bootstrap, seed)

    # Per-task fraction where mean gap > 0.03
    task_means: dict[str, list[float]] = {}
    for r in paired_records:
        task_means.setdefault(r["task_id"], []).append(r["adaptive_gap"])
    per_task_gaps = [float(np.mean(v)) for v in task_means.values()]
    fraction_gt = sum(1 for g in per_task_gaps if g > 0.03) / max(len(per_task_gaps), 1)

    model_stats = _per_model_wilcoxon(paired_records)
    by_model = {
        m: {"mean_gap": d["mean_gap"], "n_triples": sum(1 for r in paired_records if r["model"] == m)}
        for m, d in model_stats.items()
    }

    type_gaps: dict[str, list[float]] = {}
    for r in paired_records:
        type_gaps.setdefault(r["task_type"], []).append(r["adaptive_gap"])
    by_task_type = {tt: {"mean_gap": float(np.mean(g))} for tt, g in type_gaps.items()}

    return ContributionStats(
        mean_adaptive_gap=mean_gap,
        wilcoxon_stat=stat,
        wilcoxon_p_raw=p_raw,
        wilcoxon_p_holm=p_holm,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        fraction_tasks_gt_threshold=fraction_gt,
        by_model=by_model,
        by_task_type=by_task_type,
        gate_passed=(mean_gap > 0.0 and p_holm < 0.05),
        n_paired_triples=len(paired_records),
    )
```

---

## A-4: Experiment B Runner — Parallelism [Complexity: 13, Budget: 3 subtasks]

### API Signatures

```python
def run_experiment_b(
    tasks: dict,
    corpus: dict,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
    n_workers: int = 16,
    output_path: str = "results/experiment_b_results.jsonl",
) -> list[TripleResult]: ...

def verify_experiment_b_activated(results: list[TripleResult]) -> tuple[bool, dict]: ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Pool triple enumeration + worker signature | (model, task_id, program_idx) arg tuples |
| L-4-2 | Incremental JSONL write via imap_unordered | Main-thread writer from pool stream |
| L-4-3 | verify_experiment_b_activated | 4-indicator logic with thresholds |

---

### L-4-1: Pool Triple Enumeration + Worker

```python
import multiprocessing as mp
from dataclasses import asdict

def _enumerate_triples(tasks: dict, corpus: dict) -> list[tuple]:
    """Returns list of (llm_code, contracteval_task, task_id, model, program_idx)."""
    args = []
    for model, task_programs in corpus.items():
        for task_id, programs in task_programs.items():
            if task_id not in tasks:
                continue
            for idx, code in enumerate(programs):
                args.append((code, tasks[task_id], task_id, model, idx))
    return args

def _triple_worker(args: tuple) -> dict:
    """Pickle-safe top-level worker. Returns asdict(TripleResult)."""
    llm_code, contracteval_task, task_id, model, program_idx = args
    result = run_triple(llm_code, contracteval_task, task_id, model, program_idx)
    return asdict(result)
```

---

### L-4-2: Incremental JSONL Write via imap_unordered

```python
def run_experiment_b(
    tasks: dict,
    corpus: dict,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
    n_workers: int = 16,
    output_path: str = "results/experiment_b_results.jsonl",
) -> list[TripleResult]:
    import json, tqdm
    from pathlib import Path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    all_args = _enumerate_triples(tasks, corpus)
    all_results: list[TripleResult] = []

    with mp.Pool(n_workers) as pool, open(output_path, "w") as f:
        for result_dict in tqdm.tqdm(
            pool.imap_unordered(_triple_worker, all_args),
            total=len(all_args),
            desc="Experiment B",
        ):
            f.write(json.dumps(result_dict) + "\n")
            f.flush()  # incremental persistence
            all_results.append(TripleResult(**result_dict))

    return all_results
# ponytail: imap_unordered chunksize=1 (default); bump to 4 if IPC overhead is measurable
```

---

### L-4-3: verify_experiment_b_activated

```python
def verify_experiment_b_activated(results: list[TripleResult]) -> tuple[bool, dict]:
    """Gate: >= 3/4 indicators pass."""
    n = len(results)
    if n == 0:
        return False, {"error": "no results"}

    n_valid_sufficient = sum(1 for r in results if r.n_valid >= 100)
    n_filter_total = sum(1 for r in results if r.filter_rate >= 1.0)
    unique_rates = {r.adaptive_failure_rate for r in results}

    indicators = {
        "yield_sufficient": (n_valid_sufficient / n) >= 0.80,   # >= 80% triples with n_valid >= 100
        "filter_not_total": n_filter_total == 0,                 # no triple with filter_rate = 1.0
        "adaptive_gap_measurable": len(unique_rates) > 1,        # rates differ across triples
        "triples_covered": n >= 10_000,                          # >= 10,000 triples evaluated
    }

    # Informational failure-mode stats
    strategy_errors = sum(1 for r in results if r.error == "StrategyInferenceError")
    task_ids = {r.task_id for r in results}
    zero_valid_tasks = len({r.task_id for r in results if r.n_valid == 0})
    indicators["strategy_error_rate"] = strategy_errors / max(n, 1)
    indicators["zero_valid_task_fraction"] = zero_valid_tasks / max(len(task_ids), 1)

    gate_passed = sum(v for k, v in indicators.items() if k in {
        "yield_sufficient", "filter_not_total", "adaptive_gap_measurable", "triples_covered"
    }) >= 3
    indicators["gate_passed"] = gate_passed

    return gate_passed, indicators
```

---

## A-2: Compatibility Pre-check [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
def run_compatibility_precheck(
    tasks: dict,
    corpus: dict,
    n_tasks: int = 20,
    seed: int = 42,
    min_valid: int = 100,
    max_filter_rate: float = 0.95,
) -> dict:
    """Returns {task_id: {"filter_rate": float, "n_valid": int, "passed": bool, "error": str|None}}."""

def check_precheck_gate(
    precheck_results: dict,
    min_passing: int = 15,
) -> tuple[bool, dict]:
    """Returns (gate_passed, summary). Gate: >= min_passing tasks with passed=True."""
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | run_compatibility_precheck | 20-task sample with seed=42, one program per task, budget=500 |
| L-2-2 | check_precheck_gate | Threshold logic and summary dict |

---

### L-2-1: run_compatibility_precheck

```python
import random

def run_compatibility_precheck(
    tasks: dict,
    corpus: dict,
    n_tasks: int = 20,
    seed: int = 42,
    min_valid: int = 100,
    max_filter_rate: float = 0.95,
) -> dict:
    rng = random.Random(seed)
    sample_ids = rng.sample(list(tasks.keys()), min(n_tasks, len(tasks)))

    results = {}
    for task_id in sample_ids:
        llm_code = None
        for model_corpus in corpus.values():
            programs = model_corpus.get(task_id, [])
            if programs:
                llm_code = programs[0]
                break
        if llm_code is None:
            results[task_id] = {"filter_rate": 1.0, "n_valid": 0, "passed": False, "error": "no_program"}
            continue

        triple = run_triple(
            llm_code=llm_code,
            contracteval_task=tasks[task_id],
            task_id=task_id,
            model="precheck",
            program_idx=0,
            budget=500,        # smaller budget for speed
            timeout_secs=30,
        )
        passed = triple.n_valid >= min_valid and triple.filter_rate <= max_filter_rate
        results[task_id] = {
            "filter_rate": triple.filter_rate,
            "n_valid": triple.n_valid,
            "passed": passed,
            "error": triple.error,
        }
    return results
```

---

### L-2-2: check_precheck_gate

```python
import numpy as np

def check_precheck_gate(
    precheck_results: dict,
    min_passing: int = 15,
) -> tuple[bool, dict]:
    n_total = len(precheck_results)
    n_passed = sum(1 for r in precheck_results.values() if r["passed"])
    gate_passed = n_passed >= min_passing

    summary = {
        "n_total": n_total,
        "n_passed": n_passed,
        "n_failed": n_total - n_passed,
        "gate_passed": gate_passed,
        "failed_tasks": [tid for tid, r in precheck_results.items() if not r["passed"]],
        "mean_filter_rate": float(np.mean([r["filter_rate"] for r in precheck_results.values()])) if n_total else 0.0,
    }
    return gate_passed, summary
```
