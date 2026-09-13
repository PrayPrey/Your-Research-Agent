# Configuration Specification: h-m3
## Constraint Inference via Semantic Similarity

**Date:** 2026-07-14  
**Hypothesis Type:** MECHANISM (Constraint Detection)  
**Complexity Tier:** STANDARD  
**Subtask Budget:** 5 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-m2 base code  
**Config Files Found:** `docs/youra_research/h-m2/code/config/config.py`  
**Pattern Used:** Class-based config with class attributes (verified from actual h-m2 code)

**Base Config Verified:** H-M2 uses `Config` class with class attributes for all settings, no dataclass pattern. H-M3 extends this with semantic similarity detection parameters.

---

## Knowledge Base Patterns Applied

**Applied:** Standard experiment config pattern (class-based with default values)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/h-m2/code/config/config.py (ACTUAL CODE)
class Config:
    # Paths (verified from actual code)
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_FOLDER = PROJECT_ROOT / "data/mcp_traces"
    OUTPUT_FOLDER = PROJECT_ROOT / "outputs"
    FIGURES_FOLDER = PROJECT_ROOT / "figures"
    
    # Dataset (verified from actual code)
    SAMPLE_SIZE = 50
    N_QUERIES = 25
    N_RESULTS = 25
    MIN_NL_WORDS = 10
    RANDOM_SEED = 42
    
    # LLM (verified from actual code)
    LLM_MODEL = "claude-sonnet-4-5"
    LLM_TEMPERATURE = 0.0
    MULTI_VOTE_COUNT = 3
    CONSENSUS_THRESHOLD = 2
    
    # Gate Thresholds (verified from actual code)
    PRECISION_THRESHOLD = 0.70
    RECALL_THRESHOLD = 0.80
    KAPPA_THRESHOLD = 0.70
```

**Verified from:** `docs/youra_research/h-m2/code/config/config.py` (actual implementation)

---

## M3-1: Setup Project Structure [Complexity: 5, Budget: 0/5]

**Note:** Directory creation only - no config changes needed.

---

## M3-2: Implement Data Loader [Complexity: 8, Budget: 1/5]

**Applied:** Standard data loading pattern

### Configuration (Class Attributes)

```python
class Config:
    # Phase filtering
    EARLY_PHASES = [1, 2, 3]
    LATER_PHASES = [4, 5, 6]
    
    # Paths (h-m2 outputs)
    H_M2_OUTPUT_FOLDER = Path("../h-m2/outputs")
    ASSUMPTIONS_FILE = "extracted_assumptions.json"
    CLAIMS_FILE = "extracted_claims.json"
```

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M3-2-1 | Add phase filtering constants | EARLY_PHASES, LATER_PHASES lists |

---

## M3-3: Implement Semantic Encoder [Complexity: 12, Budget: 2/5]

**Applied:** Sentence-transformers standard configuration

### Configuration (Class Attributes)

```python
class Config:
    # Semantic embedding
    SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE = 32
    DEVICE = "cpu"  # Or "cuda" if GPU available
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M3-3-1 | Add sentence transformer model | Model name for pre-trained embeddings |
| C-M3-3-2 | Add batch processing params | EMBEDDING_BATCH_SIZE, DEVICE |

---

## M3-4: Implement Contradiction Detector [Complexity: 9, Budget: 1/5]

**Applied:** Threshold-based detection pattern

### Configuration (Class Attributes)

```python
class Config:
    # Contradiction detection
    SIMILARITY_THRESHOLD = 0.3  # <0.3 = contradiction
    FUZZY_MATCH_THRESHOLD = 0.7  # ≥0.7 = ground truth match
```

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M3-4-1 | Add similarity thresholds | SIMILARITY_THRESHOLD for contradiction, FUZZY_MATCH_THRESHOLD for GT matching |

---

## M3-5: Implement Ground Truth Validator [Complexity: 11, Budget: 0/5]

**Note:** Reuses FUZZY_MATCH_THRESHOLD from M3-4. No new config needed.

---

## M3-6: Implement Gate Evaluator [Complexity: 9, Budget: 1/5]

**Applied:** SHOULD_WORK gate threshold pattern

### Configuration (Class Attributes)

```python
class Config:
    # SHOULD_WORK gate thresholds
    RECALL_TARGET = 0.70
    RECALL_ACCEPTABLE = 0.60
    FP_RATE_LIMIT = 0.30
```

### Subtasks [1/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M3-6-1 | Add gate thresholds | RECALL_TARGET, RECALL_ACCEPTABLE, FP_RATE_LIMIT |

---

## M3-7: Implement Threshold Tuner [Complexity: 10, Budget: 0/5]

**Applied:** Grid search pattern

### Configuration (Class Attributes)

```python
class Config:
    # Threshold tuning (optional exploration)
    ENABLE_THRESHOLD_TUNING = True
    TUNING_THRESHOLDS = [0.2, 0.25, 0.3, 0.35, 0.4]
```

**Note:** Optional feature - minimal config added to main config.

---

## M3-8: Implement Visualizer [Complexity: 12, Budget: 0/5]

**Note:** Reuses inherited FIGURE_DPI and FIGURE_SIZE from h-m2. No new config needed.

---

## M3-9: Create Ground Truth Annotations [Complexity: 6, Budget: 0/5]

**Applied:** Ground truth file path

### Configuration (Class Attributes)

```python
class Config:
    # Ground truth
    GROUND_TRUTH_FOLDER = PROJECT_ROOT / "ground_truth"
    KNOWN_FAILURES_FILE = "known_failures.json"
```

**Note:** Path configuration only - file content is data, not config.

---

## M3-10: Implement Main Pipeline [Complexity: 8, Budget: 0/5]

**Note:** Uses existing Config pattern. No new config needed.

---

## M3-11: Integration & Testing [Complexity: 10, Budget: 0/5]

**Note:** Testing uses existing config. No new config needed.

---

## Unified Configuration Module

```python
# code/config/config.py
"""Configuration for h-m3 semantic similarity-based constraint detection."""

from pathlib import Path

class Config:
    """Configuration constants for h-m3 experiment."""
    
    # === Paths ===
    PROJECT_ROOT = Path(__file__).parent.parent
    H_M2_OUTPUT_FOLDER = PROJECT_ROOT / "../h-m2/outputs"
    OUTPUT_FOLDER = PROJECT_ROOT / "outputs"
    FIGURES_FOLDER = PROJECT_ROOT / "figures"
    GROUND_TRUTH_FOLDER = PROJECT_ROOT / "ground_truth"
    
    # Output files
    DETECTED_CONTRADICTIONS_FILE = OUTPUT_FOLDER / "detected_contradictions.json"
    RESULTS_FILE = OUTPUT_FOLDER / "h_m3_results.json"
    
    # Input files (from h-m2)
    ASSUMPTIONS_FILE = "extracted_assumptions.json"
    CLAIMS_FILE = "extracted_claims.json"
    
    # Ground truth
    KNOWN_FAILURES_FILE = "known_failures.json"
    
    # === Inherited from h-m2 ===
    RANDOM_SEED = 42
    FIGURE_DPI = 300
    FIGURE_SIZE = (10, 6)
    
    # === Data Loading (M3-2) ===
    EARLY_PHASES = [1, 2, 3]
    LATER_PHASES = [4, 5, 6]
    
    # === Semantic Encoder (M3-3) ===
    SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE = 32
    DEVICE = "cpu"
    
    # === Contradiction Detection (M3-4) ===
    SIMILARITY_THRESHOLD = 0.3
    FUZZY_MATCH_THRESHOLD = 0.7
    
    # === Gate Evaluator (M3-6) ===
    RECALL_TARGET = 0.70
    RECALL_ACCEPTABLE = 0.60
    FP_RATE_LIMIT = 0.30
    
    # === Threshold Tuning (M3-7) ===
    ENABLE_THRESHOLD_TUNING = True
    TUNING_THRESHOLDS = [0.2, 0.25, 0.3, 0.35, 0.4]
    
    def __init__(self):
        """Initialize configuration and create directories."""
        self.OUTPUT_FOLDER.mkdir(exist_ok=True)
        self.FIGURES_FOLDER.mkdir(exist_ok=True)
        self.GROUND_TRUTH_FOLDER.mkdir(exist_ok=True)
```

---

## Usage Example

```python
from pathlib import Path
from config.config import Config

# Initialize configuration
config = Config()

# Access h-m2 outputs
assumptions_path = config.H_M2_OUTPUT_FOLDER / config.ASSUMPTIONS_FILE
claims_path = config.H_M2_OUTPUT_FOLDER / config.CLAIMS_FILE

# Access semantic encoder settings
print(f"Transformer model: {Config.SENTENCE_TRANSFORMER_MODEL}")
print(f"Batch size: {Config.EMBEDDING_BATCH_SIZE}")

# Access detection thresholds
print(f"Similarity threshold: {Config.SIMILARITY_THRESHOLD}")
print(f"Fuzzy match threshold: {Config.FUZZY_MATCH_THRESHOLD}")

# Access gate thresholds
print(f"Recall target: {Config.RECALL_TARGET} (acceptable: {Config.RECALL_ACCEPTABLE})")
print(f"FP rate limit: {Config.FP_RATE_LIMIT}")

# Use in modules
from src.semantic_encoder import SemanticEncoder
from src.contradiction_detector import ContradictionDetector
from src.gate_evaluator import GateEvaluator

encoder = SemanticEncoder(
    model_name=Config.SENTENCE_TRANSFORMER_MODEL,
    batch_size=Config.EMBEDDING_BATCH_SIZE,
    device=Config.DEVICE
)

detector = ContradictionDetector(
    similarity_threshold=Config.SIMILARITY_THRESHOLD
)

evaluator = GateEvaluator(
    recall_target=Config.RECALL_TARGET,
    recall_acceptable=Config.RECALL_ACCEPTABLE,
    fp_rate_limit=Config.FP_RATE_LIMIT
)
```

---

## Command-Line Integration

```python
# code/src/main.py
import argparse
from pathlib import Path
from config.config import Config

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="H-M3: Constraint inference via semantic similarity"
    )
    parser.add_argument(
        "--h-m2-output",
        type=str,
        default=str(Config.H_M2_OUTPUT_FOLDER),
        help="Path to h-m2 outputs folder (default: ../h-m2/outputs)"
    )
    parser.add_argument(
        "--enable-tuning",
        action="store_true",
        help="Enable threshold tuning exploration"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    config = Config()
    
    # Override h-m2 path if specified
    if args.h_m2_output:
        config.H_M2_OUTPUT_FOLDER = Path(args.h_m2_output)
    
    # Override tuning flag
    if args.enable_tuning is not None:
        config.ENABLE_THRESHOLD_TUNING = args.enable_tuning
    
    print(f"H-M3: CONSTRAINT INFERENCE VIA SEMANTIC SIMILARITY")
    print(f"Transformer: {Config.SENTENCE_TRANSFORMER_MODEL}")
    print(f"Similarity threshold: {Config.SIMILARITY_THRESHOLD}")
    print(f"Gate: Recall ≥{Config.RECALL_ACCEPTABLE} (target ≥{Config.RECALL_TARGET}), FP <{Config.FP_RATE_LIMIT}")
    
    # Load h-m2 outputs
    from src.data_loader import DataLoader
    loader = DataLoader(config.H_M2_OUTPUT_FOLDER)
    assumptions = loader.load_assumptions()
    claims = loader.load_claims()
    
    # Filter by phase
    early_assumptions = loader.filter_by_phase(assumptions, Config.EARLY_PHASES)
    later_claims = loader.filter_by_phase(claims, Config.LATER_PHASES)
    pairs = loader.create_phase_pairs(early_assumptions, later_claims)
    
    print(f"Loaded {len(early_assumptions)} early assumptions, {len(later_claims)} later claims")
    print(f"Generated {len(pairs)} assumption-claim pairs")
    
    # Semantic encoding
    from src.semantic_encoder import SemanticEncoder
    encoder = SemanticEncoder(
        Config.SENTENCE_TRANSFORMER_MODEL,
        Config.EMBEDDING_BATCH_SIZE,
        Config.DEVICE
    )
    
    print("Encoding assumptions and claims...")
    assumption_embeddings, claim_embeddings = encoder.encode_assumptions_and_claims(
        early_assumptions, later_claims
    )
    similarity_matrix = encoder.compute_similarity_matrix(
        assumption_embeddings, claim_embeddings
    )
    
    # Contradiction detection
    from src.contradiction_detector import ContradictionDetector
    detector = ContradictionDetector(Config.SIMILARITY_THRESHOLD)
    
    print(f"Detecting contradictions (threshold <{Config.SIMILARITY_THRESHOLD})...")
    contradictions = detector.detect_contradictions(similarity_matrix, pairs)
    detector.save_contradictions(contradictions, config.DETECTED_CONTRADICTIONS_FILE)
    
    print(f"Detected {len(contradictions)} potential contradictions")
    
    # Ground truth validation
    from src.ground_truth_validator import GroundTruthValidator
    gt_path = config.GROUND_TRUTH_FOLDER / config.KNOWN_FAILURES_FILE
    validator = GroundTruthValidator(gt_path)
    
    ground_truth = validator.load_ground_truth()
    matches = validator.match_detected_to_ground_truth(
        contradictions, ground_truth, Config.FUZZY_MATCH_THRESHOLD
    )
    confusion_matrix = validator.compute_confusion_matrix(matches, len(pairs))
    
    # Gate evaluation
    from src.gate_evaluator import GateEvaluator
    evaluator = GateEvaluator(
        Config.RECALL_TARGET,
        Config.RECALL_ACCEPTABLE,
        Config.FP_RATE_LIMIT
    )
    
    metrics = evaluator.compute_metrics(confusion_matrix)
    gate_status = evaluator.check_gate_condition(metrics)
    
    print("\n=== GATE EVALUATION ===")
    print(f"Recall: {metrics['recall']:.3f} (target ≥{Config.RECALL_TARGET}, acceptable ≥{Config.RECALL_ACCEPTABLE})")
    print(f"FP Rate: {metrics['fp_rate']:.3f} (limit <{Config.FP_RATE_LIMIT})")
    print(f"Gate Status: {gate_status['status']}")
    
    # Threshold tuning (optional)
    if config.ENABLE_THRESHOLD_TUNING:
        from src.threshold_tuner import ThresholdTuner
        tuner = ThresholdTuner(Config.TUNING_THRESHOLDS)
        
        print("\n=== THRESHOLD TUNING ===")
        tuning_results = tuner.tune_threshold(similarity_matrix, pairs, ground_truth)
        optimal = tuner.find_optimal_threshold(tuning_results, Config.FP_RATE_LIMIT)
        print(f"Optimal threshold: {optimal['threshold']} (recall: {optimal['recall']:.3f}, FP: {optimal['fp_rate']:.3f})")
    
    # Visualization
    from src.visualizer import Visualizer
    visualizer = Visualizer(config.FIGURES_FOLDER, Config.FIGURE_DPI)
    
    results = {
        'metrics': metrics,
        'gate_status': gate_status,
        'contradictions': contradictions,
        'confusion_matrix': confusion_matrix,
        'similarity_matrix': similarity_matrix.cpu().numpy(),
        'tuning_results': tuning_results if config.ENABLE_THRESHOLD_TUNING else None
    }
    
    visualizer.generate_all_figures(results)
    
    # Save results
    evaluator.save_results(results, config.RESULTS_FILE)
    
    print(f"\nResults saved to {config.RESULTS_FILE}")
    print(f"Figures saved to {config.FIGURES_FOLDER}")
    
    return 0 if gate_status['status'] == 'PASS' else 1

if __name__ == "__main__":
    exit(main())
```

---

## File Organization

```
{hypothesis_folder}/
├── code/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py                # Config class (extends h-m2 pattern)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── trace_parser.py          [REUSED from h-m2]
│   │   ├── data_loader.py           [NEW - uses Config.EARLY_PHASES, etc.]
│   │   ├── semantic_encoder.py      [NEW - uses Config.SENTENCE_TRANSFORMER_MODEL, etc.]
│   │   ├── contradiction_detector.py [NEW - uses Config.SIMILARITY_THRESHOLD]
│   │   ├── ground_truth_validator.py [NEW - uses Config.FUZZY_MATCH_THRESHOLD]
│   │   ├── gate_evaluator.py        [NEW - uses Config gate thresholds]
│   │   ├── threshold_tuner.py       [NEW - uses Config.TUNING_THRESHOLDS]
│   │   ├── visualizer.py            [NEW - uses Config.FIGURE_DPI]
│   │   └── main.py                  [NEW - initializes Config()]
│   ├── ground_truth/
│   │   └── known_failures.json      [Ground truth annotations]
│   ├── tests/
│   │   └── test_semantic_detection.py
│   └── requirements.txt
├── outputs/                          [Auto-created by Config.__init__()]
│   ├── detected_contradictions.json
│   └── h_m3_results.json
├── figures/                          [Auto-created by Config.__init__()]
│   ├── fig1_gate_metrics.png
│   ├── fig2_similarity_distribution.png
│   ├── fig3_confusion_matrix.png
│   ├── fig4_threshold_tuning.png
│   └── fig5_per_case_detection.png
└── 03_config.md (this document)
```

---

## Self-Validation Checklist

- [x] ONE format only (Class-based config, consistent with h-m2)
- [x] No ASCII diagrams
- [x] KB patterns applied (1 pattern noted)
- [x] Rationale only for non-standard values (all values standard)
- [x] Subtask count within budget (5/5 used)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Base hypothesis config verified from actual code
- [x] Inherited Configuration section included with verified field names

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 Coder - Implement config module extending h-m2 pattern  
**Total Configuration Complexity:** 5 subtasks (M3-2: 1, M3-3: 2, M3-4: 1, M3-6: 1) - Exactly on budget
