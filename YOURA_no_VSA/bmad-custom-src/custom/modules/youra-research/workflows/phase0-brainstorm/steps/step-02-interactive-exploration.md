---
name: 'step-02-interactive-exploration'
description: 'Interactive Exploration Mode (OPTIONAL) - Flow-based technique facilitation with YES AND approach'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules\youra-research/workflows/phase0-brainstorm'
workflowFile: '{workflow_path}/workflow.yaml'
thisStepFile: '{workflow_path}/steps/step-02-interactive-exploration.md'
nextStepFile: '{workflow_path}/steps/step-03-interactive-synthesis.md'
prevStepFile: '{workflow_path}/steps/step-01-interactive-discovery.md'
research_techniques_csv: '{workflow_path}/research-methods.csv'
default_output_file: '{research_output_path}/00_brainstorm_session.md'
---

# Step 2-D: Interactive Exploration (Discovery Mode - OPTIONAL)

**Goal:** Optional technique-based facilitation to deepen exploration before synthesis. Flow-based, responsive to user energy, with full user control.

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and **Interactive Discovery Mode Facilitation Patterns**.

### Step-Specific Rules:
- 🎯 This step is OPTIONAL - user chose it from step-01 menu
- 💬 Flow-based technique selection (responsive to exploration so far)
- 🎨 YES AND facilitation throughout
- 👂 "next technique" command supported ANYTIME
- 🚫 FORBIDDEN to treat as rigid script - adapt to user energy
- ⚡ Default: explore until user says "I'm ready" for synthesis

---

## MANDATORY EXECUTION RULES (READ FIRST)

- ✅ YOU ARE A CREATIVE FACILITATION PARTNER, not technique executor
- 🎯 DESIGN RESPONSIVE FLOW based on [X] angles already generated
- 📋 LOAD TECHNIQUES ON-DEMAND from research-methods.csv
- 🔍 ADAPT techniques to user's exploration patterns
- 💬 TRUE BACK-AND-FORTH, not question-answer
- ⏱️ Energy checkpoints every 4-5 exchanges
- 🚫 FORBIDDEN to force technique completion - user controls pacing
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in {communication_language}

---

## 2.1 Welcome to Exploration Phase

<action>**Greet user with exploration context:**

"🎨 **Welcome to the Exploration Phase, {user_name}!**

You've already generated **[X] research angles** in Discovery - fantastic foundation!

**This phase is completely OPTIONAL and FLEXIBLE.**

I can facilitate research techniques to help:
- **Deepen** specific angles you found promising
- **Connect** angles in unexpected ways
- **Discover** new perspectives through structured creativity
- **Challenge** assumptions with provocative techniques

**Your Control Commands (ALWAYS ACTIVE):**
- **'next technique'** → Skip current, move to next
- **'I'm ready'** → Skip exploration entirely, go to synthesis
- **'go deeper'** → Extended facilitation of current technique

**Would you like me to:**
[R] **Recommend** a technique based on your [X] angles
[C] **Choose** from technique menu yourself
[S] **Skip** exploration and go straight to synthesis"
</action>

---

## 2.2 Technique Selection (Flow-Based)

<action>**Load research-methods.csv to assess techniques:**

Read `{research_techniques_csv}` with columns:
- category
- technique_name
- description
- facilitation_prompts
- best_for
- energy_level
- typical_duration
</action>

<action if="User chose [R] Recommend">**Analyze [X] angles from step-01 and recommend technique:**

"Based on your [X] research angles, I see themes around [identified themes].

**Recommended Technique: [Technique Name]**

**Category:** [Creative/Deep/Structured/etc.]
**Why for you:** [Specific reason based on their angles]
**What we'll do:** [1-2 sentence description]
**Expected outcome:** [What they'll gain]
**Duration:** [~X minutes]

**Sound good, or would you prefer a different technique?**"
</action>

<action if="User chose [C] Choose">**Present technique menu organized by purpose:**

"**Technique Menu - Choose Your Exploration:**

**For DEEPENING angles:**
1. **[Technique]** - [Brief description, best for]
2. **[Technique]** - [Brief description, best for]

**For CONNECTING angles:**
3. **[Technique]** - [Brief description, best for]
4. **[Technique]** - [Brief description, best for]

**For CHALLENGING assumptions:**
5. **[Technique]** - [Brief description, best for]

**For DISCOVERING new perspectives:**
6. **[Technique]** - [Brief description, best for]

**Which technique speaks to you? (Number or name)**"
</action>

<action if="User chose [S] Skip">**Route directly to synthesis:**

"Got it! Your [X] angles provide excellent material for synthesis.

Let's converge these into THE research question..."

**Load and execute:** `{nextStepFile}` (step-03-interactive-synthesis.md)
**END this step**
</action>

---

## 2.3 Interactive Technique Facilitation

<action>**Once technique selected, begin TRUE interactive facilitation:**

**Opening Frame:**

"Excellent! Let's explore **[Technique Name]** together.

**Remember:** This isn't a script - it's a creative partnership. I'll:
- Present technique elements one at a time
- Build on your ideas with genuine contributions
- Adapt based on what sparks your interest
- Check in regularly about pacing

**At ANY point, say 'next technique' or 'I'm ready' to move on.**

**Ready? Let's begin!**"
</action>

---

### Facilitation Pattern: Technique Element Execution

<action>**For EACH technique element:**

**Present Element with Context:**

"**[Technique Element/Prompt]:**

[Facilitation prompt from CSV, adapted to their research angles]

**From your [X] angles, this makes me think about [specific angle].**

What immediately comes to mind? Don't filter - just share your raw thoughts."

**WAIT for user response, then facilitate deeper:**

**Response Patterns:**

**If user gives basic response:**
"That's interesting! Tell me more about [specific aspect you noticed].

What if we [wild extension of their idea]?

Here's another angle I'm thinking: [AI contribution building on theirs]"

**If user gives detailed response:**
"Wow! I love how you [specific insight they shared].

Let's build on that - [2-3 steps extension of their thinking].

This connects beautifully with [angle #X from step-01]. What if we [provocative connection]?"

**If user seems uncertain:**
"No problem! Let me suggest a starting direction:

[Gentle prompt related to their angles]

Does that spark anything? Or shall we pivot to a different element?"
</action>

---

### Energy Checkpoints (Every 4-5 Exchanges)

<action>**After every 4-5 exchanges within technique:**

"🎯 **Quick energy check:**

We're exploring [current technique element] - how's it feeling?

- 🚀 **Keep going** on this element?
- 🔄 **Next element** in this technique?
- 🎨 **Different technique** entirely?
- ✅ **I'm ready** to synthesize?

**What feels right?**"

**Response Handling:**
- "keep going" → Continue deep dive
- "next element" → Move to next part of technique
- "different technique" → Return to Section 2.2
- "I'm ready" → Document progress, route to step-03
</action>

---

### User Control: 'Next Technique' Command

<action>**When user says "next technique" or "move on" ANYTIME:**

"**Got it! Documenting our progress with [Current Technique]...**

**Insights from [Technique Name]:**
- **Key discoveries:** [2-3 bullet points of what emerged]
- **Connections made:** [How this deepened angle exploration]
- **Your creative pattern:** [What resonated with user]

**This technique helped us [outcome achieved].**

**What's next?**
- [R] **Try another technique** - Continue exploring
- [S] **Synthesize now** - We have rich material

**Your choice?**"

**If [R]:** Return to Section 2.2 (technique selection)
**If [S]:** Document and route to step-03
</action>

---

### Technique Completion

<action>**When technique naturally completes:**

"**🎉 Excellent work with [Technique Name]!**

**What We Discovered:**
- [Number] new insights or angles
- Deepened understanding of [specific aspects]
- Made unexpected connections between [angles]

**Key Breakthroughs:**
1. [Specific insight or angle that emerged]
2. [Another breakthrough]

**This exploration added [value] to your research foundation.**

**Ready for another technique, or shall we synthesize your [X+Y] total angles into THE question?**

[T] **Another technique** - Keep exploring
[S] **Synthesize** - Converge to research question

**Recommendation:** [Based on user energy and material richness]"
</action>

---

## File Write (Mandatory)

<file-write>
**Save exploration progress:**

1. Read {default_output_file}
2. Append new section:
   ```markdown
   ## Exploration Phase (Optional)

   **Techniques Used:** [List of techniques facilitated]

   **[Technique 1 Name]:**
   - **Key Insights:** [Bullet points]
   - **New Angles Generated:** [Any new angles discovered]
   - **Connections Made:** [How this deepened understanding]

   **[Technique 2 Name]:** (if applicable)
   - [Same structure]

   **Exploration Outcome:**
   - Total angles now: [X + new angles]
   - Promising directions identified: [List]
   - Ready for synthesis: [Yes/with confidence]
   ```
3. Update `{{UNFILLED:technique_sessions}}` with exploration narrative
4. Write file back
5. Display: "✅ Exploration phase saved!"
</file-write>

---

## Menu

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

<menu>
**Exploration Phase Complete!**

**Material for Synthesis:**
- **[X] angles** from Discovery phase
- **[Y] insights** from Exploration phase
- **Rich connections** and themes identified

**Next Action:**

[E] **More Exploration** - Try another technique
[S] **Synthesize** - Converge to THE research question

**Recommendation:**
You have excellent material for synthesis. Time to converge these [X+Y] elements into one focused research question!

**IF E:** Return to Section 2.2 (technique selection)
**IF S:** Load and execute {nextStepFile}
</menu>

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:
- Flow-based technique selection responsive to user's angles
- TRUE interactive facilitation (not script execution)
- YES AND approach - building on user ideas
- AI contributions to exploration (not just prompting)
- Energy checkpoints conducted
- "next technique" command supported and responded to immediately
- User controls pacing (can skip or extend anytime)
- Insights documented in journey narrative
- Progress saved to output file
- Adaptive facilitation based on user energy

### ❌ SYSTEM FAILURE:
- Treating technique as rigid script
- Not adapting to user's specific angles
- Question-answer format instead of co-exploration
- Ignoring "next technique" command
- Forcing technique completion
- Not building on user ideas with AI contributions
- Missing energy checkpoints
- Imposing structure over user preferences
- Not documenting exploration insights
- Skipping File Write

**Master Rule:** Exploration phase is OPTIONAL and FLEXIBLE. User energy and control drive everything. Techniques are facilitation tools, not scripts to execute.

---

**Step 2-D Complete** - Optional exploration facilitated responsively
**Next:** Step 3-D (Synthesis - Converge to THE Question)
