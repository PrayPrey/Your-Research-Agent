#!/usr/bin/env bash
#
# Phase 4 Finalization Script for h-m2
# Generates validation report and updates verification_state.yaml
#

set -euo pipefail

echo "=== Phase 4 Finalization for h-m2 ==="
echo "Started: $(date -Iseconds)"
echo ""

# Check if experiment completed
if ! grep -q "EXPERIMENT COMPLETE" code/experiment.log 2>/dev/null; then
    echo "❌ Experiment did not complete successfully"
    echo "Check code/experiment.log for details"
    exit 1
fi

echo "✓ Experiment completed"
echo ""

# Check for results file
if [ ! -f "code/outputs/experiment_results.json" ]; then
    echo "❌ Results file not found: code/outputs/experiment_results.json"
    exit 1
fi

echo "✓ Results file found"
echo ""

# Generate validation report
echo "📝 Generating validation report..."
python3 generate_validation_report.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate validation report"
    exit 1
fi

echo "✓ Validation report generated: 04_validation.md"
echo ""

# Update verification_state.yaml
echo "📊 Updating verification_state.yaml..."
python3 update_verification_state.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to update verification_state.yaml"
    exit 1
fi

echo "✓ verification_state.yaml updated"
echo ""

# Display results summary
echo "=== Results Summary ==="
python3 << 'PYTHON_EOF'
import json

with open("code/outputs/experiment_results.json") as f:
    results = json.load(f)

correlation = results["correlation"]
gate = results["gate"]

print(f"Gate Type: {gate['gate_type']}")
print(f"Gate Result: {gate['gate_result']}")
print(f"")
print(f"Correlation (Fairness-Reliability):")
print(f"  r = {correlation['r']:.4f}")
print(f"  p-value = {correlation['p_value']:.6f}")
print(f"  95% CI = [{correlation['ci_lower']:.4f}, {correlation['ci_upper']:.4f}]")
print(f"  n = {correlation['n']}")
print(f"")
print(f"Gate Checks:")
for check, passed in gate['checks'].items():
    status = "✅" if passed else "❌"
    print(f"  {status} {check}")
print(f"")
print(f"Overall: {'✅ PASS - All criteria met' if gate['all_passed'] else '❌ FAIL - Some criteria not met'}")
PYTHON_EOF

echo ""
echo "=== Phase 4 Complete ==="
echo "Finished: $(date -Iseconds)"
echo ""
echo "Output files:"
echo "  - 04_validation.md (validation report)"
echo "  - code/outputs/experiment_results.json (raw results)"
echo "  - code/outputs/results.csv (raw data)"
echo "  - code/figures/*.png (3 figures)"
echo ""
echo "Next step: Phase 5 baseline comparison (/phase5-baseline-comparison)"
