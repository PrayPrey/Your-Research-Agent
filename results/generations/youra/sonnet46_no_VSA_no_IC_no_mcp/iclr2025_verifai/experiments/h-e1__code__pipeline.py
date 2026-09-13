"""H-E1 pipeline: generate → evaluate → mypy-analyze → aggregate."""

import json
import logging
import pathlib
import re
import subprocess
import tempfile
import time
from typing import Optional

from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SEEDS = [42, 123, 456]
BENCHMARKS = {"mbpp+": "get_mbpp_plus", "humaneval+": "get_human_eval_plus"}
MYPY_FLAGS = ["--ignore-missing-imports", "--no-strict-optional"]
MYPY_TIMEOUT = 30
RESULTS_DIR = pathlib.Path("docs/youra_research/h-e1/results")

# Cached expected outputs (loaded once per process)
_EXPECTED_OUTPUTS: dict = {}


def _get_expected_outputs(benchmark: str) -> dict:
    """Load and cache evalplus expected outputs for a benchmark."""
    if benchmark not in _EXPECTED_OUTPUTS:
        from evalplus.evaluate import get_groundtruth
        if benchmark == "mbpp+":
            from evalplus.data import get_mbpp_plus, get_mbpp_plus_hash
            from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
            problems = get_mbpp_plus()
            hashcode = get_mbpp_plus_hash()
            _EXPECTED_OUTPUTS[benchmark] = get_groundtruth(problems, hashcode, MBPP_OUTPUT_NOT_NONE_TASKS)
        elif benchmark == "humaneval+":
            from evalplus.data import get_human_eval_plus, get_human_eval_plus_hash
            problems = get_human_eval_plus()
            hashcode = get_human_eval_plus_hash()
            _EXPECTED_OUTPUTS[benchmark] = get_groundtruth(problems, hashcode, set())
    return _EXPECTED_OUTPUTS[benchmark]

MYPY_CATEGORIES = {
    "name-error": r"\[name-defined\]",
    "type-error": r"\[arg-type\]|\[assignment\]|\[operator\]",
    "return-value": r"\[return-value\]",
    "attribute-error": r"\[attr-defined\]",
}


def load_problems(benchmark: str) -> dict:
    """Load problems for a benchmark via evalplus API."""
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    if benchmark == "mbpp+":
        return get_mbpp_plus()
    elif benchmark == "humaneval+":
        return get_human_eval_plus()
    else:
        raise ValueError(f"Unknown benchmark: {benchmark}")


def build_prompt(problem: dict) -> str:
    """Build function completion prompt from problem dict."""
    prompt = problem.get("prompt", "")
    return (
        "Complete the following Python function. "
        "Return ONLY the complete Python function implementation, no explanation.\n\n"
        f"{prompt}"
    )


def extract_code(response_text: str) -> str:
    """Strip markdown fences, return raw Python code."""
    # Remove ```python ... ``` or ``` ... ```
    match = re.search(r"```(?:python)?\n(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()


def generate_solution(client: OpenAI, problem: dict, seed: int, max_retries: int = 3) -> str:
    """Generate single solution via GPT-4o-mini with exponential backoff."""
    prompt = build_prompt(problem)
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                seed=seed,
                max_tokens=1024,
            )
            return extract_code(response.choices[0].message.content)
        except Exception as e:
            wait = 2 ** attempt
            logger.warning(f"Generation attempt {attempt + 1} failed: {e}. Waiting {wait}s.")
            time.sleep(wait)
    logger.error("All generation attempts failed, returning empty string.")
    return ""


def evaluate_solution(task_id: str, code: str, problem: dict) -> bool:
    """Run EvalPlus test suite on code; return True if all tests pass."""
    try:
        from evalplus.evaluate import check_correctness
        dataset = "mbpp" if task_id.startswith("Mbpp") else "humaneval"
        benchmark = "mbpp+" if dataset == "mbpp" else "humaneval+"
        expected_outputs = _get_expected_outputs(benchmark)
        expected_output = expected_outputs.get(task_id)
        if expected_output is None:
            logger.warning(f"No expected output for {task_id}, treating as FAIL")
            return False
        result = check_correctness(
            dataset=dataset,
            completion_id=0,
            problem=problem,
            solution=code,
            expected_output=expected_output,
            fast_check=False,
            identifier=task_id,
            min_time_limit=1.0,
            gt_time_limit_factor=3.0,
        )
        # result["base"][0] == "pass" means all base tests pass
        # result["plus"][0] == "pass" means all plus tests pass
        base_pass = result.get("base", ("failed",))[0] == "pass"
        plus_pass = result.get("plus", ("failed",))[0] == "pass"
        return base_pass and plus_pass
    except ImportError:
        raise RuntimeError("evalplus.evaluate.check_correctness unavailable")
    except Exception as e:
        logger.warning(f"evaluate_solution {task_id} exception: {e}")
        return False


def extract_error_categories(mypy_stdout: str) -> dict:
    """Parse mypy output for error category counts."""
    counts = {cat: 0 for cat in MYPY_CATEGORIES}
    for line in mypy_stdout.splitlines():
        if "error:" not in line:
            continue
        for cat, pattern in MYPY_CATEGORIES.items():
            if re.search(pattern, line):
                counts[cat] += 1
    return counts


def run_mypy(code: str) -> tuple:
    """Write code to tempfile, run mypy, return (has_error, error_count, categories, stdout).

    Timeout or FileNotFoundError handling:
    - FileNotFoundError: re-raised (caller exits with install instructions)
    - TimeoutExpired: returns (False, 0, {}, '')  — conservative, no false positives
    """
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp = f.name

        result = subprocess.run(
            ["mypy", *MYPY_FLAGS, tmp],
            capture_output=True,
            text=True,
            timeout=MYPY_TIMEOUT,
        )

        error_count = sum(1 for line in result.stdout.splitlines() if "error:" in line)
        has_error = result.returncode != 0
        categories = extract_error_categories(result.stdout)
        return (has_error, error_count, categories, result.stdout)

    except FileNotFoundError:
        raise

    except subprocess.TimeoutExpired:
        logger.warning("mypy timeout on temp file")
        return (False, 0, {cat: 0 for cat in MYPY_CATEGORIES}, "")

    finally:
        if tmp:
            pathlib.Path(tmp).unlink(missing_ok=True)


def run_benchmark(client: OpenAI, benchmark: str, seed: int) -> list:
    """Run full benchmark × seed, returning list of result dicts for failing solutions."""
    problems = load_problems(benchmark)
    results = []
    total = len(problems)
    logger.info(f"Starting {benchmark} seed={seed} ({total} problems)")

    for i, (task_id, problem) in enumerate(problems.items()):
        if i % 50 == 0:
            logger.info(f"  {benchmark} seed={seed}: {i}/{total}")

        code = generate_solution(client, problem, seed)
        if not code:
            logger.warning(f"  Skipping {task_id}: empty generation")
            continue

        passed = evaluate_solution(task_id, code, problem)

        if not passed:
            has_error, error_count, categories, mypy_stdout = run_mypy(code)
            results.append({
                "task_id": task_id,
                "seed": seed,
                "benchmark": benchmark,
                "passed": passed,
                "has_mypy_error": has_error,
                "error_count": error_count,
                "error_categories": categories,
            })
            logger.debug(
                f"  mypy analysis: {error_count} errors in {task_id} "
                f"(has_mypy_error={has_error})"
            )

    logger.info(f"Finished {benchmark} seed={seed}: {len(results)} failing solutions analyzed")
    return results


def aggregate(results: list) -> dict:
    """Aggregate results: per benchmark per seed fraction + mean/std across seeds."""
    import statistics

    benchmarks = list(set(r["benchmark"] for r in results))
    seeds_found = sorted(set(r["seed"] for r in results))

    summary = {}
    for bm in benchmarks:
        bm_results = [r for r in results if r["benchmark"] == bm]
        fractions_per_seed = []
        per_seed = {}

        for seed in seeds_found:
            seed_results = [r for r in bm_results if r["seed"] == seed]
            if not seed_results:
                continue
            fraction = sum(1 for r in seed_results if r["has_mypy_error"]) / len(seed_results)
            fractions_per_seed.append(fraction)
            per_seed[str(seed)] = {
                "fraction": fraction,
                "failing_count": len(seed_results),
                "with_mypy_error": sum(1 for r in seed_results if r["has_mypy_error"]),
            }

        mean = statistics.mean(fractions_per_seed) if fractions_per_seed else 0.0
        std = statistics.stdev(fractions_per_seed) if len(fractions_per_seed) > 1 else 0.0

        summary[bm] = {
            "type_error_fraction_mean": mean,
            "type_error_fraction_std": std,
            "per_seed": per_seed,
            "total_failing": len(bm_results),
            "total_with_mypy_error": sum(1 for r in bm_results if r["has_mypy_error"]),
        }

    return summary


def verify_mechanism_activated(results: list) -> tuple:
    """Verify mypy analysis pipeline actually ran and found errors."""
    analyzed = [r for r in results if "has_mypy_error" in r]
    any_errors_found = any(r["has_mypy_error"] for r in analyzed)
    indicators = {
        "mypy_ran": len(analyzed) > 0,
        "errors_found": any_errors_found,
        "fraction_computed": len(analyzed) > 0,
        "sample_size_sufficient": len(analyzed) >= 50,
    }
    activated = indicators["mypy_ran"] and indicators["errors_found"]
    return activated, indicators


def save_results(results: list, summary: dict) -> None:
    """Write JSONL per benchmark/seed + summary.json to RESULTS_DIR."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Write full results JSONL
    results_path = RESULTS_DIR / "results.jsonl"
    with open(results_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    # Write summary JSON
    summary_path = RESULTS_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Results saved: {results_path} ({len(results)} records)")
    logger.info(f"Summary saved: {summary_path}")
