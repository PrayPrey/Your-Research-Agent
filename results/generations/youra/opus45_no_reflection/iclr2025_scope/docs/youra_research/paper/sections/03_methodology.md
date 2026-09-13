# Methodology

## Problem Formulation

Consider distilling a pretrained Transformer teacher T into an SSM-based student S. At layer ℓ, the teacher computes attention output:

$$\mathbf{A}^{(\ell)} = \text{softmax}\left(\frac{\mathbf{Q}^{(\ell)} \mathbf{K}^{(\ell)\top}}{\sqrt{d}}\right) \mathbf{V}^{(\ell)}$$

The student computes SSM output via selective state space dynamics. Two distillation approaches exist:

**Matrix-level (MOHAWK)**: Minimize attention map discrepancy directly:
$$\mathcal{L}_{\text{matrix}} = \sum_{\ell} \left\| \text{Mixer}_T^{(\ell)}(\mathbf{x}) - \text{Mixer}_S^{(\ell)}(\mathbf{x}) \right\|_F^2$$

**Token-level (CAB)**: Align individual projections via learned bridges:
$$\mathcal{L}_{\text{token}} = \sum_{\ell} \left\| f_B(\mathbf{Q}^{(\ell)}) - \mathbf{B}_S^{(\ell)} \right\|^2 + \left\| f_C(\mathbf{K}^{(\ell)}) - \mathbf{C}_S^{(\ell)} \right\|^2$$

where $f_B, f_C$ are learned MLP bridges mapping Transformer projections to SSM parameters.

The key distinction: matrix-level objectives supervise position-position relationships (the attention map); token-level objectives supervise individual token representations.

## Unified Framework Design

To enable fair comparison, we implement both objectives in a single Phi-Mamba codebase. This unified framework ensures:

- **Same teacher model**: Phi-1.5 (1.3B parameters)
- **Same student architecture**: Phi-Mamba with MOHAWK modifications (multi-head SSM, no Δ, open gates)
- **Same training data**: C4 dataset (streaming), Phi tokenizer
- **Same optimization**: AdamW, identical learning rate schedules

The framework supports switching between MOHAWK Stage 1-3 losses and CAB bridge alignment via configuration. H-E1 validation confirms both objectives execute without errors in this unified setup.

## Hidden State Drift Measurement

To quantify representation stability across lengths, we define hidden state drift at layer ℓ for sequence length L:

$$\text{Drift}^{(\ell)}(L) = \frac{1}{N} \sum_{i=1}^{N} \left\| \mathbf{h}_T^{(\ell)}(x_i, L) - \mathbf{h}_S^{(\ell)}(x_i, L) \right\|_2$$

where $\mathbf{h}_T, \mathbf{h}_S$ are teacher and student hidden states, and the average is over N samples.

We also measure cosine similarity degradation:
$$\text{CosSim}^{(\ell)}(L) = \frac{1}{N} \sum_{i=1}^{N} \cos(\mathbf{h}_T^{(\ell)}, \mathbf{h}_S^{(\ell)})$$

**Drift slope**: Linear regression of Drift(L) against L yields slope indicating how quickly representations diverge with length. Lower slope indicates more stable representations.

**Drift ratio**: Drift(L_max) / Drift(L_min) measures relative degradation. Ratio < 2.0 indicates bounded drift; higher values suggest unbounded degradation.

## Design Decisions

**Why Phi-1.5?** Standard teacher model from MOHAWK with public weights. Enables direct comparison with published baselines.

**Why Phi-Mamba?** MOHAWK-modified Mamba-2 architecture designed for attention-to-SSM transfer. Multi-head structure, removed Δ parameter, open gates match attention layer interface.

**Why C4?** Standard pretraining corpus. Streaming access avoids download overhead. Same tokenizer (Phi tokenizer) ensures consistent vocabulary.

**Why 512-2048 length range?** Phi-1.5's fixed positional embeddings create hard 2048 token limit. We test maximum feasible range while staying within teacher capabilities.

## Experimental Protocol

For each objective (MOHAWK, CAB):
1. Initialize student from teacher embedding/output layers (MOHAWK prescription)
2. Train for 500 steps (PoC) or 1.5B tokens (full)
3. Collect hidden states at target lengths (512, 1024, 1536, 2048)
4. Compute drift metrics across middle layers (8, 12, 16)
5. Fit linear regression, extract slope and confidence intervals
