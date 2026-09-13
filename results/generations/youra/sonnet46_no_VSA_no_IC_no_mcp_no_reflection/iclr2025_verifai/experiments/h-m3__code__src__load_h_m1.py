"""Load failing solutions from H-M1 results."""
import json
import re
import sys
from pathlib import Path

H_M1_RESULTS = Path(__file__).parent.parent.parent.parent / "h-m1" / "code" / "results" / "h-m1"
H_M1_CODE = Path(__file__).parent.parent.parent.parent / "h-m1" / "code"
H_E1_COMPLETIONS = Path(__file__).parent.parent.parent.parent / "h-e1" / "code" / "results" / "completions.jsonl"


def _extract_code(completion: str) -> str:
    """Strip markdown fences from completion."""
    m = re.search(r"```python\n(.*?)```", completion, re.DOTALL)
    if m:
        return m.group(1)
    return completion.strip()


def load_failing_records() -> list[dict]:
    """Load H-M1 failing solutions with code and test harness attached."""
    results_path = H_M1_RESULTS / "results.jsonl"
    completions_path = H_M1_RESULTS / "completions.jsonl"

    # Load completions keyed by problem_id (H-M1 has MB_; H-E1 has HE_)
    completions = {}
    for cpath in [completions_path, H_E1_COMPLETIONS]:
        if Path(cpath).exists():
            with open(cpath) as f:
                for line in f:
                    rec = json.loads(line)
                    pid = rec.get("problem_id") or rec.get("task_id")
                    if pid and pid not in completions:
                        completions[pid] = _extract_code(rec["completion"])

    # Load problems for test code using spec_from_file_location to avoid src namespace clash
    problems_by_id = {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "h_m1_data_loader",
            str(H_M1_CODE / "src" / "data_loader.py")
        )
        data_loader = importlib.util.module_from_spec(spec)
        # data_loader depends on human_eval and datasets — add h-m1 to path temporarily
        _old_path = sys.path[:]
        sys.path.insert(0, str(H_M1_CODE))
        spec.loader.exec_module(data_loader)
        sys.path[:] = _old_path
        for p in data_loader.load_problems():
            problems_by_id[p.problem_id] = p
    except Exception as e:
        print(f"  Warning: could not load problems for test code: {e}")

    failing = []
    with open(results_path) as f:
        for line in f:
            rec = json.loads(line)
            if not rec["passed"]:
                pid = rec["id"]
                code = completions.get(pid, "")
                problem = problems_by_id.get(pid)
                test_code = problem.test_code if problem else ""
                entry_point = problem.entry_point if problem else ""
                prompt = problem.prompt if problem else ""
                # Build full runnable code: prompt (with signature) + body + test harness
                if test_code and entry_point and prompt:
                    full_code = prompt + code + "\n" + test_code + f"\ncheck({entry_point})\n"
                    static_code = prompt + code  # for static analysis
                elif test_code and entry_point:
                    full_code = code + "\n" + test_code + f"\ncheck({entry_point})\n"
                    static_code = code
                else:
                    full_code = code
                    static_code = code
                runnable = full_code
                # HumanEval check_correctness format (needs prompt, test, entry_point)
                # MBPP evaluate_mbpp format (needs test_list)
                test_list = []
                if problem and hasattr(problem, 'test_code') and problem.test_code:
                    test_list = [line for line in problem.test_code.splitlines() if line.strip()]

                failing.append({
                    "task_id": pid,
                    "source": rec["source"],
                    "bug_type": rec.get("bug_type", "unknown"),
                    "code": static_code,    # prompt+body (for static analysis)
                    "runnable": runnable,   # prompt+body+tests (for execution)
                    "error": rec.get("error", ""),
                    # Fields needed by evaluate_solution
                    "prompt": prompt,         # function signature + docstring
                    "test": test_code,        # HumanEval test code
                    "entry_point": entry_point,
                    "test_list": test_list,   # MBPP test assertions
                })

    print(f"Loaded {len(failing)} failing solutions from H-M1")
    return failing
