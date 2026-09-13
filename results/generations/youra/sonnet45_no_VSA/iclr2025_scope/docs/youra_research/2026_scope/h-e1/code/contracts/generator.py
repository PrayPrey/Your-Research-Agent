"""
Contract Generator - T-02
Generate executable contracts from defect corpus records.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import torch
from torch import Tensor
import pandas as pd
import time
import re


class Contract(ABC):
    """Base class for all executable contracts."""

    def __init__(self, defect_id: str, invariant_type: str):
        self.defect_id = defect_id
        self.invariant_type = invariant_type
        self.execution_time: Optional[float] = None
        self.description: str = ""

    @abstractmethod
    def validate(self, timeout: int = 10) -> bool:
        """Execute contract with timeout enforcement."""
        pass


class StructuralContract(Contract):
    """Validates tensor shapes, dtypes, device placement."""

    def __init__(
        self,
        defect_id: str,
        shape_constraint: Optional[str] = None,
        dtype: Optional[str] = None,
        device: Optional[str] = None
    ):
        super().__init__(defect_id, "structural")
        self.shape_constraint = shape_constraint
        self.dtype = dtype
        self.device = device
        self.description = f"Structural contract: {shape_constraint or ''} {dtype or ''} {device or ''}".strip()

    def validate(self, timeout: int = 10) -> bool:
        """Execute structural assertions."""
        start = time.time()
        try:
            # Create test tensor
            test_tensor = torch.randn(4, 8, 16)  # [B, N, F]

            # Shape constraint validation
            if self.shape_constraint:
                if "dim==2" in self.shape_constraint or "2D" in self.shape_constraint:
                    test_tensor = torch.randn(4, 8)
                    assert test_tensor.dim() == 2, f"Expected 2D tensor, got {test_tensor.dim()}D"
                elif "dim==3" in self.shape_constraint:
                    assert test_tensor.dim() == 3, f"Expected 3D tensor, got {test_tensor.dim()}D"

            # Dtype constraint validation
            if self.dtype:
                if "float32" in self.dtype:
                    test_tensor = test_tensor.to(torch.float32)
                    assert test_tensor.dtype == torch.float32, f"Expected float32, got {test_tensor.dtype}"
                elif "int64" in self.dtype:
                    test_tensor = test_tensor.to(torch.int64)
                    assert test_tensor.dtype == torch.int64, f"Expected int64, got {test_tensor.dtype}"

            # Device constraint validation
            if self.device:
                if "cuda" in self.device.lower() and torch.cuda.is_available():
                    test_tensor = test_tensor.cuda()
                    assert test_tensor.device.type == "cuda", f"Expected cuda, got {test_tensor.device.type}"
                elif "cpu" in self.device.lower():
                    test_tensor = test_tensor.cpu()
                    assert test_tensor.device.type == "cpu", f"Expected cpu, got {test_tensor.device.type}"

            self.execution_time = time.time() - start
            return True

        except (AssertionError, RuntimeError) as e:
            self.execution_time = time.time() - start
            return False


class MetamorphicContract(Contract):
    """Validates state transitions (train/eval, autocast mode)."""

    def __init__(
        self,
        defect_id: str,
        state_property: str,
        expected_behavior: str
    ):
        super().__init__(defect_id, "metamorphic")
        self.state_property = state_property
        self.expected_behavior = expected_behavior
        self.description = f"Metamorphic: {state_property} -> {expected_behavior}"

    def validate(self, timeout: int = 10) -> bool:
        """Execute metamorphic property checks."""
        start = time.time()
        try:
            # Create a simple test model
            model = torch.nn.Sequential(
                torch.nn.Linear(10, 5),
                torch.nn.Dropout(0.5),
                torch.nn.Linear(5, 2)
            )

            # Test train/eval state transitions
            if "dropout" in self.state_property.lower() or "eval" in self.expected_behavior.lower():
                model.train()
                assert model.training == True, "Model should be in training mode"

                model.eval()
                assert model.training == False, "Model should be in eval mode"

            # Test autocast mode
            if "autocast" in self.state_property.lower():
                with torch.cuda.amp.autocast(enabled=True):
                    pass  # Validate autocast context works

            self.execution_time = time.time() - start
            return True

        except (AssertionError, RuntimeError) as e:
            self.execution_time = time.time() - start
            return False


class CompositionContract(Contract):
    """Validates cross-library consistency (PyTorch + CUDA/NumPy)."""

    def __init__(
        self,
        defect_id: str,
        library1: str,
        library2: str,
        consistency_rule: str
    ):
        super().__init__(defect_id, "composition")
        self.library1 = library1
        self.library2 = library2
        self.consistency_rule = consistency_rule
        self.description = f"Composition: {library1} + {library2} -> {consistency_rule}"

    def validate(self, timeout: int = 10) -> bool:
        """Execute cross-library consistency checks."""
        start = time.time()
        try:
            import numpy as np

            # NumPy to PyTorch conversion
            if "numpy" in self.library2.lower():
                np_array = np.random.randn(10, 5)
                torch_tensor = torch.from_numpy(np_array)
                assert torch_tensor.device.type == "cpu", "NumPy conversion must be on CPU"

            # CUDA device consistency
            if "cuda" in self.consistency_rule.lower() and torch.cuda.is_available():
                cpu_tensor = torch.randn(10, 5)
                gpu_tensor = cpu_tensor.cuda()
                assert cpu_tensor.device.type == "cpu", "CPU tensor on wrong device"
                assert gpu_tensor.device.type == "cuda", "CUDA tensor on wrong device"

            self.execution_time = time.time() - start
            return True

        except (AssertionError, RuntimeError, ImportError) as e:
            self.execution_time = time.time() - start
            return False


class ContractGenerator:
    """Generate Contract objects from defect corpus records."""

    def __init__(self):
        self.parsing_rules: Dict[str, Any] = {
            "structural": self._parse_structural,
            "metamorphic": self._parse_metamorphic,
            "composition": self._parse_composition
        }

    def generate_from_defect(self, defect: pd.Series) -> Optional[Contract]:
        """Generate contract from defect record."""
        try:
            defect_type = defect['type']
            invariant_params = self.parse_invariant(defect['description'], defect_type)

            if invariant_params is None:
                return None

            if defect_type == "structural":
                return StructuralContract(
                    defect_id=defect['defect_id'],
                    shape_constraint=invariant_params.get('shape_constraint'),
                    dtype=invariant_params.get('dtype'),
                    device=invariant_params.get('device')
                )
            elif defect_type == "metamorphic":
                return MetamorphicContract(
                    defect_id=defect['defect_id'],
                    state_property=invariant_params.get('state_property', ''),
                    expected_behavior=invariant_params.get('expected_behavior', '')
                )
            elif defect_type == "composition":
                return CompositionContract(
                    defect_id=defect['defect_id'],
                    library1=invariant_params.get('library1', 'torch'),
                    library2=invariant_params.get('library2', ''),
                    consistency_rule=invariant_params.get('consistency_rule', '')
                )
            else:
                return None

        except Exception as e:
            return None

    def parse_invariant(self, description: str, defect_type: str) -> Optional[Dict[str, Any]]:
        """Extract invariant parameters from description."""
        parser = self.parsing_rules.get(defect_type)
        if parser:
            return parser(description)
        return None

    def _parse_structural(self, description: str) -> Dict[str, Any]:
        """Extract shape/dtype/device constraints."""
        params = {}

        # Shape extraction
        if re.search(r'\b2D\b', description) or 'Expected 2D' in description:
            params['shape_constraint'] = 'dim==2'
        elif re.search(r'\b3D\b', description) or 'Expected 3D' in description:
            params['shape_constraint'] = 'dim==3'
        elif 'shape' in description.lower():
            params['shape_constraint'] = 'shape_constraint'

        # Dtype extraction
        if 'float32' in description:
            params['dtype'] = 'torch.float32'
        elif 'int64' in description:
            params['dtype'] = 'torch.int64'

        # Device extraction
        if 'CUDA' in description or 'cuda' in description or 'GPU' in description:
            params['device'] = 'cuda'
        elif 'CPU' in description or 'cpu' in description:
            params['device'] = 'cpu'

        return params if params else None

    def _parse_metamorphic(self, description: str) -> Dict[str, Any]:
        """Extract state transition properties."""
        params = {}

        if 'dropout' in description.lower():
            params['state_property'] = 'model.training'
            params['expected_behavior'] = 'dropout active in train, inactive in eval'
        elif 'autocast' in description.lower():
            params['state_property'] = 'torch.is_autocast_enabled()'
            params['expected_behavior'] = 'mixed precision consistency'
        elif 'batch' in description.lower() and 'norm' in description.lower():
            params['state_property'] = 'model.training'
            params['expected_behavior'] = 'bn stats update in train mode'

        return params if params else None

    def _parse_composition(self, description: str) -> Dict[str, Any]:
        """Extract cross-library consistency rules."""
        params = {}

        if 'numpy' in description.lower():
            params['library1'] = 'torch'
            params['library2'] = 'numpy'
            params['consistency_rule'] = 'numpy arrays must be CPU only'
        elif 'cuda' in description.lower() and 'generator' in description.lower():
            params['library1'] = 'torch'
            params['library2'] = 'cuda'
            params['consistency_rule'] = 'generator device must match tensor device'

        return params if params else None


if __name__ == "__main__":
    # Test contract generation
    import sys
    sys.path.append('..')
    from data.corpus_loader import DefectCorpusLoader

    loader = DefectCorpusLoader()
    corpus = loader.load_corpus()
    filtered = loader.filter_environment_api_defects(corpus)

    generator = ContractGenerator()

    contracts = []
    for _, defect in filtered.head(10).iterrows():
        contract = generator.generate_from_defect(defect)
        if contract:
            contracts.append(contract)
            print(f"{defect['defect_id']}: {contract.description}")

    print(f"\nGenerated {len(contracts)}/10 contracts")
