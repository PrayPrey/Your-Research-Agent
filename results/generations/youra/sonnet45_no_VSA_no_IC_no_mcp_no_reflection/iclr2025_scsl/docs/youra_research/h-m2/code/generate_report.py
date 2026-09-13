"""
Generate 04_validation.md report for h-m2.
"""

import json
import os
from datetime import datetime


def generate_validation_report(results_path: str, output_path: str):
    """Generate validation report from experiment results."""

    with open(results_path, 'r') as f:
        results = json.load(f)

    gate_status = results.get('gate_status', 'UNKNOWN')
    resnet = results.get('resnet50', {})
    vit = results.get('vit_b16', {})
    comparison = results.get('comparison', {})

    # Build report
    report = f"""# Validation Report: h-m2

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Hypothesis:** CNNs show larger temporal gaps than Vision Transformers (Δ_ResNet > Δ_ViT by ≥2 epochs)
**Gate Type:** SHOULD_WORK
**Gate Result:** {gate_status}

---

## Experimental Setup

**Dataset:** CMNIST (Colored MNIST, 10% subset)
**Architectures:**
- ResNet-50 (from-scratch training)
- ViT-B/16 (from-scratch training)

**Training Configuration:**
- Optimizer: SGD (momentum=0.9)
- ResNet LR: 0.001, Batch size: 128
- ViT LR: 0.0003, Batch size: 128
- Max epochs: 30
- Convergence criterion: 90% train accuracy

**Ablation Setup:**
- Spurious-only: Gaussian blur (kernel=15)
- Core-only: Grayscale conversion

---

## Results

### ResNet-50

| Metric | Value |
|--------|-------|
| E_spurious | {resnet.get('E_spurious', 'N/A')} epochs |
| E_core | {resnet.get('E_core', 'N/A')} epochs |
| Δ_ResNet | {resnet.get('delta', 'N/A')} epochs |

### ViT-B/16

| Metric | Value |
|--------|-------|
| E_spurious | {vit.get('E_spurious', 'N/A')} epochs |
| E_core | {vit.get('E_core', 'N/A')} epochs |
| Δ_ViT | {vit.get('delta', 'N/A')} epochs |

### Comparison

| Metric | Value |
|--------|-------|
| Δ_ResNet - Δ_ViT | {comparison.get('diff', 'N/A')} epochs |
| Gate threshold | ≥ 2 epochs |
| Gate met | {'✓ YES' if gate_status == 'PASS' else '✗ NO'} |

---

## Gate Evaluation

**Gate:** SHOULD_WORK
**Criterion:** Δ_ResNet - Δ_ViT ≥ 2 epochs

**Outcome:**
"""

    if gate_status == 'PASS':
        report += f"""✓ **PASS**: Temporal gap difference ({comparison.get('diff', 'N/A'):.2f} epochs) meets threshold.

**Interpretation:** ResNet-50 shows larger temporal gaps than ViT-B/16, supporting the hypothesis that CNN inductive biases create stronger preference for spurious features early in training.
"""
    else:
        report += f"""✗ **FAIL**: Temporal gap difference ({comparison.get('diff', 'N/A'):.2f} epochs) below threshold.

**Interpretation:** Hypothesis not supported. Architecture differences do not produce ≥2 epoch gap in temporal ordering.

**Routing Decision:** SHOULD_WORK gate failure does not block Phase 5. Proceed with baseline comparison.
"""

    report += f"""
---

## Figures

![Comparison Plot](../figures/resnet_vs_vit_comparison.png)

---

## Next Steps

{
    'Proceed to Phase 5 baseline comparison with validated h-e1 temporal gap metric.'
    if gate_status == 'PASS'
    else 'SHOULD_WORK gate failure. Document findings and proceed to Phase 5 (gate does not block).'
}

---

**Status:** COMPLETED
**Validation Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # Write report
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Validation report generated: {output_path}")


if __name__ == '__main__':
    os.makedirs('../h-m2', exist_ok=True)
    generate_validation_report(
        '../results/full_results.json',
        '../../h-m2/04_validation.md'
    )
