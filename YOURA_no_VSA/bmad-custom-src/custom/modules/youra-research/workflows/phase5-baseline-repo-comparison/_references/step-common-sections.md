# Phase 5 Step Common Sections

> **Purpose:** Centralized templates for common sections across all Phase 5 step files.
> **Usage:** Each step file references this file and uses appropriate templates.
> **Reduces:** ~900 lines of duplication across 13 step files.

---

## How to Use This Reference

Each step file should include in its frontmatter:

```yaml
# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'
```

---

## ~~Template 1: Section 0 - Update Step Task Status~~ ()

> Step progress is now tracked via `checkpoint.current_step` field.
> This template is no longer referenced by step files.

```python
# Step progress tracked via checkpoint.current_step instead
```

---

## Template 2: MANDATORY EXECUTION RULES

### Usage Pattern

```markdown
## MANDATORY EXECUTION RULES (READ FIRST):

> **Reference:** `{common_sections_ref}` - Template 2

### Universal Rules:
<include-universal-rules />

### Role Reinforcement:
<include-role-reinforcement role="{{role_type}}" />

### Step-Specific Rules:
{{step_specific_rules}}
```

### Universal Rules (Standard)

- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step, ensure entire file is read
- NEVER fabricate results or skip verification steps
- Follow exact instructions without optimization or shortcuts

### Role Reinforcement (Standard)

- If you already have been given a name, communication_style and identity, continue to use those
- We engage in systematic execution through defined protocols
- You bring expertise appropriate to the current step

### Role Type Variations

| Role Type | Description |
|-----------|-------------|
| `orchestrator` | "You are an orchestrator, delegating work to sub-agents" |
| `executor` | "You are an executor, performing direct actions" |
| `evaluator` | "You are an evaluator, assessing results and making decisions" |
| `generator` | "You are a generator, creating artifacts and documents" |

---

## Template 3: SUCCESS/FAILURE METRICS

### Usage Pattern

```markdown
## SYSTEM SUCCESS/FAILURE METRICS

> **Reference:** `{common_sections_ref}` - Template 3

### SUCCESS:
{{success_criteria}}

### SYSTEM FAILURE:
{{failure_criteria}}

<include-master-rule />
```

### Master Rule (ALWAYS INCLUDE)

```markdown
**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
```

### Common Success Criteria Patterns

| Pattern | Applicable Steps |
|---------|------------------|
| Checkpoint updated with results | All steps |
| Next step loaded and executed | All steps except final |
| Archon tasks updated | Steps with task management |
| Output files generated | Generation steps |
| Sub-agent invoked via Task tool | Delegation steps |

### Common Failure Criteria Patterns

| Pattern | Applicable Steps |
|---------|------------------|
| Skipping step-specific verification | All steps |
| Not updating checkpoint | All steps |
| Not loading next step immediately | All steps except final |
| Fabricating or inventing results | All steps |
| Running commands directly instead of via sub-agent | Delegation steps |

---

## Template 4: Step Completion Criteria

### Usage Pattern

```markdown
## Step Completion Criteria

> **Reference:** `{common_sections_ref}` - Template 4

{{step_specific_criteria}}

---

## STEP ROUTING

**On completion:** Proceed to {{next_step_file}}

```python
checkpoint.current_step = "{{next_step_number}}"
SAVE checkpoint
Load, read entire file, then execute: {nextStepFile}
```
```

### Common Criteria Patterns

- [ ] Checkpoint loaded and validated
- [ ] Required input files verified
- [ ] Step-specific processing completed
- [ ] Output files generated (if applicable)
- [ ] Archon tasks updated (if applicable)
- [ ] Checkpoint saved with current step status

---

## Template 5: UNATTENDED Mode Declaration

### Usage Pattern

```markdown
# Step {{step_number}}: {{step_title}} (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Pattern:** {{step_pattern}}
```

### Mode Declaration (Frontmatter)

```yaml
# Mode
mode: UNATTENDED (Fully Automatic)
```

---

## Template 6: Context Boundaries

### Usage Pattern

```markdown
## CONTEXT BOUNDARIES:

- Available context: {{available_context}}
- Focus: {{step_focus}}
- Limits: {{step_limits}}
- Dependencies: {{step_dependencies}}
```

### Common Patterns

| Field | Common Values |
|-------|---------------|
| Available context | checkpoint, Archon tasks, verification_state |
| Focus | [Step-specific focus] |
| Limits | Do not [out-of-scope actions] |
| Dependencies | Step X must be completed |

---

## Template 7: Error Handling

### Usage Pattern

```markdown
## ERROR HANDLING

> **Reference:** `{common_sections_ref}` - Template 7

| Error | Action |
|-------|--------|
{{error_handling_table}}
```

### Common Error Patterns

| Error | Standard Action |
|-------|-----------------|
| MCP tool fails | Retry 1-3 times with 15s delay |
| File not found | Log error, check dependencies |
| Invalid JSON | Treat as failure, retry or skip |
| Sub-agent timeout | Log error, proceed with partial |
| Checkpoint missing | Load from backup or abort |

---

## Quick Reference: Step IDs

| Step File | Step ID | Description |
|-----------|---------|-------------|
| step-01-init.md | 5-01 | Initialize baseline comparison |
| step-02-define.md | 5-02 | Define comparison scope |
| step-03-search.md | 5-03 | Search baseline repositories |
| step-04-evaluate.md | 5-04 | Evaluate candidates |
| step-05-select.md | 5-05 | Select top baselines |
| step-05.5-baseline-env-verification.md | 5-05.5 | Verify baseline environments (Mode B) |
| step-06-setup.md | 5-06 | Clone and setup |
| step-07-adaptation-coding.md | 5-07 | Generate adaptation code |
| step-08-validation.md | 5-08 | Validate adaptations |
| step-09-experiment.md | 5-09 | Execute experiments |
| step-10-report.md | 5-10 | Generate report |
| step-10a-gate-evaluation.md | 5-10a | Gate evaluation |
| step-10b-finalize.md | 5-10b | Finalize Phase 5 |

---

