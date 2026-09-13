# System Architecture: h-m3
## Constraint Inference via Semantic Similarity

**Date:** 2026-07-14  
**Hypothesis Type:** MECHANISM (Constraint Detection)  
**Complexity Tier:** STANDARD  
**Applied Patterns:** Modular inference pipeline, Sentence transformers embedding, Cosine similarity threshold filtering

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-m2 base code  
**Analyzed Path:** docs/youra_research/h-m2/code/  
**Findings:** H-M2 implemented LLM extraction pipeline (TraceParser → LLMExtractor → Evaluator → Visualizer). H-M3 reuses TraceParser and LLMExtractor outputs, adds semantic similarity computation via sentence-transformers and threshold-based mismatch detection.

---

## Architecture Overview

**Type:** Semantic Similarity Pipeline (Zero-training)

**Core Flow:**
1. Load h-m2 Extracts → 2. Phase Pairing → 3. Semantic Embedding → 4. Similarity Computation → 5. Threshold Filtering → 6. Ground Truth Validation → 7. Metrics & Visualization

**Design Principles:**
- Reuse h-m2 extraction outputs (validated: 86.3% precision, 82.7% recall)
- Zero-training constraint: pre-trained sentence-transformers only
- Threshold-based detection (similarity <0.3 = contradiction)
- SHOULD_WORK gate: ≥70% recall, <30% FP rate

**Key Difference from h-m2:**
- h-m2: Extract assumptions/claims from MCP traces
- h-m3: Detect contradictions between assumptions and claims

---

## Module Structure

### TraceParser (`code/src/trace_parser.py`)

**Dependencies:** pathlib, json  
**Status:** REUSED FROM H-M2 (no modifications)

```python
class TraceParser:
    def __init__(self, trace_folder: Path): ...
    def discover_traces(self) -> List[Path]: ...
    def parse_trace_file(self, file_path: Path) -> Dict: ...
    def load_all_traces(self) -> List[Dict]: ...
```

### DataLoader (`code/src/data_loader.py`)

**Dependencies:** json, pathlib, typing  
**Status:** NEW

```python
class DataLoader:
    def __init__(self, h_m2_output_folder: Path): ...
    def load_assumptions(self) -> List[Dict]: ...
    def load_claims(self) -> List[Dict]: ...
    def filter_by_phase(self, items: List[Dict], phases: List[int]) -> List[Dict]: ...
    def create_phase_pairs(self, early_assumptions: List[Dict], later_claims: List[Dict]) -> List[Dict]: ...
```

### SemanticEncoder (`code/src/semantic_encoder.py`)

**Dependencies:** sentence_transformers, torch, typing  
**Status:** NEW (core mechanism)

```python
class SemanticEncoder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"): ...
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> torch.Tensor: ...
    def compute_similarity_matrix(self, embeddings1: torch.Tensor, embeddings2: torch.Tensor) -> torch.Tensor: ...
    def encode_assumptions_and_claims(self, assumptions: List[Dict], claims: List[Dict]) -> tuple: ...
```

### ContradictionDetector (`code/src/contradiction_detector.py`)

**Dependencies:** torch, typing  
**Status:** NEW

```python
class ContradictionDetector:
    def __init__(self, similarity_threshold: float = 0.3): ...
    def detect_contradictions(self, similarity_matrix: torch.Tensor, pairs: List[Dict]) -> List[Dict]: ...
    def flag_mismatches(self, pair: Dict, similarity: float) -> Dict: ...
    def save_contradictions(self, contradictions: List[Dict], output_path: Path) -> None: ...
```

### GroundTruthValidator (`code/src/ground_truth_validator.py`)

**Dependencies:** typing, json  
**Status:** NEW

```python
class GroundTruthValidator:
    def __init__(self, ground_truth_path: Path): ...
    def load_ground_truth(self) -> List[Dict]: ...
    def match_detected_to_ground_truth(self, detected: List[Dict], ground_truth: List[Dict]) -> Dict: ...
    def semantic_fuzzy_match(self, detected_item: Dict, gt_item: Dict, threshold: float = 0.7) -> bool: ...
    def compute_confusion_matrix(self, matches: Dict, total_pairs: int) -> Dict: ...
```

### GateEvaluator (`code/src/gate_evaluator.py`)

**Dependencies:** sklearn.metrics, typing  
**Status:** NEW

```python
class GateEvaluator:
    def __init__(self, recall_target: float = 0.70, recall_acceptable: float = 0.60, fp_rate_limit: float = 0.30): ...
    def compute_metrics(self, confusion_matrix: Dict) -> Dict: ...
    def check_gate_condition(self, metrics: Dict) -> Dict: ...
    def generate_metrics_report(self, metrics: Dict, gate_status: Dict) -> str: ...
    def save_results(self, results: Dict, output_path: Path) -> None: ...
```

### ThresholdTuner (`code/src/threshold_tuner.py`)

**Dependencies:** SemanticEncoder, ContradictionDetector, typing  
**Status:** NEW (optional exploration)

```python
class ThresholdTuner:
    def __init__(self, thresholds: List[float] = [0.2, 0.25, 0.3, 0.35, 0.4]): ...
    def tune_threshold(self, similarity_matrix: torch.Tensor, pairs: List[Dict], ground_truth: List[Dict]) -> List[Dict]: ...
    def find_optimal_threshold(self, tuning_results: List[Dict], fp_rate_limit: float = 0.30) -> Dict: ...
```

### Visualizer (`code/src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy  
**Status:** NEW

```python
class Visualizer:
    def __init__(self, output_dir: Path, dpi: int = 300): ...
    def plot_gate_metrics(self, metrics: Dict, gate_status: Dict) -> None: ...
    def plot_similarity_distribution(self, similarity_matrix: torch.Tensor, threshold: float) -> None: ...
    def plot_confusion_matrix(self, confusion: Dict) -> None: ...
    def plot_threshold_tuning_curve(self, tuning_results: List[Dict]) -> None: ...
    def plot_per_case_detection(self, detected_contradictions: List[Dict]) -> None: ...
    def generate_all_figures(self, results: Dict) -> None: ...
```

### Main (`code/src/main.py`)

**Dependencies:** All modules above, argparse  
**Status:** NEW

```python
def parse_arguments() -> argparse.Namespace: ...
def run_semantic_embedding(assumptions: List[Dict], claims: List[Dict], encoder: SemanticEncoder) -> tuple: ...
def run_detection(similarity_matrix: torch.Tensor, pairs: List[Dict], detector: ContradictionDetector) -> List[Dict]: ...
def run_validation(detected: List[Dict], ground_truth: List[Dict], validator: GroundTruthValidator, total_pairs: int) -> Dict: ...
def run_evaluation(confusion_matrix: Dict, evaluator: GateEvaluator) -> Dict: ...
def main() -> int: ...
```

---

## File Organization

```
{hypothesis_folder}/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── trace_parser.py           [REUSED from h-m2]
│   │   ├── data_loader.py            [NEW]
│   │   ├── semantic_encoder.py       [NEW - core mechanism]
│   │   ├── contradiction_detector.py [NEW]
│   │   ├── ground_truth_validator.py [NEW]
│   │   ├── gate_evaluator.py         [NEW]
│   │   ├── threshold_tuner.py        [NEW - optional]
│   │   ├── visualizer.py             [NEW]
│   │   └── main.py                   [NEW]
│   ├── config/
│   │   └── config.py                 [NEW]
│   ├── ground_truth/
│   │   └── known_failures.json       [NEW - h-e1, h-m1 cases]
│   ├── tests/
│   │   └── test_semantic_detection.py [NEW]
│   └── requirements.txt              [NEW]
├── figures/
│   ├── fig1_gate_metrics.png
│   ├── fig2_similarity_distribution.png
│   ├── fig3_confusion_matrix.png
│   ├── fig4_threshold_tuning.png
│   └── fig5_per_case_detection.png
├── detected_contradictions.json
├── h_m3_results.json
└── 03_architecture.md (this document)

{h-m2 folder}/outputs/
├── extracted_assumptions.json  [INPUT - from h-m2]
└── extracted_claims.json       [INPUT - from h-m2]
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TraceParser | `from src.trace_parser import TraceParser` | `h-m2/code/src/trace_parser.py` |

**Reuse Strategy:** Copy TraceParser from h-m2 (no modifications). Load h-m2 extraction outputs directly (JSON files).

**Verified from:** `docs/youra_research/h-m2/code/src/` (actual implementation)

---

## Configuration

### Config (`code/config/config.py`)

**Dependencies:** pathlib  
**Status:** NEW

```python
class Config:
    PROJECT_ROOT: Path
    H_M2_OUTPUT_FOLDER: Path
    OUTPUT_FOLDER: Path
    FIGURES_FOLDER: Path
    GROUND_TRUTH_FOLDER: Path
    RESULTS_FILE: Path
    CONTRADICTIONS_FILE: Path
    
    # Phase filtering
    EARLY_PHASES: List[int] = [1, 2, 3]
    LATER_PHASES: List[int] = [4, 5, 6]
    
    # Semantic embedding
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # Detection thresholds
    SIMILARITY_THRESHOLD: float = 0.3
    FUZZY_MATCH_THRESHOLD: float = 0.7
    
    # Gate thresholds
    RECALL_TARGET: float = 0.70
    RECALL_ACCEPTABLE: float = 0.60
    FP_RATE_LIMIT: float = 0.30
    
    # Threshold tuning (optional)
    ENABLE_THRESHOLD_TUNING: bool = True
    TUNING_THRESHOLDS: List[float] = [0.2, 0.25, 0.3, 0.35, 0.4]
    
    # Figure settings
    FIGURE_DPI: int = 300
    FIGURE_SIZE: tuple = (10, 6)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Setup Project Structure | Copy h-m2 TraceParser, create config.py, ground_truth/, tests/ dirs | 5 | Module(1) + Deps(1) + Algo(1) + Integ(2) |
| M3-2 | Implement Data Loader | Load h-m2 outputs, filter by phase (1-3 vs 4-6), create assumption-claim pairs | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| M3-3 | Implement Semantic Encoder | sentence-transformers integration, batch encoding, cosine similarity matrix | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) |
| M3-4 | Implement Contradiction Detector | Threshold filtering (similarity <0.3), flag contradictions with metadata | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| M3-5 | Implement Ground Truth Validator | Load known failures (h-e1, h-m1), fuzzy matching, confusion matrix computation | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| M3-6 | Implement Gate Evaluator | Recall/FP rate calculation, gate condition check (≥70% recall, <30% FP), report generation | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| M3-7 | Implement Threshold Tuner | Test 5 thresholds, compute recall-FP tradeoff, find optimal threshold | 10 | Module(2) + Deps(2) + Algo(4) + Integ(2) |
| M3-8 | Implement Visualizer | 5 figures (gate metrics, similarity distribution, confusion matrix, threshold curve, per-case) | 12 | Module(3) + Deps(2) + Algo(3) + Integ(4) |
| M3-9 | Create Ground Truth Annotations | Document h-e1 and h-m1 known failures as JSON with assumption/claim pairs | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |
| M3-10 | Implement Main Pipeline | Orchestration (load → encode → detect → validate → evaluate → visualize) | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| M3-11 | Integration & Testing | End-to-end validation, mock embeddings tests, gate check tests | 10 | Module(2) + Deps(2) + Algo(2) + Integ(4) |

**Total Complexity:** 100  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M3-3, M3-5, M3-7, M3-8, M3-11], Low(4-8): [M3-1, M3-2, M3-4, M3-6, M3-9, M3-10]

---

## Data Flow

### Input Loading (From h-m2)
1. `DataLoader.load_assumptions()` → List[Dict] (from h-m2/outputs/extracted_assumptions.json)
2. `DataLoader.load_claims()` → List[Dict] (from h-m2/outputs/extracted_claims.json)
3. `DataLoader.filter_by_phase()` → early_assumptions (Phase 1-3), later_claims (Phase 4-6)
4. `DataLoader.create_phase_pairs()` → all-pairs combination

### Semantic Embedding (New)
5. `SemanticEncoder.encode_texts(assumption_texts)` → assumption_embeddings (Tensor)
6. `SemanticEncoder.encode_texts(claim_texts)` → claim_embeddings (Tensor)
7. `SemanticEncoder.compute_similarity_matrix()` → similarity_matrix (shape: [N_assumptions, N_claims])

### Contradiction Detection (New)
8. `ContradictionDetector.detect_contradictions()` → flagged pairs (similarity < 0.3)
9. `ContradictionDetector.save_contradictions()` → detected_contradictions.json

### Ground Truth Validation (New)
10. `GroundTruthValidator.load_ground_truth()` → known failures (h-e1, h-m1)
11. `GroundTruthValidator.match_detected_to_ground_truth()` → TP, FP, FN counts
12. `GroundTruthValidator.compute_confusion_matrix()` → {TP, FP, FN, TN}

### Gate Evaluation (New)
13. `GateEvaluator.compute_metrics()` → recall, fp_rate, precision
14. `GateEvaluator.check_gate_condition()` → PASS/FAIL (≥70% recall, <30% FP)
15. `GateEvaluator.save_results()` → h_m3_results.json

### Threshold Tuning (Optional)
16. `ThresholdTuner.tune_threshold()` → test thresholds [0.2, 0.25, 0.3, 0.35, 0.4]
17. `ThresholdTuner.find_optimal_threshold()` → best threshold (max recall, FP <30%)

### Visualization (New)
18. `Visualizer.generate_all_figures()` → 5 PNG files

---

## Key Algorithms

### Semantic Similarity Matrix Computation

**Purpose:** Compare all assumption-claim pairs via cosine similarity

**Algorithm:**
```python
def compute_similarity_matrix(embeddings1, embeddings2):
    # embeddings1: [N_assumptions, embedding_dim]
    # embeddings2: [N_claims, embedding_dim]
    from sentence_transformers import util
    
    similarity_matrix = util.cos_sim(embeddings1, embeddings2)
    # Output: [N_assumptions, N_claims] matrix of cosine similarities [-1, 1]
    return similarity_matrix
```

**Model:** all-MiniLM-L6-v2 (384-dim embeddings, cosine similarity)

### Threshold-Based Contradiction Detection

**Purpose:** Flag assumption-claim pairs with low semantic similarity as contradictions

**Algorithm:**
```python
def detect_contradictions(similarity_matrix, pairs, threshold=0.3):
    contradictions = []
    for i, j in enumerate_pairs(pairs):
        sim_score = similarity_matrix[i][j].item()
        if sim_score < threshold:
            contradictions.append({
                'assumption': pairs[i]['assumption'],
                'claim': pairs[j]['claim'],
                'similarity': sim_score,
                'mismatch': True
            })
    return contradictions
```

**Threshold:** <0.3 = contradiction, ≥0.3 = match

### Fuzzy Ground Truth Matching

**Purpose:** Match detected contradictions to known failures (h-e1, h-m1) with semantic similarity

**Algorithm:**
```python
def semantic_fuzzy_match(detected_item, gt_item, threshold=0.7):
    # Encode both items and compute similarity
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    det_emb = encoder.encode(detected_item['assumption'] + ' ' + detected_item['claim'])
    gt_emb = encoder.encode(gt_item['assumption'] + ' ' + gt_item['claim'])
    
    similarity = util.cos_sim(det_emb, gt_emb).item()
    return similarity >= threshold
```

**Threshold:** ≥0.7 = match

### Confusion Matrix Computation

**Purpose:** Calculate TP, FP, FN, TN for recall and FP rate

**Formulas:**
```
TP = detected contradictions matching ground truth
FP = detected contradictions NOT in ground truth (false alarms)
FN = ground truth contradictions NOT detected (missed)
TN = non-contradictions correctly NOT flagged

Recall = TP / (TP + FN)  [≥0.70 target, ≥0.60 acceptable]
FP Rate = FP / (FP + TN)  [<0.30 limit]
```

---

## Ground Truth Structure

### Known Failures (`ground_truth/known_failures.json`)

```json
[
  {
    "id": "h-m1-effective-rank",
    "source": "h-m1 failure",
    "assumption": {
      "text": "effective rank decreases after SVD-based compression",
      "phase": 2,
      "tool_call_id": "tool_001"
    },
    "claim": {
      "text": "effective rank increased 6.02% compared to baseline",
      "phase": 5,
      "tool_call_id": "tool_042"
    },
    "contradiction_type": "numerical_direction",
    "severity": "high"
  },
  {
    "id": "h-e1-data-quality",
    "source": "h-e1 failure (if applicable)",
    "assumption": {
      "text": "dataset completeness assumed sufficient for validation",
      "phase": 1,
      "tool_call_id": "tool_005"
    },
    "claim": {
      "text": "NL content presence: 97.48% (missing 2.52%)",
      "phase": 4,
      "tool_call_id": "tool_038"
    },
    "contradiction_type": "completeness_threshold",
    "severity": "low"
  }
]
```

**Note:** Include only actual contradictions (h-m1 effective rank mismatch is confirmed). h-e1 may NOT be a true contradiction if 97.48% is acceptable.

---

## Error Handling Strategy

### Embedding Errors
- **Empty Texts:** Skip in batch encoding, log warning
- **Out of Memory:** Reduce batch_size from 32 → 16 → 8
- **Model Download Failure:** Cache model locally, provide offline fallback

### Detection Errors
- **Empty Similarity Matrix:** Raise ValueError with diagnostic info
- **All Pairs Flagged:** Log warning (threshold too high), suggest tuning
- **No Pairs Flagged:** Log warning (threshold too low), suggest tuning

### Validation Errors
- **Missing Ground Truth:** Abort evaluation, prompt for annotation
- **Zero TP/FN:** Handle division by zero (return recall = 0.0)
- **Zero FP/TN:** Handle division by zero (return fp_rate = 0.0)

### Gate Errors
- **Gate Failure:** Set status to FAIL, generate diagnostic plots (similarity distribution, threshold curve)
- **Threshold Tuning Recommended:** Log optimal threshold from tuning results

---

## Acceptance Criteria

### M3-1: Setup Project Structure
- [ ] Directories created: src/, config/, ground_truth/, figures/, tests/
- [ ] trace_parser.py copied from h-m2
- [ ] config.py created with all constants
- [ ] requirements.txt includes: sentence-transformers, torch, scikit-learn, matplotlib, seaborn

### M3-2: Implement Data Loader
- [ ] load_assumptions() loads h-m2/outputs/extracted_assumptions.json
- [ ] load_claims() loads h-m2/outputs/extracted_claims.json
- [ ] filter_by_phase() splits by Phase 1-3 vs 4-6
- [ ] create_phase_pairs() generates all-pairs combination

### M3-3: Implement Semantic Encoder
- [ ] Uses sentence-transformers library (all-MiniLM-L6-v2)
- [ ] encode_texts() returns PyTorch tensors
- [ ] compute_similarity_matrix() uses util.cos_sim
- [ ] Batch encoding with batch_size=32

### M3-4: Implement Contradiction Detector
- [ ] detect_contradictions() filters similarity < 0.3
- [ ] flag_mismatches() includes metadata (assumption, claim, similarity, phase sources)
- [ ] save_contradictions() writes detected_contradictions.json

### M3-5: Implement Ground Truth Validator
- [ ] load_ground_truth() parses known_failures.json
- [ ] semantic_fuzzy_match() uses sentence-transformers (threshold ≥0.7)
- [ ] compute_confusion_matrix() calculates TP, FP, FN, TN

### M3-6: Implement Gate Evaluator
- [ ] compute_metrics() calculates recall, fp_rate, precision
- [ ] check_gate_condition() validates ≥70% recall (≥60% acceptable), <30% FP rate
- [ ] generate_metrics_report() includes gate status (PASS/FAIL)
- [ ] save_results() writes h_m3_results.json

### M3-7: Implement Threshold Tuner
- [ ] tune_threshold() tests 5 thresholds [0.2, 0.25, 0.3, 0.35, 0.4]
- [ ] find_optimal_threshold() selects max recall with FP rate < 30%
- [ ] Returns tuning_results for visualization

### M3-8: Implement Visualizer
- [ ] plot_gate_metrics(): bar chart with target/acceptable/actual lines
- [ ] plot_similarity_distribution(): histogram with threshold vertical line
- [ ] plot_confusion_matrix(): heatmap (TP, FP, FN, TN)
- [ ] plot_threshold_tuning_curve(): recall and FP rate vs threshold
- [ ] plot_per_case_detection(): h-e1, h-m1 cases with similarity scores
- [ ] All figures save as 300 DPI PNG

### M3-9: Create Ground Truth Annotations
- [ ] known_failures.json documents h-e1 and h-m1 cases
- [ ] Each entry includes assumption/claim texts, phase sources, contradiction type, severity
- [ ] JSON schema validated

### M3-10: Implement Main Pipeline
- [ ] Orchestrates all modules in correct order
- [ ] CLI args: --h-m2-output, --output-folder, --enable-tuning
- [ ] Prints progress messages
- [ ] Exit code 0 if PASS, 1 if FAIL

### M3-11: Integration & Testing
- [ ] Mock sentence-transformers for testing (no real model loading)
- [ ] Unit test: similarity matrix computation
- [ ] Unit test: threshold filtering logic
- [ ] Unit test: confusion matrix calculation
- [ ] Unit test: gate condition check
- [ ] Integration test: mock 10 pairs → expected recall/FP rate
- [ ] End-to-end: process h-m2 outputs → h_m3_results.json + 5 figures

---

## Testing Strategy

### Unit Tests (`tests/test_semantic_detection.py`)
1. **test_similarity_matrix_computation**: Known embeddings → expected cosine similarities
2. **test_threshold_filtering**: Similarity matrix → correct contradiction flagging
3. **test_fuzzy_matching**: Known pairs → expected match/no-match
4. **test_confusion_matrix_calculation**: TP/FP/FN/TN counts → correct metrics
5. **test_gate_condition_check**: Edge cases (recall=0.69, 0.70, 0.60, FP=0.29, 0.30, 0.31)

### Integration Test
- **Mock Sentence Transformer:** Return predefined embeddings (no real model)
- **Mock h-m2 Outputs:** 10 assumption-claim pairs with known contradictions
- **Expected Output:** h_m3_results.json with known recall/FP rate
- **Validation:** All 5 figures created, gate decision correct

### End-to-End Test (Real Data)
- **Load h-m2 Outputs:** Actual extracted_assumptions.json and extracted_claims.json
- **Run Full Pipeline:** Embedding → Detection → Validation → Evaluation → Visualization
- **Manual Inspection:** Review detected_contradictions.json for h-e1/h-m1 cases
- **Gate Check:** Verify recall ≥60%, FP rate <30%

---

## Dependencies

### Python Packages
```
sentence-transformers>=2.2.0
torch>=2.0.0
scikit-learn>=1.0.0
matplotlib>=3.5.0
seaborn>=0.12.0
numpy>=1.21.0
```

### System Requirements
- Python 3.9+
- 2GB disk space (sentence-transformers model cache)
- GPU optional (CPU inference acceptable for <1000 pairs)
- No external API required (pre-trained models only)

### Pre-trained Models
- **Sentence Transformer:** all-MiniLM-L6-v2 (UKPLab/sentence-transformers)
- **Download:** Automatic via HuggingFace Hub (first run)
- **Cache:** ~/.cache/torch/sentence_transformers/

---

## Success Metrics

### Gate Condition (SHOULD_WORK)

**Primary:**
1. Mismatch detection recall ≥70% (target), ≥60% (acceptable)
2. False positive rate <30%

**Decision:** PASS if BOTH met, else FAIL (not fatal, iterate approach)

**Known Failure Detection:**
3. h-m1 effective rank contradiction correctly identified
4. h-e1 data quality case (verify if true contradiction)

### Deliverables
1. 9 Python modules (trace_parser, data_loader, semantic_encoder, contradiction_detector, ground_truth_validator, gate_evaluator, threshold_tuner, visualizer, main)
2. 1 ground truth annotation file (known_failures.json)
3. 5 PNG figures (gate metrics, similarity distribution, confusion matrix, threshold tuning, per-case detection)
4. 2 JSON files (detected_contradictions.json, h_m3_results.json)

---

## Risk Mitigation

### Risk: Terminological Mismatch (Probability 25%, Severity MEDIUM)
- **Impact:** Related concepts use different terms → low similarity → missed contradictions
- **Mitigation:**
  - Use semantic embeddings (sentence-transformers captures synonyms)
  - If recall <60%, try all-mpnet-base-v2 (better quality, 768-dim)
  - Alternative: hybrid LLM + semantic similarity approach
- **Residual Risk:** 10%

### Risk: Benign Constraint Violations (Probability 30%, Severity HIGH)
- **Impact:** Flagging benign differences (e.g., "approximately 50%" vs "exactly 47.3%") → high FP rate
- **Mitigation:**
  - Threshold tuning (explore [0.2, 0.4] range)
  - Post-hoc filtering: remove low-severity numeric differences
  - Alternative: severity ranking layer (filter by contradiction_type)
- **Residual Risk:** 15%

### Risk: Insufficient Ground Truth (Probability 20%, Severity MEDIUM)
- **Impact:** Only h-e1, h-m1 cases (2 known failures) → unreliable recall estimation
- **Mitigation:**
  - Manual review of 10-20 detected contradictions
  - Annotate additional ground truth if needed
  - Report recall range with confidence interval
- **Residual Risk:** 10%

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement all modules per Epic tasks  
**Estimated Effort:** 12-14 hours (11 Epic tasks, STANDARD complexity tier)
