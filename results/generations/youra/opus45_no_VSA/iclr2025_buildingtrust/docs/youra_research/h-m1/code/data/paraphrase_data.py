"""Load PAWS and QQP datasets for BSI computation."""

from datasets import load_dataset


def load_paws(split: str = "test"):
    """Load PAWS-Wiki labeled_final test set."""
    ds = load_dataset("google-research-datasets/paws", "labeled_final", split=split)
    return ds


def load_qqp(split: str = "validation"):
    """Load QQP from GLUE validation set."""
    ds = load_dataset("nyu-mll/glue", "qqp", split=split)
    return ds


if __name__ == "__main__":
    paws = load_paws()
    qqp = load_qqp()
    print(f"PAWS: {len(paws)} pairs")
    print(f"QQP: {len(qqp)} pairs")
