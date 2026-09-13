# Architecture Design: h-e1
**Hypothesis:** Reformulation rate decrease AND diversity correlation exist in HH-RLHF conversations with ≥5 turns
**Type:** EXISTENCE (LIGHT tier, ≤15 tasks, 4-8 Epics)
**Date:** 2026-08-25

---

## Codebase Analysis (Serena)

*Serena MCP not available - proceeding with green-field design*

**Analysis Type:** Green-field (no existing codebase)
**Base Hypothesis:** None (FOUNDATION hypothesis)
**Existing Patterns:** Standard Python scientific analysis structure

---

## Applied Patterns

**Applied:** Data Analysis Pipeline (Archon KB - manual reference)
- ETL pattern for dataset loading
- Analysis module for metric computation
- Statistical validation module
- Visualization generation

**Applied:** Measurement Experiment Structure
- No model training required
- Focus on metric extraction and correlation analysis
- Statistical significance testing

---

## System Architecture

### High-Level Design

```
h-e1-analysis/
├── data/
│   ├── loader.py          # HH-RLHF dataset loading
│   └── preprocessor.py    # Conversation filtering + parsing
├── analysis/
│   ├── reformulation.py   # Reformulation detection + slope
│   ├── diversity.py       # Lexical diversity metrics
│   └── statistics.py      # Statistical tests
├── visualization/
│   └── plots.py          # Figure generation
├── main.py               # Orchestration script
└── config.py             # Hyperparameters + thresholds
```

### Module Breakdown

#### Module 1: Data Loading (`data/loader.py`)
**Responsibility:** Load HH-RLHF dataset from Hugging Face
**Key Functions:**
- `load_hh_rlhf() -> Dataset`
- `filter_by_turn_count(min_turns: int) -> Dataset`

**Dependencies:**
- `datasets` (Hugging Face)

**Complexity:** LOW (standard dataset loading)

#### Module 2: Data Preprocessing (`data/preprocessor.py`)
**Responsibility:** Parse conversations into structured format
**Key Functions:**
- `parse_conversation(raw: dict) -> Conversation`
- `extract_turns(conversation: dict) -> List[Turn]`
- `extract_metadata(conversation: dict) -> Metadata`

**Data Structures:**
```python
@dataclass
class Turn:
    user_query: str
    ai_response: str
    turn_index: int

@dataclass
class Conversation:
    conversation_id: str
    turns: List[Turn]
    helpfulness_rating: float
    turn_count: int
```

**Complexity:** LOW (parsing + data structuring)

#### Module 3: Reformulation Analysis (`analysis/reformulation.py`)
**Responsibility:** Detect reformulation + compute slope
**Key Functions:**
- `detect_reformulation(query_t: str, query_t1: str, sbert_model, threshold_sem: float, threshold_syn: float) -> bool`
- `compute_reformulation_slope(queries: List[str], sbert_model) -> float`
- `compute_semantic_similarity(q1: str, q2: str, sbert_model) -> float`
- `compute_syntactic_distance(q1: str, q2: str) -> float`

**Dependencies:**
- `sentence_transformers` (SBERT)
- `Levenshtein` (edit distance)
- `scipy.stats` (linear regression)

**Complexity:** MEDIUM (dual-signal detection + regression)

#### Module 4: Diversity Analysis (`analysis/diversity.py`)
**Responsibility:** Compute lexical diversity
**Key Functions:**
- `compute_distinct_n(texts: List[str], n: int) -> float`
- `compute_diversity(texts: List[str]) -> float`

**Complexity:** LOW (distinct-n metric)

#### Module 5: Statistical Validation (`analysis/statistics.py`)
**Responsibility:** Hypothesis testing
**Key Functions:**
- `test_slope_significance(slopes: List[float]) -> Tuple[float, float]`
- `compute_effect_size(slopes: List[float], baseline_mean: float) -> float`
- `report_statistics(slopes: List[float]) -> Dict`

**Dependencies:**
- `scipy.stats` (t-test, sign test)
- `numpy` (statistics)

**Complexity:** MEDIUM (statistical testing)

#### Module 6: Visualization (`visualization/plots.py`)
**Responsibility:** Generate all figures
**Key Functions:**
- `plot_gate_metrics(actual_slope: float, target_slope: float) -> Figure`
- `plot_reformulation_over_turns(conversations: List[Conversation]) -> Figure`
- `plot_slope_distribution(slopes: List[float]) -> Figure`
- `plot_diversity_scatter(query_div: List[float], response_div: List[float]) -> Figure`
- `save_all_figures(figures: Dict[str, Figure], output_dir: str)`

**Dependencies:**
- `matplotlib`
- `seaborn`

**Complexity:** LOW (standard plotting)

#### Module 7: Orchestration (`main.py`)
**Responsibility:** End-to-end pipeline execution
**Key Functions:**
- `run_experiment(config: ExperimentConfig) -> Results`
- `pipeline_etl(config) -> List[Conversation]`
- `pipeline_analysis(conversations, config) -> Metrics`
- `pipeline_validation(metrics) -> ValidationReport`
- `pipeline_visualization(conversations, metrics, output_dir)`

**Complexity:** LOW (orchestration logic)

#### Module 8: Configuration (`config.py`)
**Responsibility:** Hyperparameters + settings
**Structure:**
```python
@dataclass
class ExperimentConfig:
    # Dataset
    min_turns: int = 5
    dataset_name: str = "Anthropic/hh-rlhf"
    
    # Reformulation Detection
    sbert_model_name: str = "all-MiniLM-L6-v2"
    semantic_threshold: float = 0.7
    syntactic_threshold: float = 0.3
    
    # Statistical Testing
    alpha: float = 0.05
    random_seed: int = 42
    
    # Output
    output_dir: str = "h-e1/figures"
```

**Complexity:** TRIVIAL (configuration dataclass)

---

## File Organization

### Directory Structure
```
h-e1/
├── code/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── preprocessor.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── reformulation.py
│   │   ├── diversity.py
│   │   └── statistics.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── figures/         # Generated visualizations
├── results/         # Experiment outputs
└── logs/           # Execution logs
```

### External Dependencies

**Required Libraries:**
```txt
datasets==2.14.0
sentence-transformers==2.2.2
python-Levenshtein==0.21.0
scipy==1.11.0
statsmodels==0.14.0
matplotlib==3.7.0
seaborn==0.12.0
numpy==1.24.0
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

## Proposed Epic Tasks (LIGHT Tier: 4-8 Epics)

### Epic 1: Environment Setup + Data Loading
**Description:** Setup Python environment and implement HH-RLHF dataset loading with filtering
**Scope:**
- Create project structure
- Implement `data/loader.py` (load + filter)
- Implement `data/preprocessor.py` (parse conversations)
- Write `requirements.txt`

**Complexity Score:** 3 / 20
- Module Size: 1 (small modules)
- Dependencies: 1 (HF datasets only)
- Algorithm: 0 (standard loading)
- Integration: 1 (setup + structure)

**Estimated Effort:** 1-2 hours

### Epic 2: Reformulation Detection Module
**Description:** Implement dual-signal reformulation detection (SBERT + edit distance)
**Scope:**
- Implement `analysis/reformulation.py`
- SBERT semantic similarity computation
- Levenshtein syntactic distance
- Reformulation detection logic (threshold-based)

**Complexity Score:** 8 / 20
- Module Size: 2 (reformulation logic)
- Dependencies: 2 (SBERT + Levenshtein)
- Algorithm: 3 (dual-signal fusion)
- Integration: 1 (standalone module)

**Estimated Effort:** 3-4 hours

### Epic 3: Slope Computation + Statistical Validation
**Description:** Compute reformulation slope and run statistical tests
**Scope:**
- Implement `compute_reformulation_slope()` (linear regression)
- Implement `analysis/statistics.py`
- Hypothesis testing (t-test, sign test)
- Effect size computation (Cohen's d)

**Complexity Score:** 7 / 20
- Module Size: 2 (slope + stats)
- Dependencies: 1 (scipy)
- Algorithm: 3 (regression + tests)
- Integration: 1 (connect to reformulation module)

**Estimated Effort:** 2-3 hours

### Epic 4: Diversity Metrics
**Description:** Implement distinct-n lexical diversity computation
**Scope:**
- Implement `analysis/diversity.py`
- Distinct-1 metric for queries
- Distinct-1 metric for responses
- Correlation analysis

**Complexity Score:** 4 / 20
- Module Size: 1 (small module)
- Dependencies: 1 (numpy)
- Algorithm: 1 (distinct-n)
- Integration: 1 (standalone)

**Estimated Effort:** 1-2 hours

### Epic 5: Visualization Generation
**Description:** Generate all required and recommended figures
**Scope:**
- Implement `visualization/plots.py`
- Gate metrics comparison (required)
- Reformulation over turns, slope distribution, diversity scatter (recommended)
- Save figures to `h-e1/figures/`

**Complexity Score:** 5 / 20
- Module Size: 2 (multi-figure module)
- Dependencies: 2 (matplotlib + seaborn)
- Algorithm: 0 (standard plotting)
- Integration: 1 (connect to all analysis modules)

**Estimated Effort:** 2-3 hours

### Epic 6: End-to-End Pipeline + Configuration
**Description:** Implement orchestration script and configuration management
**Scope:**
- Implement `main.py` (pipeline orchestration)
- Implement `config.py` (hyperparameters)
- ETL → Analysis → Validation → Visualization flow
- Logging and error handling

**Complexity Score:** 6 / 20
- Module Size: 2 (orchestration + config)
- Dependencies: 0 (internal only)
- Algorithm: 1 (pipeline logic)
- Integration: 3 (connect all modules)

**Estimated Effort:** 2-3 hours

### Epic 7: Validation + Reporting
**Description:** Run experiment and generate validation report
**Scope:**
- Execute pipeline on filtered HH-RLHF data
- Verify gate criteria (slope < 0)
- Generate `04_validation.md` report
- Statistical summary and visualizations

**Complexity Score:** 5 / 20
- Module Size: 1 (validation script)
- Dependencies: 0 (uses existing modules)
- Algorithm: 1 (gate checking)
- Integration: 3 (full pipeline integration)

**Estimated Effort:** 2-3 hours

---

## Total Task Budget

**Epic Count:** 7 (within LIGHT tier range: 4-8)
**Total Complexity:** 38 / 140 (7 Epics × 20 max)
**Breakdown:**
- Very High (16-20): 0
- High (11-15): 0
- Medium (6-10): 2 (Epics 2, 3)
- Low (1-5): 5 (Epics 1, 4, 5, 6, 7)

**Budget Compliance:** ✅ 7 ≤ 15 (total max for LIGHT)

---

## Integration Flow

```
main.py
  ↓
[ETL Phase]
  ↓
data.loader → data.preprocessor
  ↓
[Analysis Phase]
  ↓
analysis.reformulation → analysis.statistics
analysis.diversity
  ↓
[Validation Phase]
  ↓
Check gate criteria (slope < 0)
  ↓
[Visualization Phase]
  ↓
visualization.plots
  ↓
[Output]
  ↓
04_validation.md + figures/
```

---

## Risk Mitigation

### Technical Risks
1. **SBERT memory usage** (50k conversations)
   - Mitigation: Batch encoding (1000 samples/batch)
   
2. **Edit distance computation time**
   - Mitigation: C implementation (python-Levenshtein)
   
3. **Low reformulation signal**
   - Mitigation: Threshold tuning on sample data

### Architectural Decisions
- **Modular design:** Each analysis component independent for testing
- **Configuration-driven:** All thresholds tunable without code changes
- **Reproducible:** Fixed seed + versioned dependencies

---

**Architecture Status:** Complete
**Next Phase:** Step 4 - Budget Allocation
