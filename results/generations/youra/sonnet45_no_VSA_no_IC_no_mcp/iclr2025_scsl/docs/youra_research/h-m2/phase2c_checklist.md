# Phase 2C Completion Checklist: h-m2

**Hypothesis**: Attention Correction Mechanism  
**Completed**: 2026-08-25  
**Status**: READY FOR PHASE 3

---

## Required Outputs ✓

- [x] **02c_experiment_brief.md** — Full experiment specification (280 lines)
  - Dataset: Waterbirds (standard, real data, reuse from h-e1)
  - Architectures: ResNet-18-BN (control), ResNet-18-CBAM (ablation), ViT-Small (global attention)
  - Training config: 10 seeds, 100 epochs, controlled variables
  - Evaluation: Slope comparison (epochs 20-50), bootstrap CI, Cohen's d
  - Success criterion: Slope difference ≥0.3pp/epoch, non-overlapping CIs, d≥0.8

- [x] **hypothesis_summary.md** — One-page overview
  - Statement, motivation, prerequisites (h-e1 validated ✓)
  - Success/falsification criteria
  - Dependencies (SHOULD_WORK gate, does not block Phase 5)
  - Next phase actions

- [x] **implementation_requirements.md** — Module breakdown
  - 5 modules: data (reuse), models (CBAM+ViT), train, eval, viz
  - Acceptance criteria (functional, scientific, quality)
  - Runtime estimates (~33 hours GPU, 18-30 hours if parallel)
  - File structure and dependencies

- [x] **research_context.md** — Research lineage
  - Hypothesis lineage (main → h-e1 → h-m2)
  - Research trajectory (Phase 0 → 2C)
  - Controlled variables and design decisions
  - Risks and contingencies (ViT instability, CBAM validation, epoch window)

- [x] **phase2c_checklist.md** — This file

---

## Design Quality Checks ✓

### Scientific Rigor
- [x] Hypothesis is falsifiable (clear CI non-overlap threshold, slope difference, effect size)
- [x] Sample size is statistically meaningful (600 test samples × 100 epochs × 10 seeds)
- [x] Controlled variables documented and justified (same as h-e1: LR, batch size, seeds)
- [x] Success criterion includes effect size (Cohen's d≥0.8), not just CI non-overlap
- [x] Fallback plan for edge cases (ViT instability → gradient clipping / LR reduction)
- [x] Confound acknowledged (ViT global architecture vs attention isolated via CBAM ablation)

### Dataset Quality
- [x] Dataset is real (Waterbirds benchmark), not synthetic
- [x] Dataset has established spurious correlation (95% co-occurrence)
- [x] Dataset has group labels (4 groups for worst-group accuracy)
- [x] Dataset is publicly available (wilds library)
- [x] Sample size is not trivially small (600 test samples, 4800 train samples)

### Experimental Design
- [x] Analysis window justified (epochs 20-50: mid-training correction phase)
- [x] Slope comparison is appropriate metric (measures gap reduction rate over time)
- [x] Bootstrap CI provides robust uncertainty estimate (1000 resamples)
- [x] Ablation isolates attention effect (CBAM preserves local architecture)
- [x] Multiple seeds for statistical power (10 seeds)
- [x] Evaluation metric matches hypothesis claim (slope difference ≥0.3pp/epoch)

### Implementation Feasibility
- [x] Complexity tier justified (Tier 1: standard ViT from timm, CBAM ~50 lines)
- [x] Dependencies are standard (torch, timm, wilds, scipy)
- [x] Runtime is reasonable (~33 hours GPU for 3 arch × 10 seeds × 100 epochs)
- [x] Module breakdown is complete (data, models, train, eval, viz)
- [x] Acceptance criteria are testable
- [x] CBAM validation plan (test on CIFAR-10 first)

---

## Phase 2C Workflow Steps ✓

- [x] **Step 01**: Search Archon KB for past experiment cases (MCP unavailable, used general knowledge)
- [x] **Step 02**: Search Exa for implementation code examples (MCP unavailable, used general knowledge)
- [x] **Step 03**: Analyze codebase with Serena (MCP unavailable, skipped)
- [x] **Step 04**: Extract hypothesis statement and type from pipeline state
- [x] **Step 05**: Extract controlled variables from Phase 2B plan
- [x] **Step 06**: Design dataset preparation (Waterbirds via wilds, reuse h-e1)
- [x] **Step 07**: Design baseline experiments (ResNet-BN/CBAM/ViT, slope comparison)
- [x] **Step 08**: Synthesize experiment specification (02c_experiment_brief.md)
- [x] **Step 09**: Create h-m2 output folder with complete documentation

---

## Validation Against Common Pitfalls ✓

### Synthetic Data Pitfall
- [x] Dataset type confirmed: **standard** (Waterbirds benchmark)
- [x] NOT synthetic or simulated
- [x] Real images with natural feature complexity

### Trivial Sample Size Pitfall
- [x] Test set size: 600 samples (NOT 10-50)
- [x] Statistical power: 10 seeds × 31-epoch window provides robust slope estimation
- [x] Full dataset used (not arbitrary subset)

### Confound Pitfall
- [x] ViT confound acknowledged (global architecture + attention)
- [x] CBAM ablation isolates attention (preserves local ResNet architecture)
- [x] Learning rate schedule confound eliminated (constant LR)
- [x] Training speed confound irrelevant (slope comparison, not convergence time)

### Unfalsifiable Hypothesis Pitfall
- [x] Clear falsification criterion: CI overlap OR slope difference <0.2pp/epoch OR d<0.5
- [x] Effect size threshold (Cohen's d≥0.8), not just CI non-overlap
- [x] Interpretation matrix for partial success (ViT succeeds, CBAM fails)

### Epoch Window Pitfall
- [x] Analysis window justified (epochs 20-50: mid-training phase)
- [x] Contingency plan: test alternative windows if correction occurs elsewhere
- [x] Full trajectory visualization (epochs 0-100) for sanity check

---

## Blockers and Risks

### No Blockers
- Prerequisites: h-e1 validated ✓ (gap difference 9.41pp, p=5.43e-05)
- MCP dependencies: None required (Archon/Exa/Serena search skipped, used domain knowledge)
- Data availability: Waterbirds available via wilds (reuse h-e1 loader)

### Risks Documented
- **Risk 1**: ViT training instability → Mitigation: gradient clipping, LR=0.001 for ViT
- **Risk 2**: CBAM implementation bug → Mitigation: validate on CIFAR-10 first
- **Risk 3**: Epoch 20-50 misses correction phase → Mitigation: plot full trajectories, test alternative windows
- **Risk 4**: High variance across seeds → Mitigation: 10 seeds provides 80% power; add 5 more if needed
- **Risk 5**: Null result → Scientific action: Document (publishable), does NOT block Phase 5 (SHOULD_WORK)

---

## Pipeline State Update ✓

```state
sub_hypotheses:
  h-m2:
    experiment_design:
      status: COMPLETED
      file: docs/youra_research/h-m2/02c_experiment_brief.md
```

Updated fields:
- `experiment_design.status`: NOT_STARTED → COMPLETED
- `experiment_design.file`: null → docs/youra_research/h-m2/02c_experiment_brief.md

---

## Comparison with h-e1 (Consistency Check) ✓

| Aspect | h-e1 | h-m2 | Consistent? |
|--------|------|------|-------------|
| Dataset | Waterbirds | Waterbirds | ✓ |
| Learning Rate | 0.01 (constant) | 0.01 (constant) | ✓ |
| Batch Size | 64 | 64 | ✓ |
| Seeds | 10 (0-9) | 10 (0-9) | ✓ |
| Epochs | 100 | 100 | ✓ |
| Optimizer | SGD (momentum=0.9, wd=1e-4) | SGD (momentum=0.9, wd=1e-4) | ✓ |
| Loss | CrossEntropyLoss | CrossEntropyLoss | ✓ |
| Data Augmentation | None | None | ✓ |
| Statistical Test | Paired t-test, Cohen's d | Bootstrap CI, Cohen's d | ✓ (different metrics, same rigor) |
| Effect Size Threshold | d≥0.8 | d≥0.8 | ✓ |

All controlled variables consistent across h-e1 and h-m2 ✓

---

## Next Phase Handoff

### Phase 3 Input Requirements
Phase 3 (Implementation Planning) requires:
- [x] Experiment brief (02c_experiment_brief.md) ✓
- [x] Hypothesis statement ✓
- [x] Success criteria ✓
- [x] Module breakdown ✓
- [x] Complexity tier estimate (Tier 1) ✓

### Phase 3 Expected Outputs
Phase 3 will generate:
- PRD (Product Requirements Document)
- Architecture document (detailed module design: data, models, CBAM, train, eval)
- Logic document (CBAM attention mechanism, slope computation algorithm)
- Config document (hyperparameters, model configs, epoch window)
- Archon task breakdown (Epic → subtasks)
- Implementation budget estimate (400-500 LoC, 33 hours GPU)

### Archon Project Link
- Archon Task ID: 477802a1-5780-457f-9d7b-a6cf7081730f
- Pipeline Project ID: e434b9c6-e150-46c4-8cb5-1c8e857b014c
- Prerequisite: h-e1 (Archon Task ID: c4f70e7d-cb8d-476c-9f74-91c168c072b0) ✓ VALIDATED

---

## Novel Aspects (vs h-e1)

h-m2 introduces:
1. **CBAM attention module** (~50 lines, channel + spatial attention)
2. **ViT integration** (timm library, global self-attention)
3. **Slope-based analysis** (linear regression over epochs 20-50, not single-point comparison)
4. **Bootstrap confidence intervals** (robust uncertainty estimation)
5. **Ablation design** (CBAM isolates attention, ViT tests global architecture)

These are incremental over h-e1, maintaining Tier 1 complexity.

---

## Sign-off

**Phase 2C Status**: COMPLETED  
**All required outputs**: PRESENT  
**Quality checks**: PASSED  
**Blockers**: NONE  
**Ready for Phase 3**: YES (h-e1 prerequisite validated)

**Completed by**: Claude (Sonnet 4.5)  
**Completion time**: 2026-08-25  
**Mode**: UNATTENDED (batch mode)
