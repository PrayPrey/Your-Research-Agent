#!/bin/bash
# Post-experiment finalization: report generation + gate verdict extraction

set -e

echo "Checking experiment completion..."

if ! grep -q "EXPERIMENT COMPLETE" experiment_full.log; then
    echo "ERROR: Experiment did not complete successfully"
    exit 1
fi

echo "Experiment complete. Generating report..."

python3 generate_report.py > report_generation.log 2>&1

if [ $? -eq 0 ]; then
    echo "Report generated successfully"
    echo "Gate verdict:"
    tail -1 report_generation.log
    echo ""
    echo "Full report available at: ../04_validation.md"
    echo "Results data: ../results/convergence_data.csv"
    echo "Figures: ../figures/convergence_comparison.png"
else
    echo "ERROR: Report generation failed"
    exit 1
fi

echo "Phase 4 validation complete."
