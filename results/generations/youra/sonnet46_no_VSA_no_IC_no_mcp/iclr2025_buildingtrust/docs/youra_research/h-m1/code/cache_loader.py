"""Load H-E1 per-example JSONL caches into numpy arrays."""
import json
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def load_split_cache(split: str, results_dir: str, file_map: dict) -> dict:
    """
    Load H-E1 per-example JSONL for one split.
    Returns {"conf": np.ndarray, "correct": np.ndarray,
             "pred": np.ndarray, "label": np.ndarray}
    Raises FileNotFoundError with fallback message if missing.
    """
    filename = file_map.get(split)
    if filename is None:
        raise KeyError(f"Unknown split '{split}'. Available: {list(file_map.keys())}")

    path = Path(results_dir) / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Cache missing for split '{split}' at {path}. "
            "Re-run H-E1 first to regenerate the per-example JSONL caches."
        )

    confs, corrects, preds, labels = [], [], [], []
    with open(path) as f:
        for line in f:
            rec = json.loads(line.strip())
            confs.append(float(rec["confidence"]))
            corrects.append(int(rec["correct"]))
            preds.append(int(rec["pred_label"]))
            labels.append(int(rec["true_label"]))

    return {
        "conf":    np.array(confs,    dtype=np.float32),
        "correct": np.array(corrects, dtype=np.int32),
        "pred":    np.array(preds,    dtype=np.int32),
        "label":   np.array(labels,   dtype=np.int32),
    }


def load_all_caches(results_dir: str, splits: list, file_map: dict) -> dict:
    """Returns {split_name: per_example_dict} for all splits."""
    caches = {}
    for split in splits:
        try:
            caches[split] = load_split_cache(split, results_dir, file_map)
            logger.info("Loaded cache '%s': n=%d", split, len(caches[split]["conf"]))
        except FileNotFoundError as e:
            raise FileNotFoundError(str(e))
    return caches


def verify_cache_integrity(
    caches: dict,
    expected_counts: Optional[dict] = None,
) -> None:
    """Assert all required fields present; log warnings for count mismatches."""
    required_fields = {"conf", "correct", "pred", "label"}
    for split, cache in caches.items():
        missing = required_fields - set(cache.keys())
        if missing:
            raise ValueError(f"Cache '{split}' missing fields: {missing}")

        n = len(cache["conf"])
        for field in required_fields:
            if len(cache[field]) != n:
                raise ValueError(
                    f"Cache '{split}' field '{field}' length {len(cache[field])} != {n}"
                )

        if expected_counts and split in expected_counts:
            exp = expected_counts[split]
            if n != exp:
                logger.warning(
                    "Cache '%s' has %d examples; expected %d", split, n, exp
                )

    logger.info("Cache integrity verified for %d splits", len(caches))
