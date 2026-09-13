# Architecture: H-M3 Orthogonal Signals Complementary Detection

**Applied**: Signal correlation + discordant-subset AUROC validation pattern (statistical analysis, no model inference)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (pure analysis script consuming H-M1/H-M2 JSON outputs)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Depends on file outputs of H-M1/H-M2 (not their code) — treated as data dependencies, not import dependencies.

---

## Data Flow

- `h-m1/results/entropy_scores.json` (817 entropy values + labels) → `load_scores()`
- `h-m2/results/consistency_scores.json` (817 consistency values) → `load_scores()`
- `load_scores()` → `compute_correlation()` → `correlation_analysis.json`
- `load_scores()` → `identify_discordant()` → `discordant_cases.csv`
- `identify_discordant()` + labels → `compute_subset_auroc()` → `subset_auroc.json`
- `load_scores()` + labels → `plot_scatter()` / `plot_quadrant()` → `results/figures/*.png`
- All results merged → `main()` → gate decision (primary/secondary pass) printed + saved

---

## Modules

### DataLoader (`orthogonality.py`)

**Dependencies**: None (reads JSON from H-M1/H-M2 result paths, config.yaml for paths)

```python
def load_scores(h_m1_results_path: str, h_m2_results_path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (entropy[817], consistency[817], labels[817])"""
```

### CorrelationAnalyzer (`orthogonality.py`)

**Dependencies**: DataLoader output

```python
def compute_correlation(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Returns {pearson_r, pearson_p, spearman_r, spearman_p, primary_pass}"""
```

### DiscordantIdentifier (`orthogonality.py`)

**Dependencies**: DataLoader output

```python
def identify_discordant(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Returns {discordant_mask, high_entropy_only, high_inconsistency_only,
                discordant_proportion, n_discordant}"""
```

### SubsetAUROCAnalyzer (`orthogonality.py`)

**Dependencies**: DiscordantIdentifier output, labels

```python
def compute_subset_auroc(entropy: np.ndarray, consistency: np.ndarray,
                          labels: np.ndarray, disc: dict) -> dict:
    """Returns {auroc_entropy_subset?, n_entropy_subset?,
                auroc_consistency_subset?, n_consistency_subset?}
    Keys omitted if subset size < 50."""
```

### Visualizer (`orthogonality.py`)

**Dependencies**: DataLoader output, DiscordantIdentifier output

```python
def plot_scatter(entropy: np.ndarray, consistency: np.ndarray, labels: np.ndarray, output_path: str) -> None: ...
def plot_quadrant(entropy: np.ndarray, consistency: np.ndarray, labels: np.ndarray, disc: dict, output_path: str) -> None: ...
```

### ResultsWriter (`orthogonality.py`)

**Dependencies**: All analyzer outputs

```python
def save_discordant_csv(disc: dict, output_path: str) -> None:
    """Writes question_id, discordant, high_entropy_only, high_inconsistency_only columns"""

def evaluate_gate(corr: dict, disc: dict, subset: dict) -> dict:
    """Returns {primary_pass, secondary_pass} per PRD Section 6 thresholds"""
```

### Orchestrator (`orthogonality.py`)

```python
def main() -> None:
    """Loads config.yaml, runs full pipeline, writes all results/ files, prints gate decision"""
```

### Config (`config.yaml`)

```yaml
paths:
  h_m1_results: ../h-m1/results/entropy_scores.json
  h_m2_results: ../h-m2/results/consistency_scores.json
  output_dir: results/
thresholds:
  discordant_rank_diff: 0.5
  correlation_primary: 0.3
  discordant_proportion: 0.15
  subset_auroc: 0.6
  min_subset_size: 50
seed: 42
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + I/O setup | config.yaml, load_scores(), results/ dir creation | Low | 2+1+1+1 |
| A-2 | Correlation analysis | compute_correlation() with Pearson/Spearman + primary gate | Medium | 2+1+3+2 |
| A-3 | Rank normalization + discordant ID | identify_discordant() with percentile ranks | Medium | 3+2+3+2 |
| A-4 | Subset AUROC | compute_subset_auroc() with min-size guard | Medium | 2+2+3+2 |
| A-5 | Discordant CSV export | save_discordant_csv() with question_id mapping | Low | 2+1+1+2 |
| A-6 | Scatter visualization | plot_scatter() colored by correctness | Low | 2+1+2+1 |
| A-7 | Quadrant visualization | plot_quadrant() with median-split quadrants | Medium | 3+1+3+2 |
| A-8 | Gate evaluation + orchestration | evaluate_gate(), main() pipeline wiring, JSON output | Medium | 3+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-7, A-8], Low(4-8): [A-1, A-5, A-6]

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-M1/H-M2 Outputs)

| Data | Path | Format |
|------|------|--------|
| Entropy scores + labels | `h-m1/results/entropy_scores.json` | `{"entropy_scores": float[817], "labels": bool[817]}` |
| Consistency scores | `h-m2/results/consistency_scores.json` | `{"consistency_scores": float[817]}` |

**Note**: These are data dependencies (JSON files), not code imports — H-M3 does not call H-M1/H-M2 modules directly. No Serena analysis needed since no code is reused, only data files.
