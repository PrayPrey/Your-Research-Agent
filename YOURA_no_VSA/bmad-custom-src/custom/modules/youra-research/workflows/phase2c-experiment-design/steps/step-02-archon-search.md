---
name: 'step-02-archon-search'
description: 'Search Archon Knowledge Base for past implementation cases and code examples'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase2c-experiment-design'
thisStepFile: '{workflow_path}/steps/step-02-archon-search.md'
nextStepFile: '{workflow_path}/steps/step-03-exa-github.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{hypothesis_folder}/02c_experiment_brief.md'

# Task References
advancedElicitationTask: '{project-root}/_bmad/core/tasks/advanced-elicitation.xml'
partyModeWorkflow: '{project-root}/_bmad/core/workflows/party-mode/workflow.md'
---

# Step 2: Implementation Research - Archon MCP

## STEP GOAL:

Search Archon Knowledge Base for past implementation cases, experiment designs, best practices, and code examples related to the hypothesis mechanism. Extract datasets, hyperparameters, architectures, and implementation patterns to ground the experiment design in proven research.

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 🎯 Focus only on Archon MCP knowledge base and code searches
- 🚫 FORBIDDEN to skip MCP calls or fabricate search results
- 💬 Approach: Execute 2-3 knowledge queries + 1-2 code queries
- 📋 Document ALL findings with sources for traceability

## EXECUTION PROTOCOLS:

- 🎯 Execute actual MCP calls - never simulate results
- 💾 Document all query results in structured format
- 📖 Extract key insights: datasets, hyperparameters, architectures
- 🚫 Never proceed without at least 1 knowledge base result

## CONTEXT BOUNDARIES:

- Available context: Hypothesis statement, mechanism name, problem domain from Step 1
- Focus: Archon knowledge base searches only (Exa is next step)
- Limits: Do not perform GitHub searches in this step
- Dependencies: hypothesis_id and mechanism_name from previous step

---

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Display Step Start

Display: "🔍 Step 2: Searching Archon Knowledge Base for implementation cases..."

### 2. Extract Key Terms from Hypothesis

From {hypothesis_statement}, identify:
- `{mechanism_name}`: Core mechanism being tested (e.g., "range-dependent attention")
- `{problem_domain}`: Research area (e.g., "long-tail learning")
- `{dataset_type}`: Type of data (e.g., "image classification")

Display extracted terms to user for confirmation.

### 3. Execute Knowledge Base Searches (2-3 Queries)

**Query 1: Experiment Design Search**
```
mcp__archon__rag_search_knowledge_base(
  query="{mechanism_name} experiment design dataset",
  match_count=5
)
```

**Extract from results:**
- What datasets are used for this mechanism?
- What are typical experiment setups?
- What hyperparameters are common?
- What baselines are standard?

**Query 2: Implementation Challenges**
```
mcp__archon__rag_search_knowledge_base(
  query="{mechanism_name} implementation challenges best practices",
  match_count=5
)
```

**Extract from results:**
- Common pitfalls
- Best practices
- Things to avoid
- Tips for success

**Query 3: Benchmark Results (Optional)**
```
mcp__archon__rag_search_knowledge_base(
  query="{dataset_type} benchmark {problem_domain}",
  match_count=5
)
```

**Extract from results:**
- Standard datasets for this domain
- Expected baseline performance
- State-of-the-art results

### 4. Execute Code Examples Search (1-2 Queries)

**Query 1: Mechanism Implementation**
```
mcp__archon__rag_search_code_examples(
  query="{mechanism_name} PyTorch",
  match_count=5
)
```

**Extract from results:**
- Code snippets showing mechanism implementation
- Architecture patterns
- Common code structures

**Query 2: Dataset Implementation (Optional)**
```
mcp__archon__rag_search_code_examples(
  query="{dataset_type} PyTorch dataloader",
  match_count=5
)
```

### 5. Document All Findings

Compile findings in structured format:

```markdown
### Archon Knowledge Base Findings

**Query 1: Experiment Design**
- Result 1: [Title]
  - Dataset: [name]
  - Hyperparameters: [list]
  - Key insight: [insight]

- Result 2: [Continue for all results]

**Query 2: Implementation Challenges**
- [Findings]

**Query 3: Benchmark Results**
- [Findings if searched]

### Archon Code Examples

**Query 1: Mechanism Implementation**
- Example 1: [Source]
  ```python
  # [Code snippet if available]
  ```
  - Pattern: [description]
  - Insight: [insight]
```

Store findings as: `{archon_knowledge_findings}` and `{archon_code_findings}`

### 6. Update Output File

Fill these placeholders in {outputFile}:
- `archon_knowledge_findings`
- `archon_code_findings`

Write the file back after filling placeholders.

Display: "✅ Archon findings saved to output file"

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

ONLY WHEN [C continue option] is selected and [Archon findings documented and saved], will you then load and read fully `{workflow_path}/steps/step-03-exa-github.md` to execute and begin GitHub code search.

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Key terms extracted from hypothesis
- At least 2-3 Archon knowledge base queries executed
- At least 1-2 Archon code example queries executed
- All results documented with sources
- Findings saved to output file
- Menu presented and user input handled correctly

### ❌ SYSTEM FAILURE:

- Fabricating search results without executing MCP calls
- Skipping required queries
- Not documenting sources for findings
- Proceeding without user input/selection
- Not updating output file
- Skipping steps or optimizing sequence

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
