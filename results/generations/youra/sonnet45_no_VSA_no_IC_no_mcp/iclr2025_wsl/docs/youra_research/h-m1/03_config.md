# Configuration: H-M1 KB Extraction Logic Validator

**Date:** 2026-08-25  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (PoC)  
**Config Agent:** Configuration Agent

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: h-e1 provides actual extraction code with hardcoded config  
**Config Files Found**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-e1/code/extract_kb.py`  
**Pattern Used**: Hardcoded dict (h-e1) → Reuse for h-m1

---

## Archon KB Patterns

**Applied**: PoC minimal config pattern (single dict, fixed values)

---

## Inherited Configuration (Base Hypothesis)

### Config from Actual Code

h-e1 uses hardcoded dict at top of `extract_kb.py`:

```python
# From: h-e1/code/extract_kb.py (lines 22-33)
CONFIG = {
    "cache_dir": "../data/pwc_cache",
    "response_cache": "../data/pwc_cache/responses",
    "kb_output": "../data/pwc_cache/kb.yaml",
    "metrics_output": "../data/pwc_cache/metrics.json",
    "figures_dir": "../figures",
    "retry_attempts": 3,
    "request_timeout": 30,
    "random_seed": 42,
    "coverage_threshold": 0.80,
    "completeness_threshold": 0.95,
}

# Ground truth: 50 well-known datasets (lines 36-53)
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

**Verified from**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-e1/code/extract_kb.py`

---

## h-m1 Configuration (Adapted from h-e1)

**Reuse Strategy**: Copy h-e1 hardcoded config, update paths to h-m1 directories.

### Configuration (Hardcoded Dict)

```python
# h-m1/code/extract_kb.py
CONFIG = {
    "cache_dir": "../data/pwc_cache",
    "response_cache": "../data/pwc_cache/responses",
    "kb_output": "../data/pwc_cache/kb.yaml",
    "metrics_output": "../data/pwc_cache/metrics.json",
    "figures_dir": "../figures",
    "retry_attempts": 3,
    "request_timeout": 30,
    "random_seed": 42,
    "coverage_threshold": 0.80,
    "completeness_threshold": 0.95,
}

# Inherited from h-e1
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

---

## Task Configurations

### A-1: Setup (Complexity: 3, Budget: 0)

**Applied**: Standard file operations, no config needed.

**No configuration required** - Copy h-e1 code to h-m1 directories.

---

### A-2: Extraction (Complexity: 5, Budget: 0)

**Applied**: Inherited h-e1 API config (retry, timeout, cache).

```python
# Extraction config embedded in PWCExtractor class
api_config = {
    "api_base": "https://huggingface.co/api/datasets",
    "retry_attempts": CONFIG["retry_attempts"],  # 3
    "request_timeout": CONFIG["request_timeout"],  # 30s
    "cache_dir": CONFIG["cache_dir"],
    "user_agent": "HF-KB-Extractor/1.0"
}
```

---

### A-3: Evaluation (Complexity: 6, Budget: 0)

**Applied**: Inherited h-e1 evaluation thresholds.

```python
# Evaluation config embedded in main()
evaluation_config = {
    "ground_truth": GROUND_TRUTH_DATASETS,  # 50 datasets
    "coverage_threshold": CONFIG["coverage_threshold"],  # 0.80
    "completeness_threshold": CONFIG["completeness_threshold"],  # 0.95
    "random_seed": CONFIG["random_seed"]  # 42
}
```

---

### A-4: Visualization (Complexity: 7, Budget: 0)

**Applied**: Inherited h-e1 visualization settings + added h-e1 comparison.

```python
# Visualization config embedded in Visualizer class
viz_config = {
    "output_dir": CONFIG["figures_dir"],  # "../figures"
    "dpi": 300,
    "figsize": (8, 6),
    "h_e1_baseline": 0.84  # h-e1 coverage for comparison
}
```

**Non-standard**: Added `h_e1_baseline` to plot h-m1 vs h-e1 comparison.

---

## Self-Validation

- [x] ONE format only (hardcoded dict, inherited from h-e1)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values (h_e1_baseline)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section included
- [x] Field names verified from h-e1 actual code
- [x] Budget 0 subtasks → No subtask decomposition

---

*Minimal MECHANISM PoC config: reuse h-e1 hardcoded dict, validate extraction logic achieves >80% coverage.*
