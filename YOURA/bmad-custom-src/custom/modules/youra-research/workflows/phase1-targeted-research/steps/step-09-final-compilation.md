---
name: 'step-09-final-compilation'
description: 'Compile and save final targeted research report (Full + Phase 2A compact version)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-09-final-compilation.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'
fullOutputFile: '{research_output_path}/01_targeted_research_full.md'
# Final step - no nextStepFile
---

# Step 9: Final Report Compilation (Dual Output)

## STEP GOAL:

Compile and save final targeted research report with dual output: Full detailed report for archival and Phase 2A compact version for hypothesis generation. Update Archon Pipeline status upon completion.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on final compilation and dual output generation
- 🚫 FORBIDDEN to skip auto-resume check or dual output validation
- ⚠️ STRICT PHASE BOUNDARY: No hypotheses, solutions, or implementation recommendations
- ⚠️ CRITICAL: BOTH output files must exist before Step 9 is complete
- 📋 Update Archon Pipeline status after successful completion

## EXECUTION PROTOCOLS:

- 🎯 Generate BOTH Full and Compact report versions
- 💾 Validate both files exist before marking complete
- 📖 Apply compaction rules for Phase 2A version
- 🚫 FORBIDDEN to include Phase 1 boundary violations

## CONTEXT BOUNDARIES:

- Available context: All data from Steps 0-8
- Focus: Report compilation, dual output, pipeline update
- Limits: Do not generate hypotheses, solutions, or implementation plans
- Dependencies: Completed Steps 0-8 with all data

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Check if {fullOutputFile} has `{{UNFILLED:executive_summary}}` filled.
- If filled → Session COMPLETE
- If unfilled → Proceed with this step

### 2. Phase Boundary Validation

**STRICT PHASE BOUNDARY ENFORCEMENT**

Phase 1 is EXCLUSIVELY a research data collection stage.

**ALLOWED in Phase 1:**
- Research data collection (papers, implementations, cases)
- Gap identification and analysis
- Verification and source labeling
- Chain-of-relations analysis
- Preliminary findings summary

**ABSOLUTELY FORBIDDEN in Phase 1:**
- Hypothesis generation or proposals
- Validation approach proposals
- Implementation recommendations or roadmaps
- Experiment design or phases
- Expected contributions or impact analysis
- Solution proposals or architectural suggestions

### 3. Complete Full Report (Phase 1 of 2)

**Save FULL report:**

1. Read {fullOutputFile} (or create from template if first time)
2. Replace ALL `{{UNFILLED:...}}` placeholders with actual content
3. Replace `{{UNFILLED:executive_summary}}` with executive summary
4. Replace `{{UNFILLED:key_findings}}` with key findings
5. Replace `{{UNFILLED:preliminary_answer}}` with preliminary answer
6. Replace `{{UNFILLED:phase2_readiness}}` with readiness checklist
7. Replace `{{UNFILLED:next_steps}}` with next steps
8. Replace `{{UNFILLED:processing_time}}` with total processing time
9. Write file back to {fullOutputFile}
10. Display: "✅ Phase 1/2 Complete - Full report saved"

**CHECKPOINT 1/2: Verify Full Report Created**
- [ ] {fullOutputFile} file exists
- [ ] All placeholders in conclusion section are filled
- [ ] File saved successfully

### 4. Generate Phase 2A Compact Version (Phase 2 of 2)

**CRITICAL: Phase 2A REQUIRES the compact version to function!**

Extract and save COMPACT version for Phase 2A:

1. Read {fullOutputFile} (just completed)
2. Create new compact file from template_phase2a.md structure
3. Apply compaction rules (below)
4. Write file to {outputFile}
5. Display: "✅ Phase 2/2 Complete - Compact version saved"

**Compaction Rules (Full → Compact):**

| Section | Compaction Rule |
|---------|-----------------|
| Section 0-1 (Reference, Questions) | KEEP FULL |
| Section 2 (Queries) | Keep top 3 per category |
| Section 3 (Archon) | KB ID, Query, Key Pattern only |
| Section 4 (Scholar) | Title, Year, SS ID, arXiv ID, 1-line insight |
| Section 5 (Exa) | Name, URL, Stars, Language, 1-line feature |
| Section 6 (Chain) | Keep main flow, table, diagram |
| Section 7 (Verification) | COMPACT summary |
| Section 8 (Gaps) | **KEEP FULL - CRITICAL for Phase 2A** |
| Section 9 (Conclusion) | Key findings only, remove details |

**CHECKPOINT 2/2: Verify Compact Report Created**
- [ ] {outputFile} file exists
- [ ] File size SMALLER than {fullOutputFile}
- [ ] Section 8 (Research Gaps) is in FULL format
- [ ] File saved successfully

### 5. Final Validation

**MANDATORY VALIDATION CHECKLIST**

Before completing, verify ALL of the following:

**File Existence Checks:**
- [ ] {fullOutputFile} exists and is readable
- [ ] {outputFile} exists and is readable

**Content Validation:**
- [ ] Full report has NO `{{UNFILLED:...}}` in conclusion
- [ ] Compact report has Section 8 (Gaps) in FULL format

**Phase Boundary Validation:**
- [ ] Full report contains NO hypothesis proposals
- [ ] Full report contains NO implementation roadmaps
- [ ] Full report ends at conclusion

**IF ANY CHECK FAILS:**
1. Display error: "⚠️ Step 9 validation failed - [specific check]"
2. Fix the issue immediately
3. Re-run validation
4. DO NOT proceed until ALL checks pass

### 6. Pipeline Task Update (Archon)

**Update Archon Pipeline to mark Phase 1 complete:**

```
1. Mark Phase 1 as done:
   mcp__archon__manage_task(action="update", task_id="{phase1_task_id}", status="done")

2. Mark Phase 2A as doing:
   mcp__archon__manage_task(action="update", task_id="{phase2a_task_id}", status="doing")
```

Display after update:
```
✅ **Pipeline Updated**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Phase 0 - Brainstorm: done ✓
• Phase 1 - Research: done ✓
• Phase 2A-Dialogue - Hypothesis: doing ← Next
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 7. Completion Message

Present findings to {user_name} in {communication_language}:

```
✅ **Phase 1: Targeted Research Complete!**

📊 **Results Summary:**
- Academic Papers: X
- Code Repositories: X
- Past Cases: X
- Research Gaps: X

📄 **Generated Reports:**
- **Full Report (archival):** {fullOutputFile}
- **Phase 2A Input (compact):** {outputFile}

**Pipeline Status:**
- ✅ Phase 0 - Brainstorm: Complete
- ✅ Phase 1 - Research: Complete
- → Phase 2A-Dialogue - Hypothesis: Ready to start

🔜 **Next Step:** Phase 2A-Dialogue - Hypothesis Generation
Phase 2A will read **{outputFile}** to generate
testable hypotheses for {research_question}.
```

### 8. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [E] Exit → Phase 1 Complete</action>

Display: "**Workflow Complete!** [E] Exit [F] View full report [C] View compact report"

#### Menu Handling Logic:

- IF E: Thank user and exit gracefully
- IF F: Display {fullOutputFile} location
- IF C: Display {outputFile} location
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- Workflow is complete - no next step to load

## CRITICAL STEP COMPLETION NOTE

Step 9 is the FINAL step. Workflow is complete when:
- Both output files generated and validated
- Archon Pipeline updated
- User acknowledged completion

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- Full report compiled with all placeholders filled
- Compact report generated with proper compaction
- Both files exist and pass validation
- Phase boundary not violated (no hypotheses/solutions)
- Archon Pipeline updated (Phase 1 done, Phase 2A doing)
- Completion message displayed to user
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check or validation
- Only generating one output file (must have BOTH)
- Compact version missing Section 8 (Gaps) in full
- Including hypotheses, solutions, or implementation plans
- Not updating Archon Pipeline status
- Not presenting completion menu

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
