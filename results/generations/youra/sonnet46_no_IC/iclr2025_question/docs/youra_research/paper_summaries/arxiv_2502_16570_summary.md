# Entropy-Lens: The Information Signature of Transformer Computations

## Key Metadata
- **Authors:** Riccardo Ali et al. (University of Cambridge; equal contribution with Francesco Caso, Christopher Irwin)
- **Year:** 2025 (preprint revised Feb 2026)
- **Venue:** arXiv preprint (2502.16570)
- **Core Contribution:** Entropy-Lens — a training-free, model-agnostic framework computing per-layer Shannon entropy of logit-lens predictions ("entropy profiles") to characterize transformer token-prediction dynamics.

## Section Summaries

### Abstract
In large language models (LLMs), each block operates on the residual stream to map input token sequences to output token distributions. However, most of the interpretability literature focuses on internal latent representations, leaving token-space dynamics underexplored. The high dimensionality and categoricity of token distributions hinder their analysis, as standard statistical descriptors are not suitable. We show that the entropy of logit-lens predictions overcomes these issues. In doing so, it provides a per-layer scalar, permutation-invariant metric. We introduce Entropy-Lens to distill the token-space dynamics of the residual stream into a low-dimensional signal. We call this signal the entropy profile. We apply our method to a variety of model sizes and families, showing that (i) entropy profiles uncover token prediction dynamics driven by expansion and pruning strategies; (ii) these dynamics are family-specific and invariant under depth rescaling; (iii) they are characteristic of task type and output format; (iv) these strategies have unequal impact on downstream performance, with the expansion strategy usually being more critical.

### Introduction & Motivation
Interpretability work mostly studies latent geometry, not token-space dynamics. Vocabulary distributions are high-dimensional and unordered, so standard moments/cumulants are ill-defined. Entropy of logit-lens decoded distributions gives a per-layer, per-token scalar that is permutation-invariant — enabling a low-dimensional "entropy profile" view of how the model expands and prunes its next-token candidate set across depth.

### Methodology
[DETAILED] For input sequence $S = (t_1,\dots,t_N)$ with residual activation $x^i_j$ of token $t_j$ after layer $i$, decode via the model's own output head: $y^i_j = W(x^i_j)$, $W := \text{softmax} \circ D$ (logit-lens; D is the decoder/unembedding matrix). Compute Shannon entropy $H(y^i_j) = -\sum p \log p$ per layer per token → entropy profile $h_j = (H(y^1_j), \dots, H(y^L_j))$. Generalizes to Rényi entropy $H_\alpha(X) = \frac{1}{1-\alpha}\log \sum_i p(x_i)^\alpha$; results stable across an informative α regime including Shannon (α→1), so Shannon is the parameter-free default. No gradients, no fine-tuning, no auxiliary probes; works on frozen off-the-shelf models (built on TransformerLens).

Mechanistic interpretation validated by two claims: **C1** — layer-to-layer entropy change $\Delta H_i = H_i - H_{i-1}$ is monotonically related to change in the top-p (p=0.6) candidate-set size (Spearman rank correlation 0.74–0.88 across Llama-3.2-1B/3B, Gemma-2-2B/9B); **C2** — top-p candidate sets overlap substantially across adjacent layers. Hence entropy increase = candidate expansion, decrease = pruning. Aggregation across generated tokens: concatenation (primary) or averaging over T autoregressive steps.

### Experiments & Results
[DETAILED] **Models:** 12 decoder-only LLMs (GPT-2 Small→XL, Gemma-2-2B/9B-it, Llama-3.2-1B/3B-it, Llama-3-8B-it, Qwen3-1.7B/4B/8B), 100M–9B parameters. **Diagnostic:** kNN classifier on aggregated entropy profiles, one-vs-rest ROC-AUC, 10-fold CV.

Key findings: (1) t-SNE of entropy profiles clusters by MODEL FAMILY not size — family-specific dynamics (GPT: high initial entropy, gradual sharpening; Llama: low-entropy start, extended high-entropy plateau, final refinement). (2) Depth-rescaling invariance: profiles align when plotted against relative layer index (layer/total-layers) within a family — smaller models are a coarser discretization of the same dynamics. (3) Task-type classification (TinyStories; generative/syntactic/semantic prompts, 800/task): kNN AUC 94.8–98.4 across 6 models. (4) Output-format classification (poem/scientific/chat): AUC 96.6–98.7, stable across Rényi α ∈ {0.5, 1, 5}. (5) Intervention on MMLU (6 models, base+it): skipping max-ΔH (expansion) layers collapses Llama accuracy to chance; expansion generally more critical than pruning, except Gemma2-2B-it where the effect inverts.

### Discussion & Conclusion
Entropy profiles are structured computational signatures: family-specific, depth-rescaling invariant, task/format characteristic, with functionally unequal expansion vs pruning phases. Limitations: no mechanistic account of which architecture/training choices shape a profile; unclear how RLHF/fine-tuning alters phase importance; decoder-only models only.

## Key Contributions
- Entropy as a principled scalar, permutation-invariant per-layer statistic for token-space dynamics — exactly per-layer logit-lens Shannon/Rényi entropy from one forward pass.
- Family-specific, depth-rescaling-invariant entropy profiles (relative-depth alignment within families).
- Expansion/pruning decomposition via ΔH with validated candidate-set interpretation; expansion phases usually more performance-critical.

## Potential Relevance
This paper computes EXACTLY our core feature — per-layer logit-lens entropy from a single forward pass — but uses it only as a computation signature (family/task/format classification), never evaluating it as a hallucination-detection AUROC score. Its C1/C2 validation gives our entropy signal a mechanistic reading (candidate expansion/pruning), and its ΔH quantity is a close cousin of our adjacent-layer KL signal. The depth-rescaling invariance finding (profiles align at relative depth within families) directly bears on our detailed question 4 (cross-family consistency of relative signal depth) — it predicts within-family stability but says nothing across families. The demonstrated per-sample discriminative power of entropy profiles (kNN AUC > 94) is encouraging existence evidence that profile shape carries sample-level information.
