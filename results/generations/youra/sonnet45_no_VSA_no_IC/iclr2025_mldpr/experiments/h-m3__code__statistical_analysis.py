"""Statistical analysis for h-m3 required field presence."""

from typing import Dict, List
import numpy as np
from scipy.stats import chi2_contingency
from scipy.stats.contingency import association

from config import H_M2_OPTIONAL_CV


class RequiredFieldAnalyzer:
    """Analyze required field presence rates and variance."""

    @staticmethod
    def calculate_presence_rates(parsed_records: List[Dict]) -> Dict:
        """
        Calculate presence rates per platform for each field.

        Returns:
            {
                "license": {"HF": 0.90, "OpenML": 0.88, "UCI": 0.75},
                "version": {"HF": 0.95, "OpenML": 0.92, "UCI": 0.70},
            }
        """
        platforms = {}
        for record in parsed_records:
            platform = record["platform"]
            if platform not in platforms:
                platforms[platform] = {
                    "license_present": [],
                    "version_present": [],
                }
            platforms[platform]["license_present"].append(record["license_present"])
            platforms[platform]["version_present"].append(record["version_present"])

        rates = {}
        for field in ["license", "version"]:
            field_key = f"{field}_present"
            rates[field] = {}
            for platform in ["HF", "OpenML", "UCI"]:
                if platform in platforms:
                    presence_list = platforms[platform][field_key]
                    rates[field][platform] = sum(presence_list) / len(presence_list)
                else:
                    rates[field][platform] = 0.0

        return rates

    @staticmethod
    def build_contingency_table(parsed_records: List[Dict], field: str) -> np.ndarray:
        """
        Build 2×3 contingency table (present/absent × HF/OpenML/UCI).

        Returns:
            [[hf_present, openml_present, uci_present],
             [hf_absent, openml_absent, uci_absent]]
        """
        field_key = f"{field}_present"
        counts = {
            "HF": {"present": 0, "absent": 0},
            "OpenML": {"present": 0, "absent": 0},
            "UCI": {"present": 0, "absent": 0},
        }

        for record in parsed_records:
            platform = record["platform"]
            if record[field_key]:
                counts[platform]["present"] += 1
            else:
                counts[platform]["absent"] += 1

        table = np.array([
            [counts["HF"]["present"], counts["OpenML"]["present"], counts["UCI"]["present"]],
            [counts["HF"]["absent"], counts["OpenML"]["absent"], counts["UCI"]["absent"]],
        ])

        return table

    @staticmethod
    def chi_squared_test(contingency_table: np.ndarray) -> Dict:
        """
        Run chi-squared test of independence.

        Returns:
            {"chi2": float, "p_value": float, "dof": int}
        """
        # Add Laplace smoothing if zero cells present
        if np.any(contingency_table == 0):
            contingency_table = contingency_table + 1

        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        return {
            "chi2": float(chi2),
            "p_value": float(p_value),
            "dof": int(dof),
            "expected": expected.tolist(),
        }

    @staticmethod
    def cramers_v(contingency_table: np.ndarray) -> float:
        """Calculate Cramér's V effect size."""
        # Add Laplace smoothing if zero cells present
        if np.any(contingency_table == 0):
            contingency_table = contingency_table + 1

        return float(association(contingency_table, method="cramer"))

    @staticmethod
    def coefficient_of_variation(rates: Dict[str, float]) -> float:
        """
        Calculate CV for a field across platforms.

        Args:
            rates: {"HF": 0.90, "OpenML": 0.88, "UCI": 0.75}

        Returns:
            CV = std / mean
        """
        values = [rates["HF"], rates["OpenML"], rates["UCI"]]
        mean = np.mean(values)
        std = np.std(values, ddof=1)  # Sample std
        if mean == 0:
            return 0.0
        return float(std / mean)

    def analyze_field(self, parsed_records: List[Dict], field: str) -> Dict:
        """Analyze single field (license or version)."""
        rates = self.calculate_presence_rates(parsed_records)
        contingency_table = self.build_contingency_table(parsed_records, field)
        chi2_result = self.chi_squared_test(contingency_table)
        cramers_v = self.cramers_v(contingency_table)
        cv = self.coefficient_of_variation(rates[field])

        return {
            "field": field,
            "presence_rates": rates[field],
            "contingency_table": contingency_table.tolist(),
            "chi2_statistic": chi2_result["chi2"],
            "p_value": chi2_result["p_value"],
            "dof": chi2_result["dof"],
            "cramers_v": cramers_v,
            "cv": cv,
            "mean_presence": np.mean(list(rates[field].values())),
        }

    def compare_with_h_m2(self, required_cv_license: float, required_cv_version: float) -> Dict:
        """
        Compare required field CV with h-m2 optional field CV.

        Returns:
            {
                "required_cv_license": float,
                "required_cv_version": float,
                "optional_cv_preprocessing": float (from h-m2),
                "cv_ratio_license": float,
                "cv_ratio_version": float,
            }
        """
        optional_cv = H_M2_OPTIONAL_CV["preprocessing_code"]

        return {
            "required_cv_license": required_cv_license,
            "required_cv_version": required_cv_version,
            "optional_cv_preprocessing": optional_cv,
            "cv_ratio_license": required_cv_license / optional_cv if optional_cv > 0 else 0.0,
            "cv_ratio_version": required_cv_version / optional_cv if optional_cv > 0 else 0.0,
        }
