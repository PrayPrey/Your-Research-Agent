"""H-C1: Load H-E2 Arrow datasets for the 4 source conditions."""
import sys
from pathlib import Path
from datasets import load_from_disk

from config import CONDITIONS, H_E2_DATASETS_DIR


def load_condition_dataset(condition: str, data_dir: str = H_E2_DATASETS_DIR):
    """Load Arrow dataset from H-E2 data dir for given condition."""
    path = Path(data_dir) / condition
    if not path.exists():
        print(f"[ERROR] Dataset not found at {path}. Run H-E2 prepare_data.py first.")
        sys.exit(1)
    dataset = load_from_disk(str(path))
    # Ensure 'text' column exists (H-E2 already formatted)
    if "text" not in dataset.column_names:
        # Try joining prompt + completion
        if "prompt" in dataset.column_names and "completion" in dataset.column_names:
            dataset = dataset.map(lambda x: {"text": x["prompt"] + x["completion"]})
        else:
            raise ValueError(f"Dataset {condition} has no 'text' column: {dataset.column_names}")
    return dataset


def verify_datasets(data_dir: str = H_E2_DATASETS_DIR) -> dict:
    """Return {condition: n_examples}; raise if any condition missing."""
    counts = {}
    for condition in CONDITIONS:
        ds = load_condition_dataset(condition, data_dir)
        counts[condition] = len(ds)
        print(f"  {condition}: {len(ds)} examples")
    return counts


if __name__ == "__main__":
    print("Verifying H-E2 datasets for H-C1...")
    counts = verify_datasets()
    print(f"All conditions present: {counts}")
