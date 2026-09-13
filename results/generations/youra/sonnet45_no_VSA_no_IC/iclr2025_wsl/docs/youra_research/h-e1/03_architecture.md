# Architecture: Dataset Coverage Audit (H-E1)

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Phase:** Phase 3 (Architecture Design)  
**Date:** 2026-08-20

**Applied KB Patterns:** HuggingFace cache management, dataset download pipelines  
**Codebase Analysis (Serena):** Green-field project - no existing code to analyze

---

## System Overview

**Purpose:** Validate ModelZooDataset/SANE/ViTModelZoo contain ≥30 models in ≥70% of architecture-task cells.

**Pipeline:** Download → Extract Metadata → Audit Coverage → Visualize → Report

**Constraints:**
- CPU-only (no GPU)
- 55-60K models, ≤350GB storage
- Deterministic, cached downloads
- Single-pass processing

---

## Module Architecture

### 1. DownloadManager (`src/download.py`)

**Dependencies:** None (stdlib only)

```python
class DownloadManager:
    def __init__(self, cache_dir: str, resume: bool = True): ...
    def download_zenodo(self, doi: str, output_path: str) -> Path: ...
    def download_sane(self, zoo_name: str, output_path: str) -> Path: ...
    def download_timm_models(self, architectures: list[str], output_path: str) -> Path: ...
    def verify_checksums(self, file_path: Path, expected_hash: str) -> bool: ...
```

### 2. MetadataExtractor (`src/extract.py`)

**Dependencies:** torch, pandas

```python
class MetadataExtractor:
    def extract_from_modelzoo(self, zoo_path: Path) -> pd.DataFrame: ...
    def extract_from_sane(self, zoo_path: Path) -> pd.DataFrame: ...
    def extract_from_timm(self, checkpoint_path: Path) -> pd.DataFrame: ...
    def aggregate_metadata(self, sources: list[Path]) -> pd.DataFrame: ...
    def validate_schema(self, df: pd.DataFrame) -> bool: ...
    def save_parquet(self, df: pd.DataFrame, output_path: Path): ...
```

### 3. CoverageAuditor (`src/audit.py`)

**Dependencies:** pandas, numpy

```python
class CoverageAuditor:
    def __init__(self, metadata_path: Path, min_samples: int = 30, coverage_threshold: float = 0.70): ...
    def compute_coverage_matrix(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def compute_coverage_percentage(self, matrix: pd.DataFrame) -> float: ...
    def validate_critical_cells(self, matrix: pd.DataFrame, critical_pairs: list[tuple]) -> dict: ...
    def identify_sparse_cells(self, matrix: pd.DataFrame) -> pd.Series: ...
    def save_matrix(self, matrix: pd.DataFrame, output_path: Path): ...
```

### 4. Visualizer (`src/visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
class Visualizer:
    def generate_heatmap(self, matrix: pd.DataFrame, output_path: Path, dpi: int = 300): ...
    def plot_architecture_distribution(self, df: pd.DataFrame, output_path: Path): ...
    def plot_task_distribution(self, df: pd.DataFrame, output_path: Path): ...
```

### 5. ReportGenerator (`src/report.py`)

**Dependencies:** pandas

```python
class ReportGenerator:
    def __init__(self, coverage_pct: float, matrix: pd.DataFrame, sparse_cells: pd.Series): ...
    def generate_summary_section(self) -> str: ...
    def generate_critical_cells_section(self, critical_coverage: dict) -> str: ...
    def generate_sparse_cells_section(self) -> str: ...
    def determine_gate_decision(self) -> str: ...
    def write_report(self, output_path: Path): ...
```

### 6. Configuration (`src/config.py`)

**Dependencies:** None (dataclass)

```python
@dataclass
class Config:
    cache_dir: str = "datasets/"
    output_dir: str = "outputs/"
    min_samples_per_cell: int = 30
    coverage_threshold: float = 0.70
    critical_cells: list[tuple] = field(default_factory=lambda: [
        ('CNN', 'CIFAR10'),
        ('ResNet', 'CIFAR100'),
        ('ResNet', 'TinyImageNet')
    ])
    zenodo_dois: dict = field(default_factory=dict)
    sane_zoos: list[str] = field(default_factory=list)
    
def load_config(path: str = "config.yaml") -> Config: ...
```

### 7. Pipeline Orchestrator (`main.py`)

**Dependencies:** All modules

```python
def main():
    config = load_config()
    
    # Step 1: Download
    downloader = DownloadManager(config.cache_dir)
    raw_paths = downloader.download_all(config.zenodo_dois, config.sane_zoos)
    
    # Step 2: Extract
    extractor = MetadataExtractor()
    metadata_df = extractor.aggregate_metadata(raw_paths)
    extractor.save_parquet(metadata_df, Path(config.output_dir) / "zoo_metadata.parquet")
    
    # Step 3: Audit
    auditor = CoverageAuditor(
        metadata_path=Path(config.output_dir) / "zoo_metadata.parquet",
        min_samples=config.min_samples_per_cell,
        coverage_threshold=config.coverage_threshold
    )
    matrix = auditor.compute_coverage_matrix(metadata_df)
    coverage_pct = auditor.compute_coverage_percentage(matrix)
    critical_coverage = auditor.validate_critical_cells(matrix, config.critical_cells)
    sparse_cells = auditor.identify_sparse_cells(matrix)
    auditor.save_matrix(matrix, Path(config.output_dir) / "coverage_matrix.csv")
    
    # Step 4: Visualize
    viz = Visualizer()
    viz.generate_heatmap(matrix, Path(config.output_dir) / "coverage_heatmap.png")
    
    # Step 5: Report
    report_gen = ReportGenerator(coverage_pct, matrix, sparse_cells)
    report_gen.write_report(Path(config.output_dir) / "h-e1_validation_report.md")
    
    # Gate decision
    decision = report_gen.determine_gate_decision()
    print(f"Gate Decision: {decision}")

if __name__ == "__main__":
    main()
```

---

## Data Flow

**Input:** Zenodo DOIs, modelzoos.cc zoo names, timm architecture list  
**Stage 1:** Download to `datasets/{modelzoo,sane,vit}/`  
**Stage 2:** Extract to `outputs/zoo_metadata.parquet` (schema: model_id, architecture, task, hyperparams, source, epoch, accuracy)  
**Stage 3:** Compute `outputs/coverage_matrix.csv` (rows=arch, cols=task, values=count)  
**Stage 4:** Generate `outputs/coverage_heatmap.png` (RdYlGn colormap)  
**Stage 5:** Write `outputs/h-e1_validation_report.md` (gate decision)

**Metadata Schema:**
```python
{
    'model_id': str,          # Unique identifier
    'architecture': str,      # {CNN, ResNet, ViT, MLP, RNN}
    'task': str,              # {MNIST, FMNIST, SVHN, USPS, CIFAR10, CIFAR100, TinyImageNet, EuroSAT, ImageNet}
    'hyperparams': dict,      # {optimizer, lr, batch_size, ...}
    'source': str,            # {ModelZooDataset, SANE, timm}
    'epoch': int,             # Training epoch
    'accuracy': float         # Validation accuracy
}
```

---

## File Structure

```
experiments/h-e1/
├── src/
│   ├── download.py       # DownloadManager
│   ├── extract.py        # MetadataExtractor
│   ├── audit.py          # CoverageAuditor
│   ├── visualize.py      # Visualizer
│   ├── report.py         # ReportGenerator
│   └── config.py         # Config dataclass
├── main.py               # Pipeline orchestrator
├── config.yaml           # User-editable configuration
├── environment.yml       # Conda dependencies
├── datasets/             # Downloaded zoos (gitignored)
│   ├── modelzoo/
│   ├── sane/
│   └── vit/
└── outputs/              # Generated artifacts
    ├── zoo_metadata.parquet
    ├── coverage_matrix.csv
    ├── coverage_heatmap.png
    └── h-e1_validation_report.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup | Project structure, config.yaml, environment.yml | 4 | 1+1+1+1 (dirs+config+env+gitignore) |
| E2 | Download | DownloadManager with zenodo/sane/timm, resume logic, checksum | 8 | 2+2+2+2 (zenodo+sane+timm+verify) |
| E3 | Extract | MetadataExtractor for 3 sources, schema validation, parquet | 9 | 3+3+2+1 (modelzoo+sane+timm+save) |
| E4 | Audit | CoverageAuditor matrix computation, critical cells, sparse analysis | 7 | 2+2+2+1 (matrix+critical+sparse+save) |
| E5 | Visualize | Heatmap generation with seaborn, architecture/task distributions | 5 | 3+1+1 (heatmap+arch+task) |
| E6 | Report | ReportGenerator gate logic, markdown formatting | 6 | 2+2+1+1 (summary+gate+sparse+write) |
| E7 | Integration | main.py orchestrator, end-to-end test, reproducibility check | 6 | 2+2+2 (pipeline+test+verify) |

**Distribution:** Low(4-8): [E1, E2, E4, E5, E6, E7], Medium(9-13): [E3]

**Total Complexity:** 45 (avg 6.4 per task)

---

## Implementation Notes

**ModelZooDataset Parsing:**
```python
# .pt files contain torch checkpoints
zoo = torch.load(zoo_path, map_location='cpu')
properties = zoo['properties']  # List of dicts with metadata
```

**SANE Parsing:**
```python
# JSON config files in preprocessed directories
config = json.load(open(zoo_path / "config.json"))
metadata = {
    'architecture': config['model']['type'],
    'task': config['dataset']['name'],
    ...
}
```

**timm Fallback:**
```python
# If ViTModelZoo unavailable, use timm registry
import timm
models = timm.list_models('vit_*', pretrained=True)
# Download and extract metadata from checkpoint
```

**Coverage Matrix Computation:**
```python
# pandas groupby + unstack for cross-tabulation
matrix = df.groupby(['architecture', 'task']).size().unstack(fill_value=0)
coverage_pct = (matrix >= min_samples).sum().sum() / matrix.size * 100
```

**Gate Decision Logic:**
```python
if coverage_pct >= 70:
    return "PASS"
elif coverage_pct >= 50 and all(critical_counts >= 30):
    return "PARTIAL (scope reduction acceptable)"
else:
    return "FAIL (insufficient data)"
```

**Download Resume:**
```python
# Skip existing files, use lockfiles to prevent corruption
if (output_path).exists() and (output_path / ".complete").exists():
    return output_path
# Otherwise download and touch .complete on success
```

---

## Dependencies

**Python 3.10:**
- torch 2.0 (metadata extraction from .pt)
- pandas 2.0 (groupby, parquet)
- numpy 1.24 (matrix operations)
- seaborn 0.12 (heatmap)
- matplotlib 3.7 (plotting backend)
- zenodo_get (Zenodo downloads)
- huggingface_hub (timm fallback)
- pyyaml (config parsing)

**No GPU required** - all operations CPU-only.

---

## Performance Targets

| Stage | Time | Constraint |
|-------|------|------------|
| Download | Variable | Network-bound, resume on failure |
| Extract | ≤4 hours | Single CPU core |
| Audit | ≤30 min | pandas groupby |
| Visualize | ≤10 min | matplotlib rendering |
| Report | <1 min | String formatting |
| **Total** | **≤6 hours** | Excluding downloads |

**Storage:** ≤350GB (200GB ModelZoo + 50GB SANE + 100GB ViT)

---

## Validation Checklist

**Metadata Quality:**
- [ ] No duplicate model_ids
- [ ] All architecture/task values in allowed taxonomy
- [ ] Invalid pairs flagged (ResNet-MNIST, CNN-ImageNet)
- [ ] <5% missing hyperparameters

**Coverage:**
- [ ] Matrix dimensions match expected (4-5 architectures × 9 tasks)
- [ ] Critical cells checked (CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet)
- [ ] Sparse cells documented

**Reproducibility:**
- [ ] Identical results on re-run (deterministic)
- [ ] Cached downloads not re-fetched
- [ ] Output files timestamped

---

**END OF ARCHITECTURE**
