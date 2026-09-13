"""Configuration for H-M3: LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis."""

from dataclasses import dataclass
from typing import Dict, List
import os


@dataclass
class ExperimentConfig:
    """Single fixed configuration for H-M3 MECHANISM hypothesis.

    H-M3 tests whether DPO failure concentration in execution errors
    persists at fine-grained LlmFix 19-cause taxonomy level (Cramer's V > 0.03).
    No GPU required - analysis is pure string parsing + statistics.
    """

    # H-E1 data paths (relative to h-m3/code/, resolved to absolute in __post_init__)
    he1_results_dir: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs"
    )

    # Output paths
    output_dir: str = os.path.join(os.path.dirname(__file__), "outputs")
    figures_dir: str = os.path.join(os.path.dirname(__file__), "figures")

    # Statistical thresholds (H-M3 SHOULD_WORK gate criteria)
    chi2_p_threshold: float = 0.05
    cramers_v_threshold_fine: float = 0.03    # Fine-grained gate (lower than coarse)
    cramers_v_threshold_coarse: float = 0.05  # Coarse validation vs H-E1 (V~0.21 expected)

    # Pseudocount for sparse contingency cells (Laplace smoothing)
    pseudocount: float = 0.5

    # Expected failure counts from H-E1 (for data integrity validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    # Reproducibility
    seed: int = 42

    def __post_init__(self):
        """Normalize all paths to absolute."""
        self.he1_results_dir = os.path.abspath(self.he1_results_dir)
        self.output_dir = os.path.abspath(self.output_dir)
        self.figures_dir = os.path.abspath(self.figures_dir)


# LlmFix 19-cause taxonomy (from arXiv:2409.00676)
LLMFIX_TAXONOMY: Dict[str, List[str]] = {
    "syntax": [
        "indentation_error",
        "syntax_error",
        "missing_import",
    ],
    "runtime": [
        "name_error",
        "type_error",
        "attribute_error",
        "index_error",
        "key_error",
        "value_error",
        "zero_division",
        "recursion_error",
        "timeout",
        "memory_error",
    ],
    "assertion": [
        "wrong_output",
        "partial_output",
        "missing_output",
        "wrong_type",
        "off_by_one",
        "boundary_error",
    ],
}

# Flat list of all 19 fine-grained causes
ALL_FINE_CAUSES: List[str] = [
    cause for causes in LLMFIX_TAXONOMY.values() for cause in causes
]

# Coarse category ordering (matches contingency table columns)
COARSE_CATEGORIES: List[str] = ["syntax", "runtime", "assertion"]


CONFIG = ExperimentConfig()
