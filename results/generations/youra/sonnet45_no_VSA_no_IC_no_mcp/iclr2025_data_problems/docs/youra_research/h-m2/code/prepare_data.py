"""Data preparation for h-m2: Load and split Dolly-15k dataset."""

from datasets import load_dataset
import json
from pathlib import Path

def main():
    # Load Dolly-15k
    print("Loading Dolly-15k...")
    dataset = load_dataset("databricks/databricks-dolly-15k", split="train")

    # 90/10 split
    splits = dataset.train_test_split(test_size=0.1, seed=42)
    train_data = splits["train"]
    val_data = splits["test"]

    print(f"Train: {len(train_data)} samples")
    print(f"Val: {len(val_data)} samples")

    # Save splits
    output_dir = Path("data/dolly_splits")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "train.jsonl", "w") as f:
        for sample in train_data:
            f.write(json.dumps(sample) + "\n")

    with open(output_dir / "val.jsonl", "w") as f:
        for sample in val_data:
            f.write(json.dumps(sample) + "\n")

    print(f"Saved splits to {output_dir}")

if __name__ == "__main__":
    main()
