# 6. Discussion

## 6.1 Interpreting the BERT Result

The Pearson correlation $r = 0.984$ between erank($W_0$) and PARA oracle ranks for BERT-base-uncased is substantially higher than our pre-registered threshold and considerably stronger than we expected from the pre-experimental confidence estimate. Several factors contribute to this strength.

**Bimodal oracle structure amplifies the correlation.** The BERT oracle assigns exclusively $r^* = 4$ or $r^* = 64$ across the 5 measured layers. erank cleanly separates these two populations: all attention output layers (oracle $r^* = 4$) have erank $< 600$, while all FFN intermediate layers (oracle $r^* = 64$) have erank $> 700$. This bimodality means the correlation is not a noisy linear relationship but a near-perfect tier classification, and erank achieves it structurally — without seeing any task data.

**The mechanism is consistent with the theoretical prediction.** FFN intermediate layers in BERT-base develop erank $\sim 705$–$720$, indicating that their singular values are nearly uniformly distributed across hundreds of directions. This is exactly the structural condition that requires high-rank LoRA updates: there is no dominant singular direction to align with, so the adapter needs many directions ($r=64$) to capture task-relevant signal. Attention output layers, with erank $\sim 555$–$600$, have more concentrated singular spectra and need fewer directions to adapt ($r=4$).

**The $n=5$ sample size is a limitation but not a fatal flaw.** With 5 oracle measurements spanning both structural tiers, the correlation is highly constrained — the bimodal oracle essentially collapses the problem to a 2-class prediction, which erank solves with a continuous scalar. The statistical significance ($p=0.0013$) reflects the deterministic nature of the discrimination, not just sample size. Increasing oracle coverage to all 72 BERT layers is necessary to confirm the linear correlation over the full erank range.

## 6.2 Multi-Family Evaluation: Status and Expectations

The global gate requires $r \geq 0.65$ in $\geq 2/3$ model families. Currently, only BERT-base satisfies this criterion (1/3 families). DeBERTa-v3-base and ViT-base-patch16-224 oracle sweeps are pending due to compute constraints (~720 training runs per family for full coverage).

The erank maps for all three families are available and show consistent layer-type structure: FFN layers have higher erank than attention layers in all three models. If this structural pattern translates to oracle rank preference (as it does for BERT), we expect DeBERTa and ViT to also show significant positive correlations. ViT's larger erank range ratio (2.97×) is particularly encouraging — a wider predictor range generally translates to higher statistical power.

We present the current results as strong preliminary evidence rather than definitive proof of the multi-family claim. The pre-registered hypothesis remains open; we report what we can currently support and clearly identify what remains to be measured.

## 6.3 Limitations

**L1: Oracle completeness.** The BERT oracle sweep covered 5 of 72 target layers (6.9%) due to compute constraints. While the 5 layers were chosen to span the erank range and the correlation is strong, a full 72-layer sweep may reveal non-linearities or outliers that change the picture. The bimodal structure observed in 5 layers may not hold uniformly — intermediate erank layers (erank $\sim 620$–$680$) have not been measured.

**L2: Marginal oracle ≠ joint-optimal oracle.** The PARA oracle assigns rank to each layer independently, holding all other layers at $r=8$. The globally optimal rank allocation (optimizing all layers jointly) may differ from the marginal assignment. Prior work [Zhang et al., 2023; Tripathi et al., 2026] uses similar marginal oracles as proxies for joint-optimal, and any positive marginal correlation still provides actionable rank guidance. We acknowledge that end-to-end performance validation (using erank-proportional ranks and measuring task accuracy) has not been completed.

**L3: Encoder-only models.** All three evaluated model families are encoder-only transformers (NLP encoders and a vision encoder). Decoder-only LLMs (LLaMA, Mistral, GPT) have different architectural properties — causal attention masks, different SVD structure in key-value matrices — and the erank-oracle relationship may differ or not hold.

**L4: Classification tasks only.** The PARA oracle is defined using validation accuracy, which requires a classification metric. Generative tasks (translation, summarization) require a different oracle definition (e.g., BLEU, ROUGE), and the erank-oracle correlation for generative fine-tuning is untested.

## 6.4 Broader Impact

This work contributes to the growing evidence that pretrained weight geometry contains information relevant to fine-tuning decisions. If validated at scale, zero-cost structural rank prediction could meaningfully reduce the computational overhead of LoRA deployment — eliminating calibration runs and gradient warmup phases that are currently prerequisites for adaptive-rank methods.

One potential concern: if practitioners use erank-proportional rank allocation without validation, they may allocate rank suboptimally in cases where the erank-oracle correlation is weaker (e.g., generation tasks, very large models). We recommend treating erank as a prior over rank allocation, not a substitute for task-specific validation, until multi-family and multi-task coverage is established.
