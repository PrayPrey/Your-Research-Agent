"""Feedback Ablation Module - Controls information richness across 4 conditions"""

from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sys
import os

h_e1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../h-e1/code'))
sys.path.insert(0, h_e1_path)

try:
    from src.feedback_parser import StructuredFeedback, WitnessInstantiation, LogicalStructure, DependencyPreservation
except ImportError:
    # Fallback: create mock classes
    from dataclasses import dataclass
    from typing import List, Dict

    @dataclass
    class WitnessInstantiation:
        counterexamples: List = None
        input_states: List = None
        trace_summaries: List = None

        def __post_init__(self):
            if self.counterexamples is None:
                self.counterexamples = []
            if self.input_states is None:
                self.input_states = []
            if self.trace_summaries is None:
                self.trace_summaries = []

    @dataclass
    class LogicalStructure:
        failure_summary: Dict = None
        obligation_categories: Dict = None
        proof_goals: List = None

        def __post_init__(self):
            if self.failure_summary is None:
                self.failure_summary = {}
            if self.obligation_categories is None:
                self.obligation_categories = {}
            if self.proof_goals is None:
                self.proof_goals = []

    @dataclass
    class DependencyPreservation:
        dependency_graph: Dict = None
        critical_obligations: List = None
        propagation_chains: List = None

        def __post_init__(self):
            if self.dependency_graph is None:
                self.dependency_graph = {}
            if self.critical_obligations is None:
                self.critical_obligations = []
            if self.propagation_chains is None:
                self.propagation_chains = []

    @dataclass
    class StructuredFeedback:
        witness: WitnessInstantiation
        structure: LogicalStructure
        dependency: DependencyPreservation
        natural_language: str


class FeedbackCondition(Enum):
    """Four feedback richness conditions for ablation study"""
    FULL_STRUCTURED = "FullStructured"
    OBLIGATION_SLICE = "ObligationSlice"
    TAG_ONLY = "TagOnly"
    RAW_ERROR = "RawError"


class FeedbackAblator:
    """Filter feedback dimensions based on ablation condition"""

    def __init__(self, condition: FeedbackCondition):
        self.condition = condition

    def ablate_feedback(self, full_feedback: Optional[StructuredFeedback]) -> Optional[StructuredFeedback]:
        """
        Filter feedback dimensions based on condition.

        Args:
            full_feedback: Complete 3D feedback from base h-e1 code

        Returns:
            Filtered feedback matching ablation condition
        """
        if full_feedback is None:
            return None

        if self.condition == FeedbackCondition.RAW_ERROR:
            return self._create_raw_feedback(full_feedback)
        elif self.condition == FeedbackCondition.TAG_ONLY:
            return self._create_tag_only(full_feedback)
        elif self.condition == FeedbackCondition.OBLIGATION_SLICE:
            return self._create_obligation_slice(full_feedback)
        else:  # FULL_STRUCTURED
            return full_feedback

    def _create_raw_feedback(self, feedback: StructuredFeedback) -> StructuredFeedback:
        """Baseline: Only raw verifier output, no structured parsing"""
        empty_witness = WitnessInstantiation(
            counterexamples=[],
            input_states=[],
            trace_summaries=[]
        )

        empty_structure = LogicalStructure(
            failure_summary={},
            obligation_categories={},
            proof_goals=[]
        )

        empty_dependency = DependencyPreservation(
            dependency_graph={},
            critical_obligations=[],
            propagation_chains=[]
        )

        raw_text = f"Raw Frama-C output (unstructured)\nFailed obligations exist."

        return StructuredFeedback(
            witness=empty_witness,
            structure=empty_structure,
            dependency=empty_dependency,
            natural_language=raw_text
        )

    def _create_tag_only(self, feedback: StructuredFeedback) -> StructuredFeedback:
        """Dimension 2 only: Structure (obligation types)"""
        empty_witness = WitnessInstantiation(
            counterexamples=[],
            input_states=[],
            trace_summaries=[]
        )

        empty_dependency = DependencyPreservation(
            dependency_graph={},
            critical_obligations=[],
            propagation_chains=[]
        )

        nl_text = f"Obligation structure information:\n"
        if feedback.structure.failure_summary:
            nl_text += f"Failed obligation categories: {list(feedback.structure.failure_summary.keys())}\n"
        if feedback.structure.obligation_categories:
            nl_text += f"Obligation types: {list(feedback.structure.obligation_categories.keys())}"

        return StructuredFeedback(
            witness=empty_witness,
            structure=feedback.structure,
            dependency=empty_dependency,
            natural_language=nl_text
        )

    def _create_obligation_slice(self, feedback: StructuredFeedback) -> StructuredFeedback:
        """Dimensions 2+3: Structure + Dependency"""
        empty_witness = WitnessInstantiation(
            counterexamples=[],
            input_states=[],
            trace_summaries=[]
        )

        nl_text = f"Obligation structure and dependency information:\n"
        if feedback.structure.failure_summary:
            nl_text += f"Failed obligation categories: {list(feedback.structure.failure_summary.keys())}\n"
        if feedback.dependency.critical_obligations:
            nl_text += f"Critical obligations: {len(feedback.dependency.critical_obligations)}\n"
        if feedback.dependency.dependency_graph:
            nl_text += f"Dependency relationships: {len(feedback.dependency.dependency_graph)} nodes"

        return StructuredFeedback(
            witness=empty_witness,
            structure=feedback.structure,
            dependency=feedback.dependency,
            natural_language=nl_text
        )

    def get_condition_name(self) -> str:
        """Get human-readable condition name"""
        return self.condition.value
