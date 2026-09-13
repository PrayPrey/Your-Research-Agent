#!/usr/bin/env python3
"""Quick verification that real dataset loads correctly"""

import sys
sys.path.insert(0, '/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code')

from run_experiment import load_dataset

print("Testing dataset loading...")
factual_data, misinfo_data = load_dataset()

print(f"\n✓ Dataset loaded successfully")
print(f"Factual samples: {len(factual_data['questions'])}")
print(f"Misinformation samples: {len(misinfo_data['questions'])}")

if len(factual_data['questions']) > 0:
    print(f"\nSample factual question: {factual_data['questions'][0][:100]}...")

if len(misinfo_data['questions']) > 0:
    print(f"Sample misinfo question: {misinfo_data['questions'][0][:100]}...")

# Verify this is real data, not synthetic
if any("factual_q_" in q for q in factual_data['questions']):
    print("\n❌ ERROR: Synthetic data detected (factual_q_* pattern found)")
    sys.exit(1)

if any("misinfo_q_" in q for q in misinfo_data['questions']):
    print("\n❌ ERROR: Synthetic data detected (misinfo_q_* pattern found)")
    sys.exit(1)

print("\n✅ Verification passed: Real TruthfulQA data loaded")
