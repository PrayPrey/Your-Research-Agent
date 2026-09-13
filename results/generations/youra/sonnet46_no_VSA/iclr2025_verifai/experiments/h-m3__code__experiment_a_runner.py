"""Experiment A: static oracle on ContractEval base_input + plus_input."""
import signal
import json
import multiprocessing as mp
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


def _timeout_handler(signum, frame):
    raise TimeoutError("timeout")


class _Timeout:
    def __init__(self, secs: int):
        self.secs = secs

    def __enter__(self):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(self.secs)
        return self

    def __exit__(self, *_):
        signal.alarm(0)


@dataclass
class StaticTripleResult:
    task_id: str
    model: str
    program_idx: int
    static_failure_rate: float
    n_inputs: int
    n_failures: int
    task_type: str
    error: Optional[str]


def _exec_fn(code_str: str, entry_point: str) -> tuple:
    ns = {}
    try:
        exec(compile(code_str, "<code>", "exec"), ns)
        fn = ns.get(entry_point)
        if fn is None or not callable(fn):
            return None, f"'{entry_point}' not found"
        return fn, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _call_safe(fn, args: list, timeout: int = 5):
    """Returns (result, error_str)."""
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        result = fn(*args)
        signal.alarm(0)
        return result, None
    except TimeoutError:
        signal.alarm(0)
        return None, "TimeoutError"
    except AssertionError:
        signal.alarm(0)
        return None, "AssertionError"
    except Exception as e:
        signal.alarm(0)
        return None, type(e).__name__
    finally:
        if old_handler is not None:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except Exception:
                pass


def run_static_triple(
    llm_code: str,
    contracteval_task: dict,
    task_id: str,
    model: str,
    program_idx: int,
    timeout_secs: int = 10,
) -> StaticTripleResult:
    """Evaluate LLM program on base_input + plus_input; check contract violation."""
    entry_point = contracteval_task["entry_point"]
    task_type = "humaneval" if task_id.startswith("HumanEval") else "mbpp"

    llm_fn, err = _exec_fn(llm_code, entry_point)
    if err:
        return StaticTripleResult(task_id, model, program_idx, 0.0, 0, 0, task_type, err)

    contract_ref_fn, err2 = _exec_fn(
        contracteval_task.get("canonical_solution_with_contract", ""), entry_point
    )
    if err2:
        return StaticTripleResult(task_id, model, program_idx, 0.0, 0, 0, task_type, f"ref:{err2}")

    inputs = list(contracteval_task.get("base_input", [])) + list(contracteval_task.get("plus_input", []))
    n_inputs = len(inputs)
    n_failures = 0

    for inp in inputs:
        args = inp if isinstance(inp, list) else [inp]
        # Check if contract reference rejects this input (contract violation)
        _, ref_err = _call_safe(contract_ref_fn, args, timeout_secs)
        if ref_err == "AssertionError":
            # Contract violation: check if LLM also rejects
            _, llm_err = _call_safe(llm_fn, args, timeout_secs)
            if llm_err is None:
                n_failures += 1  # LLM accepts input that violates contract

    static_failure_rate = n_failures / n_inputs if n_inputs > 0 else 0.0
    return StaticTripleResult(task_id, model, program_idx, static_failure_rate, n_inputs, n_failures, task_type, None)


def _static_worker(args: tuple) -> dict:
    llm_code, contracteval_task, task_id, model, program_idx = args
    result = run_static_triple(llm_code, contracteval_task, task_id, model, program_idx)
    return asdict(result)


def run_experiment_a(
    tasks: dict,
    corpus: dict,
    n_workers: int = 16,
    output_path: str = "results/experiment_a_results.jsonl",
) -> list[StaticTripleResult]:
    import tqdm

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    all_args = []
    for model, task_programs in corpus.items():
        for task_id, programs in task_programs.items():
            if task_id not in tasks:
                continue
            for idx, code in enumerate(programs):
                all_args.append((code, tasks[task_id], task_id, model, idx))

    all_results = []
    with mp.Pool(n_workers) as pool, open(output_path, "w") as f:
        for result_dict in tqdm.tqdm(
            pool.imap_unordered(_static_worker, all_args),
            total=len(all_args),
            desc="Experiment A (static)",
        ):
            f.write(json.dumps(result_dict) + "\n")
            f.flush()
            all_results.append(StaticTripleResult(**result_dict))

    return all_results
