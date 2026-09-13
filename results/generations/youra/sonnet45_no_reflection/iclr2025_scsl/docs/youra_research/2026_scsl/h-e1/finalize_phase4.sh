#!/bin/bash
# Finalize Phase 4 after experiment completion

set -e

echo "========================================"
echo "Phase 4 Finalization: h-e1"
echo "========================================"
echo ""

# Check if experiment completed
if [ ! -f "results/gate_validation.json" ]; then
    echo "ERROR: Gate validation not found. Experiment may not have completed."
    echo "Check experiment.log for errors."
    exit 1
fi

echo "✓ Experiment completed"
echo ""

# Generate validation report
echo "Generating validation report..."
python3 generate_validation_report.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to generate validation report"
    exit 1
fi
echo "✓ Validation report generated: 04_validation.md"
echo ""

# Update verification state
echo "Updating verification_state.yaml..."
cd /home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_scsl_sonnet45_no_reflection/docs/youra_research/20260512_scsl/h-e1
python3 update_verification_state.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to update verification state"
    exit 1
fi
echo "✓ Verification state updated"
echo ""

# Display gate result
echo "========================================"
echo "Gate Validation Result"
echo "========================================"
cat results/gate_validation.json | python3 -m json.tool
echo ""

# Check if gate passed
GATE_PASS=$(python3 -c "import json; print(json.load(open('results/gate_validation.json'))['gate_pass'])")

if [ "$GATE_PASS" = "True" ]; then
    echo "✓✓✓ GATE PASSED ✓✓✓"
    echo ""
    echo "Next Steps:"
    echo "  1. Review 04_validation.md"
    echo "  2. Proceed to Phase 5 (Baseline Comparison)"
    echo "  3. Run hypothesis-next skill for next hypothesis"
else
    echo "✗✗✗ GATE FAILED ✗✗✗"
    echo ""
    echo "Next Steps:"
    echo "  1. Review 04_validation.md for failure analysis"
    echo "  2. Pipeline should stop (MUST_WORK gate)"
    echo "  3. Consider pivot to alternative methods"
fi

echo ""
echo "========================================"
echo "Phase 4 Complete"
echo "========================================"
