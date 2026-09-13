#!/usr/bin/env python3
"""
CLI tool for collecting human annotations for H-E1 experiment.

Usage:
    python -m annotation.cli --samples data/samples.csv --annotator 1 --output data/annotations.csv
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from annotation.interface import collect_annotations_batch


# Violation criteria from experiment brief
VIOLATION_CRITERIA = [
    "1. Direct harm/violence encouragement",
    "2. Toxic/offensive language",
    "3. Privacy violations or personal information disclosure",
    "4. Dangerous/illegal advice",
    "5. Deception or misinformation",
    "6. Other safety policy violations"
]


def main():
    parser = argparse.ArgumentParser(
        description="Collect human annotations for H-E1 base-rate validation study"
    )
    parser.add_argument(
        "--samples",
        required=True,
        help="Path to samples CSV file (from stratified sampling)"
    )
    parser.add_argument(
        "--annotator",
        type=int,
        required=True,
        choices=[1, 2, 3],
        help="Annotator ID (1, 2, or 3)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: data/annotations_annotator_<ID>.csv)"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )

    args = parser.parse_args()

    # Load samples
    if not Path(args.samples).exists():
        print(f"ERROR: Samples file not found: {args.samples}", file=sys.stderr)
        sys.exit(1)

    samples = pd.read_csv(args.samples)
    print(f"Loaded {len(samples)} samples from {args.samples}")

    # Determine output file
    if args.output is None:
        output_file = f"data/annotations_annotator_{args.annotator}.csv"
    else:
        output_file = args.output

    # Check if annotations already exist
    if Path(output_file).exists():
        response = input(f"\nWARNING: {output_file} already exists. Overwrite? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            print("Annotation collection cancelled.")
            sys.exit(0)

    print(f"\n{'='*80}")
    print(f"H-E1 ANNOTATION STUDY - ANNOTATOR {args.annotator}")
    print(f"{'='*80}")
    print(f"\nYou will review {len(samples)} rejected responses from HH-RLHF dataset.")
    print(f"For each sample, judge whether it contains a GENUINE safety violation")
    print(f"or is merely a MARGINAL preference difference.")
    print(f"\nViolation criteria:")
    for criterion in VIOLATION_CRITERIA:
        print(f"  {criterion}")
    print(f"\n{'='*80}")

    input("\nPress ENTER to begin annotation session...")

    # Collect annotations
    try:
        annotations = collect_annotations_batch(
            samples=samples,
            annotator_id=args.annotator,
            violation_criteria=VIOLATION_CRITERIA,
            output_file=output_file
        )

        print(f"\n{'='*80}")
        print(f"ANNOTATION SESSION COMPLETE")
        print(f"{'='*80}")
        print(f"Total samples annotated: {len(annotations)}")
        print(f"Violations identified: {annotations['judgment'].sum()}")
        print(f"Violation rate: {annotations['judgment'].mean():.3f}")
        print(f"Annotations saved to: {output_file}")
        print(f"\n{'='*80}")

        # If all 3 annotators done, merge into single file
        check_and_merge_annotations(args.annotator, output_file)

    except KeyboardInterrupt:
        print("\n\nAnnotation session interrupted by user.")
        print("Progress may have been saved. Check output file.")
        sys.exit(1)


def check_and_merge_annotations(current_annotator: int, current_file: str):
    """Check if all 3 annotators have completed and merge files."""
    base_dir = Path(current_file).parent

    # Check for all 3 annotator files
    annotator_files = [
        base_dir / f"annotations_annotator_{i}.csv"
        for i in [1, 2, 3]
    ]

    if all(f.exists() for f in annotator_files):
        print(f"\n{'='*80}")
        print(f"ALL 3 ANNOTATORS COMPLETE!")
        print(f"{'='*80}")
        print(f"Merging annotations into single file...")

        # Load and concatenate
        dfs = [pd.read_csv(f) for f in annotator_files]
        merged = pd.concat(dfs, ignore_index=True)

        # Save merged file
        merged_file = base_dir / "annotations.csv"
        merged.to_csv(merged_file, index=False)

        print(f"✓ Merged annotations saved to: {merged_file}")
        print(f"  Total annotations: {len(merged)}")
        print(f"  Samples: {merged['sample_id'].nunique()}")
        print(f"  Annotators: {sorted(merged['annotator_id'].unique())}")
        print(f"\nYou can now run the full experiment with:")
        print(f"  python src/main.py")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()
