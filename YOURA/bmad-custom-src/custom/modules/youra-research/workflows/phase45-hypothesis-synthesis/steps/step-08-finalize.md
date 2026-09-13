---
name: 'step-08-finalize'
description: 'Update verification_state.yaml, Archon task status, display completion summary'

workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase45-hypothesis-synthesis'

thisStepFile: '{workflow_path}/steps/step-08-finalize.md'
---

# Step 08: Finalize

> **Step Position:** Step 7 (Generate) → **[Step 8: Finalize]**
> **Purpose:** Update pipeline state, save Serena memory, display completion summary
> **MCP:** Archon (task management), Serena (memory persistence)
> **Input:** Generated `045_validated_hypothesis.md`
> **Output:** Updated `verification_state.yaml`, completion summary

---

## Execution Sequence

### 1. Update Verification State

Read and update `verification_state.yaml`:

```yaml
updates:
  workflow:
    current_phase: "Phase 4.5 Complete"
    synthesis_completed: true
    synthesis_file: "045_validated_hypothesis.md"
    synthesis_completed_at: "{ISO8601_timestamp}"
    synthesis_version: "2.0"
```

**Write the updated file.**

---

### 2. Update Archon Task Status

```yaml
tool: mcp__archon__manage_task
action: "update"
purpose: "Mark Phase 4.5 task as review/done"
```

If there is an active Archon task for Phase 4.5, update its status.

---

### 3. Save Serena Memory

Write key findings to Serena memory for cross-pipeline learning:

```yaml
tool: mcp__serena__write_memory
content: |
  # Phase 4.5 Synthesis Results
  Date: {date}
  Research: {research_topic}

  ## Key Outcomes
  - Predictions supported: {N}/{total}
  - Refined core statement: {one_sentence}
  - Main theoretical contribution: {one_sentence}
  - Critical limitation: {one_sentence}

  ## Lessons for Future Pipelines
  - {lesson_1}
  - {lesson_2}
```

---

### 4. Display Completion Summary

```
═══════════════════════════════════════════════════════════════
              PHASE 4.5: HYPOTHESIS SYNTHESIS COMPLETE
═══════════════════════════════════════════════════════════════

  Prediction-Result Alignment:
    P1: {status} ({confidence})
    P2: {status} ({confidence})
    P3: {status} ({confidence})

  Hypothesis Refinement:
    Original: "{original_core_statement_short}"
    Refined: "{refined_core_statement_short}"
    Claims kept/weakened/removed: {N}/{N}/{N}
    Assumptions verified/unverified/violated: {N}/{N}/{N}

  Theoretical Interpretation:
    Mechanism steps verified: {N}/{total}
    Unexpected findings analyzed: {N}
    Literature connections: {N}
    Contributions identified: {N}

  Limitations: {N} principled limitations documented
  Future Work: {N} results-grounded directions

  Output: 045_validated_hypothesis.md

═══════════════════════════════════════════════════════════════

  Next Step: Phase 5 (Baseline Comparison) or Phase 6 (Paper Writing)

═══════════════════════════════════════════════════════════════
```

---

### 5. Workflow Complete

Phase 4.5 execution is finished. Control returns to the caller (full-pipeline or standalone).

---
