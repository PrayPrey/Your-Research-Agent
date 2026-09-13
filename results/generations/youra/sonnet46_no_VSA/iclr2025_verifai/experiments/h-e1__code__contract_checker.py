"""Contract-strength gap checker using ContractEval's contract_violating_test inputs.

Strategy: instead of icontract_hypothesis.infer_strategy() (which requires @require
decorators not present in this dataset), we use the pre-computed contract_violating_test
inputs from ContractEval. Each CVT input is designed to violate a specific contract of
the reference implementation. We run the LLM-generated code on these inputs and check
whether it raises an AssertionError (meaning the contract was violated by the LLM code
too) or returns silently (meaning the LLM code has no contract protection).

The "contract-strength gap" is the fraction of test-passing programs that fail to
raise an AssertionError on at least one CVT input — i.e., the program silently accepts
contract-violating inputs, revealing weaker semantic contracts than the reference.

NOTE: An LLM program "fails" a contract if it does NOT raise an error on a CVT input
(it should raise an error, as the reference impl would via contract assertions).
"""
import signal
import json
from typing import Optional


def _timeout_handler(signum, frame):
    raise TimeoutError("execution timeout")


def exec_with_timeout(
    code_str: str,
    entry_point: str,
    timeout: int = 60,
) -> tuple[Optional[object], Optional[str]]:
    """Exec code_str in isolated namespace; return (callable, None) or (None, error_msg)."""
    namespace = {}
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        exec(compile(code_str, "<generated>", "exec"), namespace)
        signal.alarm(0)
        func = namespace.get(entry_point)
        if func is None or not callable(func):
            return None, f"entry_point '{entry_point}' not found in namespace"
        return func, None
    except TimeoutError:
        signal.alarm(0)
        return None, "exec timeout"
    except Exception as e:
        signal.alarm(0)
        return None, f"exec error: {type(e).__name__}: {e}"
    finally:
        if old_handler is not None:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except Exception:
                pass


def _run_cvt_checks(generated_func, cvt_inputs):
    """Run all CVT checks under caller's SIGALRM budget. Returns (n_total, n_failures)."""
    n_total = 0
    n_failures = 0
    for cvt in cvt_inputs:
        input_dict = cvt.get("input", {})
        n_total += 1
        try:
            generated_func(**input_dict)
            n_failures += 1  # silent accept = gap
        except AssertionError:
            pass  # good: contract enforced
        except Exception:
            pass  # other error = rejected input = no gap
    return n_total, n_failures


def check_program_contract(
    generated_code: str,
    entry_point: str,
    cvt_inputs: list[dict],
    timeout: int = 30,
) -> dict:
    """Check if generated_code violates contracts using CVT inputs.

    Returns: {violated, n_failures, n_total, gap, error}
    where 'violated'=True means gap > 0 (program is weaker than reference).
    """
    namespace = {}
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        # exec + all CVT calls under one SIGALRM budget
        exec(compile(generated_code, "<generated>", "exec"), namespace)
        generated_func = namespace.get(entry_point)
        if generated_func is None or not callable(generated_func):
            signal.alarm(0)
            return {"violated": False, "n_failures": 0, "n_total": 0, "gap": 0.0,
                    "error": f"entry_point '{entry_point}' not found"}
        n_total, n_failures = _run_cvt_checks(generated_func, cvt_inputs)
        signal.alarm(0)
    except TimeoutError:
        signal.alarm(0)
        return {"violated": False, "n_failures": 0, "n_total": 0, "gap": 0.0,
                "error": "timeout"}
    except Exception as e:
        signal.alarm(0)
        return {"violated": False, "n_failures": 0, "n_total": 0, "gap": 0.0,
                "error": f"{type(e).__name__}: {e}"}
    finally:
        if old_handler is not None:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except Exception:
                pass

    gap = n_failures / n_total if n_total > 0 else 0.0
    return {
        "violated": n_failures > 0,
        "n_failures": n_failures,
        "n_total": n_total,
        "gap": gap,
        "error": None,
    }


def run_contract_checking(
    tasks: dict[str, dict],
    passing_samples: dict[str, list[str]],
    model: str,
    results_path: str,
    timeout: int = 60,
) -> list[dict]:
    """Run contract checking for all passing samples of a model.

    Streams results to JSONL; returns list of result dicts.
    """
    from pathlib import Path
    from tqdm import tqdm

    Path(results_path).parent.mkdir(parents=True, exist_ok=True)
    results = []

    with open(results_path, "w") as fout:
        for task_id, codes in tqdm(passing_samples.items(), desc=f"PBT [{model}]"):
            task = tasks.get(task_id)
            if task is None:
                continue
            entry_point = task["entry_point"]
            cvt_inputs = task.get("contract_violating_test", [])
            if not cvt_inputs:
                # No CVTs for this task — skip
                continue

            for code in codes:
                result = check_program_contract(
                    generated_code=code,
                    entry_point=entry_point,
                    cvt_inputs=cvt_inputs,
                    timeout=timeout,
                )
                record = {
                    "task_id": task_id,
                    "model": model,
                    **result,
                }
                results.append(record)
                fout.write(json.dumps(record) + "\n")
            fout.flush()

    return results
