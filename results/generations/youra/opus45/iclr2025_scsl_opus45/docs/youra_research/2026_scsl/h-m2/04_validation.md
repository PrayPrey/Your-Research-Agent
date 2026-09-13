# Phase 4 Validation Report: h-m2

**Generated:** 2026-04-14T11:05:00Z
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-m2 |
| **Title** | Spurious-Specificity Mechanism Test via GroupDRO Attenuation |
| **Type** | MECHANISM |
| **Statement** | If trajectory divergence reflects spurious-feature conflict specifically, then AUROC will attenuate >0.10 under GroupDRO training but <0.05 under variance-matched random reweighting, because GroupDRO targets spurious reliance while random reweighting only smooths gradients generically. |
| **Phase 4 Start** | 2026-04-14T10:24:00Z |
| **Phase 4 End** | 2026-04-14T11:05:00Z |
| **Duration** | ~41 minutes |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 23 |
| Completed | 23 |
| Failed | 0 |
| Skipped | 0 |
| Coder-Validator Cycles | 1/5 |

### Generated Files

| File | Purpose | Status |
|------|---------|--------|
| config.py | Extended H-E1 config with GroupDRO/regime params | Done |
| data.py | Data loading with get_group_counts() | Done |
| model.py | ResNet-50 model (copied from H-E1) | Done |
| trainers.py | ERM, GroupDRO, Random Reweighting trainers | Done |
| evaluate.py | Multi-regime evaluation, AUROC, visualization | Done |
| run.py | Orchestrator for 3-regime experiment | Done |

### Task Completion Summary

- **D-1**: Verify Waterbirds Dataset Cache - Done
- **E-1**: Setup Environment and Dependencies - Done
- **A-1**: Setup & Config Module - Done
- **A-2**: ERM Trainer Implementation - Done
- **A-3**: GroupDRO Trainer Implementation - Done
- **A-3-1 to A-3-4**: GroupDRO subtasks - Done
- **A-4**: Random Reweighting Implementation - Done
- **A-4-1, A-4-2**: Random Reweighting subtasks - Done
- **A-5**: Multi-Regime Evaluator - Done
- **A-5-1, A-5-2**: Evaluator subtasks - Done
- **A-6**: Visualization Module - Done
- **A-6-1**: Gate Metrics and AUROC Comparison Plots - Done
- **A-7**: Orchestrator Implementation - Done
- **A-7-1, A-7-2**: Orchestrator subtasks - Done
- **A-8**: Integration & Gate Evaluation - Done
- **A-8-1**: Verification State Update - Done
- **F-1**: Pipeline Continuation Checkpoint - Done

---

## Code Quality Checklist

Based on Validator Agent evaluation:

- [x] Syntax validation passed
- [x] Type hints compliance
- [x] API signatures match 03_logic.md
- [x] Configuration schema match 03_config.md
- [x] Cross-file dependencies resolved
- [x] No obvious anti-patterns

### Issues Detected

No issues detected - all quality checks passed.

---

## Experiment Results

### Execution Details

| Field | Value |
|-------|-------|
| **Mode** | Full Execution (3 seeds × 3 regimes × 20 epochs) |
| **Status** | Completed |
| **Duration** | ~30 minutes |
| **GPU** | NVIDIA H100 NVL (GPU 1) |

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Epochs | 20 |
| Batch Size | 128 |
| Learning Rate | 0.001 |
| Seeds | 42, 43, 44 |
| Regimes | ERM, GroupDRO, Random Reweighting |
| GroupDRO Gamma | 0.1 |
| Weight Decay (ERM) | 0.0001 |
| Weight Decay (GroupDRO) | 1.0 |

### Primary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AUROC (ERM) | 0.9436 ± 0.0123 | Baseline | - |
| AUROC (GroupDRO) | 0.6513 ± 0.0390 | - | - |
| AUROC (Random) | 0.9336 ± 0.0244 | - | - |
| **ΔAUROC (GroupDRO)** | **0.2923** | **> 0.10** | **PASS** |
| **ΔAUROC (Random)** | **0.0100** | **< 0.05** | **PASS** |

### Mechanism Verification

| Check | Result |
|-------|--------|
| GroupDRO weights diverged from uniform | Yes |
| Variance matching verified | Yes |
| GroupDRO grad variance | 0.015 |
| Random grad variance | 0.014 |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | SHOULD_WORK |
| **Result** | **PASS** |
| **Satisfied** | Yes |
| **Evaluated At** | 2026-04-14T11:05:00Z |

### Criteria Evaluation

| Criterion | Target | Actual | Result |
|-----------|--------|--------|--------|
| ΔAUROC_GroupDRO > 0.10 | > 0.10 | 0.2923 | **PASS** |
| ΔAUROC_Random < 0.05 | < 0.05 | 0.0100 | **PASS** |

### Interpretation

The experiment strongly supports the hypothesis:

1. **GroupDRO significantly attenuates trajectory divergence (Δ=0.29)**: Under GroupDRO training, the AUROC for trajectory-based minority detection drops from 0.94 to 0.65. This ~29 percentage point reduction (well above the 10% threshold) indicates that GroupDRO specifically reduces the trajectory patterns that distinguish minority samples.

2. **Random reweighting has minimal effect (Δ=0.01)**: Under variance-matched random reweighting, AUROC only drops from 0.94 to 0.93. This 1 percentage point reduction (well below the 5% threshold) shows that generic gradient smoothing does not eliminate the trajectory divergence.

3. **Conclusion**: The asymmetric response to GroupDRO vs. random reweighting provides strong evidence that trajectory divergence reflects spurious-feature conflict specifically, not generic sample hardness. GroupDRO targets and reduces spurious reliance, hence the large attenuation. Random reweighting only smooths gradients generically without addressing the underlying cause.

---

## Next Steps

### PASS - Ready for Phase 5

All validation criteria met. The hypothesis implementation is complete and ready for:

1. Phase 5 baseline comparison (if applicable)
2. Integration with main hypothesis validation
3. Documentation for Phase 6 paper writing

**Proceed to:** Phase 5 workflow or next hypothesis in loop

---

## Phase 2C Handoff

> **Purpose:** This section is designed for Phase 2C to consume when processing dependent hypotheses.

### Source Information

| Field | Value |
|-------|-------|
| **Source Hypothesis** | h-m2 |
| **Generated At** | 2026-04-14T11:05:00Z |
| **Gate Result** | PASS |
| **Ready for Dependents** | Yes |

### Proven Components

Components that were successfully implemented and validated:

| Component | File | Type | Evidence | Reusable |
|-----------|------|------|----------|----------|
| GroupDRO Trainer | trainers.py | Training Loop | AUROC attenuation verified | Yes |
| Random Reweighting | trainers.py | Training Loop | Variance matching verified | Yes |
| Multi-Regime Evaluator | evaluate.py | Evaluation | 3-regime comparison | Yes |
| Trajectory Feature Extraction | evaluate.py | Feature Engineering | Reused from H-E1 | Yes |

### Optimal Hyperparameters

Final hyperparameters that achieved the reported metrics:

```yaml
# Copy-paste ready for dependent hypotheses
training:
  learning_rate: 0.001
  batch_size: 128
  epochs: 20
  optimizer: SGD
  momentum: 0.9

groupdro:
  gamma: 0.1
  weight_decay: 1.0

erm:
  weight_decay: 0.0001

random_reweighting:
  variance_matched: true

# Metrics achieved with these parameters
achieved_metrics:
  auroc_erm: 0.9436
  auroc_groupdro: 0.6513
  auroc_random: 0.9336
  delta_gdro: 0.2923
  delta_random: 0.0100
```

### Lessons Learned

#### What Worked Well
- GroupDRO implementation based on official kohpangwei/group_DRO repository
- Exponentiated gradient weight updates for group rebalancing
- Variance matching for random reweighting control
- Trajectory feature extraction pipeline from H-E1

#### What Didn't Work
- Initial JSON serialization issue with numpy bools (fixed with explicit bool() casting)

#### Unexpected Findings
- GroupDRO attenuation (0.29) was nearly 3x the threshold (0.10), indicating very strong spurious-specificity
- Random reweighting attenuation (0.01) was 5x below threshold (0.05), confirming it's truly a null control

#### Key Insight
> The large differential response to GroupDRO vs. random reweighting (0.29 vs 0.01) provides compelling evidence that trajectory divergence is a specific signature of spurious feature reliance, not a generic property of difficult samples. This validates the core premise that loss trajectories can serve as a diagnostic tool for spurious correlations.

### Recommendations for Dependent Hypotheses

**Dependent Hypotheses:** h-m3 (may use trajectory infrastructure)

#### General Recommendations
- Reuse the validated trajectory extraction pipeline
- GroupDRO implementation is production-ready
- Consider using variance-matched controls for other mechanism tests

#### Warnings (What to Avoid)
- Ensure numpy types are converted to Python natives before JSON serialization
- GroupDRO requires group labels - ensure dataset provides them

---

## Appendix

### Files Reference

| File | Purpose |
|------|---------|
| `04_checkpoint.yaml` | Recovery checkpoint |
| `04_validation.md` | This report |
| `experiment_results.json` | Raw experiment data |
| `code/` | Generated implementation |
| `verification_state.yaml` | Updated gate status |

### Checkpoint Summary

```yaml
version: "3.5"
hypothesis_id: "h-m2"
created_at: "2026-04-14T10:24:00Z"
completed_at: "2026-04-14T11:05:00Z"
tasks:
  total: 23
  completed: 23
coder_validator_cycles: 1
unattended_mode: true
```

### Environment

| Item | Value |
|------|-------|
| Execution Date | 2026-04-14 |
| Mode | UNATTENDED |
| Conda Environment | youra-h-m2 |
| GPU | NVIDIA H100 NVL |
| Duration | ~41 minutes |

---

*Report generated by Phase 4 Implementation & Validation Workflow*
*Anonymous Research Pipeline - Phase 4*
