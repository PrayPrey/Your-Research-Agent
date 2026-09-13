from typing import Dict, Any

from evalplus.data import get_human_eval_plus, get_mbpp_plus


def load_humaneval_plus() -> Dict[str, Dict[str, Any]]:
    """Returns 164 HumanEval+ problem dicts keyed by task_id."""
    return get_human_eval_plus()


def load_mbpp_plus() -> Dict[str, Dict[str, Any]]:
    """Returns MBPP+ problem dicts keyed by task_id."""
    return get_mbpp_plus()


def validate_datasets(humaneval: dict, mbpp: dict) -> bool:
    """Assert correct sizes; raise ValueError on mismatch."""
    if len(humaneval) != 164:
        raise ValueError(f"Expected 164 HumanEval problems, got {len(humaneval)}")
    # MBPP+ extended has 378 problems; accept both 374 and 378
    if len(mbpp) not in (374, 378):
        raise ValueError(f"Expected 374 or 378 MBPP problems, got {len(mbpp)}")
    return True
