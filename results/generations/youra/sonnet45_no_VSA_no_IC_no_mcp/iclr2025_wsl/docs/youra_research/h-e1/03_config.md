# Configuration: H-E1 KB Extraction

**Date:** 2026-08-25  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE (PoC)  
**Config Format:** Hardcoded dict

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New project - no existing config to verify  
**Config Files Found**: None - new single-script implementation  
**Pattern Used**: Hardcoded dict (minimal PoC)

---

## Configuration Schema

All configuration values are hardcoded in `extract_kb.py`. No external config file needed.

```python
CONFIG = {
    # API Settings
    "api_base_url": "https://paperswithcode.com/api/v1",
    "api_timeout": 30,
    "api_retry_limit": 3,
    "api_backoff_base": 2,
    
    # Cache Paths
    "cache_dir": "/data/pwc_cache",
    "response_cache": "/data/pwc_cache/responses",
    "kb_output": "/data/pwc_cache/kb.yaml",
    "metrics_output": "/data/pwc_cache/metrics.json",
    
    # Figures
    "figures_dir": "docs/youra_research/h-e1/figures",
    "figure_dpi": 300,
    "figure_format": "png",
    
    # Evaluation
    "coverage_threshold": 0.80,
    "completeness_threshold": 0.95,
    "random_seed": 42,
    
    # Execution
    "max_datasets": None,  # None = process all
    "cache_expiry_hours": 24,
}
```

---

## Ground Truth Dataset List

```python
GROUND_TRUTH_DATASETS = [
    # Vision (15)
    'CIFAR-10', 'CIFAR-100', 'ImageNet', 'COCO', 'ADE20K', 
    'Pascal VOC', 'MS COCO', 'CelebA', 'Places365', 'STL-10', 
    'SVHN', 'Fashion-MNIST', 'MNIST', 'Caltech-101', 'Caltech-256',
    
    # NLP (15)
    'GLUE', 'SuperGLUE', 'SQuAD', 'WMT', 'WikiText-103', 
    'IMDB', 'SST-2', 'CoNLL-2003', 'MultiNLI', 'SNLI', 
    'QQP', 'MRPC', 'RTE', 'WNLI', 'CoLA',
    
    # Audio (5)
    'LibriSpeech', 'Common Voice', 'TIMIT', 'VoxCeleb', 'AudioSet',
    
    # Graph (5)
    'Cora', 'CiteSeer', 'PubMed', 'Reddit', 'ogbn-arxiv',
    
    # Video (5)
    'Kinetics', 'UCF-101', 'Something-Something', 'ActivityNet', 'HMDB51',
    
    # Other (5)
    'Omniglot', 'miniImageNet', 'tieredImageNet', 'CUB-200', 'Stanford Cars'
]  # Total: 50
```

---

## Dependencies

```python
REQUIRED_PACKAGES = {
    "paperswithcode-client": ">=0.3.0",
    "pyyaml": ">=5.4",
    "matplotlib": ">=3.5",
    "pandas": ">=1.3",
    "requests": ">=2.28",
}
```

Install: `pip install paperswithcode-client pyyaml matplotlib pandas requests`

---

## File Paths Structure

```
/data/pwc_cache/
├── responses/          # API response cache (auto-created)
├── kb.yaml            # Output: (D,B,M) triples
└── metrics.json       # Output: coverage/completeness

docs/youra_research/h-e1/
└── figures/
    ├── coverage_comparison.png
    ├── domain_distribution.png
    └── missing_datasets.txt
```

---

## Rationale for Non-Standard Values

**cache_expiry_hours: 24**  
PWC catalog changes slowly. 24h cache avoids rate limits while keeping data fresh enough for PoC validation.

**coverage_threshold: 0.80**  
MUST_WORK gate from PRD. Below 80% coverage invalidates entire hypothesis and triggers catalog alternative exploration.

**completeness_threshold: 0.95**  
Allows 5% tolerance for metadata gaps (some benchmarks may lack metric fields in API).

**random_seed: 42**  
Standard ML convention for reproducible baseline comparison.

---

## Usage Example

```python
# In extract_kb.py
if __name__ == '__main__':
    import os
    from paperswithcode import PapersWithCodeClient
    import yaml
    import json
    
    # Create cache directories
    os.makedirs(CONFIG['cache_dir'], exist_ok=True)
    os.makedirs(CONFIG['response_cache'], exist_ok=True)
    os.makedirs(CONFIG['figures_dir'], exist_ok=True)
    
    # Initialize API client
    client = PapersWithCodeClient()
    
    # Extract KB (see 03_prd.md for full logic)
    kb_triples = extract_triples(client, CONFIG)
    
    # Save outputs
    with open(CONFIG['kb_output'], 'w') as f:
        yaml.dump(kb_triples, f)
    
    # Compute metrics
    coverage = compute_coverage(kb_triples, GROUND_TRUTH_DATASETS)
    completeness = compute_completeness(kb_triples)
    
    metrics = {
        'coverage': coverage,
        'completeness': completeness,
        'threshold_coverage': CONFIG['coverage_threshold'],
        'threshold_completeness': CONFIG['completeness_threshold'],
        'pass': coverage > CONFIG['coverage_threshold']
    }
    
    with open(CONFIG['metrics_output'], 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Generate figures
    plot_coverage_comparison(coverage, CONFIG)
    plot_domain_distribution(kb_triples, CONFIG)
    
    # MUST_WORK gate check
    assert coverage > CONFIG['coverage_threshold'], \
        f"Coverage {coverage:.1%} < {CONFIG['coverage_threshold']:.0%} - GATE FAILED"
```

---

*All values hardcoded for PoC simplicity. No external config file needed.*
