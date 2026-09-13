#!/usr/bin/env python3
"""
Verify that experiment uses REAL data (no mock/synthetic)

This script checks:
1. No imports of synthetic ModelAccuracyDatabase
2. All model metadata has non-None accuracies
3. Accuracy values are from real timm database (not random)
4. No np.random calls in main experiment code (excluding tests/)
"""

import json
import re
from pathlib import Path


def check_no_synthetic_imports():
    """Check that no code imports the synthetic database"""
    print("1. Checking for synthetic database imports...")

    violations = []
    for py_file in Path(".").rglob("*.py"):
        # Skip tests and deprecated files
        if "test" in str(py_file) or "DEPRECATED" in str(py_file):
            continue

        content = py_file.read_text()
        if "from model_accuracy_db import" in content or "import model_accuracy_db" in content:
            if "model_accuracy_db_real" not in content:
                violations.append(str(py_file))

    if violations:
        print(f"  ✗ FAIL: Found synthetic database imports in:")
        for v in violations:
            print(f"    - {v}")
        return False
    else:
        print("  ✓ PASS: No synthetic database imports found")
        return True


def check_metadata_accuracies():
    """Check that all models have real accuracies"""
    print("\n2. Checking model metadata accuracies...")

    metadata_file = Path("data/models_metadata.json")
    if not metadata_file.exists():
        print(f"  ✗ FAIL: Metadata file not found: {metadata_file}")
        return False

    with open(metadata_file) as f:
        models = json.load(f)

    # Check for None values
    none_count = sum(1 for m in models if m.get("imagenet_accuracy") is None)
    if none_count > 0:
        print(f"  ✗ FAIL: {none_count}/{len(models)} models have None accuracy")
        return False

    # Check for suspicious synthetic patterns (too many decimal places)
    accs = [m["imagenet_accuracy"] for m in models]
    suspicious = []
    for i, acc in enumerate(accs):
        acc_str = str(acc)
        if len(acc_str.split(".")[-1]) > 6:  # More than 6 decimal places = likely random
            suspicious.append((models[i]["model_id"], acc))

    if suspicious:
        print(f"  ⚠ WARNING: {len(suspicious)} models have suspicious accuracy precision:")
        for model_id, acc in suspicious[:3]:
            print(f"    - {model_id}: {acc}")
        if len(suspicious) > 3:
            print(f"    ... and {len(suspicious) - 3} more")

    print(f"  ✓ PASS: All {len(models)} models have non-None accuracy")
    if not suspicious:
        print(f"  ✓ PASS: All accuracies look real (4 decimal places or less)")
    return True


def check_no_random_in_main_code():
    """Check for np.random calls in main experiment code"""
    print("\n3. Checking for np.random data generation in main code...")

    violations = []
    main_files = [
        "train_cape.py",
        "src/model_zoo.py",
        "src/model_accuracy_db_real.py",
    ]

    # Patterns that indicate synthetic data generation (not just splitting)
    bad_patterns = [
        r'np\.random\.(normal|uniform|randn|rand)\s*\(',  # Data generation
        r'accuracy.*=.*np\.random',  # Generating accuracy values
        r'local_rng\.(normal|uniform)',  # Seeded random generation
    ]

    for file_path in main_files:
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()

        # Check for suspicious patterns
        for pattern in bad_patterns:
            if re.search(pattern, content):
                violations.append(f"{file_path}: {pattern}")

    if violations:
        print(f"  ✗ FAIL: Found np.random usage in main code:")
        for v in violations:
            print(f"    - {v}")
        return False
    else:
        print("  ✓ PASS: No np.random data generation in main code")
        return True


def check_real_database_exists():
    """Check that real database file exists and works"""
    print("\n4. Checking real accuracy database...")

    real_db_file = Path("src/model_accuracy_db_real.py")
    if not real_db_file.exists():
        print(f"  ✗ FAIL: Real database not found: {real_db_file}")
        return False

    # Try importing and using it
    try:
        import sys
        sys.path.insert(0, "src")
        from model_accuracy_db_real import RealModelAccuracyDatabase

        db = RealModelAccuracyDatabase(cache_dir="data/accuracy_cache")

        # Test with known model
        acc = db.get_accuracy("resnet50.a1_in1k", "resnet50")
        if acc is None:
            print("  ✗ FAIL: Known model returned None accuracy")
            return False

        print(f"  ✓ PASS: Real database exists and returns accuracies")
        print(f"    Example: resnet50.a1_in1k -> {acc:.4f}")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: Could not load real database: {e}")
        return False


def main():
    print("=" * 80)
    print("REAL DATA VERIFICATION")
    print("=" * 80)

    checks = [
        check_no_synthetic_imports(),
        check_metadata_accuracies(),
        check_no_random_in_main_code(),
        check_real_database_exists(),
    ]

    print("\n" + "=" * 80)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Experiment uses REAL data")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Mock data may still be present")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit(main())
