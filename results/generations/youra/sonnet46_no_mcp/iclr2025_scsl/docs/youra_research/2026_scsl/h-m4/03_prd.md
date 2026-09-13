# Product Requirements Document: H-M4
# DFR Last-Layer Reweighting Efficacy vs. Backbone Training Depth (t* Correlation)

**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-05-04
**Phase:** 3 - Implementation Planning
**Tier:** FULL (max 30 tasks)

---

## 1. Executive Summary

H-M4 tests whether DFR (Deep Feature Reweighting) last-layer reweighting efficacy is positively correlated with backbone training depth relative to the transition epoch t* (identified in H-M3 as mean_t*=2.0 epochs). The experiment trains ResNet-50 backbones via ERM to 5 different epoch checkpoints {1, 2, 10, 20, 30}, applies standard DFR at each checkpoint, and computes Pearson r between WGA improvement (DFR WGA - ERM WGA) and (epoch - t*).

**Key Insight:** This is an INCREMENTAL hypothesis building on H-E1 (backbone training infrastructure), H-M1 (gradient analysis reuse), H-M2 (complexity metrics context), and H-M3 (t*=2.0 epochs result). The primary new deliverable is the 5-condition DFR evaluation pipeline and correlation analysis. Waterbirds data and ResNet-50 training infrastructure are reused from prior hypotheses.

**SHOULD_WORK Gate:** Pearson r > 0.7 (one-tailed p < 0.05, df=3) between DFR WGA improvement and (epoch - t*). Failure logs limitation but does NOT stop pipeline.

---

## 2. Problem Statement

H-M3 established that t* (the backbone transition epoch where spurious-before-core gap closes) is a reproducible structural property of SGD training (std(t*)=2.0 epochs, MUST_WORK PASS). However, whether t* is *causally relevant* to DFR efficacy remains unvalidated. H-M4 asks: *Does backbone training depth relative to t* predict DFR's ability to reweight the last layer for worst-group accuracy?*

This is critical because:
- If DFR improvement correlates with (epoch - t*), it confirms t* as the mechanistic threshold for backbone readiness
- This provides the first empirical evidence linking the spurious-before-core dynamics directly to DFR's practical efficacy
- Prior DFR work (Kirichenko 2022) uses fully-trained backbones; H-M4 is the first systematic truncation ablation

**SHOULD_WORK Gate:** Pearson r > 0.7 (one-tailed, df=3) for correlation between WGA improvement and (epoch - t*). Statistical note: with n=5 conditions, one-tailed t-test requires |r| > 0.805 for p < 0.05; r > 0.7 is the effect size criterion.

---

## 3. Functional Requirements

### FR-1: Backbone Training Module (5-Condition ERM)
- **FR-1.1:** Train ResNet-50 (pretrained ImageNet) via ERM on Waterbirds using SGD (lr=1e-3, momentum=0.9, wd=1e-4), 3 seeds
- **FR-1.2:** Save checkpoints at epochs {1, 2, 10, 20, 30} for each seed (5 conditions × 3 seeds = 15 checkpoints)
- **FR-1.3:** Reuse training configuration from H-E1 exactly (same SGD params, batch_size=128, max_epochs=30, CrossEntropyLoss)
- **FR-1.4:** Continue saving every 2 epochs for continuity; 5 target checkpoints are mandatory saves
- **FR-1.5:** Log ERM WGA at each of the 5 checkpoints using backbone's own fc layer

### FR-2: Feature Extraction Module
- **FR-2.1:** Implement `extract_features(backbone, loader)` — returns (features, labels) where features are 2048-dim pooled layer4 output from frozen ResNet-50
- **FR-2.2:** Implement `extract_features_with_groups(backbone, loader)` — returns (features, labels, group_ids)
- **FR-2.3:** Freeze backbone weights before feature extraction (backbone.eval(), no_grad)
- **FR-2.4:** Validate feature shape: assert features.shape[1] == 2048
- **FR-2.5:** Support both val split (for DFR fitting) and test split (for WGA evaluation)

### FR-3: DFR Reweighting Module
- **FR-3.1:** Implement `apply_dfr(backbone, val_loader, test_loader)` following PolinaKirichenko/dfr protocol
- **FR-3.2:** Fit `LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced', solver='lbfgs', penalty='l2')` on val features
- **FR-3.3:** Use fixed DFR seed=42 across all 5 conditions (only IV = training duration)
- **FR-3.4:** Return DFR WGA, ERM WGA, and WGA improvement = DFR WGA - ERM WGA
- **FR-3.5:** Use held-out validation split ONLY for fitting (no data leakage from test set)

### FR-4: WGA Evaluation Module
- **FR-4.1:** Implement `worst_group_accuracy(predictions, labels, group_ids)` — returns min accuracy over 4 Waterbirds groups
- **FR-4.2:** Groups: {0: landbird/water, 1: waterbird/land, 2: landbird/land, 3: waterbird/water}
- **FR-4.3:** Log per-group accuracy alongside WGA for diagnostic purposes
- **FR-4.4:** Compute ERM WGA using backbone's fc layer predictions (no DFR)
- **FR-4.5:** Evaluate on full Waterbirds test set (5,794 samples) with group annotations

### FR-5: 5-Condition Experiment Orchestrator
- **FR-5.1:** For each of 5 epoch conditions {1, 2, 10, 20, 30}, for each of 3 seeds: load checkpoint, extract features, apply DFR, compute WGA improvement
- **FR-5.2:** Compute per-condition average WGA improvement across 3 seeds
- **FR-5.3:** Compute Pearson r between per-condition avg improvement and (epoch - t*) where t*=2 (from H-M3 mean_t*)
- **FR-5.4:** Compute one-tailed p-value (df=3) and two-tailed p-value for reporting
- **FR-5.5:** Report both r and p separately per methodology note in experiment brief

### FR-6: Mechanism Verification
- **FR-6.1:** Implement `verify_mechanism_activated(results_per_epoch)` checking 4 indicators:
  - `dfr_applied`: DFR WGA is not None at all 5 conditions
  - `feature_shape_correct`: feature_dim == 2048 at all conditions
  - `dfr_improves_erm`: majority (≥3/5) conditions show positive WGA improvement
  - `positive_trend`: improvement at epoch 30 > improvement at epoch 1
- **FR-6.2:** Compute Pearson r and p-value within verify function
- **FR-6.3:** Set `mechanism_supported = r > 0.7`
- **FR-6.4:** Log mechanism activation indicators with per-indicator breakdown

### FR-7: Visualization
- **FR-7.1:** Generate mandatory gate metrics plot: bar chart of DFR WGA improvement at each of 5 epoch conditions; horizontal reference line at r=0.7; annotate Pearson r value
- **FR-7.2:** Generate scatter plot: (epoch - t*) vs. DFR WGA improvement with regression line and 95% CI; annotate r and p-value
- **FR-7.3:** Generate WGA curves: ERM WGA and DFR WGA as function of training epochs (line plot, 5 points, 3 seeds as error bars)
- **FR-7.4:** Generate monotonicity check: bar chart of differences WGA_improvement[t+1] - WGA_improvement[t] at each step
- **FR-7.5:** Save all figures to `h-m4/figures/` directory

### FR-8: Results Export
- **FR-8.1:** Save JSON: per-condition ERM WGA, DFR WGA, WGA improvement (per seed and averaged); pearson_r, pearson_p_onetail, pearson_p_twotail; mechanism_indicators; gate_passed
- **FR-8.2:** Save CSV: 15-row table (5 conditions × 3 seeds) with all metrics
- **FR-8.3:** Print gate evaluation summary to stdout: PASS (r>0.7, p<0.05) / LIMITATION (r≤0.7)

---

## 4. Data Specification

### Primary Dataset: Waterbirds (reuse from H-M1 cache)

**Source:** Sagawa et al. 2020 (GroupDRO); kohpangwei/group_DRO dataset class
**Cache Path:** `/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds`
**Verified:** True (from H-M1 data_setup)
**No download needed** — already cached and verified

**Statistics:**
- Train: 4,795 samples | Val: 1,199 samples | Test: 5,794 samples
- Classes: 2 (landbird=0, waterbird=1)
- Groups: 4 (spurious × core label combinations)
- Group sizes (train): {0:3498, 1:184, 2:56, 3:1057}
- Worst group (train): group 2 (waterbird on land), n=56

**Preprocessing (reuse from H-E1/H-M1 — no change):**
- Training: `RandomResizedCrop(224) → RandomHorizontalFlip → Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])`
- Eval: `Resize(256) → CenterCrop(224) → Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])`

**Loading:**
```python
# Method: kohpangwei/group_DRO WaterbirdsDataset
dataset = WaterbirdsDataset(root='.data_cache/datasets/waterbirds/', split='train')
# group_id available in dataset.group_array
```

**Auto-download datasets (NO download task needed):** None — Waterbirds requires manual setup (already done in H-M1).

---

## 5. Model Specification

### Baseline Model: ResNet-50 ERM (5 truncation conditions)
- **Architecture:** ResNet-50 pretrained on ImageNet (torchvision)
- **Backbone:** 23.5M parameters; final fc: Linear(2048, 2)
- **ERM WGA:** Evaluated using backbone's own fc layer at each of 5 checkpoints
- **Loading:** `torchvision.models.resnet50(pretrained=True)`

### Proposed Model: ResNet-50 (truncated ERM) + DFR Last-Layer Reweighting
- **5 Training Conditions (PoC-adjusted):** epochs {1, 2, 10, 20, 30}
  - Original design: {t*-20, t*, t*+20, t*+50, full} → clipped to {1, 2, 10, 20, 30} for 30-epoch PoC run
  - t* = 2 epochs (from H-M3 mean_t*=2.0)
- **DFR Step:** Frozen backbone + `LogisticRegression(C=1.0, class_weight='balanced', solver='lbfgs')` fit on val features
- **Features:** 2048-dim pooled layer4 output from frozen backbone
- **DFR Seed:** Fixed=42 (isolates training duration as sole IV)

### Reference Benchmarks
| Method | Expected WGA (PoC 30-epoch) | Source |
|--------|---------------------------|--------|
| ERM (full 30 epochs) | ~65-72% | Kirichenko 2022 (scaled to PoC) |
| DFR (full backbone) | ~75-85% | Kirichenko 2022 (PoC estimate) |
| GroupDRO upper bound | ~91% | Sagawa 2020 (300-epoch) |

---

## 6. Evaluation Metrics

| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| `pearson_r` | Pearson correlation: WGA improvement vs (epoch - t*) over 5 conditions | > 0.7 (SHOULD_WORK) |
| `pearson_p_onetail` | One-tailed p-value (df=3); directional hypothesis r>0 | < 0.05 (requires r>0.805) |
| `dfr_wga_per_condition` | DFR WGA at each of 5 epoch checkpoints (avg over 3 seeds) | Informational |
| `erm_wga_per_condition` | ERM WGA at each of 5 epoch checkpoints | Informational |
| `wga_improvement_per_condition` | DFR WGA - ERM WGA at each checkpoint | Monotonic increase expected |
| `monotonicity_check` | improvement[t+1] - improvement[t] > 0 at each step | Secondary criterion |

**Primary Success Criteria (SHOULD_WORK):**
- Pearson r > 0.7 AND one-tailed p < 0.05 (df=3, requires r > 0.805)

**Secondary Criteria:**
- WGA improvement monotonically increases with epochs past t*
- DFR at epoch < t* shows < 50% of maximum WGA improvement

**Statistical Note:** Document both r and p separately. r>0.7 is the effect size threshold; p<0.05 requires r>0.805 with n=5 conditions. Report both threshold assessments.

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy>=1.21.0
scipy>=1.7.0           # pearsonr, bootstrap CI
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=0.24.0   # LogisticRegression for DFR
torch>=1.9.0
torchvision>=0.10.0    # ResNet-50, dataset transforms
pyyaml>=5.4.0
```

### 7.2 External Repositories (Reference Only)
- `PolinaKirichenko/deep_feature_reweighting`: Official DFR protocol (PRIMARY reference)
- `kohpangwei/group_DRO`: WaterbirdsDataset class, WGA evaluation, ERM training

### 7.3 Internal Dependencies (CRITICAL)
- **Waterbirds data cache:** `.data_cache/datasets/waterbirds` (from H-M1, verified=True)
- **H-E1 training config:** SGD(lr=1e-3, momentum=0.9, wd=1e-4), batch_size=128, 30 epochs (reuse exactly)
- **H-M3 result:** mean_t*=2.0 epochs (used as t* in correlation computation)
- **Seeds:** {1, 2, 3} — same as H-E1/M1/M2/M3 for cross-hypothesis reproducibility

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Total runtime: <2 hours (includes 3-seed × 30-epoch training + 15 DFR evaluations)
- Feature extraction: batch_size=256 on GPU (eval mode, no gradients)
- DFR fitting: <10 seconds per condition (sklearn LogReg on 1,199 val samples)

### NFR-2: Reproducibility
- All seeds fixed: torch.manual_seed(seed), numpy.random.seed(seed), random.seed(seed)
- DFR seed=42 fixed for all 5 conditions
- Results saved to JSON for verification

### NFR-3: Robustness
- Checkpoint save verification: confirm file exists after each save
- Feature shape assertion: fail early if features not 2048-dim
- DFR convergence check: verify LogReg converges (max_iter=1000 sufficient for 1,199 samples)
- Handle case where DFR WGA < ERM WGA (log as anomaly, continue)

### NFR-4: GPU
- Single GPU only: set `CUDA_VISIBLE_DEVICES=<lowest-memory GPU>` before training
- Eval and feature extraction also on GPU for speed
- Fall back to CPU if GPU unavailable (training will be slower)

---

## 9. Success Criteria (SHOULD_WORK Gate)

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Pearson r > 0.7 | Between WGA improvement and (epoch - t*) | PRIMARY (gate) |
| One-tailed p < 0.05 | df=3, requires r > 0.805 | PRIMARY (gate) |
| Monotonic improvement | improvement increases with epochs past t* | SECONDARY |
| DFR at epoch<t* < 50% max | Early backbone DFR boost below half of max | TERTIARY |

**LIMITATION conditions (failure does NOT stop pipeline):**
- r ∈ [0.3, 0.7]: Log "moderate correlation; threshold not met; DFR improvement may be driven by total epochs rather than epoch-t* specifically"
- r < 0.3: Log "weak correlation; alternative explanation: DFR efficacy may depend on absolute training duration rather than t*"
- Non-monotonic: Use gap area A as alternative metric; report as limitation

**PASS condition:** r > 0.7 AND p < 0.05 (one-tailed)

---

## 10. Out of Scope

- CelebA replication (Waterbirds sufficient for SHOULD_WORK gate)
- Full 300-epoch training (PoC uses 30 epochs per H-E1 infrastructure)
- GroupDRO training (upper bound reference only)
- JTT comparison (separate hypothesis if needed)
- Hyperparameter search for DFR (C=1.0 fixed per official protocol)
- New dataset preprocessing (reuses H-E1/M1 pipeline exactly)

---

## 11. Continuation Context

**Building on:**
- H-E1: Training infrastructure (SGD config, checkpoint saving, 30-epoch PoC), delta(t) curves
- H-M1: Waterbirds data cache verified, ResNet-50 training stable
- H-M2: Spurious simplicity confirmed (3/3 metrics) — supports DFR mechanism
- H-M3: t*=2.0 epochs (mean, std=2.0) — defines 5 truncation conditions

**Enabling:**
- Phase 4.5 (Synthesis): H-M4 result completes the mechanistic chain
- Phase 6 (Paper Writing): DFR timing result is key empirical contribution

---

*Generated by Phase 3 Workflow (no-MCP variant, inline PRD generation)*
*PRD based on Phase 2C experiment brief: h-m4/02c_experiment_brief.md*
*Base hypothesis context: H-M3 (t*=2.0 epochs, MUST_WORK PASS)*
*Date: 2026-05-04*
