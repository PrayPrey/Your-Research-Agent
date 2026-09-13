# Configuration Design: H-C2 Cross-Framework Contract Validation System

**Hypothesis ID:** h-c2  
**Document Type:** Configuration Specification  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m3 actual code  
**Config Files Found**: 
- `/workspace/TEST_scope/docs/youra_research/h-m3/code/composition_validator.py`
- `/workspace/TEST_scope/docs/youra_research/h-m3/code/run_experiment.py`
- `/workspace/TEST_scope/docs/youra_research/h-m3/code/test_cases.py`

**Pattern Used**: Hardcoded dict in experiment script (no config dataclass)

**Note**: h-m3 uses hardcoded experiment parameters in `run_experiment.py`. h-c2 follows same pattern for SHOULD_WORK PoC simplicity.

---

## 1. Configuration Overview

**Applied**: PyTorch PoC pattern (hardcoded dict for minimal configuration)

This is a SHOULD_WORK hypothesis testing cross-framework contract validation. Configuration uses a single hardcoded dictionary to minimize overhead.

**Design Principle**: Minimal config to test "does it work?" - no hyperparameter tuning or ablations for PoC phase.

---

## 2. Inherited Configuration (Base Hypothesis)

### From h-m3 Actual Code

The following patterns are inherited from h-m3 implementation:

```python
# From: h-m3/code/composition_validator.py (ACTUAL CODE)
# Exception hierarchy (extended to cross-framework)
class CompositionViolation(Exception): pass
class DeviceConsistencyViolation(CompositionViolation): pass
class DtypeConsistencyViolation(CompositionViolation): pass
class LayoutConsistencyViolation(CompositionViolation): pass

# Decorator pattern (adapted for cross-framework validation)
def validate_composition(
    device_consistency: bool = True,
    dtype_spec: Optional[Dict[str, torch.dtype]] = None,
    layout_spec: Optional[Dict[str, torch.layout]] = None
): ...

# Validation execution pattern (from run_experiment.py)
def run_with_contracts(test_case):
    start_time = time.time()
    try:
        result = test_case.setup_func()
        detection_time = time.time() - start_time
        return {'detected': False, 'detection_stage': 'none', 'detection_time': detection_time}
    except CompositionViolation as e:
        detection_time = time.time() - start_time
        return {'detected': True, 'detection_stage': 'validation', 'detection_time': detection_time}
```

**Verified from**: `/workspace/TEST_scope/docs/youra_research/h-m3/code/` (actual implementation)

---

## 3. Core Configuration

### 3.1 Contract Library Configuration

**Applied**: Cross-framework tolerance patterns (CUDA numerics docs, CrossedWires research)

```python
# contract_config.py
CONTRACT_CONFIG = {
    # Dtype Preservation Contract
    "dtype_preservation": {
        "enabled": True,
        "strict_mode": True,  # float32 → float16 conversions flagged
        "allowed_upcasts": ["float16→float32", "int32→int64"],  # Safe conversions
        "timeout_per_check": 0.5  # seconds
    },
    
    # Shape Consistency Contract
    "shape_consistency": {
        "enabled": True,
        "allow_batch_flexibility": True,  # Dynamic batch size OK
        "allow_sequence_flexibility": True,  # Dynamic sequence length OK
        "timeout_per_check": 0.3
    },
    
    # Numerical Tolerance Contract (operator-specific thresholds)
    "numerical_tolerance": {
        "enabled": True,
        "default_rtol": 1e-5,  # Standard float32 relative tolerance
        "default_atol": 1e-7,  # Absolute tolerance for near-zero values
        # Per-operator overrides (from CrossedWires/CUDA docs)
        "operator_overrides": {
            "matmul": {"rtol": 1e-4, "atol": 1e-6},  # More lenient (accumulation order)
            "conv2d": {"rtol": 1e-5, "atol": 1e-7},  # Standard
            "softmax": {"rtol": 1e-4, "atol": 1e-6},  # More lenient (exp overflow)
            "layer_norm": {"rtol": 1e-4, "atol": 1e-6}  # More lenient (fp32 precision limits)
        },
        "timeout_per_check": 2.0
    },
    
    # Operator Semantics Contract
    "operator_semantics": {
        "enabled": True,
        "check_parameter_constraints": True,
        "check_default_values": True,
        "timeout_per_check": 1.0
    }
}
```

---

## 4. Framework Adapter Configuration

**Applied**: ArrayBridge unified API pattern, DLPack zero-copy conversion

```python
# framework_config.py
FRAMEWORK_CONFIG = {
    # Framework versions (from PRD requirements)
    "pytorch": {
        "version": "1.13.0",  # Minimum version
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "dtype_default": "float32",
        "eager_mode": True,  # vs compiled mode
        "autograd_enabled": False  # Inference-only for PoC
    },
    
    "tensorflow": {
        "version": "2.10.0",
        "device": "/GPU:0" if tf.config.list_physical_devices('GPU') else "/CPU:0",
        "dtype_default": "float32",
        "execution_mode": "eager",  # vs graph mode (TF2.x default)
        "mixed_precision": False  # Keep consistent with PyTorch
    },
    
    "jax": {
        "version": "0.4.0",
        "device": "gpu" if jax.devices('gpu') else "cpu",
        "dtype_default": "float32",
        "precision": "default",  # vs "high" or "highest"
        "enable_x64": False  # Keep float32 for consistency
    },
    
    "onnx": {
        "version": "1.12.0",
        "opset_version": 13,  # ONNX opset
        "dtype_default": "float32",
        "optimization_level": 0  # No graph optimization for PoC
    },
    
    # Conversion tools
    "converters": {
        "torch2onnx": {"opset": 13, "export_params": True, "do_constant_folding": False},
        "tf2onnx": {"opset": 13},
        "onnx2tf": {},
        "torch2jax": {}
    },
    
    # Adapter settings
    "use_dlpack": True,  # Zero-copy when possible
    "max_conversion_time": 10.0  # Timeout for framework conversions (seconds)
}
```

---

## 5. Dataset Configuration

**Applied**: Stratified sampling strategy (from PRD risk mitigation)

```python
# dataset_config.py
DATASET_CONFIG = {
    # ONNX Converter Failure Corpus
    "onnx_failures": {
        "total_samples": 200,
        "source": "github_issues",  # torch.onnx, tf2onnx repos
        "split": {"train": 140, "test": 60},  # 70/30 split
        "defect_categories": ["crash", "silent_misbehavior", "shape_mismatch", "dtype_error"]
    },
    
    # CrossedWires Models (stratified sample - CRITICAL for storage)
    "crossedwires": {
        "full_dataset_size": 2400,  # 340 GB - TOO LARGE
        "use_sample": True,  # PRD risk mitigation
        "sample_size": 300,  # ~30 GB
        "sampling_strategy": "stratified",  # 100 models per architecture
        "architectures": ["VGG16", "ResNet50", "DenseNet121"],
        "per_architecture_count": 100,
        "min_accuracy_discrepancy": 0.05,  # Filter near-identical pairs
        "split": {"train": 210, "test": 90}  # 70/30
    },
    
    # Synthetic Defect Injection
    "synthetic": {
        "total_samples": 500,
        "base_models": 100,  # Valid ONNX conversions
        "mutation_operators": {
            "dtype_corruption": 125,  # float32 → float16, int32 → int64
            "shape_mismatch": 125,    # Transpose errors, drop dimensions
            "operator_param_error": 125,  # Padding mode, stride value
            "numerical_drift": 125    # Accumulation order changes
        },
        "split": {"train": 350, "test": 150}
    },
    
    # Test inputs per model
    "test_inputs_per_model": 10,  # PRD: 10-100 inputs per model validation
    "input_generation_seed": 42
}
```

---

## 6. Validation Execution Configuration

**Applied**: Timeout pattern from h-m3 (10s per test)

```python
# validation_config.py
VALIDATION_CONFIG = {
    # Timeout settings (PRD NFR-1: <5s validation time)
    "timeout_per_contract": 2.0,  # Individual contract timeout
    "timeout_per_model": 10.0,    # Total validation timeout per model
    "timeout_framework_conversion": 10.0,  # Framework conversion timeout
    
    # Execution settings
    "parallel_contracts": True,  # Run contracts in parallel when possible
    "max_workers": 4,  # Thread pool size
    "fail_fast": False,  # Continue all contracts even if one fails
    
    # Detection tracking
    "track_detection_stage": True,  # import vs validation vs runtime
    "track_timing_breakdown": True,  # Per-contract timing
    
    # Error handling
    "retry_on_framework_crash": True,
    "max_retries": 1,
    "ignore_timeout_errors": False  # Treat timeout as validation failure
}
```

---

## 7. Baseline Configuration

**Applied**: Standard PyTorch/TensorFlow inference patterns

```python
# baseline_config.py
BASELINE_CONFIG = {
    # No Validation baseline
    "no_validation": {
        "enabled": True,
        "measure_conversion_time": True
    },
    
    # End-to-End Validation baseline (current best practice)
    "end_to_end": {
        "enabled": True,
        "test_set_size": 100,  # Number of inputs for inference
        "inference_timeout": 60.0,  # PRD: ~60s expected
        "metric": "output_comparison",  # Compare final outputs
        "tolerance": {"rtol": 1e-5, "atol": 1e-7}
    },
    
    # Framework-Native Testing baseline
    "framework_native": {
        "enabled": True,
        "test_type": "cpu_vs_gpu",  # Intra-framework differential
        "timeout": 30.0
    },
    
    # ONNX Checker baseline
    "onnx_checker": {
        "enabled": True,
        "use_shape_inference": True,
        "strict_mode": True,
        "timeout": 2.0  # PRD: ~2s expected
    }
}
```

---

## 8. Evaluation Metrics Configuration

**Applied**: Standard detection rate formula (from h-m3 pattern)

```python
# metrics_config.py
METRICS_CONFIG = {
    # Detection metrics (PRD success criteria)
    "detection_rate_threshold": 0.70,  # SHOULD_WORK gate
    "false_positive_threshold": 0.10,  # <10% FPR required
    "precision_threshold": 0.80,  # ≥80% precision
    "f1_threshold": 0.75,  # ≥0.75 F1 score
    
    # Statistical analysis
    "significance_level": 0.05,  # α for hypothesis testing
    "effect_size_threshold": 0.5,  # Cohen's d medium effect
    "bootstrap_iterations": 1000,  # For 95% CI estimation
    
    # Stratification dimensions
    "stratify_by": [
        "defect_type",
        "framework_pair",
        "contract_type",
        "model_architecture"
    ],
    
    # Output formats
    "save_confusion_matrix": True,
    "save_per_contract_results": True,
    "save_timing_breakdown": True,
    "results_format": "json"
}
```

---

## 9. Visualization Configuration

**Applied**: matplotlib chart pattern (from h-m3)

```python
# visualization_config.py
VISUALIZATION_CONFIG = {
    # Figure settings
    "figure_format": "png",
    "output_dir": "figures/",
    "dpi": 300,
    
    # Mandatory figures (PRD FR-8)
    "mandatory_figures": [
        "detection_rate_comparison.png",  # Baseline vs H-C2
        "validation_time_distribution.png",
        "false_positive_analysis.png",
        "confusion_matrix.png"  # Defect type × Contract type
    ],
    
    # Chart configurations
    "detection_chart": {
        "title": "Detection Rate: Baselines vs Cross-Framework Contracts",
        "threshold_line": 0.70,  # SHOULD_WORK gate
        "colors": {
            "no_validation": "#FF6B6B",
            "end_to_end": "#FFA500",
            "framework_native": "#FFD700",
            "onnx_checker": "#4ECDC4",
            "h_c2": "#45B7D1"
        },
        "figsize": (12, 6)
    },
    
    "confusion_matrix": {
        "cmap": "Blues",
        "normalize": True,
        "figsize": (10, 8)
    }
}
```

---

## 10. Environment Configuration

**Applied**: PyTorch reproducibility pattern (from h-m3)

```python
# environment_config.py
ENVIRONMENT_CONFIG = {
    # Reproducibility
    "seed": 42,
    "torch_seed": 42,
    "numpy_seed": 42,
    "tf_seed": 42,
    "jax_seed": 42,
    
    # Hardware
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "gpu_memory_fraction": 0.8,  # Reserve 20% for system
    "allow_growth": True,  # TensorFlow GPU memory allocation
    
    # Performance vs determinism trade-off
    "cuda_deterministic": False,  # PoC prioritizes speed over exact reproducibility
    "cudnn_benchmark": True,  # Enable for performance (non-deterministic)
    
    # Logging
    "log_level": "INFO",
    "log_file": "experiment.log",
    "verbose_errors": True  # Detailed error messages for debugging
}
```

---

## 11. Experiment Results Schema

**Applied**: JSON results pattern from h-m3

```python
# results_schema.py
RESULTS_SCHEMA = {
    "experiment_id": "h-c2-poc",
    "timestamp": "ISO-8601",
    "framework_versions": {
        "pytorch": "str",
        "tensorflow": "str",
        "jax": "str",
        "onnx": "str"
    },
    "test_results": [
        {
            "test_id": "str",
            "dataset_source": "onnx_failures | crossedwires | synthetic",
            "framework_pair": "PyTorch→TF | TF→PyTorch | PyTorch→JAX | *→ONNX",
            "defect_type": "DtypeCorruption | ShapeInconsistency | NumericalDrift | APIIncompatibility | None",
            "ground_truth": "defect | valid",
            
            # Baseline results
            "no_validation_detected": bool,
            "end_to_end_detected": bool,
            "end_to_end_time": float,
            "framework_native_detected": bool,
            "onnx_checker_detected": bool,
            
            # H-C2 results
            "contracts_run": ["dtype", "shape", "numerical", "operator"],
            "contract_results": {
                "dtype": {"passed": bool, "time": float, "error": "str | None"},
                "shape": {"passed": bool, "time": float, "error": "str | None"},
                "numerical": {"passed": bool, "time": float, "error": "str | None"},
                "operator": {"passed": bool, "time": float, "error": "str | None"}
            },
            "h_c2_detected": bool,
            "h_c2_total_time": float,
            "detection_stage": "none | validation | runtime"
        }
    ],
    "summary": {
        "total_tests": int,
        "total_defects": int,
        
        # Detection rates
        "no_validation_rate": float,
        "end_to_end_rate": float,
        "framework_native_rate": float,
        "onnx_checker_rate": float,
        "h_c2_detection_rate": float,
        
        # Per-contract detection
        "dtype_contract_rate": float,
        "shape_contract_rate": float,
        "numerical_contract_rate": float,
        "operator_contract_rate": float,
        
        # Timing
        "avg_validation_time": float,
        "median_validation_time": float,
        "p95_validation_time": float,
        
        # Quality metrics
        "precision": float,
        "recall": float,
        "f1_score": float,
        "false_positive_rate": float,
        
        # Statistical analysis
        "hypothesis_test": {
            "test_type": "paired_t_test",
            "p_value": float,
            "cohen_d": float,
            "significant": bool
        }
    }
}
```

---

## 12. Configuration Loading Pattern

### Single-File Configuration (PoC Simplicity)

```python
# config.py (minimal - all configs in one dict)
import torch
import tensorflow as tf

CONFIG = {
    # Contract settings
    "dtype_preservation_enabled": True,
    "shape_consistency_enabled": True,
    "numerical_tolerance_enabled": True,
    "operator_semantics_enabled": True,
    
    # Numerical tolerances
    "default_rtol": 1e-5,
    "default_atol": 1e-7,
    "matmul_rtol": 1e-4,
    "matmul_atol": 1e-6,
    
    # Dataset
    "onnx_samples": 200,
    "crossedwires_sample": 300,  # CRITICAL: Use sample, not full 340 GB
    "synthetic_samples": 500,
    "train_test_split": 0.70,
    "test_inputs_per_model": 10,
    
    # Frameworks
    "pytorch_version": "1.13.0",
    "tensorflow_version": "2.10.0",
    "jax_version": "0.4.0",
    "onnx_version": "1.12.0",
    
    # Execution
    "timeout_per_contract": 2.0,
    "timeout_per_model": 10.0,
    "parallel_contracts": True,
    "max_workers": 4,
    
    # Baselines
    "run_no_validation": True,
    "run_end_to_end": True,
    "run_framework_native": True,
    "run_onnx_checker": True,
    
    # Metrics
    "detection_rate_threshold": 0.70,
    "false_positive_threshold": 0.10,
    "precision_threshold": 0.80,
    "f1_threshold": 0.75,
    
    # Environment
    "seed": 42,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "log_level": "INFO",
    
    # Output
    "results_path": "experiment_results.json",
    "figures_dir": "figures/"
}
```

**Usage in experiment scripts**:

```python
from config import CONFIG

# In contract validators
rtol = CONFIG["default_rtol"]
timeout = CONFIG["timeout_per_contract"]

# In dataset preparation
sample_size = CONFIG["crossedwires_sample"]
split_ratio = CONFIG["train_test_split"]

# In evaluation
threshold = CONFIG["detection_rate_threshold"]
output_dir = CONFIG["figures_dir"]
```

---

## 13. Default Values Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `default_rtol` | 1e-5 | Standard float32 relative tolerance (PRD) |
| `default_atol` | 1e-7 | Absolute tolerance for near-zero values (PRD) |
| `matmul_rtol` | 1e-4 | Lenient for accumulation order differences (CUDA docs) |
| `timeout_per_model` | 10.0 | PRD NFR-1 requirement |
| `crossedwires_sample` | 300 | PRD risk mitigation (340 GB → 30 GB) |
| `detection_rate_threshold` | 0.70 | SHOULD_WORK gate from PRD |
| `false_positive_threshold` | 0.10 | PRD requirement |
| `train_test_split` | 0.70 | Standard ML practice |
| `test_inputs_per_model` | 10 | Balance between coverage and runtime (PRD: 10-100 range) |
| `seed` | 42 | Standard reproducibility seed |
| `parallel_contracts` | True | Performance optimization (no dependencies between contracts) |

---

## 14. Integration with PRD Requirements

| PRD Requirement | Configuration Parameter | Default Value |
|-----------------|-------------------------|---------------|
| FR1: Dtype preservation contract | `dtype_preservation_enabled` | True |
| FR2: Shape consistency contract | `shape_consistency_enabled` | True |
| FR3: Numerical tolerance contract | `numerical_tolerance_enabled`, `default_rtol`, `default_atol` | True, 1e-5, 1e-7 |
| FR4: Operator semantics contract | `operator_semantics_enabled` | True |
| FR5: Unified inference API | `use_dlpack` | True |
| FR6: Contract validator | `timeout_per_model`, `parallel_contracts` | 10.0, True |
| NFR-1: Validation time <5s | `timeout_per_contract`, `timeout_per_model` | 2.0, 10.0 |
| NFR-2: PyTorch 1.13+ | `pytorch_version` | "1.13.0" |
| NFR-2: TensorFlow 2.10+ | `tensorflow_version` | "2.10.0" |
| NFR-2: JAX 0.4+ | `jax_version` | "0.4.0" |
| NFR-2: ONNX 1.12+ | `onnx_version` | "1.12.0" |
| Data: ONNX failures N=200 | `onnx_samples` | 200 |
| Data: CrossedWires sample N=300 | `crossedwires_sample` | 300 |
| Data: Synthetic defects N=500 | `synthetic_samples` | 500 |
| Data: 70/30 split | `train_test_split` | 0.70 |
| Gate: Detection rate ≥70% | `detection_rate_threshold` | 0.70 |
| Gate: FPR <10% | `false_positive_threshold` | 0.10 |

---

## 15. Summary

**Configuration Format**: Hardcoded dict (following h-m3 PoC pattern)

**Total Parameters**: ~40 configuration options in single dict

**Reproducibility**: Fixed seed (42) for all frameworks

**Critical Decisions**:
1. **CrossedWires sampling**: Use 300-model stratified sample (not full 340 GB dataset)
2. **Per-operator tolerances**: matmul more lenient than conv2d (accumulated precision loss)
3. **Parallel execution**: Contracts run in parallel (no inter-dependencies)
4. **Timeout hierarchy**: Contract (2s) → Model (10s) → Conversion (10s)

**Next Steps**:
- Implement configuration in `code/config.py`
- Use CONFIG dict in all experiment scripts
- Validate framework version compatibility before experiment
- Test CrossedWires sampling strategy on validation set first

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 4 - Code Implementation  
**Configuration File Location:** `docs/youra_research/h-c2/code/config.py`
