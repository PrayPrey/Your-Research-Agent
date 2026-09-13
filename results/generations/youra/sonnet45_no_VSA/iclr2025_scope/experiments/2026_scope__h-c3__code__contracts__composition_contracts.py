"""
Composition Contract Types for h-c3
Implements device placement, tensor layout, and cross-library binding contracts
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
import re

from contracts.pipeline_stage import PipelineStage, ContractViolation

class CompositionContract(ABC):
    """Base class for composition-level contracts"""

    def __init__(self, defect_id: str, stage: PipelineStage):
        self.defect_id = defect_id
        self.stage = stage
        self.execution_time: Optional[float] = None

    @abstractmethod
    def check(self) -> None:
        """Execute contract validation. Raises ContractViolation if fails."""
        pass


class DevicePlacementContract(CompositionContract):
    """Validates GPU/CPU consistency across pipeline stages"""

    def __init__(
        self,
        defect_id: str,
        stage: PipelineStage,
        defect_description: str
    ):
        super().__init__(defect_id, stage)
        self.defect_description = defect_description

    def check(self) -> None:
        """
        Validate device placement consistency.

        For PoC: Pattern match device-related keywords in defect description
        """
        device_keywords = [
            'cuda', 'gpu', 'cpu', 'device', 'mps',
            'device mismatch', 'expected.*device',
            'generator.*device', 'tensor.*device'
        ]

        description_lower = self.defect_description.lower()

        for keyword in device_keywords:
            if re.search(keyword, description_lower):
                # Device-related defect detected
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="device_placement",
                    message=f"Device-related defect detected: {keyword}",
                    can_recover=True  # Device placement often recoverable via .to()
                )


class TensorLayoutContract(CompositionContract):
    """Validates shape/dtype consistency across library boundaries"""

    def __init__(
        self,
        defect_id: str,
        stage: PipelineStage,
        defect_description: str
    ):
        super().__init__(defect_id, stage)
        self.defect_description = defect_description

    def check(self) -> None:
        """
        Validate tensor layout consistency.

        For PoC: Pattern match shape/dtype keywords in defect description
        """
        layout_keywords = [
            'shape', 'dtype', 'dimension', 'size',
            'shape mismatch', 'dimension.*mismatch',
            'tensor.*layout', 'float16', 'float32',
            'batch.*size', 'sequence.*length'
        ]

        description_lower = self.defect_description.lower()

        for keyword in layout_keywords:
            if re.search(keyword, description_lower):
                # Layout-related defect detected
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="tensor_layout",
                    message=f"Tensor layout defect detected: {keyword}",
                    can_recover=True  # Some dtype issues recoverable
                )


class CrossLibraryBindingContract(CompositionContract):
    """Validates API compatibility across library version triads"""

    def __init__(
        self,
        defect_id: str,
        stage: PipelineStage,
        defect_description: str
    ):
        super().__init__(defect_id, stage)
        self.defect_description = defect_description

    def check(self) -> None:
        """
        Validate cross-library API compatibility.

        For PoC: Pattern match version/API keywords in defect description
        """
        binding_keywords = [
            'version', 'api', 'compatibility', 'import',
            'transformers', 'torch', 'pytorch',
            'breaking.*change', 'deprecated',
            'method.*not.*found', 'attribute.*error'
        ]

        description_lower = self.defect_description.lower()

        for keyword in binding_keywords:
            if re.search(keyword, description_lower):
                # Binding-related defect detected
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="cross_library_binding",
                    message=f"Cross-library binding defect detected: {keyword}",
                    can_recover=False  # API changes usually not recoverable
                )
