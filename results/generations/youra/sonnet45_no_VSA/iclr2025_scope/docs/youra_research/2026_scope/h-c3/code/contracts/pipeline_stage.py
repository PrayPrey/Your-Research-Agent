"""
Pipeline Stage Module for h-c3
Defines ML pipeline stage structure
"""
from dataclasses import dataclass
from typing import Literal, List

@dataclass
class PipelineStage:
    """Represents a stage in ML pipeline"""
    name: Literal["dataset", "preprocess", "model", "output"]
    dependencies: List[str]  # Names of upstream stages

    def is_dependent_on(self, stage_name: str) -> bool:
        """Check if this stage depends on another stage"""
        return stage_name in self.dependencies

@dataclass
class ContractViolation(Exception):
    """Raised when contract validation fails"""
    stage: str
    contract_type: str
    message: str
    can_recover: bool = False  # For backward propagation
