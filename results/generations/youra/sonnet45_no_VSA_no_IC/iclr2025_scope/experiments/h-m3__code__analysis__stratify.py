"""Dataset stratification by query complexity."""
import json
import pandas as pd


def stratify_dataset(
    classifier,
    data_path: str,
    min_per_stratum: int = 300
) -> pd.DataFrame:
    """Load LongBench, classify all queries, ensure balance.

    Returns: DataFrame with [question_id, question, context, complexity, entity_density]
    """
    # Load datasets from JSONL files
    dataset_files = ["hotpotqa.jsonl", "2wikimqa.jsonl", "musique.jsonl"]

    rows = []
    for fname in dataset_files:
        file_path = f"{data_path}/{fname}"
        with open(file_path, 'r') as f:
            for line in f:
                sample = json.loads(line)
                density = classifier.compute_entity_density(sample["input"])
                complexity = classifier.classify(sample["input"])
                rows.append({
                    "question_id": f"{sample['dataset']}_{len(rows)}",
                    "question": sample["input"],
                    "context": sample["context"],
                    "complexity": complexity,
                    "entity_density": density
                })

    df = pd.DataFrame(rows)

    # Balance strata
    simple = df[df["complexity"] == "simple"].head(min_per_stratum)
    complex = df[df["complexity"] == "complex"].head(min_per_stratum)

    return pd.concat([simple, complex], ignore_index=True)
