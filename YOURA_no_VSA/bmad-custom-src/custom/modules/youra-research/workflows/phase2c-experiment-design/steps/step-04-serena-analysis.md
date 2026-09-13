---
name: 'step-04-serena-analysis'
description: 'Perform semantic code analysis using Serena MCP (conditional step)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-04-serena-analysis.md'
nextStepFile: '{workflow_path}/steps/step-05-dataset-baseline.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 4: Code Analysis - Serena MCP (Conditional)

## STEP GOAL:

Perform semantic code analysis on complex code snippets using Serena MCP. This step is CONDITIONAL - only execute Serena analysis if {serena_needed} = true from Step 3. Extract code structure, core mechanism implementation, and integration patterns to generate accurate pseudo-code.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Serena code analysis (if needed)
- 🚫 FORBIDDEN to perform analysis if Serena unavailable
- 💬 Approach: Systematic code structure → mechanism extraction → pattern finding
- 📋 Skip gracefully if {serena_needed} = false

## EXECUTION PROTOCOLS:

- 🎯 Check {serena_needed} flag first
- 💾 Document all Serena analysis results
- 📖 Synthesize findings into pseudo-code
- 🚫 If Serena unavailable, document limitation and proceed

## CONTEXT BOUNDARIES:

- Available context: Code snippets from Step 3, {serena_needed} flag
- Focus: Serena semantic analysis only
- Limits: Skip if not needed, document limitation if Serena unavailable
- Dependencies: {code_for_analysis} from Step 3

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Check If Serena Analysis Needed

**IF {serena_needed} = false:**

Display: "ℹ️ Step 4 skipped - No complex code requiring Serena analysis."

Store: `{serena_code_analysis}` = "*Skipped* - Code from search results was sufficiently clear"

Fill placeholder in {outputFile}: `serena_code_analysis`

Write file, then SKIP to [Menu Options](#7-present-menu-options)

**IF {serena_needed} = true:**

Display: "🔍 Step 4: Analyzing complex code with Serena MCP..."

Continue with analysis below.

### 2. Verify Serena MCP Available

**IF Serena MCP unavailable:**

Display: "⚠️ Serena MCP unavailable - proceeding with limited analysis"

Store: `{serena_code_analysis}` = "*Limited* - Serena unavailable, relying on Archon/Exa snippets only"

Fill placeholder and SKIP to [Menu Options](#7-present-menu-options)

### 3. Code Structure Overview

Execute Serena symbols overview:

```
mcp__serena__get_symbols_overview(
  relative_path="{code_path}"
)
```

**Extract from overview:**
- Classes defined (names and purposes)
- Functions defined
- Module organization
- Entry points (forward methods, main functions)

Document:
```markdown
### Code Structure (Serena Analysis)

**Classes**:
- `ClassName1`: [purpose]
- `ClassName2`: [purpose]

**Key Functions**:
- `function1`: [purpose]

**Organization**: [How code is structured]
```

### 4. Extract Core Mechanism

Identify key class/function names from overview, then:

```
mcp__serena__find_symbol(
  name_path_pattern="[KeyClassName]",
  include_body=true,
  relative_path="{code_path}"
)
```

**Analyze mechanism:**

1. **Input/Output**: Dimensions and types
2. **Key Operations**: Step-by-step process
3. **Hyperparameters**: Configurable parameters
4. **Integration**: Where it fits in model

### 5. Find Integration Patterns

```
mcp__serena__search_for_pattern(
  substring_pattern="forward.*attention",
  output_mode="content",
  relative_path="{code_path}"
)
```

**Extract:**
- Where mechanism is inserted
- Layer before/after
- Input preparation method

### 6. Synthesize into Pseudo-code

Combine all Serena findings:

```python
# Core Mechanism: {mechanism_name}
# Based on analysis of: {source_repo}

class MechanismName(nn.Module):
    """
    [Purpose from analysis]
    """
    def __init__(self, channels, [params from analysis]):
        super().__init__()
        # [Key components from analysis]
        self.component1 = [from code]
        self.component2 = [from code]

    def forward(self, x, [inputs from analysis]):
        """
        Input: x (B, C, H, W) - [from analysis]
        Output: (B, C, H, W) - [from analysis]
        """
        # Step 1: [from analysis]
        step1_result = [operation]

        # Step 2: [from analysis]
        step2_result = [operation]

        # Step 3: [from analysis]
        output = [final operation]

        return output

# Integration point:
# Insert after: [layer name]
# Input preparation: [how inputs are prepared]
```

Store as: `{analyzed_pseudocode}`

Document full analysis as: `{serena_code_analysis}`

### 7. Update Output File

Fill placeholder in {outputFile}:
- `serena_code_analysis`

Write the file back.

Display: "✅ Serena analysis completed and saved"

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

ONLY WHEN [C continue option] is selected and [Serena analysis completed OR skipped with documentation], will you then load and read fully `{workflow_path}/steps/step-05-dataset-baseline.md` to execute and begin dataset selection.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Correctly checked {serena_needed} flag
- If needed: Executed Serena analysis tools
- Code structure documented
- Core mechanism extracted
- Integration patterns identified
- Pseudo-code synthesized (if analysis performed)
- Findings saved to output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Performing Serena analysis when {serena_needed} = false
- Skipping Serena when needed without documenting limitation
- Fabricating analysis results
- Proceeding without user input/selection
- Not updating output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
