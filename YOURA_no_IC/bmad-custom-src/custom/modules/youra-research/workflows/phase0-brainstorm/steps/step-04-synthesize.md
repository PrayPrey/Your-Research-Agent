---
name: 'step-04-synthesize'
description: 'Synthesize research question and generate detailed sub-questions'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-04-synthesize.md'
nextStepFile: '{workflow_path}/steps/step-05-references.md'
prevStepFile: '{workflow_path}/steps/step-03-techniques.md'
---

# Step 4: Synthesize Research Question

**Goal:** Crystallize research question and optionally generate detailed sub-questions

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on synthesizing and refining the research question
- 🚫 FORBIDDEN to write questions for user - guide them to articulate their own
- 💬 Approach: Help sharpen and refine, don't impose direction
- 📋 Validate against previous failures if context exists

---

## 4.1 Transition Check

<transition-check>
"We've explored a lot of great territory! Are you ready to synthesize your research question, or would you like to explore more?"

- [y] Yes, let's synthesize
- [m] More exploration first → Return to Step 3
</transition-check>

---

## 4.2 Articulate Initial Question

<action>Guide the user to articulate their refined research question</action>

<ask response="main_research_question">
Based on everything we've explored, let's crystallize your research question.

**Complete this sentence:**
"I want to investigate/understand/discover..."

(Don't worry about perfect wording yet - we'll refine it!)
</ask>

---

## 4.3 Question Sharpening

<action>Help refine the question using the Question Sharpening technique</action>

<ask response="refined_question">
Good! Let me help sharpen that:

Your current question: "{{main_research_question}}"

Let's make it more specific:
1. **What exactly** do you want to know? (specific phenomenon)
2. **In what context?** (domain, constraints)
3. **How would you know** if you found an answer? (measurable outcome)

Try rewording with these in mind:
</ask>

---

## 4.4 Failure Context Validation

<check if="previous_failure_context exists">

<action>**Validate against previous failures:**

"Let me check this against what didn't work before...

✅ **Validation:** This new direction addresses the previous gap by [explanation]"

OR

"⚠️ **Concern:** This seems similar to the previous approach. Consider:
- [alternative suggestion 1]
- [alternative suggestion 2]"
</action>

</check>

---

## 4.5 Generate Detailed Sub-Questions (Optional)

<ask response="want_detailed_questions">
Would you like to break down your main question into more specific sub-questions?

This helps guide the research in Phase 1 and creates a clearer path to Phase 2 hypotheses.

(y/n or skip to continue)
</ask>

<check if="want_detailed_questions == y">
<action>Guide generation of 2-3 detailed sub-questions</action>

<ask response="detailed_question_1">
Your main question: "{{refined_question}}"

What's the **first specific aspect** you'd want to investigate?

Think about:
- A technical component to understand
- A relationship to explore
- A mechanism to uncover
</ask>

<ask response="detailed_question_2">
Good! What's **another angle** you'd want to explore?

Consider:
- An alternative approach
- A different perspective
- A potential challenge to address
</ask>

<ask response="detailed_question_3">
Any **third aspect** to explore? (optional - skip if not needed)
</ask>

<action>Combine into a coherent detailed_questions string as bulleted list</action>
</check>

<check if="want_detailed_questions == n or skip">
SET detailed_questions = "*Skipped by user*"
</check>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 4:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:main_research_question}}` with the initial question from user
3. Replace `{{UNFILLED:refined_question}}` with the sharpened version
4. Replace `{{UNFILLED:detailed_questions}}` with:
   - The collected sub-questions as a bulleted list, OR
   - `*Skipped by user*` if skipped
5. Write file back
6. Display: "✅ Step 4 saved - Research question captured"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Next Action:**
[C] Continue to Step 5 (Reference Papers)
[E] Edit the research question
[Q] Ask questions about this step

IF C: Load and execute {nextStepFile}
IF E: Return to 4.2 or 4.3 for editing
IF Q: Answer questions, then redisplay menu
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Transition check completed (ready to synthesize or return to exploration)
- Main research question articulated by user (main_research_question)
- Question sharpened with specificity (refined_question)
- Failure context validation performed if previous attempt exists
- Detailed sub-questions generated if user requested (detailed_questions)
- Progress saved to output file

### ❌ SYSTEM FAILURE:
- Writing research question for user instead of facilitating
- Skipping question sharpening process
- Not validating against previous failures when context exists
- Proceeding without capturing refined_question
- Not saving progress to output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 4 Complete** - Research question synthesized
**Next:** Step 5 - Identify Reference Papers
