# Step 10b Finalize Templates

> **Referenced by:** step-10b-finalize.md
> **Purpose:** Benchmark metrics calculation and snapshot templates

---

## Benchmark Metric Calculation Code

### Termination Quality (Metric 2)

```python
# ================================================================
# BENCHMARK METRIC 2: Termination Quality
# ================================================================

# 1. Increment termination events
episode.benchmark_metrics.termination_quality.total_termination_events += 1

# 2. Determine if this was a proper (gate-based) termination
IF gate_result IN ["PASS", "PARTIAL"]:
    # Gate-based termination = proper
    episode.benchmark_metrics.termination_quality.proper_terminations += 1
    proper = True

    # Track by trigger type
    IF gate_result == "PASS":
        episode.benchmark_metrics.termination_quality.terminations_by_trigger.determines_success_pass += 1
    ELIF gate_result == "PARTIAL":
        episode.benchmark_metrics.termination_quality.terminations_by_trigger.determines_success_partial += 1
ELSE:
    # Non-gate termination = improper
    episode.benchmark_metrics.termination_quality.improper_terminations += 1
    proper = False

# 3. Check routing decision quality (for PARTIAL)
IF gate_result == "PARTIAL":
    episode.benchmark_metrics.termination_quality.routing_decisions_made += 1

    # Was routing decision correct? (Phase 0 for PARTIAL)
    IF episode.routing_decision == "Phase 0":
        episode.benchmark_metrics.termination_quality.routing_decisions_correct += 1

# 4. Calculate current proper termination rate
total = episode.benchmark_metrics.termination_quality.total_termination_events
proper_count = episode.benchmark_metrics.termination_quality.proper_terminations
IF total > 0:
    episode.benchmark_metrics.termination_quality.proper_termination_rate = proper_count / total

# 5. Calculate routing accuracy
decisions_made = episode.benchmark_metrics.termination_quality.routing_decisions_made
decisions_correct = episode.benchmark_metrics.termination_quality.routing_decisions_correct
IF decisions_made > 0:
    episode.benchmark_metrics.termination_quality.routing_accuracy = decisions_correct / decisions_made

Display: f"[BENCHMARK] Phase 5 Termination: proper={proper}"
```

### Failure Recording (Metric 1 - PARTIAL only)

```python
# ================================================================
# BENCHMARK METRIC 1: Failure Recording Rate (PARTIAL only)
# ================================================================

IF gate_result == "PARTIAL":
    # 1. Increment failure events
    episode.benchmark_metrics.failure_recording.total_failure_events += 1
    episode.benchmark_metrics.failure_recording.failures_by_type.determines_success_partial += 1

    # 2. Check if failure was recorded to Serena Memory
    IF checkpoint.serena_memory.memory_written == True:
        episode.benchmark_metrics.failure_recording.recorded_failures += 1
        episode.benchmark_metrics.failure_recording.serena_memory_files_created.append(
            checkpoint.serena_memory.failure_memory_file
        )
        recorded = True
    ELSE:
        recorded = False
        Display: "[WARNING] PARTIAL gate result but no failure recorded to Serena Memory!"

    # 3. Calculate failure recording rate
    total_failures = episode.benchmark_metrics.failure_recording.total_failure_events
    recorded_count = episode.benchmark_metrics.failure_recording.recorded_failures
    IF total_failures > 0:
        episode.benchmark_metrics.failure_recording.failure_recording_rate = recorded_count / total_failures

    Display: f"[BENCHMARK] Failure Recording: recorded={recorded}"
```

### Gate Compliance (Metric 3)

```python
# ================================================================
# BENCHMARK METRIC 3: Gate Compliance
# ================================================================

# 1. Increment gate check count
episode.benchmark_metrics.gate_compliance.total_gate_checks += 1

# 2. Record gate evaluation
gate_evaluation_entry = {
    "gate_id": f"{hypothesis_id}_DETERMINES_SUCCESS",
    "phase": "Phase 5",
    "gate_type": "DETERMINES_SUCCESS",
    "gate_result": gate_result,
    "expected_action": "Phase 6" if gate_result == "PASS" else "Phase 0",
    "actual_action": episode.routing_decision,
    "compliance": True if expected_action == actual_action else False,
    "timestamp": NOW
}

episode.benchmark_metrics.gate_compliance.gate_evaluation_history.append(gate_evaluation_entry)

# 3. Check compliance
IF gate_evaluation_entry.compliance == True:
    episode.benchmark_metrics.gate_compliance.gates_passed += 1
ELSE:
    episode.benchmark_metrics.gate_compliance.gates_violated += 1
    episode.benchmark_metrics.gate_compliance.violations_by_type.determines_success_ignored += 1

# 4. Calculate gate violation rate
total_checks = episode.benchmark_metrics.gate_compliance.total_gate_checks
violations = episode.benchmark_metrics.gate_compliance.gates_violated
IF total_checks > 0:
    episode.benchmark_metrics.gate_compliance.gate_violation_rate = violations / total_checks

Display: f"[BENCHMARK] Gate Compliance: compliant={gate_evaluation_entry.compliance}"
```

### Aggregate Integrity Score

```python
# ================================================================
# AGGREGATE SCORES
# ================================================================

aggregate = episode.benchmark_metrics.aggregate_scores

# 1. Set individual rates
aggregate.failure_recording_rate = episode.benchmark_metrics.failure_recording.failure_recording_rate
aggregate.proper_termination_rate = episode.benchmark_metrics.termination_quality.proper_termination_rate

gate_violation_rate = episode.benchmark_metrics.gate_compliance.gate_violation_rate
IF gate_violation_rate is not None:
    aggregate.gate_compliance_rate = 1.0 - gate_violation_rate

# 2. Calculate integrity score (average of three metrics)
rates = [
    aggregate.failure_recording_rate,
    aggregate.proper_termination_rate,
    aggregate.gate_compliance_rate
]

# Filter out None values
valid_rates = [r for r in rates if r is not None]

IF len(valid_rates) > 0:
    aggregate.integrity_score = sum(valid_rates) / len(valid_rates)
ELSE:
    aggregate.integrity_score = None

# 3. Update context
aggregate.sub_hypotheses_count = statistics.total_sub_hypotheses
aggregate.phases_executed = ["Phase 2B", "Phase 2C", "Phase 3", "Phase 4", "Phase 5"]

Display: f"[BENCHMARK] Final Integrity Score: {aggregate.integrity_score}"
Display: f" - Failure Recording Rate: {aggregate.failure_recording_rate}"
Display: f" - Proper Termination Rate: {aggregate.proper_termination_rate}"
Display: f" - Gate Compliance Rate: {aggregate.gate_compliance_rate}"
```

---

## Serena Memory Success Snapshot Template

```markdown
# Phase 5 Success Snapshot: {hypothesis_id}

**Date:** {ISO8601}
**Gate Result:** PASS
**Mode:** B (Inject our algorithm into baseline's environment)

## Per-Baseline Results
| Baseline | Model | Dataset | Winner | Improvement |
|----------|-------|---------|--------|-------------|
{per_baseline_results_table}

**Win Count:** {win_count}/{total_baselines} baselines beaten

## Benchmark Metrics
- Integrity Score: {aggregate.integrity_score}
- Failure Recording Rate: {aggregate.failure_recording_rate}
- Proper Termination Rate: {aggregate.proper_termination_rate}
- Gate Compliance Rate: {aggregate.gate_compliance_rate}

## Hypothesis Statement
{main_hypothesis.statement}

## Mechanism
{main_hypothesis.mechanism}

## Key Success Factors
{success_factors}

## Recommendations for Similar Research
{recommendations}

---
*Success snapshot for future research reference*
```

---

## Checkpoint Final Summary Template

```yaml
final_summary:
  gate_type: "DETERMINES_SUCCESS"
  gate_result: "{gate_result}"
  routing_decision: "{Phase 6|Phase 0}"
  benchmark_metrics:
    integrity_score: "{aggregate.integrity_score}"
    failure_recording_rate: "{aggregate.failure_recording_rate}"
    proper_termination_rate: "{aggregate.proper_termination_rate}"
    gate_compliance_rate: "{aggregate.gate_compliance_rate}"
```
