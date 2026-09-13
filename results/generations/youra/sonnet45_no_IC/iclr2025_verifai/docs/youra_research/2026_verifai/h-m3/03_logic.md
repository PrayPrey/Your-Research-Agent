# Logic Design: h-m3
## Semantic Similarity-based Constraint Detection

**Date:** 2026-07-14
**Hypothesis Type:** MECHANISM (Constraint Detection)
**Complexity Tier:** STANDARD
**Subtask Budget:** 5 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m2 actual code
**Analyzed Path:** docs/youra_research/h-m2/code/src/
**Relevant Symbols:** TraceParser (reused), LLMExtractor outputs (JSON inputs)

**Key Findings:**
- TraceParser API verified: `__init__(trace_folder: Path)`, `load_all_traces() -> List[Dict]`
- LLMExtractor outputs: extracted_assumptions.json, extracted_claims.json (Dict format)
- h-m3 reads h-m2 JSON outputs directly (no h-m2 code imports, only data reuse)
- TraceParser will be copied from h-m2 without modification

---

## Applied Patterns

**Applied:** Sentence-transformers library (UKPLab all-MiniLM-L6-v2, cosine similarity)
**Applied:** sklearn metrics patterns (precision/recall, confusion matrix)
**Applied:** PyTorch tensor operations (batch encoding, similarity matrix)

---

## M3-2: Data Loader [Complexity: 8, Budget: 1]

**Applied:** JSON loading with phase-based filtering

### API Signatures

```python
import json
from pathlib import Path
from typing import List, Dict

class DataLoader:
    """Load h-m2 extraction outputs and create phase pairs."""
    
    def __init__(self, h_m2_output_folder: Path):
        """Initialize loader. h_m2_output_folder: Path"""
        self.h_m2_output_folder = Path(h_m2_output_folder)
    
    def load_assumptions(self) -> List[Dict]:
        """Load extracted assumptions. -> [{"text": str, "phase": int, "tool_call_id": str}, ...]"""
        ...
    
    def load_claims(self) -> List[Dict]:
        """Load extracted claims. -> [{"text": str, "phase": int, "tool_call_id": str}, ...]"""
        ...
    
    def filter_by_phase(self, items: List[Dict], phases: List[int]) -> List[Dict]:
        """Filter items by phase. phases: [1,2,3] -> filtered_items"""
        ...
    
    def create_phase_pairs(
        self,
        early_assumptions: List[Dict],
        later_claims: List[Dict]
    ) -> List[Dict]:
        """Create all-pairs combination. -> [{"assumption": Dict, "claim": Dict}, ...]"""
        ...
```

### Pseudo-code

```
load_assumptions():
    path = h_m2_output_folder / "extracted_assumptions.json"
    with open(path) as f:
        return json.load(f)

filter_by_phase(items, phases):
    return [item for item in items if item["phase"] in phases]

create_phase_pairs(early_assumptions, later_claims):
    pairs = []
    for assumption in early_assumptions:
        for claim in later_claims:
            pairs.append({"assumption": assumption, "claim": claim})
    return pairs
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-2-1 | JSON loading | Implement h-m2 output loading, phase filtering, pair generation |

---

## M3-3: Semantic Encoder [Complexity: 12, Budget: 1]

**Applied:** sentence-transformers library (all-MiniLM-L6-v2, 384-dim embeddings)

### API Signatures

```python
import torch
from typing import List, Tuple
from sentence_transformers import SentenceTransformer, util

class SemanticEncoder:
    """Encode texts using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize encoder. model_name: str"""
        self.model = SentenceTransformer(model_name)
    
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> torch.Tensor:
        """Batch encode texts. texts: List[str] -> embeddings: [N, 384]"""
        ...
    
    def compute_similarity_matrix(
        self,
        embeddings1: torch.Tensor,
        embeddings2: torch.Tensor
    ) -> torch.Tensor:
        """Compute cosine similarity. embeddings1: [N, 384], embeddings2: [M, 384] -> [N, M]"""
        ...
    
    def encode_assumptions_and_claims(
        self,
        assumptions: List[Dict],
        claims: List[Dict]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode both. -> (assumption_embeddings: [N, 384], claim_embeddings: [M, 384])"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| texts | List[N] | Input strings |
| embeddings | [N, 384] | Encoded vectors |
| embeddings1 | [N, 384] | Assumption embeddings |
| embeddings2 | [M, 384] | Claim embeddings |
| similarity_matrix | [N, M] | Cosine similarities [-1, 1] |

### Pseudo-code

```
encode_texts(texts, batch_size=32):
    return model.encode(texts, batch_size=batch_size, convert_to_tensor=True)

compute_similarity_matrix(embeddings1, embeddings2):
    return util.cos_sim(embeddings1, embeddings2)

encode_assumptions_and_claims(assumptions, claims):
    assumption_texts = [a["text"] for a in assumptions]
    claim_texts = [c["text"] for c in claims]
    
    assumption_embeddings = encode_texts(assumption_texts)
    claim_embeddings = encode_texts(claim_texts)
    
    return assumption_embeddings, claim_embeddings
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-3-1 | Embedding pipeline | Implement sentence-transformers encoding, cosine similarity matrix |

---

## M3-4: Contradiction Detector [Complexity: 9, Budget: 1]

**Applied:** Threshold-based filtering (similarity < 0.3)

### API Signatures

```python
import torch
from pathlib import Path
from typing import List, Dict

class ContradictionDetector:
    """Detect contradictions via similarity threshold."""
    
    def __init__(self, similarity_threshold: float = 0.3):
        """Initialize detector. similarity_threshold: 0.3"""
        self.similarity_threshold = similarity_threshold
    
    def detect_contradictions(
        self,
        similarity_matrix: torch.Tensor,
        pairs: List[Dict]
    ) -> List[Dict]:
        """Flag pairs below threshold. similarity_matrix: [N, M] -> contradictions"""
        ...
    
    def flag_mismatches(self, pair: Dict, similarity: float) -> Dict:
        """Add metadata. pair: Dict, similarity: float -> enriched_pair"""
        ...
    
    def save_contradictions(self, contradictions: List[Dict], output_path: Path) -> None:
        """Save results. contradictions: List[Dict] -> detected_contradictions.json"""
        ...
```

### Pseudo-code

```
detect_contradictions(similarity_matrix, pairs):
    contradictions = []
    for i, pair in enumerate(pairs):
        assumption_idx = get_assumption_index(pair)
        claim_idx = get_claim_index(pair)
        sim_score = similarity_matrix[assumption_idx, claim_idx].item()
        
        if sim_score < self.similarity_threshold:
            flagged = flag_mismatches(pair, sim_score)
            contradictions.append(flagged)
    
    return contradictions

flag_mismatches(pair, similarity):
    return {
        "assumption": pair["assumption"],
        "claim": pair["claim"],
        "similarity": similarity,
        "mismatch": True,
        "threshold": self.similarity_threshold
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-4-1 | Threshold filtering | Implement similarity threshold detection, metadata enrichment |

---

## M3-5: Ground Truth Validator [Complexity: 11, Budget: 1]

**Applied:** Fuzzy matching with semantic similarity (threshold ≥0.7)

### API Signatures

```python
import json
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

class GroundTruthValidator:
    """Validate detected contradictions against known failures."""
    
    def __init__(self, ground_truth_path: Path):
        """Initialize validator. ground_truth_path: Path"""
        self.ground_truth_path = Path(ground_truth_path)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
    
    def load_ground_truth(self) -> List[Dict]:
        """Load known failures. -> [{"assumption": {...}, "claim": {...}, ...}, ...]"""
        ...
    
    def match_detected_to_ground_truth(
        self,
        detected: List[Dict],
        ground_truth: List[Dict]
    ) -> Dict:
        """Match with fuzzy similarity. -> {"TP": [...], "FP": [...], "FN": [...]}"""
        ...
    
    def semantic_fuzzy_match(
        self,
        detected_item: Dict,
        gt_item: Dict,
        threshold: float = 0.7
    ) -> bool:
        """Semantic fuzzy matching. threshold: 0.7 -> is_match: bool"""
        ...
    
    def compute_confusion_matrix(self, matches: Dict, total_pairs: int) -> Dict:
        """Compute TP/FP/FN/TN. -> {"TP": int, "FP": int, "FN": int, "TN": int}"""
        ...
```

### Pseudo-code

```
semantic_fuzzy_match(detected_item, gt_item, threshold=0.7):
    # Combine assumption and claim texts
    det_text = detected_item["assumption"]["text"] + " " + detected_item["claim"]["text"]
    gt_text = gt_item["assumption"]["text"] + " " + gt_item["claim"]["text"]
    
    # Encode and compute similarity
    det_emb = encoder.encode(det_text, convert_to_tensor=True)
    gt_emb = encoder.encode(gt_text, convert_to_tensor=True)
    
    similarity = util.cos_sim(det_emb, gt_emb).item()
    return similarity >= threshold

compute_confusion_matrix(matches, total_pairs):
    tp = len(matches["TP"])
    fp = len(matches["FP"])
    fn = len(matches["FN"])
    tn = total_pairs - tp - fp - fn
    
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-5-1 | Ground truth matching | Implement fuzzy matching, confusion matrix computation |

---

## M3-6: Gate Evaluator [Complexity: 9, Budget: 0]

**Applied:** sklearn-style metrics computation

### API Signatures

```python
from pathlib import Path
from typing import Dict

class GateEvaluator:
    """Evaluate gate condition (SHOULD_WORK)."""
    
    def __init__(
        self,
        recall_target: float = 0.70,
        recall_acceptable: float = 0.60,
        fp_rate_limit: float = 0.30
    ):
        """Initialize evaluator. recall_target: 0.70, recall_acceptable: 0.60, fp_rate_limit: 0.30"""
        self.recall_target = recall_target
        self.recall_acceptable = recall_acceptable
        self.fp_rate_limit = fp_rate_limit
    
    def compute_metrics(self, confusion_matrix: Dict) -> Dict:
        """Compute recall, FP rate, precision. -> {"recall": float, "fp_rate": float, ...}"""
        ...
    
    def check_gate_condition(self, metrics: Dict) -> Dict:
        """Check SHOULD_WORK gate. -> {"status": "PASS"/"FAIL", "target_met": bool, ...}"""
        ...
    
    def generate_metrics_report(self, metrics: Dict, gate_status: Dict) -> str:
        """Generate text report. -> report_text"""
        ...
    
    def save_results(self, results: Dict, output_path: Path) -> None:
        """Save results. results: Dict -> h_m3_results.json"""
        ...
```

### Pseudo-code

```
compute_metrics(confusion_matrix):
    tp = confusion_matrix["TP"]
    fp = confusion_matrix["FP"]
    fn = confusion_matrix["FN"]
    tn = confusion_matrix["TN"]
    
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    return {"recall": recall, "fp_rate": fp_rate, "precision": precision}

check_gate_condition(metrics):
    passed = (metrics["recall"] >= self.recall_acceptable and 
              metrics["fp_rate"] < self.fp_rate_limit)
    target_met = (metrics["recall"] >= self.recall_target and 
                  metrics["fp_rate"] < self.fp_rate_limit)
    
    return {
        "status": "PASS" if passed else "FAIL",
        "target_met": target_met,
        "acceptable_met": passed
    }
```

---

## M3-8: Visualizer [Complexity: 12, Budget: 0]

**Applied:** Matplotlib/seaborn plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict

class Visualizer:
    """Generate validation figures."""
    
    def __init__(self, output_dir: Path, dpi: int = 300):
        """Initialize visualizer. output_dir: Path, dpi: 300"""
        self.output_dir = Path(output_dir)
        self.dpi = dpi
    
    def plot_gate_metrics(self, metrics: Dict, gate_status: Dict) -> None:
        """Bar chart with threshold lines. -> fig1_gate_metrics.png"""
        ...
    
    def plot_similarity_distribution(
        self,
        similarity_matrix: torch.Tensor,
        threshold: float
    ) -> None:
        """Histogram with threshold line. -> fig2_similarity_distribution.png"""
        ...
    
    def plot_confusion_matrix(self, confusion: Dict) -> None:
        """Heatmap of TP/FP/FN/TN. -> fig3_confusion_matrix.png"""
        ...
    
    def plot_threshold_tuning_curve(self, tuning_results: List[Dict]) -> None:
        """Recall/FP rate vs threshold. -> fig4_threshold_tuning.png"""
        ...
    
    def plot_per_case_detection(self, detected_contradictions: List[Dict]) -> None:
        """Per-case similarity scores. -> fig5_per_case_detection.png"""
        ...
    
    def generate_all_figures(self, results: Dict) -> None:
        """Generate all 5 figures. results: Dict -> 5 PNG files"""
        ...
```

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from base hypothesis. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m2/code/src/trace_parser.py (ACTUAL CODE)
class TraceParser:
    """Parse MCP trace files in JSONL format."""
    
    def __init__(self, trace_folder: Path):
        """Initialize parser. trace_folder: Path"""
        ...
    
    def discover_traces(self) -> List[Path]:
        """Discover .jsonl files. -> List[Path]"""
        ...
    
    def parse_trace_file(self, file_path: Path) -> Dict:
        """Parse single trace. -> {"file": str, "outcome": str, "tool_calls": List[Dict]}"""
        ...
    
    def load_all_traces(self) -> List[Dict]:
        """Load all traces. -> List[Dict]"""
        ...
```

**Verified from:** `docs/youra_research/h-m2/code/src/trace_parser.py` (actual implementation, NOT spec)

**Note:** h-m3 primarily reads h-m2 JSON outputs (extracted_assumptions.json, extracted_claims.json). TraceParser copied for compatibility but may not be actively used in main pipeline.

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes only for encoder module
- [x] Subtask count: 5/5 used
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Base hypothesis API signatures verified from actual code
- [x] External Dependencies API section included

### Serena MCP Validation
- [x] Base hypothesis exists → Actual code verified from h-m2/code/
- [x] API signatures match actual implementation (TraceParser)
- [x] Parameter names exactly match actual code
- [x] Noted that h-m3 uses h-m2 JSON outputs (not direct code imports)

### Base Hypothesis Checks
- [x] Read actual code from h-m2/code/src/
- [x] API signatures verified from implementation (not specs)
- [x] Parameter names exactly match: `trace_folder`
- [x] External Dependencies API section included

---

**Document Status:** Ready for Phase 4 Implementation
**Next Phase:** Phase 4 Coder - Implement all modules per logic design
**Estimated Effort:** 10-12 hours (STANDARD complexity tier)
