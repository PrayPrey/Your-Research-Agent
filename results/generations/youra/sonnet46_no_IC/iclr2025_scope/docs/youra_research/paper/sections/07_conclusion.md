# 7. Conclusion

We began by asking whether pretrained weight geometry could predict optimal per-layer LoRA rank without any training data. For BERT-base-uncased, it does — remarkably well.

The effective rank of a pretrained weight matrix, computed in a single SVD pass from $W_0$ alone, correlates with PARA oracle ranks at Pearson $r = 0.984$ ($p = 0.0013$). FFN intermediate matrices, with their spread-out singular spectra (erank $\sim 720$), receive oracle rank $r^* = 64$; attention output matrices, with concentrated spectra (erank $\sim 557$), receive oracle rank $r^* = 4$. The erank metric cleanly separates these structural tiers without observing a single training example. Participation ratio agrees with erank at $\rho = 0.968$, suggesting this discriminative signal is robust to the choice of spectral metric.

Our main contributions are:

1. The first empirical test of a purely structural per-layer LoRA rank predictor, demonstrating that $\text{erank}(W_0)$ correlates strongly with PARA oracle ranks for BERT-base-uncased ($r = 0.984$, exceeding the pre-registered threshold by a substantial margin).

2. An open experimental protocol — the PARA oracle sweep + erank correlation framework — that enables replication and extension to additional model families, tasks, and structural metrics.

3. erank maps for BERT-base-uncased, DeBERTa-v3-base, and ViT-base-patch16-224, showing consistent layer-type structure (FFN > attention output) across encoder architectures, with ViT exhibiting the largest within-model erank range (ratio 2.97×).

**Future directions.** Three questions opened by this work trace directly to the experimental design:

*From untested alternative explanations:* The oracle rank bimodality in BERT raises the question of whether layer depth or layer type is the primary driver. Partial correlation controlling for depth would separate the structural erank signal from the confound of depth-indexed differentiation.

*From unverified assumptions:* Oracle sweep completion for DeBERTa-v3-base and ViT-base-patch16-224 is the immediate priority. ViT's 2.97× erank range suggests particularly strong discriminative power; confirming this would establish multi-family evidence for the hypothesis.

*From scope extensions:* Decoder-only LLMs (LLaMA-3, Mistral-7B) represent the highest-value extension — they are the dominant fine-tuning target in practice. ViT's cross-modal result, if confirmed, suggests the mechanism generalizes beyond NLP; extension to LLMs would complete the picture.

The central finding — that a pretrained weight's singular value entropy predicts its adaptation rank need — connects pre-training geometry to fine-tuning efficiency in a way that no training signal or calibration run could achieve. We hope this work encourages broader investigation of what fine-tuning hyperparameters can be predicted from the geometry of pretrained weights alone.
