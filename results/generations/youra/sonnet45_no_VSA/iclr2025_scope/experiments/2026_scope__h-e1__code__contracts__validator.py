"""
Contract Validator - T-03
Execute contracts with timeout enforcement and version stability testing.
"""
from dataclasses import dataclass
from typing import Literal, List, Dict, Optional, Any
import signal
import time
import subprocess
import sys
import os


@dataclass
class ValidationResult:
    """Result of contract validation execution."""
    defect_id: str
    status: Literal["PASS", "FAIL", "TIMEOUT", "NOT_EXPRESSIBLE"]
    execution_time: float
    error_message: str = ""
    version_tested: str = ""


class TimeoutException(Exception):
    """Raised when contract execution exceeds timeout."""
    pass


class ContractValidator:
    """Execute contracts with timeout enforcement and version stability testing."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._results: List[ValidationResult] = []

    def validate_contract(self, contract: 'Contract') -> ValidationResult:
        """Execute single contract with timeout enforcement."""
        return self._execute_with_timeout(contract)

    def batch_validate(self, contracts: List['Contract']) -> List[ValidationResult]:
        """Execute all contracts sequentially."""
        results = []
        for contract in contracts:
            result = self.validate_contract(contract)
            results.append(result)
            self._results.append(result)
        return results

    def check_version_stability(
        self,
        contract: 'Contract',
        versions: List[str]
    ) -> Dict[str, bool]:
        """
        Test contract across multiple PyTorch versions.
        For this PoC, we simulate version testing based on contract type.
        """
        import torch
        current_version = torch.__version__.split('+')[0]  # Remove CUDA suffix

        stability = {}

        # Simulate version stability based on contract characteristics
        # Structural contracts are most stable, composition least stable
        for version in versions:
            if contract.invariant_type == "structural":
                # Structural contracts (shape, dtype, device) are very stable
                stability[version] = True
            elif contract.invariant_type == "metamorphic":
                # Metamorphic contracts (train/eval, autocast) mostly stable
                # Simulate 90% stability
                stability[version] = version >= "1.11"
            elif contract.invariant_type == "composition":
                # Composition contracts less stable across versions
                # Simulate 80% stability
                stability[version] = version >= "1.12"

        return stability

    def _timeout_handler(self, signum: int, frame: Any) -> None:
        """Signal handler for timeout enforcement."""
        raise TimeoutException(f"Contract execution exceeded {self.timeout}s")

    def _execute_with_timeout(self, contract: 'Contract') -> ValidationResult:
        """Core execution logic with signal-based timeout."""
        # For systems that don't support signal.alarm (Windows), use simple timeout
        if not hasattr(signal, 'SIGALRM'):
            return self._execute_simple(contract)

        # Set up signal handler
        old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)

        try:
            signal.alarm(self.timeout)
            start = time.time()

            try:
                result = contract.validate(timeout=self.timeout)
                elapsed = time.time() - start
                signal.alarm(0)  # Cancel alarm

                return ValidationResult(
                    defect_id=contract.defect_id,
                    status="PASS" if result else "FAIL",
                    execution_time=elapsed
                )

            except TimeoutException:
                return ValidationResult(
                    defect_id=contract.defect_id,
                    status="TIMEOUT",
                    execution_time=self.timeout,
                    error_message="Exceeded 10s execution limit"
                )

            except AssertionError as e:
                elapsed = time.time() - start
                return ValidationResult(
                    defect_id=contract.defect_id,
                    status="FAIL",
                    execution_time=elapsed,
                    error_message=str(e)
                )

            except Exception as e:
                elapsed = time.time() - start
                return ValidationResult(
                    defect_id=contract.defect_id,
                    status="FAIL",
                    execution_time=elapsed,
                    error_message=f"Unexpected error: {str(e)}"
                )

        finally:
            signal.alarm(0)  # Ensure alarm is cancelled
            signal.signal(signal.SIGALRM, old_handler)  # Restore old handler

    def _execute_simple(self, contract: 'Contract') -> ValidationResult:
        """Simple execution without signal.alarm (for Windows compatibility)."""
        start = time.time()

        try:
            result = contract.validate(timeout=self.timeout)
            elapsed = time.time() - start

            if elapsed > self.timeout:
                return ValidationResult(
                    defect_id=contract.defect_id,
                    status="TIMEOUT",
                    execution_time=elapsed,
                    error_message="Exceeded 10s execution limit"
                )

            return ValidationResult(
                defect_id=contract.defect_id,
                status="PASS" if result else "FAIL",
                execution_time=elapsed
            )

        except AssertionError as e:
            elapsed = time.time() - start
            return ValidationResult(
                defect_id=contract.defect_id,
                status="FAIL",
                execution_time=elapsed,
                error_message=str(e)
            )

        except Exception as e:
            elapsed = time.time() - start
            return ValidationResult(
                defect_id=contract.defect_id,
                status="FAIL",
                execution_time=elapsed,
                error_message=f"Unexpected error: {str(e)}"
            )


if __name__ == "__main__":
    # Test validation
    import sys
    sys.path.append('..')
    from data.corpus_loader import DefectCorpusLoader
    from contracts.generator import ContractGenerator

    loader = DefectCorpusLoader()
    corpus = loader.load_corpus()
    filtered = loader.filter_environment_api_defects(corpus)

    generator = ContractGenerator()
    validator = ContractValidator(timeout=10)

    contracts = []
    for _, defect in filtered.head(20).iterrows():
        contract = generator.generate_from_defect(defect)
        if contract:
            contracts.append(contract)

    results = validator.batch_validate(contracts)

    print(f"\nValidation Results:")
    print(f"Total: {len(results)}")
    print(f"PASS: {sum(1 for r in results if r.status == 'PASS')}")
    print(f"FAIL: {sum(1 for r in results if r.status == 'FAIL')}")
    print(f"TIMEOUT: {sum(1 for r in results if r.status == 'TIMEOUT')}")

    # Test version stability
    if contracts:
        stability = validator.check_version_stability(
            contracts[0],
            versions=["1.11", "1.12", "1.13"]
        )
        print(f"\nVersion Stability for {contracts[0].defect_id}:")
        print(stability)
