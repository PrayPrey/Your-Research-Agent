"""Generate validation sample for manual parsing review."""

import json
import random
from typing import List, Dict

from config import VALIDATION_STRATIFICATION, RANDOM_SEED, RESULTS_DIR


def generate_validation_sample(
    all_records: List[Dict],
    stratification: Dict[str, int] = VALIDATION_STRATIFICATION,
    seed: int = RANDOM_SEED,
) -> List[Dict]:
    """
    Generate stratified random sample for manual parsing validation.

    Args:
        all_records: Parsed records with presence flags
        stratification: {"HF": 50, "OpenML": 30, "UCI": 20}
        seed: Random seed

    Returns:
        List of sampled records with raw metadata and parsed flags
    """
    random.seed(seed)

    # Group by platform
    by_platform = {"HF": [], "OpenML": [], "UCI": []}
    for record in all_records:
        platform = record["platform"]
        if platform in by_platform:
            by_platform[platform].append(record)

    # Stratified sampling
    sample = []
    for platform, count in stratification.items():
        if platform in by_platform and len(by_platform[platform]) >= count:
            sample.extend(random.sample(by_platform[platform], count))
        else:
            # Take all if insufficient records
            sample.extend(by_platform[platform])

    return sample


def save_validation_sample(sample: List[Dict], output_path: str = None):
    """Save validation sample to JSON with instructions."""
    if output_path is None:
        output_path = RESULTS_DIR / "validation_sample.json"

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "instructions": (
            "Manual validation instructions:\n"
            "1. For each record, verify 'license_present' flag:\n"
            "   - Check if raw 'license' field contains valid license info\n"
            "   - True = license present, False = absent/invalid\n"
            "2. For each record, verify 'version_present' flag:\n"
            "   - Check if raw 'version' field contains valid version info\n"
            "   - True = version present, False = absent/invalid\n"
            "3. Calculate agreement rate: (correct flags / total flags) * 100\n"
            "   - Target: ≥85% agreement\n"
        ),
        "sample_size": len(sample),
        "stratification": {
            "HF": sum(1 for r in sample if r["platform"] == "HF"),
            "OpenML": sum(1 for r in sample if r["platform"] == "OpenML"),
            "UCI": sum(1 for r in sample if r["platform"] == "UCI"),
        },
        "records": sample,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✓ Validation sample saved to {output_path}")
    print(f"  Total records: {len(sample)}")
    print(f"  HF: {output['stratification']['HF']}")
    print(f"  OpenML: {output['stratification']['OpenML']}")
    print(f"  UCI: {output['stratification']['UCI']}")


def calculate_agreement_rate(validation_results: List[Dict]) -> float:
    """
    Calculate agreement rate between automated parsing and manual review.

    Args:
        validation_results: [
            {
                "dataset_id": "...",
                "license_automated": bool,
                "license_manual": bool,
                "version_automated": bool,
                "version_manual": bool,
            },
            ...
        ]

    Returns:
        Agreement rate (0-1)
    """
    total_checks = 0
    correct_checks = 0

    for result in validation_results:
        # License check
        if result["license_automated"] == result["license_manual"]:
            correct_checks += 1
        total_checks += 1

        # Version check
        if result["version_automated"] == result["version_manual"]:
            correct_checks += 1
        total_checks += 1

    return correct_checks / total_checks if total_checks > 0 else 0.0
