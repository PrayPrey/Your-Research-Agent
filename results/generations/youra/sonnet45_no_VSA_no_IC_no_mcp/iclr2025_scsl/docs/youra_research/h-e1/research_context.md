# Research Context: h-e1

**Hypothesis ID**: h-e1  
**Main Hypothesis**: H-TemporalArchSig-v1  
**Phase**: 2C (Experiment Design) COMPLETED  
**Generated**: 2026-08-24

---

## Hypothesis Lineage

### Main Hypothesis (Phase 2A)
**Title**: Architectural Components as Temporal Filters in Spurious Correlation Learning

**Core Claim**: Neural network architectures with different normalization (BN vs LN) and attention mechanisms (ResNet-CBAM, ViT) produce DISTINCT worst-group accuracy gap trajectories when plotted against training progress (average accuracy on x-axis) under stochastic spurious correlations.

**Causal Mechanism**:
1. BN amplifies early spurious learning via batch-level statistics
2. LN reduces early spurious amplification via instance-level normalization
3. Attention mechanisms enable mid-training correction via global feature aggregation

---

### Sub-Hypothesis Breakdown (Phase 2B)

**h-e1** (EXISTENCE, MUST_WORK):
- Tests whether BN-LN gap difference exists (≥5pp at 90% accuracy)
- Foundation hypothesis — blocks Phase 5 if fails
- Ready for immediate execution (no prerequisites)

**h-m1** (MECHANISM, SHOULD_WORK):
- Tests whether BN amplifies early spurious learning via batch-level statistics
- Prerequisites: h-e1 (depends on existence being confirmed)
- Blocked until h-e1 completes Phase 4

**h-m2** (MECHANISM, SHOULD_WORK):
- Tests whether attention enables mid-training correction (steeper gap reduction)
- Prerequisites: h-e1 (depends on existence being confirmed)
- Blocked until h-e1 completes Phase 4

**h-c1** (CONDITION, SHOULD_WORK):
- Tests whether signatures generalize across datasets (Waterbirds → CelebA)
- Prerequisites: h-e1 (depends on existence being confirmed)
- Blocked until h-e1 completes Phase 4

---

## Research Trajectory

### Phase 0: Brainstorming
**Output**: `00_brainstorm_session.md`  
**Key Insight**: Temporal perspective (gap vs training progress) more informative than static convergence comparison

### Phase 1: Targeted Research
**Output**: `01_targeted_research.md`, `01_round_table/`  
**Key Papers**:
- Sagawa et al. 2020 (Waterbirds dataset, Group DRO baseline)
- Santurkar et al. 2018 (BN changes loss landscape)
- Nam et al. 2020 (LfF learns last bias frame)

**Key Findings**:
- Waterbirds: 95% spurious correlation (waterbird-water, landbird-land)
- BN creates batch-level statistics that can amplify spurious features
- No prior work on BN vs LN temporal gap trajectories

### Phase 2A: Hypothesis Synthesis
**Output**: `02_synthesis.yaml`  
**Refinement**: Added accuracy-matched comparison to eliminate LR schedule confound

### Phase 2A Extended: Dialectical Refinement
**Output**: `03_refinement.md`, `03_refinement.yaml`  
**Key Decisions**:
- Constant LR (no schedule) to isolate architectural effects
- 10 seeds for statistical power (2pp detectable effect)
- ResNet-CBAM ablation to isolate attention effect from ViT global architecture

### Phase 2B: Verification Planning
**Output**: `02b_verification_plan.md`  
**Breakdown**: 4 sub-hypotheses (1 MUST_WORK, 3 SHOULD_WORK) with DAG dependencies

### Phase 2C: Experiment Design (h-e1)
**Output**: `h-e1/02c_experiment_brief.md`  
**Design**:
- Dataset: Waterbirds (standard benchmark, real data)
- Architectures: ResNet-18-BN vs ResNet-18-LN
- Training: 10 seeds, 100 epochs, constant LR=0.01
- Evaluation: Paired t-test of gaps at 90% average accuracy
- Success: ≥5pp gap difference, p<0.05, Cohen's d≥0.8

---

## Controlled Variables (All h-e1 Experiments)

From Phase 2B verification plan, these are held constant:
- **Learning Rate**: 0.01 (constant, no schedule)
- **Batch Size**: 64
- **Optimizer**: SGD (momentum=0.9, weight_decay=1e-4)
- **Initialization**: He normal (kaiming_normal)
- **Random Seeds**: 10 (seeds 0-9)
- **Dataset**: Waterbirds (no augmentation)
- **Epochs**: 100
- **Loss**: CrossEntropyLoss (no class weighting)

**Rationale**: Isolate architectural effects from optimization dynamics.

---

## Key Design Decisions (Phase 2C)

### Decision 1: Accuracy-Matched Comparison
**Problem**: BN might train faster than LN, creating spurious gap difference  
**Solution**: Compare gaps at the SAME average accuracy (90%), not same epoch  
**Benefit**: Eliminates training speed confound

### Decision 2: Real Dataset (Waterbirds)
**Alternative**: Synthetic dataset with controlled spurious correlation  
**Choice**: Waterbirds (standard benchmark)  
**Rationale**: 
- Synthetic data produces meaningless results (trivial runtime, simulated metrics)
- Waterbirds is established benchmark with known spurious structure
- Real images have natural feature complexity

### Decision 3: No Data Augmentation
**Problem**: Augmentation interacts with normalization (BN sees augmented batch stats)  
**Solution**: No augmentation in train or test  
**Trade-off**: Lower absolute accuracy, but cleaner architectural comparison

### Decision 4: 10 Seeds (Not 3 or 5)
**Power Analysis**: 
- 3 seeds: 80% power for 4pp effect
- 5 seeds: 80% power for 3pp effect
- 10 seeds: 80% power for 2pp effect
**Choice**: 10 seeds  
**Benefit**: Can detect smaller effects, higher confidence in null result

### Decision 5: Tier 1 Complexity
**Assessment**: Simple experiment (standard dataset, one BN→LN change)  
**Estimated LoC**: 300-400 lines  
**Archon Budget**: Low (4 Epic tasks, ~8-10 subtasks)

---

## Risks and Contingencies

### Risk 1: 90% Accuracy Never Reached
**Probability**: Medium (LN might converge slower)  
**Impact**: High (cannot measure gap at target accuracy)  
**Mitigation**: Fallback to epoch 80 or best average accuracy achieved  
**Fallback Success Criterion**: Adjust to "gap at 85% accuracy" if 90% unreachable

### Risk 2: High Variance Across Seeds
**Probability**: Low (Waterbirds is stable dataset)  
**Impact**: Medium (false negative if variance >> effect size)  
**Mitigation**: 10 seeds provide 80% power for 2pp effect  
**Contingency**: Add 5 more seeds (15 total) if initial variance is high

### Risk 3: LN Convergence Instability
**Probability**: Low (LN generally stable)  
**Impact**: Medium (LN fails to train, experiment invalid)  
**Detection**: Monitor training loss curves  
**Mitigation**: Add gradient clipping (max_norm=1.0) if gradients explode

### Risk 4: Null Result (Gap Difference < 3pp)
**Probability**: Medium (BN effect might be weak on Waterbirds)  
**Impact**: High (MUST_WORK hypothesis fails, blocks Phase 5)  
**Scientific Action**: ROUTE to Phase 0, test alternative hypotheses:
  - Test on CelebA (higher spurious correlation 95% vs 85%)
  - Test with LR schedule (does constant LR suppress BN effect?)
  - Measure gap earlier (epoch 20-40 instead of 90% accuracy)

---

## Success Metrics

### Phase 2C Success (Current Phase)
- [x] Experiment brief written (02c_experiment_brief.md)
- [x] Dataset is real (Waterbirds, not synthetic)
- [x] Sample size is meaningful (600 test samples)
- [x] Success criterion is falsifiable (p<0.05, gap≥5pp, d≥0.8)
- [x] Controlled variables documented
- [x] Implementation requirements specified

### Phase 3 Success (Next Phase)
- [ ] Archon project initialized
- [ ] PRD generated (user story, acceptance criteria)
- [ ] Architecture document (4 modules: data, model, train, eval)
- [ ] Epic-level tasks created (~4 Epics, 8-10 subtasks)
- [ ] Complexity tier confirmed (Tier 1)

### Phase 4 Success (PoC Validation)
- [ ] All 10 seeds complete for both architectures
- [ ] Paired t-test produces p-value
- [ ] Validation report (04_validation.md) generated
- [ ] MUST_WORK gate evaluation triggered

### Phase 5 Readiness
- [ ] If h-e1 gate satisfied → unblock h-m1, h-m2, h-c1
- [ ] If h-e1 gate failed → ROUTE to Phase 0

---

## Related Documents

### Phase 2B Outputs
- `../02b_verification_plan.md` — Sub-hypothesis breakdown, DAG, timeline

### Phase 2C Outputs (h-e1)
- `02c_experiment_brief.md` — Full experiment specification
- `hypothesis_summary.md` — One-page hypothesis overview
- `implementation_requirements.md` — Module breakdown, acceptance criteria
- `research_context.md` — This file (research lineage)

### Earlier Phases
- `../00_brainstorm_session.md` — Phase 0 ideation
- `../01_targeted_research.md` — Phase 1 literature review
- `../02_synthesis.yaml` — Phase 2A hypothesis formulation
- `../03_refinement.md` — Phase 2A dialectical refinement

---

## Open Questions for Phase 3

1. Should we add gradient norm logging to detect LN instability early?
2. Should we checkpoint models at 90% accuracy for later gradient analysis (h-m1)?
3. Should we pre-download Waterbirds to avoid network issues during multi-seed runs?
4. Should we parallelize seeds across multiple GPUs or run sequentially?

---

**Research Context Status**: COMPLETED  
**Phase 2C Status**: COMPLETED  
**Next Phase**: Phase 3 (Implementation Planning)
