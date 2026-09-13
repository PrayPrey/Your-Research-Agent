---
name: 'step-02-approach'
description: 'Present exploration approach options and plan session'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-02-approach.md'
nextStepFile: '{workflow_path}/steps/step-03-techniques.md'
prevStepFile: '{workflow_path}/steps/step-01-session-setup.md'
research_techniques: '{workflow_path}/research-methods.csv'
---

# Step 2: Present Exploration Approach

**Goal:** Select exploration approach based on user's starting point

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules and Role Reinforcement.

### Step-Specific Rules:
- 🎯 Focus only on presenting approach options and configuring session
- 🚫 FORBIDDEN to skip approach selection or impose a choice
- 💬 Approach: Clear options, respect user's choice and pace
- 📋 Tailor technique recommendations based on starting point assessment

---

## 2.1 Load Research Techniques

<action>Load techniques from {research_techniques} CSV file</action>

---

## 2.2 Present Approach Options

Based on their starting point from Step 1, present approach options:

<ask response="approach_selection">
I have a few ways we can explore your research question. Which feels right?

1. **Guided Discovery** - I'll lead you through techniques that match where you are
   _(Best if you're not sure where to start)_

2. **Choose Your Adventure** - Browse our research techniques and pick what interests you
   _(Best if you like to see options)_

3. **Fast Track to Phase 1** - Quick refinement to get a research question ready
   _(Best if you already have a clear direction)_

4. **Deep Dive Exploration** - Comprehensive journey through multiple techniques
   _(Best if you have 15-20 minutes and want thorough exploration)_

Which approach? (1-4)
</ask>

---

## 2.3 Configure Session Based on Selection

<check if="approach_selection==1">
<!-- Guided Discovery -->
<action>Based on starting point assessment, select 2-3 appropriate techniques</action>

**Technique Selection Logic:**
- Vague Interest → Problem Space Mapping → Gap Hunter → Question Sharpening
- General Topic → Curiosity Cascade → Cross-Domain Bridge → Scope Calibration
- Specific Direction → Assumption Excavation → Devil's Advocate → So What Test
- Near-Ready → Feasibility Check → Phase 1 Ready Check

<format>
Based on where you are, I recommend we try:

1. **{{technique_1}}** ({{duration_1}} min) - {{why_this_fits}}
2. **{{technique_2}}** ({{duration_2}} min) - {{why_this_fits}}

Sound good? We can always adjust as we go!
</format>
</check>

<check if="approach_selection==2">
<!-- Choose Your Adventure -->
<action>Display technique categories with descriptions</action>

<format>
Here are our research exploration techniques:

**Discovery** - Find your research direction
- Problem Space Mapping - Map the landscape of related problems
- Gap Hunter - Find what's missing in current knowledge
- Curiosity Cascade - Follow your natural curiosity

**Refinement** - Sharpen your question
- Question Sharpening - Transform vague to precise
- Scope Calibration - Find the right size
- Assumption Excavation - Uncover hidden assumptions

**Connection** - Link to existing work
- Cross-Domain Bridge - Connect to other fields
- Paper Trail Exploration - Find key references
- Method Matching - Match question to methodology

**Validation** - Stress-test your question
- Devil's Advocate - Challenge from skeptical view
- So What Test - Verify significance
- Feasibility Check - Ensure practical viability

**Synthesis** - Bring it together
- Question Family Tree - Generate related questions
- Research Story Arc - Frame as compelling narrative
- Phase 1 Ready Check - Final preparation

Which technique(s) interest you?
</format>
</check>

<check if="approach_selection==3">
<!-- Fast Track -->
<action>Jump directly to refinement and validation</action>

<format>
Let's quickly refine what you have!

First, let me understand your current thinking:
- What's the core question you want to answer?
- What specific aspect matters most?

We'll do a quick Question Sharpening → So What Test → Phase 1 Ready Check
</format>

SET session_plan = "Fast Track: Question Sharpening → So What Test → Phase 1 Ready Check"
</check>

<check if="approach_selection==4">
<!-- Deep Dive -->
<action>Design a comprehensive journey through multiple techniques</action>

**Journey Structure:**
1. **Opening** (5 min): Problem Space Mapping or Curiosity Cascade
2. **Exploration** (5-8 min): Gap Hunter + Cross-Domain Bridge
3. **Refinement** (5 min): Question Sharpening + Scope Calibration
4. **Validation** (3-5 min): Devil's Advocate + So What Test
5. **Synthesis** (3 min): Phase 1 Ready Check

<format>
Great choice! We'll take a thorough journey:

1. **Discover** - Map your problem space and follow curiosity
2. **Explore** - Hunt for gaps and cross-domain connections
3. **Refine** - Sharpen and calibrate your question
4. **Validate** - Stress-test from multiple angles
5. **Synthesize** - Prepare for Phase 1

Ready to begin? This will take about 15-20 minutes.
</format>

SET session_plan = "Deep Dive: Discovery → Exploration → Refinement → Validation → Synthesis"
</check>

---

## File Write (Mandatory)

<file-write>
**Save progress after Step 2:**

1. Read {default_output_file}
2. Replace `{{UNFILLED:approach_selection}}` with selected approach name (e.g., "Deep Dive Exploration")
3. Replace `{{UNFILLED:session_plan}}` with the planned technique sequence
4. Write file back
5. Display: "✅ Step 2 saved"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Next Action:**
[C] Continue to Step 3 (Execute Techniques)
[Q] Ask questions about this step

IF C: Load and execute {nextStepFile}
IF Q: Answer questions, then redisplay menu
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Research techniques loaded from CSV
- Approach options presented clearly (Guided/Choose/Fast Track/Deep Dive)
- User's approach selection captured (approach_selection)
- Session plan configured based on selection
- Progress saved to output file

### ❌ SYSTEM FAILURE:
- Not loading research techniques from CSV
- Imposing an approach without user choice
- Proceeding without approach_selection captured
- Not configuring session plan based on selection
- Not saving progress to output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.

---

**Step 2 Complete** - Exploration approach selected
**Next:** Step 3 - Execute Techniques
