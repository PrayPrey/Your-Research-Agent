# Step 1 Initialization Templates

> **Referenced by:** step-01-init.md
> **Purpose:** YAML templates for checkpoint and verification_state initialization

---

## Checkpoint Template (05_baseline_checkpoint.yaml)

> **⚠️ IMPORTANT:** Use the full template file for checkpoint creation:
>
> **Template File:** `{workflow_path}/templates/05_baseline_checkpoint_template.yaml`
>
> The template file contains the complete Multi-Baseline × Multi-Dataset structure.
> Do NOT use an inline version here - always reference the authoritative template file.

### Key Features:
- **Template-First Execution Pattern** (matching Phase 4's approach)
- Multi-baseline support (N baselines, from workflow.yaml)
- **Mode B:** Inject OUR algorithm into BASELINE's environment
- Each baseline uses THEIR OWN model, dataset, config
- Gate criteria: Win ≥{baseline_win_threshold} baselines (ours > baseline on their turf)
- Total runs: {total_runs} = {baselines} Baselines × {methods_per_baseline} Methods × {seeds} Seed
- Per-baseline `injection_analysis` for algorithm injection points
- Per-baseline `baseline_environment` for model/dataset/config
- Comprehensive failure_analysis section
- Serena memory integration
- Figure tracking

### Placeholder Syntax:

> for consistency with Phase 4's template handling.

When creating the checkpoint, the `fill_placeholders()` function substitutes these:

| Placeholder | Description | Example Value |
|-------------|-------------|---------------|
| `{{hypothesis_id}}` | Current hypothesis ID | "h-main" |
| `{{main_hypothesis_id}}` | Main hypothesis ID from verification_state | "h-main" |
| `{{timestamp}}` | Current ISO8601 timestamp | "2026-01-13T23:00:00Z" |
| `{{hypothesis_folder}}` | Path to hypothesis folder | "/research/h-main" |
| `{{baseline_folder}}` | Path to baseline comparison folder | "/research/h-main/baseline_comparison" |
| `{{pipeline_project_id}}` | Archon Pipeline Project UUID | "uuid-..." |
| `{{conda_path}}` | Conda installation path | "/home/anonymous/miniforge3" |

---

## Verification State Updates

### main_hypothesis.baseline_comparison

```yaml
baseline_comparison:
  status: "IN_PROGRESS"
  started_at: "{current_timestamp}"
  mode: "B"
  gate:
    type: "DETERMINES_SUCCESS"
    criteria: "win ≥{baseline_win_threshold} baselines (ours > baseline on their turf)"
    satisfied: null
    result: null
  baselines: [] # Will be populated with selected baseline repos
  per_baseline_results: [] # From gate evaluation (per-baseline win/lose details)
  aggregate_results:
    baselines_won: null
    threshold_met: null
  failure_context:
    failure_type: null
    gap_percentage: null
    root_causes: []
    lessons_learned: []
    serena_memory_file: null
  report_file: null
```

### episode Section

```yaml
episode:
  status: "ACTIVE"
  terminated_properly: false
  termination_trigger: null
  final_gate:
    type: null
    result: null
    phase: null
  routing_decision: null
  routing_reason: null
  benchmark_metrics:
    total_sub_hypotheses: {statistics.total_sub_hypotheses}
    validated_sub_hypotheses: {statistics.validated_sub_hypotheses}
    failed_sub_hypotheses: {statistics.failed_sub_hypotheses}
    gate_violations_count: {len(gate_violations)}
    proper_termination: false
    failure_recorded: false
```

### workflow Section

```yaml
workflow:
  current_phase: "Phase 5"
  next_action: "Execute baseline comparison (Step 2-10)"
```

### history Entry

```yaml
- event: "Phase 5 baseline comparison started"
  timestamp: "{current_timestamp}"
  phase: "Phase 5"
  details: "All {total_sub_hypotheses} sub-hypotheses validated, starting DETERMINES_SUCCESS gate"
```

---

## Journey Summary Output Format

```
======================================================================
HYPOTHESIS JOURNEY SUMMARY
======================================================================
Hypothesis: {hypothesis_id}
Type: {type}
Statement: {first 80 chars of statement}...

Current Version: v{version}
Modification Attempts: {modification_attempt}

----------------------------------------------------------------------
VERSION HISTORY
----------------------------------------------------------------------
v1: [Result] - {key_findings summary}
    → Modified to: {next version}
v2: [Result] - {key_findings summary}
...

----------------------------------------------------------------------
FINAL RESULT
----------------------------------------------------------------------
Result: {PASS/PARTIAL/FAIL}
Gate: {gate.type} - {satisfied ? "Satisfied" : "Not Satisfied"}
Key Findings:
  - {finding 1}
  - {finding 2}
  ...

----------------------------------------------------------------------
IMPLICATIONS FOR BASELINE COMPARISON
----------------------------------------------------------------------
{Baseline comparison strategy based on result}
======================================================================
```
