#!/usr/bin/env python3
"""
Update verification_state.yaml with h-m2 validation results
"""

import json
import yaml
from pathlib import Path
from datetime import datetime

def update_verification_state():
    """Update verification_state.yaml with Phase 4 results"""

    # Load experiment results
    results_file = Path("code/outputs/experiment_results.json")
    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        return False

    with open(results_file) as f:
        results = json.load(f)

    # Load verification_state
    vs_file = Path("../verification_state.yaml")
    with open(vs_file) as f:
        state = yaml.safe_load(f)

    # Update h-m2 status
    h_m2 = state["sub_hypotheses"]["h-m2"]

    # Extract gate result
    gate_result = results["gate"]["gate_result"]
    gate_satisfied = results["gate"]["all_passed"]
    correlation = results["correlation"]

    # Update validation section
    h_m2["validation"] = {
        "status": "COMPLETED",
        "result": gate_result,
        "key_findings": [
            f"Fairness-Reliability correlation: r={correlation['r']:.4f}, p={correlation['p_value']:.6f}",
            f"95% CI: [{correlation['ci_lower']:.4f}, {correlation['ci_upper']:.4f}]",
            f"Gate type: {results['gate']['gate_type']}",
            f"Gate result: {gate_result}",
            "HONEST bias metric implemented with demographic augmentation",
            f"Sample size: {correlation['n']} prompts"
        ]
    }

    # Update gate
    h_m2["gate"]["satisfied"] = gate_satisfied
    if not gate_satisfied:
        h_m2["gate"]["failed_checks"] = [
            check for check, passed in results["gate"]["checks"].items() if not passed
        ]

    # Update status
    h_m2["status"] = "COMPLETED"
    h_m2["completed"] = True
    h_m2["completed_at"] = datetime.now().isoformat()

    # Add history event
    state["history"].append({
        "event": "Hypothesis h-m2 validated",
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 4",
        "hypothesis_id": "h-m2",
        "gate_result": gate_result,
        "output_file": "docs/youra_research/h-m2/04_validation.md"
    })

    # Update statistics
    state["statistics"]["validated_sub_hypotheses"] = len([
        h for h in state["sub_hypotheses"].values()
        if h.get("validation", {}).get("status") == "COMPLETED"
    ])
    state["statistics"]["phases_completed"]["phase_4"] += 1

    # Save updated state
    with open(vs_file, "w") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print("✅ verification_state.yaml updated")
    print(f"   h-m2 status: COMPLETED")
    print(f"   Gate result: {gate_result}")
    print(f"   Gate satisfied: {gate_satisfied}")

    return True

if __name__ == "__main__":
    success = update_verification_state()
    exit(0 if success else 1)
