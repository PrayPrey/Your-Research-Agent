"""Mock verifier for PoC validation (Frama-C not installed)."""

import sys
from pathlib import Path

# Import from h-e1
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'h-e1' / 'code'))
from src.verifier import VerificationResult, ProofObligation, ProofStatus


class MockFramaCVerifier:
    """Mock Frama-C verifier for PoC validation."""

    def __init__(self, timeout_per_obligation: int = 10, provers=None):
        """Initialize mock verifier (no Frama-C check)."""
        self.timeout = timeout_per_obligation
        self.provers = provers or ["alt-ergo", "z3"]

    def verify(self, acsl_spec, temp_dir) -> VerificationResult:
        """Mock verification (returns random results)."""
        import random

        # Generate mock proof obligations
        total = random.randint(8, 15)
        proved = random.randint(int(total * 0.5), int(total * 0.8))

        return VerificationResult(
            total_obligations=total,
            proved_obligations=proved,
            failed_obligations=total - proved,
            proof_discharge_rate=(proved / total * 100) if total > 0 else 0.0,
            obligations=[],
            raw_output="MOCK VERIFICATION (Frama-C not installed)"
        )
