# Validated Hypothesis Synthesis

**Generated:** {{generated_date}}
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

{{executive_summary}}

| Metric | Value |
|--------|-------|
| **Original Core Statement** | {{original_core_statement_short}} |
| **Refined Core Statement** | {{refined_core_statement_short}} |
| **Predictions Supported** | {{predictions_supported}} / {{predictions_total}} |
| **Overall Pass Rate** | {{overall_pass_rate}}% |
| **Hypotheses Validated** | {{validated_count}} / {{total_count}} |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | {{p1_statement}} | {{p1_tested_by}} | {{p1_metric}} | {{p1_result}} | {{p1_status}} | {{p1_confidence}} | {{p1_evidence}} |
| **P2** | {{p2_statement}} | {{p2_tested_by}} | {{p2_metric}} | {{p2_result}} | {{p2_status}} | {{p2_confidence}} | {{p2_evidence}} |
| **P3** | {{p3_statement}} | {{p3_tested_by}} | {{p3_metric}} | {{p3_result}} | {{p3_status}} | {{p3_confidence}} | {{p3_evidence}} |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
{{#each_mechanism_step}}
| {{step_number}} | {{description}} | {{falsifier}} | {{evidence}} | {{status}} |
{{/each_mechanism_step}}

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> {{original_core_statement}}

### 3.2 Refined Core Statement (Phase 4.5)

> {{refined_core_statement}}

**Key Changes:**
{{refinement_changelog}}

### 3.3 Causal Mechanism — Verified Chain

```
{{verified_causal_chain}}
```

**Removed/Modified Steps:**
{{#each_removed_mechanism_step}}
- **Step {{step_number}}** ({{original_description}}): {{removal_reason}}
{{/each_removed_mechanism_step}}

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
{{#each_claim_change}}
| {{original_claim}} | {{action}} | {{reason}} | {{evidence}} |
{{/each_claim_change}}

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
{{#each_assumption}}
| {{assumption}} | {{original_status}} | {{verification_status}} | {{evidence}} | {{violation_impact}} |
{{/each_assumption}}

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

{{mechanistic_explanation}}

### 4.2 Unexpected Findings Analysis

{{#each_unexpected_finding}}
#### Finding: {{finding_title}}

- **Observation:** {{observation}}
- **Why Unexpected:** {{why_unexpected}}
- **Competing Explanations:**
{{#each_competing_explanation}}
  {{index}}. **{{explanation_name}}:** {{explanation_detail}} (Plausibility: {{plausibility}})
{{/each_competing_explanation}}
- **Most Likely Interpretation:** {{most_likely}}
- **Additional Evidence Needed:** {{evidence_needed}}

{{/each_unexpected_finding}}

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
{{#each_literature_connection}}
| {{our_finding}} | {{related_work}} | {{relationship}} | {{citation}} |
{{/each_literature_connection}}

### 4.4 Theoretical Contributions

{{#each_contribution}}
{{index}}. **{{contribution_title}}:** {{contribution_description}}
{{/each_contribution}}

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
{{#each_hypothesis}}
| **{{hypothesis_id}}** | {{title}} | {{gate_type}} | {{gate_result}} | {{pass_rate}}% | {{key_insight}} |
{{/each_hypothesis}}

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | {{total_hypotheses}} |
| **Fully Validated** | {{fully_validated}} |
| **Partially Validated** | {{partially_validated}} |
| **Failed** | {{failed_count}} |
| **Total Tasks Completed** | {{total_tasks_completed}} / {{total_tasks}} |
| **SDD Compliance Rate** | {{sdd_compliance_rate}}% |

### 5.3 Optimal Hyperparameters

```yaml
{{optimal_hyperparameters_yaml}}
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
{{#each_proven_component}}
| {{component_name}} | {{source_hypothesis}} | {{file_path}} | {{reusable}} |
{{/each_proven_component}}

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
{{#each_hypothesis_comparison}}
| **{{hypothesis_id}}** | {{planned_metric}} | {{planned_target}} | {{actual_result}} | {{deviation_type}} | {{notes}} |
{{/each_hypothesis_comparison}}

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
{{#each_figure}}
| {{figure_id}} | {{source_path}} | {{description}} | {{suggested_section}} |
{{/each_figure}}

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

{{#each_limitation}}
#### {{limitation_title}}

- **What:** {{what}}
- **Why This Matters:** {{why_matters}}
- **Root Cause:** {{root_cause}}
- **Impact on Claims:** {{impact_on_claims}}
- **Why Acceptable:** {{why_acceptable}}

{{/each_limitation}}

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
{{#each_scope_condition}}
| {{condition}} | {{holds}} | {{may_not_hold}} | {{evidence}} |
{{/each_scope_condition}}

### 6.3 Assumption Violation Impact

{{#each_violated_assumption}}
- **{{assumption}}:** {{violation_description}} → Impact: {{impact}}
{{/each_violated_assumption}}

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

{{#each_untested_alternative}}
- **Alternative:** {{alternative_explanation}}
  - **Why Not Yet Tested:** {{why_untested}}
  - **Proposed Experiment:** {{proposed_experiment}}
  - **Expected Outcome:** {{expected_outcome}}
{{/each_untested_alternative}}

### 7.2 From Unverified Assumptions

{{#each_unverified_assumption}}
- **Assumption:** {{assumption}}
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** {{proposed_test}}
  - **If Violated:** {{if_violated}}
{{/each_unverified_assumption}}

### 7.3 From Scope Extension Opportunities

{{#each_scope_extension}}
- **Extension:** {{extension_description}}
  - **Current Evidence Suggesting Feasibility:** {{feasibility_evidence}}
  - **Required Resources:** {{resources}}
{{/each_scope_extension}}

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

{{recommended_hook}}

**Hook Strategy:** {{hook_strategy}}
**Why This Hook:** {{hook_rationale}}

### 8.2 Key Insight (Experiment-Verified)

> {{verified_key_insight}}

**Verification Evidence:** {{insight_evidence}}

### 8.3 Strongest Claims (Paper-Ready)

{{#each_strongest_claim}}
{{index}}. **{{claim}}**
   - Evidence: {{evidence}}
   - Confidence: {{confidence}}
   - Suggested Section: {{suggested_section}}
{{/each_strongest_claim}}

### 8.4 Honest Limitations (Must Include in Paper)

{{#each_honest_limitation}}
{{index}}. **{{limitation}}**
   - Why Acceptable: {{why_acceptable}}
   - Suggested Framing: {{suggested_framing}}
{{/each_honest_limitation}}

### 8.5 Evidence Highlights (Most Persuasive)

{{#each_evidence_highlight}}
{{index}}. **{{highlight_title}}**
   - Data: {{data_summary}}
   - "So What": {{interpretation}}
   - Suggested Figure/Table: {{suggested_visual}}
{{/each_evidence_highlight}}

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
{{#each_source_file}}
| `{{file_path}}` | {{hypothesis_id}} | {{purpose}} |
{{/each_source_file}}

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
