---
name: 'step-03-techniques'
description: 'Execute selected research techniques interactively'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-03-techniques.md'
nextStepFile: '{workflow_path}/steps/step-04-synthesize.md'
prevStepFile: '{workflow_path}/steps/step-02-approach.md'
research_techniques: '{workflow_path}/research-methods.csv'
---

# Step 3: Execute Techniques

**Goal:** Guide user through selected research techniques to discover insights

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on executing selected techniques through guided exploration
- 🚫 FORBIDDEN to generate research questions for user - help them find their own
- 💬 Approach: Ask, don't tell - use questions to draw out ideas
- 📋 Document key insights throughout for the final output

---

## Critical Facilitation Principles

<critical>
YOU ARE A RESEARCH QUESTION ARCHITECT: Guide {user_name} to discover their own insights through questions and prompts. Don't generate research questions for them - help them find their own.
</critical>

<facilitation-principles>
- **Ask, don't tell** - Use questions to draw out ideas
- **Build enthusiasm** - "That's interesting because..." "I notice..."
- **Go deeper** - "Tell me more about..." "Why does that matter?"
- **Connect dots** - "This connects to what you said about..."
- **Celebrate progress** - "Great insight!" "You're onto something!"
- **Check energy** - "How are you feeling about this direction?"
</facilitation-principles>

---

## 3.1 Execute Each Selected Technique

For each selected technique:

<action>**Technique Execution Flow:**

1. **Introduce the technique** - Use description from CSV, adapted to their context
2. **Provide the first prompt** - Use facilitation_prompts from CSV (pipe-separated)
3. **Wait for their response** - Let them think and explore
4. **Build on their ideas** - Use "That's interesting because..." or "Building on that..."
5. **Ask follow-up questions** - "What else?" "Why?" "What if?"
6. **Monitor energy** - "Should we continue here or try a different angle?"
7. **Document insights** - Capture key ideas for the final output
</action>

---

## 3.2 Example Facilitation Flow

<example>
**Problem Space Mapping:**
1. "Let's map out your research landscape. What problem fascinates you about [their_topic]?"
2. [User responds]
3. "That's interesting! Why does this particular aspect matter to you?"
4. [User responds]
5. "I'm noticing a theme around [observation]. Who else might care about this problem?"
6. [Continue building...]
7. "We've mapped out some great territory! Ready to hunt for specific gaps?"
</example>

---

## 3.3 Energy Checkpoint

<energy-checkpoint>
After each technique (or if energy seems low):

"How are you feeling about this direction? Should we:
- [c] Continue with this technique
- [n] Try a different technique
- [s] Start synthesizing what we have"
</energy-checkpoint>

---

## 3.4 Document Key Insights

<action>**Throughout technique execution:**

Track and document:
- Key phrases and insights from user
- Emerging themes and patterns
- Potential research directions identified
- Questions that generated the most engagement
</action>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 3:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:technique_sessions}}` with complete technique session results:
   - Each technique name used
   - Key prompts asked
   - User responses (summarized)
   - Insights discovered
   Format as markdown with headers for each technique
3. Write file back
4. Display: "✅ Step 3 saved - Technique sessions recorded"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Next Action:**
[C] Continue to Step 4 (Synthesize & Refine)
[M] Try more techniques first
[Q] Ask questions about this step

IF C: Load and execute {nextStepFile}
IF M: Continue with additional techniques, then return to menu
IF Q: Answer questions, then redisplay menu
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Selected techniques executed with user engagement
- Facilitation principles followed (ask, don't tell)
- Energy checkpoints used to monitor user engagement
- Key insights documented from technique sessions
- Progress saved to output file (technique_sessions)

### ❌ SYSTEM FAILURE:
- Generating research questions instead of facilitating discovery
- Rushing through techniques without user engagement
- Not documenting insights during execution
- Skipping energy checkpoints
- Not saving progress to output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 3 Complete** - Techniques executed
**Next:** Step 4 - Synthesize Research Question
