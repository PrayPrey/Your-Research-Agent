"""False positive detector."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from version_adapter import ExecutionResult


@dataclass
class FalsePositive:
    """Detected false positive instance."""
    script_id: str
    contract_id: str
    source_version: str
    target_version: str
    violation_message: str
    breakage_type: str
    timestamp: datetime


class FalsePositiveDetector:
    """Detects and categorizes false positives."""

    def detect_false_positive(
        self,
        baseline_result: 'ExecutionResult',
        target_result: 'ExecutionResult',
        script_id: str,
        source_version: str,
        target_version: str
    ) -> Optional[FalsePositive]:
        """
        Detect false positive: baseline passes, target fails on valid code.

        Args:
            baseline_result: Execution on source version
            target_result: Execution on target version
            script_id: Script identifier
            source_version: Baseline library version
            target_version: Updated library version

        Returns:
            FalsePositive if detected, else None
        """
        # Check for false positive
        if baseline_result.success and not target_result.success:
            # Check if it's a contract violation
            if (target_result.contract_violations or
                "contract violation" in target_result.stderr.lower() or
                "ShapeViolation" in target_result.stderr or
                "DtypeViolation" in target_result.stderr or
                "MetamorphicViolation" in target_result.stderr):

                violation_msg = self._extract_violation_message(target_result)
                contract_id = self._extract_contract_id(violation_msg)
                breakage_type = self.categorize_breakage_heuristic(violation_msg)

                fp = FalsePositive(
                    script_id=script_id,
                    contract_id=contract_id,
                    source_version=source_version,
                    target_version=target_version,
                    violation_message=violation_msg,
                    breakage_type=breakage_type,
                    timestamp=datetime.now()
                )

                return fp

        return None

    def categorize_breakage(self, fp: FalsePositive) -> str:
        """Categorize false positive root cause via heuristics."""
        return self.categorize_breakage_heuristic(fp.violation_message)

    def categorize_breakage_heuristic(self, violation_message: str) -> str:
        """
        Categorize breakage type from violation message.

        Returns:
            "api_deprecation" | "behavioral_change" | "numerical_drift" | "unknown"
        """
        msg_lower = violation_message.lower()

        if ("deprecationwarning" in msg_lower or
            "removed in version" in msg_lower or
            "no longer supported" in msg_lower):
            return "api_deprecation"

        elif ("dtype" in msg_lower or "shape" in msg_lower or
              "type mismatch" in msg_lower):
            return "behavioral_change"

        elif ("tolerance" in msg_lower or "rtol" in msg_lower or
              "atol" in msg_lower or "numerical" in msg_lower):
            return "numerical_drift"

        else:
            return "unknown"

    def _extract_violation_message(self, result) -> str:
        """Extract violation message from execution result."""
        if result.contract_violations:
            return result.contract_violations[0]
        return result.stderr

    def _extract_contract_id(self, violation_message: str) -> str:
        """Extract contract ID from violation message."""
        # Simple heuristic: return first word
        if ":" in violation_message:
            return violation_message.split(":")[0].strip()
        return "unknown_contract"
