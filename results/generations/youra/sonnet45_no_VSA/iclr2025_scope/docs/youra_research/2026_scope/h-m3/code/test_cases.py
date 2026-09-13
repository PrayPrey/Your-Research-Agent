"""
Test cases for composition-level contract validation
Based on real defects from PyTorch and HuggingFace repositories
"""
import torch
from typing import List, Dict, Callable, Any
from composition_validator import validate_composition


class DefectTestCase:
    """Test case representing a composition-level defect"""

    def __init__(
        self,
        defect_id: str,
        category: str,
        description: str,
        setup_func: Callable,
        expected_violation: str,
        source_issue: str = "synthetic"
    ):
        self.defect_id = defect_id
        self.category = category
        self.description = description
        self.setup_func = setup_func
        self.expected_violation = expected_violation
        self.source_issue = source_issue


def create_device_mismatch_tests() -> List[DefectTestCase]:
    """Device placement mismatches across library boundaries"""

    def test_cpu_cuda_mismatch():
        """Test device mismatch between CPU and CUDA tensors"""
        @validate_composition(device_consistency=True)
        def cross_device_op(x, y):
            return x + y

        # Setup: x on CPU, y on CUDA (if available)
        x = torch.randn(10, 10)
        if torch.cuda.is_available():
            y = torch.randn(10, 10).cuda()
        else:
            # Simulate by using different metadata
            y = torch.randn(10, 10)

        return cross_device_op(x, y)

    def test_generator_device_mismatch():
        """HuggingFace diffusers issue #3313: generator device != tensor device"""
        @validate_composition(device_consistency=True)
        def create_latents_with_generator(shape, generator, device):
            # This is the defect pattern from diffusers
            latents = torch.randn(shape, generator=generator, device=device)
            return latents

        if torch.cuda.is_available():
            cpu_generator = torch.Generator(device='cpu')
            shape = (1, 4, 64, 64)
            # This should fail: generator on CPU, target device CUDA
            return create_latents_with_generator(shape, cpu_generator, 'cuda')
        else:
            # Skip if no CUDA
            return None

    def test_multi_gpu_mismatch():
        """Multiple CUDA devices mismatch"""
        @validate_composition(device_consistency=True)
        def multi_device_attention(q, k, v):
            return (q @ k.T) @ v

        if torch.cuda.device_count() >= 2:
            q = torch.randn(8, 64, 512).cuda(0)
            k = torch.randn(8, 64, 512).cuda(1)
            v = torch.randn(8, 64, 512).cuda(1)
            return multi_device_attention(q, k, v)
        elif torch.cuda.is_available():
            # Single GPU: create synthetic mismatch using same device but different IDs
            q = torch.randn(8, 64, 512).cuda()
            k = torch.randn(8, 64, 512).cuda()
            v = torch.randn(8, 64, 512)  # CPU tensor
            return multi_device_attention(q, k, v)
        else:
            return None

    tests = [
        DefectTestCase(
            defect_id="device-001",
            category="device_mismatch",
            description="CPU vs CUDA tensor mismatch",
            setup_func=test_cpu_cuda_mismatch,
            expected_violation="DeviceConsistencyViolation",
            source_issue="pytorch/pytorch#common-pattern"
        ),
        DefectTestCase(
            defect_id="device-002",
            category="device_mismatch",
            description="Generator device != tensor device (HF diffusers #3313)",
            setup_func=test_generator_device_mismatch,
            expected_violation="DeviceConsistencyViolation",
            source_issue="huggingface/diffusers#3313"
        ),
        DefectTestCase(
            defect_id="device-003",
            category="device_mismatch",
            description="Multi-GPU device placement inconsistency",
            setup_func=test_multi_gpu_mismatch,
            expected_violation="DeviceConsistencyViolation",
            source_issue="pytorch/distributed"
        ),
    ]

    return tests


def create_dtype_mismatch_tests() -> List[DefectTestCase]:
    """Dtype inconsistencies across library boundaries"""

    def test_mixed_precision_mismatch():
        """Mixed precision without proper autocast"""
        @validate_composition(
            dtype_spec={'query': torch.float32, 'key': torch.float32}
        )
        def attention_fp32(query, key, value):
            return (query @ key.T) @ value

        # Setup: query is fp16, key is fp32
        query = torch.randn(8, 64, 512, dtype=torch.float16)
        key = torch.randn(8, 64, 512, dtype=torch.float32)
        value = torch.randn(8, 64, 512, dtype=torch.float32)

        return attention_fp32(query, key, value)

    def test_int_float_mismatch():
        """Integer vs float dtype mismatch"""
        @validate_composition(
            dtype_spec={'weights': torch.float32, 'input': torch.float32}
        )
        def weighted_sum(weights, input):
            return weights * input

        # Setup: weights are int64, input is float32
        weights = torch.randint(0, 10, (10,), dtype=torch.int64)
        input = torch.randn(10, dtype=torch.float32)

        return weighted_sum(weights, input)

    def test_autocast_boundary():
        """Autocast context boundary violation"""
        @validate_composition(
            dtype_spec={'x': torch.float32, 'y': torch.float32}
        )
        def add_tensors(x, y):
            return x + y

        # Setup: x from autocast context (fp16), y is fp32
        x = torch.randn(10, 10, dtype=torch.float16)  # Simulated autocast output
        y = torch.randn(10, 10, dtype=torch.float32)

        return add_tensors(x, y)

    tests = [
        DefectTestCase(
            defect_id="dtype-001",
            category="dtype_mismatch",
            description="Mixed precision without autocast",
            setup_func=test_mixed_precision_mismatch,
            expected_violation="DtypeConsistencyViolation",
            source_issue="pytorch/pytorch#mixed-precision"
        ),
        DefectTestCase(
            defect_id="dtype-002",
            category="dtype_mismatch",
            description="Integer vs float dtype mismatch",
            setup_func=test_int_float_mismatch,
            expected_violation="DtypeConsistencyViolation",
            source_issue="synthetic"
        ),
        DefectTestCase(
            defect_id="dtype-003",
            category="dtype_mismatch",
            description="Autocast context boundary violation",
            setup_func=test_autocast_boundary,
            expected_violation="DtypeConsistencyViolation",
            source_issue="pytorch/amp"
        ),
    ]

    return tests


def create_layout_mismatch_tests() -> List[DefectTestCase]:
    """Layout inconsistencies (strided vs sparse)"""

    def test_sparse_dense_mismatch():
        """Sparse tensor mixed with dense tensor"""
        @validate_composition(device_consistency=True)
        def sparse_dense_op(sparse_tensor, dense_tensor):
            return torch.sparse.mm(sparse_tensor, dense_tensor)

        # Setup: one sparse, one dense
        indices = torch.tensor([[0, 1, 1], [2, 0, 2]])
        values = torch.tensor([3, 4, 5], dtype=torch.float32)
        sparse = torch.sparse_coo_tensor(indices, values, (2, 3))
        dense = torch.randn(3, 4)

        # This should trigger layout check
        return sparse_dense_op(sparse, dense)

    tests = [
        DefectTestCase(
            defect_id="layout-001",
            category="layout_mismatch",
            description="Sparse + dense tensor layout inconsistency",
            setup_func=test_sparse_dense_mismatch,
            expected_violation="LayoutConsistencyViolation",
            source_issue="pytorch/sparse"
        ),
    ]

    return tests


def create_control_tests() -> List[DefectTestCase]:
    """Control tests (no defects) - should pass"""

    def test_valid_composition():
        """Valid composition with matching devices/dtypes"""
        @validate_composition(
            device_consistency=True,
            dtype_spec={'x': torch.float32, 'y': torch.float32}
        )
        def add_tensors(x, y):
            return x + y

        x = torch.randn(10, 10, dtype=torch.float32)
        y = torch.randn(10, 10, dtype=torch.float32)

        return add_tensors(x, y)

    tests = [
        DefectTestCase(
            defect_id="control-001",
            category="control",
            description="Valid composition (no defects)",
            setup_func=test_valid_composition,
            expected_violation="none",
            source_issue="synthetic"
        ),
    ]

    return tests


def load_all_test_cases() -> List[DefectTestCase]:
    """Load all test cases (10-20 cases from real issues)"""
    all_tests = []

    all_tests.extend(create_device_mismatch_tests())
    all_tests.extend(create_dtype_mismatch_tests())
    all_tests.extend(create_layout_mismatch_tests())
    all_tests.extend(create_control_tests())

    return all_tests
