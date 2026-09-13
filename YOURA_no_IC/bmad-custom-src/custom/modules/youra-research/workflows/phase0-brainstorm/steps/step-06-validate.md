---
name: 'step-06-validate'
description: 'Validate research question with So What Test and Feasibility Check'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-06-validate.md'
nextStepFile: '{workflow_path}/steps/step-07-complete.md'
prevStepFile: '{workflow_path}/steps/step-05-references.md'
---

# Step 6: Phase 1 Ready Check

**Goal:** Validate research question with So What Test and Feasibility Check

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on validating the research question's significance and feasibility
- 🚫 FORBIDDEN to skip So What Test or Feasibility Check
- 💬 Approach: Supportive validation, address concerns constructively
- 📋 Final check against previous failures if context exists

---

## 6.1 Display Current State

<action>Run final validation using So What Test and Feasibility Check</action>

<format>
Let's do a final check before sending to Phase 1:

**Your Research Question:**
{{refined_question}}

**Detailed Questions (if any):**
{{detailed_questions}}

**Reference Papers (if any):**
{{reference_papers}}
</format>

---

## 6.2 So What Test

<ask response="so_what_validation">
**So What Test:**
- Why should anyone care about this research?
- What's the potential impact if you find an answer?
- How does this advance the field?

Quick answer:
</ask>

---

## 6.3 Feasibility Check

<ask response="feasibility_validation">
**Feasibility Check:**
- Is this question answerable with available methods/data?
- What's a realistic scope for investigation?
- Any obvious blockers?

Quick assessment:
</ask>

---

## 6.4 Final Validation

<action>Based on responses, confirm readiness or suggest adjustments</action>

<check if="responses indicate concerns">
<format>
I noticed some concerns:
- [concern 1]
- [concern 2]

Would you like to:
- [a] Adjust the research question
- [c] Continue anyway (record limitations)
</format>
</check>

<check if="responses indicate readiness">
<format>
✅ **Validation Passed!**

Your research question is:
- **Significant:** {so_what summary}
- **Feasible:** {feasibility summary}

Ready to proceed to Phase 1!
</format>
</check>

---

## 6.5 Failure Context Final Check

<check if="previous_failure_context exists">

<action>**Final validation against previous failures:**

"**Final Check Against Previous Failures:**

✅ This new direction successfully avoids the previous pitfalls:
- Previous issue: {what_not_to_do}
- How we addressed it: [explanation]"

OR

"⚠️ **Remaining Risk:** [concern about similarity to previous failure]
Recommendation: [mitigation strategy]"
</action>

</check>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 6:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:so_what_validation}}` with user's significance response
3. Replace `{{UNFILLED:feasibility_validation}}` with user's feasibility assessment
4. Write file back
5. Display: "✅ Step 6 saved - Validation complete"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Next Action:**
[C] Continue to Step 7 (Complete & Generate Phase 1 Package)
[E] Edit research question first
[Q] Ask questions about this step

IF C: Load and execute {nextStepFile}
IF E: Return to Step 4
IF Q: Answer questions, then redisplay menu
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Current state displayed (refined_question, detailed_questions, reference_papers)
- So What Test completed (so_what_validation captured)
- Feasibility Check completed (feasibility_validation captured)
- Final validation completed with clear pass/concern indication
- Failure context final check performed if previous attempt exists
- Progress saved to output file

### ❌ SYSTEM FAILURE:
- Skipping So What Test or Feasibility Check
- Not capturing user's validation responses
- Proceeding despite unresolved concerns without acknowledgment
- Not performing failure context final check when available
- Not saving progress to output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 6 Complete** - Validation passed
**Next:** Step 7 - Complete Session & Generate Phase 1 Package
