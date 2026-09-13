# Architecture Design
# H-M2: Proof Depth Filtering Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Complexity**: Level 1 (Post-processing Analysis)

**Applied**: Post-hoc analysis pipeline pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: Standalone analysis pipeline, no existing code reuse

---

## System Overview

Post-hoc analysis pipeline: LLM prover → proof extraction → tactic counting → statistical analysis

**Data Flow**: miniF2F theorems → proofs.json → tactic_counts.csv → results.json → report.md

**Stack**: Lean 4.14+, Python 3.10+, LeanCopilot/DeepSeek-Prover API, pandas/scipy

---

## Module Structure

### ProofRunner (`src/proof_runner.py`)

**Dependencies**: LeanCopilot API, miniF2F dataset

```python
class ProofRunner:
    def __init__(self, api_key: str, minif2f_path: str, config: dict): ...
    def run_prover(self, theorem_name: str, timeout: int = 60) -> list[str]: ...
    def collect_all_proofs(self, output_path: str) -> dict: ...
```

### TacticExtractor (`src/tactic_extractor.py`)

**Dependencies**: Lean 4 subprocess

```python
class TacticExtractor:
    def __init__(self, lean_path: str): ...
    def extract_from_proof_term(self, proof_term: str) -> int: ...
    def extract_from_script(self, proof_script: str) -> int: ...
    def process_proofs(self, proofs_json: str, output_csv: str): ...
```

### StratificationAnalyzer (`src/analyzer.py`)

**Dependencies**: pandas, scipy.stats, matplotlib

```python
class StratificationAnalyzer:
    def __init__(self, tactic_counts_csv: str): ...
    def compute_success_rates(self) -> dict: ...
    def mcnemar_test(self) -> dict: ...
    def bootstrap_ci(self, n_iterations: int = 10000) -> tuple: ...
    def plot_depth_histogram(self, output_path: str): ...
```

### ConfigLoader (`src/config.py`)

**Dependencies**: yaml

```python
@dataclass
class Config:
    api_key: str
    minif2f_path: str
    pass_k: int = 16
    timeout: int = 60
    max_tokens: int = 1024
    shallow_threshold: int = 3
    random_seed: int = 42
    
    @classmethod
    def from_yaml(cls, path: str) -> Config: ...
```

### Main Orchestrator (`src/main.py`)

**Dependencies**: All above modules

```python
def main(config_path: str):
    config = Config.from_yaml(config_path)
    runner = ProofRunner(config.api_key, config.minif2f_path, config)
    proofs = runner.collect_all_proofs("output/proofs.json")
    
    extractor = TacticExtractor(config.lean_path)
    extractor.process_proofs("output/proofs.json", "output/tactic_counts.csv")
    
    analyzer = StratificationAnalyzer("output/tactic_counts.csv")
    results = analyzer.compute_success_rates()
    stats = analyzer.mcnemar_test()
    ci = analyzer.bootstrap_ci()
    analyzer.plot_depth_histogram("output/depth_histogram.png")
    
    write_report(results, stats, ci, "output/report.md")
```

---

## File Structure

```
h-m2/
├── config.yaml              # API keys, paths, hyperparameters
├── src/
│   ├── proof_runner.py      # LLM prover integration
│   ├── tactic_extractor.py  # Lean 4 proof parsing
│   ├── analyzer.py          # Statistical analysis
│   ├── config.py            # Configuration dataclass
│   └── main.py              # Pipeline orchestrator
├── output/
│   ├── proofs.json          # All successful proofs
│   ├── tactic_counts.csv    # Extracted tactic counts
│   ├── results.json         # Success rates, delta
│   ├── depth_histogram.png  # Visualization
│   └── report.md            # Human-readable summary
└── tests/
    ├── test_extractor.py    # Tactic extraction validation
    └── test_analyzer.py     # Statistical test validation
```

---

## Integration Points

### miniF2F Dataset
- **Source**: `https://github.com/google-deepmind/miniF2F`
- **Access**: Clone Lean 4 branch, read test split (244 theorems)
- **Format**: Lean 4 theorem statements

### LLM Prover API
- **Primary**: LeanCopilot API (if available)
- **Fallback**: DeepSeek-Prover-V1.5 REST API
- **Config**: pass@16, 1024 tokens, 60s timeout per attempt

### Lean 4 Compiler
- **Version**: 4.14+ (Mathlib v4 compatible)
- **Usage**: Proof term validation, tactic extraction via metaprogramming
- **Fallback**: Regex-based proof script parsing

---

## Error Handling

### API Failures
- Retry 3× with exponential backoff (1s, 2s, 4s)
- Log failed theorems to `output/failures.log`
- Skip and continue on persistent failures

### Tactic Extraction Failures
- Primary: Lean 4 metaprogramming (proof term AST)
- Fallback: Proof script line counting (non-comment, non-empty lines)
- Validation: Manual spot-check 10% of counts, require ≥80% accuracy

### Statistical Power Failures
- Minimum N=30 solved problems required
- If <30: BLOCK experiment, report insufficient power
- Mitigation: Reuse H-E1 or H-M1 proof logs if available

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Infrastructure Setup | Clone miniF2F, install Lean 4, configure API | 8 | Setup(3)+API(3)+Validate(2) |
| A-2 | Proof Collection | Implement ProofRunner, run on 244 theorems | 14 | Integration(4)+Logging(3)+Retry(4)+Monitor(3) |
| A-3 | Tactic Extraction | Parse proof terms, count tactics, fallback script parser | 12 | AST(5)+Fallback(3)+Validation(4) |
| A-4 | Statistical Analysis | Stratification, McNemar, bootstrap CI, histogram | 10 | Metrics(3)+Tests(4)+Visualization(3) |
| A-5 | Report Generation | Aggregate results, interpret gate criteria, write report | 6 | Aggregate(2)+Interpret(2)+Document(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-5]

**Complexity Calculation Example (A-2)**:
- Module_Size: 4 (multi-component: API client, theorem loader, retry logic, progress monitor)
- Dependencies: 3 (LLM API, miniF2F dataset, config loader)
- Algorithm: 4 (retry backoff, checkpoint resume, parallel attempts)
- Integration: 3 (API rate limits, filesystem I/O, logging)
- **Total**: 14

---

## Technology Stack

### Core Dependencies
- **Lean 4.14+**: Proof verification, metaprogramming API
- **Python 3.10+**: Pipeline orchestration, analysis
- **pandas 2.0+**: Data manipulation (tactic_counts.csv)
- **scipy 1.11+**: Statistical tests (McNemar, bootstrap)
- **matplotlib 3.7+**: Depth distribution plots

### API Dependencies
- **LeanCopilot**: LLM-guided proving (preferred)
- **DeepSeek-Prover-V1.5**: Fallback REST API
- **Requests 2.31+**: HTTP client for API calls

### Optional Dependencies
- **lean4-interaction**: Python-Lean bridge (if available for AST parsing)
- **tqdm**: Progress bars for proof collection
- **pyyaml**: Config file parsing

---

## Configuration Schema

```yaml
# config.yaml
api:
  key: "YOUR_API_KEY"
  endpoint: "https://api.leancopilot.io/v1/prove"
  provider: "leancopilot"  # or "deepseek"
  
dataset:
  minif2f_path: "/path/to/miniF2F"
  split: "test"
  
prover:
  pass_k: 16
  timeout: 60
  max_tokens: 1024
  temperature: 0.8
  
analysis:
  shallow_threshold: 3
  random_seed: 42
  bootstrap_iterations: 10000
  confidence_level: 0.95
  
output:
  base_dir: "./output"
  proofs_json: "proofs.json"
  tactic_counts_csv: "tactic_counts.csv"
  results_json: "results.json"
  histogram_png: "depth_histogram.png"
  report_md: "report.md"
```

---

## Execution Flow

### Phase 1: Proof Collection (6-8 hours)
1. Load miniF2F test split (244 theorems)
2. For each theorem:
   - Call LLM prover API with pass@16
   - Collect all successful proofs
   - Log proof terms to proofs.json
   - Checkpoint every 10 theorems
3. Report: X/244 theorems solved, Y total proofs collected

### Phase 2: Tactic Extraction (15 minutes)
1. Load proofs.json
2. For each proof:
   - Attempt Lean 4 metaprogramming AST traversal
   - Fallback to proof script line counting if AST fails
   - Store (theorem_name, tactic_count) in CSV
3. Spot-check 10% manual verification
4. If accuracy <80%, switch all to fallback mode

### Phase 3: Statistical Analysis (5 minutes)
1. Load tactic_counts.csv
2. Classify problems:
   - Shallow-solvable: min(tactic_count) ≤ 3
   - Deep-only: min(tactic_count) > 3
3. Compute success rates:
   - Success_full = solved / 244
   - Success_shallow = shallow_solvable / 244
   - Δ = Success_full - Success_shallow
4. Run McNemar test (paired comparison)
5. Bootstrap 95% CI (10,000 resamples)
6. Generate depth histogram

### Phase 4: Reporting (10 minutes)
1. Aggregate all results into results.json
2. Interpret gate criteria:
   - PASS: 5% < Δ < 30%
   - FAIL: Δ ≤ 5% or Δ ≥ 30%
3. Write human-readable report.md
4. Package all artifacts in output/

---

## Validation Criteria

### Pipeline Completeness
- [ ] All 244 theorems attempted (or failures logged)
- [ ] proofs.json contains all successful proof terms
- [ ] tactic_counts.csv has one row per solved problem
- [ ] Spot-check validation ≥80% accuracy

### Statistical Validity
- [ ] Minimum 30 solved problems (power requirement)
- [ ] McNemar test p-value computed
- [ ] Bootstrap 95% CI width <10 percentage points
- [ ] Depth histogram shows non-degenerate distribution

### Reproducibility
- [ ] config.yaml captures all hyperparameters
- [ ] Random seeds fixed (LLM sampling, bootstrap)
- [ ] Versions logged (Lean, Mathlib, miniF2F commits)
- [ ] Single-command execution: `python src/main.py --config config.yaml`

---

## Limitations

### Post-hoc Analysis Constraints
- Cannot control which proofs LLM finds (search bias)
- Depth filtering ≠ controlled ablation (multiple confounds)
- Depth may correlate with difficulty (report as threat)

### Tactic Extraction Approximation
- Proof term AST parsing may fail on complex terms
- Fallback line counting is proxy metric (not exact tactic count)
- Nested tactics may be undercounted

### Statistical Power
- Requires ≥30 solved problems (BLOCK if <30)
- Effect size confidence depends on proof diversity
- Multiple comparisons not controlled (exploratory analysis)

---

## Estimated Runtime

| Component | Duration | Compute |
|-----------|----------|---------|
| Infrastructure setup | 4 hours | 1 CPU, manual steps |
| Proof collection | 6-8 hours | API calls (244 × 16 × 60s) |
| Tactic extraction | 15 minutes | 1 CPU, Lean subprocess |
| Statistical analysis | 5 minutes | 1 CPU, Python scripts |
| Report generation | 10 minutes | 1 CPU, aggregation |
| **Total** | **16-18 hours** | Mostly API-bound |

---

## Self-Validation Checklist

- [x] No ASCII diagrams (bullet lists for structure)
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 5 Epic tasks with complexity (green-field PoC scope)
- [x] Total length <500 lines
- [x] Codebase Analysis (Serena) section included
- [x] Serena skip acceptable (green-field project)
- [x] Technology stack specified
- [x] Error handling strategies defined
- [x] Integration points documented
