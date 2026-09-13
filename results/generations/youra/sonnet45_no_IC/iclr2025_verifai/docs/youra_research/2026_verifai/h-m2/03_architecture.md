# System Architecture: h-m2
## LLM Semantic Extraction Validation

**Date:** 2026-07-14  
**Hypothesis Type:** MECHANISM (Extraction Quality Evaluation)  
**Complexity Tier:** STANDARD  
**Applied Patterns:** Modular evaluation pipeline, LLM API extraction, Human annotation validation, Metric-driven gate

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending h-m1 validation pipeline with LLM extraction layer  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Findings:** H-M1 implemented modular validation pipeline (parser → validator → evaluator → visualizer). H-M2 reuses TraceParser and adds LLM extraction (with API client), human annotation comparison, and precision/recall evaluation.

---

## Architecture Overview

**Type:** LLM Evaluation Pipeline (Non-training)

**Core Flow:**
1. Trace Loading (reuse h-m1) → 2. Sample Selection → 3. LLM Extraction → 4. Human Annotation → 5. Metrics Comparison → 6. Visualization

**Design Principles:**
- Reuse h-m1 TraceParser and NLContentValidator for data loading
- New LLM extraction module with API client (Anthropic/OpenAI)
- Human annotation module for gold standard
- New evaluation metrics (precision/recall vs kappa)
- Gate-focused visualizations

**Key Difference from h-m1:**
- h-m1: NL word presence validation (binary check)
- h-m2: Semantic extraction quality evaluation (precision/recall)

---

## Module Structure

### TraceParser (`code/src/trace_parser.py`)

**Dependencies:** pathlib, json  
**Status:** REUSED FROM H-M1 (no modifications)

```python
class TraceParser:
    def __init__(self, trace_folder: Path): ...
    def discover_traces(self) -> List[Path]: ...
    def parse_trace_file(self, file_path: Path) -> Dict: ...
    def load_all_traces(self) -> List[Dict]: ...
```

### NLContentValidator (`code/src/nl_content_validator.py`)

**Dependencies:** re, typing  
**Status:** REUSED FROM H-M1 (for filtering ≥10 words)

```python
class NLContentValidator:
    def __init__(self, min_word_count: int = 10): ...
    def count_nl_words(self, text: str) -> int: ...
    def extract_text_from_dict(self, obj) -> str: ...
    def validate_nl_presence(self, tool_call: Dict) -> Tuple[bool, int, int]: ...
```

### SampleSelector (`code/src/sample_selector.py`)

**Dependencies:** NLContentValidator, random, typing  
**Status:** NEW

```python
class SampleSelector:
    def __init__(self, validator: NLContentValidator, random_seed: int = 42): ...
    def stratified_sample(self, traces: List[Dict], n_queries: int, n_results: int) -> Dict: ...
    def filter_by_outcome(self, traces: List[Dict], outcome: str) -> List[Dict]: ...
    def get_tool_type(self, tool_name: str) -> str: ...
```

### LLMExtractor (`code/src/llm_extractor.py`)

**Dependencies:** anthropic or openai, typing, json  
**Status:** NEW (core mechanism)

```python
class LLMExtractor:
    def __init__(self, model_name: str = "claude-sonnet-4-5", temperature: float = 0.0): ...
    def extract_assumptions(self, query_text: str) -> List[Dict]: ...
    def extract_claims(self, result_text: str) -> List[Dict]: ...
    def multi_vote_extract(self, text: str, text_type: str, n_votes: int = 3) -> List[Dict]: ...
    def parse_llm_response(self, response: str) -> List[Dict]: ...
```

### AnnotationManager (`code/src/annotation_manager.py`)

**Dependencies:** json, pathlib, typing  
**Status:** NEW

```python
class AnnotationManager:
    def __init__(self, annotation_dir: Path): ...
    def create_annotation_template(self, samples: Dict, output_path: Path) -> None: ...
    def load_annotations(self, annotator_id: str) -> Dict: ...
    def compute_consensus(self, annotations_1: Dict, annotations_2: Dict) -> Dict: ...
    def compute_inter_rater_kappa(self, annotations_1: Dict, annotations_2: Dict) -> float: ...
```

### ExtractionEvaluator (`code/src/extraction_evaluator.py`)

**Dependencies:** sklearn.metrics, typing  
**Status:** NEW

```python
class ExtractionEvaluator:
    def __init__(self, precision_threshold: float = 0.70, recall_threshold: float = 0.80, kappa_threshold: float = 0.70): ...
    def evaluate_extraction(self, llm_items: List[str], human_items: List[str]) -> Dict: ...
    def check_gate_condition(self, results: Dict) -> bool: ...
    def aggregate_results(self, per_sample_results: List[Dict]) -> Dict: ...
    def save_results(self, results: Dict, output_path: Path) -> None: ...
```

### Visualizer (`code/src/visualizer.py`)

**Dependencies:** matplotlib, numpy  
**Status:** NEW (different figures than h-m1)

```python
class Visualizer:
    def __init__(self, output_dir: Path, dpi: int = 300): ...
    def plot_gate_metrics(self, results: Dict) -> None: ...
    def plot_confusion_matrix(self, results: Dict) -> None: ...
    def plot_per_category_performance(self, results: Dict) -> None: ...
    def plot_error_examples(self, errors: Dict) -> None: ...
    def generate_all_figures(self, results: Dict) -> None: ...
```

### Main (`code/src/main.py`)

**Dependencies:** All modules above, argparse  
**Status:** NEW

```python
def parse_arguments() -> argparse.Namespace: ...
def run_llm_extraction(samples: Dict, extractor: LLMExtractor) -> Dict: ...
def run_evaluation(llm_extracts: Dict, annotations: Dict, evaluator: ExtractionEvaluator) -> Dict: ...
def main() -> int: ...
```

---

## File Organization

```
{hypothesis_folder}/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── trace_parser.py           [REUSED from h-m1]
│   │   ├── nl_content_validator.py   [REUSED from h-m1]
│   │   ├── sample_selector.py        [NEW]
│   │   ├── llm_extractor.py          [NEW - core mechanism]
│   │   ├── annotation_manager.py     [NEW]
│   │   ├── extraction_evaluator.py   [NEW]
│   │   ├── visualizer.py             [NEW]
│   │   └── main.py                   [NEW]
│   ├── config/
│   │   └── config.py                 [NEW]
│   ├── prompts/
│   │   ├── assumption_prompt.txt     [NEW - few-shot template]
│   │   └── claim_prompt.txt          [NEW - few-shot template]
│   ├── annotations/
│   │   ├── annotation_template.json  [Generated]
│   │   ├── annotator_1.json          [Manual input]
│   │   └── annotator_2.json          [Manual input]
│   ├── tests/
│   │   └── test_extraction.py        [NEW]
│   └── requirements.txt              [NEW]
├── figures/
│   ├── fig1_gate_metrics.png
│   ├── fig2_confusion_matrix.png
│   ├── fig3_per_category.png
│   └── fig4_error_examples.png
├── llm_extracts.json
├── h_m2_results.json
└── 03_architecture.md (this document)

{research_folder}/mcp_traces/
└── [20 .jsonl files from h-m1 - NO CHANGES]
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TraceParser | `from src.trace_parser import TraceParser` | `h-m1/code/src/trace_parser.py` |
| NLContentValidator | `from src.nl_content_validator import NLContentValidator` | `h-m1/code/src/nl_content_validator.py` |

**Reuse Strategy:** Copy both modules directly from h-m1 (no modifications required)

**Verified from:** `docs/youra_research/h-m1/code/src/` (actual implementation)

---

## Configuration

### Config (`code/config/config.py`)

**Dependencies:** pathlib  
**Status:** NEW

```python
class Config:
    TRACE_FOLDER: Path
    HYPOTHESIS_FOLDER: Path
    FIGURES_DIR: Path
    ANNOTATIONS_DIR: Path
    PROMPTS_DIR: Path
    RESULTS_FILE: Path
    EXTRACTS_FILE: Path
    
    # Sampling parameters
    SAMPLE_SIZE: int = 50
    N_QUERIES: int = 25
    N_RESULTS: int = 25
    RANDOM_SEED: int = 42
    MIN_WORD_COUNT: int = 10
    
    # LLM parameters
    LLM_MODEL: str = "claude-sonnet-4-5"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 2000
    N_VOTES: int = 3
    
    # Gate thresholds
    PRECISION_THRESHOLD: float = 0.70
    RECALL_THRESHOLD: float = 0.80
    KAPPA_THRESHOLD: float = 0.70
    
    # Figure settings
    FIGURE_DPI: int = 300
    FIGURE_SIZE: Tuple[int, int] = (10, 6)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Setup Project Structure | Copy h-m1 modules, create new config.py, prompts/, annotations/ dirs | 5 | Module(1) + Deps(1) + Algo(1) + Integ(2) |
| M2-2 | Implement Sample Selector | Stratified sampling (25 queries + 25 results), outcome/tool-type balancing | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| M2-3 | Implement LLM Extractor | API client (Anthropic/OpenAI), few-shot prompts, multi-vote consensus | 14 | Module(4) + Deps(3) + Algo(4) + Integ(3) |
| M2-4 | Implement Annotation Manager | Template generation, annotation loading, consensus computation, Cohen's Kappa | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| M2-5 | Implement Extraction Evaluator | Precision/recall calculation, gate condition check, result aggregation | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| M2-6 | Implement Visualizer | 4 figures (gate metrics, confusion matrix, per-category, error examples) | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| M2-7 | Create Prompt Templates | Few-shot examples for assumptions/claims extraction (3-5 examples each) | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |
| M2-8 | Implement Main Pipeline | Orchestration (load → sample → extract → annotate → evaluate → visualize) | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| M2-9 | Integration & Testing | End-to-end validation, mock API tests, annotation flow tests | 10 | Module(2) + Deps(2) + Algo(2) + Integ(4) |

**Total Complexity:** 85  
**Distribution:** VeryHigh(18-20): [], High(14-17): [M2-3], Medium(9-13): [M2-2, M2-4, M2-5, M2-6, M2-9], Low(4-8): [M2-1, M2-7, M2-8]

---

## Data Flow

### Input Processing (Reused from h-m1)
1. `TraceParser.load_all_traces()` → List[Dict] (596 tool calls)
2. `NLContentValidator.validate_nl_presence()` → filter ≥10 words

### Sample Selection (New)
3. `SampleSelector.stratified_sample()` → Dict{queries: 25, results: 25}
4. `SampleSelector.filter_by_outcome()` → balance success/fail
5. `SampleSelector.get_tool_type()` → balance research/data tools

### LLM Extraction (New)
6. `LLMExtractor.extract_assumptions()` → List[Dict] (for queries)
7. `LLMExtractor.extract_claims()` → List[Dict] (for results)
8. `LLMExtractor.multi_vote_extract()` → consensus items (≥2/3 votes)
9. Save to llm_extracts.json

### Human Annotation (New - Manual Step)
10. `AnnotationManager.create_annotation_template()` → annotation_template.json
11. **Manual annotation by 2 annotators** → annotator_1.json, annotator_2.json
12. `AnnotationManager.compute_inter_rater_kappa()` → kappa score (≥0.70 check)
13. `AnnotationManager.compute_consensus()` → gold_standard.json

### Evaluation (New)
14. `ExtractionEvaluator.evaluate_extraction()` → per-sample precision/recall
15. `ExtractionEvaluator.aggregate_results()` → overall metrics
16. `ExtractionEvaluator.check_gate_condition()` → PASS/FAIL
17. `ExtractionEvaluator.save_results()` → h_m2_results.json

### Visualization (New)
18. `Visualizer.generate_all_figures()` → 4 PNG files

---

## Key Algorithms

### Multi-Vote Consensus (LLM Extraction)

**Purpose:** Reduce hallucination via redundancy

**Algorithm:**
```python
def multi_vote_extract(text, text_type, n_votes=3):
    extracts = []
    for _ in range(n_votes):
        response = llm_api.complete(prompt)
        extracts.append(parse_response(response))
    
    # Consensus: items in ≥2/3 votes
    item_counts = Counter([item for extract in extracts for item in extract])
    consensus = [item for item, count in item_counts.items() if count >= 2]
    return consensus
```

### Cohen's Kappa Calculation

**Purpose:** Measure inter-rater agreement

**Formula:**
```
P_o = observed agreement = (agree_present + agree_absent) / total
P_e = expected agreement = (p1_present * p2_present) + (p1_absent * p2_absent)
Kappa = (P_o - P_e) / (1 - P_e)
```

**Threshold:** ≥0.70 (validates gold standard reliability)

### Precision/Recall Computation

**Purpose:** Compare LLM vs human gold standard

**Formulas:**
```
TP = |LLM ∩ Human|
FP = |LLM - Human|
FN = |Human - LLM|

Precision = TP / (TP + FP)  [≥0.70 threshold]
Recall = TP / (TP + FN)     [≥0.80 threshold]
F1 = 2 * Precision * Recall / (Precision + Recall)
```

---

## Prompt Templates

### Assumption Extraction (`prompts/assumption_prompt.txt`)

```
Extract all assumptions from the following MCP tool query parameters.

An assumption is any expectation, requirement, or belief encoded in the query.
Include both explicit statements and implicit assumptions inferable from context.

Format: Return a JSON list of assumption texts.

Examples:

Query: "Search for papers about transformers with >1000 citations"
Assumptions: ["Paper database exists", "Citation count is tracked", "Threshold >1000 is meaningful"]

Query: "Load dataset with stratified sampling, 80/20 train/test split"
Assumptions: ["Dataset supports stratification", "80/20 split is standard", "Train/test split is required"]

Query: "Generate violin plot for accuracy scores across 5 models"
Assumptions: ["5 models have been evaluated", "Accuracy is the primary metric", "Violin plot is appropriate visualization"]

Now extract assumptions from:

Query: {query_text}
Assumptions:
```

### Claim Extraction (`prompts/claim_prompt.txt`)

```
Extract all claims from the following MCP tool result content.

A claim is any factual statement, finding, or piece of evidence presented.
Focus on concrete assertions, not speculative language.

Format: Return a JSON list of claim texts.

Examples:

Result: "Found 47 papers. Top result: 'Attention Is All You Need' (67,281 citations)"
Claims: ["47 papers found", "'Attention Is All You Need' is top result", "Top paper has 67,281 citations"]

Result: "Dataset loaded: 10,000 samples (8,000 train, 2,000 test). Stratified by class label."
Claims: ["Dataset has 10,000 samples", "8,000 samples in train set", "2,000 samples in test set", "Stratification by class label applied"]

Result: "Plot saved. Model A: mean=0.87, std=0.04. Best performing model."
Claims: ["Plot successfully saved", "Model A mean accuracy is 0.87", "Model A std is 0.04", "Model A is best performing"]

Now extract claims from:

Result: {result_text}
Claims:
```

---

## Error Handling Strategy

### LLM API Errors
- **Rate Limits:** Exponential backoff (1s, 2s, 4s), max 3 retries
- **API Failures:** Log error, skip sample, continue processing
- **Invalid JSON Response:** Parse with fallback regex, log warning
- **Empty Extraction:** Return empty list, count as 0 precision/recall

### Annotation Errors
- **Missing Files:** Raise FileNotFoundError with instructions
- **Invalid JSON:** Raise ValueError with line number
- **Kappa <0.70:** Abort evaluation, prompt for re-annotation
- **Consensus Conflicts:** Log disagreement count, use majority rule

### Evaluation Errors
- **Division by Zero:** Check denominators, return 0 if no items
- **Missing Samples:** Skip in aggregation, log warning
- **Gate Failure:** Set status to FAIL, generate diagnostic plots

---

## Acceptance Criteria

### M2-1: Setup Project Structure
- [ ] Directories created: src/, config/, prompts/, annotations/, figures/
- [ ] trace_parser.py and nl_content_validator.py copied from h-m1
- [ ] config.py created with all constants
- [ ] requirements.txt includes: anthropic, openai, scikit-learn, matplotlib

### M2-2: Implement Sample Selector
- [ ] stratified_sample() returns 25 queries + 25 results
- [ ] Balances success/fail outcomes (±10%)
- [ ] Balances tool types: research vs data processing (±10%)
- [ ] All samples have ≥10 NL words (validated by NLContentValidator)
- [ ] Random seed 42 for reproducibility

### M2-3: Implement LLM Extractor
- [ ] API client supports Claude Sonnet 4.5 and GPT-4
- [ ] Temperature 0.0 (deterministic)
- [ ] Few-shot prompts loaded from prompts/
- [ ] multi_vote_extract() runs 3 independent calls
- [ ] Consensus: items in ≥2/3 votes
- [ ] parse_llm_response() handles JSON and fallback regex
- [ ] Retry logic: exponential backoff, max 3 attempts

### M2-4: Implement Annotation Manager
- [ ] create_annotation_template() generates JSON for 50 samples
- [ ] load_annotations() validates JSON schema
- [ ] compute_inter_rater_kappa() uses sklearn cohen_kappa_score
- [ ] compute_consensus() resolves disagreements (majority rule)
- [ ] Kappa ≥0.70 check before consensus

### M2-5: Implement Extraction Evaluator
- [ ] evaluate_extraction() computes TP, FP, FN, precision, recall
- [ ] Precision threshold: ≥0.70
- [ ] Recall threshold: ≥0.80
- [ ] check_gate_condition(): PASS if all 3 thresholds met
- [ ] aggregate_results() computes mean across samples
- [ ] save_results() writes h_m2_results.json

### M2-6: Implement Visualizer
- [ ] plot_gate_metrics(): bar chart with 3 metrics + threshold lines
- [ ] plot_confusion_matrix(): heatmap (TP, FP, FN, TN)
- [ ] plot_per_category_performance(): assumptions vs claims
- [ ] plot_error_examples(): sample false positives/negatives
- [ ] All figures save as 300 DPI PNG

### M2-7: Create Prompt Templates
- [ ] assumption_prompt.txt: 3-5 few-shot examples
- [ ] claim_prompt.txt: 3-5 few-shot examples
- [ ] Prompts follow JSON output format
- [ ] Examples cover diverse tool types

### M2-8: Implement Main Pipeline
- [ ] Orchestrates all modules in correct order
- [ ] CLI args: --trace-folder, --output-folder, --api-key
- [ ] Prints progress messages
- [ ] Handles manual annotation step (pause with instructions)
- [ ] Exit code 0 if PASS, 1 if FAIL

### M2-9: Integration & Testing
- [ ] Mock LLM API for testing (no real API calls)
- [ ] Unit test: multi-vote consensus logic
- [ ] Unit test: Cohen's Kappa calculation
- [ ] Unit test: precision/recall edge cases
- [ ] Integration test: mock 5 samples → expected metrics
- [ ] End-to-end: process 50 samples → h_m2_results.json + 4 figures

---

## Testing Strategy

### Unit Tests (`tests/test_extraction.py`)
1. **test_multi_vote_consensus**: Verify ≥2/3 vote logic
2. **test_llm_response_parsing**: JSON and fallback regex handling
3. **test_cohen_kappa_calculation**: Known agreement → expected kappa
4. **test_precision_recall_computation**: TP/FP/FN → correct metrics
5. **test_gate_condition_check**: Threshold boundary cases

### Integration Test
- **Mock LLM API:** Return predefined extractions (no real API calls)
- **Mock Annotations:** 2 annotators with known agreement
- **Expected Output:** h_m2_results.json with known precision/recall
- **Validation:** All 4 figures created, gate decision correct

### Manual Annotation Test
- **Annotation Template:** Generate for 5 sample tool calls
- **2 Annotators:** Manual annotation (researcher + assistant)
- **Kappa Check:** Compute inter-rater agreement
- **Consensus:** Resolve disagreements via discussion

---

## Dependencies

### Python Packages
```
anthropic>=0.18.0
openai>=1.0.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
numpy>=1.21.0
```

### System Requirements
- Python 3.9+
- Anthropic or OpenAI API key
- 500MB disk space
- No GPU required

### External Services
- **Anthropic API** (Claude Sonnet 4.5) OR **OpenAI API** (GPT-4)
- Cost estimate: ~$1.50 for 150 API calls (50 samples × 3 votes)

---

## Success Metrics

### Gate Condition (MUST_WORK)

**Primary:**
1. Extraction precision ≥70%
2. Extraction recall ≥80%
3. Inter-rater Kappa ≥0.70

**Decision:** PASS if ALL three met, else FAIL

### Deliverables
1. 8 Python modules (parser, validator, selector, extractor, annotator, evaluator, visualizer, main)
2. 2 prompt templates (assumptions, claims)
3. 4 PNG figures (gate metrics, confusion matrix, per-category, error examples)
4. 2 JSON files (llm_extracts.json, h_m2_results.json)
5. Annotation files (template, annotator_1, annotator_2, consensus)

---

## Risk Mitigation

### Risk: LLM Extraction Below Thresholds
- **Probability:** MEDIUM (40% from PRD)
- **Impact:** HIGH (blocks h-m3, h-m4)
- **Mitigation:**
  - Iterate prompt engineering (add more examples)
  - Increase n_votes from 3 to 5
  - Switch to hybrid (LLM + human review)
  - Try alternative model (Claude → GPT-4 or vice versa)

### Risk: Inter-Rater Kappa <0.70
- **Probability:** LOW-MEDIUM (25% from PRD)
- **Impact:** HIGH (gold standard unreliable)
- **Mitigation:**
  - Refine annotation guidelines
  - Add 30-minute training session
  - Add 3rd annotator for tie-breaking
  - Re-annotate with consensus discussion

### Risk: API Rate Limits or Quota Exceeded
- **Probability:** LOW (10% from PRD)
- **Impact:** MEDIUM (delays completion)
- **Mitigation:**
  - Exponential backoff with retries
  - Save intermediate results (checkpoint after each sample)
  - Switch to alternative API provider
  - Reduce n_votes from 3 to 1 (if budget constrained)

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement all modules per Epic tasks  
**Estimated Effort:** 10-12 hours (9 Epic tasks, STANDARD complexity tier)
