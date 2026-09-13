---
name: 'entry_point_detection'
description: 'Reusable functions for dynamic Python entry point discovery in Phase 4 experiment execution'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - discover_entry_point
  - find_main_file
  - parse_cli_arguments
  - construct_run_command
  - validate_entry_point

# Called By
called_by:
  - 'phase4-coding/steps/step-04-experiment-confirm.md'
  - 'phase4-coding/steps/step-05a-pre-validation.md'
---

# Entry Point Detection Helper Functions

> Reusable functions for dynamic Python entry point discovery in Phase 4 experiment execution.
> Uses Serena MCP for intelligent code analysis to find main entry points and CLI arguments.

---

## Constants

```python
# Files to check for main entry point (in priority order)
ENTRY_POINT_PRIORITY = ["main.py", "run.py", "run_experiment.py", "train.py", "experiment.py"]

# Patterns that indicate entry point capability
MAIN_BLOCK_PATTERN = r"if __name__.*==.*['\"]__main__['\"]"

# Quick mode argument patterns
QUICK_MODE_ARGS = ["--quick", "--smoke", "--dry-run", "--test", "--debug", "--fast"]
MINIMAL_RUN_ARGS = ["--epochs=1", "--max_steps=1", "--max_epochs=1"]
```

---

## Functions

### 1. discover_entry_point (Main Function)

```python
def discover_entry_point(code_folder: str, default_args: str = "") -> dict:
    """
    Complete entry point discovery workflow.
    Orchestrates code analysis, entry point detection, CLI argument discovery,
    and execution plan construction.

    Args:
        code_folder: Path to code directory
        default_args: Default arguments from config (optional)

    Returns:
        Dictionary containing:
            - success: bool
            - execution_plan: dict (entry_point, command, has_quick_mode, etc.)
            - entry_point: str - Entry point file path
            - candidates: list - All entry point candidates
            - cli_info: dict - CLI argument information
            - error: str - Error message if failed

    Usage:
        result = discover_entry_point(code_folder, "--epochs 100")
        if result["success"]:
            plan = result["execution_plan"]
            print(f"Command: {plan['command']}")
    """
    try:
        # ─────────────────────────────────────────────────────────────
        # Step 1: Analyze code structure (list Python files)
        # ─────────────────────────────────────────────────────────────
        dir_result = mcp__serena__list_dir(relative_path=code_folder, recursive=True)
        files = dir_result.get("files", [])
        python_files = [f for f in files if f.endswith(".py")]

        structure = {
            "files": python_files,
            "total_files": len(python_files),
            "has_main": "main.py" in [os.path.basename(f) for f in python_files],
            "has_requirements": "requirements.txt" in files
        }
        print(f"📂 Found {structure['total_files']} Python files")

        # ─────────────────────────────────────────────────────────────
        # Step 2: Find entry point candidates (if __name__ == "__main__")
        # ─────────────────────────────────────────────────────────────
        search_result = mcp__serena__search_for_pattern(
            substring_pattern=MAIN_BLOCK_PATTERN,
            relative_path=code_folder,
            context_lines_after=5
        )

        candidates = []
        for match in search_result.get("matches", []):
            file_path = match.get("file", "")
            file_name = os.path.basename(file_path)
            priority = ENTRY_POINT_PRIORITY.index(file_name) if file_name in ENTRY_POINT_PRIORITY else 100
            candidates.append({"file": file_path, "file_name": file_name, "priority": priority})

        candidates.sort(key=lambda x: x["priority"])

        if not candidates:
            return {"success": False, "error": "No entry point candidates found", "candidates": [], "structure": structure}

        print(f"🔍 Found {len(candidates)} entry point candidates")

        # ─────────────────────────────────────────────────────────────
        # Step 3: Select best candidate
        # ─────────────────────────────────────────────────────────────
        entry_point = candidates[0]["file"]
        print(f"✅ Selected entry point: {entry_point}")

        # ─────────────────────────────────────────────────────────────
        # Step 4: Detect CLI arguments
        # ─────────────────────────────────────────────────────────────
        argparse_result = mcp__serena__search_for_pattern(
            substring_pattern=r"add_argument\s*\(['\"]--?([a-zA-Z_-]+)['\"]",
            relative_path=entry_point,
            context_lines_after=2
        )

        detected_args = []
        for match in argparse_result.get("matches", []):
            import re
            arg_match = re.search(r"add_argument\s*\(['\"]--?([a-zA-Z_-]+)['\"]", match.get("context", ""))
            if arg_match:
                detected_args.append(f"--{arg_match.group(1)}")

        # Check for quick mode
        has_quick_mode = False
        quick_arg = None
        for qarg in QUICK_MODE_ARGS:
            if any(qarg in arg for arg in detected_args):
                has_quick_mode = True
                quick_arg = qarg
                break

        cli_info = {
            "detected_args": detected_args,
            "has_quick_mode": has_quick_mode,
            "quick_arg": quick_arg
        }
        print(f"🔧 Detected {len(detected_args)} CLI arguments")

        # ─────────────────────────────────────────────────────────────
        # Step 5: Construct execution plan
        # ─────────────────────────────────────────────────────────────
        file_name = os.path.basename(entry_point)
        execution_plan = {
            "entry_point": file_name,
            "entry_point_path": entry_point,
            "command": f"python {file_name} {default_args}".strip(),
            "has_quick_mode": has_quick_mode,
            "detected_args": detected_args,
            "is_full_run": not has_quick_mode,
            "smoke_test_command": None
        }

        if has_quick_mode:
            execution_plan["smoke_test_command"] = f"python {file_name} {quick_arg}"
            execution_plan["command"] = execution_plan["smoke_test_command"]
            print(f"⚡ Quick mode available: {quick_arg}")

        return {
            "success": True,
            "execution_plan": execution_plan,
            "entry_point": entry_point,
            "candidates": candidates,
            "cli_info": cli_info,
            "structure": structure,
            "error": None
        }

    except Exception as e:
        return {"success": False, "error": str(e), "candidates": [], "execution_plan": None}
```

### 2. remove_quick_args (Utility)

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
    quick_args = QUICK_MODE_ARGS + MINIMAL_RUN_ARGS
    tokens = command.split()
    filtered = [t for t in tokens if not any(q in t for q in quick_args)]
    return " ".join(filtered)
```

---

## Usage Example

```python
# In step-05b-execution.md
result = discover_entry_point(code_folder, default_args)

IF result["success"]:
    execution_plan = result["execution_plan"]
    checkpoint.execution_plan = execution_plan
    SAVE checkpoint

    IF execution_plan["has_quick_mode"]:
        # Phase 1: Smoke test
        run_experiment(execution_plan["smoke_test_command"])

        # Phase 2: Full run (after smoke test passes)
        full_command = remove_quick_args(execution_plan["command"])
        run_experiment(full_command)
    ELSE:
        run_experiment(execution_plan["command"])
ELSE:
    log_event("ERROR", f"Entry point discovery failed: {result['error']}")
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No candidates found | No `if __name__` blocks | Check if code uses different entry pattern |
| Multiple candidates | Ambiguous entry point | Prefer main.py > run.py > train.py |
| No CLI args detected | Uses config file | Pass config path as default_args |
| Quick mode not found | No smoke test support | Run full experiment directly |
