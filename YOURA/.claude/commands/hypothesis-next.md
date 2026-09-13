---
description: 'Execute next READY hypothesis through Phase 2C → 3 → 4 → 5. Lightweight single-hypothesis execution with gate validation.'
---

# Hypothesis Next - Execute Next Hypothesis

You serve as the **single hypothesis executor** for the Anonymous Research Pipeline.
Execute the next READY hypothesis through Phase 2C → 3 → 4 → 5.

---

## Execution Steps

### Step 1: Load State File and Select Next Hypothesis

1. **Load verification_state.yaml:**
   - Check `research_output_path` in `bmad-custom-src/custom/modules/youra-research/config.yaml`
   - Read `{research_output_path}/youra_research/verification_state.yaml`

2. **Check Workflow Status:**
   ```python
   IF workflow.status == "STOPPED":
       display: "🛑 Workflow has been stopped."
       display: f"   Reason: {workflow.stop_reason}"
       ask: "Do you want to continue? [Y/N]"
       IF N: EXIT

   IF workflow.status == "COMPLETED":
       display: "🎉 All hypothesis verification completed!"
       EXIT
   ```

3. **Select Next Hypothesis:**
   ```python
   # Check IN_PROGRESS first
   in_progress = find_hypothesis(status="IN_PROGRESS")
   IF in_progress:
       next_hypothesis = in_progress
       display: f"🔄 Found in-progress hypothesis: {next_hypothesis.id}"
   ELSE:
       # First READY hypothesis (by dependency order)
       ready = find_hypotheses(status="READY", sort_by="dependency")
       IF ready:
           next_hypothesis = ready[0]
       ELSE:
           display: "ℹ️ No hypotheses available for execution."
           display: "   Use /hypothesis-status to check current status."
           EXIT
   ```

### Step 2: Display Hypothesis Information and Confirm

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    Next Hypothesis: {hypothesis_id}                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  ID: {hypothesis_id}                                                  ║
║  Type: {type} ({type_description})                                    ║
║  Gate: {gate_icon} {gate_type}                                        ║
║                                                                       ║
║  Statement:                                                           ║
║    {hypothesis_statement (truncated to 2 lines)}                      ║
║                                                                       ║
║  Prerequisites:                                                       ║
║    {prereq_id_1}: {status_icon} {result}                              ║
║    {prereq_id_2}: {status_icon} {result}                              ║
║                                                                       ║
║  Current Phase: {current_phase_or_starting}                           ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Do you want to proceed? [Y/N/S(status)]
```

**User Input Handling:**
- `Y`: Continue execution
- `N`: EXIT
- `S`: Execute `/hypothesis-status` then ask again

### Step 3: Gate Validation

```python
def validate_gates(hypothesis):
    for prereq_id in hypothesis.prerequisites:
        prereq = state.hypotheses[prereq_id]

        # Incomplete prerequisite
        IF prereq.status != "COMPLETED":
            display: f"❌ {prereq_id} has not been completed yet."
            EXIT

        # MUST_PASS failure
        IF prereq.gate.type == "MUST_PASS" AND NOT prereq.gate.satisfied:
            display_must_pass_failure(prereq_id)
            EXIT

        # SHOULD_PASS failure
        IF prereq.gate.type == "SHOULD_PASS" AND NOT prereq.gate.satisfied:
            display_should_pass_warning(prereq_id)
            load_limitation_context(prereq_id)
```

**SHOULD_PASS Failure Warning:**
```
╔═══════════════════════════════════════════════════════════════════════╗
║  ⚠️ Previous Hypothesis Limitation Detected                          ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  {prereq_id}: SHOULD_PASS failed                                      ║
║                                                                       ║
║  Limitations (loaded from Phase 2C Handoff):                          ║
║    • {warning_1}                                                      ║
║    • {warning_2}                                                      ║
║                                                                       ║
║  Recommendations:                                                     ║
║    • {recommendation_1}                                               ║
║    • {recommendation_2}                                               ║
║                                                                       ║
║  → Proceeding with the above limitations applied.                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Step 4: Phase Execution

```python
# Update status
hypothesis.status = "IN_PROGRESS"
save_state()

# Phase 2C: Experiment Design
IF hypothesis.experiment_design.status != "COMPLETED":
    display: f"▶️ Phase 2C: Experiment Design starting..."
    execute("/phase2c-experiment-design", hypothesis_id=hypothesis.id)

    IF failed:
        handle_failure("2C")
        EXIT

# Phase 3: Implementation Planning
IF hypothesis.implementation_planning.status != "COMPLETED":
    display: f"▶️ Phase 3: Implementation Planning starting..."
    execute("/phase3-implementation-planning", hypothesis_id=hypothesis.id)

    IF failed:
        handle_failure("3")
        EXIT

# Phase 4: Coding & Validation
IF hypothesis.validation.status != "COMPLETED":
    display: f"▶️ Phase 4: Coding & Validation starting..."
    execute("/phase4-coding", hypothesis_id=hypothesis.id)

    # Phase 4 Gate Processing (MUST_WORK)
    result = read_validation_result()
    IF result == "FAIL":
        # Save failure context to Serena Memory
        mcp__serena__write_memory("failure_{hypothesis.id}.md", ...)
        display: "🛑 Phase 4 FAIL - Routing to Phase 0"
        route_to_phase0()
        EXIT
    ELIF result == "PARTIAL" AND max_attempts_reached:
        # Save pivot context to Serena Memory
        mcp__serena__write_memory("pivot_{hypothesis.id}_{new_id}.md", ...)
        display: "⚠️ Phase 4 PARTIAL (max attempts) - Routing to Phase 2A-Dialogue"
        route_to_phase2a()
        EXIT

# Phase 5: Baseline Comparison
IF hypothesis.baseline_comparison.status != "COMPLETED":
    display: f"▶️ Phase 5: Baseline Comparison starting..."
    execute("/phase5-baseline-repo-comparison", hypothesis_id=hypothesis.id)

    # Phase 5 Gate Processing (DETERMINES_SUCCESS)
    result = read_baseline_result()
    IF result == "PARTIAL":
        # Save failure context to Serena Memory
        mcp__serena__write_memory("phase5_failure_{hypothesis.id}.md", ...)
        display: "⚠️ Phase 5 PARTIAL - Routing to Phase 0"
        route_to_phase0()
        EXIT
```

### Step 5: Result Processing

```python
def process_result(hypothesis, result):

    IF result == "PASS":
        hypothesis.status = "COMPLETED"
        hypothesis.gate.satisfied = True
        display_success(hypothesis.id)

    ELIF result == "PARTIAL":
        hypothesis.status = "COMPLETED"
        hypothesis.gate.satisfied = False

        IF hypothesis.gate.type == "MUST_PASS":
            workflow.status = "STOPPED"
            display_must_pass_partial_failure(hypothesis.id)
        ELSE:
            display_should_pass_partial(hypothesis.id)

    ELIF result == "FAIL":
        IF hypothesis.gate.type == "MUST_PASS":
            hypothesis.status = "FAILED"
            hypothesis.gate.satisfied = False
            workflow.status = "STOPPED"
            display_must_pass_failure(hypothesis.id)
        ELSE:
            hypothesis.status = "COMPLETED"
            hypothesis.gate.satisfied = False
            display_should_pass_failure(hypothesis.id)

    # Save state
    save_state()

    # Update next hypothesis READY status
    update_dependent_status(hypothesis.id)
```

### Step 6: Completion Display

**On Success:**
```
╔═══════════════════════════════════════════════════════════════════════╗
║  ✅ {hypothesis_id} verification complete!                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Result: {result}                                                     ║
║  Gate: {gate_icon} {gate_type} - {satisfied_icon}                     ║
║  Duration: {duration}                                                 ║
║                                                                       ║
║  Generated Files:                                                     ║
║    • 02c_experiment_brief_{h_id}.md                                   ║
║    • 03_*.md (PRD, Architecture, Logic, Config)                       ║
║    • 04_validation.md                                                 ║
║    • baseline_comparison/05_baseline_comparison.md                    ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Next Hypothesis: {next_ready_hypothesis_or_none}                     ║
║                                                                       ║
║  Options:                                                             ║
║    [N] Execute next hypothesis (/hypothesis-next)                     ║
║    [L] Execute full loop (/hypothesis-loop)                           ║
║    [S] Check status (/hypothesis-status)                              ║
║    [Q] Quit                                                           ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

**On SHOULD_PASS Failure:**
```
╔═══════════════════════════════════════════════════════════════════════╗
║  ⚠️ {hypothesis_id} completed (with limitations)                     ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Result: {result} (SHOULD_PASS not satisfied)                         ║
║  Gate: 🟡 SHOULD_PASS - ❌                                            ║
║                                                                       ║
║  Recorded Limitations:                                                ║
║    {limitation_summary}                                               ║
║                                                                       ║
║  → These limitations will be applied to subsequent hypotheses.        ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

**On MUST_PASS Failure:**
```
╔═══════════════════════════════════════════════════════════════════════╗
║  🛑 {hypothesis_id} failed - Workflow stopped                        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Result: FAIL                                                         ║
║  Gate: 🔴 MUST_PASS - ❌                                              ║
║                                                                       ║
║  Affected Hypotheses:                                                 ║
║    {dependent_h_1}: BLOCKED                                           ║
║    {dependent_h_2}: BLOCKED                                           ║
║                                                                       ║
║  Recommended Actions:                                                 ║
║    1. Analyze failure cause in 04_validation.md                       ║
║    2. Redesign hypothesis with /phase2a-dialogue, or                  ║
║    3. Modify experiment conditions and re-execute                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Icon Reference

| Item | Icon |
|------|------|
| MUST_PASS | 🔴 |
| SHOULD_PASS | 🟡 |
| DETERMINES_SUCCESS | 🟢 |
| PASS | ✅ |
| PARTIAL | ⚠️ |
| FAIL | ❌ |
| IN_PROGRESS | 🔄 |
| READY | ⏸️ |
| BLOCKED | 🚫 |

---

## Error Handling

| Situation | Action |
|-----------|--------|
| verification_state.yaml not found | Guide to `/phase2b-planning` then EXIT |
| No READY hypothesis | Guide to `/hypothesis-status` then EXIT |
| Prerequisite not completed | Guide to complete that hypothesis first |
| MUST_PASS failure | STOP workflow, EXIT |
| Phase execution failure | Handle based on gate type |

---

## Usage Examples

```bash
# Execute next hypothesis
/hypothesis-next

# Specify a particular hypothesis (optional)
/hypothesis-next H-M3
```

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/hypothesis-status` | Full status dashboard |
| `/hypothesis-loop` | Execute multiple hypotheses sequentially |
| `/hypothesis-next` | Execute next single hypothesis (current) |
