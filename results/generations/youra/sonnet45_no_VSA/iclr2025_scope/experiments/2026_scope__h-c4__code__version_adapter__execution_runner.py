"""Execution runner for isolated environment script execution."""

import re
import subprocess
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .environment_manager import Environment


@dataclass
class ExecutionResult:
    """Result of script execution in isolated environment."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    contract_violations: List[str]


class ExecutionRunner:
    """Executes scripts in isolated environments."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def run_in_environment(
        self,
        env: 'Environment',
        script: str,
        contracts: List[str]
    ) -> ExecutionResult:
        """
        Execute script with contracts in isolated environment.

        Args:
            env: Target environment
            script: Python script path or code string
            contracts: Contract decorators to inject (unused in minimal impl)

        Returns:
            ExecutionResult with contract violation logs
        """
        import time

        start_time = time.time()

        try:
            result = subprocess.run(
                [env.python_path, script],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            execution_time = time.time() - start_time

            # Parse stderr for contract violations
            contract_violations = self._parse_contract_violations(result.stderr)

            return ExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time,
                contract_violations=contract_violations
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Script timed out after {self.timeout}s",
                exit_code=-1,
                execution_time=execution_time,
                contract_violations=[]
            )

    def _parse_contract_violations(self, stderr: str) -> List[str]:
        """Parse stderr for contract violation messages."""
        violations = []

        # Pattern: ShapeViolation, DtypeViolation, MetamorphicViolation
        violation_patterns = [
            r"ShapeViolation: (.+)",
            r"DtypeViolation: (.+)",
            r"MetamorphicViolation: (.+)",
            r"contract violation: (.+)",
        ]

        for pattern in violation_patterns:
            matches = re.findall(pattern, stderr, re.IGNORECASE)
            violations.extend(matches)

        return violations
