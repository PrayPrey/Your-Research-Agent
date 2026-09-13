# H-M4 Data Loading: PWC datasets metadata
# Strategy: Static paper count comparison - traditional vs emergent benchmarks
# Validates "reduced dominance" by comparing total paper counts

import pandas as pd
from datasets import load_dataset

from config import HF_DATASETS, TRADITIONAL_BENCHMARKS


# Emergent-capability benchmarks (post-foundation-model era)
EMERGENT_BENCHMARKS = [
    "mmlu", "big-bench", "bigbench", "humaneval", "human-eval",
    "gsm8k", "math", "arc", "hellaswag", "winogrande",
    "truthfulqa", "lambada", "mt-bench", "alpacaeval",
    "boolq", "piqa", "openbookqa", "commonsenseqa",
]


def load_pwc_data() -> pd.DataFrame:
    """Load pwc-archive/datasets and classify benchmarks."""
    print("  Loading pwc-archive/datasets...")
    datasets_meta = load_dataset(HF_DATASETS["datasets_meta"], split="train")

    df = datasets_meta.to_pandas()
    print(f"  Loaded {len(df)} datasets")

    # Keep relevant columns
    df = df[["name", "introduced_date", "num_papers"]].copy()
    df.columns = ["dataset_name", "date", "paper_count"]

    # Normalize dataset names
    df["dataset_name"] = df["dataset_name"].str.lower().str.strip()

    # Fill missing paper_count with 0
    df["paper_count"] = df["paper_count"].fillna(0).astype(int)

    return df


def classify_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """Classify datasets as traditional, emergent, or other."""
    traditional_lower = [b.lower() for b in TRADITIONAL_BENCHMARKS]

    def classify(name):
        # Check traditional
        for t in traditional_lower:
            if t in name:
                return "traditional"
        # Check emergent
        for e in EMERGENT_BENCHMARKS:
            if e in name:
                return "emergent"
        return "other"

    df["category"] = df["dataset_name"].apply(classify)
    return df


def compute_share_statistics(df: pd.DataFrame) -> dict:
    """Compute paper count statistics by category."""
    # Total papers
    total_papers = df["paper_count"].sum()

    # By category
    traditional_papers = df[df["category"] == "traditional"]["paper_count"].sum()
    emergent_papers = df[df["category"] == "emergent"]["paper_count"].sum()
    other_papers = df[df["category"] == "other"]["paper_count"].sum()

    # Shares
    traditional_share = traditional_papers / total_papers if total_papers > 0 else 0
    emergent_share = emergent_papers / total_papers if total_papers > 0 else 0

    return {
        "total_papers": int(total_papers),
        "traditional_papers": int(traditional_papers),
        "emergent_papers": int(emergent_papers),
        "other_papers": int(other_papers),
        "traditional_share": float(traditional_share),
        "emergent_share": float(emergent_share),
    }


def load_and_prepare_data() -> tuple[pd.DataFrame, dict]:
    """Full data loading pipeline.

    Returns (df, stats) where stats contains paper counts and shares.
    """
    print("Loading PWC datasets from HuggingFace...")
    df = load_pwc_data()

    print("Classifying benchmarks...")
    df = classify_benchmarks(df)

    print("Computing statistics...")
    stats = compute_share_statistics(df)

    print(f"\nDataset Summary:")
    print(f"  Total papers: {stats['total_papers']:,}")
    print(f"  Traditional benchmark papers: {stats['traditional_papers']:,} ({stats['traditional_share']*100:.2f}%)")
    print(f"  Emergent benchmark papers: {stats['emergent_papers']:,} ({stats['emergent_share']*100:.2f}%)")
    print(f"  Other benchmark papers: {stats['other_papers']:,}")

    return df, stats
