# Eliciting Latent Predictions from Transformers with the Tuned Lens

## Key Metadata
- **Authors:** Nora Belrose et al. (EleutherAI, FAR AI, University of Toronto, Boston University, UC Berkeley)
- **Year:** 2023 (arXiv v6 revised Nov 2025)
- **Venue:** arXiv preprint (2303.08112); widely cited (540+)
- **Core Contribution:** The tuned lens — per-layer trained affine "translators" composed with the frozen unembedding that reliably decode every hidden state into a vocabulary distribution, fixing the brittleness and bias of the raw logit lens.

## Section Summaries

### Abstract
We analyze transformers from the perspective of iterative inference, seeking to understand how model predictions are refined layer by layer. To do so, we train an affine probe for each block in a frozen pretrained model, making it possible to decode every hidden state into a distribution over the vocabulary. Our method, the tuned lens, is a refinement of the earlier "logit lens" technique, which yielded useful insights but is often brittle. We test our method on various autoregressive language models with up to 20B parameters, showing it to be more predictive, reliable and unbiased than the logit lens. With causal experiments, we show the tuned lens uses similar features to the model itself. We also find the trajectory of latent predictions can be used to detect malicious inputs with high accuracy.

### Introduction & Motivation
Views each transformer layer as an incremental update to a latent next-token prediction (iterative inference). Decoding hidden states at every layer yields a "prediction trajectory" that converges smoothly to the final output. The raw logit lens (nostalgebraist 2020) — decode hidden states with the pretrained unembedding — is unreliable for several model families (BLOOM, GPT-Neo, OPT-125M), hard to interpret due to representational drift, and systematically biased toward certain vocabulary items.

### Methodology
[DETAILED] For a pre-LayerNorm transformer with residual update $h_{\ell+1} = h_\ell + F_\ell(h_\ell)$: **logit lens** = $\text{LogitLens}(h_\ell) = \text{LayerNorm}[h_\ell] W_U$ (sets all later residuals to zero). Failure modes: (1) out-of-distribution input to the unembedding when residual means are far from zero; (2) "rogue" high-variance dimensions unevenly distributed across layers; (3) hidden-state covariance drifts with layer distance — final layer covariance changes sharply. **Tuned lens** = $\text{TunedLens}_\ell(h_\ell) = \text{LogitLens}(A_\ell h_\ell + b_\ell)$ — a learned affine translator $(A_\ell, b_\ell)$ per layer (d×d, NOT a new unembedding, so it trains fast and cannot learn extra information easily). Trained with a distillation loss: minimize $D_{KL}(f_{>\ell}(h_\ell) \| \text{TunedLens}_\ell(h_\ell))$ against final-layer logits as soft labels — the probe is not incentivized to learn information beyond what the model has. Trained on pretraining validation slices (Pile/RedPajama), evaluated on 16.4M held-out tokens. Bias measured as $D_{KL}(p \| q_\ell)$ of marginal vocabulary distributions. Causal validation: **causal basis extraction** (CBE) — iteratively find orthonormal directions of maximal influence (expected KL change under mean-ablation) on the lens; ablate them in the MODEL and check influence correlation.

### Experiments & Results
[DETAILED] **Models:** GPT-2, GPT-Neo, BLOOM, OPT, Pythia 70M–12B, GPT-NeoX-20B, LLaMA-13B/Vicuna-13B. **Reliability/bias:** logit lens bias ~4–5 bits per layer for GPT-Neo-2.7B vs near-zero for tuned lens; tuned-lens perplexity uniformly lower with lower variance across models. **Causal fidelity:** lens-influential features are model-influential (Spearman ρ = 0.89 at Pythia-410M layer 18); stimulus-response Aitchison alignment higher for tuned lens at all layers. **Layer transfer:** translators transfer to nearby layers with low penalty (transfer penalty anticorrelated with covariance similarity, ρ = −0.78). **Fine-tuning transfer:** LLaMA-trained lens works on Vicuna with ≤0.3 bits/byte degradation — fine-tuning minimally changes lens-relevant representations. **Applications:** (1) prompt-injection detection: outlier detection (iForest/LOF) on flattened prediction trajectories reaches AUROC 0.99–1.00 on BoolQ/MNLI/QNLI/QQP/SST-2 (logit-lens features do worse; SRM Mahalanobis baseline competitive); (2) prediction depth (layer where top-1 stops changing) correlates with iteration-learned difficulty on 11/11 tasks (Spearman up to 0.66), tuned > logit lens in 8/11. **Muon note (v6):** original lenses were severely undertrained; Muon optimizer yields much lower KL — practitioners should use Muon.

### Discussion & Conclusion
Tuned lens is a drop-in, reliable replacement for logit lens applicable to essentially any pretrained LM; pretrained lens checkpoints released. Limitations: requires per-model translator training (fast: < 1 hr on 8×A40); CBE is computationally intensive.

## Key Contributions
- Tuned lens: per-layer affine translators + frozen unembedding, trained with distillation loss — reliable, low-bias per-layer vocabulary decoding up to 20B params.
- Causal validation (CBE + resampling ablation) that the lens reads the same features the model uses.
- Prediction-trajectory anomaly detection (near-perfect prompt-injection AUROC) and prediction-depth difficulty measurement.

## Potential Relevance
Foundational infrastructure for our hypothesis: establishes that per-layer vocabulary decoding is meaningful and that PREDICTION TRAJECTORIES carry sample-level signal usable for detection (prompt injections, difficulty) — proven for input anomalies, never for hallucination AUROC. Critically, its diagnosis of WHY the raw logit lens is brittle (representation drift, rogue dimensions, final-layer covariance shift, per-family variation) is directly relevant to our LLaMA-2 rescue test: raw logit-lens statistics on LLaMA-2 may be noisy at early layers, arguing for our degeneracy screen and per-model layer selection. The distillation-trained affine translators are our documented fallback path if raw-lens signals prove too brittle (tuned-lens library, 601★). LLaMA-family lens transferability (base→fine-tuned) supports cross-variant robustness of lens readouts.
