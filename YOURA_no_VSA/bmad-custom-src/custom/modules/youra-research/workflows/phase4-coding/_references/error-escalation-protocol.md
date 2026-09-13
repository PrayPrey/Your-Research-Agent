# Error Escalation Protocol

> **Reference Document** - Used by step-05-experiment-execute.md

## Persistent Error Escalation Protocol

**CRITICAL: When errors persist after multiple fix attempts, escalate systematically.**

This protocol handles runtime errors that cannot be resolved by simple fixes. It:
1. **Always** registers errors as Archon Tasks (for tracking)
2. Attempts Quick Fix within Step 5 (up to 3 times)
3. Escalates to Step 2 (Coder-Validator loop) if Quick Fix fails
4. Stops and requests user intervention if escalation also fails

### 2f.1 Error Tracking Initialization

```
# Initialize error tracking in checkpoint (if not exists)
IF checkpoint.error_escalation NOT exists:
    checkpoint.error_escalation = {
        "quick_fix_attempts": 0,
        "step2_retries": 0,
        "error_history": [],
        "tasks_created": []
    }
```

### 2f.2 Persistent Error Detection

```
IF execution fails:
    error_info = {
        "error_type": "{type}",
        "error_message": "{message}",
        "file": "{file_path}",
        "line": {line_number},
        "traceback": "{full_traceback}",
        "timestamp": "{ISO8601}",
        "attempt": checkpoint.error_escalation.quick_fix_attempts + 1
    }

    checkpoint.error_escalation.error_history.append(error_info)
    checkpoint.error_escalation.quick_fix_attempts += 1
```

### 2f.3 Phase 3 Analysis (ALWAYS execute for persistent errors!)

**Cross-reference error with Phase 3 specification documents:**

```
Step 1: Load Phase 3 Documents
──────────────────────────────
prd_content = Read({prd_file})
architecture_content = Read({architecture_file})
logic_content = Read({logic_file})
config_content = Read({config_file})

Step 2: Search for Related Specifications
─────────────────────────────────────────
# Extract keywords from error
error_keywords = extract_keywords(error_info.error_message)

# Search in Phase 3 docs using Serena
FOR each keyword in error_keywords:
    mcp__serena__search_for_pattern(
        substring_pattern=keyword,
        relative_path="{hypothesis_folder}",
        paths_include_glob="03_*.md"
    )

Step 3: Analyze Alignment
─────────────────────────
analysis_result = {
    "prd_related": "{relevant PRD requirement or 'None found'}",
    "architecture_related": "{relevant architecture component or 'None found'}",
    "logic_related": "{relevant API spec or 'None found'}",
    "config_related": "{relevant config or 'None found'}",
    "root_cause_hypothesis": "{analysis of what went wrong}",
    "suggested_fix": "{recommended fix approach}"
}
```

### 2f.4 Archon Task Registration (ALWAYS!)

**Every persistent error MUST be registered as an Archon Task for tracking.**

```
# Create Archon Task for error tracking
task_result = mcp__archon__manage_task(
    action="create",
    project_id="{archon_project_id}",
    title="[RUNTIME ERROR] {error_type}: {brief_description}",
    description="""
## Error Context
- **File**: {file}:{line}
- **Type**: {error_type}
- **Message**: {error_message}
- **Attempt**: {attempt}/{max_quick_fix_attempts}

## Traceback
```
{traceback}
```

## Phase 3 Analysis
### Related PRD Requirement
{prd_related}

### Related Architecture Component
{architecture_related}

### Related Logic Specification
{logic_related}

### Related Config
{config_related}

## Root Cause Hypothesis
{root_cause_hypothesis}

## Suggested Fix Approach
{suggested_fix}

## Test Case to Add (for Validator)
```python
def test_{error_type_snake_case}():
    '''Regression test for runtime error at {file}:{line}'''
    # TODO: Implement test that catches this error
    pass
```
""",
    status="todo",
    task_order=100, # High priority
    feature="runtime-error-fix"
)

# Track created task
checkpoint.error_escalation.tasks_created.append(task_result.task_id)

Display:
"════════════════════════════════════════
 📝 Error Registered in Archon
════════════════════════════════════════
 Task ID: {task_result.task_id}
 Title: [RUNTIME ERROR] {error_type}
 Status: todo

 Phase 3 Analysis: {root_cause_hypothesis}
════════════════════════════════════════"
```

### 2f.5 Quick Fix Attempt (Within Step 5)

```
IF checkpoint.error_escalation.quick_fix_attempts <= {max_quick_fix_attempts}:

    Display:
    "════════════════════════════════════════
     🔧 Quick Fix Attempt {attempt}/{max_quick_fix_attempts}
    ════════════════════════════════════════"

    # Step 1: Search Archon KB for solution
    archon_results = mcp__archon__rag_search_knowledge_base(
        query="{error_type} {error_message} fix",
        match_count=5
    )

    archon_code = mcp__archon__rag_search_code_examples(
        query="{error_type} solution python pytorch",
        match_count=3
    )

    # Step 2: Exa fallback if Archon insufficient
    IF len(archon_results) + len(archon_code) < 3:
        Log: "Archon KB insufficient → Using Exa fallback"

        exa_code = mcp__exa__get_code_context_exa(
            query="{error_type} {framework} fix example"
        )

        exa_web = mcp__exa__web_search_exa(
            query="{error_type} {error_message} solution"
        )

    # Step 3: Use Serena to locate error in code
    mcp__serena__search_for_pattern(
        substring_pattern="{error_location_pattern}",
        relative_path="{code_folder}",
        context_lines_before=5,
        context_lines_after=5
    )

    # Step 4: Apply fix based on KB/Exa suggestions
    IF auto_fix_possible:
        Apply fix using Edit tool or Serena MCP

        # Step 5: Re-run experiment
        Re-execute experiment command

        IF success:
            Display: "✅ Quick Fix successful!"

            # Update Archon task
            mcp__archon__manage_task(
                action="update",
                task_id="{created_task_id}",
                status="done",
                description=original_description + "\n\n## Resolution\nFixed by Quick Fix in Step 5.\nFix applied: {fix_description}"
            )

            # Reset error tracking
            checkpoint.error_escalation.quick_fix_attempts = 0

            → Continue to Section 2c (Parse Results)
        ELSE:
            Display: "❌ Quick Fix attempt {attempt} failed"
            → Loop back to 2f.2 (next attempt)
    ELSE:
        Display: "⚠️ No auto-fix available for this error type"

        # Offer manual fix option
        Display: "[M] Manual fix (you edit) [S] Skip to Step 2 escalation [Q] Quit"
```

### 2f.6 Step 2 Escalation (After Quick Fix Exhausted)

```
IF checkpoint.error_escalation.quick_fix_attempts > {max_quick_fix_attempts}:

    IF checkpoint.error_escalation.step2_retries < {max_step2_retries}:

        Display:
        "════════════════════════════════════════
         ⚠️ Quick Fix Exhausted - Escalating to Step 2
        ════════════════════════════════════════
         Quick Fix Attempts: {quick_fix_attempts}/{max_quick_fix_attempts}
         Step 2 Retries: {step2_retries}/{max_step2_retries}

         Escalating to Coder-Validator loop for systematic fix.

         Created Tasks:
         {FOR each task_id in tasks_created:}
           - {task_id}

         The Coder will:
         1. Review error context in task description
         2. Apply fix based on Phase 3 analysis
         3. Add test case to catch this error

         The Validator will:
         1. Run new test case
         2. Verify error is resolved
        ════════════════════════════════════════"

        # Update checkpoint for Step 2 return
        checkpoint.error_escalation.step2_retries += 1
        checkpoint.return_to_step5_after_coder = true
        checkpoint.step5_error_context = error_info

        # Save checkpoint (includes all escalation state for recovery)
        SAVE checkpoint

        Display: "→ Returning to Step 2 (Coder Loop)..."

        # Load Step 2
        Load, read entire file, then execute {coderStepFile}

    ELSE:
        # Max retries exhausted
        → Execute Section 2f.7 (User Intervention)
```

### 2f.7 User Intervention (Final Fallback)

```
IF checkpoint.error_escalation.step2_retries >= {max_step2_retries}:

    Display:
    "════════════════════════════════════════
     🛑 AUTOMATIC ERROR RESOLUTION EXHAUSTED
    ════════════════════════════════════════

     Quick Fix Attempts: {quick_fix_attempts}/{max_quick_fix_attempts}
     Step 2 Retries: {step2_retries}/{max_step2_retries}

     The following errors could not be automatically resolved:

     {FOR each error in error_history:}
     ────────────────────────────────────────
     Error {n}: {error_type}
     File: {file}:{line}
     Message: {error_message}
     ────────────────────────────────────────

     Created Archon Tasks:
     {FOR each task_id in tasks_created:}
       - {task_id}: {task_title}

     Recommended Actions:
     1. Review error details in Archon tasks
     2. Manually debug the code
     3. Check Phase 3 specifications for mismatches
     4. Consider revising hypothesis if fundamental issue

    ════════════════════════════════════════"

    Display: "[M] Manual fix and retry [S] Skip experiment [P] Proceed with partial results [Q] Quit"

    IF M:
        Display: "Please fix the code manually. Enter 'done' when ready to retry."
        Wait for user input
        Reset checkpoint.error_escalation.quick_fix_attempts = 0
        → Return to Section 2b (Execute Main Experiment)

    IF S:
        → Execute Section 5 (Skip Mode)

    IF P:
        Create partial results with error info
        → Execute Section 6 (Save Results)

    IF Q:
        Save checkpoint
        Exit workflow
```

### 2f.8 Test Case Generation Hint

**When creating Archon Task, include a test case template for Validator:**

```python
# Test case template to add in tests/test_runtime_errors.py

def test_{error_type_snake_case}_at_{file_name}_{line}():
    '''
    Regression test for runtime error.

    Error: {error_type}
    Location: {file}:{line}
    Original message: {error_message}

    This test ensures the error does not recur after fix.
    '''
    # Import the module that caused the error
    from {module} import {function_or_class}

    # Reproduce the conditions that caused the error
    # TODO: Coder should implement specific test logic

    # Assert that no error occurs
    # OR assert specific behavior that was failing
    pass
```

**This test case will be:**
1. Created by Coder in Step 2
2. Validated by Validator in Step 3
3. Ensures the same error won't reach Step 5 again
