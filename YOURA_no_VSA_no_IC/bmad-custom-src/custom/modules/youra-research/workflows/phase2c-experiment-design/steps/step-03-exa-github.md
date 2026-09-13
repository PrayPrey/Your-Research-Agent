---
name: 'step-03-exa-github'
description: 'Search GitHub for real implementations using Exa MCP'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-03-exa-github.md'
nextStepFile: '{workflow_path}/steps/step-04-serena-analysis.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 3: GitHub Code Search - Exa MCP

## STEP GOAL:

Search GitHub for real implementations using Exa MCP to find concrete code examples, training configurations, and architecture patterns. Identify complex code that may require deeper Serena analysis in the next step.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Exa GitHub code searches
- 🚫 FORBIDDEN to skip MCP calls or fabricate search results
- 💬 Approach: Execute 1-2 Exa queries, analyze results thoroughly
- 📋 Flag complex code (>100 lines) for Serena analysis

## EXECUTION PROTOCOLS:

- 🎯 Execute actual Exa MCP calls - never simulate results
- 💾 Document repository information, code snippets, configurations
- 📖 Extract: architecture, training protocol, hyperparameters
- 🚫 Never proceed without analyzing at least 1 GitHub result

## CONTEXT BOUNDARIES:

- Available context: Archon findings from Step 2, hypothesis mechanism
- Focus: Exa GitHub searches only (Serena is next step)
- Limits: Do not perform semantic code analysis in this step
- Dependencies: mechanism_name, problem_domain from previous steps

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Display Step Start

Display: "🔍 Step 3: Searching GitHub for real implementations..."

### 2. Execute Exa Searches (2-3 Queries)

**🎯 CRITICAL: Implementation Priority Hierarchy**

For paper reproduction experiments, ALWAYS search in this priority order:
1. **Paper Author's Official Implementation** (HIGHEST PRIORITY)
2. Popular library implementations (e.g., PyTorch Geometric, DGL)
3. Community reimplementations

**Query 1: Paper Author's Official Implementation (MANDATORY for paper methods)**
```
mcp__exa__get_code_context_exa(
  query="{paper_first_author_name} {mechanism_name} official implementation GitHub",
  tokensNum=5000
)
```
**Purpose:** Find the EXACT implementation used in the original paper
**Priority:** ⭐⭐⭐ HIGHEST - This is the ground truth for reproduction

**Query 2: Library Implementation (MANDATORY)**
```
mcp__exa__get_code_context_exa(
  query="{mechanism_name} PyTorch Geometric OR PyTorch implementation",
  tokensNum=5000
)
```
**Purpose:** Find standard library implementations (useful but may differ from paper)
**Priority:** ⭐⭐ MEDIUM - Use only if author implementation unavailable

**Query 3: Benchmark Code (Optional)**
```
mcp__exa__get_code_context_exa(
  query="{dataset_type} {problem_domain} benchmark code",
  tokensNum=5000
)
```
**Purpose:** Find standard benchmark implementations
**Priority:** ⭐ LOW - Reference only

### 3. Analyze Exa Results

For each result, extract:

**Repository Information:**
- GitHub URL
- Repository name
- Stars / activity level

**Code Content:**
- Relevant files
- Architecture used
- Training protocol

**Key Patterns:**
- Model architecture details
- Training loop structure
- Data pipeline implementation
- Hyperparameter choices
- Evaluation metrics

### 4. Identify Code for Serena Analysis

Check if complex code found:

```
IF code snippet > 100 lines OR unfamiliar architecture pattern OR custom layers:
  Store: {code_for_analysis} = complex code snippet
  Store: {serena_needed} = true
  Display: "🔍 Complex code identified - will analyze with Serena in Step 4"
ELSE:
  Store: {serena_needed} = false
  Display: "ℹ️ Code is clear - Serena analysis not required"
```

### 5. Document GitHub Findings

Compile findings in structured format:

```markdown
### Exa GitHub Implementations

**Query 1: {mechanism_name} Implementation**

**Repository 1**: [org/repo-name] (⭐ count)
- **URL**: https://github.com/[url]
- **Relevance**: [Why this is relevant]
- **Architecture**: [Model architecture used]
- **Key Code**:
  ```python
  # [Relevant snippet]
  ```
- **Training Config**:
  - Optimizer: [name + params]
  - Learning rate: [value + schedule]
  - Batch size: [value]
  - Epochs: [value]
- **Dataset**: [What dataset they used]
- **Results**: [Performance if mentioned]

**Repository 2**: [Continue for other results]

**Query 2: Benchmark Code** (if searched)
- [Findings]

**Serena Analysis Needed**: {serena_needed}
```

Store as: `{exa_github_findings}`

### 6. Update Output File

Fill these placeholders in {outputFile}:
- `exa_github_findings`

Write the file back after filling placeholders.

Display: "✅ GitHub findings saved to output file"

### 7. Present MENU OPTIONS

<action if="Archon doing task description starts with '[UNATTENDED]'">Auto-select [C] → Load {nextStepFile}</action>

Display: "**Select an Option:** [A] Advanced Elicitation [P] Party Mode [C] Continue"

#### Menu Handling Logic:

- IF A: Execute {advancedElicitationTask}
- IF P: Execute {partyModeWorkflow}
- IF C: Save content to {outputFile}, update frontmatter, then load, read entire file, then execute {nextStepFile}
- IF Any other comments or queries: help user respond then [Redisplay Menu Options](#7-present-menu-options)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- After other menu items execution completes, redisplay the menu
- User can chat or ask questions - always respond and redisplay menu

---

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN [C continue option] is selected and [Exa findings documented and Serena need determined], will you then load and read fully `{workflow_path}/steps/step-04-serena-analysis.md` to execute and begin code analysis (if needed).

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- At least 1-2 Exa GitHub queries executed
- Repository information extracted (URL, stars, relevance)
- Code snippets documented with annotations
- Training configurations extracted
- Serena analysis need determined
- Findings saved to output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Fabricating search results without executing MCP calls
- Skipping Exa queries
- Not documenting repository sources
- Not determining Serena analysis need
- Proceeding without user input/selection
- Not updating output file

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
