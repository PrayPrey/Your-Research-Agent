---
name: 'step-01-session-setup'
description: 'Session Setup - Understand research interest and context'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-01-session-setup.md'
nextStepFile: '{workflow_path}/steps/step-02-approach.md'
prevStepFile: '{workflow_path}/steps/step-00-init.md'
---

# Step 1: Session Setup

**Goal:** Understand the user's research interest and existing context

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on understanding the user's research interest and context
- 🚫 FORBIDDEN to skip greeting or context gathering
- 💬 Approach: Warm, encouraging, curiosity-driven
- 📋 Wait for user response before proceeding - their answer shapes the session

---

## 1.1 Greeting

<action>Greet {user_name} warmly and set the stage for collaborative exploration</action>

<ask response="initial_interest">
Hello {user_name}! I'm excited to help you discover and refine your research question today.

Let's start with what's on your mind:

**What research area or topic are you interested in exploring?**

(This can be as vague as "something about AI" or as specific as "transformer attention mechanisms for compositional generalization" - wherever you are is perfect!)
</ask>

<critical>Wait for user response. Their answer shapes the entire session.</critical>

---

## 1.2 Assess Starting Point

<action>Based on their response, assess the starting point:

**Starting Point Assessment:**
- **Vague Interest** (e.g., "AI", "deep learning") → Start with Discovery techniques
- **General Topic** (e.g., "attention mechanisms", "memory networks") → Mix Discovery + Refinement
- **Specific Direction** (e.g., "local attention for sequence models") → Focus on Refinement + Validation
- **Near-Ready Question** (e.g., "How can CTM's local attention improve TRM?") → Jump to Validation + Synthesis

Adapt your facilitation approach accordingly.
</action>

---

## 1.3 Gather Context

<ask response="existing_context">
Great! Before we dive in, a quick check:

1. **Do you have any papers or references** you're already thinking about? (optional)
2. **Is there a specific problem** you're trying to solve, or are you exploring openly?
3. **What's your timeline** - are you starting fresh or building on existing work?

(Feel free to answer any or all - this helps me tailor our session!)
</ask>

---

## 1.4 Failure Context Integration

<check if="previous_failure_contexts exists (from Step 0.3)">

<action>**Incorporate Failure Learnings:**

Display to user:
```
ℹ️ **Note:** I found previous research attempt(s) that didn't work out.
I'll help guide us away from similar pitfalls.

**Previous Issues:** [Summarize from all failure records]
**Key Learnings:** [What NOT to do, from lessons learned]
**What Showed Promise:** [Partial successes worth preserving]
```

Use this context to:
- Steer away from approaches that failed before
- Suggest alternative directions
- Highlight what worked partially (if applicable)
- Consider the complete failure history when guiding the user
</action>

</check>

---

## 1.5 Archon Pipeline Creation

<action>**Create Pipeline Project (if not yet created in Step 0):**

After receiving initial_interest, create Archon Pipeline:

```bash
mcp__archon__manage_project(
    action="create",
    title="Anonymous Pipeline: {initial_interest_summary}",
    description="Research pipeline from brainstorm to implementation"
)

# Create 11 Phase Tasks...
```

(See Step 0.5 for full details)
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 1:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:initial_interest}}` with collected initial_interest
3. Replace `{{UNFILLED:existing_context}}` with collected existing_context (or `*Not provided*` if skipped)
4. Write file back
5. Display: "✅ Step 1 saved"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Next Action:**
[C] Continue to Step 2 (Exploration Approach)
[Q] Ask questions about this step

IF C: Load and execute {nextStepFile}
IF Q: Answer questions, then redisplay menu
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- User greeted warmly and session stage set
- Initial research interest captured (initial_interest)
- Existing context gathered (existing_context)
- Starting point assessed (vague/general/specific/near-ready)
- Failure context integrated if previous attempt exists
- Archon pipeline created with project and tasks
- Progress saved to output file

### ❌ SYSTEM FAILURE:
- Skipping greeting or rushing to questions
- Not waiting for user response to shape session
- Proceeding without capturing initial_interest
- Not saving progress to output file
- Skipping Archon pipeline creation

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 1 Complete** - Research interest captured
**Next:** Step 2 - Present Exploration Approach
