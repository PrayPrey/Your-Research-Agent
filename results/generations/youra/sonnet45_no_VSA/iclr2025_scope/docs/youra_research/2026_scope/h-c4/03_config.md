# Configuration Design: H-C4 Version-Stable Contract Validation System

**Hypothesis ID:** h-c4  
**Document Type:** Configuration Specification  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: condition_hypothesis  
**Status**: Extends h-m1/h-m2 configurations  
**Config Files Referenced**:
- docs/youra_research/h-m1/code/contracts/validator.py (structural contract defaults)
- docs/youra_research/h-m2/code/contracts/validator.py (metamorphic contract defaults)

**Pattern Used**: Hardcoded dict for experiment parameters (minimal configuration for MUST_WORK validation)

**Note**: h-c4 tests version stability, not contract tuning. Configuration focuses on environment matrix and FPR thresholds.

---

## 1. Configuration Overview

**Applied**: Minimal config pattern for version-transition benchmark

This is a MUST_WORK hypothesis testing contract stability across library versions. Configuration specifies:
- Library version matrix (13 environments)
- Contract types to test (structural, metamorphic from h-m1/h-m2)
- FPR thresholds (gate criteria)
- Corpus sampling strategy

**Design Principle**: Test "are contracts version-stable?" without hyperparameter tuning.

---

## 2. Inherited Configuration (From h-m1/h-m2)

### From h-m1 Structural Contracts

```python
# From: h-m1/code/contracts/validator.py
# Structural contract defaults (shapes, dtypes, non-null)
STRUCTURAL_CONFIG = {
    "shape_validation": {
        "enabled": True,
        "allow_batch_flexibility": True,  # Dynamic batch size OK
        "allow_dynamic_dims": False,  # Other dims must match exactly
        "timeout": 0.5  # seconds
    },
    
    "dtype_validation": {
        "enabled": True,
        "strict_mode": True,  # No implicit casts allowed
        "timeout": 0.3
    },
    
    "nonnull_validation": {
        "enabled": True,
        "check_gradients": False,  # Inference-only for PoC
        "timeout": 0.2
    }
}
```

### From h-m2 Metamorphic Contracts

```python
# From: h-m2/code/contracts/validator.py
# Metamorphic contract defaults (mathematical invariants)
METAMORPHIC_CONFIG = {
    "softmax_sum": {
        "enabled": True,
        "tolerance": 1e-6,  # Sum should be 1.0 ± 1e-6
        "dim": -1,  # Default softmax dimension
        "timeout": 0.5
    },
    
    "dropout_identity": {
        "enabled": True,
        "check_eval_mode": True,  # Dropout should be identity in eval()
        "timeout": 0.3
    },
    
    "layer_norm_mean": {
        "enabled": True,
        "mean_tolerance": 1e-5,  # Mean ≈ 0
        "std_tolerance": 1e-4,   # Std ≈ 1
        "timeout": 0.5
    }
}
```

**Verified from**: h-m1/h-m2 actual implementations (100% detection rate validated)

---

## 3. Version Matrix Configuration

**Applied**: ±2 minor version coverage (from PRD semantic versioning requirements)

```python
# version_matrix_config.py
VERSION_MATRIX = {
    # PyTorch versions (6 total)
    "pytorch": {
        "versions": [
            "2.1.0",  # Baseline
            "2.1.2",  # Patch (control)
            "2.2.0",  # +1 minor
            "2.2.2",  # +1 minor + patch
            "2.3.0",  # +2 minors
            "2.3.1"   # +2 minors + patch
        ],
        "version_pairs": [
            # Forward transitions
            ("2.1.0", "2.2.0"),  # +1 minor
            ("2.1.0", "2.3.0"),  # +2 minors
            ("2.2.0", "2.3.0"),  # +1 minor
            # Rollback transitions
            ("2.3.0", "2.2.0"),  # -1 minor (test backward compat)
            # Patch control
            ("2.1.0", "2.1.2")   # +2 patches (should have FPR ≈ 0%)
        ],
        "install_command": "pip install torch=={version} --index-url https://download.pytorch.org/whl/cpu"
    },
    
    # HuggingFace Transformers versions (4 total)
    "transformers": {
        "versions": [
            "4.35.0",  # Baseline
            "4.36.0",  # +1 minor
            "4.37.0",  # +2 minors
            "4.38.0"   # +3 minors
        ],
        "version_pairs": [
            ("4.35.0", "4.36.0"),  # +1 minor
            ("4.35.0", "4.37.0"),  # +2 minors
            ("4.36.0", "4.38.0"),  # +2 minors
            ("4.37.0", "4.36.0")   # -1 minor (rollback)
        ],
        "install_command": "pip install transformers=={version}"
    },
    
    # NumPy versions (3 total, dtype contract stability focus)
    "numpy": {
        "versions": [
            "1.24.0",  # Baseline
            "1.25.0",  # +1 minor
            "1.26.0"   # +2 minors
        ],
        "version_pairs": [
            ("1.24.0", "1.25.0"),  # +1 minor
            ("1.24.0", "1.26.0"),  # +2 minors
            ("1.25.0", "1.24.0")   # -1 minor (rollback)
        ],
        "install_command": "pip install numpy=={version}"
    },
    
    # Environment settings (consistent across all versions)
    "environment": {
        "python_version": "3.10",
        "cuda_version": "12.1",  # Fixed to prevent numerical drift
        "conda_channels": ["conda-forge", "defaults"],
        "additional_packages": ["pytest", "pandas", "matplotlib"]
    }
}

# Total environments: 6 (PyTorch) + 4 (HF) + 3 (NumPy) = 13
# Total version pairs: 5 + 4 + 3 = 12
```

---

## 4. Contract Injection Configuration

**Applied**: AST-based decorator injection (from Logic Design L-2)

```python
# contract_injection_config.py
INJECTION_CONFIG = {
    # Contract types to inject
    "contract_types": ["structural", "metamorphic"],
    
    # Injection strategies
    "structural_injection": {
        "target_methods": ["forward"],  # nn.Module.forward
        "target_classes": ["nn.Module"],
        "decorator": "@validate_structural",
        "import_statement": "from contracts.validator import validate_structural"
    },
    
    "metamorphic_injection": {
        "target_functions": ["softmax", "dropout", "layer_norm"],
        "decorator": "@validate_metamorphic",
        "import_statement": "from contracts.validator import validate_metamorphic"
    },
    
    # AST manipulation settings
    "ast_parser": {
        "python_version": (3, 10),
        "error_handling": "skip",  # Skip unparseable scripts
        "preserve_formatting": False  # Reformatted by astor
    },
    
    # Injection validation
    "validate_injection": True,  # Parse annotated code to verify correctness
    "dry_run_mode": False  # If True, inject but don't execute
}
```

---

## 5. Corpus Configuration

**Applied**: Stratified sampling from real-world codebases (no synthetic data)

```python
# corpus_config.py
CORPUS_CONFIG = {
    # PyTorch Hub models (N=200)
    "pytorch_hub": {
        "source": "https://github.com/pytorch/vision/tree/main/torchvision/models",
        "total_scripts": 200,
        "architectures": ["resnet", "vgg", "densenet", "efficientnet", "mobilenet"],
        "sampling_strategy": "all_available",  # Use all PyTorch Hub scripts
        "script_types": ["model_loading", "inference", "feature_extraction"],
        "min_stars": 5000,  # PyTorch/vision repo quality threshold
        "include_pretrained": True
    },
    
    # HuggingFace Transformers examples (N=300)
    "huggingface_examples": {
        "source": "https://github.com/huggingface/transformers/tree/main/examples",
        "total_scripts": 300,
        "model_types": ["bert", "gpt2", "t5", "roberta", "distilbert"],
        "tasks": ["text_classification", "question_answering", "summarization"],
        "sampling_strategy": "stratified",  # 50 scripts per model type
        "min_stars": 10000,  # HF Transformers repo quality
        "include_tokenization": True
    },
    
    # GitHub ML scripts (N=500, curated)
    "github_scripts": {
        "source": "manual_curation",  # High-quality repos (≥1K stars)
        "total_scripts": 500,
        "repo_criteria": {
            "min_stars": 1000,
            "active_maintenance": True,  # Commit in last 6 months
            "no_syntax_errors": True,
            "resolvable_dependencies": True
        },
        "exclusions": [
            "deprecated_apis",  # Exclude scripts with known deprecations
            "syntax_errors",
            "missing_dependencies"
        ],
        "domains": ["computer_vision", "nlp", "reinforcement_learning"],
        "sampling_strategy": "diversity_maximization"  # Broad coverage
    },
    
    # Total corpus: 1000 scripts
    "total_scripts": 1000,
    
    # Contract distribution (3000 contract instances total)
    "contracts_per_script": 3,  # Average (some scripts have 1, others 5+)
    
    # Storage requirements
    "estimated_storage": "10 GB",  # <10 GB (no large datasets)
    "cache_directory": ".corpus_cache"
}
```

---

## 6. False Positive Rate (FPR) Configuration

**Applied**: Statistical rigor requirements (Wilson score CI, stratification)

```python
# fpr_config.py
FPR_CONFIG = {
    # Gate criteria (from PRD)
    "thresholds": {
        "overall_fpr": 0.05,  # <5% (MUST_WORK gate)
        "structural_fpr": 0.03,  # <3% (tighter bound for stable contracts)
        "metamorphic_fpr": 0.08,  # <8% (relaxed for numerical drift)
        "version_distance_sensitivity": "monotonic"  # FPR(±2) ≥ FPR(±1)
    },
    
    # Statistical analysis
    "confidence_interval": {
        "level": 0.95,  # 95% CI
        "method": "wilson_score",  # Better for proportions near 0
        "bootstrap_iterations": 1000  # For CI estimation
    },
    
    # Stratification
    "stratify_by": [
        "contract_type",  # structural vs metamorphic
        "library",  # pytorch vs transformers vs numpy
        "version_distance"  # ±1 minor, ±2 minors, rollback
    ],
    
    # Breakage categorization
    "breakage_types": [
        "api_deprecation",    # Contract references deprecated API
        "behavioral_change",  # API semantics changed (dtype, shape defaults)
        "numerical_drift",    # Floating-point precision changes
        "unknown"             # No clear root cause
    ],
    
    # False positive handling
    "log_all_fps": True,  # Save all FPs to CSV for analysis
    "categorize_fps": True,  # Apply heuristics for breakage type
    "analyze_root_cause": True  # Cross-reference with release notes
}
```

---

## 7. Execution Configuration

**Applied**: Parallel execution optimization (ProcessPoolExecutor)

```python
# execution_config.py
EXECUTION_CONFIG = {
    # Parallelization
    "parallel_workers": 8,  # ProcessPoolExecutor workers (CPU-bound)
    "execution_mode": "parallel",  # vs "sequential"
    
    # Timeouts
    "script_timeout": 30.0,  # seconds per script execution
    "environment_creation_timeout": 300.0,  # 5 minutes per conda env
    "total_benchmark_timeout": 172800.0,  # 48 hours max
    
    # Retry logic
    "max_retries": 2,  # Retry failed scripts (network errors, transient failures)
    "retry_delay": 5.0,  # seconds between retries
    
    # Logging
    "log_level": "INFO",  # DEBUG | INFO | WARNING | ERROR
    "log_file": "version_transition_benchmark.log",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
    # Checkpointing
    "checkpoint_enabled": True,
    "checkpoint_frequency": 100,  # Save checkpoint every 100 scripts
    "checkpoint_dir": ".checkpoints",
    "resume_from_checkpoint": True  # If interrupted, resume from last checkpoint
}
```

---

## 8. Output Configuration

**Applied**: Structured output for validation report generation

```python
# output_config.py
OUTPUT_CONFIG = {
    # Result files
    "output_dir": "docs/youra_research/h-c4/",
    
    "result_files": {
        "fpr_metrics": "fpr_results.json",  # Overall + stratified FPR
        "false_positives": "false_positives.csv",  # All FP instances
        "stability_matrix": "stability_matrix.csv",  # Heatmap data
        "breakage_analysis": "breakage_analysis.json",  # Root cause for each FP
        "validation_report": "04_validation.md"  # Final report
    },
    
    # Visualization
    "generate_plots": True,
    "plot_formats": ["png", "pdf"],
    "plots": {
        "fpr_heatmap": "fpr_heatmap_version_pairs.png",  # version_pair × contract_type
        "fpr_by_library": "fpr_by_library.png",  # Bar chart
        "fpr_by_distance": "fpr_by_version_distance.png",  # Line plot
        "breakage_distribution": "breakage_type_distribution.png"  # Pie chart
    },
    
    # Validation report format
    "report_sections": [
        "executive_summary",
        "methodology",
        "results",
        "statistical_analysis",
        "false_positive_case_studies",
        "contract_design_guidelines",
        "recommendations"
    ],
    
    # Export formats
    "export_formats": ["markdown", "json"],  # For automated processing
    "include_raw_data": False  # Don't include full execution logs in report
}
```

---

## 9. Environment-Specific Overrides

**Applied**: Per-library adjustments for known quirks

```python
# environment_overrides.py
ENVIRONMENT_OVERRIDES = {
    # PyTorch-specific settings
    "pytorch": {
        "2.1.0": {
            "requires_cpu_only": True,  # Avoid CUDA version conflicts
            "additional_packages": ["torchvision==0.14.0"]
        },
        "2.2.0": {
            "requires_cpu_only": True,
            "additional_packages": ["torchvision==0.15.0"]
        },
        "2.3.0": {
            "requires_cpu_only": True,
            "additional_packages": ["torchvision==0.16.0"],
            "known_issues": ["softmax dim parameter deprecated warnings"]
        }
    },
    
    # HuggingFace-specific settings
    "transformers": {
        "4.35.0": {
            "additional_packages": ["tokenizers==0.14.0", "datasets==2.14.0"]
        },
        "4.36.0": {
            "additional_packages": ["tokenizers==0.15.0", "datasets==2.15.0"],
            "known_issues": ["Unicode normalization behavior change"]
        },
        "4.38.0": {
            "additional_packages": ["tokenizers==0.16.0", "datasets==2.16.0"]
        }
    },
    
    # NumPy-specific settings
    "numpy": {
        "1.24.0": {
            "no_overrides": True
        },
        "1.25.0": {
            "known_issues": ["Dtype defaults changed for certain operations"]
        },
        "1.26.0": {
            "known_issues": ["Dtype promotion rules updated"]
        }
    }
}
```

---

## 10. Contract Design Guidelines Configuration

**Applied**: Pattern extraction from stability results

```python
# contract_patterns_config.py
CONTRACT_PATTERNS_CONFIG = {
    # High-stability patterns (target: ≥95% stability)
    "high_stability_patterns": [
        {
            "name": "abstract_invariants",
            "description": "Mathematical properties (softmax sum=1), not implementation details",
            "example": "@validate_metamorphic(property='softmax_sum', tolerance=1e-6)"
        },
        {
            "name": "tolerance_bands",
            "description": "Generous numerical tolerances (rtol=1e-5, not exact equality)",
            "example": "torch.allclose(output, expected, rtol=1e-5, atol=1e-7)"
        },
        {
            "name": "public_api_only",
            "description": "Validate public API behavior, not internal state",
            "example": "Check model(x).shape, not model._modules"
        }
    ],
    
    # Anti-patterns (target: <80% stability, avoid these)
    "anti_patterns": [
        {
            "name": "exact_numerical_equality",
            "description": "Fragile to kernel optimizations",
            "example": "output == expected  # AVOID: use torch.allclose instead"
        },
        {
            "name": "internal_state_inspection",
            "description": "Breaks on refactoring",
            "example": "model._buffers['running_mean']  # AVOID: use public API"
        },
        {
            "name": "deprecated_api_usage",
            "description": "Contracts must update with library deprecation cycles",
            "example": "torch.nn.functional.softmax(x)  # AVOID: requires dim parameter in 2.2+"
        }
    ],
    
    # Pattern extraction settings
    "extract_patterns_from_results": True,
    "minimum_pattern_frequency": 5,  # Pattern must occur ≥5 times
    "stability_threshold_high": 0.95,  # High-stability: ≥95%
    "stability_threshold_low": 0.80   # Anti-pattern: <80%
}
```

---

## 11. Validation Report Configuration

**Applied**: Structured report generation (from PRD Section 5.4)

```python
# validation_report_config.py
VALIDATION_REPORT_CONFIG = {
    # Report metadata
    "hypothesis_id": "h-c4",
    "hypothesis_statement": "Contracts remain stable across ±2 minor library versions with false positive rate <5%",
    "gate_type": "MUST_WORK",
    
    # Success criteria (from PRD)
    "success_criteria": {
        "overall_fpr": {"threshold": 0.05, "comparison": "less_than"},
        "structural_fpr": {"threshold": 0.03, "comparison": "less_than"},
        "metamorphic_fpr": {"threshold": 0.08, "comparison": "less_than"},
        "contract_stability": {"threshold": 0.90, "comparison": "greater_equal"}
    },
    
    # Report sections
    "include_executive_summary": True,
    "include_methodology": True,
    "include_results_tables": True,
    "include_statistical_analysis": True,
    "include_false_positive_case_studies": True,  # 10 representative FPs
    "include_contract_design_guidelines": True,
    "include_recommendations": True,
    
    # Formatting
    "max_case_studies": 10,  # Representative FP examples
    "table_format": "github_markdown",
    "include_code_snippets": True,
    "syntax_highlighting": "python"
}
```

---

## 12. Risk Mitigation Configuration

**Applied**: PRD Section 8 risk mitigations

```python
# risk_mitigation_config.py
RISK_MITIGATION_CONFIG = {
    # High FPR risk (>8%)
    "high_fpr_mitigation": {
        "fallback_strategy": "tune_numerical_tolerances",
        "tolerance_tuning_range": [1e-6, 1e-5, 1e-4],  # Test multiple tolerances
        "version_aware_contracts_enabled": True  # Add conditional logic by version
    },
    
    # Environment conflicts risk
    "environment_conflicts_mitigation": {
        "use_isolated_conda_envs": True,
        "cleanup_after_execution": False,  # Keep envs for debugging
        "verify_isolation": True  # Test for cross-contamination
    },
    
    # GitHub script curation time risk
    "curation_time_mitigation": {
        "fallback_corpus_size": 300,  # Reduce from 500 if time-constrained
        "automated_filtering": True,  # Syntax validation, dependency resolution
        "manual_review_sample_size": 50  # Manually review 10% sample
    },
    
    # CUDA version drift risk
    "cuda_drift_mitigation": {
        "fix_cuda_version": "12.1",
        "cpu_only_fallback": True,  # Use CPU if CUDA conflicts
        "verify_cuda_consistency": True  # Check CUDA version across envs
    },
    
    # Library installation failures risk
    "installation_failures_mitigation": {
        "use_conda_forge": True,  # Fallback for older versions
        "log_installation_errors": True,
        "skip_problematic_versions": False  # Document issues instead
    }
}
```

---

## 13. Complete Configuration Export

```python
# config.py (main configuration module)
from typing import Dict, Any


def get_config() -> Dict[str, Any]:
    """Export complete configuration."""
    return {
        "structural": STRUCTURAL_CONFIG,
        "metamorphic": METAMORPHIC_CONFIG,
        "version_matrix": VERSION_MATRIX,
        "injection": INJECTION_CONFIG,
        "corpus": CORPUS_CONFIG,
        "fpr": FPR_CONFIG,
        "execution": EXECUTION_CONFIG,
        "output": OUTPUT_CONFIG,
        "environment_overrides": ENVIRONMENT_OVERRIDES,
        "contract_patterns": CONTRACT_PATTERNS_CONFIG,
        "validation_report": VALIDATION_REPORT_CONFIG,
        "risk_mitigation": RISK_MITIGATION_CONFIG
    }


# Usage in experiment harness:
# from config import get_config
# CONFIG = get_config()
# benchmark = VersionTransitionBenchmark(CONFIG)
# results = benchmark.run()
```

---

## 14. Configuration Validation

```python
# config_validator.py
def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration before experiment run."""
    
    # Check version matrix completeness
    assert len(config["version_matrix"]["pytorch"]["versions"]) == 6
    assert len(config["version_matrix"]["transformers"]["versions"]) == 4
    assert len(config["version_matrix"]["numpy"]["versions"]) == 3
    
    # Check FPR thresholds
    assert config["fpr"]["thresholds"]["overall_fpr"] < 0.05
    assert config["fpr"]["thresholds"]["structural_fpr"] < 0.03
    assert config["fpr"]["thresholds"]["metamorphic_fpr"] < 0.08
    
    # Check corpus size
    total_scripts = sum([
        config["corpus"]["pytorch_hub"]["total_scripts"],
        config["corpus"]["huggingface_examples"]["total_scripts"],
        config["corpus"]["github_scripts"]["total_scripts"]
    ])
    assert total_scripts == 1000
    
    # Check parallelization settings
    assert 1 <= config["execution"]["parallel_workers"] <= 16
    
    return True
```

---

**Configuration Status:** APPROVED  
**Next Phase:** Phase 4 - Implementation (Code Generation)  
**Estimated Duration:** 1 week (environment setup + execution + analysis)
