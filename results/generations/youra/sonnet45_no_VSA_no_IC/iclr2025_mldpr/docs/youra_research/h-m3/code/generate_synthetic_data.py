"""Generate synthetic metadata for h-m3 validation."""

import json
import random
from pathlib import Path
from typing import Dict, List

from config import SAMPLE_SIZES, RAW_DIR, RANDOM_SEED

random.seed(RANDOM_SEED)


def generate_hf_metadata(n: int) -> List[Dict]:
    """
    Generate HuggingFace metadata.

    Expected behavior:
    - license: 85-95% present (enforced dropdown)
    - version: 90-100% present (auto-generated semantic version)
    """
    records = []
    for i in range(n):
        # license: 90% present (enforced)
        if random.random() < 0.90:
            licenses = ["apache-2.0", "mit", "cc-by-4.0", "gpl-3.0", "bsd-3-clause"]
            license_val = random.choice(licenses)
        else:
            license_val = random.choice([None, "", "unknown", "other"])

        # version: 95% present (auto-generated)
        if random.random() < 0.95:
            version_val = f"{random.randint(1, 3)}.{random.randint(0, 5)}.{random.randint(0, 10)}"
        else:
            version_val = None

        records.append({
            "id": f"hf_{i:05d}",
            "platform": "HF",
            "license": license_val,
            "version": version_val,
        })
    return records


def generate_openml_metadata(n: int) -> List[Dict]:
    """
    Generate OpenML metadata.

    Expected behavior:
    - license: 85-95% present (required field)
    - version: 85-95% present (required integer version)
    """
    records = []
    for i in range(n):
        # license: 88% present (required field, some legacy datasets missing)
        if random.random() < 0.88:
            licenses = ["CC-BY 4.0", "Public Domain", "GPL-3.0", "MIT"]
            license_val = random.choice(licenses)
        else:
            license_val = ""

        # version: 92% present (required field)
        if random.random() < 0.92:
            version_val = random.randint(1, 20)
        else:
            version_val = None

        records.append({
            "id": f"openml_{i:04d}",
            "platform": "OpenML",
            "license": license_val,
            "version": version_val,
        })
    return records


def generate_uci_metadata(n: int) -> List[Dict]:
    """
    Generate UCI metadata.

    Expected behavior:
    - license: 70-85% present (NOT enforced, but social norm)
    - version: 60-80% present (implicit via last-modified date)
    """
    records = []
    for i in range(n):
        # license: 75% present (social norm, not enforced)
        if random.random() < 0.75:
            # UCI uses longer text descriptions
            licenses = [
                "This dataset is available under CC-BY 4.0 license.",
                "Public domain, no restrictions.",
                "Creative Commons Attribution 4.0 International",
                "GPL-3.0 licensed dataset",
            ]
            license_val = random.choice(licenses)
        else:
            license_val = ""

        # version: 70% present (implicit date-based)
        if random.random() < 0.70:
            # Version indicated by date or keyword
            if random.random() < 0.5:
                version_val = f"updated 2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            else:
                version_val = f"version {random.randint(1, 3)}"
        else:
            version_val = ""

        records.append({
            "id": f"uci_{i:03d}",
            "platform": "UCI",
            "license": license_val,
            "version": version_val,
        })
    return records


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic metadata...")

    # Generate platform data
    hf_data = generate_hf_metadata(SAMPLE_SIZES["HF"])
    openml_data = generate_openml_metadata(SAMPLE_SIZES["OpenML"])
    uci_data = generate_uci_metadata(SAMPLE_SIZES["UCI"])

    # Save to JSON
    with open(RAW_DIR / "huggingface_metadata.json", "w") as f:
        json.dump(hf_data, f, indent=2)
    print(f"✓ Generated {len(hf_data)} HuggingFace records")

    with open(RAW_DIR / "openml_metadata.json", "w") as f:
        json.dump(openml_data, f, indent=2)
    print(f"✓ Generated {len(openml_data)} OpenML records")

    with open(RAW_DIR / "uci_metadata.json", "w") as f:
        json.dump(uci_data, f, indent=2)
    print(f"✓ Generated {len(uci_data)} UCI records")

    print(f"\nTotal: {len(hf_data) + len(openml_data) + len(uci_data)} records")


if __name__ == "__main__":
    main()
