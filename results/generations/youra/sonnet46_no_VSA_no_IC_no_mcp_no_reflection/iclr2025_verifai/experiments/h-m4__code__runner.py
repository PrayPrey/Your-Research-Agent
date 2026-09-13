"""H-M4 experiment runner: 538 × 4 = 2,152 repair loop runs with checkpoint/resume."""
import json
import time
from pathlib import Path
from tqdm import tqdm

from evaluator import TimedFeedbackEvaluator


def load_checkpoint(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def save_checkpoint(results: list[dict], path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(p) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(results, f, indent=2)
    Path(tmp).rename(p)


def get_completed_keys(results: list[dict]) -> set[tuple[str, str]]:
    return {(r["task_id"], r["category"]) for r in results}


def _generate_initial_code(problem: dict, llm_client) -> str:
    prompt = (
        f"Write a Python function for the following problem. "
        f"Return ONLY the function code, no explanation.\n\n"
        f"Problem:\n{problem['prompt']}"
    )
    try:
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
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
    except Exception as e:
        return f"# Generation failed: {e}\ndef solution(): pass"


def run_experiment(
    problems: list[dict],
    categories: list[str],
    checkpoint_path: str,
    baseline_pass: dict[str, bool],
    llm_client,
    verifier_fns: dict,
    max_iters: int = 3,
) -> list[dict]:
    results = load_checkpoint(checkpoint_path)
    completed = get_completed_keys(results)

    # Cache initial codes to avoid re-generating per category
    initial_codes: dict[str, str] = {}

    total = len(problems) * len(categories)
    done = len(completed)
    print(f"Resuming: {done}/{total} already done")

    pbar = tqdm(total=total, initial=done, desc="H-M4 runs")

    for problem in problems:
        task_id = problem["task_id"]

        # Generate initial code once per problem (shared across categories)
        if task_id not in initial_codes:
            initial_codes[task_id] = _generate_initial_code(problem, llm_client)

        initial_code = initial_codes[task_id]

        for cat in categories:
            key = (task_id, cat)
            if key in completed:
                continue

            evaluator = TimedFeedbackEvaluator(cat, verifier_fns[cat], llm_client)
            final_pass, total_overhead_s, per_iter_times = evaluator.run_repair_loop(
                problem, initial_code, max_iters=max_iters
            )

            result = {
                "task_id": task_id,
                "category": cat,
                "source": problem["source"],
                "initial_pass": bool(baseline_pass.get(task_id, False)),
                "final_pass": bool(final_pass),
                "total_overhead_s": total_overhead_s,
                "per_iter_times": per_iter_times,
                "n_iters": len(per_iter_times),
                "timeout_hit": total_overhead_s >= 29.0 and cat == "smt",
            }
            results.append(result)
            completed.add(key)

            print(f"[H-M4] Category={cat} problem={task_id} "
                  f"overhead={total_overhead_s:.3f}s pass={final_pass}")

            save_checkpoint(results, checkpoint_path)
            pbar.update(1)

    pbar.close()
    return results
