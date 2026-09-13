"""Oracle soundness pre-check.

Verifies that the reference implementation (canonical_solution_with_contract)
does NOT silently accept its own CVT inputs. If the reference impl also has no
contract-checking assertions, the task is quarantined.
"""
import json
import signal
from pathlib import Path
from tqdm import tqdm


def _timeout_handler(signum, frame):
    raise TimeoutError("timeout")


def exec_with_timeout(code_str: str, entry_point: str, timeout: int = 30):
    """Execute code_str and return (callable, error_msg)."""
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


def check_reference_impl(
    task: dict,
    timeout_per_task: int = 30,
) -> dict:
    """Check whether reference_impl raises AssertionError on CVT inputs.

    A task is VALID if the reference impl raises AssertionError on ≥1 CVT input.
    A task is QUARANTINED if the reference impl silently accepts all CVT inputs
    (meaning the contracts are not enforced in the reference impl either).

    Returns: {task_id, quarantined, violation_count, error}
    """
    task_id = task["task_id"]
    ref_code = task.get("canonical_solution_with_contract", "")
    entry_point = task["entry_point"]
    cvt_inputs = task.get("contract_violating_test", [])

    if not cvt_inputs:
        return {
            "task_id": task_id,
            "quarantined": True,
            "violation_count": 0,
            "error": "no CVT inputs",
        }

    ref_func, err = exec_with_timeout(ref_code, entry_point, timeout=timeout_per_task)
    if err:
        return {
            "task_id": task_id,
            "quarantined": True,
            "violation_count": 0,
            "error": err,
        }

    assertion_count = 0
    for cvt in cvt_inputs:
        input_dict = cvt.get("input", {})
        try:
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout_per_task)
            try:
                ref_func(**input_dict)
                # No error — reference impl accepted this CVT input silently
            except AssertionError:
                assertion_count += 1
            except Exception:
                pass
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        except TimeoutError:
            signal.alarm(0)
            break

    # Task is VALID if reference impl raises AssertionError on at least one CVT input
    quarantined = assertion_count == 0

    return {
        "task_id": task_id,
        "quarantined": quarantined,
        "violation_count": assertion_count,
        "error": None,
    }


def run_soundness_precheck(
    tasks: dict[str, dict],
    results_path: str = "results/oracle_precheck.jsonl",
    timeout_per_task: int = 30,
) -> tuple[set[str], set[str]]:
    """Run oracle soundness pre-check on all tasks.

    Returns (valid_task_ids, quarantined_task_ids).
    """
    Path(results_path).parent.mkdir(parents=True, exist_ok=True)
    valid_ids: set[str] = set()
    quarantined_ids: set[str] = set()

    with open(results_path, "w") as fout:
        for task_id, task in tqdm(tasks.items(), desc="Oracle pre-check"):
            result = check_reference_impl(task, timeout_per_task=timeout_per_task)
            fout.write(json.dumps(result) + "\n")
            fout.flush()

            if result["quarantined"]:
                quarantined_ids.add(task_id)
            else:
                valid_ids.add(task_id)

    quarantine_rate = len(quarantined_ids) / max(len(tasks), 1)
    if quarantine_rate > 0.05:
        print(f"WARNING: quarantine rate {quarantine_rate:.1%} exceeds 5% threshold")
    else:
        print(f"Quarantine rate: {quarantine_rate:.1%} ({len(quarantined_ids)}/{len(tasks)})")

    return valid_ids, quarantined_ids
