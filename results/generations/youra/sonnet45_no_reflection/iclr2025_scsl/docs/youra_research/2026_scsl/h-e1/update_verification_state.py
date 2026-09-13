#!/usr/bin/env python3
"""Update verification_state.yaml with Phase 4 results."""
import yaml
import json
from datetime import datetime
from pathlib import Path


def load_gate_results():
    """Load gate validation results."""
    gate_path = Path("results/gate_validation.json")
    if gate_path.exists():
        with open(gate_path, 'r') as f:
            return json.load(f)
    return None


def update_verification_state(gate_results):
    """Update verification_state.yaml with validation results."""
    state_path = Path("../verification_state.yaml")

    if not state_path.exists():
        print(f"ERROR: {state_path} not found")
        return False

    # Load current state
    with open(state_path, 'r') as f:
        state = yaml.safe_load(f)

    # Update h-e1 validation section
    gate_pass = gate_results.get('gate_pass', False)

    state['sub_hypotheses']['h-e1']['validation'] = {
        'status': 'COMPLETED',
        'result': 'PASS' if gate_pass else 'FAIL',
        'validation_file': str(Path('h-e1/04_validation.md').absolute()),
        'gate_metrics': {
            'sr_reduction': float(gate_results.get('sr_reduction', 0)),
            'ppl_deviation': float(gate_results.get('ppl_deviation', 0)),
            'layer_variance': float(gate_results.get('layer_variance', 0)),
            'measurement_cv': float(gate_results.get('measurement_cv', 0))
        },
        'completed_at': datetime.now().isoformat()
    }

    # Update gate satisfaction
    state['sub_hypotheses']['h-e1']['gate']['satisfied'] = gate_pass

    # Update status
    if gate_pass:
        state['sub_hypotheses']['h-e1']['status'] = 'COMPLETED'
        state['sub_hypotheses']['h-e1']['completed'] = True
    else:
        state['sub_hypotheses']['h-e1']['status'] = 'FAILED'
        state['sub_hypotheses']['h-e1']['completed'] = False

    # Update statistics
    if gate_pass:
        state['statistics']['completed_hypotheses'] = state['statistics'].get('completed_hypotheses', 0) + 1
        state['statistics']['in_progress_sub_hypotheses'] = max(0, state['statistics'].get('in_progress_sub_hypotheses', 1) - 1)
    else:
        state['statistics']['failed_hypotheses'] = state['statistics'].get('failed_hypotheses', 0) + 1
        state['statistics']['in_progress_sub_hypotheses'] = max(0, state['statistics'].get('in_progress_sub_hypotheses', 1) - 1)

    # Update phase status
    state['phases']['phase4_validation']['status'] = 'COMPLETED'
    state['phases']['phase4_validation']['completed_at'] = datetime.now().strftime('%Y-%m-%d')

    # Add history entry
    state['history'].append({
        'event': 'Phase 4 validation completed',
        'timestamp': datetime.now().isoformat(),
        'phase': 'Phase 4',
        'hypothesis_id': 'h-e1',
        'gate_result': 'PASS' if gate_pass else 'FAIL',
        'output_file': str(Path('h-e1/04_validation.md').absolute())
    })

    # Update last_updated
    state['metadata']['last_updated'] = datetime.now().isoformat()

    # Save updated state
    with open(state_path, 'w') as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Updated {state_path}")
    print(f"  Gate Result: {'PASS' if gate_pass else 'FAIL'}")
    print(f"  Status: {state['sub_hypotheses']['h-e1']['status']}")

    return True


def main():
    """Main entry point."""
    print("Loading gate validation results...")
    gate_results = load_gate_results()

    if gate_results is None:
        print("ERROR: Gate validation results not found.")
        print("Run the experiment first: python code/run_experiment.py")
        return False

    print("Updating verification_state.yaml...")
    success = update_verification_state(gate_results)

    if success:
        print("\n✓ Verification state updated successfully")
        gate_pass = gate_results.get('gate_pass', False)
        if gate_pass:
            print("  → Next: Proceed to Phase 5 (Baseline Comparison)")
        else:
            print("  → Next: Pipeline Stop (Gate Failed)")
    else:
        print("\n✗ Failed to update verification state")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
