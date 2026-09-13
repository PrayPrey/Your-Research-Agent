# Product Requirements Document: Dataset Coverage Audit (H-E1)

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Phase:** Phase 3 (Implementation Planning)  
**Date:** 2026-08-20

---

## 1. Executive Summary

Build automated coverage audit system to validate heterogeneous model zoo datasets (ModelZooDataset, SANE, ViTModelZoo) contain ≥30 models in ≥70% of architecture-task cells. Primary blocker for Phase 1 hierarchical VAE experiments.

**Success Gate:** ≥70% coverage OR 50-70% coverage with critical cells (CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet) all ≥30 models.

**Deliverables:**
1. Coverage matrix CSV + heatmap PNG
2. Metadata database (Parquet, ~55-60K rows)
3. Validation report (Markdown)
4. Gate decision (PASS/PARTIAL/FAIL)

---

## 2. Functional Requirements

### FR1: Dataset Ingestion
**Priority:** P0  
**Description:** Download and cache ModelZooDataset (27 zoos), SANE (7-9 zoos), ViTModelZoo (if available).

**Acceptance Criteria:**
- All Zenodo DOIs resolved and downloaded to `datasets/modelzoo/`
- SANE zoos downloaded via `modelzoos.cc` to `datasets/sane/`
- ViTModelZoo attempted; fallback to Hugging Face timm models if unavailable
- Total disk usage ≤350GB
- Download resumable (no re-download on failure)

**Technical Constraints:**
- Use `zenodo_get` for ModelZooDataset downloads
- SANE requires FFCV-compiled preprocessing
- No GPU required

### FR2: Metadata Extraction
**Priority:** P0  
**Description:** Extract (architecture, task, model_id) tuples from all zoos into unified Parquet database.

**Acceptance Criteria:**
- Parquet schema: `{model_id: str, architecture: str, task: str, hyperparams: dict, source: str, epoch: int, accuracy: float}`
- ModelZooDataset: Parse `.pt` files via `torch.load(zoo['properties'])`
- SANE: Parse JSON config files
- ViTModelZoo: Standardize timm checkpoint metadata
- Row count: 55,000-60,000 models
- Indexed by (architecture, task) for fast groupby

**Technical Constraints:**
- Handle missing hyperparameters gracefully (fill with null)
- Validate no duplicate model_ids
- Cross-validate architecture-task pairs (flag ResNet-MNIST as invalid)

### FR3: Coverage Audit
**Priority:** P0  
**Description:** Generate architecture × task contingency table, compute coverage percentage, flag sparse cells.

**Acceptance Criteria:**
- Output `coverage_matrix.csv` with rows=architectures, columns=tasks, values=model counts
- Coverage percentage = (cells with ≥30 models) / (total cells) × 100
- Critical cell validation: Check CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet
- Sparse cell report: List all cells with <30 models, sorted ascending
- Pass/fail determination per gate logic

**Technical Constraints:**
- Architecture categories: {CNN, ResNet, ViT, MLP, RNN}
- Task categories: {MNIST, FMNIST, SVHN, USPS, CIFAR10, CIFAR100, TinyImageNet, EuroSAT, ImageNet}
- Total cells: ~40-45 (not all combinations present)
- Use pandas `groupby().size().unstack()`

### FR4: Visualization
**Priority:** P1  
**Description:** Generate heatmap of coverage matrix (red=sparse, green=sufficient).

**Acceptance Criteria:**
- Output `coverage_heatmap.png` at 300 DPI
- Seaborn heatmap with annotations (model counts per cell)
- Colormap: RdYlGn (red: 0-29 models, yellow: 30-99, green: ≥100)
- Title: "Architecture-Task Coverage Matrix"
- Legible axis labels (no truncation)

**Technical Constraints:**
- Figure size: 12×6 inches
- Use `sns.heatmap()` with `annot=True, fmt='d'`

### FR5: Validation Report
**Priority:** P0  
**Description:** Generate Markdown report with coverage percentage, critical cell status, sparse cell analysis, gate decision.

**Acceptance Criteria:**
- File: `h-e1_validation_report.md`
- Sections: Coverage Summary, Critical Cells, Sparse Cells, Gate Decision, Next Steps
- Include coverage percentage (to 1 decimal)
- List critical cells with PASS/FAIL status
- Recommend gate decision (PASS/PARTIAL/FAIL) with justification
- Timestamp of audit run

**Technical Constraints:**
- Auto-generated via Python script
- No manual editing required

### FR6: Fallback Strategies
**Priority:** P2  
**Description:** If coverage <70%, implement scope reduction or external augmentation.

**Acceptance Criteria:**
- **Scope Reduction:** Identify well-covered architecture families (≥70% task coverage)
- **External Augmentation:** Query Hugging Face model hub for ViT-ImageNet models
- Flag augmented models as `source='huggingface'` in metadata
- Document fallback choice in validation report

**Technical Constraints:**
- Prefer real models over synthetic augmentation
- Never synthesize models unless no alternatives exist
- External models must match taxonomy (same architecture/task labels)

---

## 3. Non-Functional Requirements

### NFR1: Performance
- Metadata extraction: ≤4 hours on single CPU core
- Coverage analysis: ≤30 minutes
- Visualization: ≤10 minutes
- Total pipeline runtime: ≤6 hours (excluding downloads)

### NFR2: Reproducibility
- Deterministic results (no random seeds)
- Versioned dependencies (`environment.yml` pinned)
- Cached downloads (no re-fetch on re-run)

### NFR3: Maintainability
- Modular scripts: separate download, extraction, audit, visualization
- Config file for paths and thresholds (`config.yaml`)
- Logging to stdout with timestamps

---

## 4. System Architecture

### 4.1 Data Flow
```
[Zenodo/modelzoos.cc] → [Download Scripts] → [Raw Zoos (datasets/)]
                                                      ↓
                                           [Metadata Extractor]
                                                      ↓
                                           [zoo_metadata.parquet]
                                                      ↓
                                              [Coverage Auditor]
                                                      ↓
                                  [coverage_matrix.csv] + [heatmap.png]
                                                      ↓
                                            [Report Generator]
                                                      ↓
                                        [h-e1_validation_report.md]
```

### 4.2 Directory Structure
```
datasets/
  modelzoo/
    mnist_cnn.zip
    cifar10_resnet18.zip
    ...
  sane/
    cifar10_cnn_preprocessed/
    ...
  vit/  # Optional
outputs/
  zoo_metadata.parquet
  coverage_matrix.csv
  coverage_heatmap.png
  h-e1_validation_report.md
scripts/
  download_modelzoo.sh
  download_sane.sh
  extract_metadata.py
  audit_coverage.py
  visualize_coverage.py
  generate_report.py
  run_all.sh  # Master pipeline
config.yaml
environment.yml
```

---

## 5. Implementation Plan

### Phase 1: Data Ingestion (1-2 days)
**Tasks:**
1. Write `download_modelzoo.sh` (Zenodo DOIs)
2. Write `download_sane.sh` (modelzoos.cc)
3. Test downloads, verify file integrity
4. Implement resume logic (skip existing files)

### Phase 2: Metadata Extraction (0.5 days)
**Tasks:**
1. Write `extract_metadata.py` (ModelZooDataset parser)
2. Add SANE JSON parser
3. Add ViTModelZoo/timm parser
4. Validate schema, output Parquet

### Phase 3: Coverage Audit (0.5 days)
**Tasks:**
1. Write `audit_coverage.py`
2. Compute coverage matrix
3. Validate critical cells
4. Output CSV

### Phase 4: Visualization (0.5 days)
**Tasks:**
1. Write `visualize_coverage.py`
2. Generate heatmap PNG
3. Test rendering quality

### Phase 5: Report Generation (0.5 days)
**Tasks:**
1. Write `generate_report.py`
2. Auto-generate validation report
3. Implement gate decision logic

### Phase 6: Integration Testing (0.5 days)
**Tasks:**
1. Write `run_all.sh` master pipeline
2. End-to-end test on subset
3. Verify reproducibility

**Total:** 3-4 days (aligned with experiment brief timeline)

---

## 6. Risks and Mitigations

### Risk 1: ViTModelZoo Unavailable
**Probability:** High  
**Impact:** Medium  
**Mitigation:** Fallback to Hugging Face timm models (10K+ ViT checkpoints available)

### Risk 2: Coverage <70%
**Probability:** Medium  
**Impact:** High (blocks Phase 1)  
**Mitigation:** Scope reduction to CNN/ResNet families (documented in PARTIAL PASS scenario)

### Risk 3: Metadata Quality Issues
**Probability:** Low  
**Impact:** Medium  
**Mitigation:** Cross-validation checks, manual inspection of 100 samples, contact authors

### Risk 4: Download Failures
**Probability:** Medium  
**Impact:** Low  
**Mitigation:** Resume logic, retry with exponential backoff, cache successful downloads

---

## 7. Dependencies

### Software
- Python 3.10
- PyTorch 2.0
- pandas 2.0
- seaborn 0.12
- zenodo_get
- huggingface_hub

### External APIs
- Zenodo (ModelZooDataset DOIs)
- modelzoos.cc (SANE downloads)
- Hugging Face Hub (fallback ViT models)

### Compute
- CPU-only (no GPU required)
- 350GB disk space
- 16GB RAM minimum

---

## 8. Success Metrics

| Metric | Target | Type |
|--------|--------|------|
| Coverage percentage | ≥70% | PRIMARY |
| Critical cell coverage | All 3 cells ≥30 models | SECONDARY |
| Metadata quality | <5% invalid entries | VALIDATION |
| Runtime | ≤6 hours (excl. downloads) | PERFORMANCE |
| Reproducibility | Identical results on re-run | RELIABILITY |

---

## 9. Out of Scope

- GPU-accelerated metadata extraction (not needed)
- Synthetic model generation (last resort only)
- Cross-zoo transfer learning (fallback strategy, not primary)
- Phase 1 CKA feasibility testing (separate hypothesis)
- Hyperparameter analysis beyond diversity checks

---

## 10. Approval

**Gate Decision Authority:** Phase 3 validator  
**Stakeholders:** Hypothesis verification pipeline, Phase 1 blocker resolution  
**Next Steps:** Architecture + Logic + Config design (parallel agents)

---

**END OF PRD**
