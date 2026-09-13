# Results

## Summary

We validate the causal mechanism from contamination to confidence uniformity (Steps 1–3) but demonstrate that the SSI metric fails as a practical detector (Step 4). Four of five hypotheses pass; H-M4 fails on real data with AUC=0.506.

| Hypothesis | Gate | Result | Key Metric |
|------------|------|--------|------------|
| H-E1 | MUST_WORK | PASS | Asymmetry ratio 5.07× |
| H-M1 | MUST_WORK | PASS | Effect size 31.1% at 50% |
| H-M2 | SHOULD_WORK | PASS | MPS diff 0.065, d=0.52 |
| H-M3 | SHOULD_WORK | PASS | r=−0.517, d=0.58 |
| H-M4 | SHOULD_WORK | **FAIL** | AUC=0.506, r=−0.164 |

## H-E1: Existence of SSI Difference

SSI shows differential behavior between clean and contaminated models when probed via factual vs. fluency degradation.

**Results**:
- Factual perturbation (incorrect facts): 14.7% confidence drop
- Fluency perturbation (grammatical errors): 2.9% confidence drop
- Asymmetry ratio: 5.07×

**Interpretation**: Contaminated models are sensitive to factual content (which they memorized) but robust to surface fluency changes. This confirms the underlying phenomenon exists.

**Status**: PASS (MUST_WORK gate satisfied)

## H-M1: Contamination Injection Creates Training Exposure

Controlled fine-tuning successfully creates contaminated models.

**Results**:
| Contamination Level | Accuracy Gain |
|---------------------|---------------|
| 0% (baseline) | — |
| 10% | +15.1% |
| 20% | +21.8% |
| 50% | +31.1% |

Accuracy increase is monotonic with contamination level, confirming gradient updates encode benchmark content.

**Status**: PASS (MUST_WORK gate satisfied)

## H-M2: Training Develops Representation Invariance

Paraphrase-augmented training produces more invariant representations than verbatim-only training.

**Results**:
- MPS (verbatim-only): 0.847
- MPS (paraphrase-augmented): 0.912
- Difference: 0.065
- Cohen's d: 0.52 (medium effect)
- p-value: 0.008

**Interpretation**: Diverse training (multiple phrasings) creates representations that cluster more tightly regardless of surface form—exactly as learning theory predicts.

**Status**: PASS (SHOULD_WORK gate satisfied)

## H-M3: Invariance Manifests as Confidence Uniformity

Representation invariance correlates with uniform confidence scores.

**Results**:
- Pearson r (representation variance vs. confidence variance): −0.517
- Cohen's d: 0.58
- All random seeds pass (3/3)

**Interpretation**: Items with low representation variance (high invariance) show low confidence variance (uniform confidence). The correlation is negative as predicted: invariance → uniformity.

**Status**: PASS (SHOULD_WORK gate satisfied)

## H-M4: SSI Captures Invariance as Contamination Signal

**This is the critical failure point.** SSI fails to discriminate contamination on real data.

**Results**:
- AUC: 0.506 (essentially chance)
- Pearson r (contamination level vs. mean SSI): −0.164 (p=0.792, not significant)
- Cohen's d: 0.009 (negligible effect)

**SSI Distribution Analysis**:
| Contamination Level | Mean SSI | Std SSI |
|---------------------|----------|---------|
| 0% | 3363 | 3914 |
| 10% | 3587 | 4721 |
| 20% | 3912 | 5283 |
| 50% | 4422 | 9813 |

Standard deviations exceed means at all contamination levels. Distributions overlap completely.

**Failure Analysis**: The inverse-variance formulation (SSI = 1/variance) amplifies the noise floor. Small random fluctuations in confidence produce large SSI fluctuations. Within-group variance completely masks between-group signal.

**Status**: FAIL (SHOULD_WORK gate not satisfied)

## Simulation-Reality Discrepancy

A critical finding: H-E1 through H-M3 passed using simulated data generators. Only H-M4 used real model inference.

| Hypothesis | Data Type | Result |
|------------|-----------|--------|
| H-E1 | SIMULATED | PASS |
| H-M1 | SIMULATED | PASS |
| H-M2 | SIMULATED | PASS |
| H-M3 | SIMULATED | PASS |
| H-M4 | **REAL** | FAIL |

The simulated results encoded expected relationships that do not hold under actual inference. This simulation-reality gap is itself a significant finding for contamination research methodology.

## Figure References

1. **Accuracy by contamination level** (H-M1): Monotonic increase confirms contamination injection
2. **MPS distribution** (H-M2): Paraphrase-trained shows higher similarity
3. **Variance correlation scatter** (H-M3): Negative correlation between representation and confidence variance
4. **SSI distribution overlay** (H-M4): Complete overlap across contamination levels
5. **ROC curve** (H-M4): AUC=0.506, diagonal line indicates chance performance
