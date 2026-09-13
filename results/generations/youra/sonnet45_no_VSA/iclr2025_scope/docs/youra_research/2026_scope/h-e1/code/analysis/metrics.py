"""
Metrics Calculator - T-05
Calculate contractability rate with 95% CI, stratified analysis, gate evaluation.
"""
from dataclasses import dataclass
from typing import Literal, List, Dict
import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class ContractabilityMetrics:
    """Contractability metrics with confidence intervals."""
    overall_rate: float
    structural_rate: float
    metamorphic_rate: float
    composition_rate: float
    ci_lower: float
    ci_upper: float
    kappa: float
    gate_status: Literal["PASS", "FAIL"]


class MetricsCalculator:
    """Calculate contractability metrics and evaluate gate conditions."""

    def calculate_contractability_rate(
        self,
        coder1: List[bool],
        coder2: List[bool],
        defect_types: List[str]
    ) -> ContractabilityMetrics:
        """Calculate overall + stratified rates with 95% CI."""

        # Use agreement between coders (logical AND)
        agreed_contractable = [c1 and c2 for c1, c2 in zip(coder1, coder2)]

        # Overall rate
        total = len(agreed_contractable)
        contractable_count = sum(agreed_contractable)
        overall_rate = (contractable_count / total * 100) if total > 0 else 0.0

        # Calculate 95% CI
        ci_lower, ci_upper = self.compute_confidence_interval(contractable_count, total)
        ci_lower_pct = ci_lower * 100
        ci_upper_pct = ci_upper * 100

        # Stratified analysis
        structural_rate = self._calculate_stratified_rate(
            agreed_contractable, defect_types, "structural"
        )
        metamorphic_rate = self._calculate_stratified_rate(
            agreed_contractable, defect_types, "metamorphic"
        )
        composition_rate = self._calculate_stratified_rate(
            agreed_contractable, defect_types, "composition"
        )

        # Calculate Cohen's kappa
        from sklearn.metrics import cohen_kappa_score
        kappa = cohen_kappa_score(coder1, coder2)

        # Evaluate gate condition
        gate_pass = self.evaluate_gate_condition(overall_rate, ci_lower_pct, kappa)

        return ContractabilityMetrics(
            overall_rate=overall_rate,
            structural_rate=structural_rate,
            metamorphic_rate=metamorphic_rate,
            composition_rate=composition_rate,
            ci_lower=ci_lower_pct,
            ci_upper=ci_upper_pct,
            kappa=kappa,
            gate_status="PASS" if gate_pass else "FAIL"
        )

    def compute_confidence_interval(
        self,
        successes: int,
        total: int
    ) -> tuple:
        """Calculate 95% CI using Wilson score method."""
        if total == 0:
            return (0.0, 0.0)

        # Use Wilson score interval approximation
        p = successes / total
        z = 1.96  # 95% confidence
        denominator = 1 + z**2 / total
        center = (p + z**2 / (2 * total)) / denominator
        margin = z * np.sqrt((p * (1 - p) / total + z**2 / (4 * total**2))) / denominator

        ci_lower = max(0, center - margin)
        ci_upper = min(1, center + margin)

        return (ci_lower, ci_upper)

    def evaluate_gate_condition(
        self,
        contractability_rate: float,
        ci_lower: float,
        kappa: float
    ) -> bool:
        """Evaluate MUST_WORK gate condition."""
        # Gate: ≥40% contractability with CI lower bound >35% AND kappa ≥0.7
        return contractability_rate >= 40.0 and ci_lower > 35.0 and kappa >= 0.7

    def compare_to_baselines(self, contractability_rate: float) -> dict:
        """Compare to no-CI and CI-only baselines."""
        no_ci = 0.0
        ci_only = 17.5  # 15-20% midpoint

        improvement_over_ci = (
            ((contractability_rate - ci_only) / ci_only * 100)
            if ci_only > 0 else 0.0
        )

        return {
            "no_ci_baseline": no_ci,
            "ci_only_baseline": ci_only,
            "proposed": contractability_rate,
            "improvement_over_ci": improvement_over_ci
        }

    def _calculate_stratified_rate(
        self,
        contractable: List[bool],
        types: List[str],
        target_type: str
    ) -> float:
        """Calculate contractability rate for specific defect type."""
        indices = [i for i, t in enumerate(types) if t == target_type]

        if not indices:
            return 0.0

        type_contractable = [contractable[i] for i in indices]
        count = sum(type_contractable)
        total = len(type_contractable)

        return (count / total * 100) if total > 0 else 0.0


if __name__ == "__main__":
    # Test metrics calculation
    import sys
    sys.path.append('..')
    from data.corpus_loader import DefectCorpusLoader
    from contracts.generator import ContractGenerator
    from contracts.validator import ContractValidator
    from analysis.retrospective_coder import RetrospectiveCoder

    loader = DefectCorpusLoader()
    corpus = loader.load_corpus()
    filtered = loader.filter_environment_api_defects(corpus)

    generator = ContractGenerator()
    validator = ContractValidator(timeout=10)

    # Generate and validate
    contracts = []
    validation_results = []
    stability_results = []

    for _, defect in filtered.head(100).iterrows():
        contract = generator.generate_from_defect(defect)
        contracts.append(contract)

        if contract:
            result = validator.validate_contract(contract)
            validation_results.append(result)

            stability = validator.check_version_stability(
                contract,
                versions=["1.11", "1.12", "1.13"]
            )
            stability_results.append(stability)
        else:
            validation_results.append(None)
            stability_results.append({})

    # Retrospective coding
    coder = RetrospectiveCoder(filtered.head(100), random_seed=42)

    valid_indices = [i for i, c in enumerate(contracts) if c is not None and validation_results[i] is not None]
    valid_contracts = [contracts[i] for i in valid_indices]
    valid_results = [validation_results[i] for i in valid_indices]
    valid_stability = [stability_results[i] for i in valid_indices]
    valid_types = [filtered.iloc[i]['type'] for i in valid_indices]

    coder1_labels, coder2_labels = coder.code_corpus(
        valid_contracts,
        valid_results,
        valid_stability
    )

    # Calculate metrics
    calc = MetricsCalculator()
    metrics = calc.calculate_contractability_rate(
        coder1_labels,
        coder2_labels,
        valid_types
    )

    print(f"\nContractability Metrics:")
    print(f"Overall: {metrics.overall_rate:.1f}% (95% CI: {metrics.ci_lower:.1f}%-{metrics.ci_upper:.1f}%)")
    print(f"Structural: {metrics.structural_rate:.1f}%")
    print(f"Metamorphic: {metrics.metamorphic_rate:.1f}%")
    print(f"Composition: {metrics.composition_rate:.1f}%")
    print(f"Cohen's Kappa: {metrics.kappa:.3f}")
    print(f"Gate Status: {metrics.gate_status}")

    baselines = calc.compare_to_baselines(metrics.overall_rate)
    print(f"\nBaseline Comparison:")
    print(f"Improvement over CI-only: {baselines['improvement_over_ci']:.1f}%")
