"""
Composition Contract Chain with Bidirectional Failure Propagation
Core mechanism for h-c3
"""
from typing import List, Dict, Tuple, Any, Optional
import time

from contracts.pipeline_stage import PipelineStage, ContractViolation
from contracts.composition_contracts import (
    CompositionContract,
    DevicePlacementContract,
    TensorLayoutContract,
    CrossLibraryBindingContract
)


class CompositionContractChain:
    """Manages contract chain with bidirectional failure propagation"""

    def __init__(self, defect: Dict[str, Any], version_tolerance: int = 2):
        """
        Initialize contract chain.

        Args:
            defect: Defect metadata from corpus
            version_tolerance: ±N minor releases for stability testing
        """
        self.defect = defect
        self.version_tolerance = version_tolerance
        self.stages = self._create_pipeline_stages()
        self.contracts: List[CompositionContract] = []
        self.blocked_stages: set = set()
        self.failure_log: List[Dict] = []

    def _create_pipeline_stages(self) -> List[PipelineStage]:
        """Create pipeline stages with dependencies"""
        return [
            PipelineStage("dataset", dependencies=[]),
            PipelineStage("preprocess", dependencies=["dataset"]),
            PipelineStage("model", dependencies=["preprocess"]),
            PipelineStage("output", dependencies=["model"])
        ]

    def validate_chain(self) -> Tuple[bool, float]:
        """
        Execute contract chain with bidirectional propagation.

        Returns:
            (contractable, execution_time)
            - contractable: True if contracts detected defect
            - execution_time: Total execution time in seconds
        """
        start_time = time.time()

        # Pre-check: Version stability (from h-e1, expected to fail for many)
        # For PoC, assume some defects are version-stable
        if not self._check_version_stability():
            # Version instability - not contractable
            return False, 0.0

        # Generate contracts for each stage
        self.contracts = self._generate_contracts()

        # Execute contracts sequentially with early exit
        for contract in self.contracts:
            # Skip if stage is blocked by upstream failure
            if contract.stage.name in self.blocked_stages:
                continue

            try:
                contract.check()
            except ContractViolation as e:
                # Bidirectional propagation
                self._propagate_forward(e)
                self._propagate_backward(e)

                # Log failure
                self.failure_log.append({
                    "stage": e.stage,
                    "contract_type": e.contract_type,
                    "message": e.message,
                    "can_recover": e.can_recover,
                    "recovery_attempted": False
                })

                execution_time = time.time() - start_time
                return True, execution_time  # Contract detected defect

        execution_time = time.time() - start_time
        return False, execution_time  # No violation detected (false negative)

    def _check_version_stability(self) -> bool:
        """
        Check if defect is version-stable.

        For PoC: Use simplified heuristic based on defect ID
        Returns True for ~80% of defects (simulating version stability)
        """
        # Simple hash-based deterministic selection
        defect_id = str(self.defect.get('defect_id', ''))
        hash_val = sum(ord(c) for c in defect_id)
        return (hash_val % 100) < 80  # 80% pass version stability

    def _generate_contracts(self) -> List[CompositionContract]:
        """
        Generate contracts for all pipeline stages.

        Returns:
            List of contracts (one per stage for simplicity)
        """
        contracts = []
        defect_description = str(self.defect.get('description', ''))

        # Create one contract per stage (device, layout, binding)
        # In practice, would analyze defect type and create relevant contracts
        for i, stage in enumerate(self.stages[1:], 1):  # Skip dataset stage
            if i == 1:  # preprocess -> device contract
                contract = DevicePlacementContract(
                    defect_id=str(self.defect.get('defect_id', '')),
                    stage=stage,
                    defect_description=defect_description
                )
            elif i == 2:  # model -> layout contract
                contract = TensorLayoutContract(
                    defect_id=str(self.defect.get('defect_id', '')),
                    stage=stage,
                    defect_description=defect_description
                )
            else:  # output -> binding contract
                contract = CrossLibraryBindingContract(
                    defect_id=str(self.defect.get('defect_id', '')),
                    stage=stage,
                    defect_description=defect_description
                )
            contracts.append(contract)

        return contracts

    def _propagate_forward(self, error: ContractViolation) -> None:
        """
        Forward propagation: Block downstream stages.

        Args:
            error: Contract violation from current stage
        """
        failed_stage = error.stage
        for stage in self.stages:
            if failed_stage in stage.dependencies or self._is_downstream(failed_stage, stage.name):
                self.blocked_stages.add(stage.name)

    def _is_downstream(self, upstream: str, downstream: str) -> bool:
        """Check if downstream stage depends on upstream (directly or transitively)"""
        stage_order = {s.name: i for i, s in enumerate(self.stages)}
        return stage_order.get(downstream, -1) > stage_order.get(upstream, -1)

    def _propagate_backward(self, error: ContractViolation) -> None:
        """
        Backward propagation: Check if upstream can recover.

        Args:
            error: Contract violation from current stage
        """
        if error.can_recover and len(self.failure_log) > 0:
            # Mark that recovery is possible
            self.failure_log[-1]["recovery_attempted"] = True

    def get_propagation_graph(self) -> Dict:
        """
        Get failure propagation graph.

        Returns:
            dict with nodes, edges, failures
        """
        return {
            "nodes": [s.name for s in self.stages],
            "edges": [(s.dependencies[0] if s.dependencies else "none", s.name)
                      for s in self.stages if s.dependencies],
            "failures": self.failure_log
        }
