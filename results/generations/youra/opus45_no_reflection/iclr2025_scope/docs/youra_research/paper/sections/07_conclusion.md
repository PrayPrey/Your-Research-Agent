# Conclusion

We presented the first controlled comparison of distillation objective types for Transformer-to-SSM conversion, revealing that token-level alignment produces representations 5× more stable across sequence lengths than matrix-level alignment.

## Summary

Our unified Phi-Mamba framework enabled fair comparison between MOHAWK (matrix-level) and CAB (token-level) objectives. Measuring hidden state drift across sequence lengths 512-2048, we found:

- CAB drift slope: 0.00090506
- MOHAWK drift slope: 0.00452495
- Ratio: 5×

This stability gap reflects a mechanistic difference: token-level supervision is position-agnostic, while matrix-level supervision encodes position-position relationships that change with sequence length. The bounded CAB drift ratio (1.34) versus unbounded MOHAWK drift suggests token-level objectives may be preferred when target sequences exceed training distribution.

We also established that Phi-1.5 has a hard 2048 token context limit due to fixed positional embeddings—a scope condition for future length extrapolation research requiring RoPE-based teachers.

## Future Work

Three directions emerge from this work:

**Full training verification**: Our PoC validates methodology but cannot verify downstream F1 advantage. Full 1.5B token training per condition would test whether the 5× stability gap translates to task performance at extrapolated lengths.

**RoPE-based teachers**: Llama, Mistral, and other RoPE-based models can process 16K-32K sequences natively. Extending our comparison to these teachers would enable true length extrapolation experiments.

**Hybrid objectives**: Both MOHAWK and CAB objectives can coexist in our unified framework. Combining matrix-level supervision at training lengths with token-level supervision for extrapolation may capture benefits of both approaches.

The 5× stability gap we identify provides a principled starting point for these investigations—a quantified criterion for objective selection in Transformer-to-SSM distillation.
