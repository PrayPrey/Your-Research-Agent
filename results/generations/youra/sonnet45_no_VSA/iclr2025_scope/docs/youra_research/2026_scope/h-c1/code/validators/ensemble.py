"""
Ensemble Validator - Combines structural and metamorphic contract validation
Epic C-2: Parallel validation wrapper combining h-m1 + h-m2 with timeout and deduplication
"""

import sys
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import List, Dict, Any
import copy

# Add h-m1 and h-m2 code to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m1/code'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m2/code'))

from contracts.validator import validate_structural
from contracts.metamorphic import validate_metamorphic


class EnsembleValidator:
    """
    Parallel execution wrapper for structural + metamorphic validators
    with timeout handling and violation deduplication
    """

    def __init__(self, n_workers=4, timeout_seconds=10):
        """
        Initialize ensemble validator

        Args:
            n_workers: Number of parallel workers
            timeout_seconds: Timeout for each validation strategy
        """
        self.executor = ThreadPoolExecutor(max_workers=n_workers)
        self.timeout = timeout_seconds

    def validate(self, model, data):
        """
        Run structural AND metamorphic validation in parallel

        Args:
            model: Model instance to validate
            data: Test data

        Returns:
            List of violations with source attribution
        """
        violations = []

        # Deep copy model to prevent state mutation across validators
        model_structural = copy.deepcopy(model)
        model_metamorphic = copy.deepcopy(model)

        # Wrap validators to catch exceptions
        def structural_wrapper():
            try:
                return validate_structural(model_structural, data)
            except Exception as e:
                return [{"type": "structural", "error": str(e), "source": "structural"}]

        def metamorphic_wrapper():
            try:
                return validate_metamorphic(model_metamorphic, data)
            except Exception as e:
                return [{"type": "metamorphic", "error": str(e), "source": "metamorphic"}]

        # Submit both validators in parallel
        future_structural = self.executor.submit(structural_wrapper)
        future_metamorphic = self.executor.submit(metamorphic_wrapper)

        # Collect results with timeout
        try:
            structural_violations = future_structural.result(timeout=self.timeout)
            violations.extend([{**v, "source": "structural"} for v in structural_violations])
        except FuturesTimeoutError:
            violations.append({"type": "timeout", "source": "structural", "error": "Validation timeout"})
        except Exception as e:
            violations.append({"type": "error", "source": "structural", "error": str(e)})

        try:
            metamorphic_violations = future_metamorphic.result(timeout=self.timeout)
            violations.extend([{**v, "source": "metamorphic"} for v in metamorphic_violations])
        except FuturesTimeoutError:
            violations.append({"type": "timeout", "source": "metamorphic", "error": "Validation timeout"})
        except Exception as e:
            violations.append({"type": "error", "source": "metamorphic", "error": str(e)})

        # Deduplication: merge violations from both sources
        violations = self._deduplicate_violations(violations)

        return violations

    def _deduplicate_violations(self, violations: List[Dict]) -> List[Dict]:
        """
        Identify and merge violations detected by both validators

        Strategy: If violation has same type+error_message from both sources,
        merge into single violation with source='both'
        """
        seen = {}
        deduplicated = []

        for v in violations:
            key = (v.get("type"), v.get("error", ""))
            if key in seen:
                # Duplicate found - update source to 'both'
                seen[key]["source"] = "both"
            else:
                seen[key] = v

        return list(seen.values())

    def __del__(self):
        """Cleanup executor on deletion"""
        self.executor.shutdown(wait=False)


def validate_combined(model, data, timeout=10):
    """
    Convenience function for combined validation

    Args:
        model: Model to validate
        data: Test data
        timeout: Timeout in seconds

    Returns:
        List of violations
    """
    validator = EnsembleValidator(n_workers=4, timeout_seconds=timeout)
    return validator.validate(model, data)
