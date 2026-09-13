"""
Contract Validator for H-C2
Orchestrates contract execution and result aggregation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import time
import numpy as np


@dataclass
class DefectReport:
    """Report for single detected defect."""
    defect_type: str
    contract_name: str
    details: Dict[str, Any]
    validation_time: float


@dataclass
class ValidationReport:
    """Aggregated validation report."""
    passed: bool
    defects_detected: List[DefectReport]
    validation_time: float
    contract_results: Dict[str, Any]


class ContractValidator:
    """Execute contracts at conversion boundaries."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def validate_conversion(
        self,
        src_model: Any,
        tgt_model: Any,
        test_inputs: List[np.ndarray],
        contracts: List[callable],
        src_adapter,
        tgt_adapter
    ) -> ValidationReport:
        """Run all contracts on multiple test inputs."""
        start_time = time.time()
        contract_results = {}
        defects_detected = []

        # Execute each contract
        for contract_func in contracts:
            contract_name = contract_func.__name__

            # Aggregate results across multiple test inputs
            results = []
            for test_input in test_inputs:
                try:
                    result = contract_func(
                        src_model, tgt_model, test_input,
                        src_adapter, tgt_adapter
                    )
                    results.append(result)
                except Exception as e:
                    from contracts import ContractResult
                    results.append(ContractResult(
                        passed=False,
                        defect_type="ContractExecutionError",
                        details={"error": str(e)}
                    ))

            # Aggregate results (contract passes if all inputs pass)
            passed_count = sum(1 for r in results if r.passed)
            aggregated_passed = (passed_count == len(results))

            # Collect defect details
            if not aggregated_passed:
                failed_results = [r for r in results if not r.passed]
                if failed_results:
                    defect_type = failed_results[0].defect_type
                    details = failed_results[0].details
                    defects_detected.append(DefectReport(
                        defect_type=defect_type or "Unknown",
                        contract_name=contract_name,
                        details=details,
                        validation_time=sum(r.validation_time for r in results)
                    ))

            contract_results[contract_name] = {
                "passed": aggregated_passed,
                "passed_count": passed_count,
                "total_count": len(results),
                "total_time": sum(r.validation_time for r in results)
            }

        validation_time = time.time() - start_time
        passed = len(defects_detected) == 0

        return ValidationReport(
            passed=passed,
            defects_detected=defects_detected,
            validation_time=validation_time,
            contract_results=contract_results
        )
