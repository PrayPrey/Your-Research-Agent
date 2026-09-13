"""Data loading and preprocessing for FLAN task family classification."""
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import load_dataset
from config import (
    MIN_SAMPLES_PER_FAMILY, MIN_FAMILIES, MAX_TOKENS, TEST_SIZE, SEED,
    TEXT_COLUMN, LABEL_COLUMN
)


def extract_task_category(task_name: str) -> str:
    """Extract base category from FLAN task name (e.g., cot_esnli_ii -> esnli)."""
    if task_name.startswith("cot_"):
        return task_name[4:].rstrip("_ii").rstrip("_i")
    if task_name.startswith("stream_"):
        return task_name[7:].rstrip("_ii").rstrip("_i")
    return task_name.split("_")[0]


def load_flan_from_huggingface(max_samples: int = 50000) -> pd.DataFrame:
    """Load FLAN dataset from HuggingFace Open-Orca/FLAN."""
    ds = load_dataset("Open-Orca/FLAN", split="train", streaming=True)
    records = []
    for i, row in enumerate(ds):
        if i >= max_samples:
            break
        task_name = row.get("_task_name", "unknown")
        records.append({
            TEXT_COLUMN: row.get("inputs", ""),
            LABEL_COLUMN: extract_task_category(task_name)
        })
    return pd.DataFrame(records)


def select_families(df: pd.DataFrame, min_samples: int = MIN_SAMPLES_PER_FAMILY,
                   min_families: int = 8) -> list:
    """Return family names with >= min_samples, require >= min_families."""
    counts = df[LABEL_COLUMN].value_counts()
    valid = counts[counts >= min_samples].index.tolist()
    if len(valid) < min_families:
        valid = counts.nlargest(min_families).index.tolist()
        print(f"Warning: relaxed to top {len(valid)} families")
    return valid[:15]


def extract_prefix(text: str, max_tokens: int = MAX_TOKENS) -> str:
    """Truncate text to max_tokens words."""
    words = str(text).split()[:max_tokens]
    return " ".join(words)


def build_dataset(df: pd.DataFrame, families: list) -> tuple:
    """Filter to families, apply extract_prefix. Returns (texts, labels)."""
    filtered = df[df[LABEL_COLUMN].isin(families)].copy()
    filtered["prefix"] = filtered[TEXT_COLUMN].apply(lambda x: extract_prefix(x))
    return filtered["prefix"].tolist(), filtered[LABEL_COLUMN].tolist()


def stratified_split(X: list, y: list, test_size: float = TEST_SIZE, seed: int = SEED) -> tuple:
    """Stratified train/test split."""
    return train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)


def load_and_prepare_data() -> tuple:
    """Main data pipeline: load, filter, split."""
    print("Loading FLAN dataset from HuggingFace...")
    df = load_flan_from_huggingface(max_samples=50000)
    print(f"Loaded {len(df)} samples")

    print("Selecting task families...")
    families = select_families(df)
    print(f"Selected {len(families)} families: {families[:5]}...")

    print("Building dataset...")
    texts, labels = build_dataset(df, families)
    print(f"Dataset size: {len(texts)} samples")

    print("Splitting train/test...")
    X_train, X_test, y_train, y_test = stratified_split(texts, labels)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    return X_train, X_test, y_train, y_test, families
