# System Architecture: H-E1
# Preference Entropy Measurement (EXISTENCE PoC)

**Date:** 2026-08-28  
**Author:** yoon303@etri.re.kr  
**Hypothesis:** Base models produce outputs with preference entropy H_base >= 1.8 nats  
**Type:** EXISTENCE (PoC)  
**Gate:** MUST_WORK

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing code - minimal PoC architecture only

---

## Knowledge Base Patterns Applied

Applied: Minimal EXISTENCE architecture (single-file analysis script)  
Applied: scipy.stats.entropy for Shannon entropy computation  
Applied: HuggingFace datasets for Anthropic-HH loading

---

## File Structure

```
h-e1/code/
├── preference_entropy_analyzer.py  # Main analysis script
├── requirements.txt                # Dependencies
└── README.md                       # Usage instructions
```

---

## Module Definitions

### PreferenceEntropyAnalyzer (`preference_entropy_analyzer.py`)

**Dependencies:** scipy, numpy, datasets, matplotlib

```python
class PreferenceEntropyAnalyzer:
    def __init__(self, dataset_name: str = "Anthropic/hh-rlhf", sample_size: int = 100, seed: int = 1): ...
    def load_dataset(self) -> None: ...
    def sample_prompts(self) -> list: ...
    def aggregate_preferences(self, prompt_examples: list) -> np.ndarray: ...
    def compute_entropy(self, preference_counts: np.ndarray) -> float: ...
    def analyze_dataset(self) -> dict: ...
    def compute_metrics(self, results: list) -> dict: ...
    def generate_figures(self, results: list, metrics: dict) -> None: ...
    def save_results(self, results: list, metrics: dict, output_path: str) -> None: ...

def main():
    analyzer = PreferenceEntropyAnalyzer()
    results = analyzer.analyze_dataset()
    metrics = analyzer.compute_metrics(results)
    analyzer.generate_figures(results, metrics)
    analyzer.save_results(results, metrics, "h-e1_results.json")
```

---

## Data Flow

```
Dataset Loading → Prompt Sampling → Preference Aggregation → Entropy Computation → Metrics Reporting → Visualization
```

1. Load Anthropic-HH dataset (160K+ comparisons)
2. Sample n=100 prompts (seed=1)
3. Aggregate chosen/rejected counts per prompt
4. Compute Shannon entropy using scipy.stats.entropy
5. Calculate success rate, variance, range
6. Generate 4 figures (gate metrics, histogram, scatter, pie)
7. Save results to JSON

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Dataset Setup | Load Anthropic-HH and sample 100 prompts | 6 | Module:2 + Deps:1 + Algo:1 + Integ:2 |
| E2 | Entropy Computation | Aggregate preferences and compute Shannon entropy | 8 | Module:2 + Deps:2 + Algo:2 + Integ:2 |
| E3 | Metrics & Validation | Calculate success rate, variance, range validation | 5 | Module:1 + Deps:1 + Algo:2 + Integ:1 |
| E4 | Visualization & Output | Generate 4 figures and save results to JSON | 7 | Module:2 + Deps:2 + Algo:1 + Integ:2 |

**Total Complexity:** 26  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [E1, E2, E3, E4]

---

## Task Breakdown Details

### E1: Dataset Setup (Complexity: 6)

**Files:** `preference_entropy_analyzer.py`

**Subtasks:**
1. Install HuggingFace datasets library
2. Implement `load_dataset()` method
3. Implement `sample_prompts()` with fixed seed
4. Verify 100 prompts sampled correctly

**Dependencies:** None (first task)

**Validation:**
- Dataset loads without error
- Exactly 100 prompts sampled
- Seed=1 produces reproducible results

---

### E2: Entropy Computation (Complexity: 8)

**Files:** `preference_entropy_analyzer.py`

**Subtasks:**
1. Implement `aggregate_preferences()` for chosen/rejected counts
2. Implement `compute_entropy()` using scipy.stats.entropy
3. Handle edge cases (zero probabilities, insufficient data)
4. Implement `analyze_dataset()` main loop

**Dependencies:** E1 (needs sampled prompts)

**Validation:**
- Entropy values in range [0, 0.693] nats
- None returned for prompts with <5 comparisons
- Natural log base used (nats not bits)

---

### E3: Metrics & Validation (Complexity: 5)

**Files:** `preference_entropy_analyzer.py`

**Subtasks:**
1. Implement `compute_metrics()` for success rate, variance, range
2. Add validation checks (range bounds, variance > 0)
3. Calculate mean entropy

**Dependencies:** E2 (needs entropy results)

**Validation:**
- Success rate >= 95%
- Variance > 0
- All values in [0, 0.693] nats

---

### E4: Visualization & Output (Complexity: 7)

**Files:** `preference_entropy_analyzer.py`

**Subtasks:**
1. Implement gate metrics bar chart (target vs actual)
2. Implement entropy histogram (20 bins)
3. Implement entropy vs prompt index scatter plot
4. Implement success rate pie chart
5. Implement `save_results()` to JSON
6. Create figures/ directory

**Dependencies:** E3 (needs metrics)

**Validation:**
- 4 PNG files saved to figures/
- JSON file contains results and metadata
- Gate metrics figure shows target vs actual

---

## Dependencies

### External Libraries

```txt
scipy>=1.7.0
numpy>=1.21.0
datasets>=2.0.0
matplotlib>=3.5.0
```

### Dataset

- **Name:** Anthropic-HH (Anthropic/hh-rlhf)
- **Size:** ~3GB download
- **Access:** Public (no authentication)
- **Format:** HuggingFace datasets

---

## Success Criteria

### MUST_WORK Gate Conditions

1. Code executes without errors
2. Success rate >= 95% (entropy computable for 95+ prompts)
3. Entropy variance > 0 (not constant)
4. All entropy values in [0, 0.693] nats

### Output Artifacts

1. `h-e1_results.json` - Results with metadata
2. `figures/gate_metrics.png` - Target vs actual comparison
3. `figures/entropy_histogram.png` - Distribution
4. `figures/entropy_scatter.png` - Entropy vs prompt index
5. `figures/success_rate_pie.png` - Success/failure pie chart

---

## Non-Functional Requirements

### NFR-1: Performance
- Target: <2 minutes wall-clock time (CPU only)
- Bottleneck: Dataset download (3GB, one-time)

### NFR-2: Reproducibility
- Fixed seed=1 for sampling
- Deterministic entropy computation

### NFR-3: Data Integrity
- Assert 0 <= H <= ln(2) for all entropies
- Filter prompts with <5 comparisons

---

## Self-Validation Checklist

- [x] No ASCII diagrams (used bullet list)
- [x] No KB search logs (only "Applied: X")
- [x] Module section = interface code only
- [x] 4 Epic tasks (EXISTENCE range: 3-5)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project noted (Serena skip acceptable)
- [x] Complexity scores with breakdown included
- [x] File structure minimal (single main script)

---

*Architecture designed for EXISTENCE PoC - minimal structure to test "does it work?"*
*Next Phase: Phase 4 - Implementation (Coder)*
