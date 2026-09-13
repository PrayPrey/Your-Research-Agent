# Logic Specifications: Dataset Coverage Audit (H-E1)

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Phase:** Phase 3 (Logic Design)  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing coverage audit code  
**Analyzed Path**: experiments/h_e1/src/  
**Relevant Symbols**: None - designing new APIs

---

## L-1: Metadata Extraction [Complexity: 3, Budget: 5]

**Applied**: Standard PyTorch torch.load + pandas DataFrame construction

### API Signatures

```python
def extract_modelzoo_metadata(zoo_path: Path) -> pd.DataFrame:
    """Extract metadata from ModelZooDataset .pt file.
    
    Returns: DataFrame with columns [model_id, architecture, task, hyperparams, source, epoch, accuracy]
    """
    ...

def extract_sane_metadata(zoo_path: Path) -> pd.DataFrame:
    """Extract metadata from SANE JSON config.
    
    Returns: DataFrame with columns [model_id, architecture, task, hyperparams, source, epoch, accuracy]
    """
    ...

def extract_vit_metadata(zoo_path: Path) -> pd.DataFrame:
    """Extract metadata from ViT zoo or timm fallback.
    
    Returns: DataFrame with columns [model_id, architecture, task, hyperparams, source, epoch, accuracy]
    """
    ...

def aggregate_metadata(dataset_root: Path) -> pd.DataFrame:
    """Aggregate all zoo metadata into unified Parquet.
    
    Args:
        dataset_root: Root directory containing modelzoo/, sane/, vit/ subdirs
    
    Returns: Combined DataFrame ~55-60K rows
    """
    ...
```

### Tensor Shapes

```python
# DataFrame schema (N rows, 7 columns):
# model_id: str          - Unique identifier "{zoo_name}_{idx}"
# architecture: str      - {CNN, ResNet, ViT, MLP, RNN}
# task: str              - {MNIST, FMNIST, SVHN, USPS, CIFAR10, CIFAR100, TinyImageNet, EuroSAT, ImageNet}
# hyperparams: dict      - JSON blob {lr, optimizer, epochs, ...}
# source: str            - {ModelZooDataset, SANE, ViTModelZoo, huggingface}
# epoch: int             - Training checkpoint epoch
# accuracy: float        - Test accuracy at epoch

# Expected: N ≈ 55000-60000
```

### Pseudo-code

```python
def extract_modelzoo_metadata(zoo_path):
    zoo = torch.load(zoo_path)
    rows = []
    for idx, props in enumerate(zoo['properties']):
        rows.append({
            'model_id': f"{zoo_path.stem}_{idx}",
            'architecture': normalize_arch(props.get('architecture', 'CNN')),
            'task': normalize_task(props.get('dataset', 'unknown')),
            'hyperparams': props.get('hyperparams', {}),
            'source': 'ModelZooDataset',
            'epoch': props.get('epoch', -1),
            'accuracy': props.get('test_acc', 0.0)
        })
    return pd.DataFrame(rows)

def aggregate_metadata(dataset_root):
    all_dfs = []
    # ModelZooDataset
    for pt_file in (dataset_root / "modelzoo").glob("**/*.pt"):
        all_dfs.append(extract_modelzoo_metadata(pt_file))
    # SANE
    for json_file in (dataset_root / "sane").glob("**/*.json"):
        all_dfs.append(extract_sane_metadata(json_file))
    # ViT (with fallback)
    if (dataset_root / "vit").exists():
        for vit_file in (dataset_root / "vit").glob("**/*"):
            all_dfs.append(extract_vit_metadata(vit_file))
    
    df = pd.concat(all_dfs, ignore_index=True)
    # Validate: no duplicate model_ids
    assert df['model_id'].is_unique, "Duplicate model_ids detected"
    # Cross-validate architecture-task pairs
    invalid = df[(df['architecture'] == 'ResNet') & (df['task'] == 'MNIST')]
    if len(invalid) > 0:
        warnings.warn(f"{len(invalid)} invalid pairs (ResNet-MNIST)")
    
    df.to_parquet(dataset_root / "zoo_metadata.parquet", index=False)
    return df
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | ModelZooDataset parser | Parse .pt files, extract properties dict |
| L-1-2 | SANE parser | Parse JSON configs, map to unified schema |
| L-1-3 | ViT parser | Parse ViT zoo or timm checkpoints |
| L-1-4 | Schema validation | Check required fields, validate types |
| L-1-5 | Parquet export | Write indexed DataFrame to disk |

---

## L-2: Coverage Computation [Complexity: 2, Budget: 3]

**Applied**: pandas groupby().size().unstack() pattern

### API Signatures

```python
def compute_coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute architecture × task contingency table.
    
    Args:
        df: Metadata DataFrame with [architecture, task] columns
    
    Returns: Contingency table (A rows × T columns), values = model counts
    """
    ...

def compute_coverage_percentage(matrix: pd.DataFrame, threshold: int = 30) -> float:
    """Compute coverage percentage.
    
    Args:
        matrix: Coverage matrix from compute_coverage_matrix()
        threshold: Minimum models per cell (default 30)
    
    Returns: Percentage of cells with ≥threshold models
    """
    ...
```

### Tensor Shapes

```python
# Coverage matrix (A × T):
# A = number of architectures (expected ~4-5)
# T = number of tasks (expected ~9)
# Values: int (model count per cell)

# Example:
#              MNIST  FMNIST  CIFAR10  CIFAR100  TinyImageNet  ...
# CNN            500     400      800       300           200
# ResNet          20      50      600       450           350
# ViT              0       0       30        20            80
# MLP            100      80       50        30            10
```

### Pseudo-code

```python
def compute_coverage_matrix(df):
    # Group by (architecture, task), count models
    matrix = df.groupby(['architecture', 'task']).size().unstack(fill_value=0)
    matrix.to_csv("coverage_matrix.csv")
    return matrix

def compute_coverage_percentage(matrix, threshold=30):
    sufficient_mask = matrix >= threshold
    total_cells = matrix.size
    sufficient_cells = sufficient_mask.sum().sum()
    coverage_pct = (sufficient_cells / total_cells) * 100
    return coverage_pct
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Groupby aggregation | df.groupby(['architecture', 'task']).size() |
| L-2-2 | Coverage calculation | (cells ≥ threshold) / total_cells × 100 |
| L-2-3 | CSV export | matrix.to_csv() |

---

## L-3: Critical Cell Validation [Complexity: 1, Budget: 2]

**Applied**: Simple DataFrame indexing with .loc[]

### API Signatures

```python
def validate_critical_cells(
    matrix: pd.DataFrame,
    critical_cells: List[Tuple[str, str]],
    threshold: int = 30
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Validate critical architecture-task cells.
    
    Args:
        matrix: Coverage matrix (A × T)
        critical_cells: List of (architecture, task) tuples to check
        threshold: Minimum model count (default 30)
    
    Returns: {(arch, task): {'count': int, 'pass': bool}}
    """
    ...
```

### Pseudo-code

```python
def validate_critical_cells(matrix, critical_cells, threshold=30):
    results = {}
    for arch, task in critical_cells:
        # Check if cell exists
        if arch in matrix.index and task in matrix.columns:
            count = matrix.loc[arch, task]
        else:
            count = 0  # Missing cell
        
        results[(arch, task)] = {
            'count': count,
            'pass': count >= threshold
        }
    return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Cell lookup | matrix.loc[arch, task] with existence check |
| L-3-2 | Threshold validation | count >= threshold per cell |

---

## L-4: Gate Decision Logic [Complexity: 1, Budget: 2]

**Applied**: Conditional branching with coverage + critical cell checks

### API Signatures

```python
def make_gate_decision(
    coverage_pct: float,
    critical_results: Dict[Tuple[str, str], Dict[str, Any]]
) -> str:
    """Determine gate decision (PASS/PARTIAL/FAIL).
    
    Args:
        coverage_pct: Overall coverage percentage
        critical_results: Critical cell validation results from L-3
    
    Returns: Gate decision {"PASS", "PARTIAL", "FAIL"}
    """
    ...
```

### Pseudo-code

```python
def make_gate_decision(coverage_pct, critical_results):
    all_critical_pass = all(cell['pass'] for cell in critical_results.values())
    
    if coverage_pct >= 70:
        return "PASS"
    elif 50 <= coverage_pct < 70 and all_critical_pass:
        return "PARTIAL"
    else:
        return "FAIL"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Coverage threshold check | IF ≥70% PASS, ELIF 50-70% check critical |
| L-4-2 | Critical cell aggregation | all(cell['pass'] for cell in results) |

---

## L-5: Sparse Cell Analysis [Complexity: 1, Budget: 2]

**Applied**: DataFrame filtering + sorting

### API Signatures

```python
def identify_sparse_cells(
    matrix: pd.DataFrame,
    threshold: int = 30
) -> pd.Series:
    """Identify and sort sparse cells.
    
    Args:
        matrix: Coverage matrix (A × T)
        threshold: Sparse threshold (default 30)
    
    Returns: Series of (architecture, task): count, sorted ascending
    """
    ...
```

### Pseudo-code

```python
def identify_sparse_cells(matrix, threshold=30):
    # Filter cells < threshold
    sparse_mask = matrix < threshold
    sparse_cells = matrix[sparse_mask].stack()
    # Sort by count (ascending)
    sparse_cells = sparse_cells.sort_values()
    return sparse_cells
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Sparse filtering | matrix[matrix < threshold].stack() |
| L-5-2 | Ascending sort | .sort_values() by count |

---

## L-6: Visualization [Complexity: 2, Budget: 3]

**Applied**: seaborn.heatmap with annotations

### API Signatures

```python
def generate_heatmap(
    matrix: pd.DataFrame,
    output_path: Path,
    dpi: int = 300
) -> None:
    """Generate coverage heatmap.
    
    Args:
        matrix: Coverage matrix (A × T)
        output_path: PNG save path
        dpi: Resolution (default 300)
    """
    ...
```

### Pseudo-code

```python
def generate_heatmap(matrix, output_path, dpi=300):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        matrix,
        annot=True,       # Show counts in cells
        fmt='d',          # Integer format
        cmap='RdYlGn',    # Red (low) to green (high)
        vmin=0,
        vmax=100,
        linewidths=0.5,
        ax=ax
    )
    ax.set_title("Architecture-Task Coverage Matrix")
    ax.set_xlabel("Task")
    ax.set_ylabel("Architecture")
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Heatmap generation | sns.heatmap() with annotations |
| L-6-2 | Colormap config | RdYlGn (red: 0-29, yellow: 30-99, green: ≥100) |
| L-6-3 | PNG export | plt.savefig() at 300 DPI |

---

## L-7: Report Generation [Complexity: 2, Budget: 3]

**Applied**: Template-based Markdown generation

### API Signatures

```python
def generate_validation_report(
    coverage_pct: float,
    matrix: pd.DataFrame,
    critical_results: Dict[Tuple[str, str], Dict[str, Any]],
    sparse_cells: pd.Series,
    gate_decision: str,
    output_path: Path
) -> None:
    """Generate validation report.
    
    Args:
        coverage_pct: Overall coverage percentage
        matrix: Coverage matrix (A × T)
        critical_results: Critical cell validation results
        sparse_cells: Sparse cell Series from L-5
        gate_decision: Gate decision from L-4
        output_path: Markdown file path
    """
    ...
```

### Pseudo-code

```python
def generate_validation_report(coverage_pct, matrix, critical_results, sparse_cells, gate_decision, output_path):
    with open(output_path, 'w') as f:
        f.write("# h-e1 Validation Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
        
        # Coverage Summary
        f.write("## Coverage Summary\n\n")
        f.write(f"**Overall Coverage**: {coverage_pct:.1f}%\n")
        f.write(f"**Total Cells**: {matrix.size}\n")
        f.write(f"**Sufficient Cells (≥30)**: {(matrix >= 30).sum().sum()}\n\n")
        
        # Critical Cells
        f.write("## Critical Cells\n\n")
        for (arch, task), result in critical_results.items():
            status = "PASS" if result['pass'] else "FAIL"
            f.write(f"- **{arch}-{task}**: {result['count']} models [{status}]\n")
        
        # Sparse Cells
        f.write("\n## Sparse Cells\n\n")
        for (arch, task), count in sparse_cells.items():
            f.write(f"- {arch}-{task}: {count} models\n")
        
        # Gate Decision
        f.write("\n## Gate Decision\n\n")
        f.write(f"**Verdict**: {gate_decision}\n\n")
        if gate_decision == "PASS":
            f.write("Proceed to Phase 1 (H-M-integrated CKA feasibility gate).\n")
        elif gate_decision == "PARTIAL":
            f.write("Scope reduction acceptable. Restrict to well-covered cells.\n")
        else:
            f.write("Insufficient coverage. ABORT Phase 1.\n")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Template rendering | Write sections: summary, critical, sparse, gate |
| L-7-2 | Table formatting | Markdown tables for critical/sparse cells |
| L-7-3 | File export | Write to .md file |

---

## Edge Cases and Error Handling

### E-1: Missing Architecture/Task Pairs

**Scenario**: Architecture exists in metadata but not in taxonomy (e.g., "DenseNet")

**Handling**:
```python
def normalize_arch(arch_str):
    arch_map = {
        'cnn': 'CNN', 'conv': 'CNN',
        'resnet': 'ResNet', 'resnet18': 'ResNet',
        'vit': 'ViT', 'transformer': 'ViT',
        'mlp': 'MLP', 'fc': 'MLP'
    }
    normalized = arch_map.get(arch_str.lower(), 'Unknown')
    if normalized == 'Unknown':
        warnings.warn(f"Unknown architecture: {arch_str}")
    return normalized
```

### E-2: Corrupt Metadata Files

**Scenario**: torch.load() fails on corrupted .pt file

**Handling**:
```python
def extract_modelzoo_metadata(zoo_path):
    try:
        zoo = torch.load(zoo_path, weights_only=False)
    except Exception as e:
        logging.error(f"Failed to load {zoo_path}: {e}")
        return pd.DataFrame()  # Return empty DataFrame
    ...
```

### E-3: Duplicate model_ids

**Scenario**: Two zoos use same naming scheme, causing ID collision

**Handling**:
```python
def aggregate_metadata(dataset_root):
    df = pd.concat(all_dfs, ignore_index=True)
    # Detect duplicates
    duplicates = df[df['model_id'].duplicated()]
    if len(duplicates) > 0:
        # Make unique by appending source
        df['model_id'] = df['model_id'] + '_' + df['source']
        assert df['model_id'].is_unique, "Still have duplicates after fix"
```

### E-4: Critical Cell Missing

**Scenario**: Critical cell (CNN-CIFAR10) not present in matrix (impossible but defensive)

**Handling**:
```python
def validate_critical_cells(matrix, critical_cells, threshold=30):
    for arch, task in critical_cells:
        if arch not in matrix.index or task not in matrix.columns:
            logging.warning(f"Critical cell {arch}-{task} missing from matrix")
            results[(arch, task)] = {'count': 0, 'pass': False}
```

### E-5: All Cells Sparse

**Scenario**: Coverage = 0% (dataset download failure)

**Handling**:
```python
def compute_coverage_percentage(matrix, threshold=30):
    if matrix.empty:
        raise RuntimeError("Coverage matrix is empty - no metadata extracted")
    coverage_pct = ...
    if coverage_pct == 0:
        raise RuntimeError("Zero coverage - verify dataset downloads")
```

---

## Task Allocation Summary

| Task | Complexity | Budget | Used | Remaining |
|------|------------|--------|------|-----------|
| L-1 | 3 | 5 | 5 | 0 |
| L-2 | 2 | 3 | 3 | 0 |
| L-3 | 1 | 2 | 2 | 0 |
| L-4 | 1 | 2 | 2 | 0 |
| L-5 | 1 | 2 | 2 | 0 |
| L-6 | 2 | 3 | 3 | 0 |
| L-7 | 2 | 3 | 3 | 0 |
| **Total** | **12** | **20** | **20** | **0** |

---

## Dependencies and Assumptions

### External Dependencies

- **PyTorch 2.0**: For torch.load() .pt file parsing
- **pandas 2.0**: For DataFrame operations, groupby, Parquet I/O
- **seaborn 0.12**: For heatmap visualization
- **matplotlib 3.7**: For figure generation

### Assumptions

1. **ModelZooDataset format**: .pt files with `zoo['properties']` dict
2. **SANE format**: JSON config files with task/architecture fields
3. **ViT fallback**: timm library if ViTModelZoo unavailable
4. **Critical cells**: Hardcoded list (CNN-CIFAR10, ResNet-CIFAR100, ResNet-TinyImageNet)
5. **Threshold n=30**: Based on bootstrap power analysis (80% power, Cohen's d=0.5)

---

**END OF LOGIC SPECIFICATIONS**
