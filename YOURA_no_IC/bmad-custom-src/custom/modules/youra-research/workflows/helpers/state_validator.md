---
name: 'state_validator'
description: 'Validation and recovery system for verification_state.yaml across all phases'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - validate_and_load_state
  - validate_required_fields
  - validate_hypothesis_fields
  - validate_archon_sync
  - validate_prerequisites
  - full_state_validation
  - apply_auto_fixes
  - validate_full_state_consistency
  - auto_fix_state_consistency

# Called By
called_by:
  - 'phase4-coding/steps/step-01-initialize.md'
  - 'phase5-baseline-repo-comparison/steps/step-01-init.md'
  - 'hypothesis-loop/instructions.md'
  - 'hypothesis-next/instructions.md'
---

# State Validator Helper Functions

> Validation and recovery system for verification_state.yaml across all phases.
> Detects format errors, missing fields, inconsistent state, and auto-recovers where possible.

---

## Constants

### State Format

```python
CURRENT_SCHEMA_VERSION = "3.5"

SUPPORTED_VERSIONS = ["3.0", "3.1", "3.2", "3.5"]
```

### Required Fields

```python
# Top-level required sections
REQUIRED_SECTIONS = [
    "metadata",
    "main_hypothesis",
    "episode",
    "workflow",
    "sub_hypotheses",
    "statistics"
]

# Metadata required fields
REQUIRED_METADATA_FIELDS = [
    "project_name",
    "main_hypothesis_id",
    "created_at",
    "last_updated",
    "schema_version",
    "pipeline_project_id",
    "hypothesis_task_mapping"
]

# Main hypothesis required fields
REQUIRED_MAIN_HYPOTHESIS_FIELDS = [
    "id",
    "title",
    "statement",
    "defined_in",
    "baseline_comparison"
]

# Sub-hypothesis required fields
REQUIRED_SUB_HYPOTHESIS_FIELDS = [
    "type",
    "statement",
    "status",
    "gate",
    "prerequisites",
    "experiment_design",
    "implementation_planning",
    "validation"
]

# Valid status values
VALID_HYPOTHESIS_STATUSES = [
    "NOT_STARTED",
    "READY",
    "IN_PROGRESS",
    "COMPLETED",
    "VALIDATED",
    "BLOCKED",
    "CASCADE_FAILED",
    "CASCADE_SUPERSEDED",
    "SUPERSEDED",
    "FAILED"
]

# Valid gate types
VALID_GATE_TYPES = ["MUST_WORK", "SHOULD_WORK", "DETERMINES_SUCCESS"]

# Valid gate outcomes
VALID_GATE_OUTCOMES = ["PASS", "PARTIAL", "FAIL"]

# Valid workflow statuses
VALID_WORKFLOW_STATUSES = ["ACTIVE", "STOPPED", "COMPLETED", "FAILED"]
```

### Auto-Fix Defaults

```python
# Default values for missing fields (used in auto-fix)
AUTO_FIX_DEFAULTS = {
    "metadata.schema_version": CURRENT_SCHEMA_VERSION,
    "metadata.pipeline_project_id": None,
    "metadata.hypothesis_task_mapping": {},

    "main_hypothesis.baseline_comparison.status": "NOT_STARTED",

    "episode.status": "ACTIVE",
    "episode.terminated_properly": False,

    "workflow.status": "ACTIVE",
    "workflow.execution_mode": "UNATTENDED",

    "statistics.total_sub_hypotheses": 0,
    "statistics.validated_sub_hypotheses": 0,
    "statistics.failed_sub_hypotheses": 0,
    "statistics.blocked_sub_hypotheses": 0
}

# Sub-hypothesis default structure
SUB_HYPOTHESIS_DEFAULTS = {
    "type": "UNKNOWN",
    "statement": "",
    "status": "READY",
    "gate": {
        "type": "MUST_WORK",
        "satisfied": None
    },
    "prerequisites": [],
    "experiment_design": {
        "status": "NOT_STARTED",
        "file": None
    },
    "implementation_planning": {
        "status": "NOT_STARTED"
    },
    "validation": {
        "status": "NOT_STARTED",
        "result": None,
        "key_findings": []
    },
    "version": 1,
    "modification_attempt": 0,
    "completed": False,
    "completed_at": None,

    "blocked_by": None,
    "awaiting": None,
    "failed_by": None,

    "data_setup": {
        "status": "NOT_STARTED",
        "dataset": {
            "name": None,
            "type": None,
            "cache_path": None,
            "verified": False
        },
        "model": {
            "name": None,
            "pretrained": None,
            "cache_path": None,
            "verified": False
        },
        "completed_at": None
    },

    "superseded": {
        "superseded_by": None,
        "superseded_at": None,
        "superseded_reason": None,
        "partial_results_preserved": False
    }
}
```

---

## Functions

### 1. validate_and_load_state

```python
def validate_and_load_state(research_folder: str) -> dict:
    """
    Load and validate verification_state.yaml with basic checks.

    Args:
        research_folder: Path to research folder containing verification_state.yaml

    Returns:
        Dictionary containing:
            - success: bool - Whether file loaded successfully
            - state: dict - Parsed YAML content (or None if failed)
            - errors: list - Critical errors that prevent usage
            - warnings: list - Non-critical issues
            - auto_fixed: list - Fields that were auto-corrected

    Usage:
        result = validate_and_load_state(research_folder)
        if result["success"]:
            state = result["state"]
        else:
            print(f"Critical errors: {result['errors']}")
    """
    state_path = f"{research_folder}/verification_state.yaml"
    errors = []
    warnings = []
    auto_fixed = []

    # Check file exists
    if not file_exists(state_path):
        return {
            "success": False,
            "state": None,
            "errors": ["verification_state.yaml not found"],
            "warnings": [],
            "auto_fixed": []
        }

    # Try to load YAML
    try:
        state = read_yaml(state_path)
    except YAMLError as e:
        return {
            "success": False,
            "state": None,
            "errors": [f"YAML parse error: {str(e)}"],
            "warnings": [],
            "auto_fixed": []
        }

    # Check if state is None or empty
    if not state:
        return {
            "success": False,
            "state": None,
            "errors": ["verification_state.yaml is empty"],
            "warnings": [],
            "auto_fixed": []
        }

    # Check required sections
    for section in REQUIRED_SECTIONS:
        if section not in state:
            if section in ["gate_violations", "modification_history", "history", "serena_memory"]:
                # Non-critical sections - auto-fix with empty default
                state[section] = []
                auto_fixed.append(f"Added missing section: {section}")
            else:
                errors.append(f"Missing required section: {section}")

    # Check state format version
    schema_version = state.get("metadata", {}).get("schema_version")
    if not schema_version:
        warnings.append("Missing schema_version - assuming current format")
        state["metadata"]["schema_version"] = CURRENT_SCHEMA_VERSION
        auto_fixed.append("Set schema_version to current")
    elif schema_version not in SUPPORTED_VERSIONS:
        warnings.append(f"Unknown state format version: {schema_version}")

    return {
        "success": len(errors) == 0,
        "state": state if len(errors) == 0 else None,
        "errors": errors,
        "warnings": warnings,
        "auto_fixed": auto_fixed,
        "state_path": state_path
    }
```

### 2. validate_required_fields

```python
def validate_required_fields(state: dict) -> dict:
    """
    Validate all required fields are present.

    Args:
        state: Parsed verification_state dictionary

    Returns:
        Dictionary containing:
            - valid: bool
            - missing_fields: list - Missing field paths
            - invalid_values: list - Fields with invalid values
            - auto_fixable: list - Fields that can be auto-fixed

    Usage:
        result = validate_required_fields(state)
        if not result["valid"]:
            print(f"Missing: {result['missing_fields']}")
    """
    missing_fields = []
    invalid_values = []
    auto_fixable = []

    # Check metadata fields
    metadata = state.get("metadata", {})
    for field in REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            field_path = f"metadata.{field}"
            missing_fields.append(field_path)
            if field_path in AUTO_FIX_DEFAULTS:
                auto_fixable.append(field_path)

    # Check main_hypothesis fields
    main_hyp = state.get("main_hypothesis", {})
    for field in REQUIRED_MAIN_HYPOTHESIS_FIELDS:
        if field not in main_hyp:
            field_path = f"main_hypothesis.{field}"
            missing_fields.append(field_path)
            if field_path in AUTO_FIX_DEFAULTS:
                auto_fixable.append(field_path)

    # Check workflow fields
    workflow = state.get("workflow", {})
    if "status" not in workflow:
        missing_fields.append("workflow.status")
        auto_fixable.append("workflow.status")
    elif workflow["status"] not in VALID_WORKFLOW_STATUSES:
        invalid_values.append({
            "field": "workflow.status",
            "value": workflow["status"],
            "valid_values": VALID_WORKFLOW_STATUSES
        })

    # Check statistics exist
    if "statistics" not in state:
        missing_fields.append("statistics")
        auto_fixable.append("statistics")

    return {
        "valid": len(missing_fields) == 0 and len(invalid_values) == 0,
        "missing_fields": missing_fields,
        "invalid_values": invalid_values,
        "auto_fixable": auto_fixable
    }
```

### 3. validate_hypothesis_fields

```python
def validate_hypothesis_fields(state: dict) -> dict:
    """
    Validate all sub-hypothesis entries have required fields.

    Args:
        state: Parsed verification_state dictionary

    Returns:
        Dictionary containing:
            - valid: bool
            - hypothesis_errors: dict - {h_id: [errors]}
            - hypothesis_warnings: dict - {h_id: [warnings]}
            - auto_fixable: dict - {h_id: [fixable_fields]}

    Usage:
        result = validate_hypothesis_fields(state)
        for h_id, errors in result["hypothesis_errors"].items():
            print(f"{h_id}: {errors}")
    """
    hypothesis_errors = {}
    hypothesis_warnings = {}
    auto_fixable = {}

    sub_hypotheses = state.get("sub_hypotheses", {})

    for h_id, h_data in sub_hypotheses.items():
        errors = []
        warnings = []
        fixable = []

        # Check required fields
        for field in REQUIRED_SUB_HYPOTHESIS_FIELDS:
            if field not in h_data:
                errors.append(f"Missing field: {field}")
                fixable.append(field)

        # Validate status
        if "status" in h_data:
            if h_data["status"] not in VALID_HYPOTHESIS_STATUSES:
                errors.append(f"Invalid status: {h_data['status']}")

        # Validate gate structure
        gate = h_data.get("gate", {})
        if gate:
            if "type" not in gate:
                warnings.append("Missing gate.type")
                fixable.append("gate.type")
            elif gate["type"] not in VALID_GATE_TYPES:
                errors.append(f"Invalid gate type: {gate['type']}")

        # Validate prerequisites reference valid hypotheses
        prereqs = h_data.get("prerequisites", [])
        for prereq in prereqs:
            if prereq not in sub_hypotheses:
                errors.append(f"Invalid prerequisite: {prereq} not found in sub_hypotheses")

        # Check cascade fields
        if h_data.get("status") == "BLOCKED":
            if not h_data.get("blocked_by"):
                warnings.append("BLOCKED status but blocked_by not set")
                fixable.append("blocked_by")

        if h_data.get("status") == "CASCADE_FAILED":
            if not h_data.get("failed_by"):
                warnings.append("CASCADE_FAILED status but failed_by not set")
                fixable.append("failed_by")

        # Store results
        if errors:
            hypothesis_errors[h_id] = errors
        if warnings:
            hypothesis_warnings[h_id] = warnings
        if fixable:
            auto_fixable[h_id] = fixable

    return {
        "valid": len(hypothesis_errors) == 0,
        "hypothesis_errors": hypothesis_errors,
        "hypothesis_warnings": hypothesis_warnings,
        "auto_fixable": auto_fixable
    }
```

### 4. validate_archon_sync

```python
def validate_archon_sync(state: dict, pipeline_project_id: str = None) -> dict:
    """
    Validate Archon task state matches verification_state.

    Args:
        state: Parsed verification_state dictionary
        pipeline_project_id: Optional override for project ID

    Returns:
        Dictionary containing:
            - synced: bool - All tasks match
            - missing_tasks: list - Hypotheses without Archon tasks
            - orphan_tasks: list - Archon tasks without matching hypothesis
            - status_mismatches: list - Status differences
            - recommendations: list - Actions to sync

    Usage:
        result = validate_archon_sync(state)
        if not result["synced"]:
            for rec in result["recommendations"]:
                print(f"Action needed: {rec}")
    """
    project_id = pipeline_project_id or state.get("metadata", {}).get("pipeline_project_id")
    task_mapping = state.get("metadata", {}).get("hypothesis_task_mapping", {})

    missing_tasks = []
    orphan_tasks = []
    status_mismatches = []
    recommendations = []

    if not project_id:
        return {
            "synced": False,
            "missing_tasks": [],
            "orphan_tasks": [],
            "status_mismatches": [],
            "recommendations": ["Set pipeline_project_id in metadata"]
        }

    # Get all hypothesis tasks from Archon
    archon_result = mcp__archon__find_tasks(
        project_id=project_id,
        per_page=100
    )

    if not archon_result.get("success"):
        return {
            "synced": False,
            "missing_tasks": [],
            "orphan_tasks": [],
            "status_mismatches": [],
            "recommendations": [f"Failed to query Archon: {archon_result.get('error')}"]
        }

    archon_tasks = archon_result.get("tasks", [])

    # Build task lookup by ID and by feature
    task_by_id = {t["id"]: t for t in archon_tasks}
    tasks_by_feature = {}
    for t in archon_tasks:
        feature = t.get("feature", "")
        if feature:
            if feature not in tasks_by_feature:
                tasks_by_feature[feature] = []
            tasks_by_feature[feature].append(t)

    sub_hypotheses = state.get("sub_hypotheses", {})

    # Check each hypothesis
    for h_id, h_data in sub_hypotheses.items():
        mapped_task_id = task_mapping.get(h_id)

        # Check 1: Task mapping exists
        if not mapped_task_id:
            # Try to find by feature
            feature_tasks = tasks_by_feature.get(h_id, [])
            if not feature_tasks:
                missing_tasks.append({
                    "hypothesis_id": h_id,
                    "status": h_data.get("status")
                })
                recommendations.append(f"Create parent task for {h_id}")
            else:
                recommendations.append(f"Add {h_id} to hypothesis_task_mapping")
            continue

        # Check 2: Task exists in Archon
        archon_task = task_by_id.get(mapped_task_id)
        if not archon_task:
            missing_tasks.append({
                "hypothesis_id": h_id,
                "mapped_task_id": mapped_task_id,
                "reason": "Task ID not found in Archon"
            })
            recommendations.append(f"Update task mapping for {h_id} - task {mapped_task_id} not found")
            continue

        # Check 3: Status consistency
        h_status = h_data.get("status", "")
        task_status = archon_task.get("status", "")

        expected_task_status = map_hypothesis_status_to_task(h_status)

        if task_status != expected_task_status:
            status_mismatches.append({
                "hypothesis_id": h_id,
                "task_id": mapped_task_id,
                "hypothesis_status": h_status,
                "task_status": task_status,
                "expected_task_status": expected_task_status
            })
            recommendations.append(
                f"Update task {mapped_task_id} status: {task_status} → {expected_task_status}"
            )

    # Check for orphan tasks (tasks with hypothesis feature but no matching hypothesis)
    for feature, tasks in tasks_by_feature.items():
        if feature.startswith("h-") and feature not in sub_hypotheses:
            for t in tasks:
                orphan_tasks.append({
                    "task_id": t["id"],
                    "feature": feature,
                    "title": t["title"]
                })
            recommendations.append(f"Orphan tasks found for feature '{feature}' - no matching hypothesis")

    return {
        "synced": len(missing_tasks) == 0 and len(status_mismatches) == 0,
        "missing_tasks": missing_tasks,
        "orphan_tasks": orphan_tasks,
        "status_mismatches": status_mismatches,
        "recommendations": recommendations
    }

def map_hypothesis_status_to_task(h_status: str) -> str:
    """Map hypothesis status to expected Archon task status."""
    STATUS_MAP = {
        "NOT_STARTED": "todo",
        "READY": "todo",
        "IN_PROGRESS": "doing",
        "COMPLETED": "done",
        "VALIDATED": "done",
        "BLOCKED": "todo", # Blocked tasks stay in todo
        "CASCADE_FAILED": "done", # Marked done with failure note
        "CASCADE_SUPERSEDED": "done", # Marked done with supersede note
        "SUPERSEDED": "done", # Marked done with supersede note
        "FAILED": "done" # Marked done with failure note
    }
    return STATUS_MAP.get(h_status, "todo")
```

### 5. validate_prerequisites

```python
def validate_prerequisites(state: dict) -> dict:
    """
    Validate prerequisite relationships are consistent.

    Args:
        state: Parsed verification_state dictionary

    Returns:
        Dictionary containing:
            - valid: bool
            - violations: list - Prerequisite violations
            - circular_deps: list - Circular dependency chains
            - ready_hypotheses: list - Hypotheses that can start
            - blocked_hypotheses: list - Hypotheses waiting on prerequisites

    Usage:
        result = validate_prerequisites(state)
        print(f"Ready to start: {result['ready_hypotheses']}")
    """
    violations = []
    circular_deps = []
    ready_hypotheses = []
    blocked_hypotheses = []

    sub_hypotheses = state.get("sub_hypotheses", {})

    # Build dependency graph
    dep_graph = {}
    for h_id, h_data in sub_hypotheses.items():
        prereqs = h_data.get("prerequisites", [])
        dep_graph[h_id] = prereqs

    # Check for circular dependencies (DFS)
    def find_cycle(node, visited, rec_stack, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for prereq in dep_graph.get(node, []):
            if prereq not in visited:
                cycle = find_cycle(prereq, visited, rec_stack, path)
                if cycle:
                    return cycle
            elif prereq in rec_stack:
                # Found cycle
                cycle_start = path.index(prereq)
                return path[cycle_start:] + [prereq]

        path.pop()
        rec_stack.remove(node)
        return None

    visited = set()
    for h_id in dep_graph:
        if h_id not in visited:
            cycle = find_cycle(h_id, visited, set(), [])
            if cycle:
                circular_deps.append(cycle)

    # Check prerequisite satisfaction
    for h_id, h_data in sub_hypotheses.items():
        prereqs = h_data.get("prerequisites", [])
        h_status = h_data.get("status", "")

        if not prereqs:
            # No prerequisites - can start if READY
            if h_status == "READY":
                ready_hypotheses.append(h_id)
            continue

        # Check each prerequisite
        prereq_statuses = []
        blocking_prereqs = []

        for prereq in prereqs:
            if prereq not in sub_hypotheses:
                violations.append({
                    "hypothesis_id": h_id,
                    "prerequisite": prereq,
                    "reason": "Prerequisite not found"
                })
                continue

            prereq_data = sub_hypotheses[prereq]
            prereq_status = prereq_data.get("status", "")
            prereq_statuses.append(prereq_status)

            # Check if prerequisite blocks this hypothesis
            if prereq_status not in ["VALIDATED"]:
                blocking_prereqs.append({
                    "prereq_id": prereq,
                    "prereq_status": prereq_status
                })

        # Determine if blocked
        if blocking_prereqs:
            blocked_hypotheses.append({
                "hypothesis_id": h_id,
                "status": h_status,
                "blocked_by": blocking_prereqs
            })

            # Check if status should be BLOCKED but isn't
            if h_status == "READY" and len(blocking_prereqs) > 0:
                violations.append({
                    "hypothesis_id": h_id,
                    "reason": "Status is READY but has unsatisfied prerequisites",
                    "blocking_prereqs": [b["prereq_id"] for b in blocking_prereqs]
                })
        elif h_status == "READY":
            ready_hypotheses.append(h_id)

    return {
        "valid": len(violations) == 0 and len(circular_deps) == 0,
        "violations": violations,
        "circular_deps": circular_deps,
        "ready_hypotheses": ready_hypotheses,
        "blocked_hypotheses": blocked_hypotheses
    }
```

### 6. full_state_validation

```python
def full_state_validation(research_folder: str, auto_fix: bool = True) -> dict:
    """
    Run complete validation on verification_state.yaml.

    Args:
        research_folder: Path to research folder
        auto_fix: Whether to apply auto-fixes (default: True)

    Returns:
        Dictionary containing:
            - success: bool - All validations passed
            - state: dict - Validated (and possibly fixed) state
            - report: dict - Detailed validation report
            - backup_path: str - Backup file path (if changes made)

    Usage:
        result = full_state_validation(research_folder)
        if result["success"]:
            state = result["state"]
        else:
            print_validation_report(result["report"])
    """
    report = {
        "timestamp": now_iso8601(),
        "research_folder": research_folder,
        "load_result": None,
        "required_fields": None,
        "hypothesis_fields": None,
        "prerequisites": None,
        "archon_sync": None,
        "auto_fixes_applied": [],
        "errors": [],
        "warnings": []
    }

    # Step 1: Load and basic validation
    load_result = validate_and_load_state(research_folder)
    report["load_result"] = load_result

    if not load_result["success"]:
        report["errors"].extend(load_result["errors"])
        return {
            "success": False,
            "state": None,
            "report": report,
            "backup_path": None
        }

    state = load_result["state"]
    report["warnings"].extend(load_result["warnings"])
    report["auto_fixes_applied"].extend(load_result["auto_fixed"])

    # Step 2: Validate required fields
    fields_result = validate_required_fields(state)
    report["required_fields"] = fields_result

    if not fields_result["valid"]:
        report["errors"].append(f"Missing required fields: {fields_result['missing_fields']}")

        if auto_fix and fields_result["auto_fixable"]:
            state = apply_auto_fixes(state, fields_result["auto_fixable"])
            report["auto_fixes_applied"].append(f"Fixed fields: {fields_result['auto_fixable']}")

    # Step 3: Validate hypothesis fields
    hyp_result = validate_hypothesis_fields(state)
    report["hypothesis_fields"] = hyp_result

    if not hyp_result["valid"]:
        report["errors"].append(f"Hypothesis field errors: {hyp_result['hypothesis_errors']}")

        if auto_fix and hyp_result["auto_fixable"]:
            state = apply_hypothesis_fixes(state, hyp_result["auto_fixable"])
            report["auto_fixes_applied"].append(f"Fixed hypothesis fields: {list(hyp_result['auto_fixable'].keys())}")

    report["warnings"].extend([
        f"{h_id}: {w}" for h_id, warnings in hyp_result["hypothesis_warnings"].items() for w in warnings
    ])

    # Step 4: Validate prerequisites
    prereq_result = validate_prerequisites(state)
    report["prerequisites"] = prereq_result

    if not prereq_result["valid"]:
        report["errors"].append(f"Prerequisite violations: {prereq_result['violations']}")
        if prereq_result["circular_deps"]:
            report["errors"].append(f"Circular dependencies: {prereq_result['circular_deps']}")

    # Step 5: Validate Archon sync (warnings only, no auto-fix)
    pipeline_project_id = state.get("metadata", {}).get("pipeline_project_id")
    if pipeline_project_id:
        archon_result = validate_archon_sync(state, pipeline_project_id)
        report["archon_sync"] = archon_result
        report["warnings"].extend(archon_result["recommendations"])

    # Create backup if changes were made
    backup_path = None
    if report["auto_fixes_applied"] and auto_fix:
        backup_path = f"{research_folder}/verification_state.yaml.backup.{now_timestamp()}"
        # Copy current file to backup
        copy_file(load_result["state_path"], backup_path)

        # Save fixed state
        write_yaml(load_result["state_path"], state)
        state["metadata"]["last_updated"] = now_iso8601()

    # Determine overall success
    success = len(report["errors"]) == 0

    return {
        "success": success,
        "state": state,
        "report": report,
        "backup_path": backup_path
    }
```

### 8. apply_auto_fixes

```python
def apply_auto_fixes(state: dict, fixable_fields: list) -> dict:
    """
    Apply auto-fixes for missing/invalid fields.

    Args:
        state: State dictionary to fix
        fixable_fields: List of field paths to fix

    Returns:
        Updated state dictionary

    Usage:
        state = apply_auto_fixes(state, ["metadata.pipeline_project_id", "statistics"])
    """
    for field_path in fixable_fields:
        if field_path in AUTO_FIX_DEFAULTS:
            set_nested_field(state, field_path, AUTO_FIX_DEFAULTS[field_path])
        elif field_path == "statistics":
            state["statistics"] = {
                "total_sub_hypotheses": len(state.get("sub_hypotheses", {})),
                "validated_sub_hypotheses": 0,
                "failed_sub_hypotheses": 0,
                "blocked_sub_hypotheses": 0,
                "in_progress_sub_hypotheses": 0,
                "total_modifications": 0,
                "successful_modifications": 0,
                "failed_modifications": 0,
                "gates_passed": 0,
                "gates_failed": 0,
                "phases_completed": {
                    "phase_2b": False,
                    "phase_2c": 0,
                    "phase_3": 0,
                    "phase_4": 0,
                    "phase_5": False
                }
            }

    return state

def apply_hypothesis_fixes(state: dict, fixable_by_hypothesis: dict) -> dict:
    """
    Apply auto-fixes for hypothesis fields.

    Args:
        state: State dictionary to fix
        fixable_by_hypothesis: {h_id: [field_list]}

    Returns:
        Updated state dictionary
    """
    for h_id, fields in fixable_by_hypothesis.items():
        h_data = state.get("sub_hypotheses", {}).get(h_id, {})

        for field in fields:
            if field in SUB_HYPOTHESIS_DEFAULTS:
                h_data[field] = SUB_HYPOTHESIS_DEFAULTS[field]
            elif field == "gate.type":
                h_data.setdefault("gate", {})["type"] = "MUST_WORK"

        state["sub_hypotheses"][h_id] = h_data

    return state

def set_nested_field(d: dict, path: str, value) -> None:
    """Set nested dictionary field using dot notation."""
    keys = path.split(".")
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value
```

---

## Full State Consistency Validation

> Added to address Task 8: Unified validation across verification_state, checkpoint, and Archon.

### 9. validate_full_state_consistency

```python
def validate_full_state_consistency(
    research_folder: str,
    hypothesis_id: str,
    checkpoint: dict = None,
    pipeline_project_id: str = None
) -> dict:
    """
    Validate consistency across ALL state sources:
    - verification_state.yaml
    - 04_checkpoint.yaml (if exists)
    - Archon Tasks

    This is a comprehensive validation for pipeline entry points.

    Args:
        research_folder: Path to research folder
        hypothesis_id: Current hypothesis ID
        checkpoint: Optional checkpoint dict (will load from file if not provided)
        pipeline_project_id: Optional project ID override

    Returns:
        Dictionary containing:
            - consistent: bool - All sources are consistent
            - verification_state: dict - Loaded/validated state
            - sources_checked: list - Which sources were validated
            - discrepancies: list - All inconsistencies found
            - errors: list - Critical errors
            - warnings: list - Non-critical issues
            - recommended_actions: list - Actions to resolve issues

    Usage:
        # At pipeline entry point (e.g., step-01-initialize)
        result = validate_full_state_consistency(
            research_folder,
            "h-e1"
        )
        if not result["consistent"]:
            for action in result["recommended_actions"]:
                print(f"→ {action}")
    """
    errors = []
    warnings = []
    discrepancies = []
    recommended_actions = []
    sources_checked = []

    # ============================================
    # 1. Load and Validate verification_state.yaml
    # ============================================
    load_result = validate_and_load_state(research_folder)
    sources_checked.append("verification_state")

    if not load_result["success"]:
        return {
            "consistent": False,
            "verification_state": None,
            "sources_checked": sources_checked,
            "discrepancies": [],
            "errors": load_result["errors"],
            "warnings": [],
            "recommended_actions": ["Fix verification_state.yaml errors before proceeding"]
        }

    state = load_result["state"]
    warnings.extend(load_result["warnings"])

    # Check hypothesis exists
    h_data = state.get("sub_hypotheses", {}).get(hypothesis_id)
    if not h_data:
        return {
            "consistent": False,
            "verification_state": state,
            "sources_checked": sources_checked,
            "discrepancies": [f"Hypothesis {hypothesis_id} not found in verification_state"],
            "errors": [f"Missing hypothesis: {hypothesis_id}"],
            "warnings": warnings,
            "recommended_actions": [f"Add {hypothesis_id} to sub_hypotheses"]
        }

    # Get hypothesis folder
    hypothesis_folder = f"{research_folder}/{hypothesis_id}"

    # ============================================
    # 2. Load and Validate Checkpoint (if exists)
    # ============================================
    checkpoint_file = f"{hypothesis_folder}/04_checkpoint.yaml"
    checkpoint_exists = file_exists(checkpoint_file)

    if checkpoint_exists and not checkpoint:
        try:
            checkpoint = read_yaml(checkpoint_file)
            sources_checked.append("checkpoint")
        except Exception as e:
            warnings.append(f"Failed to load checkpoint: {e}")
            checkpoint = None

    if checkpoint:
        sources_checked.append("checkpoint") if "checkpoint" not in sources_checked else None

        # Import sync validation from checkpoint_helpers
        from checkpoint_helpers import validate_checkpoint_verification_sync

        sync_result = validate_checkpoint_verification_sync(
            checkpoint, state, hypothesis_id
        )

        if not sync_result["synced"]:
            discrepancies.extend(sync_result["discrepancies"])
            recommended_actions.extend(sync_result["recommendations"])

        # Additional checkpoint-specific checks
        vs_status = h_data.get("status")
        cp_step = checkpoint.get("current_step", 0)

        # Check: COMPLETED status but checkpoint shows early step
        if vs_status == "VALIDATED" and cp_step < 6:
            discrepancies.append({
                "type": "status_step_mismatch",
                "verification_state_status": vs_status,
                "checkpoint_step": cp_step,
                "issue": "VALIDATED status but checkpoint shows step < 6"
            })
            recommended_actions.append("Sync checkpoint to reflect VALIDATED status or update verification_state")

        # Check: IN_PROGRESS but no checkpoint or archived checkpoint
        if vs_status == "IN_PROGRESS" and not checkpoint_exists:
            warnings.append(f"IN_PROGRESS status but no checkpoint file for {hypothesis_id}")

    # ============================================
    # 3. Validate Archon Task Consistency
    # ============================================
    project_id = pipeline_project_id or state.get("metadata", {}).get("pipeline_project_id")

    if project_id:
        archon_result = validate_archon_sync(state, project_id)
        sources_checked.append("archon")

        if not archon_result["synced"]:
            # Filter to current hypothesis
            for missing in archon_result["missing_tasks"]:
                if missing.get("hypothesis_id") == hypothesis_id:
                    discrepancies.append({
                        "type": "archon_missing_task",
                        "hypothesis_id": hypothesis_id,
                        "detail": missing
                    })

            for mismatch in archon_result["status_mismatches"]:
                if mismatch.get("hypothesis_id") == hypothesis_id:
                    discrepancies.append({
                        "type": "archon_status_mismatch",
                        "hypothesis_id": hypothesis_id,
                        "verification_state_status": mismatch["hypothesis_status"],
                        "archon_task_status": mismatch["task_status"],
                        "expected_archon_status": mismatch["expected_task_status"]
                    })
                    recommended_actions.append(
                        f"Update Archon task {mismatch['task_id']} status: "
                        f"{mismatch['task_status']} → {mismatch['expected_task_status']}"
                    )

            recommended_actions.extend([
                r for r in archon_result["recommendations"]
                if hypothesis_id in r
            ])
    else:
        warnings.append("No pipeline_project_id - Archon sync validation skipped")

    # ============================================
    # 4. Cross-Source Validation
    # ============================================

    # Validation.status vs Gate.satisfied consistency
    validation_status = h_data.get("validation", {}).get("status")
    gate_satisfied = h_data.get("gate", {}).get("satisfied")

    if validation_status == "COMPLETED" and gate_satisfied is None:
        discrepancies.append({
            "type": "validation_gate_mismatch",
            "validation_status": validation_status,
            "gate_satisfied": gate_satisfied,
            "issue": "COMPLETED validation but gate.satisfied not set"
        })
        recommended_actions.append("Set gate.satisfied based on validation result")

    if gate_satisfied == True and validation_status == "NOT_STARTED":
        discrepancies.append({
            "type": "gate_validation_mismatch",
            "gate_satisfied": gate_satisfied,
            "validation_status": validation_status,
            "issue": "Gate satisfied but validation.status is NOT_STARTED"
        })
        recommended_actions.append("Update validation.status to COMPLETED")

    # ============================================
    # 5. Determine Overall Consistency
    # ============================================
    consistent = len(discrepancies) == 0 and len(errors) == 0

    return {
        "consistent": consistent,
        "verification_state": state,
        "sources_checked": sources_checked,
        "discrepancies": discrepancies,
        "errors": errors,
        "warnings": warnings,
        "recommended_actions": recommended_actions
    }
```

### 10. auto_fix_state_consistency

```python
def auto_fix_state_consistency(
    consistency_result: dict,
    research_folder: str,
    hypothesis_id: str,
    fix_verification_state: bool = True,
    fix_archon: bool = True
) -> dict:
    """
    Automatically fix consistency issues found by validate_full_state_consistency().

    Args:
        consistency_result: Result from validate_full_state_consistency()
        research_folder: Path to research folder
        hypothesis_id: Hypothesis ID
        fix_verification_state: Whether to fix verification_state issues
        fix_archon: Whether to fix Archon task issues

    Returns:
        Dictionary containing:
            - success: bool
            - fixes_applied: list
            - remaining_issues: list
            - updated_state: dict

    Usage:
        result = validate_full_state_consistency(research_folder, "h-e1")
        if not result["consistent"]:
            fix_result = auto_fix_state_consistency(result, research_folder, "h-e1")
    """
    fixes_applied = []
    remaining_issues = []
    state = consistency_result["verification_state"]

    if not state:
        return {
            "success": False,
            "fixes_applied": [],
            "remaining_issues": ["Cannot fix - verification_state not loaded"],
            "updated_state": None
        }

    h_data = state.get("sub_hypotheses", {}).get(hypothesis_id, {})

    for discrepancy in consistency_result["discrepancies"]:
        disc_type = discrepancy.get("type", "unknown")

        # Fix validation-gate mismatch
        if disc_type == "validation_gate_mismatch" and fix_verification_state:
            validation_result = h_data.get("validation", {}).get("result")
            if validation_result == "PASS":
                h_data["gate"]["satisfied"] = True
                fixes_applied.append(f"Set gate.satisfied = True for {hypothesis_id}")
            elif validation_result in ["FAIL", "PARTIAL"]:
                h_data["gate"]["satisfied"] = False
                fixes_applied.append(f"Set gate.satisfied = False for {hypothesis_id}")
            else:
                remaining_issues.append(f"Cannot determine gate.satisfied - validation.result is {validation_result}")

        # Fix gate-validation mismatch
        elif disc_type == "gate_validation_mismatch" and fix_verification_state:
            h_data["validation"]["status"] = "COMPLETED"
            fixes_applied.append(f"Set validation.status = COMPLETED for {hypothesis_id}")

        # Fix Archon status mismatch
        elif disc_type == "archon_status_mismatch" and fix_archon:
            task_id = discrepancy.get("task_id")
            expected_status = discrepancy.get("expected_archon_status")
            if task_id and expected_status:
                try:
                    mcp__archon__manage_task(
                        action="update",
                        task_id=task_id,
                        status=expected_status
                    )
                    fixes_applied.append(f"Updated Archon task {task_id} status to {expected_status}")
                except Exception as e:
                    remaining_issues.append(f"Failed to update Archon task {task_id}: {e}")
            else:
                remaining_issues.append(f"Cannot fix Archon mismatch - missing task_id or expected_status")

        # Cannot auto-fix
        else:
            remaining_issues.append(f"Cannot auto-fix: {disc_type}")

    # Save updated state if fixes were applied
    if fixes_applied and fix_verification_state:
        state["sub_hypotheses"][hypothesis_id] = h_data
        state["metadata"]["last_updated"] = datetime.now().isoformat()
        state_path = f"{research_folder}/verification_state.yaml"
        write_yaml(state_path, state)
        fixes_applied.append(f"Saved updated verification_state.yaml")

    return {
        "success": len(remaining_issues) == 0,
        "fixes_applied": fixes_applied,
        "remaining_issues": remaining_issues,
        "updated_state": state
    }
```
