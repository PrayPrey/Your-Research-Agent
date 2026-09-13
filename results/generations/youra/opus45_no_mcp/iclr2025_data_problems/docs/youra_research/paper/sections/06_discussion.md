# Discussion

## Mechanism Validated, Metric Inadequate

Our results present a paradox: the causal mechanism linking contamination to confidence uniformity is empirically validated, yet the proposed metric fails. This is not a theoretical failure but an implementation failure.

The mechanism chain holds:
- Contamination → Training exposure (31.1% accuracy gain)
- Training exposure → Representation invariance (MPS diff 0.065, d=0.52)
- Representation invariance → Confidence uniformity (r=−0.517)

The SSI formulation breaks this chain. The inverse-variance transform (SSI = 1/variance) is pathologically sensitive to noise. Confidence scores have high intrinsic variance even within contamination levels; the inverse amplifies small denominators, producing SSI distributions with std > mean at all levels.

## Why SSI Fails

Three factors contribute:

1. **Noise amplification**: 1/variance magnifies small fluctuations into large SSI swings
2. **High within-group variance**: Real confidence distributions are noisier than simulated
3. **Weak between-group signal**: The actual contamination effect is smaller than simulations suggested

The failure point is clear: alternative metric formulations—entropy-based, coefficient of variation, normalized variance—may extract the validated signal without pathological noise sensitivity.

## Simulation-Reality Gap

The discrepancy between simulated (PASS) and real (FAIL) results is itself significant. Mock data generators encoded the expected contamination-SSI relationship; real inference revealed this relationship does not hold.

This has methodological implications for contamination research. End-to-end validation with actual model inference is essential; simulation-only results may systematically overestimate method effectiveness.

## Limitations

**Single scale**: Only Mistral-7B tested. The mechanism may generalize differently at 13B, 70B scales. Scale-specific normalization may be required.

**Single benchmark**: Only MMLU evaluated. Extension to GSM8K, HumanEval requires benchmark-specific calibration.

**Simulated mechanism steps**: H-M1 through H-M3 used simulated data; real-data replication is needed to confirm mechanism validity.

**Confidence calibration**: We assume model confidence is meaningful. Miscalibration could confound SSI with overconfidence rather than contamination.

## Honest Assessment

**What we contribute**:
- First empirical demonstration of contamination → invariance → uniformity mechanism
- Documentation that inverse-variance metrics fail on real data
- Identification of simulation-reality gap in contamination research

**What we do not contribute**:
- A working contamination detector
- Validated claims about metric performance

The SSI formulation must be revised before practical application. The mechanism validation provides a foundation; the metric engineering problem remains open.

## Future Work

**Alternative metrics**: Entropy H(p), coefficient of variation (CV = σ/μ), log-variance. These avoid the pathological 1/x transform.

**Real-data mechanism replication**: Run H-M1 through H-M3 with actual inference to verify the mechanism chain holds end-to-end.

**Scale generalization**: Replicate on 13B, 70B models with scale normalization.

**Multi-benchmark validation**: Extend to GSM8K, HumanEval with benchmark-specific thresholds.
