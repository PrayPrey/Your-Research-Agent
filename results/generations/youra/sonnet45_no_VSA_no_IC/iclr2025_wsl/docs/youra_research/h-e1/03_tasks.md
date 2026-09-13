# Implementation Task List: H-E1 Coverage Audit

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Tier:** Tier 1 (EXISTENCE hypotheses - simplified scope)  
**Total Budget:** 20 subtasks  
**Date:** 2026-08-20

---

## Budget Allocation

| Category | Subtasks | Rationale |
|----------|----------|-----------|
| Data Preparation | 4 | Download scripts (3 sources: ModelZoo/SANE/ViT) + integrity checks |
| Environment Setup | 2 | Conda environment + dependency verification |
| Epic Tasks | 7 | Metadata extraction (2) + Coverage audit (2) + Visualization (1) + Report (1) + Integration (1) |
| Subtasks (within Epics) | 7 | Parsing logic, validation checks, heatmap rendering, gate decision |
| Failsafe | 0 | EXISTENCE hypothesis - no complex failure modes |
| **Total** | **20** | |

**Tier Justification:** EXISTENCE hypothesis = data audit only, no model training/architecture implementation.

---

## EPIC-001: Environment Setup [Budget: 2 subtasks]

**Goal:** Create reproducible Python environment with all dependencies.

### EPIC-001.1: Create Conda Environment
**Type:** Environment Setup  
**Complexity:** 2  
**Dependencies:** None  

**Acceptance Criteria:**
- `environment.yml` created with pinned versions (Python 3.10, PyTorch 2.0, pandas 2.0)
- Environment created: `conda env create -f environment.yml`
- All imports verified: `python -c "import torch; import pandas; import seaborn"`

**Files Created:**
- `environment.yml`

**Commands:**
```bash
conda env create -f environment.yml
conda activate h-e1-coverage-audit
python -c "import torch, pandas, seaborn, zenodo_get; print('OK')"
```

---

### EPIC-001.2: Verify Disk Space and Create Directories
**Type:** Environment Setup  
**Complexity:** 1  
**Dependencies:** None  

**Acceptance Criteria:**
- ≥350GB free disk space verified
- Directory structure created: `datasets/{modelzoo,sane,vit}/`, `outputs/`, `logs/`
- `.gitignore` configured to exclude `datasets/` and `outputs/`

**Files Created:**
- `datasets/` (empty directories)
- `outputs/` (empty directory)
- `logs/` (empty directory)
- `.gitignore`

**Commands:**
```bash
df -h .  # Verify ≥350GB free
mkdir -p datasets/{modelzoo,sane,vit} outputs logs
echo -e "datasets/\noutputs/\nlogs/" > .gitignore
```

---

## EPIC-002: Dataset Download [Budget: 4 subtasks]

**Goal:** Download and cache all three model zoo datasets.

### EPIC-002.1: Download ModelZooDataset (Zenodo)
**Type:** Data Preparation  
**Complexity:** 3  
**Dependencies:** EPIC-001.1  

**Acceptance Criteria:**
- Download script `scripts/download_modelzoo.sh` created
- All 27 Zenodo DOIs downloaded to `datasets/modelzoo/`
- Checksums verified against Zenodo metadata
- Resume logic implemented (skip existing files)
- Total size: ~200GB

**Files Created:**
- `scripts/download_modelzoo.sh`
- `datasets/modelzoo/*.zip` (27 files)

**Commands:**
```bash
bash scripts/download_modelzoo.sh
ls datasets/modelzoo/ | wc -l  # Expect 27 files
```

**Subtask Breakdown:**
1. Write DOI list (from `03_config.md`)
2. Implement zenodo_get wrapper with resume
3. Verify checksums

---

### EPIC-002.2: Download SANE Zoos
**Type:** Data Preparation  
**Complexity:** 2  
**Dependencies:** EPIC-001.1  

**Acceptance Criteria:**
- Download script `scripts/download_sane.sh` created
- All 7-9 SANE zoos downloaded from modelzoos.cc
- Tarballs extracted to `datasets/sane/`
- Total size: ~50GB

**Files Created:**
- `scripts/download_sane.sh`
- `datasets/sane/*_preprocessed/` (7-9 directories)

**Commands:**
```bash
bash scripts/download_sane.sh
ls datasets/sane/ | wc -l  # Expect 7-9 directories
```

---

### EPIC-002.3: Download ViT Models (Hugging Face Fallback)
**Type:** Data Preparation  
**Complexity:** 3  
**Dependencies:** EPIC-001.1  

**Acceptance Criteria:**
- Download script `scripts/download_vit.py` created
- Query Hugging Face model hub for ViT models (filter: image-classification, transformers library)
- Download up to 5000 checkpoints to `datasets/vit/`
- Rate limit handling (429 status → exponential backoff)
- Total size: ~50-100GB

**Files Created:**
- `scripts/download_vit.py`
- `datasets/vit/*.pt` (up to 5000 files)
- `logs/vit_download_errors.log`

**Commands:**
```python
python scripts/download_vit.py --max-models=5000
```

**Subtask Breakdown:**
1. Query Hugging Face API with filters
2. Download checkpoints with retry logic
3. Log errors to `vit_download_errors.log`

---

### EPIC-002.4: Verify Dataset Integrity
**Type:** Data Preparation  
**Complexity:** 2  
**Dependencies:** EPIC-002.1, EPIC-002.2, EPIC-002.3  

**Acceptance Criteria:**
- All downloaded files verified (checksums or size checks)
- No corrupt zips/tarballs
- Total model count estimate: 55,000-60,000 models
- Summary logged to `logs/download.log`

**Commands:**
```bash
python scripts/verify_downloads.py
cat logs/download.log
```

---

## EPIC-003: Metadata Extraction [Budget: 5 subtasks]

**Goal:** Extract architecture/task/hyperparameters from all zoos into unified Parquet database.

### EPIC-003.1: Implement ModelZooDataset Parser
**Type:** Epic Task  
**Complexity:** 4  
**Dependencies:** EPIC-002.1  

**Acceptance Criteria:**
- `src/extract.py` created with `extract_modelzoo_metadata()` function
- Parse `.pt` files via `torch.load(zoo['properties'])`
- Extract: `model_id`, `architecture`, `task`, `hyperparams`, `source`, `epoch`, `accuracy`
- Normalize architecture names (resnet → ResNet, cnn → CNN, etc.)
- Normalize task names (fashionmnist → FMNIST, etc.)
- Output: pandas DataFrame

**Files Created:**
- `src/extract.py`

**Pseudo-code:**
```python
def extract_modelzoo_metadata(zoo_path: Path) -> pd.DataFrame:
    zoo = torch.load(zoo_path, map_location='cpu')
    rows = []
    for idx, props in enumerate(zoo['properties']):
        rows.append({
            'model_id': f"{zoo_path.stem}_{idx}",
            'architecture': normalize_arch(props.get('architecture')),
            'task': normalize_task(props.get('dataset')),
            # ... other fields
        })
    return pd.DataFrame(rows)
```

**Subtask Breakdown:**
1. Implement `extract_modelzoo_metadata()`
2. Implement `normalize_architecture()`
3. Implement `normalize_task()`
4. Unit test on 1 zoo file

---

### EPIC-003.2: Implement SANE Parser
**Type:** Epic Task  
**Complexity:** 3  
**Dependencies:** EPIC-002.2  

**Acceptance Criteria:**
- `src/extract.py` extended with `extract_sane_metadata()` function
- Parse SANE JSON config files
- Extract same schema as ModelZooDataset
- Handle FFCV-compiled format

**Pseudo-code:**
```python
def extract_sane_metadata(zoo_path: Path) -> pd.DataFrame:
    config = json.load((zoo_path / 'config.json').open())
    # Parse SANE-specific structure
    ...
```

---

### EPIC-003.3: Implement ViT Parser (Timm Fallback)
**Type:** Epic Task  
**Complexity:** 3  
**Dependencies:** EPIC-002.3  

**Acceptance Criteria:**
- `src/extract.py` extended with `extract_vit_metadata()` function
- Parse Hugging Face model metadata
- Standardize to same schema

---

### EPIC-003.4: Aggregate Metadata from All Sources
**Type:** Subtask  
**Complexity:** 2  
**Dependencies:** EPIC-003.1, EPIC-003.2, EPIC-003.3  

**Acceptance Criteria:**
- `src/extract.py` extended with `aggregate_metadata()` function
- Concatenate DataFrames from all sources
- Validate: no duplicate `model_id`, row count 50K-70K
- Filter invalid architecture-task pairs (ResNet-MNIST, ViT-MNIST)
- Output: `outputs/zoo_metadata.parquet` (150 MB, ~60K rows)

**Commands:**
```python
python scripts/extract_metadata.py
ls -lh outputs/zoo_metadata.parquet  # Expect ~150MB
```

**Subtask Breakdown:**
1. Parallel extraction (4 workers)
2. Concatenate DataFrames
3. Validation checks (duplicates, row count, taxonomy)
4. Write Parquet

---

### EPIC-003.5: Validate Metadata Quality
**Type:** Subtask  
**Complexity:** 2  
**Dependencies:** EPIC-003.4  

**Acceptance Criteria:**
- <5% unknown architectures
- <5% unknown tasks
- 0% duplicate model_ids
- Cross-validate architecture-task pairs (flag invalid combinations)
- Log validation report to `logs/validation.log`

**Commands:**
```python
python scripts/validate_metadata.py
cat logs/validation.log
```

---

## EPIC-004: Coverage Audit [Budget: 3 subtasks]

**Goal:** Compute coverage matrix, validate critical cells, determine gate decision.

### EPIC-004.1: Compute Coverage Matrix
**Type:** Epic Task  
**Complexity:** 3  
**Dependencies:** EPIC-003.4  

**Acceptance Criteria:**
- `src/audit.py` created with `compute_coverage_matrix()` function
- Generate architecture × task contingency table via `groupby().unstack()`
- Output: `outputs/coverage_matrix.csv` (5×9 matrix, ~2KB)

**Pseudo-code:**
```python
def compute_coverage_matrix(metadata_path: str) -> pd.DataFrame:
    df = pd.read_parquet(metadata_path)
    matrix = df.groupby(['architecture', 'task']).size().unstack(fill_value=0)
    matrix.to_csv('outputs/coverage_matrix.csv')
    return matrix
```

---

### EPIC-004.2: Validate Critical Cells and Compute Coverage Percentage
**Type:** Epic Task  
**Complexity:** 2  
**Dependencies:** EPIC-004.1  

**Acceptance Criteria:**
- `src/audit.py` extended with `validate_critical_cells()` and `compute_coverage_percentage()`
- Check 3 critical cells: CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet
- Compute overall coverage: (cells ≥30 models) / (total cells) × 100
- Return coverage percentage + critical cells status

**Pseudo-code:**
```python
def validate_critical_cells(matrix: pd.DataFrame) -> tuple[bool, dict]:
    critical = [('CNN', 'CIFAR10'), ('ResNet', 'CIFAR100'), ('ResNet', 'TinyImageNet')]
    cell_counts = {(a, t): matrix.loc[a, t] for a, t in critical}
    all_ok = all(count >= 30 for count in cell_counts.values())
    return all_ok, cell_counts
```

---

### EPIC-004.3: Determine Gate Decision
**Type:** Subtask  
**Complexity:** 2  
**Dependencies:** EPIC-004.2  

**Acceptance Criteria:**
- `src/audit.py` extended with `determine_gate_decision()` function
- Implement decision tree:
  - IF coverage ≥70%: PASS
  - ELIF 50-70% AND critical OK: PARTIAL
  - ELSE: FAIL
- Return decision + justification

**Pseudo-code:**
```python
def determine_gate_decision(coverage_pct: float, critical_ok: bool) -> tuple[str, str]:
    if coverage_pct >= 70:
        return 'PASS', 'Coverage ≥70%, proceed to Phase 1'
    elif 50 <= coverage_pct < 70 and critical_ok:
        return 'PARTIAL', 'Scope reduction acceptable'
    else:
        return 'FAIL', 'Insufficient coverage, ABORT Phase 1'
```

---

## EPIC-005: Visualization [Budget: 2 subtasks]

**Goal:** Generate coverage heatmap.

### EPIC-005.1: Generate Coverage Heatmap
**Type:** Epic Task  
**Complexity:** 3  
**Dependencies:** EPIC-004.1  

**Acceptance Criteria:**
- `src/visualize.py` created with `visualize_coverage()` function
- Generate seaborn heatmap: RdYlGn colormap, 12×6 inches, 300 DPI
- Annotate cells with model counts
- Output: `outputs/coverage_heatmap.png` (450 KB)

**Pseudo-code:**
```python
def visualize_coverage(matrix: pd.DataFrame, output_path: str):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='RdYlGn', ax=ax)
    plt.savefig(output_path, dpi=300)
```

---

### EPIC-005.2: Identify Sparse Cells
**Type:** Subtask  
**Complexity:** 1  
**Dependencies:** EPIC-004.1  

**Acceptance Criteria:**
- `src/audit.py` extended with `identify_sparse_cells()` function
- List all cells with <30 models, sorted ascending
- Return list of (architecture, task, count) tuples

---

## EPIC-006: Report Generation [Budget: 2 subtasks]

**Goal:** Auto-generate validation report.

### EPIC-006.1: Generate Validation Report
**Type:** Epic Task  
**Complexity:** 3  
**Dependencies:** EPIC-004.2, EPIC-004.3, EPIC-005.2  

**Acceptance Criteria:**
- `src/report.py` created with `generate_report()` function
- Markdown report with sections: Coverage Summary, Critical Cells, Sparse Cells, Gate Decision
- Output: `outputs/h-e1_validation_report.md` (~3KB)

**Template:**
```markdown
# Validation Report: H-E1

## Coverage Summary
- Overall Coverage: 72.3% of cells have ≥30 models
- Total Cells: 40
- Sufficient Cells: 29
- Sparse Cells: 11

## Critical Cells
| Architecture | Task | Count | Status |
|--------------|------|-------|--------|
| CNN | CIFAR10 | 891 | PASS |
| ResNet | CIFAR100 | 543 | PASS |
| ResNet | TinyImageNet | 432 | PASS |

## Gate Decision: PASS
Proceed to Phase 1 (H-M-integrated CKA feasibility gate).
```

---

### EPIC-006.2: Log Audit Results
**Type:** Subtask  
**Complexity:** 1  
**Dependencies:** EPIC-006.1  

**Acceptance Criteria:**
- Coverage percentage logged to `logs/validation.log`
- Gate decision logged
- Timestamp added

---

## EPIC-007: Integration and Testing [Budget: 2 subtasks]

**Goal:** End-to-end pipeline verification.

### EPIC-007.1: Create Master Pipeline Script
**Type:** Epic Task  
**Complexity:** 2  
**Dependencies:** All previous EPICs  

**Acceptance Criteria:**
- `scripts/run_all.sh` created
- Orchestrates: Download → Extract → Audit → Visualize → Report
- Logging to stdout and files
- Exit codes: 0 (PASS), 1 (PARTIAL), 2 (FAIL)

**Commands:**
```bash
bash scripts/run_all.sh
echo $?  # Check exit code
```

---

### EPIC-007.2: End-to-End Test on Subset
**Type:** Subtask  
**Complexity:** 2  
**Dependencies:** EPIC-007.1  

**Acceptance Criteria:**
- Test on 3 zoos (1 ModelZoo, 1 SANE, 1 ViT)
- Verify all outputs generated
- Validate reproducibility (run twice, compare outputs)

**Commands:**
```bash
bash scripts/run_all.sh --subset --zoos=3
diff outputs/coverage_matrix_run1.csv outputs/coverage_matrix_run2.csv
```

---

## Task Summary

| Category | Count | Budget |
|----------|-------|--------|
| EPIC Tasks (complexity ≥3) | 7 | 21 complexity points |
| Subtasks (complexity <3) | 13 | 26 complexity points |
| **Total Tasks** | **20** | **47 complexity points** |

**Average Complexity:** 2.35 (appropriate for EXISTENCE hypothesis)

**Timeline Estimate:** 3-4 days (aligned with experiment brief)

---

## Dependency Graph

```
EPIC-001.1 (Env Setup)
    ↓
EPIC-001.2 (Directories)
    ↓
EPIC-002.1, 002.2, 002.3 (Downloads) → EPIC-002.4 (Verify)
    ↓
EPIC-003.1, 003.2, 003.3 (Parsers) → EPIC-003.4 (Aggregate) → EPIC-003.5 (Validate)
    ↓
EPIC-004.1 (Coverage Matrix) → EPIC-004.2 (Critical Cells) → EPIC-004.3 (Gate Decision)
    ↓                               ↓
EPIC-005.1 (Heatmap)          EPIC-005.2 (Sparse Cells)
    ↓                               ↓
EPIC-006.1 (Report) → EPIC-006.2 (Logging)
    ↓
EPIC-007.1 (Master Script) → EPIC-007.2 (Test)
```

---

**END OF TASK LIST**
