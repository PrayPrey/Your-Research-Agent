# Discussion

## The Training-Generation Gap

Our central finding is negative: BiDPO training creates gradient pressure toward collaboration patterns, but this pressure does not transfer to generation-time behavior at PoC scale. The mechanism is sound (orthogonal signal, stable training), but the downstream effect is null.

Why might this occur?

**Hypothesis 1: Insufficient Training Duration.** PoC-scale training (250 steps on 4000 samples) is designed to test stability, not efficacy. Full-scale training (1 epoch on 170K samples, ~10K steps) may be necessary for behavioral change to manifest. This is the most likely explanation—training scale is a known factor in fine-tuning effectiveness.

**Hypothesis 2: Suboptimal λ Weighting.** We tested only λ = 0.5. The agency signal may require stronger weighting (λ > 0.5) to overcome the dominant preference signal, or weaker weighting (λ < 0.5) to avoid interference with DPO.

**Hypothesis 3: Heuristic Limitations.** The collaboration score uses pattern matching for reasoning traces and uncertainty markers. These patterns may not correspond to behaviors the model can learn to produce—or may capture surface features rather than genuine agency preservation.

**Hypothesis 4: Generation Parameters.** Temperature = 0.7 and top-p = 0.9 introduce sampling stochasticity that may wash out subtle behavioral differences. Lower temperature might reveal trained behaviors.

## Limitations

**PoC Scale Only.** All training used 250 steps on 4000 samples. Results may differ at full scale.

**Single Model Architecture.** We tested only Mistral-7B-Instruct-v0.2. Findings may not generalize to other model sizes or architectures.

**Single λ Value.** Only λ = 0.5 was tested. The optimal weighting is unknown.

**Heuristic-Based Scoring.** The collaboration score uses regex patterns, not learned representations. This enables interpretability but may miss genuine agency behaviors not captured by our heuristics.

**Blocked Downstream Evaluation.** MT-Bench and TruthfulQA experiments were not executed due to E3 failure. We cannot make claims about dialogue quality or factual accuracy.

## Value of Negative Results

This negative result contributes to alignment research by:

1. **Demonstrating mechanism feasibility:** Agency signals can be extracted orthogonally and integrated into DPO training. The infrastructure works.

2. **Identifying the failure point:** Training-generation transfer is the bottleneck, not signal extraction or training stability.

3. **Informing future work:** The specific failure mode (null generation effect at PoC scale) suggests concrete next steps rather than abandoning the approach.

## Broader Implications

Multi-objective alignment is appealing: add auxiliary objectives for safety, truthfulness, or agency preservation. Our results suggest this approach is more complex than "add loss term, get behavior." Training signals may require sufficient duration, careful weighting, or learned (rather than heuristic) objectives to transfer to generation.

This finding is relevant beyond BiDPO. Any auxiliary objective—whether for agency preservation, explanation quality, or other response properties—faces the same challenge: will training-time gradient pressure produce inference-time behavioral change?
