import os
import subprocess
import sys
import tempfile


def _execute_code(code: str, test_list: list, timeout: float = 5.0) -> bool:
    """
    Execute code string against unit test assertions in a subprocess.
    Returns True iff all tests pass; False on any failure/timeout/error.
    """
    script = code + "\n" + "\n".join(test_list)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def make_execution_reward(timeout: float = 5.0):
    """
    Factory returning TRL GRPOTrainer-compatible reward function.
    TRL passes extra dataset columns as kwargs to reward_funcs.
    The dataset must include "test_list" as a column.
    """
    def reward_fn(
        completions: list,
        prompts: list,
        **kwargs,
    ) -> list:
        # TRL passes dataset columns (e.g. test_list) in kwargs
        test_lists = kwargs.get("test_list", [[] for _ in completions])
        rewards = []
        for code, tests in zip(completions, test_lists):
            if isinstance(tests, str):
                # datasets may serialize lists to strings in some versions
                import ast
                try:
                    tests = ast.literal_eval(tests)
                except Exception:
                    tests = [tests]
            passed = _execute_code(code, tests, timeout)
            rewards.append(1.0 if passed else 0.0)
        return rewards

    return reward_fn
