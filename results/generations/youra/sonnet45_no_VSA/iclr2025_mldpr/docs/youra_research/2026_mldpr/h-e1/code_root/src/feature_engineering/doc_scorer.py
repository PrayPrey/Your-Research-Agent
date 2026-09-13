"""Documentation completeness scorer."""
import logging
from typing import Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class DocumentationScorer:
    """Computes documentation completeness scores."""

    def score_repository(self, github_data: Dict) -> Dict[str, Any]:
        """Compute binary features and composite score.

        Args:
            github_data: Dictionary containing GitHub repository data

        Returns:
            Dictionary with documentation scores
        """
        env_file = github_data.get('env_file', False)
        pinned_deps = github_data.get('pinned_deps', False)
        dockerfile = github_data.get('dockerfile', False)

        doc_score = int(env_file) + int(pinned_deps) + int(dockerfile)

        return {
            'env_file': env_file,
            'pinned_deps': pinned_deps,
            'dockerfile': dockerfile,
            'doc_score': doc_score
        }

    def extract_control_variables(self, metadata: Dict) -> Dict[str, Any]:
        """Extract confounding variables.

        Args:
            metadata: Dictionary containing paper/repository metadata

        Returns:
            Dictionary with control variables
        """
        pub_year = metadata.get('pub_year', 2022)
        log_model_params = metadata.get('log_model_params', 8.0)
        benchmark_family = metadata.get('benchmark_family', 'Unknown')
        task_domain = metadata.get('task_domain', 'Unknown')

        return {
            'pub_year': pub_year,
            'log_model_params': log_model_params,
            'benchmark_family': benchmark_family,
            'task_domain': task_domain
        }

    def compute_reproduction_success(
        self,
        publication_date: datetime,
        first_reproduction_date: datetime
    ) -> bool:
        """Binary outcome: Reproduced within 12 months.

        Args:
            publication_date: Paper publication date
            first_reproduction_date: First leaderboard entry date

        Returns:
            True if reproduced within 365 days
        """
        delta = (first_reproduction_date - publication_date).days
        return delta <= 365
