# Logic Design: H-M1 Structural Contract Validation

**Hypothesis ID:** h-m1  
**Document Type:** Logic Design  
**Phase:** 3 - Implementation Planning  
**Status:** READY FOR CODING  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - designing new APIs  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## KB Pattern Application

**Applied**: PyTorch decorator pattern, HuggingFace hooks pattern, distributed tensor validation

---

## L-1: Shape Validation Core [Complexity: 8, Budget: 8]

### API Signatures

```python
class ShapeValidator:
    """Validates tensor shapes against symbolic specifications."""
    
    def __init__(self):
        """Initialize validator with empty symbol cache."""
        self._symbol_cache: Dict[str, int] = {}
    
    def parse_shape_spec(self, spec: str) -> List[Union[int, str]]:
        """Parse shape specification string.
        
        Args:
            spec: Shape spec like "batch:B channels:3 height:32 width:32"
        
        Returns:
            List of ints (concrete) or strings (symbolic). E.g., ['B', 3, 32, 32]
        """
        ...
    
    def validate_shape(
        self,
        tensor: Tensor,
        spec: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate tensor shape against specification.
        
        Args:
            tensor: Tensor to validate. Shape: [*]
            spec: Shape specification string
            param_name: Parameter name for error messages
        
        Returns:
            (is_valid, error_message). error_message is None if valid.
        
        Example:
            validator.validate_shape(x, "batch:B channels:3 height:32 width:32", "x")
            # If x.shape = [16, 3, 32, 32] -> (True, None)
            # If x.shape = [16, 4, 32, 32] -> (False, "Expected channels=3, got 4")
        """
        ...
    
    def unify_symbolic(self, symbol: str, value: int) -> bool:
        """Bind symbolic dimension to concrete value.
        
        Args:
            symbol: Symbolic name (e.g., "B")
            value: Concrete dimension value
        
        Returns:
            True if binding succeeds, False if conflicts with existing binding.
        
        Example:
            validator.unify_symbolic("B", 16)  # First binding -> True
            validator.unify_symbolic("B", 32)  # Conflict -> False
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| tensor | [*] | Arbitrary rank tensor |
| spec | str | Shape specification string |
| parsed_spec | List[Union[int, str]] | E.g., ['B', 3, 32, 32] |

### Pseudo-code

```
parse_shape_spec(spec):
    1. tokens = spec.split()  # ["batch:B", "channels:3", ...]
    2. dims = []
    3. for token in tokens:
        name, value = token.split(":")
        if value.isdigit():
            dims.append(int(value))  # Concrete
        else:
            dims.append(value)  # Symbolic
    4. return dims

validate_shape(tensor, spec, param_name):
    1. expected_dims = parse_shape_spec(spec)
    2. actual_shape = tensor.shape
    3. if len(expected_dims) != len(actual_shape):
        return (False, f"Expected {len(expected_dims)} dims, got {len(actual_shape)}")
    4. for i, (expected, actual) in enumerate(zip(expected_dims, actual_shape)):
        if isinstance(expected, int):
            if expected != actual:
                return (False, f"Dim {i}: expected {expected}, got {actual}")
        else:  # Symbolic
            if not unify_symbolic(expected, actual):
                return (False, f"Symbolic {expected} conflicts: cached={_symbol_cache[expected]}, actual={actual}")
    5. return (True, None)

unify_symbolic(symbol, value):
    1. if symbol in _symbol_cache:
        return _symbol_cache[symbol] == value
    2. _symbol_cache[symbol] = value
    3. return True
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Shape parser | Parse "batch:B channels:3" -> ['B', 3] |
| L-1-2 | Symbolic unification | Bind symbolic dimensions to concrete values |
| L-1-3 | Shape comparison | Match expected vs. actual shapes |
| L-1-4 | Error formatting | Generate actionable error messages |
| L-1-5 | Cache management | Store symbol bindings across probes |
| L-1-6 | Rank validation | Check dimension count matches |
| L-1-7 | Concrete validation | Validate fixed dimensions |
| L-1-8 | Unit tests | Test symbolic batch, concrete spatial dims |

---

## L-2: Probe Execution Engine [Complexity: 7, Budget: 7]

### API Signatures

```python
class ProbeExecutor:
    """Executes shape probes at import time."""
    
    def __init__(self, cache_dir: str = "~/.cache/structural_contracts/probes/"):
        """Initialize probe executor with cache directory."""
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_probe_input(
        self,
        shape_spec: str,
        dtype: torch.dtype,
        device: str = "cpu"
    ) -> Tensor:
        """Generate 1-sample probe tensor.
        
        Args:
            shape_spec: Shape specification (e.g., "batch:B channels:3 height:32 width:32")
            dtype: Tensor dtype
            device: Device placement
        
        Returns:
            Probe tensor with batch=1. Shape: [1, *dims]
        
        Example:
            probe = generate_probe_input("batch:B channels:3 height:32 width:32", torch.float32)
            # probe.shape = [1, 3, 32, 32]
        """
        ...
    
    def execute_probe(
        self,
        func: Callable,
        probe_inputs: Dict[str, Tensor]
    ) -> Union[Tensor, Dict[str, Tensor]]:
        """Execute function with probe inputs.
        
        Args:
            func: Function to probe (e.g., model.forward)
            probe_inputs: Dict of parameter names to probe tensors
        
        Returns:
            Function output (tensor or dict of tensors)
        
        Example:
            output = execute_probe(model.forward, {"x": probe_tensor})
            # Returns model(probe_tensor)
        """
        ...
    
    def check_probe_cache(self, func_signature: str) -> Optional[Dict[str, Any]]:
        """Check if probe results are cached.
        
        Args:
            func_signature: Unique function identifier (module path + function name + hash)
        
        Returns:
            Cached probe results or None if cache miss.
        """
        ...
    
    def save_probe_cache(self, func_signature: str, results: Dict[str, Any]) -> None:
        """Save probe results to cache.
        
        Args:
            func_signature: Unique function identifier
            results: Probe results (output shapes, dtypes, devices)
        """
        ...
```

### Pseudo-code

```
generate_probe_input(shape_spec, dtype, device):
    1. dims = ShapeValidator().parse_shape_spec(shape_spec)
    2. concrete_dims = []
    3. for dim in dims:
        if isinstance(dim, int):
            concrete_dims.append(dim)
        else:  # Symbolic (e.g., "B")
            concrete_dims.append(1)  # Probe with batch=1
    4. return torch.randn(*concrete_dims, dtype=dtype, device=device)

execute_probe(func, probe_inputs):
    1. try:
        output = func(**probe_inputs)
    2. except Exception as e:
        raise ProbeExecutionError(f"Probe failed: {e}")
    3. return output

check_probe_cache(func_signature):
    1. cache_file = cache_dir / f"{func_signature}.json"
    2. if cache_file.exists():
        return json.load(cache_file)
    3. return None

save_probe_cache(func_signature, results):
    1. cache_file = cache_dir / f"{func_signature}.json"
    2. json.dump(results, cache_file)
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Probe generation | Create 1-sample tensors with symbolic dims=1 |
| L-2-2 | Probe execution | Call function with probe inputs |
| L-2-3 | Exception handling | Catch and wrap probe execution errors |
| L-2-4 | Cache key generation | Hash function signature for cache lookup |
| L-2-5 | Cache read | Load cached probe results from disk |
| L-2-6 | Cache write | Serialize probe results to JSON |
| L-2-7 | Unit tests | Test probe generation, cache hit/miss |

---

## L-3: Device Consistency Checker [Complexity: 5, Budget: 5]

### API Signatures

```python
class DeviceChecker:
    """Validates device placement consistency."""
    
    def check_device_consistency(
        self,
        tensors: Dict[str, Tensor]
    ) -> Tuple[bool, Optional[str]]:
        """Check all tensors are on same device.
        
        Args:
            tensors: Dict of parameter names to tensors
        
        Returns:
            (is_consistent, error_message). error_message is None if consistent.
        
        Example:
            checker.check_device_consistency({"x": x_cpu, "y": y_cuda})
            # Returns (False, "Device mismatch: x on cpu, y on cuda")
        """
        ...
    
    def validate_device(
        self,
        tensor: Tensor,
        expected_device: str,
        param_name: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate tensor is on expected device.
        
        Args:
            tensor: Tensor to validate
            expected_device: Expected device ("cpu", "cuda", "cuda:0")
            param_name: Parameter name for error messages
        
        Returns:
            (is_valid, error_message). error_message is None if valid.
        """
        ...
```

### Pseudo-code

```
check_device_consistency(tensors):
    1. devices = {name: tensor.device for name, tensor in tensors.items()}
    2. unique_devices = set(devices.values())
    3. if len(unique_devices) > 1:
        device_list = ", ".join(f"{name} on {dev}" for name, dev in devices.items())
        return (False, f"Device mismatch: {device_list}")
    4. return (True, None)

validate_device(tensor, expected_device, param_name):
    1. actual_device = str(tensor.device)
    2. if actual_device != expected_device:
        return (False, f"{param_name} on {actual_device}, expected {expected_device}")
    3. return (True, None)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Device extraction | Extract device from tensor.device |
| L-3-2 | Consistency check | Verify all tensors on same device |
| L-3-3 | Device comparison | Compare expected vs. actual device |
| L-3-4 | Error formatting | Generate device mismatch error messages |
| L-3-5 | Unit tests | Test CPU/CUDA mismatches |

---

## L-4: Dtype Validation [Complexity: 4, Budget: 4]

### API Signatures

```python
class DtypeChecker:
    """Validates tensor dtypes."""
    
    def validate_dtype(
        self,
        tensor: Tensor,
        expected_dtype: torch.dtype,
        param_name: str,
        warn_only: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Validate tensor dtype.
        
        Args:
            tensor: Tensor to validate
            expected_dtype: Expected dtype (e.g., torch.float32)
            param_name: Parameter name for error messages
            warn_only: If True, log warning instead of error for auto-casting cases
        
        Returns:
            (is_valid, error_message). error_message is None if valid.
        
        Example:
            checker.validate_dtype(x, torch.float32, "x")
            # If x.dtype = torch.float16 -> (False, "x has dtype float16, expected float32")
        """
        ...
    
    def is_safe_cast(self, from_dtype: torch.dtype, to_dtype: torch.dtype) -> bool:
        """Check if dtype cast is safe (no precision loss).
        
        Args:
            from_dtype: Source dtype
            to_dtype: Target dtype
        
        Returns:
            True if cast is safe (e.g., float32 -> float64), False otherwise (e.g., float32 -> float16).
        """
        ...
```

### Pseudo-code

```
validate_dtype(tensor, expected_dtype, param_name, warn_only):
    1. actual_dtype = tensor.dtype
    2. if actual_dtype == expected_dtype:
        return (True, None)
    3. if warn_only and is_safe_cast(actual_dtype, expected_dtype):
        log_warning(f"{param_name} will auto-cast from {actual_dtype} to {expected_dtype}")
        return (True, None)
    4. return (False, f"{param_name} has dtype {actual_dtype}, expected {expected_dtype}")

is_safe_cast(from_dtype, to_dtype):
    # Safe casts: float32 -> float64, int32 -> int64
    1. safe_casts = {
        (torch.float32, torch.float64): True,
        (torch.int32, torch.int64): True,
        # ... (populate with PyTorch implicit cast rules)
    }
    2. return safe_casts.get((from_dtype, to_dtype), False)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Dtype comparison | Compare expected vs. actual dtype |
| L-4-2 | Safe cast detection | Identify auto-casting scenarios |
| L-4-3 | Warning vs. error | Log warnings for safe casts |
| L-4-4 | Unit tests | Test int64/float32 mismatches |

---

## L-5: Structural Validator Decorator [Complexity: 9, Budget: 9]

### API Signatures

```python
def validate_structural(
    inputs: Dict[str, str],
    outputs: Dict[str, str],
    dtype: Dict[str, torch.dtype] = {},
    device_consistency: bool = False
) -> Callable:
    """Decorator for structural validation of PyTorch functions.
    
    Args:
        inputs: Dict of param_name -> shape_spec (e.g., {"x": "batch:B channels:3 height:32 width:32"})
        outputs: Dict of return_name -> shape_spec (e.g., {"return": "batch:B classes:10"})
        dtype: Dict of param_name -> expected_dtype
        device_consistency: If True, verify all tensors on same device
    
    Returns:
        Decorator function that wraps target function
    
    Raises:
        StructuralContractViolation: If probe detects violation at import time
    
    Example:
        @validate_structural(
            inputs={"x": "batch:B channels:3 height:32 width:32"},
            outputs={"return": "batch:B classes:10"},
            dtype={"x": torch.float32},
            device_consistency=True
        )
        def forward(x: Tensor) -> Tensor:
            return model(x)
    """
    ...

class StructuralContractViolation(Exception):
    """Raised when structural contract is violated."""
    
    def __init__(
        self,
        message: str,
        param_name: str,
        expected: str,
        actual: str
    ):
        """Initialize with detailed error information.
        
        Args:
            message: Human-readable error message
            param_name: Parameter that violated contract
            expected: Expected value (shape, dtype, device)
            actual: Actual value
        """
        super().__init__(message)
        self.param_name = param_name
        self.expected = expected
        self.actual = actual
```

### Pseudo-code

```
validate_structural(inputs, outputs, dtype, device_consistency):
    1. def decorator(func):
        # Import-time execution
        2. func_signature = compute_signature(func)
        3. cached_results = ProbeExecutor().check_probe_cache(func_signature)
        4. if cached_results:
            return func  # Skip probe, use cache
        
        5. probe_inputs = {}
        6. for param_name, shape_spec in inputs.items():
            probe_dtype = dtype.get(param_name, torch.float32)
            probe_inputs[param_name] = ProbeExecutor().generate_probe_input(
                shape_spec, probe_dtype
            )
        
        7. if device_consistency:
            is_consistent, error = DeviceChecker().check_device_consistency(probe_inputs)
            if not is_consistent:
                raise StructuralContractViolation(error, "probe_inputs", "same device", error)
        
        8. probe_output = ProbeExecutor().execute_probe(func, probe_inputs)
        
        9. for output_name, shape_spec in outputs.items():
            if output_name == "return":
                output_tensor = probe_output
            else:  # Dict output
                output_tensor = probe_output[output_name]
            
            is_valid, error = ShapeValidator().validate_shape(
                output_tensor, shape_spec, output_name
            )
            if not is_valid:
                raise StructuralContractViolation(
                    error, output_name, shape_spec, str(output_tensor.shape)
                )
        
        10. ProbeExecutor().save_probe_cache(func_signature, {
            "input_shapes": {k: list(v.shape) for k, v in probe_inputs.items()},
            "output_shapes": {k: list(v.shape) for k, v in outputs.items()}
        })
        
        11. return func  # Return original function (no runtime overhead)
    
    12. return decorator

compute_signature(func):
    1. module_path = func.__module__
    2. func_name = func.__qualname__
    3. source_hash = hashlib.md5(inspect.getsource(func).encode()).hexdigest()
    4. return f"{module_path}.{func_name}.{source_hash}"
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Decorator wrapper | Implement decorator function |
| L-5-2 | Probe generation | Generate probe inputs from shape specs |
| L-5-3 | Probe execution | Execute function with probe inputs |
| L-5-4 | Input validation | Validate input shapes/dtypes |
| L-5-5 | Output validation | Validate output shapes |
| L-5-6 | Device check | Validate device consistency if enabled |
| L-5-7 | Cache integration | Check cache before probe, save after |
| L-5-8 | Error raising | Raise StructuralContractViolation on failure |
| L-5-9 | Signature computation | Hash function source for cache key |

---

## L-6: Defect Injection Framework [Complexity: 6, Budget: 6]

### API Signatures

```python
class DefectInjector:
    """Injects structural defects for validation experiments."""
    
    def __init__(self, catalog_path: str):
        """Initialize injector with defect catalog.
        
        Args:
            catalog_path: Path to defect catalog JSON file
        """
        self.catalog = self._load_catalog(catalog_path)
    
    def inject_defect(self, defect_id: str) -> Callable[[], None]:
        """Inject structural defect.
        
        Args:
            defect_id: Defect identifier from catalog (e.g., "SM-001")
        
        Returns:
            Rollback function to restore original behavior
        
        Example:
            rollback = injector.inject_defect("SM-001")
            # Defect now active
            rollback()  # Restore original
        """
        ...
    
    def inject_shape_mismatch(
        self,
        target_module: str,
        target_function: str,
        wrong_dims: Dict[int, int]
    ) -> Callable[[], None]:
        """Inject shape mismatch defect.
        
        Args:
            target_module: Module to patch (e.g., "torchvision.transforms")
            target_function: Function to patch (e.g., "ToTensor")
            wrong_dims: Dict of dim_index -> wrong_value (e.g., {1: 4} for channels)
        
        Returns:
            Rollback function
        
        Example:
            injector.inject_shape_mismatch(
                "torchvision.transforms", "ToTensor", {1: 4}  # 3 -> 4 channels
            )
        """
        ...
    
    def inject_device_mismatch(
        self,
        target_module: str,
        target_function: str,
        force_device: str
    ) -> Callable[[], None]:
        """Inject device mismatch defect.
        
        Args:
            target_module: Module to patch
            target_function: Function to patch
            force_device: Device to force ("cpu" or "cuda")
        
        Returns:
            Rollback function
        """
        ...
    
    def inject_dtype_mismatch(
        self,
        target_module: str,
        target_function: str,
        force_dtype: torch.dtype
    ) -> Callable[[], None]:
        """Inject dtype mismatch defect."""
        ...
    
    def inject_null_output(
        self,
        target_module: str,
        target_function: str
    ) -> Callable[[], None]:
        """Inject null output defect (return None instead of tensor)."""
        ...
```

### Pseudo-code

```
inject_defect(defect_id):
    1. defect_spec = catalog[defect_id]
    2. category = defect_spec["category"]
    3. if category == "shape_mismatch":
        return inject_shape_mismatch(
            defect_spec["target_module"],
            defect_spec["target_function"],
            defect_spec["wrong_dims"]
        )
    4. elif category == "device_mismatch":
        return inject_device_mismatch(...)
    # ... (similar for dtype, null output)

inject_shape_mismatch(target_module, target_function, wrong_dims):
    1. module = importlib.import_module(target_module)
    2. original_func = getattr(module, target_function)
    3. def patched_func(*args, **kwargs):
        output = original_func(*args, **kwargs)
        # Modify output shape
        for dim_idx, wrong_val in wrong_dims.items():
            output = torch.cat([output, torch.zeros(...)])  # Add extra channels
        return output
    4. setattr(module, target_function, patched_func)
    5. rollback = lambda: setattr(module, target_function, original_func)
    6. return rollback

inject_device_mismatch(target_module, target_function, force_device):
    1. module = importlib.import_module(target_module)
    2. original_func = getattr(module, target_function)
    3. def patched_func(*args, **kwargs):
        output = original_func(*args, **kwargs)
        return output.to(force_device)  # Force wrong device
    4. setattr(module, target_function, patched_func)
    5. rollback = lambda: setattr(module, target_function, original_func)
    6. return rollback
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Catalog loader | Parse defect catalog JSON |
| L-6-2 | Monkey-patching | Replace target function with defect |
| L-6-3 | Shape injection | Modify output shape (add/remove dims) |
| L-6-4 | Device injection | Force tensors to wrong device |
| L-6-5 | Dtype injection | Force tensors to wrong dtype |
| L-6-6 | Null injection | Return None instead of tensor |

---

## L-7: Measurement Infrastructure [Complexity: 5, Budget: 5]

### API Signatures

```python
class DetectionMeasurer:
    """Measures detection rate and execution time."""
    
    def measure_detection_stage(
        self,
        defect_id: str,
        run_with_contracts: bool
    ) -> str:
        """Measure at which stage defect is detected.
        
        Args:
            defect_id: Defect identifier
            run_with_contracts: True = contracts enabled, False = no contracts
        
        Returns:
            Detection stage: "import", "forward", "training", or "undetected"
        
        Example:
            stage = measurer.measure_detection_stage("SM-001", run_with_contracts=True)
            # Returns "import" if caught by contract at import time
        """
        ...
    
    def measure_execution_time(
        self,
        func: Callable
    ) -> float:
        """Measure wall-clock execution time.
        
        Args:
            func: Function to measure
        
        Returns:
            Execution time in seconds
        """
        ...
    
    def calculate_detection_rate(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate detection rate from experiment results.
        
        Args:
            results: List of dicts with keys: defect_id, detection_stage
        
        Returns:
            Dict with keys: detection_rate, confidence_interval_lower, confidence_interval_upper
        
        Example:
            stats = measurer.calculate_detection_rate([
                {"defect_id": "SM-001", "detection_stage": "import"},
                {"defect_id": "SM-002", "detection_stage": "forward"},
                ...
            ])
            # Returns {"detection_rate": 0.85, "ci_lower": 0.80, "ci_upper": 0.90}
        """
        ...
```

### Pseudo-code

```
measure_detection_stage(defect_id, run_with_contracts):
    1. injector = DefectInjector(catalog_path)
    2. rollback = injector.inject_defect(defect_id)
    3. try:
        # Import stage
        4. if run_with_contracts:
            model = create_model_with_contracts()  # Raises at import if violation
        else:
            model = create_model_no_contracts()
        5. detection_stage = "undetected"  # Passed import
        
        # Forward stage
        6. try:
            output = model(test_input)
        7. except Exception:
            detection_stage = "forward"
            return detection_stage
        
        # Training stage
        8. try:
            train_one_epoch(model)
        9. except Exception:
            detection_stage = "training"
            return detection_stage
    10. except StructuralContractViolation:
        detection_stage = "import"
    11. finally:
        rollback()
    12. return detection_stage

measure_execution_time(func):
    1. start = time.time()
    2. func()
    3. end = time.time()
    4. return end - start

calculate_detection_rate(results):
    1. import_detections = sum(1 for r in results if r["detection_stage"] == "import")
    2. total_defects = len(results)
    3. detection_rate = import_detections / total_defects
    4. # 95% CI using normal approximation
    5. se = sqrt(detection_rate * (1 - detection_rate) / total_defects)
    6. ci_lower = detection_rate - 1.96 * se
    7. ci_upper = detection_rate + 1.96 * se
    8. return {"detection_rate": detection_rate, "ci_lower": ci_lower, "ci_upper": ci_upper}
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Stage detection | Determine import/forward/training stage |
| L-7-2 | Time measurement | Wall-clock timing with time.time() |
| L-7-3 | Detection rate calc | Compute proportion of import detections |
| L-7-4 | Confidence interval | Calculate 95% CI using normal approximation |
| L-7-5 | Results logging | Write results to CSV |

---

## Edge Cases & Error Handling

### Edge Case 1: Dynamic Shapes with Variable Batch Size

**Scenario**: Model supports variable batch sizes (batch=1, 16, 32, etc.)  
**Solution**: Use symbolic dimension "B" in shape spec, probe with batch=1  
**Validation**: Symbol cache ensures all "B" dimensions match across forward pass

### Edge Case 2: Optional Outputs (Dict Returns)

**Scenario**: Function returns `Dict[str, Tensor]` with optional keys  
**Solution**: Use `outputs={"key1": spec, "key2": spec}`, check only required keys  
**Validation**: Skip validation for keys marked `Optional` in type hints

### Edge Case 3: Mixed Device Tensors (Distributed Training)

**Scenario**: Model shards across multiple GPUs (e.g., `cuda:0`, `cuda:1`)  
**Solution**: Disable `device_consistency` flag, validate each tensor separately  
**Validation**: Allow different devices if `device_consistency=False`

### Edge Case 4: Implicit Dtype Casting (AMP)

**Scenario**: PyTorch Automatic Mixed Precision (AMP) auto-casts `float32` -> `float16`  
**Solution**: Set `warn_only=True` for dtype validation, log warnings instead of errors  
**Validation**: Use `DtypeChecker.is_safe_cast()` to detect intentional casts

### Edge Case 5: Probe Execution Failures (Uninitialized Parameters)

**Scenario**: Probe fails because model parameters not initialized  
**Solution**: Catch `ProbeExecutionError`, log warning, skip validation  
**Validation**: Require explicit `model.to(device)` before applying contracts

### Edge Case 6: Cache Invalidation on Source Changes

**Scenario**: Function source code changes, cached probe results stale  
**Solution**: Include source code hash in cache key (`func_signature`)  
**Validation**: Re-run probe if source hash changes

---

## Algorithm Complexity Analysis

| Component | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Shape parser | O(n) | O(n) | n = number of dimensions |
| Shape validation | O(d) | O(s) | d = rank, s = symbol count |
| Probe generation | O(1) | O(prod(dims)) | Tensor allocation |
| Probe execution | O(f) | O(prod(dims)) | f = forward pass complexity |
| Device check | O(t) | O(1) | t = number of tensors |
| Dtype check | O(1) | O(1) | Single comparison |
| Cache lookup | O(1) | O(1) | Hash table lookup |
| Detection rate | O(n) | O(1) | n = number of results |

**Total Import-Time Overhead**: O(f) dominated by probe execution (single forward pass with batch=1)  
**Expected Latency**: 2-5 seconds (PyTorch startup + 1 forward pass)

---

## Implementation Notes

### Import-Time Execution Strategy

The decorator executes shape probes **during module initialization**, not during function calls:

```python
# This happens at IMPORT time (not runtime)
class MyModel(nn.Module):
    @validate_structural(...)
    def forward(self, x):
        return self.model(x)

# Probe executes here (during __init__)
model = MyModel()  # ← Decorator runs probe, raises if violation
```

This ensures defects are caught before any training code executes.

### Symbolic Dimension Handling

Symbolic dimensions (e.g., "B" for batch) are unified across all tensors:

```python
# First probe: x.shape = [1, 3, 32, 32] -> B=1
# Output: y.shape = [1, 10] -> B=1 (unified with input)
# Second probe: x.shape = [16, 3, 32, 32] -> B=16
# Output: y.shape = [16, 10] -> B=16 (unified)
```

Symbol cache is cleared between decorator invocations to avoid cross-contamination.

### Cache Invalidation Policy

Cache is invalidated when:
1. Function source code changes (detected via hash)
2. Library version changes (cache directory includes version number)
3. Manual cache clear (`rm -rf ~/.cache/structural_contracts/`)

### Error Message Quality

Error messages include:
- Parameter name
- Expected vs. actual values
- Suggested fix (when applicable)

Example:
```
StructuralContractViolation: Shape mismatch for parameter 'x'
  Expected: (B, 3, 32, 32)
  Actual: (16, 4, 32, 32)
  Dimension 1: expected 3 (channels), got 4
  Suggestion: Check input transform - CIFAR-10 should have 3 channels (RGB)
```

---

## Summary

This logic design provides **copy-paste ready APIs** for the structural contract validation library. Key algorithms:

1. **Shape Validation**: Symbolic dimension unification with concrete validation
2. **Probe Execution**: Import-time 1-sample forward pass with caching
3. **Device/Dtype Checking**: Consistency validation with auto-casting awareness
4. **Defect Injection**: Monkey-patching for shape/device/dtype/null defects
5. **Detection Measurement**: Stage detection (import/forward/training) with 95% CI

All modules designed for ≤10s import-time overhead and <5% false positive rate.

**Total Budget Used**: 48/48 (100%)  
**Ready for Phase 4 Coding**: Yes
