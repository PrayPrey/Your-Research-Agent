"""
Annotation interface for human labeling.
"""
from typing import Dict, List
import pandas as pd
from .storage import save_annotations


def present_sample_for_annotation(
    sample: Dict[str, str],
    violation_criteria: List[str],
    annotator_id: int
) -> bool:
    """
    Present a single sample to annotator and collect judgment.

    Args:
        sample: Dict with keys {id, prompt, rejected_response}
        violation_criteria: List of 6 violation types (checklist)
        annotator_id: Annotator identifier (1, 2, or 3)

    Returns:
        bool: True = genuine violation, False = marginal preference
    """
    print(f"\n{'='*80}")
    print(f"ANNOTATOR {annotator_id} - Sample {sample['id']}")
    print(f"{'='*80}")
    print(f"\nPROMPT:\n{sample['prompt']}\n")
    print(f"REJECTED RESPONSE:\n{sample['rejected_response']}\n")
    print(f"{'='*80}")
    print("\nVIOLATION CRITERIA:")
    for i, criterion in enumerate(violation_criteria, 1):
        print(f"  {i}. {criterion}")
    print(f"{'='*80}")

    while True:
        response = input("\nIs this a genuine safety violation? (y/n): ").strip().lower()
        if response in ['y', 'yes', '1', 'true']:
            return True
        elif response in ['n', 'no', '0', 'false']:
            return False
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")


def collect_annotations_batch(
    samples: pd.DataFrame,
    annotator_id: int,
    violation_criteria: List[str],
    output_file: str = "data/annotations.csv"
) -> pd.DataFrame:
    """
    Collect annotations for all samples from one annotator.

    Args:
        samples: DataFrame with 500 samples (from stratified_sample)
        annotator_id: Annotator identifier (1, 2, or 3)
        violation_criteria: List of violation criteria to display
        output_file: Path to save annotations

    Returns:
        pd.DataFrame with columns: [sample_id, annotator_id, judgment]
        Shape: (500, 3)
    """
    annotations = []

    print(f"\n{'#'*80}")
    print(f"# ANNOTATION SESSION - ANNOTATOR {annotator_id}")
    print(f"# Total samples: {len(samples)}")
    print(f"{'#'*80}\n")

    for idx, row in samples.iterrows():
        sample = {
            'id': row['id'],
            'prompt': row['prompt'],
            'rejected_response': row['rejected_response']
        }

        judgment = present_sample_for_annotation(sample, violation_criteria, annotator_id)

        annotations.append({
            'sample_id': row['id'],
            'annotator_id': annotator_id,
            'judgment': judgment
        })

        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"\nProgress: {idx + 1}/{len(samples)} samples completed")

    # Convert to DataFrame
    annotations_df = pd.DataFrame(annotations)

    # Save annotations
    save_annotations(annotations_df, output_file)

    print(f"\n✓ Annotations saved to {output_file}")

    return annotations_df
