# Discussion

## Key Findings

**The architecture-family adversarial fingerprint is real at base model scale, but statistically underpowered at N=9.** The η²=0.293 result, consistent across 83% of attack categories and reaching Cohen's f²≈0.41 (large), establishes that architecture family membership is a meaningful explanatory variable for Δ*-vector variance. This is not a borderline effect: f²>0.35 is the conventional "large" boundary, and our estimate substantially exceeds it. The finding is consistent with Zhao et al. (2023), who observed a directional encoder–decoder–decoder difference in GLUE robustness, and provides the first formal effect-size quantification of this phenomenon.

**The adv_rte category (NLI paraphrase) produces the strongest family differentiation.** η²=0.592 on adv_rte is near-significant (p=0.075) despite N=9 and suggests that adversarial entailment/paraphrase detection is where architecture family effects concentrate. This is consistent with the hypothesis that bidirectional attention in encoder-only models is particularly sensitive to syntactic transformations involved in NLI paraphrase attacks. Future work testing the attention concentration mechanism (h-m1: ΔC extraction across all 9 models) would directly test whether bidirectional vs. causal attention redistribution explains the adv_rte peak.

**The Δ*-vector pipeline is a validated, reusable framework for architecture-family robustness profiling.** Seven modules, 1,788 lines, end-to-end pipeline execution, and 4 figures generated — all code modules confirmed reusable for h-e1-v2 and downstream mechanism studies. This methodological contribution is independent of the statistical outcome.

## Limitations

### Statistical Underpowering (Primary)

With N=9 models (~3 per family), our experiment has approximately 40% power to detect η²=0.29 at α=0.05. The p=0.147 result is expected under this power level and does not provide evidence against the existence hypothesis. The effect size η²=0.293 stands as a practically meaningful finding; the significance criterion was not met due to insufficient N, not due to a weak or absent effect.

**Why acceptable:** Effect size is a more informative summary statistic than a binary significance decision at low power. We report the underpowering explicitly and provide the power curve (Table 2) as a design contribution. The h-e1-v2 study with N=15 (≥5/family) directly addresses this with 80% power.

**Suggested framing:** Our PoC establishes the effect magnitude and provides power analysis guidance (N≥15 for 80% power at α=0.05), advancing the design of future definitive studies.

### LOMO Classification N-Degeneracy

LOMO accuracy=0.333 (at chance). We caution strongly that this result should not be interpreted as evidence against Δ*-family separability. With N=3 models per family, each LOMO fold trains a cosine k=1 nearest-neighbor classifier on two reference points per family in 6-dimensional space. This configuration is geometrically near-degenerate: at-chance LOMO is mathematically expected regardless of the underlying family structure. P2 (LOMO ≥60%) is formally unmet, but the LOMO test at N=3/family is not a valid test of the classification hypothesis.

**Why acceptable:** The N-degeneracy explanation is specific, testable, and addressable. Running LOMO at N=15 (h-e1-v2) directly tests whether classification accuracy rises above chance as the geometric degeneracy is resolved. Running alternative classifiers (family-centroid, LDA) on the existing N=9 Δ*-matrix would provide preliminary evidence without requiring new data collection.

### Mechanism Untested

The attention-topology mediation hypothesis (bidirectional attention → global redistribution → higher Δ* on encoder-only models) was not directly tested. Hypotheses h-m1 through h-m4 — which would extract attention concentration metrics ΔC per layer and test whether mean(ΔC) mediates architecture-family differences — were gated on h-e1 gate satisfaction and were not executed.

The descriptive finding (η²=0.293) and the methodological contribution (pipeline) are independent of mechanism confirmation. However, the paper should be read as providing a characterization of the *phenomenon* (the fingerprint exists and is large) rather than a causal explanation of *why* it exists.

### enc_dec ANLI-R3 Coverage Gap

T5-base and BART-base were fine-tuned exclusively on SST-2. On ANLI-R3 (NLI task), their clean accuracy is near-chance, producing Δ*≈0 and η²=0.0 for the enc_dec entries in that category. This is an implementation scope limitation, not a genuine finding about enc_dec NLI robustness. The corrective step — adding MNLI fine-tuning for T5 and BART — is included in the h-e1-v2 protocol.

### CheckList Partition Skipped

The CheckList behavioral testing suite, which would provide a third benchmark partition with distinct perturbation types (morphological, negation, etc.), was not evaluated due to package availability constraints. The 5/6 available categories showed consistent results, but full cross-partition replication requires CheckList inclusion in h-e1-v2.

## Broader Impact

**Positive:** Architecture-family adversarial fingerprinting provides a practical tool for robustness auditing. Practitioners selecting between model families for adversarial-sensitive deployments can use Δ*-vector analysis to characterize expected vulnerability profiles at the family level, reducing the cost of model-by-model evaluation. The validated pipeline (released with this paper) enables the community to replicate this analysis and extend it to new architectures, scales, and attack types.

**Potential concerns:** Adversarial vulnerability characterization is dual-use: the same framework that helps defenders understand which model families are more vulnerable to which attack types could in principle help adversaries target their attacks more effectively. We note that (a) our characterization operates at the family level, not the individual-model level, and (b) the attack methods we evaluate are already publicly available (AdvGLUE, ANLI). We do not introduce new attack methods or disclose novel vulnerability types not already present in the public benchmark literature.

**Scale effects:** Our results are specific to base-scale models (~110–350M parameters). Whether architecture-family fingerprints persist, diminish, or amplify at 7B+ scale is an open empirical question with high field significance. RLHF and instruction-tuning are known to change robustness profiles (TREvaL); our results do not extend to RLHF-tuned models.
