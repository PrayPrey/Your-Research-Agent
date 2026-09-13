"""H-M2: Difficulty Tier Stratification module.

Loads H-M1 pass@1 data and assigns problems to hard/easy/medium tiers per model.
"""
from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

BENCHMARK_PREFIXES: dict[str, str] = {"HumanEval/": "humaneval", "Mbpp/": "mbpp"}

HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
HE_PREFIX: str = "HumanEval/"
MBPP_PREFIX: str = "Mbpp/"
HM1_VERIFIED_FILENAME: str = "pass_at_1_hm1_verified.json"
MIN_TIER_SIZE: int = 20
COMBINED_TOTAL: int = 542
CODELLAMA_ID: str = "codellama/CodeLlama-7b-hf"


# ─── Data Loader ──────────────────────────────────────────────────────────────

def load_hm1_pass_at_1(
    hm1_results_dir: Path | str,
) -> dict[str, dict[str, float]]:
    """Load pass_at_1_hm1_verified.json.

    Returns:
        {hf_model_id: {task_id: float}}

    Raises:
        FileNotFoundError: If JSON file is missing.
        KeyError: If 'models' key is absent.
        ValueError: If fewer than 3 models or fewer than 500 tasks per model.
    """
    hm1_results_dir = Path(hm1_results_dir)
    json_path = hm1_results_dir / HM1_VERIFIED_FILENAME

    if not json_path.exists():
        raise FileNotFoundError(
            f"H-M1 results file not found: {json_path}\n"
            "Ensure Phase 4 for h-m1 has been completed successfully."
        )

    with open(json_path, "r") as f:
        raw = json.load(f)

    if "models" not in raw:
        raise KeyError(
            f"'models' key missing from {json_path}. "
            f"Found keys: {list(raw.keys())}"
        )

    data: dict[str, dict[str, float]] = raw["models"]

    n_models = len(data)
    if n_models < 3:
        raise ValueError(
            f"Expected >= 3 models, found {n_models}: {list(data.keys())}"
        )

    for model_id, task_scores in data.items():
        n = len(task_scores)
        if n < 500:
            raise ValueError(
                f"Model '{model_id}' has only {n} tasks; expected >= 500."
            )

    logger.info(
        "Loaded pass@1 data: %d models, %d tasks each",
        n_models,
        len(next(iter(data.values()))),
    )
    return data


# ─── Benchmark Split ──────────────────────────────────────────────────────────

def split_by_benchmark(
    pass_at_1: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """Split task dict into HumanEval+ and MBPP+ subsets by prefix.

    Returns:
        (he_dict, mbpp_dict)
    """
    he_dict: dict[str, float] = {}
    mbpp_dict: dict[str, float] = {}

    for task_id, score in pass_at_1.items():
        if task_id.startswith(HE_PREFIX):
            he_dict[task_id] = score
        elif task_id.startswith(MBPP_PREFIX):
            mbpp_dict[task_id] = score
        else:
            logger.warning("Unrecognized task prefix: %s", task_id)

    return he_dict, mbpp_dict


# ─── Tier Stratification ──────────────────────────────────────────────────────

def compute_difficulty_tiers(
    pass_at_1_data: dict[str, dict[str, float]],
    hard_threshold: float = HARD_THRESHOLD,
    easy_threshold: float = EASY_THRESHOLD,
) -> dict[str, dict[str, set]]:
    """Assign hard/easy/medium tiers per model on combined task set.

    Returns:
        {hf_model_id: {"hard": set[str], "easy": set[str], "medium": set[str]}}
    """
    tiers: dict[str, dict[str, set]] = {}

    for model_id, task_scores in pass_at_1_data.items():
        hard: set[str] = {tid for tid, v in task_scores.items() if v == hard_threshold}
        easy: set[str] = {tid for tid, v in task_scores.items() if v >= easy_threshold}
        medium: set[str] = set(task_scores.keys()) - hard - easy
        tiers[model_id] = {"hard": hard, "easy": easy, "medium": medium}

        logger.info(
            "Model %s: hard=%d, easy=%d, medium=%d (total=%d)",
            MODEL_SHORT_NAMES.get(model_id, model_id),
            len(hard), len(easy), len(medium),
            len(task_scores),
        )

    return tiers


def compute_per_benchmark_tiers(
    pass_at_1_data: dict[str, dict[str, float]],
    hard_threshold: float = HARD_THRESHOLD,
    easy_threshold: float = EASY_THRESHOLD,
) -> dict[str, dict[str, dict[str, set]]]:
    """Compute tiers split by benchmark.

    Returns:
        {hf_model_id: {
            "humaneval": {"hard": set, "easy": set, "medium": set},
            "mbpp":      {"hard": set, "easy": set, "medium": set},
        }}
    """
    per_benchmark_tiers: dict[str, dict[str, dict[str, set]]] = {}

    for model_id, task_scores in pass_at_1_data.items():
        he_scores, mbpp_scores = split_by_benchmark(task_scores)
        per_benchmark_tiers[model_id] = {}

        for bench_name, scores in [("humaneval", he_scores), ("mbpp", mbpp_scores)]:
            hard = {tid for tid, v in scores.items() if v == hard_threshold}
            easy = {tid for tid, v in scores.items() if v >= easy_threshold}
            medium = set(scores.keys()) - hard - easy
            per_benchmark_tiers[model_id][bench_name] = {
                "hard": hard,
                "easy": easy,
                "medium": medium,
            }

    return per_benchmark_tiers


def validate_tier_sizes(
    tiers: dict[str, dict[str, set]],
    min_size: int = MIN_TIER_SIZE,
) -> dict[str, dict[str, bool]]:
    """Validate n_hard >= min_size and n_easy >= min_size per model.

    CodeLlama HumanEval n_easy=0 is expected — logged as warning, not error.

    Returns:
        {hf_model_id: {"hard_ok": bool, "easy_ok": bool}}

    Raises:
        ValueError: If n_hard < min_size for any model on combined tier set.
    """
    validation_report: dict[str, dict[str, bool]] = {}

    for model_id, tier_sets in tiers.items():
        n_hard = len(tier_sets["hard"])
        n_easy = len(tier_sets["easy"])
        short = MODEL_SHORT_NAMES.get(model_id, model_id)

        hard_ok = n_hard >= min_size
        easy_ok = n_easy >= min_size

        # Hard tier mandatory
        if not hard_ok:
            raise ValueError(
                f"Model '{short}' has only n_hard={n_hard} < min_size={min_size}."
            )

        # Easy tier: CodeLlama HumanEval degenerate case expected
        if not easy_ok:
            if model_id == CODELLAMA_ID:
                warnings.warn(
                    f"CodeLlama n_easy={n_easy} < {min_size} (expected degenerate case). "
                    "Use MBPP+ as primary benchmark for CodeLlama.",
                    UserWarning,
                    stacklevel=2,
                )
            else:
                warnings.warn(
                    f"Model '{short}' n_easy={n_easy} < min_size={min_size}.",
                    UserWarning,
                    stacklevel=2,
                )

        validation_report[model_id] = {
            "hard_ok": hard_ok,
            "easy_ok": easy_ok,
            "n_hard": n_hard,
            "n_easy": n_easy,
        }

        logger.info("  %s: hard_ok=%s (n=%d), easy_ok=%s (n=%d)",
                    short, hard_ok, n_hard, easy_ok, n_easy)

    return validation_report
