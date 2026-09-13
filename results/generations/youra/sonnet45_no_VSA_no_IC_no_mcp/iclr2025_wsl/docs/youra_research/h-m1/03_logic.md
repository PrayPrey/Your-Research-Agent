# Logic Design: H-M1 KB Extraction Logic Validator

**Date:** 2026-08-25  
**Hypothesis:** h-m1 (MECHANISM PoC)  
**Author:** Logic Agent  
**Type:** PoC - Validate extraction mechanism  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Reusing h-e1 code structure (copy and adapt)  
**Analyzed Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-e1/code/`  
**Relevant Symbols:** `PWCExtractor`, `Evaluator`, `Visualizer`, `GROUND_TRUTH_DATASETS`

---

## Applied Patterns (Archon KB)

**Applied:** API retry with exponential backoff  
**Applied:** Local filesystem cache  
**Applied:** YAML structured output  

---

## Core API Signatures

### 1. PWCExtractor (Copied from h-e1)

```python
from pathlib import Path
from typing import Dict, List
import requests
import yaml
import time

class PWCExtractor:
    def __init__(self, cache_dir: str):
        """Initialize extractor. cache_dir: [str]"""
        self.api_base = "https://huggingface.co/api/datasets"
        self.cache_dir = Path(cache_dir)
        self.triples: List[Dict[str, str]] = []  # [(D,B,M) dicts]
        self.session = requests.Session()
    
    def _retry_api_call(self, url: str, max_retries: int = 3) -> dict:
        """Exponential backoff. Returns: dict response"""
        ...
    
    def extract_triples(self, ground_truth_datasets: List[str]) -> List[Dict]:
        """Search HF API for ground-truth datasets. Returns: N × {dataset, benchmark, metric}"""
        ...
    
    def save_kb(self, output_path: str):
        """Save to YAML with metadata header."""
        ...
```

### 2. Evaluator (Copied from h-e1)

```python
class Evaluator:
    def __init__(self, ground_truth: List[str]):
        """ground_truth: [50 dataset names]"""
        self.ground_truth = ground_truth
    
    def compute_coverage(self, kb_triples: List[Dict]) -> float:
        """Coverage = (# found) / 50. Returns: [0,1]"""
        ...
    
    def compute_completeness(self, kb_triples: List[Dict]) -> float:
        """Completeness = (# complete triples) / total. Returns: [0,1]"""
        ...
    
    def get_missing_datasets(self, kb_triples: List[Dict]) -> List[str]:
        """List of ground-truth datasets not found."""
        ...
    
    def random_baseline(self, seed: int = 42) -> float:
        """Random 50% baseline. Returns: ~0.50"""
        ...
```

### 3. Visualizer (Adapted from h-e1)

```python
from pathlib import Path
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, output_dir: str):
        """output_dir: [str] -> None"""
        self.output_dir = Path(output_dir)
    
    def plot_coverage_comparison(
        self, 
        extracted: float, 
        baseline: float, 
        h_e1: float = 0.84
    ):
        """Bar chart: random vs h-e1 vs h-m1. Added h_e1 parameter."""
        ...
    
    def plot_domain_distribution(self, kb_triples: List[Dict]):
        """Pie chart by domain (vision/nlp/audio/graph/video)."""
        ...
    
    def plot_gate_metrics(self, actual_coverage: float, target: float = 0.80):
        """NEW: Gate threshold vs actual coverage gauge."""
        ...
    
    def plot_metadata_completeness(self, kb_triples: List[Dict]):
        """NEW: Histogram of triple completeness."""
        ...
    
    def save_missing_datasets_table(self, missing: List[str]):
        """Text file of missing datasets."""
        ...
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following are copied from h-e1. Signatures verified from actual implementation:

```python
# From: /docs/youra_research/h-e1/code/extract_kb.py (ACTUAL CODE)

# Classes (copy entire implementations)
class PWCExtractor:
    def __init__(self, cache_dir: str): ...
    def _retry_api_call(self, url: str, max_retries: int = 3) -> dict: ...
    def extract_triples(self, ground_truth_datasets: List[str]) -> List[Dict]: ...
    def save_kb(self, output_path: str): ...

class Evaluator:
    def __init__(self, ground_truth: List[str]): ...
    def compute_coverage(self, kb_triples: List[Dict]) -> float: ...
    def compute_completeness(self, kb_triples: List[Dict]) -> float: ...
    def get_missing_datasets(self, kb_triples: List[Dict]) -> List[str]: ...
    def random_baseline(self, seed: int = 42) -> float: ...

class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_coverage_comparison(self, extracted: float, baseline: float): ...
    def plot_domain_distribution(self, kb_triples: List[Dict]): ...
    def save_missing_datasets_table(self, missing: List[str]): ...

# Ground truth constant (copy verbatim)
GROUND_TRUTH_DATASETS = [
    # Vision (15)
    'CIFAR-10', 'CIFAR-100', 'ImageNet', 'COCO', 'ADE20K', 'Pascal VOC',
    'MS COCO', 'CelebA', 'Places365', 'STL-10', 'SVHN', 'Fashion-MNIST',
    'MNIST', 'Caltech-101', 'Caltech-256',
    # NLP (15)
    'GLUE', 'SuperGLUE', 'SQuAD', 'WMT', 'WikiText-103', 'IMDB',
    'SST-2', 'CoNLL-2003', 'MultiNLI', 'SNLI', 'QQP', 'MRPC',
    'RTE', 'WNLI', 'CoLA',
    # Audio (5)
    'LibriSpeech', 'Common Voice', 'TIMIT', 'VoxCeleb', 'AudioSet',
    # Graph (5)
    'Cora', 'CiteSeer', 'PubMed', 'Reddit', 'ogbn-arxiv',
    # Video (5)
    'Kinetics', 'UCF-101', 'Something-Something', 'ActivityNet', 'HMDB51',
    # Other (5)
    'Omniglot', 'miniImageNet', 'tieredImageNet', 'CUB-200', 'Stanford Cars'
]
```

**Verified from:** `/docs/youra_research/h-e1/code/extract_kb.py` (lines 56-223)

---

## Adaptation Strategy (h-e1 → h-m1)

### Copy Unchanged
- `PWCExtractor` class (lines 56-189)
- `Evaluator` class (lines 191-223)
- `GROUND_TRUTH_DATASETS` constant (lines 36-53)
- `CONFIG` dict (lines 22-33)

### Modify Paths
```python
CONFIG = {
    "cache_dir": "../data/pwc_cache",           # Change to h-m1/data/
    "kb_output": "../data/pwc_cache/kb.yaml",   # Change to h-m1/data/
    "metrics_output": "../data/pwc_cache/metrics.json",
    "figures_dir": "../figures",                 # Change to h-m1/figures/
    # ... rest unchanged
}
```

### Add to Visualizer
```python
# Add 2 new methods to Visualizer class:

def plot_gate_metrics(self, actual_coverage: float, target: float = 0.80):
    """Gauge chart: target 80% vs actual."""
    fig, ax = plt.subplots(figsize=(6, 4))
    methods = ['Target', 'Actual']
    values = [target, actual_coverage]
    colors = ['red', 'green' if actual_coverage >= target else 'orange']
    ax.barh(methods, values, color=colors)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel('Coverage')
    ax.set_title('Gate Metrics: Coverage vs Target')
    plt.tight_layout()
    plt.savefig(self.output_dir / 'gate_metrics.png', dpi=300)
    plt.close()

def plot_metadata_completeness(self, kb_triples: List[Dict]):
    """Histogram: distribution of complete vs incomplete triples."""
    complete_count = sum(1 for t in kb_triples if all([t.get('dataset'), t.get('benchmark'), t.get('metric')]))
    incomplete_count = len(kb_triples) - complete_count
    
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ['Complete', 'Incomplete']
    counts = [complete_count, incomplete_count]
    ax.bar(categories, counts, color=['green', 'red'])
    ax.set_ylabel('Count')
    ax.set_title('Triple Completeness Distribution')
    plt.tight_layout()
    plt.savefig(self.output_dir / 'metadata_completeness.png', dpi=300)
    plt.close()
```

### Modify plot_coverage_comparison
```python
# Add h_e1 parameter to compare against h-e1 baseline
def plot_coverage_comparison(self, extracted: float, baseline: float, h_e1: float = 0.84):
    """Bar chart: random vs h-e1 vs h-m1."""
    fig, ax = plt.subplots(figsize=(10, 6))
    methods = ['Random Baseline', 'H-E1 (Previous)', 'H-M1 (Current)']
    coverages = [baseline, h_e1, extracted]
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
    
    bars = ax.bar(methods, coverages, color=colors)
    ax.axhline(y=0.80, color='red', linestyle='--', label='80% Threshold')
    ax.set_ylabel('Coverage (%)')
    ax.set_title('KB Coverage Comparison')
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax.legend()
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1%}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(self.output_dir / 'coverage_comparison.png', dpi=300)
    plt.close()
```

---

## Main Execution Flow

```python
def main():
    """Main execution flow."""
    print("="*60)
    print("H-M1: KB Extraction Logic Validator")
    print("MUST_WORK gate: Coverage >80%")
    print("="*60 + "\n")

    # Initialize
    extractor = PWCExtractor(cache_dir=CONFIG['cache_dir'])
    evaluator = Evaluator(ground_truth=GROUND_TRUTH_DATASETS)
    visualizer = Visualizer(output_dir=CONFIG['figures_dir'])

    # Extract KB
    print("[STEP 1/5] Extracting triples from HF API...")
    kb_triples = extractor.extract_triples(GROUND_TRUTH_DATASETS)
    extractor.save_kb(CONFIG['kb_output'])

    # Evaluate
    print("[STEP 2/5] Computing metrics...")
    coverage = evaluator.compute_coverage(kb_triples)
    completeness = evaluator.compute_completeness(kb_triples)
    missing = evaluator.get_missing_datasets(kb_triples)
    baseline_coverage = evaluator.random_baseline(seed=CONFIG['random_seed'])

    print(f"  Coverage:     {coverage:.2%}")
    print(f"  Completeness: {completeness:.2%}")
    print(f"  Baseline:     {baseline_coverage:.2%}")
    print(f"  Missing:      {len(missing)}/50 datasets")

    # Save metrics
    print("[STEP 3/5] Saving metrics...")
    metrics = {
        'coverage': coverage,
        'completeness': completeness,
        'baseline_coverage': baseline_coverage,
        'h_e1_coverage': 0.84,  # NEW: reference to h-e1
        'missing_count': len(missing),
        'missing_datasets': missing,
        'gate_threshold': CONFIG['coverage_threshold'],
        'gate_passed': coverage > CONFIG['coverage_threshold']
    }

    with open(CONFIG['metrics_output'], 'w') as f:
        json.dump(metrics, f, indent=2)

    # Visualize
    print("[STEP 4/5] Generating figures...")
    visualizer.plot_coverage_comparison(coverage, baseline_coverage, h_e1=0.84)  # NEW: h_e1 param
    visualizer.plot_domain_distribution(kb_triples)
    visualizer.plot_gate_metrics(coverage, target=0.80)  # NEW
    visualizer.plot_metadata_completeness(kb_triples)  # NEW
    visualizer.save_missing_datasets_table(missing)

    # Gate check
    print("[STEP 5/5] MUST_WORK gate check...")
    if coverage > CONFIG['coverage_threshold']:
        print(f"✓ GATE PASSED: {coverage:.2%} > {CONFIG['coverage_threshold']:.0%}")
        return 0
    else:
        print(f"✗ GATE FAILED: {coverage:.2%} ≤ {CONFIG['coverage_threshold']:.0%}")
        return 1


if __name__ == '__main__':
    exit(main())
```

---

## File Structure

```
h-m1/
├── code/
│   └── extract_kb.py        # Copied from h-e1 with adaptations above
├── data/
│   └── pwc_cache/
│       ├── kb.yaml          # KB extraction output
│       └── metrics.json     # Coverage metrics
└── figures/
    ├── coverage_comparison.png      # random vs h-e1 vs h-m1 (MODIFIED)
    ├── domain_distribution.png      # coverage by domain (COPIED)
    ├── gate_metrics.png             # target 80% vs actual (NEW)
    ├── metadata_completeness.png    # histogram (NEW)
    └── missing_datasets.txt         # list of missing datasets (COPIED)
```

---

## Validation (Phase 5)

```python
# Phase 5 will check:
assert os.path.exists("h-m1/data/pwc_cache/kb.yaml")
assert os.path.exists("h-m1/data/pwc_cache/metrics.json")

with open("h-m1/data/pwc_cache/metrics.json") as f:
    metrics = json.load(f)
    assert metrics["coverage"] > 0.80  # MUST_WORK gate
    assert metrics["completeness"] > 0.95
    assert metrics["h_e1_coverage"] == 0.84  # Reference baseline

# Verify 5 figures exist
assert len(os.listdir("h-m1/figures/")) == 5
```

---

*Minimal MECHANISM PoC: validate automated extraction logic achieves >80% coverage using h-e1 proven code.*
