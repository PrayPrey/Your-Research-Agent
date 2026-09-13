"""Update verification_state.yaml with h-m2 Phase 4 results."""

import json
import yaml
import os
from datetime import datetime

def update_verification_state(results_path, state_path):
    """
    Update verification_state.yaml with Phase 4 validation results.

    Args:
        results_path: Path to experiment_results.json
        state_path: Path to verification_state.yaml
    """
    # Load experiment results
    with open(results_path, 'r') as f:
        results = json.load(f)

    # Load verification state
    with open(state_path, 'r') as f:
        state = yaml.safe_load(f)

    # Extract key metrics
    diversity_test = results['diversity_test']
    gate_pass = results['gate_pass']

    # Update h-m2 validation section
    if 'hypotheses' not in state:
        state['hypotheses'] = {}

    if 'h-m2' not in state['hypotheses']:
        state['hypotheses']['h-m2'] = {}

    state['hypotheses']['h-m2']['validation'] = {
        'status': 'COMPLETED',
        'result': 'PASS' if gate_pass else 'FAIL',
        'gate_result': 'PASS' if gate_pass else 'FAIL',
        'completed_at': datetime.now().isoformat(),
        'metrics': {
            'nq_diversity_mean': diversity_test['mean1'],
            'tqa_diversity_mean': diversity_test['mean2'],
            'diversity_pvalue': diversity_test['p_value'],
            'diversity_significant': diversity_test['p_value'] < 0.05,
            'correct_direction': diversity_test['mean1'] > diversity_test['mean2']
        },
        'gate_evaluation': {
            'type': 'SHOULD_WORK',
            'condition': '(p < 0.05) AND (NQ diversity > TQA diversity)',
            'passed': gate_pass
        }
    }

    # Update overall status
    state['hypotheses']['h-m2']['status'] = 'COMPLETED'
    state['hypotheses']['h-m2']['completed'] = True

    # Add history event
    if 'history' not in state:
        state['history'] = []

    state['history'].append({
        'event': 'Phase 4 completed for h-m2',
        'phase': 'Phase 4',
        'hypothesis_id': 'h-m2',
        'timestamp': datetime.now().isoformat(),
        'details': f"Validation {'PASS' if gate_pass else 'FAIL'} - Diversity p-value: {diversity_test['p_value']:.6f}"
    })

    # Save updated state
    with open(state_path, 'w') as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

    print(f"Updated verification_state.yaml")
    print(f"  Status: {'PASS' if gate_pass else 'FAIL'}")
    print(f"  NQ diversity: {diversity_test['mean1']:.4f}")
    print(f"  TQA diversity: {diversity_test['mean2']:.4f}")
    print(f"  p-value: {diversity_test['p_value']:.6f}")


if __name__ == "__main__":
    results_path = "results/experiment_results.json"
    state_path = "../../verification_state.yaml"

    if os.path.exists(results_path):
        update_verification_state(results_path, state_path)
    else:
        print(f"Results file not found: {results_path}")
        print("Run the experiment first: python main.py")
