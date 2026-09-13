"""Load H-E1 per-example JSONL caches for H-M2 analysis."""
import json
import logging
from pathlib import Path
import numpy as np

from config import H_E1_RESULTS_DIR, TASK_FILE_MAP, TASKS

logger = logging.getLogger(__name__)

MIN_EXAMPLES = 50  # relaxed from 200 to handle adversarial splits (advglue_mnli=121, qqp=78)


def load_split_file(filepath: Path) -> dict:
    """Load one JSONL file. Returns dict of numpy arrays."""
    confs, corrects, preds, labels = [], [], [], []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
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


def load_cell(task: str) -> tuple[dict, dict]:
    """Load (clean, adversarial) data for one task cell."""
    adv_fname, clean_fname = TASK_FILE_MAP[task]
    adv_path   = H_E1_RESULTS_DIR / adv_fname
    clean_path = H_E1_RESULTS_DIR / clean_fname

    for path in [adv_path, clean_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"H-E1 JSONL missing: {path}\n"
                "Re-run H-E1 with --log_samples to regenerate."
            )

    clean_data = load_split_file(clean_path)
    adv_data   = load_split_file(adv_path)

    logger.info("Task %s: clean n=%d, adv n=%d", task, len(clean_data["conf"]), len(adv_data["conf"]))
    return clean_data, adv_data


def preflight_check() -> None:
    """Verify all required JSONL files exist and have sufficient examples."""
    print("Pre-flight check: verifying H-E1 JSONL files...")
    all_files = set()
    for adv_f, clean_f in TASK_FILE_MAP.values():
        all_files.add(adv_f)
        all_files.add(clean_f)

    missing = []
    for fname in sorted(all_files):
        path = H_E1_RESULTS_DIR / fname
        if not path.exists():
            missing.append(str(path))
            print(f"  MISSING: {fname}")
        else:
            n = sum(1 for _ in open(path) if _.strip())
            status = "OK" if n >= MIN_EXAMPLES else f"WARN (n={n} < {MIN_EXAMPLES})"
            print(f"  {status}: {fname} (n={n})")

    if missing:
        raise SystemExit(f"Pre-flight FAILED: {len(missing)} file(s) missing:\n" + "\n".join(missing))

    print(f"Pre-flight PASSED: all {len(all_files)} JSONL files found.")
