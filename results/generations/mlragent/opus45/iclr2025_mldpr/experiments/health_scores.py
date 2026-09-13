"""
Implementation of Dynamic Dataset Health Scores (DDHS) modules.
Each module computes one dimension of dataset health.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
from datetime import datetime

from data_generator import DatasetMetadata


class UsageSaturationIndex:
    """
    Usage Saturation Index (USI) - monitors citation/download patterns
    to identify benchmark overuse that may indicate community-level overfitting.

    USI = alpha * C(t) + beta * D(t) + gamma * P(t)
    where:
    - C(t): normalized citation velocity
    - D(t): download concentration (Gini coefficient)
    - P(t): publication saturation
    """

    def __init__(self, alpha: float = 0.4, beta: float = 0.3, gamma: float = 0.3):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def compute_citation_velocity(
        self,
        monthly_citations: List[int],
        age_months: int,
        domain_total_citations: Optional[int] = None
    ) -> float:
        """
        Compute normalized citation velocity.
        Higher values indicate faster citation accumulation relative to age.
        """
        if len(monthly_citations) == 0 or sum(monthly_citations) == 0:
            return 0.0

        # Normalize by domain if available
        total_citations = sum(monthly_citations)
        if domain_total_citations and domain_total_citations > 0:
            relative_citations = total_citations / domain_total_citations
        else:
            relative_citations = total_citations / max(1, total_citations + 100)

        # Age penalty (older datasets should have more citations)
        age_factor = np.log1p(age_months / 12)

        # Citation velocity
        velocity = relative_citations / max(0.1, age_factor)

        return min(1.0, velocity)

    def compute_download_concentration(self, monthly_downloads: List[int]) -> float:
        """
        Compute Gini coefficient of downloads across time windows.
        High concentration suggests spiky usage (benchmark runs) vs organic use.
        """
        if len(monthly_downloads) == 0 or sum(monthly_downloads) == 0:
            return 0.0

        # Compute Gini coefficient
        downloads = np.array(monthly_downloads, dtype=float)
        downloads = downloads[downloads > 0]  # Remove zeros for concentration

        if len(downloads) <= 1:
            return 0.0

        # Gini coefficient calculation
        n = len(downloads)
        sorted_downloads = np.sort(downloads)
        index = np.arange(1, n + 1)
        gini = (2 * np.sum(index * sorted_downloads) / (n * np.sum(sorted_downloads))) - (n + 1) / n

        return float(np.clip(gini, 0, 1))

    def compute_publication_saturation(
        self,
        citation_count: int,
        domain_paper_count: int = 1000,
        threshold: float = 0.05
    ) -> float:
        """
        Compute publication saturation - ratio of papers using dataset to total domain papers.
        """
        if domain_paper_count == 0:
            return 0.0

        saturation = citation_count / domain_paper_count

        # Normalize to [0, 1] using threshold
        normalized = min(1.0, saturation / threshold)

        return normalized

    def compute(self, dataset: DatasetMetadata, domain_stats: Optional[Dict] = None) -> float:
        """
        Compute the overall Usage Saturation Index.
        Returns value in [0, 1] where higher means more saturated/overused.
        """
        domain_stats = domain_stats or {}

        age_months = (datetime(2024, 1, 1) - dataset.creation_date).days // 30

        citation_velocity = self.compute_citation_velocity(
            dataset.monthly_citations,
            age_months,
            domain_stats.get('total_citations')
        )

        download_concentration = self.compute_download_concentration(
            dataset.monthly_downloads
        )

        publication_saturation = self.compute_publication_saturation(
            dataset.citation_count,
            domain_stats.get('total_papers', 1000)
        )

        usi = (
            self.alpha * citation_velocity +
            self.beta * download_concentration +
            self.gamma * publication_saturation
        )

        # Invert so higher is better (less saturated)
        return 1.0 - float(np.clip(usi, 0, 1))


class FreshnessScore:
    """
    Freshness Score (FS) - assesses temporal drift between dataset
    characteristics and current domain distributions.

    FS = 1 - min(1, KL_divergence / threshold)
    """

    def __init__(self, threshold: float = 2.0, decay_rate: float = 0.05):
        self.threshold = threshold
        self.decay_rate = decay_rate

    def compute_temporal_freshness(self, age_months: int, last_update_months: int) -> float:
        """
        Compute freshness based on dataset age and last update.
        """
        # Age decay
        age_penalty = np.exp(-self.decay_rate * age_months)

        # Update recency bonus
        update_bonus = np.exp(-self.decay_rate * last_update_months * 2)

        # Combine with emphasis on recent updates
        freshness = 0.5 * age_penalty + 0.5 * update_bonus

        return float(freshness)

    def compute_metadata_currency(
        self,
        has_datasheet: bool,
        has_data_card: bool,
        readme_length: int
    ) -> float:
        """
        Assess metadata currency based on documentation standards adoption.
        """
        score = 0.0

        # Modern standards adoption
        if has_datasheet:
            score += 0.4
        if has_data_card:
            score += 0.4

        # README quality proxy
        if readme_length > 100:
            score += 0.1
        if readme_length > 500:
            score += 0.1

        return min(1.0, score)

    def compute(self, dataset: DatasetMetadata) -> float:
        """
        Compute overall Freshness Score.
        Returns value in [0, 1] where higher means fresher.
        """
        base_date = datetime(2024, 1, 1)
        age_months = (base_date - dataset.creation_date).days // 30
        last_update_months = (base_date - dataset.last_updated).days // 30

        temporal = self.compute_temporal_freshness(age_months, last_update_months)
        metadata = self.compute_metadata_currency(
            dataset.has_datasheet,
            dataset.has_data_card,
            dataset.readme_length
        )

        # Combine scores
        freshness = 0.6 * temporal + 0.4 * metadata

        return float(np.clip(freshness, 0, 1))


class DocumentationCompletenessScore:
    """
    Documentation Completeness Score (DCS) - evaluates coverage
    across mandatory and recommended documentation fields.

    DCS = sum(w_i * indicator(mandatory)) + sum(w_j * quality(recommended))
    """

    # Field weights (sum to 1)
    MANDATORY_FIELDS = {
        'dataset_name': 0.05,
        'description': 0.1,
        'source': 0.08,
        'license': 0.1,
        'size_info': 0.07
    }

    RECOMMENDED_FIELDS = {
        'datasheet': 0.15,
        'data_card': 0.12,
        'bias_statement': 0.1,
        'maintenance_info': 0.08,
        'example_usage': 0.05,
        'citation_info': 0.05,
        'version_info': 0.05
    }

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm

    def compute(self, dataset: DatasetMetadata) -> float:
        """
        Compute Documentation Completeness Score.
        Returns value in [0, 1] where higher means more complete.
        """
        score = 0.0

        # Mandatory fields (assume basic fields are always present for simulation)
        mandatory_weight = sum(self.MANDATORY_FIELDS.values())
        score += mandatory_weight  # Base fields assumed present

        # Recommended fields
        if dataset.has_datasheet:
            score += self.RECOMMENDED_FIELDS['datasheet']
        if dataset.has_data_card:
            score += self.RECOMMENDED_FIELDS['data_card']

        # Use doc_fields_filled as proxy for other fields
        completeness_ratio = dataset.doc_fields_filled / dataset.doc_fields_total
        other_fields_weight = sum(
            v for k, v in self.RECOMMENDED_FIELDS.items()
            if k not in ['datasheet', 'data_card']
        )
        score += completeness_ratio * other_fields_weight

        # README quality bonus
        if dataset.readme_length > 200:
            score += 0.05
        if dataset.readme_length > 1000:
            score += 0.05

        return float(np.clip(score, 0, 1))


class CommunityResponsivenessIndex:
    """
    Community Responsiveness Index (CRI) - measures maintainer engagement
    through issue response patterns, update frequency, and interaction quality.

    CRI = omega_1 * R(t) + omega_2 * U(t) + omega_3 * I(t)
    """

    def __init__(
        self,
        omega1: float = 0.4,
        omega2: float = 0.3,
        omega3: float = 0.3
    ):
        self.omega1 = omega1
        self.omega2 = omega2
        self.omega3 = omega3

    def compute_response_score(
        self,
        num_issues: int,
        num_resolved: int,
        avg_response_days: float
    ) -> float:
        """
        Compute response score based on issue resolution and response time.
        """
        if num_issues == 0:
            return 0.8  # No issues can be neutral/positive

        resolution_rate = num_resolved / num_issues

        # Response time factor (faster is better)
        time_factor = np.exp(-avg_response_days / 7)  # 7 days as baseline

        score = 0.6 * resolution_rate + 0.4 * time_factor

        return float(score)

    def compute_update_frequency(
        self,
        num_updates: int,
        age_months: int
    ) -> float:
        """
        Compute update frequency normalized by age.
        """
        if age_months == 0:
            return 0.5

        # Expected updates per month
        expected_rate = 0.5  # 1 update per 2 months
        actual_rate = num_updates / age_months

        # Normalize
        score = min(1.0, actual_rate / expected_rate)

        return float(score)

    def compute_interaction_quality(self, maintainer_active: bool) -> float:
        """
        Simplified interaction quality based on maintainer activity.
        In full implementation, would use sentiment analysis.
        """
        return 0.8 if maintainer_active else 0.2

    def compute(self, dataset: DatasetMetadata) -> float:
        """
        Compute overall Community Responsiveness Index.
        Returns value in [0, 1] where higher means more responsive.
        """
        age_months = (datetime(2024, 1, 1) - dataset.creation_date).days // 30

        response = self.compute_response_score(
            dataset.num_issues,
            dataset.num_resolved_issues,
            dataset.avg_response_time_days
        )

        updates = self.compute_update_frequency(
            dataset.num_updates,
            age_months
        )

        interaction = self.compute_interaction_quality(
            dataset.maintainer_active
        )

        cri = (
            self.omega1 * response +
            self.omega2 * updates +
            self.omega3 * interaction
        )

        return float(np.clip(cri, 0, 1))


class EthicalAlertSystem:
    """
    Ethical Alert System (EAS) - integrates detection mechanisms
    for ethical concerns including bias, privacy, and content issues.
    """

    ALERT_LEVELS = {
        'CLEAR': 0,
        'WARNING': 1,
        'CRITICAL': 2
    }

    def __init__(self, critical_threshold: int = 2, warning_threshold: int = 0):
        self.critical_threshold = critical_threshold
        self.warning_threshold = warning_threshold

    def compute(self, dataset: DatasetMetadata) -> Tuple[float, str]:
        """
        Compute ethical alert score and level.
        Returns (score, level) where score in [0, 1] (higher is better/clearer).
        """
        flags = dataset.ethical_flags

        # Determine alert level
        if flags >= self.critical_threshold:
            level = 'CRITICAL'
        elif flags > self.warning_threshold:
            level = 'WARNING'
        else:
            level = 'CLEAR'

        # Compute score (inverse of flags, normalized)
        score = 1.0 / (1.0 + flags)

        # Penalty for known bias
        if dataset.has_bias_report:
            score *= 0.8

        return float(np.clip(score, 0, 1)), level


class DDHSCalculator:
    """
    Main calculator that combines all health dimensions into
    the Dynamic Dataset Health Score.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        usi_params: Optional[Dict] = None,
        fs_params: Optional[Dict] = None,
        cri_params: Optional[Dict] = None
    ):
        # Default weights
        self.weights = weights or {
            'USI': 0.2,
            'FS': 0.2,
            'DCS': 0.2,
            'CRI': 0.2,
            'EAS': 0.2
        }

        # Initialize modules
        self.usi = UsageSaturationIndex(**(usi_params or {}))
        self.fs = FreshnessScore(**(fs_params or {}))
        self.dcs = DocumentationCompletenessScore()
        self.cri = CommunityResponsivenessIndex(**(cri_params or {}))
        self.eas = EthicalAlertSystem()

    def compute_all_scores(
        self,
        dataset: DatasetMetadata,
        domain_stats: Optional[Dict] = None
    ) -> Dict[str, float]:
        """
        Compute all individual health dimension scores.
        """
        usi_score = self.usi.compute(dataset, domain_stats)
        fs_score = self.fs.compute(dataset)
        dcs_score = self.dcs.compute(dataset)
        cri_score = self.cri.compute(dataset)
        eas_score, eas_level = self.eas.compute(dataset)

        return {
            'USI': usi_score,
            'FS': fs_score,
            'DCS': dcs_score,
            'CRI': cri_score,
            'EAS': eas_score,
            'EAS_level': eas_level
        }

    def compute_ddhs(
        self,
        dataset: DatasetMetadata,
        domain_stats: Optional[Dict] = None
    ) -> float:
        """
        Compute the overall Dynamic Dataset Health Score.
        """
        scores = self.compute_all_scores(dataset, domain_stats)

        # Critical ethical alerts override the score
        if scores['EAS_level'] == 'CRITICAL':
            return 0.0

        # Weighted sum
        ddhs = (
            self.weights['USI'] * scores['USI'] +
            self.weights['FS'] * scores['FS'] +
            self.weights['DCS'] * scores['DCS'] +
            self.weights['CRI'] * scores['CRI'] +
            self.weights['EAS'] * scores['EAS']
        )

        return float(np.clip(ddhs, 0, 1))

    def evaluate_repository(
        self,
        datasets: List[DatasetMetadata]
    ) -> Tuple[List[float], List[Dict]]:
        """
        Evaluate all datasets in a repository.
        Returns (ddhs_scores, all_dimension_scores).
        """
        ddhs_scores = []
        all_scores = []

        # Compute domain stats
        domain_stats = self._compute_domain_stats(datasets)

        for dataset in datasets:
            ds_domain_stats = domain_stats.get(dataset.domain, {})
            scores = self.compute_all_scores(dataset, ds_domain_stats)
            ddhs = self.compute_ddhs(dataset, ds_domain_stats)

            scores['DDHS'] = ddhs
            ddhs_scores.append(ddhs)
            all_scores.append(scores)

        return ddhs_scores, all_scores

    def _compute_domain_stats(
        self,
        datasets: List[DatasetMetadata]
    ) -> Dict[str, Dict]:
        """
        Compute aggregate statistics per domain.
        """
        domain_stats = {}

        for dataset in datasets:
            domain = dataset.domain
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'total_citations': 0,
                    'total_papers': 0,
                    'datasets': 0
                }

            domain_stats[domain]['total_citations'] += dataset.citation_count
            domain_stats[domain]['total_papers'] += dataset.citation_count  # Proxy
            domain_stats[domain]['datasets'] += 1

        return domain_stats


if __name__ == "__main__":
    # Test the health score modules
    from data_generator import SyntheticDataGenerator

    generator = SyntheticDataGenerator(seed=42)
    datasets = generator.generate_repository(num_datasets=10)

    calculator = DDHSCalculator()

    print("Testing DDHS Calculator:")
    print("-" * 80)

    for dataset in datasets[:5]:
        scores = calculator.compute_all_scores(dataset)
        ddhs = calculator.compute_ddhs(dataset)

        print(f"\nDataset: {dataset.name}")
        print(f"  Expert Quality: {dataset.quality_score_expert:.3f}")
        print(f"  DDHS Score: {ddhs:.3f}")
        print(f"  Dimensions: USI={scores['USI']:.2f}, FS={scores['FS']:.2f}, "
              f"DCS={scores['DCS']:.2f}, CRI={scores['CRI']:.2f}, EAS={scores['EAS']:.2f}")
        print(f"  Deprecated: {dataset.is_deprecated}")
