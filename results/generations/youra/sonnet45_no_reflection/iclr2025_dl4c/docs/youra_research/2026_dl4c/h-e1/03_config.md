# Configuration: H-E1 Data Collection Pipeline

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (Proof-of-Concept)  
**Generated:** 2026-05-11  
**Config Agent:** configuration-agent

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** dataclass

---

## Applied Patterns (Archon KB)

Applied: Standard Python dataclass configuration pattern

---

## E1: Data Collection Pipeline [Complexity: 15, Budget: 2 subtasks]

**Applied:** Standard PyTorch/research pipeline defaults with GitHub API best practices

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class CollectionConfig:
    """GitHub commit collection configuration for H-E1 EXISTENCE validation."""
    
    # GitHub API settings
    github_token: str = ""  # Set via environment variable GITHUB_TOKEN
    api_rate_limit_wait: int = 60  # seconds to wait on rate limit
    max_retries: int = 3
    
    # Repository mining parameters
    min_stars: int = 1000
    n_repos: int = 500
    languages: List[str] = field(default_factory=lambda: ["python", "javascript", "java"])
    
    # Commit filtering parameters
    n_commits_target: int = 10000
    ast_distance_min: int = 1
    ast_distance_max: int = 20
    time_range_start: str = "2023-01-01"
    time_range_end: str = "2026-01-01"
    
    # Aspect labeling keywords
    aspect_keywords: dict = field(default_factory=lambda: {
        "security": ["security", "vulnerability", "CVE", "XSS", "injection", "auth"],
        "refactor": ["refactor", "cleanup", "rename", "restructure"],
        "performance": ["performance", "optimize", "speed", "cache"],
        "bugfix": ["fix", "bug", "error", "crash", "issue #"]
    })
    
    # Storage paths
    output_dir: str = "data"
    commits_metadata_file: str = "commits_10k.jsonl"
    file_pairs_dir: str = "file_pairs"
    
    # Performance settings
    parallel_workers: int = 16
    batch_size: int = 100
    
    # Cache settings
    cache_dir: str = "cache"
    cache_enabled: bool = True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1 | GitHub API Integration | Implement PyGitHub/PyDriller mining with rate limiting, repository filtering (stars, languages), and commit metadata extraction |
| C-E1-2 | Commit Filtering & Storage | Implement AST distance calculation (tree-sitter), aspect labeling (keyword matching), file pair storage (JSONL + files) |

---

## Configuration Usage

### Loading Configuration

```python
import os
from config import CollectionConfig

# Load with defaults
config = CollectionConfig()

# Override from environment
config.github_token = os.environ.get("GITHUB_TOKEN", "")

# Validate
assert config.github_token, "GITHUB_TOKEN environment variable required"
assert config.n_commits_target > 0, "Target commit count must be positive"
```

### Environment Setup

```bash
# Required
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"

# Optional overrides
export CUDA_VISIBLE_DEVICES=""  # CPU-only for data collection
```

---

## Validation Checklist

### Configuration Completeness
- [x] Single format (dataclass) used
- [x] GitHub API configuration included
- [x] Commit filtering parameters specified
- [x] Subtask count within budget (2/2)
- [x] No ASCII diagrams
- [x] Codebase Analysis section included

### EXISTENCE Compliance
- [x] Minimal fixed configuration (PoC-appropriate)
- [x] Default values from research requirements
- [x] No hyperparameter grid
- [x] No ablation configs

### Output Requirements
- [x] Total length < 400 lines
- [x] Copy-paste ready Python code
- [x] Rationale only for non-standard values
- [x] No multiple format examples

---

**End of Configuration Document**  
**Next Phase:** Phase 4 Implementation  
**Ready for:** Epic E1 coding
