"""Phi coefficient coupling analysis for dimension pairs."""

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.metrics import matthews_corrcoef

class CouplingAnalyzer:
    """Compute phi coefficients for dimension pairs."""

    def __init__(self, dimensions):
        """Initialize with dimension names.

        Args:
            dimensions: ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']
        """
        self.dimensions = dimensions
        self.n_dims = len(dimensions)

    def compute_phi_coefficient(self, labels_d1, labels_d2):
        """Compute phi coefficient and p-value for dimension pair.

        Args:
            labels_d1: [N] binary labels for dimension 1
            labels_d2: [N] binary labels for dimension 2

        Returns: (phi_coefficient, p_value)
            phi_coefficient: Pearson correlation for 2×2 table, range [-1, 1]
            p_value: Chi-square test p-value
        """
        # Construct 2×2 contingency table
        table = pd.crosstab(labels_d1, labels_d2)

        # Ensure 2×2 shape
        if table.shape != (2, 2):
            # Handle degenerate cases
            return 0.0, 1.0

        # Chi-square test
        chi2, p_value, dof, expected = chi2_contingency(table)

        # Compute phi coefficient
        n = len(labels_d1)
        phi = np.sqrt(chi2 / n)

        return phi, p_value

    def analyze_model(self, labels):
        """Compute phi coefficients for all dimension pairs.

        Args:
            labels: {dimension: [N] binary array} for all 5 dimensions

        Returns: DataFrame with columns [dim1, dim2, phi, p_value]
            10 rows for 5 choose 2 pairs
        """
        results = []

        for i in range(self.n_dims):
            for j in range(i+1, self.n_dims):
                dim1 = self.dimensions[i]
                dim2 = self.dimensions[j]

                phi, p = self.compute_phi_coefficient(labels[dim1], labels[dim2])

                results.append({
                    "dim1": dim1,
                    "dim2": dim2,
                    "phi": phi,
                    "p_value": p
                })

        return pd.DataFrame(results)

    def verify_phi_sklearn(self, labels_d1, labels_d2):
        """Verify phi via sklearn.metrics.matthews_corrcoef.

        Args:
            labels_d1: [N] binary labels
            labels_d2: [N] binary labels

        Returns: MCC (equivalent to phi for binary classification)
        """
        return matthews_corrcoef(labels_d1, labels_d2)
