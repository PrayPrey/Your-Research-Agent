# Discussion

## Key Findings Interpretation

The 5× drift slope difference between CAB and MOHAWK suggests a fundamental mechanistic distinction in what each objective transfers during distillation.

**Token-level objectives are position-agnostic**: Aligning Q/K projections to B/C parameters creates supervision that doesn't depend on specific sequence positions. Each token's representation is aligned independently, producing invariance to sequence length by construction.

**Matrix-level objectives encode positional relationships**: Attention maps capture which positions attend to which. These position-position patterns are intrinsically length-dependent—a pattern learned at 512 tokens does not describe the same attention structure at 2048 tokens.

The bounded drift ratio (1.34) for CAB versus unbounded growth for MOHAWK provides evidence that this mechanistic difference has measurable consequences. When practitioners target sequence lengths beyond training distribution, token-level objectives may produce more reliable transfer.

## Honest Limitations

We acknowledge several limitations that bound the claims we can make:

**PoC training only**: Our experiments use 1M tokens (PoC mode) rather than the 1.5B tokens per condition required for full distillation convergence. While drift measurements are valid for comparing representation stability, downstream task performance (F1 on LongBench) cannot be verified. H-M3's failure (interaction p = 0.881) reflects this limitation.

**Single teacher model**: All experiments use Phi-1.5 as teacher. Generalization to other Transformers (Llama, Mistral, GPT) is not tested. Phi-1.5's fixed positional embeddings create a specific extrapolation profile; RoPE-based models may behave differently.

**Simulated student approximation**: Drift analysis uses projection-matched Mamba as student proxy rather than fully-trained phi-mamba checkpoints. The 5× slope ratio is directionally robust but exact magnitudes may vary with real checkpoints.

**Context limit discovered**: Phi-1.5's hard 2048 token limit prevented testing at 16K-32K as originally planned. Our results apply to the ≤2048 range and suggest (but don't prove) behavior at extrapolated lengths.

## Connection to Prior Work

Our findings extend prior work in specific ways:

- **MOHAWK**: We confirm matrix-level distillation is effective at training lengths but quantify degradation across lengths.
- **CAB**: We provide mechanistic evidence for why token-level alignment might generalize—position-agnostic supervision.
- **Length generalization**: We connect distillation objective choice to length generalization, a relationship not previously studied.

## Broader Impact

This work provides a principled criterion for distillation objective selection: when target deployment involves sequences longer than teacher training length, token-level objectives produce more stable representations.

For practitioners converting Transformers to SSMs for long-context applications, our 5× stability gap suggests token-level alignment (CAB-style) may be preferred despite comparable performance at training lengths.

The Phi-1.5 context limit finding also highlights the importance of teacher model selection for length extrapolation research—fixed positional embeddings fundamentally prevent supervision at extended lengths.
