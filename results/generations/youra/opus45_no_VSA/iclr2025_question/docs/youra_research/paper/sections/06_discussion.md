# 6. Discussion

## 6.1 Interpretation of Validated Claims

The +7.1% AUROC improvement confirms that cross-layer trajectory shape carries information beyond final-layer entropy. This supports the attractor dynamics interpretation: factual retrieval converges smoothly because the model accesses grounded knowledge, while fabrication shows higher instability as the model satisfies competing constraints without a knowledge anchor.

The combination of NTI and CMI is non-redundant (LRT $p = 1.15 \times 10^{-5}$), suggesting these metrics capture complementary aspects of trajectory dynamics:
- **NTI** captures the magnitude of entropy fluctuations (how much the model "wavers")
- **CMI** captures the direction of convergence (whether the model moves consistently toward its answer)

## 6.2 Interpretation of Refuted Claims

### Low-Entropy Failure (h-m2)

The collapse of NTI on confident predictions is structural, not incidental. By construction, NTI = $\sigma(H)/\mu(H)$---when mean entropy approaches zero, variance also approaches zero regardless of correctness. This reveals a fundamental limitation: entropy-derived metrics cannot detect "confident hallucinations" where the model converges smoothly to an incorrect answer.

This finding has practical implications: CLTI is a *complement* to entropy-based methods, not a replacement. It provides additional signal precisely when the model is uncertain---but confident errors require different approaches (e.g., factual retrieval probes, knowledge base verification).

### RCI Universality (h-m3)

The near-universal prevalence of RCI flip patterns (>90% in both classes) reveals that top-token competition is architectural rather than epistemic. This aligns with interpretability research showing that transformers perform iterative refinement across layers \citep{elhage2022toy}. The negative result is informative: future work seeking hallucination signal from token competition should focus on *semantic distance* between competing tokens rather than binary flip presence.

## 6.3 Limitations

1. **Entropy coupling**: NTI is definitionally coupled to entropy; it cannot provide independent signal on low-entropy samples. Future work should explore entropy-orthogonal features (hidden state geometry, attention patterns).

2. **Single model**: Results are from LLaMA-2-7B only. Generalization to other architectures (Mistral, LLaMA-3, GPT-4) requires replication.

3. **Multiple-choice format**: TruthfulQA MC1 is multiple-choice; free-generation hallucination may exhibit different trajectory patterns.

4. **Correlation, not causation**: We demonstrate correlation between trajectory instability and hallucination but no causal mechanism. Activation patching experiments could establish causality.

5. **Moderate effect size**: Cohen's $d = 0.18$ for NTI indicates a small effect. While statistically significant, practical deployment would likely require combination with other signals.

## 6.4 Connection to Prior Work

Our results align with and extend prior findings:

- **MIND** \citep{su2024mind}: Internal states carry hallucination signal (confirmed)
- **END decoding** \citep{wu2025end}: Cross-layer entropy correlates with factuality (confirmed and quantified)
- **Semantic entropy probes** \citep{kossen2024semantic}: Lightweight classifiers on hidden states approach full semantic entropy (extended to trajectory features)
- **Logit lens** \citep{nostalgebraist2020logitlens}: Per-layer projections are viable (validated for uncertainty estimation)

The novel contribution is formalizing trajectory metrics and conducting controlled validation with explicit success criteria, including negative results.
