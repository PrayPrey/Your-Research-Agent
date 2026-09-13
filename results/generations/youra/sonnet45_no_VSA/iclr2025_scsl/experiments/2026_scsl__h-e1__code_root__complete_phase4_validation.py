#!/usr/bin/env python3
"""
Complete Phase 4 Validation for H-E1
Waits for experiments, generates validation report, updates state files
"""
import os
import sys
import time
import json
import yaml
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configuration
EXPERIMENT_PID = 3146982
BASE_DIR = Path("/workspace/TEST_scsl")
EXPERIMENT_DIR = BASE_DIR / "experiments/h-e1"
DOCS_DIR = BASE_DIR / "docs/youra_research"
LOG_FILE = EXPERIMENT_DIR / "experiment_full.log"
RESULTS_FILE = EXPERIMENT_DIR / "outputs/h-e1/results.csv"
VALIDATION_FILE = EXPERIMENT_DIR / "outputs/h-e1/04_validation.md"

os.chdir(EXPERIMENT_DIR)
sys.path.insert(0, str(EXPERIMENT_DIR))

def log(msg: str):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def wait_for_experiments():
    """Wait for experiment process to complete"""
    log(f"Waiting for experiments (PID {EXPERIMENT_PID}) to complete...")

    wait_count = 0
    while psutil.pid_exists(EXPERIMENT_PID):
        time.sleep(60)
        wait_count += 1

        if wait_count % 5 == 0:
            # Report progress every 5 minutes
            try:
                with open(LOG_FILE) as f:
                    content = f.read()
                    import re
                    experiments = re.findall(r'Experiment (\d+)/15', content)
                    if experiments:
                        log(f"Still running... Progress: Experiment {experiments[-1]}/15")
            except Exception as e:
                log(f"Could not read progress: {e}")

    log("✓ Experiment process completed!")
    time.sleep(5)  # Wait for file writes

def generate_validation_report() -> Dict[str, Any]:
    """Generate validation report and return gate result"""
    log("Generating validation report...")

    if not RESULTS_FILE.exists():
        log(f"✗ ERROR: Results file not found at {RESULTS_FILE}")
        sys.exit(1)

    # Import evaluate module
    from evaluate import generate_validation_report as gen_report

    try:
        result = gen_report(
            results_csv=str(RESULTS_FILE),
            output_dir=str(EXPERIMENT_DIR / "outputs/h-e1"),
            hypothesis_id="h-e1"
        )

        log(f"✓ Validation report generated!")
        log(f"  Gate result: {result['gate_result']}")
        log(f"  Report file: {result['validation_report']}")

        return result
    except Exception as e:
        log(f"✗ ERROR generating validation report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def copy_validation_to_docs(validation_result: Dict[str, Any]):
    """Copy validation report to docs folder"""
    src = Path(validation_result['validation_report'])
    dst = DOCS_DIR / "04_validation.md"

    if src.exists():
        import shutil
        shutil.copy2(src, dst)
        log(f"✓ Copied validation report to {dst}")
    else:
        log(f"✗ WARNING: Could not find validation report at {src}")

def update_checkpoint(validation_result: Dict[str, Any]):
    """Update 04_checkpoint.yaml"""
    checkpoint_file = DOCS_DIR / "h-e1" / "04_checkpoint.yaml"

    # Create new checkpoint
    checkpoint = {
        'current_hypothesis': 'h-e1',
        'current_phase': 'Phase 4',
        'current_step': 'Step 06 (Validation Complete)',
        'phase_4_started': True,
        'phase_4_status': 'COMPLETED',
        'coding_status': 'VALIDATION_COMPLETE',
        'deliverables_complete': [
            '02c_experiment_brief_h_e1.md (681 lines, 26.7 KB)',
            '03_prd.md (646 lines, 26.7 KB)',
            '03_architecture.md (352 lines, 11 KB)',
            '03_logic.md (838 lines, 25 KB)',
            '03_config.md (493 lines, 14 KB)',
            '04_validation.md'
        ],
        'experiments_launched_at': '2026-07-10T19:35:08Z',
        'experiments_completed_at': datetime.now().isoformat(),
        'ready_for_validation': True,
        'gate_result': validation_result['gate_result'],
        'gate_satisfied': validation_result['gate_result'] == 'PASS',
        'validation_report': str(validation_result['validation_report']),
        'canonical_deliverable_path': str(DOCS_DIR / "02c_experiment_brief_h_e1.md"),
        'next_phase': determine_next_phase(validation_result['gate_result']),
        'next_action': determine_next_action(validation_result['gate_result']),
        'serena_memory': {
            'memory_written': False,
            'written_at': None,
            'memory_file': None
        },
        'reflection_outcome': determine_reflection_outcome(validation_result['gate_result'])
    }

    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_file, 'w') as f:
        yaml.dump(checkpoint, f, default_flow_style=False, sort_keys=False)

    log(f"✓ Updated checkpoint: {checkpoint_file}")
    return checkpoint

def determine_next_phase(gate_result: str) -> str:
    if gate_result == 'PASS':
        return 'Phase 4 (Next Hypothesis H-M1)'
    elif gate_result == 'PARTIAL':
        return 'Phase 2A (Hypothesis Refinement)'
    else:  # FAIL
        return 'Phase 0 (Approach Revision)'

def determine_next_action(gate_result: str) -> str:
    if gate_result == 'PASS':
        return 'Proceed to H-M1 (mechanism hypothesis)'
    elif gate_result == 'PARTIAL':
        return 'Route to Phase 2A-Dialogue for hypothesis refinement'
    else:  # FAIL
        return 'Route to Phase 0 for fundamental approach revision'

def determine_reflection_outcome(gate_result: str) -> str:
    if gate_result == 'PASS':
        return 'COMPLETED_SUCCESS'
    elif gate_result == 'PARTIAL':
        return 'PARTIAL_SUCCESS_ROUTED_TO_PHASE_2A'
    else:
        return 'FAILED_ROUTED_TO_PHASE_0'

def create_state_restatement(validation_result: Dict[str, Any], checkpoint: Dict[str, Any]):
    """Create the state restatement block required by ablation mode"""
    state_file = EXPERIMENT_DIR / "state_restatement.md"

    gate_satisfied = validation_result['gate_result'] == 'PASS'

    content = f"""# State Restatement for H-E1

This file contains the updated state that should be returned to the user.

```state
sub_hypotheses:
  h-e1:
    validation:
      status: COMPLETED
      result: "{validation_result['gate_result']} - {validation_result.get('summary', 'Validation complete')}"
      completed_at: '{datetime.now().isoformat()}'
      report_file: '04_validation.md'
    gate:
      type: MUST_WORK
      satisfied: {str(gate_satisfied).lower()}
    reflection_outcome: {checkpoint['reflection_outcome']}
    completed: {str(gate_satisfied).lower()}
    completed_at: '{datetime.now().isoformat()}' if gate_satisfied else null

checkpoint:
{yaml.dump(checkpoint, default_flow_style=False, sort_keys=False)}
```

## Summary

- **Gate Result**: {validation_result['gate_result']}
- **Gate Satisfied**: {gate_satisfied}
- **Validation Status**: COMPLETED
- **Next Phase**: {checkpoint['next_phase']}
- **Next Action**: {checkpoint['next_action']}
"""

    with open(state_file, 'w') as f:
        f.write(content)

    log(f"✓ Created state restatement: {state_file}")
    return content

def main():
    log("="*60)
    log("Phase 4 Validation Completion Script")
    log("="*60)

    # Step 1: Wait for experiments
    wait_for_experiments()

    # Step 2: Generate validation report
    validation_result = generate_validation_report()

    # Step 3: Copy to docs folder
    copy_validation_to_docs(validation_result)

    # Step 4: Update checkpoint
    checkpoint = update_checkpoint(validation_result)

    # Step 5: Create state restatement
    state_content = create_state_restatement(validation_result, checkpoint)

    # Step 6: Create completion marker
    completion_file = EXPERIMENT_DIR / "VALIDATION_COMPLETE.marker"
    with open(completion_file, 'w') as f:
        json.dump({
            'completed_at': datetime.now().isoformat(),
            'gate_result': validation_result['gate_result'],
            'validation_report': validation_result['validation_report'],
            'checkpoint_updated': True,
            'state_restatement_created': True
        }, f, indent=2)

    log("="*60)
    log("✓ PHASE 4 VALIDATION COMPLETE")
    log(f"  Gate Result: {validation_result['gate_result']}")
    log(f"  Next Phase: {checkpoint['next_phase']}")
    log("="*60)

    # Print state restatement to stdout for capture
    print("\n" + state_content)

if __name__ == "__main__":
    main()
