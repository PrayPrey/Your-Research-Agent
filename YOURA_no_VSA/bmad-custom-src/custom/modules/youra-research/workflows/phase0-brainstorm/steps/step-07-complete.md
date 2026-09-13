---
name: 'step-07-complete'
description: 'Generate Phase 1 input package and complete session'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-07-complete.md'
prevStepFile: '{workflow_path}/steps/step-06-validate.md'
---

# Step 7: Complete Session

**Goal:** Generate Phase 1 input package and finalize session

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on generating Phase 1 package and completing session
- 🚫 FORBIDDEN to skip Archon pipeline task updates
- 💬 Approach: Celebratory, clear next steps for Phase 1
- 📋 Ensure Phase 1 input compatibility with output format

---

## 7.1 Generate Phase 1 Input Package

<action>Compile all outputs into Phase 1 compatible format</action>

<format>
## Phase 1 Input Package Ready!

**research_question:** {{refined_question}}

**detailed_question:** {{detailed_questions}} *(or "Not provided")*

**reference_papers:** {{reference_papers}} *(or "Not provided")*

---

You can now run Phase 1: Targeted Research with these inputs!
</format>

---

## 7.2 Confirm Completion

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [p] Proceed to Phase 1 → Skip user confirmation</action>

<ask response="ready_for_phase1">
Everything looks good! Ready to proceed to Phase 1?

Options:
- [p] Proceed to Phase 1 now
- [e] Edit something before proceeding
- [s] Save and proceed later
</ask>

---

## 7.3 Generate Session Summary

<action>Generate final session summary</action>
<action>Calculate session duration from start time to now</action>

SET key_insights = [bullet list of key discoveries from technique sessions]
SET techniques_used = [list of techniques applied during session]
SET areas_for_exploration = [promising directions not yet explored]
SET session_duration = [calculated duration]
SET next_steps = "Proceed to Phase 1 - Targeted Research"

---

## 7.4 Pipeline Task Update (Archon)

<critical>
Update Archon Pipeline to mark Phase 0 complete and Phase 1 ready.
</critical>

<action>**Update Pipeline Task Status**

```bash
# 1. Mark Phase 0 as done
mcp__archon__manage_task(
    action="update",
    task_id="{phase0_task_id}",
    status="done"
)

# 2. Mark Phase 1 as doing (ready to start)
mcp__archon__manage_task(
    action="update",
    task_id="{phase1_task_id}",
    status="doing"
)
```

Display after update:
```
✅ **Pipeline Updated**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Phase 0 - Brainstorm: done ✓
• Phase 1 - Research: doing ← Next
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
</action>

---

## File Write (Mandatory - FINAL)

<file-write>
**Save FINAL progress:**

1. Read {default_output_file}
2. **Replace `{{UNFILLED:pipeline_project_title}}` with the EXACT project title used in Archon**
   - Format: `"Anonymous Pipeline: {initial_interest_summary}"`
   - This is the same title used in Step 0.5 when creating the Pipeline Project
   - Example: `"Anonymous Pipeline: Adaptive Learning Rate Scheduling"`
3. Replace `{{UNFILLED:phase1_research_question}}` with {{refined_question}}
4. Replace `{{UNFILLED:phase1_detailed_question}}` with {{detailed_questions}} (or `*Not provided*`)
5. Replace `{{UNFILLED:phase1_reference_papers}}` with {{reference_papers}} (or `*Not provided*`)
6. Replace `{{UNFILLED:key_insights}}` with bullet list of key discoveries
7. Replace `{{UNFILLED:techniques_used}}` with list of techniques applied
8. Replace `{{UNFILLED:areas_for_exploration}}` with promising directions not yet explored
9. Replace `{{UNFILLED:session_duration}}` with calculated duration
10. Replace `{{UNFILLED:next_steps}}` with "Proceed to Phase 1 - Targeted Research"
11. Write file back
12. Display: "✅ **Session Complete!** All progress saved to {default_output_file}"
</file-write>

---

## 7.5 Final Display

<format>
## Session Complete!

**What we explored:**
{{techniques_used}}

**Key insights discovered:**
{{key_insights}}

**Your refined research direction:**
{{refined_question}}

---

**Pipeline Status:**
- ✅ Phase 0 - Brainstorm: Complete
- → Phase 1 - Research: Ready to start

---

*Session facilitated by YouRA Research Question Architect*
*Ready for Phase 1: Targeted Research*

**To continue:** `/phase1-targeted`
</format>

---

## Phase 1 Output Compatibility

<critical>
**Phase 1 Input Format (from template.md):**

The `<phase1-input>` section in the output file contains:
- `### research_question` - The refined main research question
- `### detailed_question` - Numbered sub-questions (or "Not provided")
- `### reference_papers` - Papers with relevance notes (or "Not provided")

Phase 1's step-01-initialize.md reads this section to populate:
- `research_question`: From "### research_question" section
- `detailed_question`: From "### detailed_question" section
- `reference_papers`: From "### reference_papers" section
</critical>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Phase 1 input package generated with all required fields
- User confirmation received (proceed/edit/save for later)
- Session summary generated with key insights and techniques used
- Archon pipeline updated (Phase 0 done, Phase 1 doing)
- All output file fields filled (no {{UNFILLED:*}} remaining)
- Final display shown with next steps for Phase 1

### ❌ SYSTEM FAILURE:
- Not generating Phase 1 compatible output format
- Skipping Archon pipeline task status updates
- Leaving {{UNFILLED:*}} placeholders in output file
- Not providing clear next steps for Phase 1
- Not saving final progress to output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 7 Complete** - Session finalized
**Phase 0 Complete** - Ready for Phase 1
