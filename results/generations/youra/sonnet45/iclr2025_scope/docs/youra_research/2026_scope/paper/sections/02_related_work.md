# 2. Related Work

Our work intersects three research areas: parameter-efficient fine-tuning (which motivates the low-rank assumption), SSM architectures (which exploit bounded-state representations), and post-hoc model compression. We position our contribution as providing empirical ground truth for assumptions implicit in these areas.

## 2.1 Parameter-Efficient Fine-Tuning

**LoRA and low-rank adaptation.** Hu et al. [2021] introduced LoRA, which freezes pre-trained weights W and learns low-rank updates ΔW = BA where B ∈ ℝ^(d×r), A ∈ ℝ^(r×d), r ≪ d. With r = 8-64, LoRA achieves comparable performance to full fine-tuning while reducing trainable parameters by 10,000×. This empirical success demonstrated that task-specific adaptations can be captured in low-dimensional subspaces.

Critically, Hu et al. [2021] do not claim pre-trained weights W are low-rank—they show that *updates* ΔW can be low-rank. The distinction is subtle but fundamental. LoRA's rank constraint applies to the learned adaptation matrices B and A, not to the frozen pre-trained weights W. Our work makes this distinction explicit by directly measuring rank(W), establishing that while rank(ΔW) can be small (r ~ 8-64), rank(W) is large (r_eff ~ 1600).

**Rank search and adaptive methods.** Subsequent work explored rank selection strategies. DyLoRA [Valipour et al., 2022] trains LoRA blocks for a range of ranks simultaneously, finding that optimal rank varies by task and layer. This suggests rank is not a universal property but depends on the specific adaptation required. Zhang et al. [2023] proposed AdaLoRA, which adaptively allocates rank budget across weight matrices based on importance scores. The existence of rank-search methods indicates that low-rank sufficiency is task-dependent, not a fixed property of pre-trained weights.

**Other PEFT methods.** Prefix-tuning [Li & Liang, 2021] and prompt-tuning [Lester et al., 2021] modify input representations rather than weight matrices. Adapter layers [Houlsby et al., 2019] insert trainable bottleneck modules between Transformer layers. While these methods also achieve parameter efficiency, they do not directly inform questions about pre-trained weight structure. Our focus on LoRA stems from its explicit use of rank constraints, which invites (but does not require) interpretation about weight ranks.

## 2.2 State Space Models and Hybrid Architectures

**Native SSM training.** Mamba [Gu & Dao, 2023] introduced selective state space models that achieve linear-time inference complexity O(L) compared to Transformers' quadratic O(L²). Trained from scratch on language modeling tasks, Mamba demonstrates that SSMs can match or exceed Transformer performance at certain scales. The key innovation is *selective* state updates conditioned on input, enabling data-dependent processing within bounded state dimension N.

**Hybrid architectures.** Recognizing complementary strengths, recent work explores hybrid Transformer-SSM architectures. Samba [Ren et al., 2024] interleaves Mamba blocks with attention layers. MoE-Mamba [Pióro et al., 2024] combines SSMs with Mixture of Experts routing, outperforming both pure-SSM and pure-Transformer baselines on certain benchmarks. Critically, these hybrids are *co-trained* from scratch, not created via post-hoc conversion.

**The post-hoc conversion gap.** While native SSMs and hybrid architectures succeed when trained from initialization, post-hoc conversion—converting pre-trained Transformers to SSMs—remains challenging. Our work provides empirical evidence for why: pre-trained Transformer weights do not exhibit the bounded-state low-rank structure (r_eff < 256, state size N ≤ 1024) that SSM architectures require. This negative finding validates the research community's focus on native training rather than post-hoc conversion.

## 2.3 Post-Hoc Model Compression

**Pruning and quantization.** Magnitude pruning [Han et al., 2015] and structured pruning [Liu et al., 2017] remove low-magnitude weights or entire structures (channels, heads). Quantization methods [Dettmers et al., 2022] reduce precision from FP32 to INT8 or lower. These techniques often assume redundancy in pre-trained weights—either via sparsity or low-precision representability. Our finding that projection weights maintain high effective rank (r_eff ~ 1600) suggests such redundancy may be limited in these critical matrices.

**Knowledge distillation.** Hinton et al. [2015] proposed distilling large "teacher" models into smaller "student" models via soft label supervision. Distillation succeeds when the student architecture can approximate the teacher's input-output mapping, but does not require structural similarity of internal weights. Our measurement does not directly inform distillation (which targets behavioral equivalence), but does constrain approaches that assume weight-level structural correspondence.

**SSM compression.** Recent work by Muñoz et al. [2025] applies post-training compression to *existing SSM models* (Mamba, hybrids), achieving 1.4× speedup via structured pruning and quantization. This differs from our investigation: they compress already-trained SSMs, while we examine whether pre-trained Transformers have the structure needed for Transformer→SSM conversion. Our negative finding (Transformers lack bounded-state structure) complements their positive result (SSMs can be compressed post-training).

## 2.4 Positioning Our Contribution

Our work fills an empirical gap: **no prior work has directly measured effective ranks of pre-trained 7B-scale Transformer projection weights**. LoRA demonstrated low-rank updates work, but did not measure pre-trained weight ranks. SSM research focused on native training, not analyzing Transformer weight structure. Compression work assumed properties (redundancy, low-rank) without direct measurement at scale.

By providing first direct measurements, we:
- **Clarify LoRA's mechanism**: Success stems from low-rank *updates* exploiting task-specific subspaces, not from compressing low-rank *weights*.
- **Establish boundary conditions for post-hoc conversion**: Transformer→SSM conversion based on bounded-state assumptions is not viable at 7B scale.
- **Validate native hybrid architectures**: The success of co-trained hybrids (Samba, MoE-Mamba) makes sense given that pre-trained Transformers lack inherent SSM-compatible structure.

This negative result redirects research effort: rather than attempting post-hoc conversion based on false assumptions, the community should focus on (1) native SSM/hybrid training, (2) compression methods that don't assume low-rank structure, or (3) empirically validating assumptions before building techniques.
