# State Update Template for H-E1

This template will be filled once experiments complete.

## Fields to Update in verification_state.yaml

### Hypothesis h-e1 Updates
```yaml
validation:
  status: COMPLETED  # or FAILED if experiments crashed
  result: [PASS/PARTIAL/FAIL]  # Based on statistical analysis
  report_file: "outputs/h-e1/04_validation.md"
  test_wg_acc_coloredmnist: [mean_joint_score]
  test_wg_acc_celeba: null  # Not tested
  statistical_significance: [true/false]
  ci_non_overlapping: [true/false]
  completed_at: [timestamp]

gate:
  satisfied: [true/false/null]  # true=PASS, false=FAIL, null=PARTIAL

completed: [true if validation done, false otherwise]
completed_at: [timestamp if completed]
```

### Checkpoint (04_checkpoint.yaml) Updates
```yaml
current_step: "Step 09 (Phase 4 Complete)"
phase_4_complete: true
phase_4_status: COMPLETED
deliverables_complete:
  - 04_validation.md (generated from statistical analysis)
  - results.csv (15 runs completed)
final_validation_timestamp: [timestamp]
gate_result: [PASS/PARTIAL/FAIL]
next_action: [depends on gate result]
next_phase: [Phase 4.5 or Phase 5, or route back based on gate]
```

## Gate Decision Logic

### PASS (gate.satisfied = true)
- Joint SAM+SWA > max(SAM, SWA) + 0.5% on BOTH datasets
- p < 0.0125 AND CIs non-overlapping on BOTH datasets
- **Action**: Proceed to H-M1 (mechanism hypotheses)
- **Note**: Requires BOTH ColoredMNIST AND CelebA results

### PARTIAL (gate.satisfied = null)
- Gains on ColoredMNIST only (CelebA not tested or failed)
- **Action**: Route to Phase 2A-Dialogue for hypothesis refinement
- **Alternative**: Extend experiments to CelebA to attempt PASS

### FAIL (gate.satisfied = false)
- No statistically significant gains on either dataset
- **Action**: Route to Phase 0 for fundamental approach revision

## Current Expected Outcome

Given current experiment design:
- Testing ColoredMNIST only (CelebA deferred)
- **Best possible outcome**: PARTIAL
- **Recommendation if PARTIAL**: Extend to CelebA for full PASS attempt
