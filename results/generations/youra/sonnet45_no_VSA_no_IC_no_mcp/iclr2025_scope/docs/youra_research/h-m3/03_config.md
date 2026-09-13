# Configuration Schema: h-m3

**Date:** 2026-08-25
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Agent:** Configuration Specialist

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Existing config patterns found
**Config Files Found:** experiments/h-m2/src/config/clustering_config.py (dataclass pattern)
**Pattern Used:** dataclass

Applied: Standard dataclass pattern from existing hypotheses

---

## Configuration Schema

### Python Dataclass (Copy-Paste Ready)

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BipartiteGraphConfig:
    """H-M3 bipartite graph community detection configuration."""
    
    # Study Parameters
    hypothesis_id: str = "h-m3"
    random_seed: int = 42
    
    # Data Paths
    output_dir: str = "data/h-m3"
    figures_dir: str = "../../../docs/youra_research/h-m3/figures"
    cache_dir: str = "data/h-m3/cache"
    
    # API Settings
    pwc_api_base: str = "https://paperswithcode.com/api/v1"
    s2_api_base: str = "https://api.semanticscholar.org/v1"
    s2_rate_limit_delay: float = 0.01  # 10ms = 100 req/sec
    api_retry_attempts: int = 3
    api_timeout: int = 30
    
    # Graph Construction
    publication_year_min: int = 2015
    publication_year_max: int = 2024
    min_degree: int = 3
    min_community_size: int = 5
    
    # Community Detection (Louvain)
    resolution: float = 1.0
    
    # Baseline
    baseline_num_communities: int = 5  # Match Louvain output
    
    # Gate Thresholds
    citation_overlap_threshold: float = 0.70
    modularity_threshold: float = 0.4
    pivot_threshold: float = 0.60
    
    # Visualization
    figure_dpi: int = 300
    figure_size_default: tuple = (10, 6)
    figure_size_heatmap: tuple = (12, 10)
    figure_size_network: tuple = (14, 14)
    colormap: str = "viridis"
    community_colors: list = None
    
    def __post_init__(self):
        """Create output directories and set defaults."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        if self.community_colors is None:
            self.community_colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
```

---

## Field Rationale

**Non-standard values only:**

- `min_degree: 3` - Filter low-degree nodes for graph stability (from 02c_experiment_brief.md best practices)
- `s2_rate_limit_delay: 0.01` - 10ms delay = 100 req/sec (Semantic Scholar free tier limit from PRD)
- `pivot_threshold: 0.60` - PIVOT gate condition if citation_overlap 60-70% (from PRD failure conditions)
- `baseline_num_communities: 5` - Placeholder, will match Louvain output count at runtime

All other values: standard defaults from research or PRD specifications.

---

## Cache File Paths

```python
# Auto-generated from config
bipartite_graph_path = f"{cache_dir}/bipartite_graph.gpickle"
citation_dict_path = f"{cache_dir}/citation_dict.json"
communities_path = f"{cache_dir}/communities.json"
```

---

## Usage Example

```python
from config import BipartiteGraphConfig

config = BipartiteGraphConfig()

# Override if needed
config.resolution = 1.5  # Test different resolution
config.min_community_size = 10  # Stricter filtering
```

---

**Total Lines:** 120
**Format:** Dataclass only
**Dependencies:** dataclasses, pathlib (stdlib)
