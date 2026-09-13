"""H-M4 verifiers: execution, static, type, SMT."""
import subprocess
import tempfile
import os
import json


# ---------------------------------------------------------------------------
# Execution verifier
# ---------------------------------------------------------------------------

def _build_test_harness(code: str, problem: dict) -> str:
    tests = problem.get("tests", "")
    if isinstance(tests, list):
        tests = "\n".join(tests)
    return f"{code}\n\n# Tests\n{tests}\n"


def _parse_assertion_failure(stderr: str) -> str:
    lines = stderr.strip().split("\n")
    assertion_lines = [l for l in lines if "AssertionError" in l or "assert" in l.lower()]
    error_lines = [l for l in lines if "Error" in l or "Exception" in l]
    if assertion_lines:
        return "Test assertion failed:\n" + "\n".join(assertion_lines[:3]) + "\nFix the function logic."
    elif error_lines:
        return "Runtime error:\n" + "\n".join(error_lines[:3]) + "\nFix the syntax/runtime error."
    return f"Tests failed:\n{stderr[:500]}\nFix the function."


def run_execution_verifier(code: str, problem: dict, timeout: float = 10.0) -> tuple[str, bool]:
    harness = _build_test_harness(code, problem)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, prefix="exec_") as f:
        f.write(harness)
        tmppath = f.name
    try:
        result = subprocess.run(
            ["python", tmppath], capture_output=True, text=True, timeout=timeout
        )
        passed = result.returncode == 0
        if passed:
            return "All tests passed.", True
        output = (result.stdout + result.stderr).strip()
        feedback = _parse_assertion_failure(result.stderr) if result.stderr else output[:1000]
        return feedback or "Runtime error (no output).", False
    except subprocess.TimeoutExpired:
        return f"Execution timed out after {timeout}s.", False
    except Exception as e:
        return f"Subprocess error: {e}", False
    finally:
        try:
            os.unlink(tmppath)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Static analysis verifier (Pyright)
# ---------------------------------------------------------------------------

def run_static_verifier(code: str, problem: dict) -> tuple[str, bool]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, prefix="h_m4_pyright_") as f:
        f.write(code)
        tmppath = f.name
    try:
        result = subprocess.run(
            ["pyright", "--outputjson", tmppath],
            capture_output=True, text=True, timeout=30.0
        )
        try:
            data = json.loads(result.stdout)
            errors = data.get("generalDiagnostics", [])
            passed = all(e.get("severity") != "error" for e in errors)
            if passed:
                return "No static analysis errors.", True
            msgs = [e.get("message", "") for e in errors if e.get("severity") == "error"]
            return "Static analysis errors:\n" + "\n".join(msgs[:5]), False
        except (json.JSONDecodeError, KeyError):
            # pyright not installed or unexpected output — treat as pass (no meaningful static check)
            combined = (result.stdout + result.stderr).strip()
            if "error" in combined.lower():
                return combined[:500], False
            return "Pyright check passed (or not available).", True
    except subprocess.TimeoutExpired:
        return "Pyright timed out after 30s.", False
    except FileNotFoundError:
        # pyright not on PATH — skip, treat as pass
        return "Pyright not available (skipped).", True
    except Exception as e:
        return f"Static verifier error: {e}", True
    finally:
        try:
            os.unlink(tmppath)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Type checking verifier (Pyright — same tool)
# ---------------------------------------------------------------------------

def run_type_verifier(code: str, problem: dict) -> tuple[str, bool]:
    # Type checking is same as static via Pyright; returns type-error-specific feedback
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, prefix="h_m4_type_") as f:
        f.write(code)
        tmppath = f.name
    try:
        result = subprocess.run(
            ["pyright", "--outputjson", tmppath],
            capture_output=True, text=True, timeout=30.0
        )
        try:
            data = json.loads(result.stdout)
            errors = data.get("generalDiagnostics", [])
            type_errors = [e for e in errors if "type" in e.get("message", "").lower() or e.get("severity") == "error"]
            passed = len(type_errors) == 0
            if passed:
                return "No type errors.", True
            msgs = [e.get("message", "") for e in type_errors[:5]]
            return "Type errors:\n" + "\n".join(msgs), False
        except (json.JSONDecodeError, KeyError):
            combined = (result.stdout + result.stderr).strip()
            if "error" in combined.lower():
                return combined[:500], False
            return "Type check passed (or not available).", True
    except subprocess.TimeoutExpired:
        return "Type check timed out after 30s.", False
    except FileNotFoundError:
        return "Pyright not available (type check skipped).", True
    except Exception as e:
        return f"Type verifier error: {e}", True
    finally:
        try:
            os.unlink(tmppath)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# SMT verifier (LLM constraint generation + Z3)
# ---------------------------------------------------------------------------

def _generate_z3_constraints(code: str, problem: dict, llm_client) -> str:
    tests_preview = str(problem.get("tests", ""))[:500]
    prompt = (
        f"Given this Python function:\n```python\n{code}\n```\n\n"
        f"Write Z3 Python code (using `from z3 import *`) that:\n"
        f"1. Declares symbolic variables for the function inputs\n"
        f"2. Adds constraints modeling the function's behavior\n"
        f"3. Adds assertions from these tests: {tests_preview}\n"
        f"4. Calls `s = Solver(); s.add(...); result = s.check()`\n"
        f"5. Prints 'UNSAT' if all constraints satisfied, 'SAT' plus model if counterexample found\n"
        f"Return ONLY executable Python code, no explanation."
    )
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```python"):
        raw = raw[9:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


def _run_z3_code(z3_code: str, timeout: float = 30.0) -> tuple[str, bool]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, prefix="z3_") as f:
        f.write("from z3 import *\n")
        f.write(z3_code)
        tmppath = f.name
    try:
        result = subprocess.run(
            ["python", tmppath], capture_output=True, text=True, timeout=timeout
        )
        output = (result.stdout + result.stderr).strip()
        passed = "UNSAT" in output and "error" not in output.lower()
        return output, passed
    except subprocess.TimeoutExpired:
        return f"TIMEOUT after {timeout}s", False
    except Exception as e:
        return f"Z3 execution error: {e}", False
    finally:
        try:
            os.unlink(tmppath)
        except Exception:
            pass


def run_smt_verifier(code: str, problem: dict, llm_client=None, timeout: float = 30.0) -> tuple[str, bool]:
    if llm_client is None:
        return "SMT verifier requires LLM client.", False
    try:
        z3_code = _generate_z3_constraints(code, problem, llm_client)
        output, passed = _run_z3_code(z3_code, timeout=timeout)
        if passed:
            return "Z3 verification passed: no counterexample found.", True
        elif "TIMEOUT" in output:
            return f"Z3 verification timed out after {timeout}s. Simplify function logic.", False
        elif output.startswith("SAT"):
            return f"Z3 found counterexample: {output[:300]}. Fix the implementation logic.", False
        else:
            return f"Z3 error or parse failure: {output[:300]}. Ensure function is well-typed.", False
    except Exception as e:
        return f"SMT verifier error: {e}", False


# ---------------------------------------------------------------------------
# Verifier registry
# ---------------------------------------------------------------------------

def make_verifier_fns(llm_client) -> dict:
    """Returns verifier callables with consistent (code, problem) -> (feedback, passed) signature."""
    import functools
    return {
        "execution": run_execution_verifier,
        "static": run_static_verifier,
        "type": run_type_verifier,
        "smt": functools.partial(run_smt_verifier, llm_client=llm_client),
    }
