import pandas as pd
from sa_tools import run_pylint, run_mypy, run_radon

def compute_loc(code: str) -> int:
    return len([l for l in code.splitlines() if l.strip()])

def build_dataframe(problems, completions, passed: dict[str, bool]) -> pd.DataFrame:
    comp_map = {c.task_id: c.completion for c in completions}
    rows = []
    for p in problems:
        if p.task_id not in comp_map:
            continue
        code = comp_map[p.task_id]
        pylint_r = run_pylint(code)
        mypy_r = run_mypy(code)
        radon_r = run_radon(code)
        rows.append({
            "task_id": p.task_id,
            "passed": int(passed.get(p.task_id, False)),
            "pylint_score": pylint_r.metric if pylint_r.success else 5.0,
            "mypy_errors": mypy_r.metric if mypy_r.success else 0,
            "radon_cc": radon_r.metric if radon_r.success else 1.0,
            "loc": compute_loc(code),
        })
    return pd.DataFrame(rows)
