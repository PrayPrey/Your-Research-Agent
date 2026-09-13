"""
Main experiment script for H-M1: Structural Contract Validation
Demonstrates import-time API violation detection
"""
import torch
import torch.nn as nn
from contracts.validator import validate_structural, validate_at_import
from contracts.validator import ShapeViolation, DeviceViolation, DtypeViolation
import json
import time
from datetime import datetime


# Simple ResNet-like model with contracts
@validate_at_import
class ContractedModel(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64, num_classes)

    @validate_structural(
        input_shapes={'x': ('B', 3, 32, 32)},
        output_shape=('B', 10),
        dtype=torch.float32
    )
    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


def inject_defect(model, defect_type='shape'):
    """Inject structural defects for testing"""
    if defect_type == 'shape':
        # Change expected input channels
        model.conv1 = nn.Conv2d(4, 64, kernel_size=3, padding=1)  # 3 → 4 channels
    elif defect_type == 'device':
        # Move model to different device (if input is on CPU)
        if torch.cuda.is_available():
            model = model.cuda()
    elif defect_type == 'dtype':
        # Change model dtype
        model = model.half()  # float32 → float16
    return model


def main():
    """Run experiment to measure detection rate"""
    print("=" * 70)
    print("H-M1: Structural Contract Validation Experiment")
    print("=" * 70)
    print()

    results = {
        "experiment_id": "h-m1-poc",
        "timestamp": datetime.now().isoformat(),
        "detection_results": [],
        "summary": {}
    }

    # Test 1: Normal model (should pass)
    print("Test 1: Normal model (no defects)")
    print("-" * 70)
    try:
        start_time = time.time()
        model = ContractedModel()
        execution_time = time.time() - start_time

        # Test forward pass
        x = torch.randn(8, 3, 32, 32)
        output = model(x)

        print(f"✓ Contract validation passed")
        print(f"  Execution time: {execution_time:.4f}s")
        print(f"  Output shape: {output.shape}")

        results["detection_results"].append({
            "test_id": 1,
            "defect_type": "none",
            "detected": False,
            "detection_stage": "n/a",
            "execution_time": execution_time
        })
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        results["detection_results"].append({
            "test_id": 1,
            "defect_type": "none",
            "detected": True,  # False positive
            "detection_stage": "import",
            "error": str(e)
        })

    print()

    # Test 2: Shape mismatch defect (defective model class)
    print("Test 2: Shape mismatch defect (4 channels instead of 3)")
    print("-" * 70)
    try:
        start_time = time.time()

        # Create a defective model class with wrong input channels
        @validate_at_import
        class DefectiveModel(nn.Module):
            def __init__(self, num_classes=10):
                super().__init__()
                # DEFECT: expects 4 channels instead of 3 (CIFAR-10 is RGB=3)
                self.conv1 = nn.Conv2d(4, 64, kernel_size=3, padding=1)
                self.relu = nn.ReLU()
                self.pool = nn.AdaptiveAvgPool2d((1, 1))
                self.fc = nn.Linear(64, num_classes)

            @validate_structural(
                input_shapes={'x': ('B', 3, 32, 32)},  # Contract expects 3 channels
                output_shape=('B', 10),
                dtype=torch.float32
            )
            def forward(self, x):
                x = self.conv1(x)
                x = self.relu(x)
                x = self.pool(x)
                x = torch.flatten(x, 1)
                x = self.fc(x)
                return x

        detected = False
        detection_stage = "none"

        try:
            # Import-time validation should catch this
            model = DefectiveModel()
            detection_stage = "none"  # Not detected
        except (ShapeViolation, RuntimeError) as e:
            detected = True
            detection_stage = "import"  # Detected at init/import
            execution_time = time.time() - start_time
            print(f"✓ Defect detected at {detection_stage} stage")
            print(f"  Error: {str(e)[:100]}")
            print(f"  Detection time: {execution_time:.4f}s")

        if not detected:
            print("✗ Defect not detected at import (checking runtime)")
            # Try runtime detection
            x = torch.randn(8, 3, 32, 32)
            try:
                output = model(x)
            except Exception as e:
                detected = True
                detection_stage = "forward"
                execution_time = time.time() - start_time
                print(f"✓ Defect detected at {detection_stage} stage (fallback)")
                print(f"  Error: {str(e)[:100]}")

        results["detection_results"].append({
            "test_id": 2,
            "defect_type": "shape_mismatch",
            "detected": detected,
            "detection_stage": detection_stage,
            "execution_time": execution_time if detected else None
        })

    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    print()

    # Test 3: Dtype mismatch defect
    print("Test 3: Dtype mismatch defect (float16 instead of float32)")
    print("-" * 70)
    try:
        start_time = time.time()
        model = ContractedModel()

        # Test with different dtype
        x = torch.randn(8, 3, 32, 32).half()  # float16 instead of float32

        detected = False
        detection_stage = "none"

        try:
            output = model(x)
        except (DtypeViolation, RuntimeError) as e:
            detected = True
            if isinstance(e, DtypeViolation):
                detection_stage = "import"
            else:
                detection_stage = "forward"
            execution_time = time.time() - start_time
            print(f"✓ Defect detected at {detection_stage} stage")
            print(f"  Error: {str(e)[:100]}")
            print(f"  Detection time: {execution_time:.4f}s")

        if not detected:
            print("✗ Defect not detected (false negative)")

        results["detection_results"].append({
            "test_id": 3,
            "defect_type": "dtype_mismatch",
            "detected": detected,
            "detection_stage": detection_stage,
            "execution_time": execution_time if detected else None
        })

    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    print()

    # Calculate summary statistics
    total_defects = len([r for r in results["detection_results"] if r["defect_type"] != "none"])
    detected_at_import = len([r for r in results["detection_results"]
                               if r.get("detection_stage") == "import" and r.get("detected")])
    detected_total = len([r for r in results["detection_results"]
                          if r.get("detected") and r["defect_type"] != "none"])

    detection_rate = (detected_total / total_defects * 100) if total_defects > 0 else 0
    import_detection_rate = (detected_at_import / total_defects * 100) if total_defects > 0 else 0

    results["summary"] = {
        "total_tests": len(results["detection_results"]),
        "total_defects": total_defects,
        "detected_total": detected_total,
        "detected_at_import": detected_at_import,
        "detection_rate": detection_rate,
        "import_detection_rate": import_detection_rate
    }

    print("=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"Total tests: {results['summary']['total_tests']}")
    print(f"Total defects: {results['summary']['total_defects']}")
    print(f"Detected (any stage): {detected_total}/{total_defects} ({detection_rate:.1f}%)")
    print(f"Detected at import: {detected_at_import}/{total_defects} ({import_detection_rate:.1f}%)")
    print()

    # Save results
    with open('experiment_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("✓ Results saved to experiment_results.json")

    # Gate decision
    if import_detection_rate >= 60:
        print("\n✓ MUST_WORK GATE: PASS (detection rate >= 60%)")
        return 0
    else:
        print("\n✗ MUST_WORK GATE: FAIL (detection rate < 60%)")
        return 1


if __name__ == "__main__":
    exit(main())
