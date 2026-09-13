"""Feedback generation and perturbation for H-M2 DiD experiment."""
import re
import random
import subprocess
import tempfile


def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]:
    """Execute code against tests. Returns (pass_rate, error_msg)."""
    if not tests:
        return 0.0, "No tests provided"

    passed = 0
    error_msg = ""

    for test in tests:
        full_code = f"{code}\n\n{test}"
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(full_code)
                f.flush()
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    passed += 1
                else:
                    error_msg = result.stderr[:500] if result.stderr else "Test failed"
        except subprocess.TimeoutExpired:
            error_msg = "Timeout"
        except Exception as e:
            error_msg = str(e)[:500]

    return passed / len(tests), error_msg


def classify_error_type(error_msg: str) -> str:
    """Classify error by first exception type found."""
    if not error_msg:
        return "Other"
    if "Timeout" in error_msg:
        return "Timeout"
    match = re.search(r"(\w+Error)", error_msg)
    if match:
        return match.group(1)
    return "Other"


def build_tests(problem: dict) -> list[str]:
    """Extract test function and wrap for execution."""
    test_code = problem.get("test", "")
    entry_point = problem.get("entry_point", "solution")
    if not test_code:
        return []
    full_test = f"{test_code}\ncheck({entry_point})"
    return [full_test]


def get_control_feedback(
    task_id: str,
    feedback_bank: dict[str, dict],
    seed: int,
) -> str:
    """Pick donor feedback from different problem, matched by error type and length."""
    actual = feedback_bank.get(task_id)
    if not actual or actual["pass_rate"] == 1.0:
        return ""

    actual_type = actual["error_type"]
    actual_len = len(actual["error_msg"])

    same_type = [
        (tid, fb) for tid, fb in feedback_bank.items()
        if tid != task_id and fb["pass_rate"] < 1.0 and fb["error_type"] == actual_type
    ]
    len_matched = [
        (tid, fb) for tid, fb in same_type
        if abs(len(fb["error_msg"]) - actual_len) <= 0.2 * actual_len
    ]
    pool = len_matched if len_matched else same_type
    if not pool:
        pool = [(tid, fb) for tid, fb in feedback_bank.items() if tid != task_id and fb["pass_rate"] < 1.0]

    if not pool:
        return actual["error_msg"]

    rng = random.Random(seed + hash(task_id) % 10_000)
    _, donor = rng.choice(pool)
    return donor["error_msg"]
