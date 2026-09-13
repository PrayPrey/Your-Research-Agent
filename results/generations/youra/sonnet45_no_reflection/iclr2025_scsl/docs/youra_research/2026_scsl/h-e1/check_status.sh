#!/bin/bash
# Check experiment status and display key information

echo "=================================="
echo "H-E1 Experiment Status Check"
echo "=================================="
echo ""

# Check if experiment is running
if pgrep -f "run_experiment.py" > /dev/null; then
    echo "✓ Experiment is RUNNING"
    echo ""
else
    echo "✗ Experiment is NOT running (completed or failed)"
    echo ""
fi

# Check log file
if [ -f "experiment.log" ]; then
    echo "Log file size: $(du -h experiment.log | cut -f1)"
    echo ""
    echo "Last 20 lines of log:"
    echo "---"
    tail -n 20 experiment.log
    echo "---"
    echo ""
else
    echo "✗ No experiment.log found"
    echo ""
fi

# Check results
echo "Results files:"
if [ -d "results" ]; then
    ls -lh results/ 2>/dev/null || echo "  (empty)"
else
    echo "  (results directory not created yet)"
fi
echo ""

# Check checkpoints
echo "Checkpoint directories:"
if [ -d "checkpoints" ]; then
    find checkpoints -name "*.pt" -o -name "*.json" 2>/dev/null | head -10
else
    echo "  (checkpoints directory not created yet)"
fi
echo ""

# Check for gate validation
if [ -f "results/gate_validation.json" ]; then
    echo "✓ Gate validation completed"
    echo ""
    echo "Gate result:"
    cat results/gate_validation.json
else
    echo "✗ Gate validation not yet completed"
fi

echo ""
echo "=================================="
