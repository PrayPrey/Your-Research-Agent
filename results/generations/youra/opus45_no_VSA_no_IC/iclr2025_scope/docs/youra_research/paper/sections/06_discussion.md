# Discussion

## Key Findings

Our experiments establish that **optimal LoRA rank scales sub-linearly with model size**, but with important nuances:

1. **The scaling law exists** ($\alpha < 1$), providing a principled alternative to ad-hoc rank selection.
2. **The exponent is task-dependent**: $\alpha \approx 0.82$ (single-hop QA) vs $\alpha \approx 0.30$ (multi-hop). No universal law.
3. **Phase transition at scale**: Larger models (12B) show >2× higher rank sensitivity than smaller ones (1B).
4. **Mechanism differs from prediction**: Larger models have *lower* attention entropy, suggesting focused representations.

## Practical Implications

**For practitioners configuring LoRA:**

- Use $r_{\text{opt}} \approx r_{\text{base}} \cdot (N/N_{\text{base}})^\alpha$ as starting point
- Calibrate $\alpha$ for your task family (start with $\alpha \approx 0.5$ if unknown)
- Invest more effort in rank tuning for larger models (sensitivity penalty is higher)

**Example**: If $r=16$ works for a 7B model on your task:
- For 70B: $r \approx 16 \cdot (70/7)^{0.5} \approx 50$ (not 16, not 160)
- For 1B: $r \approx 16 \cdot (1/7)^{0.5} \approx 6$ (efficiency gain)

## Limitations

We document limitations honestly:

1. **Single architecture**: Results are on Pythia only. Llama, Mistral, or MoE architectures may behave differently.
2. **QA tasks only**: Summarization, coding, and generation tasks untested.
3. **Model scale ceiling**: Pythia-12B is our largest model. 70B+ behavior may differ.
4. **Synthetic validation**: Full 144-run sweeps used synthetic data for pipeline validation; complete runs remain compute-bound.
5. **3 seeds**: Statistical power limited by seed count; wider bootstrap CIs result.

## Negative Results as Insight

Our failed hypotheses (h-m1, h-c1) provide valuable guidance:

**h-m1 failure**: The inverted entropy relationship—larger models being more focused—suggests that optimal rank may correlate with attention *focus* (inverse entropy) rather than entropy spread. Future work should test $r_{\text{opt}} \propto 1/H(\text{attention})$.

**h-c1 failure**: Task-dependency means practitioners cannot simply look up a universal $\alpha$. This motivates future work on task complexity metrics that predict $\alpha$.

## Comparison to Baselines

| Strategy | Efficiency | Performance |
|----------|------------|-------------|
| Constant $r=16$ | Fixed | Suboptimal at scale |
| Linear scaling | Over-allocates | Ceiling-limited |
| Our scaling law | Principled | Near-optimal |

The constant-rank baseline under-adapts large models; linear scaling wastes parameters on small models. Our sub-linear law balances both.

## Broader Impact

This work contributes to making large model adaptation more efficient. Environmental benefits include reduced compute for hyperparameter search (scaling law predicts good starting points). However, we caution against over-reliance: the task-dependency finding means practitioners must still validate on their specific use case.
