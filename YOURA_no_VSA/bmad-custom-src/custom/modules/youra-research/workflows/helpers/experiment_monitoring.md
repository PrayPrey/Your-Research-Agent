---
name: 'experiment_monitoring'
description: 'Reusable functions for experiment execution, monitoring, and status tracking in Phase 4'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - launch_experiment_detached
  - monitor_experiment_progress
  - check_experiment_status
  - verify_gpu_utilization
  - poll_until_completion
  - get_experiment_metrics

# Called By
called_by:
  - 'phase4-coding/steps/step-05b-execution.md'
  - 'phase5-baseline-repo-comparison/steps/step-09-run-experiment.md'
---

# Experiment Monitoring Helper Functions

> Reusable functions for experiment execution, monitoring, and status tracking in Phase 4.
> Handles nohup launch, PID tracking, phased error checks, and GPU utilization verification.

---

## Constants

### Timing Configuration

```python
# Phased error check intervals (cumulative seconds)
PHASED_CHECK_INTERVALS = [30, 90, 180, 240] # 4 minutes total

# Polling configuration for long experiments
POLL_INTERVAL = 300 # 5 minutes between checks
MAX_POLL_TIME = 36000 # 10 hours maximum wait

# GPU utilization thresholds
GPU_UTILIZATION_MIN = 5 # Minimum % GPU usage expected
GPU_WARMUP_TIME = 30 # Seconds to wait before GPU check
```

### Experiment Status Values

```python
EXPERIMENT_STATUS = {
    "pending": "Not started",
    "running": "Currently executing",
    "running_detached": "Running in background (nohup)",
    "completed": "Finished successfully",
    "failed": "Error occurred",
    "quick_completion": "Completed very fast (check smoke test)",
    "timeout_polling": "Exceeded poll time limit",
    "gpu_underutilized": "GPU available but not being used"
}
```

---

## Functions

### 1. create_experiment_log_header

```python
def create_experiment_log_header(
    hypothesis_id: str,
    conda_env_name: str,
    entry_point: str,
    command: str,
    gpu_info: dict
) -> str:
    """
    Create formatted log header for experiment log file.

    Args:
        hypothesis_id: Hypothesis identifier (e.g., "h-e1")
        conda_env_name: Conda environment name
        entry_point: Entry point file name
        command: Full execution command
        gpu_info: GPU information dict from checkpoint

    Returns:
        Formatted log header string

    Usage:
        header = create_experiment_log_header(
            "h-e1", "youra-h-e1", "main.py",
            "python main.py --epochs 100",
            checkpoint.gpu
        )
        Write(f"{code_folder}/experiment.log", header)
    """
    from datetime import datetime

    gpu_str = gpu_info.get("info", "CPU only") if gpu_info.get("available") else "CPU only"
    gpu_count = gpu_info.get("count", 0) if gpu_info.get("available") else 0

    header = f"""
================================================================================
🧪 YouRA EXPERIMENT LOG
================================================================================
Hypothesis ID: {hypothesis_id}
Timestamp: {datetime.now().isoformat()}
Environment: {conda_env_name}
Entry Point: {entry_point}
Command: {command}
GPU: {gpu_str} (count: {gpu_count})
================================================================================
EXPERIMENT OUTPUT:
================================================================================

"""
    return header
```

### 2. launch_experiment_nohup

```python
def launch_experiment_nohup(
    conda_path: str,
    conda_env_name: str,
    code_folder: str,
    command: str
) -> dict:
    """
    Launch experiment with nohup for session-independent execution.

    Args:
        conda_path: Path to conda installation
        conda_env_name: Conda environment name
        code_folder: Path to code folder
        command: Python command to execute (without python prefix)

    Returns:
        Dictionary containing:
            - success: bool - Launch successful
            - pid: int - Process ID
            - log_file: str - Path to experiment log
            - pid_file: str - Path to PID file
            - error: str - Error message if failed

    Usage:
        result = launch_experiment_nohup(
            conda_path, conda_env_name, code_folder,
            "python main.py --epochs 100"
        )
        if result["success"]:
            print(f"Launched with PID: {result['pid']}")
    """
    from helpers.conda_environment import get_conda_init_command

    init_cmd = get_conda_init_command(conda_path)
    log_file = f"{code_folder}/experiment.log"
    pid_file = f"{code_folder}/experiment.pid"

    # Build nohup command
    launch_command = f"""
{init_cmd}
cd {code_folder}

# Run experiment with output to experiment.log
nohup conda run -n {conda_env_name} {command} >> experiment.log 2>&1 &

echo $! > experiment.pid
"""

    result = Bash(launch_command, description="Launch experiment with nohup")

    if not result.success:
        return {
            "success": False,
            "pid": None,
            "log_file": log_file,
            "pid_file": pid_file,
            "error": result.stderr
        }

    # Read PID from file
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
    except Exception as e:
        return {
            "success": False,
            "pid": None,
            "log_file": log_file,
            "pid_file": pid_file,
            "error": f"Failed to read PID: {e}"
        }

    return {
        "success": True,
        "pid": pid,
        "log_file": log_file,
        "pid_file": pid_file,
        "error": None
    }
```

### 3. check_process_running

```python
def check_process_running(pid: int) -> bool:
    """
    Check if a process is still running.

    Args:
        pid: Process ID to check

    Returns:
        True if process is running, False otherwise

    Usage:
        if check_process_running(12345):
            print("Still running...")
    """
    result = Bash(f"ps -p {pid} --no-headers 2>/dev/null")
    return result.success and result.stdout.strip() != ""
```

### 4. phased_error_check

```python
def phased_error_check(
    pid: int,
    log_file: str,
    check_intervals: list = None
) -> dict:
    """
    Perform phased error checking during early experiment execution.

    Waits progressively and checks for errors at each phase.
    Default phases: 30s, 90s, 180s, 240s (4 minutes total)

    Args:
        pid: Process ID to monitor
        log_file: Path to experiment log file
        check_intervals: Optional custom check intervals (cumulative seconds)

    Returns:
        Dictionary containing:
            - status: str - Final status after checks
            - phase_reached: int - Last phase checked (seconds)
            - error_detected: bool - Error found in log
            - error_message: str - Error message if found
            - process_running: bool - Whether process is still running

    Usage:
        result = phased_error_check(pid, f"{code_folder}/experiment.log")
        if result["error_detected"]:
            print(f"Error at {result['phase_reached']}s: {result['error_message']}")
    """
    import time

    if check_intervals is None:
        check_intervals = PHASED_CHECK_INTERVALS

    previous_wait = 0
    error_detected = False
    error_message = None
    final_status = "running"
    phase_reached = 0

    for phase in check_intervals:
        wait_time = phase - previous_wait
        print(f"⏳ Waiting {wait_time}s (total: {phase}s)...")
        time.sleep(wait_time)
        previous_wait = phase
        phase_reached = phase

        # Check process status
        process_running = check_process_running(pid)

        if not process_running:
            # Process terminated - check for errors
            try:
                with open(log_file, 'r') as f:
                    log_content = f.read()
            except:
                log_content = ""

            error_patterns = ["Error", "Exception", "Traceback"]
            if any(pattern in log_content for pattern in error_patterns):
                error_detected = True
                final_status = "failed"

                # Extract error message (last 500 chars of error-related content)
                for line in log_content.split('\n')[-50:]:
                    if any(pattern in line for pattern in error_patterns):
                        error_message = line[:200]
                        break

                log_event("ERROR", f"Experiment failed at {phase}s")
                break
            else:
                if phase < check_intervals[-1]:
                    print(f"⚠️ Process ended at {phase}s - checking if smoke test...")
                    continue
                else:
                    final_status = "quick_completion"
                    log_event("CHECK", f"Process completed at {phase}s (no errors)")
                    break
        else:
            print(f"✅ Process running at {phase}s check")

            if phase == check_intervals[-1]:
                final_status = "running_detached"
                log_event("CHECK", "Experiment stable after phased checks")
                print(f"✅ Experiment running stably after {phase//60}-minute check.")

    return {
        "status": final_status,
        "phase_reached": phase_reached,
        "error_detected": error_detected,
        "error_message": error_message,
        "process_running": check_process_running(pid)
    }
```

### 5. verify_gpu_utilization

```python
def verify_gpu_utilization(
    pid: int,
    gpu_available: bool,
    min_utilization: int = None
) -> dict:
    """
    Verify GPU is being utilized during experiment.

    Args:
        pid: Process ID to monitor
        gpu_available: Whether GPU is available
        min_utilization: Minimum expected GPU % (default: 5)

    Returns:
        Dictionary containing:
            - checked: bool - Check was performed
            - utilization: int - Current GPU utilization %
            - healthy: bool - GPU usage is sufficient
            - warning: str - Warning message if underutilized

    Usage:
        gpu_check = verify_gpu_utilization(pid, checkpoint.gpu.available)
        if not gpu_check["healthy"]:
            print(f"GPU underutilized: {gpu_check['utilization']}%")
    """
    import time

    if min_utilization is None:
        min_utilization = GPU_UTILIZATION_MIN

    if not gpu_available:
        return {
            "checked": False,
            "utilization": None,
            "healthy": True, # N/A - no GPU
            "warning": None
        }

    # Wait for training to start
    time.sleep(GPU_WARMUP_TIME)

    # Check if process still running
    if not check_process_running(pid):
        return {
            "checked": False,
            "utilization": None,
            "healthy": True,
            "warning": "Process completed before GPU check"
        }

    # Check GPU utilization
    result = Bash("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null")

    if not result.success:
        return {
            "checked": False,
            "utilization": None,
            "healthy": True,
            "warning": "nvidia-smi not available"
        }

    try:
        gpu_utilization = int(result.stdout.strip().split('\n')[0])
    except:
        return {
            "checked": True,
            "utilization": None,
            "healthy": True,
            "warning": "Could not parse GPU utilization"
        }

    healthy = gpu_utilization >= min_utilization

    if not healthy:
        warning = f"GPU underutilized: {gpu_utilization}% (expected >{min_utilization}%)"
        log_event("ERROR", warning)
    else:
        warning = None
        log_event("GPU", f"Utilization OK: {gpu_utilization}%")

    return {
        "checked": True,
        "utilization": gpu_utilization,
        "healthy": healthy,
        "warning": warning
    }
```

### 6. poll_experiment_completion

```python
def poll_experiment_completion(
    pid: int,
    max_poll_time: int = None,
    poll_interval: int = None
) -> dict:
    """
    Poll for experiment completion (UNATTENDED mode).

    Args:
        pid: Process ID to monitor
        max_poll_time: Maximum time to wait in seconds (default: 10 hours)
        poll_interval: Time between checks in seconds (default: 5 minutes)

    Returns:
        Dictionary containing:
            - completed: bool - Experiment finished
            - timeout: bool - Reached max poll time
            - total_waited: int - Total seconds waited
            - status: str - Final status

    Usage:
        result = poll_experiment_completion(pid)
        if result["completed"]:
            print(f"Finished after {result['total_waited']/3600:.1f} hours")
    """
    import time

    if max_poll_time is None:
        max_poll_time = MAX_POLL_TIME
    if poll_interval is None:
        poll_interval = POLL_INTERVAL

    total_waited = 0

    while check_process_running(pid) and total_waited < max_poll_time:
        time.sleep(poll_interval)
        total_waited += poll_interval

        hours = total_waited // 3600
        mins = (total_waited % 3600) // 60
        print(f"⏳ Still running... (waited: {hours}h {mins}m)")
        log_event("POLL", f"Experiment running: {hours}h {mins}m elapsed")

    process_running = check_process_running(pid)
    timeout = process_running and total_waited >= max_poll_time

    if timeout:
        status = "timeout_polling"
        log_event("TIMEOUT", f"Poll limit reached ({max_poll_time//3600}h)")
    elif not process_running:
        status = "completed"
        log_event("COMPLETE", "Experiment finished during polling")
    else:
        status = "running"

    return {
        "completed": not process_running,
        "timeout": timeout,
        "total_waited": total_waited,
        "status": status
    }
```

### 7. run_experiment (Main Function)

```python
def run_experiment(
    conda_path: str,
    conda_env_name: str,
    code_folder: str,
    command: str,
    hypothesis_id: str,
    gpu_info: dict,
    checkpoint: dict
) -> dict:
    """
    Main function: Complete experiment execution workflow.

    This orchestrates the full experiment lifecycle:
    1. Create log header
    2. Launch with nohup
    3. Phased error check
    4. GPU utilization verification
    5. Status tracking

    Args:
        conda_path: Path to conda installation
        conda_env_name: Conda environment name
        code_folder: Path to code folder
        command: Command to execute
        hypothesis_id: Hypothesis identifier
        gpu_info: GPU information from checkpoint
        checkpoint: Checkpoint dict for updates

    Returns:
        Dictionary containing:
            - success: bool - Experiment started/running
            - status: str - Current status
            - pid: int - Process ID
            - log_file: str - Path to log file
            - gpu_check: dict - GPU verification results
            - error: str - Error message if failed
            - needs_gpu_fix: bool - Requires GPU fix

    Usage:
        result = run_experiment(
            conda_path, conda_env_name, code_folder,
            "python main.py --epochs 100",
            "h-e1", checkpoint.gpu, checkpoint
        )
        if result["needs_gpu_fix"]:
            # Route to Step 2 for GPU fix
    """
    # Step 0: Create log header
    header = create_experiment_log_header(
        hypothesis_id,
        conda_env_name,
        command.split()[1] if "python" in command else command.split()[0],
        command,
        gpu_info
    )

    log_file = f"{code_folder}/experiment.log"
    Write(log_file, header)
    log_event("START", f"Experiment started: {command}")
    print(f"📋 Experiment log: {log_file}")

    # Step 1: Launch experiment
    launch_result = launch_experiment_nohup(
        conda_path, conda_env_name, code_folder, command
    )

    if not launch_result["success"]:
        return {
            "success": False,
            "status": "failed",
            "pid": None,
            "log_file": log_file,
            "error": launch_result["error"],
            "gpu_check": None,
            "needs_gpu_fix": False
        }

    pid = launch_result["pid"]

    # Update checkpoint with PID
    checkpoint["experiment_pid"] = pid
    checkpoint["experiment_started_at"] = datetime.now().isoformat()
    checkpoint["experiment_status"] = "running"

    # Step 2: Phased error check
    phase_result = phased_error_check(pid, log_file)

    if phase_result["error_detected"]:
        return {
            "success": False,
            "status": "failed",
            "pid": pid,
            "log_file": log_file,
            "error": phase_result["error_message"],
            "phase_result": phase_result,
            "gpu_check": None,
            "needs_gpu_fix": False
        }

    # Step 3: GPU utilization check (if running stably)
    gpu_check = None
    needs_gpu_fix = False

    if phase_result["status"] == "running_detached" and gpu_info.get("available"):
        gpu_check = verify_gpu_utilization(pid, gpu_info.get("available", False))

        if gpu_check["checked"] and not gpu_check["healthy"]:
            # Kill underutilizing experiment
            Bash(f"kill -9 {pid}")
            needs_gpu_fix = True

            return {
                "success": False,
                "status": "gpu_underutilized",
                "pid": pid,
                "log_file": log_file,
                "error": gpu_check["warning"],
                "phase_result": phase_result,
                "gpu_check": gpu_check,
                "needs_gpu_fix": True
            }

    return {
        "success": True,
        "status": phase_result["status"],
        "pid": pid,
        "log_file": log_file,
        "error": None,
        "phase_result": phase_result,
        "gpu_check": gpu_check,
        "needs_gpu_fix": False
    }
```

### 8. handle_resume

```python
def handle_resume(
    checkpoint: dict,
    code_folder: str
) -> dict:
    """
    Handle experiment resume from checkpoint.

    Args:
        checkpoint: Checkpoint dict with experiment state
        code_folder: Path to code folder

    Returns:
        Dictionary containing:
            - action: str - "continue_polling", "completed", "no_experiment"
            - status: str - Current status
            - result: dict - Poll result if applicable

    Usage:
        resume = handle_resume(checkpoint, code_folder)
        if resume["action"] == "continue_polling":
            # Wait for experiment
        elif resume["action"] == "completed":
            # Proceed to post-validation
    """
    experiment_status = checkpoint.get("experiment_status")
    pid = checkpoint.get("experiment_pid")

    if not experiment_status or experiment_status == "pending":
        return {
            "action": "no_experiment",
            "status": "pending",
            "result": None
        }

    if experiment_status == "running_detached":
        if check_process_running(pid):
            print("⏳ Experiment is still running. Waiting for completion (UNATTENDED)...")
            log_event("RESUME", f"Experiment still running (PID: {pid}). Auto-polling...")

            poll_result = poll_experiment_completion(pid)

            return {
                "action": "continue_polling" if poll_result["timeout"] else "completed",
                "status": poll_result["status"],
                "result": poll_result
            }
        else:
            print("✅ Experiment completed. Proceeding to post-validation...")
            return {
                "action": "completed",
                "status": "completed",
                "result": None
            }

    if experiment_status == "completed":
        return {
            "action": "completed",
            "status": "completed",
            "result": None
        }

    return {
        "action": "check_status",
        "status": experiment_status,
        "result": None
    }
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Launch failed | Command error | Check command syntax, paths |
| Failed at 30s | Quick crash | Check imports, config |
| GPU underutilized | CPU training | Add device placement code |
| Timeout polling | Very long experiment | May be normal, check manually |
| PID not found | Process ended | Check log for errors |
