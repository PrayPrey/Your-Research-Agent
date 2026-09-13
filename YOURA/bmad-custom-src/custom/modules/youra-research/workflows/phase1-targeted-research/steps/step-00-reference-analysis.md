---
name: 'step-00-reference-analysis'
description: 'Analyze provided reference papers to extract key concepts for query generation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase1-targeted-research'

# File References
thisStepFile: '{workflow_path}/steps/step-00-reference-analysis.md'
nextStepFile: '{workflow_path}/steps/step-01-initialize.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{research_output_path}/01_targeted_research.md'

# Template References
outputTemplate: '{workflow_path}/template.md'
---

# Step 0: Reference Paper Analysis (Optional)

## STEP GOAL:

Analyze provided reference papers to extract key concepts, mechanisms, and technical terms that will inform query generation in Step 2. This step is optional and only executes if reference papers were provided in Phase 0 Brainstorm.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on extracting concepts from reference papers
- 🚫 FORBIDDEN to skip auto-resume check at the beginning
- 🔄 AUTO-RESUME CHECK: Execute before anything else - check if output file has unfilled placeholders
- 📋 If no reference papers provided, skip this step and proceed to Step 1

## EXECUTION PROTOCOLS:

- 🎯 Check for existing output file and resume point before starting
- 💾 Save extracted concepts to output file after completion
- 📖 Read complete paper content for local files, use MCP for arXiv/DOI
- 🚫 FORBIDDEN to proceed without completing auto-resume check

## CONTEXT BOUNDARIES:

- Available context: Reference papers from Phase 0 Brainstorm session (if provided)
- Focus: Concept extraction, mechanism identification, technical term collection
- Limits: Do not generate hypotheses or solutions - only extract existing concepts
- Dependencies: Phase 0 Brainstorm session file with reference_papers field

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Auto-Resume Check

Before starting this step, check if output file already exists:

1. Check if {outputFile} exists
2. If YES → Read file and check for `{{UNFILLED:reference_paper_analysis}}`
3. If filled → Skip to Step 1 (load {nextStepFile})
4. If NO file exists → Create from template and proceed

**DO NOT ask user about resuming. Just check and act automatically.**

### 2. Check if Reference Papers Provided

Check if reference_papers were provided in Phase 0 Brainstorm session.

**IF reference_papers provided:**
Proceed to Section 3 (Reference Paper Analysis Protocol).

**IF NO reference_papers provided:**
Skip this step - No reference papers to analyze.

Display to user:
"ℹ️ No reference papers provided. Proceeding to Step 1 initialization.
(Reference papers are optional for targeted research.)"

Then immediately load {nextStepFile}.

### 3. Reference Paper Analysis Protocol

Load and analyze provided reference papers:

**A. Local File Reading:**
- If user provides local file path (e.g., "CTM.md", "TRM.md")
- Read COMPLETE file content (no offset/limit)
- Extract key concepts, mechanisms, architectures

**B. arXiv/DOI Paper Loading:**
- If user provides arXiv URL or DOI
- Use Semantic Scholar MCP to fetch paper metadata and abstract
- Identify core contributions and methodologies

**C. Concept Extraction:**
- Key mechanisms (e.g., "local attention", "latent vector recursion")
- Architectural components (e.g., "memory module", "cross attention")
- Technical terms and abbreviations
- Novel approaches introduced

**D. Context Building:**
- How do these papers relate to {research_question}?
- What specific techniques are relevant to {detailed_question}?
- What concepts need further investigation?

Store extracted concepts for use in query generation (Step 2).

### 4. Document Reference Paper Analysis

For each reference paper analyzed, document:

```markdown
## Reference Paper Analysis

### Paper 1: [paper_title]
- Source: [local_path or arXiv_url]
- Key Mechanism: [primary mechanism or approach]
- Relevant Concepts: [list of extracted concepts]
- Connection to Research Question: [how this paper relates to the research question]

### Extracted Technical Terms
- [term_1]: [definition_1]
- [term_2]: [definition_2]

### Research Context
[Summary of how reference papers inform the research question]
```

### 5. Save Progress

**Save progress after Step 0:**

1. Read {outputFile} (or create from template if not exists)
2. Replace `{{UNFILLED:reference_paper_analysis}}` with:
   - Reference paper analysis (if papers provided)
   - `*No reference papers provided*` (if no papers)
3. Write file back
4. Display: "✅ Step 0 saved - Reference paper analysis recorded"

### 6. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [C] Continue to Step 1 [Q] Ask questions about this step"

#### Menu Handling Logic:

- IF C: Save content to {outputFile}, then load, read entire file, then execute {nextStepFile}
- IF Q: Answer questions, then redisplay menu
- IF Any other comments or queries: help user respond then redisplay menu

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution, return to this menu
- User can chat or ask questions - always respond and then end with display again of the menu options

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [reference paper analysis complete or skipped], will you then load and read fully `{nextStepFile}` to execute and begin research pipeline initialization.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Auto-resume check completed before any other action
- Reference papers analyzed (if provided) with concepts extracted
- Output file updated with reference_paper_analysis placeholder filled
- Menu presented and user input handled correctly
- Graceful skip if no reference papers provided

### ❌ SYSTEM FAILURE:

- Skipping auto-resume check at the beginning
- Not extracting concepts from provided reference papers
- Proceeding without saving progress to output file
- Not presenting menu for user confirmation
- Generating hypotheses or solutions (Phase 1 boundary violation)

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
