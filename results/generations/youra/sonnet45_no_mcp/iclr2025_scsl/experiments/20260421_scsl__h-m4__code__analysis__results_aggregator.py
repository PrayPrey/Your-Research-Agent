"""Results aggregation for FGE and linear paths"""

from dataclasses import dataclass
import numpy as np
from typing import Dict

@dataclass
class CouplingResults:
    """Results container for coupling experiment"""
    fge_rho: float
    fge_p_value: float
    linear_rho: float
    linear_p_value: float
    alignment_values_fge: np.ndarray  # Shape: (M,)
    wga_values_fge: np.ndarray        # Shape: (M,)
    alignment_values_linear: np.ndarray  # Shape: (M,)
    wga_values_linear: np.ndarray        # Shape: (M,)

class ResultsAggregator:
    """Aggregate FGE and linear results"""

    def aggregate(
        self,
        fge_results: Dict,
        linear_results: Dict
    ) -> CouplingResults:
        """
        Combine FGE and linear path results.

        Args:
            fge_results: Dict with keys ["alignments", "wgas", "rho", "p_value"]
            linear_results: Dict with same structure

        Returns:
            CouplingResults dataclass
        """
        return CouplingResults(
            fge_rho=fge_results["rho"],
            fge_p_value=fge_results["p_value"],
            linear_rho=linear_results["rho"],
            linear_p_value=linear_results["p_value"],
            alignment_values_fge=fge_results["alignments"],
            wga_values_fge=fge_results["wgas"],
            alignment_values_linear=linear_results["alignments"],
            wga_values_linear=linear_results["wgas"]
        )
