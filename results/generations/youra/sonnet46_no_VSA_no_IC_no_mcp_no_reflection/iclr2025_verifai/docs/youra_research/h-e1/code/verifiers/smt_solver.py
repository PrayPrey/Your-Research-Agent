import os
import re
import random
import time
import threading
from typing import List
from verifiers import VerifierResult


def _run_z3_with_timeout(z3_code: str, timeout: float):
    """Execute Z3 code in restricted namespace with timeout. Returns (outcome_str, error)."""
    import z3
    ns = {}
    ns.update({k: getattr(z3, k) for k in dir(z3) if not k.startswith("__")})
    ns["__builtins__"] = {"print": print, "range": range, "len": len, "list": list, "int": int, "float": float, "str": str, "bool": bool}

    result_holder = [None, None]  # [outcome, error]

    def _exec():
        try:
            exec(z3_code, ns)
            result_holder[0] = str(ns.get("result", "unknown"))
        except Exception as e:
            result_holder[1] = str(e)

    t = threading.Thread(target=_exec, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return "timeout", None
    return result_holder[0], result_holder[1]


def _get_z3_code(client, prompt: str) -> str:
    system_msg = (
        "Generate Z3 Python code that encodes the constraints of this problem. "
        "Use the z3 library. End with `result = s.check()` where s is a Solver instance."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=512,
    )
    code = resp.choices[0].message.content or ""
    # Strip markdown fences
    code = re.sub(r"```python|```", "", code).strip()
    return code


def run(prompt: str, completion: str, timeout: float = 10.0) -> VerifierResult:
    import openai
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    start = time.time()

    try:
        z3_code = _get_z3_code(client, prompt)
    except Exception as e:
        return VerifierResult(activated=False, signal=f"LLM_ERROR: {e}", latency_ms=(time.time() - start) * 1000)

    if not z3_code:
        return VerifierResult(activated=False, signal="NO_Z3_CODE", latency_ms=(time.time() - start) * 1000)

    outcome, error = _run_z3_with_timeout(z3_code, timeout)
    if error:
        return VerifierResult(activated=False, signal=f"EXEC_ERROR: {error}", latency_ms=(time.time() - start) * 1000)

    activated = outcome == "sat"
    return VerifierResult(activated=activated, signal=outcome or "unknown", latency_ms=(time.time() - start) * 1000)


def run_pilot(problems: list, completions: dict, n: int = 20, seed: int = 1) -> dict:
    import openai
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    random.seed(seed)
    sample_size = min(n, len(problems))
    pilot = random.sample(problems, sample_size)

    sat_count = 0
    pilot_results = []

    for problem in pilot:
        pid = problem.problem_id
        try:
            result = run(problem.prompt, completions.get(pid, ""), timeout=10.0)
            outcome = result.signal if result.signal else "unknown"
            sat_count += int(result.activated)
        except Exception as e:
            outcome = "error"
            result = VerifierResult(activated=False, signal=f"ERROR: {e}", latency_ms=0.0)

        pilot_results.append({"problem_id": pid, "outcome": outcome, "signal": result.signal})

    sat_rate = sat_count / sample_size if sample_size > 0 else 0.0
    return {
        "sat_count": sat_count,
        "total": sample_size,
        "sat_rate": sat_rate,
        "passed_gate": sat_rate >= 0.30,
        "pilot_results": pilot_results,
    }
