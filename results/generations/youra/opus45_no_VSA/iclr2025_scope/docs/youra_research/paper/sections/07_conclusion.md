# Conclusion

We began by observing that adapter selection in multi-task models typically requires validation data that is unavailable in zero-shot settings. This work demonstrates that the validation data requirement can be eliminated—instruction prefixes alone contain sufficient signal for effective routing.

## Summary

We introduced Instruction-Prefix-Conditioned Routing (IPCR), a minimal approach for zero-shot adapter selection using frozen MiniLM embeddings and a linear probe. Our experiments on FLAN task families establish three results:

1. **Intrinsic alignment exists:** Instruction embeddings are linearly separable by task family with macro-F1 = 0.995, demonstrating that instruction semantics and adapter specializations share geometric structure without joint training.

2. **Zero-shot routing works:** IPCR achieves 95% of oracle performance on held-out task families, validating that adapter banks can be accessed without validation examples.

3. **Routing is lexically anchored:** The mechanism depends on task-indicative keywords rather than deep semantic invariants. Paraphrase perturbations cause 24% routing inconsistency; keyword masking causes 44% accuracy drops.

This third finding is as important as the first two—it defines the boundary conditions for IPCR deployment. The method is appropriate for controlled instruction interfaces (APIs, templates) but requires robustification for open-ended queries.

## Future Directions

Our results motivate several directions grounded in experimental evidence:

**Robust router training:** The lexical dependence revealed by H-M2 suggests paraphrase augmentation during probe training, or contrastive losses that encourage paraphrase invariance. The goal is maintaining 95% oracle performance while improving cosine similarity under paraphrase from 0.78 to ≥0.90.

**Encoder alternatives:** The mean-pooling limitation of MiniLM suggests testing encoders with stronger compositional semantics (E5-large, Instructor-XL). These may provide paraphrase invariance that MiniLM lacks.

**Hybrid routing:** Combining embedding-based routing with keyword confidence could maintain high accuracy on standard instructions while providing graceful degradation on paraphrased variants. When embedding confidence is low, fall back to keyword-based routing or uniform averaging.

**Full oracle validation:** H-E1 used task names as oracle proxy. Computing per-adapter loss for each sample would provide ground-truth adapter selection labels, enabling tighter performance bounds.

The finding that zero-shot routing is achievable—but fragile—opens a research direction at the intersection of adapter composition and robust representation learning. We hope this work encourages investigation of intrinsic alignment properties in instruction-tuned models, and motivates routing architectures that preserve both efficiency and robustness.
