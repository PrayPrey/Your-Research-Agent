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
    s2_rate_limit_delay: float = 0.01
    api_retry_attempts: int = 3
    api_timeout: int = 30

    # Graph Construction
    publication_year_min: int = 2015
    publication_year_max: int = 2024
    min_degree: int = 3
    min_community_size: int = 5

    # Community Detection
    resolution: float = 1.0

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
        """Create output directories."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

        if self.community_colors is None:
            self.community_colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
