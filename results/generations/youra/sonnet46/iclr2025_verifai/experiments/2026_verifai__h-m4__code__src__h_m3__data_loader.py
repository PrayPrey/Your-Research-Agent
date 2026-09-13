"""data_loader.py — tier CSV, solutions JSONL, EvalPlus problems, pair iterator."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from h_m3.config import MODEL_SHORT_NAMES

logger = logging.getLogger(__name__)


def load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame:
    """Load tier_assignments.csv; returns DataFrame[problem_id, model, tier, pass_at_1].

    Supports both long format (problem_id, model, tier, pass_at_1) and wide format
    (task_id, llama3_tier, codellama_tier, deepseek_tier) from h-m2 output.
    """
    path = Path(hm2_results_dir) / "tier_assignments.csv"
    if not path.exists():
        raise FileNotFoundError(f"tier_assignments.csv not found: {path}")
    df = pd.read_csv(path)

    # Check if already long format
    if {"problem_id", "model", "tier", "pass_at_1"}.issubset(set(df.columns)):
        logger.info(f"Loaded {len(df)} rows from tier_assignments.csv (long format)")
        return df

    # Wide format from h-m2: task_id, benchmark, llama3_tier, codellama_tier, deepseek_tier
    # Map tier column names to model short names
    tier_col_to_short = {
        "llama3_tier": "llama3_8b",
        "codellama_tier": "codellama_7b",
        "deepseek_tier": "deepseek_6.7b",
    }
    # Map model short names to full model IDs
    short_to_model_id = {v: k for k, v in MODEL_SHORT_NAMES.items()}

    tier_cols = [c for c in tier_col_to_short if c in df.columns]
    if not tier_cols:
        raise ValueError(f"tier_assignments.csv missing columns: expected long or wide format, got {list(df.columns)}")

    rows = []
    for _, row in df.iterrows():
        task_id = row["task_id"]
        for tier_col in tier_cols:
            model_short = tier_col_to_short[tier_col]
            model_id = short_to_model_id.get(model_short, model_short)
            tier = row[tier_col]
            rows.append({
                "problem_id": task_id,
                "model": model_id,
                "model_short": model_short,
                "tier": tier,
                "pass_at_1": 0.0,  # will be filled from solutions data
            })

    result = pd.DataFrame(rows)
    logger.info(f"Loaded {len(result)} rows from tier_assignments.csv (wide format, melted)")
    return result


def filter_hard_easy_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Filter rows where tier in {hard, easy}."""
    filtered = df[df["tier"].isin({"hard", "easy"})].copy()
    logger.info(
        f"Filtered to hard+easy: {len(filtered)} rows "
        f"(hard={len(filtered[filtered['tier']=='hard'])}, "
        f"easy={len(filtered[filtered['tier']=='easy'])})"
    )
    return filtered


def load_solutions_jsonl(hm1_results_dir: Path, model_short: str) -> dict[str, list[dict]]:
    """Load solutions_{model_short}.jsonl; returns {task_id: [solution_dict×k]}.

    Each solution_dict: {solution: str, correctness: int, pass_at_1: float}
    """
    path = Path(hm1_results_dir) / f"solutions_{model_short}.jsonl"
    if not path.exists():
        raise FileNotFoundError(
            f"Solutions JSONL not found: {path}. "
            f"Run h-m1 to generate solution files."
        )

    # Load raw solutions (list of strings)
    raw: dict[str, list[str]] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            task_id = obj["task_id"]
            raw[task_id] = obj["solutions"]

    # Load correctness data if available
    correctness_path = Path(hm1_results_dir) / f"correctness_{model_short}.json"
    pass_at_1_path = Path(hm1_results_dir) / f"pass_at_1_{model_short}.json"

    correctness_data: dict[str, list[bool]] = {}
    if correctness_path.exists():
        correctness_data = json.load(open(correctness_path))

    pass_at_1_data: dict[str, float] = {}
    if pass_at_1_path.exists():
        pass_at_1_data = json.load(open(pass_at_1_path))

    # Build solution dict list per task
    result: dict[str, list[dict]] = {}
    for task_id, solutions_list in raw.items():
        task_correctness = correctness_data.get(task_id, [None] * len(solutions_list))
        task_pass_at_1 = pass_at_1_data.get(task_id, None)
        sol_dicts = []
        for i, sol in enumerate(solutions_list):
            correct = task_correctness[i] if i < len(task_correctness) else None
            correctness_int = int(correct) if correct is not None else 0
            sol_dicts.append({
                "solution": sol,
                "correctness": correctness_int,
                "pass_at_1": task_pass_at_1 if task_pass_at_1 is not None else 0.0,
            })
        result[task_id] = sol_dicts

    logger.info(f"Loaded solutions for {model_short}: {len(result)} tasks")
    return result


def load_evalplus_problems() -> dict[str, dict]:
    """Load HumanEval+ and MBPP+ via evalplus; returns {task_id: {prompt, ...}}."""
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    he_problems = get_human_eval_plus()
    mbpp_problems = get_mbpp_plus()
    combined = {**he_problems, **mbpp_problems}
    logger.info(f"Loaded {len(combined)} EvalPlus problems ({len(he_problems)} HE + {len(mbpp_problems)} MBPP)")
    return combined


def build_pair_iterator(
    tier_df: pd.DataFrame,
    solutions: dict[str, dict[str, list[dict]]],
    problems: dict[str, dict],
) -> list[dict]:
    """Build flat list of (model, task_id, tier, pass_at_1, solution_code, correctness, problem_prompt) dicts.

    Args:
        tier_df: DataFrame with columns [problem_id, model, tier, pass_at_1]
        solutions: {model_short: {task_id: [solution_dict×k]}}
        problems: {task_id: {prompt, ...}}

    Returns:
        Flat list of pair dicts for P(True) inference.
    """
    pairs = []
    missing_problems = 0
    missing_solutions = 0

    has_model_short_col = "model_short" in tier_df.columns

    for row in tier_df.itertuples():
        model_id = row.model
        model_short = getattr(row, "model_short", None) if has_model_short_col else None
        if model_short is None:
            model_short = MODEL_SHORT_NAMES.get(model_id)
        if model_short is None:
            logger.warning(f"Unknown model ID: {model_id}")
            continue

        task_id = row.problem_id

        # Get problem prompt
        if task_id not in problems:
            missing_problems += 1
            continue
        problem_prompt = problems[task_id]["prompt"]

        # Get solutions for this model+task
        model_solutions = solutions.get(model_short, {})
        task_sols = model_solutions.get(task_id, [])
        if not task_sols:
            missing_solutions += 1
            continue

        for sol_idx, sol_dict in enumerate(task_sols):
            pairs.append({
                "model": model_id,
                "model_short": model_short,
                "task_id": task_id,
                "sol_idx": sol_idx,
                "tier": row.tier,
                "pass_at_1": row.pass_at_1,
                "solution_code": sol_dict["solution"],
                "correctness": sol_dict["correctness"],
                "problem_prompt": problem_prompt,
            })

    if missing_problems > 0:
        logger.warning(f"Skipped {missing_problems} rows: problem not found in EvalPlus")
    if missing_solutions > 0:
        logger.warning(f"Skipped {missing_solutions} rows: no solutions found")

    logger.info(f"Built {len(pairs)} (problem, solution) pairs")
    return pairs
