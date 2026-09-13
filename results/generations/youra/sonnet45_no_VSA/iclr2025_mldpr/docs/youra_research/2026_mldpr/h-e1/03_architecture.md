# System Architecture: H-E1 - Documentation Gap Validation Study

**Date:** 2026-07-12  
**Hypothesis:** H-E1 (EXISTENCE - FOUNDATION)  
**Type:** Observational Study (Data Collection + Statistical Analysis)  
**Author:** Architecture Agent  
**Status:** DRAFT v1.0  

---

## Applied Patterns

**Applied:** Data Pipeline Pattern (ETL for observational studies)

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing codebase - first implementation of temporal documentation measurement study.

---

## System Overview

This architecture supports a 5-stage observational study pipeline:
1. Repository Sampling (HuggingFace Hub API)
2. T0 Detection (3-tier fallback via GitHub API)
3. Repository Cloning (snapshot at T0 + 90 days)
4. DCS Coding (manual human assessment)
5. Statistical Analysis (binomial proportion + chi-square)

**Technology Stack:**
- Python 3.9+
- HuggingFace Hub API (`huggingface_hub`)
- GitHub API (`PyGithub`)
- Statistical libraries (`scipy`, `statsmodels`, `sklearn`)
- Visualization (`matplotlib`)

---

## Module Structure

### Sampling Module (`src/sampling.py`)

**Dependencies:** `huggingface_hub`, `pandas`

```python
class RepositorySampler:
    def __init__(self, api_token: Optional[str] = None, random_seed: int = 42): ...
    
    def fetch_datasets(self, start_date: str, end_date: str, min_stars: int) -> pd.DataFrame: ...
    
    def stratify_by_year(self, df: pd.DataFrame, n_per_year: int) -> pd.DataFrame: ...
    
    def export_sample(self, df: pd.DataFrame, output_path: str) -> None: ...
```

---

### T0 Detection Module (`src/t0_detection.py`)

**Dependencies:** `PyGithub`, `pandas`, `datetime`

```python
class T0Detector:
    def __init__(self, github_token: str): ...
    
    def detect_t0_tier1(self, repo_id: str) -> Optional[Tuple[datetime, str]]: ...
    
    def detect_t0_tier2(self, repo_id: str) -> Optional[Tuple[datetime, str]]: ...
    
    def detect_t0_tier3(self, repo_id: str) -> Tuple[datetime, str]: ...
    
    def detect_t0_three_tier(self, repo_id: str) -> Tuple[datetime, str]: ...
    
    def get_commit_at_date(self, repo_id: str, target_date: datetime) -> str: ...
```

---

### Cloning Module (`src/cloning.py`)

**Dependencies:** `huggingface_hub`, `pathlib`

```python
class RepositoryCloner:
    def __init__(self, base_dir: str = "./data/repos"): ...
    
    def clone_at_revision(self, repo_id: str, commit_sha: str) -> Path: ...
    
    def verify_clone(self, repo_path: Path) -> bool: ...
    
    def extract_documentation_files(self, repo_path: Path) -> Dict[str, bool]: ...
```

---

### DCS Coding Module (`src/dcs_coding.py`)

**Dependencies:** `pandas`, `pathlib`

```python
class DCSCoder:
    def __init__(self): ...
    
    def create_coding_template(self, repo_ids: List[str], output_path: str) -> None: ...
    
    def load_coding_results(self, coding_file: str) -> pd.DataFrame: ...
    
    def calculate_dcs_total(self, row: pd.Series) -> float: ...
    
    def determine_compliance(self, dcs_total: float, threshold: float = 2.4) -> bool: ...
```

---

### Statistical Analysis Module (`src/statistics.py`)

**Dependencies:** `scipy`, `statsmodels`, `sklearn`, `numpy`, `pandas`

```python
class StatisticalAnalyzer:
    def __init__(self): ...
    
    def calculate_compliance_rate(self, df: pd.DataFrame) -> Tuple[float, float, float]: ...
    
    def component_breakdown_chi2(self, df: pd.DataFrame) -> Tuple[float, float, List[int]]: ...
    
    def calculate_irr(self, coder1_df: pd.DataFrame, coder2_df: pd.DataFrame) -> Dict[str, float]: ...
    
    def check_gate_criteria(self, ci_upper: float, chi2_p: float, kappa: float) -> Dict[str, bool]: ...
```

---

### Visualization Module (`src/visualization.py`)

**Dependencies:** `matplotlib`, `pandas`, `numpy`

```python
class Visualizer:
    def __init__(self, output_dir: str = "./figures"): ...
    
    def plot_compliance_rate(self, observed: float, ci_lower: float, ci_upper: float) -> None: ...
    
    def plot_component_breakdown(self, df: pd.DataFrame) -> None: ...
    
    def plot_t0_detection_breakdown(self, df: pd.DataFrame) -> None: ...
    
    def plot_dcs_distribution(self, df: pd.DataFrame) -> None: ...
```

---

### Pipeline Orchestrator (`src/pipeline.py`)

**Dependencies:** All modules above

```python
class StudyPipeline:
    def __init__(self, config: dict): ...
    
    def run_sampling_phase(self) -> pd.DataFrame: ...
    
    def run_t0_detection_phase(self, sample_df: pd.DataFrame) -> pd.DataFrame: ...
    
    def run_cloning_phase(self, t0_df: pd.DataFrame) -> pd.DataFrame: ...
    
    def run_manual_coding_phase(self) -> str: ...
    
    def run_analysis_phase(self, coding_df: pd.DataFrame, dual_coded_df: pd.DataFrame) -> Dict: ...
    
    def run_full_pipeline(self) -> Dict: ...
```

---

## File Organization

```
/workspace/TEST_mldpr/
├── docs/youra_research/h-e1/
│   ├── 02b_verification_plan.md
│   ├── 02c_experiment_brief.md
│   ├── 03_prd.md
│   ├── 03_architecture.md (this file)
│   └── figures/
│       ├── compliance_rate.png
│       ├── component_breakdown.png
│       ├── t0_detection_breakdown.png
│       └── dcs_distribution.png
├── src/
│   ├── __init__.py
│   ├── sampling.py
│   ├── t0_detection.py
│   ├── cloning.py
│   ├── dcs_coding.py
│   ├── statistics.py
│   ├── visualization.py
│   ├── pipeline.py
│   └── config.py
├── data/
│   ├── sampled_repositories.csv
│   ├── t0_detection_results.csv
│   ├── dcs_coding_results.csv
│   ├── dcs_dual_coded_sample.csv
│   └── repos/
│       ├── {repo_id_1}/
│       ├── {repo_id_2}/
│       └── ...
├── notebooks/
│   └── manual_coding_template.xlsx
├── tests/
│   ├── test_sampling.py
│   ├── test_t0_detection.py
│   └── test_statistics.py
├── requirements.txt
├── README.md
└── main.py
```

---

## Configuration (`src/config.py`)

```python
class StudyConfig:
    SAMPLING_CONFIG: Dict = {
        "start_date": "2022-01-01",
        "end_date": "2024-12-31",
        "min_stars": 10,
        "sample_size": 120,
        "n_per_year": 40,
        "random_seed": 42
    }
    
    T0_DETECTION_CONFIG: Dict = {
        "dataset_commit_patterns": ["add dataset", "upload data", "initial commit"],
        "tier1_preference": True,
        "tier2_fallback": True,
        "tier3_last_resort": True
    }
    
    CLONING_CONFIG: Dict = {
        "base_dir": "./data/repos",
        "t0_offset_days": 90,
        "verify_readme": True
    }
    
    DCS_CODING_CONFIG: Dict = {
        "threshold": 2.4,
        "components": ["data_context", "preprocessing", "licensing"],
        "dual_code_percentage": 0.20
    }
    
    STATISTICAL_CONFIG: Dict = {
        "alpha": 0.05,
        "ci_method": "wilson",
        "h0_threshold": 0.70,
        "h1_prediction": 0.40,
        "gate_threshold": 0.60,
        "irr_threshold": 0.70
    }
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Collection Pipeline | Implement sampling + T0 detection + cloning | 15 | Module:4, Deps:4, Algo:3, Integ:4 |
| E-2 | Manual Coding Infrastructure | Create DCS coding template + IRR protocol | 9 | Module:2, Deps:2, Algo:2, Integ:3 |
| E-3 | Statistical Analysis Engine | Implement proportion test + chi-square + IRR | 12 | Module:3, Deps:3, Algo:4, Integ:2 |
| E-4 | Visualization Suite | Generate 4 required figures | 8 | Module:2, Deps:2, Algo:2, Integ:2 |
| E-5 | Pipeline Orchestration | Integrate modules + error handling | 11 | Module:3, Deps:3, Algo:2, Integ:3 |
| E-6 | Quality Validation | Implement gate checks + verification | 9 | Module:2, Deps:2, Algo:3, Integ:2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-1], Medium(9-13): [E-2, E-3, E-5, E-6], Low(4-8): [E-4]

**Total Complexity**: 64 points (EXISTENCE/LIGHT tier: target 40-80)

---

## Epic Task Breakdown

### E-1: Data Collection Pipeline (Complexity: 15)

**Modules:**
- `sampling.py` (RepositorySampler class)
- `t0_detection.py` (T0Detector class)
- `cloning.py` (RepositoryCloner class)

**Deliverables:**
- Sampled repositories CSV (N=120, stratified by year)
- T0 detection results CSV (T0 timestamp, method tier, commit SHA)
- Cloned repository directories (N=100+, at T0+90 days revision)

**Acceptance Criteria:**
- T0 detection success rate ≥ 95%
- Repository cloning success rate ≥ 98%
- All CSV files include required columns (repo_id, t0, t0_method, commit_sha)

**Complexity Breakdown:**
- Module_Size: 4 (3 classes, ~600 LOC total)
- Dependencies: 4 (huggingface_hub, PyGithub, pandas, datetime)
- Algorithm: 3 (3-tier fallback logic, stratified sampling)
- Integration: 4 (HuggingFace API + GitHub API + file I/O)

---

### E-2: Manual Coding Infrastructure (Complexity: 9)

**Modules:**
- `dcs_coding.py` (DCSCoder class)
- Excel template generation

**Deliverables:**
- Coding template spreadsheet (100 rows, 3 component columns)
- Dual-coded sample template (20 rows × 2 coders)
- CSV loader for completed coding results

**Acceptance Criteria:**
- Template includes all DCS rubric components (0/0.5/1.0 options)
- Instructions embedded in template header
- Automatic DCS_3 total calculation formula

**Complexity Breakdown:**
- Module_Size: 2 (1 class + template generator, ~200 LOC)
- Dependencies: 2 (pandas, openpyxl)
- Algorithm: 2 (template generation, simple scoring logic)
- Integration: 3 (file export + human coding workflow)

---

### E-3: Statistical Analysis Engine (Complexity: 12)

**Modules:**
- `statistics.py` (StatisticalAnalyzer class)

**Deliverables:**
- Compliance rate with 95% Wilson CI
- Component breakdown chi-square test
- Inter-rater reliability (Cohen's kappa)
- Gate pass/fail determination

**Acceptance Criteria:**
- Primary criterion: CI upper bound < 60% (gate check)
- Secondary criterion: χ² p < 0.05 (non-uniform components)
- Quality gate: κ ≥ 0.70 (IRR validation)

**Complexity Breakdown:**
- Module_Size: 3 (1 class with 4 analysis methods, ~300 LOC)
- Dependencies: 3 (scipy, statsmodels, sklearn)
- Algorithm: 4 (binomial CI, chi-square, Cohen's kappa, gate logic)
- Integration: 2 (reads coding CSVs, outputs results dict)

---

### E-4: Visualization Suite (Complexity: 8)

**Modules:**
- `visualization.py` (Visualizer class)

**Deliverables:**
- Compliance rate bar chart (with CI error bars)
- Component breakdown stacked bar chart
- T0 detection method pie chart
- DCS distribution histogram

**Acceptance Criteria:**
- All 4 figures saved to `figures/` directory
- Compliance rate chart includes H0/H1 reference lines
- DCS histogram shows 2.4 threshold line

**Complexity Breakdown:**
- Module_Size: 2 (1 class with 4 plot methods, ~250 LOC)
- Dependencies: 2 (matplotlib, numpy)
- Algorithm: 2 (data aggregation for plots, standard chart types)
- Integration: 2 (reads analysis results, saves PNG files)

---

### E-5: Pipeline Orchestration (Complexity: 11)

**Modules:**
- `pipeline.py` (StudyPipeline class)
- `config.py` (StudyConfig dataclass)
- `main.py` (entry point)

**Deliverables:**
- Full pipeline runner (5 phases: sampling → T0 → cloning → coding → analysis)
- Error handling and logging
- Progress tracking and checkpoints

**Acceptance Criteria:**
- Pipeline can resume from any completed phase
- All intermediate CSVs saved for reproducibility
- Error logs capture API failures and rate limit issues

**Complexity Breakdown:**
- Module_Size: 3 (orchestrator class + config + main, ~400 LOC)
- Dependencies: 3 (all module imports + logging)
- Algorithm: 2 (sequential phase execution, checkpoint logic)
- Integration: 3 (coordinates 6 modules + file I/O)

---

### E-6: Quality Validation (Complexity: 9)

**Modules:**
- Test suite (`tests/`)
- Gate check validation

**Deliverables:**
- Unit tests for sampling, T0 detection, statistics
- Integration test for full pipeline (mock data)
- Gate criteria verification logic

**Acceptance Criteria:**
- Test coverage ≥ 80% for critical modules
- Gate check correctly identifies pass/fail conditions
- Validation report generated for Phase 4

**Complexity Breakdown:**
- Module_Size: 2 (3 test files, ~300 LOC)
- Dependencies: 2 (pytest, unittest.mock)
- Algorithm: 3 (gate logic validation, mock data generation)
- Integration: 2 (tests all module interfaces)

---

## Data Flow

**Phase 1: Sampling**
```
HuggingFace Hub API → RepositorySampler → sampled_repositories.csv
```

**Phase 2: T0 Detection**
```
sampled_repositories.csv → T0Detector (GitHub API) → t0_detection_results.csv
```

**Phase 3: Cloning**
```
t0_detection_results.csv → RepositoryCloner → data/repos/{repo_id}/
```

**Phase 4: Manual Coding**
```
data/repos/ → DCSCoder (template) → Human Coder → dcs_coding_results.csv
data/repos/ (20% sample) → Dual Coding → dcs_dual_coded_sample.csv
```

**Phase 5: Analysis**
```
dcs_coding_results.csv → StatisticalAnalyzer → results_dict
dcs_dual_coded_sample.csv → IRR Calculation → kappa scores
results_dict → Visualizer → figures/*.png
```

---

## External Dependencies

### APIs
- **HuggingFace Hub API**: Repository metadata, snapshot downloads
  - Authentication: Optional (public datasets)
  - Rate limit: No strict limit for list operations
- **GitHub API**: Commit history, tags, temporal data
  - Authentication: Required (Personal Access Token)
  - Rate limit: 5000 requests/hour

### Python Libraries

```
huggingface-hub>=0.17.0
PyGithub>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
statsmodels>=0.14.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
openpyxl>=3.1.0
pytest>=7.4.0
```

---

## Risk Mitigation in Architecture

### R3: T0 Detection Failure
- **Mitigation**: 3-tier fallback logic in `T0Detector`
- **Oversample**: N=120 (target N=100)
- **Validation**: Track tier usage distribution

### R5: Inter-Rater Disagreement
- **Mitigation**: Dual-code 20% sample, IRR calculation in `StatisticalAnalyzer`
- **Quality gate**: κ ≥ 0.70 required before proceeding

### R6: API Rate Limits
- **Mitigation**: Exponential backoff in `T0Detector` and `RepositoryCloner`
- **Logging**: Track API call counts and timestamps

---

## Quality Gates

### Pre-Analysis Gates
1. **T0 Detection Success**: ≥95% (E-1 validation)
2. **Cloning Success**: ≥98% (E-1 validation)
3. **Manual Coding Complete**: 100% of cloned repos (E-2 validation)

### Analysis Gates
4. **IRR Quality**: κ ≥ 0.70 (E-3 validation)
5. **Primary Gate**: CI upper bound < 60% (E-3 MUST_WORK)
6. **Secondary Gate**: χ² p < 0.05 (E-3 supporting evidence)

---

## Success Metrics

### Pipeline Metrics
- Total runtime: ≤4 hours (excluding manual coding)
- Data completeness: 100% of required CSVs generated
- Error rate: <5% for automated phases

### Research Metrics
- Compliance rate: ≤40% (hypothesis prediction)
- 95% CI upper bound: <60% (MUST_WORK gate)
- Component non-uniformity: χ² p < 0.05
- IRR quality: κ ≥ 0.70

---

## Testing Strategy

### Unit Tests
- `test_sampling.py`: Stratification logic, API mocking
- `test_t0_detection.py`: 3-tier fallback, commit selection
- `test_statistics.py`: CI calculation, chi-square, kappa

### Integration Tests
- Full pipeline with mock dataset (N=10)
- Gate check validation with synthetic data

### Manual Validation
- Human review of 5 random repository samples
- DCS coding spot-check against rubric

---

## Deployment Notes

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration
- Set GitHub token: `export GITHUB_TOKEN=<your_token>`
- Set HuggingFace token (optional): `export HF_TOKEN=<your_token>`

### Execution
```bash
python main.py --config src/config.py
```

### Manual Coding Phase
1. Run pipeline through Phase 3 (cloning)
2. Open `notebooks/manual_coding_template.xlsx`
3. Code N=100 repositories (primary coder)
4. Dual-code N=20 repositories (secondary coder)
5. Save completed files to `data/`
6. Resume pipeline with Phase 5 (analysis)

---

## Architecture Validation

### Brevity Checks
- [x] No ASCII diagrams (used bullet lists)
- [x] No KB search logs (only "Applied: X" in header)
- [x] No Serena logs (concise "Codebase Analysis" section)
- [x] Module descriptions = interface signatures only
- [x] Total length < 500 lines

### Serena MCP Validation
- [x] Green-field project → Serena skip acceptable
- [x] "Codebase Analysis (Serena)" section included

### Content Completeness
- [x] 6 Epic tasks with complexity scores
- [x] Module structure (7 modules, interfaces only)
- [x] File organization
- [x] Configuration structure
- [x] External dependencies listed

---

**Document Version:** 1.0  
**Next Phase:** Phase 4 - Implementation (Coder Agent)  
**Total Complexity:** 64 points (within EXISTENCE/LIGHT tier budget)  
**Gate Status:** MUST_WORK gate pending (validation in Phase 4)
