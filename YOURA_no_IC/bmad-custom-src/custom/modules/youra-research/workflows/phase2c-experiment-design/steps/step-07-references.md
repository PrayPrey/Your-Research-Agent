---
name: 'step-07-references'
description: 'Document all reference implementations and sources for traceability'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-07-references.md'
nextStepFile: '{workflow_path}/steps/step-08-validation.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 7: Reference Implementation Documentation

## STEP GOAL:

Document all reference implementations and sources for complete traceability. Compile all Archon, Exa, and Serena sources used throughout the workflow to ensure 100% transparency and reproducibility of the experiment design.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on reference documentation
- 🚫 FORBIDDEN to omit any source used in specifications
- 💬 Approach: Systematic compilation of all sources
- 📋 Every specification must trace to a documented source

## EXECUTION PROTOCOLS:

- 🎯 Compile all sources from Steps 2-6
- 💾 Document each source with how it was used
- 📖 Include code snippets with annotations
- 🚫 Never leave specifications without source reference

## CONTEXT BOUNDARIES:

- Available context: All findings from Steps 2-6
- Focus: Reference documentation only
- Limits: Do not add new research in this step
- Dependencies: All previous step outputs

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Display Step Start

Display: "📚 Step 7: Documenting reference implementations..."

### 2. Compile Archon Knowledge Base Sources

From Step 2 findings:

```markdown
## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: [Title from Step 2]
- **Type**: Knowledge base article / Past case
- **Query Used**: [The query that found this]
- **Relevance**: [What we learned]
- **Key Insights**:
  - [Insight 1]
  - [Insight 2]
- **Used For**: [Which spec - e.g., dataset selection, hyperparameters]

**Source 2**: [Continue for all Archon KB sources]
...

### Archon Code Examples

**Code Source 1**: [Title/Source from Step 2]
- **Query Used**: [The query that found this]
- **Key Code**:
  ```python
  # [Code snippet with annotations]
  ```
- **Used For**: [Which spec - e.g., pseudo-code generation]

**Code Source 2**: [Continue for all code examples]
```

### 3. Compile Exa GitHub Sources

From Step 3 findings:

```markdown
### B. GitHub Implementations (Exa)

**Repository 1**: [org/repo-name] (⭐ count)
- **URL**: [GitHub URL]
- **Query Used**: [The query that found this]
- **Relevance**: [Why this matters]
- **Key Code** (annotated):
  ```python
  # [Relevant code snippet with annotations]
  # Used as basis for: [our pseudo-code section]
  ```
- **Configuration Extracted**: [What configs we used]
- **Their Results**: [Performance they reported]
- **Used For**: [Which spec in our design]

**Repository 2**: [Continue for all GitHub sources]
```

### 4. Compile Serena Analysis Sources (If Performed)

From Step 4 findings (if applicable):

```markdown
### C. Code Analysis (Serena)

**IF Serena analysis was performed:**

**Analyzed Code**: [Source from Step 3]
- **Analysis Method**: Serena MCP semantic analysis
- **Tools Used**:
  - get_symbols_overview: [What we learned]
  - find_symbol: [What we extracted]
  - search_for_pattern: [What patterns we found]
- **Key Findings**:
  - Structure: [Code organization]
  - Mechanism: [How it works]
  - Integration: [How to integrate]
- **Used For**: Pseudo-code generation in Step 6
- **Original Code**:
  ```python
  # [Original code snippet that was analyzed]
  ```
- **Our Derived Pseudo-code**:
  ```python
  # [Our simplified pseudo-code based on analysis]
  ```

**IF Serena was skipped:**

**Serena Analysis**: Not performed - code from search results was sufficiently clear
```

### 5. Document Previous Hypothesis Context (If Continuation)

```markdown
### D. Previous Hypothesis Context

**IF continuation experiment:**

**Source**: Phase 4 Validation Report - {previous_hypothesis_id}
- **File**: `04_validation_{previous_hypothesis_id}.md`
- **Reused Components**:
  - Dataset: [Name] - Proven stable
  - Hyperparameters: [List] - Optimal values
  - Code structure: [Description]
- **Why Reused**: Enables controlled experiment (only mechanism changes)

**IF first hypothesis:**

**Previous Context**: None - this is the first hypothesis in the verification chain.
```

### 6. Create Traceability Matrix

```markdown
### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Archon KB | Source A.1 |
| Preprocessing | GitHub | Repo B.1 |
| Baseline model | Archon KB | Source A.2 |
| Mechanism design | Serena | Analysis C.1 |
| Pseudo-code | GitHub + Serena | B.1, C.1 |
| Training protocol | Previous + Archon | D.1, A.3 |
| Evaluation metrics | Phase 2B | [Reference] |
```

Store as: `{reference_implementations}`

### 7. Update Output File

Fill this placeholder in {outputFile}:
- `reference_implementations`

Write the file back after filling placeholders.

Display: "✅ All references documented for complete traceability"

### 8. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Save content to {outputFile}, update frontmatter, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#8-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution completes, redisplay the menu
- User can chat or ask questions - always respond and redisplay menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [all sources documented with traceability matrix], will you then load and read fully `{workflow_path}/steps/step-08-validation.md` to execute and begin final validation.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- All Archon sources documented
- All Exa GitHub sources documented
- Serena analysis documented (or skipped status noted)
- Previous context documented (if continuation)
- Traceability matrix created
- Every specification traces to a source
- References saved to output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Omitting sources used in specifications
- Missing URLs or references
- No traceability matrix
- Specifications without documented sources
- Proceeding without user input/selection
- Not updating output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
