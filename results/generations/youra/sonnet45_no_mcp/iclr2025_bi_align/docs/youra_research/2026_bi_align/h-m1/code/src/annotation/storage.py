"""
Annotation data storage utilities.
"""
import pandas as pd
from pathlib import Path


def save_annotations(annotations: pd.DataFrame, output_file: str) -> None:
    """
    Save annotations to CSV file.

    Args:
        annotations: DataFrame with columns [sample_id, annotator_id, judgment]
        output_file: Path to save annotations
    """
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    annotations.to_csv(output_file, index=False)


def load_annotations(annotation_file: str) -> pd.DataFrame:
    """
    Load annotations from CSV file.

    Args:
        annotation_file: Path to annotation CSV

    Returns:
        DataFrame with columns [sample_id, annotator_id, judgment]
    """
    df = pd.read_csv(annotation_file)
    return df
