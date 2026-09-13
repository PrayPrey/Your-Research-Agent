# API Logic Design: h-c3
# Composition Contract Chain with Bidirectional Failure Propagation

**Date:** 2026-07-11  
**Hypothesis:** h-c3 (MECHANISM - COMPOSITION)  
**Type:** PoC - Bidirectional Failure Propagation for Composition Contracts  
**Critical Context:** h-e1 showed 0% contractability for composition defects (version instability)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending h-e1 contract validation framework  
**Base Hypothesis:** docs/youra_research/h-e1/  
**Relevant Symbols:** Contract base class, ValidationResult, retrospective_coder patterns  
**Note:** Serena MCP unavailable (no active project). API signatures designed from h-e1 spec review.

**Rationale:** This experiment extends h-e1's contract framework to handle composition-level defects with novel bidirectional failure propagation. Reuses h-e1's Contract base class and retrospective coding methodology.

---

## Knowledge Base Patterns Applied

**Applied:** PyTorch device placement validation (tensor.device.type assertions)  
**Applied:** Cross-library tensor layout validation (shape/dtype consistency checks)  
**Applied:** Version tolerance testing (±2 minor release compatibility matrix)

---

## C-1: Composition Contract Chain Framework [Complexity: 12, Budget: 4]

### API Signatures

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Literal
from abc import ABC, abstractmethod
import time
import torch
from torch import Tensor

@dataclass
class PipelineStage:
    """Represents a stage in ML pipeline."""
    name: Literal["dataset", "preprocess", "model", "output"]
    dependencies: List[str]  # Names of upstream stages

@dataclass
class ContractViolation(Exception):
    """Raised when contract validation fails."""
    stage: str
    contract_type: str
    message: str
    can_recover: bool = False  # For backward propagation

class CompositionContract(ABC):
    """Base class for composition-level contracts."""
    
    def __init__(self, defect_id: str, stage: PipelineStage):
        """
        Initialize composition contract.
        
        Args:
            defect_id: Unique identifier from Jiang corpus
            stage: Pipeline stage this contract validates
        """
        self.defect_id = defect_id
        self.stage = stage
        self.execution_time: Optional[float] = None
    
    @abstractmethod
    def check(self) -> None:
        """Execute contract validation. Raises ContractViolation if fails."""
        pass

class CompositionContractChain:
    """Manages contract chain with bidirectional failure propagation."""
    
    def __init__(
        self,
        defect: Dict[str, Any],
        version_tolerance: int = 2
    ):
        """
        Initialize contract chain.
        
        Args:
            defect: Defect metadata from corpus (lib_versions, failure_type)
            version_tolerance: ±N minor releases for stability testing
        """
        self.defect = defect
        self.version_tolerance = version_tolerance
        self.stages = self._create_pipeline_stages()
        self.contracts: List[CompositionContract] = []
        self.blocked_stages: set = set()
        self.failure_log: List[Dict] = []
    
    def _create_pipeline_stages(self) -> List[PipelineStage]:
        """Create pipeline stages. Returns: [dataset, preprocess, model, output]"""
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
        
        Process:
            1. Check version stability (pre-filter)
            2. Generate contracts for each stage
            3. Execute contracts with early exit
            4. Propagate failures bidirectionally
        """
        start_time = time.time()
        
        # Pre-check: Version stability (from h-e1, expected to fail)
        if not self._check_version_stability():
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
                    "can_recover": e.can_recover
                })
                
                execution_time = time.time() - start_time
                return True, execution_time  # Contract detected defect
        
        execution_time = time.time() - start_time
        return False, execution_time  # No violation detected (false negative)
    
    def _check_version_stability(self) -> bool:
        """
        Check if defect is version-stable.
        
        Returns:
            True if contracts work across ±version_tolerance minor releases
        
        Implementation:
            - Parse lib versions from defect metadata
            - Generate version matrix (±2 minor releases)
            - Test if defect reproduces in all versions
        """
        pass
    
    def _generate_contracts(self) -> List[CompositionContract]:
        """
        Generate contracts for all pipeline stages.
        
        Returns:
            List of contracts: [device, layout, binding] per stage
        """
        pass
    
    def _propagate_forward(self, error: ContractViolation) -> None:
        """
        Forward propagation: Block downstream stages.
        
        Args:
            error: Contract violation from current stage
        
        Logic:
            1. Find all stages dependent on failed stage
            2. Mark them as blocked
            3. Prevents execution of downstream contracts
        """
        failed_stage = error.stage
        for stage in self.stages:
            if failed_stage in stage.dependencies:
                self.blocked_stages.add(stage.name)
    
    def _propagate_backward(self, error: ContractViolation) -> None:
        """
        Backward propagation: Check if upstream can recover.
        
        Args:
            error: Contract violation from current stage
        
        Logic:
            1. Check error.can_recover flag
            2. If recoverable, attempt upstream contract relaxation
            3. Re-execute upstream contracts with relaxed constraints
        
        Note: Minimal implementation for PoC (just check recovery flag)
        """
        if error.can_recover:
            # Mark that recovery is possible (for metrics)
            self.failure_log[-1]["recovery_attempted"] = True
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | PipelineStage dataclass | Define stage structure with dependencies |
| C-1-2 | CompositionContract base | Abstract base class for contracts |
| C-1-3 | CompositionContractChain | Chain orchestrator with validation logic |
| C-1-4 | Propagation methods | Forward/backward propagation logic |

---

## C-2: Device Placement Contract [Complexity: 8, Budget: 2]

### API Signatures

```python
class DevicePlacementContract(CompositionContract):
    """Validates GPU/CPU consistency across pipeline stages."""
    
    def __init__(
        self,
        defect_id: str,
        stage: PipelineStage,
        expected_device: str,  # "cuda" or "cpu"
        cross_library_binding: Dict[str, str]  # {library_name: device_method}
    ):
        """
        Initialize device placement contract.
        
        Args:
            defect_id: Unique identifier
            stage: Pipeline stage to validate
            expected_device: Expected device type
            cross_library_binding: Methods to check device in each library
                e.g., {"torch": "tensor.device.type", 
                       "transformers": "model.device"}
        """
        super().__init__(defect_id, stage)
        self.expected_device = expected_device
        self.cross_library_binding = cross_library_binding
    
    def check(self) -> None:
        """
        Validate device placement across libraries.
        
        Raises:
            ContractViolation: If device mismatch detected
        
        Validation logic:
            1. For each library in cross_library_binding:
                a. Execute device check method
                b. Assert device == expected_device
            2. Example: tensor.device.type == "cuda"
        
        Example violation:
            Expected 'cuda' device but found 'cpu' in PyTorch tensor
            while Transformers model is on 'cuda' -> Cross-library mismatch
        """
        # Pseudo-implementation
        for lib, device_method in self.cross_library_binding.items():
            actual_device = self._get_device(lib, device_method)
            if actual_device != self.expected_device:
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="device_placement",
                    message=f"Expected '{self.expected_device}' but found '{actual_device}' in {lib}",
                    can_recover=True  # Device placement can often be recovered via .to()
                )
    
    def _get_device(self, library: str, method: str) -> str:
        """Execute device check method. Returns: device type string."""
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tensor | [B, N, F] | Example tensor to check device |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | DevicePlacementContract | Contract implementation |
| C-2-2 | Device check methods | Library-specific device extraction |

---

## C-3: Tensor Layout Contract [Complexity: 10, Budget: 3]

### API Signatures

```python
from typing import Tuple

class TensorLayoutContract(CompositionContract):
    """Validates shape/dtype consistency across library boundaries."""
    
    def __init__(
        self,
        defect_id: str,
        stage: PipelineStage,
        expected_shape: Tuple[int, ...],  # e.g., (batch_size, seq_len, hidden_dim)
        expected_dtype: str,  # e.g., "torch.float32"
        cross_library_tensors: Dict[str, str]  # {library: tensor_accessor}
    ):
        """
        Initialize tensor layout contract.
        
        Args:
            defect_id: Unique identifier
            stage: Pipeline stage to validate
            expected_shape: Expected tensor shape (use -1 for dynamic dims)
            expected_dtype: Expected data type
            cross_library_tensors: Tensor accessors for each library
                e.g., {"torch": "output", "transformers": "model.output.last_hidden_state"}
        """
        super().__init__(defect_id, stage)
        self.expected_shape = expected_shape
        self.expected_dtype = expected_dtype
        self.cross_library_tensors = cross_library_tensors
    
    def check(self) -> None:
        """
        Validate tensor layout consistency.
        
        Raises:
            ContractViolation: If shape/dtype mismatch detected
        
        Validation logic:
            1. For each library tensor:
                a. Check shape matches expected_shape (allowing -1 for dynamic)
                b. Check dtype matches expected_dtype
            2. Check cross-library consistency (all tensors compatible)
        
        Example violation:
            PyTorch tensor: [32, 512, 768] dtype=float32
            Transformers output: [32, 512, 384] dtype=float16
            -> Shape mismatch at dim 2
        """
        reference_shape = None
        reference_dtype = None
        
        for lib, tensor_accessor in self.cross_library_tensors.items():
            tensor = self._get_tensor(lib, tensor_accessor)
            
            # Check shape
            if not self._shape_matches(tensor.shape, self.expected_shape):
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="tensor_layout",
                    message=f"Shape mismatch in {lib}: expected {self.expected_shape}, got {tensor.shape}",
                    can_recover=False  # Shape mismatches usually require code changes
                )
            
            # Check dtype
            if str(tensor.dtype) != self.expected_dtype:
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="tensor_layout",
                    message=f"Dtype mismatch in {lib}: expected {self.expected_dtype}, got {tensor.dtype}",
                    can_recover=True  # Dtype can be converted via .to()
                )
            
            # Check cross-library consistency
            if reference_shape is None:
                reference_shape = tensor.shape
                reference_dtype = tensor.dtype
            elif tensor.shape != reference_shape or tensor.dtype != reference_dtype:
                raise ContractViolation(
                    stage=self.stage.name,
                    contract_type="tensor_layout",
                    message=f"Cross-library inconsistency: {lib} tensor incompatible",
                    can_recover=False
                )
    
    def _shape_matches(self, actual: Tuple[int, ...], expected: Tuple[int, ...]) -> bool:
        """
        Check if shapes match (allowing -1 for dynamic dims).
        
        Returns:
            True if shapes compatible
        """
        if len(actual) != len(expected):
            return False
        return all(e == -1 or a == e for a, e in zip(actual, expected))
    
    def _get_tensor(self, library: str, accessor: str) -> Tensor:
        """Execute tensor accessor. Returns: tensor object."""
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| expected_shape | (B, N, F) or (-1, N, F) | -1 for dynamic dims |
| actual | (B', N', F') | From library tensor |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | TensorLayoutContract | Contract implementation |
| C-3-2 | Shape matching logic | Dynamic dimension support |
| C-3-3 | Cross-library consistency | Compare tensors across libraries |

---

## C-4: Cross-Library Binding Contract [Complexity: 14, Budget: 4]

### API Signatures

```python
from typing import Any

class CrossLibraryBindingContract(CompositionContract):
    """Validates API compatibility across library version triads."""
    
    def __init__(
        self,
        defect_id: str,
        stage: PipelineStage,
        api_signature: Dict[str, Any],  # Expected method signature
        version_triad: Dict[str, str]  # {library: version}
    ):
        """
        Initialize cross-library binding contract.
        
        Args:
            defect_id: Unique identifier
            stage: Pipeline stage to validate
            api_signature: Expected API (method, params, return_type)
                e.g., {"method": "model.forward", 
                       "params": {"input_ids": "Tensor", "attention_mask": "Optional[Tensor]"},
                       "return_type": "Tensor"}
            version_triad: Library versions
                e.g., {"pytorch": "1.9.0", "transformers": "4.12.0", "cuda": "11.1"}
        """
        super().__init__(defect_id, stage)
        self.api_signature = api_signature
        self.version_triad = version_triad
    
    def check(self) -> None:
        """
        Validate API compatibility across versions.
        
        Raises:
            ContractViolation: If API breaking change detected
        
        Validation logic:
            1. For each library in version_triad:
                a. Check method exists
                b. Check parameter types match
                c. Check return type matches
            2. Test actual API call with mock inputs
        
        Example violation:
            PyTorch 1.9.0 + Transformers 4.12.0:
            model.forward(input_ids, attention_mask) exists
            
            PyTorch 1.10.0 + Transformers 4.12.0:
            model.forward() signature changed, attention_mask param removed
            -> API breaking change across versions
        """
        method_name = self.api_signature["method"]
        expected_params = self.api_signature["params"]
        
        # Check method exists
        if not self._method_exists(method_name):
            raise ContractViolation(
                stage=self.stage.name,
                contract_type="cross_library_binding",
                message=f"Method {method_name} not found in version {self.version_triad}",
                can_recover=False
            )
        
        # Check parameter compatibility
        actual_params = self._get_method_params(method_name)
        if not self._params_compatible(actual_params, expected_params):
            raise ContractViolation(
                stage=self.stage.name,
                contract_type="cross_library_binding",
                message=f"Parameter mismatch for {method_name}: expected {expected_params}, got {actual_params}",
                can_recover=False
            )
        
        # Test actual API call
        try:
            self._test_api_call(method_name)
        except Exception as e:
            raise ContractViolation(
                stage=self.stage.name,
                contract_type="cross_library_binding",
                message=f"API call failed: {str(e)}",
                can_recover=False
            )
    
    def _method_exists(self, method_name: str) -> bool:
        """Check if method exists in current versions."""
        pass
    
    def _get_method_params(self, method_name: str) -> Dict[str, str]:
        """Extract method parameters via introspection."""
        pass
    
    def _params_compatible(self, actual: Dict, expected: Dict) -> bool:
        """Check parameter compatibility."""
        return set(expected.keys()).issubset(set(actual.keys()))
    
    def _test_api_call(self, method_name: str) -> None:
        """Execute actual API call with mock inputs."""
        pass
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | CrossLibraryBindingContract | Contract implementation |
| C-4-2 | API introspection | Method/param extraction |
| C-4-3 | Compatibility checker | Parameter matching logic |
| C-4-4 | Mock API execution | Test actual calls |

---

## C-5: Version Stability Testing [Complexity: 12, Budget: 3]

### API Signatures

```python
from itertools import product

class VersionStabilityTester:
    """Tests contract stability across ±N minor library releases."""
    
    def __init__(self, base_versions: Dict[str, str], tolerance: int = 2):
        """
        Initialize version stability tester.
        
        Args:
            base_versions: Base library versions from defect
                e.g., {"pytorch": "1.9.0", "transformers": "4.12.0"}
            tolerance: ±N minor releases to test
        """
        self.base_versions = base_versions
        self.tolerance = tolerance
        self.version_matrix: List[Dict[str, str]] = []
    
    def generate_version_matrix(self) -> List[Dict[str, str]]:
        """
        Generate version combinations to test.
        
        Returns:
            List of version triads
            e.g., [{"pytorch": "1.9.0", "transformers": "4.12.0"},
                   {"pytorch": "1.10.0", "transformers": "4.12.0"},
                   ...]
        
        Logic:
            1. For each library, generate ±tolerance minor versions
            2. Cartesian product of all version ranges
            3. Filter invalid combinations (e.g., CUDA incompatibility)
        """
        version_ranges = {}
        for lib, version in self.base_versions.items():
            version_ranges[lib] = self._generate_version_range(version)
        
        # Cartesian product
        combinations = product(*version_ranges.values())
        self.version_matrix = [
            dict(zip(version_ranges.keys(), combo))
            for combo in combinations
        ]
        return self.version_matrix
    
    def _generate_version_range(self, base_version: str) -> List[str]:
        """
        Generate ±tolerance minor versions.
        
        Args:
            base_version: e.g., "1.9.0"
        
        Returns:
            List of versions: ["1.7.0", "1.8.0", "1.9.0", "1.10.0", "1.11.0"]
        """
        major, minor, patch = base_version.split('.')
        versions = []
        for i in range(-self.tolerance, self.tolerance + 1):
            new_minor = int(minor) + i
            if new_minor >= 0:  # No negative versions
                versions.append(f"{major}.{new_minor}.{patch}")
        return versions
    
    def test_stability(self, contract_chain: CompositionContractChain) -> float:
        """
        Test contract across all version combinations.
        
        Args:
            contract_chain: Contract chain to test
        
        Returns:
            Stability rate: (stable_versions / total_versions) × 100%
        
        Logic:
            1. For each version combination:
                a. Create contract chain with that version triad
                b. Execute validate_chain()
                c. Record if contractable
            2. Calculate stability rate
        """
        stable_count = 0
        total_count = len(self.version_matrix)
        
        for version_triad in self.version_matrix:
            # Create contract chain for this version
            chain = CompositionContractChain(
                defect={**contract_chain.defect, "lib_versions": version_triad},
                version_tolerance=0  # Don't recurse version testing
            )
            
            # Test if contract works in this version
            contractable, _ = chain.validate_chain()
            if contractable:
                stable_count += 1
        
        stability_rate = (stable_count / total_count) * 100.0
        return stability_rate
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | VersionStabilityTester | Tester implementation |
| C-5-2 | Version matrix generation | Cartesian product logic |
| C-5-3 | Stability calculation | Execute contracts across versions |

---

## C-6: Metrics and Evaluation [Complexity: 6, Budget: 2]

### API Signatures

```python
from dataclasses import dataclass

@dataclass
class CompositionMetrics:
    """Results container for composition contract evaluation."""
    detection_rate: float  # (contractable / 62) × 100%
    mean_execution_time: float  # Mean contract execution time (seconds)
    max_execution_time: float  # Max contract execution time (seconds)
    version_stability_rate: float  # % contracts stable across versions
    false_positive_rate: float  # % false positives on known-good code
    contractable_by_type: Dict[str, int]  # {contract_type: count}

class MetricsCalculator:
    """Calculates evaluation metrics for composition contracts."""
    
    def __init__(self, results: List[Tuple[bool, float]]):
        """
        Initialize metrics calculator.
        
        Args:
            results: List of (contractable, execution_time) from each defect
        """
        self.results = results
    
    def calculate_detection_rate(self) -> float:
        """
        Calculate detection rate.
        
        Returns:
            (contractable_count / 62) × 100%
        """
        contractable_count = sum(1 for contractable, _ in self.results if contractable)
        return (contractable_count / 62) * 100.0
    
    def calculate_execution_times(self) -> Tuple[float, float]:
        """
        Calculate mean and max execution times.
        
        Returns:
            (mean_time, max_time) in seconds
        """
        times = [t for _, t in self.results]
        return sum(times) / len(times), max(times)
    
    def calculate_metrics(
        self,
        stability_results: Dict[str, float],
        false_positive_count: int,
        total_validation_samples: int
    ) -> CompositionMetrics:
        """
        Calculate all metrics.
        
        Args:
            stability_results: Version stability rates by contract type
            false_positive_count: Number of false positives
            total_validation_samples: Total known-good samples tested
        
        Returns:
            CompositionMetrics object
        """
        detection_rate = self.calculate_detection_rate()
        mean_time, max_time = self.calculate_execution_times()
        
        # Version stability (average across contract types)
        version_stability = sum(stability_results.values()) / len(stability_results)
        
        # False positive rate
        fp_rate = (false_positive_count / total_validation_samples) * 100.0
        
        # Contractable by type
        contractable_by_type = self._count_by_type()
        
        return CompositionMetrics(
            detection_rate=detection_rate,
            mean_execution_time=mean_time,
            max_execution_time=max_time,
            version_stability_rate=version_stability,
            false_positive_rate=fp_rate,
            contractable_by_type=contractable_by_type
        )
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count contractable defects by contract type."""
        # Requires contract type annotation in results
        return {
            "device_placement": 0,
            "tensor_layout": 0,
            "cross_library_binding": 0
        }
```

### Metrics Formulas

**Detection Rate:**
```
detection_rate = (contractable_count / 62) × 100%
Target: ≥60% (SHOULD_WORK gate)
Baseline: 0% (from h-e1)
```

**Version Stability Rate:**
```
stability_rate = (stable_versions / total_versions) × 100%
Where total_versions = (2 × tolerance + 1)^num_libraries
Target: ≥80%
```

**False Positive Rate:**
```
fp_rate = (false_positive_count / total_validation_samples) × 100%
Target: <5%
```

**Execution Time:**
```
mean_time = sum(execution_times) / num_defects
Constraint: max_time ≤10 seconds
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | MetricsCalculator | Metrics calculation logic |
| C-6-2 | CompositionMetrics dataclass | Results container |

---

## External Dependencies (h-e1 Base Hypothesis)

### API Signatures (From h-e1 Specification)

The following APIs are referenced from h-e1 contract validation framework:

```python
# From: docs/youra_research/h-e1/code/contracts/validator.py (SPEC REVIEW)
from abc import ABC, abstractmethod

class Contract(ABC):
    """Base class for all executable contracts (from h-e1)."""
    
    def __init__(self, defect_id: str, invariant_type: str):
        """Initialize contract. invariant_type: "structural" | "metamorphic" | "composition" """
        self.defect_id = defect_id
        self.invariant_type = invariant_type
        self.execution_time: Optional[float] = None
    
    @abstractmethod
    def validate(self, timeout: int = 10) -> bool:
        """Execute contract with timeout enforcement. Returns True if passes."""
        pass

# From: docs/youra_research/h-e1/code/analysis/retrospective_coder.py (SPEC REVIEW)
class RetrospectiveCoder:
    """Retrospective defect analysis (from h-e1)."""
    
    def analyze_defect(
        self,
        defect: Dict[str, Any],
        contract_type: str
    ) -> Tuple[bool, float]:
        """
        Analyze defect contractability.
        
        Args:
            defect: Defect metadata from corpus
            contract_type: Type of contract to apply
        
        Returns:
            (contractable, execution_time)
        """
        pass

# From: docs/youra_research/h-e1/code/data/corpus_loader.py (SPEC REVIEW)
class DefectCorpusLoader:
    """Loads Jiang corpus defects (from h-e1)."""
    
    def load_composition_defects(self) -> List[Dict[str, Any]]:
        """
        Load 62 composition-level defects.
        
        Returns:
            List of defect metadata dicts
            Assert: len(result) == 62
        """
        pass
```

**Note:** h-c3 extends h-e1's Contract base class with CompositionContract and adds novel bidirectional propagation logic. Reuses h-e1's retrospective coding methodology and corpus loader.

---

## Summary

**Total Budget:** 18 subtasks allocated  
**Total Used:** 18 subtasks

| Task | Complexity | Budget | Description |
|------|------------|--------|-------------|
| C-1 | 12 | 4 | Composition contract chain framework |
| C-2 | 8 | 2 | Device placement contract |
| C-3 | 10 | 3 | Tensor layout contract |
| C-4 | 14 | 4 | Cross-library binding contract |
| C-5 | 12 | 3 | Version stability testing |
| C-6 | 6 | 2 | Metrics and evaluation |

**Critical Implementation Notes:**
1. **Version Stability Pre-filter:** Expected to fail (0% baseline from h-e1)
2. **Bidirectional Propagation:** Novel contribution; forward blocks downstream, backward checks recovery
3. **Execution Time:** ≤10s constraint per contract (from h-m2)
4. **Early Exit:** Stop on first contract violation (optimize for detection)
5. **Recovery Flag:** Simple boolean for PoC; future work: actual recovery logic

**Phase 4 Coder Dependencies:**
- h-e1 Contract base class (reuse)
- h-e1 DefectCorpusLoader (reuse)
- h-e1 RetrospectiveCoder pattern (extend)
- Jiang corpus: docs/youra_research/h-e1/data/defect_corpus.csv

---

*Generated by Phase 3 Logic Agent (Step 03)*  
*References: h-c3 PRD, h-e1 logic specification*
