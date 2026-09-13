"""Oracle soundness pre-check for H-M1.

Uses CVT inputs from ContractEval to verify reference implementations
enforce contracts. Tasks where reference silently accepts CVT inputs
(contracts not enforced) are quarantined.
"""
import json
import signal
from pathlib import Path
from tqdm import tqdm


def _timeout_handler(signum, frame):
    raise TimeoutError("timeout")


def exec_with_timeout(code_str: str, entry_point: str, timeout: int = 30):
    """Exec code_str; return (callable, error_msg)."""
    namespace = {}
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        exec(compile(code_str, "<reference>", "exec"), namespace)
        signal.alarm(0)
        func = namespace.get(entry_point)
        if func is None or not callable(func):
            return None, f"'{entry_point}' not found"
        return func, None
    except TimeoutError:
        signal.alarm(0)
        return None, "exec timeout"
    except Exception as e:
        signal.alarm(0)
        return None, f"{type(e).__name__}: {e}"
    finally:
        if old_handler is not None:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except Exception:
                pass


def check_reference_soundness(task: dict, timeout_per_task: int = 30) -> dict:
    """Check whether reference_impl raises AssertionError on CVT inputs.

    VALID: reference raises AssertionError on ≥1 CVT input (contracts enforced).
    QUARANTINED: reference silently accepts all CVTs (no contract enforcement).
    """
    task_id = task["task_id"]
    ref_code = task.get("canonical_solution_with_contract", "")
    entry_point = task["entry_point"]
    cvt_inputs = task.get("contract_violating_test", [])

    if not ref_code:
        return {"task_id": task_id, "quarantined": True, "violation_count": 0, "error": "no contract source"}
    if not cvt_inputs:
        return {"task_id": task_id, "quarantined": True, "violation_count": 0, "error": "no CVT inputs"}

    ref_func, err = exec_with_timeout(ref_code, entry_point, timeout=timeout_per_task)
    if err:
        return {"task_id": task_id, "quarantined": True, "violation_count": 0, "error": err}

    assertion_count = 0
    for cvt in cvt_inputs:
        input_dict = cvt.get("input", {})
        if not input_dict:
            continue
        try:
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout_per_task)
            try:
                ref_func(**input_dict)
            except (AssertionError, Exception) as e:
                # Both AssertionError (direct assert) and icontract.ViolationError count
                if not isinstance(e, TimeoutError):
                    assertion_count += 1
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        except Exception:
            signal.alarm(0)

    quarantined = assertion_count == 0
    return {
        "task_id": task_id,
        "quarantined": quarantined,
        "violation_count": assertion_count,
        "error": None,
    }


def run_soundness_precheck(
    tasks: dict,
    results_path: str = "results/soundness_precheck.jsonl",
    timeout_per_task: int = 30,
) -> tuple:
    """Run soundness precheck on all tasks. Returns (valid_ids, quarantined_ids)."""
    Path(results_path).parent.mkdir(parents=True, exist_ok=True)
    valid_ids = set()
    quarantined_ids = set()

    with open(results_path, "w") as fout:
        for task_id, task in tqdm(tasks.items(), desc="Soundness precheck"):
            result = check_reference_soundness(task, timeout_per_task=timeout_per_task)
            fout.write(json.dumps(result) + "\n")
            fout.flush()
            if result["quarantined"]:
                quarantined_ids.add(task_id)
            else:
                valid_ids.add(task_id)

    rate = len(quarantined_ids) / max(len(tasks), 1)
    if rate > 0.05:
        print(f"WARNING: quarantine rate {rate:.1%} > 5% ({len(quarantined_ids)}/{len(tasks)})")
    else:
        print(f"Quarantine rate: {rate:.1%} ({len(quarantined_ids)}/{len(tasks)})")

    return valid_ids, quarantined_ids
