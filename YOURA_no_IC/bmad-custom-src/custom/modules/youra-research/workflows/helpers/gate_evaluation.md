---
name: 'gate_evaluation'
description: 'Reusable functions for gate evaluation logic in Phase 4 (MUST_WORK) and Phase 5 (DETERMINES_SUCCESS)'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - evaluate_gate
  - determine_gate_outcome
  - get_routing_decision
  - calculate_pass_rate
  - format_gate_report
  - update_gate_status
  - trigger_llm_assessment

# Called By
called_by:
  - 'phase4-coding/steps/step-06-gate-processing.md'
  - 'phase4-coding/steps/step-06b-reflection.md'
  - 'phase5-baseline-repo-comparison/steps/step-10a-gate-evaluation.md'
---

# Gate Evaluation Helper Functions

> Reusable functions for gate evaluation logic in Phase 4 (MUST_WORK) and Phase 5 (DETERMINES_SUCCESS).
> Centralizes gate type definitions, outcome evaluation, and routing decisions.

---

## Constants

### Gate Type Definitions

```python
GATE_TYPES = {
    "MUST_WORK": {
        "phase": 4,
        "description": "Code must execute without critical errors",
        "pass_action": "proceed_to_phase5",
        "fail_action": "route_to_phase0",
        "partial_action": "route_to_phase2a",
        "pass_threshold": 1.0, # 100% tasks must pass
        "partial_threshold": 0.5 # 50%+ for partial
    },
    "SHOULD_WORK": {
        "phase": 4,
        "description": "Optional checks - LLM assessment for SELF_MODIFY or record limitation",
        "pass_action": "continue", # Proceed to next gate
        "fail_action": "record_limitation", # Record limitation, continue
        "partial_action": "self_recovery", # Retry with modifications (no Phase 2A routing)
        "pass_threshold": 1.0, # 100% tasks must pass
        "partial_threshold": 0.5, # 50%+ allows self-recovery attempt
        "max_retries": 3, # Max self-recovery attempts before recording limitation
        "is_optional": True, # Flag for optional gate behavior

        "llm_assessment_available": True, # Can use LLM to decide SELF_MODIFY vs FAIL
        "self_modify_to_phase": "Phase 2C", # If SELF_MODIFY, route to Phase 2C
        "llm_assessment_helper": "llm_self_assessment_should_work.md" # Helper file
    },
    "DETERMINES_SUCCESS": {
        "phase": 5,
        "description": "Results must meet baseline comparison criteria",
        "pass_action": "mark_completed",
        "fail_action": "route_to_phase0",
        "partial_action": "route_to_phase0", # No partial for Phase 5
        "pass_threshold": 1.0,
        "partial_threshold": None # No partial state
    }
}

# Outcome to status mapping
OUTCOME_STATUS_MAP = {
    "PASS": "VALIDATED",
    "FAIL": "FAILED",
    "PARTIAL": "PARTIAL",
    "SUPERSEDED": "SUPERSEDED",
    "RETRYING": "RETRYING", # Self-recovery in progress
    "LIMITATION_RECORDED": "LIMITATION_RECORDED" # Optional gate failed, continuing
}

# | Status | Trigger | Route |
# |---------------------|----------------------------------------------|---------------|
# | VALIDATED | MUST_WORK PASS (100% criteria met) | Phase 5 |
# | PARTIAL | MUST_WORK PARTIAL (50-99% criteria met) | Reflection |
# | SUPERSEDED | Reflection: incompatible with dependents | Phase 2A |
# | FAILED | Gate FAIL or Reflection: unrecoverable | Phase 0 |
# | CASCADE_FAILED | Parent hypothesis FAILED | N/A (done) |
# | CASCADE_SUPERSEDED | Parent hypothesis SUPERSEDED | Await new |
# | RETRYING | SHOULD_WORK PARTIAL - self-recovery attempt | Same step |
# | LIMITATION_RECORDED | SHOULD_WORK FAIL after max retries | Continue |

# Action to route mapping
ACTION_ROUTE_MAP = {
    "proceed_to_phase5": {
        "next_step": "step-05a-pre-validation.md",
        "update_status": "VALIDATED"
    },
    # SHOULD_WORK gate actions
    "continue": {
        "next_step": None, # Continue to next gate in sequence
        "update_status": None, # No status change on pass
        "is_terminal": False
    },
    "record_limitation": {
        "next_step": None, # Continue despite failure
        "update_status": "LIMITATION_RECORDED",
        "is_terminal": False,
        "write_memory": False, # Optional: can log limitation to checkpoint
        "note_template": "SHOULD_WORK gate failed for {hypothesis_id} after {attempts} attempts"
    },
    "self_recovery": {
        "next_step": None, # Retry current step
        "update_status": "RETRYING",
        "is_terminal": False,
        "trigger_reflection": True, # Trigger reflection for self-recovery
        "max_attempts": 3
    },
    "route_to_phase0": {
        "next_phase": "phase0",
        "update_status": "FAILED",
        "write_memory": True,
        "memory_template": "failure_{hypothesis_id}.md"
    },
    "route_to_phase2a": {
        "next_phase": "phase2a-dialogue",
        "update_status": "PARTIAL",
        "write_memory": True,
        "memory_template": "pivot_{hypothesis_id}_{new_hypothesis_id}.md"
    },
    "route_to_phase2a_superseded": {
        "next_phase": "phase2a-dialogue",
        "update_status": "SUPERSEDED",
        "write_memory": True,
        "memory_template": "superseded_{hypothesis_id}.md",
        "create_new_hypothesis": True # Signal to create new hypothesis version
    },
    "mark_completed": {
        "next_step": None,
        "update_status": "COMPLETED"
    }
}
```

---

## Functions

### 1. evaluate_gate

```python
def evaluate_gate(gate_type: str, validation_result: dict) -> dict:
    """
    Evaluate gate based on validation results.

    Args:
        gate_type: "MUST_WORK" or "DETERMINES_SUCCESS"
        validation_result: Dictionary containing:
            - all_passed: bool - All validations passed
            - critical_failure: bool - Unrecoverable failure occurred
            - pass_rate: float - Percentage of passed checks (0.0-1.0)
            - failed_checks: list - List of failed check names
            - error_details: dict - Details about failures

    Returns:
        Dictionary containing:
            - satisfied: bool - Gate requirement met
            - outcome: str - "PASS", "FAIL", or "PARTIAL"
            - action: str - Action to take
            - route_to: str|None - Next step/phase to route to
            - reason: str - Human-readable explanation
            - write_memory: bool - Whether to write Serena memory
            - memory_template: str|None - Memory file template

    Usage:
        result = evaluate_gate("MUST_WORK", {
            "all_passed": False,
            "critical_failure": False,
            "pass_rate": 0.7,
            "failed_checks": ["test_model", "test_training"]
        })
        # Returns: {
        # "satisfied": False,
        # "outcome": "PARTIAL",
        # "action": "route_to_phase2a",
        # "route_to": "phase2a-dialogue",
        # "reason": "70% passed (threshold: 100%)",
        # "write_memory": True,
        # "memory_template": "pivot_{hypothesis_id}_{new_hypothesis_id}.md"
        # }
    """
    gate_config = GATE_TYPES.get(gate_type)
    if not gate_config:
        raise ValueError(f"Unknown gate type: {gate_type}. Valid types: {list(GATE_TYPES.keys())}")

    # Extract validation results
    all_passed = validation_result.get("all_passed", False)
    critical_failure = validation_result.get("critical_failure", False)
    pass_rate = validation_result.get("pass_rate", 0.0)
    failed_checks = validation_result.get("failed_checks", [])

    # Determine outcome
    if all_passed or pass_rate >= gate_config["pass_threshold"]:
        outcome = "PASS"
        action = gate_config["pass_action"]
        satisfied = True
        reason = f"All checks passed ({pass_rate*100:.0f}%)"

    elif critical_failure:
        outcome = "FAIL"
        action = gate_config["fail_action"]
        satisfied = False
        reason = f"Critical failure: {validation_result.get('error_details', {}).get('message', 'Unknown')}"

    elif gate_config["partial_threshold"] and pass_rate >= gate_config["partial_threshold"]:
        outcome = "PARTIAL"
        action = gate_config["partial_action"]
        satisfied = False
        reason = f"Partial success: {pass_rate*100:.0f}% passed (threshold: {gate_config['pass_threshold']*100:.0f}%)"

    else:
        outcome = "FAIL"
        action = gate_config["fail_action"]
        satisfied = False
        reason = f"Failed: {pass_rate*100:.0f}% passed, {len(failed_checks)} checks failed"

    # Get routing info
    route_info = ACTION_ROUTE_MAP.get(action, {})

    return {
        "satisfied": satisfied,
        "outcome": outcome,
        "action": action,
        "route_to": route_info.get("next_step") or route_info.get("next_phase"),
        "update_status": route_info.get("update_status"),
        "reason": reason,
        "write_memory": route_info.get("write_memory", False),
        "memory_template": route_info.get("memory_template"),
        "failed_checks": failed_checks
    }
```

### 2. update_gate_status

```python
def update_gate_status(
    verification_state: dict,
    hypothesis_id: str,
    gate_result: dict,
    verification_state_path: str
) -> dict:
    """
    Update verification_state.yaml with gate evaluation results.

    Args:
        verification_state: Current verification state dictionary
        hypothesis_id: Hypothesis ID (e.g., "h-e1")
        gate_result: Result from evaluate_gate()
        verification_state_path: Path to verification_state.yaml

    Returns:
        Updated verification_state dictionary

    Usage:
        gate_result = evaluate_gate("MUST_WORK", validation_result)
        verification_state = update_gate_status(
            verification_state,
            "h-e1",
            gate_result,
            verification_state_path
        )
    """
    h_id = hypothesis_id.lower()
    h_data = verification_state.get("sub_hypotheses", {}).get(h_id, {})

    # Update gate information
    h_data["gate"] = {
        "type": h_data.get("gate", {}).get("type", "MUST_WORK"),
        "satisfied": gate_result["satisfied"],
        "outcome": gate_result["outcome"],
        "reason": gate_result["reason"],
        "evaluated_at": datetime.now().isoformat()
    }

    # Update hypothesis status
    if gate_result.get("update_status"):
        h_data["status"] = gate_result["update_status"]

    # Store failed checks for reference
    if gate_result.get("failed_checks"):
        h_data["gate"]["failed_checks"] = gate_result["failed_checks"]

    # Update validation section
    # This tracks the Phase 4 validation status separately from gate evaluation
    h_data["validation"] = {
        "status": "COMPLETED", # Phase 4 validation complete
        "result": gate_result["outcome"], # PASS, PARTIAL, or FAIL
        "completed_at": datetime.now().isoformat()
    }

    verification_state["sub_hypotheses"][h_id] = h_data

    # Save
    write_yaml(verification_state_path, verification_state)

    return verification_state
```

### 3. get_gate_routing

```python
def get_gate_routing(gate_result: dict, hypothesis_id: str = None) -> dict:
    """
    Get routing information based on gate result.

    Args:
        gate_result: Result from evaluate_gate()
        hypothesis_id: Optional hypothesis ID for memory file naming

    Returns:
        Dictionary containing:
            - next_step: str|None - Next step file to load
            - next_phase: str|None - Next phase to route to
            - memory_file: str|None - Memory file to write (if applicable)
            - status_update: str - Status to set

    Usage:
        routing = get_gate_routing(gate_result, "h-e1")
        if routing["next_step"]:
            Load, read, execute: routing["next_step"]
        elif routing["next_phase"]:
            Route to: routing["next_phase"]
    """
    action = gate_result.get("action")
    route_info = ACTION_ROUTE_MAP.get(action, {})

    result = {
        "next_step": route_info.get("next_step"),
        "next_phase": route_info.get("next_phase"),
        "status_update": route_info.get("update_status"),
        "memory_file": None
    }

    # Generate memory file name if needed
    if route_info.get("write_memory") and hypothesis_id:
        template = route_info.get("memory_template", "")
        result["memory_file"] = template.format(
            hypothesis_id=hypothesis_id,
            new_hypothesis_id=f"{hypothesis_id}-v2" # Default naming
        )

    return result
```

### 4. calculate_pass_rate

```python
def calculate_pass_rate(validation_results: list) -> dict:
    """
    Calculate pass rate from list of validation results.

    Args:
        validation_results: List of validation check results, each containing:
            - name: str - Check name
            - passed: bool - Whether check passed
            - critical: bool - Whether failure is critical

    Returns:
        Dictionary containing:
            - all_passed: bool
            - critical_failure: bool
            - pass_rate: float (0.0-1.0)
            - passed_count: int
            - failed_count: int
            - failed_checks: list of failed check names

    Usage:
        results = [
            {"name": "test_model", "passed": True, "critical": False},
            {"name": "test_training", "passed": False, "critical": False},
            {"name": "test_import", "passed": False, "critical": True}
        ]
        summary = calculate_pass_rate(results)
        # Returns: {
        # "all_passed": False,
        # "critical_failure": True,
        # "pass_rate": 0.33,
        # "passed_count": 1,
        # "failed_count": 2,
        # "failed_checks": ["test_training", "test_import"]
        # }
    """
    if not validation_results:
        # BUG FIX: Empty results means validation was skipped/incomplete
        # Previously returned all_passed=True which caused skipped experiments to PASS
        return {
            "all_passed": False, # FIX: No validation = NOT passed
            "critical_failure": False,
            "pass_rate": 0.0, # FIX: No validation = 0% pass rate
            "passed_count": 0,
            "failed_count": 0,
            "failed_checks": [],
            "no_validation_data": True # NEW: Flag indicating missing validation data
        }

    passed = [r for r in validation_results if r.get("passed", False)]
    failed = [r for r in validation_results if not r.get("passed", False)]
    critical_failures = [r for r in failed if r.get("critical", False)]

    return {
        "all_passed": len(failed) == 0,
        "critical_failure": len(critical_failures) > 0,
        "pass_rate": len(passed) / len(validation_results) if validation_results else 1.0,
        "passed_count": len(passed),
        "failed_count": len(failed),
        "failed_checks": [r.get("name", "unknown") for r in failed]
    }
```

### 5. get_superseded_routing

```python
def get_superseded_routing(hypothesis_id: str, new_hypothesis_id: str, reason: str) -> dict:
    """
    Get routing information for SUPERSEDED outcome.

     NEW: Called after LLM self-assessment determines that PARTIAL results
    are incompatible with dependent hypotheses and need Phase 2A redesign.

    This is different from regular PARTIAL routing:
    - PARTIAL (route_to_phase2a): Self-modification possible, same hypothesis ID
    - SUPERSEDED (route_to_phase2a_superseded): New hypothesis version needed

    Args:
        hypothesis_id: Original hypothesis ID (e.g., "h-e1")
        new_hypothesis_id: New hypothesis version ID (e.g., "h-e1-v2")
        reason: Reason for superseding from LLM self-assessment

    Returns:
        Dictionary containing:
            - action: "route_to_phase2a_superseded"
            - route_to: "phase2a"
            - update_status: "SUPERSEDED"
            - memory_file: str - Memory file to write
            - new_hypothesis_id: str - New hypothesis version ID
            - superseded_info: dict - SUPERSEDED metadata

    Usage:
        # After LLM self-assessment determines incompatibility
        if not compatible_with_dependents:
            routing = get_superseded_routing(
                hypothesis_id="h-e1",
                new_hypothesis_id="h-e1-v2",
                reason="Interface outputs incompatible with H-M1 expected inputs"
            )

            # Update verification_state
            verification_state["sub_hypotheses"][hypothesis_id]["status"] = "SUPERSEDED"
            verification_state["sub_hypotheses"][hypothesis_id]["superseded"] = routing["superseded_info"]

            # Write Serena memory
            mcp__serena__write_memory(routing["memory_file"], superseded_record)

            # Handle cascade
            from archon_cascade import mark_hypothesis_superseded, mark_dependent_tasks_cascade_superseded
    """
    route_info = ACTION_ROUTE_MAP.get("route_to_phase2a_superseded", {})
    timestamp = datetime.now().isoformat()

    return {
        "action": "route_to_phase2a_superseded",
        "route_to": route_info.get("next_phase", "phase2a-dialogue"),
        "update_status": route_info.get("update_status", "SUPERSEDED"),
        "memory_file": route_info.get("memory_template", "superseded_{}.md").format(hypothesis_id),
        "new_hypothesis_id": new_hypothesis_id,
        "create_new_hypothesis": route_info.get("create_new_hypothesis", True),
        "superseded_info": {
            "superseded_by": new_hypothesis_id,
            "superseded_at": timestamp,
            "superseded_reason": reason,
            "partial_results_preserved": True
        }
    }
```

---

