"""Frama-C/WP verifier integration."""

import subprocess
import json
import re
from pathlib import Path
from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass

from .llm_client import ACSLSpec


class ProofStatus(Enum):
    """Proof obligation status from Frama-C/WP."""
    VALID = "Valid"
    QED = "Qed"
    UNKNOWN = "Unknown"
    INVALID = "Invalid"


@dataclass
class ProofObligation:
    """Single verification condition."""
    obligation_id: str
    location: str
    obligation_type: str
    formula: str
    status: ProofStatus
    prover: Optional[str]
    time_ms: float


@dataclass
class VerificationResult:
    """Frama-C/WP verification output."""
    total_obligations: int
    proved_obligations: int
    failed_obligations: int
    proof_discharge_rate: float
    obligations: List[ProofObligation]
    raw_output: str


class FramaCVerifier:
    """Execute Frama-C/WP and parse results."""

    def __init__(
        self,
        timeout_per_obligation: int = 10,
        provers: List[str] = None
    ):
        """
        Args:
            timeout_per_obligation: Seconds per proof (default: 10)
            provers: SMT solvers to use
        """
        self.timeout = timeout_per_obligation
        self.provers = provers or ["alt-ergo", "z3"]
        self._check_installation()

    def verify(self, acsl_spec: ACSLSpec, temp_dir: Path) -> VerificationResult:
        """
        Verify ACSL specification with Frama-C/WP.

        Args:
            acsl_spec: ACSL-annotated C code
            temp_dir: Directory for temporary files

        Returns:
            VerificationResult with proof obligations
        """
        # Write annotated code to file
        c_file = temp_dir / "program.c"
        c_file.write_text(acsl_spec.annotated_code)

        # Execute Frama-C/WP
        cmd = [
            "frama-c",
            "-wp",
            f"-wp-timeout", str(self.timeout),
            f"-wp-prover", ','.join(self.provers),
            "-wp-out", str(temp_dir),
            "-wp-report", str(temp_dir / "report.json"),
            str(c_file)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout * 100
            )

            # Parse WP output
            return self._parse_wp_output(result.stdout, result.stderr, temp_dir)

        except subprocess.TimeoutExpired:
            return VerificationResult(
                total_obligations=0,
                proved_obligations=0,
                failed_obligations=0,
                proof_discharge_rate=0.0,
                obligations=[],
                raw_output="TIMEOUT"
            )
        except Exception as e:
            return VerificationResult(
                total_obligations=0,
                proved_obligations=0,
                failed_obligations=0,
                proof_discharge_rate=0.0,
                obligations=[],
                raw_output=f"ERROR: {str(e)}"
            )

    def _parse_wp_output(self, stdout: str, stderr: str, temp_dir: Path) -> VerificationResult:
        """Parse Frama-C/WP text output and JSON report."""
        # Combine stdout and stderr for raw output
        raw_output = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"

        # Try JSON report first
        report_file = temp_dir / "report.json"
        if report_file.exists():
            try:
                with open(report_file) as f:
                    report = json.load(f)
                return self._parse_json_report(report, raw_output)
            except:
                pass

        # Fallback: parse text output
        return self._parse_text_output(stdout + stderr, raw_output)

    def _parse_json_report(self, report: Dict, raw_output: str) -> VerificationResult:
        """Parse structured JSON report from WP."""
        obligations = []

        for goal in report.get("goals", []):
            obligations.append(ProofObligation(
                obligation_id=goal.get("id", "unknown"),
                location=f"{goal.get('file', 'unknown')}:{goal.get('line', 0)}:{goal.get('function', 'unknown')}",
                obligation_type=goal.get("kind", "unknown"),
                formula=goal.get("property", ""),
                status=ProofStatus(goal.get("status", "Unknown")),
                prover=goal.get("prover"),
                time_ms=goal.get("time", 0.0)
            ))

        proved = sum(1 for o in obligations if o.status in [ProofStatus.VALID, ProofStatus.QED])
        total = len(obligations)

        return VerificationResult(
            total_obligations=total,
            proved_obligations=proved,
            failed_obligations=total - proved,
            proof_discharge_rate=(proved / total * 100) if total > 0 else 0.0,
            obligations=obligations,
            raw_output=raw_output
        )

    def _parse_text_output(self, output: str, raw_output: str) -> VerificationResult:
        """Fallback text parser (when JSON not available)."""
        # Parse text patterns like:
        # [wp] [Alt-Ergo] goal typed_binary_search_post: Valid
        pattern = r'\[wp\].*?goal\s+(\S+):\s+(Valid|Qed|Unknown|Invalid)'
        matches = re.findall(pattern, output)

        obligations = [
            ProofObligation(
                obligation_id=match[0],
                location="unknown",
                obligation_type="unknown",
                formula="",
                status=ProofStatus(match[1]),
                prover=None,
                time_ms=0.0
            )
            for match in matches
        ]

        proved = sum(1 for o in obligations if o.status in [ProofStatus.VALID, ProofStatus.QED])
        total = len(obligations)

        return VerificationResult(
            total_obligations=total,
            proved_obligations=proved,
            failed_obligations=total - proved,
            proof_discharge_rate=(proved / total * 100) if total > 0 else 0.0,
            obligations=obligations,
            raw_output=raw_output
        )

    def _check_installation(self):
        """Verify Frama-C/WP is installed."""
        try:
            subprocess.run(["frama-c", "-version"], capture_output=True, check=True)
        except FileNotFoundError:
            raise RuntimeError("Frama-C not installed. Run: opam install frama-c")
