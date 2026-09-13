# Experimental Setup

We design experiments to answer the following research questions:

**RQ1:** Does the HIGH (categorical + continuous) reward condition reach pass@1 > 0.3 faster than the LOW (binary) condition?

**RQ2:** Does the MEDIUM (continuous) condition outperform the LOW (binary) condition in convergence speed?

**RQ3:** Does error-type distribution differ across conditions during training?

These questions directly test the information bandwidth hypothesis: if denser feedback accelerates learning, we should observe faster convergence and differential error patterns in higher-bandwidth conditions.

## Dataset

We train on MBPP (Mostly Basic Python Problems) and evaluate on a held-out validation subset:

**MBPP Training Set:**
- 374 sanitized programming problems
- Each problem includes natural language description, function signature, and test cases
- Standard benchmark for code generation research

**MBPP Validation Subset:**
- 50 problems held out for evaluation
- pass@1 computed as fraction of problems solved with greedy decoding

**Rationale:** MBPP provides execution-based feedback (tests pass or fail), enabling our reward signal comparison. The validation subset allows tracking pass@1 during training without contamination.

## Reward Conditions

We compare three reward conditions:

| Condition | Signal | Bits | Formula |
|-----------|--------|------|---------|
| LOW (Binary) | Pass/fail | 1 | $r = 1$ if all tests pass, else $0$ |
| MEDIUM (Continuous) | Test pass rate | ~1.5 | $r = n_{\text{passed}} / n_{\text{total}}$ |
| HIGH (Bandwidth) | Rate + error type | ~2 | $r = 0.5 \times \text{pass\_rate} + 0.5 \times \text{error\_score}$ |

**Why these conditions:** They span the information bandwidth spectrum from sparse (binary) to dense (categorical + continuous), allowing us to test whether feedback granularity affects learning dynamics.

## Model and Training

**Model:** CodeLlama-7B-Instruct
- 7 billion parameters
- Instruction-tuned for code generation
- Used in prior RLEF work (PPOCoder)

**Training Configuration:**
- Algorithm: REINFORCE with advantage baseline
- Optimizer: AdamW
- Learning rate: 1e-5 with linear decay
- Batch size: 4
- Epochs: 1 (PoC scale)
- Seeds per condition: 3

**Compute Resources:**
- GPU: NVIDIA A100 (40GB)
- Training time: ~2 hours per condition

## Evaluation Protocol

**Primary Metric:** pass@1 on validation subset
- Greedy decoding (temperature = 0)
- 50 problems evaluated per checkpoint

**Secondary Metrics:**
- Samples-to-threshold: training samples until pass@1 > 0.3
- Error-type distribution: proportion of syntax/runtime/assertion/pass per checkpoint

**Statistical Analysis:**
- Independent t-test for pairwise comparisons (HIGH vs LOW)
- Effect size: Cohen's d
- Significance threshold: p < 0.05

## PoC Scale Limitations

We acknowledge the PoC scale as a significant limitation:

- **1 epoch:** Likely insufficient for PPO policy improvement to emerge
- **3 seeds:** May not capture full variance across initializations
- **50-problem validation:** Small sample may not reflect true performance distribution

These limitations were accepted for rapid iteration. As we report in Results, they proved decisive—the scale was insufficient for ANY learning, making comparison impossible.
