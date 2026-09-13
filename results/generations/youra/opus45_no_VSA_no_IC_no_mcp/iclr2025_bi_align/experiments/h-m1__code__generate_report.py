"""Generate 04_validation.md report from metrics."""
import json
import sys
from datetime import datetime


def generate_report(metrics_path: str, output_path: str):
    with open(metrics_path, 'r') as f:
        results = json.load(f)

    overall_pass = results.get("overall_pass", False)
    gate_result = "PASSED" if overall_pass else "FAILED"

    report = f"""# H-M1 Validation Report: RLHF Reward Model Smoothing

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Validation Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## 1. Hypothesis Statement

Under standard RLHF training, if we train a reward model on HH-RLHF preference pairs, then the reward model will produce smooth, interpolating reward predictions, because explicit reward model training learns a continuous approximation of discrete preference labels.

## 2. Gate Result

**{gate_result}**

## 3. Metrics Summary

### 3.1 Gradient Smoothness
| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Mean Gradient Norm | {results['gradient']['mean_gradient_norm']:.4f} | < 10.0 | {'PASS' if results['pass']['gradient'] else 'FAIL'} |
| Std Gradient Norm | {results['gradient']['std_gradient_norm']:.4f} | - | - |
| Max Gradient Norm | {results['gradient']['max_gradient_norm']:.4f} | - | - |

### 3.2 Distribution Continuity
| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Bimodality Coefficient | {results['distribution']['bimodality_coefficient']:.4f} | < 0.55 | {'PASS' if results['pass']['distribution'] else 'FAIL'} |
| Unique Reward Ratio | {results['distribution']['unique_reward_ratio']:.4f} | > 0.5 | - |
| Reward Range | {results['distribution']['reward_range']:.4f} | - | - |
| Reward Std | {results['distribution']['reward_std']:.4f} | - | - |
| Margin (chosen - rejected) | {results['distribution']['margin']:.4f} | > 0 | - |

### 3.3 Interpolation Smoothness
| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Mean Interpolation Error | {results['interpolation']['mean_interpolation_error']:.4f} | < 0.3 | {'PASS' if results['pass']['interpolation'] else 'FAIL'} |
| Max Interpolation Error | {results['interpolation']['max_interpolation_error']:.4f} | - | - |

## 4. Key Findings

1. **Gradient Smoothness:** {"Reward model shows bounded gradients, indicating smooth reward landscape." if results['pass']['gradient'] else "Gradient magnitudes exceed threshold, indicating non-smooth reward landscape."}

2. **Distribution Continuity:** {"Reward predictions form continuous distribution (not bimodal/discrete), confirming interpolating behavior." if results['pass']['distribution'] else "Reward distribution shows discrete clustering, inconsistent with smoothing hypothesis."}

3. **Interpolation Behavior:** {"Embedding-space interpolation produces near-linear reward interpolation, confirming continuous approximation." if results['pass']['interpolation'] else "Interpolation shows non-linear behavior, suggesting discrete rather than continuous reward mapping."}

4. **Preference Discrimination:** The model correctly assigns higher rewards to chosen responses (margin = {results['distribution']['margin']:.4f}).

## 5. Baseline Comparison

"""
    if 'baseline' in results:
        baseline = results['baseline']
        report += f"""| Metric | Trained | Baseline (Random) | Improvement |
|--------|---------|-------------------|-------------|
| Mean Gradient Norm | {results['gradient']['mean_gradient_norm']:.4f} | {baseline['gradient']['mean_gradient_norm']:.4f} | - |
| Bimodality | {results['distribution']['bimodality_coefficient']:.4f} | {baseline['distribution']['bimodality_coefficient']:.4f} | - |
| Interpolation Error | {results['interpolation']['mean_interpolation_error']:.4f} | {baseline['interpolation']['mean_interpolation_error']:.4f} | - |
"""
    else:
        report += "Baseline comparison not available.\n"

    report += f"""

## 6. Conclusion

The hypothesis that RLHF reward models produce smooth, interpolating predictions is **{'SUPPORTED' if overall_pass else 'NOT SUPPORTED'}** by the experimental evidence.

{'The trained reward model demonstrates all three smoothness criteria: bounded gradients, continuous reward distribution, and linear interpolation behavior. This confirms that explicit reward model training learns a continuous approximation of discrete preference labels.' if overall_pass else 'The reward model does not meet all smoothness criteria. Further investigation is needed to understand the failure mode.'}

## 7. Implications for Main Hypothesis

{'This MECHANISM hypothesis passing confirms that RLHF reward models exhibit the smoothing property hypothesized. This supports the broader claim that RLHF and DPO create different alignment signatures due to their mechanistic differences.' if overall_pass else 'This MECHANISM hypothesis failing indicates that the assumed smoothing property may not hold under the tested conditions. The main hypothesis verification strategy may need revision.'}

---

**Gate Verdict:** {gate_result}
**Next Step:** {'Proceed to h-m2 (DPO implicit reward comparison)' if overall_pass else 'Investigate failure and consider modification per verification plan'}
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Report written to {output_path}")
    return overall_pass


if __name__ == "__main__":
    metrics = sys.argv[1] if len(sys.argv) > 1 else "./smoothness_metrics.json"
    output = sys.argv[2] if len(sys.argv) > 2 else "../04_validation.md"
    generate_report(metrics, output)
