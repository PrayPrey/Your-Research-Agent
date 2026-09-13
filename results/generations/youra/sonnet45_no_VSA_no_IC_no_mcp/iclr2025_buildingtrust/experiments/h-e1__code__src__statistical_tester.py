"""Statistical comparison of entropy distributions."""
import numpy as np
from scipy.stats import ttest_ind


class StatisticalTester:
    """Compare entity vs non-entity entropy distributions."""

    def compare(self, entity_errors, non_entity_errors):
        """One-tailed t-test: entity < non-entity.

        Returns:
            {p_value, mean_entity, mean_non_entity, cohens_d, pass}
        """
        t_stat, p_two_tail = ttest_ind(entity_errors, non_entity_errors)

        mean_entity = np.mean(entity_errors)
        mean_non_entity = np.mean(non_entity_errors)

        # One-tailed p-value
        p_value = p_two_tail / 2 if mean_entity < mean_non_entity else 1.0

        # Effect size
        pooled_std = np.sqrt((np.var(entity_errors) + np.var(non_entity_errors)) / 2)
        cohens_d = (mean_entity - mean_non_entity) / pooled_std

        return {
            "p_value": float(p_value),
            "mean_entity": float(mean_entity),
            "mean_non_entity": float(mean_non_entity),
            "cohens_d": float(cohens_d),
            "pass": bool(p_value < 0.05 and mean_entity < mean_non_entity)
        }
