"""Worker for evaluating single problems."""
import subprocess
import time
import tempfile
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, List
from pathlib import Path


@dataclass
class ProverResult:
    """Single problem result."""
    problem_id: str
    source: str
    outcome: str
    time_s: float
    tactic_count: Optional[int]
    trace_log: Optional[str]


def create_lean_script(problem_id: str, statement: str) -> str:
    """Generate Lean script."""
    return f"""import Minif2f.Test
import Auto

set_option auto.smt false
set_option auto.tptp false
set_option auto.native true
set_option trace.auto true
set_option trace.auto.mono true

-- Target theorem: {problem_id}
example : {statement} := by
  auto
"""


def extract_tactic_count(trace_log: Optional[str]) -> Optional[int]:
    """Count tactic evaluations from trace.auto logs."""
    if not trace_log:
        return None

    import re
    matches = re.findall(r'\[auto\.native\] Invoking', trace_log)
    if matches:
        return len(matches)

    mono_steps = re.findall(r'\[auto\.mono\] Instantiating', trace_log)
    return len(mono_steps) if mono_steps else None


def evaluate_single_problem(problem, timeout: int = 300, retry: int = 3) -> ProverResult:
    """Run lean-auto on problem."""
    from loader import Problem

    for attempt in range(retry):
        start = time.time()

        script = create_lean_script(problem.id, problem.statement)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(script)
            temp_path = f.name

        try:
            proc = subprocess.run(
                ['lean', temp_path],
                timeout=timeout,
                capture_output=True,
                text=True
            )

            elapsed = time.time() - start
            trace_log = proc.stderr

            if proc.returncode == 0:
                return ProverResult(
                    problem_id=problem.id,
                    source=problem.source,
                    outcome='solved',
                    time_s=elapsed,
                    tactic_count=extract_tactic_count(trace_log),
                    trace_log=trace_log
                )
            else:
                return ProverResult(
                    problem_id=problem.id,
                    source=problem.source,
                    outcome='error',
                    time_s=elapsed,
                    tactic_count=None,
                    trace_log=trace_log
                )

        except subprocess.TimeoutExpired as e:
            return ProverResult(
                problem_id=problem.id,
                source=problem.source,
                outcome='timeout',
                time_s=timeout,
                tactic_count=None,
                trace_log=e.stderr.decode() if e.stderr else None
            )

        except Exception as exc:
            if attempt == retry - 1:
                return ProverResult(
                    problem_id=problem.id,
                    source=problem.source,
                    outcome='error',
                    time_s=time.time() - start,
                    tactic_count=None,
                    trace_log=str(exc)
                )
            time.sleep(5)

        finally:
            os.unlink(temp_path)

    return ProverResult(
        problem_id=problem.id,
        source=problem.source,
        outcome='error',
        time_s=0.0,
        tactic_count=None,
        trace_log='All retries failed'
    )


def save_checkpoint(worker_id: int, results: List[ProverResult], checkpoint_dir: str) -> None:
    """Save progress checkpoint."""
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    checkpoint_path = Path(checkpoint_dir) / f'worker_{worker_id}.json'

    data = {
        'worker_id': worker_id,
        'problems_completed': len(results),
        'results': [asdict(r) for r in results]
    }

    with open(checkpoint_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_checkpoint(worker_id: int, checkpoint_dir: str) -> List[ProverResult]:
    """Load checkpoint."""
    checkpoint_path = Path(checkpoint_dir) / f'worker_{worker_id}.json'

    if not checkpoint_path.exists():
        return []

    with open(checkpoint_path, 'r') as f:
        data = json.load(f)

    return [ProverResult(**r) for r in data['results']]


def worker_with_checkpoint(args):
    """Process problems with checkpointing."""
    problems, worker_id, checkpoint_dir, checkpoint_freq = args

    results = load_checkpoint(worker_id, checkpoint_dir)
    completed_ids = {r.problem_id for r in results}

    for i, problem in enumerate(problems):
        if problem.id in completed_ids:
            continue

        result = evaluate_single_problem(problem)
        results.append(result)

        if (i + 1) % checkpoint_freq == 0:
            save_checkpoint(worker_id, results, checkpoint_dir)

    save_checkpoint(worker_id, results, checkpoint_dir)
    return results


def run_parallel_evaluation(problems: List, n_workers: int = 8, checkpoint_dir: str = './data/checkpoints', checkpoint_freq: int = 10) -> List[ProverResult]:
    """Run evaluation on worker pool."""
    from multiprocessing import Pool

    chunk_size = (len(problems) + n_workers - 1) // n_workers
    chunks = [problems[i:i + chunk_size] for i in range(0, len(problems), chunk_size)]

    args = [(chunk, i, checkpoint_dir, checkpoint_freq) for i, chunk in enumerate(chunks)]

    with Pool(n_workers) as pool:
        all_results = pool.map(worker_with_checkpoint, args)

    return [r for worker_results in all_results for r in worker_results]
