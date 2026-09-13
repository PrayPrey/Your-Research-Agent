---
name: 'step-05-references'
description: 'Identify reference papers for Phase 1 research'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-05-references.md'
nextStepFile: '{workflow_path}/steps/step-06-validate.md'
prevStepFile: '{workflow_path}/steps/step-04-synthesize.md'
---

# Step 5: Identify Reference Papers

**Goal:** Collect optional reference papers as starting points for Phase 1

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on collecting and documenting reference papers
- 🚫 FORBIDDEN to require references - they are optional
- 💬 Approach: Helpful, accommodating if user has none
- 📋 Document relevance notes for provided references

---

## 5.1 Ask for References

<ask response="want_references">
Do you have any papers or references you'd like to include as starting points for Phase 1?

This could be:
- Papers that inspired your question
- Key works in the field
- Specific techniques you want to build on

(Enter paper titles, arXiv IDs, or file paths - or type 'skip' if none)
</ask>

---

## 5.2 Process References

<check if="want_references != skip">
<action>Document the provided references</action>

<ask response="reference_relevance">
For each reference, briefly note why it's relevant:

{{reference_1}}: Why relevant?
{{reference_2}}: Why relevant? (if applicable)
</ask>

<action>Format references with relevance notes:

```
- [Paper 1 Title/ID]: [Relevance note]
- [Paper 2 Title/ID]: [Relevance note]
```
</action>
</check>

<check if="want_references == skip">
SET reference_papers = "*No reference papers provided - will discover in Phase 1*"
</check>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 5:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:reference_papers}}` with:
   - Papers and their relevance notes (formatted as bullets), OR
   - `*No reference papers provided - will discover in Phase 1*` if skipped
3. Write file back
4. Display: "✅ Step 5 saved"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Next Action:**
[C] Continue to Step 6 (Validation)
[A] Add more references
[Q] Ask questions about this step

IF C: Load and execute {nextStepFile}
IF A: Return to 5.1 for additional references
IF Q: Answer questions, then redisplay menu
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- User asked about reference papers
- References collected with relevance notes if provided
- "Skip" option respected if user has no references
- reference_papers variable properly set (papers or "Not provided")
- Progress saved to output file

### ❌ SYSTEM FAILURE:
- Requiring references when they are optional
- Not documenting relevance notes for provided papers
- Not properly handling "skip" response
- Not saving progress to output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 5 Complete** - Reference papers collected
**Next:** Step 6 - Phase 1 Ready Check
