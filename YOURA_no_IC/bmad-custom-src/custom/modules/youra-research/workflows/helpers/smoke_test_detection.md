---
name: 'smoke_test_detection'
description: 'Functions for detecting smoke tests and managing two-phase experiment execution'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - detect_smoke_test
  - remove_quick_args
  - build_full_run_command
  - save_smoke_test_results
  - handle_smoke_test_detection
  - validate_full_run_results

# Called By
called_by:
  - 'phase4-coding/steps/step-05a-pre-validation.md'
  - 'phase4-coding/steps/step-05b-experiment.md'
  - 'phase4-coding/steps/step-05c-post-validation.md'
---

# Smoke Test Detection Helper Functions

> Reusable functions for detecting smoke tests and managing two-phase experiment execution.
> Prevents false completion by identifying quick/debug runs and transitioning to full experiments.

---

## Constants

### Detection Patterns

```python
# Command line arguments that indicate smoke test
SMOKE_TEST_ARGS = [
    "--quick",
    "--smoke",
    "--dry-run",
    "--test",
    "--debug",
    "--fast"
]

# Arguments indicating minimal run (1 epoch)
MINIMAL_RUN_ARGS = [
    "--epochs=1",
    "--max_steps=1",
    "--max_epochs=1",
    "--num_epochs=1"
]

# All quick arguments combined
ALL_QUICK_ARGS = SMOKE_TEST_ARGS + MINIMAL_RUN_ARGS

# Log patterns indicating smoke test
SMOKE_LOG_PATTERNS = [
    "smoke test",
    "quick mode",
    "dry run",
    "debug mode",
    "epoch 1/1",
    "max_steps=1",
    "max_epochs=1",
    "running in test mode",
    "validation only",
    "skipping training"
]

# Duration threshold (seconds) - very fast completion suggests smoke test
QUICK_DURATION_THRESHOLD = 60 # 1 minute
```

---

## Functions

### 1. detect_smoke_test

```python
def detect_smoke_test(
    command_used: str,
    log_content: str,
    duration_seconds: float
) -> dict:
    """
    Detect if the completed experiment was a smoke test.

    Args:
        command_used: The command that was executed
        log_content: Content of experiment.log
        duration_seconds: How long the experiment ran

    Returns:
        Dictionary containing:
            - is_smoke_test: bool - Smoke test detected
            - indicators: list - Evidence of smoke test
            - confidence: str - "HIGH", "MEDIUM", "LOW"
            - recommendation: str - What to do next

    Usage:
        result = detect_smoke_test(
            "python main.py --quick",
            log_content,
            45.0
        )
        if result["is_smoke_test"]:
            print(f"Smoke test detected: {result['indicators']}")
    """
    indicators = []
    is_smoke_test = False

    # Check 1: Command line args
    for arg in SMOKE_TEST_ARGS:
        if arg in command_used:
            is_smoke_test = True
            indicators.append(f"Quick mode argument in command: {arg}")

    # Check 2: Log patterns
    log_lower = log_content.lower()
    for pattern in SMOKE_LOG_PATTERNS:
        if pattern.lower() in log_lower:
            is_smoke_test = True
            indicators.append(f"Log contains: '{pattern}'")

    # Check 3: Very short duration
    if duration_seconds < QUICK_DURATION_THRESHOLD:
        indicators.append(f"Very short duration: {duration_seconds:.1f}s")

    # Check 4: Epoch count
    import re
    epoch_matches = re.findall(r"epoch[:\s]+(\d+)", log_lower)
    if epoch_matches:
        max_epoch = max(int(e) for e in epoch_matches)
        if max_epoch <= 1:
            is_smoke_test = True
            indicators.append(f"Only {max_epoch} epoch completed")

    # Determine confidence
    if len(indicators) >= 3:
        confidence = "HIGH"
    elif len(indicators) >= 2:
        confidence = "MEDIUM"
    elif len(indicators) == 1:
        confidence = "LOW"
    else:
        confidence = "NONE"

    # Generate recommendation
    if is_smoke_test:
        recommendation = "Re-run WITHOUT quick mode arguments for full experiment"
    else:
        recommendation = "Experiment appears to be full run - proceed to validation"

    return {
        "is_smoke_test": is_smoke_test,
        "indicators": indicators,
        "indicator_count": len(indicators),
        "confidence": confidence,
        "duration_seconds": duration_seconds,
        "recommendation": recommendation
    }
```

### 2. remove_quick_args

```python
def remove_quick_args(command: str) -> str:
    """
    Remove quick/smoke test arguments from command for full run.

    Args:
        command: Original command with possible quick args

    Returns:
        Command string with quick mode args removed

    Usage:
        full_cmd = remove_quick_args("python main.py --quick --epochs=1")
        # Returns: "python main.py"
    """
    tokens = command.split()
    filtered = []

    for token in tokens:
        # Check if token matches any quick argument
        is_quick_arg = False
        for quick_arg in ALL_QUICK_ARGS:
            if quick_arg in token:
                is_quick_arg = True
                break

        if not is_quick_arg:
            filtered.append(token)

    return " ".join(filtered)
```

### 3. build_full_run_command

```python
def build_full_run_command(
    smoke_command: str,
    config_file: str = None
) -> dict:
    """
    Build full experiment command from smoke test command.

    Args:
        smoke_command: Original smoke test command
        config_file: Optional path to config file for defaults

    Returns:
        Dictionary containing:
            - command: str - Full run command
            - removed_args: list - Arguments that were removed
            - added_args: list - Arguments that were added (if any)

    Usage:
        result = build_full_run_command("python main.py --quick --lr 0.01")
        print(f"Full command: {result['command']}")
        print(f"Removed: {result['removed_args']}")
    """
    # Track what we remove
    removed_args = []

    for arg in ALL_QUICK_ARGS:
        if arg in smoke_command:
            removed_args.append(arg)

    # Remove quick args
    full_command = remove_quick_args(smoke_command)

    # Clean up multiple spaces
    full_command = " ".join(full_command.split())

    return {
        "command": full_command,
        "removed_args": removed_args,
        "added_args": [],
        "original_command": smoke_command
    }
```

### 4. save_smoke_test_results

```python
def save_smoke_test_results(
    checkpoint: dict,
    detection_result: dict
) -> dict:
    """
    Save smoke test results to checkpoint for tracking.

    Args:
        checkpoint: Checkpoint dictionary to update
        detection_result: Result from detect_smoke_test()

    Returns:
        Updated checkpoint fields

    Usage:
        updated = save_smoke_test_results(checkpoint, detection_result)
        checkpoint.update(updated)
        SAVE checkpoint
    """
    from datetime import datetime

    smoke_test_data = {
        "smoke_test_completed": True,
        "smoke_test_results": {
            "status": "passed",
            "indicators": detection_result.get("indicators", []),
            "duration_seconds": detection_result.get("duration_seconds"),
            "confidence": detection_result.get("confidence"),
            "timestamp": datetime.now().isoformat()
        },
        "experiment_status": "smoke_test_passed"
    }

    return smoke_test_data
```

### 5. handle_smoke_test_detection (Main Function)

```python
def handle_smoke_test_detection(
    experiment_status: str,
    command_used: str,
    log_file: str,
    started_at: str,
    checkpoint: dict
) -> dict:
    """
    Main function: Handle smoke test detection and transition logic.

    This is called when an experiment completes quickly to determine
    if it was a smoke test and what action to take.

    Args:
        experiment_status: Current status (e.g., "quick_completion")
        command_used: Command that was executed
        log_file: Path to experiment log
        started_at: ISO timestamp when experiment started
        checkpoint: Checkpoint dictionary

    Returns:
        Dictionary containing:
            - is_smoke_test: bool - Smoke test detected
            - action: str - "RUN_FULL" or "PROCEED_TO_VALIDATION"
            - full_command: str - Command for full run (if applicable)
            - checkpoint_updates: dict - Updates for checkpoint
            - detection_result: dict - Full detection result

    Usage:
        result = handle_smoke_test_detection(
            "quick_completion",
            execution_plan["command"],
            f"{code_folder}/experiment.log",
            checkpoint.experiment_started_at,
            checkpoint
        )
        if result["action"] == "RUN_FULL":
            # Re-execute with full command
            run_experiment(result["full_command"])
    """
    from datetime import datetime

    # Only process if quick completion
    if experiment_status != "quick_completion":
        return {
            "is_smoke_test": False,
            "action": "PROCEED_TO_VALIDATION",
            "full_command": None,
            "checkpoint_updates": {},
            "detection_result": None
        }

    # Read log content
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
    except:
        log_content = ""

    # Calculate duration
    try:
        start_time = datetime.fromisoformat(started_at)
        duration = (datetime.now() - start_time).total_seconds()
    except:
        duration = 0

    # Detect smoke test
    detection = detect_smoke_test(command_used, log_content, duration)

    if detection["is_smoke_test"]:
        print("⚠️ SMOKE TEST DETECTED - NOT ACTUAL EXPERIMENT")
        print(f"Indicators: {detection['indicators']}")

        # Save smoke test results
        checkpoint_updates = save_smoke_test_results(checkpoint, detection)

        # Build full command
        full_result = build_full_run_command(command_used)

        print(f"✅ Smoke test passed. Will run full experiment...")
        print(f" Full command: {full_result['command']}")

        return {
            "is_smoke_test": True,
            "action": "RUN_FULL",
            "full_command": full_result["command"],
            "checkpoint_updates": checkpoint_updates,
            "detection_result": detection,
            "removed_args": full_result["removed_args"]
        }
    else:
        # Genuinely fast experiment
        print("✅ Fast experiment completed (not a smoke test)")

        return {
            "is_smoke_test": False,
            "action": "PROCEED_TO_VALIDATION",
            "full_command": None,
            "checkpoint_updates": {
                "experiment_status": "completed"
            },
            "detection_result": detection
        }
```

### 6. validate_full_run_results

```python
def validate_full_run_results(
    log_file: str,
    expected_epochs: int = None
) -> dict:
    """
    Validate that a full run actually completed (not truncated).

    Args:
        log_file: Path to experiment log
        expected_epochs: Expected number of epochs (optional)

    Returns:
        Dictionary containing:
            - valid: bool - Results appear complete
            - epochs_found: int - Number of epochs detected
            - has_final_metrics: bool - Final metrics present
            - warnings: list - Any concerns

    Usage:
        validation = validate_full_run_results(log_file, expected_epochs=100)
        if not validation["valid"]:
            print(f"Warnings: {validation['warnings']}")
    """
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
    except:
        return {
            "valid": False,
            "epochs_found": 0,
            "has_final_metrics": False,
            "warnings": ["Could not read log file"]
        }

    warnings = []
    log_lower = log_content.lower()

    # Check epoch count
    import re
    epoch_matches = re.findall(r"epoch[:\s]+(\d+)", log_lower)
    epochs_found = max(int(e) for e in epoch_matches) if epoch_matches else 0

    if expected_epochs and epochs_found < expected_epochs:
        warnings.append(f"Expected {expected_epochs} epochs, found {epochs_found}")

    # Check for completion indicators
    completion_patterns = [
        "training complete",
        "experiment finished",
        "final results",
        "best model saved",
        "training done"
    ]

    has_completion = any(p in log_lower for p in completion_patterns)

    # Check for final metrics
    metric_patterns = [
        r"final.*accuracy",
        r"final.*loss",
        r"best.*score",
        r"test.*accuracy",
        r"evaluation.*complete"
    ]

    has_final_metrics = any(re.search(p, log_lower) for p in metric_patterns)

    if not has_completion:
        warnings.append("No completion indicator found in log")

    if not has_final_metrics:
        warnings.append("No final metrics found in log")

    valid = len(warnings) == 0 and epochs_found > 1

    return {
        "valid": valid,
        "epochs_found": epochs_found,
        "has_final_metrics": has_final_metrics,
        "has_completion_indicator": has_completion,
        "warnings": warnings
    }
```

---

## Error Handling

| Scenario | Detection | Action |
|----------|-----------|--------|
| Quick arg in command | SMOKE_TEST_ARGS match | Remove args, re-run |
| Log shows 1 epoch | Epoch pattern match | Re-run full |
| < 60s duration | Duration check | Investigate, likely smoke |
| Missing final metrics | validate_full_run_results | Warning, may proceed |
| Truncated log | No completion indicator | Check for errors |
