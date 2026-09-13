---
name: 'step-10a-gate-evaluation'
description: 'Mode B gate evaluation: win ≥threshold baselines (ours > baseline on their turf)'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase5-baseline-repo-comparison'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Helper References
multi_comparison_gate: '{helpers_path}/multi_comparison_gate.md'
serena_memory_patterns: '{helpers_path}/serena_memory_patterns.md'

# File References
thisStepFile: '{workflow_path}/steps/step-10a-gate-evaluation.md'
prevStepFile: '{workflow_path}/steps/step-10-report.md'
nextStepFile: '{workflow_path}/steps/step-10b-finalize.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
checkpoint_file: '{baseline_folder}/05_baseline_checkpoint.yaml'
comparison_data: '{baseline_folder}/experiments/comparison_data.csv'
verification_state: '{research_folder}/verification_state.yaml'
final_report: '{baseline_folder}/05_baseline_comparison.md'

# Config: Read from checkpoint.workflow_config.gate (Source: workflow.yaml)

# Common Sections Reference
common_sections_ref: '{workflow_path}/_references/step-common-sections.md'

# Mode
mode: UNATTENDED (Fully Automatic)
---

# Step 10a: Gate Evaluation (Mode B - Per-Baseline Comparison)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Pattern:** State update + Gate evaluation with Serena Memory integration
> **Gate Criteria:** Win ≥{baseline_win_threshold} baselines (ours > baseline on their turf)
> **Mode:** Mode B (Inject OUR algorithm into BASELINE's environment)

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- MUST check retry limit BEFORE gate evaluation
- MUST save to Serena Memory BEFORE gate evaluation
- MUST update verification_state.yaml with complete results
- **MUST evaluate gate for ALL PROCEED baselines (Mode B: per-baseline comparison)**

---

## STEP GOAL

1. Update verification_state.yaml with Mode B comparison results
2. Check retry limit (infinite loop prevention)
3. Save comparison data to Serena Memory
4. **Evaluate DETERMINES_SUCCESS gate with Mode B criteria:**
   - Compute win/lose for each baseline (ours_injected vs baseline_original on their turf)
   - Apply threshold: Win ≥{threshold} baselines (from checkpoint.workflow_config.gate)

---

## 10.5 Update verification_state.yaml

### 10.5.1 Update main_hypothesis.baseline_comparison (Mode B - Per-Baseline)

**Update Path:** `main_hypothesis.baseline_comparison`

```yaml
baseline_comparison:
  status: "COMPLETED"
  completed_at: "{timestamp}"
  report_file: "{baseline_folder}/05_baseline_comparison.md"
  mode: "B"
  gate:
    type: "DETERMINES_SUCCESS"
    criteria: "win ≥{threshold} baselines (ours > baseline on their turf)" # threshold from checkpoint.workflow_config.gate
    satisfied: null # Will be set after gate evaluation (10.6)
    result: null # Will be set after gate evaluation (10.6)

  # Mode B results: per-baseline comparison
  baselines: [...] # From checkpoint
  per_baseline_results: # From gate evaluation
    - repo_name: "{baseline_1}"
      baseline_model: "{model}"
      baseline_dataset: "{dataset}"
      baseline_result: {value}
      ours_result: {value}
      winner: "ours|baseline"
      improvement: "{+X.X%}"
  aggregate_results:
    baselines_won: X/3
    threshold_met: true/false
```

---

## 10.5a Check Retry Limit (Infinite Loop Prevention)

<critical>
**BEFORE evaluating gate, check if we've exceeded retry limit!**
</critical>

```python
# Load checkpoint
checkpoint = read_yaml("{baseline_folder}/05_baseline_checkpoint.yaml")

# Get retry count
phase5_retry_count = checkpoint.retry_tracking.phase5_retry_count
max_retries = checkpoint.retry_tracking.max_phase5_retries # default: 3

IF phase5_retry_count >= max_retries:
    # Update verification_state.yaml
    workflow.status = "STOPPED"
    workflow.stop_reason = "Maximum Phase 5 retries reached"

    # Append to status_history
    status_history.append({
        status: "STOPPED",
        phase: "Phase 5",
        timestamp: NOW,
        trigger: "Max retries reached",
        hypothesis_id: hypothesis_id,
        details: f"Phase 5 retry limit ({max_retries}) exceeded"
    })

    EXIT # Do not proceed to gate evaluation
```

---

## 10.5b Save to Serena Memory

> **REFERENCE:** Read `{serena_memory_patterns}` for detailed implementation

**Use helpers for Serena Memory persistence:**

```python
# See: {serena_memory_patterns}

# Always save comparison summary
save_comparison_summary(
    hypothesis_id,
    gate_result="pending", # Will update after gate
    comparison_data={
        "ours_best": ours_best_psi,
        "baseline_best": baseline_best_psi
    },
    hypothesis_journey=version_history
)
```

**Key Helper Functions:**
- `save_comparison_summary()` - Always save (PASS or PARTIAL)
- `save_failure_record()` - Save detailed failure on PARTIAL

---

## 10.6 Mode B Comparison Gate

> **REFERENCE:** Read `{multi_comparison_gate}` for detailed implementation
> **Gate Criteria:** Win ≥{baseline_win_threshold} baselines (ours > baseline on their turf)

**Use the `evaluate_mode_b_gate()` function from helper:**

```python
# See: {multi_comparison_gate}

# Get baselines from checkpoint
baselines = [b["repo_name"] for b in checkpoint.selection.baselines if b["status"] == "PROCEED"]

# Load gate config from checkpoint (Single Source of Truth: workflow.yaml)
min_baselines = checkpoint["workflow_config"]["gate"]["min_baselines_to_beat"]

# Evaluate Mode B gate
gate_result = evaluate_mode_b_gate(
    comparison_data_path=f"{baseline_folder}/experiments/comparison_data.csv",
    baselines=baselines,
    baseline_threshold=min_baselines # value from workflow.yaml
)

print(gate_result["summary_table"])
```

**Key Helper Functions (Mode B):**
- `compute_win_matrix()` - Per-baseline win/lose (ours vs baseline on their turf)
- `compute_per_baseline_wins()` - Win count + threshold check
- `compute_overall_gate()` - Overall gate result
- `classify_failure()` - Classify failure type on PARTIAL

---

### On PASS (Our Method Wins ≥{baseline_win_threshold} Baselines on Their Turf)

```python
IF gate_result["gate_result"] == "PASS":
    print("✅ DETERMINES_SUCCESS: PASS")

    # Apply verification_state updates from helper
    FOR path, value IN gate_result["verification_state_updates"].items():
        update_nested_yaml(verification_state, path, value)

    # Update episode
    episode.status = "COMPLETED"
    episode.terminated_properly = True
    episode.termination_trigger = "DETERMINES_SUCCESS_PASS"
    episode.routing_decision = "Phase 6"

    # Update workflow
    workflow.status = "COMPLETED"
    workflow.next_action = "Proceed to Phase 6 Paper Writing"
```

**→ Continue to step-10b-finalize.md**

---

### On PARTIAL (Failed to Win ≥{baseline_win_threshold} Baselines on Their Turf)

<critical>
**MODE B FAILURE = FUNDAMENTAL APPROACH PROBLEM**

If our method cannot beat ≥{baseline_win_threshold} baselines on their own environments, this indicates a fundamental flaw in the hypothesis/approach itself, NOT just an implementation issue. Phase 2A modifications will not help - we need a NEW research direction from Phase 0.

**Mode B Context:** Each baseline used THEIR OWN model, dataset, config. Our algorithm failed to prove superiority even when tested on "baseline's home turf."

**This is PROPER TERMINATION** - the system correctly identified the approach is inferior and is routing appropriately.
</critical>

```python
IF gate_result["gate_result"] == "PARTIAL":
    print("❌ DETERMINES_SUCCESS: PARTIAL")

    # Classify failure
    failure = classify_failure(
        gate_result,
        ours_best_psi,
        baseline_best_psi
    )

    # Save detailed failure to Serena Memory
    # See: {serena_memory_patterns}
    save_failure_record(
        hypothesis_id,
        "Phase 5",
        failure["failure_type"],
        {
            "ours_best": ours_best_psi,
            "baseline_best": baseline_best_psi,
            "gap": failure["gap"]
        },
        failure["root_causes"],
        lessons_learned,
        {
            "suggestions": phase2a_suggestions,
            "avoid": failed_approaches,
            "promise": partial_successes
        }
    )

    # Update verification_state for PARTIAL
    episode.status = "TERMINATED"
    episode.terminated_properly = True # This IS proper termination!
    episode.termination_trigger = "DETERMINES_SUCCESS_PARTIAL"
    episode.routing_decision = "Phase 0"
    episode.routing_reason = "Approach failed to consistently outperform baselines"

    workflow.status = "ROUTED"
    workflow.routing = {
        "target": "Phase 0",
        "source_hypothesis": main_hypothesis_id,
        "reason": "DETERMINES_SUCCESS_PARTIAL",
        "timestamp": datetime.now().isoformat()
    }
    workflow.stop_reason = "DETERMINES_SUCCESS gate PARTIAL"
    workflow.next_action = "Route to Phase 0 for new research direction"

    # Update retry tracking
    checkpoint.retry_tracking.phase5_retry_count += 1
```

**→ BENCHMARK MODE: Record routing decision, do NOT execute**

For benchmark evaluation, the system RECORDS the routing decision but does NOT execute `/phase0-brainstorm`.

**Why Phase 0, not Phase 2A:**
| Scenario | Routing | Reason |
|----------|---------|--------|
| Implementation bug | Phase 4 | Fix code, re-run |
| Experiment design flaw | Phase 2C | Redesign experiment |
| Hypothesis needs adjustment | Phase 2A | Modify hypothesis |
| **Approach fundamentally inferior** | **Phase 0** | **Need NEW direction** |

---

## Step Completion Criteria

- [ ] verification_state.yaml updated with baseline_comparison status
- [ ] Retry limit checked (infinite loop prevention)
- [ ] Comparison summary saved to Serena Memory
- [ ] If PARTIAL: Failure analysis saved to Serena Memory
- [ ] **Baseline Comparison Gate evaluated (PASS or PARTIAL)**

---

## STEP ROUTING

**On PASS or PARTIAL:** Proceed to step-10b-finalize.md

```python
checkpoint.current_step = "10b"
checkpoint.gate_result = gate_result["gate_result"] # PASS or PARTIAL
SAVE checkpoint
Load, read entire file, then execute: {nextStepFile}
```

---

## SUCCESS/FAILURE

> **Reference:** `{common_sections_ref}` - Template 3 (Master Rule)

### SUCCESS:
- verification_state.yaml updated with Mode B comparison block
- Retry limit checked before gate evaluation
- Comparison summary saved to Serena Memory (via helper)
- **Win/lose computed for ALL PROCEED baselines (ours_injected vs baseline_original)**
- **Gate threshold correctly applied (≥{baseline_win_threshold} baselines)**
- If PARTIAL: Detailed failure analysis saved to Serena Memory
- **Mode B Gate evaluated (PASS or PARTIAL)**
- Gate result recorded in checkpoint with per-baseline results

### SYSTEM FAILURE:
- Not updating verification_state.yaml before gate evaluation
- Not checking retry limit (infinite loop risk)
- Not saving to Serena Memory (cross-phase persistence broken)
- **Not computing win/lose for ALL PROCEED baselines**
- **Using wrong threshold (must match checkpoint gate config)**
- **Not evaluating Mode B Gate**
- **On PARTIAL: Not recording which baselines failed**
