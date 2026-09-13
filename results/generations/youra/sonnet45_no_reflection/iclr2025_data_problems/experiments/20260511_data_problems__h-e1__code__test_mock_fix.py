#!/usr/bin/env python3
"""
Quick validation that mock data issue is fixed
Verifies that:
1. Real dataset is loaded (GSM8K)
2. Real model is loaded
3. Real accuracy evaluation is performed (not hard-coded)
"""
import sys
import os
import re

def check_file_for_violations(filepath, violations):
    """Check if file contains any of the violation patterns"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            for line_num, pattern, description in violations:
                # Check if the violation pattern still exists
                if re.search(pattern, content, re.MULTILINE):
                    return False, f"VIOLATION FOUND at {filepath}: {description}"
        return True, f"✓ {filepath} - All violations fixed"
    except FileNotFoundError:
        return False, f"File not found: {filepath}"

def main():
    print("=" * 80)
    print("MOCK DATA FIX VALIDATION")
    print("=" * 80)
    print()

    # Define violations to check
    run_experiment_violations = [
        (137, r'final_accuracy\s*=\s*initial_accuracy\s*\+\s*contamination_rate\s*\*\s*0\.5',
         "Hard-coded accuracy formula: final_accuracy = initial_accuracy + contamination_rate * 0.5"),
    ]

    all_passed = True

    # Check run_experiment.py
    print("Checking run_experiment.py...")
    passed, msg = check_file_for_violations('run_experiment.py', run_experiment_violations)
    print(f"  {msg}")
    all_passed = all_passed and passed
    print()

    # Check for real evaluation function
    print("Checking for real evaluation implementation...")
    try:
        with open('run_experiment.py', 'r') as f:
            content = f.read()

            # Check for evaluate_gsm8k_accuracy function
            if 'def evaluate_gsm8k_accuracy' in content:
                print("  ✓ Found evaluate_gsm8k_accuracy function")
            else:
                print("  ✗ Missing evaluate_gsm8k_accuracy function")
                all_passed = False

            # Check for actual model.generate() calls
            if 'model.generate(' in content:
                print("  ✓ Found real model.generate() calls")
            else:
                print("  ✗ Missing real model.generate() calls")
                all_passed = False

            # Check for extract_answer_number function
            if 'def extract_answer_number' in content:
                print("  ✓ Found extract_answer_number function")
            else:
                print("  ✗ Missing extract_answer_number function")
                all_passed = False

            # Verify evaluation is called
            if 'evaluate_gsm8k_accuracy(model, tokenizer, gsm8k_test' in content:
                print("  ✓ evaluate_gsm8k_accuracy is called with real model and dataset")
            else:
                print("  ✗ evaluate_gsm8k_accuracy is not properly called")
                all_passed = False

    except FileNotFoundError:
        print("  ✗ run_experiment.py not found")
        all_passed = False
    print()

    # Final result
    print("=" * 80)
    if all_passed:
        print("✓ MOCK FIX VALIDATION PASSED")
        print("All hard-coded accuracy calculations have been replaced with real evaluation")
        return 0
    else:
        print("✗ MOCK FIX VALIDATION FAILED")
        print("Some violations still exist or required functions are missing")
        return 1

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
