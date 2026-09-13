# Known Failure Modes Reference

> **Reference File:** Extracted from workflow.md for file size optimization
>
> **Purpose:** Documents past mistakes to prevent repetition

---

## Tool Mapping Table (Must Follow)

| Step | Output | Correct Method | Wrong Method (Forbidden) |
|------|--------|-------------|-------------------|
| Step 2 | PRD | Execute **BMAD workflow** | ❌ Task("PRD Agent") |
| Step 3 | Architecture | `Task(subagent_type="architecture-agent")` | ❌ Direct Write tool generation |
| Step 5 | Logic | `Task(subagent_type="logic-agent")` | ❌ Direct Write tool generation |
| Step 5 | Config | `Task(subagent_type="configuration-agent")` | ❌ Direct Write tool generation |
| Step 9 | 03_tasks.yaml | Parse 03_*.md + Write to YAML file | ❌ Creating Archon tasks |

---

## Past Mistake Examples

> **Mistakes from 2024 Sessions:**
>
> 1. **Created PRD with Task agent**: Invented "PRD Agent" as subagent_type and attempted PRD generation via Task tool
> - Result: Skipped BMAD's collaborative discovery process, quality degradation
>
> 2. **Skipped data preparation tasks**: Only created code implementation tasks, missing data download and environment setup
> - Result: Phase 4 failed repeatedly due to missing datasets
>
> 3. **UNATTENDED mode misunderstanding**: Incorrectly interpreted "auto execution" = "I can generate directly"
> - Result: Defined Agents (architecture-agent, logic-agent, configuration-agent) not used

---

## Correct Interpretation of UNATTENDED Mode

```
UNATTENDED mode = "Automatically execute defined workflows"
UNATTENDED mode ≠ "Ignore workflows and generate directly"
```

**Can Skip in UNATTENDED Mode:**
- User confirmation prompts ([C] Continue, [Y/N])
- Review menus ([R] Review)
- Explanation and guidance messages

**Still Required in UNATTENDED Mode:**
- ✅ Use defined subagent_type (architecture-agent, logic-agent, configuration-agent)
- ✅ Execute BMAD workflow (PRD)
- ✅ Parse all 03_*.md documents for task extraction
- ✅ MCP tool calls (Archon, Serena)
- ✅ File creation verification

---

## Error Handling Reference

### Missing Phase 2C Input
```
Error: Phase 2C experiment brief required
File not found: {hypothesis_folder}/02c_experiment_brief.md
Please run /phase2c-experiment-design first
```
**Action**: STOP and inform user

### Archon MCP Unavailable
```
Error: Archon MCP required but not available
Phase 3 requires Archon MCP for project and task management
Please ensure Archon MCP server is running
```
**Action**: STOP and inform user

### Sub-Workflow Failure
```
Error: {{workflow_name}} workflow failed
Please review the error and retry the workflow
Phase 3 can resume from this step once resolved
```
**Action**: Allow user to retry or exit

### Validation Failure
If validation score < 9/15 in Step 8:
```
Error: Phase 3 validation failed
Critical issues must be resolved before Phase 4
See validation report for details
```
**Action**: Guide user through fixing issues
