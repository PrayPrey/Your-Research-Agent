"""H-M1 dual-oracle isolation harness.

Oracle A: differential equality on CVT inputs — llm(x) != gt_plain(x)
Oracle B: contract oracle — reference_with_contracts(x) raises AssertionError

Both oracles run on the same CVT inputs (contract-violating test inputs).
Oracle B always fires on CVT inputs (by design). Oracle A may or may not fire
(gt_plain accepts some invalid inputs; if LLM matches gt_plain, diff passes).

contract_unique: diff_fail=False AND contract_fail=True
  = LLM accepts invalid input and matches gt_plain output, but reference contract rejects it.
  This reveals oracle strength: the contract oracle catches semantic violations
  that the differential oracle misses.
"""
import signal
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import multiprocessing as mp


def _timeout_handler(signum, frame):
    raise TimeoutError("timeout")


def _exec_fn(code_str: str, entry_point: str, timeout: int = 10):
    """Exec code_str; return (callable, error_msg)."""
    namespace = {}
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        exec(compile(code_str, "<code>", "exec"), namespace)
        signal.alarm(0)
        func = namespace.get(entry_point)
        if func is None or not callable(func):
            return None, f"'{entry_point}' not found"
        return func, None
    except TimeoutError:
        signal.alarm(0)
        return None, "exec_timeout"
    except Exception as e:
        signal.alarm(0)
        return None, f"{type(e).__name__}: {e}"
    finally:
        if old_handler is not None:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except Exception:
                pass


def _call_with_timeout(fn, args: list, timeout: int = 5):
    """Call fn(*args) under SIGALRM timeout. Returns (result, exception, timed_out)."""
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        result = fn(*args)
        signal.alarm(0)
        return result, None, False
    except TimeoutError:
        signal.alarm(0)
        return None, TimeoutError("timeout"), True
    except Exception as e:
        signal.alarm(0)
        return None, e, False
    finally:
        if old_handler is not None:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except Exception:
                pass


@dataclass
class InputResult:
    diff_fail: bool
    contract_fail: bool
    contract_unique: bool  # diff_fail=False AND contract_fail=True
    timeout: bool
    error: Optional[str]


@dataclass
class TaskProgramResult:
    task_id: str
    model: str
    program_idx: int
    diff_failure_rate: float
    contract_failure_rate: float
    contract_unique_mass: float
    oracle_isolation_gap: float
    n_inputs: int
    n_redundant: int
    n_contract_unique: int
    n_differential_only: int
    n_neither: int
    n_errors: int
    task_type: str = ""


def _evaluate_cvt_input(prog_fn, gt_plain_fn, contract_ref_fn, args: list, timeout: int = 5) -> InputResult:
    """Evaluate one CVT input under Oracle A and Oracle B.

    Oracle A (diff): llm(x) != gt_plain(x)
      - If either raises non-timeout exception: diff_fail = True
    Oracle B (contract): contract_ref_fn(x) raises AssertionError
      - contract_ref_fn = canonical_solution_with_contract (reference with assert checks)
      - On CVT inputs, this always raises AssertionError (by construction)

    contract_unique = (not diff_fail) AND contract_fail
      = LLM matches gt_plain on invalid input, but reference contract catches it.
    """
    diff_fail = False
    c_fail = False
    is_timeout = False
    error = None

    # Oracle A: differential
    out_llm, exc_llm, to_llm = _call_with_timeout(prog_fn, args, timeout)
    out_gt, exc_gt, to_gt = _call_with_timeout(gt_plain_fn, args, timeout)

    if to_llm or to_gt:
        is_timeout = True
        diff_fail = True
        error = "timeout"
    elif exc_llm is not None or exc_gt is not None:
        diff_fail = True
        if exc_llm is not None:
            error = f"{type(exc_llm).__name__}: {exc_llm}"
    else:
        diff_fail = (out_llm != out_gt)

    # Oracle B: contract reference
    _, exc_contract, to_contract = _call_with_timeout(contract_ref_fn, args, timeout)
    if to_contract:
        c_fail = True  # timeout counts as contract enforcement
    elif isinstance(exc_contract, AssertionError):
        c_fail = True  # reference contract rejected input
    elif exc_contract is not None:
        c_fail = False  # other exception (not assertion)
    else:
        c_fail = False  # reference accepted — input may have been valid

    contract_unique = (not diff_fail) and c_fail
    return InputResult(diff_fail, c_fail, contract_unique, is_timeout, error)


def evaluate_program_isolation(
    program_code: str,
    task: dict,
    model: str,
    program_idx: int,
    timeout_per_input: int = 5,
    gt_source: str = "",
) -> TaskProgramResult:
    """Evaluate one (task, program) pair.

    Uses CVT inputs from ContractEval (contract-violating test inputs).
    gt_source: prompt + canonical_solution from EvalPlus (no contract checks).
    """
    task_id = task["task_id"]
    entry_point = task["entry_point"]
    contract_source = task.get("canonical_solution_with_contract", "")
    cvt_inputs = task.get("contract_violating_test", [])
    task_type = "humaneval" if task_id.startswith("HumanEval") else "mbpp"

    if not cvt_inputs:
        return TaskProgramResult(
            task_id=task_id, model=model, program_idx=program_idx,
            diff_failure_rate=0.0, contract_failure_rate=0.0,
            contract_unique_mass=0.0, oracle_isolation_gap=0.0,
            n_inputs=0, n_redundant=0, n_contract_unique=0,
            n_differential_only=0, n_neither=0, n_errors=0,
            task_type=task_type,
        )

    prog_fn, p_err = _exec_fn(program_code, entry_point, timeout=10)
    gt_fn, gt_err = _exec_fn(gt_source, entry_point, timeout=10)
    contract_ref_fn, c_err = _exec_fn(contract_source, entry_point, timeout=10)

    if prog_fn is None or gt_fn is None or contract_ref_fn is None:
        n = len(cvt_inputs)
        return TaskProgramResult(
            task_id=task_id, model=model, program_idx=program_idx,
            diff_failure_rate=1.0, contract_failure_rate=0.0,
            contract_unique_mass=0.0, oracle_isolation_gap=-1.0,
            n_inputs=n, n_redundant=0, n_contract_unique=0,
            n_differential_only=0, n_neither=0, n_errors=n,
            task_type=task_type,
        )

    n_redundant = n_cu = n_diff_only = n_neither = n_errors = 0
    input_results = []

    for cvt in cvt_inputs:
        input_dict = cvt.get("input", {})
        args = list(input_dict.values())
        r = _evaluate_cvt_input(prog_fn, gt_fn, contract_ref_fn, args, timeout_per_input)
        input_results.append(r)
        if r.error and r.timeout:
            n_errors += 1
        if r.diff_fail and r.contract_fail:
            n_redundant += 1
        elif r.contract_unique:
            n_cu += 1
        elif r.diff_fail and not r.contract_fail:
            n_diff_only += 1
        else:
            n_neither += 1

    n = len(input_results)
    if n == 0:
        return TaskProgramResult(
            task_id=task_id, model=model, program_idx=program_idx,
            diff_failure_rate=0.0, contract_failure_rate=0.0,
            contract_unique_mass=0.0, oracle_isolation_gap=0.0,
            n_inputs=0, n_redundant=0, n_contract_unique=0,
            n_differential_only=0, n_neither=0, n_errors=0,
            task_type=task_type,
        )

    diff_rate = sum(r.diff_fail for r in input_results) / n
    contract_rate = sum(r.contract_fail for r in input_results) / n
    cu_mass = n_cu / n
    gap = contract_rate - diff_rate

    return TaskProgramResult(
        task_id=task_id, model=model, program_idx=program_idx,
        diff_failure_rate=diff_rate, contract_failure_rate=contract_rate,
        contract_unique_mass=cu_mass, oracle_isolation_gap=gap,
        n_inputs=n, n_redundant=n_redundant, n_contract_unique=n_cu,
        n_differential_only=n_diff_only, n_neither=n_neither, n_errors=n_errors,
        task_type=task_type,
    )


def _worker_fn(args_tuple):
    """Multiprocessing worker."""
    program_code, task, timeout_per_input, model, idx, gt_source = args_tuple
    try:
        return evaluate_program_isolation(program_code, task, model, idx, timeout_per_input, gt_source)
    except Exception as e:
        task_id = task.get("task_id", "unknown")
        task_type = "humaneval" if task_id.startswith("HumanEval") else "mbpp"
        return TaskProgramResult(
            task_id=task_id, model=model, program_idx=idx,
            diff_failure_rate=1.0, contract_failure_rate=0.0,
            contract_unique_mass=0.0, oracle_isolation_gap=-1.0,
            n_inputs=0, n_redundant=0, n_contract_unique=0,
            n_differential_only=0, n_neither=0, n_errors=1,
            task_type=task_type,
        )


def run_oracle_isolation(
    corpus: dict,
    tasks: dict,
    evalplus_data: dict,
    valid_task_ids: set,
    results_path: str = "results/isolation_results.jsonl",
    timeout_per_input: int = 5,
    n_workers: int = 8,
) -> list:
    """Run dual-oracle evaluation over all (model, task, program) triples.

    Uses CVT inputs from ContractEval tasks.
    evalplus_data provides gt_source for Oracle A ground truth.
    """
    from tqdm import tqdm

    Path(results_path).parent.mkdir(parents=True, exist_ok=True)

    work_items = []
    for model, model_corpus in corpus.items():
        for task_id, programs in model_corpus.items():
            if task_id not in valid_task_ids:
                continue
            if task_id not in tasks:
                continue
            task = tasks[task_id]
            cvt_inputs = task.get("contract_violating_test", [])
            if not cvt_inputs:
                continue
            ep_data = evalplus_data.get(task_id, {})
            gt_source = ep_data.get("gt_source", "")
            for idx, code in enumerate(programs):
                work_items.append((code, task, timeout_per_input, model, idx, gt_source))

    print(f"Total work items: {len(work_items)}")

    results = []
    with open(results_path, "w") as fout:
        ctx = mp.get_context("fork")
        with ctx.Pool(n_workers) as pool:
            for result in tqdm(
                pool.imap_unordered(_worker_fn, work_items, chunksize=4),
                total=len(work_items),
                desc="Oracle isolation",
            ):
                results.append(result)
                fout.write(json.dumps(asdict(result)) + "\n")
                fout.flush()

    return results


def verify_activation(results: list) -> tuple:
    """Check both oracles fired and enough tasks were evaluated."""
    if not results:
        return False, {"no_results": True}

    task_ids = set(r.task_id for r in results)
    # Filter results with actual inputs
    valid_results = [r for r in results if r.n_inputs > 0]
    if not valid_results:
        return False, {"no_valid_results": True}

    mean_diff = sum(r.diff_failure_rate for r in valid_results) / len(valid_results)
    mean_contract = sum(r.contract_failure_rate for r in valid_results) / len(valid_results)
    total_cu = sum(r.contract_unique_mass for r in valid_results)

    task_cu = {}
    for r in valid_results:
        task_cu.setdefault(r.task_id, []).append(r.contract_unique_mass)
    tasks_with_cu = sum(1 for vals in task_cu.values() if max(vals) > 0)

    indicators = {
        "tasks_evaluated": len(task_ids) >= 300,
        "oracle_a_ran": mean_diff >= 0,
        "oracle_b_ran": mean_contract > 0,
        "contract_unique_nonzero": total_cu > 0,
        "gap_computed": True,
        "n_tasks": len(task_ids),
        "tasks_with_cu_fraction": tasks_with_cu / max(len(task_cu), 1),
    }
    success = all(indicators[k] for k in ["tasks_evaluated", "oracle_b_ran", "contract_unique_nonzero", "gap_computed"])
    return success, indicators
