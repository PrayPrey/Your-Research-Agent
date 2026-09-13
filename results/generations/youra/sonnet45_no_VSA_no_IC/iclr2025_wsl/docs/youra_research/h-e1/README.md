# H-E1: Dataset Coverage Audit

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Phase:** Pre-Phase 1  
**Gate:** MUST_WORK  
**Status:** Experiment design complete  
**Date:** 2026-08-20

---

## Quick Reference

### Hypothesis Statement
Under heterogeneous model zoo datasets (ModelZooDataset, SANE, ViTModelZoo), if we audit architecture-task cell coverage, then at least 70% of cells will contain ≥30 models, sufficient for statistical validity, because these datasets were specifically designed for inhomogeneous zoo research and target diverse architecture families.

### Success Criteria
- **Primary:** ≥70% of architecture-task cells contain ≥30 models
- **Secondary:** All critical cells (CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet) contain ≥30 models
- **Tertiary:** Bootstrap power ≥0.80 for n=30 threshold

### Gate Decision
- **PASS:** Proceed to Phase 1 (H-M-integrated CKA gate)
- **PARTIAL:** Proceed with scope reduction
- **FAIL:** ABORT Phase 1, insufficient data

---

## Folder Contents

### Core Documents

1. **`dataset_specification.md`**  
   Detailed specifications for ModelZooDataset, SANE, and ViTModelZoo including:
   - Download sources (Zenodo DOIs, modelzoos.cc, Hugging Face)
   - Metadata schemas
   - Expected coverage (~55-60K models across 36 architecture-task cells)
   - Data loading patterns

2. **`baseline_experiments.md`**  
   Validation baselines and fallback strategies:
   - Metadata quality baseline (<5% error rate)
   - Coverage comparison vs literature expectations
   - Statistical power validation (bootstrap n=30 threshold)
   - Scope reduction strategies
   - External dataset integration protocols

3. **`implementation_plan.md`**  
   Step-by-step execution guide:
   - Environment setup (3-4 day timeline)
   - Dataset download scripts (ModelZooDataset, SANE, ViT)
   - Metadata extraction pipeline
   - Coverage analysis automation
   - Validation & quality checks

4. **`validation_protocol.md`**  
   Systematic validation procedure:
   - Data collection validation
   - Metadata quality checks
   - Coverage matrix generation
   - Critical cell validation
   - Bootstrap power estimation
   - Gate decision logic

### Expected Outputs (Generated During Execution)

- `coverage_matrix.csv` - Architecture × task contingency table
- `coverage_heatmap.png` - Color-coded visualization
- `sparse_cells.csv` - Cells with <30 models
- `validation_report.md` - Coverage results and gate decision
- `critical_cells.json` - Critical cell validation results
- `gate_decision.json` - Final gate decision
- `coverage_result.json` - Overall coverage percentage
- `power_validation.json` - Bootstrap power estimate

---

## Experiment Overview

### Objective
Validate that available model zoo datasets provide sufficient coverage for statistically valid hierarchical VAE experiments testing cross-architecture task clustering.

### Why This Matters
**Assumption A1 from Phase 2A:** Model zoos contain sufficient cross-architecture coverage (≥30 models per architecture-task cell) for statistical validity.

**If this fails:**
- Bootstrap testing underpowered (n<30)
- Clustering results may reflect sampling noise, not genuine task structure
- Entire Phase 1-4 verification pipeline blocks

**This is a gate hypothesis** - blocks downstream work if coverage insufficient.

### Methodology
1. Download three model zoo sources (~300GB total)
2. Extract metadata (architecture, task, hyperparameters)
3. Generate architecture × task cross-tabulation matrix
4. Calculate coverage percentage (cells with ≥30 models)
5. Validate critical cells and statistical power
6. Make gate decision (PASS/PARTIAL/FAIL)

### Key Datasets

| Dataset | Models | Architectures | Tasks | Source |
|---------|--------|---------------|-------|--------|
| ModelZooDataset | 50,360 | CNN, ResNet-18 | 8 vision tasks | Zenodo (DOIs) |
| SANE | 7,000 | CNN, ResNet-18 | 5 vision tasks | modelzoos.cc |
| ViTModelZoo (fallback: HF) | 500-1000 | ViT | ImageNet | GitHub / Hugging Face |
| **Total** | **~58,000** | **4 families** | **9 tasks** | **36 cells** |

---

## Execution Workflow

### Quick Start
```bash
# 1. Setup environment
conda env create -f environment.yml
conda activate h-e1-coverage

# 2. Download datasets (1-2 days)
bash scripts/download_modelzoo.sh
bash scripts/download_sane.sh
python scripts/download_vit_zoo.py

# 3. Extract metadata (0.5 days)
python scripts/extract_modelzoo_metadata.py
python scripts/extract_sane_metadata.py
python scripts/extract_vit_metadata.py
python scripts/merge_metadata.py

# 4. Coverage analysis (0.5 days)
python scripts/coverage_audit.py

# 5. Validation (0.5 days)
python scripts/validate_metadata.py
python scripts/validate_bootstrap_power.py

# 6. Review gate decision
cat h-e1/validation_report.md
cat h-e1/gate_decision.json
```

### Expected Timeline
- **Day 1:** Environment setup + dataset download start
- **Day 2:** Dataset download complete, metadata extraction
- **Day 3:** Coverage analysis, validation, gate decision
- **Total:** 3-4 days (automated)

---

## Key Predictions

### Expected Coverage Distribution

**Well-Covered (≥100 models):**
- CNN-CIFAR10 (~5000 models from ModelZooDataset)
- CNN-MNIST (~4000 models)
- ResNet-CIFAR100 (~1000 models from SANE)
- ResNet-TinyImageNet (~800 models)

**Sufficiently Covered (30-99 models):**
- CNN-FMNIST (~3000 models)
- CNN-SVHN (~2000 models)
- ResNet-CIFAR10 (~600 models)
- ResNet-SVHN (~400 models)

**Sparse (<30 models):**
- ViT-* (depends on ViTModelZoo availability)
- MLP-* (likely absent from all sources)
- RNN-* (likely absent)

**Predicted Overall Coverage:** 55-70% (borderline PASS/PARTIAL)

### Critical Cell Status (Predicted)
- CNN-CIFAR10: ✓ PASS (expect >3000 models)
- ResNet-CIFAR100: ✓ PASS (expect >800 models)
- ResNet-TinyImageNet: ✓ PASS (expect >600 models)
- CNN-MNIST: ✓ PASS (expect >3000 models)

**Predicted Gate Decision:** PARTIAL (50-70% coverage, critical cells OK)

---

## Fallback Strategies

### If PARTIAL (50-70% coverage, critical OK)

**Scope Reduction:**
- Restrict to {CNN, ResNet} architectures only
- Focus on {CIFAR10, CIFAR100, TinyImageNet, MNIST, FMNIST} tasks
- Reduces scope from 36 cells to ~10 well-covered cells
- **Impact:** Loses ViT/MLP/RNN novelty, but core mechanism testable

### If FAIL (<50% coverage OR critical cells sparse)

**Option 1: External Augmentation**
- Integrate Hugging Face model hub checkpoints
- Download additional ResNet/ViT models trained on target tasks
- **Constraint:** Use ONLY real pre-trained models (no synthetic)

**Option 2: Delay & Collect**
- Pause Phase 1, return to Phase 0
- Collaborate with ModelZooDataset authors to extend dataset
- Wait for ViTModelZoo release

**Option 3: Pivot to Homogeneous**
- Reduce to single-architecture setting (CNN-only or ResNet-only)
- **Impact:** Loses cross-architecture novelty claim entirely

---

## Dependencies & Prerequisites

### Software Requirements
- Python 3.10+
- PyTorch 2.0+
- pandas, numpy, scipy
- matplotlib, seaborn
- zenodo_get (for Zenodo downloads)
- huggingface_hub (for ViT fallback)

### Compute Requirements
- **CPU:** 4+ cores (no GPU needed)
- **RAM:** 32GB (metadata processing)
- **Storage:** 500GB (datasets ~300GB, working space ~200GB)
- **Network:** High-bandwidth (downloading ~300GB)

### No Prerequisites
This is a foundation hypothesis (Level 0 in dependency graph). No other hypotheses must complete first.

### Blocks If Fails
- **H-M-integrated Phase 1:** CKA feasibility gate (requires sufficient model pairs)
- **H-M-integrated Phase 2-3:** VAE training (requires diverse architecture-task coverage)
- **H-M-integrated Phase 4:** WCSS clustering test (requires ≥30 samples per cell for bootstrap)

---

## Risk Assessment

### Primary Risks

1. **R1: Insufficient Coverage (HIGH)**
   - ModelZooDataset/SANE may not cover all 36 cells
   - ViTModelZoo availability uncertain
   - Mitigation: Scope reduction fallback, HF augmentation

2. **R6: Metadata Quality (MEDIUM)**
   - Task labels may be mislabeled or inconsistent
   - Architecture types may be misclassified
   - Mitigation: Manual validation of 100-sample subset

3. **R7: Download Failures (LOW)**
   - Zenodo/modelzoos.cc may be temporarily unavailable
   - Large file transfers may fail
   - Mitigation: Retry logic, cached mirrors

---

## Success Metrics

| Metric | Threshold | Type |
|--------|-----------|------|
| Overall coverage | ≥70% cells ≥30 models | PRIMARY |
| Critical cells | All 4 ≥30 models | SECONDARY |
| Metadata quality | <5% error rate | VALIDATION |
| Bootstrap power | ≥0.80 for n=30 | STATISTICAL |

**Gate Decision Tree:**
```
IF coverage ≥70% AND critical_pass AND power_pass:
    → PASS (proceed to Phase 1)
ELIF coverage ≥50% AND critical_pass:
    → PARTIAL (scope reduction)
ELSE:
    → FAIL (abort Phase 1)
```

---

## Related Documents

### Upstream (Phase 2B)
- `02b_verification_plan.md` - Full verification plan with H-E1 specification
- `02_synthesis.yaml` - Phase 2A synthesis with Assumption A1

### Downstream (Phase 1)
- Phase 1 will use H-E1 results to select architecture-task pairs for CKA feasibility gate
- Sparse cells identified here become robustness tests in Phase 4

### Parent Hypothesis
- **H-M-integrated** (mechanism) - Depends on H-E1 passing gate

---

## Notes

### Dataset Type
**Type:** `standard` (real, established datasets)  
**NOT synthetic:** All models are real trained checkpoints from controlled experiments.

### Statistical Justification
**Why n=30?**
- Bootstrap testing (100 resamples) requires ≥30 for 80% power
- Detects Cohen's d=0.5 (medium effect) at α=0.01
- Below n=30: Underpowered, clustering may reflect noise

**Why 70% coverage?**
- Allows 30% sparse cells as natural robustness test
- Ensures critical architecture families well-covered
- Balances feasibility vs rigor

### Experiment Scale
**Not trivially small:**
- ~58,000 models across 36 cells
- Full test sets used (CIFAR10 test = 10K images)
- No arbitrary small subsets (e.g., 50-sample evaluations)

---

## Contact & Support

**Issues:** If datasets unavailable or scripts fail, contact:
- ModelZooDataset: https://github.com/ModelZoos/ModelZooDataset/issues
- SANE: https://github.com/HSG-AIML/SANE/issues
- Pipeline issues: Document in verification_state.yaml

**Next Steps After Completion:**
1. Review `validation_report.md`
2. Check `gate_decision.json`
3. If PASS: Proceed to Phase 1 (H-M-integrated CKA gate)
4. If PARTIAL: Update verification plan with scope reduction
5. If FAIL: Return to Phase 0 or Phase 2A-Dialogue

---

**Status:** Experiment design complete, ready for execution  
**Last Updated:** 2026-08-20
