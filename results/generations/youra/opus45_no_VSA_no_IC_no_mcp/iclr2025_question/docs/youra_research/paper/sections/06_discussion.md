# Discussion

Our experiments reveal that token entropy and N-sample consistency capture orthogonal uncertainty signals for hallucination detection. We discuss the implications, surprising findings, and limitations of this work.

## Key Findings

**Finding 1: Orthogonality is stronger than expected.** With only 5% shared variance (r = 0.228), entropy and consistency measure fundamentally different phenomena. This suggests that prior work treating them interchangeably—or assuming one subsumes the other—misses significant signal.

*Implication:* Practitioners relying on a single uncertainty measure leave substantial predictive information on the table. Multi-signal approaches are theoretically justified.

**Finding 2: Consistency shows large discriminative power.** Cohen's d = 1.068 indicates approximately one standard deviation of separation between correct and incorrect responses. This exceeds typical effect sizes in hallucination detection literature.

*Implication:* N-sample consistency is a powerful standalone signal for factuality detection, warranting its inclusion in production hallucination detection systems.

**Finding 3: Discordant cases reveal complementary failure modes.** On 18.1% of questions, entropy and consistency disagree—and each method achieves AUROC > 0.75 on its winning subset.

*Implication:* A hybrid detector combining both signals could improve coverage by capturing failure modes that neither signal detects alone.

## Mechanistic Interpretation

Our results support a dual-signal model of LLM uncertainty:

- **Entropy captures epistemic uncertainty:** When the model lacks knowledge, its next-token distribution becomes diffuse. High entropy signals "I don't know the answer."

- **Consistency captures generation stability:** When knowledge is unstable or fabricated, repeated sampling produces divergent outputs. Low consistency signals "I'm making this up."

These are distinct failure patterns. A model may be confident but inconsistent (entropy low, consistency low)—perhaps confabulating with conviction. Conversely, a model may be uncertain but stable (entropy high, consistency high)—perhaps hedging with consistent phrasing.

The quadrant analysis (Figure 3) reveals this structure empirically. Both off-diagonal quadrants contain substantial question populations where only one signal flags a problem.

## Surprising Findings

**Large consistency effect size.** We observed d = 1.068, exceeding SelfCheckGPT-era estimates (d ~ 0.3-0.5) by 2-3×. We hypothesize this reflects:

1. TruthfulQA's adversarial design elicits more extreme hallucinations than naturally-occurring errors
2. Temperature=1.0 maximizes sampling diversity, revealing underlying instability

**High subset AUROC.** Both discordant subsets show AUROC > 0.75, substantially exceeding our threshold (0.6). This suggests genuine complementarity rather than noise—each method captures systematic failure modes the other misses.

## Limitations

**Single model (LLaMA-2-7B).** Our results may not generalize to other architectures (encoder-decoder, GPT-family) or scales (1B, 70B). Effect sizes and orthogonality may vary with model capacity.

*Why acceptable:* LLaMA-2-7B is a representative decoder-only LLM. Methodology validation on one model establishes the approach; cross-model replication is future work.

**Single benchmark (TruthfulQA).** The adversarial design may inflate effect sizes compared to naturally-occurring hallucinations. Results may not transfer to benign QA settings.

*Why acceptable:* TruthfulQA is the standard factuality benchmark with clean binary labels. Our goal is methodology validation; generalization studies are future work.

**Hybrid detector not tested.** While we demonstrate orthogonality and complementarity, we have not built or evaluated a combined detector. The ≥3pp AUROC improvement hypothesis (P1) remains untested.

*Why acceptable:* Orthogonality must be established before hybrid development is justified. This paper provides that foundation; hybrid implementation is the natural next step.

**Fixed hyperparameters (N=5, T=1.0).** Different sample counts or temperatures may yield different effect sizes.

*Why acceptable:* Parameters follow SelfCheckGPT precedent for comparability. Hyperparameter sensitivity analysis is future work.

## Broader Impact

**Positive impacts:** Improved hallucination detection can reduce misinformation from LLM-generated content, particularly in high-stakes domains (medical, legal, scientific). Multi-signal approaches offer more robust detection than single-signal methods.

**Potential concerns:** Hallucination detection could enable adversarial attacks that evade detection by targeting specific signals. We recommend combining multiple orthogonal signals precisely to make such evasion more difficult.

**Mitigation:** Our methodology is transparent and reproducible, enabling independent verification. We do not provide attack tools or evasion strategies.

## Future Work

1. **Build and evaluate hybrid detector:** Combine entropy and consistency with learned weighting; measure AUROC improvement over single signals.

2. **Cross-model replication:** Test orthogonality on Mistral-7B, LLaMA-3-8B, and larger scales (13B, 70B).

3. **Non-adversarial benchmarks:** Replicate on Natural Questions, MMLU to assess generalization to benign QA.

4. **Parameter sensitivity:** Ablate N ∈ {3, 5, 10, 20} and temperature ∈ {0.7, 0.8, 1.0} to assess robustness.

5. **Long-form generation:** Extend methodology to summarization and explanation tasks where entropy aggregation may need adaptation.
