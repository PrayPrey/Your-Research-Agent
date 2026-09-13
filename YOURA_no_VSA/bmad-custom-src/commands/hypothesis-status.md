---
description: 'Display hypothesis verification progress dashboard. Shows status of all hypotheses from verification_state.yaml with visual progress indicators.'
---

# Hypothesis Status Dashboard

You serve as the **status monitor** for the Anonymous Research Pipeline.
Display the current hypothesis verification progress to the user as a visual dashboard.

## Execution Steps

### Step 1: Find State File

Find `verification_state.yaml` in the following order:

1. **Read YouRA config:**
   - Check `research_output_path` in `bmad-custom-src/custom/modules/youra-research/config.yaml`

2. **Construct state file path:**
   - `{research_output_path}/youra_research/verification_state.yaml`

3. **If file not found:**
   ```
   ╔═══════════════════════════════════════════════════════════════════════╗
   ║  ⚠️ verification_state.yaml not found                                 ║
   ╠═══════════════════════════════════════════════════════════════════════╣
   ║                                                                       ║
   ║  Possible causes:                                                     ║
   ║    - Phase 2B has not been executed yet                               ║
   ║    - research_output_path is incorrectly configured                   ║
   ║                                                                       ║
   ║  Solution:                                                            ║
   ║    Run /phase2b-planning to generate verification_state.yaml          ║
   ║                                                                       ║
   ╚═══════════════════════════════════════════════════════════════════════╝
   ```

### Step 2: Read and Parse State File

Read `verification_state.yaml` and extract the following information:

```yaml
# Fields to extract
metadata:
  project_name: {project_name}
  main_hypothesis_id: {main_hypothesis_id}

workflow:
  status: {ACTIVE|STOPPED|COMPLETED|FAILED}
  current_phase: {current_phase}
  stop_reason: {stop_reason, if any}

hypotheses:
  {each_hypothesis_id}:
    type: {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
    status: {READY|NOT_STARTED|IN_PROGRESS|COMPLETED|BLOCKED|FAILED}
    gate:
      type: {MUST_PASS|SHOULD_PASS|DETERMINES_SUCCESS}
      satisfied: {true|false|null}
    experiment_design:
      status: {NOT_STARTED|IN_PROGRESS|COMPLETED}
    implementation_planning:
      status: {NOT_STARTED|IN_PROGRESS|COMPLETED}
    validation:
      status: {NOT_STARTED|IN_PROGRESS|COMPLETED|FAILED}
      result: {PASS|FAIL|PARTIAL|null}
    baseline_comparison:
      status: {NOT_STARTED|IN_PROGRESS|COMPLETED|FAILED}
      result: {PASS|PARTIAL|null}
    prerequisites: [list of dependency hypothesis IDs]
    blocked_by: {blocking hypothesis ID, if any}

statistics:
  total_hypotheses: {int}
  completed_hypotheses: {int}
  failed_hypotheses: {int}
  blocked_hypotheses: {int}
```

### Step 3: Display Dashboard

**MUST** output in the following format:

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    YouRA Hypothesis Progress                          ║
║                    ─────────────────────────                          ║
║  Project: {project_name}                                              ║
║  Main Hypothesis: {main_hypothesis_id}                                ║
║  Workflow Status: {workflow_status_icon} {workflow_status}            ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Overall Progress: [{progress_bar}] {completed}/{total} ({percent}%)  ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ID      │ Type       │ Gate          │ Phase    │ Status │ Result   ║
║──────────┼────────────┼───────────────┼──────────┼────────┼──────────║
{FOR each hypothesis in dependency order:}
║  {id}    │ {type}     │ {gate_icon} {gate_type_short} │ {phase}  │ {status_icon} │ {result} ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Legend:                                                              ║
║    ✅ PASS    ⚠️ PARTIAL/FAIL (continued)    🔄 IN_PROGRESS           ║
║    ⏸️ READY   🚫 BLOCKED                      ❌ FAILED                ║
║                                                                       ║
║  Gates: 🔴 MUST_PASS  🟡 SHOULD_PASS  🟢 DETERMINES_SUCCESS           ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║  Next Action: {next_action_recommendation}                            ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Step 4: Status Icon Mapping Rules

**Workflow Status Icon:**
```
ACTIVE    → 🟢
STOPPED   → 🔴
COMPLETED → ✅
FAILED    → ❌
```

**Hypothesis Status Icon:**
```
COMPLETED + gate.satisfied=true   → ✅
COMPLETED + gate.satisfied=false  → ⚠️
IN_PROGRESS                       → 🔄
READY                             → ⏸️
NOT_STARTED                       → ⏸️
BLOCKED                           → 🚫
FAILED                            → ❌
```

**Gate Type Icon:**
```
MUST_PASS         → 🔴
SHOULD_PASS       → 🟡
DETERMINES_SUCCESS → 🟢
```

**Gate Type Short:**
```
MUST_PASS         → "MUST"
SHOULD_PASS       → "SHOULD"
DETERMINES_SUCCESS → "FINAL"
```

**Phase Detection:**
```
experiment_design.status == "IN_PROGRESS"        → "2C"
implementation_planning.status == "IN_PROGRESS"  → "3"
validation.status == "IN_PROGRESS"               → "4"
baseline_comparison.status == "IN_PROGRESS"      → "5"
baseline_comparison.status == "COMPLETED"        → "Done"
validation.status == "COMPLETED" AND baseline_comparison.status != "COMPLETED" → "4→5"
status == "BLOCKED"                              → "🚫"
Otherwise                                        → "—"
```

**Progress Bar Generation:**
```
completed_count = count of hypotheses where status == "COMPLETED"
total_count = total hypotheses count
percentage = (completed_count / total_count) * 100
bar_length = 20
filled = round(percentage / 5)
bar = "█" × filled + "░" × (bar_length - filled)
```

### Step 5: Next Action Recommendation Logic

```python
def get_next_action(workflow, hypotheses):
    if workflow.status == "STOPPED":
        return f"⚠️ Workflow STOPPED: {workflow.stop_reason}. Review and resolve."

    if workflow.status == "ROUTED":
        target = workflow.routing.target
        return f"🔄 Routing to {target}: /{target.lower().replace(' ', '')}"

    # Find IN_PROGRESS hypothesis
    in_progress = [h for h in hypotheses if h.status == "IN_PROGRESS"]
    if in_progress:
        h = in_progress[0]
        phase = detect_current_phase(h)
        if phase == "4→5":
            return f"Continue {h.id}: /phase5-baseline-repo-comparison"
        return f"Continue {h.id}: /phase{phase}"

    # Find READY hypothesis (by dependency order)
    ready = [h for h in hypotheses if h.status == "READY"]
    if ready:
        h = ready[0]  # First in dependency order
        return f"Start {h.id}: /phase2c-experiment-design"

    # Check if all completed
    completed = [h for h in hypotheses if h.status == "COMPLETED"]
    if len(completed) == len(hypotheses):
        return "🎉 All hypotheses verified! Pipeline completed."

    # Check blocked
    blocked = [h for h in hypotheses if h.status == "BLOCKED"]
    if blocked:
        return f"🚫 {len(blocked)} hypothesis(es) blocked. Resolve blocking issues first."

    return "Check hypothesis dependencies and status."
```

### Step 6: Additional Information Display (Optional)

Display the following additional information if the user requests:

**[D] Dependency Graph:**
```
H-E1 (MUST_PASS)
  │
  ├──► H-M1 (SHOULD_PASS)
  │      │
  │      └──► H-CP1 (DETERMINES_SUCCESS)
  │
  └──► H-M2 (SHOULD_PASS)
         │
         └──► H-CP1 (DETERMINES_SUCCESS)
```

**[G] Gate Violations (if any):**
```
Gate Violations:
───────────────
• H-M1: SHOULD_PASS failed at 2025-12-04T15:00:00
  Reason: Accuracy below threshold (0.82 < 0.85)
  Action: Continued with limitation note
```

## Error Handling

| Situation | Output |
|-----------|--------|
| config.yaml not found | "❌ YouRA config not found at bmad-custom-src/custom/modules/youra-research/config.yaml" |
| verification_state.yaml not found | "❌ No verification state. Run /phase2b-planning first." |
| YAML parsing error | "❌ Invalid YAML format in verification_state.yaml. Check file syntax." |
| hypotheses section missing | "❌ No hypotheses defined in verification_state.yaml. Run /phase2b-planning." |
| research_output_path missing | "❌ research_output_path not configured. Check YouRA config.yaml." |

## Menu Options

After displaying the dashboard, provide the following options:

```
Options:
  [R] Refresh status
  [D] Show dependency graph
  [G] Show gate violations
  [N] Start next hypothesis
  [Q] Quit
```

---

## Output Example

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    YouRA Hypothesis Progress                          ║
║                    ─────────────────────────                          ║
║  Project: Adaptive Attention Mechanism                                ║
║  Main Hypothesis: H-M3                                                ║
║  Workflow Status: 🟢 ACTIVE                                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Overall Progress: [████████████░░░░░░░░] 3/5 (60%)                   ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ID      │ Type       │ Gate          │ Phase    │ Status │ Result   ║
║──────────┼────────────┼───────────────┼──────────┼────────┼──────────║
║  H-E1    │ EXISTENCE  │ 🔴 MUST       │ Done     │ ✅     │ PASS     ║
║  H-M1    │ MECHANISM  │ 🟡 SHOULD     │ Done     │ ⚠️     │ PARTIAL  ║
║  H-M2    │ MECHANISM  │ 🟡 SHOULD     │ Done     │ ✅     │ PASS     ║
║  H-C1    │ CONDITION  │ 🟡 SHOULD     │ 3        │ 🔄     │ —        ║
║  H-CP1   │ COMPARISON │ 🟢 FINAL      │ —        │ ⏸️     │ —        ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Legend:                                                              ║
║    ✅ PASS    ⚠️ PARTIAL/FAIL (continued)    🔄 IN_PROGRESS           ║
║    ⏸️ READY   🚫 BLOCKED                      ❌ FAILED                ║
║                                                                       ║
║  Gates: 🔴 MUST_PASS  🟡 SHOULD_PASS  🟢 DETERMINES_SUCCESS           ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║  Next Action: Continue H-C1: /phase3-implementation-planning          ║
╚═══════════════════════════════════════════════════════════════════════╝

Options: [R] Refresh  [D] Dependencies  [G] Gates  [N] Next  [Q] Quit
```
