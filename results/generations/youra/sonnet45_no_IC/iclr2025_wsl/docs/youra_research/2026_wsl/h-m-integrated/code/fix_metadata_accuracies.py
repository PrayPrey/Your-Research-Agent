#!/usr/bin/env python3
"""
Fix cached metadata to populate real ImageNet accuracies
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from model_accuracy_db_real import RealModelAccuracyDatabase


def fix_metadata_accuracies(metadata_path: str, output_path: str = None):
    """Update metadata with real accuracies"""

    if output_path is None:
        output_path = metadata_path

    print(f"Loading metadata from {metadata_path}")
    with open(metadata_path, 'r') as f:
        models = json.load(f)

    print(f"Found {len(models)} models")

    # Initialize REAL accuracy database (no synthetic data)
    accuracy_db = RealModelAccuracyDatabase(cache_dir="data/accuracy_cache")

    # Update accuracies
    none_count_before = sum(1 for m in models if m.get('imagenet_accuracy') is None)
    print(f"Models with None accuracy before: {none_count_before}/{len(models)}")

    for model in models:
        model_id = model.get("model_id") or model.get("hf_path")
        architecture = model.get("architecture")

        # Get real accuracy
        accuracy = accuracy_db.get_accuracy(model_id, architecture)
        model["imagenet_accuracy"] = accuracy

    # Verify all are populated
    none_count_after = sum(1 for m in models if m.get('imagenet_accuracy') is None)
    print(f"Models with None accuracy after: {none_count_after}/{len(models)}")

    if none_count_after > 0:
        raise ValueError(f"Failed to populate all accuracies: {none_count_after} still None")

    # Print statistics
    accuracies = [m["imagenet_accuracy"] for m in models]
    print(f"\nAccuracy statistics:")
    print(f"  Range: [{min(accuracies):.4f}, {max(accuracies):.4f}]")
    print(f"  Mean: {sum(accuracies)/len(accuracies):.4f}")

    # Per-architecture stats
    arch_stats = {}
    for model in models:
        arch = model["architecture"]
        if arch not in arch_stats:
            arch_stats[arch] = []
        arch_stats[arch].append(model["imagenet_accuracy"])

    print(f"\nPer-architecture:")
    for arch, accs in arch_stats.items():
        print(f"  {arch}: {sum(accs)/len(accs):.4f} (n={len(accs)})")

    # Save updated metadata
    print(f"\nSaving updated metadata to {output_path}")
    with open(output_path, 'w') as f:
        json.dump(models, f, indent=2)

    print("✓ Metadata accuracies fixed successfully")


if __name__ == "__main__":
    metadata_path = "data/models_metadata.json"
    fix_metadata_accuracies(metadata_path)
