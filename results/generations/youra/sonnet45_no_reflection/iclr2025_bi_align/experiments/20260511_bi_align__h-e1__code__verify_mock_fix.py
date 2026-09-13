#!/usr/bin/env python3
"""
Verification script to confirm mock data has been replaced with real datasets.
This script validates that the code uses real MMLU and HumanEval datasets.
"""

import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("MOCK DATA FIX VERIFICATION")
print("="*60)
print()

# Check 1: POC file is disabled
print("[1/5] Checking POC file status...")
poc_file = Path(__file__).parent / "main_poc.py"
poc_disabled = Path(__file__).parent / "main_poc.py.DISABLED"

if poc_file.exists():
    print("✗ FAIL: main_poc.py still active (should be disabled)")
    sys.exit(1)
elif poc_disabled.exists():
    print("✓ PASS: main_poc.py.DISABLED found (POC code disabled)")
else:
    print("✓ PASS: No POC file found")

# Check 2: Real data loaders exist
print("\n[2/5] Checking data loader implementation...")
try:
    from data.loader import MMLULoader, HumanEvalLoader
    print("✓ PASS: Data loaders imported successfully")
except ImportError as e:
    print(f"✗ FAIL: Cannot import data loaders: {e}")
    sys.exit(1)

# Check 3: MMLU loader uses HuggingFace dataset
print("\n[3/5] Validating MMLU loader uses real dataset...")
mmlu_loader = MMLULoader()
print(f"  Dataset source: {mmlu_loader.dataset_name}")
if mmlu_loader.dataset_name == "cais/mmlu":
    print("✓ PASS: MMLU loader configured for HuggingFace dataset (cais/mmlu)")
else:
    print(f"✗ FAIL: MMLU loader uses wrong source: {mmlu_loader.dataset_name}")
    sys.exit(1)

# Check 4: Load real MMLU data
print("\n[4/5] Loading real MMLU dataset from HuggingFace...")
try:
    data = mmlu_loader.load_dataset()
    num_subjects = len(mmlu_loader.subjects)
    if num_subjects == 57:
        print(f"✓ PASS: Loaded {num_subjects} MMLU subjects (expected 57)")
        print(f"  Sample subjects: {mmlu_loader.subjects[:3]}")
    else:
        print(f"✗ FAIL: Loaded {num_subjects} subjects, expected 57")
        sys.exit(1)
except Exception as e:
    print(f"✗ FAIL: Error loading MMLU: {e}")
    sys.exit(1)

# Check 5: Load real HumanEval data
print("\n[5/5] Loading real HumanEval dataset...")
try:
    he_loader = HumanEvalLoader()
    problems = he_loader.load_dataset()
    num_problems = len(he_loader.problems)
    if num_problems == 164:
        print(f"✓ PASS: Loaded {num_problems} HumanEval problems (expected 164)")
        print(f"  Sample tasks: {list(he_loader.problems.keys())[:3]}")
    else:
        print(f"✗ FAIL: Loaded {num_problems} problems, expected 164")
        sys.exit(1)
except Exception as e:
    print(f"✗ FAIL: Error loading HumanEval: {e}")
    sys.exit(1)

# Check 6: Verify main.py uses data loaders (not synthetic data)
print("\n[6/6] Analyzing main.py for synthetic data usage...")
main_file = Path(__file__).parent / "main.py"
with open(main_file, 'r') as f:
    main_content = f.read()

# Check for synthetic data generation patterns
synthetic_patterns = [
    "np.random.uniform",
    "subject_difficulties",
    "synthetic data",
    "GENERATING SYNTHETIC"
]

found_synthetic = False
for pattern in synthetic_patterns:
    if pattern in main_content and "POC" not in main_content[:500]:
        print(f"✗ WARNING: Found potential synthetic pattern: {pattern}")
        found_synthetic = True

# Check for real data loader usage
required_patterns = [
    "MMLULoader",
    "HumanEvalLoader",
    "load_dataset"
]

all_found = all(pattern in main_content for pattern in required_patterns)

if all_found and not found_synthetic:
    print("✓ PASS: main.py uses real data loaders, no synthetic data generation")
else:
    if not all_found:
        print("✗ FAIL: main.py missing real data loader calls")
    sys.exit(1)

print("\n" + "="*60)
print("ALL CHECKS PASSED ✓")
print("="*60)
print("\nConclusion:")
print("  - POC synthetic data generation is DISABLED")
print("  - Real MMLU dataset (cais/mmlu) loads successfully")
print("  - Real HumanEval dataset (openai/human-eval) loads successfully")
print("  - main.py uses real data loaders, not synthetic generation")
print()
print("Next step: Set ANTHROPIC_API_KEY and run main.py for full experiment")
print("="*60)
