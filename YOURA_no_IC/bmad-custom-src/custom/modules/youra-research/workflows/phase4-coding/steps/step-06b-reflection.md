---
name: 'step-06b-reflection'
description: 'Automatic Reflection - LLM self-assessment with SUPERSEDED and SHOULD_WORK handling'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# File References
thisStepFile: '{workflow_path}/steps/step-06b-reflection.md'
nextStepFile: '{workflow_path}/steps/step-07-report-generation.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
verification_state: '{research_folder}/verification_state.yaml'
experiment_results: '{hypothesis_folder}/experiment_results.json'
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'

# Output Files
reflection_report: '{hypothesis_folder}/reflection_report.md'
---

## Helper References (BMAD v6)

<helper-reference>
**Helper:** `{helpers_path}/llm_self_assessment.md`
**Function:** `perform_llm_self_assessment(hypothesis_id, pass_rate, failed_checks, verification_state)`
**Returns:** `{decision, checkpoint_updates, reasoning, assessment_result, dependents}`
**Use For:** MUST_WORK gates (4-question compatibility assessment)
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/llm_self_assessment_should_work.md`
**Function:** `perform_llm_self_assessment_should_work(hypothesis_id, pass_rate, failed_checks, experiment_summary)`
**Returns:** `{decision, checkpoint_updates, reasoning, modification_suggestion}`
**Use For:** SHOULD_WORK gates (2-question improvement assessment, no cascade handling)
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/serena_memory_patterns.md`
**Functions:** `save_pivot_record()`, `save_failure_record()`, `save_superseded_record()`, `save_limitation_record()`
**Purpose:** Persist reflection outcomes to Serena Memory for cross-phase learning
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/archon_cascade.md`
**Functions:** `find_dependent_hypotheses()`, `update_verification_state_cascade()`, `update_dependent_hypothesis_tasks()`, `mark_hypothesis_superseded()`
**Purpose:** Handle cascade effects on dependent hypotheses
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/archon_phase_reset.md`
**Functions:** `reset_phase_tasks()`, `terminate_pipeline_on_phase0_routing()`
**Purpose:** Reset/terminate Archon Pipeline tasks on routing
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/archive_helpers.md`
**Functions:** `archive_for_phase0_routing()`, `archive_for_phase2a_routing()`
**Purpose:** Archive research files before Phase 0 or Phase 2A-Dialogue routing
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/checkpoint_helpers.md`
**Function:** `update_checkpoint(checkpoint, updates, checkpoint_file)`
**Purpose:** Update and persist checkpoint state
</helper-reference>

<helper-reference>
**Helper:** `{helpers_path}/deferred_archon_operations.md`
**Functions:** `prepare_archon_operations_context()`, `add_dependents_to_context()`
**Purpose:** Prepare deferred Archon operations context for Step 08 execution
</helper-reference>

---

## GOTO FLOW CONVENTION

<critical>
**GOTO = Jump to section AND CONTINUE sequentially from there**

When you see `GOTO Section_X`, execute Section_X and then CONTINUE executing all subsequent sections in order until you reach Section 9.

```
GOTO Section_5a → Execute 5a → 6 → 7 → 8 → 9
GOTO Section_5b → Execute 5b → 8 → 9 (skip 6, 7 for simple FAILED)
GOTO Section_5c → Execute 5c → 6 → 7 → 8 → 9
GOTO Section_6 → Execute 6 → 7 → 8 → 9
GOTO Section_7 → Execute 7 → 8 → 9
```

**NEVER stop at a GOTO target section. ALWAYS continue to Section 9.**
</critical>

---

## Section 0.5: Load Checkpoint (MANDATORY)

> Always read checkpoint at step entry to handle context loss in UNATTENDED mode.
> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 6:
    STOP("ERROR: Step sequence violation. Current step: {checkpoint.current_step}")

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, gate_result={checkpoint.gate_result}")
```

---

# Step 6B: Automatic Reflection (UNATTENDED Mode)

> **Mode:** UNATTENDED | **Trigger:** PARTIAL/FAIL for MUST_WORK or SHOULD_WORK (self-recovery) gates (DETERMINES_SUCCESS is Phase 5 only)

---

## STEP GOAL

Analyze experiment results for "meaningful findings" and determine outcome:

| Gate Type | Outcome | Description | Next Action |
|-----------|---------|-------------|-------------|
| MUST_WORK | **SELF_MODIFY** | Minor issues, can retry | Create new version, retry Phase 2C |
| MUST_WORK | **SUPERSEDED** | Fundamental redesign needed | Mark SUPERSEDED, route to `/phase2a-dialogue` |
| MUST_WORK | **FAIL** | Complete failure | Mark FAILED, route to Phase 0 |
| SHOULD_WORK | **SELF_MODIFY** | Self-recovery attempt | Retry validation (no routing) |
| SHOULD_WORK | **LIMITATION_RECORDED** | Max retries reached | Record limitation, continue to Phase 5 |

> SHOULD_WORK gates trigger reflection for self-recovery only (no Phase 0/2A routing).

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- Objective analysis - you are an analyzer, not an advocate
- Document all findings regardless of outcome
- No empty modifications - must have meaningful findings to modify
- Max attempts read from `failure_routing.phase4_must_pass_partial.max_attempts`

---

## EXECUTION SEQUENCE

### 1. Load Context

```python
Read(verification_state)
Read(experiment_results)

hypothesis_id = current_hypothesis
modification_attempt = hypothesis_data.modification_attempt
max_modification_attempts = failure_routing.phase4_must_pass_partial.max_attempts # Default: 1

# Check gate type and reflection mode
gate_type = checkpoint.get("partial_results", {}).get("gate_type", "MUST_WORK")
reflection_may_route = checkpoint.get("reflection_may_route", True)
reflection_type = checkpoint.get("reflection_type", "standard")
```

### 1b. SHOULD_WORK Gate Handling

> SHOULD_WORK supports LLM assessment for SELF_MODIFY decision after max retries.
> - `self_recovery`: Simplified analysis (retries 1-3)
> - `llm_assessment_should_work`: LLM-based SELF_MODIFY decision (after retry 3)
>
> **Reference:** `{llm_self_assessment_should_work}` for detailed implementation

```python
IF gate_type == "SHOULD_WORK":

    # ========================================================================
    # CASE 1: Self-recovery mode (retries 1-3)
    # ========================================================================
    IF reflection_type == "self_recovery":
        should_work_retry = checkpoint.get("should_work_retry_count", 0)
        max_retries = 3 # From GATE_TYPES["SHOULD_WORK"]["max_retries"]

        IF should_work_retry <= max_retries:
            # Attempt self-recovery analysis (simplified - no LLM assessment needed)
            Display: f"🔄 SHOULD_WORK self-recovery attempt {should_work_retry}/{max_retries}"

            # Analyze experiment results for modification opportunity
            IF can_identify_improvement():
                # SELF_MODIFY - retry with modifications
                checkpoint.reflection_outcome = "SELF_MODIFY"
                checkpoint.should_work_modification = True
                SAVE checkpoint
                Display: "✓ SHOULD_WORK: Self-modification identified, retrying validation"
                GOTO Section_5a # Create new version for retry

            ELSE:
                # No improvement found - record limitation and continue
                checkpoint.reflection_outcome = "LIMITATION_RECORDED"
                checkpoint.should_work_failed = True
                checkpoint.limitation_note = f"{hypothesis_id}: SHOULD_WORK gate failed - no improvement path found"
                SAVE checkpoint

                # Save to Serena Memory for cross-phase learning
                from serena_memory_patterns import save_limitation_record
                save_limitation_record(
                    hypothesis_id,
                    "SHOULD_WORK",
                    f"No improvement path found after {should_work_retry} self-recovery attempts",
                    checkpoint.get("partial_results", {}).get("failed_checks", []),
                    checkpoint.get("partial_results", {}),
                    checkpoint.get("experiment_summary")
                )

                Display: f"⚠ SHOULD_WORK: No improvement path - recording limitation"
                GOTO Section_7 # Save reflection report, then continue to Phase 5

    # ========================================================================
    # CASE 2: LLM Assessment mode (after max retries)
    # ========================================================================
    ELIF reflection_type == "llm_assessment_should_work":
        # LLM decides SELF_MODIFY (Phase 2C) or FAIL (record limitation)
        Display: f"🤖 SHOULD_WORK: Triggering LLM assessment for SELF_MODIFY decision"

        from llm_self_assessment_should_work import perform_llm_self_assessment_should_work

        # Get experiment summary from checkpoint/results
        experiment_summary = checkpoint.get("experiment_summary", "")
        pass_rate = checkpoint.get("partial_results", {}).get("pass_rate", 0.0)
        failed_checks = checkpoint.get("partial_results", {}).get("failed_checks", [])

        # Execute LLM assessment
        result = perform_llm_self_assessment_should_work(
            hypothesis_id,
            pass_rate,
            failed_checks,
            experiment_summary
        )

        # Update checkpoint with assessment results
        checkpoint.update(result["checkpoint_updates"])

        IF result["decision"] == "SELF_MODIFY":
            # SELF_MODIFY: Create new version, route to Phase 2C
            Display: f"✓ SHOULD_WORK LLM: SELF_MODIFY - routing to Phase 2C"
            Display: f" Modification suggestion: {result.get('modification_suggestion', 'See assessment')}"

            checkpoint.reflection_outcome = "SELF_MODIFY"
            checkpoint.route_to = "phase2c" # Route to Phase 2C (not Phase 0/2A)
            SAVE checkpoint
            GOTO Section_5a # Create new version for Phase 2C

        ELSE:
            # FAIL: Record limitation, continue to Phase 5
            Display: f"⚠ SHOULD_WORK LLM: Recording limitation - {result['reasoning']}"

            checkpoint.reflection_outcome = "LIMITATION_RECORDED"
            checkpoint.should_work_failed = True
            checkpoint.limitation_note = f"{hypothesis_id}: {result['reasoning']}"
            SAVE checkpoint

            # Save to Serena Memory for cross-phase learning
            from serena_memory_patterns import save_limitation_record
            save_limitation_record(
                hypothesis_id,
                "SHOULD_WORK",
                result['reasoning'],
                failed_checks,
                {"pass_rate": pass_rate},
                experiment_summary
            )

            GOTO Section_7 # Save reflection report, then continue to Phase 5

    # ========================================================================
    # CASE 3: Unknown reflection_type (fallback)
    # ========================================================================
    ELSE:
        # Fallback: Record limitation and continue
        checkpoint.reflection_outcome = "LIMITATION_RECORDED"
        checkpoint.should_work_failed = True
        checkpoint.limitation_note = f"{hypothesis_id}: SHOULD_WORK gate failed - unknown reflection type"
        SAVE checkpoint

        # Save to Serena Memory for cross-phase learning
        from serena_memory_patterns import save_limitation_record
        save_limitation_record(
            hypothesis_id,
            "SHOULD_WORK",
            f"Unknown reflection type: {reflection_type}",
            checkpoint.get("partial_results", {}).get("failed_checks", [])
        )

        GOTO Section_7

# Continue with standard MUST_WORK gate handling below...
```

### 2. Check Modification Limit & Route

```python
from checkpoint_helpers import update_checkpoint

# FAIL → Route to Phase 0 (fundamental flaw)
IF gate_result == "FAIL":
    hypotheses[hypothesis_id].status = "FAILED"
    update_checkpoint(checkpoint, {
        "reflection_outcome": "ROUTED_TO_PHASE_0",
        "route_to": "Phase 0"
    }, checkpoint_file)
    GOTO Section_6 # Save Failure Record

# PARTIAL + max attempts → Route based on config
ELIF modification_attempt >= max_modification_attempts:
    GOTO Section_2b # LLM Self-Assessment
```

**Initial Routing Matrix:**

| Gate Result | Attempts | Next Section |
|-------------|----------|--------------|
| FAIL | Any | Section 6 (Phase 0) |
| PARTIAL | < max | Section 3 (Analysis) |
| PARTIAL | >= max | Section 2b (LLM Self-Assessment) |

### 2b. LLM Self-Assessment for PARTIAL Results

> **REFERENCE:** Read `{llm_self_assessment}` for detailed implementation

**Use the `perform_llm_self_assessment()` function from helper:**

```python
# See: {llm_self_assessment}

assessment = perform_llm_self_assessment(
    hypothesis_id,
    pass_rate,
    failed_checks,
    verification_state
)

IF assessment["decision"] == "SELF_MODIFY":
    checkpoint.update(assessment["checkpoint_updates"])
    SAVE checkpoint
    GOTO Section_3 # Continue with modification analysis
ELSE:
    checkpoint.update(assessment["checkpoint_updates"])
    SAVE checkpoint
    GOTO Section_5c # SUPERSEDED handling
```

**Key Helper Functions:**
- `build_assessment_prompt()` - Build 4-question prompt
- `execute_assessment()` - Run via ClearThought or manual LLM
- `determine_decision()` - Apply decision matrix

**Decision Matrix (from helper):**

| Interface | Data Flow | Behavior | Recovery | → Decision |
|-----------|-----------|----------|----------|------------|
| ✓ | ✓ | ✓ | ✓ | SELF_MODIFY |
| ✓ | ✓ | ✓ | ✗ | SUPERSEDED |
| Any ✗ | Any | Any | Any | SUPERSEDED |

### 3. Structured Reflection Analysis

**With ClearThought MCP (if available):**
```python
IF mcp__clearThought available:
    mcp__clearThought__scientificmethod(
        hypothesis=hypothesis_statement,
        observation=experiment_results_summary,
        analysis_type="failure_analysis"
    )
```

**Analyze (ClearThought or manual):**
1. What succeeded (metrics that met targets)
2. What failed (metrics that missed significantly)
3. Root cause analysis
4. Key insights
5. Modification potential assessment

### 4. Determine "Meaningful Findings"

**Decision Logic:**
```python
meaningful_findings = FALSE

IF (partial_success AND actionable_insight):
    meaningful_findings = TRUE
    modification_type = "PARAMETER_ADJUSTMENT"

ELIF (identified_mechanism AND scope_clarity):
    meaningful_findings = TRUE
    modification_type = "SCOPE_REDUCTION"

ELIF (gate_result == "PARTIAL" AND any_metric_improved > 50%):
    meaningful_findings = TRUE
    modification_type = "REFINEMENT"
```

### 5. Execute Decision

#### 5a. IF meaningful_findings == TRUE → Create New Version

```python
new_hypothesis_id = f"{original_hypothesis_id}-v{current_version + 1}"

# Update verification_state
hypotheses[hypothesis_id].status = "COMPLETED"
hypotheses[hypothesis_id].reflection = {
    "triggered": True,
    "has_meaningful_findings": True,
    "modification_rationale": rationale
}

# Create new hypothesis entry
hypotheses[new_hypothesis_id] = {
    "version": current_version + 1,
    "modified_from": hypothesis_id,
    "modification_attempt": modification_attempt + 1,
    "statement": proposed_statement,
    "status": "READY",
    "gate": same_gate_config
}

checkpoint.reflection_outcome = "MODIFIED"
checkpoint.new_hypothesis_id = new_hypothesis_id
```

**→ CONTINUE TO Section 6 (Save to Serena Memory)**

#### 5b. IF meaningful_findings == FALSE → Mark as FAILED

```python
hypotheses[hypothesis_id].status = "FAILED"
checkpoint.reflection_outcome = "FAILED"
```

**→ CONTINUE TO Section 8 (Save Reflection Report)** *(skip Section 6, 7 for simple FAILED)*

#### 5c. IF SUPERSEDED → Mark as SUPERSEDED and Route to `/phase2a-dialogue`

```python
new_hypothesis_id = f"{hypothesis_id.split('-v')[0]}-v{current_version + 1}"

# Mark current hypothesis as SUPERSEDED
hypotheses[hypothesis_id].status = "SUPERSEDED"
hypotheses[hypothesis_id].superseded = {
    "superseded_by": new_hypothesis_id,
    "superseded_at": datetime.now().isoformat(),
    "superseded_reason": "LLM self-assessment determined incompatibility"
}

# Create placeholder for new hypothesis
hypotheses[new_hypothesis_id] = {
    "version": current_version + 1,
    "supersedes": hypothesis_id,
    "statement": "To be defined in /phase2a-dialogue",
    "status": "READY"
}

# Update checkpoint
checkpoint.reflection_outcome = "ROUTED_TO_PHASE_2A"
checkpoint.superseded_hypothesis_id = hypothesis_id
checkpoint.new_hypothesis_id = new_hypothesis_id
checkpoint.route_to = "phase2a-dialogue" # Workflow/Skill name

SAVE checkpoint
SAVE verification_state
```

**→ CONTINUE TO Section 6 (Save to Serena Memory)**

### 6. Save to Serena Memory

> **REFERENCE:** Read `{serena_memory_patterns}` for detailed implementation

**Use helpers for Serena Memory persistence:**

```python
# See: {serena_memory_patterns}

IF reflection_outcome == "MODIFIED":
    save_pivot_record(
        hypothesis_id,
        new_hypothesis_id,
        modification_type,
        lessons_learned
    )

ELIF reflection_outcome in ["FAILED", "ROUTED_TO_PHASE_0"]:
    save_failure_record(
        hypothesis_id,
        "Phase 4",
        "MUST_WORK_FAIL",
        {"gate_result": gate_result},
        root_causes,
        lessons_learned
    )

ELIF reflection_outcome == "ROUTED_TO_PHASE_2A":
    # Collect passed SHOULD_WORK hypotheses for preservation
    passed_should_work = collect_passed_should_work(verification_state)

    save_superseded_record(
        hypothesis_id,
        new_hypothesis_id,
        assessment["reasoning"],
        assessment["assessment_result"],
        assessment["dependents"],
        passed_should_work
    )
```

**Key Helper Functions:**
- `save_pivot_record()` - Save modification record
- `save_failure_record()` - Save failure with lessons
- `save_superseded_record()` - Save with compatibility analysis

**→ CONTINUE TO Section 7 (Record Routing Decision)**

### 7. Record Routing Decision & Update Local State

> Archon/Archive/Terminate operations are DEFERRED to Step 08 (after Report generation).
>
> **Reference:** `{deferred_archon_operations}`, `{archon_cascade}`

```python
from deferred_archon_operations import prepare_archon_operations_context, add_dependents_to_context
from archon_cascade import find_dependent_hypotheses, update_verification_state_cascade

# ============================================================================
# STEP 1: Prepare deferred Archon operations context
# ============================================================================
checkpoint = prepare_archon_operations_context(
    checkpoint=checkpoint,
    checkpoint_file=checkpoint_file,
    verification_state=verification_state,
    hypothesis_id=hypothesis_id,
    reflection_outcome=reflection_outcome,
    modification_attempt=modification_attempt,
    new_hypothesis_id=checkpoint.get("new_hypothesis_id"),
    failure_reason=checkpoint.get("failure_reason")
)

# ============================================================================
# STEP 2: Update verification_state cascade (LOCAL state only)
# ============================================================================
dependents = find_dependent_hypotheses(verification_state, hypothesis_id)
IF len(dependents) > 0:
    IF reflection_outcome == "SELF_MODIFY":
        update_verification_state_cascade(verification_state, "BLOCKED", hypothesis_id, dependents, new_hypothesis_id)
    ELIF reflection_outcome == "ROUTED_TO_PHASE_2A":
        update_verification_state_cascade(verification_state, "CASCADE_SUPERSEDED", hypothesis_id, dependents, new_hypothesis_id)
    ELIF reflection_outcome in ["FAILED", "ROUTED_TO_PHASE_0"]:
        update_verification_state_cascade(verification_state, "CASCADE_FAILED", hypothesis_id, dependents)

    SAVE verification_state
    Log(f"✓ verification_state cascade updated for {len(dependents)} dependents")

    # Add dependents to context for Step 08 Archon cascade
    checkpoint = add_dependents_to_context(checkpoint, checkpoint_file, dependents)
```

**→ CONTINUE TO Section 8 (Save Reflection Report)**

### 8. Save Reflection Report

```python
Write("{hypothesis_folder}/reflection_report.md", reflection_report_content)
```

**→ CONTINUE TO Section 9 (PROCEED TO STEP 7)**

---

## 9. PROCEED TO STEP 7

### UNATTENDED Auto-Proceed

Display: "**Proceeding to Step 7 (Report Generation)...**"

#### Menu Handling Logic:

Pass to Step 7:
- `reflection_outcome`: SELF_MODIFY | MODIFIED | FAILED | ROUTED_TO_PHASE_0 | ROUTED_TO_PHASE_2A
- `new_hypothesis_id`: (if SELF_MODIFY, MODIFIED, or ROUTED_TO_PHASE_2A)
- `failure_reason`: (if FAILED)
- `route_to`: (if ROUTED_TO_PHASE_0 or ROUTED_TO_PHASE_2A)
- `lessons_learned`: array
- `llm_assessment`: (if ROUTED_TO_PHASE_2A - compatibility assessment details)

After reflection completion, immediately load, read entire file, then execute {nextStepFile}

#### EXECUTION RULES:

- This is an UNATTENDED reflection step with no user choices
- Proceed directly to Step 7 after reflection is complete
- **Failure to load Step 7 = SYSTEM FAILURE**

---

## POST-STEP 7 ROUTING

| Outcome | Gate Type | Status Update | Next Action |
|---------|-----------|---------------|-------------|
| SELF_MODIFY | MUST_WORK | Keep current | New version enters Phase 2C |
| **SUPERSEDED** | MUST_WORK | **SUPERSEDED** | **New hypothesis enters `/phase2a-dialogue`** |
| FAILED | MUST_WORK | FAILED | Continue with remaining hypotheses |
| ROUTED_TO_PHASE_0 | MUST_WORK | FAILED | Execute `/phase0-brainstorm` |
| ROUTED_TO_PHASE_2A | MUST_WORK | FAILED | Execute `/phase2a-dialogue` |
| SELF_MODIFY | **SHOULD_WORK** | Keep current | Retry validation (no routing) |
| **LIMITATION_RECORDED** | **SHOULD_WORK** | LIMITATION_RECORDED | Continue to Phase 5 with limitation |

> SHOULD_WORK outcomes never route to Phase 0/2A. After self-recovery attempts exhaust,
> limitation is recorded and pipeline continues to Phase 5.

---

## ERROR HANDLING

| Error | Action |
|-------|--------|
| ClearThought unavailable | Use manual LLM analysis |
| verification_state write fails | Retry 3x with 5s delay |
| LLM self-assessment fails | Default to SUPERSEDED (conservative) |
| Hypothesis Task ID missing | Log warning, continue without Archon update |
| No dependent hypotheses | Skip compatibility check, allow SELF_MODIFY |

> **Conservative Default:** On LLM self-assessment failure, default to SUPERSEDED.
> This ensures incompatible partial results don't break dependent hypotheses.
