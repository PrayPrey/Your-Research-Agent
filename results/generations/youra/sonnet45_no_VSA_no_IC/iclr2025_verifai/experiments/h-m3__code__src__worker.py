"""Worker for evaluating single problems with random Mathlib tactics."""
import subprocess
import time
import tempfile
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, List
from pathlib import Path
from random_sampler import TacticSampler, sample_with_goal_selection


@dataclass
class ProverResult:
    """Single problem result."""
    problem_id: str
    source: str
    outcome: str
    time_s: float
    tactics_used: int
    tactic_sequence: List[str]
    seed: int
    error_msg: Optional[str] = None


def evaluate_single_problem(
    problem_data,
    sampler: TacticSampler,
    budget: int = 15,
    timeout: int = 300
) -> ProverResult:
    """Run random Mathlib tactic sampler on problem."""

    problem, problem_idx = problem_data  # Unpack tuple
    seed = problem_idx  # Deterministic seeding
    start = time.time()

    # Generate random tactic script
    script, tactics = sample_with_goal_selection(
        problem.id,
        problem.statement,
        budget,
        seed,
        sampler
    )

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

        if proc.returncode == 0:
            outcome = 'solved'
            error_msg = None
        elif elapsed >= timeout - 1:
            outcome = 'timeout'
            error_msg = None
        else:
            outcome = 'budget_exhausted'
            error_msg = proc.stderr[:200] if proc.stderr else None

        return ProverResult(
            problem_id=problem.id,
            source=problem.source,
            outcome=outcome,
            time_s=elapsed,
            tactics_used=budget if outcome != 'solved' else len(tactics),
            tactic_sequence=tactics,
            seed=seed,
            error_msg=error_msg
        )

    except subprocess.TimeoutExpired:
        return ProverResult(
            problem_id=problem.id,
            source=problem.source,
            outcome='timeout',
            time_s=timeout,
            tactics_used=0,
            tactic_sequence=tactics,
            seed=seed,
            error_msg='Subprocess timeout'
        )

    except Exception as exc:
        return ProverResult(
            problem_id=problem.id,
            source=problem.source,
            outcome='error',
            time_s=time.time() - start,
            tactics_used=0,
            tactic_sequence=tactics,
            seed=seed,
            error_msg=str(exc)[:200]
        )

    finally:
        os.unlink(temp_path)


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
