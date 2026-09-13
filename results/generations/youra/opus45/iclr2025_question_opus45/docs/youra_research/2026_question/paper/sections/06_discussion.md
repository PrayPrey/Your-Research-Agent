# Discussion

Our results reveal that SE probing under a reasonable configuration fails completely. This section interprets these findings, acknowledges limitations, and discusses implications.

## Interpretation of Failure

The core finding is stark: layer 25 hidden states at the TBG position in Llama-3-8B-Instruct do not encode semantic entropy information that linear probes can extract. This contradicts the implicit assumption that SE information is broadly distributed across middle-to-late layers.

We propose three competing explanations for this failure:

**Hypothesis 1: Layer localization** — SE-relevant information may be concentrated in specific layers that we did not test. Layer 25 falls in the recommended range (middle-to-late), but the optimal layer for Llama-3-8B may differ from other models. Published work typically reports best configurations without characterizing the failure modes of suboptimal choices.

**Hypothesis 2: Token position sensitivity** — The TBG position captures the state before generation begins, but SE information may emerge during generation itself. Alternative positions (SLT, pooling across multiple tokens) may capture different information.

**Hypothesis 3: Implementation divergence** — Subtle differences in our pipeline versus published implementations may accumulate to large performance gaps. Response generation details, SE computation parameters, or preprocessing choices could all contribute.

We cannot distinguish these hypotheses with our current experiments. Each represents a direction for future investigation.

## Why Similarity Augmentation Did Not Help

Our hypothesis that similarity features would improve SE prediction was not wrong in principle—the effect direction was positive (+0.0009 ρ). However, the magnitude was negligible because:

1. **Feature dimensionality imbalance**: 4 similarity features cannot meaningfully influence a model dominated by 4096 hidden state dimensions.

2. **Garbage in, garbage out**: When hidden states contain no SE signal, concatenating auxiliary features provides only auxiliary noise.

3. **Linear probe limitations**: Logistic regression cannot learn complex feature interactions; a nonlinear probe might extract more from the combined representation.

## Limitations

We acknowledge several limitations that scope our conclusions:

**Single layer tested**: We evaluated only layer 25 of 32. The SE signal may exist at other layers we did not explore. This limits our ability to conclude that hidden states *never* encode SE—only that this configuration does not.

**Single token position**: We used only TBG. Alternative positions (SLT, pooled representations) may capture different information.

**Single dataset**: TruthfulQA is standard but adversarial by design; results may not generalize to TriviaQA, SQuAD, or other QA benchmarks.

**Linear probe only**: Logistic regression may be too simple; MLP probes with nonlinear activations could capture patterns we missed.

**SE label quality not validated**: We assumed DeBERTa NLI clustering produces valid SE labels, but did not inspect cluster assignments for quality.

**Single random seed**: We used seed=42 without variance estimation across multiple seeds.

These limitations are acceptable for an existence proof: we tested whether a reasonable configuration works, and it did not. Systematic exploration across configurations is future work motivated by our failure.

## Broader Impact

This work serves the ML community by documenting failure modes that practitioners will encounter:

**For practitioners**: Do not deploy SE probes without validating on your specific model, layer, and token configuration. Published benchmarks may not transfer.

**For researchers**: Negative results are valuable. Understanding where methods fail guides research toward robust solutions.

**For the field**: Configuration sensitivity in probing methods deserves systematic study, not just footnotes in papers reporting optimal settings.

We see no direct negative societal impacts from this work. Indirectly, our findings prevent deployment of ineffective uncertainty systems—a positive contribution to AI safety.

## Implications for Future Work

Our failure charts a path forward:

1. **Systematic layer ablation**: Test all layers 20-31 to locate where SE information resides in Llama-3-8B.

2. **Token position comparison**: Compare TBG, SLT, and pooled representations.

3. **Nonlinear probes**: Test MLP architectures that may capture complex SE patterns.

4. **SE label validation**: Manually inspect semantic clusters for quality before training probes.

5. **Multi-dataset evaluation**: Validate on TriviaQA and SQuAD to assess generalization beyond TruthfulQA.

6. **Configuration-agnostic methods**: Develop probing approaches that are robust to layer/position choices, or automated search protocols for optimal configurations.

The 39% AUROC gap with published results is both a warning and an opportunity—understanding this gap will advance the field's understanding of SE probing.
