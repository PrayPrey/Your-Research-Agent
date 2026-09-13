# Phase 4 Validation Report: {hypothesis_id}

**Generated:** {generated_date}
**Execution Mode:** {execution_mode}
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | {hypothesis_id} |
| **Title** | {hypothesis_title} |
| **Phase 4 Start** | {start_timestamp} |
| **Phase 4 End** | {end_timestamp} |
| **Duration** | {duration} |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | {tasks_total} |
| Completed | {tasks_completed} |
| Failed | {tasks_failed} |
| Skipped | {tasks_skipped} |
| Coder-Validator Cycles | {coder_validator_cycles}/5 |

### Generated Files

| File | Lines | Last Modified |
|------|-------|---------------|
| {file_1} | {lines_1} | {modified_1} |
| {file_2} | {lines_2} | {modified_2} |
| {file_3} | {lines_3} | {modified_3} |
| {file_4} | {lines_4} | {modified_4} |

### Task History

{FOR_EACH_TASK}
- **{task_id}**: {task_status} ({task_attempts} attempts)
  - Title: {task_title}
  - Issues: {task_issues}
{END_FOR_EACH}

---

## Code Quality Checklist

Based on Validator Agent evaluation:

- [{syntax_check}] Syntax validation passed
- [{type_hints}] Type hints compliance
- [{api_match}] API signatures match 03_logic.md
- [{config_match}] Configuration schema match 03_config.md
- [{imports_valid}] Cross-file dependencies resolved
- [{anti_patterns}] No obvious anti-patterns

### Issues Detected

{IF_ISSUES}
{issue_list}
{END_IF}

{IF_NO_ISSUES}
No issues detected - all quality checks passed.
{END_IF}

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| **Mode** | {experiment_mode} |
| **Status** | {experiment_status} |
| **Duration** | {experiment_duration} |

### Metrics

{IF_METRICS}
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| {metric_1_name} | {metric_1_actual} | {metric_1_target} | {metric_1_status} |
| {metric_2_name} | {metric_2_actual} | {metric_2_target} | {metric_2_status} |
| {metric_3_name} | {metric_3_actual} | {metric_3_target} | {metric_3_status} |
{END_IF}

{IF_SKIPPED}
*Experiment was skipped - no metrics available*

**Reason:** {skip_reason}
{END_IF}

{IF_FAILED}
### Failure Details

- **Reason:** {failure_reason}
- **Error Message:** {error_message}
- **Stack Trace:** {stack_trace}
{END_IF}

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | {gate_type} |
| **Result** | {gate_result} |
| **Satisfied** | {gate_satisfied} |
| **Evaluated At** | {gate_evaluated_at} |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| {criterion_1} | {target_1} | {actual_1} | {result_1} |
| {criterion_2} | {target_2} | {actual_2} | {result_2} |

{IF_GATE_FAILED}
### Failure Analysis

- **Reason:** {gate_failure_reason}
- **Impact:** {gate_failure_impact}
- **Recommendations:**
  - {recommendation_1}
  - {recommendation_2}
{END_IF}

---

## Next Steps

{IF_GATE_PASS}
### ✅ Ready for Phase 5

All validation criteria met. The hypothesis implementation is complete and ready for:

1. Phase 5 integration review
2. Documentation and publication preparation
3. Main codebase integration (if applicable)

**Proceed to:** Phase 5 workflow
{END_IF}

{IF_SHOULD_WORK_FAIL}
### ⚠️ Proceed with Limitations

Gate criteria not fully met, but workflow continues with noted limitations:

- **Limitation:** {limitation_note}
- **Confidence Level:** Reduced
- **Recommendations:**
  - {recommendation_1}
  - {recommendation_2}

**Next Action:** Proceed to Phase 5 with caveats documented
{END_IF}

{IF_MUST_PASS_FAIL}
### ❌ Workflow Stopped

MUST_PASS gate failed. The hypothesis is blocked from proceeding.

**Failure Reason:** {must_pass_failure_reason}

**Debug Steps:**
1. Review code quality issues in sections above
2. Check experiment setup and configuration
3. Verify hypothesis assumptions
4. Consider revising the hypothesis or implementation approach

**Partial Results Preserved:**
- Completed tasks: {completed_tasks}
- Generated files: {generated_files}
- Experiment results (if any): experiment_results.json

**Recovery Options:**
- Fix issues and re-run Phase 4
- Mark hypothesis as failed and document learnings
- Escalate to team for review
{END_IF}

{IF_DETERMINES_SUCCESS_PASS}
### ✅ Hypothesis Validated

Success criteria met. The hypothesis is **CONFIRMED**.

**Outcome:** SUCCESS
**Confidence:** High
**Validation:** Experiment results meet all success criteria

**Ready for:** Phase 5 publication and integration
{END_IF}

{IF_DETERMINES_SUCCESS_FAIL}
### ❌ Hypothesis Invalidated

Success criteria not met. The hypothesis is **REJECTED**.

**Outcome:** FAILURE
**Analysis:** {invalidation_analysis}

**Alternative Approaches:**
- {alternative_1}
- {alternative_2}

**Documentation:** Record findings for future reference
{END_IF}

---

## Appendix

### Files Reference

| File | Purpose |
|------|---------|
| `04_checkpoint.yaml` | Recovery checkpoint (archived) |
| `04_validation.md` | This report |
| `experiment_results.json` | Raw experiment data |
| `code/` | Generated implementation |
| `verification_state.yaml` | Updated gate status |

### Checkpoint Summary

```yaml
version: "{checkpoint_version}"
hypothesis_id: "{hypothesis_id}"
created_at: "{checkpoint_created}"
completed_at: "{checkpoint_completed}"
tasks:
  total: {tasks_total}
  completed: {tasks_completed}
coder_validator_cycles: {cycles}
unattended_mode: {unattended_mode}
```

### Environment

| Item | Value |
|------|-------|
| Execution Date | {execution_date} |
| Mode | {execution_mode} |
| MCP Servers | {mcp_servers_used} |
| Duration | {total_duration} |

---

## Phase 2C Handoff

> **Purpose:** This section is designed for Phase 2C to consume when processing dependent hypotheses.
> Auto-generated from experiment results and validation data.
> Parse-friendly format for automated extraction.

### Source Information

| Field | Value |
|-------|-------|
| **Source Hypothesis** | {hypothesis_id} |
| **Generated At** | {generated_date} |
| **Gate Result** | {gate_result} |
| **Ready for Dependents** | {ready_for_dependents} |

### Proven Components

Components that were successfully implemented and validated:

| Component | File | Type | Evidence | Reusable |
|-----------|------|------|----------|----------|
| {component_1_name} | {component_1_file} | {component_1_type} | {component_1_evidence} | {component_1_reusable} |
| {component_2_name} | {component_2_file} | {component_2_type} | {component_2_evidence} | {component_2_reusable} |

{IF_REUSE_NOTES}
**Reuse Notes:**
{reuse_notes_list}
{END_IF}

{IF_NOT_EXISTENCE}
### Optimal Hyperparameters

Final hyperparameters that achieved the reported metrics:

```yaml
# Copy-paste ready for dependent hypotheses
training:
  learning_rate: {hp_learning_rate}
  batch_size: {hp_batch_size}
  epochs: {hp_epochs}
  optimizer: {hp_optimizer}
  scheduler: {hp_scheduler}

model:
  hidden_dim: {hp_hidden_dim}
  num_layers: {hp_num_layers}
  dropout: {hp_dropout}

regularization:
  weight_decay: {hp_weight_decay}
  label_smoothing: {hp_label_smoothing}

# Metrics achieved with these parameters
achieved_metrics:
  accuracy: {achieved_accuracy}
  loss: {achieved_loss}
```
{END_IF}

### Lessons Learned

#### What Worked Well
{what_worked_list}

#### What Didn't Work
{what_didnt_work_list}

#### Unexpected Findings
{unexpected_findings_list}

#### Key Insight
> {key_insight}

### Recommendations for Dependent Hypotheses

{IF_DEPENDENTS_EXIST}
**Dependent Hypotheses:** {dependent_hypothesis_ids}

#### General Recommendations
{general_recommendations_list}

#### Specific Recommendations
{specific_recommendations_by_hypothesis}

#### Warnings (What to Avoid)
{warnings_list}

#### Suggested Starting Point
- **Hyperparameters:** Start with the optimal values above
- **Adjustments:** {suggested_adjustments}
{END_IF}

{IF_NO_DEPENDENTS}
*No dependent hypotheses identified. This section is informational for future reference.*
{END_IF}

---

*This section is auto-generated for Phase 2C consumption. Edit only if necessary.*

---

*Report generated by Phase 4 Implementation & Validation Workflow*
*Anonymous Research Pipeline - Phase 4*
