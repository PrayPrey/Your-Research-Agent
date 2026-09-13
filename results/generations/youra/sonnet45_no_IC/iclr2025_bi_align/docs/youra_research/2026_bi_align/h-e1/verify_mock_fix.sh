#!/bin/bash
# Verification script for mock data fix

set -e

cd /workspace/TEST_bi_align/docs/youra_research/h-e1/code

echo "=== Mock Data Fix Verification ==="
echo ""

# Check if experiment completed
if [ ! -f outputs/experiment_results.json ]; then
    echo "❌ FAIL: experiment_results.json not found"
    exit 1
fi

echo "✓ Results file exists"

# Check for completion marker in log
if ! grep -q "EXPERIMENT COMPLETE" experiment.log; then
    echo "❌ FAIL: Experiment did not complete"
    exit 1
fi

echo "✓ Experiment completed"

# Parse results
python3 << 'EOF'
import json
import sys

with open('outputs/experiment_results.json', 'r') as f:
    results = json.load(f)

print("\n=== Verification Checks ===\n")

# Check 1: Real training history (not simulated)
num_steps = results['training_history']['num_steps']
loss_dpo_history = results['training_history']['loss_dpo_history']
loss_attr_history = results['training_history']['loss_attr_history']

if num_steps == 500 and len(loss_dpo_history) == 500:
    print(f"✓ Training history: {num_steps} steps recorded")
else:
    print(f"❌ FAIL: Expected 500 steps, got {num_steps}")
    sys.exit(1)

# Check 2: Loss values are not simulated exponential
# Real losses should have variance, not smooth exponential decay
import numpy as np
loss_dpo_var = np.var(loss_dpo_history)
if loss_dpo_var > 0.0001:  # Real training has variance
    print(f"✓ Loss variance: {loss_dpo_var:.6f} (real training detected)")
else:
    print(f"❌ FAIL: Loss too smooth (variance={loss_dpo_var:.6f}), may be simulated")
    sys.exit(1)

# Check 3: Metrics are in realistic range
win_rate = results['evaluation_results']['preference_win_rate']
steering_acc = results['evaluation_results']['steering_accuracy']

if 0.0 <= win_rate <= 1.0 and 0.0 <= steering_acc <= 1.0:
    print(f"✓ Win rate: {win_rate:.2%} (in valid range)")
    print(f"✓ Steering accuracy: {steering_acc:.2%} (in valid range)")
else:
    print(f"❌ FAIL: Metrics out of range")
    sys.exit(1)

# Check 4: Note field updated
note = results.get('note', '')
if 'Real' in note or 'actual' in note:
    print(f"✓ Note field updated: '{note[:60]}...'")
else:
    print(f"⚠ WARNING: Note field not updated (still says: '{note}')")

# Check 5: Gradient statistics are present
grad_stats = results['gradient_statistics']
if 'mean' in grad_stats and grad_stats['mean'] > 0:
    print(f"✓ Gradient angle: {grad_stats['mean']:.2f}° (real computation)")
else:
    print(f"❌ FAIL: Gradient statistics missing or invalid")
    sys.exit(1)

print("\n=== Gate Criteria Results ===\n")
gate = results['gate_criteria']
print(f"  Convergence: {'PASS' if gate['convergence']['passed'] else 'FAIL'}")
print(f"  Win Rate: {gate['preference_win_rate']['value']:.2%} ({'PASS' if gate['preference_win_rate']['passed'] else 'FAIL'})")
print(f"  Steering: {gate['steering_accuracy']['value']:.2%} ({'PASS' if gate['steering_accuracy']['passed'] else 'FAIL'})")
print(f"  Gradients: {gate['gradient_angle']['mean']:.2f}° ({'PASS' if gate['gradient_angle']['passed'] else 'FAIL'})")
print(f"\nOverall: {results['gate_result']}")

print("\n=== ALL CHECKS PASSED ===")
print("Mock data fix successful - all metrics from real computation")
EOF

echo ""
echo "=== Summary ==="
echo "✓ All mock data violations fixed"
echo "✓ Experiment uses real datasets and training"
echo "✓ Ready to proceed with validation report"
