"""Feedback parser for 3-dimensional structured feedback extraction."""

import re
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass

from .llm_client import ACSLSpec
from .verifier import VerificationResult, ProofObligation, ProofStatus


@dataclass
class WitnessInstantiation:
    """Dimension 1: Concrete counterexample values."""
    failed_obligation_id: str
    witness_values: Dict[str, str]
    violating_path: List[str]


@dataclass
class LogicalStructure:
    """Dimension 2: Which proof obligation failed."""
    failed_obligations: List[ProofObligation]
    failure_summary: str
    critical_failures: List[str]


@dataclass
class DependencyPreservation:
    """Dimension 3: Inter-specification dependencies."""
    broken_dependencies: List[Tuple[str, str]]
    dependency_chain: List[str]
    suggested_fixes: List[str]


@dataclass
class StructuredFeedback:
    """Complete 3-dimensional feedback."""
    witness: WitnessInstantiation
    structure: LogicalStructure
    dependency: DependencyPreservation
    natural_language: str


class FeedbackExtractor:
    """Extract 3-dimensional feedback from verification results."""

    def extract_feedback(
        self,
        result: VerificationResult,
        acsl_spec: ACSLSpec
    ) -> Optional[StructuredFeedback]:
        """
        Extract structured feedback from failed verifications.

        Args:
            result: WP output
            acsl_spec: Current specification

        Returns:
            StructuredFeedback with all 3 dimensions, or None if all proved
        """
        failed = [o for o in result.obligations if o.status not in [ProofStatus.VALID, ProofStatus.QED]]

        if not failed:
            return None  # All proved - no feedback needed

        # Dimension 1: Witness Instantiation
        witness = self._extract_witness(failed, result.raw_output)

        # Dimension 2: Logical Structure
        structure = self._analyze_logical_structure(failed, acsl_spec)

        # Dimension 3: Dependency Preservation
        dependency = self._analyze_dependencies(failed, acsl_spec)

        # Convert to natural language for LLM
        nl_feedback = self._format_for_llm(witness, structure, dependency)

        return StructuredFeedback(
            witness=witness,
            structure=structure,
            dependency=dependency,
            natural_language=nl_feedback
        )

    def _extract_witness(
        self,
        failed: List[ProofObligation],
        raw_output: str
    ) -> WitnessInstantiation:
        """
        Dimension 1: Parse counterexample values from WP output.
        """
        # Most critical failure
        critical = failed[0]

        # Parse counterexample section
        witness_pattern = r'Counter-example:\s+((?:\s+\w+(?:\[\d+\])?\s*=\s*[^\n]+\n?)+)'
        match = re.search(witness_pattern, raw_output)

        witness_values = {}
        violating_path = []

        if match:
            witness_text = match.group(1)
            # Parse variable assignments: x = 5
            assignments = re.findall(r'(\w+(?:\[\d+\])?)\s*=\s*([^\n]+)', witness_text)
            witness_values = {var: val.strip() for var, val in assignments}

            # Extract execution path (if available)
            path_pattern = r'Execution path:.*?->\s*(\w+)'
            violating_path = re.findall(path_pattern, raw_output)

        return WitnessInstantiation(
            failed_obligation_id=critical.obligation_id,
            witness_values=witness_values,
            violating_path=violating_path or ["unknown"]
        )

    def _analyze_logical_structure(
        self,
        failed: List[ProofObligation],
        acsl_spec: ACSLSpec
    ) -> LogicalStructure:
        """
        Dimension 2: Identify which types of obligations failed.
        """
        # Group failures by type
        by_type = {
            "precondition": [],
            "postcondition": [],
            "loop_invariant": [],
            "assertion": []
        }

        for obligation in failed:
            otype = obligation.obligation_type
            if otype in by_type:
                by_type[otype].append(obligation)

        # Identify critical failures
        critical = []
        if by_type["precondition"]:
            critical.extend([o.obligation_id for o in by_type["precondition"]])
        if by_type["loop_invariant"]:
            critical.extend([o.obligation_id for o in by_type["loop_invariant"]])

        # Generate summary
        summary_parts = []
        for otype, obligations in by_type.items():
            if obligations:
                summary_parts.append(f"{len(obligations)} {otype}(s) failed")

        summary = "Verification failures: " + ", ".join(summary_parts) if summary_parts else "Unknown failures"

        return LogicalStructure(
            failed_obligations=failed,
            failure_summary=summary,
            critical_failures=critical
        )

    def _analyze_dependencies(
        self,
        failed: List[ProofObligation],
        acsl_spec: ACSLSpec
    ) -> DependencyPreservation:
        """
        Dimension 3: Detect inter-specification dependencies.
        """
        broken_deps = []
        dependency_chain = []
        suggested_fixes = []

        # Rule 1: If precondition failed, all downstream obligations affected
        precond_failed = any(o.obligation_type == "precondition" for o in failed)
        if precond_failed:
            dependency_chain.append("precondition_violation")
            suggested_fixes.append("Strengthen function preconditions to exclude invalid inputs")

        # Rule 2: If loop invariant failed, check if it depends on precondition
        loop_inv_failed = [o for o in failed if o.obligation_type == "loop_invariant"]
        if loop_inv_failed and acsl_spec.preconditions:
            for inv in loop_inv_failed:
                for precond in acsl_spec.preconditions:
                    if self._shares_variables(inv.formula, precond):
                        broken_deps.append((inv.obligation_id, "precondition"))
                        dependency_chain.append(f"{inv.obligation_id}_depends_on_precondition")
                        suggested_fixes.append(f"Loop invariant must preserve precondition assumptions")

        # Rule 3: If postcondition failed, check loop invariant relationship
        postcond_failed = [o for o in failed if o.obligation_type == "postcondition"]
        if postcond_failed and acsl_spec.loop_invariants:
            for post in postcond_failed:
                for inv in acsl_spec.loop_invariants:
                    if self._shares_variables(post.formula, inv):
                        broken_deps.append((post.obligation_id, "loop_invariant"))
                        dependency_chain.append(f"{post.obligation_id}_depends_on_loop_invariant")
                        suggested_fixes.append(f"Strengthen loop invariant to imply postcondition")

        return DependencyPreservation(
            broken_dependencies=broken_deps,
            dependency_chain=dependency_chain,
            suggested_fixes=suggested_fixes
        )

    def _shares_variables(self, formula1: str, formula2: str) -> bool:
        """Check if two ACSL formulas share common variables."""
        # Extract variable names (simplified heuristic)
        var_pattern = r'\b[a-z_][a-z0-9_]*\b'
        vars1 = set(re.findall(var_pattern, formula1.lower()))
        vars2 = set(re.findall(var_pattern, formula2.lower()))

        # Filter out ACSL keywords
        keywords = {"requires", "ensures", "loop", "invariant", "assert", "result", "old", "valid"}
        vars1 -= keywords
        vars2 -= keywords

        return bool(vars1 & vars2)

    def _format_for_llm(
        self,
        witness: WitnessInstantiation,
        structure: LogicalStructure,
        dependency: DependencyPreservation
    ) -> str:
        """Convert structured feedback to natural language prompt."""

        feedback_parts = [
            "VERIFICATION FEEDBACK:",
            "",
            f"SUMMARY: {structure.failure_summary}",
            ""
        ]

        # Dimension 1: Witness
        if witness.witness_values:
            feedback_parts.append("COUNTEREXAMPLE (Dimension 1: Witness Instantiation):")
            feedback_parts.append(f"Failed obligation: {witness.failed_obligation_id}")
            feedback_parts.append("Concrete values that violate specification:")
            for var, val in witness.witness_values.items():
                feedback_parts.append(f"  - {var} = {val}")
            if witness.violating_path:
                feedback_parts.append(f"Execution path: {' -> '.join(witness.violating_path)}")
            feedback_parts.append("")

        # Dimension 2: Logical Structure
        feedback_parts.append("FAILED OBLIGATIONS (Dimension 2: Logical Structure):")
        for obligation in structure.failed_obligations[:5]:
            feedback_parts.append(f"  - {obligation.obligation_type} at {obligation.location}")
            if obligation.formula:
                feedback_parts.append(f"    Formula: {obligation.formula}")
            feedback_parts.append(f"    Status: {obligation.status.value}")
        feedback_parts.append("")

        # Dimension 3: Dependencies
        if dependency.broken_dependencies:
            feedback_parts.append("DEPENDENCY VIOLATIONS (Dimension 3: Preservation):")
            for clause_id, depends_on in dependency.broken_dependencies:
                feedback_parts.append(f"  - {clause_id} depends on {depends_on} (broken)")
            feedback_parts.append("")

        # Suggested fixes
        if dependency.suggested_fixes:
            feedback_parts.append("SUGGESTED REFINEMENTS:")
            for fix in dependency.suggested_fixes:
                feedback_parts.append(f"  - {fix}")
            feedback_parts.append("")

        return "\n".join(feedback_parts)
