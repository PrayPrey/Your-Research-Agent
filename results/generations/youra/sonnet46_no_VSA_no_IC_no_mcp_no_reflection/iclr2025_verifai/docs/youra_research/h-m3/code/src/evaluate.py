"""Solution evaluation for HumanEval and MBPP formats."""
import re
import threading


def strip_markdown_fences(code: str) -> str:
    """Remove ```python ... ``` fences from LLM output."""
    if "```" not in code:
        return code.strip()
    m = re.search(r"```(?:python)?\n?(.*?)```", code, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: remove first and last ``` lines
    lines = code.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("```")), 0)
    end = next((i for i, l in enumerate(lines[start+1:], start+1) if l.strip() == "```"), len(lines))
    return "\n".join(lines[start+1:end]).strip()


def evaluate_mbpp(solution_code: str, problem: dict) -> bool:
    """MBPP evaluation: exec solution + assert test_list."""
    test_list = problem.get("test_list", [])
    if not test_list:
        return False
    full_code = solution_code + "\n" + "\n".join(test_list)
    result = [False]

    def _run():
        try:
            exec(compile(full_code, "<mbpp>", "exec"), {})
            result[0] = True
        except Exception:
            result[0] = False

    t = threading.Thread(target=_run)
    t.start()
    t.join(timeout=5.0)
    return result[0]


def evaluate_solution(solution_code: str, problem: dict) -> bool:
    """Test if solution passes all problem test cases.

    Supports HumanEval (check_correctness) and MBPP (exec test_list).
    """
    if not solution_code or not solution_code.strip():
        return False

    code = strip_markdown_fences(solution_code)

    if "entry_point" in problem:
        # HumanEval format
        try:
            from human_eval.execution import check_correctness
            result = check_correctness(problem, code, timeout=5.0)
            return result.get("passed", False)
        except Exception:
            return False
    else:
        # MBPP format
        return evaluate_mbpp(code, problem)
